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

DESIGNED = {
    "mcq", "matrix", "venn", "short_response",            # Round 1
    "concept_map", "decision_tree", "ranked",             # Round 2
    "mini_case", "tradeoff", "three_two_one",
}


# ---------- Glyphs (24x24 viewBox, 1.5pt stroke, no fill) ----------
# The four "designed" glyphs come from the bundle's HTML mockups.
# The other six are placeholders authored to match the line-icon style;
# the design team will replace them when those formats ship.

GLYPHS = {
    # Round 1 (design team)
    "mcq":            '<svg viewBox="0 0 24 24"><circle cx="6" cy="7" r="2"/><circle cx="6" cy="17" r="2"/><path d="M11 7 H21"/><path d="M11 17 H21"/></svg>',
    "matrix":         '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18"/><path d="M3 9 H21"/><path d="M3 15 H21"/><path d="M9 3 V21"/><path d="M15 3 V21"/></svg>',
    "venn":           '<svg viewBox="0 0 24 24"><circle cx="9" cy="12" r="6"/><circle cx="15" cy="12" r="6"/></svg>',
    "short_response": '<svg viewBox="0 0 24 24"><path d="M4 7 H20"/><path d="M4 12 H20"/><path d="M4 17 H14"/></svg>',
    # Round 2 (design team)
    "concept_map":    '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="2.6" fill="currentColor"/><circle cx="4" cy="5" r="1.8"/><circle cx="20" cy="5" r="1.8"/><circle cx="4" cy="19" r="1.8"/><circle cx="20" cy="19" r="1.8"/><path d="M10 11 L5.4 6.2 M14 11 L18.6 6.2 M10 13 L5.4 17.8 M14 13 L18.6 17.8"/></svg>',
    "decision_tree":  '<svg viewBox="0 0 24 24"><circle cx="12" cy="4" r="1.8"/><circle cx="6" cy="12" r="1.8"/><circle cx="18" cy="12" r="1.8"/><circle cx="3" cy="20" r="1.6"/><circle cx="9" cy="20" r="1.6"/><circle cx="15" cy="20" r="1.6"/><circle cx="21" cy="20" r="1.6"/><path d="M11 5.4 L7 10.6 M13 5.4 L17 10.6 M5 13.4 L3.5 18.4 M7 13.4 L8.5 18.4 M17 13.4 L15.5 18.4 M19 13.4 L20.5 18.4"/></svg>',
    "ranked":         '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="3" fill="currentColor" stroke="none"/><rect x="3" y="11" width="13" height="3" fill="currentColor" stroke="none"/><rect x="3" y="17" width="8" height="3" fill="currentColor" stroke="none"/></svg>',
    "mini_case":      '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16"/><path d="M6 9 H18 M6 13 H18 M6 17 H14"/></svg>',
    "tradeoff":       '<svg viewBox="0 0 24 24"><path d="M12 3 V21"/><path d="M3 9 H10 M10 9 L7 6 M10 9 L7 12"/><path d="M21 15 H14 M14 15 L17 12 M14 15 L17 18"/></svg>',
    "three_two_one":  '<svg viewBox="0 0 24 24"><path d="M3 6 H21"/><path d="M3 12 H17"/><path d="M3 18 H11"/></svg>',
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


def _strip_underscore_runs(text: str) -> str:
    """Replace inline underscore runs with empty so they don't appear inside
    structured prompt text (the gold slot below carries the writing space)."""
    return re.sub(r"_{4,}", "", text).strip()


def _strip_md_bold(text: str) -> str:
    """Drop **...** wrappers; keep inner text. Used for labels/prompts that
    will be re-bolded by the template."""
    return re.sub(r"\*\*(.+?)\*\*", r"\1", text)


# ---------- F04 Concept Map ----------

# Match a heading line "**N. label**" then capture anything following on the
# same line (trailing text and/or a parenthetical descriptor) as the
# "descriptor" tail. Body is captured until the next **N. heading or EOF.
CMAP_NODE_RE = re.compile(
    r"^\*\*(\d+)\.\s+(.+?)\*\*\s*(.*?)$\s*(.*?)(?=\n\*\*\d+\.\s|\Z)",
    re.DOTALL | re.MULTILINE,
)


def extract_concept_map(payload: str) -> dict:
    """Pattern: center prompt + 'Connect ... N things:' intro + **N. Label**
    numbered sections.  Each section has a label, a description, and one or
    more inline fill-ins for the slot + why prompt.

    Returns {} if fewer than 2 numbered sections are found, so unusual
    concept-map markdown (e.g., 6sw/wk6/day4 which uses a center 'Place X in
    the center' instruction with non-bold numbered items) falls back."""
    nodes = list(CMAP_NODE_RE.finditer(payload))
    if len(nodes) < 2:
        return {}

    # Center prompt = first paragraph before the numbered sections, stripped
    # of the underscore fill-in run.
    pre = payload[: nodes[0].start()].strip()
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", pre) if p.strip()]
    center_prompt = ""
    if paragraphs:
        center_prompt = _strip_underscore_runs(paragraphs[0])
    intro = ""
    if len(paragraphs) >= 2:
        intro = _strip_md_bold(_strip_underscore_runs(paragraphs[1]))

    extracted = []
    for m in nodes:
        num = m.group(1)
        label = _strip_underscore_runs(m.group(2))
        # Trailing text on the heading line is the descriptor (may include a
        # parenthetical like "(from Day 2 matrix)" — preserve it intact, but
        # strip surrounding whitespace).
        descriptor_raw = (m.group(3) or "").strip()
        # Strip surrounding parens if the entire trail is a parenthetical
        if descriptor_raw.startswith("(") and descriptor_raw.endswith(")"):
            descriptor = descriptor_raw[1:-1].strip()
        else:
            descriptor = descriptor_raw
        body = m.group(4).strip()

        # Body is typically two paragraphs: "My X: ___. Why...?" and a
        # standalone underscore line (the "why" slot). Split.
        body_paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        # First paragraph carries the slot prompt + why prompt; second is the
        # underscore-only why slot.
        prompt_text = ""
        why_prompt = ""
        if body_paragraphs:
            first = body_paragraphs[0]
            # Split on the period that ends the slot label, if any
            split = re.split(r"\.\s+(?=Why|One sentence|In one sentence|How|What|Where|When)", first, maxsplit=1)
            if len(split) == 2:
                prompt_text = _strip_underscore_runs(split[0]).rstrip(".")
                why_prompt = _strip_underscore_runs(split[1]).rstrip(":")
            else:
                prompt_text = _strip_underscore_runs(first).rstrip(".")

        extracted.append({
            "num": num,
            "label": label,
            "descriptor": descriptor,
            "prompt": prompt_text,
            "why_prompt": why_prompt,
        })

    return {
        "center_prompt": center_prompt.rstrip(":"),
        "intro": intro,
        "nodes": extracted,
    }


# ---------- F05 Decision Tree ----------

DT_ROLE_RE = re.compile(r"^My\s+([A-Z][^\n:]{1,60}?)\s+role\s*[:.]?\s*(.+?)\s*$", re.MULTILINE)
DT_PROBLEM_RE = re.compile(r"^Problem:\s*(.+?)(?=\n\n|\nStep\s|\Z)", re.DOTALL | re.MULTILINE)
DT_STEP_RE = re.compile(
    r"^Step\s+(\d+):\s*(.+?)(?=\nStep\s+\d+:|\Z)",
    re.DOTALL | re.MULTILINE,
)


def extract_decision_tree(payload: str) -> dict:
    """Pattern: optional role bar + optional Problem: + 'Step N: prompt'
    sections, where Step 2 may carry an 'I need to talk to / Because' branch.

    Returns {} for the rare ticket whose markdown uses **Step 1:** with
    YES/NO bullet branches (e.g., 6sw/wk5/day3), which falls back."""
    if "**Step" in payload:
        # Different shape — fall back
        return {}

    steps_iter = list(DT_STEP_RE.finditer(payload))
    if len(steps_iter) < 2:
        return {}

    # Role bar
    role_label, role_descriptor = "", ""
    rm = DT_ROLE_RE.search(payload[: steps_iter[0].start()])
    if rm:
        role_label = rm.group(1).strip()
        role_descriptor = rm.group(2).strip()
        # The descriptor often has the underscore + parenthetical descriptor
        # combined: "______ (Shift Supervisor / ...)"
        descriptor_match = re.search(r"\((.+?)\)", role_descriptor)
        role_descriptor = descriptor_match.group(1).strip() if descriptor_match else ""

    # Problem
    pm = DT_PROBLEM_RE.search(payload)
    problem = pm.group(1).strip() if pm else ""
    problem = _strip_underscore_runs(problem)

    # Steps
    steps = []
    for m in steps_iter:
        num = m.group(1)
        body = m.group(2).strip()
        # Split the prompt from the slot/branch.
        # Detect IF/IF or "I need to talk to / Because" two-column pattern.
        branch = None
        # Look for the "I need to talk to:" + "Because:" pattern
        talk_m = re.search(r"I need to talk to:\s*([^\n]*)", body)
        because_m = re.search(r"Because:\s*([^\n]*)", body, re.IGNORECASE)
        if talk_m and because_m:
            # Strip these out of the prompt
            prompt_text = body[:talk_m.start()].strip()
            branch = {
                "left_label": "I need to talk to",
                "right_label": "Because",
            }
        else:
            prompt_text = body

        # The prompt text often ends with "(One sentence:)" or "?"; clean it.
        # Also strip trailing underscore lines.
        prompt_text = re.sub(r"_{4,}", "", prompt_text).strip()
        # Remove trailing ":" if any.
        prompt_text = prompt_text.rstrip(":").strip()

        steps.append({
            "num": num,
            "prompt": prompt_text,
            "branch": branch,
            "slot_lines": 4 if not branch else 3,
        })

    return {
        "role_label": role_label.upper() if role_label else "",
        "role_descriptor": role_descriptor,
        "problem": problem,
        "steps": steps,
    }


# ---------- F06 Ranked Justification ----------

RANKED_ITEM_RE = re.compile(r"^\s*[-*]\s+(.+?)(?::\s*rank\s+_+|:?\s*$)", re.MULTILINE)
RANKED_FOLLOW_RE = re.compile(r"^\s*[-*]\s+Rank\s+(\d+)(?:\s*\(([^)]+)\))?:\s*(.*?)$", re.MULTILINE)


def extract_ranked(payload: str) -> dict:
    """Pattern: stem + bullet list of items + optional rule strip + follow-up
    'Rank N:' rows.

    Returns {} if the bullet list isn't clean (e.g., 4sw/wk4/day2 has a
    different multi-question shape)."""
    # Stem is the first paragraph
    stem_para = _first_paragraph(payload)
    stem = _strip_md_bold(stem_para)

    # Items: bullet list before the "For each rank" or follow-up section
    items = []
    follow_split = re.search(r"^\s*For\s+(?:each|my|the)\s+", payload, re.MULTILINE | re.IGNORECASE)
    list_section = payload[len(stem_para):follow_split.start()] if follow_split else payload[len(stem_para):]

    for m in RANKED_ITEM_RE.finditer(list_section):
        item_text = _strip_underscore_runs(m.group(1)).rstrip(":").strip()
        # Skip if this is a "Rank N" follow-up row, not an item
        if re.match(r"Rank\s+\d+", item_text, re.IGNORECASE):
            continue
        if item_text:
            items.append(item_text)

    if not (3 <= len(items) <= 5):
        return {}

    # Optional rule strip — look for parenthetical list of rules in the stem
    # or a short callout line just before the follow-up.
    rule_strip = ""
    rule_strip_label = ""
    callout_text = ""
    if follow_split:
        between = payload[follow_split.start():]
        callout_m = re.search(r"For\s+each\s+(?:rank|item)[^.\n]*?\(([^)]+)\)", payload, re.IGNORECASE)
        if callout_m:
            rule_strip = callout_m.group(1).strip()
            rule_strip_label = "Rules"
        callout_match = re.search(r"For\s+(?:each|my|the)\s+[^\n:]+:?\s*$", payload, re.MULTILINE | re.IGNORECASE)
        if callout_match:
            callout_text = callout_match.group(0).strip().rstrip(":")

    follows = []
    for fm in RANKED_FOLLOW_RE.finditer(payload):
        rank_num = fm.group(1)
        qual = fm.group(2) or ""
        label = f"Rank {rank_num}" + (f" ({qual.strip()})" if qual else "")
        follows.append({"label": label.upper()})

    if not follows:
        # Without follow-up rows the structured render is incomplete
        return {}

    return {
        "stem": stem.strip(),
        "items_list": items,
        "rule_strip": rule_strip,
        "rule_strip_label": rule_strip_label,
        "callout": callout_text or "FOR EACH RANK, NAME ONE RULE THAT SUPPORTS YOUR CHOICE:",
        "follows": follows,
    }


# ---------- F07 Mini-Case ----------

MINI_QUESTION_RE = re.compile(r"^\s*(\d+)\.\s+(.+?)(?=\n\s*\d+\.\s|\Z)", re.DOTALL | re.MULTILINE)
STEP_PAIR_RE = re.compile(r"^\s*[-*]\s*Step\s+(\d+):\s*(.+?)$", re.MULTILINE)


def extract_mini_case(payload: str) -> dict:
    """Pattern: 'Scenario:' block + numbered questions, some with 'Step 1/2'
    sub-bullets."""
    sm = re.search(r"^Scenario:\s*(.+?)(?=\n\s*\d+\.\s|\n\s*\n|\Z)",
                   payload, re.DOTALL | re.MULTILINE)
    if not sm:
        # Some Mini-Case variants don't use the literal "Scenario:" prefix
        # but still have a paragraph then numbered questions.
        first = _first_paragraph(payload)
        if not first or not re.search(r"^\s*1\.\s", payload, re.MULTILINE):
            return {}
        scenario = first
        rest_start = len(first)
    else:
        scenario = sm.group(1).strip()
        rest_start = sm.end()

    # Strip leading "Scenario:" if doubled
    scenario = re.sub(r"^Scenario:\s*", "", scenario, flags=re.IGNORECASE).strip()
    scenario = _strip_md_bold(_strip_underscore_runs(scenario))

    body = payload[rest_start:]
    questions = []
    for qm in MINI_QUESTION_RE.finditer(body):
        num = qm.group(1)
        text = qm.group(2).strip()

        # Detect step pair: "- Step 1: ..." / "- Step 2: ..."
        steps = list(STEP_PAIR_RE.finditer(text))
        if len(steps) == 2:
            # Prompt is everything before the first Step row
            prompt = text[: steps[0].start()].strip()
            prompt = _strip_underscore_runs(prompt)
            questions.append({
                "num": num,
                "prompt": prompt,
                "step_pair": [
                    {"label": f"Step {steps[0].group(1)}", "slot_lines": 2},
                    {"label": f"Step {steps[1].group(1)}", "slot_lines": 2},
                ],
                "slot_lines": 0,
            })
        else:
            prompt = _strip_underscore_runs(text).strip()
            # Append a question mark only if the prompt has no terminal
            # punctuation already.
            if prompt and prompt[-1] not in "?.:!":
                prompt += "?"
            # Heuristic: longer prompts get more lines
            slot_lines = 3 if len(prompt) > 90 else 2
            questions.append({
                "num": num,
                "prompt": prompt,
                "step_pair": None,
                "slot_lines": slot_lines,
            })

    if len(questions) < 2:
        return {}

    return {
        "scenario": scenario,
        "questions": questions,
    }


# ---------- F08 Trade-off ----------

# Two markdown shapes in the corpus:
#   `- **(A) Look it up.** Pros: helps a coworker, ...`   (label inside bold)
#   `- **(A)** A senior living home with 80 ...`          (label outside bold)
TRADEOFF_OPT_RE = re.compile(
    r"^[-*]\s*\*\*\(([AB])\)(?:\s*([^*]*?))?\.?\*\*\s*(.+?)$",
    re.MULTILINE,
)


def extract_tradeoff(payload: str) -> dict:
    """Pattern: scenario + bold (A)/(B) options + Pros A/B slots +
    My choice + Quality list + justify."""
    opts = list(TRADEOFF_OPT_RE.finditer(payload))
    if len(opts) != 2:
        return {}

    scenario_text = payload[: opts[0].start()].strip()
    scenario = _strip_underscore_runs(scenario_text)
    # Drop trailing bullets carry-over
    scenario = re.sub(r"\n\s*[-*].*$", "", scenario, flags=re.DOTALL).strip()

    def _split_label_and_pros(inner_label: str, after_bold: str):
        """Combine the label-inside-bold and the rest-of-line text into a
        single (label, pros) pair. The 'pros' text often starts with 'Pros:'.
        If no inner label, the rest-of-line up to the first 'Pros:' is the
        label, and the remainder is the pros."""
        inner = (inner_label or "").strip().rstrip(".")
        rest = after_bold.strip()
        # Split rest on "Pros:" if present
        pros_split = re.split(r"\bPros\s*:\s*", rest, maxsplit=1, flags=re.IGNORECASE)
        if len(pros_split) == 2:
            outer_label, pros = pros_split[0].strip().rstrip("."), pros_split[1].strip()
        else:
            outer_label, pros = rest, ""
        # Combine inner + outer label: inner takes precedence, outer fills if empty
        label = inner if inner else outer_label
        return label, pros

    a_label, a_pros = _split_label_and_pros(opts[0].group(2), opts[0].group(3))
    b_label, b_pros = _split_label_and_pros(opts[1].group(2), opts[1].group(3))

    # Remove "Pros: " prefix if duplicated
    a_pros = re.sub(r"^Pros:\s*", "", a_pros, flags=re.IGNORECASE)
    b_pros = re.sub(r"^Pros:\s*", "", b_pros, flags=re.IGNORECASE)

    # Quality list: line that starts with "Quality list:" then comma/slash list
    qual_m = re.search(r"Quality list:\s*([^\n]+?)(?:\.\s|\n|$)", payload)
    quality_list = []
    if qual_m:
        raw = qual_m.group(1)
        raw = re.sub(r"\(or write your own\)", "", raw, flags=re.IGNORECASE)
        for sep in ("/", ","):
            if sep in raw:
                quality_list = [q.strip().rstrip(".") for q in raw.split(sep) if q.strip()]
                break
        if not quality_list:
            quality_list = [raw.strip()]

    # Justify prompt = the question after "Quality list:" line, skipping the
    # "(Or write your own.)" parenthetical that often closes the list.
    justify_prompt = ""
    if qual_m:
        after = payload[qual_m.end():]
        # Strip leading parenthetical "(Or write your own.)" or similar
        after = re.sub(r"^\s*\([^)]+\)\s*", "", after)
        # Take the first sentence-like text up to a question mark
        jm = re.search(r"([A-Z][^?]+\?)", after, re.DOTALL)
        if jm:
            justify_prompt = _strip_underscore_runs(jm.group(1)).strip()

    return {
        "scenario": scenario,
        "a_label": a_label,
        "a_pros": a_pros,
        "b_label": b_label,
        "b_pros": b_pros,
        "quality_list": quality_list,
        "justify_prompt": justify_prompt,
    }


# ---------- F10 3-2-1 Reflective ----------

BOLD_BLOCK_RE = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)


def extract_three_two_one(payload: str) -> dict:
    """Pattern: stem + three bold sections opening with the numerals 3 / 2 / 1.

    Handles both markdown variants seen in the corpus:
      a) `**3 things ... :**`           — full phrase bolded as one unit
      b) `**3** things ... :`           — numeral bolded alone, label after

    Approach: scan every bold block; sections that open with a digit are
    treated as section heads. Body for a head is everything between this bold
    block and the next bold block (or end of payload)."""
    matches = list(BOLD_BLOCK_RE.finditer(payload))
    if len(matches) < 3:
        return {}

    sections = []
    for i, m in enumerate(matches):
        bold_text = m.group(1).strip()
        digit_m = re.match(r"^(\d)\b\s*(.*)$", bold_text, re.DOTALL)
        if not digit_m:
            continue
        num = int(digit_m.group(1))
        label_in_bold = digit_m.group(2).strip().rstrip(":").rstrip()

        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(payload)
        body = payload[body_start:body_end]
        # If the bold block was just the numeral (variant b), the label trails
        # the bold block in plain text on the same paragraph.
        if not label_in_bold:
            # Take everything up to the first newline of the body as the label
            head_line = body.lstrip("\n").split("\n", 1)[0].strip().rstrip(":")
            label = head_line
        else:
            label = label_in_bold

        slot_lines = sum(1 for line in body.splitlines()
                         if re.match(r"^\s*\d+\.\s", line))
        if slot_lines == 0:
            # Single-slot last section ("1 connection: ___") often has no
            # numbered child — render exactly N slots based on the section
            # number.
            slot_lines = num

        sections.append({"num": num, "label": label, "slots": min(slot_lines, num)})

    nums = [s["num"] for s in sections]
    if nums[:3] != [3, 2, 1]:
        return {}

    cols = sections[:3]

    # Stem is whatever appears before the first **3** section
    stem = ""
    if matches:
        pre = payload[: matches[0].start()].strip()
        stem = _first_paragraph(pre) if pre else ""

    return {
        "stem": stem,
        "cols": cols,
    }


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
        "concept_map": {},
        "decision_tree": {},
        "ranked": {},
        "mini_case": {},
        "tradeoff": {},
        "three_two_one": {},
        "fallback_html": "",
    }

    fid = ticket.format_id
    extractor_map = {
        "mcq":            ("mcq",            lambda t: extract_mcq(t.payload)),
        "matrix":         ("matrix",         lambda t: extract_matrix(t.payload)),
        "venn":           ("venn",           lambda t: extract_venn(t)),
        "short_response": ("short_response", lambda t: extract_short_response(t.payload)),
        "concept_map":    ("concept_map",    lambda t: extract_concept_map(t.payload)),
        "decision_tree":  ("decision_tree",  lambda t: extract_decision_tree(t.payload)),
        "ranked":         ("ranked",         lambda t: extract_ranked(t.payload)),
        "mini_case":      ("mini_case",      lambda t: extract_mini_case(t.payload)),
        "tradeoff":       ("tradeoff",       lambda t: extract_tradeoff(t.payload)),
        "three_two_one":  ("three_two_one",  lambda t: extract_three_two_one(t.payload)),
    }

    if fid in extractor_map:
        key, extractor = extractor_map[fid]
        ctx[key] = extractor(ticket)
        # short_response always fires the structured render even with empty stem
        if not ctx[key] and fid != "short_response":
            ctx["fallback_html"] = render_fallback_html(ticket.payload)
            ctx["format_id"] = "fallback"
    else:
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
