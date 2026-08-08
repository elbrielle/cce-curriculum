"""Build the unpublished 3SW Week 4 Culinary Arts and Hospitality Canvas module."""

import asyncio
import json
import mimetypes
import re
import sys
from pathlib import Path

import httpx


BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
MODULE_NAME = "3SW Wk4: Culinary Arts and Hospitality"
ANNOTATION_TITLE = "PRACTICE: Culinary Twist Menu Design"
QUIZ_TITLE = "PRACTICE: Motivation Check"
RECOMMENDATION_TITLE = "PRACTICE: Hospitality Career and Business Recommendation"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/3sw/wk4"


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


async def upsert_assignment(client, title, description, submission_types, annotatable_attachment_id=None):
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    found = next((entry for entry in assignments if entry.get("name") == title), None)
    data = {
        "assignment[name]": title,
        "assignment[description]": description,
        "assignment[submission_types][]": submission_types,
        "assignment[grading_type]": "not_graded",
        "assignment[points_possible]": "0",
        "assignment[published]": "false",
    }
    if annotatable_attachment_id:
        data["assignment[annotatable_attachment_id]"] = str(annotatable_attachment_id)
    return await api(client, "PUT" if found else "POST", f"/courses/{COURSE_ID}/assignments/{found['id']}" if found else f"/courses/{COURSE_ID}/assignments", data=data)


QUESTIONS = [
    ("Q1 - Intrinsic motivation", "Which example is primarily intrinsic motivation?", "A baker keeps practicing because improving the technique feels satisfying.", ["A baker receives a cash prize.", "A baker avoids losing a shift.", "A baker earns a gift card."], "Correct. The motivation comes from satisfaction in the work itself.", "Intrinsic motivation comes from interest, purpose, or satisfaction in the task."),
    ("Q2 - Extrinsic motivation", "Which example is primarily extrinsic motivation?", "A hotel team earns a bonus for meeting a service goal.", ["A planner enjoys solving a complex seating problem.", "A chef feels proud after mastering a technique.", "A manager likes helping a new employee improve."], "Correct. The bonus is an outside reward.", "Extrinsic motivation comes from an outside reward or consequence."),
    ("Q3 - Motivation differences", "Why might the same reward affect two workers differently?", "People value different rewards and may respond differently to the same incentive.", ["One worker must be dishonest.", "Intrinsic motivation always works better.", "Every employee responds to money in the same way."], "Correct. Motivation is personal and context matters.", "Do not assume one motivator works the same way for everyone."),
    ("Q4 - Data label", "The evidence guide lists $68,130 for Lodging Managers. What does that number mean?", "May 2024 U.S. median annual pay.", ["Guaranteed DFW starting pay.", "The minimum salary for every hotel manager.", "The amount every manager earns after one year."], "Correct. Keep the year, geography, and measure attached.", "The figure is a national median, not local starting pay or a guarantee."),
]


async def upsert_quiz(client):
    quizzes = await paged(client, f"/courses/{COURSE_ID}/quizzes")
    quiz = next((entry for entry in quizzes if entry.get("title") == QUIZ_TITLE), None)
    data = {"quiz[title]": QUIZ_TITLE, "quiz[description]": "<p>Ungraded practice. Retry and use the feedback before completing the written motivation plan.</p>", "quiz[quiz_type]": "practice_quiz", "quiz[published]": "false", "quiz[allowed_attempts]": "-1", "quiz[show_correct_answers]": "true", "quiz[shuffle_answers]": "false"}
    quiz = await api(client, "PUT" if quiz else "POST", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}" if quiz else f"/courses/{COURSE_ID}/quizzes", data=data)
    existing = await paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    for position, (name, text, correct, wrong, correct_comment, incorrect_comment) in enumerate(QUESTIONS, 1):
        found = next((question for question in existing if question.get("question_name") == name), None)
        payload = {"question": {"question_name": name, "question_text": text, "question_type": "multiple_choice_question", "position": position, "points_possible": 1, "correct_comments": correct_comment, "incorrect_comments": incorrect_comment, "answers": [{"answer_text": correct, "answer_weight": 100}] + [{"answer_text": answer, "answer_weight": 0} for answer in wrong]}}
        await api(client, "PUT" if found else "POST", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions", json=payload)
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
        support = "course files/CCR Materials/3SW/Wk4"
        support_folder = await ensure_folder(client, support)
        names = {
            "CAREERS": "3sw-wk4-hospitality-career-evidence-guide.pdf",
            "MENU": "3sw-wk4-culinary-twist-menu-brief.pdf",
            "MOTIVATION": "3sw-wk4-motivation-career-comparison.pdf",
            "CARDS": "3sw-wk4-hotel-rescue-cards.pdf",
            "RESPONSE": "3sw-wk4-hotel-rescue-response.pdf",
            "EVENT": "3sw-wk4-cater-create-event-brief.pdf",
            "RECOMMENDATION": "3sw-wk4-hospitality-recommendation.pdf",
            "RUBRIC": "3sw-wk4-hospitality-minor-rubric.pdf",
        }
        files = {key: await upload(client, ROOT / "docs/resources/worksheets" / name, support) for key, name in names.items()}
        annotation = await upsert_assignment(client, ANNOTATION_TITLE, "<p>Design directly on the Culinary Twist Menu Brief with Canvas annotation, or submit a file or text explanation. Paper, Canva, and Adobe Express are equal routes.</p>", ["student_annotation", "online_upload", "online_text_entry"], files["MENU"]["id"])
        recommendation = await upsert_assignment(client, RECOMMENDATION_TITLE, "<p>Submit the private five-to-seven-sentence Hospitality Career and Business Recommendation as text or a file. This remains unpublished and ungraded until the live Minor assignment group and 40/60 weighting are verified.</p>", ["online_upload", "online_text_entry"])
        quiz = await upsert_quiz(client)

        selected_visuals = {
            1: ["fyf-hospitality-opener-optimized.jpg", "fyf-culinary-twist-plan.png", "fyf-culinary-twist-menu.png"],
            2: ["fyf-motivation-types.png", "fyf-motivation-plan.png"],
            3: ["fyf-hotel-rescue-roles.png", "fyf-hotel-rescue-solutions.png"],
            4: ["fyf-cater-create-menu.png", "fyf-cater-create-experience.png"],
            5: ["fyf-irving-hospitality-context.png"],
        }
        folders, visuals = {}, {}
        for day, names_for_day in selected_visuals.items():
            folder_path = f"course files/CCR Materials/3SW/Wk4/Day {day} Visuals"
            folders[day], visuals[day] = await ensure_folder(client, folder_path), {}
            for name in names_for_day:
                visuals[day][name] = await upload(client, ASSETS / f"day{day}" / name, folder_path)

        annotation_url = f"/courses/{COURSE_ID}/assignments/{annotation['id']}"
        quiz_url = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        recommendation_url = f"/courses/{COURSE_ID}/assignments/{recommendation['id']}"

        student = {
            1: {"TITLE": "Culinary Twist Menu Design", "PURPOSE": "Create a menu item that responds to an ingredient constraint and communicates clearly to a customer.", "TODAY": "<ul><li>explore hospitality work;</li><li>plan a fictional dish;</li><li>design, test, and revise a menu item.</li></ul>", "READY": f'<p>Open {file_link(files["MENU"]["id"], "the Culinary Twist Menu Brief")} or <a href="{annotation_url}">open the Canvas annotation activity</a>. Paper, Canva, and Adobe Express are equal.</p><p><strong>Safety boundary:</strong> this is a design task. Do not prepare or taste food.</p>', "MEDIA": image_tag(visuals[1]["fyf-hospitality-opener-optimized.jpg"]["id"], "Find Your Future hospitality and tourism cluster opener") + image_tag(visuals[1]["fyf-culinary-twist-plan.png"]["id"], "Find Your Future Culinary Twist ingredient and preparation planning directions") + image_tag(visuals[1]["fyf-culinary-twist-menu.png"]["id"], "Find Your Future Culinary Twist menu design directions"), "STEPS": step(1, "Choose the guest need", "<p>Name the event or customer and one need such as access, comfort, cost, safety, or enjoyment.</p>") + step(2, "Plan within constraints", "<p>Choose four or five base ingredients. Add the assigned special ingredient and explain what it changes.</p>") + step(3, "Create the menu item", "<p>Add a dish name, price, two- or three-sentence description, and at least three sketch labels.</p>") + step(4, "Run the reader test", "<p>Can a customer identify the dish, main ingredients, special ingredient, and price? Revise one unclear part.</p>"), "EXIT": "<p>Which skill transfers best to another career: working with constraints, describing a product, pricing, or visual communication? Give one example.</p>", "DONE": "<ul><li>all four menu elements;</li><li>three sketch labels;</li><li>one reader revision;</li><li>one transferable-skill connection.</li></ul>", "SUPPORT": "<p>dish = plato · ingredient = ingrediente · menu = menú · price = precio · customer = cliente. A labeled plate outline is included. Rehearse the description aloud before writing.</p>", "FALLBACK": "<p>The PDF and embedded source page are the complete absence route. Save a digital copy or bring the paper brief to class.</p>"},
            2: {"TITLE": "Motivation and Three-Career Comparison", "PURPOSE": "Use motivation ideas and one fixed evidence set to compare three hospitality careers.", "TODAY": "<ul><li>distinguish intrinsic and extrinsic motivation;</li><li>design a short competition plan;</li><li>compare three careers using the same measures.</li></ul>", "READY": f'<p>Open {file_link(files["MOTIVATION"]["id"], "the Motivation and Career Comparison")} and {file_link(files["CAREERS"]["id"], "the Hospitality Career Evidence Guide")}.</p>', "MEDIA": image_tag(visuals[2]["fyf-motivation-types.png"]["id"], "Find Your Future intrinsic and extrinsic motivation examples") + image_tag(visuals[2]["fyf-motivation-plan.png"]["id"], "Find Your Future professional baking competition planning page"), "STEPS": step(1, "Build a motivation plan", "<p>Give the competition one goal, two rules, an outside reward, and an intrinsic motivator. Explain why two bakers might respond differently.</p>") + step(2, "Check the idea", f'<p><a href="{quiz_url}">Open the Motivation Check</a>. Retry and use the feedback.</p>') + step(3, "Read the fixed career evidence", "<p>Compare Chef or Head Cook, Lodging Manager, and Event Planner. Keep year, geography, and measure attached to each number.</p>") + step(4, "Compare and recommend", "<p>Use one career fact, one motivation idea, and one tradeoff. The highest salary is not automatically the best fit.</p>"), "EXIT": "<p>Underline the year, geography, and measure attached to one number. Circle one motivation idea that transfers to more than one career.</p>", "DONE": "<ul><li>motivation plan complete;</li><li>all three career rows complete;</li><li>two careers compared;</li><li>fit decision uses evidence and a tradeoff.</li></ul>", "SUPPORT": "<p>motivation = motivación · median = mediana · preparation = preparación · reward = recompensa · tradeoff = compensación. Read one career row at a time.</p>", "FALLBACK": "<p>The two PDFs contain every required fact. Xello local data and H&amp;L browsing are optional additions, not replacements.</p>"},
            3: {"TITLE": "Hotel Rescue Team Response", "PURPOSE": "Use one hotel role to help solve a service crisis without making an unsafe or unverified promise.", "TODAY": "<ul><li>prepare one role response;</li><li>coordinate three or more roles;</li><li>transfer the process to a small business.</li></ul>", "READY": f'<p>Open {file_link(files["CARDS"]["id"], "the Hotel Rescue Role and Crisis Cards")} and {file_link(files["RESPONSE"]["id"], "the Team and Individual Response")}.</p>', "MEDIA": image_tag(visuals[3]["fyf-hotel-rescue-roles.png"]["id"], "Find Your Future Hotel Rescue roles and crisis choices") + image_tag(visuals[3]["fyf-hotel-rescue-solutions.png"]["id"], "Find Your Future Hotel Rescue solution planning page"), "STEPS": step(1, "Prepare your role", "<p>Complete the individual role page before the group discussion.</p>") + step(2, "Verify", "<p>Separate confirmed facts from unanswered questions.</p>") + step(3, "Protect and coordinate", "<p>Protect the safety, accessibility, reservation, or client requirement. Give at least three roles different actions.</p>") + step(4, "Communicate and follow through", "<p>Write a factual message with no unverified promise. Assign one role to check that the plan happened.</p>"), "EXIT": "<p>How would the same response process help a caterer, restaurant, lodging business, or event planner? Name what the owner sells or coordinates.</p>", "DONE": "<ul><li>individual role evidence;</li><li>team response map;</li><li>three coordinated roles;</li><li>factual message;</li><li>individual business transfer.</li></ul>", "SUPPORT": "<p>verify = verificar · guest = huésped · accessible = accesible · promise = promesa · follow through = dar seguimiento. Written role evidence is equal to acting.</p>", "FALLBACK": "<p>Select one role and crisis and complete the response independently. The packet includes enough space for every required response.</p>"},
            4: {"TITLE": "Cater and Create Client Experience", "PURPOSE": "Design a connected event experience that fits one client, feeling, and practical limit.", "TODAY": "<ul><li>define the client and business goal;</li><li>connect menu, space, and service choices;</li><li>test and revise the plan.</li></ul>", "READY": f'<p>Open {file_link(files["EVENT"]["id"], "the Cater and Create Event Brief")}.</p><p>Use a fictional client. Do not include a real name, address, contact information, payment detail, or public post.</p>', "MEDIA": image_tag(visuals[4]["fyf-cater-create-menu.png"]["id"], "Find Your Future Cater and Create menu directions") + image_tag(visuals[4]["fyf-cater-create-experience.png"]["id"], "Find Your Future Cater and Create event experience directions"), "STEPS": step(1, "Set the goal", "<p>Choose an event, feeling, client or audience, and one practical limit.</p>") + step(2, "Design the connected experience", "<p>Add three foods or drinks, a labeled space plan, entertainment, a take-home touch, and one accessibility choice.</p>") + step(3, "Check the business responsibility", "<p>Explain what the owner sells or coordinates and one responsibility beyond cooking.</p>") + step(4, "Run the client test", "<p>A partner, teacher, or self-check names one strength and one workable change. Make and record one revision.</p>"), "EXIT": "<p>Why might a client pay for the complete experience? Name one design detail and one business limit.</p>", "DONE": "<ul><li>client, feeling, and limit;</li><li>connected menu and space;</li><li>extra touches and accessibility choice;</li><li>owner responsibility;</li><li>one visible revision.</li></ul>", "SUPPORT": "<p>client = cliente · catering = servicio de banquetes · guest = invitado · limit = límite · revise = revisar. A labeled sketch is equal to a polished layout.</p>", "FALLBACK": "<p>The PDF is the complete independent route. Paper, Canva, Adobe Express, and another approved tool are equal.</p>"},
            5: {"TITLE": "Hospitality Career and Business Recommendation", "PURPOSE": "Use the week's evidence to recommend one career and explain a related business opportunity.", "TODAY": "<ul><li>audit the three-career evidence;</li><li>plan from Jordan's scenario;</li><li>write and self-score an individual recommendation.</li></ul>", "READY": f'<p>Open {file_link(files["RECOMMENDATION"]["id"], "the Hospitality Recommendation")}, {file_link(files["RUBRIC"]["id"], "the 16-point rubric")}, and {file_link(files["CAREERS"]["id"], "the fixed evidence guide")}.</p>', "MEDIA": image_tag(visuals[5]["fyf-irving-hospitality-context.png"]["id"], "Find Your Future Irving hospitality and culinary program context", 650), "STEPS": step(1, "Audit the evidence", "<p>Check the median, preparation, growth, openings, and work condition for all three careers. Correct any measure drift.</p>") + step(2, "Read Jordan's scenario", "<p>Mark the interests and constraints. Compare all three careers before selecting one.</p>") + step(3, "Write five to seven sentences", "<p>Use one career task, one correctly labeled number, one tradeoff, one business opportunity, and one verified local connection when relevant.</p>") + step(4, "Self-score and submit", f'<p>Revise one weak criterion, then <a href="{recommendation_url}">open the private recommendation assignment</a> or submit the paper copy.</p>'), "EXIT": "<p>Which evidence changed the recommendation most: the task, preparation route, or schedule? Why do the other two still matter?</p>", "DONE": "<ul><li>all three careers considered;</li><li>five to seven sentences;</li><li>number retains source meaning;</li><li>tradeoff and business opportunity;</li><li>rubric self-check.</li></ul>", "SUPPORT": "<p>recommendation = recomendación · evidence = evidencia · preparation = preparación · schedule = horario · business = negocio. Numbered sentence jobs and ten full-width writing lines are provided.</p>", "FALLBACK": "<p>The fixed guide, prompt, and rubric are the complete route. Xello Decision Making, eDynamic 6.1, and H&amp;L App Exploration are optional extensions only.</p>"},
        }

        teacher = {
            1: {"TITLE": "Culinary Twist Menu Design", "SUBTITLE": "50 minutes · TEKS d(1)(B), d(1)(C)", "ALERT": "<strong>Individual evidence comes first.</strong> Canvas annotation is a pilot; paper, Canva, and Adobe Express remain equal routes.", "PREP": f'<ul><li>Post {file_link(files["MENU"]["id"], "the menu brief")} and open the unpublished annotation activity.</li><li>Project the optimized hospitality opener and Culinary Twist directions.</li><li>Assign one special ingredient or offer two choices.</li></ul>', "EVIDENCE": "<p>Menu brief with four menu elements, three sketch labels, one reader revision, and one transferable-skill connection. Formative.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "What makes a food experience feel special?") + flow("#4a9d2f", "Open the cluster · 8", "Identify food and guest-experience work.") + flow("#1f617a", "Plan · 12", "Ingredients, constraint, preparation, customer result.") + flow("#e3ad19", "Build and test · 20", "Create the menu item and revise for a reader.") + flow("#1f617a", "Share and exit · 5", "Transfer one design skill."), "MONITOR": "<p>At minute 12, students should have the constraint and two preparation steps. At minute 25, they should have all four menu elements. Do not score art polish, public speaking, or tool choice. Do not let fictional allergen language become a safety guarantee.</p>", "RESOURCES": "<p>Licensed FYF pp. 111-113 are embedded. FYF Restaurant Rebrand is an optional extension.</p>", "SUPPORT": "<p>Offer a labeled plate outline, two special-ingredient choices, and a strong/flat description pair. The packet reserves a full page for the sketch and separate lines for the two- or three-sentence description.</p>", "FALLBACK": "<p>No food preparation or tasting. If annotation fails, use paper or an approved digital file. Collect the same evidence from every route.</p>"},
            2: {"TITLE": "Motivation and Three-Career Comparison", "SUBTITLE": "50 minutes · TEKS d(4)(B), d(5)(E)", "ALERT": "<strong>Use one fixed evidence set.</strong> The Quiz checks misconceptions; the written comparison is the evidence.", "PREP": f'<ul><li>Post {file_link(files["MOTIVATION"]["id"], "the comparison packet")} and {file_link(files["CAREERS"]["id"], "the evidence guide")}.</li><li>Open the unpublished practice Quiz.</li><li>Model intrinsic versus extrinsic without ranking one as morally better.</li></ul>', "EVIDENCE": "<p>Competition plan, complete three-career comparison, two-career motivation transfer, and evidence-based fit decision. Recommended minor packet evidence.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "Internal and external reasons.") + flow("#4a9d2f", "Motivation plan · 15", "Goal, rules, reward, intrinsic reason.") + flow("#1f617a", "Career evidence · 10", "Same measures for all three careers.") + flow("#e3ad19", "Compare and transfer · 15", "Use one fact and one tradeoff.") + flow("#1f617a", "Exit · 5", "Audit labels and transfer statement."), "MONITOR": "<p>Correct answers: satisfaction in improving is intrinsic; a bonus is extrinsic; people may respond differently to one incentive; $68,130 is a May 2024 U.S. median. Full written evidence compares all three careers and does not treat highest pay as automatic best fit.</p>", "RESOURCES": '<p><a href="https://www.bls.gov/ooh/food-preparation-and-serving/chefs-and-head-cooks.htm">BLS Chefs and Head Cooks</a> · <a href="https://www.bls.gov/ooh/management/lodging-managers.htm">BLS Lodging Managers</a> · <a href="https://www.bls.gov/ooh/business-and-financial/meeting-convention-and-event-planners.htm">BLS Event Planners</a></p>', "SUPPORT": "<p>Read one career row at a time, pre-highlight measure labels, and allow oral rehearsal. Each requested comparison has dedicated full-width writing space.</p>", "FALLBACK": "<p>The fixed PDFs carry the lesson. Xello localized data is optional only when geography, date, and measure remain visible. H&amp;L is optional.</p>"},
            3: {"TITLE": "Hotel Rescue Team Response", "SUBTITLE": "50 minutes · TEKS d(1)(C), d(3)(I)", "ALERT": "<strong>One crisis per team.</strong> Every student completes individual role evidence before discussion and an individual transfer after it.", "PREP": f'<ul><li>Post {file_link(files["CARDS"]["id"], "role and crisis cards")} and {file_link(files["RESPONSE"]["id"], "the response packet")}.</li><li>Choose teams of up to six and assign one crisis to each.</li><li>Prepare a teacher model for absent or unfinished groups.</li></ul>', "EVIDENCE": "<p>Individual role evidence, one coordinated team response, and individual small-business transfer. Formative.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "Verify before promising.") + flow("#4a9d2f", "Assign and prepare · 8", "One role and one crisis.") + flow("#1f617a", "Team response · 20", "Verify, protect, coordinate, communicate.") + flow("#e3ad19", "Read another response · 10", "Strong move plus risk or question.") + flow("#1f617a", "Individual transfer · 7", "Apply the process to a small business."), "MONITOR": "<p>Non-negotiables: do not ignore food safety to solve staffing; do not move a guest to a room that misses an accessibility requirement; do not promise a room, ride, payment, or refund before verification. Full response assigns at least three roles different actions and names follow-through.</p>", "RESOURCES": "<p>Licensed FYF pp. 117-118 are embedded. The custom packet separates role, team, review, and transfer evidence so group talk does not erase individual learning.</p>", "SUPPORT": "<p>Use role starters, complete Verify before grouping, and allow written participation instead of acting. The independent route uses the same role and crisis cards.</p>", "FALLBACK": "<p>An absent student completes one role and crisis independently using the teacher model for the comparison step. No peer post or live platform is required.</p>"},
            4: {"TITLE": "Cater and Create Client Experience", "SUBTITLE": "50 minutes · TEKS d(1)(C), d(3)(I)", "ALERT": "<strong>Design a service, not only a look.</strong> Client communication, staffing, cost, access, and risk are part of entrepreneurship.", "PREP": f'<ul><li>Post {file_link(files["EVENT"]["id"], "the event brief")}.</li><li>Project the licensed menu and experience pages.</li><li>Have paper tools ready; Canva and Adobe Express are optional equal routes.</li></ul>', "EVIDENCE": "<p>Client, feeling, practical limit, connected event design, owner responsibility, and one visible revision. Formative.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "Experience beyond food.") + flow("#4a9d2f", "Client and business goal · 8", "Event, feeling, audience, limit.") + flow("#1f617a", "Design · 27", "Menu, space, service, access, extra touches.") + flow("#e3ad19", "Client test · 5", "One strength and workable change.") + flow("#1f617a", "Exit · 5", "Value and owner responsibility."), "MONITOR": "<p>At minute 18 of design, check the practical limit. A coherent-looking plan still needs a realistic response to time, budget, staffing, space, allergies, accessibility, or weather. Do not collect real client data or require a public post.</p>", "RESOURCES": "<p>Licensed FYF pp. 119-120 are embedded. Current local context may include FireBird Cafe Catering, but do not turn an opportunity into a guarantee.</p>", "SUPPORT": "<p>Preselect an event and feeling, provide a word/color bank, and accept labeled sketches. The packet reserves a full page for the experience map and separate space for client feedback and revision.</p>", "FALLBACK": "<p>Paper is equal. Use fictional clients only; no real account, name, address, contact information, or payment details.</p>"},
            5: {"TITLE": "Hospitality Career and Business Recommendation", "SUBTITLE": "50 minutes · TEKS d(1)(C), d(3)(I), d(5)(E)", "ALERT": "<strong>Recommended 16-point minor, not yet configured.</strong> Keep the Assignment unpublished and ungraded until the live Minor group and 40/60 weighting are confirmed.", "PREP": f'<ul><li>Post {file_link(files["RECOMMENDATION"]["id"], "the recommendation")}, {file_link(files["RUBRIC"]["id"], "the student-visible rubric")}, and {file_link(files["CAREERS"]["id"], "the evidence guide")}.</li><li>Open the private unpublished Assignment.</li><li>Review current local program wording without promising admission, credentials, jobs, or salary.</li></ul>', "EVIDENCE": "<p>Individual five-to-seven-sentence recommendation using a task, correctly labeled number, tradeoff, business opportunity, and verified local connection when relevant.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "Rank decision factors.") + flow("#4a9d2f", "Audit evidence · 10", "Correct all five fields.") + flow("#1f617a", "Scenario plan · 10", "Compare all three careers.") + flow("#e3ad19", "Recommendation · 20", "Five to seven sentences with evidence.") + flow("#1f617a", "Self-score and submit · 5", "Revise one weak criterion."), "MONITOR": "<p>Any of the three careers can earn full credit when the task, evidence, tradeoff, and opportunity fit Jordan. Suggested conversion after local approval: 15-16 Masters, 13-14 Meets, 12 Approaches, 10-11 Needs Improvement. Score content, not English mechanics unless meaning is unclear.</p>", "RESOURCES": '<p><a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte/singley-academy">Current Singley Academy programs</a> · current district pages for Lodging and Resort Management. Xello Decision Making, eDynamic 6.1, and H&amp;L App Exploration are optional extensions.</p>', "SUPPORT": "<p>Use five planning fields and numbered sentence jobs. The recommendation page provides ten full-width writing lines for a five-to-seven-sentence response; speech-to-text is equal.</p>", "FALLBACK": "<p>The fixed packet is the complete absence and platform-failure route. Do not add favorite counts or screenshots to the evidence requirement.</p>"},
        }

        day_names = {1: "Culinary Twist Menu Design", 2: "Motivation and Career Comparison", 3: "Hotel Rescue", 4: "Cater and Create", 5: "Hospitality Recommendation"}
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 3SW Wk4 Day {day} - {day_names[day]}"
            student_page = await upsert_page(client, student_title, render("3sw-wk4-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, **student[day]}))
            teacher_title = f"TEACHER: 3SW Wk4 Day {day} Facilitator Guide"
            teacher_page = await upsert_page(client, teacher_title, render("3sw-wk4-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **teacher[day]}))
            await upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            pages[day] = {"teacher": teacher_page, "student": student_page}
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title)]
            if day == 1:
                await upsert_item(client, module["id"], "Assignment", annotation["id"], ANNOTATION_TITLE)
                order.append(("Assignment", annotation["id"], ANNOTATION_TITLE))
            if day == 2:
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
            "annotation": {"id": annotation["id"], "published": annotation.get("published"), "submission_types": annotation.get("submission_types"), "annotatable_attachment_id": annotation.get("annotatable_attachment_id")},
            "quiz": {"id": quiz["id"], "published": quiz.get("published"), "quiz_type": quiz.get("quiz_type"), "allowed_attempts": quiz.get("allowed_attempts")},
            "recommendation": {"id": recommendation["id"], "published": recommendation.get("published"), "grading_type": recommendation.get("grading_type")},
            "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
            "folders": {str(day): {"id": folder["id"], "locked": folder["locked"]} for day, folder in folders.items()},
            "files": {key: value["id"] for key, value in files.items()},
            "pages": {str(day): {kind: {"url": value["url"], "published": value["published"]} for kind, value in pair.items()} for day, pair in pages.items()},
            "items": [{"id": item["id"], "position": item["position"], "title": item["title"], "type": item["type"], "page_url": item.get("page_url")} for item in final_items],
        }, indent=2))


asyncio.run(main())
