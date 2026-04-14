# CCE Curriculum

36-week Career and College Explorations course for Irving ISD VILS Labs (Texas) — a new prep for middle school VILS classrooms across the district, distinct from the Engineering VILS curriculum.
Aligned to TEKS &sect;127.2 Career and College Exploration (Adopted 2023).

## Quick Start

```bash
# validate all 36 guides
python3 build/validate.py

# rebuild all .docx facilitator guides
python3 build/build_docx.py

# rebuild a single guide
python3 build/build_docx.py cce-curriculum/guides/1sw/wk1-robotics-manufacturing.md

# rebuild the scope & sequence spreadsheet
python3 build/build_xlsx.py
```

Requires: `python-docx`, `openpyxl`, `pyyaml` (`pip install python-docx openpyxl pyyaml`).

## Structure

```
cce-curriculum/               <- source of truth (edit these)
  scope-and-sequence.md       <- master pacing guide (36 rows, 13 columns)
  guides/
    1sw/  wk0-wk5             <- IT / Manufacturing
    2sw/  wk1-wk6             <- Law / Health Science
    3sw/  wk1-wk6             <- Ag / Hospitality / Entrepreneurship
    4sw/  wk1-wk6             <- Career Planning / Aviation / Trades
    5sw/  wk1-wk6             <- Architecture / Construction / Finance
    6sw/  wk1-wk6             <- Education / Business / Capstone
  resources/
    teks-coverage-matrix.md   <- TEKS code -> weeks -> status
    free-resource-directory.md
    edynamic-unit-map.md
    reference-pdfs/           <- H&L workbook text extracts (.txt only; PDFs are local-only)
  notes/
    development-notes.md      <- flag status, open items
    revision-plan.md          <- H&L workbook chapter-to-week crosswalk

build/                        <- Python build scripts (md -> docx/xlsx)
output/                       <- generated files (gitignored, rebuild from source)
```

## Platforms

| Platform | Role | Access |
|----------|------|--------|
| **Hats & Ladders** | Core: RIASEC, career clusters, Hat Finder, Career Plan | App + student workbook (282pp) + Powerskills supplement (221pp) |
| **Xello** | Supplement: quizzes, resume builder | District login |
| **eDynamic Learning** | Supplement: career exploration units | District login |
| **VILS Tech** | Hands-on: Sphero, Glowforge, drones, micro:bit, LEGOs | Lab equipment |

## Editing Guides

Every guide follows the template in `GUIDE-FORMAT.md`. Key rules:
- Frontmatter (YAML) is required
- Sections must appear in the exact order listed in GUIDE-FORMAT.md
- Special markers (`> **Teacher:**`, `> [H&L PLATFORM]`, `**WARM-UP:**`, etc.) are parsed by the build script for colored formatting

## H&L Workbook References

The official Hats & Ladders student workbook and Powerskills supplement are the authoritative source for H&L content. The PDFs are too large for GitHub (116MB + 21MB) and live locally at `cce-curriculum/resources/reference-pdfs/`. Searchable `.txt` extracts are committed to the repo.

```bash
# search for an activity
grep -n -i "candy conundrum" cce-curriculum/resources/reference-pdfs/HatsandLadders.txt

# search powerskills
grep -n -i "conflict resolution" cce-curriculum/resources/reference-pdfs/Powerskills.txt
```

The full chapter-to-week crosswalk is in `cce-curriculum/notes/revision-plan.md`.

## Current Status

- **36/36** facilitator guides complete
- **0** `[VERIFY IN H&L]` flags remaining (all 57 resolved)
- **6** `[VERIFY IN eDynamic]` flags remaining (need teacher dashboard access)
- **0** TEKS standards marked NEEDS ENRICHMENT
- All guides pass `validate.py` and build cleanly

## For AI Agents

Read `CLAUDE.md` first -- it has the full repo map, build instructions, H&L search patterns, and editing conventions. The revision plan at `notes/revision-plan.md` maps every H&L workbook chapter to curriculum weeks.
