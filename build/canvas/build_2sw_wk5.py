"""Build the unpublished 2SW Week 5 communication module, practice quiz, and discussion."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
from urllib.parse import urlencode
import httpx

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
STUDENT_GOOGLE_COPY_URLS = {
    1: "https://docs.google.com/document/d/1nV08lKrHpHUaeUygdCwVsSlx2qBDmvaxNGTNcc2fg5s/copy",
    2: "https://docs.google.com/document/d/1MYCdVB6EZFXZbuIEfGPWIrC0R0622lGLIBgRE6eXmxw/copy",
    3: "https://docs.google.com/document/d/1cF0nX0yn3SgRsl3m53ZGSKJLDJgJ2-qcv0vYhmtpwNw/copy",
    4: "https://docs.google.com/document/d/1te6GqUbdLvHn1I75m-NQFYCfZQhHFW8_bJ1azYkKGOA/copy",
    5: "https://docs.google.com/document/d/1dk2cjFBbRzPaFIRb0rWaED-p87mDiRzVs7NT0JCa4Jo/copy",
}


# One Google Doc per worksheet (build/google_docs/student_worksheet_docs.json).
# Keyed by (day, anchor label) so a worksheet button never opens the day's exit ticket.
STUDENT_WORKSHEET_COPY_URLS = {
    (1, 'the optional no-workbook route'): "https://docs.google.com/document/d/1fcEF3KRszk0K7BUDRIKDLseKlE97qa98iFHAJ-YLtAs/copy",
    (2, 'the optional Active Listening Lab'): "https://docs.google.com/document/d/146IUed7GJ2Eq_VqN2bCd_qCVga7w4gsJTdx8YH7KEZI/copy",
    (3, 'the Advocacy, SMART Goal, and Time Plan'): "https://docs.google.com/document/d/1L7AaMPYKsNscR-7x1l_6oCYN_6pV0WnsuvbnzL_X_sg/copy",
    (4, 'Workplace Message Companion'): "https://docs.google.com/document/d/1hJj50BVJSXr_Udf-PryPEVn3Beab8JEDWV-oNYC8p4w/copy",
    (5, 'the optional two-page paper response'): "https://docs.google.com/document/d/1TIi7L2Kdie-5pfjV-LtfaY9KeTNbWe2qobuhqD4lvfw/copy",
}


def student_copy_link(day, label):
    url = STUDENT_WORKSHEET_COPY_URLS.get((day, label), STUDENT_GOOGLE_COPY_URLS[day])
    return f'<a href="{url}">{label}</a>'

MODULE_NAME = "2SW Wk5: Communication and Goal Setting"
QUIZ_TITLE = "PRACTICE: Active Listening Evidence Check"
DISCUSSION_TITLE = "PRACTICE: Little Library Message Lab"
MINOR_TITLE = "MINOR 3: Communication and Goal Synthesis"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/2sw/wk5"


# Preservation-first adaptation of Jenna Hainlen's teacher-shared
# "Self-Advocacy Scenarios" deck. The source deck contains 36 school, social,
# workplace, and adult-life situations. This bank keeps the strongest Grade 7
# fits, removes private-disclosure prompts and adult financial/legal disputes,
# and retains the source's short scenario-first teaching move. The complete
# source deck stays in the private AVID reference library; it is not uploaded by
# this importer.
ADVOCACY_SCENARIOS = [
    (
        "Confusing directions",
        "You are working on a CCE task and reach a confusing section. You do not know how to finish it, and the checkpoint is tomorrow.",
    ),
    (
        "Your name",
        "It is the third week of school, and a teacher still mispronounces your name.",
    ),
    (
        "Return after an absence",
        "You return to a project after an absence. A checkpoint is coming up, and you do not know what changed or what you still need to finish.",
    ),
    (
        "Finding a resource",
        "You need a useful book or source, but this is your first time using the library and you do not know where to begin.",
    ),
    (
        "Uneven group work",
        "You are working on a group project, but the other group members expect you to do most of the work.",
    ),
    (
        "A distracting workspace",
        "A student at your table is off-task and distracting. It is making it hard for you to focus on the work.",
    ),
    (
        "Different career interests",
        "A family member wants you to explore the same career they chose, but you want to investigate something different.",
    ),
    (
        "Unfamiliar workplace task",
        "During fictional workplace training, a situation comes up that was not in the directions. You do not want to interrupt, but you also do not want to guess or create a safety problem.",
    ),
    (
        "An uncomfortable comment",
        "During a fictional workplace or group task, someone makes repeated comments that make the work feel uncomfortable or unsafe.",
    ),
]


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
    unlocked = []
    for entry in final:
        if not entry.get("locked"):
            refreshed = await api(c, "GET", f"/files/{entry['id']}")
            if not refreshed.get("locked"):
                unlocked.append(entry.get("display_name") or entry.get("filename"))
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
    return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0 0 6px;color:{color}">{title}</h4>{text}</div>'


def advocacy_scenario_bank():
    cards = "".join(
        f'<li style="margin:0 0 10px"><strong>{title}:</strong> {scenario}</li>'
        for title, scenario in ADVOCACY_SCENARIOS
    )
    return (
        '<details style="border:1px solid #d9c9ed;border-radius:8px;padding:12px 16px;margin:14px 0;background:#faf8fd">'
        '<summary style="font-weight:700;color:#5a2d91;cursor:pointer">Fictional scenario bank</summary>'
        f'<ol style="padding-left:22px">{cards}</ol>'
        '</details>'
    )


def advocacy_frame():
    return (
        '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:12px 16px;margin:12px 0">'
        '<p style="margin-top:0"><strong>Notice:</strong> What happened or what is unclear?</p>'
        '<p><strong>Need:</strong> What support, clarification, space, or route is needed?</p>'
        '<p><strong>Reason:</strong> What task, access, or safety reason can be shared without private details?</p>'
        '<p style="margin-bottom:0"><strong>Next step:</strong> What safe action could happen now, or which trusted adult can help?</p>'
        '</div>'
    )


def advocacy_model():
    return (
        '<div style="border:1px solid #bad4df;border-radius:8px;background:#fff;padding:12px 16px;margin:12px 0">'
        '<p style="margin-top:0"><strong>Worked model - confusing directions</strong></p>'
        '<p><strong>Notice:</strong> “The last two directions are unclear to me.”</p>'
        '<p><strong>Need:</strong> “I need one example or the steps read aloud.”</p>'
        '<p><strong>Reason:</strong> “The checkpoint is tomorrow, and I want to finish the task correctly.”</p>'
        '<p style="margin-bottom:0"><strong>Next step:</strong> “Can you show me the first step, or tell me who can help?”</p>'
        '</div>'
    )


def advocacy_safety_boundary():
    return (
        '<div style="border-left:5px solid #b33a3a;background:#fff2f2;padding:12px 16px;margin:12px 0">'
        '<strong>Self-advocacy is not self-rescue.</strong> If a situation feels unsafe, threatening, harassing, or medically urgent, stop the practice frame and get a trusted adult right away. Follow campus emergency procedures when immediate help is needed. You never have to share private health, family, disability, or discipline details for this activity.'
        '</div>'
    )


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
    <li>Your two Week 5 communication examples and CareerOneStop Skills Matcher notes or fixed career pair from Day 5</li>
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
                "READY": f"<p>Open your workbook to FYF pp. 144-145. Use {student_copy_link(1, 'the optional no-workbook route')} only when your teacher assigns it. Keep {file_link(files['GUIDE']['id'], 'the Powerskills Transfer Guide')} available for examples.</p>",
                "STEPS": step(
                    1,
                    "Learn the three moves",
                    image_tag(
                        uploads[1]["fyf-powerskills-chart.png"]["id"],
                        "Find Your Future Powerskills chart with ten transferable skills",
                        700,
                    )
                    + "<p>Open your <em>Find Your Future</em> workbook to pp. 12-14 and use the Powerskills chart.</p><p>Listen. Compromise fairly. Stay respectful.</p>",
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
                "READY": f"<p>Open your workbook to FYF pp. 62-63. Use {student_copy_link(2, 'the optional Active Listening Lab')} only when your teacher assigns the no-workbook or extended-practice route.</p>",
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
                "PURPOSE": "Use a clear response frame, then turn a need into a realistic goal, time plan, and backup.",
                "TOPIC": "Goals and Time",
                "I_CAN": "I can state a need respectfully and build a SMART goal with protected work time and a backup strategy.",
                "SHOW_LEARNING": "Complete the Advocacy, SMART Goal, and Time Plan.",
                "TODAY": "<ul><li>practice one fictional self-advocacy scenario;</li><li>read three community voices;</li><li>write one SMART goal;</li><li>schedule two actions and one backup.</li></ul>",
                "READY": f"<p>Open {student_copy_link(3, 'the Advocacy, SMART Goal, and Time Plan')} and keep {file_link(files['RUBRIC']['id'], 'the weekly rubric')} nearby.</p>",
                "STEPS": step(
                    1,
                    "Practice the four-move response",
                    advocacy_frame()
                    + advocacy_model()
                    + advocacy_scenario_bank()
                    + "<p>Use the scenario your teacher selects. If you are absent, choose one from the bank. Write or rehearse one response that uses all four moves. You may keep the response private or use the fictional point of view.</p>"
                    + advocacy_safety_boundary(),
                )
                + step(
                    2,
                    "Use the frame with the advocacy need",
                    image_tag(
                        uploads[3]["fyf-advocacy-need.png"]["id"],
                        "Find Your Future fictional mobile farmers market advocacy scenario and three community voices",
                        700,
                    )
                    + "<p>Open your <em>Find Your Future</em> workbook to p. 134.</p><p>Choose one community voice. Name what the person notices, needs, and can explain, then propose one respectful next step.</p>",
                )
                + step(
                    3,
                    "Build the SMART goal",
                    "<p>Use “end of the next class” or the teacher-posted Week 6 checkpoint. Your goal needs an action, measure, reason, and deadline.</p><div style=\"border-left:4px solid #1f617a;background:#f2f8fb;padding:10px 14px;margin:12px 0\"><p><strong>Worked model:</strong> “By the Week 6 checkpoint, I will compare three careers using one responsibility and one preparation fact for each so I can choose one route to investigate next. I will work Tuesday from 4:00–4:20 and Thursday from 4:00–4:20. If a site is blocked, I will use the saved guide and finish the same comparison offline.”</p><p><strong>Find:</strong> the action, measure, reason, deadline, two work blocks, obstacle, and different backup route.</p></div><p><strong>Complete frame:</strong> “By ____, I will ____ as shown by ____.”</p>",
                )
                + step(
                    4,
                    "Protect the time",
                    "<p>Schedule two short work blocks. Name an obstacle and an if-then backup.</p><p><strong>Complete frame:</strong> “I will work on it ____. If ____, then I will ____.”</p>",
                )
                + step(
                    5,
                    "Keep it private or ask for feedback",
                    "<p>Use a private self-check, teacher conference, or optional peer response.</p>",
                ),
                "DONE": "<ul><li>one Notice, Need, Reason, and Next step practice response;</li><li>all five SMART parts;</li><li>two time blocks;</li><li>one obstacle and useful backup;</li><li>two-career advocacy transfer.</li></ul>",
                "SUPPORT": "<p>advocate = abogar por ti o por otra persona · need = necesidad · reason = razón · next step = próximo paso · goal = meta · deadline = fecha límite · obstacle = obstáculo · backup = alternativa. Use the four labeled moves in Step 1 and the complete goal frames in Steps 3-4.</p>",
                "FALLBACK": "<p>Use a fictional scenario and keep the response private. If a situation is unsafe, threatening, harassing, or medically urgent, stop the practice frame and get a trusted adult right away. You do not have to share private health, family, disability, or discipline details. If you do not want to share a personal goal, revise a fictional student's goal and use the same checklist.</p>",
            },
            4: {
                "TITLE": "Write So the Reader Can Act",
                "PURPOSE": "Create a fictional public message and rewrite a workplace message using fixed facts.",
                "TOPIC": "Transferable Skills",
                "I_CAN": "I can write a clear fictional public message and revise a workplace message using only supplied facts.",
                "SHOW_LEARNING": "Complete the FYF Little Library message and one fixed-fact workplace rewrite.",
                "TODAY": "<ul><li>write a clear Little Library update;</li><li>give useful feedback;</li><li>rewrite one vague workplace message.</li></ul>",
                "READY": f"<p>Open your workbook to FYF pp. 147-148. If your teacher assigns the private/paper route, open the one-page {student_copy_link(4, 'Workplace Message Companion')}.</p>",
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
                "TITLE": "Connect Communication Skills to a Plan",
                "PURPOSE": "Study skill suggestions or fixed career evidence, then revise your next step.",
                "TOPIC": "Goals and Time",
                "I_CAN": "I can analyze skill suggestions or fixed career evidence and revise a goal using evidence from two careers.",
                "SHOW_LEARNING": "Submit the four-part Communication and Goal Synthesis.",
                "TODAY": "<ul><li>name two Week 5 examples with visible communication actions;</li><li>record two Skills Matcher suggestions or use the fixed career pair;</li><li>revise a goal and compare one skill across careers;</li><li>store five short Entry 2 phrases without another submission.</li></ul>",
                "READY": f'<p>Open the <a href="{minor_url}">Communication and Goal Synthesis</a> and {file_link(files["RUBRIC"]["id"], "the 16-point rubric")}. Use {student_copy_link(5, "the optional two-page paper response")} only when your teacher assigns paper. Retrieve your CCE Six-Weeks Evidence Log from the CCE binder or teacher-designated digital folder; it stays with you.</p>',
                "STEPS": step(
                    1,
                    "Sort two Week 5 examples",
                    "<p>Choose two activities from this week. For each one, name the situation, the visible communication action, and what the action improved. Do not enter private names, medical details, or personal disputes.</p>",
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
                )
                + step(
                    5,
                    "Submit once and store Entry 2",
                    "<p>Submit the Communication and Goal Synthesis in the Canvas or paper response home your teacher assigned. Keep it open for 2 to 3 minutes. In <strong>Entry 2</strong> of your CCE Six-Weeks Evidence Log, copy short phrases for: <strong>Communication and Goal Synthesis</strong>; your named communication skill; one visible action from a Week 5 example; your backup strategy as the revision or recovery move; and your evidence-based next action.</p><p>Return the log to your CCE binder or teacher-designated digital folder. Do not submit the log or the synthesis again. The log is not another grade.</p>",
                ),
                "DONE": "<ul><li>two skill suggestions or the fixed career pair recorded honestly;</li><li>revised goal, two Week 5 examples, and a two-career transfer comparison;</li><li>Entry 2 stored in the Evidence Log or five short phrases saved in an Entry 2 hold note.</li></ul>",
                "SUPPORT": "<p>action = acción; responsibility = responsabilidad; suggestion = sugerencia; transferable = transferible. Complete frames are beside Steps 2-4.</p>",
                "FALLBACK": "<p>Use the fixed IT support specialist and dental assistant pair when your teacher assigns it. If the Evidence Log is missing, save the same five short phrases from the open synthesis under <strong>Entry 2 hold</strong> in the CCE notebook or teacher-designated digital folder.</p>",
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
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and communication actions warm-up", '''<p>Welcome students to Week 5 and project the communication traits challenge.</p><ul><li>Ask students: <em>“We often say someone is a 'good communicator.' What does a good communicator actually DO that you can observe with your eyes and ears? Name ONE observable action, not just a vague personality trait like 'nice.'”</em></li><li>Collect 2-3 student suggestions. Guide students to translate vague words into concrete actions: replace 'nice' with <em>“lets the speaker finish without interrupting”</em>; replace 'smart' with <em>“asks clarifying questions when instructions are ambiguous.”</em></li><li>Bridge with, <em>“In any technical career, knowing how to do the job is only half the battle. Powerskills—especially communication and conflict resolution—keep projects moving forward.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-12 - Powerskills across diverse career clusters", '''<p>Open FYF pp. 12-14 and p. 139 (Transferable Skills) and display the Powerskills Transfer Guide.</p><ul><li>Have students examine two contrasting careers from prior weeks (e.g., Software Developer and Registered Nurse).</li><li>Ask: <em>“What is ONE Powerskill that both of these workers must demonstrate daily, even though their technical tools are completely different?”</em></li><li>Emphasize the core thesis: Technical skills execute tasks; Powerskills coordinate human collaboration, manage crises, and prevent costly errors.</li></ul>''')
                    + flow("#1f617a", "Minutes 12-17 - The Three Conflict Resolution Moves", '''<p>Project and explicitly model the Three Non-Negotiable Conflict Moves:</p><ul><li>1. <strong>Listen Actively:</strong> Ensure every person articulates their core need without interruption.</li><li>2. <strong>Compromise Fairly:</strong> Merge ideas, split duties, or trade responsibilities equitably rather than forcing an all-or-nothing vote.</li><li>3. <strong>Stay Respectful:</strong> Target the logistical problem, never the person's identity or character.</li><li>Model the 'Company Name' row on FYF p. 144: Demonstrate why <em>“we will just vote”</em> is an incomplete solution if minority concerns are ignored and resentment remains.</li></ul>''')
                    + flow("#e3ad19", "Minutes 17-37 - Smoothie-company team conflict resolution plan", '''<p>Organize students into small teams (3-4 students) with assigned operational roles: Reader, Recorder, Facilitator, and Designer.</p><ul><li>Teams collaborate in FYF pp. 144-145 to resolve three realistic business disputes: (1) Company Name, (2) Launch Date, and (3) Marketing Jobs.</li><li>Enforce the essential safety invariant: Compromise NEVER means compromising physical safety, sanitization protocols, or legal requirements. If a conflict involves a hazard, the protocol is always: protect safety, follow standard procedure, and notify the supervisor.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 24): Verify that every group articulates each member's underlying need rather than just writing 'we compromised.'<br>• Lap 2 (Minute 32): Check that groups have a concrete fallback plan if their primary compromise fails.</li></ul>''')
                    + flow("#1f617a", "Minutes 37-42 - Debrief: Workplace stakes across industries", '''<p>Lead a whole-class evaluative synthesis discussion.</p><ul><li>Ask: <em>“How do the consequences of an unresolved conflict escalate as you move from a student smoothie company to an emergency room triage desk or an active construction site?”</em></li><li>Highlight how communication failure in healthcare or industry leads to clinical errors or physical injury.</li></ul>''')
                    + flow("#1f617a", "Minutes 42-47 - Individual two-career transfer check DOL", '''<p>Students work independently to complete their private Transfer Check.</p><ul><li>Students select TWO careers, identify a realistic workplace conflict likely to emerge in each, describe the first safe communication move, and identify what communication principle remains identical across both settings.</li><li>Accept written responses, speech-to-text, or teacher-conference checks.</li></ul>''')
                    + flow("#606c76", "Minutes 47-50 - Submit evidence and reset materials", '''<p>Verify completion of FYF p. 145 and collect individual transfer checks.</p><ul><li><strong>Safe Trim:</strong> At minute 35, complete Name and Launch Date rows in writing; accept oral solutions for Marketing Jobs. Protect the individual transfer check and close.</li></ul>''')
                ),
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
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and information overload warm-up", '''<p>Welcome students and project the listening challenge prompt.</p><ul><li>Ask, <em>“When someone tells you an urgent story filled with frantic background details, emotional venting, and side comments, what specific listening strategy helps you extract the few facts that actually matter?”</em></li><li>Collect 2-3 student thoughts (e.g., jotting keywords, asking the speaker to pause, repeating back the main concern).</li><li>Bridge with, <em>“Active listening is a critical clinical and operational power skill. In high-stakes environments, missing one vital detail can cause disastrous mistakes.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-12 - Two-read protocol: Maria's triage account", '''<p>Display the written transcript of Maria's Triage Account (FYF p. 62).</p><ul><li><strong>First Read (Pencils Down):</strong> Read the complete patient narrative aloud while students listen for overall context and emotional tone.</li><li><strong>Second Read (Mark Evidence):</strong> Students annotate the text, underlining observable physical facts, timing markers, and medical history.</li><li>Emphasize the core clinical boundary: Students are listening to document raw facts, NOT to guess a medical diagnosis.</li></ul>''')
                    + flow("#1f617a", "Minutes 12-22 - Essential vs. background detail sorting audit", '''<p>Students independently complete the 4-row evidence table on FYF p. 63.</p><ul><li>Guide students to categorize each detail with a defensible rationale: (1) <strong>Essential:</strong> persistent chest tightness, onset at 7:00 AM, shortness of breath, radiating shoulder pain, hypertension medication history; (2) <strong>Background:</strong> holding a heavy briefcase, spilled coffee, stressful morning traffic, pending paperwork.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 17): Verify students justify WHY a detail is essential based on clinical relevance rather than personal interest.</li></ul>''')
                    + flow("#e3ad19", "Minutes 22-31 - Authoring clarifying questions and peer comparison", '''<p>Students craft TWO precise questions that request crucial missing information.</p><ul><li>Teach the question standard: Do not ask questions that repeat known facts. Ask questions that close open information gaps (e.g., <em>“Did you take your blood pressure medication this morning?”</em> or <em>“Has this radiating pain ever happened before?”</em>).</li><li>Pairs compare their sorted details and questions, explaining their rationale.</li></ul>''')
                    + flow("#1f617a", "Minutes 31-42 - Safe workplace listening simulation: Notice, Question, Next Step", '''<p>Direct students to the three fictional workplace communication cards (Supply Shortage, Scheduling Conflict, Broken Equipment).</p><ul><li>Students practice the 3-step active listening routine: (1) Paraphrase the speaker's core message; (2) Ask one clarifying question; (3) Propose a safe, appropriate routing step to an adult or supervisor.</li><li>Observer partners provide immediate structured feedback using the <strong>Notice + Question + Next Step</strong> protocol (avoiding the superficial 'compliment sandwich').</li></ul>''')
                    + flow("#1f617a", "Minutes 42-47 - Canvas Active Listening Evidence Check DOL", '''<p>Students open the retryable Canvas Active Listening Evidence Check.</p><ul><li>Assess understanding of essential vs. background facts, clarifying question design, role boundaries, and transfer across careers.</li><li>Students review automatic feedback and revise any missed concept.</li></ul>''')
                    + flow("#606c76", "Minutes 47-50 - Review feedback and workspace reset", '''<p>Confirm completion of the Canvas evidence check and close student devices.</p><ul><li><strong>Safe Trim:</strong> At minute 32, execute one structured listening card as a whole group rather than multiple peer rotations; fiercely protect the Canvas evidence check.</li></ul>''')
                ),
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
                "ALERT": "<strong>Self-advocacy is not self-rescue.</strong> If a situation is unsafe, threatening, harassing, or medically urgent, students stop the practice frame and get a trusted adult right away. SMART still requires scheduled work and a backup strategy.",
                "PREP": f"<ul><li><strong>Per student:</strong> 1 two-page {file_link(files['SMART']['id'], 'SMART/time plan')}, double-sided when available, and 1 pencil; or 1 device for the approved digital annotation route.</li><li><strong>Teacher:</strong> 1 display/device with FYF p. 134, the embedded fictional scenario bank, and {file_link(files['RUBRIC']['id'], 'student-visible weekly rubric')}. Select one scenario before class; do not project the complete private source deck.</li><li><strong>Source note:</strong> the scenario-first practice is curated from Jenna Hainlen's teacher-shared <em>Self-Advocacy Scenarios</em> deck. The CCE version keeps her short situation-and-response structure while removing adult disputes, unsafe disclosure prompts, and AVID-only machinery.</li><li><strong>Checkpoint:</strong> use end of next class or the teacher-posted Week 6 checkpoint; no extra calendar handout.</li><li><strong>Grouping:</strong> individual/private goal evidence; peer response optional.</li></ul>",
                "EVIDENCE": "<p>One brief formative Notice, Need, Reason, and Next step response inside the existing two-page artifact; then the durable SMART goal, two time blocks, obstacle, if-then backup, and two-career advocacy transfer. There is no new submission or separate grade.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and four-move self-advocacy warm-up", '''<p>Welcome students and project the self-advocacy challenge scenario.</p><ul><li>Introduce the Four-Move Self-Advocacy Routine:<br>1. <strong>Notice:</strong> Objectively state what happened or what is unclear.<br>2. <strong>Need:</strong> Explicitly state the exact accommodation, resource, or clarification required.<br>3. <strong>Reason:</strong> Give a shareable, task-focused rationale without oversharing private personal details.<br>4. <strong>Next Step:</strong> Propose a safe, constructive action or identify which trusted adult to consult.</li><li>Emphasize the vital safety boundary: Self-advocacy is NOT self-rescue. If a situation involves physical danger, bullying, harassment, or medical emergencies, students do NOT negotiate; they immediately alert a trusted adult.</li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-13 - Analyzing the community advocacy case (FYF p. 134)", '''<p>Read the community nutrition scenario on FYF p. 134.</p><ul><li>Students identify what the stakeholders notice and need, state a shareable reason regarding food access, and propose one realistic community health next step.</li><li>Emphasize: Use the scenario to analyze advocacy mechanisms; do not treat textbook numbers as current national statistics.</li></ul>''')
                    + flow("#1f617a", "Minutes 13-20 - Modeling a rigorous SMART goal with time buffers", '''<p>Dissect and model the difference between a vague wish and a rigorous SMART goal.</p><ul><li>Non-example: <em>“I want to get better at health careers.”</em></li><li>Worked Exemplar: <em>“By the Week 6 Friday checkpoint, I will complete comparison charts for three Health Science careers, identifying one daily duty and one degree requirement for each, so I can select my top CTE pathway.”</em></li><li>Demonstrate how to schedule two concrete 20-minute calendar blocks and formulate an <strong>If-Then Contingency Plan</strong> for anticipated obstacles.</li></ul>''')
                    + flow("#e3ad19", "Minutes 20-38 - Authoring the Advocacy, SMART Goal, and Time Plan", '''<p>Students work independently on their two-page Advocacy, SMART Goal, and Time Plan.</p><ul><li>Draft their personal career exploration goal meeting all five SMART criteria.</li><li>Schedule TWO dedicated time blocks during the upcoming week.</li><li>Identify ONE realistic obstacle (e.g., conflicting sports practice, Wi-Fi outage) and author an actionable If-Then backup plan that adjusts the operational schedule while protecting the final goal.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 26): Verify goals contain a measurable count/artifact and an exact deadline.<br>• Lap 2 (Minute 33): Check If-Then statements; ensure the backup modifies the strategy, not the goal itself.</li></ul>''')
                    + flow("#1f617a", "Minutes 38-45 - Rubric self-audit and two-career advocacy transfer DOL", '''<p>Students self-audit their goal against the 16-point rubric.</p><ul><li>Students complete the transfer prompt: Explain how professional self-advocacy operates in two distinct careers (e.g., an architectural drafter requesting updated engineering specs vs. a medical assistant reporting an unreadable physician order).</li></ul>''')
                    + flow("#606c76", "Minutes 45-50 - Submit plan and workspace reset", '''<p>Collect completed plans or verify digital submissions.</p><ul><li><strong>Safe Trim:</strong> At minute 35, transition directly to the self-audit and transfer check, skipping optional peer feedback. Protect the If-Then contingency plan and submission.</li></ul>''')
                ),
                "MONITOR": "<ul><li><strong>Scenario CFU:</strong> the response states what happened, asks for a specific support or route, gives a shareable reason, and proposes a safe next step. Do not require a student to explain private circumstances.</li><li><strong>Safety pivot:</strong> if the scenario involves danger, harassment, threats, medical urgency, or possible harm, the correct next step is a trusted adult or campus emergency route, not negotiation.</li><li><strong>Model CFU:</strong> identify action, measure, and deadline in the SMART example.</li><li><strong>Lap 1:</strong> check visible product/count and real checkpoint. If more than 1 in 4 uses “someday,” revise one deadline together.</li><li><strong>Lap 2:</strong> check that the backup changes route, not goal. Prompt “What different route still reaches the evidence?”</li><li><strong>Full durable evidence:</strong> five SMART parts, two time blocks, obstacle, controllable backup, two-career advocacy transfer. The four-move scenario response is formative inside the same artifact.</li><li><strong>Trim:</strong> use one scenario and private self-check instead of peer feedback. Do not cut backup, revision, transfer, or close.</li></ul>",
                "SUPPORT": "<p>Keep all four labels visible: <strong>“I notice ____. I need ____. The reason I can share is ____. A safe next step is ____.”</strong> Then place the goal frame beside the task: <strong>“By ____, I will ____ as shown by ____. I will work on it ____. If ____, then I will ____.”</strong> A written, oral, AAC, or teacher-conference response may use the same four moves. Goals remain private; a fictional goal may replace personal disclosure.</p>",
                "FALLBACK": "<p>No live platform or separate scenario deck is required. Speech-to-text, teacher conference, paper, and private digital annotation are equal. Use a fictional scenario in place of personal disclosure. Unsafe, threatening, harassing, or medically urgent situations go to a trusted adult or campus emergency route immediately.</p>",
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
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and vague message warm-up", '''<p>Welcome students and project the ambiguous workplace text.</p><ul><li>Project: <em>“Stuff is low. Someone should get more before it runs out.”</em></li><li>Ask students: <em>“If you received this message at work, what critical pieces of information are missing that prevent you from taking immediate action?”</em></li><li>Collect 2-3 responses: What exact item? What quantity? By what deadline? Who is 'someone'? Where does it go?</li><li>Bridge with, <em>“In the professional world, vague writing wastes hours and causes operational gridlock. Today you learn to write actionable messages that allow readers to act immediately.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-12 - The Four Workplace Writing Checks", '''<p>Review FYF pp. 147-148 and establish the Four Writing Standards:</p><ul><li>1. <strong>Write for the Reader:</strong> Anticipate what the recipient needs to know to accomplish the task.</li><li>2. <strong>Be Clear and Concise:</strong> Cut fluff; state key facts in simple, direct language.</li><li>3. <strong>Stay on Topic:</strong> Include only details relevant to the immediate operational action.</li><li>4. <strong>Proofread for Accuracy:</strong> Verify dates, quantities, names, and contact protocols before sending.</li></ul>''')
                    + flow("#1f617a", "Minutes 12-28 - Authoring the fictional Little Library community message", '''<p>Students draft a public-facing community update for a fictional Little Free Library.</p><ul><li>Students include: current book inventory status, specific genres needed, drop-off location, and an actionable invitation for neighborhood readers, plus two relevant hashtags.</li><li>Enforce data privacy: Never use real student home addresses, personal phone numbers, or social media handles.</li><li>Students posting to Canvas Discussion reply to ONE classmate using the <strong>Notice + Question + Next Step</strong> protocol. (Private paper route students complete the self-check).</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 18): Verify posts contain an explicit reader call-to-action.<br>• Lap 2 (Minute 24): Audit privacy compliance—zero real personal data.</li></ul>''')
                    + flow("#e3ad19", "Minutes 28-40 - Fixed-fact workplace message rewrite lab", '''<p>Direct students to the Workplace Message Companion.</p><ul><li>Students select ONE scenario: Supply Shortage, Patient Scheduling Delay, or Malfunctioning Diagnostic Equipment.</li><li>Constraint: <strong>Use ONLY the facts supplied in the brief.</strong> Never invent clinical diagnoses, legal policies, or unauthorized medical advice.</li><li>Draft the professional memo using the template: <em>“The [Equipment/Supply] is [Current Status]. Please [Specific Action] by [Deadline]. Direct questions to [Supervising Role].”</em></li></ul>''')
                    + flow("#1f617a", "Minutes 40-47 - Cross-career communication transfer DOL", '''<p>Students answer the Day 4 Transfer Prompt.</p><ul><li>Compare how the intended audience changes when writing as a Dental Receptionist (patient-facing) vs. an IT Help Desk Technician (internal employee-facing).</li><li>Identify ONE writing standard that remains non-negotiable in both professions.</li></ul>''')
                    + flow("#606c76", "Minutes 47-50 - Submit evidence and workspace reset", '''<p>Confirm discussion submissions or collect paper companion sheets.</p><ul><li><strong>Safe Trim:</strong> At minute 32, replace peer replies with individual self-audits to ensure all students complete the workplace rewrite and transfer check.</li></ul>''')
                ),
                "MONITOR": "<ul><li><strong>Warm-up CFU:</strong> identify missing status, audience, and requested action.</li><li><strong>Lap 1:</strong> check fictional status and reader action. If more than 1 in 4 posts includes identifying information, stop and reset the fictional-data rule.</li><li><strong>Lap 2:</strong> underline supplied workplace facts. Invented policy or medical guidance triggers revision from the facts only.</li><li><strong>Strong evidence:</strong> reader, exact status, requested action, safe routing, and one quality transferred across careers.</li><li><strong>Trim:</strong> use private self-check instead of peer reply. Do not cut workplace rewrite, transfer, or close.</li></ul>",
                "SUPPORT": "<p>Place this beside the rewrite: <strong>“The ____ is ____. Please ____ by ____. Questions should go to ____.”</strong> Offer typed, handwritten, audio, and speech-to-text drafts. Do not grade hashtags or mechanics unless meaning is unclear.</p>",
                "FALLBACK": "<p>Skip public posting for privacy, absence, or accommodation. FYF remains the Little Library surface; the one-page companion adds only the missing workplace rewrite and transfer evidence.</p>",
            },
            5: {
                "TITLE": "Connect Communication Skills to a Plan",
                "TOPIC": "Goals and Time",
                "OBJECTIVE": "Students will analyze Skills Matcher suggestions or fixed career evidence and revise a goal using transferable-skill evidence.",
                "TEKS": "d(4)(A), d(4)(B); d(1)(A) supporting evidence",
                "DOL": "Submitted Communication and Goal Synthesis scored with the 16-point rubric.",
                "SUBTITLE": "50 minutes · TEKS d(4)(A), d(4)(B); d(1)(A) supporting",
                "ALERT": "<strong>Fixed evidence is complete.</strong> CareerOneStop may generate suggestions, but the IT support specialist and dental assistant pair supports the same transfer analysis when the public tool is blocked or unfinished.",
                "PREP": f'<ul><li><strong>Per student:</strong> 1 internet-connected device with CareerOneStop and Canvas access.</li><li><strong>Teacher:</strong> 1 display for Skills Matcher checkpoints and the fixed two-career pair.</li><li><strong>Print only for assigned students:</strong> 1 two-page {file_link(files["SYNTH"]["id"], "synthesis")} per paper-response student, double-sided when available.</li><li><strong>Grouping:</strong> individual/private Minor evidence; optional partner talk shares only non-sensitive patterns.</li><li>Open the unpublished <a href="{minor_url}">Communication and Goal Synthesis</a> and {file_link(files["RUBRIC"]["id"], "student-visible rubric")}.</li><li>Remind students to retrieve the CCE Six-Weeks Evidence Log from the CCE binder or teacher-designated digital folder named in Week 0. It stays with the student.</li></ul>',
                "EVIDENCE": "<p>The four-part Canvas Minor includes a revised goal, time plan and backup, two Week 5 activity examples, two-career skill transfer, and one evidence-based next action. Entry 2 is a 2- to 3-minute transfer into the student-owned Evidence Log, not another Assignment, upload, or grade.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and communication responsibility warm-up", '''<p>Welcome students, seat them with their weekly work, and project the launch prompt.</p><ul><li>Ask, <em>“Think of ONE real responsibility you have managed—at school, at home, on an athletic team, in a church group, or in a club. What specific communication action did that responsibility require from you?”</em></li><li>Collect 2-3 student examples (e.g., explaining rules to younger siblings, coordinating group project roles, emailing a teacher about an absence).</li><li>Bridge with, <em>“Today we synthesize our Week 5 communication skills, evaluate our strengths using career data, and finalize our 16-point Major checkpoint.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-13 - Week 5 communication evidence sort", '''<p>Students review their completed artifacts from Days 1 to 4.</p><ul><li>Students select TWO specific learning activities that demonstrated a core communication skill (e.g., Day 1 Conflict Plan, Day 2 Maria Triage Sort, Day 3 SMART Goal, or Day 4 Workplace Rewrite).</li><li>For each activity, log: (1) The specific situation, (2) The concrete communication action taken, and (3) The observable outcome or improvement achieved.</li></ul>''')
                    + flow("#1f617a", "Minutes 13-33 - CareerOneStop Skills Matcher exploration", '''<p>Direct students to the online CareerOneStop Skills Matcher (or the fixed IT Support &amp; Dental Assistant reference pair).</p><ul><li>Students evaluate 40 skill and knowledge dimensions using the standard behavioral anchors.</li><li>Pause for structured progress checkpoints after Question 10, Question 20, and Question 30.</li><li>Students record two career suggestions generated by their responses and identify ONE surprising pattern in their skill cluster.</li><li>Emphasize: Skills Matcher results are reflective exploration tools, NOT permanent labels or career prescriptions.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Checkpoint 1 (Minute 18): Confirm all students have completed ratings 1-10.<br>• Checkpoint 2 (Minute 25): Checkpoint at rating 20.<br>• Checkpoint 3 (Minute 30): Checkpoint at rating 30.</li></ul>''')
                    + flow("#e3ad19", "Minutes 33-45 - Private synthesis and goal revision (Major Checkpoint)", '''<p>Students author their formal Communication and Goal Synthesis for the 16-point Major:</p><ul><li>1. <strong>Goal Revision:</strong> Refine their Day 3 SMART goal using insights from the Skills Matcher.</li><li>2. <strong>Time &amp; Contingency:</strong> Re-verify their protected time blocks and If-Then obstacle plan.</li><li>3. <strong>Evidence Integration:</strong> Integrate the two Week 5 activity examples demonstrating their communication growth.</li><li>4. <strong>Transfer Analysis:</strong> Compare how this communication skill functions across two distinct careers.</li><li>Self-audit against the 16-point rubric before final submission.</li></ul>''')
                    + flow("#24323d", "Minutes 45-48 - CCE Six-Weeks Evidence Log: Entry 2 capture", '''<p>Students open their CCE Six-Weeks Evidence Log (in their CCE binder or digital portfolio).</p><ul><li>Record the five required Entry 2 summary phrases:<br>• Artifact: <em>“Communication and Goal Synthesis”</em><br>• Core Skill: [Selected transferable communication skill]<br>• Observable Action: [Specific action from Week 5]<br>• Contingency Move: [If-Then backup plan]<br>• Next Action: [Evidence-based next step]</li><li>Return the log to its permanent storage folder (do NOT collect or grade separately).</li></ul>''')
                    + flow("#606c76", "Minutes 48-50 - Submit Major and close", '''<p>Verify private Canvas submission of the Synthesis assignment or collect paper packets.</p><ul><li><strong>Safe Trim:</strong> At minute 32, if Skills Matcher is incomplete, transition immediately to the supplied IT Support &amp; Dental Assistant reference cards; protect the 16-point synthesis, rubric revision, and Evidence Log Entry 2.</li></ul>''')
                ),
                "MONITOR": "<ul><li><strong>Minute 12 CFU:</strong> two Week 5 examples name a visible communication action.</li><li><strong>Matcher checkpoints:</strong> after ratings 10, 20, and 30, verify progress and read anchors aloud if students click without reading.</li><li><strong>Synthesis lap:</strong> check revised goal, protected time, backup, two Week 5 activity examples, and one communication action across two careers. Prompt “What does the worker do with the skill?”</li><li><strong>Submit/check:</strong> verify five short Entry 2 phrases copied from the open synthesis: artifact, skill, visible action, backup as recovery, and next action. The log returns to the named CCE storage place and is not collected.</li><li><strong>Boundary:</strong> results are idea-generators from self-ratings, not identity or verdict. Use multiple sources and counselor discussion for decisions.</li><li><strong>Trim:</strong> at minute 32, stop after the current chunk and use the fixed IT support specialist and dental assistant pair in the Student Guide. Record Matcher incomplete; protect synthesis and submit.</li></ul>",
                "SUPPORT": "<p>Place these beside the response: <strong>“I used ____ when I ____.” “The suggestions share ____ because I rated ____ as important.” “In ____, the worker uses ____ when ____.”</strong> Read anchors aloud in chunks. Private writing, audio, and teacher conference are equal.</p>",
                "FALLBACK": "<p>If CareerOneStop is blocked or incomplete, use the fixed IT support specialist and dental assistant pair supplied in the Student Guide and paper route. Do not pretend the assessment was completed. If the Evidence Log is missing, students copy the same five short phrases from the open synthesis under <strong>Entry 2 hold</strong> in the CCE notebook or teacher-designated digital folder, then transfer them later. Do not reconstruct or upload old work.</p>",
            },
        }
        titles = {
            1: "STUDENT: 2SW Wk5 Day 1 - Conflict Resolution",
            2: "STUDENT: 2SW Wk5 Day 2 - Active Listening",
            3: "STUDENT: 2SW Wk5 Day 3 - Advocacy and SMART Time Plan",
            4: "STUDENT: 2SW Wk5 Day 4 - Written Message Lab",
            5: "STUDENT: 2SW Wk5 Day 5 - Communication Skills and Goal Synthesis",
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
