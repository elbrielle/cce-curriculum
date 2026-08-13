"""Build the unpublished 3SW Week 3 Sustainable Engineering Canvas module."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
import httpx

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
MODULE_NAME = "3SW Wk3: Sustainable Engineering and Pest Patrol"
CAREER_TITLE = "PRACTICE: Sustainable Career Match"
DRAFT_TITLE = "PRACTICE: Pest Patrol Drone Draft"
PACKET_TITLE = "MAJOR 2: Sustainable Engineering Design and Trends Evidence"
GOALS_TITLE = "PRACTICE: Xello Set Goals Reflection"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/3sw/wk3"
WORKSHEET_FILES = {
    "CAREERS": "3sw-wk3-sustainable-career-problem-guide.pdf",
    "FIELD": "3sw-wk3-pest-patrol-field-notes.pdf",
    "DESIGN": "3sw-wk3-drone-design-brief.pdf",
    "REVIEW": "3sw-wk3-peer-review-revision.pdf",
    "TRENDS": "3sw-wk3-societal-trends-evidence.pdf",
    "EVAL": "3sw-wk3-societal-trends-evaluation.pdf",
    "RUBRIC": "3sw-wk3-sustainable-engineering-major-rubric.pdf",
    "GOALS": "3sw-wk3-xello-goals-plan.pdf",
}
VISUAL_FILES = {
    2: (
        "fyf-pest-patrol-field-notes-1.jpg",
        "fyf-pest-patrol-field-notes-2.jpg",
    ),
    3: ("fyf-pest-patrol-design-review.png",),
    4: ("fyf-pest-patrol-design-review.png",),
    5: ("fyf-adaptability-goal-bridge.png",),
}
XELLO_GUIDE = ROOT / "cce-curriculum/resources/xello-licensed/prerequisites/goals.pdf"


def preflight():
    required = [
        TEMPLATES / "3sw-wk3-student.html",
        TEMPLATES / "3sw-wk3-teacher.html",
        *(
            ROOT / "docs/resources/worksheets" / name
            for name in WORKSHEET_FILES.values()
        ),
        XELLO_GUIDE,
        *(
            ASSETS / f"day{day}" / name
            for day, names in VISUAL_FILES.items()
            for name in names
        ),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"3SW Wk3 preflight missing required files: {missing}")


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


async def lock_folder_files(client, folder, required_names=()):
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
    current = await api(client, "GET", f"/folders/{folder['id']}")
    final = await paged(client, f"/folders/{folder['id']}/files")
    names = {
        entry.get("display_name") or entry.get("filename") for entry in final
    }
    missing = set(required_names) - names
    unlocked = [
        entry.get("display_name") or entry.get("filename")
        for entry in final
        if not entry.get("locked")
    ]
    if current.get("locked") is not True or missing or unlocked:
        raise RuntimeError(
            f"3SW Wk3 folder invariant failed for {folder['id']}: "
            f"missing={sorted(missing)} unlocked={unlocked}"
        )
    return current, final


def preferred_images(folder):
    candidates = sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg"}
    )
    jpeg_stems = {
        path.stem.lower()
        for path in candidates
        if path.suffix.lower() in {".jpg", ".jpeg"}
    }
    return [
        path
        for path in candidates
        if path.suffix.lower() != ".png" or path.stem.lower() not in jpeg_stems
    ]


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


async def require_major_preflight(client):
    groups = await paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group_matches = [
        entry for entry in groups if entry.get("name") == "Major Assessments (60%)"
    ]
    if len(group_matches) != 1:
        raise RuntimeError(
            "Expected exactly one assignment group named 'Major Assessments (60%)'; "
            f"found {len(group_matches)}"
        )
    group = group_matches[0]
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [
        assignment
        for assignment in assignments
        if assignment.get("name") == PACKET_TITLE
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one existing mapped Major assignment named {PACKET_TITLE!r}; found {len(matches)}"
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
            f"Mapped Major invariant failed before module writes: "
            f"published={found.get('published')}, points={found.get('points_possible')}, "
            f"group={found.get('assignment_group_id')}, grading={found.get('grading_type')}, "
            f"omit={found.get('omit_from_final_grade')}"
        )
    return found, group


async def update_major_assignment(client, found, group):
    description = "<p>Submit the final Pest Patrol design, the revision record, and the Sustainable Engineering Trends Evaluation. Paper, Canva, Adobe Express, or another approved route is equal. Drawing polish and platform access do not earn extra points.</p>"
    rubric_note = re.search(
        r'<div data-cce-rubric-note="[^"]+".*?</div>',
        found.get("description") or "",
        flags=re.I | re.S,
    )
    if rubric_note:
        description += rubric_note.group(0)
    data = {
        "assignment[description]": description,
        "assignment[submission_types][]": [
            "online_upload",
            "online_text_entry",
            "media_recording",
        ],
        "assignment[published]": "false",
    }
    packet = await api(
        client, "PUT", f"/courses/{COURSE_ID}/assignments/{found['id']}", data=data
    )
    if (
        packet.get("published")
        or float(packet.get("points_possible") or 0) != 100
        or packet.get("assignment_group_id") != group["id"]
        or packet.get("grading_type") != "points"
        or packet.get("omit_from_final_grade") is not False
    ):
        raise RuntimeError(
            f"Major invariant failed after update: published={packet.get('published')}, "
            f"points={packet.get('points_possible')}, group={packet.get('assignment_group_id')}, "
            f"grading={packet.get('grading_type')}, omit={packet.get('omit_from_final_grade')}"
        )
    return packet


async def upsert_practice_assignment(
    client, title, description, submission_types, peer_reviews=False
):
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [
        assignment for assignment in assignments if assignment.get("name") == title
    ]
    if len(matches) > 1:
        raise RuntimeError(
            f"Expected at most one assignment named {title!r}; found {len(matches)}"
        )
    found = matches[0] if matches else None
    data = {
        "assignment[name]": title,
        "assignment[description]": description,
        "assignment[submission_types][]": submission_types,
        "assignment[grading_type]": "not_graded",
        "assignment[points_possible]": "0",
        "assignment[omit_from_final_grade]": "true",
        "assignment[published]": "false",
        "assignment[peer_reviews]": "true" if peer_reviews else "false",
        "assignment[automatic_peer_reviews]": "false",
    }
    assignment = await api(
        client,
        "PUT" if found else "POST",
        (
            f"/courses/{COURSE_ID}/assignments/{found['id']}"
            if found
            else f"/courses/{COURSE_ID}/assignments"
        ),
        data=data,
    )
    if (
        assignment.get("published")
        or float(assignment.get("points_possible") or 0) != 0
        or assignment.get("grading_type") != "not_graded"
        or not assignment.get("omit_from_final_grade")
        or bool(assignment.get("peer_reviews")) != peer_reviews
        or bool(assignment.get("automatic_peer_reviews"))
        or not set(submission_types).issubset(
            set(assignment.get("submission_types") or [])
        )
    ):
        raise RuntimeError(
            f"Practice invariant failed for {title!r}: published={assignment.get('published')}, "
            f"points={assignment.get('points_possible')}, grading={assignment.get('grading_type')}, "
            f"omit={assignment.get('omit_from_final_grade')}, peer={assignment.get('peer_reviews')}, "
            f"automatic_peer={assignment.get('automatic_peer_reviews')}, "
            f"submissions={assignment.get('submission_types')}"
        )
    return assignment


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
                or (kind == "Assignment" and item.get("content_id") == key)
            )
        ),
        None,
    )
    if found:
        return await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{found['id']}",
            data={"module_item[title]": title},
        )
    data = {"module_item[type]": kind, "module_item[title]": title}
    if kind == "Page":
        data["module_item[page_url]"] = key
    elif kind == "Assignment":
        data["module_item[content_id]"] = key
    return await api(
        client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data=data
    )


def file_link(file_id, label):
    return f'<a href="/courses/{COURSE_ID}/files/{file_id}/preview" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">{label}</a>'


def image_tag(file_id, alt, max_width=700):
    return f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" style="display:block;width:100%;max-width:{max_width}px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'


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
        packet, major_group = await require_major_preflight(client)
        module = await ensure_module(client)
        career = await upsert_practice_assignment(
            client,
            CAREER_TITLE,
            '<div style="max-width:820px;margin:0 auto;font-family:Arial,Helvetica,sans-serif;line-height:1.5;color:#24323d"><h2 style="color:#5a2d91">Sustainable Career Match</h2><p><strong>Submit one individual response:</strong></p><ol><li>Name the lead career.</li><li>Name one task that matches the crop-and-water problem.</li><li>Name a weaker lead and explain why it is weaker for this problem.</li><li>Use one current fact from the fixed guide. Keep the measure and date attached to any number.</li></ol><p><strong>Complete frame:</strong> “The ____ should lead because this worker ____. A weaker lead is ____ because ____. One current fact is ____.”</p><p>You may type the response or upload the completed guide. Do not submit an H&amp;L profile screenshot.</p></div>',
            ["online_text_entry", "online_upload"],
        )
        draft = await upsert_practice_assignment(
            client,
            DRAFT_TITLE,
            "<p>Submit the Pest Patrol draft or retain the labeled paper original for review. Evidence includes six labeled features, three field-report links, one evidence-to-feature-to-benefit chain, one tradeoff, and the career role, work product, and user. A file, image, text explanation, or media recording may document the same criteria. Paper is equal. Peer review is available only after the teacher manually assigns reviewers.</p>",
            ["online_upload", "online_text_entry", "media_recording"],
            peer_reviews=True,
        )
        packet = await update_major_assignment(client, packet, major_group)
        goals = await upsert_practice_assignment(
            client,
            GOALS_TITLE,
            "<p>Submit the private Goal Check as text or an uploaded PDF. Name the timeframe and next task for each of two goals, one obstacle that could affect either goal, one backup plan, and which goal may need revision after its first task. Do not copy full private goal statements or post profile screenshots.</p>",
            ["online_text_entry", "online_upload"],
        )

        support = "course files/CCR Materials/3SW/Wk3"
        support_folder = await ensure_folder(client, support)
        names = WORKSHEET_FILES
        files = {
            key: await upload(
                client, ROOT / "docs/resources/worksheets" / name, support
            )
            for key, name in names.items()
        }
        files["XELLO"] = await upload(
            client,
            XELLO_GUIDE,
            support,
        )

        folders, visuals, visual_required = {}, {}, {}
        for day in range(1, 6):
            path = f"course files/CCR Materials/3SW/Wk3/Day {day} Visuals"
            folders[day], visuals[day] = await ensure_folder(client, path), {}
            source = ASSETS / f"day{day}"
            day_images = preferred_images(source) if source.exists() else []
            visual_required[day] = tuple(image.name for image in day_images)
            for image in day_images:
                visuals[day][image.name] = await upload(client, image, path)

        support_folder, support_folder_files = await lock_folder_files(
            client,
            support_folder,
            (*WORKSHEET_FILES.values(), XELLO_GUIDE.name),
        )
        folder_files = {}
        for day in range(1, 6):
            folders[day], folder_files[day] = await lock_folder_files(
                client, folders[day], visual_required[day]
            )

        career_url = f"/courses/{COURSE_ID}/assignments/{career['id']}"
        draft_url = f"/courses/{COURSE_ID}/assignments/{draft['id']}"
        packet_url = f"/courses/{COURSE_ID}/assignments/{packet['id']}"
        goals_url = f"/courses/{COURSE_ID}/assignments/{goals['id']}"
        field_media = image_tag(
            visuals[2]["fyf-pest-patrol-field-notes-1.jpg"]["id"],
            "Find Your Future Pest Patrol agricultural engineer field notes",
        ) + image_tag(
            visuals[2]["fyf-pest-patrol-field-notes-2.jpg"]["id"],
            "Find Your Future Pest Patrol farmer and plant scientist field notes",
        )
        design_media = image_tag(
            visuals[3]["fyf-pest-patrol-design-review.png"]["id"],
            "Find Your Future Pest Patrol drone design and peer review directions",
        )
        review_media = image_tag(
            visuals[4]["fyf-pest-patrol-design-review.png"]["id"],
            "Find Your Future Pest Patrol design and peer review page",
        )
        goal_media = image_tag(
            visuals[5]["fyf-adaptability-goal-bridge.png"]["id"],
            "Find Your Future Adaptability scenario used as a goal-planning bridge",
        )

        contracts = {
            1: {
                "TOPIC": "Career Opportunities",
                "OBJECTIVE": "Students will match one sustainable-engineering career to a crop-and-water problem using current evidence.",
                "TEKS": "d(1)(C)",
                "DOL": "Individual response naming a lead career, matching task, weaker comparison, and one current fact from the fixed guide.",
                "STUDENT_OBJECTIVE": "match one sustainable-engineering career to a crop-and-water problem using current evidence.",
                "STUDENT_DOL": "I will name a lead career, matching task, weaker comparison, and one current fact from the fixed guide.",
            },
            2: {
                "TOPIC": "Career Opportunities",
                "OBJECTIVE": "Students will identify how an agricultural engineer uses worker reports to create testable design constraints.",
                "TEKS": "d(1)(C)",
                "DOL": "Pest Patrol Field Notes and Constraints with an agricultural-engineer work-product connection.",
                "STUDENT_OBJECTIVE": "explain how an agricultural engineer turns worker reports into design constraints.",
                "STUDENT_DOL": "I will complete the field notes, constraints, and agricultural-engineer work-product connection.",
            },
            3: {
                "TOPIC": "Career Opportunities",
                "OBJECTIVE": "Students will identify an agricultural-engineering career opportunity by creating a labeled drone design brief from field evidence.",
                "TEKS": "d(1)(C)",
                "DOL": "Pest Patrol Drone Design Brief draft with a named career, work product, and user.",
                "STUDENT_OBJECTIVE": "show what an agricultural-engineering worker produces by building a drone design brief from field evidence.",
                "STUDENT_DOL": "I will submit a labeled drone design brief that names the career role, work product, and user.",
            },
            4: {
                "TOPIC": "Emerging Careers",
                "OBJECTIVE": "Students will evaluate how two societal trends change sustainable-engineering careers and work tasks using current evidence.",
                "TEKS": "d(1)(D), d(5)(C)",
                "DOL": "One visible Pest Patrol revision plus a two-trend evaluation using two sourced facts and one evidence limit.",
                "STUDENT_OBJECTIVE": "evaluate how two trends change sustainable-engineering careers and work tasks using current evidence.",
                "STUDENT_DOL": "I will show one visible design revision and evaluate two trends using two facts and one evidence limit.",
            },
            5: {
                "TOPIC": "Goal Setting",
                "OBJECTIVE": "Students will demonstrate goal-setting strategies by saving two goals with a timeframe, next task, obstacle, and backup plan.",
                "TEKS": "d(4)(A)",
                "DOL": "Two saved Xello goals + private Goal Check and Reflection.",
                "STUDENT_OBJECTIVE": "build two goals that include a timeframe, next task, obstacle, and backup plan.",
                "STUDENT_DOL": "I will save two goals in Xello and complete the private Goal Check and Reflection.",
            },
        }

        student = {
            1: {
                "TITLE": "Match Careers to a Resource Problem",
                "PURPOSE": "Use current career evidence to choose who should lead a crop-and-water problem.",
                "TODAY": "<ul><li>compare four careers;</li><li>choose a lead career for a drought problem;</li><li>state what the evidence does not prove.</li></ul>",
                "READY": f'<p>Open {file_link(files["CAREERS"]["id"], "the two-page Career and Problem Guide")}.</p>',
                "MEDIA": "",
                "STEPS": step(
                    1,
                    "Read the work, not only the pay",
                    "<p>Compare tasks, preparation, May 2024 U.S. median pay, growth, and annual openings.</p>",
                )
                + step(
                    2,
                    "Read the crop-and-water brief",
                    "<p>NASA and USDA evidence describe drought, soil moisture, drone uses, and real technology limits.</p>",
                )
                + step(
                    3,
                    "Choose and defend",
                    f'<p>Name one matching task, one weaker lead, and one current fact. Use: “The ____ should lead because this worker ____. A weaker lead is ____ because ____. One current fact is ____.” Then <a href="{career_url}">open the private Sustainable Career Match</a> to type the response or upload the completed guide.</p>',
                )
                + step(
                    4,
                    "Check the boundary",
                    "<p>Do not relabel a national median as DFW starting pay or treat a projection as a promise.</p>",
                ),
                "EXIT": "<p>Which matters more for this problem: career growth or the worker's actual task? Use one fact.</p>",
                "DONE": "<ul><li>lead career selected;</li><li>task-to-problem link;</li><li>comparison to another career;</li><li>source/date/measure kept accurate;</li><li>private response submitted or paper guide collected.</li></ul>",
                "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> task, preparation, median, projection, evidence limit.</p>",
                "SUPPORT": "<p>task = tarea · preparation = preparación · median = mediana · projection = proyección. Frame: “I chose ____ because this worker ____.”</p>",
                "FALLBACK": "<p>The PDF is the full route. H&amp;L is optional and no live search is required.</p>",
            },
            2: {
                "TITLE": "Turn Field Reports into Constraints",
                "PURPOSE": "See how an agricultural engineer turns three worker viewpoints into design rules.",
                "TODAY": "<ul><li>record useful facts from three reports;</li><li>write three testable constraints;</li><li>rank the most important constraint.</li></ul>",
                "READY": f'<p>Open {file_link(files["FIELD"]["id"], "Pest Patrol Field Notes and Constraints")}.</p>',
                "MEDIA": field_media,
                "STEPS": step(
                    1,
                    "Read one source at a time",
                    "<p>Agricultural Engineer, Farmer, then Plant Scientist. Finish each section before moving on.</p>",
                )
                + step(
                    2,
                    "Write what the drone must do",
                    '<p>Turn facts into functions, not decorations. Example: “The engineer report says the field is windy, so the drone must stay steady in 15-20 mph wind.”</p>',
                )
                + step(
                    3,
                    "Build three constraints",
                    "<p>Detection, movement/coverage, and one practical limit.</p>",
                )
                + step(
                    4,
                    "Rank and explain",
                    '<p>Choose the most important constraint and point to the source that supports it. Use: “____ comes first because the ____ report shows ____.”</p>',
                ),
                "EXIT": "<p>If the team could meet only two constraints, which one could wait and what risk would that create?</p>",
                "DONE": "<ul><li>all three reports recorded;</li><li>three testable constraints;</li><li>agricultural-engineer work product named;</li><li>one ranked decision.</li></ul>",
                "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> detect, map, report, withstand, cover, protect, constraint.</p>",
                "SUPPORT": "<p>detect = detectar · cover = cubrir · withstand = resistir · constraint = restricción.</p>",
                "FALLBACK": "<p>The embedded pages and packet are the complete absence route. No platform login is needed.</p>",
            },
            3: {
                "TITLE": "Design the Pest Patrol Drone",
                "PURPOSE": "Create the kind of evidence-based design brief an agricultural-engineering worker could use.",
                "TODAY": "<ul><li>label six or more features;</li><li>connect three labels to field evidence;</li><li>explain one tradeoff.</li></ul>",
                "READY": f'<p>Open {file_link(files["DESIGN"]["id"], "the two-page Drone Design Brief")} and {file_link(files["RUBRIC"]["id"], "the 16-point rubric")}.</p>',
                "MEDIA": design_media,
                "STEPS": step(
                    1,
                    "Keep the evidence visible",
                    '<p>Use the Day 2 constraints without copying them again. Example chain: “The farmer cannot walk every row, so the drone includes a mapping route. This helps the farmer find problem areas faster.”</p>',
                )
                + step(
                    2,
                    "Choose an equal build route",
                    "<p>Paper, Canva for Education, Adobe Express, or another approved route. Art polish does not earn extra points.</p>",
                )
                + step(
                    3,
                    "Draw and label",
                    "<p>Use the full-page canvas. Show sensing, movement, farmer reporting, safety/crop protection, and two more functions.</p>",
                )
                + step(
                    4,
                    "Explain and submit",
                    f'<p>Complete the evidence chain and tradeoff, then <a href="{draft_url}">open the Pest Patrol Drone Draft assignment</a>. Paper is equal.</p>',
                ),
                "EXIT": "<p>Which feature has the strongest field-report evidence, and which source supports it?</p>",
                "DONE": "<ul><li>six labeled features;</li><li>three evidence links;</li><li>career role, work product, and user named;</li><li>benefit and limit stated;</li><li>draft submitted digitally or on paper.</li></ul>",
                "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> feature, label, evidence, benefit, tradeoff, user.</p><p><strong>Use for your own chain:</strong> “The report says ____. My design includes ____. This helps ____ because ____.”</p>",
                "SUPPORT": "<p>feature = característica · label = etiqueta · evidence = evidencia · tradeoff = compensación. A basic outline is available without lowering the criteria.</p>",
                "FALLBACK": "<p>No drone hardware is required. If Canvas fails, keep the paper original or saved file for Day 4 review.</p>",
            },
            4: {
                "TITLE": "Review, Revise, and Evaluate Trends",
                "PURPOSE": "Use specific feedback, make one visible revision, and evaluate two changing-work trends.",
                "TODAY": "<ul><li>review one drone design;</li><li>make and explain one revision;</li><li>compare two societal trends with sourced evidence.</li></ul>",
                "READY": f'<p>Open {file_link(files["REVIEW"]["id"], "the Peer Review and Revision Record")}, {file_link(files["TRENDS"]["id"], "the Trends Evidence Guide")}, and {file_link(files["EVAL"]["id"], "the Trends Evaluation")}.</p>',
                "MEDIA": review_media,
                "STEPS": step(
                    1,
                    "Review privately",
                    '<p>Use the FYF p. 95 review or a teacher-assigned Canvas peer review. Give one specific next step: “Label what the camera detects so the farmer knows why it is useful.” Then record the revision decision on the one-page sheet.</p>',
                )
                + step(
                    2,
                    "Revise on purpose",
                    "<p>Show the exact change and explain why it improves evidence, function, clarity, or safety.</p>",
                )
                + step(
                    3,
                    "Read three fixed trends",
                    "<p>Precision agriculture, wind/solar installation work, and technology in the water workforce.</p>",
                )
                + step(
                    4,
                    "Compare and recommend",
                    f'<p>Write 3-4 complete sentences using two facts and one evidence limit. Use: “The ____ trend changes ____ work by ____. The evidence shows ____, but it does not prove ____.” When complete, <a href="{packet_url}">open the Sustainable Engineering Evidence Packet assignment</a>.</p>',
                ),
                "EXIT": "<p>Which trend changes more daily work? Use one fact and one limit.</p>",
                "DONE": "<ul><li>specific peer or self-review;</li><li>one visible revision;</li><li>two trends compared;</li><li>two facts and one limit;</li><li>packet submitted when complete.</li></ul>",
                "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> trend, revision, projection, daily task, evidence limit.</p>",
                "SUPPORT": "<p>trend = tendencia · revision = revisión · projection = proyección · limit = límite. A self-review or teacher conference replaces a missing reviewer.</p>",
                "FALLBACK": "<p>Paper review is equal. The fixed evidence guide replaces open searching. Late work does not depend on automatic peer assignment.</p>",
            },
            5: {
                "TITLE": "Set Two Goals in Xello",
                "PURPOSE": "Plan two honest goals, save them in Xello, and name a next task and backup.",
                "TODAY": "<ul><li>use an adaptability example;</li><li>save at least two Xello goals;</li><li>complete a private reflection.</li></ul>",
                "READY": f'<p>Open {file_link(files["GOALS"]["id"], "the Goal Check and Private Reflection")}. Keep personal details private.</p>',
                "MEDIA": goal_media,
                "STEPS": step(
                    1,
                    "Draft two goals",
                    '<p>Give each goal a timeframe, one task, and an obstacle with a backup plan. Fictional model: “By October 1, I will finish one career-interview question list. If I cannot meet the worker, I will use a teacher-approved career profile.”</p>',
                )
                + step(
                    2,
                    "Save in Xello",
                    "<p>ClassLink &gt; Xello &gt; About Me &gt; Goals &gt; Set a goal. Save at least two goals.</p>",
                )
                + step(
                    3,
                    "Check the plan",
                    "<p>Confirm both goals appear. Your teacher uses the Completion Standards report; do not submit a profile screenshot.</p>",
                )
                + step(
                    4,
                    "Reflect privately",
                    f'<p>Finish the reflection, then <a href="{goals_url}">open the private Xello Set Goals Reflection assignment</a>.</p>',
                ),
                "EXIT": "<p>Which goal has the clearest next task, and which may need revision after the first attempt?</p>",
                "DONE": "<ul><li>two goals saved in Xello;</li><li>timeframe and task for each;</li><li>private reflection complete;</li><li>catch-up recorded if Xello failed.</li></ul>",
                "VISIBLE_SUPPORT": "<p><strong>Word bank:</strong> goal, timeframe, next task, obstacle, backup plan.</p><p><strong>Use this frame:</strong> “If ____ gets in the way, I will ____ so I can keep moving toward ____.”</p>",
                "SUPPORT": "<p>goal = meta · timeframe = plazo · task = tarea · obstacle = obstáculo · backup = alternativa.</p>",
                "FALLBACK": "<p>Submit the paper plan and schedule supervised Xello catch-up. Paper planning does not replace the required save.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Match Careers to a Resource Problem",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>Fixed evidence is the core.</strong> Do not depend on exact H&amp;L Hat titles or open salary searches.",
                "PREP": f'<ul><li><strong>Default digital route:</strong> post {file_link(files["CAREERS"]["id"], "the two-page career/problem guide")} and open the unpublished private <strong>{CAREER_TITLE}</strong> assignment. Default print count is 0.</li><li><strong>No-device route:</strong> print one guide per student, double-sided. Collect the completed guide rather than requiring a second Canvas copy.</li><li><strong>Devices and grouping:</strong> one device per student or pair for reading; the response is individual. Pairs are used only for the comparison.</li><li>Project the supplied model below. H&amp;L remains optional enrichment.</li></ul>',
                "EVIDENCE": "<p><strong>Private Canvas text/upload or collected paper guide:</strong> one lead career, one matching task, one weaker comparison, and one current fact. This is formative and grade neutral.</p>",
                "MODEL": "<p><strong>Supplied model:</strong> Agricultural Engineer should lead because this worker designs farm systems and monitoring equipment. Wind Turbine Technician is a weaker lead because turbine repair does not address crop monitoring. One current fact is that agricultural engineers typically need a bachelor's degree. The model uses no salary figure, so no pay measure is required.</p>",
                "FLOW": flow(
                    "#5a2d91",
                    "Resource warm-up · 5",
                    "Water, food, energy, or clean air.",
                )
                + flow(
                    "#4a9d2f",
                    "Career evidence · 8",
                    "Task, preparation, pay measure, growth, openings.",
                )
                + flow(
                    "#1f617a",
                    "Drought problem brief · 20",
                    "Choose and defend a lead career.",
                )
                + flow(
                    "#e3ad19", "Compare and revise · 10", "State an evidence boundary."
                )
                + flow("#1f617a", "Submit and reset · 7", "Individual response, exit check, materials."),
                "MONITOR": "<p><strong>District response move:</strong> Stop and Jot the resource problem for 60 seconds, then use Think-Pair-Share for the weaker-lead comparison.</p><p><strong>Lap 1, minute 13:</strong> check that each student selected a worker task before looking at pay. Feedback: underline the task that fits the crop-and-water brief. If several students choose only by salary or growth, pause and compare one task row to one data row.</p><p><strong>Lap 2, minute 33:</strong> check for a lead, matching task, weaker comparison, and current fact. Agricultural Engineer is the most direct lead when the reason names farm systems, irrigation, equipment, or monitoring. Environmental Engineer can earn credit with a clear water-system argument. Correct every DFW-starting-pay relabel.</p><p><strong>Safe trim:</strong> cut the partner share and move directly to individual revision. Protect the four-part response and submission/reset window.</p>",
                "RESOURCES": '<p><a href="https://www.bls.gov/ooh/architecture-and-engineering/environmental-engineers.htm">BLS Environmental Engineers</a> · <a href="https://www.bls.gov/ooh/architecture-and-engineering/agricultural-engineers.htm">BLS Agricultural Engineers</a> · <a href="https://www.bls.gov/ooh/installation-maintenance-and-repair/wind-turbine-technicians.htm">BLS Wind Technicians</a> · <a href="https://www.bls.gov/ooh/construction-and-extraction/solar-photovoltaic-installers.htm">BLS Solar Installers</a> · <a href="https://climatekids.nasa.gov/soil/">NASA drought and soil moisture</a></p>',
                "SUPPORT": "<p>Highlight the task column, narrow the first choice to Agricultural Engineer or Environmental Engineer, and allow oral rehearsal with the complete frame beside Step 3. Score evidence, not English mechanics, unless meaning is unclear.</p>",
                "FALLBACK": "<p>The fixed PDF and paper guide are the complete no-search route. If Canvas fails, collect the guide and do not require students to retype it later. No personal profile or screenshot is needed.</p>",
            },
            2: {
                "TITLE": "Turn Field Reports into Constraints",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>Read one source at a time.</strong> The workbook pages are dense, so close each chunk before opening the next.",
                "PREP": f'<ul><li><strong>Per student:</strong> FYF workbook pp. 93-94, one {file_link(files["FIELD"]["id"], "two-page field-notes sheet")} printed double-sided, one pencil, and one highlighter. This is one required sheet per student.</li><li><strong>Devices:</strong> none required when students have their workbook. Use one display device only for the supplied model and embedded absence images.</li><li><strong>Grouping:</strong> individual recording; pairs of two for a 60-second source check after each report.</li></ul>',
                "EVIDENCE": "<p><strong>Collected or teacher-checked field-notes sheet:</strong> useful facts from all three reports, three constraints, the agricultural-engineer work product, and one ranked decision. Formative; no second Canvas copy.</p>",
                "MODEL": '<p><strong>Supplied fact-to-function model:</strong> “The engineer report says the site has 15-20 mph wind, so the drone must stay steady enough to collect usable images in that wind.” This is testable and tied to a source. “Add strong wings” is not enough because it does not state the required function.</p>',
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Questions before drawing.")
                + flow(
                    "#4a9d2f",
                    "Source preview · 7",
                    "Engineer, Farmer, Plant Scientist.",
                )
                + flow(
                    "#1f617a", "Read and record · 23", "One closed chunk per source."
                )
                + flow(
                    "#e3ad19",
                    "Build constraints · 10",
                    "Detection, coverage, practical limit.",
                )
                + flow("#1f617a", "Exit · 5", "Rank and defend."),
                "MONITOR": "<p><strong>District response move:</strong> use Chunking with a 60-second Turn and Talk after each report: Partner A names one fact; Partner B turns it into a drone function.</p><p><strong>Lap 1, minute 17:</strong> check the engineer and farmer rows for accurate facts and one function. Feedback: point to the exact report line before writing “the drone must.” If several students copy whole paragraphs, model selecting only the fact that changes the design.</p><p><strong>Lap 2, minute 35:</strong> check that all three constraints are testable and each has evidence or reasoning. Cost, battery, weather, safety, accuracy, and farmer time are acceptable practical limits when explained. If several constraints are part names, pause and revise one into a function.</p><p><strong>Safe trim:</strong> cut the partner reports and extension test. Protect all three source rows, three constraints, the career work-product connection, and the ranked decision.</p>",
                "RESOURCES": "<p>FYF pp. 93-94 are embedded in the student guide. No separate deck is required.</p>",
                "SUPPORT": "<p>Use the point-of-use word bank detect, map, report, withstand, cover, protect, and constraint. The two-page sheet asks for one or two useful facts per report instead of recopying the workbook.</p>",
                "FALLBACK": "<p>The workbook and one double-sided field-notes sheet are the complete route. An absent student uses the embedded licensed pages and the same sheet. No live platform or extra worksheet is required.</p>",
            },
            3: {
                "TITLE": "Design the Pest Patrol Drone",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>Paper, Canva, and Adobe Express are equal.</strong> The evidence chain and function are scored, not art polish or premium assets.",
                "PREP": f'<ul><li><strong>Per student:</strong> completed Day 2 constraints, one {file_link(files["DESIGN"]["id"], "two-page design brief")} printed double-sided, pencil, and colored pencils. A student using Canva or Adobe may work digitally, but still needs an equal place for the evidence chain and tradeoff; default design-brief print count is one per student.</li><li><strong>Devices:</strong> one per digital-route student; no device or drone hardware is required for the paper route.</li><li>Post the {file_link(files["RUBRIC"]["id"], "rubric")} digitally; default rubric print count is 0. Open the unpublished draft Assignment. Offer the simple outline only as a support.</li><li><strong>Grouping:</strong> individual design; pairs of two for the tradeoff rehearsal.</li></ul>',
                "EVIDENCE": "<p>Six labeled features, three evidence links, one evidence chain, one tradeoff, and a named career role/work product/user. This begins the Major 2 packet.</p>",
                "MODEL": '<p><strong>Supplied evidence-chain model:</strong> “The farmer cannot walk every row, so the drone includes a mapping route. This helps the farmer find problem areas faster.” <strong>Non-example:</strong> “The drone has a cool camera.” The non-example names a part but gives no source, function, or benefit.</p>',
                "FLOW": flow(
                    "#5a2d91",
                    "Useful-sketch warm-up · 5",
                    "Labels, arrows, function, evidence.",
                )
                + flow(
                    "#4a9d2f", "Model one chain · 8", "Evidence to feature to benefit."
                )
                + flow(
                    "#1f617a",
                    "Design and label · 25",
                    "Paper or approved digital route.",
                )
                + flow(
                    "#e3ad19",
                    "Tradeoff check · 7",
                    "Benefit plus cost, risk, or limit.",
                )
                + flow("#1f617a", "Submit · 5", "Canvas draft or paper record."),
                "MONITOR": "<p><strong>District response move:</strong> Stop and Jot one evidence chain before students draw, then use a 60-second Think-Pair-Share for the tradeoff.</p><p><strong>Lap 1, minute 18:</strong> check for a large usable sketch and at least three function labels. Feedback: add a verb after each part name. If several students choose templates or decoration before functions, return the class to the supplied outline.</p><p><strong>Lap 2, minute 32:</strong> check six labels and three arrows to Day 2 evidence. If several students have labels without source links, pause and apply the supplied chain to one feature.</p><p><strong>Safe trim:</strong> cut color and decorative polish. Protect six functional labels, three evidence links, one complete chain, one tradeoff, and the five-minute save/submit/reset window. Keep automatic peer review off.</p>",
                "RESOURCES": f'<p>{file_link(files["DESIGN"]["id"], "Design Brief")} · {file_link(files["RUBRIC"]["id"], "student-visible rubric")} · licensed FYF p. 95 embedded.</p>',
                "SUPPORT": "<p>A full page is reserved for drawing. Allow bilingual labels, speech-to-text for the rationale, and a basic outline without reducing criteria.</p>",
                "FALLBACK": "<p>No hardware is required. If Canvas fails, collect the paper original or saved file for Day 4.</p>",
            },
            4: {
                "TITLE": "Review, Revise, and Evaluate Trends",
                "SUBTITLE": "50 minutes · TEKS d(1)(D), d(5)(C)",
                "ALERT": "<strong>Peer availability does not control the grade.</strong> Use the FYF p. 95 review as the default, or use manual Canvas reviewers, structured self-review, or a teacher conference.",
                "PREP": f'<ul><li><strong>Per student:</strong> saved drone draft, FYF workbook p. 95, one {file_link(files["REVIEW"]["id"], "revision record")}, and one {file_link(files["EVAL"]["id"], "two-page trends evaluation")} printed double-sided. This is three printed pages per student.</li><li>Post the {file_link(files["TRENDS"]["id"], "two-page trends guide")} and {file_link(files["RUBRIC"]["id"], "rubric")} digitally; default print count is 0 for both. Print one trends guide per pair only for a no-device class.</li><li><strong>Devices and grouping:</strong> one device per student or pair for the fixed guide; pairs of two for review, with structured self-review or a teacher conference as the equal alternate.</li><li>If using Canvas peer review, manually assign reviewers only after submissions exist. Open the unpublished Major 2 Assignment.</li></ul>',
                "EVIDENCE": "<p><strong>One combined Major submission:</strong> final Pest Patrol design, revision record, and two-trend evaluation using two facts and one limit. The evaluation conclusion is 3-4 complete sentences, not a second long essay.</p>",
                "MODEL": '<p><strong>Supplied feedback model:</strong> “Label what the camera detects so the farmer knows why it is useful.” <strong>Supplied trend model:</strong> “Precision-agriculture tools can change an agricultural engineer\'s monitoring work by adding sensor and drone data. USDA evidence supports scouting and monitoring, but it does not prove every farm can afford or benefit from the same system.”</p>',
                "FLOW": flow(
                    "#5a2d91", "Feedback warm-up · 5", "Evidence beats praise."
                )
                + flow(
                    "#4a9d2f",
                    "Review and revise · 12",
                    "One strength, one next step, one visible change.",
                )
                + flow(
                    "#1f617a",
                    "Read fixed trends · 8",
                    "Agriculture, energy, water workforce.",
                )
                + flow("#e3ad19", "Evaluate two trends · 18", "Two facts, changed tasks, limit, 3-4 sentence conclusion.")
                + flow("#1f617a", "Submit and reset · 7", "Highlight facts and limit; submit once."),
                "MONITOR": "<p><strong>District response move:</strong> run a 60-second Q-SSA review: Question from the criteria, Signal the label or feature, Stem for one next step, Assess the revision.</p><p><strong>Lap 1, minute 15:</strong> check for one specific next step and one visible change. Feedback must point to the work, not the person. If reviewer access fails, move immediately to self-review or a teacher conference.</p><p><strong>Lap 2, minute 33:</strong> check that each selected trend has a changed task, one sourced fact, and one limit. If several students treat growth as a guarantee or a U.S. median as starting pay, pause and use the supplied trend model.</p><p><strong>Minute 43 target:</strong> the 3-4 sentence conclusion contains both trends, two facts total, and one evidence limit. No single trend or career is correct. <strong>Safe trim:</strong> replace partner review with a five-minute self-review and cut oral sharing. Protect one visible revision, the two-trend evidence, and the seven-minute submit/cleanup window.</p>",
                "RESOURCES": '<p><a href="https://www.ars.usda.gov/research/publications/publication/?seqNo115=346120">USDA agriculture-drone research</a> · <a href="https://www.epa.gov/sustainable-water-infrastructure/water-infrastructure-sector-workforce">EPA water workforce</a> · current BLS pages listed in the guide.</p>',
                "SUPPORT": "<p>Use the workbook's existing review table for feedback. The one-page CCE record captures only the revision decision and proof. Point-of-use frames sit beside the review and evaluation steps. The Trends Evaluation gives one full-width line per short fact or limit and eight lines for the 3-4 sentence conclusion.</p>",
                "FALLBACK": "<p>The fixed guide replaces open research. Paper is equal to Canvas peer review, and an absent student uses self-review.</p>",
            },
            5: {
                "TITLE": "Set Two Goals in Xello",
                "SUBTITLE": "50 minutes · TEKS d(4)(A) · required Grade 8 Xello completion",
                "ALERT": "<strong>Required task: Set goals, 20 minutes, save at least two goals.</strong> The licensed Xello guide is an extended 25-30 minute resource and asks for three goals; the live district minimum controls today.",
                "PREP": f'<ul><li><strong>Per student:</strong> one district device. Default print count is 0. Post {file_link(files["GOALS"]["id"], "the private Goal Check")} digitally; print one copy per student only for the paper-planning or outage route.</li><li>Test ClassLink and Xello, then open the Completion Standards report before class.</li><li>Open the licensed {file_link(files["XELLO"]["id"], "Set Goals educator guide")} for the supplied modeling sequence. The guide is an extension, not a third-goal requirement.</li><li>Open the private reflection Assignment. Grouping is individual/private; no partner disclosure is required.</li></ul>',
                "EVIDENCE": "<p>Completion Standards report shows at least two saved goals; the private reflection names a timeframe, next task, obstacle, backup, and possible revision. Formative d(4)(A) evidence.</p>",
                "MODEL": '<p><strong>Privacy-safe fictional model:</strong> “By October 1, I will finish one career-interview question list. My next task is to write five questions by Friday. If I cannot meet the worker, I will use a teacher-approved career profile and revise the interview plan.” Model the fields, not a personal disclosure.</p>',
                "FLOW": flow("#5a2d91", "Goal warm-up · 5", "What keeps a plan moving?")
                + flow(
                    "#4a9d2f",
                    "Adaptability bridge · 8",
                    "Control, change, and backup action.",
                )
                + flow(
                    "#1f617a",
                    "Xello Set goals · 20",
                    "Two goals, timeframe, one task each.",
                )
                + flow(
                    "#e3ad19",
                    "Private reflection · 12",
                    "Next task, obstacle, backup, likely revision.",
                )
                + flow(
                    "#1f617a",
                    "Report, catch-up, and reset · 5",
                    "Verify or schedule supervised completion.",
                ),
                "MONITOR": "<p><strong>District response move:</strong> use a private Stop and Jot for the obstacle/backup plan, then Active Monitor navigation without reading private goal content.</p><p><strong>Lap 1, minute 13:</strong> every student is in About Me &gt; Goals or has a named access barrier. If several students remain on Home, pause for one ClassLink/navigation reset.</p><p><strong>Lap 2, minute 29:</strong> each student has saved Goal 1 and started Goal 2, or is on the documented paper/catch-up route. Feedback targets timeframe and next task without requiring personal disclosure.</p><p><strong>Minute 45 target:</strong> two saved goals are visible in the Completion Standards report and the private reflection is submitted or collected. The extended guide's third goal is optional. <strong>Safe trim:</strong> reduce the adaptability bridge to one control/change/backup example. Protect the 20-minute Xello minimum, private reflection, and report/catch-up record.</p>",
                "RESOURCES": f'<p>{file_link(files["XELLO"]["id"], "Licensed Xello Set Goals guide")} · {file_link(files["GOALS"]["id"], "one-page private goal check")} · FYF p. 146 embedded as a short adaptability bridge.</p>',
                "SUPPORT": "<p>Use Xello for the full goal statements. The one-page check prevents duplicate writing and gives students room for the timeframe, next task, obstacle, backup plan, and private reflection.</p>",
                "FALLBACK": "<p>Paper planning supports access but does not replace Xello. Schedule supervised catch-up and verify through the report.</p>",
            },
        }

        day_names = {
            1: "Careers and Resource Problems",
            2: "Field Reports and Constraints",
            3: "Pest Patrol Drone Design",
            4: "Review, Revision, and Trends",
            5: "Xello Set Goals",
        }
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_item(
                client, module["id"], "SubHeader", None, header_title
            )
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 3SW Wk3 Day {day} - {day_names[day]}"
            student_page = await upsert_page(
                client,
                student_title,
                render(
                    "3sw-wk3-student.html",
                    {
                        "COURSE_ID": COURSE_ID,
                        "DAY": day,
                        **contracts[day],
                        **student[day],
                    },
                ),
            )
            teacher_title = f"TEACHER: 3SW Wk3 Day {day} Facilitator Guide"
            teacher_page = await upsert_page(
                client,
                teacher_title,
                render(
                    "3sw-wk3-teacher.html",
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
            if day == 1:
                await upsert_item(
                    client, module["id"], "Assignment", career["id"], CAREER_TITLE
                )
                order.append(("Assignment", career["id"], CAREER_TITLE))
            if day == 3:
                await upsert_item(
                    client, module["id"], "Assignment", draft["id"], DRAFT_TITLE
                )
                order.append(("Assignment", draft["id"], DRAFT_TITLE))
            if day == 4:
                await upsert_item(
                    client, module["id"], "Assignment", packet["id"], PACKET_TITLE
                )
                order.append(("Assignment", packet["id"], PACKET_TITLE))
            if day == 5:
                await upsert_item(
                    client, module["id"], "Assignment", goals["id"], GOALS_TITLE
                )
                order.append(("Assignment", goals["id"], GOALS_TITLE))

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
        if module.get("published"):
            raise RuntimeError("3SW Wk3 module unexpectedly published")
        for label, assignment in (
            ("career", career),
            ("draft", draft),
            ("Major", packet),
            ("goals", goals),
        ):
            if assignment.get("published"):
                raise RuntimeError(f"3SW Wk3 {label} assignment unexpectedly published")
        published_pages = [
            value["url"]
            for pair in pages.values()
            for value in pair.values()
            if value.get("published")
        ]
        if published_pages:
            raise RuntimeError(f"Published 3SW Wk3 pages remain: {published_pages}")
        published_items = [
            entry.get("title") for entry in final_items if entry.get("published")
        ]
        if published_items:
            raise RuntimeError(f"Published 3SW Wk3 module items remain: {published_items}")
        if len(final_items) != len(order):
            raise RuntimeError(
                f"Expected {len(order)} 3SW Wk3 module items; found {len(final_items)}"
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
                    f"3SW Wk3 module order mismatch at position {position}"
                )
        print(
            json.dumps(
                {
                    "module": {"id": module["id"], "published": module["published"]},
                    "assignments": {
                        "career": {
                            "id": career["id"],
                            "published": career.get("published"),
                            "grading_type": career.get("grading_type"),
                            "omit_from_final_grade": career.get(
                                "omit_from_final_grade"
                            ),
                        },
                        "draft": {
                            "id": draft["id"],
                            "published": draft.get("published"),
                            "grading_type": draft.get("grading_type"),
                            "omit_from_final_grade": draft.get(
                                "omit_from_final_grade"
                            ),
                            "peer_reviews": draft.get("peer_reviews"),
                            "automatic_peer_reviews": draft.get(
                                "automatic_peer_reviews"
                            ),
                        },
                        "packet": {
                            "id": packet["id"],
                            "published": packet.get("published"),
                            "points_possible": packet.get("points_possible"),
                            "assignment_group_id": packet.get("assignment_group_id"),
                            "grading_type": packet.get("grading_type"),
                            "omit_from_final_grade": packet.get(
                                "omit_from_final_grade"
                            ),
                        },
                        "goals": {
                            "id": goals["id"],
                            "published": goals.get("published"),
                            "grading_type": goals.get("grading_type"),
                            "omit_from_final_grade": goals.get(
                                "omit_from_final_grade"
                            ),
                        },
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
