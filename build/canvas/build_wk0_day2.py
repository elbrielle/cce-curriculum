"""Build the unpublished Week 0 Day 2 teacher/student Canvas pilot.

Run with a Canvas token on stdin. The token is never stored by this script.
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
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/1sw/wk0/day2"
FOLDER_PATH = "course files/CCR Materials/1SW/Wk0/Day 2 Visuals"
TEACHER_PAGE_URL = "teacher-day-2-facilitator-guide"
STUDENT_PAGE_TITLE = "STUDENT: 1SW Wk0 Day 2 - Who Are You at Work?"


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower().replace("&", "and")).strip("-")


async def api(client, method, path, *, data=None, params=None):
    response = await client.request(method, f"{BASE}/api/v1{path}", data=data, params=params)
    response.raise_for_status()
    return response.json() if response.content else None


async def paged(client, path, params=None):
    results = []
    url = f"{BASE}/api/v1{path}"
    query = {"per_page": 100, **(params or {})}
    while url:
        response = await client.get(url, params=query)
        response.raise_for_status()
        results.extend(response.json())
        url = response.links.get("next", {}).get("url")
        query = None
    return results


async def ensure_folder(client):
    current = ""
    folder = None
    for name in FOLDER_PATH.split("/")[1:]:
        target = f"{current}/{name}".strip("/")
        encoded = httpx.URL("/" + target).raw_path.decode("ascii").lstrip("/")
        response = await client.get(
            f"{BASE}/api/v1/courses/{COURSE_ID}/folders/by_path/{encoded}"
        )
        if response.status_code == 200 and response.json():
            folder = response.json()[-1]
        else:
            parent_path = "course files" + (f"/{current}" if current else "")
            folder = await api(
                client,
                "POST",
                f"/courses/{COURSE_ID}/folders",
                data={"name": name, "parent_folder_path": parent_path, "locked": "true"},
            )
        current = target
    if folder and not folder.get("locked"):
        folder = await api(client, "PUT", f"/folders/{folder['id']}", data={"locked": "true"})
    return folder


async def upload(client, path):
    init = await api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/files",
        data={"name": path.name, "parent_folder_path": FOLDER_PATH, "on_duplicate": "overwrite"},
    )
    upload_response = await client.post(
        init["upload_url"],
        data=init["upload_params"],
        files={"file": (path.name, path.read_bytes(), mimetypes.guess_type(path.name)[0] or "application/octet-stream")},
        follow_redirects=True,
    )
    upload_response.raise_for_status()
    return upload_response.json()


async def find_file(client, display_name):
    files = await paged(client, f"/courses/{COURSE_ID}/files", {"search_term": display_name})
    return next(item for item in files if item.get("display_name") == display_name)


def render_template(filename, values):
    text = (TEMPLATES / filename).read_text()
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    unresolved = sorted(set(re.findall(r"\{\{[^}]+\}\}", text)))
    if unresolved:
        raise ValueError(f"Unresolved template values in {filename}: {unresolved}")
    return text


async def upsert_page(client, title, body, url=None):
    page_url = url or slugify(title)
    data = {
        "wiki_page[title]": title,
        "wiki_page[body]": body,
        "wiki_page[published]": "false",
        "wiki_page[editing_roles]": "teachers",
    }
    response = await client.get(f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{page_url}")
    if response.status_code == 200:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/pages/{page_url}", data=data)
    response.raise_for_status() if response.status_code != 404 else None
    return await api(client, "POST", f"/courses/{COURSE_ID}/pages", data=data)


async def place_pages(client, teacher, student):
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{MODULE_ID}/items")
    teacher_item = next(item for item in items if item.get("page_url") == teacher["url"])
    await api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/modules/{MODULE_ID}/items/{teacher_item['id']}",
        data={"module_item[title]": "TEACHER: Day 2 Facilitator Guide", "module_item[position]": 3},
    )
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{MODULE_ID}/items")
    student_item = next((item for item in items if item.get("page_url") == student["url"]), None)
    if student_item:
        return await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{MODULE_ID}/items/{student_item['id']}",
            data={"module_item[title]": STUDENT_PAGE_TITLE, "module_item[position]": 4},
        )
    return await api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/modules/{MODULE_ID}/items",
        data={
            "module_item[type]": "Page",
            "module_item[page_url]": student["url"],
            "module_item[title]": STUDENT_PAGE_TITLE,
            "module_item[position]": 4,
        },
    )


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        folder = await ensure_folder(client)
        uploaded = {}
        for path in sorted(ASSETS.glob("*.png")):
            uploaded[path.name] = await upload(client, path)
        exit_ticket = await find_file(client, "1sw-wk0-day2-h-and-l-setup-and-discover-your-core-core-day-a.pdf")
        values = {
            "COURSE_ID": COURSE_ID,
            "WORKBOOK_IMAGE_ID": uploaded["irving-isd-ccmr-programs-of-study.png"]["id"],
            "TYPES_IMAGE_ID": uploaded["six-core-personality-types.png"]["id"],
            "APP_IMAGE_ID": uploaded["open-hats-and-ladders-discover-your-core.png"]["id"],
            "EXIT_TICKET_FILE_ID": exit_ticket["id"],
            "STUDENT_PAGE_URL": slugify(STUDENT_PAGE_TITLE),
        }
        student = await upsert_page(
            client,
            STUDENT_PAGE_TITLE,
            render_template("wk0-day2-student.html", values),
        )
        teacher = await upsert_page(
            client,
            "TEACHER: Day 2 Facilitator Guide",
            render_template("wk0-day2-teacher.html", values),
            TEACHER_PAGE_URL,
        )
        item = await place_pages(client, teacher, student)
        print(json.dumps({
            "folder": {"id": folder["id"], "locked": folder["locked"]},
            "uploaded_files": [{"id": value["id"], "name": key} for key, value in uploaded.items()],
            "teacher_page": {"url": teacher["url"], "published": teacher["published"]},
            "student_page": {"url": student["url"], "published": student["published"]},
            "student_module_item": {"id": item["id"], "position": item["position"]},
        }, indent=2))


asyncio.run(main())
