#!/usr/bin/env python3
"""Publish one week's decks after the owner approves them.

Two halves, because Drive is reached through rclone on the owner's Mac and Canvas through the API:

  1) Drive (run on the Mac; needs the iisd-drive rclone remote):
       bash build/slides/publish_drive.sh 1sw-wk3 "SW1 · Wk3 Computer Science IT"
     uploads docs/resources/slides/<week>-dayN.pptx into the unit's Google Masters/ as Google Slides
     (rclone --drive-import-formats pptx) and the .pptx into Download Releases/, then writes
     build/slides/slides_registry.json with gslides_url / pptx_drive_url per day.

  2) Canvas (token on stdin):
       python3 build/slides/publish_week.py 1sw-wk3 --course 98060 --apply < ~/.canvas_token
     uploads each .pptx to Canvas Files under Slides/<week>/ (overwrite by name), records canvas_file_id
     in the registry, then runs apply_response_routes.py --apply --weeks <WEEK> so every facilitator
     guide's Student response routes panel carries a "Slides for Day N" row. Page bodies only; nothing
     is published or unpublished. Fleet courses get the same row through fleet_parity_apply.py.

  3) Public site: copies docs/resources/slides/public/<week>-dayN.pptx into public-site/static/slides/
     so build_site.py can link the rights-clean twin. Never the full deck.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import shutil
import subprocess
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
BASE = "https://learn.irvingisd.net"
REG = ROOT / "build/slides/slides_registry.json"


def load_reg():
    return json.load(open(REG)) if REG.exists() else {"days": {}}


def day_key(week: str, n: int):
    sw, wk = week.split("-")  # 1sw-wk3
    return f"{sw[0]}SW-Wk{wk[2:]}-Day{n}"


def upload(c, course, local: Path, folder_path: str):
    init = c.post(f"{BASE}/api/v1/courses/{course}/files", data={"name": local.name, "parent_folder_path": folder_path, "on_duplicate": "overwrite"}).json()
    r = c.post(init["upload_url"], data=init["upload_params"], files={"file": (local.name, local.read_bytes(), mimetypes.guess_type(local.name)[0] or "application/octet-stream")}, follow_redirects=True)
    r.raise_for_status()
    return r.json()["id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("week"); ap.add_argument("--course", type=int, default=98060); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    token = sys.stdin.readline().strip()
    reg = load_reg()
    decks = sorted((ROOT / "docs/resources/slides").glob(f"{a.week}-day*.pptx"))
    if not decks:
        sys.exit(f"no decks for {a.week}; run build_week.sh first")
    with httpx.Client(headers={"Authorization": f"Bearer {token}"}, timeout=180) as c:
        for deck in decks:
            n = int(deck.stem[-1]); key = day_key(a.week, n)
            entry = reg["days"].setdefault(key, {})
            if a.apply:
                entry["canvas_file_id"] = upload(c, a.course, deck, f"Slides/{a.week}")
            entry["pptx"] = str(deck.relative_to(ROOT))
            print(key, entry)
            pub = ROOT / "docs/resources/slides/public" / deck.name
            if pub.exists():
                dest = ROOT / "public-site/static/slides"; dest.mkdir(parents=True, exist_ok=True)
                shutil.copy2(pub, dest / deck.name)
    REG.write_text(json.dumps(reg, indent=1))
    if a.apply:
        sw, wk = a.week.split("-")
        subprocess.run([sys.executable, str(ROOT / "build/canvas/apply_response_routes.py"), "--apply", "--weeks", f"{sw[0]}SW-Wk{wk[2:]}"], input=token + "\n", text=True, check=True)
    else:
        print("dry run: registry updated locally, no Canvas writes. Add --apply after the owner approves the decks.")


if __name__ == "__main__":
    main()
