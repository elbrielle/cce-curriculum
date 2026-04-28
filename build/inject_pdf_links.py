#!/usr/bin/env python3
"""
inject_pdf_links.py — Add (or refresh) the · [Printable PDF](...) link on
every **EXIT TICKET** marker line in docs/Nsw/wkN-topic/dayN.md.

Idempotent: re-running yields no diff if PDF paths haven't changed.

Usage:
  python3 build/inject_pdf_links.py                 # all day files
  python3 build/inject_pdf_links.py docs/2sw/...    # subset
  python3 build/inject_pdf_links.py --check         # report-only, no writes
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# Re-use the parser from build_pdfs so slug/path logic stays in one place.
sys.path.insert(0, str(ROOT / "build"))
from build_pdfs import parse_day_file  # noqa: E402

# Match the EXIT TICKET marker line, with or without an existing PDF link.
MARKER_RE = re.compile(
    r"^(\*\*EXIT TICKET\*\*\s*\([^)]+\))"           # group 1: marker + (Format)
    r"(?:\s*·\s*\[Printable PDF\]\([^)]*\))?"      # optional existing link
    r"(\s*:\s*)$",                                  # group 2: trailing colon (+ trailing whitespace)
    re.MULTILINE,
)


def expected_link_for(ticket) -> str:
    return (
        f"../../resources/exit-tickets/"
        f"{ticket.block_num}sw-wk{ticket.week_num}-day{ticket.day_num}-{ticket.slug}.pdf"
    )


def expected_marker_line(match, ticket) -> str:
    marker = match.group(1)
    colon = match.group(2)
    return f"{marker} · [Printable PDF]({expected_link_for(ticket)}){colon}"


def process_file(path: Path, check_only: bool) -> str:
    """
    Returns one of: 'updated', 'unchanged', 'skipped' (no marker / no parsable ticket),
    or 'check-fail' (in --check mode, would have changed).
    """
    ticket = parse_day_file(path)
    if ticket is None:
        return "skipped"

    raw = path.read_text(encoding="utf-8")
    m = MARKER_RE.search(raw)
    if not m:
        # parse_day_file matched but our marker regex didn't — formatting drift
        return "skipped"

    new_line = expected_marker_line(m, ticket)
    if raw[m.start() : m.end()] == new_line:
        return "unchanged"

    if check_only:
        return "check-fail"

    new_raw = raw[: m.start()] + new_line + raw[m.end() :]
    path.write_text(new_raw, encoding="utf-8")
    return "updated"


def collect(globs):
    if not globs:
        return sorted(DOCS.glob("*sw/wk*-*/day*.md"))
    paths = []
    for g in globs:
        paths.extend(ROOT.glob(g))
    return sorted(set(paths))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Optional day-file globs")
    parser.add_argument("--check", action="store_true",
                        help="Report files that would change; do not write.")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress per-file logging.")
    args = parser.parse_args(argv)

    files = collect(args.paths)
    if not files:
        print("No day files matched.", file=sys.stderr)
        return 1

    counts = {"updated": 0, "unchanged": 0, "skipped": 0, "check-fail": 0}
    for p in files:
        result = process_file(p, check_only=args.check)
        counts[result] += 1
        if not args.quiet and result not in ("unchanged", "skipped"):
            rel = p.relative_to(ROOT)
            tag = "WOULD UPDATE" if result == "check-fail" else "UPDATED    "
            print(f"  {tag}  {rel}")

    print(f"\nDone. updated={counts['updated']} unchanged={counts['unchanged']} "
          f"skipped={counts['skipped']} check-fail={counts['check-fail']}")
    if args.check and counts["check-fail"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
