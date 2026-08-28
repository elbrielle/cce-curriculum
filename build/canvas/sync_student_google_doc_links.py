#!/usr/bin/env python3
"""Prepare and apply guarded CCE response-home panels on Canvas Pages.

The default mode is a read-only prepare pass. It reads the 180-row student
response-route registry, discovers or verifies the paired Canvas Pages, and
writes a private immutable plan. It never mutates Canvas.

Apply is deliberately a separate operation. It accepts only the canonical
reviewed registry plus an explicitly named immutable plan and plan SHA-256.
Before the first write it sequentially re-reads all 360 Pages and requires the
exact reviewed Page IDs, URL slugs, body hashes, and publication readbacks.
Every mutation is a body-only ``wiki_page[body]`` PUT followed by exact
readback. No publication field is ever sent.

The Canvas token is read from stdin only and is never written to an artifact.
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
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

import httpx


ROOT = Path(__file__).resolve().parents[2]
FINAL_REGISTRY = (
    ROOT / "build" / "google_docs" / "student_response_route_registry.json"
)
DRAFT_REGISTRY = (
    ROOT / "build" / "google_docs" / "student_response_route_registry.draft.json"
)
BASE = "https://learn.irvingisd.net"
DEFAULT_COURSE_ID = 98060
CANONICAL_DRIVE_PREFIX = "VILS27/Units_CCR/"
REVIEWED_STATUS = "reviewed"
EXPECTED_ROUTE_COUNT = 180
EXPECTED_PAGE_COUNT = EXPECTED_ROUTE_COUNT * 2
BLOCK_ID = "cce-student-google-doc"
START = "<!-- CCE_STUDENT_GOOGLE_DOC_START -->"
END = "<!-- CCE_STUDENT_GOOGLE_DOC_END -->"
PAGE_KEY_RE = re.compile(r"^(\d+)SW-Wk(\d+)-Day(\d+)$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DOC_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")
DISCOVERY_TITLE_OVERRIDES = {
    **{
        (f"1SW-Wk0-Day{day}", "teacher"): f"TEACHER: Day {day} Facilitator Guide"
        for day in range(1, 6)
    },
    ("1SW-Wk0-Day1", "student"): (
        "STUDENT: 1SW Wk0 Day 1 - CCE Notebook and First-Week Goal"
    ),
    ("1SW-Wk0-Day5", "student"): (
        "STUDENT: 1SW Wk0 Day 5 - Career Perks, Neutrals, and Quirks"
    ),
    ("1SW-Wk3-Day5", "student"): (
        "STUDENT: 1SW Wk3 Day 5 - Learning Style Quiz and Lesson"
    ),
    ("2SW-Wk3-Day5", "student"): (
        "STUDENT: 2SW Wk3 Day 5 - Build a Nursing Career Evidence Map"
    ),
    ("3SW-Wk1-Day4", "student"): (
        "STUDENT: 3SW Wk1 Day 4 - Transferable Skills"
    ),
    ("3SW-Wk3-Day5", "student"): "STUDENT: 3SW Wk3 Day 5 - Xello Interests",
    ("4SW-Wk1-Day3", "student"): (
        "STUDENT: 4SW Wk1 Day 3 - Xello Save Quick Sims"
    ),
    ("4SW-Wk2-Day3", "student"): (
        "STUDENT: 4SW Wk2 Day 3 - Postsecondary Route Trail and College Credit"
    ),
    ("4SW-Wk6-Day5", "student"): (
        "STUDENT: 4SW Wk6 Day 5 - Recovery: Private Mid-Year Reflection"
    ),
    ("5SW-Wk2-Day4", "student"): (
        "STUDENT: 5SW Wk2 Day 4 - Fixed-Data Test and Redesign"
    ),
    ("5SW-Wk5-Day3", "student"): (
        "STUDENT: 5SW Wk5 Day 3 - Compare the Same Offer Across Locations"
    ),
    ("6SW-Wk1-Day3", "student"): (
        "STUDENT: 6SW Wk1 Day 3 - Xello Discover Learning Pathways"
    ),
    ("6SW-Wk2-Day3", "student"): (
        "STUDENT: 6SW Wk2 Day 3 - Complete Xello Resume and Revise"
    ),
    ("6SW-Wk3-Day4", "student"): (
        "STUDENT: 6SW Wk3 Day 4 - Family Fun Pass"
    ),
    ("6SW-Wk4-Day3", "student"): (
        "STUDENT: 6SW Wk4 Day 3 - BrainBoost Decision and Career Outline"
    ),
    ("6SW-Wk5-Day1", "student"): (
        "STUDENT: 6SW Wk5 Day 1 - Job Search and Posting Screen"
    ),
    ("6SW-Wk5-Day3", "student"): (
        "STUDENT: 6SW Wk5 Day 3 - Sample Application and References"
    ),
    ("6SW-Wk5-Day4", "student"): (
        "STUDENT: 6SW Wk5 Day 4 - Interview Preparation"
    ),
    ("6SW-Wk6-Day1", "student"): (
        "STUDENT: 6SW Wk6 Day 1 - Evidence Audit and Recovery"
    ),
    ("6SW-Wk6-Day3", "student"): (
        "STUDENT: 6SW Wk6 Day 3 - Career Evidence Brief and Rehearsal"
    ),
    ("6SW-Wk6-Day4", "student"): (
        "STUDENT: 6SW Wk6 Day 4 - Communicated Capstone and Revision"
    ),
    ("6SW-Wk6-Day5", "student"): (
        "STUDENT: 6SW Wk6 Day 5 - Reflection and Transfer Forward"
    ),
}
assert len(DISCOVERY_TITLE_OVERRIDES) == 27
CCE_RESPONSE_ROUTE_COURSE_IDS = {98060, 97813, 97247, 97931, 98637}
PLAN_ROOT = (
    Path.home()
    / ".config"
    / "canvas-fleet-parity"
    / "cce"
    / "source-response-routes"
    / "plans"
)
BACKUP_ROOT = (
    Path.home()
    / ".config"
    / "canvas-fleet-parity"
    / "cce"
    / "source-response-routes"
    / "backups"
)


class RegistryError(ValueError):
    """The route registry does not satisfy the requested safety contract."""


class RouteReplacementError(ValueError):
    """The existing response-home HTML cannot be replaced unambiguously."""


@dataclass(frozen=True)
class ElementRange:
    tag: str
    start: int
    end: int
    open_end: int
    close_start: int
    open_tag: str


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


def stable_json(payload: Any) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def write_private_immutable(path: Path, payload: Any) -> None:
    """Create a private artifact without overwriting an existing plan."""

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


def canonical_page_slug(value: str) -> str:
    """Return a Canvas Page URL slug from a slug or an exact Canvas URL."""

    if not isinstance(value, str) or not value.strip():
        raise RegistryError("Canvas page url must be a non-empty string")
    value = value.strip()
    if "://" not in value:
        if "/" in value or value.startswith("."):
            raise RegistryError(f"Invalid Canvas page URL slug: {value!r}")
        return value
    parsed = urlparse(value)
    if parsed.scheme != "https" or parsed.netloc != urlparse(BASE).netloc:
        raise RegistryError(f"Canvas page URL is outside {BASE}: {value!r}")
    match = re.fullmatch(r"/courses/\d+/pages/([^/]+)", parsed.path.rstrip("/"))
    if not match:
        raise RegistryError(f"Canvas page URL is not a Page URL: {value!r}")
    return match.group(1)


def page_needle(day_key: str) -> str:
    match = PAGE_KEY_RE.fullmatch(day_key)
    if not match:
        raise RegistryError(f"Invalid day key: {day_key!r}")
    six_weeks, week, day = match.groups()
    return f"{six_weeks}SW Wk{week} Day {int(day)}"


def expected_day_keys() -> set[str]:
    """Return the exact 180-day CCE curriculum address set."""

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
    assert len(keys) == EXPECTED_ROUTE_COUNT
    return keys


def _required_string(mapping: dict, key: str, context: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RegistryError(f"{context}.{key} must be a non-empty string")
    return value.strip()


def _normalise_canvas_identity(identity: dict, context: str) -> dict:
    page_id = identity.get("page_id")
    if not isinstance(page_id, int) or isinstance(page_id, bool) or page_id <= 0:
        raise RegistryError(f"{context}.page_id must be a positive integer")
    slug = canonical_page_slug(_required_string(identity, "url", context))
    expected_hash = _required_string(identity, "expected_body_sha256", context)
    if not SHA256_RE.fullmatch(expected_hash):
        raise RegistryError(f"{context}.expected_body_sha256 is not SHA-256")
    published = identity.get("published_readback")
    if not isinstance(published, bool):
        raise RegistryError(f"{context}.published_readback must be boolean")
    return {
        "page_id": page_id,
        "url": slug,
        "expected_body_sha256": expected_hash,
        "published_readback": published,
    }


def load_registry(path: Path, *, for_apply: bool) -> dict:
    """Load a draft discovery registry or the reviewed apply registry."""

    path = path.expanduser().resolve()
    if not path.is_file():
        raise RegistryError(f"Registry does not exist: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RegistryError("Registry root must be an object")
    review_status = payload.get("review_status")
    if not isinstance(review_status, str):
        raise RegistryError("Registry review_status must be a string")
    if for_apply:
        if path != FINAL_REGISTRY.resolve() or ".draft" in path.name.lower():
            raise RegistryError(
                "Apply requires --registry build/google_docs/"
                f"{FINAL_REGISTRY.name}; draft or renamed registries are not accepted"
            )
        if review_status != REVIEWED_STATUS:
            raise RegistryError(
                f"Apply requires review_status={REVIEWED_STATUS!r}; "
                f"found {review_status!r}"
            )

    raw_routes = payload.get("routes")
    if raw_routes is None and not for_apply:
        raw_routes = payload.get("rows")
    if not isinstance(raw_routes, list):
        raise RegistryError("Registry routes must be an array")
    if len(raw_routes) != EXPECTED_ROUTE_COUNT:
        raise RegistryError(
            f"Expected {EXPECTED_ROUTE_COUNT} routes; found {len(raw_routes)}"
        )

    routes: list[dict] = []
    day_keys: set[str] = set()
    route_ids: set[str] = set()
    document_ids: set[str] = set()
    canvas_page_ids: set[int] = set()
    canvas_urls: set[str] = set()
    for index, raw in enumerate(raw_routes):
        context = f"routes[{index}]"
        if not isinstance(raw, dict):
            raise RegistryError(f"{context} must be an object")
        day_key = _required_string(raw, "day_key", context)
        if not PAGE_KEY_RE.fullmatch(day_key):
            raise RegistryError(f"{context}.day_key is invalid: {day_key!r}")
        route_id = raw.get("route_id") or day_key
        if not isinstance(route_id, str) or not route_id.strip():
            raise RegistryError(f"{context}.route_id must be a non-empty string")
        route_id = route_id.strip()
        if for_apply and "route_id" not in raw:
            raise RegistryError(f"{context}.route_id is required for apply")
        if day_key in day_keys:
            raise RegistryError(f"Duplicate day_key: {day_key}")
        if route_id in route_ids:
            raise RegistryError(f"Duplicate route_id: {route_id}")
        day_keys.add(day_key)
        route_ids.add(route_id)

        title = raw.get("title") or raw.get("display_title") or day_key
        if not isinstance(title, str) or not title.strip():
            raise RegistryError(f"{context}.title must be a non-empty string")
        title = title.strip()

        google_doc = raw.get("google_doc")
        normalised_doc: dict | None = None
        if isinstance(google_doc, dict):
            document_id = google_doc.get("document_id") or google_doc.get("id")
            if (
                google_doc.get("document_id")
                and google_doc.get("id")
                and google_doc["document_id"] != google_doc["id"]
            ):
                raise RegistryError(
                    f"{context}.google_doc id and document_id do not match"
                )
            copy_url = google_doc.get("copy_url")
            pdf_url = google_doc.get("pdf_export_url") or google_doc.get(
                "export_pdf_url"
            )
            folder_path = google_doc.get("folder_path")
            complete = all(
                isinstance(value, str) and value.strip()
                for value in (document_id, copy_url, pdf_url)
            )
            if complete:
                document_id = document_id.strip()
                copy_url = copy_url.strip()
                pdf_url = pdf_url.strip()
                if not DOC_ID_RE.fullmatch(document_id):
                    raise RegistryError(f"{context}.google_doc.document_id is invalid")
                expected_copy = (
                    f"https://docs.google.com/document/d/{document_id}/copy"
                )
                expected_pdf = (
                    f"https://docs.google.com/document/d/{document_id}/export?format=pdf"
                )
                if copy_url != expected_copy:
                    raise RegistryError(
                        f"{context}.google_doc.copy_url is not the same-Doc /copy URL"
                    )
                if pdf_url != expected_pdf:
                    raise RegistryError(
                        f"{context}.google_doc PDF URL is not the same-Doc PDF export"
                    )
                if for_apply and (
                    not isinstance(folder_path, str)
                    or not folder_path.startswith(CANONICAL_DRIVE_PREFIX)
                    or not folder_path.endswith("/Google Masters")
                ):
                    raise RegistryError(
                        f"{context}.google_doc.folder_path is outside canonical Google Masters"
                    )
                if document_id in document_ids:
                    raise RegistryError(f"Duplicate Google document_id: {document_id}")
                document_ids.add(document_id)
                normalised_doc = {
                    **google_doc,
                    "document_id": document_id,
                    "copy_url": copy_url,
                    "pdf_export_url": pdf_url,
                    "folder_path": folder_path,
                }
        if for_apply and normalised_doc is None:
            raise RegistryError(f"{context}.google_doc is incomplete")

        onenote = raw.get("onenote")
        if for_apply:
            if not isinstance(onenote, dict):
                raise RegistryError(f"{context}.onenote must be an object")
            if onenote.get("status") != "pending":
                raise RegistryError(
                    f"{context}.onenote.status must be 'pending' for the placeholder"
                )
            if onenote.get("url") is not None:
                raise RegistryError(
                    f"{context}.onenote.url must remain null while the button is a placeholder"
                )

        source = raw.get("source")
        if source is None and not for_apply:
            source = raw.get("source_evidence")
        if for_apply and (not isinstance(source, dict) or not source):
            raise RegistryError(f"{context}.source must be reviewed source evidence")

        source_course = None
        canvas = raw.get("canvas")
        if isinstance(canvas, dict):
            source_course = canvas.get("source_course")
        if source_course is None and not for_apply:
            source_course = raw.get("canvas_identity")
        normalised_canvas = None
        if isinstance(source_course, dict):
            course_id = source_course.get("course_id", DEFAULT_COURSE_ID)
            teacher = source_course.get("teacher")
            student = source_course.get("student")
            if isinstance(teacher, dict) and isinstance(student, dict):
                if not isinstance(course_id, int) or isinstance(course_id, bool):
                    raise RegistryError(
                        f"{context}.canvas.source_course.course_id is invalid"
                    )
                if course_id != DEFAULT_COURSE_ID:
                    raise RegistryError(
                        f"{context}.canvas.source_course.course_id must be "
                        f"{DEFAULT_COURSE_ID}"
                    )
                normalised_canvas = {
                    "course_id": course_id,
                    "teacher": _normalise_canvas_identity(
                        teacher, f"{context}.canvas.source_course.teacher"
                    ),
                    "student": _normalise_canvas_identity(
                        student, f"{context}.canvas.source_course.student"
                    ),
                }
                for role in ("teacher", "student"):
                    identity = normalised_canvas[role]
                    if identity["page_id"] in canvas_page_ids:
                        raise RegistryError(
                            f"Duplicate Canvas page_id: {identity['page_id']}"
                        )
                    if identity["url"] in canvas_urls:
                        raise RegistryError(f"Duplicate Canvas page url: {identity['url']}")
                    canvas_page_ids.add(identity["page_id"])
                    canvas_urls.add(identity["url"])
        if for_apply and normalised_canvas is None:
            raise RegistryError(
                f"{context}.canvas.source_course needs reviewed teacher and student identities"
            )

        routes.append(
            {
                "route_id": route_id,
                "day_key": day_key,
                "title": title,
                "google_doc": normalised_doc,
                "onenote": onenote,
                "source": source,
                "canvas": {"source_course": normalised_canvas}
                if normalised_canvas
                else None,
            }
        )

    required_day_keys = expected_day_keys()
    if day_keys != required_day_keys:
        missing = sorted(required_day_keys - day_keys)
        unexpected = sorted(day_keys - required_day_keys)
        raise RegistryError(
            "Registry does not contain the exact 180-day CCE address set; "
            f"missing={missing}, unexpected={unexpected}"
        )

    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "schema_version": payload.get("schema_version"),
        "review_status": review_status,
        "routes": routes,
    }


def link_block(route: dict, role: str) -> str:
    """Render the exact student or teacher response-home panel."""

    if role not in {"teacher", "student"}:
        raise ValueError(f"Unknown role: {role}")
    google_doc = route.get("google_doc")
    if not isinstance(google_doc, dict):
        raise RegistryError(f"{route['day_key']} has no complete Google Doc route")
    title = html.escape(route["title"], quote=False)
    copy_url = html.escape(google_doc["copy_url"], quote=True)
    pdf_url = html.escape(google_doc["pdf_export_url"], quote=True)
    if role == "teacher":
        return (
            f'<aside id="{BLOCK_ID}" '
            'style="margin:24px 0;padding:18px;border:1px solid #b8d9ae;'
            'border-left:6px solid #4a9d2f;border-radius:10px;background:#f4faf2">'
            '<p style="margin:0 0 5px;color:#356f23;font-size:13px"><strong>'
            'Choose one response home before class</strong></p><h2 '
            'style="margin:0 0 8px;color:#234b18">Student '
            'worksheet</h2><p style="margin:0 0 14px">Google Docs is the typing '
            'default. Students complete the work once in the option you choose.</p>'
            '<div style="display:flex;flex-wrap:wrap;gap:10px;margin:0 0 12px">'
            f'<a href="{copy_url}" target="_blank" style="display:inline-block;'
            'background:#1a73e8;color:#fff;padding:10px 14px;border-radius:6px;'
            'text-decoration:none"><strong>Make a Google Doc copy</strong></a>'
            '<span style="display:inline-block;background:#e5e7eb;'
            'color:#4b5563;padding:10px 14px;border:1px solid #c7cbd1;'
            'border-radius:6px"><strong>OneNote template — link coming soon</strong></span>'
            f'<a href="{pdf_url}" target="_blank" style="display:inline-block;'
            'background:#fff;color:#24323d;padding:10px 14px;border:1px solid #7c8790;'
            'border-radius:6px;text-decoration:none"><strong>Download printable '
            'PDF</strong></a></div><p style="margin:0;color:#4b5563;font-size:14px"><strong>'
            f'{title}</strong> · Give the class one option. Do not require students to '
            'copy the same response into another platform.</p></aside>'
        )
    return (
        f'<aside id="{BLOCK_ID}" '
        'style="margin:24px 0;padding:18px;border:2px solid #4a9d2f;'
        'border-radius:10px;background:#f2f8ef"><p style="margin:0 0 5px;'
        'color:#356f23;font-size:13px"><strong>Response Home</strong></p><h2 '
        'style="margin:0 0 8px;'
        'color:#234b18">Type today’s work in Google Docs</h2><p style="margin:0 0 14px">'
        f'<a href="{copy_url}" target="_blank" style="display:inline-block;'
        'background:#1a73e8;color:#fff;padding:11px 16px;border-radius:6px;'
        'text-decoration:none"><strong>Make your copy: '
        f'{title}</strong></a></p><p style="margin:0">Type in your copy and submit or share it '
        'the way your teacher directs. Complete this work in one place only.</p></aside>'
    )


_CONTAINER_TAG_RE = re.compile(
    r"<\s*(?P<close>/?)\s*(?P<tag>div|aside|section|p)\b[^>]*>", re.I
)
_ANY_TAG_RE = re.compile(r"<[^>]+>")
_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
_ID_RE_TEMPLATE = r"\bid\s*=\s*([\"']){id}\1"


def _element_ranges(body: str) -> list[ElementRange]:
    stack: list[tuple[str, int, int, str]] = []
    ranges: list[ElementRange] = []
    for match in _CONTAINER_TAG_RE.finditer(body):
        tag = match.group("tag").lower()
        if not match.group("close"):
            stack.append((tag, match.start(), match.end(), match.group(0)))
            continue
        open_index = None
        for index in range(len(stack) - 1, -1, -1):
            if stack[index][0] == tag:
                open_index = index
                break
        if open_index is None:
            continue
        open_tag, start, open_end, raw_open = stack[open_index]
        del stack[open_index:]
        ranges.append(
            ElementRange(
                tag=open_tag,
                start=start,
                end=match.end(),
                open_end=open_end,
                close_start=match.start(),
                open_tag=raw_open,
            )
        )
    return ranges


def _visible_text(fragment: str) -> str:
    fragment = _COMMENT_RE.sub(" ", fragment)
    fragment = _ANY_TAG_RE.sub(" ", fragment)
    return " ".join(html.unescape(fragment).split())


def _dedupe_overlapping(ranges: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    ordered = sorted(set(ranges), key=lambda item: (item[0], -(item[1] - item[0])))
    result: list[tuple[int, int]] = []
    for candidate in ordered:
        if any(
            candidate[0] >= current[0] and candidate[1] <= current[1]
            for current in result
        ):
            continue
        result.append(candidate)
    return result


def _overlaps(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] < right[1] and right[0] < left[1]


def _resolve_midyear_profile_response_homes(
    body: str,
    response_ranges: list[tuple[int, int]],
) -> tuple[tuple[int, int], tuple[int, int], str] | None:
    """Resolve the one reviewed page with a compact and detailed route label.

    4SW-Wk1-Day1 has a short summary card and a later linked instruction that
    both begin with Response Home. Only the detailed linked paragraph is the
    route container. The summary remains useful page context, so its label is
    changed to ``Today’s work:``. Every string and link-shape check below must
    match; all other multi-container pages remain a hard stop.
    """

    if len(response_ranges) != 2:
        return None
    compact_text = (
        "Response Home: complete a Mid-Year Profile Audit with an earlier result, "
        "three current facts, and a supported conclusion."
    )
    detailed_text = (
        "Response home: use the front-and-back Mid-Year Profile Audit your teacher "
        "gives you. Write your name on it. Your teacher will collect it today and "
        "return it for the Day 5 Blueprint. Open the same audit only if you need a "
        "replacement or absence copy. H&L, Xello, and earlier portfolio work are "
        "optional evidence sources; a private screenshot is not required."
    )
    compact_matches: list[tuple[int, int]] = []
    detailed_matches: list[tuple[int, int]] = []
    for candidate in response_ranges:
        fragment = body[candidate[0] : candidate[1]]
        visible = _visible_text(fragment)
        if visible == compact_text and not re.search(r"<a\b", fragment, re.I):
            compact_matches.append(candidate)
        if (
            visible == detailed_text
            and len(re.findall(r"<a\b", fragment, re.I)) == 1
            and re.search(
                r"/courses/(?:98060|97813|97247|97931|98637)/files/",
                fragment,
            )
            and re.search(r">\s*Open the same audit\s*</a>", fragment, re.I)
        ):
            detailed_matches.append(candidate)
    if len(compact_matches) != 1 or len(detailed_matches) != 1:
        return None
    compact = compact_matches[0]
    compact_fragment = body[compact[0] : compact[1]]
    relabeled, replacements = re.subn(
        r"(<strong\b[^>]*>)Response Home:(</strong>)",
        r"\1Today’s work:\2",
        compact_fragment,
        count=1,
        flags=re.I,
    )
    if replacements != 1:
        return None
    return detailed_matches[0], compact, relabeled


def replace_response_home(body: str, block: str) -> tuple[str, dict]:
    """Replace route HTML by byte range, preserving every non-route byte."""

    body = body or ""
    elements = _element_ranges(body)
    id_re = re.compile(_ID_RE_TEMPLATE.format(id=re.escape(BLOCK_ID)), re.I)
    own_ranges = [
        (element.start, element.end)
        for element in elements
        if id_re.search(element.open_tag)
    ]
    comment_ranges = [
        (match.start(), match.end())
        for match in re.finditer(re.escape(START) + r".*?" + re.escape(END), body, re.S)
    ]
    legacy_pattern = re.compile(
        r"<aside\b[^>]*>(?:(?!</aside>).)*?"
        r"<h2\b[^>]*>\s*(?:Student Google Doc|Typeable Google Doc)\s*</h2>"
        r"(?:(?!</aside>).)*?"
        r"https://docs\.google\.com/document/d/[A-Za-z0-9_-]+/copy"
        r"(?:(?!</aside>).)*?</aside>",
        re.I | re.S,
    )
    legacy_ranges = [(match.start(), match.end()) for match in legacy_pattern.finditer(body)]
    route_ranges = _dedupe_overlapping(own_ranges + comment_ranges + legacy_ranges)
    if len(route_ranges) > 1:
        raise RouteReplacementError(
            f"Found {len(route_ranges)} separate existing route blocks"
        )

    response_ranges: list[tuple[int, int]] = []
    response_label = re.compile(
        r"^(?:Today(?:'|’)s\s+)?Response Home(?:\s*:)?(?:\s|$)", re.I
    )
    for element in elements:
        candidate = (element.start, element.end)
        if any(_overlaps(candidate, route_range) for route_range in route_ranges):
            continue
        visible = _visible_text(body[element.open_end : element.close_start])
        if len(visible) <= 1200 and response_label.search(visible):
            response_ranges.append(candidate)
    # Prefer the smallest matching element when a simple Response Home is
    # wrapped in a larger layout container. Disjoint matches remain ambiguous.
    response_ranges = [
        candidate
        for candidate in sorted(set(response_ranges))
        if not any(
            other != candidate
            and other[0] >= candidate[0]
            and other[1] <= candidate[1]
            for other in response_ranges
        )
    ]
    special_summary_edit: tuple[int, int, str] | None = None
    special_resolution = _resolve_midyear_profile_response_homes(
        body, response_ranges
    )
    if len(response_ranges) > 1:
        if special_resolution is None:
            raise RouteReplacementError(
                f"Found {len(response_ranges)} plausible Response Home containers"
            )
        detailed, compact, relabeled = special_resolution
        response_ranges = [detailed]
        special_summary_edit = (compact[0], compact[1], relabeled)

    edits: list[tuple[int, int, str]] = (
        [special_summary_edit] if special_summary_edit else []
    )
    if response_ranges:
        target = response_ranges[0]
        edits.append((target[0], target[1], block))
        for route_range in route_ranges:
            if not _overlaps(route_range, target):
                edits.append((route_range[0], route_range[1], ""))
        method = (
            "replace_detailed_response_home_and_relabel_summary"
            if special_summary_edit
            else "replace_response_home"
        )
    elif route_ranges:
        target = route_ranges[0]
        edits.append((target[0], target[1], block))
        method = "replace_existing_route_block"
    else:
        separator = "" if not body or body.endswith("\n") else "\n"
        edits.append((len(body), len(body), f"{separator}{block}"))
        method = "append_no_existing_route_container"

    transformed = body
    for start, end, replacement in sorted(edits, reverse=True):
        transformed = transformed[:start] + replacement + transformed[end:]
    return transformed, {
        "method": method,
        "removed_route_block_count": len(route_ranges),
        "replaced_response_home_count": len(response_ranges),
        "relabeled_response_summary_count": int(special_summary_edit is not None),
    }


def body_only_payload(body: str) -> dict[str, str]:
    """The only payload shape that this script may send to Canvas."""

    return {"wiki_page[body]": body}


async def paged(client: httpx.AsyncClient, path: str) -> list[dict]:
    rows: list[dict] = []
    url: str | None = f"{BASE}/api/v1{path}"
    params: dict | None = {"per_page": 100}
    while url:
        response = await client.get(url, params=params)
        response.raise_for_status()
        rows.extend(response.json())
        url = response.links.get("next", {}).get("url")
        params = None
    return rows


def _headers_from_stdin() -> dict[str, str]:
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    return {"Authorization": f"Bearer {token}"}


def _discover_page(pages: list[dict], day_key: str, role: str) -> dict:
    exact_title = DISCOVERY_TITLE_OVERRIDES.get((day_key, role))
    if exact_title is not None:
        matches = [page for page in pages if page.get("title") == exact_title]
        if len(matches) != 1:
            raise RuntimeError(
                f"Expected one exact-title {role} page for {day_key}: "
                f"{exact_title!r}; found {[page.get('title') for page in matches]}"
            )
        return matches[0]
    needle = page_needle(day_key).lower()
    matches = [
        page
        for page in pages
        if (page.get("title") or "").lower().startswith(f"{role}:")
        and needle in (page.get("title") or "").lower()
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one {role} page for {day_key}; "
            f"found {[page.get('title') for page in matches]}"
        )
    return matches[0]


async def _get_page(client: httpx.AsyncClient, course_id: int, slug: str) -> dict:
    response = await client.get(f"{BASE}/api/v1/courses/{course_id}/pages/{slug}")
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError(f"Canvas returned a non-object Page for {slug}")
    return payload


def _default_plan_path(course_id: int) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    return PLAN_ROOT / f"course-{course_id}-response-routes-{timestamp}.json"


async def prepare_plan(args: argparse.Namespace, registry: dict) -> dict:
    """Perform read-only discovery and write an immutable, non-applied plan."""

    headers = _headers_from_stdin()
    async with httpx.AsyncClient(
        headers=headers,
        timeout=60,
        follow_redirects=True,
        limits=httpx.Limits(max_connections=12, max_keepalive_connections=12),
    ) as client:
        needs_discovery = any(route["canvas"] is None for route in registry["routes"])
        pages = (
            await paged(client, f"/courses/{args.course_id}/pages")
            if needs_discovery
            else []
        )
        targets: list[dict] = []
        issues: list[dict] = []
        for route in registry["routes"]:
            for role in ("teacher", "student"):
                identity = None
                if route["canvas"]:
                    source_course = route["canvas"]["source_course"]
                    if source_course["course_id"] != args.course_id:
                        issues.append(
                            {
                                "route_id": route["route_id"],
                                "role": role,
                                "code": "registry_course_id_mismatch",
                                "expected": args.course_id,
                                "actual": source_course["course_id"],
                            }
                        )
                    identity = source_course[role]
                    summary = {"url": identity["url"], "page_id": identity["page_id"]}
                else:
                    try:
                        summary = _discover_page(pages, route["day_key"], role)
                    except RuntimeError as exc:
                        issues.append(
                            {
                                "route_id": route["route_id"],
                                "role": role,
                                "code": "canvas_page_discovery_failed",
                                "message": str(exc),
                            }
                        )
                        continue
                try:
                    current = await _get_page(
                        client, args.course_id, canonical_page_slug(summary["url"])
                    )
                except (httpx.HTTPError, RegistryError) as exc:
                    issues.append(
                        {
                            "route_id": route["route_id"],
                            "role": role,
                            "code": "canvas_page_read_failed",
                            "message": str(exc),
                        }
                    )
                    continue
                observed_body = current.get("body") or ""
                observed_hash = sha256_text(observed_body)
                target_issues: list[str] = []
                if identity:
                    if current.get("page_id") != identity["page_id"]:
                        target_issues.append("page_id_mismatch")
                    if current.get("url") != identity["url"]:
                        target_issues.append("page_url_mismatch")
                    if observed_hash != identity["expected_body_sha256"]:
                        target_issues.append("expected_body_sha256_mismatch")
                    if current.get("published") is not identity["published_readback"]:
                        target_issues.append("published_readback_mismatch")
                if route["google_doc"] is None:
                    target_issues.append("google_doc_route_incomplete")
                    after_body = None
                    transformation = None
                else:
                    try:
                        after_body, transformation = replace_response_home(
                            observed_body, link_block(route, role)
                        )
                    except RouteReplacementError as exc:
                        target_issues.append("response_home_replacement_ambiguous")
                        issues.append(
                            {
                                "route_id": route["route_id"],
                                "role": role,
                                "code": "response_home_replacement_ambiguous",
                                "message": str(exc),
                            }
                        )
                        after_body = None
                        transformation = None
                for code in target_issues:
                    if code != "response_home_replacement_ambiguous":
                        issues.append(
                            {
                                "route_id": route["route_id"],
                                "role": role,
                                "code": code,
                            }
                        )
                targets.append(
                    {
                        "route_id": route["route_id"],
                        "day_key": route["day_key"],
                        "role": role,
                        "page_id": current.get("page_id"),
                        "page_url": current.get("url"),
                        "title": current.get("title"),
                        "endpoint": (
                            f"/api/v1/courses/{args.course_id}/pages/{current.get('url')}"
                        ),
                        "registry_expected_before_body_sha256": identity.get(
                            "expected_body_sha256"
                        )
                        if identity
                        else None,
                        "observed_before_body_sha256": observed_hash,
                        "expected_published_readback": identity.get(
                            "published_readback"
                        )
                        if identity
                        else None,
                        "observed_published": current.get("published"),
                        "before_body": observed_body,
                        "after_body": after_body,
                        "after_body_sha256": sha256_text(after_body)
                        if isinstance(after_body, str)
                        else None,
                        "transformation": transformation,
                        "would_change": after_body != observed_body
                        if isinstance(after_body, str)
                        else None,
                        "issues": target_issues,
                    }
                )

    issue_free = not issues and len(targets) == EXPECTED_PAGE_COUNT
    plan = {
        "schema_version": 2,
        "artifact": "CCE source-course response-route immutable plan",
        "created_at": utc_now(),
        "mode": "prepare_read_only",
        "authorization": "not_applied",
        "status": (
            "ready_for_explicit_apply"
            if issue_free and registry["review_status"] == REVIEWED_STATUS
            else "blocked_or_draft"
        ),
        "course_id": args.course_id,
        "registry": {
            "path": registry["path"],
            "sha256": registry["sha256"],
            "review_status": registry["review_status"],
            "route_count": len(registry["routes"]),
        },
        "safety_contract": {
            "mutation_endpoint": "Canvas Pages update",
            "allowed_put_fields": ["wiki_page[body]"],
            "publication_fields_sent": [],
            "preflight": "sequential exact Page ID, URL, body SHA-256, publication readback",
            "readback": "exact body plus publication readback after every PUT",
        },
        "summary": {
            "route_count": len(registry["routes"]),
            "target_count": len(targets),
            "would_change_count": sum(
                target.get("would_change") is True for target in targets
            ),
            "issue_count": len(issues),
        },
        "issues": issues,
        "targets": targets,
    }
    output = (
        args.plan_output.expanduser().resolve()
        if args.plan_output
        else _default_plan_path(args.course_id)
    )
    write_private_immutable(output, plan)
    return {
        "status": "prepared_read_only",
        "course_id": args.course_id,
        "registry_review_status": registry["review_status"],
        "route_count": len(registry["routes"]),
        "target_count": len(targets),
        "would_change_count": plan["summary"]["would_change_count"],
        "issue_count": len(issues),
        "plan_file": str(output),
        "plan_sha256": sha256_file(output),
        "canvas_writes": 0,
    }


def _load_and_validate_plan(
    path: Path,
    expected_sha256: str,
    registry: dict,
    course_id: int,
) -> dict:
    path = path.expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"Plan does not exist: {path}")
    if stat_mode := (path.stat().st_mode & 0o777):
        if stat_mode & 0o222:
            raise ValueError(
                f"Plan must be immutable (no write bits); found mode {stat_mode:04o}"
            )
    if not SHA256_RE.fullmatch(expected_sha256):
        raise ValueError("--expected-plan-sha256 must be a lowercase SHA-256")
    actual_sha256 = sha256_file(path)
    if actual_sha256 != expected_sha256:
        raise ValueError(
            f"Plan SHA-256 mismatch: expected {expected_sha256}, found {actual_sha256}"
        )
    plan = json.loads(path.read_text(encoding="utf-8"))
    if plan.get("status") != "ready_for_explicit_apply":
        raise ValueError(f"Plan is not apply-ready: {plan.get('status')!r}")
    if plan.get("authorization") != "not_applied":
        raise ValueError("Plan authorization marker is invalid")
    if plan.get("course_id") != course_id:
        raise ValueError("Plan course_id does not match --course-id")
    plan_registry = plan.get("registry") or {}
    if plan_registry.get("sha256") != registry["sha256"]:
        raise ValueError("Reviewed registry bytes changed after the plan was prepared")
    if plan_registry.get("review_status") != REVIEWED_STATUS:
        raise ValueError("Plan was not prepared from a reviewed registry")
    if plan.get("issues"):
        raise ValueError("Plan contains unresolved issues")
    targets = plan.get("targets")
    if not isinstance(targets, list) or len(targets) != EXPECTED_PAGE_COUNT:
        raise ValueError(f"Plan must contain exactly {EXPECTED_PAGE_COUNT} targets")

    route_by_id = {route["route_id"]: route for route in registry["routes"]}
    seen: set[tuple[str, str]] = set()
    for target in targets:
        if not isinstance(target, dict):
            raise ValueError("Every plan target must be an object")
        key = (target.get("route_id"), target.get("role"))
        if (
            key in seen
            or key[0] not in route_by_id
            or key[1] not in {"teacher", "student"}
        ):
            raise ValueError(f"Invalid or duplicate plan target: {key}")
        seen.add(key)
        route = route_by_id[key[0]]
        identity = route["canvas"]["source_course"][key[1]]
        if target.get("page_id") != identity["page_id"]:
            raise ValueError(f"Plan Page ID differs from reviewed registry for {key}")
        if target.get("page_url") != identity["url"]:
            raise ValueError(f"Plan Page URL differs from reviewed registry for {key}")
        expected_endpoint = f"/api/v1/courses/{course_id}/pages/{identity['url']}"
        if target.get("endpoint") != expected_endpoint:
            raise ValueError(f"Plan endpoint differs from reviewed registry for {key}")
        if target.get("day_key") != route["day_key"]:
            raise ValueError(f"Plan day key differs from reviewed registry for {key}")
        if (
            target.get("registry_expected_before_body_sha256")
            != identity["expected_body_sha256"]
        ):
            raise ValueError(f"Plan before hash differs from reviewed registry for {key}")
        before = target.get("before_body")
        after = target.get("after_body")
        if not isinstance(before, str) or not isinstance(after, str):
            raise ValueError(f"Plan body is missing for {key}")
        if sha256_text(before) != identity["expected_body_sha256"]:
            raise ValueError(f"Plan before body hash is invalid for {key}")
        if target.get("observed_before_body_sha256") != sha256_text(before):
            raise ValueError(f"Plan observed before hash is invalid for {key}")
        rebuilt, transformation = replace_response_home(
            before, link_block(route, key[1])
        )
        if after != rebuilt or target.get("after_body_sha256") != sha256_text(rebuilt):
            raise ValueError(f"Plan after body is not reproducible for {key}")
        if target.get("transformation") != transformation:
            raise ValueError(f"Plan transformation metadata differs for {key}")
        if target.get("would_change") is not (before != rebuilt):
            raise ValueError(f"Plan change marker is invalid for {key}")
        if target.get("issues"):
            raise ValueError(f"Plan target contains unresolved issues for {key}")
        if (
            target.get("expected_published_readback")
            is not identity["published_readback"]
        ):
            raise ValueError(f"Plan publication readback differs for {key}")
    if len(seen) != EXPECTED_PAGE_COUNT:
        raise ValueError("Plan does not cover every reviewed route and role")
    return plan


def _verify_current_page(current: dict, target: dict, *, phase: str) -> None:
    failures: list[str] = []
    if current.get("page_id") != target["page_id"]:
        failures.append(f"page_id {current.get('page_id')} != {target['page_id']}")
    if current.get("url") != target["page_url"]:
        failures.append(f"url {current.get('url')!r} != {target['page_url']!r}")
    body_hash = sha256_text(current.get("body") or "")
    if body_hash != target["registry_expected_before_body_sha256"]:
        failures.append(
            f"body_sha256 {body_hash} != "
            f"{target['registry_expected_before_body_sha256']}"
        )
    if current.get("published") is not target["expected_published_readback"]:
        failures.append(
            f"published {current.get('published')!r} != "
            f"{target['expected_published_readback']!r}"
        )
    if failures:
        raise RuntimeError(
            f"{phase} mismatch for {target['route_id']} {target['role']}: "
            + "; ".join(failures)
        )


def _write_backup(course_id: int, plan_sha256: str, preflight: list[dict]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    path = BACKUP_ROOT / f"course-{course_id}-response-routes-{timestamp}.json"
    payload = {
        "schema_version": 2,
        "artifact": "CCE pre-apply source response-route backup",
        "created_at": utc_now(),
        "course_id": course_id,
        "plan_sha256": plan_sha256,
        "pages": [
            {
                "route_id": item["target"]["route_id"],
                "role": item["target"]["role"],
                "page_id": item["page"].get("page_id"),
                "page_url": item["page"].get("url"),
                "title": item["page"].get("title"),
                "published": item["page"].get("published"),
                "front_page": item["page"].get("front_page"),
                "body_sha256": sha256_text(item["page"].get("body") or ""),
                "body": item["page"].get("body") or "",
            }
            for item in preflight
        ],
    }
    write_private_immutable(path, payload)
    return path


async def apply_plan(args: argparse.Namespace, registry: dict, plan: dict) -> dict:
    """Sequentially preflight, back up, body-only update, and read back."""

    headers = _headers_from_stdin()
    plan_sha256 = args.expected_plan_sha256
    async with httpx.AsyncClient(
        headers=headers,
        timeout=60,
        follow_redirects=True,
        limits=httpx.Limits(max_connections=1, max_keepalive_connections=1),
    ) as client:
        preflight: list[dict] = []
        for target in plan["targets"]:
            current = await _get_page(client, args.course_id, target["page_url"])
            _verify_current_page(current, target, phase="preflight")
            preflight.append({"target": target, "page": current})

        changed = [item for item in preflight if item["target"]["would_change"]]
        backup = (
            _write_backup(args.course_id, plan_sha256, preflight) if changed else None
        )

        applied: list[dict] = []
        for item in changed:
            target = item["target"]
            current = await _get_page(client, args.course_id, target["page_url"])
            _verify_current_page(current, target, phase="immediate pre-PUT")
            response = await client.put(
                f"{BASE}{target['endpoint']}",
                data=body_only_payload(target["after_body"]),
            )
            response.raise_for_status()
            readback = await _get_page(client, args.course_id, target["page_url"])
            if readback.get("body") != target["after_body"]:
                raise RuntimeError(
                    f"Exact body readback failed for {target['route_id']} {target['role']}"
                )
            if readback.get("published") is not target["expected_published_readback"]:
                raise RuntimeError(
                    f"Publication readback changed for {target['route_id']} {target['role']}"
                )
            if (
                readback.get("page_id") != target["page_id"]
                or readback.get("url") != target["page_url"]
            ):
                raise RuntimeError(
                    f"Canvas Page identity changed for {target['route_id']} {target['role']}"
                )
            applied.append(
                {
                    "route_id": target["route_id"],
                    "role": target["role"],
                    "page_id": target["page_id"],
                    "page_url": target["page_url"],
                    "after_body_sha256": target["after_body_sha256"],
                    "published_readback": readback.get("published"),
                }
            )

        for target in plan["targets"]:
            final = await _get_page(client, args.course_id, target["page_url"])
            if final.get("body") != target["after_body"]:
                raise RuntimeError(
                    f"Final exact body readback failed for {target['route_id']} {target['role']}"
                )
            if final.get("published") is not target["expected_published_readback"]:
                raise RuntimeError(
                    f"Final publication readback changed for {target['route_id']} {target['role']}"
                )

    return {
        "status": "applied_and_exactly_verified",
        "course_id": args.course_id,
        "route_count": len(registry["routes"]),
        "target_count": len(plan["targets"]),
        "page_body_put_count": len(applied),
        "publication_fields_sent": 0,
        "backup_file": str(backup) if backup else None,
        "plan_file": str(args.plan.expanduser().resolve()),
        "plan_sha256": plan_sha256,
        "applied": applied,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registry",
        type=Path,
        required=True,
        help=(
            "180-route registry. Prepare may inspect the canonical draft; apply "
            f"requires {FINAL_REGISTRY.relative_to(ROOT)}."
        ),
    )
    parser.add_argument("--course-id", type=int, default=DEFAULT_COURSE_ID)
    parser.add_argument(
        "--plan-output",
        type=Path,
        help="New immutable prepare-plan path; defaults to the private safety directory",
    )
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--expected-plan-sha256")
    args = parser.parse_args(argv)
    if args.course_id != DEFAULT_COURSE_ID:
        parser.error(
            f"This source-baseline tool is pinned to CCE course {DEFAULT_COURSE_ID}"
        )
    if args.apply:
        if args.plan_output:
            parser.error("--plan-output cannot be combined with --apply")
        if not args.plan or not args.expected_plan_sha256:
            parser.error("--apply requires --plan and --expected-plan-sha256")
    elif args.plan or args.expected_plan_sha256:
        parser.error("--plan and --expected-plan-sha256 require --apply")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    registry = load_registry(args.registry, for_apply=args.apply)
    if args.apply:
        plan = _load_and_validate_plan(
            args.plan,
            args.expected_plan_sha256,
            registry,
            args.course_id,
        )
        result = asyncio.run(apply_plan(args, registry, plan))
    else:
        result = asyncio.run(prepare_plan(args, registry))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
