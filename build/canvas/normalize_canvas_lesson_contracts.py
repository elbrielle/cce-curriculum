#!/usr/bin/env python3
"""Insert or replace the visible lesson contract on all unpublished Canvas pairs."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from html.parser import HTMLParser
import json
import re
import sys

import httpx

from lesson_contracts import contract_html, load_contracts


BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
CONTRACT_RE = re.compile(
    r"<section\b[^>]*\bdata-cce-lesson-contract\s*=\s*['\"]1['\"][^>]*>"
    r".*?</section>",
    re.I | re.S,
)
CONTRACT_MARKER_RE = re.compile(
    r"data-cce-lesson-contract\s*=\s*['\"]1['\"]", re.I
)
TEACHER_LEGACY_RE = re.compile(
    r'<strong\b[^>]*>\s*topic\s*:?.*?'
    r'<strong\b[^>]*>\s*objective\s*:?.*?'
    r'<strong\b[^>]*>\s*teks\s*:?.*?'
    r'<strong\b[^>]*>\s*demonstration of learning\s*:?',
    re.I | re.S,
)
STUDENT_LEGACY_RE = re.compile(
    r'<strong\b[^>]*>\s*topic\s*:?.*?'
    r'<strong\b[^>]*>\s*(?:objective|i can|today[’\']s learning)\s*:?.*?'
    r'<strong\b[^>]*>\s*show (?:your|my) learning\s*:?',
    re.I | re.S,
)
ROLE_RE = re.compile(r"^(TEACHER|STUDENT)\b", re.I)
DAY_RE = re.compile(r"\bDay\s+([1-5])\b", re.I)
WEEK_RE = re.compile(r"^([1-6]SW Wk\d+):")


async def paged(client: httpx.AsyncClient, path: str) -> list[dict]:
    records: list[dict] = []
    url = f"{BASE}/api/v1{path}"
    params = {"per_page": 100}
    while url:
        response = await client.get(url, params=params)
        response.raise_for_status()
        records.extend(response.json())
        url = response.links.get("next", {}).get("url")
        params = None
    return records


@dataclass
class _Container:
    tag: str
    start: int
    end: int | None
    inside_contract: bool


class _ContainerParser(HTMLParser):
    """Collect exact div/section spans without rewriting the source HTML."""

    def __init__(self, body: str) -> None:
        super().__init__(convert_charrefs=False)
        self.body = body
        self.line_starts = [0]
        self.line_starts.extend(
            match.end() for match in re.finditer(r"\n", body)
        )
        self.containers: list[_Container] = []
        self.stack: list[int] = []

    def _offset(self) -> int:
        line, column = self.getpos()
        return self.line_starts[line - 1] + column

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag not in {"div", "section"}:
            return
        parent_inside_contract = bool(
            self.stack and self.containers[self.stack[-1]].inside_contract
        )
        is_contract = any(
            name.lower() == "data-cce-lesson-contract" and value == "1"
            for name, value in attrs
        )
        self.containers.append(
            _Container(
                tag=tag,
                start=self._offset(),
                end=None,
                inside_contract=parent_inside_contract or is_contract,
            )
        )
        self.stack.append(len(self.containers) - 1)

    def handle_endtag(self, tag: str) -> None:
        if tag not in {"div", "section"} or not self.stack:
            return
        index = self.stack[-1]
        if self.containers[index].tag != tag:
            # Fail closed on malformed nesting instead of guessing a broad span.
            return
        self.stack.pop()
        close_end = self.body.find(">", self._offset())
        if close_end >= 0:
            self.containers[index].end = close_end + 1


def legacy_contract_span(body: str, role: str) -> tuple[int, int] | None:
    """Return the smallest complete legacy contract container.

    This is intentionally nesting-aware. A flat contract resolves to its panel,
    while a three-cell Topic/I can/Show grid resolves to the shared grid wrapper.
    Source bytes outside the selected container are never parsed or rewritten.
    """
    pattern = TEACHER_LEGACY_RE if role == "teacher" else STUDENT_LEGACY_RE
    parser = _ContainerParser(body)
    parser.feed(body)
    parser.close()
    candidates: list[tuple[int, int]] = []
    for container in parser.containers:
        if container.end is None or container.inside_contract:
            continue
        raw = body[container.start : container.end]
        if CONTRACT_MARKER_RE.search(raw):
            continue
        # A complete page wrapper can coincidentally contain the label sequence.
        # Refuse to delete a candidate that also contains the page title/banner.
        if re.search(r"<h[12]\b", raw, re.I):
            continue
        if pattern.search(raw):
            candidates.append((container.start, container.end))
    if not candidates:
        return None
    return min(candidates, key=lambda span: (span[1] - span[0], span[0]))


def legacy_contract_count(body: str, role: str) -> int:
    count = 0
    remainder = body
    while (span := legacy_contract_span(remainder, role)) is not None:
        count += 1
        remainder = remainder[: span[0]] + remainder[span[1] :]
    return count


def without_contracts(body: str, role: str) -> str:
    """Remove complete marked/legacy contract containers for preservation checks."""
    remainder = CONTRACT_RE.sub("", body)
    while (span := legacy_contract_span(remainder, role)) is not None:
        remainder = remainder[: span[0]] + remainder[span[1] :]
    return remainder


def insert_contract(body: str, panel: str, role: str) -> str:
    if CONTRACT_RE.search(body):
        normalized = CONTRACT_RE.sub(panel, body, count=1)
    elif (span := legacy_contract_span(body, role)) is not None:
        normalized = body[: span[0]] + panel + body[span[1] :]
    else:
        normalized = body
        # Keep the page title/banner first, then show the daily contract before
        # prep, directions, optional disclosures, or instructional content.
        h1 = re.search(r"</h1>", body, re.I)
        if h1:
            normalized = body[: h1.end()] + panel + body[h1.end() :]
        else:
            normalized = panel + body

    while (extra := legacy_contract_span(normalized, role)) is not None:
        normalized = normalized[: extra[0]] + normalized[extra[1] :]
    return normalized


async def run(token: str, *, dry_run: bool = False) -> dict:
    contracts = {(row.week, row.day): row for row in load_contracts()}
    if len(contracts) != 180:
        raise RuntimeError(f"Expected 180 contracts; found {len(contracts)}")
    updated = 0
    would_update = 0
    verified = 0
    noncontract_preserved = 0
    legacy_contracts_removed = 0
    preservation_failures: list[str] = []
    missing: list[str] = []
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as client:
        modules = await paged(client, f"/courses/{COURSE_ID}/modules")
        for module in modules:
            week_match = WEEK_RE.match(module.get("name") or "")
            if not week_match:
                continue
            week = week_match.group(1)
            items = await paged(
                client,
                f"/courses/{COURSE_ID}/modules/{module['id']}/items?include[]=content_details",
            )
            for item in items:
                title = item.get("title") or ""
                role_match = ROLE_RE.match(title)
                day_match = DAY_RE.search(title)
                if not role_match or not day_match or item.get("type") != "Page":
                    continue
                role = role_match.group(1).lower()
                day = int(day_match.group(1))
                contract = contracts.get((week, day))
                if not contract:
                    missing.append(f"{week} Day {day}")
                    continue
                response = await client.get(
                    f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{item['page_url']}"
                )
                response.raise_for_status()
                page = response.json()
                old = page.get("body") or ""
                before_legacy = legacy_contract_count(old, role)
                new = insert_contract(old, contract_html(contract, role), role)
                after_legacy = legacy_contract_count(new, role)
                legacy_contracts_removed += before_legacy - after_legacy
                if new != old:
                    would_update += 1
                    if not dry_run:
                        response = await client.put(
                            f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{item['page_url']}",
                            data={"wiki_page[body]": new, "wiki_page[published]": "false"},
                        )
                        response.raise_for_status()
                        updated += 1
                if dry_run:
                    final = new
                else:
                    response = await client.get(
                        f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{item['page_url']}"
                    )
                    response.raise_for_status()
                    final = response.json().get("body") or ""
                if without_contracts(old, role) == without_contracts(final, role):
                    noncontract_preserved += 1
                else:
                    preservation_failures.append(
                        item.get("title") or item.get("page_url")
                    )
                required = (
                    "Topic:",
                    "Objective:",
                    "Demonstration of Learning:" if role == "teacher" else "Show Your Learning:",
                )
                if (
                    all(label in final for label in required)
                    and len(CONTRACT_RE.findall(final)) == 1
                    and legacy_contract_count(final, role) == 0
                ):
                    verified += 1
                else:
                    missing.append(item.get("title") or item.get("page_url"))
    return {
        "contracts": len(contracts),
        "paired_pages_verified": verified,
        "pages_updated": updated,
        "pages_would_update": would_update,
        "legacy_contracts_removed": legacy_contracts_removed,
        "noncontract_preserved": noncontract_preserved,
        "preservation_failures": sorted(set(preservation_failures)),
        "missing": sorted(set(missing)),
        "published": False,
        "dry_run": dry_run,
    }


def main() -> int:
    unknown = [arg for arg in sys.argv[1:] if arg != "--dry-run"]
    if unknown:
        print(f"Unknown arguments: {' '.join(unknown)}", file=sys.stderr)
        return 2
    dry_run = "--dry-run" in sys.argv[1:]
    token = sys.stdin.readline().strip()
    if not token:
        print("Canvas token required on stdin", file=sys.stderr)
        return 2
    try:
        payload = asyncio.run(run(token, dry_run=dry_run))
    except Exception as exc:  # redact by never printing the token or request headers
        print(f"Lesson-contract normalization failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(payload, indent=2))
    return (
        0
        if not payload["missing"]
        and not payload["preservation_failures"]
        and payload["paired_pages_verified"] == 360
        and payload["noncontract_preserved"] == 360
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
