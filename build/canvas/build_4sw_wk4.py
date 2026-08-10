"""Build the unpublished 4SW Week 4 drone systems module."""

import asyncio
import json
import sys

import httpx

import build_4sw_wk1 as common


COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/4sw/wk4"
MODULE_NAME = "4SW Wk4: Drone Systems, Rules, and Iteration"
DESIGN_TITLE = "PRACTICE: Wildlife-Tracking Drone Design"
CAREER_QUIZ_TITLE = "PRACTICE: Label the Career Evidence"
RULE_QUIZ_TITLE = "PRACTICE: Indoor, Outdoor, or Part 107?"
TEST_TITLE = "PRACTICE: Drone Systems Test and Iteration"
BRIEF_TITLE = "MINOR 2: Drone Systems Evidence Brief"


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    found = next((m for m in modules if m["name"] == MODULE_NAME), None)
    data = {"module[published]": "false"}
    if found:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data=data)
    data["module[name]"] = MODULE_NAME
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


async def upsert_item(client, module_id, kind, key, title):
    items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    found = next((item for item in items if
        (kind == "SubHeader" and item.get("title") == title) or
        (kind == "Page" and item.get("page_url") == key) or
        (kind in ("Assignment", "Quiz") and item.get("content_id") == key)), None)
    if found:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module_id}/items/{found['id']}", data={"module_item[title]": title})
    data = {"module_item[type]": kind, "module_item[title]": title}
    if kind == "Page":
        data["module_item[page_url]"] = key
    elif kind in ("Assignment", "Quiz"):
        data["module_item[content_id]"] = key
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data=data)


QUIZZES = {
    CAREER_QUIZ_TITLE: [
        ("Q1 - Salary label", "Which label is accurate for $51,940 in the supplied Surveying and Mapping Technicians card?", "May 2024 U.S. national median pay", ["DFW starting salary", "Guaranteed first-year pay", "Hourly wage for every technician"], "Correct. Keep year, geography, and measure with the number.", "The card reports a national median, not a local starting salary."),
        ("Q2 - Preparation", "Which occupation in the supplied guide typically requires a bachelor's degree?", "Cartographer or Photogrammetrist", ["Surveying and Mapping Technician", "Aerospace Engineering and Operations Technologist or Technician", "Every occupation that uses drone data"], "Correct. Preparation belongs to the occupation, not to the tool.", "The evidence guide lists a bachelor's degree for Cartographers and Photogrammetrists."),
        ("Q3 - High wage", "Which comparison supports a high-wage classification in this activity?", "The occupation's May 2024 national median is above the same-source all-occupations median.", ["The career sounds technical.", "One website calls it a good job.", "The occupation uses a drone."], "Correct. The comparison uses the same source, geography, year, and measure.", "Using a drone does not by itself prove high wage."),
        ("Q4 - High demand", "Which evidence is needed for the class high-demand rule?", "Projected growth and annual openings from the dated occupation card", ["A single job advertisement", "The student's career preference", "Whether the work is outdoors"], "Correct. Both trend and openings matter.", "Preference and setting do not establish labor demand."),
        ("Q5 - Taylor's tradeoff", "Fictional Taylor likes fieldwork and technology but is unsure about a four-year degree. Which first investigation best uses the supplied evidence?", "Investigate Surveying and Mapping Technician, then verify local GIS training and drone-task expectations with a current program or employer.", ["Choose Cartographer because the highest degree always creates the best fit.", "Choose any job called drone pilot because all drone work has the same preparation and pay.", "Choose the fastest-growing occupation and ignore annual openings and daily work."], "Correct. This recommendation uses Taylor's stated constraint and includes a verification step.", "A defensible recommendation uses preparation, work, labor evidence, and a next verification step."),
    ],
    RULE_QUIZ_TITLE: [
        ("Q1 - Indoor gym", "A microdrone stays inside a closed gym. Which statement is accurate?", "FAA Part 107 does not apply to an indoor-only operation, but campus and model safety rules still apply.", ["Part 107 automatically authorizes it.", "No safety checks apply indoors.", "Calling it educational removes every rule."], "Correct. Federal operating rules and campus safety are separate checks.", "Indoor-only does not mean no safety process."),
        ("Q2 - Outdoor lesson", "A middle-school class plans an outdoor educational flight. What should happen first?", "The school identifies the applicable operating route and obtains required district/campus approval.", ["Fly because every educational flight is automatically exempt.", "Use the indoor checklist as authorization.", "Ask a student to choose the rule."], "Correct. Educational purpose alone does not settle the operating route.", "An indoor checklist cannot authorize an outdoor operation."),
        ("Q3 - Paid inspection", "Which rule is the likely federal starting point for a paid roof inspection?", "Part 107, followed by verification of the operation's current requirements", ["The recreational exception", "No FAA rule because the aircraft is small", "The classroom tabletop route"], "Correct. The operation is work, and the exact details still need verification.", "A paid inspection is not a recreational classroom scenario."),
        ("Q4 - Certificate boundary", "Which statement accurately describes the FAA Remote Pilot Certificate in this lesson?", "It is a Part 107 pathway with current eligibility, testing, application, vetting, and recurrent-training requirements.", ["It is required for every indoor-only flight.", "Completing this middle-school lesson earns the certificate.", "It replaces campus approval and the model-specific safety process."], "Correct. The lesson explains the pathway but does not certify or authorize a student.", "The certificate does not replace campus safety, and the lesson does not award it."),
    ],
}


async def upsert_quiz(client, title, questions):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    found = next((q for q in quizzes if q.get("title") == title), None)
    data = {"quiz[title]": title, "quiz[description]": "<p>Ungraded, retryable practice with immediate feedback. Use the feedback to repair labels or rule decisions before the exit check.</p>", "quiz[quiz_type]": "practice_quiz", "quiz[published]": "false", "quiz[allowed_attempts]": "-1", "quiz[show_correct_answers]": "true", "quiz[shuffle_answers]": "false"}
    endpoint = f"/courses/{COURSE_ID}/quizzes/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes"
    quiz = await common.api(client, "PUT" if found else "POST", endpoint, data=data)
    existing = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    for position, (name, prompt, correct, wrong, yes, no) in enumerate(questions, 1):
        prior = next((q for q in existing if q.get("question_name") == name), None)
        payload = {"question": {"question_name": name, "question_text": prompt, "question_type": "multiple_choice_question", "position": position, "points_possible": 1, "correct_comments": yes, "incorrect_comments": no, "answers": [{"answer_text": correct, "answer_weight": 100}] + [{"answer_text": answer, "answer_weight": 0} for answer in wrong]}}
        path = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior['id']}" if prior else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        await common.api(client, "PUT" if prior else "POST", path, json=payload)
    return await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


async def require_minor_assignment(client, description):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == BRIEF_TITLE]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one existing mapped Minor assignment named {BRIEF_TITLE!r}; found {len(matches)}"
        )
    found = matches[0]
    if float(found.get("points_possible") or 0) != 100:
        raise RuntimeError(
            f"Refusing to modify {BRIEF_TITLE!r}: expected 100 points, found {found.get('points_possible')}"
        )
    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group = next(
        (entry for entry in groups if entry.get("id") == found.get("assignment_group_id")),
        None,
    )
    if not group or group.get("name") != "Minor Assessments (40%)":
        raise RuntimeError(
            f"Refusing to modify {BRIEF_TITLE!r}: expected Minor Assessments (40%) group"
        )
    return await common.api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{found['id']}",
        data={
            "assignment[description]": description,
            "assignment[submission_types][]": [
                "online_upload",
                "online_text_entry",
                "media_recording",
            ],
            "assignment[published]": "false",
        },
    )


def image_tag(file_id, alt):
    return f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" style="display:block;width:100%;max-width:700px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        module = await ensure_module(client)
        support_path = "course files/CCR Materials/4SW/Wk4"
        support_folder = await common.ensure_folder(client, support_path)
        names = {
            "DESIGN": "4sw-wk4-wildlife-tracking-drone-design.pdf",
            "CAREERS": "4sw-wk4-drone-enabled-occupations.pdf",
            "RULES": "4sw-wk4-drone-operation-decision-readiness.pdf",
            "TEST": "4sw-wk4-drone-systems-test.pdf",
            "BRIEF": "4sw-wk4-drone-systems-evidence-brief.pdf",
            "RUBRIC": "4sw-wk4-drone-systems-evidence-rubric.pdf",
        }
        files = {key: await common.upload(client, ROOT / "docs/resources/worksheets" / name, support_path) for key, name in names.items()}
        selected = {1: ["fyf-protecting-wildlife-requirements.jpg"], 5: ["fyf-drone-engineering-program.jpg"]}
        visuals, visual_folders = {}, {}
        for day, image_names in selected.items():
            folder_path = f"course files/CCR Materials/4SW/Wk4/Day {day} Visuals"
            visual_folders[day] = await common.ensure_folder(client, folder_path)
            visuals[day] = {name: await common.upload(client, ASSETS / f"day{day}" / name, folder_path) for name in image_names}

        quizzes = {title: await upsert_quiz(client, title, questions) for title, questions in QUIZZES.items()}
        design = await common.upsert_assignment(client, DESIGN_TITLE, "<p>Annotate or upload the wildlife-system blueprint, type a labeled response, or use paper. Art quality is not scored.</p>", ["student_annotation", "online_upload", "online_text_entry"], files["DESIGN"]["id"])
        test = await common.upsert_assignment(client, TEST_TITLE, "<p>Submit the systems test log by Canvas annotation, upload, or text. Live indoor microdrone, simulator, and tabletop routes are equal.</p>", ["student_annotation", "online_upload", "online_text_entry"], files["TEST"]["id"])
        brief_description = f'<p>Submit the private four-part Drone Systems Evidence Brief by upload, text entry, approved media response, or paper. Use the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">student-visible 16-point scoring guide</a> before submitting. The assignment is already mapped as a 100-point Minor Assessment and remains unpublished for teacher review and cloning. Live flight, hardware access, speed, artistic quality, public speaking, and H&amp;L activity do not affect the score.</p>'
        brief = await require_minor_assignment(client, brief_description)
        urls = {
            "design": f"/courses/{COURSE_ID}/assignments/{design['id']}",
            "career_quiz": f"/courses/{COURSE_ID}/quizzes/{quizzes[CAREER_QUIZ_TITLE]['id']}",
            "rule_quiz": f"/courses/{COURSE_ID}/quizzes/{quizzes[RULE_QUIZ_TITLE]['id']}",
            "test": f"/courses/{COURSE_ID}/assignments/{test['id']}",
            "brief": f"/courses/{COURSE_ID}/assignments/{brief['id']}",
        }
        media = {
            1: image_tag(visuals[1]["fyf-protecting-wildlife-requirements.jpg"]["id"], "Find Your Future Protecting Wildlife scenario and robot mission requirements"),
            2: "", 3: "", 4: "",
            5: image_tag(visuals[5]["fyf-drone-engineering-program.jpg"]["id"], "Find Your Future programs of study page with Engineering Design and Drone Engineering workbook context"),
        }
        link, step, flow = common.file_link, common.step, common.flow
        contracts = {
            1: {
                "TOPIC": "Career Clusters",
                "OBJECTIVE": "Students will explore and describe the CTE career clusters and identify career opportunities within one or more career clusters using evidence from Career Clusters.",
                "TEKS": "d(1)(B), d(1)(C)",
                "DOL": "Individual FYF p. 105 wildlife-tracking blueprint with six labeled system jobs plus one evidence-based redesign and occupation work product.",
                "I_CAN": "describe the Engineering cluster and connect a wildlife need to a labeled system design.",
                "SHOW": "complete my FYF p. 105 blueprint, changed-mission redesign, and occupation work-product check.",
            },
            2: {
                "TOPIC": "Emerging Careers",
                "OBJECTIVE": "Students will research and evaluate emerging occupations related to career interest areas, describe preparation requirements, and classify careers as high skill, high wage, or high demand using evidence from Emerging Careers.",
                "TEKS": "d(1)(D), d(2)(A), d(5)(B)",
                "DOL": "Five-question Drone-Enabled Occupations evidence check with source labels, preparation, classification, tradeoff, and verification step.",
                "I_CAN": "compare three occupations that may use drone data and classify them with dated evidence.",
                "SHOW": "complete the five-question career evidence check and repair any label or tradeoff I miss.",
            },
            3: {
                "TOPIC": "Career Preparation",
                "OBJECTIVE": "Students will research and describe academic, technical, certification, and training requirements for one or more careers in an identified career cluster using evidence from Career Preparation.",
                "TEKS": "d(2)(A)",
                "DOL": "Four-question operating-rule evidence check plus a team readiness gate when a live, simulator, or tabletop test route is used.",
                "I_CAN": "separate indoor, outdoor educational, and Part 107 decisions and explain the Remote Pilot pathway boundary.",
                "SHOW": "complete the four-question rule check and use the correct team readiness gate for today's route.",
            },
            4: {
                "TOPIC": "Career Opportunities",
                "OBJECTIVE": "Students will identify career opportunities within one or more career clusters and identify skills that transfer among a variety of careers using evidence from Career Opportunities.",
                "TEKS": "d(1)(C), d(4)(B)",
                "DOL": "Team three-trial systems log plus an individual evidence-based iteration and two-occupation skill-transfer response.",
                "I_CAN": "use test evidence to improve one variable and explain how the same skill appears in two occupations.",
                "SHOW": "complete the team run log and my individual iteration, tradeoff, and skill-transfer response.",
            },
            5: {
                "TOPIC": "Emerging Careers",
                "OBJECTIVE": "Students will research and evaluate emerging occupations, describe preparation requirements, identify transferable skills, and classify careers using evidence from Emerging Careers.",
                "TEKS": "d(1)(D), d(2)(A), d(4)(B), d(5)(B)",
                "DOL": "Private individual 16-point Drone Systems Evidence Brief with visible self-score and revision.",
                "I_CAN": "combine design, occupation, rule, and test evidence into one accurate private brief.",
                "SHOW": "submit my private Drone Systems Evidence Brief after self-scoring and revising the weakest section.",
            },
        }
        student = {
            1: {
                "TITLE": "Design a Wildlife-Tracking Drone System",
                "PURPOSE": "Turn a fictional conservation need into testable system requirements and a labeled design.",
                "TODAY": "<ul><li>identify needs and constraints;</li><li>write four requirements;</li><li>label six system jobs;</li><li>redesign for a changed mission.</li></ul>",
                "READY": f'<p>Use FYF pp. 104-105. Draw and label the blueprint in FYF p. 105. Use {link(files["DESIGN"]["id"], "the three-page Design Companion")} only for the missing evidence or as the no-workbook/enlarged route. You may submit a photo of FYF p. 105 plus a typed redesign through <a href="{urls["design"]}">the private practice Assignment</a>.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:12px 16px;margin:14px 0"><strong>Words for this task:</strong> requirement · constraint · navigation · payload · communication · disturbance<br><strong>Use this frame:</strong> “Because the mission needs ____, the ____ system must ____.”</div>',
                "STEPS": step(1, "Read the FYF user need", "<p>Separate what the conservationist needs from rain-forest and animal-behavior constraints.</p>")
                + step(2, "Write four requirements", "<p>State what flight, data, communication, and wildlife-protection systems must do.</p>")
                + step(3, "Design in FYF p. 105", "<p>Label six system jobs and add a short job statement. Record one assumption and one tradeoff.</p>")
                + step(4, "Change the mission", "<p>For sea turtles at night, keep one component, change one, cite mission evidence, and name one occupation work product.</p>"),
                "EXIT": "<p>Name one design change, the mission evidence that requires it, and one occupation work product.</p>",
                "DONE": "<ul><li>four requirements;</li><li>six labeled system jobs on FYF p. 105 or the access packet;</li><li>assumption and tradeoff;</li><li>evidence-based redesign;</li><li>occupation work product.</li></ul>",
                "SUPPORT": "<p>requirement/requisito · constraint/restricción · payload/carga útil · tradeoff/ventaja y costo. The companion separates the blueprint, explanation, and redesign so none is squeezed into a narrow table.</p>",
                "FALLBACK": "<p>The embedded FYF scenario and three-page companion are the complete no-workbook route. Canvas annotation, a photo plus typed redesign, upload, and paper are equal.</p>",
            },
            2: {
                "TITLE": "Compare Drone-Enabled Occupations",
                "PURPOSE": "Compare three real occupations without turning “uses a drone” into a made-up career category.",
                "TODAY": "<ul><li>compare work and preparation;</li><li>keep labels with pay and outlook;</li><li>classify with the published course rule;</li><li>make one evidence-based recommendation.</li></ul>",
                "READY": f'<p>Post or open {link(files["CAREERS"]["id"], "the two-page occupation reference")}. Then open <a href="{urls["career_quiz"]}">the five-question evidence check</a>. Default printing: none.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:12px 16px;margin:14px 0"><strong>Words for this task:</strong> median · growth · annual openings · preparation · tradeoff<br><strong>Use this frame:</strong> “Taylor should investigate ____ because ____ and ____. A tradeoff is ____. Taylor should verify ____ with ____.”</div>',
                "STEPS": step(1, "Compare the work", "<p>Read the worker product, drone/data connection, and preparation for all three occupations.</p>")
                + step(2, "Apply the course rule", "<p>Keep the May 2024 U.S. national median, 2024-34 growth, and annual openings together.</p>")
                + step(3, "Keep the limitation", "<p>An occupation may use drones without every worker flying one. National evidence may differ from local pay and hiring.</p>")
                + step(4, "Complete and repair", f'<p>Use <a href="{urls["career_quiz"]}">the five-question check</a>. Read the feedback and repair any source label, preparation match, classification, or tradeoff you miss.</p>'),
                "EXIT": "<p>Recommend which occupation fictional Taylor should investigate first and name the next fact Taylor must verify.</p>",
                "DONE": "<ul><li>three occupations compared;</li><li>source/date/geography/measure labels kept;</li><li>preparation and classification decisions checked;</li><li>one tradeoff and verification step;</li><li>practice feedback used.</li></ul>",
                "SUPPORT": "<p>median/mediana · growth/crecimiento · openings/vacantes anuales · preparation/preparación. Read one row at a time: circle the work product, box preparation, and underline the pay label.</p>",
                "FALLBACK": "<p>The posted reference and evidence check replace live search and H&amp;L. If Canvas is unavailable, answer the five prompts orally or on paper with the same evidence.</p>",
            },
            3: {
                "TITLE": "Decide Which Drone Rule Applies",
                "PURPOSE": "Separate federal operating rules from campus and model-specific safety approval.",
                "TODAY": "<ul><li>compare indoor, outdoor educational, and paid work;</li><li>read the Remote Pilot pathway boundary;</li><li>complete the rule check;</li><li>use a team readiness gate only for today's selected route.</li></ul>",
                "READY": f'<p>Post page 1 of {link(files["RULES"]["id"], "the three-page Decision and Readiness guide")}. Print page 2 once per team only when a test route is used. Page 3 is the no-Canvas individual route. Then open <a href="{urls["rule_quiz"]}">the four-question rule check</a>.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:12px 16px;margin:14px 0"><strong>Words for this task:</strong> indoor only · operating route · authorization · verify · recurrent training<br><strong>Use this frame:</strong> “Before anyone acts, the school must verify ____ with ____. The indoor checklist does not answer ____ because ____.”</div>',
                "STEPS": step(1, "Compare three situations", "<p>Indoor-only, outdoor educational, and paid inspection do not use one automatic rule.</p>")
                + step(2, "Read the certificate boundary", "<p>The Remote Pilot Certificate has current eligibility, testing, application, vetting, and recurrent-training requirements. This lesson does not award it.</p>")
                + step(3, "Complete the rule check", f'<p>Use <a href="{urls["rule_quiz"]}">the four-question practice Quiz</a> and repair any rule or certificate boundary you miss.</p>')
                + step(4, "Use today's readiness gate", "<p>If the teacher selected live, simulator, or tabletop testing, complete the team check before equipment or tokens move.</p>"),
                "EXIT": "<p>Explain why an indoor checklist cannot authorize an outdoor flight and name the current source or authorized person to use.</p>",
                "DONE": "<ul><li>three situations distinguished;</li><li>certificate boundary identified;</li><li>four-question rule check completed;</li><li>practice feedback used;</li><li>team readiness gate completed when applicable.</li></ul>",
                "SUPPORT": "<p>indoor only/solo interior · operating route/vía legal de operación · authorization/autorización · verify/verificar. Use location, purpose, organization/route, current source, then campus/model approval.</p>",
                "FALLBACK": "<p>No live aircraft is required. The posted rule guide, page 3 individual decision, simulator, and tabletop routes are equal. Outdoor student flight is not part of this lesson.</p>",
            },
            4: {
                "TITLE": "Test and Improve an Inspection System",
                "PURPOSE": "Run controlled trials, change one variable, and use evidence to choose a next test.",
                "TODAY": "<ul><li>select an equal test route;</li><li>complete three trials or two plus a written third;</li><li>record breakdowns and revisions;</li><li>connect one skill to two occupations.</li></ul>",
                "READY": f'<p>Use {link(files["TEST"]["id"], "the three-page Test and Iteration log")} or <a href="{urls["test"]}">the Canvas activity</a>. Print pages 1-2 once per team and page 3 once per student. Live indoor microdrone, simulator, and tabletop routes use the same evidence.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:12px 16px;margin:14px 0"><strong>Words for this task:</strong> trial · variable · breakdown · limitation · evidence · iteration<br><strong>Use this frame:</strong> “I would ____ because Trial ____ showed ____. The skill ____ also matters in ____ and ____ because ____.”</div>',
                "STEPS": step(1, "Set the mission and roles", "<p>Inspect a marked panel, stay inside the boundary, and return one usable observation. Rotate operator/mover, spotter, logger, and communication checker.</p>")
                + step(2, "Test one variable", "<p>Run, record the result and limitation, then change only one main variable.</p>")
                + step(3, "Make a team claim", "<p>Use all three trials to identify the strongest result, evidence limit, and next test.</p>")
                + step(4, "Write individually", "<p>State the revision, expected evidence, tradeoff decision, and how one transferable skill appears in two occupations.</p>"),
                "EXIT": "<p>Compare a fast rerun with pausing to investigate. Choose one and cite the team log.</p>",
                "DONE": "<ul><li>three trials or two plus a written third;</li><li>one variable at a time;</li><li>team claim and evidence limit;</li><li>individual next-test and tradeoff note;</li><li>two-occupation skill connection.</li></ul>",
                "SUPPORT": "<p>trial/prueba · variable/variable · limitation/limitación · evidence/evidencia. Operator/mover, spotter, logger, and communication checker are equal roles. The individual page is separate from the shared team log.</p>",
                "FALLBACK": "<p>No student is graded on flight, speed, hardware, speaking, or art. If live flight is not teacher-cleared, move directly to simulator or tabletop. An absent student uses the model data on page 3.</p>",
            },
            5: {
                "TITLE": "Drone Systems Evidence Brief",
                "PURPOSE": "Synthesize design, occupation, rule, and test evidence into one accurate private brief.",
                "TODAY": "<ul><li>reopen Days 1-4 evidence;</li><li>write four evidence sections;</li><li>self-score and revise;</li><li>submit privately.</li></ul>",
                "READY": f'<p>Open {link(files["BRIEF"]["id"], "the four-page Evidence Brief")} and post {link(files["RUBRIC"]["id"], "the two-page 16-point rubric")}. The PDF is the paper or enlarged route; typed and private media responses use the same four numbered jobs.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:12px 16px;margin:14px 0"><strong>Words for this task:</strong> synthesize · accurate · limitation · revise · operating route<br><strong>Use the complete frames printed beside each of the four evidence parts.</strong></div>',
                "STEPS": step(1, "Design reasoning", "<p>Connect a user need to a system response, constraint, tradeoff, and changed-mission revision.</p>")
                + step(2, "Occupation and classification", "<p>Use an exact occupation title and keep source/date/geography/measure with the evidence.</p>")
                + step(3, "Rule and iteration", "<p>Make one bounded rule/safety decision and one test-based revision with a two-occupation skill transfer.</p>")
                + step(4, "Audit and submit", f'<p>Remove or correct one unsupported claim, self-score, revise the weakest section, then <a href="{urls["brief"]}">submit privately</a>.</p>'),
                "EXIT": "<p>Name one source or rule label you kept accurate, one skill connected to two occupations, and one claim you corrected.</p>",
                "DONE": "<ul><li>all four brief sections;</li><li>accurate labels and classification limitation;</li><li>bounded rule decision;</li><li>test-based revision and transfer;</li><li>self-score and visible revision;</li><li>private submission.</li></ul>",
                "SUPPORT": "<p>synthesize/integrar · accurate/preciso · limitation/limitación · revise/revisar. Each part has its own full-width response region and complete sentence frame.</p>",
                "FALLBACK": "<p>Missing live-flight evidence uses the tabletop model log. H&amp;L is optional. Canvas failure means the four-page paper brief or a later private upload without penalty.</p>",
            },
        }
        teacher = {
            1: {
                "TITLE": "Design a Wildlife-Tracking Drone System",
                "SUBTITLE": "50 minutes · TEKS d(1)(B), d(1)(C)",
                "ALERT": "<strong>Engineering design, not a flight lesson.</strong> The conservation problem is fictional, and students are not asked to collect real animal, location, or environmental data.",
                "PREP": f'<ul><li>Use FYF pp. 104-105 as the default source and blueprint surface.</li><li>Post {link(files["DESIGN"]["id"], "the three-page Design Companion")} as the no-workbook, enlarged, or annotation route. Do not print it automatically for students using FYF p. 105.</li><li>Project the embedded FYF scenario and prepare one labeled system model.</li></ul>',
                "EVIDENCE": "<p>FYF p. 105 blueprint with six labeled system jobs plus four requirements, assumption, tradeoff, changed-mission redesign, and one occupation work product. Formative.</p>",
                "FLOW": flow("#5a2d91", "Launch · 5", "User, need, and constraint.") + flow("#4a9d2f", "FYF scenario · 8", "Protecting Wildlife requirements.") + flow("#1f617a", "System model · 7", "Need to requirement and six jobs.") + flow("#e3ad19", "Design · 20", "FYF p. 105 blueprint and companion evidence.") + flow("#4a9d2f", "Changed mission · 5", "Sea-turtle redesign.") + flow("#1f617a", "Exit · 5", "Change, evidence, work product."),
                "MONITOR": "<p>Require measurable system jobs, not decorative labels. Strong tradeoffs name the advantage and the cost. The occupation response names a work product. Score reasoning, not drawing quality.</p>",
                "RESOURCES": "<p>Licensed FYF pp. 104-105 supply the fictional Protecting Wildlife problem and blueprint space. The companion captures the requirements, assumption, tradeoff, redesign, and occupation evidence FYF does not ask for.</p>",
                "SUPPORT": "<p>Model need versus requirement. Put the word bank and complete frame beside the task. Allow labeled drawing, typed response, speech-to-text, annotation, or photo plus typed redesign.</p>",
                "FALLBACK": "<p>No platform or drone is required. FYF plus a private typed redesign is the default. The three-page companion is the complete no-workbook route.</p>",
            },
            2: {
                "TITLE": "Compare Drone-Enabled Occupations",
                "SUBTITLE": "50 minutes · TEKS d(1)(D), d(2)(A), d(5)(B)",
                "ALERT": "<strong>Use one evidence basis.</strong> All pay is May 2024 U.S. national median; all outlook is 2024-34 BLS. Do not call these DFW or starting figures.",
                "PREP": f'<ul><li>Post or project {link(files["CAREERS"]["id"], "the two-page occupation reference")}. Default printing: none.</li><li>Open the unpublished five-question practice Quiz.</li><li>Keep live H&amp;L optional.</li></ul>',
                "EVIDENCE": "<p>Five-question individual evidence check covering pay label, preparation, wage and demand decisions, tradeoff, and current verification step. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Occupation versus tool.") + flow("#4a9d2f", "Evidence rows · 12", "Work product and preparation.") + flow("#1f617a", "Classify · 15", "Skill, wage, demand, and limits.") + flow("#e3ad19", "Evidence check · 13", "Five questions with repair feedback.") + flow("#1f617a", "Exit · 5", "Taylor recommendation and verification."),
                "MONITOR": "<p>Key values: Surveying and Mapping Technician $51,940, 5%, 7,600 openings; Cartographer/Photogrammetrist $78,380, 6%, 1,000; Aerospace Engineering and Operations Technologist/Technician $79,830, 8%, 900. The same-source comparison is $49,500 median and 3% growth.</p>",
                "RESOURCES": '<p><a href="https://www.bls.gov/ooh/architecture-and-engineering/surveying-and-mapping-technicians.htm">BLS Surveying and Mapping</a> · <a href="https://www.bls.gov/ooh/architecture-and-engineering/cartographers-and-photogrammetrists.htm">BLS Cartographers</a> · <a href="https://www.bls.gov/ooh/architecture-and-engineering/aerospace-engineering-and-operations-technicians.htm">BLS Aerospace Technologists and Technicians</a></p>',
                "SUPPORT": "<p>Read one evidence row at a time. Students circle work product, box preparation, and underline the pay label before the Quiz. The Taylor frame is visible beside the recommendation.</p>",
                "FALLBACK": "<p>No open search is required. H&amp;L remains supplemental. The posted two-page guide and five-question evidence check are the complete route.</p>",
            },
            3: {
                "TITLE": "Decide Which Drone Rule Applies",
                "SUBTITLE": "50 minutes · TEKS d(2)(A)",
                "ALERT": "<strong>No outdoor student flight.</strong> This lesson practices decisions. Indoor-only operations still require campus and model approval; an indoor checklist never authorizes outdoor operation.",
                "PREP": f'<ul><li>Post page 1 of {link(files["RULES"]["id"], "the three-page Decision and Readiness guide")}.</li><li>Print page 2 once per team only when a live, simulator, or tabletop test route is used. Page 3 is the no-Canvas individual route.</li><li>Open the current FAA sources and unpublished four-question practice Quiz. Select the Day 4 route before class.</li></ul>',
                "EVIDENCE": "<p>Four-question individual rule and certificate-boundary check plus one team readiness gate when a test route is used. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Federal rule versus campus rule.") + flow("#4a9d2f", "Three situations · 12", "Indoor, outdoor educational, paid work.") + flow("#1f617a", "Certificate boundary · 8", "Current pathway, no authorization claim.") + flow("#e3ad19", "Rule Quiz · 12", "Four questions and feedback repair.") + flow("#4a9d2f", "Readiness gate · 8", "Only for today's selected route.") + flow("#1f617a", "Exit · 5", "Rule, source, safety check."),
                "MONITOR": "<p>Key: indoor-only means Part 107 does not apply but campus and model rules remain; an outdoor school lesson requires a verified legal operating route and district approval; paid inspection starts with Part 107. The lesson explains the Remote Pilot pathway but does not certify or authorize a student.</p>",
                "RESOURCES": '<p><a href="https://www.faa.gov/faq/do-faa-rules-and-regulations-apply-commercial-uas-or-drone-operations-conducted-indoors-only">FAA indoor FAQ</a> · <a href="https://www.faa.gov/uas/educational_users">FAA Educational Users</a> · <a href="https://www.faa.gov/uas/commercial_operators/become_a_drone_pilot">Remote Pilot Certificate</a> · <a href="https://www.faa.gov/uas/commercial_operators">Current Part 107 operating resources</a></p>',
                "SUPPORT": "<p>Use the decision sequence: location, purpose, organization or route, current source, then campus and model approval. Keep the word bank and full frame visible during the Quiz repair.</p>",
                "FALLBACK": "<p>Simulator and tabletop are equal. Live indoor flight only follows campus approval, exact model SOP, teacher authorization and training, equipment inspection, clear zone, supervision, and stop procedure.</p>",
            },
            4: {
                "TITLE": "Test and Improve an Inspection System",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(4)(B)",
                "ALERT": "<strong>Live flight is optional.</strong> Use it only after the Day 3 readiness gate. Do not grade flight, speed, hardware access, speaking, or art.",
                "PREP": f'<ul><li>Post {link(files["TEST"]["id"], "the three-page Test and Iteration log")} and Canvas activity. Print pp. 1-2 once per team and p. 3 once per student when using paper.</li><li>Set up one teacher-cleared route: live indoor microdrone, simulator, or tabletop.</li><li>Mark the boundary, target, observation point, and stop procedure. Prepare one completed model trial.</li></ul>',
                "EVIDENCE": "<p>Team three-trial log and evidence limit plus individual next-test, tradeoff, and skill transfer to two occupations. Formative.</p>",
                "FLOW": flow("#5a2d91", "Readiness · 5", "Confirm route and stop condition.") + flow("#4a9d2f", "Model · 8", "Goal, result, breakdown, revision.") + flow("#1f617a", "Three trials · 24", "Eight minutes each; written third if needed.") + flow("#e3ad19", "Individual note · 8", "Evidence, next test, transfer.") + flow("#1f617a", "Exit · 5", "Tradeoff decision."),
                "MONITOR": "<p>Change one main variable. A strong result describes usable evidence and a limitation. Stop live operation immediately for boundary, control, equipment, connection, or authorization failure.</p>",
                "RESOURCES": "<p>The classroom inspection is fictional and does not train or certify a real inspection operation. The manufacturer and campus SOP control the hardware route.</p>",
                "SUPPORT": "<p>Operator or mover, spotter, logger, and communication checker are equal. Pages 1-2 are shared team evidence; p. 3 is individual. The complete response frame sits beside the individual decision.</p>",
                "FALLBACK": "<p>If any live-flight check fails, switch immediately to simulator or tabletop. An absent student uses the supplied model data for the same individual reasoning.</p>",
            },
            5: {
                "TITLE": "Drone Systems Evidence Brief",
                "SUBTITLE": "50 minutes · TEKS d(1)(D), d(2)(A), d(4)(B), d(5)(B)",
                "ALERT": "<strong>Minor 2 in the 4SW assessment map.</strong> The importer verifies the existing 100-point Minor Assessments (40%) mapping and keeps the Assignment unpublished.",
                "PREP": f'<ul><li>Post {link(files["BRIEF"]["id"], "the four-page Evidence Brief")} and {link(files["RUBRIC"]["id"], "the two-page student-visible rubric")}. The PDF is the paper or enlarged route; typed and media responses use the same four jobs.</li><li>Open the protected private unpublished Minor Assignment.</li><li>Return or provide model evidence from Days 1-4.</li></ul>',
                "EVIDENCE": "<p>Private design, occupation and classification, rule and safety, and test and transfer synthesis with self-score and revision. Minor 2, scored with the 16-point rubric and converted to 100 gradebook points.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Find one unsupported claim.") + flow("#4a9d2f", "Anonymous models · 5", "Two useful evidence moves.") + flow("#1f617a", "Reopen evidence · 8", "Source and rule labels.") + flow("#e3ad19", "Brief · 25", "Four numbered evidence parts.") + flow("#1f617a", "Audit and submit · 7", "Self-score and revise."),
                "MONITOR": "<p>Suggested conversion: 15-16 Masters, 13-14 Meets, 12 Approaches, 10-11 Needs Improvement; below 10 follows campus policy. Score evidence and reasoning, not career preference, flight, hardware, speaking, art, H&amp;L, or English mechanics unless meaning is unclear.</p>",
                "RESOURCES": '<p>FYF pp. 108-109 are the district workbook context for Engineering Design, Drone Engineering, postsecondary options, IBCs, CTSOs, and work-based learning. Keep those HQIM names. Current FAA and BLS sources supply bounded rule and labor evidence.</p>',
                "SUPPORT": "<p>The four-page brief separates every reasoning job and places a complete frame beside each part. Offer text, speech-to-text, teacher scribe, private media, or paper.</p>",
                "FALLBACK": "<p>Use model tabletop evidence when a prior artifact is missing. Canvas failure means the four-page paper brief or later private upload without penalty.</p>",
            },
        }
        day_names = {1:"Wildlife-Tracking System Design", 2:"Drone-Enabled Occupations", 3:"Drone Rules and Readiness", 4:"Systems Test and Iteration", 5:"Drone Systems Evidence Brief"}
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 4SW Wk4 Day {day} - {day_names[day]}"
            student_page = await common.upsert_page(client, student_title, common.render("4sw-wk4-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, "MEDIA": media[day], **contracts[day], **student[day]}))
            teacher_title = f"TEACHER: 4SW Wk4 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(client, teacher_title, common.render("4sw-wk4-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **contracts[day], **teacher[day]}))
            await upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title)]
            pages[day] = {"teacher": teacher_page, "student": student_page}
            extras = {1: [("Assignment", design["id"], DESIGN_TITLE)], 2: [("Quiz", quizzes[CAREER_QUIZ_TITLE]["id"], CAREER_QUIZ_TITLE)], 3: [("Quiz", quizzes[RULE_QUIZ_TITLE]["id"], RULE_QUIZ_TITLE)], 4: [("Assignment", test["id"], TEST_TITLE)], 5: [("Assignment", brief["id"], BRIEF_TITLE)]}[day]
            for kind, key, title in extras:
                await upsert_item(client, module["id"], kind, key, title)
                order.append((kind, key, title))
        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(i for i in items if (kind == "SubHeader" and i.get("id") == key) or (kind == "Page" and i.get("page_url") == key) or (kind in ("Assignment", "Quiz") and i.get("content_id") == key))
            await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}", data={"module_item[position]": position, "module_item[title]": title})
        final_items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        print(json.dumps({
            "module": {"id": module["id"], "published": module["published"]},
            "quizzes": {title: {"id": quiz["id"], "published": quiz.get("published"), "quiz_type": quiz.get("quiz_type"), "allowed_attempts": quiz.get("allowed_attempts")} for title, quiz in quizzes.items()},
            "assignments": {"design": {"id": design["id"], "published": design.get("published"), "points_possible": design.get("points_possible"), "grading_type": design.get("grading_type"), "submission_types": design.get("submission_types"), "annotatable_attachment_id": design.get("annotatable_attachment_id")}, "test": {"id": test["id"], "published": test.get("published"), "points_possible": test.get("points_possible"), "grading_type": test.get("grading_type"), "submission_types": test.get("submission_types"), "annotatable_attachment_id": test.get("annotatable_attachment_id")}, "brief": {"id": brief["id"], "published": brief.get("published"), "points_possible": brief.get("points_possible"), "assignment_group_id": brief.get("assignment_group_id"), "submission_types": brief.get("submission_types"), "grading_type": brief.get("grading_type")}},
            "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
            "visual_folders": {str(day): {"id": folder["id"], "locked": folder["locked"]} for day, folder in visual_folders.items()},
            "files": {key: value["id"] for key, value in files.items()},
            "visuals": {str(day): {name: value["id"] for name, value in entries.items()} for day, entries in visuals.items()},
            "pages": {str(day): {kind: {"url": value["url"], "published": value["published"]} for kind, value in pair.items()} for day, pair in pages.items()},
            "items": [{"position": i["position"], "type": i["type"], "title": i["title"]} for i in final_items],
        }, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
