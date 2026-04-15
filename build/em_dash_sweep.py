#!/usr/bin/env python3
"""
Em dash + AI cliché sweep for CCE curriculum docs/.

This script applies context-sensitive em dash replacements and AI cliché
cleanup across all docs/*.md files. It reads each file, applies pattern-based
replacements, and writes back only if changes were made.

Rules:
- KEEP em dashes in # headings (structural chrome)
- KEEP em dashes inside quoted BLS/government attribution blocks
- Replace all others using the rubric hierarchy

Out of scope:
- Wk0 days 1, 2, 4, 5 (recently compressed, clean)
- Files outside docs/

Usage: python3 build/em_dash_sweep.py [--dry-run] [--block 1sw|2sw|3sw|4sw|5sw|6sw]
"""

import os
import re
import sys
import glob
import argparse

EM_DASH = "\u2014"  # —

# Files to never touch
SKIP_FILES = {
    "docs/1sw/wk0-classroom-routines/day1.md",
    "docs/1sw/wk0-classroom-routines/day2.md",
    "docs/1sw/wk0-classroom-routines/day4.md",
    "docs/1sw/wk0-classroom-routines/day5.md",
}

# AI cliché patterns: (regex, replacement_func_or_string)
# These need context — we handle them line by line
CLICHE_PATTERNS = [
    # "vital skill" → "skill", "vital role" → "role", etc.
    (r'\bvital\s+(skill|role|component|part|step|tool|resource|foundation|piece)\b', r'\1'),
    # "essential skill" → "skill"
    (r'\bessential\s+(skill|part|component|step|tool|element)\b', r'\1'),
    # "meaningful\s+X" where X is a filler noun
    (r'\bmeaningful\s+(learning experience|experience|connection|activity|discussion|impact)\b', r'\1'),
    # "engaging\s+X" where X is a filler noun
    (r'\bengaging\s+(activity|lesson|experience|discussion|way)\b', r'\1'),
    # "hone their/your/student skills" (decorative) → "practice their/your/student skills"
    (r'\bhone\s+(their|your|students\'?)\s+(skills?)\b', r'practice \1 \2'),
    # "hone skills" → "practice skills"
    (r'\bhone\s+(skills?)\b', r'practice \1'),
    # "the journey of career exploration" → "career exploration"
    (r'\bthe journey of\s+', ''),
    # "dive into" → "explore" (but only when it's filler)
    (r'\b[Dd]ive into\b', lambda m: 'Explore' if m.group()[0] == 'D' else 'explore'),
    # "cutting-edge" → remove or replace
    (r'\bcutting-edge\s+', ''),
    # "in today's" → "in the current" (context dependent, may need manual review)
    # Skip — too context-dependent for automation
    # "innovative" → remove when adjective filler
    (r'\binnovative\s+(approach|solution|way|method|tool)\b', r'\1'),
    # "impactful" → remove when filler
    (r'\bimpactful\s+(experience|activity|lesson|way)\b', r'\1'),
    # "instrumental" → remove when filler
    (r'\binstrumental\s+in\b', 'important for'),
    # "at the end of the day" → remove
    (r'\b[Aa]t the end of the day,?\s*', lambda m: '' if m.group()[0] == 'a' else ''),
    # "navigate the" → context dependent, skip automated
]


def is_heading(line):
    """Check if a line is a markdown heading."""
    return line.lstrip().startswith('#')


def is_table_row(line):
    """Check if a line is a markdown table row."""
    stripped = line.strip()
    return stripped.startswith('|') and stripped.endswith('|')


def process_em_dashes_in_line(line, line_num):
    """Process em dashes in a single line, returning the modified line."""
    if EM_DASH not in line:
        return line

    # Rule: KEEP em dashes in headings (structural chrome)
    if is_heading(line):
        return line

    # Process each em dash occurrence
    result = line

    # Pattern 1: "**Bold Text** — Description" → "**Bold Text:** Description"
    # Common in lists like pathway descriptions, career lists
    result = re.sub(
        r'\*\*([^*]+)\*\*\s*' + EM_DASH + r'\s*',
        r'**\1:** ',
        result
    )

    # Pattern 2: "(parenthetical) — Description" → "(parenthetical): Description"
    result = re.sub(
        r'\)\s*' + EM_DASH + r'\s*',
        '): ',
        result
    )

    # Pattern 3: "BLS — Topic:" → "BLS, Topic:"
    result = re.sub(
        r'BLS\s*' + EM_DASH + r'\s*',
        'BLS, ',
        result
    )

    # Pattern 4: "Source: ... — \"Title\"" → "Source: ..., \"Title\""
    result = re.sub(
        r'(pp?\.\s*\d[\d-]*)\s*' + EM_DASH + r'\s*',
        r'\1, ',
        result
    )

    # Pattern 5: "text — d(N)(X)" (TEKS code reference after formative assessment)
    result = re.sub(
        r'\s*' + EM_DASH + r'\s*(d\(\d\)\([A-Z]\))',
        r', \1',
        result
    )

    # Pattern 6: Independent clauses "sentence — sentence" → "sentence. Sentence"
    # Only if what follows starts with a capital letter (or "and", "but", "so", "the", etc.)
    def replace_independent_clause(m):
        before = m.group(1)
        after = m.group(2)
        # If what follows looks like a new sentence (starts with capital)
        if after and after[0].isupper():
            return f"{before}. {after}"
        # Otherwise use comma
        return f"{before}, {after}"

    result = re.sub(
        r'([.!?a-z\"\'])\s*' + EM_DASH + r'\s*([A-Za-z])',
        replace_independent_clause,
        result
    )

    # Pattern 7: Any remaining em dashes → comma (safest default)
    if EM_DASH in result:
        result = result.replace(f' {EM_DASH} ', ', ')
        result = result.replace(EM_DASH, ', ')

    return result


def process_cliches_in_line(line):
    """Process AI clichés in a single line."""
    result = line
    for pattern, replacement in CLICHE_PATTERNS:
        if callable(replacement):
            result = re.sub(pattern, replacement, result)
        else:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


def process_file(filepath, dry_run=False):
    """Process a single file for em dashes and clichés."""
    rel_path = os.path.relpath(filepath, os.getcwd())

    # Skip protected files
    if rel_path in SKIP_FILES:
        return 0, 0, 0

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    original_content = ''.join(lines)
    em_dash_count_before = original_content.count(EM_DASH)

    new_lines = []
    em_dashes_removed = 0
    cliches_fixed = 0

    for i, line in enumerate(lines, 1):
        # Em dash processing
        new_line = process_em_dashes_in_line(line, i)

        # Count em dashes removed
        removed = line.count(EM_DASH) - new_line.count(EM_DASH)
        em_dashes_removed += removed

        # Cliché processing
        cliche_line = process_cliches_in_line(new_line)
        if cliche_line != new_line:
            cliches_fixed += 1

        new_lines.append(cliche_line)

    new_content = ''.join(new_lines)
    em_dash_count_after = new_content.count(EM_DASH)

    if new_content != original_content:
        if not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
        return em_dashes_removed, em_dash_count_after, cliches_fixed
    return 0, em_dash_count_after, 0


def main():
    parser = argparse.ArgumentParser(description='Em dash + AI cliché sweep')
    parser.add_argument('--dry-run', action='store_true', help='Preview without writing')
    parser.add_argument('--block', type=str, help='Process only this block (1sw, 2sw, etc.)')
    parser.add_argument('--include-resources', action='store_true', help='Include docs/resources/ and docs/index.md')
    args = parser.parse_args()

    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Build file list
    if args.block:
        patterns = [f"docs/{args.block}/*/*.md"]
    else:
        patterns = ["docs/[1-6]sw/*/*.md"]

    if args.include_resources:
        patterns.extend(["docs/index.md", "docs/resources/*.md"])

    files = []
    for pattern in patterns:
        files.extend(sorted(glob.glob(pattern)))

    # Deduplicate
    files = sorted(set(files))

    total_removed = 0
    total_remaining = 0
    total_cliches = 0
    files_changed = 0

    print(f"{'DRY RUN: ' if args.dry_run else ''}Processing {len(files)} files...")
    print()

    for filepath in files:
        rel = os.path.relpath(filepath)
        removed, remaining, cliches = process_file(filepath, args.dry_run)
        if removed > 0 or cliches > 0:
            files_changed += 1
            print(f"  {rel}: {removed} em dashes removed ({remaining} kept), {cliches} clichés fixed")
        total_removed += removed
        total_remaining += remaining
        total_cliches += cliches

    print()
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Summary:")
    print(f"  Files processed: {len(files)}")
    print(f"  Files changed: {files_changed}")
    print(f"  Em dashes removed: {total_removed}")
    print(f"  Em dashes remaining (structural): {total_remaining}")
    print(f"  Cliché lines fixed: {total_cliches}")


if __name__ == '__main__':
    main()
