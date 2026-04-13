# Curriculum Revision Plan: H&L Workbook Integration

**Created:** 2026-04-13
**Status:** In Progress
**Purpose:** Use the official Hats & Ladders and Powerskills workbooks to resolve unverified content flags and enrich facilitator guides.

---

## Reference Materials

Two official H&L workbooks were added to `cce-curriculum/resources/reference-pdfs/`:

| File | Pages | Size | Content |
|------|-------|------|---------|
| `HatsandLadders.pdf` | 282 pages | 116 MB | Full Career & College Exploration student workbook. 17 chapters covering all career clusters, activities, hat research, and powerskill lessons. |
| `Powerskills.pdf` | 221 pages | 21 MB | Supplemental Powerskills workbook. 12 standalone modules with student activities, worksheets, and discussion prompts. |

Searchable text extracts are alongside the PDFs:
- `HatsandLadders.txt` (13,472 lines)
- `Powerskills.txt` (1,456 lines)

**Important:** The H&L PDF is too large (116MB) for direct PDF reading tools. Always use the `.txt` extract for searching, or use `pdftotext -f <start> -l <end>` to extract specific page ranges. The Powerskills PDF (21MB) can be read via `pdftotext` as well.

---

## Current State of Facilitator Guides

All 36 guides exist in `cce-curriculum/guides/`. They contain flags marking unverified content:

| Flag | Count | Meaning |
|------|-------|---------|
| `[VERIFY IN H&L]` | 57 | Content assumed/guessed about H&L platform -- needs confirmation from workbook |
| `[H&L PLATFORM]` | 109 | H&L platform instructions -- some are accurate, some need enrichment with actual activity names/steps |
| `[VERIFY IN eDynamic]` | 6 | Content about eDynamic Learning -- separate from this revision |

**Total flags to resolve with the H&L workbook: ~166** (57 VERIFY + 109 PLATFORM that may need enrichment)

---

## H&L Workbook Structure (Chapter-by-Chapter)

Each career cluster chapter follows a consistent pattern:
1. **"Exploring the World of [Cluster]"** -- overview page with cluster description
2. **2-4 Named Activities** -- hands-on student activities (e.g., "Candy Conundrum", "Safety Supervisor")
3. **Powerskill Lesson** (in some chapters) -- one powerskill taught in the context of that cluster
4. **Hat Research** -- structured career research activity using H&L platform
5. **"What is Happening at NEISD?"** -- local district CTE pathway information

### Full Chapter Index

| Ch | Title | Named Activities | Powerskill | PDF Pages (approx) |
|----|-------|-----------------|------------|---------------------|
| 1 | My Career Journey | Exploring the World of Work, Meet the Career Clusters, My Building Blocks, Learning My Core Personality Type, Discovering My Work Values | Design Thinking | 1-15 |
| 2 | Agriculture, Food & Natural Resources | Candy Conundrum, Farm to Table, Ag-Tech Pest Patrol | Time Management | 16-36 |
| 3 | Architecture & Construction | Safety Supervisor, Power Pitch, Trash to Treasure, Unexpected Architecture | -- | 37-54 |
| 4 | Arts, A/V Technology & Communications | Digital Storytelling, Game On!, Creative Entrepreneurs | Attention to Detail | 55-70 |
| 5 | Business, Marketing & Finance | Marketing on the Move, Think Inside the Box, Pitching Investors | Written Communication | 71-87 |
| 6 | Education & Training | Community Classroom, Job Search, Teaching Toolbox | Leadership | 88-104 |
| 7 | Energy | Refinery Contamination, Resume Writing, Energy for Everyone | -- | 105-118 |
| 8 | Engineering | Protecting Wildlife, Mission to Mars, Infrastructure Imagination | Work Ethic | 119-136 |
| 9 | Health Science | Perfect Toothbrush, Cover Letter: The Golden Ticket, Physical Therapy in Action, Farm Fresh Express | -- | 137-157 |
| 10 | Hospitality & Tourism | Culinary Twist, Hotel Rescue, Pack Your Bags: Local Tourism Campaign | Motivation | 158-174 |
| 11 | Human Services | Stress Toolkit, Job Interviews, Practicing for a Job Interview, Get Out and Move! | -- | 175-190 |
| 12 | Information Technology | Cybersecurity in Action, Job Applications, Website Design | -- | 191-207 |
| 13 | Law & Public Service | Emergency Essentials: Kit Design, Missing Painting, Local Risk Response | Persuasion | 208-228 |
| 14 | Manufacturing | Machine Breakdown Mystery, Job References, Designing Metalworks, Task Bot in Action | -- | 229-246 |
| 15 | Transportation, Distribution & Logistics | Transportation Troubles, Delivery Connection App | Creativity | 247-265 |
| 16 | My Next Steps | Thinking About My Career Journey, Iceberg Cartoon, My Career and Course Plan, Lifestyle Snapshot, Being a Career Thinker | -- | 266-275 |
| 17 | TEKS Alignment | TEKS reference table | -- | 276-282 |

### Powerskills Workbook Index

| Module | ~Pages in PDF |
|--------|---------------|
| Introduction to Powerskills | 1-2 |
| Design Thinking | 3-4 |
| Motivation | 5-6 |
| Teamwork | 7-9 |
| Time Management | 10-12 |
| Work Ethic | 13-15 |
| Adaptability | 16-18 |
| Conflict Resolution | 19-21 |
| Giving and Receiving Feedback | 22-24 |
| Written Communication | 25-26 |
| Attention to Detail | 27-29 |
| Advocacy | 30-32 |
| Learning Agility | 33-35 |

---

## Crosswalk: H&L Chapters --> CCE Curriculum Weeks

This maps each H&L workbook chapter to the CCE week(s) where its content should be used.

| H&L Chapter | CCE Six Weeks | CCE Week(s) | Notes |
|-------------|---------------|-------------|-------|
| Ch 1: My Career Journey | 1SW | Wk 0 (Classroom Routines) | RIASEC, personality type, work values, Building Blocks. All onboarding content. |
| Ch 2: Ag, Food & Natural Resources | 3SW | Wk 1 (Vet Science), Wk 2 (Plant Science), Wk 3 (Sustainable Engineering) | Cluster tour, Candy Conundrum, Farm to Table, Ag-Tech Pest Patrol |
| Ch 3: Architecture & Construction | 5SW | Wk 1 (Architecture), Wk 2 (Civil Eng), Wk 3 (Construction), Wk 4 (HVAC/Electrical) | Safety Supervisor, Power Pitch, Trash to Treasure, Unexpected Architecture |
| Ch 4: Arts, A/V & Communications | 6SW | Wk 2 (Graphic Design/Resume) | Digital Storytelling, Game On!, Creative Entrepreneurs |
| Ch 5: Business, Marketing & Finance | 6SW | Wk 3 (Business Marketing), Wk 4 (Sales) | Marketing on the Move, Think Inside the Box, Pitching Investors |
| Ch 6: Education & Training | 6SW | Wk 1 (Education) | Community Classroom, Job Search, Teaching Toolbox |
| Ch 7: Energy | -- | Not directly mapped | No dedicated Energy week in current curriculum. Could supplement Engineering or Sustainable Eng weeks. |
| Ch 8: Engineering | 4SW | Wk 4 (Drone Engineering); 3SW Wk 3 (Sustainable Eng) | Protecting Wildlife, Mission to Mars, Infrastructure Imagination |
| Ch 9: Health Science | 2SW | Wk 3 (Nursing), Wk 4 (Dental/Billing), Wk 6 (Biomedical) | Perfect Toothbrush, Cover Letter, Physical Therapy, Farm Fresh Express |
| Ch 10: Hospitality & Tourism | 3SW | Wk 4 (Culinary/Hospitality) | Culinary Twist, Hotel Rescue, Pack Your Bags |
| Ch 11: Human Services | 3SW | Wk 5 (Cosmetology) | Stress Toolkit, Job Interviews, Get Out and Move! |
| Ch 12: Information Technology | 1SW | Wk 2-5 (Programming, CS, Tech Support, Cybersecurity) | Cybersecurity in Action, Job Applications, Website Design |
| Ch 13: Law & Public Service | 2SW | Wk 1 (Legal Studies), Wk 2 (Law Enforcement/EMT) | Emergency Essentials, Missing Painting, Local Risk Response |
| Ch 14: Manufacturing | 1SW | Wk 1 (Robotics/Manufacturing) | Machine Breakdown Mystery, Designing Metalworks, Task Bot in Action |
| Ch 15: Transportation, Dist & Logistics | 4SW | Wk 3 (Aviation), Wk 5 (Automotive), Wk 6 (Trades Capstone) | Transportation Troubles, Delivery Connection App |
| Ch 16: My Next Steps | 4SW Wk 1-2 (Career Planning, Course Mapping); 6SW Wk 6 (Capstone) | Career plan, course plan, lifestyle snapshot |
| Ch 17: TEKS Alignment | Reference | Update `teks-coverage-matrix.md` if needed |

### Powerskills --> CCE Weeks

| Powerskill Module | Where Used in CCE | H&L Chapter Context |
|-------------------|-------------------|---------------------|
| Design Thinking | 1SW Wk 0 (onboarding) | Ch 1: My Career Journey |
| Motivation | 3SW Wk 4 (Culinary) or standalone | Ch 10: Hospitality |
| Teamwork | Any collaboration week | Standalone supplement |
| Time Management | Standalone or 3SW Wk 1 (Ag) | Ch 2: Agriculture |
| Work Ethic | 4SW Wk 6 (Trades Capstone) or standalone | Ch 8: Engineering |
| Adaptability | 3SW Wk 3 (Sustainable Eng) | Standalone supplement |
| Conflict Resolution | 2SW Wk 5 (Powerskills Communication) | Standalone supplement |
| Giving & Receiving Feedback | 6SW Wk 4 (Sales/Presentations) | Standalone supplement |
| Written Communication | 6SW Wk 2 (Graphic Design/Resume) | Ch 5: Business |
| Attention to Detail | 6SW Wk 2 or standalone | Ch 4: Arts |
| Advocacy | 2SW Wk 1 (Legal Studies) | Standalone supplement |
| Learning Agility | 4SW Wk 1 (Career Planning mid-year) | Standalone supplement |

---

## Revision Workflow

### For Each Six Weeks Block (recommended order: 1SW, 2SW, 3SW, 4SW, 5SW, 6SW):

1. **Identify the relevant H&L chapters** using the crosswalk above.
2. **Extract the chapter text** from `HatsandLadders.txt` using line numbers or `pdftotext -f <page> -l <page>` for the relevant page range.
3. **Read each guide's VERIFY flags** -- `grep "VERIFY IN H&L" <guide>.md`
4. **For each flag**, find the matching content in the workbook text extract and:
   - Replace `[VERIFY IN H&L]` flags with confirmed `[H&L PLATFORM]` instructions
   - Update activity names to match the workbook exactly
   - Add specific activity steps, discussion prompts, and worksheet references
   - Enrich existing `[H&L PLATFORM]` blocks with actual workbook details
5. **Check Powerskills alignment** -- if a Powerskill is used that week, pull the actual activity steps from the Powerskills workbook.
6. **Rebuild the .docx** for any changed guides: `python3 build/build_docx.py path/to/guide.md`

### Token Management Strategy

- **Never read the full H&L PDF at once.** It's 282 pages / 13,472 lines of text.
- **Use grep on `.txt` files** to locate specific content before reading page ranges.
- **Work one six-weeks block at a time** to keep context focused.
- **The Powerskills `.txt` is small** (1,456 lines) and can be searched freely.
- **Page ranges in the H&L PDF** are documented in the chapter index above. Use `pdftotext -f <start> -l <end>` to extract only what's needed.

### Search Patterns for Common Lookups

```bash
# Find a specific activity in H&L text
grep -n -i "candy conundrum" cce-curriculum/resources/reference-pdfs/HatsandLadders.txt

# Find all content for a chapter (use line numbers from index)
sed -n '<start_line>,<end_line>p' cce-curriculum/resources/reference-pdfs/HatsandLadders.txt

# Find a powerskill module
grep -n -i "time management" cce-curriculum/resources/reference-pdfs/Powerskills.txt

# Find all VERIFY flags in a specific six weeks
grep -n "VERIFY IN H&L" cce-curriculum/guides/1sw/*.md

# Extract specific PDF pages to text for detailed reading
pdftotext -f 16 -l 36 cce-curriculum/resources/reference-pdfs/HatsandLadders.pdf -
```

---

## Files Modified by This Revision

When complete, the following will have been updated:
- All 36 guides in `cce-curriculum/guides/*/` -- VERIFY flags resolved, H&L PLATFORM blocks enriched
- `cce-curriculum/scope-and-sequence.md` -- H&L activity names corrected to match workbook
- `cce-curriculum/resources/teks-coverage-matrix.md` -- updated if Ch 17 reveals gaps
- `cce-curriculum/notes/development-notes.md` -- revision log entry added

---

## Completion Criteria

- [ ] All 57 `[VERIFY IN H&L]` flags resolved (removed or converted to confirmed `[H&L PLATFORM]`)
- [ ] All 109 `[H&L PLATFORM]` blocks reviewed and enriched with actual activity names/steps
- [ ] Powerskill modules correctly mapped and integrated
- [ ] Activity names in scope-and-sequence match workbook exactly
- [ ] TEKS alignment cross-checked against Ch 17
- [ ] All changed guides rebuilt to .docx
