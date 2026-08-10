"""Build the unpublished 4SW Week 6 evidence-synthesis Canvas module."""

import asyncio
import json
import sys

import httpx

import build_4sw_wk1 as common


COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/4sw/wk6"
MODULE_NAME = "4SW Wk6: Skills That Transfer and Mid-Year Evidence"
TRUCK_TITLE = "PRACTICE: Truck Evidence and Priority"
SKILLS_TITLE = "PRACTICE: Transferable Skills Evidence"
ORG_QUIZ_TITLE = "PRACTICE: Career Organization Type Check"
INTEGRITY_QUIZ_TITLE = "PRACTICE: Integrity and Accurate Records"
REFLECTION_TITLE = "DRAFT: Private Mid-Year Evidence Reflection"
LEGACY_REFLECTION_TITLE = REFLECTION_TITLE
REFLECTION_TITLE = "RECOVERY: Private Mid-Year Evidence Reflection"


CONTRACTS = {
    1: {
        "TOPIC": "Transferable Skills",
        "OBJECTIVE": "Students will separate observations from conclusions, choose a safe inspection priority using evidence, and explain how analytical reasoning transfers to another career task.",
        "TEKS": "d(4)(B)",
        "DOL": "Completed FYF pp. 154-155 priority and plan plus one clue-limit-safe-action and cross-career transfer response.",
        "I_CAN": "separate a clue from a conclusion, choose a safe priority, and show how analytical reasoning transfers to another career task.",
        "SHOW": "Complete FYF pp. 154-155, then write one clue-limit-safe-action and cross-career transfer response.",
    },
    2: {
        "TOPIC": "Transferable Skills",
        "OBJECTIVE": "Students will use specific job tasks to show how four skills transfer among six careers.",
        "TEKS": "d(4)(B)",
        "DOL": "Four transferable-skill comparisons, a three-example pattern claim, and an independent two-career transfer response.",
        "I_CAN": "use specific tasks to prove that a skill transfers among different careers.",
        "SHOW": "Complete four skill comparisons, a three-example claim, and one independent two-career transfer response.",
    },
    3: {
        "TOPIC": "Extended Learning",
        "OBJECTIVE": "Students will distinguish CTSOs, professional associations, a credentialing organization, and a government agency; explain how one realistic student opportunity supports career exploration and development.",
        "TEKS": "d(3)(F), d(3)(H)",
        "DOL": "Four-question practice Quiz and one Sam decision with an accurate type, benefit, access boundary, and career-development value.",
        "I_CAN": "tell what four organization types do and explain how one student opportunity supports career development.",
        "SHOW": "Complete the four-question practice Quiz and recommend one school-based opportunity now and one professional network to investigate later, using facts and an access boundary.",
    },
    4: {
        "TOPIC": "Professional Character",
        "OBJECTIVE": "Students will identify work ethic, integrity, dedication, and perseverance in four fictional workplace decisions and connect one trait to prior class evidence.",
        "TEKS": "d(4)(F)",
        "DOL": "Five-question practice Quiz, one justified workplace decision, and one personal class-artifact evidence audit.",
        "I_CAN": "identify four professional characteristics and connect one to a visible action in my class work.",
        "SHOW": "Complete the five-question practice Quiz, justify one workplace decision, and audit one prior class artifact.",
    },
    5: {
        "TOPIC": "Evidence Reflection",
        "OBJECTIVE": "Students will use fixed and personal evidence to explain one change in career thinking, prove two transferable skills, evaluate one professional association and its membership boundary, and set two supported next actions.",
        "TEKS": "d(4)(B), d(3)(H)",
        "DOL": "Teacher-assigned private four-part recovery reflection, self-score, and visible revision.",
        "I_CAN": "use evidence to explain a change, prove two skills, evaluate one professional association, and plan two next actions.",
        "SHOW": "When assigned for recovery or replacement, submit a private four-part reflection with a self-score and one visible revision.",
    },
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


QUIZZES = {
    ORG_QUIZ_TITLE: [
        {
            "name": "Q1 - CTSO",
            "prompt": "Which pair contains two career and technical student organizations?",
            "correct": "SkillsUSA and TSA",
            "wrong": ["ASE and FAA", "NSPE and FAA", "AOPA and ASE"],
            "yes": "Correct. Both are school-connected CTSOs.",
            "no": "SkillsUSA and TSA are the CTSOs in this evidence set.",
        },
        {"name": "Q2 - Credentialing", "prompt": "Which organization assesses and credentials automotive knowledge and experience?", "correct": "ASE", "wrong": ["FAA", "TSA", "NSPE"], "yes": "Correct. ASE is an independent nonprofit credentialing organization.", "no": "ASE develops automotive assessments and credentials; it is not a school club."},
        {"name": "Q3 - Government", "prompt": "Which organization is a federal government agency rather than a membership association?", "correct": "FAA", "wrong": ["AOPA", "NSPE", "SkillsUSA"], "yes": "Correct. The FAA is part of the U.S. Department of Transportation.", "no": "The FAA regulates aviation and is not an association a student joins."},
        {"name": "Q4 - Access", "prompt": "What is the strongest first step for a student interested in SkillsUSA?", "correct": "Ask a CTE teacher or counselor whether the school has a chapter and what access requires.", "wrong": ["Assume every campus has a free chapter.", "Register for an ASE professional test instead.", "Join the FAA."], "yes": "Correct. School access and local requirements must be verified.", "no": "A national organization page does not prove a particular campus chapter."},
        {"name": "Q5 - Sam decision", "type": "essay_question", "prompt": "Fictional Sam wants a school-based leadership and competition opportunity now and an aviation professional network to investigate later. Recommend one organization for now and one for later. Use one card fact for each, explain how the school opportunity supports career exploration or development, and name one access, eligibility, cost, or privacy question."},
    ],
    INTEGRITY_QUIZ_TITLE: [
        {"name": "Q1 - Pressure to sign", "prompt": "A worker is asked to sign an inspection they did not complete. What is the strongest action?", "correct": "Do not sign; record the incomplete status accurately and use the supervisor or authorized handoff route.", "wrong": ["Sign now and fix it later.", "Delete the record.", "Guess that the inspection passed."], "yes": "Correct. Integrity protects both the work and the record.", "no": "A signature must not claim work that was not completed."},
        {"name": "Q2 - Conflicting data", "prompt": "Two approved classroom measurements conflict. What should the team record?", "correct": "Both results, the conflict, and the approved next verification step", "wrong": ["Only the result that looks best", "The average as a guaranteed truth", "No result at all"], "yes": "Correct. Honest uncertainty is usable evidence.", "no": "Do not hide or relabel a conflicting measurement."},
        {"name": "Q3 - Perseverance", "prompt": "Which statement best describes perseverance?", "correct": "Continue through difficulty while keeping safety, quality, and authorization boundaries.", "wrong": ["Continue any task even when it becomes unsafe.", "Hide a mistake to finish on time.", "Never ask for help."], "yes": "Correct. Persistence does not erase professional boundaries.", "no": "Unsafe persistence is not professional perseverance."},
        {"name": "Q4 - Evidence", "prompt": "Which statement is personal evidence of work ethic in class?", "correct": "I completed every required evidence row, noticed one weak explanation, and revised it before submitting.", "wrong": ["I have good work ethic.", "My favorite career is automotive.", "I opened the website."], "yes": "Correct. The statement names visible action and revision.", "no": "A trait label or click is not evidence by itself."},
        {"name": "Q5 - Dedication", "prompt": "Which statement best shows dedication?", "correct": "I kept improving the required product because quality mattered, while still following the deadline and safety rules.", "wrong": ["I refused every revision because the first version was already finished.", "I continued an unsafe task because stopping would look weak.", "I hid the incomplete part so the product looked finished."], "yes": "Correct. Dedication is sustained commitment to quality and purpose within professional boundaries.", "no": "Dedication does not erase deadlines, safety, honesty, or revision."},
        {"name": "Q6 - Evidence audit", "type": "essay_question", "prompt": "Choose one fictional case and one prior class artifact. For the case, name the characteristic, trustworthy action, accurate record or handoff, and harm prevented. For the artifact, name one visible action that proves a professional characteristic and one honest revision still needed."},
    ],
}


async def upsert_quiz(client, title, questions):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    found = next((quiz for quiz in quizzes if quiz.get("title") == title), None)
    data = {
        "quiz[title]": title,
        "quiz[description]": "<p>Ungraded, unlimited-retry evidence check with immediate feedback.</p>",
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
            await common.api(client, "DELETE", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior['id']}")
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


async def upsert_recovery_assignment(client, description):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [
        entry
        for entry in assignments
        if entry.get("name") in {REFLECTION_TITLE, LEGACY_REFLECTION_TITLE}
    ]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one Week 6 recovery reflection; found {len(matches)}")
    if matches:
        found = matches[0]
    else:
        found = await common.upsert_assignment(
            client,
            REFLECTION_TITLE,
            description,
            ["online_upload", "online_text_entry", "media_recording"],
        )
    return await common.api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{found['id']}",
        data={
            "assignment[name]": REFLECTION_TITLE,
            "assignment[description]": description,
            "assignment[submission_types][]": ["online_upload", "online_text_entry", "media_recording"],
            "assignment[grading_type]": "not_graded",
            "assignment[points_possible]": "0",
            "assignment[published]": "false",
        },
    )


def image_tag(file_id, alt):
    return (
        f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" '
        'style="display:block;width:100%;max-width:700px;height:auto;margin:14px auto;border:1px solid #ddd" '
        f'data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'
    )


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        module = await ensure_module(client)
        support_path = "course files/CCR Materials/4SW/Wk6"
        support_folder = await common.ensure_folder(client, support_path)
        names = {
            "TRUCK": "4sw-wk6-truck-evidence-and-priority.pdf",
            "SKILLS": "4sw-wk6-transferable-skills-evidence.pdf",
            "ORGS": "4sw-wk6-career-organization-types.pdf",
            "INTEGRITY": "4sw-wk6-integrity-and-evidence-audit.pdf",
            "REFLECTION": "4sw-wk6-mid-year-evidence-reflection.pdf",
            "RUBRIC": "4sw-wk6-mid-year-evidence-rubric.pdf",
        }
        files = {
            key: await common.upload(client, ROOT / "docs/resources/worksheets" / name, support_path)
            for key, name in names.items()
        }
        visual_path = "course files/CCR Materials/4SW/Wk6/Day 1 Visuals"
        visual_folder = await common.ensure_folder(client, visual_path)
        visuals = {}
        for name in (
            "fyf-analytical-reasoning-tools.jpg",
            "fyf-truck-clue-sets.jpg",
            "fyf-truck-priority-and-plan.jpg",
        ):
            visuals[name] = await common.upload(client, ASSETS / "day1" / name, visual_path)

        quizzes = {title: await upsert_quiz(client, title, questions) for title, questions in QUIZZES.items()}
        truck = await common.upsert_assignment(
            client,
            TRUCK_TITLE,
            f'<p><strong>Workbook first:</strong> complete FYF pp. 154-155, then write the clue-limit-safe-action exit response. Use the <a href="/courses/{COURSE_ID}/files/{files["TRUCK"]["id"]}/preview">three-page fallback</a> only for no-workbook, enlarged, absence, or Canvas-annotation access. This is a fictional evidence task, not a real diagnosis or repair.</p>',
            ["student_annotation", "online_upload", "online_text_entry"],
            files["TRUCK"]["id"],
        )
        skills = await common.upsert_assignment(
            client,
            SKILLS_TITLE,
            f'<p>Use the six fixed career-task cards. Type the four labeled comparisons, three-example claim, and independent transfer response, or use the <a href="/courses/{COURSE_ID}/files/{files["SKILLS"]["id"]}/preview">four-page paper or enlarged fallback</a>. Task evidence matters more than the number of checked boxes.</p>',
            ["student_annotation", "online_upload", "online_text_entry"],
            files["SKILLS"]["id"],
        )
        reflection_description = (
            f'<p><strong>Open only for teacher-approved recovery or replacement evidence.</strong> This is not an automatic third Major or fourth Minor. '
            f'Use the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">student-visible rubric</a>. '
            'Submit the private four-part reflection by upload, text, approved private media, or paper.</p>'
        )
        reflection = await upsert_recovery_assignment(client, reflection_description)
        urls = {
            "truck": f"/courses/{COURSE_ID}/assignments/{truck['id']}",
            "skills": f"/courses/{COURSE_ID}/assignments/{skills['id']}",
            "orgs": f"/courses/{COURSE_ID}/quizzes/{quizzes[ORG_QUIZ_TITLE]['id']}",
            "integrity": f"/courses/{COURSE_ID}/quizzes/{quizzes[INTEGRITY_QUIZ_TITLE]['id']}",
            "reflection": f"/courses/{COURSE_ID}/assignments/{reflection['id']}",
        }
        media = {
            1: image_tag(visuals["fyf-analytical-reasoning-tools.jpg"]["id"], "Find Your Future Analytical Reasoning introduction and code-reader and dashboard-light tool limits")
            + image_tag(visuals["fyf-truck-clue-sets.jpg"]["id"], "Four fictional truck clue sets for oil, battery, temperature, and tire-pressure issues")
            + image_tag(visuals["fyf-truck-priority-and-plan.jpg"]["id"], "Find Your Future issue-priority scale and two-issue planning prompts; the repeated Issue 3 label at lower right should read Issue 4"),
            2: '''<div style="border:1px solid #bad4df;border-radius:10px;padding:14px 18px;margin:18px 0;background:#f8fbfc"><h3 style="margin-top:0;color:#1f617a">Six career-task cards</h3><ul><li><strong>Software developer:</strong> tests a change, explains an issue, and coordinates a release.</li><li><strong>Nurse:</strong> verifies supplied information, communicates a handoff, and works with a care team.</li><li><strong>Lawyer:</strong> reviews evidence, explains a position, and prepares with a legal team.</li><li><strong>Pilot:</strong> uses checklists, evaluates supplied flight information, and communicates with authorized personnel.</li><li><strong>Drone systems technician:</strong> tests a system, records results, and explains a revision.</li><li><strong>Automotive service technician:</strong> follows inspection steps, documents findings, and explains supported next steps.</li></ul><p><strong>Model:</strong> “They all need attention to detail” is only a claim. “A software developer checks a code change; an automotive technician follows an inspection checklist” gives visible task evidence.</p><p style="font-size:14px;color:#52616b">These cards are classroom examples, not complete job descriptions.</p></div>''',
            3: '''<div style="border:1px solid #bad4df;border-radius:10px;padding:14px 18px;margin:18px 0;background:#f8fbfc"><h3 style="margin-top:0;color:#1f617a">Read the organization cards</h3><p><strong>SkillsUSA: CTSO.</strong> Middle- and high-school participation runs through a school chapter or approved local plan. Ask a CTE teacher or counselor about local access. The national page does not prove a particular campus chapter or free activity.</p><p><strong>TSA: CTSO.</strong> Middle- and high-school STEM participation runs through a school-affiliated chapter and advisor. The national page does not prove a particular campus chapter, fee, or event.</p><p><strong>ASE: credentialing organization.</strong> ASE develops automotive assessments and credentials. Professional certification requires the applicable test and approved experience or substitution. ASE is not a school club.</p><p><strong>FAA: government agency.</strong> The FAA is part of the U.S. Department of Transportation. It regulates aviation and issues certificates in authorized contexts. It is not a membership association.</p><p><strong>NSPE: professional association.</strong> Current student membership requires qualifying full-time college, graduate, or formal pre-engineering transfer-program enrollment. It is a later professional network, not blanket middle-school membership.</p><p><strong>AOPA: professional association.</strong> AOPA currently advertises free high-school membership for U.S. residents ages 13-20. A student still follows family and district privacy rules before creating an account. AOPA does not issue FAA certificates.</p><p style="font-size:14px;color:#52616b">Official source pages checked August 10, 2026. The teacher guide includes direct links.</p></div>''',
            4: '''<div style="border:1px solid #bad4df;border-radius:10px;padding:14px 18px;margin:18px 0;background:#f8fbfc"><h3 style="margin-top:0;color:#1f617a">Four characteristics and four fictional cases</h3><ul><li><strong>Work ethic:</strong> reliable effort and responsibility.</li><li><strong>Integrity:</strong> honest action and records, even when no one is watching.</li><li><strong>Dedication:</strong> sustained commitment to quality and purpose.</li><li><strong>Perseverance:</strong> continuing through difficulty while keeping safety and quality boundaries.</li></ul><ol><li>A technician notices a blank checklist field after the item moved to the next station. A supervisor is available.</li><li>A team receives two conflicting approved classroom measurements. A teammate wants to report only the better result.</li><li>A worker reaches shift change with one observation not yet verified.</li><li>A worker is pressured to sign an inspection they did not complete.</li></ol><p><strong>Boundary:</strong> Perseverance never means continuing an unsafe or unauthorized task.</p></div>''',
            5: "",
        }
        link, step, flow = common.file_link, common.step, common.flow

        student = {
            1: {
                "TITLE": "Analytical Reasoning: What the Clues Support",
                "PURPOSE": "Separate supplied clues from conclusions and choose a safe inspection priority.",
                "TODAY": "<ul><li>read four fictional clue sets;</li><li>name broad system concerns;</li><li>rank inspection priority;</li><li>write safe next steps.</li></ul>",
                "READY": f'<p><strong>Workbook first:</strong> open FYF pp. 153-155. Use {link(files["TRUCK"]["id"], "the three-page no-workbook fallback")} or <a href="{urls["truck"]}">Canvas annotation</a> only when directed. The workbook repeats Issue 3; the tire-pressure box is Issue 4.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> clue = supplied fact · concern = broad system to inspect · conclusion = claim that still needs proof · priority = order for responding.</p><p><strong>Use this frame:</strong> The clue shows ___. It does not prove ___. The safe next step is ___ because ___. A ___ also uses analytical reasoning when the worker ___.</p></div>',
                "STEPS": step(1, "Keep the boundary", "<p>A light or code points toward a system; it does not prove a failed part, repair, or safe-to-drive decision.</p>")
                + step(2, "Complete four evidence rows", "<p>Use two clues, one broad concern, one unproved conclusion, and one evidence need per case.</p>")
                + step(3, "Rank priority", "<p>Rank quickest stop-and-inspect response. A lower rank does not mean safe to ignore.</p>")
                + step(4, "Write authorized next steps", "<p>Stop/protect, notify/hand off, and identify the evidence a trained person still needs. Do not prescribe a repair.</p>"),
                "EXIT": "<p>Correct the claim that a code already proves the broken part, then name one different career task that uses the same clue-to-conclusion reasoning.</p>",
                "DONE": "<ul><li>FYF pp. 154-155 complete;</li><li>four ranks;</li><li>two safe next-step plans;</li><li>one clue-limit-safe-action and cross-career transfer response.</li></ul>",
                "SUPPORT": "<p>clue = pista · conclusion = conclusión · inspect = inspeccionar · priority = prioridad. Read one clue set at a time and highlight only supplied facts.</p>",
                "FALLBACK": "<p>The three-page fallback and adjacent image descriptions are the complete independent route when the workbook is unavailable. Do not print it by default. No partner, open search, vehicle, or personal car knowledge is required.</p>",
            },
            2: {
                "TITLE": "Prove That a Skill Transfers",
                "PURPOSE": "Use specific tasks to show how four skills transfer among six careers.",
                "TODAY": "<ul><li>read six fixed career cards;</li><li>compare four skills;</li><li>build a three-example claim;</li><li>complete an independent transfer check.</li></ul>",
                "READY": f'<p><a href="{urls["skills"]}">Open the private Canvas response</a>. Keep {link(files["SKILLS"]["id"], "the four-page paper or enlarged fallback")} available without printing it for everyone.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> task = tarea · skill = habilidad · common = en común · setting = entorno.</p><p><strong>Use this frame:</strong> ___ and ___ both use ___ when they ___. The common behavior is ___. The technical setting changes ___ because ___.</p></div>',
                "STEPS": step(1, "Move from claim to proof", "<p>A skill label is not proof. Name the visible task where the worker uses it.</p>")
                + step(2, "Compare four skills", "<p>For each skill, use two careers, common behavior, and a technical-setting difference.</p>")
                + step(3, "Build a pattern claim", "<p>Use three task examples and one honest limit.</p>")
                + step(4, "Check independently", "<p>Choose two careers from different clusters and prove one transfer.</p>"),
                "EXIT": "<p>Name two careers, one transferable skill, one task in each, and the common behavior.</p>",
                "DONE": "<ul><li>four skill comparisons;</li><li>specific task evidence;</li><li>three-example claim;</li><li>independent transfer response.</li></ul>",
                "SUPPORT": "<p>task = tarea · skill = habilidad · common = en común · technical = técnico. Phrases are acceptable in evidence boxes.</p>",
                "FALLBACK": "<p>The four-page fallback includes the fixed cards and every response job. Do not print it by default. No 48-cell grid, partner, live research, or login is required.</p>",
            },
            3: {
                "TITLE": "Career Organizations: Type, Access, and Value",
                "PURPOSE": "Distinguish CTSOs and professional associations from credentialing and government organizations.",
                "TODAY": "<ul><li>learn four organization types;</li><li>read six dated cards;</li><li>recommend one now and one later opportunity;</li><li>repair inaccurate labels.</li></ul>",
                "READY": f'<p>Open the six dated cards in this guide and <a href="{urls["orgs"]}">the five-question practice Quiz</a>. Keep {link(files["ORGS"]["id"], "the three-page paper fallback")} available without printing it for everyone.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> chapter = capítulo local · membership = membresía · credential = credencial · agency = agencia.</p><p><strong>Use this frame:</strong> Sam should ask about ___ now because ___. This could support career development by ___. Later, Sam could investigate ___, but first Sam must verify ___.</p></div>',
                "STEPS": step(1, "Sort by main job", "<p>CTSO, professional association, credentialing organization, or government agency.</p>")
                + step(2, "Read access before benefits", "<p>Record who can access the named opportunity and what the source does not prove.</p>")
                + step(3, "Decide for Sam", "<p>Recommend a school-based opportunity now and a professional network to investigate later.</p>")
                + step(4, "Practice and decide", f'<p><a href="{urls["orgs"]}">Complete four feedback questions and the individual Sam decision</a>.</p>'),
                "EXIT": "<p>What makes Sam's now/later plan realistic instead of guaranteed?</p>",
                "DONE": "<ul><li>four feedback questions;</li><li>school-based organization, source fact, and career-development value;</li><li>later professional organization and source fact;</li><li>one access, eligibility, cost, or privacy question.</li></ul>",
                "SUPPORT": "<p>membership = membresía · student organization = organización estudiantil · credential = credencial · government agency = agencia gubernamental.</p>",
                "FALLBACK": "<p>The three-page fallback contains the same cards and questions. Do not print it by default. No dense public website, group jigsaw, public presentation, or personal membership is required.</p>",
            },
            4: {
                "TITLE": "Work Ethic and Integrity: Document the Decision",
                "PURPOSE": "Apply four professional characteristics to accurate actions and records.",
                "TODAY": "<ul><li>distinguish four characteristics;</li><li>solve four fictional cases;</li><li>audit one class artifact;</li><li>repair misconceptions.</li></ul>",
                "READY": f'<p>Open the four fictional cases in this guide and <a href="{urls["integrity"]}">the six-item practice Quiz</a> with five feedback questions and one evidence-audit response. Keep {link(files["INTEGRITY"]["id"], "the three-page paper fallback")} available without printing it for everyone.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> integrity = integridad · record = registro · verify = verificar · supervisor = supervisor.</p><p><strong>Use this frame:</strong> This case requires ___. The worker should ___ and record or report ___. This prevents ___ because ___.</p></div>',
                "STEPS": step(1, "Name the characteristic", "<p>Work ethic, integrity, dedication, or perseverance.</p>")
                + step(2, "Choose the trustworthy action", "<p>Name what the worker should do and what the record should say.</p>")
                + step(3, "Audit personal evidence", "<p>Use one class artifact, one visible action, one honest limitation, and one next step.</p>")
                + step(4, "Practice and audit", f'<p><a href="{urls["integrity"]}">Complete five feedback questions and the private evidence-audit response</a>.</p>'),
                "EXIT": "<p>Respond to pressure to sign an inspection that was not completed.</p>",
                "DONE": "<ul><li>five feedback questions;</li><li>one justified case decision;</li><li>accurate record or supervisor route;</li><li>personal evidence audit.</li></ul>",
                "SUPPORT": "<p>integrity = integridad · record = registro · verify = verificar · supervisor = supervisor. Employment history is not required.</p>",
                "FALLBACK": "<p>The three-page fallback contains the same cases and response jobs. Do not print it by default. H&amp;L is optional; no private Career Plan or screenshot is required.</p>",
            },
            5: {
                "TITLE": "Recovery: Private Mid-Year Evidence Reflection",
                "PURPOSE": "When your teacher assigns recovery or replacement evidence, use specific course evidence to show a change, two transferable skills, one professional-association decision, and two next actions.",
                "TODAY": "<ul><li>build an evidence strip;</li><li>complete four response jobs;</li><li>self-score and revise;</li><li>submit privately.</li></ul>",
                "READY": f'<p><strong>Open this task only when your teacher assigns it for recovery or replacement.</strong> Use the private Canvas response and {link(files["RUBRIC"]["id"], "the two-page rubric")}. Keep {link(files["REFLECTION"]["id"], "the four-page paper fallback")} available when needed.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> reflection = reflexión · evidence = evidencia · association = asociación · revision = revisión.</p><p><strong>Use this frame:</strong> At first, I thought ___. After ___, I now think ___. The evidence that mattered was ___ because ___. The professional association I would investigate is ___, but I still need to verify ___.</p></div>',
                "STEPS": step(1, "Gather bounded evidence", "<p>Use one earlier assumption, current direction, two class tasks, one accurate professional-association fact, and one membership question.</p>")
                + step(2, "Write four parts", "<p>Change in thinking; two skills; professional-association decision; two next actions.</p>")
                + step(3, "Self-score and revise", "<p>Revise the weakest criterion. Longer personal stories are not required.</p>")
                + step(4, "Submit privately", f'<p><a href="{urls["reflection"]}">Submit by upload, text, private media, or paper</a>.</p>'),
                "EXIT": "<p>Record three accurate labels, two evidence moves, and one revision.</p>",
                "DONE": "<ul><li>four reflection parts;</li><li>specific evidence labels;</li><li>two timed actions with support and backup;</li><li>visible revision;</li><li>private submission.</li></ul>",
                "SUPPORT": "<p>reflection = reflexión · evidence = evidencia · route = ruta · revision = revisión. Bullet points are allowed in Parts 2 and 4.</p>",
                "FALLBACK": "<p>The four-page paper route is complete when Canvas is unavailable. Use the generic evidence strip when earlier work is missing. No public sharing, profile screenshot, or partner disclosure is required.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Analytical Reasoning: What the Clues Support",
                "SUBTITLE": "50 minutes · TEKS d(4)(B)",
                "ALERT": "<strong>Fictional evidence task only.</strong> Students do not diagnose or repair a real vehicle, prescribe a part, or declare it safe to drive.",
                "PREP": f'<ul><li>Ask students to open FYF pp. 153-155.</li><li>Keep {link(files["TRUCK"]["id"], "the three-page fallback")} for no-workbook, enlarged, absence, or annotation access; do not print it by default.</li><li>Project the three FYF pages and name the repeated Issue 3 typo.</li><li>Model clue, concern, conclusion, and evidence need.</li></ul>',
                "EVIDENCE": "<p>Completed FYF pp. 154-155 priority and plan plus one clue-limit-safe-action and cross-career transfer response. Formative.</p>",
                "FLOW": flow("#5a2d91", "Clue or conclusion · 5", "Sort three statements.")
                + flow("#4a9d2f", "Tool limits · 7", "Light and code-reader boundaries.")
                + flow("#1f617a", "Four clue sets · 18", "Evidence before conclusion.")
                + flow("#e3ad19", "Priority and plan · 15", "Stop, notify, inspect.")
                + flow("#1f617a", "Exit · 5", "Clue, limit, safe action."),
                "MONITOR": "<p>Broad accepted concerns: lubrication/engine-temperature; electrical/charging; cooling/temperature; tire/steering. Strong top ranks use steam/very hot and tire pulling/soft evidence; oil plus heat can also be defended. A lower rank still requires service.</p>",
                "RESOURCES": "<p>Licensed FYF pp. 153-155 carry the default task. The fallback corrects the Issue 4 label and removes open repair research without replacing the workbook.</p>",
                "SUPPORT": "<p>Keep the point-of-use word bank and full frame visible. Read clue sets aloud, highlight supplied facts, and allow typing, dictation, annotation, or paper.</p>",
                "FALLBACK": "<p>No vehicle, partner, personal story, or site is required. The three delivery images total about 508 KB; the three-page fallback is the independent text route.</p>",
            },
            2: {
                "TITLE": "Prove That a Skill Transfers",
                "SUBTITLE": "50 minutes · TEKS d(4)(B)",
                "ALERT": "<strong>Task evidence, not box count.</strong> The former 48-cell grid was removed because it demanded cramped repetitive writing without improving the standard evidence.",
                "PREP": f'<ul><li>Post the fixed cards and private Canvas response.</li><li>Keep {link(files["SKILLS"]["id"], "the four-page fallback")} for paper or enlarged access; do not print it by default.</li><li>Model claim versus proof.</li></ul>',
                "EVIDENCE": "<p>Four skills compared across six careers, two task examples per skill, three-example pattern claim, and independent transfer. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "One skill plus one task.")
                + flow("#4a9d2f", "Evidence model · 8", "Claim versus proof.")
                + flow("#1f617a", "Compare · 25", "Four skills across six cards.")
                + flow("#e3ad19", "Pattern claim · 7", "Three tasks and one limit.")
                + flow("#1f617a", "Exit · 5", "Two-cluster transfer."),
                "MONITOR": "<p>Full evidence names the task, common behavior, and technical difference. Do not teach the false binary that soft skills matter more than technical skills in every hiring decision.</p>",
                "RESOURCES": "<p>The six fixed task cards are course-derived examples, not complete occupation descriptions. Live research is unnecessary.</p>",
                "SUPPORT": "<p>Keep the point-of-use word bank and full frame visible. Read one card and skill at a time. Accept phrases in comparison fields; require a complete final claim.</p>",
                "FALLBACK": "<p>Annotation, upload, text, and paper are equal. The four-page fallback is complete and should not be printed by default. No partner or login is required.</p>",
            },
            3: {
                "TITLE": "Career Organizations: Type, Access, and Value",
                "SUBTITLE": "50 minutes · TEKS d(3)(F), d(3)(H)",
                "ALERT": "<strong>Corrected organization types.</strong> FAA is government; ASE is credentialing; SkillsUSA/TSA are CTSOs; NSPE/AOPA are professional associations.",
                "PREP": f'<ul><li>Post the six dated cards and five-question practice Quiz.</li><li>Keep {link(files["ORGS"]["id"], "the three-page paper fallback")} available without default printing.</li><li>Open current official source pages only if extending the fixed cards.</li></ul>',
                "EVIDENCE": "<p>Four selected-response checks plus an individual Sam recommendation using two card facts, career-development value, and one access, eligibility, cost, or privacy question. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Membership, test, or rule?")
                + flow("#4a9d2f", "Four types · 10", "Main job and access.")
                + flow("#1f617a", "Six cards · 20", "Classify and preserve limits.")
                + flow("#e3ad19", "Decision · 10", "School opportunity now, network later.")
                + flow("#1f617a", "Exit · 5", "Repair FAA/ASE/SkillsUSA labels."),
                "MONITOR": "<p>SkillsUSA/TSA access depends on a school chapter or approved local plan. ASE does not prove universal professional certification. FAA is an agency. NSPE student eligibility is not blanket middle-school membership. AOPA currently advertises a free U.S. high-school category for ages 13-20, but account creation still follows family and district privacy rules.</p>",
                "RESOURCES": '<p><a href="https://www.skillsusa.org/join/how-to-join/">SkillsUSA How to Join</a> · <a href="https://tsaweb.org/membership/membership-faq">TSA Membership FAQ</a> · <a href="https://ase.com/about/">ASE About</a> · <a href="https://www.faa.gov/about">FAA About</a> · <a href="https://www.nspe.org/membership/types-membership/student-membership">NSPE Student Membership</a> · <a href="https://www.aopa.org/account/studentjoinform">AOPA High School Membership</a></p>',
                "SUPPORT": "<p>Keep the point-of-use word bank and full frame visible. Use the four-type chart and one card at a time. The practice Quiz gives immediate corrective feedback before the individual decision.</p>",
                "FALLBACK": "<p>The three-page fallback is the complete no-web route and should not be printed by default. No group jigsaw, public presentation, or personal membership data is required.</p>",
            },
            4: {
                "TITLE": "Work Ethic and Integrity: Document the Decision",
                "SUBTITLE": "50 minutes · TEKS d(4)(F)",
                "ALERT": "<strong>Accuracy before drama.</strong> Use fictional bounded cases; do not invent real repair, aviation, clinical, or inspection procedures.",
                "PREP": f'<ul><li>Post the four fictional cases and six-item practice Quiz: five feedback questions plus one evidence-audit response.</li><li>Keep {link(files["INTEGRITY"]["id"], "the three-page paper fallback")} available without default printing.</li><li>Prepare one school-artifact model.</li></ul>',
                "EVIDENCE": "<p>Five selected-response checks, one justified case decision, and one personal class-artifact evidence audit. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Hard work versus trustworthy work.")
                + flow("#4a9d2f", "Four traits · 10", "Definitions and boundaries.")
                + flow("#1f617a", "Four cases · 20", "Action, record, harm prevented.")
                + flow("#e3ad19", "Evidence audit · 10", "Visible class action and limitation.")
                + flow("#1f617a", "Exit · 5", "Pressure-to-sign decision."),
                "MONITOR": "<p>Integrity requires an accurate action and record, not only “tell the truth.” Perseverance never means continuing unsafe or unauthorized work. Employment history is not required.</p>",
                "RESOURCES": "<p>The CCE fictional cases are the complete source. H&amp;L career browse is optional and never graded.</p>",
                "SUPPORT": "<p>Keep the point-of-use word bank and full frame visible. Use characteristic/action/record/harm labels, oral rehearsal, and private response modes.</p>",
                "FALLBACK": "<p>The three-page fallback contains the same cases and response jobs and should not be printed by default. No screenshot, profile history, partner, or workplace experience is required.</p>",
            },
            5: {
                "TITLE": "Recovery: Private Mid-Year Evidence Reflection",
                "SUBTITLE": "50 minutes · TEKS d(4)(B), d(3)(H)",
                "ALERT": "<strong>Recovery or replacement only.</strong> This is not an automatic third Major or fourth Minor. Keep the Assignment unpublished, worth zero points, and not graded until a teacher assigns it for an approved recovery decision.",
                "PREP": f'<ul><li>Post {link(files["RUBRIC"]["id"], "the student-visible rubric")}.</li><li>Open the private recovery Assignment only when assigned.</li><li>Keep {link(files["REFLECTION"]["id"], "the four-page paper fallback")} available without default printing.</li><li>Prepare the generic evidence strip.</li></ul>',
                "EVIDENCE": "<p>Teacher-assigned private four-part recovery reflection, self-score, visible revision, and two supported actions. Zero points and not graded by default.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Before/now assumption.")
                + flow("#4a9d2f", "Evidence strip · 8", "Bounded facts and question.")
                + flow("#1f617a", "Reflection · 27", "Four separate response jobs.")
                + flow("#e3ad19", "Self-score · 5", "Revise weakest criterion.")
                + flow("#1f617a", "Private submit · 5", "Text, upload, media, or paper."),
                "MONITOR": "<p>Score only after an approved decision. The six weeks already has two mapped majors and three mapped minors. Do not score career preference, public speaking, profile history, platform access, accent, or grammar unless meaning is unclear.</p>",
                "RESOURCES": "<p>Days 1-4 evidence is the source base. Day 5 specifically requires a professional-association fact and membership boundary for d(3)(H). The generic strip prevents missing earlier artifacts from becoming a failure point.</p>",
                "SUPPORT": "<p>Keep the point-of-use word bank and complete frame visible. Use bullet points in Parts 2/4, speech-to-text, private media, teacher scribe, or paper. Every multi-sentence job has a full-width block.</p>",
                "FALLBACK": "<p>No sharing circle or partner disclosure is required. Canvas failure means paper or later upload without penalty.</p>",
            },
        }

        day_names = {
            1: "What the Clues Support",
            2: "Prove a Skill Transfers",
            3: "Career Organization Types",
            4: "Integrity and Accurate Records",
            5: "Recovery: Private Mid-Year Reflection",
        }
        extras = {
            1: ("Assignment", truck["id"], TRUCK_TITLE),
            2: ("Assignment", skills["id"], SKILLS_TITLE),
            3: ("Quiz", quizzes[ORG_QUIZ_TITLE]["id"], ORG_QUIZ_TITLE),
            4: ("Quiz", quizzes[INTEGRITY_QUIZ_TITLE]["id"], INTEGRITY_QUIZ_TITLE),
            5: ("Assignment", reflection["id"], REFLECTION_TITLE),
        }
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 4SW Wk6 Day {day} - {day_names[day]}"
            student_page = await common.upsert_page(
                client,
                student_title,
                common.render(
                    "4sw-wk6-student.html",
                    {"COURSE_ID": COURSE_ID, "DAY": day, "MEDIA": media[day], **CONTRACTS[day], **student[day]},
                ),
            )
            teacher_title = f"TEACHER: 4SW Wk6 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(
                client,
                teacher_title,
                common.render(
                    "4sw-wk6-teacher.html",
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

        def matches_item(entry, kind, key):
            return entry.get("type") == kind and (
                (kind == "SubHeader" and entry.get("id") == key)
                or (kind == "Page" and entry.get("page_url") == key)
                or (kind in ("Assignment", "Quiz") and entry.get("content_id") == key)
            )

        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        keep_ids = set()
        for kind, key, _title in order:
            match = next(
                (entry for entry in items if entry["id"] not in keep_ids and matches_item(entry, kind, key)),
                None,
            )
            if not match:
                raise RuntimeError(f"Missing expected module item: {kind} {key}")
            keep_ids.add(match["id"])
        for entry in items:
            if entry["id"] not in keep_ids:
                await common.api(
                    client,
                    "DELETE",
                    f"/courses/{COURSE_ID}/modules/{module['id']}/items/{entry['id']}",
                )
        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(entry for entry in items if matches_item(entry, kind, key))
            await common.api(
                client,
                "PUT",
                f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}",
                data={"module_item[position]": position, "module_item[title]": title},
            )
        final_items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        if len(final_items) != len(order):
            raise RuntimeError(f"Expected {len(order)} Week 6 module items; found {len(final_items)}")
        ordered_final = sorted(final_items, key=lambda entry: entry.get("position", 0))
        for position, ((kind, key, _title), entry) in enumerate(zip(order, ordered_final), 1):
            if entry.get("position") != position or not matches_item(entry, kind, key):
                raise RuntimeError(f"Week 6 module order mismatch at position {position}")
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
                        "truck": {
                            "id": truck["id"],
                            "published": truck.get("published"),
                            "submission_types": truck.get("submission_types"),
                            "annotatable_attachment_id": truck.get("annotatable_attachment_id"),
                        },
                        "skills": {
                            "id": skills["id"],
                            "published": skills.get("published"),
                            "submission_types": skills.get("submission_types"),
                            "annotatable_attachment_id": skills.get("annotatable_attachment_id"),
                        },
                        "reflection": {
                            "id": reflection["id"],
                            "published": reflection.get("published"),
                            "submission_types": reflection.get("submission_types"),
                            "grading_type": reflection.get("grading_type"),
                        },
                    },
                    "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
                    "visual_folder": {"id": visual_folder["id"], "locked": visual_folder["locked"]},
                    "files": {key: value["id"] for key, value in files.items()},
                    "visuals": {key: value["id"] for key, value in visuals.items()},
                    "pages": {
                        str(day): {
                            kind: {"url": value["url"], "published": value["published"]}
                            for kind, value in pair.items()
                        }
                        for day, pair in pages.items()
                    },
                    "items": [
                        {"position": item["position"], "type": item["type"], "title": item["title"]}
                        for item in final_items
                    ],
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
