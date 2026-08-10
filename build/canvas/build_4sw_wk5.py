"""Build the unpublished 4SW Week 5 automotive evidence module."""

import asyncio
import json
import sys

import httpx

import build_4sw_wk1 as common


COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/4sw/wk5"
MODULE_NAME = "4SW Wk5: Automotive Evidence and Training Routes"
CRASH_TITLE = "PRACTICE: Crash Crew Evidence and Preliminary Plan"
ASE_QUIZ_TITLE = "PRACTICE: ASE and Training Route Check"
CAREER_TITLE = "PRACTICE: Compare Three Automotive Occupations"
SOURCE_QUIZ_TITLE = "PRACTICE: What Does This Source Prove?"
BRIEF_TITLE = "MINOR 3: Automotive Evidence Brief"


CONTRACTS = {
    1: {
        "TOPIC": "Career Clusters",
        "OBJECTIVE": "Students will explore and describe the Transportation, Distribution, and Logistics career cluster and identify automotive career opportunities by separating visible evidence from questions for a trained inspection.",
        "TEKS": "d(1)(B), d(1)(C)",
        "DOL": "Individual FYF p. 151 collision report plus three bounded inspection questions, a broad process sequence, and one changed-vehicle occupation response.",
        "I_CAN": "describe the Transportation cluster and show how an automotive worker separates visible evidence from questions for a trained inspection.",
        "SHOW": "Complete FYF p. 151, three bounded inspection questions, a broad process sequence, and one changed-vehicle occupation response.",
    },
    2: {
        "TOPIC": "Career Preparation",
        "OBJECTIVE": "Students will research and describe automotive preparation and certification requirements, evaluate three training options, and identify steps for entering a Registered Apprenticeship or technical-college route.",
        "TEKS": "d(2)(A), d(2)(B), d(3)(G)",
        "DOL": "Five-question ASE and Training Route practice Quiz with an individual Jordan recommendation using two source facts, one tradeoff or missing fact, and one verification step.",
        "I_CAN": "describe the ASE requirements, evaluate three training options, and name a real next step.",
        "SHOW": "Complete the five-question practice Quiz and recommend a first route for Jordan with two facts, one tradeoff or missing fact, and one verification step.",
    },
    3: {
        "TOPIC": "Career Preparation",
        "OBJECTIVE": "Students will research and describe preparation requirements and compare salaries for three automotive careers using one dated evidence basis.",
        "TEKS": "d(2)(A), d(5)(E)",
        "DOL": "Three-career comparison with all salary labels, preparation and task differences, one evidence limitation, and a Taylor recommendation.",
        "I_CAN": "describe preparation and compare salaries for three automotive careers without mixing evidence labels.",
        "SHOW": "Compare all three careers, keep the salary labels, explain one limitation, and recommend a first career for Taylor using two facts.",
    },
    4: {
        "TOPIC": "Training Options",
        "OBJECTIVE": "Students will evaluate automotive education and training options and identify application or enrollment questions for high-school, technical-college, and Registered Apprenticeship routes.",
        "TEKS": "d(2)(B), d(3)(G)",
        "DOL": "Four-question source-evidence practice Quiz with an individual Dani recommendation using two facts, one tradeoff or missing fact, and one authorized verification source.",
        "I_CAN": "evaluate three automotive training routes and write the next application or enrollment question.",
        "SHOW": "Complete the four-question practice Quiz and recommend Dani's first route with two facts, one tradeoff or missing fact, and one authorized verification source.",
    },
    5: {
        "TOPIC": "Career Opportunities",
        "OBJECTIVE": "Students will identify an automotive career opportunity, evaluate a realistic preparation route, and compare salaries for three careers using current evidence.",
        "TEKS": "d(1)(C), d(2)(B), d(3)(G), d(5)(E)",
        "DOL": "Private four-part Automotive Evidence Brief with visible self-score and revision.",
        "I_CAN": "identify an automotive direction, evaluate a preparation route, and compare three salaries without overclaiming the evidence.",
        "SHOW": "Submit a private four-part Automotive Evidence Brief with a self-score and one visible revision.",
    },
}


QUIZZES = {
    ASE_QUIZ_TITLE: [
        {
            "name": "Q1 - ASE distinction",
            "prompt": "Which statement is accurate?",
            "correct": "ASE Entry-Level and professional ASE certification are different; professional certification requires the applicable test and approved experience or substitution.",
            "wrong": [
                "Any automotive classroom test creates professional ASE certification.",
                "ASE Entry-Level requires two years of work experience.",
                "A school can guarantee every student professional ASE certification.",
            ],
            "yes": "Correct. Keep the credential context and experience requirement accurate.",
            "no": "Passing one test does not erase the professional work-experience requirement.",
        },
        {
            "name": "Q2 - Employer learning",
            "prompt": "Which claim stays within the BLS evidence?",
            "correct": "Some workers enter with a high school diploma and learn on the job; the exact employer route still must be verified.",
            "wrong": [
                "Every dealership offers a Registered Apprenticeship.",
                "Every technician must first earn an associate degree.",
                "On-the-job learning guarantees professional ASE certification.",
            ],
            "yes": "Correct. The statement keeps the preparation route and its limit.",
            "no": "The source describes a common route, not a guarantee from every employer.",
        },
        {
            "name": "Q3 - Registered apprenticeship",
            "prompt": "Which feature belongs to a Registered Apprenticeship?",
            "correct": "Paid employment with structured on-the-job learning, related instruction, mentorship, and sponsor-controlled admission",
            "wrong": [
                "Every dealership job automatically qualifies.",
                "Four unpaid years before work begins.",
                "Guaranteed admission for every applicant.",
            ],
            "yes": "Correct. Registered Apprenticeship is a specific sponsored training model.",
            "no": "Do not use apprenticeship as a label for every job with informal training.",
        },
        {
            "name": "Q4 - TCC label",
            "prompt": "TCC lists $888 for a 12-credit award in 2026-27. Which label must stay with that figure?",
            "correct": "In-state, in-county tuition and fees; books and other materials excluded",
            "wrong": [
                "Total cost for every student",
                "DFW apprenticeship wage",
                "Guaranteed price for all future years",
            ],
            "yes": "Correct. Residency, year, and exclusions remain attached.",
            "no": "The published figure is a bounded tuition-and-fee estimate.",
        },
        {
            "name": "Q5 - Jordan recommendation",
            "type": "essay_question",
            "prompt": "Jordan needs income soon, can travel only within DFW, and may want an associate degree later. Recommend the first route Jordan should investigate. Use two source facts, name one tradeoff or missing fact, and write one exact verification step.",
        },
    ],
    SOURCE_QUIZ_TITLE: [
        {
            "name": "Q1 - HQIM and current source",
            "prompt": "Which statement uses the automotive sources correctly?",
            "correct": "Use FYF's Automotive Technology, Collision Repair, and Diesel & Heavy Equipment Technology names, then use current district sources for campuses and enrollment logistics.",
            "wrong": [
                "Ignore the workbook and rename every program from memory.",
                "Assume every workbook example guarantees current admission.",
                "Treat a college page as the Irving high-school coursebook.",
            ],
            "yes": "Correct. The HQIM supplies the student-facing program context; current sources answer current logistics questions.",
            "no": "Keep the HQIM vocabulary and use the correct current source for details it does not state.",
        },
        {
            "name": "Q2 - Source gap",
            "prompt": "The current district page does not state transportation or schedule details. What should the student record?",
            "correct": "Not confirmed in this source; ask the counselor or current program contact",
            "wrong": [
                "Invent the most likely schedule.",
                "Assume transportation is included.",
                "Use a private-school advertisement as the district answer.",
            ],
            "yes": "Correct. Accurate uncertainty is stronger than a guess.",
            "no": "A missing logistics field remains a verification question.",
        },
        {
            "name": "Q3 - TCC cost",
            "prompt": "Which claim stays within the TCC source?",
            "correct": "The 2026-27 in-county estimate is $4,440 for the 60-credit AAS, excluding books and other materials.",
            "wrong": [
                "Every student pays exactly $4,440 total.",
                "The AAS is free for Irving students.",
                "TCC guarantees an automotive job.",
            ],
            "yes": "Correct. The claim retains the assumptions and exclusions.",
            "no": "Do not convert an estimate into a guarantee.",
        },
        {
            "name": "Q4 - Dani recommendation",
            "type": "essay_question",
            "prompt": "Dani needs a low-cost, hands-on automotive route and may want college credit later. Recommend the first route Dani should investigate. Use two facts, name one tradeoff or missing fact, and write the exact question Dani should ask an authorized source.",
        },
    ],
}


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    found = next((entry for entry in modules if entry["name"] == MODULE_NAME), None)
    data = {"module[published]": "false"}
    if found:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data=data)
    data["module[name]"] = MODULE_NAME
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


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


async def upsert_quiz(client, title, questions):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    found = next((entry for entry in quizzes if entry.get("title") == title), None)
    data = {
        "quiz[title]": title,
        "quiz[description]": "<p>Ungraded, retryable evidence practice. Selected-response items provide immediate feedback. The final short response is individual and may be completed in the paper fallback when needed.</p>",
        "quiz[quiz_type]": "practice_quiz",
        "quiz[published]": "false",
        "quiz[allowed_attempts]": "-1",
        "quiz[show_correct_answers]": "true",
        "quiz[shuffle_answers]": "false",
    }
    endpoint = f"/courses/{COURSE_ID}/quizzes/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes"
    quiz = await common.api(client, "PUT" if found else "POST", endpoint, data=data)
    existing = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    desired_names = {question["name"] for question in questions}
    for prior in existing:
        if prior.get("question_name") not in desired_names:
            await common.api(
                client,
                "DELETE",
                f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior['id']}",
            )
    existing = [prior for prior in existing if prior.get("question_name") in desired_names]
    for position, question in enumerate(questions, 1):
        prior = next((entry for entry in existing if entry.get("question_name") == question["name"]), None)
        item = {
            "question_name": question["name"],
            "question_text": question["prompt"],
            "question_type": question.get("type", "multiple_choice_question"),
            "position": position,
            "points_possible": 1,
        }
        if item["question_type"] == "multiple_choice_question":
            item.update(
                {
                    "correct_comments": question["yes"],
                    "incorrect_comments": question["no"],
                    "answers": [{"answer_text": question["correct"], "answer_weight": 100}]
                    + [{"answer_text": answer, "answer_weight": 0} for answer in question["wrong"]],
                }
            )
        payload = {"question": item}
        path = (
            f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior['id']}"
            if prior
            else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        )
        await common.api(client, "PUT" if prior else "POST", path, json=payload)
    return await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


async def require_minor_assignment(client, description):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == BRIEF_TITLE]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one existing mapped Minor assignment named {BRIEF_TITLE!r}; found {len(matches)}")
    found = matches[0]
    if float(found.get("points_possible") or 0) != 100:
        raise RuntimeError(f"Refusing to modify {BRIEF_TITLE!r}: expected 100 points, found {found.get('points_possible')}")
    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group = next((entry for entry in groups if entry.get("id") == found.get("assignment_group_id")), None)
    if not group or group.get("name") != "Minor Assessments (40%)":
        raise RuntimeError(f"Refusing to modify {BRIEF_TITLE!r}: expected Minor Assessments (40%) group")
    return await common.api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{found['id']}",
        data={
            "assignment[description]": description,
            "assignment[submission_types][]": ["online_upload", "online_text_entry", "media_recording"],
            "assignment[published]": "false",
        },
    )


def image_tag(file_id, alt, caption):
    return (
        f'<figure style="margin:16px auto;text-align:center"><img loading="lazy" '
        f'src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" '
        'style="display:block;width:100%;max-width:700px;height:auto;margin:0 auto;border:1px solid #ddd" '
        f'data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'
        f'<figcaption style="font-size:14px;color:#52616b;margin-top:6px">{caption}</figcaption></figure>'
    )


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        module = await ensure_module(client)
        support_path = "course files/CCR Materials/4SW/Wk5"
        support_folder = await common.ensure_folder(client, support_path)
        names = {
            "CRASH": "4sw-wk5-crash-crew-evidence-and-preliminary-plan.pdf",
            "ASE": "4sw-wk5-ase-and-automotive-training-routes.pdf",
            "CAREERS": "4sw-wk5-three-automotive-occupations.pdf",
            "ROUTES": "4sw-wk5-automotive-route-decision.pdf",
            "BRIEF": "4sw-wk5-automotive-evidence-brief.pdf",
            "RUBRIC": "4sw-wk5-automotive-evidence-rubric.pdf",
        }
        files = {
            key: await common.upload(client, ROOT / "docs/resources/worksheets" / name, support_path)
            for key, name in names.items()
        }

        day1_path = "course files/CCR Materials/4SW/Wk5/Day 1 Visuals"
        day1_folder = await common.ensure_folder(client, day1_path)
        day1_assets = {
            "views": await common.upload(client, ASSETS / "day1/fyf-crash-crew-vehicle-views.jpg", day1_path),
            "report": await common.upload(client, ASSETS / "day1/fyf-crash-crew-collision-report.jpg", day1_path),
            "plan": await common.upload(client, ASSETS / "day1/fyf-crash-crew-repair-plan.jpg", day1_path),
        }
        day4_path = "course files/CCR Materials/4SW/Wk5/Day 4 Visuals"
        day4_folder = await common.ensure_folder(client, day4_path)
        day4_assets = {
            "programs": await common.upload(client, ASSETS / "day4/fyf-automotive-programs.jpg", day4_path),
            "spotlight": await common.upload(client, ASSETS / "day4/fyf-automotive-program-spotlight.jpg", day4_path),
        }

        quizzes = {
            title: await upsert_quiz(client, title, questions)
            for title, questions in QUIZZES.items()
        }
        crash_description = (
            f'<p><strong>Workbook first:</strong> complete FYF p. 151, then answer the three numbered evidence jobs below. '
            f'Use the <a href="/courses/{COURSE_ID}/files/{files["CRASH"]["id"]}/preview">three-page companion</a> '
            'only for no-workbook, enlarged, or Canvas-annotation access.</p><ol><li>Write three bounded inspection questions for visible conditions.</li>'
            '<li>Put the broad shop stages in a safe order.</li><li>For a vehicle with cameras or sensors behind the bumper, name one added question and one automotive occupation with a bounded role.</li></ol>'
            '<p>This is a fictional visible-evidence exercise, not a real vehicle diagnosis or repair procedure.</p>'
        )
        crash = await common.upsert_assignment(
            client,
            CRASH_TITLE,
            crash_description,
            ["student_annotation", "online_upload", "online_text_entry"],
            files["CRASH"]["id"],
        )
        career = await common.upsert_assignment(
            client,
            CAREER_TITLE,
            "<p>Complete the fixed three-occupation comparison by Canvas annotation, upload, text, or paper. Keep year, geography, and measure with every salary figure.</p>",
            ["student_annotation", "online_upload", "online_text_entry"],
            files["CAREERS"]["id"],
        )
        brief_description = (
            f'<p>Submit the private Automotive Evidence Brief by upload, text, media, or paper. Use the '
            f'<a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">student-visible 16-point rubric</a>. '
            'Complete the same four evidence jobs in every submission mode. Career preference and public speaking are not graded.</p>'
        )
        brief = await require_minor_assignment(client, brief_description)
        urls = {
            "crash": f"/courses/{COURSE_ID}/assignments/{crash['id']}",
            "ase": f"/courses/{COURSE_ID}/quizzes/{quizzes[ASE_QUIZ_TITLE]['id']}",
            "career": f"/courses/{COURSE_ID}/assignments/{career['id']}",
            "source": f"/courses/{COURSE_ID}/quizzes/{quizzes[SOURCE_QUIZ_TITLE]['id']}",
            "brief": f"/courses/{COURSE_ID}/assignments/{brief['id']}",
        }
        media = {
            1: (
                image_tag(day1_assets["views"]["id"], "Find Your Future Crash Crew fictional red vehicle shown from three front-left angles with visible bumper, fender, and headlight damage", "FYF p. 150: examine all three views before writing.")
                + image_tag(day1_assets["report"]["id"], "Find Your Future Crash Crew collision report with fields for vehicle description, area, damaged parts, visible damage, and possible cause", "FYF p. 151: this is the default student writing surface.")
                + '<details style="border:1px solid #d2d2d2;border-radius:8px;padding:12px 16px;margin:16px 0"><summary style="font-weight:700;cursor:pointer">Open FYF p. 152 only when your teacher directs you</summary>'
                + image_tag(day1_assets["plan"]["id"], "Find Your Future Crash Crew repair-plan page with repair-or-replace table, broad repair-plan space, time estimate, and discussion prompts", "FYF p. 152: use it for broad questions only. Do not write operational repair instructions.")
                + '</details>'
            ),
            2: "",
            3: "",
            4: (
                image_tag(day4_assets["programs"]["id"], "Find Your Future Irving ISD programs page naming Automotive Technology, Collision Repair, Diesel and Heavy Equipment Technology, and Aviation Maintenance", "FYF p. 168: use these HQIM program names.")
                + image_tag(day4_assets["spotlight"]["id"], "Find Your Future program spotlight naming Automotive Service Excellence, SkillsUSA, and Automotive Enterprise Days", "FYF p. 169: district-customized program context.")
            ),
            5: "",
        }
        link, step, flow = common.file_link, common.step, common.flow

        student = {
            1: {
                "TITLE": "Crash Crew: Visible Evidence",
                "PURPOSE": "Use the workbook collision case to separate visible evidence from questions for a trained inspection.",
                "TODAY": "<ul><li>read the fictional Crash Crew problem;</li><li>complete FYF p. 151;</li><li>write three bounded inspection questions;</li><li>revise for a sensor-equipped vehicle.</li></ul>",
                "READY": f'<p>Open FYF pp. 150-151 and <a href="{urls["crash"]}">the private Crash Crew evidence check</a>. Use {link(files["CRASH"]["id"], "the three-page companion")} only if you need the no-workbook, enlarged, or annotation route.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:12px 16px;margin:14px 0"><strong>Words for this task:</strong> part/pieza · visible condition/condición visible · inspect/inspeccionar · confirm/confirmar<br><strong>Use this frame:</strong> “The image supports ____. It does not prove ____. A ____ would next ____ because ____.”</div>',
                "STEPS": step(1, "Read and observe", "<p>Look at all three vehicle views before writing. Do not use a real vehicle or personal crash story.</p>")
                + step(2, "Complete FYF p. 151", "<p>Describe cracked, creased, shifted, missing, or scratched conditions. Mark an uncertain part name <strong>confirm</strong>.</p>")
                + step(3, "Write bounded questions", "<p>Ask what an authorized technician or approved source would still need. Do not invent settings, structural pulls, airbag work, or calibration instructions.</p>")
                + step(4, "Change the vehicle", "<p>Add one question for cameras or sensors behind the bumper and name the occupation that would contribute next.</p>"),
                "EXIT": "<p>Respond to the customer who says the damage is only cosmetic and the vehicle is safe.</p>",
                "DONE": "<ul><li>FYF p. 151 or four evidence rows;</li><li>three bounded inspection questions;</li><li>broad process sequence;</li><li>changed-vehicle question;</li><li>one occupation and bounded role.</li></ul>",
                "SUPPORT": "<p>Say the observation aloud before writing. A part is a noun; a condition is what you can see. Typing, dictation, annotation, upload, and paper are equal routes.</p>",
                "FALLBACK": "<p>The embedded pages and companion are the complete independent route. No live vehicle, partner, H&amp;L login, or open search is required.</p>",
            },
            2: {
                "TITLE": "ASE and Automotive Training Routes",
                "PURPOSE": "Separate credential contexts and compare employer training, Registered Apprenticeship, and public technical college.",
                "TODAY": "<ul><li>repair one ASE misconception;</li><li>read three short route cards;</li><li>compare the routes for fictional Jordan;</li><li>submit one evidence-based recommendation.</li></ul>",
                "READY": f'<p>Open <a href="{urls["ase"]}">the five-question practice Quiz</a>. The source cards are built into the lesson. Use {link(files["ASE"]["id"], "the three-page fallback")} only for no-device, enlarged, or paper access.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:12px 16px;margin:14px 0"><strong>Words for this task:</strong> credential/credencial · experience/experiencia · route/ruta · tradeoff/ventaja y costo<br><strong>Use this frame:</strong> “Jordan should investigate ____ first because ____ and ____. A tradeoff or missing fact is ____. Jordan should verify ____ with ____.”</div>',
                "STEPS": step(1, "Separate the ASE contexts", "<p>Entry-Level has no work-experience requirement. Professional certification requires the applicable test and approved experience or substitution.</p>")
                + step(2, "Compare three routes", "<p>Employer/OJT is not automatically a Registered Apprenticeship. Keep TCC's year, residency assumption, and exclusions with its costs.</p>")
                + step(3, "Recommend for Jordan", "<p>Use two facts, one tradeoff or missing fact, and one authorized verification step.</p>")
                + step(4, "Submit the Quiz", "<p>Repair any selected-response item after feedback. The final short response remains individual.</p>"),
                "EXIT": "<p>Your Quiz response is the exit check: first route, two facts, one tradeoff or missing fact, and one verification step.</p>",
                "DONE": "<ul><li>five Quiz items;</li><li>ASE distinction;</li><li>all three routes considered;</li><li>two source facts;</li><li>one tradeoff or missing fact;</li><li>one verification step.</li></ul>",
                "SUPPORT": "<p>Read one card and answer one item at a time. Speech-to-text or a private audio response may replace the final typed paragraph.</p>",
                "FALLBACK": "<p>The three-page fallback is the complete no-device route. No private-school marketing site or H&amp;L login is required.</p>",
            },
            3: {
                "TITLE": "Compare Three Automotive Occupations",
                "PURPOSE": "Compare three careers on one dated salary basis and keep every limitation visible.",
                "TODAY": "<ul><li>read three fixed BLS cards;</li><li>rank all three medians;</li><li>compare preparation and tasks;</li><li>recommend an occupation for fictional Taylor.</li></ul>",
                "READY": f'<p>Open {link(files["CAREERS"]["id"], "the three-page landscape comparison")} or <a href="{urls["career"]}">the Canvas annotation activity</a>. Salary means May 2024 U.S. national median annual wage.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:12px 16px;margin:14px 0"><strong>Words for this task:</strong> median/mediana · openings/vacantes · preparation/preparación · limitation/limitación<br><strong>Use this frame:</strong> “Taylor should investigate ____ because ____ and ____. The national evidence cannot answer ____, so Taylor should verify it with ____.”</div>',
                "STEPS": step(1, "Read one card at a time", "<p>Auto Service, Diesel Service, and Automotive Body/Related Repair are distinct occupations.</p>")
                + step(2, "Compare all three", "<p>Rank medians and compare preparation, growth, openings, and one task difference.</p>")
                + step(3, "Keep the limitation", "<p>National evidence is not DFW starting pay. Body/glass outlook and openings use a combined group.</p>")
                + step(4, "Recommend for Taylor", "<p>Use two facts and one local question that national data cannot answer.</p>"),
                "EXIT": "<p>Complete the comparison and write a bounded Taylor recommendation.</p>",
                "DONE": "<ul><li>all three medians;</li><li>preparation and task comparison;</li><li>one limitation;</li><li>two-fact recommendation;</li><li>authorized local source.</li></ul>",
                "SUPPORT": "<p>Highlight year, geography, and measure before comparing. Do not calculate salary divided by years of education.</p>",
                "FALLBACK": "<p>The fixed guide is the full no-login route. Xello may add a separately labeled local cross-check; H&amp;L is optional.</p>",
            },
            4: {
                "TITLE": "Evaluate Automotive Training Routes",
                "PURPOSE": "Use the HQIM program names, current logistics, and route evidence to recommend a first investigation step.",
                "TODAY": "<ul><li>read FYF pp. 168-169;</li><li>compare Irving, TCC, and Registered Apprenticeship evidence;</li><li>recommend for fictional Dani;</li><li>write an exact verification question.</li></ul>",
                "READY": f'<p>Open FYF pp. 168-169 and <a href="{urls["source"]}">the four-question source Quiz</a>. Use {link(files["ROUTES"]["id"], "the two-page fallback")} only for no-device, enlarged, or paper access.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:12px 16px;margin:14px 0"><strong>Words for this task:</strong> admission/admisión · tuition/matrícula · sponsor/patrocinador · verify/verificar<br><strong>Use this frame:</strong> “Dani should investigate ____ first because ____ and ____. A tradeoff or missing fact is ____. Dani should ask ____ whether ____.”</div>',
                "STEPS": step(1, "Use the HQIM names", "<p>FYF names Automotive Technology, Collision Repair, and Diesel &amp; Heavy Equipment Technology. The current district page confirms the broader offering at four campuses.</p>")
                + step(2, "Preserve logistics questions", "<p>Write <strong>not confirmed in this source</strong> for grade, prerequisite, schedule, transportation, or credential details the source does not state.</p>")
                + step(3, "Compare three routes", "<p>Keep TCC year, residency, and exclusions and Registered Apprenticeship sponsor admission with the evidence.</p>")
                + step(4, "Recommend for Dani", "<p>Address low cost, hands-on work, and possible future college credit without guaranteeing admission, certification, or hiring.</p>"),
                "EXIT": "<p>Your Quiz response is the exit check: first route, two facts, one tradeoff or missing fact, and one exact question.</p>",
                "DONE": "<ul><li>four Quiz items;</li><li>HQIM program names;</li><li>three routes considered;</li><li>two source facts;</li><li>one tradeoff or missing fact;</li><li>authorized verification source.</li></ul>",
                "SUPPORT": "<p>Accurate uncertainty is stronger than a guess. Use the images, read-aloud, chunked cards, or speech-to-text.</p>",
                "FALLBACK": "<p>The two-page fallback and embedded HQIM pages are the complete route when a site fails. No private-school search is required.</p>",
            },
            5: {
                "TITLE": "Automotive Evidence Brief",
                "PURPOSE": "Synthesize visible evidence, three-career data, and a realistic training route into one private recommendation.",
                "TODAY": "<ul><li>reopen Days 1-4 evidence;</li><li>complete four response jobs;</li><li>self-score and revise;</li><li>submit privately.</li></ul>",
                "READY": f'<p>Open {link(files["BRIEF"]["id"], "the four-page Evidence Brief")} and {link(files["RUBRIC"]["id"], "the two-page 16-point rubric")}. The PDF is the paper or enlarged route; typed and private media responses use the same four jobs.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:12px 16px;margin:14px 0"><strong>Words for this task:</strong> evidence/evidencia · route/ruta · tradeoff/ventaja y costo · limitation/limitación · revise/revisar<br><strong>Use the complete frame beside each of the four response jobs.</strong></div>',
                "STEPS": step(1, "Bring forward evidence", "<p>Use one Crash Crew boundary, all three salary labels, one ASE distinction, one route tradeoff, and one authorized source.</p>")
                + step(2, "Write four sections", "<p>Visible evidence; three-career comparison and direction; preparation route; limitation, next action, and revision.</p>")
                + step(3, "Self-score and revise", "<p>Revise the weakest criterion. Career preference itself is not graded.</p>")
                + step(4, "Submit privately", f'<p><a href="{urls["brief"]}">Submit by upload, text, media, or paper</a>.</p>'),
                "EXIT": "<p>Audit three accurate labels, two comparisons, and one unsupported claim removed.</p>",
                "DONE": "<ul><li>four response jobs;</li><li>all three career medians;</li><li>route advantage and tradeoff;</li><li>verification question;</li><li>seven-day action;</li><li>visible revision and private submission.</li></ul>",
                "SUPPORT": "<p>Each multi-sentence job has a full-width block. Use typing, speech-to-text, private media, teacher scribe, or paper.</p>",
                "FALLBACK": "<p>Use the model evidence strip when prior work is missing. Save careers is not repeated. Canvas failure means paper or later upload.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Crash Crew: Visible Evidence",
                "SUBTITLE": "50 minutes · TEKS d(1)(B), d(1)(C)",
                "ALERT": "<strong>Workbook first; preliminary evidence only.</strong> Students use FYF p. 151, then complete the private bounded-question response. They do not diagnose a real vehicle, declare it safe, or invent structural, restraint, electrical, tool, or calibration procedures.",
                "PREP": f'<ul><li>Tell students to open FYF pp. 150-151.</li><li>Post <a href="{urls["crash"]}">the Crash Crew evidence check</a>.</li><li>Keep {link(files["CRASH"]["id"], "the three-page companion")} only for no-workbook, enlarged, or annotation access.</li><li>Model part versus visible condition.</li></ul>',
                "EVIDENCE": "<p>FYF p. 151 plus three bounded questions, broad process sequence, changed-vehicle decision, and occupation role. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Seen versus not yet known.") + flow("#4a9d2f", "Problem · 8", "Cluster, customer need, image limit.") + flow("#1f617a", "FYF p. 151 · 12", "Neutral visible evidence.") + flow("#e3ad19", "Bounded questions · 15", "Questions and broad sequence.") + flow("#4a9d2f", "Changed vehicle · 5", "Sensors behind bumper.") + flow("#1f617a", "Exit · 5", "Respond to unsafe overclaim."),
                "MONITOR": "<p>Parts are nouns; conditions are observations. Require <strong>confirm</strong> on uncertain labels. A full occupation statement names what the worker contributes without prescribing a real repair.</p>",
                "RESOURCES": "<p>FYF pp. 150-152 supply the licensed fictional scenario. The Canvas companion turns the open repair prompt into a safer evidence-and-authorization question without replacing the workbook.</p>",
                "SUPPORT": "<p>Keep the point-of-use word bank and frame visible. Allow oral rehearsal, typing, dictation, annotation, upload, or paper. The image and adjacent description support absence and low-vision discussion.</p>",
                "FALLBACK": "<p>No live vehicle, partner, personal story, H&amp;L, or open search is required. Page 1 of the companion replaces FYF p. 151 only when the workbook is unavailable.</p>",
            },
            2: {
                "TITLE": "ASE and Automotive Training Routes",
                "SUBTITLE": "50 minutes · TEKS d(2)(A), d(2)(B), d(3)(G)",
                "ALERT": "<strong>Do not collapse the credentials.</strong> Entry-Level has no work-experience requirement. Professional ASE certification requires the test and approved experience or substitution.",
                "PREP": f'<ul><li>Post the five-question practice Quiz.</li><li>Keep {link(files["ASE"]["id"], "the three-page fallback")} for no-device or paper access.</li><li>Open current ASE, TWC, BLS, and TCC pages.</li></ul>',
                "EVIDENCE": "<p>Four selected-response checks plus an individual Jordan recommendation with two facts, a tradeoff or missing fact, and verification step. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Credential, training, or job.") + flow("#4a9d2f", "ASE · 8", "Entry-Level versus professional.") + flow("#1f617a", "Route cards · 12", "OJT, Registered Apprenticeship, TCC.") + flow("#e3ad19", "Quiz and compare · 18", "Feedback plus Jordan response.") + flow("#1f617a", "Repair and exit · 7", "Revise one item and submit."),
                "MONITOR": "<p>Reject fixed test fees, universal wage premiums, guaranteed certification, and the claim that every dealership job is a Registered Apprenticeship. There is no predetermined winning route.</p>",
                "RESOURCES": '<p><a href="https://www.ase.com/entry-level/">ASE Entry-Level</a> · <a href="https://ase.com/tests/work-experience/">ASE experience</a> · <a href="https://www.twc.texas.gov/programs/apprenticeship/apprenticeshiptexas">TWC ApprenticeshipTexas</a> · <a href="https://www.tccd.edu/academics/courses-and-programs/programs-a-z/credit/automotive-automotive-service-technology/">TCC Automotive</a></p>',
                "SUPPORT": "<p>Read one source card and answer one item at a time. The fallback separates supported fact, advantage, tradeoff, and missing fact. Permit speech-to-text or private audio for the final response.</p>",
                "FALLBACK": "<p>The three-page fallback is the complete route when the Quiz or sites fail. Do not print it by default. No private-school marketing research is needed.</p>",
            },
            3: {
                "TITLE": "Compare Three Automotive Occupations",
                "SUBTITLE": "50 minutes · TEKS d(2)(A), d(5)(E)",
                "ALERT": "<strong>One comparison basis.</strong> May 2024 U.S. national medians are not DFW starting or experienced salaries. Keep combined-group labels on body/glass outlook evidence.",
                "PREP": f'<ul><li>Post {link(files["CAREERS"]["id"], "the three-page landscape comparison")} and annotation activity.</li><li>Print only for paper or enlarged access.</li><li>Have a calculator available for dollar differences only.</li></ul>',
                "EVIDENCE": "<p>All three careers, salary ranking, preparation and task comparison, limitation, and Taylor recommendation. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Repair missing labels.") + flow("#4a9d2f", "Cards · 12", "One occupation at a time.") + flow("#1f617a", "Compare · 18", "All three on one basis.") + flow("#e3ad19", "Recommend · 10", "Two facts and local question.") + flow("#1f617a", "Exit · 5", "Matrix and limitation."),
                "MONITOR": "<p>Key medians: auto $49,670; diesel $60,640; body/related $51,680. Growth/openings: auto 4%/70,000; diesel 2%/26,500; body/glass group 2%/16,000. Do not calculate salary divided by universal education years.</p>",
                "RESOURCES": '<p><a href="https://www.bls.gov/ooh/installation-maintenance-and-repair/automotive-service-technicians-and-mechanics.htm">BLS Auto</a> · <a href="https://www.bls.gov/ooh/installation-maintenance-and-repair/diesel-service-technicians-and-mechanics.htm">BLS Diesel</a> · <a href="https://www.bls.gov/ooh/installation-maintenance-and-repair/automotive-body-and-glass-repairers.htm">BLS Body/Glass</a></p>',
                "SUPPORT": "<p>Keep the point-of-use frame visible. Highlight year, geography, and measure. The landscape design keeps paragraph responses out of narrow cells.</p>",
                "FALLBACK": "<p>No live site is load-bearing. Xello-localized data stays in a separately labeled cross-check; H&amp;L is optional.</p>",
            },
            4: {
                "TITLE": "Evaluate Automotive Training Routes",
                "SUBTITLE": "50 minutes · TEKS d(2)(B), d(3)(G)",
                "ALERT": "<strong>Use the HQIM and the right current source for the right job.</strong> FYF supplies the student-facing program names. The current district page confirms the broader offering and campuses. The current coursebook, counselor, or CTE program confirms enrollment logistics.",
                "PREP": f'<ul><li>Post FYF pp. 168-169 and the four-question source Quiz.</li><li>Keep {link(files["ROUTES"]["id"], "the two-page fallback")} for no-device or paper access.</li><li>Open the current Irving CTE page and keep TCC/TWC cards ready.</li></ul>',
                "EVIDENCE": "<p>Three selected-response checks plus an individual Dani recommendation with two facts, a tradeoff or missing fact, and exact verification question. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "HQIM fact, logistics fact, question.") + flow("#4a9d2f", "Local route · 10", "Program names and current campuses.") + flow("#1f617a", "Compare · 20", "Irving, TCC, Registered Apprenticeship.") + flow("#e3ad19", "Quiz and recommend · 10", "Cost, hands-on, future credit.") + flow("#1f617a", "Exit · 5", "Exact verification question."),
                "MONITOR": "<p>Current district evidence confirms Automotive, Collision Repair and Diesel at Cardwell, Irving, MacArthur, and Nimitz. Accept <strong>not confirmed</strong> for logistics the source does not state. Keep TCC's 2026-27 in-county assumption and exclusions visible.</p>",
                "RESOURCES": '<p><a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte">Irving High School CTE</a> · <a href="https://www.tccd.edu/academics/courses-and-programs/programs-a-z/credit/automotive-automotive-service-technology/">TCC Automotive</a> · <a href="https://www.twc.texas.gov/programs/apprenticeship/apprenticeshiptexas">TWC ApprenticeshipTexas</a></p>',
                "SUPPORT": "<p>Keep the HQIM images, word bank, and full frame visible. Chunk by route. The fallback gives multi-sentence reasoning a full-width block.</p>",
                "FALLBACK": "<p>The embedded HQIM pages and two-page fallback are complete when sites fail. Do not print the fallback by default. No private-school search is required.</p>",
            },
            5: {
                "TITLE": "Automotive Evidence Brief",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(2)(B), d(3)(G), d(5)(E)",
                "ALERT": "<strong>Minor 3 in the 4SW assessment map.</strong> The protected Assignment must remain in Minor Assessments (40%), worth 100 gradebook points, and unpublished for teacher cloning. Save careers is not repeated.",
                "PREP": f'<ul><li>Post {link(files["BRIEF"]["id"], "the four-page Evidence Brief")} and {link(files["RUBRIC"]["id"], "the two-page student rubric")}.</li><li>Open the protected private unpublished Minor Assignment.</li><li>Return or provide model evidence from Days 1-4.</li></ul>',
                "EVIDENCE": "<p>Private four-part synthesis, source audit, self-score, revision, and next action. Minor 3, scored with the 16-point rubric and converted to 100 gradebook points.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Repair two overclaims.") + flow("#4a9d2f", "Models · 8", "Two trustworthy evidence moves.") + flow("#1f617a", "Audit · 10", "Days 1-4 labels.") + flow("#e3ad19", "Brief · 20", "Four response jobs.") + flow("#1f617a", "Revise/submit · 7", "Weakest criterion and private submission."),
                "MONITOR": "<p>Suggested evidence profile: 15-16 Masters, 13-14 Meets, 12 Approaches, 10-11 Needs Improvement; below 10 follows campus policy. Score evidence and reasoning, not career preference, speaking, platform access, vehicle knowledge, or grammar unless meaning is unclear.</p>",
                "RESOURCES": "<p>The fixed evidence set is the complete source base. H&amp;L and Xello career browse are optional; no completion screenshot or public result is required.</p>",
                "SUPPORT": "<p>Four pages separate the four response jobs. Keep the point-of-use frames visible. Allow typing, speech-to-text, private media, teacher scribe, or paper.</p>",
                "FALLBACK": "<p>Missing prior work uses the model strip. Canvas failure means paper or later upload without penalty.</p>",
            },
        }

        day_names = {
            1: "Crash Crew Visible Evidence",
            2: "ASE and Training Routes",
            3: "Three Automotive Occupations",
            4: "Automotive Route Decision",
            5: "Automotive Evidence Brief",
        }
        extras = {
            1: ("Assignment", crash["id"], CRASH_TITLE),
            2: ("Quiz", quizzes[ASE_QUIZ_TITLE]["id"], ASE_QUIZ_TITLE),
            3: ("Assignment", career["id"], CAREER_TITLE),
            4: ("Quiz", quizzes[SOURCE_QUIZ_TITLE]["id"], SOURCE_QUIZ_TITLE),
            5: ("Assignment", brief["id"], BRIEF_TITLE),
        }
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 4SW Wk5 Day {day} - {day_names[day]}"
            student_page = await common.upsert_page(
                client,
                student_title,
                common.render(
                    "4sw-wk5-student.html",
                    {"COURSE_ID": COURSE_ID, "DAY": day, "MEDIA": media[day], **CONTRACTS[day], **student[day]},
                ),
            )
            teacher_title = f"TEACHER: 4SW Wk5 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(
                client,
                teacher_title,
                common.render(
                    "4sw-wk5-teacher.html",
                    {
                        "COURSE_ID": COURSE_ID,
                        "DAY": day,
                        "STUDENT_PAGE_URL": student_page["url"],
                        **CONTRACTS[day],
                        **teacher[day],
                    },
                ),
            )
            await upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title)]
            pages[day] = {"teacher": teacher_page, "student": student_page}
            kind, key, title = extras[day]
            await upsert_item(client, module["id"], kind, key, title)
            order.append((kind, key, title))

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
                    "quizzes": {
                        title: {
                            "id": quiz["id"],
                            "published": quiz.get("published"),
                            "quiz_type": quiz.get("quiz_type"),
                            "allowed_attempts": quiz.get("allowed_attempts"),
                        }
                        for title, quiz in quizzes.items()
                    },
                    "assignments": {
                        "crash": {"id": crash["id"], "published": crash.get("published"), "submission_types": crash.get("submission_types"), "annotatable_attachment_id": crash.get("annotatable_attachment_id")},
                        "career": {"id": career["id"], "published": career.get("published"), "submission_types": career.get("submission_types"), "annotatable_attachment_id": career.get("annotatable_attachment_id")},
                        "brief": {"id": brief["id"], "published": brief.get("published"), "submission_types": brief.get("submission_types"), "grading_type": brief.get("grading_type"), "points_possible": brief.get("points_possible"), "assignment_group_id": brief.get("assignment_group_id")},
                    },
                    "folders": {"support": {"id": support_folder["id"], "locked": support_folder["locked"]}, "day1": {"id": day1_folder["id"], "locked": day1_folder["locked"]}, "day4": {"id": day4_folder["id"], "locked": day4_folder["locked"]}},
                    "files": {key: value["id"] for key, value in files.items()},
                    "licensed_visuals": {"day1": {key: value["id"] for key, value in day1_assets.items()}, "day4": {key: value["id"] for key, value in day4_assets.items()}},
                    "pages": {str(day): {kind: {"url": value["url"], "published": value["published"]} for kind, value in pair.items()} for day, pair in pages.items()},
                    "items": [{"position": item["position"], "type": item["type"], "title": item["title"]} for item in final_items],
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
