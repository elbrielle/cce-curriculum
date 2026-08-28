#!/usr/bin/env python3
"""Prepare or apply the source-course Student Guide copy-button repair.

The desired Student Guide body is rebuilt from the immutable pre-panel backup.
Only reviewed response-work PDF anchors are retargeted to the matching Google
Doc ``/copy`` URL. The obsolete generic Google-Doc aside is removed. Days that
have no eligible response-work anchor receive one compact, lesson-specific
button without route-selection prose.

Prepare is read-only. Apply requires an explicitly named immutable plan, its
SHA-256, and a reviewed-plan confirmation. Canvas writes are Page-body-only;
publication and date fields are readback guards and are never sent.
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


ROOT = Path(__file__).resolve().parents[2]
BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
SELECTOR_MAP = (
    ROOT / "build/google_docs/student_response_link_selector_inventory.json"
)
REGISTRY = ROOT / "build/google_docs/student_response_route_registry.json"
SOURCE_BACKUP = (
    Path.home()
    / ".config/canvas-fleet-parity/cce/source-response-routes/backups"
    / "course-98060-response-routes-20260826T010841.246973Z.json"
)
APPLIED_SOURCE_PLAN = (
    Path.home()
    / ".config/canvas-fleet-parity/cce/source-response-routes/plans"
    / "course-98060-response-routes-20260826T010619.949837Z.json"
)
APPLIED_SOURCE_PLAN_SHA256 = (
    "9cc7b6f27ad03fcf947ff5e1987c8ef9fc941e2142ab7dc65d320b6c1f07e00c"
)
PLAN_ROOT = (
    Path.home()
    / ".config/canvas-fleet-parity/cce/source-student-button-repair/plans"
)
BACKUP_ROOT = (
    Path.home()
    / ".config/canvas-fleet-parity/cce/source-student-button-repair/backups"
)
BLOCK_ID = "cce-student-google-doc"
EXPECTED_ROUTE_COUNT = 180
PAGE_DATE_FIELDS = ("todo_date", "publish_at", "unlock_at", "lock_at")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
READBACK_DELAYS = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)


class RepairError(RuntimeError):
    """A selector, identity, mutation, or readback guard failed closed."""


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


def expected_day_keys() -> set[str]:
    keys = {
        f"1SW-Wk{week}-Day{day}"
        for week in range(0, 6)
        for day in range(1, 6)
    }
    keys.update(
        f"{six_weeks}SW-Wk{week}-Day{day}"
        for six_weeks in range(2, 7)
        for week in range(1, 7)
        for day in range(1, 6)
    )
    if len(keys) != EXPECTED_ROUTE_COUNT:
        raise AssertionError("CCE day-address invariant failed")
    return keys


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RepairError(f"Could not read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RepairError(f"JSON root must be an object: {path}")
    return value


def write_private_immutable(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path.parent, 0o700)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(stable_json(payload))
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    os.chmod(path, 0o400)


def require_private_immutable(path: Path, *, label: str) -> Path:
    expanded = path.expanduser()
    if expanded.is_symlink():
        raise RepairError(f"{label} must not be a symlink")
    resolved = expanded.resolve()
    if not resolved.is_file():
        raise RepairError(f"{label} is not a regular file: {resolved}")
    mode = resolved.stat().st_mode & 0o777
    if mode & 0o077 or mode & 0o222:
        raise RepairError(
            f"{label} must be private and immutable; found mode {mode:04o}"
        )
    return resolved


def token_headers() -> dict[str, str]:
    token = sys.stdin.readline().strip()
    if not token:
        raise RepairError("Canvas token required on stdin")
    return {"Authorization": f"Bearer {token}"}


def visible_text(fragment: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def anchor_records(body: str) -> list[dict]:
    records = []
    for match in re.finditer(r"<a\b([^>]*)>(.*?)</a>", body, re.I | re.S):
        open_end = body.find(">", match.start()) + 1
        if open_end <= match.start():
            raise RepairError("Unterminated anchor opening tag")
        open_tag = body[match.start() : open_end]
        href_match = re.search(r'\bhref\s*=\s*(["\'])(.*?)\1', open_tag, re.I | re.S)
        if not href_match:
            continue
        records.append(
            {
                "start": match.start(),
                "end": match.end(),
                "open_end": open_end,
                "open_tag": open_tag,
                "inner": match.group(2),
                "inner_start": open_end,
                "inner_end": open_end + len(match.group(2)),
                "text": visible_text(match.group(2)),
                "href": html.unescape(href_match.group(2)),
                "href_value_start": match.start() + href_match.start(2),
                "href_value_end": match.start() + href_match.end(2),
            }
        )
    return records


def legacy_aside_range(body: str) -> tuple[int, int] | None:
    pattern = re.compile(
        rf'<aside\b[^>]*\bid\s*=\s*(["\']){re.escape(BLOCK_ID)}\1[^>]*>'
        r".*?</aside>",
        re.I | re.S,
    )
    matches = list(pattern.finditer(body))
    if len(matches) > 1:
        raise RepairError(f"Found {len(matches)} legacy Google Doc asides")
    return (matches[0].start(), matches[0].end()) if matches else None


def exact_heading_range(body: str, route: dict) -> tuple[int, int]:
    heading = route["insertion_heading"]
    matches = []
    for match in re.finditer(
        r"<(h[1-6])\b[^>]*>.*?</\1>", body, re.I | re.S
    ):
        element = match.group(0)
        if (
            visible_text(element) == heading["text"]
            and match.group(1).lower() == heading["tag"]
            and sha256_text(element) == heading["element_sha256"]
        ):
            matches.append((match.start(), match.end()))
    if len(matches) != 1:
        raise RepairError(
            f"{route['route_id']} exact insertion heading matched {len(matches)} elements"
        )
    return matches[0]


def _remove_canvas_file_metadata(open_tag: str) -> str:
    result = open_tag
    for attribute in ("data-api-endpoint", "data-api-returntype"):
        result, count = re.subn(
            rf"\s+{attribute}\s*=\s*([\"']).*?\1",
            "",
            result,
            count=1,
            flags=re.I | re.S,
        )
        if count != 1:
            raise RepairError(f"Selected file anchor lacks {attribute}")
    return result


def retarget_selected_anchors(body: str, route: dict) -> tuple[str, list[dict]]:
    edits: list[tuple[int, int, str]] = []
    evidence = []
    records = anchor_records(body)
    for selector in route["selectors"]:
        matches = []
        for record in records:
            file_match = re.search(r"/files/(\d+)", record["href"])
            if (
                record["text"] == selector["anchor_text"]
                and file_match
                and int(file_match.group(1)) == selector["source_file_id"]
                and sha256_text(record["href"]) == selector["source_href_sha256"]
                and sha256_text(record["open_tag"])
                == selector["source_open_tag_sha256"]
            ):
                matches.append(record)
        if len(matches) != 1:
            raise RepairError(
                f"{route['route_id']} selector {selector['anchor_text']!r} "
                f"matched {len(matches)} anchors"
            )
        record = matches[0]
        new_open_tag = record["open_tag"]
        href_match = re.search(
            r'\bhref\s*=\s*(["\'])(.*?)\1', new_open_tag, re.I | re.S
        )
        if not href_match:
            raise RepairError("Selected anchor lost its href")
        new_open_tag = (
            new_open_tag[: href_match.start(2)]
            + route["copy_url"]
            + new_open_tag[href_match.end(2) :]
        )
        new_open_tag = _remove_canvas_file_metadata(new_open_tag)
        edits.append((record["start"], record["open_end"], new_open_tag))
        replacement_text = selector.get("replacement_anchor_text")
        if replacement_text is not None:
            if re.search(r"<[^>]+>", record["inner"]):
                raise RepairError(
                    f"{route['route_id']} reviewed label replacement contains nested HTML"
                )
            edits.append(
                (
                    record["inner_start"],
                    record["inner_end"],
                    html.escape(replacement_text),
                )
            )
        evidence.append(
            {
                "anchor_text": selector["anchor_text"],
                "source_file_id": selector["source_file_id"],
                "source_file_display_name": selector["source_file_display_name"],
                "before_open_tag_sha256": sha256_text(record["open_tag"]),
                "after_open_tag_sha256": sha256_text(new_open_tag),
                "replacement_anchor_text": replacement_text,
            }
        )
    transformed = body
    for start, end, replacement in sorted(edits, reverse=True):
        transformed = transformed[:start] + replacement + transformed[end:]
    return transformed, evidence


def bare_button(copy_url: str, label: str) -> str:
    return (
        f'<p><a href="{html.escape(copy_url, quote=True)}" target="_blank" '
        'style="display:inline-block;background:#1f617a;color:#fff;'
        'padding:11px 18px;border-radius:6px;text-decoration:none">'
        f"<strong>{html.escape(label)}</strong></a></p>"
    )


def desired_body(original_body: str, route: dict) -> tuple[str, dict]:
    aside = legacy_aside_range(original_body)
    body = original_body
    if route["strategy"] == "retarget_response_work_pdf_anchor":
        body, anchor_evidence = retarget_selected_anchors(body, route)
        # Anchor edits before the aside do not change the aside offsets in the
        # original string only when applied in reverse. Re-find after edits.
        current_aside = legacy_aside_range(body)
        if current_aside:
            body = body[: current_aside[0]] + body[current_aside[1] :]
        method = "retarget_existing_response_work_pdf"
    elif route["strategy"] == "insert_bare_copy_button":
        anchor_evidence = []
        button = bare_button(route["copy_url"], route["button_label"])
        if aside is not None:
            body = body[: aside[0]] + body[aside[1] :]
        start, end = exact_heading_range(body, route)
        line_start = body.rfind("\n", 0, start) + 1
        indent = body[line_start:start]
        if indent.strip():
            indent = ""
        suffix = body[end:]
        insertion = "\n" + indent + button
        if suffix and not suffix.startswith("\n"):
            insertion += "\n" + indent
        body = body[:end] + insertion + suffix
        method = "insert_after_reviewed_point_of_use_heading"
    else:
        raise RepairError(f"Unknown route strategy: {route['strategy']}")

    if legacy_aside_range(body) is not None:
        raise RepairError(f"{route['route_id']} still contains the generic aside")
    copy_count = sum(
        record["href"] == route["copy_url"] for record in anchor_records(body)
    )
    expected_count = len(route.get("selectors", [])) or 1
    if copy_count != expected_count:
        raise RepairError(
            f"{route['route_id']} has {copy_count} copy links; expected {expected_count}"
        )
    forbidden = (
        "Type in your copy and submit or share it the way your teacher directs",
        "Choose one response home before class",
        "Type today’s work in Google Docs",
    )
    if any(value in body for value in forbidden):
        raise RepairError(f"{route['route_id']} retains generic process language")
    return body, {
        "method": method,
        "retargeted_anchor_count": len(anchor_evidence),
        "copy_link_count": copy_count,
        "removed_legacy_aside": aside is not None,
        "anchor_evidence": anchor_evidence,
    }


def load_inputs(*, allow_historical_registry: bool = False) -> tuple[dict, dict, dict]:
    inventory = load_json(SELECTOR_MAP)
    registry = load_json(REGISTRY)
    backup_path = require_private_immutable(SOURCE_BACKUP, label="source backup")
    backup = load_json(backup_path)
    applied_plan_path = require_private_immutable(
        APPLIED_SOURCE_PLAN, label="applied source plan"
    )
    if sha256_file(applied_plan_path) != APPLIED_SOURCE_PLAN_SHA256:
        raise RepairError("Applied source plan SHA-256 mismatch")
    applied_plan = load_json(applied_plan_path)
    if inventory.get("review_status") != "reviewed":
        raise RepairError("Selector inventory is not reviewed")
    summary = inventory.get("summary", {})
    expected_summary = {
        "day_count": 180,
        "selector_count": 185,
        "days_with_selectors": 166,
        "days_without_selectors": 14,
        "selector_multiplicity": {"0": 14, "1": 151, "2": 12, "3": 2, "4": 1},
        "classification_counts": {
            "daily_exit_ticket_pdf": 8,
            "student_response_work_pdf": 177,
        },
        "reviewed_anchor_text_replacement_count": 2,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise RepairError(
                f"Selector-inventory {key} differs from the reviewed contract"
            )
    if (
        inventory.get("inputs", {})
        .get("historical_route_registry", {})
        .get("sha256")
        != sha256_file(REGISTRY)
    ):
        raise RepairError("Selector inventory was not built from this registry")
    inventory_days = inventory.get("days")
    registry_routes = registry.get("routes")
    if not isinstance(inventory_days, list) or not isinstance(registry_routes, list):
        raise RepairError("Selector inventory or registry routes are invalid")
    selector_keys = {row.get("route_id") for row in inventory_days}
    registry_keys = {row.get("route_id") for row in registry_routes}
    if selector_keys != expected_day_keys() or registry_keys != expected_day_keys():
        raise RepairError("Inputs do not contain the exact 180-day address set")
    if allow_historical_registry:
        if (
            registry.get("review_status") != "historical"
            or registry.get("mutation_authority") != "none_requires_new_promotion"
        ):
            raise RepairError("Expected the explicitly historical registry fixture")
    elif (
        registry.get("review_status") != "reviewed"
        or registry.get("mutation_authority")
        != "reviewed_source_course_body_plan_only"
    ):
        raise RepairError(
            "Response-route registry cannot authorize work; promote a fresh draft first"
        )
    if backup.get("course_id") != COURSE_ID:
        raise RepairError("Source backup is for the wrong course")
    backup_by_route = {
        row["route_id"]: row
        for row in backup.get("pages", [])
        if row.get("role") == "student"
    }
    registry_by_route = {row["route_id"]: row for row in registry_routes}
    applied_targets = {
        row["route_id"]: row
        for row in applied_plan.get("targets", [])
        if row.get("role") == "student"
    }
    if set(applied_targets) != expected_day_keys():
        raise RepairError("Applied source plan lacks the exact 180 Student Guides")
    normalised_routes = []
    for day in inventory_days:
        route_id = day["route_id"]
        backup_page = backup_by_route.get(route_id)
        registry_row = registry_by_route[route_id]
        applied_target = applied_targets[route_id]
        if not backup_page:
            raise RepairError(f"{route_id}: missing immutable backup Page")
        if sha256_text(backup_page["body"]) != day["student_page"][
            "expected_before_body_sha256"
        ]:
            raise RepairError(f"{route_id}: selector/backup body hash mismatch")
        if (
            backup_page["page_id"] != day["student_page"]["page_id"]
            or backup_page["page_url"] != day["student_page"]["page_url"]
        ):
            raise RepairError(f"{route_id}: selector/backup identity mismatch")
        if (
            applied_target.get("issues") != []
            or applied_target.get("page_id") != backup_page["page_id"]
            or applied_target.get("page_url") != backup_page["page_url"]
            or sha256_text(applied_target.get("after_body") or "")
            != applied_target.get("after_body_sha256")
        ):
            raise RepairError(f"{route_id}: applied-plan target guard mismatch")
        copy_url = day["google_doc_copy_url"]
        if copy_url != registry_row["google_doc"]["copy_url"]:
            raise RepairError(f"{route_id}: selector/registry copy URL mismatch")
        if day["selectors"]:
            selectors = []
            records = anchor_records(backup_page["body"])
            for raw in day["selectors"]:
                matches = []
                for record in records:
                    file_match = re.search(r"/files/(\d+)", record["href"])
                    if (
                        record["text"] == raw["anchor_text"]
                        and file_match
                        and int(file_match.group(1))
                        == raw["expected_canvas_file_id"]
                        and sha256_text(record["href"])
                        == raw["expected_old_href_complete_sha256"]
                    ):
                        matches.append(record)
                if len(matches) != 1:
                    raise RepairError(
                        f"{route_id}: reviewed selector matched {len(matches)} anchors"
                    )
                selectors.append(
                    {
                        "anchor_text": raw["anchor_text"],
                        "source_file_display_name": raw[
                            "expected_canvas_filename"
                        ],
                        "source_file_id": raw["expected_canvas_file_id"],
                        "source_href_sha256": raw[
                            "expected_old_href_complete_sha256"
                        ],
                        "source_open_tag_sha256": sha256_text(
                            matches[0]["open_tag"]
                        ),
                        "classification": raw["classification"],
                        "context_heading": raw["context_heading"],
                        "replacement_anchor_text": raw.get(
                            "replacement_anchor_text"
                        ),
                        "remove_stale_canvas_file_metadata": True,
                    }
                )
            normalised_routes.append(
                {
                    "route_id": route_id,
                    "strategy": "retarget_response_work_pdf_anchor",
                    "copy_url": copy_url,
                    "selectors": selectors,
                }
            )
        else:
            review = day.get("no_selector_review") or {}
            insertion = review.get(
                "suggested_bare_button_insertion_if_separately_approved"
            ) or {}
            heading = insertion.get("heading_signature")
            if not isinstance(heading, dict):
                raise RepairError(f"{route_id}: no reviewed heading signature")
            lesson_title = registry_row["title"].split("|")[-1].strip()
            normalised_routes.append(
                {
                    "route_id": route_id,
                    "strategy": "insert_bare_copy_button",
                    "copy_url": copy_url,
                    "button_label": f"Make your copy: {lesson_title}",
                    "insertion_heading": heading,
                    "review_reason": review.get("reason"),
                }
            )
    return {
        "review_status": "reviewed",
        "summary": {
            "route_count": 180,
            "retarget_route_count": 166,
            "retarget_anchor_count": 185,
            "bare_button_route_count": 14,
            "hold_count": 0,
        },
        "routes": normalised_routes,
        "applied_source_plan": {
            "path": str(applied_plan_path),
            "sha256": APPLIED_SOURCE_PLAN_SHA256,
            "student_targets": applied_targets,
        },
    }, registry, backup


def page_guards(page: dict) -> dict:
    published = page.get("published")
    front_page = page.get("front_page")
    if not isinstance(published, bool) or not isinstance(front_page, bool):
        raise RepairError("Canvas Page publication/front-page readback is invalid")
    return {
        "published": published,
        "front_page": front_page,
        "dates": {field: page.get(field) for field in PAGE_DATE_FIELDS},
    }


def classify_prepare_body(live_body: str, known_bad_body: str, desired: str) -> str:
    if live_body == desired:
        return "after"
    if live_body == known_bad_body:
        return "before"
    raise RepairError("Live Student Guide is neither known bad-panel after nor desired")


async def get_page(client: httpx.AsyncClient, slug: str) -> dict:
    response = await client.get(f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{slug}")
    response.raise_for_status()
    value = response.json()
    if not isinstance(value, dict):
        raise RepairError(f"Canvas returned a non-object Page for {slug}")
    return value


def default_plan_path() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    return PLAN_ROOT / f"course-{COURSE_ID}-student-copy-button-repair-{stamp}.json"


async def prepare(args: argparse.Namespace) -> dict:
    selectors, registry, backup = load_inputs()
    selector_by_route = {row["route_id"]: row for row in selectors["routes"]}
    registry_by_route = {row["route_id"]: row for row in registry["routes"]}
    backup_by_route = {
        row["route_id"]: row
        for row in backup["pages"]
        if row.get("role") == "student"
    }
    applied_by_route = selectors["applied_source_plan"]["student_targets"]
    if set(backup_by_route) != expected_day_keys():
        raise RepairError("Source backup lacks the exact 180 Student Guide set")

    headers = token_headers()
    targets = []
    async with httpx.AsyncClient(
        headers=headers, timeout=60, follow_redirects=True
    ) as client:
        for route_id in sorted(expected_day_keys()):
            selector = selector_by_route[route_id]
            registry_row = registry_by_route[route_id]
            backup_page = backup_by_route[route_id]
            if selector["copy_url"] != registry_row["google_doc"]["copy_url"]:
                raise RepairError(f"{route_id}: selector/registry copy URL mismatch")
            desired, proof = desired_body(backup_page["body"], selector)
            live = await get_page(client, backup_page["page_url"])
            if live.get("page_id") != backup_page["page_id"]:
                raise RepairError(f"{route_id}: Page identity changed")
            if live.get("url") != backup_page["page_url"]:
                raise RepairError(f"{route_id}: Page URL changed")
            applied_target = applied_by_route[route_id]
            if live.get("title") != applied_target["title"]:
                raise RepairError(f"{route_id}: Page title changed")
            prepared_state = classify_prepare_body(
                live.get("body") or "",
                applied_target["after_body"],
                desired,
            )
            guards = page_guards(live)
            targets.append(
                {
                    "route_id": route_id,
                    "role": "student",
                    "course_id": COURSE_ID,
                    "page_id": live["page_id"],
                    "page_url": live["url"],
                    "page_title": applied_target["title"],
                    "before_body": applied_target["after_body"],
                    "before_body_sha256": applied_target["after_body_sha256"],
                    "after_body": desired,
                    "after_body_sha256": sha256_text(desired),
                    "publication_and_date_guard": guards,
                    "mutation_proof": proof,
                    "prepared_live_state": prepared_state,
                    "needs_change": prepared_state == "before",
                }
            )
    plan = {
        "schema_version": 1,
        "artifact": "CCE source Student Guide copy-button repair plan",
        "status": "prepared_pending_review",
        "mode": "read_only_prepare",
        "course_id": COURSE_ID,
        "created_at": utc_now(),
        "inputs": {
            "selector_map_path": str(SELECTOR_MAP),
            "selector_map_sha256": sha256_file(SELECTOR_MAP),
            "registry_path": str(REGISTRY),
            "registry_sha256": sha256_file(REGISTRY),
            "source_backup_path": str(SOURCE_BACKUP),
            "source_backup_sha256": sha256_file(SOURCE_BACKUP),
            "applied_source_plan_path": str(APPLIED_SOURCE_PLAN),
            "applied_source_plan_sha256": APPLIED_SOURCE_PLAN_SHA256,
        },
        "safety_contract": {
            "student_pages_only": True,
            "body_only_put": True,
            "publication_fields_sent": 0,
            "date_fields_sent": 0,
            "post_or_delete_paths": 0,
            "stop_on_mismatch": True,
        },
        "summary": {
            "target_count": len(targets),
            "change_count": sum(row["needs_change"] for row in targets),
            "current_count": sum(not row["needs_change"] for row in targets),
            "retargeted_anchor_count": sum(
                row["mutation_proof"]["retargeted_anchor_count"] for row in targets
            ),
            "bare_button_count": sum(
                row["mutation_proof"]["retargeted_anchor_count"] == 0
                for row in targets
            ),
        },
        "targets": targets,
    }
    if plan["summary"]["target_count"] != EXPECTED_ROUTE_COUNT:
        raise RepairError("Prepared plan does not contain 180 Student Guides")
    output = Path(args.output).expanduser() if args.output else default_plan_path()
    write_private_immutable(output, plan)
    return {"plan": str(output), "plan_sha256": sha256_file(output), **plan["summary"]}


def body_only_payload(body: str) -> dict[str, str]:
    return {"wiki_page[body]": body}


async def put_body(client: httpx.AsyncClient, slug: str, body: str) -> dict:
    response = await client.put(
        f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{slug}",
        data=body_only_payload(body),
    )
    response.raise_for_status()
    value = response.json()
    if not isinstance(value, dict):
        raise RepairError(f"Canvas returned a non-object PUT response for {slug}")
    return value


def verify_live_identity_and_guards(target: dict, live: dict) -> None:
    if live.get("page_id") != target["page_id"] or live.get("url") != target["page_url"]:
        raise RepairError(f"{target['route_id']}: Page identity mismatch")
    if page_guards(live) != target["publication_and_date_guard"]:
        raise RepairError(f"{target['route_id']}: publication/date guard changed")
    if live.get("title") != target["page_title"]:
        raise RepairError(f"{target['route_id']}: Page title changed")


def classify_live_body(target: dict, live: dict) -> str:
    verify_live_identity_and_guards(target, live)
    body = live.get("body") or ""
    if body == target["after_body"]:
        return "after"
    if body == target["before_body"]:
        return "before"
    raise RepairError(f"{target['route_id']}: unexpected third body")


async def readback_after(
    client: httpx.AsyncClient, target: dict
) -> dict:
    for delay in READBACK_DELAYS:
        if delay:
            await asyncio.sleep(delay)
        live = await get_page(client, target["page_url"])
        state = classify_live_body(target, live)
        if state == "after":
            return live
        # Only an exact stale-before body is retryable. Guard changes and any
        # third body raise immediately in ``classify_live_body``.
    raise RepairError(f"{target['route_id']}: exact post-write readback failed")


async def apply(args: argparse.Namespace) -> dict:
    if not args.confirm_reviewed_plan:
        raise RepairError("Apply requires --confirm-reviewed-plan")
    if not args.plan or not args.plan_sha256:
        raise RepairError("Apply requires --plan and --plan-sha256")
    if not SHA256_RE.fullmatch(args.plan_sha256):
        raise RepairError("--plan-sha256 is not SHA-256")
    plan_path = require_private_immutable(Path(args.plan), label="repair plan")
    if sha256_file(plan_path) != args.plan_sha256:
        raise RepairError("Repair plan SHA-256 mismatch")
    plan = load_json(plan_path)
    if (
        plan.get("course_id") != COURSE_ID
        or plan.get("status") != "prepared_pending_review"
        or plan.get("summary", {}).get("target_count") != EXPECTED_ROUTE_COUNT
    ):
        raise RepairError("Repair plan does not satisfy the source-course contract")
    if plan.get("inputs", {}).get("selector_map_sha256") != sha256_file(SELECTOR_MAP):
        raise RepairError("Selector map changed after prepare")
    if plan.get("inputs", {}).get("registry_sha256") != sha256_file(REGISTRY):
        raise RepairError("Registry changed after prepare")
    if plan.get("inputs", {}).get("source_backup_sha256") != sha256_file(SOURCE_BACKUP):
        raise RepairError("Source backup changed after prepare")
    if (
        plan.get("inputs", {}).get("applied_source_plan_sha256")
        != APPLIED_SOURCE_PLAN_SHA256
        or sha256_file(APPLIED_SOURCE_PLAN) != APPLIED_SOURCE_PLAN_SHA256
    ):
        raise RepairError("Applied source plan changed after prepare")

    targets = plan["targets"]
    if args.pilot_route:
        targets = [row for row in targets if row["route_id"] == args.pilot_route]
        if len(targets) != 1:
            raise RepairError(f"Pilot route is not in the plan: {args.pilot_route}")
    headers = token_headers()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup_path = BACKUP_ROOT / f"course-{COURSE_ID}-student-buttons-{timestamp}.json"
    async with httpx.AsyncClient(
        headers=headers, timeout=60, follow_redirects=True
    ) as client:
        # Full selected-scope preflight before the first write. This accepts an
        # exact after body so a verified pilot or interrupted run can resume.
        live_pages = []
        states: dict[str, str] = {}
        for target in targets:
            live = await get_page(client, target["page_url"])
            state = classify_live_body(target, live)
            states[target["route_id"]] = state
            live_pages.append(
                {
                    "route_id": target["route_id"],
                    "page_id": live["page_id"],
                    "page_url": live["url"],
                    "page_title": live.get("title"),
                    "body": live.get("body") or "",
                    "body_sha256": sha256_text(live.get("body") or ""),
                    "publication_and_date_guard": page_guards(live),
                    "preflight_state": state,
                }
            )
        write_private_immutable(
            backup_path,
            {
                "schema_version": 1,
                "artifact": "CCE source Student Guide button-repair pre-apply backup",
                "course_id": COURSE_ID,
                "created_at": utc_now(),
                "plan_sha256": args.plan_sha256,
                "pilot_route": args.pilot_route,
                "pages": live_pages,
            },
        )

        changed = 0
        for target in targets:
            if states[target["route_id"]] == "after":
                continue
            await put_body(client, target["page_url"], target["after_body"])
            await readback_after(client, target)
            changed += 1
        # Independent final selected-scope readback.
        for target in targets:
            live = await get_page(client, target["page_url"])
            if classify_live_body(target, live) != "after":
                raise RepairError(f"{target['route_id']}: final body is not exact after")
    return {
        "status": "pilot_exactly_verified" if args.pilot_route else "applied_and_exactly_verified",
        "course_id": COURSE_ID,
        "target_count": len(targets),
        "body_put_count": changed,
        "publication_fields_sent": 0,
        "date_fields_sent": 0,
        "backup": str(backup_path),
        "plan_sha256": args.plan_sha256,
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    subparsers = value.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare", help="Read-only plan creation")
    prepare_parser.add_argument("--output")
    apply_parser = subparsers.add_parser("apply", help="Guarded body-only apply")
    apply_parser.add_argument("--plan", required=True)
    apply_parser.add_argument("--plan-sha256", required=True)
    apply_parser.add_argument("--confirm-reviewed-plan", action="store_true")
    apply_parser.add_argument("--pilot-route")
    return value


async def async_main() -> dict:
    args = parser().parse_args()
    return await (prepare(args) if args.command == "prepare" else apply(args))


def main() -> None:
    try:
        result = asyncio.run(async_main())
    except (RepairError, httpx.HTTPError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    print(stable_json(result), end="")


if __name__ == "__main__":
    main()
