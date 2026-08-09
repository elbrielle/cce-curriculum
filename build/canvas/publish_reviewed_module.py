#!/usr/bin/env python3
"""Publish one reviewed Canvas module without exposing facilitator guides.

The module must already follow the CCE Day 1-5 contract. Student pages,
subheaders, and contextual Canvas interactions are published; every teacher
page and teacher module item remains unpublished. The exact module materials
folder is unlocked for authenticated course use. No content is deleted.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

import httpx

from build_4sw_wk1 import BASE, COURSE_ID


async def api(client: httpx.AsyncClient, method: str, path: str, **kwargs):
    response = await client.request(method, f"{BASE}/api/v1{path}", **kwargs)
    response.raise_for_status()
    return response.json() if response.content else None


async def paged(client: httpx.AsyncClient, path: str, params=None) -> list[dict]:
    records: list[dict] = []
    url: str | None = f"{BASE}/api/v1{path}"
    query = {"per_page": 100, **(params or {})}
    while url:
        response = await client.get(url, params=query)
        response.raise_for_status()
        records.extend(response.json())
        url = response.links.get("next", {}).get("url")
        query = None
    return records


async def inventory(
    client: httpx.AsyncClient, module_name: str, materials_prefix: str
) -> dict:
    modules = await paged(client, f"/courses/{COURSE_ID}/modules")
    matches = [module for module in modules if module.get("name") == module_name]
    if len(matches) != 1:
        raise RuntimeError(f"expected one module {module_name!r}; found {len(matches)}")
    module = matches[0]
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
    pages: list[dict] = []
    for item in items:
        if item.get("type") != "Page":
            continue
        page = await api(
            client, "GET", f"/courses/{COURSE_ID}/pages/{item['page_url']}"
        )
        pages.append({"item": item, "page": page})

    teachers = [row for row in pages if (row["page"].get("title") or "").startswith("TEACHER:")]
    students = [row for row in pages if (row["page"].get("title") or "").startswith("STUDENT:")]
    unknown = [
        row["page"].get("title")
        for row in pages
        if row not in teachers and row not in students
    ]
    headers = [item for item in items if item.get("type") == "SubHeader"]
    interactions = [
        item
        for item in items
        if item.get("type") not in {"Page", "SubHeader"}
    ]
    folders = await paged(client, f"/courses/{COURSE_ID}/folders")
    material_folders = [
        folder
        for folder in folders
        if (
            (folder.get("full_name") or "").startswith(materials_prefix)
            or materials_prefix.startswith((folder.get("full_name") or "") + "/")
        )
        and (folder.get("full_name") or "") != "course files"
    ]
    problems: list[str] = []
    if unknown:
        problems.append(f"unclassified pages: {unknown}")
    if len(teachers) != 5 or len(students) != 5:
        problems.append(
            f"expected five teacher and five student pages; found {len(teachers)} and {len(students)}"
        )
    if len(headers) != 5:
        problems.append(f"expected five Day subheaders; found {len(headers)}")
    if not material_folders:
        problems.append(f"no folders match {materials_prefix!r}")
    return {
        "module": module,
        "items": items,
        "teachers": teachers,
        "students": students,
        "headers": headers,
        "interactions": interactions,
        "material_folders": material_folders,
        "problems": problems,
    }


async def set_item_published(
    client: httpx.AsyncClient, module_id: int, item_id: int, published: bool
) -> None:
    await api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/modules/{module_id}/items/{item_id}",
        data={"module_item[published]": str(published).lower()},
    )


async def publish_interaction(client: httpx.AsyncClient, item: dict) -> None:
    content_id = item.get("content_id")
    kind = item.get("type")
    if kind == "Assignment":
        await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/assignments/{content_id}",
            data={"assignment[published]": "true", "assignment[notify_of_update]": "false"},
        )
    elif kind == "Discussion":
        await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/discussion_topics/{content_id}",
            data={"published": "true"},
        )
    elif kind == "Quiz":
        await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/quizzes/{content_id}",
            data={"quiz[published]": "true", "quiz[notify_of_update]": "false"},
        )
    elif kind == "File":
        await api(client, "PUT", f"/files/{content_id}", data={"locked": "false"})
    elif kind not in {"ExternalUrl", "ExternalTool"}:
        raise RuntimeError(f"unsupported module interaction type: {kind}")


async def apply(client: httpx.AsyncClient, before: dict) -> None:
    if before["problems"]:
        raise RuntimeError("; ".join(before["problems"]))
    module_id = before["module"]["id"]

    for row in before["teachers"]:
        page = row["page"]
        await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/pages/{page['url']}",
            data={
                "wiki_page[published]": "false",
                "wiki_page[editing_roles]": "teachers",
                "wiki_page[notify_of_update]": "false",
            },
        )
        await set_item_published(client, module_id, row["item"]["id"], False)

    for row in before["students"]:
        page = row["page"]
        await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/pages/{page['url']}",
            data={
                "wiki_page[published]": "true",
                "wiki_page[editing_roles]": "teachers",
                "wiki_page[notify_of_update]": "false",
            },
        )
        await set_item_published(client, module_id, row["item"]["id"], True)

    for item in before["headers"]:
        await set_item_published(client, module_id, item["id"], True)
    for item in before["interactions"]:
        await publish_interaction(client, item)
        await set_item_published(client, module_id, item["id"], True)
    for folder in before["material_folders"]:
        if folder.get("locked"):
            await api(
                client,
                "PUT",
                f"/folders/{folder['id']}",
                data={"locked": "false"},
            )
    await api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/modules/{module_id}",
        data={"module[published]": "true"},
    )
    # Canvas publishes every child item when a parent module changes from draft
    # to published. Reassert the teacher boundary after that cascade.
    for row in before["teachers"]:
        page = row["page"]
        await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/pages/{page['url']}",
            data={
                "wiki_page[published]": "false",
                "wiki_page[editing_roles]": "teachers",
                "wiki_page[notify_of_update]": "false",
            },
        )
        await set_item_published(client, module_id, row["item"]["id"], False)


def summary(value: dict) -> dict:
    return {
        "module": {
            "id": value["module"].get("id"),
            "name": value["module"].get("name"),
            "published": value["module"].get("published"),
            "position": value["module"].get("position"),
            "unlock_at": value["module"].get("unlock_at"),
            "prerequisite_module_ids": value["module"].get("prerequisite_module_ids"),
            "require_sequential_progress": value["module"].get("require_sequential_progress"),
        },
        "teacher_pages": [
            {"title": row["page"].get("title"), "published": row["page"].get("published"), "item_published": row["item"].get("published")}
            for row in value["teachers"]
        ],
        "student_pages": [
            {"title": row["page"].get("title"), "published": row["page"].get("published"), "item_published": row["item"].get("published")}
            for row in value["students"]
        ],
        "headers": len(value["headers"]),
        "interactions": [
            {"type": item.get("type"), "title": item.get("title"), "published": item.get("published")}
            for item in value["interactions"]
        ],
        "materials_folders": [
            {"id": folder.get("id"), "name": folder.get("full_name"), "locked": folder.get("locked")}
            for folder in value["material_folders"]
        ],
        "problems": value["problems"],
    }


async def run(args, token: str) -> int:
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as client:
        before = await inventory(client, args.module, args.materials_prefix)
        if args.apply:
            await apply(client, before)
        after = await inventory(client, args.module, args.materials_prefix)
        passed = (
            not after["problems"]
            and bool(after["module"].get("published")) == bool(args.apply)
            and all(not row["page"].get("published") and not row["item"].get("published") for row in after["teachers"])
            and all(row["page"].get("published") and row["item"].get("published") for row in after["students"])
            and all(item.get("published") for item in after["headers"])
            and all(item.get("published") for item in after["interactions"])
            and all(not folder.get("locked") for folder in after["material_folders"])
        )
        print(json.dumps({"mode": "apply" if args.apply else "audit", "before": summary(before), "after": summary(after), "passed": passed}, indent=2))
        return 0 if (not args.apply or passed) else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", required=True)
    parser.add_argument("--materials-prefix", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    token = sys.stdin.readline().strip()
    if not token:
        print("Canvas token required on stdin", file=sys.stderr)
        return 2
    return asyncio.run(run(args, token))


if __name__ == "__main__":
    raise SystemExit(main())
