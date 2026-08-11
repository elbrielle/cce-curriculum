"""Read-only Canvas module QA. Reads the API token from stdin and prints no secrets."""

import asyncio, json, re, sys
import httpx

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
SUBMISSION_LINK_MARKER = 'cce-mapped-assignment-link-v1'

WEEK_SPECS = {
    "6SW Wk5: Job Search, Applications, and Interviews": {
        "items": 20,
        "pages": 10,
        "assignment_titles": [
            "PRACTICE: Job Search and Posting Evidence",
            "PRACTICE: Tailored Cover Letter",
            "PRACTICE: Application and References",
            "PRACTICE: Interview Readiness Planner",
            "MAJOR 1: Job Skills, Application, and Mock Interview Portfolio",
        ],
        "major_title": "MAJOR 1: Job Skills, Application, and Mock Interview Portfolio",
        "major_group": "Major Assessments (60%)",
        "practice_titles": [
            "PRACTICE: Job Search and Posting Evidence",
            "PRACTICE: Tailored Cover Letter",
            "PRACTICE: Application and References",
            "PRACTICE: Interview Readiness Planner",
        ],
        "submission_markers": 1,
        "submission_marker_page_prefix": "STUDENT: 6SW Wk5 Day 5",
        "quiz_title": "PRACTICE QUIZ: Interview Readiness Check",
        "question_names": [
            "Q1 - screening",
            "Q2 - application",
            "Q3 - references",
            "Q4 - appearance",
            "Q5 - privacy",
        ],
        "file_names": {
            "6sw-wk5-job-search-and-posting-evidence.pdf",
            "6sw-wk5-cover-letter-simulation.pdf",
            "6sw-wk5-application-and-references.pdf",
            "6sw-wk5-interview-readiness.pdf",
            "6sw-wk5-mock-interview-and-thank-you.pdf",
            "6sw-wk5-job-skills-rubric.pdf",
        },
        "folder_suffixes": {"CCR Materials/6SW/Wk5"},
    },
    "6SW Wk6: Career Evidence Capstone": {
        "items": 20,
        "pages": 10,
        "assignment_titles": [
            "CAPSTONE: Evidence Inventory and Recovery",
            "CAPSTONE: Individual Career Plan",
            "CAPSTONE: Presentation Plan and Rehearsal",
            "MAJOR 2: Individual Career Plan and Communicated Capstone",
            "CAPSTONE: Final Course Reflection",
        ],
        "major_title": "MAJOR 2: Individual Career Plan and Communicated Capstone",
        "major_group": "Major Assessments (60%)",
        "practice_titles": [
            "CAPSTONE: Evidence Inventory and Recovery",
            "CAPSTONE: Individual Career Plan",
            "CAPSTONE: Presentation Plan and Rehearsal",
            "CAPSTONE: Final Course Reflection",
        ],
        "submission_markers": 1,
        "submission_marker_page_prefix": "STUDENT: 6SW Wk6 Day 4",
        "file_names": {
            "6sw-wk6-career-evidence-inventory.pdf",
            "6sw-wk6-individual-career-plan.pdf",
            "6sw-wk6-capstone-presentation-plan.pdf",
            "6sw-wk6-capstone-delivery-record.pdf",
            "6sw-wk6-final-course-reflection.pdf",
            "6sw-wk6-capstone-rubric.pdf",
            "fyf-p277.jpg",
            "fyf-p278.jpg",
            "fyf-p279.jpg",
            "fyf-p280.jpg",
            "fyf-p297.jpg",
            "fyf-p298.jpg",
            "fyf-p299.jpg",
            "fyf-p300.jpg",
        },
        "folder_suffixes": {
            "CCR Materials/6SW/Wk6",
            "CCR Materials/6SW/Wk6/Locked Licensed Visuals",
        },
    },
}


async def api(client, path):
    response = await client.get(f"{BASE}/api/v1{path}")
    response.raise_for_status()
    return response.json()


async def paged(client, path):
    results = []
    url = f"{BASE}/api/v1{path}"
    params = {"per_page": 100}
    while url:
        response = await client.get(url, params=params)
        response.raise_for_status()
        results.extend(response.json())
        url = response.links.get("next", {}).get("url")
        params = None
    return results


async def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        raise SystemExit("usage: qa_canvas_module.py MODULE_ID")
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    module_id = int(sys.argv[1])
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=60
    ) as client:
        module = await api(client, f"/courses/{COURSE_ID}/modules/{module_id}")
        spec = WEEK_SPECS.get(module.get("name"))
        items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
        problems = []
        pages = []
        interactives = []
        file_ids = set()
        positions = [item.get("position") for item in items]
        if module.get("published"):
            problems.append("module is published")
        if positions != list(range(1, len(items) + 1)):
            problems.append(f"positions are not consecutive: {positions}")
        for item in items:
            if item.get("type") == "Quiz" and item.get("content_id"):
                quiz = await api(
                    client, f"/courses/{COURSE_ID}/quizzes/{item['content_id']}"
                )
                questions = await paged(
                    client,
                    f"/courses/{COURSE_ID}/quizzes/{item['content_id']}/questions",
                )
                if quiz.get("published") or item.get("published"):
                    problems.append(f"quiz published: {quiz.get('id')}")
                if quiz.get("quiz_type") != "practice_quiz":
                    problems.append(f"quiz is not practice: {quiz.get('id')}")
                if quiz.get("allowed_attempts") != -1:
                    problems.append(f"quiz is not unlimited-attempt: {quiz.get('id')}")
                if quiz.get("show_correct_answers") is not True:
                    problems.append(f"quiz hides correct answers: {quiz.get('id')}")
                interactives.append(
                    {
                        "item_id": item["id"],
                        "position": item["position"],
                        "type": "Quiz",
                        "content_id": quiz.get("id"),
                        "title": quiz.get("title"),
                        "published": quiz.get("published"),
                        "quiz_type": quiz.get("quiz_type"),
                        "questions": len(questions),
                        "allowed_attempts": quiz.get("allowed_attempts"),
                        "show_correct_answers": quiz.get("show_correct_answers"),
                        "question_names": [
                            question.get("question_name") for question in questions
                        ],
                    }
                )
                continue
            if item.get("type") == "Discussion" and item.get("content_id"):
                topic = await api(
                    client,
                    f"/courses/{COURSE_ID}/discussion_topics/{item['content_id']}",
                )
                if topic.get("published") or item.get("published"):
                    problems.append(f"discussion published: {topic.get('id')}")
                interactives.append(
                    {
                        "item_id": item["id"],
                        "position": item["position"],
                        "type": "Discussion",
                        "content_id": topic.get("id"),
                        "title": topic.get("title"),
                        "published": topic.get("published"),
                    }
                )
                continue
            if item.get("type") == "Assignment" and item.get("content_id"):
                assignment = await api(
                    client, f"/courses/{COURSE_ID}/assignments/{item['content_id']}"
                )
                if assignment.get("published") or item.get("published"):
                    problems.append(f"assignment published: {assignment.get('id')}")
                title = assignment.get("name") or ""
                if title.startswith(("PRACTICE:", "FORMATIVE:", "RECOVERY:")):
                    if float(assignment.get("points_possible") or 0) != 0:
                        problems.append(
                            f"grade-neutral assignment has points: {assignment.get('id')}"
                        )
                    if assignment.get("omit_from_final_grade") is not True:
                        problems.append(
                            f"grade-neutral assignment counts toward final grade: {assignment.get('id')}"
                        )
                interactives.append(
                    {
                        "item_id": item["id"],
                        "position": item["position"],
                        "type": "Assignment",
                        "content_id": assignment.get("id"),
                        "title": assignment.get("name"),
                        "published": assignment.get("published"),
                        "grading_type": assignment.get("grading_type"),
                        "points_possible": assignment.get("points_possible"),
                        "omit_from_final_grade": assignment.get(
                            "omit_from_final_grade"
                        ),
                        "submission_types": assignment.get("submission_types"),
                        "annotatable_attachment_id": assignment.get(
                            "annotatable_attachment_id"
                        ),
                        "assignment_group_id": assignment.get("assignment_group_id"),
                    }
                )
                continue
            if item.get("type") == "SubHeader":
                interactives.append(
                    {
                        "item_id": item["id"],
                        "position": item["position"],
                        "type": "SubHeader",
                        "title": item.get("title"),
                    }
                )
                continue
            if item.get("type") != "Page" or not item.get("page_url"):
                problems.append(
                    f"unsupported module item {item.get('id')}: {item.get('type')}"
                )
                continue
            page = await api(client, f"/courses/{COURSE_ID}/pages/{item['page_url']}")
            body = page.get("body") or ""
            unresolved = sorted(set(re.findall(r"\{\{[^}]+\}\}", body)))
            if page.get("published"):
                problems.append(f"page published: {page['url']}")
            if unresolved:
                problems.append(f"unresolved fields in {page['url']}: {unresolved}")
            if "enhanceable_content" in body:
                problems.append(f"legacy Canvas tabs in {page['url']}")
            file_ids.update(int(value) for value in re.findall(r"/files/(\d+)", body))
            pages.append(
                {
                    "item_id": item["id"],
                    "position": item["position"],
                    "url": page["url"],
                    "title": item.get("title"),
                    "published": page["published"],
                    "body_chars": len(body),
                    "submission_markers": body.count(SUBMISSION_LINK_MARKER),
                }
            )
        files = []
        folder_ids = set()
        for file_id in sorted(file_ids):
            try:
                record = await api(client, f"/files/{file_id}")
                files.append(
                    {
                        "id": file_id,
                        "name": record.get("display_name"),
                        "locked": record.get("locked"),
                    }
                )
                if not record.get("locked"):
                    problems.append(
                        f"referenced file is unlocked: {file_id} {record.get('display_name')}"
                    )
                if record.get("folder_id"):
                    folder_ids.add(int(record["folder_id"]))
            except httpx.HTTPStatusError as exc:
                problems.append(
                    f"file {file_id} did not resolve: HTTP {exc.response.status_code}"
                )
        folders = []
        for folder_id in sorted(folder_ids):
            folder = await api(client, f"/folders/{folder_id}")
            folder_files = await paged(client, f"/folders/{folder_id}/files")
            if not folder.get("locked"):
                problems.append(
                    f"referenced folder is unlocked: {folder_id} {folder.get('full_name')}"
                )
            unlocked = [
                record.get("id") for record in folder_files if not record.get("locked")
            ]
            if unlocked:
                problems.append(
                    f"folder {folder_id} contains unlocked files: {unlocked}"
                )
            folders.append(
                {
                    "id": folder_id,
                    "name": folder.get("full_name"),
                    "locked": folder.get("locked"),
                    "files": len(folder_files),
                    "all_files_locked": not unlocked,
                }
            )
        external_quiz = None
        if spec:
            if len(items) != spec["items"]:
                problems.append(
                    f"expected {spec['items']} module items; found {len(items)}"
                )
            if len(pages) != spec["pages"]:
                problems.append(f"expected {spec['pages']} pages; found {len(pages)}")
            item_types = [item.get("type") for item in items]
            expected_types = ["SubHeader", "Page", "Page", "Assignment"] * 5
            if item_types != expected_types:
                problems.append(f"module item type order mismatch: {item_types}")

            assignments = [
                entry for entry in interactives if entry.get("type") == "Assignment"
            ]
            assignment_titles = [entry.get("title") for entry in assignments]
            if assignment_titles != spec["assignment_titles"]:
                problems.append(
                    f"assignment title/order mismatch: {assignment_titles}"
                )
            for entry in assignments:
                title = entry.get("title") or ""
                if title in spec["practice_titles"]:
                    if float(entry.get("points_possible") or 0) != 0:
                        problems.append(f"practice assignment has points: {title}")
                    if entry.get("grading_type") != "percent":
                        problems.append(
                            f"practice assignment lost its submission-preserving percentage setting: {title}"
                        )
                    if entry.get("omit_from_final_grade") is not True:
                        problems.append(f"practice assignment counts toward grade: {title}")
                if title == spec["major_title"]:
                    if float(entry.get("points_possible") or 0) != 100:
                        problems.append("mapped Major is not worth 100 points")
                    if entry.get("grading_type") != "points":
                        problems.append("mapped Major is not points-graded")
                    if entry.get("omit_from_final_grade") is True:
                        problems.append("mapped Major is omitted from final grade")
                    groups = await paged(client, f"/courses/{COURSE_ID}/assignment_groups")
                    group = next(
                        (
                            candidate
                            for candidate in groups
                            if candidate.get("id") == entry.get("assignment_group_id")
                        ),
                        None,
                    )
                    if not group or group.get("name") != spec["major_group"]:
                        problems.append(
                            f"mapped Major is outside {spec['major_group']}"
                        )

            marker_pages = [page for page in pages if page["submission_markers"]]
            marker_count = sum(page["submission_markers"] for page in pages)
            if marker_count != spec["submission_markers"]:
                problems.append(
                    f"expected {spec['submission_markers']} submission marker; found {marker_count}"
                )
            if marker_pages and not all(
                (page.get("title") or "").startswith(
                    spec["submission_marker_page_prefix"]
                )
                for page in marker_pages
            ):
                problems.append(
                    "submission marker appears outside "
                    f"{spec['submission_marker_page_prefix']}"
                )

            file_names = {record.get("name") for record in files}
            if file_names != spec["file_names"]:
                problems.append(
                    f"referenced module file set mismatch: {sorted(file_names)}"
                )
            folder_names = {
                folder.get("name") or "" for folder in folders
            }
            matched_suffixes = {
                suffix
                for suffix in spec["folder_suffixes"]
                if any(name.endswith(suffix) for name in folder_names)
            }
            if matched_suffixes != spec["folder_suffixes"] or len(folders) != len(
                spec["folder_suffixes"]
            ):
                problems.append(
                    f"module files are outside the exact locked folders: {folders}"
                )

            for entry in assignments:
                title = entry.get("title") or ""
                submission_types = set(entry.get("submission_types") or [])
                required_types = {
                    "student_annotation",
                    "online_upload",
                    "online_text_entry",
                }
                if title == spec["major_title"]:
                    required_types.add("media_recording")
                if not required_types.issubset(submission_types):
                    problems.append(
                        f"assignment is missing an approved private route: {title} {sorted(submission_types)}"
                    )
                if entry.get("annotatable_attachment_id") is None:
                    problems.append(f"assignment has no annotatable packet: {title}")

            if spec.get("quiz_title"):
                quizzes = await paged(client, f"/courses/{COURSE_ID}/quizzes")
                quiz_matches = [
                    quiz for quiz in quizzes if quiz.get("title") == spec["quiz_title"]
                ]
                if len(quiz_matches) != 1:
                    problems.append(
                        f"expected one {spec['quiz_title']!r}; found {len(quiz_matches)}"
                    )
                else:
                    quiz = await api(
                        client, f"/courses/{COURSE_ID}/quizzes/{quiz_matches[0]['id']}"
                    )
                    questions = await paged(
                        client,
                        f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions",
                    )
                    names = [question.get("question_name") for question in questions]
                    if quiz.get("published"):
                        problems.append(f"linked practice Quiz is published: {quiz.get('id')}")
                    if quiz.get("quiz_type") != "practice_quiz":
                        problems.append("linked Quiz is not a practice Quiz")
                    if quiz.get("allowed_attempts") != -1:
                        problems.append("linked practice Quiz is not unlimited-attempt")
                    if quiz.get("show_correct_answers") is not True:
                        problems.append("linked practice Quiz hides correct answers")
                    if quiz.get("shuffle_answers") is not False:
                        problems.append("linked practice Quiz shuffles the fixed answer order")
                    if names != spec["question_names"]:
                        problems.append(f"linked practice Quiz order mismatch: {names}")
                    external_quiz = {
                        "id": quiz.get("id"),
                        "title": quiz.get("title"),
                        "published": quiz.get("published"),
                        "quiz_type": quiz.get("quiz_type"),
                        "allowed_attempts": quiz.get("allowed_attempts"),
                        "show_correct_answers": quiz.get("show_correct_answers"),
                        "shuffle_answers": quiz.get("shuffle_answers"),
                        "question_names": names,
                    }
        result = {
            "module": {
                "id": module_id,
                "name": module.get("name"),
                "published": module.get("published"),
            },
            "items": len(items),
            "pages": pages,
            "interactives": interactives,
            "referenced_files": files,
            "referenced_folders": folders,
            "external_quiz": external_quiz,
            "problems": problems,
            "passed": not problems,
        }
        print(json.dumps(result, indent=2))
        if problems:
            raise SystemExit(2)


asyncio.run(main())
