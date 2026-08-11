"""Build the unpublished 5SW Week 2 Civil Engineering evidence module."""

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
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/5sw/wk2"
MODULE_NAME = "5SW Wk2: Civil Engineering — Systems, Evidence, and Design"

SYSTEMS_TITLE = "PRACTICE: Civil Engineering and Systems Evidence"
QUIZ_TITLE = "PRACTICE: Assessment and Emerging Work Evidence Check"
QUIZ_ALIASES = ("MINOR 2: Assessment and Emerging Work Evidence Check",)
ASSESSMENT_TITLE = "MINOR 2: Assessment and Emerging-Specialty Evidence"
DESIGN_TITLE = "PRACTICE: Bridge Design Evidence"
TEST_TITLE = "PRACTICE: Bridge Test and Redesign Evidence"
PORTFOLIO_TITLE = "FORMATIVE: Civil Engineering Evidence Portfolio"

WORKSHEET_NAMES = {
    "CAREER": "5sw-wk2-civil-engineer-and-systems-evidence.pdf",
    "ASSESS": "5sw-wk2-assessment-and-emerging-specialty.pdf",
    "DESIGN": "5sw-wk2-bridge-design-options.pdf",
    "TEST": "5sw-wk2-bridge-test-and-redesign.pdf",
    "SYNTHESIS": "5sw-wk2-engineering-synthesis.pdf",
    "RUBRIC": "5sw-wk2-assessment-emerging-rubric.pdf",
    "PORTFOLIO_RUBRIC": "5sw-wk2-engineering-evidence-rubric.pdf",
}

VISUAL_NAMES = {
    1: (
        ("cluster", "fyf-p103-engineering-opener.jpg"),
        ("systems", "fyf-p174-systems-thinking.jpg"),
        ("kitchen", "fyf-p175-kitchen-plan.jpg"),
    ),
    5: (
        ("mars", "fyf-p106-mission-to-mars.jpg"),
        ("rover", "fyf-p107-rover-design.jpg"),
    ),
}

RUBRIC_NOTE_PATTERN = re.compile(
    r'<div data-cce-rubric-note="cce-advisory-rubric-v1".*?</div>',
    flags=re.I | re.S,
)


def preflight():
    required = [
        ROOT / "build/canvas/templates/5sw-wk2-student.html",
        ROOT / "build/canvas/templates/5sw-wk2-teacher.html",
        *(ROOT / "docs/resources/worksheets" / name for name in WORKSHEET_NAMES.values()),
        *(ASSETS / f"day{day}" / name for day, entries in VISUAL_NAMES.items() for _key, name in entries),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"5SW Wk2 preflight missing required files: {missing}")


async def canvas_preflight(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    module_matches = [entry for entry in modules if entry.get("name") == MODULE_NAME]
    if len(module_matches) > 1:
        raise RuntimeError(f"Duplicate Canvas modules named {MODULE_NAME!r}: {[entry['id'] for entry in module_matches]}")

    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    assessment_matches = [entry for entry in assignments if entry.get("name") == ASSESSMENT_TITLE]
    if len(assessment_matches) != 1:
        raise RuntimeError(
            f"Expected one existing mapped Minor assignment named {ASSESSMENT_TITLE!r}; found {len(assessment_matches)}"
        )
    for title in (SYSTEMS_TITLE, DESIGN_TITLE, TEST_TITLE, PORTFOLIO_TITLE):
        matches = [entry for entry in assignments if entry.get("name") == title]
        if len(matches) > 1:
            raise RuntimeError(f"Duplicate practice/formative assignments named {title!r}: {[entry['id'] for entry in matches]}")

    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    minor_groups = [entry for entry in groups if entry.get("name") == "Minor Assessments (40%)"]
    if len(minor_groups) != 1:
        raise RuntimeError("Expected exactly one assignment group named 'Minor Assessments (40%)'")
    assessment = assessment_matches[0]
    rubric_note = RUBRIC_NOTE_PATTERN.search(assessment.get("description") or "")
    if (
        assessment.get("published")
        or float(assessment.get("points_possible") or 0) != 100
        or assessment.get("assignment_group_id") != minor_groups[0]["id"]
        or assessment.get("grading_type") != "points"
        or assessment.get("omit_from_final_grade") is not False
        or rubric_note is None
    ):
        raise RuntimeError(
            f"Mapped Minor invariant failed before module writes: published={assessment.get('published')}, "
            f"points={assessment.get('points_possible')}, group={assessment.get('assignment_group_id')}, "
            f"grading={assessment.get('grading_type')}, omit={assessment.get('omit_from_final_grade')}, "
            f"rubric_note={rubric_note is not None}"
        )

    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    quiz_matches = [
        entry for entry in quizzes if entry.get("title") == QUIZ_TITLE or entry.get("title") in QUIZ_ALIASES
    ]
    if len(quiz_matches) > 1:
        raise RuntimeError(f"Duplicate current/legacy Week 2 practice quizzes: {[entry['id'] for entry in quiz_matches]}")
    return assessment, minor_groups[0], rubric_note.group(0)


async def upload_locked(client, path, folder_path):
    uploaded = await common.upload(client, path, folder_path)
    record = await common.api(client, "GET", f"/files/{uploaded['id']}")
    if not record.get("locked"):
        record = await common.api(client, "PUT", f"/files/{uploaded['id']}", data={"locked": "true"})
    if not record.get("locked"):
        raise RuntimeError(f"Canvas did not lock uploaded file {path.name!r}")
    return record


async def lock_folder_files(client, folder):
    current = await common.api(client, "GET", f"/folders/{folder['id']}")
    if not current.get("locked"):
        current = await common.api(client, "PUT", f"/folders/{folder['id']}", data={"locked": "true"})
    if not current.get("locked"):
        raise RuntimeError(f"Canvas did not lock folder {folder['id']}")
    for entry in await common.paged(client, f"/folders/{folder['id']}/files"):
        if not entry.get("locked"):
            await common.api(client, "PUT", f"/files/{entry['id']}", data={"locked": "true"})
    final = await common.paged(client, f"/folders/{folder['id']}/files")
    unlocked = [entry.get("display_name") or entry.get("filename") for entry in final if not entry.get("locked")]
    if unlocked:
        raise RuntimeError(f"Unlocked files remain in folder {folder['id']}: {unlocked}")
    return current, len(final)


CONTRACTS = {
    1: {
        "TOPIC": "Engineering Systems",
        "OBJECTIVE": "Students will describe the Engineering cluster, one civil-engineering route, and how one design choice affects a larger system.",
        "TEKS": "d(1)(B), d(1)(C), d(2)(A)",
        "DOL": "Career/preparation card + kitchen systems decision.",
        "I_CAN": "describe the Engineering cluster, one civil-engineering route, and how one choice affects a larger system.",
        "SHOW": "Complete the career/preparation evidence and one FYF kitchen systems decision.",
    },
    2: {
        "TOPIC": "Assessment Impact",
        "OBJECTIVE": "Students will explain how one assessment may affect a personal route and evaluate a changing engineering specialty.",
        "TEKS": "d(3)(E), d(1)(D)",
        "DOL": "Assessment-impact decision + emerging-specialty evaluation.",
        "I_CAN": "explain one possible assessment impact and evaluate a changing engineering specialty with dated evidence.",
        "SHOW": "Submit Minor 2 with an assessment decision, verification question, two-specialty comparison, judgment, and limitation.",
    },
    3: {
        "TOPIC": "Bridge Design Evidence",
        "OBJECTIVE": "Students will compare bridge systems, create two options, and select a design from evidence.",
        "TEKS": "d(1)(C)",
        "DOL": "Two-view options + critique + individual career-role decision.",
        "I_CAN": "compare bridge systems, create two constrained options, and identify the next career role and work product.",
        "SHOW": "Submit two top-and-side options, critique, supported choice, and individual career-role decision.",
    },
    4: {
        "TOPIC": "Test and Redesign",
        "OBJECTIVE": "Students will record a standardized result and use failure evidence to justify a redesign.",
        "TEKS": "d(1)(C)",
        "DOL": "Fixed-data failure analysis + individual redesign and career-role limit.",
        "I_CAN": "analyze standardized results, justify a redesign, and identify who reviews the evidence next.",
        "SHOW": "Submit a fixed-data failure analysis, individual redesign, next role, and prototype limit.",
    },
    5: {
        "TOPIC": "Engineering Synthesis",
        "OBJECTIVE": "Students will identify a pattern in test evidence, transfer the design cycle, and explain a realistic engineering next step.",
        "TEKS": "d(1)(C)",
        "DOL": "Rover transfer note + individual weekly portfolio.",
        "I_CAN": "transfer the design cycle to a fictional rover brief and explain a realistic engineering next step.",
        "SHOW": "Complete the FYF rover transfer note and submit the private formative synthesis portfolio.",
    },
}


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    matches = [module for module in modules if module.get("name") == MODULE_NAME]
    if len(matches) > 1:
        raise RuntimeError(f"Duplicate Canvas modules named {MODULE_NAME!r}: {[entry['id'] for entry in matches]}")
    found = matches[0] if matches else None
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
            and (
                (kind == "SubHeader" and item.get("title") == title)
                or (kind == "Page" and item.get("page_url") == key)
                or (kind in ("Assignment", "Quiz") and item.get("content_id") == key)
            )
        ),
        None,
    )
    if found:
        return await common.api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{found['id']}",
            data={"module_item[title]": title, "module_item[published]": "false"},
        )
    data = {"module_item[type]": kind, "module_item[title]": title, "module_item[published]": "false"}
    if kind == "Page":
        data["module_item[page_url]"] = key
    elif kind in ("Assignment", "Quiz"):
        data["module_item[content_id]"] = key
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data=data)


QUESTIONS = [
    (
        "Q1 - PSAT 8/9 boundary",
        "Which statement stays within the current PSAT 8/9 evidence?",
        "A school or district may administer it in Grade 8 or 9, and its scores are not sent to colleges.",
        ["Every student takes it in Grade 9.", "It is a college-admission score.", "It automatically enters every student in National Merit."],
        "Correct. The local administration schedule still needs district verification.",
        "Do not turn a possible Grade 8 or 9 administration into a universal schedule or admissions claim.",
    ),
    (
        "Q2 - ACT science boundary",
        "Which statement is current for the enhanced ACT?",
        "The Composite uses English, math, and reading; science availability can vary by administration.",
        ["Science always determines the Composite.", "The ACT is the only assessment colleges may consider.", "A science score guarantees engineering admission."],
        "Correct. Institution, program, and scholarship policies must be checked for the student's cycle.",
        "ACT science is no longer a stable universal contrast with the SAT.",
    ),
    (
        "Q3 - TSIA2 boundary",
        "Which statement accurately describes TSIA2?",
        "It supports readiness and placement decisions for entering non-exempt students; exemptions and dual-credit rules must be verified.",
        ["Every Texas college student must take it with no exemptions.", "It is a national engineering license exam.", "One score guarantees college admission."],
        "Correct. The next step is checking the current authorized rule for the student's situation.",
        "Texas has exemptions and context-specific rules; do not present TSIA2 as universal with no exceptions.",
    ),
    (
        "Q4 - emerging evidence",
        "What makes the strongest claim that an engineering specialty is emerging or Bright Outlook?",
        "A named occupation, dated source, changing need or technology, and a stated evidence limitation.",
        ["A futuristic-sounding job title by itself.", "An unlabeled DFW salary guess.", "A social-media post with no occupation code."],
        "Correct. Transportation Engineers and Water/Wastewater Engineers are recognized O*NET specialties under Civil Engineers.",
        "The judgment needs a sourceable occupation and a reason the evidence could change.",
    ),
]


async def upsert_quiz(client):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    matches = [
        quiz for quiz in quizzes if quiz.get("title") == QUIZ_TITLE or quiz.get("title") in QUIZ_ALIASES
    ]
    if len(matches) > 1:
        raise RuntimeError(f"Duplicate current/legacy Week 2 practice quizzes: {[entry['id'] for entry in matches]}")
    found = matches[0] if matches else None
    data = {
        "quiz[title]": QUIZ_TITLE,
        "quiz[description]": "<p>Ungraded, unlimited-retry practice. Use the feedback to repair assessment-impact and emerging-work claims.</p>",
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
    for prior_question in existing:
        if prior_question.get("question_name") not in desired_names:
            await common.api(
                client,
                "DELETE",
                f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior_question['id']}",
            )
    existing = [question for question in existing if question.get("question_name") in desired_names]
    unique = []
    seen_names = set()
    for prior_question in existing:
        name = prior_question.get("question_name")
        if name in seen_names:
            await common.api(
                client,
                "DELETE",
                f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior_question['id']}",
            )
        else:
            seen_names.add(name)
            unique.append(prior_question)
    existing = unique
    for position, (name, prompt, correct, wrong, yes, no) in enumerate(QUESTIONS, 1):
        prior_question = next((question for question in existing if question.get("question_name") == name), None)
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
            f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior_question['id']}"
            if prior_question
            else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        )
        await common.api(client, "PUT" if prior_question else "POST", path, json=payload)
    expected = [name for name, *_rest in QUESTIONS]
    final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    final_by_name = {entry.get("question_name"): entry for entry in final_questions}
    if set(final_by_name) != set(expected) or len(final_questions) != len(expected):
        actual = [entry.get("question_name") for entry in final_questions]
        raise RuntimeError(f"Civil Engineering Quiz mismatch: expected {expected}, found {actual}")
    reorder_fields = []
    for name in expected:
        reorder_fields.extend(
            [("order[][id]", str(final_by_name[name]["id"])), ("order[][type]", "question")]
        )
    await common.api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/reorder",
        content=urlencode(reorder_fields),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    actual = [entry.get("question_name") for entry in final_questions]
    if actual != expected:
        raise RuntimeError(f"Civil Engineering Quiz mismatch: expected {expected}, found {actual}")
    final = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
    if final.get("published") or final.get("quiz_type") != "practice_quiz" or int(final.get("allowed_attempts") or 0) != -1:
        raise RuntimeError(f"Practice quiz invariant failed for {QUIZ_TITLE!r}")
    return final


async def require_minor_assignment(client, found, group, rubric_note, description, attachment_id):
    data = {
        "assignment[name]": ASSESSMENT_TITLE,
        "assignment[description]": description + rubric_note,
        "assignment[published]": "false",
        "assignment[points_possible]": "100",
        "assignment[grading_type]": "points",
        "assignment[assignment_group_id]": str(group["id"]),
        "assignment[omit_from_final_grade]": "false",
        "assignment[submission_types][]": ["student_annotation", "online_upload", "online_text_entry"],
        "assignment[annotatable_attachment_id]": str(attachment_id),
    }
    assignment = await common.api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{found['id']}",
        data=data,
    )
    if (
        assignment.get("published")
        or float(assignment.get("points_possible") or 0) != 100
        or assignment.get("grading_type") != "points"
        or assignment.get("assignment_group_id") != group["id"]
        or assignment.get("omit_from_final_grade") is not False
        or RUBRIC_NOTE_PATTERN.search(assignment.get("description") or "") is None
        or set(assignment.get("submission_types") or []) != {"student_annotation", "online_upload", "online_text_entry"}
    ):
        raise RuntimeError(f"Mapped Minor post-update invariant failed for {ASSESSMENT_TITLE!r}")
    await assert_annotation_files(client, ASSESSMENT_TITLE, assignment, attachment_id)
    return assignment


async def assert_annotation_files(client, title, assignment, attachment_id):
    source = await common.api(client, "GET", f"/files/{attachment_id}")
    clone_id = int(assignment.get("annotatable_attachment_id") or 0)
    clone = await common.api(client, "GET", f"/files/{clone_id}") if clone_id else {}
    if clone and not clone.get("locked"):
        clone = await common.api(client, "PUT", f"/files/{clone_id}", data={"locked": "true"})
    if (
        not clone_id
        or source.get("locked") is not True
        or clone.get("locked") is not True
        or clone.get("filename") != source.get("filename")
        or int(clone.get("size") or -1) != int(source.get("size") or -2)
    ):
        raise RuntimeError(f"Annotation attachment invariant failed for {title!r}")


async def upsert_practice_assignment(client, title, description, attachment_id):
    assignment = await common.upsert_assignment(
        client,
        title,
        description,
        ["student_annotation", "online_upload", "online_text_entry"],
        attachment_id,
    )
    if (
        assignment.get("published")
        or float(assignment.get("points_possible") or 0) != 0
        or assignment.get("grading_type") != "percent"
        or assignment.get("omit_from_final_grade") is not True
        or set(assignment.get("submission_types") or []) != {"student_annotation", "online_upload", "online_text_entry"}
    ):
        raise RuntimeError(f"Practice assignment invariant failed for {title!r}")
    await assert_annotation_files(client, title, assignment, attachment_id)
    return assignment


async def upsert_formative_assignment(client, description):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == PORTFOLIO_TITLE]
    if len(matches) > 1:
        raise RuntimeError(f"Duplicate formative assignments named {PORTFOLIO_TITLE!r}: {[entry['id'] for entry in matches]}")
    found = matches[0] if matches else None
    data = {
        "assignment[name]": PORTFOLIO_TITLE,
        "assignment[description]": description,
        "assignment[published]": "false",
        "assignment[points_possible]": "0",
        "assignment[grading_type]": "not_graded",
        "assignment[omit_from_final_grade]": "true",
        "assignment[submission_types][]": ["online_upload", "online_text_entry", "media_recording"],
    }
    endpoint = f"/courses/{COURSE_ID}/assignments/{found['id']}" if found else f"/courses/{COURSE_ID}/assignments"
    assignment = await common.api(client, "PUT" if found else "POST", endpoint, data=data)
    if (
        assignment.get("published")
        or float(assignment.get("points_possible") or 0) != 0
        or assignment.get("grading_type") != "not_graded"
        or assignment.get("omit_from_final_grade") is not True
        or set(assignment.get("submission_types") or []) != {"online_upload", "online_text_entry", "media_recording"}
    ):
        raise RuntimeError(f"Formative assignment invariant failed for {PORTFOLIO_TITLE!r}")
    return assignment


async def main():
    preflight()
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")

    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        assessment_preflight, minor_group, rubric_note = await canvas_preflight(client)
        module = await ensure_module(client)
        support_path = "course files/CCR Materials/5SW/Wk2"
        support_folder = await common.ensure_folder(client, support_path)
        files = {
            key: await upload_locked(client, ROOT / "docs/resources/worksheets" / name, support_path)
            for key, name in WORKSHEET_NAMES.items()
        }

        visual_files = {}
        visual_folders = {}
        for day, names in VISUAL_NAMES.items():
            folder_path = f"course files/CCR Materials/5SW/Wk2/Day {day} Visuals"
            visual_folders[day] = await common.ensure_folder(client, folder_path)
            for key, name in names:
                visual_files[key] = await upload_locked(client, ASSETS / f"day{day}" / name, folder_path)
        support_folder, support_file_count = await lock_folder_files(client, support_folder)
        visual_folder_counts = {}
        for day, folder in visual_folders.items():
            visual_folders[day], visual_folder_counts[day] = await lock_folder_files(client, folder)

        quiz = await upsert_quiz(client)
        assessment = await require_minor_assignment(
            client,
            assessment_preflight,
            minor_group,
            rubric_note,
            "<p>Submit the assessment-impact decision and two-specialty comparison by Canvas annotation, upload, typed labeled response, or paper. Use the student-visible 16-point rubric; bridge fabrication and team ranking are not part of this grade.</p>",
            files["ASSESS"]["id"],
        )
        systems = await upsert_practice_assignment(
            client,
            SYSTEMS_TITLE,
            "<p>Annotate or upload the fixed civil-engineering evidence and systems plan, type labeled responses, or use paper.</p>",
            files["CAREER"]["id"],
        )
        design = await upsert_practice_assignment(
            client,
            DESIGN_TITLE,
            "<p>Submit two bridge options with top and side views, critique, choice, and an individual career-role explanation.</p>",
            files["DESIGN"]["id"],
        )
        test = await upsert_practice_assignment(
            client,
            TEST_TITLE,
            "<p>Use the complete fixed dataset, then submit an individual failure analysis, redesign, next-role decision, and prototype limit. This module supplies no live-test kit or approved physical-test protocol.</p>",
            files["TEST"]["id"],
        )
        portfolio = await upsert_formative_assignment(
            client,
            "<p>Submit the private Civil Engineering Evidence Portfolio by upload, text, media recording, or paper. This is permanently formative: 0 points, not graded, and unpublished for teacher cloning.</p>",
        )

        urls = {
            "systems": f"/courses/{COURSE_ID}/assignments/{systems['id']}",
            "quiz": f"/courses/{COURSE_ID}/quizzes/{quiz['id']}",
            "assessment": f"/courses/{COURSE_ID}/assignments/{assessment['id']}",
            "design": f"/courses/{COURSE_ID}/assignments/{design['id']}",
            "test": f"/courses/{COURSE_ID}/assignments/{test['id']}",
            "portfolio": f"/courses/{COURSE_ID}/assignments/{portfolio['id']}",
        }
        link, step, flow = common.file_link, common.step, common.flow
        media = {
            1: prior.image_tag(visual_files["cluster"]["id"], "Find Your Future Engineering cluster opener")
            + prior.image_tag(visual_files["systems"]["id"], "Find Your Future systems-thinking kitchen scenario and existing floor plan")
            + prior.image_tag(visual_files["kitchen"]["id"], "Find Your Future cabinet-planning grid and discussion prompts"),
            2: "",
            3: "",
            4: "",
            5: prior.image_tag(visual_files["mars"]["id"], "Find Your Future fictional Mission to Mars design brief")
            + prior.image_tag(visual_files["rover"]["id"], "Find Your Future rover sketch and discussion directions"),
        }

        student = {
            1: {
                "TITLE": "Civil Engineering Careers and Systems",
                "PURPOSE": "Use fixed evidence to describe civil-engineering work and explain how one design choice affects a system.",
                "TODAY": "<ul><li>describe the Engineering cluster;</li><li>read one current career card;</li><li>distinguish high-school and postsecondary routes;</li><li>revise a kitchen system.</li></ul>",
                "READY": f'<p>Open your FYF workbook to p. 103 and pp. 174–175. Use <a href="{urls["systems"]}">the Canvas evidence activity</a> for the fixed career card and short response. {link(files["CAREER"]["id"], "The two-page companion")} is the paper, enlarged, or no-workbook route; do not complete both Canvas and paper.</p>',
                "LANGUAGE": "<p><strong>Word bank:</strong> system/sistema · evidence/evidencia · preparation/preparación · license/licencia · infrastructure/infraestructura.</p><p><strong>Use this frame:</strong> The source supports [evidence], but it does not prove [limit]. When I placed [choice], it affected [second element] because [reason].</p>",
                "STEPS": step(1, "Read the fixed career evidence", "<p><strong>Civil Engineer:</strong> plans, designs, and supervises infrastructure work; bachelor’s degree is typical; May 2024 U.S. median is $99,590; 2024–34 growth is 5% with about 23,600 openings/year. PE licensure is not universal for every entry-level role.</p>")
                + step(2, "Describe the cluster", "<p>Name two roles and the evidence they exchange.</p>")
                + step(3, "Use the pathway distinction", "<p>The public MacArthur label is Engineering; the 2026–27 IISD coursebook names Civil Engineering. Neither replaces a bachelor’s or license route.</p>")
                + step(4, "Complete FYF p. 175 once", "<p>Use the p. 174 appliance layout, add cabinets on the workbook grid, and explain one second element affected by your choice.</p>"),
                "EXIT": "<p>Describe one cluster problem, one career, and one accurate preparation requirement.</p>",
                "DONE": "<ul><li>evidence card;</li><li>cluster and role connection;</li><li>pathway boundary;</li><li>readable kitchen plan;</li><li>systems explanation.</li></ul>",
                "SUPPORT": "<p>Use the two-page companion, embedded FYF pages, enlarged print, typing, dictation, or teacher scribe. The p. 175 workbook grid remains the default drawing surface.</p>",
                "FALLBACK": "<p>The embedded visuals, fixed card, and companion are the full no-workbook route. H&amp;L, open search, and a partner are not required.</p>",
            },
            2: {
                "TITLE": "Assessment Impact and Emerging Work",
                "PURPOSE": "Explain one possible assessment impact and evaluate two recognized changing engineering specialties.",
                "TODAY": "<ul><li>read four current assessment cards;</li><li>write one verification question;</li><li>compare two O*NET specialties;</li><li>name a limitation.</li></ul>",
                "READY": f'<p>Open {link(files["ASSESS"]["id"], "the three-page assessment and specialty packet")} and {link(files["RUBRIC"]["id"], "the student-visible Minor 2 rubric")}.</p>',
                "LANGUAGE": "<p><strong>Word bank:</strong> assessment/evaluación · exemption/exención · placement/colocación · specialty/especialidad · limitation/limitación.</p><p><strong>Use this frame:</strong> This result may affect [goal] because [reason]. It does not decide [boundary] by itself. I would verify [question] with [source].</p>",
                "STEPS": step(1, "Choose an assessment", "<p>Explain a possible effect on a goal and what the result does not decide by itself.</p><p><strong>Model:</strong> Taylor is exploring civil engineering. PSAT 8/9 may show a readiness area, but it does not decide admission or pathway access. Taylor would ask the counselor when and how the district uses the result.</p>")
                + step(2, "Verify next", "<p>Write one exact question and name the authorized source that should answer it.</p>")
                + step(3, "Compare specialties", "<p>Use Transportation Engineers and Water/Wastewater Engineers. Record work, driver, preparation context, and limitation.</p>")
                + step(4, "Submit once", f'<p><a href="{urls["assessment"]}">Submit Minor 2 privately</a>. Your packet or typed response is the demonstration of learning. Use <a href="{urls["quiz"]}">the retryable practice Quiz</a> only when your teacher assigns a quick repair or early-finish check; it is not extra graded evidence.</p>'),
                "EXIT": "<p>Point to the sentence that gives an assessment impact and boundary, then point to the specialty judgment and limitation. Revise either one if the evidence is missing.</p>",
                "DONE": "<ul><li>assessment decision;</li><li>verification question;</li><li>two-specialty comparison;</li><li>supported judgment;</li><li>limitation.</li></ul>",
                "SUPPORT": "<p>Read cards one row at a time. Use typing, speech-to-text, read-aloud, enlarged print, or the paper packet. Score evidence and reasoning, not English mechanics unless meaning is unclear.</p>",
                "FALLBACK": "<p>The dated cards replace live research. A blocked site or unknown future policy does not prevent completion.</p>",
            },
            3: {
                "TITLE": "Bridge Design — Two Options",
                "PURPOSE": "Create and compare two bridge concepts within one clear evidence boundary.",
                "TODAY": "<ul><li>read the constraints;</li><li>draw two top views;</li><li>draw two side views;</li><li>critique and choose.</li></ul>",
                "READY": f'<p>Open {link(files["DESIGN"]["id"], "the four-page bridge design packet")} or <a href="{urls["design"]}">the Canvas annotation activity</a>.</p>',
                "LANGUAGE": "<p><strong>Word bank:</strong> span/tramo · support/apoyo · member/elemento · load/carga · weak point/punto débil.</p><p><strong>Use this frame:</strong> I selected Option [A/B] because [evidence]. Next, a [role] would use [evidence] to produce [work product].</p>",
                "STEPS": step(1, "Read the boundary", "<p>This classroom prototype does not validate a real bridge.</p><p><strong>Two-option model:</strong> Option A uses two straight rails and a flat deck. Option B changes the side geometry to repeated triangular units while keeping the same span and load point. The meaningful change is geometry, not color.</p>")
                + step(2, "Draw Option A", "<p>Use the separate top and side fields. Label span, supports, members, joints, and load point.</p>")
                + step(3, "Draw Option B", "<p>Change a meaningful variable, not just color or decoration.</p>")
                + step(4, "Critique and choose", "<p>Cite one strength for each option, select one, and name the worker who owns the next step.</p>"),
                "EXIT": "<p>Name the next career role, required evidence, and expected work product.</p>",
                "DONE": "<ul><li>four readable views;</li><li>two predictions;</li><li>two evidence-based strengths;</li><li>supported choice;</li><li>career-role evidence.</li></ul>",
                "SUPPORT": "<p>Use enlarged grids, tactile pieces, a verbal description, typing, dictation, or a teacher scribe. Design reasoning, not drawing polish, is the evidence.</p>",
                "FALLBACK": "<p>No physical materials or team are required today. Drawing, typed description, enlarged grid, or dictation are accepted.</p>",
            },
            4: {
                "TITLE": "Fixed-Data Test and Redesign",
                "PURPOSE": "Use comparable evidence to identify a failure pattern and propose one specific redesign.",
                "TODAY": "<ul><li>predict from a fixed dataset;</li><li>compare standardized results;</li><li>analyze failure;</li><li>propose and justify a redesign.</li></ul>",
                "READY": f'<p>Open {link(files["TEST"]["id"], "the four-page fixed-data and redesign packet")} or <a href="{urls["test"]}">the Canvas annotation activity</a>.</p>',
                "LANGUAGE": "<p><strong>Word bank:</strong> stage/etapa · failure/falla · redesign/rediseño · variable/variable · prototype/prototipo.</p><p><strong>Use this frame:</strong> Sample [code] reached [result]. I would change [feature] because [evidence]. Next, a [role] would use [evidence] to produce [work product].</p>",
                "STEPS": step(1, "Predict before the reveal", "<p>Use the three fictional sample descriptions and cite one visible clue.</p>")
                + step(2, "Record comparable evidence", "<p>Reveal the same staged results and stop evidence for every sample. This module uses the fixed dataset and does not require a live test.</p>")
                + step(3, "Analyze failure", "<p>Name the result, evidence, and first failed or limited element.</p><p><strong>Model:</strong> Sample A completed Stage 2. The center deck reached the displacement mark before Stage 3, so the supported claim is that deck displacement limited this test. It does not prove one universal bridge rule.</p>")
                + step(4, "Redesign", "<p>Propose one specific change, why it should help, and what the next test should measure.</p>"),
                "EXIT": "<p>Name who reviews the evidence next and one limit of the classroom prototype.</p>",
                "DONE": "<ul><li>prediction;</li><li>comparable result;</li><li>failure evidence;</li><li>specific redesign;</li><li>career and limit explanation.</li></ul>",
                "SUPPORT": "<p>Use the same fixed data with read-aloud, enlarged print, typing, dictation, or teacher scribe. No fine-motor or fabrication skill is required.</p>",
                "FALLBACK": "<p>The fictional three-sample dataset is the complete route for every student. This module supplies no live-test kit or approved physical-test protocol.</p>",
            },
            5: {
                "TITLE": "Mars Transfer and Weekly Synthesis",
                "PURPOSE": "Transfer the design cycle to a fictional rover brief and synthesize the week's individual evidence.",
                "TODAY": "<ul><li>find a class result pattern;</li><li>design a fictional rover;</li><li>explain one tradeoff;</li><li>submit the private portfolio.</li></ul>",
                "READY": f'<p>Open your FYF workbook to pp. 106–107. Use {link(files["SYNTHESIS"]["id"], "the three-page synthesis companion")} for the evidence the workbook does not collect and {link(files["PORTFOLIO_RUBRIC"]["id"], "the one-page formative feedback guide")}. The companion is not a second rover drawing.</p>',
                "LANGUAGE": "<p><strong>Word bank:</strong> constraint/restricción · tradeoff/compensación · pattern/patrón · route/ruta · verify/verificar.</p><p><strong>Use this frame:</strong> Across the results, [pattern] appeared, except [exception]. The high-school pathway can help me [step], but I still need [postsecondary step].</p>",
                "STEPS": step(1, "Read anonymous results", "<p>State a pattern, exception, and the evidence—not a public team ranking.</p><p><strong>Model:</strong> Samples A and C stopped before the cap; Sample B reached the cap. Because the samples differ in more than one feature, the results do not prove that one shape caused the difference.</p>")
                + step(2, "Complete FYF p. 107 once", "<p>Label four rover needs and two constraints in the workbook design field. Treat the scenario as fictional, not current NASA reporting.</p>")
                + step(3, "Explain the cycle", "<p>Connect define, test, revise, and evidence across bridge and rover work.</p>")
                + step(4, "Submit the synthesis once", f'<p><a href="{urls["portfolio"]}">Submit the three-part synthesis companion</a>. Refer to the title, result, or sentence from your earlier Minor and bridge evidence. Do not re-upload the Day 2 Minor or the Day 3-4 packets.</p>'),
                "EXIT": "<p>Explain how the high-school pathway supports—but does not complete—the postsecondary route, then write one current verification question.</p>",
                "DONE": "<ul><li>result pattern and limitation;</li><li>rover design and tradeoff;</li><li>four-part synthesis;</li><li>pathway boundary;</li><li>private portfolio.</li></ul>",
                "SUPPORT": "<p>Use private text, audio, media recording, enlarged print, speech-to-text, or paper. The workbook holds the rover drawing; the companion holds the synthesis.</p>",
                "FALLBACK": "<p>The licensed images, adjacent text, fixed result set, and solo response are the full independent route. No public speaking or H&amp;L favorite is required.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Civil Engineering Careers and Systems",
                "SUBTITLE": "50 minutes · TEKS d(1)(B), d(1)(C), d(2)(A)",
                "ALERT": "<strong>Use the dated distinction.</strong> The current public MacArthur page says Engineering; the 2026–27 IISD coursebook names Civil Engineering. Neither label proves a completed postsecondary route.",
                "PREP": f'<ul><li><strong>Per student:</strong> one FYF workbook, pencil, and one Canvas-capable device for the private short response. Default companion prints: 0.</li><li><strong>Print only by route:</strong> one two-page {link(files["CAREER"]["id"], "evidence companion")} per no-workbook, enlarged, or paper-route student. Students use workbook + Canvas or one companion, not both.</li><li><strong>Teacher display:</strong> FYF pp. 103 and 174–175 plus this supplied model: <em>May 2024 | U.S. | median annual wage | BLS = $99,590. This is not a DFW starting salary or guarantee. Placing a cabinet beside the refrigerator may force a door-clearance change; the first choice affects a second element.</em></li><li><strong>Grouping and collection:</strong> independent evidence; pairs of two may rehearse the system explanation. Initial FYF p. 175 during the minute-40 lap. Collect one Canvas response or one companion and close devices.</li></ul>',
                "EVIDENCE": "<p>One route only: career evidence card, cluster/role connection, pathway boundary, readable FYF kitchen plan, and systems explanation. Formative.</p>",
                "FLOW": flow("#1f617a", "Cluster · 5", "One infrastructure problem.") + flow("#4a9d2f", "Career evidence · 15", "Work, preparation, pay, outlook, license boundary.") + flow("#5a2d91", "Pathway · 10", "Current district-source distinction.") + flow("#e3ad19", "Systems plan · 15", "Kitchen choice and second effect.") + flow("#1f617a", "Exit · 5", "Cluster, career, preparation."),
                "MONITOR": "<p><strong>Minute 12:</strong> students retain May 2024, U.S., median, and BLS with $99,590. If one-third label it local or starting pay, project the supplied source-label model and require a repaired label. <strong>Minute 28:</strong> each student has one career product and preparation fact plus the pathway boundary. <strong>Minute 42:</strong> FYF p. 175 shows a first placement, affected element, and reason. If students describe only appearance, ask, “What second element had to move or stay clear?” <strong>Safe trim:</strong> shorten the pathway share and partner rehearsal; protect the career/preparation evidence, p. 175 systems decision, and private exit. Bachelor’s is typical; PE licensure is not universal for every entry-level role.</p>",
                "RESOURCES": '<p><a href="https://www.bls.gov/ooh/architecture-and-engineering/civil-engineers.htm">BLS Civil Engineers</a> · <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte/macarthur-high-school">Irving ISD MacArthur CTE</a>. Licensed FYF pages remain inside Canvas.</p>',
                "SUPPORT": "<p>Read the card one field at a time. FYF p. 175 has the full-page drawing field; allow Canvas annotation, enlarged print, verbal planning, or dictation.</p>",
                "FALLBACK": "<p>No H&amp;L login, open search, or partner is required. The embedded visuals and fixed card are the full route.</p>",
            },
            2: {
                "TITLE": "Assessment Impact and Emerging Work",
                "SUBTITLE": "50 minutes · TEKS d(3)(E), d(1)(D)",
                "ALERT": "<strong>Do not memorize unstable policies.</strong> Students identify a possible impact, what must be verified, and where to verify it.",
                "PREP": f'<ul><li><strong>Per student:</strong> one Canvas-capable device and private access to {link(files["ASSESS"]["id"], "the three-page current-source packet")}; post {link(files["RUBRIC"]["id"], "the two-page Minor 2 rubric")} digitally. Default prints: 0.</li><li><strong>Paper route:</strong> one three-page packet per assigned student; print one rubric only if the student will mark it. Collect one individual Minor response, never a group submission.</li><li><strong>Project this supplied model:</strong> <em>Taylor is exploring civil engineering. PSAT 8/9 may show a readiness area, but it does not decide admission or pathway access. Taylor would ask the counselor when and how the district uses the result. Transportation engineering is changing with mobility data and resilience; O*NET marks it Bright Outlook, but BLS pay rolls up to Civil Engineers.</em></li><li>Keep the Quiz unpublished and use it only after Minor submission for a teacher-assigned repair/retry or early-finisher check.</li></ul>',
                "EVIDENCE": "<p><strong>Minor 2 in the 5SW assessment map:</strong> protected 100-point assessment impact decision, verification question, two-specialty comparison, judgment, and limitation. Bridge fabrication and the rover design are outside this grade.</p>",
                "FLOW": flow("#1f617a", "Boundaries · 5", "What a result can and cannot decide.") + flow("#4a9d2f", "Assessment cards · 12", "Four current bounded uses.") + flow("#5a2d91", "Decision · 10", "Goal impact and verification question.") + flow("#e3ad19", "Specialties · 18", "Compare, judge, limit.") + flow("#1f617a", "Submit or repair · 5", "Submit Minor 2; use the Quiz only for assigned repair/retry."),
                "MONITOR": "<p><strong>Minute 12:</strong> students can state one possible use and one boundary. If one-third write guarantees, reshow the Taylor model. <strong>Minute 25:</strong> the impact, boundary, exact question, and authorized source are present. <strong>Minute 39:</strong> both specialties have work, driver, preparation context, and limitation. <strong>Minute 46:</strong> the judgment cites a source detail. If a student lacks a current future policy, turn it into the verification question rather than inventing an answer. Safe trim: omit the optional Quiz and verbal share; protect every Minor rubric job and private submission. PSAT 8/9 scores are not sent to colleges; ACT Composite uses English, math, and reading; TSIA2 applies to entering non-exempt students.</p>",
                "RESOURCES": '<p><a href="https://counselors.collegeboard.org/assessments/psat-8-9/overview-dates">College Board PSAT 8/9</a> · <a href="https://www.act.org/content/act/en/products-and-services/the-act-educator/the-act-test/enhancements-k12.html">ACT enhancements</a> · <a href="https://www.highered.texas.gov/texas-success-initiative/">Texas Success Initiative</a> · <a href="https://www.onetonline.org/link/summary/17-2051.01">O*NET Transportation Engineers</a> · <a href="https://www.onetonline.org/link/summary/17-2051.02">O*NET Water/Wastewater Engineers</a></p>',
                "SUPPORT": "<p>Use sentence frames: This result may affect __ because __. It does not decide __ by itself. I would verify __ at __.</p>",
                "FALLBACK": "<p>All required evidence is in the packet. A site outage or uncertain future policy becomes a verification question, not a student penalty.</p>",
            },
            3: {
                "TITLE": "Bridge Design — Two Options",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>No build or live test is required.</strong> Students create two evidence options today and use the complete fixed dataset tomorrow.",
                "PREP": f'<ul><li><strong>Per student:</strong> one Canvas-capable device for annotation or one four-page {link(files["DESIGN"]["id"], "design packet")} printed landscape, plus pencil and ruler. Use one route only.</li><li><strong>Grouping:</strong> individual options and career-role response; pairs of two may give the brief critique. A student may use self-review or a teacher conference instead.</li><li><strong>Teacher display:</strong> project packet page 1 and the supplied model: Option A = two straight rails and flat deck; Option B = repeated triangular side units with the same span and load point. The meaningful changed variable is geometry, not decoration.</li><li>No physical materials, build station, or live research are required. Collect one annotation/upload or packet; close devices and stack rulers.</li></ul>',
                "EVIDENCE": "<p>Two top/side concepts, predictions, critique, choice, and individual career-role evidence. Formative.</p>",
                "FLOW": flow("#1f617a", "Shape notice · 5", "Geometry and connection behavior.") + flow("#4a9d2f", "Constraints · 10", "Span, supports, load, stop rule.") + flow("#5a2d91", "Compare systems · 10", "Beam, truss, arch boundaries.") + flow("#e3ad19", "Two options · 20", "Four views, critique, choice.") + flow("#1f617a", "Exit · 5", "Next worker and work product."),
                "MONITOR": "<p><strong>Minute 10:</strong> students can point to the 12-inch span, supports, and marked load point. <strong>Minute 25:</strong> Option A has top/side views, load path, and predicted weak point. <strong>Minute 38:</strong> Option B changes one meaningful system feature; if one-third changed only color, reshow the supplied model and circle the geometry difference. <strong>Minute 45:</strong> critique, supported choice, next role, needed evidence, and work product are present. Safe trim: accept clean labeled line diagrams and one concise strength per option; protect both distinct options, supported choice, and individual role response. Triangulation can stabilize an idealized frame, but it does not validate a classroom bridge.</p>",
                "RESOURCES": "<p>The CCE constraints are a classroom evidence model, not professional design guidance. Use only teacher-curated visuals; no 15-minute open-web bridge research.</p>",
                "SUPPORT": "<p>Each option has one landscape page with separate top and side fields. Accept enlarged grids, tactile pieces, verbal description, dictation, or a data/design role.</p>",
                "FALLBACK": "<p>No build, team, fine-motor performance, or public explanation is required for Day 3 evidence.</p>",
            },
            4: {
                "TITLE": "Fixed-Data Test and Redesign",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>Fixed data is the complete default.</strong> This module does not supply an approved physical test kit or live-test protocol. Do not improvise with textbooks, desks, scales, loose weights, or student load placement.",
                "PREP": f'<ul><li><strong>Per student:</strong> one Canvas-capable device for annotation or one four-page {link(files["TEST"]["id"], "fixed-data/redesign packet")}, plus pencil. Default physical materials: 0.</li><li><strong>Grouping:</strong> independent prediction, analysis, redesign, and role response. Pairs of two may rehearse one claim, but each student submits one route.</li><li>Project packet page 1, keep page 2 results hidden until minute 25, and display this supplied model after the reveal: <em>Sample A completed Stage 2; deck displacement before Stage 3 limited this test. A supported redesign strengthens or changes the deck and names the next measurement. The result does not prove a universal bridge rule.</em></li><li><strong>No live test from these directions:</strong> a future demonstration requires a separately approved exact bridge, material set, secured supports, labeled load stages and unit, safe cap, catch tray, marked keep-clear zone, tested timing, student observation roles, reset, and cleanup protocol. Pivot to the supplied data if any element is missing.</li></ul>',
                "EVIDENCE": "<p>Comparable result, failure evidence, specific redesign, next measure, career reviewer, and prototype limit. Formative.</p>",
                "FLOW": flow("#1f617a", "Predict · 5", "Visible clue before reveal.") + flow("#4a9d2f", "Inspect · 20", "Three fixed samples and variables.") + flow("#5a2d91", "Reveal · 10", "Comparable stages and stop evidence.") + flow("#e3ad19", "Redesign · 10", "One supported change and next measure.") + flow("#1f617a", "Exit · 5", "Reviewer and limit."),
                "MONITOR": "<p><strong>Minute 10:</strong> each prediction cites one visible clue without seeing the result. If one-third claim certainty, model “predicts” versus “proves.” <strong>Minute 25:</strong> reveal A = Stage 2/deck displacement; B = Stage 5 safe cap/no stop; C = Stage 3/support slip. <strong>Minute 35:</strong> each student has a fair comparison, uncontrolled variable, pattern, and exception. <strong>Minute 44:</strong> redesign names the exact result evidence and next measure; role response names a reviewer and real-world limit. Safe trim: shorten pair rehearsal and accept labeled bullets; protect result, redesign, measure, role, and limit. Collect one annotation/upload or packet and close devices. Do not rank students or samples as if the dataset validates one universal design.</p>",
                "RESOURCES": "<p>The fixed dataset is explicitly fictional classroom evidence. Strength-to-weight is not calculated unless every bridge mass is measured with a valid method; the default comparison is maximum completed standardized stage.</p>",
                "SUPPORT": "<p>Read the three sample rows aloud, reveal one result at a time, and collect individual analysis. Fabrication and fine-motor performance are not required.</p>",
                "FALLBACK": "<p>The fixed dataset is already the full route for class, absence, unavailable consumables, insufficient stations, or access needs.</p>",
            },
            5: {
                "TITLE": "Mars Transfer and Weekly Synthesis",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>Formative engineering portfolio.</strong> Use the bridge/design evidence for feedback and revision; it is not one of the two mapped 5SW majors. Keep the Assignment permanently at 0 points, not graded, and unpublished for teacher cloning.",
                "PREP": f'<ul><li><strong>Per student:</strong> one FYF workbook, pencil, and one device for the private formative submission. Post {link(files["SYNTHESIS"]["id"], "the three-page synthesis companion")} and {link(files["PORTFOLIO_RUBRIC"]["id"], "the one-page feedback guide")} digitally. Default prints: 0.</li><li><strong>Paper route:</strong> one three-page synthesis companion per assigned student; print the feedback guide only if the student will mark it. FYF p. 107 remains the only rover drawing surface.</li><li><strong>Teacher display:</strong> FYF pp. 106–107 and this supplied result model: <em>A and C stopped before the cap; B reached it. Because the samples differ in more than one feature, the evidence does not prove that one shape caused the difference.</em></li><li><strong>Grouping and collection:</strong> independent synthesis; pairs of two may rehearse the pattern. Students refer to earlier Minor/bridge evidence by title, result, or sentence and do not re-upload it. Collect one synthesis submission or paper companion.</li></ul>',
                "EVIDENCE": "<p>Result pattern/limit, fictional rover design/tradeoff, four-part synthesis, pathway boundary, and verification question.</p>",
                "FLOW": flow("#1f617a", "Pattern · 5", "Anonymous results, no ranking.") + flow("#4a9d2f", "FYF rover · 15", "Fictional design and constraints.") + flow("#5a2d91", "Synthesis · 20", "Career, assessment, specialty, redesign.") + flow("#e3ad19", "Pathway · 5", "Support and postsecondary boundary.") + flow("#1f617a", "Submit · 5", "Private evidence route."),
                "MONITOR": "<p><strong>Minute 8:</strong> pattern includes evidence and one exception/limit. If one-third claim causation, project the supplied result model. <strong>Minute 22:</strong> FYF p. 107 has four component needs, two constraints, and one tradeoff. <strong>Minute 36:</strong> each synthesis section points to an earlier fact or result without re-uploading prior work. <strong>Minute 45:</strong> pathway support, postsecondary boundary, and current verification question are present. Safe trim: accept labeled bullets and one strong sentence per synthesis section; do not remove career/preparation, assessment boundary, specialty evidence, bridge redesign, or pathway verification. If time ends, save the same companion for completion; do not create a second packet or grade the formative portfolio. Close devices after the private submission.</p>",
                "RESOURCES": "<p>Licensed FYF pages remain in authenticated Canvas. Current district-source labels are stated with dates and treated as a question to verify—not forced into a false DIRECT/STEPPING-STONE choice.</p>",
                "SUPPORT": "<p>Allow private text, audio, media recording, speech-to-text, enlarged print, or paper. FYF p. 107 provides the rover sketch field; the companion does not duplicate it.</p>",
                "FALLBACK": "<p>No team attendance, public speaking, physical bridge, H&amp;L favorite, Xello task, or eDynamic completion is required.</p>",
            },
        }

        day_names = {
            1: "Civil Engineering Careers and Systems",
            2: "Assessment Impact and Emerging Work",
            3: "Bridge Design — Two Options",
            4: "Fixed-Data Test and Redesign",
            5: "Mars Transfer and Weekly Synthesis",
        }
        extras = {
            1: ("Assignment", systems["id"], SYSTEMS_TITLE),
            2: ("Assignment", assessment["id"], ASSESSMENT_TITLE),
            3: ("Assignment", design["id"], DESIGN_TITLE),
            4: ("Assignment", test["id"], TEST_TITLE),
            5: ("Assignment", portfolio["id"], PORTFOLIO_TITLE),
        }
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            await upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header_title, header_title))
            student_title = f"STUDENT: 5SW Wk2 Day {day} - {day_names[day]}"
            student_page = await common.upsert_page(
                client,
                student_title,
                common.render(
                    "5sw-wk2-student.html",
                    {"COURSE_ID": COURSE_ID, "DAY": day, "MEDIA": media[day], **CONTRACTS[day], **student[day]},
                ),
            )
            teacher_title = f"TEACHER: 5SW Wk2 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(
                client,
                teacher_title,
                common.render(
                    "5sw-wk2-teacher.html",
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

        if len(order) != 21:
            raise RuntimeError(f"Week 2 module contract requires exactly 21 items; built {len(order)}")

        def matches_item(entry, kind, key):
            return entry.get("type") == kind and (
                (kind == "SubHeader" and entry.get("title") == key)
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
                data={
                    "module_item[position]": position,
                    "module_item[title]": title,
                    "module_item[published]": "false",
                },
            )

        final_items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        if len(final_items) != 21:
            raise RuntimeError(f"Expected 21 Week 2 module items; found {len(final_items)}")
        ordered_final = sorted(final_items, key=lambda entry: entry.get("position", 0))
        for position, ((kind, key, title), entry) in enumerate(zip(order, ordered_final), 1):
            if (
                entry.get("position") != position
                or not matches_item(entry, kind, key)
                or entry.get("title") != title
                or entry.get("published") is not False
            ):
                raise RuntimeError(f"Week 2 module order mismatch at position {position}")
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        if module.get("published"):
            raise RuntimeError("Week 2 module unexpectedly published")

        quiz = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
        if quiz.get("published") or quiz.get("quiz_type") != "practice_quiz" or int(quiz.get("allowed_attempts") or 0) != -1:
            raise RuntimeError(f"Final practice quiz invariant failed for {QUIZ_TITLE!r}")
        final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
        if [entry.get("question_name") for entry in final_questions] != [name for name, *_rest in QUESTIONS]:
            raise RuntimeError(f"Final practice quiz question order failed for {QUIZ_TITLE!r}")

        systems = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{systems['id']}")
        assessment = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assessment['id']}")
        design = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{design['id']}")
        test = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{test['id']}")
        portfolio = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{portfolio['id']}")
        for title, assignment, source in (
            (SYSTEMS_TITLE, systems, files["CAREER"]),
            (DESIGN_TITLE, design, files["DESIGN"]),
            (TEST_TITLE, test, files["TEST"]),
        ):
            if (
                assignment.get("published")
                or float(assignment.get("points_possible") or 0) != 0
                or assignment.get("grading_type") != "percent"
                or assignment.get("omit_from_final_grade") is not True
                or set(assignment.get("submission_types") or []) != {"student_annotation", "online_upload", "online_text_entry"}
            ):
                raise RuntimeError(f"Final practice assignment invariant failed for {title!r}")
            await assert_annotation_files(client, title, assignment, source["id"])
        if (
            assessment.get("published")
            or float(assessment.get("points_possible") or 0) != 100
            or assessment.get("grading_type") != "points"
            or assessment.get("assignment_group_id") != minor_group["id"]
            or assessment.get("omit_from_final_grade") is not False
            or RUBRIC_NOTE_PATTERN.search(assessment.get("description") or "") is None
            or set(assessment.get("submission_types") or []) != {"student_annotation", "online_upload", "online_text_entry"}
        ):
            raise RuntimeError(f"Final mapped Minor invariant failed for {ASSESSMENT_TITLE!r}")
        await assert_annotation_files(client, ASSESSMENT_TITLE, assessment, files["ASSESS"]["id"])
        if (
            portfolio.get("published")
            or float(portfolio.get("points_possible") or 0) != 0
            or portfolio.get("grading_type") != "not_graded"
            or portfolio.get("omit_from_final_grade") is not True
            or set(portfolio.get("submission_types") or []) != {"online_upload", "online_text_entry", "media_recording"}
        ):
            raise RuntimeError(f"Final formative assignment invariant failed for {PORTFOLIO_TITLE!r}")

        for day, pair in pages.items():
            for kind, value in pair.items():
                page = await common.api(client, "GET", f"/courses/{COURSE_ID}/pages/{value['url']}")
                if page.get("published"):
                    raise RuntimeError(f"Published Week 2 {kind} page on Day {day}")
        support_folder, support_file_count = await lock_folder_files(client, support_folder)
        for day, folder in visual_folders.items():
            visual_folders[day], visual_folder_counts[day] = await lock_folder_files(client, folder)

        print(
            json.dumps(
                {
                    "module": {"id": module["id"], "published": module["published"]},
                    "quiz": {"id": quiz["id"], "published": quiz.get("published"), "allowed_attempts": quiz.get("allowed_attempts")},
                    "assignments": {
                        "systems": {"id": systems["id"], "published": systems.get("published"), "submission_types": systems.get("submission_types")},
                        "assessment": {"id": assessment["id"], "published": assessment.get("published"), "submission_types": assessment.get("submission_types")},
                        "design": {"id": design["id"], "published": design.get("published"), "submission_types": design.get("submission_types")},
                        "test": {"id": test["id"], "published": test.get("published"), "submission_types": test.get("submission_types")},
                        "portfolio": {"id": portfolio["id"], "published": portfolio.get("published"), "submission_types": portfolio.get("submission_types")},
                    },
                    "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"], "files": support_file_count},
                    "visual_folders": {
                        str(day): {"id": folder["id"], "locked": folder["locked"], "files": visual_folder_counts[day]}
                        for day, folder in visual_folders.items()
                    },
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
