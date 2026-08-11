"""Build the unpublished 3SW Week 4 Culinary Arts and Hospitality Canvas module."""

import asyncio
import json
import mimetypes
import re
import sys
from pathlib import Path
from urllib.parse import urlencode

import httpx

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
MODULE_NAME = "3SW Wk4: Culinary Arts and Hospitality"
ANNOTATION_TITLE = "PRACTICE: Culinary Twist Menu Design"
QUIZ_TITLE = "PRACTICE: Motivation Check"
RECOMMENDATION_TITLE = "MINOR 2: Hospitality Career and Business Recommendation"
MINOR_GROUP_NAME = "Minor Assessments (40%)"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/3sw/wk4"


def preflight():
    worksheet_names = (
        "3sw-wk4-hospitality-career-evidence-guide.pdf",
        "3sw-wk4-culinary-twist-menu-brief.pdf",
        "3sw-wk4-motivation-career-comparison.pdf",
        "3sw-wk4-hotel-rescue-cards.pdf",
        "3sw-wk4-hotel-rescue-response.pdf",
        "3sw-wk4-cater-create-event-brief.pdf",
        "3sw-wk4-hospitality-recommendation.pdf",
        "3sw-wk4-hospitality-minor-rubric.pdf",
    )
    visual_names = {
        1: (
            "fyf-hospitality-opener-optimized.jpg",
            "fyf-culinary-twist-plan.png",
            "fyf-culinary-twist-menu.png",
        ),
        2: ("fyf-motivation-types.png", "fyf-motivation-plan.png"),
        3: ("fyf-hotel-rescue-roles.png", "fyf-hotel-rescue-solutions.png"),
        4: ("fyf-cater-create-menu.png", "fyf-cater-create-experience.png"),
        5: ("fyf-irving-hospitality-context.png",),
    }
    required = [
        TEMPLATES / "3sw-wk4-student.html",
        TEMPLATES / "3sw-wk4-teacher.html",
        *(ROOT / "docs/resources/worksheets" / name for name in worksheet_names),
        *(
            ASSETS / f"day{day}" / name
            for day, names in visual_names.items()
            for name in names
        ),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"3SW Wk4 preflight missing required files: {missing}")


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower().replace("&", "and")).strip("-")


async def api(client, method, path, **kwargs):
    response = await client.request(method, f"{BASE}/api/v1{path}", **kwargs)
    response.raise_for_status()
    return response.json() if response.content else None


async def paged(client, path, params=None):
    output, url, query = [], f"{BASE}/api/v1{path}", {"per_page": 100, **(params or {})}
    while url:
        response = await client.get(url, params=query)
        response.raise_for_status()
        output += response.json()
        url, query = response.links.get("next", {}).get("url"), None
    return output


async def ensure_module(client):
    modules = await paged(client, f"/courses/{COURSE_ID}/modules")
    matches = [module for module in modules if module["name"] == MODULE_NAME]
    if len(matches) > 1:
        raise RuntimeError(
            f"Duplicate Canvas modules named {MODULE_NAME!r}: {[module['id'] for module in matches]}"
        )
    found = matches[0] if matches else None
    if found:
        return await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{found['id']}",
            data={"module[name]": MODULE_NAME, "module[published]": "false"},
        )
    return await api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/modules",
        data={"module[name]": MODULE_NAME, "module[published]": "false"},
    )


async def ensure_folder(client, path):
    current, folder = "", None
    for name in path.split("/")[1:]:
        target = f"{current}/{name}".strip("/")
        encoded = httpx.URL("/" + target).raw_path.decode("ascii").lstrip("/")
        response = await client.get(
            f"{BASE}/api/v1/courses/{COURSE_ID}/folders/by_path/{encoded}"
        )
        if response.status_code == 200 and response.json():
            folder = response.json()[-1]
        else:
            folder = await api(
                client,
                "POST",
                f"/courses/{COURSE_ID}/folders",
                data={
                    "name": name,
                    "parent_folder_path": "course files"
                    + (f"/{current}" if current else ""),
                    "locked": "true",
                },
            )
        current = target
    if folder and not folder.get("locked"):
        folder = await api(
            client, "PUT", f"/folders/{folder['id']}", data={"locked": "true"}
        )
    return folder


async def upload(client, path, folder_path):
    start = await api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/files",
        data={
            "name": path.name,
            "parent_folder_path": folder_path,
            "on_duplicate": "overwrite",
        },
    )
    response = await client.post(
        start["upload_url"],
        data=start["upload_params"],
        files={
            "file": (
                path.name,
                path.read_bytes(),
                mimetypes.guess_type(path.name)[0] or "application/octet-stream",
            )
        },
        follow_redirects=True,
    )
    response.raise_for_status()
    uploaded = response.json()
    record = await api(
        client, "PUT", f"/files/{uploaded['id']}", data={"locked": "true"}
    )
    if not record.get("locked"):
        raise RuntimeError(f"Canvas did not lock uploaded file {path.name!r}")
    return record


async def lock_folder_files(client, folder):
    current = await api(client, "GET", f"/folders/{folder['id']}")
    if not current.get("locked"):
        current = await api(
            client, "PUT", f"/folders/{folder['id']}", data={"locked": "true"}
        )
    if not current.get("locked"):
        raise RuntimeError(
            f"Canvas did not lock folder {folder.get('full_name') or folder['id']}"
        )
    for entry in await paged(client, f"/folders/{folder['id']}/files"):
        if not entry.get("locked"):
            await api(
                client, "PUT", f"/files/{entry['id']}", data={"locked": "true"}
            )
    final = await paged(client, f"/folders/{folder['id']}/files")
    unlocked = [
        entry.get("display_name") or entry.get("filename")
        for entry in final
        if not entry.get("locked")
    ]
    if unlocked:
        raise RuntimeError(f"Unlocked files remain in folder {folder['id']}: {unlocked}")
    return current, len(final)


def render(template, values):
    text = (TEMPLATES / template).read_text()
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    unresolved = sorted(set(re.findall(r"\{\{[^}]+\}\}", text)))
    if unresolved:
        raise ValueError(f"Unresolved values in {template}: {unresolved}")
    return text


async def upsert_page(client, title, body):
    url = slugify(title)
    data = {
        "wiki_page[title]": title,
        "wiki_page[body]": body,
        "wiki_page[published]": "false",
        "wiki_page[editing_roles]": "teachers",
    }
    response = await client.get(f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{url}")
    if response.status_code == 200:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/pages/{url}", data=data)
    if response.status_code != 404:
        response.raise_for_status()
    return await api(client, "POST", f"/courses/{COURSE_ID}/pages", data=data)


async def upsert_practice_assignment(
    client, title, description, submission_types, annotatable_attachment_id=None
):
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == title]
    if len(matches) > 1:
        raise RuntimeError(
            f"Duplicate assignments named {title!r}: {[entry['id'] for entry in matches]}"
        )
    found = matches[0] if matches else None
    data = {
        "assignment[name]": title,
        "assignment[description]": description,
        "assignment[submission_types][]": submission_types,
        "assignment[grading_type]": "not_graded",
        "assignment[points_possible]": "0",
        "assignment[omit_from_final_grade]": "true",
        "assignment[published]": "false",
    }
    if annotatable_attachment_id:
        data["assignment[annotatable_attachment_id]"] = str(annotatable_attachment_id)
    assignment = await api(
        client,
        "PUT" if found else "POST",
        (
            f"/courses/{COURSE_ID}/assignments/{found['id']}"
            if found
            else f"/courses/{COURSE_ID}/assignments"
        ),
        data=data,
    )
    if (
        assignment.get("published")
        or float(assignment.get("points_possible") or 0) != 0
        or assignment.get("grading_type") != "not_graded"
        or not assignment.get("omit_from_final_grade")
        or (
            annotatable_attachment_id
            and assignment.get("annotatable_attachment_id")
            != annotatable_attachment_id
        )
    ):
        raise RuntimeError(
            f"Formative assignment invariant failed for {title!r}: "
            f"published={assignment.get('published')}, points={assignment.get('points_possible')}, "
            f"grading={assignment.get('grading_type')}, omit={assignment.get('omit_from_final_grade')}, "
            f"attachment={assignment.get('annotatable_attachment_id')}"
        )
    return assignment


async def require_minor_preflight(client):
    groups = await paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group_matches = [entry for entry in groups if entry.get("name") == MINOR_GROUP_NAME]
    if len(group_matches) != 1:
        raise RuntimeError(
            f"Expected exactly one assignment group named {MINOR_GROUP_NAME!r}; "
            f"found {len(group_matches)}"
        )
    group = group_matches[0]
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [
        entry for entry in assignments if entry.get("name") == RECOMMENDATION_TITLE
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one existing mapped Minor assignment named {RECOMMENDATION_TITLE!r}; found {len(matches)}"
        )
    found = matches[0]
    if (
        found.get("published")
        or float(found.get("points_possible") or 0) != 100
        or found.get("assignment_group_id") != group["id"]
        or found.get("grading_type") != "points"
        or found.get("omit_from_final_grade")
    ):
        raise RuntimeError(
            f"Mapped Minor invariant failed before module writes: "
            f"published={found.get('published')}, points={found.get('points_possible')}, "
            f"group={found.get('assignment_group_id')}, grading={found.get('grading_type')}, "
            f"omit={found.get('omit_from_final_grade')}"
        )
    return found, group


async def update_minor_assignment(client, assignment):
    description = (
        "<p>Submit the private five-to-seven-sentence Hospitality Career and Business "
        "Recommendation. Use one career task, one correctly labeled number, one "
        "preparation or schedule trade-off, one entrepreneurial opportunity, and one "
        "supported local connection when relevant. Paper, typed text, uploaded file, "
        "or media response are equal routes.</p>"
    )
    existing = assignment.get("description") or ""
    note = re.search(
        r'<div data-cce-rubric-note="cce-advisory-rubric-v1".*?</div>',
        existing,
        flags=re.DOTALL,
    )
    if note and "cce-advisory-rubric-v1" not in description:
        description = description.rstrip() + note.group(0)
    updated = await api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{assignment['id']}",
        data={
            "assignment[name]": RECOMMENDATION_TITLE,
            "assignment[description]": description,
            "assignment[submission_types][]": [
                "online_upload",
                "online_text_entry",
                "media_recording",
            ],
            "assignment[grading_type]": "points",
            "assignment[points_possible]": "100",
            "assignment[omit_from_final_grade]": "false",
            "assignment[published]": "false",
        },
    )
    if (
        updated.get("published")
        or float(updated.get("points_possible") or 0) != 100
        or updated.get("grading_type") != "points"
        or updated.get("omit_from_final_grade")
        or updated.get("assignment_group_id") != assignment.get("assignment_group_id")
    ):
        raise RuntimeError(
            f"Mapped Minor invariant failed after update for {RECOMMENDATION_TITLE!r}"
        )
    return updated


QUESTIONS = [
    (
        "Q1 - Intrinsic motivation",
        "Which example is primarily intrinsic motivation?",
        "A baker keeps practicing because improving the technique feels satisfying.",
        [
            "A baker receives a cash prize.",
            "A baker avoids losing a shift.",
            "A baker earns a gift card.",
        ],
        "Correct. The motivation comes from satisfaction in the work itself.",
        "Intrinsic motivation comes from interest, purpose, or satisfaction in the task.",
    ),
    (
        "Q2 - Extrinsic motivation",
        "Which example is primarily extrinsic motivation?",
        "A hotel team earns a bonus for meeting a service goal.",
        [
            "A planner enjoys solving a complex seating problem.",
            "A chef feels proud after mastering a technique.",
            "A manager likes helping a new employee improve.",
        ],
        "Correct. The bonus is an outside reward.",
        "Extrinsic motivation comes from an outside reward or consequence.",
    ),
    (
        "Q3 - Motivation differences",
        "Why might the same reward affect two workers differently?",
        "People value different rewards and may respond differently to the same incentive.",
        [
            "One worker must be dishonest.",
            "Intrinsic motivation always works better.",
            "Every employee responds to money in the same way.",
        ],
        "Correct. Motivation is personal and context matters.",
        "Do not assume one motivator works the same way for everyone.",
    ),
    (
        "Q4 - Data label",
        "The evidence guide lists $68,130 for Lodging Managers. What does that number mean?",
        "May 2024 U.S. median annual pay.",
        [
            "Guaranteed DFW starting pay.",
            "The minimum salary for every hotel manager.",
            "The amount every manager earns after one year.",
        ],
        "Correct. Keep the year, geography, and measure attached.",
        "The figure is a national median, not local starting pay or a guarantee.",
    ),
]


async def prepare_quiz_questions(client, quiz_id, desired_names):
    existing = await paged(
        client, f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions"
    )
    keep, seen = [], set()
    for question in existing:
        name = question.get("question_name")
        if name not in desired_names or name in seen:
            await api(
                client,
                "DELETE",
                f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions/{question['id']}",
            )
        else:
            seen.add(name)
            keep.append(question)
    return keep


async def finalize_quiz_order(client, quiz_id, expected_names):
    final = await paged(
        client, f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions"
    )
    by_name = {entry.get("question_name"): entry for entry in final}
    if set(by_name) != set(expected_names) or len(final) != len(expected_names):
        raise RuntimeError(
            f"Quiz {quiz_id} question mismatch: {[entry.get('question_name') for entry in final]}"
        )
    fields = []
    for name in expected_names:
        fields.extend(
            [
                ("order[][id]", str(by_name[name]["id"])),
                ("order[][type]", "question"),
            ]
        )
    await api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/quizzes/{quiz_id}/reorder",
        content=urlencode(fields),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    ordered = await paged(
        client, f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions"
    )
    actual = [entry.get("question_name") for entry in ordered]
    if actual != expected_names:
        raise RuntimeError(
            f"Quiz {quiz_id} order mismatch: expected {expected_names}, found {actual}"
        )


async def upsert_quiz(client):
    quizzes = await paged(client, f"/courses/{COURSE_ID}/quizzes")
    matches = [entry for entry in quizzes if entry.get("title") == QUIZ_TITLE]
    if len(matches) > 1:
        raise RuntimeError(
            f"Duplicate quizzes named {QUIZ_TITLE!r}: {[entry['id'] for entry in matches]}"
        )
    quiz = matches[0] if matches else None
    data = {
        "quiz[title]": QUIZ_TITLE,
        "quiz[description]": "<p>Ungraded optional practice. Retry and use the feedback. The written comparison remains the lesson evidence.</p>",
        "quiz[quiz_type]": "practice_quiz",
        "quiz[published]": "false",
        "quiz[allowed_attempts]": "-1",
        "quiz[show_correct_answers]": "true",
        "quiz[shuffle_answers]": "false",
    }
    quiz = await api(
        client,
        "PUT" if quiz else "POST",
        (
            f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
            if quiz
            else f"/courses/{COURSE_ID}/quizzes"
        ),
        data=data,
    )
    expected = [spec[0] for spec in QUESTIONS]
    existing = await prepare_quiz_questions(client, quiz["id"], set(expected))
    for position, (
        name,
        text,
        correct,
        wrong,
        correct_comment,
        incorrect_comment,
    ) in enumerate(QUESTIONS, 1):
        found = next(
            (
                question
                for question in existing
                if question.get("question_name") == name
            ),
            None,
        )
        payload = {
            "question": {
                "question_name": name,
                "question_text": text,
                "question_type": "multiple_choice_question",
                "position": position,
                "points_possible": 1,
                "correct_comments": correct_comment,
                "incorrect_comments": incorrect_comment,
                "answers": [{"answer_text": correct, "answer_weight": 100}]
                + [{"answer_text": answer, "answer_weight": 0} for answer in wrong],
            }
        }
        await api(
            client,
            "PUT" if found else "POST",
            (
                f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{found['id']}"
                if found
                else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
            ),
            json=payload,
        )
    await finalize_quiz_order(client, quiz["id"], expected)
    final = await api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
    if (
        final.get("published")
        or final.get("quiz_type") != "practice_quiz"
        or int(final.get("allowed_attempts") or 0) != -1
    ):
        raise RuntimeError(
            f"Practice quiz invariant failed: published={final.get('published')}, "
            f"type={final.get('quiz_type')}, attempts={final.get('allowed_attempts')}"
        )
    return final


async def upsert_item(client, module_id, kind, key, title):
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    found = next(
        (
            item
            for item in items
            if item.get("type") == kind
            and (
                (kind == "SubHeader" and item.get("title") == title)
                or (kind == "Page" and item.get("page_url") == key)
                or (
                    kind in ("Assignment", "Quiz")
                    and item.get("content_id") == key
                )
            )
        ),
        None,
    )
    if found:
        return await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{found['id']}",
            data={"module_item[title]": title},
        )
    data = {"module_item[type]": kind, "module_item[title]": title}
    if kind == "Page":
        data["module_item[page_url]"] = key
    elif kind in ("Assignment", "Quiz"):
        data["module_item[content_id]"] = key
    return await api(
        client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data=data
    )


def file_link(file_id, label):
    return f'<a href="/courses/{COURSE_ID}/files/{file_id}/preview" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">{label}</a>'


def image_tag(file_id, alt, max_width=700):
    return f'<img src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" loading="lazy" style="display:block;width:100%;max-width:{max_width}px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'


def step(number, title, body):
    return f'<h3 style="color:#5a2d91;border-bottom:3px solid #d9c9ed">{number}. {title}</h3>{body}'


def flow(color, title, text):
    return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'


async def main():
    preflight()
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as client:
        recommendation, minor_group = await require_minor_preflight(client)
        module = await ensure_module(client)
        support = "course files/CCR Materials/3SW/Wk4"
        support_folder = await ensure_folder(client, support)
        names = {
            "CAREERS": "3sw-wk4-hospitality-career-evidence-guide.pdf",
            "MENU": "3sw-wk4-culinary-twist-menu-brief.pdf",
            "MOTIVATION": "3sw-wk4-motivation-career-comparison.pdf",
            "CARDS": "3sw-wk4-hotel-rescue-cards.pdf",
            "RESPONSE": "3sw-wk4-hotel-rescue-response.pdf",
            "EVENT": "3sw-wk4-cater-create-event-brief.pdf",
            "RECOMMENDATION": "3sw-wk4-hospitality-recommendation.pdf",
            "RUBRIC": "3sw-wk4-hospitality-minor-rubric.pdf",
        }
        files = {
            key: await upload(
                client, ROOT / "docs/resources/worksheets" / name, support
            )
            for key, name in names.items()
        }
        annotation = await upsert_practice_assignment(
            client,
            ANNOTATION_TITLE,
            "<p><strong>Workbook route:</strong> complete FYF pp. 112-113, then use text entry for the reader revision and transferable-skill check. <strong>No-workbook route:</strong> annotate the Culinary Twist brief or upload the same evidence. Students do not complete both the workbook and the full brief. Paper, Canva, and Adobe Express are equal routes.</p><p>Text-entry prompts: What did you revise so a customer can understand the item? Which skill transfers to another career, and how?</p>",
            ["student_annotation", "online_upload", "online_text_entry"],
            files["MENU"]["id"],
        )
        recommendation = await update_minor_assignment(client, recommendation)
        quiz = await upsert_quiz(client)

        selected_visuals = {
            1: [
                "fyf-hospitality-opener-optimized.jpg",
                "fyf-culinary-twist-plan.png",
                "fyf-culinary-twist-menu.png",
            ],
            2: ["fyf-motivation-types.png", "fyf-motivation-plan.png"],
            3: ["fyf-hotel-rescue-roles.png", "fyf-hotel-rescue-solutions.png"],
            4: ["fyf-cater-create-menu.png", "fyf-cater-create-experience.png"],
            5: ["fyf-irving-hospitality-context.png"],
        }
        folders, visuals = {}, {}
        for day, names_for_day in selected_visuals.items():
            folder_path = f"course files/CCR Materials/3SW/Wk4/Day {day} Visuals"
            folders[day], visuals[day] = await ensure_folder(client, folder_path), {}
            for name in names_for_day:
                visuals[day][name] = await upload(
                    client, ASSETS / f"day{day}" / name, folder_path
                )

        support_folder, support_file_count = await lock_folder_files(
            client, support_folder
        )
        folder_file_counts = {}
        for day, folder in folders.items():
            folders[day], folder_file_counts[day] = await lock_folder_files(
                client, folder
            )

        annotation_url = f"/courses/{COURSE_ID}/assignments/{annotation['id']}"
        quiz_url = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        recommendation_url = f"/courses/{COURSE_ID}/assignments/{recommendation['id']}"

        contracts = {
            1: {
                "TOPIC": "Hospitality Careers",
                "OBJECTIVE": "Students will explore and describe the CTE career clusters and identify career opportunities within one or more career clusters using evidence from Career Clusters.",
                "TEKS": "d(1)(B), d(1)(C)",
                "DOL": "Completed FYF pp. 112-113 Culinary Twist plan and menu plus a reader revision and transferable-skill check in the Canvas practice text entry or teacher-provided index card.",
                "STUDENT_OBJECTIVE": "describe hospitality work and build a clear menu item within a customer constraint.",
                "STUDENT_DOL": "complete FYF pp. 112-113, revise one unclear part, and connect one skill to another career.",
                "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> dish = plato · ingredient = ingrediente · constraint = condición o límite · customer = cliente.</p><p><strong>Use this frame:</strong> The special ingredient changes ____ by ____. I revised ____ so the customer can ____.</p>",
            },
            2: {
                "TOPIC": "Career Comparison",
                "OBJECTIVE": "Students will identify skills that transfer among a variety of careers and use resources to compare the salaries of at least three careers in an interest area using evidence from Transferable Skills.",
                "TEKS": "d(4)(B), d(5)(E)",
                "DOL": "FYF p. 122 Motivation Plan plus a marked three-career evidence table, two comparison responses, and one evidence-based fit decision.",
                "STUDENT_OBJECTIVE": "compare motivation, preparation, pay, and work conditions across three hospitality careers.",
                "STUDENT_DOL": "complete FYF p. 122 and recommend one career using a fact, a motivation idea, and a trade-off.",
                "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> intrinsic = satisfaction from the work · extrinsic = outside reward · median = middle pay · trade-off = a benefit paired with a cost or limit.</p><p><strong>Use this frame:</strong> I recommend ____ because ____. One trade-off is ____, which matters because ____.</p>",
            },
            3: {
                "TOPIC": "Hotel Operations",
                "OBJECTIVE": "Students will identify hospitality career opportunities, explain how coordinated hotel roles solve one fictional service crisis, and identify a small-business opportunity that uses the same process.",
                "TEKS": "d(1)(C), d(3)(I)",
                "DOL": "FYF p. 118 coordinated response plus an individual role record and small-business transfer naming what the owner sells or coordinates.",
                "STUDENT_OBJECTIVE": "use one hotel role to help solve a service problem and transfer the response process to a small business.",
                "STUDENT_DOL": "complete my role evidence, help build the FYF p. 118 team solution, and explain how the process helps another hospitality business.",
                "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> verify = check what is true · protect = keep a requirement from being ignored · coordinate = connect different actions · follow through = confirm the plan happened.</p><p><strong>Use this frame:</strong> My role should first ____ because ____. This process would help a ____ business by ____.</p>",
            },
            4: {
                "TOPIC": "Catering Entrepreneurship",
                "OBJECTIVE": "Students will identify catering career opportunities and explain entrepreneurship by designing a connected client service with one practical limit and one owner responsibility.",
                "TEKS": "d(1)(C), d(3)(I)",
                "DOL": "FYF pp. 119-120 Cater and Create design plus the one-page client, entrepreneurship, and revision companion.",
                "STUDENT_OBJECTIVE": "design a connected event service and explain what the catering owner sells, coordinates, and must manage.",
                "STUDENT_DOL": "complete FYF pp. 119-120 and the one-page client, business, and revision companion.",
                "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> client = customer who hires the business · limit = condition the plan must work within · service = work provided for a client · revise = improve after feedback.</p><p><strong>Use this frame:</strong> A client might pay for this experience because ____. The owner must also ____.</p>",
            },
            5: {
                "TOPIC": "Career Recommendation",
                "OBJECTIVE": "Students will compare salary and preparation evidence for three hospitality careers and recommend one career with a related entrepreneurial opportunity and supported local connection.",
                "TEKS": "d(1)(C), d(3)(I), d(5)(E)",
                "DOL": "Five-to-seven-sentence Hospitality Career and Business Recommendation scored with the 16-point rubric in mapped Minor 2.",
                "STUDENT_OBJECTIVE": "recommend one hospitality career using accurate career evidence, a trade-off, and a related business opportunity.",
                "STUDENT_DOL": "submit a five-to-seven-sentence recommendation and self-check it with the 16-point rubric.",
                "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> recommendation = recomendación · evidence = evidencia · preparation = preparación · trade-off = benefit plus cost or limit · business = negocio.</p><p><strong>Use this frame:</strong> I recommend ____ because ____. The evidence shows ____. One trade-off is ____. A related business could ____.</p>",
            },
        }

        student = {
            1: {
                "TITLE": "Culinary Twist Menu Design",
                "PURPOSE": "Create a menu item that responds to an ingredient constraint and communicates clearly to a customer.",
                "TODAY": "<ul><li>explore hospitality work;</li><li>plan a fictional dish;</li><li>design, test, and revise a menu item.</li></ul>",
                "READY": f'<p><strong>Default route:</strong> open your workbook to FYF pp. 112-113. After the menu, use <a href="{annotation_url}">the practice text entry</a> for the two short evidence checks. Use {file_link(files["MENU"]["id"], "the optional no-workbook brief")} or its Canvas annotation route only if you cannot write in the workbook. Do not complete both the workbook and the full brief.</p><p><strong>Safety boundary:</strong> this is a design task. Do not prepare or taste food.</p>',
                "MEDIA": image_tag(
                    visuals[1]["fyf-hospitality-opener-optimized.jpg"]["id"],
                    "Find Your Future hospitality and tourism cluster opener",
                )
                + image_tag(
                    visuals[1]["fyf-culinary-twist-plan.png"]["id"],
                    "Find Your Future Culinary Twist ingredient and preparation planning directions",
                )
                + image_tag(
                    visuals[1]["fyf-culinary-twist-menu.png"]["id"],
                    "Find Your Future Culinary Twist menu design directions",
                ),
                "STEPS": step(
                    1,
                    "Choose the guest need",
                    "<p>Name the event or customer and one need such as access, comfort, cost, safety, or enjoyment.</p>",
                )
                + step(
                    2,
                    "Plan within constraints",
                    "<p>Choose four or five base ingredients. Add the assigned special ingredient. Use this frame beside your response: <strong>The special ingredient changes the ____ by ____.</strong></p>",
                )
                + step(
                    3,
                    "Create the menu item",
                    "<p>Add a dish name, price, two- or three-sentence description, and at least three sketch labels.</p>",
                )
                + step(
                    4,
                    "Run the reader test",
                    f'<p>Can a customer identify the dish, main ingredients, special ingredient, and price? Revise one unclear part. Then use <a href="{annotation_url}">the practice text entry</a> or your teacher\'s index card to record what changed and complete: <strong>____ transfers to ____ because both jobs require ____.</strong></p>',
                ),
                "EXIT": "<p>Which skill transfers best to another career: working with constraints, describing a product, pricing, or visual communication? Give one example.</p>",
                "DONE": "<ul><li>all four menu elements;</li><li>three sketch labels;</li><li>one reader revision;</li><li>one transferable-skill connection.</li></ul>",
                "SUPPORT": "<p>dish = plato · ingredient = ingrediente · menu = menú · price = precio · customer = cliente. A labeled plate outline is included. Rehearse the description aloud before writing.</p>",
                "FALLBACK": "<p>The embedded FYF pages show the activity. If you do not have the workbook, use the optional brief or Canvas annotation. Save one route only.</p>",
            },
            2: {
                "TITLE": "Motivation and Three-Career Comparison",
                "PURPOSE": "Use motivation ideas and one fixed evidence set to compare three hospitality careers.",
                "TODAY": "<ul><li>distinguish intrinsic and extrinsic motivation;</li><li>design a short competition plan;</li><li>compare three careers using the same measures.</li></ul>",
                "READY": f'<p>Open your workbook to FYF p. 122. Also open {file_link(files["MOTIVATION"]["id"], "the two-page Hospitality Career Comparison")} and {file_link(files["CAREERS"]["id"], "the Hospitality Career Evidence Guide")}.</p>',
                "MEDIA": image_tag(
                    visuals[2]["fyf-motivation-types.png"]["id"],
                    "Find Your Future intrinsic and extrinsic motivation examples",
                )
                + image_tag(
                    visuals[2]["fyf-motivation-plan.png"]["id"],
                    "Find Your Future professional baking competition planning page",
                ),
                "STEPS": step(
                    1,
                    "Build the motivation plan in the workbook",
                    "<p>On FYF p. 122, give the competition one goal, two rules, an outside reward, and an intrinsic motivator. Explain why two bakers might respond differently.</p>",
                )
                + step(
                    2,
                    "Optional practice check",
                    f'<p>If your teacher directs you or you finish early, <a href="{quiz_url}">open the Motivation Check</a>. Retry and use the feedback. The written comparison is today\'s evidence.</p>',
                )
                + step(
                    3,
                    "Read the fixed career evidence",
                    "<p>The stable table is already printed on the companion. Circle the highest median, box the most annual openings, and star the bachelor's-typical route. Keep year, geography, and measure attached to each number.</p>",
                )
                + step(
                    4,
                    "Compare and recommend",
                    "<p>Use one career fact, one motivation idea, and one trade-off. Use the complete frames beside each response; name both the benefit and the cost or limit.</p>",
                ),
                "EXIT": "<p>Underline the year, geography, and measure attached to one number. Circle one motivation idea that transfers to more than one career.</p>",
                "DONE": "<ul><li>FYF p. 122 motivation plan complete;</li><li>all three careers marked and compared;</li><li>two motivation-transfer responses;</li><li>fit decision uses evidence and a trade-off.</li></ul>",
                "SUPPORT": "<p>motivation = motivación · median = mediana · preparation = preparación · reward = recompensa · trade-off = beneficio y costo o límite. Read one career row at a time.</p>",
                "FALLBACK": "<p>The two PDFs contain every required fact. Xello local data and H&amp;L browsing are optional additions, not replacements.</p>",
            },
            3: {
                "TITLE": "Hotel Rescue Team Response",
                "PURPOSE": "Use one hotel role to help solve a service crisis without making an unsafe or unverified promise.",
                "TODAY": "<ul><li>prepare one role response;</li><li>coordinate three or more roles;</li><li>transfer the process to a small business.</li></ul>",
                "READY": f'<p>Open your workbook to FYF pp. 117-118 and {file_link(files["RESPONSE"]["id"], "the two-page individual response")}. Your teacher will project or share one team copy of {file_link(files["CARDS"]["id"], "the role and crisis cards")}.</p>',
                "MEDIA": image_tag(
                    visuals[3]["fyf-hotel-rescue-roles.png"]["id"],
                    "Find Your Future Hotel Rescue roles and crisis choices",
                )
                + image_tag(
                    visuals[3]["fyf-hotel-rescue-solutions.png"]["id"],
                    "Find Your Future Hotel Rescue solution planning page",
                ),
                "STEPS": step(
                    1,
                    "Prepare your role",
                    "<p>Complete page 1 of the individual response before the group discussion.</p>",
                )
                + step(
                    2,
                    "Verify and protect",
                    "<p>Separate confirmed facts from unanswered questions. Protect the safety, accessibility, reservation, or client requirement.</p>",
                )
                + step(
                    3,
                    "Build the team solution in the workbook",
                    "<p>Use FYF p. 118. Give at least three roles different actions, write a factual message, and name who follows through.</p>",
                )
                + step(
                    4,
                    "Transfer the process",
                    "<p>Complete page 2 after reading another ready solution or the teacher model. Use the frame beside the response to name what the small-business owner coordinates.</p>",
                ),
                "EXIT": "<p>How would the same response process help a caterer, restaurant, lodging business, or event planner? Name what the owner sells or coordinates.</p>",
                "DONE": "<ul><li>individual role evidence;</li><li>FYF p. 118 team solution;</li><li>three coordinated roles;</li><li>factual message and follow-through;</li><li>individual business transfer.</li></ul>",
                "SUPPORT": "<p>verify = verificar · guest = huésped · accessible = accesible · promise = promesa · follow through = dar seguimiento. Written role evidence is equal to acting.</p>",
                "FALLBACK": "<p>Select one role and crisis. Use the embedded FYF p. 118 page and the teacher model to complete the same individual response independently.</p>",
            },
            4: {
                "TITLE": "Cater and Create Client Experience",
                "PURPOSE": "Design a connected event experience that fits one client, feeling, and practical limit.",
                "TODAY": "<ul><li>define the client and business goal;</li><li>connect menu, space, and service choices;</li><li>test and revise the plan.</li></ul>",
                "READY": f'<p>Open your workbook to FYF pp. 119-120 and {file_link(files["EVENT"]["id"], "the one-page Cater and Create companion")}.</p><p>Use a fictional client. Do not include a real name, address, contact information, payment detail, or public post.</p>',
                "MEDIA": image_tag(
                    visuals[4]["fyf-cater-create-menu.png"]["id"],
                    "Find Your Future Cater and Create menu directions",
                )
                + image_tag(
                    visuals[4]["fyf-cater-create-experience.png"]["id"],
                    "Find Your Future Cater and Create event experience directions",
                ),
                "STEPS": step(
                    1,
                    "Set the client and business goal",
                    "<p>Use the companion to choose an event, feeling, audience, and one practical limit.</p>",
                )
                + step(
                    2,
                    "Design in the workbook",
                    "<p>Use FYF pp. 119-120 for the menu, table or space, entertainment, take-home touch, and accessibility choice.</p>",
                )
                + step(
                    3,
                    "Name the business responsibility",
                    "<p>On the companion, explain what the owner sells or coordinates and one responsibility beyond cooking.</p>",
                )
                + step(
                    4,
                    "Run the client test",
                    "<p>A partner, teacher, or self-check names one strength and one workable change. Revise the workbook design and record the change. Use the complete client-value frame beside the final response.</p>",
                ),
                "EXIT": "<p>Why might a client pay for the complete experience? Name one design detail and one business limit.</p>",
                "DONE": "<ul><li>FYF pp. 119-120 design;</li><li>client, feeling, and practical limit;</li><li>owner responsibility;</li><li>one visible revision;</li><li>client-value explanation.</li></ul>",
                "SUPPORT": "<p>client = cliente · catering = servicio de banquetes · guest = invitado · limit = límite · revise = revisar. A labeled sketch is equal to a polished layout.</p>",
                "FALLBACK": "<p>The embedded workbook pages plus the one-page companion are the complete independent route. Paper, Canva, Adobe Express, and another approved tool are equal.</p>",
            },
            5: {
                "TITLE": "Hospitality Career and Business Recommendation",
                "PURPOSE": "Use the week's evidence to recommend one career and explain a related business opportunity.",
                "TODAY": "<ul><li>audit the three-career evidence;</li><li>plan from Jordan's scenario;</li><li>write and self-score an individual recommendation.</li></ul>",
                "READY": f'<p>Open {file_link(files["RECOMMENDATION"]["id"], "the Hospitality Recommendation")}, {file_link(files["RUBRIC"]["id"], "the 16-point rubric")}, and {file_link(files["CAREERS"]["id"], "the fixed evidence guide")}.</p>',
                "MEDIA": image_tag(
                    visuals[5]["fyf-irving-hospitality-context.png"]["id"],
                    "Find Your Future Irving hospitality and culinary program context",
                    650,
                ),
                "STEPS": step(
                    1,
                    "Audit the evidence",
                    "<p>Check the median, preparation, growth, openings, and work condition for all three careers. Correct any measure drift.</p>",
                )
                + step(
                    2,
                    "Read Jordan's scenario",
                    "<p>Mark the interests and constraints. Compare all three careers before selecting one.</p>",
                )
                + step(
                    3,
                    "Write five to seven sentences",
                    "<p>Use one career task, one correctly labeled number, one trade-off, one business opportunity, and one verified local connection when relevant. The sentence jobs sit directly above the ten writing lines.</p>",
                )
                + step(
                    4,
                    "Self-score and submit",
                    f'<p>Revise one weak criterion, then <a href="{recommendation_url}">open the private recommendation assignment</a> or submit the paper copy.</p>',
                ),
                "EXIT": "<p>Which evidence changed the recommendation most: the task, preparation route, or schedule? Why do the other two still matter?</p>",
                "DONE": "<ul><li>all three careers considered;</li><li>five to seven sentences;</li><li>number retains source meaning;</li><li>trade-off and business opportunity;</li><li>rubric self-check.</li></ul>",
                "SUPPORT": "<p>recommendation = recomendación · evidence = evidencia · preparation = preparación · schedule = horario · business = negocio. Numbered sentence jobs and ten full-width writing lines are provided.</p>",
                "FALLBACK": "<p>The fixed guide, prompt, and rubric are the complete route. Xello Decision Making, eDynamic 6.1, and H&amp;L App Exploration are optional extensions only.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Culinary Twist Menu Design",
                "SUBTITLE": "50 minutes · TEKS d(1)(B), d(1)(C)",
                "ALERT": "<strong>Workbook first.</strong> Students complete FYF pp. 112-113, then place the two short evidence checks in the practice text entry or on one index card. The three-page brief is an optional no-workbook route, not extra work.",
                "PREP": f'<ul><li><strong>Per student:</strong> one FYF workbook opened to pp. 111-113, one pencil, and optional colored pencils or markers.</li><li><strong>Paper-only evidence:</strong> one index card for the reader revision and transferable-skill check. Canvas text entry is the default response home.</li><li><strong>Teacher:</strong> one display device and six visible workbook special-ingredient choices: pomegranate seeds, marshmallow fluff, sprinkles, coffee beans, gummy bears, or syrup.</li><li><strong>Optional route:</strong> post {file_link(files["MENU"]["id"], "the no-workbook brief")} and annotation activity; do not print a class set.</li><li><strong>Grouping:</strong> independent design; a two-minute reader check may use a partner, teacher, or self-check.</li></ul>',
                "EVIDENCE": "<p>FYF pp. 112-113 with four menu elements and three sketch labels, plus one reader revision and one transferable-skill connection. Formative.</p>",
                "FLOW": flow(
                    "#5a2d91",
                    "Warm-up · 5",
                    "What makes a food experience feel special?",
                )
                + flow(
                    "#4a9d2f",
                    "Open the cluster · 8",
                    "Identify food and guest-experience work.",
                )
                + flow(
                    "#1f617a",
                    "Plan · 12",
                    "Ingredients, constraint, preparation, customer result.",
                )
                + flow(
                    "#e3ad19",
                    "Build and test · 20",
                    "Create the menu item and revise for a reader.",
                )
                + flow("#1f617a", "Submit and reset · 5", "Record the revision and transfer check; return materials."),
                "MONITOR": "<p><strong>Model:</strong> pomegranate seeds → crush some into a dressing and keep some whole → add tart flavor, red color, and crunch to a festival taco salad. This models communication, not a recipe or safety guarantee. <strong>Lap 1:</strong> by minute 12, students have the special ingredient, what it changes, and two preparation steps. <strong>Lap 2:</strong> by minute 25, all four menu elements are in progress. If more than 25% are missing one, pause for a 60-second four-label model. Do not score art polish, public speaking, or tool choice. <strong>Trim:</strong> skip the 30-second share; preserve the reader revision, transfer check, and five-minute collection/reset.</p>",
                "RESOURCES": "<p>Licensed FYF pp. 111-113 are embedded. FYF Restaurant Rebrand is an optional extension.</p>",
                "SUPPORT": "<p>Offer two special-ingredient choices and keep the evidence chain visible. Put the complete ingredient-change and transfer frames beside the matching response. The workbook supplies the full plan and design space; the optional brief supplies the same space only when a student lacks the workbook.</p>",
                "FALLBACK": "<p>No food preparation or tasting. If annotation fails, use paper or an approved digital file. Collect the same evidence from every route.</p>",
            },
            2: {
                "TITLE": "Motivation and Three-Career Comparison",
                "SUBTITLE": "50 minutes · TEKS d(4)(B), d(5)(E)",
                "ALERT": "<strong>Use one fixed evidence set.</strong> The optional Quiz checks misconceptions for early finishers or the next class opening; the written comparison is the evidence.",
                "PREP": f'<ul><li><strong>Per student:</strong> one FYF workbook opened to p. 122, one {file_link(files["MOTIVATION"]["id"], "two-page comparison")} digitally or printed double-sided, and one pencil.</li><li><strong>Teacher:</strong> one display device with {file_link(files["CAREERS"]["id"], "the fixed evidence guide")} and completed table. Do not print the guide per student.</li><li><strong>Device:</strong> one per student only when assigning the optional unpublished practice Quiz.</li><li><strong>Grouping:</strong> independent writing; pairs may check evidence labels after each student finishes.</li></ul>',
                "EVIDENCE": "<p>FYF p. 122 motivation plan, three-career comparison, two-career motivation transfer, and an evidence-based fit decision with a visible trade-off. Formative evidence that feeds Day 5.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Internal and external reasons.")
                + flow(
                    "#4a9d2f",
                    "Motivation plan · 15",
                    "Goal, rules, reward, intrinsic reason.",
                )
                + flow(
                    "#1f617a",
                    "Career evidence · 10",
                    "Same measures for all three careers.",
                )
                + flow(
                    "#e3ad19",
                    "Compare and transfer · 15",
                    "Use one fact and one trade-off.",
                )
                + flow("#1f617a", "Exit and reset · 5", "Audit labels, store evidence, and return materials."),
                "MONITOR": "<p><strong>Model:</strong> “Improving the technique feels satisfying” is intrinsic; “the winner receives a paid bakery shadow day” is extrinsic. Do not rank one as morally better. <strong>Lap 1:</strong> by minute 30, students have all three evidence marks and both comparison prompts started. If more than 25% relabel a median as starting or DFW pay, rebuild one complete label: May 2024 U.S. median annual pay. <strong>Key:</strong> Lodging Manager has the highest median; Chef or Head Cook has the most projected annual openings; Event Planner has a bachelor's degree as typical entry education. <strong>Trim:</strong> the Quiz is optional for early finishers or the next class opening; preserve the written fit decision and five-minute evidence-label check.</p>",
                "RESOURCES": '<p><a href="https://www.bls.gov/ooh/food-preparation-and-serving/chefs-and-head-cooks.htm">BLS Chefs and Head Cooks</a> · <a href="https://www.bls.gov/ooh/management/lodging-managers.htm">BLS Lodging Managers</a> · <a href="https://www.bls.gov/ooh/business-and-financial/meeting-convention-and-event-planners.htm">BLS Event Planners</a></p>',
                "SUPPORT": "<p>Read one prefilled career row at a time, pre-highlight measure labels, and rehearse the recommendation orally. Complete intrinsic, extrinsic, and recommendation frames sit beside the matching response spaces. Students compare rather than copy stable data.</p>",
                "FALLBACK": "<p>The fixed PDFs carry the lesson. Xello localized data is optional only when geography, date, and measure remain visible. H&amp;L is optional.</p>",
            },
            3: {
                "TITLE": "Hotel Rescue Team Response",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(3)(I)",
                "ALERT": "<strong>One crisis per team.</strong> Every student completes individual role evidence before discussion and an individual transfer after it.",
                "PREP": f'<ul><li><strong>Per student:</strong> one FYF workbook opened to pp. 117-118, one {file_link(files["RESPONSE"]["id"], "two-page individual response")} digitally or printed double-sided, and one pencil.</li><li><strong>Per team:</strong> one projected or three-page {file_link(files["CARDS"]["id"], "role/crisis set")}; print `ceiling(roster ÷ 6)` sets, not one per student.</li><li><strong>Teacher:</strong> one display device with the completed Crisis C model in this guide.</li><li><strong>Grouping:</strong> teams of four to six. Six use one role each. Five combine Concierge with Guest Services. Four also combine Hotel Director with Front Desk.</li></ul>',
                "EVIDENCE": "<p>Individual role evidence, FYF p. 118 coordinated team response, and individual small-business transfer. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 4", "Verify before promising.")
                + flow("#4a9d2f", "Assign and prepare · 7", "Move to teams; assign one role and one crisis.")
                + flow(
                    "#1f617a",
                    "Team response · 19",
                    "Verify, protect, coordinate, communicate.",
                )
                + flow(
                    "#e3ad19",
                    "Read a response · 8",
                    "Use a ready peer response or the teacher model.",
                )
                + flow(
                    "#1f617a",
                    "Individual transfer · 7",
                    "Apply the process to a small business.",
                )
                + flow("#5a2d91", "Collect and reset · 5", "Store FYF and individual evidence; return card sets."),
                "MONITOR": "<p><strong>Teacher model, Crisis C:</strong> verify the request, meeting time, room status, and suitable rooms; protect accessibility; Guest Services checks room/timeline; Front Desk gives the verified update; Concierge offers only a verified immediate option; Hotel Director handles authorized service recovery. Message: “I can confirm your accessible room is still being prepared. I am checking the exact ready time now, and I will update you by ____. Meanwhile, the verified option available is ____.” Guest Services confirms the room and update happened. <strong>Lap 1:</strong> at minute 13, each student has two needed facts, one protected requirement, and one action. If more than 25% starts with a promise, sort one statement as confirmed, being checked, or not yet promised. <strong>Lap 2:</strong> at minute 30, teams have three different role actions and follow-through. <strong>Trim:</strong> replace peer exchange with the model; preserve individual evidence, FYF p. 118, transfer, and five-minute reset.</p>",
                "RESOURCES": "<p>Licensed FYF pp. 117-118 are embedded. The workbook carries the team solution; the two-page companion protects individual evidence before and after the group task.</p>",
                "SUPPORT": "<p>Use role starters, complete Verify before grouping, and allow written participation instead of acting. Keep the complete business-transfer frame beside the response. The independent route uses the same cards and completed teacher model.</p>",
                "FALLBACK": "<p>An absent student completes one role and crisis independently using the teacher model for the comparison step. No peer post or live platform is required.</p>",
            },
            4: {
                "TITLE": "Cater and Create Client Experience",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(3)(I)",
                "ALERT": "<strong>Design a service, not only a look.</strong> Client communication, staffing, cost, access, and risk are part of entrepreneurship.",
                "PREP": f'<ul><li><strong>Per student:</strong> one FYF workbook opened to pp. 119-120, one {file_link(files["EVENT"]["id"], "one-page companion")}, one pencil, and optional colored pencils or markers.</li><li><strong>Teacher:</strong> one display device with the licensed pages and completed client/limit model in this guide.</li><li><strong>Device:</strong> only for students using an approved digital design route.</li><li><strong>Grouping:</strong> independent design; a five-minute client test may use a partner, teacher, or self-check.</li></ul>',
                "EVIDENCE": "<p>FYF pp. 119-120 connected event design plus one-page evidence for client, practical limit, owner responsibility, and visible revision. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Experience beyond food.")
                + flow(
                    "#4a9d2f",
                    "Client and business goal · 8",
                    "Event, feeling, audience, limit.",
                )
                + flow(
                    "#1f617a",
                    "Design · 27",
                    "Menu, space, service, access, extra touches.",
                )
                + flow(
                    "#e3ad19", "Client test · 5", "One strength and workable change."
                )
                + flow("#1f617a", "Exit and reset · 5", "Record value and owner responsibility; return materials."),
                "MONITOR": "<p><strong>Model:</strong> fictional school recognition dinner; calm and welcoming feeling; students and families; 90-minute setup limit. Connect menu, table, quiet welcome activity, and take-home note; the owner coordinates food, setup, staffing, access, and client updates. <strong>Lap:</strong> at minute 18 of design, students can point to the client, feeling, limit, and two connected choices. If more than 25% has disconnected ideas, ask, “Which client need does this choice solve?” Do not collect real client data or require a public post. <strong>Trim:</strong> use teacher or self-check instead of a partner; preserve visible revision, exit response, and five-minute reset.</p>",
                "RESOURCES": "<p>Licensed FYF pp. 119-120 are embedded. Current local context may include FireBird Cafe Catering, but do not turn an opportunity into a guarantee.</p>",
                "SUPPORT": "<p>Preselect an event and feeling, keep the completed model visible, and accept labeled sketches. The complete client-value frame sits beside the response. The workbook supplies the large design areas; the companion asks only for missing evidence.</p>",
                "FALLBACK": "<p>Paper is equal. Use fictional clients only; no real account, name, address, contact information, or payment details.</p>",
            },
            5: {
                "TITLE": "Hospitality Career and Business Recommendation",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(3)(I), d(5)(E)",
                "ALERT": "<strong>Mapped Minor 2.</strong> The Canvas assignment remains unpublished but is already configured for 100 points in Minor Assessments (40%).",
                "PREP": f'<ul><li><strong>Per student:</strong> one {file_link(files["RECOMMENDATION"]["id"], "two-page recommendation")} digitally or printed double-sided, the {file_link(files["RUBRIC"]["id"], "student-visible rubric")}, one pencil, and one device for private Canvas submission when used.</li><li><strong>Teacher:</strong> one display device with {file_link(files["CAREERS"]["id"], "the fixed evidence guide")}, Jordan\'s scenario, the five-field evidence check, and the unpublished mapped Minor 2 Assignment.</li><li><strong>Grouping:</strong> individual assessment; use private conferences, not public sharing.</li><li>Review local program wording without promising admission, credentials, jobs, or salary.</li></ul>',
                "EVIDENCE": "<p>Individual five-to-seven-sentence recommendation using a task, correctly labeled number, trade-off, business opportunity, and verified local connection when relevant.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Rank decision factors.")
                + flow("#4a9d2f", "Audit evidence · 10", "Correct all five fields.")
                + flow("#1f617a", "Scenario plan · 10", "Compare all three careers.")
                + flow(
                    "#e3ad19",
                    "Recommendation · 20",
                    "Five to seven sentences with evidence.",
                )
                + flow(
                    "#1f617a", "Self-score and submit · 5", "Revise one weak criterion."
                ),
                "MONITOR": "<p><strong>Model only the evidence chain:</strong> Lodging Manager → coordinates guest service and hotel operations → $68,130 May 2024 U.S. median annual pay → evenings/weekends may be required → a small lodging or guest-service business sells and coordinates a verified service. Students still choose Jordan's fit. <strong>Lap:</strong> at minute 25, each plan has a task, labeled number, trade-off, and business opportunity. If more than 25% has a preference without evidence, model how one row becomes one sentence. Any career can earn full credit with accurate fit. Score four 0-4 criteria and convert `(raw ÷ 16) × 100`, rounded. Score content, not mechanics unless meaning is unclear. <strong>Trim:</strong> reduce the warm-up share or verbal debrief; preserve recommendation, rubric revision, private submission, and reset.</p>",
                "RESOURCES": '<p><a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte/singley-academy">Current Singley Academy programs</a> · current district pages for Lodging and Resort Management. Xello Decision Making, eDynamic 6.1, and H&amp;L App Exploration are optional extensions.</p>',
                "SUPPORT": "<p>Use five planning fields and keep the numbered sentence jobs beside the ten full-width writing lines. Speech-to-text, keyboard entry, and teacher scribing are equal routes.</p>",
                "FALLBACK": "<p>The fixed packet is the complete absence and platform-failure route. Do not add favorite counts or screenshots to the evidence requirement.</p>",
            },
        }

        day_names = {
            1: "Culinary Twist Menu Design",
            2: "Motivation and Career Comparison",
            3: "Hotel Rescue",
            4: "Cater and Create",
            5: "Hospitality Recommendation",
        }
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_item(
                client, module["id"], "SubHeader", None, header_title
            )
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 3SW Wk4 Day {day} - {day_names[day]}"
            student_page = await upsert_page(
                client,
                student_title,
                render(
                    "3sw-wk4-student.html",
                    {
                        "COURSE_ID": COURSE_ID,
                        "DAY": day,
                        **student[day],
                        **contracts[day],
                    },
                ),
            )
            teacher_title = f"TEACHER: 3SW Wk4 Day {day} Facilitator Guide"
            teacher_page = await upsert_page(
                client,
                teacher_title,
                render(
                    "3sw-wk4-teacher.html",
                    {
                        "COURSE_ID": COURSE_ID,
                        "DAY": day,
                        "STUDENT_PAGE_URL": student_page["url"],
                        **teacher[day],
                        **contracts[day],
                    },
                ),
            )
            await upsert_item(
                client, module["id"], "Page", teacher_page["url"], teacher_title
            )
            await upsert_item(
                client, module["id"], "Page", student_page["url"], student_title
            )
            pages[day] = {"teacher": teacher_page, "student": student_page}
            order += [
                ("Page", teacher_page["url"], teacher_title),
                ("Page", student_page["url"], student_title),
            ]
            if day == 1:
                await upsert_item(
                    client,
                    module["id"],
                    "Assignment",
                    annotation["id"],
                    ANNOTATION_TITLE,
                )
                order.append(("Assignment", annotation["id"], ANNOTATION_TITLE))
            if day == 2:
                await upsert_item(client, module["id"], "Quiz", quiz["id"], QUIZ_TITLE)
                order.append(("Quiz", quiz["id"], QUIZ_TITLE))
            if day == 5:
                await upsert_item(
                    client,
                    module["id"],
                    "Assignment",
                    recommendation["id"],
                    RECOMMENDATION_TITLE,
                )
                order.append(("Assignment", recommendation["id"], RECOMMENDATION_TITLE))

        items = await paged(
            client, f"/courses/{COURSE_ID}/modules/{module['id']}/items"
        )

        def matches_item(entry, kind, key):
            if entry.get("type") != kind:
                return False
            if kind == "SubHeader":
                return entry.get("id") == key
            if kind == "Page":
                return entry.get("page_url") == key
            return entry.get("content_id") == key

        keep_ids = set()
        for kind, key, _title in order:
            item = next(
                (
                    entry
                    for entry in items
                    if entry["id"] not in keep_ids
                    and matches_item(entry, kind, key)
                ),
                None,
            )
            if item is None:
                raise RuntimeError(f"Missing expected module item: {kind} {key}")
            keep_ids.add(item["id"])
        for entry in items:
            if entry["id"] not in keep_ids:
                await api(
                    client,
                    "DELETE",
                    f"/courses/{COURSE_ID}/modules/{module['id']}/items/{entry['id']}",
                )

        items = await paged(
            client, f"/courses/{COURSE_ID}/modules/{module['id']}/items"
        )
        for position, (kind, key, title) in enumerate(order, 1):
            matching = [entry for entry in items if matches_item(entry, kind, key)]
            if len(matching) != 1:
                raise RuntimeError(
                    f"Expected one module item for {kind} {key}; found {len(matching)}"
                )
            await api(
                client,
                "PUT",
                f"/courses/{COURSE_ID}/modules/{module['id']}/items/{matching[0]['id']}",
                data={"module_item[position]": position, "module_item[title]": title},
            )

        final_items = sorted(
            await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items"),
            key=lambda entry: entry.get("position") or 0,
        )
        module = await api(
            client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}"
        )
        annotation = await api(
            client,
            "GET",
            f"/courses/{COURSE_ID}/assignments/{annotation['id']}",
        )
        quiz = await api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
        recommendation = await api(
            client,
            "GET",
            f"/courses/{COURSE_ID}/assignments/{recommendation['id']}",
        )
        if module.get("published"):
            raise RuntimeError("3SW Wk4 module unexpectedly published")
        if (
            annotation.get("published")
            or float(annotation.get("points_possible") or 0) != 0
            or annotation.get("grading_type") != "not_graded"
            or not annotation.get("omit_from_final_grade")
            or annotation.get("annotatable_attachment_id") != files["MENU"]["id"]
        ):
            raise RuntimeError("3SW Wk4 formative annotation invariant failed")
        if (
            quiz.get("published")
            or quiz.get("quiz_type") != "practice_quiz"
            or int(quiz.get("allowed_attempts") or 0) != -1
        ):
            raise RuntimeError("3SW Wk4 practice quiz invariant failed")
        if (
            recommendation.get("published")
            or float(recommendation.get("points_possible") or 0) != 100
            or recommendation.get("grading_type") != "points"
            or recommendation.get("omit_from_final_grade")
            or recommendation.get("assignment_group_id") != minor_group["id"]
        ):
            raise RuntimeError("3SW Wk4 mapped Minor invariant failed after assembly")
        published_pages = [
            value["url"]
            for pair in pages.values()
            for value in pair.values()
            if value.get("published")
        ]
        if published_pages:
            raise RuntimeError(f"Published 3SW Wk4 pages remain: {published_pages}")
        if not support_folder.get("locked") or any(
            not folder.get("locked") for folder in folders.values()
        ):
            raise RuntimeError("One or more 3SW Wk4 Canvas folders remain unlocked")
        if len(final_items) != len(order):
            raise RuntimeError(
                f"Expected {len(order)} 3SW Wk4 module items; found {len(final_items)}"
            )
        published_items = [
            entry.get("title") for entry in final_items if entry.get("published")
        ]
        if published_items:
            raise RuntimeError(
                f"Published 3SW Wk4 module items remain: {published_items}"
            )
        for position, ((kind, key, title), item) in enumerate(
            zip(order, final_items), 1
        ):
            if (
                item.get("position") != position
                or item.get("title") != title
                or not matches_item(item, kind, key)
            ):
                raise RuntimeError(f"3SW Wk4 module order mismatch at {position}")
        print(
            json.dumps(
                {
                    "module": {"id": module["id"], "published": module["published"]},
                    "annotation": {
                        "id": annotation["id"],
                        "published": annotation.get("published"),
                        "submission_types": annotation.get("submission_types"),
                        "annotatable_attachment_id": annotation.get(
                            "annotatable_attachment_id"
                        ),
                    },
                    "quiz": {
                        "id": quiz["id"],
                        "published": quiz.get("published"),
                        "quiz_type": quiz.get("quiz_type"),
                        "allowed_attempts": quiz.get("allowed_attempts"),
                    },
                    "recommendation": {
                        "id": recommendation["id"],
                        "published": recommendation.get("published"),
                        "grading_type": recommendation.get("grading_type"),
                        "points_possible": recommendation.get("points_possible"),
                        "assignment_group_id": recommendation.get(
                            "assignment_group_id"
                        ),
                    },
                    "support_folder": {
                        "id": support_folder["id"],
                        "locked": support_folder["locked"],
                        "file_count": support_file_count,
                    },
                    "folders": {
                        str(day): {
                            "id": folder["id"],
                            "locked": folder["locked"],
                            "file_count": folder_file_counts[day],
                        }
                        for day, folder in folders.items()
                    },
                    "files": {key: value["id"] for key, value in files.items()},
                    "pages": {
                        str(day): {
                            kind: {"url": value["url"], "published": value["published"]}
                            for kind, value in pair.items()
                        }
                        for day, pair in pages.items()
                    },
                    "items": [
                        {
                            "id": item["id"],
                            "position": item["position"],
                            "title": item["title"],
                            "type": item["type"],
                            "page_url": item.get("page_url"),
                        }
                        for item in final_items
                    ],
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
