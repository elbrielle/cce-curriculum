#!/usr/bin/env python3
"""Audit or repair Canvas files used by CCE course content.

CCE modules remain under the teacher's publication control.  Files referenced by
course pages or module content, including images and linked PDFs, must be
available to enrolled students whenever a teacher publishes the containing
module.  Canvas evaluates both the file record and every ancestor folder, so the
repair opens the referenced file and its complete folder chain.

The default is read-only and an apply run requires ``--apply``.  This program
never publishes or unpublishes a module, module item, page, assignment,
discussion, or quiz.  It snapshots those states before the file/folder writes
and verifies that they are unchanged afterward.

Examples:

    uv run --with httpx python cce_student_resource_access_fix.py --discover
    uv run --with httpx python cce_student_resource_access_fix.py \
        --check --course-id 98060
    uv run --with httpx python cce_student_resource_access_fix.py \
        --apply --course-id 98060

The token is read from a hidden prompt or one line of stdin.  It is never saved
or printed.
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

try:
    import httpx
except ImportError:  # pragma: no cover - exercised only outside the project runtime
    sys.exit(
        "This tool needs httpx. Run it with "
        "`uv run --with httpx python cce_student_resource_access_fix.py ...`."
    )


BASE = "https://learn.irvingisd.net"
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
FILE_REFERENCE_RE = re.compile(
    r"(?:/api/v1)?/(?:courses/\d+/)?files/(\d+)"
    r"(?=$|[/?#&\s\"'<>,])",
    re.IGNORECASE,
)
FOLDER_PREVIEW_RE = re.compile(
    r"/(?:courses/\d+/)?files/(?:folder/[^?\"'<>\s]*)?"
    r"[^\"'<>\s]*?[?&](?:amp;)?preview=(\d+)",
    re.IGNORECASE,
)
CCE_COURSE_RE = re.compile(
    r"(?:\bCCE\b|\bCC\s+EXPL(?:OR(?:ATIONS?)?)?\b|"
    r"CAREER\s+(?:AND|&)\s+COLLEGE\s+EXPL)",
    re.IGNORECASE,
)


class AttributeValueParser(HTMLParser):
    """Collect every HTML attribute value that may contain a Canvas file URL."""

    def __init__(self) -> None:
        super().__init__()
        self.values: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        del tag
        self.values.extend(value for _, value in attrs if value)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)


def file_ids_in_text(value: str) -> set[int]:
    """Return file IDs from links, images, embeds, and Canvas preview URLs."""

    if not value:
        return set()
    ids = {int(match) for match in FILE_REFERENCE_RE.findall(value)}
    ids.update(int(match) for match in FOLDER_PREVIEW_RE.findall(value))
    return ids


def file_ids_in_html(body: str) -> set[int]:
    """Parse valid HTML attributes and retain a raw fallback for malformed HTML."""

    parser = AttributeValueParser()
    parser.feed(body or "")
    ids = file_ids_in_text(body or "")
    for value in parser.values:
        ids.update(file_ids_in_text(value))
    return ids


def strings_in(value: Any) -> Iterable[str]:
    """Yield strings recursively from Canvas quiz/interaction JSON."""

    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from strings_in(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings_in(child)


def restriction_reasons(record: dict, *, folder: bool = False) -> list[str]:
    """Describe settings that can keep an enrolled student from a resource."""

    reasons: list[str] = []
    if record.get("locked"):
        reasons.append("locked")
    if record.get("hidden"):
        reasons.append("hidden")
    if record.get("lock_at"):
        reasons.append("lock_at")
    if record.get("unlock_at"):
        reasons.append("unlock_at")
    return reasons


def open_payload(*, folder: bool = False) -> dict[str, str]:
    """Clear every independent file/folder availability control."""

    payload = {
        "locked": "false",
        "hidden": "false",
        "lock_at": "",
        "unlock_at": "",
    }
    # Preserve ``visibility_level`` exactly. Canvas documents ``inherit`` as the
    # default, and changing it is unrelated to clearing a file/folder lock.
    return payload


async def request(
    client: httpx.AsyncClient, method: str, path: str, **kwargs: Any
) -> httpx.Response:
    url = path if path.startswith("http") else f"{BASE}/api/v1{path}"
    for attempt in range(1, 4):
        try:
            response = await client.request(method, url, **kwargs)
        except TRANSIENT_EXCEPTIONS as exc:
            if attempt == 3:
                raise RuntimeError(
                    f"{method} {urlparse(url).path} failed after 3 attempts: "
                    f"{type(exc).__name__}"
                ) from exc
            await asyncio.sleep(0.25 * attempt)
            continue
        if response.status_code in TRANSIENT_STATUSES:
            if attempt == 3:
                raise RuntimeError(
                    f"{method} {urlparse(url).path} failed after 3 attempts: "
                    f"HTTP {response.status_code}"
                )
            await asyncio.sleep(0.25 * attempt)
            continue
        if response.status_code >= 400:
            raise RuntimeError(
                f"Canvas {method} {urlparse(url).path} returned "
                f"{response.status_code}: {response.text[:240]}"
            )
        return response
    raise AssertionError("unreachable")


async def api(
    client: httpx.AsyncClient, method: str, path: str, **kwargs: Any
) -> Any:
    response = await request(client, method, path, **kwargs)
    return response.json() if response.content else None


async def paged(
    client: httpx.AsyncClient, path: str, params: dict[str, Any] | None = None
) -> list[dict]:
    records: list[dict] = []
    url: str | None = f"{BASE}/api/v1{path}"
    query: dict[str, Any] | None = {"per_page": 100, **(params or {})}
    while url:
        response = await request(client, "GET", url, params=query)
        payload = response.json()
        if not isinstance(payload, list):
            raise RuntimeError(
                f"Canvas GET {urlparse(url).path} returned a non-list page"
            )
        records.extend(payload)
        url = response.links.get("next", {}).get("url")
        query = None
    return records


async def gather_limited(
    functions: Iterable[tuple[Any, tuple[Any, ...]]], limit: int = 12
) -> list[Any]:
    semaphore = asyncio.Semaphore(limit)

    async def run(function: Any, arguments: tuple[Any, ...]) -> Any:
        async with semaphore:
            return await function(*arguments)

    return list(
        await asyncio.gather(
            *(run(function, arguments) for function, arguments in functions)
        )
    )


async def publication_snapshot(
    client: httpx.AsyncClient, course_id: int
) -> dict[str, Any]:
    """Capture every publication switch this tool promises not to change."""

    course, modules, pages, assignments, discussions, quizzes = await asyncio.gather(
        api(client, "GET", f"/courses/{course_id}"),
        paged(client, f"/courses/{course_id}/modules"),
        paged(client, f"/courses/{course_id}/pages"),
        paged(client, f"/courses/{course_id}/assignments"),
        paged(client, f"/courses/{course_id}/discussion_topics"),
        paged(client, f"/courses/{course_id}/quizzes"),
    )
    module_item_batches = await gather_limited(
        (
            (
                paged,
                (client, f"/courses/{course_id}/modules/{module['id']}/items"),
            )
            for module in modules
        )
    )
    return {
        "course": {
            "workflow_state": course.get("workflow_state"),
            "default_view": course.get("default_view"),
        },
        "modules": {
            str(module["id"]): bool(module.get("published")) for module in modules
        },
        "module_items": {
            f"{module['id']}:{item['id']}": bool(item.get("published"))
            for module, items in zip(modules, module_item_batches)
            for item in items
        },
        "pages": {
            str(page["url"]): {
                "published": bool(page.get("published")),
                "front_page": bool(page.get("front_page")),
            }
            for page in pages
        },
        "assignments": {
            str(record["id"]): bool(record.get("published"))
            for record in assignments
        },
        "discussions": {
            str(record["id"]): bool(record.get("published"))
            for record in discussions
        },
        "quizzes": {
            str(record["id"]): bool(record.get("published")) for record in quizzes
        },
    }


@dataclass
class PreparedCourse:
    course_id: int
    course_name: str
    references: dict[int, set[str]]
    file_records: dict[int, dict]
    folder_records: dict[int, dict]
    unresolved_file_ids: list[int]
    foreign_file_ids: list[int]
    surface_counts: dict[str, int]
    publication_before: dict[str, Any]

    @property
    def restricted_files(self) -> dict[int, list[str]]:
        return {
            file_id: restriction_reasons(record)
            for file_id, record in self.file_records.items()
            if restriction_reasons(record)
        }

    @property
    def restricted_folders(self) -> dict[int, list[str]]:
        return {
            folder_id: restriction_reasons(record, folder=True)
            for folder_id, record in self.folder_records.items()
            if restriction_reasons(record, folder=True)
        }


def add_reference(
    references: dict[int, set[str]], payload: Any, surface: str
) -> None:
    for value in strings_in(payload):
        for file_id in file_ids_in_html(value):
            references[file_id].add(surface)


def add_assignment_references(
    references: dict[int, set[str]], assignment: dict[str, Any]
) -> None:
    """Collect linked files plus Canvas's direct student-annotation attachment."""

    label = f"Assignment: {assignment.get('name') or assignment.get('id')}"
    add_reference(references, assignment, label)
    annotatable_attachment_id = assignment.get("annotatable_attachment_id")
    if (
        isinstance(annotatable_attachment_id, int)
        and not isinstance(annotatable_attachment_id, bool)
    ):
        references[annotatable_attachment_id].add(
            label + " > annotatable attachment"
        )


async def prepare_course(
    client: httpx.AsyncClient, course_id: int
) -> PreparedCourse:
    """Discover every Canvas file used by course pages and module content."""

    course = await api(client, "GET", f"/courses/{course_id}")
    if int(course.get("id")) != course_id:
        raise RuntimeError(
            f"course identity mismatch: requested {course_id}, got {course.get('id')}"
        )

    pages, modules, course_folders, publication_before = await asyncio.gather(
        paged(client, f"/courses/{course_id}/pages"),
        paged(client, f"/courses/{course_id}/modules"),
        paged(client, f"/courses/{course_id}/folders"),
        publication_snapshot(client, course_id),
    )
    page_details = await gather_limited(
        (
            (
                api,
                (client, "GET", f"/courses/{course_id}/pages/{page['url']}"),
            )
            for page in pages
        )
    )
    module_item_batches = await gather_limited(
        (
            (
                paged,
                (client, f"/courses/{course_id}/modules/{module['id']}/items"),
            )
            for module in modules
        )
    )

    references: dict[int, set[str]] = defaultdict(set)
    for page in page_details:
        add_reference(
            references,
            page.get("body") or "",
            f"Page: {page.get('title') or page.get('url')}",
        )

    assignment_ids: set[int] = set()
    discussion_ids: set[int] = set()
    quiz_ids: set[int] = set()
    item_count = 0
    direct_file_items = 0
    for module, items in zip(modules, module_item_batches):
        for item in items:
            item_count += 1
            label = (
                f"Module: {module.get('name')} > "
                f"{item.get('title') or item.get('type')}"
            )
            add_reference(references, item, label)
            content_id = item.get("content_id")
            item_type = item.get("type")
            if item_type == "File" and content_id:
                references[int(content_id)].add(label)
                direct_file_items += 1
            elif item_type == "Assignment" and content_id:
                assignment_ids.add(int(content_id))
            elif item_type == "Discussion" and content_id:
                discussion_ids.add(int(content_id))
            elif item_type == "Quiz" and content_id:
                quiz_ids.add(int(content_id))

    async def fetch_assignment(assignment_id: int) -> dict:
        return await api(
            client, "GET", f"/courses/{course_id}/assignments/{assignment_id}"
        )

    async def fetch_discussion(discussion_id: int) -> dict:
        return await api(
            client,
            "GET",
            f"/courses/{course_id}/discussion_topics/{discussion_id}",
        )

    async def fetch_quiz(quiz_id: int) -> tuple[dict, list[dict]]:
        quiz, questions = await asyncio.gather(
            api(client, "GET", f"/courses/{course_id}/quizzes/{quiz_id}"),
            paged(client, f"/courses/{course_id}/quizzes/{quiz_id}/questions"),
        )
        return quiz, questions

    assignments = await gather_limited(
        ((fetch_assignment, (record_id,)) for record_id in sorted(assignment_ids))
    )
    discussions = await gather_limited(
        ((fetch_discussion, (record_id,)) for record_id in sorted(discussion_ids))
    )
    quizzes = await gather_limited(
        ((fetch_quiz, (record_id,)) for record_id in sorted(quiz_ids))
    )
    for assignment in assignments:
        add_assignment_references(references, assignment)
    for discussion in discussions:
        add_reference(
            references,
            discussion,
            f"Discussion: {discussion.get('title') or discussion.get('id')}",
        )
    for quiz, questions in quizzes:
        label = f"Quiz: {quiz.get('title') or quiz.get('id')}"
        add_reference(references, quiz, label)
        add_reference(references, questions, label + " questions")

    semaphore = asyncio.Semaphore(12)

    async def get_file(file_id: int) -> tuple[int, dict | None, str | None]:
        async with semaphore:
            try:
                record = await api(client, "GET", f"/files/{file_id}")
            except RuntimeError as exc:
                return file_id, None, str(exc)
            return file_id, record, None

    fetched = await asyncio.gather(
        *(get_file(file_id) for file_id in sorted(references))
    )
    unresolved_file_ids = [file_id for file_id, _, error in fetched if error]
    candidate_files = {
        file_id: record
        for file_id, record, error in fetched
        if record is not None and error is None
    }
    course_folder_map = {
        int(folder["id"]): folder for folder in course_folders if folder.get("id")
    }
    foreign_file_ids = [
        file_id
        for file_id, record in candidate_files.items()
        if int(record.get("folder_id") or 0) not in course_folder_map
    ]
    file_records = {
        file_id: record
        for file_id, record in candidate_files.items()
        if file_id not in foreign_file_ids
    }

    folder_records: dict[int, dict] = {}
    for record in file_records.values():
        current_id = int(record.get("folder_id") or 0)
        seen: set[int] = set()
        while current_id:
            if current_id in seen:
                raise RuntimeError(f"folder ancestry cycle at {current_id}")
            seen.add(current_id)
            folder = course_folder_map.get(current_id)
            if folder is None:
                raise RuntimeError(
                    f"referenced file folder {current_id} is not in course {course_id}"
                )
            folder_records[current_id] = folder
            parent_id = folder.get("parent_folder_id")
            current_id = int(parent_id) if parent_id else 0

    return PreparedCourse(
        course_id=course_id,
        course_name=str(course.get("name") or ""),
        references=dict(references),
        file_records=file_records,
        folder_records=folder_records,
        unresolved_file_ids=sorted(unresolved_file_ids),
        foreign_file_ids=sorted(foreign_file_ids),
        surface_counts={
            "pages": len(page_details),
            "modules": len(modules),
            "module_items": item_count,
            "direct_file_items": direct_file_items,
            "assignments": len(assignments),
            "discussions": len(discussions),
            "quizzes": len(quizzes),
        },
        publication_before=publication_before,
    )


def record_summary(
    prepared: PreparedCourse,
    *, check_only: bool,
    changed_files: int = 0,
    changed_folders: int = 0,
    publication_unchanged: bool | None = None,
    restricted_before_files: int | None = None,
    restricted_before_folders: int | None = None,
    verbose: bool = False,
) -> dict[str, Any]:
    restricted_files = prepared.restricted_files
    restricted_folders = prepared.restricted_folders
    mime_counts = Counter(
        str(record.get("content-type") or record.get("content_type") or "unknown")
        for record in prepared.file_records.values()
    )
    examples = []
    limit = None if verbose else 25
    for file_id in sorted(restricted_files):
        if limit is not None and len(examples) >= limit:
            break
        record = prepared.file_records[file_id]
        examples.append(
            {
                "id": file_id,
                "name": record.get("display_name") or record.get("filename"),
                "content_type": record.get("content-type")
                or record.get("content_type"),
                "reasons": restricted_files[file_id],
                "referenced_from": sorted(prepared.references.get(file_id, set())),
            }
        )
    passed = (
        not restricted_files
        and not restricted_folders
        and not prepared.unresolved_file_ids
        and not prepared.foreign_file_ids
    )
    before_files = (
        len(restricted_files)
        if restricted_before_files is None
        else restricted_before_files
    )
    before_folders = (
        len(restricted_folders)
        if restricted_before_folders is None
        else restricted_before_folders
    )
    return {
        "course_id": prepared.course_id,
        "course": prepared.course_name,
        "check_only": check_only,
        "surfaces": prepared.surface_counts,
        "referenced_files": len(prepared.file_records),
        "referenced_file_types": dict(sorted(mime_counts.items())),
        "folder_chain": len(prepared.folder_records),
        "restricted_before": {
            "files": before_files,
            "folders": before_folders,
        },
        "restricted_after": {
            "files": len(restricted_files),
            "folders": len(restricted_folders),
        },
        "changed": {"files": changed_files, "folders": changed_folders},
        "unresolved_file_ids": prepared.unresolved_file_ids,
        "cross_course_file_ids_not_changed": prepared.foreign_file_ids,
        "restricted_file_examples": examples,
        "restricted_examples_truncated": (
            not verbose and len(restricted_files) > len(examples)
        ),
        "publication_states_unchanged": publication_unchanged,
        "passed": passed if check_only else None,
    }


async def apply_course(
    client: httpx.AsyncClient, prepared: PreparedCourse, *, verbose: bool
) -> dict[str, Any]:
    """Open only prepared files/folders and prove publication states unchanged."""

    if prepared.unresolved_file_ids or prepared.foreign_file_ids:
        raise RuntimeError(
            f"course {prepared.course_id} has unresolved or cross-course references; "
            "no writes are allowed"
        )
    restricted_files = prepared.restricted_files
    restricted_folders = prepared.restricted_folders
    semaphore = asyncio.Semaphore(12)

    async def update_folder(folder_id: int) -> None:
        async with semaphore:
            await api(
                client,
                "PUT",
                f"/folders/{folder_id}",
                data=open_payload(folder=True),
            )

    # Canvas inherits folder restrictions. Open parents before children.
    depths = sorted(
        {
            str(prepared.folder_records[folder_id].get("full_name") or "").count(
                "/"
            )
            for folder_id in restricted_folders
        }
    )
    for depth in depths:
        await asyncio.gather(
            *(
                update_folder(folder_id)
                for folder_id in sorted(restricted_folders)
                if str(
                    prepared.folder_records[folder_id].get("full_name") or ""
                ).count("/")
                == depth
            )
        )

    async def update_file(file_id: int) -> None:
        async with semaphore:
            await api(
                client,
                "PUT",
                f"/files/{file_id}",
                data=open_payload(folder=False),
            )

    await asyncio.gather(*(update_file(file_id) for file_id in sorted(restricted_files)))

    async def refetch_file(file_id: int) -> tuple[int, dict]:
        async with semaphore:
            return file_id, await api(client, "GET", f"/files/{file_id}")

    async def refetch_folder(folder_id: int) -> tuple[int, dict]:
        async with semaphore:
            return folder_id, await api(client, "GET", f"/folders/{folder_id}")

    prepared.file_records = dict(
        await asyncio.gather(
            *(refetch_file(file_id) for file_id in sorted(prepared.file_records))
        )
    )
    prepared.folder_records = dict(
        await asyncio.gather(
            *(
                refetch_folder(folder_id)
                for folder_id in sorted(prepared.folder_records)
            )
        )
    )
    publication_after = await publication_snapshot(client, prepared.course_id)
    if publication_after != prepared.publication_before:
        raise RuntimeError(
            f"course {prepared.course_id} publication-state invariant changed; "
            "stop and inspect Canvas history"
        )
    if prepared.restricted_files or prepared.restricted_folders:
        raise RuntimeError(
            f"course {prepared.course_id} still has restricted referenced resources: "
            f"files={sorted(prepared.restricted_files)} "
            f"folders={sorted(prepared.restricted_folders)}"
        )
    summary = record_summary(
        prepared,
        check_only=False,
        changed_files=len(restricted_files),
        changed_folders=len(restricted_folders),
        publication_unchanged=True,
        restricted_before_files=len(restricted_files),
        restricted_before_folders=len(restricted_folders),
        verbose=verbose,
    )
    summary["passed"] = True
    return summary


async def discover_courses(client: httpx.AsyncClient) -> list[dict[str, Any]]:
    # ``/courses`` contains only courses in which the caller is enrolled. An
    # admin token may manage many teacher courses without an enrollment, so add
    # account-level searches when the token exposes account access.
    records = await paged(
        client,
        "/courses",
        params={
            "state[]": ["available", "unpublished"],
            "include[]": ["term"],
        },
    )
    try:
        accounts = await paged(client, "/accounts")
    except RuntimeError:
        accounts = []

    async def account_matches(account_id: int) -> list[dict]:
        found: dict[int, dict] = {}
        # IISD currently uses ``CC EXPL`` in the course code. The broader terms
        # cover teacher-renamed copies; the final CCE regex remains fail-closed.
        for search_term in ("CC EXPL", "CCE", "CAREER COLLEGE"):
            for course in await paged(
                client,
                f"/accounts/{account_id}/courses",
                params={
                    "state[]": ["created", "claimed", "available"],
                    "completed": "false",
                    "search_term": search_term,
                    "search_by": "course",
                    "include[]": ["term"],
                },
            ):
                found[int(course["id"])] = course
        return list(found.values())

    if accounts:
        account_batches = await gather_limited(
            (
                (account_matches, (int(account["id"]),))
                for account in accounts
                if account.get("id")
            ),
            limit=4,
        )
        records.extend(course for batch in account_batches for course in batch)

    records = list({int(course["id"]): course for course in records}.values())
    matches = []
    for course in records:
        haystack = " ".join(
            str(course.get(field) or "")
            for field in ("name", "course_code", "sis_course_id")
        )
        if not CCE_COURSE_RE.search(haystack):
            continue
        matches.append(
            {
                "id": int(course["id"]),
                "name": course.get("name"),
                "course_code": course.get("course_code"),
                "workflow_state": course.get("workflow_state"),
                "term": (course.get("term") or {}).get("name"),
            }
        )
    return sorted(matches, key=lambda record: (record.get("name") or "", record["id"]))


def read_courses_file(path: str) -> list[int]:
    course_ids: list[int] = []
    for line_number, raw in enumerate(Path(path).read_text().splitlines(), start=1):
        value = raw.split("#", 1)[0].strip()
        if not value:
            continue
        if not value.isdigit():
            raise SystemExit(
                f"{path}:{line_number}: expected one numeric Canvas course ID"
            )
        course_ids.append(int(value))
    return course_ids


def read_token() -> str:
    if sys.stdin.isatty():
        return getpass.getpass("Canvas access token (hidden): ").strip()
    return sys.stdin.readline().strip()


def self_test() -> None:
    sample = """
    <img src="/courses/98060/files/123/preview" alt="one">
    <a href="https://learn.irvingisd.net/courses/98060/files/456/download?download_frd=1">PDF</a>
    <iframe data-api-endpoint="/api/v1/courses/98060/files/789"></iframe>
    <a href="/courses/98060/files/folder/CCR%20Materials?preview=901">Folder preview</a>
    <a href="https://example.org/files/words/not-an-id">outside file</a>
    """
    assert file_ids_in_html(sample) == {123, 456, 789, 901}
    assignment_references: dict[int, set[str]] = defaultdict(set)
    add_assignment_references(
        assignment_references,
        {
            "id": 42,
            "name": "Annotate this PDF",
            "description": '<a href="/courses/98060/files/555">Reference</a>',
            "annotatable_attachment_id": 777,
        },
    )
    assert assignment_references == {
        555: {"Assignment: Annotate this PDF"},
        777: {"Assignment: Annotate this PDF > annotatable attachment"},
    }
    assert restriction_reasons(
        {
            "locked": False,
            "hidden": False,
            "lock_at": None,
            "unlock_at": None,
            "visibility_level": "course",
        }
    ) == []
    assert restriction_reasons(
        {
            "locked": True,
            "hidden": True,
            "lock_at": "2026-08-24T12:00:00Z",
            "unlock_at": "2026-08-25T12:00:00Z",
            "visibility_level": "inherit",
        }
    ) == [
        "locked",
        "hidden",
        "lock_at",
        "unlock_at",
    ]
    assert "visibility_level" not in open_payload(folder=False)
    assert "visibility_level" not in open_payload(folder=True)
    assert CCE_COURSE_RE.search("S1 - CC EXPLOR - LUCERO")
    print("self-test: PASS")


async def async_main(args: argparse.Namespace, token: str) -> int:
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as client:
        me = await api(client, "GET", "/users/self")
        print(
            f"Signed in as {me.get('name')} (user {me.get('id')}); "
            f"mode={'APPLY' if args.apply else 'CHECK'}",
            file=sys.stderr,
        )
        if args.discover:
            matches = await discover_courses(client)
            print(json.dumps({"discovered_cce_courses": matches}, indent=2))
            return 0

        course_ids = sorted(set(args.course_id))
        prepared_courses: list[PreparedCourse] = []
        for course_id in course_ids:
            print(f"Preflighting course {course_id}...", file=sys.stderr)
            prepared_courses.append(await prepare_course(client, course_id))

        if args.apply:
            blockers = [
                prepared.course_id
                for prepared in prepared_courses
                if prepared.unresolved_file_ids or prepared.foreign_file_ids
            ]
            if blockers:
                summaries = [
                    record_summary(
                        prepared,
                        check_only=True,
                        publication_unchanged=None,
                        verbose=args.verbose,
                    )
                    for prepared in prepared_courses
                ]
                print(json.dumps(summaries, indent=2))
                print(
                    "Apply aborted before all writes because one or more courses "
                    f"have unresolved/cross-course file references: {blockers}",
                    file=sys.stderr,
                )
                return 2
            results = []
            for prepared in prepared_courses:
                print(f"Applying course {prepared.course_id}...", file=sys.stderr)
                results.append(
                    await apply_course(client, prepared, verbose=args.verbose)
                )
        else:
            results = [
                record_summary(
                    prepared,
                    check_only=True,
                    publication_unchanged=None,
                    verbose=args.verbose,
                )
                for prepared in prepared_courses
            ]
        print(json.dumps(results, indent=2))
        return 0 if all(result.get("passed") for result in results) else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audit or unlock Canvas files referenced by CCE pages and module content "
            "without changing publication states."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="read-only audit")
    mode.add_argument("--apply", action="store_true", help="apply and verify repair")
    mode.add_argument(
        "--discover",
        action="store_true",
        help="list CCE-looking courses available to this token; never applies",
    )
    parser.add_argument(
        "--course-id",
        type=int,
        action="append",
        default=[],
        help="Canvas course ID (repeatable)",
    )
    parser.add_argument(
        "--courses-file", help="text file containing one Canvas course ID per line"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="include every restricted file in JSON"
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.courses_file:
        args.course_id.extend(read_courses_file(args.courses_file))
    if args.discover and args.course_id:
        parser.error("--discover does not accept --course-id")
    if not args.discover and not args.course_id:
        parser.error("give --course-id/--courses-file, or use --discover")
    if not args.discover and not (args.check or args.apply):
        parser.error("choose --check or --apply")
    token = read_token()
    if not token:
        raise SystemExit("A Canvas token is required on hidden stdin.")
    try:
        return asyncio.run(async_main(args, token))
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
