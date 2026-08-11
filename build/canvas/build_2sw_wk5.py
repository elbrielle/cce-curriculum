"""Build the unpublished 2SW Week 5 communication module, practice quiz, and discussion."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
from urllib.parse import urlencode
import httpx

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
MODULE_NAME = "2SW Wk5: Communication and Goal Setting"
QUIZ_TITLE = "PRACTICE: Active Listening Evidence Check"
DISCUSSION_TITLE = "PRACTICE: Little Library Message Lab"
MINOR_TITLE = "MINOR 3: Communication and Goal Synthesis"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/2sw/wk5"


def slugify(v):
    return re.sub(r"[^a-z0-9]+", "-", v.lower().replace("&", "and")).strip("-")


async def api(c, m, p, **kw):
    r = await c.request(m, f"{BASE}/api/v1{p}", **kw)
    r.raise_for_status()
    return r.json() if r.content else None


async def paged(c, p, params=None):
    out = []
    url = f"{BASE}/api/v1{p}"
    q = {"per_page": 100, **(params or {})}
    while url:
        r = await c.get(url, params=q)
        r.raise_for_status()
        out += r.json()
        url = r.links.get("next", {}).get("url")
        q = None
    return out


async def ensure_module(c):
    modules = await paged(c, f"/courses/{COURSE_ID}/modules")
    found = next((m for m in modules if m["name"] == MODULE_NAME), None)
    if found:
        return await api(
            c,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{found['id']}",
            data={"module[name]": MODULE_NAME, "module[published]": "false"},
        )
    return await api(
        c,
        "POST",
        f"/courses/{COURSE_ID}/modules",
        data={"module[name]": MODULE_NAME, "module[published]": "false"},
    )


async def ensure_folder(c, path):
    current = ""
    folder = None
    for name in path.split("/")[1:]:
        target = f"{current}/{name}".strip("/")
        enc = httpx.URL("/" + target).raw_path.decode("ascii").lstrip("/")
        r = await c.get(f"{BASE}/api/v1/courses/{COURSE_ID}/folders/by_path/{enc}")
        if r.status_code == 200 and r.json():
            folder = r.json()[-1]
        else:
            folder = await api(
                c,
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
            c, "PUT", f"/folders/{folder['id']}", data={"locked": "true"}
        )
    return folder


async def upload(c, path, folder):
    init = await api(
        c,
        "POST",
        f"/courses/{COURSE_ID}/files",
        data={
            "name": path.name,
            "parent_folder_path": folder,
            "on_duplicate": "overwrite",
        },
    )
    r = await c.post(
        init["upload_url"],
        data=init["upload_params"],
        files={
            "file": (
                path.name,
                path.read_bytes(),
                mimetypes.guess_type(path.name)[0] or "application/octet-stream",
            )
        },
        follow_redirects=True,
    )
    r.raise_for_status()
    record = await api(c, "PUT", f"/files/{r.json()['id']}", data={"locked": "true"})
    if not record.get("locked"):
        raise RuntimeError(f"Canvas did not lock uploaded file {path.name!r}")
    return record


async def lock_folder_files(c, folder):
    current = await api(c, "GET", f"/folders/{folder['id']}")
    if not current.get("locked"):
        current = await api(c, "PUT", f"/folders/{folder['id']}", data={"locked": "true"})
    if not current.get("locked"):
        raise RuntimeError(
            f"Canvas did not lock folder {folder.get('full_name') or folder['id']}"
        )
    for entry in await paged(c, f"/folders/{folder['id']}/files"):
        if not entry.get("locked"):
            await api(c, "PUT", f"/files/{entry['id']}", data={"locked": "true"})
    final = await paged(c, f"/folders/{folder['id']}/files")
    unlocked = [
        entry.get("display_name") or entry.get("filename")
        for entry in final
        if not entry.get("locked")
    ]
    if unlocked:
        raise RuntimeError(f"Unlocked files remain in folder {folder['id']}: {unlocked}")
    return current


def render(name, values):
    text = (TEMPLATES / name).read_text()
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", str(v))
    unresolved = sorted(set(re.findall(r"\{\{[^}]+\}\}", text)))
    if unresolved:
        raise ValueError(f"Unresolved values in {name}: {unresolved}")
    return text


async def upsert_page(c, title, body, url):
    data = {
        "wiki_page[title]": title,
        "wiki_page[body]": body,
        "wiki_page[published]": "false",
        "wiki_page[editing_roles]": "teachers",
    }
    r = await c.get(f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{url}")
    if r.status_code == 200:
        return await api(c, "PUT", f"/courses/{COURSE_ID}/pages/{url}", data=data)
    if r.status_code != 404:
        r.raise_for_status()
    return await api(c, "POST", f"/courses/{COURSE_ID}/pages", data=data)


async def upsert_page_item(c, module_id, page, title):
    items = await paged(c, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    item = next((i for i in items if i.get("page_url") == page["url"]), None)
    if item:
        return await api(
            c,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            data={"module_item[title]": title},
        )
    return await api(
        c,
        "POST",
        f"/courses/{COURSE_ID}/modules/{module_id}/items",
        data={
            "module_item[type]": "Page",
            "module_item[page_url]": page["url"],
            "module_item[title]": title,
        },
    )


async def upsert_subheader(c, module_id, title):
    items = await paged(c, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    item = next(
        (i for i in items if i.get("type") == "SubHeader" and i.get("title") == title),
        None,
    )
    if item:
        return await api(
            c,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            data={"module_item[title]": title, "module_item[indent]": "0"},
        )
    return await api(
        c,
        "POST",
        f"/courses/{COURSE_ID}/modules/{module_id}/items",
        data={
            "module_item[type]": "SubHeader",
            "module_item[title]": title,
            "module_item[indent]": "0",
        },
    )


def file_link(file_id, label):
    return f'<a href="/courses/{COURSE_ID}/files/{file_id}/preview" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">{label}</a>'


def image_tag(file_id, alt, max_width=760):
    return f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" style="display:block;width:100%;max-width:{max_width}px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'


def step(num, title, body, color="#5a2d91"):
    return f'<h3 style="color:{color};border-bottom:3px solid #d9c9ed">{num}. {title}</h3>{body}'


def flow(color, title, text):
    return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'


QUIZ_QUESTIONS = [
    {
        "name": "Q1 - Essential detail",
        "text": "Which detail from Maria's fictional account is essential to record?",
        "correct": "The chest tightness started about three hours ago and has not gone away.",
        "wrong": [
            "She had paperwork after lunch.",
            "She usually carries coffee.",
            "She had a busy week.",
        ],
        "correct_comment": "Correct. Onset and persistence are key reported details.",
        "incorrect_comment": "Choose a detail that directly describes the reported concern, timing, or risk context.",
    },
    {
        "name": "Q2 - New question",
        "text": "Which question asks for information Maria did not already give?",
        "correct": "Have you noticed nausea, sweating, or dizziness?",
        "wrong": [
            "Did the pain start today?",
            "Has the pain gone away?",
            "Did it spread into your shoulder?",
        ],
        "correct_comment": "Correct. The account did not answer that question.",
        "incorrect_comment": "A clarifying question closes a gap instead of repeating a known detail.",
    },
    {
        "name": "Q3 - Role boundary",
        "text": "A classmate reports real chest pain and shortness of breath. What should you do?",
        "correct": "Get an adult and emergency help immediately.",
        "wrong": [
            "Practice the classroom questions first.",
            "Decide whether it is serious.",
            "Wait until the end of class.",
        ],
        "correct_comment": "Correct. Real symptoms are not a classroom practice case.",
        "incorrect_comment": "Do not diagnose or delay. Get immediate adult or emergency help.",
    },
    {
        "name": "Q4 - Paraphrase",
        "text": "Which response best shows active listening in the equipment scenario?",
        "correct": "I heard that the cart wheel sticks only when the cart is full. What load was on it when that happened?",
        "wrong": [
            "The cart is definitely broken.",
            "Just submit the request again.",
            "That happened to me once.",
        ],
        "correct_comment": "Correct. It paraphrases and asks a new question.",
        "incorrect_comment": "Look for both a faithful paraphrase and a question that closes a gap.",
    },
    {
        "name": "Q5 - Transfer",
        "text": "Which example shows active listening transferring to another career?",
        "correct": "A mechanic repeats the driver's concern and asks when the sound occurs.",
        "wrong": [
            "A designer chooses a favorite color.",
            "A chef memorizes a recipe alone.",
            "A student guesses what a customer meant.",
        ],
        "correct_comment": "Correct. The listener paraphrases and asks for useful detail.",
        "incorrect_comment": "Transfer evidence names the career and the same listening action.",
    },
]


async def prepare_quiz_questions(c, quiz_id, desired_names):
    existing = await paged(c, f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions")
    keep, seen = [], set()
    for question in existing:
        name = question.get("question_name")
        if name not in desired_names or name in seen:
            await api(
                c,
                "DELETE",
                f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions/{question['id']}",
            )
        else:
            seen.add(name)
            keep.append(question)
    return keep


async def finalize_quiz_order(c, quiz_id, expected_names):
    final = await paged(c, f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions")
    by_name = {entry.get("question_name"): entry for entry in final}
    if set(by_name) != set(expected_names) or len(final) != len(expected_names):
        raise RuntimeError(
            f"Quiz {quiz_id} question mismatch: "
            f"{[entry.get('question_name') for entry in final]}"
        )
    fields = []
    for name in expected_names:
        fields.extend(
            [("order[][id]", str(by_name[name]["id"])), ("order[][type]", "question")]
        )
    await api(
        c,
        "POST",
        f"/courses/{COURSE_ID}/quizzes/{quiz_id}/reorder",
        content=urlencode(fields),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    ordered = await paged(c, f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions")
    actual = [entry.get("question_name") for entry in ordered]
    if actual != expected_names:
        raise RuntimeError(
            f"Quiz {quiz_id} order mismatch: expected {expected_names}, found {actual}"
        )


async def upsert_quiz(c):
    quizzes = await paged(c, f"/courses/{COURSE_ID}/quizzes")
    quiz = next((q for q in quizzes if q.get("title") == QUIZ_TITLE), None)
    data = {
        "quiz[title]": QUIZ_TITLE,
        "quiz[description]": "<p>Ungraded active-listening practice. Retry and use the feedback.</p>",
        "quiz[quiz_type]": "practice_quiz",
        "quiz[published]": "false",
        "quiz[allowed_attempts]": "-1",
        "quiz[show_correct_answers]": "true",
        "quiz[shuffle_answers]": "false",
    }
    quiz = await api(
        c,
        "PUT" if quiz else "POST",
        f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        if quiz
        else f"/courses/{COURSE_ID}/quizzes",
        data=data,
    )
    expected = [spec["name"] for spec in QUIZ_QUESTIONS]
    existing = await prepare_quiz_questions(c, quiz["id"], set(expected))
    for position, spec in enumerate(QUIZ_QUESTIONS, start=1):
        found = next(
            (q for q in existing if q.get("question_name") == spec["name"]), None
        )
        answers = [{"answer_text": spec["correct"], "answer_weight": 100}] + [
            {"answer_text": v, "answer_weight": 0} for v in spec["wrong"]
        ]
        payload = {
            "question": {
                "question_name": spec["name"],
                "question_text": spec["text"],
                "question_type": "multiple_choice_question",
                "position": position,
                "points_possible": 1,
                "correct_comments": spec["correct_comment"],
                "incorrect_comments": spec["incorrect_comment"],
                "answers": answers,
            }
        }
        await api(
            c,
            "PUT" if found else "POST",
            f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{found['id']}"
            if found
            else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions",
            json=payload,
        )
    await finalize_quiz_order(c, quiz["id"], expected)
    return await api(c, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


async def upsert_quiz_item(c, module_id, quiz):
    items = await paged(c, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    item = next(
        (
            i
            for i in items
            if i.get("type") == "Quiz" and i.get("content_id") == quiz["id"]
        ),
        None,
    )
    if item:
        return await api(
            c,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            data={"module_item[title]": QUIZ_TITLE},
        )
    return await api(
        c,
        "POST",
        f"/courses/{COURSE_ID}/modules/{module_id}/items",
        data={
            "module_item[type]": "Quiz",
            "module_item[content_id]": quiz["id"],
            "module_item[title]": QUIZ_TITLE,
        },
    )


async def upsert_discussion(c):
    topics = await paged(c, f"/courses/{COURSE_ID}/discussion_topics")
    found = next((d for d in topics if d.get("title") == DISCUSSION_TITLE), None)
    message = """<p><strong>This is a fictional message lab.</strong> Do not use a real account, address, photo, handle, phone number, or personal name.</p><ol><li>Post a 2-4 sentence Little Library update with a clear status, one reader action, and two useful hashtags.</li><li>Choose one supplied workplace message and rewrite it using only the facts shown:<ul><li><strong>Supply:</strong> Room 204 has 12 pairs of medium gloves and no large gloves; delivery is Friday; notify the supply lead today.</li><li><strong>Schedule:</strong> fictional orientation moved from Tuesday at 3:30 p.m. to Thursday at 3:30 p.m.; location remains Training Room B; questions use the official program portal.</li><li><strong>Repair:</strong> cart C-14's front-left wheel sticks above 20 pounds; remove it from use and notify Facilities.</li></ul></li><li>Reply to one classmate's fictional post with Notice + Question + Next Step.</li></ol><p>A private written response to the same prompts is an equal route.</p>"""
    data = {
        "title": DISCUSSION_TITLE,
        "message": message,
        "discussion_type": "threaded",
        "published": "false",
        "require_initial_post": "true",
    }
    if found:
        discussion = await api(
            c, "PUT", f"/courses/{COURSE_ID}/discussion_topics/{found['id']}", data=data
        )
    else:
        discussion = await api(
            c, "POST", f"/courses/{COURSE_ID}/discussion_topics", data=data
        )
    if discussion.get("published") or discussion.get("assignment_id"):
        raise RuntimeError(
            "Practice discussion invariant failed after update: "
            f"published={discussion.get('published')}, "
            f"assignment_id={discussion.get('assignment_id')}"
        )
    return discussion


async def upsert_discussion_item(c, module_id, discussion):
    items = await paged(c, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    item = next(
        (
            i
            for i in items
            if i.get("type") == "Discussion" and i.get("content_id") == discussion["id"]
        ),
        None,
    )
    if item:
        return await api(
            c,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            data={"module_item[title]": DISCUSSION_TITLE},
        )
    return await api(
        c,
        "POST",
        f"/courses/{COURSE_ID}/modules/{module_id}/items",
        data={
            "module_item[type]": "Discussion",
            "module_item[content_id]": discussion["id"],
            "module_item[title]": DISCUSSION_TITLE,
        },
    )


async def upsert_assignment_item(c, module_id, assignment):
    items = await paged(c, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    item = next(
        (
            i
            for i in items
            if i.get("type") == "Assignment" and i.get("content_id") == assignment["id"]
        ),
        None,
    )
    if item:
        return await api(
            c,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            data={"module_item[title]": MINOR_TITLE},
        )
    return await api(
        c,
        "POST",
        f"/courses/{COURSE_ID}/modules/{module_id}/items",
        data={
            "module_item[type]": "Assignment",
            "module_item[content_id]": assignment["id"],
            "module_item[title]": MINOR_TITLE,
        },
    )


async def require_minor_preflight(c):
    assignments = await paged(c, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == MINOR_TITLE]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one existing mapped Minor assignment named {MINOR_TITLE!r}; found {len(matches)}"
        )
    found = matches[0]
    if float(found.get("points_possible") or 0) != 100:
        raise RuntimeError(
            f"Refusing to modify {MINOR_TITLE!r}: expected 100 points, found {found.get('points_possible')}"
        )
    groups = await paged(c, f"/courses/{COURSE_ID}/assignment_groups")
    group = next(
        (entry for entry in groups if entry.get("id") == found.get("assignment_group_id")),
        None,
    )
    if not group or group.get("name") != "Minor Assessments (40%)":
        raise RuntimeError(
            f"Refusing to modify {MINOR_TITLE!r}: expected Minor Assessments (40%) group"
        )
    return found


async def update_minor_assignment(c, assignment, description, attachment_id):
    existing_description = assignment.get("description") or ""
    note = re.search(
        r'<div data-cce-rubric-note="cce-advisory-rubric-v1".*?</div>',
        existing_description,
        flags=re.DOTALL,
    )
    if note and "cce-advisory-rubric-v1" not in description:
        description = description.rstrip() + note.group(0)
    updated = await api(
        c,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{assignment['id']}",
        data={
            "assignment[name]": MINOR_TITLE,
            "assignment[description]": description,
            "assignment[published]": "false",
            "assignment[points_possible]": "100",
            "assignment[grading_type]": "points",
            "assignment[submission_types][]": [
                "student_annotation",
                "online_upload",
                "online_text_entry",
                "media_recording",
            ],
            "assignment[annotatable_attachment_id]": str(attachment_id),
        },
    )
    if updated.get("published") or float(updated.get("points_possible") or 0) != 100:
        raise RuntimeError(
            "Mapped Minor invariant failed after update: "
            f"published={updated.get('published')}, "
            f"points={updated.get('points_possible')}"
        )
    return updated


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as c:
        minor = await require_minor_preflight(c)
        module = await ensure_module(c)
        quiz = await upsert_quiz(c)
        discussion = await upsert_discussion(c)
        names = {
            "GUIDE": "2sw-wk5-powerskills-transfer-guide.pdf",
            "CONFLICT": "2sw-wk5-conflict-resolution-plan.pdf",
            "LISTEN": "2sw-wk5-active-listening-lab.pdf",
            "SMART": "2sw-wk5-advocacy-smart-time-plan.pdf",
            "WRITE": "2sw-wk5-written-message-lab.pdf",
            "SYNTH": "2sw-wk5-work-experience-skills-synthesis.pdf",
            "RUBRIC": "2sw-wk5-communication-goal-rubric.pdf",
        }
        support = "course files/CCR Materials/2SW/Wk5"
        core = await ensure_folder(c, support)
        files = {
            k: await upload(c, ROOT / "docs/resources/worksheets" / v, support)
            for k, v in names.items()
        }
        files["XELLO"] = await upload(
            c,
            ROOT
            / "cce-curriculum/resources/xello-licensed/prerequisites/experiences.pdf",
            support,
        )
        uploads = {}
        folders = {}
        for day in range(1, 6):
            fp = f"course files/CCR Materials/2SW/Wk5/Day {day} Visuals"
            folders[day] = await ensure_folder(c, fp)
            uploads[day] = {}
            source = ASSETS / f"day{day}"
            if source.exists():
                for path in sorted(source.glob("*.png")):
                    uploads[day][path.name] = await upload(c, path, fp)
        core = await lock_folder_files(c, core)
        for day, folder in folders.items():
            folders[day] = await lock_folder_files(c, folder)
        minor = await update_minor_assignment(
            c,
            minor,
            f"""<div style="max-width:860px;margin:0 auto;font-family:Arial,Helvetica,sans-serif;line-height:1.5;color:#24323d">
  <h2 style="color:#5a2d91">Communication and Goal Synthesis</h2>
  <div style="border:1px solid #bad4df;border-radius:9px;background:#f2f8fb;padding:14px 18px">
    <p><strong>Topic:</strong> Goals and Transferable Skills</p>
    <p><strong>Objective:</strong> Use a time-management plan and evidence from two careers to explain how one communication skill transfers.</p>
    <p><strong>Show your learning:</strong> Submit the four-part communication and goal synthesis.</p>
  </div>
  <h3>Use these sources</h3>
  <ul>
    <li>Your Day 3 SMART goal and time plan</li>
    <li>Your Xello Work experience and CareerOneStop Skills Matcher notes from Day 5</li>
    <li>{file_link(files["RUBRIC"]["id"], "16-point scoring rubric")}</li>
    <li>{file_link(files["SYNTH"]["id"], "optional two-page paper route")} only when your teacher assigns paper</li>
  </ul>
  <h3>Complete four parts</h3>
  <ol>
    <li>Revise the SMART goal so it has an action, measure, reason, and deadline.</li>
    <li>Name one work block, one likely obstacle, and an if-then backup.</li>
    <li>Name one transferable communication skill, cite two Week 5 activities that show it, and explain what the skill looks like in two careers.</li>
    <li>Use one result pattern or authentic experience to explain the next action you will take.</li>
  </ol>
  <p><strong>Submit:</strong> Type the four parts here, upload a document, or record a brief media response. Upload the paper route only when your teacher assigned it.</p>
</div>""",
            files["SYNTH"]["id"],
        )
        quiz_url = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        discussion_url = f"/courses/{COURSE_ID}/discussion_topics/{discussion['id']}"
        minor_url = f"/courses/{COURSE_ID}/assignments/{minor['id']}"
        student = {
            1: {
                "TITLE": "Resolve Conflict and Keep the Work Moving",
                "PURPOSE": "Use three moves to build a fair plan, then show the skill in two careers.",
                "TOPIC": "Transferable Skills",
                "I_CAN": "I can use listening, fair compromise, and respectful language to solve a team conflict and show how the skill transfers.",
                "SHOW_LEARNING": "Complete the FYF conflict plan and an individual two-career transfer check.",
                "TODAY": "<ul><li>read a fictional team conflict;</li><li>write three specific solutions;</li><li>transfer the skill to two careers.</li></ul>",
                "READY": f"<p>Open your workbook to FYF pp. 144-145. Use {file_link(files['CONFLICT']['id'], 'the optional no-workbook route')} only when your teacher assigns it. Keep {file_link(files['GUIDE']['id'], 'the Powerskills Transfer Guide')} available for examples.</p>",
                "STEPS": step(
                    1,
                    "Learn the three moves",
                    image_tag(
                        uploads[1]["fyf-powerskills-chart.png"]["id"],
                        "Find Your Future Powerskills chart with ten transferable skills",
                        700,
                    )
                    + "<p>Listen. Compromise fairly. Stay respectful.</p>",
                )
                + step(
                    2,
                    "Read the smoothie conflicts",
                    image_tag(
                        uploads[1]["fyf-conflict-scenario.png"]["id"],
                        "Find Your Future fictional smoothie-company conflict scenario",
                        700,
                    ),
                )
                + step(
                    3,
                    "Complete all three plan rows",
                    image_tag(
                        uploads[1]["fyf-conflict-plan.png"]["id"],
                        "Find Your Future conflict-resolution table and optional advertisement directions",
                        700,
                    )
                    + "<p>Name what each person needs, one specific solution, and how the team will know it is fair.</p><p><strong>Use when helpful:</strong> “Each person needs ____. We can ____ so that ____. If that does not work, we will ____.”</p>",
                )
                + step(
                    4,
                    "Transfer the skill",
                    "<p>Give your teacher a brief written, oral, AAC, or conference response. Name two careers, a conflict each could face, and the first safe move.</p><p><strong>Complete frame:</strong> “In ____, the conflict could be ____. The first safe move is ____ because ____.”</p>",
                ),
                "DONE": "<ul><li>three complete conflict rows;</li><li>specific actions instead of “talk it out”;</li><li>two-career transfer response;</li><li>no safety rule compromised.</li></ul>",
                "SUPPORT": "<p>conflict = conflicto · listen = escuchar · compromise = compromiso · respectful = respetuoso. Complete frames are beside Steps 3 and 4.</p>",
                "FALLBACK": "<p>Complete the plan independently from the embedded pages. The poster is optional and artistic quality is not graded.</p>",
            },
            2: {
                "TITLE": "Listen for the Detail That Matters",
                "PURPOSE": "Sort key details, ask a new question, and stay inside the listener role.",
                "TOPIC": "Transferable Skills",
                "I_CAN": "I can separate essential details from background details, ask a new question, and transfer active listening to another career.",
                "SHOW_LEARNING": "Complete FYF p. 63 and the Canvas Active Listening Evidence Check.",
                "TODAY": "<ul><li>read a fictional account twice;</li><li>sort four details;</li><li>practice paraphrasing and a new question.</li></ul>",
                "READY": f"<p>Open your workbook to FYF pp. 62-63. Use {file_link(files['LISTEN']['id'], 'the optional Active Listening Lab')} only when your teacher assigns the no-workbook or extended-practice route.</p>",
                "STEPS": step(
                    1,
                    "Read without diagnosing",
                    image_tag(
                        uploads[2]["fyf-maria-account.png"]["id"],
                        "Find Your Future fictional Maria account for active-listening practice; students do not diagnose",
                        700,
                    )
                    + "<p>First read: pencils down. Second read: mark details.</p>",
                )
                + step(
                    2,
                    "Sort and explain",
                    image_tag(
                        uploads[2]["fyf-listening-response.png"]["id"],
                        "Find Your Future essential/background detail table and clarifying-question prompts",
                        700,
                    )
                    + "<p>Record two essential and two background details with reasons.</p><p><strong>Complete frame:</strong> “The detail ____ is essential/background because ____.”</p>",
                )
                + step(
                    3,
                    "Ask two new questions",
                    "<p>Do not repeat information already in the account.</p><p><strong>Complete frame:</strong> “I heard you say ____. What ____?”</p>",
                )
                + step(
                    4,
                    "Try one safe workplace card",
                    "<div style=\"border:1px solid #bad4df;border-radius:8px;padding:12px 16px;margin:12px 0\"><p><strong>Supply handoff:</strong> The first-aid cabinet seems low on gloves, but the inventory says two boxes remain. The next shift needs a clear count and safe next step.</p><p><strong>Appointment mix-up:</strong> A fictional reminder lists Tuesday while the office calendar lists Thursday. Use no real names, phone numbers, or appointment details.</p><p><strong>Equipment problem:</strong> A cart wheel sticks only when the cart is full, but the request says only “cart broken.”</p></div><p>Choose one. Paraphrase, ask one new question, and name a safe next step. Acting and written analysis are equal.</p>",
                )
                + step(
                    5,
                    "Complete the evidence check",
                    f'<p><a href="{quiz_url}">Open the Active Listening Evidence Check</a>. It is ungraded and retryable. This is the transfer check, so do not complete a second exit sheet.</p>',
                ),
                "DONE": "<ul><li>four details sorted with reasons;</li><li>two new questions;</li><li>one safe practice response;</li><li>Canvas evidence check complete.</li></ul>",
                "SUPPORT": "<p>essential = esencial · background = contexto · paraphrase = parafrasear · clarify = aclarar. Complete frames are beside Steps 2 and 3.</p>",
                "FALLBACK": "<p>The embedded pages and optional lab contain the complete route. Real chest pain with shortness of breath needs immediate adult or emergency help.</p>",
            },
            3: {
                "TITLE": "Advocate, Set a Goal, and Protect the Time",
                "PURPOSE": "Turn a need into a realistic goal, time plan, and backup.",
                "TOPIC": "Goals and Time",
                "I_CAN": "I can state a need respectfully and build a SMART goal with protected work time and a backup strategy.",
                "SHOW_LEARNING": "Complete the Advocacy, SMART Goal, and Time Plan.",
                "TODAY": "<ul><li>read three community voices;</li><li>write one SMART goal;</li><li>schedule two actions and one backup.</li></ul>",
                "READY": f"<p>Open {file_link(files['SMART']['id'], 'the Advocacy, SMART Goal, and Time Plan')} and keep {file_link(files['RUBRIC']['id'], 'the weekly rubric')} nearby.</p>",
                "STEPS": step(
                    1,
                    "Identify the need",
                    image_tag(
                        uploads[3]["fyf-advocacy-need.png"]["id"],
                        "Find Your Future fictional mobile farmers market advocacy scenario and three community voices",
                        700,
                    )
                    + "<p>Name one voice that should shape the plan and one respectful action.</p>",
                )
                + step(
                    2,
                    "Build the SMART goal",
                    "<p>Use “end of the next class” or the teacher-posted Week 6 checkpoint. Your goal needs an action, measure, reason, and deadline.</p><div style=\"border-left:4px solid #1f617a;background:#f2f8fb;padding:10px 14px;margin:12px 0\"><p><strong>Worked model:</strong> “By the Week 6 checkpoint, I will compare three careers using one responsibility and one preparation fact for each so I can choose one route to investigate next. I will work Tuesday from 4:00–4:20 and Thursday from 4:00–4:20. If a site is blocked, I will use the saved guide and finish the same comparison offline.”</p><p><strong>Find:</strong> the action, measure, reason, deadline, two work blocks, obstacle, and different backup route.</p></div><p><strong>Complete frame:</strong> “By ____, I will ____ as shown by ____.”</p>",
                )
                + step(
                    3,
                    "Protect the time",
                    "<p>Schedule two short work blocks. Name an obstacle and an if-then backup.</p><p><strong>Complete frame:</strong> “I will work on it ____. If ____, then I will ____.”</p>",
                )
                + step(
                    4,
                    "Keep it private or ask for feedback",
                    "<p>Use a private self-check, teacher conference, or optional peer response.</p>",
                ),
                "DONE": "<ul><li>all five SMART parts;</li><li>two time blocks;</li><li>one obstacle and useful backup;</li><li>two-career advocacy transfer.</li></ul>",
                "SUPPORT": "<p>goal = meta · deadline = fecha límite · obstacle = obstáculo · backup = alternativa. Complete frames are beside Steps 2 and 3.</p>",
                "FALLBACK": "<p>If you do not want to share a personal goal, revise a fictional student's goal and use the same checklist.</p>",
            },
            4: {
                "TITLE": "Write So the Reader Can Act",
                "PURPOSE": "Create a fictional public message and rewrite a workplace message using fixed facts.",
                "TOPIC": "Transferable Skills",
                "I_CAN": "I can write a clear fictional public message and revise a workplace message using only supplied facts.",
                "SHOW_LEARNING": "Complete the FYF Little Library message and one fixed-fact workplace rewrite.",
                "TODAY": "<ul><li>write a clear Little Library update;</li><li>give useful feedback;</li><li>rewrite one vague workplace message.</li></ul>",
                "READY": f"<p>Open your workbook to FYF pp. 147-148. If your teacher assigns the private/paper route, open the one-page {file_link(files['WRITE']['id'], 'Workplace Message Companion')}.</p>",
                "STEPS": step(
                    1,
                    "Use four writing checks",
                    image_tag(
                        uploads[4]["fyf-written-post.png"]["id"],
                        "Find Your Future fictional Little Library post frame and four writing tips",
                        700,
                    )
                    + "<p>Reader-focused. Clear and concise. On-topic. Proofread.</p>",
                )
                + step(
                    2,
                    "Draft a fictional post",
                    image_tag(
                        uploads[4]["fyf-little-library-prompt.png"]["id"],
                        "Find Your Future fictional Little Library scenario and brainstorm prompts",
                        700,
                    )
                    + "<p>Do not use a real account, address, photo, handle, phone number, or personal name.</p>",
                )
                + step(
                    3,
                    "Choose the feedback route",
                    f'<p><a href="{discussion_url}">Open the optional Little Library Message Lab discussion</a>, or use the private written route. The Discussion collects the fictional post, one fixed-fact workplace rewrite, and Notice + Question + Next Step feedback. The private route uses the same criteria.</p>',
                )
                + step(
                    4,
                    "Rewrite one fixed message",
                    "<p>Use only the supplied supply, schedule, or cart-repair facts in the Discussion or companion. Do not invent medical guidance, test results, charting, or workplace policy.</p><p><strong>Complete frame:</strong> “The ____ is ____. Please ____ by ____. Questions should go to ____.”</p>",
                ),
                "DONE": "<ul><li>fictional status and reader action;</li><li>two useful hashtags;</li><li>one feedback response or private self-check;</li><li>one fixed-fact workplace rewrite.</li></ul>",
                "SUPPORT": "<p>status = estado · audience = audiencia · concise = conciso · proofread = revisar. The complete workplace-message frame is beside Step 4.</p>",
                "FALLBACK": "<p>The paper/private route is equal. No public post or peer reply is required for full evidence.</p>",
            },
            5: {
                "TITLE": "Record Experience and Connect Skills to a Plan",
                "PURPOSE": "Complete the required Xello task, study skill suggestions, and revise your next step.",
                "TOPIC": "Goals and Time",
                "I_CAN": "I can add one authentic Work experience, analyze skill suggestions, and revise a goal using evidence from two careers.",
                "SHOW_LEARNING": "Submit the four-part Communication and Goal Synthesis.",
                "TODAY": "<ul><li>save one real Work experience in Xello;</li><li>record two Skills Matcher suggestions or use the fixed career pair;</li><li>revise a goal and compare one skill across careers.</li></ul>",
                "READY": f'<p>Open the <a href="{minor_url}">Communication and Goal Synthesis</a> and {file_link(files["RUBRIC"]["id"], "the 16-point rubric")}. Use {file_link(files["SYNTH"]["id"], "the optional two-page paper route")} only when your teacher assigns paper.</p>',
                "STEPS": step(
                    1,
                    "Add one real Work experience",
                    "<p>ClassLink &gt; Xello &gt; About Me &gt; Experiences &gt; Work. Add at least one experience that actually happened and save. Do not invent one or enter private details.</p>",
                )
                + step(
                    2,
                    "Use the Skills Matcher",
                    '<p><a href="https://www.careeronestop.org/Toolkit/Skills/skills-matcher.aspx">Open the CareerOneStop Skills Matcher</a>. Rate all 40 areas in chunks of 10. Pause after 10, 20, and 30. Record two suggestions and one pattern. Results are idea-generators, not a verdict; use more than one source and discuss important decisions with a counselor. Do not submit a screenshot.</p><div style="border-left:4px solid #1f617a;background:#f2f8fb;padding:10px 14px;margin:12px 0"><p><strong>Fixed pair if the tool is blocked or stopped:</strong></p><ul><li><strong>IT support specialist:</strong> paraphrases the user’s problem, asks when it happens, and records a clear support ticket.</li><li><strong>Dental assistant:</strong> listens for the person’s exact concern, repeats it to confirm, and routes it to the licensed team member without diagnosing.</li></ul><p>Record CareerOneStop as incomplete. Compare one communication skill across this pair; do not invent assessment results.</p></div><p><strong>Complete frame:</strong> “The suggestions share ____ because I rated ____ as important.”</p>',
                )
                + step(
                    3,
                    "Revise the plan",
                    "<p>Update the SMART goal, time block, and backup strategy from Day 3.</p><p><strong>Complete frame:</strong> “By ____, I will ____. I will work on it ____. If ____, then ____.”</p>",
                )
                + step(
                    4,
                    "Show transfer",
                    "<p>Name two Week 5 activities that show the Powerskill. Then compare the skill across two careers: name what stays the same and what changes.</p><p><strong>Complete frame:</strong> “I showed ____ when I ____ and ____. In ____, the worker uses the skill when ____. In ____, the same skill ____.”</p>",
                ),
                "DONE": "<ul><li>Xello save or catch-up recorded;</li><li>two skill suggestions or the fixed career pair recorded honestly;</li><li>revised goal and time plan;</li><li>two Week 5 examples and a two-career transfer comparison.</li></ul>",
                "SUPPORT": "<p>experience = experiencia; responsibility = responsabilidad; suggestion = sugerencia; transferable = transferible. Complete frames are beside Steps 2-4.</p>",
                "FALLBACK": "<p>If Xello fails, complete the reflection and finish the required save in supervised catch-up. If CareerOneStop fails or remains incomplete at the stop time, use the fixed IT support specialist and dental assistant pair in Step 2 and record the tool as incomplete. Xello Time Management is supplemental and does not replace Work experiences.</p>",
            },
        }
        teacher = {
            1: {
                "TITLE": "Resolve Conflict and Keep the Work Moving",
                "TOPIC": "Transferable Skills",
                "OBJECTIVE": "Students will use listening, compromise, and respectful language to solve a team conflict, then transfer the skill to two careers.",
                "TEKS": "d(4)(B)",
                "DOL": "FYF Conflict Resolution Plan and individual two-career transfer check.",
                "SUBTITLE": "50 minutes · TEKS d(4)(B)",
                "ALERT": "<strong>Protect the plan, not the poster.</strong> The three-row conflict plan and two-career transfer response are the evidence. The advertisement is optional.",
                "PREP": f"<ul><li><strong>Per student:</strong> 1 FYF workbook and 1 pencil.</li><li><strong>Teacher:</strong> 1 display/device with the embedded FYF pages, {file_link(files['GUIDE']['id'], 'transfer guide')}, projected roles, and timer.</li><li><strong>Print only for assigned students:</strong> 1 two-page {file_link(files['CONFLICT']['id'], 'no-workbook route')} per student, double-sided when available. Default copies: 0.</li><li><strong>Grouping:</strong> groups of 3-4. Reader, recorder, facilitator, designer; omit designer in groups of 3. Every student completes an individual transfer check.</li></ul>",
                "EVIDENCE": "<p>Three specific solutions plus two-career transfer. Formative only.</p>",
                "FLOW": flow(
                    "#5a2d91",
                    "Warm-up · 5",
                    "Turn traits into observable communication actions.",
                )
                + flow(
                    "#4a9d2f",
                    "Powerskills · 7",
                    "Defend one skill shared by two careers.",
                )
                + flow(
                    "#1f617a",
                    "Three moves · 5",
                    "Listen, compromise fairly, stay respectful.",
                )
                + flow(
                    "#e3ad19",
                    "Conflict plan · 20",
                    "Check one row from every group at minute 12.",
                )
                + flow(
                    "#1f617a",
                    "Debrief/check · 5",
                    "Check the plan before transfer.",
                )
                + flow("#1f617a", "Individual transfer · 5", "Written, oral, AAC, or conference response.")
                + flow("#606c76", "Submit and reset · 3", "Confirm evidence; return materials."),
                "MONITOR": "<ul><li><strong>Model CFU:</strong> explain why voting is incomplete before needs are heard.</li><li><strong>Lap 1:</strong> check one row per group for each need and a specific action. If more than 1 in 4 groups writes “talk it out,” model a concrete action and backup.</li><li><strong>Lap 2:</strong> check safety language. Any compromised safety rule triggers a pause: protect safety, follow procedure, notify the appropriate adult.</li><li><strong>Strong evidence:</strong> each need, fair action, backup, two careers, likely conflict, first safe move.</li><li><strong>Trim:</strong> at minute 35, finish Name and Launch date in writing; give one Marketing-jobs action orally. Do not cut individual transfer or close.</li></ul>",
                "SUPPORT": "<p>Place these beside the response: <strong>“Each person needs ____. We can ____ so that ____. If that does not work, we will ____.”</strong> and <strong>“In ____, the conflict could be ____. The first safe move is ____ because ____.”</strong> Permit independent, speech-to-text, oral, and AAC routes. Do not grade drawing.</p>",
                "FALLBACK": "<p>The student page contains all sources. An absent student completes the same plan independently. Do not assign both FYF and the duplicate no-workbook plan.</p>",
            },
            2: {
                "TITLE": "Listen for the Detail That Matters",
                "TOPIC": "Transferable Skills",
                "OBJECTIVE": "Students will separate essential from background detail, ask a new question, and show how active listening transfers to another career.",
                "TEKS": "d(4)(B)",
                "DOL": "FYF p. 63 responses and completed Canvas Active Listening Evidence Check.",
                "SUBTITLE": "50 minutes · TEKS d(4)(B)",
                "ALERT": "<strong>Listening practice, not diagnosis.</strong> Real chest pain with shortness of breath requires immediate adult or emergency help.",
                "PREP": f"<ul><li><strong>Per student:</strong> 1 FYF workbook, 1 pencil, and 1 internet-connected device.</li><li><strong>Teacher:</strong> 1 display/device with the written Maria account, three embedded practice cards, and unpublished quiz.</li><li><strong>Print only for assigned students:</strong> 1 two-page {file_link(files['LISTEN']['id'], 'Active Listening Lab')} per no-workbook/no-device student, double-sided when available. Default copies: 0.</li><li><strong>Grouping:</strong> individual FYF/quiz evidence; pairs of 2 for one practice card. Written analysis equals acting.</li></ul>",
                "EVIDENCE": "<p>Four justified details, two new questions, and the ungraded Canvas evidence check. The quiz is the transfer check; no second exit sheet.</p>",
                "FLOW": flow(
                    "#5a2d91",
                    "Warm-up · 4",
                    "Name a strategy for a detail-heavy story.",
                )
                + flow("#4a9d2f", "Two reads · 7", "Pencils down, then mark evidence.")
                + flow("#1f617a", "Sort · 10", "Essential or background with reasons.")
                + flow(
                    "#e3ad19",
                    "Ask and compare · 9",
                    "Two new questions and one comparison.",
                )
                + flow(
                    "#1f617a",
                    "Safe practice · 12",
                    "One card: paraphrase, question, safe route.",
                )
                + flow("#1f617a", "Canvas evidence check · 5", "Retry and read one feedback message.")
                + flow("#606c76", "Review and reset · 3", "Confirm FYF page; close quiz."),
                "MONITOR": "<ul><li><strong>Second-read CFU:</strong> point to one exact detail without diagnosing.</li><li><strong>Lap 1:</strong> check two essential and two background details with reasons. If more than 1 in 4 sorts by interest instead of relevance, model relevance to the listener's task.</li><li><strong>Lap 2:</strong> check questions request new information. Use “What gap is still open?” when students repeat known details.</li><li><strong>Key:</strong> persistent tightness, onset, shortness of breath, spread, medication/history, family history are essential; paperwork, busy week, bag/coffee are generally background.</li><li><strong>Trim:</strong> at minute 32, use one practice card and no repeated role rotations. Do not cut the role-boundary quiz item or close.</li></ul>",
                "SUPPORT": "<p>Keep the account visible. Place these beside the task: <strong>“The detail ____ is essential/background because ____.”</strong> and <strong>“I heard you say ____. What ____?”</strong> Offer actor, listener, observer, and written routes.</p>",
                "FALLBACK": "<p>The embedded cards and optional lab provide the no-workbook route. No student shares personal health information or performs publicly. A no-device student uses the lab transfer prompt instead of completing a duplicate quiz later unless the teacher assigns recovery.</p>",
            },
            3: {
                "TITLE": "Advocate, Set a Goal, and Protect the Time",
                "TOPIC": "Goals and Time",
                "OBJECTIVE": "Students will state a need respectfully and build a SMART goal with protected time and a backup strategy.",
                "TEKS": "d(4)(A); d(4)(B) through the two-career transfer check",
                "DOL": "Advocacy, SMART Goal, and Time Plan.",
                "SUBTITLE": "50 minutes · TEKS d(4)(A), d(4)(B)",
                "ALERT": "<strong>SMART is not enough by itself.</strong> Students also schedule the work and create a backup strategy.",
                "PREP": f"<ul><li><strong>Per student:</strong> 1 two-page {file_link(files['SMART']['id'], 'SMART/time plan')}, double-sided when available, and 1 pencil; or 1 device for the approved digital annotation route.</li><li><strong>Teacher:</strong> 1 display/device with FYF p. 134 and {file_link(files['RUBRIC']['id'], 'student-visible weekly rubric')}. The worked model is embedded in the Student Guide.</li><li><strong>Checkpoint:</strong> use end of next class or the teacher-posted Week 6 checkpoint; no extra calendar handout.</li><li><strong>Grouping:</strong> individual/private goal evidence; peer response optional.</li></ul>",
                "EVIDENCE": "<p>SMART goal, two time blocks, obstacle, if-then backup, and two-career advocacy transfer.</p>",
                "FLOW": flow(
                    "#5a2d91",
                    "Assertive warm-up · 4",
                    "Rewrite one aggressive sentence.",
                )
                + flow(
                    "#4a9d2f",
                    "Advocacy need · 8",
                    "Use affected voices without repeating a stale national count.",
                )
                + flow(
                    "#1f617a", "SMART model · 7", "Action, measure, reason, deadline."
                )
                + flow(
                    "#e3ad19",
                    "Draft and schedule · 20",
                    "Protect time and plan for one obstacle.",
                )
                + flow(
                    "#1f617a",
                    "Revise and transfer · 7",
                    "Private revision and two-career check.",
                )
                + flow("#606c76", "Submit and reset · 4", "Check all parts; preserve privacy."),
                "MONITOR": "<ul><li><strong>Model CFU:</strong> identify action, measure, and deadline in the example.</li><li><strong>Lap 1:</strong> check visible product/count and real checkpoint. If more than 1 in 4 uses “someday,” revise one deadline together.</li><li><strong>Lap 2:</strong> check that the backup changes route, not goal. Prompt “What different route still reaches the evidence?”</li><li><strong>Full evidence:</strong> five SMART parts, two time blocks, obstacle, controllable backup, two-career advocacy transfer.</li><li><strong>Trim:</strong> use private self-check instead of peer feedback. Do not cut backup, revision, transfer, or close.</li></ul>",
                "SUPPORT": "<p>Place this beside the task: <strong>“By ____, I will ____ as shown by ____. I will work on it ____. If ____, then I will ____.”</strong> Goals remain private. A fictional goal may replace personal disclosure.</p>",
                "FALLBACK": "<p>No live platform is required. Speech-to-text, teacher conference, paper, and private digital annotation are equal. The revised worksheet provides full-width writing space.</p>",
            },
            4: {
                "TITLE": "Write So the Reader Can Act",
                "TOPIC": "Transferable Skills",
                "OBJECTIVE": "Students will write a clear fictional public message and revise a workplace message using only supplied facts.",
                "TEKS": "d(4)(B)",
                "DOL": "FYF Little Library message and fixed-fact workplace rewrite.",
                "SUBTITLE": "50 minutes · TEKS d(4)(B)",
                "ALERT": "<strong>Everything stays fictional.</strong> The Discussion is optional and ungraded; the private written route is equal.",
                "PREP": f"<ul><li><strong>Per student:</strong> 1 FYF workbook and 1 pencil; add 1 internet-connected device when using the Discussion.</li><li><strong>Teacher:</strong> 1 display/device with the fixed messages and privacy rule.</li><li><strong>Private/paper route:</strong> 1 one-page {file_link(files['WRITE']['id'], 'Workplace Message Companion')} per student. Discussion route default copies: 0.</li><li><strong>Grouping:</strong> individual drafts; pairs of 2 for optional feedback. Private self-check is equal.</li><li>Choose Discussion or private route before class.</li></ul>",
                "EVIDENCE": "<p>FYF fictional Little Library message and one fixed-fact workplace rewrite. Feedback/self-check supports revision but is not a separate artifact.</p>",
                "FLOW": flow(
                    "#5a2d91",
                    "Missing-detail warm-up · 4",
                    "Identify what the reader still needs.",
                )
                + flow(
                    "#4a9d2f",
                    "Four writing checks · 7",
                    "Reader, clarity, topic, proofread.",
                )
                + flow(
                    "#1f617a",
                    "Little Library post · 17",
                    "Fictional status, action, and two hashtags.",
                )
                + flow(
                    "#e3ad19",
                    "Fixed-fact rewrite · 13",
                    "Use only supplied facts and safe routing.",
                )
                + flow(
                    "#1f617a",
                    "Feedback and transfer · 6",
                    "Notice + Question + Next Step; compare readers.",
                )
                + flow("#606c76", "Submit and reset · 3", "Confirm both message jobs."),
                "MONITOR": "<ul><li><strong>Warm-up CFU:</strong> identify missing status, audience, and requested action.</li><li><strong>Lap 1:</strong> check fictional status and reader action. If more than 1 in 4 posts includes identifying information, stop and reset the fictional-data rule.</li><li><strong>Lap 2:</strong> underline supplied workplace facts. Invented policy or medical guidance triggers revision from the facts only.</li><li><strong>Strong evidence:</strong> reader, exact status, requested action, safe routing, and one quality transferred across careers.</li><li><strong>Trim:</strong> use private self-check instead of peer reply. Do not cut workplace rewrite, transfer, or close.</li></ul>",
                "SUPPORT": "<p>Place this beside the rewrite: <strong>“The ____ is ____. Please ____ by ____. Questions should go to ____.”</strong> Offer typed, handwritten, audio, and speech-to-text drafts. Do not grade hashtags or mechanics unless meaning is unclear.</p>",
                "FALLBACK": "<p>Skip public posting for privacy, absence, or accommodation. FYF remains the Little Library surface; the one-page companion adds only the missing workplace rewrite and transfer evidence.</p>",
            },
            5: {
                "TITLE": "Record Experience and Connect Skills to a Plan",
                "TOPIC": "Goals and Time",
                "OBJECTIVE": "Students will add one authentic Work experience in Xello, analyze Skills Matcher suggestions, and revise a goal using transferable-skill evidence.",
                "TEKS": "d(4)(A), d(4)(B); d(1)(A) supporting evidence",
                "DOL": "Submitted Communication and Goal Synthesis scored with the 16-point rubric.",
                "SUBTITLE": "50 minutes · TEKS d(4)(A), d(4)(B); d(1)(A) supporting",
                "ALERT": "<strong>Required task: Work experiences.</strong> Xello Time Management is supplemental and does not replace this Grade 8 completion standard.",
                "PREP": f'<ul><li><strong>Per student:</strong> 1 internet-connected device with ClassLink, Xello, CareerOneStop, and Canvas access.</li><li><strong>Teacher:</strong> 1 device with Completion Standards open and 1 display for Skills Matcher checkpoints.</li><li><strong>Print only for assigned students:</strong> 1 two-page {file_link(files["SYNTH"]["id"], "synthesis")} per student, double-sided when available. Default copies: 0.</li><li><strong>Grouping:</strong> individual/private profile and Minor evidence; optional partner talk shares only non-sensitive patterns.</li><li>Open the unpublished <a href="{minor_url}">Communication and Goal Synthesis</a>, {file_link(files["RUBRIC"]["id"], "student-visible rubric")}, and licensed {file_link(files["XELLO"]["id"], "My experiences guide")}.</li></ul>',
                "EVIDENCE": "<p>Required Xello save/report plus the four-part Canvas Minor: revised goal, time plan and backup, two Week 5 activity examples, two-career skill transfer, and one evidence-based next action.</p>",
                "FLOW": flow(
                    "#5a2d91",
                    "Responsibility warm-up · 4",
                    "List one real responsibility without forcing a category.",
                )
                + flow(
                    "#4a9d2f",
                    "Xello Work experiences · 10",
                    "Add at least one authentic experience or record catch-up.",
                )
                + flow(
                    "#1f617a",
                    "Skills Matcher · 18",
                    "Rate in chunks of 10; record two suggestions and one pattern.",
                )
                + flow(
                    "#e3ad19",
                    "Private synthesis · 13",
                    "Revise goal, time, backup, and transfer evidence.",
                )
                + flow(
                    "#1f617a",
                    "Submit/verify · 5",
                    "Check report and list absences/access failures.",
                ),
                "MONITOR": "<ul><li><strong>Minute 14 CFU:</strong> Work experience saved or catch-up recorded privately.</li><li><strong>Matcher checkpoints:</strong> after ratings 10, 20, and 30, verify progress and read anchors aloud if students click without reading.</li><li><strong>Synthesis lap:</strong> check revised goal, protected time, backup, two Week 5 activity examples, and one communication action across two careers. Prompt “What does the worker do with the skill?”</li><li><strong>Boundary:</strong> results are idea-generators from self-ratings, not identity or verdict. Use multiple sources and counselor discussion for decisions.</li><li><strong>Trim:</strong> at minute 32, stop after the current chunk and use the fixed IT support specialist and dental assistant pair in the Student Guide. Record Matcher incomplete; protect Xello, synthesis, and submit.</li></ul>",
                "SUPPORT": "<p>Place these beside the response: <strong>“I used ____ when I ____.” “The suggestions share ____ because I rated ____ as important.” “In ____, the worker uses ____ when ____.”</strong> Read anchors aloud in chunks. Private writing, audio, and teacher conference are equal.</p>",
                "FALLBACK": "<p>Paper does not replace Xello completion. Move the save to supervised catch-up. If CareerOneStop is blocked/incomplete, use the fixed IT support specialist and dental assistant pair supplied in the Student Guide and paper route. Do not pretend the assessment was completed. Xello Time Management is supplemental only.</p>",
            },
        }
        titles = {
            1: "STUDENT: 2SW Wk5 Day 1 - Conflict Resolution",
            2: "STUDENT: 2SW Wk5 Day 2 - Active Listening",
            3: "STUDENT: 2SW Wk5 Day 3 - Advocacy and SMART Time Plan",
            4: "STUDENT: 2SW Wk5 Day 4 - Written Message Lab",
            5: "STUDENT: 2SW Wk5 Day 5 - Work Experience and Skills Synthesis",
        }
        pages = {}
        order = []
        for day in range(1, 6):
            header = await upsert_subheader(c, module["id"], f"Day {day}")
            order.append(("SubHeader", header["id"], f"Day {day}"))
            st = titles[day]
            student_page = await upsert_page(
                c,
                st,
                render(
                    "2sw-wk5-student.html",
                    {"COURSE_ID": COURSE_ID, "DAY": day, **student[day]},
                ),
                slugify(st),
            )
            tt = f"TEACHER: 2SW Wk5 Day {day} Facilitator Guide"
            teacher_page = await upsert_page(
                c,
                tt,
                render(
                    "2sw-wk5-teacher.html",
                    {
                        "COURSE_ID": COURSE_ID,
                        "DAY": day,
                        "STUDENT_PAGE_URL": student_page["url"],
                        **teacher[day],
                    },
                ),
                slugify(tt),
            )
            await upsert_page_item(c, module["id"], teacher_page, tt)
            await upsert_page_item(c, module["id"], student_page, st)
            pages[day] = {"teacher": teacher_page, "student": student_page}
            order.extend(
                [("Page", teacher_page["url"], tt), ("Page", student_page["url"], st)]
            )
            if day == 2:
                await upsert_quiz_item(c, module["id"], quiz)
                order.append(("Quiz", quiz["id"], QUIZ_TITLE))
            if day == 4:
                await upsert_discussion_item(c, module["id"], discussion)
                order.append(("Discussion", discussion["id"], DISCUSSION_TITLE))
            if day == 5:
                await upsert_assignment_item(c, module["id"], minor)
                order.append(("Assignment", minor["id"], MINOR_TITLE))
        items = await paged(c, f"/courses/{COURSE_ID}/modules/{module['id']}/items")

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
                    if entry["id"] not in keep_ids and matches_item(entry, kind, key)
                ),
                None,
            )
            if item is None:
                raise RuntimeError(f"Missing expected module item: {kind} {key}")
            keep_ids.add(item["id"])
        for entry in items:
            if entry["id"] not in keep_ids:
                await api(
                    c,
                    "DELETE",
                    f"/courses/{COURSE_ID}/modules/{module['id']}/items/{entry['id']}",
                )
        items = await paged(c, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, start=1):
            item = next(entry for entry in items if matches_item(entry, kind, key))
            await api(
                c,
                "PUT",
                f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}",
                data={"module_item[position]": position, "module_item[title]": title},
            )
        final = await paged(c, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        module = await api(c, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        if module.get("published"):
            raise RuntimeError("Week 5 module unexpectedly published")
        if quiz.get("published"):
            raise RuntimeError("Week 5 practice quiz unexpectedly published")
        if discussion.get("published") or discussion.get("assignment_id"):
            raise RuntimeError("Week 5 practice discussion is published or graded")
        if minor.get("published") or float(minor.get("points_possible") or 0) != 100:
            raise RuntimeError("Week 5 mapped Minor invariant failed")
        published_pages = [
            value["url"]
            for pair in pages.values()
            for value in pair.values()
            if value.get("published")
        ]
        if published_pages:
            raise RuntimeError(f"Published Week 5 pages remain: {published_pages}")
        if len(final) != len(order):
            raise RuntimeError(
                f"Expected {len(order)} Week 5 module items; found {len(final)}"
            )
        for position, ((kind, key, title), item) in enumerate(zip(order, final), start=1):
            if (
                item.get("position") != position
                or item.get("title") != title
                or not matches_item(item, kind, key)
            ):
                raise RuntimeError(f"Week 5 module order mismatch at position {position}")
        print(
            json.dumps(
                {
                    "module": {"id": module["id"], "published": module["published"]},
                    "quiz": {"id": quiz["id"], "published": quiz.get("published")},
                    "discussion": {
                        "id": discussion["id"],
                        "published": discussion.get("published"),
                    },
                    "minor": {
                        "id": minor["id"],
                        "published": minor.get("published"),
                        "points": minor.get("points_possible"),
                        "submission_types": minor.get("submission_types"),
                    },
                    "folders": {
                        str(d): {"id": f["id"], "locked": f["locked"]}
                        for d, f in folders.items()
                    },
                    "files": {k: v["id"] for k, v in files.items()},
                    "pages": {
                        str(d): {
                            k: {"url": v["url"], "published": v["published"]}
                            for k, v in p.items()
                        }
                        for d, p in pages.items()
                    },
                    "items": [
                        {
                            "id": i["id"],
                            "position": i["position"],
                            "title": i["title"],
                            "type": i["type"],
                            "page_url": i.get("page_url"),
                            "content_id": i.get("content_id"),
                        }
                        for i in final
                    ],
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
