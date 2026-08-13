#!/usr/bin/env python3
"""Read-only QA for the complete unpublished CCR Canvas course transfer.

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

from configure_assessment_map import (
    ASSESSMENTS,
    MAJOR_GROUP,
    MINOR_GROUP,
    SUBMISSION_LINK_MARKER,
)
from configure_assessment_rubrics import NOTE_MARKER, RUBRIC_PREFIX, RUBRICS

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
ROOT = Path(__file__).resolve().parents[2]
CANVAS_DIR = Path(__file__).resolve().parent
BUILDERS = [
    *(CANVAS_DIR / f"build_wk{week}.py" for week in range(6)),
    *(CANVAS_DIR / f"build_2sw_wk{week}.py" for week in range(1, 7)),
    *(CANVAS_DIR / f"build_3sw_wk{week}.py" for week in range(1, 7)),
    *(CANVAS_DIR / f"build_4sw_wk{week}.py" for week in range(1, 7)),
    *(CANVAS_DIR / f"build_5sw_wk{week}.py" for week in range(1, 7)),
    *(CANVAS_DIR / f"build_6sw_wk{week}.py" for week in range(1, 7)),
]
ORIENTATION_MODULE = "START HERE: CCE Course Orientation"
TEACHER_MODULE = "Teacher Build: Licensed Resources"
TEACHER_TITLE = "TEACHER: CCE Course Launch Guide"
STUDENT_TITLE = "STUDENT: Start Here - How CCE Works"
HOME_TITLE = "Career and College Exploration Home"
CONTRACT_SECTION_RE = re.compile(
    r"<section\b[^>]*\bdata-cce-lesson-contract\s*=\s*['\"]1['\"][^>]*>"
    r".*?</section>",
    re.I | re.S,
)
TEACHER_LEGACY_CONTRACT_RE = re.compile(
    r'<strong\b[^>]*>\s*topic\s*:?.*?'
    r'<strong\b[^>]*>\s*objective\s*:?.*?'
    r'<strong\b[^>]*>\s*teks\s*:?.*?'
    r'<strong\b[^>]*>\s*demonstration of learning\s*:?',
    re.I | re.S,
)
STUDENT_LEGACY_CONTRACT_RE = re.compile(
    r'<strong\b[^>]*>\s*topic\s*:?.*?'
    r'<strong\b[^>]*>\s*(?:objective|i can|today[’\']s learning)\s*:?.*?'
    r'<strong\b[^>]*>\s*show (?:your|my) learning\s*:?',
    re.I | re.S,
)
REQUEST_CONCURRENCY = 8
_request_semaphore: asyncio.Semaphore | None = None
_object_tasks: dict[str, asyncio.Task[object]] = {}
_paged_tasks: dict[str, asyncio.Task[list[dict]]] = {}


class BodyAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.images: list[dict[str, str | None]] = []
        self.links: list[str] = []
        self.text: list[str] = []
        self.body_h1 = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag.lower() == "img":
            self.images.append(values)
        if tag.lower() == "a" and values.get("href"):
            self.links.append(str(values["href"]))
        if tag.lower() == "h1":
            self.body_h1 += 1

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


async def _api(client: httpx.AsyncClient, path: str) -> object:
    if _request_semaphore is None:
        raise RuntimeError("request semaphore was not initialized")
    async with _request_semaphore:
        response = await client.get(f"{BASE}/api/v1{path}")
    response.raise_for_status()
    return response.json()


async def api(client: httpx.AsyncClient, path: str) -> object:
    """Return one exact GET result, sharing repeated reads across the audit."""

    task = _object_tasks.get(path)
    if task is None:
        task = asyncio.create_task(_api(client, path))
        _object_tasks[path] = task
    return await task


async def _paged(client: httpx.AsyncClient, path: str) -> list[dict]:
    results: list[dict] = []
    url: str | None = f"{BASE}/api/v1{path}"
    params: dict[str, int] | None = {"per_page": 100}
    while url:
        if _request_semaphore is None:
            raise RuntimeError("request semaphore was not initialized")
        async with _request_semaphore:
            response = await client.get(url, params=params)
        response.raise_for_status()
        results.extend(response.json())
        url = response.links.get("next", {}).get("url")
        params = None
    return results


async def paged(client: httpx.AsyncClient, path: str) -> list[dict]:
    """Return one paginated GET result, sharing repeated reads across the audit."""

    task = _paged_tasks.get(path)
    if task is None:
        task = asyncio.create_task(_paged(client, path))
        _paged_tasks[path] = task
    return await task


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
            if (
                float(assignment.get("points_possible") or 0) == 0
                and assignment.get("omit_from_final_grade") is not True
            ):
                problems.append(
                    f"grade-neutral assignment counts toward final grade: {assignment.get('id')}"
                )
            submission_types = assignment.get("submission_types") or []
            if not set(submission_types) - {"none", "not_graded"}:
                problems.append(
                    f"assignment has no submission route: {assignment.get('id')}"
                )
            interactions.append(
                {
                    "type": "Assignment",
                    "id": assignment.get("id"),
                    "title": assignment.get("name"),
                    "submission_types": submission_types,
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
        contract_sections = CONTRACT_SECTION_RE.findall(body)
        if len(contract_sections) != 1:
            problems.append(
                f"page must contain exactly one marked lesson contract; found "
                f"{len(contract_sections)}: {page.get('url')}"
            )
        outside_contract = CONTRACT_SECTION_RE.sub("", body)
        legacy_pattern = (
            TEACHER_LEGACY_CONTRACT_RE
            if role == "teacher"
            else STUDENT_LEGACY_CONTRACT_RE
            if role == "student"
            else None
        )
        if legacy_pattern and legacy_pattern.search(outside_contract):
            problems.append(
                f"page contains a duplicate legacy lesson contract: {page.get('url')}"
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
            if (image.get("loading") or "").lower() != "lazy":
                problems.append(f"image missing loading=lazy in {page.get('url')}")
        if role == "student":
            required_sections = {
                "topic": ("topic:",),
                "objective": ("objective:", "i can:"),
                "show your learning": ("show your learning:", "show my learning:"),
                "today you will": (
                    "today you will",
                    "what you will do",
                ),
                "you are done when": ("you are done when", "done when"),
            }
            strong_label_patterns = {
                "topic": r"<strong\b[^>]*>\s*topic\s*:?\s*</strong>",
                "objective": r"<strong\b[^>]*>\s*(?:objective|i can)\s*:?\s*</strong>",
                "show your learning": r"<strong\b[^>]*>\s*show (?:your|my) learning\s*:?\s*</strong>",
            }
            for label, aliases in required_sections.items():
                visible_match = any(alias in visible_text for alias in aliases)
                semantic_match = bool(
                    label in strong_label_patterns
                    and re.search(
                        strong_label_patterns[label], body, flags=re.IGNORECASE
                    )
                )
                if not visible_match and not semantic_match:
                    problems.append(
                        f"student page missing '{label}': {page.get('url')}"
                    )
            if not any(
                label in visible_text for label in ("absent", "absence", "platform")
            ):
                problems.append(
                    f"student page missing absence/platform route: {page.get('url')}"
                )
        elif role == "teacher":
            required_sections = {
                "topic": ("topic:",),
                "objective": ("objective:",),
                "teks": ("teks:",),
                "demonstration of learning": ("demonstration of learning:",),
                "before class": ("before class", "before students arrive"),
                "50-minute flow": (
                    "50-minute flow",
                    "50-minute lesson flow",
                    "50 minute flow",
                    "50 minute lesson flow",
                ),
            }
            for label, aliases in required_sections.items():
                if not any(alias in visible_text for alias in aliases):
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
        if record.get("locked") is not True:
            problems.append(
                f"referenced file is unlocked: {file_id} {record.get('display_name')}"
            )
        if folder_id and folder_id not in folders:
            folder = await api(client, f"/folders/{folder_id}")
            folders[folder_id] = folder
            if not folder.get("locked"):
                problems.append(
                    f"referenced file folder is unlocked: {folder_id} {folder.get('full_name')}"
                )
            folder_files = await paged(client, f"/folders/{folder_id}/files")
            unlocked = sorted(
                file.get("id")
                for file in folder_files
                if file.get("locked") is not True
            )
            if unlocked:
                problems.append(
                    f"referenced folder contains unlocked files: {folder_id} {unlocked}"
                )
        files.append(
            {
                "id": file_id,
                "name": record.get("display_name"),
                "size": record.get("size"),
                "folder_id": folder_id,
                "locked": record.get("locked"),
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
    home_page = None
    if student_items:
        student_page = await api(
            client, f"/courses/{COURSE_ID}/pages/{student_items[0]['page_url']}"
        )
    if launch_items:
        teacher_page = await api(
            client, f"/courses/{COURSE_ID}/pages/{launch_items[0]['page_url']}"
        )
    course_pages = await paged(client, f"/courses/{COURSE_ID}/pages")
    home_matches = [page for page in course_pages if page.get("title") == HOME_TITLE]
    if len(home_matches) != 1:
        problems.append(
            f"expected one replacement course-home page; found {len(home_matches)}"
        )
    elif home_matches:
        home_page = await api(
            client, f"/courses/{COURSE_ID}/pages/{home_matches[0]['url']}"
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
        (
            "home",
            home_page,
            (
                "start today's lesson",
                "how this course works",
                "if you were absent",
                "grades and feedback",
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
        if parser.body_h1:
            problems.append(
                f"{role} orientation page contains {parser.body_h1} body H1 heading(s); "
                "Canvas already supplies the page-title H1"
            )

    if student_page and teacher_page:
        student_url = str(student_page.get("url"))
        if not any(student_url in href for href in parsed["teacher"].links):
            problems.append("teacher launch page does not link to student orientation")
    if student_page and home_page:
        student_url = str(student_page.get("url"))
        if not any(student_url in href for href in parsed["home"].links):
            problems.append("replacement course-home page does not link to orientation")
        if not any(
            f"/courses/{COURSE_ID}/modules" in href for href in parsed["home"].links
        ):
            problems.append("replacement course-home page does not link to Modules")

    return {
        "module_id": orientation.get("id"),
        "teacher_module_id": teacher_module.get("id"),
        "student_page": student_page.get("url") if student_page else None,
        "teacher_page": teacher_page.get("url") if teacher_page else None,
        "home_page": home_page.get("url") if home_page else None,
        "problems": problems,
        "passed": not problems,
    }


async def audit_assessment_map(client: httpx.AsyncClient, modules: list[dict]) -> dict:
    problems: list[str] = []
    course = await api(client, f"/courses/{COURSE_ID}")
    groups = await paged(
        client, f"/courses/{COURSE_ID}/assignment_groups?include[]=assignments"
    )
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    rubrics = await paged(client, f"/courses/{COURSE_ID}/rubrics")
    rubric_specs = {spec.assignment_title: spec for spec in RUBRICS}
    module_by_name = {module.get("name"): module for module in modules}
    group_by_name: dict[str, dict] = {}
    for name, expected_weight in ((MINOR_GROUP, 40), (MAJOR_GROUP, 60)):
        matches = [group for group in groups if group.get("name") == name]
        if len(matches) != 1:
            problems.append(
                f"expected one assignment group {name!r}; found {len(matches)}"
            )
            continue
        group = matches[0]
        group_by_name[name] = group
        if float(group.get("group_weight") or 0) != expected_weight:
            problems.append(
                f"assignment group {name!r} weight is {group.get('group_weight')}, "
                f"expected {expected_weight}"
            )
    if not course.get("apply_assignment_group_weights"):
        problems.append("course assignment-group weighting is not enabled")

    mapped_ids: set[int] = set()
    mapped_counts = {MINOR_GROUP: 0, MAJOR_GROUP: 0}
    rows: list[dict] = []
    for assessment in ASSESSMENTS:
        matches = [
            assignment
            for assignment in assignments
            if assignment.get("name") == assessment.title
        ]
        if len(matches) != 1:
            problems.append(
                f"expected one mapped assignment {assessment.title!r}; found {len(matches)}"
            )
            continue
        assignment = matches[0]
        assignment_detail = await api(
            client,
            f"/courses/{COURSE_ID}/assignments/{assignment['id']}?include[]=rubric",
        )
        mapped_ids.add(int(assignment["id"]))
        mapped_counts[assessment.group] += 1
        group = group_by_name.get(assessment.group)
        if group and assignment.get("assignment_group_id") != group.get("id"):
            problems.append(
                f"mapped assignment is in the wrong group: {assessment.title}"
            )
        if float(assignment.get("points_possible") or 0) != 100:
            problems.append(f"mapped assignment is not 100 points: {assessment.title}")
        if assignment.get("grading_type") != "points":
            problems.append(
                f"mapped assignment is not points-graded: {assessment.title}"
            )
        if assignment.get("published"):
            problems.append(f"mapped assignment is published: {assessment.title}")
        if NOTE_MARKER not in (assignment_detail.get("description") or ""):
            problems.append(
                f"mapped assignment is missing the raw-to-100 conversion note: {assessment.title}"
            )
        submission_types = assignment.get("submission_types") or []
        if not set(submission_types) - {"none", "not_graded"}:
            problems.append(
                f"mapped assignment has no submission route: {assessment.title}"
            )
        rubric_title = RUBRIC_PREFIX + assessment.title
        rubric_matches = [
            rubric for rubric in rubrics if rubric.get("title") == rubric_title
        ]
        rubric_id = None
        if len(rubric_matches) != 1:
            problems.append(
                f"expected one advisory rubric {rubric_title!r}; found {len(rubric_matches)}"
            )
        else:
            rubric = rubric_matches[0]
            rubric_id = rubric.get("id")
            rubric_detail = await api(
                client,
                f"/courses/{COURSE_ID}/rubrics/{rubric_id}?include[]=associations",
            )
            spec = rubric_specs[assessment.title]
            criteria = rubric_detail.get("data") or []
            if len(criteria) not in {3, 4, 6}:
                problems.append(
                    f"advisory rubric has unexpected criterion count for {assessment.title}: {len(criteria)}"
                )
            points = sum(float(criterion.get("points") or 0) for criterion in criteria)
            if points != spec.points or float(rubric_detail.get("points_possible") or 0) != spec.points:
                problems.append(
                    f"advisory rubric raw total is wrong for {assessment.title}: criteria={points:g} rubric={rubric_detail.get('points_possible')} expected={spec.points}"
                )
            for criterion in criteria:
                ratings = criterion.get("ratings") or []
                if len(ratings) < 5 or not any(
                    float(rating.get("points") or 0) == 0 for rating in ratings
                ):
                    problems.append(
                        f"advisory rubric criterion lacks a complete zero-point scale for {assessment.title}: {criterion.get('description')}"
                    )
            associations = [
                entry
                for entry in (rubric_detail.get("associations") or [])
                if entry.get("association_type") == "Assignment"
                and int(entry.get("association_id")) == int(assignment["id"])
            ]
            if len(associations) != 1:
                problems.append(
                    f"advisory rubric is not associated exactly once with {assessment.title}"
                )
            else:
                association = associations[0]
                if association.get("use_for_grading"):
                    problems.append(
                        f"raw rubric is incorrectly driving the 100-point grade: {assessment.title}"
                    )
                if association.get("purpose") != "grading":
                    problems.append(
                        f"advisory rubric is not available for scoring: {assessment.title}"
                    )
            if assignment_detail.get("use_rubric_for_grading") is not False:
                problems.append(
                    f"assignment does not expose the rubric as advisory: {assessment.title}"
                )
        module = module_by_name.get(assessment.module)
        if not module:
            problems.append(f"mapped assignment module is missing: {assessment.module}")
        else:
            items = await paged(
                client, f"/courses/{COURSE_ID}/modules/{module['id']}/items"
            )
            assignment_items = [
                item
                for item in items
                if item.get("type") == "Assignment"
                and item.get("content_id") == assignment.get("id")
            ]
            if len(assignment_items) != 1:
                problems.append(
                    f"mapped assignment is not in its module exactly once: {assessment.title}"
                )
            student_items = [
                item
                for item in items
                if item.get("type") == "Page"
                and (item.get("title") or "").startswith("STUDENT:")
                and f"Day {assessment.day}" in (item.get("title") or "")
            ]
            if len(student_items) != 1:
                problems.append(
                    f"mapped assignment has no unique Day {assessment.day} student guide: {assessment.title}"
                )
            else:
                student_page = await api(
                    client,
                    f"/courses/{COURSE_ID}/pages/{student_items[0]['page_url']}",
                )
                student_body = student_page.get("body") or ""
                expected_href = f"/courses/{COURSE_ID}/assignments/{assignment['id']}"
                if student_body.count(SUBMISSION_LINK_MARKER) != 1:
                    problems.append(
                        f"student guide lacks one mapped submission panel: {assessment.title}"
                    )
                if expected_href not in student_body:
                    problems.append(
                        f"student guide does not link to its mapped assignment: {assessment.title}"
                    )
        rows.append(
            {
                "id": assignment.get("id"),
                "title": assessment.title,
                "group": assessment.group,
                "module": assessment.module,
                "rubric_id": rubric_id,
            }
        )

    for name, group in group_by_name.items():
        extras = [
            assignment.get("name")
            for assignment in group.get("assignments") or []
            if int(assignment.get("id")) not in mapped_ids
        ]
        if extras:
            problems.append(f"unmapped assignments in {name}: {extras}")
    if mapped_counts != {MINOR_GROUP: 18, MAJOR_GROUP: 12}:
        problems.append(f"mapped assessment counts are wrong: {mapped_counts}")
    expected_rubric_titles = {RUBRIC_PREFIX + item.title for item in ASSESSMENTS}
    extra_rubrics = sorted(
        rubric.get("title")
        for rubric in rubrics
        if (rubric.get("title") or "").startswith(RUBRIC_PREFIX)
        and rubric.get("title") not in expected_rubric_titles
    )
    if extra_rubrics:
        problems.append(f"unmapped CCE advisory rubrics: {extra_rubrics}")

    return {
        "minor": mapped_counts[MINOR_GROUP],
        "major": mapped_counts[MAJOR_GROUP],
        "assignments": rows,
        "rubrics": sum(row.get("rubric_id") is not None for row in rows),
        "problems": problems,
        "passed": not problems,
    }


async def run(token: str) -> int:
    global _request_semaphore
    _request_semaphore = asyncio.Semaphore(REQUEST_CONCURRENCY)
    _object_tasks.clear()
    _paged_tasks.clear()
    names = expected_modules()
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=90
    ) as client:
        modules = await paged(client, f"/courses/{COURSE_ID}/modules")
        orientation_result = await audit_orientation(client, modules)
        assessment_result = await audit_assessment_map(client, modules)
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

        results = await asyncio.gather(
            *(audit_module(client, module) for module in selected)
        )
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
            "assessment_map": assessment_result,
            "modules": results,
            "passed": orientation_result["passed"]
            and assessment_result["passed"]
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
    if len(names) != 36 or len(set(names)) != 36:
        print(
            f"Preflight failed: expected 36 unique module names; found {len(names)}",
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
