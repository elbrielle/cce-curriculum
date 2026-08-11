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
        "DOL": "Four-page mock-interview and thank-you record plus the six-criterion Major 1 evidence profile.",
        "I_CAN": "prepare for an interview, participate as interviewee and interviewer, revise from feedback, and write a brief fictional thank-you note.",
        "SHOW": "Submit the four-page Day 5 record and six-criterion self-score; earlier Days 1-3 evidence stays where it was first submitted or turned in.",
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


async def mapped_major_assignment(client):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == TITLES[5]]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one existing mapped Major named {TITLES[5]!r}; found {len(matches)}")
    found = matches[0]
    if float(found.get("points_possible") or 0) != 100:
        raise RuntimeError(f"Refusing to modify Job Skills Major: expected 100 points, found {found.get('points_possible')}")
    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group = next((entry for entry in groups if entry.get("id") == found.get("assignment_group_id")), None)
    if not group or group.get("name") != "Major Assessments (60%)":
        raise RuntimeError("Refusing to modify Job Skills Major outside Major Assessments (60%)")
    return found


async def require_major_assignment(client, found, description, attachment_id):
    scoring_note = (
        '<div data-cce-rubric-note="cce-advisory-rubric-v1" style="border-left:4px solid #5d3f6a;padding:10px 14px;margin:16px 0">'
        '<p><strong>How this is scored:</strong> Use the student-visible six-criterion profile. Add the ratings out of 24, use the published conversion table, and enter that percentage as the score out of 100.</p>'
        '<p>Days 1-3 remain where first submitted or turned in. Students submit only the Day 5 record and self-score here; the teacher scores earlier evidence from its original location.</p></div>'
    )
    return await common.api(
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
            "assignment[submission_types][]": ["student_annotation", "online_upload", "online_text_entry", "media_recording"],
            "assignment[annotatable_attachment_id]": str(attachment_id),
        },
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
        '<p style="margin:0 0 14px">Submit only the four-page Day 5 record and self-score here. Days 1-3 stay where you first submitted or turned them in.</p>'
        f'<p style="margin:0"><a href="{assignment_urls[5]}" style="display:inline-block;background:#5d3f6a;color:#fff;padding:11px 18px;border-radius:6px;text-decoration:none;font-weight:700" data-api-endpoint="/api/v1{assignment_urls[5]}" data-api-returntype="Assignment">Open {TITLES[5]}</a></p></section>'
    )
    return {
        1: {"TITLE": "Job Search and Posting Screen", "PURPOSE": "Use a safe search cycle to screen a fictional posting before any contact or personal-data step.", "TODAY": "<ul><li>put seven job-search actions in order;</li><li>mark duties, skills, and one boundary;</li><li>match truthful evidence and keep a gap visible;</li><li>choose a verified next action.</li></ul>", "READY": f'<p>Open {link(files["SEARCH"]["id"], "the two-page record")} and <a href="{assignment_urls[1]}">the private Canvas annotation or submission route</a>. The posting is fictional, not a vacancy.</p>', "SUPPORT": '<p><strong>Word bank:</strong> posting/oferta de empleo · screen/revisar · verify/verificar · evidence/evidencia · authorized/autorizado.</p><p><strong>Use this frame in Step 4:</strong> I would verify <strong>[detail]</strong> through <strong>[official or known route]</strong> before <strong>[action]</strong>.</p>', "STEPS": step(1, "Order the cycle", "<p>Number target, prepare, search, screen, track, tailor/apply, and follow up. Screening comes before personal data or contact.</p>") + step(2, "Read the fixed posting", "<p>Underline two duties, box two desired skills, and star one boundary.</p>") + step(3, "Match without inventing", "<p>Use two supplied Jordan actions. Keep one gap visible; a gap is not permission to invent a credential or result.</p>") + step(4, "Verify and decide", "<p>Record two independent checks and choose continue through a verified route, pause and verify, or stop and report.</p>"), "SUBMISSION": "", "EXIT": "<p>Name the search step students may skip and the consequence.</p>", "DONE": "<ul><li>seven actions ordered;</li><li>posting marked;</li><li>two matches and one honest gap;</li><li>two verification checks;</li><li>safe decision and exit.</li></ul>", "FALLBACK": "<p>The fixed case is the complete route. Type, annotate, dictate, use enlarged print, or use paper. No live job board, H&amp;L, FYF Rung 5, employer contact, account, or personal data is required.</p>"},
        2: {"TITLE": "Tailored Cover Letter", "PURPOSE": "Write a concise fictional cover letter that connects posting needs to truthful evidence and sounds like a person.", "TODAY": "<ul><li>match two needs to two supplied actions;</li><li>plan and draft three short paragraphs;</li><li>audit every claim;</li><li>make one revision visible.</li></ul>", "READY": f'<p>Open {link(files["COVER"]["id"], "the three-page cover-letter lab")} and <a href="{assignment_urls[2]}">the private Canvas route</a>. The letter is not sent.</p>', "SUPPORT": '<p><strong>Word bank:</strong> requirement/requisito · evidence/evidencia · tailor/adaptar · qualification/cualificación · revision/revisión.</p><p><strong>Use this frame in the evidence paragraph:</strong> Your posting asks for <strong>[need]</strong>. Jordan demonstrated <strong>[skill]</strong> when <strong>[action and result]</strong>.</p>', "STEPS": step(1, "Match the evidence", "<p>Connect accurate data entry to checking 120 entries. Connect communication or organization to revising labels, greeting families, or asking clarifying questions.</p>") + step(2, "Plan three paragraph jobs", "<p>Opening: role and interest. Evidence: two truthful links. Closing: thanks and an authorized next step.</p>") + step(3, "Draft in plain language", "<p>Use supplied evidence only. Do not invent work history, credentials, employer facts, or results.</p>") + step(4, "Audit and revise", "<p>Remove generic praise and unsupported claims. Preserve one before/after change and explain why it is more accurate, specific, relevant, or clear.</p>"), "SUBMISSION": "", "EXIT": "<p>Explain why the visible revision improved the letter.</p>", "DONE": "<ul><li>two evidence links and one honest gap;</li><li>three-paragraph plan and draft;</li><li>accuracy and privacy audit;</li><li>final fictional letter;</li><li>visible revision.</li></ul>", "FALLBACK": "<p>Typing, annotation, dictation, enlarged print, and paper are equal routes. Score evidence and meaning, not inflated enthusiasm or perfect English mechanics. Nothing is sent.</p>"},
        3: {"TITLE": "Sample Application and References", "PURPOSE": "Complete one consistent fictional application and ask permission before sharing any reference information.", "TODAY": "<ul><li>use supplied facts or N/A;</li><li>keep the application consistent with the letter;</li><li>choose reference roles with firsthand evidence;</li><li>draft—but do not send—a permission request.</li></ul>", "READY": f'<p>Open {link(files["APP"]["id"], "the four-page fictional application and reference record")} and <a href="{assignment_urls[3]}">the private Canvas route</a>. Use Jordan Rivera from start to finish.</p>', "SUPPORT": '<p><strong>Word bank:</strong> applicable/aplicable · N/A/no aplica · consistent/coherente · reference/referencia · permission/permiso.</p><p><strong>Use this frame in Step 3:</strong> I chose the <strong>[role]</strong> because that person observed Jordan <strong>[action]</strong>.</p>', "STEPS": step(1, "Read before entering", "<p>Use a supplied fact when available, N/A only when allowed, and never provide private or invented information.</p>") + step(2, "Complete in chunks", "<p>Target and education; experience and skills; fictional availability. Pause after each chunk for a consistency check.</p>") + step(3, "Choose reference roles", "<p>Select people who observed relevant work. Do not enter real names or contact information.</p>") + step(4, "Ask first and audit", "<p>Draft an unsent permission request, then check every field for accuracy, consistency, and privacy.</p>"), "SUBMISSION": "", "EXIT": "<p>Explain how permission protects the applicant, reference, and employer.</p>", "DONE": "<ul><li>applicable fields complete or N/A;</li><li>evidence consistent with the letter;</li><li>reference roles tied to firsthand evidence;</li><li>unsent permission request;</li><li>privacy audit.</li></ul>", "FALLBACK": "<p>Type, annotate, dictate, use enlarged print, or use paper. Never enter a real name, contact route, availability, ID, signature, health, family, or immigration detail.</p>"},
        4: {"TITLE": "Interview Preparation", "PURPOSE": "Prepare for the interview context, build truthful evidence notes, and rehearse the interviewer role without memorizing a script.", "TODAY": "<ul><li>compare office, task-demonstration, and virtual contexts;</li><li>prepare three truthful responses;</li><li>prepare a job-related follow-up and neutral note;</li><li>review five Quiz explanations.</li></ul>", "READY": f'<p>Open {link(files["READY"]["id"], "the three-page planner")}, <a href="{assignment_urls[4]}">the private planner route</a>, and <a href="{quiz_url}">{QUIZ_TITLE}</a>. Your route is assigned before Day 5; private details are not written on the packet.</p>', "SUPPORT": '<p><strong>Word bank:</strong> context/contexto · task/tarea · accommodation/adaptación · evidence/evidencia · follow-up/seguimiento.</p><p><strong>Use this frame in Step 1:</strong> For a <strong>[format/task]</strong> interview, Jordan should prepare <strong>[action]</strong> because <strong>[job, safety, technology, or access reason]</strong>.</p>', "STEPS": step(1, "Prepare for the context", "<p>Workplace, task, safety, format, technology, and accommodation come before fashion rules. Record two preparations and one item to verify for each context.</p>") + step(2, "Build evidence, not a script", "<p>Use Situation or Task - Action - Result or Reflection. School, project, activity, service, and responsibility examples count; paid work is not required.</p>") + step(3, "Prepare the interviewer role", "<p>Write one relevant follow-up, one neutral evidence note, and one question about the job or training. Do not ask protected or unrelated personal questions.</p>") + step(4, "Complete the practice Quiz", "<p>Review every explanation. Record the assigned route and one final preparation action; tell the teacher privately if you need a different route.</p>"), "SUBMISSION": "", "EXIT": "<p>Record the assigned Day 5 route and one final preparation action.</p>", "DONE": "<ul><li>three context decisions;</li><li>three response plans and growth action;</li><li>interviewer follow-up and neutral note;</li><li>route confirmed without private disclosure;</li><li>five Quiz explanations reviewed.</li></ul>", "FALLBACK": "<p>Short notes, dictation, annotation, enlarged print, paper, AAC, and private conference are supported. No public performance or camera is required. Xello Job Interviews is supplemental only.</p>"},
        5: {"TITLE": "Mock Interview and Follow-Up", "PURPOSE": "Produce interviewee and interviewer evidence, apply feedback, and write a brief fictional follow-up without duplicating earlier submissions.", "TODAY": "<ul><li>complete interviewee and interviewer roles;</li><li>record specific feedback and apply one change;</li><li>write and audit a fictional thank-you note;</li><li>self-score the six criteria and submit the Day 5 record.</li></ul>", "READY": f'<p>Open {link(files["MOCK"]["id"], "the four-page Day 5 record")}, {link(files["RUBRIC"]["id"], "the two-page evidence profile")}, and your Day 4 notes. Days 1-3 stay in their original locations.</p>', "SUPPORT": '<p><strong>Word bank:</strong> interviewee/entrevistado · interviewer/entrevistador · follow-up/seguimiento · revision/revisión · thank-you/agradecimiento.</p><p><strong>Use this frame after feedback:</strong> I changed <strong>[specific response move]</strong> after <strong>[feedback]</strong>. The change helped because <strong>[effect]</strong>.</p>', "STEPS": step(1, "Ready check", "<p>Open the posting, Jordan evidence, three answer notes, assigned route, and feedback method.</p>") + step(2, "Round 1: produce both roles", "<p>In a pair, each person completes one interviewee turn and one interviewer turn. Conference, small-group, recording, and AAC routes use the same evidence jobs.</p>") + step(3, "Feedback, revision, and Round 2", "<p>Record one specific strength and one exact change. Apply the change in a second response or role exchange.</p>") + step(4, "Write, self-score, and submit", "<p>Write a brief fictional thank-you note; do not send it. Self-score all six criteria, revise the weakest available evidence, and submit only the Day 5 record.</p>"), "SUBMISSION": submit, "EXIT": "<p>Name the strongest evidence and the next revision.</p>", "DONE": "<ul><li>assessable interviewee and interviewer evidence;</li><li>specific feedback and applied revision;</li><li>fictional thank-you note;</li><li>six-criterion self-score;</li><li>Day 5 record submitted once.</li></ul>", "FALLBACK": "<p>Partner absence does not block completion. Use a teacher conference, small group, private recording, AAC, or scheduled make-up. Written interviewer notes may show the interviewer role; interviewee evidence remains spoken or accommodation-aligned communicated evidence.</p>"},
    }


def teacher_content(files, quiz_url):
    link, flow = common.file_link, common.flow
    color = "#5d3f6a"
    source_block = {
        1: '<p><a href="https://www.careeronestop.org/JobSearch/job-search.aspx">CareerOneStop Job Search</a> (accessed August 2026).</p>',
        2: '<p><a href="https://www.careeronestop.org/JobSearch/Resumes/cover-letters.aspx">CareerOneStop Cover Letters</a> (accessed August 2026).</p>',
        3: '<p><a href="https://www.careeronestop.org/JobSearch/Find-Jobs/job-applications.aspx">CareerOneStop Job Applications</a> · <a href="https://www.careeronestop.org/JobSearch/Resumes/references.aspx">CareerOneStop References</a> (accessed August 2026).</p>',
        4: '<p><a href="https://www.careeronestop.org/JobSearch/Interview/interview-and-negotiate.aspx">CareerOneStop Interview Guidance</a> · <a href="https://www.eeoc.gov/pre-employment-inquiries-and-disability">EEOC Pre-Employment Disability Inquiry Boundary</a> (accessed August 2026).</p>',
        5: '<p><a href="https://www.careeronestop.org/JobSearch/Interview/interview-and-negotiate.aspx">CareerOneStop Interview and Follow-Up Guidance</a> · <a href="https://www.eeoc.gov/prohibited-employment-policiespractices">EEOC Prohibited Employment Practices</a> (accessed August 2026).</p>',
    }
    common_support = "<p>Word banks and complete frames appear beside the evidence job. Accept typing, annotation, dictation, enlarged print, paper, teacher conference, and authorized AAC. Score evidence and meaning, not accent, eye contact, handshake, camera use, clothing cost/style, disability, paid work history, public confidence, or English mechanics unless meaning is unclear.</p>"
    common_fallback = "<p>The Jordan/Pecan Creek case is the complete route. No live job board, employer contact, account, personal data, family participation, public Discussion, H&amp;L, Xello, eDynamic, or camera is required. Absent students use the same fixed case and private route; schedule interview evidence rather than assigning a public performance.</p>"
    return {
        1: {"TITLE": "Job Search and Posting Screen", "SUBTITLE": "50 minutes · Two-page record", "ALERT": "<strong>Fictional posting:</strong> a posting is a lead, not proof. Students do not register, apply, contact an employer, or share personal data.", "PREP": f'<ul><li>Post {link(files["SEARCH"]["id"], "the two-page record")} and private annotation route; default printing is zero.</li><li>Display the seven mixed actions and the fictional Pecan Creek posting.</li><li>Open the coordinated Student Guide.</li></ul>', "EVIDENCE": "<p>Collect the ordered cycle, marked posting, two truthful matches, one honest gap, two independent verification checks, authorized next action, and exit response.</p>", "FLOW": flow(color, "Bellringer · 5", "First-draft order; mark one uncertain step.") + flow("#4c8b38", "Model the cycle · 8", "Target, prepare, search, screen, track, tailor/apply, follow up.") + flow("#155d7a", "Notice and label · 10", "Duties, desired skills, evidence limits, and facts requiring verification.") + flow("#d39b22", "Posting screen · 17", "Two matches, one gap, two checks, and authorized action.") + flow(color, "Turn and talk · 5", "Compare one match and one risk; revise individually.") + flow("#4c8b38", "Exit · 5", "Skipped step and consequence."), "MONITOR": "<p><strong>Sequence key by printed row:</strong> 6, 1, 7, 4, 2, 5, 3. Full evidence distinguishes the posting from independent employer verification. A safe conclusion can be continue through a verified route, pause and verify, or stop and report when supported. Trim partner sharing first.</p>", "RESOURCES": source_block[1], "SUPPORT": common_support, "FALLBACK": common_fallback},
        2: {"TITLE": "Tailored Cover Letter", "SUBTITLE": "50 minutes · Three-page lab", "ALERT": "<strong>Not sent:</strong> students use the fictional posting and Jordan evidence only. Requirements vary; a real applicant follows the posting about whether a cover letter is required.", "PREP": f'<ul><li>Post {link(files["COVER"]["id"], "the three-page cover-letter lab")}, {link(files["RUBRIC"]["id"], "the two-page Major profile")}, and private annotation route.</li><li>Keep the posting and Jordan evidence visible.</li><li>Prepare the model evidence links below.</li></ul>', "EVIDENCE": "<p>Collect two accurate evidence links, one honest gap, a three-paragraph plan/draft, claim audit, final fictional letter, and visible revision.</p>", "FLOW": flow(color, "Bellringer · 5", "Sort three statements into résumé, cover letter, or neither.") + flow("#4c8b38", "Model · 8", "Name the position, connect evidence, explain fit without invention, close courteously.") + flow("#155d7a", "Plan · 9", "Two posting needs, two Jordan actions, and one honest gap.") + flow("#d39b22", "Draft · 13", "Three short paragraphs in plain language.") + flow(color, "Audit and final · 10", "Check every claim and preserve one before/after revision.") + flow("#4c8b38", "Exit · 5", "Why the revision improved the letter."), "MONITOR": "<p><strong>Model links:</strong> accurate data entry → checked 120 entries; organization/communication → revised labels after confusion, greeted families under supervision, or asked clarifying questions. Full evidence names the role, uses two supplied links, invents no credential/work history/result, and closes courteously. Trim peer exchange first.</p>", "RESOURCES": source_block[2], "SUPPORT": common_support, "FALLBACK": common_fallback},
        3: {"TITLE": "Sample Application and References", "SUBTITLE": "50 minutes · Four-page simulation", "ALERT": "<strong>Privacy boundary:</strong> use supplied facts or N/A only. Never collect, display, or ask students to destroy real identity, availability, signature, health, family, immigration, or reference data.", "PREP": f'<ul><li>Post {link(files["APP"]["id"], "the four-page packet")} and private annotation route.</li><li>Keep Jordan Rivera and Pecan Creek visible from start to finish.</li><li>Prepare three field-sort examples: supplied fact, N/A, and excluded/private.</li></ul>', "EVIDENCE": "<p>Collect complete/N/A fields, consistent experience and skills, reference roles tied to firsthand evidence, an unsent permission request, and privacy audit.</p>", "FLOW": flow(color, "Bellringer · 5", "Sort fields into supplied fact, N/A, or excluded.") + flow("#4c8b38", "Application model · 7", "Read directions, use a specific target, complete applicable fields, keep evidence consistent.") + flow("#155d7a", "Chunked application · 18", "Target/education, then experience/skills/fictional availability; monitor between chunks.") + flow("#d39b22", "Reference protocol · 8", "Choose roles that observed relevant work.") + flow(color, "Permission draft and audit · 7", "Draft, do not send; ask before sharing any contact route.") + flow("#4c8b38", "Exit · 5", "How permission protects all three parties."), "MONITOR": "<p><strong>Key:</strong> use Jordan's supplied facts; use N/A only when allowed; never fill a blank by inventing. Strong reference choices can speak from firsthand observation. Permission precedes sharing, even when the person is a teacher. Trim optional comparison first.</p>", "RESOURCES": source_block[3], "SUPPORT": common_support, "FALLBACK": common_fallback},
        4: {"TITLE": "Interview Preparation", "SUBTITLE": "50 minutes · Planner plus retryable Quiz", "ALERT": "<strong>Context first:</strong> workplace, task, safety, format, technology, and accommodation determine preparation. Do not teach one expensive, gendered, body-based, cultural, eye-contact, handshake, or camera rule.", "PREP": f'<ul><li>Post {link(files["READY"]["id"], "the three-page planner")}, the private planner route, and <a href="{quiz_url}">{QUIZ_TITLE}</a>.</li><li>Preassign paired, small-group, teacher-conference, private-recording, and AAC routes.</li><li>No student writes private accommodation details or performs publicly.</li></ul>', "EVIDENCE": "<p>Collect three context decisions, three truthful response plans, one growth action, interviewer follow-up and neutral note, route confirmation, and review of all five Quiz explanations.</p>", "FLOW": flow(color, "Bellringer · 5", "What changes across office, task-demonstration, and virtual interviews?") + flow("#4c8b38", "Context model · 8", "Workplace, task, safety, format, technology, and access.") + flow("#155d7a", "Answer model · 8", "Situation or Task - Action - Result or Reflection.") + flow("#d39b22", "Prepare three answers · 14", "Evidence notes, not memorized scripts.") + flow(color, "Interviewer role · 7", "Relevant follow-up, neutral note, and job/training question.") + flow("#4c8b38", "Practice Quiz · 5", "Review every explanation.") + flow("#155d7a", "Exit · 3", "Assigned route and one final action."), "MONITOR": "<p><strong>Context models:</strong> office/customer-facing—clean, functional, role-aware; task demonstration—confirm PPE/tools/site instructions; virtual/phone—test audio, privacy, notifications, and backup route. A school/project/activity/service example is valid. Exclude protected or unrelated personal questions. Trim optional partner rehearsal first.</p>", "RESOURCES": source_block[4], "SUPPORT": common_support, "FALLBACK": common_fallback},
        5: {"TITLE": "Mock Interview and Follow-Up", "SUBTITLE": "50 minutes · Major 1", "ALERT": "<strong>One new submission:</strong> Days 1-3 stay in their original Canvas or labeled-paper locations. Students submit only the Day 5 record and self-score here.", "PREP": f'<ul><li>Post {link(files["MOCK"]["id"], "the four-page Day 5 record")}, {link(files["RUBRIC"]["id"], "the two-page evidence profile")}, and private mapped Major Assignment.</li><li>Confirm every route and feedback method before class.</li><li>For pairs: A interviews B for 3 minutes, switch for 3 minutes, and use 4 minutes for neutral notes. Repeat one improved response each in Round 2.</li></ul>', "EVIDENCE": "<p>Collect interviewee and interviewer evidence, specific feedback, applied revision, context preparation, fictional thank-you note, six-criterion self-score, and Day 5 private submission. Score Days 1-3 from their original locations.</p>", "FLOW": flow(color, "Ready check · 5", "Posting, evidence bank, three answer notes, route, and feedback method.") + flow("#4c8b38", "Round 1 · 10", "Each student produces interviewee and interviewer evidence.") + flow("#155d7a", "Feedback and revision · 6", "One specific strength and one exact change.") + flow("#d39b22", "Round 2 · 10", "Apply the change in a second response or role exchange.") + flow(color, "Thank-you note · 9", "Brief, specific, fictional, accurate, courteous, and unsent.") + flow("#4c8b38", "Self-score and revision · 7", "Score six criteria and revise the weakest available evidence.") + flow("#155d7a", "Private submit · 3", "Day 5 record only."), "MONITOR": "<p><strong>Pair protocol:</strong> both students interview and answer. <strong>Solo/conference/recording/AAC protocol:</strong> a teacher or supplied prompt serves as counterpart; the student produces the interviewee response, one job-related follow-up, neutral interviewer notes, feedback, and revised response. Interviewee evidence is relevant, truthful, organized, responsive, and visibly revised. Trim an extra exchange, not revision or thank-you time.</p>", "RESOURCES": source_block[5], "SUPPORT": common_support, "FALLBACK": common_fallback},
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

    names = {"SEARCH": "6sw-wk5-job-search-and-posting-evidence.pdf", "COVER": "6sw-wk5-cover-letter-simulation.pdf", "APP": "6sw-wk5-application-and-references.pdf", "READY": "6sw-wk5-interview-readiness.pdf", "MOCK": "6sw-wk5-mock-interview-and-thank-you.pdf", "RUBRIC": "6sw-wk5-job-skills-rubric.pdf"}
    support_paths = {key: ROOT / "docs/resources/worksheets" / name for key, name in names.items()}
    missing = [str(path) for path in support_paths.values() if not path.is_file()]
    if missing:
        raise RuntimeError(f"Refusing partial Canvas write; missing upload dependencies: {missing}")

    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        mapped_major = await mapped_major_assignment(client)  # fail before any write
        module = await ensure_module(client)
        folder_path = "course files/CCR Materials/6SW/Wk5"
        folder = await common.ensure_folder(client, folder_path)
        files = {key: await common.upload(client, path, folder_path) for key, path in support_paths.items()}
        quiz = await upsert_quiz(client)
        assignments = {}
        for day, key in {1: "SEARCH", 2: "COVER", 3: "APP", 4: "READY"}.items():
            assignments[day] = await common.upsert_assignment(client, TITLES[day], "<p>Complete privately by Canvas annotation, upload, typed labeled responses, dictation, or paper. This practice is 0 points, omitted from the final grade, and unpublished for teacher transfer.</p>", ["student_annotation", "online_upload", "online_text_entry"], files[key]["id"])
        major_description = f'<p>Submit {common.file_link(files["MOCK"]["id"], "the four-page mock-interview and thank-you record")} and use {common.file_link(files["RUBRIC"]["id"], "the six-criterion evidence profile")} to self-score. Days 1-3 stay where first submitted or turned in; do not upload them again. Private live, conference, recorded, AAC, and documented accommodation-aligned routes are supported.</p>'
        assignments[5] = await require_major_assignment(client, mapped_major, major_description, files["MOCK"]["id"])
        assignment_urls = {day: f"/courses/{COURSE_ID}/assignments/{assignment['id']}" for day, assignment in assignments.items()}
        quiz_url = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        students = student_content(files, assignment_urls, quiz_url)
        teachers = teacher_content(files, quiz_url)
        labels = {1: "Job Search and Posting Screen", 2: "Tailored Cover Letter", 3: "Sample Application and References", 4: "Interview Preparation", 5: "Mock Interview and Follow-Up"}
        order, pages = [], {}
        for day in range(1, 6):
            header_title = f"Day {day} · {labels[day]}"
            header = await prior.upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
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
            return entry.get("type") == kind and ((kind == "SubHeader" and entry.get("id") == key) or (kind == "Page" and entry.get("page_url") == key) or (kind == "Assignment" and entry.get("content_id") == key))

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
            await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}", data={"module_item[position]": position, "module_item[title]": title})
        final = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        ordered = sorted(final, key=lambda entry: entry.get("position", 0))
        if len(ordered) != len(order):
            raise RuntimeError(f"Expected {len(order)} Job Skills module items; found {len(ordered)}")
        for position, ((kind, key, _title), entry) in enumerate(zip(order, ordered), 1):
            if entry.get("position") != position or not matches_item(entry, kind, key):
                raise RuntimeError(f"Job Skills module order mismatch at position {position}")

        folder_files = await lock_every_file_in_folder(client, folder)
        folder = await common.api(client, "GET", f"/folders/{folder['id']}")
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        quiz = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
        if module.get("published") or not folder.get("locked") or any(not record.get("locked") for record in folder_files):
            raise RuntimeError("Job Skills module must stay unpublished and every support file/folder locked")
        if quiz.get("published") or quiz.get("quiz_type") != "practice_quiz" or quiz.get("allowed_attempts") != -1 or not quiz.get("show_correct_answers"):
            raise RuntimeError("Interview practice Quiz settings mismatch")
        for day in range(1, 5):
            assignment = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignments[day]['id']}")
            if assignment.get("published") or float(assignment.get("points_possible") or 0) != 0 or assignment.get("grading_type") != "not_graded" or not assignment.get("omit_from_final_grade"):
                raise RuntimeError(f"Day {day} practice assignment grading/publish mismatch")
            assignments[day] = assignment
        major = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignments[5]['id']}")
        if major.get("published") or float(major.get("points_possible") or 0) != 100 or major.get("grading_type") != "points" or major.get("omit_from_final_grade"):
            raise RuntimeError("Job Skills Major grading/publish mismatch")
        if any(page.get("published") for pair in pages.values() for page in pair.values()):
            raise RuntimeError("Every Job Skills page must remain unpublished")
        assignments[5] = major
        print(json.dumps({"module": {"id": module["id"], "published": module["published"]}, "folder": {"id": folder["id"], "locked": folder["locked"], "files_locked": len(folder_files)}, "files": {key: record["id"] for key, record in files.items()}, "quiz": {"id": quiz["id"], "published": quiz.get("published"), "type": quiz.get("quiz_type"), "attempts": quiz.get("allowed_attempts")}, "assignments": {str(day): {"id": assignment["id"], "published": assignment.get("published"), "points": assignment.get("points_possible"), "grading_type": assignment.get("grading_type"), "omit": assignment.get("omit_from_final_grade")} for day, assignment in assignments.items()}, "pages": {str(day): {kind: {"url": page["url"], "published": page["published"]} for kind, page in pair.items()} for day, pair in pages.items()}, "items": [{"position": entry["position"], "type": entry["type"], "title": entry["title"]} for entry in ordered]}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
