# PLANNING.md — CCE Curriculum Vetting & Teacher Handoff

**Last updated:** 2026-04-14
**Purpose:** Brief a new agent (and any sub-agents it spawns) on the full state of the CCE curriculum project, the vetting work that needs to happen before tomorrow's teacher review, and the plan for the teacher presentation and feedback cycle.

This document replaces the previously-deleted `handoff-website-build.md` and `handoff-prompt.md`. If you are a new agent reading this: **start here, not with those files (they no longer exist).**

---

## 1. What This Project Is

This repo contains a full **36-week Career and College Explorations (CCE)** course curriculum for grade 7 at Bowie Middle School, Irving ISD, Texas, aligned to **TEKS §127.2 Career and College Exploration (Adopted 2023)**.

The curriculum is delivered as a static MkDocs Material website that teachers read in the browser. Each of the 36 weeks has:
- **1 weekly overview** (`overview.md`) — big picture: TEKS, vocabulary, materials, career connection, "Week at a Glance" table, assessments, differentiation
- **5 daily lesson plans** (`day1.md` through `day5.md`) — lesson overview table, warm-up, 2-3 activities with facilitation notes, exit ticket, differentiation

**216 daily files + 36 overviews + scope-and-sequence + resources = the course.**

### Platform stack
- **Hats & Ladders** (H&L) — core platform. Student workbook (282 pages, 17 chapters) + Powerskills supplement (221 pages, 12 modules). This is the spine of the content.
- **Xello** — supplemental career exploration (7th-grade task list mapped to specific weeks)
- **eDynamic Learning** — supplemental units (teacher does not yet have full platform access)
- **VILS tech** — Sphero, TinkerCAD, Canva, Glowforge, MakeCode, micro:bit, drones, LEGO — mapped week by week in the scope and sequence

### Lineage (where the curriculum came from)
1. **Original scope-and-sequence** — a 13-column spreadsheet the teacher built mapping every week to H&L cluster, activities, supplemental resources, tech integration, Xello task, eDynamic unit, TEKS codes, and notes. Lives at `cce-curriculum/scope-and-sequence.md`.
2. **Legacy facilitator guides** — 36 `.md` files in `cce-curriculum/guides/` built from the original scope-and-sequence. These had TEKS alignment, vocabulary, career connection, and lesson sequences, but used an old format with `> **Teacher:** "..."` scripting blocks and `[VERIFY IN H&L]` flags.
3. **H&L workbook integration** — The two official H&L workbook PDFs (`HatsandLadders.pdf`, `Powerskills.pdf`) were added, extracted to `.txt`, and used to resolve all 57 `[VERIFY IN H&L]` flags. Real workbook activity names and page numbers replaced guesses.
4. **Website rebuild** — Every week was rebuilt in a new two-tier format (weekly overview + 5 daily plans) for the MkDocs site. The 5SW Wk1 Architecture week was built first as the **prototype** and approved. The other 35 weeks were built against that prototype.
5. **Current state (2026-04-14):** 216 markdown files live at `docs/` covering all 36 weeks. Site builds clean (`mkdocs build --strict` — zero warnings, zero errors). Committed and pushed to a public GitHub repo (`elbrielle/cce-curriculum`) and deployed via GitHub Actions to GitHub Pages (`https://elbrielle.github.io/cce-curriculum/`).

**The curriculum has NOT been vetted by classroom teachers yet.** That is tomorrow's meeting and the reason this document exists.

---

## 2. Repo Layout (what lives where)

```
27 CCR Planning/                                 ← project root
├── CLAUDE.md                                    ← project rules (READ FIRST)
├── PLANNING.md                                  ← this file
├── README.md                                    ← quick start
├── mkdocs.yml                                   ← site config + full nav
├── GUIDE-FORMAT.md                              ← legacy docx format rules
├── PATHWAYS.md                                  ← Irving ISD CTE pathway reference
├── PLATFORMS.md                                 ← H&L / Xello / eDynamic / VILS details
│
├── docs/                                        ← THE WEBSITE (source of truth for daily plans)
│   ├── index.md
│   ├── scope-and-sequence.md
│   ├── 1sw/ … 6sw/                              ← six-weeks blocks
│   │   └── wkN-topic/
│   │       ├── overview.md                      ← weekly big picture
│   │       ├── day1.md … day5.md                ← five daily lesson plans
│   └── resources/
│       ├── teks-coverage-matrix.md
│       └── free-resource-directory.md
│
├── cce-curriculum/                              ← LEGACY / reference (do not edit for website content)
│   ├── scope-and-sequence.md                    ← master pacing guide (authoritative)
│   ├── guides/Xsw/wkN-topic.md                  ← legacy guides used as structural reference
│   ├── resources/
│   │   ├── teks-coverage-matrix.md
│   │   ├── free-resource-directory.md
│   │   ├── edynamic-unit-map.md
│   │   └── reference-pdfs/                      ← H&L workbook PDFs + .txt extracts
│   │       ├── HatsandLadders.pdf               ← 116MB, 282pp, DO NOT READ IN FULL
│   │       ├── HatsandLadders.txt               ← 13,472 lines, grep this instead
│   │       ├── Powerskills.pdf                  ← 21MB, 221pp
│   │       └── Powerskills.txt                  ← 1,456 lines
│   └── notes/
│       ├── development-notes.md
│       └── revision-plan.md                     ← H&L chapter → week crosswalk
│
├── build/                                       ← python build scripts (for legacy .docx output)
├── output/                                      ← generated artifacts (gitignored)
└── site/                                        ← built MkDocs site (gitignored)
```

**Critical distinction:** `docs/` is the website and the current source of truth for daily lessons. `cce-curriculum/guides/` is the legacy format retained for TEKS/vocabulary/structural reference only. Edits to improve the student experience go in `docs/`.

---

## 3. Format Rules You Must Follow

Before editing anything, read **`CLAUDE.md`** — it is the authoritative rulebook for this project. Key rules summarized:

- **No teacher scripting.** Never write `> **Teacher:** "..."`. Use natural facilitation prose: *"Introduce the activity by connecting X to Y. Walk students through the setup by projecting the login screen."*
- **Source-ground everything.** Every H&L activity citation must include chapter and page: `(H&L Ch 3, p. 40: "Safety Supervisor")`. Every Xello task must match the scope-and-sequence column 8 name. Every eDynamic unit must match column 9.
- **Concrete deliverables per day.** Every day ends with a specific artifact (PNG screenshot, completed worksheet, sketch, research template, 60-second pitch). Not "students explore."
- **Activity specs, not vague instructions.** "Design a building with at least 4 walls, a roof, 1 door opening, and 2 window openings. Export as PNG." Not "design a building."
- **Use `!!! tip "Facilitation Tip"` admonition blocks** for teacher guidance. Use `!!! note`, `!!! warning` as needed.
- **Use `> [H&L PLATFORM] ...` blocks** for app navigation because students use both the workbook AND the app.
- **Prototype to match:** `docs/5sw/wk1-architecture/` — overview.md + day1-5.md. Match the section order and the Lesson Overview 2-col table exactly.

---

## 4. What Vetting Tomorrow's Review Needs

Tomorrow (2026-04-15) classroom teachers will see this curriculum for the first time. Before then, we need an **internal vetting pass** so teachers are reviewing something we already believe in. The vetting covers eight dimensions. Each is a separate workstream — split them across sub-agents.

### Dimension 1 — Scope and Sequence Fidelity
**Question:** Is the website staying true to the original scope and sequence spreadsheet?

**Authoritative source:** `cce-curriculum/scope-and-sequence.md` (13 columns × 36 rows). The columns are: Six Weeks | Week | CCE Topic | H&L Cluster | H&L Specific Activities | Supplemental Resources | Tech Integration | Xello Standards | eDynamic Unit | TEKS Standards | TEKS Codes | Notes | Facilitator Guide Filename.

**Checks:**
- Does each week's `docs/Xsw/wkN-*/overview.md` cover the H&L cluster named in column 4?
- Does the week reference the specific H&L activities in column 5? (e.g., 5SW Wk1 must reference Safety Supervisor, Power Pitch, Trash to Treasure, Unexpected Architecture)
- Do tech-integration weeks actually use the tool in column 7? (e.g., 5SW Wk1 must use TinkerCAD — verified ✓ in prototype)
- Are Xello tasks from column 8 referenced in at least one day that week?
- Are eDynamic units from column 9 referenced (even if marked `[VERIFY IN eDynamic]`)?
- Flag any week where the `docs/` content drifted from the scope-and-sequence spec.

**Deliverable:** A table of 36 rows (one per week) with `[PASS / PARTIAL / DRIFT]` and a one-line reason for each non-PASS.

---

### Dimension 2 — TEKS Coverage Accuracy
**Question:** Is every week using the correct, recorded TEKS codes, and does the year-level coverage hit every required d(1)–d(8) standard?

**Authoritative source:** `cce-curriculum/resources/teks-coverage-matrix.md` + TEKS §127.2 list in scope-and-sequence column 11.

**Checks:**
- For each `docs/Xsw/wkN-*/overview.md`, cross-check the `## TEKS Alignment` section against scope-and-sequence column 11 for that row. They must match.
- Are the TEKS codes *actually demonstrated* in the daily plans? (e.g., if the overview claims `d(5)(D)` — prepare a personal budget — does at least one day include a budget deliverable? This is the most common drift.)
- Run a year-level roll-up: every TEKS code from `d(1)(A)` through `d(8)(C)` should appear in at least one week. Flag any gaps.
- Check the three previously-enriched standards: `d(3)(B)` College Credit, `d(3)(C)` College Funding, `d(3)(E)` Standardized Testing. These were flagged as needing enrichment. Confirm they now have real activities, not just mentions.

**Deliverable:** (a) TEKS coverage matrix showing every d(N)(X) standard with the list of weeks covering it. (b) A drift list — any week whose `## TEKS Alignment` claim is not actually demonstrated in the daily plans.

**Grep pattern examples:**
```
# Which weeks claim d(5)(D)?
grep -l "d(5)(D)" docs/*/*/overview.md

# Does that week actually have "budget" in a daily plan?
grep -l "budget\|Budget" docs/5sw/wk5-personal-budget/day*.md
```

---

### Dimension 3 — Activity Quality, Rigor, and Engagement
**Question:** Do the activities make sense for 7th graders, are they rigorous enough to hit DOK 2-4, and are they engaging enough to hold a room of middle-schoolers for 50 minutes?

**Rigor markers to look for:**
- Every daily plan should have a `**DOK 2:**`, `**DOK 3:**`, or `**DOK 4:**` higher-order question. DOK 1 recall is insufficient for this standard.
- Activities should require students to *produce* something (a sketch, a calculation, a design, a pitch, a worksheet) — not just read/watch.
- Source grounding: Each major activity should cite either H&L workbook (Ch N, p. X), Powerskills module, scope-and-sequence, BLS, or Irving ISD pathways.

**Engagement markers to look for:**
- Warm-ups should be genuine hooks, not vocabulary quizzes. Good: *"It's July in Texas. Your air conditioning breaks at 2 AM when it's 95° outside. How much would you pay to fix it right now?"* Bad: *"Define HVAC."*
- Variety across the 5 days: direct instruction, hands-on, research, partner work, presentation.
- Use of students' real local context (DFW, Irving ISD, Cardwell/Ratteree pathways) where possible.

**Grade-level appropriateness:**
- Text density: daily plans should be scannable by a teacher during planning, not academic papers.
- Vocabulary: introduce technical terms with brief definitions; do not assume prior knowledge.
- Reading level: aim for grade 6-8 Lexile for student-facing prompts.

**Deliverable:** A three-column review table by week — `Rigor: 1-5 | Engagement: 1-5 | One specific concern or strength`. Focus attention on the outlier low scorers.

---

### Dimension 4 — Differentiation and Scaffolding
**Question:** Does every daily plan have usable scaffolding for students who struggle, meaningful extensions for students who finish early, and real language support for ELL students?

**Checks:**
- Every `dayN.md` has a `## Differentiation` section with `**Support:**`, `**Extension:**`, and `**ELL:**` bullets. Flag any that are missing a bullet or use a template placeholder.
- Is Support actually scaffolded or just "give them the answer key"? Good support reduces cognitive load (pre-filled rows, paired work, simplified worksheet). Bad support eliminates the learning.
- Is Extension meaningful or just "do the same thing twice"? Good extension deepens the thinking (research a second city, redesign based on feedback, compare pathways). Bad extension pads time.
- ELL language support should include the **Spanish translations** for the day's key vocabulary AND one structural accommodation (bilingual handout, paired with bilingual peer, visual reference card).

**Deliverable:** A list of daily plans whose differentiation is thin or template-y, with a suggested rewrite for each.

---

### Dimension 5 — Timing Feasibility
**Question:** Do the activity timings actually add up to a 50-minute period, and do they leave room for transitions and the unexpected?

**Check:** For each `dayN.md`:
- Add up the minute tags across `Warm-Up`, all Activities, and `Exit Ticket`.
- Total should equal 48-52 minutes (50-min period with slight flex).
- Warm-up should be 5-7 minutes maximum.
- No single activity should exceed 25 minutes without a clear checkpoint or transition.
- Exit ticket should be 3-5 minutes — not 0, not 10.

**Grep pattern:**
```
# Get all the time tags for a week
grep -E "\([0-9]+ min\)" docs/5sw/wk2-civil-engineering/day*.md
```

**Deliverable:** A list of any daily plans whose timing adds to <45 or >55 minutes. For each, suggest which activity to trim or extend.

---

### Dimension 6 — Teacher Autonomy (Not Over-Scripting)
**Question:** Does the curriculum give teachers structure without dictating their classroom culture?

**This is critical feedback from the teacher.** Classroom culture varies by teacher, school, and student population. A curriculum that scripts every word kills teacher judgment, but one that is too vague leaves new teachers without enough support.

**Red flags to check for:**
- Any remaining `> **Teacher:** "..."` scripting blocks (should be zero — grep for them).
- Overly prescriptive facilitation notes that dictate tone or specific phrasing a teacher must use.
- Rigid group sizes, seating arrangements, or procedural choreography that would not work in every classroom.
- Activities that only work with a specific technology setup.

**Green flags to preserve:**
- Facilitation notes that describe WHAT happens (student task, deliverable spec) and WHY (learning goal, connection to career).
- `!!! tip "Facilitation Tip"` blocks that give classroom experience ("if a student struggles with X, prompt them with Y"). These are advice, not commands.
- Variety of grouping suggestions (pairs, small group, whole class) so teachers can adapt.

**Grep patterns:**
```
# Should return ZERO results
grep -rn "> \*\*Teacher:" docs/

# Find facilitation notes that sound like scripts (patterns with "say to students")
grep -rn "say to students\|tell students that\|explain that" docs/
```

**Deliverable:** A list of facilitation notes that are too prescriptive, with proposed rewrites. And a "teacher autonomy statement" that can go in a new `docs/resources/teacher-guide.md` explaining the intent.

---

### Dimension 7 — Assessment Coherence (Formative → Summative)
**Question:** Do the formative assessments during the week build toward the summative assessment at the end of the week? Are the summatives across the six weeks building toward the capstone?

**Checks per week:**
- Does each day's exit ticket measure something the summative will also measure?
- Do the formative deliverables (sketches, worksheets, drafts) feed into the summative (presentation, final product, portfolio)?
- Are TEKS codes in the Formative Assessment section a subset of the Summative Assessment TEKS?
- Is the summative actually a summative (requires synthesis) or just the Day 5 activity relabeled?

**Checks across the year:**
- Does 1SW Wk0 establish the Climber Profile / RIASEC data that later weeks can reference?
- Do 4SW Wk1-2 Career Planning weeks use the career favorites accumulated in 1SW-3SW?
- Does the 6SW Wk6 Capstone actually synthesize data from all 36 weeks?

**Deliverable:** A week-by-week coherence check and a cross-year flow diagram showing how Climber Profile → Career Favorites → Career Plan → Capstone progresses.

---

### Dimension 8 — Video Integration
**Question:** Are videos integrated where they would strengthen the lesson, and are they either free/public resources or linked from H&L/Xello?

**Current state:** The curriculum references H&L cluster tour videos and "From the Field" interviews because the H&L workbook says to use them. Some weeks also reference Code.org, PBS Design Squad, FAA Drone Zone, Ted-Ed, and CareerOneStop career videos.

**Checks:**
- Every week that benefits from a visual hook should have at least one video reference on Day 1 (cluster tour) or a key activity day.
- Video references should be **real, accessible URLs** — not "find a video about X" placeholders.
- Videos should not be over-used as filler. No more than ~10 minutes of video per day; the rest should be active student work.
- Any video linked externally must be age-appropriate and district-filter friendly (the district blocks some `github.io` pages, so external links need the same scrutiny).

**Grep pattern:**
```
# Find all video and YouTube references
grep -rn "youtube\|vimeo\|video\|[Vv]ideo" docs/ | head -50
```

**Deliverable:** A list of weeks that would benefit from adding a video, and any existing video references that should be swapped for higher-quality alternatives.

---

## 5. Token-Efficient Editing Heuristics

**Do not re-read every document for every change.** The curriculum is ~216 files × 80-150 lines = ~25,000 lines. Reading everything eats context and slows work. Use these patterns instead:

### Search, don't scan
- **Use `Grep` (ripgrep)** for all content searches. `Grep` can find patterns across all 216 files in under a second and returns just the matches.
- **Use `Glob`** to find files by name pattern. Never use `find` or `ls` via Bash.
- **Use `output_mode: "files_with_matches"`** as the default — only switch to `content` when you need to see the surrounding line.

### Audit before editing
- For format audits, grep for structural markers, don't read files:
  ```
  grep -l "## Warm-Up" docs/*/*/day*.md                     # every daily plan should have this
  grep -c "^## " docs/5sw/wk1-architecture/day1.md          # count section headers
  grep -rn "^# Day" docs/                                    # get every Day 1-5 title
  grep -rn "> \*\*Teacher:" docs/                            # scripting violations (should be 0)
  grep -rn "\[VERIFY IN" docs/                               # unresolved flags
  ```
- For outlier detection, use `wc -l` to find files that are far from the median:
  ```
  wc -l docs/*/*/day*.md | sort -n | tail -20    # longest files
  wc -l docs/*/*/day*.md | sort -n | head -20    # shortest files
  ```
- Only read the outliers. Sample the middle randomly if you need a quality baseline.

### Edit surgically, not holistically
- **Use the `Edit` tool with `old_string` / `new_string`.** The tool only sends the diff, not the whole file. For bulk renames, use `replace_all: true`.
- **Never `Read` then `Write` the whole file** unless you are creating a new file or intentionally replacing >80% of it.
- For bulk edits across many files (e.g., "change every instance of 'Cyber Safety Creator' to 'Cybersecurity in Action'"), consider a small python or bash script committed to `build/` as a one-time migration rather than chaining N Edit calls.

### Delegate in parallel when the task is N-at-a-time
- If you need to audit all 36 weeks along one dimension (e.g., timing), launch **one sub-agent per six-weeks block** with a focused lens. They work in parallel, return findings, and you consolidate.
- Each sub-agent should receive a self-contained prompt — the minimum files to read, the specific question, the expected deliverable format. Do not expect sub-agents to share context with each other.
- Use `run_in_background: true` for sub-agents and the file-count polling pattern (see session history) if you need progress updates without reading their transcripts.

### Verify before committing
- Before `git commit`, always run:
  ```
  python3 -m mkdocs build --strict      # catches broken links and missing files
  git diff --stat                        # sanity-check scope of changes
  grep -rn "> \*\*Teacher:" docs/        # confirm no scripting regressions
  ```
- Never `git push --force` without explicit user permission.

### What NOT to do
- **Do not read `HatsandLadders.pdf` directly.** It is 116MB / 282 pages. Use `HatsandLadders.txt` (13,472 lines) with `Grep`, or extract a specific page range with `pdftotext -f <start> -l <end> HatsandLadders.pdf -`.
- **Do not reopen the original planning/scope-and-sequence spreadsheet.** The markdown version is the source of truth.
- **Do not batch more than ~10 Edit calls in a single response.** If you need more, write a script.

---

## 6. Teacher Presentation Plan (Tomorrow, 2026-04-15)

Teachers are seeing this for the first time. The goal of tomorrow's meeting is NOT to defend the curriculum — it is to let teachers pick it apart in a structured way so we can take real feedback.

### Presentation outline (45-60 min, leave time for discussion)

**Part 1 — Where this came from (8 min)**
1. The original scope-and-sequence spreadsheet — show the 13 columns on screen
2. Hats & Ladders as the spine — briefly tour the workbook Ch 3 (Architecture) as a live example
3. How the website got built from those two sources + TEKS §127.2
4. The current status: 216 daily plans, ~20,000 lines, build passes clean, live at `https://elbrielle.github.io/cce-curriculum/`
5. **Transparent caveat:** "Nothing here has been tested with students yet. Today is the first real review."

**Part 2 — How it's laid out (12 min)**
1. Six-weeks blocks → weekly overview + 5 daily plans (show folder tree)
2. Walk through ONE week end-to-end as the exemplar: **5SW Wk1 Architecture** (the prototype — safest choice)
   - Overview: TEKS, vocabulary, Week at a Glance, differentiation
   - Day 1: H&L Safety Supervisor activity
   - Day 3: TinkerCAD skill builder
   - Day 5: Presentations + Career Plan update
3. Show how source grounding works: every H&L activity cites chapter + page
4. Show the `!!! tip "Facilitation Tip"` blocks — framed as advice, not commands

**Part 3 — Decisions we made (and why) (10 min)**
Preempt the obvious questions with the rationales:
- **Why no teacher scripting?** Classroom culture varies. We describe the flow, not the lines.
- **Why two-tier (overview + daily)?** Teachers plan weekly AND day-of. Both views matter.
- **Why source-grounded to H&L?** We pay for the platform, the workbook is 282 pages, students should actually open it.
- **Why 50-minute periods?** That is Bowie's current bell schedule.
- **Why concrete deliverables?** Formative assessment needs an artifact. "Students explore" is not an exit ticket.
- **What is missing?** Teachers know. Let them tell us.

**Part 4 — Pick it apart (20+ min)**
Hand teachers the feedback form (below). Give them 15-20 min to open the website in the browser, pick a week they care about, and leave comments. Then walk the room and talk to each teacher 1:1.

**Part 5 — What happens to your feedback (5 min)**
- Every comment becomes a GitHub issue tagged by week and dimension.
- Triage happens that same week; priority fixes ship within 2 days.
- Teachers get read access to the GitHub issue tracker so they can see their feedback in the queue.
- A follow-up meeting in 1 week to review changes and collect round 2 feedback.

### Feedback form (share live at the meeting)

Use a single shared Google Doc or Form with these questions per week reviewed. Keep it short so teachers actually fill it out.

```
Teacher name (optional):
Week reviewed (Block + Week, e.g., "3SW Wk1 Vet Science"):

1. Fidelity — does this week match what the scope-and-sequence said it would cover? [yes / partial / no — explain]
2. Rigor — is the DOK level appropriate for 7th grade? [too easy / about right / too hard — explain]
3. Engagement — would your students actually do this? [yes / maybe / no — explain]
4. Timing — can you finish a day in 50 minutes? [yes / tight / no — explain]
5. Teacher autonomy — is the facilitation prescriptive or flexible? [too scripted / about right / too vague — explain]
6. Differentiation — do the scaffolds and extensions work for your students? [yes / partial / no — explain]
7. Materials — do you have access to everything listed? [yes / some / no — list gaps]
8. One thing I would change:
9. One thing I would keep exactly as-is:
10. Anything I would not teach at all and why:
```

### What to bring to the meeting
- Laptop projecting `https://elbrielle.github.io/cce-curriculum/`
- Printout of `scope-and-sequence.md` (teachers like seeing the master table)
- Printout of one exemplar daily plan (5SW Wk1 Day 1) for paper reference
- Printed copies of the feedback form OR a shared Google Doc URL ready to share
- A note about the district filter: the site is publicly accessible from home/cellular but may be blocked on district Wi-Fi; teachers may need to review from a personal device until the CIPA category is updated

---

## 7. Post-Meeting Feedback Intake Plan

1. **Collect all feedback** into a single spreadsheet or Google Doc with columns: Teacher | Week | Dimension | Feedback | Priority (P0/P1/P2) | Status
2. **Triage within 24 hours:**
   - **P0 (ship within 2 days):** factual errors, missing TEKS alignment, broken materials references, safety issues
   - **P1 (ship within 1 week):** rigor/engagement/timing fixes, differentiation improvements, activity replacements
   - **P2 (backlog):** nice-to-have enhancements, optional extensions, stylistic preferences
3. **Create a GitHub issue** for every P0/P1 item so the work is tracked and auditable
4. **Edit cycle:** use the token-efficient heuristics in Section 5 above. Batch edits by type across all weeks rather than fixing one week at a time.
5. **Ship round 2** with `git push` and automatic GitHub Pages redeploy
6. **Close the loop** by messaging teachers individually when their specific feedback has been addressed, with a link to the updated page

---

## 8. Handoff Prompt for the Next Agent

**Copy everything below the dashed line into a new Claude Code session when you want to kick off the vetting work.**

---

You are taking over a 36-week middle school Career and College Explorations curriculum project. The curriculum is built, committed, and published — but has not yet been vetted by classroom teachers. A teacher review meeting is scheduled for tomorrow and we need an internal vetting pass first.

**Read these files in parallel to get oriented:**
1. `/Users/elishalucero/Coding Projects/27 CCR Planning/PLANNING.md` — the full project handoff, vetting plan, teacher meeting plan, and token-efficient editing heuristics. **Start here.**
2. `/Users/elishalucero/Coding Projects/27 CCR Planning/CLAUDE.md` — the project rules (format, writing style, source grounding).
3. `/Users/elishalucero/Coding Projects/27 CCR Planning/cce-curriculum/scope-and-sequence.md` — the authoritative master pacing guide.
4. `/Users/elishalucero/Coding Projects/27 CCR Planning/docs/5sw/wk1-architecture/overview.md` — the prototype weekly overview.
5. `/Users/elishalucero/Coding Projects/27 CCR Planning/docs/5sw/wk1-architecture/day1.md` — the prototype daily plan format.

**Your job is to run the vetting pass described in `PLANNING.md` Section 4.** There are 8 dimensions to check:
1. Scope and sequence fidelity
2. TEKS coverage accuracy
3. Activity rigor and engagement
4. Differentiation and scaffolding quality
5. Timing feasibility (50-min periods)
6. Teacher autonomy (not over-scripting)
7. Assessment coherence (formative → summative → capstone)
8. Video integration

**Strategy — split the work across parallel sub-agents:**
- Launch one sub-agent per dimension, or bundle dimensions by six-weeks block if that fits the data better
- Each sub-agent gets a focused prompt, a narrow reading list, and a specific deliverable format
- Use the token-efficient heuristics in `PLANNING.md` Section 5 — grep before reading, edit surgically, never re-read the whole file for a small change
- Consolidate sub-agent findings into a single vetting report at `cce-curriculum/notes/vetting-report.md`
- Flag anything that needs teacher judgment rather than trying to fix it yourself — teachers will see the curriculum tomorrow

**Expected deliverables at the end of the vetting pass:**
1. `cce-curriculum/notes/vetting-report.md` — 8 sections (one per dimension) with findings, severity, and recommendations
2. A list of P0 fixes ready to ship before the teacher meeting (factual errors, TEKS drift, broken references)
3. A P1 backlog for post-meeting work
4. Any pre-meeting edits committed with a clean `mkdocs build --strict`
5. A summary for the user including: what passed cleanly, what needs teacher feedback, and what you fixed preemptively

**Do not:**
- Read the full `HatsandLadders.pdf` — use `HatsandLadders.txt` with `Grep`
- Rewrite large sections of a daily plan without evidence it is broken — trust the prototype unless you can prove drift
- Add new activities or reshape timing without confirming the scope-and-sequence supports it
- Delete content just because you would write it differently — classroom teachers see it tomorrow, let them weigh in

**Current state as of handoff:**
- All 216 daily plans + 36 overviews built and live at `https://elbrielle.github.io/cce-curriculum/`
- `mkdocs build --strict` passes with zero warnings
- Git: branch `main` is clean and pushed to `elbrielle/cce-curriculum` (public repo)
- Most recent commit: `ae831be Build all 35 remaining weeks: 210 daily plans + overviews`
- Teacher meeting: tomorrow (2026-04-15)

Begin by reading the files above in parallel, then propose your vetting strategy (which dimensions you will check, which you will delegate to sub-agents, what order) before making any changes. After I approve the strategy, execute and report.
