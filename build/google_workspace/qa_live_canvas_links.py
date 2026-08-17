#!/usr/bin/env python3
"""Read-only live Canvas verification for CCE Google /copy delivery links.

The Canvas token is read once from stdin. It is never accepted as a command-line
argument, written to disk, or printed.
"""

from __future__ import annotations

import ast
import asyncio
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
ROOT = Path(__file__).resolve().parents[2]
PARITY = ROOT / "cce-curriculum/notes/google-workspace-parity-manifest.json"
DRIVE_STATE = ROOT / "cce-curriculum/notes/google-workspace-drive-state.json"
BUILDERS = {
    "1SW Wk0": ROOT / "build/canvas/build_wk0.py",
    "1SW Wk1": ROOT / "build/canvas/build_wk1.py",
}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.links.append(str(href))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def module_name(path: Path) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "MODULE_NAME" for target in node.targets):
            continue
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return node.value.value
    raise RuntimeError(f"{path.relative_to(ROOT)} has no literal MODULE_NAME")


def expected_contract() -> dict[tuple[str, int], dict[str, object]]:
    payload = json.loads(PARITY.read_text(encoding="utf-8"))
    contract: dict[tuple[str, int], dict[str, object]] = {}
    for artifact in payload["artifacts"]:
        match = re.fullmatch(r"([1-6]SW Wk\d+) Day ([1-5])", artifact["curriculum_address"])
        if not match:
            continue
        key = match.group(1), int(match.group(2))
        contract[key] = {
            "copy_urls": {artifact["drive"]["native_google_file"]["copy_url"]},
            "canvas_file_ids": {artifact["canvas"]["file_id"]},
        }
    state = json.loads(DRIVE_STATE.read_text(encoding="utf-8"))
    for unit in state["units"]:
        for support in unit.get("native_support_files", []):
            if support["key"] != "1sw-wk0-first-week-goal-setting":
                continue
            record = contract.setdefault(("1SW Wk0", 1), {"copy_urls": set(), "canvas_file_ids": set()})
            record["copy_urls"].add(support["copy_url"])
            record["support_name"] = "cce-first-week-goal-setting.docx"
    return contract


async def paged(client: "httpx.AsyncClient", path: str) -> list[dict]:
    rows: list[dict] = []
    url: str | None = f"{BASE}/api/v1{path}"
    params: dict[str, int] | None = {"per_page": 100}
    while url:
        response = await client.get(url, params=params)
        response.raise_for_status()
        rows.extend(response.json())
        url = response.links.get("next", {}).get("url")
        params = None
    return rows


async def run(token: str) -> dict[str, object]:
    contract = expected_contract()
    required_module_names = {address: module_name(path) for address, path in BUILDERS.items()}
    discovered_support: dict[str, int] = {}
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=90) as client:
        modules = await paged(client, f"/courses/{COURSE_ID}/modules")
        for address, expected_name in required_module_names.items():
            matches = [module for module in modules if module.get("name") == expected_name]
            require(len(matches) == 1, f"expected one live module named {expected_name!r}; found {len(matches)}")
            module = matches[0]
            require(module.get("published") is False, f"module is published: {expected_name}")
            items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
            teacher_items = [
                item for item in items
                if item.get("type") == "Page" and str(item.get("title") or "").startswith("TEACHER:")
            ]
            require(len(teacher_items) == 5, f"{address}: expected five Teacher pages")
            for item in teacher_items:
                require(item.get("published") is False, f"published Teacher module item: {item.get('title')}")
                day_match = re.search(r"\bDay\s+([1-5])\b", str(item.get("title") or ""), flags=re.I)
                require(day_match is not None, f"Teacher page has no day number: {item.get('title')}")
                day = int(day_match.group(1))
                expected = contract.get((address, day))
                require(expected is not None, f"{address} Day {day}: no Google delivery contract")
                response = await client.get(f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{item['page_url']}")
                response.raise_for_status()
                page = response.json()
                require(page.get("published") is False, f"published Teacher page: {page.get('title')}")
                body = page.get("body") or ""
                parser = LinkParser()
                parser.feed(body)
                links = set(parser.links)
                missing = sorted(expected["copy_urls"] - links)
                require(not missing, f"{address} Day {day}: missing exact Google /copy links {missing}")
                body_file_ids = {int(value) for value in re.findall(r"/files/(\d+)", body)}
                missing_files = sorted(expected["canvas_file_ids"] - body_file_ids)
                require(not missing_files, f"{address} Day {day}: missing exact Canvas files {missing_files}")
                file_records: list[dict] = []
                for file_id in sorted(body_file_ids):
                    file_response = await client.get(f"{BASE}/api/v1/files/{file_id}")
                    file_response.raise_for_status()
                    file_record = file_response.json()
                    require(file_record.get("locked") is True, f"Canvas file is unlocked: {file_id}")
                    file_records.append(file_record)
                support_name = expected.get("support_name")
                if isinstance(support_name, str):
                    support_matches = [row for row in file_records if row.get("display_name") == support_name]
                    require(len(support_matches) == 1, f"{address} Day {day}: expected one locked {support_name}")
                    discovered_support[support_name] = int(support_matches[0]["id"])

    return {
        "course_id": COURSE_ID,
        "modules": len(BUILDERS),
        "teacher_pages": 10,
        "copy_links": sum(len(record["copy_urls"]) for record in contract.values()),
        "discovered_support_files": discovered_support,
        "passed": True,
    }


def main() -> int:
    try:
        contract = expected_contract()
        require(len(contract) == 10, f"expected ten Teacher-page contracts; found {len(contract)}")
        require(sum(len(record["copy_urls"]) for record in contract.values()) == 11, "expected eleven Google /copy links")
        for path in BUILDERS.values():
            module_name(path)
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError, SyntaxError) as exc:
        print(f"Canvas Google-link preflight failed: {exc}", file=sys.stderr)
        return 2
    if sys.argv[1:] == ["--preflight"]:
        print("Canvas Google-link preflight: PASS modules=2 teacher_pages=10 copy_links=11")
        return 0
    if sys.argv[1:]:
        print("usage: qa_live_canvas_links.py [--preflight]", file=sys.stderr)
        return 2
    global httpx
    try:
        import httpx
    except ModuleNotFoundError:
        print("httpx is required; run through `uv run --with httpx`", file=sys.stderr)
        return 2
    token = sys.stdin.readline().strip()
    if not token:
        print("Canvas token required on stdin", file=sys.stderr)
        return 2
    try:
        result = asyncio.run(run(token))
    except Exception as exc:
        print(f"Canvas Google-link QA failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
