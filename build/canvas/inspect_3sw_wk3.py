"""Read-only saved-state inspection for the 3SW Wk3 Canvas module."""

import asyncio, json, sys
import httpx

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
MODULE_NAME = "3SW Wk3: Sustainable Engineering and Pest Patrol"
ASSIGNMENTS = {
    "PRACTICE: Pest Patrol Drone Draft",
    "PRACTICE: Sustainable Engineering Evidence Packet",
    "PRACTICE: Xello Set Goals Reflection",
}


async def paged(client, path):
    output, url, params = [], f"{BASE}/api/v1{path}", {"per_page": 100}
    while url:
        response = await client.get(url, params=params)
        response.raise_for_status()
        output += response.json()
        url, params = response.links.get("next", {}).get("url"), None
    return output


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        modules = await paged(client, f"/courses/{COURSE_ID}/modules")
        module = next(module for module in modules if module["name"] == MODULE_NAME)
        items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        pages = await paged(client, f"/courses/{COURSE_ID}/pages")
        pages = [page for page in pages if page["title"].startswith(("TEACHER: 3SW Wk3", "STUDENT: 3SW Wk3"))]
        assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
        assignments = [assignment for assignment in assignments if assignment["name"] in ASSIGNMENTS]
        folders = await paged(client, f"/courses/{COURSE_ID}/folders")
        folders = [folder for folder in folders if "CCR Materials/3SW/Wk3" in folder.get("full_name", "")]
        print(json.dumps({
            "module": {"id": module["id"], "published": module["published"]},
            "items": [{"position": item["position"], "type": item["type"], "title": item["title"], "content_id": item.get("content_id"), "page_url": item.get("page_url")} for item in items],
            "pages": [{"title": page["title"], "url": page["url"], "published": page["published"]} for page in pages],
            "assignments": [{"id": assignment["id"], "name": assignment["name"], "published": assignment["published"], "grading_type": assignment["grading_type"], "peer_reviews": assignment.get("peer_reviews"), "automatic_peer_reviews": assignment.get("automatic_peer_reviews"), "submission_types": assignment.get("submission_types")} for assignment in assignments],
            "folders": [{"id": folder["id"], "full_name": folder["full_name"], "locked": folder["locked"]} for folder in folders],
        }, indent=2))


asyncio.run(main())
