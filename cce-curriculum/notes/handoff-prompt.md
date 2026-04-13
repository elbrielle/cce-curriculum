# Agent Handoff Prompt: Pre-Vetting Session Preparation

**Copy and paste everything below the line into a new Claude Code session.**

---

I need you to complete the pre-vetting session preparation for this CCE curriculum project. A previous agent did the following work:

1. Added two official H&L workbook PDFs to the project and extracted them to searchable `.txt` files at `cce-curriculum/resources/reference-pdfs/`
2. Resolved all 57 `[VERIFY IN H&L]` flags across all 36 facilitator guides using the actual workbook content
3. Ran a 3-part audit (format compliance, TEKS coverage, scope-sequence consistency) and created an approved execution plan

**The approved plan is at `.claude/plans/shimmering-twirling-salamander.md` -- read it first.** It has full context on what was found and what needs to happen.

**The revision plan with H&L workbook crosswalk is at `cce-curriculum/notes/revision-plan.md`.** It maps every H&L chapter to curriculum weeks and has search patterns for the workbook text files.

## What's Already Done
- All 57 `[VERIFY IN H&L]` flags resolved (0 remaining)
- PDFs moved, extracted to `.txt`, indexed
- CLAUDE.md updated with reference PDF instructions
- Revision plan and crosswalk documented

## What You Need to Do (8 Tasks, in order)

### Task 1: Sync scope-and-sequence H&L activities column (~20 rows)
The guides were updated with verified workbook content but `cce-curriculum/scope-and-sequence.md` column 5 ("H&L Specific Activities") still has old assumptions. Key fixes needed:
- 1SW Wk5: "Cybersecurity in Action interactive game" → it's a project-based activity (Cyber Safety Creator), not a game
- Any row mentioning standalone "PowerSkills module" → the workbook has NO standalone Communication, Problem Solving, or MoneySkills modules (they're individual activities spread across the Powerskills supplement)
- Any row mentioning "scenario-based game" for a cluster → check if the guide now says something different (many were corrected to reference specific workbook activities instead)
- Strategy: `grep -n "H&L PLATFORM" cce-curriculum/guides/Xsw/wkY-*.md` to see what each guide actually says, then compare to the scope-and-sequence row

### Task 2: Update scope-and-sequence filename column (36 rows)
Column 13 ("Facilitator Guide Filename") references `.docx` names like `FG_1SW_Wk1_Robotics_Manufacturing.docx`. Replace all 36 with the actual `.md` source filenames (e.g., `wk1-robotics-manufacturing.md`). These are the source of truth.

### Task 3: TEKS enrichment for d(3)B, d(3)C, d(3)E
The TEKS coverage matrix (`cce-curriculum/resources/teks-coverage-matrix.md`) marks 3 standards as NEEDS ENRICHMENT:
- `d(3)(B)` College Credit (AP/dual credit): Add DOK question + brief teacher discussion within existing Day in `4sw/wk2-course-mapping.md`
- `d(3)(C)` College Funding (FAFSA/scholarships): Add within existing Day in `5sw/wk5-personal-budget.md`
- `d(3)(E)` Standardized Testing (PSAT/SAT/ACT): Add within existing Day in `4sw/wk2-course-mapping.md`
- Must fit within existing 50-minute blocks -- no restructuring timings
- For each: update the guide's `## TEKS Alignment` section, update `teks-coverage-matrix.md` status to COVERED, update scope-and-sequence TEKS columns for those weeks

### Task 4: Add "Irving ISD Pathway:" line to 12 guides
These 12 guides in `2sw/` and `3sw/` are missing the standardized `**Irving ISD Pathway:**` bold line in their `## Career Connection` section. All other 24 guides have it. The pathway data already exists in the body text of each guide -- just format it as a bold line to match the pattern used in `1sw/`, `4sw/`, `5sw/`, `6sw/` guides. Check any `1sw/` guide for the correct format.

### Task 5: Fix 2SW Wk2 missing d(1)(B) TEKS code
`cce-curriculum/guides/2sw/wk2-law-enforcement-emt.md` covers the Law cluster but is missing `d(1)(B)` (Explore and describe CTE career clusters) from its TEKS Alignment section and from the scope-and-sequence TEKS columns for that row.

### Task 6: Deepen 4 thinnest guides
These guides have only 3-4 teacher scripts and ~169-175 lines (vs. 190+ and 6+ scripts for strong guides):
- `2sw/wk6-biomedical-health-science.md` (3 scripts, 170 lines)
- `3sw/wk2-plant-science.md` (3 scripts, 169 lines)
- `3sw/wk3-sustainable-engineering.md` (4 scripts, 175 lines)
- `3sw/wk6-entrepreneurship.md` (4 scripts, 181 lines)
Add 2-3 teacher scripts with proper `> **Teacher:** "..."` format and expand abbreviated activity descriptions. Use any `1sw/` guide as the quality reference for depth and structure.

### Task 7: Annotate 6 remaining eDynamic VERIFY flags
6 `[VERIFY IN eDynamic]` flags remain (can't resolve without platform access). Add a note to `cce-curriculum/notes/development-notes.md` listing them as known open items:
- `5sw/wk1-architecture.md` (2 flags)
- `6sw/wk1-education.md` (1 flag)
- `6sw/wk2-graphic-design-resume.md` (2 flags)
- `6sw/wk3-business-marketing.md` (1 flag)

### Task 8: Run validate + build
```bash
cd "/Users/elishalucero/Coding Projects/27 CCR Planning"
python3 build/validate.py                    # should pass clean
python3 build/build_docx.py                  # generates 36 .docx files to output/docx/
python3 build/build_xlsx.py                  # generates scope-and-sequence spreadsheet
```

## Verification Checks
After all tasks:
- `grep -rc "VERIFY IN H&L" cce-curriculum/guides/` returns 0
- `grep -c "NEEDS ENRICHMENT" cce-curriculum/resources/teks-coverage-matrix.md` returns 0
- `python3 build/validate.py` passes clean
- Build scripts complete without errors

## Important Notes
- Read `CLAUDE.md` and `GUIDE-FORMAT.md` before editing any guides
- The H&L workbook text extracts at `cce-curriculum/resources/reference-pdfs/HatsandLadders.txt` and `Powerskills.txt` are searchable with grep -- use them for any content questions
- eDynamic is supplemental (teacher doesn't have full access right now)
- Everything must fit within existing 50-minute class periods
- Don't restructure the scope-and-sequence order -- follow the original curriculum structure
