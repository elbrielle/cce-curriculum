"""Build the unpublished 4SW Week 2 counseling-ready course-planning module."""

import asyncio
import json
import re
import sys
from urllib.parse import urlencode

import httpx

import build_4sw_wk1 as common


BASE = common.BASE
COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/4sw/wk2"
MODULE_NAME = "4SW Wk2: Build a Counseling-Ready High School Plan"
QUIZ_TITLE = "PRACTICE: What Does This Assessment Affect?"
ANNOTATION_TITLE = "DRAFT: Four-Year Course Plan Annotation"
PLAN_TITLE = "MAJOR 2: Individual High School and Career Plan"
MAJOR_GROUP = "Major Assessments (60%)"
TEMPLATES = ROOT / "build/canvas/templates"


def preflight():
    worksheet_names = (
        "4sw-wk2-transition-and-assessment-decisions.pdf",
        "4sw-wk2-four-year-course-plan-draft.pdf",
        "4sw-wk2-college-credit-and-family-conversation.pdf",
        "4sw-wk2-smart-experience-action-plan.pdf",
        "4sw-wk2-individual-high-school-career-plan.pdf",
        "4sw-wk2-high-school-career-plan-rubric.pdf",
    )
    visual_names = {
        2: ("fyf-rung7-classes-to-consider.jpg", "fyf-rung7-plan-in-action.jpg"),
        4: ("fyf-rung6-smart-goals.jpg", "fyf-rung6-goal-check.jpg"),
        5: ("fyf-rung7-opportunities.jpg",),
    }
    required = [
        TEMPLATES / "4sw-wk2-student.html",
        TEMPLATES / "4sw-wk2-teacher.html",
        *(ROOT / "docs/resources/worksheets" / name for name in worksheet_names),
        *(
            ASSETS / f"day{day}" / name
            for day, names in visual_names.items()
            for name in names
        ),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"4SW Wk2 preflight missing required files: {missing}")


async def canvas_preflight(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    module_matches = [entry for entry in modules if entry.get("name") == MODULE_NAME]
    if len(module_matches) > 1:
        raise RuntimeError(
            f"Duplicate Canvas modules named {MODULE_NAME!r}: "
            f"{[entry['id'] for entry in module_matches]}"
        )

    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    major_groups = [entry for entry in groups if entry.get("name") == MAJOR_GROUP]
    if len(major_groups) != 1:
        raise RuntimeError(
            f"Expected exactly one {MAJOR_GROUP!r} group; found {len(major_groups)}"
        )

    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    plan_matches = [entry for entry in assignments if entry.get("name") == PLAN_TITLE]
    if len(plan_matches) != 1:
        raise RuntimeError(
            f"Expected one existing mapped Major assignment named {PLAN_TITLE!r}; "
            f"found {len(plan_matches)}"
        )
    plan = plan_matches[0]
    rubric_note = re.search(
        r'<div data-cce-rubric-note="cce-advisory-rubric-v1".*?</div>',
        plan.get("description") or "",
        flags=re.I | re.S,
    )
    if (
        plan.get("published")
        or float(plan.get("points_possible") or 0) != 100
        or plan.get("grading_type") != "points"
        or plan.get("assignment_group_id") != major_groups[0].get("id")
        or plan.get("omit_from_final_grade") is not False
        or rubric_note is None
    ):
        raise RuntimeError(
            f"Mapped Major preflight failed for {PLAN_TITLE!r}: "
            f"published={plan.get('published')}, points={plan.get('points_possible')}, "
            f"grading={plan.get('grading_type')}, group={plan.get('assignment_group_id')}, "
            f"omit={plan.get('omit_from_final_grade')}"
        )

    annotation_matches = [
        entry for entry in assignments if entry.get("name") == ANNOTATION_TITLE
    ]
    if len(annotation_matches) > 1:
        raise RuntimeError(
            f"Duplicate assignments named {ANNOTATION_TITLE!r}: "
            f"{[entry['id'] for entry in annotation_matches]}"
        )
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    quiz_matches = [entry for entry in quizzes if entry.get("title") == QUIZ_TITLE]
    if len(quiz_matches) > 1:
        raise RuntimeError(
            f"Duplicate quizzes named {QUIZ_TITLE!r}: "
            f"{[entry['id'] for entry in quiz_matches]}"
        )
    return {
        "plan": plan,
        "major_group": major_groups[0],
        "rubric_note": rubric_note.group(0),
    }


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    matches = [entry for entry in modules if entry.get("name") == MODULE_NAME]
    if len(matches) > 1:
        raise RuntimeError(
            f"Duplicate Canvas modules named {MODULE_NAME!r}: "
            f"{[entry['id'] for entry in matches]}"
        )
    found = matches[0] if matches else None
    data = {"module[published]": "false"}
    if found:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data=data)
    data["module[name]"] = MODULE_NAME
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


async def upload_locked(client, path, folder_path):
    uploaded = await common.upload(client, path, folder_path)
    record = await common.api(
        client, "GET", f"/files/{uploaded['id']}"
    )
    if not record.get("locked"):
        record = await common.api(
            client, "PUT", f"/files/{uploaded['id']}", data={"locked": "true"}
        )
    if not record.get("locked"):
        raise RuntimeError(f"Canvas did not lock uploaded file {path.name!r}")
    return record


async def lock_folder_files(client, folder):
    current = await common.api(client, "GET", f"/folders/{folder['id']}")
    if not current.get("locked"):
        current = await common.api(
            client, "PUT", f"/folders/{folder['id']}", data={"locked": "true"}
        )
    if not current.get("locked"):
        raise RuntimeError(f"Canvas did not lock folder {folder['id']}")
    for entry in await common.paged(client, f"/folders/{folder['id']}/files"):
        if not entry.get("locked"):
            await common.api(
                client, "PUT", f"/files/{entry['id']}", data={"locked": "true"}
            )
    final = await common.paged(client, f"/folders/{folder['id']}/files")
    unlocked = [
        entry.get("display_name") or entry.get("filename")
        for entry in final
        if not entry.get("locked")
    ]
    if unlocked:
        raise RuntimeError(f"Unlocked files remain in folder {folder['id']}: {unlocked}")
    return current, len(final)


QUESTIONS = [
    (
        "Q1 - End-of-course assessment",
        "Which assessment result is most directly connected to Texas high school graduation requirements?",
        "A required STAAR End-of-Course assessment, subject to current state rules and approved alternatives.",
        ["The PSAT only.", "Any industry certification exam.", "The ASVAB only."],
        "Correct. End-of-Course requirements are part of the Texas graduation framework.",
        "PSAT, ASVAB, and industry certifications serve different purposes. Check current TEA graduation rules.",
    ),
    (
        "Q2 - College placement",
        "A student has been admitted to a Texas college but needs to know whether they can begin in college-level reading and math. What should the student verify?",
        "The institution's current college-readiness and placement rules, including TSIA exemptions or alternatives.",
        ["Only the ASVAB score.", "Only the student's industry certification.", "Whether the student passed an AP art course."],
        "Correct. TSIA and approved exemptions or alternatives can affect placement, not every student's admission decision.",
        "Admission, placement, military qualification, and credentialing are different decisions.",
    ),
    (
        "Q3 - Military options",
        "Which assessment can support career exploration and may affect military qualification and job options during an enlistment process?",
        "ASVAB",
        ["TSIA", "AP exam", "STAAR English I EOC only"],
        "Correct. The ASVAB has a distinct career-exploration and military role.",
        "The other assessments do not replace the ASVAB in an enlistment process.",
    ),
    (
        "Q4 - Industry certification",
        "What is the safest planning claim about an industry certification assessment?",
        "It measures requirements for a specific credential and does not replace every college or graduation assessment.",
        ["It is a universal college entrance exam.", "It guarantees a job in the field.", "Every CTE student takes the same certification."],
        "Correct. Keep the credential name, eligibility, and current requirements attached to the claim.",
        "A certification is specific. It does not guarantee employment or replace unrelated assessments.",
    ),
]


async def upsert_quiz(client):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    matches = [entry for entry in quizzes if entry.get("title") == QUIZ_TITLE]
    if len(matches) > 1:
        raise RuntimeError(
            f"Duplicate quizzes named {QUIZ_TITLE!r}: {[entry['id'] for entry in matches]}"
        )
    quiz = matches[0] if matches else None
    data = {
        "quiz[title]": QUIZ_TITLE,
        "quiz[description]": "<p>Ungraded practice. Retry and use the feedback to separate graduation, admission, placement, career-exploration, military, and credential decisions.</p>",
        "quiz[quiz_type]": "practice_quiz",
        "quiz[published]": "false",
        "quiz[allowed_attempts]": "-1",
        "quiz[show_correct_answers]": "true",
        "quiz[shuffle_answers]": "false",
    }
    path = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}" if quiz else f"/courses/{COURSE_ID}/quizzes"
    quiz = await common.api(client, "PUT" if quiz else "POST", path, data=data)
    existing = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    expected_names = [spec[0] for spec in QUESTIONS]
    seen = set()
    for question in existing:
        name = question.get("question_name")
        if name not in expected_names or name in seen:
            await common.api(
                client,
                "DELETE",
                f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{question['id']}",
            )
        else:
            seen.add(name)
    existing = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    for position, (name, text, correct, wrong, correct_comment, incorrect_comment) in enumerate(QUESTIONS, 1):
        found = next((entry for entry in existing if entry.get("question_name") == name), None)
        payload = {
            "question": {
                "question_name": name,
                "question_text": text,
                "question_type": "multiple_choice_question",
                "position": position,
                "points_possible": 1,
                "correct_comments": correct_comment,
                "incorrect_comments": incorrect_comment,
                "answers": [{"answer_text": correct, "answer_weight": 100}]
                + [{"answer_text": answer, "answer_weight": 0} for answer in wrong],
            }
        }
        question_path = (
            f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{found['id']}"
            if found
            else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        )
        await common.api(client, "PUT" if found else "POST", question_path, json=payload)
    final_questions = await common.paged(
        client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
    )
    by_name = {entry.get("question_name"): entry for entry in final_questions}
    if set(by_name) != set(expected_names) or len(final_questions) != len(expected_names):
        raise RuntimeError(
            f"Quiz {quiz['id']} question mismatch: "
            f"{[entry.get('question_name') for entry in final_questions]}"
        )
    fields = []
    for name in expected_names:
        fields.extend(
            [("order[][id]", str(by_name[name]["id"])), ("order[][type]", "question")]
        )
    await common.api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/reorder",
        content=urlencode(fields),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    ordered = await common.paged(
        client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
    )
    actual_order = [entry.get("question_name") for entry in ordered]
    if actual_order != expected_names:
        raise RuntimeError(
            f"Quiz {quiz['id']} order mismatch: expected {expected_names}, found {actual_order}"
        )
    final = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
    if (
        final.get("published")
        or final.get("quiz_type") != "practice_quiz"
        or int(final.get("allowed_attempts") or 0) != -1
    ):
        raise RuntimeError(
            f"Practice quiz invariant failed: published={final.get('published')}, "
            f"type={final.get('quiz_type')}, attempts={final.get('allowed_attempts')}"
        )
    return final


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
            data={"module_item[title]": title, "module_item[published]": "false"},
        )
    data = {
        "module_item[type]": kind,
        "module_item[title]": title,
        "module_item[published]": "false",
    }
    if kind == "Page":
        data["module_item[page_url]"] = key
    elif kind in ("Assignment", "Quiz"):
        data["module_item[content_id]"] = key
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data=data)


async def upsert_annotation(client, description, attachment_id):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == ANNOTATION_TITLE]
    if len(matches) > 1:
        raise RuntimeError(
            f"Duplicate assignments named {ANNOTATION_TITLE!r}: "
            f"{[entry['id'] for entry in matches]}"
        )
    found = matches[0] if matches else None
    data = {
        "assignment[name]": ANNOTATION_TITLE,
        "assignment[description]": description,
        "assignment[submission_types][]": [
            "student_annotation",
            "online_upload",
            "online_text_entry",
        ],
        "assignment[annotatable_attachment_id]": str(attachment_id),
        "assignment[grading_type]": "percent",
        "assignment[points_possible]": "0",
        "assignment[omit_from_final_grade]": "true",
        "assignment[published]": "false",
    }
    assignment = await common.api(
        client,
        "PUT" if found else "POST",
        (
            f"/courses/{COURSE_ID}/assignments/{found['id']}"
            if found
            else f"/courses/{COURSE_ID}/assignments"
        ),
        data=data,
    )
    assignment = await common.api(
        client,
        "GET",
        f"/courses/{COURSE_ID}/assignments/{assignment['id']}",
    )
    source_file = await common.api(client, "GET", f"/files/{attachment_id}")
    annotation_attachment_id = int(
        assignment.get("annotatable_attachment_id") or 0
    )
    annotation_file = (
        await common.api(client, "GET", f"/files/{annotation_attachment_id}")
        if annotation_attachment_id
        else {}
    )
    if annotation_file and not annotation_file.get("locked"):
        annotation_file = await common.api(
            client,
            "PUT",
            f"/files/{annotation_attachment_id}",
            data={"locked": "true"},
        )
    failures = {
        "published": assignment.get("published") is not False,
        "points_possible": float(assignment.get("points_possible") or 0) != 0,
        "grading_type": assignment.get("grading_type") != "percent",
        "omit_from_final_grade": assignment.get("omit_from_final_grade") is not True,
        "annotatable_attachment_missing": not annotation_attachment_id,
        "source_file_locked": source_file.get("locked") is not True,
        "annotation_file_locked": annotation_file.get("locked") is not True,
        "annotation_filename": annotation_file.get("filename")
        != source_file.get("filename"),
        "annotation_size": int(annotation_file.get("size") or -1)
        != int(source_file.get("size") or -2),
    }
    failed = [name for name, value in failures.items() if value]
    if failed:
        raise RuntimeError(
            f"Annotation invariant failed ({', '.join(failed)}): "
            f"published={assignment.get('published')}, "
            f"points={assignment.get('points_possible')}, grading={assignment.get('grading_type')}, "
            f"omit={assignment.get('omit_from_final_grade')}, "
            f"source_file={attachment_id}, attachment={annotation_attachment_id}, "
            f"source_name={source_file.get('filename')!r}, "
            f"attachment_name={annotation_file.get('filename')!r}, "
            f"source_size={source_file.get('size')}, "
            f"attachment_size={annotation_file.get('size')}"
        )
    return assignment


async def update_major_assignment(client, plan_id, group_id, description):
    updated = await common.api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{plan_id}",
        data={
            "assignment[name]": PLAN_TITLE,
            "assignment[description]": description,
            "assignment[submission_types][]": [
                "online_upload",
                "online_text_entry",
                "media_recording",
            ],
            "assignment[points_possible]": "100",
            "assignment[grading_type]": "points",
            "assignment[assignment_group_id]": str(group_id),
            "assignment[omit_from_final_grade]": "false",
            "assignment[published]": "false",
        },
    )
    if (
        updated.get("published")
        or float(updated.get("points_possible") or 0) != 100
        or updated.get("grading_type") != "points"
        or updated.get("assignment_group_id") != group_id
        or updated.get("omit_from_final_grade") is not False
        or 'data-cce-rubric-note="cce-advisory-rubric-v1"'
        not in (updated.get("description") or "")
    ):
        raise RuntimeError(
            f"Mapped Major invariant failed for {PLAN_TITLE!r}: "
            f"published={updated.get('published')}, points={updated.get('points_possible')}, "
            f"grading={updated.get('grading_type')}, group={updated.get('assignment_group_id')}, "
            f"omit={updated.get('omit_from_final_grade')}"
        )
    return updated


def image_tag(file_id, alt):
    return (
        f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" '
        'style="display:block;width:100%;max-width:700px;height:auto;margin:14px auto;border:1px solid #ddd" '
        f'data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'
    )


def matches_item(item, kind, key):
    if item.get("type") != kind:
        return False
    if kind == "SubHeader":
        return item.get("title") == key
    if kind == "Page":
        return item.get("page_url") == key
    if kind in ("Assignment", "Quiz"):
        return item.get("content_id") == key
    return False


async def main():
    preflight()
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        state = await canvas_preflight(client)
        module = await ensure_module(client)
        support_path = "course files/CCR Materials/4SW/Wk2"
        support_folder = await common.ensure_folder(client, support_path)
        worksheet_names = {
            "TRANSITION": "4sw-wk2-transition-and-assessment-decisions.pdf",
            "COURSE": "4sw-wk2-four-year-course-plan-draft.pdf",
            "CREDIT": "4sw-wk2-college-credit-and-family-conversation.pdf",
            "SMART": "4sw-wk2-smart-experience-action-plan.pdf",
            "PLAN": "4sw-wk2-individual-high-school-career-plan.pdf",
            "RUBRIC": "4sw-wk2-high-school-career-plan-rubric.pdf",
        }
        files = {
            key: await upload_locked(client, ROOT / "docs/resources/worksheets" / name, support_path)
            for key, name in worksheet_names.items()
        }

        selected = {
            2: ["fyf-rung7-classes-to-consider.jpg", "fyf-rung7-plan-in-action.jpg"],
            4: ["fyf-rung6-smart-goals.jpg", "fyf-rung6-goal-check.jpg"],
            5: ["fyf-rung7-opportunities.jpg"],
        }
        visuals, visual_folders = {}, {}
        for day, names in selected.items():
            folder_path = f"course files/CCR Materials/4SW/Wk2/Day {day} Visuals"
            visual_folders[day] = await common.ensure_folder(client, folder_path)
            visuals[day] = {
                name: await upload_locked(client, ASSETS / f"day{day}" / name, folder_path)
                for name in names
            }

        support_folder, support_file_count = await lock_folder_files(
            client, support_folder
        )
        visual_file_counts = {}
        for day, folder in visual_folders.items():
            visual_folders[day], visual_file_counts[day] = await lock_folder_files(
                client, folder
            )

        quiz = await upsert_quiz(client)
        annotation = await upsert_annotation(
            client,
            "<p>Complete the counseling-ready four-year draft by Canvas annotation, file upload, text entry, or paper. Do not submit official course requests. Mark uncertain entries for counselor verification.</p>",
            files["COURSE"]["id"],
        )
        plan_description = f'<p>Submit only the completed four-page Individual High School and Career Plan by file upload, typed response, or approved audio response. Days 1-4 are evidence-building checkpoints, not four additional required uploads. Use the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">student scoring guide</a> before submitting. This assignment is mapped as a 100-point Major Assessment and remains unpublished for teacher review and cloning.</p>{state["rubric_note"]}'
        plan_assignment = await update_major_assignment(
            client,
            state["plan"]["id"],
            state["major_group"]["id"],
            plan_description,
        )
        quiz_url = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        annotation_url = f"/courses/{COURSE_ID}/assignments/{annotation['id']}"
        plan_url = f"/courses/{COURSE_ID}/assignments/{plan_assignment['id']}"

        media = {
            1: "",
            2: image_tag(
                visuals[2]["fyf-rung7-classes-to-consider.jpg"]["id"],
                "Find Your Future Rung 7 blank table for classes and how each class may support a goal",
            )
            + image_tag(
                visuals[2]["fyf-rung7-plan-in-action.jpg"]["id"],
                "Find Your Future Rung 7 prompts for local opportunities and actions during high school",
            ),
            3: "",
            4: image_tag(
                visuals[4]["fyf-rung6-smart-goals.jpg"]["id"],
                "Find Your Future Rung 6 SMART goal definitions and short-term goal form",
            )
            + image_tag(
                visuals[4]["fyf-rung6-goal-check.jpg"]["id"],
                "Find Your Future Rung 6 medium-term and long-term goal forms with realism and challenge check",
            ),
            5: image_tag(
                visuals[5]["fyf-rung7-opportunities.jpg"]["id"],
                "Find Your Future Rung 7 tables for clubs, organizations, activities, programs, and opportunities",
            ),
        }

        contracts = {
            1: {
                "TOPIC": "Academic Transitions",
                "OBJECTIVE": "Students will describe the current Texas graduation framework and analyze how different assessments can affect graduation, placement, admission, scholarships, career exploration, or military options.",
                "TEKS": "d(3)(A), d(3)(E)",
                "DOL": "Completed High School Transition and Assessment Decisions packet.",
                "I_CAN": "explain how graduation rules and different assessments affect different planning decisions.",
                "SHOW": "complete the Transition and Assessment Decisions packet and use evidence to correct a mixed-up assessment claim.",
            },
            2: {
                "TOPIC": "Course Planning",
                "OBJECTIVE": "Students will use current Irving ISD course descriptions to draft a four-year sequence, explain one prerequisite chain, and identify questions that require counselor confirmation.",
                "TEKS": "d(8)(B), d(3)(A)",
                "DOL": "Counseling-Ready Four-Year Course Plan Draft in Canvas annotation or the three-page paper route.",
                "I_CAN": "build a four-year course-plan draft without turning an unknown into a fact.",
                "SHOW": "complete one source-checked course plan with a prerequisite chain, verification label, backup, and counseling questions.",
            },
            3: {
                "TOPIC": "College Credit",
                "OBJECTIVE": "Students will compare AP and dual credit using current sources, document one option and its limitation, and explain the developing plan through a family, trusted-adult, counselor, teacher, or private reflection route.",
                "TEKS": "d(3)(B), d(3)(D)",
                "DOL": "Completed College Credit and Plan Check.",
                "I_CAN": "compare AP and dual credit and name what I still need to verify before using either option in my plan.",
                "SHOW": "complete the College Credit and Plan Check with one current option, one limitation, and one keep, change, or verify decision.",
            },
            4: {
                "TOPIC": "Extended Learning",
                "OBJECTIVE": "Students will evaluate one experience that could support a career direction and write a SMART action plan with an access check, support, obstacle, and backup strategy.",
                "TEKS": "d(3)(F), d(8)(C)",
                "DOL": "FYF SMART goal plus the Experience Access and Backup Check.",
                "I_CAN": "turn one useful experience into a realistic SMART goal with an access check and backup.",
                "SHOW": "complete the FYF SMART goal and one-page access, skill-transfer, support, obstacle, backup, and seven-day action check.",
            },
            5: {
                "TOPIC": "Course Planning",
                "OBJECTIVE": "Students will synthesize self-evidence, current course and preparation evidence, one advanced or college-credit option, and an action and revision plan into one individual high school and career plan.",
                "TEKS": "d(8)(B), d(8)(C), d(3)(D)",
                "DOL": "Individual High School and Career Plan with student-visible 16-point rubric.",
                "I_CAN": "use self, course, preparation, and action evidence to build a plan that can change when the evidence changes.",
                "SHOW": "submit one private Individual High School and Career Plan after a rubric check and visible revision.",
            },
        }

        file_link = common.file_link
        step = common.step
        flow = common.flow
        student = {
            1: {
                "TITLE": "Graduation and Assessment Decisions",
                "PURPOSE": "Separate graduation, admission, placement, career-exploration, military, and credential decisions before you plan.",
                "TODAY": "<ul><li>read the current Texas graduation framework;</li><li>identify one endorsement question;</li><li>analyze two assessment scenarios.</li></ul>",
                "READY": f'<p>Use one printed copy of {file_link(files["TRANSITION"]["id"], "the three-page Transition and Assessment Decisions packet")}. Page 1 already contains the dated Grade 8 cohort facts. Keep the packet in your CCR Week 2 folder for Day 5.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Decision words:</strong> graduation · admission · placement · scholarship · career exploration · military qualification · credential.</p><p><strong>Use this frame:</strong> ___ may affect ___, but it does not decide ___. I will verify ___ with ___.</p></div>',
                "STEPS": step(1, "Record the two planning levels", "<p>Write the 22-credit foundation baseline and what the 26-credit endorsement plan adds. Keep the source and year.</p>")
                + step(2, "Write a counseling-ready endorsement statement", "<p>Name one possible endorsement and one question. Do not write “always” unless a current source proves it.</p>")
                + step(3, "Match the decision, not just the test name", "<p>For each scenario, name what the result may affect, a next step, and one fact to verify.</p>")
                + step(4, "Check your thinking", f'<p>Finish the packet exit check. If time remains or you need another practice route, <a href="{quiz_url}">open the optional four-question practice check</a> and use the feedback.</p>'),
                "EXIT": "<p>Correct Jordan's claim that the SAT, TSIA, and an industry certification are all the same kind of test.</p>",
                "DONE": "<ul><li>graduation framework and source;</li><li>possible endorsement plus question;</li><li>assessment purpose table;</li><li>two scenario decisions;</li><li>one current verification source or person.</li></ul>",
                "SUPPORT": "<p>graduation = graduación · admission = admisión · placement = colocación · credential = credencial. Point to one word in the packet decision bank, then complete: “___ may affect ___, but it does not decide ___.”</p>",
                "FALLBACK": "<p>The printed packet is the complete route. Its dated cohort note and decision bank replace the live source and practice Quiz when either is unavailable. Keep the packet for Day 5.</p>",
            },
            2: {
                "TITLE": "Four-Year Course Plan Draft",
                "PURPOSE": "Build a source-checked draft for a future counselor conversation, not an official schedule.",
                "TODAY": "<ul><li>find current course information;</li><li>draft Grades 9-12;</li><li>explain one prerequisite chain;</li><li>keep a backup and counselor questions.</li></ul>",
                "READY": f'<p><strong>Default route:</strong> <a href="{annotation_url}">open the Canvas course-plan annotation</a>. Use {file_link(files["COURSE"]["id"], "the three-page paper or enlarged route")} only when your teacher assigns that route. Do not complete both. Keep the current Irving ISD coursebook open.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Planning words:</strong> prerequisite = a course required first · verify = check with a current source or counselor · backup = another route that protects the same goal.</p><p><strong>Use this frame:</strong> I placed ___ before ___ because the coursebook lists ___ as a prerequisite. I still need to verify ___.</p></div>',
                "STEPS": step(1, "Keep the source with the course", "<p>Record the exact title, grade level, prerequisite, source, and access date.</p><div style=\"border:1px solid #bad4df;background:#f2f8fb;padding:12px 16px;margin:12px 0\"><p style=\"margin:0 0 6px\"><strong>Worked sequence from the 2026-27 Irving coursebook:</strong></p><p style=\"margin:0\">Grade 9 English I → Grade 10 English II (prerequisite: English I) → Grade 11 English III - Dual Credit (prerequisite: English II). Mark <strong>VERIFY</strong> beside dual-credit readiness, campus availability, and counselor placement. A source-checked English III route is the backup.</p></div>")
                + step(2, "Draft one year at a time", "<p>Complete Grades 9-12. A blank marked for verification is better than an invented course. Use the model's structure, not its English choices.</p>")
                + step(3, "Explain the sequence", "<p>Show one prerequisite chain and why an earlier choice matters later.</p>")
                + step(4, "Protect the goal", "<p>Add a backup and two counselor questions about access, application, transportation, capacity, or sequence.</p>"),
                "EXIT": "<p>What do you do when a course title is current but its grade level, campus, or prerequisite is unclear?</p>",
                "DONE": "<ul><li>source and access date;</li><li>four-year draft;</li><li>one prerequisite chain;</li><li>one item marked for verification;</li><li>one backup;</li><li>two counselor questions.</li></ul>",
                "SUPPORT": "<p>prerequisite = requisito previo · verify = verificar · backup = alternativa. Complete: “I placed ___ before ___ because the coursebook lists ___ as a prerequisite. I still need to verify ___.”</p>",
                "FALLBACK": "<p>Use the embedded worked sequence and the three-page paper route. Mark every missing operational detail <strong>VERIFY</strong>. Do not submit course requests; the official Xello tasks wait for the counseling window.</p>",
            },
            3: {
                "TITLE": "College Credit and Plan Conversation",
                "PURPOSE": "Compare AP and dual credit, then test your plan with a question or reflection.",
                "TODAY": "<ul><li>compare AP and dual credit;</li><li>document one current local option;</li><li>explain one part of your plan;</li><li>record what you will keep, change, or verify.</li></ul>",
                "READY": f'<p>Open {file_link(files["CREDIT"]["id"], "the two-page College Credit and Plan Check")}. Your teacher will post the current TEA AP, dual-credit, and Irving coursebook pages.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Compare with:</strong> exam score · college course · receiving-college policy · eligibility · transcript · transfer · cost.</p><p><strong>Use this frame:</strong> AP and dual credit both ___. AP depends on ___, while dual credit depends on ___. Before I choose, I need to verify ___.</p></div>',
                "STEPS": step(1, "Compare the routes", "<p>AP uses an exam and receiving-college policy. Dual credit is a college course that gives high school and college credit after successful completion.</p>")
                + step(2, "Document one current option", "<p>Keep the exact name, type, grade level, prerequisite, possible credit, source/date, and one limitation or question.</p><div style=\"border:1px solid #bad4df;background:#f2f8fb;padding:12px 16px;margin:12px 0\"><p style=\"margin:0 0 6px\"><strong>Current Irving source card · 2026-27:</strong></p><p style=\"margin:0\"><strong>English III - Dual Credit</strong> is listed for Grades 10-12 with English II as the prerequisite. The coursebook says successful completion meets high-school and college-credit requirements. Still verify college readiness, campus availability, cost, transfer, and placement with the counselor or receiving college.</p></div>")
                + step(3, "Choose an equal conversation route", "<p>Use a family member, trusted adult, counselor, teacher, private writing, or private audio. A signature is not required.</p>")
                + step(4, "Revise honestly", "<p>Record one part you will keep, change, or verify because of the question or reflection.</p>"),
                "EXIT": "<p>Add one accurate fact to AP only, both, and dual credit only. Then write one verification question.</p>",
                "DONE": "<ul><li>accurate source comparison;</li><li>one current local option;</li><li>one limitation or question;</li><li>equal conversation or private route;</li><li>one keep, change, or verify decision.</li></ul>",
                "SUPPORT": "<p>exam score = puntaje de examen · college course = curso universitario · transfer = transferencia · eligibility = elegibilidad. Rehearse with the two sentence frames before writing.</p>",
                "FALLBACK": "<p>Use the embedded 2026-27 Irving source card and complete the private written reflection. Label any unanswered eligibility, transfer, cost, or scheduling detail <strong>VERIFY</strong>. No family signature, partner, or live search is required.</p>",
            },
            4: {
                "TITLE": "SMART Experience Action Plan",
                "PURPOSE": "Turn one possible experience into a realistic action with support and a backup.",
                "TODAY": "<ul><li>evaluate one experience;</li><li>write all five SMART parts;</li><li>check access, support, obstacle, and backup;</li><li>choose one action within seven days.</li></ul>",
                "READY": f'<p><strong>Default route:</strong> complete the SMART goal on FYF pp. 292-293, then open {file_link(files["SMART"]["id"], "the one-page Experience Access and Backup Check")}. The companion collects only the evidence the workbook does not ask for.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>SMART:</strong> Specific · Measurable · Achievable · Relevant · Time-Bound.</p><p><strong>Use these frames:</strong> By ___, I will ___, and I will know I made progress when ___. If ___ blocks the plan, I will ___ so I can still build ___.</p></div>',
                "STEPS": step(1, "Choose a real or clearly unverified experience", "<p>Choose one route: (1) an independent three-sample project, (2) a four-week service or responsibility role with an evidence log, or (3) one verified campus/community meeting with an independent-project backup. Do not contact an unfamiliar adult or workplace.</p>")
                + step(2, "Name the value", "<p>Record the skill it builds and how the same skill transfers to a second career.</p>")
                + step(3, "Write the five SMART parts", "<p>Specific, Measurable, Achievable, Relevant, and Time-Bound.</p>")
                + step(4, "Protect the plan", "<p>Add support, likely obstacle, backup, and one first action within seven days. Use an if/when-then action: “When class ends Friday, I will spend 20 minutes on sample 1. If the device is unavailable, I will sketch the same evidence on paper.”</p>"),
                "EXIT": "<p>Rank measure, access, time, support, and backup. Revise the weakest part now.</p>",
                "DONE": "<ul><li>experience and source;</li><li>skill plus second-career transfer;</li><li>all five SMART parts;</li><li>support and obstacle;</li><li>backup;</li><li>seven-day action.</li></ul>",
                "SUPPORT": "<p>specific = específico · measurable = medible · achievable = alcanzable · relevant = pertinente · time-bound = con fecha. Use “By [date], I will...” and “If [obstacle], I will...”</p>",
                "FALLBACK": "<p>The embedded workbook pages plus the one-page companion are the full independent route. Use an independent project or current responsibility if a club or program cannot be verified.</p>",
            },
            5: {
                "TITLE": "Individual High School and Career Plan",
                "PURPOSE": "Combine your evidence into a current direction, course and preparation plan, backup, and revision rule.",
                "TODAY": "<ul><li>gather Days 1-4 evidence;</li><li>write the individual plan;</li><li>self-score with the rubric;</li><li>revise and submit privately.</li></ul>",
                "READY": f'<p><strong>Default route:</strong> complete {file_link(files["PLAN"]["id"], "the four-page Individual Plan")} and use {file_link(files["RUBRIC"]["id"], "the two-page 16-point rubric")} on screen. Print the rubric only when you need a paper or enlarged copy. Submit the plan privately; keep Days 1-4 as source evidence.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Plan words:</strong> direction · evidence · prerequisite · preparation · backup · revision rule.</p><p><strong>Use these frames:</strong> My current direction is ___ because my evidence shows ___. I will revise this plan if ___ because that evidence would change ___.</p></div>',
                "STEPS": step(1, "Direction and self-evidence", "<p>Name a current direction, two pieces of self-evidence, and evidence that would make you reconsider.</p>")
                + step(2, "Course and preparation evidence", "<p>Bring forward the four-year draft, prerequisite chain, one verification item, preparation after high school, and one advanced or college-credit option.</p>")
                + step(3, "Action and revision", "<p>Write actions for seven days, the next counseling meeting, and Grade 9. Add support, backup, and a revision rule.</p>")
                + step(4, "Self-score and submit", f'<p>Circle one rubric level in each row, revise one weak section, then <a href="{plan_url}">submit the private plan</a> or hand in paper.</p>'),
                "EXIT": "<p>List three evidence-supported parts, two counseling questions, and one condition that would make you revise.</p>",
                "DONE": "<ul><li>all seven plan sections;</li><li>source/date labels kept;</li><li>backup and revision rule;</li><li>student-visible rubric check;</li><li>one visible revision;</li><li>private submission.</li></ul>",
                "SUPPORT": "<p>direction = dirección · evidence = evidencia · revision = revisión. Use “My current direction is... because...” and “I will revise this plan if...” Text, speech-to-text, and media answer the same jobs.</p>",
                "FALLBACK": "<p>Use the matching Student Guide and dated source cards to rebuild a missing section. Days 1-4 are source material, not four additional uploads. Canvas failure means paper or later upload without penalty. This is not an official course request.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Graduation and Assessment Decisions",
                "SUBTITLE": "50 minutes · TEKS d(3)(A), d(3)(E)",
                "ALERT": "<strong>Use the August 2026 Chapter 74 rule.</strong> The foundation baseline remains 22 credits and an endorsement requires at least 26. Beginning with students entering Grade 9 in 2026-2027, teach the new Personal Financial Literacy and social-studies choices. Current Grade 8 students enter high school after that start date. The 2025 toolkit shows prior-cohort wording.",
                "PREP": f'<ul><li><strong>Print:</strong> one copy per student of {file_link(files["TRANSITION"]["id"], "the three-page transition packet")}; no separate cohort or assessment cards. Page 1 carries the August 2026 Grade 8 cohort facts and page 2 carries the decision bank.</li><li><strong>Project:</strong> <a href="https://tea.texas.gov/laws-and-rules/sboe-rules-tac/sboe-tac-currently-effect/ch074b.pdf">current TEA Chapter 74, Subchapter B</a>. One device per pair is enough for a source check; the packet is the no-device route.</li><li><strong>Canvas:</strong> keep the four-question Quiz unpublished until the teacher chooses to use it as optional practice or recovery.</li></ul>',
                "EVIDENCE": "<p>Current graduation framework, possible endorsement plus verification question, purpose table, two assessment scenarios, and one source/person to verify. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "High school question and likely decision.")
                + flow("#4a9d2f", "Graduation framework · 12", "Foundation versus endorsement plan.")
                + flow("#1f617a", "Endorsement question · 10", "Possible connection without an always claim.")
                + flow("#e3ad19", "Assessment scenarios · 18", "Decision, next step, and verification.")
                + flow("#1f617a", "Exit · 5", "Correct the all-tests-are-the-same misconception."),
                "MONITOR": "<p><strong>Monitor:</strong> During the scenario block, check every student's first decision label before reading the explanation. Give the feedback, “Name the decision this result affects.” <strong>Misconception:</strong> students group every assessment as college admission. If three students do this, pause and sort EOC, TSIA, and certification under graduation, placement, and credential before restarting. <strong>Safe trim:</strong> skip the optional Canvas Quiz; do not trim the two scenarios or exit correction. <strong>Retain:</strong> record the formative completion during the exit lap, then students place the packet in their CCR Week 2 folder for Day 5.</p><p><strong>Key:</strong> EOC connects to graduation rules; PSAT to practice/feedback and some scholarship programs; SAT/ACT to admission or scholarships when a program uses them; TSIA to college readiness/placement with exemptions or alternatives; ASVAB to exploration and military qualification/job options; certification assessments to a named credential.</p>",
                "RESOURCES": "<p>Current TEA Chapter 74, Subchapter B controls the statewide baseline. The 2025 toolkit is a prior-cohort reference. The revised rule begins with students entering Grade 9 in 2026-2027 and therefore covers later cohorts, including current Grade 8 students. Irving course titles and each student's plan still require district and counselor confirmation.</p>",
                "SUPPORT": "<p>Point to the packet decision bank at the moment students enter each scenario. Read one scenario at a time, allow a 30-second oral rehearsal, and require the complete frame: “___ may affect ___, but it does not decide ___. I will verify ___ with ___.”</p>",
                "FALLBACK": "<p>The printed packet is the complete route and already includes the dated cohort facts. If the live TEA page or Canvas Quiz fails, students keep the source year and verification question. Do not require test-registration sites or private scores.</p>",
            },
            2: {
                "TITLE": "Four-Year Course Plan Draft",
                "SUBTITLE": "50 minutes · TEKS d(8)(B), d(3)(A)",
                "ALERT": "<strong>Draft, not requests.</strong> Do not open Xello Submit course requests or parent approval until counselors confirm the local window and process.",
                "PREP": f'<ul><li><strong>Default digital route:</strong> one device per student, the unpublished annotation Assignment, and the <a href="https://www.irvingisd.net/departments-services/curriculum-and-instruction/middle-school-and-high-school-course-descriptions">2026-27 Irving coursebook</a>.</li><li><strong>Paper/enlarged route:</strong> print one copy per assigned student of {file_link(files["COURSE"]["id"], "the three-page course-plan draft")}; students do not complete both routes.</li><li><strong>Project:</strong> the finished English I → English II → English III - Dual Credit example already embedded in the Student Guide. No teacher-created course card or model is required.</li></ul>',
                "EVIDENCE": "<p>Four-year draft, current source/date, one prerequisite chain, one verification label, backup, and two counselor questions. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "What prerequisite errors can cause.")
                + flow("#4a9d2f", "Source model · 10", "Exact title, grade, prerequisite, question, backup.")
                + flow("#1f617a", "Draft · 25", "Grades 9-12 and sequence check.")
                + flow("#e3ad19", "Audit · 5", "Source, sequence, verification.")
                + flow("#1f617a", "Exit · 5", "Branch when a detail is unclear."),
                "MONITOR": "<p><strong>Monitor:</strong> Lap 1 checks exact title/source/date and gives “Show me the line that supports this.” Lap 2 checks one prerequisite chain. Lap 3 checks a VERIFY label, backup, and two counselor questions. <strong>Misconception:</strong> a full table looks stronger than an honest unknown. If three students invent the same course or campus, stop and model a labeled VERIFY branch. <strong>Safe trim:</strong> change the peer audit to the same private self-audit; protect the prerequisite chain, backup, and questions. <strong>Save:</strong> Canvas students submit the annotation; paper students place the draft in the CCR Week 2 folder for Day 5.</p>",
                "RESOURCES": "<p>Authenticated Xello configuration: 4-year course plan 30 min; Make plans 30 min/add at least one plan; Submit course requests 20 min/Grade 8 only; parent approval 15 min/current due May 1, 2027. These remain counselor-window tasks.</p>",
                "SUPPORT": "<p>Use the embedded source-checked English sequence and complete one new Grade 9 row together. Keep the complete frame beside the explanation: “I placed ___ before ___ because ___. I still need to verify ___.” Canvas annotation is the default; the three-page paper route keeps the same evidence.</p>",
                "FALLBACK": "<p>The embedded model plus paper draft replace live search. Students mark unavailable details VERIFY and write the counselor question. Platform failure never authorizes an invented course or false Xello completion.</p>",
            },
            3: {
                "TITLE": "College Credit and Plan Conversation",
                "SUBTITLE": "50 minutes · TEKS d(3)(B), d(3)(D)",
                "ALERT": "<strong>No automatic credit or free-course promise.</strong> AP depends on exam performance and receiving-college policy. Dual credit has eligibility, completion, transfer, cost, and local-availability questions.",
                "PREP": f'<ul><li><strong>Print:</strong> one copy per student of {file_link(files["CREDIT"]["id"], "the two-page College Credit and Plan Check")}. Students keep it for Day 5.</li><li><strong>Devices:</strong> one per pair for current <a href="https://tea.texas.gov/student-readiness-and-high-school/college-career-and-military-prep/advanced-placement">TEA AP</a>, <a href="https://tea.texas.gov/student-readiness-and-high-school/college-career-and-military-prep/dual-credit">TEA Dual Credit</a>, and Irving coursebook checks; the printed packet and embedded card are the no-device route.</li><li><strong>Project:</strong> the 2026-27 Irving English III - Dual Credit source card embedded in the Student Guide. No teacher-created card is required.</li></ul>',
                "EVIDENCE": "<p>Accurate comparison, one current local option with source/date, limitation or question, and one keep/change/verify reflection. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Question before choosing college-credit work.")
                + flow("#4a9d2f", "Compare · 12", "AP and dual-credit evidence.")
                + flow("#1f617a", "Current option · 15", "Name, type, eligibility, possible credit, limitation.")
                + flow("#e3ad19", "Plan conversation · 13", "Equal adult or private route.")
                + flow("#1f617a", "Exit · 5", "AP-only, both, dual-only, question."),
                "MONITOR": "<p><strong>Monitor:</strong> At the end of the comparison, listen to one AP/dual-credit Think-Pair-Share per table. Then check each current option for a source/date and limitation. Give the feedback, “Attach the condition to the claim.” <strong>Misconception:</strong> taking AP guarantees credit or any dual credit is free and transfers everywhere. If it appears at two tables, return to receiving-college policy and FAST eligibility before research continues. <strong>Safe trim:</strong> use the embedded Irving card instead of live option research; protect the comparison and keep/change/verify reflection. <strong>Retain:</strong> students place the two-page check in the Week 2 folder.</p>",
                "RESOURCES": "<p>Use TEA for the route definitions and current Irving sources for local availability. A receiving college or counselor answers transfer and operational questions.</p>",
                "SUPPORT": "<p>Keep the word bank and complete AP/dual-credit frame visible during the comparison. Students rehearse once before writing. Family, trusted adult, counselor, teacher, private writing, and private audio are equal.</p>",
                "FALLBACK": "<p>No signature is required. The dated source card and private reflection route complete the lesson without a partner or family conversation.</p>",
            },
            4: {
                "TITLE": "SMART Experience Action Plan",
                "SUBTITLE": "50 minutes · TEKS d(3)(F), d(8)(C)",
                "ALERT": "<strong>Verify access before naming an opportunity.</strong> Do not promise a CTSO chapter, internship, job shadow, transportation route, or adult contact from workbook context alone.",
                "PREP": f'<ul><li><strong>Required HQIM:</strong> one FYF workbook per student, open to pp. 292-293.</li><li><strong>Print:</strong> one copy per student of {file_link(files["SMART"]["id"], "the one-page Experience Access and Backup Check")}. Students keep both pieces for Day 5.</li><li><strong>Project:</strong> the three ready routes in the Student Guide: independent three-sample project; four-week service/responsibility evidence log; or one verified meeting with an independent-project backup. No teacher-created opportunity list is required.</li></ul>',
                "EVIDENCE": "<p>Evaluated experience, transferable skill, all five SMART parts, access check, support, obstacle, backup, and seven-day action. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Experience and skill.")
                + flow("#4a9d2f", "SMART model · 8", "Weak versus source-checked goal.")
                + flow("#1f617a", "Evaluate experience · 10", "Skill, second career, access, alternative.")
                + flow("#e3ad19", "Write plan · 17", "Five SMART parts and protection.")
                + flow("#4a9d2f", "Self-check · 5", "Underline each part.")
                + flow("#1f617a", "Exit · 5", "Rank and revise the weak part."),
                "MONITOR": "<p><strong>Monitor:</strong> Lap 1 checks that the experience is real or marked VERIFY. Lap 2 has students point to all five SMART parts. Lap 3 checks access, obstacle, backup, and an exact seven-day action. Give the feedback, “Name when you will act and what you will do if the barrier happens.” <strong>Misconception:</strong> naming a club is a complete plan. If three students stop there, model the embedded when-then action and paper/device backup. <strong>Safe trim:</strong> drop the optional partner review and use the private checklist; do not trim the SMART goal or access/backup companion. <strong>Retain:</strong> the workbook and one-page companion return to the Week 2 evidence folder.</p>",
                "RESOURCES": "<p>Licensed Rung 6 pages are embedded. Rung 7 supplies opportunity categories, but current campus information controls availability.</p>",
                "SUPPORT": "<p>Keep the SMART labels beside the workbook and the if/when-then frame beside the obstacle and backup job. Allow oral rehearsal or speech-to-text before students record the same evidence.</p>",
                "FALLBACK": "<p>No eDynamic unit is required. An absent student can complete the packet with the embedded visuals and one source-checked option card.</p>",
            },
            5: {
                "TITLE": "Individual High School and Career Plan",
                "SUBTITLE": "50 minutes · TEKS d(8)(B), d(8)(C), d(3)(D)",
                "ALERT": "<strong>Major 2 is already mapped.</strong> The Assignment stays unpublished, is worth 100 points, and remains in Major Assessments (60%) so each teacher can publish it after cloning.",
                "PREP": f'<ul><li><strong>Default:</strong> one device per student, {file_link(files["PLAN"]["id"], "the four-page plan")}, the on-screen {file_link(files["RUBRIC"]["id"], "two-page student rubric")}, and the private unpublished Assignment.</li><li><strong>Paper/enlarged route:</strong> print one four-page plan per assigned student and one rubric only for students who need paper or enlarged scoring support.</li><li><strong>Set out:</strong> each student’s retained Days 1-4 evidence folder. No additional source packet or upload is required.</li></ul>',
                "EVIDENCE": "<p>Submit the four-page Individual Plan only. It synthesizes self-evidence, course and preparation evidence, college-credit evidence, timed actions, support, backup, and a revision rule. Major 2, scored with the 16-point profile and recorded as 100 gradebook points.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Supported part and open question.")
                + flow("#4a9d2f", "Gather · 5", "Days 1-4 evidence set.")
                + flow("#1f617a", "Write · 28", "8 min direction/self-evidence; 10 min course/preparation; 8 min action/revision, with a 1-minute source check after each of the first two chunks.")
                + flow("#e3ad19", "Self-score · 7", "Circle, revise, and retain evidence labels.")
                + flow("#1f617a", "Submit · 5", "Private 3-2-1 and plan."),
                "MONITOR": "<p><strong>Monitor:</strong> Check one section after each writing chunk: self-evidence, then course/preparation evidence, then action/revision. Give “Show the source or label VERIFY” before students continue. If several students copy unsupported claims, pause at the source/date field and revise one model line together. <strong>Safe trim:</strong> shorten the warm-up share and use a private rubric check; protect the visible revision and private submission. <strong>Collect:</strong> submit only the four-page plan in Canvas or collect the paper plan. Days 1-4 remain source evidence, not additional uploads.</p><p><strong>Scoring:</strong> Suggested conversion after local approval: 15-16 Masters, 13-14 Meets, 12 Approaches, 10-11 Needs Improvement; below 10 follows campus policy. Score evidence and reasoning, not family availability, adult agreement, grammar unless meaning is unclear, handwriting, art, accent, or submission mode.</p>",
                "RESOURCES": "<p>The plan prepares students for the counselor-controlled Xello planning tasks. It does not count as 4-year course plan, Make plans, Submit course requests, or parent approval completion.</p>",
                "SUPPORT": "<p>Use one numbered prompt per evidence job, speech-to-text, teacher scribe, or private media recording. The PDFs preserve full-width space.</p>",
                "FALLBACK": "<p>Missing prior evidence is rebuilt from the matching Student Guide and embedded source card. If class ends before all four rubric criteria are present, use the teacher's recovery window; do not delete a criterion to force submission. Canvas failure means paper or later upload without penalty.</p>",
            },
        }

        day_names = {
            1: "Graduation and Assessment Decisions",
            2: "Four-Year Course Plan Draft",
            3: "College Credit and Plan Conversation",
            4: "SMART Experience Action Plan",
            5: "Individual High School and Career Plan",
        }
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            await upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header_title, header_title))
            student_title = f"STUDENT: 4SW Wk2 Day {day} - {day_names[day]}"
            student_page = await common.upsert_page(
                client,
                student_title,
                common.render(
                    "4sw-wk2-student.html",
                    {"COURSE_ID": COURSE_ID, "DAY": day, "MEDIA": media[day], **contracts[day], **student[day]},
                ),
            )
            teacher_title = f"TEACHER: 4SW Wk2 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(
                client,
                teacher_title,
                common.render(
                    "4sw-wk2-teacher.html",
                    {
                        "COURSE_ID": COURSE_ID,
                        "DAY": day,
                        "STUDENT_PAGE_URL": student_page["url"],
                        **contracts[day],
                        **teacher[day],
                    },
                ),
            )
            await upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            order.extend(
                [
                    ("Page", teacher_page["url"], teacher_title),
                    ("Page", student_page["url"], student_title),
                ]
            )
            pages[day] = {"teacher": teacher_page, "student": student_page}
            if day == 1:
                await upsert_item(client, module["id"], "Quiz", quiz["id"], QUIZ_TITLE)
                order.append(("Quiz", quiz["id"], QUIZ_TITLE))
            if day == 2:
                await upsert_item(client, module["id"], "Assignment", annotation["id"], ANNOTATION_TITLE)
                order.append(("Assignment", annotation["id"], ANNOTATION_TITLE))
            if day == 5:
                await upsert_item(client, module["id"], "Assignment", plan_assignment["id"], PLAN_TITLE)
                order.append(("Assignment", plan_assignment["id"], PLAN_TITLE))

        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        keep_ids = set()
        for kind, key, _title in order:
            item = next(
                (
                    entry
                    for entry in items
                    if entry["id"] not in keep_ids and matches_item(entry, kind, key)
                ),
                None,
            )
            if item is None:
                raise RuntimeError(f"Missing expected module item: {kind} {key}")
            keep_ids.add(item["id"])
        for entry in items:
            if entry["id"] not in keep_ids:
                await common.api(
                    client,
                    "DELETE",
                    f"/courses/{COURSE_ID}/modules/{module['id']}/items/{entry['id']}",
                )

        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            matching = [entry for entry in items if matches_item(entry, kind, key)]
            if len(matching) != 1:
                raise RuntimeError(
                    f"Expected one module item for {kind} {key}; found {len(matching)}"
                )
            await common.api(
                client,
                "PUT",
                f"/courses/{COURSE_ID}/modules/{module['id']}/items/{matching[0]['id']}",
                data={
                    "module_item[position]": position,
                    "module_item[title]": title,
                    "module_item[published]": "false",
                },
            )

        final_items = sorted(
            await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items"),
            key=lambda entry: entry.get("position") or 0,
        )
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        quiz = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
        annotation = await common.api(
            client, "GET", f"/courses/{COURSE_ID}/assignments/{annotation['id']}"
        )
        annotation_file = await common.api(
            client,
            "GET",
            f"/files/{annotation['annotatable_attachment_id']}",
        )
        annotation_source = await common.api(
            client,
            "GET",
            f"/files/{files['COURSE']['id']}",
        )
        plan_assignment = await common.api(
            client, "GET", f"/courses/{COURSE_ID}/assignments/{plan_assignment['id']}"
        )
        if module.get("published"):
            raise RuntimeError("4SW Wk2 module unexpectedly published")
        if (
            quiz.get("published")
            or quiz.get("quiz_type") != "practice_quiz"
            or int(quiz.get("allowed_attempts") or 0) != -1
        ):
            raise RuntimeError("4SW Wk2 practice quiz invariant failed")
        if (
            annotation.get("published")
            or float(annotation.get("points_possible") or 0) != 0
            or annotation.get("grading_type") != "percent"
            or not annotation.get("omit_from_final_grade")
            or annotation_file.get("locked") is not True
            or annotation_source.get("locked") is not True
            or annotation_file.get("filename") != annotation_source.get("filename")
            or int(annotation_file.get("size") or -1)
            != int(annotation_source.get("size") or -2)
        ):
            raise RuntimeError("4SW Wk2 annotation invariant failed")
        if (
            plan_assignment.get("published")
            or float(plan_assignment.get("points_possible") or 0) != 100
            or plan_assignment.get("grading_type") != "points"
            or plan_assignment.get("assignment_group_id") != state["major_group"]["id"]
            or plan_assignment.get("omit_from_final_grade") is not False
            or 'data-cce-rubric-note="cce-advisory-rubric-v1"'
            not in (plan_assignment.get("description") or "")
        ):
            raise RuntimeError("4SW Wk2 mapped Major invariant failed")
        published_pages = [
            value["url"]
            for pair in pages.values()
            for value in pair.values()
            if value.get("published")
        ]
        if published_pages:
            raise RuntimeError(f"Published 4SW Wk2 pages remain: {published_pages}")
        if not support_folder.get("locked") or any(
            not folder.get("locked") for folder in visual_folders.values()
        ):
            raise RuntimeError("One or more 4SW Wk2 Canvas folders remain unlocked")
        if len(final_items) != 18 or len(final_items) != len(order):
            raise RuntimeError(
                f"Expected exactly 18 4SW Wk2 module items; found {len(final_items)}"
            )
        published_items = [
            entry.get("title") for entry in final_items if entry.get("published")
        ]
        if published_items:
            raise RuntimeError(f"Published 4SW Wk2 module items remain: {published_items}")
        for position, ((kind, key, title), item) in enumerate(zip(order, final_items), 1):
            if (
                item.get("position") != position
                or item.get("title") != title
                or not matches_item(item, kind, key)
            ):
                raise RuntimeError(f"4SW Wk2 module order mismatch at {position}")
        print(
            json.dumps(
                {
                    "module": {"id": module["id"], "published": module["published"]},
                    "quiz": {
                        "id": quiz["id"],
                        "published": quiz.get("published"),
                        "quiz_type": quiz.get("quiz_type"),
                        "allowed_attempts": quiz.get("allowed_attempts"),
                    },
                    "annotation": {
                        "id": annotation["id"],
                        "published": annotation.get("published"),
                        "submission_types": annotation.get("submission_types"),
                        "annotatable_attachment_id": annotation.get("annotatable_attachment_id"),
                        "points_possible": annotation.get("points_possible"),
                        "grading_type": annotation.get("grading_type"),
                        "omit_from_final_grade": annotation.get("omit_from_final_grade"),
                    },
                    "plan_assignment": {
                        "id": plan_assignment["id"],
                        "published": plan_assignment.get("published"),
                        "points_possible": plan_assignment.get("points_possible"),
                        "assignment_group_id": plan_assignment.get("assignment_group_id"),
                        "submission_types": plan_assignment.get("submission_types"),
                        "grading_type": plan_assignment.get("grading_type"),
                        "omit_from_final_grade": plan_assignment.get("omit_from_final_grade"),
                    },
                    "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"], "file_count": support_file_count},
                    "visual_folders": {
                        str(day): {"id": folder["id"], "locked": folder["locked"], "file_count": visual_file_counts[day]}
                        for day, folder in visual_folders.items()
                    },
                    "files": {key: value["id"] for key, value in files.items()},
                    "visuals": {
                        str(day): {name: value["id"] for name, value in entries.items()}
                        for day, entries in visuals.items()
                    },
                    "pages": {
                        str(day): {
                            kind: {"url": value["url"], "published": value["published"]}
                            for kind, value in pair.items()
                        }
                        for day, pair in pages.items()
                    },
                    "items": [
                        {"position": item["position"], "type": item["type"], "title": item["title"]}
                        for item in final_items
                    ],
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
