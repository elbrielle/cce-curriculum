#!/usr/bin/env python3
"""Render and audit the replacement CCE Canvas home page without contacting Canvas."""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
from html.parser import HTMLParser
from pathlib import Path

from playwright.async_api import async_playwright
from textstat import textstat

from build_course_orientation import (
    CLASSLINK_URL,
    COURSE_ID,
    HATS_LADDERS_URL,
    HOME_ASSETS,
    HOME_ASSET_DIR,
    ONENOTE_URL,
    TEACHER_EMAIL,
    home_body,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "tmp/course-home-preview"


class HomeAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.headings: list[tuple[int, str]] = []
        self.links: list[dict[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.tables = 0
        self.scripts = 0
        self.styles = 0
        self._heading_level: int | None = None
        self._heading_text: list[str] = []
        self._link: dict[str, str] | None = None
        self._link_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._heading_level = int(tag[1])
            self._heading_text = []
        elif tag == "a":
            self._link = attr
            self._link_text = []
        elif tag == "img":
            self.images.append(attr)
        elif tag == "table":
            self.tables += 1
        elif tag == "script":
            self.scripts += 1
        elif tag == "style":
            self.styles += 1

    def handle_data(self, data: str) -> None:
        if self._heading_level is not None:
            self._heading_text.append(data)
        if self._link is not None:
            self._link_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._heading_level is not None and tag == f"h{self._heading_level}":
            self.headings.append(
                (self._heading_level, " ".join("".join(self._heading_text).split()))
            )
            self._heading_level = None
            self._heading_text = []
        elif tag == "a" and self._link is not None:
            self._link["text"] = " ".join("".join(self._link_text).split())
            self.links.append(self._link)
            self._link = None
            self._link_text = []


def icon_data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def local_body() -> str:
    icons = {
        key: icon_data_uri(HOME_ASSET_DIR / filename)
        for key, filename in HOME_ASSETS.items()
    }
    return home_body(icons)


def static_audit(body: str) -> tuple[dict, list[str]]:
    audit = HomeAudit()
    audit.feed(body)
    problems: list[str] = []
    required_links = {
        f"/courses/{COURSE_ID}/modules",
        ONENOTE_URL,
        HATS_LADDERS_URL,
        CLASSLINK_URL,
        f"mailto:{TEACHER_EMAIL}",
    }
    actual_links = {link.get("href", "") for link in audit.links}
    missing_links = sorted(required_links - actual_links)
    if missing_links:
        problems.append(f"missing required links: {missing_links}")
    if len(audit.links) != len(required_links):
        problems.append(
            f"expected {len(required_links)} exact links; found {len(audit.links)}"
        )
    for link in audit.links:
        if not link.get("text"):
            problems.append(f"link has no visible text: {link.get('href')}")
        if link.get("target") == "_blank" and "noopener" not in link.get("rel", ""):
            problems.append(f"new-tab link is missing noopener: {link.get('href')}")
    if len(audit.images) != 4:
        problems.append(f"expected one Modules icon and three official tool logos; found {len(audit.images)}")
    for image in audit.images:
        if "alt" not in image:
            problems.append("image is missing an alt attribute")
    heading_levels = [level for level, _ in audit.headings]
    for previous, current in zip(heading_levels, heading_levels[1:]):
        if current > previous + 1:
            problems.append(f"heading level skips from h{previous} to h{current}")
    if audit.tables:
        problems.append(f"found {audit.tables} table(s)")
    if audit.scripts or audit.styles:
        problems.append(
            f"found unsupported script/style blocks: scripts={audit.scripts}, styles={audit.styles}"
        )
    for stale in (
        "four tools, four jobs",
        "one answer should have one home",
        "every tool has one job",
        "public-safe",
        "source-grounded",
        "load-bearing",
        "need another course page",
        "if a tool does not open",
    ):
        if stale in body.lower():
            problems.append(f"contains rejected or internal phrase: {stale!r}")

    plain_text = " ".join(
        text
        for _, text in audit.headings
        if text
    )
    # Include the complete visible body for the reading-level result.
    text_collector = VisibleText()
    text_collector.feed(body)
    visible_text = " ".join(text_collector.parts)
    report = {
        "headings": audit.headings,
        "links": [{"text": link.get("text"), "href": link.get("href")} for link in audit.links],
        "images": len(audit.images),
        "tables": audit.tables,
        "heading_text": plain_text,
        "flesch_kincaid_grade": round(textstat.flesch_kincaid_grade(visible_text), 1),
    }
    return report, problems


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        cleaned = " ".join(data.split())
        if cleaned:
            self.parts.append(cleaned)


async def render(out_dir: Path, executable_path: Path | None = None) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    body = local_body()
    static, problems = static_audit(body)
    html = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>CCE Course Home Preview</title></head>'
        '<body style="margin:0;padding:24px;background:#f7f7f8">'
        '<main aria-label="CCE course home" style="max-width:1100px;margin:0 auto;background:#fff;padding:24px">'
        f"{body}</main></body></html>"
    )
    local_html = out_dir / "course-home.html"
    local_html.write_text(html, encoding="utf-8")
    browser_rows = []
    async with async_playwright() as playwright:
        options = {"executable_path": str(executable_path)} if executable_path else {}
        browser = await playwright.chromium.launch(**options)
        for name, viewport in (
            ("desktop-1280", {"width": 1280, "height": 900}),
            ("mobile-390", {"width": 390, "height": 844}),
        ):
            page = await browser.new_page(viewport=viewport, device_scale_factor=1)
            await page.goto(local_html.as_uri())
            await page.wait_for_load_state("networkidle")
            metrics = await page.evaluate(
                r"""() => ({
                    scrollWidth: document.documentElement.scrollWidth,
                    clientWidth: document.documentElement.clientWidth,
                    scrollHeight: document.documentElement.scrollHeight,
                    links: Array.from(document.querySelectorAll('a[href]')).map((a) => ({text: a.innerText.trim(), href: a.getAttribute('href')})),
                    images: document.images.length,
                    loadedImages: Array.from(document.images).filter((img) => img.complete && img.naturalWidth > 0).length,
                    clippedCards: Array.from(document.querySelectorAll('section')).filter((node) => node.scrollWidth > node.clientWidth + 1).length,
                    unresolved: (document.body.innerText.match(/\{\{[^}]+\}\}/g) || []).length
                })"""
            )
            metrics["horizontalOverflow"] = metrics["scrollWidth"] > metrics["clientWidth"]
            if metrics["horizontalOverflow"]:
                problems.append(f"{name}: horizontal overflow")
            if metrics["loadedImages"] != metrics["images"]:
                problems.append(
                    f"{name}: loaded {metrics['loadedImages']} of {metrics['images']} images"
                )
            if metrics["clippedCards"]:
                problems.append(f"{name}: {metrics['clippedCards']} clipped section(s)")
            if metrics["unresolved"]:
                problems.append(f"{name}: unresolved template tokens")
            screenshot = out_dir / f"course-home-{name}.png"
            await page.screenshot(path=str(screenshot), full_page=True)
            browser_rows.append({"viewport": name, "screenshot": screenshot.name, **metrics})
            await page.close()
        await browser.close()

    result = {
        "out_dir": str(out_dir),
        "static": static,
        "browser": browser_rows,
        "problems": sorted(set(problems)),
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))
    return 1 if problems else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--executable-path", type=Path)
    args = parser.parse_args()
    executable_path = args.executable_path.resolve() if args.executable_path else None
    return asyncio.run(render(args.out_dir.resolve(), executable_path))


if __name__ == "__main__":
    raise SystemExit(main())
