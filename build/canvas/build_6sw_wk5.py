"""Build the unpublished 6SW Week 5 job-readiness module."""

import asyncio
import json
import sys
from urllib.parse import urlencode

import httpx

import build_5sw_wk1 as prior
from configure_assessment_map import SUBMISSION_LINK_MARKER


common = prior.common
COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
MODULE_NAME = "6SW Wk5: Job Search, Applications, and Interviews"
TITLES = {
    1: "PRACTICE: Job Search and Posting Evidence",
    2: "PRACTICE: Tailored Cover Letter",
    3: "PRACTICE: Application and References",
    4: "PRACTICE: Interview Readiness Planner",
    5: "MAJOR 1: Job Skills, Application, and Mock Interview Portfolio",
}
QUIZ_TITLE = "PRACTICE QUIZ: Interview Readiness Check"
TEMPLATES = ROOT / "build/canvas/templates"
WORKSHEET_NAMES = {
    "SEARCH": "6sw-wk5-job-search-and-posting-evidence.pdf",
    "COVER": "6sw-wk5-cover-letter-simulation.pdf",
    "APP": "6sw-wk5-application-and-references.pdf",
    "READY": "6sw-wk5-interview-readiness.pdf",
    "MOCK": "6sw-wk5-mock-interview-and-thank-you.pdf",
    "RUBRIC": "6sw-wk5-job-skills-rubric.pdf",
}
ANNOTATION_DAYS = {1: "SEARCH", 2: "COVER", 3: "APP", 4: "READY", 5: "MOCK"}
RUBRIC_MARKER = 'data-cce-rubric-note="cce-advisory-rubric-v1"'


def preflight():
    required = [
        TEMPLATES / "6sw-wk5-student.html",
        TEMPLATES / "6sw-wk5-teacher.html",
        *(ROOT / "docs/resources/worksheets" / name for name in WORKSHEET_NAMES.values()),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"6SW Wk5 preflight missing required files: {missing}")


async def canvas_preflight(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    module_matches = [entry for entry in modules if entry.get("name") == MODULE_NAME]
    if len(module_matches) > 1:
        raise RuntimeError(f"Duplicate 6SW Wk5 modules: {[entry['id'] for entry in module_matches]}")

    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    major_groups = [entry for entry in groups if entry.get("name") == "Major Assessments (60%)"]
    if len(major_groups) != 1:
        raise RuntimeError(f"Expected exactly one Major Assessments (60%) group; found {len(major_groups)}")
    major_group = major_groups[0]

    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    assignment_matches = {}
    for day, title in TITLES.items():
        matches = [entry for entry in assignments if entry.get("name") == title]
        if day == 5 and len(matches) != 1:
            raise RuntimeError(f"Expected exactly one mapped Major named {title!r}; found {len(matches)}")
        if day != 5 and len(matches) > 1:
            raise RuntimeError(f"Duplicate practice assignments named {title!r}: {[entry['id'] for entry in matches]}")
        found = matches[0] if matches else None
        if found and day != 5 and (
            found.get("published") is not False
            or float(found.get("points_possible") or 0) != 0
            or found.get("grading_type") != "percent"
            or found.get("omit_from_final_grade") is not True
        ):
            raise RuntimeError(f"Refusing to modify malformed practice assignment {title!r}")
        assignment_matches[day] = found

    major = assignment_matches[5]
    if (
        major.get("published") is not False
        or float(major.get("points_possible") or 0) != 100
        or major.get("grading_type") != "points"
        or major.get("omit_from_final_grade") is not False
        or major.get("assignment_group_id") != major_group.get("id")
        or RUBRIC_MARKER not in (major.get("description") or "")
    ):
        raise RuntimeError("Refusing to modify malformed mapped Job Skills Major")

    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    quiz_matches = [entry for entry in quizzes if entry.get("title") == QUIZ_TITLE]
    if len(quiz_matches) > 1:
        raise RuntimeError(f"Duplicate quizzes named {QUIZ_TITLE!r}: {[entry['id'] for entry in quiz_matches]}")
    if quiz_matches and (
        quiz_matches[0].get("published") is not False
        or quiz_matches[0].get("quiz_type") != "practice_quiz"
        or int(quiz_matches[0].get("allowed_attempts") or 0) != -1
    ):
        raise RuntimeError(f"Refusing to modify malformed practice Quiz {QUIZ_TITLE!r}")
    return assignment_matches, major_group, quiz_matches[0] if quiz_matches else None

CONTRACTS = {
    1: {
        "TOPIC": "Job Search",
        "OBJECTIVE": "Students will identify and apply the steps of an effective job search by sequencing a safe search cycle, screening a fictional posting, and selecting an authorized next action.",
        "TEKS": "d(6)(A)",
        "DOL": "Two-page job-search and posting-screen decision record.",
        "I_CAN": "sequence a safe job-search cycle, screen a fictional posting, and choose an authorized next action.",
        "SHOW": "Complete the two-page job-search and posting-screen decision record.",
    },
    2: {
        "TOPIC": "Business Correspondence",
        "OBJECTIVE": "Students will write appropriate business correspondence by tailoring a fictional cover letter to a posting, using supplied evidence, and making one visible revision.",
        "TEKS": "d(7)(B)",
        "DOL": "Three-page fictional cover-letter plan, draft, evidence audit, and final revision.",
        "I_CAN": "tailor a fictional cover letter to a posting, use supplied evidence, and make one visible revision.",
        "SHOW": "Complete the three-page cover-letter plan, draft, evidence audit, and final revision.",
    },
    3: {
        "TOPIC": "Applications and References",
        "OBJECTIVE": "Students will complete a sample job application and explain protocol for selecting and using references by using supplied fictional information and asking permission before sharing.",
        "TEKS": "d(7)(C), d(7)(D)",
        "DOL": "Four-page fictional application, reference-role plan, unsent permission request, and privacy audit.",
        "I_CAN": "complete a fictional application and explain how to select references and ask permission before sharing their information.",
        "SHOW": "Complete the four-page fictional application, reference-role plan, unsent permission request, and privacy audit.",
    },
    4: {
        "TOPIC": "Interview Preparation",
        "OBJECTIVE": "Students will describe context-appropriate appearance for an interview and prepare truthful, relevant responses and interviewer questions for a mock interview.",
        "TEKS": "d(6)(B)",
        "DOL": "Three-page interview-readiness planner plus five-question retryable practice Quiz.",
        "I_CAN": "describe context-appropriate interview preparation and prepare truthful responses and job-related interviewer questions.",
        "SHOW": "Complete the three-page interview-readiness planner and review all five practice Quiz explanations.",
    },
    5: {
        "TOPIC": "Mock Interview",
        "OBJECTIVE": "Students will describe context-appropriate interview preparation, participate in a mock interview as interviewee and interviewer, revise from feedback, and write appropriate thank-you correspondence.",
        "TEKS": "d(6)(B), d(6)(C), d(7)(B)",
        "DOL": "Assessable interviewee and interviewer oral/AAC evidence documented by private media or the teacher checkoff, plus the four-page record and six-criterion Major 1 evidence profile.",
        "I_CAN": "prepare for an interview, participate as interviewee and interviewer, revise from feedback, and write a brief fictional thank-you note.",
        "SHOW": "Complete oral/AAC interview evidence through the assigned recording or teacher-checkoff route, then submit the four-page Day 5 record and six-criterion self-score; earlier evidence stays where it is.",
    },
}


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    matches = [module for module in modules if module.get("name") == MODULE_NAME]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one {MODULE_NAME!r} module; found {len(matches)}")
    data = {"module[name]": MODULE_NAME, "module[published]": "false"}
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
    actual_names = {record.get("filename") for record in final}
    if any(record.get("locked") is not True for record in final) or not set(expected_names).issubset(actual_names):
        raise RuntimeError(f"Unlocked or missing files remain in folder {folder['id']}")
    return current, final


async def assert_annotation_assignment(
    client,
    title,
    assignment,
    source_id,
    routes,
    *,
    points,
    grading_type,
    omit,
    group_id=None,
    require_marker=False,
):
    fresh = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignment['id']}")
    source = await common.api(client, "GET", f"/files/{source_id}")
    clone_id = int(fresh.get("annotatable_attachment_id") or 0)
    clone = await common.api(client, "GET", f"/files/{clone_id}") if clone_id else {}
    if clone and clone.get("locked") is not True:
        clone = await common.api(client, "PUT", f"/files/{clone_id}", data={"locked": "true"})
    failed = (
        fresh.get("published") is not False
        or float(fresh.get("points_possible") or 0) != float(points)
        or fresh.get("grading_type") != grading_type
        or fresh.get("omit_from_final_grade") is not omit
        or set(fresh.get("submission_types") or []) != set(routes)
        or not clone_id
        or source.get("locked") is not True
        or clone.get("locked") is not True
        or clone.get("filename") != source.get("filename")
        or int(clone.get("size") or -1) != int(source.get("size") or -2)
        or (group_id is not None and fresh.get("assignment_group_id") != group_id)
        or (require_marker and RUBRIC_MARKER not in (fresh.get("description") or ""))
    )
    if failed:
        raise RuntimeError(f"Assignment invariant failed for {title!r}")
    return fresh


async def upsert_practice_assignment(client, found, title, description, attachment_id, routes):
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
    return await assert_annotation_assignment(
        client,
        title,
        assignment,
        attachment_id,
        routes,
        points=0,
        grading_type="percent",
        omit=True,
    )


async def require_major_assignment(client, found, group, description, attachment_id):
    scoring_note = (
        '<div data-cce-rubric-note="cce-advisory-rubric-v1" style="border-left:4px solid #5d3f6a;padding:10px 14px;margin:16px 0">'
        '<p><strong>How this is scored:</strong> Use the student-visible six-criterion profile. Add the ratings out of 24, use the published conversion table, and enter that percentage as the score out of 100.</p>'
        '<p>Days 1-3 and the CCE Evidence Log remain where they are. Recorded route uploads the written Day 5 record/self-score and private audio/video together. Live, conference, or AAC route submits the written record while the teacher completes the Day 5 Interview Evidence Checkoff. Text or media alone is incomplete.</p></div>'
    )
    routes = ["student_annotation", "online_upload", "online_text_entry"]
    assignment = await common.api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{found['id']}",
        data={
            "assignment[name]": TITLES[5],
            "assignment[description]": description + scoring_note,
            "assignment[published]": "false",
            "assignment[points_possible]": "100",
            "assignment[grading_type]": "points",
            "assignment[omit_from_final_grade]": "false",
            "assignment[assignment_group_id]": str(group["id"]),
            "assignment[submission_types][]": routes,
            "assignment[annotatable_attachment_id]": str(attachment_id),
        },
    )
    return await assert_annotation_assignment(
        client,
        TITLES[5],
        assignment,
        attachment_id,
        routes,
        points=100,
        grading_type="points",
        omit=False,
        group_id=group["id"],
        require_marker=True,
    )


QUESTIONS = [
    ("Q1 - screening", "What happens before an applicant shares private information?", "Screen the posting, source, employer, directions, and data request.", ["Send an ID photo first.", "Use any link in a message.", "Contact every employer listed."], "Correct. Screening comes before disclosure or contact.", "A posting does not automatically make a request safe."),
    ("Q2 - application", "What should a student enter when a field does not apply in this simulation?", "N/A when directions allow it; never invent information.", ["A made-up credential", "A family member's information", "A random number"], "Correct. Complete, truthful, and consistent beats invented detail.", "Never fabricate a field to make an application look full."),
    ("Q3 - references", "What must happen before sharing a reference's contact information?", "Ask the person for permission and explain the role.", ["Assume a teacher agrees.", "List a family member without asking.", "Post the person's details publicly."], "Correct. Permission comes first.", "Reference information belongs to another person and must not be shared without permission."),
    ("Q4 - appearance", "Which interview-appearance rule is strongest?", "Prepare for the workplace, task, safety requirements, format, and accommodations.", ["Every interview requires a suit.", "Expensive clothing earns points.", "Eye contact is required for every person."], "Correct. Context, safety, and access come before fashion rules.", "Appearance guidance is not universal, costly, body-based, or disability-based."),
    ("Q5 - privacy", "Which classroom action is allowed?", "Draft a fictional thank-you note and do not send it.", ["Submit a real Social Security number.", "Contact the fictional employer.", "Publish a classmate's reference details."], "Correct. The simulation stays fictional and private.", "No real application, message, contact, or personal-data disclosure is required."),
]


async def upsert_quiz(client):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    matches = [quiz for quiz in quizzes if quiz.get("title") == QUIZ_TITLE]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one {QUIZ_TITLE!r} Quiz; found {len(matches)}")
    data = {
        "quiz[title]": QUIZ_TITLE,
        "quiz[description]": "<p>Ungraded, unlimited-retry practice on screening, applications, references, interview context, and privacy. Review every feedback explanation.</p>",
        "quiz[quiz_type]": "practice_quiz",
        "quiz[published]": "false",
        "quiz[allowed_attempts]": "-1",
        "quiz[show_correct_answers]": "true",
        "quiz[shuffle_answers]": "false",
    }
    quiz = await common.api(client, "PUT" if matches else "POST", f"/courses/{COURSE_ID}/quizzes/{matches[0]['id']}" if matches else f"/courses/{COURSE_ID}/quizzes", data=data)
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
        payload = {"question": {"question_name": name, "question_text": prompt, "question_type": "multiple_choice_question", "position": position, "points_possible": 1, "correct_comments": yes, "incorrect_comments": no, "answers": [{"answer_text": correct, "answer_weight": 100}] + [{"answer_text": answer, "answer_weight": 0} for answer in wrong]}}
        path = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{old['id']}" if old else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        await common.api(client, "PUT" if old else "POST", path, json=payload)
    expected = [name for name, *_rest in QUESTIONS]
    final = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    by_name = {question.get("question_name"): question for question in final}
    if set(by_name) != set(expected) or len(final) != len(expected):
        raise RuntimeError("Interview practice Quiz question set mismatch")
    fields = []
    for name in expected:
        fields.extend([("order[][id]", str(by_name[name]["id"])), ("order[][type]", "question")])
    await common.api(client, "POST", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/reorder", content=urlencode(fields), headers={"Content-Type": "application/x-www-form-urlencoded"})
    final = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    if [question.get("question_name") for question in final] != expected:
        raise RuntimeError("Interview practice Quiz order mismatch")
    return await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


def student_content(files, assignment_urls, quiz_url):
    link, step = common.file_link, common.step
    submit = (
        f'<section data-cce-marker="{SUBMISSION_LINK_MARKER}" style="border:2px solid #5d3f6a;border-radius:12px;padding:18px 20px;margin:24px 0;background:#faf7fb">'
        '<h3 style="margin:0 0 8px;color:#5d3f6a">Submit Major 1 evidence</h3>'
        '<p style="margin:0 0 14px"><strong>Two parts are required.</strong> Recorded route: upload the completed four-page record/self-score and private audio/video together as files in one submission. Live, conference, or AAC route: submit the written record by annotation, upload, or exact labeled text; the teacher completes the Day 5 Interview Evidence Checkoff. Text or media alone is incomplete. Days 1-3 and the CCE Evidence Log stay where they are.</p>'
        f'<p style="margin:0"><a href="{assignment_urls[5]}" style="display:inline-block;background:#5d3f6a;color:#fff;padding:11px 18px;border-radius:6px;text-decoration:none;font-weight:700" data-api-endpoint="/api/v1{assignment_urls[5]}" data-api-returntype="Assignment">Open {TITLES[5]}</a></p></section>'
    )
    return {
        1: {"TITLE": "Job Search and Posting Screen", "PURPOSE": "Use a safe search cycle to screen a fictional posting before any contact or personal-data step.", "TODAY": "<ul><li>put seven job-search actions in order;</li><li>mark duties, skills, and one boundary;</li><li>match truthful evidence and keep a gap visible;</li><li>choose a verified next action.</li></ul>", "READY": f'<p>Open {link(files["SEARCH"]["id"], "the two-page record")} and <a href="{assignment_urls[1]}">the private Canvas annotation or submission route</a>. The posting is fictional, not a vacancy.</p>', "SUPPORT": '<p><strong>Word bank:</strong> posting/oferta de empleo · screen/revisar · verify/verificar · evidence/evidencia · authorized/autorizado.</p><p><strong>Use this frame in Step 4:</strong> I would verify <strong>[detail]</strong> through <strong>[official or known route]</strong> before <strong>[action]</strong>.</p>', "STEPS": step(1, "Order the cycle", "<p>Number target, prepare, search, screen, track, tailor/apply, and follow up. Screening comes before personal data or contact.</p>") + step(2, "Read the fixed posting", "<p>Underline two duties, box two desired skills, and star one boundary.</p>") + step(3, "Match without inventing", "<p>Use two supplied Jordan actions. Keep one gap visible; a gap is not permission to invent a credential or result.</p>") + step(4, "Verify and decide", "<p>Record two independent checks and choose continue through a verified route, pause and verify, or stop and report.</p>"), "SUBMISSION": "", "EXIT": "<p>Name the search step students may skip and the consequence.</p>", "DONE": "<ul><li>seven actions ordered;</li><li>posting marked;</li><li>two matches and one honest gap;</li><li>two verification checks;</li><li>safe decision and exit.</li></ul>", "FALLBACK": "<p>The fixed case is the complete route. Type, annotate, dictate, use enlarged print, or use paper. No live job board, H&amp;L, FYF Rung 5, employer contact, account, or personal data is required.</p>"},
        2: {"TITLE": "Tailored Cover Letter", "PURPOSE": "Write a concise fictional cover letter that connects posting needs to truthful evidence and sounds like a person.", "TODAY": "<ul><li>match two needs to two supplied actions;</li><li>plan and draft three short paragraphs;</li><li>audit every claim;</li><li>make one revision visible.</li></ul>", "READY": f'<p>Open {link(files["COVER"]["id"], "the three-page cover-letter lab")} and <a href="{assignment_urls[2]}">the private Canvas route</a>. The letter is not sent.</p>', "SUPPORT": '<p><strong>Word bank:</strong> requirement/requisito · evidence/evidencia · tailor/adaptar · qualification/cualificación · revision/revisión.</p><p><strong>Use this frame in the evidence paragraph:</strong> Your posting asks for <strong>[need]</strong>. Jordan demonstrated <strong>[skill]</strong> when <strong>[action and result]</strong>.</p>', "STEPS": step(1, "Match the evidence", "<p>Connect accurate data entry to checking 120 entries. Connect communication or organization to revising labels, greeting families, or asking clarifying questions.</p>") + step(2, "Plan three paragraph jobs", "<p>Opening: role and interest. Evidence: two truthful links. Closing: thanks and an authorized next step.</p>") + step(3, "Draft in plain language", "<p>Use supplied evidence only. Do not invent work history, credentials, employer facts, or results.</p>") + step(4, "Audit and revise", "<p>Remove generic praise and unsupported claims. Preserve one before/after change and explain why it is more accurate, specific, relevant, or clear.</p>"), "SUBMISSION": "", "EXIT": "<p>Explain why the visible revision improved the letter.</p>", "DONE": "<ul><li>two evidence links and one honest gap;</li><li>three-paragraph plan and draft;</li><li>accuracy and privacy audit;</li><li>final fictional letter;</li><li>visible revision.</li></ul>", "FALLBACK": "<p>Typing, annotation, dictation, enlarged print, and paper are equal routes. Score evidence and meaning, not inflated enthusiasm or perfect English mechanics. Nothing is sent.</p>"},
        3: {"TITLE": "Sample Application and References", "PURPOSE": "Complete one consistent fictional application and ask permission before sharing any reference information.", "TODAY": "<ul><li>use supplied facts or N/A;</li><li>keep the application consistent with the letter;</li><li>choose reference roles with firsthand evidence;</li><li>draft—but do not send—a permission request.</li></ul>", "READY": f'<p>Open {link(files["APP"]["id"], "the four-page fictional application and reference record")} and <a href="{assignment_urls[3]}">the private Canvas route</a>. Use Jordan Rivera from start to finish.</p>', "SUPPORT": '<p><strong>Word bank:</strong> applicable/aplicable · N/A/no aplica · consistent/coherente · reference/referencia · permission/permiso.</p><p><strong>Use this frame in Step 3:</strong> I chose the <strong>[role]</strong> because that person observed Jordan <strong>[action]</strong>.</p>', "STEPS": step(1, "Read before entering", "<p>Use a supplied fact when available, N/A only when allowed, and never provide private or invented information.</p>") + step(2, "Complete in chunks", "<p>Target and education; experience and skills; fictional availability. Pause after each chunk for a consistency check.</p>") + step(3, "Choose reference roles", "<p>Select people who observed relevant work. Do not enter real names or contact information.</p>") + step(4, "Ask first and audit", "<p>Draft an unsent permission request, then check every field for accuracy, consistency, and privacy.</p>"), "SUBMISSION": "", "EXIT": "<p>Explain how permission protects the applicant, reference, and employer.</p>", "DONE": "<ul><li>applicable fields complete or N/A;</li><li>evidence consistent with the letter;</li><li>reference roles tied to firsthand evidence;</li><li>unsent permission request;</li><li>privacy audit.</li></ul>", "FALLBACK": "<p>Type, annotate, dictate, use enlarged print, or use paper. Never enter a real name, contact route, availability, ID, signature, health, family, or immigration detail.</p>"},
        4: {"TITLE": "Interview Preparation", "PURPOSE": "Prepare for the interview context, build truthful evidence notes, and rehearse the interviewer role without memorizing a script.", "TODAY": "<ul><li>compare office, task-demonstration, and virtual contexts;</li><li>select one true example from the CCE Evidence Log or use Jordan;</li><li>prepare three truthful response notes and an interviewer follow-up;</li><li>rehearse an accessible professional opening and close;</li><li>review five Quiz explanations.</li></ul>", "READY": f'<p>Open {link(files["READY"]["id"], "the three-page planner")}, <a href="{assignment_urls[4]}">the private planner route</a>, and <a href="{quiz_url}">{QUIZ_TITLE}</a>. If available, open your <strong>CCE Six-Weeks Evidence Log</strong>; it is a source, not another submission. Your route is assigned before Day 5; private details are not written on the packet.</p>', "SUPPORT": '<p><strong>Word bank:</strong> context/contexto · task/tarea · accommodation/adaptación · evidence/evidencia · follow-up/seguimiento.</p><p><strong>Evidence frame:</strong> In <strong>[situation or task]</strong>, I <strong>[action]</strong>. The result or reflection was <strong>[result, learning, or next step]</strong>.</p><p><strong>Accessible opening:</strong> Hello. I’m Jordan. I’m here to discuss the office assistant role. Thank you for meeting with me. <strong>Close:</strong> Thank you for your time. What is the next step in your process?</p>', "STEPS": step(1, "Prepare for the context", "<p>Workplace, task, safety, format, technology, and accommodation come before fashion rules. Record two preparations and one item to verify for each context.</p>") + step(2, "Build evidence, not a script", "<p>Select one CCE Evidence Log entry or use the Jordan fallback. Mark the Situation or Task, Action, and Result or Reflection. School, project, activity, service, and responsibility examples count; paid work is not required.</p>") + step(3, "Prepare both roles", "<p>Build three short evidence notes. Rehearse the opening and close through speech, AAC, text-to-speech, an interpreter, or private conference. Then write one relevant follow-up, one neutral evidence note, and one question about the job or training. Do not ask protected or unrelated personal questions.</p>") + step(4, "Complete the practice Quiz", "<p>Review every explanation. Record the assigned route and one final preparation action; tell the teacher privately if you need a different route.</p>"), "SUBMISSION": "", "EXIT": "<p>Record the assigned Day 5 route and one final preparation action.</p>", "DONE": "<ul><li>three context decisions;</li><li>one Evidence Log or Jordan example expanded into response notes;</li><li>three response plans and growth action;</li><li>accessible opening and close ready in the assigned communication route;</li><li>interviewer follow-up and neutral note;</li><li>route confirmed and five Quiz explanations reviewed.</li></ul>", "FALLBACK": "<p>Short notes, dictation, annotation, enlarged print, paper, speech, AAC, text-to-speech, an interpreter, and private conference are supported. If the Evidence Log is unavailable, use the complete Jordan bank; do not reconstruct or resubmit old work. No public performance, handshake, eye contact, camera, or one body or speech style is required. Xello Job Interviews is supplemental only.</p>"},
        5: {"TITLE": "Mock Interview and Follow-Up", "PURPOSE": "Produce interviewee and interviewer evidence, apply feedback, and write a brief fictional follow-up without duplicating earlier submissions.", "TODAY": "<ul><li>use one prepared Evidence Log or Jordan example;</li><li>complete interviewee and interviewer roles with an accessible opening and close;</li><li>record specific feedback and apply one change;</li><li>submit both the written Day 5 record and oral/AAC evidence through the assigned route.</li></ul>", "READY": f'<p>Open {link(files["MOCK"]["id"], "the four-page Day 5 record")}, {link(files["RUBRIC"]["id"], "the two-page evidence profile")}, and your Day 4 notes. Your <strong>CCE Six-Weeks Evidence Log</strong> may stay open as a source; it is not uploaded. Confirm whether your oral/AAC evidence is recorded or documented on the teacher checkoff. Days 1-3 stay in their original locations.</p>', "SUPPORT": '<p><strong>Word bank:</strong> interviewee/entrevistado · interviewer/entrevistador · follow-up/seguimiento · revision/revisión · thank-you/agradecimiento.</p><p><strong>Opening:</strong> Hello. I’m Jordan. I’m here to discuss the office assistant role. Thank you for meeting with me. <strong>Close:</strong> Thank you for your time. What is the next step in your process?</p><p><strong>Revision frame:</strong> I changed <strong>[specific response move]</strong> after <strong>[feedback]</strong>. The change helped because <strong>[effect]</strong>.</p>', "STEPS": step(1, "Ready check", "<p>Open the posting, one prepared Evidence Log or Jordan example, three answer notes, assigned route, feedback method, and teacher checkoff or recording plan.</p>") + step(2, "Round 1: produce both roles", "<p>Begin with the accessible opening and end with the close through speech, AAC, text-to-speech, an interpreter, or private conference. In a pair, each person completes one interviewee turn and one interviewer turn. Conference, small-group, recording, and AAC routes use the same evidence jobs.</p>") + step(3, "Feedback, revision, and Round 2", "<p>Record one specific strength and one exact change. Apply the change in a second response or role exchange.</p>") + step(4, "Write, self-score, and submit", "<p>Write a brief fictional thank-you note; do not send it. Self-score all six criteria and revise the weakest evidence. <strong>Recorded route:</strong> upload the written record and private audio/video together as files. <strong>Live, conference, or AAC route:</strong> submit the written record by annotation, upload, or exact labeled text while the teacher completes the Day 5 Interview Evidence Checkoff. Text or media alone is incomplete. Do not upload the Evidence Log or earlier artifacts.</p>"), "SUBMISSION": submit, "EXIT": "<p>Name the strongest evidence and the next revision.</p>", "DONE": "<ul><li>accessible opening and close through the assigned communication route;</li><li>assessable interviewee and interviewer evidence;</li><li>specific feedback and applied revision;</li><li>fictional thank-you note;</li><li>six-criterion self-score;</li><li>written record plus recorded media or teacher checkoff complete.</li></ul>", "FALLBACK": "<p>Partner absence or a missing Evidence Log does not block completion. Use Jordan plus speech, AAC, text-to-speech, an interpreter, teacher conference, small group, private recording, or scheduled make-up. No handshake, eye contact, camera, or one body or speech style is required. Written interviewer notes may show the interviewer role; interviewee evidence remains spoken or accommodation-aligned communicated evidence and is recorded by media or the teacher checkoff.</p>"},
    }


def teacher_content(files, quiz_url):
    link, flow = common.file_link, common.flow
    color = "#5d3f6a"
    source_block = {
        1: '<p><a href="https://www.careeronestop.org/JobSearch/job-search.aspx">CareerOneStop Job Search</a> (accessed August 2026).</p>',
        2: '<p><a href="https://www.careeronestop.org/JobSearch/Resumes/cover-letters.aspx">CareerOneStop Cover Letters</a> (accessed August 2026).</p>',
        3: '<p><a href="https://www.careeronestop.org/JobSearch/Resumes/job-applications.aspx">CareerOneStop Job Applications</a> · <a href="https://www.careeronestop.org/JobSearch/Resumes/references.aspx">CareerOneStop References</a> (accessed August 2026).</p>',
        4: '<p><a href="https://www.careeronestop.org/JobSearch/Interview/interview-and-negotiate.aspx">CareerOneStop Interview Guidance</a> · <a href="https://www.eeoc.gov/pre-employment-inquiries-and-disability">EEOC Pre-Employment Disability Inquiry Boundary</a> (accessed August 2026).</p>',
        5: '<p><a href="https://www.careeronestop.org/JobSearch/Interview/interview-and-negotiate.aspx">CareerOneStop Interview and Follow-Up Guidance</a> · <a href="https://www.eeoc.gov/prohibited-employment-policiespractices">EEOC Prohibited Employment Practices</a> (accessed August 2026).</p>',
    }
    common_support = "<p>Word banks and complete frames appear beside the evidence job. Accept typing, annotation, dictation, enlarged print, paper, teacher conference, and authorized AAC. Score evidence and meaning, not accent, eye contact, handshake, camera use, clothing cost/style, disability, paid work history, public confidence, or English mechanics unless meaning is unclear.</p>"
    common_fallback = "<p>The Jordan/Pecan Creek case is the complete route. No live job board, employer contact, account, personal data, family participation, public Discussion, H&amp;L, Xello, eDynamic, or camera is required. Absent students use the same fixed case and private route; schedule interview evidence rather than assigning a public performance.</p>"
    return {
        1: {"TITLE": "Job Search and Posting Screen", "SUBTITLE": "50 minutes · Two-page record", "ALERT": "<strong>Fictional posting:</strong> a posting is a lead, not proof. Students do not register, apply, contact an employer, or share personal data.", "PREP": f'<ul><li>Post {link(files["SEARCH"]["id"], "the two-page record")} and private annotation route; default printing is zero.</li><li>Display the seven mixed actions and the fictional Pecan Creek posting.</li><li>Open the coordinated Student Guide.</li></ul>', "EVIDENCE": "<p>Collect the ordered cycle, marked posting, two truthful matches, one honest gap, two independent verification checks, authorized next action, and exit response.</p>", "FLOW": flow(color, "Bellringer · 5", "First-draft order; mark one uncertain step.") + flow("#4c8b38", "Model the cycle · 8", "Target, prepare, search, screen, track, tailor/apply, follow up.") + flow("#155d7a", "Notice and label · 10", "Duties, desired skills, evidence limits, and facts requiring verification.") + flow("#d39b22", "Posting screen · 17", "Two matches, one gap, two checks, and authorized action.") + flow(color, "Turn and talk · 5", "Compare one match and one risk; revise individually.") + flow("#4c8b38", "Exit · 5", "Skipped step and consequence."), "MONITOR": "<p><strong>Sequence key by printed row:</strong> 6, 1, 7, 4, 2, 5, 3. Full evidence distinguishes the posting from independent employer verification. A safe conclusion can be continue through a verified route, pause and verify, or stop and report when supported. Trim partner sharing first.</p>", "RESOURCES": source_block[1], "SUPPORT": common_support, "FALLBACK": common_fallback},
        2: {"TITLE": "Tailored Cover Letter", "SUBTITLE": "50 minutes · Three-page lab", "ALERT": "<strong>Not sent:</strong> students use the fictional posting and Jordan evidence only. Requirements vary; a real applicant follows the posting about whether a cover letter is required.", "PREP": f'<ul><li>Post {link(files["COVER"]["id"], "the three-page cover-letter lab")}, {link(files["RUBRIC"]["id"], "the two-page Major profile")}, and private annotation route.</li><li>Keep the posting and Jordan evidence visible.</li><li>Prepare the model evidence links below.</li></ul>', "EVIDENCE": "<p>Collect two accurate evidence links, one honest gap, a three-paragraph plan/draft, claim audit, final fictional letter, and visible revision.</p>", "FLOW": flow(color, "Bellringer · 5", "Sort three statements into résumé, cover letter, or neither.") + flow("#4c8b38", "Model · 8", "Name the position, connect evidence, explain fit without invention, close courteously.") + flow("#155d7a", "Plan · 9", "Two posting needs, two Jordan actions, and one honest gap.") + flow("#d39b22", "Draft · 13", "Three short paragraphs in plain language.") + flow(color, "Audit and final · 10", "Check every claim and preserve one before/after revision.") + flow("#4c8b38", "Exit · 5", "Why the revision improved the letter."), "MONITOR": "<p><strong>Model links:</strong> accurate data entry → checked 120 entries; organization/communication → revised labels after confusion, greeted families under supervision, or asked clarifying questions. Full evidence names the role, uses two supplied links, invents no credential/work history/result, and closes courteously. Trim peer exchange first.</p>", "RESOURCES": source_block[2], "SUPPORT": common_support, "FALLBACK": common_fallback},
        3: {"TITLE": "Sample Application and References", "SUBTITLE": "50 minutes · Four-page simulation", "ALERT": "<strong>Privacy boundary:</strong> use supplied facts or N/A only. Never collect or display real identity, availability, signature, health, family, immigration, or reference data, and never ask students to provide it.", "PREP": f'<ul><li>Post {link(files["APP"]["id"], "the four-page packet")} and private annotation route.</li><li>Keep Jordan Rivera and Pecan Creek visible from start to finish.</li><li>Prepare three field-sort examples: supplied fact, N/A, and excluded/private.</li></ul>', "EVIDENCE": "<p>Collect complete/N/A fields, consistent experience and skills, reference roles tied to firsthand evidence, an unsent permission request, and privacy audit.</p>", "FLOW": flow(color, "Bellringer · 5", "Sort fields into supplied fact, N/A, or excluded.") + flow("#4c8b38", "Application model · 7", "Read directions, use a specific target, complete applicable fields, keep evidence consistent.") + flow("#155d7a", "Chunked application · 18", "Target/education, then experience/skills/fictional availability; monitor between chunks.") + flow("#d39b22", "Reference protocol · 8", "Choose roles that observed relevant work.") + flow(color, "Permission draft and audit · 7", "Draft, do not send; ask before sharing any contact route.") + flow("#4c8b38", "Exit · 5", "How permission protects all three parties."), "MONITOR": "<p><strong>Key:</strong> use Jordan's supplied facts; use N/A only when allowed; never fill a blank by inventing. Strong reference choices can speak from firsthand observation. Permission precedes sharing, even when the person is a teacher. Trim optional comparison first.</p>", "RESOURCES": source_block[3], "SUPPORT": common_support, "FALLBACK": common_fallback},
        4: {"TITLE": "Interview Preparation", "SUBTITLE": "50 minutes · Planner plus retryable Quiz", "ALERT": "<strong>Context first:</strong> workplace, task, safety, format, technology, and accommodation determine preparation. Do not teach one expensive, gendered, body-based, cultural, eye-contact, handshake, or camera rule.", "PREP": f'<ul><li>Post {link(files["READY"]["id"], "the three-page planner")}, the private planner route, and <a href="{quiz_url}">{QUIZ_TITLE}</a>.</li><li>Ask students to open one <strong>CCE Six-Weeks Evidence Log</strong> entry as a source. Do not collect the log or old artifacts again; use the complete Jordan bank when the log is missing or not appropriate.</li><li>Project this complete response model: <em>Situation/task: our design team had two versions of the event flyer. Action: I compared the audience and deadline, asked which information had to be noticed first, and revised the larger heading. Result/reflection: the viewer found the date faster; next time I would run the test before choosing colors.</em> Nonexample: <em>I am creative and helped my group.</em></li><li>Project the accessible opening and close: <em>Hello. I’m Jordan. I’m here to discuss the office assistant role. Thank you for meeting with me.</em> / <em>Thank you for your time. What is the next step in your process?</em> Model the same words through speech, AAC, text-to-speech, an interpreter, or private conference.</li><li>Preassign paired, small-group, teacher-conference, private-recording, and AAC routes. No student writes private accommodation details or performs publicly.</li></ul>', "EVIDENCE": "<p>Collect three context decisions, three truthful response plans, one growth action, an accessible opening and close, interviewer follow-up and neutral note, route confirmation, and review of all five Quiz explanations. The Evidence Log stays with the student.</p>", "FLOW": flow(color, "Bellringer · 5", "What changes across office, task-demonstration, and virtual interviews?") + flow("#4c8b38", "Context model · 8", "Workplace, task, safety, format, technology, and access.") + flow("#155d7a", "Evidence model · 8", "Expand one Evidence Log or Jordan example; model the accessible opening and close.") + flow("#d39b22", "Prepare three answers · 14", "Evidence notes, not memorized scripts.") + flow(color, "Interviewer role · 7", "Relevant follow-up, neutral note, and job/training question.") + flow("#4c8b38", "Practice Quiz · 5", "Review every explanation.") + flow("#155d7a", "Exit · 3", "Assigned route and one final action."), "MONITOR": "<p><strong>Minute 13:</strong> context choices match the actual workplace, task, safety, format, technology, or access need. <strong>Minute 25:</strong> each student has one complete evidence arc with a specific action; if one-third use only traits, label the model's Situation/Task, Action, and Result/Reflection. <strong>Minute 39:</strong> three response notes are truthful and brief enough to speak rather than read, and the opening/close works through the assigned communication route. <strong>Minute 47:</strong> route, technology/communication check, and interviewer follow-up are ready. Trim optional partner rehearsal first; protect the evidence arc, accessible opening/close, assigned route, and private support check.</p>", "RESOURCES": source_block[4], "SUPPORT": common_support, "FALLBACK": common_fallback},
        5: {"TITLE": "Mock Interview and Follow-Up", "SUBTITLE": "50 minutes · Major 1", "ALERT": "<strong>One new submission:</strong> Days 1-3 and the CCE Evidence Log stay in their original locations. Day 5 requires the written record plus recorded media or a named teacher oral/AAC checkoff.", "PREP": f'<ul><li>Post {link(files["MOCK"]["id"], "the four-page Day 5 record")}, {link(files["RUBRIC"]["id"], "the two-page evidence profile")}, the private mapped Major Assignment, and a roster titled <strong>Day 5 Interview Evidence Checkoff</strong>.</li><li>Checkoff fields: <strong>student, date, route, accessible opening/close complete, interviewee evidence complete, interviewer follow-up/neutral notes complete, feedback applied in Round 2, oral/AAC complete, written record complete, and follow-up date when needed</strong>.</li><li>Students may keep one Evidence Log entry open as a prompt; it is not collected or uploaded. Jordan is the complete fallback.</li><li>Confirm every route and feedback method before class. For pairs: A interviews B for 3 minutes, switch for 3 minutes, and use 4 minutes for neutral notes. Repeat one improved response each in Round 2. Speech, AAC, text-to-speech, an interpreter, and private conference are equal opening/close routes.</li></ul>', "EVIDENCE": "<p>Collect the written Day 5 record and either private recorded media or the named teacher checkoff for an accessible opening/close, interviewee/interviewer evidence, specific feedback, applied revision, context preparation, fictional thank-you note, and six-criterion self-score. Score Days 1-3 from their original locations; do not collect the Evidence Log.</p>", "FLOW": flow(color, "Ready check · 5", "Posting, one Evidence Log or Jordan example, three answer notes, opening/close, route, feedback method, and checkoff/recording plan.") + flow("#4c8b38", "Round 1 · 10", "Each student opens, produces interviewee/interviewer evidence, and closes through the assigned route.") + flow("#155d7a", "Feedback and revision · 6", "One specific strength and one exact change.") + flow("#d39b22", "Round 2 · 10", "Apply the change in a second response or role exchange.") + flow(color, "Thank-you note · 9", "Brief, specific, fictional, accurate, courteous, and unsent.") + flow("#4c8b38", "Self-score and revision · 7", "Score six criteria and revise the weakest available evidence.") + flow("#155d7a", "Private submit · 3", "Written record plus media/checkoff completion."), "MONITOR": "<p><strong>Minute 5:</strong> every student has a prepared example, accessible opening/close, assigned route, feedback method, and checkoff or recording plan; use Jordan immediately when a log or partner is unavailable. <strong>Minute 15:</strong> the opening/close and both pair roles or the equivalent conference/recording/AAC jobs are documented. <strong>Minute 31:</strong> one specific feedback move is visible in Round 2. <strong>Minute 43:</strong> the fictional thank-you note is accurate, specific, and unsent. <strong>Minute 48:</strong> all six criteria are self-scored and both parts are routed: recorded students upload written record + media together; live/conference/AAC students submit writing while the teacher completes the named checkoff. Text or media alone is incomplete. Trim an extra exchange, not the accessible opening/close, revision, thank-you, self-score, or two-part collection.</p>", "RESOURCES": source_block[5], "SUPPORT": common_support, "FALLBACK": common_fallback},
    }


async def main():
    preflight()
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")

    support_paths = {key: ROOT / "docs/resources/worksheets" / name for key, name in WORKSHEET_NAMES.items()}

    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        existing_assignments, major_group, _existing_quiz = await canvas_preflight(client)
        module = await ensure_module(client)
        folder_path = "course files/CCR Materials/6SW/Wk5"
        folder = await common.ensure_folder(client, folder_path)
        files = {key: await upload_locked(client, path, folder_path) for key, path in support_paths.items()}
        folder, _folder_files = await lock_folder_files(client, folder, [path.name for path in support_paths.values()])
        quiz = await upsert_quiz(client)
        routes = ["student_annotation", "online_upload", "online_text_entry"]
        assignments = {}
        for day, key in {1: "SEARCH", 2: "COVER", 3: "APP", 4: "READY"}.items():
            assignments[day] = await upsert_practice_assignment(
                client,
                existing_assignments[day],
                TITLES[day],
                "<p>Complete privately by Canvas annotation, one upload, exact labeled text, dictation within the text route, or labeled paper. This practice is 0 points, omitted from the final grade, and unpublished for teacher transfer.</p>",
                files[key]["id"],
                routes,
            )
        major_description = (
            f'<p><strong>Two parts are required.</strong> Use {common.file_link(files["MOCK"]["id"], "the four-page mock-interview and thank-you record")} and '
            f'{common.file_link(files["RUBRIC"]["id"], "the six-criterion evidence profile")} to self-score. '
            "<strong>Recorded route:</strong> upload the completed written record/self-score and private audio/video together as files in one submission. "
            "<strong>Live, conference, or AAC route:</strong> submit the written record by annotation, upload, or exact labeled text; the teacher records student, date, route, accessible opening/close, interviewee evidence, interviewer follow-up/neutral notes, feedback applied in Round 2, oral/AAC completion, written-record completion, and any follow-up date on the Day 5 Interview Evidence Checkoff. Text or media alone is incomplete. Days 1-3 and the CCE Evidence Log stay where they are.</p>"
        )
        assignments[5] = await require_major_assignment(
            client,
            existing_assignments[5],
            major_group,
            major_description,
            files["MOCK"]["id"],
        )
        assignment_urls = {day: f"/courses/{COURSE_ID}/assignments/{assignment['id']}" for day, assignment in assignments.items()}
        quiz_url = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        students = student_content(files, assignment_urls, quiz_url)
        teachers = teacher_content(files, quiz_url)
        labels = {1: "Job Search and Posting Screen", 2: "Tailored Cover Letter", 3: "Sample Application and References", 4: "Interview Preparation", 5: "Mock Interview and Follow-Up"}
        order, pages = [], {}
        for day in range(1, 6):
            header_title = f"Day {day} · {labels[day]}"
            await prior.upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header_title, header_title))
            student_title = f"STUDENT: 6SW Wk5 Day {day} - {labels[day]}"
            student_page = await common.upsert_page(client, student_title, common.render("6sw-wk5-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, **CONTRACTS[day], **students[day]}))
            teacher_title = f"TEACHER: 6SW Wk5 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(client, teacher_title, common.render("6sw-wk5-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **CONTRACTS[day], **teachers[day]}))
            await prior.upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await prior.upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            await prior.upsert_item(client, module["id"], "Assignment", assignments[day]["id"], TITLES[day])
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title), ("Assignment", assignments[day]["id"], TITLES[day])]
            pages[day] = {"teacher": teacher_page, "student": student_page}

        def matches_item(entry, kind, key):
            return entry.get("type") == kind and ((kind == "SubHeader" and entry.get("title") == key) or (kind == "Page" and entry.get("page_url") == key) or (kind == "Assignment" and entry.get("content_id") == key))

        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        keep_ids = set()
        for kind, key, _title in order:
            match = next((entry for entry in items if entry["id"] not in keep_ids and matches_item(entry, kind, key)), None)
            if not match:
                raise RuntimeError(f"Missing expected Job Skills module item: {kind} {key}")
            keep_ids.add(match["id"])
        for entry in items:
            if entry["id"] not in keep_ids:
                await common.api(client, "DELETE", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{entry['id']}")
        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(entry for entry in items if matches_item(entry, kind, key))
            await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}", data={"module_item[position]": position, "module_item[title]": title, "module_item[published]": "false"})
        final = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        ordered = sorted(final, key=lambda entry: entry.get("position", 0))
        if len(ordered) != 20:
            raise RuntimeError(f"Expected 20 Job Skills module items; found {len(ordered)}")
        for position, ((kind, key, title), entry) in enumerate(zip(order, ordered), 1):
            if entry.get("position") != position or entry.get("title") != title or entry.get("published") is not False or not matches_item(entry, kind, key):
                raise RuntimeError(f"Job Skills module order mismatch at position {position}")

        folder, folder_files = await lock_folder_files(client, folder, [path.name for path in support_paths.values()])
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
        module_matches = [entry for entry in modules if entry.get("name") == MODULE_NAME]
        quiz = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
        if module.get("published") is not False or len(module_matches) != 1 or module_matches[0].get("id") != module.get("id") or folder.get("locked") is not True or any(record.get("locked") is not True for record in folder_files):
            raise RuntimeError("Job Skills module must stay unpublished and every support file/folder locked")
        if quiz.get("published") is not False or quiz.get("quiz_type") != "practice_quiz" or int(quiz.get("allowed_attempts") or 0) != -1 or quiz.get("show_correct_answers") is not True:
            raise RuntimeError("Interview practice Quiz settings mismatch")
        final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
        if [question.get("question_name") for question in final_questions] != [name for name, *_rest in QUESTIONS]:
            raise RuntimeError("Interview practice Quiz final question order mismatch")
        for day in range(1, 5):
            assignments[day] = await assert_annotation_assignment(client, TITLES[day], assignments[day], files[ANNOTATION_DAYS[day]]["id"], routes, points=0, grading_type="percent", omit=True)
        assignments[5] = await assert_annotation_assignment(client, TITLES[5], assignments[5], files["MOCK"]["id"], routes, points=100, grading_type="points", omit=False, group_id=major_group["id"], require_marker=True)
        for day, pair in pages.items():
            for kind, page in pair.items():
                fresh = await common.api(client, "GET", f"/courses/{COURSE_ID}/pages/{page['url']}")
                if fresh.get("published") is not False:
                    raise RuntimeError(f"Published 6SW Wk5 page remains: {fresh.get('title')}")
                pages[day][kind] = fresh
        print(json.dumps({"module": {"id": module["id"], "published": module["published"]}, "folder": {"id": folder["id"], "locked": folder["locked"], "files_locked": len(folder_files)}, "files": {key: record["id"] for key, record in files.items()}, "quiz": {"id": quiz["id"], "published": quiz.get("published"), "type": quiz.get("quiz_type"), "attempts": quiz.get("allowed_attempts")}, "assignments": {str(day): {"id": assignment["id"], "published": assignment.get("published"), "points": assignment.get("points_possible"), "grading_type": assignment.get("grading_type"), "omit": assignment.get("omit_from_final_grade")} for day, assignment in assignments.items()}, "pages": {str(day): {kind: {"url": page["url"], "published": page["published"]} for kind, page in pair.items()} for day, pair in pages.items()}, "items": [{"position": entry["position"], "type": entry["type"], "title": entry["title"]} for entry in ordered]}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
