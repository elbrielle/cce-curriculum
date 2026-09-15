#!/usr/bin/env python3
"""Verify the recorded Units_CCR folder tree against current local distribution sources."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "cce-curriculum/notes/google-workspace-distribution-inventory.json"
DRIVE_STATE = ROOT / "cce-curriculum/notes/google-workspace-drive-state.json"
PARITY = ROOT / "cce-curriculum/notes/google-workspace-parity-manifest.json"
STUDENT_DOCS = ROOT / "build/google_docs/student_worksheet_links.json"
DRIVE_ID = re.compile(r"^[A-Za-z0-9_-]+$")
STUDENT_PAGE_ID = re.compile(r"^([1-6])SW-Wk(\d+)-Day([1-5])$")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"Drive distribution: FAIL: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_source(value: object) -> Path:
    require(isinstance(value, str) and value, "release source is missing")
    pure = PurePosixPath(value)
    require(not pure.is_absolute() and ".." not in pure.parts, f"unsafe source path {value}")
    path = (ROOT / pure).resolve()
    require(path == ROOT or ROOT in path.parents, f"outside-repository source path {value}")
    return path


def require_id(value: object, label: str, seen: set[str]) -> str:
    require(isinstance(value, str) and bool(DRIVE_ID.fullmatch(value)), f"invalid {label}")
    require(value not in seen, f"reused {label}: {value}")
    seen.add(value)
    return value


def main() -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    state = json.loads(DRIVE_STATE.read_text(encoding="utf-8"))
    parity = json.loads(PARITY.read_text(encoding="utf-8"))
    student_docs = json.loads(STUDENT_DOCS.read_text(encoding="utf-8"))

    require(inventory.get("unit_count") == 36, "distribution inventory must contain 36 units")
    require(state.get("version") == 1, "unsupported Drive-state version")
    require(state.get("expected_unit_count") == 36, "Drive state must require 36 units")
    require(
        state.get("expected_public_resource_references") == 310,
        "Drive state must require 310 unit-resource references",
    )
    require(state.get("drive_root") == parity.get("drive_root"), "Drive root drift")
    live = state.get("live_verification", {})
    require(
        live.get("verified_student_google_docs") == 173,
        "Drive state must record 173 verified student Google Docs",
    )
    require(
        live.get("verified_native_google_files") == 184,
        "Drive state must record 184 native Google files",
    )

    inventory_units = {row["curriculum_address"]: row for row in inventory["units"]}
    state_units = state.get("units")
    require(isinstance(state_units, list) and len(state_units) == 36, "Drive state unit count drift")
    require(
        {row.get("curriculum_address") for row in state_units} == set(inventory_units),
        "Drive state unit-address set drift",
    )

    seen_folder_ids: set[str] = set()
    seen_file_ids: set[str] = set()
    release_count = 0
    native_support_count = 0
    for row in state_units:
        address = row["curriculum_address"]
        expected = inventory_units[address]
        unit = row.get("unit_folder")
        require(isinstance(unit, dict), f"{address}: unit folder is missing")
        require(unit.get("title") == expected["drive_folder_title"], f"{address}: unit title drift")
        require_id(unit.get("id"), f"{address} unit-folder ID", seen_folder_ids)
        require_id(row.get("google_masters_folder_id"), f"{address} Google Masters ID", seen_folder_ids)
        require_id(row.get("download_releases_folder_id"), f"{address} Download Releases ID", seen_folder_ids)

        releases = row.get("public_releases")
        require(isinstance(releases, list), f"{address}: public releases must be a list")
        expected_releases = {item["source"]: item for item in expected["public_resources"]}
        actual_releases = {item.get("source"): item for item in releases}
        require(len(actual_releases) == len(releases), f"{address}: duplicate release source")
        require(set(actual_releases) == set(expected_releases), f"{address}: release set drift")
        for source, release in actual_releases.items():
            expected_release = expected_releases[source]
            path = safe_source(source)
            require(path.is_file(), f"{address}: missing local release {source}")
            require(release.get("sha256") == expected_release["sha256"], f"{address}: recorded SHA drift for {source}")
            require(release.get("bytes") == expected_release["bytes"], f"{address}: recorded byte-count drift for {source}")
            require(path.stat().st_size == release["bytes"], f"{address}: local byte-count drift for {source}")
            require(sha256(path) == release["sha256"], f"{address}: local SHA drift for {source}")
            require_id(release.get("drive_file_id"), f"{address} release file ID", seen_file_ids)
            require(isinstance(release.get("drive_name"), str) and release["drive_name"], f"{address}: release name is missing")
            release_count += 1

        native_support = row.get("native_support_files", [])
        require(isinstance(native_support, list), f"{address}: native support files must be a list")
        for support in native_support:
            require(isinstance(support, dict), f"{address}: malformed native support record")
            source = support.get("source")
            path = safe_source(source)
            require(path.is_file(), f"{address}: missing native-support source {source}")
            require(path.stat().st_size == support.get("bytes"), f"{address}: native-support byte-count drift")
            require(sha256(path) == support.get("sha256"), f"{address}: native-support SHA drift")
            native_id = require_id(
                support.get("native_google_file_id"),
                f"{address} native support file ID",
                seen_file_ids,
            )
            require(
                support.get("copy_url") == f"https://docs.google.com/document/d/{native_id}/copy",
                f"{address}: native support /copy URL drift",
            )
            release = actual_releases.get(source)
            require(release is not None, f"{address}: native support has no matching Office release")
            require(
                support.get("office_release_file_id") == release.get("drive_file_id"),
                f"{address}: native support Office-release ID drift",
            )
            require(support.get("sharing") == "iis-d-domain-reader", f"{address}: native support sharing drift")
            canvas_source = safe_source(support.get("canvas_source"))
            require(canvas_source.is_file(), f"{address}: native support Canvas source is missing")
            require(
                support["copy_url"] in canvas_source.read_text(encoding="utf-8"),
                f"{address}: native support /copy link is missing from Canvas source",
            )
            public_pages = support.get("public_source_pages")
            require(isinstance(public_pages, list) and public_pages, f"{address}: native support public pages are missing")
            for public_page in public_pages:
                public_path = safe_source(public_page)
                require(public_path.is_file(), f"{address}: native support public page is missing")
                require(
                    support["copy_url"] in public_path.read_text(encoding="utf-8"),
                    f"{address}: native support /copy link is missing from public source",
                )
            native_support_count += 1

    require(release_count == 310, f"expected 310 releases, found {release_count}")

    state_by_address = {row["curriculum_address"]: row for row in state_units}
    registry_root = student_docs.get("drive_root", {})
    require(
        registry_root.get("id") == parity["drive_root"]["id"]
        and registry_root.get("url") == parity["drive_root"]["url"],
        "student Google Doc registry root drift",
    )
    student_rows = student_docs.get("documents")
    require(
        isinstance(student_rows, list) and len(student_rows) == 173,
        "student Google Doc registry must contain 173 rows",
    )
    require(
        len({row.get("page_id") for row in student_rows}) == 173,
        "student Google Doc page IDs must be unique",
    )
    for document in student_rows:
        page_id = document.get("page_id", "")
        match = STUDENT_PAGE_ID.fullmatch(page_id)
        require(match is not None, f"invalid student Google Doc page ID {page_id}")
        address = f"{match.group(1)}SW Wk{match.group(2)}"
        unit = state_by_address.get(address)
        require(unit is not None, f"{page_id}: no matching Drive unit")
        require(
            document.get("folder_id") == unit["google_masters_folder_id"],
            f"{page_id}: Google Masters folder ID drift",
        )
        require(
            isinstance(document.get("folder_path"), str)
            and document["folder_path"].startswith("VILS27/Units_CCR/")
            and document["folder_path"].endswith("/Google Masters"),
            f"{page_id}: canonical folder path drift",
        )
        document_id = require_id(
            document.get("document_id"),
            f"{page_id} student Google Doc ID",
            seen_file_ids,
        )
        require(
            document.get("copy_url")
            == f"https://docs.google.com/document/d/{document_id}/copy",
            f"{page_id}: /copy URL drift",
        )

    for artifact in parity["artifacts"]:
        match = re.fullmatch(r"([1-6]SW Wk\d+) Day \d+", artifact["curriculum_address"])
        if not match:
            continue
        address = match.group(1)
        unit = state_by_address[address]
        drive = artifact["drive"]
        require(drive["unit_folder"]["id"] == unit["unit_folder"]["id"], f"{artifact['key']}: unit-folder ID drift")
        require(drive["google_masters_folder_id"] == unit["google_masters_folder_id"], f"{artifact['key']}: Google Masters ID drift")
        require(drive["download_releases_folder_id"] == unit["download_releases_folder_id"], f"{artifact['key']}: Download Releases ID drift")

    print(
        "Drive distribution: PASS "
        f"units={len(state_units)} folders={len(seen_folder_ids)} "
        f"releases={release_count} native_support={native_support_count} "
        f"student_docs={len(student_rows)}"
    )


if __name__ == "__main__":
    main()
