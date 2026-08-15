#!/usr/bin/env python3
"""Read-only course publication snapshot for the official CCR Canvas course.

This complements the unpublished-transfer verifier. It reports learner-facing
navigation, front-page, module, page, file-folder, and assignment-group risks
without changing Canvas or treating intentional unpublished staging as a pass.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
from html.parser import HTMLParser

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
HOME_TITLE = "Career and College Exploration Home"
ORIENTATION_MODULE = "START HERE: CCE Course Orientation"
TEACHER_MODULE = "Teacher Build: Licensed Resources"
EXPECTED_WEEK_MODULES = 36
CORE_TABS = {"home", "modules", "grades"}


class TextAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text: list[str] = []
        self.tables = 0
        self.images: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "table":
            self.tables += 1
        if tag.lower() == "img":
            self.images.append(dict(attrs))

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.text.append(data.strip())


async def api(client: httpx.AsyncClient, path: str) -> object:
    response = await client.get(f"{BASE}/api/v1{path}")
    response.raise_for_status()
    return response.json()


async def paged(client: httpx.AsyncClient, path: str) -> list[dict]:
    records: list[dict] = []
    url: str | None = f"{BASE}/api/v1{path}"
    params: dict[str, int] | None = {"per_page": 100}
    while url:
        response = await client.get(url, params=params)
        response.raise_for_status()
        records.extend(response.json())
        url = response.links.get("next", {}).get("url")
        params = None
    return records


def week_module(name: str) -> bool:
    return bool(re.match(r"^[1-6]SW Wk[0-6]:", name))


async def run(token: str) -> int:
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=90
    ) as client:
        course = await api(client, f"/courses/{COURSE_ID}")
        tabs = await api(client, f"/courses/{COURSE_ID}/tabs")
        modules = await paged(client, f"/courses/{COURSE_ID}/modules")
        pages = await paged(client, f"/courses/{COURSE_ID}/pages")
        groups = await paged(
            client, f"/courses/{COURSE_ID}/assignment_groups?include[]=assignments"
        )
        assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
        front_page = await api(client, f"/courses/{COURSE_ID}/front_page")

        front_audit = TextAudit()
        front_audit.feed(front_page.get("body") or "")
        front_text = " ".join(front_audit.text).lower()

        active_tabs = [
            {
                "id": tab.get("id"),
                "label": tab.get("label"),
                "type": tab.get("type"),
            }
            for tab in tabs
            if not tab.get("hidden") and str(tab.get("id")) != "settings"
        ]
        active_tab_ids = {str(tab["id"]) for tab in active_tabs}
        extra_tabs = [tab for tab in active_tabs if str(tab.get("id")) not in CORE_TABS]

        week_modules = [
            module for module in modules if week_module(module.get("name") or "")
        ]
        published_week_modules = [
            module.get("name") for module in week_modules if module.get("published")
        ]
        orientation = [
            module for module in modules if module.get("name") == ORIENTATION_MODULE
        ]
        teacher_modules = [
            module for module in modules if module.get("name") == TEACHER_MODULE
        ]
        replacement_pages = [page for page in pages if page.get("title") == HOME_TITLE]
        published_pages = sorted(
            page.get("title") for page in pages if page.get("published")
        )

        group_rows = [
            {
                "id": group.get("id"),
                "name": group.get("name"),
                "weight": group.get("group_weight"),
                # Some Canvas deployments omit the requested embedded assignment
                # list. Count the authoritative course assignment records by
                # group id so the publication gate cannot report a false zero.
                "assignments": sum(
                    assignment.get("assignment_group_id") == group.get("id")
                    for assignment in assignments
                ),
                "published_assignments": sum(
                    assignment.get("assignment_group_id") == group.get("id")
                    and assignment.get("published")
                    for assignment in assignments
                ),
            }
            for group in groups
        ]
        legacy_groups = [
            row
            for row in group_rows
            if row["name"] not in {"Minor Assessments (40%)", "Major Assessments (60%)"}
        ]
        mapped_groups = {row["name"]: row for row in group_rows}

        must_fix: list[str] = []
        warnings: list[str] = []
        if front_page.get("title") != HOME_TITLE:
            must_fix.append(
                f"front page is {front_page.get('title')!r}, not the reviewed replacement"
            )
        if "grade / subject" in front_text or "teacher name" in front_text:
            must_fix.append("front page still exposes generic template placeholders")
        if front_audit.tables:
            must_fix.append(
                f"front page contains {front_audit.tables} table(s); verify none are layout tables"
            )
        if len(replacement_pages) != 1:
            must_fix.append(
                f"expected one replacement home page; found {len(replacement_pages)}"
            )
        if len(week_modules) != EXPECTED_WEEK_MODULES:
            must_fix.append(
                f"expected {EXPECTED_WEEK_MODULES} week modules; found {len(week_modules)}"
            )
        if not published_week_modules:
            must_fix.append("no instructional week module is currently student-visible")
        if len(orientation) != 1:
            must_fix.append(
                f"expected one orientation module; found {len(orientation)}"
            )
        elif not orientation[0].get("published"):
            must_fix.append("student orientation module is still unpublished")
        if len(teacher_modules) != 1:
            must_fix.append(
                f"expected one teacher-build module; found {len(teacher_modules)}"
            )
        elif teacher_modules[0].get("published"):
            must_fix.append("teacher-build module is published")
        if extra_tabs:
            warnings.append(
                f"{len(extra_tabs)} navigation tabs are enabled beyond Home, Modules, and Grades"
            )
        published_legacy_groups = [
            row for row in legacy_groups if row["published_assignments"]
        ]
        if published_legacy_groups:
            warnings.append(
                f"{len(published_legacy_groups)} legacy/default groups contain published assignments"
            )
        if not course.get("apply_assignment_group_weights"):
            must_fix.append("assignment-group weighting is not enabled")
        for name, weight, count in (
            ("Minor Assessments (40%)", 40, 18),
            ("Major Assessments (60%)", 60, 12),
        ):
            group = mapped_groups.get(name)
            if not group:
                must_fix.append(f"missing mapped assignment group {name!r}")
                continue
            if float(group.get("weight") or 0) != weight:
                must_fix.append(
                    f"{name} weight is {group.get('weight')}; expected {weight}"
                )
            if group.get("assignments") != count:
                must_fix.append(
                    f"{name} contains {group.get('assignments')} assignments; "
                    f"expected {count}"
                )

        snapshot = {
            "course": {
                "id": course.get("id"),
                "name": course.get("name"),
                "published": course.get("workflow_state") == "available",
                "default_view": course.get("default_view"),
            },
            "front_page": {
                "title": front_page.get("title"),
                "published": front_page.get("published"),
                "tables": front_audit.tables,
                "images": len(front_audit.images),
                "template_placeholders": any(
                    marker in front_text
                    for marker in ("grade / subject", "teacher name")
                ),
            },
            "replacement_home": replacement_pages,
            "modules": {
                "total": len(modules),
                "week_modules": len(week_modules),
                "published_week_modules": published_week_modules,
                "orientation_published": bool(
                    orientation and orientation[0].get("published")
                ),
                "teacher_module_published": bool(
                    teacher_modules and teacher_modules[0].get("published")
                ),
            },
            "navigation": {
                "active": active_tabs,
                "core_present": sorted(CORE_TABS & active_tab_ids),
                "extra": extra_tabs,
            },
            "assignment_groups": group_rows,
            "legacy_groups": legacy_groups,
            "published_pages": published_pages,
            "must_fix": must_fix,
            "warnings": warnings,
            "ready_for_publication": not must_fix and not warnings,
        }
        print(json.dumps(snapshot, indent=2))
        return 0 if snapshot["ready_for_publication"] else 2


def main() -> int:
    if "--preflight" in sys.argv[1:]:
        print(
            "Preflight passed: publication audit is read-only and expects one stdin token."
        )
        return 0
    if sys.argv[1:]:
        print("usage: qa_course_publication.py [--preflight]", file=sys.stderr)
        return 2
    global httpx
    try:
        import httpx
    except ModuleNotFoundError:
        print(
            "httpx is required; run through `uv run --with httpx`",
            file=sys.stderr,
        )
        return 2
    token = sys.stdin.readline().strip()
    if not token:
        print("Canvas token required on stdin", file=sys.stderr)
        return 2
    return asyncio.run(run(token))


if __name__ == "__main__":
    raise SystemExit(main())
