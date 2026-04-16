# CCE Curriculum Codebase

## What This Is

A 36-week Career and College Explorations (CCE) course curriculum for grade 7 across Irving ISD VILS Labs, Texas. Aligned to TEKS 127.2 Career and College Exploration (Adopted 2023). Delivered as a MkDocs Material static site. Core platform is Hats & Ladders, supplemented by Xello, eDynamic Learning, and VILS technology integration.

## Repo Structure

```
27 CCR Planning/
├── CLAUDE.md                          ← you are here
├── PLANNING.md                        ← project state + agent briefing
├── mkdocs.yml                         ← site config + full nav
├── PATHWAYS.md                        ← Irving ISD CTE pathway reference
├── PLATFORMS.md                       ← platform descriptions
│
├── docs/                              ← THE WEBSITE (source of truth)
│   ├── scope-and-sequence.md
│   ├── 1sw/ ... 6sw/                  ← six-weeks blocks
│   │   └── wkN-topic/
│   │       ├── overview.md            ← weekly big picture
│   │       └── day1.md ... day5.md    ← five daily lesson plans
│   └── resources/
│
├── cce-curriculum/                    ← reference data (not the website)
│   ├── scope-and-sequence.md          ← master pacing guide (authoritative)
│   ├── resources/reference-pdfs/      ← H&L workbook PDFs + .txt extracts
│   └── notes/
│       ├── editing-heuristics.md      ← READ before substantive edits
│       ├── instinct-review.md
│       ├── vetting-report.md          ← FROZEN
│       └── revision-plan.md           ← H&L chapter-to-week crosswalk
│
├── build/                             ← Python build scripts (docx/xlsx)
└── site/                              ← built MkDocs site (gitignored)
```

**Edit `docs/` only.** Original `.docx`/`.xlsx` files in root are reference copies (gitignored).

## Curriculum Structure

Each week has two tiers:

1. **Weekly Overview** (`overview.md`) — Lesson Objective, DOL, TEKS Alignment, Materials, Career Connection, Vocabulary, Bridge to Theory, IISD Instructional Strategies, Week at a Glance, Formative/Summative Assessment, Differentiation.

2. **Daily Lesson Plans** (`day1.md` through `day5.md`) — Lesson Overview table, Warm-Up, Activities with facilitation notes, Deliverable, Exit Ticket, Differentiation.

**Prototype to match:** `docs/5sw/wk1-architecture/`

## Writing Rules

- **No teacher scripting.** Never `> **Teacher:** "..."`. Describe what teacher and students do in facilitation prose.
- **Concrete deliverables per day.** Every plan ends with a specific artifact (PNG, worksheet, presentation).
- **Activity specs, not vague instructions.** "Design a building with 4+ walls, roof, 1 door, 2 windows. Export as PNG."
- **Facilitation tips, not scripts.** "If students struggle with grouping, demonstrate align-then-group on the projector."
- **No em dashes** in teacher-facing `docs/` body prose. Developer-facing files are fine.

## Source Grounding

All content must trace to one of these:

- **H&L Student Workbook** (282pp, 17 ch) — cite as `(H&L Ch N, p. X)` or `(H&L Ch N: "Activity Name")`
- **H&L Powerskills Supplement** (221pp, 12 modules) — cite as `(Powerskills, p. X: "Module Name")`
- **Scope and Sequence** (`cce-curriculum/scope-and-sequence.md`)
- **Xello 7th-Grade Task List** — names from S&S column 8
- **eDynamic Learning Units** — unit numbers from S&S column 9
- **BLS Occupational Outlook Handbook** — salary, education, outlook data
- **Irving ISD CTE Pathways** (PATHWAYS.md) — verify against [canonical website](https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte) before citing

Do not invent H&L activities, Xello features, or platform capabilities. If unsure, mark with `[VERIFY]`.

## Editing Protocol

Before any substantive edit, read **`cce-curriculum/notes/editing-heuristics.md`**. It has:
- Decision table ("before editing X, read Y")
- Paste-ready grep recipes
- "Never do X without reading more" rules
- Escalation criteria

Also read **`PLANNING.md`** for current project state, non-negotiables, and preservation loop.

## Special Markers

Parsed by build script and MkDocs for styled rendering:

| Marker | Usage |
|--------|-------|
| `> [H&L PLATFORM] ...` | Hats & Ladders platform instruction |
| `> [VERIFY IN eDynamic] ...` | Needs eDynamic verification |
| `**WARM-UP:** ...` | Daily warm-up prompt |
| `**EXIT TICKET:** ...` | Daily exit ticket |
| `**DOK N:** ...` | Depth of Knowledge question |
| `**DELIVERABLE:** ...` | Student submission artifact |

**Deprecated:** `> **Teacher:** "..."` — do NOT use.

## H&L Workbook Reference

Two PDFs in `cce-curriculum/resources/reference-pdfs/`. The H&L PDF is 116MB/282pp — **never read in full**.

```bash
# Search the text extract
grep -n -i "safety supervisor" cce-curriculum/resources/reference-pdfs/HatsandLadders.txt

# Extract specific pages
pdftotext -f 37 -l 54 cce-curriculum/resources/reference-pdfs/HatsandLadders.pdf -

# Search Powerskills
grep -n -i "time management" cce-curriculum/resources/reference-pdfs/Powerskills.txt
```

Chapter-to-week crosswalk: `cce-curriculum/notes/revision-plan.md`

## Build

```bash
python3 -m mkdocs build --strict    # validate site
python3 -m mkdocs serve             # local preview at 127.0.0.1:8000
python3 build/build_docx.py         # rebuild .docx files (legacy)
python3 build/build_xlsx.py         # rebuild spreadsheet (legacy)
```
