#!/usr/bin/env python3
"""Read-only QA for the unpublished 4SW Wk2-6SW Wk6 Canvas transfer.

The Canvas token is read once from stdin. The script never writes to Canvas,
prints the token, or accepts it as a command-line argument.
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
CANVAS_DIR = Path(__file__).resolve().parent
BUILDERS = [
    *(CANVAS_DIR / f"build_4sw_wk{week}.py" for week in range(2, 7)),
    *(CANVAS_DIR / f"build_5sw_wk{week}.py" for week in range(1, 7)),
    *(CANVAS_DIR / f"build_6sw_wk{week}.py" for week in range(1, 7)),
]
ORIENTATION_MODULE = "START HERE: CCE Course Orientation"
TEACHER_MODULE = "Teacher Build: Licensed Resources"
TEACHER_TITLE = "TEACHER: CCE Course Launch Guide"
STUDENT_TITLE = "STUDENT: Start Here - How CCE Works"


class BodyAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.images: list[dict[str, str | None]] = []
        self.links: list[str] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag.lower() == "img":
            self.images.append(values)
        if tag.lower() == "a" and values.get("href"):
            self.links.append(str(values["href"]))

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.text.append(data.strip())


def module_name(builder: Path) -> str:
    tree = ast.parse(builder.read_text(encoding="utf-8"), filename=str(builder))
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(
            isinstance(target, ast.Name) and target.id == "MODULE_NAME"
            for target in targets
        ):
            continue
        value = node.value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return value.value
    raise ValueError(f"{builder.relative_to(ROOT)} has no literal MODULE_NAME")


def expected_modules() -> list[str]:
    return [module_name(builder) for builder in BUILDERS]


async def api(client: httpx.AsyncClient, path: str) -> object:
    response = await client.get(f"{BASE}/api/v1{path}")
    response.raise_for_status()
    return response.json()


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


async def audit_module(client: httpx.AsyncClient, module: dict) -> dict:
    module_id = module["id"]
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    problems: list[str] = []
    pages: list[dict] = []
    interactions: list[dict] = []
    file_ids: set[int] = set()

    if module.get("published"):
        problems.append("module is published")
    positions = [item.get("position") for item in items]
    if positions != list(range(1, len(items) + 1)):
        problems.append(f"module positions are not consecutive: {positions}")
    for item in items:
        if item.get("published"):
            problems.append(
                f"module item is published: {item.get('id')} {item.get('title')}"
            )

    subheaders = [item for item in items if item.get("type") == "SubHeader"]
    subheader_days = [day_number(item.get("title") or "") for item in subheaders]
    if subheader_days != [1, 2, 3, 4, 5]:
        problems.append(f"day subheaders are not Day 1-5 in order: {subheader_days}")

    for item in items:
        kind = item.get("type")
        if kind == "SubHeader":
            continue
        if kind == "Quiz" and item.get("content_id"):
            quiz = await api(
                client, f"/courses/{COURSE_ID}/quizzes/{item['content_id']}"
            )
            questions = await paged(
                client, f"/courses/{COURSE_ID}/quizzes/{item['content_id']}/questions"
            )
            if quiz.get("published"):
                problems.append(f"quiz is published: {quiz.get('id')}")
            if quiz.get("quiz_type") != "practice_quiz":
                problems.append(
                    f"quiz is not practice: {quiz.get('id')} {quiz.get('quiz_type')}"
                )
            if not questions:
                problems.append(f"quiz has no questions: {quiz.get('id')}")
            interactions.append(
                {
                    "type": "Quiz",
                    "id": quiz.get("id"),
                    "title": quiz.get("title"),
                    "questions": len(questions),
                }
            )
            continue
        if kind == "Discussion" and item.get("content_id"):
            topic = await api(
                client, f"/courses/{COURSE_ID}/discussion_topics/{item['content_id']}"
            )
            if topic.get("published"):
                problems.append(f"discussion is published: {topic.get('id')}")
            interactions.append(
                {
                    "type": "Discussion",
                    "id": topic.get("id"),
                    "title": topic.get("title"),
                }
            )
            continue
        if kind == "Assignment" and item.get("content_id"):
            assignment = await api(
                client, f"/courses/{COURSE_ID}/assignments/{item['content_id']}"
            )
            if assignment.get("published"):
                problems.append(f"assignment is published: {assignment.get('id')}")
            if not assignment.get("submission_types"):
                problems.append(
                    f"assignment has no submission route: {assignment.get('id')}"
                )
            interactions.append(
                {
                    "type": "Assignment",
                    "id": assignment.get("id"),
                    "title": assignment.get("name"),
                    "submission_types": assignment.get("submission_types"),
                }
            )
            continue
        if kind != "Page" or not item.get("page_url"):
            problems.append(f"unsupported module item: {item.get('id')} {kind}")
            continue

        page = await api(client, f"/courses/{COURSE_ID}/pages/{item['page_url']}")
        body = page.get("body") or ""
        parser = BodyAudit()
        parser.feed(body)
        visible_text = " ".join(parser.text).lower()
        title = page.get("title") or item.get("title") or ""
        role = (
            "teacher"
            if title.startswith("TEACHER:")
            else "student"
            if title.startswith("STUDENT:")
            else "other"
        )
        if page.get("published"):
            problems.append(f"page is published: {page.get('url')}")
        unresolved = sorted(set(re.findall(r"\{\{[^}]+\}\}", body)))
        if unresolved:
            problems.append(f"unresolved fields in {page.get('url')}: {unresolved}")
        if "enhanceable_content" in body:
            problems.append(f"legacy Canvas tabs in {page.get('url')}")
        for image in parser.images:
            if not (image.get("alt") or "").strip():
                problems.append(f"image missing useful alt text in {page.get('url')}")
        if role == "student":
            for label in ("today you will", "exit check", "you are done when"):
                if label not in visible_text:
                    problems.append(
                        f"student page missing '{label}': {page.get('url')}"
                    )
            if "absent" not in visible_text and "platform" not in visible_text:
                problems.append(
                    f"student page missing absence/platform route: {page.get('url')}"
                )
        elif role == "teacher":
            for label in ("before class", "50-minute flow"):
                if label not in visible_text:
                    problems.append(
                        f"teacher page missing '{label}': {page.get('url')}"
                    )
        else:
            problems.append(f"paired page lacks TEACHER/STUDENT title: {title}")

        file_ids.update(int(value) for value in re.findall(r"/files/(\d+)", body))
        pages.append(
            {
                "role": role,
                "day": day_number(title),
                "title": title,
                "url": page.get("url"),
                "body_chars": len(body),
                "images": len(parser.images),
                "links": parser.links,
            }
        )

    teacher_pages = [page for page in pages if page["role"] == "teacher"]
    student_pages = [page for page in pages if page["role"] == "student"]
    teacher_days = [page["day"] for page in teacher_pages]
    student_days = [page["day"] for page in student_pages]
    if len(teacher_days) != 5 or set(teacher_days) != {1, 2, 3, 4, 5}:
        problems.append("teacher page set is not exactly Day 1-5")
    if len(student_days) != 5 or set(student_days) != {1, 2, 3, 4, 5}:
        problems.append("student page set is not exactly Day 1-5")
    for teacher in teacher_pages:
        student = next(
            (page for page in student_pages if page["day"] == teacher["day"]), None
        )
        if student and not any(
            str(student["url"]) in href for href in teacher["links"]
        ):
            problems.append(
                f"Day {teacher['day']} teacher page does not link to student page"
            )

    files: list[dict] = []
    folders: dict[int, dict] = {}
    for file_id in sorted(file_ids):
        try:
            record = await api(client, f"/files/{file_id}")
        except httpx.HTTPStatusError as exc:
            problems.append(
                f"file {file_id} does not resolve: HTTP {exc.response.status_code}"
            )
            continue
        folder_id = record.get("folder_id")
        if folder_id and folder_id not in folders:
            folder = await api(client, f"/folders/{folder_id}")
            folders[folder_id] = folder
            if not folder.get("locked"):
                problems.append(
                    f"referenced file folder is unlocked: {folder_id} {folder.get('full_name')}"
                )
        files.append(
            {
                "id": file_id,
                "name": record.get("display_name"),
                "size": record.get("size"),
                "folder_id": folder_id,
            }
        )

    return {
        "id": module_id,
        "name": module.get("name"),
        "items": len(items),
        "pages": len(pages),
        "interactions": len(interactions),
        "files": len(files),
        "locked_folders": len(folders),
        "problems": problems,
        "passed": not problems,
    }


async def audit_orientation(client: httpx.AsyncClient, modules: list[dict]) -> dict:
    problems: list[str] = []
    orientation_matches = [
        module for module in modules if module.get("name") == ORIENTATION_MODULE
    ]
    teacher_matches = [
        module for module in modules if module.get("name") == TEACHER_MODULE
    ]
    if len(orientation_matches) != 1:
        problems.append(
            f"expected one orientation module; found {len(orientation_matches)}"
        )
    if len(teacher_matches) != 1:
        problems.append(
            f"expected one teacher-build module; found {len(teacher_matches)}"
        )
    if problems:
        return {"problems": problems, "passed": False}

    orientation = orientation_matches[0]
    teacher_module = teacher_matches[0]
    if orientation.get("published"):
        problems.append("orientation module is published")
    if teacher_module.get("published"):
        problems.append("teacher-build module is published")
    if orientation.get("position") != 1:
        problems.append(
            f"orientation module is not first: position={orientation.get('position')}"
        )

    orientation_items = await paged(
        client, f"/courses/{COURSE_ID}/modules/{orientation['id']}/items"
    )
    teacher_items = await paged(
        client, f"/courses/{COURSE_ID}/modules/{teacher_module['id']}/items"
    )
    student_items = [
        item
        for item in orientation_items
        if item.get("type") == "Page" and item.get("title") == STUDENT_TITLE
    ]
    launch_items = [
        item
        for item in teacher_items
        if item.get("type") == "Page" and item.get("title") == TEACHER_TITLE
    ]
    if len(student_items) != 1:
        problems.append(
            f"expected one student orientation page item; found {len(student_items)}"
        )
    if len(launch_items) != 1:
        problems.append(
            f"expected one teacher launch page item; found {len(launch_items)}"
        )
    if len(orientation_items) != 1:
        problems.append(
            f"orientation module should contain one page; found {len(orientation_items)} items"
        )
    for item in [*orientation_items, *launch_items]:
        if item.get("published"):
            problems.append(
                f"orientation item is published: {item.get('id')} {item.get('title')}"
            )

    student_page = None
    teacher_page = None
    if student_items:
        student_page = await api(
            client, f"/courses/{COURSE_ID}/pages/{student_items[0]['page_url']}"
        )
    if launch_items:
        teacher_page = await api(
            client, f"/courses/{COURSE_ID}/pages/{launch_items[0]['page_url']}"
        )

    parsed: dict[str, BodyAudit] = {}
    for role, page, labels in (
        (
            "student",
            student_page,
            ("today you will", "exit check", "you are done when", "absent"),
        ),
        (
            "teacher",
            teacher_page,
            (
                "before the course opens",
                "publication sequence",
                "when the planned route fails",
            ),
        ),
    ):
        if not page:
            continue
        if page.get("published"):
            problems.append(f"{role} orientation page is published")
        body = page.get("body") or ""
        parser = BodyAudit()
        parser.feed(body)
        parsed[role] = parser
        visible_text = " ".join(parser.text).lower()
        for label in labels:
            if label not in visible_text:
                problems.append(f"{role} orientation page missing '{label}'")
        if re.search(r"\{\{[^}]+\}\}", body):
            problems.append(f"{role} orientation page has unresolved fields")
        if "enhanceable_content" in body:
            problems.append(f"{role} orientation page uses legacy Canvas tabs")

    if student_page and teacher_page:
        student_url = str(student_page.get("url"))
        if not any(student_url in href for href in parsed["teacher"].links):
            problems.append("teacher launch page does not link to student orientation")

    return {
        "module_id": orientation.get("id"),
        "teacher_module_id": teacher_module.get("id"),
        "student_page": student_page.get("url") if student_page else None,
        "teacher_page": teacher_page.get("url") if teacher_page else None,
        "problems": problems,
        "passed": not problems,
    }


async def run(token: str) -> int:
    names = expected_modules()
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=90
    ) as client:
        modules = await paged(client, f"/courses/{COURSE_ID}/modules")
        orientation_result = await audit_orientation(client, modules)
        global_problems: list[str] = []
        selected: list[dict] = []
        for name in names:
            week_key = name.split(":", 1)[0]
            week_matches = [
                module
                for module in modules
                if (module.get("name") or "").startswith(f"{week_key}:")
            ]
            if len(week_matches) != 1:
                found_names = [module.get("name") for module in week_matches]
                global_problems.append(
                    f"expected one {week_key} module; found {len(week_matches)}: {found_names}"
                )
            matches = [module for module in modules if module.get("name") == name]
            if len(matches) != 1:
                global_problems.append(
                    f"expected exactly one module named {name!r}; found {len(matches)}"
                )
                continue
            selected.append(matches[0])

        results = [await audit_module(client, module) for module in selected]
        summary = {
            "expected_modules": len(names),
            "found_modules": len(selected),
            "passed_modules": sum(1 for result in results if result["passed"]),
            "items": sum(result["items"] for result in results),
            "pages": sum(result["pages"] for result in results),
            "interactions": sum(result["interactions"] for result in results),
            "referenced_files": sum(result["files"] for result in results),
            "global_problems": global_problems,
            "orientation": orientation_result,
            "modules": results,
            "passed": orientation_result["passed"]
            and not global_problems
            and all(result["passed"] for result in results),
        }
        print(json.dumps(summary, indent=2))
        return 0 if summary["passed"] else 2


def main() -> int:
    try:
        names = expected_modules()
    except (SyntaxError, ValueError) as exc:
        print(f"Preflight failed: {exc}", file=sys.stderr)
        return 2
    if len(names) != 17 or len(set(names)) != 17:
        print(
            f"Preflight failed: expected 17 unique module names; found {len(names)}",
            file=sys.stderr,
        )
        return 2
    if "--preflight" in sys.argv[1:]:
        print(f"Preflight passed: {len(names)} unique expected Canvas modules.")
        return 0
    if sys.argv[1:]:
        print("usage: qa_remaining_unpublished.py [--preflight]", file=sys.stderr)
        return 2
    global httpx
    try:
        import httpx
    except ModuleNotFoundError:
        print(
            "httpx is required for live Canvas QA; run through `uv run --with httpx`",
            file=sys.stderr,
        )
        return 2
    token = sys.stdin.readline().strip()
    if not token:
        print("Canvas token required on stdin", file=sys.stderr)
        return 2
    return asyncio.run(run(token))


if __name__ == "__main__":
    raise SystemExit(main())
