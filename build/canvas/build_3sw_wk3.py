"""Build the unpublished 3SW Week 3 Sustainable Engineering Canvas module."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
import httpx

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
MODULE_NAME = "3SW Wk3: Sustainable Engineering and Pest Patrol"
DRAFT_TITLE = "PRACTICE: Pest Patrol Drone Draft"
PACKET_TITLE = "PRACTICE: Sustainable Engineering Evidence Packet"
GOALS_TITLE = "PRACTICE: Xello Set Goals Reflection"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/3sw/wk3"


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


async def upsert_assignment(client, title, description, peer_reviews=False):
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    found = next((assignment for assignment in assignments if assignment.get("name") == title), None)
    data = {
        "assignment[name]": title,
        "assignment[description]": description,
        "assignment[submission_types][]": ["online_upload", "online_text_entry", "online_url"],
        "assignment[grading_type]": "not_graded",
        "assignment[points_possible]": "0",
        "assignment[published]": "false",
        "assignment[peer_reviews]": "true" if peer_reviews else "false",
        "assignment[automatic_peer_reviews]": "false",
    }
    return await api(client, "PUT" if found else "POST", f"/courses/{COURSE_ID}/assignments/{found['id']}" if found else f"/courses/{COURSE_ID}/assignments", data=data)


async def upsert_item(client, module_id, kind, key, title):
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    found = next((item for item in items if (kind == "SubHeader" and item.get("title") == title) or (kind == "Page" and item.get("page_url") == key) or (kind == "Assignment" and item.get("content_id") == key)), None)
    if found:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module_id}/items/{found['id']}", data={"module_item[title]": title})
    data = {"module_item[type]": kind, "module_item[title]": title}
    if kind == "Page":
        data["module_item[page_url]"] = key
    elif kind == "Assignment":
        data["module_item[content_id]"] = key
    return await api(client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data=data)


def file_link(file_id, label):
    return f'<a href="/courses/{COURSE_ID}/files/{file_id}/preview" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">{label}</a>'


def image_tag(file_id, alt, max_width=700):
    return f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" style="display:block;width:100%;max-width:{max_width}px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'


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
        draft = await upsert_assignment(client, DRAFT_TITLE, "<p>Submit a Pest Patrol drone draft as a file, image, text explanation, or approved design URL. Paper is equal. Peer review is available only after the teacher manually assigns reviewers.</p>", True)
        packet = await upsert_assignment(client, PACKET_TITLE, "<p>Submit the final drone design, revision record, and trends evaluation. This object remains unpublished and ungraded until the course Major/Minor grade map is configured.</p>")
        goals = await upsert_assignment(client, GOALS_TITLE, "<p>Submit the private goal reflection as text or an uploaded PDF. Do not post personal goals or profile screenshots to a discussion.</p>")

        support = "course files/CCR Materials/3SW/Wk3"
        support_folder = await ensure_folder(client, support)
        names = {
            "CAREERS": "3sw-wk3-sustainable-career-problem-guide.pdf",
            "FIELD": "3sw-wk3-pest-patrol-field-notes.pdf",
            "DESIGN": "3sw-wk3-drone-design-brief.pdf",
            "REVIEW": "3sw-wk3-peer-review-revision.pdf",
            "TRENDS": "3sw-wk3-societal-trends-evidence.pdf",
            "EVAL": "3sw-wk3-societal-trends-evaluation.pdf",
            "RUBRIC": "3sw-wk3-sustainable-engineering-major-rubric.pdf",
            "GOALS": "3sw-wk3-xello-goals-plan.pdf",
        }
        files = {key: await upload(client, ROOT / "docs/resources/worksheets" / name, support) for key, name in names.items()}
        files["XELLO"] = await upload(client, ROOT / "cce-curriculum/resources/xello-licensed/prerequisites/goals.pdf", support)

        folders, visuals = {}, {}
        for day in range(1, 6):
            path = f"course files/CCR Materials/3SW/Wk3/Day {day} Visuals"
            folders[day], visuals[day] = await ensure_folder(client, path), {}
            source = ASSETS / f"day{day}"
            if source.exists():
                for image in sorted(source.glob("*.png")):
                    visuals[day][image.name] = await upload(client, image, path)

        draft_url = f"/courses/{COURSE_ID}/assignments/{draft['id']}"
        packet_url = f"/courses/{COURSE_ID}/assignments/{packet['id']}"
        goals_url = f"/courses/{COURSE_ID}/assignments/{goals['id']}"
        field_media = image_tag(visuals[2]["fyf-pest-patrol-field-notes-1.png"]["id"], "Find Your Future Pest Patrol agricultural engineer field notes") + image_tag(visuals[2]["fyf-pest-patrol-field-notes-2.png"]["id"], "Find Your Future Pest Patrol farmer and plant scientist field notes")
        design_media = image_tag(visuals[3]["fyf-pest-patrol-design-review.png"]["id"], "Find Your Future Pest Patrol drone design and peer review directions")
        review_media = image_tag(visuals[4]["fyf-pest-patrol-design-review.png"]["id"], "Find Your Future Pest Patrol design and peer review page")
        goal_media = image_tag(visuals[5]["fyf-adaptability-goal-bridge.png"]["id"], "Find Your Future Adaptability scenario used as a goal-planning bridge")

        student = {
            1: {"TITLE": "Match Careers to a Resource Problem", "PURPOSE": "Use current career evidence to choose who should lead a crop-and-water problem.", "TODAY": "<ul><li>compare four careers;</li><li>choose a lead career for a drought problem;</li><li>state what the evidence does not prove.</li></ul>", "READY": f'<p>Open {file_link(files["CAREERS"]["id"], "the two-page Career and Problem Guide")}.</p>', "MEDIA": "", "STEPS": step(1, "Read the work, not only the pay", "<p>Compare tasks, preparation, May 2024 U.S. median pay, growth, and annual openings.</p>") + step(2, "Read the crop-and-water brief", "<p>NASA and USDA evidence describe drought, soil moisture, drone uses, and real technology limits.</p>") + step(3, "Choose and defend", "<p>Name one matching task, one weaker lead, and one current fact.</p>") + step(4, "Check the boundary", "<p>Do not relabel a national median as DFW starting pay or treat a projection as a promise.</p>"), "EXIT": "<p>Which matters more for this problem: career growth or the worker's actual task? Use one fact.</p>", "DONE": "<ul><li>lead career selected;</li><li>task-to-problem link;</li><li>comparison to another career;</li><li>source/date/measure kept accurate.</li></ul>", "SUPPORT": "<p>task = tarea · preparation = preparación · median = mediana · projection = proyección. Frame: “I chose ____ because this worker ____.”</p>", "FALLBACK": "<p>The PDF is the full route. H&amp;L is optional and no live search is required.</p>"},
            2: {"TITLE": "Turn Field Reports into Constraints", "PURPOSE": "Read three worker viewpoints and turn evidence into design rules.", "TODAY": "<ul><li>record useful facts from three reports;</li><li>write three testable constraints;</li><li>rank the most important constraint.</li></ul>", "READY": f'<p>Open {file_link(files["FIELD"]["id"], "Pest Patrol Field Notes and Constraints")}.</p>', "MEDIA": field_media, "STEPS": step(1, "Read one source at a time", "<p>Agricultural Engineer, Farmer, then Plant Scientist. Finish each section before moving on.</p>") + step(2, "Write what the drone must do", "<p>Turn facts into functions, not decorations.</p>") + step(3, "Build three constraints", "<p>Detection, movement/coverage, and one practical limit.</p>") + step(4, "Rank and explain", "<p>Choose the most important constraint and point to the source that supports it.</p>"), "EXIT": "<p>If the team could meet only two constraints, which one could wait and what risk would that create?</p>", "DONE": "<ul><li>all three reports recorded;</li><li>three testable constraints;</li><li>evidence beside each constraint;</li><li>one ranked decision.</li></ul>", "SUPPORT": "<p>detect = detectar · cover = cubrir · withstand = resistir · constraint = restricción.</p>", "FALLBACK": "<p>The embedded pages and packet are the complete absence route. No platform login is needed.</p>"},
            3: {"TITLE": "Design the Pest Patrol Drone", "PURPOSE": "Communicate a drone idea with functions, evidence links, and a tradeoff.", "TODAY": "<ul><li>label six or more features;</li><li>connect three labels to field evidence;</li><li>explain one tradeoff.</li></ul>", "READY": f'<p>Open {file_link(files["DESIGN"]["id"], "the three-page Drone Design Brief")} and {file_link(files["RUBRIC"]["id"], "the 16-point rubric")}.</p>', "MEDIA": design_media, "STEPS": step(1, "Copy the constraints", "<p>Keep Day 2 evidence visible.</p>") + step(2, "Choose an equal build route", "<p>Paper, Canva for Education, Adobe Express, or another approved route. Art polish does not earn extra points.</p>") + step(3, "Draw and label", "<p>Use the full-page canvas. Show sensing, movement, farmer reporting, safety/crop protection, and two more functions.</p>") + step(4, "Explain and submit", f'<p>Complete the evidence chain and tradeoff, then <a href="{draft_url}">open the Pest Patrol Drone Draft assignment</a>. Paper is equal.</p>'), "EXIT": "<p>Which feature has the strongest field-report evidence, and which source supports it?</p>", "DONE": "<ul><li>six labeled features;</li><li>three evidence links;</li><li>benefit and limit stated;</li><li>draft submitted digitally or on paper.</li></ul>", "SUPPORT": "<p>feature = característica · label = etiqueta · evidence = evidencia · tradeoff = compensación. A basic outline is available without lowering the criteria.</p>", "FALLBACK": "<p>No drone hardware is required. If Canvas fails, keep the paper original or saved file for Day 4 review.</p>"},
            4: {"TITLE": "Review, Revise, and Evaluate Trends", "PURPOSE": "Use specific feedback, make one visible revision, and evaluate two changing-work trends.", "TODAY": "<ul><li>review one drone design;</li><li>make and explain one revision;</li><li>compare two societal trends with sourced evidence.</li></ul>", "READY": f'<p>Open {file_link(files["REVIEW"]["id"], "the Peer Review and Revision Record")}, {file_link(files["TRENDS"]["id"], "the Trends Evidence Guide")}, and {file_link(files["EVAL"]["id"], "the Trends Evaluation")}.</p>', "MEDIA": review_media, "STEPS": step(1, "Review privately", "<p>Use the printed form or a teacher-assigned Canvas peer review. Write one strength and one useful next step.</p>") + step(2, "Revise on purpose", "<p>Show the exact change and explain why it improves evidence, function, clarity, or safety.</p>") + step(3, "Read three fixed trends", "<p>Precision agriculture, wind/solar installation work, and technology in the water workforce.</p>") + step(4, "Compare and recommend", f'<p>Use two facts and one evidence limit. When complete, <a href="{packet_url}">open the Sustainable Engineering Evidence Packet assignment</a>.</p>'), "EXIT": "<p>Which trend changes more daily work? Use one fact and one limit.</p>", "DONE": "<ul><li>specific peer or self-review;</li><li>one visible revision;</li><li>two trends compared;</li><li>two facts and one limit;</li><li>packet submitted when complete.</li></ul>", "SUPPORT": "<p>trend = tendencia · revision = revisión · projection = proyección · limit = límite. A self-review or teacher conference replaces a missing reviewer.</p>", "FALLBACK": "<p>Paper review is equal. The fixed evidence guide replaces open searching. Late work does not depend on automatic peer assignment.</p>"},
            5: {"TITLE": "Set Two Goals in Xello", "PURPOSE": "Plan two honest goals, save them in Xello, and name a next task and backup.", "TODAY": "<ul><li>use an adaptability example;</li><li>save at least two Xello goals;</li><li>complete a private reflection.</li></ul>", "READY": f'<p>Open {file_link(files["GOALS"]["id"], "the Goals Plan and Private Reflection")}. Keep personal details private.</p>', "MEDIA": goal_media, "STEPS": step(1, "Draft two goals", "<p>Give each goal a timeframe, one task, and an obstacle with a backup plan.</p>") + step(2, "Save in Xello", "<p>ClassLink &gt; Xello &gt; Plans &gt; Goals &amp; Plans &gt; Set a goal. Save at least two goals.</p>") + step(3, "Check the plan", "<p>Confirm both goals appear. Your teacher uses the Completion Standards report; do not submit a profile screenshot.</p>") + step(4, "Reflect privately", f'<p>Finish the reflection, then <a href="{goals_url}">open the private Xello Set Goals Reflection assignment</a>.</p>'), "EXIT": "<p>Which goal has the clearest next task, and which may need revision after the first attempt?</p>", "DONE": "<ul><li>two goals saved in Xello;</li><li>timeframe and task for each;</li><li>private reflection complete;</li><li>catch-up recorded if Xello failed.</li></ul>", "SUPPORT": "<p>goal = meta · timeframe = plazo · task = tarea · obstacle = obstáculo · backup = alternativa.</p>", "FALLBACK": "<p>Submit the paper plan and schedule supervised Xello catch-up. Paper planning does not replace the required save.</p>"},
        }

        teacher = {
            1: {"TITLE": "Match Careers to a Resource Problem", "SUBTITLE": "50 minutes · TEKS d(1)(C)", "ALERT": "<strong>Fixed evidence is the core.</strong> Do not depend on exact H&amp;L Hat titles or open salary searches.", "PREP": f'<ul><li>Post {file_link(files["CAREERS"]["id"], "the career/problem guide")}.</li><li>Project one row and model median versus starting pay.</li><li>H&amp;L may remain optional enrichment.</li></ul>', "EVIDENCE": "<p>Problem-to-career response with one task link, one comparison, and one current fact. Formative.</p>", "FLOW": flow("#5a2d91", "Resource warm-up · 5", "Water, food, energy, or clean air.") + flow("#4a9d2f", "Career evidence · 10", "Task, preparation, pay measure, growth, openings.") + flow("#1f617a", "Drought problem brief · 20", "Choose and defend a lead career.") + flow("#e3ad19", "Compare and revise · 10", "State an evidence boundary.") + flow("#1f617a", "Exit · 5", "Task versus growth."), "MONITOR": "<p>Agricultural Engineer is the most direct lead when the explanation names farm systems, irrigation, equipment, or monitoring. Environmental Engineer also works with a clear water-system argument. Score reasoning, not preference. Correct every DFW-starting-pay relabel.</p>", "RESOURCES": '<p><a href="https://www.bls.gov/ooh/architecture-and-engineering/environmental-engineers.htm">BLS Environmental Engineers</a> · <a href="https://www.bls.gov/ooh/architecture-and-engineering/agricultural-engineers.htm">BLS Agricultural Engineers</a> · <a href="https://www.bls.gov/ooh/installation-maintenance-and-repair/wind-turbine-technicians.htm">BLS Wind Technicians</a> · <a href="https://www.bls.gov/ooh/construction-and-extraction/solar-photovoltaic-installers.htm">BLS Solar Installers</a> · <a href="https://climatekids.nasa.gov/soil/">NASA drought and soil moisture</a></p>', "SUPPORT": "<p>Highlight the task column, narrow the first choice to two careers, and allow oral rehearsal. One full-width line is enough for the required fact; longer reasoning has two lines.</p>", "FALLBACK": "<p>The PDF is the complete route. No platform or live search is required.</p>"},
            2: {"TITLE": "Turn Field Reports into Constraints", "SUBTITLE": "50 minutes · TEKS d(1)(C)", "ALERT": "<strong>Read one source at a time.</strong> The workbook pages are dense, so close each chunk before opening the next.", "PREP": f'<ul><li>Post the licensed FYF crops and {file_link(files["FIELD"]["id"], "the three-page field-notes packet")}.</li><li>Model one fact-to-function statement.</li><li>Have highlighters ready.</li></ul>', "EVIDENCE": "<p>Three source summaries, three constraints, and one ranked decision. Formative.</p>", "FLOW": flow("#5a2d91", "Warm-up · 5", "Questions before drawing.") + flow("#4a9d2f", "Source preview · 8", "Engineer, Farmer, Plant Scientist.") + flow("#1f617a", "Read and record · 25", "One closed chunk per source.") + flow("#e3ad19", "Build constraints · 7", "Detection, coverage, practical limit.") + flow("#1f617a", "Exit · 5", "Rank and defend."), "MONITOR": "<p>Check three things: copied facts are accurate, constraints describe functions, and students can point to the supporting source. Cost, battery, weather, safety, accuracy, and farmer time are acceptable practical limits when explained.</p>", "RESOURCES": "<p>FYF pp. 93-94 are embedded in the student guide. No separate deck is required.</p>", "SUPPORT": "<p>Use the word bank detect, map, report, withstand, cover, protect. The packet has three full pages so two or three facts are not squeezed into table cells.</p>", "FALLBACK": "<p>The embedded licensed pages and packet are the complete absence route.</p>"},
            3: {"TITLE": "Design the Pest Patrol Drone", "SUBTITLE": "50 minutes · TEKS d(1)(C)", "ALERT": "<strong>Paper, Canva, and Adobe Express are equal.</strong> The evidence chain and function are scored, not art polish or premium assets.", "PREP": f'<ul><li>Post {file_link(files["DESIGN"]["id"], "the three-page design brief")} and {file_link(files["RUBRIC"]["id"], "rubric")}.</li><li>Open the unpublished draft Assignment.</li><li>Offer the simple outline only as a support.</li></ul>', "EVIDENCE": "<p>Six labeled features, three evidence links, one evidence chain, and one tradeoff. This begins the recommended major packet.</p>", "FLOW": flow("#5a2d91", "Useful-sketch warm-up · 5", "Labels, arrows, function, evidence.") + flow("#4a9d2f", "Model one chain · 8", "Evidence to feature to benefit.") + flow("#1f617a", "Design and label · 27", "Paper or approved digital route.") + flow("#e3ad19", "Tradeoff check · 5", "Benefit plus cost, risk, or limit.") + flow("#1f617a", "Submit · 5", "Canvas draft or paper record."), "MONITOR": "<p>Minute 8: shape and labels. Minute 16: six functions. Minute 23: three evidence links. If several students name parts without explaining functions, pause and model one stronger label. Keep automatic peer review off.</p>", "RESOURCES": f'<p>{file_link(files["DESIGN"]["id"], "Design Brief")} · {file_link(files["RUBRIC"]["id"], "student-visible rubric")} · licensed FYF p. 95 embedded.</p>', "SUPPORT": "<p>A full page is reserved for drawing. Allow bilingual labels, speech-to-text for the rationale, and a basic outline without reducing criteria.</p>", "FALLBACK": "<p>No hardware is required. If Canvas fails, collect the paper original or saved file for Day 4.</p>"},
            4: {"TITLE": "Review, Revise, and Evaluate Trends", "SUBTITLE": "50 minutes · TEKS d(1)(D), d(5)(C)", "ALERT": "<strong>Peer availability does not control the grade.</strong> Use manual Canvas reviewers, paper partners, structured self-review, or a teacher conference.", "PREP": f'<ul><li>Post {file_link(files["REVIEW"]["id"], "peer review")}, {file_link(files["TRENDS"]["id"], "trends guide")}, {file_link(files["EVAL"]["id"], "evaluation")}, and {file_link(files["RUBRIC"]["id"], "rubric")}.</li><li>If using Canvas peer review, manually assign reviewers only after submissions exist.</li><li>Open the unpublished packet Assignment.</li></ul>', "EVIDENCE": "<p>Specific feedback, one visible revision, and a two-trend evaluation using two facts and one limit. Recommended 16-point major packet.</p>", "FLOW": flow("#5a2d91", "Feedback warm-up · 5", "Evidence beats praise.") + flow("#4a9d2f", "Review and revise · 18", "One strength, one next step, one visible change.") + flow("#1f617a", "Read fixed trends · 17", "Agriculture, energy, water workforce.") + flow("#e3ad19", "Recommendation · 5", "Begin 5-7 sentences.") + flow("#1f617a", "Exit · 5", "Highlight facts and limit."), "MONITOR": "<p>No single trend or career is correct. Full evidence explains a changed task, keeps source/date/measure attached, states one limit, and gives a defensible recommendation. Peer comments are formative and should not lower a score when a reviewer misses a problem.</p>", "RESOURCES": '<p><a href="https://www.ars.usda.gov/research/publications/publication/?seqNo115=346120">USDA agriculture-drone research</a> · <a href="https://www.epa.gov/sustainable-water-infrastructure/water-infrastructure-sector-workforce">EPA water workforce</a> · current BLS pages listed in the guide.</p>', "SUPPORT": "<p>The review form gives separate full-width areas for a strength and next step. The trends evaluation gives one full-width line per phrase/fact and eight lines for the 5-7 sentence recommendation.</p>", "FALLBACK": "<p>The fixed guide replaces open research. Paper is equal to Canvas peer review, and an absent student uses self-review.</p>"},
            5: {"TITLE": "Set Two Goals in Xello", "SUBTITLE": "50 minutes · required Grade 8 Xello completion", "ALERT": "<strong>Required task: Set goals, 20 minutes, save at least two goals.</strong> The licensed Xello guide is an extended 25-30 minute resource and asks for three goals; the live district minimum controls today.", "PREP": f'<ul><li>Test ClassLink and Xello.</li><li>Open the Completion Standards report.</li><li>Post {file_link(files["GOALS"]["id"], "the private Goals Plan")} and the licensed {file_link(files["XELLO"]["id"], "Set Goals educator guide")}.</li><li>Open the private reflection Assignment.</li></ul>', "EVIDENCE": "<p>Completion Standards report shows at least two saved goals; private reflection names next task, possible revision, and an optional career connection. Formative.</p>", "FLOW": flow("#5a2d91", "Goal warm-up · 5", "What keeps a plan moving?") + flow("#4a9d2f", "Adaptability bridge · 10", "Control, change, and backup action.") + flow("#1f617a", "Xello Set goals · 20", "Two goals, timeframe, one task each.") + flow("#e3ad19", "Private reflection · 12", "Next task, likely revision, career connection.") + flow("#1f617a", "Report/catch-up · 3", "Verify or schedule supervised completion."), "MONITOR": "<p>Do not require screenshots or public goal sharing. A goal can be school, skill, career exploration, personal responsibility, or another honest category. Full completion is two saved goals. The extended guide's third goal is optional.</p>", "RESOURCES": f'<p>{file_link(files["XELLO"]["id"], "Licensed Xello Set Goals guide")} · {file_link(files["GOALS"]["id"], "two-page private plan")} · FYF p. 146 embedded as a short adaptability bridge.</p>', "SUPPORT": "<p>Draft on paper first, conference privately, and use category/timeframe/task/obstacle/backup labels. One line is reserved for each goal statement, two for each task, and two for each obstacle/backup.</p>", "FALLBACK": "<p>Paper planning supports access but does not replace Xello. Schedule supervised catch-up and verify through the report.</p>"},
        }

        day_names = {1: "Careers and Resource Problems", 2: "Field Reports and Constraints", 3: "Pest Patrol Drone Design", 4: "Review, Revision, and Trends", 5: "Xello Set Goals"}
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 3SW Wk3 Day {day} - {day_names[day]}"
            student_page = await upsert_page(client, student_title, render("3sw-wk3-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, **student[day]}))
            teacher_title = f"TEACHER: 3SW Wk3 Day {day} Facilitator Guide"
            teacher_page = await upsert_page(client, teacher_title, render("3sw-wk3-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **teacher[day]}))
            await upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            pages[day] = {"teacher": teacher_page, "student": student_page}
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title)]
            if day == 3:
                await upsert_item(client, module["id"], "Assignment", draft["id"], DRAFT_TITLE)
                order.append(("Assignment", draft["id"], DRAFT_TITLE))
            if day == 4:
                await upsert_item(client, module["id"], "Assignment", packet["id"], PACKET_TITLE)
                order.append(("Assignment", packet["id"], PACKET_TITLE))
            if day == 5:
                await upsert_item(client, module["id"], "Assignment", goals["id"], GOALS_TITLE)
                order.append(("Assignment", goals["id"], GOALS_TITLE))

        items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(entry for entry in items if (kind == "SubHeader" and entry.get("id") == key) or (kind == "Page" and entry.get("page_url") == key) or (kind == "Assignment" and entry.get("content_id") == key))
            await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}", data={"module_item[position]": position, "module_item[title]": title})

        final_items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        module = await api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        print(json.dumps({
            "module": {"id": module["id"], "published": module["published"]},
            "assignments": {"draft": {"id": draft["id"], "published": draft.get("published"), "peer_reviews": draft.get("peer_reviews"), "automatic_peer_reviews": draft.get("automatic_peer_reviews")}, "packet": {"id": packet["id"], "published": packet.get("published")}, "goals": {"id": goals["id"], "published": goals.get("published")}},
            "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
            "folders": {str(day): {"id": folder["id"], "locked": folder["locked"]} for day, folder in folders.items()},
            "files": {key: value["id"] for key, value in files.items()},
            "pages": {str(day): {kind: {"url": value["url"], "published": value["published"]} for kind, value in pair.items()} for day, pair in pages.items()},
            "items": [{"id": item["id"], "position": item["position"], "title": item["title"], "type": item["type"], "page_url": item.get("page_url")} for item in final_items],
        }, indent=2))


asyncio.run(main())
