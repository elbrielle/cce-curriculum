"""Build the unpublished 6SW Week 2 Arts/AV, resume, and job-search module."""

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
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/6sw/wk2"
MODULE_NAME = "6SW Wk2: Arts/AV — First Resume and Design Evidence"
MODULE_ALIASES = ("6SW Wk2: Arts/AV - First Resume and Design Evidence",)
TITLES = {
    1: "PRACTICE: Podcast Production Evidence",
    2: "PRACTICE: First Resume Draft",
    3: "PRACTICE: Attention to Detail and Resume Revision",
    4: "PRACTICE: Seven-Step Job Search",
    5: "MINOR 2: Resume, Revision, and Job-Search Evidence",
}
MINOR_ALIASES = ("MINOR 2: Resume and Merch Design Evidence",)
TEMPLATES = ROOT / "build/canvas/templates"
WORKSHEET_NAMES = {
    "PODCAST": "6sw-wk2-podcast-production-plan.pdf",
    "RESUME": "6sw-wk2-first-resume-draft.pdf",
    "DETAIL": "6sw-wk2-audio-cue-and-resume-revision.pdf",
    "SEARCH": "6sw-wk2-effective-job-search.pdf",
    "MERCH": "6sw-wk2-merch-mode-design.pdf",
    "RUBRIC": "6sw-wk2-resume-design-rubric.pdf",
}
VISUAL_PAGES = (255, 256, 257, 258, 270, 271, 272, 273)
RUBRIC_MARKER = 'data-cce-rubric-note="cce-advisory-rubric-v1"'


def preflight():
    required = [
        TEMPLATES / "6sw-wk2-student.html",
        TEMPLATES / "6sw-wk2-teacher.html",
        *(ROOT / "docs/resources/worksheets" / name for name in WORKSHEET_NAMES.values()),
        *(ASSETS / f"fyf-p{page}.jpg" for page in VISUAL_PAGES),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"6SW Wk2 preflight missing required files: {missing}")


async def canvas_preflight(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    accepted_modules = {MODULE_NAME, *MODULE_ALIASES}
    module_matches = [entry for entry in modules if entry.get("name") in accepted_modules]
    if len(module_matches) > 1:
        raise RuntimeError(f"Duplicate 6SW Wk2 modules: {[entry['id'] for entry in module_matches]}")
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    for day in (1, 2, 4):
        matches = [entry for entry in assignments if entry.get("name") == TITLES[day]]
        if len(matches) > 1:
            raise RuntimeError(f"Duplicate assignments named {TITLES[day]!r}: {[entry['id'] for entry in matches]}")
    minor_matches = [entry for entry in assignments if entry.get("name") in {TITLES[5], *MINOR_ALIASES}]
    if len(minor_matches) != 1:
        raise RuntimeError(f"Expected exactly one mapped Resume Minor; found {[entry['id'] for entry in minor_matches]}")
    minor = minor_matches[0]
    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    minor_groups = [entry for entry in groups if entry.get("name") == "Minor Assessments (40%)"]
    if len(minor_groups) != 1:
        raise RuntimeError(f"Expected exactly one Minor Assessments (40%) group; found {[entry['id'] for entry in minor_groups]}")
    description = minor.get("description") or ""
    if (
        minor.get("assignment_group_id") != minor_groups[0].get("id")
        or minor.get("published") is not False
        or float(minor.get("points_possible") or 0) != 100
        or minor.get("grading_type") != "points"
        or minor.get("omit_from_final_grade") is not False
        or RUBRIC_MARKER not in description
    ):
        raise RuntimeError("Mapped Resume Minor failed prewrite group/grade/rubric/unpublished checks")
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    quiz_matches = [entry for entry in quizzes if entry.get("title") == TITLES[3]]
    if len(quiz_matches) > 1:
        raise RuntimeError(f"Duplicate quizzes named {TITLES[3]!r}: {[entry['id'] for entry in quiz_matches]}")
    marker_pattern = re.compile(
        r'<div\b[^>]*data-cce-rubric-note=["\']cce-advisory-rubric-v1["\'][^>]*>.*?</div>',
        re.IGNORECASE | re.DOTALL,
    )
    marker_match = marker_pattern.search(description)
    if not marker_match:
        raise RuntimeError("Mapped Resume Minor is missing the exact rubric conversion-note block")
    return minor, minor_groups[0], marker_match.group(0)

CONTRACTS = {
    1: {
        "TOPIC": "Media Production",
        "OBJECTIVE": "Students will identify at least two Arts/AV career opportunities and explain how their production roles contribute to a podcast work product.",
        "TEKS": "d(1)(C)",
        "DOL": "Completed FYF Behind the Microphone plan plus a two-page individual production-role, access, and revision companion.",
        "I_CAN": "identify two Arts/AV careers and explain how their production roles contribute to a podcast.",
        "SHOW": "Complete the FYF plan and two-page companion with two roles, access/rights checks, and a visible revision.",
    },
    2: {
        "TOPIC": "Resume Writing",
        "OBJECTIVE": "Students will write a truthful, privacy-safe one-page resume with standard headings and specific evidence from school, projects, activities, service, or responsibilities.",
        "TEKS": "d(7)(A)",
        "DOL": "Three-page resume planner and assembled one-page resume submitted privately in Canvas or on paper.",
        "I_CAN": "write a truthful, privacy-safe one-page resume with standard headings and specific evidence.",
        "SHOW": "Complete the three-page planner and assemble a readable one-page resume without sensitive data.",
    },
    3: {
        "TOPIC": "Revision Evidence",
        "OBJECTIVE": "Students will identify a sound-production career opportunity and revise an audio cue and one resume bullet so another reader can act without guessing.",
        "TEKS": "d(1)(C), d(7)(A)",
        "DOL": "Completed FYF audio-cue work, one-page resume before-and-after revision record, and reviewed Quiz feedback.",
        "I_CAN": "identify a sound-production career and revise an audio cue and resume bullet so another reader does not have to guess.",
        "SHOW": "Complete the FYF cue work, record one visible resume revision, and use the practice Quiz feedback.",
    },
    4: {
        "TOPIC": "Job Search",
        "OBJECTIVE": "Students will identify and apply seven steps of an effective job search to one supplied fictional opportunity without applying or sharing personal data.",
        "TEKS": "d(6)(A)",
        "DOL": "Three-page seven-step trace with a supplied fictional posting, screening record, tracker, tailored resume bullet, and authorized next action.",
        "I_CAN": "apply seven job-search steps to a fictional opportunity while protecting personal data.",
        "SHOW": "Complete the three-page trace, screen the supplied posting, tailor one true bullet, and name an authorized next action.",
    },
    5: {
        "TOPIC": "Visual Communication",
        "OBJECTIVE": "Students will identify a graphic-design career opportunity, test an audience-centered visual concept, and synthesize truthful resume, revision, and job-search evidence.",
        "TEKS": "d(1)(C), d(6)(A), d(7)(A)",
        "DOL": "Final private résumé, visible revision record, seven-step job-search evidence, tailored bullet, next action, and visible 16-point Minor 2 rubric; FYF Merch Mode remains formative.",
        "I_CAN": "test a visual concept and use this week's resume, revision, and job-search evidence to show what I can do next.",
        "SHOW": "Complete the FYF design practice, then submit the final private resume, revision, job-search evidence, tailored bullet, next action, and self-score.",
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


async def mapped_minor_assignment(client):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    accepted = {TITLES[5], *MINOR_ALIASES}
    matches = [entry for entry in assignments if entry.get("name") in accepted]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one existing mapped Resume Minor named in {sorted(accepted)!r}; found {len(matches)}")
    found = matches[0]
    if (
        found.get("published") is not False
        or float(found.get("points_possible") or 0) != 100
        or found.get("grading_type") != "points"
        or found.get("omit_from_final_grade") is not False
        or RUBRIC_MARKER not in (found.get("description") or "")
    ):
        raise RuntimeError("Refusing to modify Resume Minor: prewrite grade/rubric/unpublished invariant failed")
    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group = next((entry for entry in groups if entry.get("id") == found.get("assignment_group_id")), None)
    if not group or group.get("name") != "Minor Assessments (40%)":
        raise RuntimeError("Refusing to modify Resume Minor outside Minor Assessments (40%)")
    return found


async def require_minor_assignment(client, found, group, description, scoring_note):
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
        assignment.get("published") is not False
        or assignment.get("assignment_group_id") != group.get("id")
        or float(assignment.get("points_possible") or 0) != 100
        or assignment.get("grading_type") != "points"
        or assignment.get("omit_from_final_grade") is not False
        or RUBRIC_MARKER not in (assignment.get("description") or "")
    ):
        raise RuntimeError("Resume Minor failed post-update grade/rubric/unpublished checks")
    return assignment


async def upload_locked(client, path, folder_path):
    uploaded = await common.upload(client, path, folder_path)
    record = await common.api(client, "GET", f"/files/{uploaded['id']}")
    if not record.get("locked"):
        record = await common.api(client, "PUT", f"/files/{uploaded['id']}", data={"locked": "true"})
    if record.get("locked") is not True:
        raise RuntimeError(f"Canvas did not lock {path.name!r}")
    return record


async def lock_folder_files(client, folder):
    current = await common.api(client, "GET", f"/folders/{folder['id']}")
    if not current.get("locked"):
        current = await common.api(client, "PUT", f"/folders/{folder['id']}", data={"locked": "true"})
    if current.get("locked") is not True:
        raise RuntimeError(f"Canvas did not lock folder {folder['id']}")
    for record in await common.paged(client, f"/folders/{folder['id']}/files"):
        if not record.get("locked"):
            await common.api(client, "PUT", f"/files/{record['id']}", data={"locked": "true"})
    final = await common.paged(client, f"/folders/{folder['id']}/files")
    if any(record.get("locked") is not True for record in final):
        raise RuntimeError(f"Unlocked files remain in folder {folder['id']}")
    return current, len(final)


async def assert_annotation_assignment(client, title, assignment, source_id):
    fresh = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignment['id']}")
    source = await common.api(client, "GET", f"/files/{source_id}")
    clone_id = int(fresh.get("annotatable_attachment_id") or 0)
    clone = await common.api(client, "GET", f"/files/{clone_id}") if clone_id else {}
    if clone and not clone.get("locked"):
        clone = await common.api(client, "PUT", f"/files/{clone_id}", data={"locked": "true"})
    required_routes = {"student_annotation", "online_upload", "online_text_entry"}
    if (
        fresh.get("published") is not False
        or float(fresh.get("points_possible") or 0) != 0
        or fresh.get("grading_type") != "percent"
        or fresh.get("omit_from_final_grade") is not True
        or set(fresh.get("submission_types") or []) != required_routes
        or not clone_id
        or source.get("locked") is not True
        or clone.get("locked") is not True
        or clone.get("filename") != source.get("filename")
        or int(clone.get("size") or -1) != int(source.get("size") or -2)
    ):
        raise RuntimeError(f"Practice annotation invariant failed for {title!r}")
    return fresh


async def upsert_practice_assignment(client, title, description, attachment_id):
    assignment = await common.upsert_assignment(
        client,
        title,
        description,
        ["student_annotation", "online_upload", "online_text_entry"],
        attachment_id,
    )
    return await assert_annotation_assignment(client, title, assignment, attachment_id)


QUESTIONS = [
    ("Q1 - privacy", "Which item stays off the classroom resume?", "Home address and personal phone number", ["Relevant school project", "True technical skill", "Current school name"], "Correct. This classroom resume minimizes sensitive contact data.", "Projects, skills, and education can be relevant; sensitive contact data is excluded."),
    ("Q2 - evidence", "Which bullet gives the strongest evidence?", "Designed two original event flyers and revised the hierarchy after teacher feedback.", ["Creative", "Good at Canva", "Hard worker"], "Correct. It uses action, task, and revision evidence.", "Traits or tool names without evidence are too vague."),
    ("Q3 - cue detail", "Why add material and surface to an audio cue?", "They help the sound worker create the intended sound without guessing.", ["They guarantee the movie is popular.", "They replace the director.", "They make every sound louder."], "Correct. Detail supports another worker's action.", "Detail improves clarity; it does not guarantee outcomes or change roles."),
    ("Q4 - search step", "What should happen before a student acts on a job-board result?", "Screen the posting and verify the employer through an official route or known adult.", ["Upload personal data immediately.", "Message the contact in the ad.", "Assume the first result is current."], "Correct. Searching and verifying are separate steps.", "A result or message is not independent verification."),
    ("Q5 - platform", "What counts as the required resume evidence?", "The truthful privacy-safe resume in Canvas or on paper; an optional Xello copy is supplemental.", ["Only an Xello completion screen", "Three H&L favorites", "A public Discussion post"], "Correct. The standard is the resume, not a platform click.", "Xello and H&L are not required completion tasks here, and resumes remain private."),
]
if len({question[0] for question in QUESTIONS}) != len(QUESTIONS):
    raise ValueError("Resume practice Quiz question names must be unique")


async def upsert_quiz(client):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    matches = [quiz for quiz in quizzes if quiz.get("title") == TITLES[3]]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one {TITLES[3]!r} Quiz; found {len(matches)}")
    data = {"quiz[title]": TITLES[3], "quiz[description]": "<p>Ungraded, unlimited-retry practice on resume evidence, privacy, detail, and job-search safety.</p>", "quiz[quiz_type]": "practice_quiz", "quiz[published]": "false", "quiz[allowed_attempts]": "-1", "quiz[show_correct_answers]": "true", "quiz[shuffle_answers]": "false"}
    quiz = await common.api(client, "PUT" if matches else "POST", f"/courses/{COURSE_ID}/quizzes/{matches[0]['id']}" if matches else f"/courses/{COURSE_ID}/quizzes", data=data)
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
        raise RuntimeError("Resume practice Quiz question set mismatch")
    fields = []
    for name in expected:
        fields.extend([("order[][id]", str(by_name[name]["id"])), ("order[][type]", "question")])
    await common.api(client, "POST", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/reorder", content=urlencode(fields), headers={"Content-Type": "application/x-www-form-urlencoded"})
    final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    if [entry.get("question_name") for entry in final_questions] != expected:
        raise RuntimeError("Resume practice Quiz order mismatch")
    final = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
    if final.get("published") is not False or final.get("quiz_type") != "practice_quiz" or int(final.get("allowed_attempts") or 0) != -1:
        raise RuntimeError("Resume practice Quiz state mismatch")
    return final


def student_content(files, visuals, urls):
    link, step = common.file_link, common.step
    media = lambda pairs: '<h3 style="color:#7b3f8c;border-bottom:3px solid #dcc7e3">Licensed workbook pages</h3>' + ''.join(prior.image_tag(visuals[key]["id"], alt) for key, alt in pairs)
    minor_panel = (
        f'<section data-cce-marker="{SUBMISSION_LINK_MARKER}" '
        'style="border:2px solid #1f617a;border-radius:12px;padding:18px 20px;'
        'margin:24px 0;background:#f2f8fb">'
        '<h3 style="margin:0 0 8px;color:#1f617a">Submit your minor evidence</h3>'
        '<p style="margin:0 0 14px">Use the visible rubric to check your work. Upload one '
        'combined PDF/document containing the final resume, visible revision record, and seven-step '
        'job-search evidence; or turn in one labeled paper set. Typed responses use the rubric labels '
        'in the same order. Do not upload Merch Mode.</p>'
        f'<p style="margin:0"><a href="{urls[5]}" '
        'style="display:inline-block;background:#1f617a;color:#fff;padding:11px 18px;'
        'border-radius:6px;text-decoration:none;font-weight:700" '
        f'data-api-endpoint="/api/v1{urls[5]}" data-api-returntype="Assignment">'
        f'Open {TITLES[5]}</a></p></section>'
    )
    return {
        1: {"TITLE": "Behind the Microphone", "PURPOSE": "Plan how Arts/AV workers shape one podcast episode for a clear audience without requiring a public recording.", "TODAY": "<ul><li>identify two production careers;</li><li>complete the FYF episode plan;</li><li>protect privacy, access, and rights;</li><li>record one revision.</li></ul>", "READY": f'<p><strong>Start in FYF pp. 255 and 270-271.</strong> Use {link(files["PODCAST"]["id"], "the two-page individual companion")} or <a href="{urls[1]}">the private annotation activity</a> for the evidence the workbook does not collect.</p>', "MEDIA": media([("p255", "Arts, Audio Visual Technology and Communications cluster opener with example careers"), ("p270", "Behind the Microphone audience, episode, host, topic, and promotion planning"), ("p271", "Podcast outline, pitch, discussion, and optional recording prompt")]), "STEPS": step(1, "Define audience and purpose", "<p>Finish the audience, topic, and purpose jobs in FYF.</p>") + step(2, "Build the episode", "<p>Plan a clear opening, middle, questions or key points, and closing.</p>") + step(3, "Map two production roles", "<p>Name what each worker contributes to the shared work product.</p>") + step(4, "Protect and revise", "<p>Check privacy, audio rights, transcript/caption access, and one revision.</p>"), "EXIT": "<p>Name one career, its work product, and one planning decision that helps the audience.</p>", "DONE": "<ul><li>FYF plan or complete no-workbook route;</li><li>two roles and contributions;</li><li>access/rights checks;</li><li>individual contribution, revision, and evidence limit.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> audience/audiencia · contribution/contribución · sequence/secuencia · transcript/transcripción.</p><p><strong>Use this frame:</strong> The <strong>[role]</strong> contributes <strong>[work product]</strong> so the audience can <strong>[purpose]</strong>.</p>", "FALLBACK": "<p>The locked FYF pages and two-page companion are the complete no-workbook route. No public recording, guest, social post, copyrighted music, H&amp;L, or platform account is required.</p>"},
        2: {"TITLE": "Write a First Resume", "PURPOSE": "Turn true school, project, activity, service, or responsibility evidence into a private one-page resume.", "TODAY": "<ul><li>study a fictional model;</li><li>protect sensitive data;</li><li>draft specific evidence bullets;</li><li>assemble and check one page.</li></ul>", "READY": f'<p>Open {link(files["RESUME"]["id"], "the three-page resume planner")} or <a href="{urls[2]}">the private upload/annotation activity</a>.</p>', "MEDIA": "", "STEPS": step(1, "Study the model", "<p>Notice the safe header, standard headings, and action + task + evidence bullets.</p>") + step(2, "Choose true evidence", "<p>Paid work is not required. Use school, projects, activities, service, or responsibilities.</p>") + step(3, "Build the one-page resume", "<p>Use Education, Skills, and Projects/Activities/Service headings.</p>") + step(4, "Run the assembly check", "<p>Readable, consistent, relevant, truthful, and private.</p>"), "EXIT": "<p>Read your strongest bullet and name one detail that makes it evidence.</p>", "DONE": "<ul><li>privacy-safe header;</li><li>standard headings;</li><li>three supported skills;</li><li>specific project/activity/service evidence;</li><li>one readable page.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> heading/encabezado · skill/habilidad · evidence/evidencia · action verb/verbo de acción.</p><p><strong>Use this frame:</strong> I <strong>[action] [task]</strong> so that/resulting in <strong>[evidence or purpose]</strong>.</p>", "FALLBACK": "<p>The packet includes a fictional privacy-safe model. Canvas or paper is complete. Optional Xello copying can happen later; it is not required evidence.</p>"},
        3: {"TITLE": "Attention to Detail and Resume Revision", "PURPOSE": "Make an audio cue and resume bullet specific enough that another worker or reader does not have to guess.", "TODAY": "<ul><li>complete the FYF audio-cue work;</li><li>identify a sound-production role;</li><li>repair one vague resume bullet;</li><li>use Quiz feedback.</li></ul>", "READY": f'<p><strong>Start in FYF pp. 272-273.</strong> Open {link(files["DETAIL"]["id"], "the one-page resume revision record")} and <a href="{urls[3]}">the retryable practice Quiz</a>.</p>', "MEDIA": media([("p272", "Attention to Detail introduction and incomplete Kitchen Mess audio cue script"), ("p273", "Missing-detail prompts, cue-rewrite space, discussion, and optional safe activity")]), "STEPS": step(1, "Add usable cue detail", "<p>Complete the FYF work with action, material/object, surface/environment, timing/intensity, and mood where relevant.</p>") + step(2, "Name the career connection", "<p>Identify one sound-production role and work product.</p>") + step(3, "Show a resume revision", "<p>Keep the vague before, specific after, reason, and consistency repair.</p>") + step(4, "Use feedback", "<p>The practice Quiz is ungraded and unlimited retry.</p>"), "EXIT": "<p>Name the strongest detail or resume repair and why it helps.</p>", "DONE": "<ul><li>FYF cue work or no-workbook route;</li><li>sound-production career/work product;</li><li>visible before-and-after resume evidence;</li><li>one consistency repair;</li><li>Quiz feedback reviewed.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> cue/señal · material/material · surface/superficie · timing/ritmo · revise/revisar.</p><p><strong>Use this frame:</strong> The first version only said <strong>[vague claim]</strong>. The revision shows <strong>[evidence]</strong> by <strong>[action]</strong>.</p>", "FALLBACK": "<p>The locked FYF pages plus the one-page revision record are the complete route. No device exchange or login sharing is allowed.</p>"},
        4: {"TITLE": "Seven Steps of an Effective Job Search", "PURPOSE": "Practice a complete job-search process with a supplied fictional opportunity and no real-world application.", "TODAY": "<ul><li>trace seven steps;</li><li>screen a supplied posting;</li><li>track the opportunity;</li><li>tailor one true resume bullet.</li></ul>", "READY": f'<p>Open {link(files["SEARCH"]["id"], "the three-page job-search trace")} or <a href="{urls[4]}">the private annotation activity</a>.</p>', "MEDIA": "", "STEPS": step(1, "Target and prepare", "<p>Name the opportunity and ready truthful materials.</p>") + step(2, "Choose sources and search", "<p>Use specific words, location, credible sites, official employer verification, and known adults.</p>") + step(3, "Screen and track", "<p>Read the supplied fictional posting and record source/date, deadline, status, route, and next action.</p>") + step(4, "Tailor and follow up", "<p>Revise one true bullet; act only through an authorized route.</p>"), "EXIT": "<p>Name the most dangerous step to skip and explain the risk.</p>", "DONE": "<ul><li>all seven steps;</li><li>supplied posting screened;</li><li>tracker complete;</li><li>tailored truthful bullet;</li><li>authorized next action.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> target/meta · source/fuente · screen/revisar · track/registrar · tailor/adaptar.</p><p><strong>Use this frame:</strong> The posting asks for <strong>[responsibility]</strong>. My evidence shows <strong>[proof]</strong>. I would verify <strong>[fact]</strong> with <strong>[trusted route]</strong>.</p>", "FALLBACK": "<p>The fixed fictional card is complete. Do not apply, register, contact anyone, upload to an external site, or enter personal information.</p>"},
        5: {"TITLE": "Merch Mode and Final Resume Evidence", "PURPOSE": "Test an original visual concept, then submit the resume, revision, and safe job-search evidence that Minor 2 scores.", "TODAY": "<ul><li>complete the FYF Merch Mode design;</li><li>run a three-second audience test;</li><li>connect one designer duty to a resume bullet;</li><li>submit and self-score Minor 2.</li></ul>", "READY": f'<p><strong>Start in FYF pp. 256-258.</strong> Use {link(files["MERCH"]["id"], "the two-page audience-test companion")} for formative design evidence. For Minor 2, review {link(files["RESUME"]["id"], "the resume packet")}, {link(files["DETAIL"]["id"], "the revision record")}, {link(files["SEARCH"]["id"], "the job-search trace")}, and {link(files["RUBRIC"]["id"], "the visible rubric")}.</p>' + minor_panel, "MEDIA": media([("p256", "Merch Mode fictional band scenario and identity and audience planning"), ("p257", "Five design principles and brainstorm prompt"), ("p258", "Large sketch area, sharing prompts, and design-career discussion")]), "STEPS": step(1, "Use an original fictional identity", "<p>No real band mark, album art, character, or trademark.</p>") + step(2, "Sketch and test", "<p>Use FYF and the companion. Canva, Adobe Express, or paper are equal.</p>") + step(3, "Connect to graphic design", "<p>Name one duty, work product, evidence limit, and truthful resume bullet.</p>") + step(4, "Submit Minor 2", "<p>Submit the final resume, visible revision, seven-step search evidence, tailored bullet, next action, and self-score. Merch Mode remains formative.</p>"), "EXIT": "<p>State one audience choice, one revision, and one truthful resume bullet.</p>", "DONE": "<ul><li>formative original design practice;</li><li>final privacy-safe resume;</li><li>visible revision record;</li><li>seven-step job-search trace;</li><li>tailored bullet and next action;</li><li>Minor 2 self-score.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> hierarchy/jerarquía · audience/audiencia · revise/revisar · evidence/evidencia · next action/próximo paso.</p><p><strong>Use this frame:</strong> Designed <strong>[work product]</strong> for a fictional <strong>[audience]</strong>; tested <strong>[choice]</strong> and revised <strong>[change]</strong> after <strong>[evidence]</strong>.</p>", "FALLBACK": "<p>Paper is equal. Use the fixed packets for missing work. Merch Mode remains formative; Xello, H&amp;L, eDynamic, public sharing, and software polish are not required.</p>"},
    }


def teacher_content(files):
    link, flow = common.file_link, common.flow
    color = "#7b3f8c"
    sources = '<p><a href="https://www.careeronestop.org/JobSearch/Resumes/ResumeGuide/introduction.aspx">CareerOneStop Resume Guide</a> · <a href="https://www.bls.gov/ooh/arts-and-design/graphic-designers.htm">BLS Graphic Designers</a> · <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte">Irving ISD High School CTE</a>.</p>'
    support = '<p>Point to the visible word bank and complete frame before students write. Accept typing, dictation, annotation, enlarged print, bilingual labels, paper, private rehearsal, and teacher scribing. Score evidence and reasoning, not English mechanics unless meaning is unclear.</p>'
    fallback = '<p>Locked FYF images and fixed companions are the complete absence/platform route. No public recording, public Discussion, real application, employer contact, personal-data entry, device exchange, H&amp;L, Xello, or eDynamic completion is required.</p>'
    return {
        1: {"TITLE": "Behind the Microphone", "SUBTITLE": "50 minutes · FYF pp. 255 and 270-271 first", "ALERT": "<strong>Trim point:</strong> protect audience, structure, two career roles, access/rights, and revision; trim decorative promotion work first.", "PREP": f'<ul><li><strong>Per student:</strong> FYF pp. 255 and 270-271, pencil, and one two-page {link(files["PODCAST"]["id"], "individual companion")} by Canvas annotation or print. Use the locked images only for a missing workbook.</li><li><strong>Grouping:</strong> teams of three or four may build the FYF episode plan; every student completes and submits an individual companion.</li><li>Project this supplied model: <em>The producer contributes the episode order and deadline plan; the editor/access lead contributes the transcript and final sequence so the audience can follow the episode.</em></li><li>Use one labeled paper tray or the private Canvas collector. No recording equipment is required.</li></ul>', "EVIDENCE": "<p>Check the shared FYF plan in place; collect one individual companion per student with two roles/contributions, access and rights checks, individual contribution, revision, and evidence limit.</p>", "FLOW": flow(color, "Cluster opener · 7", "Name how Arts/AV workers communicate through sound, image, text, movement, and interaction.") + flow("#4c8b38", "Read the brief · 8", "Set audience, privacy, copyright, and accessibility boundaries.") + flow("#1f617a", "Complete the FYF plan · 22", "Monitor purpose, structure, questions/key points, and closing.") + flow("#d39b22", "Individual production evidence · 8", "Use partner, teacher, or self-review; record roles and revision.") + flow(color, "Exit · 5", "Career, work product, and audience-centered decision."), "MONITOR": "<p><strong>Minute 15:</strong> every team has an audience, purpose, and episode topic. If one-third start with promotion, redirect them to audience and purpose. <strong>Minute 30:</strong> the plan has an opening, middle, questions/key points, and closing. <strong>Minute 43:</strong> each companion names two distinct roles and one access/rights decision. Audio may be original, licensed, teacher supplied, or omitted. Safe trim: remove decorative promotion work, not audience, structure, roles, access/rights, or revision. Collect companions; return shared workbooks and close devices.</p>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        2: {"TITLE": "Write a First Resume", "SUBTITLE": "50 minutes · private one-page evidence", "ALERT": "<strong>Privacy boundary:</strong> minimize personal data and never reward invented titles, dates, awards, hours, results, tools, or experience.", "PREP": f'<ul><li><strong>Per student:</strong> one three-page {link(files["RESUME"]["id"], "model, planner, and one-page draft")}, pencil, and a private Canvas or paper route.</li><li><strong>Grouping:</strong> independent evidence selection; a student may rehearse one redacted bullet with a partner, but students do not exchange devices, files, or full resumes.</li><li>Project this model: <em>Designed two original event flyers and revised the hierarchy after teacher feedback.</em> Nonexample: <em>Good at Canva.</em></li><li>Optional Xello copying must not replace Canvas or paper. Use one labeled paper tray or private collector.</li></ul>', "EVIDENCE": "<p>Collect a one-page resume with a safe header, standard headings, specific true evidence, consistent details, and no sensitive information.</p>", "FLOW": flow(color, "Purpose and privacy · 7", "A resume matches true evidence to a target; it is not a personal-data form.") + flow("#4c8b38", "Study the model · 10", "Notice standard headings, action verbs, specific evidence, and simple formatting.") + flow("#1f617a", "Plan and assemble · 23", "Use school, projects, activities, service, responsibilities, or the labeled scenario.") + flow("#d39b22", "Assembly check · 7", "Check readability, truthfulness, consistency, relevance, and privacy.") + flow(color, "Exit · 3", "Strongest bullet and its evidence."), "MONITOR": "<p><strong>Minute 14:</strong> students can point to the action, task, and evidence/purpose in the model. If one-third list traits or tools only, contrast the model and nonexample. <strong>Minute 31:</strong> each student has three truthful evidence bullets and standard headings. <strong>Minute 44:</strong> the one-page draft is readable and contains no sensitive data. Safe trim: assemble two strongest bullets plus one supported skill today; finish formatting privately during catch-up. Protect truthfulness, privacy, headings, and a readable one-page route. Collect one resume route.</p>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        3: {"TITLE": "Attention to Detail and Resume Revision", "SUBTITLE": "50 minutes · FYF pp. 272-273 first", "ALERT": "<strong>Evidence boundary:</strong> a revision is visible before-and-after evidence, not a claim that the student fixed it.", "PREP": f'<ul><li><strong>Per student:</strong> FYF pp. 272-273, pencil, the Day 2 resume, and one {link(files["DETAIL"]["id"], "resume revision record")} by print or private file. The locked FYF images replace a missing workbook.</li><li>Project this cue model: <em>Fast rubber-soled footsteps cross a tile floor, then stop at the metal bowl.</em> Resume model: <em>Before: Creative. After: Designed two flyer layouts and revised the larger heading after feedback.</em></li><li>Peer review is optional and uses only a student-controlled redacted bullet. Keep the five-question Quiz ungraded, unpublished, and unlimited-retry.</li></ul>', "EVIDENCE": "<p>Check the FYF cue work in place; collect the one-page career/resume revision record. The Quiz repairs labels and is not another written DOL.</p>", "FLOW": flow(color, "Detail model · 7", "Another worker should be able to act without guessing.") + flow("#4c8b38", "FYF cue work · 15", "Add action, material/object, surface/environment, timing/intensity, and mood where relevant.") + flow("#1f617a", "Resume audit · 13", "Replace one vague claim and identify one consistency issue.") + flow("#d39b22", "Record before and after · 10", "Require visible evidence and why it helps the reader.") + flow(color, "Quiz and exit · 5", "Use feedback; name the strongest repair."), "MONITOR": "<p><strong>Minute 14:</strong> each cue names an action plus at least two useful conditions. If one-third only add adjectives, reproject the cue model and label material, surface, and timing. <strong>Minute 31:</strong> the resume record preserves the vague before and specific after. <strong>Minute 44:</strong> students explain why the change helps and name one consistency repair. Safe trim: complete one cue together and leave the Quiz for catch-up; never trim the visible before/after resume evidence. Collect the revision record and return resumes.</p>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        4: {"TITLE": "Seven Steps of an Effective Job Search", "SUBTITLE": "50 minutes · supplied fictional posting", "ALERT": "<strong>Safety boundary:</strong> students do not apply, create accounts, contact anyone, upload to an external site, or enter personal information.", "PREP": f'<ul><li><strong>Per student:</strong> one three-page {link(files["SEARCH"]["id"], "seven-step trace")}, pencil, and the student\'s private resume or the printed Jordan model.</li><li><strong>Grouping:</strong> independent tracker; pairs may screen the supplied posting, then each student tailors one true bullet.</li><li>Project this model: <em>Target: classroom design helper. Source: supplied CCE card. Screen: fictional, no contact route. Status: practice only. Next action: compare one true flyer bullet to the responsibilities.</em></li><li>No live job board, open search, application, account, employer contact, or external upload is required.</li></ul>', "EVIDENCE": "<p>Collect one seven-step trace per student with screening evidence, tracker, tailored true bullet, and authorized next action.</p>", "FLOW": flow(color, "Warm-up · 5", "Why is search jobs not a complete plan?") + flow("#4c8b38", "Model the seven steps · 10", "Walk one target from preparation through authorized follow-up.") + flow("#1f617a", "Build Steps 1-4 · 12", "Target, materials, credible sources, and search string.") + flow("#d39b22", "Screen and track · 13", "Use only the supplied fictional posting.") + flow("#1f617a", "Tailor and follow up · 7", "Revise one true bullet and name an authorized next action.") + flow(color, "Exit · 3", "Most dangerous skipped step and risk."), "MONITOR": "<p><strong>Minute 14:</strong> students can sequence all seven steps. If one-third apply before screening, replay target → prepare → source/search → screen → track → tailor/authorized apply → follow-up. <strong>Minute 30:</strong> the tracker keeps source/date, fictional status, and authorized route visible. <strong>Minute 43:</strong> the tailored bullet uses true evidence and the next action names a trusted verification route. Safe trim: supply the search string and screen one field together; protect screening, tracker, tailored bullet, and authorized next action. Collect one trace.</p>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        5: {"TITLE": "Merch Mode and Final Resume Evidence", "SUBTITLE": "50 minutes · FYF pp. 256-258 + Minor 2", "ALERT": "<strong>Minor 2:</strong> score only the resume, visible revision, safe seven-step search, tailored evidence, and next action. Merch Mode is formative and trims first.", "PREP": f'<ul><li><strong>Per student:</strong> FYF pp. 256-258, pencil/markers, one two-page {link(files["MERCH"]["id"], "audience-test companion")}, the final resume, revision record, job-search trace, and access to the {link(files["RUBRIC"]["id"], "Minor 2 rubric")}.</li><li><strong>Start-of-class readiness gate:</strong> students place the resume, revision record, job-search trace, and rubric in order before beginning Merch Mode. Send missing-evidence students to the fixed recovery facts/models inside those packets; do not make them reconstruct Days 2-4 or complete Merch Mode first.</li><li><strong>Grouping:</strong> design and Minor evidence are individual; use pairs only for the three-second test. Teacher conference or self-test is equal.</li><li>Project this design model: <em>The intended message is calm electronic music. The title is the largest element; one original wave symbol repeats; the viewer first noticed the title. Revision: increase contrast between the title and background.</em></li><li>Default digital collection: one combined PDF/document with the final resume, revision record, seven-step search evidence, and rubric self-score/visible revision. Typed route follows those exact labels. Paper route is one labeled set. Do not submit Merch Mode as a second graded artifact.</li></ul>', "EVIDENCE": "<p>Formative: one original design concept, quick audience test, revision, and graphic-design connection. Minor 2: collect one combined digital file, exact labeled typed response, or one labeled paper set containing the final resume, visible revision, seven-step trace, tailored bullet, next action, rubric self-score, and visible revision.</p>", "FLOW": flow(color, "Readiness gate · 8", "Put all Minor evidence in order; route missing evidence to the fixed packet models.") + flow("#4c8b38", "Merch principle and sketch · 8", "Use one audience, message, hierarchy choice, and original symbol.") + flow("#d39b22", "Three-second test · 8", "Record what was noticed and make one visible revision.") + flow("#1f617a", "Career and resume link · 6", "Graphic-design duty, evidence limit, and truthful bullet.") + flow("#4c8b38", "Minor review and self-score · 13", "Check all four criteria and make one visible evidence repair.") + flow(color, "Package and submit · 7", "Upload one combined file, type exact labels, or turn in one labeled set."), "MONITOR": "<p><strong>Minute 8:</strong> every student has all Minor evidence in order or is using the fixed recovery model for a missing criterion. If one-third are missing work, pause Merch Mode and run the rubric recovery route. <strong>Minute 22:</strong> ready students have one original testable design concept and one viewer/self-test note. <strong>Minute 37:</strong> every Minor route contains the resume, revision, seven-step trace, tailored bullet, and next action. <strong>Minute 46:</strong> the rubric has a self-score and visible evidence repair. Safe trim: defer Merch Mode build/polish and accept one paper sketch plus self-test; never trim Minor assembly, self-score, privacy check, or submission. Current BLS: $61,300 May 2024 U.S. median; bachelor's typical; 2% projected 2024-34; about 20,000 annual openings. These are not DFW starting pay or a guarantee.</p>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
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
        minor_preflight, minor_group, scoring_note = await canvas_preflight(client)
        module = await ensure_module(client)
        path = "course files/CCR Materials/6SW/Wk2"
        folder = await common.ensure_folder(client, path)
        files = {key: await upload_locked(client, ROOT / "docs/resources/worksheets" / name, path) for key, name in WORKSHEET_NAMES.items()}
        visual_path = "course files/CCR Materials/6SW/Wk2/Locked Licensed Visuals"
        visual_folder = await common.ensure_folder(client, visual_path)
        visuals = {f"p{page}": await upload_locked(client, ASSETS / f"fyf-p{page}.jpg", visual_path) for page in VISUAL_PAGES}
        folder, support_file_count = await lock_folder_files(client, folder)
        visual_folder, visual_file_count = await lock_folder_files(client, visual_folder)
        quiz = await upsert_quiz(client)
        assignments = {}
        for day, key in {1: "PODCAST", 2: "RESUME", 4: "SEARCH"}.items():
            descriptions = {
                1: "Complete FYF pp. 270-271 first. Submit only the individual production-role companion by annotation, upload, typed labeled responses, or one labeled paper copy. Do not rebuild or submit a second podcast plan.",
                2: "Submit one private first resume route: annotate the attached model/planner, upload the completed resume, type the labeled headings and bullets, or turn in one labeled paper copy. Do not include sensitive contact or reference data.",
                4: "Complete one seven-step route using the attached fictional posting: annotation, upload, typed labeled responses, or one labeled paper copy. Do not apply, contact anyone, create an account, or enter personal data.",
            }
            assignments[day] = await upsert_practice_assignment(client, TITLES[day], f"<p>{descriptions[day]}</p>", files[key]["id"])
        evidence_links = (
            f'<p>Submit the private final evidence: {common.file_link(files["RESUME"]["id"], "one-page resume")}, '
            f'{common.file_link(files["DETAIL"]["id"], "visible revision record")}, '
            f'{common.file_link(files["SEARCH"]["id"], "seven-step job-search trace and tailored bullet")}, '
            f'and {common.file_link(files["RUBRIC"]["id"], "self-score rubric")}. '
            'Default digital route: upload one combined PDF/document containing the final resume, visible revision record, seven-step job-search evidence, tailored bullet, next action, self-score, and visible revision. Typed route: use those exact labels in that order. Paper route: turn in one labeled bundle. Merch Mode design is formative and is not another graded artifact. '
            'Career preference, platform access, graphic polish, paid work history, public sharing, and English mechanics unless meaning is unclear do not determine the score.</p>'
        )
        assignments[5] = await require_minor_assignment(client, minor_preflight, minor_group, evidence_links, scoring_note)
        urls = {day: f"/courses/{COURSE_ID}/assignments/{assignment['id']}" for day, assignment in assignments.items()}
        urls[3] = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        students = student_content(files, visuals, urls)
        teachers = teacher_content(files)
        labels = {1: "Behind the Microphone", 2: "Write a First Resume", 3: "Attention to Detail and Resume Revision", 4: "Seven Steps of an Effective Job Search", 5: "Merch Mode and Final Resume Evidence"}
        interactions = {1: ("Assignment", assignments[1]["id"], TITLES[1]), 2: ("Assignment", assignments[2]["id"], TITLES[2]), 3: ("Quiz", quiz["id"], TITLES[3]), 4: ("Assignment", assignments[4]["id"], TITLES[4]), 5: ("Assignment", assignments[5]["id"], TITLES[5])}
        order, pages = [], {}
        for day in range(1, 6):
            header_title = f"Day {day} · {labels[day]}"
            await prior.upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header_title, header_title))
            student_title = f"STUDENT: 6SW Wk2 Day {day} - {labels[day]}"
            student_page = await common.upsert_page(client, student_title, common.render("6sw-wk2-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, **CONTRACTS[day], **students[day]}))
            teacher_title = f"TEACHER: 6SW Wk2 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(client, teacher_title, common.render("6sw-wk2-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **CONTRACTS[day], **teachers[day]}))
            await prior.upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await prior.upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            kind, key, title = interactions[day]
            await prior.upsert_item(client, module["id"], kind, key, title)
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title), (kind, key, title)]
            pages[day] = {"teacher": teacher_page, "student": student_page}

        def matches_item(entry, kind, key):
            return entry.get("type") == kind and ((kind == "SubHeader" and entry.get("title") == key) or (kind == "Page" and entry.get("page_url") == key) or (kind in ("Assignment", "Quiz") and entry.get("content_id") == key))

        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        keep_ids = set()
        for kind, key, _title in order:
            match = next((entry for entry in items if entry["id"] not in keep_ids and matches_item(entry, kind, key)), None)
            if not match:
                raise RuntimeError(f"Missing expected Resume module item: {kind} {key}")
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
        if len(order) != 20 or len(ordered) != 20:
            raise RuntimeError(f"Expected exactly 20 Resume module items; built {len(order)} and found {len(ordered)}")
        for position, ((kind, key, title), entry) in enumerate(zip(order, ordered), 1):
            if entry.get("position") != position or not matches_item(entry, kind, key) or entry.get("title") != title or entry.get("published") is not False:
                raise RuntimeError(f"Resume module order mismatch at position {position}")
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        if module.get("published") is not False:
            raise RuntimeError("Resume module unexpectedly published")
        fresh_modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
        fresh_aliases = [entry for entry in fresh_modules if entry.get("name") in {MODULE_NAME, *MODULE_ALIASES}]
        if len(fresh_aliases) != 1 or fresh_aliases[0].get("id") != module.get("id") or fresh_aliases[0].get("published") is not False:
            raise RuntimeError("Final Resume module alias/state invariant failed")
        for day, key in {1: "PODCAST", 2: "RESUME", 4: "SEARCH"}.items():
            assignments[day] = await assert_annotation_assignment(client, TITLES[day], assignments[day], files[key]["id"])
        minor = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignments[5]['id']}")
        if (
            minor.get("assignment_group_id") != minor_group.get("id")
            or minor.get("published") is not False
            or float(minor.get("points_possible") or 0) != 100
            or minor.get("grading_type") != "points"
            or minor.get("omit_from_final_grade") is not False
            or RUBRIC_MARKER not in (minor.get("description") or "")
        ):
            raise RuntimeError("Final Resume Minor invariant failed")
        assignments[5] = minor
        quiz = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
        if quiz.get("published") is not False or quiz.get("quiz_type") != "practice_quiz" or int(quiz.get("allowed_attempts") or 0) != -1:
            raise RuntimeError("Final Resume Quiz invariant failed")
        for day, pair in pages.items():
            for kind, value in pair.items():
                page = await common.api(client, "GET", f"/courses/{COURSE_ID}/pages/{value['url']}")
                if page.get("published") is not False:
                    raise RuntimeError(f"Published 6SW Wk2 {kind} page on Day {day}")
                pair[kind] = page
        folder, support_file_count = await lock_folder_files(client, folder)
        visual_folder, visual_file_count = await lock_folder_files(client, visual_folder)
        print(json.dumps({"module": {"id": module["id"], "published": module["published"]}, "folder": {"id": folder["id"], "locked": folder["locked"], "files": support_file_count}, "visual_folder": {"id": visual_folder["id"], "locked": visual_folder["locked"], "files": visual_file_count}, "files": {key: record["id"] for key, record in files.items()}, "visuals": {key: record["id"] for key, record in visuals.items()}, "quiz": {"id": quiz["id"], "published": quiz.get("published")}, "assignments": {str(day): {"id": assignment["id"], "published": assignment.get("published"), "points": assignment.get("points_possible"), "grading_type": assignment.get("grading_type"), "omit_from_final_grade": assignment.get("omit_from_final_grade")} for day, assignment in assignments.items()}, "pages": {str(day): {kind: {"url": page["url"], "published": page["published"]} for kind, page in pair.items()} for day, pair in pages.items()}, "items": [{"position": entry["position"], "type": entry["type"], "title": entry["title"]} for entry in ordered]}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
