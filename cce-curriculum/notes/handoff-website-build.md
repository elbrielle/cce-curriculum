# Handoff: Complete the CCE Curriculum Website (35 remaining weeks)

## What's Done

One prototype week is fully built: **5th Six Weeks, Week 1: Architecture** (`docs/5sw/wk1-architecture/`). It has:
- `overview.md` — weekly big picture (TEKS, vocabulary, materials, career connection, "Week at a Glance" table, assessments, differentiation)
- `day1.md` through `day5.md` — daily lesson plans with facilitation notes (NO teacher scripting), H&L workbook activities as timed student tasks, Xello integration, concrete deliverables, exit tickets, differentiation

The site is configured with MkDocs Material theme (`mkdocs.yml`) and deploys to GitHub Pages via `.github/workflows/deploy-site.yml`.

## What You Need to Do

Build the remaining **35 weeks** in the same format. Each week = 1 overview + 5 daily plans = 6 markdown files in `docs/`.

## Critical Instructions

### Read These First
1. **`CLAUDE.md`** — full project context, structure, writing style rules, source grounding requirements
2. **`docs/5sw/wk1-architecture/`** — the prototype. Match this format exactly.
3. **`cce-curriculum/notes/revision-plan.md`** — H&L chapter-to-week crosswalk (which workbook chapter maps to which curriculum week, with named activities and page ranges)
4. **`cce-curriculum/scope-and-sequence.md`** — master pacing guide. Every week's row has: H&L cluster, H&L activities, supplemental resources, tech integration, Xello task, eDynamic unit, TEKS codes, and notes

### Source Grounding Rules
All content must trace to an authoritative source. Do NOT invent activities or platform features.

- **H&L Student Workbook** — searchable at `cce-curriculum/resources/reference-pdfs/HatsandLadders.txt` (13,472 lines). Cite as `(H&L Ch N, p. X)` or `(H&L Ch N: "Activity Name")`. The workbook tells students to use the H&L app (Hat Finder, Climber Profile, Building Blocks, Career Plan) — include those app instructions in `[H&L PLATFORM]` blocks because students use the app.
- **H&L Powerskills Supplement** — searchable at `cce-curriculum/resources/reference-pdfs/Powerskills.txt` (1,456 lines). Cite as `(Powerskills, p. X: "Module Name")`
- **Scope and Sequence** — `cce-curriculum/scope-and-sequence.md`, columns: H&L Activities, Xello, eDynamic, TEKS
- **Xello** — specific 7th-grade lesson/quiz names are in scope-and-sequence column 8
- **eDynamic** — unit numbers in scope-and-sequence column 9. 6 eDynamic VERIFY flags remain (listed in `notes/development-notes.md`)
- **BLS OOH** — for salary, education, and job outlook data
- **Irving ISD Pathways** — `PATHWAYS.md` for local pathway names, schools, certifications

### Writing Style (from CLAUDE.md)
- **NO teacher scripting.** Do NOT write `> **Teacher:** "..."`. Describe what the teacher does and what students do in natural facilitation language.
- **Concrete deliverables per lesson.** PNG screenshot, completed worksheet, research template, presentation outline — every day ends with a specific artifact.
- **Activity specs, not vague instructions.** Instead of "design a building," specify minimum requirements.
- **Facilitation tips** using `!!! tip` admonition blocks for teacher guidance.
- **`[H&L PLATFORM]` blocks** for platform-specific instructions — keep these for app navigation since students use both workbook AND app.
- Study the VILS reference examples in `cce-curriculum/resources/vils-reference/` for format style (NOT content).

### Workflow Per Week

1. **Read the scope-and-sequence row** for that week
2. **Find the H&L chapter** in the crosswalk (`notes/revision-plan.md`)
3. **Search the workbook text** for named activities: `grep -n -i "activity name" cce-curriculum/resources/reference-pdfs/HatsandLadders.txt`
4. **Read the existing weekly guide** (`cce-curriculum/guides/Xsw/wkN-topic.md`) — pull structural content (TEKS, vocabulary, career connection, DOL, differentiation, materials)
5. **Create `docs/Xsw/wkN-topic/overview.md`** — match the prototype overview format
6. **Create `docs/Xsw/wkN-topic/day1.md` through `day5.md`** — match the prototype daily plan format
7. **Update `mkdocs.yml`** nav section with the new week

### H&L Chapter → Week Quick Reference

| Weeks | H&L Chapter | Key Activities |
|-------|-------------|---------------|
| 1SW Wk0 | Ch 1: My Career Journey | RIASEC, Work Values, Building Blocks |
| 1SW Wk1 | Ch 14: Manufacturing | Machine Breakdown Mystery, Designing Metalworks, Task Bot in Action |
| 1SW Wk2-5 | Ch 12: IT | Cybersecurity in Action, Job Applications, Website Design |
| 2SW Wk1-2 | Ch 13: Law & Public Service | Emergency Essentials, Missing Painting, Local Risk Response |
| 2SW Wk3-4,6 | Ch 9: Health Science | Perfect Toothbrush, Cover Letter, Physical Therapy, Farm Fresh Express |
| 2SW Wk5 | Powerskills | Conflict Resolution, Giving & Receiving Feedback, Written Communication, Advocacy |
| 3SW Wk1-3 | Ch 2: Ag | Candy Conundrum, Farm to Table, Ag-Tech Pest Patrol |
| 3SW Wk4 | Ch 10: Hospitality | Culinary Twist, Hotel Rescue, Pack Your Bags |
| 3SW Wk5 | Ch 11: Human Services | Stress Toolkit, Job Interviews, Get Out and Move! |
| 3SW Wk6 | Ch 5: Business | Marketing on the Move, Think Inside the Box, Pitching Investors |
| 4SW Wk1-2 | Ch 16: My Next Steps | Career Plan, Course Plan, Lifestyle Snapshot |
| 4SW Wk3,5 | Ch 15: Transportation | Transportation Troubles, Delivery Connection App |
| 4SW Wk4 | Ch 8: Engineering | Protecting Wildlife, Mission to Mars, Infrastructure Imagination |
| 4SW Wk6 | Ch 16 + Powerskills (Work Ethic) | Career Plan wrap-up |
| 5SW Wk1-4 | Ch 3: A&C | Safety Supervisor, Power Pitch, Trash to Treasure, Unexpected Architecture |
| 5SW Wk5 | Ch 16 | Lifestyle Snapshot budgeting |
| 5SW Wk6 | Ch 5: Business | Real Estate pathway |
| 6SW Wk1 | Ch 6: Education | Community Classroom, Job Search, Teaching Toolbox |
| 6SW Wk2 | Ch 4: Arts | Digital Storytelling, Game On!, Creative Entrepreneurs |
| 6SW Wk3-4 | Ch 5: Business | Marketing on the Move, Pitching Investors |
| 6SW Wk5 | Ch 11: Human Services | Job skills activities |
| 6SW Wk6 | Ch 16: My Next Steps | Final Career Plan |

### Recommended Build Order

Work in six-weeks blocks to stay focused on one H&L chapter at a time:
1. **5SW** (4 remaining: wk2-civil-eng, wk3-construction, wk4-hvac, wk5-budget, wk6-real-estate) — already in Ch 3
2. **3SW** (6 weeks) — Ch 2, 10, 11, 5
3. **2SW** (6 weeks) — Ch 13, 9, Powerskills
4. **1SW** (6 weeks) — Ch 1, 14, 12
5. **4SW** (6 weeks) — Ch 16, 15, 8
6. **6SW** (6 weeks) — Ch 6, 4, 5, 11, 16

### Verification

After each six-weeks block:
- `python3 -m mkdocs build --strict` — site builds without errors
- All daily plans have: Lesson Overview table, Warm-Up, ≥2 activities with facilitation notes, Deliverable, Exit Ticket, Differentiation
- All H&L activities cite workbook chapter and page
- All Xello tasks match scope-and-sequence column 8
- No `> **Teacher:** "..."` scripting blocks (deprecated)

After all 36 weeks:
- `python3 -m mkdocs build --strict` passes
- `python3 build/validate.py` passes (for the legacy guides)
- `git push` triggers GitHub Pages deployment
