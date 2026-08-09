"""Build the unpublished 4SW Week 3 aviation and transportation module."""

import asyncio
import json
import sys

import httpx

import build_4sw_wk1 as common


BASE = common.BASE
COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/4sw/wk3"
MODULE_NAME = "4SW Wk3: Aviation Routes, Systems, and Action Planning"
QUIZ_TITLE = "PRACTICE: Is This Survey Useful?"
LAB_TITLE = "PRACTICE: Airport Design and Simulation Lab"
PLAN_TITLE = "DRAFT: Aviation Route and Action Plan"


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    found = next((entry for entry in modules if entry["name"] == MODULE_NAME), None)
    data = {"module[published]": "false"}
    if found:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data=data)
    data["module[name]"] = MODULE_NAME
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


QUESTIONS = [
    (
        "Q1 - Neutral wording",
        "Which survey question is most neutral?",
        "How often would you use a bus that arrived every 20 minutes?",
        [
            "Wouldn't a faster bus make everyone's life better?",
            "Why is the current bus schedule terrible?",
            "Don't you agree that the city needs more buses?",
        ],
        "Correct. It asks one measurable question without pushing a preferred answer.",
        "A useful survey question does not tell the respondent what to think.",
    ),
    (
        "Q2 - Complete choices",
        "A frequency question offers only Never, Sometimes, and Every day. What is the best revision?",
        "Use clear, non-overlapping ranges and add Not sure when it closes a real gap.",
        [
            "Keep the choices because every response fits perfectly.",
            "Ask for the respondent's name instead.",
            "Replace the question with a slogan.",
        ],
        "Correct. Distinct ranges make the results easier to interpret.",
        "Answer choices should cover realistic responses without overlapping.",
    ),
    (
        "Q3 - Privacy",
        "Which detail should this fictional transportation survey avoid collecting?",
        "A respondent's exact home address and work schedule",
        [
            "A broad transportation barrier",
            "How often a route might be used",
            "A suggestion for improving a stop"],
        "Correct. The analyst does not need precise identifying or schedule information for this design task.",
        "Collect only information needed to answer the fictional transportation question.",
    ),
    (
        "Q4 - Evidence to action",
        "A repeated survey pattern shows that evening-shift workers cannot reach the current route after 9 p.m. What is a defensible analyst response?",
        "Recommend that the city evaluate later service, route access, cost, and staffing using more evidence.",
        [
            "Promise that every route will run all night.",
            "Publish the respondents' schedules.",
            "Ignore the pattern because it came from a survey."],
        "Correct. The recommendation stays connected to evidence and does not promise a final decision.",
        "An analyst can recommend further evaluation, not guarantee a policy change.",
    ),
]


async def upsert_quiz(client):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    found = next((entry for entry in quizzes if entry.get("title") == QUIZ_TITLE), None)
    data = {
        "quiz[title]": QUIZ_TITLE,
        "quiz[description]": "<p>Ungraded practice. Retry and use the feedback to check wording, answer choices, privacy, and an evidence-based recommendation.</p>",
        "quiz[quiz_type]": "practice_quiz",
        "quiz[published]": "false",
        "quiz[allowed_attempts]": "-1",
        "quiz[show_correct_answers]": "true",
        "quiz[shuffle_answers]": "false",
    }
    endpoint = f"/courses/{COURSE_ID}/quizzes/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes"
    quiz = await common.api(client, "PUT" if found else "POST", endpoint, data=data)
    existing = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    for position, (name, prompt, correct, wrong, yes, no) in enumerate(QUESTIONS, 1):
        prior = next((entry for entry in existing if entry.get("question_name") == name), None)
        payload = {
            "question": {
                "question_name": name,
                "question_text": prompt,
                "question_type": "multiple_choice_question",
                "position": position,
                "points_possible": 1,
                "correct_comments": yes,
                "incorrect_comments": no,
                "answers": [{"answer_text": correct, "answer_weight": 100}]
                + [{"answer_text": answer, "answer_weight": 0} for answer in wrong],
            }
        }
        question_path = (
            f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior['id']}"
            if prior
            else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        )
        await common.api(client, "PUT" if prior else "POST", question_path, json=payload)
    return await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


async def upsert_item(client, module_id, kind, key, title):
    items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    found = next(
        (
            item
            for item in items
            if (kind == "SubHeader" and item.get("title") == title)
            or (kind == "Page" and item.get("page_url") == key)
            or (kind in ("Assignment", "Quiz") and item.get("content_id") == key)
        ),
        None,
    )
    if found:
        return await common.api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{found['id']}",
            data={"module_item[title]": title},
        )
    data = {"module_item[type]": kind, "module_item[title]": title}
    if kind == "Page":
        data["module_item[page_url]"] = key
    elif kind in ("Assignment", "Quiz"):
        data["module_item[content_id]"] = key
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data=data)


def image_tag(file_id, alt, max_width=700):
    return (
        f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" '
        f'style="display:block;width:100%;max-width:{max_width}px;height:auto;margin:14px auto;border:1px solid #ddd" '
        f'data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'
    )


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        module = await ensure_module(client)
        support_path = "course files/CCR Materials/4SW/Wk3"
        support_folder = await common.ensure_folder(client, support_path)
        names = {
            "SURVEY": "4sw-wk3-transportation-survey-design.pdf",
            "ROUTES": "4sw-wk3-aviation-careers-and-pilot-routes.pdf",
            "LAB": "4sw-wk3-airport-design-simulation-lab.pdf",
            "CARDS": "4sw-wk3-classroom-scenario-cards.pdf",
            "PLAN": "4sw-wk3-aviation-route-action-plan.pdf",
            "RUBRIC": "4sw-wk3-route-action-rubric.pdf",
        }
        files = {
            key: await common.upload(client, ROOT / "docs/resources/worksheets" / filename, support_path)
            for key, filename in names.items()
        }

        selected = {
            1: [
                "fyf-transportation-cluster.jpg",
                "fyf-transportation-survey-scenario.jpg",
                "fyf-transportation-survey-build.jpg",
            ],
            2: ["fyf-flight-line-fixers-intro.jpg", "fyf-aviation-maintenance-program.jpg"],
            5: ["fyf-aviation-app-exploration.jpg"],
        }
        visuals, visual_folders = {}, {}
        for day, image_names in selected.items():
            folder_path = f"course files/CCR Materials/4SW/Wk3/Day {day} Visuals"
            visual_folders[day] = await common.ensure_folder(client, folder_path)
            visuals[day] = {
                name: await common.upload(client, ASSETS / f"day{day}" / name, folder_path)
                for name in image_names
            }

        quiz = await upsert_quiz(client)
        lab = await common.upsert_assignment(
            client,
            LAB_TITLE,
            "<p>Plan, test, and revise the fictional classroom airport model. Use Canvas annotation, upload, text entry, or paper. LEGO, paper, and Lucid are equal build routes. This is not FAA training.</p>",
            ["student_annotation", "online_upload", "online_text_entry"],
            files["LAB"]["id"],
        )
        plan = await common.upsert_assignment(
            client,
            PLAN_TITLE,
            "<p>Submit the private Aviation Route and Action Plan by upload, text entry, or media recording. The student-visible 16-point rubric is attached. Keep this unpublished and ungraded until the Minor group and 40/60 weighting are verified.</p>",
            ["online_upload", "online_text_entry", "media_recording"],
        )
        quiz_url = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        lab_url = f"/courses/{COURSE_ID}/assignments/{lab['id']}"
        plan_url = f"/courses/{COURSE_ID}/assignments/{plan['id']}"
        lucid_url = f"/courses/{COURSE_ID}/external_tools/17478"

        media = {
            1: image_tag(visuals[1]["fyf-transportation-cluster.jpg"]["id"], "Find Your Future Transportation, Distribution, and Logistics cluster opener")
            + image_tag(visuals[1]["fyf-transportation-survey-scenario.jpg"]["id"], "Find Your Future Transportation Survey Project scenario and first two steps")
            + image_tag(visuals[1]["fyf-transportation-survey-build.jpg"]["id"], "Find Your Future Transportation Survey Project incentive and campaign steps"),
            2: image_tag(visuals[2]["fyf-flight-line-fixers-intro.jpg"]["id"], "Find Your Future Flight Line Fixers introduction and simplified observation table")
            + image_tag(visuals[2]["fyf-aviation-maintenance-program.jpg"]["id"], "Find Your Future workbook Aviation Maintenance program paragraph", 620),
            3: "",
            4: "",
            5: image_tag(visuals[5]["fyf-aviation-app-exploration.jpg"]["id"], "Find Your Future optional H and L app exploration page"),
        }

        file_link, step, flow = common.file_link, common.step, common.flow
        student = {
            1: {
                "TITLE": "Transportation Cluster and Survey Design",
                "PURPOSE": "Design questions that could reveal a transportation need without collecting private information.",
                "TODAY": "<ul><li>meet Transportation careers;</li><li>choose a fictional audience;</li><li>draft ten balanced questions;</li><li>revise one question after a quality check.</li></ul>",
                "READY": f'<p>Open {file_link(files["SURVEY"]["id"], "the four-page Survey Design packet")}. Keep the survey fictional. Do not collect names, addresses, schedules, contact information, or real responses.</p>',
                "STEPS": step(1, "Define the audience and need", "<p>Choose one fictional audience. Write the transportation problem and the evidence an analyst would need.</p>")
                + step(2, "Draft the ten questions", "<p>Write seven multiple-choice and three short-answer questions. Use neutral wording and distinct answer choices.</p>")
                + step(3, "Add a hypothetical incentive", "<p>Explain one idea that might increase response. It is not a real offer or promise.</p>")
                + step(4, "Check and revise", f'<p>Use the five checks, revise one question, then <a href="{quiz_url}">complete the practice Quiz</a>.</p>'),
                "EXIT": "<p>Identify neutral wording, one misleading answer-choice problem, one privacy boundary, and one analyst action.</p>",
                "DONE": "<ul><li>fictional audience and need;</li><li>7 multiple-choice and 3 short-answer questions;</li><li>hypothetical incentive;</li><li>five-part quality check;</li><li>one visible revision;</li><li>practice feedback reviewed.</li></ul>",
                "SUPPORT": "<p>neutral = neutral · response choice = opción de respuesta · private information = información privada. A reason or comparison gets its own full-width writing area in the packet.</p>",
                "FALLBACK": "<p>The embedded workbook pages and packet are the complete independent route. A missing partner uses the self-check column. Do not distribute the survey.</p>",
            },
            2: {
                "TITLE": "Aviation Careers and Pilot Routes",
                "PURPOSE": "Compare aviation work and preparation without confusing national median pay, local pay, entry pay, or military service.",
                "TODAY": "<ul><li>compare three aviation careers;</li><li>compare civilian and Air Force pilot examples;</li><li>name one route tradeoff;</li><li>write a source-based recommendation for fictional Sam.</li></ul>",
                "READY": f'<p>Open {file_link(files["ROUTES"]["id"], "the four-page Careers and Pilot Routes guide")}. The pay figures are May 2024 U.S. national medians, not DFW starting salaries.</p>',
                "STEPS": step(1, "Compare the three careers", "<p>Read daily work, common preparation, and the exact pay label for commercial pilot, air traffic controller, and aircraft mechanic.</p>")
                + step(2, "Compare two pilot examples", "<p>Record two steps, one possible advantage, one tradeoff, and one verification question for each route.</p>")
                + step(3, "Keep the military boundary", "<p>The Air Force example requires officer eligibility, selection, training, and a current 10-year active-duty commitment after pilot training. It is service, not free flight school.</p>")
                + step(4, "Recommend an investigation route", "<p>Write three sentences for fictional Sam using two facts and an authorized next source.</p>"),
                "EXIT": "<p>Choose the first route Sam should investigate, cite one step and tradeoff, and name who or what should verify the next requirement.</p>",
                "DONE": "<ul><li>three-career comparison;</li><li>two route examples;</li><li>advantage and tradeoff for each;</li><li>three-sentence recommendation;</li><li>one local course or access question.</li></ul>",
                "SUPPORT": "<p>route = ruta · preparation = preparación · commitment = compromiso · tradeoff = ventaja y costo · verify = verificar. Use “This route may fit because...” and “Before deciding, Sam must verify...”</p>",
                "FALLBACK": "<p>The dated guide replaces live search and H&amp;L. Flight Line Fixers is optional. No student diagnoses a real aircraft or completes a personal medical or military eligibility screen.</p>",
            },
            3: {
                "TITLE": "Design a Classroom Airport Map",
                "PURPOSE": "Build a shared map that can be tested, explained, and revised.",
                "TODAY": "<ul><li>plan before building;</li><li>label routes and gates;</li><li>predict one conflict point;</li><li>test one movement and revise.</li></ul>",
                "READY": f'<p>Open {file_link(files["LAB"]["id"], "the Airport Design and Simulation Lab")} or <a href="{lab_url}">the Canvas annotation activity</a>. Your build route may be LEGO, paper, or <a href="{lucid_url}">Lucid</a>; all use the same evidence checklist.</p>',
                "STEPS": step(1, "Read the classroom constraints", "<p>Two labeled runways, taxi routes, tower, four gates, north arrow, and an alternate route. These are classroom rules, not FAA standards.</p>")
                + step(2, "Draw the top-down plan", "<p>Add movement arrows, one predicted conflict point, and one planned revision before building.</p>")
                + step(3, "Build through an equal route", "<p>Use LEGO, paper, or Lucid. Artwork and construction detail are not graded.</p>")
                + step(4, "Run the readiness check", "<p>Move one aircraft from Gate 1 to R1 and back. Correct one blocked or confusing route.</p>"),
                "EXIT": "<p>Name one map feature and role, one conflict point with evidence, and one revision completed or still needed.</p>",
                "DONE": "<ul><li>complete labeled sketch;</li><li>one predicted conflict;</li><li>one revision;</li><li>usable model or map;</li><li>individual design note.</li></ul>",
                "SUPPORT": "<p>runway = pista · taxi route = ruta de rodaje · gate = puerta · conflict point = punto de conflicto. Planner, recorder, mover, checker, and builder are equal roles.</p>",
                "FALLBACK": "<p>Use the independent paper/digital map. A photo is optional and cannot include faces or student names. No partner or speaking performance is required.</p>",
            },
            4: {
                "TITLE": "Test, Communicate, and Revise",
                "PURPOSE": "Use precise classroom directions, test changing constraints, and connect a timed revision to evidence.",
                "TODAY": "<ul><li>practice a five-step classroom protocol;</li><li>run three tests;</li><li>log one breakdown each run;</li><li>write an individual timed iteration plan.</li></ul>",
                "READY": f'<p>Open {file_link(files["LAB"]["id"], "the Simulation Run Log")} and {file_link(files["CARDS"]["id"], "the two-page Scenario Cards")}. This is a fictional classroom protocol, not FAA phraseology.</p>',
                "STEPS": step(1, "Practice Name, Route, Repeat, Confirm, Log", "<p>Use one aircraft and one complete model call before starting a timed run.</p>")
                + step(2, "Run three eight-minute tests", "<p>Test, identify a breakdown, revise, and prepare the next run. One aircraft waits when two requests arrive together.</p>")
                + step(3, "Keep roles equal", "<p>Controller, mover, recorder, and safety checker all create evidence. Speaking is not required.</p>")
                + step(4, "Write the individual plan", "<p>Name the goal, exact two- or three-minute work block, support, evidence, and next adjustment.</p>"),
                "EXIT": "<p>For the blocked Taxi A scenario, choose a sequence, write the full classroom call, and state one two-minute improvement goal.</p>",
                "DONE": "<ul><li>three run-log sections or two plus a written third;</li><li>breakdown and revision each run;</li><li>individual timed iteration plan;</li><li>new scenario response.</li></ul>",
                "SUPPORT": "<p>Name = nombre · route = ruta · repeat = repetir · confirm = confirmar · log = registrar. The printed card keeps all five steps visible.</p>",
                "FALLBACK": "<p>Use the model map and written scenario route. Paper, LEGO, and Lucid use the same evidence. Team performance is not required for the individual work.</p>",
            },
            5: {
                "TITLE": "Aviation Route and Action Plan",
                "PURPOSE": "Choose a current direction and protect it with sources, timing, support, a backup, and a revision rule.",
                "TODAY": "<ul><li>reopen career and simulation evidence;</li><li>write three timed stages;</li><li>add support, obstacle, backup, and revision condition;</li><li>self-score, revise, and submit privately.</li></ul>",
                "READY": f'<p>Open {file_link(files["PLAN"]["id"], "the six-page Action Plan")} and {file_link(files["RUBRIC"]["id"], "the two-page 16-point rubric")}.</p>',
                "STEPS": step(1, "Choose a current direction", "<p>Investigate aviation, select another Transportation career, or state that the cluster is not your current fit. The direction itself is not graded.</p>")
                + step(2, "Bring forward evidence", "<p>Keep daily work, preparation, tradeoff, simulation skill, source, date, geography, and measure.</p>")
                + step(3, "Write three stages", "<p>Plan one action within seven days, one before the next counseling meeting, and one during Grade 9 or after high school. Add completion evidence and honest labels.</p>")
                + step(4, "Self-score and submit", f'<p>Revise the weakest section, then <a href="{plan_url}">submit privately</a> by upload, text, media, or paper.</p>'),
                "EXIT": "<p>List three timed stages, one support and one backup, and one condition that would make you revise.</p>",
                "DONE": "<ul><li>current direction and reason;</li><li>daily-work and preparation facts;</li><li>three timed stages;</li><li>source/date labels;</li><li>support, obstacle, backup, and revision condition;</li><li>one visible revision and private submission.</li></ul>",
                "SUPPORT": "<p>direction = dirección · evidence = evidencia · backup = alternativa · revise = revisar. Text, speech-to-text, private media, and paper answer the same evidence jobs.</p>",
                "FALLBACK": "<p>Missing simulation work can use the model log. H&amp;L, Xello Jobs and Employers, and eDynamic are optional extensions only. Canvas failure means paper or later upload without penalty.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Transportation Cluster and Survey Design",
                "SUBTITLE": "50 minutes · TEKS d(1)(B), d(1)(C)",
                "ALERT": "<strong>Fictional design only.</strong> Students do not distribute the survey, collect real responses, or request personal information. The optional incentive is never promised.",
                "PREP": f'<ul><li>Post {file_link(files["SURVEY"]["id"], "the Survey Design packet")}.</li><li>Open the embedded FYF pp. 149 and 166-167.</li><li>Open the unpublished practice Quiz.</li></ul>',
                "EVIDENCE": "<p>Individual ten-question draft, quality check, one visible revision, and an analyst-to-career explanation. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Visible and hidden transportation work.") + flow("#4a9d2f", "Read problem · 8", "Cluster, problem, evidence.") + flow("#1f617a", "Build survey · 27", "Audience, questions, incentive, quality revision.") + flow("#e3ad19", "Career connection · 5", "Pattern, recommendation, second career.") + flow("#1f617a", "Practice check · 5", "Four retryable items with feedback."),
                "MONITOR": "<p>Reject leading wording, overlapping or incomplete choices, and unnecessary identifiers. Strong recommendations remain tied to a fictional pattern and do not promise policy.</p>",
                "RESOURCES": "<p>FYF supplies the cluster and survey scenario. The CCE packet adds the privacy boundary, neutral-question models, and independent evidence route.</p>",
                "SUPPORT": "<p>Model one multiple-choice and one short-answer item. Allow type, speech-to-text, or handwriting. The packet provides full-width space for each question.</p>",
                "FALLBACK": "<p>A missing partner uses self-check. Canvas failure uses the paper check. Do not use a live form or collect student transportation stories.</p>",
            },
            2: {
                "TITLE": "Aviation Careers and Pilot Routes",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(3)(G)",
                "ALERT": "<strong>Keep every claim bounded.</strong> BLS values are May 2024 national medians. The military route is service with selection and obligation, not free flight school. JROTC is not pilot training.",
                "PREP": f'<ul><li>Post {file_link(files["ROUTES"]["id"], "the dated evidence guide")}.</li><li>Open current <a href="https://www.faa.gov/education/about/careers-aviation-and-space">FAA careers</a>, <a href="https://www.faa.gov/licenses_certificates/airline_certification/pilotschools">pilot schools</a>, <a href="https://www.faa.gov/air-traffic-controller-qualifications">ATC qualifications</a>, <a href="https://www.bls.gov/ooh/transportation-and-material-moving/airline-and-commercial-pilots.htm">BLS pilots</a>, <a href="https://www.bls.gov/ooh/transportation-and-material-moving/air-traffic-controllers.htm">BLS ATC</a>, and <a href="https://www.bls.gov/ooh/installation-maintenance-and-repair/aircraft-and-avionics-equipment-mechanics-and-technicians.htm">BLS mechanics</a>.</li><li>Keep Flight Line Fixers optional.</li></ul>',
                "EVIDENCE": "<p>Three-career comparison, civilian/Air Force route comparison, tradeoffs, verification questions, and source-based recommendation. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Information Sam needs.") + flow("#4a9d2f", "Three careers · 12", "Work, preparation, national median, limitation.") + flow("#1f617a", "Pilot routes · 23", "Steps, advantage, tradeoff, source, recommendation.") + flow("#e3ad19", "Irving/JROTC boundary · 5", "Current public programs and one question.") + flow("#1f617a", "Exit · 5", "Defensible first investigation route."),
                "MONITOR": "<p>Key values: commercial pilot $122,670; ATC $144,580; aircraft mechanic/service technician $78,680. All are May 2024 U.S. national medians. No route is the single right answer.</p>",
                "RESOURCES": "<p>Current Irving public CTE information lists Aviation Maintenance, Drone Engineering, and Marine JROTC at Irving High. Course access still requires current coursebook/counselor verification. Do not repeat the workbook's simulator or automotive-IBC claims as current guarantees.</p>",
                "SUPPORT": "<p>Use the four-page fixed evidence guide one section at a time. Private writing, typing, and media are equal. Do not ask students to disclose military family history or health information.</p>",
                "FALLBACK": "<p>No H&amp;L or open search is required. Flight Line Fixers asks students to observe image evidence, not diagnose an aircraft or learn real maintenance-dispatch decisions.</p>",
            },
            3: {
                "TITLE": "Design a Classroom Airport Map",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>Equal build routes.</strong> LEGO is recommended when available, but paper and the live Canvas Lucid integration use the same checklist and grading boundary.",
                "PREP": f'<ul><li>Post {file_link(files["LAB"]["id"], "the Lab packet")} and open the annotation Assignment.</li><li>Prepare four aircraft tokens per team and one model/non-example.</li><li>Test <a href="{lucid_url}">the Canvas Lucid integration</a> before offering it.</li></ul>',
                "EVIDENCE": "<p>Team or independent map, predicted conflict, revision, readiness test, and individual design note. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Role-to-information match.") + flow("#4a9d2f", "Rules · 7", "Fictional classroom constraints.") + flow("#1f617a", "Plan · 12", "Top-down sketch and conflict prediction.") + flow("#e3ad19", "Build · 16", "LEGO, paper, or Lucid.") + flow("#4a9d2f", "Readiness · 5", "One route test and correction.") + flow("#1f617a", "Exit · 5", "Individual feature, conflict, revision."),
                "MONITOR": "<p>Check complete routes, readable labels, visible conflict, and alternate route. The six-stud LEGO gap is a classroom constraint, not an FAA rule. Do not score artistry or material access.</p>",
                "RESOURCES": "<p>The CCE model is the complete route. A live airport map may be shown only as optional context, not as the required source students must decode.</p>",
                "SUPPORT": "<p>Assign planner, recorder, mover, checker, or builder. The 9-page combined Lab spans Days 3-4; Canvas annotation/text/upload and paper are equal.</p>",
                "FALLBACK": "<p>Independent map is equal. If Lucid fails, move directly to paper. Photos are optional and contain no faces or names.</p>",
            },
            4: {
                "TITLE": "Test, Communicate, and Revise",
                "SUBTITLE": "50 minutes · TEKS d(4)(A), d(1)(C)",
                "ALERT": "<strong>Classroom protocol only.</strong> Do not teach the five steps as FAA phraseology or ask students to invent real emergency, radio-failure, or separation procedures.",
                "PREP": f'<ul><li>Return maps and post {file_link(files["CARDS"]["id"], "the Scenario Cards")}.</li><li>Post the five-step card and one completed log.</li><li>Prepare a timer and the written-model route.</li></ul>',
                "EVIDENCE": "<p>Three run logs or two plus written third, team revisions, individual timed iteration plan, and new-scenario response. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Find ambiguity.") + flow("#4a9d2f", "Protocol · 8", "Name, Route, Repeat, Confirm, Log.") + flow("#1f617a", "Three tests · 24", "Run, diagnose communication breakdown, revise.") + flow("#e3ad19", "Individual plan · 8", "Timed action and evidence.") + flow("#1f617a", "Exit · 5", "New blocked-route scenario."),
                "MONITOR": "<p>Run 1 checks complete call/repeat. Run 2 checks sequencing and holding one aircraft. Run 3 checks revision under a changed constraint. If time slips, the third run becomes written; keep the individual timed plan.</p>",
                "RESOURCES": "<p>The simplified classroom model supports systems thinking and communication. It does not certify real aviation safety, radio language, or operational skill.</p>",
                "SUPPORT": "<p>Speaking, moving, recording, checking, writing, text, and media are equal routes. Keep the five steps visible and chunk one run at a time.</p>",
                "FALLBACK": "<p>Use the model map and written scenarios. No team performance is required for the individual evidence.</p>",
            },
            5: {
                "TITLE": "Aviation Route and Action Plan",
                "SUBTITLE": "50 minutes · TEKS d(4)(A), d(1)(C)",
                "ALERT": "<strong>Minor 1 in the 4SW assessment map.</strong> Keep the Assignment unpublished and ungraded until the Minor group and 40/60 weighting are verified.",
                "PREP": f'<ul><li>Post {file_link(files["PLAN"]["id"], "the Action Plan")} and {file_link(files["RUBRIC"]["id"], "the student-visible rubric")}.</li><li>Open the private unpublished Assignment.</li><li>Return Day 2 and Day 4 evidence.</li></ul>',
                "EVIDENCE": "<p>Private direction, source evidence, three timed stages, support, obstacle, backup, revision condition, self-score, and revision. Minor 1, scored with the 16-point rubric and converted to 100 gradebook points.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Direction, not lifetime promise.") + flow("#4a9d2f", "Two showcases · 8", "Transferable revision ideas.") + flow("#1f617a", "Reopen evidence · 10", "Work, preparation, tradeoff, skill, source.") + flow("#e3ad19", "Three stages · 20", "Actions, timing, support, backup, revision.") + flow("#1f617a", "Self-score/submit · 7", "Revise weakest section and submit privately."),
                "MONITOR": "<p>Suggested conversion after local approval: 15-16 Masters, 13-14 Meets, 12 Approaches, 10-11 Needs Improvement; below 10 follows campus policy. Score evidence and reasoning, not career preference, build quality, speaking, H&amp;L ratings, family military history, grammar unless meaning is unclear, or submission mode.</p>",
                "RESOURCES": "<p>H&amp;L browse, Xello Jobs and Employers, and eDynamic goal setting are optional after core evidence. The locked workbook App Exploration page is context only and does not prove platform completion.</p>",
                "SUPPORT": "<p>The six-page plan gives separate full-width areas for each reasoning job. Use speech-to-text, teacher scribe, or private media as needed.</p>",
                "FALLBACK": "<p>Missing simulation work uses the model log. Canvas failure means paper or later upload. No partner, family signature, public post, or live presentation is required.</p>",
            },
        }

        day_names = {
            1: "Transportation Cluster and Survey Design",
            2: "Aviation Careers and Pilot Routes",
            3: "Design a Classroom Airport Map",
            4: "Test, Communicate, and Revise",
            5: "Aviation Route and Action Plan",
        }
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 4SW Wk3 Day {day} - {day_names[day]}"
            student_page = await common.upsert_page(
                client,
                student_title,
                common.render(
                    "4sw-wk3-student.html",
                    {"COURSE_ID": COURSE_ID, "DAY": day, "MEDIA": media[day], **student[day]},
                ),
            )
            teacher_title = f"TEACHER: 4SW Wk3 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(
                client,
                teacher_title,
                common.render(
                    "4sw-wk3-teacher.html",
                    {
                        "COURSE_ID": COURSE_ID,
                        "DAY": day,
                        "STUDENT_PAGE_URL": student_page["url"],
                        **teacher[day],
                    },
                ),
            )
            await upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            order.extend([("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title)])
            pages[day] = {"teacher": teacher_page, "student": student_page}
            if day == 1:
                await upsert_item(client, module["id"], "Quiz", quiz["id"], QUIZ_TITLE)
                order.append(("Quiz", quiz["id"], QUIZ_TITLE))
            if day == 3:
                await upsert_item(client, module["id"], "Assignment", lab["id"], LAB_TITLE)
                order.append(("Assignment", lab["id"], LAB_TITLE))
            if day == 5:
                await upsert_item(client, module["id"], "Assignment", plan["id"], PLAN_TITLE)
                order.append(("Assignment", plan["id"], PLAN_TITLE))

        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(
                entry
                for entry in items
                if (kind == "SubHeader" and entry.get("id") == key)
                or (kind == "Page" and entry.get("page_url") == key)
                or (kind in ("Assignment", "Quiz") and entry.get("content_id") == key)
            )
            await common.api(
                client,
                "PUT",
                f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}",
                data={"module_item[position]": position, "module_item[title]": title},
            )

        final_items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        print(
            json.dumps(
                {
                    "module": {"id": module["id"], "published": module["published"]},
                    "quiz": {"id": quiz["id"], "published": quiz.get("published"), "quiz_type": quiz.get("quiz_type"), "allowed_attempts": quiz.get("allowed_attempts")},
                    "lab": {"id": lab["id"], "published": lab.get("published"), "submission_types": lab.get("submission_types"), "annotatable_attachment_id": lab.get("annotatable_attachment_id")},
                    "plan": {"id": plan["id"], "published": plan.get("published"), "submission_types": plan.get("submission_types"), "grading_type": plan.get("grading_type")},
                    "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
                    "visual_folders": {str(day): {"id": folder["id"], "locked": folder["locked"]} for day, folder in visual_folders.items()},
                    "files": {key: value["id"] for key, value in files.items()},
                    "visuals": {str(day): {name: value["id"] for name, value in entries.items()} for day, entries in visuals.items()},
                    "pages": {str(day): {kind: {"url": value["url"], "published": value["published"]} for kind, value in pair.items()} for day, pair in pages.items()},
                    "items": [{"position": item["position"], "type": item["type"], "title": item["title"]} for item in final_items],
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
