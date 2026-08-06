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

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
MODULE_ID = 542880
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).resolve().parent / "templates"
ASSET_ROOT = ROOT / "cce-curriculum/resources/canvas-licensed/1sw/wk0"


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
    return folder


async def upload(client, path, folder_path):
    init = await api(client, "POST", f"/courses/{COURSE_ID}/files", data={"name": path.name, "parent_folder_path": folder_path, "on_duplicate": "overwrite"})
    response = await client.post(init["upload_url"], data=init["upload_params"], files={"file": (path.name, path.read_bytes(), mimetypes.guess_type(path.name)[0] or "application/octet-stream")}, follow_redirects=True)
    response.raise_for_status()
    return response.json()


async def find_file(client, display_name):
    files = await paged(client, f"/courses/{COURSE_ID}/files", {"search_term": display_name})
    match = next((item for item in files if item.get("display_name") == display_name), None)
    if not match:
        raise ValueError(f"Canvas file not found: {display_name}")
    return match


def render_template(filename, values):
    text = (TEMPLATES / filename).read_text()
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    unresolved = sorted(set(re.findall(r"\{\{[^}]+\}\}", text)))
    if unresolved:
        raise ValueError(f"Unresolved values in {filename}: {unresolved}")
    return text


async def upsert_page(client, *, title, body, page_url):
    data = {"wiki_page[title]": title, "wiki_page[body]": body, "wiki_page[published]": "false", "wiki_page[editing_roles]": "teachers"}
    response = await client.get(f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{page_url}")
    if response.status_code == 200:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/pages/{page_url}", data=data)
    if response.status_code != 404:
        response.raise_for_status()
    return await api(client, "POST", f"/courses/{COURSE_ID}/pages", data=data)


async def upsert_item(client, page, title):
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{MODULE_ID}/items")
    item = next((entry for entry in items if entry.get("page_url") == page["url"]), None)
    if item:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{MODULE_ID}/items/{item['id']}", data={"module_item[title]": title})
    return await api(client, "POST", f"/courses/{COURSE_ID}/modules/{MODULE_ID}/items", data={"module_item[type]": "Page", "module_item[page_url]": page["url"], "module_item[title]": title})


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        support_names = {
            "D1_SAFETY": "lab-safety-contract.pdf", "D1_SAFETY_BI": "lab-safety-contract-spanish.pdf", "D1_SCAFFOLD": "career-hunt-scaffold.pdf", "D1_EXIT": "1sw-wk0-day1-lab-routines-and-your-choice-flex-day.pdf",
            "D3_WORD_BANK": "building-blocks-word-bank.pdf", "D3_WORD_BANK_BI": "building-blocks-word-bank-bilingual.pdf", "D3_EXIT": "1sw-wk0-day3-work-values-and-building-blocks-core-day-b.pdf",
            "D4_JOURNEY": "my-career-journey.pdf", "D4_STEMS": "my-career-journey-stems.pdf", "D4_BI": "my-career-journey-bilingual.pdf", "D4_RUBRIC": "wk0-career-journey-rubric.pdf", "D4_EXIT": "1sw-wk0-day4-my-career-journey-reflection-core-day-c.pdf",
            "D5_RESEARCH": "career-research-worksheet.pdf", "D5_EXAMPLE": "career-research-worksheet-example.pdf", "D5_BI": "career-research-worksheet-bilingual.pdf", "D5_EXIT": "1sw-wk0-day5-catch-up-and-your-choice-flex-day.pdf",
        }
        support = {key: await find_file(client, name) for key, name in support_names.items()}
        uploads, folders = {}, {}
        for day in (1, 3, 4, 5):
            folder_path = f"course files/CCR Materials/1SW/Wk0/Day {day} Visuals"
            folders[day] = await ensure_folder(client, folder_path)
            uploads[day] = {}
            for path in sorted((ASSET_ROOT / f"day{day}").glob("*.png")):
                uploads[day][path.name] = await upload(client, path, folder_path)

        specs = [
            {"day": 1, "teacher_url": "teacher-day-1-facilitator-guide", "teacher_title": "TEACHER: Day 1 Facilitator Guide", "student_title": "STUDENT: 1SW Wk0 Day 1 - Welcome to the CCE Lab", "values": {"CAREER_HUNT_IMAGE_ID": uploads[1]["classroom-career-hunt.png"]["id"], "SAFETY_FILE_ID": support["D1_SAFETY"]["id"], "SAFETY_BILINGUAL_FILE_ID": support["D1_SAFETY_BI"]["id"], "CAREER_HUNT_SCAFFOLD_FILE_ID": support["D1_SCAFFOLD"]["id"], "EXIT_TICKET_FILE_ID": support["D1_EXIT"]["id"]}},
            {"day": 3, "teacher_url": "teacher-day-3-facilitator-guide", "teacher_title": "TEACHER: Day 3 Facilitator Guide", "student_title": "STUDENT: 1SW Wk0 Day 3 - Work Values and Building Blocks", "values": {"WORK_VALUES_IMAGE_ID": uploads[3]["open-hats-and-ladders-discover-your-work-values.png"]["id"], "BUILDING_BLOCKS_IMAGE_ID": uploads[3]["my-building-blocks-inventory.png"]["id"], "WORD_BANK_FILE_ID": support["D3_WORD_BANK"]["id"], "WORD_BANK_BILINGUAL_FILE_ID": support["D3_WORD_BANK_BI"]["id"], "EXIT_TICKET_FILE_ID": support["D3_EXIT"]["id"]}},
            {"day": 4, "teacher_url": "teacher-day-4-facilitator-guide", "teacher_title": "TEACHER: Day 4 Facilitator Guide", "student_title": "STUDENT: 1SW Wk0 Day 4 - My Career Journey", "values": {"COMMUNITY_IMAGE_ID": uploads[4]["building-a-career-community.png"]["id"], "JOURNEY_FILE_ID": support["D4_JOURNEY"]["id"], "JOURNEY_STEMS_FILE_ID": support["D4_STEMS"]["id"], "JOURNEY_BILINGUAL_FILE_ID": support["D4_BI"]["id"], "RUBRIC_FILE_ID": support["D4_RUBRIC"]["id"], "EXIT_TICKET_FILE_ID": support["D4_EXIT"]["id"]}},
            {"day": 5, "teacher_url": "teacher-day-5-facilitator-guide", "teacher_title": "TEACHER: Day 5 Facilitator Guide", "student_title": "STUDENT: 1SW Wk0 Day 5 - Catch Up or Research Careers", "values": {"PERKS_IMAGE_ID": uploads[5]["perks-and-quirks-introduction.png"]["id"], "CAREER_TABLES_IMAGE_ID": uploads[5]["perks-and-quirks-career-tables.png"]["id"], "CAREER_RESEARCH_FILE_ID": support["D5_RESEARCH"]["id"], "CAREER_RESEARCH_EXAMPLE_FILE_ID": support["D5_EXAMPLE"]["id"], "CAREER_RESEARCH_BILINGUAL_FILE_ID": support["D5_BI"]["id"], "EXIT_TICKET_FILE_ID": support["D5_EXIT"]["id"]}},
        ]
        pages, ordered = {}, [("1sw-wk0-teacher-guide", "1SW Wk0: Teacher Guide")]
        for spec in specs:
            student_url = slugify(spec["student_title"])
            values = {"COURSE_ID": COURSE_ID, "STUDENT_PAGE_URL": student_url, **spec["values"]}
            student = await upsert_page(client, title=spec["student_title"], body=render_template(f"wk0-day{spec['day']}-student.html", values), page_url=student_url)
            teacher = await upsert_page(client, title=spec["teacher_title"], body=render_template(f"wk0-day{spec['day']}-teacher.html", values), page_url=spec["teacher_url"])
            pages[spec["day"]] = {"teacher": teacher, "student": student}
            await upsert_item(client, teacher, spec["teacher_title"])
            await upsert_item(client, student, spec["student_title"])

        ordered.extend([(pages[1]["teacher"]["url"], specs[0]["teacher_title"]), (pages[1]["student"]["url"], specs[0]["student_title"]), ("teacher-day-2-facilitator-guide", "TEACHER: Day 2 Facilitator Guide"), ("student-1sw-wk0-day-2-who-are-you-at-work", "STUDENT: 1SW Wk0 Day 2 - Who Are You at Work?"), (pages[3]["teacher"]["url"], specs[1]["teacher_title"]), (pages[3]["student"]["url"], specs[1]["student_title"]), (pages[4]["teacher"]["url"], specs[2]["teacher_title"]), (pages[4]["student"]["url"], specs[2]["student_title"]), (pages[5]["teacher"]["url"], specs[3]["teacher_title"]), (pages[5]["student"]["url"], specs[3]["student_title"])])
        items = await paged(client, f"/courses/{COURSE_ID}/modules/{MODULE_ID}/items")
        by_url = {item.get("page_url"): item for item in items}
        for position, (url, title) in reversed(list(enumerate(ordered, start=1))):
            item = by_url[url]
            await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{MODULE_ID}/items/{item['id']}", data={"module_item[title]": title, "module_item[position]": position})

        module = await api(client, "GET", f"/courses/{COURSE_ID}/modules/{MODULE_ID}")
        final_items = await paged(client, f"/courses/{COURSE_ID}/modules/{MODULE_ID}/items")
        print(json.dumps({"module": {"id": MODULE_ID, "published": module["published"]}, "folders": {str(day): {"id": folder["id"], "locked": folder["locked"]} for day, folder in folders.items()}, "pages": {str(day): {kind: {"url": page["url"], "published": page["published"]} for kind, page in pair.items()} for day, pair in pages.items()}, "items": [{"id": item["id"], "position": item["position"], "title": item["title"], "page_url": item.get("page_url")} for item in final_items]}, indent=2))


asyncio.run(main())
