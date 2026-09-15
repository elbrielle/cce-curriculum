"""Build the unpublished 4SW Week 1 Mid-Year Career Blueprint Canvas module."""

import asyncio
import json
import mimetypes
import re
import sys
from pathlib import Path

import httpx

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
STUDENT_GOOGLE_COPY_URLS = {
    1: "https://docs.google.com/document/d/18PB5zUUTEgQaVmOH_cqam_ozNeeg6QYXy0PliAQc99c/copy",
    2: "https://docs.google.com/document/d/1EsDBV1nbncBIm6_Wo7nwTfztMKPw5jgAUoLUBIDfEOs/copy",
    3: "https://docs.google.com/document/d/1ZqAjo6PImJeqq2637mLc6Di0nY7E9nEEudKFRo04-N0/copy",
    4: "https://docs.google.com/document/d/1_F79rG1DQFUmQKMeeDj6UZ_cw0PNr7QRHIlmSEiYZvQ/copy",
    5: "https://docs.google.com/document/d/16oW1HGXv9XObRcYogVaTxrfsx_JsEEWRlMqj4LSX7p4/copy",
}


# One Google Doc per worksheet (build/google_docs/student_worksheet_docs.json).
# Keyed by (day, anchor label) so a worksheet button never opens the day's exit ticket.
STUDENT_WORKSHEET_COPY_URLS = {
    (1, 'Open the same audit'): "https://docs.google.com/document/d/1hYba2Nc6Lkl-53VC-Ln5pI455dT9FkZj1fVL_08s6WQ/copy",
    (2, 'the enlarged support packet'): "https://docs.google.com/document/d/1DlHVY9yAxSr5PJS9WMNNw8ItxxkIuFH2SyFbKhiuNLA/copy",
    (3, 'the Quick Sim Decision Record'): "https://docs.google.com/document/d/1ZHQnYqCh61yj89aHSLUp-28_UfZYlyL0xKJvUMClh9s/copy",
    (4, 'the four-page paper or enlarged route'): "https://docs.google.com/document/d/1rfAIYlGwxR8vaC8-foyMKX39To99bd6VgDMvpiAbotk/copy",
    (5, 'the three-page Mid-Year Career Blueprint'): "https://docs.google.com/document/d/1h24Z_QBTM4tVNec-am3Z9hU3ADqLoNWN9xuor6hKYf0/copy",
}


def student_copy_link(day, label):
    url = STUDENT_WORKSHEET_COPY_URLS.get((day, label), STUDENT_GOOGLE_COPY_URLS[day])
    return f'<a href="{url}">{label}</a>'

MODULE_NAME = "4SW Wk1: Build Your Mid-Year Career Blueprint"
ANNOTATION_TITLE = "PRACTICE: Career Iceberg Annotation"
PATHWAY_TITLE = "PRACTICE: Pathway and CTSO Decision"
BLUEPRINT_TITLE = "MAJOR 1: Mid-Year Career Blueprint"
RUBRIC_NOTE_MARKER = 'data-cce-rubric-note="cce-advisory-rubric-v1"'
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/4sw/wk1"
WORKSHEET_FILES = {
    "AUDIT": "4sw-wk1-midyear-profile-audit.pdf",
    "ICEBERG": "4sw-wk1-career-iceberg-and-goal.pdf",
    "DEEP": "4sw-wk1-career-deep-dive.pdf",
    "PATHWAY": "4sw-wk1-pathway-and-ctso-decision.pdf",
    "BLUEPRINT": "4sw-wk1-midyear-career-blueprint.pdf",
    "RUBRIC": "4sw-wk1-midyear-blueprint-rubric.pdf",
}
VISUAL_FILES = {
    1: ("fyf-rung-1-who-you-are.jpg",),
    2: (
        "fyf-career-iceberg-model.jpg",
        "fyf-rung-2-career-goal.jpg",
        "fyf-rung-2-career-snapshot.jpg",
    ),
    5: ("fyf-career-thinker-and-doer.jpg",),
}
RN_CARD = """<div style="border:1px solid #bad4df;background:#f2f8fb;padding:14px 18px;margin:14px 0"><p><strong>Supplied dated career card: Registered Nurse</strong> (BLS Occupational Outlook Handbook, accessed August 11, 2026)</p><ul><li><strong>Work:</strong> provides and coordinates patient care; educates patients and the public.</li><li><strong>Settings:</strong> hospitals, physicians' offices, home healthcare, nursing facilities, clinics, and schools.</li><li><strong>Preparation:</strong> approved nursing program and state license; common education routes include bachelor's, associate's, or approved diploma programs.</li><li><strong>Pay:</strong> $93,600, May 2024 U.S. median annual wage. This is not DFW starting pay.</li><li><strong>Outlook:</strong> 5% U.S. projected growth, 2024-2034.</li><li><strong>Source:</strong> <a href="https://www.bls.gov/ooh/healthcare/registered-nurses.htm">BLS Occupational Outlook Handbook: Registered Nurses</a></li></ul></div>"""
PATHWAY_SNAPSHOT = """<div style="border:1px solid #bad4df;background:#f2f8fb;padding:14px 18px;margin:14px 0"><p><strong>Supplied Irving ISD CTE snapshot</strong> (district High School CTE page, accessed August 11, 2026). Use exact names; write <em>not yet confirmed</em> for a course, prerequisite, transportation route, application step, or local CTSO chapter that this snapshot does not establish.</p><ul><li><strong>Cardwell:</strong> Business Management; Early Childhood Education; Automotive, Collision Repair and Diesel; Cosmetology.</li><li><strong>Irving High:</strong> Biomedical Sciences; Aviation Maintenance and Drone Engineering; Education and Training; Lodging and Resort Management; Business Management and Marketing; Digital Communications and Graphic Design; Computer Science; Automotive, Collision Repair and Diesel; Cosmetology.</li><li><strong>MacArthur:</strong> Architecture, Construction and Engineering; Business, Retail Management and Entrepreneurship; Real Estate; Education and Training; Lodging and Resort Management; Digital Communications and Graphic Design; Computer Science; Automotive, Collision Repair and Diesel; Cosmetology.</li><li><strong>Nimitz:</strong> Agricultural Science; Sustainable Engineering; Education and Training; Lodging and Resort Management; Business Management and Marketing; Digital Communications and Graphic Design; Computer Science; Automotive, Collision Repair and Diesel; Cosmetology.</li><li><strong>Singley Academy:</strong> School of Health Sciences; School of Culinary Arts and Hospitality; School of Innovative Technology; School of Law and Public Service. Admission is application- and lottery-based; current dates must be checked.</li></ul><p><strong>Current sources:</strong> Irving ISD High School CTE and School Choice pages.</p></div>"""


def preflight():
    required = [
        TEMPLATES / "4sw-wk1-student.html",
        TEMPLATES / "4sw-wk1-teacher.html",
        *(ROOT / "docs/resources/worksheets" / name for name in WORKSHEET_FILES.values()),
        *(
            ASSETS / f"day{day}" / name
            for day, names in VISUAL_FILES.items()
            for name in names
        ),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"4SW Wk1 preflight missing required files: {missing}")


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


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
    matches = [entry for entry in modules if entry["name"] == MODULE_NAME]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one module named {MODULE_NAME!r}; found {len(matches)}")
    if matches:
        found = matches[0]
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
    unlocked = []
    for entry in final:
        if not entry.get("locked"):
            refreshed = await api(client, "GET", f"/files/{entry['id']}")
            if not refreshed.get("locked"):
                unlocked.append(entry.get("display_name") or entry.get("filename"))
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
    data = {"wiki_page[title]": title, "wiki_page[body]": body, "wiki_page[published]": "false", "wiki_page[editing_roles]": "teachers"}
    response = await client.get(f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{url}")
    if response.status_code == 200:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/pages/{url}", data=data)
    if response.status_code != 404:
        response.raise_for_status()
    return await api(client, "POST", f"/courses/{COURSE_ID}/pages", data=data)


async def upsert_assignment(client, title, description, submission_types, attachment_id=None):
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == title]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one practice assignment named {title!r}; found {len(matches)}")
    found = matches[0] if matches else None
    data = {
        "assignment[name]": title,
        "assignment[description]": description,
        "assignment[submission_types][]": submission_types,
        # Canvas removes online submission routes when Display Grade is set to
        # Not Graded. Keep private evidence collection available while making
        # the formative item gradebook-neutral.
        "assignment[grading_type]": "percent",
        "assignment[points_possible]": "0",
        "assignment[omit_from_final_grade]": "true",
        "assignment[published]": "false",
    }
    if attachment_id:
        data["assignment[annotatable_attachment_id]"] = str(attachment_id)
    endpoint = f"/courses/{COURSE_ID}/assignments/{found['id']}" if found else f"/courses/{COURSE_ID}/assignments"
    assignment = await api(client, "PUT" if found else "POST", endpoint, data=data)
    if (
        assignment.get("published")
        or float(assignment.get("points_possible") or 0) != 0
        or assignment.get("omit_from_final_grade") is not True
    ):
        raise RuntimeError(
            f"Practice assignment invariant failed for {title!r}: "
            f"published={assignment.get('published')}, points={assignment.get('points_possible')}, "
            f"omit={assignment.get('omit_from_final_grade')}"
        )
    return assignment


async def require_major_preflight(client):
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == BLUEPRINT_TITLE]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one existing mapped Major assignment named {BLUEPRINT_TITLE!r}; found {len(matches)}"
        )
    found = matches[0]
    groups = await paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group_matches = [entry for entry in groups if entry.get("name") == "Major Assessments (60%)"]
    if len(group_matches) != 1:
        raise RuntimeError("Expected exactly one assignment group named 'Major Assessments (60%)'")
    group = group_matches[0]
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
            f"Mapped Major invariant failed before module writes: published={found.get('published')}, "
            f"points={found.get('points_possible')}, group={found.get('assignment_group_id')}, "
            f"grading={found.get('grading_type')}, omit={found.get('omit_from_final_grade')}, "
            f"rubric_note={rubric_note is not None}"
        )
    return found, group


async def update_major_assignment(client, found, group, description):
    rubric_note = re.search(
        r'<div data-cce-rubric-note="cce-advisory-rubric-v1".*?</div>',
        found.get("description") or "",
        flags=re.I | re.S,
    )
    if rubric_note is None:
        raise RuntimeError(f"Mapped Major is missing required rubric conversion note: {BLUEPRINT_TITLE!r}")
    description += rubric_note.group(0)
    blueprint = await api(
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
        blueprint.get("published")
        or float(blueprint.get("points_possible") or 0) != 100
        or blueprint.get("assignment_group_id") != group["id"]
        or blueprint.get("grading_type") != "points"
        or blueprint.get("omit_from_final_grade") is not False
        or RUBRIC_NOTE_MARKER not in (blueprint.get("description") or "")
    ):
        raise RuntimeError(
            f"Major invariant failed after update: published={blueprint.get('published')}, "
            f"points={blueprint.get('points_possible')}, group={blueprint.get('assignment_group_id')}, "
            f"grading={blueprint.get('grading_type')}, omit={blueprint.get('omit_from_final_grade')}, "
            f"rubric_note={RUBRIC_NOTE_MARKER in (blueprint.get('description') or '')}"
        )
    return blueprint


async def upsert_item(client, module_id, kind, key, title):
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    found = next((item for item in items if (kind == "SubHeader" and item.get("title") == title) or (kind == "Page" and item.get("page_url") == key) or (kind == "Assignment" and item.get("content_id") == key)), None)
    if found:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module_id}/items/{found['id']}", data={"module_item[title]": title, "module_item[published]": "false"})
    data = {"module_item[type]": kind, "module_item[title]": title, "module_item[published]": "false"}
    if kind == "Page":
        data["module_item[page_url]"] = key
    elif kind == "Assignment":
        data["module_item[content_id]"] = key
    return await api(client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data=data)


def module_item_matches(item, kind, key, title):
    if item.get("type") != kind:
        return False
    if kind == "SubHeader":
        return item.get("title") == title
    if kind == "Page":
        return item.get("page_url") == key
    if kind == "Assignment":
        return item.get("content_id") == key
    return False


async def reconcile_module_items(client, module_id, expected):
    remaining = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    kept = []
    for position, (kind, key, title) in enumerate(expected, 1):
        matches = [item for item in remaining if module_item_matches(item, kind, key, title)]
        if matches:
            item = matches[0]
            for duplicate in matches[1:]:
                await api(client, "DELETE", f"/courses/{COURSE_ID}/modules/{module_id}/items/{duplicate['id']}")
                remaining.remove(duplicate)
        else:
            item = await upsert_item(client, module_id, kind, key, title)
        remaining = [entry for entry in remaining if entry.get("id") != item.get("id")]
        item = await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            data={
                "module_item[title]": title,
                "module_item[position]": position,
                "module_item[published]": "false",
            },
        )
        kept.append(item)
    for stale in remaining:
        await api(client, "DELETE", f"/courses/{COURSE_ID}/modules/{module_id}/items/{stale['id']}")

    final = sorted(
        await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items"),
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


def file_link(file_id, label):
    return f'<a href="/courses/{COURSE_ID}/files/{file_id}/preview" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">{label}</a>'


def image_tag(file_id, alt):
    return f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" style="display:block;width:100%;max-width:700px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'


def step(number, title, body):
    return f'<h3 style="color:#5a2d91;border-bottom:3px solid #d9c9ed">{number}. {title}</h3>{body}'


def flow(color, title, text):
    return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0 0 6px;color:{color}">{title}</h4>{text}</div>'


async def main():
    preflight()
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        mapped_major, major_group = await require_major_preflight(client)
        module = await ensure_module(client)
        support = "course files/CCR Materials/4SW/Wk1"
        support_folder = await ensure_folder(client, support)
        files = {key: await upload(client, ROOT / "docs/resources/worksheets" / name, support) for key, name in WORKSHEET_FILES.items()}

        visuals, folders = {}, {}
        for day, image_names in VISUAL_FILES.items():
            folder_path = f"course files/CCR Materials/4SW/Wk1/Day {day} Visuals"
            folders[day], visuals[day] = await ensure_folder(client, folder_path), {}
            for name in image_names:
                visuals[day][name] = await upload(client, ASSETS / f"day{day}" / name, folder_path)
        support_folder = await lock_folder_files(client, support_folder)
        for day in folders:
            folders[day] = await lock_folder_files(client, folders[day])

        annotation = await upsert_assignment(client, ANNOTATION_TITLE, "<p>Label the Career Iceberg directly in Canvas, upload the completed file, type a labeled response, or use the paper copy. Art quality is not scored.</p>", ["student_annotation", "online_upload", "online_text_entry"], files["ICEBERG"]["id"])
        pathway_practice = await upsert_assignment(
            client,
            PATHWAY_TITLE,
            '<p>Submit one private pathway decision as typed text, a file, or an approved audio response. Include two or three current Irving ISD options, one source and access date, a comparison of the top two, one CTSO benefit, and one fact to verify. Use the linked packet only when you need the paper or enlarged route.</p>',
            ["online_upload", "online_text_entry", "media_recording"],
        )
        blueprint_description = f'<p>Submit only your completed three-page Mid-Year Career Blueprint by file upload, typed response, or approved audio response. Days 1-4 are evidence-building checkpoints, not five separate required uploads. Use the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">student scoring guide</a> before submitting. This assignment is already mapped as a 100-point Major Assessment and remains unpublished for teacher review and cloning.</p>'
        blueprint = await update_major_assignment(client, mapped_major, major_group, blueprint_description)
        annotation_url = f"/courses/{COURSE_ID}/assignments/{annotation['id']}"
        pathway_practice_url = f"/courses/{COURSE_ID}/assignments/{pathway_practice['id']}"
        blueprint_url = f"/courses/{COURSE_ID}/assignments/{blueprint['id']}"

        media = {
            1: image_tag(visuals[1]["fyf-rung-1-who-you-are.jpg"]["id"], "Find Your Future Rung 1 prompts for interests, strengths, skills, work values, and personality evidence"),
            2: image_tag(visuals[2]["fyf-career-iceberg-model.jpg"]["id"], "Find Your Future Career Iceberg worked example showing visible results above water and hidden effort below") + image_tag(visuals[2]["fyf-rung-2-career-goal.jpg"]["id"], "Find Your Future Rung 2 career goal prompts") + image_tag(visuals[2]["fyf-rung-2-career-snapshot.jpg"]["id"], "Find Your Future Rung 2 career snapshot prompts"),
            3: "",
            4: "",
            5: image_tag(visuals[5]["fyf-career-thinker-and-doer.jpg"]["id"], "Find Your Future Career Thinker and Doer reflection and career community prompts"),
        }

        contracts = {
            1: {"TOPIC": "Career Assessment", "OBJECTIVE": "Students will compare an earlier career-assessment or profile result with current evidence.", "TEKS": "d(1)(A)", "DOL": "Mid-Year Profile Audit.", "I_CAN": "compare an earlier career result with evidence from what I have done this year.", "SHOW": "complete a Mid-Year Profile Audit with an earlier result, three current facts, and a supported conclusion."},
            2: {"TOPIC": "Career Assessment", "OBJECTIVE": "Students will explain the visible and hidden work behind one career and name a current direction.", "TEKS": "d(1)(A), d(8)(A)", "DOL": "Career Iceberg and Goal in the FYF workbook, support packet, or Canvas annotation.", "I_CAN": "explain the visible and hidden work behind one career and name my current direction.", "SHOW": "complete a Career Iceberg and Goal in my workbook, on paper, or in Canvas."},
            3: {"TOPIC": "Financial Planning", "OBJECTIVE": "Students will build and save a Xello Quick sim with career, education, and expense choices, then explain one financial tradeoff.", "TEKS": "d(5)(D)", "DOL": "Saved Xello Quick sim plus one career-education-expense tradeoff explanation.", "I_CAN": "build and save a Quick sim and explain how one choice changed the monthly plan.", "SHOW": "save one Quick sim with a career, education, and at least one expense, then explain one tradeoff."},
            4: {"TOPIC": "Extended Learning", "OBJECTIVE": "Students will compare current Irving ISD pathway options and explain one benefit of CTSO participation.", "TEKS": "d(3)(F), d(8)(A)", "DOL": "Private Pathway and CTSO Decision.", "I_CAN": "compare Irving ISD pathways and explain how one CTSO experience could help me prepare.", "SHOW": "submit a private Pathway and CTSO Decision with a source, comparison, benefit, and verification question."},
            5: {"TOPIC": "Career Planning", "OBJECTIVE": "Students will synthesize self, Quick Sim, and pathway evidence into a current plan with a backup and next action.", "TEKS": "d(1)(A), d(5)(D), d(8)(A)", "DOL": "Mid-Year Career Blueprint.", "I_CAN": "use self, Quick Sim, and pathway evidence to make a current plan with a backup and next action.", "SHOW": "submit one private Mid-Year Career Blueprint and revise it with the student scoring guide."},
        }

        student = {
            1: {"TITLE":"Mid-Year Profile Audit","PURPOSE":"Use current evidence to examine how your career thinking has changed or stayed the same.","TODAY":"<ul><li>review one earlier result or idea;</li><li>collect three current pieces of evidence;</li><li>defend one conclusion.</li></ul>","READY":f'<p><strong>Response home:</strong> use the front-and-back Mid-Year Profile Audit your teacher gives you. Write your name on it. Your teacher will collect it today and return it for the Day 5 Blueprint. {student_copy_link(1, "Open the same audit")} only if you need a replacement or absence copy. H&amp;L, Xello, and earlier portfolio work are optional evidence sources; a private screenshot is not required.</p>',"LANGUAGE":'<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> evidence = a specific result, choice, task, or experience · pattern = what repeats · supports = agrees with · complicates = adds another side.</p><p><strong>Use this frame:</strong> My earlier result said ___. Current evidence shows ___ and ___. This supports, complicates, or changes the result because ___.</p></div>',"STEPS":step(1,"Choose the earlier result","<p>Record one earlier assessment result, work value, Building Block, career idea, or clearly labeled current baseline.</p>")+step(2,"Collect three pieces of evidence","<p>Use specific activities, choices, feedback, or profile results from different sources.</p>")+step(3,"Analyze the pattern","<p>Decide whether the evidence supports, complicates, or changes the earlier result. Explain why.</p>"),"EXIT":"<p>What is one conclusion you can defend now, and what evidence supports it? Put the completed audit in the class collection folder before leaving.</p>","DONE":"<ul><li>one baseline;</li><li>three specific pieces of evidence;</li><li>one pattern;</li><li>one defensible conclusion;</li><li>name on the audit and audit handed in for Day 5.</li></ul>","SUPPORT":"<p>evidence = evidencia · earlier = anterior · current = actual · pattern = patrón. Use the complete frame above and speak your explanation before writing.</p>","FALLBACK":"<p>If you were absent, print the audit or use a notebook with the same four section headings. If earlier evidence is missing, use today's self-evidence inventory and label it as your baseline. Give the completed work to your teacher so it can be returned on Day 5.</p>"},
            2: {"TITLE":"Career Iceberg and Goal","PURPOSE":"Show the visible and hidden work behind one career, then decide whether it remains a useful direction.","TODAY":"<ul><li>study an iceberg model;</li><li>label one career iceberg;</li><li>write a working career goal.</li></ul>","READY":f'<p><strong>Default route:</strong> use FYF pp. 6-8 and 283-284 in your workbook. Use {student_copy_link(2, "the enlarged support packet")} or <a href="{annotation_url}">the Canvas annotation</a> only when the workbook is unavailable or you need that route. Do not complete both.</p>',"LANGUAGE":'<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Sort hidden work into:</strong> skills · tools or technology · education or training · responsibilities or challenges.</p><p><strong>Use this frame:</strong> One hidden requirement is ___. It strengthens, weakens, or complicates my interest because ___.</p></div>',"STEPS":step(1,"Read the model","<p>Use FYF pp. 6-7. Find what people see above the waterline and what the career requires below it.</p>")+step(2,"Build your iceberg","<p>On FYF p. 8, add at least three visible parts and eight hidden parts. Label each hidden part with one category from the blue box above.</p>")+step(3,"Set a working goal","<p>Use FYF pp. 283-284. Connect two Day 1 facts, one hidden requirement, and one research question. This is a current direction, not a permanent promise.</p>"),"EXIT":"<p>Name one hidden requirement that changed how you see the career. Does it strengthen, weaken, or complicate your interest?</p>","DONE":"<ul><li>three visible items;</li><li>eight hidden items across the labeled categories;</li><li>two self-evidence connections;</li><li>one research question.</li></ul>","SUPPORT":"<p>visible = visible · hidden = oculto · training = capacitación · responsibility = responsabilidad. Drawing skill is not scored.</p>","FALLBACK":"<p>The support packet, Canvas annotation, typed list, or audio response replaces the workbook route. The embedded images explain the task for an absent student.</p>"},
            3: {"TITLE":"Xello Save Quick Sims","PURPOSE":"Test how career, education, and expense choices change a monthly plan.","TODAY":"<ul><li>open The Real Game;</li><li>add a career and education;</li><li>add at least one expense;</li><li>save the Quick sim and explain one tradeoff.</li></ul>","READY":f'<p>Open <strong>ClassLink &gt; Xello &gt; Home &gt; The Real Game</strong>. Keep {student_copy_link(3, "the Quick Sim Decision Record")} open for the short debrief or the teacher-assigned no-device learning route. Paper supports the learning but does not count as Xello completion.</p>',"LANGUAGE":'<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> career/carrera · education/educación · expense/gasto · debt/deuda · tradeoff/ventaja y costo.</p><p><strong>Use this frame:</strong> Adding ___ changed the plan by ___. The tradeoff is ___.</p></div>',"STEPS":step(1,"Open the assigned task","<p>Open Home, then The Real Game. Start one Quick sim.</p>")+step(2,"Complete the three actions","<p>Open your <em>Find Your Future</em> workbook to pp. 285-286 and use your Rung 3 career, training, and salary notes as your starting choices. Add a career, add education, and add at least one expense. Student loans and family members count as expenses when selected.</p>")+step(3,"Review and save","<p>Notice how education and expenses change the monthly plan. Save the Quick sim instead of racing through extra scenarios.</p>")+step(4,"Explain the tradeoff","<p>Name the choice that changed the plan most and explain its benefit and cost.</p>"),"EXIT":"<p>Which choice had the largest effect on your Quick sim, and what would you change in a second scenario?</p>","DONE":"<ul><li>one Quick sim saved;</li><li>career added;</li><li>education added;</li><li>at least one expense added;</li><li>one tradeoff explained.</li></ul>","SUPPORT":"<p>Use the three-action checklist, read one choice at a time, and rehearse the tradeoff sentence aloud before writing.</p>","FALLBACK":'<p>If Xello is unavailable, complete the fixed Jordan scenario on the Decision Record and tell your teacher. The teacher schedules the required Xello save in a supervised recovery window; paper does not count as completion.</p>'},
            4: {"TITLE":"Irving Pathway and CTSO Decision","PURPOSE":"Compare current local options and explain how one student organization could help you prepare.","TODAY":"<ul><li>read current Irving ISD program information;</li><li>compare and rank pathways;</li><li>connect one CTSO benefit.</li></ul>","READY":f'<p><strong>Digital route:</strong> <a href="{pathway_practice_url}">open the private Pathway and CTSO Decision</a>. Use <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte">Irving ISD High School CTE</a>, the <a href="https://www.irvingisd.net/departments-services/curriculum-and-instruction/middle-school-and-high-school-course-descriptions">2026-27 coursebook page</a>, and the <a href="https://tea.texas.gov/student-readiness-and-high-school/college-career-and-military-prep/career-and-technical-education/career-and-technical-education-student-organizations">TEA CTSO page</a>. Use {student_copy_link(4, "the four-page paper or enlarged route")} only when needed.</p>',"LANGUAGE":'<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> pathway = a sequence of related courses · prerequisite = a course or condition needed first · CTSO = a student organization connected to CTE.</p><p><strong>Use this frame:</strong> ___ is stronger for me right now because the district source shows ___. A CTSO could help me ___ by ___.</p></div>',"STEPS":step(1,"Record exact current names","<p>Capture the pathway or program, location when verified, one connection, and one course, requirement, or question.</p>")+step(2,"Compare before ranking","<p>Use fit and evidence, not popularity. It is acceptable to write “not yet confirmed.”</p>")+step(3,"Add a CTSO benefit","<p>Select a plausible organization and explain one specific preparation benefit. Confirm local chapter availability before claiming it exists.</p>")+step(4,"Submit privately",f'<p><a href="{pathway_practice_url}">Submit the structured text, file, or approved audio response</a>. This practice is grade-neutral.</p>'),"EXIT":"<p>Name your current first choice, one verified fact, one unanswered question, and one way a CTSO could help.</p>","DONE":"<ul><li>three current options, or two with support;</li><li>sources and access date;</li><li>evidence-based ranking;</li><li>one CTSO benefit;</li><li>one verification question.</li></ul>","SUPPORT":"<p>pathway = trayectoria · requirement = requisito · verified = verificado · organization = organización. Read one program card at a time.</p>","FALLBACK":PATHWAY_SNAPSHOT + '<p>If a site is unavailable, use this supplied snapshot and mark every course, prerequisite, access step, or local chapter detail that still needs verification. The paper packet is the complete no-platform response route.</p>'},
            5: {"TITLE":"Mid-Year Career Blueprint","PURPOSE":"Turn the week's evidence into a current plan, a backup direction, and one next action.","TODAY":"<ul><li>gather Days 1-4 evidence;</li><li>build a private Blueprint;</li><li>self-score and revise.</li></ul>","READY":f'<p>Open {student_copy_link(5, "the three-page Mid-Year Career Blueprint")} and {file_link(files["RUBRIC"]["id"], "the student scoring guide")}. You submit the Blueprint only. Days 1-4 are evidence sources, not four extra uploads.</p>',"LANGUAGE":'<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Blueprint jobs:</strong> self-evidence · Quick Sim evidence · pathway · backup · trade-off · next action.</p><p><strong>Use this frame:</strong> My current direction is ___ because ___. My backup is ___. One trade-off is ___. Within six weeks, I will ___.</p></div>',"STEPS":step(1,"Gather","<p>Bring forward self-evidence, the iceberg insight, the saved Quick Sim career-education-expense tradeoff, and one verified pathway fact.</p>")+step(2,"Build","<p>Name a current direction, backup, next six-week action, and question for a trusted adult or professional.</p>")+step(3,"Self-score and revise","<p>Check all four criteria. Revise one weak area before you submit.</p>")+step(4,"Submit privately",f'<p><a href="{blueprint_url}">Open the private Blueprint assignment</a>, or hand in the paper copy.</p>'),"EXIT":"<p>My plan is stronger now because I used evidence from ____ to change or confirm ____.</p>","DONE":"<ul><li>all Blueprint jobs;</li><li>Quick Sim tradeoff retained;</li><li>specific backup and next action;</li><li>private scoring-guide check;</li><li>one visible revision.</li></ul>","SUPPORT":"<p>blueprint = plan · backup = plan alternativo · next action = próxima acción. Text, speech-to-text, and media recording answer the same sentence jobs.</p>","FALLBACK":"<p>Use the fallback evidence box if an earlier artifact is missing. Canvas failure does not change the task or score; submit paper or upload later.</p>"},
        }

        teacher = {
            1: {
                "TITLE": "Mid-Year Profile Audit",
                "SUBTITLE": "50 minutes · TEKS d(1)(A)",
                "ALERT": "<strong>Do not require a retake.</strong> Students analyze earlier evidence against current evidence; a private screenshot is never required.",
                "PREP": f'<ul><li><strong>Print:</strong> one {file_link(files["AUDIT"]["id"], "Mid-Year Profile Audit")} per student, double-sided: two pages on one sheet. This is the default response home.</li><li><strong>Devices:</strong> zero required for the core; one per student only when students choose to consult existing H&amp;L, Xello, or portfolio evidence.</li><li>Set one labeled Day 1-to-Day 5 class folder or period tray. Collect the named audits today and return them on Day 5.</li><li>Keep the no-prior-evidence baseline route ready for new or absent students.</li></ul>',
                "MODEL": "<p><strong>Label:</strong> “I am a Helper.” <strong>Usable evidence:</strong> “I chose patient-care and teaching tasks in three activities, and I liked explaining directions to a partner.” <strong>Conclusion:</strong> “The Helper result still fits, but my troubleshooting work shows an Analyzer side too.” Ask students which words make the second statement evidence rather than a label.</p>",
                "EVIDENCE": "<p>One earlier result or baseline, three specific current facts, one pattern, and one defensible conclusion on the named Audit. Formative; collect and retain for Day 5.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and changed interests warm-up", '''<p>Welcome students back to the start of the Fourth Six-Weeks (4SW) and project the personal growth prompt.</p><ul><li>Ask students: <em>“Think back to the very first week of school in August when you filled out your interest surveys. What is ONE interest, hobby, or career curiosity you had in August that has noticeably shifted, expanded, or completely disappeared after four months in middle school? What caused that change?”</em></li><li>Collect 2-3 student reflections. Emphasize that intellectual and career growth is not a failure of consistency; maturing interests are the natural result of trying new experiences and learning authentic skills.</li><li>Bridge with, <em>“Today we audit our mid-year profiles. We will compare our baseline August data with concrete evidence from our semester work on our Mid-Year Profile Audit Sheet.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-15 - Modeling empty labels vs. usable behavioral evidence", '''<p>Direct students' attention to the main display and model the difference between a superficial label and actionable evidence:</p><ul><li><strong>Non-Example (Vague Label):</strong> <em>“I am an artistic person and I am good at technology.”</em></li><li><strong>Exemplar (Concrete Behavioral Evidence):</strong> <em>“In our 2SW CAD drafting project, I chose to redesign the mechanical joint three times after my partner pointed out tolerance errors, and I enjoyed troubleshooting the 3D printer file.”</em></li><li>Guide students to analyze why the exemplar is powerful: It names a specific task, an authentic action, peer feedback, and observable problem-solving behavior.</li><li>Review the Four Evidence Categories: (1) Hands-on tasks you chose willingly, (2) Skills you improved through revision, (3) Team roles where you contributed effectively, and (4) Authentic feedback from teachers or peers.</li></ul>''')
                    + flow("#1f617a", "Minutes 15-35 - Independent mid-year evidence audit sprint (Two-Page Sheet)", '''<p>Students independently audit their semester work on the Mid-Year Profile Audit Sheet:</p><ul><li>Step 1 (Baseline Retrieval): Record their initial career cluster / assessment result from August (or baseline starting point).</li><li>Step 2 (Three Factual Evidence Anchors): Identify THREE specific projects, labs, or tasks completed during 1SW-3SW. For each, describe what they did and what it revealed about their strengths.</li><li>Step 3 (Pattern Recognition): Identify ONE consistent behavioral pattern running across those three examples (e.g., preference for structured systems, creative visual problem-solving, or human-centered advocacy).</li><li>Step 4 (Defensible Conclusion): Author a 2-3 sentence conclusion stating whether their August assessment still fits, has evolved, or requires a new direction.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 22): Check that students cite concrete projects/tasks from 1SW-3SW rather than generic character traits.<br>• Lap 2 (Minute 30): Verify students state a defensible conclusion grounded in their three evidence anchors.</li></ul>''')
                    + flow("#e3ad19", "Minutes 35-45 - Structured peer clarification &amp; evidence defense", '''<p>Elbow partners execute a 5-minute Clarification Protocol:</p><ul><li>Partner A reads their 3 evidence anchors and defensible conclusion.</li><li>Partner B asks ONE probing clarification question: <em>“Which project was the hardest for you, and how did your response to that challenge support your conclusion?”</em></li><li>Partners swap roles after 2 minutes. Partner A writes a visible refinement clarifying their conclusion.</li><li>Alternative Route: Students using the private written route record their self-clarification in writing.</li></ul>''')
                    + flow("#1f617a", "Minutes 45-50 - DOL check, collection, and class folder storage", '''<p>Collect the named Profile Audits and store them in the designated Period Tray.</p><ul><li>Remind students: <em>“Do not take these home! These audits will be returned on Day 5 to construct your Mid-Year Career Blueprint (Major 1).”</em></li><li><strong>Safe Trim:</strong> Trim whole-class sharing; fiercely protect the 3 concrete evidence anchors, defensible conclusion, and secure collection in the class folder.</li></ul>''')
                ),
                "MONITOR": "<p><strong>Lap 1, minute 8:</strong> verify an earlier result or clearly labeled current baseline. <strong>Lap 2, minute 18:</strong> check that each evidence item names an action, choice, task, feedback point, or result. If more than one third of the class writes broad preferences such as “I like technology,” pause for a two-minute second teach with the supplied model. If students are behind, trim the partner share to one clarifying question; protect the conclusion and collection. Do not score whether the student's interests changed in the direction an adult expected.</p>",
                "RESOURCES": "<p>Licensed FYF Rung 1 is embedded. H&amp;L, Xello, notebooks, and earlier work are optional evidence sources.</p>",
                "SUPPORT": "<p>Offer the evidence bank, sentence frames, oral rehearsal, and speech-to-text. The PDF gives multiple lines for every explanation.</p>",
                "FALLBACK": "<p>A new or absent student uses the current baseline inventory. No platform history is required. Collect the replacement or notebook version in the same class folder.</p>",
            },
            2: {
                "TITLE": "Career Iceberg and Goal",
                "SUBTITLE": "50 minutes · TEKS d(1)(A), d(8)(A)",
                "ALERT": "<strong>Workbook first.</strong> FYF pp. 6-8 and 283-284 are the normal route. Canvas annotation and the enlarged CCE packet replace the workbook when needed; students do not complete both.",
                "PREP": f'<ul><li><strong>Materials:</strong> one FYF workbook per student; optional colored pencils shared by table.</li><li><strong>Print:</strong> zero by default. Print the {file_link(files["ICEBERG"]["id"], "four-page enlarged route")} only for students using that replacement.</li><li><strong>Devices:</strong> zero for the workbook route; one per student only for annotation, typed, media, or optional source access.</li><li>Project the licensed FYF model. Students keep workbook pages; collect only the alternate Canvas or paper response selected for that student.</li></ul>',
                "MODEL": "<p>Use the FYF sports iceberg. Above the waterline: trophy and first place. Below it: training, late nights, strategy, sacrifice, and support. Then model one career item: <strong>Architect visible result:</strong> finished building plan. <strong>Hidden requirement:</strong> repeated revisions after client feedback. Ask: Is “wears nice clothes” a useful hidden requirement? Why not?</p>",
                "EVIDENCE": "<p>Three visible items, eight hidden items across categories, two self-evidence links, one requirement, and one research question. Formative.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and the hidden work of success warm-up", '''<p>Welcome students, seat them with FYF pp. 6-8, and project the visible vs. hidden success prompt.</p><ul><li>Ask students: <em>“When you see a professional athlete hoist a championship trophy, an architect walk through a gleaming skyscraper, or a surgeon complete a complex operation, what percentage of their total career effort are you actually seeing on television or social media?”</em></li><li>Collect 2-3 student thoughts: Emphasize that the public only witnesses the top 10% (the visible outcome)—the trophy, the completed building, or the applause. The bottom 90% is hidden beneath the surface: thousands of hours of unseen practice, credentialing, regulatory exams, failed drafts, and personal sacrifice.</li><li>Bridge with, <em>“Every high-wage, high-skill career is an iceberg. Today we deconstruct the hidden demands of our target careers on FYF pp. 6-8 and author an authentic career goal on pp. 283-284.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-15 - Deconstructing the Career Iceberg model (FYF pp. 6-7)", '''<p>Guide students through the FYF pp. 6-7 Sports and Architecture Iceberg diagrams:</p><ul><li>Above the Waterline (Visible Outcomes): Finished blueprints, professional titles, salary paychecks, client handshakes.</li><li>Below the Waterline (Hidden Realities across Six Categories):<br>1. <strong>Required Technical Tools &amp; Equipment</strong> (e.g., CAD software, diagnostic monitors).<br>2. <strong>Educational &amp; Licensure Benchmarks</strong> (degrees, state board exams, continuing education).<br>3. <strong>Daily Unglamorous Responsibilities</strong> (documentation, compliance logs, supply management).<br>4. <strong>Physical &amp; Cognitive Demands</strong> (long standing shifts, intense mathematical precision, high-stress accountability).<br>5. <strong>Professional Support Networks</strong> (mentors, union representatives, professional associations).<br>6. <strong>Essential Soft Skills</strong> (conflict resolution, active listening, patience).</li><li>CFU Prompt: <em>“Why is 'wears a stylish business suit' NOT a useful hidden requirement? What makes a requirement functionally essential?”</em></li></ul>''')
                    + flow("#1f617a", "Minutes 15-33 - Mapping the Career Iceberg (FYF p. 8 / Enlarged Packet)", '''<p>Students construct their comprehensive Career Iceberg on FYF p. 8:</p><ul><li>Select ONE primary career of interest (grounded in 1SW-3SW exploration).</li><li>Above Waterline: Record THREE visible public outcomes of this career.</li><li>Below Waterline: Record at least EIGHT hidden requirements distributed across the six functional categories (at least one in each category).</li><li>Add TWO personal self-evidence connections: link two hidden requirements directly to personal habits or skills identified on Day 1.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 22): Ensure students populate all six below-waterline categories, not just education.<br>• Lap 2 (Minute 30): Verify students connect at least two hidden requirements to Day 1 audit evidence.</li></ul>''')
                    + flow("#e3ad19", "Minutes 33-45 - Authoring the actionable career goal (FYF pp. 283-284)", '''<p>Students turn their iceberg analysis into a structured career goal on FYF pp. 283-284:</p><ul><li>1. <strong>Target Career Direction:</strong> Formulate a clear career direction statement (recognizing it remains open to revision).</li><li>2. <strong>High-Stakes Hidden Requirement:</strong> Name the single most challenging hidden hurdle (e.g., 4-year degree debt, rigorous state licensure exam, or heavy physical stamina).</li><li>3. <strong>Immediate Research Question:</strong> Author ONE concrete, unanswered investigation question to verify with an industry professional or high school counselor.</li></ul>''')
                    + flow("#1f617a", "Minutes 45-50 - Changed perception exit check and workspace reset", '''<p>Students record their research question and one changed career perception on Canvas (or an exit card).</p><ul><li><strong>Safe Trim:</strong> Reduce oral share-out; fiercely protect the 8 hidden iceberg items, 2 self-evidence links, and actionable research question.</li></ul>''')
                ),
                "MONITOR": "<p><strong>Lap 1, build minute 6:</strong> check one skill, tool, training step, responsibility, challenge, and support. <strong>Lap 2, goal minute 6:</strong> check two Day 1 connections and one unanswered research question. If students list only visible products, pause and sort the supplied architect examples. If time slips, reduce the final share-out; do not cut the goal or research question. Accept uncertainty and do not force a permanent career commitment.</p>",
                "RESOURCES": "<p>FYF pp. 6-8 and 283-284 carry the core task. Canvas DocViewer annotation is an optional practice interaction and absence route.</p>",
                "SUPPORT": "<p>Use the point-of-use category list, typed labels, oral description, or enlarged packet. Drawing skill is not scored.</p>",
                "FALLBACK": "<p>If the workbook or annotation is unavailable, use upload, text, media, or paper. The Student Guide contains the model and full directions.</p>",
            },
            3: {
                "TITLE": "Xello Save Quick Sims",
                "SUBTITLE": "50 minutes · TEKS d(5)(D)",
                "ALERT": "<strong>Required Grade 7 task:</strong> protect Save quick sims. A completed sim contains a career, education, and at least one expense. Paper supports learning but does not count as completion.",
                "PREP": f'<ul><li><strong>Devices:</strong> one per student. Test ClassLink &gt; Xello &gt; Home &gt; The Real Game in a demo account.</li><li>Open the Completion Standards report to <strong>Save quick sims</strong>. The task has no prerequisite.</li><li>Post {file_link(files["DEEP"]["id"], "the two-page Quick Sim Decision Record")} for the debrief and no-device learning support. Print only for the assigned paper route.</li><li>Prepare a private list for complete, incomplete, access issue, and absent. Do not collect screenshots or publish students&#39; financial choices.</li></ul>',
                "MODEL": '<p><strong>Three-action model:</strong> add a career, add education, and add at least one expense. Ask, “What changed after the education choice? What changed after the expense?” A valid tradeoff names both a benefit and a cost.</p>',
                "EVIDENCE": "<p>Verify one saved Quick sim in the Completion Standards report and check one short career-education-expense tradeoff explanation. Formative; the explanation feeds the Day 5 Blueprint.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and financial life simulation launch", '''<p>Welcome students, have them log in to ClassLink, and project the financial decision launch prompt.</p><ul><li>Ask students: <em>“When you start living on your own after high school or college, which single financial decision will impact your monthly cash flow more than anything else: your choice of career, your student loan debt from education, or where you choose to live? Why?”</em></li><li>Collect 2-3 student predictions. Explain that adult living requires balancing income with lifestyle costs and debt obligations simultaneously.</li><li>Bridge with, <em>“Today we launch The Real Game in Xello and complete our official Grade 7 Completion Standards requirement: <strong>Save quick sims</strong>.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-15 - Three required actions for official task completion", '''<p>Walk students through the precise click-path in Xello on the main screen:</p><ul><li>Click Path: <strong>ClassLink &gt; Xello &gt; Home Screen &gt; The Real Game &gt; Quick Sims</strong>.</li><li>Explain the three mandatory actions required for the system to record official task completion:<br>1. <strong>Select ONE Career:</strong> Choose an occupation matching your current interests.<br>2. <strong>Select ONE Education Pathway:</strong> Associate degree, Bachelor's degree, Apprenticeship, or Military/On-the-Job Training.<br>3. <strong>Select at least ONE Essential Monthly Expense:</strong> Housing/rent, transportation, or personal living costs.</li><li>Demonstrate how the system calculates the monthly net cash flow and indicates whether the plan is in surplus or deficit.</li><li>Alert: <em>“Do not rapidly click through five different simulations. Build ONE thoughtful simulation, observe the financial impact of each choice, and click SAVE.”</em></li></ul>''')
                    + flow("#1f617a", "Minutes 15-40 - Hands-on simulation build &amp; financial stress-testing", '''<p>Students build, test, and save their Quick Sim in Xello:</p><ul><li>Inspect the financial effects of varying lifestyle choices: What happens to monthly surplus when upgrading from a shared apartment to a private luxury rental? What happens when student loan payments kick in?</li><li>Once the plan is balanced, click <strong>Save Quick Sim</strong> to record completion in the district portal.</li><li>Students open the Xello Quick Sim Decision Record (digital or paper) and record: (1) Selected career, (2) Education route, (3) Largest single monthly expense, (4) Final monthly balance, and (5) ONE significant financial tradeoff.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 22): Verify every student has entered The Real Game and added the three core components.<br>• Lap 2 (Minute 34): Confirm every student has clicked 'Save' and has begun writing their tradeoff explanation.</li></ul>''')
                    + flow("#e3ad19", "Minutes 40-45 - Authoring the benefit-and-cost tradeoff analysis", '''<p>Students construct their tradeoff statement on their Decision Record:</p><ul><li>Model the Tradeoff Formula: <em>“Choosing <strong>[Education/Career Route]</strong> resulted in <strong>[Specific Benefit]</strong>, but it required the trade-off of <strong>[Specific Cost / Financial Limitation]</strong>.”</em></li><li>Example: <em>“Choosing a four-year university engineering degree provided higher starting salary potential, but it created $450 in monthly loan repayments that limited my early housing options.”</em></li></ul>''')
                    + flow("#1f617a", "Minutes 45-50 - Completion verification report audit and device reset", '''<p>Teacher inspects the live Xello Completion Standards report on the teacher station.</p><ul><li>Verify green checkmarks for <strong>Save quick sims</strong>. Log any student with technical access issues for supervised recovery.</li><li>Have students log out of Xello and return devices to the charging cart.</li><li><strong>Safe Trim:</strong> Skip comparing multiple secondary simulations; fiercely protect the 3 required actions, clicking Save, the tradeoff sentence, and teacher report audit.</li></ul>''')
                ),
                "MONITOR": "<p><strong>Minute 8:</strong> every student is in The Real Game or has a named access barrier. <strong>Minute 18:</strong> each sim includes career, education, and one expense. <strong>Minute 35:</strong> students can name the choice that changed the plan most. <strong>Minute 45:</strong> the sim is saved and the tradeoff sentence is complete. If Xello fails, use the fixed Jordan scenario for learning and schedule the required save in supervised recovery. Do not count paper as completion.</p>",
                "RESOURCES": '<p><a href="https://help.xello.world/en-us/content/Knowledge-Base/Xello-6-12/The-Real-Game/Students-TRG.htm">Xello: How students work with The Real Game</a> · <a href="https://help.xello.world/en-us/content/Knowledge-Base/Xello-6-12/Completion-Standards/List-of-Tasks.htm">Xello Completion Standards task list</a></p>',
                "SUPPORT": "<p>Use the three-action checklist, read one choice at a time, oral rehearsal, and the bilingual point-of-use word bank. A peer may point but does not control another account.</p>",
                "FALLBACK": "<p>The fixed Jordan scenario carries the learning when Xello is unavailable. It does not create platform completion. Record the barrier and schedule a supervised Xello recovery window.</p>",
            },
            4: {
                "TITLE": "Irving Pathway and CTSO Decision",
                "SUBTITLE": "50 minutes · TEKS d(3)(F), d(8)(A)",
                "ALERT": "<strong>Private digital route by default.</strong> The four-page packet is the paper, enlarged, or independent route. Do not print both routes for every student.",
                "PREP": f'<ul><li><strong>Devices:</strong> one per student for the default private Canvas response and current district sources.</li><li><strong>Print:</strong> zero by default. Print the {file_link(files["PATHWAY"]["id"], "four-page paper or enlarged route")} only for students using that replacement.</li><li>Open the unpublished practice Assignment. Test the current Irving CTE, coursebook, School Choice, and TEA CTSO pages.</li><li>Project the supplied model and keep the embedded August 11 snapshot available. The teacher does not create separate pathway cards.</li></ul>',
                "MODEL": "<p><strong>Current-option model:</strong> “Architecture, Construction and Engineering at MacArthur is my first option because the current district page lists that exact program and it connects to my architect research. The exact ninth-grade course is <em>not yet confirmed</em>, so I would check the 2026-27 coursebook and ask my counselor. TSA may offer design and competition practice, but I still need to confirm whether a local chapter is available.” Identify the verified fact, the fit claim, the CTSO benefit, and the verification question.</p>",
                "EVIDENCE": "<p>Two or three current options, source labels, evidence-based comparison, one CTSO benefit, and one verification question. Formative and grade-neutral.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and informed pathway selection warm-up", '''<p>Welcome students, seat them with devices, and project the high school transition prompt.</p><ul><li>Ask students: <em>“In just over a year, you will step onto a high school campus with dozens of specialized CTE programs. Before you lock in your ninth-grade endorsement and course choices, what two verified facts and what key school professional must you consult before making a final commitment?”</em></li><li>Collect 2-3 student thoughts: Verified course prerequisites, campus location/transportation policies, and the campus academic counselor.</li><li>Bridge with, <em>“Course catalogs change and rumors are dangerous. Today we investigate authentic Irving ISD CTE programs, explore Career &amp; Technical Student Organizations (CTSOs), and make an informed pathway choice.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-17 - Navigating Irving ISD CTE hubs and state-recognized CTSOs", '''<p>Guide students through authentic district resources on the main display:</p><ul><li>1. <strong>Irving ISD High School CTE Hub:</strong> Explore programs across Cardwell Career Prep, Irving High, MacArthur High, Nimitz High, and Singley Academy.</li><li>2. <strong>2026-27 Course Descriptions:</strong> Trace an introductory ninth-grade course to its advanced practicum courses.</li><li>3. <strong>Understanding CTSOs:</strong> Introduce Career &amp; Technical Student Organizations recognized by the Texas Education Agency (TEA): TSA (Technology Student Association), SkillsUSA, DECA, HOSA (Future Health Professionals), FFA (Future Farmers of America), FCCLA, and TAFE.</li><li>Model the difference between a program and a credential: <em>“Enrolling in Automotive Technology is a CTE program pathway; ASE certification is the optional credential earned after passing state/industry exams.”</em></li><li>Model CTSO preparation benefit: <em>“Joining SkillsUSA provides real-world leadership development, competitive technical skills testing, and professional networking with regional employers.”</em></li></ul>''')
                    + flow("#1f617a", "Minutes 17-35 - Comparative pathway evaluation &amp; CTSO alignment sprint", '''<p>Students complete their Pathway and CTSO Decision in Canvas (or on the 4-page packet):</p><ul><li>Option 1 (Primary Choice): Name the exact CTE program, the campus offering it, and the introductory ninth-grade course.</li><li>Option 2 (Realistic Backup Choice): Name an alternative pathway aligned with secondary interests.</li><li>Document Source Attribution: Record the access date and verify the campus offering.</li><li>CTSO Connection: Identify the matching CTSO, cite ONE concrete leadership/preparation benefit, and formulate ONE question regarding local campus chapter availability.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 24): Verify students cite exact program names and campus locations from the district directory.<br>• Lap 2 (Minute 31): Ensure students label unverified course prerequisites as 'Not Yet Confirmed—Ask Counselor.'</li></ul>''')
                    + flow("#e3ad19", "Minutes 35-45 - Verifying enrollment questions and peer consultation", '''<p>Elbow partners review each other's pathway selections for 5 minutes:</p><ul><li>Partner checks: Did they name an introductory course? Is their CTSO connected to their industry cluster?</li><li>Students draft TWO specific, well-formulated questions to ask during their upcoming 8th-grade high school planning conference with their counselor.</li></ul>''')
                    + flow("#1f617a", "Minutes 45-50 - Submit private pathway decision and workspace reset", '''<p>Students submit their private Pathway Decision in Canvas and close browser tabs.</p><ul><li><strong>Safe Trim:</strong> Compare two pathways instead of three if time compresses; protect the primary choice, backup, CTSO benefit, counselor verification question, and clean submission.</li></ul>''')
                ),
                "MONITOR": "<p><strong>Lap 1, source minute 6:</strong> verify exact program and campus names plus access date. <strong>Lap 2, compare minute 10:</strong> check that the ranking uses evidence and that the CTSO line names a preparation benefit. If students treat a program as a credential or invent a chapter, pause on the supplied model and require “not yet confirmed.” If time slips, compare two options with every field; do not cut the CTSO benefit, verification question, or private submission.</p>",
                "RESOURCES": PATHWAY_SNAPSHOT + '<p><a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte">Irving ISD High School CTE</a> · <a href="https://www.irvingisd.net/departments-services/curriculum-and-instruction/middle-school-and-high-school-course-descriptions">2026-27 course descriptions</a> · <a href="https://www.irvingisd.net/schools/schools-of-choice">Irving ISD School Choice</a> · <a href="https://tea.texas.gov/student-readiness-and-high-school/college-career-and-military-prep/career-and-technical-education/career-and-technical-education-student-organizations">TEA CTSOs</a></p>',
                "SUPPORT": "<p>Compare two options with all evidence fields when reduced quantity is documented. Use the complete point-of-use frame, text-to-speech, or the paper route.</p>",
                "FALLBACK": "<p>If live sites fail, use the supplied snapshot and mark unverified facts as questions. No vendor unit or platform state is required.</p>",
            },
            5: {
                "TITLE": "Mid-Year Career Blueprint",
                "SUBTITLE": "50 minutes · TEKS d(1)(A), d(5)(D), d(8)(A)",
                "ALERT": "<strong>Major 1 is already mapped.</strong> The Assignment stays unpublished, is worth 100 points, and remains in Major Assessments (60%) so each teacher can publish it after cloning.",
                "PREP": f'<ul><li>Return each student&#39;s named Day 1 Audit. Make the Day 2 iceberg, Day 3 Quick Sim tradeoff, and Day 4 pathway decision available.</li><li><strong>Digital route:</strong> one device per student; post {file_link(files["BLUEPRINT"]["id"], "the three-page Blueprint")} and {file_link(files["RUBRIC"]["id"], "the student scoring guide")}; open the unpublished private Assignment.</li><li><strong>Paper route:</strong> print one three-page Blueprint per student using paper; the rubric may stay projected or in Canvas, so default rubric printing is zero.</li><li>Display the six evidence jobs before class. Keep the missing-artifact fallback box visible.</li></ul>',
                "MODEL": "<p><strong>Seven-sentence fictional model:</strong> “My earlier result suggested Creator. That still fits because I chose design tasks in three projects and revised them after feedback. In my Quick Sim, I chose an architect career, a four-year education route, and housing as my largest expense. The education route increased debt, while the career income supported more of the monthly plan; that tradeoff means I need to compare education cost with the work I want. Architecture, Construction and Engineering at MacArthur is my current Irving option because the district page lists that exact program. My backup is Digital Communications and Graphic Design. Within six weeks, I will ask my counselor which ninth-grade course starts the MacArthur pathway and record the answer.” Ask students to point to self-evidence, Quick Sim evidence, pathway evidence, backup, tradeoff, and next action.</p>",
                "EVIDENCE": "<p>Submit the Blueprint only. It synthesizes self, Quick Sim, pathway, backup, tradeoff, and next-action evidence. Major 1 is scored with the 16-point rubric and converted to 100 gradebook points.</p>",
                "FLOW": (
                    flow("#5a2d91", "Minutes 0-5 - Welcome and evidence-based revision warm-up", '''<p>Welcome students, distribute their named Day 1 Profile Audits, and project the Blueprint launch prompt.</p><ul><li>Ask students: <em>“What is the difference between quitting on a goal because it got hard versus revising a plan because you discovered new evidence about yourself and the real world?”</em></li><li>Collect 2-3 student thoughts: Quitting is driven by frustration or avoidance; evidence-based revision is mature strategic thinking based on authentic data.</li><li>Bridge with, <em>“Today is Major 1: The Mid-Year Career Blueprint! You will synthesize all five days of evidence into an executive career plan that connects who you are with where you are going.”</em></li></ul>''')
                    + flow("#4a9d2f", "Minutes 5-13 - Deconstructing the 16-point Blueprint rubric &amp; exemplar", '''<p>Display the Mid-Year Career Blueprint and review the six mandatory evidence jobs:</p><ul><li>Job 1: <strong>Self-Evidence &amp; Evolution:</strong> Compare August baseline to current mid-year behavioral evidence.</li><li>Job 2: <strong>Career Demands &amp; Reality:</strong> Reference the Day 2 hidden iceberg requirements.</li><li>Job 3: <strong>Quick Sim Financial Tradeoff:</strong> State the Day 3 career, education route, largest expense, and financial balance.</li><li>Job 4: <strong>Primary Irving ISD Pathway:</strong> State the exact high school program, campus, and introductory course.</li><li>Job 5: <strong>Strategic Backup Pathway:</strong> Identify a viable secondary option aligned with personal skills.</li><li>Job 6: <strong>Six-Week Immediate Action:</strong> Define a concrete action to execute within six weeks (who to ask, what to verify, and observable sign of completion).</li><li>Review the 16-point rubric bands (15-16 Masters, 13-14 Meets, 12 Approaches, 10-11 Needs Improvement).</li></ul>''')
                    + flow("#1f617a", "Minutes 13-35 - Authoring the Mid-Year Career Blueprint (Major 1 Sprint)", '''<p>Students independently draft their Mid-Year Career Blueprint (in Canvas or on the 3-Page Packet):</p><ul><li>Draft Sections 1-3 (Minutes 13-22): Synthesize Day 1 self-audit, Day 2 iceberg demands, and Day 3 Quick Sim financial data.</li><li>Draft Sections 4-6 (Minutes 22-35): Detail the primary Irving ISD pathway, backup direction, and 6-week counselor action step.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 18): Verify students integrate their actual Day 1 audit data and Day 3 Quick Sim numbers.<br>• Lap 2 (Minute 28): Confirm the six-week action specifies a concrete task, helper, and completion sign.</li></ul>''')
                    + flow("#e3ad19", "Minutes 35-45 - Rubric self-audit and iterative refinement", '''<p>Students evaluate their draft against the 16-point rubric:</p><ul><li>Score each of the four criteria (Self-Evidence, Financial Tradeoff, Pathway Reasoning, Next Action).</li><li>Identify their lowest-scoring section and execute a 3-minute targeted revision to elevate the evidence.</li><li>Conduct private teacher conferencing with students needing differentiated writing support.</li></ul>''')
                    + flow("#1f617a", "Minutes 45-50 - Submit Major 1 and 4SW Week 1 close", '''<p>Students submit their completed Blueprint in Canvas or hand in paper packets.</p><ul><li>Congratulate students on completing their Mid-Year Career Blueprint!</li><li><strong>Safe Trim:</strong> Eliminate oral presentations or peer review; fiercely protect all six evidence jobs, rubric self-audit, private submission, and workspace reset.</li></ul>''')
                ),
                "MONITOR": "<p><strong>Lap 1, build minute 8:</strong> check earlier/current self-evidence and one complete Quick Sim career-education-expense tradeoff. <strong>Lap 2, build minute 16:</strong> check current pathway evidence, backup, and tradeoff. <strong>Lap 3, review minute 4:</strong> check the six-week action for a specific action, helper, and completion sign. If a third of the class lacks a rubric criterion, pause for a three-minute whole-group repair using the supplied model. If time slips, remove partner review and use self-review only; never cut self-evidence, Quick Sim evidence, pathway reasoning, tradeoff, next action, or the five-minute private submission. Unfinished work uses the same private recovery route next class; it is not converted to homework by default.</p><p>Use the associated Canvas rubric: 15-16 Masters, 13-14 Meets, 12 Approaches, 10-11 Needs Improvement; below 10 follows campus policy. Score evidence and reasoning, not grammar, art, accent, or submission mode unless meaning is unclear.</p>",
                "RESOURCES": "<p>FYF p. 22 frames career planning as evidence, action, and revision. Days 1-4 provide source material; they are not separate required Major uploads. Xello stores the Quick Sim; students bring forward only the career, education, expense, and tradeoff evidence they choose.</p>",
                "SUPPORT": "<p>Use numbered sentence jobs, speech-to-text, teacher scribe, or media recording. The printable has full-width writing space matched to the requested response.</p>",
                "FALLBACK": "<p>A missing earlier artifact does not force a restart. Use the evidence already visible in the Blueprint. Canvas failure means paper or later upload without penalty. An unfinished in-class Blueprint returns through the same private assignment or paper route during the next teacher-provided recovery window.</p>",
            },
        }

        day_names = {1:"Profile Audit",2:"Career Iceberg",3:"Xello Save Quick Sims",4:"Pathway and CTSO Decision",5:"Mid-Year Career Blueprint"}
        pages, order = {}, []
        for day in range(1, 6):
            title = f"Day {day} · {day_names[day]}"
            order.append(("SubHeader", None, title))
            student_title = f"STUDENT: 4SW Wk1 Day {day} - {day_names[day]}"
            student_page = await upsert_page(client, student_title, render("4sw-wk1-student.html", {"COURSE_ID":COURSE_ID,"DAY":day,"MEDIA":media[day],**contracts[day],**student[day]}))
            teacher_title = f"TEACHER: 4SW Wk1 Day {day} Facilitator Guide"
            teacher_page = await upsert_page(client, teacher_title, render("4sw-wk1-teacher.html", {"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student_page["url"],**contracts[day],**teacher[day]}))
            order += [("Page",teacher_page["url"],teacher_title),("Page",student_page["url"],student_title)]
            pages[day] = {"teacher":teacher_page,"student":student_page}
            if day == 2:
                order.append(("Assignment",annotation["id"],ANNOTATION_TITLE))
            if day == 4:
                order.append(("Assignment",pathway_practice["id"],PATHWAY_TITLE))
            if day == 5:
                order.append(("Assignment",blueprint["id"],BLUEPRINT_TITLE))

        final_items = await reconcile_module_items(client, module["id"], order)
        module = await api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        modules = await paged(client, f"/courses/{COURSE_ID}/modules")
        if module.get("published") or len([entry for entry in modules if entry.get("name") == MODULE_NAME]) != 1:
            raise RuntimeError(f"Final module invariant failed: published={module.get('published')}")
        for day, pair in pages.items():
            for kind, page in pair.items():
                final_page = await api(client, "GET", f"/courses/{COURSE_ID}/pages/{page['url']}")
                if final_page.get("published"):
                    raise RuntimeError(f"Day {day} {kind} page is published")
                pair[kind] = final_page
        annotation = await api(client, "GET", f"/courses/{COURSE_ID}/assignments/{annotation['id']}")
        pathway_practice = await api(client, "GET", f"/courses/{COURSE_ID}/assignments/{pathway_practice['id']}")
        blueprint = await api(client, "GET", f"/courses/{COURSE_ID}/assignments/{blueprint['id']}")
        for practice in (annotation, pathway_practice):
            if practice.get("published") or float(practice.get("points_possible") or 0) != 0 or practice.get("omit_from_final_grade") is not True:
                raise RuntimeError(f"Final practice invariant failed for {practice.get('name')!r}")
        if (
            blueprint.get("published")
            or float(blueprint.get("points_possible") or 0) != 100
            or blueprint.get("assignment_group_id") != major_group["id"]
            or blueprint.get("grading_type") != "points"
            or blueprint.get("omit_from_final_grade") is not False
            or RUBRIC_NOTE_MARKER not in (blueprint.get("description") or "")
        ):
            raise RuntimeError(f"Final Major invariant failed for {BLUEPRINT_TITLE!r}")
        print(json.dumps({
            "module":{"id":module["id"],"published":module["published"]},
            "annotation":{"id":annotation["id"],"published":annotation.get("published"),"submission_types":annotation.get("submission_types"),"annotatable_attachment_id":annotation.get("annotatable_attachment_id")},
            "pathway_practice":{"id":pathway_practice["id"],"published":pathway_practice.get("published"),"submission_types":pathway_practice.get("submission_types"),"grading_type":pathway_practice.get("grading_type"),"omit_from_final_grade":pathway_practice.get("omit_from_final_grade")},
            "blueprint":{"id":blueprint["id"],"published":blueprint.get("published"),"submission_types":blueprint.get("submission_types"),"grading_type":blueprint.get("grading_type"),"points_possible":blueprint.get("points_possible"),"assignment_group_id":blueprint.get("assignment_group_id"),"omit_from_final_grade":blueprint.get("omit_from_final_grade")},
            "support_folder":{"id":support_folder["id"],"locked":support_folder["locked"]},
            "visual_folders":{str(day):{"id":folder["id"],"locked":folder["locked"]} for day,folder in folders.items()},
            "files":{key:value["id"] for key,value in files.items()},
            "visuals":{str(day):{name:value["id"] for name,value in entries.items()} for day,entries in visuals.items()},
            "pages":{str(day):{kind:{"url":value["url"],"published":value["published"]} for kind,value in pair.items()} for day,pair in pages.items()},
            "items":[{"position":item["position"],"type":item["type"],"title":item["title"],"published":item.get("published")} for item in final_items],
        }, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
