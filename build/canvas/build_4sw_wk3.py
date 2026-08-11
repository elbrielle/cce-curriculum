"""Build the unpublished 4SW Week 3 aviation and transportation module."""

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
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/4sw/wk3"
MODULE_NAME = "4SW Wk3: Aviation Routes, Systems, and Action Planning"
QUIZ_TITLE = "PRACTICE: Is This Survey Useful?"
LAB_TITLE = "PRACTICE: Airport Design and Simulation Lab"
PLAN_TITLE = "MINOR 1: Aviation Route and Action Plan"
RUBRIC_NOTE_MARKER = 'data-cce-rubric-note="cce-advisory-rubric-v1"'
WORKSHEET_FILES = {
    "SURVEY": "4sw-wk3-transportation-survey-design.pdf",
    "ROUTES": "4sw-wk3-aviation-careers-and-pilot-routes.pdf",
    "LAB": "4sw-wk3-airport-design-simulation-lab.pdf",
    "CARDS": "4sw-wk3-classroom-scenario-cards.pdf",
    "PLAN": "4sw-wk3-aviation-route-action-plan.pdf",
    "RUBRIC": "4sw-wk3-route-action-rubric.pdf",
}
VISUAL_FILES = {
    1: (
        "fyf-transportation-cluster.jpg",
        "fyf-transportation-survey-scenario.jpg",
        "fyf-transportation-survey-build.jpg",
    ),
    2: ("fyf-flight-line-fixers-intro.jpg", "fyf-aviation-maintenance-program.jpg"),
    5: ("fyf-aviation-app-exploration.jpg",),
}


def preflight():
    required = [
        ROOT / "build/canvas/templates/4sw-wk3-student.html",
        ROOT / "build/canvas/templates/4sw-wk3-teacher.html",
        *(ROOT / "docs/resources/worksheets" / name for name in WORKSHEET_FILES.values()),
        *(
            ASSETS / f"day{day}" / name
            for day, names in VISUAL_FILES.items()
            for name in names
        ),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"4SW Wk3 preflight missing required files: {missing}")


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    matches = [entry for entry in modules if entry["name"] == MODULE_NAME]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one module named {MODULE_NAME!r}; found {len(matches)}")
    found = matches[0] if matches else None
    data = {"module[published]": "false"}
    if found:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data=data)
    data["module[name]"] = MODULE_NAME
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


QUESTIONS = [
    (
        "Q1 - Neutral wording",
        "Which survey question is most neutral?",
        "How often would you use a bus that arrived every 20 minutes?",
        [
            "Wouldn't a faster bus make everyone's life better?",
            "Why is the current bus schedule terrible?",
            "Don't you agree that the city needs more buses?",
        ],
        "Correct. It asks one measurable question without pushing a preferred answer.",
        "A useful survey question does not tell the respondent what to think.",
    ),
    (
        "Q2 - Complete choices",
        "A frequency question offers only Never, Sometimes, and Every day. What is the best revision?",
        "Use clear, non-overlapping ranges and add Not sure when it closes a real gap.",
        [
            "Keep the choices because every response fits perfectly.",
            "Ask for the respondent's name instead.",
            "Replace the question with a slogan.",
        ],
        "Correct. Distinct ranges make the results easier to interpret.",
        "Answer choices should cover realistic responses without overlapping.",
    ),
    (
        "Q3 - Privacy",
        "Which detail should this fictional transportation survey avoid collecting?",
        "A respondent's exact home address and work schedule",
        [
            "A broad transportation barrier",
            "How often a route might be used",
            "A suggestion for improving a stop"],
        "Correct. The analyst does not need precise identifying or schedule information for this design task.",
        "Collect only information needed to answer the fictional transportation question.",
    ),
    (
        "Q4 - Evidence to action",
        "A repeated survey pattern shows that evening-shift workers cannot reach the current route after 9 p.m. What is a defensible analyst response?",
        "Recommend that the city evaluate later service, route access, cost, and staffing using more evidence.",
        [
            "Promise that every route will run all night.",
            "Publish the respondents' schedules.",
            "Ignore the pattern because it came from a survey."],
        "Correct. The recommendation stays connected to evidence and does not promise a final decision.",
        "An analyst can recommend further evaluation, not guarantee a policy change.",
    ),
]


async def prepare_quiz_questions(client, quiz_id, desired_names):
    existing = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions")
    keep, seen = [], set()
    for question in existing:
        name = question.get("question_name")
        if name not in desired_names or name in seen:
            await common.api(client, "DELETE", f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions/{question['id']}")
        else:
            seen.add(name)
            keep.append(question)
    return keep


async def finalize_quiz_order(client, quiz_id, expected_names):
    final = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions")
    by_name = {entry.get("question_name"): entry for entry in final}
    if set(by_name) != set(expected_names) or len(final) != len(expected_names):
        raise RuntimeError(f"Quiz {quiz_id} question mismatch: {[entry.get('question_name') for entry in final]}")
    fields = []
    for name in expected_names:
        fields.extend([("order[][id]", str(by_name[name]["id"])), ("order[][type]", "question")])
    await common.api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/quizzes/{quiz_id}/reorder",
        content=urlencode(fields),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    ordered = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions")
    actual = [entry.get("question_name") for entry in ordered]
    if actual != expected_names:
        raise RuntimeError(f"Quiz {quiz_id} order mismatch: expected {expected_names}, found {actual}")


async def upsert_quiz(client):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    matches = [entry for entry in quizzes if entry.get("title") == QUIZ_TITLE]
    if len(matches) > 1:
        raise RuntimeError(f"Duplicate quizzes named {QUIZ_TITLE!r}: {[entry['id'] for entry in matches]}")
    found = matches[0] if matches else None
    data = {
        "quiz[title]": QUIZ_TITLE,
        "quiz[description]": "<p>Grade-neutral practice. Retry and use the feedback to check wording, answer choices, privacy, and an evidence-based recommendation.</p>",
        "quiz[quiz_type]": "practice_quiz",
        "quiz[published]": "false",
        "quiz[allowed_attempts]": "-1",
        "quiz[show_correct_answers]": "true",
        "quiz[shuffle_answers]": "false",
    }
    endpoint = f"/courses/{COURSE_ID}/quizzes/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes"
    quiz = await common.api(client, "PUT" if found else "POST", endpoint, data=data)
    expected = [spec[0] for spec in QUESTIONS]
    existing = await prepare_quiz_questions(client, quiz["id"], set(expected))
    for position, (name, prompt, correct, wrong, yes, no) in enumerate(QUESTIONS, 1):
        prior = next((entry for entry in existing if entry.get("question_name") == name), None)
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
        question_path = (
            f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior['id']}"
            if prior
            else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        )
        await common.api(client, "PUT" if prior else "POST", question_path, json=payload)
    await finalize_quiz_order(client, quiz["id"], expected)
    final = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
    if final.get("published") or final.get("quiz_type") != "practice_quiz" or int(final.get("allowed_attempts") or 0) != -1:
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


def module_item_matches(item, kind, key, title):
    if item.get("type") != kind:
        return False
    if kind == "SubHeader":
        return item.get("title") == title
    if kind == "Page":
        return item.get("page_url") == key
    if kind in ("Assignment", "Quiz"):
        return item.get("content_id") == key
    return False


async def reconcile_module_items(client, module_id, expected):
    remaining = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    kept = []
    for position, (kind, key, title) in enumerate(expected, 1):
        matches = [item for item in remaining if module_item_matches(item, kind, key, title)]
        if matches:
            item = matches[0]
            for duplicate in matches[1:]:
                await common.api(client, "DELETE", f"/courses/{COURSE_ID}/modules/{module_id}/items/{duplicate['id']}")
                remaining.remove(duplicate)
        else:
            item = await upsert_item(client, module_id, kind, key, title)
        remaining = [entry for entry in remaining if entry.get("id") != item.get("id")]
        item = await common.api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            data={"module_item[title]": title, "module_item[position]": position, "module_item[published]": "false"},
        )
        kept.append(item)
    for stale in remaining:
        await common.api(client, "DELETE", f"/courses/{COURSE_ID}/modules/{module_id}/items/{stale['id']}")
    final = sorted(
        await common.paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items"),
        key=lambda item: item.get("position") or 0,
    )
    if len(final) != len(expected):
        raise RuntimeError(f"Expected {len(expected)} exact module items; found {len(final)}")
    for item, (kind, key, title) in zip(final, expected):
        if not module_item_matches(item, kind, key, title) or item.get("title") != title or item.get("published"):
            raise RuntimeError(
                f"Module item invariant failed at position {item.get('position')}: "
                f"type={item.get('type')}, title={item.get('title')}, published={item.get('published')}"
            )
    return final


async def require_minor_preflight(client):
    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group_matches = [entry for entry in groups if entry.get("name") == "Minor Assessments (40%)"]
    if len(group_matches) != 1:
        raise RuntimeError(
            "Expected exactly one assignment group named 'Minor Assessments (40%)'; "
            f"found {len(group_matches)}"
        )
    group = group_matches[0]
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == PLAN_TITLE]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one existing mapped Minor assignment named {PLAN_TITLE!r}; found {len(matches)}"
        )
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
            f"Mapped Minor invariant failed before module writes: published={found.get('published')}, "
            f"points={found.get('points_possible')}, group={found.get('assignment_group_id')}, "
            f"grading={found.get('grading_type')}, omit={found.get('omit_from_final_grade')}, "
            f"rubric_note={rubric_note is not None}"
        )
    return found, group


async def update_minor_assignment(client, found, group, description):
    rubric_note = re.search(
        r'<div data-cce-rubric-note="cce-advisory-rubric-v1".*?</div>',
        found.get("description") or "",
        flags=re.I | re.S,
    )
    if rubric_note is None:
        raise RuntimeError(f"Mapped Minor is missing required rubric conversion note: {PLAN_TITLE!r}")
    plan = await common.api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{found['id']}",
        data={
            "assignment[description]": description + rubric_note.group(0),
            "assignment[submission_types][]": [
                "online_upload",
                "online_text_entry",
                "media_recording",
            ],
            "assignment[published]": "false",
        },
    )
    if (
        plan.get("published")
        or float(plan.get("points_possible") or 0) != 100
        or plan.get("assignment_group_id") != group["id"]
        or plan.get("grading_type") != "points"
        or plan.get("omit_from_final_grade") is not False
        or RUBRIC_NOTE_MARKER not in (plan.get("description") or "")
    ):
        raise RuntimeError(
            f"Minor invariant failed after update: published={plan.get('published')}, "
            f"points={plan.get('points_possible')}, group={plan.get('assignment_group_id')}, "
            f"grading={plan.get('grading_type')}, omit={plan.get('omit_from_final_grade')}, "
            f"rubric_note={RUBRIC_NOTE_MARKER in (plan.get('description') or '')}"
        )
    return plan


async def upsert_lab_annotation(client, description, attachment_id):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == LAB_TITLE]
    if len(matches) > 1:
        raise RuntimeError(f"Duplicate assignments named {LAB_TITLE!r}: {[entry['id'] for entry in matches]}")
    found = matches[0] if matches else None
    data = {
        "assignment[name]": LAB_TITLE,
        "assignment[description]": description,
        "assignment[submission_types][]": ["student_annotation", "online_upload", "online_text_entry"],
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
    assignment = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignment['id']}")
    source_file = await common.api(client, "GET", f"/files/{attachment_id}")
    annotation_attachment_id = int(assignment.get("annotatable_attachment_id") or 0)
    annotation_file = (
        await common.api(client, "GET", f"/files/{annotation_attachment_id}")
        if annotation_attachment_id
        else {}
    )
    if annotation_file and not annotation_file.get("locked"):
        annotation_file = await common.api(client, "PUT", f"/files/{annotation_attachment_id}", data={"locked": "true"})
    failures = {
        "published": assignment.get("published") is not False,
        "points_possible": float(assignment.get("points_possible") or 0) != 0,
        "grading_type": assignment.get("grading_type") != "percent",
        "omit_from_final_grade": assignment.get("omit_from_final_grade") is not True,
        "annotatable_attachment_missing": not annotation_attachment_id,
        "source_file_locked": source_file.get("locked") is not True,
        "annotation_file_locked": annotation_file.get("locked") is not True,
        "annotation_filename": annotation_file.get("filename") != source_file.get("filename"),
        "annotation_size": int(annotation_file.get("size") or -1) != int(source_file.get("size") or -2),
    }
    failed = [name for name, value in failures.items() if value]
    if failed:
        raise RuntimeError(
            f"Lab annotation invariant failed ({', '.join(failed)}): source={attachment_id}, "
            f"attachment={annotation_attachment_id}, source_name={source_file.get('filename')!r}, "
            f"attachment_name={annotation_file.get('filename')!r}, source_size={source_file.get('size')}, "
            f"attachment_size={annotation_file.get('size')}"
        )
    return assignment


def image_tag(file_id, alt, max_width=700):
    return (
        f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" '
        f'style="display:block;width:100%;max-width:{max_width}px;height:auto;margin:14px auto;border:1px solid #ddd" '
        f'data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'
    )


async def main():
    preflight()
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        mapped_minor, minor_group = await require_minor_preflight(client)
        module = await ensure_module(client)
        support_path = "course files/CCR Materials/4SW/Wk3"
        support_folder = await common.ensure_folder(client, support_path)
        files = {
            key: await common.upload(client, ROOT / "docs/resources/worksheets" / filename, support_path)
            for key, filename in WORKSHEET_FILES.items()
        }

        visuals, visual_folders = {}, {}
        for day, image_names in VISUAL_FILES.items():
            folder_path = f"course files/CCR Materials/4SW/Wk3/Day {day} Visuals"
            visual_folders[day] = await common.ensure_folder(client, folder_path)
            visuals[day] = {
                name: await common.upload(client, ASSETS / f"day{day}" / name, folder_path)
                for name in image_names
            }
        support_folder = await common.lock_folder_files(client, support_folder)
        for day in visual_folders:
            visual_folders[day] = await common.lock_folder_files(client, visual_folders[day])

        quiz = await upsert_quiz(client)
        lab = await upsert_lab_annotation(
            client,
            "<p>Plan, test, and revise the fictional classroom airport model. Pages 1-2 are team evidence; pages 3-4 are individual evidence. Use Canvas annotation, upload, text entry, or the assigned paper pages. LEGO, paper, and Lucid are equal build routes. This is not FAA training.</p>",
            files["LAB"]["id"],
        )
        plan_description = f'<p>Start the four-page Aviation Route and Action Plan on Day 2 and submit it once on Day 5. Include one source-labeled career fact, one route tradeoff and verification question, three timed actions, support, obstacle, equal backup, revision condition, self-score, and visible revision. Submit privately by file upload, typed response, or approved media response. Use the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">student scoring guide</a> before submitting. This assignment is already mapped as a 100-point Minor Assessment and remains unpublished for teacher review and cloning.</p>'
        plan = await update_minor_assignment(client, mapped_minor, minor_group, plan_description)
        quiz_url = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        lab_url = f"/courses/{COURSE_ID}/assignments/{lab['id']}"
        plan_url = f"/courses/{COURSE_ID}/assignments/{plan['id']}"
        lucid_url = f"/courses/{COURSE_ID}/external_tools/17478"

        media = {
            1: image_tag(visuals[1]["fyf-transportation-cluster.jpg"]["id"], "Find Your Future Transportation, Distribution, and Logistics cluster opener")
            + image_tag(visuals[1]["fyf-transportation-survey-scenario.jpg"]["id"], "Find Your Future Transportation Survey Project scenario and first two steps")
            + image_tag(visuals[1]["fyf-transportation-survey-build.jpg"]["id"], "Find Your Future Transportation Survey Project incentive and campaign steps"),
            2: '<details style="border:1px solid #c9dce6;border-radius:8px;background:#f2f8fb;padding:10px 14px;margin:16px 0"><summary style="font-weight:700;color:#1f617a;cursor:pointer">Optional: Flight Line Fixers and workbook program context</summary>'
            + image_tag(visuals[2]["fyf-flight-line-fixers-intro.jpg"]["id"], "Find Your Future Flight Line Fixers introduction and simplified observation table")
            + image_tag(visuals[2]["fyf-aviation-maintenance-program.jpg"]["id"], "Find Your Future workbook Aviation Maintenance program paragraph", 620)
            + "</details>",
            3: "",
            4: "",
            5: '<details style="border:1px solid #c9dce6;border-radius:8px;background:#f2f8fb;padding:10px 14px;margin:16px 0"><summary style="font-weight:700;color:#1f617a;cursor:pointer">Optional after the core plan: H&amp;L App Exploration</summary>'
            + image_tag(visuals[5]["fyf-aviation-app-exploration.jpg"]["id"], "Find Your Future optional H and L app exploration page")
            + "</details>",
        }

        file_link, step, flow = common.file_link, common.step, common.flow
        contracts = {
            1: {
                "TOPIC": "Career Clusters",
                "OBJECTIVE": "Students will explore and describe the CTE career clusters and identify career opportunities within one or more career clusters using evidence from Career Clusters.",
                "TEKS": "d(1)(B), d(1)(C)",
                "DOL": "Team Transportation Survey Project with 10 questions, a hypothetical incentive, a campaign choice, and an individual survey-quality check.",
                "I_CAN": "describe the Transportation cluster and design a useful survey with my team.",
                "SHOW": "complete the team Transportation Survey Project and my individual survey-quality check.",
            },
            2: {
                "TOPIC": "Career Opportunities",
                "OBJECTIVE": "Students will identify career opportunities within one or more career clusters and investigate and report the steps required to participate or enroll in career and educational opportunities using evidence from Career Opportunities.",
                "TEKS": "d(1)(C), d(3)(G)",
                "DOL": "Completed Day 2 evidence section of the Aviation Route and Action Plan with one source-based route decision.",
                "I_CAN": "compare aviation careers and report the steps and tradeoffs in two pilot-preparation routes.",
                "SHOW": "complete the Day 2 evidence section of my Aviation Route and Action Plan using the dated reference guide.",
            },
            3: {
                "TOPIC": "Career Opportunities",
                "OBJECTIVE": "Students will identify career opportunities within one or more career clusters using evidence from Career Opportunities.",
                "TEKS": "d(1)(C)",
                "DOL": "Team airport map and readiness check plus an individual design note that names an aviation role and work product.",
                "I_CAN": "connect an airport-operations role to a map feature and revise a classroom model.",
                "SHOW": "complete the team map and readiness check plus my individual design note.",
            },
            4: {
                "TOPIC": "Goals and Time",
                "OBJECTIVE": "Students will demonstrate effective time-management and goal-setting strategies and identify career opportunities within one or more career clusters using evidence from Goals and Time.",
                "TEKS": "d(4)(A), d(1)(C)",
                "DOL": "Team Simulation Run Log with three tests plus an individual timed iteration plan and new-scenario response.",
                "I_CAN": "use a timed goal to improve a team system and explain the aviation work behind the change.",
                "SHOW": "complete the team run log and my individual timed iteration and new-scenario response.",
            },
            5: {
                "TOPIC": "Goals and Time",
                "OBJECTIVE": "Students will demonstrate effective time-management and goal-setting strategies and identify career opportunities within one or more career clusters using evidence from Goals and Time.",
                "TEKS": "d(4)(A), d(1)(C)",
                "DOL": "Private individual Aviation Route and Action Plan with student-visible 16-point rubric.",
                "I_CAN": "use evidence, timing, support, and a backup to plan my next career-exploration steps.",
                "SHOW": "submit my private Aviation Route and Action Plan after self-scoring and revising it.",
            },
        }
        student = {
            1: {
                "TITLE": "Transportation Cluster and Survey Design",
                "PURPOSE": "Design questions that could reveal a transportation need without collecting private information.",
                "TODAY": "<ul><li>meet Transportation careers;</li><li>choose a fictional audience with your team;</li><li>build ten balanced questions;</li><li>add an incentive and campaign choice;</li><li>complete your own quality check.</li></ul>",
                "READY": f'<p>Use FYF pp. 166-167 with {file_link(files["SURVEY"]["id"], "the three-page team Survey Project packet")}. Your team needs one packet or shared digital copy. Keep the survey fictional. Do not collect names, addresses, schedules, contact information, or real responses.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:12px 16px;margin:14px 0"><strong>Words for this task:</strong> neutral · answer choice · private information · campaign<br><strong>Use this frame:</strong> “This question is useful because [reason]. We revised [question or choice] so the answers would [improvement].”</div>',
                "STEPS": step(1, "Define the audience and need", "<p>Choose one fictional audience as a team. Name the transportation problem and the evidence an analyst would need.</p>")
                + step(2, "Build the ten questions", "<p>Write seven multiple-choice and three short-answer questions together. Use neutral wording and distinct answer choices. Record each team member's job.</p>")
                + step(3, "Add an incentive and campaign choice", "<p>Explain one hypothetical incentive and choose one FYF campaign format. Neither is a real offer or public post.</p>")
                + step(4, "Complete your own quality check", f'<p>Revise one question with your team, then <a href="{quiz_url}">complete the individual practice Quiz</a> and connect the work to a Transportation career.</p>'),
                "EXIT": "<p>Identify neutral wording, one misleading answer-choice problem, one privacy boundary, and one analyst action.</p>",
                "DONE": "<ul><li>team audience and need;</li><li>7 multiple-choice and 3 short-answer questions;</li><li>hypothetical incentive and campaign choice;</li><li>team roles recorded;</li><li>one visible revision;</li><li>individual practice feedback and career connection completed.</li></ul>",
                "SUPPORT": "<p>neutral = neutral · response choice = opción de respuesta · private information = información privada. A reason or comparison gets its own full-width writing area in the packet.</p>",
                "FALLBACK": "<p>The embedded workbook pages and packet are the complete independent route. A missing partner completes one shortened five-question survey and the same individual check. Do not distribute the survey.</p>",
            },
            2: {
                "TITLE": "Aviation Careers and Pilot Routes",
                "PURPOSE": "Compare aviation work and preparation without confusing national median pay, local pay, entry pay, or military service.",
                "TODAY": "<ul><li>compare three aviation careers;</li><li>compare civilian and Air Force pilot examples;</li><li>name one route tradeoff;</li><li>write a source-based recommendation for fictional Sam.</li></ul>",
                "READY": f'<p>Post or open {file_link(files["ROUTES"]["id"], "the two-page Careers and Pilot Routes reference")}. Then open {file_link(files["PLAN"]["id"], "the four-page Aviation Route and Action Plan")} and complete only the Day 2 evidence section. The pay figures are May 2024 U.S. national medians, not DFW starting salaries.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:12px 16px;margin:14px 0"><strong>Words for this task:</strong> route · preparation · commitment · tradeoff · verify<br><strong>Use this frame:</strong> “The [route] may fit Sam because [evidence]. A tradeoff is [benefit or limit]. Before deciding, Sam must verify [unknown] with [authorized source or person].”</div>',
                "STEPS": step(1, "Compare the three careers", "<p>Read daily work, common preparation, and the exact pay label for commercial pilot, air traffic controller, and aircraft mechanic.</p>")
                + step(2, "Compare two pilot examples", "<p>Use the reference table to compare the steps, possible advantages, tradeoffs, and verification sources. Do not recopy the whole table.</p>")
                + step(3, "Keep the military boundary", "<p>The Air Force example requires officer eligibility, selection, training, and a current 10-year active-duty commitment after pilot training. It is service, not free flight school.</p>")
                + step(4, "Recommend an investigation route", "<p>Write three sentences for fictional Sam using two facts and an authorized next source.</p>"),
                "EXIT": "<p>Choose the first route Sam should investigate, cite one step and tradeoff, and name who or what should verify the next requirement.</p>",
                "DONE": "<ul><li>three careers reviewed;</li><li>both route examples compared;</li><li>one selected entry step and tradeoff recorded;</li><li>authorized verification source named;</li><li>source-based recommendation and local access question completed.</li></ul>",
                "SUPPORT": "<p>route/ruta · preparation/preparación · commitment/compromiso · verify/verificar. Read one evidence card at a time; mark work, preparation, pay label, and source before writing.</p>",
                "FALLBACK": "<p>The dated guide replaces live search and H&amp;L. Flight Line Fixers is optional. No student diagnoses a real aircraft or completes a personal medical or military eligibility screen.</p>",
            },
            3: {
                "TITLE": "Design a Classroom Airport Map",
                "PURPOSE": "Build a shared map that can be tested, explained, and revised.",
                "TODAY": "<ul><li>plan before building;</li><li>label routes and gates;</li><li>predict one conflict point;</li><li>test one movement and revise.</li></ul>",
                "READY": f'<p>Open {file_link(files["LAB"]["id"], "the Airport Design and Simulation Lab")} or <a href="{lab_url}">the Canvas annotation activity</a>. Your build route may be LEGO, paper, or <a href="{lucid_url}">Lucid</a>; all use the same evidence checklist.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:12px 16px;margin:14px 0"><strong>Words for this task:</strong> runway · taxi route · gate · conflict point · alternate route<br><strong>Use this frame:</strong> “A [aviation role] uses the [map feature] to [task]. We changed [feature or sequence] because the test showed [evidence].”</div>',
                "STEPS": step(1, "Read the classroom constraints", "<p>Two labeled runways, taxi routes, tower, four gates, north arrow, and an alternate route. These are classroom rules, not FAA standards.</p>")
                + step(2, "Draw the top-down plan", "<p>Add movement arrows, one predicted conflict point, and one planned revision before building.</p>")
                + step(3, "Build through an equal route", "<p>Use LEGO, paper, or Lucid. Artwork and construction detail are not graded.</p>")
                + step(4, "Run the readiness check", "<p>Move one aircraft from Gate 1 to R1 and back. Correct one blocked or confusing route.</p>"),
                "EXIT": "<p>Name one map feature and role, one conflict point with evidence, and one revision completed or still needed.</p>",
                "DONE": "<ul><li>complete labeled sketch;</li><li>one predicted conflict;</li><li>one revision;</li><li>usable model or map;</li><li>individual design note.</li></ul>",
                "SUPPORT": "<p>runway = pista · taxi route = ruta de rodaje · gate = puerta · conflict point = punto de conflicto. Planner, recorder, mover, checker, and builder are equal roles.</p>",
                "FALLBACK": "<p>Use the independent paper/digital map. A photo is optional and cannot include faces or student names. No partner or speaking performance is required.</p>",
            },
            4: {
                "TITLE": "Test, Communicate, and Revise",
                "PURPOSE": "Use precise classroom directions, test changing constraints, and connect a timed revision to evidence.",
                "TODAY": "<ul><li>practice a five-step classroom protocol;</li><li>run three tests;</li><li>log one breakdown each run;</li><li>write an individual timed iteration plan.</li></ul>",
                "READY": f'<p>Use pages 1-2 of {file_link(files["LAB"]["id"], "the four-page Lab")} once per team and pages 3-4 once per student. Project or give each team {file_link(files["CARDS"]["id"], "the one-page Scenario Cards")}. This is a fictional classroom protocol, not FAA phraseology.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:12px 16px;margin:14px 0"><strong>Protocol words:</strong> Name · Route · Repeat · Confirm · Log<br><strong>Use this frame:</strong> “Our goal was [specific improvement] during the [two- or three]-minute block. The log shows [evidence], so next we would [adjustment].”</div>',
                "STEPS": step(1, "Practice Name, Route, Repeat, Confirm, Log", "<p>Use one aircraft and one complete model call before starting a timed run.</p>")
                + step(2, "Run three eight-minute tests", "<p>Test, identify a breakdown, revise, and prepare the next run. One aircraft waits when two requests arrive together.</p>")
                + step(3, "Keep roles equal", "<p>Controller, mover, recorder, and safety checker all create evidence. Speaking is not required.</p>")
                + step(4, "Write the individual plan", "<p>Name the goal, exact two- or three-minute work block, support, evidence, and next adjustment.</p>"),
                "EXIT": "<p>For the blocked Taxi A scenario, choose a sequence, write the full classroom call, and state one two-minute improvement goal.</p>",
                "DONE": "<ul><li>three run-log sections or two plus a written third;</li><li>breakdown and revision each run;</li><li>individual timed iteration plan;</li><li>new scenario response.</li></ul>",
                "SUPPORT": "<p>Name = nombre · route = ruta · repeat = repetir · confirm = confirmar · log = registrar. The printed card keeps all five steps visible.</p>",
                "FALLBACK": "<p>Use the model map and written scenario route. Paper, LEGO, and Lucid use the same evidence. Team performance is not required for the individual work.</p>",
            },
            5: {
                "TITLE": "Aviation Route and Action Plan",
                "PURPOSE": "Choose a current direction and protect it with sources, timing, support, a backup, and a revision rule.",
                "TODAY": "<ul><li>reopen career and simulation evidence;</li><li>write three timed stages;</li><li>add support, obstacle, backup, and revision condition;</li><li>self-score, revise, and submit privately.</li></ul>",
                "READY": f'<p>Reopen {file_link(files["PLAN"]["id"], "the four-page Action Plan you started on Day 2")} and {file_link(files["RUBRIC"]["id"], "the two-page 16-point rubric")}.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:12px 16px;margin:14px 0"><strong>Planning words:</strong> direction · evidence · time block · support · backup · revise<br><strong>Use this frame:</strong> “By [date], I will [action] for [minutes]. I will know it is complete when [evidence]. If [obstacle] happens, I will [equal backup] instead.”</div>',
                "STEPS": step(1, "Choose a current direction", "<p>Investigate aviation, select another Transportation career, or state that the cluster is not your current fit. The direction itself is not graded.</p>")
                + step(2, "Bring forward evidence", "<p>Keep daily work, preparation, tradeoff, simulation skill, source, date, geography, and measure.</p>")
                + step(3, "Write three stages", "<p>Plan one action within seven days, one before the next counseling meeting, and one during Grade 9 or after high school. Add completion evidence and honest labels.</p>")
                + step(4, "Self-score and submit", f'<p>Revise the weakest section, then <a href="{plan_url}">submit privately</a> by upload, text, media, or paper.</p>'),
                "EXIT": "<p>List three timed stages, one support and one backup, and one condition that would make you revise.</p>",
                "DONE": "<ul><li>current direction and reason;</li><li>daily-work and preparation facts;</li><li>three timed stages;</li><li>source/date labels;</li><li>support, obstacle, backup, and revision condition;</li><li>one visible revision and private submission.</li></ul>",
                "SUPPORT": "<p>direction = dirección · evidence = evidencia · backup = alternativa · revise = revisar. Text, speech-to-text, private media, and paper answer the same evidence jobs.</p>",
                "FALLBACK": "<p>Missing simulation work can use the model log. H&amp;L, Xello Jobs and Employers, and eDynamic are optional extensions only. Canvas failure means paper or later upload without penalty.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Transportation Cluster and Survey Design",
                "SUBTITLE": "50 minutes · TEKS d(1)(B), d(1)(C)",
                "ALERT": "<strong>Fictional team design only.</strong> Students do not distribute the survey, collect real responses, or request personal information. The incentive and campaign remain hypothetical.",
                "PREP": f'<ul><li><strong>Teams:</strong> four students. Assign facilitator/timekeeper, question writer, choice checker, and campaign designer.</li><li><strong>Print:</strong> one {file_link(files["SURVEY"]["id"], "three-page Survey Project packet")} per team, or zero when each team has one shared editable digital copy. Keep one half-sheet per student only for a Canvas outage.</li><li><strong>Devices:</strong> one per student for the five-minute private practice Quiz; one per team during drafting only when using the shared digital route.</li><li>Open FYF pp. 149 and 166-167. Put one labeled tray or digital folder per class period where teams will submit the single packet/copy.</li></ul>',
                "MODEL": "<p><strong>Useful item:</strong> “How many days each week would you use a bus after 6 p.m.? 0 · 1-2 · 3-4 · 5 or more · Not sure.” <strong>Non-example:</strong> “Don’t you agree the terrible evening bus schedule must change?” Ask students to name the neutral wording, complete choices, and missing private detail. Then model the revision frame: “The first question is useful because it asks one measurable thing. We revised the ranges so every realistic answer had one place.”</p>",
                "EVIDENCE": "<p>Team ten-question survey, incentive, campaign choice, role record, and visible revision plus each student's private survey-quality check and career connection. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Visible and hidden transportation work.") + flow("#4a9d2f", "Read problem · 7", "Cluster, audience, evidence.") + flow("#1f617a", "Team survey · 23", "Ten questions with accountable roles.") + flow("#e3ad19", "Incentive/campaign · 7", "One hypothetical choice and reason.") + flow("#4a9d2f", "Revise · 3", "Quality-check one question.") + flow("#1f617a", "Individual check · 5", "Quiz feedback and career connection."),
                "MONITOR": "<p><strong>CFU before release:</strong> students vote useful/not useful on the supplied pair and defend one choice. <strong>Lap 1, team minute 6:</strong> check an exact fictional audience, one need, and at least three neutral questions. <strong>Lap 2, team minute 15:</strong> check seven multiple-choice and three short-answer stems, distinct choices, and no identifiers. If a third of teams are below six usable questions, pause for a two-minute question-stem sort and reduce the default to five polished questions only for those teams; keep both question types, privacy, campaign choice, visible revision, and individual Quiz. <strong>Safe trim:</strong> skip public sharing. Protect the Quiz, one visible revision, and collection of the single team copy.</p>",
                "RESOURCES": "<p>FYF supplies the cluster and survey scenario. The CCE packet adds the privacy boundary, neutral-question models, and independent evidence route.</p>",
                "SUPPORT": "<p>Model one multiple-choice and one short-answer item. Teach the team jobs before release, monitor one criterion per lap, and require every student to complete the private check. The packet provides usable question space without four separate copies.</p>",
                "FALLBACK": "<p>A missing partner completes the shortened five-question independent route. Canvas failure uses one half-sheet per student for the four-item check. The recorder places the named team packet in the period tray; the materials lead returns pencils and closes the shared file. Do not collect student transportation stories.</p>",
            },
            2: {
                "TITLE": "Aviation Careers and Pilot Routes",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(3)(G)",
                "ALERT": "<strong>Keep every claim bounded.</strong> BLS values are May 2024 national medians. The military route is service with selection and obligation, not free flight school. JROTC is not pilot training.",
                "PREP": f'<ul><li><strong>Print:</strong> one {file_link(files["PLAN"]["id"], "four-page Action Plan")} per student only for the paper route; students retain it through Day 5. Default digital printing is zero. Project or post {file_link(files["ROUTES"]["id"], "the two-page dated reference")}; print one per table only when projection/access is not usable.</li><li><strong>Devices:</strong> one per student for the default private digital response; zero for paper. Open current <a href="https://www.faa.gov/education/about/careers-aviation-and-space">FAA careers</a>, <a href="https://www.faa.gov/licenses_certificates/airline_certification/pilotschools">pilot schools</a>, <a href="https://www.faa.gov/air-traffic-controller-qualifications">ATC qualifications</a>, <a href="https://www.bls.gov/ooh/transportation-and-material-moving/airline-and-commercial-pilots.htm">BLS pilots</a>, <a href="https://www.bls.gov/ooh/transportation-and-material-moving/air-traffic-controllers.htm">BLS ATC</a>, and <a href="https://www.bls.gov/ooh/installation-maintenance-and-repair/aircraft-and-avionics-equipment-mechanics-and-technicians.htm">BLS mechanics</a>.</li><li>Use one labeled class folder for paper plans. Keep Flight Line Fixers optional and collapsed.</li></ul>',
                "MODEL": "<p><strong>Fictional Sam model:</strong> “Sam should investigate the civilian route first because Sam wants to compare local training schedules before making a service decision. One entry step is choosing an FAA-certificated instructor or school; a Part 141 school uses an FAA-approved structured curriculum, but that does not make it universally better. A tradeoff is that training time and cost vary. Before deciding, Sam should verify certificate requirements on the FAA Become a Pilot page and ask a counselor which Irving course is currently available.” Ask students to locate the route, evidence, tradeoff, unknown, and authorized verification source.</p>",
                "EVIDENCE": "<p>Day 2 section of the final Action Plan: three-career evidence, civilian/Air Force route tradeoff, verification question, and source-based recommendation. Formative checkpoint for Minor 1.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Information Sam needs.") + flow("#4a9d2f", "Three careers · 12", "Work, preparation, national median, limitation.") + flow("#1f617a", "Pilot routes · 23", "Steps, advantage, tradeoff, source, recommendation.") + flow("#e3ad19", "Irving/JROTC boundary · 5", "Current public programs and one question.") + flow("#1f617a", "Exit · 5", "Defensible first investigation route."),
                "MONITOR": "<p><strong>CFU after the career cards:</strong> label $122,670 as May 2024 U.S. median annual wage, not local or starting pay. <strong>Lap 1, minute 10:</strong> check one exact career title, daily-work fact, preparation fact, full pay label, and source. <strong>Lap 2, pilot-route minute 12:</strong> check one entry step, one tradeoff, one unknown, and an authorized source. If students choose a route from preference alone, pause on the supplied Sam model and color-code claim/evidence/unknown. <strong>Safe trim:</strong> omit the optional Irving/JROTC discussion and turn it into the local verification question; protect the recommendation, source/date labels, and return/retention of the Day 2 plan.</p><p>Key values: commercial pilot $122,670; ATC $144,580; aircraft mechanic/service technician $78,680. All are May 2024 U.S. national medians. No route is the single right answer.</p>",
                "RESOURCES": "<p>Current Irving public CTE information lists Aviation Maintenance, Drone Engineering, and Marine JROTC at Irving High. Course access still requires current coursebook/counselor verification. Do not repeat the workbook's simulator or automotive-IBC claims as current guarantees.</p>",
                "SUPPORT": "<p>Project or post the two-page fixed reference and read one card at a time. Students write only in the final Action Plan started today. Private writing, typing, and media are equal. Do not ask students to disclose military family history or health information.</p>",
                "FALLBACK": "<p>No H&amp;L or open search is required. Flight Line Fixers asks students to observe image evidence, not diagnose an aircraft or learn real maintenance-dispatch decisions. Students save the digital plan in the named private location or place the named paper plan in the class folder; do not submit the Minor early.</p>",
            },
            3: {
                "TITLE": "Design a Classroom Airport Map",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>Equal build routes.</strong> LEGO is recommended when available, but paper and the live Canvas Lucid integration use the same checklist and grading boundary.",
                "PREP": f'<ul><li><strong>Teams:</strong> four students. Assign planner, builder, mover, and checker/recorder; combine roles in teams of three.</li><li><strong>Print:</strong> Lab pp. 1-2 once per team and p. 3 once per student today; hold p. 4 for Day 4. Default digital printing is zero. Post {file_link(files["LAB"]["id"], "the four-page Lab")} and open the annotation Assignment.</li><li><strong>Materials per team:</strong> one baseplate or one 11×17 sheet or one Lucid board; four labeled aircraft tokens; one pencil and two markers for paper; one small tray or envelope for tokens. Do not mix build routes within a team.</li><li><strong>Devices:</strong> one per student for Canvas annotation or one per team for Lucid; zero for LEGO/paper. Test <a href="{lucid_url}">the Canvas Lucid integration</a> before offering it.</li></ul>',
                "MODEL": "<p><strong>Ready model:</strong> R1 and R2 are two nonintersecting parallel runways. Taxi A connects Gates 1-2 to R1; Taxi B connects Gates 3-4 to R2. A tower marker can see both runways. The predicted conflict is where Taxi A meets the shared gate lane, so the revision adds a hold marker and a one-aircraft-at-a-time rule. <strong>Non-example:</strong> two unlabeled lines, one gate, no taxi route, no north arrow, and aircraft that must jump across the page. Ask: Which exact checklist jobs fail?</p>",
                "EVIDENCE": "<p>Team or independent map, predicted conflict, revision, readiness test, and individual design note. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Role-to-information match.") + flow("#4a9d2f", "Rules · 7", "Fictional classroom constraints.") + flow("#1f617a", "Plan · 12", "Top-down sketch and conflict prediction.") + flow("#e3ad19", "Build · 16", "LEGO, paper, or Lucid.") + flow("#4a9d2f", "Readiness · 5", "One route test and correction.") + flow("#1f617a", "Exit · 5", "Individual feature, conflict, revision."),
                "MONITOR": "<p><strong>CFU before materials:</strong> teams point to runway, taxi route, gate, tower, north arrow, and alternate route on the supplied model. <strong>Lap 1, plan minute 6:</strong> check all labels, two movement arrows, and one predicted conflict before releasing materials. <strong>Lap 2, build minute 9:</strong> check that every route physically connects and the alternate remains usable. If a third of teams begin decorating before the route works, pause materials and require the readiness checklist. <strong>Safe trim:</strong> use a flat paper model instead of finishing construction; protect the labeled sketch, conflict/revision, individual p. 3 note, five-minute readiness test, and cleanup. The six-stud LEGO gap is a classroom constraint, not an FAA rule. Do not score artistry or material access.</p>",
                "RESOURCES": "<p>The CCE model is the complete route. A live airport map may be shown only as optional context, not as the required source students must decode.</p>",
                "SUPPORT": "<p>Assign planner, recorder, mover, checker, or builder. For paper, print Lab pp. 1-2 once per team and p. 3 once per student today; hold p. 4 for Day 4. Canvas annotation/text/upload and paper remain equal.</p>",
                "FALLBACK": "<p>Independent map is equal. If Lucid fails, move directly to paper. The recorder places Lab pp. 1-2 with the labeled model and four tokens in the team tray; each student hands in or saves p. 3. Photos are optional and contain no faces or names.</p>",
            },
            4: {
                "TITLE": "Test, Communicate, and Revise",
                "SUBTITLE": "50 minutes · TEKS d(4)(A), d(1)(C)",
                "ALERT": "<strong>Classroom protocol only.</strong> Do not teach the five steps as FAA phraseology or ask students to invent real emergency, radio-failure, or separation procedures.",
                "PREP": f'<ul><li><strong>Teams/materials:</strong> return one map, four tokens, one token tray, and Lab p. 2 per four-student team; return Lab p. 4 to every student.</li><li><strong>Print:</strong> zero by default when projecting {file_link(files["CARDS"]["id"], "the one-page Scenario Cards")}; otherwise one card page per team. <strong>Devices:</strong> zero for paper/LEGO; one per team for Lucid.</li><li>Project the supplied five-step protocol and completed log below. Prepare one visible timer.</li><li>Keep the written third-scenario route ready. No student improvises a real emergency or radio-failure procedure.</li></ul>',
                "MODEL": "<p><strong>Complete classroom call:</strong> Controller: “Alpha, move from Gate 1 to the R1 hold marker by Taxi A.” Mover: “Alpha repeats: Gate 1 to R1 hold marker by Taxi A.” Controller: “Confirmed.” Recorder logs complete route/no conflict. <strong>Completed log:</strong> Goal—keep Bravo still while Alpha moves. Breakdown—both tokens entered Taxi A. Revision—add a hold marker and name the first aircraft. Evidence—second run moved one aircraft at a time. <strong>Non-example:</strong> “Plane, go over there.”</p>",
                "EVIDENCE": "<p>Three run logs or two plus written third, team revisions, individual timed iteration plan, and new-scenario response. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Find ambiguity.") + flow("#4a9d2f", "Protocol · 8", "Name, Route, Repeat, Confirm, Log.") + flow("#1f617a", "Three tests · 24", "Run, diagnose communication breakdown, revise.") + flow("#e3ad19", "Individual plan · 8", "Timed action and evidence.") + flow("#1f617a", "Exit · 5", "New blocked-route scenario."),
                "MONITOR": "<p><strong>CFU before the timer:</strong> one team identifies Name, Route, Repeat, Confirm, and Log in the supplied call. <strong>Lap 1, Run 1 minute 2:</strong> check full route language and repeat/confirm. <strong>Lap 2, Run 2 minute 2:</strong> check one aircraft held and the reason logged. <strong>Lap 3, Run 3 minute 2:</strong> check a route or sequence revision tied to the constraint. If two teams move without repeat/confirm, stop the clock and rehearse the model once. <strong>Safe trim:</strong> complete Run 3 as the written scenario. Never cut the individual p. 4 timed plan, new-scenario response, five-minute collection, or materials reset.</p>",
                "RESOURCES": "<p>The simplified classroom model supports systems thinking and communication. It does not certify real aviation safety, radio language, or operational skill.</p>",
                "SUPPORT": "<p>Speaking, moving, recording, checking, writing, text, and media are equal routes. Keep the five steps visible and chunk one run at a time.</p>",
                "FALLBACK": "<p>Use the model map and written scenarios. No team performance is required for the individual evidence. The recorder returns the map, p. 2 log, and four tokens to the tray; each student submits or saves p. 4 before devices close.</p>",
            },
            5: {
                "TITLE": "Aviation Route and Action Plan",
                "SUBTITLE": "50 minutes · TEKS d(4)(A), d(1)(C)",
                "ALERT": "<strong>Minor 1 in the 4SW assessment map.</strong> The importer protects the existing 100-point assignment in Minor Assessments (40%) and refuses to recreate or remap it.",
                "PREP": f'<ul><li>Return each named {file_link(files["PLAN"]["id"], "four-page Action Plan started on Day 2")} and Day 4 individual evidence. Post {file_link(files["RUBRIC"]["id"], "the student-visible rubric")}; default rubric printing is zero.</li><li><strong>Devices:</strong> one per student for the default private Canvas submission; zero for paper. <strong>Print:</strong> zero unless replacing a missing/damaged plan.</li><li>Open the protected private unpublished Minor Assignment. Prepare one late-save tray or the same private digital recovery route for unfinished in-class plans.</li></ul>',
                "MODEL": "<p><strong>Seven-sentence fictional model:</strong> “My current direction is aircraft mechanic because I am interested in inspecting and documenting systems. BLS reports a May 2024 U.S. median annual wage of $78,680 for aircraft mechanics and service technicians; this is not DFW starting pay. A common preparation route is an FAA-approved maintenance program, but I still need to verify the current Irving course sequence with my counselor. By Friday, I will compare the district course description with the FAA mechanic page for 20 minutes and save two labeled facts. Before my next counseling meeting, I will write one question about enrollment and bring the source. During Grade 9, I will complete the confirmed first course or use my equal backup of comparing Drone Engineering if access changes. My support is my counselor; if the course is unavailable, I will revise the plan after checking the current coursebook.” Ask students to identify source accuracy, route reasoning, three stages, support, backup, and revision condition.</p>",
                "EVIDENCE": "<p>Private direction, source evidence, three timed stages, support, obstacle, backup, revision condition, self-score, and revision. Minor 1, scored with the 16-point rubric and converted to 100 gradebook points.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Direction, not lifetime promise.") + flow("#4a9d2f", "Model and CFU · 8", "Locate every rubric job in the supplied model.") + flow("#1f617a", "Reopen evidence · 10", "Work, preparation, tradeoff, skill, source.") + flow("#e3ad19", "Three stages · 20", "Actions, timing, support, backup, revision.") + flow("#1f617a", "Self-score/submit · 7", "Revise weakest section and submit privately."),
                "MONITOR": "<p><strong>CFU after the model:</strong> students point to the three time horizons and the equal backup. <strong>Checkpoint, plan minute 7:</strong> career direction, work/preparation evidence, and full source labels are present. <strong>Checkpoint, minute 14:</strong> all three actions have a time, completion sign, and authorized support/source. <strong>Checkpoint, review minute 3:</strong> obstacle, equal backup, revision condition, self-score, and visible revision are present. If a third of students lack a rubric job, pause for a three-minute model audit. <strong>Safe trim:</strong> remove team showcases and use the model only; do not cut any rubric criterion or the final five-minute private submission. Unfinished in-class work uses the same private assignment or paper recovery tray during the next teacher-provided window, not automatic homework.</p><p>Suggested conversion after local approval: 15-16 Masters, 13-14 Meets, 12 Approaches, 10-11 Needs Improvement; below 10 follows campus policy. Score evidence and reasoning, not career preference, build quality, speaking, H&amp;L ratings, family military history, grammar unless meaning is unclear, or submission mode.</p>",
                "RESOURCES": "<p>H&amp;L browse, Xello Jobs and Employers, and eDynamic goal setting are optional after core evidence. The locked workbook App Exploration page is context only and does not prove platform completion. The assignment contains the same response jobs for students using typed or media evidence.</p>",
                "SUPPORT": "<p>The four-page plan gives each major reasoning job its own writing region without asking students to recopy the reference guide. Use speech-to-text, teacher scribe, or private media as needed.</p>",
                "FALLBACK": "<p>Missing simulation work uses the supplied model log. Canvas failure means named paper in the private tray or later upload. Students submit the plan once; the team survey and lab remain formative evidence, not extra Minor uploads. No partner, family signature, public post, or live presentation is required.</p>",
            },
        }

        day_names = {
            1: "Transportation Cluster and Survey Design",
            2: "Aviation Careers and Pilot Routes",
            3: "Design a Classroom Airport Map",
            4: "Test, Communicate, and Revise",
            5: "Aviation Route and Action Plan",
        }
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            order.append(("SubHeader", None, header_title))
            student_title = f"STUDENT: 4SW Wk3 Day {day} - {day_names[day]}"
            student_page = await common.upsert_page(
                client,
                student_title,
                common.render(
                    "4sw-wk3-student.html",
                    {"COURSE_ID": COURSE_ID, "DAY": day, "MEDIA": media[day], **contracts[day], **student[day]},
                ),
            )
            teacher_title = f"TEACHER: 4SW Wk3 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(
                client,
                teacher_title,
                common.render(
                    "4sw-wk3-teacher.html",
                    {
                        "COURSE_ID": COURSE_ID,
                        "DAY": day,
                        "STUDENT_PAGE_URL": student_page["url"],
                        **contracts[day],
                        **teacher[day],
                    },
                ),
            )
            order.extend([("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title)])
            pages[day] = {"teacher": teacher_page, "student": student_page}
            if day == 1:
                order.append(("Quiz", quiz["id"], QUIZ_TITLE))
            if day == 3:
                order.append(("Assignment", lab["id"], LAB_TITLE))
            if day == 5:
                order.append(("Assignment", plan["id"], PLAN_TITLE))

        final_items = await reconcile_module_items(client, module["id"], order)
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
        if module.get("published") or len([entry for entry in modules if entry.get("name") == MODULE_NAME]) != 1:
            raise RuntimeError(f"Final module invariant failed: published={module.get('published')}")
        if len(final_items) != 18:
            raise RuntimeError(f"Expected 18 exact module items; found {len(final_items)}")
        for day, pair in pages.items():
            for kind, page in pair.items():
                final_page = await common.api(client, "GET", f"/courses/{COURSE_ID}/pages/{page['url']}")
                if final_page.get("published"):
                    raise RuntimeError(f"Day {day} {kind} page is published")
                pair[kind] = final_page
        quiz = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
        final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
        if (
            quiz.get("published")
            or quiz.get("quiz_type") != "practice_quiz"
            or int(quiz.get("allowed_attempts") or 0) != -1
            or [entry.get("question_name") for entry in final_questions] != [spec[0] for spec in QUESTIONS]
        ):
            raise RuntimeError(f"Final practice Quiz invariant failed for {QUIZ_TITLE!r}")
        lab = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{lab['id']}")
        lab_source = await common.api(client, "GET", f"/files/{files['LAB']['id']}")
        lab_attachment = await common.api(client, "GET", f"/files/{lab['annotatable_attachment_id']}")
        required_lab_routes = {"student_annotation", "online_upload", "online_text_entry"}
        if (
            lab.get("published")
            or float(lab.get("points_possible") or 0) != 0
            or lab.get("grading_type") != "percent"
            or lab.get("omit_from_final_grade") is not True
            or not required_lab_routes.issubset(set(lab.get("submission_types") or []))
            or lab_source.get("locked") is not True
            or lab_attachment.get("locked") is not True
            or lab_attachment.get("filename") != lab_source.get("filename")
            or int(lab_attachment.get("size") or -1) != int(lab_source.get("size") or -2)
        ):
            raise RuntimeError(f"Final lab annotation invariant failed for {LAB_TITLE!r}")
        plan = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{plan['id']}")
        if (
            plan.get("published")
            or float(plan.get("points_possible") or 0) != 100
            or plan.get("assignment_group_id") != minor_group["id"]
            or plan.get("grading_type") != "points"
            or plan.get("omit_from_final_grade") is not False
            or RUBRIC_NOTE_MARKER not in (plan.get("description") or "")
        ):
            raise RuntimeError(f"Final Minor invariant failed for {PLAN_TITLE!r}")
        support_folder = await common.lock_folder_files(client, support_folder)
        for day in visual_folders:
            visual_folders[day] = await common.lock_folder_files(client, visual_folders[day])
        print(
            json.dumps(
                {
                    "module": {"id": module["id"], "published": module["published"]},
                    "quiz": {"id": quiz["id"], "published": quiz.get("published"), "quiz_type": quiz.get("quiz_type"), "allowed_attempts": quiz.get("allowed_attempts")},
                    "lab": {"id": lab["id"], "published": lab.get("published"), "submission_types": lab.get("submission_types"), "annotatable_attachment_id": lab.get("annotatable_attachment_id")},
                    "plan": {"id": plan["id"], "published": plan.get("published"), "points_possible": plan.get("points_possible"), "assignment_group_id": plan.get("assignment_group_id"), "submission_types": plan.get("submission_types"), "grading_type": plan.get("grading_type")},
                    "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
                    "visual_folders": {str(day): {"id": folder["id"], "locked": folder["locked"]} for day, folder in visual_folders.items()},
                    "files": {key: value["id"] for key, value in files.items()},
                    "visuals": {str(day): {name: value["id"] for name, value in entries.items()} for day, entries in visuals.items()},
                    "pages": {str(day): {kind: {"url": value["url"], "published": value["published"]} for kind, value in pair.items()} for day, pair in pages.items()},
                    "items": [{"position": item["position"], "type": item["type"], "title": item["title"]} for item in final_items],
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
