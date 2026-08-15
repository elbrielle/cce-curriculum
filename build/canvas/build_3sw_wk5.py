"""Build the unpublished 3SW Week 5 Cosmetology Canvas module."""

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
MODULE_NAME = "3SW Wk5: Style, Service, and Cosmetology Careers"
QUIZ_TITLE = "PRACTICE: Texas Cosmetology License and Safety Check"
RECOMMENDATION_TITLE = "MINOR 3: Cosmetology Career and Business Recommendation"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/3sw/wk5"
WORKSHEET_FILES = {
    "CONCEPT": "3sw-wk5-sfx-concept-lab-brief.pdf",
    "BUILD_RECORD": "3sw-wk5-sfx-build-test-record.pdf",
    "QUALITY": "3sw-wk5-sfx-quality-revision.pdf",
    "EVIDENCE": "3sw-wk5-texas-cosmetology-evidence-guide.pdf",
    "PATHWAY": "3sw-wk5-cosmetology-pathway-decision.pdf",
    "CAMPAIGN": "3sw-wk5-salon-wellness-campaign.pdf",
    "RECOMMENDATION": "3sw-wk5-cosmetology-recommendation.pdf",
    "RUBRIC": "3sw-wk5-cosmetology-minor-rubric.pdf",
}
VISUAL_FILES = {
    1: (
        "fyf-human-services-opener.jpg",
        "fyf-sfx-research.jpg",
        "fyf-sfx-concept-card.jpg",
    ),
    2: ("fyf-sfx-build.jpg",),
    3: ("fyf-sfx-quality-check.jpg",),
    4: ("fyf-stress-toolkit.jpg", "fyf-stress-posts.jpg"),
    5: (
        "fyf-irving-cosmetology-context.jpg",
        "fyf-student-enterprise-context.jpg",
    ),
}


def preflight():
    required = [
        TEMPLATES / "3sw-wk5-student.html",
        TEMPLATES / "3sw-wk5-teacher.html",
        *(
            ROOT / "docs/resources/worksheets" / name
            for name in WORKSHEET_FILES.values()
        ),
        *(
            ASSETS / f"day{day}" / name
            for day, names in VISUAL_FILES.items()
            for name in names
        ),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"3SW Wk5 preflight missing required files: {missing}")


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
    matches = [module for module in modules if module["name"] == MODULE_NAME]
    if len(matches) > 1:
        raise RuntimeError(
            f"Expected at most one module named {MODULE_NAME!r}; found {len(matches)}"
        )
    if matches:
        found = matches[0]
        return await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{found['id']}",
            data={"module[name]": MODULE_NAME, "module[published]": "false"},
        )
    return await api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/modules",
        data={"module[name]": MODULE_NAME, "module[published]": "false"},
    )


async def ensure_folder(client, path):
    current, folder = "", None
    for name in path.split("/")[1:]:
        target = f"{current}/{name}".strip("/")
        encoded = httpx.URL("/" + target).raw_path.decode("ascii").lstrip("/")
        response = await client.get(
            f"{BASE}/api/v1/courses/{COURSE_ID}/folders/by_path/{encoded}"
        )
        if response.status_code == 200 and response.json():
            folder = response.json()[-1]
        else:
            folder = await api(
                client,
                "POST",
                f"/courses/{COURSE_ID}/folders",
                data={
                    "name": name,
                    "parent_folder_path": "course files"
                    + (f"/{current}" if current else ""),
                    "locked": "true",
                },
            )
        current = target
    if folder and not folder.get("locked"):
        folder = await api(
            client, "PUT", f"/folders/{folder['id']}", data={"locked": "true"}
        )
    return folder


async def upload(client, path, folder_path):
    start = await api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/files",
        data={
            "name": path.name,
            "parent_folder_path": folder_path,
            "on_duplicate": "overwrite",
        },
    )
    response = await client.post(
        start["upload_url"],
        data=start["upload_params"],
        files={
            "file": (
                path.name,
                path.read_bytes(),
                mimetypes.guess_type(path.name)[0] or "application/octet-stream",
            )
        },
        follow_redirects=True,
    )
    response.raise_for_status()
    uploaded = response.json()
    record = await api(
        client, "PUT", f"/files/{uploaded['id']}", data={"locked": "true"}
    )
    if not record.get("locked"):
        raise RuntimeError(f"Canvas did not lock uploaded file {path.name!r}")
    return record


async def lock_folder_files(client, folder):
    current = await api(client, "GET", f"/folders/{folder['id']}")
    if not current.get("locked"):
        current = await api(
            client, "PUT", f"/folders/{folder['id']}", data={"locked": "true"}
        )
    if not current.get("locked"):
        raise RuntimeError(
            f"Canvas did not lock folder {folder.get('full_name') or folder['id']}"
        )
    for entry in await paged(client, f"/folders/{folder['id']}/files"):
        if not entry.get("locked"):
            await api(
                client, "PUT", f"/files/{entry['id']}", data={"locked": "true"}
            )
    final = await paged(client, f"/folders/{folder['id']}/files")
    unlocked = [
        entry.get("display_name") or entry.get("filename")
        for entry in final
        if not entry.get("locked")
    ]
    if unlocked:
        raise RuntimeError(f"Unlocked files remain in folder {folder['id']}: {unlocked}")
    return current


def render(template, values):
    text = (TEMPLATES / template).read_text()
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    unresolved = sorted(set(re.findall(r"\{\{[^}]+\}\}", text)))
    if unresolved:
        raise ValueError(f"Unresolved values in {template}: {unresolved}")
    return text


async def upsert_page(client, title, body):
    url = slugify(title)
    data = {
        "wiki_page[title]": title,
        "wiki_page[body]": body,
        "wiki_page[published]": "false",
        "wiki_page[editing_roles]": "teachers",
    }
    response = await client.get(f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{url}")
    if response.status_code == 200:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/pages/{url}", data=data)
    if response.status_code != 404:
        response.raise_for_status()
    return await api(client, "POST", f"/courses/{COURSE_ID}/pages", data=data)


async def require_minor_preflight(client):
    groups = await paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group_matches = [
        entry for entry in groups if entry.get("name") == "Minor Assessments (40%)"
    ]
    if len(group_matches) != 1:
        raise RuntimeError(
            "Expected exactly one assignment group named 'Minor Assessments (40%)'; "
            f"found {len(group_matches)}"
        )
    group = group_matches[0]
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [
        entry for entry in assignments if entry.get("name") == RECOMMENDATION_TITLE
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one existing mapped Minor assignment named {RECOMMENDATION_TITLE!r}; found {len(matches)}"
        )
    found = matches[0]
    if (
        found.get("published")
        or float(found.get("points_possible") or 0) != 100
        or found.get("assignment_group_id") != group["id"]
        or found.get("grading_type") != "points"
        or found.get("omit_from_final_grade") is not False
    ):
        raise RuntimeError(
            f"Mapped Minor invariant failed before module writes: "
            f"published={found.get('published')}, points={found.get('points_possible')}, "
            f"group={found.get('assignment_group_id')}, grading={found.get('grading_type')}, "
            f"omit={found.get('omit_from_final_grade')}"
        )
    return found, group


async def update_minor_assignment(client, found, group):
    description = "<p>Submit the private Cosmetology Career and Business Recommendation as typed text, a file, or an approved audio response. Use an accurate career task, current Texas training or license evidence, a verified next step, an entrepreneurship opportunity and responsibility, a trade-off, and one design-to-career connection. Paper is equal.</p>"
    rubric_note = re.search(
        r'<div data-cce-rubric-note="[^"]+".*?</div>',
        found.get("description") or "",
        flags=re.I | re.S,
    )
    if rubric_note:
        description += rubric_note.group(0)
    recommendation = await api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{found['id']}",
        data={
            "assignment[description]": description,
            "assignment[submission_types][]": [
                "online_upload",
                "online_text_entry",
                "media_recording",
            ],
            "assignment[published]": "false",
        },
    )
    if (
        recommendation.get("published")
        or float(recommendation.get("points_possible") or 0) != 100
        or recommendation.get("assignment_group_id") != group["id"]
        or recommendation.get("grading_type") != "points"
        or recommendation.get("omit_from_final_grade") is not False
    ):
        raise RuntimeError(
            f"Minor invariant failed after update: published={recommendation.get('published')}, "
            f"points={recommendation.get('points_possible')}, "
            f"group={recommendation.get('assignment_group_id')}, "
            f"grading={recommendation.get('grading_type')}, "
            f"omit={recommendation.get('omit_from_final_grade')}"
        )
    return recommendation


QUESTIONS = [
    (
        "Q1 - Operator course",
        "What does the current Texas Cosmetology Operator route require before the exams?",
        "A 1,000-hour operator course at a TDLR-licensed school.",
        [
            "A 500-hour online course from any website.",
            "An informal apprenticeship with any salon owner.",
            "Only a high school diploma.",
        ],
        "Correct. The course must be 1,000 hours at a licensed school.",
        "The current TDLR operator page does not list an informal apprenticeship route.",
    ),
    (
        "Q2 - Exams",
        "Which exams does the current Texas Cosmetology Operator route require?",
        "A written exam and a practical exam.",
        [
            "Only a written exam.",
            "Only a practical exam.",
            "No exam after the training hours.",
        ],
        "Correct. Both exams are required.",
        "Recheck the dated TDLR evidence guide: written and practical exams are separate steps.",
    ),
    (
        "Q3 - Unknown local facts",
        "The evidence guide does not give the exact family cost of an Irving ISD route. What should a student do?",
        "Ask the current counselor, CTE office, or coursebook and label the fact as unknown until verified.",
        [
            "Write $0 because it is a public school.",
            "Copy the price of a private school.",
            "Skip the question and claim cost does not matter.",
        ],
        "Correct. A useful decision separates verified facts from unanswered local questions.",
        "Do not invent cost, hours, transportation, or admission information.",
    ),
    (
        "Q4 - Wage label",
        "The evidence guide lists $16.95 per hour. What does that number mean?",
        "May 2024 U.S. median hourly wage for hairdressers, hairstylists, and cosmetologists.",
        [
            "Guaranteed DFW starting pay.",
            "The minimum wage for every Texas salon.",
            "The exact pay after one year.",
        ],
        "Correct. Keep the year, geography, occupation, and measure attached.",
        "The figure is a national median, not local starting pay or a guarantee.",
    ),
    (
        "Q5 - Lab boundary",
        "Where may a student build the classroom SFX texture model?",
        "On the teacher-approved practice surface or in an approved digital tool.",
        [
            "On a classmate's arm.",
            "On the student's face.",
            "On clothing that someone is wearing.",
        ],
        "Correct. Classroom materials never go on a person.",
        "The lab boundary is non-negotiable: practice surface or approved digital tool only.",
    ),
]


async def prepare_quiz_questions(client, quiz_id, desired_names):
    existing = await paged(
        client, f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions"
    )
    keep, seen = [], set()
    for question in existing:
        name = question.get("question_name")
        if name not in desired_names or name in seen:
            await api(
                client,
                "DELETE",
                f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions/{question['id']}",
            )
        else:
            seen.add(name)
            keep.append(question)
    return keep


async def finalize_quiz_order(client, quiz_id, expected_names):
    final = await paged(
        client, f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions"
    )
    by_name = {entry.get("question_name"): entry for entry in final}
    if set(by_name) != set(expected_names) or len(final) != len(expected_names):
        raise RuntimeError(
            f"Quiz {quiz_id} question mismatch: {[entry.get('question_name') for entry in final]}"
        )
    fields = []
    for name in expected_names:
        fields.extend(
            [
                ("order[][id]", str(by_name[name]["id"])),
                ("order[][type]", "question"),
            ]
        )
    await api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/quizzes/{quiz_id}/reorder",
        content=urlencode(fields),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    ordered = await paged(
        client, f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions"
    )
    actual = [entry.get("question_name") for entry in ordered]
    if actual != expected_names:
        raise RuntimeError(
            f"Quiz {quiz_id} order mismatch: expected {expected_names}, found {actual}"
        )


async def upsert_quiz(client):
    quizzes = await paged(client, f"/courses/{COURSE_ID}/quizzes")
    matches = [entry for entry in quizzes if entry.get("title") == QUIZ_TITLE]
    if len(matches) > 1:
        raise RuntimeError(
            f"Duplicate quizzes named {QUIZ_TITLE!r}: {[entry['id'] for entry in matches]}"
        )
    quiz = matches[0] if matches else None
    data = {
        "quiz[title]": QUIZ_TITLE,
        "quiz[description]": "<p>Ungraded optional practice after the core pathway decision or during recovery. Retry and use the feedback.</p>",
        "quiz[quiz_type]": "practice_quiz",
        "quiz[published]": "false",
        "quiz[allowed_attempts]": "-1",
        "quiz[show_correct_answers]": "true",
        "quiz[shuffle_answers]": "false",
    }
    quiz = await api(
        client,
        "PUT" if quiz else "POST",
        (
            f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
            if quiz
            else f"/courses/{COURSE_ID}/quizzes"
        ),
        data=data,
    )
    expected = [spec[0] for spec in QUESTIONS]
    existing = await prepare_quiz_questions(client, quiz["id"], set(expected))
    for position, (
        name,
        question_text,
        correct,
        wrong,
        correct_comment,
        incorrect_comment,
    ) in enumerate(QUESTIONS, 1):
        found = next(
            (entry for entry in existing if entry.get("question_name") == name), None
        )
        payload = {
            "question": {
                "question_name": name,
                "question_text": question_text,
                "question_type": "multiple_choice_question",
                "position": position,
                "points_possible": 1,
                "correct_comments": correct_comment,
                "incorrect_comments": incorrect_comment,
                "answers": [{"answer_text": correct, "answer_weight": 100}]
                + [{"answer_text": answer, "answer_weight": 0} for answer in wrong],
            }
        }
        path = (
            f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{found['id']}"
            if found
            else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        )
        await api(client, "PUT" if found else "POST", path, json=payload)
    await finalize_quiz_order(client, quiz["id"], expected)
    final = await api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
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
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
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
        return await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{found['id']}",
            data={
                "module_item[title]": title,
                "module_item[published]": "false",
            },
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
    return await api(
        client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data=data
    )


def file_link(file_id, label):
    return f'<a href="/courses/{COURSE_ID}/files/{file_id}/preview" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">{label}</a>'


def image_tag(file_id, alt, max_width=700):
    return f'<img src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" loading="lazy" style="display:block;width:100%;max-width:{max_width}px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'


def step(number, title, body):
    return f'<h3 style="color:#5a2d91;border-bottom:3px solid #d9c9ed">{number}. {title}</h3>{body}'


def flow(color, title, text):
    return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'


async def main():
    preflight()
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as client:
        recommendation, minor_group = await require_minor_preflight(client)
        module = await ensure_module(client)
        support = "course files/CCR Materials/3SW/Wk5"
        support_folder = await ensure_folder(client, support)
        names = WORKSHEET_FILES
        files = {
            key: await upload(
                client, ROOT / "docs/resources/worksheets" / name, support
            )
            for key, name in names.items()
        }
        quiz = await upsert_quiz(client)
        recommendation = await update_minor_assignment(
            client, recommendation, minor_group
        )

        selected_visuals = VISUAL_FILES
        folders, visuals = {}, {}
        for day, day_names in selected_visuals.items():
            folder_path = f"course files/CCR Materials/3SW/Wk5/Day {day} Visuals"
            folders[day], visuals[day] = await ensure_folder(client, folder_path), {}
            for name in day_names:
                visuals[day][name] = await upload(
                    client, ASSETS / f"day{day}" / name, folder_path
                )

        support_folder = await lock_folder_files(client, support_folder)
        for day in range(1, 6):
            folders[day] = await lock_folder_files(client, folders[day])

        quiz_url = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        recommendation_url = f"/courses/{COURSE_ID}/assignments/{recommendation['id']}"

        contracts = {
            1: {
                "TOPIC": "Career Clusters",
                "OBJECTIVE": "Students will explore and describe the Human Services career cluster and identify career opportunities within the cluster using a labeled SFX texture concept.",
                "TEKS": "d(1)(B), d(1)(C)",
                "DOL": "Completed FYF pp. 128-129 research and concept card plus a career-task and transferable-skill check.",
                "STUDENT_OBJECTIVE": "describe Human Services work and connect one career task to an SFX design skill.",
                "STUDENT_DOL": "complete FYF pp. 128-129 and the career-task and transferable-skill check.",
                "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> prosthetic = made piece added to change appearance · texture = how a surface looks or feels · layer = one piece placed over another.</p><p><strong>Use this frame:</strong> A ____ uses ____ to ____. Today's design skill transfers because ____.</p>",
            },
            2: {
                "TOPIC": "Career Opportunities",
                "OBJECTIVE": "Students will identify a theatrical or performance makeup career opportunity by following a texture map, testing a layered model, and documenting one revision.",
                "TEKS": "d(1)(C)",
                "DOL": "Finished texture model plus the one-page SFX Build and Test Record with a career documentation connection.",
                "STUDENT_OBJECTIVE": "build, test, and document a layered texture model the way an SFX artist records a revision.",
                "STUDENT_DOL": "finish the model and one-page build/test record, including the career documentation connection.",
                "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> align = stay in the intended position · flatten = lose raised shape · detach = come apart · revise = make a useful change.</p><p><strong>Use this frame:</strong> An SFX artist would document this change because ____.</p>",
            },
            3: {
                "TOPIC": "Career Preparation",
                "OBJECTIVE": "Students will research and describe current Texas cosmetology training and license requirements and investigate the steps required to enter high-school or postsecondary training using a pathway decision.",
                "TEKS": "d(2)(A), d(3)(G)",
                "DOL": "Completed FYF p. 131 quality check plus the two-page Cosmetology Pathway Decision.",
                "STUDENT_OBJECTIVE": "compare two training settings without inventing missing facts and put the Texas license steps in order.",
                "STUDENT_DOL": "complete FYF p. 131 and the two-page pathway decision with one verified fact and one unanswered question.",
                "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> license = state permission for regulated work · route = place or sequence used to prepare · requirement = condition every applicant must meet · unknown = fact the source does not establish.</p><p><strong>Use this frame:</strong> I recommend ____ because the evidence says ____. Before enrolling, Alex still needs to ask ____.</p>",
            },
            4: {
                "TOPIC": "Entrepreneurship",
                "OBJECTIVE": "Students will define entrepreneurship and identify a beauty-industry opportunity and owner responsibilities using a fictional wellness campaign.",
                "TEKS": "d(3)(I)",
                "DOL": "FYF p. 133 three-post series plus the two-page Salon and Wellness Campaign Companion.",
                "STUDENT_OBJECTIVE": "design a fictional beauty business and explain how accurate communication supports the client and the owner.",
                "STUDENT_DOL": "complete the three-post series in FYF p. 133 and the two-page business, safety, revision, and trust companion.",
                "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> client = customer · service = work provided for a client · responsibility = work the owner must manage · trust = confidence built through accurate actions.</p><p><strong>Use this frame:</strong> This campaign could build trust because ____. The owner must still ____.</p>",
            },
            5: {
                "TOPIC": "Career Opportunities",
                "OBJECTIVE": "Students will use career, license, program, entrepreneurship, and design evidence to make an individual recommendation.",
                "TEKS": "d(1)(C), d(2)(A), d(3)(G), d(3)(I)",
                "DOL": "Cosmetology Career and Business Recommendation with rubric self-check.",
                "STUDENT_OBJECTIVE": "recommend one Human Services career using accurate preparation, next-step, business, trade-off, and design evidence.",
                "STUDENT_DOL": "submit a six-to-eight-sentence recommendation and design-to-career connection after the rubric self-check.",
                "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> recommendation = choice supported by reasons · verified = checked in a named source · responsibility = work the owner must manage · trade-off = benefit plus cost or limit.</p><p><strong>Use this frame:</strong> I recommend ____ because ____. Texas requires ____. One trade-off is ____.</p>",
            },
        }

        student = {
            1: {
                "TITLE": "Human Services and SFX Texture Concept",
                "PURPOSE": "Plan a believable texture transformation and connect the design work to Human Services careers.",
                "TODAY": "<ul><li>identify Human Services careers;</li><li>explain texture and layering;</li><li>create a labeled texture map.</li></ul>",
                "READY": f'<p><strong>Default route:</strong> open your workbook to FYF pp. 127-129. Use {file_link(files["CONCEPT"]["id"], "the three-page no-workbook concept brief")} only if you cannot write in the workbook. Do not complete both.</p><p>Gather colored pencils and the teacher-provided index card for the individual exit check.</p>',
                "MEDIA": image_tag(
                    visuals[1]["fyf-human-services-opener.jpg"]["id"],
                    "Find Your Future Human Services cluster opener",
                )
                + image_tag(
                    visuals[1]["fyf-sfx-research.jpg"]["id"],
                    "Find Your Future Special Effects Makeup research challenge",
                )
                + image_tag(
                    visuals[1]["fyf-sfx-concept-card.jpg"]["id"],
                    "Find Your Future SFX texture style guide and concept card",
                ),
                "STEPS": step(
                    1,
                    "Open the cluster",
                    "<p>Name three Human Services careers and one task or client need for each.</p>",
                )
                + step(
                    2,
                    "Read the challenge",
                    "<p>Answer the research questions on FYF p. 128. Rehearse aloud before writing if helpful.</p>",
                )
                + step(
                    3,
                    "Choose one main texture",
                    "<p>Select scaled, cracked, wrinkled, or rock/geode. Use at most one secondary texture.</p>",
                )
                + step(
                    4,
                    "Draw the texture map",
                    "<p>Complete the concept card on FYF p. 129. Label three layers or material choices and show where the texture spreads.</p>",
                ),
                "EXIT": "<p>On the teacher-provided index card, write your name and complete: <strong>A ____ uses ____ to ____. Today's design skill transfers because ____.</strong> Turn in the card before reset.</p>",
                "DONE": "<ul><li>FYF p. 128 research;</li><li>FYF p. 129 concept card;</li><li>three sketch labels;</li><li>career-task and transferable-skill check.</li></ul>",
                "SUPPORT": "<p>texture = textura · layer = capa · scale = escama · crack = grieta. Use the embedded style guide and two teacher-selected texture choices.</p>",
                "FALLBACK": "<p>The embedded FYF pages show the full activity. Use the three-page brief only when you cannot write in the workbook. H&amp;L is optional and no screenshot is required.</p>",
            },
            2: {
                "TITLE": "Build and Test the SFX Texture Model",
                "PURPOSE": "Turn the texture map into a layered model, then test and revise it safely.",
                "TODAY": "<ul><li>build on an approved practice surface;</li><li>overlap at least three pieces or layers;</li><li>record a test and revision.</li></ul>",
                "READY": f'<p>Open your FYF p. 129 concept map and {file_link(files["BUILD_RECORD"]["id"], "the one-page SFX Build and Test Record")}. Use the teacher-approved dry, digital, or optional campus-approved lab route.</p><p><strong>Safety boundary:</strong> no classroom material goes on a person, clothing, face, arm, hair, or skin.</p>',
                "MEDIA": image_tag(
                    visuals[2]["fyf-sfx-build.jpg"]["id"],
                    "Find Your Future SFX build sequence; classroom safety routes replace direct skin application",
                ),
                "STEPS": step(
                    1,
                    "Set the structure",
                    "<p>Place the largest shape or digital layer first.</p>",
                )
                + step(
                    2,
                    "Overlap",
                    "<p>Add at least three visible layers that support the main texture.</p>",
                )
                + step(
                    3,
                    "Test from three feet",
                    "<p>Check whether the texture still reads clearly and whether pieces stay aligned.</p>",
                )
                + step(
                    4,
                    "Record the change",
                    "<p>Use the one-page record for the result, one success, one problem, and one revision. <strong>Complete frame:</strong> An SFX artist would document this change because ____.</p>",
                ),
                "EXIT": "<p>A model has many details but no clear main texture. What should the artist change first, and why?</p>",
                "DONE": "<ul><li>approved practice surface;</li><li>three overlapping layers;</li><li>one-page test record;</li><li>one revision and career documentation connection;</li><li>clean work area.</li></ul>",
                "SUPPORT": "<p>overlap = superponer · align = alinear · revise = revisar. Pre-cut paper and a digital layered mockup are equal.</p>",
                "FALLBACK": "<p>Use the dry relief or digital route. An adhesive lab is never required for absence recovery or grading.</p>",
            },
            3: {
                "TITLE": "Quality Check and Texas Cosmetology Pathways",
                "PURPOSE": "Use visible evidence to revise a design and current sources to compare two training settings.",
                "TODAY": "<ul><li>rate and revise the SFX model;</li><li>identify Texas license steps;</li><li>compare high-school and postsecondary training.</li></ul>",
                "READY": f'<p>Open your workbook to FYF p. 131, {file_link(files["EVIDENCE"]["id"], "the dated Texas evidence guide")}, and {file_link(files["PATHWAY"]["id"], "the two-page Pathway Decision")}. Use {file_link(files["QUALITY"]["id"], "the enlarged no-workbook quality sheet")} only when you cannot write on FYF p. 131.</p>',
                "MEDIA": image_tag(
                    visuals[3]["fyf-sfx-quality-check.jpg"]["id"],
                    "Find Your Future SFX quality check, problem solving, and improvement plan",
                ),
                "STEPS": step(
                    1,
                    "Rate the evidence",
                    "<p>Complete the quality check, problem-solving response, and improvement plan on FYF p. 131.</p>",
                )
                + step(
                    2,
                    "Mark the current facts",
                    "<p>Box 1,000 hours; underline both exams; star age and fee; bracket the current Irving ISD campus list.</p>",
                )
                + step(
                    3,
                    "Compare two settings",
                    "<p>Do not invent cost, schedule, transportation, admission, or high-school hours. <strong>Complete frame:</strong> I recommend ____ because the evidence says ____. Before enrolling, Alex still needs to ask ____.</p>",
                )
                + step(
                    4,
                    "Optional practice",
                    f'<p>If the core pathway decision is complete or your teacher assigns recovery, <a href="{quiz_url}">open the license and safety practice check</a>. Retry and use the feedback.</p>',
                ),
                "EXIT": "<p>What state requirement stays the same in both settings, and what local question could change the decision?</p>",
                "DONE": "<ul><li>FYF p. 131 quality check;</li><li>two-setting pathway comparison;</li><li>one verified fact and one unanswered question;</li><li>five license steps in order.</li></ul>",
                "SUPPORT": "<p>license = licencia · training = capacitación · exam = examen · fee = tarifa. Read one evidence section at a time.</p>",
                "FALLBACK": "<p>The fixed guide and worksheets contain every required fact. No live TDLR navigation or partner is required.</p>",
            },
            4: {
                "TITLE": "Salon Entrepreneurship and Wellness Communication",
                "PURPOSE": "Design a fictional beauty business and one useful, safe wellness campaign post.",
                "TODAY": "<ul><li>define a business opportunity;</li><li>identify owner responsibilities;</li><li>create and revise one private campaign post.</li></ul>",
                "READY": f'<p>Open your workbook to FYF pp. 132-133 and {file_link(files["CAMPAIGN"]["id"], "the two-page Salon and Wellness Campaign Companion")}. Paper, Canva, and Adobe Express are equal.</p><p>Use a fictional business and customer. Do not create a real account or public post.</p>',
                "MEDIA": image_tag(
                    visuals[4]["fyf-stress-toolkit.jpg"]["id"],
                    "Find Your Future Stress Toolkit technique table",
                )
                + image_tag(
                    visuals[4]["fyf-stress-posts.jpg"]["id"],
                    "Find Your Future three-post campaign and partner review directions",
                ),
                "STEPS": step(
                    1,
                    "Define the business",
                    "<p>Name the service, fictional customer, location type, meaningful difference, and one owner skill.</p>",
                )
                + step(
                    2,
                    "Map the customer experience",
                    "<p>Complete the scheduling, service, sanitation, records, and access path.</p>",
                )
                + step(
                    3,
                    "Create one polished post",
                    "<p>On FYF p. 133, use one technique, a headline, plain explanation, realistic tip, and visual. Use the other two frames for rough plans.</p>",
                )
                + step(
                    4,
                    "Run the safety check",
                    "<p>Use the companion to remove medical advice, guaranteed results, real details, and unclear language. Record one revision. <strong>Complete frame:</strong> This campaign could build trust because ____. The owner must still ____.</p>",
                ),
                "EXIT": "<p>How can a useful post build trust without replacing professional help?</p>",
                "DONE": "<ul><li>business concept and service map;</li><li>FYF p. 133 one polished post and two rough plans;</li><li>reader and safety check;</li><li>one revision;</li><li>entrepreneurship connection.</li></ul>",
                "SUPPORT": "<p>customer = cliente · owner = propietario · wellness = bienestar · trust = confianza. Private self-check is equal to partner feedback.</p>",
                "FALLBACK": "<p>The PDF and embedded pages are the complete route. No public post, real account, or personal wellness disclosure is required.</p>",
            },
            5: {
                "TITLE": "Cosmetology Career and Business Recommendation",
                "PURPOSE": "Use the week's evidence to recommend one Human Services career and explain a related business opportunity.",
                "TODAY": "<ul><li>audit the evidence;</li><li>plan five evidence jobs;</li><li>write, self-score, revise, and submit privately.</li></ul>",
                "READY": f'<p>Open {file_link(files["RECOMMENDATION"]["id"], "the recommendation")}, {file_link(files["RUBRIC"]["id"], "the 16-point rubric")}, and {file_link(files["EVIDENCE"]["id"], "the Texas evidence guide")}.</p>',
                "MEDIA": image_tag(
                    visuals[5]["fyf-irving-cosmetology-context.jpg"]["id"],
                    "Find Your Future Irving ISD cosmetology program context",
                )
                + image_tag(
                    visuals[5]["fyf-student-enterprise-context.jpg"]["id"],
                    "Find Your Future student enterprise, license, and SkillsUSA context",
                ),
                "STEPS": step(
                    1,
                    "Audit the evidence",
                    "<p>Check the career task, Texas requirement, current next step, owner responsibility, and trade-off.</p>",
                )
                + step(
                    2,
                    "Plan for Jordan",
                    "<p>Complete all five planning fields before drafting.</p>",
                )
                + step(
                    3,
                    "Write and connect",
                    "<p>Write 6-8 sentences, then connect one design decision to a career skill. <strong>Complete frames:</strong> I recommend ____ because ____. Texas requires ____. A verified next step is ____. One opportunity is ____, and the owner must ____. One trade-off is ____. My ____ design shows ____ because ____.</p>",
                )
                + step(
                    4,
                    "Self-score and submit",
                    f'<p>Revise one weak criterion, then <a href="{recommendation_url}">open the private recommendation assignment</a> or submit the paper copy.</p>',
                ),
                "EXIT": "<p>Which evidence changed the recommendation most, and why do the other factors still matter?</p>",
                "DONE": "<ul><li>6-8 sentence recommendation;</li><li>accurate task and Texas fact;</li><li>verified next step;</li><li>opportunity, responsibility, and trade-off;</li><li>design-to-career connection;</li><li>rubric revision.</li></ul>",
                "SUPPORT": "<p>recommendation = recomendación · evidence = evidencia · responsibility = responsabilidad · trade-off = beneficio y límite. Typed, speech-to-text, and approved audio are equal.</p>",
                "FALLBACK": "<p>The fixed packet is the full route. Xello Career Factors, eDynamic 4.2, and H&amp;L favorites are optional extensions only.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Human Services and SFX Texture Concept",
                "SUBTITLE": "50 minutes · TEKS d(1)(B), d(1)(C)",
                "ALERT": "<strong>The workbook is the default work surface.</strong> The three-page concept brief is only for a student who cannot write in FYF pp. 128-129. Its last page preserves the full-size concept sketch the workbook otherwise supplies.",
                "PREP": f'<ul><li><strong>Default print count: 0.</strong> Students use FYF pp. 127-129. Print one copy of {file_link(files["CONCEPT"]["id"], "the three-page no-workbook concept brief")} only for each student without the workbook.</li><li>Place one index card per student for the individual career-task and transferable-skill exit check.</li><li>Project the licensed workbook pages and the supplied model below; no teacher-created sample is required.</li><li>Students work individually. Pairs are for oral rehearsal only.</li></ul>',
                "MODEL": "<p><strong>Strong texture map:</strong> Main texture: cracked stone. Build route: dry paper relief. Labels: torn-cardboard base, overlapping paper cracks, darker center lines, smaller cracks spreading outward. <strong>Cluttered non-example:</strong> scales, fur, glitter, wrinkles, and cracks appear with no main texture. Ask: Which plan could a builder follow without asking the artist what to do?</p>",
                "EVIDENCE": "<p>FYF pp. 128-129 research and concept card, three useful sketch labels, and the named index-card career-task and transferable-skill check. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Notice visible texture clues.")
                + flow(
                    "#4a9d2f", "Human Services · 8", "Three careers and client needs."
                )
                + flow("#1f617a", "SFX research · 8", "Prosthetic, texture, layering.")
                + flow(
                    "#e3ad19",
                    "Concept map · 22",
                    "One main texture, materials, colors, labels.",
                )
                + flow("#1f617a", "Exit and reset · 7", "Collect the career-task check and return materials."),
                "MONITOR": "<p><strong>District response move:</strong> Stop and Jot one visible texture clue, then Turn and Talk before writing. <strong>Lap 1, minute 13:</strong> every student has three Human Services careers and one task or client need. If several students list appearance words instead of work, model one task: “A hair stylist consults with a client before cutting or styling.” <strong>Lap 2, minute 31:</strong> every plan has one main texture, a build route, and three useful labels. If designs become a pile of unrelated textures, have students circle one main texture and cross out extras. <strong>Safe trim:</strong> skip whole-group sharing. Protect the individual career-task check, labeled plan, collection, and reset.</p>",
                "RESOURCES": "<p>Licensed FYF pp. 127-129 are embedded. H&amp;L p. 138 App Exploration is an optional extension, not required evidence.</p>",
                "SUPPORT": "<p>Use the embedded FYF style guide as the visual bank, narrow the choice to two texture families, and allow oral rehearsal. FYF p. 129 provides the main sketch area; the alternate brief uses its third page for the full-size map when the workbook is unavailable.</p>",
                "FALLBACK": "<p>No platform is required. An absent student uses the embedded pages and the no-workbook brief only when the workbook is unavailable.</p>",
            },
            2: {
                "TITLE": "Build and Test the SFX Texture Model",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>Dry or digital is the turnkey core.</strong> Adhesive work is optional only after the full campus safety gate.",
                "PREP": f'<ul><li>Print one {file_link(files["BUILD_RECORD"]["id"], "one-page SFX Build and Test Record")} per student and provide one cardstock board per dry-route student.</li><li>Per student: at least three teacher-approved dry layer pieces. Per pair: one scissors and one tape roll. Per table of four: one supply tray and one return bin. Per digital-route student: one device.</li><li>Assign one materials manager and one cleanup checker per table. Test the optional digital route before class.</li><li>Do not require food, seeds, pasta, salt, latex, or eyelash glue.</li></ul>',
                "MODEL": "<p><strong>Build/test record example:</strong> “The torn-paper cracks stayed readable from three feet away. One top strip flattened and hid the center line. I trimmed the strip and moved it outward. An SFX artist records that change so the next build repeats what worked and avoids the same failure.”</p>",
                "EVIDENCE": "<p>Approved-surface model, three overlapping layers, one-page test record, one revision, and the career documentation connection. Formative.</p>",
                "FLOW": flow(
                    "#5a2d91", "Warm-up · 5", "Name the three essential layers."
                )
                + flow(
                    "#4a9d2f",
                    "Safety and demo · 8",
                    "Surface, order, overlap, test, cleanup.",
                )
                + flow("#1f617a", "Build · 22", "Structure first, then detail.")
                + flow(
                    "#e3ad19",
                    "Test, revise, and clean · 10",
                    "View from three feet, record evidence, return tools and loose materials.",
                )
                + flow("#1f617a", "Exit · 5", "Fix the missing main texture."),
                "MONITOR": "<p><strong>District response move:</strong> students point to the three essential layers before building. <strong>Lap 1, minute 18:</strong> the main structure is visible and the approved surface is clear. If several students begin with small decoration, pause and rebuild one large-to-small sequence. <strong>Lap 2, minute 31:</strong> three layers overlap and students have begun the test record. If a model fails, keep it as evidence and move directly to cause and revision. <strong>Minute 45 target:</strong> tools and loose materials are in the return bin and the record is collected. <strong>Safe trim:</strong> remove extra detail. Protect one test, one revision, the career connection, and cleanup.</p>",
                "RESOURCES": "<p>Licensed FYF p. 130 is embedded as source context. The Canvas directions set the classroom safety route.</p>",
                "SUPPORT": "<p>Use pre-cut dry materials, two route cards, speech-to-text, and a digital mockup. All writing jobs have separate lines.</p>",
                "FALLBACK": "<p>No material on a person. Paper relief and digital layers are full absence routes. Optional adhesive work requires product label, SDS, allergy, ventilation, approved surface, supervision, storage, and cleanup checks.</p>",
            },
            3: {
                "TITLE": "Quality Check and Texas Cosmetology Pathways",
                "SUBTITLE": "50 minutes · TEKS d(2)(A), d(3)(G)",
                "ALERT": "<strong>Use the current in-state beginner route.</strong> The TDLR Apply page requires a 1,000-hour course at a licensed school; do not substitute an informal salon apprenticeship for this scenario. Out-of-state, equivalence, and other special application cases are outside this lesson.",
                "PREP": f'<ul><li>Print one double-sided {file_link(files["PATHWAY"]["id"], "two-page pathway decision")} per student. Students use FYF p. 131 for the quality check.</li><li>Post {file_link(files["EVIDENCE"]["id"], "the dated evidence guide")} digitally; print one copy per pair only when devices are unavailable.</li><li>Keep {file_link(files["QUALITY"]["id"], "the enlarged no-workbook quality sheet")} as an alternate route only; print one per student without the workbook, not a class set.</li><li>The practice Quiz is optional after the core pathway decision or during recovery; it is not part of the default 50 minutes.</li></ul>',
                "MODEL": "<p><strong>Pathway model:</strong> “I recommend the Irving ISD high-school setting because the current district page confirms a Cosmetology program, and the state still requires the 1,000-hour licensed-school route. Before enrolling, Alex needs to ask the counselor which campus, schedule, transportation, and hours apply.” Point out the verified fact, the recommendation, and the unanswered local question.</p>",
                "EVIDENCE": "<p>FYF p. 131 quality check, complete two-setting comparison, one verified fact, one unanswered local question, and ordered license steps. Formative.</p>",
                "FLOW": flow(
                    "#5a2d91", "Warm-up · 5", "What held and what needs rebuilding?"
                )
                + flow(
                    "#4a9d2f",
                    "Quality and revision · 10",
                    "Three criteria and labeled redesign.",
                )
                + flow(
                    "#1f617a",
                    "Read evidence · 13",
                    "Mark the current Texas and district facts.",
                )
                + flow(
                    "#e3ad19",
                    "Pathway decision · 15",
                    "Compare settings; do not invent unknowns.",
                )
                + flow("#1f617a", "Exit and collect · 7", "Shared requirement, local question, packet check."),
                "MONITOR": "<p><strong>District response move:</strong> students box one fixed state requirement and circle one local unknown before discussion. <strong>Lap 1, minute 17:</strong> FYF p. 131 has a visible success, problem cause, and improvement plan. <strong>Lap 2, minute 31:</strong> both route columns separate verified facts from questions. If students invent cost, completion time, or transportation, label the cell <em>unknown—ask</em> and use the supplied model. <strong>Key:</strong> 1,000-hour course at a licensed school; written exam eligibility after 900 reported hours; practical after 1,000 hours and the written exam; age 17; $50 application; two-year license. Current district page lists Cardwell, Irving, MacArthur, and Nimitz. <strong>Safe trim:</strong> omit the optional Quiz or extended route discussion. Protect the two-setting comparison, ordered license steps, exit, and collection.</p>",
                "RESOURCES": '<p><a href="https://www.tdlr.texas.gov/barbering-and-cosmetology/individuals/apply-cosmetologist.htm">Current TDLR operator requirements</a> · <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte">Current Irving ISD High School CTE</a> · <a href="https://www.bls.gov/ooh/personal-care-and-service/barbers-hairstylists-and-cosmetologists.htm">BLS occupation profile</a></p>',
                "SUPPORT": "<p>Read one section at a time, pre-highlight labels, and allow oral rehearsal. The recommendation gets six full-width lines and the enrollment questions have separate fields.</p>",
                "FALLBACK": "<p>The fixed evidence guide is load-bearing; live navigation is optional. Treat workbook salon details as context until locally confirmed.</p>",
            },
            4: {
                "TITLE": "Salon Entrepreneurship and Wellness Communication",
                "SUBTITLE": "50 minutes · TEKS d(3)(I)",
                "ALERT": "<strong>Students build the three-post series in FYF p. 133.</strong> The companion collects the business, safety, revision, and trust evidence the workbook does not ask for.",
                "PREP": f'<ul><li>Print one double-sided {file_link(files["CAMPAIGN"]["id"], "two-page Salon and Wellness Campaign Companion")} per student. Students use FYF pp. 132-133 for the post series.</li><li>Project the licensed workbook pages and the supplied safe/unsafe model below; no teacher-created sample is required.</li><li>Paper is the default. Provide one device per student only for the optional Canva or Adobe Express route. Students work individually; a partner, teacher, or private self-check is equal.</li></ul>',
                "MODEL": "<p><strong>Safe fictional model:</strong> “Pause Studio: Try a short breathing break. Breathe in slowly, then breathe out slowly. This may help you pause and refocus. If stress feels hard to manage, talk with a trusted adult or professional.” <strong>Unsafe non-example:</strong> “Our method cures anxiety in 30 seconds.” Ask students to identify the guarantee and medical claim, then rewrite it as general wellness information.</p>",
                "EVIDENCE": "<p>Business concept, customer-experience map, FYF p. 133 three-post series, safety check, one revision, and the entrepreneurship connection. Formative.</p>",
                "FLOW": flow(
                    "#5a2d91", "Warm-up · 5", "Service plus owner responsibility."
                )
                + flow(
                    "#4a9d2f",
                    "Define the business · 10",
                    "Customer, difference, skill, service map.",
                )
                + flow(
                    "#1f617a",
                    "Read the toolkit · 6",
                    "Choose three different techniques.",
                )
                + flow(
                    "#e3ad19",
                    "Create, check, and revise · 22",
                    "One polished post, two rough plans, revision.",
                )
                + flow("#1f617a", "Exit, collect, and reset · 7", "Trust without medical advice."),
                "MONITOR": "<p><strong>District response move:</strong> students classify the supplied pair as safe or unsafe, then defend the choice with one phrase from the post. <strong>Lap 1, minute 13:</strong> the business concept names a service, fictional customer, meaningful difference, and owner responsibility. If students describe only a logo or color, ask what the owner must do for the customer. <strong>Lap 2, minute 31:</strong> one polished post and two rough plans use three different workbook techniques. If several posts promise a cure or guaranteed result, pause for the supplied rewrite. Reject real handles, names, locations, contact details, diagnoses, and treatment language. <strong>Safe trim:</strong> replace partner review with the private self-check. Protect one polished post, two rough plans, safety revision, entrepreneurship connection, and collection.</p>",
                "RESOURCES": "<p>Licensed FYF pp. 132-133 are embedded. Canva and Adobe Express are optional approved production tools.</p>",
                "SUPPORT": "<p><strong>Fictional customer choices:</strong> a student preparing for a performance, or an adult client with a busy workday. <strong>Headline choices:</strong> Pause and Breathe, One-Minute Reset, or Make Space to Refocus. The supplied strong/unsafe model pair supports the safety check. FYF p. 133 provides three large post frames; the companion gives each missing evidence job its own field.</p>",
                "FALLBACK": "<p>No public account or post. Students do not disclose personal wellness information. Paper is equal.</p>",
            },
            5: {
                "TITLE": "Cosmetology Career and Business Recommendation",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(2)(A), d(3)(G), d(3)(I)",
                "ALERT": "<strong>This is the mapped Minor 3.</strong> Canvas records 100 points in Minor Assessments (40%); the 16-point rubric is the student-visible evidence profile. Keep both unpublished in the master course.",
                "PREP": f'<ul><li>Print one double-sided {file_link(files["RECOMMENDATION"]["id"], "recommendation")} per paper-route student. Post {file_link(files["RUBRIC"]["id"], "the rubric")} and {file_link(files["EVIDENCE"]["id"], "the evidence guide")} digitally; print one set per student only for a no-device route.</li><li>Open the private unpublished Assignment and provide one device per Canvas-route student. Each student submits one recommendation; no partner artifact or platform screenshot is required.</li></ul>',
                "MODEL": "<p><strong>Seven-sentence model:</strong> “I recommend Hair Stylist because Jordan wants creative, client-facing work. A hair stylist consults with clients and cuts or styles hair. In Texas, the operator route requires 1,000 hours at a licensed school and written and practical exams. Jordan's next verified step is to ask the Irving ISD counselor which campus and schedule apply. A related business opportunity is a salon, but the owner must manage sanitation, records, and client communication. One trade-off is that salon schedules may include evenings or weekends. The SFX texture map shows the same planning skill because the artist turns a client or production goal into a labeled design.”</p>",
                "EVIDENCE": "<p>Individual 6-8 sentence recommendation plus one design-to-career connection and rubric revision.</p>",
                "FLOW": flow(
                    "#5a2d91", "Warm-up · 5", "Rank Jordan's decision factors."
                )
                + flow(
                    "#4a9d2f",
                    "Audit · 8",
                    "Task, Texas fact, next step, opportunity, trade-off.",
                )
                + flow("#1f617a", "Plan · 8", "Five separate evidence jobs.")
                + flow(
                    "#e3ad19",
                    "Write and connect · 22",
                    "Recommendation plus transferable skill.",
                )
                + flow(
                    "#1f617a", "Self-score and submit · 7", "Revise one weak criterion."
                ),
                "MONITOR": "<p><strong>District response move:</strong> students point to the five numbered evidence jobs before drafting. <strong>Lap 1, minute 17:</strong> all five planning fields contain labeled evidence, not unsupported opinions. If several students omit the Texas fact or next step, return to the evidence guide and model one sentence without giving a recommendation choice. <strong>Lap 2, minute 34:</strong> the draft includes career task, Texas fact, next step, opportunity/responsibility, and trade-off; the design connection remains separate. Any Human Services career may earn full credit. Evidence-profile bands: 15-16 Masters, 13-14 Meets, 12 Approaches, 10-11 Needs Improvement; 0-9 follows campus policy. Convert the 16-point profile to the 100-point Canvas score. <strong>Safe trim:</strong> skip warm-up sharing. Protect the rubric self-check, revision, private submission, and reset.</p>",
                "RESOURCES": "<p>The current district context is embedded. Xello Career Factors, eDynamic 4.2, and H&amp;L favorites are supplemental extensions only.</p>",
                "SUPPORT": "<p>Use numbered planning fields, oral rehearsal, speech-to-text, or approved audio. Ten full-width lines support the 6-8 sentence response.</p>",
                "FALLBACK": "<p>The fixed guide, prompt, and rubric are the complete independent route. No screenshot, favorite count, public post, or partner is required.</p>",
            },
        }

        day_names = {
            1: "Human Services and SFX Concept",
            2: "Build and Test the Texture Model",
            3: "Quality and Texas Pathways",
            4: "Salon and Wellness Campaign",
            5: "Career and Business Recommendation",
        }
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_item(
                client, module["id"], "SubHeader", None, header_title
            )
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 3SW Wk5 Day {day} - {day_names[day]}"
            student_page = await upsert_page(
                client,
                student_title,
                render(
                    "3sw-wk5-student.html",
                    {
                        "COURSE_ID": COURSE_ID,
                        "DAY": day,
                        **contracts[day],
                        **student[day],
                    },
                ),
            )
            teacher_title = f"TEACHER: 3SW Wk5 Day {day} Facilitator Guide"
            teacher_page = await upsert_page(
                client,
                teacher_title,
                render(
                    "3sw-wk5-teacher.html",
                    {
                        "COURSE_ID": COURSE_ID,
                        "DAY": day,
                        "STUDENT_PAGE_URL": student_page["url"],
                        **contracts[day],
                        **teacher[day],
                    },
                ),
            )
            await upsert_item(
                client, module["id"], "Page", teacher_page["url"], teacher_title
            )
            await upsert_item(
                client, module["id"], "Page", student_page["url"], student_title
            )
            pages[day] = {"teacher": teacher_page, "student": student_page}
            order += [
                ("Page", teacher_page["url"], teacher_title),
                ("Page", student_page["url"], student_title),
            ]
            if day == 3:
                await upsert_item(client, module["id"], "Quiz", quiz["id"], QUIZ_TITLE)
                order.append(("Quiz", quiz["id"], QUIZ_TITLE))
            if day == 5:
                await upsert_item(
                    client,
                    module["id"],
                    "Assignment",
                    recommendation["id"],
                    RECOMMENDATION_TITLE,
                )
                order.append(("Assignment", recommendation["id"], RECOMMENDATION_TITLE))

        items = await paged(
            client, f"/courses/{COURSE_ID}/modules/{module['id']}/items"
        )

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
            item = next(
                (
                    entry
                    for entry in items
                    if entry["id"] not in keep_ids
                    and matches_item(entry, kind, key)
                ),
                None,
            )
            if item is None:
                raise RuntimeError(f"Missing expected module item: {kind} {key}")
            keep_ids.add(item["id"])
        for entry in items:
            if entry["id"] not in keep_ids:
                await api(
                    client,
                    "DELETE",
                    f"/courses/{COURSE_ID}/modules/{module['id']}/items/{entry['id']}",
                )

        items = await paged(
            client, f"/courses/{COURSE_ID}/modules/{module['id']}/items"
        )
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(entry for entry in items if matches_item(entry, kind, key))
            await api(
                client,
                "PUT",
                f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}",
                data={"module_item[position]": position, "module_item[title]": title},
            )

        final_items = sorted(
            await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items"),
            key=lambda entry: entry.get("position") or 0,
        )
        module = await api(
            client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}"
        )
        quiz = await api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
        recommendation = await api(
            client,
            "GET",
            f"/courses/{COURSE_ID}/assignments/{recommendation['id']}",
        )
        final_questions = await paged(
            client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        )
        if module.get("published"):
            raise RuntimeError("3SW Wk5 module unexpectedly published")
        if (
            quiz.get("published")
            or quiz.get("quiz_type") != "practice_quiz"
            or int(quiz.get("allowed_attempts") or 0) != -1
        ):
            raise RuntimeError(
                f"3SW Wk5 practice Quiz invariant failed: published={quiz.get('published')}, "
                f"type={quiz.get('quiz_type')}, attempts={quiz.get('allowed_attempts')}"
            )
        if [entry.get("question_name") for entry in final_questions] != [
            spec[0] for spec in QUESTIONS
        ]:
            raise RuntimeError("3SW Wk5 practice Quiz question order changed")
        if (
            recommendation.get("published")
            or float(recommendation.get("points_possible") or 0) != 100
            or recommendation.get("assignment_group_id") != minor_group["id"]
            or recommendation.get("grading_type") != "points"
            or recommendation.get("omit_from_final_grade") is not False
        ):
            raise RuntimeError(
                f"3SW Wk5 Minor invariant failed at final gate: "
                f"published={recommendation.get('published')}, "
                f"points={recommendation.get('points_possible')}, "
                f"group={recommendation.get('assignment_group_id')}, "
                f"grading={recommendation.get('grading_type')}, "
                f"omit={recommendation.get('omit_from_final_grade')}"
            )
        published_pages = [
            value["url"]
            for pair in pages.values()
            for value in pair.values()
            if value.get("published")
        ]
        if published_pages:
            raise RuntimeError(f"Published 3SW Wk5 pages remain: {published_pages}")
        published_items = [
            entry.get("title") for entry in final_items if entry.get("published")
        ]
        if published_items:
            raise RuntimeError(f"Published 3SW Wk5 module items remain: {published_items}")
        if len(final_items) != len(order) or len(final_items) != 17:
            raise RuntimeError(
                f"Expected 17 3SW Wk5 module items; found {len(final_items)}"
            )
        for position, ((kind, key, title), item) in enumerate(
            zip(order, final_items), start=1
        ):
            if (
                item.get("position") != position
                or item.get("title") != title
                or not matches_item(item, kind, key)
            ):
                raise RuntimeError(
                    f"3SW Wk5 module order mismatch at position {position}"
                )
        print(
            json.dumps(
                {
                    "module": {"id": module["id"], "published": module["published"]},
                    "quiz": {
                        "id": quiz["id"],
                        "published": quiz.get("published"),
                        "quiz_type": quiz.get("quiz_type"),
                        "allowed_attempts": quiz.get("allowed_attempts"),
                        "questions": len(final_questions),
                    },
                    "recommendation": {
                        "id": recommendation["id"],
                        "published": recommendation.get("published"),
                        "points_possible": recommendation.get("points_possible"),
                        "assignment_group_id": recommendation.get(
                            "assignment_group_id"
                        ),
                        "grading_type": recommendation.get("grading_type"),
                        "omit_from_final_grade": recommendation.get(
                            "omit_from_final_grade"
                        ),
                        "submission_types": recommendation.get("submission_types"),
                    },
                    "support_folder": {
                        "id": support_folder["id"],
                        "locked": support_folder["locked"],
                    },
                    "folders": {
                        str(day): {"id": folder["id"], "locked": folder["locked"]}
                        for day, folder in folders.items()
                    },
                    "files": {key: value["id"] for key, value in files.items()},
                    "pages": {
                        str(day): {
                            kind: {"url": value["url"], "published": value["published"]}
                            for kind, value in pair.items()
                        }
                        for day, pair in pages.items()
                    },
                    "items": [
                        {
                            "id": item["id"],
                            "position": item["position"],
                            "title": item["title"],
                            "type": item["type"],
                            "page_url": item.get("page_url"),
                        }
                        for item in final_items
                    ],
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
