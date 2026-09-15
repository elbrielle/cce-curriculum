"""Build the unpublished 3SW Week 2 Plant Science Canvas module."""

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
STUDENT_GOOGLE_COPY_URLS = {
    1: "https://docs.google.com/document/d/1KSfuOFyLOJsNnbmnIWK1NqtjrvTDWcsuK9Cykq5ZyPc/copy",
    2: "https://docs.google.com/document/d/1Y8YKxE6i3_LdDeu8hshUK5kM4VljXdt9wLfQFsz04NE/copy",
    3: "https://docs.google.com/document/d/1-9KSSZMmAxndNAS0pOQdbeYlX4ejB59w713jaLdNyLU/copy",
    4: "https://docs.google.com/document/d/1rA6Y1d1pZbrYi6_iV6RzrYSvDe4IXI6FEcyZmwkbqlU/copy",
    5: "https://docs.google.com/document/d/1-gtRusemBl5CR1d1KHYOjXJL5WGI9d1jajqOnW-_jYE/copy",
}


# One Google Doc per worksheet (build/google_docs/student_worksheet_docs.json).
# Keyed by (day, anchor label) so a worksheet button never opens the day's exit ticket.
STUDENT_WORKSHEET_COPY_URLS = {
    (2, 'the two-page Farm-to-Table Planner'): "https://docs.google.com/document/d/1gi19YBcWDpeE85s2p3syOM262o_myc0dNxnA8m9g5QU/copy",
    (3, 'your planner'): "https://docs.google.com/document/d/1gi19YBcWDpeE85s2p3syOM262o_myc0dNxnA8m9g5QU/copy",
    (4, 'the two-page evaluation'): "https://docs.google.com/document/d/1bf8IHvRGjv_JwdMnAXD-05Y_7lRbmt6XErVXH6_KU0Q/copy",
    (5, 'the private reflection'): "https://docs.google.com/document/d/1p73y6vX0_h7IwnbPIK4llyizrdaH78PYs_izGAvp5oE/copy",
}


def student_copy_link(day, label):
    url = STUDENT_WORKSHEET_COPY_URLS.get((day, label), STUDENT_GOOGLE_COPY_URLS[day])
    return f'<a href="{url}">{label}</a>'


def student_copy_button(day, label):
    return (
        f'<p><a href="{STUDENT_GOOGLE_COPY_URLS[day]}" target="_blank" '
        'style="display:inline-block;background:#1f617a;color:#fff;padding:11px 18px;'
        'border-radius:6px;text-decoration:none"><strong>'
        f'{label}</strong></a></p>'
    )

MODULE_NAME = "3SW Wk2: Plant Science and Agricultural Communication"
QUIZ_TITLE = "PRACTICE: Emerging Plant-Tech Evidence Check"
PACKET_TITLE = "MAJOR 1: Farm-to-Table and Emerging Plant-Tech Evidence"
CAREER_TITLE = "PRACTICE: Plant Career Connection"
TRANSFER_TITLE = "FORMATIVE: Communication Skill Transfer"
REFLECTION_TITLE = "PRACTICE: Plant-Career Evidence Reflection"
LEGACY_REFLECTION_TITLE = "PRACTICE: " + "Xello " + "Biases Reflection"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/3sw/wk2"


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
    found = next((value for value in modules if value["name"] == MODULE_NAME), None)
    if found:
        return await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{found['id']}",
            data={
                "module[name]": MODULE_NAME,
                "module[published]": "false",
            },
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
    unlocked = []
    for entry in final:
        if not entry.get("locked"):
            refreshed = await api(client, "GET", f"/files/{entry['id']}")
            if not refreshed.get("locked"):
                unlocked.append(entry.get("display_name") or entry.get("filename"))
    if unlocked:
        raise RuntimeError(f"Unlocked files remain in folder {folder['id']}: {unlocked}")
    return current


def render(template_name, values):
    text = (TEMPLATES / template_name).read_text()
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    unresolved = sorted(set(re.findall(r"\{\{[^}]+\}\}", text)))
    if unresolved:
        raise ValueError(f"Unresolved values in {template_name}: {unresolved}")
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


async def upsert_module_item(client, module_id, kind, key, title):
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    found = next(
        (
            entry
            for entry in items
            if (kind == "Page" and entry.get("page_url") == key)
            or (kind in ("Quiz", "Assignment") and entry.get("content_id") == key)
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
    payload = {"module_item[type]": kind, "module_item[title]": title}
    payload[
        "module_item[page_url]" if kind == "Page" else "module_item[content_id]"
    ] = key
    return await api(
        client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data=payload
    )


async def upsert_header(client, module_id, title):
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    found = next(
        (
            entry
            for entry in items
            if entry.get("type") == "SubHeader" and entry.get("title") == title
        ),
        None,
    )
    return found or await api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/modules/{module_id}/items",
        data={"module_item[type]": "SubHeader", "module_item[title]": title},
    )


def file_link(file_id, label):
    return f'<a href="/courses/{COURSE_ID}/files/{file_id}/preview" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">{label}</a>'


def image_tag(file_id, alt, max_width=720):
    return f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" style="display:block;width:100%;max-width:{max_width}px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'


def step(number, title, body):
    return f'<h3 style="color:#5a2d91;border-bottom:3px solid #d9c9ed">{number}. {title}</h3>{body}'


def flow(color, title, text):
    return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0 0 6px;color:{color}">{title}</h4>{text}</div>'


QUESTIONS = [
    (
        "Q1 - Data boundary",
        "A Precision Agriculture Systems Technician is not a separate BLS category. What is the accurate way to use the guide?",
        "Use the Agricultural and Food Science Technician figures as parent-occupation evidence and state the limit.",
        [
            "Call $48,480 a DFW starting salary.",
            "Claim every technician uses the same tools.",
            "Treat the specialty as a guaranteed new occupation.",
        ],
        "Correct. Parent-occupation evidence can inform an evaluation when the limit stays visible.",
        "Keep the specialty, parent occupation, measure, geography, and date attached.",
    ),
    (
        "Q2 - Median",
        "What does the May 2024 U.S. median show?",
        "Half of workers in that occupation earned more and half earned less.",
        [
            "The guaranteed first-year salary in Irving.",
            "The amount every employer must pay.",
            "The cost of the required degree.",
        ],
        "Correct. Median is a wage measure, not starting pay or a guarantee.",
        "The guide does not provide a DFW starting salary.",
    ),
    (
        "Q3 - Emerging",
        "Why can a specialty be described as emerging even when its parent occupation already exists?",
        "Technology may change the tasks, tools, and skills inside an established occupation.",
        [
            "Every new title creates a new BLS category.",
            "Emerging always means 20% growth.",
            "A social-media post used the word future.",
        ],
        "Correct. Emerging work may be a change in tasks and tools, not a brand-new category.",
        "Look for the choice that explains how work changes.",
    ),
    (
        "Q4 - Technology link",
        "Which evidence best connects agricultural engineering to changing technology?",
        "BLS notes work with AI, geospatial systems, and automated irrigation, spraying, and harvesting.",
        [
            "The job has the highest salary in the table.",
            "All farms use identical robots.",
            "The title includes the word engineer.",
        ],
        "Correct. The claim uses a named technology and changed task.",
        "A strong emerging-career claim links technology to work rather than relying on pay or title alone.",
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
    final = await paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions")
    by_name = {entry.get("question_name"): entry for entry in final}
    if set(by_name) != set(expected_names) or len(final) != len(expected_names):
        raise RuntimeError(
            f"Quiz {quiz_id} question mismatch: "
            f"{[entry.get('question_name') for entry in final]}"
        )
    fields = []
    for name in expected_names:
        fields.extend(
            [("order[][id]", str(by_name[name]["id"])), ("order[][type]", "question")]
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
            f"Expected at most one quiz named {QUIZ_TITLE!r}; found {len(matches)}"
        )
    quiz = matches[0] if matches else None
    data = {
        "quiz[title]": QUIZ_TITLE,
        "quiz[description]": "<p>Ungraded practice. Retry and use the feedback before submitting the Emerging Plant-Tech Evaluation.</p>",
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
    expected = [entry[0] for entry in QUESTIONS]
    existing = await prepare_quiz_questions(client, quiz["id"], set(expected))
    for position, (
        name,
        text,
        correct,
        wrong,
        correct_comment,
        incorrect_comment,
    ) in enumerate(QUESTIONS, 1):
        found = next((q for q in existing if q.get("question_name") == name), None)
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
                + [{"answer_text": value, "answer_weight": 0} for value in wrong],
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
    quiz = await api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
    if quiz.get("published") or quiz.get("quiz_type") != "practice_quiz":
        raise RuntimeError(
            f"Practice quiz invariant failed: published={quiz.get('published')}, "
            f"type={quiz.get('quiz_type')}"
        )
    return quiz


async def require_major_assignment(client):
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == PACKET_TITLE]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one existing mapped Major assignment named {PACKET_TITLE!r}; found {len(matches)}"
        )
    found = matches[0]
    if float(found.get("points_possible") or 0) != 100:
        raise RuntimeError(
            f"Refusing to modify {PACKET_TITLE!r}: expected 100 points, found {found.get('points_possible')}"
        )
    groups = await paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group = next(
        (
            entry
            for entry in groups
            if entry.get("id") == found.get("assignment_group_id")
        ),
        None,
    )
    if not group or group.get("name") != "Major Assessments (60%)":
        raise RuntimeError(
            f"Refusing to modify {PACKET_TITLE!r}: expected Major Assessments (60%) group"
        )
    data = {
        "assignment[description]": "<p>Submit the Farm-to-Table infographic and the individual Emerging Plant-Tech Evaluation. Canva, Adobe Express, paper, or another approved route is equal. Do not include real personal contact information.</p>",
        "assignment[submission_types][]": [
            "online_upload",
            "online_text_entry",
            "media_recording",
        ],
        "assignment[published]": "false",
    }
    packet = await api(
        client, "PUT", f"/courses/{COURSE_ID}/assignments/{found['id']}", data=data
    )
    if (
        packet.get("published")
        or float(packet.get("points_possible") or 0) != 100
        or packet.get("assignment_group_id") != group["id"]
        or packet.get("grading_type") != "points"
        or packet.get("omit_from_final_grade") is not False
    ):
        raise RuntimeError(
            f"Major invariant failed after update: published={packet.get('published')}, "
            f"points={packet.get('points_possible')}, group={packet.get('assignment_group_id')}, "
            f"grading={packet.get('grading_type')}, omit={packet.get('omit_from_final_grade')}"
        )
    return packet


async def upsert_career_assignment(client):
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == CAREER_TITLE]
    if len(matches) > 1:
        raise RuntimeError(
            f"Expected at most one assignment named {CAREER_TITLE!r}; found {len(matches)}"
        )
    found = matches[0] if matches else None
    data = {
        "assignment[name]": CAREER_TITLE,
        "assignment[description]": '<div style="max-width:820px;margin:0 auto;font-family:Arial,Helvetica,sans-serif;line-height:1.5;color:#24323d"><h2 style="color:#5a2d91">Plant Career Connection</h2><p><strong>Submit only three details:</strong> one chosen plant-system role, one accurate duty, and one preparation fact.</p><p><strong>Complete frame:</strong> “A [role] would [duty]. A typical entry route is [preparation].”</p><p>Keep the first-repair decision, two clues, and labeled system improvement in <em>Find Your Future</em> pp. 89-90. Do not copy those workbook responses into this check.</p></div>',
        "assignment[submission_types][]": ["online_text_entry"],
        "assignment[grading_type]": "not_graded",
        "assignment[points_possible]": "0",
        "assignment[omit_from_final_grade]": "true",
        "assignment[published]": "false",
    }
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
        or "online_text_entry" not in (assignment.get("submission_types") or [])
    ):
        raise RuntimeError(
            f"Career practice invariant failed: published={assignment.get('published')}, "
            f"points={assignment.get('points_possible')}, grading={assignment.get('grading_type')}, "
            f"omit={assignment.get('omit_from_final_grade')}, submissions={assignment.get('submission_types')}"
        )
    return assignment


async def upsert_practice_assignment(client):
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [
        entry
        for entry in assignments
        if entry.get("name") in {REFLECTION_TITLE, LEGACY_REFLECTION_TITLE}
    ]
    if len(matches) > 1:
        raise RuntimeError(
            f"Expected at most one assignment named {REFLECTION_TITLE!r}; found {len(matches)}"
        )
    found = matches[0] if matches else None
    data = {
        "assignment[name]": REFLECTION_TITLE,
        "assignment[description]": "<p>Submit the private Plant-Career Evidence Reflection as text or upload the supplied PDF. Use one fixed Plant-Tech Guide fact and one fair investigation strategy. Do not post a public discussion.</p>",
        "assignment[submission_types][]": ["online_text_entry", "online_upload"],
        "assignment[grading_type]": "not_graded",
        "assignment[points_possible]": "0",
        "assignment[omit_from_final_grade]": "true",
        "assignment[published]": "false",
    }
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
    ):
        raise RuntimeError(
            f"Reflection invariant failed: published={assignment.get('published')}, "
            f"points={assignment.get('points_possible')}, grading={assignment.get('grading_type')}, "
            f"omit={assignment.get('omit_from_final_grade')}"
        )
    return assignment


async def upsert_transfer_assignment(client):
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == TRANSFER_TITLE]
    if len(matches) > 1:
        raise RuntimeError(
            f"Expected at most one assignment named {TRANSFER_TITLE!r}; found {len(matches)}"
        )
    found = matches[0] if matches else None
    data = {
        "assignment[name]": TRANSFER_TITLE,
        "assignment[description]": "<p>Name one communication skill used in your infographic. Explain how an Agricultural Communications Specialist uses that skill and how a worker in one other career uses the same skill for a different task. Submit two sentences as text or a short private recording.</p>",
        "assignment[submission_types][]": ["online_text_entry", "media_recording"],
        "assignment[grading_type]": "not_graded",
        "assignment[points_possible]": "0",
        "assignment[omit_from_final_grade]": "true",
        "assignment[published]": "false",
    }
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
    ):
        raise RuntimeError(
            f"Transfer invariant failed: published={assignment.get('published')}, "
            f"points={assignment.get('points_possible')}, grading={assignment.get('grading_type')}, "
            f"omit={assignment.get('omit_from_final_grade')}"
        )
    return assignment


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as client:
        module = await ensure_module(client)
        quiz = await upsert_quiz(client)
        packet = await require_major_assignment(client)
        career = await upsert_career_assignment(client)
        transfer = await upsert_transfer_assignment(client)
        reflection = await upsert_practice_assignment(client)

        support_path = "course files/CCR Materials/3SW/Wk2"
        support_folder = await ensure_folder(client, support_path)
        names = {
            "CAREERS": "3sw-wk2-plant-career-evidence-guide.pdf",
            "PLANNER": "3sw-wk2-farm-to-table-planner.pdf",
            "RUBRIC": "3sw-wk2-plant-science-major-rubric.pdf",
            "EMERGING_GUIDE": "3sw-wk2-emerging-plant-tech-evidence.pdf",
            "EMERGING_EVAL": "3sw-wk2-emerging-plant-tech-evaluation.pdf",
            "BIAS_REFLECT": "3sw-wk2-xello-biases-reflection.pdf",
        }
        files = {
            key: await upload(
                client, ROOT / "docs/resources/worksheets" / name, support_path
            )
            for key, name in names.items()
        }
        folders, uploads = {}, {}
        for day in range(1, 6):
            folder_path = f"course files/CCR Materials/3SW/Wk2/Day {day} Visuals"
            folders[day], uploads[day] = await ensure_folder(client, folder_path), {}
            source = ASSETS / f"day{day}"
            if source.exists():
                for path in sorted(source.glob("*.png")):
                    if day == 5 and path.name.startswith("xello-biases-"):
                        continue
                    uploads[day][path.name] = await upload(client, path, folder_path)
        support_folder = await lock_folder_files(client, support_folder)
        for day, folder in folders.items():
            folders[day] = await lock_folder_files(client, folder)

        quiz_url = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        packet_url = f"/courses/{COURSE_ID}/assignments/{packet['id']}"
        career_url = f"/courses/{COURSE_ID}/assignments/{career['id']}"
        transfer_url = f"/courses/{COURSE_ID}/assignments/{transfer['id']}"
        reflection_url = f"/courses/{COURSE_ID}/assignments/{reflection['id']}"

        def workbook_page(day, filename, alt, label):
            file_id = uploads[day][filename]["id"]
            return image_tag(file_id, alt, 650) + f"<p>{file_link(file_id, label)}</p>"

        grow_pages = {
            1: workbook_page(
                1,
                "fyf-grow-system-rescue-1.png",
                "Find Your Future Grow System Rescue page 88",
                "Open FYF p. 88 full size",
            ),
            2: workbook_page(
                1,
                "fyf-grow-system-rescue-2.png",
                "Find Your Future Grow System Rescue page 89",
                "Open FYF p. 89 full size",
            ),
            3: workbook_page(
                1,
                "fyf-grow-system-rescue-3.png",
                "Find Your Future Grow System Rescue page 90",
                "Open FYF p. 90 full size",
            ),
        }
        farm_pages = {
            1: workbook_page(
                2,
                "fyf-farm-to-table-1.png",
                "Find Your Future Farm to Table client brief page 91",
                "Open FYF p. 91 full size",
            ),
            2: workbook_page(
                2,
                "fyf-farm-to-table-2.png",
                "Find Your Future Farm to Table planning and interview page 92",
                "Open FYF p. 92 full size",
            ),
        }
        # Canvas strips CSS aspect-ratio from iframe styles. Keep explicit dimensions so
        # the player does not collapse to the browser's 150-pixel default height.
        bls_video = '<details style="border:1px solid #bad4df;border-radius:8px;padding:12px 16px;margin:14px 0;background:#f2f8fb"><summary style="font-weight:700;color:#1f617a;cursor:pointer">Optional: watch the BLS Agricultural Engineers video</summary><p style="font-size:14px">This video is enrichment. The fixed evidence guide carries every required fact.</p><div style="max-width:760px;margin:12px auto"><iframe width="760" height="428" style="display:block;width:100%;max-width:760px;border:0" src="https://www.youtube.com/embed/ozIUJsnBDLY" title="U.S. Bureau of Labor Statistics video: Agricultural Engineers" loading="lazy" allowfullscreen></iframe></div></details>'
        process_wireframe = '''<details style="border:1px solid #bad4df;border-radius:8px;padding:12px 16px;margin:14px 0;background:#f2f8fb"><summary style="font-weight:700;color:#1f617a;cursor:pointer">Teacher model: four-step process infographic wireframe</summary><p><strong>Use this structure, not its wording.</strong> The model shows reading order and space planning without completing the Sunny Fields task for students.</p><div style="max-width:720px;margin:12px auto;border:2px solid #5a2d91;border-radius:10px;padding:14px;background:#fff"><p style="margin:0 0 12px;text-align:center;font-size:22px;font-weight:700;color:#5a2d91">[Clear title for the chosen crop]</p><div style="border-left:6px solid #4a9d2f;padding:8px 12px;margin:8px 0"><strong>1 · Planting</strong><br>[one short explanation] + [one labeled visual]</div><div style="border-left:6px solid #1f617a;padding:8px 12px;margin:8px 0"><strong>2 · Growing and monitoring</strong><br>[one short explanation] + [one labeled visual]</div><div style="border-left:6px solid #e3ad19;padding:8px 12px;margin:8px 0"><strong>3 · Harvesting and packing</strong><br>[one short explanation] + [one labeled visual]</div><div style="border-left:6px solid #9a4f79;padding:8px 12px;margin:8px 0"><strong>4 · Selling or delivery</strong><br>[one short explanation] + [one labeled visual]</div><p style="margin:12px 0 0;padding:10px;background:#f7f1fb"><strong>Two client-fact callouts:</strong> [fact + why a shopper cares] · [fact + why a shopper cares]</p></div><p><strong>Reader path:</strong> title → steps 1–4 → two fact callouts. During the model, point to each region and ask, “Where does your eye go next?”</p></details>'''

        contracts = {
            1: {
                "TOPIC": "Plant Careers",
                "OBJECTIVE": "Students will identify one plant-system career role and describe one preparation fact connected to that work.",
                "TEKS": "d(1)(C), d(2)(A)",
                "DOL": "First-repair decision supported by two clues, one labeled system improvement, and one accurate career-role connection that includes a preparation fact.",
                "STUDENT_OBJECTIVE": "identify one plant-system career role and one way a person prepares for that work.",
                "STUDENT_DOL": "defend a first repair with two clues, label one improvement, and connect the work to one career role and its preparation.",
            },
            2: {
                "TOPIC": "Client Communication",
                "OBJECTIVE": "Students will identify an agricultural communication career opportunity by translating a fictional client brief into an accurate visual plan.",
                "TEKS": "d(1)(C)",
                "DOL": "Four-step content plan, two client facts, full-page sketch, two interview questions in FYF p. 92, and one accurate Agricultural Communications Specialist role connection.",
                "STUDENT_OBJECTIVE": "plan a clear farm-to-table message that meets a fictional client's requirements.",
                "STUDENT_DOL": "complete a four-step plan, choose two useful client facts, sketch the page, write two interview questions, and explain what an Agricultural Communications Specialist produces for a client.",
            },
            3: {
                "TOPIC": "Transferable Communication",
                "OBJECTIVE": "Students will identify how visual communication and audience awareness transfer between agricultural communication and another career.",
                "TEKS": "d(4)(B)",
                "DOL": "Completed infographic, documented revision, and a two-career explanation of how one communication skill transfers.",
                "STUDENT_OBJECTIVE": "build and revise a clear infographic, then explain how one communication skill works in two careers.",
                "STUDENT_DOL": "complete and save the infographic, name one revision, and compare how the same skill is used in agricultural communication and another career.",
            },
            4: {
                "TOPIC": "Emerging Plant Technology",
                "OBJECTIVE": "Students will evaluate how a changing technology or trend affects tasks and career choices in plant and agriculture work.",
                "TEKS": "d(1)(D), d(5)(C)",
                "DOL": "Individual 4-6 sentence evaluation using a technology-to-task connection, two dated facts, and one data limit.",
                "STUDENT_OBJECTIVE": "evaluate how one technology changes agriculture work without turning a broad data source into a job promise.",
                "STUDENT_DOL": "write a 4-6 sentence evaluation with one changed task, two dated facts, and one evidence limit.",
            },
            5: {
                "TOPIC": "Fair Career Investigation",
                "OBJECTIVE": "Students will revisit an assumption about emerging or nontraditional career work and evaluate it with one career fact.",
                "TEKS": "d(1)(D)",
                "DOL": "Revised plant-tech evidence plus a private assumption-evidence-action reflection.",
                "STUDENT_OBJECTIVE": "use evidence to test a career assumption before ruling a career in or out.",
                "STUDENT_DOL": "revise one evidence link and submit a private reflection with one assumption, one fixed career fact, and one fair next action.",
            },
        }

        student = {
            1: {
                "TITLE": "Diagnose a Grow System",
                "PURPOSE": "Use plant-system clues to choose a first repair and connect the work to real careers.",
                "TODAY": "<ul><li>compare three plant-system careers and their preparation;</li><li>diagnose a fictional hydroponic problem;</li><li>defend the first repair.</li></ul>",
                "READY": f'<p>Open {file_link(files["CAREERS"]["id"], "the Plant Systems Career Evidence Guide")} and use FYF pp. 88-90.</p>',
                "MEDIA": "",
                "STEPS": step(
                    1,
                    "Meet the work",
                    student_copy_button(1, "Make your copy: Diagnose a Grow System") + (grow_pages[1]
                    + f'<p>Compare technician, scientist, and engineer duties and typical entry routes. Choose the role most likely to test the system first.</p><p><a href="{career_url}">Open the private Plant Career Connection check</a>. Submit only your chosen role, one accurate duty, and one preparation fact.</p><p><strong>Career frame:</strong> "A [role] would [duty]. A typical entry route is [preparation]."</p>'),
                )
                + step(
                    2,
                    "Read every clue",
                    grow_pages[2]
                    + "<p>Mark plant symptoms, water movement, light, nutrients, and cleanliness. More than one problem may be present.</p>",
                )
                + step(
                    3,
                    "Choose the first repair",
                    grow_pages[3]
                    + '<p>Use at least two clues on workbook p. 90. Explain why this repair comes before the others.</p><p><strong>Reasoning frame:</strong> "I would fix [repair] first because [clue 1] and [clue 2]."</p>',
                )
                + step(
                    4,
                    "Sketch an improvement",
                    "<p>On workbook p. 90, the back of the page, or plain paper, label water flow, nutrients, lights, plant placement, and one prevention feature.</p>",
                ),
                "EXIT": "<p>Check both evidence homes: the private Canvas check has only the chosen role, duty, and preparation fact; FYF pp. 89-90 hold the first-repair decision, two clues, and labeled improvement.</p>",
                "DONE": "<ul><li>private career check submitted with one role, duty, and preparation fact;</li><li>all clues reviewed in FYF;</li><li>one first repair defended with two clues in FYF;</li><li>one system improvement labeled in FYF.</li></ul>",
                "VISIBLE_SUPPORT": '<p><strong>Word bank:</strong> duty = responsabilidad · preparation = preparación · evidence = evidencia · priority = prioridad.</p><p><strong>Career frame:</strong> "A [role] would [duty]. A typical entry route is [preparation]."</p><p><strong>Repair frame:</strong> "I would fix [repair] first because [clue 1] and [clue 2]."</p>',
                "SUPPORT": "<p>Use labels and short phrases in the sketch. Read the clues aloud or color-code water, light, nutrients, and cleanliness before choosing a repair.</p>",
                "FALLBACK": "<p>The embedded workbook pages and fixed career guide are the complete route. A plain-paper system sketch is equal to chart paper. If Canvas is unavailable, draft the three career details in the FYF margin and transfer only those details to the private check at the next access point.</p>",
            },
            2: {
                "TITLE": "Plan a Farm-to-Table Infographic",
                "PURPOSE": "Turn a fictional client's brief into a clear message for grocery shoppers.",
                "TODAY": "<ul><li>identify the Agricultural Communications Specialist role;</li><li>read the client requirements;</li><li>plan four process steps;</li><li>make a full-page sketch.</li></ul>",
                "READY": f'<p>Open {student_copy_link(2, "the two-page Farm-to-Table Planner")} and {file_link(files["RUBRIC"]["id"], "the student-visible 16-point rubric")}. Use FYF p. 92 for the two interview questions.</p>',
                "MEDIA": "",
                "STEPS": step(
                    1,
                    "Meet the role and client",
                    farm_pages[1]
                    + "<p>The workbook places you in the role of an <strong>Agricultural Communications Specialist</strong>. This worker turns agriculture information into messages for a specific audience. Choose strawberries, grapes, bell peppers, or cucumbers. Treat every farm fact as scenario information, not a claim about a real business.</p>",
                )
                + step(
                    2,
                    "Plan the four steps",
                    "<p>Planting, growing and monitoring, harvesting and packing, then selling or delivery. Give each step one short explanation and one visual.</p>",
                )
                + step(
                    3,
                    "Choose two useful facts",
                    '<p>Explain why each fact matters to an adult grocery shopper.</p><p><strong>Frame:</strong> "A shopper would care about [fact] because [reason]."</p>',
                )
                + step(
                    4,
                    "Sketch, ask, and connect",
                    farm_pages[2]
                    + "<p>Use the planner's full-page box for the infographic sketch. Then write two interview questions in the large boxes on FYF p. 92. Complete the planner's career-connection line by naming what the specialist produces and who uses it.</p>",
                ),
                "EXIT": "<p>What does an Agricultural Communications Specialist produce in this scenario, who uses it, and how does the reading order help that audience?</p>",
                "DONE": "<ul><li>Agricultural Communications Specialist role explained;</li><li>crop and audience named;</li><li>four process steps planned;</li><li>two scenario facts selected;</li><li>full-page sketch shows reading order;</li><li>two interview questions completed on FYF p. 92.</li></ul>",
                "VISIBLE_SUPPORT": '<p><strong>Word bank:</strong> audience = público · harvest = cosecha · consumer = consumidor · reading order = orden de lectura.</p><p><strong>Exit frame:</strong> "The specialist creates [product] for [audience]. The reading order helps by [reason]."</p>',
                "SUPPORT": "<p>Use labels and phrases; full paragraphs are not required. Narrate the sketch to a partner, the teacher, or yourself before adding text.</p>",
                "FALLBACK": "<p>The two-page planner supplies the content plan and full-page sketch. FYF p. 92 supplies the interview-question space. No design login or partner is required today.</p>",
            },
            3: {
                "TITLE": "Build and Test the Infographic",
                "PURPOSE": "Create a readable client artifact and revise it after a quick usability check.",
                "TODAY": "<ul><li>build in Canva, Adobe Express, or on paper;</li><li>check reading order and accessibility;</li><li>explain how communication transfers between careers.</li></ul>",
                "READY": f'<p>Keep {student_copy_link(3, "your planner")} and {file_link(files["RUBRIC"]["id"], "the rubric")} visible.</p>',
                "MEDIA": "",
                "STEPS": step(
                    1,
                    "Choose an equal build route",
                    farm_pages[2]
                    + "<p>Use Canva for Education, Adobe Express, paper/chart paper, or another teacher-approved route. Premium templates and art skill do not earn extra points.</p>",
                )
                + step(
                    2,
                    "Build the message",
                    "<p>Add a title, four ordered steps, one visual per step, and two facts from the fictional brief. Use short, accurate wording.</p>",
                )
                + step(
                    3,
                    "Run a 60-second reader test",
                    "<p>A classmate, teacher, or self-check names where the eye goes first and one unclear spot. No same-crop partner is required.</p>",
                )
                + step(
                    4,
                    "Revise, save, and transfer",
                    f'<p>Fix one message or accessibility problem. Save the infographic with your name and keep it for tomorrow; do not submit it to the Major yet.</p><p><a href="{transfer_url}">Open the private Communication Skill Transfer check</a>. Submit two sentences or a short private recording. <strong>Complete frame:</strong> "[Skill] helps an Agricultural Communications Specialist [specific task]. The same skill helps a [second career] [different task]." This is the formative d(4)(B) evidence; it is not another major-grade criterion.</p>',
                ),
                "EXIT": "<p>Name one communication skill you used. How would the same skill help an Agricultural Communications Specialist and a worker in one other career?</p>",
                "DONE": "<ul><li>four steps and two facts;</li><li>clear reading order;</li><li>readable text and contrast;</li><li>one revision;</li><li>infographic saved for tomorrow;</li><li>private two-career transfer check submitted.</li></ul>",
                "VISIBLE_SUPPORT": '<p><strong>Word bank:</strong> clarity = claridad · contrast = contraste · revise = revisar · audience = público.</p><p><strong>Frame:</strong> "[Skill] helps an Agricultural Communications Specialist [task]. The same skill helps a [second career] [different task]."</p>',
                "SUPPORT": "<p>Use built-in icons, shapes, or your own drawings. Text-to-speech can check wording. A teacher or self-check can replace peer feedback.</p>",
                "FALLBACK": "<p>Paper is an equal route. Photograph or scan the finished page for Canvas; if upload fails, turn in the labeled original and record the access issue. The transfer check can be a private oral response to the teacher if Canvas fails.</p>",
            },
            4: {
                "TITLE": "Evaluate Emerging Plant-Tech Work",
                "PURPOSE": "Explain how technology changes real agriculture tasks without inventing a job-market promise.",
                "TODAY": "<ul><li>separate a specialty from its BLS parent occupation;</li><li>evaluate one technology-to-task change;</li><li>state what the data cannot prove.</li></ul>",
                "READY": f'<p>Open {file_link(files["EMERGING_GUIDE"]["id"], "the Emerging Plant-Tech Evidence Guide")} and {student_copy_link(4, "the two-page evaluation")}.</p>',
                "MEDIA": bls_video,
                "STEPS": step(
                    1,
                    "Choose one specialty",
                    "<p>Precision agriculture systems technician, controlled-environment plant scientist, or agricultural automation engineer.</p>",
                )
                + step(
                    2,
                    "Trace the change",
                    '<p>Connect one named technology to one changed task and one needed skill or preparation route.</p><p><strong>Complete frame:</strong> "[Technology] changes the task of [task] because workers now [specific action]. This makes [skill or preparation] important."</p>',
                )
                + step(
                    3,
                    "Use two dated facts",
                    '<p>Keep the parent occupation, U.S. median, date, and outlook labels attached. State one evidence limit.</p><p><strong>Complete frame:</strong> "The [parent occupation] figure is a May 2024 U.S. median, so it cannot prove [local starting pay or exact specialty pay]."</p>',
                )
                + step(
                    4,
                    "Check the reasoning",
                    f'<p><a href="{quiz_url}">Open the Emerging Plant-Tech Evidence Check</a>. Retry and revise your evaluation. Then <a href="{packet_url}">open the Plant Science Evidence Packet assignment</a> and submit the saved infographic plus today\'s evaluation together, one time.</p>',
                ),
                "EXIT": '<p>Why is "technology is changing the work" more accurate than claiming every specialty is a brand-new occupation?</p>',
                "DONE": "<ul><li>specialty and parent occupation named;</li><li>technology connected to a task;</li><li>two dated facts;</li><li>one data limit;</li><li>4-6 sentence evaluation revised and submitted.</li></ul>",
                "VISIBLE_SUPPORT": '<p><strong>Word bank:</strong> specialty = especialidad · parent occupation = ocupación principal · automation = automatización · limit = límite.</p><p><strong>Frame:</strong> "This specialty deserves more investigation because [technology] changes [task]. The data cannot prove [limit]."</p>',
                "SUPPORT": "<p>Highlight specialty, parent occupation, measure/date, and limitation in four different patterns or colors. The evaluation gives ten lines for the 4-6 sentence response.</p>",
                "FALLBACK": "<p>The fixed guide is the complete no-search route. Skip the video if blocked. The quiz is practice; use the paper self-check if Canvas is unavailable.</p>",
            },
            5: {
                "TITLE": "Test a Plant-Career Assumption with Evidence",
                "PURPOSE": "Strengthen one plant-tech evidence link and test a career assumption with a fixed fact.",
                "TODAY": "<ul><li>audit one plant-tech evidence link;</li><li>test one assumption privately;</li><li>choose a fair way to investigate a career.</li></ul>",
                "READY": f'<p>Open {file_link(files["EMERGING_GUIDE"]["id"], "the Emerging Plant-Tech Evidence Guide")}, your Day 4 evaluation, and {student_copy_link(5, "the private reflection")}. Keep personal identity and experiences private unless you choose to share them.</p>',
                "MEDIA": "",
                "STEPS": step(
                    1,
                    "Warm up",
                    "<p>Think privately: Where do people learn assumptions about careers? You may pass on public sharing.</p>",
                )
                + step(
                    2,
                    "Audit one evidence link",
                    "<p>Reopen the Day 4 evaluation. Strengthen the technology-to-task link, one source label, or the evidence limit using the fixed guide.</p>",
                )
                + step(
                    3,
                    "Test an assumption with evidence",
                    '<p>Use one fixed Plant-Tech Guide fact. You do not need to disclose a protected identity or personal experience.</p><p><strong>Complete frame:</strong> "People may assume [idea]. The fact [evidence] challenges or complicates that idea because [reason]."</p>',
                )
                + step(
                    4,
                    "Submit privately",
                    f'<p>Complete the PDF or <a href="{reflection_url}">open the private Canvas assignment</a>. Then <a href="{packet_url}">revise and submit the evidence packet</a> if your teacher has not already collected it. Do not use a public discussion.</p>',
                ),
                "EXIT": "<p>What is one fair action, such as reading a profile, taking a course, interviewing a worker, or job shadowing, that can test an assumption before you rule a career out?</p>",
                "DONE": "<ul><li>one plant-tech evidence link revised;</li><li>one assumption tested with a fixed career fact;</li><li>one fair next action and private submission complete.</li></ul>",
                "VISIBLE_SUPPORT": '<p><strong>Word bank:</strong> bias = sesgo · assumption = suposición · challenge = cuestionar · evidence = evidencia.</p><p><strong>Frame:</strong> "People may assume [idea]. The fact [evidence] challenges or complicates that idea because [reason]."</p>',
                "SUPPORT": "<p>A teacher may read prompts aloud and conference privately. Students may use an assumption from media or general culture instead of personal disclosure.</p>",
                "FALLBACK": "<p>Use the fixed Plant-Tech Guide and the paper or Canvas response home your teacher assigned.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Diagnose a Grow System",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(2)(A)",
                "ALERT": "<strong>Do not turn Day 1 into an open H&amp;L search.</strong> The fixed career guide and licensed workbook carry the lesson with no login or live-data verification burden.",
                "PREP": f'<ul><li><strong>Per student:</strong> FYF workbook pp. 88-90 and pencil. Keep one sheet of plain paper per student available only if the workbook sketch space is not usable.</li><li><strong>Devices:</strong> one per student or one per pair for {file_link(files["CAREERS"]["id"], "the career guide")}; default print count is 0. Print one guide per pair only for a no-device class.</li><li>Open the unpublished private <strong>{CAREER_TITLE}</strong> assignment. It accepts one individual Canvas text response and remains 0-point, not graded, and omitted from the final grade.</li><li><strong>Grouping:</strong> individual evidence; optional pairs for the warm-up and clue comparison.</li><li>Model one two-clue diagnosis without giving the final priority.</li></ul>',
                "EVIDENCE": "<p><strong>FYF pp. 89-90:</strong> first-repair decision supported by two clues and one labeled system improvement. <strong>Private Canvas practice check:</strong> one chosen role, one accurate duty, and one preparation fact. Do not make students copy the grow-system response into Canvas.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and grow-system inputs warm-up", '''<p>Welcome students to Week 2 of Agriculture and project the agricultural technology launch prompt.</p><ul><li>Ask students: <em>“In an automated indoor hydroponic or vertical farming system, what are the four non-negotiable physical inputs that MUST reach every single plant root continuously to ensure crop survival?”</em></li><li>Collect 2-3 student thoughts. Catalog the four essential inputs: (1) Oxygenated water circulation, (2) Balanced dissolved mineral nutrients, (3) Adequate photosynthetic LED lighting, and (4) Proper temperature and pH balance.</li><li>Bridge with, <em>“When crops fail in controlled environment agriculture, technicians cannot guess; they must isolate the malfunctioning subsystem. Today you diagnose a hydroponic failure on FYF pp. 88-90.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-13 - Fixed career evidence and credential benchmark check", '''<p>Direct students to the Plant Career Evidence Guide and open the private Canvas Career Check:</p><ul><li>Analyze three plant science occupations:<br>• <em>Agricultural and Food Science Technician:</em> Associate degree; May 2024 U.S. median pay $48,480; sets up laboratory grow tests, calibrates sensors, monitors water pumps and nutrient delivery.<br>• <em>Soil and Plant Scientist:</em> Bachelor's degree; May 2024 U.S. median pay $71,410; researches plant genetics, soil chemistry, disease resistance, and crop yields.<br>• <em>Agricultural Engineer:</em> Bachelor's degree in engineering; May 2024 U.S. median pay $84,630; designs automated climate controls, irrigation pumps, and greenhouse structures.</li><li>Students submit ONE chosen role, ONE verified daily task, and ONE exact preparation credential in Canvas.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 10): Confirm all students submit their private role/duty/credential check before opening the case clues.</li></ul>''')
                    + flow("#1f617a", "Minutes 13-33 - Investigating the hydroponic grow-system failure (FYF pp. 88-89)", '''<p>Students examine the five diagnostic clues from the fictional vertical farm:</p><ul><li>Clue 1: Reservoir water level is full, but lower tray plants show severe wilting and leaf yellowing (chlorosis).</li><li>Clue 2: Submersible pump motor is humming and warm to touch, but water flow rate out of the manifold is a trickle (0.2 gal/min vs. 2.0 gal/min normal).</li><li>Clue 3: Upper trays receive normal nutrient misting; lower trays show zero active misting.</li><li>Clue 4: Nutrient reservoir EC (electrical conductivity) and pH are within normal parameters.</li><li>Clue 5: Filter screen at the intake manifold has heavy algae and sediment accumulation.</li><li>Guide students to avoid the single-symptom fallacy: Yellow leaves do NOT automatically mean nutrient deficiency; here, pump manifold blockage prevents the solution from circulating.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 2 (Minute 24): Verify students mark evidence across all 5 clues before declaring a repair.</li></ul>''')
                    + flow("#e3ad19", "Minutes 33-45 - Prioritizing the first repair and schematic engineering", '''<p>Students author their engineering decision on FYF pp. 89-90:</p><ul><li>1. <strong>First-Repair Priority:</strong> Specify the immediate mechanical repair (clear intake filter and flush pump manifold blockage). Defend why this takes priority over adjusting nutrients or replacing lights.</li><li>2. <strong>Labeled System Schematic:</strong> Sketch the repaired grow loop, drawing callout labels for the reservoir, pump, filter, delivery manifold, root tray, and return drain.</li><li>3. <strong>Long-term Prevention Feature:</strong> Add ONE preventative engineering improvement (e.g., automated dual inline pre-filters or optical flow sensors with audio alarm).</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 3 (Minute 38): Check schematics; ensure students use technical arrows and functional labels, not just decorative drawings.</li></ul>''')
                    + flow("#1f617a", "Minutes 45-50 - Verification of two evidence homes and workspace reset", '''<p>Verify both evidence homes: FYF pp. 89-90 physical workbook and the private Canvas career check.</p><ul><li><strong>Safe Trim:</strong> At minute 35, convert detailed pictorial drawings to functional block diagrams with labels; fiercely protect the 2-clue repair defense, prevention feature, and Canvas career check.</li></ul>''')
                ),
                "MONITOR": "<p><strong>District moves:</strong> use a 60-second Stop and Jot for the warm-up, then Active Monitor the individual evidence. <strong>Minute 13 target:</strong> each student has submitted one role, one duty, and one preparation fact in the private Canvas check. If several students copy salary figures, pause and model duty → preparation once. <strong>Minute 28 target:</strong> every FYF clue is marked before a repair is chosen. Strong reasoning often prioritizes slow water flow/pump or blockage because weak roots and uneven growth support inadequate circulation; accept another first repair when two supplied clues and a coherent sequence support it. Students should not claim one symptom proves one cause. Career key: technician tests/records and usually follows an associate-degree route; scientist studies plant/soil conditions and typically needs at least a bachelor's degree; engineer designs system changes and typically needs an engineering bachelor's degree.</p><p><strong>Safe trim:</strong> reduce the system sketch to labels and arrows. Protect the private role-duty-preparation response and the FYF two-clue first-repair decision.</p>",
                "RESOURCES": f'<p>{file_link(files["CAREERS"]["id"], "Dated career evidence guide")} · The private Canvas check is the only career-response submission home. H&amp;L browsing is optional enrichment only.</p>',
                "SUPPORT": "<p>Read clues aloud, color-code water/light/nutrients/cleanliness, allow oral rehearsal, and accept labeled diagrams plus short phrases. The workbook provides substantial writing space on pp. 89-90.</p>",
                "FALLBACK": "<p>All licensed pages are embedded. An absent student completes the same individual FYF decision and sketch plus the private Canvas career check; partner comparison is optional. If Canvas is unavailable, draft the three career details in the FYF margin and transfer only those details at the next access point.</p>",
            },
            2: {
                "TITLE": "Plan a Farm-to-Table Infographic",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>Sunny Fields Farm is fictional.</strong> Preserve workbook facts as scenario details; do not convert them into claims about a real business or current agriculture practice.",
                "PREP": f'<ul><li><strong>Per student:</strong> FYF workbook pp. 91-92, {file_link(files["PLANNER"]["id"], "the two-page planner")} printed double-sided, pencil, and markers or colored pencils. Post the {file_link(files["RUBRIC"]["id"], "student rubric")} digitally; default rubric print count is 0.</li><li><strong>Teacher display:</strong> open the supplied four-step wireframe below. No design login is needed.</li><li><strong>Grouping:</strong> individual plan; pairs of two only for the brief trace and reader-path rehearsal.</li></ul>' + process_wireframe,
                "EVIDENCE": "<p>Client requirement map, four-step content plan, two useful facts, full-page sketch, two interview questions on FYF p. 92, and one accurate Agricultural Communications Specialist role connection. This begins the recommended major packet.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and food journey stages warm-up", '''<p>Welcome students, seat them with FYF pp. 91-92, and project the supply-chain prompt.</p><ul><li>Ask students: <em>“From the moment a seed is planted in soil to the moment fresh produce arrives on a school cafeteria tray, what are the four major operational stages that food travels through? Name all four in order.”</em></li><li>Collect 2-3 student responses: (1) Planting &amp; Cultivation, (2) Monitoring &amp; Growth Management, (3) Harvesting &amp; Processing/Packaging, (4) Transportation &amp; Distribution/Delivery.</li><li>Bridge with, <em>“Consumers often have zero knowledge of how food reaches their table. Today you act as an Agricultural Communications Specialist planning an informative public infographic for Sunny Fields Farm.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-13 - Analyzing the Sunny Fields Farm client brief", '''<p>Project the fictional client brief and review four essential communication criteria:</p><ul><li>1. <strong>Professional Role:</strong> Agricultural Communications Specialist (creates visual and written media translating complex agricultural science for the public).</li><li>2. <strong>Target Audience:</strong> Local middle school students and families visiting the community farm market.</li><li>3. <strong>Crop Selection:</strong> Choose ONE crop profile (Hydroponic Butterhead Lettuce, Heirloom Roma Tomatoes, or Greenhouse Strawberries).</li><li>4. <strong>Required Client Content:</strong> Must incorporate at least TWO verified numerical farm facts from the brief (e.g., 90% water reduction compared to field agriculture; zero synthetic pesticide application).</li></ul>''')
                    + flow("#1f617a", "Minutes 13-33 - Constructing the four-stage content planner", '''<p>Students independently complete their two-page Farm-to-Table Planner:</p><ul><li>Stage 1 (Planting): Detail seed germination, substrate choice, and initial nutrient soaking.</li><li>Stage 2 (Growing &amp; Monitoring): Detail automated sensor monitoring, pest scouting, and daily EC/pH testing.</li><li>Stage 3 (Harvesting &amp; Packing): Detail sanitized hand-harvesting, cold-water washing, and biodegradable packaging.</li><li>Stage 4 (Selling &amp; Delivery): Detail refrigerated transport within a 25-mile local radius directly to neighborhood schools.</li><li>Enforce client integrity: Integrate the two chosen numerical facts directly into stages 1 and 2.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 22): Check that students use ONLY supplied client facts, avoiding invented statistics.</li></ul>''')
                    + flow("#e3ad19", "Minutes 33-45 - Drafting the full-page wireframe schematic", '''<p>Students draft a full-page wireframe schematic of their infographic:</p><ul><li>Establish a clear visual hierarchy: Prominent Title Banner &rarr; Chronological 4-Box Z-Pattern Reading Flow &rarr; Callout Stat Bubbles for the two numerical facts &rarr; Bottom Client Contact &amp; Source Footer.</li><li>Students turn to FYF p. 92 and author TWO investigative interview questions they would ask a commercial hydroponic grower to gather further technical data.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 2 (Minute 39): Verify wireframe shows distinct visual regions and reading arrows, not a single unreadable wall of text.</li></ul>''')
                    + flow("#1f617a", "Minutes 45-50 - Agricultural communications DOL and workspace reset", '''<p>Direct students to the Day 2 Exit Ticket.</p><ul><li>Prompt: <em>“State the title of the communication professional who created this visual, name the target audience, and describe how your visual design guides the reader's eye from Stage 1 to Stage 4.”</em></li><li>Collect planners or verify completion.</li><li><strong>Safe Trim:</strong> Omit partner rehearsal; protect the 4-stage content plan, 2 client facts, wireframe sketch, and FYF p. 92 interview questions.</li></ul>''')
                ),
                "MONITOR": "<p><strong>District moves:</strong> Think-Pair-Share the brief trace, then Active Monitor the planner. <strong>Minute 13 target:</strong> every student has marked role, audience, crop choices, and required content. If the class confuses scenario facts with outside research, reset with “Use only what the client supplied.” <strong>Minute 30 target:</strong> all four stages and two client facts are planned. Require planting, growing/monitoring, harvesting/packing, and selling/delivery. Students may choose any listed crop. The role connection should identify that an Agricultural Communications Specialist creates an agriculture message or visual for a specific audience. The custom planner adds only the roomy content plan and full-page sketch. Students use the two large boxes already provided on FYF p. 92 for interview questions.</p><p><strong>Safe trim:</strong> cut the share-out or narrated rehearsal. Protect the four-step plan, two facts, full-page sketch, and two interview questions.</p>",
                "RESOURCES": "<p>Licensed FYF pp. 91-92 are embedded at the step where students use them. Canva and Adobe are not needed until Day 3.</p>",
                "SUPPORT": "<p>Use icons plus words, provide the four-step word bank at the point of use, accept phrases, and let students narrate the sketch before writing. Do not grade drawing quality.</p>",
                "FALLBACK": "<p>The two-page planner plus FYF p. 92 form the complete absence route. If a student misses partner talk, use a teacher or self trace of the reading order.</p>",
            },
            3: {
                "TITLE": "Build and Test the Infographic",
                "SUBTITLE": "50 minutes · TEKS d(4)(B)",
                "ALERT": "<strong>Canva for Education, Adobe Express, and paper are equal.</strong> Do not require premium assets, a personal account, or a real social-media post. Submit through Canvas, not Google Classroom.",
                "PREP": f'<ul><li><strong>Per student:</strong> completed Day 2 plan and either one district device or one sheet of paper/chart paper with markers. Keep paper visible from the start.</li><li>Confirm Canva for Education or Adobe Express only if offering the digital route; do not require a personal login.</li><li>Post the {file_link(files["RUBRIC"]["id"], "student rubric")} digitally; default print count is 0. Open only the unpublished transfer check today. The Major opens after Day 4.</li><li><strong>Grouping:</strong> individual artifact; pairs of two for the 60-second reader test, with teacher/self-check as the equal alternate.</li></ul>' + process_wireframe,
                "EVIDENCE": "<p>Farm-to-Table infographic and one documented message/accessibility revision. The separate private Communication Skill Transfer check collects the two-career d(4)(B) response as formative evidence; it is not scored in the major-packet rubric.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and visual design criteria warm-up", '''<p>Welcome students, seat them with their Day 2 wireframes, and project the design standard prompt.</p><ul><li>Ask students: <em>“When a busy reader glances at an infographic for five seconds, what design elements make the difference between a graphic that communicates instantly and one that gets ignored or causes confusion?”</em></li><li>Collect 2-3 responses: High color contrast, readable bold typography, concise chunked text, clear numbered step progression, and relevant icons.</li><li>Bridge with, <em>“Today we produce our final Farm-to-Table Infographic using Canva, Adobe Express, or professional paper drafting, then run a rapid peer readability test.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-13 - Modeling professional visual standards and accessibility", '''<p>Display the approved wireframe exemplar and review the four production rubrics:</p><ul><li>1. <strong>Visual Readability:</strong> High contrast between dark text and light backgrounds; minimum 14pt body text for legibility.</li><li>2. <strong>Information Chunking:</strong> Every stage has a distinct bordered container or color band.</li><li>3. <strong>Factual Accuracy:</strong> Both numerical client facts are highlighted in stat callout boxes with accurate units.</li><li>4. <strong>Accessibility:</strong> Logical top-to-bottom or left-to-right reading order with clear section numbering.</li></ul>''')
                    + flow("#1f617a", "Minutes 13-38 - Infographic production sprint (Digital or Paper Route)", '''<p>Students produce their final graphic using their chosen route (both routes are 100% equal):</p><ul><li>Digital: Construct in Canva for Education / Adobe Express using the 4-region layout.</li><li>Paper: Draft on large white drawing sheets using rulers, colored pens, and highlighters.</li><li>Enforce pacing: At Minute 25 (midpoint), pause class for a 30-second screen check—ensure all students have completed Stages 1 &amp; 2 and are not wasting time searching for decorative stickers.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 22): Verify students place content first before selecting decorative fonts.<br>• Lap 2 (Minute 32): Confirm both client numerical facts are visible on the graphic.</li></ul>''')
                    + flow("#e3ad19", "Minutes 38-45 - 60-Second Reader Test and iterative revision", '''<p>Pairs execute the 60-Second Reader Usability Test:</p><ul><li>Partner A displays their graphic silently to Partner B for exactly 60 seconds.</li><li>Partner B states: (1) The first piece of information their eye caught, and (2) ONE element that felt crowded or unclear.</li><li>Partner A documents ONE specific revision (e.g., bolding Stage 3 heading, increasing font size on the water-saving statistic, increasing whitespace).</li><li>Reverse roles immediately.</li></ul>''')
                    + flow("#1f617a", "Minutes 45-50 - Save artifact and private transfer check DOL", '''<p>Students save their infographic file or store their physical poster.</p><ul><li>Students open the private Canvas Transfer Check and complete the two-career prompt: Explain how visual communication skills function for an Agricultural Communications Specialist vs. a Graphic Designer in Urban Architecture.</li><li>Note: The major packet is submitted once tomorrow after Day 4!</li><li><strong>Safe Trim:</strong> Cut decorative borders; protect the 4 ordered stages, 2 facts, documented user revision, and private transfer check.</li></ul>''')
                ),
                "MONITOR": "<p><strong>District moves:</strong> chunk the build with a visible midpoint and Active Monitor for one criterion at a time. <strong>Minute 13 target:</strong> title, four regions, and reading path are placed. If several students are choosing templates instead of building content, move everyone to the supplied wireframe. <strong>Minute 32 target:</strong> four ordered steps, one visual and short explanation per step, and two scenario facts are visible. Run the 60-second reader test: first look, unclear spot, one revision. The d(4)(B) response must name two different careers and show how one communication skill looks in each; “communication is important” does not demonstrate transfer.</p><p><strong>Safe trim:</strong> cut decorative polish first. Protect one visible revision, the saved artifact, and the private transfer check. Do not collect the Major today.</p>",
                "RESOURCES": f'<p>{file_link(files["PLANNER"]["id"], "Planner")} · {file_link(files["RUBRIC"]["id"], "16-point student rubric")} · The separate ungraded transfer check accepts text or a private recording. Students save and retain the infographic for tomorrow; the combined Major submission happens once after Day 4.</p>',
                "SUPPORT": "<p>Provide a four-box layout, built-in icons, speech-to-text, enlarged print, and a paper route. Score communication rather than artistry or English mechanics unless meaning is unclear.</p>",
                "FALLBACK": "<p>If a design platform fails, move immediately to paper. If Canvas upload fails, collect the labeled original or file and record the access issue.</p>",
            },
            4: {
                "TITLE": "Evaluate Emerging Plant-Tech Work",
                "SUBTITLE": "50 minutes · TEKS d(1)(D), d(5)(C)",
                "ALERT": "<strong>Do not invent a job title's salary.</strong> Every specialty is paired with a real BLS parent occupation, and students must state that limitation.",
                "PREP": f'<ul><li><strong>Per student:</strong> saved infographic, {file_link(files["EMERGING_EVAL"]["id"], "two-page evaluation")} printed double-sided, pencil, and one device for the practice quiz/submit route.</li><li>Post {file_link(files["EMERGING_GUIDE"]["id"], "the dated evidence guide")} digitally; default print count is 0. Print one guide per pair only for a no-device class. Post the {file_link(files["RUBRIC"]["id"], "rubric")} digitally.</li><li>Test or skip the optional official BLS video. Open the unpublished quiz and combined Major assignment.</li><li><strong>Grouping:</strong> individual evaluation and submission; pairs may rehearse the parent/specialty distinction.</li></ul>',
                "EVIDENCE": "<p>Individual technology-to-task evaluation with two dated facts, one evidence limit, and a revision. This completes the recommended 16-point major packet.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and emerging agtech warm-up", '''<p>Welcome students and project the agricultural technology innovation prompt.</p><ul><li>Ask students: <em>“Artificial intelligence, autonomous tractors, drone crop monitoring, and automated gene editing are transforming agriculture. Why can you NOT simply type 'AI Drone Crop Specialist salary' into Google and trust the first number that appears?”</em></li><li>Collect student perspectives. Explain the labor data reality: <strong>Emerging specialized job titles evolve faster than government statistical codes; therefore, economists track them under verified parent occupations.</strong></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-13 - Modeling parent occupations and data limitations", '''<p>Display the Emerging Plant-Tech Evidence Guide and model the parent-specialty relationship:</p><ul><li>Specialty: <strong>Precision Agriculture Systems Technician</strong> &rarr; Verified BLS Parent Occupation: <strong>Agricultural and Food Science Technicians</strong> (SOC 19-4011).</li><li>Labor Market Metrics: May 2024 U.S. median pay $48,480; projected 2024-34 growth 5%; 4,200 annual openings.</li><li>The Data Limitation: <em>“This parent category includes food laboratory quality testers and grain inspectors, so the median reflects the broader field rather than a guarantee for an autonomous tractor specialist.”</em></li><li>Model authoring the limitation sentence: Ground claims in verified parent data while explicitly disclosing statistical boundaries.</li></ul>''')
                    + flow("#1f617a", "Minutes 13-23 - Auditing the three emerging agtech specialties", '''<p>Students read the three dated occupational profiles in the Emerging Plant-Tech Guide:</p><ul><li>1. <strong>Precision Agriculture Systems Technician:</strong> Parent = Agricultural &amp; Food Science Technicians ($48,480 median, 5% growth; Associate degree). Calibrates GPS telemetry, maintains drone spectral cameras, repairs variable-rate fertilizer applicators.</li><li>2. <strong>Controlled Environment Plant Specialist:</strong> Parent = Soil and Plant Scientists ($71,410 median, 5% growth; Bachelor's degree). Formulates hydroponic nutrient chemistry, programs microclimate photoperiods, conducts pathogen assays.</li><li>3. <strong>Agricultural Robotics Systems Integrator:</strong> Parent = Agricultural Engineers ($84,630 median, 6% growth; Bachelor's degree in engineering). Integrates computer vision algorithms, engineers robotic harvesting arms, tests obstacle detection in field conditions.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 18): Verify students pair each specialty with its exact BLS parent title.</li></ul>''')
                    + flow("#e3ad19", "Minutes 23-43 - Authoring the Technology-to-Task Evaluation (Major Packet)", '''<p>Students draft their 4-6 sentence technical evaluation on their Day 4 Evidence Sheet:</p><ul><li>Sentence 1: Name the emerging technology and the specific agricultural specialty.</li><li>Sentence 2: Detail ONE concrete work task where the technician uses this technology.</li><li>Sentence 3: Cite TWO verified labor facts from the parent occupation with complete source attribution (May 2024 U.S. median salary and 2024-34 growth rate).</li><li>Sentence 4: Articulate ONE defensible data limitation explaining why parent data is an approximation.</li><li>Sentence 5: Propose ONE immediate next research step to investigate Texas-specific CTE programs.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 2 (Minute 34): Check data limitations; ensure students do not treat parent medians as local starting wages.</li></ul>''')
                    + flow("#4a9d2f", "Minutes 43-47 - Practice check and self-audit", '''<p>Students take the 4-question Canvas Practice Check or use the paper self-audit rubric.</p><ul><li>Confirm understanding of parent occupation proxies, statistical limitations, and degree requirements.</li></ul>''')
                    + flow("#1f617a", "Minutes 47-50 - Combined Major submission and workspace reset", '''<p>Students submit their completed 16-point Major (Farm-to-Table Infographic + Emerging Tech Evaluation):</p><ul><li>Confirm successful submission on Canvas or collect physical packets.</li><li><strong>Safe Trim:</strong> Skip optional video hook; replace Canvas quiz with independent rubric self-check; protect the 5-sentence evaluation, data limitation, and combined Major submission.</li></ul>''')
                ),
                "MONITOR": "<p><strong>District moves:</strong> chunk the evaluation into technology → task → two dated facts → limit, then Active Monitor each link. <strong>Minute 16 target:</strong> students have a specialty, parent occupation, and technology-to-task chain. If students call the parent median a local starting salary, stop and model the complete limit frame. <strong>Minute 36 target:</strong> 4–6 sentences contain two dated facts and one data limit. Key facts: technician parent = $48,480/5%; soil and plant scientist = $71,410/5%; agricultural engineer = $84,630/6%. All are May 2024 U.S. medians/outlook 2024–34. The figure belongs to the parent occupation and cannot prove an exact specialty's local starting pay.</p><p><strong>Safe trim:</strong> cut the optional video first. If needed, replace the Canvas practice quiz with the paper self-check. Protect the individual evaluation, one revision, and one combined submission of infographic plus evaluation.</p>",
                "RESOURCES": '<p><a href="https://www.bls.gov/ooh/life-physical-and-social-science/agricultural-and-food-science-technicians.htm">BLS Technicians</a> · <a href="https://www.bls.gov/ooh/life-physical-and-social-science/agricultural-and-food-scientists.htm">BLS Scientists</a> · <a href="https://www.bls.gov/ooh/architecture-and-engineering/agricultural-engineers.htm">BLS Engineers</a> · <a href="https://www.ars.usda.gov/oc/dof/farming-with-precision/">USDA Precision Agriculture</a> · <a href="https://www.nifa.usda.gov/about-nifa/impacts/automation-specialty-crops">USDA Automation for Specialty Crops</a></p>',
                "SUPPORT": "<p>Model one trend-to-task chain. Highlight specialty, parent occupation, measure/date, and limitation in four colors. The evaluation gives ten full writing lines for the 4-6 sentence response.</p>",
                "FALLBACK": "<p>The fixed guide replaces open searching and job boards. The video and quiz are optional support; the paper evaluation is the durable evidence.</p>",
            },
            5: {
                "TITLE": "Plant-Tech Evidence and Fair Career Investigation",
                "SUBTITLE": "50 minutes · TEKS d(1)(D)",
                "ALERT": "<strong>Use the fixed plant-tech evidence.</strong> No Xello lesson, profile screenshot, or platform catch-up is required.",
                "PREP": f'<ul><li><strong>Per student:</strong> the Day 4 evaluation and the {file_link(files["BIAS_REFLECT"]["id"], "one-page private reflection")} digitally; default print count is 0, with one copy per student only for the paper route.</li><li>Open the {file_link(files["EMERGING_GUIDE"]["id"], "Emerging Plant-Tech Evidence Guide")} and one complete assumption-to-evidence model.</li><li><strong>Grouping:</strong> individual/private work. Project the warm-up; do not require public sharing.</li></ul>',
                "EVIDENCE": "<p>One revised plant-tech evidence link plus a private career-assumption reflection using one fixed career fact and one fair investigation strategy. No public discussion.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and career assumptions warm-up", '''<p>Welcome students, seat them with their weekly materials, and project the career perceptions prompt.</p><ul><li>Ask students: <em>“When people hear the word 'agriculture,' many immediately picture an 1800s manual pitchfork or an open dirt field. Where do these outdated cultural stereotypes come from, and how do they prevent students from considering high-tech careers in plant robotics and genetics?”</em></li><li>Hear 2-3 student thoughts. Explain: <em>“Media representations often lag decades behind real industry practice. Today we reflect on how evidence-based career exploration dispels outdated assumptions.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-25 - Comprehensive Week 2 evidence audit and technical refinement", '''<p>Students reopen their Day 4 evaluations and the Emerging Plant-Tech Evidence Guide:</p><ul><li>Conduct a 4-point technical quality audit on their submitted evaluation:</li><li>1. <strong>Technology Precision:</strong> Does the writing name specific hardware/software (e.g., multispectral drone sensors, closed-loop nutrient dosers) rather than vague terms like 'computers'?</li><li>2. <strong>Work Task Fidelity:</strong> Is the described action an authentic daily job responsibility?</li><li>3. <strong>Statistical Labeling:</strong> Are 'May 2024', 'U.S.', and 'median' properly attached to every dollar figure?</li><li>4. <strong>Data Boundary:</strong> Does the text explicitly acknowledge the parent occupation relationship?</li><li>Students write one concrete sentence refinement directly on their evaluation sheet.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 15): Guide students to strengthen vague task sentences into actionable technical descriptions.</li></ul>''')
                    + flow("#1f617a", "Minutes 25-42 - Authoring the private Plant-Career Evidence Reflection", '''<p>Students complete their private reflection on Canvas (or the approved paper reflection sheet):</p><ul><li>Section 1: <strong>Outdated Assumption:</strong> Document ONE common societal or media misconception about agricultural and plant science careers.</li><li>Section 2: <strong>Verified Factual Counter-Evidence:</strong> Cite at least ONE verified technical fact, work condition, or labor market metric from Week 2 that disproves this misconception.</li><li>Section 3: <strong>Fair Investigation Strategy:</strong> Articulate a concrete personal strategy for fairly investigating future career fields before making premature judgments based on social media or peer opinions.</li><li>Privacy Invariant: Reflections remain individual and private; students are never required to disclose personal identities, family backgrounds, or private experiences.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 2 (Minute 34): Verify students cite concrete technical facts from the guide to counter their chosen misconception.</li></ul>''')
                    + flow("#e3ad19", "Minutes 42-47 - Finalizing portfolio evidence and revision check", '''<p>Students verify completion of all Week 2 portfolio components:</p><ul><li>1. Grow-system diagnosis and repair schematic (FYF pp. 89-90).</li><li>2. Farm-to-Table Infographic (Canva digital or paper original).</li><li>3. Emerging Plant-Tech Evaluation (scored with the 16-pt Major rubric).</li><li>4. Private Plant-Career Evidence Reflection.</li></ul>''')
                    + flow("#606c76", "Minutes 47-50 - Submit reflection and workspace close", '''<p>Confirm submission of the private Canvas reflection or collect paper reflection sheets.</p><ul><li>Congratulate students on completing their deep dive into Plant Science and Agricultural Technology!</li><li><strong>Safe Trim:</strong> Cut any whole-group share-out; protect the evidence audit, private reflection with factual counter-evidence, and portfolio verification.</li></ul>''')
                ),
                "MONITOR": "<p>Use a private Stop and Jot, then Active Monitor the evidence labels without reading personal opinions aloud. <strong>Minute 15 target:</strong> each student has identified one evidence link to strengthen. <strong>Minute 35 target:</strong> one assumption, one fixed career fact, and one fair investigation move are present. Protect privacy: students may write about general cultural or media assumptions and are never required to disclose identity or discrimination experiences.</p><p><strong>Safe trim:</strong> cut public sharing. Protect the evidence revision, private reflection, and submission.</p>",
                "RESOURCES": f'<p>{file_link(files["EMERGING_GUIDE"]["id"], "Emerging Plant-Tech Evidence Guide")} · {file_link(files["BIAS_REFLECT"]["id"], "Plant-Career Evidence Reflection")}</p>',
                "SUPPORT": "<p>Read prompts aloud, permit a private pass on discussion, and offer bilingual labels and teacher conference. The one-page reflection provides three separate response areas instead of one dense paragraph box.</p>",
                "FALLBACK": "<p>The fixed guide and paper or Canvas reflection are the complete routes. An absent student completes the same evidence revision.</p>",
            },
        }

        day_names = {
            1: "Diagnose a Grow System",
            2: "Plan a Farm-to-Table Infographic",
            3: "Build and Test the Infographic",
            4: "Evaluate Emerging Plant-Tech Work",
            5: "Plant-Tech Evidence and Fair Career Investigation",
        }
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_header(client, module["id"], header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 3SW Wk2 Day {day} - {day_names[day]}"
            student_page = await upsert_page(
                client,
                student_title,
                render(
                    "3sw-wk2-student.html",
                    {
                        "COURSE_ID": COURSE_ID,
                        "DAY": day,
                        **contracts[day],
                        **student[day],
                    },
                ),
            )
            teacher_title = f"TEACHER: 3SW Wk2 Day {day} Facilitator Guide"
            teacher_page = await upsert_page(
                client,
                teacher_title,
                render(
                    "3sw-wk2-teacher.html",
                    {
                        "COURSE_ID": COURSE_ID,
                        "DAY": day,
                        "STUDENT_PAGE_URL": student_page["url"],
                        **contracts[day],
                        **teacher[day],
                    },
                ),
            )
            await upsert_module_item(
                client, module["id"], "Page", teacher_page["url"], teacher_title
            )
            await upsert_module_item(
                client, module["id"], "Page", student_page["url"], student_title
            )
            pages[day] = {"teacher": teacher_page, "student": student_page}
            order += [
                ("Page", teacher_page["url"], teacher_title),
                ("Page", student_page["url"], student_title),
            ]
            if day == 1:
                await upsert_module_item(
                    client,
                    module["id"],
                    "Assignment",
                    career["id"],
                    CAREER_TITLE,
                )
                order.append(("Assignment", career["id"], CAREER_TITLE))
            if day == 3:
                await upsert_module_item(
                    client,
                    module["id"],
                    "Assignment",
                    transfer["id"],
                    TRANSFER_TITLE,
                )
                order.append(("Assignment", transfer["id"], TRANSFER_TITLE))
            if day == 4:
                await upsert_module_item(
                    client, module["id"], "Quiz", quiz["id"], QUIZ_TITLE
                )
                await upsert_module_item(
                    client, module["id"], "Assignment", packet["id"], PACKET_TITLE
                )
                order += [
                    ("Quiz", quiz["id"], QUIZ_TITLE),
                    ("Assignment", packet["id"], PACKET_TITLE),
                ]
            if day == 5:
                await upsert_module_item(
                    client,
                    module["id"],
                    "Assignment",
                    reflection["id"],
                    REFLECTION_TITLE,
                )
                order.append(("Assignment", reflection["id"], REFLECTION_TITLE))

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
                    if entry["id"] not in keep_ids and matches_item(entry, kind, key)
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
            item = next(entry for entry in items if matches_item(entry, kind, key))
            await api(
                client,
                "PUT",
                f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}",
                data={"module_item[position]": position, "module_item[title]": title},
            )

        final_items = sorted(
            await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items"),
            key=lambda entry: entry.get("position") or 0,
        )
        module = await api(
            client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}"
        )
        if module.get("published"):
            raise RuntimeError("3SW Wk2 module unexpectedly published")
        if quiz.get("published"):
            raise RuntimeError("3SW Wk2 practice quiz unexpectedly published")
        for label, assignment in (
            ("Major", packet),
            ("career", career),
            ("transfer", transfer),
            ("reflection", reflection),
        ):
            if assignment.get("published"):
                raise RuntimeError(f"3SW Wk2 {label} assignment unexpectedly published")
        published_pages = [
            value["url"]
            for pair in pages.values()
            for value in pair.values()
            if value.get("published")
        ]
        if published_pages:
            raise RuntimeError(f"Published 3SW Wk2 pages remain: {published_pages}")
        published_items = [
            entry.get("title") for entry in final_items if entry.get("published")
        ]
        if published_items:
            raise RuntimeError(f"Published 3SW Wk2 module items remain: {published_items}")
        if len(final_items) != len(order):
            raise RuntimeError(
                f"Expected {len(order)} 3SW Wk2 module items; found {len(final_items)}"
            )
        for position, ((kind, key, title), item) in enumerate(
            zip(order, final_items), start=1
        ):
            if (
                item.get("position") != position
                or item.get("title") != title
                or not matches_item(item, kind, key)
            ):
                raise RuntimeError(
                    f"3SW Wk2 module order mismatch at position {position}"
                )
        groups = await paged(client, f"/courses/{COURSE_ID}/assignment_groups")
        print(
            json.dumps(
                {
                    "module": {"id": module["id"], "published": module["published"]},
                    "quiz": {"id": quiz["id"], "published": quiz.get("published")},
                    "assignments": {
                        "packet": {
                            "id": packet["id"],
                            "published": packet.get("published"),
                            "grading_type": packet.get("grading_type"),
                            "omit_from_final_grade": packet.get(
                                "omit_from_final_grade"
                            ),
                        },
                        "career": {
                            "id": career["id"],
                            "published": career.get("published"),
                            "grading_type": career.get("grading_type"),
                            "omit_from_final_grade": career.get(
                                "omit_from_final_grade"
                            ),
                        },
                        "reflection": {
                            "id": reflection["id"],
                            "published": reflection.get("published"),
                            "grading_type": reflection.get("grading_type"),
                            "omit_from_final_grade": reflection.get(
                                "omit_from_final_grade"
                            ),
                        },
                        "transfer": {
                            "id": transfer["id"],
                            "published": transfer.get("published"),
                            "grading_type": transfer.get("grading_type"),
                            "omit_from_final_grade": transfer.get(
                                "omit_from_final_grade"
                            ),
                        },
                    },
                    "assignment_groups": [
                        {
                            "id": group["id"],
                            "name": group["name"],
                            "group_weight": group.get("group_weight"),
                        }
                        for group in groups
                    ],
                    "support_folder": {
                        "id": support_folder["id"],
                        "locked": support_folder["locked"],
                    },
                    "folders": {
                        str(day): {"id": folder["id"], "locked": folder["locked"]}
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
