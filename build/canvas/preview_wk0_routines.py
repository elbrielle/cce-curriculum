#!/usr/bin/env python3
"""Render all Week 0 Canvas guides locally at desktop and mobile widths.

This helper never contacts Canvas. It replaces template IDs with inert values,
replaces Canvas-only images with labeled SVG placeholders, and writes full-page
PNGs plus an overflow and image-load manifest for all five Teacher/Student pairs.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import re
from pathlib import Path

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "build/canvas/templates"
DEFAULT_OUT = ROOT / "tmp/wk0-routines-preview"
SPECS = tuple(
    f"wk0-day{day}-{role}.html"
    for day in range(1, 6)
    for role in ("teacher", "student")
)


def placeholder_data_uri(label: str) -> str:
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="420" viewBox="0 0 900 420">
<rect width="900" height="420" fill="#f2f8fb"/>
<rect x="4" y="4" width="892" height="412" rx="18" fill="none" stroke="#1f617a" stroke-width="8"/>
<text x="450" y="196" text-anchor="middle" font-family="Arial" font-size="34" fill="#1f617a">Local preview placeholder</text>
<text x="450" y="246" text-anchor="middle" font-family="Arial" font-size="24" fill="#24323d">{label}</text>
</svg>"""
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def render_local(template_name: str) -> str:
    html = (TEMPLATES / template_name).read_text(encoding="utf-8")
    html = re.sub(r"\{\{[^}]+\}\}", "999999", html)
    html = re.sub(
        r'src="[^"]+"',
        lambda match: f'src="{placeholder_data_uri(template_name)}"',
        html,
    )
    html = re.sub(r'href="[^"]+"', 'href="#"', html)
    return "<!doctype html><html><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"></head><body>" + html + "</body></html>"


async def build(out_dir: Path, executable_path: Path | None = None) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    async with async_playwright() as playwright:
        launch_options = {"executable_path": str(executable_path)} if executable_path else {}
        browser = await playwright.chromium.launch(**launch_options)
        for template_name in SPECS:
            stem = Path(template_name).stem
            local_html = out_dir / f"{stem}.html"
            local_html.write_text(render_local(template_name), encoding="utf-8")
            for label, viewport in (
                ("desktop", {"width": 1200, "height": 900}),
                ("mobile", {"width": 390, "height": 844}),
            ):
                page = await browser.new_page(viewport=viewport, device_scale_factor=1)
                await page.goto(local_html.as_uri())
                await page.wait_for_load_state("networkidle")
                await page.evaluate(
                    """async () => {
                        document.querySelectorAll('details').forEach((node) => { node.open = true; });
                        await Promise.all(Array.from(document.images).map((img) => {
                            if (img.complete) return Promise.resolve();
                            return new Promise((resolve) => {
                                img.addEventListener('load', resolve, { once: true });
                                img.addEventListener('error', resolve, { once: true });
                            });
                        }));
                    }"""
                )
                metrics = await page.evaluate(
                    r"""() => ({
                        scrollWidth: document.documentElement.scrollWidth,
                        clientWidth: document.documentElement.clientWidth,
                        scrollHeight: document.documentElement.scrollHeight,
                        unresolved: (document.body.innerText.match(/\{\{[^}]+\}\}/g) || []).length,
                        images: document.images.length,
                        loadedImages: Array.from(document.images).filter((img) => img.complete && img.naturalHeight > 0).length,
                        expandedDetails: Array.from(document.querySelectorAll('details')).filter((node) => node.open).length
                    })"""
                )
                screenshot = out_dir / f"{stem}-{label}.png"
                await page.screenshot(path=str(screenshot), full_page=True)
                manifest.append(
                    {
                        "template": template_name,
                        "viewport": label,
                        "screenshot": screenshot.name,
                        **metrics,
                        "horizontalOverflow": metrics["scrollWidth"] > metrics["clientWidth"],
                    }
                )
                await page.close()
        await browser.close()

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    failures = [
        row
        for row in manifest
        if row["horizontalOverflow"]
        or row["unresolved"]
        or row["loadedImages"] != row["images"]
    ]
    print(json.dumps({"out_dir": str(out_dir), "renders": len(manifest), "failures": failures}, indent=2))
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--executable-path",
        type=Path,
        help="Optional installed Chromium/headless-shell path for offline QA.",
    )
    args = parser.parse_args()
    executable_path = args.executable_path.resolve() if args.executable_path else None
    return asyncio.run(build(args.out_dir.resolve(), executable_path))


if __name__ == "__main__":
    raise SystemExit(main())
