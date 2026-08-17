#!/usr/bin/env python3
"""Fail closed on the complete 36-unit Google Drive artifact contract."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "cce-curriculum/notes/google-workspace-complete-artifact-inventory.json"
STATE = ROOT / "cce-curriculum/notes/google-workspace-drive-state.json"
DRIVE_ID = re.compile(r"^[A-Za-z0-9_-]+$")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"complete artifact QA: FAIL: {message}")


def safe_path(value: object) -> Path:
    require(isinstance(value, str) and value, "missing source path")
    pure = PurePosixPath(value)
    require(not pure.is_absolute() and ".." not in pure.parts, f"unsafe source path {value}")
    path = (ROOT / pure).resolve()
    require(path == ROOT or ROOT in path.parents, f"outside-repository source path {value}")
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    state = json.loads(STATE.read_text(encoding="utf-8"))
    summary = inventory.get("summary", {})

    require(summary.get("unit_count") == 36, "unit count must be 36")
    require(summary.get("required_unit_release_references") == 305, "required release count must be 305")
    require(summary.get("unique_required_sources") == 302, "unique source count must be 302")
    require(summary.get("missing_drive_release_references") == 0, "Drive release gaps remain")
    require(summary.get("excluded_artifacts") == 1, "excluded artifact count drift")
    require(
        inventory.get("excluded_artifacts")
        == [
            {
                "curriculum_address": "2SW Wk4",
                "source": "docs/resources/worksheets/2sw-wk4-evidence-check-teacher-key.pdf",
                "reason": "teacher_answer_key_canvas_only",
            }
        ],
        "teacher-answer-key exclusion drift",
    )

    state_by_address = {row["curriculum_address"]: row for row in state["units"]}
    require(len(state_by_address) == 36, "Drive state unit count drift")
    require(state.get("expected_complete_release_references") == 305, "Drive state release contract drift")
    require(state.get("expected_complete_unique_sources") == 302, "Drive state unique-source contract drift")

    seen_ids: set[str] = set()
    seen_refs = 0
    unique_sources: set[str] = set()
    for unit in inventory["units"]:
        address = unit["curriculum_address"]
        state_unit = state_by_address.get(address)
        require(state_unit is not None, f"missing Drive state for {address}")
        actual = {row["source"]: row for row in state_unit.get("complete_releases", [])}
        require(len(actual) == len(state_unit.get("complete_releases", [])), f"{address}: duplicate complete release source")
        expected = {row["source"]: row for row in unit["required_releases"]}
        require(set(actual) == set(expected), f"{address}: complete release set drift")

        for source, artifact in expected.items():
            record = actual[source]
            path = safe_path(source)
            require(path.is_file(), f"{address}: source is missing {source}")
            require(path.suffix.lower() == ".pdf" or artifact["google_native_required"], f"{address}: unsupported release type {source}")
            require(path.stat().st_size == artifact["bytes"] == record["bytes"], f"{address}: byte-count drift for {source}")
            require(sha256(path) == artifact["sha256"] == record["sha256"], f"{address}: SHA drift for {source}")
            require(artifact["drive_file"] is not None, f"{address}: missing Drive record for {source}")
            require(artifact["drive_file"]["id"] == record["drive_file_id"], f"{address}: Drive ID drift for {source}")
            require(artifact["drive_file"]["name"] == record["drive_name"], f"{address}: Drive name drift for {source}")
            require(record["artifact_type"] == artifact["artifact_type"], f"{address}: artifact type drift for {source}")
            require(record["source_origins"] == artifact["source_origins"], f"{address}: source-origin drift for {source}")
            require(record["public_site_included"] == artifact["public_site_included"], f"{address}: public-site decision drift for {source}")
            file_id = record["drive_file_id"]
            require(isinstance(file_id, str) and DRIVE_ID.fullmatch(file_id), f"{address}: invalid Drive ID for {source}")
            require(file_id not in seen_ids, f"reused Drive ID {file_id}")
            seen_ids.add(file_id)
            unique_sources.add(source)
            seen_refs += 1

    require(seen_refs == 305, f"expected 305 release references, found {seen_refs}")
    require(len(unique_sources) == 302, f"expected 302 unique sources, found {len(unique_sources)}")
    print(
        "complete artifact QA: PASS "
        f"units=36 releases={seen_refs} unique_sources={len(unique_sources)} "
        f"drive_ids={len(seen_ids)} exclusions=1"
    )


if __name__ == "__main__":
    main()
