#!/usr/bin/env python3
"""Return the CCR Canvas source course to a fully staged template.

The source course contains every teacher guide, student guide, interaction,
rubric, and file, but it does not decide what a teacher publishes after
cloning. This script unpublishes all 36 instructional modules, the student
orientation, the replacement home page, and their child content. It also
relocks curriculum and licensed file folders. Nothing is deleted.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys

import httpx

from build_4sw_wk1 import BASE, COURSE_ID
from build_course_orientation import (
    HOME_TITLE,
    ORIENTATION_MODULE,
    STUDENT_TITLE,
    TEACHER_MODULE,
    TEACHER_TITLE,
)

WEEK_PATTERN = re.compile(r"^[1-6]SW Wk[0-6]:")
LOCKED_FOLDER_PREFIXES = (
    "course files/CCR Materials",
    "course files/Licensed",
)
INERT_FRONT_PAGE_TITLE = "Welcome!"


async def api(client: httpx.AsyncClient, method: str, path: str, **kwargs):
    response = await client.request(method, f"{BASE}/api/v1{path}", **kwargs)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"Canvas {method} {path} returned {response.status_code}: "
            f"{response.text[:500]}"
        ) from exc
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


def target_module(module: dict) -> bool:
    name = module.get("name") or ""
    return bool(WEEK_PATTERN.match(name)) or name in {
        ORIENTATION_MODULE,
        TEACHER_MODULE,
    }


async def stage_interaction(client: httpx.AsyncClient, item: dict) -> None:
    content_id = item.get("content_id")
    kind = item.get("type")
    if kind == "Assignment":
        await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/assignments/{content_id}",
            data={
                "assignment[published]": "false",
                "assignment[notify_of_update]": "false",
            },
        )
    elif kind == "Discussion":
        await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/discussion_topics/{content_id}",
            data={"published": "false"},
        )
    elif kind == "Quiz":
        await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/quizzes/{content_id}",
            data={
                "quiz[published]": "false",
                "quiz[notify_of_update]": "false",
            },
        )


async def stage(client: httpx.AsyncClient) -> None:
    # Canvas will reject unpublishing the active front page while the course
    # default view is still Pages. Return the course to Modules first.
    await api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}",
        data={"course[default_view]": "modules"},
    )

    pages = await paged(client, f"/courses/{COURSE_ID}/pages")
    home_matches = [page for page in pages if page.get("title") == HOME_TITLE]
    if len(home_matches) != 1:
        raise RuntimeError(
            f"expected one page {HOME_TITLE!r}; found {len(home_matches)}"
        )
    if home_matches[0].get("front_page"):
        placeholders = [
            page for page in pages if page.get("title") == INERT_FRONT_PAGE_TITLE
        ]
        if len(placeholders) != 1:
            raise RuntimeError(
                f"expected one inert front page {INERT_FRONT_PAGE_TITLE!r}; "
                f"found {len(placeholders)}"
            )
        placeholder = placeholders[0]
        await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/pages/{placeholder['url']}",
            data={
                "wiki_page[published]": "true",
                "wiki_page[front_page]": "true",
                "wiki_page[editing_roles]": "teachers",
                "wiki_page[notify_of_update]": "false",
            },
        )
        pages = await paged(client, f"/courses/{COURSE_ID}/pages")

    for title in {HOME_TITLE, STUDENT_TITLE, TEACHER_TITLE}:
        matches = [page for page in pages if page.get("title") == title]
        if len(matches) != 1:
            raise RuntimeError(f"expected one page {title!r}; found {len(matches)}")
        page = matches[0]
        if not page.get("published") and not page.get("front_page"):
            continue
        update = {
            "wiki_page[published]": "false",
            "wiki_page[editing_roles]": "teachers",
            "wiki_page[notify_of_update]": "false",
        }
        if title == HOME_TITLE:
            update["wiki_page[front_page]"] = "false"
        await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/pages/{page['url']}",
            data=update,
        )

    modules = await paged(client, f"/courses/{COURSE_ID}/modules")
    for module in [entry for entry in modules if target_module(entry)]:
        module_id = module["id"]
        if module.get("published"):
            await api(
                client,
                "PUT",
                f"/courses/{COURSE_ID}/modules/{module_id}",
                data={"module[published]": "false"},
            )
        items = await paged(
            client, f"/courses/{COURSE_ID}/modules/{module_id}/items"
        )
        for item in items:
            if not item.get("published"):
                continue
            if item.get("type") == "Page" and item.get("page_url"):
                await api(
                    client,
                    "PUT",
                    f"/courses/{COURSE_ID}/pages/{item['page_url']}",
                    data={
                        "wiki_page[published]": "false",
                        "wiki_page[editing_roles]": "teachers",
                        "wiki_page[notify_of_update]": "false",
                    },
                )
            else:
                await stage_interaction(client, item)
            await api(
                client,
                "PUT",
                f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
                data={"module_item[published]": "false"},
            )

    folders = await paged(client, f"/courses/{COURSE_ID}/folders")
    for folder in folders:
        full_name = folder.get("full_name") or ""
        if not full_name.startswith(LOCKED_FOLDER_PREFIXES):
            continue
        if not folder.get("locked"):
            await api(
                client,
                "PUT",
                f"/folders/{folder['id']}",
                data={"locked": "true"},
            )

async def audit(client: httpx.AsyncClient) -> dict:
    course = await api(client, "GET", f"/courses/{COURSE_ID}")
    modules = await paged(client, f"/courses/{COURSE_ID}/modules")
    targets = [module for module in modules if target_module(module)]
    pages = await paged(client, f"/courses/{COURSE_ID}/pages")
    page_by_title = {page.get("title"): page for page in pages}
    folders = await paged(client, f"/courses/{COURSE_ID}/folders")
    target_folders = [
        folder
        for folder in folders
        if (folder.get("full_name") or "").startswith(LOCKED_FOLDER_PREFIXES)
    ]
    published_items: list[str] = []
    published_content: list[str] = []
    for module in targets:
        items = await paged(
            client, f"/courses/{COURSE_ID}/modules/{module['id']}/items"
        )
        for item in items:
            if item.get("published"):
                published_items.append(f"{module['name']} :: {item.get('title')}")
            if item.get("type") == "Page" and item.get("page_url"):
                page = await api(
                    client,
                    "GET",
                    f"/courses/{COURSE_ID}/pages/{item['page_url']}",
                )
                if page.get("published"):
                    published_content.append(page.get("title"))
            elif item.get("type") == "Assignment":
                assignment = await api(
                    client,
                    "GET",
                    f"/courses/{COURSE_ID}/assignments/{item['content_id']}",
                )
                if assignment.get("published"):
                    published_content.append(assignment.get("name"))
            elif item.get("type") == "Discussion":
                discussion = await api(
                    client,
                    "GET",
                    f"/courses/{COURSE_ID}/discussion_topics/{item['content_id']}",
                )
                if discussion.get("published"):
                    published_content.append(discussion.get("title"))
            elif item.get("type") == "Quiz":
                quiz = await api(
                    client,
                    "GET",
                    f"/courses/{COURSE_ID}/quizzes/{item['content_id']}",
                )
                if quiz.get("published"):
                    published_content.append(quiz.get("title"))

    expected_pages = [HOME_TITLE, STUDENT_TITLE, TEACHER_TITLE]
    published_course_pages = [
        title
        for title in expected_pages
        if page_by_title.get(title, {}).get("published")
    ]
    published_modules = [
        module.get("name") for module in targets if module.get("published")
    ]
    unlocked_folders = [
        folder.get("full_name") for folder in target_folders if not folder.get("locked")
    ]
    week_modules = [
        module for module in targets if WEEK_PATTERN.match(module.get("name") or "")
    ]
    passed = (
        len(week_modules) == 36
        and course.get("default_view") == "modules"
        and not published_modules
        and not published_items
        and not published_content
        and not published_course_pages
        and not unlocked_folders
    )
    return {
        "course": {
            "id": course.get("id"),
            "default_view": course.get("default_view"),
        },
        "week_modules": len(week_modules),
        "published_modules": published_modules,
        "published_items": published_items,
        "published_content": published_content,
        "published_course_pages": published_course_pages,
        "locked_folders": len(target_folders) - len(unlocked_folders),
        "unlocked_folders": unlocked_folders,
        "passed": passed,
    }


async def main() -> None:
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as client:
        await stage(client)
        print(json.dumps(await audit(client), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
