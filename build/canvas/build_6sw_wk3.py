"""Build the unpublished 6SW Week 3 marketing module."""

import asyncio
import json
import re
import sys
from urllib.parse import urlencode

import httpx

import build_5sw_wk1 as prior
from configure_assessment_map import SUBMISSION_LINK_MARKER


common = prior.common
COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/6sw/wk3"
MODULE_NAME = "6SW Wk3: Marketing - Audience, Entrepreneurship, and Data"
RUBRIC_NOTE_MARKER = 'data-cce-rubric-note="cce-advisory-rubric-v1"'
WORKSHEET_FILES = {
    "CLICK": "6sw-wk3-click-factor-campaign.pdf",
    "CHANGE": "6sw-wk3-written-communication-and-change.pdf",
    "EXPERT": "6sw-wk3-expert-edge-plan.pdf",
    "FAMILY": "6sw-wk3-family-fun-pass-analysis.pdf",
    "BRIEF": "6sw-wk3-marketing-evidence-brief.pdf",
    "RUBRIC": "6sw-wk3-marketing-evidence-rubric.pdf",
}
VISUAL_FILES = {f"p{page}": f"fyf-p{page}.jpg" for page in (147, 148, 222, 223, 224, 225, 226, 227, 228, 229, 230)}
TITLES = {
    1: "PRACTICE: Click Factor Audience Test and Revision",
    2: "PRACTICE: Written Communication and Changing Conditions",
    3: "PRACTICE: Expert Edge Opportunity and Revision",
    4: "PRACTICE: Family Fun Pass Evidence Decision",
    5: "MINOR 3: Ethical Marketing Evidence Brief",
}
QUIZ_TITLE = "PRACTICE QUIZ: Marketing Evidence and Boundaries"
QUIZ_ALIASES = (TITLES[2],)
MINOR_ALIASES = ("MINOR 3: Marketing Evidence Brief",)


def preflight():
    required = [
        ROOT / "build/canvas/templates/6sw-wk3-student.html",
        ROOT / "build/canvas/templates/6sw-wk3-teacher.html",
        *(ROOT / "docs/resources/worksheets" / name for name in WORKSHEET_FILES.values()),
        *(ASSETS / name for name in VISUAL_FILES.values()),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"6SW Wk3 preflight missing required files: {missing}")

CONTRACTS = {
    1: {
        "TOPIC": "Audience and Message",
        "OBJECTIVE": "Students will identify a marketing career opportunity and use supplied product evidence to create, test, and revise a truthful audience-specific call to action.",
        "TEKS": "d(1)(C)",
        "DOL": "Completed FYF Click Factor work plus a two-page individual audience test, visible revision, and career/work-product connection.",
        "I_CAN": "identify a marketing career and use product evidence to create, test, and revise a truthful call to action for an audience.",
        "SHOW": "Complete Click Factor and the two-page companion with an audience-message chain, test evidence, visible revision, and career connection.",
    },
    2: {
        "TOPIC": "Changing Conditions",
        "OBJECTIVE": "Students will identify a marketing career opportunity and analyze how one economic condition and one societal or technology condition could change marketing work and preparation.",
        "TEKS": "d(1)(C), d(5)(C)",
        "DOL": "Completed FYF Little Library message plus a two-page individual revision, fixed-source condition comparison, preparation recommendation, and career connection.",
        "I_CAN": "identify a marketing career and explain how economic and societal or technology changes could affect the work and preparation.",
        "SHOW": "Complete the FYF message and two-page companion with a visible revision, two distinct condition effects, preparation recommendation, and career connection.",
    },
    3: {
        "TOPIC": "Entrepreneurship",
        "OBJECTIVE": "Students will identify a fictional entrepreneurial opportunity by connecting a skill, audience need, deliverable, responsibility, and risk to a marketing career.",
        "TEKS": "d(1)(C), d(3)(I)",
        "DOL": "Completed FYF Expert Edge plan plus a two-page individual opportunity, responsibility/risk, private test, revision, and career connection.",
        "I_CAN": "define entrepreneurship by connecting a need, deliverable, responsibility, and risk to a fictional opportunity and marketing career.",
        "SHOW": "Complete Expert Edge and the two-page companion with an opportunity chain, responsibility/risk/control, private test, visible revision, and career connection.",
    },
    4: {
        "TOPIC": "Data-Informed Decisions",
        "OBJECTIVE": "Students will identify how a marketing career uses preference, performance, and qualitative evidence to choose a strategy, name a limitation, and plan a next test.",
        "TEKS": "d(1)(C)",
        "DOL": "Completed FYF Family Fun Pass work plus a two-page individual goal, three-point evidence stack, decision rule, limitation, next test, and career connection.",
        "I_CAN": "explain how a marketing worker uses different evidence to choose a strategy, name a limit, and plan a next test.",
        "SHOW": "Complete the FYF decision and two-page companion with a goal, three evidence points, decision rule, limitation, next test, and career connection.",
    },
    5: {
        "TOPIC": "Ethical Marketing",
        "OBJECTIVE": "Students will create an evidence brief that identifies a marketing career and entrepreneurial opportunity, explains an ethical audience message and data-informed decision, and analyzes distinct effects of economic and societal or technology change.",
        "TEKS": "d(1)(C), d(3)(I), d(5)(C)",
        "DOL": "Private four-page Marketing Evidence Brief plus a 16-point self-score and one visible evidence-based revision.",
        "I_CAN": "use this week's evidence to explain an ethical marketing decision, entrepreneurial opportunity, career connection, and two different changing-condition effects.",
        "SHOW": "Submit the private four-page Marketing Evidence Brief, complete the 16-point self-score, and make one visible evidence-based revision.",
    },
}


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    matches = [module for module in modules if module.get("name") == MODULE_NAME]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one {MODULE_NAME!r} module; found {len(matches)}")
    data = {"module[published]": "false", "module[name]": MODULE_NAME}
    if matches:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{matches[0]['id']}", data=data)
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


async def mapped_minor_assignment(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    module_matches = [entry for entry in modules if entry.get("name") == MODULE_NAME]
    if len(module_matches) > 1:
        raise RuntimeError(f"Duplicate Marketing modules: {[entry['id'] for entry in module_matches]}")
    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group_matches = [entry for entry in groups if entry.get("name") == "Minor Assessments (40%)"]
    if len(group_matches) != 1:
        raise RuntimeError(f"Expected exactly one Minor Assessments (40%) group; found {len(group_matches)}")
    group = group_matches[0]
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    for day in (1, 2, 3, 4):
        practice_matches = [entry for entry in assignments if entry.get("name") == TITLES[day]]
        if len(practice_matches) > 1:
            raise RuntimeError(f"Duplicate assignments named {TITLES[day]!r}: {[entry['id'] for entry in practice_matches]}")
    accepted = {TITLES[5], *MINOR_ALIASES}
    matches = [entry for entry in assignments if entry.get("name") in accepted]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one existing mapped Marketing Minor named in {sorted(accepted)!r}; found {len(matches)}")
    found = matches[0]
    rubric_note = re.search(
        r'<div data-cce-rubric-note="cce-advisory-rubric-v1".*?</div>',
        found.get("description") or "",
        flags=re.I | re.S,
    )
    if (
        found.get("assignment_group_id") != group.get("id")
        or found.get("published") is not False
        or float(found.get("points_possible") or 0) != 100
        or found.get("grading_type") != "points"
        or found.get("omit_from_final_grade") is not False
        or rubric_note is None
    ):
        raise RuntimeError("Mapped Marketing Minor failed prewrite group/grade/rubric/unpublished checks")
    return found, group, rubric_note.group(0)


async def require_minor_assignment(client, found, group, scoring_note, description):
    assignment = await common.api(client, "PUT", f"/courses/{COURSE_ID}/assignments/{found['id']}", data={
        "assignment[name]": TITLES[5],
        "assignment[description]": description + scoring_note,
        "assignment[published]": "false",
        "assignment[points_possible]": "100",
        "assignment[grading_type]": "points",
        "assignment[omit_from_final_grade]": "false",
        "assignment[assignment_group_id]": str(group["id"]),
        "assignment[submission_types][]": ["online_upload", "online_text_entry"],
    })
    assignment = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignment['id']}")
    if (
        assignment.get("assignment_group_id") != group.get("id")
        or assignment.get("published") is not False
        or float(assignment.get("points_possible") or 0) != 100
        or assignment.get("grading_type") != "points"
        or assignment.get("omit_from_final_grade") is not False
        or RUBRIC_NOTE_MARKER not in (assignment.get("description") or "")
        or set(assignment.get("submission_types") or []) != {"online_upload", "online_text_entry"}
    ):
        raise RuntimeError("Marketing Minor failed post-update assignment invariant")
    return assignment


async def upload_locked(client, path, folder_path):
    uploaded = await common.upload(client, path, folder_path)
    record = await common.api(client, "GET", f"/files/{uploaded['id']}")
    if record.get("locked") is not True:
        record = await common.api(client, "PUT", f"/files/{record['id']}", data={"locked": "true"})
    if record.get("locked") is not True:
        raise RuntimeError(f"Canvas did not lock {path.name!r}")
    return record


async def assert_folder_files(client, folder, expected_names):
    folder = await common.lock_folder_files(client, folder)
    records = await common.paged(client, f"/folders/{folder['id']}/files")
    actual = {record.get("display_name") or record.get("filename") for record in records}
    if folder.get("locked") is not True or any(record.get("locked") is not True for record in records):
        raise RuntimeError(f"Marketing folder lock invariant failed for {folder['id']}")
    missing = set(expected_names) - actual
    if missing:
        raise RuntimeError(f"Marketing folder is missing required files: {sorted(missing)!r}")
    return folder, records


async def assert_annotation_assignment(client, assignment, source_attachment_id):
    fresh = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignment['id']}")
    source = await common.api(client, "GET", f"/files/{source_attachment_id}")
    clone_id = int(fresh.get("annotatable_attachment_id") or 0)
    clone = await common.api(client, "GET", f"/files/{clone_id}") if clone_id else {}
    if clone and clone.get("locked") is not True:
        clone = await common.api(client, "PUT", f"/files/{clone_id}", data={"locked": "true"})
    if (
        fresh.get("published") is not False
        or float(fresh.get("points_possible") or 0) != 0
        or fresh.get("grading_type") != "percent"
        or fresh.get("omit_from_final_grade") is not True
        or set(fresh.get("submission_types") or []) != {"student_annotation", "online_upload", "online_text_entry"}
        or not clone_id
        or source.get("locked") is not True
        or clone.get("locked") is not True
        or clone.get("filename") != source.get("filename")
        or int(clone.get("size") or -1) != int(source.get("size") or -2)
    ):
        raise RuntimeError(f"Marketing practice Assignment invariant failed for {fresh.get('name')!r}")
    return fresh


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


QUESTIONS = [
    ("Q1 - ethical CTA", "Which call to action crosses the lesson boundary?", "Only 2 left - guaranteed! when neither claim is verified", ["See the five dessert skills you will practice.", "Compare the weekly snack-box options.", "Choose the car-wash plan that fits your schedule."], "Correct. Urgency, scarcity, and guarantees must be truthful.", "Accurate product information and direct comparison can support an informed choice."),
    ("Q2 - salary label", "What does the $76,950 figure mean in this lesson?", "BLS May 2024 U.S. median pay for Market Research Analysts and Marketing Specialists", ["Guaranteed DFW starting pay", "The pay for every marketing worker", "A student's expected first salary"], "Correct. Measure, date, geography, and occupation stay visible.", "It is a dated national median, not local starting pay or a guarantee."),
    ("Q3 - openings and growth", "Which statement uses the BLS evidence accurately?", "The occupation is projected to grow 7% from 2024-34 and average about 87,200 openings per year; these are different measures.", ["There will be exactly 87,200 new jobs every year.", "Every graduate has a 7% chance of a job.", "The figures prove a DFW shortage."], "Correct. Growth and average annual openings are different measures.", "The figures do not prove individual outcomes or a local shortage."),
    ("Q4 - changing conditions", "Which example is a societal or technology condition rather than an economic condition?", "Customers expect accessible mobile content and clear privacy choices.", ["A company cuts its campaign budget after customers spend less.", "A business delays hiring because sales fall.", "A store reduces promotion spending during a slowdown."], "Correct. Audience expectations, access, privacy, and tools are societal or technology conditions.", "Spending, budgets, demand, and hiring are economic effects in this comparison."),
    ("Q5 - platform boundary", "What counts as the required evidence this week?", "The private Canvas or paper reasoning and revision; H&L, Xello, eDynamic, Canva, and Adobe Express are optional supports.", ["Two H&L favorites", "A Xello School Subjects completion screen", "A public social-media post"], "Correct. Standards evidence is reasoning and revision, not a platform click.", "No public post or supplemental platform completion is required."),
]


async def upsert_quiz(client):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    matches = [quiz for quiz in quizzes if quiz.get("title") in {QUIZ_TITLE, *QUIZ_ALIASES}]
    exact = [quiz for quiz in matches if quiz.get("title") == QUIZ_TITLE]
    found = exact[0] if exact else (matches[0] if matches else None)
    for duplicate in matches:
        if found and duplicate.get("id") == found.get("id"):
            continue
        await common.api(client, "DELETE", f"/courses/{COURSE_ID}/quizzes/{duplicate['id']}")
    data = {
        "quiz[title]": QUIZ_TITLE,
        "quiz[description]": "<p>Ungraded, unlimited-retry practice on ethical communication, current source labels, changing conditions, and platform boundaries.</p>",
        "quiz[quiz_type]": "practice_quiz",
        "quiz[published]": "false",
        "quiz[allowed_attempts]": "-1",
        "quiz[show_correct_answers]": "true",
        "quiz[shuffle_answers]": "false",
    }
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
        raise RuntimeError("Marketing practice Quiz question set mismatch")
    fields = []
    for name in expected:
        fields.extend([("order[][id]", str(by_name[name]["id"])), ("order[][type]", "question")])
    await common.api(client, "POST", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/reorder", content=urlencode(fields), headers={"Content-Type": "application/x-www-form-urlencoded"})
    final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    if [entry.get("question_name") for entry in final_questions] != expected:
        raise RuntimeError("Marketing practice Quiz order mismatch")
    final = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
    if (
        final.get("published") is not False
        or final.get("quiz_type") != "practice_quiz"
        or int(final.get("allowed_attempts") or 0) != -1
        or final.get("shuffle_answers") is not False
    ):
        raise RuntimeError("Marketing practice Quiz state mismatch")
    return final


def student_content(files, visuals, urls):
    link, step = common.file_link, common.step
    media = lambda pairs: '<h3 style="color:#9a4d19;border-bottom:3px solid #efc5aa">Licensed workbook pages</h3>' + ''.join(prior.image_tag(visuals[key]["id"], alt) for key, alt in pairs)
    minor_panel = (
        f'<section data-cce-marker="{SUBMISSION_LINK_MARKER}" '
        'style="border:2px solid #155d7a;border-radius:12px;padding:18px 20px;margin:24px 0;background:#eef8fc">'
        '<h3 style="margin:0 0 8px;color:#155d7a">Submit your minor evidence</h3>'
        '<p style="margin:0 0 14px">Use the visible rubric to check your work, then submit through this private Canvas assignment. Your teacher will tell you whether to type, upload a file, or turn in the paper route.</p>'
        f'<p style="margin:0"><a href="{urls[5]}" style="display:inline-block;background:#155d7a;color:#fff;padding:11px 18px;border-radius:6px;text-decoration:none;font-weight:700" data-api-endpoint="/api/v1{urls[5]}" data-api-returntype="Assignment">Open {TITLES[5]}</a></p></section>'
    )
    return {
        1: {"TITLE": "Click Factor", "PURPOSE": "Use a supplied product brief to write, test, and revise a truthful call to action for one audience.", "TODAY": "<ul><li>compare five CTA approaches;</li><li>choose one supplied product;</li><li>build, test, and revise one ad;</li><li>connect the work to a marketing career.</li></ul>", "READY": f'<p><strong>Start in FYF pp. 225-227 and 230.</strong> Sample the CTA approaches, then choose one product for the complete ad. Use {link(files["CLICK"]["id"], "the two-page audience-test companion")} or <a href="{urls[1]}">the private annotation activity</a> for the evidence the workbook does not collect.</p>', "MEDIA": media([("p225", "Click Factor introduction with two ad examples"), ("p226", "Five CTA approaches and the Local Car Wash and Cooking Class prompts"), ("p227", "After-School Snack Box and Fishing Gear prompts"), ("p230", "Full-page ad mock-up requirements and planning space")]), "STEPS": step(1, "Sample and choose", "<p>Compare the supplied CTA approaches. Draft two truthful CTAs for one chosen product; your teacher may supply the other comparison examples.</p>") + step(2, "Build one ad", "<p>Complete the FYF mock-up with a headline, accurate description, CTA, clear hierarchy, and one access feature.</p>") + step(3, "Run the truth and three-second checks", "<p>Do not invent scarcity, discounts, popularity, testimonials, deadlines, guarantees, or collect real audience data.</p>") + step(4, "Revise and connect", "<p>Keep the before and after. Name one marketing career, work product, and next use of the test evidence.</p>"), "EXIT": "<p>Name the career, work product, and revision that made the message clearer or more accurate.</p>", "DONE": "<ul><li>sampled CTA approaches and one complete FYF ad or no-workbook route;</li><li>audience-message chain;</li><li>truth/access/privacy check;</li><li>three-second test;</li><li>visible revision and career connection.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> audience/audiencia · accurate/exacto · benefit/beneficio · evidence/evidencia.</p><p><strong>Use this frame:</strong> This CTA fits <strong>[audience]</strong> because <strong>[supplied fact or need]</strong>. I changed <strong>[revision]</strong> so <strong>[audience effect]</strong>.</p>", "FALLBACK": "<p>The locked FYF pages plus the two-page companion are the complete no-workbook route. No real campaign, account, link, QR code, purchase, tracking, audience survey, public post, H&amp;L, Xello, or design platform is required.</p>"},
        2: {"TITLE": "Written Communication and Changing Conditions", "PURPOSE": "Revise a clear fictional message and compare how two different conditions could change marketing work and preparation.", "TODAY": "<ul><li>complete and revise the Little Library message;</li><li>read current BLS evidence;</li><li>compare an economic condition with a societal or technology condition;</li><li>choose a preparation response.</li></ul>", "READY": f'<p><strong>Start in FYF pp. 147-148.</strong> Use {link(files["CHANGE"]["id"], "the two-page revision and changing-conditions companion")} or <a href="{urls[2]}">the private annotation activity</a> for the evidence the workbook does not collect. Use the <a href="{urls["QUIZ"]}">retryable practice Quiz</a> only for feedback.</p>', "MEDIA": media([("p147", "Written Communication Little Library scenario and brainstorm"), ("p148", "Four effective-writing moves and fictional social-message space")]), "STEPS": step(1, "Write for purpose and audience", "<p>State the fictional status, important detail, safe action, and one access need.</p>") + step(2, "Revise visibly", "<p>Record one clarity, privacy, or accessibility change.</p>") + step(3, "Read the career card", "<p>$76,950 May 2024 U.S. median; bachelor's typical; 7% projected growth, 2024-34; about 87,200 openings per year. These are not DFW starting pay or guarantees.</p>") + step(4, "Separate the conditions", "<p>Economic effects concern spending, budgets, demand, or hiring. Societal/technology effects concern audience behavior, tools, channels, access, privacy, or human review.</p>"), "EXIT": "<p>Use the practice Quiz feedback or state one condition effect, one reason, and one preparation action.</p>", "DONE": "<ul><li>FYF message or complete no-workbook route;</li><li>visible revision;</li><li>bounded BLS conclusion;</li><li>two distinct condition effects;</li><li>preparation recommendation and career connection;</li><li>one private response route submitted.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> purpose/propósito · budget/presupuesto · demand/demanda · channel/canal · privacy/privacidad.</p><p><strong>Use this frame:</strong> Economic pressure may change <strong>[work/hiring]</strong> because <strong>[evidence]</strong>. The societal or technology change instead requires <strong>[skill/action]</strong> because <strong>[reason]</strong>.</p>", "FALLBACK": "<p>The locked FYF pages plus the two-page companion are the complete route. Do not make a real post or enter real names, locations, handles, photos, or contact information. Submit one private annotation, upload, typed-label, or paper route. The Quiz is feedback, not duplicate evidence.</p>"},
        3: {"TITLE": "Expert Edge", "PURPOSE": "Turn a skill into a fictional entrepreneurial opportunity while keeping responsibility, risk, and privacy visible.", "TODAY": "<ul><li>complete the FYF service plan;</li><li>define the opportunity;</li><li>name responsibility, risk, and control;</li><li>test, revise, and connect the plan to a marketing career.</li></ul>", "READY": f'<p><strong>Start in FYF pp. 222-224.</strong> Use {link(files["EXPERT"]["id"], "the two-page opportunity and revision companion")} or <a href="{urls[3]}">the private annotation activity</a> for the evidence the workbook does not collect.</p>', "MEDIA": media([("p222", "Expert Edge scenario and skill-to-need brainstorm"), ("p223", "Consulting service, mission, fictional price, and add-on plan"), ("p224", "Original logo, private pitch, feedback, and career discussion")]), "STEPS": step(1, "Build the FYF service", "<p>Connect a skill, audience, need, deliverable, mission, fictional unit/price, and add-on.</p>") + step(2, "Define the opportunity", "<p>Explain why the idea responds to a need rather than only naming a hobby or topic.</p>") + step(3, "Keep responsibility and risk visible", "<p>Name one owner responsibility, one uncertainty, and one control or boundary.</p>") + step(4, "Test and revise privately", "<p>Partner, teacher, or self-check. Oral delivery and logo polish are optional and not scored.</p>"), "EXIT": "<p>Explain why the idea is an opportunity and name one responsibility or risk control.</p>", "DONE": "<ul><li>FYF work or complete no-workbook route;</li><li>opportunity chain;</li><li>responsibility/risk/control;</li><li>private test and visible revision;</li><li>career/work-product connection.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> opportunity/oportunidad · deliverable/producto entregable · responsibility/responsabilidad · risk/riesgo.</p><p><strong>Use this frame:</strong> This is an opportunity because <strong>[audience]</strong> needs <strong>[deliverable]</strong>. The owner must <strong>[responsibility]</strong> and control <strong>[risk]</strong> by <strong>[action]</strong>.</p>", "FALLBACK": "<p>This is not a launch. No sale, payment, booking, contact, account, public promotion, client data, income promise, or copied mark is required. The locked pages and companion are the complete no-workbook route.</p>"},
        4: {"TITLE": "Family Fun Pass", "PURPOSE": "Use three evidence types to choose a strategy, explain a conflict, and plan the next test.", "TODAY": "<ul><li>read FYF p. 229, then p. 228;</li><li>name the campaign goal;</li><li>build a three-point evidence stack;</li><li>state a limitation, next test, and career connection.</li></ul>", "READY": f'<p><strong>Start with the data on FYF p. 229, then complete the decision work on p. 228.</strong> Use {link(files["FAMILY"]["id"], "the two-page evidence-decision companion")} or <a href="{urls[4]}">the private annotation activity</a> for the individual evidence the workbook does not collect.</p>', "MEDIA": media([("p229", "Family Fun Pass audience-preference and past-campaign tables with focus-group quotes"), ("p228", "Strategy choices, pitch space, and class-discussion prompts")]), "STEPS": step(1, "Set the goal first", "<p>Choose awareness, clicks, sales, trust, or broad age reach.</p>") + step(2, "Build an evidence stack", "<p>Use two exact numbers and one quote or pattern. State what each one supports.</p>") + step(3, "Resolve a conflict", "<p>Name the decision rule that makes one evidence type matter more for this goal.</p>") + step(4, "Keep uncertainty visible", "<p>Name one limit, one small next test, the result to measure, and the worker who would use it.</p>"), "EXIT": "<p>State the strategy, goal, strongest number, one limit, and one result to test next.</p>", "DONE": "<ul><li>FYF work or complete no-workbook route;</li><li>goal and three evidence points;</li><li>decision rule;</li><li>limitation and next test;</li><li>career/work-product connection.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> goal/meta · strategy/estrategia · measure/medida · evidence/evidencia · limitation/limitación.</p><p><strong>Use this frame:</strong> For the goal <strong>[goal]</strong>, I recommend <strong>[strategy]</strong> because <strong>[number]</strong> shows <strong>[meaning]</strong>. The limit is <strong>[limit]</strong>, so I would test <strong>[next result]</strong>.</p>", "FALLBACK": "<p>The locked FYF pages plus the two-page companion are the complete no-workbook route. The data are a fictional scenario, not a universal claim about age groups. No site, login, public pitch, or open-web research is required.</p>"},
        5: {"TITLE": "Ethical Marketing Evidence Brief", "PURPOSE": "Use the week's strongest evidence to explain an ethical marketing decision, entrepreneurial opportunity, career connection, and two different changing-condition effects.", "TODAY": "<ul><li>select evidence from the week;</li><li>complete four reasoning sections;</li><li>self-score with the 16-point rubric;</li><li>make one visible evidence-based revision.</li></ul>", "READY": f'<p>Open {link(files["BRIEF"]["id"], "the four-page Marketing Evidence Brief")} and {link(files["RUBRIC"]["id"], "the two-page Minor 3 rubric")}. Use completed FYF work and companions as evidence.</p>', "MEDIA": "", "STEPS": step(1, "Career, audience, and ethical message", "<p>Name the worker, work product, audience, message choice, boundary, and tested revision.</p>") + step(2, "Entrepreneurship and responsibility", "<p>State the opportunity, need, deliverable, responsibility, risk, control, and price limit.</p>") + step(3, "Data and changing conditions", "<p>Use two numbers and one quote/pattern, then keep economic and societal/technology effects distinct.</p>") + step(4, "Self-score and revise", "<p>Use all four criteria. Keep the original and changed evidence visible.</p>") + minor_panel, "EXIT": "<p>Name your strongest evidence, weakest criterion, and the revision that improved it.</p>", "DONE": "<ul><li>all four brief sections;</li><li>current source labels;</li><li>economic and societal/technology effects kept distinct;</li><li>16-point self-score;</li><li>visible revision and private submission.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> synthesis/síntesis · opportunity/oportunidad · strategy/estrategia · source/fuente · revise/revisar.</p><p><strong>Use this frame:</strong> My evidence supports <strong>[decision]</strong> because <strong>[number, quote, or test]</strong>. I revised <strong>[part]</strong> after checking <strong>[criterion]</strong>.</p>", "FALLBACK": "<p>The four-page brief includes recap prompts. Accept typing, dictation, annotation, enlarged print, or paper. No live/public pitch, H&amp;L favorite, Xello completion, eDynamic progress, real campaign, or personal business disclosure is required.</p>"},
    }


def teacher_content(files):
    link, flow = common.file_link, common.flow
    color = "#9a4d19"
    sources = '<p><a href="https://www.bls.gov/ooh/business-and-financial/market-research-analysts.htm">BLS Market Research Analysts and Marketing Specialists</a> · <a href="https://www.ftc.gov/business-guidance/advertising-marketing">FTC Advertising and Marketing</a> · <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte/macarthur-high-school">Irving ISD MacArthur High School CTE</a>.</p>'
    support = '<p>Each companion is one front-and-back sheet. Stable facts and the worked example are prefilled. Labels use short fields; reasons and comparisons receive 2-3 full-width lines; the final brief separates every sentence job. Point-of-use word banks and complete frames support the exact language function. Accept typing, dictation, annotation, enlarged print, or paper, and score evidence rather than English mechanics unless meaning is unclear.</p>'
    fallback = '<p>FYF is the default student work surface on Days 1-4. Locked workbook images plus the companion form the complete no-workbook route; students do not complete both routes twice. H&amp;L, Xello School Subjects at Work, eDynamic 4.1, Canva, Adobe Express, a public Discussion, real posting/sale/contact/payment, personal data, testimonials, tracking, and copied marks are not required.</p>'
    return {
        1: {"TITLE": "Click Factor", "SUBTITLE": "50 minutes · FYF pp. 225-227 and 230", "ALERT": "<strong>Truth and privacy boundary:</strong> claims must use supplied evidence. Use only the fictional audience; do not collect, track, or target real student/minor data.", "PREP": f'<ul><li><strong>Default:</strong> one FYF workbook and device per student, one projector, zero prints. Post {link(files["CLICK"]["id"], "the two-page companion")} and private annotation route.</li><li><strong>Paper:</strong> one front-and-back companion per student, pencils/markers, and one collection tray. Students use either Canvas or paper, not both.</li><li><strong>Grouping:</strong> pairs compare CTAs and run the three-second test; each student completes and submits one response route. Teacher conference or self-test is equal.</li></ul>', "EVIDENCE": "<p>Check FYF drafts and ad in place. Collect only one individual audience-message chain, truth/access check, test, visible revision, and career/work-product connection.</p>", "MODEL": '<div style="border:1px solid #efc5aa;border-radius:8px;padding:12px 16px;background:#fff8f3"><p><strong>Model:</strong> Busy students need a quick way to compare the weekly snack-box mix. CTA: “Compare this week\'s sweet-and-salty mix.” Three-second test: the viewer saw “compare” but missed “weekly.” Revision: “Compare this week\'s snack-box mix.” Career: a marketing specialist records the tested copy and result.</p><p><strong>Non-example:</strong> “Only two boxes left—guaranteed favorite!” No supplied fact supports scarcity or a guarantee.</p></div>', "FLOW": flow(color, "Warm-up and truth model · 6", "Audience, supplied fact, action, unsupported claim.") + flow("#4c8b38", "Sample CTA types · 9", "Compare supplied approaches; draft two CTA variants for one chosen product.") + flow("#155d7a", "Build one FYF ad · 17", "Headline, accurate description, CTA, hierarchy, and access.") + flow("#d39b22", "Test and revise · 10", "Three-second partner, teacher, or self-check.") + flow("#155d7a", "Career connection · 4", "Worker, work product, next use of evidence.") + flow(color, "Submit and cleanup · 4", "One private route and material return."), "MONITOR": "<ul><li><strong>Minute 12:</strong> each student can point to one supplied fact and one clear action. If one-third invents urgency, pause and repair the model claim.</li><li><strong>Minute 30:</strong> every ad has an audience, accurate description, CTA, hierarchy, and access cue.</li><li><strong>Minute 42:</strong> before/after wording responds to test evidence, not decoration preference.</li><li><strong>Trim/recovery:</strong> supply the second sample CTA and cut optional polish/share-out. Protect one FYF ad, individual test/revision, career link, submission, and cleanup. Save the same companion for recovery.</li></ul>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        2: {"TITLE": "Written Communication and Changing Conditions", "SUBTITLE": "50 minutes · FYF pp. 147-148 + private companion + practice Quiz", "ALERT": "<strong>Fictional message:</strong> no real account, name, location, handle, photo, contact information, student data, or audience tracking. The Quiz is feedback after the private response, not the DOL.", "PREP": f'<ul><li><strong>Default:</strong> one FYF workbook and device per student, one projector, zero prints. Post {link(files["CHANGE"]["id"], "the two-page companion")}, private annotation route, and retryable Quiz.</li><li><strong>Paper:</strong> one front-and-back companion per student, pencils, one collection tray, and a five-question check only for a Canvas outage.</li><li>Students respond individually. A brief turn-and-talk may compare conditions without sharing personal social-media use.</li></ul>', "EVIDENCE": "<p>Collect one private FYF-message revision/conditions companion. Quiz feedback repairs labels but does not replace or duplicate the written evidence.</p>", "MODEL": '<div style="border:1px solid #efc5aa;border-radius:8px;padding:12px 16px;background:#fff8f3"><p><strong>Before:</strong> “We need books! #help.” <strong>After:</strong> “The fictional Little Library has room for about 20 gently used children\'s books. Use the classroom drop-off route.” The revision adds status, truthful action, and a private route.</p><p><strong>Conditions model:</strong> A 20% budget cut may reduce campaign spending and make result measurement more important. Accessible mobile content and privacy expectations require workers to check readable design, consent, accuracy, and human review. Preparation: practice data analysis and accessible message design. <strong>Limit:</strong> the BLS figure is a May 2024 U.S. median, not DFW starting pay.</p></div>', "FLOW": flow(color, "Warm-up/model · 6", "Vague versus usable fictional notice.") + flow("#4c8b38", "FYF message · 10", "Purpose, audience, important detail, safe action.") + flow("#155d7a", "Visible revision · 8", "Clarity, privacy, or access change.") + flow("#d39b22", "Current card and conditions · 16", "Separate economic from societal/technology effects.") + flow("#155d7a", "Preparation recommendation · 5", "Career, work product, and skill/learning step.") + flow(color, "Submit/Quiz/cleanup · 5", "Private response first; feedback if time."), "MONITOR": "<ul><li><strong>Minute 14:</strong> messages include status, truthful action, and no identifying data. If one-third copies the vague prompt, project the before/after model.</li><li><strong>Minute 32:</strong> students label $76,950 as May 2024 U.S. median, 7% as 2024-34 growth, and about 87,200 as annual openings; never substitute the 63,000 numeric employment change.</li><li><strong>Minute 43:</strong> economic effect concerns spending/budget/demand/hiring; societal/technology effect concerns behavior/tools/access/privacy/human review.</li><li><strong>Trim/recovery:</strong> defer Quiz retries and sharing. Protect the revision, two distinct effects, preparation, private submission, and cleanup.</li></ul>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        3: {"TITLE": "Expert Edge", "SUBTITLE": "50 minutes · FYF pp. 222-224", "ALERT": "<strong>Classroom plan only:</strong> no sale, payment, booking, contact, account, client data, public promotion, income promise, or copied identity.", "PREP": f'<ul><li><strong>Default:</strong> one FYF workbook and device per student, one projector, zero prints. Post {link(files["EXPERT"]["id"], "the two-page companion")} and private annotation route.</li><li><strong>Paper:</strong> one front-and-back companion per student, pencils/markers, and one collection tray.</li><li><strong>Grouping:</strong> individual plan; partner, teacher conference, or self-check for feedback. Oral pitch and logo polish are optional.</li></ul>', "EVIDENCE": "<p>Check the FYF service plan in place. Collect only one individual opportunity chain, responsibility/risk/control, private test, visible revision, and career/work-product connection.</p>", "MODEL": '<div style="border:1px solid #efc5aa;border-radius:8px;padding:12px 16px;background:#fff8f3"><p><strong>Model:</strong> Skill: organizing digital photos. Need: a family wants a clear album plan. Deliverable: a labeled-folder plan and album outline. Fictional price: $8 per planning outline—not an income promise. Responsibility: describe what is included. Risk: private photos could be exposed. Control: use fictional filenames only and never collect files. Test note: the limit was unclear. Revision: add “planning outline only; no photo upload.” Career: a marketing specialist tests the service description.</p><p><strong>Non-example:</strong> “I like photos, so I have a business.” A hobby alone is not a need, deliverable, or bounded opportunity.</p></div>', "FLOW": flow(color, "Skill-to-need model · 6", "Need and deliverable, not only a hobby.") + flow("#4c8b38", "Build FYF service · 17", "Audience, need, deliverable, mission, unit/price, add-on.") + flow("#155d7a", "Responsibility/risk/control · 10", "Keep owner action and uncertainty distinct.") + flow("#d39b22", "Private test/revision · 9", "Partner, conference, or self-check.") + flow("#155d7a", "Career connection · 4", "Worker, work product, next evidence use.") + flow(color, "Submit and cleanup · 4", "One private route and material return."), "MONITOR": "<ul><li><strong>Minute 12:</strong> students can name audience + need + deliverable. If one-third starts with logo only, reproject the model chain.</li><li><strong>Minute 29:</strong> the fictional price includes a unit and no income promise; responsibility, risk, and control are distinct.</li><li><strong>Minute 42:</strong> feedback produces one visible clarity or safety revision.</li><li><strong>Trim/recovery:</strong> cut logo polish and oral pitch. Protect opportunity reasoning, responsibility/risk/control, revision, career link, submission, and cleanup.</li></ul>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        4: {"TITLE": "Family Fun Pass", "SUBTITLE": "50 minutes · FYF p. 229, then p. 228", "ALERT": "<strong>Fictional workbook data:</strong> use the supplied group-level scenario only. Do not survey students, collect personal preference data, track behavior, or claim universal age-group patterns.", "PREP": f'<ul><li><strong>Default:</strong> one FYF workbook and device per student, one projector, zero prints. Post {link(files["FAMILY"]["id"], "the two-page landscape companion")} and private annotation route.</li><li><strong>Paper:</strong> one two-page landscape packet per student and one collection tray.</li><li>Students decide individually after one pair evidence-sort. No live survey, site, account, public pitch, or open-web research.</li></ul>', "EVIDENCE": "<p>Check the FYF pitch in place. Collect only one individual goal, two numbers and one quote/pattern, decision rule, limitation, next test/result, and career connection.</p>", "MODEL": '<div style="border:1px solid #efc5aa;border-radius:8px;padding:12px 16px;background:#fff8f3"><p><strong>Model:</strong> Goal: sales. Strategy: Influencer. Evidence: 1,450 past sales, very high engagement, and the focus-group quote about trusted recommendations. Conflict: Social had more clicks. Decision rule: for a sales goal, past sales matter more than clicks. Limit: a past campaign does not predict the next one. Test: run a small fictional A/B comparison and measure completed sign-ups. Career: a market research analyst reports the test result.</p><p><strong>Non-example:</strong> “Influencer is best because I like it.” Preference is not a decision rule.</p></div>', "FLOW": flow(color, "Goal-before-metric · 6", "Name what success means.") + flow("#4c8b38", "Read/sort evidence · 9", "Preference, performance, and quotes answer different questions.") + flow("#155d7a", "Compare and choose · 15", "Two numbers and one quote/pattern tied to the goal.") + flow("#d39b22", "Conflict, limit, test · 11", "Decision rule and exact result to measure.") + flow("#155d7a", "Career connection · 5", "Worker and next use of result.") + flow(color, "Submit and cleanup · 4", "One private route and material return."), "MONITOR": "<ul><li><strong>Minute 12:</strong> every student names a goal before a strategy. If one-third picks by preference, project the sales-goal model.</li><li><strong>Minute 29:</strong> the evidence stack has two exact numbers and one quote/pattern with meanings.</li><li><strong>Minute 43:</strong> conflict, decision rule, limitation, next test, and exact result are visible.</li><li><strong>Trim/recovery:</strong> supply the third-strategy comparison and cut sharing. Protect goal, three-point evidence, limit/test, career link, submission, and cleanup.</li></ul>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        5: {"TITLE": "Ethical Marketing Evidence Brief", "SUBTITLE": "50 minutes · Minor 3", "ALERT": "<strong>Minor 3:</strong> one private four-page brief plus the visible 16-point self-score and revision. Earlier work is reference evidence, not another upload.", "PREP": f'<ul><li><strong>Default:</strong> one device per student, one projector, zero prints. Post {link(files["BRIEF"]["id"], "the four-page brief")}, {link(files["RUBRIC"]["id"], "the two-page rubric")}, and private Minor 3 Assignment.</li><li><strong>Paper:</strong> one four-page brief and one two-page rubric per student, stapled as one set, plus one collection tray.</li><li>Students work individually. Prior work may be referenced; missing work uses the fixed recap/model rather than four replacement packets.</li></ul>', "EVIDENCE": "<p>Collect one brief and rubric/self-score with audience/communication, entrepreneurship, data decision, career/changing conditions, and one visible evidence revision.</p>", "MODEL": '<div style="border:1px solid #efc5aa;border-radius:8px;padding:12px 16px;background:#fff8f3"><p><strong>Complete model strip:</strong> A market research analyst studies audience response and reports results. For busy students, “Compare this week\'s snack-box mix” uses a supplied fact and collects no personal data; a three-second test led me to add “this week.” My fictional photo-organizing opportunity provides a labeled-folder plan only; the owner explains scope and uses fictional filenames to control privacy risk. For the Family Fun Pass sales goal, Influencer is supported by 1,450 sales, very high engagement, and the trusted-recommendation quote, but past data cannot guarantee the next result, so I would measure completed sign-ups in a small fictional test. Economic budget pressure may reduce campaign spending; accessibility/privacy/tool changes require data analysis, accessible design, and human review. I would practice those skills and verify live program details.</p><p><strong>Non-example:</strong> “Marketing fits because social media is fun and the salary is $76,950.” Preference and an unlabeled median do not complete the evidence jobs.</p></div>', "FLOW": flow(color, "Readiness/model · 7", "Four rubric jobs and fixed recap route.") + flow("#4c8b38", "Career/audience · 8", "Worker, source label, message, boundary, revision.") + flow("#155d7a", "Entrepreneurship · 9", "Need, deliverable, responsibility, risk, control.") + flow("#d39b22", "Data/conditions · 12", "Evidence stack, limit/test, two distinct effects.") + flow("#155d7a", "Self-score/revise · 8", "Weakest criterion and visible repair.") + flow(color, "Submit and cleanup · 6", "One private digital file/text route or labeled paper set."), "MONITOR": "<ul><li><strong>Minute 10:</strong> every student has prior evidence or the complete model strip; no one is rebuilding four days.</li><li><strong>Minute 26:</strong> audience/communication and entrepreneurship fields include a boundary, not only preference.</li><li><strong>Minute 40:</strong> data decision includes two numbers, quote/pattern, limitation/test; economic and societal/technology effects remain distinct.</li><li><strong>Minute 46:</strong> all four self-scores and one visible revision are complete.</li><li><strong>Trim/recovery:</strong> accept labeled bullets and cut sharing/polish. Never trim a rubric job, self-score, revision, private submission, or cleanup. Save the same brief for a scheduled recovery window.</li></ul>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
    }


async def main():
    preflight()
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        # Validate the weighted object before the first Canvas mutation.
        mapped_minor, minor_group, scoring_note = await mapped_minor_assignment(client)
        module = await ensure_module(client)
        path = "course files/CCR Materials/6SW/Wk3"
        folder = await common.ensure_folder(client, path)
        files = {key: await upload_locked(client, ROOT / "docs/resources/worksheets" / name, path) for key, name in WORKSHEET_FILES.items()}
        visual_path = "course files/CCR Materials/6SW/Wk3/Locked Licensed Visuals"
        visual_folder = await common.ensure_folder(client, visual_path)
        visuals = {key: await upload_locked(client, ASSETS / name, visual_path) for key, name in VISUAL_FILES.items()}
        folder, folder_files = await assert_folder_files(client, folder, WORKSHEET_FILES.values())
        visual_folder, visual_files = await assert_folder_files(client, visual_folder, VISUAL_FILES.values())
        quiz = await upsert_quiz(client)
        assignments = {}
        for day, key in {1: "CLICK", 2: "CHANGE", 3: "EXPERT", 4: "FAMILY"}.items():
            assignments[day] = await upsert_practice_assignment(
                client,
                TITLES[day],
                "<p>Complete the FYF work once, then submit only the individual evidence delta by private annotation, upload, typed labeled responses, or one labeled paper copy. This practice is worth 0 points, omitted from the final grade, and unpublished.</p>",
                files[key]["id"],
            )
        evidence_links = (
            f'<p>Submit {common.file_link(files["BRIEF"]["id"], "the private four-page Marketing Evidence Brief")} and '
            f'{common.file_link(files["RUBRIC"]["id"], "the visible 16-point self-score and revision record")}. '
            'Use prior FYF work and companions as evidence; do not submit a public post or supplemental platform screenshot. '
            'Audience fit, ethical communication, entrepreneurship reasoning, data use, source labels, career connection, and revision are scored. '
            'Graphic polish, platform access, public speaking, personal business experience, and English mechanics unless meaning is unclear do not determine the score.</p>'
        )
        assignments[5] = await require_minor_assignment(client, mapped_minor, minor_group, scoring_note, evidence_links)
        urls = {day: f"/courses/{COURSE_ID}/assignments/{assignment['id']}" for day, assignment in assignments.items()}
        urls["QUIZ"] = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        students = student_content(files, visuals, urls)
        teachers = teacher_content(files)
        labels = {1: "Click Factor", 2: "Written Communication and Changing Conditions", 3: "Expert Edge", 4: "Family Fun Pass", 5: "Ethical Marketing Evidence Brief"}
        interactions = {day: ("Assignment", assignments[day]["id"], TITLES[day]) for day in range(1, 6)}
        order, pages = [], {}
        for day in range(1, 6):
            header_title = f"Day {day} · {labels[day]}"
            await prior.upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header_title, header_title))
            student_title = f"STUDENT: 6SW Wk3 Day {day} - {labels[day]}"
            student_page = await common.upsert_page(client, student_title, common.render("6sw-wk3-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, **CONTRACTS[day], **students[day]}))
            teacher_title = f"TEACHER: 6SW Wk3 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(client, teacher_title, common.render("6sw-wk3-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **CONTRACTS[day], **teachers[day]}))
            await prior.upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await prior.upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            kind, key, title = interactions[day]
            await prior.upsert_item(client, module["id"], kind, key, title)
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title), (kind, key, title)]
            pages[day] = {"teacher": teacher_page, "student": student_page}

        # Keep the response home first and the optional feedback Quiz directly after it.
        await prior.upsert_item(client, module["id"], "Quiz", quiz["id"], QUIZ_TITLE)
        order.insert(8, ("Quiz", quiz["id"], QUIZ_TITLE))
        ordered = await prior.reconcile_module_items(client, module["id"], order)
        if len(ordered) != 21:
            raise RuntimeError(f"Expected 21 exact Marketing module items; found {len(ordered)}")

        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
        if module.get("published") is not False or len([entry for entry in modules if entry.get("name") == MODULE_NAME]) != 1:
            raise RuntimeError("Final Marketing module uniqueness/unpublished invariant failed")
        for day, pair in pages.items():
            for kind, page in pair.items():
                fresh = await common.api(client, "GET", f"/courses/{COURSE_ID}/pages/{page['url']}")
                if fresh.get("published") is not False:
                    raise RuntimeError(f"Marketing Day {day} {kind} page is published")
                pair[kind] = fresh
        for day, key in {1: "CLICK", 2: "CHANGE", 3: "EXPERT", 4: "FAMILY"}.items():
            assignments[day] = await assert_annotation_assignment(client, assignments[day], files[key]["id"])
        minor = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignments[5]['id']}")
        if (
            minor.get("assignment_group_id") != minor_group.get("id")
            or minor.get("published") is not False
            or float(minor.get("points_possible") or 0) != 100
            or minor.get("grading_type") != "points"
            or minor.get("omit_from_final_grade") is not False
            or RUBRIC_NOTE_MARKER not in (minor.get("description") or "")
            or set(minor.get("submission_types") or []) != {"online_upload", "online_text_entry"}
        ):
            raise RuntimeError("Final Marketing Minor invariant failed")
        assignments[5] = minor
        quiz = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
        if quiz.get("published") is not False or quiz.get("quiz_type") != "practice_quiz" or int(quiz.get("allowed_attempts") or 0) != -1 or quiz.get("shuffle_answers") is not False:
            raise RuntimeError("Final Marketing Quiz invariant failed")
        folder, folder_files = await assert_folder_files(client, folder, WORKSHEET_FILES.values())
        visual_folder, visual_files = await assert_folder_files(client, visual_folder, VISUAL_FILES.values())
        print(json.dumps({"module": {"id": module["id"], "published": module["published"]}, "folder": {"id": folder["id"], "locked": folder["locked"], "files_locked": len(folder_files)}, "visual_folder": {"id": visual_folder["id"], "locked": visual_folder["locked"], "files_locked": len(visual_files)}, "files": {key: record["id"] for key, record in files.items()}, "visuals": {key: record["id"] for key, record in visuals.items()}, "quiz": {"id": quiz["id"], "published": quiz.get("published")}, "assignments": {str(day): {"id": assignment["id"], "published": assignment.get("published"), "points": assignment.get("points_possible"), "grading_type": assignment.get("grading_type"), "omit_from_final_grade": assignment.get("omit_from_final_grade")} for day, assignment in assignments.items()}, "pages": {str(day): {kind: {"url": page["url"], "published": page["published"]} for kind, page in pair.items()} for day, pair in pages.items()}, "items": [{"position": entry["position"], "type": entry["type"], "title": entry["title"]} for entry in ordered]}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
