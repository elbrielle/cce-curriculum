#!/usr/bin/env python3
"""Render a student worksheet source (build/worksheet_sources/*.md) as
Google-Docs-import-friendly HTML.

Why this exists: the per-day student Google Docs were generated from the
exit-ticket template only, so every worksheet button on a Student Guide
opened the wrong document (see cce-curriculum/notes/audits/2026-09-14-*).
Each response-route worksheet now gets its own Google Doc built from the
same markdown that builds its PDF, so the PDF, the Doc, and (later) the
OneNote page stay one source.

Output conventions (chosen to survive the Drive HTML -> Google Doc import):
  [[lines: N]]  -> one-cell shaded table with N blank lines (typeable box)
  [[box: H]]    -> one-cell shaded table sized from H inches (~4 lines/in)
  [[pagebreak]] -> <p style="page-break-before:always">
  - [ ] item    -> ☐ item
  ______ runs   -> kept as text so the blank stays visible; a whole
                   underscore line becomes a one-line shaded box
  tables        -> bordered; empty cells get a non-breaking space so they
                   keep height and are clickable

Usage:
  python3 build/google_docs/render_worksheet_gdoc_html.py <slug> [...]
  python3 build/google_docs/render_worksheet_gdoc_html.py --all --out DIR
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

import markdown as md

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "build" / "worksheet_sources"
sys.path.insert(0, str(ROOT / "build"))
from build_worksheets import parse_front_matter, Sheet  # noqa: E402

LINES_MARKER = re.compile(r"\[\[\s*lines\s*:\s*(\d+)\s*\]\]", re.I)
BOX_MARKER = re.compile(r"\[\[\s*box\s*:\s*([0-9]*\.?[0-9]+)\s*(?:in|\")?\s*\]\]", re.I)
PAGEBREAK_MARKER = re.compile(r"\[\[\s*pagebreak\s*\]\]", re.I)
TASK_LINE = re.compile(r"^(\s*)[-*+]\s+\[([ xX])\]\s*(.*)$")
UNDERSCORE_LINE = re.compile(r"^\s*_{6,}\s*$")
TABLE_ROW = re.compile(r"^\s*\|")

SHADE = "#f1f3f4"
BORDER = "#9aa0a6"
CELL_STYLE = f"border:1px solid {BORDER};background:{SHADE};padding:6px 8px;vertical-align:top;"
TABLE_STYLE = "border-collapse:collapse;width:100%;margin:6px 0 10px 0;"


def response_box(lines: int, prompt: str | None = None) -> str:
    body = "<br>".join("&nbsp;" for _ in range(max(1, lines)))
    label = f"<p style='margin:0 0 4px 0;font-size:10pt;color:#5f6368'>{html.escape(prompt)}</p>" if prompt else ""
    return (
        f"{label}<table style='{TABLE_STYLE}'><tr><td style='{CELL_STYLE}'>{body}</td></tr></table>"
    )


def pre_markdown(body: str) -> str:
    out = []
    for raw in body.split("\n"):
        if PAGEBREAK_MARKER.fullmatch(raw.strip()):
            out.extend(["", "<p style=\"page-break-before:always\">&nbsp;</p>", ""])
            continue
        m = LINES_MARKER.fullmatch(raw.strip())
        if m:
            out.extend(["", response_box(int(m.group(1))), ""])
            continue
        m = BOX_MARKER.fullmatch(raw.strip())
        if m:
            out.extend(["", response_box(max(2, int(float(m.group(1)) * 4))), ""])
            continue
        if UNDERSCORE_LINE.match(raw):
            out.extend(["", response_box(1), ""])
            continue
        # inline markers sharing a line with prose: split them out
        if LINES_MARKER.search(raw) or BOX_MARKER.search(raw):
            def _sub(mm):
                return "\n\n" + response_box(int(mm.group(1))) + "\n\n"
            raw = LINES_MARKER.sub(_sub, raw)
            raw = BOX_MARKER.sub(lambda mm: "\n\n" + response_box(max(2, int(float(mm.group(1)) * 4))) + "\n\n", raw)
            out.append(raw)
            continue
        t = TASK_LINE.match(raw)
        if t:
            indent, state, text = t.groups()
            mark = "☑" if state.lower() == "x" else "☐"
            raw = f"{indent}- {mark} {text}"
        # protect inline blanks from markdown emphasis parsing
        raw = INLINE_BLANK.sub(lambda mm: BLANK_TOKEN * max(1, min(3, len(mm.group(0)) // 12)), raw)
        out.append(raw)
    return "\n".join(out)


INLINE_BLANK = re.compile(r"_{3,}")
BLANK_TOKEN = "⁣BLANK⁣"
BLANK_HTML = "<span style='background-color:#f1f3f4'>" + "&nbsp;" * 14 + "</span>"


def post_html(h: str) -> str:
    # bordered tables + keep empty cells tall
    h = h.replace("<table>", f"<table style='{TABLE_STYLE}'>")
    h = re.sub(r"<th>", f"<th style='border:1px solid {BORDER};padding:6px 8px;background:#e8eaed;text-align:left'>", h)
    h = re.sub(r"<td>", f"<td style='border:1px solid {BORDER};padding:6px 8px;vertical-align:top'>", h)
    h = re.sub(r"(<td[^>]*>)\s*(</td>)", r"\1&nbsp;<br>&nbsp;\2", h)
    h = re.sub(r"<h2>", "<h2 style='font-size:14pt'>", h)
    h = re.sub(r"<h3>", "<h3 style='font-size:12pt'>", h)
    h = h.replace(BLANK_TOKEN, BLANK_HTML)
    return h


def render(path: Path, day_label: str = "") -> tuple[Sheet, str]:
    sheet = Sheet(path)
    fm, body = parse_front_matter(path.read_text(encoding="utf-8"), sheet)
    title = fm.get("title", path.stem).strip()
    slug = fm.get("slug", path.stem).strip()
    sheet.title, sheet.slug = title, slug
    body_html = post_html(md.markdown(pre_markdown(body.strip("\n")), extensions=["tables"]))
    header = (
        f"<p style='font-size:16pt;font-weight:bold'>{html.escape(day_label + ': ' if day_label else '')}{html.escape(title)}</p>"
        "<p style='color:#5f6368'>Career and College Explorations · Student Worksheet</p>"
        f"<table style='{TABLE_STYLE}'><tr>"
        f"<td style='{CELL_STYLE}'><b>Name:</b>&nbsp;</td>"
        f"<td style='{CELL_STYLE}'><b>Class / Period:</b>&nbsp;</td>"
        f"<td style='{CELL_STYLE}'><b>Date:</b>&nbsp;</td></tr></table>"
        "<p style='font-size:10pt;color:#5f6368'>Type in the shaded boxes. Save this copy in your Drive; you may need it again on a later day. / Escribe en los cuadros sombreados. Guarda esta copia en tu Drive.</p>"
    )
    return sheet, f"<html><body style='font-family:Arial;font-size:11pt'>{header}{body_html}</body></html>"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default=str(ROOT / ".tmp" / "gdoc-html"))
    ap.add_argument("--label", default="")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    paths = sorted(SRC_DIR.glob("*.md")) if a.all else [SRC_DIR / f"{s}.md" for s in a.slugs]
    for p in paths:
        sheet, h = render(p, a.label)
        (out / f"{sheet.slug}.html").write_text(h, encoding="utf-8")
        print(sheet.slug, len(h))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
