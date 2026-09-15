"""Build the unpublished 3SW Week 6 Entrepreneurship Canvas module."""

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
    1: "https://docs.google.com/document/d/1kS1AzgrAqLeZukTZ6ql_z0SzqMLTvKmUsBumDwR-swk/copy",
    2: "https://docs.google.com/document/d/1fxcakYpq4YFYJO0OvWCdxi7NkIoDx3cRBeKYb0sZrWY/copy",
    3: "https://docs.google.com/document/d/16qhLtCZXfq3-hjAbD0m3wwpHAgdMjDWxNDxLVRuwjtM/copy",
    4: "https://docs.google.com/document/d/1pgDBYyBjHCXEex_heuEL0bhRnSPv5e0J1F7R2gtqQdQ/copy",
    5: "https://docs.google.com/document/d/1JSekSC6t7jLXY2Yl0nHvdmD0l-HqGSJZvy13PK0UGy4/copy",
}


# One Google Doc per worksheet (build/google_docs/student_worksheet_docs.json).
# Keyed by (day, anchor label) so a worksheet button never opens the day's exit ticket.
STUDENT_WORKSHEET_COPY_URLS = {
    (1, 'the two-page Entrepreneurship Opportunity Guide'): "https://docs.google.com/document/d/1kUMxIn62Gma1uqow3R9qe6ZZ-3pHnd7shhScR-cLY98/copy",
    (2, 'the support and catch-up packet'): "https://docs.google.com/document/d/1oZ_V2ieQiZ5616eUB--PbkF6v4G7Ko2Ft3IhJxcIeoA/copy",
    (3, 'the support packet'): "https://docs.google.com/document/d/1oZ_V2ieQiZ5616eUB--PbkF6v4G7Ko2Ft3IhJxcIeoA/copy",
    (4, 'the Venture Brief and Individual Pitch Record'): "https://docs.google.com/document/d/1cCYMFzSWUJVKiB9kEU1QHNSQMnx_tx4swQgSaZUjmFE/copy",
    (5, 'the Personal Budget and Decision Plan'): "https://docs.google.com/document/d/1Z6ZI5BQB1cvPmGp_CxdwOMoW9rItpRfMYZXpNWTal0w/copy",
}


def student_copy_link(day, label):
    url = STUDENT_WORKSHEET_COPY_URLS.get((day, label), STUDENT_GOOGLE_COPY_URLS[day])
    return f'<a href="{url}">{label}</a>'

MODULE_NAME = "3SW Wk6: Build, Test, and Pitch a Business Idea"
QUIZ_TITLE = "PRACTICE: Entrepreneurship Evidence Check"
PORTFOLIO_TITLE = "RECOVERY: Entrepreneurship Portfolio"
LEGACY_PORTFOLIO_TITLE = "DRAFT: Entrepreneurship Portfolio"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/3sw/wk6"


def preflight():
    worksheet_names = (
        "3sw-wk6-entrepreneurship-opportunity-guide.pdf",
        "3sw-wk6-million-dollar-idea-support-packet.pdf",
        "3sw-wk6-venture-brief-and-pitch-record.pdf",
        "3sw-wk6-dallas-county-living-cost-guide.pdf",
        "3sw-wk6-budget-and-scholarship-plan.pdf",
        "3sw-wk6-entrepreneurship-portfolio-rubric.pdf",
    )
    visual_names = {
        1: (
            "fyf-business-opener.jpg",
            "fyf-irving-business-programs.jpg",
            "fyf-irving-business-context.jpg",
        ),
        2: (
            "fyf-million-dollar-idea-problem.jpg",
            "fyf-million-dollar-idea-sprint.jpg",
        ),
        3: (
            "fyf-million-dollar-idea-test.jpg",
            "fyf-million-dollar-idea-call.jpg",
        ),
    }
    required = [
        TEMPLATES / "3sw-wk6-student.html",
        TEMPLATES / "3sw-wk6-teacher.html",
        *(ROOT / "docs/resources/worksheets" / name for name in worksheet_names),
        *(
            ASSETS / f"day{day}" / name
            for day, names in visual_names.items()
            for name in names
        ),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"3SW Wk6 preflight missing required files: {missing}")


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
            f"Duplicate Canvas modules named {MODULE_NAME!r}: "
            f"{[module['id'] for module in matches]}"
        )
    found = matches[0] if matches else None
    if found:
        return await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{found['id']}",
            data={"module[name]": MODULE_NAME, "module[published]": "false"},
        )
    return await api(client, "POST", f"/courses/{COURSE_ID}/modules", data={"module[name]": MODULE_NAME, "module[published]": "false"})


async def ensure_folder(client, path):
    current, folder = "", None
    for name in path.split("/")[1:]:
        target = f"{current}/{name}".strip("/")
        encoded = httpx.URL("/" + target).raw_path.decode("ascii").lstrip("/")
        response = await client.get(f"{BASE}/api/v1/courses/{COURSE_ID}/folders/by_path/{encoded}")
        if response.status_code == 200 and response.json():
            folder = response.json()[-1]
        else:
            folder = await api(client, "POST", f"/courses/{COURSE_ID}/folders", data={"name": name, "parent_folder_path": "course files" + (f"/{current}" if current else ""), "locked": "true"})
        current = target
    if folder and not folder.get("locked"):
        folder = await api(client, "PUT", f"/folders/{folder['id']}", data={"locked": "true"})
    return folder


async def upload(client, path, folder_path):
    start = await api(client, "POST", f"/courses/{COURSE_ID}/files", data={"name": path.name, "parent_folder_path": folder_path, "on_duplicate": "overwrite"})
    response = await client.post(start["upload_url"], data=start["upload_params"], files={"file": (path.name, path.read_bytes(), mimetypes.guess_type(path.name)[0] or "application/octet-stream")}, follow_redirects=True)
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
    data = {"wiki_page[title]": title, "wiki_page[body]": body, "wiki_page[published]": "false", "wiki_page[editing_roles]": "teachers"}
    response = await client.get(f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{url}")
    if response.status_code == 200:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/pages/{url}", data=data)
    if response.status_code != 404:
        response.raise_for_status()
    return await api(client, "POST", f"/courses/{COURSE_ID}/pages", data=data)


async def upsert_assignment(client, title, description):
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [
        entry
        for entry in assignments
        if entry.get("name") in {title, LEGACY_PORTFOLIO_TITLE}
    ]
    if len(matches) > 1:
        raise RuntimeError(
            f"Expected at most one Week 6 recovery portfolio; found {len(matches)}: "
            f"{[entry['id'] for entry in matches]}"
        )
    found = matches[0] if matches else None
    data = {
        "assignment[name]": title,
        "assignment[description]": description,
        "assignment[submission_types][]": ["online_upload", "online_text_entry", "media_recording"],
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
            f"Recovery assignment invariant failed for {title!r}: "
            f"published={assignment.get('published')}, "
            f"points={assignment.get('points_possible')}, "
            f"grading={assignment.get('grading_type')}, "
            f"omit={assignment.get('omit_from_final_grade')}"
        )
    return assignment


async def canvas_preflight(client):
    modules = await paged(client, f"/courses/{COURSE_ID}/modules")
    module_matches = [entry for entry in modules if entry.get("name") == MODULE_NAME]
    if len(module_matches) > 1:
        raise RuntimeError(
            f"Duplicate Canvas modules named {MODULE_NAME!r}: "
            f"{[entry['id'] for entry in module_matches]}"
        )
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    assignment_matches = [
        entry
        for entry in assignments
        if entry.get("name") in {PORTFOLIO_TITLE, LEGACY_PORTFOLIO_TITLE}
    ]
    if len(assignment_matches) > 1:
        raise RuntimeError(
            "Duplicate Week 6 recovery portfolios must be resolved before writes: "
            f"{[entry['id'] for entry in assignment_matches]}"
        )
    quizzes = await paged(client, f"/courses/{COURSE_ID}/quizzes")
    quiz_matches = [entry for entry in quizzes if entry.get("title") == QUIZ_TITLE]
    if len(quiz_matches) > 1:
        raise RuntimeError(
            f"Duplicate quizzes named {QUIZ_TITLE!r}: "
            f"{[entry['id'] for entry in quiz_matches]}"
        )


QUESTIONS = [
    ("Q1 - Complete opportunity", "Which description is a complete entrepreneurship opportunity?", "Families wait too long for affordable event meals, so a student team proposes a mobile meal-prep service and identifies food safety and on-time delivery as owner responsibilities.", ["Start a restaurant because restaurants make money.", "Sell something online and hope people buy it.", "Choose a logo before identifying a customer or problem."], "Correct. A usable opportunity connects a problem, customer, offer, and owner responsibility.", "A business name or product alone does not show an opportunity."),
    ("Q2 - Stress-test evidence", "Which statement gives the strongest customer-choice evidence?", "Students currently borrow chargers from the office, and a low-cost locker rental would be available in the same hallway.", ["Everyone will love my idea.", "The colors look professional.", "I have wanted to build this for a long time."], "Correct. It names the current option and a specific reason a customer might choose the new one.", "Enthusiasm and appearance are not evidence of customer choice."),
    ("Q3 - Abandon it", "When can Abandon It be a strong entrepreneurial decision?", "When the evidence shows the risk or build challenge is greater than the idea's current value.", ["Only when the student did not finish the work.", "Never; entrepreneurs must keep every idea.", "Only when classmates dislike the idea."], "Correct. Stopping or changing an idea can save time and money.", "The verdict is not the score. The evidence and reasoning are."),
    ("Q4 - Living-cost label", "What does the $3,450 monthly classroom figure represent?", "A rounded Dallas County living-cost scenario for one adult with no children, based on an MIT page updated February 15, 2026.", ["Guaranteed DFW starting pay.", "Every adult's exact monthly budget.", "A salary after taxes for any career."], "Correct. Keep place, household, date, and measure attached.", "It is a planning scenario, not pay or personal tax advice."),
    ("Q5 - Revenue", "A venture sold $5,000 this month. What must the owner know before using that amount as personal income?", "The business expenses and other obligations that must be paid before profit is available.", ["The color of the business logo.", "How many social-media likes the venture received.", "Whether the owner enjoyed the work."], "Correct. Revenue is not the same as personal income or profit.", "Subtract business expenses before reasoning about money available to the owner."),
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
            f"Duplicate quizzes named {QUIZ_TITLE!r}: {[entry['id'] for entry in matches]}"
        )
    quiz = matches[0] if matches else None
    data = {"quiz[title]": QUIZ_TITLE, "quiz[description]": "<p>Ungraded practice. Retry and use the feedback before finalizing the portfolio.</p>", "quiz[quiz_type]": "practice_quiz", "quiz[published]": "false", "quiz[allowed_attempts]": "-1", "quiz[show_correct_answers]": "true", "quiz[shuffle_answers]": "false"}
    quiz = await api(client, "PUT" if quiz else "POST", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}" if quiz else f"/courses/{COURSE_ID}/quizzes", data=data)
    expected = [spec[0] for spec in QUESTIONS]
    existing = await prepare_quiz_questions(client, quiz["id"], set(expected))
    for position, (name, question_text, correct, wrong, correct_comment, incorrect_comment) in enumerate(QUESTIONS, 1):
        found = next((entry for entry in existing if entry.get("question_name") == name), None)
        payload = {"question": {"question_name": name, "question_text": question_text, "question_type": "multiple_choice_question", "position": position, "points_possible": 1, "correct_comments": correct_comment, "incorrect_comments": incorrect_comment, "answers": [{"answer_text": correct, "answer_weight": 100}] + [{"answer_text": answer, "answer_weight": 0} for answer in wrong]}}
        path = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        await api(client, "PUT" if found else "POST", path, json=payload)
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
    found = next((item for item in items if item.get("type") == kind and ((kind == "SubHeader" and item.get("title") == title) or (kind == "Page" and item.get("page_url") == key) or (kind in ("Assignment", "Quiz") and item.get("content_id") == key))), None)
    if found:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module_id}/items/{found['id']}", data={"module_item[title]": title, "module_item[published]": "false"})
    data = {"module_item[type]": kind, "module_item[title]": title, "module_item[published]": "false"}
    if kind == "Page":
        data["module_item[page_url]"] = key
    elif kind in ("Assignment", "Quiz"):
        data["module_item[content_id]"] = key
    return await api(client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data=data)


def file_link(file_id, label):
    return f'<a href="/courses/{COURSE_ID}/files/{file_id}/preview" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">{label}</a>'


def image_tag(file_id, alt, max_width=700):
    return f'<img src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" loading="lazy" style="display:block;width:100%;max-width:{max_width}px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'


def step(number, title, body):
    return f'<h3 style="color:#5a2d91;border-bottom:3px solid #d9c9ed">{number}. {title}</h3>{body}'


def flow(color, title, text):
    return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0 0 6px;color:{color}">{title}</h4>{text}</div>'


async def main():
    preflight()
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        await canvas_preflight(client)
        module = await ensure_module(client)
        support = "course files/CCR Materials/3SW/Wk6"
        support_folder = await ensure_folder(client, support)
        names = {
            "OPPORTUNITY": "3sw-wk6-entrepreneurship-opportunity-guide.pdf",
            "IDEA": "3sw-wk6-million-dollar-idea-support-packet.pdf",
            "VENTURE": "3sw-wk6-venture-brief-and-pitch-record.pdf",
            "COST": "3sw-wk6-dallas-county-living-cost-guide.pdf",
            "BUDGET": "3sw-wk6-budget-and-scholarship-plan.pdf",
            "RUBRIC": "3sw-wk6-entrepreneurship-portfolio-rubric.pdf",
        }
        files = {key: await upload(client, ROOT / "docs/resources/worksheets" / name, support) for key, name in names.items()}

        visuals, folders = {}, {}
        selected_visuals = {
            1: [
                "fyf-business-opener.jpg",
                "fyf-irving-business-programs.jpg",
                "fyf-irving-business-context.jpg",
            ],
            2: ["fyf-million-dollar-idea-problem.jpg", "fyf-million-dollar-idea-sprint.jpg"],
            3: ["fyf-million-dollar-idea-test.jpg", "fyf-million-dollar-idea-call.jpg"],
        }
        for day, day_names in selected_visuals.items():
            folder_path = f"course files/CCR Materials/3SW/Wk6/Day {day} Visuals"
            folders[day], visuals[day] = await ensure_folder(client, folder_path), {}
            for name in day_names:
                visuals[day][name] = await upload(client, ASSETS / f"day{day}" / name, folder_path)

        support_folder, support_file_count = await lock_folder_files(
            client, support_folder
        )
        folder_file_counts = {}
        for day, folder in folders.items():
            folders[day], folder_file_counts[day] = await lock_folder_files(
                client, folder
            )

        quiz = await upsert_quiz(client)
        assignment_description = f'<p>This private, unpublished portfolio is a teacher-approved recovery or replacement route, not a third automatic Major. Submit the individual evidence as a file, text response, or approved audio response. Group participation supports the work, but the evidence profile uses the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">16-point rubric</a> and never depends on another student’s attendance or speaking.</p>'
        portfolio = await upsert_assignment(client, PORTFOLIO_TITLE, assignment_description)
        quiz_url = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        portfolio_url = f"/courses/{COURSE_ID}/assignments/{portfolio['id']}"

        contracts = {
            1: {
                "TOPIC": "Business Opportunities",
                "OBJECTIVE": "Students will define entrepreneurship and identify opportunities in several fields, including one field of personal interest.",
                "TEKS": "d(3)(I)",
                "DOL": "Completed Entrepreneurship Opportunity Guide.",
                "I_CAN": "define entrepreneurship and identify one opportunity in a field I care about.",
                "SHOW": "complete the Entrepreneurship Opportunity Guide with a problem, customer, offer, and owner responsibility.",
            },
            2: {
                "TOPIC": "Idea Generation",
                "OBJECTIVE": "Students will write a clear problem statement, generate at least 10 possible business ideas, and select two using visible criteria.",
                "TEKS": "d(3)(I)",
                "DOL": "A problem statement, at least 10 ideas, two screened ideas with reasons, and one dropped-idea reason on FYF pp. 234-235 or the matching support pages.",
                "I_CAN": "turn one problem into at least 10 possible business ideas and screen the strongest two.",
                "SHOW": "complete FYF pp. 234-235 or the matching support pages with a problem, idea sprint, top two, and one dropped idea.",
            },
            3: {
                "TOPIC": "Idea Testing",
                "OBJECTIVE": "Students will compare two ideas using three tests and make an evidence-based Move Forward, Needs Work, or Abandon It decision.",
                "TEKS": "d(3)(I)",
                "DOL": "Completed stress test and 6-8 sentence decision.",
                "I_CAN": "stress-test two ideas and make a decision that uses a strength, risk, and specific evidence.",
                "SHOW": "complete all three tests for both ideas and write a 6-8 sentence Move Forward, Needs Work, or Abandon It decision.",
            },
            4: {
                "TOPIC": "Venture Pitch",
                "OBJECTIVE": "Students will build a clear venture brief, communicate the evidence in a short pitch, and connect a visible action to a professional characteristic.",
                "TEKS": "d(3)(I), d(4)(F)",
                "DOL": "Group brief plus each student’s speaking/written record, one peer note, and work-ethic response.",
                "I_CAN": "communicate a venture clearly and explain how one action shows a professional quality.",
                "SHOW": "complete the group brief and my individual pitch record, evidence note, and owner-and-employee work-ethic response.",
            },
            5: {
                "TOPIC": "Personal Budget",
                "OBJECTIVE": "Students will revise a personal budget so expenses do not exceed income, distinguish business revenue from personal income, and explain one evidence-based lifestyle decision.",
                "TEKS": "d(3)(I), d(5)(D)",
                "DOL": "Personal Budget and Decision Plan with balanced totals, source labels, and revenue explanation.",
                "I_CAN": "balance a monthly budget, keep the source labels attached, and explain one evidence-based lifestyle decision.",
                "SHOW": "submit the balanced budget, revenue explanation, and decision reflection.",
            },
        }

        student = {
            1: {"TITLE": "Find an Entrepreneurship Opportunity", "PURPOSE": "Connect a real problem or customer need to a possible business and an owner responsibility.", "TODAY": "<ul><li>define entrepreneurship;</li><li>compare opportunities in several fields;</li><li>choose one field you care about.</li></ul>", "READY": f'<p>Open {file_link(files["OPPORTUNITY"]["id"], "the Entrepreneurship Opportunity Guide")}.</p>', "MEDIA": image_tag(visuals[1]["fyf-business-opener.jpg"]["id"], "Find Your Future Business, Marketing, and Finance opener and Be the Decision Maker prompt"), "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> entrepreneur = person who organizes a business · customer = person who may choose the offer · responsibility = work the owner must manage.</p><p><strong>Use this frame:</strong> People who ___ need ___, so a business could ___. The owner would need to ___.</p></div>', "STEPS": step(1, "Make the business decision", "<p>Choose advertise, hire, or buy equipment. Name one fact you need before deciding.</p>") + step(2, "Read five examples", "<p>For each example, find the problem, offer, and owner responsibility.</p>") + step(3, "Create four opportunities", "<p>Use four different fields. A business name alone is not enough.</p>") + step(4, "Choose one to investigate", "<p>Name one fact you know and one question to answer before spending money.</p>"), "EXIT": "<p>Name one field, one problem, and the first question an owner should answer.</p>", "DONE": "<ul><li>definition in your own words;</li><li>four complete opportunity rows;</li><li>one personal-interest choice;</li><li>one fact and one open question.</li></ul>", "SUPPORT": "<p>entrepreneur = emprendedor/a · customer = cliente · responsibility = responsabilidad. Oral rehearsal and bilingual drafting are equal planning routes.</p>", "FALLBACK": "<p>The guide and embedded opener are the complete route. H&amp;L is optional; no screenshot or favorite count is required.</p>"},
            2: {"TITLE": "Spot a Problem and Run an Idea Sprint", "PURPOSE": "Generate many possible solutions before choosing the two ideas with the strongest evidence.", "TODAY": "<ul><li>write a clear problem statement;</li><li>generate at least 10 ideas in five minutes;</li><li>screen the best two.</li></ul>", "READY": f'<p>Use FYF pp. 234-235 by default. Use {student_copy_link(2, "the support and catch-up packet")} only when the workbook is unavailable or the enlarged scaffold is needed; do not complete both.</p>', "MEDIA": image_tag(visuals[2]["fyf-million-dollar-idea-problem.jpg"]["id"], "Find Your Future Million Dollar Idea problem statement page") + image_tag(visuals[2]["fyf-million-dollar-idea-sprint.jpg"]["id"], "Find Your Future rapid idea generation and top-two screening page"), "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> problem = what is happening and why it matters · first version = the smallest testable version · customer choice = why someone may use it.</p><p><strong>Use this frame:</strong> ___ experiences ___, which matters because ___. A first version could ___.</p></div>', "STEPS": step(1, "Name the problem", "<p>Write what is happening, who experiences it, and why it matters.</p>") + step(2, "Sprint for five minutes", "<p>Write short phrases. Do not judge, erase, or improve ideas until time ends.</p>") + step(3, "Screen the list", "<p>Check problem fit, realistic first version, and whether someone would use it.</p>") + step(4, "Develop the top two", "<p>Give a separate reason for each test. Name one dropped idea and why it failed.</p>"), "EXIT": "<p>What evidence separated your strongest idea from one you dropped?</p>", "DONE": "<ul><li>clear problem statement;</li><li>10-12 ideas;</li><li>two selected ideas;</li><li>three screening reasons for each;</li><li>one dropped-idea reason.</li></ul>", "SUPPORT": "<p>Use the problem menu. Short phrases may be English, Spanish, or both during the sprint. Final reasons can be rehearsed aloud before writing.</p>", "FALLBACK": "<p>The four-page packet is the full no-workbook or independent route. No partner or platform is required.</p>"},
            3: {"TITLE": "Stress-Test Two Ideas and Decide", "PURPOSE": "Use three tests to decide whether an idea should move forward, change, or stop for now.", "TODAY": "<ul><li>test both ideas;</li><li>name one strength and risk;</li><li>write an evidence-based call.</li></ul>", "READY": f'<p>Continue on FYF pp. 236-237 when you used the workbook yesterday. Continue {student_copy_link(3, "the support packet")} only when that was your Day 2 route.</p>', "MEDIA": image_tag(visuals[3]["fyf-million-dollar-idea-test.jpg"]["id"], "Find Your Future two-idea stress-test page") + image_tag(visuals[3]["fyf-million-dollar-idea-call.jpg"]["id"], "Find Your Future Make the Call and group comparison page"), "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Three tests:</strong> problem fit · customer choice · build challenge.</p><p><strong>Use this frame:</strong> I chose ___ because ___. Its strongest evidence is ___. Its biggest risk is ___. Therefore, my call is ___.</p></div>', "STEPS": step(1, "Test problem fit", "<p>Explain how well each idea solves the exact problem.</p>") + step(2, "Test customer choice", "<p>Explain why someone might choose each idea over another option.</p>") + step(3, "Test the build", "<p>Name the biggest challenge for a first version.</p>") + step(4, "Make the call", "<p>Write 6-8 sentences: Move Forward, Needs Work, or Abandon It. Any verdict can earn full credit.</p>") + step(5, "Check the evidence", f'<p><a href="{quiz_url}">Open the ungraded Entrepreneurship Evidence Check</a>. Retry and use the feedback.</p>'), "EXIT": "<p>Which test separated the ideas most clearly, and why did it matter?</p>", "DONE": "<ul><li>both ideas tested three ways;</li><li>biggest risk for each;</li><li>supported call with strength and risk;</li><li>practice check reviewed.</li></ul>", "SUPPORT": "<p>fit = ajuste · customer = cliente · challenge = desafío · evidence = evidencia. Use one question at a time, oral rehearsal, or speech-to-text.</p>", "FALLBACK": "<p>Continue the same work surface you used on Day 2. Replace the small-group compare with a written comparison.</p>"},
            4: {"TITLE": "Build and Pitch the Venture Brief", "PURPOSE": "Turn the tested idea into a short, clear explanation and show professional responsibility through your own actions.", "TODAY": "<ul><li>complete six venture sections;</li><li>prepare one speaking or written job;</li><li>give one evidence-based Star and Wish;</li><li>explain a work-ethic action.</li></ul>", "READY": f'<p>Open {file_link(files["VENTURE"]["id"], "the Venture Brief and Individual Pitch Record")} and {file_link(files["RUBRIC"]["id"], "the recovery evidence rubric")}.</p><p><strong>Printing:</strong> pages 1-2 are one copy per team; pages 3-4 are one copy per student. The full file is the digital and absence route.</p>', "MEDIA": "", "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Pitch jobs:</strong> problem · offer · customer choice · challenge · evidence · first-version needs.</p><p><strong>Use these frames:</strong> Our evidence shows ___. A customer may choose this because ___. I showed ___ when I ___; that matters to owners and employees because ___.</p></div>', "STEPS": step(1, "Build the brief", "<p>Problem, offer, customer choice, challenge, call, and first-version needs.</p>") + step(2, "Prepare your evidence", "<p>Write the two points you must say and one likely question. Live, recorded, private, and written routes use the same evidence.</p>") + step(3, "Pitch for 90 seconds", "<p>Listen for the problem, offer, and evidence. The audience records one specific Star and Wish.</p>") + step(4, "Name a professional action", "<p>Choose integrity, preparation, dedication, perseverance, or reliability. Explain how your action matters for owners and employees.</p>"), "EXIT": "<p>What action made your group more ready, accurate, or reliable today?</p>", "DONE": "<ul><li>six-section group brief;</li><li>individual speaking or written record;</li><li>one evidence-based peer note;</li><li>owner-and-employee work-ethic comparison.</li></ul>", "SUPPORT": "<p>pitch = presentación · evidence = evidencia · integrity = integridad · reliability = confiabilidad. Use the written or recorded route when live presentation is not the best access route.</p>", "FALLBACK": "<p>Use your own strongest idea if a group is unavailable. You may present privately, record, or submit the written record. No class vote or public post is required.</p>"},
            5: {"TITLE": "Build, Test, and Revise a Personal Budget", "PURPOSE": "Use one dated Dallas County scenario to build, test, revise, and explain a personal budget.", "TODAY": "<ul><li>build and total a first budget;</li><li>revise one lifestyle choice;</li><li>explain the revised plan and revenue difference.</li></ul>", "READY": f'<p>Open {file_link(files["COST"]["id"], "the Dallas County Living-Cost Guide")} and {file_link(files["BUDGET"]["id"], "the Personal Budget and Decision Plan")}.</p><p><strong>Printing:</strong> print the budget plan once per assigned paper student.</p>', "MEDIA": "", "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Source labels:</strong> Dallas County · one adult/no children · updated February 15, 2026 · living-cost estimate.</p><p><strong>Word bank:</strong> income = money available · expense = money spent · revenue = all business sales · profit = revenue minus business expenses · tradeoff = a choice with a benefit and cost.</p><p><strong>Use this frame:</strong> My revised budget works because ___. Revenue is not personal income because ___.</p></div>', "STEPS": step(1, "Read all four labels", "<p>Dallas County · one adult/no children · updated February 15, 2026 · living-cost estimate.</p>") + step(2, "Build the first budget", "<p>Start with $3,450 monthly after-tax income. Enter every category and total the first plan.</p>") + step(3, "Revise and test", "<p>Make one realistic lifestyle choice. Build a revised budget at or below $3,450 and calculate the percentage used by the two largest categories.</p>") + step(4, "Explain the decision", "<p>Name the choice, one difficult-to-change expense, one flexible expense, and why business revenue is not personal income.</p>") + step(5, "Submit and store Entry 3", f'<p><a href="{portfolio_url}">Open the private recovery Portfolio Assignment</a> only when your teacher assigns it as recovery or replacement evidence. Otherwise, submit the budget as directed. Copy five short phrases into Evidence Log Entry 3; keep the log with you.</p>'), "EXIT": "<p>Which lifestyle choice changed your revised budget most, and what fact would you verify before using this plan for a real household?</p>", "DONE": "<ul><li>first and revised totals with the four source labels;</li><li>revised total at or below $3,450 plus percentage check;</li><li>revenue explanation, decision reflection, and Entry 3 stored privately.</li></ul>", "SUPPORT": "<p>budget = presupuesto · income = ingreso · expense = gasto · revenue = ingresos del negocio · tradeoff = compensación. Use a calculator, read-aloud, chunked table, or oral rehearsal.</p>", "FALLBACK": "<p>Use the fixed cost guide and the paper or Canvas budget plan your teacher assigned. If the Evidence Log is missing, save five short phrases in the CCE notebook or teacher-designated digital folder.</p>"},
        }

        student[1].update(
            {
                "READY": (
                    f'<p>Open {student_copy_link(1, "the two-page Entrepreneurship Opportunity Guide")}. '
                    "Default: write on one printed copy and return it to your teacher at the end of class. "
                    "If your teacher already posted a private digital annotation route, you may type or annotate "
                    "in the same guide and submit it there.</p>"
                ),
                "MEDIA": (
                    image_tag(
                        visuals[1]["fyf-business-opener.jpg"]["id"],
                        "Find Your Future Business, Marketing, and Finance opener and Be the Decision Maker prompt",
                    )
                    + image_tag(
                        visuals[1]["fyf-irving-business-programs.jpg"]["id"],
                        "Find Your Future Irving ISD Business, Marketing, and Finance programs and program spotlight, page 252",
                    )
                    + image_tag(
                        visuals[1]["fyf-irving-business-context.jpg"]["id"],
                        "Find Your Future Irving ISD business program examples and career-organization context, page 253",
                    )
                ),
                "STEPS": (
                    step(
                        1,
                        "Make the business decision",
                        "<p>Open your <em>Find Your Future</em> workbook to p. 221.</p><p>Choose advertise, hire, or buy equipment. Name one fact you need before deciding.</p>",
                    )
                    + step(
                        2,
                        "Scan local context and read five examples",
                        "<p>Open your workbook to pp. 252-253 and use the Irving ISD program pages as curriculum context. Then, for each guide example, find the problem, offer, and owner responsibility.</p>",
                    )
                    + step(
                        3,
                        "Create four opportunities",
                        "<p>Use four different fields. A business name alone is not enough.</p>",
                    )
                    + step(
                        4,
                        "Choose one to investigate",
                        "<p>Name one fact you know and one question to answer before spending money.</p>",
                    )
                ),
                "FALLBACK": (
                    "<p>The guide and three embedded FYF pages are the complete route. "
                    "FYF p. 254 and H&amp;L cluster exploration are optional; no screenshot, "
                    "favorite count, or platform response is required.</p>"
                ),
            }
        )
        student[2].update(
            {
                "FALLBACK": (
                    "<p>The four-page packet is the full no-workbook or independent route. "
                    "Use one route, not both; no partner or platform is required.</p>"
                )
            }
        )
        student[3].update(
            {
                "FALLBACK": (
                    "<p>Continue the same work surface you used on Day 2. If Day 2 evidence is missing, "
                    "compare these two fixed ideas: a checkout charging station and classroom delivery "
                    "of charged power banks. Replace the small-group compare with a written comparison.</p>"
                )
            }
        )
        student[4].update(
            {
                "READY": (
                    f'<p>Open {student_copy_link(4, "the Venture Brief and Individual Pitch Record")} '
                    f'and {file_link(files["RUBRIC"]["id"], "the recovery evidence rubric")}.</p>'
                    "<p><strong>Teams:</strong> Work in a team of 3-4. Use one copy of pages 1-2 per team "
                    "and one copy of pages 3-4 per student. The full file is the digital and absence route.</p>"
                ),
                "LANGUAGE": (
                    '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0">'
                    "<p><strong>Team jobs:</strong> problem/customer lead · offer/evidence lead · "
                    "challenge/first-version lead · timekeeper/question lead. In a team of three, "
                    "combine the last two jobs.</p>"
                    "<p><strong>Use these frames:</strong> Our evidence shows ___. A customer may choose "
                    "this because ___. I showed ___ when I ___; that matters to owners and employees "
                    "because ___.</p></div>"
                ),
                "STEPS": (
                    step(
                        1,
                        "Build the brief",
                        "<p>Use the Day 3 idea your team can defend with evidence, from your <em>Find Your Future</em> workbook pp. 234-237. Complete the problem, offer, customer choice, challenge, call, and first-version needs.</p>",
                    )
                    + step(
                        2,
                        "Prepare your evidence",
                        "<p>Write the two points you must say and one likely question. Live, recorded, private, and written routes use the same evidence.</p>",
                    )
                    + step(
                        3,
                        "Pitch for 90 seconds",
                        "<p>Listen for the problem, offer, and evidence. The audience records one specific Star and Wish.</p>",
                    )
                    + step(
                        4,
                        "Name a professional action",
                        "<p>Choose integrity, preparation, dedication, perseverance, or reliability. Explain how your action matters for owners and employees.</p>",
                    )
                ),
            }
        )
        student[5].update(
            {
                "READY": (
                    f'<p>Open {file_link(files["COST"]["id"], "the Dallas County Living-Cost Guide")}, '
                    f'{student_copy_link(5, "the Personal Budget and Decision Plan")}.</p>'
                    "<p><strong>Materials:</strong> one budget copy per assigned paper student; "
                    "one cost guide and calculator per pair.</p>"
                    "<p><strong>Evidence Log:</strong> open Entry 3 from your CCE binder or teacher-designated "
                    "digital folder. Keep it with you; it is not another submission.</p>"
                ),
                "EXIT": (
                    "<p><strong>Decision and Entry 3:</strong> Name the lifestyle choice that changed the revised "
                    "budget most and one fact you would verify for a real household. Copy five short phrases "
                    "from the revised plan into Entry 3. "
                    "If the log is missing, record the phrases in your CCE notebook or teacher-designated "
                    "digital folder and transfer them later. Do not reconstruct earlier work.</p>"
                ),
                "FALLBACK": student[5]["FALLBACK"]
                + "<p>A missing Evidence Log does not require a second submission. Save the five short phrases "
                "in your CCE notebook or teacher-designated digital folder and transfer them later.</p>",
            }
        )

        teacher = {
            1: {
                "TITLE": "What Counts as an Entrepreneurship Opportunity?",
                "SUBTITLE": "50 minutes · TEKS d(3)(I)",
                "ALERT": "<strong>Fixed evidence route.</strong> H&amp;L is optional. Students do not need exact Hat titles, unverified public-page labels, or prior-week memory.",
                "PREP": f'<ul><li>Print {file_link(files["OPPORTUNITY"]["id"], "the two-page Opportunity Guide")} once per student and collect it at the end of class. Use a private digital annotation route only if one already works.</li><li>Open the licensed FYF p. 221 image, FYF pp. 252-253 district context, and current Irving ISD High School CTE page.</li></ul>',
                "EVIDENCE": "<p>Four cross-field opportunities, a personal definition, one field of interest, one fact, and one open question. Formative.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and business decision warm-up", '''<p>Welcome students to Week 6 (Business, Marketing, Finance &amp; Entrepreneurship) and project the opening business decision prompt.</p><ul><li>Ask students: <em>“Imagine a small business owner suddenly has $2,500 in unexpected profit at the end of the month. They could spend it on advertising, hiring extra part-time help, or purchasing a piece of upgraded equipment. Which choice would you make, and what critical missing facts would you need before deciding?”</em></li><li>Collect 2-3 student perspectives: Emphasize that business decisions are never pure guesses—they require verifying current customer demand, workflow bottlenecks, and maintenance costs.</li><li>Bridge with, <em>“Entrepreneurship is not just having a cool idea or wanting to be your own boss; it is identifying real human problems, delivering a reliable solution, and taking personal ownership of daily operational risks.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-15 - Business career cluster orientation and defining entrepreneurship", '''<p>Direct students to FYF p. 221 and pp. 252-253 for the Business Cluster and district CTE overview:</p><ul><li>Define Entrepreneurship: <strong>The process of designing, launching, and running a new business venture by identifying unmet customer needs and assuming financial and operational risk.</strong></li><li>Review Irving ISD CTE pathways in Business, Marketing, and Finance (available across district comprehensive high schools and Singley Academy).</li><li>Clarify the three foundational pillars of any authentic opportunity: (1) An identifiable customer group with a specific pain point, (2) A concrete product or service offer, and (3) Documented daily owner responsibilities (bookkeeping, supply sourcing, quality control, customer communication).</li></ul>''')
                    + flow("#1f617a", "Minutes 15-27 - Analyzing authentic cross-field entrepreneurship models", '''<p>Display the Entrepreneurship Opportunity Guide and analyze four authentic ventures spanning different industries:</p><ul><li>Example 1 (Agriculture/Personal Care): Mobile pet grooming and organic coat care service.</li><li>Example 2 (Technology/Creative): Drone aerial photography for local real estate agents.</li><li>Example 3 (Hospitality/Culinary): Pop-up artisan breakfast taco catering trailer.</li><li>Example 4 (Trade/Service): Mobile bicycle repair and preventative tune-up workshop.</li><li>Deconstruct each example into its core structural components: Identified Problem, Specific Offer, Target Customer, and Owner Responsibility.</li></ul>''')
                    + flow("#e3ad19", "Minutes 27-45 - Building the four-field cross-industry opportunity inventory", '''<p>Students complete their Two-Page Opportunity Guide:</p><ul><li>Generate FOUR distinct, school-appropriate entrepreneurial ventures across four different fields (Health/Wellness, Creative Arts/Digital, Trades/Repairs, and Community/Education).</li><li>Select ONE personal-interest venture to explore in depth: draft a clear problem statement, an offer description, and identify TWO primary owner responsibilities.</li><li>Formulate ONE concrete, unanswered investigation question to ask an industry professional.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 32): Ensure students name four different industry fields rather than four slight variations of the same business.<br>• Lap 2 (Minute 40): Verify owner responsibilities detail daily operational tasks (inventory, sanitation, scheduling) rather than just 'making profit.'</li></ul>''')
                    + flow("#1f617a", "Minutes 45-50 - DOL check and workspace reset", '''<p>Students record their personal venture problem and investigation question on their exit card (or Canvas).</p><ul><li><strong>Safe Trim:</strong> Skip oral group presentations; fiercely protect the 4 cross-field ventures, target problem statement, owner responsibilities, and 5-minute workspace reset.</li></ul>''')
                ),
                "MONITOR": "<p>Full evidence connects problem/customer, offer, and owner responsibility. Accept any school-appropriate field. A store name or “make money” alone is not enough.</p>",
                "RESOURCES": '<p>FYF p. 221 and pp. 252-253 are embedded; FYF p. 254/H&amp;L is optional. Current district cross-check: <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte">Irving ISD High School CTE</a>. Treat workbook district names as curriculum context.</p>',
                "SUPPORT": "<p>Use the fixed example table and one sentence frame. Allow oral rehearsal or bilingual drafting.</p>",
                "FALLBACK": "<p>The guide is the full independent route. No H&amp;L screenshot or favorite count.</p>",
            },
            2: {
                "TITLE": "Spot a Problem and Generate Ideas",
                "SUBTITLE": "50 minutes · TEKS d(3)(I)",
                "ALERT": "<strong>The sprint measures quantity.</strong> Students get full credit for imperfect or strange ideas; screening happens after the timer.",
                "PREP": f'<ul><li>Default to one FYF workbook per student, pp. 234-235. Post or print {file_link(files["IDEA"]["id"], "the support packet")} only for students without the workbook or needing the enlarged scaffold; do not assign both.</li><li>Open a visible five-minute timer.</li></ul>',
                "EVIDENCE": "<p>Problem statement, 10-12 ideas, top two with three reasons each, and one dropped-idea reason. Formative.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and complaint-to-problem transformation warm-up", '''<p>Welcome students, seat them with FYF pp. 234-235, and project the problem-framing prompt.</p><ul><li>Ask students: <em>“Every day, people complain about things: 'The school hallway is too crowded,' 'My phone charger cord always frays,' or 'It's impossible to find healthy snacks after practice.' How does an entrepreneur turn an annoying complaint into a solvable business opportunity?”</em></li><li>Collect 2-3 student examples: A complaint blames circumstances; an entrepreneurial problem statement defines who suffers, what barrier exists, and why fixing it creates economic value.</li><li>Bridge with, <em>“Great businesses do not start with products—they start with problems. Today we run a rapid-fire divergent ideation sprint on FYF pp. 234-235.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-13 - Authoring the core customer problem statement (FYF p. 234)", '''<p>Students frame an authentic customer problem statement on FYF p. 234:</p><ul><li>Structure: <strong>[Target Customer Demographic]</strong> experiences difficulty when <strong>[Specific Operational Barrier / Pain Point]</strong> because <strong>[Underlying Cause]</strong>, which results in <strong>[Negative Consequence / Frustration]</strong>.</li><li>Students select from the Problem Menu or define a school/community issue.</li><li>Model: <em>“Busy middle school athletes experience dehydration and energy crashes after practice because existing vending machines only sell sugary soda, resulting in sluggish performance and fatigue.”</em></li></ul>''')
                    + flow("#1f617a", "Minutes 13-20 - High-volume divergent ideation sprint (5-minute timer)", '''<p>Launch the 5-Minute Divergent Ideation Sprint:</p><ul><li>Set a visible 5-minute countdown timer on the main display.</li><li>Sprint Rules: Prioritize QUANTITY over perfection. Students record 10-12 distinct, creative ideas that could address the target problem. No self-censoring; weird, futuristic, and wildly creative solutions are fully valid during divergent ideation.</li><li><strong>Active Monitoring Checkpoint (Minute 17):</strong> If students stall at 3-4 ideas, prompt: <em>“What is the lowest-cost version? What is the mobile/delivery version? What is the automated digital version?”</em></li></ul>''')
                    + flow("#e3ad19", "Minutes 20-45 - Idea screening, top-two selection &amp; dropped-idea defense (FYF p. 235)", '''<p>Students transition from divergent ideation to convergent analysis on FYF p. 235:</p><ul><li>Apply three screening filters: (1) Problem Alignment (Does it solve the core issue?), (2) Feasibility / MVP Potential (Can a middle school or high school entrepreneur build a working first version?), and (3) Customer Willingness to Use/Pay.</li><li>Narrow the list to the TOP TWO strongest venture concepts: Detail THREE distinct operational reasons supporting each idea.</li><li>Defend ONE dropped idea: Explicitly explain WHY an eliminated idea was rejected (e.g., prohibitive startup costs, regulatory hurdles, or weak customer demand).</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 28): Check that students provide distinct evidence-based justifications for each of the top two ideas.<br>• Lap 2 (Minute 38): Ensure the dropped-idea rationale points to a genuine operational barrier.</li></ul>''')
                    + flow("#1f617a", "Minutes 45-50 - Submit ideation records and workspace reset", '''<p>Verify completion of FYF pp. 234-235 and collect support packets.</p><ul><li><strong>Safe Trim:</strong> Skip whole-class idea pitching; protect the problem statement, 10-idea sprint, top-2 comparative reasoning, dropped-idea defense, and 5-minute reset.</li></ul>''')
                ),
                "MONITOR": "<p>At minute 3 of the sprint, students should have six ideas. Repair with: Who has the problem? What is the smallest version? What do customers do now?</p>",
                "RESOURCES": "<p>Licensed FYF pp. 234-235 are embedded. The support packet is the equal no-workbook, enlarged-scaffold, or absence route; students use one route, not both.</p>",
                "SUPPORT": "<p>Use the eight-item problem menu. Short bilingual phrases count during the sprint; score reasoning after screening.</p>",
                "FALLBACK": "<p>No partner or platform is required. Do not use real classmates’ private information in a problem scenario.</p>",
            },
            3: {
                "TITLE": "Stress-Test and Make the Call",
                "SUBTITLE": "50 minutes · TEKS d(3)(I)",
                "ALERT": "<strong>Abandon It can earn full credit.</strong> Score the comparison and reasoning, not whether the venture moves forward.",
                "PREP": f'<ul><li>Default to FYF pp. 236-237. Post {file_link(files["IDEA"]["id"], "the support packet")} only for students already using that route.</li><li>Open the unpublished practice Quiz.</li><li>Tell students the printed workbook skips Step 6; nothing is missing.</li></ul>',
                "EVIDENCE": "<p>Two-idea stress test, risks, 6-8 sentence call, and practice check. Recommended core portfolio evidence.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and idea stress-testing warm-up", '''<p>Welcome students, seat them with FYF pp. 236-237, and project the venture evaluation prompt.</p><ul><li>Ask students: <em>“Think about your favorite idea from yesterday. What is the single biggest operational, financial, or human risk that could cause that business to completely fail in its first 90 days? What evidence would prove you should walk away?”</em></li><li>Collect 2-3 student thoughts: Emphasize that in professional venture capital and lean startup development, recognizing when to pivot or abandon an idea saves months of wasted capital.</li><li>Bridge with, <em>“An entrepreneur who ignores risks goes bankrupt. Today we stress-test our top two ideas across three brutal operational filters and make the executive call: Move Forward, Pivot, or Abandon.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-25 - The three-filter venture stress test (FYF pp. 236-237)", '''<p>Students stress-test Idea A and Idea B sequentially through three evaluation gates:</p><ul><li>Gate 1 (Problem-Solution Fit): Will target customers actually adopt this over their existing habit or current free alternative?</li><li>Gate 2 (Market &amp; Customer Choice): Is the market large enough, and does the offer provide a clear, defensible differentiator?</li><li>Gate 3 (Execution &amp; Minimum Viable Product Challenge): What is the most difficult technical, legal, or supply-chain hurdle required to build Version 1?</li><li>Students assign objective numerical or qualitative ratings and record specific risk notes for BOTH ideas.</li><li>(Note: Remind students the printed FYF workbook intentionally skips step 6; all required fields are accounted for).</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 15): Ensure students evaluate BOTH ideas thoroughly, not just their pre-selected favorite.</li></ul>''')
                    + flow("#1f617a", "Minutes 25-37 - Authoring the executive verdict (6-8 sentence call)", '''<p>Students author their formal 6-8 sentence Executive Decision on FYF p. 237:</p><ul><li>Sentence 1: State the final verdict (Proceed with Idea A, Proceed with Idea B, Pivot to a Modified Model, or Abandon Both). Note: 'Abandon' can earn full credit if supported with evidence!</li><li>Sentence 2-3: Detail the winning idea's primary competitive advantage and how it passed the three stress-test gates.</li><li>Sentence 4-5: Acknowledge the single largest operational or financial risk and propose a concrete risk mitigation strategy.</li><li>Sentence 6-8: Define the immediate, low-cost prototype test (e.g., a customer interest survey or sample batch) to run before spending significant money.</li></ul>''')
                    + flow("#e3ad19", "Minutes 37-45 - Rapid peer critique &amp; practice check", '''<p>Elbow partners conduct a 90-second Stress-Test Review:</p><ul><li>Partner checks: Did the author acknowledge a genuine risk, or did they fall into the 'everyone will love it' trap?</li><li>Students complete the 5-minute Canvas Practice Check (immediate formative feedback).</li></ul>''')
                    + flow("#1f617a", "Minutes 45-50 - Submit executive decision and workspace reset", '''<p>Collect FYF evidence and reset classroom tables.</p><ul><li><strong>Safe Trim:</strong> Skip oral peer share; fiercely protect the 2-idea stress test, 6-8 sentence executive call, risk acknowledgment, and 5-minute reset.</li></ul>''')
                ),
                "MONITOR": "<p>Reject “everyone will like it” as evidence. Strong work compares both ideas, acknowledges a real risk, and connects the call to one test. Quiz key is encoded with feedback.</p>",
                "RESOURCES": "<p>Licensed FYF pp. 236-237 are embedded. The support packet is the continuation route for students already using it. The practice Quiz checks bounded misconceptions; it does not replace the written decision.</p>",
                "SUPPORT": "<p>Release one question at a time. Use sentence frames, oral rehearsal, speech-to-text, or the fixed table.</p>",
                "FALLBACK": "<p>Replace group compare with a written comparison. If Day 2 evidence is missing, use the fixed charging-station versus delivered-power-bank pair.</p>",
            },
            4: {
                "TITLE": "Venture Brief and Pitch",
                "SUBTITLE": "50 minutes · TEKS d(3)(I), d(4)(F)",
                "ALERT": "<strong>Presentation math is protected.</strong> Eight groups fit at 90 seconds plus a 30-second question and 30-second transition. Use recordings or a private written route when the number of groups cannot fit.",
                "PREP": f'<ul><li>Post {file_link(files["VENTURE"]["id"], "the Venture Brief")}, {file_link(files["RUBRIC"]["id"], "the recovery rubric")}, and the 90-second timer.</li><li>Print pages 1-2 once per team and pages 3-4 once per student; do not print four pages per student.</li><li>Prepare live, private, recorded, and written routes.</li></ul>',
                "EVIDENCE": "<p>Six-section group brief plus each student’s speaking/written record, one evidence-based peer note, and work-ethic action. Individual evidence prevents group attendance from determining the evidence profile.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and executive pitch launch warm-up", '''<p>Welcome students, assemble them with their pitch teams, and project the pitch criteria prompt.</p><ul><li>Ask students: <em>“In professional venture competitions and investor boardrooms, founders have only 90 seconds to convince stakeholders. What three elements must be communicated instantly to earn credibility?”</em></li><li>Collect 2-3 student thoughts: The clear problem, the specific differentiated solution, and evidence of market feasibility.</li><li>Bridge with, <em>“Today is Venture Pitch Day! Every team delivers a structured 90-second pitch, fields critical audience questions, and documents individual workplace ethics actions.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-20 - Finalizing the Six-Section Venture Brief &amp; role rehearsal", '''<p>Teams finalize their Venture Brief (Pages 1-2) and divide speaking responsibilities:</p><ul><li>Section 1: Venture Name, Tagline &amp; Target Industry.</li><li>Section 2: The Core Customer Problem &amp; Market Need.</li><li>Section 3: The Differentiated Offer (Product/Service Details).</li><li>Section 4: Key Operational Hurdle &amp; Risk Mitigation.</li><li>Section 5: MVP Prototype Plan &amp; Low-Cost Verification Test.</li><li>Section 6: Local High School CTE Connection (Singley Academy / District CTE alignment).</li><li>Assign explicit team speaking roles: Speaker 1 (Problem/Customer), Speaker 2 (Offer/Differentiation), Speaker 3 (Risks/Prototype), Speaker 4 (Q&amp;A Lead / Timekeeper).</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 12): Halt decorative poster/slide design at minute 9; force students to rehearse verbal delivery with the 90-second timer.</li></ul>''')
                    + flow("#1f617a", "Minutes 20-44 - Professional 90-second venture pitch rotation", '''<p>Conduct the structured Venture Pitch Rotation:</p><ul><li>Each team receives strictly 90 seconds to pitch, followed by 30 seconds for ONE targeted audience inquiry and 30 seconds for transition (Total: 2.5 minutes per team).</li><li>Audience Responsibility: Every student records peer feedback on their Individual Pitch Record (Page 3-4): noting ONE specific factual strength and ONE operational question.</li><li>Scoring Integrity: Teachers score observable preparation, factual clarity, risk honesty, and collaborative teamwork. DO NOT score acting, popularity, artistic slides, or run a class popularity vote!</li><li>Alternate Route: Any team unable to fit live delivers their pitch via private recording or written submission.</li></ul>''')
                    + flow("#e3ad19", "Minutes 44-50 - Individual work-ethic reflection and workspace reset", '''<p>Students independently complete their individual exit reflection on Page 4:</p><ul><li>Prompt: <em>“Identify ONE concrete professional work-ethic behavior (e.g., proactive communication, meeting deadlines, thorough preparation, admitting mistakes) that distinguishes high-performing entrepreneurs and employees. How will you apply this behavior this semester?”</em></li><li>Collect Team Briefs and Individual Records. Reset classroom furniture.</li><li><strong>Safe Trim:</strong> Cap pitches strictly at 90 seconds; eliminate class deliberation votes; fiercely protect the 6-section brief, individual peer records, work-ethic reflection, and 5-minute reset.</li></ul>''')
                ),
                "MONITOR": "<p>Score observable preparation, accuracy, follow-through, revision, or honesty. Do not score confidence, accent, popularity, artwork, or whether the venture receives class approval. Skip the class vote.</p>",
                "RESOURCES": "<p>The CCE brief traces every section to the student’s Million Dollar Idea evidence. Canva or Adobe Express is optional; a plain brief is equal.</p>",
                "SUPPORT": "<p>Allow live, private, recorded, or written presentation. Use assigned roles and private self-review when peer feedback is unavailable.</p>",
                "FALLBACK": "<p>A student without a group uses their own idea. No public posting of ideas is required.</p>",
            },
            5: {
                "TITLE": "Build, Test, and Revise a Personal Budget",
                "SUBTITLE": "50 minutes · TEKS d(3)(I), d(5)(D)",
                "ALERT": "<strong>Use the fixed Dallas County scenario.</strong> Protect the first budget, revised budget, percentage check, revenue distinction, and decision reflection. No Xello task or screenshot is required.",
                "PREP": f'<ul><li>Post {file_link(files["COST"]["id"], "the dated cost guide")}, {file_link(files["BUDGET"]["id"], "the budget plan")}, and {file_link(files["RUBRIC"]["id"], "the recovery rubric")}.</li><li>Print one budget plan per assigned paper student and supply one cost guide and calculator per pair.</li><li>Ask students to open Entry 3 of the CCE Six-Weeks Evidence Log. Do not collect it.</li></ul>',
                "EVIDENCE": "<p>Balanced first and revised budgets, percentage calculation, revenue distinction, and decision reflection. The 16-point portfolio is recovery or replacement evidence only; it is not a third automatic Major.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and financial reality warm-up", '''<p>Welcome students, seat them with the Dallas County Living Cost Guide, and project the financial literacy prompt.</p><ul><li>Ask students: <em>“When high school graduates enter the workforce and see a $4,000 monthly gross paycheck, why is it dangerous to assume they have $4,000 to spend on rent, food, and fun?”</em></li><li>Collect 2-3 student thoughts: Payroll taxes (FICA, federal withholding), mandatory fixed expenses (rent, utilities, insurance), and the difference between business revenue and personal take-home pay.</li><li>Bridge with, <em>“Financial independence requires mastering cash flow. Today we build, test, and balance a realistic personal monthly budget using authentic Dallas County economic data.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-20 - Dallas County economic data audit and initial budget build", '''<p>Examine the Dallas County Living Cost Guide (based on MIT Living Wage &amp; Dallas College benchmarks):</p><ul><li>Review baseline monthly living expenses for a single adult in Dallas County: Housing/Rent ($1,250-$1,450), Food/Groceries ($350-$450), Transportation/Car/Insurance ($550-$700), Healthcare ($250-$350), Utilities/Internet ($200-$300), and Miscellaneous/Personal ($150-$250).</li><li>Total monthly living threshold: approximately $3,450 net monthly take-home pay.</li><li>Students enter baseline category estimates into Budget Column 1 (Initial Plan) and sum the initial total.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 15): Verify students copy sourced monthly figures accurately with full dollar-and-cent labels.</li></ul>''')
                    + flow("#1f617a", "Minutes 20-35 - Budget stress-testing, lifestyle choices &amp; balancing sprint", '''<p>Students test and balance their personal budget under financial constraints:</p><ul><li>Introduce the Scenario Limit: Net monthly earned income is capped at $3,450.</li><li>Students adjust flexible categories in Column 2 (Revised Plan): choosing between private apartment vs. shared roommate living; public transit vs. vehicle ownership; home cooking vs. restaurant dining.</li><li>Calculate Housing Percentage: <code>(Monthly Housing Cost ÷ Total Budget) × 100</code>. Enforce the financial benchmark: Housing should not exceed 35% of total take-home pay!</li><li>Crucial Entrepreneurial Distinction: Students explain the difference between Business Gross Revenue (total money taken in by a company) and Personal Net Income (owner's take-home pay after business expenses and taxes).</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 2 (Minute 28): Confirm the revised budget totals $3,450 or less and housing percentage is calculated correctly.</li></ul>''')
                    + flow("#e3ad19", "Minutes 35-45 - Financial decision reflection &amp; Six-Weeks Log Entry 3", '''<p>Students synthesize their financial plan through a written reflection:</p><ul><li>Explain ONE trade-off made to achieve a balanced budget (e.g., eliminating subscription services or living with a roommate to afford reliable transportation).</li><li>Identify ONE variable expense that requires weekly monitoring to avoid deficit.</li><li>Complete Entry 3 of the CCE Six-Weeks Evidence Log in their CCE binder or digital portfolio (recording their final venture concept, budget balance, and personal reflection).</li></ul>''')
                    + flow("#606c76", "Minutes 45-50 - Submit budget portfolio and Six-Weeks reset", '''<p>Collect Budget and Scholarship Plans. Congratulate students on completing the entire Third Six-Weeks (3SW) Curriculum!</p><ul><li><strong>Safe Trim:</strong> Skip whole-class budget sharing; fiercely protect the balanced revised budget, housing percentage calculation, revenue distinction, reflection, and workspace reset.</li></ul>''')
                ),
                "MONITOR": "<p>Lap 1 checks the four source labels and first total. Lap 2 checks a revised total of $3,450 or less plus the percentage calculation and revenue/personal-income distinction. At minute 40, every student should have a decision reflection and one fact to verify. Trim whole-group sharing before any budget reasoning or the five-minute submission window.</p>",
                "RESOURCES": '<p><a href="https://livingwage.mit.edu/counties/48113">MIT Dallas County source</a> · <a href="https://www.dallascollege.edu/research/reports/living-wages-community-college/">Dallas College 2026 brief</a></p>',
                "SUPPORT": "<p>Use calculator, read-aloud, chunked table, speech-to-text, or audio. The print packet gives separate cells for calculations and full-width lines for each explanation.</p>",
                "FALLBACK": "<p>The fixed cost guide and paper or Canvas budget plan are the complete routes. H&amp;L salary is not required.</p>",
            },
        }

        teacher[1].update(
            {
                "ALERT": (
                    "<strong>Fixed evidence route.</strong> H&amp;L is optional. Use FYF pp. 252-253 "
                    "for district curriculum context. Students do not need exact Hat titles, unverified "
                    "public-page labels, or prior-week memory."
                ),
                "PREP": (
                    f'<ul><li>Print {file_link(files["OPPORTUNITY"]["id"], "the two-page Opportunity Guide")} '
                    "once per student and collect it at the end of class. If an established private digital "
                    "annotation route already works, post the same file as an equal option; do not configure a "
                    "new destination for this lesson.</li>"
                    "<li>Open the licensed FYF p. 221 opener and FYF pp. 252-253 district-context images.</li>"
                    '<li>Open the <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte">current Irving ISD High School CTE page</a> for teacher verification only.</li>'
                    "<li>FYF p. 254 and H&amp;L are optional; do not require a platform response.</li></ul>"
                ),
                "MONITOR": (
                    "<p>Use two laps during the cross-field list. At minute 6, check that each row names a "
                    "need and offer. At minute 12, check for four different fields and one owner responsibility "
                    "per row. If a quarter of the class has four versions of the same business, model one "
                    "contrasting field, then restart. Trim the optional whole-group share before the completed "
                    "guide or close.</p>"
                ),
                "RESOURCES": (
                    '<p>Licensed FYF p. 221 and pp. 252-253 are embedded. FYF p. 254 is the optional H&amp;L '
                    'App Exploration. Current district cross-check: <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte">Irving ISD High School CTE</a>. '
                    "Treat workbook district names as curriculum context; do not make students reconcile sources.</p>"
                ),
            }
        )
        teacher[2].update(
            {
                "PREP": (
                    f'<ul><li>Default: one FYF workbook per student, pp. 234-235. Post or print '
                    f'{file_link(files["IDEA"]["id"], "the four-page support packet")} only for students '
                    "without the workbook or needing the enlarged scaffold; do not assign both.</li>"
                    "<li>Open a visible five-minute timer.</li></ul>"
                ),
                "MONITOR": (
                    "<p>Lap 1 at sprint minute 3: students should have about six ideas. Prompt with: Who has "
                    "the problem? What is the smallest version? What do customers do now? Lap 2 during screening: "
                    "require a different reason for each test and one dropped-idea reason. If fewer than half reach "
                    "six ideas, add two silent sprint minutes. Trim partner sharing before the top-two evidence.</p>"
                ),
            }
        )
        teacher[3].update(
            {
                "PREP": (
                    f'<ul><li>Default: continue FYF pp. 236-237. Post '
                    f'{file_link(files["IDEA"]["id"], "the support packet")} only for students already using '
                    "that route.</li><li>Open the unpublished practice Quiz.</li>"
                    "<li>Tell students the printed workbook skips Step 6; nothing is missing.</li></ul>"
                ),
                "MONITOR": (
                    "<p>Release one test at a time. Lap 1 checks that both ideas receive separate evidence; lap 2 "
                    "checks one real risk and a verdict tied to the deciding test. If Day 2 evidence is missing, "
                    "use the fixed charging-station versus delivered-power-bank pair in the support packet. "
                    "Trim the group compare before the written call or five-minute practice check.</p>"
                ),
                "FALLBACK": (
                    "<p>Replace group compare with a written comparison. The fixed fallback pair prevents an "
                    "absence from becoming a new teacher-created example.</p>"
                ),
            }
        )
        teacher[4].update(
            {
                "PREP": (
                    f'<ul><li>Post {file_link(files["VENTURE"]["id"], "the Venture Brief")}, '
                    f'{file_link(files["RUBRIC"]["id"], "the recovery rubric")}, and the 90-second timer.</li>'
                    "<li>Build teams of 3-4. Assign problem/customer lead, offer/evidence lead, challenge/first-version "
                    "lead, and timekeeper/question lead; combine the last two in a team of three.</li>"
                    "<li>Print pages 1-2 once per team and pages 3-4 once per student.</li>"
                    "<li>Prepare live, private, recorded, and written routes plus one collection location for the "
                    "team brief and each student record.</li></ul>"
                ),
                "MONITOR": (
                    "<p>Lap 1 at build minute 6 checks six brief sections and Day 3 evidence. Lap 2 at minute 11 "
                    "checks that every student has two speaking/written points and one likely question. Stop design "
                    "work at minute 9. If there are more than eight teams or five minutes are lost, move the "
                    "remaining pitches to recorded, private, or written evidence. Trim a second audience question, "
                    "never the individual pitch record or work-ethic close.</p>"
                ),
            }
        )
        teacher[5].update(
            {
                "PREP": (
                    f'<ul><li>Post {file_link(files["COST"]["id"], "the dated cost guide")}, '
                    f'{file_link(files["BUDGET"]["id"], "the budget plan")}, '
                    f'{file_link(files["RUBRIC"]["id"], "the recovery rubric")}.</li>'
                    "<li>Print one budget plan per assigned paper student and supply one cost guide and calculator per pair.</li>"
                    "<li>Ask students to open Entry 3 of the CCE Six-Weeks Evidence Log from their CCE binder "
                    "or teacher-designated digital folder. Do not collect it.</li></ul>"
                ),
                "MONITOR": (
                    "<p>Lap 1 checks the four source labels and first total. Lap 2 checks a revised total of $3,450 "
                    "or less plus the percentage calculation and revenue/personal-income distinction. At minute 40, "
                    "check that every student has a decision reflection and one fact to verify. At minute 47, check "
                    "that Entry 3 copies the five short phrases already visible in "
                    "the revised plan. If the log is missing, students save those phrases in their CCE notebook or "
                    "teacher-designated digital folder and transfer them later. Do not collect or score the log. "
                    "Trim whole-group sharing before budget reasoning or the submission window.</p>"
                ),
            }
        )

        day_names = {1: "Entrepreneurship Opportunities", 2: "Problem and Idea Sprint", 3: "Stress-Test and Decide", 4: "Venture Brief and Pitch", 5: "Build and Revise a Personal Budget"}
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 3SW Wk6 Day {day} - {day_names[day]}"
            student_page = await upsert_page(client, student_title, render("3sw-wk6-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, **contracts[day], **student[day]}))
            teacher_title = f"TEACHER: 3SW Wk6 Day {day} Facilitator Guide"
            teacher_page = await upsert_page(client, teacher_title, render("3sw-wk6-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **contracts[day], **teacher[day]}))
            await upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            pages[day] = {"teacher": teacher_page, "student": student_page}
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title)]
            if day == 3:
                await upsert_item(client, module["id"], "Quiz", quiz["id"], QUIZ_TITLE)
                order.append(("Quiz", quiz["id"], QUIZ_TITLE))
            if day == 5:
                await upsert_item(client, module["id"], "Assignment", portfolio["id"], PORTFOLIO_TITLE)
                order.append(("Assignment", portfolio["id"], PORTFOLIO_TITLE))

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

        items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
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
                data={
                    "module_item[position]": position,
                    "module_item[title]": title,
                    "module_item[published]": "false",
                },
            )

        final_items = sorted(
            await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items"),
            key=lambda entry: entry.get("position") or 0,
        )
        module = await api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        quiz = await api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
        portfolio = await api(
            client, "GET", f"/courses/{COURSE_ID}/assignments/{portfolio['id']}"
        )
        if module.get("published"):
            raise RuntimeError("3SW Wk6 module unexpectedly published")
        if (
            quiz.get("published")
            or quiz.get("quiz_type") != "practice_quiz"
            or int(quiz.get("allowed_attempts") or 0) != -1
        ):
            raise RuntimeError("3SW Wk6 practice quiz invariant failed")
        if (
            portfolio.get("published")
            or float(portfolio.get("points_possible") or 0) != 0
            or portfolio.get("grading_type") != "not_graded"
            or not portfolio.get("omit_from_final_grade")
        ):
            raise RuntimeError("3SW Wk6 recovery portfolio invariant failed")
        published_pages = [
            value["url"]
            for pair in pages.values()
            for value in pair.values()
            if value.get("published")
        ]
        if published_pages:
            raise RuntimeError(f"Published 3SW Wk6 pages remain: {published_pages}")
        if not support_folder.get("locked") or any(
            not folder.get("locked") for folder in folders.values()
        ):
            raise RuntimeError("One or more 3SW Wk6 Canvas folders remain unlocked")
        if len(final_items) != 17 or len(final_items) != len(order):
            raise RuntimeError(
                f"Expected exactly 17 3SW Wk6 module items; found {len(final_items)}"
            )
        published_items = [
            entry.get("title") for entry in final_items if entry.get("published")
        ]
        if published_items:
            raise RuntimeError(
                f"Published 3SW Wk6 module items remain: {published_items}"
            )
        for position, ((kind, key, title), item) in enumerate(
            zip(order, final_items), 1
        ):
            if (
                item.get("position") != position
                or item.get("title") != title
                or not matches_item(item, kind, key)
            ):
                raise RuntimeError(f"3SW Wk6 module order mismatch at {position}")
        print(json.dumps({
            "module": {"id": module["id"], "published": module["published"]},
            "quiz": {"id": quiz["id"], "published": quiz.get("published"), "quiz_type": quiz.get("quiz_type"), "allowed_attempts": quiz.get("allowed_attempts")},
            "portfolio": {"id": portfolio["id"], "published": portfolio.get("published"), "grading_type": portfolio.get("grading_type"), "points_possible": portfolio.get("points_possible"), "omit_from_final_grade": portfolio.get("omit_from_final_grade"), "submission_types": portfolio.get("submission_types")},
            "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"], "file_count": support_file_count},
            "folders": {str(day): {"id": folder["id"], "locked": folder["locked"], "file_count": folder_file_counts[day]} for day, folder in folders.items()},
            "files": {key: value["id"] for key, value in files.items()},
            "pages": {str(day): {kind: {"url": value["url"], "published": value["published"]} for kind, value in pair.items()} for day, pair in pages.items()},
            "items": [{"id": item["id"], "position": item["position"], "title": item["title"], "type": item["type"], "page_url": item.get("page_url")} for item in final_items],
        }, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
