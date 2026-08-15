"""Build the unpublished 3SW Week 1 Veterinary Science Canvas module."""

import asyncio
import json
import mimetypes
import re
import sys
from pathlib import Path
from urllib.parse import urlencode

import httpx

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
MODULE_NAME = "3SW Wk1: Veterinary Science"
QUIZ_TITLE = "PRACTICE: Veterinary Triage Evidence Check"
ASSIGNMENT_TITLE = "PRACTICE: Xello Skills Reflection"
MAPPED_MINOR_TITLE = "MINOR 1: Veterinary Pathway Evidence Packet"
MINOR_GROUP_NAME = "Minor Assessments (40%)"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/3sw/wk1"
XELLO = ROOT / "cce-curriculum/resources/xello-licensed/lessons"


def preflight():
    required = [
        TEMPLATES / "3sw-wk1-student.html",
        TEMPLATES / "3sw-wk1-teacher.html",
        *(ROOT / "docs/resources/worksheets" / name for name in (
            "3sw-wk1-veterinary-career-evidence-guide.pdf",
            "3sw-wk1-veterinary-career-comparison.pdf",
            "3sw-wk1-veterinary-triage-record.pdf",
            "3sw-wk1-xello-skills-reflection.pdf",
            "3sw-wk1-veterinary-pathway-brief.pdf",
            "3sw-wk1-veterinary-evidence-rubric.pdf",
        )),
        XELLO / "skills.pdf",
        XELLO / "skills/skills-slides-irving.pptx",
        XELLO / "skills/skills-slides-spanish.pptx",
        ASSETS / "day1/fyf-agriculture-opener.jpg",
        *(ASSETS / "day3" / f"fyf-vet-triage-{number}.png" for number in range(1, 5)),
        *(ASSETS / "day5" / f"fyf-irving-ag-programs-{number}.png" for number in range(1, 3)),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"3SW Wk1 preflight missing required files: {missing}")


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower().replace("&", "and")).strip("-")


async def api(client, method, path, **kwargs):
    response = await client.request(method, f"{BASE}/api/v1{path}", **kwargs)
    response.raise_for_status()
    return response.json() if response.content else None


async def paged(client, path, params=None):
    output, url, query = [], f"{BASE}/api/v1{path}", {"per_page": 100, **(params or {})}
    while url:
        response = await client.get(url, params=query)
        response.raise_for_status()
        output += response.json()
        url, query = response.links.get("next", {}).get("url"), None
    return output


async def ensure_module(client):
    modules = await paged(client, f"/courses/{COURSE_ID}/modules")
    matches = [value for value in modules if value["name"] == MODULE_NAME]
    if len(matches) > 1:
        raise RuntimeError(f"Duplicate Canvas modules named {MODULE_NAME!r}: {[value['id'] for value in matches]}")
    found = matches[0] if matches else None
    if found:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data={"module[name]": MODULE_NAME, "module[published]": "false"})
    return await api(client, "POST", f"/courses/{COURSE_ID}/modules", data={"module[name]": MODULE_NAME, "module[published]": "false"})


async def ensure_folder(client, path):
    current, folder = "", None
    for name in path.split("/")[1:]:
        target = f"{current}/{name}".strip("/")
        encoded = httpx.URL("/" + target).raw_path.decode("ascii").lstrip("/")
        response = await client.get(f"{BASE}/api/v1/courses/{COURSE_ID}/folders/by_path/{encoded}")
        if response.status_code == 200 and response.json():
            folder = response.json()[-1]
        else:
            folder = await api(client, "POST", f"/courses/{COURSE_ID}/folders", data={"name": name, "parent_folder_path": "course files" + (f"/{current}" if current else ""), "locked": "true"})
        current = target
    if folder and not folder.get("locked"):
        folder = await api(client, "PUT", f"/folders/{folder['id']}", data={"locked": "true"})
    return folder


async def upload(client, path, folder_path):
    start = await api(client, "POST", f"/courses/{COURSE_ID}/files", data={"name": path.name, "parent_folder_path": folder_path, "on_duplicate": "overwrite"})
    response = await client.post(start["upload_url"], data=start["upload_params"], files={"file": (path.name, path.read_bytes(), mimetypes.guess_type(path.name)[0] or "application/octet-stream")}, follow_redirects=True)
    response.raise_for_status()
    uploaded = response.json()
    record = await api(client, "PUT", f"/files/{uploaded['id']}", data={"locked": "true"})
    if not record.get("locked"):
        raise RuntimeError(f"Canvas did not lock uploaded file {path.name!r}")
    return record


async def lock_folder_files(client, folder):
    current = await api(client, "GET", f"/folders/{folder['id']}")
    if not current.get("locked"):
        current = await api(client, "PUT", f"/folders/{folder['id']}", data={"locked": "true"})
    if not current.get("locked"):
        raise RuntimeError(f"Canvas did not lock folder {folder.get('full_name') or folder['id']}")
    for entry in await paged(client, f"/folders/{folder['id']}/files"):
        if not entry.get("locked"):
            await api(client, "PUT", f"/files/{entry['id']}", data={"locked": "true"})
    final = await paged(client, f"/folders/{folder['id']}/files")
    unlocked = [entry.get("display_name") or entry.get("filename") for entry in final if not entry.get("locked")]
    if unlocked:
        raise RuntimeError(f"Unlocked files remain in folder {folder['id']}: {unlocked}")
    return current, len(final)


def render(template_name, values):
    text = (TEMPLATES / template_name).read_text()
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    unresolved = sorted(set(re.findall(r"\{\{[^}]+\}\}", text)))
    if unresolved:
        raise ValueError(f"Unresolved values in {template_name}: {unresolved}")
    return text


async def upsert_page(client, title, body, legacy_titles=()):
    url = slugify(title)
    data = {"wiki_page[title]": title, "wiki_page[body]": body, "wiki_page[published]": "false", "wiki_page[editing_roles]": "teachers"}
    for candidate in (url, *(slugify(value) for value in legacy_titles)):
        response = await client.get(f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{candidate}")
        if response.status_code == 200:
            return await api(client, "PUT", f"/courses/{COURSE_ID}/pages/{candidate}", data=data)
        if response.status_code != 404:
            response.raise_for_status()
    return await api(client, "POST", f"/courses/{COURSE_ID}/pages", data=data)


async def upsert_module_item(client, module_id, kind, key, title):
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    found = next((entry for entry in items if (kind == "Page" and entry.get("page_url") == key) or (kind in ("Quiz", "Assignment") and entry.get("content_id") == key)), None)
    if found:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module_id}/items/{found['id']}", data={"module_item[title]": title})
    payload = {"module_item[type]": kind, "module_item[title]": title}
    payload["module_item[page_url]" if kind == "Page" else "module_item[content_id]"] = key
    return await api(client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data=payload)


async def upsert_header(client, module_id, title, legacy_titles=()):
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    accepted = {title, *legacy_titles}
    found = next((entry for entry in items if entry.get("type") == "SubHeader" and entry.get("title") in accepted), None)
    if found:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module_id}/items/{found['id']}", data={"module_item[title]": title}) if found.get("title") != title else found
    return await api(client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data={"module_item[type]": "SubHeader", "module_item[title]": title})


def file_link(file_id, label):
    return f'<a href="/courses/{COURSE_ID}/files/{file_id}/preview" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">{label}</a>'


def image_tag(file_id, alt, max_width=720):
    return f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" style="display:block;width:100%;max-width:{max_width}px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'


def step(number, title, body):
    return f'<h3 style="color:#5a2d91;border-bottom:3px solid #d9c9ed">{number}. {title}</h3>{body}'


def flow(color, title, text):
    return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'


QUESTIONS = [
    ("Q1 - Barnaby priority", "Which evidence most strongly supports seeing Barnaby first?", "Repeated unproductive retching, a painful distended abdomen, heart rate 150, and a weak pulse.", ["Barnaby weighs 100 pounds.", "Barnaby is a Great Dane.", "Barnaby ate breakfast yesterday."], "Correct. The cluster of abnormal observations signals the highest priority.", "Use the abnormal observations together, not breed or size alone."),
    ("Q2 - Leo boundary", "What is the strongest conclusion about Leo?", "The observations fit the supplied shedding reference, but a veterinarian still makes the diagnosis.", ["Leo definitely has one disease.", "Leo needs a student-selected medicine.", "Cloudy eyes always mean an emergency."], "Correct. Triage compares observations; it does not diagnose.", "Students may prioritize and report observations, but they do not diagnose or prescribe."),
    ("Q3 - Strong reasoning", "Which response shows the strongest triage reasoning?", "Compare each animal with the correct species normal range and cite at least two relevant observations.", ["Choose the animal that looks scariest.", "Use one vital sign for every animal.", "Vote before reading the reference ranges."], "Correct. Species-specific ranges plus multiple observations make the reasoning defensible.", "Look for the choice that uses the supplied ranges and more than one observation."),
    ("Q4 - Role boundary", "Which statement keeps the veterinary role boundary clear?", "A veterinary team member records and reports observations; a veterinarian diagnoses and treats.", ["A student can diagnose after reading one chart.", "The triage team should recommend medicine.", "A normal temperature proves the animal is healthy."], "Correct. Observation and escalation are different from diagnosis and treatment.", "The classroom task stops at observation, prioritization, and reporting."),
]


async def prepare_quiz_questions(client, quiz_id, desired_names):
    existing = await paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions")
    keep, seen = [], set()
    for question in existing:
        name = question.get("question_name")
        if name not in desired_names or name in seen:
            await api(client, "DELETE", f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions/{question['id']}")
        else:
            seen.add(name)
            keep.append(question)
    return keep


async def finalize_quiz_order(client, quiz_id, expected_names):
    final = await paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions")
    by_name = {entry.get("question_name"): entry for entry in final}
    if set(by_name) != set(expected_names) or len(final) != len(expected_names):
        raise RuntimeError(f"Quiz {quiz_id} question mismatch: {[entry.get('question_name') for entry in final]}")
    fields = []
    for name in expected_names:
        fields.extend([("order[][id]", str(by_name[name]["id"])), ("order[][type]", "question")])
    await api(client, "POST", f"/courses/{COURSE_ID}/quizzes/{quiz_id}/reorder", content=urlencode(fields), headers={"Content-Type": "application/x-www-form-urlencoded"})
    ordered = await paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions")
    actual = [entry.get("question_name") for entry in ordered]
    if actual != expected_names:
        raise RuntimeError(f"Quiz {quiz_id} order mismatch: expected {expected_names}, found {actual}")


async def upsert_quiz(client):
    quizzes = await paged(client, f"/courses/{COURSE_ID}/quizzes")
    matches = [entry for entry in quizzes if entry.get("title") == QUIZ_TITLE]
    if len(matches) > 1:
        raise RuntimeError(f"Duplicate quizzes named {QUIZ_TITLE!r}: {[entry['id'] for entry in matches]}")
    quiz = matches[0] if matches else None
    data = {"quiz[title]": QUIZ_TITLE, "quiz[description]": "<p>Ungraded practice. Retry and use the feedback before finalizing your triage record.</p>", "quiz[quiz_type]": "practice_quiz", "quiz[published]": "false", "quiz[allowed_attempts]": "-1", "quiz[show_correct_answers]": "true", "quiz[shuffle_answers]": "false"}
    quiz = await api(client, "PUT" if quiz else "POST", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}" if quiz else f"/courses/{COURSE_ID}/quizzes", data=data)
    expected = [spec[0] for spec in QUESTIONS]
    existing = await prepare_quiz_questions(client, quiz["id"], set(expected))
    for position, (name, text, correct, wrong, correct_comment, incorrect_comment) in enumerate(QUESTIONS, 1):
        found = next((q for q in existing if q.get("question_name") == name), None)
        payload = {"question": {"question_name": name, "question_text": text, "question_type": "multiple_choice_question", "position": position, "points_possible": 1, "correct_comments": correct_comment, "incorrect_comments": incorrect_comment, "answers": [{"answer_text": correct, "answer_weight": 100}] + [{"answer_text": value, "answer_weight": 0} for value in wrong]}}
        await api(client, "PUT" if found else "POST", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions", json=payload)
    await finalize_quiz_order(client, quiz["id"], expected)
    final = await api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
    if final.get("published") or final.get("quiz_type") != "practice_quiz" or int(final.get("allowed_attempts") or 0) != -1:
        raise RuntimeError(f"Practice quiz invariant failed: published={final.get('published')}, type={final.get('quiz_type')}, attempts={final.get('allowed_attempts')}")
    return final


async def upsert_assignment(client):
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == ASSIGNMENT_TITLE]
    if len(matches) > 1:
        raise RuntimeError(f"Duplicate assignments named {ASSIGNMENT_TITLE!r}: {[entry['id'] for entry in matches]}")
    found = matches[0] if matches else None
    data = {"assignment[name]": ASSIGNMENT_TITLE, "assignment[description]": "<p>Submit the private Xello Skills reflection as text or the supplied PDF. Do not upload a screenshot of your Xello profile.</p>", "assignment[submission_types][]": ["online_text_entry", "online_upload"], "assignment[grading_type]": "not_graded", "assignment[points_possible]": "0", "assignment[omit_from_final_grade]": "true", "assignment[published]": "false"}
    assignment = await api(client, "PUT" if found else "POST", f"/courses/{COURSE_ID}/assignments/{found['id']}" if found else f"/courses/{COURSE_ID}/assignments", data=data)
    if assignment.get("published") or float(assignment.get("points_possible") or 0) != 0 or assignment.get("grading_type") != "not_graded" or not assignment.get("omit_from_final_grade"):
        raise RuntimeError(f"Formative reflection invariant failed: published={assignment.get('published')}, points={assignment.get('points_possible')}, grading={assignment.get('grading_type')}, omit={assignment.get('omit_from_final_grade')}")
    return assignment


async def require_mapped_minor(client):
    groups = await paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group_matches = [entry for entry in groups if entry.get("name") == MINOR_GROUP_NAME]
    if len(group_matches) != 1:
        raise RuntimeError(
            f"Expected exactly one assignment group named {MINOR_GROUP_NAME!r}; "
            f"found {len(group_matches)}"
        )
    group = group_matches[0]
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == MAPPED_MINOR_TITLE]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one mapped assignment named {MAPPED_MINOR_TITLE!r}; "
            f"found {len(matches)}"
        )
    minor = matches[0]
    if (
        minor.get("published")
        or float(minor.get("points_possible") or 0) != 100
        or minor.get("assignment_group_id") != group["id"]
        or minor.get("grading_type") != "points"
        or minor.get("omit_from_final_grade")
    ):
        raise RuntimeError(
            f"Mapped Minor invariant failed before module writes: "
            f"published={minor.get('published')}, points={minor.get('points_possible')}, "
            f"group={minor.get('assignment_group_id')}, grading={minor.get('grading_type')}, "
            f"omit={minor.get('omit_from_final_grade')}"
        )
    return minor, group


async def main():
    preflight()
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        minor, minor_group = await require_mapped_minor(client)
        module, quiz, assignment = await ensure_module(client), await upsert_quiz(client), await upsert_assignment(client)
        support_path = "course files/CCR Materials/3SW/Wk1"
        support_folder = await ensure_folder(client, support_path)
        names = {"CAREERS": "3sw-wk1-veterinary-career-evidence-guide.pdf", "COMPARE": "3sw-wk1-veterinary-career-comparison.pdf", "TRIAGE": "3sw-wk1-veterinary-triage-record.pdf", "REFLECT": "3sw-wk1-xello-skills-reflection.pdf", "PATHWAY": "3sw-wk1-veterinary-pathway-brief.pdf", "RUBRIC": "3sw-wk1-veterinary-evidence-rubric.pdf"}
        files = {key: await upload(client, ROOT / "docs/resources/worksheets" / name, support_path) for key, name in names.items()}
        files["XELLO_GUIDE"] = await upload(client, XELLO / "skills.pdf", support_path)
        files["XELLO_DECK"] = await upload(client, XELLO / "skills/skills-slides-irving.pptx", support_path)
        files["XELLO_SPANISH"] = await upload(client, XELLO / "skills/skills-slides-spanish.pptx", support_path)
        folders, uploads = {}, {}
        for day in range(1, 6):
            folder_path = f"course files/CCR Materials/3SW/Wk1/Day {day} Visuals"
            folders[day], uploads[day] = await ensure_folder(client, folder_path), {}
            source = ASSETS / f"day{day}"
            if source.exists():
                for path in sorted(
                    candidate
                    for candidate in source.iterdir()
                    if candidate.suffix.lower() in {".png", ".jpg", ".jpeg"}
                    and not (
                        candidate.suffix.lower() == ".png"
                        and (
                            candidate.with_suffix(".jpg").exists()
                            or candidate.with_suffix(".jpeg").exists()
                        )
                    )
                ):
                    uploads[day][path.name] = await upload(client, path, folder_path)
        support_folder, support_file_count = await lock_folder_files(client, support_folder)
        folder_file_counts = {}
        for day, folder in folders.items():
            folders[day], folder_file_counts[day] = await lock_folder_files(client, folder)

        quiz_url, assignment_url = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}", f"/courses/{COURSE_ID}/assignments/{assignment['id']}"
        student = {
            1: {
                "TITLE": "Meet the Veterinary Team",
                "PURPOSE": "Compare three veterinary careers using one dated evidence set.",
                "TODAY": "<ul><li>identify what each role does;</li><li>compare education, pay, growth, and openings;</li><li>choose one role to investigate.</li></ul>",
                "READY": f'<p>Open {file_link(files["CAREERS"]["id"], "the Veterinary Career Evidence Guide")}.</p>',
                "MEDIA": image_tag(uploads[1]["fyf-agriculture-opener.jpg"]["id"], "Find Your Future agriculture and animal-care career opener"),
                "STEPS": step(1, "Stop and Jot", "<p>Who works on a veterinary team, and what might that person do?</p>") + step(2, "Read all three career cards", "<p>Read duties first. Then read preparation and labor evidence. Keep the salary measure, source, date, and education route attached to each number.</p>") + step(3, "Choose one role", "<p>Complete the Day 1 choice on the guide. Use this frame: <strong>I would investigate ____ because the work includes ____ and the preparation requires ____.</strong></p>"),
                "EXIT": "<p>Submit or store the Day 1 choice. A partner may check that the two facts can be found in the guide.</p>",
                "DONE": "<ul><li>three roles reviewed;</li><li>one role chosen;</li><li>one daily task and one preparation requirement recorded.</li></ul>",
                "SUPPORT": "<p><strong>Word bank:</strong> median = mediana · training = formación · openings = vacantes · veterinarian = veterinario/a.</p><p><strong>Frame:</strong> I would investigate ____ because the work includes ____ and the preparation requires ____.</p>",
                "FALLBACK": "<p>The fixed evidence guide is the full no-login and absence route. H&amp;L is optional enrichment.</p>",
            },
            2: {
                "TITLE": "Compare Veterinary Career Paths",
                "PURPOSE": "Use the same measures to explain how veterinary roles differ.",
                "TODAY": "<ul><li>complete a three-role comparison;</li><li>choose one fictional scenario;</li><li>recommend a role with two facts and one trade-off.</li></ul>",
                "READY": f'<p>Open {file_link(files["COMPARE"]["id"], "the Veterinary Career Comparison")} and the evidence guide.</p>',
                "MEDIA": "",
                "STEPS": step(1, "Transfer the evidence", "<p>Fill every row from the fixed guide. Do not mix national median pay with starting pay.</p>") + step(2, "Check the preparation routes", "<p>Compare short-term training, an associate degree, and a professional degree. A partner may check your labels after you finish independently.</p>") + step(3, "Choose one scenario", "<p>Choose Scenario A or B. Use this frame: <strong>I recommend ____ because ____ and ____; however, ____.</strong></p>"),
                "EXIT": "<p>Submit or store the completed comparison and one scenario recommendation.</p>",
                "DONE": "<ul><li>all six evidence rows complete for all three careers;</li><li>salary measure and source kept accurate;</li><li>one scenario recommendation uses two facts and one trade-off.</li></ul>",
                "SUPPORT": "<p><strong>Word bank:</strong> assistant = asistente · technician = técnico/a · degree = título · trade-off = costo y beneficio.</p><p><strong>Frame:</strong> I recommend ____ because ____ and ____; however, ____.</p>",
                "FALLBACK": "<p>The two PDFs contain all required facts. No web search or partner is required.</p>",
            },
            3: {
                "TITLE": "Veterinary Triage: Observe, Compare, Report",
                "PURPOSE": "Prioritize two fictional patients using supplied observations and species-specific ranges without diagnosing.",
                "TODAY": "<ul><li>read the two fictional patient charts;</li><li>compare observations with the correct ranges;</li><li>defend which patient should be seen first.</li></ul>",
                "READY": '<p>Use <em>Find Your Future</em> pp. 96-99. Write your evidence and decision on p. 99.</p><p><strong>Role boundary:</strong> You observe, compare, prioritize, and report. A veterinarian diagnoses and treats.</p>',
                "MEDIA": "",
                "STEPS": step(1, "Read both patient charts", image_tag(uploads[3]["fyf-vet-triage-1.png"]["id"], "Find Your Future veterinary triage patient chart page 96", 650) + f'<p>{file_link(uploads[3]["fyf-vet-triage-1.png"]["id"], "Open FYF p. 96 full size")}</p>' + image_tag(uploads[3]["fyf-vet-triage-2.png"]["id"], "Find Your Future veterinary triage patient chart page 97", 650) + f'<p>{file_link(uploads[3]["fyf-vet-triage-2.png"]["id"], "Open FYF p. 97 full size")}</p><p>Mark symptoms, vital signs, species, and time for Leo and Barnaby before choosing a priority.</p>') + step(2, "Use the correct reference", image_tag(uploads[3]["fyf-vet-triage-3.png"]["id"], "Find Your Future veterinary triage reference page 98", 650) + f'<p>{file_link(uploads[3]["fyf-vet-triage-3.png"]["id"], "Open FYF p. 98 full size")}</p><p>Compare the snake observations with the ball-python reference and the dog observations with the dog reference.</p>') + step(3, "Record the decision on workbook p. 99", image_tag(uploads[3]["fyf-vet-triage-4.png"]["id"], "Find Your Future veterinary triage response page 99", 650) + f'<p>{file_link(uploads[3]["fyf-vet-triage-4.png"]["id"], "Open FYF p. 99 full size")}</p><p>Cite at least two observations. Use this frame: <strong>The technician produced ____. I would report ____ first because ____ and ____.</strong></p>') + step(4, "Check your reasoning", f'<p><a href="{quiz_url}">Open the Triage Evidence Check</a>. Retry and use the feedback. If devices are unavailable, submit p. 99 and complete the quiz during the next class opening.</p>'),
                "EXIT": "<p>Submit or store p. 99. Return the workbook and device as directed.</p>",
                "DONE": "<ul><li>Leo and Barnaby reviewed;</li><li>workbook p. 99 completed;</li><li>triage record named as the work product;</li><li>first choice defended with two observations;</li><li>no diagnosis or treatment advice.</li></ul>",
                "SUPPORT": "<p><strong>Word bank:</strong> triage = triaje · observation = observación · range = rango · priority = prioridad.</p><p><strong>Frame:</strong> The technician produced ____. I would report ____ first because ____ and ____.</p>",
                "FALLBACK": f'<p>All four licensed activity pages are embedded. If the workbook is unavailable or you need a more structured layout, use the optional {file_link(files["TRIAGE"]["id"], "Veterinary Triage Evidence Record")}. A private written response replaces discussion.</p>',
            },
            4: {
                "TITLE": "Xello Skills",
                "PURPOSE": "Complete the required Skills lesson and connect one transferable skill to veterinary work.",
                "TODAY": "<ul><li>complete Xello Skills;</li><li>identify one skill you use now;</li><li>connect it to two careers.</li></ul>",
                "READY": f'<p>Open {file_link(files["REFLECT"]["id"], "the private Skills Reflection")}.</p><p><strong>Prerequisite:</strong> at least three saved careers.</p>',
                "MEDIA": "",
                "STEPS": step(1, "Log in", "<p>ClassLink &gt; Xello &gt; Home &gt; Lessons. Tell the teacher now if Xello or the three-career prerequisite is blocked.</p>") + step(2, "Complete Skills", "<p>Use the full 35-minute lesson block. Read the examples before choosing an answer.</p>") + step(3, "Reflect privately", f'<p>Complete the PDF or <a href="{assignment_url}">open the private reflection assignment</a>. Use this frame: <strong>____ is useful in veterinary work when ____. It is useful in ____ when ____.</strong> Do not upload a profile screenshot.</p>'),
                "EXIT": "<p>Submit the private reflection. Your teacher verifies Xello completion through the report.</p>",
                "DONE": "<ul><li>Skills lesson completed or supervised catch-up recorded;</li><li>one current or teacher-provided skill named;</li><li>two-career transfer explained;</li><li>reflection kept private.</li></ul>",
                "SUPPORT": "<p><strong>Word bank:</strong> skill = habilidad · transferable = transferible · improve = mejorar · evidence = evidencia.</p><p><strong>Frame:</strong> ____ is useful in veterinary work when ____. It is useful in ____ when ____.</p>",
                "FALLBACK": "<p>If Xello or the prerequisite is blocked, select observation, communication, problem solving, teamwork, or organization on the reflection and mark the supervised catch-up box. Paper supports today's thinking; it does not count as Xello completion.</p>",
            },
            5: {
                "TITLE": "Build a Veterinary Pathway Recommendation",
                "PURPOSE": "Connect veterinary career evidence, the district workbook, and one realistic next step.",
                "TODAY": "<ul><li>read the Nimitz Animal Science opportunity in the workbook;</li><li>build a pathway recommendation;</li><li>self-check it with the rubric.</li></ul>",
                "READY": f'<p>Open {file_link(files["PATHWAY"]["id"], "the Veterinary Pathway Recommendation")} and {file_link(files["RUBRIC"]["id"], "the 16-point evidence rubric")}.</p>',
                "MEDIA": "",
                "STEPS": step(1, "Read the district pathway evidence", image_tag(uploads[5]["fyf-irving-ag-programs-1.png"]["id"], "Find Your Future Irving agriculture program information page 100", 650) + f'<p>{file_link(uploads[5]["fyf-irving-ag-programs-1.png"]["id"], "Open FYF p. 100 full size")}</p>' + image_tag(uploads[5]["fyf-irving-ag-programs-2.png"]["id"], "Find Your Future Irving agriculture program information page 101", 650) + f'<p>{file_link(uploads[5]["fyf-irving-ag-programs-2.png"]["id"], "Open FYF p. 101 full size")}</p><p>Record <strong>Animal Science</strong> and one experience exactly as the workbook presents them.</p>') + step(2, "Build the recommendation", "<p>Name one career, preparation route, daily task, labor-market fact, Animal Science opportunity, postsecondary requirement, and next action. Use this frame: <strong>I recommend ____ because ____. FYF shows ____. After high school, the student would still need ____. A useful next step is ____.</strong></p>") + step(3, "Self-check and revise", "<p>Use all four rubric criteria. Add evidence where a reader would otherwise have to guess.</p>"),
                "EXIT": "<p>Submit the recommendation and rubric check, then return materials.</p>",
                "DONE": "<ul><li>career and preparation accurate;</li><li>dated labor fact included;</li><li>Animal Science evidence from FYF pp. 100-101 used accurately;</li><li>high-school and postsecondary steps named;</li><li>rubric self-check complete.</li></ul>",
                "SUPPORT": "<p><strong>Word bank:</strong> pathway = trayectoria · credential = credencial · postsecondary = después de la preparatoria · next step = próximo paso.</p><p><strong>Frame:</strong> I recommend ____ because ____. FYF shows ____. After high school, the student would still need ____. A useful next step is ____.</p>",
                "FALLBACK": "<p>The PDFs and embedded workbook pages are complete. H&amp;L App Exploration is optional and does not require a screenshot.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Meet the Veterinary Team",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(2)(A)",
                "ALERT": "<strong>Use the fixed, dated evidence cards.</strong> Do not make H&amp;L or a live salary search load-bearing.",
                "PREP": f'<ul><li><strong>Per student:</strong> one FYF workbook, one two-page {file_link(files["CAREERS"]["id"], "evidence guide")} printed double-sided, and one pencil. A Canvas annotation/text-entry route may replace the print.</li><li><strong>Teacher:</strong> one display device with FYF p. 87.</li><li><strong>Grouping:</strong> independent reading and writing; pairs only for the four-minute evidence check.</li></ul>',
                "EVIDENCE": "<p>One chosen role supported by one daily task and one preparation requirement. This is formative preparation for the weekly minor packet.</p>",
                "FLOW": flow("#5a2d91", "Stop and Jot · 4", "Who works on a veterinary team, and what might that person do?") + flow("#4a9d2f", "FYF opener · 7", "Notice the range of agriculture and animal-care work on p. 87.") + flow("#1f617a", "Fixed evidence · 14", "Chunk the cards: duties first, then preparation and labor evidence.") + flow("#e3ad19", "Chosen-role response · 16", "Complete the guide's Day 1 choice with one task and one preparation fact.") + flow("#4a9d2f", "Partner evidence check · 4", "Partners point to the two source facts; they do not select a role for each other.") + flow("#1f617a", "Submit and reset · 5", "Store or submit the Day 1 choice and return materials."),
                "MONITOR": "<p><strong>Lap 1:</strong> after the duties chunk, students can point to one task for each role. If more than 25% confuse roles, pause and relabel the three rows. <strong>Lap 2:</strong> the chosen-role response names one task and one preparation requirement. If either is missing, point to the matching row. <strong>Key:</strong> veterinarian has the highest May 2024 U.S. median and longest preparation; veterinary assistant has the shortest typical entry route; veterinary technician usually requires an associate degree and state credential rules vary. <strong>Trim:</strong> skip optional H&amp;L and reduce the partner check to one fact; preserve the chosen-role response and five-minute reset.</p>",
                "RESOURCES": '<p><a href="https://www.bls.gov/ooh/healthcare/veterinary-assistants-and-laboratory-animal-caretakers.htm">BLS Veterinary Assistants</a> · <a href="https://www.bls.gov/ooh/healthcare/veterinary-technologists-and-technicians.htm">BLS Veterinary Technicians</a> · <a href="https://www.bls.gov/ooh/healthcare/veterinarians.htm">BLS Veterinarians</a></p>',
                "SUPPORT": "<p>Read cards aloud and keep labels beside numbers. The complete chosen-role frame sits beside the response space. Permit typed, written, dictated, or teacher-scribed evidence; score the evidence, not mechanics unless meaning is unclear.</p>",
                "FALLBACK": "<p>The fixed guide is the complete absence and no-login route. H&amp;L is optional enrichment only.</p>",
            },
            2: {
                "TITLE": "Compare Veterinary Career Paths",
                "SUBTITLE": "50 minutes · TEKS d(2)(A), d(5)(A)",
                "ALERT": "<strong>One salary basis.</strong> All three figures are May 2024 U.S. medians; none is starting pay, DFW-local pay, or a guarantee.",
                "PREP": f'<ul><li><strong>Per student:</strong> the Day 1 evidence guide, one two-page {file_link(files["COMPARE"]["id"], "comparison sheet")} printed double-sided, and one pencil. A Canvas route may replace the print.</li><li><strong>Teacher:</strong> one display device with a completed sample row.</li><li><strong>Grouping:</strong> independent table and scenario response; pairs may check labels after independent work.</li></ul>',
                "EVIDENCE": "<p>Completed three-role comparison plus one fictional-scenario recommendation using two accurate facts and one trade-off. Recommended minor packet evidence.</p>",
                "FLOW": flow("#5a2d91", "Stop and Jot · 4", "Rank career factors for a fictional student.") + flow("#4a9d2f", "Model measures · 8", "Complete one sample row and distinguish median, growth, openings, and preparation.") + flow("#1f617a", "Comparison · 22", "Students complete all six rows; partners may check labels after independent work.") + flow("#e3ad19", "One scenario · 11", "Choose Scenario A or B and recommend with two facts and one trade-off.") + flow("#1f617a", "Submit and reset · 5", "Store or submit the comparison and return materials."),
                "MONITOR": "<p><strong>Lap 1:</strong> after two rows, every number keeps its measure. If more than 25% write starting or DFW pay, stop and relabel the May 2024 U.S. median row. <strong>Lap 2:</strong> the chosen scenario response contains two accurate facts and one actual trade-off. If it is only a preference, send the student back to two labeled rows. <strong>Trim:</strong> finish fewer partner checks; do not cut the scenario recommendation or five-minute reset.</p>",
                "RESOURCES": f'<p>{file_link(files["CAREERS"]["id"], "Dated evidence guide")} · {file_link(files["RUBRIC"]["id"], "16-point rubric")}</p>',
                "SUPPORT": "<p>Keep the modeled row visible and place the complete recommendation frame beside the scenario response. Allow extra processing time, speech-to-text, keyboard entry, or teacher scribing.</p>",
                "FALLBACK": "<p>No login, search, or partner is required. The guide and comparison are the complete absence route.</p>",
            },
            3: {},
            4: {
                "TITLE": "Xello Skills",
                "SUBTITLE": "50 minutes · TEKS d(4)(B)",
                "ALERT": "<strong>Required Grade 8 task: Skills lesson, 35 minutes.</strong> Students need at least three saved careers. Earlier Life experiences and Volunteer hours are not repeated.",
                "PREP": f'<ul><li><strong>Per student:</strong> one internet-connected device and headphones. Provide the one-page {file_link(files["REFLECT"]["id"], "private reflection")} digitally or print one copy only for paper-route students.</li><li><strong>Teacher:</strong> one report-access device, one display device, the {file_link(files["XELLO_GUIDE"]["id"], "official facilitator guide")}, {file_link(files["XELLO_DECK"]["id"], "Irving-adapted slides")}, and optional {file_link(files["XELLO_SPANISH"]["id"], "Spanish support deck")}.</li><li><strong>Grouping:</strong> brief partner definition; Xello and reflection remain individual and private.</li></ul>',
                "EVIDENCE": "<p>Xello Completion Standards report and a private reflection comparing one skill in veterinary work and another career. No public profile screenshot.</p>",
                "FLOW": flow("#5a2d91", "Think-Pair-Share · 4", "Define a transferable skill and name two settings.") + flow("#4a9d2f", "Xello Skills · 35", "ClassLink &gt; Xello &gt; Home &gt; Lessons &gt; Skills.") + flow("#1f617a", "Private reflection · 8", "Compare one skill in veterinary work and another career.") + flow("#e3ad19", "Verify or record catch-up · 3", "Use the report or record a supervised catch-up need."),
                "MONITOR": "<p><strong>Minute 4:</strong> verify ClassLink and the three-saved-careers prerequisite. Blocked students select a teacher-provided skill, mark the catch-up box, and complete the transfer thinking without claiming Xello completion. <strong>Minute 20:</strong> students should be inside Skills; if more than 25% are still navigating, project the numbered route once. The official guide's 85-minute extension is teacher support, not another student requirement. <strong>Trim:</strong> omit optional discussion and extended-guide activities; preserve the assigned lesson, private reflection, and catch-up record.</p>",
                "RESOURCES": f'<p>{file_link(files["XELLO_GUIDE"]["id"], "Official extended facilitator guide")} · {file_link(files["XELLO_DECK"]["id"], "ClassLink launch slides")}</p>',
                "SUPPORT": "<p>Keep navigation visible; offer read-aloud, chunking, bilingual labels, the optional Spanish deck, and the point-of-use complete transfer frame. Do not infer student ability from a self-report result.</p>",
                "FALLBACK": "<p>If Xello or the prerequisite is blocked, use observation, communication, problem solving, teamwork, or organization for today's reflection and schedule supervised catch-up. Paper does not count as Xello completion.</p>",
            },
            5: {},
        }

        teacher[3] = {
            "TITLE": "Veterinary Triage",
            "SUBTITLE": "50 minutes · TEKS d(1)(C)",
            "ALERT": "<strong>Fictional simulation.</strong> Students observe, compare, prioritize, and report; they do not diagnose, prescribe, or advise treatment.",
            "PREP": f'<ul><li><strong>Per student:</strong> one FYF workbook opened to pp. 96-99, one pencil, and one device for the practice quiz.</li><li><strong>Optional print:</strong> one two-page {file_link(files["TRIAGE"]["id"], "structured triage record")} only for assigned students or an absent student without the workbook.</li><li><strong>Teacher:</strong> one display device with pp. 96-99 and the unpublished practice quiz.</li><li><strong>Grouping:</strong> private individual reasoning; an optional partner check may point to evidence without public performance.</li></ul>',
            "EVIDENCE": "<p>Completed FYF p. 99 notes for Leo and Barnaby, a decision naming who is seen first, and a two-observation defense that identifies the veterinary technician's role.</p>",
            "FLOW": flow("#5a2d91", "Stop and Jot · 4", "Separate an observation from a diagnosis.") + flow("#4a9d2f", "Patient charts · 8", "Read Leo and Barnaby before deciding.") + flow("#1f617a", "Compare ranges · 10", "Use the correct species reference.") + flow("#e3ad19", "Workbook decision · 18", "Complete p. 99 and defend the priority with two observations.") + flow("#4a9d2f", "Practice check · 5", "Retry with feedback.") + flow("#1f617a", "Submit and reset · 5", "Name the technician's work product, submit or store p. 99, and return materials."),
            "MONITOR": "<p><strong>Lap 1:</strong> observations come before any priority choice. If more than 25% diagnose, restate the boundary: observe, compare, prioritize, report. <strong>Lap 2:</strong> p. 99 uses the correct species reference and two case details; ask, “Which range or observation supports that?” when appearance controls the choice. <strong>Key:</strong> Barnaby is first because repeated unproductive retching, a painful distended abdomen, a heart rate of 150, and a weak pulse form the highest-risk cluster. Leo's cloudy eyes and dull skin match the supplied shedding reference. <strong>Pivot/trim:</strong> if devices fail or time compresses, preserve p. 99 and the five-minute reset; move the ungraded quiz to the next class opening.</p>",
            "RESOURCES": "<p>FYF pp. 96-99 carry the full activity and enough writing space. The custom record is an optional structured scaffold, not a default print requirement.</p>",
            "SUPPORT": "<p>Read charts aloud, chunk one patient at a time, highlight range columns, and allow a private written route. Use the point-of-use word bank and complete sentence frame. Do not grade acting or public speaking.</p>",
            "FALLBACK": "<p>All four activity pages and the optional record are in Canvas. Real animal concerns go to a qualified adult and veterinarian, not the classroom simulation.</p>",
        }
        teacher[5] = {
            "TITLE": "Veterinary Pathway Recommendation",
            "SUBTITLE": "50 minutes · TEKS d(2)(A), d(3)(A)",
            "ALERT": "<strong>Keep the district workbook in front.</strong> FYF pp. 100-101 are the primary local pathway source. Present program, certification, and experience details as opportunities, not guaranteed outcomes.",
            "PREP": f'<ul><li><strong>Per student:</strong> one FYF workbook, one two-page {file_link(files["PATHWAY"]["id"], "pathway recommendation")} printed double-sided or available through Canvas, and one {file_link(files["RUBRIC"]["id"], "rubric")} in print or Canvas.</li><li><strong>Teacher:</strong> one display device with FYF pp. 100-101. Use the public Nimitz page only as background for a current-detail question.</li><li><strong>Grouping:</strong> independent work; use private teacher conferences instead of requiring a public share.</li></ul>',
            "EVIDENCE": "<p>Two-page recommendation with career, preparation, daily task, dated labor fact, FYF pathway evidence, a postsecondary requirement, and a realistic middle-to-high-school next step. Recommended 16-point minor evidence packet.</p>",
            "FLOW": flow("#5a2d91", "Stop and Jot · 4", "Sort statements as fact, opportunity, or guarantee.") + flow("#4a9d2f", "Workbook evidence · 9", "Read FYF pp. 100-101 and record Animal Science exactly.") + flow("#1f617a", "Build recommendation · 22", "Use the labeled evidence sections and the complete point-of-use frame.") + flow("#e3ad19", "Rubric and revise · 10", "Self-check all four criteria.") + flow("#1f617a", "Submit and reset · 5", "Submit the recommendation and rubric check, then return materials."),
            "MONITOR": "<p><strong>Lap 1:</strong> students record <em>Animal Science</em> and one specific FYF experience or opportunity without renaming the program. <strong>Lap 2:</strong> the middle-school action and postsecondary requirement stay in sequence; if a response promises admission, certification, or employment, ask whether the source calls it a fact, opportunity, or guarantee. Accept any career choice supported with accurate evidence. Do not award extra points for H&amp;L or design polish. Use the approved 16-point rubric and mapped Canvas conversion. <strong>Trim:</strong> reduce the verbal debrief or focus a private conference on one rubric criterion; preserve the recommendation, submission, and reset.</p>",
            "RESOURCES": '<p>Primary: <em>Find Your Future</em> pp. 100-101. Teacher background only: <a href="https://nimitz.irvingisd.net/about-us/veterinary-science">Nimitz Veterinary Science page</a>. H&amp;L App Exploration remains optional enrichment.</p>',
            "SUPPORT": "<p>Use labeled short sections instead of requiring a paragraph. Permit speech-to-text, keyboard entry, enlarged print, and bilingual labels. The PDF provides enough space for each requested response.</p>",
            "FALLBACK": "<p>Canvas contains the complete evidence set. No live site, favorite count, or screenshot is required.</p>",
        }

        contracts = {
            1: {"TOPIC": "Veterinary Careers", "OBJECTIVE": "Students will identify three veterinary career opportunities, then describe one daily task and one preparation requirement for a chosen role.", "TEKS": "d(1)(C), d(2)(A)", "DOL": "Choose one veterinary role and support the choice with one daily-work fact and one preparation fact.", "STUDENT_OBJECTIVE": "identify three veterinary careers, then describe one daily task and one preparation requirement for a chosen role.", "STUDENT_DOL": "choose one role and support my choice with a daily-work fact and a preparation fact.", "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> median = mediana · training = formación · openings = vacantes.</p><p><strong>Frame:</strong> I would investigate ____ because the work includes ____ and the preparation requires ____.</p>"},
            2: {"TOPIC": "Career Evidence", "OBJECTIVE": "Students will describe preparation requirements and analyze pay, growth, and annual-opening evidence for three veterinary careers.", "TEKS": "d(2)(A), d(5)(A)", "DOL": "Complete the three-career comparison and recommend one role using two accurate facts and one trade-off.", "STUDENT_OBJECTIVE": "compare preparation, pay, growth, and openings for three veterinary careers.", "STUDENT_DOL": "complete the comparison and recommend one role using two facts and one trade-off.", "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> degree = título · openings = vacantes · trade-off = ventaja y costo.</p><p><strong>Frame:</strong> I recommend ____ because ____ and ____; however, ____.</p>"},
            3: {"TOPIC": "Veterinary Triage", "OBJECTIVE": "Students will identify the veterinary technician's role by using supplied evidence to observe, prioritize, and report on two fictional patients.", "TEKS": "d(1)(C)", "DOL": "Complete FYF p. 99 and name the veterinary technician's work product while defending the first-priority patient with two case details.", "STUDENT_OBJECTIVE": "use evidence to explain how a veterinary technician observes, prioritizes, and reports.", "STUDENT_DOL": "complete workbook p. 99 and defend which patient should be seen first with two case details.", "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> triage = triaje · observation = observación · range = rango · priority = prioridad.</p><p><strong>Frame:</strong> The technician produced ____. I would report ____ first because ____ and ____.</p>"},
            4: {"TOPIC": "Transferable Skills", "OBJECTIVE": "Students will identify how one skill transfers between veterinary work and another career by completing Xello Skills and a private evidence reflection.", "TEKS": "d(4)(B)", "DOL": "Xello Completion Standards report and a private reflection comparing how one skill appears in veterinary work and another career.", "STUDENT_OBJECTIVE": "explain how one skill can be used in veterinary work and another career.", "STUDENT_DOL": "complete Xello Skills and privately compare how one skill appears in veterinary work and another career.", "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> skill = habilidad · transferable = transferible · improve = mejorar.</p><p><strong>Frame:</strong> ____ is useful in veterinary work when ____. It is useful in ____ when ____.</p>"},
            5: {"TOPIC": "Veterinary Pathways", "OBJECTIVE": "Students will describe middle-school-to-high-school and high-school-to-postsecondary requirements for one veterinary career route using FYF and career evidence.", "TEKS": "d(2)(A), d(3)(A)", "DOL": "Complete a pathway recommendation that includes a career route, preparation evidence, one FYF pathway opportunity, one postsecondary requirement, and one realistic next step.", "STUDENT_OBJECTIVE": "describe the high-school and postsecondary steps for one veterinary career route.", "STUDENT_DOL": "complete a pathway recommendation with one FYF opportunity, one postsecondary requirement, and one next step.", "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> pathway = trayectoria · credential = credencial · postsecondary = después de la preparatoria · next step = próximo paso.</p><p><strong>Frame:</strong> I recommend ____ because ____. FYF shows ____. After high school, the student would still need ____. A useful next step is ____.</p>"},
        }

        day_names = {1: "Meet the Veterinary Team", 2: "Compare Veterinary Career Paths", 3: "Veterinary Triage", 4: "Xello Skills", 5: "Veterinary Pathway Recommendation"}
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            legacy_header_titles = ("Day 5 · Veterinary Pathway Brief",) if day == 5 else ()
            header = await upsert_header(client, module["id"], header_title, legacy_header_titles)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 3SW Wk1 Day {day} - {day_names[day]}"
            legacy_student_titles = ("STUDENT: 3SW Wk1 Day 5 - Veterinary Pathway Brief",) if day == 5 else ()
            student_page = await upsert_page(client, student_title, render("3sw-wk1-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, **contracts[day], **student[day]}), legacy_student_titles)
            teacher_title = f"TEACHER: 3SW Wk1 Day {day} Facilitator Guide"
            teacher_page = await upsert_page(client, teacher_title, render("3sw-wk1-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **contracts[day], **teacher[day]}))
            await upsert_module_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await upsert_module_item(client, module["id"], "Page", student_page["url"], student_title)
            pages[day] = {"teacher": teacher_page, "student": student_page}
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title)]
            if day == 3:
                await upsert_module_item(client, module["id"], "Quiz", quiz["id"], QUIZ_TITLE)
                order.append(("Quiz", quiz["id"], QUIZ_TITLE))
            if day == 4:
                await upsert_module_item(client, module["id"], "Assignment", assignment["id"], ASSIGNMENT_TITLE)
                order.append(("Assignment", assignment["id"], ASSIGNMENT_TITLE))
            if day == 5:
                await upsert_module_item(client, module["id"], "Assignment", minor["id"], MAPPED_MINOR_TITLE)
                order.append(("Assignment", minor["id"], MAPPED_MINOR_TITLE))

        items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")

        def matches_item(entry, kind, key):
            if entry.get("type") != kind:
                return False
            if kind == "SubHeader":
                return entry.get("id") == key
            if kind == "Page":
                return entry.get("page_url") == key
            return entry.get("content_id") == key

        keep_ids = set()
        for kind, key, _title in order:
            item = next((entry for entry in items if entry["id"] not in keep_ids and matches_item(entry, kind, key)), None)
            if item is None:
                raise RuntimeError(f"Missing expected module item: {kind} {key}")
            keep_ids.add(item["id"])
        for entry in items:
            if entry["id"] not in keep_ids:
                await api(client, "DELETE", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{entry['id']}")

        items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            matching = [entry for entry in items if matches_item(entry, kind, key)]
            if len(matching) != 1:
                raise RuntimeError(f"Expected one module item for {kind} {key}; found {len(matching)}")
            await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{matching[0]['id']}", data={"module_item[position]": position, "module_item[title]": title})

        final_items = sorted(await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items"), key=lambda entry: entry.get("position") or 0)
        module = await api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        quiz = await api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
        assignment = await api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignment['id']}")
        minor = await api(client, "GET", f"/courses/{COURSE_ID}/assignments/{minor['id']}")
        if module.get("published"):
            raise RuntimeError("3SW Wk1 module unexpectedly published")
        if quiz.get("published") or quiz.get("quiz_type") != "practice_quiz" or int(quiz.get("allowed_attempts") or 0) != -1:
            raise RuntimeError("3SW Wk1 practice quiz invariant failed")
        if assignment.get("published") or float(assignment.get("points_possible") or 0) != 0 or assignment.get("grading_type") != "not_graded" or not assignment.get("omit_from_final_grade"):
            raise RuntimeError("3SW Wk1 formative reflection invariant failed")
        if (
            minor.get("published")
            or float(minor.get("points_possible") or 0) != 100
            or minor.get("grading_type") != "points"
            or minor.get("omit_from_final_grade")
            or minor.get("assignment_group_id") != minor_group["id"]
        ):
            raise RuntimeError("3SW Wk1 mapped Minor invariant failed after module assembly")
        published_pages = [value["url"] for pair in pages.values() for value in pair.values() if value.get("published")]
        if published_pages:
            raise RuntimeError(f"Published 3SW Wk1 pages remain: {published_pages}")
        if not support_folder.get("locked") or any(not folder.get("locked") for folder in folders.values()):
            raise RuntimeError("One or more 3SW Wk1 Canvas folders remain unlocked")
        if len(final_items) != len(order):
            raise RuntimeError(f"Expected {len(order)} 3SW Wk1 module items; found {len(final_items)}")
        published_items = [entry.get("title") for entry in final_items if entry.get("published")]
        if published_items:
            raise RuntimeError(f"Published 3SW Wk1 module items remain: {published_items}")
        for position, ((kind, key, title), item) in enumerate(zip(order, final_items), 1):
            if item.get("position") != position or item.get("title") != title or not matches_item(item, kind, key):
                raise RuntimeError(f"3SW Wk1 module order mismatch at position {position}")
        print(json.dumps({"module": {"id": module["id"], "published": module["published"]}, "quiz": {"id": quiz["id"], "published": quiz.get("published"), "quiz_type": quiz.get("quiz_type"), "allowed_attempts": quiz.get("allowed_attempts")}, "assignment": {"id": assignment["id"], "published": assignment.get("published"), "grading_type": assignment.get("grading_type"), "omit_from_final_grade": assignment.get("omit_from_final_grade")}, "minor": {"id": minor["id"], "published": minor.get("published"), "points_possible": minor.get("points_possible"), "assignment_group_id": minor.get("assignment_group_id"), "grading_type": minor.get("grading_type"), "omit_from_final_grade": minor.get("omit_from_final_grade")}, "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"], "file_count": support_file_count}, "folders": {str(day): {"id": folder["id"], "locked": folder["locked"], "file_count": folder_file_counts[day]} for day, folder in folders.items()}, "files": {key: value["id"] for key, value in files.items()}, "pages": {str(day): {kind: {"url": value["url"], "published": value["published"]} for kind, value in pair.items()} for day, pair in pages.items()}, "items": [{"id": item["id"], "position": item["position"], "title": item["title"], "type": item["type"], "page_url": item.get("page_url")} for item in final_items]}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
