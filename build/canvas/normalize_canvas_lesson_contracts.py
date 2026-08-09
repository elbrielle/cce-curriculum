#!/usr/bin/env python3
"""Insert or replace the visible lesson contract on all unpublished Canvas pairs."""

from __future__ import annotations

import asyncio
import json
import re
import sys

import httpx

from lesson_contracts import contract_html, load_contracts


BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
CONTRACT_RE = re.compile(
    r'<section data-cce-lesson-contract="1".*?</section>', re.I | re.S
)
ROLE_RE = re.compile(r"^(TEACHER|STUDENT)\b", re.I)
DAY_RE = re.compile(r"\bDay\s+([1-5])\b", re.I)
WEEK_RE = re.compile(r"^([1-6]SW Wk\d+):")


async def paged(client: httpx.AsyncClient, path: str) -> list[dict]:
    records: list[dict] = []
    url = f"{BASE}/api/v1{path}"
    params = {"per_page": 100}
    while url:
        response = await client.get(url, params=params)
        response.raise_for_status()
        records.extend(response.json())
        url = response.links.get("next", {}).get("url")
        params = None
    return records


def insert_contract(body: str, panel: str) -> str:
    if CONTRACT_RE.search(body):
        return CONTRACT_RE.sub(panel, body, count=1)
    # Keep the page title/banner first, then show the daily contract before
    # prep, directions, optional disclosures, or instructional content.
    h1 = re.search(r"</h1>", body, re.I)
    if h1:
        return body[: h1.end()] + panel + body[h1.end() :]
    return panel + body


async def run(token: str) -> dict:
    contracts = {(row.week, row.day): row for row in load_contracts()}
    if len(contracts) != 180:
        raise RuntimeError(f"Expected 180 contracts; found {len(contracts)}")
    updated = 0
    verified = 0
    missing: list[str] = []
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as client:
        modules = await paged(client, f"/courses/{COURSE_ID}/modules")
        for module in modules:
            week_match = WEEK_RE.match(module.get("name") or "")
            if not week_match:
                continue
            week = week_match.group(1)
            items = await paged(
                client,
                f"/courses/{COURSE_ID}/modules/{module['id']}/items?include[]=content_details",
            )
            for item in items:
                title = item.get("title") or ""
                role_match = ROLE_RE.match(title)
                day_match = DAY_RE.search(title)
                if not role_match or not day_match or item.get("type") != "Page":
                    continue
                role = role_match.group(1).lower()
                day = int(day_match.group(1))
                contract = contracts.get((week, day))
                if not contract:
                    missing.append(f"{week} Day {day}")
                    continue
                response = await client.get(
                    f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{item['page_url']}"
                )
                response.raise_for_status()
                page = response.json()
                old = page.get("body") or ""
                new = insert_contract(old, contract_html(contract, role))
                if new != old:
                    response = await client.put(
                        f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{item['page_url']}",
                        data={"wiki_page[body]": new, "wiki_page[published]": "false"},
                    )
                    response.raise_for_status()
                    updated += 1
                final = new
                required = (
                    "Topic:",
                    "Objective:",
                    "Demonstration of Learning:" if role == "teacher" else "Show Your Learning:",
                )
                if all(label in final for label in required):
                    verified += 1
                else:
                    missing.append(item.get("title") or item.get("page_url"))
    return {
        "contracts": len(contracts),
        "paired_pages_verified": verified,
        "pages_updated": updated,
        "missing": sorted(set(missing)),
        "published": False,
    }


def main() -> int:
    token = sys.stdin.readline().strip()
    if not token:
        print("Canvas token required on stdin", file=sys.stderr)
        return 2
    try:
        payload = asyncio.run(run(token))
    except Exception as exc:  # redact by never printing the token or request headers
        print(f"Lesson-contract normalization failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(payload, indent=2))
    return 0 if not payload["missing"] and payload["paired_pages_verified"] == 360 else 1


if __name__ == "__main__":
    raise SystemExit(main())
