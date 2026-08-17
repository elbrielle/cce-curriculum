#!/usr/bin/env python3
"""Run the local CCE Canvas, public-site, and Google Drive parity contract."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COMMANDS = [
    [sys.executable, "build/google_workspace/build_distribution_inventory.py"],
    [sys.executable, "build/google_workspace/build_complete_artifact_inventory.py"],
    ["uv", "run", "--with", "markdown", "--with", "beautifulsoup4", "python", "public-site/build_site.py"],
    ["uv", "run", "--with", "beautifulsoup4", "python", "public-site/verify_site.py"],
    [sys.executable, "build/google_workspace/qa_parity_manifest.py"],
    [sys.executable, "build/google_workspace/build_distribution_inventory.py"],
    [sys.executable, "build/google_workspace/qa_drive_distribution.py"],
    [sys.executable, "build/google_workspace/build_complete_artifact_inventory.py"],
    [sys.executable, "build/google_workspace/qa_complete_artifact_inventory.py"],
    [sys.executable, "build/google_workspace/qa_delivery_links.py"],
    [sys.executable, "build/google_workspace/qa_live_canvas_links.py", "--preflight"],
    ["uv", "run", "--with", "httpx", "python", "build/canvas/qa_remaining_unpublished.py", "--preflight"],
]


def main() -> None:
    for command in COMMANDS:
        subprocess.run(command, cwd=ROOT, check=True)
    print("CCE Google Workspace parity: PASS")


if __name__ == "__main__":
    main()
