#!/usr/bin/env python3
"""Record verified fixed-layout Drive uploads in the stable Drive-state file.

This is a mechanical readback step.  It never calls Drive and never invents an
ID.  New IDs must come from the connector upload result file produced during a
verified release run.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / "cce-curriculum/notes/google-workspace-drive-state.json"
INVENTORY_PATH = ROOT / "cce-curriculum/notes/google-workspace-complete-artifact-inventory.json"
READBACK_PATH = ROOT / "tmp/google-drive-pdf-upload-results.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"record complete Drive releases: FAIL: {message}")


def main() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    readback = json.loads(READBACK_PATH.read_text(encoding="utf-8"))

    require(readback.get("count") == len(readback.get("files", [])), "readback count drift")
    uploaded = {(row["a"], row["s"]): row for row in readback["files"]}
    require(len(uploaded) == len(readback["files"]), "duplicate upload readback key")
    require(len({row["id"] for row in readback["files"]}) == len(readback["files"]), "reused upload file ID")

    inventory_by_address = {row["curriculum_address"]: row for row in inventory["units"]}
    state_by_address = {row["curriculum_address"]: row for row in state["units"]}
    require(set(inventory_by_address) == set(state_by_address), "unit address drift")

    seen_ids: set[str] = set()
    complete_count = 0
    for address, unit in state_by_address.items():
        expected = inventory_by_address[address]
        releases = []
        for artifact in expected["required_releases"]:
            source = artifact["source"]
            existing = artifact.get("drive_file")
            if existing:
                file_id = existing["id"]
                drive_name = existing["name"]
            else:
                uploaded_row = uploaded.get((address, source))
                require(uploaded_row is not None, f"{address}: no upload readback for {source}")
                require(uploaded_row.get("parent_id") == unit["download_releases_folder_id"], f"{address}: parent mismatch for {source}")
                require(uploaded_row.get("mime_type") == "application/pdf", f"{address}: MIME mismatch for {source}")
                file_id = uploaded_row["id"]
                drive_name = uploaded_row["n"]
            require(file_id not in seen_ids, f"reused Drive file ID {file_id}")
            seen_ids.add(file_id)
            releases.append(
                {
                    "source": source,
                    "sha256": artifact["sha256"],
                    "bytes": artifact["bytes"],
                    "artifact_type": artifact["artifact_type"],
                    "source_origins": artifact["source_origins"],
                    "drive_file_id": file_id,
                    "drive_name": drive_name,
                    "public_site_included": artifact["public_site_included"],
                }
            )
        unit["complete_releases"] = releases
        unit["public_releases"] = [
            {
                "source": release["source"],
                "sha256": release["sha256"],
                "bytes": release["bytes"],
                "drive_file_id": release["drive_file_id"],
                "drive_name": release["drive_name"],
            }
            for release in releases
            if release["public_site_included"]
        ]
        complete_count += len(releases)

    require(complete_count == inventory["summary"]["required_unit_release_references"], "complete release count drift")
    state["expected_complete_release_references"] = complete_count
    state["expected_complete_unique_sources"] = inventory["summary"]["unique_required_sources"]
    public_count = sum(len(unit["public_releases"]) for unit in state_by_address.values())
    state["expected_public_resource_references"] = public_count
    require(public_count == complete_count, "not every complete release is present on the public site")
    state["checked_on"] = "2026-08-17"
    state["live_verification"]["checked_on"] = "2026-08-17"
    state["live_verification"]["matching_public_releases"] = public_count
    state["complete_release_readback_date"] = readback.get("uploaded_at")
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"record complete Drive releases: PASS releases={complete_count} drive_ids={len(seen_ids)}")


if __name__ == "__main__":
    main()
