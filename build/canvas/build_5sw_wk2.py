"""Build the unpublished 5SW Week 2 Civil Engineering evidence module."""

import asyncio
import json
import sys

import httpx

import build_5sw_wk1 as prior


common = prior.common
COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/5sw/wk2"
MODULE_NAME = "5SW Wk2: Civil Engineering — Systems, Evidence, and Design"

SYSTEMS_TITLE = "PRACTICE: Civil Engineering and Systems Evidence"
QUIZ_TITLE = "PRACTICE: Assessment and Emerging Work Evidence Check"
QUIZ_ALIASES = ("MINOR 2: Assessment and Emerging Work Evidence Check",)
ASSESSMENT_TITLE = "MINOR 2: Assessment and Emerging-Specialty Evidence"
DESIGN_TITLE = "PRACTICE: Bridge Design Evidence"
TEST_TITLE = "PRACTICE: Bridge Test and Redesign Evidence"
PORTFOLIO_TITLE = "FORMATIVE: Civil Engineering Evidence Portfolio"


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    found = next((module for module in modules if module["name"] == MODULE_NAME), None)
    data = {"module[published]": "false"}
    if found:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data=data)
    data["module[name]"] = MODULE_NAME
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


QUESTIONS = [
    (
        "Q1 - PSAT 8/9 boundary",
        "Which statement stays within the current PSAT 8/9 evidence?",
        "A school or district may administer it in Grade 8 or 9, and its scores are not sent to colleges.",
        ["Every student takes it in Grade 9.", "It is a college-admission score.", "It automatically enters every student in National Merit."],
        "Correct. The local administration schedule still needs district verification.",
        "Do not turn a possible Grade 8 or 9 administration into a universal schedule or admissions claim.",
    ),
    (
        "Q2 - ACT science boundary",
        "Which statement is current for the enhanced ACT?",
        "The Composite uses English, math, and reading; science availability can vary by administration.",
        ["Science always determines the Composite.", "The ACT is the only assessment colleges may consider.", "A science score guarantees engineering admission."],
        "Correct. Institution, program, and scholarship policies must be checked for the student's cycle.",
        "ACT science is no longer a stable universal contrast with the SAT.",
    ),
    (
        "Q3 - TSIA2 boundary",
        "Which statement accurately describes TSIA2?",
        "It supports readiness and placement decisions for entering non-exempt students; exemptions and dual-credit rules must be verified.",
        ["Every Texas college student must take it with no exemptions.", "It is a national engineering license exam.", "One score guarantees college admission."],
        "Correct. The next step is checking the current authorized rule for the student's situation.",
        "Texas has exemptions and context-specific rules; do not present TSIA2 as universal with no exceptions.",
    ),
    (
        "Q4 - emerging evidence",
        "What makes the strongest claim that an engineering specialty is emerging or Bright Outlook?",
        "A named occupation, dated source, changing need or technology, and a stated evidence limitation.",
        ["A futuristic-sounding job title by itself.", "An unlabeled DFW salary guess.", "A social-media post with no occupation code."],
        "Correct. Transportation Engineers and Water/Wastewater Engineers are recognized O*NET specialties under Civil Engineers.",
        "The judgment needs a sourceable occupation and a reason the evidence could change.",
    ),
]


async def upsert_quiz(client):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    found = next(
        (
            quiz
            for quiz in quizzes
            if quiz.get("title") == QUIZ_TITLE or quiz.get("title") in QUIZ_ALIASES
        ),
        None,
    )
    data = {
        "quiz[title]": QUIZ_TITLE,
        "quiz[description]": "<p>Ungraded, unlimited-retry practice. Use the feedback to repair assessment-impact and emerging-work claims.</p>",
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
        prior_question = next((question for question in existing if question.get("question_name") == name), None)
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
            f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior_question['id']}"
            if prior_question
            else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        )
        await common.api(client, "PUT" if prior_question else "POST", path, json=payload)
    return await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")

    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        module = await ensure_module(client)
        support_path = "course files/CCR Materials/5SW/Wk2"
        support_folder = await common.ensure_folder(client, support_path)
        worksheet_names = {
            "CAREER": "5sw-wk2-civil-engineer-and-systems-evidence.pdf",
            "ASSESS": "5sw-wk2-assessment-and-emerging-specialty.pdf",
            "DESIGN": "5sw-wk2-bridge-design-options.pdf",
            "TEST": "5sw-wk2-bridge-test-and-redesign.pdf",
            "SYNTHESIS": "5sw-wk2-engineering-synthesis.pdf",
            "RUBRIC": "5sw-wk2-assessment-emerging-rubric.pdf",
            "PORTFOLIO_RUBRIC": "5sw-wk2-engineering-evidence-rubric.pdf",
        }
        files = {
            key: await common.upload(client, ROOT / "docs/resources/worksheets" / name, support_path)
            for key, name in worksheet_names.items()
        }

        visual_files = {}
        for day, names in {
            1: [
                ("cluster", "fyf-p103-engineering-opener.jpg"),
                ("systems", "fyf-p174-systems-thinking.jpg"),
                ("kitchen", "fyf-p175-kitchen-plan.jpg"),
            ],
            5: [
                ("mars", "fyf-p106-mission-to-mars.jpg"),
                ("rover", "fyf-p107-rover-design.jpg"),
            ],
        }.items():
            folder_path = f"course files/CCR Materials/5SW/Wk2/Day {day} Visuals"
            await common.ensure_folder(client, folder_path)
            for key, name in names:
                visual_files[key] = await common.upload(client, ASSETS / f"day{day}" / name, folder_path)

        quiz = await upsert_quiz(client)
        assessment = await common.upsert_assignment(
            client,
            ASSESSMENT_TITLE,
            "<p>Submit the assessment-impact decision and two-specialty comparison by Canvas annotation, upload, typed labeled response, or paper. Use the student-visible 16-point rubric; bridge fabrication and team ranking are not part of this grade.</p>",
            ["student_annotation", "online_upload", "online_text_entry"],
            files["ASSESS"]["id"],
        )
        systems = await common.upsert_assignment(
            client,
            SYSTEMS_TITLE,
            "<p>Annotate or upload the fixed civil-engineering evidence and systems plan, type labeled responses, or use paper.</p>",
            ["student_annotation", "online_upload", "online_text_entry"],
            files["CAREER"]["id"],
        )
        design = await common.upsert_assignment(
            client,
            DESIGN_TITLE,
            "<p>Submit two bridge options with top and side views, critique, choice, and an individual career-role explanation.</p>",
            ["student_annotation", "online_upload", "online_text_entry"],
            files["DESIGN"]["id"],
        )
        test = await common.upsert_assignment(
            client,
            TEST_TITLE,
            "<p>Use the controlled physical route or equal fixed dataset, then submit an individual failure analysis and redesign.</p>",
            ["student_annotation", "online_upload", "online_text_entry"],
            files["TEST"]["id"],
        )
        portfolio = await common.upsert_assignment(
            client,
            PORTFOLIO_TITLE,
            "<p>Submit the private Civil Engineering Evidence Portfolio by upload, text, media recording, or paper. Keep unpublished and ungraded until the Major assignment group and 40/60 weighting are verified.</p>",
            ["online_upload", "online_text_entry", "media_recording"],
        )

        urls = {
            "systems": f"/courses/{COURSE_ID}/assignments/{systems['id']}",
            "quiz": f"/courses/{COURSE_ID}/quizzes/{quiz['id']}",
            "assessment": f"/courses/{COURSE_ID}/assignments/{assessment['id']}",
            "design": f"/courses/{COURSE_ID}/assignments/{design['id']}",
            "test": f"/courses/{COURSE_ID}/assignments/{test['id']}",
            "portfolio": f"/courses/{COURSE_ID}/assignments/{portfolio['id']}",
        }
        link, step, flow = common.file_link, common.step, common.flow
        media = {
            1: prior.image_tag(visual_files["cluster"]["id"], "Find Your Future Engineering cluster opener")
            + prior.image_tag(visual_files["systems"]["id"], "Find Your Future systems-thinking kitchen scenario and existing floor plan")
            + prior.image_tag(visual_files["kitchen"]["id"], "Find Your Future cabinet-planning grid and discussion prompts"),
            2: "",
            3: "",
            4: "",
            5: prior.image_tag(visual_files["mars"]["id"], "Find Your Future fictional Mission to Mars design brief")
            + prior.image_tag(visual_files["rover"]["id"], "Find Your Future rover sketch and discussion directions"),
        }

        student = {
            1: {
                "TITLE": "Civil Engineering Careers and Systems",
                "PURPOSE": "Use fixed evidence to describe civil-engineering work and explain how one design choice affects a system.",
                "TODAY": "<ul><li>describe the Engineering cluster;</li><li>read one current career card;</li><li>distinguish high-school and postsecondary routes;</li><li>revise a kitchen system.</li></ul>",
                "READY": f'<p>Open {link(files["CAREER"]["id"], "the four-page career and systems packet")} or <a href="{urls["systems"]}">the Canvas annotation activity</a>.</p>',
                "STEPS": step(1, "Read the fixed career evidence", "<p>Keep occupation, work, preparation, May 2024 U.S. median, outlook, and license boundary together.</p>")
                + step(2, "Describe the cluster", "<p>Name two roles and the evidence they exchange.</p>")
                + step(3, "Use the pathway distinction", "<p>The public MacArthur label is Engineering; the 2026–27 IISD coursebook names Civil Engineering. Neither replaces a bachelor’s or license route.</p>")
                + step(4, "Revise the system", "<p>Use the supplied kitchen layout, add cabinets, and explain one second element affected by your choice.</p>"),
                "EXIT": "<p>Describe one cluster problem, one career, and one accurate preparation requirement.</p>",
                "DONE": "<ul><li>evidence card;</li><li>cluster and role connection;</li><li>pathway boundary;</li><li>readable kitchen plan;</li><li>systems explanation.</li></ul>",
                "SUPPORT": "<p>system = sistema · evidence = evidencia · preparation = preparación · license = licencia · infrastructure = infraestructura.</p>",
                "FALLBACK": "<p>The embedded visuals and packet are the full route. H&amp;L, open search, and a partner are not required.</p>",
            },
            2: {
                "TITLE": "Assessment Impact and Emerging Work",
                "PURPOSE": "Explain one possible assessment impact and evaluate two recognized changing engineering specialties.",
                "TODAY": "<ul><li>read four current assessment cards;</li><li>write one verification question;</li><li>compare two O*NET specialties;</li><li>name a limitation.</li></ul>",
                "READY": f'<p>Open {link(files["ASSESS"]["id"], "the five-page assessment and specialty packet")} and {link(files["RUBRIC"]["id"], "the student-visible Minor 2 rubric")}.</p>',
                "STEPS": step(1, "Choose an assessment", "<p>Explain a possible effect on a goal and what the result does not decide by itself.</p>")
                + step(2, "Verify next", "<p>Write one exact question and name the authorized source that should answer it.</p>")
                + step(3, "Compare specialties", "<p>Use Transportation Engineers and Water/Wastewater Engineers. Record work, driver, preparation context, and limitation.</p>")
                + step(4, "Submit and repair claims", f'<p><a href="{urls["assessment"]}">Submit the evidence privately</a>, then <a href="{urls["quiz"]}">use the retryable practice Quiz</a> to check current-policy boundaries.</p>'),
                "EXIT": "<p>Write one accurate assessment-impact statement, one emerging-work judgment, and one evidence limitation.</p>",
                "DONE": "<ul><li>assessment decision;</li><li>verification question;</li><li>two-specialty comparison;</li><li>supported judgment;</li><li>limitation.</li></ul>",
                "SUPPORT": "<p>assessment = evaluación · exemption = exención · placement = colocación · specialty = especialidad · limitation = limitación.</p>",
                "FALLBACK": "<p>The dated cards replace live research. A blocked site or unknown future policy does not prevent completion.</p>",
            },
            3: {
                "TITLE": "Bridge Design — Two Options",
                "PURPOSE": "Create and compare two bridge concepts within one clear evidence boundary.",
                "TODAY": "<ul><li>read the constraints;</li><li>draw two top views;</li><li>draw two side views;</li><li>critique and choose.</li></ul>",
                "READY": f'<p>Open {link(files["DESIGN"]["id"], "the six-page bridge design packet")} or <a href="{urls["design"]}">the Canvas annotation activity</a>.</p>',
                "STEPS": step(1, "Read the boundary", "<p>This classroom prototype does not validate a real bridge.</p>")
                + step(2, "Draw Option A", "<p>Use the dedicated top- and side-view pages. Label span, supports, members, and load point.</p>")
                + step(3, "Draw Option B", "<p>Change a meaningful variable, not just color or decoration.</p>")
                + step(4, "Critique and choose", "<p>Cite one strength for each option, select one, and name the worker who owns the next step.</p>"),
                "EXIT": "<p>Name the next career role, required evidence, and expected work product.</p>",
                "DONE": "<ul><li>four readable views;</li><li>two predictions;</li><li>two evidence-based strengths;</li><li>supported choice;</li><li>career-role evidence.</li></ul>",
                "SUPPORT": "<p>span = tramo · support = apoyo · member = elemento · load = carga · weak point = punto débil.</p>",
                "FALLBACK": "<p>No physical materials or team are required today. Drawing, typed description, enlarged grid, or dictation are accepted.</p>",
            },
            4: {
                "TITLE": "Controlled Test or Equal Data Analysis",
                "PURPOSE": "Use comparable evidence to identify a failure pattern and propose one specific redesign.",
                "TODAY": "<ul><li>pass the safety gate;</li><li>use one load protocol or fixed dataset;</li><li>analyze failure;</li><li>propose and justify a redesign.</li></ul>",
                "READY": f'<p>Open {link(files["TEST"]["id"], "the five-page test and redesign packet")} or <a href="{urls["test"]}">the Canvas annotation activity</a>.</p>',
                "STEPS": step(1, "Confirm the route", "<p>Use the teacher-controlled physical station only when every safety item and supply is ready. Otherwise use the equal fixed dataset.</p>")
                + step(2, "Record comparable evidence", "<p>Use the same staged load and stop rule. Never use textbooks or unstable desks.</p>")
                + step(3, "Analyze failure", "<p>Name the result, evidence, and first failed or limited element.</p>")
                + step(4, "Redesign", "<p>Propose one specific change, why it should help, and what the next test should measure.</p>"),
                "EXIT": "<p>Name who reviews the evidence next and one limit of the classroom prototype.</p>",
                "DONE": "<ul><li>safety or fixed-data route;</li><li>comparable result;</li><li>failure evidence;</li><li>specific redesign;</li><li>career and limit explanation.</li></ul>",
                "SUPPORT": "<p>stage = etapa · failure = falla · redesign = rediseño · variable = variable · prototype = prototipo.</p>",
                "FALLBACK": "<p>The fictional three-sample dataset is an equal route for absence, unavailable supplies, mobility/fine-motor needs, or a closed test station.</p>",
            },
            5: {
                "TITLE": "Mars Transfer and Weekly Synthesis",
                "PURPOSE": "Transfer the design cycle to a fictional rover brief and synthesize the week's individual evidence.",
                "TODAY": "<ul><li>find a class result pattern;</li><li>design a fictional rover;</li><li>explain one tradeoff;</li><li>submit the private portfolio.</li></ul>",
                "READY": f'<p>Open {link(files["SYNTHESIS"]["id"], "the five-page synthesis packet")} and {link(files["PORTFOLIO_RUBRIC"]["id"], "the formative portfolio rubric")}.</p>',
                "STEPS": step(1, "Read anonymous results", "<p>State a pattern, exception, and the evidence—not a public team ranking.</p>")
                + step(2, "Use the fictional Mars brief", "<p>Label four rover needs and two constraints in the large design field.</p>")
                + step(3, "Explain the cycle", "<p>Connect define, test, revise, and evidence across bridge and rover work.</p>")
                + step(4, "Submit privately", f'<p><a href="{urls["portfolio"]}">Submit</a> career/systems, assessment/specialty, design/test/redesign, and synthesis evidence.</p>'),
                "EXIT": "<p>Explain how the high-school pathway supports—but does not complete—the postsecondary route, then write one current verification question.</p>",
                "DONE": "<ul><li>result pattern and limitation;</li><li>rover design and tradeoff;</li><li>four-part synthesis;</li><li>pathway boundary;</li><li>private portfolio.</li></ul>",
                "SUPPORT": "<p>constraint = restricción · tradeoff = compensación · pattern = patrón · route = ruta · verify = verificar.</p>",
                "FALLBACK": "<p>The licensed images, adjacent text, fixed result set, and solo response are the full independent route. No public speaking or H&amp;L favorite is required.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Civil Engineering Careers and Systems",
                "SUBTITLE": "50 minutes · TEKS d(1)(B), d(1)(C), d(2)(A)",
                "ALERT": "<strong>Use the dated distinction.</strong> The current public MacArthur page says Engineering; the 2026–27 IISD coursebook names Civil Engineering. Neither label proves a completed postsecondary route.",
                "PREP": f'<ul><li>Post {link(files["CAREER"]["id"], "the career and systems packet")} and annotation activity.</li><li>Open the three locked FYF visuals.</li><li>Model occupation, source, date, geography, measure, and license boundary.</li></ul>',
                "EVIDENCE": "<p>Career evidence card, cluster/role connection, pathway boundary, readable kitchen plan, and systems explanation. Formative.</p>",
                "FLOW": flow("#1f617a", "Cluster · 5", "One infrastructure problem.") + flow("#4a9d2f", "Career evidence · 15", "Work, preparation, pay, outlook, license boundary.") + flow("#5a2d91", "Pathway · 10", "Current district-source distinction.") + flow("#e3ad19", "Systems plan · 15", "Kitchen choice and second effect.") + flow("#1f617a", "Exit · 5", "Cluster, career, preparation."),
                "MONITOR": "<p>Key evidence: May 2024 U.S. median $99,590; bachelor’s typical; 5% 2024–34; about 23,600 openings/year. PE licensure is not universal for every entry-level role; state and public-service/signing rules vary.</p>",
                "RESOURCES": '<p><a href="https://www.bls.gov/ooh/architecture-and-engineering/civil-engineers.htm">BLS Civil Engineers</a> · <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte/macarthur-high-school">Irving ISD MacArthur CTE</a>. Licensed FYF pages remain inside Canvas.</p>',
                "SUPPORT": "<p>Read the card one field at a time. The kitchen plan has a full-page drawing field; allow annotation, enlarged print, verbal planning, or dictation.</p>",
                "FALLBACK": "<p>No H&amp;L login, open search, or partner is required. The embedded visuals and fixed card are the full route.</p>",
            },
            2: {
                "TITLE": "Assessment Impact and Emerging Work",
                "SUBTITLE": "50 minutes · TEKS d(3)(E), d(1)(D)",
                "ALERT": "<strong>Do not memorize unstable policies.</strong> Students identify a possible impact, what must be verified, and where to verify it.",
                "PREP": f'<ul><li>Post {link(files["ASSESS"]["id"], "the current-source packet")}, {link(files["RUBRIC"]["id"], "the Minor 2 rubric")}, and retryable Quiz.</li><li>Keep the four assessment cards visible.</li><li>Preselect one fictional pathway goal for modeling.</li></ul>',
                "EVIDENCE": "<p><strong>Minor 2 in the 5SW assessment map:</strong> assessment impact decision, verification question, two-specialty comparison, judgment, and limitation. Convert the rubric result to a 100-point grade only after the Minor group is verified.</p>",
                "FLOW": flow("#1f617a", "Boundaries · 5", "What a result can and cannot decide.") + flow("#4a9d2f", "Assessment cards · 15", "Four current bounded uses.") + flow("#5a2d91", "Decision · 10", "Goal impact and verification question.") + flow("#e3ad19", "Specialties · 15", "Compare, judge, limit.") + flow("#1f617a", "Exit · 5", "Impact and emerging evidence."),
                "MONITOR": "<p>PSAT 8/9 is Grade 8 or 9 and not sent to colleges; enhanced ACT Composite uses English, math, and reading; TSIA2 applies to entering non-exempt students; ASVAB use varies by service/program. For d(1)(D), require a named O*NET occupation, driver/change, judgment, and limitation.</p>",
                "RESOURCES": '<p><a href="https://counselors.collegeboard.org/assessments/psat-8-9/overview-dates">College Board PSAT 8/9</a> · <a href="https://www.act.org/content/act/en/products-and-services/the-act-educator/the-act-test/enhancements-k12.html">ACT enhancements</a> · <a href="https://www.highered.texas.gov/texas-success-initiative/">Texas Success Initiative</a> · <a href="https://www.onetonline.org/link/summary/17-2051.01">O*NET Transportation Engineers</a> · <a href="https://www.onetonline.org/link/summary/17-2051.02">O*NET Water/Wastewater Engineers</a></p>',
                "SUPPORT": "<p>Use sentence frames: This result may affect __ because __. It does not decide __ by itself. I would verify __ at __.</p>",
                "FALLBACK": "<p>All required evidence is in the packet. A site outage or uncertain future policy becomes a verification question, not a student penalty.</p>",
            },
            3: {
                "TITLE": "Bridge Design — Two Options",
                "SUBTITLE": "50 minutes · d(1)(C) reinforcement through career-role evidence",
                "ALERT": "<strong>Confirm the Day 4 route before class.</strong> If supplies, test rig, staffing, or safe protocol are not ready, plan the equal fixed-data route now.",
                "PREP": f'<ul><li>Post {link(files["DESIGN"]["id"], "the six-page design packet")} and annotation activity.</li><li>Prepare a short static bridge-system comparison.</li><li>If building, distribute identical premeasured kits and publish the exact constraints.</li></ul>',
                "EVIDENCE": "<p>Two top/side concepts, predictions, critique, choice, and individual career-role evidence. Formative.</p>",
                "FLOW": flow("#1f617a", "Shape notice · 5", "Geometry and connection behavior.") + flow("#4a9d2f", "Constraints · 10", "Span, supports, load, stop rule.") + flow("#5a2d91", "Compare systems · 10", "Beam, truss, arch boundaries.") + flow("#e3ad19", "Two options · 20", "Four views, critique, choice.") + flow("#1f617a", "Exit · 5", "Next worker and work product."),
                "MONITOR": "<p>Require two meaningfully different systems, not decorative variations. Triangulation can stabilize a pin-jointed frame, but joints, materials, span, and load still matter. Do not call any classroom sketch structurally validated.</p>",
                "RESOURCES": "<p>The CCE constraints are a classroom evidence model, not professional design guidance. Use only teacher-curated visuals; no 15-minute open-web bridge research.</p>",
                "SUPPORT": "<p>Each view has its own large landscape page. Accept enlarged grids, tactile pieces, verbal description, dictation, or a data/design role.</p>",
                "FALLBACK": "<p>No build, team, fine-motor performance, or public explanation is required for Day 3 evidence.</p>",
            },
            4: {
                "TITLE": "Controlled Test or Equal Data Analysis",
                "SUBTITLE": "50 minutes · d(1)(C) reinforcement through evidence ownership",
                "ALERT": "<strong>Safety gate is binding.</strong> No textbooks, unstable desks, improvised scales on the bridge, student load placement, or uncontrolled failure testing.",
                "PREP": f'<ul><li>Post {link(files["TEST"]["id"], "the test/redesign packet")} and annotation activity.</li><li>Choose PHYSICAL or FIXED DATA before students enter.</li><li>For PHYSICAL: secure supports/catch tray, mark a keep-clear zone, use known lightweight stages and one safe cap, and assign teacher-only load placement.</li></ul>',
                "EVIDENCE": "<p>Comparable result, failure evidence, specific redesign, next measure, career reviewer, and prototype limit. Formative.</p>",
                "FLOW": flow("#1f617a", "Safety/protocol · 5", "One route and one stop rule.") + flow("#4a9d2f", "Build or inspect · 25", "Physical checkpoints or fixed samples.") + flow("#5a2d91", "Test/data · 10", "Comparable stages and stop evidence.") + flow("#e3ad19", "Redesign · 5", "One supported change.") + flow("#1f617a", "Exit · 5", "Reviewer and limit."),
                "MONITOR": "<p>Fixed key: A completes stage 2, center deck displaces before 3; B reaches the safe cap at stage 5 with no stop; C completes stage 3, support contact slips before 4. Multiple redesigns can earn full credit when tied to evidence. Do not rank teams publicly.</p>",
                "RESOURCES": "<p>The fixed dataset is explicitly fictional classroom evidence. Strength-to-weight is not calculated unless every bridge mass is measured with a valid method; the default comparison is maximum completed standardized stage.</p>",
                "SUPPORT": "<p>Assign design lead, builder, recorder/data analyst, and safety observer as useful roles, but collect the individual analysis. Offer the fixed-data route without penalty.</p>",
                "FALLBACK": "<p>Use the fixed dataset for absence, unavailable consumables, insufficient stations, mobility/fine-motor needs, or any failed safety check.</p>",
            },
            5: {
                "TITLE": "Mars Transfer and Weekly Synthesis",
                "SUBTITLE": "50 minutes · TEKS d(1)(C); portfolio reassesses d(1)(B), d(1)(D), d(2)(A), d(3)(E)",
                "ALERT": "<strong>Formative engineering portfolio.</strong> Use the bridge/design evidence for feedback and revision; it is not one of the two mapped 5SW majors. Keep unpublished and ungraded until the review gate passes.",
                "PREP": f'<ul><li>Post the two locked FYF visuals, {link(files["SYNTHESIS"]["id"], "the synthesis packet")}, and {link(files["PORTFOLIO_RUBRIC"]["id"], "the formative portfolio rubric")}.</li><li>Prepare anonymous physical or fixed-data results.</li><li>Open the private portfolio Assignment.</li></ul>',
                "EVIDENCE": "<p>Result pattern/limit, fictional rover design/tradeoff, four-part synthesis, pathway boundary, and verification question.</p>",
                "FLOW": flow("#1f617a", "Pattern · 5", "Anonymous results, no ranking.") + flow("#4a9d2f", "Rover brief · 20", "Fictional design and constraints.") + flow("#5a2d91", "Tradeoff · 10", "Bridge/rover cycle connection.") + flow("#e3ad19", "Synthesis · 10", "Career, assessment, specialty, redesign.") + flow("#1f617a", "Exit · 5", "Pathway support and verification."),
                "MONITOR": "<p>The Mars activity is a fictional workbook transfer brief, not current NASA status. Strong synthesis preserves one accurate career/preparation claim, an assessment impact with boundary, recognized emerging-work evidence, and a result-supported redesign.</p>",
                "RESOURCES": "<p>Licensed FYF pages remain in authenticated Canvas. Current district-source labels are stated with dates and treated as a question to verify—not forced into a false DIRECT/STEPPING-STONE choice.</p>",
                "SUPPORT": "<p>Allow private text, audio, media recording, speech-to-text, enlarged print, or paper. The rover sketch has a dedicated large field.</p>",
                "FALLBACK": "<p>No team attendance, public speaking, physical bridge, H&amp;L favorite, Xello task, or eDynamic completion is required.</p>",
            },
        }

        day_names = {
            1: "Civil Engineering Careers and Systems",
            2: "Assessment Impact and Emerging Work",
            3: "Bridge Design — Two Options",
            4: "Controlled Test or Equal Data Analysis",
            5: "Mars Transfer and Weekly Synthesis",
        }
        extras = {
            1: ("Assignment", systems["id"], SYSTEMS_TITLE),
            2: ("Assignment", assessment["id"], ASSESSMENT_TITLE),
            3: ("Assignment", design["id"], DESIGN_TITLE),
            4: ("Assignment", test["id"], TEST_TITLE),
            5: ("Assignment", portfolio["id"], PORTFOLIO_TITLE),
        }
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await prior.upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 5SW Wk2 Day {day} - {day_names[day]}"
            student_page = await common.upsert_page(
                client,
                student_title,
                common.render("5sw-wk2-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, "MEDIA": media[day], **student[day]}),
            )
            teacher_title = f"TEACHER: 5SW Wk2 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(
                client,
                teacher_title,
                common.render("5sw-wk2-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **teacher[day]}),
            )
            await prior.upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await prior.upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            order.extend([("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title)])
            pages[day] = {"teacher": teacher_page, "student": student_page}
            kind, key, title = extras[day]
            await prior.upsert_item(client, module["id"], kind, key, title)
            order.append((kind, key, title))
            if day == 2:
                await prior.upsert_item(client, module["id"], "Quiz", quiz["id"], QUIZ_TITLE)
                order.append(("Quiz", quiz["id"], QUIZ_TITLE))

        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(
                item
                for item in items
                if (kind == "SubHeader" and item.get("id") == key)
                or (kind == "Page" and item.get("page_url") == key)
                or (kind in ("Assignment", "Quiz") and item.get("content_id") == key)
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
                    "quiz": {"id": quiz["id"], "published": quiz.get("published"), "allowed_attempts": quiz.get("allowed_attempts")},
                    "assignments": {
                        "systems": {"id": systems["id"], "published": systems.get("published"), "submission_types": systems.get("submission_types")},
                        "assessment": {"id": assessment["id"], "published": assessment.get("published"), "submission_types": assessment.get("submission_types")},
                        "design": {"id": design["id"], "published": design.get("published"), "submission_types": design.get("submission_types")},
                        "test": {"id": test["id"], "published": test.get("published"), "submission_types": test.get("submission_types")},
                        "portfolio": {"id": portfolio["id"], "published": portfolio.get("published"), "submission_types": portfolio.get("submission_types")},
                    },
                    "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
                    "files": {key: value["id"] for key, value in files.items()},
                    "visuals": {key: value["id"] for key, value in visual_files.items()},
                    "pages": {
                        str(day): {
                            kind: {"url": value["url"], "published": value["published"]}
                            for kind, value in pair.items()
                        }
                        for day, pair in pages.items()
                    },
                    "items": [{"position": item["position"], "type": item["type"], "title": item["title"]} for item in final_items],
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
