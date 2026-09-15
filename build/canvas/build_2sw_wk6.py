"""Build the unpublished 2SW Week 6 biomedical module and interactions."""

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
    1: "https://docs.google.com/document/d/1ZGGB2aOAcmUUHjtX69COLVL_eT9pu089Wsr5O-24nko/copy",
    2: "https://docs.google.com/document/d/1ywixqoEL8s163zMPjp6K8AHun4WlQ6oB7lE8gFUybNI/copy",
    3: "https://docs.google.com/document/d/15lXbU9bX39sGlMVAahwdxWUPTBvWNZKwo94flpvqLzY/copy",
    4: "https://docs.google.com/document/d/1aj5j7tPX3VRtyzhGvMqeR3SFU7oE7jsqJI535hqIJlA/copy",
    5: "https://docs.google.com/document/d/1hhU2CBtX2Q1m0lJ5BCkl5ZHgKAY2jOoCtkaFOJvaLeo/copy",
}


# One Google Doc per worksheet (build/google_docs/student_worksheet_docs.json).
# Keyed by (day, anchor label) so a worksheet button never opens the day's exit ticket.
STUDENT_WORKSHEET_COPY_URLS = {
    (1, 'the Cover Letter Lab'): "https://docs.google.com/document/d/1kbvKfdgCuP6C682Etfc9_3K4hLRQlFxTM8q1pqzrUiY/copy",
    (2, 'the optional expanded design record'): "https://docs.google.com/document/d/1UEXN0pkcE3HucvzSlYRBbu4wmjPwx7KiP0vGXHCXiz0/copy",
    (3, 'the optional expanded investigation record'): "https://docs.google.com/document/d/1316fVWZkJY7j0QQZc_H6wWQkVmI_JSvtiXyYfxHQwLo/copy",
    (4, 'the optional expanded response plan'): "https://docs.google.com/document/d/16JL29owdyoFQpNw11bJXvbGlQ3xmjJSlmjQyfcxQTaw/copy",
    (5, 'the optional one-page paper response'): "https://docs.google.com/document/d/1B-u3xDcvptqNrcsmkIlGljiAyokwpjl_7AIE2gM1N1M/copy",
}


def student_copy_link(day, label):
    url = STUDENT_WORKSHEET_COPY_URLS.get((day, label), STUDENT_GOOGLE_COPY_URLS[day])
    return f'<a href="{url}">{label}</a>'

MODULE_NAME = "2SW Wk6: Science Meets Medicine"
QUIZ_TITLE = "PRACTICE: Outbreak Evidence Check"
ASSIGNMENT_TITLE = "PRACTICE: Biomedical Career Evidence Reflection"
LEGACY_ASSIGNMENT_TITLE = "PRACTICE: " + "Explore Career " + "Matches Reflection"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/2sw/wk6"


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower().replace("&", "and")).strip("-")


async def api(client, method, path, **kwargs):
    response = await client.request(method, f"{BASE}/api/v1{path}", **kwargs)
    response.raise_for_status()
    return response.json() if response.content else None


async def paged(client, path, params=None):
    output = []
    url = f"{BASE}/api/v1{path}"
    query = {"per_page": 100, **(params or {})}
    while url:
        response = await client.get(url, params=query)
        response.raise_for_status()
        output += response.json()
        url = response.links.get("next", {}).get("url")
        query = None
    return output


async def ensure_module(client):
    modules = await paged(client, f"/courses/{COURSE_ID}/modules")
    found = next((module for module in modules if module["name"] == MODULE_NAME), None)
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
    current = ""
    folder = None
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
    record = await api(
        client, "PUT", f"/files/{response.json()['id']}", data={"locked": "true"}
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
            await api(client, "PUT", f"/files/{entry['id']}", data={"locked": "true"})
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


async def upsert_page(client, title, body, url):
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


async def upsert_page_item(client, module_id, page, title):
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    item = next(
        (entry for entry in items if entry.get("page_url") == page["url"]), None
    )
    if item:
        return await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            data={"module_item[title]": title},
        )
    return await api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/modules/{module_id}/items",
        data={
            "module_item[type]": "Page",
            "module_item[page_url]": page["url"],
            "module_item[title]": title,
        },
    )


async def upsert_subheader(client, module_id, title):
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    item = next(
        (
            entry
            for entry in items
            if entry.get("type") == "SubHeader" and entry.get("title") == title
        ),
        None,
    )
    if item:
        return await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            data={"module_item[title]": title, "module_item[indent]": "0"},
        )
    return await api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/modules/{module_id}/items",
        data={
            "module_item[type]": "SubHeader",
            "module_item[title]": title,
            "module_item[indent]": "0",
        },
    )


def file_link(file_id, label):
    return f'<a href="/courses/{COURSE_ID}/files/{file_id}/preview" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">{label}</a>'


def image_tag(file_id, alt, max_width=760):
    return f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" style="display:block;width:100%;max-width:{max_width}px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'


def step(number, title, body, color="#5a2d91"):
    return f'<h3 style="color:{color};border-bottom:3px solid #d9c9ed">{number}. {title}</h3>{body}'


def flow(color, title, text):
    return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0 0 6px;color:{color}">{title}</h4>{text}</div>'


QUIZ_QUESTIONS = [
    {
        "name": "Q1 - Comparison group",
        "text": "Which Fairview Edge evidence gives the strongest comparison group?",
        "correct": "Two residents drank bottled water and did not get sick.",
        "wrong": [
            "One resident played soccer.",
            "One resident is 52 years old.",
            "The town has about 2,000 residents.",
        ],
        "correct_comment": "Correct. Comparing exposed and unexposed residents strengthens the working claim.",
        "incorrect_comment": "Look for evidence that compares exposure and outcome, not a detail that applies to only one person.",
    },
    {
        "name": "Q2 - Claim boundary",
        "text": "What is the strongest conclusion the class can make before water testing?",
        "correct": "Tap-water exposure after flooding is a supported working hypothesis that still needs testing.",
        "wrong": [
            "The tap water is proven to be the cause.",
            "Every resident will become sick.",
            "River swimming caused every case.",
        ],
        "correct_comment": "Correct. The pattern supports a hypothesis, not final proof.",
        "incorrect_comment": "The case supports a working claim, but confirming tests are still required.",
    },
    {
        "name": "Q3 - Immediate versus prevention",
        "text": "Which choice is a prevention step rather than an immediate action?",
        "correct": "Protect the water source from future flooding.",
        "wrong": [
            "Provide safe drinking water during the current event.",
            "Tell residents the current approved safety directions.",
            "Collect water samples today.",
        ],
        "correct_comment": "Correct. Prevention changes the system before the next event.",
        "incorrect_comment": "Immediate actions address the current event. Prevention reduces the chance of a future event.",
    },
    {
        "name": "Q4 - Real event boundary",
        "text": "A real local water warning appears during class. What should students do?",
        "correct": "Follow current local officials, district directions, and a trusted adult.",
        "wrong": [
            "Use the fictional worksheet as official guidance.",
            "Write their own public-health instructions.",
            "Wait for classmates to vote on the best action.",
        ],
        "correct_comment": "Correct. The classroom case is not official guidance.",
        "incorrect_comment": "A real event requires current official directions, not a classroom simulation.",
    },
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
    quiz = next((entry for entry in quizzes if entry.get("title") == QUIZ_TITLE), None)
    data = {
        "quiz[title]": QUIZ_TITLE,
        "quiz[description]": "<p>Ungraded practice. Retry and use the feedback before writing the response plan.</p>",
        "quiz[quiz_type]": "practice_quiz",
        "quiz[published]": "false",
        "quiz[allowed_attempts]": "-1",
        "quiz[show_correct_answers]": "true",
        "quiz[shuffle_answers]": "false",
    }
    quiz = await api(
        client,
        "PUT" if quiz else "POST",
        f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        if quiz
        else f"/courses/{COURSE_ID}/quizzes",
        data=data,
    )
    expected = [spec["name"] for spec in QUIZ_QUESTIONS]
    existing = await prepare_quiz_questions(client, quiz["id"], set(expected))
    for position, spec in enumerate(QUIZ_QUESTIONS, start=1):
        found = next(
            (
                question
                for question in existing
                if question.get("question_name") == spec["name"]
            ),
            None,
        )
        answers = [{"answer_text": spec["correct"], "answer_weight": 100}] + [
            {"answer_text": value, "answer_weight": 0} for value in spec["wrong"]
        ]
        payload = {
            "question": {
                "question_name": spec["name"],
                "question_text": spec["text"],
                "question_type": "multiple_choice_question",
                "position": position,
                "points_possible": 1,
                "correct_comments": spec["correct_comment"],
                "incorrect_comments": spec["incorrect_comment"],
                "answers": answers,
            }
        }
        await api(
            client,
            "PUT" if found else "POST",
            f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{found['id']}"
            if found
            else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions",
            json=payload,
        )
    await finalize_quiz_order(client, quiz["id"], expected)
    return await api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


async def upsert_quiz_item(client, module_id, quiz):
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    item = next(
        (
            entry
            for entry in items
            if entry.get("type") == "Quiz" and entry.get("content_id") == quiz["id"]
        ),
        None,
    )
    if item:
        return await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            data={"module_item[title]": QUIZ_TITLE},
        )
    return await api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/modules/{module_id}/items",
        data={
            "module_item[type]": "Quiz",
            "module_item[content_id]": quiz["id"],
            "module_item[title]": QUIZ_TITLE,
        },
    )


async def upsert_assignment(client):
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    found = next(
        (
            entry
            for entry in assignments
            if entry.get("name") in {ASSIGNMENT_TITLE, LEGACY_ASSIGNMENT_TITLE}
        ),
        None,
    )
    data = {
        "assignment[name]": ASSIGNMENT_TITLE,
        "assignment[description]": """<div style="max-width:820px;margin:0 auto;font-family:Arial,Helvetica,sans-serif;line-height:1.5;color:#24323d"><h2 style="color:#5a2d91">Biomedical Career Evidence Reflection</h2><div style="border:1px solid #bad4df;border-radius:9px;background:#f2f8fb;padding:14px 18px"><p><strong>Topic:</strong> Biomedical Career Evidence</p><p><strong>I can:</strong> Compare three fixed biomedical careers and support one recommendation with a task, preparation fact, and source-labeled career fact.</p><p><strong>Show my learning:</strong> Submit a private evidence-based recommendation.</p></div><h3>Respond privately</h3><ol><li>Name one biomedical career to keep exploring.</li><li>Use one central task and one preparation fact.</li><li>Use one pay, outlook, or annual-openings fact with its source labels.</li><li>Name one tradeoff and one question to verify next.</li></ol><p>Type the response or upload the supplied one-page paper response.</p></div>""",
        "assignment[submission_types][]": ["online_text_entry", "online_upload"],
        "assignment[grading_type]": "not_graded",
        "assignment[points_possible]": "0",
        "assignment[omit_from_final_grade]": "true",
        "assignment[published]": "false",
    }
    if found:
        assignment = await api(
            client, "PUT", f"/courses/{COURSE_ID}/assignments/{found['id']}", data=data
        )
    else:
        assignment = await api(
            client, "POST", f"/courses/{COURSE_ID}/assignments", data=data
        )
    if (
        assignment.get("published")
        or float(assignment.get("points_possible") or 0) != 0
        or assignment.get("grading_type") != "not_graded"
        or not assignment.get("omit_from_final_grade")
    ):
        raise RuntimeError(
            "Formative reflection invariant failed after update: "
            f"published={assignment.get('published')}, "
            f"points={assignment.get('points_possible')}, "
            f"grading={assignment.get('grading_type')}, "
            f"omit={assignment.get('omit_from_final_grade')}"
        )
    return assignment


async def upsert_assignment_item(client, module_id, assignment):
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    item = next(
        (
            entry
            for entry in items
            if entry.get("type") == "Assignment"
            and entry.get("content_id") == assignment["id"]
        ),
        None,
    )
    if item:
        return await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            data={"module_item[title]": ASSIGNMENT_TITLE},
        )
    return await api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/modules/{module_id}/items",
        data={
            "module_item[type]": "Assignment",
            "module_item[content_id]": assignment["id"],
            "module_item[title]": ASSIGNMENT_TITLE,
        },
    )


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as client:
        module = await ensure_module(client)
        quiz = await upsert_quiz(client)
        assignment = await upsert_assignment(client)

        support_path = "course files/CCR Materials/2SW/Wk6"
        support_folder = await ensure_folder(client, support_path)
        worksheet_names = {
            "CAREERS": "2sw-wk6-biomedical-career-evidence-guide.pdf",
            "LETTER": "2sw-wk6-cover-letter-lab.pdf",
            "MEDICS": "2sw-wk6-mini-medics-design-record.pdf",
            "INVESTIGATE": "2sw-wk6-outbreak-investigation-record.pdf",
            "RESPONSE": "2sw-wk6-outbreak-response-plan.pdf",
            "REFLECT": "2sw-wk6-xello-career-matches-reflection.pdf",
        }
        files = {
            key: await upload(
                client, ROOT / "docs/resources/worksheets" / name, support_path
            )
            for key, name in worksheet_names.items()
        }
        uploads = {}
        folders = {}
        for day in range(1, 6):
            folder_path = f"course files/CCR Materials/2SW/Wk6/Day {day} Visuals"
            folders[day] = await ensure_folder(client, folder_path)
            uploads[day] = {}
            source = ASSETS / f"day{day}"
            if source.exists():
                for path in sorted(source.glob("*.png")):
                    uploads[day][path.name] = await upload(client, path, folder_path)

        support_folder = await lock_folder_files(client, support_folder)
        for day, folder in folders.items():
            folders[day] = await lock_folder_files(client, folder)

        quiz_url = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        assignment_url = f"/courses/{COURSE_ID}/assignments/{assignment['id']}"
        student = {
            1: {
                "TITLE": "Compare Biomedical Careers and Write for a Job",
                "PURPOSE": "Use one dated evidence set and answer a fictional job posting with honest evidence.",
                "TOPIC": "Biomedical Careers",
                "I_CAN": "I can compare three biomedical careers and write a practice cover letter that answers one employer need with honest evidence.",
                "SHOW_LEARNING": "Complete the career comparison and five-part practice cover letter.",
                "TODAY": "<ul><li>compare three biomedical careers;</li><li>read a fictional Student Lab Helper posting;</li><li>write a five-part practice cover letter.</li></ul>",
                "READY": f"<p>Open {file_link(files['CAREERS']['id'], 'the Biomedical Career Evidence Guide')} and {student_copy_link(1, 'the Cover Letter Lab')}.</p>",
                "MEDIA": "",
                "STEPS": step(
                    1,
                    "Compare the evidence",
                    "<p>Find the highest median, fastest growth, and most annual openings. Write why the answers differ.</p>",
                )
                + step(
                    2,
                    "Choose one career",
                    "<p>Record a daily-work reason, education trade-off, and dated labor-market fact.</p>",
                )
                + step(
                    3,
                    "Read the fictional posting",
                    "<p>Mark two employer needs and one responsibility. Do not submit the letter to a real employer.</p>",
                )
                + step(
                    4,
                    "Draft all five parts",
                    "<p>Greeting, opening, evidence-based body, closing, and sign-off. Underline the employer need once and your true evidence twice.</p><div style=\"border-left:5px solid #1f617a;background:#f2f8fb;padding:10px 14px;margin:12px 0\"><strong>Use while drafting:</strong> employer/empleador · need/necesidad · evidence/evidencia · reliable/confiable<br><strong>Complete thought:</strong> The posting asks for _____. I practiced this when _____. This would help the lab because _____.</div>",
                ),
                "EXIT": "<p>Imani has no paid work experience. She organized Science Olympiad supplies and checked a measurement table. Name one posting need she can answer, then write one honest need-to-evidence sentence.</p>",
                "DONE": "<ul><li>three career measures compared correctly;</li><li>one source and date recorded;</li><li>all five letter parts complete;</li><li>no invented credential, job, or private detail.</li></ul>",
                "SUPPORT": "<p>median = mediana · outlook = perspectiva · employer = empleador · evidence = evidencia. Frame: “The posting asks for ____. I practiced this when ____.”</p>",
                "FALLBACK": "<p>Both PDFs contain the complete lesson. No web search, H&amp;L login, or partner is required.</p>",
            },
            2: {
                "TITLE": "Design a Mini Medic",
                "PURPOSE": "Build a future-technology concept that meets a mission and names the evidence it would still need.",
                "TOPIC": "Biomedical Design",
                "I_CAN": "I can use the FYF future-technology scenario to plan, label, and explain a tiny medical robot and name a career connected to the work.",
                "SHOW_LEARNING": "Complete FYF pp. 80-81, one evidence question, and one biomedical-career connection.",
                "TODAY": "<ul><li>read the four mission checks;</li><li>plan, draw, and label a design;</li><li>map its journey and name one safety question.</li></ul>",
                "READY": f"<p>Open your workbook to FYF pp. 79-81. Use {student_copy_link(2, 'the optional expanded design record')} only when your teacher assigns the no-workbook or extended route. Get paper and a pencil or marker.</p>",
                "MEDIA": image_tag(
                    uploads[2]["fyf-p79-mini-medics.png"]["id"],
                    "Find Your Future Mini Medics mission and design requirements",
                    650,
                ),
                "STEPS": step(
                    1,
                    "Plan before drawing",
                    image_tag(
                        uploads[2]["fyf-p80-mini-medics.png"]["id"],
                        "Find Your Future Mini Medics planning fields",
                        650,
                    )
                    + "<p>Name the size, guidance, three tools, vessel protection, and completion signal.</p>",
                )
                + step(
                    2,
                    "Draw and label",
                    image_tag(
                        uploads[2]["fyf-p81-mini-medics.png"]["id"],
                        "Find Your Future drawing, journey, and discussion directions",
                        650,
                    )
                    + "<p>Every label needs a purpose. Artistic skill is not the goal.</p>",
                )
                + step(
                    3,
                    "Map the journey",
                    "<p>Explain enter, travel, act, and finish.</p>",
                )
                + step(
                    4,
                    "Name the missing evidence",
                    "<p>Write what a medical researcher would need before testing the idea further.</p><div style=\"border-left:5px solid #1f617a;background:#f2f8fb;padding:10px 14px;margin:12px 0\"><strong>Use while explaining:</strong> clot/coágulo · vessel/vaso · guide/guiar · signal/señal · evidence/evidencia<br><strong>Complete thought:</strong> The _____ feature helps the design _____, but researchers still need evidence about _____ before testing.</div>",
                )
                + step(
                    5,
                    "Connect the work to a career",
                    "<p>Name one biomedical worker who would design, test, or operate part of this system and state the work product.</p>",
                ),
                "EXIT": "<p>A smaller design may fit, but does that prove it is safe? Explain which control or vessel-damage evidence is still needed.</p>",
                "DONE": "<ul><li>size comparison and three tools;</li><li>guidance, vessel protection, and signal;</li><li>four-part journey;</li><li>one research evidence need;</li><li>one career and work product.</li></ul>",
                "SUPPORT": "<p>clot = coágulo · vessel = vaso · guide = guiar · signal = señal. You may label a teacher-provided outline.</p>",
                "FALLBACK": "<p>Use the embedded pages and PDF. Plain paper is equal to chart paper. You may work independently.</p>",
            },
            3: {
                "TITLE": "Follow the Outbreak Evidence",
                "PURPOSE": "Compare exposure and outcome, write a supported claim, and name what still needs testing.",
                "TOPIC": "Outbreak Evidence",
                "I_CAN": "I can use the FYF case to explain how an epidemiologist compares evidence, writes a working claim, and identifies what still needs testing.",
                "SHOW_LEARNING": "Complete FYF pp. 75-76 and one epidemiologist work-product sentence.",
                "TODAY": "<ul><li>read the fictional Fairview Edge case;</li><li>compare sick and healthy residents;</li><li>support one working claim with at least three clues.</li></ul>",
                "READY": f"<p>Open your workbook to FYF pp. 74-76. Use {student_copy_link(3, 'the optional expanded investigation record')} only when your teacher assigns the no-workbook or extended route.</p><p><strong>Real-event boundary:</strong> In a real health or water emergency, follow local officials and a trusted adult.</p>",
                "MEDIA": image_tag(
                    uploads[3]["fyf-p74-outbreak.png"]["id"],
                    "Find Your Future fictional Fairview Edge resident case table",
                    650,
                )
                + image_tag(
                    uploads[3]["fyf-p75-outbreak.png"]["id"],
                    "Find Your Future environmental clues and investigation-report prompts",
                    650,
                ),
                "STEPS": step(
                    1,
                    "Compare exposure and outcome",
                    "<p>Include residents who became sick and residents who stayed healthy.</p>",
                )
                + step(
                    2,
                    "Write the report",
                    "<p>Record cases, symptoms, timing, three clues, likely source, and a because statement.</p><div style=\"border-left:5px solid #1f617a;background:#f2f8fb;padding:10px 14px;margin:12px 0\"><strong>Use while comparing:</strong> outbreak/brote · exposure/exposición · outcome/resultado · source/fuente · hypothesis/hipótesis<br><strong>Complete thought:</strong> Sick residents mostly _____, while residents who stayed healthy _____. The evidence suggests _____ because _____. It does not yet prove _____.</div>",
                )
                + step(
                    3,
                    "Analyze the pattern",
                    image_tag(
                        uploads[3]["fyf-p76-outbreak.png"]["id"],
                        "Find Your Future outbreak pattern, severity, and risk prompts",
                        650,
                    )
                    + "<p>Separate what the case supports from what still needs testing.</p>",
                )
                + step(
                    4,
                    "Use the feedback check",
                    f'<p><a href="{quiz_url}">Open the Outbreak Evidence Check</a>. Retry and read the feedback.</p>',
                )
                + step(
                    5,
                    "Name the career work product",
                    "<p>An epidemiologist turns the comparison into a working investigation report. Name one part of that report and who uses it next.</p>",
                ),
                "EXIT": "<p>Rank the sick-resident tap-water pattern, healthy bottled-water comparison, flooding near the well, and one resident's river swim. Defend your strongest and weakest evidence.</p>",
                "DONE": "<ul><li>sick and healthy residents compared;</li><li>three clues and one supported claim;</li><li>one unanswered question and test;</li><li>one epidemiologist work product named;</li><li>practice check completed or reviewed.</li></ul>",
                "SUPPORT": "<p>outbreak = brote · source = fuente · exposure = exposición · pattern = patrón. Frame: “The evidence suggests ____ because ____.”</p>",
                "FALLBACK": "<p>The embedded case and PDF are the complete route. A written self-check replaces partner talk.</p>",
            },
            4: {
                "TITLE": "Build the Outbreak Response",
                "PURPOSE": "Use evidence to choose confirming tests, immediate actions, and one prevention priority.",
                "TOPIC": "Outbreak Response",
                "I_CAN": "I can use the FYF case to explain how public-health workers connect evidence to tests, immediate action, and prevention.",
                "SHOW_LEARNING": "Complete FYF pp. 77-78 and one public-health career-role sentence.",
                "TODAY": "<ul><li>choose tests that could confirm the source;</li><li>estimate impact using town facts;</li><li>separate immediate action from prevention.</li></ul>",
                "READY": f"<p>Open your workbook to FYF pp. 77-78 and your Day 3 work. Use {student_copy_link(4, 'the optional expanded response plan')} only when your teacher assigns the no-workbook or extended route.</p><p><strong>Real-event boundary:</strong> This is fictional analysis, not official health guidance.</p>",
                "MEDIA": image_tag(
                    uploads[4]["fyf-p77-response.png"]["id"],
                    "Find Your Future helpful information, confirming tests, and impact choices",
                    650,
                )
                + image_tag(
                    uploads[4]["fyf-p78-response.png"]["id"],
                    "Find Your Future immediate-action and prevention choices",
                    650,
                ),
                "STEPS": step(
                    1,
                    "Confirm the working claim",
                    "<p>Choose checks that reach the suspected source and explain why they matter.</p>",
                )
                + step(
                    2,
                    "Estimate possible impact",
                    "<p>Use the 2,000-resident population and shared water-system facts.</p>",
                )
                + step(
                    3,
                    "Choose immediate actions",
                    "<p>Use the supplied choices and explain why they reduce harm during the current event.</p>",
                )
                + step(
                    4,
                    "Choose a prevention priority",
                    "<p>Connect one supplied prevention choice to a clue and explain why it should come first.</p><div style=\"border-left:5px solid #1f617a;background:#f2f8fb;padding:10px 14px;margin:12px 0\"><strong>Use while deciding:</strong> immediate/inmediato · prevention/prevención · evidence/evidencia · trade-off/ventaja y límite<br><strong>Complete thought:</strong> We would _____ now because _____. To prevent another event, we would _____ because the case shows _____.</div>",
                )
                + step(
                    5,
                    "Name the career role",
                    "<p>Name one public-health worker who would test, communicate, or manage part of the response and what that worker produces.</p>",
                ),
                "EXIT": "<p>Classify safe-water distribution and moving well equipment above the flood line as immediate action or prevention. Explain each choice with a case clue.</p>",
                "DONE": "<ul><li>checks connect to the suspected source;</li><li>impact uses case facts;</li><li>immediate actions include a reason;</li><li>one prevention step answers a clue;</li><li>one public-health worker and work product named.</li></ul>",
                "SUPPORT": "<p>immediate = inmediato · prevention = prevención · test = analizar · trade-off = compensación. Frame: “We would ____ now because ____. We would prevent the next event by ____.”</p>",
                "FALLBACK": "<p>If you missed Day 3, use the teacher-provided working claim and case summary. No presentation is required.</p>",
            },
            5: {
                "TITLE": "Use Biomedical Career Evidence",
                "PURPOSE": "Compare the same fixed evidence for three careers and support one current recommendation.",
                "TOPIC": "Biomedical Career Evidence",
                "I_CAN": "I can compare three biomedical careers and support one recommendation with a task, preparation fact, and source-labeled career fact.",
                "SHOW_LEARNING": "Submit the private Biomedical Career Evidence Reflection.",
                "TODAY": "<ul><li>compare three fixed biomedical careers;</li><li>support one recommendation with evidence;</li><li>name one tradeoff and one next question.</li></ul>",
                "READY": f'<p>Open {file_link(files["CAREERS"]["id"], "the Biomedical Career Evidence Guide")} and <a href="{assignment_url}">the private Canvas reflection</a>. Use {student_copy_link(5, "the optional one-page paper response")} only when your teacher assigns paper.</p>',
                "MEDIA": "",
                "STEPS": step(
                    1, "Compare three careers", "<p>Review biomedical engineer, epidemiologist, and medical scientist. Record one central task and common preparation for each.</p>"
                )
                + step(
                    2,
                    "Keep the source labels",
                    "<p>Use one pay, outlook, or annual-openings fact. Keep the year, geography, and measure attached.</p>",
                )
                + step(
                    3,
                    "Make and test a recommendation",
                    "<p>Choose one career to keep exploring. Support it with a task and preparation fact, then name one tradeoff.</p>",
                )
                + step(
                    4,
                    "Reflect privately",
                    f'<p><a href="{assignment_url}">Open the private reflection assignment</a>. Type the four responses or upload the paper response only when your teacher assigned it.</p><div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:10px 14px;margin:12px 0"><strong>Use while reflecting:</strong> task/tarea · preparation/preparación · evidence/evidencia · tradeoff/compensación · verify/verificar<br><strong>Complete thought:</strong> I recommend exploring ____ because the task ____ and preparation ____ fit ____. The source shows ____. I still need to verify ____.</div>',
                )
                + step(
                    5,
                    "Finished early? (optional)",
                    "<p>Open your <em>Find Your Future</em> workbook to pp. 82-83, Patient Education. Sketch or generate a labeled medical illustration, compare it with a trusted anatomy source, and name one accurate feature and one problem.</p>",
                ),
                "EXIT": "<p>Your final reflection response is the exit check. Explain why one source-labeled fact supports or complicates your recommendation. Do not submit a second response.</p>",
                "DONE": "<ul><li>three careers compared;</li><li>recommendation uses a task, preparation fact, and source-labeled fact;</li><li>tradeoff and next question submitted privately.</li></ul>",
                "SUPPORT": "<p>task = tarea · preparation = preparación · evidence = evidencia · tradeoff = compensación · verify = verificar. Rehearse the complete thought before writing.</p>",
                "FALLBACK": "<p>Use the fixed career guide and the paper or Canvas response home your teacher assigned.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Biomedical Careers and a Practice Cover Letter",
                "TOPIC": "Biomedical Careers",
                "OBJECTIVE": "Students will compare three biomedical careers using preparation and labor-market evidence, then write a practice cover letter that answers one employer need with honest evidence.",
                "TEKS": "d(1)(C), d(2)(A), d(5)(A), d(7)(B)",
                "DOL": "Completed three-career comparison and five-part practice cover letter.",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(2)(A), d(5)(A), d(7)(B)",
                "ALERT": "<strong>Use the fixed evidence and fictional posting.</strong> Do not make teachers find a live job ad or make students search mixed salary measures.",
                "PREP": f"<ul><li><strong>Default grouping:</strong> pairs for the career scan; individual writing for the letter.</li><li>Project or post {file_link(files['CAREERS']['id'], 'the Biomedical Career Evidence Guide')}; print one copy per pair only when devices are not the reference route.</li><li>Provide one two-page {file_link(files['LETTER']['id'], 'Cover Letter Lab')} per student, or assign digital annotation. Project the supplied fictional posting.</li><li><strong>Supplied model:</strong> “The posting asks for attention to detail. I practiced this when I checked the labels and measurements in my science investigation before submitting it.”</li><li>Keep BLS source links available for questions. No live job search is needed.</li></ul>",
                "EVIDENCE": "<p>Collect one individual five-part practice letter per student. The three-career comparison is a reference/Stop and Jot, not a second graded packet. Formative portfolio evidence only; Week 6 adds no Minor or Major.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and career criteria warm-up", '''<p>Welcome students to Week 6 of Health Science and project the career priorities launch prompt.</p><ul><li>Ask students: <em>“When choosing a professional career in science or engineering, which factor should carry the most weight: daily work responsibilities, required years of education, earning potential, or the community problem the job solves? Defend your choice in one sentence.”</em></li><li>Hear 2-3 quick shares. Frame the lesson: <em>“Today we examine three advanced biomedical careers, compare their labor market metrics, and learn how to write an honest, evidence-based cover letter matching an employer's real needs.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-17 - Analyzing the Biomedical Career Evidence Guide", '''<p>Project the Biomedical Career Evidence Guide comparing three specialized occupations:</p><ul><li>1. <strong>Biomedical Engineer:</strong> Bachelor's degree; May 2024 U.S. median pay $100,710; 7% growth (highest median salary). Designs biocompatible devices, medical software, and artificial organs.</li><li>2. <strong>Epidemiologist:</strong> Master's degree; May 2024 U.S. median pay $81,390; 19% projected growth (fastest growth). Investigates disease patterns, infection sources, and public health policies.</li><li>3. <strong>Medical Scientist:</strong> Doctoral/Professional degree (Ph.D./M.D.); May 2024 U.S. median pay $100,890; 10,000 projected annual openings (highest volume of annual openings). Conducts clinical trials and laboratory research to develop new treatments.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 12): Verify students keep source labels (May 2024, U.S., median) firmly attached to every wage figure and do not mistake national medians for starting salaries.</li></ul>''')
                    + flow("#1f617a", "Minutes 17-25 - Dissecting the fictional laboratory internship posting", '''<p>Project the fictional summer laboratory internship posting.</p><ul><li>Guide students to identify TWO explicit employer requirements: (1) Rigorous attention to detail and measurement precision, and (2) Dependable collaborative teamwork under tight deadlines.</li><li>Model matching an employer need to authentic, honest student evidence without exaggeration: <em>“The posting asks for attention to detail. I practiced this when I calibrated measurements and verified data tables during our micro:bit simulator build.”</em></li></ul>''')
                    + flow("#e3ad19", "Minutes 25-42 - Drafting the Five-Part Practice Cover Letter", '''<p>Students draft their formal practice cover letter in the Cover Letter Lab:</p><ul><li>Part 1: Professional Header &amp; Salutation (Date, Hiring Manager, Laboratory Title).</li><li>Part 2: Opening Paragraph (State the exact position applied for and enthusiasm for the laboratory mission).</li><li>Part 3: Evidence Body Paragraph (Directly match one authentic personal accomplishment or classroom experience to one stated employer need).</li><li>Part 4: Professional Closing &amp; Next Step (Request an interview and state contact availability).</li><li>Part 5: Formal Sign-off and Signature.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 2 (Minute 34): Check student body paragraphs. Verify students provide concrete evidence from middle school projects, clubs, or family responsibilities rather than fabricating fake credentials.</li></ul>''')
                    + flow("#1f617a", "Minutes 42-47 - Need-to-evidence DOL and letter review", '''<p>Direct students to the Day 1 Exit Ticket prompt.</p><ul><li>Students complete the structured frame: <em>“The employer posting requires [Specific Need]. My strongest honest evidence for this requirement is [Concrete Past Action] because [Reason it proves readiness].”</em></li><li>Students underline their need-to-evidence sentence directly within their draft letter.</li></ul>''')
                    + flow("#24323d", "Minutes 47-50 - Collect letters and workspace reset", '''<p>Collect completed cover letters and transition materials.</p><ul><li><strong>Safe Trim:</strong> Provide the completed comparison key as a Stop-and-Jot reference rather than requiring full written chart transcription; fiercely protect the fictional posting analysis, authentic body paragraph, and exit check.</li></ul>''')
                ),
                "MONITOR": "<p><strong>Lap 1—career labels:</strong> target = May 2024 U.S. median and 2024-34 projection stay attached. Key: Biomedical Engineer has the highest median, Epidemiologist the fastest growth, Medical Scientist the most annual openings. If several students call median starting pay, pause and relabel one figure together. <strong>Lap 2—posting evidence:</strong> target = one exact employer need matched to one true example. Ask, “Which words came from the posting, and what did you actually do?” If students invent experience, return to the supplied school/team/family examples. <strong>Lap 3—letter:</strong> target = all five parts plus a specific body paragraph.</p><p><strong>Safe trim:</strong> use the teacher-key Stop and Jot instead of a full three-career written comparison. Protect the posting match, honest body paragraph, and five-part letter check.</p>",
                "RESOURCES": '<p><a href="https://www.bls.gov/ooh/architecture-and-engineering/biomedical-engineers.htm">BLS Biomedical Engineers</a> · <a href="https://www.bls.gov/ooh/life-physical-and-social-science/epidemiologists.htm">BLS Epidemiologists</a> · <a href="https://www.bls.gov/ooh/life-physical-and-social-science/medical-scientists.htm">BLS Medical Scientists</a></p>',
                "SUPPORT": "<p>The complete need-to-evidence frame is visible beside the drafting step. Read the posting aloud and mark one need/example in different colors. Permit typed, written, dictated, or teacher-scribed responses when documented. Score evidence, not mechanics unless meaning is unclear.</p>",
                "FALLBACK": "<p>No vendor login is required. Both PDFs contain the full absence route. H&amp;L is optional enrichment only.</p>",
            },
            2: {
                "TITLE": "Mini Medics Design Challenge",
                "TOPIC": "Biomedical Design",
                "OBJECTIVE": "Students will use the FYF future-technology scenario to plan, label, and explain a tiny medical robot and identify a biomedical career connected to the work.",
                "TEKS": "d(1)(C)",
                "DOL": "FYF pp. 80-81 design, one evidence question, and one career-work-product connection.",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>Future-technology scenario.</strong> The workbook asks students to design and reason. Do not present the concept as a clinically available treatment.",
                "PREP": f"<ul><li><strong>Default grouping:</strong> individual FYF design, then partner feedback. Provide one workbook and pencil per student, one ruler per pair, and one drawing-tool cup per table.</li><li>Open licensed pp. 79-81; students write on FYF pp. 80-81 by default.</li><li>Keep {file_link(files['MEDICS']['id'], 'the optional expanded design record')} for the no-workbook or extended route instead of printing it automatically. Chart paper is optional, not required.</li><li>Project the four mission checks. Model one purpose label: <strong>tracking signal — helps the trained team locate the design</strong>. Students create the remaining labels.</li></ul>",
                "EVIDENCE": "<p>Check one individual mission-aligned plan, labeled design, four-part journey, research evidence question, and career-work-product sentence. Formative portfolio evidence only; do not grade art, public speaking, or materials access.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and nanomedicine design warm-up", '''<p>Welcome students and project the future-medicine engineering prompt.</p><ul><li>Ask, <em>“Imagine engineers design a tiny medical robot small enough to travel through a human blood vessel to clear a blockage. Beyond making it small, what critical physical or navigational factor must the engineers control to prevent harming the patient?”</em></li><li>Collect 2-3 student thoughts (e.g., vessel wall damage, getting stuck, steering control, power source, safe removal).</li><li>Bridge with, <em>“In biomedical engineering, miniaturization creates tremendous medical potential but requires extreme safety protocols. Today you engineer a fictional nanorobot prototype on FYF pp. 80-81.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-13 - Four biomedical engineering mission constraints", '''<p>Open FYF pp. 79-81 and review the four core engineering criteria:</p><ul><li>1. <strong>Microscopic Scale:</strong> Must safely navigate microscopic capillary and arterial dimensions.</li><li>2. <strong>Active Guidance System:</strong> Magnetic, acoustic, or chemical propulsion controlled by clinicians.</li><li>3. <strong>Vessel Wall Protection:</strong> Smooth, biocompatible casing that prevents tissue laceration or clotting.</li><li>4. <strong>Continuous Tracking Signal:</strong> Emits an ultrasonic or radio signal so the clinical team tracks its real-time location.</li><li>Model one purpose label: <em>“Tracking Beacon — transmits ultrasound pulses so the surgical team maps real-time location on the monitor.”</em></li></ul>''')
                    + flow("#1f617a", "Minutes 13-37 - Three-chunk engineering design sprint (Plan, Draw, Map)", '''<p>Students construct their nanomedical prototype across three progressive checkpoints:</p><ul><li><strong>Chunk 1 (Plan &amp; Tool Selection - 8 min):</strong> Select exactly THREE micro-tools (e.g., micro-gripper, thermal dissolver, localized medicine injector). Justify how each tool operates safely.</li><li><strong>Chunk 2 (Technical Schematic - 10 min):</strong> Draw the robot with four precise purpose-driven callout labels (guidance, casing, tools, tracking).</li><li><strong>Chunk 3 (Mission Journey Map - 6 min):</strong> Chart the 4-phase clinical pathway: Injection/Entry &rarr; Vessel Navigation &rarr; Targeted Intervention &rarr; Safe Retrieval/Deactivation.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Checkpoint 1 (Minute 20): Check that students label tool FUNCTIONS, not just shapes.<br>• Checkpoint 2 (Minute 30): Verify the 4-phase journey map shows active clinician control at every step.</li></ul>''')
                    + flow("#e3ad19", "Minutes 37-42 - Peer safety review and protocol audit", '''<p>Pairs conduct a structured 5-minute peer audit using the Design Review Protocol.</p><ul><li>Partner A identifies the single strongest mechanical design feature.</li><li>Partner B asks ONE critical safety question (e.g., <em>“What happens if the tracking signal fails inside a deep vessel?”</em>).</li><li>Each student records one actionable safety refinement on their schematic.</li></ul>''')
                    + flow("#1f617a", "Minutes 42-47 - Design safety DOL and biomedical career connection", '''<p>Direct students to the Day 2 Exit Ticket.</p><ul><li>Prompt: <em>“Why does making a medical device smaller NOT automatically make it safer? Then, name the biomedical career that would design, test, and manufacture this physical device.”</em></li><li>Confirm student identification of <strong>Biomedical Engineer</strong> and the associated design documentation work product.</li></ul>''')
                    + flow("#24323d", "Minutes 47-50 - Material return and workspace reset", '''<p>Return rulers and drawing materials; collect completed design workbooks.</p><ul><li><strong>Safe Trim:</strong> Cut chart-paper extensions and partner comparisons; protect the 4-label schematic, 4-phase journey map, and the safety exit check.</li></ul>''')
                ),
                "MONITOR": "<p><strong>Checkpoint 1—release to draw:</strong> target = size, three tools, guidance, vessel protection, and signal. If three or more students stall on decoration, stop and model how one label states a purpose. <strong>Checkpoint 2—journey:</strong> target = enter, travel, act, finish in a workable order. Ask, “Where is the trained team still in control?” <strong>Checkpoint 3—evidence:</strong> target = one safety question plus a biomedical career and work product. Key exit answer: smaller may help fit but does not prove control or vessel safety.</p><p><strong>Safe trim:</strong> cut chart-paper transfer and partner comparison first. Protect the mission check, labeled workbook design, evidence question, and career-work-product sentence. Reserve three minutes for tool return and evidence collection.</p>",
                "RESOURCES": "<p>Licensed FYF pp. 79-81 are embedded in the student page. Patient Education pp. 82-83 is reserved for optional Canva or Adobe Express extension.</p>",
                "SUPPORT": "<p>The design-evidence frame and bilingual terms are visible beside the missing-evidence step. Allow the supplied workbook outline, speech-to-text, and independent work. The optional PDF now has one proportional sketch box. Plain paper and chart paper are equal.</p>",
                "FALLBACK": "<p>No equipment or live site is required. The student page and PDF contain the complete route.</p>",
            },
            3: {
                "TITLE": "Outbreak Investigators: Follow the Evidence",
                "TOPIC": "Outbreak Evidence",
                "OBJECTIVE": "Students will use the FYF case to explain how an epidemiologist compares exposure and outcome, writes a working claim, and identifies what still needs testing.",
                "TEKS": "d(1)(C)",
                "DOL": "FYF pp. 75-76 investigation report and one epidemiologist work-product sentence.",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>Fictional case.</strong> A supported hypothesis is not proof, and the worksheet is not real public-health guidance.",
                "PREP": f"<ul><li><strong>Default grouping:</strong> individual FYF pp. 75-76 with a two-minute pair comparison. Provide one workbook per student and project the embedded case table.</li><li>Keep {file_link(files['INVESTIGATE']['id'], 'the optional expanded investigation record')} for the no-workbook or extended route; do not print it as a second class packet.</li><li>Open the unpublished evidence quiz. Display the fictional-case/real-event boundary before students enter the case.</li></ul>",
                "EVIDENCE": "<p>Collect one individual FYF investigation report with a sick-to-healthy comparison, three clues, working claim, unanswered test, and epidemiologist work-product sentence. The quiz is formative feedback, not a second graded artifact. Week 6 adds no Minor or Major.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and epidemiological data warm-up", '''<p>Welcome students and project the epidemic investigation launch prompt.</p><ul><li>Ask, <em>“When an unexplained illness suddenly strikes a community, what four categories of evidence must investigators gather immediately before making any public claims?”</em></li><li>Collect student answers. Sort their responses into the Four Epidemiological Pillars: (1) <strong>Exposure:</strong> What did people eat, drink, or touch? (2) <strong>Symptoms:</strong> What exact clinical signs appeared? (3) <strong>Timeline:</strong> When did symptoms start? (4) <strong>Comparison Group:</strong> Who was exposed to the same environment but remained healthy?</li><li>Bridge with, <em>“Epidemiologists are medical detectives. Today we investigate a sudden outbreak in the fictional town of Fairview Edge on FYF pp. 75-76.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-10 - The Epidemiologist role and strict scientific boundaries", '''<p>Establish the professional role and non-negotiable scientific boundaries:</p><ul><li>Epidemiologists search for patterns, calculate disease rates, and test hypotheses; they DO NOT jump to conclusions based on dramatic single anecdotes.</li><li>Safety &amp; Ethics Rule: Fairview Edge is a fictional simulation. Real-world public health emergencies follow strict county health department protocols and certified water testing.</li></ul>''')
                    + flow("#1f617a", "Minutes 10-22 - Auditing Fairview Edge case data (Exposure vs. Outcome)", '''<p>Direct students to the Fairview Edge case evidence table (FYF p. 75).</p><ul><li>Pairs execute a structured data audit, comparing sick residents against healthy residents:</li><li>Clue 1: All 8 sick residents drank municipal tap water.</li><li>Clue 2: Heavy flooding occurred 48 hours prior near Well Station #4.</li><li>Clue 3: Two residents who drank ONLY bottled water lived in the same neighborhood but showed ZERO gastrointestinal symptoms (the vital comparison group!).</li><li>Clue 4: Several sick residents swam in the river, but not all; tap water is the only universal exposure.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 16): Intervene if students focus solely on sick patients. Prompt: <em>“Look at the healthy residents. What did they drink?”</em></li></ul>''')
                    + flow("#e3ad19", "Minutes 22-40 - Authoring the Epidemiological Investigation Report", '''<p>Students independently draft their formal Investigation Report (FYF p. 76):</p><ul><li>1. <strong>Working Claim (Hypothesis):</strong> Formulate a defensible claim: <em>“Contaminated municipal tap water following well flooding is the most probable exposure source causing acute gastrointestinal illness.”</em></li><li>2. <strong>Evidence Chain:</strong> Cite three concrete facts (flood timing, 100% tap water correlation among sick, and 0% illness among bottled water drinkers).</li><li>3. <strong>Unanswered Question &amp; Next Test:</strong> Identify what test must occur before proving causality (laboratory bacterial culture of Well #4 water).</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 2 (Minute 32): Verify students qualify their claim as a working hypothesis, not absolute proof.</li></ul>''')
                    + flow("#1f617a", "Minutes 40-47 - Formative quiz and career connection DOL", '''<p>Students complete the short Canvas Evidence Quiz or written check.</p><ul><li>Assess identification of the comparison group, elimination of river swimming as sole cause, and next testing step.</li><li>Complete the exit sentence: <em>“An Epidemiologist produces an [Investigation Report / Outbreak Summary] which is used by [City Water Authority / Public Health Officials] to take immediate safety action.”</em></li></ul>''')
                    + flow("#24323d", "Minutes 47-50 - Collect reports and transition buffer", '''<p>Confirm completion of FYF p. 76 and close student devices.</p><ul><li><strong>Safe Trim:</strong> Move the optional practice quiz to an asynchronous review; fiercely protect the sick-vs-healthy data comparison, working claim, and next testing step.</li></ul>''')
                ),
                "MONITOR": "<p><strong>Lap 1—comparison:</strong> target = exposure and outcome in the same sentence, including a healthy comparison. If several students list only sick residents, pause and point to the bottled-water rows without supplying the claim. <strong>Lap 2—claim:</strong> target = tap-water exposure after flooding near the well, supported by three clues and qualified as a hypothesis. If one river swim becomes the whole explanation, ask whether it accounts for every case. <strong>Lap 3—next test:</strong> target = water testing or additional interviews. <strong>Lap 4—career:</strong> target = an investigation-report part and its next user.</p><p><strong>Safe trim:</strong> move the practice quiz and ranked exit check to the next opening. Protect the individual comparison, working claim, unanswered test, and career-work-product sentence.</p>",
                "RESOURCES": '<p>Optional enrichment: <a href="https://www.cdc.gov/nerd-academy/outbreak-investigations/index.html">CDC NERD Academy outbreak investigations</a>. Keep it supplemental.</p>',
                "SUPPORT": "<p>The complete comparison/claim frame is visible beside the report step. Read the table aloud, highlight exposure and outcome columns, and allow a written partner route. Provide the real-event boundary in text and speech. Score the evidence chain, not English mechanics.</p>",
                "FALLBACK": "<p>The embedded licensed pages make the absence route complete. Students do not need to search the web.</p>",
            },
            4: {
                "TITLE": "Outbreak Investigators: Build the Response",
                "TOPIC": "Outbreak Response",
                "OBJECTIVE": "Students will use the FYF case to explain how public-health workers connect evidence to confirming tests, immediate action, and prevention.",
                "TEKS": "d(1)(C)",
                "DOL": "FYF pp. 77-78 response plan and one public-health career-role sentence.",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>Analyze supplied actions only.</strong> Students do not invent medical or public-health instructions.",
                "PREP": f"<ul><li><strong>Default grouping:</strong> individual FYF pp. 77-78 with an optional quiet partner check. Provide one workbook per student.</li><li>Project the supplied Day 3 working claim: <strong>Tap-water exposure after flooding near the well is the strongest current hypothesis; bottled-water residents who stayed healthy strengthen the comparison, but water testing is still needed.</strong></li><li>Keep {file_link(files['RESPONSE']['id'], 'the optional expanded response plan')} for the no-workbook or extended route; do not print it automatically.</li><li>Display the real-event boundary. Students analyze only the supplied action list.</li></ul>",
                "EVIDENCE": "<p>Collect one individual FYF response plan with a confirming test, fact-based impact estimate, explained immediate action, prevention priority tied to a clue, and public-health career-role sentence. Formative portfolio evidence only; Week 6 adds no Minor or Major.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and immediate action vs. prevention warm-up", '''<p>Welcome students and project the emergency response prompt.</p><ul><li>Ask, <em>“When a town's water supply is contaminated, what is the crucial difference between an immediate emergency action taken today and a long-term preventive action taken over the next six months?”</em></li><li>Collect 2-3 student thoughts (e.g., today: boil water notice and bottled water distribution; six months: rebuilding the well above flood level and adding filtration).</li><li>Bridge with, <em>“Public health response requires a coordinated strategy that stops immediate harm while engineering long-term resilience. Today we build the Fairview Edge Outbreak Response Plan.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-18 - Sourcing confirming tests and estimating population impact", '''<p>Review the Day 3 working claim and open FYF pp. 77-78.</p><ul><li>1. <strong>Confirming Test:</strong> Select the exact scientific test required to confirm bacterial contamination at Well Station #4 (water microbiology culture for E. coli/coliform bacteria).</li><li>2. <strong>Population Impact Estimation:</strong> Fairview Edge has an estimated population of 2,000 residents on the municipal water grid. Students calculate potential exposure if 60% of households drink unboiled tap water.</li><li>Address common misconception: Emphasize that population impact must be grounded in actual municipal census data, not guessed hyperbole like 'millions.'</li></ul>''')
                    + flow("#1f617a", "Minutes 18-36 - Designing the multi-tiered Outbreak Response Plan", '''<p>Students evaluate and select interventions from the supplied public health action menu:</p><ul><li><strong>Tier 1: Immediate Emergency Containment (0-24 Hours):</strong> Issue emergency boil-water notice; distribute bottled water to schools and elderly centers; temporarily shut down Well #4 pump.</li><li><strong>Tier 2: Intermediate Remediation (1-2 Weeks):</strong> Shock chlorinate municipal water mains; conduct daily water testing across all distribution zones.</li><li><strong>Tier 3: Long-term Systemic Prevention (1-3 Years):</strong> Elevate Well #4 electrical controls 5 feet above the 100-year floodplain; install automated ultraviolet disinfection.</li><li>Students identify ONE operational trade-off (e.g. cost, resident inconvenience, business disruption).</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 25): Verify students differentiate between today's emergency actions and permanent infrastructure changes.<br>• Lap 2 (Minute 31): Check trade-off analysis—ensure students articulate concrete community costs.</li></ul>''')
                    + flow("#e3ad19", "Minutes 36-42 - Response plan checklist and partner review", '''<p>Pairs conduct a 6-minute peer review using the Response Plan Quality Rubric.</p><ul><li>Verify that every proposed action ties directly to a verified case clue from Day 3.</li><li>Confirm that a supervisory public health authority is designated for each action.</li></ul>''')
                    + flow("#1f617a", "Minutes 42-47 - Action classification DOL and public health career sentence", '''<p>Direct students to the Day 4 Exit Ticket.</p><ul><li>Classify two actions: (1) <em>“Distributing 5,000 gallons of bottled water to the neighborhood center is an [Immediate Containment / Long-term Prevention] action because [Reason].”</em> (2) <em>“Re-engineering the well pump housing above the floodplain is a [Immediate Containment / Long-term Prevention] action because [Reason].”</em></li><li>Complete the career-role sentence: <em>“A Public Health Officer coordinates this response plan with city managers to protect community safety.”</em></li></ul>''')
                    + flow("#24323d", "Minutes 47-50 - Submit plans and case closure", '''<p>Collect completed response plans and close the Fairview Edge simulation.</p><ul><li><strong>Safe Trim:</strong> Replace partner review with an independent 3-minute self-audit; protect the confirming test, population estimate, immediate-vs-prevention classification, and career sentence.</li></ul>''')
                ),
                "MONITOR": "<p><strong>Lap 1—test:</strong> target = the check reaches the suspected source and names a supporting result. <strong>Lap 2—impact:</strong> target = reasoning uses the 2,000-person population or shared system. If students write “thousands,” ask them to compare the estimate with the town total. <strong>Lap 3—immediate action:</strong> target = one supplied action plus why it reduces current harm. <strong>Lap 4—prevention:</strong> target = one system change tied to a case clue and one trade-off. If several students check every option, pause and model one evidence-to-action sentence. Key exit: safe-water distribution is immediate; moving equipment above flood level is prevention.</p><p><strong>Safe trim:</strong> replace peer review with the private checklist. Protect one test, impact estimate, immediate action, prevention priority, and career-role sentence.</p>",
                "RESOURCES": "<p>Licensed FYF pp. 77-78 supply the action list. The CCE worksheet adds role, support, evidence, and trade-off reasoning.</p>",
                "SUPPORT": "<p>The complete immediate/prevention frame and bilingual terms are visible beside the decision step. Permit typed, written, or dictated evidence. No presentation is required. Score the evidence-to-action link, not English mechanics.</p>",
                "FALLBACK": "<p>An absent student starts from the teacher-provided Day 3 claim. In a real event, follow current local officials and district directions.</p>",
            },
            5: {
                "TITLE": "Biomedical Career Evidence Reflection",
                "TOPIC": "Biomedical Career Evidence",
                "OBJECTIVE": "Students will compare fixed evidence for three biomedical careers and support one current recommendation with a task, preparation fact, and source-labeled career fact.",
                "TEKS": "d(1)(C), d(2)(A)",
                "DOL": "Submitted private Biomedical Career Evidence Reflection.",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(2)(A)",
                "ALERT": "<strong>Use the fixed evidence guide.</strong> No saved-career prerequisite, profile screenshot, or platform completion is required.",
                "PREP": f"<ul><li>Open {file_link(files['CAREERS']['id'], 'the Biomedical Career Evidence Guide')} and one strong model.</li><li><strong>Default grouping:</strong> individual response with one brief partner rehearsal.</li><li>Open the private Canvas reflection assignment. Use {file_link(files['REFLECT']['id'], 'the one-page reflection')} only for the assigned paper route.</li></ul>",
                "EVIDENCE": "<p>Collect one private recommendation using a career task, preparation fact, source-labeled career fact, tradeoff, and question to verify. Formative portfolio evidence only; Week 6 adds no Minor or Major.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and evidence reflection warm-up", '''<p>Welcome students, seat them with their weekly materials, and project the reflective launch prompt.</p><ul><li>Ask, <em>“Over the past two six-weeks, you have explored law, public safety, nursing, dental health, medical billing, and biomedical science. When evaluating all these options, which piece of evidence tells you the MOST about your personal fit: the daily work tasks, the required degree, or the type of problem you get to solve each day?”</em></li><li>Collect 2-3 student thoughts. Bridge with, <em>“Today we synthesize our Health Science exploration, compare three biomedical careers using verified labor data, and finalize our 2SW portfolio reflection.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-25 - Comprehensive three-career evidence audit", '''<p>Students reopen the Biomedical Career Evidence Guide and their notes from Day 1.</p><ul><li>Students audit three careers across four rigorous dimensions: (1) Core daily clinical/engineering tasks, (2) Mandatory educational preparation (Bachelor's vs. Master's vs. Ph.D./M.D.), (3) Authentic work conditions and physical environments, and (4) Verified May 2024 U.S. median pay and projected 2024-34 outlook.</li><li>Enforce source integrity: Verify students preserve the survey year (May 2024), geographic scope (national U.S.), and statistical measure (median).</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 12): Confirm students have completed all rows with exact BLS figures.<br>• Lap 2 (Minute 20): Check preparation fields—differentiate undergraduate engineering degrees from graduate epidemiology programs.</li></ul>''')
                    + flow("#1f617a", "Minutes 25-45 - Authoring the private Biomedical Career Evidence Reflection", '''<p>Students complete their formal written reflection on Canvas (or the approved paper reflection sheet):</p><ul><li>1. <strong>Personal Career Fit Recommendation:</strong> Recommend ONE biomedical career that best matches personal strengths and interests.</li><li>2. <strong>Evidence Support:</strong> Cite at least ONE daily work task and ONE educational preparation requirement supporting the recommendation.</li><li>3. <strong>Source-Labeled Economic Benchmark:</strong> Incorporate the May 2024 U.S. median salary and 2024-34 growth projection with full source labels.</li><li>4. <strong>Realistic Trade-off:</strong> Identify ONE authentic trade-off or challenge associated with this pathway (e.g. rigorous advanced math/science prerequisites, lengthy post-graduate residency, high educational expense).</li><li>5. <strong>Next Unanswered Question:</strong> Formulate ONE precise, actionable factual question to research next.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 3 (Minute 36): Verify students include a genuine trade-off and a concrete question to verify.</li></ul>''')
                    + flow("#e3ad19", "Minutes 45-50 - Submit reflection and 2SW portfolio wrap-up", '''<p>Students submit their completed reflection on the private Canvas assignment or hand in their labeled paper sheet.</p><ul><li>Verify submission status on student screens.</li><li>Briefly celebrate the conclusion of the Health Science and Public Service clusters for the Second Six Weeks!</li><li><strong>Safe Trim:</strong> Provide pre-printed comparison rows so students focus immediately on authoring their personal recommendation, trade-off, and next fact to verify.</li></ul>''')
                ),
                "MONITOR": "<p><strong>Minute 10:</strong> target = three careers have a central task and preparation fact. <strong>Minute 25:</strong> target = one source-labeled fact is attached to the recommendation. <strong>Minute 40:</strong> target = tradeoff and question to verify are present. <strong>Final check:</strong> collect one private reflection; do not require a public recommendation.</p><p><strong>Safe trim:</strong> provide the fixed career rows and require the recommendation, source label, tradeoff, and question to verify.</p>",
                "RESOURCES": f'<p>{file_link(files["CAREERS"]["id"], "Biomedical Career Evidence Guide")}</p><p>{file_link(files["REFLECT"]["id"], "Biomedical Career Evidence Reflection")}</p>',
                "SUPPORT": "<p>The complete recommendation frame is visible beside the private reflection. Offer read-aloud, chunking, bilingual labels, oral rehearsal, and a private written response. Score evidence use, not preference or English mechanics.</p>",
                "FALLBACK": "<p>The fixed guide and paper or Canvas reflection are the complete routes. An absent student completes the same comparison without platform catch-up.</p>",
            },
        }

        titles = {
            1: "STUDENT: 2SW Wk6 Day 1 - Biomedical Careers and Cover Letter",
            2: "STUDENT: 2SW Wk6 Day 2 - Mini Medics Design",
            3: "STUDENT: 2SW Wk6 Day 3 - Outbreak Evidence",
            4: "STUDENT: 2SW Wk6 Day 4 - Outbreak Response",
            5: "STUDENT: 2SW Wk6 Day 5 - Biomedical Career Evidence Reflection",
        }
        pages = {}
        order = []
        for day in range(1, 6):
            header = await upsert_subheader(client, module["id"], f"Day {day}")
            order.append(("SubHeader", header["id"], f"Day {day}"))
            student_title = titles[day]
            student_page = await upsert_page(
                client,
                student_title,
                render(
                    "2sw-wk6-student.html",
                    {"COURSE_ID": COURSE_ID, "DAY": day, **student[day]},
                ),
                slugify(student_title),
            )
            teacher_title = f"TEACHER: 2SW Wk6 Day {day} Facilitator Guide"
            teacher_page = await upsert_page(
                client,
                teacher_title,
                render(
                    "2sw-wk6-teacher.html",
                    {
                        "COURSE_ID": COURSE_ID,
                        "DAY": day,
                        "STUDENT_PAGE_URL": student_page["url"],
                        **teacher[day],
                    },
                ),
                slugify(teacher_title),
            )
            await upsert_page_item(client, module["id"], teacher_page, teacher_title)
            await upsert_page_item(client, module["id"], student_page, student_title)
            pages[day] = {"teacher": teacher_page, "student": student_page}
            order.extend(
                [
                    ("Page", teacher_page["url"], teacher_title),
                    ("Page", student_page["url"], student_title),
                ]
            )
            if day == 3:
                await upsert_quiz_item(client, module["id"], quiz)
                order.append(("Quiz", quiz["id"], QUIZ_TITLE))
            if day == 5:
                await upsert_assignment_item(client, module["id"], assignment)
                order.append(("Assignment", assignment["id"], ASSIGNMENT_TITLE))

        items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")

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
        items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, start=1):
            item = next(entry for entry in items if matches_item(entry, kind, key))
            await api(
                client,
                "PUT",
                f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}",
                data={"module_item[position]": position, "module_item[title]": title},
            )

        final_items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        module = await api(
            client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}"
        )
        if module.get("published"):
            raise RuntimeError("Week 6 module unexpectedly published")
        if quiz.get("published"):
            raise RuntimeError("Week 6 practice quiz unexpectedly published")
        if assignment.get("published"):
            raise RuntimeError("Week 6 formative reflection unexpectedly published")
        published_pages = [
            value["url"]
            for pair in pages.values()
            for value in pair.values()
            if value.get("published")
        ]
        if published_pages:
            raise RuntimeError(f"Published Week 6 pages remain: {published_pages}")
        if len(final_items) != len(order):
            raise RuntimeError(
                f"Expected {len(order)} Week 6 module items; found {len(final_items)}"
            )
        for position, ((kind, key, title), item) in enumerate(
            zip(order, final_items), start=1
        ):
            if (
                item.get("position") != position
                or item.get("title") != title
                or not matches_item(item, kind, key)
            ):
                raise RuntimeError(f"Week 6 module order mismatch at position {position}")
        print(
            json.dumps(
                {
                    "module": {"id": module["id"], "published": module["published"]},
                    "quiz": {"id": quiz["id"], "published": quiz.get("published")},
                    "assignment": {
                        "id": assignment["id"],
                        "published": assignment.get("published"),
                        "grading_type": assignment.get("grading_type"),
                        "omit_from_final_grade": assignment.get("omit_from_final_grade"),
                    },
                    "folders": {
                        str(day): {"id": folder["id"], "locked": folder["locked"]}
                        for day, folder in folders.items()
                    },
                    "support_folder": {
                        "id": support_folder["id"],
                        "locked": support_folder["locked"],
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
                            "content_id": item.get("content_id"),
                        }
                        for item in final_items
                    ],
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
