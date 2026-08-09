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
        (
            "Q1 - CTSO",
            "Which pair contains two career and technical student organizations?",
            "SkillsUSA and TSA",
            ["ASE and FAA", "NSPE and FAA", "AOPA and ASE"],
            "Correct. Both are school-connected CTSOs.",
            "SkillsUSA and TSA are the CTSOs in this evidence set.",
        ),
        (
            "Q2 - Credentialing",
            "Which organization assesses and credentials automotive knowledge and experience?",
            "ASE",
            ["FAA", "TSA", "NSPE"],
            "Correct. ASE is an independent nonprofit credentialing organization.",
            "ASE develops automotive assessments and credentials; it is not a school club.",
        ),
        (
            "Q3 - Government",
            "Which organization is a federal government agency rather than a membership association?",
            "FAA",
            ["AOPA", "NSPE", "SkillsUSA"],
            "Correct. The FAA is part of the U.S. Department of Transportation.",
            "The FAA regulates aviation and is not an association a student joins.",
        ),
        (
            "Q4 - Access",
            "What is the strongest first step for a student interested in SkillsUSA?",
            "Ask a CTE teacher or counselor whether the school has a chapter and what access requires.",
            ["Assume every campus has a free chapter.", "Register for an ASE professional test instead.", "Join the FAA."],
            "Correct. School access and local requirements must be verified.",
            "A national organization page does not prove a particular campus chapter.",
        ),
    ],
    INTEGRITY_QUIZ_TITLE: [
        (
            "Q1 - Pressure to sign",
            "A worker is asked to sign an inspection they did not complete. What is the strongest action?",
            "Do not sign; record the incomplete status accurately and use the supervisor or authorized handoff route.",
            ["Sign now and fix it later.", "Delete the record.", "Guess that the inspection passed."],
            "Correct. Integrity protects both the work and the record.",
            "A signature must not claim work that was not completed.",
        ),
        (
            "Q2 - Conflicting data",
            "Two approved classroom measurements conflict. What should the team record?",
            "Both results, the conflict, and the approved next verification step",
            ["Only the result that looks best", "The average as a guaranteed truth", "No result at all"],
            "Correct. Honest uncertainty is usable evidence.",
            "Do not hide or relabel a conflicting measurement.",
        ),
        (
            "Q3 - Perseverance",
            "Which statement best describes perseverance?",
            "Continue through difficulty while keeping safety, quality, and authorization boundaries.",
            ["Continue any task even when it becomes unsafe.", "Hide a mistake to finish on time.", "Never ask for help."],
            "Correct. Persistence does not erase professional boundaries.",
            "Unsafe persistence is not professional perseverance.",
        ),
        (
            "Q4 - Evidence",
            "Which statement is personal evidence of work ethic in class?",
            "I completed every required evidence row, noticed one weak explanation, and revised it before submitting.",
            ["I have good work ethic.", "My favorite career is automotive.", "I opened the website."],
            "Correct. The statement names visible action and revision.",
            "A trait label or click is not evidence by itself.",
        ),
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
    for position, (name, prompt, correct, wrong, yes, no) in enumerate(questions, 1):
        prior = next((question for question in existing if question.get("question_name") == name), None)
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
        path = (
            f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior['id']}"
            if prior
            else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        )
        await common.api(client, "PUT" if prior else "POST", path, json=payload)
    return await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


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
            "<p>Annotate or upload the fictional Truck Evidence packet, type a labeled response, or use paper. This is an evidence-boundary task, not a real diagnosis or repair.</p>",
            ["student_annotation", "online_upload", "online_text_entry"],
            files["TRUCK"]["id"],
        )
        skills = await common.upsert_assignment(
            client,
            SKILLS_TITLE,
            "<p>Annotate or upload the Transferable Skills packet, type the four labeled comparisons, or use paper. Task evidence matters more than the number of checked boxes.</p>",
            ["student_annotation", "online_upload", "online_text_entry"],
            files["SKILLS"]["id"],
        )
        reflection = await common.upsert_assignment(
            client,
            REFLECTION_TITLE,
            "<p>Submit the private Mid-Year Evidence Reflection by upload, text, media, or paper. Keep unpublished and ungraded because the 4SW map already contains three minors and two majors.</p>",
            ["online_upload", "online_text_entry", "media_recording"],
        )
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
            2: "",
            3: "",
            4: "",
            5: "",
        }
        link, step, flow = common.file_link, common.step, common.flow

        student = {
            1: {
                "TITLE": "Analytical Reasoning: What the Clues Support",
                "PURPOSE": "Separate supplied clues from conclusions and choose a safe inspection priority.",
                "TODAY": "<ul><li>read four fictional clue sets;</li><li>name broad system concerns;</li><li>rank inspection priority;</li><li>write safe next steps.</li></ul>",
                "READY": f'<p>Open {link(files["TRUCK"]["id"], "the five-page Truck Evidence packet")} or <a href="{urls["truck"]}">the Canvas annotation activity</a>. The workbook image repeats Issue 3; the tire-pressure box is Issue 4.</p>',
                "STEPS": step(1, "Keep the boundary", "<p>A light or code points toward a system; it does not prove a failed part, repair, or safe-to-drive decision.</p>")
                + step(2, "Complete four evidence rows", "<p>Use two clues, one broad concern, one unproved conclusion, and one evidence need per case.</p>")
                + step(3, "Rank priority", "<p>Rank quickest stop-and-inspect response. A lower rank does not mean safe to ignore.</p>")
                + step(4, "Write authorized next steps", "<p>Stop/protect, notify/hand off, and identify the evidence a trained person still needs. Do not prescribe a repair.</p>"),
                "EXIT": "<p>Correct the claim that a code already proves the broken part and lets the team skip inspection.</p>",
                "DONE": "<ul><li>four evidence rows;</li><li>four ranks;</li><li>two safe next-step plans;</li><li>one clue-limit-action exit response.</li></ul>",
                "SUPPORT": "<p>clue = pista · conclusion = conclusión · inspect = inspeccionar · priority = prioridad. The packet repeats every clue in text.</p>",
                "FALLBACK": "<p>The packet and adjacent image descriptions are the complete independent route. No partner, open search, vehicle, or personal car knowledge is required.</p>",
            },
            2: {
                "TITLE": "Prove That a Skill Transfers",
                "PURPOSE": "Use specific tasks to show how four skills transfer among six careers.",
                "TODAY": "<ul><li>read six fixed career cards;</li><li>compare four skills;</li><li>build a three-example claim;</li><li>complete an independent transfer check.</li></ul>",
                "READY": f'<p>Open {link(files["SKILLS"]["id"], "the seven-page Transferable Skills packet")} or <a href="{urls["skills"]}">the Canvas annotation activity</a>.</p>',
                "STEPS": step(1, "Move from claim to proof", "<p>A skill label is not proof. Name the visible task where the worker uses it.</p>")
                + step(2, "Compare four skills", "<p>For each skill, use two careers, common behavior, and a technical-setting difference.</p>")
                + step(3, "Build a pattern claim", "<p>Use three task examples and one honest limit.</p>")
                + step(4, "Check independently", "<p>Choose two careers from different clusters and prove one transfer.</p>"),
                "EXIT": "<p>Name two careers, one transferable skill, one task in each, and the common behavior.</p>",
                "DONE": "<ul><li>four skill comparisons;</li><li>specific task evidence;</li><li>three-example claim;</li><li>independent transfer response.</li></ul>",
                "SUPPORT": "<p>task = tarea · skill = habilidad · common = en común · technical = técnico. Phrases are acceptable in evidence boxes.</p>",
                "FALLBACK": "<p>The fixed cards replace live career research. No 48-cell grid, partner, or login is required.</p>",
            },
            3: {
                "TITLE": "Career Organizations: Type, Access, and Value",
                "PURPOSE": "Distinguish CTSOs and professional associations from credentialing and government organizations.",
                "TODAY": "<ul><li>learn four organization types;</li><li>read six dated cards;</li><li>recommend one now and one later opportunity;</li><li>repair inaccurate labels.</li></ul>",
                "READY": f'<p>Open {link(files["ORGS"]["id"], "the five-page Career Organization packet")}.</p>',
                "STEPS": step(1, "Sort by main job", "<p>CTSO, professional association, credentialing organization, or government agency.</p>")
                + step(2, "Read access before benefits", "<p>Record who can access the named opportunity and what the source does not prove.</p>")
                + step(3, "Decide for Sam", "<p>Recommend a school-based opportunity now and a professional network to investigate later.</p>")
                + step(4, "Practice and repair", f'<p><a href="{urls["orgs"]}">Complete the retryable organization-type check</a>, then correct the three-label exit claim.</p>'),
                "EXIT": "<p>Correct the types and access for FAA, ASE, and SkillsUSA.</p>",
                "DONE": "<ul><li>six classified cards;</li><li>benefit/function and access boundary;</li><li>now/later decision;</li><li>practice feedback reviewed.</li></ul>",
                "SUPPORT": "<p>membership = membresía · student organization = organización estudiantil · credential = credencial · government agency = agencia gubernamental.</p>",
                "FALLBACK": "<p>The dated cards are the full route. No dense public website, group jigsaw, public presentation, or personal membership is required.</p>",
            },
            4: {
                "TITLE": "Work Ethic and Integrity: Document the Decision",
                "PURPOSE": "Apply four professional characteristics to accurate actions and records.",
                "TODAY": "<ul><li>distinguish four characteristics;</li><li>solve four fictional cases;</li><li>audit one class artifact;</li><li>repair misconceptions.</li></ul>",
                "READY": f'<p>Open {link(files["INTEGRITY"]["id"], "the seven-page Integrity and Evidence Audit")}.</p>',
                "STEPS": step(1, "Name the characteristic", "<p>Work ethic, integrity, dedication, or perseverance.</p>")
                + step(2, "Choose the trustworthy action", "<p>Name what the worker should do and what the record should say.</p>")
                + step(3, "Audit personal evidence", "<p>Use one class artifact, one visible action, one honest limitation, and one next step.</p>")
                + step(4, "Practice and repair", f'<p><a href="{urls["integrity"]}">Complete the retryable integrity check</a>, then answer the independent case.</p>'),
                "EXIT": "<p>Respond to pressure to sign an inspection that was not completed.</p>",
                "DONE": "<ul><li>four case decisions;</li><li>accurate record/supervisor routes;</li><li>personal evidence audit;</li><li>practice feedback reviewed.</li></ul>",
                "SUPPORT": "<p>integrity = integridad · record = registro · verify = verificar · supervisor = supervisor. Employment history is not required.</p>",
                "FALLBACK": "<p>All cases are fictional and independent. H&amp;L is optional; no private Career Plan or screenshot is required.</p>",
            },
            5: {
                "TITLE": "Private Mid-Year Evidence Reflection",
                "PURPOSE": "Use evidence to explain one change, prove two skills, evaluate one opportunity, and plan two next actions.",
                "TODAY": "<ul><li>build an evidence strip;</li><li>complete four response jobs;</li><li>self-score and revise;</li><li>submit privately.</li></ul>",
                "READY": f'<p>Open {link(files["REFLECTION"]["id"], "the five-page reflection")} and {link(files["RUBRIC"]["id"], "the two-page rubric")}.</p>',
                "STEPS": step(1, "Gather bounded evidence", "<p>Use one earlier assumption, current direction, two class tasks, one accurate organization/route fact, and one question.</p>")
                + step(2, "Write four parts", "<p>Change in thinking; two skills; organization/route decision; two next actions.</p>")
                + step(3, "Self-score and revise", "<p>Revise the weakest criterion. Longer personal stories are not required.</p>")
                + step(4, "Submit privately", f'<p><a href="{urls["reflection"]}">Submit by upload, text, private media, or paper</a>.</p>'),
                "EXIT": "<p>Record three accurate labels, two evidence moves, and one revision.</p>",
                "DONE": "<ul><li>four reflection parts;</li><li>specific evidence labels;</li><li>two timed actions with support and backup;</li><li>visible revision;</li><li>private submission.</li></ul>",
                "SUPPORT": "<p>reflection = reflexión · evidence = evidencia · route = ruta · revision = revisión. Bullet points are allowed in Parts 2 and 4.</p>",
                "FALLBACK": "<p>Use the generic evidence strip when earlier work is missing. No public sharing, profile screenshot, or partner disclosure is required.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Analytical Reasoning: What the Clues Support",
                "SUBTITLE": "50 minutes · TEKS d(4)(B)",
                "ALERT": "<strong>Fictional evidence task only.</strong> Students do not diagnose or repair a real vehicle, prescribe a part, or declare it safe to drive.",
                "PREP": f'<ul><li>Post {link(files["TRUCK"]["id"], "the Truck Evidence packet")} and annotation activity.</li><li>Project the three FYF pages and name the repeated Issue 3 typo.</li><li>Model clue, concern, conclusion, and evidence need.</li></ul>',
                "EVIDENCE": "<p>Four bounded evidence rows, four ranks, two authorized next-step plans, and one transfer response. Formative.</p>",
                "FLOW": flow("#5a2d91", "Clue or conclusion · 5", "Sort three statements.")
                + flow("#4a9d2f", "Tool limits · 7", "Light and code-reader boundaries.")
                + flow("#1f617a", "Four clue sets · 18", "Evidence before conclusion.")
                + flow("#e3ad19", "Priority and plan · 15", "Stop, notify, inspect.")
                + flow("#1f617a", "Exit · 5", "Clue, limit, safe action."),
                "MONITOR": "<p>Broad accepted concerns: lubrication/engine-temperature; electrical/charging; cooling/temperature; tire/steering. Strong top ranks use steam/very hot and tire pulling/soft evidence; oil plus heat can also be defended. A lower rank still requires service.</p>",
                "RESOURCES": "<p>Licensed FYF pp. 153-155 are embedded. The CCE packet corrects the Issue 4 label and removes open repair research.</p>",
                "SUPPORT": "<p>Read clue sets aloud, highlight supplied facts, and allow typing, dictation, annotation, or paper. Every multi-sentence job has its own space.</p>",
                "FALLBACK": "<p>No vehicle, partner, personal story, or site is required. The three delivery images total about 508 KB; the packet is the independent text route.</p>",
            },
            2: {
                "TITLE": "Prove That a Skill Transfers",
                "SUBTITLE": "50 minutes · TEKS d(4)(B)",
                "ALERT": "<strong>Task evidence, not box count.</strong> The former 48-cell grid was removed because it demanded cramped repetitive writing without improving the standard evidence.",
                "PREP": f'<ul><li>Post {link(files["SKILLS"]["id"], "the fixed-card packet")} and annotation activity.</li><li>Model claim versus proof.</li></ul>',
                "EVIDENCE": "<p>Four skills compared across six careers, two task examples per skill, three-example pattern claim, and independent transfer. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "One skill plus one task.")
                + flow("#4a9d2f", "Evidence model · 8", "Claim versus proof.")
                + flow("#1f617a", "Compare · 25", "Four skills across six cards.")
                + flow("#e3ad19", "Pattern claim · 7", "Three tasks and one limit.")
                + flow("#1f617a", "Exit · 5", "Two-cluster transfer."),
                "MONITOR": "<p>Full evidence names the task, common behavior, and technical difference. Do not teach the false binary that soft skills matter more than technical skills in every hiring decision.</p>",
                "RESOURCES": "<p>The six fixed task cards are course-derived examples, not complete occupation descriptions. Live research is unnecessary.</p>",
                "SUPPORT": "<p>Read one card and skill at a time. Accept phrases in evidence fields; require a complete final claim. Each skill owns a full page.</p>",
                "FALLBACK": "<p>Annotation, upload, text, and paper are equal. No partner or login is required.</p>",
            },
            3: {
                "TITLE": "Career Organizations: Type, Access, and Value",
                "SUBTITLE": "50 minutes · TEKS d(3)(F), d(3)(H)",
                "ALERT": "<strong>Corrected organization types.</strong> FAA is government; ASE is credentialing; SkillsUSA/TSA are CTSOs; NSPE/AOPA are professional associations.",
                "PREP": f'<ul><li>Post {link(files["ORGS"]["id"], "the six-card packet")} and practice Quiz.</li><li>Open current official source pages only if extending the fixed cards.</li></ul>',
                "EVIDENCE": "<p>Six classifications, access boundaries, one now/later recommendation, and corrected exit matrix. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Membership, test, or rule?")
                + flow("#4a9d2f", "Four types · 10", "Main job and access.")
                + flow("#1f617a", "Six cards · 20", "Classify and preserve limits.")
                + flow("#e3ad19", "Decision · 10", "School opportunity now, network later.")
                + flow("#1f617a", "Exit · 5", "Repair FAA/ASE/SkillsUSA labels."),
                "MONITOR": "<p>SkillsUSA/TSA access depends on a chapter/advisor. ASE does not prove universal professional certification. FAA cannot be joined as an association. NSPE student eligibility is not a blanket middle-school invitation. AOPA category eligibility and cost must be checked.</p>",
                "RESOURCES": '<p><a href="https://www.skillsusa.org/join/how-to-join/">SkillsUSA join</a> · <a href="https://tsaweb.org/docs/default-source/default-document-library/tsa-facts.pdf">TSA facts</a> · <a href="https://ase.com/about/">ASE About</a> · <a href="https://www.faa.gov/about">FAA About</a> · <a href="https://www.nspe.org/membership/types-membership/student-membership">NSPE students</a> · <a href="https://aopa.org/membership">AOPA membership</a></p>',
                "SUPPORT": "<p>Use the four-type chart and one card at a time. The practice Quiz gives immediate corrective feedback before the independent exit.</p>",
                "FALLBACK": "<p>The packet is the complete no-web route. No group jigsaw, public presentation, or personal membership data is required.</p>",
            },
            4: {
                "TITLE": "Work Ethic and Integrity: Document the Decision",
                "SUBTITLE": "50 minutes · TEKS d(4)(F)",
                "ALERT": "<strong>Accuracy before drama.</strong> Use fictional bounded cases; do not invent real repair, aviation, clinical, or inspection procedures.",
                "PREP": f'<ul><li>Post {link(files["INTEGRITY"]["id"], "the case packet")} and practice Quiz.</li><li>Prepare one school-artifact model.</li></ul>',
                "EVIDENCE": "<p>Four case decisions, accurate record/supervisor routes, one personal class-artifact audit, and independent exit. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Hard work versus trustworthy work.")
                + flow("#4a9d2f", "Four traits · 10", "Definitions and boundaries.")
                + flow("#1f617a", "Four cases · 20", "Action, record, harm prevented.")
                + flow("#e3ad19", "Evidence audit · 10", "Visible class action and limitation.")
                + flow("#1f617a", "Exit · 5", "Pressure-to-sign decision."),
                "MONITOR": "<p>Integrity requires an accurate action and record, not only “tell the truth.” Perseverance never means continuing unsafe or unauthorized work. Employment history is not required.</p>",
                "RESOURCES": "<p>The CCE fictional cases are the complete source. H&amp;L career browse is optional and never graded.</p>",
                "SUPPORT": "<p>Use characteristic/action/record/harm labels, oral rehearsal, and private response modes. Each case owns a full page.</p>",
                "FALLBACK": "<p>No screenshot, profile history, partner, or workplace experience is required.</p>",
            },
            5: {
                "TITLE": "Private Mid-Year Evidence Reflection",
                "SUBTITLE": "50 minutes · TEKS d(4)(B), d(3)(H)",
                "ALERT": "<strong>Portfolio synthesis, not an automatic third major.</strong> Keep unpublished and ungraded because the 4SW map already contains three minors and two majors.",
                "PREP": f'<ul><li>Post {link(files["REFLECTION"]["id"], "the reflection")} and {link(files["RUBRIC"]["id"], "the rubric")}.</li><li>Open the private Assignment.</li><li>Prepare the generic evidence strip.</li></ul>',
                "EVIDENCE": "<p>Four-part private reflection, self-score, visible revision, and two supported actions. Portfolio synthesis or approved recovery/replacement evidence.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Before/now assumption.")
                + flow("#4a9d2f", "Evidence strip · 8", "Bounded facts and question.")
                + flow("#1f617a", "Reflection · 27", "Four separate response jobs.")
                + flow("#e3ad19", "Self-score · 5", "Revise weakest criterion.")
                + flow("#1f617a", "Private submit · 5", "Text, upload, media, or paper."),
                "MONITOR": "<p>Score only after an approved decision. The six weeks already has two mapped majors and three mapped minors. Do not score career preference, public speaking, profile history, platform access, accent, or grammar unless meaning is unclear.</p>",
                "RESOURCES": "<p>Days 1-4 packets are the source base. The generic strip prevents missing earlier artifacts from becoming a failure point.</p>",
                "SUPPORT": "<p>Use sentence frames, bullet points in Parts 2/4, speech-to-text, private media, teacher scribe, or paper. Every multi-sentence job has a full page or full-width block.</p>",
                "FALLBACK": "<p>No sharing circle or partner disclosure is required. Canvas failure means paper or later upload without penalty.</p>",
            },
        }

        day_names = {
            1: "What the Clues Support",
            2: "Prove a Skill Transfers",
            3: "Career Organization Types",
            4: "Integrity and Accurate Records",
            5: "Private Mid-Year Reflection",
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
                    {"COURSE_ID": COURSE_ID, "DAY": day, "MEDIA": media[day], **student[day]},
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
