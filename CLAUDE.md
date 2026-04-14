# CCE Curriculum Codebase

## What This Is

A 36-week Career and College Explorations (CCE) course curriculum for middle school (grades 6-8) across Irving ISD VILS Labs, Texas. This is a new prep delivered in VILS labs district-wide, distinct from the Engineering VILS curriculum class. Aligned to TEKS §127.2 Career and College Exploration (Adopted 2023). The curriculum uses Hats & Ladders as the core platform, supplemented by Xello, eDynamic Learning, and VILS technology integration.

## Curriculum Structure: Overview + Daily Plans

The curriculum uses a **two-tier structure** for each week:

1. **Weekly Overview** (`guides/Xsw/wkN-topic.md`) — the "big picture" document. Contains: Lesson Objective, DOL, TEKS Alignment, Materials, Career Connection, Vocabulary, Bridge to Theory, IISD Instructional Strategies, Formative/Summative Assessment, Differentiation. No daily lesson flow details.

2. **Daily Lesson Plans** (`guides/Xsw/wkN-topic/day1.md` through `day5.md`) — one per class period. Each follows this structure:
   - **Lesson Overview** (objectives, time, deliverable)
   - **Warm-Up** (5 min discussion prompt)
   - **Activities** with facilitation notes (NOT teacher scripting — describe the flow, process, and what to watch for)
   - **Deliverable** (concrete artifact: screenshot, worksheet, presentation)
   - **Reflection / Exit Ticket**
   - **Differentiation** (per-lesson supports)

### Writing Style for Daily Plans

- **No teacher scripting.** Do NOT use `> **Teacher:** "..."` quotes. Instead, describe what the teacher does and what students do in natural facilitation language. Example: "Introduce the activity by connecting TinkerCAD to professional CAD tools used at MacArthur HS. Walk students through account creation by projecting the sign-up screen."
- **Concrete deliverables per lesson.** Every daily plan ends with a specific artifact: PNG screenshot, completed worksheet, research template, presentation outline.
- **Activity specs, not vague instructions.** Instead of "design a building," specify: "Design a building with at least 4 walls, a roof, 1 door opening, and 2 window openings. Export as PNG."
- **Facilitation tips** instead of scripts. "If students struggle with grouping, demonstrate align-then-group on the projector."
- **Source-grounded in workbooks.** H&L activities reference the specific workbook chapter, page, and activity name. Xello activities reference the specific lesson/quiz name from the 7th-grade task list. eDynamic references the unit number.

### Source Grounding Requirements

All curriculum content must trace back to one of these authoritative sources:
- **H&L Student Workbook** (282pp, 17 chapters) — cite as `(H&L Ch N, p. X)` or `(H&L Ch N: "Activity Name")`
- **H&L Powerskills Supplement** (221pp, 12 modules) — cite as `(Powerskills, p. X: "Module Name")`
- **Scope and Sequence** (`scope-and-sequence.md`) — the master pacing guide from the original planning spreadsheet
- **Xello 7th-Grade Task List** — specific lesson/quiz names mapped in scope-and-sequence column 8
- **eDynamic Learning Units** — unit numbers mapped in scope-and-sequence column 9
- **BLS Occupational Outlook Handbook** — for salary, education, and job outlook data
- **Irving ISD CTE Pathways** (PATHWAYS.md) — for local pathway names, schools, and certifications

Do not invent H&L activities, Xello features, or platform capabilities. If unsure, mark with `[VERIFY]` and cite the source you checked.

## Repo Structure

```
27 CCR Planning/                       ← project root
├── CLAUDE.md                          ← you are here
├── README.md                          ← quick start + project summary
├── mkdocs.yml                         ← MkDocs site configuration
├── GUIDE-FORMAT.md                    ← markdown template + formatting rules
├── PATHWAYS.md                        ← Irving ISD CTE pathway reference data
├── PLATFORMS.md                       ← platform descriptions (H&L, Xello, eDynamic, VILS)
│
├── cce-curriculum/                    ← the markdown curriculum (source of truth)
│   ├── scope-and-sequence.md          ← master pacing guide (13-column table, 36 rows)
│   ├── guides/
│   │   ├── 1sw/                       ← 1st Six Weeks: IT / Manufacturing
│   │   │   ├── wk0-classroom-routines.md       ← weekly overview
│   │   │   ├── wk0-classroom-routines/          ← daily plans folder
│   │   │   │   ├── day1.md ... day5.md
│   │   │   ├── wk1-robotics-manufacturing.md
│   │   │   ├── wk1-robotics-manufacturing/
│   │   │   │   ├── day1.md ... day5.md
│   │   │   └── ... (same pattern for all weeks)
│   │   ├── 2sw/ ... 6sw/              ← same structure per six-weeks block
│   ├── resources/
│   │   ├── teks-coverage-matrix.md
│   │   ├── free-resource-directory.md
│   │   ├── edynamic-unit-map.md
│   │   └── reference-pdfs/            ← H&L workbook PDFs (local only) + .txt extracts (in repo)
│   └── notes/
│       ├── development-notes.md
│       └── revision-plan.md           ← H&L chapter-to-week crosswalk
│
├── docs/                              ← MkDocs site source (symlinks or copies from cce-curriculum)
├── build/                             ← Python build scripts (md → docx/xlsx)
├── output/                            ← generated files (gitignored)
└── site/                              ← built MkDocs site (gitignored)
```

## How to Edit the Curriculum

The **markdown files in `docs/`** are the live source of truth for the MkDocs website (the actual teacher-facing curriculum). The `cce-curriculum/guides/` folder is legacy reference from the initial conversion and should not be edited. The original `.docx` and `.xlsx` files in the root and `SW1-SW6/` are reference copies from the initial conversion and should not be edited.

Each facilitator guide follows a strict markdown template documented in `GUIDE-FORMAT.md`. Read that file before editing or creating guides.

### Editing heuristics (MUST READ before substantive edits)

Before making any substantive edit — and especially before reading multiple files to "get context" — consult **`cce-curriculum/notes/editing-heuristics.md`**. It contains:

- A **decision table** for "before editing X, read Y" (dependency-scope principle)
- **Paste-ready grep recipes** for S&S lookups, TEKS auditing, timing sums, DOK checks, differentiation checks, and H&L workbook lookups
- **Seven "never edit X without reading more"** rules for the edit types that most often break curriculum soundness
- **Escalation criteria** for when an edit is actually a redesign and should be bumped to the user

The goal is to strike the balance between reading too little (breaking logical flow or source grounding) and reading too much (wasting tokens). When in doubt, read more; when certain, grep.

## How to Build

```bash
python3 build/build_docx.py              # rebuild all 36 facilitator guide .docx files
python3 build/build_docx.py path/to.md   # rebuild a single guide
python3 build/build_xlsx.py              # rebuild the scope & sequence spreadsheet
```

Output goes to `output/docx/` and `output/`. Requires `python-docx`, `openpyxl`, and `pyyaml`.

## Reference PDFs (H&L Workbooks)

Two official Hats & Ladders workbooks live in `cce-curriculum/resources/reference-pdfs/`. These are the authoritative source for resolving `[VERIFY IN H&L]` flags and enriching `[H&L PLATFORM]` blocks in the facilitator guides.

**Critical:** The H&L PDF is 116MB / 282 pages. Never attempt to read it in full. Use the pre-extracted `.txt` files for searching, or `pdftotext -f <start_page> -l <end_page>` for targeted extraction. The full revision plan and chapter-to-week crosswalk is in `cce-curriculum/notes/revision-plan.md`.

### How to Search the Workbooks
```bash
# Search H&L text for a specific activity
grep -n -i "candy conundrum" cce-curriculum/resources/reference-pdfs/HatsandLadders.txt

# Extract specific PDF pages (e.g., Ch 2: Ag, pages 16-36)
pdftotext -f 16 -l 36 cce-curriculum/resources/reference-pdfs/HatsandLadders.pdf -

# Search Powerskills text
grep -n -i "time management" cce-curriculum/resources/reference-pdfs/Powerskills.txt

# Find VERIFY flags in a specific six weeks block
grep -n "VERIFY IN H&L" cce-curriculum/guides/1sw/*.md
```

### VILS Style Reference (DO NOT copy content)

Three Verizon Innovative Learning Schools facilitator guides are in `cce-curriculum/resources/vils-reference/`. These are **style references only** — study the lesson plan FORMAT (facilitation language, activity flow, deliverable specs, differentiation placement) but do NOT copy their content, topics, or branding. Our content comes from the H&L workbooks, scope-and-sequence, and our own TEKS-aligned activities.

- `VILS_Unit_Overview_Example.docx` — Unit overview format (objectives, materials, "The Why", common misconceptions, preparation checklist)
- `VILS_Daily_Lesson_Canva_Example.docx` — Daily lesson with Canva (warm-up, content sections, activity video, deliverable, reflection)
- `VILS_Daily_Lesson_TinkerCAD_Example.docx` — Daily lesson with TinkerCAD/3D modeling (scale calculations, guided tutorial, customization challenge)

**What to take from these:** No teacher scripting. Facilitation tips instead of dialogue. Clear deliverable per lesson. Activity videos/tutorials do the teaching. Concrete specs for student work.

**What NOT to take:** Their specific content, era themes, ISTE standards, or Canvas LMS references.

### Building New Weeks (Overview + Daily Plans)

For each week, follow this workflow:

1. **Read the scope-and-sequence row** for that week — get the H&L cluster, activities, Xello task, eDynamic unit, TEKS codes, and notes
2. **Check `notes/revision-plan.md`** for the H&L chapter + page range mapped to that week
3. **Extract the chapter content** from `HatsandLadders.txt` (use grep or line ranges) — identify the named activities, their steps, discussion prompts, and Hat Research template
4. **Read the existing weekly overview** (`guides/Xsw/wkN-topic.md`) — pull the strong structural elements (TEKS, vocabulary, career connection, DOL, differentiation)
5. **Create the overview** in `docs/Xsw/wkN-topic/overview.md` — weekly big picture with "Week at a Glance" table
6. **Create 5 daily plans** in `docs/Xsw/wkN-topic/day1.md` through `day5.md` — each with the lesson overview table, warm-up, activities with facilitation notes, deliverable, exit ticket, differentiation
7. **Use the 5SW Wk1 Architecture prototype** (`docs/5sw/wk1-architecture/`) as the format reference
8. **Update `mkdocs.yml`** nav section with the new week's pages
9. **Where the H&L workbook tells students to use the app** (Hat Finder, Climber Profile, Building Blocks, Career Plan), include those app instructions in `[H&L PLATFORM]` blocks — students use BOTH the workbook activities AND the app

## Key Conventions

### Weekly Overview Sections (in order)
Every weekly overview has these sections as `##` headings: Lesson Objective, Demonstration of Learning, TEKS Alignment, Materials Needed, Career Connection, Vocabulary, Bridge to Theory (Hats & Ladders), IISD Instructional Strategies, Week at a Glance, Formative Assessment, Summative Assessment, Differentiation.

The "Week at a Glance" section is a brief table or list summarizing each day's focus and deliverable. It replaces the old detailed "Lesson Sequence" which now lives in the daily plan files.

### Daily Plan Sections (in order)
Each daily plan (`dayN.md`) has: Lesson Overview (table with time/objectives/deliverable/materials), Warm-Up, Activity sections with facilitation notes, Deliverable + submission instructions, Reflection/Exit Ticket, Differentiation notes.

### Special Markers
These inline markers are parsed by the build script and MkDocs for styled rendering:
- `> [H&L PLATFORM] ...` — Hats & Ladders platform instruction (blue background)
- `> [VERIFY IN eDynamic] ...` — needs verification in eDynamic (purple background)
- `**WARM-UP:** ...` — daily warm-up prompt (yellow background)
- `**EXIT TICKET:** ...` — daily exit ticket (green background)
- `**DOK N:** ...` — Depth of Knowledge question (red label)
- `**DELIVERABLE:** ...` — student submission artifact (bold)

**Deprecated:** `> **Teacher:** "..."` teacher scripting blocks. Do NOT use in new content. Use facilitation notes in natural prose instead.

## DOCX Formatting Specs

- **Page:** US Letter, 0.75" margins (1080 DXA)
- **Font:** Arial throughout
- **Colors:** Navy (#1B2A4A) headers, Blue (#2E75B6) accents, Light Blue (#E8F0FE) H&L callouts, Yellow (#FFF8E1) warm-ups, Green (#E8F5E9) exit tickets/"I can" statements, Light Purple (#F3E5F5) eDynamic flags, Orange (#FFF3E0) verify flags
- **Title:** 32pt bold navy centered | **Subtitle:** 22pt italic gray centered
- **Info table:** 2x2 (Topic, Length, H&L Cluster, Irving ISD Pathways)
- **Flag boxes:** Colored background with bold colored label prefix
  - `[VERIFY IN H&L]` = orange bg (#FFF3E0), orange text (#E65100)
  - `[VERIFY IN eDynamic]` = purple bg (#F3E5F5), purple text (#6A1B9A)
  - `[H&L PLATFORM]` = blue bg (#E8F0FE), purple text (#7030A0)
- **Bullets:** LevelFormat.BULLET (never unicode) | **Tables:** DXA widths only, ShadingType.CLEAR
- **Python packages:** `python-docx` 1.2+, `openpyxl` 3.1+, `pyyaml` 6+

## XLSX Specs

4-tab spreadsheet rebuilt from markdown sources:
- **Tab 1 - Master Pacing Guide:** 13 columns, from `scope-and-sequence.md`
- **Tab 2 - TEKS Coverage Matrix:** 5 columns, from `resources/teks-coverage-matrix.md`
- **Tab 3 - Free Resource Directory:** 6 columns, from `resources/free-resource-directory.md`
- **Tab 4 - eDynamic Unit Map:** 6 columns, from `resources/edynamic-unit-map.md`
