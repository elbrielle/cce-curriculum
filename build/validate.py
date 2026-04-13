#!/usr/bin/env python3
"""
validate.py -- Check all facilitator guide markdown files for issues.

Usage:
    python build/validate.py              # validate all guides
    python build/validate.py path/to.md   # validate one file

Checks:
  - YAML frontmatter has all required fields
  - All 12 required ## sections exist in correct order
  - Lesson Sequence has at least one ### Day heading
  - Differentiation has all 3 ### subsections
  - Special markers use correct syntax
  - No stray # (h1) headings
"""

import sys, re, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDES_DIR = ROOT / "cce-curriculum" / "guides"

REQUIRED_FIELDS = [
    "six_weeks", "week", "title", "subtitle",
    "topic", "length", "cluster", "pathways",
]

REQUIRED_SECTIONS = [
    "Lesson Objective",
    "Demonstration of Learning",
    "TEKS Alignment",
    "Materials Needed",
    "Career Connection",
    "Vocabulary",
    "Bridge to Theory (Hats & Ladders)",
    "IISD Instructional Strategies",
    "Lesson Sequence",
    "Formative Assessment",
    "Summative Assessment",
    "Differentiation",
]

DIFF_SUBSECTIONS = [
    "Scaffolded Learning",
    "Extensions",
    "ELL Language Support",
]


def validate_file(path):
    """Validate a single markdown guide. Returns list of issue strings."""
    issues = []
    text = path.read_text(encoding="utf-8")

    # ── Frontmatter ──
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    if not m:
        issues.append("Missing YAML frontmatter (---)")
        return issues

    try:
        meta = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        issues.append(f"Invalid YAML: {e}")
        return issues

    for field in REQUIRED_FIELDS:
        if not meta.get(field):
            issues.append(f"Missing frontmatter field: {field}")

    body = text[m.end():]

    # ── No h1 headings ──
    h1s = re.findall(r'^# [^#]', body, re.MULTILINE)
    if h1s:
        issues.append(f"Found {len(h1s)} h1 heading(s) -- title should come from frontmatter, not # heading")

    # ── Required ## sections ──
    found_sections = re.findall(r'^## (.+)$', body, re.MULTILINE)
    found_clean = [s.strip() for s in found_sections]

    for req in REQUIRED_SECTIONS:
        if req not in found_clean:
            issues.append(f"Missing section: ## {req}")

    # Check order of the ones that are present
    expected_order = [s for s in REQUIRED_SECTIONS if s in found_clean]
    actual_order = [s for s in found_clean if s in REQUIRED_SECTIONS]
    if expected_order != actual_order:
        issues.append("Sections are out of order")

    # ── Lesson Sequence needs ### Day headings ──
    lesson_seq_match = re.search(r'^## Lesson Sequence\s*\n(.*?)(?=^## |\Z)', body, re.MULTILINE | re.DOTALL)
    if lesson_seq_match:
        day_headings = re.findall(r'^### Day \d', lesson_seq_match.group(1), re.MULTILINE)
        if not day_headings:
            issues.append("Lesson Sequence has no ### Day headings")

    # ── Differentiation subsections ──
    diff_match = re.search(r'^## Differentiation\s*\n(.*?)(?=^## |\Z)', body, re.MULTILINE | re.DOTALL)
    if diff_match:
        diff_content = diff_match.group(1)
        for sub in DIFF_SUBSECTIONS:
            if f"### {sub}" not in diff_content:
                issues.append(f"Differentiation missing subsection: ### {sub}")

    # ── Marker syntax checks ──
    # Teacher scripts should be in blockquotes
    bad_teacher = re.findall(r'^(?!>)\s*\*\*Teacher:\*\*', body, re.MULTILINE)
    if bad_teacher:
        issues.append(f"{len(bad_teacher)} teacher script(s) not in blockquotes (should start with > )")

    # Flags should be in blockquotes
    for tag in ["H&L PLATFORM", "VERIFY IN H&L", "VERIFY IN eDynamic"]:
        bad = re.findall(rf'^(?!>)\s*\[{re.escape(tag)}\]', body, re.MULTILINE)
        if bad:
            issues.append(f"{len(bad)} [{tag}] flag(s) not in blockquotes")

    return issues


def main():
    if len(sys.argv) > 1:
        files = [Path(f) for f in sys.argv[1:]]
    else:
        files = sorted(GUIDES_DIR.rglob("*.md"))

    total_issues = 0
    clean = 0

    for path in files:
        issues = validate_file(path)
        if issues:
            print(f"\n  {path.name}")
            for issue in issues:
                print(f"    - {issue}")
            total_issues += len(issues)
        else:
            clean += 1

    print(f"\n{'=' * 50}")
    print(f"Validated {len(files)} files: {clean} clean, {len(files) - clean} with issues ({total_issues} total)")

    return 0 if total_issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
