"""Build the unpublished 6SW Week 1 Education evidence module."""

import asyncio
import json
import re
import sys
from urllib.parse import urlencode

import httpx

import build_5sw_wk1 as prior


common = prior.common
COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/6sw/wk1"
MODULE_NAME = "6SW Wk1: Education — Learning Design, Routes, and Service"
RUBRIC_NOTE_MARKER = 'data-cce-rubric-note="cce-advisory-rubric-v1"'
WORKSHEET_FILES = {
    "CLASSROOM": "6sw-wk1-community-classroom-plan.pdf",
    "ROUTES": "6sw-wk1-texas-education-routes.pdf",
    "POSTINGS": "6sw-wk1-education-job-evidence.pdf",
    "PLAY": "6sw-wk1-teach-through-play-service.pdf",
    "PORTFOLIO": "6sw-wk1-education-evidence-portfolio.pdf",
    "RUBRIC": "6sw-wk1-education-portfolio-rubric.pdf",
}
VISUAL_FILES = {f"p{page}": f"fyf-p{page}.jpg" for page in range(213, 220)}
TITLES = {
    1: "PRACTICE: Community Classroom Learning-Space Plan",
    2: "PRACTICE: Texas Education Career Routes",
    3: "PRACTICE: Reading Education Job Evidence",
    4: "PRACTICE: Teach Through Play and Service",
    5: "MINOR 1: Education Evidence Portfolio",
}
MINOR_ALIASES = ("MINOR 1: Education Career Evidence Portfolio",)


def preflight():
    required = [
        ROOT / "build/canvas/templates/6sw-wk1-student.html",
        ROOT / "build/canvas/templates/6sw-wk1-teacher.html",
        *(ROOT / "docs/resources/worksheets" / name for name in WORKSHEET_FILES.values()),
        *(ASSETS / name for name in VISUAL_FILES.values()),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"6SW Wk1 preflight missing required files: {missing}")

CONTRACTS = {
    1: {"TOPIC": "Learning Design", "OBJECTIVE": "Students will describe the Education and Training cluster and identify how two careers contribute to a learning-space design.", "TEKS": "d(1)(B), d(1)(C)", "DOL": "FYF team concept plus a two-page individual career-and-design explanation.", "I_CAN": "describe the Education and Training cluster and explain how two careers contribute to a learning-space design.", "SHOW": "Use the FYF concept once, then submit the two-page individual career-and-design explanation."},
    2: {"TOPIC": "Career Preparation", "OBJECTIVE": "Students will describe common Texas classroom-teacher requirements, compare two preparation patterns, and identify provider evidence needed before choosing a route.", "TEKS": "d(2)(A), d(2)(B)", "DOL": "Three-page Texas Education Career Routes comparison and evidence-based recommendation.", "I_CAN": "separate common Texas teacher requirements from provider details and compare two preparation patterns.", "SHOW": "Complete the three-page route comparison and make a recommendation that names the evidence still needed."},
    3: {"TOPIC": "Job Evidence", "OBJECTIVE": "Students will identify two Education and Training opportunities and distinguish their responsibilities, skills, qualifications, preparation, and evidence limits.", "TEKS": "d(1)(C), d(2)(A)", "DOL": "Two-page two-card job-evidence comparison plus a retryable practice Quiz.", "I_CAN": "compare two Education and Training opportunities without turning one posting into a universal rule.", "SHOW": "Complete the two-card comparison, state one evidence limit, and use the practice Quiz feedback."},
    4: {"TOPIC": "Service Learning", "OBJECTIVE": "Students will identify an early-childhood education work product, revise it from test evidence, and explain how service benefits a community while building skills transferable to two careers.", "TEKS": "d(1)(C), d(4)(E)", "DOL": "FYF activity plus a two-page individual revision and service analysis.", "I_CAN": "design and revise a child-friendly activity, then explain how service builds a skill used in two careers.", "SHOW": "Create and test the FYF activity once, then submit the two-page individual revision and service analysis."},
    5: {"TOPIC": "Career Evidence", "OBJECTIVE": "Students will synthesize career, preparation, job-posting, learning-design, and service evidence to justify an Education and Training direction and next action.", "TEKS": "d(1)(B), d(1)(C), d(2)(A), d(2)(B), d(4)(E)", "DOL": "Three-page Education Career Evidence Portfolio plus a visible one-page 16-point rubric.", "I_CAN": "use this week's evidence to justify an Education and Training direction, limitation, and next action.", "SHOW": "Submit the three-page portfolio, self-score with the one-page rubric, and make one visible revision."},
}


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    matches = [module for module in modules if module.get("name") == MODULE_NAME]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one module named {MODULE_NAME!r}; found {len(matches)}")
    found = matches[0] if matches else None
    data = {"module[published]": "false", "module[name]": MODULE_NAME}
    if found:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data=data)
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


async def mapped_minor_assignment(client):
    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group_matches = [entry for entry in groups if entry.get("name") == "Minor Assessments (40%)"]
    if len(group_matches) != 1:
        raise RuntimeError(
            "Expected exactly one assignment group named 'Minor Assessments (40%)'; "
            f"found {len(group_matches)}"
        )
    group = group_matches[0]
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    accepted = {TITLES[5], *MINOR_ALIASES}
    matches = [entry for entry in assignments if entry.get("name") in accepted]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one existing mapped Education Minor named in {sorted(accepted)!r}; found {len(matches)}")
    found = matches[0]
    rubric_note = re.search(
        r'<div data-cce-rubric-note="cce-advisory-rubric-v1".*?</div>',
        found.get("description") or "",
        flags=re.I | re.S,
    )
    if (
        found.get("published")
        or float(found.get("points_possible") or 0) != 100
        or found.get("assignment_group_id") != group["id"]
        or found.get("grading_type") != "points"
        or found.get("omit_from_final_grade") is not False
        or rubric_note is None
    ):
        raise RuntimeError(
            f"Mapped Education Minor invariant failed before module writes: published={found.get('published')}, "
            f"points={found.get('points_possible')}, group={found.get('assignment_group_id')}, "
            f"grading={found.get('grading_type')}, omit={found.get('omit_from_final_grade')}, "
            f"rubric_note={rubric_note is not None}"
        )
    return found, group, rubric_note.group(0)


async def assert_annotation_assignment(client, assignment, source_attachment_id, *, mapped=False):
    assignment = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignment['id']}")
    source_file = await common.api(client, "GET", f"/files/{source_attachment_id}")
    annotation_id = int(assignment.get("annotatable_attachment_id") or 0)
    annotation_file = await common.api(client, "GET", f"/files/{annotation_id}") if annotation_id else {}
    if annotation_file and not annotation_file.get("locked"):
        annotation_file = await common.api(client, "PUT", f"/files/{annotation_id}", data={"locked": "true"})
    required_routes = {"student_annotation", "online_upload", "online_text_entry"}
    failures = {
        "published": assignment.get("published") is not False,
        "points": float(assignment.get("points_possible") or 0) != (100 if mapped else 0),
        "grading": assignment.get("grading_type") != ("points" if mapped else "percent"),
        "omit": assignment.get("omit_from_final_grade") is not (False if mapped else True),
        "routes": set(assignment.get("submission_types") or []) != required_routes,
        "annotation_missing": not annotation_id,
        "source_locked": source_file.get("locked") is not True,
        "clone_locked": annotation_file.get("locked") is not True,
        "clone_name": annotation_file.get("filename") != source_file.get("filename"),
        "clone_size": int(annotation_file.get("size") or -1) != int(source_file.get("size") or -2),
    }
    failed = [name for name, value in failures.items() if value]
    if failed:
        raise RuntimeError(f"Education annotation Assignment invariant failed for {assignment.get('name')!r}: {failed}")
    return assignment


async def assert_folder_files(client, folder, expected_names):
    """Lock and verify every file currently stored in an exact module folder."""
    folder = await common.lock_folder_files(client, folder)
    files = await common.paged(client, f"/folders/{folder['id']}/files")
    actual = {record.get("display_name") or record.get("filename") for record in files}
    if folder.get("locked") is not True or any(record.get("locked") is not True for record in files):
        raise RuntimeError(f"Education folder lock invariant failed for {folder['id']}")
    if actual != set(expected_names):
        raise RuntimeError(
            f"Education folder contents mismatch for {folder['id']}: "
            f"expected={sorted(expected_names)!r}, actual={sorted(actual)!r}"
        )
    return folder, files


async def upsert_practice_assignment(client, title, description, attachment_id):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == title]
    if len(matches) > 1:
        raise RuntimeError(f"Duplicate assignments named {title!r}: {[entry['id'] for entry in matches]}")
    found = matches[0] if matches else None
    assignment = await common.api(
        client,
        "PUT" if found else "POST",
        f"/courses/{COURSE_ID}/assignments/{found['id']}" if found else f"/courses/{COURSE_ID}/assignments",
        data={
            "assignment[name]": title,
            "assignment[description]": description,
            "assignment[published]": "false",
            "assignment[points_possible]": "0",
            "assignment[grading_type]": "percent",
            "assignment[omit_from_final_grade]": "true",
            "assignment[submission_types][]": ["student_annotation", "online_upload", "online_text_entry"],
            "assignment[annotatable_attachment_id]": str(attachment_id),
        },
    )
    return await assert_annotation_assignment(client, assignment, attachment_id)


async def require_minor_assignment(client, found, group, rubric_note, description, attachment_id):
    assignment = await common.api(client, "PUT", f"/courses/{COURSE_ID}/assignments/{found['id']}", data={
        "assignment[name]": TITLES[5],
        "assignment[description]": description + rubric_note,
        "assignment[published]": "false",
        "assignment[points_possible]": "100",
        "assignment[grading_type]": "points",
        "assignment[omit_from_final_grade]": "false",
        "assignment[assignment_group_id]": str(group["id"]),
        "assignment[submission_types][]": ["student_annotation", "online_upload", "online_text_entry"],
        "assignment[annotatable_attachment_id]": str(attachment_id),
    })
    assignment = await assert_annotation_assignment(client, assignment, attachment_id, mapped=True)
    if assignment.get("assignment_group_id") != group["id"] or RUBRIC_NOTE_MARKER not in (assignment.get("description") or ""):
        raise RuntimeError("Education Minor group/rubric invariant failed after update")
    return assignment


QUESTIONS = [
    ("Q1 - posting field", "Which line is a responsibility?", "Lead a small-group practice activity using the teacher's plan.", ["Bachelor's degree required.", "Clear communication preferred.", "Two years of experience required."], "Correct. A responsibility is work the employee performs.", "Degree, skill, and experience statements are qualifications or preparation evidence."),
    ("Q2 - preferred", "What does preferred usually mean in a posting?", "Helpful to the employer, but not automatically a minimum requirement", ["Legally required for every employer", "A daily responsibility", "Guaranteed after hiring"], "Correct. Keep preferred separate from required.", "Do not turn preferred language into a universal requirement."),
    ("Q3 - evidence limit", "What can one supplied posting card prove?", "What this scenario says, plus the need to verify a live employer posting before applying", ["Every employer uses the same rules", "The job will still be open next year", "The exact DFW starting salary"], "Correct. A posting is bounded evidence.", "One posting cannot prove universal rules, future availability, or an omitted salary measure."),
    ("Q4 - Texas route", "Which item is one of TEA's common classroom-teacher requirements?", "Complete an approved educator preparation program", ["Favorite three H&L careers", "Use one identical provider price", "Complete Xello Discover learning pathways"], "Correct. Approved preparation is one common requirement.", "Platform clicks and one provider's details are not statewide certification requirements."),
    ("Q5 - local boundary", "What does the current Irving public CTE page verify?", "The district currently lists Education and Training at three comprehensive high schools and Early Childhood Education at Cardwell.", ["Every listed student earns a credential", "Every student is admitted automatically", "All course schedules and placements are guaranteed"], "Correct. Keep a public program listing separate from guarantees.", "The public page does not prove admission, schedule, credential, placement, or travel details."),
]


async def upsert_quiz(client):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    matches = [quiz for quiz in quizzes if quiz.get("title") == TITLES[3]]
    if len(matches) > 1:
        raise RuntimeError(f"Duplicate quizzes named {TITLES[3]!r}: {[entry['id'] for entry in matches]}")
    found = matches[0] if matches else None
    data = {"quiz[title]": TITLES[3], "quiz[description]": "<p>Ungraded, unlimited-retry practice on posting fields, preparation, and evidence limits.</p>", "quiz[quiz_type]": "practice_quiz", "quiz[published]": "false", "quiz[allowed_attempts]": "-1", "quiz[show_correct_answers]": "true", "quiz[shuffle_answers]": "false"}
    quiz = await common.api(client, "PUT" if found else "POST", f"/courses/{COURSE_ID}/quizzes/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes", data=data)
    existing = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    desired_names = {name for name, *_rest in QUESTIONS}
    for question in existing:
        if question.get("question_name") not in desired_names:
            await common.api(client, "DELETE", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{question['id']}")
    existing = [entry for entry in existing if entry.get("question_name") in desired_names]
    seen = set()
    for question in existing:
        name = question.get("question_name")
        if name in seen:
            await common.api(client, "DELETE", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{question['id']}")
        else:
            seen.add(name)
    for position, (name, prompt, correct, wrong, yes, no) in enumerate(QUESTIONS, 1):
        old = next((question for question in existing if question.get("question_name") == name), None)
        payload = {"question": {"question_name": name, "question_text": prompt, "question_type": "multiple_choice_question", "position": position, "points_possible": 1, "correct_comments": yes, "incorrect_comments": no, "answers": [{"answer_text": correct, "answer_weight": 100}] + [{"answer_text": answer, "answer_weight": 0} for answer in wrong]}}
        path = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{old['id']}" if old else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        await common.api(client, "PUT" if old else "POST", path, json=payload)
    expected = [name for name, *_rest in QUESTIONS]
    final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    by_name = {entry.get("question_name"): entry for entry in final_questions}
    if set(by_name) != set(expected) or len(final_questions) != len(expected):
        raise RuntimeError("Education practice Quiz question set mismatch")
    fields = []
    for name in expected:
        fields.extend([("order[][id]", str(by_name[name]["id"])), ("order[][type]", "question")])
    await common.api(client, "POST", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/reorder", content=urlencode(fields), headers={"Content-Type": "application/x-www-form-urlencoded"})
    final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    if [entry.get("question_name") for entry in final_questions] != expected:
        raise RuntimeError("Education practice Quiz order mismatch")
    quiz = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
    if quiz.get("published") or quiz.get("quiz_type") != "practice_quiz" or int(quiz.get("allowed_attempts") or 0) != -1 or quiz.get("shuffle_answers") is not False:
        raise RuntimeError(f"Education Quiz invariant failed: published={quiz.get('published')}, type={quiz.get('quiz_type')}, attempts={quiz.get('allowed_attempts')}, shuffle={quiz.get('shuffle_answers')}")
    return quiz


def student_content(files, visuals, urls):
    link, step = common.file_link, common.step
    media = lambda pairs: '<h3 style="color:#126b68;border-bottom:3px solid #a9d8d5">Licensed workbook pages</h3>' + ''.join(prior.image_tag(visuals[key]["id"], alt) for key, alt in pairs)
    return {
        1: {"TITLE": "Community Classroom", "PURPOSE": "Turn the FYF brief into a learning-space concept that supports a real science goal.", "TODAY": "<ul><li>describe the cluster;</li><li>choose a learning goal;</li><li>map two Education careers;</li><li>explain and revise one design choice.</li></ul>", "READY": f'<p><strong>Read the FYF brief on pp. 213-215.</strong> Build the team concept once in FYF. Then record only your individual reasoning in {link(files["CLASSROOM"]["id"], "the two-page evidence surface")} or <a href="{urls[1]}">the private annotation activity</a>. Do not redraw the team poster.</p>', "MEDIA": media([("p213", "Education and Training cluster opener with three example careers"), ("p214", "Community Classroom scenario, requirements, goals, and science topics"), ("p215", "Community Classroom brainstorm, poster, presentation, and reflection steps")]), "STEPS": step(1, "Choose the learning goal", "<p>Name what third graders will learn, not only a decoration theme.</p>") + step(2, "Map two career contributions", "<p>Name what each worker produces or decides.</p>") + step(3, "Explain one design choice", "<p>Use the team FYF concept; explain how one choice supports learning, access, safety, or clarity.</p>") + step(4, "Write and revise", "<p>Add one feedback note and one individual revision recommendation.</p>"), "EXIT": "<p>Name one career, its contribution, one design choice, and the learning goal it supports.</p>", "DONE": "<ul><li>one team FYF concept;</li><li>one two-page individual explanation;</li><li>two distinct career contributions;</li><li>one evidence-based revision.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> learning goal/meta de aprendizaje · contribute/contribuir · investigate/investigar · access/acceso.</p><p><strong>Use this frame:</strong> The ___ contributes ___ so students can ___.</p>", "FALLBACK": "<p><strong>Complete no-team concept — Soil Detectives Lab:</strong> Third graders compare sealed soil samples, record observations, and explain how soil affects plant growth. The teacher sets the investigation sequence; the museum educator creates picture-based specimen prompts. Low materials shelves, wide table paths, sealed trays, and picture labels support access and safety. Headline: <em>Investigate soil like a scientist.</em> Feedback: the station labels look too similar. Recommended revision: add a different large picture and texture cue to each station. Use these facts for the same two-page individual questions. H&amp;L is not required.</p>"},
        2: {"TITLE": "Texas Education Career Routes", "PURPOSE": "Separate Texas requirements from the provider details a student still has to verify.", "TODAY": "<ul><li>read the five common requirements;</li><li>protect the Educational Aide I boundary;</li><li>compare two route patterns;</li><li>recommend what Jordan should verify.</li></ul>", "READY": f'<p>Open {link(files["ROUTES"]["id"], "the three-page route guide")} or <a href="{urls[2]}">the private annotation activity</a>.</p>', "MEDIA": "", "STEPS": step(1, "Mark statewide evidence", "<p>Keep TEA requirements separate from one provider's details.</p>") + step(2, "Read the Aide boundary", "<p>A pathway name alone does not guarantee certification.</p>") + step(3, "Compare route patterns", "<p>Degree timing differs; program quality, clinical route, cost, aid, and timing still require provider evidence.</p>") + step(4, "Advise Jordan", "<p>Cannot decide yet is valid when you name the missing evidence.</p>"), "EXIT": "<p>One statewide requirement, one provider-variable detail, and one question before enrollment.</p>", "DONE": "<ul><li>two common requirements;</li><li>Educational Aide I condition;</li><li>current Irving boundary;</li><li>three provider questions;</li><li>supported recommendation.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> requirement/requisito · provider/proveedor · varies/varía · verify/verificar.</p><p><strong>Use this frame:</strong> Jordan cannot choose from the route label alone. Jordan should compare ___ because ___.</p>", "FALLBACK": "<p>The fixed TEA and Irving evidence is complete. No application, provider contact, payment, Xello, eDynamic, or H&amp;L is required.</p>"},
        3: {"TITLE": "Read Education Job Evidence", "PURPOSE": "Compare two opportunities without turning one posting into a universal career rule.", "TODAY": "<ul><li>read three fixed cards;</li><li>record two;</li><li>compare preparation and transferable skills;</li><li>use Quiz feedback.</li></ul>", "READY": f'<p>Open {link(files["POSTINGS"]["id"], "the two-page evidence guide")} and <a href="{urls[3]}">the retryable practice Quiz</a>.</p>', "MEDIA": "", "STEPS": step(1, "Separate the fields", "<p>A responsibility is work performed; a qualification is a condition for consideration.</p>") + step(2, "Record two cards", "<p>Copy short evidence phrases rather than rewriting the cards.</p>") + step(3, "Compare with limits", "<p>State what appears true in these scenarios and what needs live verification.</p>") + step(4, "Repair with feedback", "<p>Quiz attempts are ungraded and unlimited.</p>"), "EXIT": "<p>One responsibility, one qualification, and one claim the cards cannot prove.</p>", "DONE": "<ul><li>two-card record;</li><li>preparation comparison;</li><li>transferable-skill explanation;</li><li>evidence limit;</li><li>Quiz feedback used.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> responsibility/responsabilidad · qualification/requisito · preferred/preferido · preparation/preparación.</p><p><strong>Use this frame:</strong> Card ___ appears enterable sooner in this scenario because ___. It does not prove ___.</p>", "FALLBACK": "<p>No live job board, account, advertisement click, or application is required.</p>"},
        4: {"TITLE": "Teach Through Play and Service", "PURPOSE": "Design and revise a child-friendly activity, then connect service to skills used across careers.", "TODAY": "<ul><li>use the FYF targets;</li><li>create the activity once;</li><li>record test evidence and revisions;</li><li>connect service to two careers.</li></ul>", "READY": f'<p><strong>Read the FYF brief on pp. 216-217.</strong> Create and test the activity once in FYF. Then record only your individual evidence in {link(files["PLAY"]["id"], "the two-page revision and service surface")} or <a href="{urls[4]}">the private annotation activity</a>. Do not copy the full plan or map again.</p>', "MEDIA": media([("p216", "Teach Through Play scenario and gross and fine motor target skills"), ("p217", "Teach Through Play planning, test, improvement, and discussion steps")]), "STEPS": step(1, "Create one safe activity", "<p>Use FYF for the activity steps and provide a seated, supported, pre-cut, tear, trace, or other access-equivalent option.</p>") + step(2, "Test the activity", "<p>Partner, tabletop, teacher conference, or individual simulation are equal.</p>") + step(3, "Record evidence and revise", "<p>Name one point of confusion or access need and two evidence-based revisions.</p>") + step(4, "Analyze service", "<p>Use a real, planned, or supplied tutoring scenario without private disclosure.</p>"), "EXIT": "<p>Name one revision, one community benefit, and one skill used in two careers.</p>", "DONE": "<ul><li>one FYF activity created and tested;</li><li>one two-page individual evidence surface;</li><li>two evidence-based revisions;</li><li>community benefit;</li><li>two-career skill transfer.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> gross motor/motricidad gruesa · fine motor/motricidad fina · service/servicio · revision/revisión.</p><p><strong>Use this frame:</strong> Service benefits the community by ___. In a ___ career, the skill helps ___.</p>", "FALLBACK": "<p>The locked FYF images provide the brief. If the workbook or team is unavailable, use the complete teacher-supplied activity scenario; use individual simulation and the supplied library-tutoring scenario for the same two-page evidence route.</p>"},
        5: {"TITLE": "Education Evidence Portfolio", "PURPOSE": "Use five evidence types to justify a direction, limitation, and next action.", "TODAY": "<ul><li>read the current Irving evidence strip;</li><li>assemble the week's evidence;</li><li>self-score;</li><li>make one visible revision.</li></ul>", "READY": f'<p>Open {link(files["PORTFOLIO"]["id"], "the three-page portfolio")}, {link(files["RUBRIC"]["id"], "the one-page rubric")}, and <a href="{urls[5]}">the private Minor 1 Assignment</a>.</p>', "MEDIA": media([("p218", "Workbook Education and Training program context and I Am Next spotlight"), ("p219", "Workbook program, Educational Aide I, TAFE, endorsement, and field-experience context")]), "STEPS": step(1, "Keep current and workbook claims labeled", "<p>The portfolio includes a current Irving strip. FYF pp. 218-219 remain district-workbook context; time-sensitive promises need verification.</p>") + step(2, "Assemble five evidence types", "<p>Use career, preparation, posting, design/revision, and service evidence. The missing-work strip is an honest fallback.</p>") + step(3, "Conclude with a limit", "<p>Career preference is valid but is not the evidence being scored.</p>") + step(4, "Self-score and repair", "<p>Revise the weakest criterion before private submission.</p>"), "EXIT": "<p>One supported conclusion, one limitation, and one next action.</p>", "DONE": "<ul><li>three-page portfolio;</li><li>current source/date and boundary;</li><li>five evidence types;</li><li>rubric self-score;</li><li>visible revision.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> evidence/evidencia · pathway/programa de estudio · limitation/limitación · next action/próximo paso.</p><p><strong>Use this frame:</strong> The strongest evidence is ___. A limit is ___. My next action is ___ because ___.</p>", "FALLBACK": "<p>The portfolio contains a current Irving strip and a fixed missing-work strip. FYF p. 220 H&amp;L exploration, Xello Discover learning pathways, and eDynamic 7.2 are optional extensions only.</p>"},
    }


def teacher_content(files):
    link, flow = common.file_link, common.flow
    color = "#126b68"
    sources = '<p><a href="https://tea.texas.gov/educators/certification/initial-certification/becoming-classroom-teacher-texas">TEA Classroom Teacher</a> · <a href="https://tea.texas.gov/educators/certification/becoming-educational-aide-texas">TEA Educational Aide</a> · <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte">Irving High School CTE</a>.</p>'
    support = '<p>Point to the visible word bank and complete frame before students write. Accept typing, dictation, annotation, enlarged print, bilingual labels, paper, private rehearsal, and teacher scribing. Score evidence and reasoning, not English mechanics unless meaning is unclear.</p>'
    fallback = '<p>Locked FYF images and fixed companions are the complete absence/platform route. No application, provider contact, public Discussion, personal volunteer disclosure, H&amp;L, Xello, eDynamic, or live job-board work is required.</p>'
    return {
        1: {"TITLE": "Community Classroom", "SUBTITLE": "50 minutes · FYF pp. 213-215 first", "ALERT": "<strong>Trim point:</strong> protect the learning goal, career contributions, and design reasoning; trim decorative poster work first.", "PREP": f'<ul><li><strong>Default:</strong> one device and FYF workbook per student, one projector, zero prints. Post {link(files["CLASSROOM"]["id"], "the two-page individual evidence companion")} and private annotation route.</li><li><strong>Paper:</strong> print one two-page companion per student; set one collection tray. Students use either paper or Canvas, not both.</li><li>Teams create the concept once in FYF. The companion is individual reasoning only. Optional partner feedback needs no extra materials; poster board is not required.</li></ul>', "EVIDENCE": "<p>Score the team FYF concept in place. Collect only the two-page individual goal, two career contributions, design-choice explanation, booking explanation, feedback, and revision.</p>", "MODEL": '<div style="border:1px solid #a9d8d5;border-radius:8px;padding:12px 16px;background:#f1fbfa"><p><strong>Complete fallback concept — Soil Detectives Lab:</strong> Third graders compare sealed soil samples, record observations, and explain how soil affects plant growth. The teacher sets the investigation sequence; the museum educator creates picture-based specimen prompts. Low materials shelves, wide table paths, sealed trays, and picture labels support access and safety. <strong>Headline:</strong> “Investigate soil like a scientist.” <strong>Feedback:</strong> the station labels look too similar. <strong>Revision:</strong> add a different large picture and texture cue to each station.</p><p><strong>Non-example:</strong> “Add blue walls because blue is calm.” Decoration alone does not show a learning purpose.</p></div>', "FLOW": flow(color, "Warm-up and cluster · 5", "Stop-and-jot, then one turn-and-talk.") + flow("#4c8b38", "Read and model · 9", "FYF pp. 213-214; one complete evidence chain.") + flow("#1f617a", "Team concept · 21", "Create one FYF concept; individual students record goal, roles, and one design reason.") + flow("#d39b22", "Booking decision/revision · 10", "Self-check, peer, or teacher feedback.") + flow(color, "Submit/cleanup · 5", "Two-page private response and material return."), "MONITOR": "<ul><li><strong>Minute 12:</strong> every student has a third-grade science goal and two distinct Education roles. If one-third lists decorations only, project the model and rebuild one choice as goal → worker → design.</li><li><strong>Minute 30:</strong> each team FYF concept shows the learning action; each student has explained one design choice and one access or safety need. Students behind use the complete Soil Detectives Lab concept and continue the same individual questions.</li><li><strong>Minute 43:</strong> the booking explanation names learning, not just appearance, and one evidence-based revision.</li><li><strong>Trim/recovery:</strong> cut partner sharing and poster polish. Protect goal, roles, design reasoning, revision, submission, and cleanup. Save the same two-page artifact for recovery.</li></ul>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        2: {"TITLE": "Texas Education Career Routes", "SUBTITLE": "50 minutes · state requirements and provider evidence", "ALERT": "<strong>Accuracy boundary:</strong> do not call one preparation route automatically cheaper, faster, paid, unpaid, easier, or better.", "PREP": f'<ul><li><strong>Default:</strong> one device per student, one projector, zero prints. Post {link(files["ROUTES"]["id"], "the three-page fixed guide")} and annotation route.</li><li><strong>Paper:</strong> print one three-page guide per student and set one collection tray.</li><li>Students work individually. Open the current TEA teacher and Educational Aide pages for teacher reference only. Students do not open applications, contact providers, submit data, or pay fees.</li></ul>', "EVIDENCE": "<p>Collect statewide requirements, Educational Aide boundary, provider questions, and Jordan's evidence-based recommendation.</p>", "MODEL": '<div style="border:1px solid #a9d8d5;border-radius:8px;padding:12px 16px;background:#f1fbfa"><p><strong>Model:</strong> “Both routes must use an approved educator preparation program. Jordan still needs each provider\'s admission rules, clinical placement, total cost/aid, and timeline. The route label alone does not support a choice.”</p><p><strong>Non-example:</strong> “Alternative certification is always faster and cheaper.” Those facts vary by provider and candidate.</p></div>', "FLOW": flow(color, "Warm-up · 5", "Three facts needed before choosing.") + flow("#4c8b38", "Requirements/model · 10", "Five common requirements and CTE exception note.") + flow("#1f617a", "Route evidence · 14", "Statewide versus provider-variable.") + flow("#d39b22", "Aide/Irving boundary · 8", "Exact conditions and public-listing limit.") + flow("#1f617a", "Jordan decision · 8", "Three facts and supported next step.") + flow(color, "Submit/cleanup · 5", "Requirement, variable, question."), "MONITOR": "<ul><li><strong>Minute 13:</strong> students can name two of the five common requirements and mark one provider-variable field. If one-third treats a route label as proof, sort four statements together.</li><li><strong>Minute 29:</strong> Educational Aide evidence includes age 18+, course/credit/grade conditions, written superintendent verification, and the application/background-review boundary without promising certification.</li><li><strong>Minute 42:</strong> Jordan response names three exact provider facts and may honestly say cannot decide yet.</li><li><strong>Trim/recovery:</strong> cut sharing, never the statewide/provider distinction, Aide boundary, decision, submission, or cleanup. Save the same guide for recovery.</li></ul>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        3: {"TITLE": "Read Education Job Evidence", "SUBTITLE": "50 minutes · fixed cards and retryable feedback", "ALERT": "<strong>Evidence boundary:</strong> one posting or fictional card cannot prove universal employer rules, future availability, or DFW starting pay.", "PREP": f'<ul><li><strong>Default:</strong> one device per student, one projector, zero prints. Post {link(files["POSTINGS"]["id"], "the two-page fixed guide")} and unpublished unlimited-retry practice Quiz.</li><li><strong>Paper:</strong> print one two-page landscape guide per student; set one collection tray. Keep a five-question paper check only for a Canvas outage.</li><li>Students work individually after a brief field-sort turn-and-talk. No live job-board account or open search is required.</li></ul>', "EVIDENCE": "<p>Collect the two-card comparison and evidence limit; use the Quiz only for immediate feedback, not duplicate scored evidence.</p>", "MODEL": '<div style="border:1px solid #a9d8d5;border-radius:8px;padding:12px 16px;background:#f1fbfa"><p><strong>Model:</strong> “Support a small-group activity is a responsibility because it is work the aide performs. Diploma/equivalent plus the employer\'s stated rules is preparation evidence. Card A appears enterable sooner in this scenario, but a student must verify a live employer posting and district rules.”</p><p><strong>Non-example:</strong> “Preferred means every applicant must have it.” Preferred is not automatically required.</p></div>', "FLOW": flow(color, "Warm-up/model · 7", "Responsibility, qualification, preferred.") + flow("#4c8b38", "Read fixed cards · 8", "One field at a time.") + flow("#1f617a", "Record two cards · 17", "Copy short evidence phrases.") + flow("#d39b22", "Compare/limit · 10", "Preparation, transfer, live verification.") + flow(color, "Quiz/submit · 8", "Feedback, exit, material return."), "MONITOR": "<ul><li><strong>Minute 12:</strong> students correctly label one responsibility and one qualification. If one-third confuses them, use the supplied model and retag two lines.</li><li><strong>Minute 29:</strong> two cards have short evidence phrases in all four fields; students are not copying entire cards.</li><li><strong>Minute 40:</strong> comparison names exact preparation wording, one transferable skill, and a source limit.</li><li><strong>Quiz gate:</strong> one attempt, feedback read, retry missed ideas only. If Canvas fails, use the guide/paper check. Do not require a second written comparison.</li><li><strong>Trim/recovery:</strong> cut turn-and-talk and extra retries. Protect comparison, limit, one feedback pass, submission, and cleanup.</li></ul>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        4: {"TITLE": "Teach Through Play and Service", "SUBTITLE": "50 minutes · FYF pp. 216-217 first", "ALERT": "<strong>Access boundary:</strong> physical performance, cutting skill, disability, artistry, disclosure, and partner attendance are not scored.", "PREP": f'<ul><li><strong>Default:</strong> one device and FYF workbook per student, one projector, zero prints. Post {link(files["PLAY"]["id"], "the two-page individual evidence companion")} and private annotation route.</li><li><strong>Paper:</strong> print one two-page companion per student and set one collection tray. Students use either paper or Canvas, not both.</li><li><strong>Optional physical test, per pair:</strong> one pair of teacher-approved scissors and two sheets of scrap paper. Clear one safe tabletop or movement lane. Tabletop, teacher-conference, and individual simulation need no physical materials.</li></ul>', "EVIDENCE": "<p>Score the FYF activity plan in place. Collect only the two-page individual test evidence, two revisions, community benefit, and two-career skill transfer.</p>", "MODEL": '<div style="border:1px solid #a9d8d5;border-radius:8px;padding:12px 16px;background:#f1fbfa"><p><strong>Model:</strong> “Children carry a picture card to the matching station, then tear or trace a matching shape. During a tabletop test, the station labels were too similar. I added one large picture and one texture cue to each station. This improves clarity and access.”</p><p><strong>Service model:</strong> “The library volunteer helps a child finish their own work and practices breaking directions into steps. Teachers and museum educators both use that skill with different audiences.”</p><p><strong>Non-example:</strong> “The partner liked it, so no revision is needed.”</p></div>', "FLOW": flow(color, "Warm-up/model · 5", "Gross/fine motor with equal access route.") + flow("#4c8b38", "Read brief · 6", "Safety, access, child-friendly language.") + flow("#1f617a", "Create once in FYF · 17", "Steps, targets, and support stay in the workbook/team plan.") + flow("#d39b22", "Test/revise · 10", "Record evidence and two revisions on the individual surface.") + flow("#1f617a", "Service analysis · 7", "Community benefit and two-career transfer.") + flow(color, "Submit/cleanup · 5", "Two-page response, scissors/scrap/device return."), "MONITOR": "<ul><li><strong>Minute 11:</strong> the FYF activity includes a gross-motor target and fine-motor or access-equivalent target. If one-third treats access as an afterthought, model the picture/texture cue.</li><li><strong>Minute 27:</strong> every team has one testable FYF activity; students can name the action, materials, and one safety/access support without recopied plans.</li><li><strong>Minute 38:</strong> each student's two revisions name test evidence and why each helps.</li><li><strong>Minute 45:</strong> service analysis names a community benefit and one skill used in two careers; redirect personal disclosure to the supplied library scenario.</li><li><strong>Trim/recovery:</strong> use individual simulation and cut sharing. Protect two revisions, service transfer, submission, and material cleanup. Save the same two-page artifact for recovery.</li></ul>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        5: {"TITLE": "Education Evidence Portfolio", "SUBTITLE": "50 minutes · Minor 1 evidence synthesis", "ALERT": "<strong>Minor 1:</strong> score the three-page portfolio with the visible 16-point rubric. Do not score career preference, private history, platform access, or artwork.", "PREP": f'<ul><li><strong>Default:</strong> one device per student, one projector, zero prints. Post {link(files["PORTFOLIO"]["id"], "the three-page portfolio")}, {link(files["RUBRIC"]["id"], "the one-page rubric")}, and private Minor 1 Assignment.</li><li><strong>Paper:</strong> print one three-page portfolio and one one-page landscape rubric per student; set one collection tray.</li><li>Students submit individually. Open current Irving evidence and FYF pp. 218-219. Missing earlier work uses the fixed strip, not reconstruction of four lessons.</li></ul>', "EVIDENCE": "<p>Collect one self-contained portfolio with career/source, preparation/posting, design/revision/service, conclusion/limitation/action, self-score, and revision.</p>", "MODEL": '<div style="border:1px solid #a9d8d5;border-radius:8px;padding:12px 16px;background:#f1fbfa"><p><strong>Complete model strip:</strong> “The August 2026 Irving page lists Education and Training at Irving High, MacArthur, and Nimitz, but it does not guarantee admission or certification. A teacher commonly needs an approved EPP; provider cost and clinical placement still need verification. The Instructional Aide card lists supporting small-group instruction as a responsibility. My learning-space revision added picture cues after the test showed confusing labels. Tutoring service builds the skill of breaking directions into steps. Education currently fits because I value explaining ideas, but I still need to verify a program and observe the daily work.”</p><p><strong>Non-example:</strong> “I like teaching, so the pathway guarantees me a job.”</p></div>', "FLOW": flow(color, "Current/local model · 7", "Listing, workbook context, guarantees.") + flow("#4c8b38", "Evidence setup · 5", "Prior work or fixed missing-work strip.") + flow("#1f617a", "Assemble evidence · 21", "All four rubric jobs.") + flow("#d39b22", "Self-score/revise · 10", "Weakest criterion and visible repair.") + flow(color, "Submit/cleanup · 7", "One private portfolio and material return."), "MONITOR": "<ul><li><strong>Minute 10:</strong> every student has prior evidence or the fixed missing-work strip and one source/date boundary.</li><li><strong>Minute 25:</strong> preparation/posting and design/revision/service evidence are visible. If one-third writes preference only, project the complete model strip.</li><li><strong>Minute 38:</strong> conclusion uses four evidence types, one limit, and one specific next action. Labeled bullets are acceptable; do not cut a rubric job.</li><li><strong>Minute 45:</strong> all four self-scores and one visible revision are complete.</li><li><strong>Trim/recovery:</strong> cut sharing and workbook rereading. Protect every rubric criterion, revision, private submission, and cleanup. Save the same portfolio for a scheduled recovery window; do not add a second packet.</li></ul>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
    }


async def lock_every_file_in_folder(client, folder):
    records = await common.paged(client, f"/folders/{folder['id']}/files")
    locked = []
    for record in records:
        if not record.get("locked"):
            record = await common.api(client, "PUT", f"/files/{record['id']}", data={"locked": "true"})
        locked.append(record)
    return locked


async def main():
    preflight()
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        # Validate the weighted object before the first Canvas mutation.
        mapped_minor, minor_group, rubric_note = await mapped_minor_assignment(client)
        module = await ensure_module(client)
        path = "course files/CCR Materials/6SW/Wk1"
        folder = await common.ensure_folder(client, path)
        files = {key: await common.upload(client, ROOT / "docs/resources/worksheets" / name, path) for key, name in WORKSHEET_FILES.items()}
        folder, folder_files = await assert_folder_files(client, folder, WORKSHEET_FILES.values())
        visual_path = "course files/CCR Materials/6SW/Wk1/Locked Licensed Visuals"
        visual_folder = await common.ensure_folder(client, visual_path)
        visuals = {key: await common.upload(client, ASSETS / name, visual_path) for key, name in VISUAL_FILES.items()}
        visual_folder, visual_folder_files = await assert_folder_files(client, visual_folder, VISUAL_FILES.values())
        quiz = await upsert_quiz(client)
        assignments = {}
        for day, key in {1: "CLASSROOM", 2: "ROUTES", 4: "PLAY"}.items():
            assignments[day] = await upsert_practice_assignment(client, TITLES[day], "<p>Complete privately by annotation, upload, typed labeled responses, or paper. Use one response route, not all routes. This practice is worth 0 points, omitted from the final grade, and unpublished.</p>", files[key]["id"])
        assignments[5] = await require_minor_assignment(client, mapped_minor, minor_group, rubric_note, "<p>Submit the private three-page Education Evidence Portfolio by annotation, upload, or typed labeled response; the teacher may collect the same labeled paper portfolio. Use the visible 16-point rubric. Career preference, artwork, platform access, English mechanics unless meaning is unclear, private service history, and submission mode do not determine the score.</p>", files["PORTFOLIO"]["id"])
        urls = {day: f"/courses/{COURSE_ID}/assignments/{assignment['id']}" for day, assignment in assignments.items()}
        urls[3] = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        students = student_content(files, visuals, urls)
        teachers = teacher_content(files)
        labels = {1: "Community Classroom", 2: "Texas Education Career Routes", 3: "Read Education Job Evidence", 4: "Teach Through Play and Service", 5: "Education Evidence Portfolio"}
        interactions = {1: ("Assignment", assignments[1]["id"], TITLES[1]), 2: ("Assignment", assignments[2]["id"], TITLES[2]), 3: ("Quiz", quiz["id"], TITLES[3]), 4: ("Assignment", assignments[4]["id"], TITLES[4]), 5: ("Assignment", assignments[5]["id"], TITLES[5])}
        order, pages = [], {}
        for day in range(1, 6):
            header_title = f"Day {day} · {labels[day]}"
            header = await prior.upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 6SW Wk1 Day {day} - {labels[day]}"
            student_page = await common.upsert_page(client, student_title, common.render("6sw-wk1-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, **CONTRACTS[day], **students[day]}))
            teacher_title = f"TEACHER: 6SW Wk1 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(client, teacher_title, common.render("6sw-wk1-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **CONTRACTS[day], **teachers[day]}))
            await prior.upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await prior.upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            kind, key, title = interactions[day]
            await prior.upsert_item(client, module["id"], kind, key, title)
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title), (kind, key, title)]
            pages[day] = {"teacher": teacher_page, "student": student_page}

        ordered = await prior.reconcile_module_items(client, module["id"], order)
        if len(ordered) != 20:
            raise RuntimeError(f"Expected 20 exact Education module items; found {len(ordered)}")

        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
        if module.get("published") or len([entry for entry in modules if entry.get("name") == MODULE_NAME]) != 1:
            raise RuntimeError(f"Final Education module invariant failed: published={module.get('published')}")
        for day, pair in pages.items():
            for kind, page in pair.items():
                fresh = await common.api(client, "GET", f"/courses/{COURSE_ID}/pages/{page['url']}")
                if fresh.get("published"):
                    raise RuntimeError(f"Education Day {day} {kind} page is published")
                pair[kind] = fresh
        for day, key in {1: "CLASSROOM", 2: "ROUTES", 4: "PLAY"}.items():
            assignments[day] = await assert_annotation_assignment(client, assignments[day], files[key]["id"])
        assignments[5] = await assert_annotation_assignment(client, assignments[5], files["PORTFOLIO"]["id"], mapped=True)
        if assignments[5].get("assignment_group_id") != minor_group["id"] or RUBRIC_NOTE_MARKER not in (assignments[5].get("description") or ""):
            raise RuntimeError("Final Education Minor group/rubric invariant failed")
        quiz = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
        if quiz.get("published") or quiz.get("quiz_type") != "practice_quiz" or int(quiz.get("allowed_attempts") or 0) != -1:
            raise RuntimeError("Final Education Quiz invariant failed")
        folder, folder_files = await assert_folder_files(client, folder, WORKSHEET_FILES.values())
        visual_folder, visual_folder_files = await assert_folder_files(client, visual_folder, VISUAL_FILES.values())
        print(json.dumps({"module": {"id": module["id"], "published": module["published"]}, "folder": {"id": folder["id"], "locked": folder["locked"], "files_locked": len(folder_files)}, "visual_folder": {"id": visual_folder["id"], "locked": visual_folder["locked"], "files_locked": len(visual_folder_files)}, "files": {key: record["id"] for key, record in files.items()}, "visuals": {key: record["id"] for key, record in visuals.items()}, "quiz": {"id": quiz["id"], "published": quiz.get("published")}, "assignments": {str(day): {"id": assignment["id"], "published": assignment.get("published"), "points": assignment.get("points_possible"), "grading_type": assignment.get("grading_type"), "omit_from_final_grade": assignment.get("omit_from_final_grade")} for day, assignment in assignments.items()}, "pages": {str(day): {kind: {"url": page["url"], "published": page["published"]} for kind, page in pair.items()} for day, pair in pages.items()}, "items": [{"position": entry["position"], "type": entry["type"], "title": entry["title"]} for entry in ordered]}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
