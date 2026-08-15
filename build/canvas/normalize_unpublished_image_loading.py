#!/usr/bin/env python3
"""Add native lazy loading to images in the exact unpublished CCR week modules.

The Canvas token is read once from stdin. The script never publishes content,
prints the token, or accepts it as a command-line argument. It is idempotent:
pages that already have an explicit image loading policy are left unchanged.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys

import httpx
from qa_remaining_unpublished import BASE, COURSE_ID, expected_modules

IMAGE_WITHOUT_LOADING = re.compile(
    r"<img\b(?![^>]*\bloading\s*=)",
    flags=re.IGNORECASE,
)
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
RETRYABLE_EXCEPTIONS = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadError,
    httpx.ReadTimeout,
    httpx.RemoteProtocolError,
    httpx.WriteError,
    httpx.WriteTimeout,
)
MAX_ATTEMPTS = 3


async def request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    data: dict[str, str] | None = None,
    params: dict[str, int] | None = None,
) -> httpx.Response:
    """Retry only transient Canvas/network failures; every write is idempotent."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = await client.request(method, url, data=data, params=params)
        except RETRYABLE_EXCEPTIONS as exc:
            if attempt == MAX_ATTEMPTS:
                raise ValueError(
                    f"{method} request failed after {MAX_ATTEMPTS} attempts: "
                    f"{type(exc).__name__}"
                ) from exc
            await asyncio.sleep(attempt)
            continue
        if response.status_code not in RETRYABLE_STATUS_CODES:
            response.raise_for_status()
            return response
        if attempt == MAX_ATTEMPTS:
            raise ValueError(
                f"{method} request failed after {MAX_ATTEMPTS} attempts: "
                f"HTTPStatusError status={response.status_code}"
            )
        retry_after = response.headers.get("Retry-After", "")
        delay = int(retry_after) if retry_after.isdigit() else attempt
        await asyncio.sleep(min(delay, 5))
    raise RuntimeError("unreachable retry state")


async def api(
    client: httpx.AsyncClient,
    method: str,
    path: str,
    *,
    data: dict[str, str] | None = None,
) -> object:
    response = await request(client, method, f"{BASE}/api/v1{path}", data=data)
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


def add_lazy_loading(body: str) -> tuple[str, int]:
    updated, count = IMAGE_WITHOUT_LOADING.subn('<img loading="lazy"', body)
    return updated, count


async def run(token: str) -> dict:
    names = expected_modules()
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=90
    ) as client:
        modules = await paged(client, f"/courses/{COURSE_ID}/modules")
        by_name: dict[str, list[dict]] = {}
        for module in modules:
            by_name.setdefault(module.get("name") or "", []).append(module)

        pages_seen = 0
        pages_updated = 0
        images_updated = 0
        changed_pages: list[str] = []

        for name in names:
            matches = by_name.get(name, [])
            if len(matches) != 1:
                raise ValueError(
                    f"expected one unpublished module named {name!r}; found {len(matches)}"
                )
            module = matches[0]
            if module.get("published"):
                raise ValueError(f"refusing to modify published module: {name}")

            items = await paged(
                client, f"/courses/{COURSE_ID}/modules/{module['id']}/items"
            )
            for item in items:
                if item.get("type") != "Page" or not item.get("page_url"):
                    continue
                if item.get("published"):
                    raise ValueError(
                        f"refusing to modify published module item: {item.get('title')}"
                    )
                page = await api(
                    client,
                    "GET",
                    f"/courses/{COURSE_ID}/pages/{item['page_url']}",
                )
                pages_seen += 1
                if page.get("published"):
                    raise ValueError(
                        f"refusing to modify published page: {page.get('url')}"
                    )
                body = page.get("body") or ""
                updated_body, changed = add_lazy_loading(body)
                if not changed:
                    continue
                await api(
                    client,
                    "PUT",
                    f"/courses/{COURSE_ID}/pages/{page['url']}",
                    data={
                        "wiki_page[body]": updated_body,
                        "wiki_page[published]": "false",
                    },
                )
                pages_updated += 1
                images_updated += changed
                changed_pages.append(page.get("url"))

        return {
            "modules": len(names),
            "pages_seen": pages_seen,
            "pages_updated": pages_updated,
            "images_updated": images_updated,
            "changed_pages": changed_pages,
        }


def main() -> int:
    if sys.argv[1:] == ["--preflight"]:
        sample = '<p><img src="a"><img loading="lazy" src="b"></p>'
        updated, count = add_lazy_loading(sample)
        if count != 1 or updated.count('loading="lazy"') != 2:
            print(
                "Preflight failed: image normalization is not idempotent",
                file=sys.stderr,
            )
            return 2
        names = expected_modules()
        if len(names) != 36 or len(set(names)) != 36:
            print("Preflight failed: expected 36 unique modules", file=sys.stderr)
            return 2
        print("Preflight passed: 36-module lazy-loading repair is idempotent.")
        return 0
    if sys.argv[1:]:
        print(
            "usage: normalize_unpublished_image_loading.py [--preflight]",
            file=sys.stderr,
        )
        return 2
    token = sys.stdin.readline().strip()
    if not token:
        print("Canvas token required on stdin", file=sys.stderr)
        return 2
    try:
        result = asyncio.run(run(token))
    except (httpx.HTTPError, ValueError) as exc:
        print(f"Image normalization failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
