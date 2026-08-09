"""Build the unpublished 3SW Week 2 Plant Science Canvas module."""

import asyncio
import json
import mimetypes
import re
import sys
from pathlib import Path

import httpx

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
MODULE_NAME = "3SW Wk2: Plant Science and Agricultural Communication"
QUIZ_TITLE = "PRACTICE: Emerging Plant-Tech Evidence Check"
PACKET_TITLE = "MAJOR 1: Farm-to-Table and Emerging Plant-Tech Evidence"
REFLECTION_TITLE = "PRACTICE: Xello Biases Reflection"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/3sw/wk2"
XELLO = ROOT / "cce-curriculum/resources/xello-licensed/lessons/biases-and-career-choices"


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
    return f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" style="display:block;width:100%;max-width:{max_width}px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'


def step(number, title, body):
    return f'<h3 style="color:#5a2d91;border-bottom:3px solid #d9c9ed">{number}. {title}</h3>{body}'


def flow(color, title, text):
    return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'


QUESTIONS = [
    ("Q1 - Data boundary", "A Precision Agriculture Systems Technician is not a separate BLS category. What is the accurate way to use the guide?", "Use the Agricultural and Food Science Technician figures as parent-occupation evidence and state the limit.", ["Call $48,480 a DFW starting salary.", "Claim every technician uses the same tools.", "Treat the specialty as a guaranteed new occupation."], "Correct. Parent-occupation evidence can inform an evaluation when the limit stays visible.", "Keep the specialty, parent occupation, measure, geography, and date attached."),
    ("Q2 - Median", "What does the May 2024 U.S. median show?", "Half of workers in that occupation earned more and half earned less.", ["The guaranteed first-year salary in Irving.", "The amount every employer must pay.", "The cost of the required degree."], "Correct. Median is a wage measure, not starting pay or a guarantee.", "The guide does not provide a DFW starting salary."),
    ("Q3 - Emerging", "Why can a specialty be described as emerging even when its parent occupation already exists?", "Technology may change the tasks, tools, and skills inside an established occupation.", ["Every new title creates a new BLS category.", "Emerging always means 20% growth.", "A social-media post used the word future."], "Correct. Emerging work may be a change in tasks and tools, not a brand-new category.", "Look for the choice that explains how work changes."),
    ("Q4 - Technology link", "Which evidence best connects agricultural engineering to changing technology?", "BLS notes work with AI, geospatial systems, and automated irrigation, spraying, and harvesting.", ["The job has the highest salary in the table.", "All farms use identical robots.", "The title includes the word engineer."], "Correct. The claim uses a named technology and changed task.", "A strong emerging-career claim links technology to work, not just pay or title."),
]


async def upsert_quiz(client):
    quizzes = await paged(client, f"/courses/{COURSE_ID}/quizzes")
    quiz = next((entry for entry in quizzes if entry.get("title") == QUIZ_TITLE), None)
    data = {"quiz[title]": QUIZ_TITLE, "quiz[description]": "<p>Ungraded practice. Retry and use the feedback before submitting the Emerging Plant-Tech Evaluation.</p>", "quiz[quiz_type]": "practice_quiz", "quiz[published]": "false", "quiz[allowed_attempts]": "-1", "quiz[show_correct_answers]": "true", "quiz[shuffle_answers]": "false"}
    quiz = await api(client, "PUT" if quiz else "POST", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}" if quiz else f"/courses/{COURSE_ID}/quizzes", data=data)
    existing = await paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    for position, (name, text, correct, wrong, correct_comment, incorrect_comment) in enumerate(QUESTIONS, 1):
        found = next((q for q in existing if q.get("question_name") == name), None)
        payload = {"question": {"question_name": name, "question_text": text, "question_type": "multiple_choice_question", "position": position, "points_possible": 1, "correct_comments": correct_comment, "incorrect_comments": incorrect_comment, "answers": [{"answer_text": correct, "answer_weight": 100}] + [{"answer_text": value, "answer_weight": 0} for value in wrong]}}
        await api(client, "PUT" if found else "POST", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions", json=payload)
    return await api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


async def upsert_assignment(client, title, description, submission_types):
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    found = next((entry for entry in assignments if entry.get("name") == title), None)
    data = {"assignment[name]": title, "assignment[description]": description, "assignment[submission_types][]": submission_types, "assignment[grading_type]": "not_graded", "assignment[points_possible]": "0", "assignment[published]": "false"}
    return await api(client, "PUT" if found else "POST", f"/courses/{COURSE_ID}/assignments/{found['id']}" if found else f"/courses/{COURSE_ID}/assignments", data=data)


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        module = await ensure_module(client)
        quiz = await upsert_quiz(client)
        packet = await upsert_assignment(client, PACKET_TITLE, "<p>Submit the Farm-to-Table infographic and the individual Emerging Plant-Tech Evaluation. Canva, Adobe Express, paper, or another approved route is equal. Do not include real personal contact information.</p>", ["online_upload", "online_text_entry", "online_url"])
        reflection = await upsert_assignment(client, REFLECTION_TITLE, "<p>Submit the private Xello Biases reflection as text or upload the supplied PDF. Do not post a public discussion or profile screenshot.</p>", ["online_text_entry", "online_upload"])

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
        files = {key: await upload(client, ROOT / "docs/resources/worksheets" / name, support_path) for key, name in names.items()}
        files["XELLO_GUIDE"] = await upload(client, XELLO.parent / "biases-and-career-choices.pdf", support_path)
        files["XELLO_DECK"] = await upload(client, XELLO / "introduction-template.pptx", support_path)
        files["XELLO_TRAIL"] = await upload(client, XELLO / "career-trailblazers-student-instructions.pdf", support_path)
        files["XELLO_MATCH"] = await upload(client, XELLO / "non-traditional-career-matches-student-instructions.pdf", support_path)

        folders, uploads = {}, {}
        for day in range(1, 6):
            folder_path = f"course files/CCR Materials/3SW/Wk2/Day {day} Visuals"
            folders[day], uploads[day] = await ensure_folder(client, folder_path), {}
            source = ASSETS / f"day{day}"
            if source.exists():
                for path in sorted(source.glob("*.png")):
                    uploads[day][path.name] = await upload(client, path, folder_path)

        quiz_url = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        packet_url = f"/courses/{COURSE_ID}/assignments/{packet['id']}"
        reflection_url = f"/courses/{COURSE_ID}/assignments/{reflection['id']}"

        grow_media = "".join(image_tag(uploads[1][f"fyf-grow-system-rescue-{n}.png"]["id"], f"Find Your Future Grow System Rescue page {n}", 650) for n in range(1, 4))
        farm_media = "".join(image_tag(uploads[2][f"fyf-farm-to-table-{n}.png"]["id"], f"Find Your Future Farm to Table page {n}", 650) for n in range(1, 3))
        bias_media = "".join(image_tag(uploads[5][name]["id"], alt, 720) for name, alt in [
            ("xello-biases-warm-up.png", "Xello Biases and career choices warm-up questions"),
            ("xello-biases-sign-in.png", "Xello Google single sign-on reminder"),
            ("xello-biases-navigation.png", "Xello lesson navigation from the student dashboard"),
        ])
        # Canvas strips CSS aspect-ratio from iframe styles. Keep explicit dimensions so
        # the player does not collapse to the browser's 150-pixel default height.
        bls_video = '<div style="max-width:760px;margin:16px auto"><iframe width="760" height="428" style="display:block;width:100%;max-width:760px;border:0" src="https://www.youtube.com/embed/ozIUJsnBDLY" title="U.S. Bureau of Labor Statistics video: Agricultural Engineers" loading="lazy" allowfullscreen></iframe><p style="font-size:14px">Optional official BLS career video. If video is blocked, use the fixed evidence guide.</p></div>'

        student = {
            1: {"TITLE": "Diagnose a Grow System", "PURPOSE": "Use plant-system clues to choose a first repair and connect the work to real careers.", "TODAY": "<ul><li>compare three plant-system careers;</li><li>diagnose a fictional hydroponic problem;</li><li>defend the first repair.</li></ul>", "READY": f'<p>Open {file_link(files["CAREERS"]["id"], "the Plant Systems Career Evidence Guide")}. Use FYF pp. 88-90 or the embedded pages.</p>', "MEDIA": grow_media, "STEPS": step(1, "Meet the work", "<p>Compare technician, scientist, and engineer duties. Choose the role most likely to test the system first.</p>") + step(2, "Read every clue", "<p>Mark plant symptoms, water movement, light, nutrients, and cleanliness. More than one problem may be present.</p>") + step(3, "Choose the first repair", "<p>Use at least two clues. Explain why this repair comes before the others.</p>") + step(4, "Sketch an improvement", "<p>On paper or the back of the workbook page, label water flow, nutrients, lights, plant placement, and one prevention feature.</p>"), "EXIT": "<p>Which clue had the greatest effect on your first-repair decision, and what evidence would you check next?</p>", "DONE": "<ul><li>all clues reviewed;</li><li>one first repair defended with two clues;</li><li>one system improvement labeled;</li><li>one career connection accurate.</li></ul>", "SUPPORT": "<p>nutrients = nutrientes · water flow = flujo de agua · evidence = evidencia · priority = prioridad. Frame: “I would fix ____ first because ____ and ____.”</p>", "FALLBACK": "<p>The embedded licensed pages and fixed career guide are the complete route. A plain-paper system sketch is equal to chart paper.</p>"},
            2: {"TITLE": "Plan a Farm-to-Table Infographic", "PURPOSE": "Turn a fictional client's brief into a clear message for grocery shoppers.", "TODAY": "<ul><li>read the client requirements;</li><li>plan four process steps;</li><li>make a full-page sketch.</li></ul>", "READY": f'<p>Open {file_link(files["PLANNER"]["id"], "the three-page Farm-to-Table Planner")} and {file_link(files["RUBRIC"]["id"], "the student-visible 16-point rubric")}.</p>', "MEDIA": farm_media, "STEPS": step(1, "Use the fictional brief", "<p>Choose strawberries, grapes, bell peppers, or cucumbers. Treat every farm fact as scenario information, not a claim about a real business.</p>") + step(2, "Plan the four steps", "<p>Planting, growing and monitoring, harvesting and packing, then selling or delivery. Give each step one short explanation and one visual.</p>") + step(3, "Choose two useful facts", "<p>Explain why each fact matters to an adult grocery shopper.</p>") + step(4, "Sketch the whole page", "<p>Use the full-page box. Show reading order, title, four steps, visuals, and two facts. Rough drawings are enough.</p>"), "EXIT": "<p>Point to the first place a reader should look and the path the reader follows next. What makes that order clear?</p>", "DONE": "<ul><li>crop and audience named;</li><li>four process steps planned;</li><li>two scenario facts selected;</li><li>full-page sketch shows reading order;</li><li>two interview questions drafted.</li></ul>", "SUPPORT": "<p>audience = público · harvest = cosecha · consumer = consumidor · reading order = orden de lectura. Use labels and phrases; full paragraphs are not required.</p>", "FALLBACK": "<p>The PDF has a full page for the sketch and enough space for each response. No design login or partner is required today.</p>"},
            3: {"TITLE": "Build and Test the Infographic", "PURPOSE": "Create a readable client artifact and revise it after a quick usability check.", "TODAY": "<ul><li>build in Canva, Adobe Express, or on paper;</li><li>check reading order and accessibility;</li><li>submit a draft in Canvas.</li></ul>", "READY": f'<p>Keep {file_link(files["PLANNER"]["id"], "your planner")} and {file_link(files["RUBRIC"]["id"], "the rubric")} visible.</p>', "MEDIA": image_tag(uploads[2]["fyf-farm-to-table-2.png"]["id"], "Find Your Future Farm to Table creation and interview directions", 650), "STEPS": step(1, "Choose an equal build route", "<p>Use Canva for Education, Adobe Express, paper/chart paper, or another teacher-approved route. Premium templates and art skill do not earn extra points.</p>") + step(2, "Build the message", "<p>Add a title, four ordered steps, one visual per step, and two facts from the fictional brief. Use short, accurate wording.</p>") + step(3, "Run a 60-second reader test", "<p>A classmate, teacher, or self-check names where the eye goes first and one unclear spot. No same-crop partner is required.</p>") + step(4, "Revise and submit", f'<p>Fix one message or accessibility problem, then <a href="{packet_url}">open the Plant Science Evidence Packet assignment</a> and upload the infographic draft. You will add the Day 4 evaluation before final scoring.</p>'), "EXIT": "<p>What did you revise, and how does the change help a reader understand the farm-to-table process?</p>", "DONE": "<ul><li>four steps and two facts;</li><li>clear reading order;</li><li>readable text and contrast;</li><li>copyright/privacy check;</li><li>one revision and Canvas draft submission.</li></ul>", "SUPPORT": "<p>clarity = claridad · contrast = contraste · revise = revisar · source = fuente. Use built-in icons, shapes, or your own drawings. Text-to-speech can check wording.</p>", "FALLBACK": "<p>Paper is an equal route. Photograph or scan the finished page for Canvas; if upload fails, turn in the labeled original and record the access issue.</p>"},
            4: {"TITLE": "Evaluate Emerging Plant-Tech Work", "PURPOSE": "Explain how technology changes real agriculture tasks without inventing a job-market promise.", "TODAY": "<ul><li>separate a specialty from its BLS parent occupation;</li><li>evaluate one technology-to-task change;</li><li>state what the data cannot prove.</li></ul>", "READY": f'<p>Open {file_link(files["EMERGING_GUIDE"]["id"], "the Emerging Plant-Tech Evidence Guide")} and {file_link(files["EMERGING_EVAL"]["id"], "the two-page evaluation")}.</p>', "MEDIA": bls_video, "STEPS": step(1, "Choose one specialty", "<p>Precision agriculture systems technician, controlled-environment plant scientist, or agricultural automation engineer.</p>") + step(2, "Trace the change", "<p>Connect one named technology to one changed task and one needed skill or preparation route.</p>") + step(3, "Use two dated facts", "<p>Keep the parent occupation, U.S. median, date, and outlook labels attached. State one evidence limit.</p>") + step(4, "Check the reasoning", f'<p><a href="{quiz_url}">Open the Emerging Plant-Tech Evidence Check</a>. Retry, revise your evaluation, and add it to the <a href="{packet_url}">evidence packet assignment</a>.</p>'), "EXIT": "<p>Why is “technology is changing the work” more accurate than claiming every specialty is a brand-new occupation?</p>", "DONE": "<ul><li>specialty and parent occupation named;</li><li>technology connected to a task;</li><li>two dated facts;</li><li>one data limit;</li><li>4-6 sentence evaluation revised and submitted.</li></ul>", "SUPPORT": "<p>specialty = especialidad · parent occupation = ocupación principal · automation = automatización · limit = límite. Frame: “This specialty deserves more investigation because ____. The data cannot prove ____.”</p>", "FALLBACK": "<p>The fixed guide is the complete no-search route. Skip the video if blocked. The quiz is practice; use the paper self-check if Canvas is unavailable.</p>"},
            5: {"TITLE": "Xello Biases and Career Choices", "PURPOSE": "Complete the required Xello lesson and test one career assumption with evidence.", "TODAY": "<ul><li>complete Biases and career choices in Xello;</li><li>revisit one assumption privately;</li><li>choose a fair way to investigate a career.</li></ul>", "READY": f'<p>Open {file_link(files["BIAS_REFLECT"]["id"], "the private reflection")}. Keep personal identity and experiences private unless you choose to share them.</p>', "MEDIA": bias_media, "STEPS": step(1, "Warm up", "<p>Think privately: Where do people learn assumptions about careers? You may pass on public sharing.</p>") + step(2, "Complete the assigned lesson", "<p>ClassLink &gt; Xello &gt; Home &gt; Lessons &gt; Biases and career choices. Use the full 30-minute block.</p>") + step(3, "Test an assumption with evidence", "<p>Use one Plant-Tech Guide fact or one Xello career-profile fact. You do not need to disclose a protected identity or personal experience.</p>") + step(4, "Submit privately", f'<p>Complete the PDF or <a href="{reflection_url}">open the private Canvas assignment</a>. Do not use a public discussion or profile screenshot.</p>'), "EXIT": "<p>What is one fair action—such as reading a profile, taking a course, interviewing a worker, or job shadowing—that can test an assumption before you rule a career out?</p>", "DONE": "<ul><li>Xello lesson completed or catch-up recorded;</li><li>one assumption named without forced disclosure;</li><li>one career fact used;</li><li>one fair next action explained;</li><li>private submission complete.</li></ul>", "SUPPORT": "<p>bias = sesgo · assumption = suposición · challenge = cuestionar · evidence = evidencia. A teacher may read prompts aloud and conference privately.</p>", "FALLBACK": "<p>If Xello fails, complete the private reflection with the Plant-Tech Guide and move the required lesson to supervised catch-up. Paper does not count as Xello completion.</p>"},
        }

        teacher = {
            1: {"TITLE": "Diagnose a Grow System", "SUBTITLE": "50 minutes · TEKS d(1)(C), d(2)(A)", "ALERT": "<strong>Do not turn Day 1 into an open H&amp;L search.</strong> The fixed career guide and licensed workbook carry the lesson with no login or live-data verification burden.", "PREP": f'<ul><li>Post {file_link(files["CAREERS"]["id"], "the career guide")} and FYF pp. 88-90.</li><li>Provide plain paper for the optional system sketch.</li><li>Model one two-clue diagnosis without giving the final priority.</li></ul>', "EVIDENCE": "<p>First-repair decision supported by two clues, one labeled system improvement, and one accurate career-role connection. Formative evidence.</p>", "FLOW": flow("#5a2d91", "System warm-up · 5", "What must reach every plant?") + flow("#4a9d2f", "Career evidence · 8", "Technician, scientist, engineer.") + flow("#1f617a", "Investigate and diagnose · 20", "Read every clue before choosing.") + flow("#e3ad19", "Prioritize and sketch · 12", "First repair plus prevention feature.") + flow("#1f617a", "Exit · 5", "Strongest clue and next evidence check."), "MONITOR": "<p>Strong reasoning prioritizes slow water flow/pump or blockage because weak roots and uneven growth support inadequate circulation; accept another first repair when two supplied clues and a coherent sequence support it. Students should not claim that one symptom proves one cause. Career key: technician tests/records, scientist studies plant/soil conditions, engineer designs system changes.</p>", "RESOURCES": f'<p>{file_link(files["CAREERS"]["id"], "Dated career evidence guide")} · H&amp;L browsing is optional enrichment only.</p>', "SUPPORT": "<p>Read clues aloud, color-code water/light/nutrients/cleanliness, allow oral rehearsal, and accept labeled diagrams plus short phrases. The workbook provides substantial writing space on pp. 89-90.</p>", "FALLBACK": "<p>All licensed pages are embedded. An absent student completes the same individual decision and sketch; partner comparison is optional.</p>"},
            2: {"TITLE": "Plan a Farm-to-Table Infographic", "SUBTITLE": "50 minutes · TEKS d(1)(C), d(4)(B)", "ALERT": "<strong>Sunny Fields Farm is fictional.</strong> Preserve workbook facts as scenario details; do not convert them into claims about a real business or current agriculture practice.", "PREP": f'<ul><li>Post FYF pp. 91-92, {file_link(files["PLANNER"]["id"], "the three-page planner")}, and {file_link(files["RUBRIC"]["id"], "the major rubric")}.</li><li>Show one simple process infographic model from a teacher-created or licensed source.</li><li>Have pencils/markers ready; no login is needed.</li></ul>', "EVIDENCE": "<p>Client requirement map, four-step content plan, two useful facts, full-page sketch, and two interview questions. This begins the recommended major packet.</p>", "FLOW": flow("#5a2d91", "Food-journey warm-up · 5", "Name four likely stages.") + flow("#4a9d2f", "Client brief · 8", "Audience, crop choices, required content.") + flow("#1f617a", "Content plan · 20", "Four steps and two facts.") + flow("#e3ad19", "Full-page sketch · 12", "Reading order, visuals, labels.") + flow("#1f617a", "Exit · 5", "Trace the reader path."), "MONITOR": "<p>Require planting, growing/monitoring, harvesting/packing, and selling/delivery. Students may choose any listed crop. The planner intentionally devotes a full page to the sketch and separate lines to questions; do not compress the work into the workbook's small interview boxes.</p>", "RESOURCES": "<p>Licensed FYF client brief is embedded. Canva and Adobe are not needed until Day 3.</p>", "SUPPORT": "<p>Use icons plus words, provide a four-step word bank, accept phrases, and let students narrate the sketch before writing. Do not grade drawing quality.</p>", "FALLBACK": "<p>The planner is the complete absence route. If a student misses partner talk, use a teacher/self trace of the reading order.</p>"},
            3: {"TITLE": "Build and Test the Infographic", "SUBTITLE": "50 minutes · TEKS d(1)(C), d(4)(B)", "ALERT": "<strong>Canva for Education, Adobe Express, and paper are equal.</strong> Do not require premium assets, a personal account, or a real social-media post. Submit through Canvas, not Google Classroom.", "PREP": f'<ul><li>Confirm the district-approved Canva or Adobe route only if offering it.</li><li>Keep paper/chart paper ready from the start.</li><li>Post the {file_link(files["RUBRIC"]["id"], "rubric")} and open the unpublished evidence-packet assignment.</li><li>Project a finished teacher model with a clear reading order.</li></ul>', "EVIDENCE": "<p>Farm-to-Table infographic draft plus one documented message/accessibility revision. Recommended major evidence continues; platform choice is not scored.</p>", "FLOW": flow("#5a2d91", "Plan check · 5", "Four steps, two facts, reader path.") + flow("#4a9d2f", "Model and criteria · 8", "Readable, accurate, source-safe.") + flow("#1f617a", "Build · 25", "Digital or paper route.") + flow("#e3ad19", "Reader test and revise · 7", "First look plus one unclear spot.") + flow("#1f617a", "Submit draft · 5", "Canvas upload, URL, text note, or paper record."), "MONITOR": "<p>Full draft: engaging title, four ordered steps, one visual and short explanation per step, and two scenario facts. Reject real personal contact information, uncited outside images, unreadable text, or claims not in the fictional brief. A self-check replaces a missing peer.</p>", "RESOURCES": f'<p>{file_link(files["PLANNER"]["id"], "Planner")} · {file_link(files["RUBRIC"]["id"], "16-point rubric")} · Canvas assignment accepts upload, text entry, or URL.</p>', "SUPPORT": "<p>Provide a four-box layout, built-in icons, speech-to-text, enlarged print, and a paper route. Score communication rather than artistry or English mechanics unless meaning is unclear.</p>", "FALLBACK": "<p>If a design platform fails, move immediately to paper. If Canvas upload fails, collect the labeled original or file and record the access issue.</p>"},
            4: {"TITLE": "Evaluate Emerging Plant-Tech Work", "SUBTITLE": "50 minutes · TEKS d(1)(D), d(5)(C)", "ALERT": "<strong>Do not invent a job title's salary.</strong> Every specialty is paired with a real BLS parent occupation, and students must state that limitation.", "PREP": f'<ul><li>Post {file_link(files["EMERGING_GUIDE"]["id"], "the dated evidence guide")}, {file_link(files["EMERGING_EVAL"]["id"], "evaluation")}, and {file_link(files["RUBRIC"]["id"], "rubric")}.</li><li>Test or skip the optional official BLS video.</li><li>Open the unpublished practice quiz and evidence-packet assignment.</li></ul>', "EVIDENCE": "<p>Individual technology-to-task evaluation with two dated facts, one evidence limit, and a revision. This completes the recommended 16-point major packet.</p>", "FLOW": flow("#5a2d91", "Optional BLS hook · 4", "Agricultural engineering tasks.") + flow("#4a9d2f", "Parent/specialty model · 8", "What a proxy can and cannot show.") + flow("#1f617a", "Read the fixed guide · 10", "Three specialties, three routes.") + flow("#e3ad19", "Individual evaluation · 20", "Technology, task, two facts, limit.") + flow("#4a9d2f", "Practice quiz · 5", "Retry and revise.") + flow("#1f617a", "Submit · 3", "Add evaluation to the packet."), "MONITOR": "<p>Key facts: technician parent = $48,480/5%; soil and plant scientist = $71,410/5%; agricultural engineer = $84,630/6%. All are May 2024 U.S. medians/outlook 2024-34. Full evidence says the figure belongs to the parent occupation and cannot prove an exact specialty's local starting pay.</p>", "RESOURCES": '<p><a href="https://www.bls.gov/ooh/life-physical-and-social-science/agricultural-and-food-science-technicians.htm">BLS Technicians</a> · <a href="https://www.bls.gov/ooh/life-physical-and-social-science/agricultural-and-food-scientists.htm">BLS Scientists</a> · <a href="https://www.bls.gov/ooh/architecture-and-engineering/agricultural-engineers.htm">BLS Engineers</a> · <a href="https://www.ars.usda.gov/oc/dof/farming-with-precision/">USDA Precision Agriculture</a> · <a href="https://www.nifa.usda.gov/about-nifa/impacts/automation-specialty-crops">USDA Automation for Specialty Crops</a></p>', "SUPPORT": "<p>Model one trend-to-task chain. Highlight specialty, parent occupation, measure/date, and limitation in four colors. The evaluation gives ten full writing lines for the 4-6 sentence response.</p>", "FALLBACK": "<p>The fixed guide replaces open searching and job boards. The video and quiz are optional support; the paper evaluation is the durable evidence.</p>"},
            5: {"TITLE": "Xello Biases and Career Choices", "SUBTITLE": "50 minutes · consolidates d(1)(D) and d(4)(B)", "ALERT": "<strong>Required Grade 8 task: Biases and career choices, 30 minutes.</strong> Do not repeat Work experiences. The licensed 80-minute facilitator package is an extended sequence; only Activity 2 is the district completion task today.", "PREP": f'<ul><li>Check the Xello Completion Standards report and test ClassLink.</li><li>Open the {file_link(files["XELLO_GUIDE"]["id"], "official 80-minute facilitator guide")} and {file_link(files["XELLO_DECK"]["id"], "seven-slide teacher deck")}.</li><li>Use only Activity 2 today. The {file_link(files["XELLO_TRAIL"]["id"], "Career Trailblazers")} and {file_link(files["XELLO_MATCH"]["id"], "Non-traditional Career Matches")} handouts are optional extensions.</li><li>Post the {file_link(files["BIAS_REFLECT"]["id"], "private reflection")} and assignment.</li></ul>', "EVIDENCE": "<p>Xello Completion Standards report plus a private career-assumption reflection using one career fact and one fair investigation strategy. No public discussion or profile screenshot.</p>", "FLOW": flow("#5a2d91", "Private warm-up · 5", "Where do career assumptions come from?") + flow("#4a9d2f", "Xello lesson · 30", "Home > Lessons > Biases and career choices.") + flow("#1f617a", "Private reflection · 12", "Assumption, career fact, fair next move.") + flow("#e3ad19", "Report/catch-up · 3", "Verify or schedule supervised completion."), "MONITOR": "<p>Activity 2 has no prerequisite. The extended Activity 3 recommends Matchmaker and asks students to revisit a discounted career; it is not today's completion minimum. Protect privacy: students may write about general cultural/media assumptions and are never required to disclose identity or discrimination experiences.</p>", "RESOURCES": f'<p>{file_link(files["XELLO_DECK"]["id"], "Official teacher deck with speaker notes")} · {file_link(files["XELLO_GUIDE"]["id"], "Full licensed facilitator package")}. No downloadable student video was present in the captured package; do not invent or scrape one.</p>', "SUPPORT": "<p>Use the official slides, read prompts aloud, permit a private pass on discussion, and offer bilingual labels and teacher conference. The one-page reflection provides three separate response areas instead of one dense paragraph box.</p>", "FALLBACK": "<p>If Xello fails, students use the fixed Plant-Tech Guide for the private reflection and complete Xello in supervised catch-up. Paper does not count as platform completion.</p>"},
        }

        day_names = {1: "Diagnose a Grow System", 2: "Plan a Farm-to-Table Infographic", 3: "Build and Test the Infographic", 4: "Evaluate Emerging Plant-Tech Work", 5: "Xello Biases and Career Choices"}
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_header(client, module["id"], header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 3SW Wk2 Day {day} - {day_names[day]}"
            student_page = await upsert_page(client, student_title, render("3sw-wk2-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, **student[day]}))
            teacher_title = f"TEACHER: 3SW Wk2 Day {day} Facilitator Guide"
            teacher_page = await upsert_page(client, teacher_title, render("3sw-wk2-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **teacher[day]}))
            await upsert_module_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await upsert_module_item(client, module["id"], "Page", student_page["url"], student_title)
            pages[day] = {"teacher": teacher_page, "student": student_page}
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title)]
            if day == 4:
                await upsert_module_item(client, module["id"], "Quiz", quiz["id"], QUIZ_TITLE)
                await upsert_module_item(client, module["id"], "Assignment", packet["id"], PACKET_TITLE)
                order += [("Quiz", quiz["id"], QUIZ_TITLE), ("Assignment", packet["id"], PACKET_TITLE)]
            if day == 5:
                await upsert_module_item(client, module["id"], "Assignment", reflection["id"], REFLECTION_TITLE)
                order.append(("Assignment", reflection["id"], REFLECTION_TITLE))

        items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(entry for entry in items if (kind == "SubHeader" and entry.get("id") == key) or (kind == "Page" and entry.get("page_url") == key) or (kind in ("Quiz", "Assignment") and entry.get("content_id") == key))
            await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}", data={"module_item[position]": position, "module_item[title]": title})

        final_items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        module = await api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        groups = await paged(client, f"/courses/{COURSE_ID}/assignment_groups")
        print(json.dumps({
            "module": {"id": module["id"], "published": module["published"]},
            "quiz": {"id": quiz["id"], "published": quiz.get("published")},
            "assignments": {"packet": {"id": packet["id"], "published": packet.get("published"), "grading_type": packet.get("grading_type")}, "reflection": {"id": reflection["id"], "published": reflection.get("published"), "grading_type": reflection.get("grading_type")}},
            "assignment_groups": [{"id": group["id"], "name": group["name"], "group_weight": group.get("group_weight")} for group in groups],
            "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
            "folders": {str(day): {"id": folder["id"], "locked": folder["locked"]} for day, folder in folders.items()},
            "files": {key: value["id"] for key, value in files.items()},
            "pages": {str(day): {kind: {"url": value["url"], "published": value["published"]} for kind, value in pair.items()} for day, pair in pages.items()},
            "items": [{"id": item["id"], "position": item["position"], "title": item["title"], "type": item["type"], "page_url": item.get("page_url")} for item in final_items],
        }, indent=2))


asyncio.run(main())
