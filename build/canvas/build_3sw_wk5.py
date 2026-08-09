"""Build the unpublished 3SW Week 5 Cosmetology Canvas module."""

import asyncio
import json
import mimetypes
import re
import sys
from pathlib import Path

import httpx


BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
MODULE_NAME = "3SW Wk5: Style, Service, and Cosmetology Careers"
QUIZ_TITLE = "PRACTICE: Texas Cosmetology License and Safety Check"
RECOMMENDATION_TITLE = "MINOR 3: Cosmetology Career and Business Recommendation"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/3sw/wk5"


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
    ("Q1 - Operator course", "What does the current Texas Cosmetology Operator route require before the exams?", "A 1,000-hour operator course at a TDLR-licensed school.", ["A 500-hour online course from any website.", "An informal apprenticeship with any salon owner.", "Only a high school diploma."], "Correct. The course must be 1,000 hours at a licensed school.", "The current TDLR operator page does not list an informal apprenticeship route."),
    ("Q2 - Exams", "Which exams does the current Texas Cosmetology Operator route require?", "A written exam and a practical exam.", ["Only a written exam.", "Only a practical exam.", "No exam after the training hours."], "Correct. Both exams are required.", "Recheck the dated TDLR evidence guide: written and practical exams are separate steps."),
    ("Q3 - Unknown local facts", "The evidence guide does not give the exact family cost of an Irving ISD route. What should a student do?", "Ask the current counselor, CTE office, or coursebook and label the fact as unknown until verified.", ["Write $0 because it is a public school.", "Copy the price of a private school.", "Skip the question and claim cost does not matter."], "Correct. A useful decision separates verified facts from unanswered local questions.", "Do not invent cost, hours, transportation, or admission information."),
    ("Q4 - Wage label", "The evidence guide lists $16.95 per hour. What does that number mean?", "May 2024 U.S. median hourly wage for hairdressers, hairstylists, and cosmetologists.", ["Guaranteed DFW starting pay.", "The minimum wage for every Texas salon.", "The exact pay after one year."], "Correct. Keep the year, geography, occupation, and measure attached.", "The figure is a national median, not local starting pay or a guarantee."),
    ("Q5 - Lab boundary", "Where may a student build the classroom SFX texture model?", "On the teacher-approved practice surface or in an approved digital tool.", ["On a classmate's arm.", "On the student's face.", "On clothing that someone is wearing."], "Correct. Classroom materials never go on a person.", "The lab boundary is non-negotiable: practice surface or approved digital tool only."),
]


async def upsert_quiz(client):
    quizzes = await paged(client, f"/courses/{COURSE_ID}/quizzes")
    quiz = next((entry for entry in quizzes if entry.get("title") == QUIZ_TITLE), None)
    data = {"quiz[title]": QUIZ_TITLE, "quiz[description]": "<p>Ungraded practice. Retry and use the feedback before writing the pathway decision.</p>", "quiz[quiz_type]": "practice_quiz", "quiz[published]": "false", "quiz[allowed_attempts]": "-1", "quiz[show_correct_answers]": "true", "quiz[shuffle_answers]": "false"}
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
        support = "course files/CCR Materials/3SW/Wk5"
        support_folder = await ensure_folder(client, support)
        names = {
            "CONCEPT": "3sw-wk5-sfx-concept-lab-brief.pdf",
            "QUALITY": "3sw-wk5-sfx-quality-revision.pdf",
            "EVIDENCE": "3sw-wk5-texas-cosmetology-evidence-guide.pdf",
            "PATHWAY": "3sw-wk5-cosmetology-pathway-decision.pdf",
            "CAMPAIGN": "3sw-wk5-salon-wellness-campaign.pdf",
            "RECOMMENDATION": "3sw-wk5-cosmetology-recommendation.pdf",
            "RUBRIC": "3sw-wk5-cosmetology-minor-rubric.pdf",
        }
        files = {key: await upload(client, ROOT / "docs/resources/worksheets" / name, support) for key, name in names.items()}
        quiz = await upsert_quiz(client)
        recommendation = await upsert_assignment(client, RECOMMENDATION_TITLE, "<p>Submit the private Cosmetology Career and Business Recommendation as text, file, or an approved audio response. Paper is equal. This remains unpublished and ungraded until the live Minor assignment group and 40/60 weighting are verified.</p>")

        selected_visuals = {
            1: ["fyf-human-services-opener.jpg", "fyf-sfx-research.jpg", "fyf-sfx-concept-card.jpg"],
            2: ["fyf-sfx-build.jpg"],
            3: ["fyf-sfx-quality-check.jpg"],
            4: ["fyf-stress-toolkit.jpg", "fyf-stress-posts.jpg"],
            5: ["fyf-irving-cosmetology-context.jpg", "fyf-student-enterprise-context.jpg"],
        }
        folders, visuals = {}, {}
        for day, day_names in selected_visuals.items():
            folder_path = f"course files/CCR Materials/3SW/Wk5/Day {day} Visuals"
            folders[day], visuals[day] = await ensure_folder(client, folder_path), {}
            for name in day_names:
                visuals[day][name] = await upload(client, ASSETS / f"day{day}" / name, folder_path)

        quiz_url = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        recommendation_url = f"/courses/{COURSE_ID}/assignments/{recommendation['id']}"

        student = {
            1: {"TITLE": "Human Services and SFX Texture Concept", "PURPOSE": "Plan a believable texture transformation and connect the design work to Human Services careers.", "TODAY": "<ul><li>identify Human Services careers;</li><li>explain texture and layering;</li><li>create a labeled texture map.</li></ul>", "READY": f'<p>Open {file_link(files["CONCEPT"]["id"], "the SFX Texture Concept and Lab Brief")} and gather colored pencils.</p>', "MEDIA": image_tag(visuals[1]["fyf-human-services-opener.jpg"]["id"], "Find Your Future Human Services cluster opener") + image_tag(visuals[1]["fyf-sfx-research.jpg"]["id"], "Find Your Future Special Effects Makeup research challenge") + image_tag(visuals[1]["fyf-sfx-concept-card.jpg"]["id"], "Find Your Future SFX texture style guide and concept card"), "STEPS": step(1, "Open the cluster", "<p>Name three Human Services careers and one task or client need for each.</p>") + step(2, "Read the challenge", "<p>Answer the prosthetic and texture questions. Rehearse aloud before writing if helpful.</p>") + step(3, "Choose one main texture", "<p>Select scaled, cracked, wrinkled, or rock/geode. Use at most one secondary texture.</p>") + step(4, "Draw the texture map", "<p>Label three layers or material choices and show where the texture spreads.</p>"), "EXIT": "<p>Name one Human Services career and one design skill that transfers to it.</p>", "DONE": "<ul><li>two research responses;</li><li>character and color plan;</li><li>one equal build route;</li><li>full labeled texture map.</li></ul>", "SUPPORT": "<p>texture = textura · layer = capa · scale = escama · crack = grieta. Use the embedded style guide and two teacher-selected texture choices.</p>", "FALLBACK": "<p>The PDF and three embedded pages are the full independent route. H&amp;L is optional and no screenshot is required.</p>"},
            2: {"TITLE": "Build and Test the SFX Texture Model", "PURPOSE": "Turn the texture map into a layered model, then test and revise it safely.", "TODAY": "<ul><li>build on an approved practice surface;</li><li>overlap at least three pieces or layers;</li><li>record a test and revision.</li></ul>", "READY": f'<p>Continue {file_link(files["CONCEPT"]["id"], "the SFX Lab Brief")} and use the teacher-approved dry, digital, or optional adhesive-lab route.</p><p><strong>Safety boundary:</strong> no classroom material goes on a person, clothing, face, arm, hair, or skin.</p>', "MEDIA": image_tag(visuals[2]["fyf-sfx-build.jpg"]["id"], "Find Your Future SFX build sequence; classroom safety routes replace direct skin application"), "STEPS": step(1, "Set the structure", "<p>Place the largest shape or digital layer first.</p>") + step(2, "Overlap", "<p>Add at least three visible layers that support the main texture.</p>") + step(3, "Test from three feet", "<p>Check whether the texture still reads clearly and whether pieces stay aligned.</p>") + step(4, "Record the change", "<p>Draw the result or note the private filename. Record one success, one problem, and one revision.</p>"), "EXIT": "<p>A model has many details but no clear main texture. What should the artist change first, and why?</p>", "DONE": "<ul><li>approved practice surface;</li><li>three overlapping layers;</li><li>test record;</li><li>one revision;</li><li>clean work area.</li></ul>", "SUPPORT": "<p>overlap = superponer · align = alinear · revise = revisar. Pre-cut paper and a digital layered mockup are equal.</p>", "FALLBACK": "<p>Use the dry relief or digital route. An adhesive lab is never required for absence recovery or grading.</p>"},
            3: {"TITLE": "Quality Check and Texas Cosmetology Pathways", "PURPOSE": "Use visible evidence to revise a design and current sources to compare two training settings.", "TODAY": "<ul><li>rate and revise the SFX model;</li><li>identify Texas license steps;</li><li>compare high-school and postsecondary training.</li></ul>", "READY": f'<p>Open {file_link(files["QUALITY"]["id"], "the SFX Quality Check")}, {file_link(files["EVIDENCE"]["id"], "the dated Texas evidence guide")}, and {file_link(files["PATHWAY"]["id"], "the Pathway Decision")}.</p>', "MEDIA": image_tag(visuals[3]["fyf-sfx-quality-check.jpg"]["id"], "Find Your Future SFX quality check, problem solving, and improvement plan"), "STEPS": step(1, "Rate the evidence", "<p>Use texture, stability, and plan-match criteria. Draw a three-label revision.</p>") + step(2, "Mark the current facts", "<p>Box 1,000 hours; underline both exams; star age and fee; bracket the current Irving ISD campus list.</p>") + step(3, "Compare two settings", "<p>Do not invent cost, schedule, transportation, admission, or high-school hours.</p>") + step(4, "Check misconceptions", f'<p><a href="{quiz_url}">Open the license and safety practice check</a>. Retry and use the feedback.</p>'), "EXIT": "<p>What state requirement stays the same in both settings, and what local question could change the decision?</p>", "DONE": "<ul><li>quality ratings and revision;</li><li>two-setting comparison;</li><li>one verified fact and one unanswered question;</li><li>five license steps in order.</li></ul>", "SUPPORT": "<p>license = licencia · training = capacitación · exam = examen · fee = tarifa. Read one evidence section at a time.</p>", "FALLBACK": "<p>The fixed guide and worksheets contain every required fact. No live TDLR navigation or partner is required.</p>"},
            4: {"TITLE": "Salon Entrepreneurship and Wellness Communication", "PURPOSE": "Design a fictional beauty business and one useful, safe wellness campaign post.", "TODAY": "<ul><li>define a business opportunity;</li><li>identify owner responsibilities;</li><li>create and revise one private campaign post.</li></ul>", "READY": f'<p>Open {file_link(files["CAMPAIGN"]["id"], "the Salon and Wellness Campaign Brief")}. Paper, Canva, and Adobe Express are equal.</p><p>Use a fictional business and customer. Do not create a real account or public post.</p>', "MEDIA": image_tag(visuals[4]["fyf-stress-toolkit.jpg"]["id"], "Find Your Future Stress Toolkit technique table") + image_tag(visuals[4]["fyf-stress-posts.jpg"]["id"], "Find Your Future three-post campaign and partner review directions"), "STEPS": step(1, "Define the business", "<p>Name the service, fictional customer, location type, meaningful difference, and one owner skill.</p>") + step(2, "Sketch the customer experience", "<p>Label service, scheduling, sanitation, access, and records or inventory.</p>") + step(3, "Create one polished post", "<p>Use one technique, a headline, plain explanation, realistic tip, and visual. Plan two more posts without polishing them.</p>") + step(4, "Run the safety check", "<p>Remove medical advice, guaranteed results, real details, and unclear language. Record one revision.</p>"), "EXIT": "<p>How can a useful post build trust without replacing professional help?</p>", "DONE": "<ul><li>complete business concept;</li><li>one polished fictional post;</li><li>two rough post plans;</li><li>reader and safety check;</li><li>one revision.</li></ul>", "SUPPORT": "<p>customer = cliente · owner = propietario · wellness = bienestar · trust = confianza. Private self-check is equal to partner feedback.</p>", "FALLBACK": "<p>The PDF and embedded pages are the complete route. No public post, real account, or personal wellness disclosure is required.</p>"},
            5: {"TITLE": "Cosmetology Career and Business Recommendation", "PURPOSE": "Use the week's evidence to recommend one Human Services career and explain a related business opportunity.", "TODAY": "<ul><li>audit the evidence;</li><li>plan five evidence jobs;</li><li>write, self-score, revise, and submit privately.</li></ul>", "READY": f'<p>Open {file_link(files["RECOMMENDATION"]["id"], "the recommendation")}, {file_link(files["RUBRIC"]["id"], "the 16-point rubric")}, and {file_link(files["EVIDENCE"]["id"], "the Texas evidence guide")}.</p>', "MEDIA": image_tag(visuals[5]["fyf-irving-cosmetology-context.jpg"]["id"], "Find Your Future Irving ISD cosmetology program context") + image_tag(visuals[5]["fyf-student-enterprise-context.jpg"]["id"], "Find Your Future student enterprise, license, and SkillsUSA context"), "STEPS": step(1, "Audit the evidence", "<p>Check the career task, Texas requirement, current next step, owner responsibility, and tradeoff.</p>") + step(2, "Plan for Jordan", "<p>Complete all five planning fields before drafting.</p>") + step(3, "Write and connect", "<p>Write 6-8 sentences, then connect one design decision to a career skill.</p>") + step(4, "Self-score and submit", f'<p>Revise one weak criterion, then <a href="{recommendation_url}">open the private recommendation assignment</a> or submit the paper copy.</p>'), "EXIT": "<p>Which evidence changed the recommendation most, and why do the other factors still matter?</p>", "DONE": "<ul><li>6-8 sentence recommendation;</li><li>accurate task and Texas fact;</li><li>verified next step;</li><li>opportunity, responsibility, and tradeoff;</li><li>design-to-career connection;</li><li>rubric revision.</li></ul>", "SUPPORT": "<p>recommendation = recomendación · evidence = evidencia · responsibility = responsabilidad · tradeoff = compensación. Typed, speech-to-text, and approved audio are equal.</p>", "FALLBACK": "<p>The fixed packet is the full route. Xello Career Factors, eDynamic 4.2, and H&amp;L favorites are optional extensions only.</p>"},
        }

        teacher = {
            1: {"TITLE": "Human Services and SFX Texture Concept", "SUBTITLE": "50 minutes · TEKS d(1)(B), d(1)(C)", "ALERT": "<strong>Fixed evidence first.</strong> H&amp;L exploration is optional; every student leaves with the same concept evidence.", "PREP": f'<ul><li>Post {file_link(files["CONCEPT"]["id"], "the concept brief")}.</li><li>Project the three licensed workbook pages.</li><li>Prepare one strong texture map and one cluttered non-example.</li></ul>', "EVIDENCE": "<p>Two research responses, complete concept fields, route choice, and full-page labeled texture map. Formative.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "Notice visible texture clues.") + flow("#4a9d2f", "Human Services · 8", "Three careers and client needs.") + flow("#1f617a", "SFX research · 10", "Prosthetic, texture, layering.") + flow("#e3ad19", "Concept map · 22", "One main texture, materials, colors, labels.") + flow("#1f617a", "Exit · 5", "Career and transferable design skill."), "MONITOR": "<p>Minute 10 of planning: main texture and build route. Minute 17: at least three labels. Do not accept an overloaded mix of unrelated textures. Score the plan, not drawing polish.</p>", "RESOURCES": "<p>Licensed FYF pp. 127-129 are embedded. H&amp;L p. 138 App Exploration is an optional extension, not required evidence.</p>", "SUPPORT": "<p>Offer a texture photo bank, two selected choices, and oral rehearsal. The brief reserves a full page for the labeled map.</p>", "FALLBACK": "<p>No platform is required. An absent student uses the same embedded pages and brief independently.</p>"},
            2: {"TITLE": "Build and Test the SFX Texture Model", "SUBTITLE": "50 minutes · TEKS d(1)(C)", "ALERT": "<strong>Dry or digital is the turnkey core.</strong> Adhesive work is optional only after the full campus safety gate.", "PREP": f'<ul><li>Continue {file_link(files["CONCEPT"]["id"], "the lab brief")}.</li><li>Prepare dry relief kits and cardstock practice boards.</li><li>Test the digital route if offered.</li><li>Do not require food, seeds, pasta, salt, latex, or eyelash glue.</li></ul>', "EVIDENCE": "<p>Approved-surface model, three overlapping layers, three-part test record, and one revision. Formative.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "Name the three essential layers.") + flow("#4a9d2f", "Safety and demo · 8", "Surface, order, overlap, test, cleanup.") + flow("#1f617a", "Build · 25", "Structure first, then detail.") + flow("#e3ad19", "Test and revise · 7", "View from three feet and record evidence.") + flow("#1f617a", "Exit · 5", "Fix the missing main texture."), "MONITOR": "<p>Minute 10: main structure present. Minute 18: three overlapping layers. Fabrication route does not affect the score. A failed model remains usable evidence when the student tests and revises it.</p>", "RESOURCES": "<p>Licensed FYF p. 130 is embedded as source context. The Canvas directions set the classroom safety route.</p>", "SUPPORT": "<p>Use pre-cut dry materials, two route cards, speech-to-text, and a digital mockup. All writing jobs have separate lines.</p>", "FALLBACK": "<p>No material on a person. Paper relief and digital layers are full absence routes. Optional adhesive work requires product label, SDS, allergy, ventilation, approved surface, supervision, storage, and cleanup checks.</p>"},
            3: {"TITLE": "Quality Check and Texas Cosmetology Pathways", "SUBTITLE": "50 minutes · TEKS d(2)(A), d(3)(G)", "ALERT": "<strong>Corrected legal route.</strong> Do not teach the unsupported Texas cosmetology apprenticeship from the earlier draft.", "PREP": f'<ul><li>Post {file_link(files["QUALITY"]["id"], "the quality sheet")}, {file_link(files["EVIDENCE"]["id"], "the dated evidence guide")}, and {file_link(files["PATHWAY"]["id"], "the pathway decision")}.</li><li>Open the unpublished practice Quiz.</li></ul>', "EVIDENCE": "<p>Design revision, complete two-setting comparison, one verified fact, one unanswered local question, and ordered license steps. Recommended Week 5 minor packet evidence.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "What held and what needs rebuilding?") + flow("#4a9d2f", "Quality and revision · 10", "Three criteria and labeled redesign.") + flow("#1f617a", "Read evidence · 15", "Mark the current Texas and district facts.") + flow("#e3ad19", "Pathway decision · 15", "Compare settings; do not invent unknowns.") + flow("#1f617a", "Exit · 5", "Shared requirement and local question."), "MONITOR": "<p>Key: 1,000-hour course at a licensed school; written exam eligibility after 900 reported hours; practical after 1,000 hours and written exam; age 17; $50 application; two-year license. Current district page lists Cardwell, Irving, MacArthur, and Nimitz. Either setting can fit Alex when the reasoning uses a verified fact and unanswered question.</p>", "RESOURCES": '<p><a href="https://www.tdlr.texas.gov/barbering-and-cosmetology/individuals/apply-cosmetologist.htm">Current TDLR operator requirements</a> · <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte">Current Irving ISD High School CTE</a> · <a href="https://www.bls.gov/ooh/personal-care-and-service/barbers-hairstylists-and-cosmetologists.htm">BLS occupation profile</a></p>', "SUPPORT": "<p>Read one section at a time, pre-highlight labels, and allow oral rehearsal. The recommendation gets six full-width lines and the enrollment questions have separate fields.</p>", "FALLBACK": "<p>The fixed evidence guide is load-bearing; live navigation is optional. Treat workbook salon details as context until locally confirmed.</p>"},
            4: {"TITLE": "Salon Entrepreneurship and Wellness Communication", "SUBTITLE": "50 minutes · TEKS d(3)(I)", "ALERT": "<strong>One polished post is enough.</strong> Two additional headlines preserve the three-part campaign without an impossible design sprint.", "PREP": f'<ul><li>Post {file_link(files["CAMPAIGN"]["id"], "the campaign brief")}.</li><li>Project the two licensed workbook pages.</li><li>Prepare a safe model and an unsupported-promise non-example.</li></ul>', "EVIDENCE": "<p>Business concept, customer-experience sketch, one polished fictional post, two rough plans, safety check, and one revision. Formative.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "Service plus owner responsibility.") + flow("#4a9d2f", "Define the business · 12", "Customer, difference, skill, service map.") + flow("#1f617a", "Read the toolkit · 8", "Choose three different techniques.") + flow("#e3ad19", "Create and test · 20", "One polished post, two rough plans, revision.") + flow("#1f617a", "Exit · 5", "Trust without medical advice."), "MONITOR": "<p>Reject guaranteed outcomes, diagnoses, treatment language, real handles, names, locations, and contact details. Do not score artwork or tool choice. A private self-check is equal to partner review.</p>", "RESOURCES": "<p>Licensed FYF pp. 132-133 are embedded. Canva and Adobe Express are optional approved production tools.</p>", "SUPPORT": "<p>Offer two fictional customers, a headline bank, and a strong/unsafe model pair. The design page has a large post area and separate revision lines.</p>", "FALLBACK": "<p>No public account or post. Students do not disclose personal wellness information. Paper is equal.</p>"},
            5: {"TITLE": "Cosmetology Career and Business Recommendation", "SUBTITLE": "50 minutes · TEKS d(1)(C), d(2)(A), d(3)(G), d(3)(I)", "ALERT": "<strong>Recommended 16-point minor, not yet configured.</strong> Keep the Assignment unpublished and ungraded until the live Minor group and 40/60 weighting are verified.", "PREP": f'<ul><li>Post {file_link(files["RECOMMENDATION"]["id"], "the recommendation")}, {file_link(files["RUBRIC"]["id"], "the rubric")}, and {file_link(files["EVIDENCE"]["id"], "the evidence guide")}.</li><li>Open the private unpublished Assignment.</li></ul>', "EVIDENCE": "<p>Individual 6-8 sentence recommendation plus one design-to-career connection and rubric revision.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "Rank Jordan's decision factors.") + flow("#4a9d2f", "Audit · 8", "Task, Texas fact, next step, opportunity, tradeoff.") + flow("#1f617a", "Plan · 8", "Five separate evidence jobs.") + flow("#e3ad19", "Write and connect · 22", "Recommendation plus transferable skill.") + flow("#1f617a", "Self-score and submit · 7", "Revise one weak criterion."), "MONITOR": "<p>Any Human Services career may earn full credit. Recommended bands after approval: 15-16 Masters, 13-14 Meets, 12 Approaches, 10-11 Needs Improvement. Score reasoning and evidence, not English mechanics unless meaning is unclear.</p>", "RESOURCES": "<p>The current district context is embedded. Xello Career Factors, eDynamic 4.2, and H&amp;L favorites are supplemental extensions only.</p>", "SUPPORT": "<p>Use numbered planning fields, oral rehearsal, speech-to-text, or approved audio. Ten full-width lines support the 6-8 sentence response.</p>", "FALLBACK": "<p>The fixed guide, prompt, and rubric are the complete independent route. No screenshot, favorite count, public post, or partner is required.</p>"},
        }

        day_names = {1: "Human Services and SFX Concept", 2: "Build and Test the Texture Model", 3: "Quality and Texas Pathways", 4: "Salon and Wellness Campaign", 5: "Career and Business Recommendation"}
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 3SW Wk5 Day {day} - {day_names[day]}"
            student_page = await upsert_page(client, student_title, render("3sw-wk5-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, **student[day]}))
            teacher_title = f"TEACHER: 3SW Wk5 Day {day} Facilitator Guide"
            teacher_page = await upsert_page(client, teacher_title, render("3sw-wk5-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **teacher[day]}))
            await upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            pages[day] = {"teacher": teacher_page, "student": student_page}
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title)]
            if day == 3:
                await upsert_item(client, module["id"], "Quiz", quiz["id"], QUIZ_TITLE)
                order.append(("Quiz", quiz["id"], QUIZ_TITLE))
            if day == 5:
                await upsert_item(client, module["id"], "Assignment", recommendation["id"], RECOMMENDATION_TITLE)
                order.append(("Assignment", recommendation["id"], RECOMMENDATION_TITLE))

        items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(entry for entry in items if (kind == "SubHeader" and entry.get("id") == key) or (kind == "Page" and entry.get("page_url") == key) or (kind in ("Quiz", "Assignment") and entry.get("content_id") == key))
            await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}", data={"module_item[position]": position, "module_item[title]": title})

        final_items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        module = await api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        print(json.dumps({
            "module": {"id": module["id"], "published": module["published"]},
            "quiz": {"id": quiz["id"], "published": quiz.get("published"), "quiz_type": quiz.get("quiz_type"), "allowed_attempts": quiz.get("allowed_attempts")},
            "recommendation": {"id": recommendation["id"], "published": recommendation.get("published"), "grading_type": recommendation.get("grading_type"), "submission_types": recommendation.get("submission_types")},
            "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
            "folders": {str(day): {"id": folder["id"], "locked": folder["locked"]} for day, folder in folders.items()},
            "files": {key: value["id"] for key, value in files.items()},
            "pages": {str(day): {kind: {"url": value["url"], "published": value["published"]} for kind, value in pair.items()} for day, pair in pages.items()},
            "items": [{"id": item["id"], "position": item["position"], "title": item["title"], "type": item["type"], "page_url": item.get("page_url")} for item in final_items],
        }, indent=2))


asyncio.run(main())
