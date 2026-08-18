#!/usr/bin/env python3
"""Build the local source-of-truth inventory for the Units_CCR Drive mirror.

The public-site manifest decides which public-safe files are in distribution.
The Google Workspace parity manifest decides which editable Google masters exist.
This script joins those records by curriculum week so Drive organization can be
checked from one deterministic file instead of a handwritten list.
"""

from __future__ import annotations

import json
import posixpath
import re
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[2]
SITE_ROOT = ROOT / "public-site/dist"
SITE_MANIFEST = SITE_ROOT / "data/site-manifest.json"
PARITY_MANIFEST = ROOT / "cce-curriculum/notes/google-workspace-parity-manifest.json"
OUTPUT = ROOT / "cce-curriculum/notes/google-workspace-distribution-inventory.json"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in {"a", "img", "source"}:
            return
        attr_name = "href" if tag == "a" else "src"
        for name, value in attrs:
            if name == attr_name and value:
                self.urls.append(value)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"distribution inventory: FAIL: {message}")


def week_address(source: str) -> tuple[str, str] | None:
    parts = PurePosixPath(source).parts
    if len(parts) < 3 or parts[0] != "docs":
        return None
    match = re.fullmatch(r"wk(\d+)-.+", parts[2])
    if not match or not re.fullmatch(r"[1-6]sw", parts[1]):
        return None
    return parts[1].upper(), f"Wk{match.group(1)}"


def folder_title(source: str) -> str:
    parts = PurePosixPath(source).parts
    sw = f"SW{parts[1][0]}"
    week_slug = parts[2]
    week, slug = week_slug.split("-", 1)
    acronyms = {"av": "AV", "emt": "EMT", "hvac": "HVAC", "it": "IT"}
    words = " ".join(acronyms.get(word, word.capitalize()) for word in slug.split("-"))
    return f"{sw} · {week.title()} {words}"


def resolve_output_link(page_output: str, href: str) -> str | None:
    split = urlsplit(href)
    if split.scheme or split.netloc or href.startswith(("#", "mailto:", "tel:")):
        return None
    base_dir = posixpath.dirname(page_output)
    resolved = posixpath.normpath(posixpath.join(base_dir, split.path))
    return resolved.lstrip("/")


def main() -> None:
    require(SITE_MANIFEST.is_file(), "build public-site/dist before creating the inventory")
    site = json.loads(SITE_MANIFEST.read_text(encoding="utf-8"))
    parity = json.loads(PARITY_MANIFEST.read_text(encoding="utf-8"))

    resources_by_output = {row["output"]: row for row in site["copied_resources"]}
    weeks: dict[tuple[str, str], dict[str, object]] = {}

    for page in site["pages"]:
        address = week_address(page["source"])
        if not address:
            continue
        key = address
        week = weeks.setdefault(
            key,
            {
                "curriculum_address": f"{address[0]} {address[1]}",
                "source_directory": str(PurePosixPath(page["source"]).parent),
                "drive_folder_title": folder_title(page["source"]),
                "public_resources": {},
                "editable_artifacts": [],
            },
        )
        html_path = SITE_ROOT / page["output"]
        require(html_path.is_file(), f"missing built page {page['output']}")
        parser = LinkParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
        for href in parser.urls:
            resolved = resolve_output_link(page["output"], href)
            resource = resources_by_output.get(resolved or "")
            if resource:
                week["public_resources"][resource["source"]] = resource

    parity_unit_titles: dict[tuple[str, str], str] = {}
    for artifact in parity["artifacts"]:
        # Daily decks use "<SW> <Wk> Day N"; a teacher weekly implementation deck
        # uses "<SW> <Wk> <Teacher> weekly implementation" and belongs to the same week.
        match = re.fullmatch(r"([1-6]SW) (Wk\d+) (?:Day \d+|\S+ weekly implementation)", artifact["curriculum_address"])
        if not match:
            continue
        key = match.group(1), match.group(2)
        require(key in weeks, f"editable artifact has no public curriculum week: {artifact['key']}")
        unit_folder = artifact["drive"].get("unit_folder")
        if unit_folder:
            unit_title = unit_folder["title"]
            previous_title = parity_unit_titles.setdefault(key, unit_title)
            require(
                previous_title == unit_title,
                f"editable artifacts disagree on the Drive unit title for {key[0]} {key[1]}",
            )
            weeks[key]["drive_folder_title"] = unit_title
        weeks[key]["editable_artifacts"].append(
            {
                "key": artifact["key"],
                "display_title": artifact["display_title"],
                "source": artifact["source"],
                "native_google_file": artifact["drive"]["native_google_file"],
                "office_release": artifact["drive"]["office_release"],
                "public_site": artifact["public_site"],
            }
        )

    ordered = []
    for key in sorted(weeks, key=lambda item: (int(item[0][0]), int(item[1][2:]))):
        week = weeks[key]
        week["public_resources"] = [
            week["public_resources"][name] for name in sorted(week["public_resources"])
        ]
        week["editable_artifacts"] = sorted(
            week["editable_artifacts"], key=lambda row: row["key"]
        )
        week["public_resource_count"] = len(week["public_resources"])
        week["editable_artifact_count"] = len(week["editable_artifacts"])
        ordered.append(week)

    payload = {
        "version": 1,
        "generated_from": {
            "public_site_manifest": str(SITE_MANIFEST.relative_to(ROOT)),
            "google_workspace_parity_manifest": str(PARITY_MANIFEST.relative_to(ROOT)),
        },
        "drive_root": parity["drive_root"],
        "unit_count": len(ordered),
        "unique_public_resource_count": len(resources_by_output),
        "units": ordered,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "distribution inventory: PASS "
        f"units={len(ordered)} unique_public_resources={len(resources_by_output)} "
        f"unit_resource_references={sum(row['public_resource_count'] for row in ordered)}"
    )


if __name__ == "__main__":
    main()
