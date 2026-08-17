#!/usr/bin/env python3
"""Verify exact Google /copy delivery links in Canvas and the public mirror source."""

from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]
PARITY = ROOT / "cce-curriculum/notes/google-workspace-parity-manifest.json"
DRIVE_STATE = ROOT / "cce-curriculum/notes/google-workspace-drive-state.json"
SITE_MANIFEST = ROOT / "public-site/dist/data/site-manifest.json"
COPY_URL = re.compile(r"https://docs\.google\.com/[^\s\"'<>]+/copy")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"delivery links: FAIL: {message}")


def safe_path(value: object, label: str) -> Path:
    require(isinstance(value, str) and value, f"missing {label}")
    pure = PurePosixPath(value)
    require(not pure.is_absolute() and ".." not in pure.parts, f"unsafe {label}: {value}")
    path = (ROOT / pure).resolve()
    require(path == ROOT or ROOT in path.parents, f"outside-repository {label}: {value}")
    return path


def text_files(root: Path, patterns: tuple[str, ...]) -> list[Path]:
    files: set[Path] = set()
    for pattern in patterns:
        files.update(path for path in root.rglob(pattern) if path.is_file())
    return sorted(files)


def main() -> None:
    parity = json.loads(PARITY.read_text(encoding="utf-8"))
    drive_state = json.loads(DRIVE_STATE.read_text(encoding="utf-8"))
    site_manifest = json.loads(SITE_MANIFEST.read_text(encoding="utf-8"))
    site_outputs = {row["source"]: row["output"] for row in site_manifest["pages"]}

    canvas_files = text_files(ROOT / "build/canvas", ("*.py", "*.html"))
    canvas_text = "\n".join(path.read_text(encoding="utf-8") for path in canvas_files)
    public_source_files = text_files(ROOT / "docs", ("*.md",))
    public_source_text = "\n".join(path.read_text(encoding="utf-8") for path in public_source_files)
    built_html_files = text_files(ROOT / "public-site/dist", ("*.html",))
    built_html_text = "\n".join(path.read_text(encoding="utf-8") for path in built_html_files)

    expected_canvas: set[str] = set()
    expected_public: set[str] = set()
    keys: set[str] = set()

    for artifact in parity["artifacts"]:
        key = artifact["key"]
        require(key not in keys, f"duplicate artifact key {key}")
        keys.add(key)
        copy_url = artifact["drive"]["native_google_file"]["copy_url"]
        expected_canvas.add(copy_url)
        require(copy_url in canvas_text, f"{key}: /copy link is missing from Canvas source")
        public = artifact["public_site"]
        if public["included"]:
            expected_public.add(copy_url)
            source_pages = public.get("source_pages")
            require(isinstance(source_pages, list) and source_pages, f"{key}: public source pages are missing")
            for source_page in source_pages:
                source_path = safe_path(source_page, f"{key} public source page")
                require(copy_url in source_path.read_text(encoding="utf-8"), f"{key}: /copy link is missing from public source page")
                output = site_outputs.get(source_page)
                require(isinstance(output, str), f"{key}: public source page is absent from site manifest")
                built_path = ROOT / "public-site/dist" / output
                require(built_path.is_file(), f"{key}: built public page is missing")
                require(copy_url in built_path.read_text(encoding="utf-8"), f"{key}: /copy link is missing from built public page")
        else:
            require(copy_url not in public_source_text, f"{key}: authenticated /copy link leaked into public source")
            require(copy_url not in built_html_text, f"{key}: authenticated /copy link leaked into built public site")

    for unit in drive_state["units"]:
        for support in unit.get("native_support_files", []):
            key = support["key"]
            require(key not in keys, f"duplicate support key {key}")
            keys.add(key)
            copy_url = support["copy_url"]
            expected_canvas.add(copy_url)
            expected_public.add(copy_url)
            canvas_source = safe_path(support["canvas_source"], f"{key} Canvas source")
            require(copy_url in canvas_source.read_text(encoding="utf-8"), f"{key}: /copy link is missing from Canvas source")
            for source_page in support["public_source_pages"]:
                source_path = safe_path(source_page, f"{key} public source page")
                require(copy_url in source_path.read_text(encoding="utf-8"), f"{key}: /copy link is missing from public source")
                output = site_outputs.get(source_page)
                require(isinstance(output, str), f"{key}: public source page is absent from site manifest")
                built_path = ROOT / "public-site/dist" / output
                require(built_path.is_file(), f"{key}: built public page is missing")
                require(copy_url in built_path.read_text(encoding="utf-8"), f"{key}: /copy link is missing from built public page")

    actual_public = set(COPY_URL.findall(built_html_text))
    require(actual_public == expected_public, f"built public /copy set drift: expected {sorted(expected_public)} found {sorted(actual_public)}")
    actual_canvas = set(COPY_URL.findall(canvas_text))
    require(expected_canvas <= actual_canvas, "Canvas source /copy set is incomplete")

    print(
        "delivery links: PASS "
        f"artifacts={len(keys)} canvas_copy_links={len(expected_canvas)} "
        f"public_copy_links={len(expected_public)}"
    )


if __name__ == "__main__":
    main()
