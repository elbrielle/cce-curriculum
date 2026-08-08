"""Build the unpublished 3SW Week 1 Veterinary Science Canvas module."""

import asyncio
import json
import mimetypes
import re
import sys
from pathlib import Path

import httpx

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
MODULE_NAME = "3SW Wk1: Veterinary Science"
QUIZ_TITLE = "PRACTICE: Veterinary Triage Evidence Check"
ASSIGNMENT_TITLE = "PRACTICE: Xello Skills Reflection"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/3sw/wk1"
XELLO = ROOT / "cce-curriculum/resources/xello-licensed/lessons"


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
        return await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data={"module[published]": "false"}) if found.get("published") else found
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
    data = {"wiki_page[title]": title, "wiki_page[body]": body, "wiki_page[published]": "false", "wiki_page[editing_roles]": "teachers"}
    response = await client.get(f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{url}")
    if response.status_code == 200:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/pages/{url}", data=data)
    if response.status_code != 404:
        response.raise_for_status()
    return await api(client, "POST", f"/courses/{COURSE_ID}/pages", data=data)


async def upsert_module_item(client, module_id, kind, key, title):
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    found = next((entry for entry in items if (kind == "Page" and entry.get("page_url") == key) or (kind in ("Quiz", "Assignment") and entry.get("content_id") == key)), None)
    if found:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module_id}/items/{found['id']}", data={"module_item[title]": title})
    payload = {"module_item[type]": kind, "module_item[title]": title}
    payload["module_item[page_url]" if kind == "Page" else "module_item[content_id]"] = key
    return await api(client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data=payload)


async def upsert_header(client, module_id, title):
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    found = next((entry for entry in items if entry.get("type") == "SubHeader" and entry.get("title") == title), None)
    return found or await api(client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data={"module_item[type]": "SubHeader", "module_item[title]": title})


def file_link(file_id, label):
    return f'<a href="/courses/{COURSE_ID}/files/{file_id}/preview" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">{label}</a>'


def image_tag(file_id, alt, max_width=720):
    return f'<img src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" style="display:block;width:100%;max-width:{max_width}px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'


def step(number, title, body):
    return f'<h3 style="color:#5a2d91;border-bottom:3px solid #d9c9ed">{number}. {title}</h3>{body}'


def flow(color, title, text):
    return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'


QUESTIONS = [
    ("Q1 - Barnaby priority", "Which evidence most strongly supports seeing Barnaby first?", "Repeated unproductive retching, a painful distended abdomen, heart rate 150, and a weak pulse.", ["Barnaby weighs 100 pounds.", "Barnaby is a Great Dane.", "Barnaby ate breakfast yesterday."], "Correct. The cluster of abnormal observations signals the highest priority.", "Use the abnormal observations together, not breed or size alone."),
    ("Q2 - Leo boundary", "What is the strongest conclusion about Leo?", "The observations fit the supplied shedding reference, but a veterinarian still makes the diagnosis.", ["Leo definitely has one disease.", "Leo needs a student-selected medicine.", "Cloudy eyes always mean an emergency."], "Correct. Triage compares observations; it does not diagnose.", "Students may prioritize and report observations, but they do not diagnose or prescribe."),
    ("Q3 - Strong reasoning", "Which response shows the strongest triage reasoning?", "Compare each animal with the correct species normal range and cite at least two relevant observations.", ["Choose the animal that looks scariest.", "Use one vital sign for every animal.", "Vote before reading the reference ranges."], "Correct. Species-specific ranges plus multiple observations make the reasoning defensible.", "Look for the choice that uses the supplied ranges and more than one observation."),
    ("Q4 - Role boundary", "Which statement keeps the veterinary role boundary clear?", "A veterinary team member records and reports observations; a veterinarian diagnoses and treats.", ["A student can diagnose after reading one chart.", "The triage team should recommend medicine.", "A normal temperature proves the animal is healthy."], "Correct. Observation and escalation are different from diagnosis and treatment.", "The classroom task stops at observation, prioritization, and reporting."),
]


async def upsert_quiz(client):
    quizzes = await paged(client, f"/courses/{COURSE_ID}/quizzes")
    quiz = next((entry for entry in quizzes if entry.get("title") == QUIZ_TITLE), None)
    data = {"quiz[title]": QUIZ_TITLE, "quiz[description]": "<p>Ungraded practice. Retry and use the feedback before finalizing your triage record.</p>", "quiz[quiz_type]": "practice_quiz", "quiz[published]": "false", "quiz[allowed_attempts]": "-1", "quiz[show_correct_answers]": "true", "quiz[shuffle_answers]": "false"}
    quiz = await api(client, "PUT" if quiz else "POST", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}" if quiz else f"/courses/{COURSE_ID}/quizzes", data=data)
    existing = await paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    for position, (name, text, correct, wrong, correct_comment, incorrect_comment) in enumerate(QUESTIONS, 1):
        found = next((q for q in existing if q.get("question_name") == name), None)
        payload = {"question": {"question_name": name, "question_text": text, "question_type": "multiple_choice_question", "position": position, "points_possible": 1, "correct_comments": correct_comment, "incorrect_comments": incorrect_comment, "answers": [{"answer_text": correct, "answer_weight": 100}] + [{"answer_text": value, "answer_weight": 0} for value in wrong]}}
        await api(client, "PUT" if found else "POST", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions", json=payload)
    return await api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


async def upsert_assignment(client):
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    found = next((entry for entry in assignments if entry.get("name") == ASSIGNMENT_TITLE), None)
    data = {"assignment[name]": ASSIGNMENT_TITLE, "assignment[description]": "<p>Submit the private Xello Skills reflection as text or the supplied PDF. Do not upload a screenshot of your Xello profile.</p>", "assignment[submission_types][]": ["online_text_entry", "online_upload"], "assignment[grading_type]": "not_graded", "assignment[points_possible]": "0", "assignment[published]": "false"}
    return await api(client, "PUT" if found else "POST", f"/courses/{COURSE_ID}/assignments/{found['id']}" if found else f"/courses/{COURSE_ID}/assignments", data=data)


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        module, quiz, assignment = await ensure_module(client), await upsert_quiz(client), await upsert_assignment(client)
        support_path = "course files/CCR Materials/3SW/Wk1"
        support_folder = await ensure_folder(client, support_path)
        names = {"CAREERS": "3sw-wk1-veterinary-career-evidence-guide.pdf", "COMPARE": "3sw-wk1-veterinary-career-comparison.pdf", "TRIAGE": "3sw-wk1-veterinary-triage-record.pdf", "REFLECT": "3sw-wk1-xello-skills-reflection.pdf", "PATHWAY": "3sw-wk1-veterinary-pathway-brief.pdf", "RUBRIC": "3sw-wk1-veterinary-evidence-rubric.pdf"}
        files = {key: await upload(client, ROOT / "docs/resources/worksheets" / name, support_path) for key, name in names.items()}
        files["XELLO_GUIDE"] = await upload(client, XELLO / "skills.pdf", support_path)
        files["XELLO_DECK"] = await upload(client, XELLO / "skills/skills-slides-irving.pptx", support_path)
        files["XELLO_SPANISH"] = await upload(client, XELLO / "skills/skills-slides-spanish.pptx", support_path)
        folders, uploads = {}, {}
        for day in range(1, 6):
            folder_path = f"course files/CCR Materials/3SW/Wk1/Day {day} Visuals"
            folders[day], uploads[day] = await ensure_folder(client, folder_path), {}
            source = ASSETS / f"day{day}"
            if source.exists():
                for path in sorted(source.glob("*.png")):
                    uploads[day][path.name] = await upload(client, path, folder_path)

        quiz_url, assignment_url = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}", f"/courses/{COURSE_ID}/assignments/{assignment['id']}"
        student = {
            1: {"TITLE": "Meet the Veterinary Team", "PURPOSE": "Compare three veterinary careers using one dated evidence set.", "TODAY": "<ul><li>identify what each role does;</li><li>compare education, pay, growth, and openings;</li><li>choose one role to investigate.</li></ul>", "READY": f'<p>Open {file_link(files["CAREERS"]["id"], "the Veterinary Career Evidence Guide")}.</p>', "MEDIA": image_tag(uploads[1]["fyf-agriculture-opener.png"]["id"], "Find Your Future agriculture and animal-care career opener"), "STEPS": step(1, "Notice the range of work", "<p>Animal-care careers include observation, communication, science, recordkeeping, and hands-on care.</p>") + step(2, "Read all three career cards", "<p>Keep the salary measure, source, date, and education route attached to each number.</p>") + step(3, "Choose one role", "<p>Write one daily-work reason and one education trade-off.</p>"), "EXIT": "<p>Why does the highest median-pay role also require the longest preparation?</p>", "DONE": "<ul><li>three roles reviewed;</li><li>one source/date recorded;</li><li>one role choice defended with two facts.</li></ul>", "SUPPORT": "<p>median = mediana · training = formación · openings = vacantes · veterinarian = veterinario/a. Frame: “I would investigate ____ because ____.”</p>", "FALLBACK": "<p>The fixed evidence guide is the full no-login and absence route. H&amp;L is optional enrichment.</p>"},
            2: {"TITLE": "Compare Veterinary Career Paths", "PURPOSE": "Use the same measures to explain how veterinary roles differ.", "TODAY": "<ul><li>complete a three-role comparison;</li><li>explain one preparation trade-off;</li><li>recommend a role for a fictional student.</li></ul>", "READY": f'<p>Open {file_link(files["COMPARE"]["id"], "the Veterinary Career Comparison")} and the evidence guide.</p>', "MEDIA": "", "STEPS": step(1, "Transfer the evidence", "<p>Fill every row from the fixed guide. Do not mix national median pay with starting pay.</p>") + step(2, "Compare preparation", "<p>Explain what changes from short-term training to an associate degree to a professional degree.</p>") + step(3, "Make a recommendation", "<p>Use at least two facts and one interest or work-value fit.</p>"), "EXIT": "<p>A student wants animal-care work soon after high school but may continue college later. Which role is the strongest first investigation, and what trade-off should the student know?</p>", "DONE": "<ul><li>all three rows complete;</li><li>salary measure and source kept accurate;</li><li>recommendation uses two facts.</li></ul>", "SUPPORT": "<p>assistant = asistente · technician = técnico/a · degree = título · trade-off = compensación. Typed, written, or dictated evidence is equal.</p>", "FALLBACK": "<p>The two PDFs contain all required facts. No web search or partner is required.</p>"},
            3: {"TITLE": "Veterinary Triage: Observe, Compare, Report", "PURPOSE": "Prioritize fictional patients using supplied observations and species-specific ranges without diagnosing.", "TODAY": "<ul><li>read four fictional patient charts;</li><li>compare observations with the correct ranges;</li><li>defend a priority order.</li></ul>", "READY": f'<p>Open {file_link(files["TRIAGE"]["id"], "the Veterinary Triage Record")}.</p><p><strong>Role boundary:</strong> You observe, compare, prioritize, and report. A veterinarian diagnoses and treats.</p>', "MEDIA": "".join(image_tag(uploads[3][f"fyf-vet-triage-{n}.png"]["id"], f"Find Your Future veterinary triage case page {n}", 650) for n in range(1, 5)), "STEPS": step(1, "Read every chart", "<p>Mark symptoms, vital signs, species, and time.</p>") + step(2, "Use the correct reference", "<p>Compare dogs with dog ranges and reptiles with the supplied reptile information.</p>") + step(3, "Record the priority order", "<p>Cite at least two observations for the first patient.</p>") + step(4, "Check your reasoning", f'<p><a href="{quiz_url}">Open the Triage Evidence Check</a>. Retry and use the feedback.</p>'), "EXIT": "<p>What evidence made your first-priority patient more urgent than your second?</p>", "DONE": "<ul><li>all four patients reviewed;</li><li>priority order recorded;</li><li>first choice defended with two observations;</li><li>no diagnosis or treatment advice.</li></ul>", "SUPPORT": "<p>triage = triaje · observation = observación · range = rango · priority = prioridad. Frame: “I would report ____ first because ____ and ____.”</p>", "FALLBACK": "<p>All four licensed case pages are embedded. A private written response replaces discussion.</p>"},
            4: {"TITLE": "Xello Skills", "PURPOSE": "Complete the required Skills lesson and connect one transferable skill to veterinary work.", "TODAY": "<ul><li>complete Xello Skills;</li><li>identify one skill you use now;</li><li>connect it to two careers.</li></ul>", "READY": f'<p>Open {file_link(files["REFLECT"]["id"], "the private Skills Reflection")}.</p><p><strong>Prerequisite:</strong> at least three saved careers.</p>', "MEDIA": "", "STEPS": step(1, "Log in", "<p>ClassLink &gt; Xello &gt; Home &gt; Lessons.</p>") + step(2, "Complete Skills", "<p>Use the full 35-minute lesson block. Read the examples before choosing an answer.</p>") + step(3, "Reflect privately", f'<p>Complete the PDF or <a href="{assignment_url}">open the private reflection assignment</a>. Do not upload a profile screenshot.</p>'), "EXIT": "<p>Name one skill that transfers between a veterinary career and a different career. How would the skill look different?</p>", "DONE": "<ul><li>Skills lesson completed or catch-up recorded;</li><li>one current skill named;</li><li>two-career transfer explained;</li><li>reflection kept private.</li></ul>", "SUPPORT": "<p>skill = habilidad · transferable = transferible · improve = mejorar · evidence = evidencia. Use the teacher deck, read-aloud, and bilingual labels as needed.</p>", "FALLBACK": "<p>If Xello or prerequisites fail, complete the reflection scaffold and move the required lesson to supervised catch-up. Paper does not count as Xello completion.</p>"},
            5: {"TITLE": "Build a Veterinary Pathway Brief", "PURPOSE": "Connect career evidence, current Nimitz program information, and one realistic next step.", "TODAY": "<ul><li>separate current district facts from workbook context;</li><li>build a one-page pathway brief;</li><li>self-check it with the rubric.</li></ul>", "READY": f'<p>Open {file_link(files["PATHWAY"]["id"], "the Veterinary Pathway Brief")} and {file_link(files["RUBRIC"]["id"], "the 16-point evidence rubric")}.</p>', "MEDIA": "".join(image_tag(uploads[5][name]["id"], alt, 650) for name, alt in [("fyf-irving-ag-programs-1.png", "Find Your Future Irving agriculture program context page 1"), ("fyf-irving-ag-programs-2.png", "Find Your Future Irving agriculture program context page 2"), ("fyf-ag-app-exploration.png", "Find Your Future agriculture app exploration extension")]), "STEPS": step(1, "Read the evidence boundary", "<p>Current Nimitz information is the local planning source. Workbook pages are context and may be older.</p>") + step(2, "Build the brief", "<p>Name one career, preparation route, daily task, labor-market fact, Nimitz connection, and next action.</p>") + step(3, "Self-check and revise", "<p>Use all four rubric criteria. Add evidence where a reader would otherwise have to guess.</p>"), "EXIT": "<p>What is one action an eighth grader can take now without claiming a guaranteed credential or admission?</p>", "DONE": "<ul><li>career and preparation accurate;</li><li>dated labor fact included;</li><li>current local program wording used;</li><li>one realistic next step;</li><li>rubric self-check complete.</li></ul>", "SUPPORT": "<p>pathway = trayectoria · credential = credencial · clinical hours = horas clínicas · next step = próximo paso. Use short labeled sections; a paragraph is not required.</p>", "FALLBACK": "<p>The PDFs and embedded pages are complete. H&amp;L App Exploration is optional and does not require a screenshot.</p>"},
        }

        teacher = {
            1: {"TITLE": "Meet the Veterinary Team", "SUBTITLE": "50 minutes · TEKS d(1)(C), d(2)(A), d(5)(A)", "ALERT": "<strong>Use the fixed, dated evidence cards.</strong> Do not make H&amp;L or a live salary search load-bearing.", "PREP": f'<ul><li>Post {file_link(files["CAREERS"]["id"], "the evidence guide")}.</li><li>Project the workbook opener.</li><li>Choose whether H&amp;L browsing is available as an extension.</li></ul>', "EVIDENCE": "<p>One career choice supported by a daily-work fact and an education trade-off.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "Who works on a veterinary team?") + flow("#4a9d2f", "Workbook opener · 10", "Notice the range of agricultural and animal-care work.") + flow("#1f617a", "Fixed evidence · 15", "Read all three career cards.") + flow("#e3ad19", "Choose and compare · 15", "Defend one role with two facts.") + flow("#1f617a", "Exit · 5", "Explain preparation and pay without promising an outcome."), "MONITOR": "<p>Key: Veterinarian has the highest U.S. median pay and longest preparation. Vet assistant has the shortest typical entry route. Vet tech usually requires an associate degree and credentialing varies. This begins a recommended minor evidence packet; do not grade platform clicks.</p>", "RESOURCES": '<p><a href="https://www.bls.gov/ooh/healthcare/veterinary-assistants-and-laboratory-animal-caretakers.htm">BLS Veterinary Assistants</a> · <a href="https://www.bls.gov/ooh/healthcare/veterinary-technologists-and-technicians.htm">BLS Veterinary Technicians</a> · <a href="https://www.bls.gov/ooh/healthcare/veterinarians.htm">BLS Veterinarians</a></p>', "SUPPORT": "<p>Read cards aloud; keep labels and numbers together; permit typed, written, dictated, or teacher-scribed evidence. Score reasoning, not mechanics unless meaning is unclear.</p>", "FALLBACK": "<p>The fixed guide is the complete absence route. H&amp;L is optional enrichment only.</p>"},
            2: {"TITLE": "Compare Veterinary Career Paths", "SUBTITLE": "50 minutes · TEKS d(2)(A), d(5)(A)", "ALERT": "<strong>One salary basis.</strong> All three figures are May 2024 U.S. medians; none is starting pay or a guarantee.", "PREP": f'<ul><li>Post {file_link(files["COMPARE"]["id"], "the comparison sheet")} and evidence guide.</li><li>Model one row and one two-fact recommendation.</li></ul>', "EVIDENCE": "<p>Completed three-role comparison plus an evidence-based recommendation. Recommended minor packet evidence.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "Rank career factors.") + flow("#4a9d2f", "Model measures · 10", "Median, education, growth, openings.") + flow("#1f617a", "Comparison · 20", "Complete all three rows.") + flow("#e3ad19", "Scenario · 10", "Recommend with two facts and a trade-off.") + flow("#1f617a", "Exit · 5", "Defend a first investigation."), "MONITOR": "<p>Stop measure drift immediately. A role can be a good fit without being highest paid. Full evidence uses two accurate facts and a realistic trade-off; career preference itself is not scored.</p>", "RESOURCES": f'<p>{file_link(files["CAREERS"]["id"], "Dated evidence guide")} · {file_link(files["RUBRIC"]["id"], "16-point rubric")}</p>', "SUPPORT": "<p>Use one modeled row, bilingual labels, sentence frames, and extra processing time. The comparison PDF has dedicated writing space for each requested response.</p>", "FALLBACK": "<p>No login, search, or partner is required. Both PDFs are the complete route.</p>"},
            3: {"TITLE": "Veterinary Triage", "SUBTITLE": "50 minutes · TEKS d(1)(C), d(4)(B)", "ALERT": "<strong>Fictional simulation.</strong> Students observe, compare, prioritize, and report; they do not diagnose, prescribe, or advise treatment.", "PREP": f'<ul><li>Open licensed FYF pp. 96–99.</li><li>Post {file_link(files["TRIAGE"]["id"], "the triage record")}.</li><li>Open the unpublished practice quiz.</li></ul>', "EVIDENCE": "<p>Four-patient priority order and two-observation defense for the first patient.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "Observation versus diagnosis.") + flow("#4a9d2f", "Patient charts · 8", "Read all four before ranking.") + flow("#1f617a", "Compare ranges · 12", "Use the correct species reference.") + flow("#e3ad19", "Decision record · 15", "Prioritize and defend.") + flow("#4a9d2f", "Practice check · 5", "Retry with feedback.") + flow("#1f617a", "Exit · 5", "Compare first and second priority."), "MONITOR": "<p>Barnaby is the intended first priority because the abnormal signs form a high-risk cluster. Accept other ordering after first only when students cite the supplied observations and ranges. No visible normal sign proves overall health.</p>", "RESOURCES": "<p>Licensed workbook case pages are embedded individually. The custom record supplies the decision-writing space missing from the case page.</p>", "SUPPORT": "<p>Read charts aloud, chunk one patient at a time, highlight range columns, and allow a private written route. Do not grade acting or public speaking.</p>", "FALLBACK": "<p>All four case pages and the record are in Canvas. Real animal concerns go to a qualified adult and veterinarian, not the classroom simulation.</p>"},
            4: {"TITLE": "Xello Skills", "SUBTITLE": "50 minutes · TEKS d(4)(B)", "ALERT": "<strong>Required Grade 8 task: Skills lesson, 35 minutes.</strong> Students need at least three saved careers. Earlier Life experiences and Volunteer hours are not repeated.", "PREP": f'<ul><li>Check the Completion Standards report and prerequisite status.</li><li>Test ClassLink &gt; Xello.</li><li>Open the {file_link(files["XELLO_GUIDE"]["id"], "official facilitator guide")}, {file_link(files["XELLO_DECK"]["id"], "Irving-adapted slides")}, and optional {file_link(files["XELLO_SPANISH"]["id"], "Spanish support deck")}.</li><li>Post {file_link(files["REFLECT"]["id"], "the private reflection")}.</li></ul>', "EVIDENCE": "<p>Xello Completion Standards report plus a private two-career transfer reflection. No public profile screenshot.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "Define a transferable skill.") + flow("#4a9d2f", "Xello Skills · 35", "Home &gt; Lessons &gt; Skills.") + flow("#1f617a", "Private reflection · 7", "Name one skill and two career contexts.") + flow("#e3ad19", "Report/catch-up · 3", "Record completion or supervised catch-up."), "MONITOR": "<p>District minimum is the assigned 35-minute lesson. The official six-page guide describes an extended 85-minute sequence; use it as teacher support, not an extra student requirement. Verify through the report, not screenshots.</p>", "RESOURCES": f'<p>{file_link(files["XELLO_GUIDE"]["id"], "Official extended facilitator guide")} · {file_link(files["XELLO_DECK"]["id"], "ClassLink launch slides")}</p>', "SUPPORT": "<p>Keep numbered navigation visible; offer read-aloud, chunking, bilingual labels, optional Spanish slides, and private written response. Do not infer student ability from a self-report result.</p>", "FALLBACK": "<p>If Xello or prerequisites fail, use the reflection scaffold and schedule supervised catch-up. Paper does not count as Xello completion.</p>"},
            5: {"TITLE": "Veterinary Pathway Brief", "SUBTITLE": "50 minutes · TEKS d(2)(A), d(3)(A), d(5)(A)", "ALERT": "<strong>Use current local wording.</strong> Nimitz lists Small Animal Management, Large Animal Veterinary Science, and Advanced Animal Science. Certification opportunities and clinical hours are pathways, not guarantees.", "PREP": f'<ul><li>Post {file_link(files["PATHWAY"]["id"], "the pathway brief")} and {file_link(files["RUBRIC"]["id"], "the rubric")}.</li><li>Open the current Nimitz Veterinary Science page.</li><li>Label workbook pages as curriculum context.</li></ul>', "EVIDENCE": "<p>One-page brief with career, preparation, daily task, dated labor fact, current local connection, and realistic next action. Recommended 16-point minor evidence packet.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "Fact, opportunity, or guarantee?") + flow("#4a9d2f", "Local evidence · 10", "Current Nimitz page versus workbook context.") + flow("#1f617a", "Build brief · 20", "Six labeled evidence sections.") + flow("#e3ad19", "Rubric/revise · 10", "Self-check all four criteria.") + flow("#1f617a", "Exit · 5", "Name a realistic eighth-grade action."), "MONITOR": "<p>Accept a range of career choices when all evidence is accurate. Do not award extra points for H&amp;L, design polish, or a claimed guaranteed credential. Suggested conversion after local approval: 15–16 Masters, 13–14 Meets, 12 Approaches, 10–11 Needs Improvement.</p>", "RESOURCES": '<p><a href="https://nimitz.irvingisd.net/about-us/veterinary-science">Current Nimitz Veterinary Science page</a>. H&amp;L App Exploration remains optional enrichment.</p>', "SUPPORT": "<p>Use labeled short sections instead of requiring a paragraph. Permit speech-to-text, keyboard entry, enlarged print, and bilingual labels. The PDF provides enough space for each requested response.</p>", "FALLBACK": "<p>Canvas contains the complete evidence set. No live site, favorite count, or screenshot is required.</p>"},
        }

        day_names = {1: "Meet the Veterinary Team", 2: "Compare Veterinary Career Paths", 3: "Veterinary Triage", 4: "Xello Skills", 5: "Veterinary Pathway Brief"}
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_header(client, module["id"], header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 3SW Wk1 Day {day} - {day_names[day]}"
            student_page = await upsert_page(client, student_title, render("3sw-wk1-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, **student[day]}))
            teacher_title = f"TEACHER: 3SW Wk1 Day {day} Facilitator Guide"
            teacher_page = await upsert_page(client, teacher_title, render("3sw-wk1-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **teacher[day]}))
            await upsert_module_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await upsert_module_item(client, module["id"], "Page", student_page["url"], student_title)
            pages[day] = {"teacher": teacher_page, "student": student_page}
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title)]
            if day == 3:
                await upsert_module_item(client, module["id"], "Quiz", quiz["id"], QUIZ_TITLE)
                order.append(("Quiz", quiz["id"], QUIZ_TITLE))
            if day == 4:
                await upsert_module_item(client, module["id"], "Assignment", assignment["id"], ASSIGNMENT_TITLE)
                order.append(("Assignment", assignment["id"], ASSIGNMENT_TITLE))

        items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(entry for entry in items if (kind == "SubHeader" and entry.get("id") == key) or (kind == "Page" and entry.get("page_url") == key) or (kind in ("Quiz", "Assignment") and entry.get("content_id") == key))
            await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}", data={"module_item[position]": position, "module_item[title]": title})

        final_items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        module = await api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        print(json.dumps({"module": {"id": module["id"], "published": module["published"]}, "quiz": {"id": quiz["id"], "published": quiz.get("published")}, "assignment": {"id": assignment["id"], "published": assignment.get("published"), "grading_type": assignment.get("grading_type")}, "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]}, "folders": {str(day): {"id": folder["id"], "locked": folder["locked"]} for day, folder in folders.items()}, "files": {key: value["id"] for key, value in files.items()}, "pages": {str(day): {kind: {"url": value["url"], "published": value["published"]} for kind, value in pair.items()} for day, pair in pages.items()}, "items": [{"id": item["id"], "position": item["position"], "title": item["title"], "type": item["type"], "page_url": item.get("page_url")} for item in final_items]}, indent=2))


asyncio.run(main())
