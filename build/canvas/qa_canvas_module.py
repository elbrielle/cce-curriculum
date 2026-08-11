"""Read-only Canvas module QA. Reads the API token from stdin and prints no secrets."""

import asyncio, json, re, sys
import httpx

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
SUBMISSION_LINK_MARKER = 'cce-mapped-assignment-link-v1'


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
            "problems": problems,
            "passed": not problems,
        }
        print(json.dumps(result, indent=2))
        if problems:
            raise SystemExit(2)


asyncio.run(main())
