#!/usr/bin/env python3
"""Refresh Drive-state metadata for already verified in-place PDF releases.

This helper never calls Drive. It is intentionally limited to changed local PDF
releases plus the explicit old-to-new replacement map in publication-policy.json.
Run it only after the Drive sync helper has verified stable IDs, sizes, and hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "cce-curriculum/notes/google-workspace-drive-state.json"
POLICY = ROOT / "public-site/publication-policy.json"
COMPLETE_INVENTORY = ROOT / "cce-curriculum/notes/google-workspace-complete-artifact-inventory.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def changed_pdfs() -> set[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    paths: set[str] = set()
    for record in result.stdout.split("\0"):
        if not record:
            continue
        path = record[3:].split(" -> ", 1)[-1]
        if path.startswith("docs/resources/") and path.lower().endswith(".pdf"):
            paths.add(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    state = json.loads(STATE.read_text(encoding="utf-8"))
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    complete_inventory = json.loads(COMPLETE_INVENTORY.read_text(encoding="utf-8"))
    replacements = policy.get("superseded_resources", {})
    targets = changed_pdfs() | set(replacements.values())
    updated = 0
    provenance_updated = 0
    complete_by_address = {
        unit["curriculum_address"]: {
            release["source"]: release for release in unit["required_releases"]
        }
        for unit in complete_inventory["units"]
    }

    for unit in state["units"]:
        for key in ("public_releases", "complete_releases"):
            for release in unit.get(key, []):
                source = replacements.get(release["source"], release["source"])
                if source not in targets:
                    continue
                path = ROOT / source
                if not path.is_file():
                    raise SystemExit(f"Drive state refresh: missing {source}")
                release["source"] = source
                release["drive_name"] = path.name
                release["bytes"] = path.stat().st_size
                release["sha256"] = sha256(path)
                updated += 1

        expected_complete = complete_by_address[unit["curriculum_address"]]
        for release in unit.get("complete_releases", []):
            expected = expected_complete[release["source"]]
            before = (
                release.get("artifact_type"),
                release.get("source_origins"),
                release.get("public_site_included"),
            )
            release["artifact_type"] = expected["artifact_type"]
            release["source_origins"] = expected["source_origins"]
            release["public_site_included"] = expected["public_site_included"]
            after = (
                release["artifact_type"],
                release["source_origins"],
                release["public_site_included"],
            )
            provenance_updated += before != after

    if not args.apply:
        print(json.dumps({"mode": "preview", "records": updated, "provenance_records": provenance_updated}, indent=2))
        return
    STATE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"mode": "apply", "records": updated, "provenance_records": provenance_updated}, indent=2))


if __name__ == "__main__":
    main()
