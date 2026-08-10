"""Build the unpublished 5SW Week 1 Architecture evidence module."""

import asyncio
import json
import sys

import httpx

import build_4sw_wk1 as common


COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/5sw/wk1"
MODULE_NAME = "5SW Wk1: Blueprint Builders — Architecture Evidence"

SAFETY_TITLE = "PRACTICE: Safety Supervisor Evidence Plan"
QUIZ_TITLE = "PRACTICE: Architecture Career Evidence Check"
QUIZ_ALIASES = ("MINOR 1: Architecture Career Evidence Check",)
ASSESSMENT_TITLE = "MINOR 1: Three-Career Architecture Comparison"
DESIGN_TITLE = "PRACTICE: Community Learning Space Concept"
REVISION_TITLE = "PRACTICE: Building Test and Revision"
PORTFOLIO_TITLE = "FORMATIVE: Architecture Evidence Portfolio"


CONTRACTS = {
    1: {
        "TOPIC": "Career Clusters",
        "OBJECTIVE": "Students will describe how Architecture & Construction roles work together and use supplied FYF evidence to create a bounded fictional safety plan.",
        "TEKS": "d(1)(B), d(1)(C)",
        "DOL": "Completed FYF Safety Supervisor work plus one professional-boundary and cluster-role response.",
        "I_CAN": "describe how Architecture & Construction roles work together and use FYF evidence in a fictional safety plan.",
        "SHOW": "Complete the FYF Safety Supervisor work and explain one professional boundary and cluster-role connection.",
    },
    2: {
        "TOPIC": "Career Preparation",
        "OBJECTIVE": "Students will compare three careers using consistent preparation and salary evidence.",
        "TEKS": "d(2)(A), d(5)(E)",
        "DOL": "Minor 1 three-career comparison with complete source labels, preparation boundaries, recommendation, and limitation.",
        "I_CAN": "compare three careers using the same salary basis and accurate preparation evidence.",
        "SHOW": "Submit Minor 1 with all three careers, source labels, preparation boundaries, a supported recommendation, and one limitation.",
    },
    3: {
        "TOPIC": "Career Opportunities",
        "OBJECTIVE": "Students will identify how an Architecture & Construction worker uses top and front views and create a two-view concept with five spatial-design operations.",
        "TEKS": "d(1)(C)",
        "DOL": "Two-view concept, first design checkpoint, and career-role work-product explanation.",
        "I_CAN": "create top and front views and explain how an Architecture & Construction worker uses this kind of design evidence.",
        "SHOW": "Complete two views, a first design checkpoint, and one career-role work-product explanation.",
    },
    4: {
        "TOPIC": "Career Opportunities",
        "OBJECTIVE": "Students will test a concept against the brief, document one evidence-based revision, and explain which Architecture & Construction worker uses the evidence next.",
        "TEKS": "d(1)(C)",
        "DOL": "Private design submission, revision record, and next-worker work-product explanation.",
        "I_CAN": "test and revise a concept, then explain which Architecture & Construction worker uses the evidence next.",
        "SHOW": "Submit the design privately with one evidence-based revision and a next-worker work-product explanation.",
    },
    5: {
        "TOPIC": "Career Clusters",
        "OBJECTIVE": "Students will apply city-goal evidence to a novelty-building concept and explain how multiple cluster roles work together.",
        "TEKS": "d(1)(B), d(1)(C)",
        "DOL": "Individual city-goal decision, three-role cluster synthesis, and formative private portfolio.",
        "I_CAN": "use city goals to shape a novelty-building concept and explain how three cluster roles work together.",
        "SHOW": "Record one city-goal decision, explain three collaborating roles, and submit the formative portfolio privately.",
    },
}


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    found = next((module for module in modules if module["name"] == MODULE_NAME), None)
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
            if item.get("type") == kind
            and ((kind == "SubHeader" and item.get("title") == title)
            or (kind == "Page" and item.get("page_url") == key)
            or (kind in ("Assignment", "Quiz") and item.get("content_id") == key))
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


QUESTIONS = [
    (
        "Q1 - salary label",
        "The evidence guide lists $96,690 for architects. What does that figure mean?",
        "May 2024 U.S. median annual wage from BLS",
        ["DFW starting salary", "Guaranteed first-year pay", "Maximum salary in Texas"],
        "Correct. Keep occupation, May 2024, U.S., median, and BLS with the figure.",
        "The source does not label this figure DFW, starting, maximum, or guaranteed pay.",
    ),
    (
        "Q2 - compare all three",
        "Which order correctly ranks the three May 2024 U.S. medians from highest to lowest?",
        "Architect, Drafter, Interior Designer",
        ["Drafter, Architect, Interior Designer", "Interior Designer, Drafter, Architect", "All three have the same median"],
        "Correct. The evidence guide lists $96,690, $65,380, and $63,490.",
        "Reopen the fixed guide and compare the same salary column for all three careers.",
    ),
    (
        "Q3 - licensure structure",
        "Which statement stays within the current architecture-registration evidence?",
        "Requirements vary, but a common structure includes approved education, documented experience, and examination.",
        ["Every architect follows exactly seven years of school.", "Passing one software course creates an architecture license.", "Every drafter must complete the ARE."],
        "Correct. The exact route and timing vary by jurisdiction and prior education.",
        "Do not replace a variable registration process with one universal timeline.",
    ),
    (
        "Q4 - design boundary",
        "What does a Grade 8 Tinkercad or paper concept prove?",
        "It shows spatial choices and whether visible brief requirements were addressed.",
        ["It proves the building is structurally safe.", "It proves code and accessibility compliance.", "It authorizes construction."],
        "Correct. The concept is evidence of design thinking, not construction approval.",
        "Structural, code, accessibility, cost, and constructability review require qualified professionals.",
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
        "quiz[description]": "<p>Ungraded, unlimited-retry practice. Use the feedback to repair salary, preparation, and design-boundary labels.</p>",
        "quiz[quiz_type]": "practice_quiz",
        "quiz[published]": "false",
        "quiz[allowed_attempts]": "-1",
        "quiz[show_correct_answers]": "true",
        "quiz[shuffle_answers]": "false",
    }
    endpoint = f"/courses/{COURSE_ID}/quizzes/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes"
    quiz = await common.api(client, "PUT" if found else "POST", endpoint, data=data)
    existing = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    desired_names = {name for name, *_rest in QUESTIONS}
    for prior in existing:
        if prior.get("question_name") not in desired_names:
            await common.api(
                client,
                "DELETE",
                f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior['id']}",
            )
    existing = [prior for prior in existing if prior.get("question_name") in desired_names]
    unique = []
    seen_names = set()
    for prior in existing:
        name = prior.get("question_name")
        if name in seen_names:
            await common.api(
                client,
                "DELETE",
                f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior['id']}",
            )
        else:
            seen_names.add(name)
            unique.append(prior)
    existing = unique
    for position, (name, prompt, correct, wrong, yes, no) in enumerate(QUESTIONS, 1):
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
    expected = [name for name, *_rest in QUESTIONS]
    final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    final_by_name = {entry.get("question_name"): entry for entry in final_questions}
    if set(final_by_name) != set(expected) or len(final_questions) != len(expected):
        actual = [entry.get("question_name") for entry in final_questions]
        raise RuntimeError(f"Architecture Quiz mismatch: expected {expected}, found {actual}")
    reorder_data = []
    for name in expected:
        reorder_data.extend(
            [("order[][id]", str(final_by_name[name]["id"])), ("order[][type]", "question")]
        )
    await common.api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/reorder",
        data=reorder_data,
    )
    final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    actual = [entry.get("question_name") for entry in final_questions]
    if actual != expected:
        raise RuntimeError(f"Architecture Quiz mismatch: expected {expected}, found {actual}")
    return await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


async def require_minor_assignment(client, description, attachment_id):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == ASSESSMENT_TITLE]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one existing mapped Minor assignment named {ASSESSMENT_TITLE!r}; found {len(matches)}"
        )
    found = matches[0]
    if float(found.get("points_possible") or 0) != 100:
        raise RuntimeError(
            f"Refusing to modify {ASSESSMENT_TITLE!r}: expected 100 points, found {found.get('points_possible')}"
        )
    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group = next((entry for entry in groups if entry.get("id") == found.get("assignment_group_id")), None)
    if not group or group.get("name") != "Minor Assessments (40%)":
        raise RuntimeError(
            f"Refusing to modify {ASSESSMENT_TITLE!r}: expected Minor Assessments (40%) group"
        )
    data = {
        "assignment[name]": ASSESSMENT_TITLE,
        "assignment[description]": description,
        "assignment[published]": "false",
        "assignment[points_possible]": "100",
        "assignment[grading_type]": "points",
        "assignment[submission_types][]": ["student_annotation", "online_upload", "online_text_entry"],
        "assignment[annotatable_attachment_id]": str(attachment_id),
    }
    return await common.api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{found['id']}",
        data=data,
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
        support_path = "course files/CCR Materials/5SW/Wk1"
        support_folder = await common.ensure_folder(client, support_path)
        worksheet_names = {
            "SAFETY": "5sw-wk1-safety-supervisor-evidence-plan.pdf",
            "CAREERS": "5sw-wk1-three-career-evidence-comparison.pdf",
            "DESIGN": "5sw-wk1-concept-building-design.pdf",
            "REVISION": "5sw-wk1-design-test-and-revision.pdf",
            "LANDMARK": "5sw-wk1-unexpected-architecture-evidence.pdf",
            "RUBRIC": "5sw-wk1-architecture-comparison-rubric.pdf",
            "PORTFOLIO_RUBRIC": "5sw-wk1-architecture-portfolio-rubric.pdf",
        }
        files = {
            key: await common.upload(client, ROOT / "docs/resources/worksheets" / name, support_path)
            for key, name in worksheet_names.items()
        }

        visual_files = {}
        for day, names in {
            1: [
                ("cluster", "fyf-architecture-cluster-opener.jpg"),
                ("scenario", "fyf-safety-supervisor-scenario.jpg"),
                ("steps", "fyf-safety-supervisor-steps.jpg"),
            ],
            5: [
                ("city", "climber-city-goals.jpg"),
                ("unexpected", "fyf-unexpected-architecture-scenario.jpg"),
                ("design", "fyf-unexpected-architecture-design.jpg"),
                ("pitch", "fyf-unexpected-architecture-pitch.jpg"),
            ],
        }.items():
            folder_path = f"course files/CCR Materials/5SW/Wk1/Day {day} Visuals"
            await common.ensure_folder(client, folder_path)
            for key, name in names:
                visual_files[key] = await common.upload(client, ASSETS / f"day{day}" / name, folder_path)

        quiz = await upsert_quiz(client)
        comparison = await require_minor_assignment(
            client,
            "<p>Submit the completed three-career comparison by Canvas annotation, upload, typed labeled response, or paper. Use the student-visible 16-point rubric; Tinkercad, drawing, and public speaking are not part of this grade.</p>",
            files["CAREERS"]["id"],
        )
        safety = await common.upsert_assignment(
            client,
            SAFETY_TITLE,
            "<p>Annotate or upload the fictional Safety Supervisor plan, type labeled responses, or use paper. This is not real commercial-diving or construction guidance.</p>",
            ["student_annotation", "online_upload", "online_text_entry"],
            files["SAFETY"]["id"],
        )
        design = await common.upsert_assignment(
            client,
            DESIGN_TITLE,
            "<p>Submit the two-view concept by Canvas annotation, upload, text, or paper. Tinkercad and paper routes use the same evidence criteria.</p>",
            ["student_annotation", "online_upload", "online_text_entry"],
            files["DESIGN"]["id"],
        )
        revision = await common.upsert_assignment(
            client,
            REVISION_TITLE,
            "<p>Submit the design image or paper equivalent with the test-and-revision record. Tool speed and artistic polish are not scored.</p>",
            ["student_annotation", "online_upload", "online_text_entry"],
            files["REVISION"]["id"],
        )
        portfolio = await common.upsert_assignment(
            client,
            PORTFOLIO_TITLE,
            "<p>Submit the private Architecture Evidence Portfolio by upload, text, media recording, or paper. This is formative feedback, not a Week 1 Major. Keep it unpublished, worth 0 points, and not graded.</p>",
            ["online_upload", "online_text_entry", "media_recording"],
        )

        urls = {
            "safety": f"/courses/{COURSE_ID}/assignments/{safety['id']}",
            "quiz": f"/courses/{COURSE_ID}/quizzes/{quiz['id']}",
            "comparison": f"/courses/{COURSE_ID}/assignments/{comparison['id']}",
            "design": f"/courses/{COURSE_ID}/assignments/{design['id']}",
            "revision": f"/courses/{COURSE_ID}/assignments/{revision['id']}",
            "portfolio": f"/courses/{COURSE_ID}/assignments/{portfolio['id']}",
        }
        link, step, flow = common.file_link, common.step, common.flow
        media = {
            1: image_tag(visual_files["cluster"]["id"], "Find Your Future Architecture and Construction cluster opener")
            + image_tag(visual_files["scenario"]["id"], "Safety Supervisor fictional underwater research lab scenario")
            + image_tag(visual_files["steps"]["id"], "Safety Supervisor workbook planning steps"),
            2: '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:18px 0">'
            '<section style="border:1px solid #bad4df;border-radius:10px;padding:14px"><h3 style="margin-top:0;color:#1f617a">Architect</h3><p><strong>May 2024 U.S. median:</strong> $96,690</p><p><strong>Common route:</strong> degree requirements vary by jurisdiction; licensure commonly includes education, documented experience, and examination.</p><p><strong>Work product:</strong> plans and design documents.</p></section>'
            '<section style="border:1px solid #bad4df;border-radius:10px;padding:14px"><h3 style="margin-top:0;color:#1f617a">Drafter</h3><p><strong>May 2024 U.S. median:</strong> $65,380</p><p><strong>Common route:</strong> education after high school is common; preparation varies by drafting specialty and employer.</p><p><strong>Work product:</strong> technical drawings and models.</p></section>'
            '<section style="border:1px solid #bad4df;border-radius:10px;padding:14px"><h3 style="margin-top:0;color:#1f617a">Interior Designer</h3><p><strong>May 2024 U.S. median:</strong> $63,490</p><p><strong>Common route:</strong> a bachelor\'s degree is typical; title or practice rules vary by jurisdiction.</p><p><strong>Work product:</strong> functional interior plans and specifications.</p></section>'
            '</div><p style="font-size:14px;color:#52616b"><strong>Source basis for all three cards:</strong> U.S. Bureau of Labor Statistics Occupational Outlook Handbook, May 2024 median annual wages. Use the linked teacher sources for the full current profiles.</p>',
            3: "",
            4: "",
            5: image_tag(visual_files["city"]["id"], "City of Hollow Bend project summary, four city goals, and three novelty-building examples")
            + image_tag(visual_files["unexpected"]["id"], "Unexpected Architecture fictional city-council scenario")
            + image_tag(visual_files["design"]["id"], "Unexpected Architecture brainstorming and two-view design directions")
            + image_tag(visual_files["pitch"]["id"], "Unexpected Architecture pitch and feedback directions"),
        }

        student = {
            1: {
                "TITLE": "Cluster Roles and Safety Supervisor",
                "PURPOSE": "Describe how cluster roles work together and use supplied evidence in a fictional hazard plan.",
                "TODAY": "<ul><li>sort four current ACE pathways;</li><li>match hazards and evidence categories;</li><li>design a labeled fictional plan;</li><li>name a professional boundary.</li></ul>",
                "READY": f'<p><strong>Default route:</strong> use FYF pp. 171-173 in your workbook. Use {link(files["SAFETY"]["id"], "the enlarged three-page fallback")} or <a href="{urls["safety"]}">the Canvas annotation activity</a> only when the workbook is unavailable or you need that route. Do not complete both.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> hazard = something that could cause harm · control = a way to reduce risk · boundary = what a student plan cannot prove.</p><p><strong>Use this frame:</strong> The scenario shows ___. Our plan uses ___ because ___. A qualified professional would still need to ___.</p></div>',
                "STEPS": step(1, "Read the boundary", "<p>This is not real diving or construction guidance.</p>")
                + step(2, "Match evidence", "<p>Connect scenario hazards to people, environment, tools, movement, and emergency-planning categories.</p>")
                + step(3, "Plan and map", "<p>Write five evidence-linked rules and label the dedicated work-area map.</p>")
                + step(4, "Connect careers", "<p>Name one worker contribution and how it connects to another role.</p>"),
                "EXIT": "<p>Name a career, describe its work in this scenario, and connect it to another cluster role.</p>",
                "DONE": "<ul><li>five evidence-linked rules;</li><li>four equipment/person categories;</li><li>readable map;</li><li>professional boundary;</li><li>career connection.</li></ul>",
                "SUPPORT": "<p>hazard = peligro · evidence = evidencia · qualified professional = profesional calificado · safe zone = zona segura.</p>",
                "FALLBACK": "<p>The images, adjacent text, and packet are the full independent route. H&amp;L and open search are not required.</p>",
            },
            2: {
                "TITLE": "Compare Career Preparation and Pay",
                "PURPOSE": "Compare three careers using one dated source basis and accurate preparation boundaries.",
                "TODAY": "<ul><li>keep labels with salary figures;</li><li>compare preparation;</li><li>rank all three medians;</li><li>recommend with two evidence details.</li></ul>",
                "READY": f'<p><strong>Digital route:</strong> use the three evidence cards below and <a href="{urls["comparison"]}">open Minor 1</a>. Use {link(files["CAREERS"]["id"], "the four-page paper or enlarged route")} only when needed. Open {link(files["RUBRIC"]["id"], "the student-visible Minor 1 rubric")} before you begin.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Keep these labels with every pay figure:</strong> occupation · May 2024 · United States · median · BLS.</p><p><strong>Use this frame:</strong> I recommend ___ for Jordan because the median is ___ and the preparation usually includes ___. One limitation is ___.</p></div>',
                "STEPS": step(1, "Read the salary label", "<p>Every figure is a May 2024 U.S. median from BLS. It is not DFW, starting, or guaranteed pay.</p>")
                + step(2, "Compare preparation", "<p>Separate education, documented experience, examination, and registration boundaries.</p>")
                + step(3, "Recommend", "<p>Cite one salary figure and one preparation difference for fictional Jordan.</p>")
                + step(4, "Submit and repair labels", f'<p><a href="{urls["comparison"]}">Submit the comparison privately</a>, then <a href="{urls["quiz"]}">use the retryable practice Quiz</a> to check labels.</p>'),
                "EXIT": "<p>Rank all three medians, then explain why salary alone cannot decide fit.</p>",
                "DONE": "<ul><li>three career rows;</li><li>three salary labels;</li><li>preparation difference;</li><li>supported recommendation;</li><li>one limitation.</li></ul>",
                "SUPPORT": "<p>median = mediana · preparation = preparación · experience = experiencia · examination = examen.</p>",
                "FALLBACK": "<p>The fixed guide replaces live research. Xello-local evidence is optional and stays in its separately labeled field.</p>",
            },
            3: {
                "TITLE": "Two-View Concept Design",
                "PURPOSE": "Create top and front views and explain how a worker uses this kind of design evidence.",
                "TODAY": "<ul><li>choose Canvas or paper;</li><li>practice five spatial operations;</li><li>draw top and front views;</li><li>explain the related work product.</li></ul>",
                "READY": f'<p>Open {link(files["DESIGN"]["id"], "the four-page concept route")} or <a href="{urls["design"]}">the Canvas annotation activity</a>. If your teacher has opened a tested Tinkercad Classroom, you may use the class code and nickname. Do not create a new personal account.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Design labels:</strong> top view · front view · entrance · window · purposeful feature · user need.</p><p><strong>Use this frame:</strong> A ___ would use this concept to ___. The labeled ___ helps that worker understand ___.</p></div>',
                "STEPS": step(1, "Read the fictional brief", "<p>Design a small community learning space. This is not a construction-ready plan.</p>")
                + step(2, "Practice five operations", "<p>Place, resize, align, group, and hole/subtract. On paper, draw, measure, align, combine, and mark openings.</p>")
                + step(3, "Draw two views", "<p>Use the dedicated top-view and front-view pages. Label the user, entrance, windows, roof, and purposeful feature.</p>")
                + step(4, "Begin and save", "<p>Build the main footprint and walls or complete the equal paper base.</p>"),
                "EXIT": "<p>Name one worker who uses a more advanced design and what that worker produces or decides.</p>",
                "DONE": "<ul><li>two readable views;</li><li>all brief labels;</li><li>first design checkpoint;</li><li>one user-centered choice;</li><li>career-role evidence.</li></ul>",
                "SUPPORT": "<p>place = colocar · resize = cambiar tamaño · align = alinear · group = agrupar · opening = abertura.</p>",
                "FALLBACK": "<p>The paper route has the same requirements and score. Tool speed, device access, and art polish are not graded.</p>",
            },
            4: {
                "TITLE": "Test, Revise, and Submit",
                "PURPOSE": "Test a concept against the brief and document one evidence-based revision.",
                "TODAY": "<ul><li>set one priority;</li><li>complete visible requirements;</li><li>test one choice;</li><li>revise and submit privately.</li></ul>",
                "READY": f'<p>Open {link(files["REVISION"]["id"], "the three-page revision record")} or <a href="{urls["revision"]}">the Canvas activity</a>. Continue on the same design surface you used on Day 3.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Revision jobs:</strong> original choice · evidence noticed · change made · expected improvement · next worker.</p><p><strong>Use this frame:</strong> I noticed ___. I changed ___ to ___ because ___. Next, a ___ would use this evidence to ___.</p></div>',
                "STEPS": step(1, "Set a priority", "<p>Choose complete, fix, or clarify from the requirement table.</p>")
                + step(2, "Use the checkpoints", "<p>Footprint/walls/roof; entrance/windows; purposeful feature and labels.</p>")
                + step(3, "Test and revise", "<p>Record the original choice, evidence observed, revision, and why it should help.</p>")
                + step(4, "Submit privately", "<p>Upload the model image, use the teacher-visible saved model, or submit the paper route.</p>"),
                "EXIT": "<p>Name a worker who contributes next and one limit of this Grade 8 concept.</p>",
                "DONE": "<ul><li>requirements audited;</li><li>test evidence;</li><li>specific revision;</li><li>private submission;</li><li>career and limit explanation.</li></ul>",
                "SUPPORT": "<p>test = probar · evidence = evidencia · revise = revisar · limitation = limitación.</p>",
                "FALLBACK": "<p>If export fails, the teacher-visible Classroom model plus the revision record is temporary evidence. Paper remains equal.</p>",
            },
            5: {
                "TITLE": "Unexpected Architecture and Synthesis",
                "PURPOSE": "Use city-goal evidence in a novelty concept and explain how three cluster roles work together.",
                "TODAY": "<ul><li>choose two city goals;</li><li>contribute to front and side views;</li><li>give or record a short explanation;</li><li>complete the private portfolio.</li></ul>",
                "READY": f'<p><strong>Default route:</strong> use FYF pp. 182-184 in your workbook. Use {link(files["LANDMARK"]["id"], "the two-page individual fallback")} when the workbook is unavailable or you need that route. Open {link(files["PORTFOLIO_RUBRIC"]["id"], "the one-page formative feedback guide")} before submitting.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>City goals:</strong> show city identity · attract visitors · support local growth · spark interest in design.</p><p><strong>Use this frame:</strong> We chose ___ and ___. The ___ contributes ___, while the ___ contributes ___. Together, these roles ___.</p></div>',
                "STEPS": step(1, "Read the city goals", "<p>Choose two goals from the licensed brief. A memorable shape must still serve users.</p>")
                + step(2, "Build the firm concept", "<p>Draw front and side views, label evidence, and record your individual contribution.</p>")
                + step(3, "Pitch or explain", "<p>Use a one-minute paired, written, or private recorded route. Public speaking is formative.</p>")
                + step(4, "Submit the portfolio", f'<p><a href="{urls["portfolio"]}">Submit privately</a>: career comparison, design, revision record, and individual synthesis.</p>'),
                "EXIT": "<p>Explain how three distinct roles work together and preserve one Day 2 source label.</p>",
                "DONE": "<ul><li>two city goals;</li><li>individual contribution;</li><li>three role explanations;</li><li>salary/preparation evidence;</li><li>complete private portfolio.</li></ul>",
                "SUPPORT": "<p>city goal = meta de la ciudad · contribution = contribución · role = función · source label = etiqueta de fuente.</p>",
                "FALLBACK": "<p>Create a solo concept or analyze the supplied model. No group, live pitch, H&amp;L favorite, or eDynamic completion is required.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Cluster Roles and Safety Supervisor",
                "SUBTITLE": "50 minutes · TEKS d(1)(B), d(1)(C)",
                "ALERT": "<strong>Fictional and non-operational.</strong> Student plans are never commercial-diving, emergency, engineering, or construction guidance.",
                "PREP": f'<ul><li>Ask students to open FYF pp. 171-173.</li><li>Project the three locked visuals and post the fixed evidence card.</li><li>Keep {link(files["SAFETY"]["id"], "the enlarged fallback")} and annotation route available without printing them for everyone.</li><li>Review the current MacArthur ACE labels: Architecture, Construction, Engineering, Welding.</li></ul>',
                "EVIDENCE": "<p>Five evidence-linked rules, equipment/person categories, readable map, professional boundary, and career connection. Formative.</p>",
                "FLOW": flow("#5a2d91", "Notice · 5", "One room design decision.") + flow("#4a9d2f", "Cluster · 10", "Roles and current ACE pathways.") + flow("#1f617a", "Evidence plan · 25", "Rules, categories, map, boundary.") + flow("#e3ad19", "Peer check · 5", "Evidence and readability.") + flow("#1f617a", "Exit · 5", "Career work and role connection."),
                "MONITOR": "<p>Accept different priorities when they cite the supplied evidence. Require a qualified-professional boundary. Do not allow invented technical settings or pure oxygen as a generic control.</p>",
                "RESOURCES": '<p><a href="https://www.osha.gov/commercial-diving">OSHA commercial diving</a> supports the boundary; the student task uses the fictional CCE evidence categories, not operational procedures.</p>',
                "SUPPORT": "<p>Provide read-aloud, bilingual labels, typing, dictation, annotation, or paper. The map has a dedicated full page.</p>",
                "FALLBACK": "<p>No open search, H&amp;L login, partner, or drawing skill is required.</p>",
            },
            2: {
                "TITLE": "Compare Career Preparation and Pay",
                "SUBTITLE": "50 minutes · TEKS d(2)(A), d(5)(E)",
                "ALERT": "<strong>One evidence basis.</strong> May 2024 U.S. medians are not DFW, starting, maximum, or guaranteed pay.",
                "PREP": f'<ul><li>Post {link(files["CAREERS"]["id"], "the fixed evidence guide")}, {link(files["RUBRIC"]["id"], "the Minor 1 rubric")}, and Quiz.</li><li>Model occupation, source, year, geography, and measure.</li></ul>',
                "EVIDENCE": "<p><strong>Minor 1 in the 5SW assessment map:</strong> three careers, preparation boundaries, salary comparison, limitation, and Jordan recommendation. The protected Assignment remains worth 100 points in Minor Assessments (40%) and unpublished for teacher cloning.</p>",
                "FLOW": flow("#5a2d91", "Labels · 5", "Unsupported versus supported claim.") + flow("#4a9d2f", "Model · 10", "Architect preparation and salary.") + flow("#1f617a", "Compare · 20", "Three fixed career rows.") + flow("#e3ad19", "Recommend · 10", "Salary plus preparation.") + flow("#1f617a", "Exit · 5", "Rank and limitation."),
                "MONITOR": "<p>Key medians: Architect $96,690; Drafter $65,380; Interior Designer $63,490. Different recommendations can earn full credit. Reject the invented salary-to-education ratio.</p>",
                "RESOURCES": '<p><a href="https://www.bls.gov/ooh/architecture-and-engineering/architects.htm">BLS Architects</a> · <a href="https://www.bls.gov/ooh/architecture-and-engineering/drafters.htm">BLS Drafters</a> · <a href="https://www.bls.gov/ooh/arts-and-design/interior-designers.htm">BLS Interior Designers</a> · <a href="https://www.ncarb.org/become-architect/earn-license">NCARB licensure</a></p>',
                "SUPPORT": "<p>Read one career at a time. Preparation and final reasoning receive separate full-width fields.</p>",
                "FALLBACK": "<p>The guide is the complete no-login route. Xello-local data is optional and separately labeled; H&amp;L is not load-bearing.</p>",
            },
            3: {
                "TITLE": "Two-View Concept Design",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>Canvas and paper are ready now.</strong> Tinkercad is an optional extension only after district approval and a tested teacher-managed Classroom. Do not improvise student account creation.",
                "PREP": f'<ul><li>Post {link(files["DESIGN"]["id"], "the four-page concept route")} and annotation activity.</li><li>If enabling Tinkercad, test Safe Mode, the class-code and nickname route, saving, and Chromebook performance before class.</li></ul>',
                "EVIDENCE": "<p>Top and front views, first design checkpoint, user-centered choice, and career-role explanation. Formative.</p>",
                "FLOW": flow("#5a2d91", "Brief · 5", "Fictional community space.") + flow("#4a9d2f", "Choose surface · 5", "Canvas, paper, or enabled Tinkercad.") + flow("#1f617a", "Spatial operations · 15", "Five digital or paper actions.") + flow("#e3ad19", "Concept · 20", "Two views and first checkpoint.") + flow("#1f617a", "Exit · 5", "Career product or decision."),
                "MONITOR": "<p>Tinkercad introduces spatial modeling; it does not prove professional CAD competency. Confirm views and labels before tool polish.</p>",
                "RESOURCES": '<p><a href="https://www.autodesk.com/company/legal-notices-trademarks/privacy-statement/childrens-privacy-statement">Autodesk children\'s privacy statement</a>. Verify current district approval and student join directions before class.</p>',
                "SUPPORT": "<p>Use starter model, grid paper, enlarged print, trackpad directions, typing, dictation, or teacher scribe.</p>",
                "FALLBACK": "<p>The paper route begins immediately after a failed join; it is not extra work or a lower score.</p>",
            },
            4: {
                "TITLE": "Test, Revise, and Submit",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>Concept boundary.</strong> The product does not prove structural safety, code/accessibility compliance, cost, or construction readiness.",
                "PREP": f'<ul><li>Open the private submission and post {link(files["REVISION"]["id"], "the three-page revision record")}.</li><li>If using the optional Tinkercad extension, open the tested Classroom and verify the current screenshot or export route.</li></ul>',
                "EVIDENCE": "<p>Requirement audit, test evidence, revision, private submission, career and limitation explanation. Formative.</p>",
                "FLOW": flow("#5a2d91", "Priority · 5", "Complete, fix, or clarify.") + flow("#4a9d2f", "Reteach · 5", "One common operation.") + flow("#1f617a", "Build/test · 30", "Three visible checkpoints.") + flow("#e3ad19", "Submit · 5", "Private digital or paper route.") + flow("#1f617a", "Exit · 5", "Next worker and limitation."),
                "MONITOR": "<p>Look for a visible requirement test and a revision connected to evidence. Do not score platform speed or visual polish.</p>",
                "RESOURCES": "<p>Use current Tinkercad student-view screenshots captured after the Classroom is created. Avoid brittle directions until the live route is tested.</p>",
                "SUPPORT": "<p>Provide extra time through accommodations, starter shapes, paper, speech-to-text, or a teacher-visible saved-model route.</p>",
                "FALLBACK": "<p>If export fails, accept the teacher-visible saved model and revision record temporarily. Canvas ownership replaces a public full-name filename.</p>",
            },
            5: {
                "TITLE": "Unexpected Architecture and Weekly Synthesis",
                "SUBTITLE": "50 minutes · TEKS d(1)(B), d(1)(C)",
                "ALERT": "<strong>Formative weekly portfolio.</strong> Use this to rehearse and revise evidence; it is not one of the two mapped 5SW majors. Keep the Assignment permanently at 0 points, not graded, and unpublished for teacher cloning.",
                "PREP": f'<ul><li>Ask students to open FYF pp. 182-184.</li><li>Post the locked city-goal visual, {link(files["LANDMARK"]["id"], "the two-page individual fallback")}, and {link(files["PORTFOLIO_RUBRIC"]["id"], "the one-page feedback guide")} without printing them for everyone.</li><li>Open the private formative portfolio Assignment and prepare groups plus a solo route.</li></ul>',
                "EVIDENCE": "<p>Two city goals, individual contribution, three-role synthesis, one preserved Day 2 label, and complete private portfolio.</p>",
                "FLOW": flow("#5a2d91", "Brief · 5", "City goals and examples.") + flow("#4a9d2f", "Firm concept · 25", "Choose, draw, label, record.") + flow("#1f617a", "Pitch/gallery · 15", "One-minute equal routes.") + flow("#e3ad19", "Synthesis · 5", "Three roles and source label."),
                "MONITOR": "<p>A strong synthesis describes distinct work by at least three roles, retains a salary/preparation label, and connects the concept to stated city goals. Public speaking and group attendance are not scored.</p>",
                "RESOURCES": '<p>Licensed FYF and Climber Notes remain in authenticated Canvas. Current local pathway labels come from <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte/macarthur-high-school">Irving ISD MacArthur CTE</a>.</p>',
                "SUPPORT": "<p>Allow solo analysis, written explanation, private recording, speech-to-text, or paper. Students complete the design once in FYF or through the shared team artifact; the two-page fallback captures individual evidence without requiring another drawing.</p>",
                "FALLBACK": "<p>No group, live pitch, H&amp;L favorite, personal profile screenshot, or eDynamic completion is required.</p>",
            },
        }

        day_names = {
            1: "Cluster Roles and Safety Supervisor",
            2: "Career Preparation and Pay",
            3: "Concept Modeling Foundations",
            4: "Build, Test, Revise, and Submit",
            5: "Unexpected Architecture and Synthesis",
        }
        extras = {
            1: ("Assignment", safety["id"], SAFETY_TITLE),
            2: ("Assignment", comparison["id"], ASSESSMENT_TITLE),
            3: ("Assignment", design["id"], DESIGN_TITLE),
            4: ("Assignment", revision["id"], REVISION_TITLE),
            5: ("Assignment", portfolio["id"], PORTFOLIO_TITLE),
        }
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 5SW Wk1 Day {day} - {day_names[day]}"
            student_page = await common.upsert_page(
                client,
                student_title,
                common.render(
                    "5sw-wk1-student.html",
                    {"COURSE_ID": COURSE_ID, "DAY": day, "MEDIA": media[day], **CONTRACTS[day], **student[day]},
                ),
            )
            teacher_title = f"TEACHER: 5SW Wk1 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(
                client,
                teacher_title,
                common.render(
                    "5sw-wk1-teacher.html",
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
            order.extend([("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title)])
            pages[day] = {"teacher": teacher_page, "student": student_page}
            kind, key, title = extras[day]
            await upsert_item(client, module["id"], kind, key, title)
            order.append((kind, key, title))
            if day == 2:
                await upsert_item(client, module["id"], "Quiz", quiz["id"], QUIZ_TITLE)
                order.append(("Quiz", quiz["id"], QUIZ_TITLE))

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
            item = next(item for item in items if matches_item(item, kind, key))
            await common.api(
                client,
                "PUT",
                f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}",
                data={"module_item[position]": position, "module_item[title]": title},
            )

        final_items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        if len(final_items) != len(order):
            raise RuntimeError(f"Expected {len(order)} Week 1 module items; found {len(final_items)}")
        ordered_final = sorted(final_items, key=lambda entry: entry.get("position", 0))
        for position, ((kind, key, _title), entry) in enumerate(zip(order, ordered_final), 1):
            if entry.get("position") != position or not matches_item(entry, kind, key):
                raise RuntimeError(f"Week 1 module order mismatch at position {position}")
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        print(
            json.dumps(
                {
                    "module": {"id": module["id"], "published": module["published"]},
                    "quiz": {"id": quiz["id"], "published": quiz.get("published"), "allowed_attempts": quiz.get("allowed_attempts")},
                    "assignments": {
                        "safety": {"id": safety["id"], "published": safety.get("published"), "submission_types": safety.get("submission_types")},
                        "comparison": {"id": comparison["id"], "published": comparison.get("published"), "submission_types": comparison.get("submission_types")},
                        "design": {"id": design["id"], "published": design.get("published"), "submission_types": design.get("submission_types")},
                        "revision": {"id": revision["id"], "published": revision.get("published"), "submission_types": revision.get("submission_types")},
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
