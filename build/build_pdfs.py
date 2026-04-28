#!/usr/bin/env python3
"""
build_pdfs.py — Render printable exit-ticket PDFs from CCE day-file markdown.

Pipeline:
  1. Walk every docs/Nsw/wkN-topic/dayN.md
  2. Extract H1 (-> slug + subtitle) and the **EXIT TICKET** block
     (format name, payload body, TEKS codes)
  3. Map the format label to one of the ten canonical formats; render via
     the Jinja2 template at build/exit_ticket_template/template.html.j2
  4. Print to PDF via Playwright headless Chromium
  5. Output: docs/resources/exit-tickets/<Nsw>-wk<N>-day<N>-<slug>.pdf

The renderer ships structured layouts for the four "designed" formats
(MCQ, Matrix, Venn, Short Response) and a preserved-markdown fallback
for the other six (Concept Map, Decision Tree, Ranked, Mini-Case,
Trade-off, 3-2-1) until the design team finishes those layouts.

Usage:
  python3 build/build_pdfs.py                            # all
  python3 build/build_pdfs.py docs/2sw/wk2-*/day*.md     # subset (glob)
  python3 build/build_pdfs.py --dry-run                  # parse only
  python3 build/build_pdfs.py --html-only                # write HTML, skip PDF
"""

import argparse
import asyncio
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import markdown as md
from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.async_api import async_playwright


# ---------- Paths ----------

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
TEMPLATE_DIR = ROOT / "build" / "exit_ticket_template"
OUT_DIR = DOCS / "resources" / "exit-tickets"
RENDER_TMP = TEMPLATE_DIR / "_render.html"  # transient HTML file Playwright loads


# ---------- Format catalog ----------
# Prefix-match against the parenthetical in **EXIT TICKET** (Foo Bar):
# Order matters — longer/more-specific prefixes come first when ambiguous.

FORMATS = [
    # (prefix,                         id,               name,                          code,  half)
    ("Diagnostic MCQ",                 "mcq",            "Diagnostic MCQ",              "F01", True),
    ("Comparison Matrix",              "matrix",         "Comparison Matrix",           "F02", False),
    ("Venn Diagram",                   "venn",           "Venn Diagram",                "F03", False),
    ("Concept Map",                    "concept_map",    "Concept Map",                 "F04", False),
    ("Decision Tree",                  "decision_tree",  "Decision Tree",               "F05", False),
    ("Ranked Justification",           "ranked",         "Ranked Justification",        "F06", False),
    ("Mini-Case",                      "mini_case",      "Mini-Case",                   "F07", False),
    ("Trade-off",                      "tradeoff",       "Trade-off",                   "F08", False),
    ("Short Constructed Response",     "short_response", "Short Constructed Response",  "F09", True),
    ("3-2-1",                          "three_two_one",  "3-2-1 Reflective",            "F10", True),
]

DESIGNED = {"mcq", "matrix", "venn", "short_response"}


# ---------- Glyphs (24x24 viewBox, 1.5pt stroke, no fill) ----------
# The four "designed" glyphs come from the bundle's HTML mockups.
# The other six are placeholders authored to match the line-icon style;
# the design team will replace them when those formats ship.

GLYPHS = {
    "mcq":            '<svg viewBox="0 0 24 24"><circle cx="6" cy="7" r="2"/><circle cx="6" cy="17" r="2"/><path d="M11 7 H21"/><path d="M11 17 H21"/></svg>',
    "matrix":         '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18"/><path d="M3 9 H21"/><path d="M3 15 H21"/><path d="M9 3 V21"/><path d="M15 3 V21"/></svg>',
    "venn":           '<svg viewBox="0 0 24 24"><circle cx="9" cy="12" r="6"/><circle cx="15" cy="12" r="6"/></svg>',
    "short_response": '<svg viewBox="0 0 24 24"><path d="M4 7 H20"/><path d="M4 12 H20"/><path d="M4 17 H14"/></svg>',
    # placeholders below — replace when the design team ships the layouts
    "concept_map":    '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="2.2"/><circle cx="4" cy="5" r="1.4"/><circle cx="20" cy="5" r="1.4"/><circle cx="4" cy="19" r="1.4"/><circle cx="20" cy="19" r="1.4"/><path d="M12 12 L4.8 5.6"/><path d="M12 12 L19.2 5.6"/><path d="M12 12 L4.8 18.4"/><path d="M12 12 L19.2 18.4"/></svg>',
    "decision_tree":  '<svg viewBox="0 0 24 24"><circle cx="12" cy="5" r="1.5"/><circle cx="6" cy="13" r="1.5"/><circle cx="18" cy="13" r="1.5"/><circle cx="6" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M12 5 L6.7 12"/><path d="M12 5 L17.3 12"/><path d="M6 14.5 L6 18.5"/><path d="M18 14.5 L18 18.5"/></svg>',
    "ranked":         '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="3"/><rect x="3" y="11" width="13" height="3"/><rect x="3" y="17" width="8" height="3"/></svg>',
    "mini_case":      '<svg viewBox="0 0 24 24"><rect x="4" y="3" width="16" height="18"/><path d="M7 8 H17"/><path d="M7 12 H17"/><path d="M7 16 H13"/></svg>',
    "tradeoff":       '<svg viewBox="0 0 24 24"><path d="M12 3 V21"/><path d="M3 8 H9"/><path d="M5 6 L3 8 L5 10"/><path d="M21 16 H15"/><path d="M19 14 L21 16 L19 18"/></svg>',
    "three_two_one":  '<svg viewBox="0 0 24 24"><path d="M3 6 H21"/><path d="M3 9 H21"/><path d="M3 12 H21"/><path d="M3 15 H17"/><path d="M3 18 H17"/><path d="M3 21 H13"/></svg>',
    "fallback":       '<svg viewBox="0 0 24 24"><rect x="4" y="3" width="16" height="18"/><path d="M7 8 H17"/><path d="M7 12 H17"/><path d="M7 16 H13"/></svg>',
}


# ---------- Data classes ----------

@dataclass
class Ticket:
    block_num: str
    week_num: str
    day_num: str
    block_tile: str           # "2.2.2"
    page_id: str              # "2SW-Wk2-Day2"
    slug: str
    title: str
    subtitle: str
    format_id: str
    format_name: str
    format_code: str
    format_num: str           # "01 / 10"
    half_page: bool
    teks_codes: list = field(default_factory=list)
    teks_chip: str = ""
    payload: str = ""
    format_label_raw: str = ""
    source_path: Optional[Path] = None


# ---------- Parsers ----------

SLUG_BAD = re.compile(r"[^a-z0-9]+")

def slugify(text: str) -> str:
    text = text.lower()
    # collapse em/en dashes and ampersands first
    text = text.replace("&", " and ")
    text = SLUG_BAD.sub("-", text)
    return text.strip("-")


H1_RE = re.compile(r"^# Day (\d+):\s*(.+?)\s*$", re.MULTILINE)

# Match the EXIT TICKET marker through the end of its section.
# The section ends at the next `---` on its own line, the next `## ` heading,
# or the end of file.
EXIT_TICKET_RE = re.compile(
    r"^\*\*EXIT TICKET\*\*\s*\(([^)]+)\)"
    r"(?:\s*·\s*\[Printable PDF\]\([^)]+\))?"
    r":\s*\n+"
    r"(.*?)"
    r"(?=\n\n---\s*\n|\n## |\Z)",
    re.MULTILINE | re.DOTALL,
)

# Trailing TEKS chip: *(d(1)(C), d(4)(F))*  — possibly mid-paragraph
TEKS_CHIP_RE = re.compile(
    r"\*\(\s*(d\(\d+\)\([A-Z]\)(?:\s*,\s*d\(\d+\)\([A-Z]\))*)\s*\)\*"
)
TEKS_CODE_RE = re.compile(r"d\(\d+\)\([A-Z]\)")


def map_format(label: str):
    norm = label.strip().lower()
    for prefix, fid, fname, fcode, half in FORMATS:
        if norm.startswith(prefix.lower()):
            return fid, fname, fcode, half
    return "fallback", label.strip(), "F00", False


def parse_day_file(path: Path) -> Optional[Ticket]:
    raw = path.read_text(encoding="utf-8")

    h1 = H1_RE.search(raw)
    if not h1:
        return None
    day_num, title = h1.group(1), h1.group(2).strip()

    rel_parts = path.relative_to(DOCS).parts
    block_match = re.match(r"(\d+)sw", rel_parts[0])
    week_match = re.match(r"wk(\d+)", rel_parts[1])
    if not block_match or not week_match:
        return None
    block_num, week_num = block_match.group(1), week_match.group(1)

    et = EXIT_TICKET_RE.search(raw)
    if not et:
        return None
    format_label_raw = et.group(1).strip()
    payload_raw = et.group(2).strip()

    fid, fname, fcode, half = map_format(format_label_raw)

    # Extract TEKS chip — take the last one if multiple appear
    chips = TEKS_CHIP_RE.findall(payload_raw)
    teks_codes = TEKS_CODE_RE.findall(chips[-1]) if chips else []
    teks_chip = " · ".join(teks_codes)

    # Strip ALL TEKS chips from payload (they're metadata, not student-facing prose)
    payload_clean = TEKS_CHIP_RE.sub("", payload_raw).strip()
    # Collapse blank lines that appear from removed chips
    payload_clean = re.sub(r"\n{3,}", "\n\n", payload_clean)

    slug = slugify(title)

    return Ticket(
        block_num=block_num,
        week_num=week_num,
        day_num=day_num,
        block_tile=f"{block_num}.{week_num}.{day_num}",
        page_id=f"{block_num}SW-Wk{week_num}-Day{day_num}",
        slug=slug,
        title=title,
        subtitle=title,
        format_id=fid,
        format_name=fname,
        format_code=fcode,
        format_num=f"{fcode[1:]} / 10" if fcode != "F00" else "00 / 10",
        half_page=half,
        teks_codes=teks_codes,
        teks_chip=teks_chip,
        payload=payload_clean,
        format_label_raw=format_label_raw,
        source_path=path,
    )


# ---------- Per-format payload extractors ----------

MCQ_OPT_RE = re.compile(r"^\s*[-*]\s*([A-D])\.\s+(.+?)\s*$", re.MULTILINE)


def extract_mcq(payload: str) -> dict:
    """Pull A/B/C/D options + scenario + stem from MCQ payload."""
    options = [
        {"letter": m.group(1), "text": m.group(2)}
        for m in MCQ_OPT_RE.finditer(payload)
    ]
    if not options:
        return {}

    # Everything before the first MCQ option line is scenario + stem
    first_opt_pos = MCQ_OPT_RE.search(payload).start()
    head = payload[:first_opt_pos].strip()
    # Tail (anything after the last option) becomes a callout if present
    last_opt = list(MCQ_OPT_RE.finditer(payload))[-1]
    tail = payload[last_opt.end():].strip()

    # Split head into scenario (first paragraph) and stem (last paragraph,
    # usually the bolded "Question?" line)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", head) if p.strip()]
    scenario, stem = "", ""
    if len(paragraphs) >= 2:
        scenario = paragraphs[0]
        stem = paragraphs[-1]
    elif paragraphs:
        stem = paragraphs[0]

    # Strip leading/trailing **bold** markdown from the stem (template re-bolds)
    stem = re.sub(r"^\*\*(.+?)\*\*$", r"\1", stem.strip())

    callout = ""
    if tail:
        # Take the first line of the tail as the callout if it's short.
        first_line = tail.splitlines()[0].strip()
        if first_line and len(first_line) < 200:
            callout = first_line

    return {
        "scenario": scenario,
        "stem": stem,
        "options": options,
        "callout": callout,
    }


MD_TABLE_RE = re.compile(
    r"^\|(.+?)\|\s*\n\|(?:\s*[-:]+\s*\|)+\s*\n((?:\|.+?\|\s*\n)+)",
    re.MULTILINE,
)


def extract_matrix(payload: str) -> dict:
    """Detect a markdown table and return columns + row labels.
    Returns {} if no table is found (caller falls back)."""
    m = MD_TABLE_RE.search(payload)
    if not m:
        return {}

    header_row = [c.strip() for c in m.group(1).split("|")]
    header_row = [c for c in header_row if c is not None]
    if not header_row:
        return {}
    # First column is the row-label column header (often blank)
    columns = [c for c in header_row[1:] if c.strip()]
    if not columns:
        return {}

    rows = []
    for line in m.group(2).splitlines():
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells:
            continue
        label = cells[0]
        if not label:
            continue
        # Treat <br> or two-line label as label + sublabel
        sub = ""
        if "<br>" in label:
            label, sub = [p.strip() for p in label.split("<br>", 1)]
        rows.append({"label": label, "sublabel": sub, "cells": cells[1:]})

    if not rows:
        return {}

    # Stem = the prose immediately before the table (first paragraph)
    pre = payload[: m.start()].strip()
    stem_paragraphs = [p.strip() for p in re.split(r"\n\s*\n", pre) if p.strip()]
    stem = stem_paragraphs[-1] if stem_paragraphs else ""
    stem = re.sub(r"^\*\*(.+?)\*\*$", r"\1", stem.strip())

    # Callout = first line of prose after the table, if any
    post = payload[m.end():].strip()
    callout = ""
    if post:
        first = post.splitlines()[0].strip()
        if first and len(first) < 200 and not first.startswith("|"):
            callout = first.lstrip("*").strip()

    return {
        "stem": stem,
        "columns": columns,
        "rows": rows,
        "callout": callout,
    }


VS_RE = re.compile(r"\b([A-Z][A-Za-z& -]+?)\s+(?:vs?\.?|or)\s+([A-Z][A-Za-z& -]+?)\b")


def extract_venn(ticket: "Ticket") -> dict:
    """Extract two labels from the title (e.g., 'Detective vs Lawyer').
    Falls back to {} if no clean two-item pair is found — caller renders
    the markdown fallback."""
    # First try title
    for source in (ticket.title, ticket.payload[:300]):
        m = VS_RE.search(source)
        if m:
            left = m.group(1).strip().rstrip(",").strip()
            right = m.group(2).strip().rstrip(",").strip()
            if left and right and len(left) < 30 and len(right) < 30:
                return {
                    "left_label": left,
                    "right_label": right,
                    "stem": _first_paragraph(ticket.payload),
                    "callout": _last_short_line(ticket.payload),
                }
    return {}


def extract_short_response(payload: str) -> dict:
    """Stem only — the body is just a lined writing area."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", payload) if p.strip()]
    if not paragraphs:
        return {"stem": ""}
    # Use the first 1-2 paragraphs as the stem; render through markdown so
    # **bold** and inline emphasis carry through.
    head = "\n\n".join(paragraphs[:2])
    stem_html = md.markdown(head, extensions=["extra"])
    # strip surrounding <p> if there's only one paragraph
    return {"stem": stem_html}


def _first_paragraph(payload: str) -> str:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", payload) if p.strip()]
    return paragraphs[0] if paragraphs else ""


def _last_short_line(payload: str) -> str:
    for line in reversed(payload.splitlines()):
        line = line.strip().lstrip("*").strip()
        if line and len(line) < 200:
            return line
    return ""


# ---------- Markdown -> HTML for fallback ----------

UNDERSCORE_LINE = re.compile(r"^\s*_{6,}\s*$")
INLINE_UNDERSCORES = re.compile(r"_{6,}")


def render_fallback_html(payload: str) -> str:
    """Render preserved markdown to HTML for the fallback body.

    Two distinct underscore patterns appear in the corpus and need different
    treatments:

    - "Underscore-only line" — a paragraph that's just a long run of
      underscores (sometimes with leading whitespace from indented authoring).
      These represent a full-width writing slot. Convert to a gold-tinted
      .fb-line block (~9mm tall, matching the design system's answer-region
      treatment).

    - "Inline underscore run" — a label followed by underscores ("Label: ___")
      mid-paragraph. These represent a fill-in slot inline with text. Convert
      to a gold-tinted .fb-blank inline-block (~2in wide).
    """
    out_lines = []
    for line in payload.splitlines():
        if UNDERSCORE_LINE.match(line):
            # Wrap in blank lines so python-markdown treats it as a raw
            # HTML block and passes it through.
            out_lines.append("")
            out_lines.append('<div class="fb-line"></div>')
            out_lines.append("")
        else:
            line = INLINE_UNDERSCORES.sub('<span class="fb-blank"></span>', line)
            out_lines.append(line)

    return md.markdown(
        "\n".join(out_lines),
        extensions=["extra", "tables", "sane_lists"],
    )


# ---------- Renderer ----------

def build_jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=False,
        lstrip_blocks=False,
    )


def ticket_to_context(ticket: Ticket) -> dict:
    ctx = {
        "block_tile": ticket.block_tile,
        "page_id": ticket.page_id,
        "subtitle": ticket.subtitle,
        "format_id": ticket.format_id,
        "format_name": ticket.format_name,
        "format_code": ticket.format_code,
        "format_num": ticket.format_num,
        "half_page": ticket.half_page,
        "teks_chip": ticket.teks_chip,
        "glyph_svg": GLYPHS.get(ticket.format_id, GLYPHS["fallback"]),
        "mcq": {},
        "matrix": {},
        "venn": {},
        "short_response": {},
        "fallback_html": "",
    }

    fid = ticket.format_id
    if fid == "mcq":
        ctx["mcq"] = extract_mcq(ticket.payload)
        if not ctx["mcq"]:  # parser couldn't find options
            ctx["fallback_html"] = render_fallback_html(ticket.payload)
            ctx["format_id"] = "fallback"
    elif fid == "matrix":
        ctx["matrix"] = extract_matrix(ticket.payload)
        if not ctx["matrix"]:
            ctx["fallback_html"] = render_fallback_html(ticket.payload)
            ctx["format_id"] = "fallback"
    elif fid == "venn":
        ctx["venn"] = extract_venn(ticket)
        if not ctx["venn"]:
            ctx["fallback_html"] = render_fallback_html(ticket.payload)
            ctx["format_id"] = "fallback"
    elif fid == "short_response":
        ctx["short_response"] = extract_short_response(ticket.payload)
    else:
        # The six fallback formats + any unknown format
        ctx["fallback_html"] = render_fallback_html(ticket.payload)

    return ctx


def render_html_for(ticket: Ticket, env: Environment) -> str:
    template = env.get_template("template.html.j2")
    return template.render(**ticket_to_context(ticket))


# ---------- Playwright PDF driver ----------

async def render_pdfs(tickets: list, html_only: bool = False) -> list:
    """Render every ticket. Returns list of (ticket, output_path) pairs."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    env = build_jinja_env()
    results = []

    if html_only:
        for t in tickets:
            html = render_html_for(t, env)
            out = OUT_DIR / f"{t.page_id.lower().replace('-', '-')}-{t.slug}.html"
            # Normalise to '<Nsw>-wk<N>-day<N>-<slug>.html'
            out = OUT_DIR / f"{t.block_num}sw-wk{t.week_num}-day{t.day_num}-{t.slug}.html"
            out.write_text(html, encoding="utf-8")
            results.append((t, out))
        return results

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        for t in tickets:
            html = render_html_for(t, env)
            RENDER_TMP.write_text(html, encoding="utf-8")
            await page.goto(f"file://{RENDER_TMP}")
            # Wait for fonts and images
            await page.wait_for_load_state("networkidle")
            try:
                await page.evaluate("document.fonts.ready")
            except Exception:
                pass
            out = OUT_DIR / f"{t.block_num}sw-wk{t.week_num}-day{t.day_num}-{t.slug}.pdf"
            await page.pdf(
                path=str(out),
                format="Letter",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                prefer_css_page_size=True,
            )
            results.append((t, out))
        await context.close()
        await browser.close()

    # Clean up the transient render file
    if RENDER_TMP.exists():
        RENDER_TMP.unlink()

    return results


# ---------- Driver ----------

def collect_day_files(globs: list) -> list:
    if not globs:
        return sorted(DOCS.glob("*sw/wk*-*/day*.md"))
    paths = []
    for g in globs:
        if Path(g).is_absolute():
            paths.extend(Path("/").glob(g.lstrip("/")))
        else:
            paths.extend(ROOT.glob(g))
    # Dedupe + sort
    return sorted(set(paths))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Optional day-file globs")
    parser.add_argument("--dry-run", action="store_true", help="Parse only; no PDFs")
    parser.add_argument("--html-only", action="store_true", help="Write HTML next to PDFs; skip PDF render")
    parser.add_argument("--clean", action="store_true", help="Delete OUT_DIR before generating")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-ticket logging")
    args = parser.parse_args(argv)

    files = collect_day_files(args.paths)
    if not files:
        print("No day files matched.", file=sys.stderr)
        return 1

    tickets = []
    skipped = []
    for p in files:
        t = parse_day_file(p)
        if t is None:
            skipped.append(p)
        else:
            tickets.append(t)

    if not args.quiet:
        print(f"Parsed {len(tickets)} tickets; skipped {len(skipped)} files without an EXIT TICKET marker:")
        for s in skipped:
            print(f"  SKIP {s.relative_to(ROOT)}")

    # Format coverage summary
    if not args.quiet:
        from collections import Counter
        counts = Counter(t.format_id for t in tickets)
        print("\nFormat coverage:")
        for fid, n in sorted(counts.items(), key=lambda kv: -kv[1]):
            structured = "structured" if fid in DESIGNED else "fallback"
            print(f"  {fid:18s} {n:3d}  ({structured})")
        print()

    if args.dry_run:
        return 0

    if args.clean and OUT_DIR.exists():
        for f in OUT_DIR.glob("*.pdf"):
            f.unlink()
        for f in OUT_DIR.glob("*.html"):
            f.unlink()

    if args.html_only:
        results = asyncio.run(render_pdfs(tickets, html_only=True))
    else:
        results = asyncio.run(render_pdfs(tickets, html_only=False))

    if not args.quiet:
        print(f"\nWrote {len(results)} files to {OUT_DIR.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
