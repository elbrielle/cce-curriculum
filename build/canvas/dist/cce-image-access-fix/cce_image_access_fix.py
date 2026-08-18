#!/usr/bin/env python3
"""CCE Canvas image-access fix (standalone).

Problem: when a CCE course is imported from Canvas Commons, the image files used on
lesson pages (and the folders they sit in) can arrive locked, so students see a
padlock where the picture should be. A later Commons update does not reopen them.

What this does, per course: reads the course pages, finds only the Canvas files
used by <img> elements, and sets those files and their folder chains to
published/unlocked. It changes nothing else: no publishing of modules or pages,
no home-page changes, no student data read.

Usage (Python 3.9+; needs the httpx package: `pip3 install httpx`):

    python3 cce_image_access_fix.py --check --course-id 97981          # dry run, changes nothing
    python3 cce_image_access_fix.py --course-id 97981                  # apply
    python3 cce_image_access_fix.py --course-id 97981 --course-id 98060 # several courses
    python3 cce_image_access_fix.py --courses-file ids.txt             # one course ID per line

The Canvas token is typed at a hidden prompt (or piped on stdin). It is never
written to disk or printed. Use a token from an account with teacher or admin
access to each course (an admin token works for all of them).
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
import json
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse

try:
    import httpx
except ImportError:  # pragma: no cover
    sys.exit("This tool needs the httpx package: run `pip3 install httpx` (or `uv run --with httpx python3 cce_image_access_fix.py ...`).")

BASE = "https://learn.irvingisd.net"
FILE_PATH_RE = re.compile(r"/(?:courses/\d+/)?files/(\d+)(?:/|$)")
TRANSIENT_STATUSES = {429, 500, 502, 503, 504}


class ImageSourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sources: list[str] = []

    def handle_starttag(self, tag, attrs) -> None:
        if tag.lower() != "img":
            return
        source = dict(attrs).get("src")
        if source:
            self.sources.append(source)


def image_file_ids(body: str) -> set[int]:
    parser = ImageSourceParser()
    parser.feed(body or "")
    ids: set[int] = set()
    for source in parser.sources:
        match = FILE_PATH_RE.search(urlparse(source).path)
        if match:
            ids.add(int(match.group(1)))
    return ids


async def request(client, method, path, **kwargs):
    url = path if path.startswith("http") else f"{BASE}/api/v1{path}"
    for attempt in range(1, 4):
        try:
            response = await client.request(method, url, **kwargs)
        except (httpx.TransportError,) as exc:
            if attempt == 3:
                raise RuntimeError(f"{method} {path} failed after 3 attempts: {type(exc).__name__}") from exc
            await asyncio.sleep(0.25 * attempt)
            continue
        if response.status_code in TRANSIENT_STATUSES:
            if attempt == 3:
                raise RuntimeError(f"{method} {path} failed after 3 attempts: HTTP {response.status_code}")
            await asyncio.sleep(0.25 * attempt)
            continue
        if response.status_code >= 400:
            raise RuntimeError(f"Canvas {method} {urlparse(url).path} returned {response.status_code}: {response.text[:200]}")
        return response
    raise AssertionError("unreachable")


async def api(client, method, path, **kwargs):
    response = await request(client, method, path, **kwargs)
    return response.json() if response.content else None


async def paged(client, path):
    records = []
    url = f"{BASE}/api/v1{path}"
    params = {"per_page": 100}
    while url:
        response = await request(client, "GET", url, params=params)
        records.extend(response.json())
        url = response.links.get("next", {}).get("url")
        params = None
    return records


def visible(record) -> bool:
    return not record.get("locked") and not record.get("hidden")


async def fix_course(client, course_id: int, check_only: bool) -> dict:
    course = await api(client, "GET", f"/courses/{course_id}")
    pages = await paged(client, f"/courses/{course_id}/pages")
    semaphore = asyncio.Semaphore(10)

    async def page_body(page):
        async with semaphore:
            full = await api(client, "GET", f"/courses/{course_id}/pages/{page['url']}")
            return full.get("body") or ""

    bodies = await asyncio.gather(*(page_body(p) for p in pages))
    image_ids: set[int] = set()
    for body in bodies:
        image_ids.update(image_file_ids(body))
    if not image_ids:
        return {"course_id": course_id, "course": course.get("name"), "pages": len(pages), "image_files": 0, "note": "no Canvas file-backed images on pages", "passed": True}

    async def get_file(file_id):
        async with semaphore:
            try:
                return file_id, await api(client, "GET", f"/files/{file_id}")
            except RuntimeError as exc:
                return file_id, {"_error": str(exc)}

    files = dict(await asyncio.gather(*(get_file(fid) for fid in sorted(image_ids))))
    missing = [fid for fid, rec in files.items() if "_error" in rec]
    files = {fid: rec for fid, rec in files.items() if "_error" not in rec}
    files = {fid: rec for fid, rec in files.items() if str(rec.get("content-type") or rec.get("content_type") or "").startswith("image/")}

    # Folder chains (Canvas locks a file if ANY ancestor folder is locked).
    folder_cache: dict[int, dict] = {}
    chain_ids: set[int] = set()
    for rec in files.values():
        current = rec.get("folder_id")
        seen = set()
        while current and current not in seen:
            seen.add(current)
            folder = folder_cache.get(current)
            if folder is None:
                folder = await api(client, "GET", f"/folders/{current}")
                folder_cache[current] = folder
            chain_ids.add(int(folder["id"]))
            current = folder.get("parent_folder_id")

    locked_files_before = [fid for fid, rec in files.items() if not visible(rec)]
    locked_folders_before = [fid for fid in chain_ids if not visible(folder_cache[fid])]

    if not check_only:
        # parents before children
        for depth in sorted({str(folder_cache[f].get("full_name") or "").count("/") for f in chain_ids}):
            batch = [f for f in chain_ids if str(folder_cache[f].get("full_name") or "").count("/") == depth and not visible(folder_cache[f])]

            async def open_folder(fid):
                async with semaphore:
                    await api(client, "PUT", f"/folders/{fid}", data={"locked": "false", "hidden": "false"})

            await asyncio.gather(*(open_folder(f) for f in batch))

        async def open_file(fid):
            async with semaphore:
                await api(client, "PUT", f"/files/{fid}", data={"locked": "false", "hidden": "false"})

        await asyncio.gather(*(open_file(f) for f in locked_files_before))

    # Verify
    async def refetch_file(fid):
        async with semaphore:
            return fid, await api(client, "GET", f"/files/{fid}")

    async def refetch_folder(fid):
        async with semaphore:
            return fid, await api(client, "GET", f"/folders/{fid}")

    files_after = dict(await asyncio.gather(*(refetch_file(f) for f in files)))
    folders_after = dict(await asyncio.gather(*(refetch_folder(f) for f in chain_ids)))
    still_files = [f for f, r in files_after.items() if not visible(r)]
    still_folders = [f for f, r in folders_after.items() if not visible(r)]
    return {
        "course_id": course_id,
        "course": course.get("name"),
        "pages": len(pages),
        "image_files": len(files),
        "folder_chain": len(chain_ids),
        "locked_before": {"files": len(locked_files_before), "folders": len(locked_folders_before)},
        "still_locked": {"files": still_files, "folders": still_folders},
        "unresolved_file_ids": missing,
        "check_only": check_only,
        "passed": not still_files and not still_folders if not check_only else not locked_files_before and not locked_folders_before,
    }


def read_token() -> str:
    if sys.stdin.isatty():
        return getpass.getpass("Canvas access token (hidden): ").strip()
    return sys.stdin.readline().strip()


async def main() -> None:
    parser = argparse.ArgumentParser(description="Unlock CCE embedded images and their folders in Canvas courses.")
    parser.add_argument("--course-id", type=int, action="append", default=[], help="Canvas course ID (repeatable)")
    parser.add_argument("--courses-file", help="text file with one course ID per line")
    parser.add_argument("--check", action="store_true", help="dry run: report only, change nothing")
    args = parser.parse_args()
    course_ids = list(args.course_id)
    if args.courses_file:
        with open(args.courses_file, encoding="utf-8") as handle:
            course_ids.extend(int(line.strip()) for line in handle if line.strip().isdigit())
    if not course_ids:
        parser.error("give at least one --course-id or a --courses-file")
    token = read_token()
    if not token:
        sys.exit("A Canvas token is required.")
    results = []
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        me = await api(client, "GET", "/users/self")
        print(f"Signed in as: {me.get('name')} (user {me.get('id')}){'  [CHECK ONLY]' if args.check else ''}", file=sys.stderr)
        for course_id in course_ids:
            try:
                result = await fix_course(client, course_id, args.check)
            except Exception as exc:  # keep going through the list
                result = {"course_id": course_id, "error": str(exc), "passed": False}
            results.append(result)
            status = "ok  " if result.get("passed") else "FAIL"
            summary = result.get("error") or f"images={result.get('image_files')} folders={result.get('folder_chain')} locked_before={result.get('locked_before')} still_locked={result.get('still_locked')}"
            print(f"{status} course {course_id} {result.get('course') or ''}: {summary}")
    print(json.dumps(results, indent=2))
    if not all(r.get("passed") for r in results):
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
