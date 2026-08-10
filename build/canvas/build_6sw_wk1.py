"""Build the unpublished 6SW Week 1 Education evidence module."""

import asyncio
import json
import sys
from urllib.parse import urlencode

import httpx

import build_5sw_wk1 as prior


common = prior.common
COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/6sw/wk1"
MODULE_NAME = "6SW Wk1: Education — Learning Design, Routes, and Service"
TITLES = {
    1: "PRACTICE: Community Classroom Learning-Space Plan",
    2: "PRACTICE: Texas Education Career Routes",
    3: "PRACTICE: Reading Education Job Evidence",
    4: "PRACTICE: Teach Through Play and Service",
    5: "MINOR 1: Education Evidence Portfolio",
}
MINOR_ALIASES = ("MINOR 1: Education Career Evidence Portfolio",)

CONTRACTS = {
    1: {"TOPIC": "Learning Design", "OBJECTIVE": "Students will describe the Education and Training cluster and identify how two careers contribute to a learning-space design.", "TEKS": "d(1)(B), d(1)(C)", "DOL": "FYF Community Classroom concept plus a three-page individual learning-space plan and role explanation.", "I_CAN": "describe the Education and Training cluster and explain how two careers contribute to a learning-space design.", "SHOW": "Complete the FYF Community Classroom concept and the three-page individual plan with a role explanation."},
    2: {"TOPIC": "Career Preparation", "OBJECTIVE": "Students will describe common Texas classroom-teacher requirements, compare two preparation patterns, and identify provider evidence needed before choosing a route.", "TEKS": "d(2)(A), d(2)(B)", "DOL": "Three-page Texas Education Career Routes comparison and evidence-based recommendation.", "I_CAN": "separate common Texas teacher requirements from provider details and compare two preparation patterns.", "SHOW": "Complete the three-page route comparison and make a recommendation that names the evidence still needed."},
    3: {"TOPIC": "Job Evidence", "OBJECTIVE": "Students will identify two Education and Training opportunities and distinguish their responsibilities, skills, qualifications, preparation, and evidence limits.", "TEKS": "d(1)(C), d(2)(A)", "DOL": "Two-page two-card job-evidence comparison plus a retryable practice Quiz.", "I_CAN": "compare two Education and Training opportunities without turning one posting into a universal rule.", "SHOW": "Complete the two-card comparison, state one evidence limit, and use the practice Quiz feedback."},
    4: {"TOPIC": "Service Learning", "OBJECTIVE": "Students will identify an early-childhood education work product, revise it from test evidence, and explain how service benefits a community while building skills transferable to two careers.", "TEKS": "d(1)(C), d(4)(E)", "DOL": "FYF Teach Through Play concept plus a three-page activity, revision, and service analysis.", "I_CAN": "design and revise a child-friendly activity, then explain how service builds a skill used in two careers.", "SHOW": "Complete the FYF concept and three-page companion with two revisions, a community benefit, and two-career skill transfer."},
    5: {"TOPIC": "Career Evidence", "OBJECTIVE": "Students will synthesize career, preparation, job-posting, learning-design, and service evidence to justify an Education and Training direction and next action.", "TEKS": "d(1)(B), d(1)(C), d(2)(A), d(2)(B), d(4)(E)", "DOL": "Three-page Education Career Evidence Portfolio plus a visible one-page 16-point rubric.", "I_CAN": "use this week's evidence to justify an Education and Training direction, limitation, and next action.", "SHOW": "Submit the three-page portfolio, self-score with the one-page rubric, and make one visible revision."},
}


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    found = next((module for module in modules if module.get("name") == MODULE_NAME), None)
    data = {"module[published]": "false", "module[name]": MODULE_NAME}
    if found:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data=data)
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


async def mapped_minor_assignment(client):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    accepted = {TITLES[5], *MINOR_ALIASES}
    matches = [entry for entry in assignments if entry.get("name") in accepted]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one existing mapped Education Minor named in {sorted(accepted)!r}; found {len(matches)}")
    found = matches[0]
    if float(found.get("points_possible") or 0) != 100:
        raise RuntimeError(f"Refusing to modify Education Minor: expected 100 points, found {found.get('points_possible')}")
    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group = next((entry for entry in groups if entry.get("id") == found.get("assignment_group_id")), None)
    if not group or group.get("name") != "Minor Assessments (40%)":
        raise RuntimeError("Refusing to modify Education Minor outside Minor Assessments (40%)")
    return found


async def require_minor_assignment(client, description, attachment_id):
    found = await mapped_minor_assignment(client)
    scoring_note = (
        '<div data-cce-rubric-note="cce-advisory-rubric-v1" '
        'style="border-left:4px solid #0b5f8a;padding:10px 14px;margin:16px 0">'
        '<p><strong>How this is scored:</strong> Use the student-visible Canvas rubric. '
        'Add the raw criterion ratings out of 16, divide by 16, multiply by 100, and round '
        'to the nearest whole point. Enter that percentage as the score out of 100. A score '
        'below 60 follows campus recovery or reassessment policy.</p>'
        '<p>The rubric is advisory in Canvas so its raw total cannot silently replace the '
        '100-point district grade.</p></div>'
    )
    return await common.api(client, "PUT", f"/courses/{COURSE_ID}/assignments/{found['id']}", data={
        "assignment[name]": TITLES[5],
        "assignment[description]": description + scoring_note,
        "assignment[published]": "false",
        "assignment[points_possible]": "100",
        "assignment[grading_type]": "points",
        "assignment[omit_from_final_grade]": "false",
        "assignment[submission_types][]": ["student_annotation", "online_upload", "online_text_entry", "media_recording"],
        "assignment[annotatable_attachment_id]": str(attachment_id),
    })


QUESTIONS = [
    ("Q1 - posting field", "Which line is a responsibility?", "Lead a small-group practice activity using the teacher's plan.", ["Bachelor's degree required.", "Clear communication preferred.", "Two years of experience required."], "Correct. A responsibility is work the employee performs.", "Degree, skill, and experience statements are qualifications or preparation evidence."),
    ("Q2 - preferred", "What does preferred usually mean in a posting?", "Helpful to the employer, but not automatically a minimum requirement", ["Legally required for every employer", "A daily responsibility", "Guaranteed after hiring"], "Correct. Keep preferred separate from required.", "Do not turn preferred language into a universal requirement."),
    ("Q3 - evidence limit", "What can one supplied posting card prove?", "What this scenario says, plus the need to verify a live employer posting before applying", ["Every employer uses the same rules", "The job will still be open next year", "The exact DFW starting salary"], "Correct. A posting is bounded evidence.", "One posting cannot prove universal rules, future availability, or an omitted salary measure."),
    ("Q4 - Texas route", "Which item is one of TEA's common classroom-teacher requirements?", "Complete an approved educator preparation program", ["Favorite three H&L careers", "Use one identical provider price", "Complete Xello Discover learning pathways"], "Correct. Approved preparation is one common requirement.", "Platform clicks and one provider's details are not statewide certification requirements."),
    ("Q5 - local boundary", "What does the current Irving public CTE page verify?", "The district currently lists Education and Training at three comprehensive high schools and Early Childhood Education at Cardwell.", ["Every listed student earns a credential", "Every student is admitted automatically", "All course schedules and placements are guaranteed"], "Correct. Keep a public program listing separate from guarantees.", "The public page does not prove admission, schedule, credential, placement, or travel details."),
]


async def upsert_quiz(client):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    found = next((quiz for quiz in quizzes if quiz.get("title") == TITLES[3]), None)
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
    return await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


def student_content(files, visuals, urls):
    link, step = common.file_link, common.step
    media = lambda pairs: '<h3 style="color:#126b68;border-bottom:3px solid #a9d8d5">Licensed workbook pages</h3>' + ''.join(prior.image_tag(visuals[key]["id"], alt) for key, alt in pairs)
    return {
        1: {"TITLE": "Community Classroom", "PURPOSE": "Turn the FYF brief into a learning-space concept that supports a real science goal.", "TODAY": "<ul><li>describe the cluster;</li><li>choose a learning goal;</li><li>map two Education careers;</li><li>design and revise a learning space.</li></ul>", "READY": f'<p><strong>Start in FYF pp. 213-215.</strong> Use {link(files["CLASSROOM"]["id"], "the three-page individual companion")} or <a href="{urls[1]}">the private annotation activity</a> to plan and explain your contribution.</p>', "MEDIA": media([("p213", "Education and Training cluster opener with three example careers"), ("p214", "Community Classroom scenario, requirements, goals, and science topics"), ("p215", "Community Classroom brainstorm, poster, presentation, and reflection steps")]), "STEPS": step(1, "Choose the learning goal", "<p>Name what third graders will learn, not only a decoration theme.</p>") + step(2, "Map two career contributions", "<p>Name what each worker produces or decides.</p>") + step(3, "Plan and draw", "<p>Show where students investigate, discuss, make, and explain.</p>") + step(4, "Write and revise", "<p>Use one feedback note to improve learning, access, safety, or clarity.</p>"), "EXIT": "<p>Name one career, its contribution, one design choice, and the learning goal it supports.</p>", "DONE": "<ul><li>FYF concept;</li><li>three-page companion;</li><li>two distinct career contributions;</li><li>one visible revision.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> learning goal/meta de aprendizaje · contribute/contribuir · investigate/investigar · access/acceso.</p><p><strong>Use this frame:</strong> The ___ contributes ___ so students can ___.</p>", "FALLBACK": "<p>The locked FYF images plus the companion are the complete no-workbook route. H&amp;L is not required.</p>"},
        2: {"TITLE": "Texas Education Career Routes", "PURPOSE": "Separate Texas requirements from the provider details a student still has to verify.", "TODAY": "<ul><li>read the five common requirements;</li><li>protect the Educational Aide I boundary;</li><li>compare two route patterns;</li><li>recommend what Jordan should verify.</li></ul>", "READY": f'<p>Open {link(files["ROUTES"]["id"], "the three-page route guide")} or <a href="{urls[2]}">the private annotation activity</a>.</p>', "MEDIA": "", "STEPS": step(1, "Mark statewide evidence", "<p>Keep TEA requirements separate from one provider's details.</p>") + step(2, "Read the Aide boundary", "<p>A pathway name alone does not guarantee certification.</p>") + step(3, "Compare route patterns", "<p>Degree timing differs; program quality, clinical route, cost, aid, and timing still require provider evidence.</p>") + step(4, "Advise Jordan", "<p>Cannot decide yet is valid when you name the missing evidence.</p>"), "EXIT": "<p>One statewide requirement, one provider-variable detail, and one question before enrollment.</p>", "DONE": "<ul><li>two common requirements;</li><li>Educational Aide I condition;</li><li>current Irving boundary;</li><li>three provider questions;</li><li>supported recommendation.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> requirement/requisito · provider/proveedor · varies/varía · verify/verificar.</p><p><strong>Use this frame:</strong> Jordan cannot choose from the route label alone. Jordan should compare ___ because ___.</p>", "FALLBACK": "<p>The fixed TEA and Irving evidence is complete. No application, provider contact, payment, Xello, eDynamic, or H&amp;L is required.</p>"},
        3: {"TITLE": "Read Education Job Evidence", "PURPOSE": "Compare two opportunities without turning one posting into a universal career rule.", "TODAY": "<ul><li>read three fixed cards;</li><li>record two;</li><li>compare preparation and transferable skills;</li><li>use Quiz feedback.</li></ul>", "READY": f'<p>Open {link(files["POSTINGS"]["id"], "the two-page evidence guide")} and <a href="{urls[3]}">the retryable practice Quiz</a>.</p>', "MEDIA": "", "STEPS": step(1, "Separate the fields", "<p>A responsibility is work performed; a qualification is a condition for consideration.</p>") + step(2, "Record two cards", "<p>Copy short evidence phrases rather than rewriting the cards.</p>") + step(3, "Compare with limits", "<p>State what appears true in these scenarios and what needs live verification.</p>") + step(4, "Repair with feedback", "<p>Quiz attempts are ungraded and unlimited.</p>"), "EXIT": "<p>One responsibility, one qualification, and one claim the cards cannot prove.</p>", "DONE": "<ul><li>two-card record;</li><li>preparation comparison;</li><li>transferable-skill explanation;</li><li>evidence limit;</li><li>Quiz feedback used.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> responsibility/responsabilidad · qualification/requisito · preferred/preferido · preparation/preparación.</p><p><strong>Use this frame:</strong> Card ___ appears enterable sooner in this scenario because ___. It does not prove ___.</p>", "FALLBACK": "<p>No live job board, account, advertisement click, or application is required.</p>"},
        4: {"TITLE": "Teach Through Play and Service", "PURPOSE": "Design and revise a child-friendly activity, then connect service to skills used across careers.", "TODAY": "<ul><li>use the FYF targets;</li><li>plan and map an activity;</li><li>test through an approved route;</li><li>connect service to two careers.</li></ul>", "READY": f'<p><strong>Start in FYF pp. 216-217.</strong> Use {link(files["PLAY"]["id"], "the three-page companion")} or <a href="{urls[4]}">the private annotation activity</a>.</p>', "MEDIA": media([("p216", "Teach Through Play scenario and gross and fine motor target skills"), ("p217", "Teach Through Play planning, test, improvement, and discussion steps")]), "STEPS": step(1, "Plan safe, child-friendly steps", "<p>Provide a seated, supported, pre-cut, tear, trace, or other access-equivalent option.</p>") + step(2, "Map the activity", "<p>Label materials, movement, fine-motor work, and access or safety support.</p>") + step(3, "Test and revise", "<p>Partner, tabletop, teacher conference, or individual simulation are equal.</p>") + step(4, "Analyze service", "<p>Use a real, planned, or supplied tutoring scenario without private disclosure.</p>"), "EXIT": "<p>Name one revision, one community benefit, and one skill used in two careers.</p>", "DONE": "<ul><li>FYF concept;</li><li>three-page companion;</li><li>two revisions;</li><li>community benefit;</li><li>two-career skill transfer.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> gross motor/motricidad gruesa · fine motor/motricidad fina · service/servicio · revision/revisión.</p><p><strong>Use this frame:</strong> Service benefits the community by ___. In a ___ career, the skill helps ___.</p>", "FALLBACK": "<p>The supplied library-tutoring scenario and individual simulation are the complete absence or no-partner route.</p>"},
        5: {"TITLE": "Education Evidence Portfolio", "PURPOSE": "Use five evidence types to justify a direction, limitation, and next action.", "TODAY": "<ul><li>read the current Irving evidence strip;</li><li>assemble the week's evidence;</li><li>self-score;</li><li>make one visible revision.</li></ul>", "READY": f'<p>Open {link(files["PORTFOLIO"]["id"], "the three-page portfolio")}, {link(files["RUBRIC"]["id"], "the one-page rubric")}, and <a href="{urls[5]}">the private Minor 1 Assignment</a>.</p>', "MEDIA": media([("p218", "Workbook Education and Training program context and I Am Next spotlight"), ("p219", "Workbook program, Educational Aide I, TAFE, endorsement, and field-experience context")]), "STEPS": step(1, "Keep current and workbook claims labeled", "<p>The portfolio includes a current Irving strip. FYF pp. 218-219 remain district-workbook context; time-sensitive promises need verification.</p>") + step(2, "Assemble five evidence types", "<p>Use career, preparation, posting, design/revision, and service evidence. The missing-work strip is an honest fallback.</p>") + step(3, "Conclude with a limit", "<p>Career preference is valid but is not the evidence being scored.</p>") + step(4, "Self-score and repair", "<p>Revise the weakest criterion before private submission.</p>"), "EXIT": "<p>One supported conclusion, one limitation, and one next action.</p>", "DONE": "<ul><li>three-page portfolio;</li><li>current source/date and boundary;</li><li>five evidence types;</li><li>rubric self-score;</li><li>visible revision.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> evidence/evidencia · pathway/programa de estudio · limitation/limitación · next action/próximo paso.</p><p><strong>Use this frame:</strong> The strongest evidence is ___. A limit is ___. My next action is ___ because ___.</p>", "FALLBACK": "<p>The portfolio contains a current Irving strip and a fixed missing-work strip. FYF p. 220 H&amp;L exploration, Xello Discover learning pathways, and eDynamic 7.2 are optional extensions only.</p>"},
    }


def teacher_content(files):
    link, flow = common.file_link, common.flow
    color = "#126b68"
    sources = '<p><a href="https://tea.texas.gov/educators/certification/initial-certification/becoming-classroom-teacher-texas">TEA Classroom Teacher</a> · <a href="https://tea.texas.gov/educators/certification/becoming-educational-aide-texas">TEA Educational Aide</a> · <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte">Irving High School CTE</a>.</p>'
    support = '<p>Point to the visible word bank and complete frame before students write. Accept typing, dictation, annotation, enlarged print, bilingual labels, paper, private rehearsal, and teacher scribing. Score evidence and reasoning, not English mechanics unless meaning is unclear.</p>'
    fallback = '<p>Locked FYF images and fixed companions are the complete absence/platform route. No application, provider contact, public Discussion, personal volunteer disclosure, H&amp;L, Xello, eDynamic, or live job-board work is required.</p>'
    return {
        1: {"TITLE": "Community Classroom", "SUBTITLE": "50 minutes · FYF pp. 213-215 first", "ALERT": "<strong>Trim point:</strong> protect the learning goal, career contributions, and design reasoning; trim decorative poster work first.", "PREP": f'<ul><li>Have students open FYF pp. 213-215.</li><li>Post {link(files["CLASSROOM"]["id"], "the three-page companion")} and private annotation route.</li><li>Choose paper or Canvas for the individual plan; do not require both. Poster materials are optional.</li></ul>', "EVIDENCE": "<p>Collect the FYF concept plus the individual goal, two career contributions, labeled design, booking explanation, and revision.</p>", "FLOW": flow(color, "Warm-up and cluster · 5", "Name one way an Education worker helps someone learn.") + flow("#4c8b38", "Read and model · 10", "Read FYF pp. 213-214; connect one design choice to a science goal.") + flow("#1f617a", "Plan and draw · 22", "Monitor goal, career contributions, sequence, labels, and access or safety.") + flow("#d39b22", "Booking card and feedback · 8", "Peer, self-check, or teacher conference routes are equal.") + flow(color, "Exit · 5", "Career, contribution, design choice, and learning goal."), "MONITOR": "<p>Multiple designs can earn full credit. Require a third-grade science goal, a sequence children can perform, two distinct career contributions, and one design choice tied to learning. Do not score poster polish.</p>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        2: {"TITLE": "Texas Education Career Routes", "SUBTITLE": "50 minutes · state requirements and provider evidence", "ALERT": "<strong>Accuracy boundary:</strong> do not call one preparation route automatically cheaper, faster, paid, unpaid, easier, or better.", "PREP": f'<ul><li>Post {link(files["ROUTES"]["id"], "the three-page fixed guide")} and annotation route.</li><li>Open the current TEA teacher and Educational Aide pages for teacher reference.</li><li>Students do not open applications, contact providers, submit data, or pay fees.</li></ul>', "EVIDENCE": "<p>Collect statewide requirements, Educational Aide boundary, provider questions, and Jordan's evidence-based recommendation.</p>", "FLOW": flow(color, "Warm-up · 5", "What facts would you need before choosing a program?") + flow("#4c8b38", "Five common requirements · 10", "Degree for most certificates, approved EPP, exams, application, and fingerprinting/background review.") + flow("#1f617a", "Route evidence · 15", "Separate statewide facts from provider-variable details.") + flow("#d39b22", "Educational Aide and Irving · 8", "Read exact thresholds and the public-listing boundary.") + flow("#1f617a", "Jordan decision · 7", "Name three provider facts and a supported next step.") + flow(color, "Exit · 5", "Requirement, variable detail, and verification question."), "MONITOR": "<p>Accept cannot decide yet when the student names the missing evidence. High-school Educational Aide I pattern: age 18+, 70+ in at least two specified courses totaling at least three credits, district verification, application steps, and criminal-history/fingerprinting review. Do not turn the pathway name into a credential promise.</p>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        3: {"TITLE": "Read Education Job Evidence", "SUBTITLE": "50 minutes · fixed cards and retryable feedback", "ALERT": "<strong>Evidence boundary:</strong> one posting or fictional card cannot prove universal employer rules, future availability, or DFW starting pay.", "PREP": f'<ul><li>Post {link(files["POSTINGS"]["id"], "the two-page fixed guide")} and the practice Quiz.</li><li>Choose Canvas response or print; do not require both.</li><li>No live job-board account or open search is required.</li></ul>', "EVIDENCE": "<p>Collect the two-card comparison and evidence limit; use the Quiz only for immediate feedback.</p>", "FLOW": flow(color, "Warm-up · 5", "Responsibility or qualification: what is the difference?") + flow("#4c8b38", "Model one field · 10", "Label responsibility, skill, qualification, preparation, and preferred.") + flow("#1f617a", "Read and record two cards · 18", "Students copy short phrases, then explain the comparison.") + flow("#d39b22", "Compare and limit · 10", "Require preparation evidence, skill transfer, and live-verification limit.") + flow(color, "Quiz · 5", "Use feedback and retry.") + flow("#26323a", "Exit · 2", "Responsibility, qualification, and limit."), "MONITOR": "<p>Card A appears enterable sooner only inside the supplied scenarios. Preferred is not automatically required. Do not grade the first Quiz attempt or require duplicate written responses after the comparison.</p>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        4: {"TITLE": "Teach Through Play and Service", "SUBTITLE": "50 minutes · FYF pp. 216-217 first", "ALERT": "<strong>Access boundary:</strong> physical performance, cutting skill, disability, artistry, disclosure, and partner attendance are not scored.", "PREP": f'<ul><li>Have students open FYF pp. 216-217 and post {link(files["PLAY"]["id"], "the three-page companion")}.</li><li>If offering a physical test, provide teacher-approved scissors, scrap paper, and clear movement space.</li><li>Keep tabletop, conference, and individual simulation routes equally available.</li></ul>', "EVIDENCE": "<p>Collect the child-friendly sequence, map, two evidence-based revisions, community benefit, and two-career skill transfer.</p>", "FLOW": flow(color, "Warm-up and model · 5", "Demonstrate gross versus fine motor without grading ability.") + flow("#4c8b38", "Read the brief · 7", "Set safety and access-equivalent routes.") + flow("#1f617a", "Plan and map · 18", "Monitor directions, materials, targets, and access support.") + flow("#d39b22", "Test and revise · 10", "Use partner, tabletop, conference, or individual simulation.") + flow("#1f617a", "Service analysis · 7", "Use real, planned, or supplied library-tutoring evidence.") + flow(color, "Exit · 3", "Revision, community benefit, and skill transfer."), "MONITOR": "<p>Require both supplied targets or an access-equivalent fine-motor route, two specific revisions, one community benefit, and a skill applied in two careers. The supplied tutoring scenario prevents forced personal disclosure.</p>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        5: {"TITLE": "Education Evidence Portfolio", "SUBTITLE": "50 minutes · Minor 1 evidence synthesis", "ALERT": "<strong>Minor 1:</strong> score the three-page portfolio with the visible 16-point rubric. Do not score career preference, private history, platform access, or artwork.", "PREP": f'<ul><li>Post {link(files["PORTFOLIO"]["id"], "the three-page portfolio")}, {link(files["RUBRIC"]["id"], "the one-page rubric")}, and private Minor 1 Assignment.</li><li>Open the current Irving CTE page and FYF pp. 218-219.</li><li>Keep the Assignment unpublished until teacher transfer/review.</li></ul>', "EVIDENCE": "<p>Collect one self-contained portfolio with career/source, preparation/posting, design/revision/service, conclusion/limitation/action, self-score, and revision.</p>", "FLOW": flow(color, "Current local evidence · 8", "Separate the current public listing from workbook context and guarantees.") + flow("#4c8b38", "Workbook comparison · 5", "Read FYF pp. 218-219; label time-sensitive claims.") + flow("#1f617a", "Assemble evidence · 22", "Use Days 1-4 or the fixed missing-work strip.") + flow("#d39b22", "Self-score and revise · 10", "Use all four criteria and repair the weakest one.") + flow(color, "Exit · 5", "Supported conclusion, limitation, and next action."), "MONITOR": "<p>Current listing: Education and Training at Irving High, MacArthur, and Nimitz; Early Childhood Education at Cardwell. Require source/date, local boundary, design evidence, preparation distinction, posting fact, service value, limitation, and next action. Use the missing-work strip honestly; do not invent student history.</p>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
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
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        # Validate the weighted object before the first Canvas mutation.
        await mapped_minor_assignment(client)
        module = await ensure_module(client)
        path = "course files/CCR Materials/6SW/Wk1"
        folder = await common.ensure_folder(client, path)
        names = {"CLASSROOM": "6sw-wk1-community-classroom-plan.pdf", "ROUTES": "6sw-wk1-texas-education-routes.pdf", "POSTINGS": "6sw-wk1-education-job-evidence.pdf", "PLAY": "6sw-wk1-teach-through-play-service.pdf", "PORTFOLIO": "6sw-wk1-education-evidence-portfolio.pdf", "RUBRIC": "6sw-wk1-education-portfolio-rubric.pdf"}
        files = {key: await common.upload(client, ROOT / "docs/resources/worksheets" / name, path) for key, name in names.items()}
        visual_path = "course files/CCR Materials/6SW/Wk1/Locked Licensed Visuals"
        visual_folder = await common.ensure_folder(client, visual_path)
        visuals = {f"p{page}": await common.upload(client, ASSETS / f"fyf-p{page}.jpg", visual_path) for page in range(213, 220)}
        quiz = await upsert_quiz(client)
        assignments = {}
        for day, key in {1: "CLASSROOM", 2: "ROUTES", 4: "PLAY"}.items():
            assignments[day] = await common.upsert_assignment(client, TITLES[day], "<p>Complete privately by annotation, upload, typed labeled responses, or paper. Use one response route, not all routes.</p>", ["student_annotation", "online_upload", "online_text_entry"], files[key]["id"])
        assignments[5] = await require_minor_assignment(client, "<p>Submit the private three-page Education Evidence Portfolio. Use the visible 16-point rubric. Career preference, artwork, platform access, English mechanics unless meaning is unclear, private service history, and submission mode do not determine the score.</p>", files["PORTFOLIO"]["id"])
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

        def matches_item(entry, kind, key):
            return entry.get("type") == kind and ((kind == "SubHeader" and entry.get("id") == key) or (kind == "Page" and entry.get("page_url") == key) or (kind in ("Assignment", "Quiz") and entry.get("content_id") == key))

        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        keep_ids = set()
        for kind, key, _title in order:
            match = next((entry for entry in items if entry["id"] not in keep_ids and matches_item(entry, kind, key)), None)
            if not match:
                raise RuntimeError(f"Missing expected Education module item: {kind} {key}")
            keep_ids.add(match["id"])
        for entry in items:
            if entry["id"] not in keep_ids:
                await common.api(client, "DELETE", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{entry['id']}")
        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(entry for entry in items if matches_item(entry, kind, key))
            await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}", data={"module_item[position]": position, "module_item[title]": title})
        final = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        ordered = sorted(final, key=lambda entry: entry.get("position", 0))
        if len(ordered) != len(order):
            raise RuntimeError(f"Expected {len(order)} Education module items; found {len(ordered)}")
        for position, ((kind, key, _title), entry) in enumerate(zip(order, ordered), 1):
            if entry.get("position") != position or not matches_item(entry, kind, key):
                raise RuntimeError(f"Education module order mismatch at position {position}")

        folder_files = await lock_every_file_in_folder(client, folder)
        visual_files = await lock_every_file_in_folder(client, visual_folder)
        folder = await common.api(client, "GET", f"/folders/{folder['id']}")
        visual_folder = await common.api(client, "GET", f"/folders/{visual_folder['id']}")
        if not folder.get("locked") or not visual_folder.get("locked") or any(not record.get("locked") for record in folder_files + visual_files):
            raise RuntimeError("Every Education support folder and file must remain locked")
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        print(json.dumps({"module": {"id": module["id"], "published": module["published"]}, "folder": {"id": folder["id"], "locked": folder["locked"]}, "visual_folder": {"id": visual_folder["id"], "locked": visual_folder["locked"]}, "files": {key: record["id"] for key, record in files.items()}, "visuals": {key: record["id"] for key, record in visuals.items()}, "quiz": {"id": quiz["id"], "published": quiz.get("published")}, "assignments": {str(day): {"id": assignment["id"], "published": assignment.get("published"), "points": assignment.get("points_possible"), "grading_type": assignment.get("grading_type"), "omit_from_final_grade": assignment.get("omit_from_final_grade")} for day, assignment in assignments.items()}, "pages": {str(day): {kind: {"url": page["url"], "published": page["published"]} for kind, page in pair.items()} for day, pair in pages.items()}, "items": [{"position": entry["position"], "type": entry["type"], "title": entry["title"]} for entry in ordered]}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
