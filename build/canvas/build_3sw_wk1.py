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
    uploaded = response.json()
    return await api(client, "PUT", f"/files/{uploaded['id']}", data={"locked": "true"})


def render(template_name, values):
    text = (TEMPLATES / template_name).read_text()
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    unresolved = sorted(set(re.findall(r"\{\{[^}]+\}\}", text)))
    if unresolved:
        raise ValueError(f"Unresolved values in {template_name}: {unresolved}")
    return text


async def upsert_page(client, title, body, legacy_titles=()):
    url = slugify(title)
    data = {"wiki_page[title]": title, "wiki_page[body]": body, "wiki_page[published]": "false", "wiki_page[editing_roles]": "teachers"}
    for candidate in (url, *(slugify(value) for value in legacy_titles)):
        response = await client.get(f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{candidate}")
        if response.status_code == 200:
            return await api(client, "PUT", f"/courses/{COURSE_ID}/pages/{candidate}", data=data)
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


async def upsert_header(client, module_id, title, legacy_titles=()):
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    accepted = {title, *legacy_titles}
    found = next((entry for entry in items if entry.get("type") == "SubHeader" and entry.get("title") in accepted), None)
    if found:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module_id}/items/{found['id']}", data={"module_item[title]": title}) if found.get("title") != title else found
    return await api(client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data={"module_item[type]": "SubHeader", "module_item[title]": title})


def file_link(file_id, label):
    return f'<a href="/courses/{COURSE_ID}/files/{file_id}/preview" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">{label}</a>'


def image_tag(file_id, alt, max_width=720):
    return f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" style="display:block;width:100%;max-width:{max_width}px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'


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
            1: {"TITLE": "Meet the Veterinary Team", "PURPOSE": "Compare three veterinary careers using one dated evidence set.", "TODAY": "<ul><li>identify what each role does;</li><li>compare education, pay, growth, and openings;</li><li>choose one role to investigate.</li></ul>", "READY": f'<p>Open {file_link(files["CAREERS"]["id"], "the Veterinary Career Evidence Guide")}.</p>', "MEDIA": image_tag(uploads[1]["fyf-agriculture-opener.png"]["id"], "Find Your Future agriculture and animal-care career opener"), "STEPS": step(1, "Notice the range of work", "<p>Animal-care careers include observation, communication, science, recordkeeping, and hands-on care.</p>") + step(2, "Read all three career cards", "<p>Keep the salary measure, source, date, and education route attached to each number.</p>") + step(3, "Choose one role", "<p>Write one daily-work reason and one preparation fact.</p>"), "EXIT": "<p>Why does the highest median-pay role also require the longest preparation?</p>", "DONE": "<ul><li>three roles reviewed;</li><li>one source and date recorded;</li><li>one role choice defended with two facts.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> median = mediana · training = formación · openings = vacantes · veterinarian = veterinario/a.</p><p><strong>Frame:</strong> “I would investigate ____ because the work includes ____ and the preparation requires ____.”</p>", "FALLBACK": "<p>The fixed evidence guide is the full no-login and absence route. H&amp;L is optional enrichment.</p>"},
            2: {"TITLE": "Compare Veterinary Career Paths", "PURPOSE": "Use the same measures to explain how veterinary roles differ.", "TODAY": "<ul><li>complete a three-role comparison;</li><li>explain one preparation trade-off;</li><li>recommend a role for a fictional student.</li></ul>", "READY": f'<p>Open {file_link(files["COMPARE"]["id"], "the Veterinary Career Comparison")} and the evidence guide.</p>', "MEDIA": "", "STEPS": step(1, "Transfer the evidence", "<p>Fill every row from the fixed guide. Do not mix national median pay with starting pay.</p>") + step(2, "Compare preparation", "<p>Explain what changes from short-term training to an associate degree to a professional degree.</p>") + step(3, "Make a recommendation", "<p>Use at least two accurate facts and name one realistic trade-off.</p>"), "EXIT": "<p>A student wants animal-care work soon after high school but may continue college later. Which role should the student investigate first, and what trade-off should the student know?</p>", "DONE": "<ul><li>all six evidence rows complete for all three careers;</li><li>salary measure and source kept accurate;</li><li>recommendation uses two facts and one trade-off.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> assistant = asistente · technician = técnico/a · degree = título · trade-off = costo y beneficio.</p><p><strong>Frame:</strong> “I recommend ____ because ____; however, ____.”</p>", "FALLBACK": "<p>The two PDFs contain all required facts. No web search or partner is required.</p>"},
            3: {"TITLE": "Veterinary Triage: Observe, Compare, Report", "PURPOSE": "Prioritize two fictional patients using supplied observations and species-specific ranges without diagnosing.", "TODAY": "<ul><li>read the two fictional patient charts;</li><li>compare observations with the correct ranges;</li><li>defend which patient should be seen first.</li></ul>", "READY": '<p>Use <em>Find Your Future</em> pp. 96-99. Write your evidence and decision on p. 99.</p><p><strong>Role boundary:</strong> You observe, compare, prioritize, and report. A veterinarian diagnoses and treats.</p>', "MEDIA": "", "STEPS": step(1, "Read both patient charts", image_tag(uploads[3]["fyf-vet-triage-1.png"]["id"], "Find Your Future veterinary triage patient chart page 96", 650) + f'<p>{file_link(uploads[3]["fyf-vet-triage-1.png"]["id"], "Open FYF p. 96 full size")}</p>' + image_tag(uploads[3]["fyf-vet-triage-2.png"]["id"], "Find Your Future veterinary triage patient chart page 97", 650) + f'<p>{file_link(uploads[3]["fyf-vet-triage-2.png"]["id"], "Open FYF p. 97 full size")}</p><p>Mark symptoms, vital signs, species, and time for Leo and Barnaby.</p>') + step(2, "Use the correct reference", image_tag(uploads[3]["fyf-vet-triage-3.png"]["id"], "Find Your Future veterinary triage reference page 98", 650) + f'<p>{file_link(uploads[3]["fyf-vet-triage-3.png"]["id"], "Open FYF p. 98 full size")}</p><p>Compare the snake observations with the ball-python reference and the dog observations with the dog reference.</p>') + step(3, "Record the decision on workbook p. 99", image_tag(uploads[3]["fyf-vet-triage-4.png"]["id"], "Find Your Future veterinary triage response page 99", 650) + f'<p>{file_link(uploads[3]["fyf-vet-triage-4.png"]["id"], "Open FYF p. 99 full size")}</p><p>Cite at least two observations for the patient who should be seen first. This written triage record is the veterinary technician\'s work product in the simulation.</p>') + step(4, "Check your reasoning", f'<p><a href="{quiz_url}">Open the Triage Evidence Check</a>. Retry and use the feedback.</p>'), "EXIT": "<p>What record did the veterinary technician produce, and what evidence made one patient more urgent than the other?</p>", "DONE": "<ul><li>Leo and Barnaby reviewed;</li><li>workbook p. 99 completed;</li><li>triage record named as the work product;</li><li>first choice defended with two observations;</li><li>no diagnosis or treatment advice.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> triage = triaje · observation = observación · range = rango · priority = prioridad.</p><p><strong>Frame:</strong> “The technician produced ____. I would report ____ first because ____ and ____.”</p>", "FALLBACK": f'<p>All four licensed activity pages are embedded. If the workbook is unavailable or you need a more structured layout, use the optional {file_link(files["TRIAGE"]["id"], "Veterinary Triage Evidence Record")}. A private written response replaces discussion.</p>'},
            4: {"TITLE": "Xello Skills", "PURPOSE": "Complete the required Skills lesson and connect one transferable skill to veterinary work.", "TODAY": "<ul><li>complete Xello Skills;</li><li>identify one skill you use now;</li><li>connect it to two careers.</li></ul>", "READY": f'<p>Open {file_link(files["REFLECT"]["id"], "the private Skills Reflection")}.</p><p><strong>Prerequisite:</strong> at least three saved careers.</p>', "MEDIA": "", "STEPS": step(1, "Log in", "<p>ClassLink &gt; Xello &gt; Home &gt; Lessons.</p>") + step(2, "Complete Skills", "<p>Use the full 35-minute lesson block. Read the examples before choosing an answer.</p>") + step(3, "Reflect privately", f'<p>Complete the PDF or <a href="{assignment_url}">open the private reflection assignment</a>. Do not upload a profile screenshot.</p>'), "EXIT": "<p>Name one skill that transfers between a veterinary career and a different career. How would the skill look different?</p>", "DONE": "<ul><li>Skills lesson completed or catch-up recorded;</li><li>one current skill named;</li><li>two-career transfer explained;</li><li>reflection kept private.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> skill = habilidad · transferable = transferible · improve = mejorar · evidence = evidencia.</p><p><strong>Frame:</strong> “____ is useful in veterinary work when ____. It is useful in ____ when ____.”</p>", "FALLBACK": "<p>If Xello or prerequisites fail, complete the reflection scaffold and move the required lesson to supervised catch-up. Paper does not count as Xello completion.</p>"},
            5: {"TITLE": "Build a Veterinary Pathway Recommendation", "PURPOSE": "Connect veterinary career evidence, the district workbook, and one realistic next step.", "TODAY": "<ul><li>read the Nimitz Animal Science and Veterinary Science opportunities in the workbook;</li><li>build a pathway recommendation;</li><li>self-check it with the rubric.</li></ul>", "READY": f'<p>Open {file_link(files["PATHWAY"]["id"], "the Veterinary Pathway Recommendation")} and {file_link(files["RUBRIC"]["id"], "the 16-point evidence rubric")}.</p>', "MEDIA": "", "STEPS": step(1, "Read the district pathway evidence", image_tag(uploads[5]["fyf-irving-ag-programs-1.png"]["id"], "Find Your Future Irving agriculture program information page 100", 650) + f'<p>{file_link(uploads[5]["fyf-irving-ag-programs-1.png"]["id"], "Open FYF p. 100 full size")}</p>' + image_tag(uploads[5]["fyf-irving-ag-programs-2.png"]["id"], "Find Your Future Irving agriculture program information page 101", 650) + f'<p>{file_link(uploads[5]["fyf-irving-ag-programs-2.png"]["id"], "Open FYF p. 101 full size")}</p><p>Use <em>Find Your Future</em> pp. 100-101 as the primary local source. Record the program name and one experience exactly as the workbook presents them.</p>') + step(2, "Build the recommendation", "<p>Name one career, preparation route, daily task, labor-market fact, Nimitz opportunity, postsecondary requirement, and next action.</p>") + step(3, "Self-check and revise", "<p>Use all four rubric criteria. Add evidence where a reader would otherwise have to guess.</p>"), "EXIT": "<p>What is one action an eighth grader can take now that supports the high-school and postsecondary route?</p>", "DONE": "<ul><li>career and preparation accurate;</li><li>dated labor fact included;</li><li>FYF pp. 100-101 evidence used accurately;</li><li>high-school and postsecondary steps named;</li><li>rubric self-check complete.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> pathway = trayectoria · credential = credencial · postsecondary = después de la preparatoria · next step = próximo paso.</p><p>Use short labeled sections. A paragraph is not required.</p>", "FALLBACK": "<p>The PDFs and embedded workbook pages are complete. H&amp;L App Exploration is optional and does not require a screenshot.</p>"},
        }

        teacher = {
            1: {"TITLE": "Meet the Veterinary Team", "SUBTITLE": "50 minutes · TEKS d(1)(C), d(2)(A)", "ALERT": "<strong>Use the fixed, dated evidence cards.</strong> Do not make H&amp;L or a live salary search load-bearing.", "PREP": f'<ul><li>Post {file_link(files["CAREERS"]["id"], "the evidence guide")}.</li><li>Project the workbook opener.</li><li>Choose whether H&amp;L browsing is available as an extension.</li></ul>', "EVIDENCE": "<p>One career choice supported by a daily-work fact and a preparation fact.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "Who works on a veterinary team?") + flow("#4a9d2f", "Workbook opener · 10", "Notice the range of agricultural and animal-care work.") + flow("#1f617a", "Fixed evidence · 15", "Read all three career cards.") + flow("#e3ad19", "Choose and compare · 15", "Defend one role with two facts.") + flow("#1f617a", "Exit · 5", "Explain preparation and pay without promising an outcome."), "MONITOR": "<p>Key: Veterinarian has the highest U.S. median pay and longest preparation. Vet assistant has the shortest typical entry route. Vet tech usually requires an associate degree and credentialing varies. This is formative preparation for the recommended weekly minor evidence packet; do not grade platform clicks.</p>", "RESOURCES": '<p><a href="https://www.bls.gov/ooh/healthcare/veterinary-assistants-and-laboratory-animal-caretakers.htm">BLS Veterinary Assistants</a> · <a href="https://www.bls.gov/ooh/healthcare/veterinary-technologists-and-technicians.htm">BLS Veterinary Technicians</a> · <a href="https://www.bls.gov/ooh/healthcare/veterinarians.htm">BLS Veterinarians</a></p>', "SUPPORT": "<p>Read cards aloud; keep labels and numbers together; permit typed, written, dictated, or teacher-scribed evidence. Score reasoning, not mechanics unless meaning is unclear.</p>", "FALLBACK": "<p>The fixed guide is the complete absence route. H&amp;L is optional enrichment only.</p>"},
            2: {"TITLE": "Compare Veterinary Career Paths", "SUBTITLE": "50 minutes · TEKS d(2)(A), d(5)(A)", "ALERT": "<strong>One salary basis.</strong> All three figures are May 2024 U.S. medians; none is starting pay or a guarantee.", "PREP": f'<ul><li>Post {file_link(files["COMPARE"]["id"], "the comparison sheet")} and evidence guide.</li><li>Model one row and one two-fact recommendation.</li></ul>', "EVIDENCE": "<p>Completed three-role comparison plus an evidence-based recommendation. Recommended minor packet evidence.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "Rank career factors.") + flow("#4a9d2f", "Model measures · 10", "Median, education, growth, openings.") + flow("#1f617a", "Comparison · 20", "Complete all six evidence rows for all three careers.") + flow("#e3ad19", "Scenario · 10", "Recommend with two facts and a trade-off.") + flow("#1f617a", "Exit · 5", "Defend a first investigation."), "MONITOR": "<p>Stop measure drift immediately. A role can be a good fit without being highest paid. Full evidence uses two accurate facts and a realistic trade-off; career preference itself is not scored.</p>", "RESOURCES": f'<p>{file_link(files["CAREERS"]["id"], "Dated evidence guide")} · {file_link(files["RUBRIC"]["id"], "16-point rubric")}</p>', "SUPPORT": "<p>Use one modeled row, bilingual labels, sentence frames, and extra processing time. The comparison PDF has dedicated writing space for each requested response.</p>", "FALLBACK": "<p>No login, search, or partner is required. Both PDFs are the complete route.</p>"},
            3: {},
            4: {"TITLE": "Xello Skills", "SUBTITLE": "50 minutes · TEKS d(4)(B)", "ALERT": "<strong>Required Grade 8 task: Skills lesson, 35 minutes.</strong> Students need at least three saved careers. Earlier Life experiences and Volunteer hours are not repeated.", "PREP": f'<ul><li>Check the Completion Standards report and prerequisite status.</li><li>Test ClassLink &gt; Xello.</li><li>Open the {file_link(files["XELLO_GUIDE"]["id"], "official facilitator guide")}, {file_link(files["XELLO_DECK"]["id"], "Irving-adapted slides")}, and optional {file_link(files["XELLO_SPANISH"]["id"], "Spanish support deck")}.</li><li>Post {file_link(files["REFLECT"]["id"], "the private reflection")}.</li></ul>', "EVIDENCE": "<p>Xello Completion Standards report plus a private two-career transfer reflection. No public profile screenshot.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "Define a transferable skill.") + flow("#4a9d2f", "Xello Skills · 35", "Home &gt; Lessons &gt; Skills.") + flow("#1f617a", "Private reflection · 7", "Name one skill and two career contexts.") + flow("#e3ad19", "Report/catch-up · 3", "Record completion or supervised catch-up."), "MONITOR": "<p>District minimum is the assigned 35-minute lesson. The official six-page guide describes an extended 85-minute sequence; use it as teacher support, not an extra student requirement. Verify through the report, not screenshots.</p>", "RESOURCES": f'<p>{file_link(files["XELLO_GUIDE"]["id"], "Official extended facilitator guide")} · {file_link(files["XELLO_DECK"]["id"], "ClassLink launch slides")}</p>', "SUPPORT": "<p>Keep numbered navigation visible; offer read-aloud, chunking, bilingual labels, optional Spanish slides, and private written response. Do not infer student ability from a self-report result.</p>", "FALLBACK": "<p>If Xello or prerequisites fail, use the reflection scaffold and schedule supervised catch-up. Paper does not count as Xello completion.</p>"},
            5: {},
        }

        teacher[3] = {
            "TITLE": "Veterinary Triage",
            "SUBTITLE": "50 minutes · TEKS d(1)(C)",
            "ALERT": "<strong>Fictional simulation.</strong> Students observe, compare, prioritize, and report; they do not diagnose, prescribe, or advise treatment.",
            "PREP": f'<ul><li>Have students open FYF pp. 96-99; p. 99 is the default writing surface.</li><li>Keep the optional {file_link(files["TRIAGE"]["id"], "structured triage record")} available for absence or additional scaffolding.</li><li>Open the unpublished practice quiz.</li></ul>',
            "EVIDENCE": "<p>Completed FYF p. 99 notes for Leo and Barnaby, a decision naming who is seen first, and a two-observation defense that identifies the veterinary technician's role.</p>",
            "FLOW": flow("#5a2d91", "Warm-up · 5", "Observation versus diagnosis.") + flow("#4a9d2f", "Patient charts · 8", "Read Leo and Barnaby before deciding.") + flow("#1f617a", "Compare ranges · 12", "Use the correct species reference.") + flow("#e3ad19", "Workbook decision · 15", "Complete p. 99 and defend the priority.") + flow("#4a9d2f", "Practice check · 5", "Retry with feedback.") + flow("#1f617a", "Exit · 5", "Name the technician's work product and compare the two patients."),
            "MONITOR": "<p>Barnaby is the intended first priority because repeated unproductive retching, a painful distended abdomen, a heart rate of 150, and a weak pulse form the highest-risk cluster. Leo's cloudy eyes and dull skin match the supplied shedding reference. Students may prioritize and report; they may not diagnose either animal.</p>",
            "RESOURCES": "<p>FYF pp. 96-99 carry the full activity and enough writing space. The custom record is an optional structured scaffold, not a default print requirement.</p>",
            "SUPPORT": "<p>Read charts aloud, chunk one patient at a time, highlight range columns, and allow a private written route. Use the point-of-use word bank and complete sentence frame. Do not grade acting or public speaking.</p>",
            "FALLBACK": "<p>All four activity pages and the optional record are in Canvas. Real animal concerns go to a qualified adult and veterinarian, not the classroom simulation.</p>",
        }
        teacher[5] = {
            "TITLE": "Veterinary Pathway Recommendation",
            "SUBTITLE": "50 minutes · TEKS d(2)(A), d(3)(A)",
            "ALERT": "<strong>Keep the district workbook in front.</strong> FYF pp. 100-101 are the primary local pathway source. Present program, certification, and experience details as opportunities, not guaranteed outcomes.",
            "PREP": f'<ul><li>Post {file_link(files["PATHWAY"]["id"], "the pathway recommendation")} and {file_link(files["RUBRIC"]["id"], "the rubric")}.</li><li>Have students open FYF pp. 100-101.</li><li>Use the public Nimitz page only as teacher background if a student asks a current-detail question.</li></ul>',
            "EVIDENCE": "<p>Two-page recommendation with career, preparation, daily task, dated labor fact, FYF pathway evidence, a postsecondary requirement, and a realistic middle-to-high-school next step. Recommended 16-point minor evidence packet.</p>",
            "FLOW": flow("#5a2d91", "Warm-up · 5", "Fact, opportunity, or guarantee?") + flow("#4a9d2f", "Workbook evidence · 10", "Read FYF pp. 100-101.") + flow("#1f617a", "Build recommendation · 20", "Use labeled evidence sections.") + flow("#e3ad19", "Rubric/revise · 10", "Self-check all four criteria.") + flow("#1f617a", "Exit · 5", "Name a useful transition action."),
            "MONITOR": "<p>Accept a range of career choices when all evidence is accurate. Require a middle-school-to-high-school step and a high-school-to-postsecondary requirement. Do not award extra points for H&amp;L, design polish, or a claimed guaranteed credential. Suggested conversion after local approval: 15-16 Masters, 13-14 Meets, 12 Approaches, 10-11 Needs Improvement.</p>",
            "RESOURCES": '<p>Primary: <em>Find Your Future</em> pp. 100-101. Teacher background only: <a href="https://nimitz.irvingisd.net/about-us/veterinary-science">Nimitz Veterinary Science page</a>. H&amp;L App Exploration remains optional enrichment.</p>',
            "SUPPORT": "<p>Use labeled short sections instead of requiring a paragraph. Permit speech-to-text, keyboard entry, enlarged print, and bilingual labels. The PDF provides enough space for each requested response.</p>",
            "FALLBACK": "<p>Canvas contains the complete evidence set. No live site, favorite count, or screenshot is required.</p>",
        }

        contracts = {
            1: {"TOPIC": "Veterinary Careers", "OBJECTIVE": "Students will identify three veterinary career opportunities and describe one preparation requirement for each role.", "TEKS": "d(1)(C), d(2)(A)", "DOL": "Choose one veterinary role and support the choice with one daily-work fact and one preparation fact.", "STUDENT_OBJECTIVE": "identify three veterinary careers and explain how a worker prepares for each role.", "STUDENT_DOL": "choose one role and support my choice with a daily-work fact and a preparation fact.", "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> median = mediana · training = formación · openings = vacantes.</p><p><strong>Frame:</strong> I would investigate ____ because the work includes ____ and the preparation requires ____.</p>"},
            2: {"TOPIC": "Career Evidence", "OBJECTIVE": "Students will describe preparation requirements and analyze pay, growth, and annual-opening evidence for three veterinary careers.", "TEKS": "d(2)(A), d(5)(A)", "DOL": "Complete the three-career comparison and recommend one role using two accurate facts and one trade-off.", "STUDENT_OBJECTIVE": "compare preparation, pay, growth, and openings for three veterinary careers.", "STUDENT_DOL": "complete the comparison and recommend one role using two facts and one trade-off.", "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> degree = título · openings = vacantes · trade-off = ventaja y costo.</p><p><strong>Frame:</strong> I recommend ____ because ____ and ____; however, ____.</p>"},
            3: {"TOPIC": "Veterinary Triage", "OBJECTIVE": "Students will identify the veterinary technician's role by using supplied evidence to observe, prioritize, and report on two fictional patients.", "TEKS": "d(1)(C)", "DOL": "Complete FYF p. 99 and name the veterinary technician's work product while defending the first-priority patient with two case details.", "STUDENT_OBJECTIVE": "use evidence to explain how a veterinary technician observes, prioritizes, and reports.", "STUDENT_DOL": "complete workbook p. 99 and defend which patient should be seen first with two case details.", "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> triage = triaje · observation = observación · range = rango · priority = prioridad.</p><p><strong>Frame:</strong> The technician produced ____. I would report ____ first because ____ and ____.</p>"},
            4: {"TOPIC": "Transferable Skills", "OBJECTIVE": "Students will identify how one skill transfers between veterinary work and another career by completing Xello Skills and a private evidence reflection.", "TEKS": "d(4)(B)", "DOL": "Complete the Xello Skills lesson and a private reflection that compares how one skill appears in two careers.", "STUDENT_OBJECTIVE": "explain how one skill can be used in veterinary work and another career.", "STUDENT_DOL": "complete Xello Skills and compare how one skill appears in two careers.", "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> skill = habilidad · transferable = transferible · improve = mejorar.</p><p><strong>Frame:</strong> ____ is useful in veterinary work when ____. It is useful in ____ when ____.</p>"},
            5: {"TOPIC": "Veterinary Pathways", "OBJECTIVE": "Students will describe middle-school-to-high-school and high-school-to-postsecondary requirements for one veterinary career route using FYF and career evidence.", "TEKS": "d(2)(A), d(3)(A)", "DOL": "Complete a pathway recommendation that includes a career route, preparation evidence, one FYF pathway opportunity, one postsecondary requirement, and one realistic next step.", "STUDENT_OBJECTIVE": "describe the high-school and postsecondary steps for one veterinary career route.", "STUDENT_DOL": "complete a pathway recommendation with one FYF opportunity, one postsecondary requirement, and one next step.", "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> pathway = trayectoria · credential = credencial · postsecondary = después de la preparatoria · next step = próximo paso.</p><p><strong>Frame:</strong> I recommend ____ because ____. FYF shows ____. After high school, the student would still need ____. A useful next step is ____.</p>"},
        }

        day_names = {1: "Meet the Veterinary Team", 2: "Compare Veterinary Career Paths", 3: "Veterinary Triage", 4: "Xello Skills", 5: "Veterinary Pathway Recommendation"}
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            legacy_header_titles = ("Day 5 · Veterinary Pathway Brief",) if day == 5 else ()
            header = await upsert_header(client, module["id"], header_title, legacy_header_titles)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 3SW Wk1 Day {day} - {day_names[day]}"
            legacy_student_titles = ("STUDENT: 3SW Wk1 Day 5 - Veterinary Pathway Brief",) if day == 5 else ()
            student_page = await upsert_page(client, student_title, render("3sw-wk1-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, **contracts[day], **student[day]}), legacy_student_titles)
            teacher_title = f"TEACHER: 3SW Wk1 Day {day} Facilitator Guide"
            teacher_page = await upsert_page(client, teacher_title, render("3sw-wk1-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **contracts[day], **teacher[day]}))
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


if __name__ == "__main__":
    asyncio.run(main())
