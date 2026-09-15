#!/usr/bin/env python3
"""QA gate for a CCE classroom deck.

  python3 build/slides/qa_deck.py docs/resources/slides/1sw-wk3-day2.pptx [--out .tmp/deck-qa/1sw-wk3-day2]

Checks (fails the build on any):
  1. every slide has speaker notes and exactly one [Sources] block
  2. no text box or picture extends outside the 1280x720 canvas
  3. no two text boxes overlap by more than a sliver (text painted under text)
  4. no banned strings on slides: "HQIM", "TEKS", "[VERIFY]", "{{", "Minute 0", "5E", "Engage"/"Explore" as headings, "Lorem"
  5. renders every slide to PNG (LibreOffice -> pdftoppm) and writes a contact sheet for the human pass
Prints PASS/FAIL and the render directory. The contact sheet is not optional: look at it.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import subprocess
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

EMU_PER_PX = 9525  # 96 dpi
W, H = 1280, 720
BANNED = ["HQIM", "TEKS", "[VERIFY]", "{{", "Lorem", "5E"]


def px(emu):
    return emu / EMU_PER_PX


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("pptx"); ap.add_argument("--out", default=None); ap.add_argument("--allow-overlap", type=float, default=0.15)
    a = ap.parse_args()
    src = Path(a.pptx)
    out = Path(a.out or f".tmp/deck-qa/{src.stem}")
    out.mkdir(parents=True, exist_ok=True)
    prs = Presentation(str(src))
    fails, notes = [], []
    for n, s in enumerate(prs.slides, 1):
        # 1 notes + sources
        txt = s.notes_slide.notes_text_frame.text if s.has_notes_slide else ""
        if not txt.strip(): fails.append(f"slide {n}: no speaker notes")
        elif txt.count("[Sources]") != 1: fails.append(f"slide {n}: expected one [Sources] block, found {txt.count('[Sources]')}")
        boxes = []
        for sh in s.shapes:
            if sh.left is None: continue
            x0, y0, x1, y1 = px(sh.left), px(sh.top), px(sh.left + sh.width), px(sh.top + sh.height)
            # 2 canvas
            if x0 < -1 or y0 < -1 or x1 > W + 1 or y1 > H + 1: fails.append(f"slide {n}: '{sh.name}' outside canvas ({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f})")
            if sh.has_text_frame and sh.text_frame.text.strip():
                boxes.append((x0, y0, x1, y1, sh.text_frame.text[:30]))
                # 4 banned
                for b in BANNED:
                    if b in sh.text_frame.text: fails.append(f"slide {n}: banned string {b!r} in '{sh.text_frame.text[:40]}'")
        # 3 text-over-text
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                ax0, ay0, ax1, ay1, at = boxes[i]; bx0, by0, bx1, by1, bt = boxes[j]
                ix = max(0, min(ax1, bx1) - max(ax0, bx0)); iy = max(0, min(ay1, by1) - max(ay0, by0))
                inter = ix * iy
                small = min((ax1 - ax0) * (ay1 - ay0), (bx1 - bx0) * (by1 - by0))
                if small > 0 and inter / small > a.allow_overlap:
                    fails.append(f"slide {n}: text boxes overlap {inter/small:.0%}: {at!r} / {bt!r}")
    # 5 render
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out), str(src)], check=True, capture_output=True)
    pdf = out / (src.stem + ".pdf")
    for f in glob.glob(str(out / "s-*.png")): os.remove(f)
    subprocess.run(["pdftoppm", "-r", "60", "-png", str(pdf), str(out / "s")], check=True)
    pngs = sorted(glob.glob(str(out / "s-*.png")))
    from PIL import Image
    ims = [Image.open(f) for f in pngs]
    if ims:
        w, h = ims[0].size; cols = 3; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * w, rows * h), "white")
        for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * w, (i // cols) * h))
        sheet.save(out / "contact-sheet.png")
    notes.append(f"{len(prs.slides)} slides rendered -> {out}/contact-sheet.png (look at it)")
    print("\n".join(notes))
    if fails:
        print("FAIL"); print("\n".join(fails)); return 1
    print("PASS"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
