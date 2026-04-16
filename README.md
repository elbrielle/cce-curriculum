# CCE Curriculum

36-week Career and College Explorations course for Irving ISD VILS Labs (Texas) — a new prep for middle school VILS classrooms across the district, distinct from the Engineering VILS curriculum.
Aligned to TEKS &sect;127.2 Career and College Exploration (Adopted 2023).

## Quick Start

```bash
# validate the MkDocs site (zero warnings required)
python3 -m mkdocs build --strict

# local preview
python3 -m mkdocs serve    # → http://127.0.0.1:8000/

# legacy: rebuild .docx/.xlsx
python3 build/build_docx.py
python3 build/build_xlsx.py
```

Live site: `https://elbrielle.github.io/cce-curriculum/latest/`

## Structure

```
docs/                         <- THE WEBSITE (source of truth, edit these)
  scope-and-sequence.md
  1sw/ ... 6sw/               <- six-weeks blocks
    wkN-topic/
      overview.md             <- weekly big picture
      day1.md ... day5.md     <- daily lesson plans
  resources/

cce-curriculum/               <- reference data (not the website)
  scope-and-sequence.md       <- master pacing guide (authoritative)
  resources/reference-pdfs/   <- H&L workbook .txt extracts (PDFs local-only)
  notes/                      <- editing heuristics, revision plan, review notes

build/                        <- Python build scripts (legacy docx/xlsx)
```

## Platforms

| Platform | Role | Access |
|----------|------|--------|
| **Hats & Ladders** | Core: RIASEC, career clusters, Hat Finder, Career Plan | App + student workbook (282pp) + Powerskills supplement (221pp) |
| **Xello** | Supplement: quizzes, resume builder | District login |
| **eDynamic Learning** | Supplement: career exploration units | District login |
| **VILS Tech** | Hands-on: Sphero, Glowforge, drones, micro:bit, LEGOs | Lab equipment |

## Editing the Curriculum

Edit files in `docs/` only. Prototype week: `docs/5sw/wk1-architecture/`. Key rules:
- No teacher scripting (`> **Teacher:**` is deprecated)
- Source-ground all content to H&L workbook, S&S, Xello, eDynamic, or BLS
- See `CLAUDE.md` for full editing rules and `cce-curriculum/notes/editing-heuristics.md` for the dependency-scope protocol

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
- Site builds clean (`mkdocs build --strict`)

## For AI Agents

Read `CLAUDE.md` first, then `PLANNING.md` for current project state. The revision plan at `cce-curriculum/notes/revision-plan.md` maps every H&L workbook chapter to curriculum weeks.
