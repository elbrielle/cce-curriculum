#!/usr/bin/env python3
"""Fail-closed local checks for the CCE Google Workspace parity manifest."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "cce-curriculum/notes/google-workspace-parity-manifest.json"
DRIVE_ID = re.compile(r"^[A-Za-z0-9_-]+$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")
PROTECTED_PUBLIC_PARTS = {
    "avid-reference",
    "canvas-licensed",
    "climber-notes",
    "hl-teacher-resources",
    "reference-pdfs",
    "xello-licensed",
}

ARTIFACT_TYPES = {
    "presentation": {
        "native_mime": "application/vnd.google-apps.presentation",
        "copy_prefix": "https://docs.google.com/presentation/d/",
        "office_suffix": ".pptx",
    },
    "document": {
        "native_mime": "application/vnd.google-apps.document",
        "copy_prefix": "https://docs.google.com/document/d/",
        "office_suffix": ".docx",
    },
    "spreadsheet": {
        "native_mime": "application/vnd.google-apps.spreadsheet",
        "copy_prefix": "https://docs.google.com/spreadsheets/d/",
        "office_suffix": ".xlsx",
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"parity manifest: FAIL: {message}")


def require_drive_id(value: object, label: str) -> str:
    require(isinstance(value, str) and bool(DRIVE_ID.fullmatch(value)), f"invalid {label}")
    return value


def safe_repo_path(value: object, label: str) -> Path:
    require(isinstance(value, str) and value, f"missing {label}")
    pure = PurePosixPath(value)
    require(not pure.is_absolute() and ".." not in pure.parts, f"unsafe {label}: {value}")
    path = (ROOT / pure).resolve()
    require(path == ROOT or ROOT in path.parents, f"outside-repository {label}: {value}")
    return path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(payload.get("version") == 1, "unsupported manifest version")
    root = payload.get("drive_root")
    require(isinstance(root, dict), "drive_root must be an object")
    require_drive_id(root.get("id"), "drive root ID")
    artifacts = payload.get("artifacts")
    require(isinstance(artifacts, list) and artifacts, "artifacts must be a nonempty list")

    keys: set[str] = set()
    drive_file_ids: set[str] = set()
    checked = 0
    for index, artifact in enumerate(artifacts, 1):
        label = f"artifact {index}"
        require(isinstance(artifact, dict), f"{label} must be an object")
        key = artifact.get("key")
        require(isinstance(key, str) and key and key not in keys, f"duplicate or missing {label} key")
        keys.add(key)

        artifact_type = artifact.get("artifact_type")
        require(artifact_type in ARTIFACT_TYPES, f"{key}: unsupported artifact type")
        type_contract = ARTIFACT_TYPES[artifact_type]

        source = artifact.get("source")
        require(isinstance(source, dict), f"{key}: source must be an object")
        source_path = safe_repo_path(source.get("path"), f"{key} source path")
        require(source_path.is_file(), f"{key}: source file is missing")
        expected_sha = source.get("sha256")
        require(isinstance(expected_sha, str) and bool(SHA256.fullmatch(expected_sha)), f"{key}: invalid source SHA-256")
        require(file_sha256(source_path) == expected_sha, f"{key}: source SHA-256 drift")
        require(source_path.stat().st_size == source.get("bytes"), f"{key}: source byte-count drift")

        canvas = artifact.get("canvas")
        require(isinstance(canvas, dict), f"{key}: canvas must be an object")
        require(isinstance(canvas.get("course_id"), int) and canvas["course_id"] > 0, f"{key}: invalid Canvas course ID")
        require(isinstance(canvas.get("file_id"), int) and canvas["file_id"] > 0, f"{key}: invalid Canvas file ID")
        require(canvas.get("locked") is True, f"{key}: Canvas file must be locked")

        drive = artifact.get("drive")
        require(isinstance(drive, dict), f"{key}: drive must be an object")
        require_drive_id(drive.get("google_masters_folder_id"), f"{key} Google Masters folder ID")
        require_drive_id(drive.get("download_releases_folder_id"), f"{key} Download Releases folder ID")
        unit = drive.get("unit_folder")
        require(isinstance(unit, dict), f"{key}: unit folder must be an object")
        require_drive_id(unit.get("id"), f"{key} unit folder ID")

        native = drive.get("native_google_file")
        office = drive.get("office_release")
        require(isinstance(native, dict) and isinstance(office, dict), f"{key}: Drive file records are incomplete")
        native_id = require_drive_id(native.get("id"), f"{key} native file ID")
        office_id = require_drive_id(office.get("id"), f"{key} Office release ID")
        require(native_id not in drive_file_ids and office_id not in drive_file_ids, f"{key}: reused Drive file ID")
        drive_file_ids.update((native_id, office_id))
        expected_copy = f"{type_contract['copy_prefix']}{native_id}/copy"
        require(native.get("copy_url") == expected_copy, f"{key}: native Google /copy URL drift")
        require(native.get("mime_type") == type_contract["native_mime"], f"{key}: native Google MIME drift")
        require(native.get("sharing") == "iis-d-domain-reader", f"{key}: native Google sharing drift")
        require(
            str(office.get("name", "")).lower().endswith(type_contract["office_suffix"]),
            f"{key}: Office release suffix drift",
        )

        public = artifact.get("public_site")
        require(isinstance(public, dict) and isinstance(public.get("included"), bool), f"{key}: public-site decision is missing")
        protected = bool(PROTECTED_PUBLIC_PARTS.intersection(PurePosixPath(source["path"]).parts))
        require(not (protected and public["included"]), f"{key}: protected source cannot enter the public site")
        if not public["included"]:
            require(isinstance(public.get("reason"), str) and public["reason"].strip(), f"{key}: excluded public artifact needs a reason")

        qa = artifact.get("qa")
        require(isinstance(qa, dict), f"{key}: QA record is missing")
        if artifact_type == "presentation":
            require(isinstance(native.get("slide_count"), int) and native["slide_count"] > 0, f"{key}: invalid slide count")
            require(qa.get("native_render_count") == native.get("slide_count"), f"{key}: render count does not match slide count")
            require(qa.get("native_notes_page_count") == native.get("slide_count"), f"{key}: notes count does not match slide count")
            require(qa.get("all_native_slides_visually_compared") is True, f"{key}: native visual comparison is incomplete")
        elif artifact_type == "document":
            require(isinstance(qa.get("native_page_count"), int) and qa["native_page_count"] > 0, f"{key}: invalid native page count")
            require(qa.get("native_render_count") == qa.get("native_page_count"), f"{key}: document render count does not match page count")
            require(qa.get("all_native_pages_visually_compared") is True, f"{key}: native document visual comparison is incomplete")
        require(qa.get("mr_lucero_hits") == 0, f"{key}: incorrect teacher title remains")
        checked += 1

    print(f"parity manifest: PASS artifacts={checked} drive_files={len(drive_file_ids)}")


if __name__ == "__main__":
    main()
