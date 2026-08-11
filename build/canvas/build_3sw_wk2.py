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
MODULE_NAME = "3SW Wk2: Plant Science and Agricultural Communication"
QUIZ_TITLE = "PRACTICE: Emerging Plant-Tech Evidence Check"
PACKET_TITLE = "MAJOR 1: Farm-to-Table and Emerging Plant-Tech Evidence"
CAREER_TITLE = "PRACTICE: Plant Career Connection"
TRANSFER_TITLE = "FORMATIVE: Communication Skill Transfer"
REFLECTION_TITLE = "PRACTICE: Xello Biases Reflection"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/3sw/wk2"
XELLO = (
    ROOT / "cce-curriculum/resources/xello-licensed/lessons/biases-and-career-choices"
)


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
    unlocked = [
        entry.get("display_name") or entry.get("filename")
        for entry in final
        if not entry.get("locked")
    ]
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
    return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'


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
    matches = [entry for entry in assignments if entry.get("name") == REFLECTION_TITLE]
    if len(matches) > 1:
        raise RuntimeError(
            f"Expected at most one assignment named {REFLECTION_TITLE!r}; found {len(matches)}"
        )
    found = matches[0] if matches else None
    data = {
        "assignment[name]": REFLECTION_TITLE,
        "assignment[description]": "<p>Submit the private Xello Biases reflection as text or upload the supplied PDF. Do not post a public discussion or profile screenshot.</p>",
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
        files["XELLO_GUIDE"] = await upload(
            client, XELLO.parent / "biases-and-career-choices.pdf", support_path
        )
        files["XELLO_DECK"] = await upload(
            client, XELLO / "introduction-template.pptx", support_path
        )
        files["XELLO_TRAIL"] = await upload(
            client, XELLO / "career-trailblazers-student-instructions.pdf", support_path
        )
        files["XELLO_MATCH"] = await upload(
            client,
            XELLO / "non-traditional-career-matches-student-instructions.pdf",
            support_path,
        )

        folders, uploads = {}, {}
        for day in range(1, 6):
            folder_path = f"course files/CCR Materials/3SW/Wk2/Day {day} Visuals"
            folders[day], uploads[day] = await ensure_folder(client, folder_path), {}
            source = ASSETS / f"day{day}"
            if source.exists():
                for path in sorted(source.glob("*.png")):
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
        bias_warmup = image_tag(
            uploads[5]["xello-biases-warm-up.png"]["id"],
            "Xello Biases and career choices warm-up questions",
            720,
        )
        bias_navigation = image_tag(
            uploads[5]["xello-biases-navigation.png"]["id"],
            "Xello lesson navigation from the student dashboard",
            720,
        )
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
                "TOPIC": "Career Bias",
                "OBJECTIVE": "Students will revisit an assumption about emerging or nontraditional career work and evaluate it with one career fact.",
                "TEKS": "d(1)(D)",
                "DOL": "Xello Completion Standards record plus a private assumption-evidence-action reflection.",
                "STUDENT_OBJECTIVE": "use evidence to test a career assumption before ruling a career in or out.",
                "STUDENT_DOL": "complete the Xello lesson and submit a private reflection with one assumption, one career fact, and one fair next action.",
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
                    grow_pages[1]
                    + f'<p>Compare technician, scientist, and engineer duties and typical entry routes. Choose the role most likely to test the system first.</p><p><a href="{career_url}">Open the private Plant Career Connection check</a>. Submit only your chosen role, one accurate duty, and one preparation fact.</p><p><strong>Career frame:</strong> "A [role] would [duty]. A typical entry route is [preparation]."</p>',
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
                "FALLBACK": "<p>The embedded licensed pages and fixed career guide are the complete route. A plain-paper system sketch is equal to chart paper. If Canvas is unavailable, draft the three career details in the FYF margin and transfer only those details to the private check at the next access point.</p>",
            },
            2: {
                "TITLE": "Plan a Farm-to-Table Infographic",
                "PURPOSE": "Turn a fictional client's brief into a clear message for grocery shoppers.",
                "TODAY": "<ul><li>identify the Agricultural Communications Specialist role;</li><li>read the client requirements;</li><li>plan four process steps;</li><li>make a full-page sketch.</li></ul>",
                "READY": f'<p>Open {file_link(files["PLANNER"]["id"], "the two-page Farm-to-Table Planner")} and {file_link(files["RUBRIC"]["id"], "the student-visible 16-point rubric")}. Use FYF p. 92 for the two interview questions.</p>',
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
                "READY": f'<p>Keep {file_link(files["PLANNER"]["id"], "your planner")} and {file_link(files["RUBRIC"]["id"], "the rubric")} visible.</p>',
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
                "READY": f'<p>Open {file_link(files["EMERGING_GUIDE"]["id"], "the Emerging Plant-Tech Evidence Guide")} and {file_link(files["EMERGING_EVAL"]["id"], "the two-page evaluation")}.</p>',
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
                "TITLE": "Xello Biases and Career Choices",
                "PURPOSE": "Complete the required Xello lesson and test one career assumption with evidence.",
                "TODAY": "<ul><li>complete Biases and career choices in Xello;</li><li>revisit one assumption privately;</li><li>choose a fair way to investigate a career.</li></ul>",
                "READY": f'<p>Open {file_link(files["BIAS_REFLECT"]["id"], "the private reflection")}. Keep personal identity and experiences private unless you choose to share them.</p>',
                "MEDIA": "",
                "STEPS": step(
                    1,
                    "Warm up",
                    bias_warmup
                    + "<p>Think privately: Where do people learn assumptions about careers? You may pass on public sharing.</p>",
                )
                + step(
                    2,
                    "Complete the assigned lesson",
                    bias_navigation
                    + "<p>ClassLink &gt; Xello &gt; Home &gt; Lessons &gt; Biases and career choices. Use the full 30-minute block.</p>",
                )
                + step(
                    3,
                    "Test an assumption with evidence",
                    '<p>Use one Plant-Tech Guide fact or one Xello career-profile fact. You do not need to disclose a protected identity or personal experience.</p><p><strong>Complete frame:</strong> "People may assume [idea]. The fact [evidence] challenges or complicates that idea because [reason]."</p>',
                )
                + step(
                    4,
                    "Submit privately",
                    f'<p>Complete the PDF or <a href="{reflection_url}">open the private Canvas assignment</a>. Do not use a public discussion or profile screenshot.</p>',
                ),
                "EXIT": "<p>What is one fair action, such as reading a profile, taking a course, interviewing a worker, or job shadowing, that can test an assumption before you rule a career out?</p>",
                "DONE": "<ul><li>Xello lesson completed or catch-up recorded;</li><li>one assumption named without forced disclosure;</li><li>one career fact used;</li><li>one fair next action explained;</li><li>private submission complete.</li></ul>",
                "VISIBLE_SUPPORT": '<p><strong>Word bank:</strong> bias = sesgo · assumption = suposición · challenge = cuestionar · evidence = evidencia.</p><p><strong>Frame:</strong> "People may assume [idea]. The fact [evidence] challenges or complicates that idea because [reason]."</p>',
                "SUPPORT": "<p>A teacher may read prompts aloud and conference privately. Students may use an assumption from media or general culture instead of personal disclosure.</p>",
                "FALLBACK": "<p>If Xello fails, complete the private reflection with the Plant-Tech Guide and move the required lesson to supervised catch-up. Paper does not count as Xello completion.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Diagnose a Grow System",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(2)(A)",
                "ALERT": "<strong>Do not turn Day 1 into an open H&amp;L search.</strong> The fixed career guide and licensed workbook carry the lesson with no login or live-data verification burden.",
                "PREP": f'<ul><li><strong>Per student:</strong> FYF workbook pp. 88-90 and pencil. Keep one sheet of plain paper per student available only if the workbook sketch space is not usable.</li><li><strong>Devices:</strong> one per student or one per pair for {file_link(files["CAREERS"]["id"], "the career guide")}; default print count is 0. Print one guide per pair only for a no-device class.</li><li>Open the unpublished private <strong>{CAREER_TITLE}</strong> assignment. It accepts one individual Canvas text response and remains 0-point, not graded, and omitted from the final grade.</li><li><strong>Grouping:</strong> individual evidence; optional pairs for the warm-up and clue comparison.</li><li>Model one two-clue diagnosis without giving the final priority.</li></ul>',
                "EVIDENCE": "<p><strong>FYF pp. 89-90:</strong> first-repair decision supported by two clues and one labeled system improvement. <strong>Private Canvas practice check:</strong> one chosen role, one accurate duty, and one preparation fact. Do not make students copy the grow-system response into Canvas.</p>",
                "FLOW": flow(
                    "#5a2d91", "System warm-up · 5", "What must reach every plant?"
                )
                + flow(
                    "#4a9d2f",
                    "Career evidence · 8",
                    "Submit one role, duty, and preparation fact privately.",
                )
                + flow(
                    "#1f617a",
                    "Investigate and diagnose · 20",
                    "Read every clue before choosing.",
                )
                + flow(
                    "#e3ad19",
                    "Prioritize and sketch · 12",
                    "First repair plus prevention feature.",
                )
                + flow(
                    "#1f617a",
                    "Verify and reset · 5",
                    "Check the two evidence homes and return materials.",
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
                "FLOW": flow(
                    "#5a2d91", "Food-journey warm-up · 5", "Name four likely stages."
                )
                + flow(
                    "#4a9d2f",
                    "Client brief · 8",
                    "Role, audience, crop choices, required content.",
                )
                + flow("#1f617a", "Content plan · 20", "Four steps and two facts.")
                + flow(
                    "#e3ad19",
                    "Full-page sketch · 12",
                    "Reading order, visuals, labels.",
                )
                + flow(
                    "#1f617a", "Exit · 5", "Role, product, audience, and reader path."
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
                "FLOW": flow(
                    "#5a2d91", "Plan check · 5", "Four steps, two facts, reader path."
                )
                + flow(
                    "#4a9d2f",
                    "Model and criteria · 8",
                    "Readable, accurate, source-safe.",
                )
                + flow("#1f617a", "Build · 25", "Digital or paper route.")
                + flow(
                    "#e3ad19",
                    "Reader test and revise · 7",
                    "First look plus one unclear spot.",
                )
                + flow(
                    "#1f617a",
                    "Save and transfer · 5",
                    "Save the artifact; submit only the private two-career comparison.",
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
                "FLOW": flow(
                    "#5a2d91",
                    "Optional BLS hook · 4",
                    "Agricultural engineering tasks.",
                )
                + flow(
                    "#4a9d2f",
                    "Parent/specialty model · 8",
                    "What a proxy can and cannot show.",
                )
                + flow(
                    "#1f617a",
                    "Read the fixed guide · 10",
                    "Three specialties, three routes.",
                )
                + flow(
                    "#e3ad19",
                    "Individual evaluation · 20",
                    "Technology, task, two facts, limit.",
                )
                + flow("#4a9d2f", "Practice quiz · 5", "Retry and revise.")
                + flow(
                    "#1f617a",
                    "Submit · 3",
                    "Submit the saved infographic and evaluation together once.",
                ),
                "MONITOR": "<p><strong>District moves:</strong> chunk the evaluation into technology → task → two dated facts → limit, then Active Monitor each link. <strong>Minute 16 target:</strong> students have a specialty, parent occupation, and technology-to-task chain. If students call the parent median a local starting salary, stop and model the complete limit frame. <strong>Minute 36 target:</strong> 4–6 sentences contain two dated facts and one data limit. Key facts: technician parent = $48,480/5%; soil and plant scientist = $71,410/5%; agricultural engineer = $84,630/6%. All are May 2024 U.S. medians/outlook 2024–34. The figure belongs to the parent occupation and cannot prove an exact specialty's local starting pay.</p><p><strong>Safe trim:</strong> cut the optional video first. If needed, replace the Canvas practice quiz with the paper self-check. Protect the individual evaluation, one revision, and one combined submission of infographic plus evaluation.</p>",
                "RESOURCES": '<p><a href="https://www.bls.gov/ooh/life-physical-and-social-science/agricultural-and-food-science-technicians.htm">BLS Technicians</a> · <a href="https://www.bls.gov/ooh/life-physical-and-social-science/agricultural-and-food-scientists.htm">BLS Scientists</a> · <a href="https://www.bls.gov/ooh/architecture-and-engineering/agricultural-engineers.htm">BLS Engineers</a> · <a href="https://www.ars.usda.gov/oc/dof/farming-with-precision/">USDA Precision Agriculture</a> · <a href="https://www.nifa.usda.gov/about-nifa/impacts/automation-specialty-crops">USDA Automation for Specialty Crops</a></p>',
                "SUPPORT": "<p>Model one trend-to-task chain. Highlight specialty, parent occupation, measure/date, and limitation in four colors. The evaluation gives ten full writing lines for the 4-6 sentence response.</p>",
                "FALLBACK": "<p>The fixed guide replaces open searching and job boards. The video and quiz are optional support; the paper evaluation is the durable evidence.</p>",
            },
            5: {
                "TITLE": "Xello Biases and Career Choices",
                "SUBTITLE": "50 minutes · TEKS d(1)(D)",
                "ALERT": "<strong>Required Grade 8 task: Biases and career choices, 30 minutes.</strong> Do not repeat Work experiences. The licensed 80-minute facilitator package is an extended sequence; only Activity 2 is the district completion task today.",
                "PREP": f'<ul><li><strong>Per student:</strong> one district device and headphones if the Xello lesson uses audio. Post the {file_link(files["BIAS_REFLECT"]["id"], "one-page private reflection")} digitally; default print count is 0, with one copy per student only for the paper route.</li><li>Check the Xello Completion Standards report and test ClassLink. Open the {file_link(files["XELLO_GUIDE"]["id"], "official 80-minute facilitator guide")} for teacher background, but use only Activity 2 today.</li><li>The {file_link(files["XELLO_TRAIL"]["id"], "Career Trailblazers")} and {file_link(files["XELLO_MATCH"]["id"], "Non-traditional Career Matches")} handouts are optional extensions, not required prep.</li><li><strong>Grouping:</strong> individual/private work. Project the warm-up and navigation; do not require public sharing.</li></ul>',
                "EVIDENCE": "<p>Xello Completion Standards report plus a private career-assumption reflection using one career fact and one fair investigation strategy. No public discussion or profile screenshot.</p>",
                "FLOW": flow(
                    "#5a2d91",
                    "Private warm-up · 5",
                    "Where do career assumptions come from?",
                )
                + flow(
                    "#4a9d2f",
                    "Xello lesson · 30",
                    "Home > Lessons > Biases and career choices.",
                )
                + flow(
                    "#1f617a",
                    "Private reflection · 12",
                    "Assumption, career fact, fair next move.",
                )
                + flow(
                    "#e3ad19",
                    "Report/catch-up · 3",
                    "Verify or schedule supervised completion.",
                ),
                "MONITOR": "<p><strong>Curriculum note:</strong> d(1)(D) is reinforcement through the private evidence check; Xello is the completion-standard carrier. Activity 2 has no prerequisite. The extended Activity 3 recommends Matchmaker and asks students to revisit a discounted career; it is not today's minimum. <strong>District move:</strong> use a private Stop and Jot, then Active Monitor navigation without reading student answers. <strong>Minute 8 target:</strong> every student is in Biases and career choices or has a named access barrier. If several students remain on Home, pause for one ClassLink/navigation reset. <strong>Minute 35 target:</strong> lesson completion or supervised catch-up is recorded. Protect privacy: students may write about general cultural or media assumptions and are never required to disclose identity or discrimination experiences.</p><p><strong>Safe trim:</strong> cut public sharing and optional extensions. Protect the 30-minute Xello lesson, report/catch-up record, and private reflection.</p>",
                "RESOURCES": f'<p>{file_link(files["XELLO_DECK"]["id"], "Original seven-slide Xello template")} · {file_link(files["XELLO_GUIDE"]["id"], "Full licensed facilitator package")}. The original template is stored for teacher reference, but its Google sign-in slide does not match Irving ClassLink and its first exit question is unrelated to today\'s task. Do not project slides 5 or 7. The Canvas Student Guide supplies the corrected launch and exit.</p>',
                "SUPPORT": "<p>Read prompts aloud, permit a private pass on discussion, and offer bilingual labels and teacher conference. The one-page reflection provides three separate response areas instead of one dense paragraph box.</p>",
                "FALLBACK": "<p>If Xello fails, students use the fixed Plant-Tech Guide for the private reflection and complete Xello in supervised catch-up. Paper does not count as platform completion.</p>",
            },
        }

        day_names = {
            1: "Diagnose a Grow System",
            2: "Plan a Farm-to-Table Infographic",
            3: "Build and Test the Infographic",
            4: "Evaluate Emerging Plant-Tech Work",
            5: "Xello Biases and Career Choices",
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
