#!/usr/bin/env python3
"""Configure the reviewed learner-facing Canvas course shell.

The script is intentionally narrow and repeat-safe. It publishes only the
reviewed course home and student orientation, keeps the teacher build and all
instructional weeks unpublished, and reduces learner navigation to Home,
Modules, and Grades. Use ``--audit`` for a read-only preview and ``--apply`` to
make the exact changes.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

import httpx

import build_course_orientation as orientation

BASE = orientation.common.BASE
COURSE_ID = orientation.COURSE_ID
KEEP_TABS = {"home", "modules", "grades", "settings"}
LEGACY_TEMPLATE_PAGES = {"Meet Your Teacher", "Quick Links", "Schedule", "Syllabus", "Welcome!"}


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


def exactly_one(records: list[dict], key: str, value: str, label: str) -> dict:
    matches = [record for record in records if record.get(key) == value]
    if len(matches) != 1:
        raise RuntimeError(f"expected one {label}; found {len(matches)}")
    return matches[0]


async def snapshot(client: httpx.AsyncClient) -> dict:
    course = await api(client, "GET", f"/courses/{COURSE_ID}")
    modules = await paged(client, f"/courses/{COURSE_ID}/modules")
    pages = await paged(client, f"/courses/{COURSE_ID}/pages")
    tabs = await api(client, "GET", f"/courses/{COURSE_ID}/tabs")
    enrollments = await paged(
        client,
        f"/courses/{COURSE_ID}/enrollments",
        {"type[]": "StudentEnrollment", "state[]": "active"},
    )

    home = exactly_one(pages, "title", orientation.HOME_TITLE, "replacement home page")
    student = exactly_one(
        pages, "title", orientation.STUDENT_TITLE, "student orientation page"
    )
    orientation_module = exactly_one(
        modules,
        "name",
        orientation.ORIENTATION_MODULE,
        "student orientation module",
    )
    teacher_module = exactly_one(
        modules, "name", orientation.TEACHER_MODULE, "teacher build module"
    )
    orientation_items = await paged(
        client, f"/courses/{COURSE_ID}/modules/{orientation_module['id']}/items"
    )
    student_item = exactly_one(
        orientation_items,
        "page_url",
        student["url"],
        "student orientation module item",
    )

    active_tabs = [
        {"id": tab.get("id"), "label": tab.get("label")}
        for tab in tabs
        if not tab.get("hidden")
    ]
    return {
        "course": {
            "id": course.get("id"),
            "default_view": course.get("default_view"),
            "active_student_enrollments": len(enrollments),
        },
        "home": {
            "id": home.get("page_id"),
            "url": home.get("url"),
            "published": home.get("published"),
            "front_page": home.get("front_page"),
        },
        "orientation": {
            "module_id": orientation_module.get("id"),
            "module_published": orientation_module.get("published"),
            "page_url": student.get("url"),
            "page_published": student.get("published"),
            "item_id": student_item.get("id"),
            "item_published": student_item.get("published"),
        },
        "teacher_module": {
            "id": teacher_module.get("id"),
            "published": teacher_module.get("published"),
        },
        "active_tabs": active_tabs,
        "objects": {
            "home": home,
            "student": student,
            "orientation_module": orientation_module,
            "student_item": student_item,
            "teacher_module": teacher_module,
            "tabs": tabs,
        },
    }


async def apply(client: httpx.AsyncClient, before: dict) -> None:
    objects = before["objects"]
    home = objects["home"]
    student = objects["student"]
    orientation_module = objects["orientation_module"]
    student_item = objects["student_item"]
    teacher_module = objects["teacher_module"]

    await api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/pages/{home['url']}",
        data={
            "wiki_page[published]": "true",
            "wiki_page[front_page]": "true",
            "wiki_page[editing_roles]": "teachers",
            "wiki_page[notify_of_update]": "false",
        },
    )
    await api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/pages/{student['url']}",
        data={
            "wiki_page[published]": "true",
            "wiki_page[editing_roles]": "teachers",
            "wiki_page[notify_of_update]": "false",
        },
    )
    await api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/modules/{orientation_module['id']}/items/{student_item['id']}",
        data={"module_item[published]": "true", "module_item[position]": "1"},
    )
    await api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/modules/{orientation_module['id']}",
        data={"module[published]": "true", "module[position]": "1"},
    )
    await api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/modules/{teacher_module['id']}",
        data={"module[published]": "false"},
    )
    await api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}",
        data={"course[default_view]": "wiki"},
    )

    positions = {"modules": 2, "grades": 3}
    for tab in objects["tabs"]:
        tab_id = str(tab.get("id"))
        if tab_id in {"home", "settings"}:
            continue
        data = {"hidden": "false" if tab_id in KEEP_TABS else "true"}
        if tab_id in positions:
            data["position"] = str(positions[tab_id])
        await api(
            client, "PUT", f"/courses/{COURSE_ID}/tabs/{tab_id}", data=data
        )
    pages = await paged(client, f"/courses/{COURSE_ID}/pages")
    for page in pages:
        if page.get("title") not in LEGACY_TEMPLATE_PAGES:
            continue
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


def public_snapshot(value: dict) -> dict:
    return {key: item for key, item in value.items() if key != "objects"}


async def run(mode: str, token: str) -> int:
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as client:
        before = await snapshot(client)
        if mode == "apply":
            await apply(client, before)
        after = await snapshot(client)
        expected_tabs = {"home", "modules", "grades", "settings"}
        active_tab_ids = {row["id"] for row in after["active_tabs"]}
        passed = (
            after["course"]["default_view"] == "wiki"
            and after["home"]["published"]
            and after["home"]["front_page"]
            and after["orientation"]["module_published"]
            and after["orientation"]["page_published"]
            and after["orientation"]["item_published"]
            and not after["teacher_module"]["published"]
            and active_tab_ids == expected_tabs
        )
        print(
            json.dumps(
                {
                    "mode": mode,
                    "before": public_snapshot(before),
                    "after": public_snapshot(after),
                    "passed": passed,
                },
                indent=2,
            )
        )
        return 0 if (mode == "audit" or passed) else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    token = sys.stdin.readline().strip()
    if not token:
        print("Canvas token required on stdin", file=sys.stderr)
        return 2
    return asyncio.run(run("apply" if args.apply else "audit", token))


if __name__ == "__main__":
    raise SystemExit(main())
