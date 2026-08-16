"""Build the unpublished 5SW Week 1 Architecture evidence module."""

import asyncio
import json
import re
import sys
from urllib.parse import urlencode

import httpx

import build_4sw_wk1 as common


COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/5sw/wk1"
MODULE_NAME = "5SW Wk1: Blueprint Builders — Architecture Evidence"

SAFETY_TITLE = "PRACTICE: Safety Supervisor Evidence Plan"
QUIZ_TITLE = "PRACTICE: Architecture Career Evidence Check"
QUIZ_ALIASES = ("MINOR 1: Architecture Career Evidence Check",)
ASSESSMENT_TITLE = "MINOR 1: Three-Career Architecture Comparison"
DESIGN_TITLE = "PRACTICE: Community Learning Space Concept"
REVISION_TITLE = "PRACTICE: Building Test and Revision"
PORTFOLIO_TITLE = "FORMATIVE: Architecture Evidence Portfolio"
RUBRIC_NOTE_MARKER = 'data-cce-rubric-note="cce-advisory-rubric-v1"'
WORKSHEET_FILES = {
    "SAFETY": "5sw-wk1-safety-supervisor-evidence-plan.pdf",
    "CAREERS": "5sw-wk1-three-career-evidence-comparison.pdf",
    "DESIGN": "5sw-wk1-concept-building-design.pdf",
    "REVISION": "5sw-wk1-design-test-and-revision.pdf",
    "LANDMARK": "5sw-wk1-unexpected-architecture-evidence.pdf",
    "RUBRIC": "5sw-wk1-architecture-comparison-rubric.pdf",
    "PORTFOLIO_RUBRIC": "5sw-wk1-architecture-portfolio-rubric.pdf",
}
VISUAL_FILES = {
    1: (
        "fyf-architecture-cluster-opener.jpg",
        "fyf-safety-supervisor-scenario.jpg",
        "fyf-safety-supervisor-steps.jpg",
    ),
    5: (
        "climber-city-goals.jpg",
        "fyf-unexpected-architecture-scenario.jpg",
        "fyf-unexpected-architecture-design.jpg",
        "fyf-unexpected-architecture-pitch.jpg",
    ),
}


def preflight():
    required = [
        ROOT / "build/canvas/templates/5sw-wk1-student.html",
        ROOT / "build/canvas/templates/5sw-wk1-teacher.html",
        *(ROOT / "docs/resources/worksheets" / name for name in WORKSHEET_FILES.values()),
        *(
            ASSETS / f"day{day}" / name
            for day, names in VISUAL_FILES.items()
            for name in names
        ),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"5SW Wk1 preflight missing required files: {missing}")


CONTRACTS = {
    1: {
        "TOPIC": "Career Clusters",
        "OBJECTIVE": "Students will describe how Architecture & Construction roles work together and use supplied FYF evidence to create a bounded fictional safety plan.",
        "TEKS": "d(1)(B), d(1)(C)",
        "DOL": "Completed FYF Safety Supervisor work plus one professional-boundary and cluster-role response.",
        "I_CAN": "describe how Architecture & Construction roles work together and use FYF evidence in a fictional safety plan.",
        "SHOW": "Complete the FYF Safety Supervisor work and explain one professional boundary and cluster-role connection.",
    },
    2: {
        "TOPIC": "Career Preparation",
        "OBJECTIVE": "Students will compare three careers using consistent preparation and salary evidence.",
        "TEKS": "d(2)(A), d(5)(E)",
        "DOL": "Minor 1 three-career comparison with complete source labels, preparation boundaries, recommendation, and limitation.",
        "I_CAN": "compare three careers using the same salary basis and accurate preparation evidence.",
        "SHOW": "Submit Minor 1 with all three careers, source labels, preparation boundaries, a supported recommendation, and one limitation.",
    },
    3: {
        "TOPIC": "Career Opportunities",
        "OBJECTIVE": "Students will identify how an Architecture & Construction worker uses top and front views and create a two-view concept with five spatial-design operations.",
        "TEKS": "d(1)(C)",
        "DOL": "Two-view concept, first design checkpoint, and career-role work-product explanation.",
        "I_CAN": "create top and front views and explain how an Architecture & Construction worker uses this kind of design evidence.",
        "SHOW": "Complete two views, a first design checkpoint, and one career-role work-product explanation.",
    },
    4: {
        "TOPIC": "Career Opportunities",
        "OBJECTIVE": "Students will test a concept against the brief, document one evidence-based revision, and explain which Architecture & Construction worker uses the evidence next.",
        "TEKS": "d(1)(C)",
        "DOL": "Private design submission, revision record, and next-worker work-product explanation.",
        "I_CAN": "test and revise a concept, then explain which Architecture & Construction worker uses the evidence next.",
        "SHOW": "Submit the design privately with one evidence-based revision and a next-worker work-product explanation.",
    },
    5: {
        "TOPIC": "Career Clusters",
        "OBJECTIVE": "Students will apply city-goal evidence to a novelty-building concept and explain how multiple cluster roles work together.",
        "TEKS": "d(1)(B), d(1)(C)",
        "DOL": "Individual city-goal decision, three-role cluster synthesis, and formative private portfolio.",
        "I_CAN": "use city goals to shape a novelty-building concept and explain how three cluster roles work together.",
        "SHOW": "Record one city-goal decision, explain three collaborating roles, and submit the formative portfolio privately.",
    },
}


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    matches = [module for module in modules if module["name"] == MODULE_NAME]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one module named {MODULE_NAME!r}; found {len(matches)}")
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
    for position, (kind, key, title) in enumerate(expected, 1):
        matches = [item for item in remaining if module_item_matches(item, kind, key, title)]
        if matches:
            item = matches[0]
            for duplicate in matches[1:]:
                await common.api(
                    client,
                    "DELETE",
                    f"/courses/{COURSE_ID}/modules/{module_id}/items/{duplicate['id']}",
                )
                remaining.remove(duplicate)
        else:
            item = await upsert_item(client, module_id, kind, key, title)
        remaining = [entry for entry in remaining if entry.get("id") != item.get("id")]
        await common.api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            data={
                "module_item[title]": title,
                "module_item[position]": position,
                "module_item[published]": "false",
            },
        )
    for stale in remaining:
        await common.api(
            client,
            "DELETE",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{stale['id']}",
        )
    final = sorted(
        await common.paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items"),
        key=lambda item: item.get("position") or 0,
    )
    if len(final) != len(expected):
        raise RuntimeError(f"Expected {len(expected)} exact module items; found {len(final)}")
    for position, (item, (kind, key, title)) in enumerate(zip(final, expected), 1):
        if (
            item.get("position") != position
            or not module_item_matches(item, kind, key, title)
            or item.get("title") != title
            or item.get("published")
        ):
            raise RuntimeError(
                f"Module item invariant failed at position {position}: "
                f"type={item.get('type')}, title={item.get('title')}, published={item.get('published')}"
            )
    return final


QUESTIONS = [
    (
        "Q1 - salary label",
        "The evidence guide lists $96,690 for architects. What does that figure mean?",
        "May 2024 U.S. median annual wage from BLS",
        ["DFW starting salary", "Guaranteed first-year pay", "Maximum salary in Texas"],
        "Correct. Keep occupation, May 2024, U.S., median, and BLS with the figure.",
        "The source does not label this figure DFW, starting, maximum, or guaranteed pay.",
    ),
    (
        "Q2 - compare all three",
        "Which order correctly ranks the three May 2024 U.S. medians from highest to lowest?",
        "Architect, Drafter, Interior Designer",
        ["Drafter, Architect, Interior Designer", "Interior Designer, Drafter, Architect", "All three have the same median"],
        "Correct. The evidence guide lists $96,690, $65,380, and $63,490.",
        "Reopen the fixed guide and compare the same salary column for all three careers.",
    ),
    (
        "Q3 - licensure structure",
        "Which statement stays within the current architecture-registration evidence?",
        "Requirements vary, but a common structure includes approved education, documented experience, and examination.",
        ["Every architect follows exactly seven years of school.", "Passing one software course creates an architecture license.", "Every drafter must complete the ARE."],
        "Correct. The exact route and timing vary by jurisdiction and prior education.",
        "Do not replace a variable registration process with one universal timeline.",
    ),
    (
        "Q4 - design boundary",
        "What does a Grade 8 Tinkercad or paper concept prove?",
        "It shows spatial choices and whether visible brief requirements were addressed.",
        ["It proves the building is structurally safe.", "It proves code and accessibility compliance.", "It authorizes construction."],
        "Correct. The concept is evidence of design thinking, not construction approval.",
        "Structural, code, accessibility, cost, and constructability review require qualified professionals.",
    ),
]


async def upsert_quiz(client):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    matches = [quiz for quiz in quizzes if quiz.get("title") == QUIZ_TITLE or quiz.get("title") in QUIZ_ALIASES]
    exact = [quiz for quiz in matches if quiz.get("title") == QUIZ_TITLE]
    found = exact[0] if exact else (matches[0] if matches else None)
    for duplicate in matches:
        if found and duplicate["id"] == found["id"]:
            continue
        await common.api(client, "DELETE", f"/courses/{COURSE_ID}/quizzes/{duplicate['id']}")
    data = {
        "quiz[title]": QUIZ_TITLE,
        "quiz[description]": "<p>Ungraded, unlimited-retry practice. Use the feedback to repair salary, preparation, and design-boundary labels.</p>",
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
    for prior in existing:
        if prior.get("question_name") not in desired_names:
            await common.api(
                client,
                "DELETE",
                f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior['id']}",
            )
    existing = [prior for prior in existing if prior.get("question_name") in desired_names]
    unique = []
    seen_names = set()
    for prior in existing:
        name = prior.get("question_name")
        if name in seen_names:
            await common.api(
                client,
                "DELETE",
                f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior['id']}",
            )
        else:
            seen_names.add(name)
            unique.append(prior)
    existing = unique
    for position, (name, prompt, correct, wrong, yes, no) in enumerate(QUESTIONS, 1):
        prior = next((question for question in existing if question.get("question_name") == name), None)
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
            f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior['id']}"
            if prior
            else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        )
        await common.api(client, "PUT" if prior else "POST", path, json=payload)
    expected = [name for name, *_rest in QUESTIONS]
    final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    final_by_name = {entry.get("question_name"): entry for entry in final_questions}
    if set(final_by_name) != set(expected) or len(final_questions) != len(expected):
        actual = [entry.get("question_name") for entry in final_questions]
        raise RuntimeError(f"Architecture Quiz mismatch: expected {expected}, found {actual}")
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
        raise RuntimeError(f"Architecture Quiz mismatch: expected {expected}, found {actual}")
    final = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
    if final.get("published") or final.get("quiz_type") != "practice_quiz" or int(final.get("allowed_attempts") or 0) != -1:
        raise RuntimeError(f"Practice Quiz invariant failed for {QUIZ_TITLE!r}")
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
    matches = [entry for entry in assignments if entry.get("name") == ASSESSMENT_TITLE]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one existing mapped Minor assignment named {ASSESSMENT_TITLE!r}; found {len(matches)}"
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


async def update_minor_assignment(client, found, group, description, attachment_id):
    rubric_note = re.search(
        r'<div data-cce-rubric-note="cce-advisory-rubric-v1".*?</div>',
        found.get("description") or "",
        flags=re.I | re.S,
    )
    if rubric_note is None:
        raise RuntimeError(f"Mapped Minor is missing required rubric conversion note: {ASSESSMENT_TITLE!r}")
    data = {
        "assignment[name]": ASSESSMENT_TITLE,
        "assignment[description]": description + rubric_note.group(0),
        "assignment[published]": "false",
        "assignment[points_possible]": "100",
        "assignment[grading_type]": "points",
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
    assignment = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignment['id']}")
    if (
        assignment.get("published")
        or float(assignment.get("points_possible") or 0) != 100
        or assignment.get("assignment_group_id") != group["id"]
        or assignment.get("grading_type") != "points"
        or assignment.get("omit_from_final_grade") is not False
        or RUBRIC_NOTE_MARKER not in (assignment.get("description") or "")
    ):
        raise RuntimeError(f"Minor invariant failed after update for {ASSESSMENT_TITLE!r}")
    return await assert_annotation_assignment(client, assignment, attachment_id, mapped=True)


async def assert_annotation_assignment(client, assignment, source_attachment_id, *, mapped=False):
    assignment = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignment['id']}")
    source_file = await common.api(client, "GET", f"/files/{source_attachment_id}")
    annotation_attachment_id = int(assignment.get("annotatable_attachment_id") or 0)
    annotation_file = await common.api(client, "GET", f"/files/{annotation_attachment_id}") if annotation_attachment_id else {}
    if annotation_file and not annotation_file.get("locked"):
        annotation_file = await common.api(client, "PUT", f"/files/{annotation_attachment_id}", data={"locked": "true"})
    required_routes = {"student_annotation", "online_upload", "online_text_entry"}
    failures = {
        "published": assignment.get("published") is not False,
        "points_possible": float(assignment.get("points_possible") or 0) != (100 if mapped else 0),
        "grading_type": assignment.get("grading_type") != ("points" if mapped else "percent"),
        "omit_from_final_grade": assignment.get("omit_from_final_grade") is not (False if mapped else True),
        "submission_types": not required_routes.issubset(set(assignment.get("submission_types") or [])),
        "annotatable_attachment_missing": not annotation_attachment_id,
        "source_file_locked": source_file.get("locked") is not True,
        "annotation_file_locked": annotation_file.get("locked") is not True,
        "annotation_filename": annotation_file.get("filename") != source_file.get("filename"),
        "annotation_size": int(annotation_file.get("size") or -1) != int(source_file.get("size") or -2),
    }
    failed = [name for name, value in failures.items() if value]
    if failed:
        raise RuntimeError(f"Annotation Assignment invariant failed for {assignment.get('name')!r}: {failed}")
    return assignment


async def upsert_annotation_assignment(client, title, description, attachment_id):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == title]
    if len(matches) > 1:
        raise RuntimeError(f"Duplicate assignments named {title!r}: {[entry['id'] for entry in matches]}")
    found = matches[0] if matches else None
    data = {
        "assignment[name]": title,
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
    return await assert_annotation_assignment(client, assignment, attachment_id)


def image_tag(file_id, alt):
    return (
        f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" '
        'style="display:block;width:100%;max-width:700px;height:auto;margin:14px auto;border:1px solid #ddd" '
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
        support_path = "course files/CCR Materials/5SW/Wk1"
        support_folder = await common.ensure_folder(client, support_path)
        files = {
            key: await common.upload(client, ROOT / "docs/resources/worksheets" / name, support_path)
            for key, name in WORKSHEET_FILES.items()
        }

        visual_files = {}
        visual_specs = {
            1: [
                ("cluster", "fyf-architecture-cluster-opener.jpg"),
                ("scenario", "fyf-safety-supervisor-scenario.jpg"),
                ("steps", "fyf-safety-supervisor-steps.jpg"),
            ],
            5: [
                ("city", "climber-city-goals.jpg"),
                ("unexpected", "fyf-unexpected-architecture-scenario.jpg"),
                ("design", "fyf-unexpected-architecture-design.jpg"),
                ("pitch", "fyf-unexpected-architecture-pitch.jpg"),
            ],
        }
        visual_folders = {}
        for day, names in visual_specs.items():
            folder_path = f"course files/CCR Materials/5SW/Wk1/Day {day} Visuals"
            visual_folders[day] = await common.ensure_folder(client, folder_path)
            for key, name in names:
                visual_files[key] = await common.upload(client, ASSETS / f"day{day}" / name, folder_path)

        support_folder = await common.lock_folder_files(client, support_folder)
        for day, folder in list(visual_folders.items()):
            visual_folders[day] = await common.lock_folder_files(client, folder)

        quiz = await upsert_quiz(client)
        comparison = await update_minor_assignment(
            client,
            mapped_minor,
            minor_group,
            "<p>Submit the completed three-career comparison by Canvas annotation, upload, typed labeled response, or paper. Use the student-visible 16-point rubric; Tinkercad, drawing, and public speaking are not part of this grade.</p>",
            files["CAREERS"]["id"],
        )
        safety = await upsert_annotation_assignment(
            client,
            SAFETY_TITLE,
            "<p>Annotate or upload the fictional Safety Supervisor plan, type labeled responses, or use paper. This is not real commercial-diving or construction guidance.</p>",
            files["SAFETY"]["id"],
        )
        design = await upsert_annotation_assignment(
            client,
            DESIGN_TITLE,
            "<p>Submit the two-view concept by Canvas annotation, upload, text, or paper. Tinkercad and paper routes use the same evidence criteria.</p>",
            files["DESIGN"]["id"],
        )
        revision = await upsert_annotation_assignment(
            client,
            REVISION_TITLE,
            "<p>Submit the design image or paper equivalent with the test-and-revision record. Tool speed and artistic polish are not scored.</p>",
            files["REVISION"]["id"],
        )
        portfolio = await common.upsert_assignment(
            client,
            PORTFOLIO_TITLE,
            "<p>Submit the Day 3 concept evidence, Day 4 revision evidence, and Day 5 individual synthesis by upload, text, media recording, or paper. The already graded Day 2 Minor remains referenced in place and is not reuploaded. This is formative feedback, not a Week 1 Major.</p>",
            ["online_upload", "online_text_entry", "media_recording"],
        )

        urls = {
            "safety": f"/courses/{COURSE_ID}/assignments/{safety['id']}",
            "quiz": f"/courses/{COURSE_ID}/quizzes/{quiz['id']}",
            "comparison": f"/courses/{COURSE_ID}/assignments/{comparison['id']}",
            "design": f"/courses/{COURSE_ID}/assignments/{design['id']}",
            "revision": f"/courses/{COURSE_ID}/assignments/{revision['id']}",
            "portfolio": f"/courses/{COURSE_ID}/assignments/{portfolio['id']}",
        }
        link, step, flow = common.file_link, common.step, common.flow
        media = {
            1: image_tag(visual_files["cluster"]["id"], "Find Your Future Architecture and Construction cluster opener")
            + image_tag(visual_files["scenario"]["id"], "Safety Supervisor fictional underwater research lab scenario")
            + image_tag(visual_files["steps"]["id"], "Safety Supervisor workbook planning steps"),
            2: '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:18px 0">'
            '<section style="border:1px solid #bad4df;border-radius:10px;padding:14px"><h3 style="margin-top:0;color:#1f617a">Architect</h3><p><strong>May 2024 U.S. median:</strong> $96,690</p><p><strong>Common route:</strong> degree requirements vary by jurisdiction; licensure commonly includes education, documented experience, and examination.</p><p><strong>Work product:</strong> plans and design documents.</p></section>'
            '<section style="border:1px solid #bad4df;border-radius:10px;padding:14px"><h3 style="margin-top:0;color:#1f617a">Drafter</h3><p><strong>May 2024 U.S. median:</strong> $65,380</p><p><strong>Common route:</strong> education after high school is common; preparation varies by drafting specialty and employer.</p><p><strong>Work product:</strong> technical drawings and models.</p></section>'
            '<section style="border:1px solid #bad4df;border-radius:10px;padding:14px"><h3 style="margin-top:0;color:#1f617a">Interior Designer</h3><p><strong>May 2024 U.S. median:</strong> $63,490</p><p><strong>Common route:</strong> a bachelor\'s degree is typical; title or practice rules vary by jurisdiction.</p><p><strong>Work product:</strong> functional interior plans and specifications.</p></section>'
            '</div><p style="font-size:14px;color:#52616b"><strong>Source basis for all three cards:</strong> U.S. Bureau of Labor Statistics Occupational Outlook Handbook, May 2024 median annual wages. Use the linked teacher sources for the full current profiles.</p>',
            3: "",
            4: "",
            5: image_tag(visual_files["city"]["id"], "City of Hollow Bend project summary, four city goals, and three novelty-building examples")
            + image_tag(visual_files["unexpected"]["id"], "Unexpected Architecture fictional city-council scenario")
            + image_tag(visual_files["design"]["id"], "Unexpected Architecture brainstorming and two-view design directions")
            + image_tag(visual_files["pitch"]["id"], "Unexpected Architecture pitch and feedback directions"),
        }

        student = {
            1: {
                "TITLE": "Cluster Roles and Safety Supervisor",
                "PURPOSE": "Describe how cluster roles work together and use supplied evidence in a fictional hazard plan.",
                "TODAY": "<ul><li>sort four current ACE pathways;</li><li>match hazards and evidence categories;</li><li>design a labeled fictional plan;</li><li>name a professional boundary.</li></ul>",
                "READY": f'<p><strong>Default route:</strong> read FYF pp. 171-173, then use <a href="{urls["safety"]}">the Canvas annotation activity</a> as your individual response home. Use {link(files["SAFETY"]["id"], "the three-page paper route")} only when needed. Complete one response surface, not both.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> hazard = something that could cause harm · control = a way to reduce risk · boundary = what a student plan cannot prove.</p><p><strong>Use this frame:</strong> The scenario shows ___. Our plan uses ___ because ___. A qualified professional would still need to ___.</p></div>',
                "STEPS": step(1, "Read the boundary", "<p>This is not real diving or construction guidance.</p>")
                + step(2, "Match evidence", "<p>Connect scenario hazards to people, environment, tools, movement, and emergency-planning categories.</p>")
                + step(3, "Plan and map", "<p>Write five evidence-linked rules and label the dedicated work-area map.</p>")
                + step(4, "Connect careers", "<p>Name one worker contribution and how it connects to another role.</p>"),
                "EXIT": "<p>Name a career, describe its work in this scenario, and connect it to another cluster role.</p>",
                "DONE": "<ul><li>five evidence-linked rules;</li><li>four equipment/person categories;</li><li>readable map;</li><li>professional boundary;</li><li>career connection.</li></ul>",
                "SUPPORT": "<p>hazard = peligro · evidence = evidencia · qualified professional = profesional calificado · safe zone = zona segura.</p>",
                "FALLBACK": "<p>The images, adjacent text, and packet are the full independent route. H&amp;L and open search are not required.</p>",
            },
            2: {
                "TITLE": "Compare Career Preparation and Pay",
                "PURPOSE": "Compare three careers using one dated source basis and accurate preparation boundaries.",
                "TODAY": "<ul><li>keep labels with salary figures;</li><li>compare preparation;</li><li>rank all three medians;</li><li>recommend with two evidence details.</li></ul>",
                "READY": f'<p><strong>Digital route:</strong> use the three evidence cards below and <a href="{urls["comparison"]}">open Minor 1</a>. Use {link(files["CAREERS"]["id"], "the four-page paper or enlarged route")} only when needed. Open {link(files["RUBRIC"]["id"], "the student-visible Minor 1 rubric")} before you begin.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Keep these labels with every pay figure:</strong> occupation · May 2024 · United States · median · BLS.</p><p><strong>Use this frame:</strong> I recommend ___ for Jordan because the median is ___ and the preparation usually includes ___. One limitation is ___.</p></div>',
                "STEPS": step(1, "Read the salary label", "<p>Every figure is a May 2024 U.S. median from BLS. It is not DFW, starting, or guaranteed pay.</p>")
                + step(2, "Compare preparation", "<p>Separate education, documented experience, examination, and registration boundaries.</p>")
                + step(3, "Recommend", "<p>Cite one salary figure and one preparation difference for fictional Jordan.</p>")
                + step(4, "Submit the Minor", f'<p><a href="{urls["comparison"]}">Submit the comparison privately</a>. Use <a href="{urls["quiz"]}">the optional repair Quiz</a> only if your teacher assigns it after submission.</p>'),
                "EXIT": "<p>Rank all three medians, then explain why salary alone cannot decide fit.</p>",
                "DONE": "<ul><li>three career rows;</li><li>three salary labels;</li><li>preparation difference;</li><li>supported recommendation;</li><li>one limitation.</li></ul>",
                "SUPPORT": "<p>median = mediana · preparation = preparación · experience = experiencia · examination = examen.</p>",
                "FALLBACK": "<p>The fixed guide replaces live research. Xello-local evidence is optional and stays in its separately labeled field.</p>",
            },
            3: {
                "TITLE": "Two-View Concept Design",
                "PURPOSE": "Create top and front views and explain how a worker uses this kind of design evidence.",
                "TODAY": "<ul><li>choose Canvas or paper;</li><li>practice five spatial operations;</li><li>draw top and front views;</li><li>explain the related work product.</li></ul>",
                "READY": f'<p>Open {link(files["DESIGN"]["id"], "the four-page concept route")} or <a href="{urls["design"]}">the Canvas annotation activity</a>. If your teacher has opened a tested Tinkercad Classroom, you may use the class code and nickname. Do not create a new personal account.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Design labels:</strong> top view · front view · entrance · window · purposeful feature · user need.</p><p><strong>Use this frame:</strong> A ___ would use this concept to ___. The labeled ___ helps that worker understand ___.</p></div>',
                "STEPS": step(1, "Read the fictional brief", "<p>Design a small community learning space. This is not a construction-ready plan.</p>")
                + step(2, "Practice five operations", "<p>Place, resize, align, group, and hole/subtract. On paper, draw, measure, align, combine, and mark openings.</p>")
                + step(3, "Draw two views", "<p>Use the dedicated top-view and front-view pages. Label the user, entrance, windows, roof, and purposeful feature.</p>")
                + step(4, "Begin and save", "<p>Build the main footprint and walls or complete the equal paper base.</p>"),
                "EXIT": "<p>Name one worker who uses a more advanced design and what that worker produces or decides.</p>",
                "DONE": "<ul><li>two readable views;</li><li>all brief labels;</li><li>first design checkpoint;</li><li>one user-centered choice;</li><li>career-role evidence.</li></ul>",
                "SUPPORT": "<p>place = colocar · resize = cambiar tamaño · align = alinear · group = agrupar · opening = abertura.</p>",
                "FALLBACK": "<p>The paper route has the same requirements and score. Tool speed, device access, and art polish are not graded.</p>",
            },
            4: {
                "TITLE": "Test, Revise, and Submit",
                "PURPOSE": "Test a concept against the brief and document one evidence-based revision.",
                "TODAY": "<ul><li>set one priority;</li><li>complete visible requirements;</li><li>test one choice;</li><li>revise and submit privately.</li></ul>",
                "READY": f'<p>Open {link(files["REVISION"]["id"], "the three-page revision record")} or <a href="{urls["revision"]}">the Canvas activity</a>. Continue on the same design surface you used on Day 3.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Revision jobs:</strong> original choice · evidence noticed · change made · expected improvement · next worker.</p><p><strong>Use this frame:</strong> I noticed ___. I changed ___ to ___ because ___. Next, a ___ would use this evidence to ___.</p></div>',
                "STEPS": step(1, "Set a priority", "<p>Choose complete, fix, or clarify from the requirement table.</p>")
                + step(2, "Use the checkpoints", "<p>Footprint/walls/roof; entrance/windows; purposeful feature and labels.</p>")
                + step(3, "Test and revise", "<p>Record the original choice, evidence observed, revision, and why it should help.</p>")
                + step(4, "Submit privately", "<p>Upload the model image, use the teacher-visible saved model, or submit the paper route.</p>"),
                "EXIT": "<p>Name a worker who contributes next and one limit of this Grade 8 concept.</p>",
                "DONE": "<ul><li>requirements audited;</li><li>test evidence;</li><li>specific revision;</li><li>private submission;</li><li>career and limit explanation.</li></ul>",
                "SUPPORT": "<p>test = probar · evidence = evidencia · revise = revisar · limitation = limitación.</p>",
                "FALLBACK": "<p>If export fails, the teacher-visible Classroom model plus the revision record is temporary evidence. Paper remains equal.</p>",
            },
            5: {
                "TITLE": "Unexpected Architecture and Synthesis",
                "PURPOSE": "Use city-goal evidence in a novelty concept and explain how three cluster roles work together.",
                "TODAY": "<ul><li>choose two city goals;</li><li>contribute to front and side views;</li><li>give or record a short explanation;</li><li>complete the private portfolio.</li></ul>",
                "READY": f'<p><strong>Default route:</strong> use FYF pp. 182-184 in your workbook. Use {link(files["LANDMARK"]["id"], "the two-page individual fallback")} when the workbook is unavailable or you need that route. Open {link(files["PORTFOLIO_RUBRIC"]["id"], "the one-page formative feedback guide")} before submitting.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>City goals:</strong> show city identity · attract visitors · support local growth · spark interest in design.</p><p><strong>Use this frame:</strong> We chose ___ and ___. The ___ contributes ___, while the ___ contributes ___. Together, these roles ___.</p></div>',
                "STEPS": step(1, "Read the city goals", "<p>Choose two goals from the licensed brief. A memorable shape must still serve users.</p>")
                + step(2, "Build the firm concept", "<p>Draw front and side views, label evidence, and record your individual contribution.</p>")
                + step(3, "Pitch or explain", "<p>Use a one-minute paired, written, or private recorded route. Public speaking is formative.</p>")
                + step(4, "Submit the portfolio", f'<p><a href="{urls["portfolio"]}">Submit privately</a>: Day 3 concept evidence, Day 4 revision evidence, and your Day 5 individual synthesis. Reference the graded Day 2 Minor in place; do not upload it again.</p>'),
                "EXIT": "<p>Explain how three distinct roles work together and preserve one Day 2 source label.</p>",
                "DONE": "<ul><li>two city goals;</li><li>individual contribution;</li><li>three role explanations;</li><li>one correctly labeled fact referenced from Day 2;</li><li>Day 3-5 evidence submitted privately.</li></ul>",
                "SUPPORT": "<p>city goal = meta de la ciudad · contribution = contribución · role = función · source label = etiqueta de fuente.</p>",
                "FALLBACK": "<p>Create a solo concept or analyze the supplied model. No group, live pitch, H&amp;L favorite, or eDynamic completion is required.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Cluster Roles and Safety Supervisor",
                "SUBTITLE": "50 minutes · TEKS d(1)(B), d(1)(C)",
                "ALERT": "<strong>Fictional and non-operational.</strong> Student plans are never commercial-diving, emergency, engineering, or construction guidance.",
                "PREP": f'<ul><li><strong>Default:</strong> one FYF workbook and one Canvas-capable device per student, one projector, zero prints. FYF pp. 171-173 supply the scenario; the Canvas annotation is each student\'s response home.</li><li><strong>Paper:</strong> one {link(files["SAFETY"]["id"], "three-page packet")} per student and one collection tray per class.</li><li>Partners check evidence for two minutes; every student keeps and submits an individual response.</li><li>Review the current MacArthur ACE labels: Architecture, Construction, Engineering, Welding.</li></ul>',
                "MODEL": '<div style="border:1px solid #bad4df;border-radius:8px;padding:14px 18px;background:#f2f8fb"><p><strong>Ready-to-project example:</strong> The scenario shows poor visibility and equipment-failure hazards. The plan marks an exit, surface-support station, and safe zone. A qualified supervisor would approve the actual controls and decide when work must stop. An architect could organize the space; a construction manager could coordinate workers and sequencing.</p><p><strong>Non-example:</strong> “Set the tank to 80% and keep working” invents an operational procedure the evidence does not support.</p></div>',
                "EVIDENCE": "<p>Five evidence-linked rules, equipment/person categories, readable map, professional boundary, and career connection. Formative.</p>",
                "FLOW": flow("#5a2d91", "Notice · 5", "One room design decision.") + flow("#4a9d2f", "Cluster · 10", "Roles and current ACE pathways.") + flow("#1f617a", "Evidence plan · 25", "Rules, categories, map, boundary.") + flow("#e3ad19", "Peer check · 5", "Evidence and readability.") + flow("#1f617a", "Exit · 5", "Career work and role connection."),
                "MONITOR": '<ul><li><strong>CFU at minute 8:</strong> students name one hazard, one evidence category, and one job that could respond. If fewer than four of five sampled students separate the hazard from the job, project the supplied model.</li><li><strong>Lap 1, minutes 15-20:</strong> look for rules tied to supplied evidence, not invented settings.</li><li><strong>Lap 2, minutes 28-34:</strong> check the map for exit, surface support, and safe-zone labels plus the qualified-professional boundary. If more than one-third prescribe procedures, pause and contrast the model with the non-example.</li><li><strong>Trim:</strong> skip whole-group sharing. Protect the final five-minute career connection, private submission, and tray collection.</li></ul>',
                "RESOURCES": '<p><a href="https://www.osha.gov/commercial-diving">OSHA commercial diving</a> supports the boundary; the student task uses the fictional CCE evidence categories, not operational procedures.</p>',
                "SUPPORT": "<p>Provide read-aloud, bilingual labels, typing, dictation, annotation, or paper. The map has a dedicated full page.</p>",
                "FALLBACK": "<p>No open search, H&amp;L login, partner, or drawing skill is required.</p>",
            },
            2: {
                "TITLE": "Compare Career Preparation and Pay",
                "SUBTITLE": "50 minutes · TEKS d(2)(A), d(5)(E)",
                "ALERT": "<strong>One evidence basis.</strong> May 2024 U.S. medians are not DFW, starting, maximum, or guaranteed pay.",
                "PREP": f'<ul><li><strong>Default:</strong> one device per student, one projector, zero prints. Post {link(files["CAREERS"]["id"], "the fixed evidence guide")} and {link(files["RUBRIC"]["id"], "the Minor 1 rubric")}.</li><li><strong>Paper:</strong> one four-page comparison and one two-page rubric per student, plus one collection tray per class.</li><li>The Quiz is optional repair/retry after Minor submission; it is not another required DOL.</li></ul>',
                "MODEL": '<div style="border:1px solid #bad4df;border-radius:8px;padding:14px 18px;background:#f2f8fb"><p><strong>Jordan model:</strong> I recommend drafter as the first career to investigate. The BLS May 2024 U.S. median annual wage is $65,380, which ranks second of the three. An associate\'s degree is typical, although certificate or diploma routes also exist. Architect ranks first at $96,690 but commonly requires a longer jurisdiction-specific route that usually includes education, documented experience, and examination. Interior designer ranks third at $63,490 and typically requires a bachelor\'s degree. Salary alone cannot show Jordan\'s interests, local openings, or starting pay.</p></div>',
                "EVIDENCE": "<p><strong>Minor 1 in the 5SW assessment map:</strong> three careers, preparation boundaries, salary comparison, limitation, and Jordan recommendation. The protected Assignment remains worth 100 points in Minor Assessments (40%) and unpublished for teacher cloning.</p>",
                "FLOW": flow("#5a2d91", "Labels · 5", "Unsupported versus supported claim.") + flow("#4a9d2f", "Model · 8", "Jordan response and evidence labels.") + flow("#1f617a", "Compare · 22", "Three fixed career rows.") + flow("#e3ad19", "Recommend · 10", "Salary plus preparation.") + flow("#1f617a", "Submit · 5", "Minor 1; optional repair later."),
                "MONITOR": '<ul><li><strong>CFU at minute 8:</strong> students label $96,690 as architect, May 2024, U.S., median annual wage, BLS. Reteach if any label is missing in three of five samples.</li><li><strong>Lap 1, minutes 15-22:</strong> verify all three preparation routes retain “typical,” “common,” or jurisdiction limits.</li><li><strong>Lap 2, minutes 28-35:</strong> check the rank, difference, and Jordan evidence before students recommend. Different recommendations can earn full credit.</li><li><strong>Pivot:</strong> give students the complete model and ask them to color-code salary, preparation, and limitation before drafting their own response.</li><li><strong>Trim:</strong> skip partner share and the optional Quiz. Protect the rubric self-check and Minor submission.</li></ul>',
                "RESOURCES": '<p><a href="https://www.bls.gov/ooh/architecture-and-engineering/architects.htm">BLS Architects</a> · <a href="https://www.bls.gov/ooh/architecture-and-engineering/drafters.htm">BLS Drafters</a> · <a href="https://www.bls.gov/ooh/arts-and-design/interior-designers.htm">BLS Interior Designers</a> · <a href="https://www.ncarb.org/become-architect/earn-license">NCARB licensure</a></p>',
                "SUPPORT": "<p>Read one career at a time. Preparation and final reasoning receive separate full-width fields.</p>",
                "FALLBACK": "<p>The guide is the complete no-login route. Xello-local data is optional and separately labeled; H&amp;L is not required.</p>",
            },
            3: {
                "TITLE": "Two-View Concept Design",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>Canvas and paper are ready now.</strong> Tinkercad is an optional extension only after district approval and a tested teacher-managed Classroom. Do not improvise student account creation.",
                "PREP": f'<ul><li><strong>Default:</strong> one device per student, one projector, zero prints; post {link(files["DESIGN"]["id"], "the four-page concept route")} and annotation activity.</li><li><strong>Paper:</strong> one four-page packet, one pencil, and one ruler per student; one collection tray per class.</li><li>If enabling Tinkercad, test Safe Mode, the class-code and teacher-provided nickname route, saving, and Chromebook performance before class. Paper remains equal.</li></ul>',
                "MODEL": '<div style="border:1px solid #bad4df;border-radius:8px;padding:14px 18px;background:#f2f8fb"><svg viewBox="0 0 700 260" role="img" aria-label="Top and front view model of a small community learning space" style="width:100%;height:auto"><rect x="40" y="42" width="270" height="170" fill="#fff" stroke="#24323d" stroke-width="4"/><rect x="150" y="162" width="52" height="50" fill="#fff8e7" stroke="#24323d" stroke-width="3"/><rect x="70" y="70" width="90" height="55" fill="#d9edf5" stroke="#1f617a" stroke-width="3"/><rect x="205" y="70" width="72" height="105" rx="36" fill="#e5f1dd" stroke="#4a9d2f" stroke-width="3"/><text x="40" y="28" font-size="20" font-weight="700">TOP VIEW</text><text x="76" y="102" font-size="16">learning area</text><text x="154" y="196" font-size="15">entrance</text><text x="218" y="118" font-size="15">quiet pod</text><rect x="390" y="82" width="270" height="130" fill="#fff" stroke="#24323d" stroke-width="4"/><polygon points="390,82 525,28 660,82" fill="#e5f1dd" stroke="#24323d" stroke-width="4"/><rect x="500" y="152" width="48" height="60" fill="#fff8e7" stroke="#24323d" stroke-width="3"/><rect x="420" y="110" width="52" height="34" fill="#d9edf5" stroke="#1f617a" stroke-width="3"/><rect x="575" y="110" width="52" height="34" fill="#d9edf5" stroke="#1f617a" stroke-width="3"/><text x="390" y="28" font-size="20" font-weight="700">FRONT VIEW</text><text x="425" y="133" font-size="15">window</text><text x="503" y="186" font-size="15">door</text></svg><p><strong>Model explanation:</strong> An architect could use the two views to communicate layout and exterior intent. The labeled entrance helps the team understand how users enter; it does not prove code, accessibility, structural safety, or construction readiness.</p></div>',
                "EVIDENCE": "<p>Top and front views, first design checkpoint, user-centered choice, and career-role explanation. Formative.</p>",
                "FLOW": flow("#5a2d91", "Brief · 5", "Fictional community space.") + flow("#4a9d2f", "Choose surface · 5", "Canvas, paper, or enabled Tinkercad.") + flow("#1f617a", "Spatial operations · 15", "Five digital or paper actions.") + flow("#e3ad19", "Concept · 20", "Two views and first checkpoint.") + flow("#1f617a", "Exit · 5", "Career product or decision."),
                "MONITOR": '<ul><li><strong>CFU at minute 8:</strong> students point to what top and front views show differently.</li><li><strong>Checkpoint at minute 15:</strong> every student has a surface and the main footprint. Start the paper route immediately after a failed join.</li><li><strong>Lap 1, minutes 18-25:</strong> check top/front orientation and entrance/window labels.</li><li><strong>Lap 2, minutes 30-38:</strong> require one purposeful feature and one user need before tool polish.</li><li><strong>Trim:</strong> cut the fifth operation demonstration, not the two views, checkpoint, or career-role exit. Collect paper in the class tray at minute 45.</li></ul>',
                "RESOURCES": '<p><a href="https://www.autodesk.com/company/legal-notices-trademarks/privacy-statement/childrens-privacy-statement">Autodesk children\'s privacy statement</a>. Verify current district approval and student join directions before class.</p>',
                "SUPPORT": "<p>Use starter model, grid paper, enlarged print, trackpad directions, typing, dictation, or teacher scribe.</p>",
                "FALLBACK": "<p>The paper route begins immediately after a failed join; it is not extra work or a lower score.</p>",
            },
            4: {
                "TITLE": "Test, Revise, and Submit",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>Concept boundary.</strong> The product does not prove structural safety, code/accessibility compliance, cost, or construction readiness.",
                "PREP": f'<ul><li><strong>Default:</strong> one device and retained Day 3 concept per student, one projector, zero prints; open the private submission and post {link(files["REVISION"]["id"], "the three-page revision record")}.</li><li><strong>Paper:</strong> one three-page record per student, the retained design, pencils/rulers as needed, and one collection tray per class.</li><li>If using optional Tinkercad, open the tested Classroom and verify the teacher-visible saved-model or tested export route.</li></ul>',
                "MODEL": '<div style="border:1px solid #bad4df;border-radius:8px;padding:14px 18px;background:#f2f8fb"><p><strong>Complete revision model:</strong> Original choice: the entrance opened directly into the quiet pod. Test evidence: the labeled user path crossed the quiet space. Revision: move the entrance beside the learning area and add a short divider. Expected improvement: visitors can enter without interrupting the quiet pod. Next worker: an interior designer could develop the interior circulation and material plan. Limit: this Grade 8 concept does not prove code or accessibility compliance.</p></div>',
                "EVIDENCE": "<p>Requirement audit, test evidence, revision, private submission, career and limitation explanation. Formative.</p>",
                "FLOW": flow("#5a2d91", "Priority · 5", "Complete, fix, or clarify.") + flow("#4a9d2f", "Model · 5", "Evidence-based revision.") + flow("#1f617a", "Build/test · 27", "Three visible checkpoints.") + flow("#e3ad19", "Review · 8", "Requirement and revision evidence.") + flow("#1f617a", "Submit/clean · 5", "Private route and exit."),
                "MONITOR": '<ul><li><strong>Checkpoint at minute 15:</strong> footprint, walls, roof, and response mode are visible.</li><li><strong>Checkpoint at minute 25:</strong> entrance, windows, and purposeful feature are labeled.</li><li><strong>Lap, minutes 28-35:</strong> require test evidence before accepting a revision.</li><li><strong>Checkpoint at minute 37:</strong> original choice, evidence, revision, expected improvement, next worker, and limit are all present.</li><li><strong>Pivot:</strong> students may use labeled bullets or the complete frame. <strong>Trim:</strong> cut partner review, not revision evidence, the private submission, or cleanup. Save the same artifact for a teacher-scheduled recovery window if needed.</li></ul>',
                "RESOURCES": "<p>The Canvas and paper directions are complete now. If a teacher enables Tinkercad, use only the tested teacher-managed Classroom route; do not promise screenshots or controls that have not been verified in that class.</p>",
                "SUPPORT": "<p>Provide extra time through accommodations, starter shapes, paper, speech-to-text, or a teacher-visible saved-model route.</p>",
                "FALLBACK": "<p>If export fails, accept the teacher-visible saved model and revision record temporarily. Canvas ownership replaces a public full-name filename.</p>",
            },
            5: {
                "TITLE": "Unexpected Architecture and Weekly Synthesis",
                "SUBTITLE": "50 minutes · TEKS d(1)(B), d(1)(C)",
                "ALERT": "<strong>Formative weekly portfolio.</strong> Use this to rehearse and revise evidence; it is not one of the two mapped 5SW majors. Keep the Assignment permanently at 0 points, not graded, and unpublished for teacher cloning.",
                "PREP": f'<ul><li><strong>Default:</strong> one FYF workbook and one device per student, one projector, zero prints. Use teams of 3-4 with one shared design surface per team and one individual private portfolio response per student.</li><li><strong>Roles:</strong> facilitator, evidence checker, sketch lead, timekeeper. In a 3-person team, combine evidence checker and timekeeper.</li><li><strong>Paper:</strong> one {link(files["LANDMARK"]["id"], "two-page individual form")} per student only when needed, one shared team sheet per team if FYF is unavailable, and one collection tray per class.</li><li>Post {link(files["PORTFOLIO_RUBRIC"]["id"], "the feedback guide")}. Day 2 Minor evidence stays referenced in place; students do not resubmit it.</li></ul>',
                "MODEL": '<div style="border:1px solid #bad4df;border-radius:8px;padding:14px 18px;background:#f2f8fb"><p><strong>Firm model:</strong> Our “Open Book” learning center supports city identity and attracts visitors. The architect shapes the front and side views around a readable book form. The drafter turns those choices into precise technical drawings. The interior designer plans how visitors move, learn, and gather inside. Together, the roles move from concept to coordinated design evidence. From Day 2, the architect salary fact must remain labeled: $96,690, May 2024 U.S. median annual wage, BLS. That figure does not show local starting pay or whether this concept can be built.</p></div>',
                "EVIDENCE": "<p>Two city goals, individual contribution, three-role synthesis, one preserved Day 2 label, and complete private portfolio.</p>",
                "FLOW": flow("#5a2d91", "Brief · 5", "City goals and roles.") + flow("#4a9d2f", "Firm concept · 22", "Choose, draw, label, record.") + flow("#1f617a", "Paired pitch · 12", "One-minute equal routes.") + flow("#e3ad19", "Synthesis/submit · 11", "Individual evidence and cleanup."),
                "MONITOR": '<ul><li><strong>Checkpoint at minute 12:</strong> each team has two city goals, roles, and one shared surface; solo students use the supplied model-analysis route.</li><li><strong>Lap 1, minutes 15-22:</strong> check that front and side views serve a stated city goal, not decoration alone.</li><li><strong>Checkpoint at minute 27:</strong> every student records an individual contribution.</li><li><strong>Lap 2, minutes 31-38:</strong> listen for three distinct role contributions and one correctly labeled Day 2 fact.</li><li><strong>Trim:</strong> use paired firms instead of a gallery rotation. Protect the final 11 minutes for individual synthesis, private Day 3-5 submission, material return, and tray collection. Missing prior work uses the supplied model; do not create a replacement packet or resubmit the Minor.</li></ul>',
                "RESOURCES": '<p>Licensed FYF and Climber Notes remain in authenticated Canvas. Current local pathway labels come from <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte/macarthur-high-school">Irving ISD MacArthur CTE</a>.</p>',
                "SUPPORT": "<p>Allow solo analysis, written explanation, private recording, speech-to-text, or paper. Students complete the design once in FYF or through the shared team artifact; the two-page fallback captures individual evidence without requiring another drawing.</p>",
                "FALLBACK": "<p>No group, live pitch, H&amp;L favorite, personal profile screenshot, or eDynamic completion is required.</p>",
            },
        }

        day_names = {
            1: "Cluster Roles and Safety Supervisor",
            2: "Career Preparation and Pay",
            3: "Concept Modeling Foundations",
            4: "Build, Test, Revise, and Submit",
            5: "Unexpected Architecture and Synthesis",
        }
        extras = {
            1: ("Assignment", safety["id"], SAFETY_TITLE),
            2: ("Assignment", comparison["id"], ASSESSMENT_TITLE),
            3: ("Assignment", design["id"], DESIGN_TITLE),
            4: ("Assignment", revision["id"], REVISION_TITLE),
            5: ("Assignment", portfolio["id"], PORTFOLIO_TITLE),
        }
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 5SW Wk1 Day {day} - {day_names[day]}"
            student_page = await common.upsert_page(
                client,
                student_title,
                common.render(
                    "5sw-wk1-student.html",
                    {"COURSE_ID": COURSE_ID, "DAY": day, "MEDIA": media[day], **CONTRACTS[day], **student[day]},
                ),
            )
            teacher_title = f"TEACHER: 5SW Wk1 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(
                client,
                teacher_title,
                common.render(
                    "5sw-wk1-teacher.html",
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

        final_items = await reconcile_module_items(client, module["id"], order)
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
        if module.get("published") or len([entry for entry in modules if entry.get("name") == MODULE_NAME]) != 1:
            raise RuntimeError(f"Final module invariant failed: published={module.get('published')}")
        if len(final_items) != 21:
            raise RuntimeError(f"Expected 21 exact module items; found {len(final_items)}")
        for day, pair in pages.items():
            for kind, page in pair.items():
                fresh = await common.api(client, "GET", f"/courses/{COURSE_ID}/pages/{page['url']}")
                if fresh.get("published"):
                    raise RuntimeError(f"Day {day} {kind} page is published")
                pair[kind] = fresh
        quiz = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
        final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
        expected_questions = [name for name, *_rest in QUESTIONS]
        quiz_matches = [entry for entry in await common.paged(client, f"/courses/{COURSE_ID}/quizzes") if entry.get("title") == QUIZ_TITLE or entry.get("title") in QUIZ_ALIASES]
        if (
            len(quiz_matches) != 1
            or quiz.get("published")
            or quiz.get("quiz_type") != "practice_quiz"
            or int(quiz.get("allowed_attempts") or 0) != -1
            or [entry.get("question_name") for entry in final_questions] != expected_questions
        ):
            raise RuntimeError(f"Final practice Quiz invariant failed for {QUIZ_TITLE!r}")
        safety = await assert_annotation_assignment(client, safety, files["SAFETY"]["id"])
        design = await assert_annotation_assignment(client, design, files["DESIGN"]["id"])
        revision = await assert_annotation_assignment(client, revision, files["REVISION"]["id"])
        comparison = await assert_annotation_assignment(client, comparison, files["CAREERS"]["id"], mapped=True)
        if (
            comparison.get("assignment_group_id") != minor_group["id"]
            or RUBRIC_NOTE_MARKER not in (comparison.get("description") or "")
        ):
            raise RuntimeError(f"Final Minor group/rubric invariant failed for {ASSESSMENT_TITLE!r}")
        portfolio = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{portfolio['id']}")
        portfolio_routes = {"online_upload", "online_text_entry", "media_recording"}
        if (
            portfolio.get("published")
            or float(portfolio.get("points_possible") or 0) != 0
            or portfolio.get("grading_type") != "percent"
            or portfolio.get("omit_from_final_grade") is not True
            or not portfolio_routes.issubset(set(portfolio.get("submission_types") or []))
        ):
            raise RuntimeError(f"Final formative Assignment invariant failed for {PORTFOLIO_TITLE!r}")
        support_folder = await common.lock_folder_files(client, support_folder)
        for day, folder in list(visual_folders.items()):
            visual_folders[day] = await common.lock_folder_files(client, folder)
        print(
            json.dumps(
                {
                    "module": {"id": module["id"], "published": module["published"]},
                    "quiz": {"id": quiz["id"], "published": quiz.get("published"), "allowed_attempts": quiz.get("allowed_attempts")},
                    "assignments": {
                        "safety": {"id": safety["id"], "published": safety.get("published"), "submission_types": safety.get("submission_types")},
                        "comparison": {"id": comparison["id"], "published": comparison.get("published"), "submission_types": comparison.get("submission_types")},
                        "design": {"id": design["id"], "published": design.get("published"), "submission_types": design.get("submission_types")},
                        "revision": {"id": revision["id"], "published": revision.get("published"), "submission_types": revision.get("submission_types")},
                        "portfolio": {"id": portfolio["id"], "published": portfolio.get("published"), "submission_types": portfolio.get("submission_types")},
                    },
                    "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
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
