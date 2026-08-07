"""Read-only Canvas module QA. Reads the API token from stdin and prints no secrets."""

import asyncio, json, re, sys
import httpx

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060

async def api(client, path):
    response = await client.get(f"{BASE}/api/v1{path}")
    response.raise_for_status()
    return response.json()

async def paged(client, path):
    results=[]; url=f"{BASE}/api/v1{path}"; params={"per_page":100}
    while url:
        response=await client.get(url,params=params); response.raise_for_status(); results.extend(response.json())
        url=response.links.get("next",{}).get("url"); params=None
    return results

async def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        raise SystemExit("usage: qa_canvas_module.py MODULE_ID")
    token=sys.stdin.readline().strip()
    if not token: raise SystemExit("Canvas token required on stdin")
    module_id=int(sys.argv[1])
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"},timeout=60) as client:
        module=await api(client,f"/courses/{COURSE_ID}/modules/{module_id}")
        items=await paged(client,f"/courses/{COURSE_ID}/modules/{module_id}/items")
        problems=[]; pages=[]; file_ids=set()
        positions=[item.get("position") for item in items]
        if module.get("published"): problems.append("module is published")
        if positions != list(range(1,len(items)+1)): problems.append(f"positions are not consecutive: {positions}")
        for item in items:
            if item.get("type") != "Page" or not item.get("page_url"):
                problems.append(f"item {item.get('id')} is not a page")
                continue
            page=await api(client,f"/courses/{COURSE_ID}/pages/{item['page_url']}")
            body=page.get("body") or ""
            unresolved=sorted(set(re.findall(r"\{\{[^}]+\}\}",body)))
            if page.get("published"): problems.append(f"page published: {page['url']}")
            if unresolved: problems.append(f"unresolved fields in {page['url']}: {unresolved}")
            if "enhanceable_content" in body: problems.append(f"legacy Canvas tabs in {page['url']}")
            file_ids.update(int(value) for value in re.findall(r"/files/(\d+)",body))
            pages.append({"item_id":item["id"],"position":item["position"],"url":page["url"],"published":page["published"],"body_chars":len(body)})
        files=[]
        for file_id in sorted(file_ids):
            try:
                record=await api(client,f"/files/{file_id}")
                files.append({"id":file_id,"name":record.get("display_name"),"locked":record.get("locked")})
            except httpx.HTTPStatusError as exc:
                problems.append(f"file {file_id} did not resolve: HTTP {exc.response.status_code}")
        result={"module":{"id":module_id,"name":module.get("name"),"published":module.get("published")},"items":len(items),"pages":pages,"referenced_files":files,"problems":problems,"passed":not problems}
        print(json.dumps(result,indent=2))
        if problems: raise SystemExit(2)

asyncio.run(main())
