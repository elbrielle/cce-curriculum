# CCE Curriculum Codebase

## What This Is

A 36-week Career and College Explorations (CCE) course curriculum for middle school (grades 6-8) at Bowie Middle School, Irving ISD, Texas. Aligned to TEKS §127.2 Career and College Exploration (Adopted 2023). The curriculum uses Hats & Ladders as the core platform, supplemented by Xello, eDynamic Learning, and VILS technology integration.

## Repo Structure

```
27 CCR Planning/                       ← project root (this directory)
├── CLAUDE.md                          ← you are here
├── GUIDE-FORMAT.md                    ← markdown template + formatting rules for facilitator guides
├── PATHWAYS.md                        ← Irving ISD CTE pathway reference data
├── PLATFORMS.md                       ← platform descriptions (H&L, Xello, eDynamic, VILS)
│
├── cce-curriculum/                    ← the markdown curriculum (source of truth)
│   ├── scope-and-sequence.md          ← master pacing guide (13-column table, 36 rows)
│   ├── guides/
│   │   ├── 1sw/                       ← 1st Six Weeks: IT / Manufacturing
│   │   │   ├── wk0-classroom-routines.md
│   │   │   ├── wk1-robotics-manufacturing.md
│   │   │   ├── wk2-programming-it.md
│   │   │   ├── wk3-computer-science-it.md
│   │   │   ├── wk4-tech-support-it.md
│   │   │   └── wk5-cybersecurity-it.md
│   │   ├── 2sw/                       ← 2nd Six Weeks: Law / Health Science
│   │   │   ├── wk1-legal-studies.md
│   │   │   ├── wk2-law-enforcement-emt.md
│   │   │   ├── wk3-nursing-health-science.md
│   │   │   ├── wk4-dental-medical-billing.md
│   │   │   ├── wk5-powerskills-communication.md
│   │   │   └── wk6-biomedical-health-science.md
│   │   ├── 3sw/                       ← 3rd Six Weeks: Ag / Hospitality / Entrepreneurship
│   │   │   ├── wk1-vet-science.md
│   │   │   ├── wk2-plant-science.md
│   │   │   ├── wk3-sustainable-engineering.md
│   │   │   ├── wk4-culinary-hospitality.md
│   │   │   ├── wk5-cosmetology.md
│   │   │   └── wk6-entrepreneurship.md
│   │   ├── 4sw/                       ← 4th Six Weeks: Career Planning / Aviation / Trades
│   │   │   ├── wk1-career-planning.md
│   │   │   ├── wk2-course-mapping.md
│   │   │   ├── wk3-aviation.md
│   │   │   ├── wk4-drone-engineering.md
│   │   │   ├── wk5-automotive.md
│   │   │   └── wk6-trades-capstone.md
│   │   ├── 5sw/                       ← 5th Six Weeks: Architecture / Construction / Finance
│   │   │   ├── wk1-architecture.md
│   │   │   ├── wk2-civil-engineering.md
│   │   │   ├── wk3-construction-trades.md
│   │   │   ├── wk4-hvac-electrical-plumbing.md
│   │   │   ├── wk5-personal-budget.md
│   │   │   └── wk6-real-estate.md
│   │   └── 6sw/                       ← 6th Six Weeks: Education / Business / Capstone
│   │       ├── wk1-education.md
│   │       ├── wk2-graphic-design-resume.md
│   │       ├── wk3-business-marketing.md
│   │       ├── wk4-sales-presentations.md
│   │       ├── wk5-job-skills-mock-interview.md
│   │       └── wk6-capstone.md
│   ├── resources/
│   │   ├── teks-coverage-matrix.md    ← TEKS code → weeks covered → coverage status
│   │   ├── free-resource-directory.md ← external URLs, tools, and free resources
│   │   ├── edynamic-unit-map.md       ← eDynamic units mapped to CCE weeks
│   │   └── reference-pdfs/            ← official H&L workbook PDFs + text extracts
│   │       ├── HatsandLadders.pdf     ← 282-page student workbook (116MB, too large for direct read)
│   │       ├── HatsandLadders.txt     ← searchable text extract (13,472 lines)
│   │       ├── Powerskills.pdf        ← 221-page powerskills supplement (21MB)
│   │       └── Powerskills.txt        ← searchable text extract (1,456 lines)
│   └── notes/
│       ├── development-notes.md       ← authoring notes, flag explanations, TEKS notes
│       └── revision-plan.md           ← H&L workbook integration plan + crosswalk
│
├── build/                             ← Python build scripts for md → docx/xlsx
│   ├── build_docx.py                  ← converts guides/*.md → formatted .docx
│   ├── build_xlsx.py                  ← rebuilds scope & sequence spreadsheet
│   └── config.py                      ← shared styles, colors, fonts, page setup
│
├── output/                            ← generated files (not source of truth)
│   ├── docx/                          ← built facilitator guide .docx files
│   └── CCE_Comprehensive_Scope_Sequence.xlsx
│
├── SW1-SW6/                           ← original .docx files (reference copies)
├── CCE_Comprehensive_Scope_Sequence.xlsx  ← original spreadsheet (reference copy)
├── CCE_Curriculum_Development_Notes.docx  ← original dev notes (reference copy)
└── convert_all.py                     ← one-time conversion script (docx → md)
```

## How to Edit the Curriculum

The **markdown files in `cce-curriculum/`** are the source of truth. Edit those directly. The original `.docx` and `.xlsx` files in the root and `SW1-SW6/` are reference copies from the initial conversion and should not be edited.

Each facilitator guide follows a strict markdown template documented in `GUIDE-FORMAT.md`. Read that file before editing or creating guides.

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

### Revision Workflow (per guide)
1. Check `notes/revision-plan.md` for the H&L chapter + page range mapped to that week
2. Extract that chapter's text from the `.txt` file or via `pdftotext`
3. Resolve each `[VERIFY IN H&L]` flag with confirmed workbook content
4. Enrich `[H&L PLATFORM]` blocks with actual activity names and steps
5. Rebuild the .docx: `python3 build/build_docx.py path/to/guide.md`

## Key Conventions

### Facilitator Guide Sections (in order)
Every guide has these sections as `##` headings: Lesson Objective, Demonstration of Learning, TEKS Alignment, Materials Needed, Career Connection, Vocabulary, Bridge to Theory (Hats & Ladders), IISD Instructional Strategies, Lesson Sequence, Formative Assessment, Summative Assessment, Differentiation.

### Special Markers in Guides
These inline markers are parsed by the build script for colored formatting:
- `> **Teacher:** "..."` — teacher scripting (blue label, italic quote)
- `> [H&L PLATFORM] ...` — Hats & Ladders platform instruction (blue background)
- `> [VERIFY IN H&L] ...` — needs verification in H&L (orange background)
- `> [VERIFY IN eDynamic] ...` — needs verification in eDynamic (purple background)
- `**WARM-UP:** ...` — daily warm-up prompt (yellow background)
- `**EXIT TICKET:** ...` — daily exit ticket (green background)
- `**DOK N:** ...` — Depth of Knowledge question (red label)
- `**EDP:** ...` — Engineering Design Process step (purple italic)

### Heading Hierarchy in Lesson Sequence
- `### Day N: Title` — day heading
- `#### Activity Name (time)` — activity within a day

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
