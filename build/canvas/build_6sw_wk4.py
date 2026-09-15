"""Build the unpublished 6SW Week 4 sales and oral-evidence module."""

import asyncio
import json
import sys
from urllib.parse import urlencode

import httpx

import build_5sw_wk1 as prior
from configure_assessment_map import SUBMISSION_LINK_MARKER


common = prior.common
COURSE_ID = common.COURSE_ID
STUDENT_GOOGLE_COPY_URLS = {
    1: "https://docs.google.com/document/d/11Dz2W7M0xqwL2YWyfTcCUKm4Csc4klTx87vNgV69Cws/copy",
    2: "https://docs.google.com/document/d/1F1hMo_XUDFC-sBs1ex-isFau2SLaURIN_YxgbPsuh-E/copy",
    3: "https://docs.google.com/document/d/1ud6DX18VXUhv_pnZbfIZf7Xnzxw3unUyOjjDUNrNOBA/copy",
    4: "https://docs.google.com/document/d/1zVAt8D4gDqnu3sI5EwWch5cQcxIq2yvDu60gDB2gxtE/copy",
    5: "https://docs.google.com/document/d/1_ZC31w6pL3tZlEx6mG_rhBiiiMEyirL1cUXExi516Zk/copy",
}


# One Google Doc per worksheet (build/google_docs/student_worksheet_docs.json).
# Keyed by (day, anchor label) so a worksheet button never opens the day's exit ticket.
STUDENT_WORKSHEET_COPY_URLS = {
    (1, 'the two-page audience and accuracy companion'): "https://docs.google.com/document/d/1UwcD6nfhnKn5Swt_YTfV0ZiLBUeht0igsFexdIsJXo4/copy",
    (2, 'the two-page delivery and revision record'): "https://docs.google.com/document/d/148wVvimVz0-kYzqPy_JcOPwuf3d_TfNJd-IhX4ICC_0/copy",
    (3, 'the two-page individual decision and career-outline companion'): "https://docs.google.com/document/d/1ThvL-DROnB-0elo0WR6TqdPJJEM1bKDM8kC6panAXtc/copy",
    (4, 'the two-page landscape appearance and rehearsal companion'): "https://docs.google.com/document/d/1gfL2w9PDNJoP14x7OxMuVt5g3kuGesblkRncIcWlPgA/copy",
    (5, 'the two-page Career Oral Evidence Brief'): "https://docs.google.com/document/d/1uO4LlYZDRWZd9oERemAu8WtHrX1-DczhP_Eaf_Jt1mQ/copy",
}


def student_copy_link(day, label):
    url = STUDENT_WORKSHEET_COPY_URLS.get((day, label), STUDENT_GOOGLE_COPY_URLS[day])
    return f'<a href="{url}">{label}</a>'

ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/6sw/wk4"
MODULE_NAME = "6SW Wk4: Sales and Career Oral Evidence"
MODULE_ALIASES = ("6SW Wk4: Sales / Presentations",)
TITLES = {
    1: "PRACTICE: Audience and Sales Pitch Plan",
    2: "PRACTICE: Oral Pitch Delivery and Revision",
    3: "PRACTICE: BrainBoost Decision and Career Outline",
    4: "PRACTICE: Interview Appearance and Rehearsal",
    5: "FORMATIVE: Career Oral Evidence Brief",
}
DAY4_ASSIGNMENT_TITLE = "PRACTICE: Interview Appearance and Rehearsal Record"
TEMPLATES = ROOT / "build/canvas/templates"
WORKSHEET_NAMES = {
    "PLAN": "6sw-wk4-sales-pitch-plan.pdf",
    "DELIVERY": "6sw-wk4-pitch-delivery-record.pdf",
    "BRAIN": "6sw-wk4-brainboost-and-career-outline.pdf",
    "APPEAR": "6sw-wk4-appearance-and-rehearsal.pdf",
    "ORAL": "6sw-wk4-career-oral-evidence.pdf",
    "RUBRIC": "6sw-wk4-career-oral-rubric.pdf",
}
VISUAL_PAGES = (241, 242, 243, 244, 245, 246, 247, 280, 299)
ANNOTATION_DAYS = {1: "PLAN", 2: "DELIVERY", 3: "BRAIN", 4: "APPEAR", 5: "ORAL"}


def preflight():
    required = [
        TEMPLATES / "6sw-wk4-student.html",
        TEMPLATES / "6sw-wk4-teacher.html",
        *(ROOT / "docs/resources/worksheets" / name for name in WORKSHEET_NAMES.values()),
        *(ASSETS / f"fyf-p{page}.jpg" for page in VISUAL_PAGES),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"6SW Wk4 preflight missing required files: {missing}")


async def canvas_preflight(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    module_matches = [entry for entry in modules if entry.get("name") in {MODULE_NAME, *MODULE_ALIASES}]
    if len(module_matches) > 1:
        raise RuntimeError(f"Duplicate 6SW Wk4 modules: {[entry['id'] for entry in module_matches]}")
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    assignment_matches = {}
    assignment_titles = {1: TITLES[1], 2: TITLES[2], 3: TITLES[3], 4: DAY4_ASSIGNMENT_TITLE, 5: TITLES[5]}
    for day, title in assignment_titles.items():
        matches = [entry for entry in assignments if entry.get("name") == title]
        if len(matches) > 1:
            raise RuntimeError(f"Duplicate assignments named {title!r}: {[entry['id'] for entry in matches]}")
        # Legacy unpublished practices may have extra submission routes. The
        # write below normalizes those routes, and the post-write/final checks
        # require the exact approved set. Grading/publication state still fails
        # closed before any mutation.
        if matches and (
            matches[0].get("published") is not False
            or float(matches[0].get("points_possible") or 0) != 0
            or matches[0].get("grading_type") != "percent"
            or matches[0].get("omit_from_final_grade") is not True
        ):
            raise RuntimeError(f"Refusing to modify malformed formative assignment {title!r}")
        assignment_matches[day] = matches[0] if matches else None
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    quiz_matches = [entry for entry in quizzes if entry.get("title") == TITLES[4]]
    if len(quiz_matches) > 1:
        raise RuntimeError(f"Duplicate quizzes named {TITLES[4]!r}: {[entry['id'] for entry in quiz_matches]}")
    if quiz_matches and (
        quiz_matches[0].get("published") is not False
        or quiz_matches[0].get("quiz_type") != "practice_quiz"
        or int(quiz_matches[0].get("allowed_attempts") or 0) != -1
    ):
        raise RuntimeError(f"Refusing to modify malformed practice Quiz {TITLES[4]!r}")
    return assignment_matches, quiz_matches[0] if quiz_matches else None

CONTRACTS = {
    1: {
        "TOPIC": "Audience and Message",
        "OBJECTIVE": "Students will identify a sales or marketing career opportunity and use FYF pitch evidence to plan an accurate audience-specific hook, offer, benefit, and call to action.",
        "TEKS": "d(1)(C), d(4)(B)",
        "DOL": "Completed FYF 30 Seconds to Sell work plus a two-page individual audience/assumption check, ethical boundary, career/work-product connection, and selected oral route.",
        "I_CAN": "identify a sales or marketing career and use FYF evidence to plan an accurate pitch for a specific audience.",
        "SHOW": "Complete FYF 30 Seconds to Sell and the two-page companion with an audience/fact/assumption check, ethical boundary, career connection, and selected oral route.",
    },
    2: {
        "TOPIC": "Oral Revision",
        "OBJECTIVE": "Students will communicate an audience-specific pitch twice, use feedback to make one visible revision, and explain how the communication skill transfers to a second career.",
        "TEKS": "d(4)(B)",
        "DOL": "Two timed oral/AAC pitch attempts, one specific feedback point, a visible before/after revision, and a two-career transfer response.",
        "I_CAN": "deliver a short pitch twice, use specific feedback to revise it, and explain how the same communication skill works in another career.",
        "SHOW": "Record two timed oral/AAC attempts, specific feedback, a visible before/after revision, evidence of its effect, and a two-career transfer response.",
    },
    3: {
        "TOPIC": "Problem Solving",
        "OBJECTIVE": "Students will identify how a sales, marketing, or design career uses evidence to define a campaign problem, screen solutions, and organize a bounded career brief.",
        "TEKS": "d(1)(C), d(4)(B)",
        "DOL": "Completed FYF BrainBoost work plus a two-page individual cause statement, evidence-linked decision, fixed-source career outline, and cross-career problem-solving connection.",
        "I_CAN": "use campaign evidence to separate a cause from a result, choose a bounded solution, and connect the problem-solving move to two careers.",
        "SHOW": "Complete FYF BrainBoost and the two-page companion with a cause/evidence decision, rejected unsupported claim, career outline, and cross-career connection.",
    },
    4: {
        "TOPIC": "Interview Appearance",
        "OBJECTIVE": "Students will describe context-appropriate interview appearance across office, task-demonstration, and virtual settings, then rehearse a career brief twice using an appropriate private recording, Canvas evidence card, teacher-approved visual, or AAC technology route.",
        "TEKS": "d(6)(B), d(4)(C)",
        "DOL": "Three context decisions with verification questions, retryable practice Quiz feedback, two timed oral/AAC career rehearsals using one appropriate technology choice, and one visible revision.",
        "I_CAN": "choose interview preparation for the workplace, task, safety needs, format, and accommodation, then use appropriate technology to rehearse and revise my career brief.",
        "SHOW": "Complete three context decisions, review Quiz feedback, and record two timed oral/AAC rehearsals using one appropriate technology choice and one visible revision.",
    },
    5: {
        "TOPIC": "Career Oral Evidence",
        "OBJECTIVE": "Students will deliver a 60-90-second oral/AAC career brief using an appropriate private recording, Canvas evidence card, teacher-approved visual, or AAC technology route, with one duty, preparation evidence, a correctly labeled labor figure, and a bounded conclusion.",
        "TEKS": "d(1)(C), d(4)(B), d(4)(C)",
        "DOL": "Private 60-90-second oral/AAC career brief with one appropriate technology choice, two-page delivery record, two-career transfer reflection, 16-point self-score, and one visible revision note.",
        "I_CAN": "use appropriate technology to deliver a concise career brief with accurate source labels and explain how one communication skill works in two careers.",
        "SHOW": "Submit the private 60-90-second oral/AAC brief using one appropriate technology choice, two-page evidence record, two-career transfer reflection, self-score, and visible revision note.",
    },
}


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    matches = [module for module in modules if module.get("name") in {MODULE_NAME, *MODULE_ALIASES}]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one {MODULE_NAME!r} module; found {len(matches)}")
    data = {"module[published]": "false", "module[name]": MODULE_NAME}
    if matches:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{matches[0]['id']}", data=data)
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


async def upload_locked(client, path, folder_path):
    uploaded = await common.upload(client, path, folder_path)
    record = await common.api(client, "GET", f"/files/{uploaded['id']}")
    if record.get("locked") is not True:
        record = await common.api(client, "PUT", f"/files/{uploaded['id']}", data={"locked": "true"})
    if record.get("locked") is not True:
        raise RuntimeError(f"Canvas did not lock {path.name!r}")
    return record


async def lock_folder_files(client, folder, expected_names):
    current = await common.api(client, "GET", f"/folders/{folder['id']}")
    if current.get("locked") is not True:
        current = await common.api(client, "PUT", f"/folders/{folder['id']}", data={"locked": "true"})
    if current.get("locked") is not True:
        raise RuntimeError(f"Canvas did not lock folder {folder['id']}")
    for record in await common.paged(client, f"/folders/{folder['id']}/files"):
        if record.get("locked") is not True:
            await common.api(client, "PUT", f"/files/{record['id']}", data={"locked": "true"})
    final = await common.paged(client, f"/folders/{folder['id']}/files")
    names = {record.get("filename") for record in final}
    if any(record.get("locked") is not True for record in final) or not set(expected_names).issubset(names):
        raise RuntimeError(f"Unlocked files remain in folder {folder['id']}")
    return current, len(final)


async def assert_annotation_assignment(client, title, assignment, source_id, required_routes):
    fresh = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignment['id']}")
    source = await common.api(client, "GET", f"/files/{source_id}")
    clone_id = int(fresh.get("annotatable_attachment_id") or 0)
    clone = await common.api(client, "GET", f"/files/{clone_id}") if clone_id else {}
    if clone and clone.get("locked") is not True:
        clone = await common.api(client, "PUT", f"/files/{clone_id}", data={"locked": "true"})
    if (
        fresh.get("published") is not False
        or float(fresh.get("points_possible") or 0) != 0
        or fresh.get("grading_type") != "percent"
        or fresh.get("omit_from_final_grade") is not True
        or set(fresh.get("submission_types") or []) != set(required_routes)
        or not clone_id
        or source.get("locked") is not True
        or clone.get("locked") is not True
        or clone.get("filename") != source.get("filename")
        or int(clone.get("size") or -1) != int(source.get("size") or -2)
    ):
        raise RuntimeError(f"Formative annotation invariant failed for {title!r}")
    return fresh


async def upsert_formative_assignment(client, found, title, description, attachment_id, routes):
    data = {
        "assignment[name]": title,
        "assignment[description]": description,
        "assignment[submission_types][]": routes,
        "assignment[annotatable_attachment_id]": str(attachment_id),
        "assignment[grading_type]": "percent",
        "assignment[points_possible]": "0",
        "assignment[omit_from_final_grade]": "true",
        "assignment[published]": "false",
    }
    assignment = await common.api(
        client,
        "PUT" if found else "POST",
        f"/courses/{COURSE_ID}/assignments/{found['id']}" if found else f"/courses/{COURSE_ID}/assignments",
        data=data,
    )
    return await assert_annotation_assignment(client, title, assignment, attachment_id, routes)


QUESTIONS = [
    (
        "Q1 - appearance context",
        "Which rule works across different interview settings?",
        "Prepare for the workplace, task, safety needs, format, and accommodations; choose clean, functional, role-aware clothing.",
        ["Every interview requires a suit.", "Expensive clothing earns a higher score.", "One gendered list works for everyone."],
        "Correct. Context and safety come before fashion rules.",
        "Appearance guidance is not universal, expensive, or gendered.",
    ),
    (
        "Q2 - skilled trade",
        "What should a student do before bringing or using tools or PPE for an interview task?",
        "Confirm the employer or site instructions and required safety route.",
        ["Bring any tools from home.", "Wear fashion footwear instead of safety gear.", "Assume every site uses the same PPE."],
        "Correct. Site and task requirements must be confirmed.",
        "PPE and tool rules are specific to the task and site.",
    ),
    (
        "Q3 - virtual",
        "Which preparation best supports a virtual interview?",
        "Test audio, lighting, background and privacy, notifications, and a backup connection route.",
        ["Require a camera regardless of access needs.", "Open every app during the interview.", "Share the meeting link publicly."],
        "Correct. Technology, privacy, and backup planning matter.",
        "Camera use is not always required, and privacy still applies.",
    ),
    (
        "Q4 - salary label",
        "Which label is accurate for the fixed Sales Managers figure?",
        "$138,060 May 2024 U.S. median; not DFW starting pay or a guarantee.",
        ["Guaranteed DFW entry salary", "The pay for every salesperson", "A live job opening"],
        "Correct. Measure, date, geography, and limitation stay visible.",
        "A national median is not local starting pay, a vacancy, or a personal outcome.",
    ),
    (
        "Q5 - oral route",
        "Which route can demonstrate the oral-presentation standard?",
        "A live, teacher-conference, recorded audio/video, or AAC brief with assessable oral or communicated evidence.",
        ["A written outline alone with no authorized accommodation", "A H&L favorite", "A public Discussion post"],
        "Correct. Several private oral and AAC routes can show the same evidence.",
        "Written planning supports oral evidence but is not automatically the same standard.",
    ),
]


async def upsert_quiz(client):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    matches = [quiz for quiz in quizzes if quiz.get("title") == TITLES[4]]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one {TITLES[4]!r} Quiz; found {len(matches)}")
    data = {
        "quiz[title]": TITLES[4],
        "quiz[description]": "<p>Ungraded, unlimited-retry practice on appearance context, safety, virtual readiness, source labels, and equivalent oral routes.</p>",
        "quiz[quiz_type]": "practice_quiz",
        "quiz[published]": "false",
        "quiz[allowed_attempts]": "-1",
        "quiz[show_correct_answers]": "true",
        "quiz[shuffle_answers]": "false",
    }
    quiz = await common.api(
        client,
        "PUT" if matches else "POST",
        f"/courses/{COURSE_ID}/quizzes/{matches[0]['id']}" if matches else f"/courses/{COURSE_ID}/quizzes",
        data=data,
    )
    existing = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    desired_names = {name for name, *_rest in QUESTIONS}
    for question in existing:
        if question.get("question_name") not in desired_names:
            await common.api(client, "DELETE", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{question['id']}")
    existing = [question for question in existing if question.get("question_name") in desired_names]
    seen = set()
    for question in existing:
        name = question.get("question_name")
        if name in seen:
            await common.api(client, "DELETE", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{question['id']}")
        else:
            seen.add(name)
    for position, (name, prompt, correct, wrong, yes, no) in enumerate(QUESTIONS, 1):
        old = next((question for question in existing if question.get("question_name") == name), None)
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
        path = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{old['id']}" if old else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        await common.api(client, "PUT" if old else "POST", path, json=payload)
    expected = [name for name, *_rest in QUESTIONS]
    final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    by_name = {question.get("question_name"): question for question in final_questions}
    if set(by_name) != set(expected) or len(final_questions) != len(expected):
        raise RuntimeError("Sales practice Quiz question set mismatch")
    fields = []
    for name in expected:
        fields.extend([("order[][id]", str(by_name[name]["id"])), ("order[][type]", "question")])
    await common.api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/reorder",
        content=urlencode(fields),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    if [question.get("question_name") for question in final_questions] != expected:
        raise RuntimeError("Sales practice Quiz order mismatch")
    final = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
    if final.get("published") is not False or final.get("quiz_type") != "practice_quiz" or int(final.get("allowed_attempts") or 0) != -1:
        raise RuntimeError("Sales practice Quiz state mismatch")
    return final


def student_content(files, visuals, urls):
    link, step = common.file_link, common.step
    media = lambda pairs: '<h3 style="color:#245f69;border-bottom:3px solid #b9d9de">Workbook pages</h3>' + "".join(prior.image_tag(visuals[key]["id"], alt) for key, alt in pairs)
    submission_panel = (
        f'<section data-cce-marker="{SUBMISSION_LINK_MARKER}" '
        'style="border:2px solid #245f69;border-radius:12px;padding:18px 20px;margin:24px 0;background:#f4fafb">'
        '<h3 style="margin:0 0 8px;color:#245f69">Submit your formative oral evidence</h3>'
        '<p style="margin:0 0 14px">Use the rubric to check both parts. <strong>Recorded route:</strong> upload the completed brief/rubric and private audio/video together as files in one submission. <strong>Live, conference, or AAC route:</strong> submit the written brief/rubric by annotation, upload, or exact labeled text; your teacher records the career, date, route, time, technology used, and completion on the class checkoff. Text alone is not oral evidence.</p>'
        f'<p style="margin:0"><a href="{urls[5]}" style="display:inline-block;background:#245f69;color:#fff;padding:11px 18px;border-radius:6px;text-decoration:none;font-weight:700" data-api-endpoint="/api/v1{urls[5]}" data-api-returntype="Assignment">Open {TITLES[5]}</a></p></section>'
    )
    return {
        1: {
            "TITLE": "Audience and Sales Pitch Plan",
            "PURPOSE": "Use FYF evidence to plan a short fictional pitch for a specific audience without inventing claims.",
            "TODAY": "<ul><li>label the four pitch parts;</li><li>choose a fictional offer and audience;</li><li>complete the FYF plan and draft;</li><li>check accuracy and connect the work to a career.</li></ul>",
            "READY": f'<p><strong>Start in FYF pp. 241-243.</strong> Use {student_copy_link(1, "the two-page audience and accuracy companion")} or <a href="{urls[1]}">the private annotation activity</a> for the evidence the workbook does not collect. Do not complete both work routes.</p>',
            "MEDIA": media([("p241", "30 Seconds to Sell pitch anatomy and SparkClean worked example"), ("p242", "Offer, audience, and four-part pitch planner"), ("p243", "Full pitch, practice, feedback, and discussion prompts")]),
            "STEPS": step(1, "Label the model", "<p>Find the hook, clear offer, audience benefit, and call to action. Mark any claim that would need verification.</p>") + step(2, "Choose the fictional offer and audience", "<p>Complete FYF Steps 2-3. Separate a supplied fact or logical reason from an audience assumption.</p>") + step(3, "Plan and write", "<p>Complete FYF Steps 4-5. Use benefits, not only features; keep the language accurate.</p>") + step(4, "Add the companion evidence", "<p>Record the ethical boundary, career/work product, transferable skill, and Day 2 oral route.</p>"),
            "EXIT": "<p>Name the career, work product, and one claim or assumption you kept bounded.</p>",
            "DONE": "<ul><li>FYF pitch or no-workbook route;</li><li>audience/fact/assumption check;</li><li>accuracy and privacy boundary;</li><li>career and transfer evidence;</li><li>selected oral route.</li></ul>",
            "SUPPORT": "<p><strong>Word bank:</strong> audience/audiencia · benefit/beneficio · evidence/evidencia · assumption/suposicion · accurate/exacto.</p><p><strong>Use this frame:</strong> The benefit fits <strong>[audience]</strong> because <strong>[fact or reason]</strong>. I should not assume <strong>[assumption]</strong>.</p>",
            "FALLBACK": "<p>The locked FYF images plus the two-page companion are the complete no-workbook route. No real sale, public post, link, payment, customer, account, H&amp;L, Xello, eDynamic, or design platform is required.</p>",
        },
        2: {
            "TITLE": "Deliver, Test, and Revise",
            "PURPOSE": "Deliver the FYF pitch twice through a private oral/AAC route and make one specific revision between attempts.",
            "TODAY": "<ul><li>check the pitch boundary;</li><li>deliver once;</li><li>collect specific feedback;</li><li>revise, deliver again, and transfer the skill.</li></ul>",
            "READY": f'<p><strong>Use your FYF pp. 241-243 pitch.</strong> Open {student_copy_link(2, "the two-page delivery and revision record")} and <a href="{urls[2]}">the private upload/annotation activity</a>. Recorded route: upload the written record and private audio/video together. Live, conference, or AAC route: submit the written record while your teacher completes the oral/AAC checkoff.</p>',
            "MEDIA": media([("p243", "Practice, partner/small-group/class options, feedback record, and discussion")]),
            "STEPS": step(1, "Check the boundary", "<p>Remove unsupported urgency, guarantees, health, popularity, scarcity, or income claims.</p>") + step(2, "Deliver once", "<p>Use the route your teacher assigned: live partner/small group, teacher conference, private recording, or AAC. Keep it at 60 seconds or less.</p>") + step(3, "Get specific feedback", "<p>Name an exact word, sentence, pause, or organization choice to revise.</p>") + step(4, "Revise and deliver again", "<p>Keep the before/after language visible, record the time and effect, then compare how the skill works in two careers.</p>"),
            "EXIT": "<p>State the revision that changed clarity, accuracy, organization, or delivery/AAC output.</p>",
            "DONE": "<ul><li>two timed oral/AAC attempts;</li><li>specific feedback;</li><li>visible revision;</li><li>evidence of its effect;</li><li>two-career transfer response.</li></ul>",
            "SUPPORT": "<p><strong>Word bank:</strong> pace/ritmo · clear/claro · specific/especifico · revise/revisar · feedback/retroalimentacion.</p><p><strong>Use this frame:</strong> I changed <strong>[exact part]</strong> because the audience needs <strong>[clearer meaning or action]</strong>.</p>",
            "FALLBACK": "<p>Partner attendance and camera use are not required. Use a teacher conference, private recording, or AAC make-up. A written outline supports oral evidence but does not automatically replace it.</p>",
        },
        3: {
            "TITLE": "BrainBoost Decision and Career Outline",
            "PURPOSE": "Use FYF campaign evidence to separate a cause from a result, choose a bounded solution, and organize career evidence.",
            "TODAY": "<ul><li>analyze the supplied campaign;</li><li>generate and screen solutions;</li><li>complete the FYF campaign plan;</li><li>record individual problem-solving and career evidence.</li></ul>",
            "READY": f'<p><strong>Start in FYF pp. 244-247.</strong> Use {student_copy_link(3, "the two-page individual decision and career-outline companion")} or <a href="{urls[3]}">the private annotation activity</a> for the evidence the workbook does not collect.</p>',
            "MEDIA": media([("p244", "BrainBoost scenario and email evidence"), ("p245", "Social and in-store evidence, customer feedback, and problem statement"), ("p246", "Solution brainstorm and three-idea screening table"), ("p247", "Mini campaign plan, share and reflection prompts")]),
            "STEPS": step(1, "Find the cause", "<p>The campaign reached the stated audience. Low sales are the result; use the customer comments to name a possible message or value cause.</p>") + step(2, "Generate and screen", "<p>Complete FYF p. 246. Reject any solution that invents a health, nutrition, discount, scarcity, popularity, testimonial, or data claim.</p>") + step(3, "Build the FYF campaign plan", "<p>Complete p. 247, then record your own cause/evidence decision and cross-career problem-solving connection.</p>") + step(4, "Outline the career brief", "<p>Use one fixed BLS card or previously verified evidence. Keep the occupation, duty, preparation, measure, date, geography, and limitation together.</p>"),
            "EXIT": "<p>State the result, possible cause, evidence, and the next evidence step in a second career.</p>",
            "DONE": "<ul><li>FYF/no-workbook BrainBoost work;</li><li>individual cause and evidence decision;</li><li>rejected unsupported claim;</li><li>two-career transfer;</li><li>complete oral outline.</li></ul>",
            "SUPPORT": "<p><strong>Word bank:</strong> result/resultado · cause/causa · evidence/evidencia · screen/evaluar · limitation/limitacion.</p><p><strong>Use this frame:</strong> The result is <strong>[result]</strong>, but <strong>[evidence]</strong> suggests the cause may be <strong>[cause]</strong>. A <strong>[second career]</strong> would next check <strong>[evidence]</strong>.</p>",
            "FALLBACK": "<p>The locked FYF images plus the two-page companion are the complete no-workbook route. The fixed career cards remove the need for H&amp;L, prior portfolio work, or open-web research.</p>",
        },
        4: {
            "TITLE": "Interview Appearance and Rehearsal",
            "PURPOSE": "Choose interview preparation for the actual context, then rehearse and revise your career brief.",
            "TODAY": "<ul><li>compare office, task-demonstration, and virtual contexts;</li><li>complete a retryable Quiz;</li><li>rehearse once;</li><li>revise and rehearse again.</li></ul>",
            "READY": f'<p>Open {student_copy_link(4, "the two-page landscape appearance and rehearsal companion")}, <a href="{urls[4]}">the private rehearsal-record activity</a>, and <a href="{urls["quiz"]}">the retryable practice Quiz</a>. Use one record route; do not complete both print and digital copies.</p>',
            "MEDIA": "",
            "STEPS": step(1, "Use the context", "<p>Base the choice on workplace, task, safety, format, and accommodation--not cost, body, gender, culture, religion, or disability.</p>") + step(2, "Make three decisions", "<p>Choose and explain preparation for an office/customer-facing interview, a skilled-trade task demonstration, and a virtual interview. Write one respectful question to verify for each.</p>") + step(3, "Use Quiz feedback", "<p>Check safety, source labels, virtual readiness, and the oral-route boundary. Retry after reading the feedback.</p>") + step(4, "Rehearse twice", "<p>Use a live, conference, private recording, or AAC route. Keep the revision visible between attempts.</p>"),
            "EXIT": "<p>Name one final content check and one final delivery/AAC check.</p>",
            "DONE": "<ul><li>three context decisions and questions;</li><li>access/safety reasoning;</li><li>Quiz feedback reviewed;</li><li>two timed oral/AAC career rehearsals;</li><li>one appropriate technology choice;</li><li>visible revision.</li></ul>",
            "SUPPORT": "<p><strong>Word bank:</strong> workplace/lugar de trabajo · task/tarea · safety/seguridad · accommodation/adaptacion · verify/verificar.</p><p><strong>Use this frame:</strong> For <strong>[context]</strong>, I would choose <strong>[functional choice]</strong> because <strong>[task, safety, or access reason]</strong>. I would verify <strong>[question]</strong>.</p>",
            "FALLBACK": "<p>No clothing modeling or personal body, cost, culture, religion, disability, or gender disclosure. Use a private rehearsal route. If video or bandwidth fails, use audio, phone, AAC, or an approved reschedule.</p>",
        },
        5: {
            "TITLE": "Career Oral Evidence Brief",
            "PURPOSE": "Deliver a concise career brief with accurate source labels, then use the feedback profile to plan one visible revision.",
            "TODAY": "<ul><li>run the final source and content check;</li><li>deliver 60-90 seconds through your assigned oral/AAC route;</li><li>record transfer evidence;</li><li>self-score and revise.</li></ul>",
            "READY": f'<p>Open {student_copy_link(5, "the two-page Career Oral Evidence Brief")}, {link(files["RUBRIC"]["id"], "the two-page formative feedback profile")}, and the private submission below. Use your Day 3 career outline and Day 4 rehearsal as reference; do not submit every earlier packet.</p>',
            "MEDIA": '<details style="border:1px solid #b9d9de;border-radius:8px;padding:12px 16px;margin:18px 0"><summary style="font-weight:700;color:#245f69;cursor:pointer">Optional FYF presentation references</summary>' + "".join([prior.image_tag(visuals["p299"]["id"], "Prepare and Present checklist and presentation tips; this capstone page is a reference only"), prior.image_tag(visuals["p280"]["id"], "FYF capstone rubric including Presenter Delivery; this page is a reference only")]) + "</details>",
            "STEPS": step(1, "Check the source labels", "<p>Career, duty/work product, preparation, measure, amount, geography, date/source, limitation, bounded conclusion, and time.</p>") + step(2, "Deliver through your assigned route", "<p>Whole group, small group, teacher conference, private recording, or AAC. Use the appropriate technology choice recorded on your brief. The route changes; the evidence does not.</p>") + step(3, "Transfer the skill", "<p>Explain how one communication skill works in two different careers.</p>") + step(4, "Self-score and revise", "<p>Use all four criteria. Keep the before/after revision visible and submit only the brief plus rubric/self-score.</p>") + submission_panel,
            "EXIT": "<p>State your strongest exact evidence and the revision you would make next.</p>",
            "DONE": "<ul><li>60-90-second oral/AAC brief;</li><li>appropriate technology choice;</li><li>correct source labels and limitation;</li><li>delivery evidence;</li><li>two-career transfer;</li><li>self-score and visible revision.</li></ul>",
            "SUPPORT": "<p><strong>Word bank:</strong> work product/producto de trabajo · preparation/preparacion · median/mediana · limitation/limitacion · source/fuente.</p><p><strong>Use this frame:</strong> A <strong>[career]</strong> creates or studies <strong>[work product]</strong>. The source reports <strong>[measure and amount]</strong> for <strong>[geography/date]</strong>, but it does not prove <strong>[limit]</strong>.</p>",
            "FALLBACK": "<p>Use a supervised conference, private recording, or AAC make-up. Written-only work is not mislabeled oral evidence unless an accommodation changes the task. No public Discussion or family-adult dependency.</p>",
        },
    }


def teacher_content(files):
    link, flow = common.file_link, common.flow
    color = "#245f69"
    sources = '<p><a href="https://cloudfront.careeronestop.org/JobSearch/Interview/interview-and-negotiate.aspx?frd=true">CareerOneStop Interview Guidance</a> · <a href="https://cloudfront.careeronestop.org/Veterans/JobSearch/Interviews/dress-for-success.aspx?frd=true">CareerOneStop Appearance Guidance</a> · <a href="https://www.bls.gov/ooh/management/sales-managers.htm">BLS Sales Managers</a> · <a href="https://www.bls.gov/ooh/business-and-financial/market-research-analysts.htm">BLS Market Research Analysts</a> · <a href="https://www.bls.gov/ooh/arts-and-design/graphic-designers.htm">BLS Graphic Designers</a> · <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte/macarthur-high-school">Irving ISD MacArthur CTE</a>.</p>'
    support = "<p>Point-of-use word banks and complete sentence frames appear before the student steps. Companion prompts are sized for the requested answer: short labels use one line; reasons and transfer explanations use two or three full-width lines. Accept typing, dictation, annotation, enlarged print, live/private recording, or AAC. Score evidence and meaning, not English mechanics unless meaning is unclear.</p>"
    fallback = "<p>Locked FYF pages support projection and absence. Students use the workbook first and one companion route for evidence the workbook does not collect; do not make them complete both the workbook and a duplicate packet. H&amp;L, Xello, eDynamic, public Discussion, real sales/posts/accounts/data, clothing expense/modeling, family contact information, and camera use are not required.</p>"
    return {
        1: {
            "TITLE": "Audience and Sales Pitch Plan",
            "SUBTITLE": "50 minutes · FYF pp. 241-243",
            "ALERT": "<strong>Workbook first:</strong> FYF holds the seven-step pitch activity. The two-page companion adds audience/assumption, ethical, career, transfer, and oral-route evidence; it does not replace FYF for students who have the workbook.",
            "PREP": f'<ul><li><strong>Per student:</strong> FYF pp. 241-243, pencil, and one {link(files["PLAN"]["id"], "two-page companion")} by private annotation or print.</li><li><strong>Model:</strong> <em>Audience: busy students. Fact: the fictional service offers 20-minute review sessions. Benefit: review can fit between activities. Safe action: compare the two session options. Do not claim it guarantees a grade.</em></li><li>Preassign Day 2 live, conference, recording, or AAC routes; use one labeled tray or private collector.</li></ul>',
            "EVIDENCE": "<p>Collect the FYF pitch plus the individual audience/fact/assumption check, accuracy/privacy boundary, career/work-product connection, transferable skill, and selected Day 2 oral route.</p>",
            "FLOW": (
                flow(color, "Minutes 0-5 - Welcome and persuasive sales pitch anatomy warm-up", '''<p>Welcome students to Week 4 of 6SW (Sales &amp; Professional Presentations) and project the persuasive pitch prompt.</p><ul><li>Ask students: <em>“When someone tries to sell you something—whether it's an app subscription, a pair of sneakers, or a school fundraiser candy bar—what immediately turns you off versus what genuinely grabs your attention? Why are manipulative guarantees and manufactured urgency less effective than clear problem-solving and authentic benefits?”</em></li><li>Collect 2-3 student thoughts: Pushy salespeople sound fake; great communicators explain how something actually helps you!</li><li>Bridge with, <em>“Sales is a critical business discipline built on empathy, audience analysis, and clear communication. Today we examine FYF pp. 241-243 ('SparkClean' case study), analyze the 4-part anatomy of a professional pitch, and author an ethical sales proposal.”</em></li></ul>''')
                + flow("#4c8b38", "Minutes 5-13 - Deconstructing the 4-part pitch anatomy &amp; ethical claims", '''<p>Deconstruct the 4 Core Pillars of a Persuasive Sales Pitch on the main screen:</p><ul><li>1. <strong>The Hook (15-20s):</strong> Captures immediate audience attention with a relatable question, surprising statistic, or relevant problem scenario.</li><li>2. <strong>The Problem &amp; Offering (30s):</strong> Defines the customer's pain point and introduces the specific product or service that solves it.</li><li>3. <strong>Audience-Centered Benefits (30s):</strong> Contrasts features with benefits: Features are what the product *is*; benefits are what the product *does for the customer* (e.g., feature: 20-minute study session; benefit: fits into a busy athletic schedule).</li><li>4. <strong>The Clear Call to Action (CTA) (15s):</strong> Directs the audience to one unambiguous, low-risk next step (e.g., <em>“Compare our two trial options today”</em>).</li><li>Ethical &amp; Truthful Boundaries: Remove all unsupported claims—no health guarantees, fake popularity ('everyone has one!'), artificial scarcity ('only 1 left!'), or get-rich-quick income promises.</li></ul>''')
                + flow("#8e4f7a", "Minutes 13-33 - FYF sales pitch authoring sprint (FYF pp. 241-243)", '''<p>Students craft their 4-part sales pitch in FYF and complete their 2-page companion:</p><ul><li>Select a supplied product scenario and profile the target customer's daily routine and pain points.</li><li>Draft Pitch Architecture: Author Hook, Problem/Offering, Two Distinct Benefits, and Ethical CTA.</li><li>Complete Companion Analysis: Separate verified product facts from unproven marketing assumptions.</li><li>Career Connection: Explain how Sales Managers, Real Estate Agents, and Technical Consultants utilize persuasive pitch structure in daily client briefings.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 20): Check that students distinguish features from customer benefits.<br>• Lap 2 (Minute 28): Verify that CTAs provide a specific, low-risk action without exaggerated claims.</li></ul>''')
                + flow("#d39b22", "Minutes 33-45 - Partner ethical claim audit &amp; Day 2 route selection", '''<p>Elbow partners audit each other's pitch scripts:</p><ul><li>Partner checks for ethical boundaries: 'Are there any fake guarantees or manufactured urgency?'</li><li>Students select their Day 2 Oral Delivery Route: (1) Live partner rehearsal, (2) Private teacher conference, (3) Private audio/video recording, or (4) Speech-generating AAC device.</li></ul>''')
                + flow(color, "Minutes 45-50 - Submit Day 1 Companion and wrap-up", '''<p>Students submit their completed companion in Canvas or place paper copies in the collection tray.</p><ul><li><strong>Safe Trim:</strong> Skip general sharing; fiercely protect the 4-part pitch outline, ethical claim audit, delivery route selection, and private exit.</li></ul>''')
            ),
            "MONITOR": "<p><strong>Minute 13:</strong> students can point to hook, offer, benefit, and call to action. If one-third confuse feature and benefit, contrast <em>20-minute session</em> with <em>fits between activities</em>. <strong>Minute 30:</strong> each pitch names an audience situation and supplied fact or labeled reason. <strong>Minute 44:</strong> the companion has the ethical boundary, career connection, and Day 2 route. Safe trim: remove optional sharing, not the four pitch parts or companion evidence. Collect one route and return workbooks.</p>",
            "RESOURCES": sources,
            "SUPPORT": support,
            "FALLBACK": fallback,
        },
        2: {
            "TITLE": "Deliver, Test, and Revise",
            "SUBTITLE": "50 minutes · FYF p. 243",
            "ALERT": "<strong>Oral evidence with equal private routes:</strong> partner attendance and camera use are not requirements. A written draft supports the delivery but does not automatically replace oral/AAC evidence.",
            "PREP": f'<ul><li><strong>Per student:</strong> Day 1 pitch, pencil, and one {link(files["DELIVERY"]["id"], "two-page delivery record")} by private annotation or print; one timer serves the class.</li><li><strong>Model:</strong> Before: <em>Sign up now.</em> Feedback: the next step is vague. After: <em>Compare the two fictional session options and circle the one that fits your schedule.</em> Effect: the audience knows the safe next action.</li><li>Confirm live, conference, recorded, and AAC routes before class; pairs share feedback, not devices or files.</li></ul>',
            "EVIDENCE": "<p>Collect two timed oral/AAC attempts, one exact feedback point, visible before/after revision, evidence of its effect, and a two-career transfer response.</p>",
            "FLOW": (
                flow(color, "Minutes 0-5 - Welcome and professional oral delivery modeling warm-up", '''<p>Welcome students, seat them with their Day 1 pitch script and delivery record, and project the oral delivery prompt.</p><ul><li>Ask students: <em>“When delivering a professional presentation, why does pacing, vocal variety, and structured pausing matter just as much as the words on the page? How can rushing through a pitch in 20 seconds destroy your credibility?”</em></li><li>Collect 2-3 student thoughts: Rushing makes you sound nervous or dishonest; clear pauses give listeners time to understand!</li><li>Bridge with, <em>“Public speaking is an iterative skill honed through structured practice and targeted feedback. Today we execute Attempt 1 of our product pitch, gather specific peer or conference feedback, implement a visible revision, and deliver Attempt 2.”</em></li></ul>''')
                + flow("#4c8b38", "Minutes 5-10 - Silent accuracy screening &amp; delivery criteria", '''<p>Display the Delivery Evaluation Criteria on the main screen:</p><ul><li>1. <strong>Understandable Pacing &amp; Articulation:</strong> Aim for 60-90 seconds; speak at a measured pace with deliberate pauses after key points.</li><li>2. <strong>Clear Structural Signposts:</strong> Use transition words (<em>“First,” “The primary benefit is,” “Here is how to get started”</em>) so the audience can track the argument.</li><li>3. <strong>Safe, Unambiguous Call to Action:</strong> Close with a clear directive that empowers the listener.</li><li>Silent Accuracy Screening (Minutes 7-10): Students spend 3 minutes silently reviewing their script to cross out any remaining buzzwords, fake urgency, or exaggerated claims before speaking.</li></ul>''')
                + flow("#8e4f7a", "Minutes 10-25 - Attempt 1 delivery &amp; targeted peer/conference feedback", '''<p>Students deliver Attempt 1 across their designated technology routes:</p><ul><li>Deliver 60-90s pitch to partner, during teacher conference, or via private recording/AAC device.</li><li>Listener logs exact time and provides targeted, actionable feedback using the 2-part feedback frame:<br>• <strong>Exact Strength:</strong> <em>“Your hook effectively highlighted the time crunch students face.”</em><br>• <strong>Specific Revision Needed:</strong> <em>“Your call to action was too rushed; slow down and specify exactly where to click.”</em></li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 15): Ensure partners use timing devices and stay within the 60-90s target window.<br>• Lap 2 (Minute 21): Stop vague praise like 'it was good'; require specific word or sentence critiques.</li></ul>''')
                + flow("#d39b22", "Minutes 25-35 - Script revision &amp; before-and-after documentation", '''<p>Students execute a visible revision on page 2 of their delivery record:</p><ul><li>Document 'Before' phrasing, partner feedback, and revised 'After' phrasing.</li><li>Practice the revised section silently or in a whisper run.</li></ul>''')
                + flow("#4c8b38", "Minutes 35-45 - Attempt 2 delivery &amp; transferable communication synthesis", '''<p>Students deliver Attempt 2 incorporating their revision:</p><ul><li>Deliver second attempt and log new time in delivery record.</li><li>Complete Transferable Skill Synthesis: Explain how structured pitching techniques transfer to job interviews, high school team projects, and client presentations.</li></ul>''')
                + flow(color, "Minutes 45-50 - Submit Day 2 Delivery Record and wrap-up", '''<p>Students submit their delivery record in Canvas; teacher records checkoff on class roster.</p><ul><li><strong>Safe Trim:</strong> Shorten class debrief; fiercely protect Attempt 1, specific feedback, visible revision, Attempt 2, and private record submission.</li></ul>''')
            ),
            "MONITOR": "<p><strong>Minute 15:</strong> each student has Attempt 1 time and one exact strength. If one-third give trait feedback, reproject the before-feedback-after model. <strong>Minute 31:</strong> before and after language is visible and the reason names the audience need. <strong>Minute 44:</strong> Attempt 2 time, effect, and transfer are recorded. Do not score accent, eye contact, memorization, confidence, or camera use. Safe trim: remove share-outs and finish transfer in catch-up; preserve Attempt 2 and visible revision. Collect one record.</p>",
            "RESOURCES": sources,
            "SUPPORT": support,
            "FALLBACK": fallback,
        },
        3: {
            "TITLE": "BrainBoost Decision and Career Outline",
            "SUBTITLE": "50 minutes · FYF pp. 244-247",
            "ALERT": "<strong>Workbook first:</strong> FYF holds the campaign analysis, brainstorm, three-solution table, and mini campaign plan. The companion adds individual cause/evidence, claim screening, transfer, and career-outline evidence.",
            "PREP": f'<ul><li><strong>Per student:</strong> FYF pp. 244-247, pencil, and one {link(files["BRAIN"]["id"], "two-page companion")} by private annotation or print.</li><li><strong>Cause/evidence model:</strong> <em>Result: sales are low. Evidence: students say the snack looks like other snacks and the reason to try it is unclear. Possible cause: the campaign does not communicate a distinct value.</em></li><li><strong>Career-outline model:</strong> <em>Market research analysts study consumer preferences. A bachelor\'s degree is typical. BLS reports a $76,950 May 2024 U.S. median and 7% projected growth for 2024-34. Those measures are not DFW starting pay or a guarantee.</em></li></ul>',
            "EVIDENCE": "<p>Collect FYF BrainBoost work plus an individual cause/evidence decision, rejected unsupported claim, cross-career problem-solving response, and complete fixed-source career outline. Oral evidence begins on Day 4; the outline itself is not mislabeled d(4)(C).</p>",
            "FLOW": (
                flow(color, "Minutes 0-5 - Welcome and diagnosing business failure warm-up", '''<p>Welcome students, seat them with FYF workbooks (pp. 244-247) or companions, and project the marketing rescue prompt.</p><ul><li>Ask students: <em>“When a product launches with heavy advertising but sales plummet after two weeks, is the low sales number the actual problem or merely the symptom? What underlying root causes might explain why customers didn't buy?”</em></li><li>Collect 2-3 student thoughts: The price was too high, the packaging was confusing, or the ad didn't explain why anyone needed it!</li><li>Bridge with, <em>“Business leaders solve complex operational problems by analyzing root causes rather than symptoms under TEKS d(4)(B). Today we complete the 'BrainBoost' marketing rescue on FYF pp. 244-247, and author our 60-90 second career evidence brief outline.”</em></li></ul>''')
                + flow("#4c8b38", "Minutes 5-13 - Root cause analysis vs. symptom &amp; career brief architecture", '''<p>Display the BrainBoost Scenario Evidence and Career Brief Structure on the screen:</p><ul><li>1. <strong>The BrainBoost Dilemma (FYF pp. 244-247):</strong> 'BrainBoost' energy snack bars launched to teens, but sales are 75% below forecast. Focus-group data reveals: packaging looks like medicine, claims of 'brain power' sound unbelievable, and students don't know when to eat it.</li><li>2. <strong>Root Cause vs. Symptom:</strong> Low sales is the *result*; the *cause* is confusing product positioning and unverified medical claims!</li><li>3. <strong>The 3-Solution Rescue Plan:</strong> Screen potential turnaround strategies; eliminate any that rely on fake health claims or deceptive influencer testimonials.</li><li>4. <strong>Deconstruct the 60-90 Second Career Evidence Brief Outline (TEKS d(4)(C)):</strong><br>• Opening &amp; Career Target (15s): State occupation and core work product.<br>• Preparation Route (20s): Degree, postsecondary pathway, or certification required.<br>• Sourced Labor Evidence (25s): May 2024 BLS median wage, 2024-34 outlook, and annual openings with complete statistical labels.<br>• Evidence Limitation &amp; Next Action (15s): Note that national medians do not guarantee DFW starting pay, and state concrete next step.</li></ul>''')
                + flow("#8e4f7a", "Minutes 13-33 - FYF BrainBoost turnaround &amp; career outline authoring sprint", '''<p>Students analyze the data in FYF and complete their 2-page companion:</p><ul><li>Part 1 (BrainBoost Rescue): Complete the 3-solution turnaround matrix; select the best evidence-based campaign revision; reject all unsupported medical claims.</li><li>Part 2 (Career Evidence Brief Outline): Select target career (from prior research or supplied BLS cards: Market Research Analyst, Sales Manager, Graphic Designer). Draft structured bullet points for all 4 briefing segments.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 21): Ensure students identify confusing positioning as the root cause, not 'teenagers don't like snacks.'<br>• Lap 2 (Minute 29): Verify career outlines contain complete BLS labels (measure, amount, geography, date).</li></ul>''')
                + flow("#d39b22", "Minutes 33-45 - Partner outline audit &amp; claim screening", '''<p>Elbow partners audit each other's career outlines:</p><ul><li>Partner verifies: 'Does the outline include a national labor limitation? Does it name a concrete next action?'</li><li>Execute One Outline Edit: Refine phrasing to ensure the speech flows logically within 60-90 seconds.</li></ul>''')
                + flow(color, "Minutes 45-50 - Submit Day 3 Companion and wrap-up", '''<p>Students submit their completed companion in Canvas or file paper packets.</p><ul><li><strong>Safe Trim:</strong> Provide pre-written BrainBoost solution options; fiercely protect root-cause analysis, career outline completion, BLS labels, and private submission.</li></ul>''')
            ),
            "MONITOR": "<p><strong>Minute 13:</strong> students distinguish the low-sales result from a message/value cause. If one-third blame the audience, reread the supplied reach fact and comments. <strong>Minute 31:</strong> each chosen solution answers exact evidence and adds no claim. <strong>Minute 44:</strong> the career outline keeps duty, preparation, measure, geography/date, and limitation together. Safe trim: remove campaign sketch polish and provide the fixed career card; preserve cause/evidence, rejected claim, transfer, and outline. Collect the companion.</p>",
            "RESOURCES": sources,
            "SUPPORT": support,
            "FALLBACK": fallback,
        },
        4: {
            "TITLE": "Interview Appearance and Rehearsal",
            "SUBTITLE": "50 minutes · Context-first CCE lesson",
            "ALERT": "<strong>Appearance is a job-context decision:</strong> workplace, task, safety, format, and accommodation determine the plan. Do not teach cost, body, gender, culture, religion, disability, or fashion taste as professionalism.",
            "PREP": f'<ul><li><strong>Per student:</strong> one {link(files["APPEAR"]["id"], "two-page landscape companion")}, the private rehearsal-record Assignment, pencil, Quiz access, and the Day 3 outline. One timer serves the class. Students use one Canvas or paper record route, not both.</li><li>Preassign live, conference, private recording, or AAC routes. Every route names appropriate technology: timer plus evidence card/approved visual, private recording, or AAC device.</li><li><strong>Rehearsal model:</strong> <em>Attempt 1 omitted the labor-evidence limit. Revision: add “This U.S. median does not guarantee my pay.” Attempt 2 includes the limit while the Canvas evidence card keeps the source label visible.</em></li></ul>',
            "EVIDENCE": "<p>Collect three context decisions and respectful verification questions, Quiz-feedback review, two timed oral/AAC career rehearsals, one appropriate technology choice, visible revision, and evidence of what changed.</p>",
            "FLOW": (
                flow(color, "Minutes 0-5 - Welcome and context-first interview appearance warm-up", '''<p>Welcome students, seat them with devices or the 2-page landscape companion, and project the interview attire prompt.</p><ul><li>Ask students: <em>“If you were interviewing for an apprentice electrician job at a major commercial construction site, would wearing a 3-piece business suit demonstrate professionalism? Why is professional interview appearance entirely dependent on the specific workplace context, task requirements, and safety standards?”</em></li><li>Collect 2-3 student thoughts: Wearing a suit on a jobsite is impractical and unsafe; steel-toe boots and work shirts show you know the job!</li><li>Bridge with, <em>“Professionalism is context-dependent, safety-first, and task-driven under TEKS d(6)(B). Today we evaluate appropriate appearance across 3 distinct workplace scenarios, and rehearse our 60-90 second career evidence brief.”</em></li></ul>''')
                + flow("#4c8b38", "Minutes 5-17 - 3 interview contexts, virtual protocols &amp; respectful verification", '''<p>Display the 3 Context-Driven Workplace Scenarios and Virtual Standards on the screen:</p><ul><li>1. <strong>Scenario A (Corporate / Customer-Facing Office):</strong> Business casual/professional; clean pressed attire, neutral colors, closed-toe shoes; verify company dress code in advance.</li><li>2. <strong>Scenario B (Skilled Trades / Hands-On Task Demonstration):</strong> Clean, durable work pants (jeans/canvas), work boots (steel-toe if required), hair tied back, zero dangling jewelry, safety glasses/PPE; verify tool and site safety rules with the hiring manager.</li><li>3. <strong>Scenario C (Virtual / Remote Video Interview):</strong> Professional upper-body attire, clean quiet space, neutral/blurred background, lighting in front of face (not behind), microphone and webcam tested, notifications silenced; establish a backup phone route in case Wi-Fi drops.</li><li>Universal Access &amp; Anti-Bias Principle: Professionalism is never determined by brand names, expensive clothing, hair texture, cultural dress, or disability accommodations!</li><li>Formulating Respectful Inquiries: Model how an applicant contacts HR to ask: <em>“Could you clarify the expected dress code and safety gear for the on-site walkthrough portion of the interview?”</em></li></ul>''')
                + flow("#8e4f7a", "Minutes 17-25 - Practice Quiz &amp; scenario analysis sprint", '''<p>Students analyze the 3 scenarios and complete the practice check:</p><ul><li>Document appearance decisions and respectful verification questions for all 3 scenarios.</li><li>Complete the 5-question retryable Canvas Quiz to reinforce safety gear, virtual interview readiness, and oral delivery standards.</li></ul>''')
                + flow("#d39b22", "Minutes 25-45 - Career brief Rehearsals 1 &amp; 2 sprint", '''<p>Students execute two timed rehearsals of their 60-90 second career brief:</p><ul><li>Rehearsal 1 (Minutes 25-33): Partner timer or device timer logs exact seconds. Partner checks for complete BLS labels and labor limitation.</li><li>Specific Feedback &amp; Revision (Minutes 33-38): Identify one exact delivery or content fix (e.g., 'Add the 2024-34 date to your growth percentage').</li><li>Rehearsal 2 (Minutes 38-45): Deliver second run; verify timing sits between 60 and 90 seconds.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 29): Verify students speak for at least 60 seconds.<br>• Lap 2 (Minute 41): Confirm students record the effect of their revision on the companion.</li></ul>''')
                + flow(color, "Minutes 45-50 - Submit Day 4 Companion and wrap-up", '''<p>Students submit their completed companion in Canvas and prepare for Day 5 presentations.</p><ul><li><strong>Safe Trim:</strong> Defer multiple Quiz retries; fiercely protect the 3 context appearance decisions, both timed rehearsals, visible revision, and private submission.</li></ul>''')
            ),
            "MONITOR": "<p><strong>Models:</strong> office/customer-facing = clean functional clothing plus workplace/access verification; task demonstration = clean work clothing plus exact site PPE/tool verification; virtual = tested audio, private background, notifications off, backup route, and verified access expectations. <strong>Minute 17:</strong> each scenario has a functional choice and question. If one-third write fashion rules, return to workplace/task/safety/format/accommodation. <strong>Minute 33:</strong> Attempt 1 includes oral/AAC evidence and named technology. <strong>Minute 45:</strong> Attempt 2 and revision are complete. Safe trim: leave the Quiz for catch-up and remove class modeling; preserve both rehearsals and technology evidence. Collect the companion and close devices.</p>",
            "RESOURCES": sources,
            "SUPPORT": support,
            "FALLBACK": fallback,
        },
        5: {
            "TITLE": "Career Oral Evidence Brief",
            "SUBTITLE": "50 minutes · Formative Week 4 evidence",
            "ALERT": "<strong>No separate Week 4 grade:</strong> this is planned formative rehearsal for the Week 5 interview and Week 6 capstone. Every student still needs assessable oral/AAC evidence through an assigned route.",
            "PREP": f'<ul><li><strong>Per student:</strong> one {link(files["ORAL"]["id"], "two-page Career Oral Evidence Brief")}, one {link(files["RUBRIC"]["id"], "two-page feedback profile")}, Day 3 outline, and assigned technology. One class roster/checkoff and timer are required.</li><li>Before class assign slots, parallel groups, conferences, private recordings, or AAC. Checkoff fields: <strong>student, career, date, route, seconds, technology used, oral/AAC complete, written record complete</strong>.</li><li><strong>Complete model:</strong> <em>I am exploring market research analysis because the work studies what audiences need. Analysts collect and explain consumer evidence; a bachelor\'s degree is typical. BLS reports a $76,950 May 2024 U.S. median and 7% projected growth for 2024-34. Those measures do not guarantee DFW starting pay. My next step is to compare the work with graphic design.</em></li><li>Keep FYF pp. 280 and 299 as teacher references only.</li></ul>',
            "EVIDENCE": "<p>Collect a 60-90-second oral/AAC career brief with one appropriate technology choice, duty/work product, preparation, correctly labeled labor evidence, limitation, bounded conclusion, and understandable organization; add delivery evidence, two-career transfer, self-score, and one visible revision.</p>",
            "FLOW": (
                flow(color, "Minutes 0-5 - Welcome and oral briefing readiness gate warm-up", '''<p>Welcome students, execute the oral briefing readiness gate, and project the delivery prompt.</p><ul><li><strong>Readiness Gate (Minutes 0-4):</strong> Students retrieve their Day 3 outline and Day 4 companion; confirm their assigned technology route (Live small group, Teacher conference, Private Canvas recording, or AAC device).</li><li>Ask students: <em>“When delivering a professional oral brief, why is confidence rooted in preparation and evidence rather than theatrics? How does using an evidence card or presentation tool keep your message focused and credible?”</em></li><li>Collect 2-3 student thoughts: Knowing your facts keeps you calm; an evidence card ensures you don't forget numbers!</li><li>Bridge with, <em>“Today is our Career Oral Evidence Brief under TEKS d(4)(C)! Every student delivers a structured 60-90 second presentation using appropriate technology, completes their reflection, and self-scores on our 16-point rubric.”</em></li></ul>''')
                + flow("#4c8b38", "Minutes 5-40 - Dedicated oral/AAC briefing delivery window", '''<p>Teacher manages the structured briefing queue while students execute assigned delivery modes:</p><ul><li>Queue Management: Conduct teacher-conference briefings and small-group live deliveries at the teacher station while parallel groups record in quiet corners or test AAC devices.</li><li>Teacher Logs Active Checkoff Sheet: Record student name, target career, date, technology route, exact elapsed seconds, oral completion status, and written submission status.</li><li>Independent Work for Waiting Students: Students awaiting conferences complete their 2-page brief reflection, rubric self-score, and cross-career transfer analysis.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 15): Ensure quiet environment for students recording on Chromebooks or using AAC devices.<br>• Lap 2 (Minute 30): Check off at least 70% of the class roster; verify that student delivery times remain between 60 and 90 seconds.</li></ul>''')
                + flow("#8e4f7a", "Minutes 40-47 - Rubric self-score &amp; visible evidence repair", '''<p>Students finalize their 2-page Career Oral Evidence Brief:</p><ul><li>Score performance against the 16-point formative rubric: Content Accuracy, Labor Evidence &amp; Limitations, Professional Delivery &amp; Organization, and Appropriate Technology Use.</li><li>Document One Visible Revision: Make an immediate text edit to elevate their written reflection or outline.</li></ul>''')
                + flow("#d39b22", "Minutes 47-50 - Week 5 preview, submission &amp; wrap-up", '''<p>Students submit their completed briefs in Canvas and preview Week 5:</p><ul><li>Recording route students submit written brief + media file in Canvas. Live/conference/AAC students submit written brief while teacher finalizes checkoff roster.</li><li>Preview Week 5: <em>“Next week we step into the hot seat for our CCE Job Skills &amp; Mock Interview module!”</em></li><li><strong>Safe Trim:</strong> Finish remaining conferences asynchronously; fiercely protect oral/AAC evidence checkoff, written brief completion, and private submission.</li></ul>''')
            ),
            "MONITOR": "<p><strong>Minute 5:</strong> every student has a route, slot, and named technology. If one-third are not ready, use the complete fixed model and conference queue. <strong>Minute 25:</strong> the checkoff shows at least half of oral/AAC routes complete while waiting students finish written evidence. <strong>Minute 43:</strong> each student has oral/AAC completion plus written record/self-score or a named make-up slot. Recorded route submits written record plus media together. Live/conference/AAC route submits written record while the teacher completes the named checkoff. Text alone is not oral evidence. Safe trim: remove public sharing and preview; preserve oral/AAC evidence, technology, written record, and checkoff.</p>",
            "RESOURCES": sources,
            "SUPPORT": support,
            "FALLBACK": fallback,
        },
    }


async def main():
    preflight()
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    support_paths = {key: ROOT / "docs/resources/worksheets" / name for key, name in WORKSHEET_NAMES.items()}
    visual_paths = {f"p{page}": ASSETS / f"fyf-p{page}.jpg" for page in VISUAL_PAGES}

    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        existing_assignments, _existing_quiz = await canvas_preflight(client)
        module = await ensure_module(client)
        support_path = "course files/CCR Materials/6SW/Wk4"
        support_folder = await common.ensure_folder(client, support_path)
        files = {key: await upload_locked(client, path, support_path) for key, path in support_paths.items()}
        visual_path = "course files/CCR Materials/6SW/Wk4/Locked Licensed Visuals"
        visual_folder = await common.ensure_folder(client, visual_path)
        visuals = {key: await upload_locked(client, path, visual_path) for key, path in visual_paths.items()}
        support_folder, _support_count = await lock_folder_files(client, support_folder, [path.name for path in support_paths.values()])
        visual_folder, _visual_count = await lock_folder_files(client, visual_folder, [path.name for path in visual_paths.values()])

        quiz = await upsert_quiz(client)
        routes = ["student_annotation", "online_upload", "online_text_entry"]
        descriptions = {
            1: "<p>Complete the FYF pitch first. Submit only the two-page companion by annotation, one PDF/photo upload, or labeled text. This private formative activity is 0 points, omitted from the final grade, and unpublished for teacher transfer.</p>",
            2: "<p><strong>Two parts are required.</strong> Recorded route: upload the completed two-page delivery record and private audio/video together as files in one submission. Live, conference, or AAC route: submit the written record by annotation, upload, or labeled text; the teacher records student, date, route, both attempt times, feedback/revision, and oral/AAC completion on the class checkoff. Text alone is not oral evidence. This private formative activity is 0 points, omitted from the final grade, and unpublished for teacher transfer.</p>",
            3: "<p>Complete FYF BrainBoost first. Submit only the two-page individual companion by annotation, one PDF/photo upload, or labeled text. This private formative activity is 0 points, omitted from the final grade, and unpublished for teacher transfer.</p>",
            4: "<p>Submit one two-page rehearsal record by annotation, one PDF/photo upload, or exact labeled text. Record all three context decisions, both oral/AAC rehearsal attempts, the technology actually used, and one visible revision. The retryable Quiz is feedback; it is not a substitute for this record. This private formative activity is 0 points, omitted from the final grade, and unpublished for teacher transfer.</p>",
        }
        assignments = {
            day: await upsert_formative_assignment(
                client,
                existing_assignments[day],
                TITLES[day],
                descriptions[day],
                files[key]["id"],
                routes,
            )
            for day, key in {1: "PLAN", 2: "DELIVERY", 3: "BRAIN"}.items()
        }
        assignments[4] = await upsert_formative_assignment(
            client,
            existing_assignments[4],
            DAY4_ASSIGNMENT_TITLE,
            descriptions[4],
            files["APPEAR"]["id"],
            routes,
        )
        final_description = (
            f'<p><strong>Two parts are required.</strong> Use {common.file_link(files["ORAL"]["id"], "the two-page Career Oral Evidence Brief")} and '
            f'{common.file_link(files["RUBRIC"]["id"], "the two-page feedback profile and self-score")}. '
            "<strong>Recorded route:</strong> upload the completed brief/rubric and private audio/video together as files in one submission. "
            "<strong>Live, conference, or AAC route:</strong> submit the written brief/rubric by annotation, upload, or exact labeled text; the teacher records student, career, date, route, seconds, technology used, oral/AAC complete, and written record complete on the class checkoff. Text alone is not oral evidence. Earlier work stays in place and is not re-uploaded. This private formative activity is 0 points, omitted from the final grade, and unpublished for teacher transfer.</p>"
        )
        assignments[5] = await upsert_formative_assignment(
            client,
            existing_assignments[5],
            TITLES[5],
            final_description,
            files["ORAL"]["id"],
            routes,
        )
        urls = {day: f"/courses/{COURSE_ID}/assignments/{assignment['id']}" for day, assignment in assignments.items()}
        urls["quiz"] = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"

        students = student_content(files, visuals, urls)
        teachers = teacher_content(files)
        labels = {
            1: "Audience and Sales Pitch Plan",
            2: "Deliver, Test, and Revise",
            3: "BrainBoost Decision and Career Outline",
            4: "Interview Appearance and Rehearsal",
            5: "Career Oral Evidence Brief",
        }
        interactions = {
            1: ("Assignment", assignments[1]["id"], TITLES[1]),
            2: ("Assignment", assignments[2]["id"], TITLES[2]),
            3: ("Assignment", assignments[3]["id"], TITLES[3]),
            4: ("Assignment", assignments[4]["id"], DAY4_ASSIGNMENT_TITLE),
            5: ("Assignment", assignments[5]["id"], TITLES[5]),
        }
        order, pages = [], {}
        for day in range(1, 6):
            header_title = f"Day {day} · {labels[day]}"
            await prior.upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header_title, header_title))
            student_title = f"STUDENT: 6SW Wk4 Day {day} - {labels[day]}"
            student_page = await common.upsert_page(
                client,
                student_title,
                common.render("6sw-wk4-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, **CONTRACTS[day], **students[day]}),
            )
            teacher_title = f"TEACHER: 6SW Wk4 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(
                client,
                teacher_title,
                common.render("6sw-wk4-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **CONTRACTS[day], **teachers[day]}),
            )
            await prior.upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await prior.upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            kind, key, title = interactions[day]
            await prior.upsert_item(client, module["id"], kind, key, title)
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title), (kind, key, title)]
            pages[day] = {"teacher": teacher_page, "student": student_page}

        def matches_item(entry, kind, key):
            return entry.get("type") == kind and (
                (kind == "SubHeader" and entry.get("title") == key)
                or (kind == "Page" and entry.get("page_url") == key)
                or (kind in ("Assignment", "Quiz") and entry.get("content_id") == key)
            )

        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        keep_ids = set()
        for kind, key, _title in order:
            match = next((entry for entry in items if entry["id"] not in keep_ids and matches_item(entry, kind, key)), None)
            if not match:
                raise RuntimeError(f"Missing expected Sales module item: {kind} {key}")
            keep_ids.add(match["id"])
        for entry in items:
            if entry["id"] not in keep_ids:
                await common.api(client, "DELETE", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{entry['id']}")
        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(entry for entry in items if matches_item(entry, kind, key))
            await common.api(
                client,
                "PUT",
                f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}",
                data={"module_item[position]": position, "module_item[title]": title, "module_item[published]": "false"},
            )
        final = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        ordered = sorted(final, key=lambda entry: entry.get("position", 0))
        if len(ordered) != 20:
            raise RuntimeError(f"Expected 20 Sales module items; found {len(ordered)}")
        for position, ((kind, key, title), entry) in enumerate(zip(order, ordered), 1):
            if entry.get("position") != position or entry.get("title") != title or entry.get("published") is not False or not matches_item(entry, kind, key):
                raise RuntimeError(f"Sales module order mismatch at position {position}")

        support_folder, _support_count = await lock_folder_files(client, support_folder, [path.name for path in support_paths.values()])
        visual_folder, _visual_count = await lock_folder_files(client, visual_folder, [path.name for path in visual_paths.values()])
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
        aliases = [entry for entry in modules if entry.get("name") in {MODULE_NAME, *MODULE_ALIASES}]
        if module.get("published") is not False or len(aliases) != 1 or aliases[0].get("id") != module.get("id"):
            raise RuntimeError("Sales module must remain unpublished")
        for day, assignment in assignments.items():
            title = DAY4_ASSIGNMENT_TITLE if day == 4 else TITLES[day]
            assignments[day] = await assert_annotation_assignment(client, title, assignment, files[ANNOTATION_DAYS[day]]["id"], routes)
        quiz = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
        if quiz.get("published") is not False or quiz.get("quiz_type") != "practice_quiz" or int(quiz.get("allowed_attempts") or 0) != -1:
            raise RuntimeError("Sales practice Quiz final state mismatch")
        final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
        expected_question_names = [name for name, *_rest in QUESTIONS]
        if [question.get("question_name") for question in final_questions] != expected_question_names:
            raise RuntimeError("Sales practice Quiz final question order mismatch")
        for day, pair in pages.items():
            for kind, page in pair.items():
                fresh = await common.api(client, "GET", f"/courses/{COURSE_ID}/pages/{page['url']}")
                if fresh.get("published") is not False:
                    raise RuntimeError(f"Published 6SW Wk4 page remains: {fresh.get('title')}")
                pages[day][kind] = fresh
        print(
            json.dumps(
                {
                    "module": {"id": module["id"], "published": module["published"]},
                    "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
                    "visual_folder": {"id": visual_folder["id"], "locked": visual_folder["locked"]},
                    "files": {key: record["id"] for key, record in files.items()},
                    "visuals": {key: record["id"] for key, record in visuals.items()},
                    "quiz": {"id": quiz["id"], "published": quiz.get("published")},
                    "assignments": {
                        str(day): {
                            "id": assignment["id"],
                            "published": assignment.get("published"),
                            "points": assignment.get("points_possible"),
                            "grading_type": assignment.get("grading_type"),
                            "omit_from_final_grade": assignment.get("omit_from_final_grade"),
                        }
                        for day, assignment in assignments.items()
                    },
                    "pages": {
                        str(day): {kind: {"url": page["url"], "published": page["published"]} for kind, page in pair.items()}
                        for day, pair in pages.items()
                    },
                    "items": [{"position": entry["position"], "type": entry["type"], "title": entry["title"]} for entry in ordered],
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
