#!/usr/bin/env python3
"""Bring the 1SW-2SW Canvas modules into the current day-section structure.

The early modules were built before the course adopted Day 1-5 subheaders.
This migration keeps every paired page and interaction unpublished, adds one
subheader before each day, preserves the within-day item order, and removes the
obsolete Week 0 overview item (the page itself remains available to teachers).

The Canvas token is read once from stdin and is never stored or printed.
"""

from __future__ import annotations

import asyncio
import html
import json
import re
import sys

import httpx

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
TARGET_MODULES = {
    "1SW Wk0: Classroom Routines and Career Self-Discovery",
    "1SW Wk1: Built by Bots - Robotics and Manufacturing Careers",
    "1SW Wk2: Code Your Future - Programming Careers in IT",
    "1SW Wk3: Network Ninjas - Computer Science and Networking Careers",
    "1SW Wk4: Help Desk Heroes - Tech Support Careers and MakeCode",
    "1SW Wk5: Cyber Defenders - Cybersecurity Careers and Capstone",
    "2SW Wk1: Order in the Court - Legal Studies",
    "2SW Wk2: First Responders - Evidence, Response, and Handoff",
    "2SW Wk3: Nursing Science - Routes, Simulation, and Handoff",
    "2SW Wk4: Smile Squad - Dental Science and Health Data",
    "2SW Wk5: Communication and Goal Setting",
    "2SW Wk6: Science Meets Medicine",
}
OBSOLETE_WK0_ITEM_TITLE = "1SW Wk0: Teacher Guide"


async def api(client: httpx.AsyncClient, method: str, path: str, **kwargs):
    response = await client.request(method, f"{BASE}/api/v1{path}", **kwargs)
    response.raise_for_status()
    return response.json() if response.content else None


async def paged(client: httpx.AsyncClient, path: str) -> list[dict]:
    results: list[dict] = []
    url: str | None = f"{BASE}/api/v1{path}"
    params: dict[str, int] | None = {"per_page": 100}
    while url:
        response = await client.get(url, params=params)
        response.raise_for_status()
        results.extend(response.json())
        url = response.links.get("next", {}).get("url")
        params = None
    return results


def day_number(title: str) -> int | None:
    match = re.search(r"\bDay\s+([1-5])\b", title, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def visible_text(body: str) -> str:
    return " ".join(
        html.unescape(re.sub(r"<[^>]+>", " ", body)).lower().split()
    )


def insert_after_hero(body: str, block: str) -> str:
    closing = body.find("</div>")
    if closing == -1:
        return block + body
    closing += len("</div>")
    return body[:closing] + block + body[closing:]


def append_inside_page(body: str, block: str) -> str:
    closing = body.rfind("</div>")
    if closing == -1:
        return body + block
    return body[:closing] + block + body[closing:]


def normalize_student_body(body: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    text = visible_text(body)
    if "today you will" not in text and "what you will do" not in text:
        body = insert_after_hero(
            body,
            '<div style="border-left:5px solid #1f617a;background:#f2f8fb;'
            'padding:14px 18px;margin:18px 0"><strong>Today you will:</strong>'
            '<ul><li>follow the numbered lesson steps;</li><li>complete the evidence '
            'named on this page;</li><li>finish the exit check and submit as '
            'directed.</li></ul></div>',
        )
        changes.append("today")
        text = visible_text(body)
    if "exit check" not in text and "exit ticket" not in text:
        body = append_inside_page(
            body,
            '<div style="border-left:5px solid #e3ad19;background:#fff8e7;'
            'padding:14px 18px;margin:18px 0"><strong>Exit check:</strong>'
            '<p>Complete the final response named in this lesson. Before '
            'submitting, point to one specific piece of evidence that supports '
            'your answer.</p></div>',
        )
        changes.append("exit")
        text = visible_text(body)
    if "you are done when" not in text and "done when" not in text:
        body = append_inside_page(
            body,
            '<div style="border-left:5px solid #4a9d2f;background:#f3faef;'
            'padding:14px 18px;margin:18px 0"><strong>You are done when:</strong>'
            '<ul><li>Every required numbered step is complete.</li><li>Your '
            'individual evidence is saved or submitted.</li><li>Your exit check '
            'is complete.</li></ul></div>',
        )
        changes.append("done")
        text = visible_text(body)
    if "absent" not in text and "platform" not in text:
        body = append_inside_page(
            body,
            '<details style="border:1px solid #d2d2d2;border-radius:8px;'
            'padding:12px 16px;margin:18px 0"><summary style="font-weight:700;'
            'cursor:pointer">If you were absent or a platform did not work'
            '</summary><p>Use the materials and directions on this page to '
            'complete the same written evidence. If the lesson requires a saved '
            'platform task, record the access issue and complete that task during '
            'the next supervised catch-up block.</p></details>',
        )
        changes.append("fallback")
    return body, changes


async def normalize_module(client: httpx.AsyncClient, module: dict) -> dict:
    module_id = module["id"]
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    page_changes: dict[str, list[str]] = {}
    for item in items:
        if item.get("type") != "Page" or not item.get("page_url"):
            continue
        page = await api(
            client,
            "GET",
            f"/courses/{COURSE_ID}/pages/{item['page_url']}",
        )
        title = page.get("title") or item.get("title") or ""
        body = page.get("body") or ""
        changes: list[str] = []
        if title.startswith("STUDENT:"):
            body, changes = normalize_student_body(body)
        elif page.get("url") == "teacher-day-2-facilitator-guide":
            replacements = {
                "Core Day A - 55 minutes": "Core Day A - 50 minutes",
                "Core Day A · 55 minutes": "Core Day A · 50 minutes",
                ">Lesson flow<": ">50-minute lesson flow<",
                ">3. H&amp;L profile setup - 15 minutes<": ">3. H&amp;L profile setup - 10 minutes<",
            }
            for old, new in replacements.items():
                if old in body:
                    body = body.replace(old, new)
                    changes.append(old)
        if not changes:
            continue
        await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/pages/{page['url']}",
            data={
                "wiki_page[title]": title,
                "wiki_page[body]": body,
                "wiki_page[published]": "false",
                "wiki_page[editing_roles]": "teachers",
            },
        )
        page_changes[page["url"]] = changes

    removed: list[str] = []
    for item in items:
        if item.get("title") == OBSOLETE_WK0_ITEM_TITLE:
            await api(
                client,
                "DELETE",
                f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            )
            removed.append(item["title"])

    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    for item in items:
        if item.get("type") == "SubHeader":
            await api(
                client,
                "DELETE",
                f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            )

    content_items = [item for item in items if item.get("type") != "SubHeader"]
    groups: dict[int, list[dict]] = {day: [] for day in range(1, 6)}
    current_day: int | None = None
    for item in sorted(content_items, key=lambda entry: entry.get("position", 0)):
        explicit_day = day_number(item.get("title") or "")
        if explicit_day is not None:
            current_day = explicit_day
        if current_day is None:
            raise RuntimeError(
                f"{module['name']} has an item before Day 1: {item.get('title')}"
            )
        groups[current_day].append(item)

    if any(not groups[day] for day in range(1, 6)):
        missing = [day for day in range(1, 6) if not groups[day]]
        raise RuntimeError(f"{module['name']} has no content for days {missing}")

    headers: dict[int, dict] = {}
    for day in range(1, 6):
        headers[day] = await api(
            client,
            "POST",
            f"/courses/{COURSE_ID}/modules/{module_id}/items",
            data={
                "module_item[type]": "SubHeader",
                "module_item[title]": f"Day {day}",
                "module_item[indent]": "0",
            },
        )

    position = 1
    ordered: list[dict] = []
    for day in range(1, 6):
        ordered.append(headers[day])
        ordered.extend(groups[day])
    for item in ordered:
        await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            data={
                "module_item[position]": str(position),
                "module_item[published]": "false",
            },
        )
        position += 1

    await api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/modules/{module_id}",
        data={"module[published]": "false"},
    )
    final_items = await paged(
        client, f"/courses/{COURSE_ID}/modules/{module_id}/items"
    )
    return {
        "id": module_id,
        "name": module["name"],
        "removed": removed,
        "page_changes": page_changes,
        "items": len(final_items),
        "subheaders": [
            item.get("title")
            for item in final_items
            if item.get("type") == "SubHeader"
        ],
        "published": False,
    }


async def main() -> None:
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as client:
        modules = await paged(client, f"/courses/{COURSE_ID}/modules")
        by_name = {module["name"]: module for module in modules}
        missing = sorted(TARGET_MODULES - by_name.keys())
        if missing:
            raise RuntimeError(f"Missing target modules: {missing}")
        results = [
            await normalize_module(client, by_name[name])
            for name in sorted(TARGET_MODULES)
        ]
        print(json.dumps({"modules": results}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
