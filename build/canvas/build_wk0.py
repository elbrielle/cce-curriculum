"""Build the complete unpublished Week 0 teacher/student Canvas module.

Run with a Canvas token on stdin. The token is never stored or printed.
"""

import asyncio
import json
import mimetypes
import re
import sys
from pathlib import Path

import httpx

from lesson_contracts import contract_html, load_contracts

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
MODULE_ID = 542880
MODULE_NAME = "1SW Wk0: Classroom Routines and Career Self-Discovery"
MINOR_TITLE = "MINOR 1: My Career Journey Reflection"
MINOR_GROUP = "Minor Assessments (40%)"
RUBRIC_NOTE_MARKER = 'data-cce-rubric-note="cce-advisory-rubric-v1"'
MINOR_SUBMISSION_TYPES = frozenset({"online_upload", "online_text_entry"})
LEGACY_MINOR_SUBMISSION_TYPES = frozenset(
    {"online_upload", "online_text_entry", "media_recording"}
)
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).resolve().parent / "templates"
ASSET_ROOT = ROOT / "cce-curriculum/resources/canvas-licensed/1sw/wk0"
DECK_ROOT = ROOT / "cce-curriculum/resources/avid-reference/source/derived"
SUPPORT_UPLOADS = {
    "cce-week1-day1-source-grounded.pptx": DECK_ROOT / "cce-week1-day1-source-grounded.pptx",
    "cce-week1-day2-source-grounded.pptx": DECK_ROOT / "cce-week1-day2-source-grounded.pptx",
    "cce-week1-day3-source-grounded.pptx": DECK_ROOT / "cce-week1-day3-source-grounded.pptx",
    "cce-week1-day4-source-grounded.pptx": DECK_ROOT / "cce-week1-day4-source-grounded.pptx",
    "cce-week1-day5-source-grounded.pptx": DECK_ROOT / "cce-week1-day5-source-grounded.pptx",
    "cce-first-week-goal-setting.pdf": ROOT / "docs/resources/worksheets/cce-first-week-goal-setting.pdf",
    "cce-first-week-goal-setting.docx": ROOT / "docs/resources/worksheets/cce-first-week-goal-setting.docx",
    "building-blocks-word-bank.pdf": ROOT / "docs/resources/worksheets/building-blocks-word-bank.pdf",
    "building-blocks-word-bank-bilingual.pdf": ROOT / "docs/resources/worksheets/building-blocks-word-bank-bilingual.pdf",
    "my-career-journey.pdf": ROOT / "docs/resources/worksheets/my-career-journey.pdf",
    "my-career-journey-stems.pdf": ROOT / "docs/resources/worksheets/my-career-journey-stems.pdf",
    "my-career-journey-bilingual.pdf": ROOT / "docs/resources/worksheets/my-career-journey-bilingual.pdf",
    "wk0-career-journey-rubric.pdf": ROOT / "docs/resources/worksheets/wk0-career-journey-rubric.pdf",
}
GOOGLE_DECK_COPY_URLS = {
    1: "https://docs.google.com/presentation/d/1xFcSPWu2qyQnNcihzHFpubHbVU_MCT1bX3fjEq-NQQQ/copy",
    2: "https://docs.google.com/presentation/d/13hsWv5_pShfI0bzmxAgaLLREGLGvM_Nwscpnph5WLKo/copy",
    3: "https://docs.google.com/presentation/d/1UX3uGRnXlVI8TW1wbJAlS28pXy4hyfQnbvillK7xRdk/copy",
    4: "https://docs.google.com/presentation/d/1aQm3ndpwRZ09E_jJNjzIZ46GaNpdWEC8FY2Er7Y90y4/copy",
    5: "https://docs.google.com/presentation/d/1NCK6fm2PLEI1w-fJAKqF5moIloAVN1oq0Sg2FKRK49c/copy",
}
GOOGLE_GOAL_COPY_URL = "https://docs.google.com/document/d/1rb8sHX56FYPeddRX-QX0_YG-bD7FrZZpQnh06q0r9w8/copy"
VISUAL_FILES = {
    2: (
        "irving-isd-ccmr-programs-of-study.png",
        "six-core-personality-types.png",
        "open-hats-and-ladders-discover-your-core.png",
    ),
    3: (
        "my-building-blocks-introduction.png",
        "my-building-blocks-inventory.png",
        "my-building-blocks-skills.png",
        "open-hats-and-ladders-discover-your-work-values.png",
    ),
    4: ("building-a-career-community.png",),
    5: ("perks-and-quirks-career-tables.png", "perks-and-quirks-introduction.png"),
}

WEEK_CONTRACTS = {
    row.day: row for row in load_contracts() if row.week == "1SW Wk0"
}


def preflight():
    required = [
        *(TEMPLATES / f"wk0-day{day}-{role}.html" for day in (1, 2, 3, 4, 5) for role in ("teacher", "student")),
        *SUPPORT_UPLOADS.values(),
        *(ASSET_ROOT / f"day{day}" / name for day, names in VISUAL_FILES.items() for name in names),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"1SW Wk0 local preflight failed; missing={missing}")
    if sorted(WEEK_CONTRACTS) != [1, 2, 3, 4, 5]:
        raise RuntimeError(
            f"1SW Wk0 contract preflight failed; days={sorted(WEEK_CONTRACTS)}"
        )


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower().replace("&", "and")).strip("-")


async def api(client, method, path, *, data=None, params=None):
    response = await client.request(method, f"{BASE}/api/v1{path}", data=data, params=params)
    response.raise_for_status()
    return response.json() if response.content else None


async def paged(client, path, params=None):
    results, url = [], f"{BASE}/api/v1{path}"
    query = {"per_page": 100, **(params or {})}
    while url:
        response = await client.get(url, params=query)
        response.raise_for_status()
        results.extend(response.json())
        url = response.links.get("next", {}).get("url")
        query = None
    return results


async def ensure_folder(client, folder_path):
    current, folder = "", None
    for name in folder_path.split("/")[1:]:
        target = f"{current}/{name}".strip("/")
        encoded = httpx.URL("/" + target).raw_path.decode("ascii").lstrip("/")
        response = await client.get(f"{BASE}/api/v1/courses/{COURSE_ID}/folders/by_path/{encoded}")
        if response.status_code == 200 and response.json():
            folder = response.json()[-1]
        else:
            parent = "course files" + (f"/{current}" if current else "")
            folder = await api(client, "POST", f"/courses/{COURSE_ID}/folders", data={"name": name, "parent_folder_path": parent, "locked": "true"})
        current = target
    if folder and not folder.get("locked"):
        folder = await api(client, "PUT", f"/folders/{folder['id']}", data={"locked": "true"})
    if folder:
        folder = await api(client, "GET", f"/folders/{folder['id']}")
    if not folder or folder.get("locked") is not True:
        raise RuntimeError(f"Canvas folder did not remain locked: {folder_path}")
    return folder


async def upload(client, path, folder_path):
    init = await api(client, "POST", f"/courses/{COURSE_ID}/files", data={"name": path.name, "parent_folder_path": folder_path, "on_duplicate": "overwrite"})
    response = await client.post(init["upload_url"], data=init["upload_params"], files={"file": (path.name, path.read_bytes(), mimetypes.guess_type(path.name)[0] or "application/octet-stream")}, follow_redirects=True)
    response.raise_for_status()
    uploaded = response.json()
    if uploaded.get("locked") is not True:
        uploaded = await api(client, "PUT", f"/files/{uploaded['id']}", data={"locked": "true"})
    if uploaded.get("locked") is not True:
        raise RuntimeError(f"Canvas file did not remain locked: {path.name}")
    return uploaded


async def lock_folder_files(client, folder, required_names=()):
    current = await api(client, "GET", f"/folders/{folder['id']}")
    if current.get("locked") is not True:
        current = await api(client, "PUT", f"/folders/{folder['id']}", data={"locked": "true"})
    files = await paged(client, f"/folders/{folder['id']}/files")
    for file in files:
        if file.get("locked") is not True:
            await api(client, "PUT", f"/files/{file['id']}", data={"locked": "true"})
    current = await api(client, "GET", f"/folders/{folder['id']}")
    verified = await paged(client, f"/folders/{folder['id']}/files")
    names = {file.get("display_name") or file.get("filename") for file in verified}
    missing = set(required_names) - names
    unlocked = [file.get("id") for file in verified if file.get("locked") is not True]
    if current.get("locked") is not True or missing or unlocked:
        raise RuntimeError(
            f"1SW Wk0 folder invariant failed for {folder['id']}: "
            f"missing={sorted(missing)} unlocked={unlocked}"
        )
    return current, verified


def resolve_folder_files(files, names_by_key):
    resolved = {}
    for key, display_name in names_by_key.items():
        matches = [
            file
            for file in files
            if (file.get("display_name") or file.get("filename")) == display_name
        ]
        if len(matches) != 1:
            raise RuntimeError(
                f"Expected one Wk0 support file named {display_name!r} in the exact locked folder; "
                f"found {len(matches)}"
            )
        if matches[0].get("locked") is not True:
            raise RuntimeError(f"Wk0 support file did not remain locked: {display_name}")
        resolved[key] = matches[0]
    return resolved


async def require_module_preflight(client):
    modules = await paged(client, f"/courses/{COURSE_ID}/modules")
    matches = [module for module in modules if module.get("name") == MODULE_NAME]
    if len(matches) != 1 or matches[0].get("id") != MODULE_ID:
        raise RuntimeError(
            f"1SW Wk0 module preflight failed: expected id={MODULE_ID} name={MODULE_NAME!r}; "
            f"matches={[(module.get('id'), module.get('name')) for module in matches]}"
        )
    module = matches[0]
    if module.get("published") is not False:
        raise RuntimeError(f"1SW Wk0 module must remain unpublished before writes: {module}")
    return module


async def require_mapped_minor_preflight(client):
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [assignment for assignment in assignments if assignment.get("name") == MINOR_TITLE]
    if len(matches) != 1:
        raise RuntimeError(
            f"1SW Wk0 mapped Minor preflight failed: expected one assignment named "
            f"{MINOR_TITLE!r}; found {len(matches)}"
        )
    groups = await paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group_matches = [group for group in groups if group.get("name") == MINOR_GROUP]
    if len(group_matches) != 1:
        raise RuntimeError(
            f"1SW Wk0 mapped Minor preflight failed: expected one group named "
            f"{MINOR_GROUP!r}; found {len(group_matches)}"
        )
    assignment, group = matches[0], group_matches[0]
    failures = {
        "published": assignment.get("published") is not False,
        "points": float(assignment.get("points_possible") or 0) != 100,
        "grading": assignment.get("grading_type") != "points",
        "group": assignment.get("assignment_group_id") != group.get("id"),
        "omit": assignment.get("omit_from_final_grade") is not False,
        "rubric_note": RUBRIC_NOTE_MARKER not in (assignment.get("description") or ""),
        "submission_types": frozenset(assignment.get("submission_types") or [])
        not in {MINOR_SUBMISSION_TYPES, LEGACY_MINOR_SUBMISSION_TYPES},
    }
    failed = [name for name, bad in failures.items() if bad]
    if failed:
        raise RuntimeError(
            f"1SW Wk0 mapped Minor invariant failed before writes: failed={failed}; "
            f"id={assignment.get('id')} group={assignment.get('assignment_group_id')}"
        )
    return assignment, group


async def normalize_mapped_minor(client, assignment, group):
    description = assignment.get("description") or ""
    if RUBRIC_NOTE_MARKER not in description:
        raise RuntimeError("Wk0 mapped Minor rubric marker disappeared before normalization")
    await api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{assignment['id']}",
        data={
            "assignment[name]": MINOR_TITLE,
            "assignment[description]": description,
            "assignment[assignment_group_id]": str(group["id"]),
            "assignment[points_possible]": "100",
            "assignment[grading_type]": "points",
            "assignment[omit_from_final_grade]": "false",
            "assignment[published]": "false",
            "assignment[submission_types][]": sorted(MINOR_SUBMISSION_TYPES),
        },
    )
    fresh = await api(
        client, "GET", f"/courses/{COURSE_ID}/assignments/{assignment['id']}"
    )
    failures = {
        "published": fresh.get("published") is not False,
        "points": float(fresh.get("points_possible") or 0) != 100,
        "grading": fresh.get("grading_type") != "points",
        "group": fresh.get("assignment_group_id") != group.get("id"),
        "omit": fresh.get("omit_from_final_grade") is not False,
        "rubric_note": RUBRIC_NOTE_MARKER not in (fresh.get("description") or ""),
        "submission_types": frozenset(fresh.get("submission_types") or [])
        != MINOR_SUBMISSION_TYPES,
    }
    failed = [name for name, bad in failures.items() if bad]
    if failed:
        raise RuntimeError(
            f"Wk0 mapped Minor normalization failed: failed={failed}; id={fresh.get('id')}"
        )
    return fresh


def render_template(filename, values):
    text = (TEMPLATES / filename).read_text()
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    unresolved = sorted(set(re.findall(r"\{\{[^}]+\}\}", text)))
    if unresolved:
        raise ValueError(f"Unresolved values in {filename}: {unresolved}")
    match = re.fullmatch(r"wk0-day([1-5])-(teacher|student)\.html", filename)
    if not match:
        raise RuntimeError(f"Cannot bind lesson contract to template {filename}")
    day = int(match.group(1))
    role = match.group(2)
    # A targeted Wk0 rerun can happen after the coursewide contract normalizer.
    # Bind the canonical panel here so the rerun cannot temporarily replace it
    # with a legacy or missing contract.
    return contract_html(WEEK_CONTRACTS[day], role) + text


async def upsert_page(client, *, title, body, page_url):
    data = {"wiki_page[title]": title, "wiki_page[body]": body, "wiki_page[published]": "false", "wiki_page[editing_roles]": "teachers"}
    response = await client.get(f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{page_url}")
    if response.status_code == 200:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/pages/{page_url}", data=data)
    if response.status_code != 404:
        response.raise_for_status()
    return await api(client, "POST", f"/courses/{COURSE_ID}/pages", data=data)


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


async def create_module_item(client, kind, key, title):
    data = {
        "module_item[type]": kind,
        "module_item[title]": title,
        "module_item[published]": "false",
    }
    if kind == "Page":
        data["module_item[page_url]"] = key
    elif kind == "Assignment":
        data["module_item[content_id]"] = str(key)
    elif kind != "SubHeader":
        raise RuntimeError(f"Unsupported Wk0 module item kind: {kind!r}")
    return await api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/modules/{MODULE_ID}/items",
        data=data,
    )


async def reconcile_module_items(client, expected):
    if len(expected) != 16:
        raise RuntimeError(f"Expected a literal 16-item Wk0 inventory; received {len(expected)}")
    kind_counts = {kind: sum(1 for item_kind, _key, _title in expected if item_kind == kind) for kind in {"SubHeader", "Page", "Assignment"}}
    if kind_counts != {"SubHeader": 5, "Page": 10, "Assignment": 1}:
        raise RuntimeError(f"Wk0 typed inventory contract failed: {kind_counts}")
    identities = [
        (kind, title if kind == "SubHeader" else key)
        for kind, key, title in expected
    ]
    titles = [title for _kind, _key, title in expected]
    if len(set(identities)) != 16 or len(set(titles)) != 16:
        raise RuntimeError("Wk0 typed inventory must contain 16 unique identities and titles")

    remaining = await paged(client, f"/courses/{COURSE_ID}/modules/{MODULE_ID}/items")
    kept = []
    for position, (kind, key, title) in enumerate(expected, 1):
        matches = [item for item in remaining if module_item_matches(item, kind, key, title)]
        if matches:
            item = matches[0]
            for duplicate in matches[1:]:
                await api(
                    client,
                    "DELETE",
                    f"/courses/{COURSE_ID}/modules/{MODULE_ID}/items/{duplicate['id']}",
                )
                remaining.remove(duplicate)
        else:
            item = await create_module_item(client, kind, key, title)
        remaining = [entry for entry in remaining if entry.get("id") != item.get("id")]
        item = await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{MODULE_ID}/items/{item['id']}",
            data={
                "module_item[title]": title,
                "module_item[position]": position,
                "module_item[published]": "false",
            },
        )
        kept.append(item)
    for stale in remaining:
        await api(
            client,
            "DELETE",
            f"/courses/{COURSE_ID}/modules/{MODULE_ID}/items/{stale['id']}",
        )

    final = sorted(
        await paged(client, f"/courses/{COURSE_ID}/modules/{MODULE_ID}/items"),
        key=lambda item: item.get("position") or 0,
    )
    if len(final) != len(expected):
        raise RuntimeError(f"Expected {len(expected)} exact Wk0 module items; found {len(final)}")
    for position, (item, (kind, key, title)) in enumerate(zip(final, expected), 1):
        if (
            int(item.get("position") or 0) != position
            or not module_item_matches(item, kind, key, title)
            or item.get("title") != title
            or item.get("published") is not False
        ):
            raise RuntimeError(
                f"Wk0 module item invariant failed at expected position {position}: "
                f"actual_position={item.get('position')}, "
                f"type={item.get('type')}, title={item.get('title')}, "
                f"page_url={item.get('page_url')}, content_id={item.get('content_id')}, "
                f"published={item.get('published')}"
            )
    return final


async def main():
    preflight()
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        await require_module_preflight(client)
        mapped_minor, minor_group = await require_mapped_minor_preflight(client)
        mapped_minor = await normalize_mapped_minor(client, mapped_minor, minor_group)
        support_names = {
            "D1_DECK": "cce-week1-day1-source-grounded.pptx",
            "D2_DECK": "cce-week1-day2-source-grounded.pptx",
            "D3_DECK": "cce-week1-day3-source-grounded.pptx",
            "D4_DECK": "cce-week1-day4-source-grounded.pptx",
            "D5_DECK": "cce-week1-day5-source-grounded.pptx",
            "D1_GOAL": "cce-first-week-goal-setting.pdf",
            "D1_GOAL_DOCX": "cce-first-week-goal-setting.docx",
            "D3_WORD_BANK": "building-blocks-word-bank.pdf",
            "D3_WORD_BANK_BI": "building-blocks-word-bank-bilingual.pdf",
            "D4_JOURNEY": "my-career-journey.pdf",
            "D4_STEMS": "my-career-journey-stems.pdf",
            "D4_BI": "my-career-journey-bilingual.pdf",
            "D4_RUBRIC": "wk0-career-journey-rubric.pdf",
        }
        support_folder = await ensure_folder(client, "course files/CCR Materials/1SW/Wk0")
        for path in SUPPORT_UPLOADS.values():
            await upload(client, path, "course files/CCR Materials/1SW/Wk0")
        support_folder, support_files = await lock_folder_files(
            client, support_folder, support_names.values()
        )
        support = resolve_folder_files(support_files, support_names)
        uploads, folders = {}, {}
        for day in (1, 2, 3, 4, 5):
            folder_path = f"course files/CCR Materials/1SW/Wk0/Day {day} Visuals"
            folders[day] = await ensure_folder(client, folder_path)
            uploads[day] = {}
            required_names = VISUAL_FILES.get(day, ())
            for name in required_names:
                path = ASSET_ROOT / f"day{day}" / name
                uploads[day][name] = await upload(client, path, folder_path)
            await lock_folder_files(client, folders[day], required_names)

        specs = [
            {"day": 1, "teacher_url": "teacher-day-1-facilitator-guide", "teacher_title": "TEACHER: Day 1 Facilitator Guide", "student_title": "STUDENT: 1SW Wk0 Day 1 - CCE Notebook and First-Week Goal", "values": {"DECK_FILE_ID": support["D1_DECK"]["id"], "GOOGLE_DECK_COPY_URL": GOOGLE_DECK_COPY_URLS[1], "GOAL_FILE_ID": support["D1_GOAL"]["id"], "GOAL_DOCX_FILE_ID": support["D1_GOAL_DOCX"]["id"], "GOOGLE_GOAL_COPY_URL": GOOGLE_GOAL_COPY_URL}},
            {"day": 2, "teacher_url": "teacher-day-2-facilitator-guide", "teacher_title": "TEACHER: Day 2 Facilitator Guide", "student_title": "STUDENT: 1SW Wk0 Day 2 - Who Are You at Work?", "values": {"DECK_FILE_ID": support["D2_DECK"]["id"], "GOOGLE_DECK_COPY_URL": GOOGLE_DECK_COPY_URLS[2], "WORKBOOK_IMAGE_ID": uploads[2]["irving-isd-ccmr-programs-of-study.png"]["id"], "TYPES_IMAGE_ID": uploads[2]["six-core-personality-types.png"]["id"], "APP_IMAGE_ID": uploads[2]["open-hats-and-ladders-discover-your-core.png"]["id"]}},
            {"day": 3, "teacher_url": "teacher-day-3-facilitator-guide", "teacher_title": "TEACHER: Day 3 Facilitator Guide", "student_title": "STUDENT: 1SW Wk0 Day 3 - Work Values and Building Blocks", "values": {"DECK_FILE_ID": support["D3_DECK"]["id"], "GOOGLE_DECK_COPY_URL": GOOGLE_DECK_COPY_URLS[3], "WORK_VALUES_IMAGE_ID": uploads[3]["open-hats-and-ladders-discover-your-work-values.png"]["id"], "BUILDING_BLOCKS_IMAGE_ID": uploads[3]["my-building-blocks-inventory.png"]["id"], "WORD_BANK_FILE_ID": support["D3_WORD_BANK"]["id"], "WORD_BANK_BILINGUAL_FILE_ID": support["D3_WORD_BANK_BI"]["id"]}},
            {"day": 4, "teacher_url": "teacher-day-4-facilitator-guide", "teacher_title": "TEACHER: Day 4 Facilitator Guide", "student_title": "STUDENT: 1SW Wk0 Day 4 - My Career Journey", "values": {"DECK_FILE_ID": support["D4_DECK"]["id"], "GOOGLE_DECK_COPY_URL": GOOGLE_DECK_COPY_URLS[4], "COMMUNITY_IMAGE_ID": uploads[4]["building-a-career-community.png"]["id"], "JOURNEY_FILE_ID": support["D4_JOURNEY"]["id"], "JOURNEY_STEMS_FILE_ID": support["D4_STEMS"]["id"], "JOURNEY_BILINGUAL_FILE_ID": support["D4_BI"]["id"], "RUBRIC_FILE_ID": support["D4_RUBRIC"]["id"], "ASSIGNMENT_ID": mapped_minor["id"]}},
            {"day": 5, "teacher_url": "teacher-day-5-facilitator-guide", "teacher_title": "TEACHER: Day 5 Facilitator Guide", "student_title": "STUDENT: 1SW Wk0 Day 5 - Catch Up, Xello, and Perks and Quirks", "values": {"DECK_FILE_ID": support["D5_DECK"]["id"], "GOOGLE_DECK_COPY_URL": GOOGLE_DECK_COPY_URLS[5], "PERKS_IMAGE_ID": uploads[5]["perks-and-quirks-introduction.png"]["id"], "CAREER_TABLES_IMAGE_ID": uploads[5]["perks-and-quirks-career-tables.png"]["id"]}},
        ]
        pages = {}
        for spec in specs:
            student_url = slugify(spec["student_title"])
            values = {"COURSE_ID": COURSE_ID, "STUDENT_PAGE_URL": student_url, **spec["values"]}
            student = await upsert_page(client, title=spec["student_title"], body=render_template(f"wk0-day{spec['day']}-student.html", values), page_url=student_url)
            teacher = await upsert_page(client, title=spec["teacher_title"], body=render_template(f"wk0-day{spec['day']}-teacher.html", values), page_url=spec["teacher_url"])
            pages[spec["day"]] = {"teacher": teacher, "student": student}
        ordered = [
            ("SubHeader", None, "Day 1"),
            ("Page", pages[1]["teacher"]["url"], specs[0]["teacher_title"]),
            ("Page", pages[1]["student"]["url"], specs[0]["student_title"]),
            ("SubHeader", None, "Day 2"),
            ("Page", pages[2]["teacher"]["url"], specs[1]["teacher_title"]),
            ("Page", pages[2]["student"]["url"], specs[1]["student_title"]),
            ("SubHeader", None, "Day 3"),
            ("Page", pages[3]["teacher"]["url"], specs[2]["teacher_title"]),
            ("Page", pages[3]["student"]["url"], specs[2]["student_title"]),
            ("SubHeader", None, "Day 4"),
            ("Page", pages[4]["teacher"]["url"], specs[3]["teacher_title"]),
            ("Page", pages[4]["student"]["url"], specs[3]["student_title"]),
            ("Assignment", mapped_minor["id"], MINOR_TITLE),
            ("SubHeader", None, "Day 5"),
            ("Page", pages[5]["teacher"]["url"], specs[4]["teacher_title"]),
            ("Page", pages[5]["student"]["url"], specs[4]["student_title"]),
        ]
        final_items = await reconcile_module_items(client, ordered)

        module = await api(client, "GET", f"/courses/{COURSE_ID}/modules/{MODULE_ID}")
        if module.get("name") != MODULE_NAME or module.get("published") is not False:
            raise RuntimeError(f"Wk0 final module invariant failed: {module}")
        final_pages = [
            await api(client, "GET", f"/courses/{COURSE_ID}/pages/{page_url}")
            for kind, page_url, _title in ordered
            if kind == "Page"
        ]
        if any(page.get("published") is not False for page in final_pages):
            raise RuntimeError("Wk0 final page invariant failed: a lesson page is published")
        final_minor, final_group = await require_mapped_minor_preflight(client)
        if frozenset(final_minor.get("submission_types") or []) != MINOR_SUBMISSION_TYPES:
            raise RuntimeError(
                "Wk0 mapped Minor final submission-route invariant failed: "
                f"{final_minor.get('submission_types')}"
            )
        if final_minor.get("id") != mapped_minor.get("id") or final_group.get("id") != minor_group.get("id"):
            raise RuntimeError("Wk0 mapped Minor identity changed during module reconciliation")
        print(json.dumps({"module": {"id": MODULE_ID, "published": module["published"]}, "folders": {str(day): {"id": folder["id"], "locked": folder["locked"]} for day, folder in folders.items()}, "pages": {str(day): {kind: {"url": page["url"], "published": page["published"]} for kind, page in pair.items()} for day, pair in pages.items()}, "minor": {"id": final_minor["id"], "group_id": final_group["id"], "published": final_minor["published"], "submission_types": final_minor["submission_types"]}, "items": [{"id": item["id"], "position": item["position"], "type": item["type"], "title": item["title"], "page_url": item.get("page_url"), "content_id": item.get("content_id")} for item in final_items]}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
