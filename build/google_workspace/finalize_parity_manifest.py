#!/usr/bin/env python3
"""Record a verified final native-Drive parity readback in the manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "cce-curriculum/notes/google-workspace-parity-manifest.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--updates-json", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    updates = json.loads(args.updates_json)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    artifacts = {artifact["key"]: artifact for artifact in manifest["artifacts"]}

    for key, update in updates.items():
        if key not in artifacts:
            raise SystemExit(f"parity manifest finalize: unknown artifact {key}")
        artifact = artifacts[key]
        native = artifact["drive"]["native_google_file"]
        count = int(update["slide_count"])
        native["revision_id_at_check"] = update["revision_id"]
        native["bytes_at_check"] = int(update["bytes_at_check"])
        native["slide_count"] = count
        qa = artifact["qa"]
        qa.update(
            {
                "checked_on": "2026-08-24",
                "native_render_count": count,
                "native_notes_page_count": count,
                "all_native_slides_visually_compared": True,
                "mr_lucero_hits": 0,
                "notes": update["notes"],
            }
        )
        artifact["sync_status"] = {
            "as_of": "2026-08-24",
            "local_source": "current",
            "canvas_file": "current-2026-08-24-deploy",
            "drive_office_release": "current-2026-08-24",
            "drive_native_google_file": "current-2026-08-24",
        }

    if not args.apply:
        print(json.dumps({"mode": "preview", "artifacts": sorted(updates)}, indent=2))
        return
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"mode": "apply", "artifacts": sorted(updates)}, indent=2))


if __name__ == "__main__":
    main()
