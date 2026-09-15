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
STUDENT_GOOGLE_COPY_URLS = {
    1: "https://docs.google.com/document/d/13geM24WvlvHkcl0TjN4P4ClUTIvsbj8soDe-w463Jv0/copy",
    2: "https://docs.google.com/document/d/1YkDFsdLc3uY6AW8WJPEEOQFoJ38pvxHnfduyjXNPfUw/copy",
    3: "https://docs.google.com/document/d/1fYZeXauc58G-c3FDNdhSt_aV_593EzbyNftAx4tmT-k/copy",
    4: "https://docs.google.com/document/d/19LBaW7jeIqYo-RABSwCU-_k3yGdS3kRroMdTJtHcun4/copy",
    5: "https://docs.google.com/document/d/14ljm0n3folAPDb2LEodoSZ3Twxm5dshnAfKLY8V2FDs/copy",
}


# One Google Doc per worksheet (build/google_docs/student_worksheet_docs.json).
# Keyed by (day, anchor label) so a worksheet button never opens the day's exit ticket.
STUDENT_WORKSHEET_COPY_URLS = {
    (1, 'the two-page individual companion'): "https://docs.google.com/document/d/1XovFzxfYMgtkBTSmAk94jfCbEtHP5Lf1JHyWYiLtGfM/copy",
    (2, 'the three-page resume planner'): "https://docs.google.com/document/d/1p2mety0YATf3lOqjvGgQM_zq07ADEuMeaZ7rqjotydA/copy",
    (3, 'the one-page Xello Resume and Revision Record'): "https://docs.google.com/document/d/1OBVfD9KZ3IXGKamOFTej5aC59Et_ZxdgNB9abWf1zcM/copy",
    (4, 'the three-page job-search trace'): "https://docs.google.com/document/d/1bC1wb0p2kU1o07RJyj05v1ERAMI6bU5hMYw605D9v3Y/copy",
    (5, 'the job-search trace'): "https://docs.google.com/document/d/1bC1wb0p2kU1o07RJyj05v1ERAMI6bU5hMYw605D9v3Y/copy",
    (5, 'the resume packet'): "https://docs.google.com/document/d/1p2mety0YATf3lOqjvGgQM_zq07ADEuMeaZ7rqjotydA/copy",
    (5, 'the revision record'): "https://docs.google.com/document/d/1OBVfD9KZ3IXGKamOFTej5aC59Et_ZxdgNB9abWf1zcM/copy",
    (5, 'the two-page audience-test companion'): "https://docs.google.com/document/d/1d5w4mf47X3_vsEuBD1SDTYHjARJVcjBH80PA0edyvFI/copy",
}


def student_copy_link(day, label):
    url = STUDENT_WORKSHEET_COPY_URLS.get((day, label), STUDENT_GOOGLE_COPY_URLS[day])
    return f'<a href="{url}">{label}</a>'

ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/6sw/wk2"
MODULE_NAME = "6SW Wk2: Arts/AV — First Resume and Design Evidence"
MODULE_ALIASES = ("6SW Wk2: Arts/AV - First Resume and Design Evidence",)
TITLES = {
    1: "PRACTICE: Podcast Production Evidence",
    2: "PRACTICE: First Resume Draft",
    3: "SUPPORT: Xello Resume and Revision Record",
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
        "TOPIC": "Resume Revision",
        "OBJECTIVE": "Students will complete the required Xello Resume task and revise one resume bullet so it uses truthful, specific evidence.",
        "TEKS": "d(7)(A)",
        "DOL": "Xello Resume completion verified in the report plus one private before-and-after resume revision.",
        "I_CAN": "complete my Xello Resume and revise one resume bullet with truthful, specific evidence.",
        "SHOW": "Complete the Xello Resume task and submit one private before-and-after resume revision.",
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
    ("Q5 - platform", "What counts as the required resume evidence?", "Xello Resume completion plus the truthful privacy-safe CCE resume and visible revision.", ["Only an Xello completion screen", "Three H&L favorites", "A public Discussion post"], "Correct. The platform task and private CCE evidence have different jobs.", "A completion screen alone does not show the truthful résumé evidence and revision the teacher scores."),
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
    media = lambda pairs: '<h3 style="color:#7b3f8c;border-bottom:3px solid #dcc7e3">Workbook pages</h3>' + ''.join(prior.image_tag(visuals[key]["id"], alt) for key, alt in pairs)
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
        1: {"TITLE": "Behind the Microphone", "PURPOSE": "Plan how Arts/AV workers shape one podcast episode for a clear audience without requiring a public recording.", "TODAY": "<ul><li>identify two production careers;</li><li>complete the FYF episode plan;</li><li>protect privacy, access, and rights;</li><li>record one revision.</li></ul>", "READY": f'<p><strong>Start in FYF pp. 255 and 270-271.</strong> Use {student_copy_link(1, "the two-page individual companion")} or <a href="{urls[1]}">the private annotation activity</a> for the evidence the workbook does not collect.</p>', "MEDIA": media([("p255", "Arts, Audio Visual Technology and Communications cluster opener with example careers"), ("p270", "Behind the Microphone audience, episode, host, topic, and promotion planning"), ("p271", "Podcast outline, pitch, discussion, and optional recording prompt")]), "STEPS": step(1, "Define audience and purpose", "<p>Finish the audience, topic, and purpose jobs in FYF.</p>") + step(2, "Build the episode", "<p>Plan a clear opening, middle, questions or key points, and closing.</p>") + step(3, "Map two production roles", "<p>Name what each worker contributes to the shared work product.</p>") + step(4, "Protect and revise", "<p>Check privacy, audio rights, transcript/caption access, and one revision.</p>"), "EXIT": "<p>Name one career, its work product, and one planning decision that helps the audience.</p>", "DONE": "<ul><li>FYF plan or complete no-workbook route;</li><li>two roles and contributions;</li><li>access/rights checks;</li><li>individual contribution, revision, and evidence limit.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> audience/audiencia · contribution/contribución · sequence/secuencia · transcript/transcripción.</p><p><strong>Use this frame:</strong> The <strong>[role]</strong> contributes <strong>[work product]</strong> so the audience can <strong>[purpose]</strong>.</p>", "FALLBACK": "<p>The locked FYF pages and two-page companion are the complete no-workbook route. No public recording, guest, social post, copyrighted music, H&amp;L, or platform account is required.</p>"},
        2: {"TITLE": "Write a First Resume", "PURPOSE": "Turn true school, project, activity, service, or responsibility evidence into a private one-page resume.", "TODAY": "<ul><li>compare a strong model with a teacher-created weak sample;</li><li>protect sensitive data;</li><li>use one CCE Evidence Log entry or another true experience;</li><li>assemble and check one page.</li></ul>", "READY": f'<p>Open {student_copy_link(2, "the three-page resume planner")} or <a href="{urls[2]}">the private upload/annotation activity</a>. If available, open your <strong>CCE Six-Weeks Evidence Log</strong>; it is a source, not another submission.</p>', "MEDIA": "", "STEPS": step(1, "Compare the models", "<p><strong>Adapted teacher-created weak sample:</strong> <em>Objective: To get a job. Skills: Can use a computer. Project: Helped with flyers.</em> Compare it with Jordan's model. The weak version names broad claims but does not show the action, task, evidence, or purpose.</p>") + step(2, "Choose true evidence", "<p>Start with one CCE Evidence Log entry if you have it, or use another true school, project, activity, service, or responsibility example. Paid work is not required. Jordan is the privacy-safe fallback.</p>") + step(3, "Build the one-page resume", "<p>Use Education, Skills, and Projects/Activities/Service headings. Turn each broad claim into action + task + evidence or purpose.</p>") + step(4, "Run the assembly check", "<p>Readable, consistent, relevant, truthful, and private.</p>"), "EXIT": "<p>Read your strongest bullet and name one detail that makes it evidence.</p>", "DONE": "<ul><li>privacy-safe header;</li><li>standard headings;</li><li>three supported skills;</li><li>specific project/activity/service evidence;</li><li>one readable page.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> heading/encabezado · skill/habilidad · evidence/evidencia · action verb/verbo de acción.</p><p><strong>Use this frame:</strong> I <strong>[action] [task]</strong> so that/resulting in <strong>[evidence or purpose]</strong>.</p>", "FALLBACK": "<p>The packet includes the fictional privacy-safe Jordan model. The CCE Evidence Log helps students locate earlier evidence, but no one reconstructs or re-uploads old work. Canvas or paper is complete. Students use this draft during the required Xello Resume task on Day 3; Xello does not replace the private CCE evidence.</p>"},
        3: {"TITLE": "Complete Xello Resume and Revise", "PURPOSE": "Complete the required Xello Resume task, then strengthen one private résumé bullet with truthful evidence.", "TODAY": "<ul><li>open My Resume in Xello;</li><li>complete truthful résumé sections;</li><li>revise one private CCE résumé bullet;</li><li>finish the report check.</li></ul>", "READY": f'<p>Open <strong>ClassLink &gt; Xello &gt; About Me &gt; My Resume</strong>. Open your <em>Find Your Future</em> workbook to pp. 272-273 for the Attention to Detail activity, and keep your Day 2 CCE résumé and {student_copy_link(3, "the one-page Xello Resume and Revision Record")} open. Do not copy Xello contact details into Canvas or paper.</p>', "MEDIA": media([("p272", "Attention to Detail powerskill page with the sound-design script and audio cue example"), ("p273", "Identify the Missing Details steps for materials, environment, and mood")]), "STEPS": step(1, "Open My Resume", "<p>Use truthful school, project, activity, service, or responsibility evidence. Xello lists no prerequisite for Resume.</p>") + step(2, "Complete the assigned task", "<p>Review or add accurate education, skills, and experiences. If Xello asks for contact information you should not share or do not know, stop and ask your teacher.</p>") + step(3, "Show a private revision", "<p>Use the missing-detail habit from FYF pp. 272-273. Keep the vague before, write an action + task + evidence/purpose after, and explain why it helps.</p>") + step(4, "Finish privately", "<p>Your teacher verifies Xello completion and collects only the CCE revision record, not a profile screenshot.</p>"), "EXIT": "<p>Name the strongest résumé repair and why it helps the reader.</p>", "DONE": "<ul><li>Xello Resume complete or recovery recorded;</li><li>truthful education, skills, and experience evidence;</li><li>visible before-and-after CCE résumé revision;</li><li>no Xello contact details copied into Canvas or paper.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> heading/encabezado · skill/habilidad · experience/experiencia · revise/revisar.</p><p><strong>Use this frame:</strong> The first version only said <strong>[vague claim]</strong>. The revision shows <strong>[evidence]</strong> by <strong>[action]</strong>.</p>", "FALLBACK": "<p>If Xello is unavailable, complete the private CCE revision and tell your teacher. The required Xello task moves to supervised recovery; paper does not count as completion.</p>"},
        4: {"TITLE": "Seven Steps of an Effective Job Search", "PURPOSE": "Practice a complete job-search process with a supplied fictional opportunity and no real-world application.", "TODAY": "<ul><li>trace seven steps;</li><li>screen a supplied posting;</li><li>track the opportunity;</li><li>tailor one true resume bullet.</li></ul>", "READY": f'<p>Open {student_copy_link(4, "the three-page job-search trace")} or <a href="{urls[4]}">the private annotation activity</a>.</p>', "MEDIA": "", "STEPS": step(1, "Target and prepare", "<p>Name the opportunity and ready truthful materials.</p>") + step(2, "Choose sources and search", "<p>Use specific words, location, credible sites, official employer verification, and known adults.</p>") + step(3, "Screen and track", "<p>Read the supplied fictional posting and record source/date, deadline, status, route, and next action.</p>") + step(4, "Tailor and follow up", "<p>Revise one true bullet; act only through an authorized route.</p>"), "EXIT": "<p>Name the most dangerous step to skip and explain the risk.</p>", "DONE": "<ul><li>all seven steps;</li><li>supplied posting screened;</li><li>tracker complete;</li><li>tailored truthful bullet;</li><li>authorized next action.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> target/meta · source/fuente · screen/revisar · track/registrar · tailor/adaptar.</p><p><strong>Use this frame:</strong> The posting asks for <strong>[responsibility]</strong>. My evidence shows <strong>[proof]</strong>. I would verify <strong>[fact]</strong> with <strong>[trusted route]</strong>.</p>", "FALLBACK": "<p>The fixed fictional card is complete. Do not apply, register, contact anyone, upload to an external site, or enter personal information.</p>"},
        5: {"TITLE": "Merch Mode and Final Resume Evidence", "PURPOSE": "Test an original visual concept, then submit the resume, revision, and safe job-search evidence that Minor 2 scores.", "TODAY": "<ul><li>complete the FYF Merch Mode design;</li><li>run a three-second audience test;</li><li>connect one designer duty to a resume bullet;</li><li>submit and self-score Minor 2.</li></ul>", "RESPONSE_SOURCE_FILE_IDS": [files["MERCH"]["id"], files["RESUME"]["id"], files["DETAIL"]["id"], files["SEARCH"]["id"]], "READY": f'<p><strong>Start in FYF pp. 256-258.</strong> Use {student_copy_link(5, "the two-page audience-test companion")} for formative design evidence. For Minor 2, review {student_copy_link(5, "the resume packet")}, {student_copy_link(5, "the revision record")}, {student_copy_link(5, "the job-search trace")}, and {link(files["RUBRIC"]["id"], "the visible rubric")}.</p>' + minor_panel, "MEDIA": media([("p256", "Merch Mode fictional band scenario and identity and audience planning"), ("p257", "Five design principles and brainstorm prompt"), ("p258", "Large sketch area, sharing prompts, and design-career discussion")]), "STEPS": step(1, "Use an original fictional identity", "<p>No real band mark, album art, character, or trademark.</p>") + step(2, "Sketch and test", "<p>Use FYF and the companion. Canva, Adobe Express, or paper are equal.</p>") + step(3, "Connect to graphic design", "<p>Name one duty, work product, evidence limit, and truthful resume bullet.</p>") + step(4, "Submit Minor 2", "<p>Submit the final resume, visible revision, seven-step search evidence, tailored bullet, next action, and self-score. Merch Mode remains formative.</p>"), "EXIT": "<p>State one audience choice, one revision, and one truthful resume bullet.</p>", "DONE": "<ul><li>formative original design practice;</li><li>final privacy-safe resume;</li><li>visible revision record;</li><li>seven-step job-search trace;</li><li>tailored bullet and next action;</li><li>Minor 2 self-score.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> hierarchy/jerarquía · audience/audiencia · revise/revisar · evidence/evidencia · next action/próximo paso.</p><p><strong>Use this frame:</strong> Designed <strong>[work product]</strong> for a fictional <strong>[audience]</strong>; tested <strong>[choice]</strong> and revised <strong>[change]</strong> after <strong>[evidence]</strong>.</p>", "FALLBACK": "<p>Paper is equal. Use the fixed packets for missing work. Merch Mode remains formative; Xello, H&amp;L, eDynamic, public sharing, and software polish are not required.</p>"},
    }


def teacher_content(files):
    link, flow = common.file_link, common.flow
    color = "#7b3f8c"
    sources = '<p><a href="https://www.careeronestop.org/JobSearch/Resumes/ResumeGuide/introduction.aspx">CareerOneStop Resume Guide</a> · <a href="https://www.bls.gov/ooh/arts-and-design/graphic-designers.htm">BLS Graphic Designers</a> · <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte">Irving ISD High School CTE</a>.</p>'
    support = '<p>Point to the visible word bank and complete frame before students write. Accept typing, dictation, annotation, enlarged print, bilingual labels, paper, private rehearsal, and teacher scribing. Score evidence and reasoning, not English mechanics unless meaning is unclear.</p>'
    fallback = '<p>Locked FYF images and fixed companions are the complete absence/platform route. No public recording, public Discussion, real application, employer contact, personal-data entry, device exchange, H&amp;L, Xello, or eDynamic completion is required.</p>'
    return {
        1: {"TITLE": "Behind the Microphone", "SUBTITLE": "50 minutes · FYF pp. 255 and 270-271 first", "ALERT": "<strong>Trim point:</strong> protect audience, structure, two career roles, access/rights, and revision; trim decorative promotion work first.", "PREP": f'<ul><li><strong>Per student:</strong> FYF pp. 255 and 270-271, pencil, and one two-page {link(files["PODCAST"]["id"], "individual companion")} by Canvas annotation or print. Use the locked images only for a missing workbook.</li><li><strong>Grouping:</strong> teams of three or four may build the FYF episode plan; every student completes and submits an individual companion.</li><li>Project this supplied model: <em>The producer contributes the episode order and deadline plan; the editor/access lead contributes the transcript and final sequence so the audience can follow the episode.</em></li><li>Use one labeled paper tray or the private Canvas collector. No recording equipment is required.</li></ul>', "EVIDENCE": "<p>Check the shared FYF plan in place; collect one individual companion per student with two roles/contributions, access and rights checks, individual contribution, revision, and evidence limit.</p>", "FLOW": (
            flow(color, "Minutes 0-7 - Welcome and Arts/AV audio production warm-up", '''<p>Welcome students to Week 2 of 6SW (Arts, A/V Technology &amp; Communications Cluster) and project the podcast production prompt.</p><ul><li>Ask students: <em>“When you listen to a professionally produced podcast, radio broadcast, or audio documentary, what creative and technical jobs happen behind the scenes before that audio ever reaches your headphones? Who structures the interview questions, who operates the mixing console, who edits out background hum, and who generates the written transcript for deaf or hard-of-hearing listeners?”</em></li><li>Collect 2-3 student thoughts: Sound engineers, producers, scriptwriters, voice talent, and accessibility leads!</li><li>Bridge with, <em>“Arts &amp; A/V careers communicate ideas through sound, image, movement, and interaction. Today we analyze FYF pp. 255 and 270-271, explore audio production roles, and design a structured podcast episode plan with strict copyright and accessibility standards.”</em></li></ul>''')
            + flow("#4c8b38", "Minutes 7-15 - Specialized production roles, copyright &amp; accessibility modeling", '''<p>Deconstruct the 4 Core Audio Production Roles and Legal Standards on the screen:</p><ul><li>1. <strong>Executive Producer:</strong> Manages episode structure, timeline, interview bookings, and overall creative vision.</li><li>2. <strong>Audio Engineer / Editor:</strong> Operates microphones and DAW software (digital audio workstation), balances audio levels, eliminates noise, and mixes sound effects.</li><li>3. <strong>Head Scriptwriter / Researcher:</strong> Crafts compelling interview questions, fact-checks background research, and authors host copy.</li><li>4. <strong>Accessibility &amp; Rights Coordinator:</strong> Ensures all background music is royalty-free/licensed and produces an accurate, time-stamped text transcript for universal access.</li><li>Ethical &amp; Legal Boundaries: Never use copyrighted commercial music without permission; protect interviewee privacy; and guarantee equal access through written transcripts.</li><li>Project the Exemplar: Model how the producer's run-of-show sequence connects directly to the audio editor's final cut.</li></ul>''')
            + flow("#1f617a", "Minutes 15-37 - FYF podcast episode planning sprint (FYF pp. 255 &amp; 270-271)", '''<p>Production teams develop their episode blueprint in FYF while each student records on their companion:</p><ul><li>Define Episode Title, Target Audience, and Core Educational Purpose.</li><li>Map the 4-Part Segment Flow: (1) Intro Hook &amp; Music Cue (30s), (2) Main Segment / Expert Interview (3 min), (3) Audience Question / Discussion (2 min), (4) Outro &amp; Call to Action (30s).</li><li>Author 3 Deep Interview Questions: Craft open-ended questions that provoke meaningful stories rather than simple 'yes/no' answers.</li><li>Document Production Responsibilities: Record specific contributions of the Producer vs. Audio Editor.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 23): Verify teams focus on clear episode purpose rather than superficial logos or celebrity gossip.<br>• Lap 2 (Minute 32): Confirm students include copyright-cleared music notes and full text transcripts for accessibility.</li></ul>''')
            + flow("#d39b22", "Minutes 37-45 - Production peer audit &amp; episode revision", '''<p>Elbow partners audit each other's episode plans against professional broadcast standards:</p><ul><li>Partners check: 'Does the episode have a clear hook, verified audio source licensing, and an accessibility plan?'</li><li>Execute One Concrete Revision: Refine an interview question or add specific audio cue instructions to improve pacing.</li></ul>''')
            + flow(color, "Minutes 45-50 - Submit Day 1 Companion and folder storage", '''<p>Students submit their completed two-page companion in Canvas or place paper copies in the collection tray.</p><ul><li><strong>Safe Trim:</strong> Skip whole-class sharing; fiercely protect the 4-part episode structure, two career roles, accessibility/rights check, and private exit.</li></ul>''')
        ), "MONITOR": "<p><strong>Minute 15:</strong> every team has an audience, purpose, and episode topic. If one-third start with promotion, redirect them to audience and purpose. <strong>Minute 30:</strong> the plan has an opening, middle, questions/key points, and closing. <strong>Minute 43:</strong> each companion names two distinct roles and one access/rights decision. Audio may be original, licensed, teacher supplied, or omitted. Safe trim: remove decorative promotion work, not audience, structure, roles, access/rights, or revision. Collect companions; return shared workbooks and close devices.</p>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        2: {"TITLE": "Write a First Resume", "SUBTITLE": "50 minutes · private one-page evidence", "ALERT": "<strong>Privacy boundary:</strong> minimize personal data and never reward invented titles, dates, awards, hours, results, tools, or experience.", "PREP": f'<ul><li><strong>Per student:</strong> one three-page {link(files["RESUME"]["id"], "model, planner, and one-page draft")}, pencil, a private Canvas or paper route, and the student-owned <strong>CCE Six-Weeks Evidence Log</strong> when available.</li><li><strong>Grouping:</strong> independent evidence selection; a student may rehearse one redacted bullet with a partner, but students do not exchange devices, files, or full resumes.</li><li><strong>Preserve the classroom comparison:</strong> project the adapted teacher-created weak sample <em>Objective: To get a job. Skills: Can use a computer. Project: Helped with flyers.</em> Then contrast it with <em>Designed two original event flyers and revised the hierarchy after teacher feedback.</em> Ask what action, task, evidence, or purpose the weak sample hides.</li><li>The Evidence Log is a source only; do not collect it or require old artifacts again. Jordan is the complete fallback. Students use the private draft during the required Xello Resume block on Day 3; the Xello task does not replace Canvas or paper. Use one labeled paper tray or private collector.</li></ul>', "EVIDENCE": "<p>Collect a one-page resume with a safe header, standard headings, specific true evidence, consistent details, and no sensitive information. Do not collect the Evidence Log or old artifacts again.</p>", "FLOW": (
            flow(color, "Minutes 0-7 - Welcome and resume purpose &amp; privacy warm-up", '''<p>Welcome students, seat them with devices or the 3-page resume planner, and project the resume deconstruction prompt.</p><ul><li>Ask students: <em>“What is the true purpose of a resume? Is it an autobiography of your whole life, a personal data form, or a professional marketing document designed to demonstrate relevant skills to a prospective employer? Why must 8th graders NEVER include home addresses, birth dates, personal phone numbers, or social security numbers on a resume?”</em></li><li>Collect 2-3 student thoughts: A resume is a skills summary; personal info creates identity theft and privacy risks!</li><li>Bridge with, <em>“A professional resume is evidence-based and privacy-safe. Today we examine the difference between weak task statements and strong impact bullets, and author your first professional CCE resume.”</em></li></ul>''')
            + flow("#4c8b38", "Minutes 7-17 - Weak vs. strong bullet modeling &amp; standard resume anatomy", '''<p>Display the Contrasting Resume Models and Anatomy on the main screen:</p><ul><li>Anatomy of a Privacy-Safe Middle School Resume:<br>• 1. <strong>Contact Header:</strong> Full name, school name/city/state, professional school email ONLY. (NO home address, personal phone, age, photo, or ID numbers!).<br>• 2. <strong>Objective / Summary Statement:</strong> 1-2 sentences stating the specific opportunity sought and key strengths.<br>• 3. <strong>Education Section:</strong> Current school, anticipated 8th-grade completion date, honors/awards/GPA.<br>• 4. <strong>Relevant Projects &amp; Skills:</strong> Course projects (e.g., CCE budget portfolio, science labs, CAD models), technical tools, and interpersonal skills.<br>• 5. <strong>School Activities &amp; Community Service:</strong> Clubs, sports, library volunteering, church/neighborhood service.</li><li>Project the Teacher-Created Sample Comparison:<br>• <strong>Weak / Vague:</strong> <em>“Objective: To get a job. Skills: Can use a computer. Project: Helped with flyers.”</em><br>• <strong>Strong / Sourced:</strong> <em>“Designed two original community event flyers using digital layout software; revised visual hierarchy and typography based on teacher design feedback to improve readability.”</em><br>• Highlight the 3-Part Impact Formula: <strong>Action Verb + Specific Task + Visible Evidence or Purpose</strong>.</li></ul>''')
            + flow("#1f617a", "Minutes 17-40 - Drafting the privacy-safe one-page resume sprint", '''<p>Students draft their one-page resume using evidence from their CCE Evidence Log (or the Jordan fallback):</p><ul><li>Section 1: Format safe contact header and focused objective statement.</li><li>Section 2: Record education details and academic recognitions.</li><li>Section 3: Author 3 Evidence-Based Action Bullets: Draw from CCE modules (e.g., architectural floor plan design, electrical circuit modeling, Dallas County personal budget calculations).</li><li>Section 4: List technical competencies (Google Docs, Canvas, presentation software) and verified volunteer service.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 24): Verify zero sensitive personal data (no phone numbers, physical addresses, or birthdates).<br>• Lap 2 (Minute 34): Check that every bullet begins with a strong past-tense action verb (e.g., 'Calculated,' 'Designed,' 'Analyzed').</li></ul>''')
            + flow("#d39b22", "Minutes 40-47 - Readability, truthfulness &amp; formatting audit", '''<p>Students conduct an independent 5-point quality audit on their draft:</p><ul><li>Verify: (1) 1-page length, (2) consistent font/margins, (3) 100% truthful claims (no exaggerated experience), (4) zero spelling errors, (5) bullet impact formula followed.</li></ul>''')
            + flow(color, "Minutes 47-50 - Submit Day 2 Resume draft and wrap-up", '''<p>Students submit their completed draft in Canvas or file paper copies in their CCE binder.</p><ul><li><strong>Safe Trim:</strong> Assemble 2 strongest bullets today; finish formatting during catch-up; protect privacy boundaries, headings, and truthful evidence.</li></ul>''')
        ), "MONITOR": "<p><strong>Minute 14:</strong> students can explain why <em>Can use a computer</em> is weaker than an action + task + evidence bullet. If one-third still list traits or tools only, label the four missing parts directly on the teacher-created sample. <strong>Minute 31:</strong> each student has three truthful evidence bullets and standard headings. <strong>Minute 44:</strong> the one-page draft is readable and contains no sensitive data. Safe trim: assemble two strongest bullets plus one supported skill today; finish formatting privately during catch-up. Protect truthfulness, privacy, headings, and a readable one-page route. Collect one resume route; leave the Evidence Log and old artifacts with the student.</p>", "RESOURCES": sources + '<p><strong>Local teacher source:</strong> weak-resume comparison adapted from Jenna Hainlen\'s teacher-created classroom samples; names and adult work-history details were replaced for Grade 7 use.</p>', "SUPPORT": support, "FALLBACK": fallback},
        3: {"TITLE": "Complete Xello Resume and Revise", "SUBTITLE": "50 minutes · required Grade 7 Xello task", "ALERT": "<strong>Required task and privacy boundary:</strong> protect 30 minutes for Xello Resume. The CCE résumé remains the private scored evidence. Do not collect a profile screenshot or Xello contact details.", "PREP": f'<ul><li><strong>Devices:</strong> one per student. Test ClassLink &gt; Xello &gt; About Me &gt; My Resume in a demo account.</li><li>Open the Completion Standards report to <strong>Resume</strong>. Xello lists no prerequisite for this task.</li><li><strong>Per student:</strong> the Day 2 CCE résumé and one {link(files["DETAIL"]["id"], "Xello Resume and Revision Record")} by print or private file.</li><li>Project the revision model: <em>Before: Creative. After: Designed two flyer layouts and revised the larger heading after feedback.</em></li><li>If Xello asks for contact information a student should not share or does not know, the student stops and asks the teacher. Do not invent data.</li></ul>', "EVIDENCE": "<p>Verify Xello Resume in the Completion Standards report and collect one private before-and-after CCE résumé revision. The platform completion does not replace the résumé evidence.</p>", "FLOW": (
            flow(color, "Minutes 0-5 - Welcome and digital resume builder launch warm-up", '''<p>Welcome students, seat them at Chromebooks with their Day 2 resume draft, and project the Xello launch prompt.</p><ul><li>Ask students: <em>“Why do modern companies and school districts use digital resume builders and applicant tracking systems (ATS)? How does transferring your paper resume into a digital database prepare you for future high school internship and college scholarship applications?”</em></li><li>Collect 2-3 student thoughts: Standardized digital formatting, easy updating as you gain experience, and digital job matching!</li><li>Bridge with, <em>“Today we complete the required Grade 7 Xello task: 'Resume' in the About Me section, and document a critical before-and-after revision on your private CCE resume.”</em></li></ul>''')
            + flow("#4c8b38", "Minutes 5-10 - Xello Resume click path &amp; privacy boundary reminder", '''<p>Guide students through the ClassLink launch to Xello on the screen:</p><ul><li>Click Path: ClassLink &rarr; Xello &rarr; About Me &rarr; 'Resume' (or 'My Resume').</li><li>Privacy Gate Reminder: If Xello prompts for personal phone numbers or street addresses that you do not wish to share, use your school address or leave the field blank. Do NOT invent fake data!</li><li>Task Scope: Enter your accurate education, at least two verified skills, school activities or volunteer roles, and at least one project or work experience entry.</li><li>Project the Revision Model: Contrast vague resume bullets with precise, evidence-based statements.</li></ul>''')
            + flow("#1f617a", "Minutes 10-40 - Dedicated Xello Resume builder completion sprint", '''<p>Students build their digital resume inside Xello using their Day 2 draft as a guide:</p><ul><li>Enter Education: Current school and grade level.</li><li>Enter Skills: Add relevant technical, creative, and interpersonal skills.</li><li>Enter Experience / Activities: Input CCE course accomplishments, clubs, athletics, or community service.</li><li>Generate / Preview Resume: Review the formatted output in Xello.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 18): Ensure all students have logged in and are entering real educational data.<br>• Lap 2 (Minute 32): Verify students enter descriptive bullet points rather than single-word entries. Check the educator Completion Standards dashboard to verify task completion.</li></ul>''')
            + flow("#d39b22", "Minutes 40-45 - Private CCE before-and-after revision record", '''<p>Students complete their 1-page private revision record in Canvas (or paper):</p><ul><li>Document One Specific Bullet Revision: Write down the 'Before' phrasing, the 'After' revised phrasing, and the specific reason why the revision improves professional impact.</li><li>Example: <em>Before: Creative. &rarr; After: Designed two flyer layouts and revised typography hierarchy after feedback.</em></li></ul>''')
            + flow(color, "Minutes 45-50 - Dashboard verification check and wrap-up", '''<p>Teacher confirms task completion on the Xello educator dashboard:</p><ul><li>Students submit their private revision record in Canvas and log off Chromebooks.</li><li><strong>Safe Trim:</strong> Protect the 30-minute Xello builder block; trim opening remarks; paper revision supports learning but does not replace digital Xello completion.</li></ul>''')
        ), "MONITOR": "<p><strong>Minute 8:</strong> every student is in My Resume or has a named access/data question. <strong>Minute 25:</strong> sections use truthful evidence; no invented titles, dates, awards, hours, results, tools, or experience. <strong>Minute 40:</strong> Xello completion is visible or recovery is recorded. <strong>Minute 47:</strong> the CCE revision preserves the vague before and specific after. Safe trim: shorten the opening comparison; protect the 30-minute Xello block, visible revision, report check, and privacy boundary.</p>", "RESOURCES": sources + '<p><a href="https://help.xello.world/en-us/content/Knowledge-Base/Xello-6-12/Resume-Builder/Students-Resume-Builder.htm">Xello: Students and Resume Builder</a> · <a href="https://help.xello.world/en-us/Content/Resources/PDFs/Prereq-Lessons-6-12/Resume.pdf">Xello My resume lesson prerequisites and artifacts</a></p>', "SUPPORT": support, "FALLBACK": "<p>If Xello is unavailable, complete the private CCE revision and record the access barrier. Schedule the required Xello Resume task in supervised recovery; paper does not count as completion.</p>"},
        4: {"TITLE": "Seven Steps of an Effective Job Search", "SUBTITLE": "50 minutes · supplied fictional posting", "ALERT": "<strong>Safety boundary:</strong> students do not apply, create accounts, contact anyone, upload to an external site, or enter personal information.", "PREP": f'<ul><li><strong>Per student:</strong> one three-page {link(files["SEARCH"]["id"], "seven-step trace")}, pencil, and the student\'s private resume or the printed Jordan model.</li><li><strong>Grouping:</strong> independent tracker; pairs may screen the supplied posting, then each student tailors one true bullet.</li><li>Project this model: <em>Target: classroom design helper. Source: supplied CCE card. Screen: fictional, no contact route. Status: practice only. Next action: compare one true flyer bullet to the responsibilities.</em></li><li>No live job board, open search, application, account, employer contact, or external upload is required.</li></ul>', "EVIDENCE": "<p>Collect one seven-step trace per student with screening evidence, tracker, tailored true bullet, and authorized next action.</p>", "FLOW": (
            flow(color, "Minutes 0-5 - Welcome and job search strategy warm-up", '''<p>Welcome students, seat them with the 3-page job search trace, and project the job hunt prompt.</p><ul><li>Ask students: <em>“If someone tells you, ‘I'm going to get a job this weekend by just searching online and applying to every link I see,’ why is that an ineffective and potentially dangerous strategy? What critical steps must happen before and after you click submit?”</em></li><li>Collect 2-3 student thoughts: Scams, applying for jobs you aren't qualified for, uncustomized resumes, and lack of follow-up!</li><li>Bridge with, <em>“A successful job search follows a disciplined, professional methodology. Today we master the 7 Steps of an Effective Job Search under TEKS d(6)(A) and screen a supplied fictional job posting.”</em></li></ul>''')
            + flow("#4c8b38", "Minutes 5-15 - Deconstructing the 7-step job search framework", '''<p>Display the 7 Sequential Steps of an Effective Job Search on the screen:</p><ul><li>1. <strong>Step 1: Self-Inventory &amp; Target:</strong> Assess personal skills, interests, work values, age/transportation limits, and desired roles.</li><li>2. <strong>Step 2: Prepare Professional Materials:</strong> Create and update a tailored, error-free resume, references list, and portfolio samples.</li><li>3. <strong>Step 3: Source Legitimate Opportunities:</strong> Use credible school job boards, verified employer career pages, and professional networking (avoid unverified ads).</li><li>4. <strong>Step 4: Screen &amp; Analyze Postings:</strong> Scrutinize job duties, minimum age, required qualifications, schedule, and red flags (e.g., wire transfer requests).</li><li>5. <strong>Step 5: Tailor Application &amp; Submit:</strong> Customize resume bullets to match posting keywords; submit through authorized channels only.</li><li>6. <strong>Step 6: Interview Preparation:</strong> Research the company, practice answering behavioral questions using STAR technique, and prepare questions for the interviewer.</li><li>7. <strong>Step 7: Professional Follow-Up:</strong> Send a polite thank-you email within 24 hours and maintain an organized job application tracking log.</li><li>Safety Boundary: Never enter personal data, bank info, or credit cards on unverified sites!</li></ul>''')
            + flow("#1f617a", "Minutes 15-32 - Fictional posting analysis &amp; application tracking sprint", '''<p>Students analyze the supplied fictional posting ('Community Center Youth Recreation Assistant') in their trace packet:</p><ul><li>Complete Job Screening Matrix: Record employer name, role, wage, hours, minimum age requirement, and mandatory qualifications.</li><li>Log Entry in Job Tracker: Record date, position, company, status ('Screening / In Progress'), and next action.</li><li>Tailor One Resume Bullet: Select one true accomplishment from Day 2 and rewrite it to directly mirror a responsibility in the recreation posting.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 22): Verify students correctly identify the age and qualification requirements.<br>• Lap 2 (Minute 28): Check that tailored bullets use truthful student experiences, not invented work history.</li></ul>''')
            + flow("#d39b22", "Minutes 32-45 - Partner screening audit &amp; follow-up protocol", '''<p>Elbow partners audit each other's 7-step tracker and tailored bullet:</p><ul><li>Ensure the tailored bullet directly targets a duty from the posting without exaggerating.</li><li>Draft a professional 3-sentence follow-up inquiry to check on application status.</li></ul>''')
            + flow(color, "Minutes 45-50 - Submit Day 4 Job Search Trace and wrap-up", '''<p>Students submit their completed trace in Canvas or turn in packet sheets.</p><ul><li><strong>Safe Trim:</strong> Screen one field together as a class; fiercely protect the 7-step sequence, posting screening, tailored bullet, and follow-up protocol.</li></ul>''')
        ), "MONITOR": "<p><strong>Minute 14:</strong> students can sequence all seven steps. If one-third apply before screening, replay target → prepare → source/search → screen → track → tailor/authorized apply → follow-up. <strong>Minute 30:</strong> the tracker keeps source/date, fictional status, and authorized route visible. <strong>Minute 43:</strong> the tailored bullet uses true evidence and the next action names a trusted verification route. Safe trim: supply the search string and screen one field together; protect screening, tracker, tailored bullet, and authorized next action. Collect one trace.</p>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        5: {"TITLE": "Merch Mode and Final Resume Evidence", "SUBTITLE": "50 minutes · FYF pp. 256-258 + Minor 2", "ALERT": "<strong>Minor 2:</strong> score only the resume, visible revision, safe seven-step search, tailored evidence, and next action. Merch Mode is formative and trims first.", "PREP": f'<ul><li><strong>Per student:</strong> FYF pp. 256-258, pencil/markers, one two-page {link(files["MERCH"]["id"], "audience-test companion")}, the final resume, revision record, job-search trace, and access to the {link(files["RUBRIC"]["id"], "Minor 2 rubric")}.</li><li><strong>Start-of-class readiness gate:</strong> students place the resume, revision record, job-search trace, and rubric in order before beginning Merch Mode. Send missing-evidence students to the fixed recovery facts/models inside those packets; do not make them reconstruct Days 2-4 or complete Merch Mode first.</li><li><strong>Grouping:</strong> design and Minor evidence are individual; use pairs only for the three-second test. Teacher conference or self-test is equal.</li><li>Project this design model: <em>The intended message is calm electronic music. The title is the largest element; one original wave symbol repeats; the viewer first noticed the title. Revision: increase contrast between the title and background.</em></li><li>Default digital collection: one combined PDF/document with the final resume, revision record, seven-step search evidence, and rubric self-score/visible revision. Typed route follows those exact labels. Paper route is one labeled set. Do not submit Merch Mode as a second graded artifact.</li></ul>', "EVIDENCE": "<p>Formative: one original design concept, quick audience test, revision, and graphic-design connection. Minor 2: collect one combined digital file, exact labeled typed response, or one labeled paper set containing the final resume, visible revision, seven-step trace, tailored bullet, next action, rubric self-score, and visible revision.</p>", "FLOW": (
            flow(color, "Minutes 0-8 - Start-of-class readiness gate &amp; visual branding warm-up", '''<p>Welcome students, execute the Minor 2 readiness gate, and project the graphic design prompt.</p><ul><li><strong>Readiness Gate (Minutes 0-4):</strong> Students assemble their completed Week 2 artifacts in order: (1) Final Resume, (2) Revision Record, (3) 7-Step Job Search Trace, and (4) Minor 2 Rubric. Students missing prior work receive the fixed recovery model to complete today's analysis.</li><li>Ask students: <em>“When a graphic designer creates merchandise for a brand, tour, or community organization, how do typography hierarchy, color contrast, and iconography communicate an immediate visual message in less than three seconds?”</em></li><li>Collect 2-3 student thoughts: Bold headers catch the eye first; colors set the mood; clean symbols communicate identity!</li><li>Bridge with, <em>“Today is Minor 2! We complete our formative 'Merch Mode' design challenge on FYF pp. 256-258, conduct a 3-second visual hierarchy test, and synthesize our final resume and job search evidence for Minor 2 scoring.”</em></li></ul>''')
            + flow("#4c8b38", "Minutes 8-16 - Merch Mode design principles &amp; 3-second test modeling", '''<p>Display Visual Hierarchy Principles and the 3-Second Test Protocol on the screen:</p><ul><li>1. <strong>Original Visual Branding:</strong> Create an original band, brand, or community event merchandise design (no copyrighted corporate logos or trademarked characters!).</li><li>2. <strong>Visual Hierarchy:</strong> The most critical element (e.g., event title) must be the largest and highest contrast; supporting details (date, venue) are secondary.</li><li>3. <strong>The 3-Second Visual Test:</strong> Display your design to a partner for exactly 3 seconds, then cover it. Partner answers: (1) What was the first element you noticed? (2) What message or feeling did the design convey?</li><li>BLS Labor Benchmark for Graphic Designers: May 2024 U.S. median annual wage = $61,300; bachelor's degree typical entry; 2% projected growth (2024-34); ~20,000 annual openings nationwide.</li><li>Review the 16-Point Minor 2 Rubric: Truthfulness &amp; Privacy, Visible Resume Revision, 7-Step Job Search Process, and Tailored Evidence &amp; Next Action.</li></ul>''')
            + flow("#1f617a", "Minutes 16-30 - FYF Merch Mode sketch &amp; 3-second partner test (FYF pp. 256-258)", '''<p>Students sketch their original merchandise design in FYF (or digital tool) and conduct the test:</p><ul><li>Sketch original layout incorporating a focal symbol, clear title typography, and intentional color palette.</li><li>Conduct the 3-Second Test with elbow partner and record feedback in companion.</li><li>Execute One Design Revision: Modify contrast or element size to ensure the primary message is instantly legible.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 21): Verify all designs are 100% original student concepts (no copyrighted Marvel, Nike, or anime logos).<br>• Lap 2 (Minute 27): Confirm partners record specific visual feedback from the 3-second test.</li></ul>''')
            + flow("#d39b22", "Minutes 30-43 - Minor 2 evidence assembly &amp; rubric self-score", '''<p>Students assemble their final Minor 2 portfolio package:</p><ul><li>Assemble the 4 required components: (1) One-page Privacy-Safe Resume, (2) Before-and-After Revision Record, (3) 7-Step Job Search Trace, (4) Tailored Bullet &amp; Next Action.</li><li>Self-Score against the 16-point Minor 2 rubric across all 4 criteria.</li><li>Execute One Final Evidence Polish: Refine the weakest section to elevate the score.</li></ul>''')
            + flow(color, "Minutes 43-50 - Submit Minor 2 Package and wrap-up", '''<p>Students submit their completed Minor 2 package in Canvas or turn in paper sets.</p><ul><li>Congratulate students on mastering professional resume authoring and job search literacy!</li><li><strong>Safe Trim:</strong> Defer advanced Merch Mode coloring to catch-up; fiercely protect Minor 2 portfolio assembly, rubric self-score, privacy compliance, and final submission.</li></ul>''')
        ), "MONITOR": "<p><strong>Minute 8:</strong> every student has all Minor evidence in order or is using the fixed recovery model for a missing criterion. If one-third are missing work, pause Merch Mode and run the rubric recovery route. <strong>Minute 22:</strong> ready students have one original testable design concept and one viewer/self-test note. <strong>Minute 37:</strong> every Minor route contains the resume, revision, seven-step trace, tailored bullet, and next action. <strong>Minute 46:</strong> the rubric has a self-score and visible evidence repair. Safe trim: defer Merch Mode build/polish and accept one paper sketch plus self-test; never trim Minor assembly, self-score, privacy check, or submission. Current BLS: $61,300 May 2024 U.S. median; bachelor's typical; 2% projected 2024-34; about 20,000 annual openings. These are not DFW starting pay or a guarantee.</p>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
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
        students = student_content(files, visuals, urls)
        teachers = teacher_content(files)
        labels = {1: "Behind the Microphone", 2: "Write a First Resume", 3: "Complete Xello Resume and Revise", 4: "Seven Steps of an Effective Job Search", 5: "Merch Mode and Final Resume Evidence"}
        interactions = {1: ("Assignment", assignments[1]["id"], TITLES[1]), 2: ("Assignment", assignments[2]["id"], TITLES[2]), 4: ("Assignment", assignments[4]["id"], TITLES[4]), 5: ("Assignment", assignments[5]["id"], TITLES[5])}
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
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title)]
            if day in interactions:
                kind, key, title = interactions[day]
                await prior.upsert_item(client, module["id"], kind, key, title)
                order.append((kind, key, title))
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
        if len(order) != 19 or len(ordered) != 19:
            raise RuntimeError(f"Expected exactly 19 Resume module items; built {len(order)} and found {len(ordered)}")
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
        for day, pair in pages.items():
            for kind, value in pair.items():
                page = await common.api(client, "GET", f"/courses/{COURSE_ID}/pages/{value['url']}")
                if page.get("published") is not False:
                    raise RuntimeError(f"Published 6SW Wk2 {kind} page on Day {day}")
                pair[kind] = page
        folder, support_file_count = await lock_folder_files(client, folder)
        visual_folder, visual_file_count = await lock_folder_files(client, visual_folder)
        print(json.dumps({"module": {"id": module["id"], "published": module["published"]}, "folder": {"id": folder["id"], "locked": folder["locked"], "files": support_file_count}, "visual_folder": {"id": visual_folder["id"], "locked": visual_folder["locked"], "files": visual_file_count}, "files": {key: record["id"] for key, record in files.items()}, "visuals": {key: record["id"] for key, record in visuals.items()}, "assignments": {str(day): {"id": assignment["id"], "published": assignment.get("published"), "points": assignment.get("points_possible"), "grading_type": assignment.get("grading_type"), "omit_from_final_grade": assignment.get("omit_from_final_grade")} for day, assignment in assignments.items()}, "pages": {str(day): {kind: {"url": page["url"], "published": page["published"]} for kind, page in pair.items()} for day, pair in pages.items()}, "items": [{"position": entry["position"], "type": entry["type"], "title": entry["title"]} for entry in ordered]}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
