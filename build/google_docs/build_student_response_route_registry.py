#!/usr/bin/env python3
"""Build the deterministic, local-only CCE student response-route draft.

The draft joins four read-only inputs:

* the current 180-day source specification;
* the existing 173 native Google Doc IDs;
* trusted-read manifests for those 173 Docs plus the known Week 0 Day 1 Doc; and
* seven reviewed manual specifications for the registry gaps.

No network client is imported and no Drive or Canvas mutation is possible from
this script.  The output is intentionally marked ``draft`` and contains no
Canvas page identity.  A separately reviewed registry is required before any
Canvas apply operation.

Usage:

    python3 build/google_docs/build_student_response_route_registry.py
    python3 build/google_docs/build_student_response_route_registry.py --check
    python3 build/google_docs/build_student_response_route_registry.py --stdout
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GOOGLE_DOCS_ROOT = ROOT / "build" / "google_docs"
SOURCE_SPEC = GOOGLE_DOCS_ROOT / "student_worksheet_source_specs.draft.json"
LIVE_LINK_REGISTRY = GOOGLE_DOCS_ROOT / "student_worksheet_links.json"
MANUAL_SPECS = GOOGLE_DOCS_ROOT / "student_response_route_manual_specs.json"
TRUSTED_READ_CURRENT_ROOT = ROOT / ".tmp" / "docs-trusted-read" / "20260825-current"
TRUSTED_READ_FINAL_ROOT = ROOT / ".tmp" / "docs-trusted-read" / "20260825-final"
DEFAULT_OUTPUT = GOOGLE_DOCS_ROOT / "student_response_route_registry.draft.json"
FINAL_REGISTRY = GOOGLE_DOCS_ROOT / "student_response_route_registry.json"

CANONICAL_DRIVE_ROOT_ID = "1FbY0WdnXN-PkW6Vi76qcpDfp7SKq5c5H"
CANONICAL_DRIVE_ROOT_PATH = "VILS27/Units_CCR"
GOOGLE_MASTERS_SUFFIX = "/Google Masters"
KNOWN_WEEK_0_DAY_1_DOC_ID = "1rb8sHX56FYPeddRX-QX0_YG-bD7FrZZpQnh06q0r9w8"
LEGACY_PATH_PATTERNS = (
    "27 CCR Planning",
    "27%20CCR%20Planning",
    "iisd-drive:27 CCR Planning",
)
DAY_KEY_RE = re.compile(
    r"^(?P<six_weeks>[1-6])SW-Wk(?P<week>\d+)-Day(?P<day>[1-5])$"
)
DAY_TITLE_PREFIX_RE = re.compile(r"^Day\s+\d+\s*:\s*", re.IGNORECASE)


class RegistryError(ValueError):
    """Raised when an input violates a fail-closed registry invariant."""


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_json(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RegistryError(f"Required input is missing: {repo_path(path)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RegistryError(f"Expected a JSON object: {repo_path(path)}")
    return payload


def validate_hash(path_text: str, expected: str | None, context: str) -> None:
    if not path_text or not expected:
        raise RegistryError(f"{context}: path and SHA-256 are required")
    path = (ROOT / path_text).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as error:
        raise RegistryError(f"{context}: source escapes the repository: {path_text}") from error
    if not path.is_file():
        raise RegistryError(f"{context}: source is missing: {path_text}")
    actual = sha256_path(path)
    if actual != expected:
        raise RegistryError(
            f"{context}: stale SHA-256 for {path_text}; expected {expected}, found {actual}"
        )


def reject_legacy_path(value: str | None, context: str) -> None:
    if value is None:
        return
    if any(pattern.casefold() in value.casefold() for pattern in LEGACY_PATH_PATTERNS):
        raise RegistryError(f"{context}: legacy Drive routing is forbidden: {value}")


def validate_folder(folder_id: Any, folder_path: Any, context: str) -> None:
    if not isinstance(folder_id, str) or not folder_id.strip():
        raise RegistryError(f"{context}: canonical Google Masters folder_id is required")
    if not isinstance(folder_path, str):
        raise RegistryError(f"{context}: canonical Google Masters folder_path is required")
    reject_legacy_path(folder_path, context)
    if not folder_path.startswith(f"{CANONICAL_DRIVE_ROOT_PATH}/"):
        raise RegistryError(
            f"{context}: folder must be below {CANONICAL_DRIVE_ROOT_PATH}: {folder_path}"
        )
    if not folder_path.endswith(GOOGLE_MASTERS_SUFFIX):
        raise RegistryError(f"{context}: native Docs must route to Google Masters: {folder_path}")


def coordinates(day_key: str) -> tuple[int, int, int]:
    match = DAY_KEY_RE.fullmatch(day_key)
    if not match:
        raise RegistryError(f"Invalid day_key: {day_key}")
    return tuple(int(match.group(name)) for name in ("six_weeks", "week", "day"))


def target_title(day: dict[str, Any], manual: dict[str, Any] | None) -> str:
    if manual is not None:
        title = manual.get("title")
        if not isinstance(title, str) or not title.strip():
            raise RegistryError(f"{day['day_key']}: reviewed manual title is required")
        return title.strip()
    h1 = day.get("h1")
    if not isinstance(h1, str) or not h1.strip():
        raise RegistryError(f"{day['day_key']}: current H1 is required for target title")
    lesson_title = DAY_TITLE_PREFIX_RE.sub("", h1).strip()
    return (
        f"CCE | {day['six_weeks']}SW Wk{day['week']} Day {day['day']} | "
        f"{lesson_title}"
    )


def validate_source_record(day: dict[str, Any]) -> None:
    key = str(day["day_key"])
    validate_hash(
        str(day["day_source"]["path"]),
        day["day_source"].get("sha256"),
        f"{key} day_source",
    )
    validate_hash(
        str(day["canvas_builder"]["path"]),
        day["canvas_builder"].get("sha256"),
        f"{key} canvas_builder",
    )
    template = day.get("student_template")
    if not isinstance(template, dict):
        raise RegistryError(f"{key}: student_template is required")
    validate_hash(str(template["path"]), template.get("sha256"), f"{key} student_template")

    for index, source in enumerate(day.get("builder_linked_worksheet_sources", [])):
        validate_hash(
            str(source["source_path"]),
            source.get("source_sha256"),
            f"{key} worksheet source {index}",
        )
        if source.get("pdf_path") is not None:
            validate_hash(
                str(source["pdf_path"]),
                source.get("pdf_sha256"),
                f"{key} worksheet PDF {index}",
            )

    seen_pdfs: set[tuple[str, str]] = set()
    for index, source in enumerate(day.get("linked_pdfs", [])):
        path_text = source.get("path")
        digest = source.get("sha256")
        if path_text is None and digest is None:
            continue
        if not isinstance(path_text, str) or not isinstance(digest, str):
            raise RegistryError(f"{key} linked PDF {index}: partial local source identity")
        pair = (path_text, digest)
        if pair in seen_pdfs:
            continue
        seen_pdfs.add(pair)
        validate_hash(path_text, digest, f"{key} linked PDF {index}")


def source_evidence(
    day: dict[str, Any],
    manual: dict[str, Any] | None,
    manual_file_sha256: str,
) -> dict[str, Any]:
    worksheets = []
    for source in day.get("builder_linked_worksheet_sources", []):
        worksheets.append(
            {
                "path": source["source_path"],
                "sha256": source["source_sha256"],
                "pdf_path": source.get("pdf_path"),
                "pdf_sha256": source.get("pdf_sha256"),
                "audience": source.get("audience"),
                "variant_of": source.get("variant_of"),
                "is_response_route_candidate": source.get("is_response_route_candidate"),
            }
        )

    printable_by_identity: dict[tuple[str, str], dict[str, str]] = {}
    for source in day.get("linked_pdfs", []):
        path_text = source.get("path")
        digest = source.get("sha256")
        if isinstance(path_text, str) and isinstance(digest, str):
            printable_by_identity[(path_text, digest)] = {
                "path": path_text,
                "sha256": digest,
            }

    evidence: dict[str, Any] = {
        "source_spec_record_sha256": sha256_json(day),
        "day_source": {
            "path": day["day_source"]["path"],
            "sha256": day["day_source"]["sha256"],
        },
        "canvas_builder": {
            "path": day["canvas_builder"]["path"],
            "sha256": day["canvas_builder"]["sha256"],
        },
        "student_template": {
            "path": day["student_template"]["path"],
            "sha256": day["student_template"]["sha256"],
        },
        "worksheet_sources": worksheets,
        "linked_printable_sources": [
            printable_by_identity[key] for key in sorted(printable_by_identity)
        ],
        "manual_spec": None,
    }
    if manual is not None:
        evidence["manual_spec"] = {
            "path": repo_path(MANUAL_SPECS),
            "file_sha256": manual_file_sha256,
            "record_sha256": sha256_json(manual),
            "layout_spec_status": manual["layout_spec_status"],
            "content_spec": manual["content_spec"],
            "supplemental_sources": manual.get("supplemental_sources", []),
        }
    return evidence


def load_trusted_read(
    day_key: str,
    document_id: str,
) -> dict[str, Any]:
    final_directory = TRUSTED_READ_FINAL_ROOT / day_key
    current_directory = TRUSTED_READ_CURRENT_ROOT / day_key
    directory = final_directory if final_directory.is_dir() else current_directory
    manifest_path = directory / "manifest.json"
    document_text_path = directory / "document-text.md"
    manifest = load_json(manifest_path)
    if manifest.get("kind") != "google-docs-trusted-read" or manifest.get("status") != "complete":
        raise RegistryError(f"{day_key}: trusted read is not complete")
    target = manifest.get("target")
    if not isinstance(target, dict) or target.get("documentId") != document_id:
        raise RegistryError(f"{day_key}: trusted-read document ID does not match the live registry")
    revision_id = target.get("revisionId")
    if not isinstance(revision_id, str) or not revision_id:
        raise RegistryError(f"{day_key}: trusted-read revision ID is missing")
    file_record = manifest.get("files", {}).get("document_text", {})
    semantic_hash = file_record.get("sha256")
    if not isinstance(semantic_hash, str) or not semantic_hash:
        raise RegistryError(f"{day_key}: trusted-read semantic hash is missing")
    if not document_text_path.is_file():
        raise RegistryError(f"{day_key}: trusted-read document-text.md is missing")
    if sha256_path(document_text_path) != semantic_hash:
        raise RegistryError(f"{day_key}: trusted-read document-text.md hash mismatch")
    return {
        "manifest_path": repo_path(manifest_path),
        "manifest_sha256": sha256_path(manifest_path),
        "revision_id": revision_id,
        "semantic_hash": semantic_hash,
        "live_title": target.get("title"),
    }


def validate_manual_spec(
    manual: dict[str, Any],
    day: dict[str, Any],
) -> None:
    key = str(day["day_key"])
    if manual.get("layout_spec_status") != "reviewed":
        raise RegistryError(f"{key}: manual layout specification is not reviewed")
    validate_folder(manual.get("folder_id"), manual.get("folder_path"), f"{key} manual spec")
    guards = manual.get("source_guards")
    if not isinstance(guards, dict):
        raise RegistryError(f"{key}: manual source_guards are required")
    expected = {
        "day_source_sha256": day["day_source"]["sha256"],
        "canvas_builder_sha256": day["canvas_builder"]["sha256"],
        "student_template_sha256": day["student_template"]["sha256"],
    }
    for field, wanted in expected.items():
        if guards.get(field) != wanted:
            raise RegistryError(
                f"{key}: manual {field} is stale; expected current source hash {wanted}"
            )
    content_spec = manual.get("content_spec")
    if not isinstance(content_spec, dict) or not content_spec.get("purpose"):
        raise RegistryError(f"{key}: reviewed manual content_spec is required")
    required = content_spec.get("required_elements")
    if not isinstance(required, list) or not required:
        raise RegistryError(f"{key}: reviewed manual required_elements are required")
    for index, source in enumerate(manual.get("supplemental_sources", [])):
        validate_hash(
            str(source.get("path", "")),
            source.get("sha256"),
            f"{key} manual supplemental source {index}",
        )


def build_payload() -> dict[str, Any]:
    source_payload = load_json(SOURCE_SPEC)
    live_payload = load_json(LIVE_LINK_REGISTRY)
    manual_payload = load_json(MANUAL_SPECS)

    if source_payload.get("schema_version") != 1:
        raise RegistryError("Unsupported student source-spec schema")
    if live_payload.get("schema") != 1:
        raise RegistryError("Unsupported live student worksheet registry schema")
    if manual_payload.get("schema_version") != 1:
        raise RegistryError("Unsupported manual response-route spec schema")
    if manual_payload.get("review_status") != "reviewed":
        raise RegistryError("Manual response-route specs must be reviewed")

    drive_root = live_payload.get("drive_root")
    if not isinstance(drive_root, dict):
        raise RegistryError("Live registry Drive root is missing")
    root_name = drive_root.get("name")
    reject_legacy_path(str(root_name) if root_name is not None else None, "live registry root")
    if drive_root.get("id") != CANONICAL_DRIVE_ROOT_ID or root_name != CANONICAL_DRIVE_ROOT_PATH:
        raise RegistryError("Live registry is not routed to canonical VILS27/Units_CCR")
    manual_root = manual_payload.get("canonical_drive_root")
    if manual_root != {"id": CANONICAL_DRIVE_ROOT_ID, "path": CANONICAL_DRIVE_ROOT_PATH}:
        raise RegistryError("Manual specs are not locked to canonical VILS27/Units_CCR")

    if source_payload.get("live_registry", {}).get("sha256") != sha256_path(LIVE_LINK_REGISTRY):
        raise RegistryError("Student source-spec draft is stale against student_worksheet_links.json")

    days = source_payload.get("days")
    live_rows = live_payload.get("documents")
    manual_rows = manual_payload.get("specs")
    if not isinstance(days, list) or len(days) != 180:
        raise RegistryError(f"Expected exactly 180 source days, found {len(days or [])}")
    if not isinstance(live_rows, list) or len(live_rows) != 173:
        raise RegistryError(f"Expected exactly 173 live Google Docs, found {len(live_rows or [])}")
    if not isinstance(manual_rows, list) or len(manual_rows) != 7:
        raise RegistryError(f"Expected exactly seven manual specs, found {len(manual_rows or [])}")

    live_by_key: dict[str, dict[str, Any]] = {}
    live_document_ids: set[str] = set()
    for row in live_rows:
        key = str(row.get("page_id"))
        if key in live_by_key:
            raise RegistryError(f"Duplicate live registry day: {key}")
        document_id = row.get("document_id")
        if not isinstance(document_id, str) or not document_id:
            raise RegistryError(f"{key}: live document ID is missing")
        if document_id in live_document_ids:
            raise RegistryError(f"Duplicate live document ID: {document_id}")
        live_document_ids.add(document_id)
        validate_folder(row.get("folder_id"), row.get("folder_path"), f"{key} live registry")
        live_by_key[key] = row

    manual_by_key: dict[str, dict[str, Any]] = {}
    for row in manual_rows:
        key = str(row.get("day_key"))
        if key in manual_by_key:
            raise RegistryError(f"Duplicate manual spec day: {key}")
        manual_by_key[key] = row

    day_keys = [str(day.get("day_key")) for day in days]
    if len(day_keys) != len(set(day_keys)):
        raise RegistryError("Source-spec draft contains duplicate day keys")
    if day_keys != sorted(day_keys, key=coordinates):
        raise RegistryError("Source-spec days are not in deterministic curriculum order")

    source_manual_keys = {
        str(day["day_key"]) for day in days if day.get("manual_spec_required") is True
    }
    if set(manual_by_key) != source_manual_keys:
        raise RegistryError(
            "Manual specs must exactly cover the source-spec gaps; "
            f"expected {sorted(source_manual_keys, key=coordinates)}, "
            f"found {sorted(manual_by_key, key=coordinates)}"
        )
    if set(live_by_key) | set(manual_by_key) != set(day_keys):
        raise RegistryError("Live plus manual routes do not cover exactly all 180 days")
    if set(live_by_key) & set(manual_by_key):
        raise RegistryError("A route may not be both live-registry and manual-spec owned")

    current_trusted_dirs = {
        path.name for path in TRUSTED_READ_CURRENT_ROOT.iterdir() if path.is_dir()
    }
    final_trusted_dirs = (
        {path.name for path in TRUSTED_READ_FINAL_ROOT.iterdir() if path.is_dir()}
        if TRUSTED_READ_FINAL_ROOT.is_dir()
        else set()
    )
    trusted_dirs = current_trusted_dirs | final_trusted_dirs
    expected_trusted_keys = set(live_by_key) | {
        key for key, row in manual_by_key.items() if row.get("document_id") is not None
    }
    if trusted_dirs != expected_trusted_keys:
        raise RegistryError(
            "Trusted-read directories must exactly cover every known existing Doc; "
            f"missing={sorted(expected_trusted_keys - trusted_dirs)}, "
            f"extra={sorted(trusted_dirs - expected_trusted_keys)}"
        )

    manual_file_sha256 = sha256_path(MANUAL_SPECS)
    routes: list[dict[str, Any]] = []
    for day in days:
        key = str(day["day_key"])
        six_weeks, week, day_number = coordinates(key)
        if (
            int(day.get("six_weeks", -1)),
            int(day.get("week", -1)),
            int(day.get("day", -1)),
        ) != (six_weeks, week, day_number):
            raise RegistryError(f"{key}: coordinate fields do not match day_key")
        validate_source_record(day)

        manual = manual_by_key.get(key)
        live = live_by_key.get(key)
        if manual is not None:
            validate_manual_spec(manual, day)
            document_id = manual.get("document_id")
            folder_id = manual["folder_id"]
            folder_path = manual["folder_path"]
            trusted_read = (
                load_trusted_read(key, document_id)
                if isinstance(document_id, str) and document_id
                else None
            )
            subtitle = manual.get("subtitle")
            layout_spec_status = manual["layout_spec_status"]
        else:
            assert live is not None
            document_id = live["document_id"]
            folder_id = live["folder_id"]
            folder_path = live["folder_path"]
            trusted_read = load_trusted_read(key, document_id)
            subtitle = None
            layout_spec_status = "source_derived_pending_content_review"

        if document_id is not None and (not isinstance(document_id, str) or not document_id):
            raise RegistryError(f"{key}: invalid document ID")
        if key == "1SW-Wk0-Day1" and document_id != KNOWN_WEEK_0_DAY_1_DOC_ID:
            raise RegistryError("1SW-Wk0-Day1 must preserve its known native Google Doc ID")
        title = target_title(day, manual)
        if document_id is None:
            document_status = "pending_creation"
        elif trusted_read is None:
            document_status = "existing_trusted_read_pending"
        else:
            document_status = "existing_trusted_read"

        google_doc = {
            "id": document_id,
            "revision_id": trusted_read["revision_id"] if trusted_read else None,
            "semantic_hash": trusted_read["semantic_hash"] if trusted_read else None,
            "live_title": trusted_read["live_title"] if trusted_read else None,
            "title_status": (
                "not_read"
                if trusted_read is None
                else ("current" if trusted_read["live_title"] == title else "rename_pending")
            ),
            "status": document_status,
            "copy_url": (
                f"https://docs.google.com/document/d/{document_id}/copy"
                if document_id
                else None
            ),
            "pdf_export_url": (
                f"https://docs.google.com/document/d/{document_id}/export?format=pdf"
                if document_id
                else None
            ),
            "folder_id": folder_id,
            "folder_path": folder_path,
            "trusted_read": (
                {
                    "manifest_path": trusted_read["manifest_path"],
                    "manifest_sha256": trusted_read["manifest_sha256"],
                }
                if trusted_read
                else None
            ),
        }
        routes.append(
            {
                "route_id": key,
                "day_key": key,
                "six_weeks": six_weeks,
                "week": week,
                "day": day_number,
                "title": title,
                "subtitle": subtitle,
                "layout_spec_status": layout_spec_status,
                "source": source_evidence(day, manual, manual_file_sha256),
                "google_doc": google_doc,
                "onenote": {
                    "status": "pending",
                    "url": None,
                },
                "canvas": {
                    "status": "pending_fresh_source_course_audit",
                    "source_course": {
                        "course_id": None,
                        "teacher": None,
                        "student": None,
                    },
                },
            }
        )

    manual_existing_count = sum(
        isinstance(row.get("document_id"), str) and bool(row.get("document_id"))
        for row in manual_rows
    )
    expected_known_count = len(live_by_key) + manual_existing_count
    expected_pending_count = len(manual_rows) - manual_existing_count
    document_ids = [route["google_doc"]["id"] for route in routes if route["google_doc"]["id"]]
    if (
        len(document_ids) != expected_known_count
        or len(document_ids) != len(set(document_ids))
    ):
        raise RegistryError(
            "Known Google Doc IDs must exactly equal the 173 preserved registry IDs "
            f"plus {manual_existing_count} reviewed manual IDs"
        )
    pending_keys = [route["day_key"] for route in routes if route["google_doc"]["id"] is None]
    if len(pending_keys) != expected_pending_count:
        raise RegistryError(
            f"Expected exactly {expected_pending_count} pending document IDs, "
            f"found {len(pending_keys)}"
        )
    if any(
        route["canvas"]["source_course"][field] is not None
        for route in routes
        for field in ("course_id", "teacher", "student")
    ):
        raise RegistryError("Canvas identity must remain null until the fresh source-course audit")
    if any(route["onenote"] != {"status": "pending", "url": None} for route in routes):
        raise RegistryError("OneNote routes must remain pending with a null URL")

    return {
        "schema_version": 1,
        "artifact": "CCE student response-route registry draft",
        "review_status": "draft",
        "mutation_authority": "none",
        "determinism": (
            "No timestamp is emitted. Routes are sorted in curriculum order; all local "
            "source, trusted-read, and manual-spec identities are SHA-256 guarded."
        ),
        "canonical_drive_root": {
            "id": CANONICAL_DRIVE_ROOT_ID,
            "path": CANONICAL_DRIVE_ROOT_PATH,
        },
        "inputs": {
            "source_spec": {
                "path": repo_path(SOURCE_SPEC),
                "sha256": sha256_path(SOURCE_SPEC),
            },
            "live_google_doc_registry": {
                "path": repo_path(LIVE_LINK_REGISTRY),
                "sha256": sha256_path(LIVE_LINK_REGISTRY),
            },
            "manual_specs": {
                "path": repo_path(MANUAL_SPECS),
                "sha256": manual_file_sha256,
            },
            "trusted_read_roots": [
                repo_path(TRUSTED_READ_CURRENT_ROOT),
                repo_path(TRUSTED_READ_FINAL_ROOT),
            ],
        },
        "summary": {
            "route_count": len(routes),
            "preserved_live_registry_document_id_count": len(live_by_key),
            "known_additional_document_id_count": manual_existing_count,
            "known_document_id_count": len(document_ids),
            "document_id_pending_count": len(pending_keys),
            "document_id_pending_day_keys": pending_keys,
            "live_revision_id_count": sum(
                1 for route in routes if route["google_doc"]["revision_id"] is not None
            ),
            "onenote_pending_count": len(routes),
            "canvas_identity_count": 0,
        },
        "routes": routes,
    }


def render_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def resolve_output(value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    candidate = candidate.resolve()
    protected = {
        LIVE_LINK_REGISTRY.resolve(),
        FINAL_REGISTRY.resolve(),
        SOURCE_SPEC.resolve(),
        MANUAL_SPECS.resolve(),
    }
    if candidate in protected:
        raise RegistryError(f"Refusing to overwrite protected registry input/final: {candidate}")
    return candidate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Draft output path (default: build/google_docs/student_response_route_registry.draft.json)",
    )
    parser.add_argument("--check", action="store_true", help="Fail if the draft is missing or stale")
    parser.add_argument("--stdout", action="store_true", help="Print deterministic JSON instead of writing")
    args = parser.parse_args()

    try:
        output = resolve_output(args.output)
        payload = build_payload()
    except (RegistryError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    rendered = render_payload(payload)
    if args.stdout:
        sys.stdout.write(rendered)
        return 0
    if args.check:
        if not output.is_file():
            print(f"Draft is missing: {output}", file=sys.stderr)
            return 1
        if output.read_text(encoding="utf-8") != rendered:
            print(f"Draft is stale: {output}", file=sys.stderr)
            return 1
        print(f"Draft is current: {output}")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(f"Wrote {payload['summary']['route_count']} routes to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
