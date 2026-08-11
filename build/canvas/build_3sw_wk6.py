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
MODULE_NAME = "3SW Wk6: Build, Test, and Pitch a Business Idea"
QUIZ_TITLE = "PRACTICE: Entrepreneurship Evidence Check"
PORTFOLIO_TITLE = "RECOVERY: Entrepreneurship Portfolio"
LEGACY_PORTFOLIO_TITLE = "DRAFT: Entrepreneurship Portfolio"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/3sw/wk6"
XELLO = ROOT / "cce-curriculum/resources/xello-licensed/scholarships"


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
        XELLO / "scholarships-guide-students.pdf",
        XELLO / "scholarships-guide-students-spanish.pdf",
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
    return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'


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
        files["XELLO_EN"] = await upload(client, XELLO / "scholarships-guide-students.pdf", support)
        files["XELLO_ES"] = await upload(client, XELLO / "scholarships-guide-students-spanish.pdf", support)

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
                "OBJECTIVE": "Students will revise a personal budget so expenses do not exceed income, distinguish business revenue from personal income, and complete the required Xello Scholarship profile.",
                "TEKS": "d(3)(I), d(5)(D)",
                "DOL": "Personal Budget and Xello Scholarship Plan plus Xello Completion Standards report.",
                "I_CAN": "balance a monthly budget, keep the source labels attached, and complete my private Xello Scholarship profile.",
                "SHOW": "submit the balanced budget and revenue explanation while the teacher verifies Xello completion in the report.",
            },
        }

        student = {
            1: {"TITLE": "Find an Entrepreneurship Opportunity", "PURPOSE": "Connect a real problem or customer need to a possible business and an owner responsibility.", "TODAY": "<ul><li>define entrepreneurship;</li><li>compare opportunities in several fields;</li><li>choose one field you care about.</li></ul>", "READY": f'<p>Open {file_link(files["OPPORTUNITY"]["id"], "the Entrepreneurship Opportunity Guide")}.</p>', "MEDIA": image_tag(visuals[1]["fyf-business-opener.jpg"]["id"], "Find Your Future Business, Marketing, and Finance opener and Be the Decision Maker prompt"), "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> entrepreneur = person who organizes a business · customer = person who may choose the offer · responsibility = work the owner must manage.</p><p><strong>Use this frame:</strong> People who ___ need ___, so a business could ___. The owner would need to ___.</p></div>', "STEPS": step(1, "Make the business decision", "<p>Choose advertise, hire, or buy equipment. Name one fact you need before deciding.</p>") + step(2, "Read five examples", "<p>For each example, find the problem, offer, and owner responsibility.</p>") + step(3, "Create four opportunities", "<p>Use four different fields. A business name alone is not enough.</p>") + step(4, "Choose one to investigate", "<p>Name one fact you know and one question to answer before spending money.</p>"), "EXIT": "<p>Name one field, one problem, and the first question an owner should answer.</p>", "DONE": "<ul><li>definition in your own words;</li><li>four complete opportunity rows;</li><li>one personal-interest choice;</li><li>one fact and one open question.</li></ul>", "SUPPORT": "<p>entrepreneur = emprendedor/a · customer = cliente · responsibility = responsabilidad. Oral rehearsal and bilingual drafting are equal planning routes.</p>", "FALLBACK": "<p>The guide and embedded opener are the complete route. H&amp;L is optional; no screenshot or favorite count is required.</p>"},
            2: {"TITLE": "Spot a Problem and Run an Idea Sprint", "PURPOSE": "Generate many possible solutions before choosing the two ideas with the strongest evidence.", "TODAY": "<ul><li>write a clear problem statement;</li><li>generate at least 10 ideas in five minutes;</li><li>screen the best two.</li></ul>", "READY": f'<p>Use FYF pp. 234-235 by default. Use {file_link(files["IDEA"]["id"], "the support and catch-up packet")} only when the workbook is unavailable or the enlarged scaffold is needed; do not complete both.</p>', "MEDIA": image_tag(visuals[2]["fyf-million-dollar-idea-problem.jpg"]["id"], "Find Your Future Million Dollar Idea problem statement page") + image_tag(visuals[2]["fyf-million-dollar-idea-sprint.jpg"]["id"], "Find Your Future rapid idea generation and top-two screening page"), "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> problem = what is happening and why it matters · first version = the smallest testable version · customer choice = why someone may use it.</p><p><strong>Use this frame:</strong> ___ experiences ___, which matters because ___. A first version could ___.</p></div>', "STEPS": step(1, "Name the problem", "<p>Write what is happening, who experiences it, and why it matters.</p>") + step(2, "Sprint for five minutes", "<p>Write short phrases. Do not judge, erase, or improve ideas until time ends.</p>") + step(3, "Screen the list", "<p>Check problem fit, realistic first version, and whether someone would use it.</p>") + step(4, "Develop the top two", "<p>Give a separate reason for each test. Name one dropped idea and why it failed.</p>"), "EXIT": "<p>What evidence separated your strongest idea from one you dropped?</p>", "DONE": "<ul><li>clear problem statement;</li><li>10-12 ideas;</li><li>two selected ideas;</li><li>three screening reasons for each;</li><li>one dropped-idea reason.</li></ul>", "SUPPORT": "<p>Use the problem menu. Short phrases may be English, Spanish, or both during the sprint. Final reasons can be rehearsed aloud before writing.</p>", "FALLBACK": "<p>The four-page packet is the full no-workbook or independent route. No partner or platform is required.</p>"},
            3: {"TITLE": "Stress-Test Two Ideas and Decide", "PURPOSE": "Use three tests to decide whether an idea should move forward, change, or stop for now.", "TODAY": "<ul><li>test both ideas;</li><li>name one strength and risk;</li><li>write an evidence-based call.</li></ul>", "READY": f'<p>Continue on FYF pp. 236-237 when you used the workbook yesterday. Continue {file_link(files["IDEA"]["id"], "the support packet")} only when that was your Day 2 route.</p>', "MEDIA": image_tag(visuals[3]["fyf-million-dollar-idea-test.jpg"]["id"], "Find Your Future two-idea stress-test page") + image_tag(visuals[3]["fyf-million-dollar-idea-call.jpg"]["id"], "Find Your Future Make the Call and group comparison page"), "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Three tests:</strong> problem fit · customer choice · build challenge.</p><p><strong>Use this frame:</strong> I chose ___ because ___. Its strongest evidence is ___. Its biggest risk is ___. Therefore, my call is ___.</p></div>', "STEPS": step(1, "Test problem fit", "<p>Explain how well each idea solves the exact problem.</p>") + step(2, "Test customer choice", "<p>Explain why someone might choose each idea over another option.</p>") + step(3, "Test the build", "<p>Name the biggest challenge for a first version.</p>") + step(4, "Make the call", "<p>Write 6-8 sentences: Move Forward, Needs Work, or Abandon It. Any verdict can earn full credit.</p>") + step(5, "Check the evidence", f'<p><a href="{quiz_url}">Open the ungraded Entrepreneurship Evidence Check</a>. Retry and use the feedback.</p>'), "EXIT": "<p>Which test separated the ideas most clearly, and why did it matter?</p>", "DONE": "<ul><li>both ideas tested three ways;</li><li>biggest risk for each;</li><li>supported call with strength and risk;</li><li>practice check reviewed.</li></ul>", "SUPPORT": "<p>fit = ajuste · customer = cliente · challenge = desafío · evidence = evidencia. Use one question at a time, oral rehearsal, or speech-to-text.</p>", "FALLBACK": "<p>Continue the same work surface you used on Day 2. Replace the small-group compare with a written comparison.</p>"},
            4: {"TITLE": "Build and Pitch the Venture Brief", "PURPOSE": "Turn the tested idea into a short, clear explanation and show professional responsibility through your own actions.", "TODAY": "<ul><li>complete six venture sections;</li><li>prepare one speaking or written job;</li><li>give one evidence-based Star and Wish;</li><li>explain a work-ethic action.</li></ul>", "READY": f'<p>Open {file_link(files["VENTURE"]["id"], "the Venture Brief and Individual Pitch Record")} and {file_link(files["RUBRIC"]["id"], "the recovery evidence rubric")}.</p><p><strong>Printing:</strong> pages 1-2 are one copy per team; pages 3-4 are one copy per student. The full file is the digital and absence route.</p>', "MEDIA": "", "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Pitch jobs:</strong> problem · offer · customer choice · challenge · evidence · first-version needs.</p><p><strong>Use these frames:</strong> Our evidence shows ___. A customer may choose this because ___. I showed ___ when I ___; that matters to owners and employees because ___.</p></div>', "STEPS": step(1, "Build the brief", "<p>Problem, offer, customer choice, challenge, call, and first-version needs.</p>") + step(2, "Prepare your evidence", "<p>Write the two points you must say and one likely question. Live, recorded, private, and written routes use the same evidence.</p>") + step(3, "Pitch for 90 seconds", "<p>Listen for the problem, offer, and evidence. The audience records one specific Star and Wish.</p>") + step(4, "Name a professional action", "<p>Choose integrity, preparation, dedication, perseverance, or reliability. Explain how your action matters for owners and employees.</p>"), "EXIT": "<p>What action made your group more ready, accurate, or reliable today?</p>", "DONE": "<ul><li>six-section group brief;</li><li>individual speaking or written record;</li><li>one evidence-based peer note;</li><li>owner-and-employee work-ethic comparison.</li></ul>", "SUPPORT": "<p>pitch = presentación · evidence = evidencia · integrity = integridad · reliability = confiabilidad. Use the written or recorded route when live presentation is not the best access route.</p>", "FALLBACK": "<p>Use your own strongest idea if a group is unavailable. You may present privately, record, or submit the written record. No class vote or public post is required.</p>"},
            5: {"TITLE": "Build a Budget and Complete Scholarship Profile", "PURPOSE": "Revise a monthly budget using one dated scenario, then complete the required private Xello matching profile.", "TODAY": "<ul><li>balance a personal budget;</li><li>separate business revenue from personal income;</li><li>complete Xello Scholarship profile.</li></ul>", "READY": f'<p>Open {file_link(files["COST"]["id"], "the Dallas County Living-Cost Guide")}, {file_link(files["BUDGET"]["id"], "the Budget and Scholarship Plan")}, and {file_link(files["XELLO_EN"]["id"], "Xello’s student Scholarships Guide")} (<span lang="es">{file_link(files["XELLO_ES"]["id"], "guía en español")}</span>).</p><p><strong>Printing:</strong> print budget pages 1-2. Page 3 is only the no-device Xello directions and catch-up check.</p>', "MEDIA": '<details style="border:1px solid #d2d2d2;border-radius:8px;padding:12px 16px;margin:18px 0"><summary style="font-weight:700;cursor:pointer">Optional 2:02 Xello scholarship video</summary><div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;margin:12px 0"><iframe src="https://www.youtube-nocookie.com/embed/CPI2tVXPDRs" title="Xello: Discover your scholarship options, 2 minutes 2 seconds" loading="lazy" allowfullscreen style="position:absolute;top:0;left:0;width:100%;height:100%;border:0"></iframe></div><p>The linked guide and visible steps contain the required directions.</p></details>', "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Source labels:</strong> Dallas County · one adult/no children · updated February 15, 2026 · living-cost estimate.</p><p><strong>Word bank:</strong> income = money available · expense = money spent · revenue = all business sales · profit = revenue minus business expenses.</p><p><strong>Use this frame:</strong> My revised budget works because ___. Revenue is not personal income because ___.</p></div>', "STEPS": step(1, "Read all four labels", "<p>Dallas County · one adult/no children · updated February 15, 2026 · living-cost estimate.</p>") + step(2, "Build and revise the budget", "<p>Start with $3,450 monthly after-tax income. Total both budgets and keep the revised total at or below the available amount.</p>") + step(3, "Explain the money", "<p>Calculate the two largest categories and explain why business revenue is not personal income.</p>") + step(4, "Complete Scholarship profile", "<p>Open Scholarships from the top menu or College Planning, then open the profile or profile booster. Answer honestly, including “I don’t know.” Do not copy private answers into Canvas.</p>") + step(5, "Submit privately", f'<p><a href="{portfolio_url}">Open the private recovery Portfolio Assignment</a> only when your teacher assigns it as recovery or replacement evidence. Otherwise, submit the budget as directed.</p>'), "EXIT": "<p>How can a scholarship change a future budget without becoming guaranteed income?</p>", "DONE": "<ul><li>first and revised budget totals;</li><li>revised total at or below $3,450;</li><li>source labels and revenue explanation;</li><li>Xello profile complete or catch-up recorded;</li><li>no private profile answers submitted.</li></ul>", "SUPPORT": "<p>budget = presupuesto · income = ingreso · expense = gasto · scholarship = beca. Use a calculator, read-aloud, chunked table, or oral rehearsal.</p>", "FALLBACK": "<p>If Xello fails, finish the budget, then join the supervised catch-up list. Paper does not count as Xello completion. The official PDF is the text alternative to the video.</p>"},
        }

        student[1].update(
            {
                "READY": (
                    f'<p>Open {file_link(files["OPPORTUNITY"]["id"], "the two-page Entrepreneurship Opportunity Guide")}. '
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
                        "<p>Choose advertise, hire, or buy equipment. Name one fact you need before deciding.</p>",
                    )
                    + step(
                        2,
                        "Scan local context and read five examples",
                        "<p>Use the embedded FYF program pages as curriculum context. Then, for each guide example, find the problem, offer, and owner responsibility.</p>",
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
                    f'<p>Open {file_link(files["VENTURE"]["id"], "the Venture Brief and Individual Pitch Record")} '
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
                        "<p>Use the Day 3 idea your team can defend with evidence. Complete the problem, offer, customer choice, challenge, call, and first-version needs.</p>",
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
                    f'{file_link(files["BUDGET"]["id"], "the Budget and Scholarship Plan")}, and '
                    f'{file_link(files["XELLO_EN"]["id"], "Xello’s student Scholarships Guide")} '
                    f'(<span lang="es">{file_link(files["XELLO_ES"]["id"], "guía en español")}</span>).</p>'
                    "<p><strong>Materials:</strong> one budget copy (pp. 1-2) and one device per student; "
                    "one cost guide and calculator per pair. Page 3 is only the no-device Xello directions "
                    "and catch-up check.</p>"
                )
            }
        )

        teacher = {
            1: {"TITLE": "What Counts as an Entrepreneurship Opportunity?", "SUBTITLE": "50 minutes · TEKS d(3)(I)", "ALERT": "<strong>Fixed evidence route.</strong> H&amp;L is optional. Treat FYF pp. 252-253 as the district curriculum context; do not make exact Hat titles, unverified public-page labels, or prior-week memory load-bearing.", "PREP": f'<ul><li>Print {file_link(files["OPPORTUNITY"]["id"], "the two-page Opportunity Guide")} once per student and collect it at the end of class. Use a private digital annotation route only if one already works.</li><li>Open the licensed FYF p. 221 image, FYF pp. 252-253 district context, and current Irving ISD High School CTE page.</li></ul>', "EVIDENCE": "<p>Four cross-field opportunities, a personal definition, one field of interest, one fact, and one open question. Formative.</p>", "FLOW": flow("#5a2d91", "Decision warm-up · 5", "Choose advertise, hire, or equipment; name missing evidence.") + flow("#4a9d2f", "Cluster and district context · 10", "Define entrepreneurship; scan FYF pp. 252-253 as curriculum context.") + flow("#1f617a", "Read examples · 12", "Problem, offer, owner responsibility.") + flow("#e3ad19", "Build the list · 18", "Four fields and one personal-interest choice.") + flow("#1f617a", "Close · 5", "Field, problem, first question."), "MONITOR": "<p>Full evidence connects problem/customer, offer, and owner responsibility. Accept any school-appropriate field. A store name or “make money” alone is not enough.</p>", "RESOURCES": '<p>FYF p. 221 and pp. 252-253 are embedded; FYF p. 254/H&amp;L is optional. Current district cross-check: <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte">Irving ISD High School CTE</a>. Treat workbook district names as curriculum context.</p>', "SUPPORT": "<p>Use the fixed example table and one sentence frame. Allow oral rehearsal or bilingual drafting.</p>", "FALLBACK": "<p>The guide is the full independent route. No H&amp;L screenshot or favorite count.</p>"},
            2: {"TITLE": "Spot a Problem and Generate Ideas", "SUBTITLE": "50 minutes · TEKS d(3)(I)", "ALERT": "<strong>The sprint measures quantity.</strong> Students get full credit for imperfect or strange ideas; screening happens after the timer.", "PREP": f'<ul><li>Default to one FYF workbook per student, pp. 234-235. Post or print {file_link(files["IDEA"]["id"], "the support packet")} only for students without the workbook or needing the enlarged scaffold; do not assign both.</li><li>Open a visible five-minute timer.</li></ul>', "EVIDENCE": "<p>Problem statement, 10-12 ideas, top two with three reasons each, and one dropped-idea reason. Formative.</p>", "FLOW": flow("#5a2d91", "Notice problems · 5", "Turn a complaint into a problem statement.") + flow("#4a9d2f", "Write the problem · 8", "What, who, and why it matters.") + flow("#1f617a", "Idea sprint · 7", "One-minute setup plus five-minute sprint.") + flow("#e3ad19", "Screen · 10", "Problem fit, realistic first version, customer use.") + flow("#4a9d2f", "Develop · 15", "Top two and one dropped idea.") + flow("#1f617a", "Close · 5", "Evidence that separated two ideas."), "MONITOR": "<p>At minute 3 of the sprint, students should have six ideas. Repair with: Who has the problem? What is the smallest version? What do customers do now?</p>", "RESOURCES": "<p>Licensed FYF pp. 234-235 are embedded. The support packet is the equal no-workbook, enlarged-scaffold, or absence route; students use one route, not both.</p>", "SUPPORT": "<p>Use the eight-item problem menu. Short bilingual phrases count during the sprint; score reasoning after screening.</p>", "FALLBACK": "<p>No partner or platform is required. Do not use real classmates’ private information in a problem scenario.</p>"},
            3: {"TITLE": "Stress-Test and Make the Call", "SUBTITLE": "50 minutes · TEKS d(3)(I)", "ALERT": "<strong>Abandon It can earn full credit.</strong> Score the comparison and reasoning, not whether the venture moves forward.", "PREP": f'<ul><li>Default to FYF pp. 236-237. Post {file_link(files["IDEA"]["id"], "the support packet")} only for students already using that route.</li><li>Open the unpublished practice Quiz.</li><li>Tell students the printed workbook skips Step 6; nothing is missing.</li></ul>', "EVIDENCE": "<p>Two-idea stress test, risks, 6-8 sentence call, and practice check. Recommended core portfolio evidence.</p>", "FLOW": flow("#5a2d91", "Re-enter · 5", "Current favorite and evidence that could change it.") + flow("#4a9d2f", "Stress-test · 20", "Release problem fit, customer choice, and build challenge one at a time.") + flow("#1f617a", "Make the call · 12", "Strength, risk, and deciding evidence.") + flow("#e3ad19", "Compare · 8", "45 seconds each or private written route.") + flow("#1f617a", "Practice check · 5", "Immediate feedback and retry."), "MONITOR": "<p>Reject “everyone will like it” as evidence. Strong work compares both ideas, acknowledges a real risk, and connects the call to one test. Quiz key is encoded with feedback.</p>", "RESOURCES": "<p>Licensed FYF pp. 236-237 are embedded. The support packet is the continuation route for students already using it. The practice Quiz checks bounded misconceptions; it does not replace the written decision.</p>", "SUPPORT": "<p>Release one question at a time. Use sentence frames, oral rehearsal, speech-to-text, or the fixed table.</p>", "FALLBACK": "<p>Replace group compare with a written comparison. If Day 2 evidence is missing, use the fixed charging-station versus delivered-power-bank pair.</p>"},
            4: {"TITLE": "Venture Brief and Pitch", "SUBTITLE": "50 minutes · TEKS d(3)(I), d(4)(F)", "ALERT": "<strong>Presentation math is protected.</strong> Eight groups fit at 90 seconds plus a 30-second question and 30-second transition. Use recordings or a private written route when the number of groups cannot fit.", "PREP": f'<ul><li>Post {file_link(files["VENTURE"]["id"], "the Venture Brief")}, {file_link(files["RUBRIC"]["id"], "the recovery rubric")}, and the 90-second timer.</li><li>Print pages 1-2 once per team and pages 3-4 once per student; do not print four pages per student.</li><li>Prepare live, private, recorded, and written routes.</li></ul>', "EVIDENCE": "<p>Six-section group brief plus each student’s speaking/written record, one evidence-based peer note, and work-ethic action. Individual evidence prevents group attendance from determining the evidence profile.</p>", "FLOW": flow("#5a2d91", "Launch · 5", "Clear problem, offer, evidence.") + flow("#4a9d2f", "Build and rehearse · 15", "Stop decoration at minute 9.") + flow("#1f617a", "Pitch rotation · 24", "90-second pitch, question, transition.") + flow("#e3ad19", "Individual close · 6", "Professional action for owners and employees."), "MONITOR": "<p>Score observable preparation, accuracy, follow-through, revision, or honesty. Do not score confidence, accent, popularity, artwork, or whether the venture receives class approval. Skip the class vote.</p>", "RESOURCES": "<p>The CCE brief traces every section to the student’s Million Dollar Idea evidence. Canva or Adobe Express is optional; a plain brief is equal.</p>", "SUPPORT": "<p>Allow live, private, recorded, or written presentation. Use assigned roles and private self-review when peer feedback is unavailable.</p>", "FALLBACK": "<p>A student without a group uses their own idea. No public posting of ideas is required.</p>"},
            5: {"TITLE": "Personal Budget and Xello Scholarship Profile", "SUBTITLE": "50 minutes · TEKS d(3)(I), d(5)(D)", "ALERT": "<strong>Sequence repair.</strong> Do not repeat Save careers. Protect 20 minutes for the required Grade 8 Scholarship profile and verify through the Completion Standards report.", "PREP": f'<ul><li>Post {file_link(files["COST"]["id"], "the dated cost guide")}, {file_link(files["BUDGET"]["id"], "the budget plan")}, {file_link(files["XELLO_EN"]["id"], "Xello’s English guide")}, {file_link(files["XELLO_ES"]["id"], "Xello’s Spanish guide")}, and {file_link(files["RUBRIC"]["id"], "the recovery rubric")}.</li><li>Print budget pages 1-2. Print page 3 only for the no-device Xello direction or catch-up route.</li><li>Open the Xello Completion Standards report and optional official video.</li></ul>', "EVIDENCE": "<p>Balanced revised budget, percentage calculation, revenue distinction, and Xello report completion. The 16-point portfolio is recovery or replacement evidence only; it is not a third automatic Major.</p>", "FLOW": flow("#5a2d91", "Source labels · 5", "Place, household, date, measure.") + flow("#4a9d2f", "Budget · 20", "First budget, lifestyle choice, revised budget, reasoning.") + flow("#1f617a", "Xello profile · 20", "Complete matching profile; no application required.") + flow("#e3ad19", "Submit · 5", "Budget and catch-up record; recovery portfolio only when assigned."), "MONITOR": "<p>Revised expenses must total $3,450 or less. There is no one correct lifestyle choice. Xello answers must be honest; “I don’t know” is acceptable. Do not collect private profile answers or screenshots.</p>", "RESOURCES": '<p><a href="https://livingwage.mit.edu/counties/48113">MIT Dallas County source</a> · <a href="https://www.dallascollege.edu/research/reports/living-wages-community-college/">Dallas College 2026 brief</a> · <a href="https://help.xello.world/en-us/content/Knowledge-Base/Xello-6-12/College-Planning/KB_6-12_Scholarships.htm">Xello Scholarships resources</a></p>', "SUPPORT": "<p>Use calculator, read-aloud, chunked table, speech-to-text, or audio. The print packet gives separate cells for calculations and full-width lines for each explanation.</p>", "FALLBACK": "<p>Platform failure moves to supervised Xello catch-up; paper does not count as completion. The official PDF is the video text route. H&amp;L salary is not load-bearing.</p>"},
        }

        teacher[1].update(
            {
                "ALERT": (
                    "<strong>Fixed evidence route.</strong> H&amp;L is optional. Treat FYF pp. 252-253 "
                    "as the district curriculum context; do not make exact Hat titles, unverified public-page "
                    "labels, or prior-week memory load-bearing."
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
                "FLOW": (
                    flow(
                        "#5a2d91",
                        "Decision warm-up · 5",
                        "Choose advertise, hire, or equipment; name missing evidence.",
                    )
                    + flow(
                        "#4a9d2f",
                        "Cluster and district context · 10",
                        "Define entrepreneurship; scan FYF pp. 252-253 as curriculum context.",
                    )
                    + flow(
                        "#1f617a",
                        "Read examples · 12",
                        "Problem, offer, owner responsibility.",
                    )
                    + flow(
                        "#e3ad19",
                        "Build the list · 18",
                        "Four fields and one personal-interest choice.",
                    )
                    + flow("#1f617a", "Close · 5", "Field, problem, first question.")
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
                    f'{file_link(files["XELLO_EN"]["id"], "Xello’s English guide")}, '
                    f'{file_link(files["XELLO_ES"]["id"], "Xello’s Spanish guide")}, and '
                    f'{file_link(files["RUBRIC"]["id"], "the recovery rubric")}.</li>'
                    "<li>Print budget pp. 1-2 once per student, supply one cost guide and calculator per pair, "
                    "and one device per student. Print p. 3 only for no-device directions or catch-up.</li>"
                    "<li>Open the Xello Completion Standards report and optional official video.</li></ul>"
                ),
                "MONITOR": (
                    "<p>Lap 1 checks the four source labels and first total. Lap 2 checks a revised total of $3,450 "
                    "or less plus the revenue/personal-income distinction. At the Xello transition, verify that "
                    "students can reach Scholarship matches/profile before releasing the 20-minute block. If Xello "
                    "fails, move students to the supervised catch-up list; never collect private answers or "
                    "screenshots. Trim the optional video before budget reasoning or required profile time.</p>"
                ),
            }
        )

        day_names = {1: "Entrepreneurship Opportunities", 2: "Problem and Idea Sprint", 3: "Stress-Test and Decide", 4: "Venture Brief and Pitch", 5: "Budget and Scholarship Profile"}
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
