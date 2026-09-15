#!/usr/bin/env python3
"""Safely replace changed stored Drive releases while preserving file IDs.

This helper is intentionally limited to ordinary stored binaries. It never
touches native Google files and never calls ``rclone sync``. Every target must
already have a recorded Drive ID; renamed replacements update the old file's
bytes first and then rename that same Drive object.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / "cce-curriculum/notes/google-workspace-drive-state.json"
PARITY_PATH = ROOT / "cce-curriculum/notes/google-workspace-parity-manifest.json"
POLICY_PATH = ROOT / "public-site/publication-policy.json"
REMOTE = "iisd-drive:"
DRIVE_ROOT_ID = "1FbY0WdnXN-PkW6Vi76qcpDfp7SKq5c5H"
DEFAULT_DECK_KEYS = {
    "1sw-wk0-day5-source-grounded-slides",
    "1sw-wk1-day5-manufacturing-source-grounded-slides",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"Drive release sync: FAIL: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rclone(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    command = [
        "rclone",
        *args,
        "--log-level",
        "ERROR",
        "--drive-root-folder-id",
        DRIVE_ROOT_ID,
    ]
    return subprocess.run(
        command,
        cwd=ROOT,
        check=check,
        text=True,
        capture_output=True,
    )


def remote_record(remote_path: str, *, required: bool = True) -> dict | None:
    result = rclone("lsjson", "--hash", "--metadata", f"{REMOTE}{remote_path}", check=False)
    if result.returncode != 0:
        if required:
            raise SystemExit(
                f"Drive release sync: FAIL: cannot read {remote_path!r}: "
                f"{result.stderr.strip() or result.stdout.strip()}"
            )
        return None
    records = json.loads(result.stdout)
    if not records:
        if required:
            raise SystemExit(f"Drive release sync: FAIL: missing {remote_path!r}")
        return None
    require(len(records) == 1, f"ambiguous remote path {remote_path!r}")
    return records[0]


def changed_resource_paths() -> set[str]:
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
        path = record[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path.startswith("docs/resources/") and path.lower().endswith(".pdf"):
            paths.add(path)
    return paths


def build_plan(deck_keys: set[str], *, include_resources: bool = True) -> list[dict]:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    parity = json.loads(PARITY_PATH.read_text(encoding="utf-8"))
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))

    by_source: dict[str, dict] = {}
    for unit in state["units"]:
        for release in [
            *unit.get("public_releases", []),
            *unit.get("complete_releases", []),
        ]:
            by_source.setdefault(
                release["source"],
                {
                    "unit_title": unit["unit_folder"]["title"],
                    "drive_name": release["drive_name"],
                    "drive_id": release["drive_file_id"],
                },
            )

    plan: list[dict] = []
    superseded = policy.get("superseded_resources", {})
    replacement_sources = set(superseded.values())
    if include_resources:
        for source in sorted(changed_resource_paths()):
            if source in replacement_sources or source not in by_source:
                continue
            record = by_source[source]
            plan.append(
                {
                    "source": source,
                    "local": str((ROOT / source).resolve()),
                    "remote": (
                        f"{record['unit_title']}/Download Releases/"
                        f"{record['drive_name']}"
                    ),
                    "drive_id": record["drive_id"],
                    "final_name": record["drive_name"],
                }
            )

        for old_source, new_source in superseded.items():
            if old_source not in by_source and new_source in by_source:
                continue  # already replaced on Drive; nothing left to rename
            require(old_source in by_source, f"no recorded Drive ID for {old_source}")
            local = ROOT / new_source
            require(local.is_file(), f"replacement file is missing: {new_source}")
            record = by_source[old_source]
            base = f"{record['unit_title']}/Download Releases"
            plan.append(
                {
                    "source": new_source,
                    "replaces": old_source,
                    "local": str(local.resolve()),
                    "remote": f"{base}/{record['drive_name']}",
                    "rename_to": f"{base}/{local.name}",
                    "drive_id": record["drive_id"],
                    "final_name": local.name,
                }
            )

    artifacts = {artifact["key"]: artifact for artifact in parity["artifacts"]}
    for key in sorted(deck_keys):
        require(key in artifacts, f"unknown parity artifact {key!r}")
        artifact = artifacts[key]
        drive = artifact["drive"]
        source = artifact["source"]["path"]
        local = ROOT / source
        require(local.is_file(), f"deck source is missing: {source}")
        office = drive["office_release"]
        plan.append(
            {
                "source": source,
                "deck_key": key,
                "local": str(local.resolve()),
                "remote": (
                    f"{drive['unit_folder']['title']}/Download Releases/"
                    f"{office['name']}"
                ),
                "drive_id": office["id"],
                "final_name": office["name"],
            }
        )

    seen_ids: set[str] = set()
    for target in plan:
        require(target["drive_id"] not in seen_ids, f"duplicate target ID {target['drive_id']}")
        seen_ids.add(target["drive_id"])
    return plan


def preflight(plan: list[dict]) -> list[dict]:
    results = []
    for target in plan:
        local = Path(target["local"])
        require(local.is_file(), f"missing local file {local}")
        current = remote_record(target["remote"])
        require(current.get("ID") == target["drive_id"], f"Drive ID drift for {target['source']}")
        if rename_to := target.get("rename_to"):
            existing_destination = remote_record(rename_to, required=False)
            require(
                existing_destination is None
                or existing_destination.get("ID") == target["drive_id"],
                f"rename destination already exists with another ID: {rename_to}",
            )
        results.append(
            {
                **target,
                "local_bytes": local.stat().st_size,
                "local_sha256": sha256(local),
                "remote_before_bytes": current.get("Size"),
                "remote_before_sha256": current.get("Hashes", {}).get("sha256"),
            }
        )
    return results


def apply(plan: list[dict]) -> list[dict]:
    results = []
    for target in plan:
        local = Path(target["local"])
        rclone("copyto", str(local), f"{REMOTE}{target['remote']}")
        current_path = target["remote"]
        if rename_to := target.get("rename_to"):
            rclone("moveto", f"{REMOTE}{current_path}", f"{REMOTE}{rename_to}")
            current_path = rename_to
        final = remote_record(current_path)
        local_hash = sha256(local)
        require(final.get("ID") == target["drive_id"], f"Drive ID changed for {target['source']}")
        require(int(final.get("Size") or -1) == local.stat().st_size, f"byte-count mismatch for {target['source']}")
        require(
            final.get("Hashes", {}).get("sha256") == local_hash,
            f"SHA-256 mismatch for {target['source']}",
        )
        results.append(
            {
                "source": target["source"],
                "drive_id": final["ID"],
                "drive_name": target["final_name"],
                "bytes": local.stat().st_size,
                "sha256": local_hash,
                "remote_path": current_path,
            }
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--deck-key", action="append", default=[])
    parser.add_argument(
        "--decks-only",
        action="store_true",
        help="Skip changed PDF releases and operate only on the selected deck keys.",
    )
    args = parser.parse_args()
    deck_keys = set(args.deck_key) or DEFAULT_DECK_KEYS
    plan = build_plan(deck_keys, include_resources=not args.decks_only)
    checked = preflight(plan)
    if not args.apply:
        print(json.dumps({"mode": "preflight", "count": len(checked), "files": checked}, indent=2))
        return
    results = apply(plan)
    print(json.dumps({"mode": "apply", "count": len(results), "files": results}, indent=2))


if __name__ == "__main__":
    main()
