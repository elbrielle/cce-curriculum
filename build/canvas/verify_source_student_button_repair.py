#!/usr/bin/env python3
"""Independently verify the live CCE source response-route repair.

This verifier is read-only. It compares all 180 live Student Guides with the
final immutable repair plan and all 180 Teacher Guides with the immutable
source response-route plan, verifies publication/date guards and response-link
semantics, then writes a private immutable receipt. It has no Canvas write path.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import html
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx


BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
FINAL_REPAIR_PLAN = (
    Path.home()
    / ".config/canvas-fleet-parity/cce/source-student-button-repair/plans"
    / "course-98060-student-copy-button-repair-20260826T030656.618984Z.json"
)
FINAL_REPAIR_PLAN_SHA256 = (
    "1f7a0172f608862666e3117a8045606e5fbbf1828962f6e88a71cfdbb60f3111"
)
SOURCE_PLAN = (
    Path.home()
    / ".config/canvas-fleet-parity/cce/source-response-routes/plans"
    / "course-98060-response-routes-20260826T010619.949837Z.json"
)
SOURCE_PLAN_SHA256 = (
    "9cc7b6f27ad03fcf947ff5e1987c8ef9fc941e2142ab7dc65d320b6c1f07e00c"
)
SOURCE_BACKUP = (
    Path.home()
    / ".config/canvas-fleet-parity/cce/source-response-routes/backups"
    / "course-98060-response-routes-20260826T010841.246973Z.json"
)
FULL_APPLY_BACKUP = (
    Path.home()
    / ".config/canvas-fleet-parity/cce/source-student-button-repair/backups"
    / "course-98060-student-buttons-20260826T031101.833138Z.json"
)
FULL_APPLY_BACKUP_SHA256 = (
    "0c1981c63162b6dcb82983e57aad8ccc3a3fed7ad13fb15ba898b9e73662e412"
)
REGISTRY = (
    Path(__file__).resolve().parents[2]
    / "build/google_docs/student_response_route_registry.json"
)
RECEIPT_ROOT = (
    Path.home()
    / ".config/canvas-fleet-parity/cce/source-student-button-repair/receipts"
)
PAGE_DATE_FIELDS = ("todo_date", "publish_at", "unlock_at", "lock_at")
BLOCK_ID = "cce-student-google-doc"
EXPECTED_ROUTE_COUNT = 180


class VerifyError(RuntimeError):
    """Live state does not satisfy the reviewed repair contract."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def load_pinned(path: Path, expected_sha: str, label: str) -> dict:
    resolved = path.expanduser().resolve()
    if not resolved.is_file() or resolved.is_symlink():
        raise VerifyError(f"{label} is not a regular pinned file")
    if sha256_file(resolved) != expected_sha:
        raise VerifyError(f"{label} SHA-256 mismatch")
    value = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise VerifyError(f"{label} root is not an object")
    return value


def write_private_immutable(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path.parent, 0o700)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(stable_json(value))
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    os.chmod(path, 0o400)


def token_headers() -> dict[str, str]:
    token = sys.stdin.readline().strip()
    if not token:
        raise VerifyError("Canvas token required on stdin")
    return {"Authorization": f"Bearer {token}"}


def visible_text(fragment: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def anchors(body: str) -> list[dict[str, str]]:
    result = []
    for match in re.finditer(r"<a\b([^>]*)>(.*?)</a>", body, re.I | re.S):
        href_match = re.search(
            r'\bhref\s*=\s*(["\'])(.*?)\1', match.group(1), re.I | re.S
        )
        if href_match:
            result.append(
                {
                    "href": html.unescape(href_match.group(2)),
                    "text": visible_text(match.group(2)),
                }
            )
    return result


def route_panel(body: str) -> str:
    pattern = re.compile(
        rf'<aside\b[^>]*\bid\s*=\s*(["\']){BLOCK_ID}\1[^>]*>.*?</aside>',
        re.I | re.S,
    )
    matches = list(pattern.finditer(body))
    if len(matches) != 1:
        raise VerifyError(f"Expected one teacher response panel; found {len(matches)}")
    return matches[0].group(0)


def page_dates(page: dict) -> dict:
    return {field: page.get(field) for field in PAGE_DATE_FIELDS}


async def get_page(
    client: httpx.AsyncClient, semaphore: asyncio.Semaphore, slug: str
) -> dict:
    async with semaphore:
        response = await client.get(
            f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{slug}"
        )
        response.raise_for_status()
        value = response.json()
    if not isinstance(value, dict):
        raise VerifyError(f"Canvas returned a non-object Page for {slug}")
    return value


def verify_identity(live: dict, target: dict, role: str) -> None:
    if (
        live.get("page_id") != target["page_id"]
        or live.get("url") != target["page_url"]
        or live.get("title") != target["title"]
    ):
        raise VerifyError(f"{target['route_id']} {role}: identity/title mismatch")


async def verify(output: Path | None) -> dict:
    repair_plan = load_pinned(
        FINAL_REPAIR_PLAN, FINAL_REPAIR_PLAN_SHA256, "final repair plan"
    )
    source_plan = load_pinned(SOURCE_PLAN, SOURCE_PLAN_SHA256, "source plan")
    full_backup = load_pinned(
        FULL_APPLY_BACKUP, FULL_APPLY_BACKUP_SHA256, "full apply backup"
    )
    source_backup = json.loads(SOURCE_BACKUP.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    student_targets = {row["route_id"]: row for row in repair_plan["targets"]}
    teacher_targets = {
        row["route_id"]: row
        for row in source_plan["targets"]
        if row.get("role") == "teacher"
    }
    registry_routes = {row["route_id"]: row for row in registry["routes"]}
    full_backup_students = {row["route_id"]: row for row in full_backup["pages"]}
    source_backup_teachers = {
        row["route_id"]: row
        for row in source_backup["pages"]
        if row.get("role") == "teacher"
    }
    for name, mapping in (
        ("student targets", student_targets),
        ("teacher targets", teacher_targets),
        ("registry", registry_routes),
        ("student apply backup", full_backup_students),
        ("teacher source backup", source_backup_teachers),
    ):
        if len(mapping) != EXPECTED_ROUTE_COUNT:
            raise VerifyError(f"{name} does not contain 180 routes")

    headers = token_headers()
    semaphore = asyncio.Semaphore(12)
    async with httpx.AsyncClient(
        headers=headers,
        timeout=60,
        follow_redirects=True,
        limits=httpx.Limits(max_connections=12, max_keepalive_connections=12),
    ) as client:
        student_live, teacher_live = await asyncio.gather(
            asyncio.gather(
                *(
                    get_page(client, semaphore, target["page_url"])
                    for target in student_targets.values()
                )
            ),
            asyncio.gather(
                *(
                    get_page(client, semaphore, target["page_url"])
                    for target in teacher_targets.values()
                )
            ),
        )

    student_records = []
    mapped_copy_links = 0
    bare_buttons = 0
    student_published = {True: 0, False: 0}
    for route_id, live in zip(student_targets, student_live):
        target = student_targets[route_id]
        target_for_identity = {**target, "title": target["page_title"]}
        verify_identity(live, target_for_identity, "student")
        body = live.get("body") or ""
        if body != target["after_body"]:
            raise VerifyError(f"{route_id} student: body differs from repair plan")
        backup_guard = full_backup_students[route_id][
            "publication_and_date_guard"
        ]
        if (
            live.get("published") != backup_guard["published"]
            or live.get("front_page") != backup_guard["front_page"]
            or page_dates(live) != backup_guard["dates"]
        ):
            raise VerifyError(f"{route_id} student: publication/date guard changed")
        if re.search(
            rf'<aside\b[^>]*\bid\s*=\s*(["\']){BLOCK_ID}\1', body, re.I
        ):
            raise VerifyError(f"{route_id} student: generic panel remains")
        forbidden = (
            "Type in your copy and submit or share it the way your teacher directs",
            "Choose one response home before class",
            "Type today’s work in Google Docs",
            "Complete this work in one place only",
        )
        if any(value in body for value in forbidden):
            raise VerifyError(f"{route_id} student: generic process prose remains")
        copy_url = registry_routes[route_id]["google_doc"]["copy_url"]
        copy_anchors = [row for row in anchors(body) if row["href"] == copy_url]
        mapped = target["mutation_proof"]["retargeted_anchor_count"]
        expected_copy_count = mapped or 1
        if len(copy_anchors) != expected_copy_count:
            raise VerifyError(f"{route_id} student: copy-link count mismatch")
        if mapped:
            mapped_copy_links += mapped
        else:
            bare_buttons += 1
            if "background:#1f617a" not in body:
                raise VerifyError(f"{route_id} student: bare button is not CCE teal")
        student_published[bool(live["published"])] += 1
        student_records.append(
            {
                "route_id": route_id,
                "page_id": live["page_id"],
                "page_url": live["url"],
                "body_sha256": sha256_text(body),
                "published": live["published"],
                "front_page": live["front_page"],
                "dates": page_dates(live),
                "mapped_copy_link_count": mapped,
                "bare_button_count": int(mapped == 0),
            }
        )

    teacher_records = []
    teacher_published = {True: 0, False: 0}
    teacher_non_null_dates = 0
    for route_id, live in zip(teacher_targets, teacher_live):
        target = teacher_targets[route_id]
        verify_identity(live, target, "teacher")
        body = live.get("body") or ""
        if body != target["after_body"]:
            raise VerifyError(f"{route_id} teacher: body differs from source plan")
        source_before = source_backup_teachers[route_id]
        if (
            live.get("published") != target["observed_published"]
            or live.get("published") != source_before["published"]
            or live.get("front_page") != source_before["front_page"]
        ):
            raise VerifyError(f"{route_id} teacher: publication/front-page changed")
        route = registry_routes[route_id]
        copy_url = route["google_doc"]["copy_url"]
        pdf_url = route["google_doc"]["pdf_export_url"]
        panel = route_panel(body)
        panel_anchors = anchors(panel)
        if sum(row["href"] == copy_url for row in panel_anchors) != 1:
            raise VerifyError(f"{route_id} teacher: Google copy link mismatch")
        if sum(row["href"] == pdf_url for row in panel_anchors) != 1:
            raise VerifyError(f"{route_id} teacher: same-Doc PDF link mismatch")
        if "OneNote template — link coming soon" not in panel:
            raise VerifyError(f"{route_id} teacher: OneNote placeholder missing")
        if any("OneNote template" in row["text"] for row in panel_anchors):
            raise VerifyError(f"{route_id} teacher: OneNote placeholder is linked")
        dates = page_dates(live)
        teacher_non_null_dates += sum(value is not None for value in dates.values())
        teacher_published[bool(live["published"])] += 1
        teacher_records.append(
            {
                "route_id": route_id,
                "page_id": live["page_id"],
                "page_url": live["url"],
                "body_sha256": sha256_text(body),
                "published": live["published"],
                "front_page": live["front_page"],
                "dates": dates,
                "google_copy_link_count": 1,
                "same_doc_pdf_link_count": 1,
                "onenote_pending_placeholder_count": 1,
            }
        )

    if mapped_copy_links != 185 or bare_buttons != 14:
        raise VerifyError("Student selector/bare-button totals do not match 185/14")
    if teacher_non_null_dates != 0:
        raise VerifyError("Teacher Page date fields are not all null")
    aggregate = sha256_text(
        "\n".join(
            f"{row['route_id']}:{row['body_sha256']}"
            for row in student_records + teacher_records
        )
    )
    receipt = {
        "schema_version": 1,
        "artifact": "CCE source Student-button independent post-apply receipt",
        "status": "passed",
        "mode": "read_only",
        "canvas_writes": 0,
        "course_id": COURSE_ID,
        "created_at": utc_now(),
        "inputs": {
            "repair_plan": {
                "path": str(FINAL_REPAIR_PLAN),
                "sha256": FINAL_REPAIR_PLAN_SHA256,
            },
            "source_plan": {
                "path": str(SOURCE_PLAN),
                "sha256": SOURCE_PLAN_SHA256,
            },
            "full_apply_backup": {
                "path": str(FULL_APPLY_BACKUP),
                "sha256": FULL_APPLY_BACKUP_SHA256,
            },
            "registry_sha256": sha256_file(REGISTRY),
        },
        "summary": {
            "student_page_count": len(student_records),
            "student_exact_after_count": len(student_records),
            "student_mapped_copy_link_count": mapped_copy_links,
            "student_bare_button_count": bare_buttons,
            "student_generic_panel_count": 0,
            "student_process_prose_count": 0,
            "student_published_true": student_published[True],
            "student_published_false": student_published[False],
            "teacher_page_count": len(teacher_records),
            "teacher_exact_source_after_count": len(teacher_records),
            "teacher_google_copy_link_count": len(teacher_records),
            "teacher_same_doc_pdf_link_count": len(teacher_records),
            "teacher_onenote_pending_placeholder_count": len(teacher_records),
            "teacher_published_true": teacher_published[True],
            "teacher_published_false": teacher_published[False],
            "teacher_non_null_date_field_count": teacher_non_null_dates,
            "aggregate_body_sha256": aggregate,
        },
        "preservation_evidence": {
            "student_publication_dates_match_full_apply_backup": True,
            "teacher_publication_front_page_match_source_plan_and_backup": True,
            "teacher_date_fields_currently_all_null": True,
            "teacher_targets_in_student_repair_plan": 0,
        },
        "students": student_records,
        "teachers": teacher_records,
    }
    if output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        output = RECEIPT_ROOT / f"course-{COURSE_ID}-postrepair-{stamp}.json"
    write_private_immutable(output, receipt)
    return {
        "status": "passed",
        "receipt": str(output),
        "receipt_sha256": sha256_file(output),
        **receipt["summary"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = asyncio.run(verify(args.output.expanduser() if args.output else None))
    except (VerifyError, httpx.HTTPError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    print(stable_json(result), end="")


if __name__ == "__main__":
    main()
