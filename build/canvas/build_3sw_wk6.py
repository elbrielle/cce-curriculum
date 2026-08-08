"""Build the unpublished 3SW Week 6 Entrepreneurship Canvas module."""

import asyncio
import json
import mimetypes
import re
import sys
from pathlib import Path

import httpx


BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
MODULE_NAME = "3SW Wk6: Build, Test, and Pitch a Business Idea"
QUIZ_TITLE = "PRACTICE: Entrepreneurship Evidence Check"
PORTFOLIO_TITLE = "DRAFT: Entrepreneurship Portfolio"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/3sw/wk6"
XELLO = ROOT / "cce-curriculum/resources/xello-licensed/scholarships"


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
    found = next((module for module in modules if module["name"] == MODULE_NAME), None)
    if found:
        if found.get("published"):
            return await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data={"module[published]": "false"})
        return found
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
    return response.json()


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
    found = next((entry for entry in assignments if entry.get("name") == title), None)
    data = {
        "assignment[name]": title,
        "assignment[description]": description,
        "assignment[submission_types][]": ["online_upload", "online_text_entry", "media_recording"],
        "assignment[grading_type]": "not_graded",
        "assignment[points_possible]": "0",
        "assignment[published]": "false",
    }
    path = f"/courses/{COURSE_ID}/assignments/{found['id']}" if found else f"/courses/{COURSE_ID}/assignments"
    return await api(client, "PUT" if found else "POST", path, data=data)


QUESTIONS = [
    ("Q1 - Complete opportunity", "Which description is a complete entrepreneurship opportunity?", "Families wait too long for affordable event meals, so a student team proposes a mobile meal-prep service and identifies food safety and on-time delivery as owner responsibilities.", ["Start a restaurant because restaurants make money.", "Sell something online and hope people buy it.", "Choose a logo before identifying a customer or problem."], "Correct. A usable opportunity connects a problem, customer, offer, and owner responsibility.", "A business name or product alone does not show an opportunity."),
    ("Q2 - Stress-test evidence", "Which statement gives the strongest customer-choice evidence?", "Students currently borrow chargers from the office, and a low-cost locker rental would be available in the same hallway.", ["Everyone will love my idea.", "The colors look professional.", "I have wanted to build this for a long time."], "Correct. It names the current option and a specific reason a customer might choose the new one.", "Enthusiasm and appearance are not evidence of customer choice."),
    ("Q3 - Abandon it", "When can Abandon It be a strong entrepreneurial decision?", "When the evidence shows the risk or build challenge is greater than the idea's current value.", ["Only when the student did not finish the work.", "Never; entrepreneurs must keep every idea.", "Only when classmates dislike the idea."], "Correct. Stopping or changing an idea can save time and money.", "The verdict is not the score. The evidence and reasoning are."),
    ("Q4 - Living-cost label", "What does the $3,450 monthly classroom figure represent?", "A rounded Dallas County living-cost scenario for one adult with no children, based on an MIT page updated February 15, 2026.", ["Guaranteed DFW starting pay.", "Every adult's exact monthly budget.", "A salary after taxes for any career."], "Correct. Keep place, household, date, and measure attached.", "It is a planning scenario, not pay or personal tax advice."),
    ("Q5 - Revenue", "A venture sold $5,000 this month. What must the owner know before using that amount as personal income?", "The business expenses and other obligations that must be paid before profit is available.", ["The color of the business logo.", "How many social-media likes the venture received.", "Whether the owner enjoyed the work."], "Correct. Revenue is not the same as personal income or profit.", "Subtract business expenses before reasoning about money available to the owner."),
]


async def upsert_quiz(client):
    quizzes = await paged(client, f"/courses/{COURSE_ID}/quizzes")
    quiz = next((entry for entry in quizzes if entry.get("title") == QUIZ_TITLE), None)
    data = {"quiz[title]": QUIZ_TITLE, "quiz[description]": "<p>Ungraded practice. Retry and use the feedback before finalizing the portfolio.</p>", "quiz[quiz_type]": "practice_quiz", "quiz[published]": "false", "quiz[allowed_attempts]": "-1", "quiz[show_correct_answers]": "true", "quiz[shuffle_answers]": "false"}
    quiz = await api(client, "PUT" if quiz else "POST", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}" if quiz else f"/courses/{COURSE_ID}/quizzes", data=data)
    existing = await paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    for position, (name, question_text, correct, wrong, correct_comment, incorrect_comment) in enumerate(QUESTIONS, 1):
        found = next((entry for entry in existing if entry.get("question_name") == name), None)
        payload = {"question": {"question_name": name, "question_text": question_text, "question_type": "multiple_choice_question", "position": position, "points_possible": 1, "correct_comments": correct_comment, "incorrect_comments": incorrect_comment, "answers": [{"answer_text": correct, "answer_weight": 100}] + [{"answer_text": answer, "answer_weight": 0} for answer in wrong]}}
        path = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        await api(client, "PUT" if found else "POST", path, json=payload)
    return await api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


async def upsert_item(client, module_id, kind, key, title):
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    found = next((item for item in items if (kind == "SubHeader" and item.get("title") == title) or (kind == "Page" and item.get("page_url") == key) or (kind in ("Assignment", "Quiz") and item.get("content_id") == key)), None)
    if found:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module_id}/items/{found['id']}", data={"module_item[title]": title})
    data = {"module_item[type]": kind, "module_item[title]": title}
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
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
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
            1: ["fyf-business-opener.jpg"],
            2: ["fyf-million-dollar-idea-problem.jpg", "fyf-million-dollar-idea-sprint.jpg"],
            3: ["fyf-million-dollar-idea-test.jpg", "fyf-million-dollar-idea-call.jpg"],
        }
        for day, day_names in selected_visuals.items():
            folder_path = f"course files/CCR Materials/3SW/Wk6/Day {day} Visuals"
            folders[day], visuals[day] = await ensure_folder(client, folder_path), {}
            for name in day_names:
                visuals[day][name] = await upload(client, ASSETS / f"day{day}" / name, folder_path)

        quiz = await upsert_quiz(client)
        assignment_description = f'<p>Submit the individual Entrepreneurship Portfolio as a file, text response, or approved audio response. Group participation supports the work, but the individual score uses the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">16-point rubric</a>. This remains unpublished and ungraded until the live Major assignment group and 40/60 weighting are verified.</p>'
        portfolio = await upsert_assignment(client, PORTFOLIO_TITLE, assignment_description)
        quiz_url = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        portfolio_url = f"/courses/{COURSE_ID}/assignments/{portfolio['id']}"

        student = {
            1: {"TITLE": "Find an Entrepreneurship Opportunity", "PURPOSE": "Connect a real problem or customer need to a possible business and an owner responsibility.", "TODAY": "<ul><li>define entrepreneurship;</li><li>compare opportunities in several fields;</li><li>choose one field you care about.</li></ul>", "READY": f'<p>Open {file_link(files["OPPORTUNITY"]["id"], "the Entrepreneurship Opportunity Guide")}.</p>', "MEDIA": image_tag(visuals[1]["fyf-business-opener.jpg"]["id"], "Find Your Future Business, Marketing, and Finance opener and Be the Decision Maker prompt"), "STEPS": step(1, "Make the business decision", "<p>Choose advertise, hire, or buy equipment. Name one fact you need before deciding.</p>") + step(2, "Read five examples", "<p>For each example, find the problem, offer, and owner responsibility.</p>") + step(3, "Create four opportunities", "<p>Use four different fields. A business name alone is not enough.</p>") + step(4, "Choose one to investigate", "<p>Name one fact you know and one question to answer before spending money.</p>"), "EXIT": "<p>Name one field, one problem, and the first question an owner should answer.</p>", "DONE": "<ul><li>definition in your own words;</li><li>four complete opportunity rows;</li><li>one personal-interest choice;</li><li>one fact and one open question.</li></ul>", "SUPPORT": "<p>entrepreneur = emprendedor/a · customer = cliente · responsibility = responsabilidad. Use the fixed examples and sentence frame: “People who ___ need ___, so a business could ___.”</p>", "FALLBACK": "<p>The guide and embedded opener are the complete route. H&amp;L is optional; no screenshot or favorite count is required.</p>"},
            2: {"TITLE": "Spot a Problem and Run an Idea Sprint", "PURPOSE": "Generate many possible solutions before choosing the two ideas with the strongest evidence.", "TODAY": "<ul><li>write a clear problem statement;</li><li>generate at least 10 ideas in five minutes;</li><li>screen the best two.</li></ul>", "READY": f'<p>Use FYF pp. 234-235 or {file_link(files["IDEA"]["id"], "the support and catch-up packet")}.</p>', "MEDIA": image_tag(visuals[2]["fyf-million-dollar-idea-problem.jpg"]["id"], "Find Your Future Million Dollar Idea problem statement page") + image_tag(visuals[2]["fyf-million-dollar-idea-sprint.jpg"]["id"], "Find Your Future rapid idea generation and top-two screening page"), "STEPS": step(1, "Name the problem", "<p>Write what is happening, who experiences it, and why it matters.</p>") + step(2, "Sprint for five minutes", "<p>Write short phrases. Do not judge, erase, or improve ideas until time ends.</p>") + step(3, "Screen the list", "<p>Check problem fit, realistic first version, and whether someone would use it.</p>") + step(4, "Develop the top two", "<p>Give a separate reason for each test. Name one dropped idea and why it failed.</p>"), "EXIT": "<p>What evidence separated your strongest idea from one you dropped?</p>", "DONE": "<ul><li>clear problem statement;</li><li>10-12 ideas;</li><li>two selected ideas;</li><li>three screening reasons for each;</li><li>one dropped-idea reason.</li></ul>", "SUPPORT": "<p>Use the problem menu. Short phrases may be English, Spanish, or both during the sprint. Final reasons can be rehearsed aloud before writing.</p>", "FALLBACK": "<p>The four-page packet is the full paper or independent route. No partner or platform is required.</p>"},
            3: {"TITLE": "Stress-Test Two Ideas and Decide", "PURPOSE": "Use three tests to decide whether an idea should move forward, change, or stop for now.", "TODAY": "<ul><li>test both ideas;</li><li>name one strength and risk;</li><li>write an evidence-based call.</li></ul>", "READY": f'<p>Continue {file_link(files["IDEA"]["id"], "the support packet")} or FYF pp. 236-237.</p>', "MEDIA": image_tag(visuals[3]["fyf-million-dollar-idea-test.jpg"]["id"], "Find Your Future two-idea stress-test page") + image_tag(visuals[3]["fyf-million-dollar-idea-call.jpg"]["id"], "Find Your Future Make the Call and group comparison page"), "STEPS": step(1, "Test problem fit", "<p>Explain how well each idea solves the exact problem.</p>") + step(2, "Test customer choice", "<p>Explain why someone might choose each idea over another option.</p>") + step(3, "Test the build", "<p>Name the biggest challenge for a first version.</p>") + step(4, "Make the call", "<p>Write 6-8 sentences: Move Forward, Needs Work, or Abandon It. Any verdict can earn full credit.</p>") + step(5, "Check the evidence", f'<p><a href="{quiz_url}">Open the ungraded Entrepreneurship Evidence Check</a>. Retry and use the feedback.</p>'), "EXIT": "<p>Which test separated the ideas most clearly, and why did it matter?</p>", "DONE": "<ul><li>both ideas tested three ways;</li><li>biggest risk for each;</li><li>supported call with strength and risk;</li><li>practice check reviewed.</li></ul>", "SUPPORT": "<p>fit = ajuste · customer = cliente · challenge = desafío · evidence = evidencia. Use one question at a time and the sentence frames in the packet.</p>", "FALLBACK": "<p>The packet and embedded pages are the complete independent route. Replace the small-group compare with a written comparison.</p>"},
            4: {"TITLE": "Build and Pitch the Venture Brief", "PURPOSE": "Turn the tested idea into a short, clear explanation and show professional responsibility through your own actions.", "TODAY": "<ul><li>complete six venture sections;</li><li>prepare one speaking or written job;</li><li>give one evidence-based Star and Wish;</li><li>explain a work-ethic action.</li></ul>", "READY": f'<p>Open {file_link(files["VENTURE"]["id"], "the Venture Brief and Individual Pitch Record")} and {file_link(files["RUBRIC"]["id"], "the portfolio rubric")}.</p>', "MEDIA": "", "STEPS": step(1, "Build the brief", "<p>Problem, offer, customer choice, challenge, call, and first-version needs.</p>") + step(2, "Prepare your evidence", "<p>Write the two points you must say and one likely question. Live, recorded, private, and written routes use the same evidence.</p>") + step(3, "Pitch for 90 seconds", "<p>Listen for the problem, offer, and evidence. The audience records one specific Star and Wish.</p>") + step(4, "Name a professional action", "<p>Choose integrity, preparation, dedication, perseverance, or reliability. Explain how your action matters for owners and employees.</p>"), "EXIT": "<p>What action made your group more ready, accurate, or reliable today?</p>", "DONE": "<ul><li>six-section group brief;</li><li>individual speaking or written record;</li><li>one evidence-based peer note;</li><li>owner-and-employee work-ethic comparison.</li></ul>", "SUPPORT": "<p>pitch = presentación · evidence = evidencia · integrity = integridad · reliability = confiabilidad. Use the written or recorded route when live presentation is not the best access route.</p>", "FALLBACK": "<p>Use your own strongest idea if a group is unavailable. You may present privately, record, or submit the written record. No class vote or public post is required.</p>"},
            5: {"TITLE": "Build a Budget and Complete Scholarship Profile", "PURPOSE": "Revise a monthly budget using one dated scenario, then complete the required private Xello matching profile.", "TODAY": "<ul><li>balance a personal budget;</li><li>separate business revenue from personal income;</li><li>complete Xello Scholarship profile.</li></ul>", "READY": f'<p>Open {file_link(files["COST"]["id"], "the Dallas County Living-Cost Guide")}, {file_link(files["BUDGET"]["id"], "the Budget and Scholarship Plan")}, and {file_link(files["XELLO_EN"]["id"], "Xello’s student Scholarships Guide")} (<span lang="es">{file_link(files["XELLO_ES"]["id"], "guía en español")}</span>).</p>', "MEDIA": '<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;margin:18px 0"><iframe src="https://www.youtube-nocookie.com/embed/CPI2tVXPDRs" title="Xello: Discover your scholarship options, 2 minutes 2 seconds" loading="lazy" allowfullscreen style="position:absolute;top:0;left:0;width:100%;height:100%;border:0"></iframe></div><p><em>The video is optional. The linked guide and steps below contain the required directions.</em></p>', "STEPS": step(1, "Read all four labels", "<p>Dallas County · one adult/no children · updated February 15, 2026 · living-cost estimate.</p>") + step(2, "Build and revise the budget", "<p>Start with $3,450 monthly after-tax income. Total both budgets and keep the revised total at or below the available amount.</p>") + step(3, "Explain the money", "<p>Calculate the two largest categories and explain why business revenue is not personal income.</p>") + step(4, "Complete Scholarship profile", "<p>Open College Planning → Scholarships or Scholarship matches → profile or profile booster. Answer honestly, including “I don’t know.” Do not copy private answers into Canvas.</p>") + step(5, "Submit privately", f'<p><a href="{portfolio_url}">Open the draft private Portfolio Assignment</a>. Use file, text, or approved audio.</p>'), "EXIT": "<p>How can a scholarship change a future budget without becoming guaranteed income?</p>", "DONE": "<ul><li>first and revised budget totals;</li><li>revised total at or below $3,450;</li><li>source labels and revenue explanation;</li><li>Xello profile complete or catch-up recorded;</li><li>no private profile answers submitted.</li></ul>", "SUPPORT": "<p>budget = presupuesto · income = ingreso · expense = gasto · scholarship = beca. Use a calculator, read-aloud, chunked table, or oral rehearsal.</p>", "FALLBACK": "<p>If Xello fails, finish the budget and private reflection, then join the supervised catch-up list. Paper does not count as Xello completion. The official PDF is the text alternative to the video.</p>"},
        }

        teacher = {
            1: {"TITLE": "What Counts as an Entrepreneurship Opportunity?", "SUBTITLE": "50 minutes · TEKS d(3)(I)", "ALERT": "<strong>Fixed evidence route.</strong> H&amp;L is optional. Do not make exact Hat titles, old district program names, or prior-week memory load-bearing.", "PREP": f'<ul><li>Post {file_link(files["OPPORTUNITY"]["id"], "the Opportunity Guide")}.</li><li>Open the licensed FYF p. 221 image and current Irving ISD High School CTE page.</li></ul>', "EVIDENCE": "<p>Four cross-field opportunities, a personal definition, one field of interest, one fact, and one open question. Formative.</p>", "FLOW": flow("#5a2d91", "Decision warm-up · 5", "Choose advertise, hire, or equipment; name missing evidence.") + flow("#4a9d2f", "Cluster opener · 10", "Define entrepreneurship and separate idea from opportunity.") + flow("#1f617a", "Read examples · 12", "Problem, offer, owner responsibility.") + flow("#e3ad19", "Build the list · 18", "Four fields and one personal-interest choice.") + flow("#1f617a", "Close · 5", "Field, problem, first question."), "MONITOR": "<p>Full evidence connects problem/customer, offer, and owner responsibility. Accept any school-appropriate field. A store name or “make money” alone is not enough.</p>", "RESOURCES": '<p>FYF p. 221 is embedded. Current district source: <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte">Irving ISD High School CTE</a>. Treat workbook district names as historical context.</p>', "SUPPORT": "<p>Use the fixed example table and one sentence frame. Allow oral rehearsal or bilingual drafting.</p>", "FALLBACK": "<p>The guide is the full independent route. No H&amp;L screenshot or favorite count.</p>"},
            2: {"TITLE": "Spot a Problem and Generate Ideas", "SUBTITLE": "50 minutes · TEKS d(3)(I)", "ALERT": "<strong>The sprint measures quantity.</strong> Students get full credit for imperfect or strange ideas; screening happens after the timer.", "PREP": f'<ul><li>Post FYF pp. 234-235 and {file_link(files["IDEA"]["id"], "the support packet")}.</li><li>Open a visible five-minute timer.</li></ul>', "EVIDENCE": "<p>Problem statement, 10-12 ideas, top two with three reasons each, and one dropped-idea reason. Formative.</p>", "FLOW": flow("#5a2d91", "Notice problems · 5", "Turn a complaint into a problem statement.") + flow("#4a9d2f", "Write the problem · 8", "What, who, and why it matters.") + flow("#1f617a", "Idea sprint · 7", "One-minute setup plus five-minute sprint.") + flow("#e3ad19", "Screen · 10", "Problem fit, realistic first version, customer use.") + flow("#4a9d2f", "Develop · 15", "Top two and one dropped idea.") + flow("#1f617a", "Close · 5", "Evidence that separated two ideas."), "MONITOR": "<p>At minute 3 of the sprint, students should have six ideas. Repair with: Who has the problem? What is the smallest version? What do customers do now?</p>", "RESOURCES": "<p>Licensed FYF pp. 234-235 are embedded. The support packet is an equal absence and paper route.</p>", "SUPPORT": "<p>Use the eight-item problem menu. Short bilingual phrases count during the sprint; score reasoning after screening.</p>", "FALLBACK": "<p>No partner or platform is required. Do not use real classmates’ private information in a problem scenario.</p>"},
            3: {"TITLE": "Stress-Test and Make the Call", "SUBTITLE": "50 minutes · TEKS d(3)(I)", "ALERT": "<strong>Abandon It can earn full credit.</strong> Score the comparison and reasoning, not whether the venture moves forward.", "PREP": f'<ul><li>Post FYF pp. 236-237 and {file_link(files["IDEA"]["id"], "the support packet")}.</li><li>Open the unpublished practice Quiz.</li><li>Tell students the printed workbook skips Step 6; nothing is missing.</li></ul>', "EVIDENCE": "<p>Two-idea stress test, risks, 6-8 sentence call, and practice check. Recommended core portfolio evidence.</p>", "FLOW": flow("#5a2d91", "Re-enter · 5", "Current favorite and evidence that could change it.") + flow("#4a9d2f", "Stress-test · 20", "Release problem fit, customer choice, and build challenge one at a time.") + flow("#1f617a", "Make the call · 12", "Strength, risk, and deciding evidence.") + flow("#e3ad19", "Compare · 8", "45 seconds each or private written route.") + flow("#1f617a", "Practice check · 5", "Immediate feedback and retry."), "MONITOR": "<p>Reject “everyone will like it” as evidence. Strong work compares both ideas, acknowledges a real risk, and connects the call to one test. Quiz key is encoded with feedback.</p>", "RESOURCES": "<p>Licensed FYF pp. 236-237 are embedded. The practice Quiz checks bounded misconceptions; it does not replace the written decision.</p>", "SUPPORT": "<p>Release one question at a time. Use sentence frames, oral rehearsal, speech-to-text, or the fixed table.</p>", "FALLBACK": "<p>Replace group compare with a written comparison. No student is locked out by attendance or partner availability.</p>"},
            4: {"TITLE": "Venture Brief and Pitch", "SUBTITLE": "50 minutes · TEKS d(3)(I), d(4)(F)", "ALERT": "<strong>Presentation math is protected.</strong> Eight groups fit at 90 seconds plus a 30-second question and 30-second transition. Use two stations or recordings for more groups.", "PREP": f'<ul><li>Post {file_link(files["VENTURE"]["id"], "the Venture Brief")}, {file_link(files["RUBRIC"]["id"], "the rubric")}, and the 90-second timer.</li><li>Prepare live, private, recorded, and written routes.</li></ul>', "EVIDENCE": "<p>Six-section group brief plus each student’s speaking/written record, one evidence-based peer note, and work-ethic action. Individual evidence prevents group attendance from determining the score.</p>", "FLOW": flow("#5a2d91", "Launch · 5", "Clear problem, offer, evidence.") + flow("#4a9d2f", "Build and rehearse · 15", "Stop decoration at minute 9.") + flow("#1f617a", "Pitch rotation · 24", "90-second pitch, question, transition.") + flow("#e3ad19", "Individual close · 6", "Professional action for owners and employees."), "MONITOR": "<p>Score observable preparation, accuracy, follow-through, revision, or honesty. Do not score confidence, accent, popularity, artwork, or whether the venture receives class approval. Skip the class vote.</p>", "RESOURCES": "<p>The CCE brief traces every section to the student’s Million Dollar Idea evidence. Canva or Adobe Express is optional; a plain brief is equal.</p>", "SUPPORT": "<p>Allow live, private, recorded, or written presentation. Use assigned roles and private self-review when peer feedback is unavailable.</p>", "FALLBACK": "<p>A student without a group uses their own idea. No public posting of ideas is required.</p>"},
            5: {"TITLE": "Personal Budget and Xello Scholarship Profile", "SUBTITLE": "50 minutes · TEKS d(3)(I), d(5)(D)", "ALERT": "<strong>Sequence repair.</strong> Do not repeat Save careers. Protect 20 minutes for the required Grade 8 Scholarship profile and verify through the Completion Standards report.", "PREP": f'<ul><li>Post {file_link(files["COST"]["id"], "the dated cost guide")}, {file_link(files["BUDGET"]["id"], "the budget plan")}, {file_link(files["XELLO_EN"]["id"], "Xello’s English guide")}, {file_link(files["XELLO_ES"]["id"], "Xello’s Spanish guide")}, and {file_link(files["RUBRIC"]["id"], "the rubric")}.</li><li>Open the Xello Completion Standards report and official video.</li></ul>', "EVIDENCE": "<p>Balanced revised budget, percentage calculation, revenue distinction, private reflection, and Xello report completion. Recommended 16-point major portfolio, not configured until grade groups are verified.</p>", "FLOW": flow("#5a2d91", "Source labels · 5", "Place, household, date, measure.") + flow("#4a9d2f", "Budget · 20", "First budget, lifestyle choice, revised budget, reasoning.") + flow("#1f617a", "Xello profile · 20", "Complete matching profile; no application required.") + flow("#e3ad19", "Submit · 5", "Private portfolio and catch-up record."), "MONITOR": "<p>Revised expenses must total $3,450 or less. There is no one correct lifestyle choice. Xello answers must be honest; “I don’t know” is acceptable. Do not collect private profile answers or screenshots.</p>", "RESOURCES": '<p><a href="https://livingwage.mit.edu/counties/48113">MIT Dallas County source</a> · <a href="https://www.dallascollege.edu/research/reports/living-wages-community-college/">Dallas College 2026 brief</a> · <a href="https://help.xello.world/en-us/content/Knowledge-Base/Xello-6-12/College-Planning/KB_6-12_Scholarships.htm">Xello Scholarships resources</a></p>', "SUPPORT": "<p>Use calculator, read-aloud, chunked table, speech-to-text, or audio. The print packet gives separate cells for calculations and full-width lines for each explanation.</p>", "FALLBACK": "<p>Platform failure moves to supervised Xello catch-up; paper does not count as completion. The official PDF is the video text route. H&amp;L salary is not load-bearing.</p>"},
        }

        day_names = {1: "Entrepreneurship Opportunities", 2: "Problem and Idea Sprint", 3: "Stress-Test and Decide", 4: "Venture Brief and Pitch", 5: "Budget and Scholarship Profile"}
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 3SW Wk6 Day {day} - {day_names[day]}"
            student_page = await upsert_page(client, student_title, render("3sw-wk6-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, **student[day]}))
            teacher_title = f"TEACHER: 3SW Wk6 Day {day} Facilitator Guide"
            teacher_page = await upsert_page(client, teacher_title, render("3sw-wk6-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **teacher[day]}))
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
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(entry for entry in items if (kind == "SubHeader" and entry.get("id") == key) or (kind == "Page" and entry.get("page_url") == key) or (kind in ("Quiz", "Assignment") and entry.get("content_id") == key))
            await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}", data={"module_item[position]": position, "module_item[title]": title})

        final_items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        module = await api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        print(json.dumps({
            "module": {"id": module["id"], "published": module["published"]},
            "quiz": {"id": quiz["id"], "published": quiz.get("published"), "quiz_type": quiz.get("quiz_type"), "allowed_attempts": quiz.get("allowed_attempts")},
            "portfolio": {"id": portfolio["id"], "published": portfolio.get("published"), "grading_type": portfolio.get("grading_type"), "submission_types": portfolio.get("submission_types")},
            "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
            "folders": {str(day): {"id": folder["id"], "locked": folder["locked"]} for day, folder in folders.items()},
            "files": {key: value["id"] for key, value in files.items()},
            "pages": {str(day): {kind: {"url": value["url"], "published": value["published"]} for kind, value in pair.items()} for day, pair in pages.items()},
            "items": [{"id": item["id"], "position": item["position"], "title": item["title"], "type": item["type"], "page_url": item.get("page_url")} for item in final_items],
        }, indent=2))


asyncio.run(main())
