#!/usr/bin/env python3
"""Fail-closed verification for the generated CCE public mirror."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE = ROOT / "public-site" / "dist"
COMPLETE_ARTIFACT_INVENTORY = ROOT / "cce-curriculum/notes/google-workspace-complete-artifact-inventory.json"
UNWANTED_STRUCTURAL_METAPHOR = re.compile(r"\bload(?:\s+|-+)bearing\b", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, default=DEFAULT_SITE)
    return parser.parse_args()


def clean_local_path(value: str) -> str:
    return unquote(urlsplit(value).path)


def verify(site: Path) -> None:
    problems: list[str] = []
    manifest_path = site / "data" / "site-manifest.json"
    if not manifest_path.is_file():
        raise SystemExit("Missing data/site-manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("week_count") != 36:
        problems.append(f"week_count={manifest.get('week_count')} expected=36")
    if manifest.get("lesson_count") != 180:
        problems.append(f"lesson_count={manifest.get('lesson_count')} expected=180")
    if manifest.get("page_count") != 228:
        problems.append(f"page_count={manifest.get('page_count')} expected=228")

    excluded = set(manifest["publication_policy"].get("excluded_markdown", []))
    expected_exclusions = {
        "resources/canvas-engagement-and-organization-patterns.md",
        "resources/resources-status.md",
        "resources/teks-coverage-matrix.md",
    }
    if excluded != expected_exclusions:
        problems.append(f"excluded_markdown={sorted(excluded)} expected={sorted(expected_exclusions)}")

    protected = tuple(manifest["publication_policy"]["protected_path_fragments"])
    copied = manifest.get("copied_resources", [])
    inventory = json.loads(COMPLETE_ARTIFACT_INVENTORY.read_text(encoding="utf-8"))
    expected_sources = {
        release["source"]
        for unit in inventory["units"]
        for release in unit["required_releases"]
    }
    copied_sources = {record["source"] for record in copied}
    if len(copied) != 302:
        problems.append(f"copied resources={len(copied)} expected=302")
    if copied_sources != expected_sources:
        problems.append(
            f"copied resource set drift missing={sorted(expected_sources - copied_sources)} "
            f"extra={sorted(copied_sources - expected_sources)}"
        )
    excluded_sources = {record["source"] for record in inventory["excluded_artifacts"]}
    if copied_sources & excluded_sources:
        problems.append(f"excluded artifacts copied: {sorted(copied_sources & excluded_sources)}")
    for record in copied:
        lowered = record["source"].lower()
        if any(fragment in lowered for fragment in protected):
            problems.append(f"protected copied resource: {record['source']}")
        target = site / record["output"]
        if not target.is_file():
            problems.append(f"missing copied resource: {record['output']}")
        elif target.stat().st_size != record["bytes"]:
            problems.append(f"copied resource size drift: {record['output']}")

    identities = json.loads((site / "data" / "module-identities.json").read_text(encoding="utf-8"))
    if len(identities.get("modules", {})) != 36:
        problems.append("module-identities must contain exactly 36 module IDs")
    if len(set(identities.get("modules", {}).values())) != 36:
        problems.append("module-identities contains duplicate module IDs")

    html_files = sorted(site.rglob("*.html"))
    if len(html_files) != manifest.get("page_count"):
        problems.append(f"html files={len(html_files)} manifest page_count={manifest.get('page_count')}")
    seen_titles: dict[str, Path] = {}
    week_download_sections = 0
    expected_week_counts = {
        unit["curriculum_address"]: unit["required_release_count"]
        for unit in inventory["units"]
    }
    for page in html_files:
        page_text = page.read_text(encoding="utf-8")
        soup = BeautifulSoup(page_text, "html.parser")
        rel = page.relative_to(site)
        if UNWANTED_STRUCTURAL_METAPHOR.search(soup.get_text(" ", strip=True)):
            problems.append(f"unwanted structural metaphor: {rel}")
        if soup.html is None or soup.html.get("lang") != "en":
            problems.append(f"missing html lang=en: {rel}")
        if len(soup.find_all("h1")) != 1:
            problems.append(f"expected one H1: {rel} got={len(soup.find_all('h1'))}")
        title = soup.title.get_text(strip=True) if soup.title else ""
        if not title:
            problems.append(f"missing title: {rel}")
        elif title in seen_titles:
            problems.append(f"duplicate title: {rel} and {seen_titles[title].relative_to(site)}")
        else:
            seen_titles[title] = page
        if not soup.find("a", class_="skip-link"):
            problems.append(f"missing skip link: {rel}")
        if not soup.find("main", id="main-content"):
            problems.append(f"missing main landmark: {rel}")
        downloads = soup.find("section", class_="unit-downloads")
        if downloads:
            week_download_sections += 1
            match = re.fullmatch(r"curriculum/([1-6])sw/wk(\d+)-[^/]+/index\.html", rel.as_posix())
            if not match:
                problems.append(f"downloads section outside week overview: {rel}")
            else:
                address = f"{match.group(1)}SW Wk{match.group(2)}"
                actual_count = len(downloads.find_all("a", href=True))
                expected_count = expected_week_counts[address]
                if actual_count != expected_count:
                    problems.append(f"{address} downloads={actual_count} expected={expected_count}")
        for node, attribute in [(anchor, "href") for anchor in soup.find_all("a", href=True)] + [(image, "src") for image in soup.find_all("img", src=True)] + [(script, "src") for script in soup.find_all("script", src=True)] + [(link, "href") for link in soup.find_all("link", href=True)]:
            value = node.get(attribute, "").strip()
            if not value or value.startswith(("#", "http://", "https://", "mailto:", "tel:", "data:")):
                continue
            local = clean_local_path(value)
            resolved = (page.parent / local).resolve()
            try:
                resolved.relative_to(site.resolve())
            except ValueError:
                problems.append(f"link escapes site: {rel} -> {value}")
                continue
            if not resolved.exists():
                problems.append(f"broken local reference: {rel} -> {value}")
                continue
            fragment = urlsplit(value).fragment
            if fragment and resolved.suffix == ".html":
                target_soup = BeautifulSoup(resolved.read_text(encoding="utf-8"), "html.parser")
                if target_soup.find(id=unquote(fragment)) is None:
                    problems.append(f"missing fragment: {rel} -> {value}")

    search = json.loads((site / "data" / "search-index.json").read_text(encoding="utf-8"))
    if len(search) != len(manifest["pages"]):
        problems.append(f"search entries={len(search)} expected={len(manifest['pages'])}")
    for record in search:
        if not re.fullmatch(r"[a-z0-9][a-z0-9_./-]*\.html", record["url"]):
            problems.append(f"unsafe search URL: {record['url']}")
        if not (site / record["url"]).is_file():
            problems.append(f"missing search target: {record['url']}")

    if week_download_sections != 36:
        problems.append(f"week download sections={week_download_sections} expected=36")

    if problems:
        print("PUBLIC SITE VERIFY: FAIL")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)
    print(f"PUBLIC SITE VERIFY: PASS pages={len(html_files)} weeks=36 lessons=180 resources={len(copied)}")


if __name__ == "__main__":
    verify(parse_args().site.resolve())
