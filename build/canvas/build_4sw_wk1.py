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
    3: ("fyf-rung-3-career-deep-dive.jpg", "fyf-rung-3-skills-check.jpg"),
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
    unlocked = [entry.get("display_name") or entry.get("filename") for entry in final if not entry.get("locked")]
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
    return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'


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
            3: image_tag(visuals[3]["fyf-rung-3-career-deep-dive.jpg"]["id"], "Find Your Future Rung 3 education, salary, and outlook prompts") + image_tag(visuals[3]["fyf-rung-3-skills-check.jpg"]["id"], "Find Your Future Rung 3 career skills check"),
            4: "",
            5: image_tag(visuals[5]["fyf-career-thinker-and-doer.jpg"]["id"], "Find Your Future Career Thinker and Doer reflection and career community prompts"),
        }

        contracts = {
            1: {"TOPIC": "Career Assessment", "OBJECTIVE": "Students will compare an earlier career-assessment or profile result with current evidence.", "TEKS": "d(1)(A)", "DOL": "Mid-Year Profile Audit.", "I_CAN": "compare an earlier career result with evidence from what I have done this year.", "SHOW": "complete a Mid-Year Profile Audit with an earlier result, three current facts, and a supported conclusion."},
            2: {"TOPIC": "Career Assessment", "OBJECTIVE": "Students will explain the visible and hidden work behind one career and name a current direction.", "TEKS": "d(1)(A), d(8)(A)", "DOL": "Career Iceberg and Goal in the FYF workbook, support packet, or Canvas annotation.", "I_CAN": "explain the visible and hidden work behind one career and name my current direction.", "SHOW": "complete a Career Iceberg and Goal in my workbook, on paper, or in Canvas."},
            3: {"TOPIC": "Career Research", "OBJECTIVE": "Students will document work, preparation, pay, and outlook for one career using labeled evidence.", "TEKS": "d(8)(B)", "DOL": "Career Deep Dive.", "I_CAN": "document career work, preparation, pay, and outlook without losing the source labels.", "SHOW": "complete the FYF Career Deep Dive and use one labeled fact to name a realistic first step."},
            4: {"TOPIC": "Extended Learning", "OBJECTIVE": "Students will compare current Irving ISD pathway options and explain one benefit of CTSO participation.", "TEKS": "d(3)(F), d(8)(A)", "DOL": "Private Pathway and CTSO Decision.", "I_CAN": "compare Irving ISD pathways and explain how one CTSO experience could help me prepare.", "SHOW": "submit a private Pathway and CTSO Decision with a source, comparison, benefit, and verification question."},
            5: {"TOPIC": "Career Planning", "OBJECTIVE": "Students will synthesize self, career, and pathway evidence into a current plan with a backup and next action.", "TEKS": "d(1)(A), d(8)(A), d(8)(B)", "DOL": "Mid-Year Career Blueprint.", "I_CAN": "use self, career, and pathway evidence to make a current plan with a backup and next action.", "SHOW": "submit one private Mid-Year Career Blueprint and revise it with the student scoring guide."},
        }

        student = {
            1: {"TITLE":"Mid-Year Profile Audit","PURPOSE":"Use current evidence to examine how your career thinking has changed or stayed the same.","TODAY":"<ul><li>review one earlier result or idea;</li><li>collect three current pieces of evidence;</li><li>defend one conclusion.</li></ul>","READY":f'<p><strong>Response home:</strong> use the front-and-back Mid-Year Profile Audit your teacher gives you. Write your name on it. Your teacher will collect it today and return it for the Day 5 Blueprint. <a href="/courses/{COURSE_ID}/files/{files["AUDIT"]["id"]}/preview">Open the same audit</a> only if you need a replacement or absence copy. H&amp;L, Xello, and earlier portfolio work are optional evidence sources; a private screenshot is not required.</p>',"LANGUAGE":'<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> evidence = a specific result, choice, task, or experience · pattern = what repeats · supports = agrees with · complicates = adds another side.</p><p><strong>Use this frame:</strong> My earlier result said ___. Current evidence shows ___ and ___. This supports, complicates, or changes the result because ___.</p></div>',"STEPS":step(1,"Choose the earlier result","<p>Record one earlier assessment result, work value, Building Block, career idea, or clearly labeled current baseline.</p>")+step(2,"Collect three pieces of evidence","<p>Use specific activities, choices, feedback, or profile results from different sources.</p>")+step(3,"Analyze the pattern","<p>Decide whether the evidence supports, complicates, or changes the earlier result. Explain why.</p>"),"EXIT":"<p>What is one conclusion you can defend now, and what evidence supports it? Put the completed audit in the class collection folder before leaving.</p>","DONE":"<ul><li>one baseline;</li><li>three specific pieces of evidence;</li><li>one pattern;</li><li>one defensible conclusion;</li><li>name on the audit and audit handed in for Day 5.</li></ul>","SUPPORT":"<p>evidence = evidencia · earlier = anterior · current = actual · pattern = patrón. Use the complete frame above and speak your explanation before writing.</p>","FALLBACK":"<p>If you were absent, print the audit or use a notebook with the same four section headings. If earlier evidence is missing, use today's self-evidence inventory and label it as your baseline. Give the completed work to your teacher so it can be returned on Day 5.</p>"},
            2: {"TITLE":"Career Iceberg and Goal","PURPOSE":"Show the visible and hidden work behind one career, then decide whether it remains a useful direction.","TODAY":"<ul><li>study an iceberg model;</li><li>label one career iceberg;</li><li>write a working career goal.</li></ul>","READY":f'<p><strong>Default route:</strong> use FYF pp. 6-8 and 283-284 in your workbook. Use {file_link(files["ICEBERG"]["id"], "the enlarged support packet")} or <a href="{annotation_url}">the Canvas annotation</a> only when the workbook is unavailable or you need that route. Do not complete both.</p>',"LANGUAGE":'<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Sort hidden work into:</strong> skills · tools or technology · education or training · responsibilities or challenges.</p><p><strong>Use this frame:</strong> One hidden requirement is ___. It strengthens, weakens, or complicates my interest because ___.</p></div>',"STEPS":step(1,"Read the model","<p>Use FYF pp. 6-7. Find what people see above the waterline and what the career requires below it.</p>")+step(2,"Build your iceberg","<p>On FYF p. 8, add at least three visible parts and eight hidden parts. Label each hidden part with one category from the blue box above.</p>")+step(3,"Set a working goal","<p>Use FYF pp. 283-284. Connect two Day 1 facts, one hidden requirement, and one research question. This is a current direction, not a permanent promise.</p>"),"EXIT":"<p>Name one hidden requirement that changed how you see the career. Does it strengthen, weaken, or complicate your interest?</p>","DONE":"<ul><li>three visible items;</li><li>eight hidden items across the labeled categories;</li><li>two self-evidence connections;</li><li>one research question.</li></ul>","SUPPORT":"<p>visible = visible · hidden = oculto · training = capacitación · responsibility = responsabilidad. Drawing skill is not scored.</p>","FALLBACK":"<p>The support packet, Canvas annotation, typed list, or audio response replaces the workbook route. The embedded images explain the task for an absent student.</p>"},
            3: {"TITLE":"Career Deep Dive","PURPOSE":"Research one career without losing the place, year, and meaning attached to a number.","TODAY":"<ul><li>identify daily work and preparation;</li><li>record pay and outlook accurately;</li><li>choose one realistic first step.</li></ul>","READY":f'<p><strong>Default route:</strong> use FYF pp. 285-286 and carry forward the career snapshot from pp. 283-284. Use {file_link(files["DEEP"]["id"], "the enlarged Deep Dive and source guide")} only when the workbook is unavailable or you need the added scaffold. Do not complete both.</p>',"LANGUAGE":'<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Keep four labels with pay:</strong> source · date · place · measure. A national median is not DFW starting pay.</p><p><strong>Use this frame:</strong> The requirement that needs the most planning is ___. The source says ___. My first step is ___.</p></div>',"STEPS":step(1,"Name the work","<p>Carry forward two common tasks and one work setting from FYF pp. 283-284. Put them beside the career name or in your notebook.</p>")+step(2,"Document preparation","<p>Complete the education, training, license, certification, and preparation-time fields.</p>")+step(3,"Label every number","<p>Complete FYF p. 286. Write source, date, place, and measure beside the pay box or in your notebook. Write the outlook years beside the outlook box.</p>")+step(4,"Plan from the evidence","<p>Name the requirement that needs the most planning and one first step.</p>"),"EXIT":"<p>Which requirement will take the most planning for you? Cite the evidence and name one first step.</p>","DONE":"<ul><li>tasks and condition;</li><li>preparation evidence;</li><li>fully labeled salary and outlook;</li><li>source title or URL;</li><li>one first step.</li></ul>","SUPPORT":"<p>median = mediana · outlook = perspectiva · source = fuente · measure = medida. Complete one source field at a time.</p>","FALLBACK":RN_CARD + '<p>Use this supplied card with the enlarged guide if a site or login does not work. Do not invent or relabel a number.</p>'},
            4: {"TITLE":"Irving Pathway and CTSO Decision","PURPOSE":"Compare current local options and explain how one student organization could help you prepare.","TODAY":"<ul><li>read current Irving ISD program information;</li><li>compare and rank pathways;</li><li>connect one CTSO benefit.</li></ul>","READY":f'<p><strong>Digital route:</strong> <a href="{pathway_practice_url}">open the private Pathway and CTSO Decision</a>. Use <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte">Irving ISD High School CTE</a>, the <a href="https://www.irvingisd.net/departments-services/curriculum-and-instruction/middle-school-and-high-school-course-descriptions">2026-27 coursebook page</a>, and the <a href="https://tea.texas.gov/student-readiness-and-high-school/college-career-and-military-prep/career-and-technical-education/career-and-technical-education-student-organizations">TEA CTSO page</a>. Use {file_link(files["PATHWAY"]["id"], "the four-page paper or enlarged route")} only when needed.</p>',"LANGUAGE":'<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> pathway = a sequence of related courses · prerequisite = a course or condition needed first · CTSO = a student organization connected to CTE.</p><p><strong>Use this frame:</strong> ___ is stronger for me right now because the district source shows ___. A CTSO could help me ___ by ___.</p></div>',"STEPS":step(1,"Record exact current names","<p>Capture the pathway or program, location when verified, one connection, and one course, requirement, or question.</p>")+step(2,"Compare before ranking","<p>Use fit and evidence, not popularity. It is acceptable to write “not yet confirmed.”</p>")+step(3,"Add a CTSO benefit","<p>Select a plausible organization and explain one specific preparation benefit. Confirm local chapter availability before claiming it exists.</p>")+step(4,"Submit privately",f'<p><a href="{pathway_practice_url}">Submit the structured text, file, or approved audio response</a>. This practice is grade-neutral.</p>'),"EXIT":"<p>Name your current first choice, one verified fact, one unanswered question, and one way a CTSO could help.</p>","DONE":"<ul><li>three current options, or two with support;</li><li>sources and access date;</li><li>evidence-based ranking;</li><li>one CTSO benefit;</li><li>one verification question.</li></ul>","SUPPORT":"<p>pathway = trayectoria · requirement = requisito · verified = verificado · organization = organización. Read one program card at a time.</p>","FALLBACK":PATHWAY_SNAPSHOT + '<p>If a site is unavailable, use this supplied snapshot and mark every course, prerequisite, access step, or local chapter detail that still needs verification. The paper packet is the complete no-platform response route.</p>'},
            5: {"TITLE":"Mid-Year Career Blueprint","PURPOSE":"Turn the week's evidence into a current plan, a backup direction, and one next action.","TODAY":"<ul><li>gather Days 1-4 evidence;</li><li>build a private Blueprint;</li><li>self-score and revise.</li></ul>","READY":f'<p>Open {file_link(files["BLUEPRINT"]["id"], "the three-page Mid-Year Career Blueprint")} and {file_link(files["RUBRIC"]["id"], "the student scoring guide")}. You submit the Blueprint only. Days 1-4 are evidence sources, not four extra uploads.</p>',"LANGUAGE":'<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Blueprint jobs:</strong> self-evidence · career evidence · pathway · backup · trade-off · next action.</p><p><strong>Use this frame:</strong> My current direction is ___ because ___. My backup is ___. One trade-off is ___. Within six weeks, I will ___.</p></div>',"STEPS":step(1,"Gather","<p>Bring forward self-evidence, the iceberg insight, career preparation and data, and one verified pathway fact.</p>")+step(2,"Build","<p>Name a current direction, backup, next six-week action, and question for a trusted adult or professional.</p>")+step(3,"Self-score and revise","<p>Check all four criteria. Revise one weak area before you submit.</p>")+step(4,"Submit privately",f'<p><a href="{blueprint_url}">Open the private Blueprint assignment</a>, or hand in the paper copy.</p>'),"EXIT":"<p>My plan is stronger now because I used evidence from ____ to change or confirm ____.</p>","DONE":"<ul><li>all Blueprint jobs;</li><li>source labels retained;</li><li>specific backup and next action;</li><li>private scoring-guide check;</li><li>one visible revision.</li></ul>","SUPPORT":"<p>blueprint = plan · backup = plan alternativo · next action = próxima acción. Text, speech-to-text, and media recording answer the same sentence jobs.</p>","FALLBACK":"<p>Use the fallback evidence box if an earlier artifact is missing. Canvas failure does not change the task or score; submit paper or upload later.</p>"},
        }

        teacher = {
            1: {"TITLE":"Mid-Year Profile Audit","SUBTITLE":"50 minutes · TEKS d(1)(A)","ALERT":"<strong>Do not require a retake.</strong> Students analyze earlier evidence against current evidence; a private screenshot is never required.","PREP":f'<ul><li><strong>Print:</strong> one {file_link(files["AUDIT"]["id"], "Mid-Year Profile Audit")} per student, double-sided: two pages on one sheet. This is the default response home.</li><li><strong>Devices:</strong> zero required for the core; one per student only when students choose to consult existing H&amp;L, Xello, or portfolio evidence.</li><li>Set one labeled Day 1-to-Day 5 class folder or period tray. Collect the named audits today and return them on Day 5.</li><li>Keep the no-prior-evidence baseline route ready for new or absent students.</li></ul>',"MODEL":"<p><strong>Label:</strong> “I am a Helper.” <strong>Usable evidence:</strong> “I chose patient-care and teaching tasks in three activities, and I liked explaining directions to a partner.” <strong>Conclusion:</strong> “The Helper result still fits, but my troubleshooting work shows an Analyzer side too.” Ask students which words make the second statement evidence rather than a label.</p>","EVIDENCE":"<p>One earlier result or baseline, three specific current facts, one pattern, and one defensible conclusion on the named Audit. Formative; collect and retain for Day 5.</p>","FLOW":flow("#5a2d91","Warm-up · 5","Name one changed interest and its cause.")+flow("#4a9d2f","Evidence model and CFU · 10","Sort two examples as label or evidence; require the specific action, choice, or feedback that makes evidence usable.")+flow("#1f617a","Audit · 20","Record the baseline, three facts, pattern, and conclusion.")+flow("#e3ad19","Discuss · 10","Use the complete frame in a partner exchange or private written route; partner asks one clarifying question.")+flow("#1f617a","Exit and collect · 5","Defend one conclusion, write the student's name, and place the Audit in the period folder."),"MONITOR":"<p><strong>Lap 1, minute 8:</strong> verify an earlier result or clearly labeled current baseline. <strong>Lap 2, minute 18:</strong> check that each evidence item names an action, choice, task, feedback point, or result. If more than one third of the class writes broad preferences such as “I like technology,” pause for a two-minute second teach with the supplied model. If students are behind, trim the partner share to one clarifying question; protect the conclusion and collection. Do not score whether the student's interests changed in the direction an adult expected.</p>","RESOURCES":"<p>Licensed FYF Rung 1 is embedded. H&amp;L, Xello, notebooks, and earlier work are optional evidence sources.</p>","SUPPORT":"<p>Offer the evidence bank, sentence frames, oral rehearsal, and speech-to-text. The PDF gives multiple lines for every explanation.</p>","FALLBACK":"<p>A new or absent student uses the current baseline inventory. No platform history is required. Collect the replacement or notebook version in the same class folder.</p>"},
            2: {"TITLE":"Career Iceberg and Goal","SUBTITLE":"50 minutes · TEKS d(1)(A), d(8)(A)","ALERT":"<strong>Workbook first.</strong> FYF pp. 6-8 and 283-284 are the normal route. Canvas annotation and the enlarged CCE packet replace the workbook when needed; students do not complete both.","PREP":f'<ul><li><strong>Materials:</strong> one FYF workbook per student; optional colored pencils shared by table.</li><li><strong>Print:</strong> zero by default. Print the {file_link(files["ICEBERG"]["id"], "four-page enlarged route")} only for students using that replacement.</li><li><strong>Devices:</strong> zero for the workbook route; one per student only for annotation, typed, media, or optional source access.</li><li>Project the licensed FYF model. Students keep workbook pages; collect only the alternate Canvas or paper response selected for that student.</li></ul>',"MODEL":"<p>Use the FYF sports iceberg. Above the waterline: trophy and first place. Below it: training, late nights, strategy, sacrifice, and support. Then model one career item: <strong>Architect visible result:</strong> finished building plan. <strong>Hidden requirement:</strong> repeated revisions after client feedback. Ask: Is “wears nice clothes” a useful hidden requirement? Why not?</p>","EVIDENCE":"<p>Three visible items, eight hidden items across categories, two self-evidence links, one requirement, and one research question. Formative.</p>","FLOW":flow("#5a2d91","Warm-up · 5","What work does success hide?")+flow("#4a9d2f","Model and CFU · 10","Use FYF pp. 6-7; students classify four items as visible or hidden and defend one choice.")+flow("#1f617a","Build · 18","Use FYF p. 8 or the selected equal replacement route to label the iceberg.")+flow("#e3ad19","Goal · 12","Use FYF pp. 283-284, Day 1 evidence, and one research question.")+flow("#1f617a","Exit and reset · 5","Explain one changed perception, close devices, and return shared supplies."),"MONITOR":"<p><strong>Lap 1, build minute 6:</strong> check one skill, tool, training step, responsibility, challenge, and support. <strong>Lap 2, goal minute 6:</strong> check two Day 1 connections and one unanswered research question. If students list only visible products, pause and sort the supplied architect examples. If time slips, reduce the final share-out; do not cut the goal or research question. Accept uncertainty and do not force a permanent career commitment.</p>","RESOURCES":"<p>FYF pp. 6-8 and 283-284 carry the core task. Canvas DocViewer annotation is an optional practice interaction and absence route.</p>","SUPPORT":"<p>Use the point-of-use category list, typed labels, oral description, or enlarged packet. Drawing skill is not scored.</p>","FALLBACK":"<p>If the workbook or annotation is unavailable, use upload, text, media, or paper. The Student Guide contains the model and full directions.</p>"},
            3: {"TITLE":"Career Deep Dive","SUBTITLE":"50 minutes · TEKS d(8)(B)","ALERT":"<strong>Workbook first.</strong> FYF pp. 285-286 carry the task, with work evidence carried forward from pp. 283-284. Students add source, date, place, and measure beside the pay field or in a notebook. The CCE guide is the enlarged no-workbook route.","PREP":f'<ul><li><strong>Materials:</strong> one FYF workbook and one device per student; one projected copy of the supplied Registered Nurse card.</li><li><strong>Print:</strong> zero by default. Print the {file_link(files["DEEP"]["id"], "four-page enlarged guide")} only for students using the no-workbook or added-scaffold route.</li><li>Open FYF pp. 283-286 and test the selected sources. The dated card below is ready; the teacher does not create another model.</li><li>Students keep the Deep Dive for Day 5. End with tabs closed and the device returned to its assigned charging or storage location.</li></ul>',"MODEL":RN_CARD + '<p>Point to the four pay labels: <strong>source</strong> BLS OOH, <strong>date</strong> May 2024 data/accessed August 11, 2026, <strong>place</strong> U.S., <strong>measure</strong> median annual wage. Then point to the projection years. Ask which label prevents students from calling this DFW starting pay.</p>',"EVIDENCE":"<p>Tasks, work condition, preparation, license or certification when applicable, fully labeled salary and outlook, source, and first step. Formative; students retain it for Day 5.</p>","FLOW":flow("#5a2d91","Warm-up · 5","Label place, year, and measure.")+flow("#4a9d2f","Source model and CFU · 10","Read the supplied card; students identify the four wage labels and the projection years.")+flow("#1f617a","Deep dive · 25","Use FYF pp. 285-286 and carried-forward pp. 283-284 work evidence to research and record.")+flow("#e3ad19","Evidence check · 5","Circle one complete label set and repair one incomplete claim.")+flow("#1f617a","Exit and close · 5","Plan from one requirement, save work, and close source tabs."),"MONITOR":"<p><strong>Lap 1, minute 8:</strong> verify the exact career title and preparation source. <strong>Lap 2, minute 18:</strong> check every number for source, date, place, measure, and projection years when applicable. If one third of the class confuses median with starting pay or national with local, project the supplied card and relabel it together. If students are behind, make the partner label check independent; protect the source labels, first step, and exit response. Reject unlabeled numbers, not student preferences.</p>","RESOURCES":RN_CARD + '<p>FYF and district-licensed Xello or H&amp;L are the first evidence sources. <a href="https://www.bls.gov/ooh/">BLS Occupational Outlook Handbook</a> is a national cross-check. Keep competing measures separate.</p>',"SUPPORT":"<p>Read one source field at a time, pre-highlight labels, and offer the fixed card or enlarged guide. Students may rehearse the exit response aloud.</p>","FALLBACK":"<p>The supplied dated card plus enlarged guide is the complete no-login and no-workbook route.</p>"},
            4: {"TITLE":"Irving Pathway and CTSO Decision","SUBTITLE":"50 minutes · TEKS d(3)(F), d(8)(A)","ALERT":"<strong>Private digital route by default.</strong> The four-page packet is the paper, enlarged, or independent route. Do not print both routes for every student.","PREP":f'<ul><li><strong>Devices:</strong> one per student for the default private Canvas response and current district sources.</li><li><strong>Print:</strong> zero by default. Print the {file_link(files["PATHWAY"]["id"], "four-page paper or enlarged route")} only for students using that replacement.</li><li>Open the unpublished practice Assignment. Test the current Irving CTE, coursebook, School Choice, and TEA CTSO pages.</li><li>Project the supplied model and keep the embedded August 11 snapshot available. The teacher does not create separate pathway cards.</li></ul>',"MODEL":"<p><strong>Current-option model:</strong> “Architecture, Construction and Engineering at MacArthur is my first option because the current district page lists that exact program and it connects to my architect research. The exact ninth-grade course is <em>not yet confirmed</em>, so I would check the 2026-27 coursebook and ask my counselor. TSA may offer design and competition practice, but I still need to confirm whether a local chapter is available.” Identify the verified fact, the fit claim, the CTSO benefit, and the verification question.</p>","EVIDENCE":"<p>Two or three current options, source labels, evidence-based comparison, one CTSO benefit, and one verification question. Formative and grade-neutral.</p>","FLOW":flow("#5a2d91","Warm-up · 5","Name two facts and one person needed before choosing.")+flow("#4a9d2f","Current source route and CFU · 12","Follow one program from district page to course question; classify program, course, certification, and unanswered detail.")+flow("#1f617a","Compare · 18","Compare two or three options using fit and evidence.")+flow("#e3ad19","CTSO connection · 10","Add one specific preparation benefit and one local-availability check.")+flow("#1f617a","Exit and submit · 5","Submit the private choice, verified fact, question, and benefit; close tabs."),"MONITOR":"<p><strong>Lap 1, source minute 6:</strong> verify exact program and campus names plus access date. <strong>Lap 2, compare minute 10:</strong> check that the ranking uses evidence and that the CTSO line names a preparation benefit. If students treat a program as a credential or invent a chapter, pause on the supplied model and require “not yet confirmed.” If time slips, compare two options with every field; do not cut the CTSO benefit, verification question, or private submission.</p>","RESOURCES":PATHWAY_SNAPSHOT + '<p><a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte">Irving ISD High School CTE</a> · <a href="https://www.irvingisd.net/departments-services/curriculum-and-instruction/middle-school-and-high-school-course-descriptions">2026-27 course descriptions</a> · <a href="https://www.irvingisd.net/schools/schools-of-choice">Irving ISD School Choice</a> · <a href="https://tea.texas.gov/student-readiness-and-high-school/college-career-and-military-prep/career-and-technical-education/career-and-technical-education-student-organizations">TEA CTSOs</a></p>',"SUPPORT":"<p>Compare two options with all evidence fields when reduced quantity is documented. Use the complete point-of-use frame, text-to-speech, or the paper route.</p>","FALLBACK":"<p>If live sites fail, use the supplied snapshot and mark unverified facts as questions. No vendor unit or platform state is required.</p>"},
            5: {"TITLE":"Mid-Year Career Blueprint","SUBTITLE":"50 minutes · TEKS d(1)(A), d(8)(A), d(8)(B)","ALERT":"<strong>Major 1 is already mapped.</strong> The Assignment stays unpublished, is worth 100 points, and remains in Major Assessments (60%) so each teacher can publish it after cloning.","PREP":f'<ul><li>Return each student&#39;s named Day 1 Audit. Place Days 2-4 workbook pages or response files where students can reach them.</li><li><strong>Digital route:</strong> one device per student; post {file_link(files["BLUEPRINT"]["id"], "the three-page Blueprint")} and {file_link(files["RUBRIC"]["id"], "the student scoring guide")}; open the unpublished private Assignment.</li><li><strong>Paper route:</strong> print one three-page Blueprint per student using paper; the rubric may stay projected or in Canvas, so default rubric printing is zero.</li><li>Display the six evidence jobs before class. Keep the missing-artifact fallback box visible.</li></ul>',"MODEL":"<p><strong>Seven-sentence fictional model:</strong> “My earlier result suggested Creator. That still fits because I chose design tasks in three projects and revised them after feedback. My current direction is architect; BLS reports a May 2024 U.S. median annual wage of $96,690 and 4% U.S. growth from 2024-2034. Architecture, Construction and Engineering at MacArthur is my current Irving option because the district page lists that exact program. My backup is Digital Communications and Graphic Design. One trade-off is that the licensed-architect route includes a degree, experience, and an exam, so I still need to decide whether that preparation fits me. Within six weeks, I will ask my counselor which ninth-grade course starts the MacArthur pathway and record the answer.” Ask students to point to self-evidence, career evidence, pathway evidence, backup, trade-off, and next action.</p>","EVIDENCE":"<p>Submit the Blueprint only. It synthesizes self, career, pathway, backup, trade-off, and next action evidence. Major 1, scored with the 16-point rubric and converted to 100 gradebook points.</p>","FLOW":flow("#5a2d91","Warm-up · 5","Distinguish evidence-based revision from quitting.")+flow("#4a9d2f","Career thinker and model · 8","Use FYF p. 22 and locate all six evidence jobs in the supplied model.")+flow("#1f617a","Blueprint · 22","Checkpoint at minute 8: self and career evidence; minute 15: pathway and backup; minute 22: trade-off and next action.")+flow("#e3ad19","Review · 10","Self-review every rubric criterion, then use teacher, source-label partner, or audio rehearsal as needed.")+flow("#1f617a","Submit · 5","Complete the private exit sentence, submit once, and return paper sources."),"MONITOR":"<p><strong>Lap 1, build minute 8:</strong> check earlier/current self-evidence and one labeled career fact. <strong>Lap 2, build minute 16:</strong> check current pathway evidence, backup, and trade-off. <strong>Lap 3, review minute 4:</strong> check the six-week action for a specific action, helper, and completion sign. If a third of the class lacks a rubric criterion, pause for a three-minute whole-group repair using the supplied model. If time slips, remove partner review and use self-review only; never cut self-evidence, career evidence, pathway reasoning, trade-off, next action, or the five-minute private submission. Unfinished work uses the same private recovery route next class; it is not converted to homework by default.</p><p>Use the associated Canvas rubric: 15-16 Masters, 13-14 Meets, 12 Approaches, 10-11 Needs Improvement; below 10 follows campus policy. Score evidence and reasoning, not grammar, art, accent, or submission mode unless meaning is unclear.</p>","RESOURCES":"<p>FYF p. 22 frames career planning as evidence, action, and revision. Days 1-4 provide source material; they are not separate required Major uploads. Model sources: BLS Architects, Irving ISD High School CTE, accessed August 11, 2026.</p>","SUPPORT":"<p>Use numbered sentence jobs, speech-to-text, teacher scribe, or media recording. The printable has full-width writing space matched to the requested response.</p>","FALLBACK":"<p>A missing earlier artifact does not force a restart. Use the evidence already visible in the Blueprint. Canvas failure means paper or later upload without penalty. An unfinished in-class Blueprint returns through the same private assignment or paper route during the next teacher-provided recovery window.</p>"},
        }

        day_names = {1:"Profile Audit",2:"Career Iceberg",3:"Career Deep Dive",4:"Pathway and CTSO Decision",5:"Mid-Year Career Blueprint"}
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
