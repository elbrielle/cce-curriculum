#!/usr/bin/env python3
"""Keep embedded Canvas images visible without publishing lesson content.

Canvas evaluates both a file and its ancestor folders when a student loads an
embedded image. This normalizer finds file IDs used specifically by ``<img>``
elements, makes only those image files course-visible, and opens only their
folder chains. It does not publish modules, module items, instructional pages,
assignments, discussions, or quizzes.

The reviewed CCE course home is the one intentional exception: it is kept
published, designated as the front page, and paired with the Pages (``wiki``)
course default. Teachers continue to decide which instructional modules to
publish.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import termios
from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx

from build_4sw_wk1 import BASE, COURSE_ID
from build_course_orientation import HOME_TITLE

FILE_PATH_RE = re.compile(r"/(?:courses/\d+/)?files/(\d+)(?:/|$)")
TRANSIENT_STATUSES = {429, 500, 502, 503, 504}
TRANSIENT_EXCEPTIONS = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadError,
    httpx.ReadTimeout,
    httpx.RemoteProtocolError,
    httpx.WriteError,
    httpx.WriteTimeout,
)


class ImageSourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sources: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "img":
            return
        source = dict(attrs).get("src")
        if source:
            self.sources.append(source)


def image_file_ids(body: str) -> set[int]:
    """Return Canvas file IDs used by image elements, not ordinary links."""

    parser = ImageSourceParser()
    parser.feed(body or "")
    ids: set[int] = set()
    for source in parser.sources:
        path = urlparse(source).path
        match = FILE_PATH_RE.search(path)
        if match:
            ids.add(int(match.group(1)))
    return ids


async def request(
    client: httpx.AsyncClient, method: str, path: str, **kwargs
) -> httpx.Response:
    url = path if path.startswith("http") else f"{BASE}/api/v1{path}"
    for attempt in range(1, 4):
        try:
            response = await client.request(method, url, **kwargs)
        except TRANSIENT_EXCEPTIONS as exc:
            if attempt == 3:
                raise RuntimeError(
                    f"{method} request failed after 3 attempts: {type(exc).__name__}"
                ) from exc
            await asyncio.sleep(0.25 * attempt)
            continue
        if response.status_code in TRANSIENT_STATUSES:
            if attempt == 3:
                raise RuntimeError(
                    f"{method} request failed after 3 attempts: "
                    f"HTTPStatusError status={response.status_code}"
                )
            await asyncio.sleep(0.25 * attempt)
            continue
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"Canvas {method} {urlparse(url).path} returned "
                f"{response.status_code}: {response.text[:300]}"
            ) from exc
        return response
    raise AssertionError("unreachable")


async def api(client: httpx.AsyncClient, method: str, path: str, **kwargs):
    response = await request(client, method, path, **kwargs)
    return response.json() if response.content else None


async def paged(client: httpx.AsyncClient, path: str) -> list[dict]:
    records: list[dict] = []
    url: str | None = f"{BASE}/api/v1{path}"
    params: dict[str, int] | None = {"per_page": 100}
    while url:
        response = await request(client, "GET", url, params=params)
        records.extend(response.json())
        url = response.links.get("next", {}).get("url")
        params = None
    return records


async def page_details(client: httpx.AsyncClient, pages: list[dict]) -> list[dict]:
    semaphore = asyncio.Semaphore(12)

    async def fetch(page: dict) -> dict:
        async with semaphore:
            return await api(
                client,
                "GET",
                f"/courses/{COURSE_ID}/pages/{page['url']}",
            )

    return list(await asyncio.gather(*(fetch(page) for page in pages)))


async def discover(client: httpx.AsyncClient) -> tuple[dict, set[int]]:
    pages = await paged(client, f"/courses/{COURSE_ID}/pages")
    homes = [page for page in pages if page.get("title") == HOME_TITLE]
    if len(homes) != 1:
        raise RuntimeError(f"expected one page {HOME_TITLE!r}; found {len(homes)}")
    details = await page_details(client, pages)
    file_ids: set[int] = set()
    for page in details:
        file_ids.update(image_file_ids(page.get("body") or ""))
    if not file_ids:
        raise RuntimeError("no Canvas file-backed images were found in course pages")
    home = next(page for page in details if page.get("title") == HOME_TITLE)
    return home, file_ids


async def folder_chain(
    client: httpx.AsyncClient, folder_id: int, cache: dict[int, dict]
) -> list[dict]:
    chain: list[dict] = []
    seen: set[int] = set()
    current_id: int | None = folder_id
    while current_id:
        if current_id in seen:
            raise RuntimeError(f"folder ancestry cycle at {current_id}")
        seen.add(current_id)
        folder = cache.get(current_id)
        if folder is None:
            folder = await api(client, "GET", f"/folders/{current_id}")
            cache[current_id] = folder
        chain.append(folder)
        parent = folder.get("parent_folder_id")
        current_id = int(parent) if parent else None
    return chain


def file_is_visible(record: dict) -> bool:
    return not record.get("locked") and not record.get("hidden")


def folder_is_visible(record: dict) -> bool:
    return not record.get("locked") and not record.get("hidden")


async def normalize(client: httpx.AsyncClient, *, check_only: bool = False) -> dict:
    home, image_ids = await discover(client)
    file_records: dict[int, dict] = {}
    folders: dict[int, dict] = {}
    folder_cache: dict[int, dict] = {}
    semaphore = asyncio.Semaphore(12)

    async def get_file(file_id: int) -> tuple[int, dict]:
        async with semaphore:
            return file_id, await api(client, "GET", f"/files/{file_id}")

    for file_id, record in await asyncio.gather(
        *(get_file(file_id) for file_id in sorted(image_ids))
    ):
        content_type = str(record.get("content-type") or record.get("content_type") or "")
        if not content_type.startswith("image/"):
            raise RuntimeError(
                f"img element points to non-image file {file_id}: {content_type!r}"
            )
        file_records[file_id] = record
        folder_id = record.get("folder_id")
        if not folder_id:
            raise RuntimeError(f"embedded image {file_id} has no folder")

    for folder_id in sorted(
        {int(record["folder_id"]) for record in file_records.values()}
    ):
        for folder in await folder_chain(client, folder_id, folder_cache):
            folders[int(folder["id"])] = folder

    if not check_only:
        async def show_folder(folder_id: int, folder: dict) -> None:
            if not folder_is_visible(folder):
                async with semaphore:
                    await api(
                        client,
                        "PUT",
                        f"/folders/{folder_id}",
                        data={"locked": "false", "hidden": "false"},
                    )

        # Canvas inherits file restrictions through the folder tree. Unlock
        # parents before children; same-depth folders can be updated together.
        depths = sorted(
            {
                str(folder.get("full_name") or "").count("/")
                for folder in folders.values()
            }
        )
        for depth in depths:
            await asyncio.gather(
                *(
                    show_folder(folder_id, folder)
                    for folder_id, folder in sorted(folders.items())
                    if str(folder.get("full_name") or "").count("/") == depth
                )
            )

        async def show_file(file_id: int, record: dict) -> None:
            current = record
            if current.get("locked") or current.get("hidden"):
                async with semaphore:
                    current = await api(
                        client,
                        "PUT",
                        f"/files/{file_id}",
                        data={
                            "locked": "false",
                            "hidden": "false",
                        },
                    )

        await asyncio.gather(
            *(show_file(file_id, record) for file_id, record in sorted(file_records.items()))
        )
        await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/pages/{home['url']}",
            data={
                "wiki_page[published]": "true",
                "wiki_page[front_page]": "true",
                "wiki_page[editing_roles]": "teachers",
                "wiki_page[notify_of_update]": "false",
            },
        )
        await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}",
            data={"course[default_view]": "wiki"},
        )

    final_home = await api(client, "GET", f"/courses/{COURSE_ID}/front_page")
    final_course = await api(client, "GET", f"/courses/{COURSE_ID}")
    async def final_file(file_id: int) -> tuple[int, dict]:
        async with semaphore:
            return file_id, await api(client, "GET", f"/files/{file_id}")

    async def final_folder(folder_id: int) -> tuple[int, dict]:
        async with semaphore:
            return folder_id, await api(client, "GET", f"/folders/{folder_id}")

    final_files = dict(
        await asyncio.gather(*(final_file(file_id) for file_id in sorted(image_ids)))
    )
    final_folders = dict(
        await asyncio.gather(*(final_folder(folder_id) for folder_id in sorted(folders)))
    )
    bad_files = [file_id for file_id, record in final_files.items() if not file_is_visible(record)]
    bad_folders = [
        folder_id
        for folder_id, record in final_folders.items()
        if not folder_is_visible(record)
    ]
    problems: list[str] = []
    if final_home.get("title") != HOME_TITLE or not final_home.get("published"):
        problems.append("active front page is not the published CCE home")
    if final_course.get("default_view") != "wiki":
        problems.append("course default view is not Pages")
    if bad_files:
        problems.append(f"embedded image files are restricted: {bad_files}")
    if bad_folders:
        problems.append(f"embedded image folder chain is restricted: {bad_folders}")
    if problems:
        raise RuntimeError("; ".join(problems))
    return {
        "course_id": COURSE_ID,
        "home_page": final_home.get("url"),
        "home_published": final_home.get("published"),
        "default_view": final_course.get("default_view"),
        "embedded_image_files": len(final_files),
        "visible_folder_chain": len(final_folders),
        "check_only": check_only,
        "passed": True,
    }


def self_test() -> None:
    sample = """
    <img src="/courses/98060/files/123/preview" alt="one">
    <a href="/courses/98060/files/999/preview">PDF</a>
    <IMG src="https://learn.irvingisd.net/files/456/download?download_frd=1">
    <img src="data:image/png;base64,AAAA">
    """
    assert image_file_ids(sample) == {123, 456}
    assert file_is_visible(
        {"locked": False, "hidden": False}
    )
    assert not file_is_visible(
        {"locked": True, "hidden": False}
    )
    assert folder_is_visible({"locked": False, "hidden": False})
    print("self-test: PASS")


def read_token() -> str:
    """Read one token from stdin without echoing it in an interactive terminal."""

    if not sys.stdin.isatty():
        return sys.stdin.readline().strip()
    descriptor = sys.stdin.fileno()
    original = termios.tcgetattr(descriptor)
    hidden = termios.tcgetattr(descriptor)
    hidden[3] &= ~termios.ECHO
    try:
        termios.tcsetattr(descriptor, termios.TCSADRAIN, hidden)
        return sys.stdin.readline().strip()
    finally:
        termios.tcsetattr(descriptor, termios.TCSADRAIN, original)
        print(file=sys.stderr)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    token = read_token()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as client:
        print(json.dumps(await normalize(client, check_only=args.check), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
