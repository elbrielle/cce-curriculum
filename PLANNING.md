# PLANNING.md — CCE Curriculum Vetting & Teacher Handoff

**Last updated:** 2026-04-14
**Purpose:** Brief a new agent (and any sub-agents it spawns) on the full state of the CCE curriculum project, the vetting work that needs to happen before tomorrow's teacher review, and the plan for the teacher presentation and feedback cycle.

This document replaces the previously-deleted `handoff-website-build.md` and `handoff-prompt.md`. If you are a new agent reading this: **start here, not with those files (they no longer exist).**

---

## 1. What This Project Is

This repo contains a full **36-week Career and College Explorations (CCE)** course curriculum for grade 7 across **Irving ISD VILS Labs**, Texas — a new prep deployed in VILS classrooms district-wide, distinct from the existing Engineering VILS curriculum class. Aligned to **TEKS §127.2 Career and College Exploration (Adopted 2023)**.

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

### Dimension 9 — Skill-Before-Enforcement (Taught Before Tested)
**Question:** When the curriculum instructs a teacher to enforce a "real-world" discipline (hard time cuts, interview formalities, attire rules, deadline holds), has that skill actually been named, modeled, or communicated to students *before* the enforcement moment?

**Why this dimension exists.** Enforcement without prior instruction is surprise punishment, not pedagogy. A teacher who cuts a 7th grader off mid-sentence during their first-ever 4-minute team presentation has not taught pacing. The same instruction in 6SW Wk4 Sales/Presentations — after students have drilled timed pitches with verbal warnings on Days 3 and 4 — is defensible reinforcement. Same words, very different pedagogical meaning. The clinical pass did not catch this; it caught scripting, DOK, timing, differentiation, but not whether an enforcement was earned.

**Red flags to check for:**
- Facilitation tips that instruct "cut students off mid-sentence" or "no exceptions" enforcement of a format rule that has not been drilled earlier in the week.
- Hard professional-discipline instructions appearing in **content weeks** (drones, automotive, HVAC, real estate) without a prior student-facing warning.
- Appeals to "real world" authority ("Real conferences cut speakers off", "Real interviews end when time is up") as a substitute for a concrete curriculum tie.
- Facilitation tips that sound muscular but make the first encounter with a skill a failure moment for the student.

**Green flags to preserve:**
- Explicit student-facing warnings *before* the enforcement moment: "At 4 min we will cut you off — practice ending at 3:45."
- References to a prior activity where the skill was drilled ("uses the Powerskills training from Day 2").
- Enforcement only in weeks where the skill is in the Lesson Objective or DOL.
- Opt-outs named for students who haven't had the prior drill (written pitches, small-group instead of whole-class).

**Companion — declarative fluff patterns:**
Phrases like "This is real X discipline", "This builds real Y", "This is what real Z do", and "This is the most important skill they will learn" are filler. They do not help the teacher. Either replace with a concrete downstream tie ("prepares students for Day 5 presentations") or delete.

**Grep patterns:**
```
# Hard-enforcement language
grep -rn "mid-sentence\|no exceptions\|cut .* off at\|Cut .* off\|hard cutoff" docs/

# "Real world" appeals that substitute for pedagogy
grep -rn "This is real\|This builds real\|This is what real\|Real conferences\|Real interviews" docs/

# For each hit, verify: does the week's overview.md name the enforced skill
# in Lesson Objective or DOL? Do Days 1-4 include explicit practice of the
# skill? Are students warned in advance in the facilitation notes?
# If No to all three, the enforcement is surprise discipline — either soften
# (schedule-fairness framing) or move the hard cut to a skill week.
```

**Deliverable:** A list of facilitation tips that enforce a skill before it has been taught, with proposed fixes (remove the enforcement, add a prior-day warning, or soften to schedule-fairness).

---

## 5. Token-Efficient Editing Heuristics

**Load `cce-curriculum/notes/editing-heuristics.md` before any substantive editing session.** That file is the authoritative protocol: decision table ("before editing X, read Y"), paste-ready grep recipes, "never do X without reading more" rules, escalation criteria.

**Patterns specific to this vetting work:**

- **Search, don't scan.** Use `Grep` (ripgrep) and `Glob`, never `find`/`ls`/`cat`. Default `output_mode: "files_with_matches"`; switch to `content` only for surrounding context.
- **Audit structural markers, not file bodies.** `grep -l "## Warm-Up" docs/*/*/day*.md`, `grep -rn "> \*\*Teacher:" docs/` (scripting, must be 0), `grep -rn "\[VERIFY IN" docs/` (unresolved flags). For outlier detection use `wc -l docs/*/*/day*.md | sort -n` and read only outliers.
- **Edit, don't rewrite.** `Edit` with `old_string`/`new_string` sends only the diff. Read + Write the full file only for new files or >80% replacements. For bulk prose patterns across many files, prefer a one-shot Python script in `build/` (see `build/em_dash_sweep.py`) over chaining N Edit calls — lesson 18.
- **Delegate in parallel for N-at-a-time audits.** One sub-agent per six-weeks block with a self-contained prompt (files to read, specific question, deliverable format). Do NOT delegate small grep sweeps or targeted edits — lesson 10.
- **Never read `HatsandLadders.pdf` directly** (116MB / 282 pages). Use `HatsandLadders.txt` with `Grep`, or `pdftotext -f <start> -l <end>` for a specific chapter.
- **Before committing:** `python3 -m mkdocs build --strict` + `git diff --stat` + the full preservation loop in §10. Never `--force`, never `--no-verify`.

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
- **Why 50-minute periods?** That matches the current IISD middle school bell schedule used across the VILS labs.
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

## 8. Handoff Prompt — Teacher/Writer Instinct Review

**This is different from the clinical pass in §4.** The clinical pass (commit `d207fb1`, frozen in `vetting-report.md`) answered "do timings add up, is differentiation present, is DOK written somewhere." This pass answers "will a 20-minute activity actually take 20 minutes with real students? Will a warm-up land with a 7th grader in 2nd period on a Tuesday? Does variety hold across 5 days or does the week collapse into five days of read-and-type?" Grep can't do it — you have to read a week the way a teacher reads it.

### How to run it — two sub-agents in adversarial dialogue

**Agent 1 — Teacher Implementer.** Simulates a VILS lab teacher at an Irving ISD middle school with 60 minutes to decide whether to run the week Monday. Doesn't know H&L intimately. Lobs concerns, doesn't fix anything. Read-only (curriculum + S&S + `HatsandLadders.txt` extracts + `resources-status.md` + PLANNING.md; never the 116MB PDF directly).

**Instincts to apply:** Will this activity fit the time (can 24 7th-graders realistically set up + execute + clean up in 20 min, not just "do the minutes add up")? Will the warm-up actually land (no vulnerable-share too early, no required context students lack)? Is the 5-day variety real or does the week secretly become five days of read-and-type? Do the transitions work (partner share → silent individual work in 30 seconds implied)? Does the deliverable spec match the time (4 walls + roof + door + 2 windows in 20 min on first-time TinkerCAD)? Is the facilitation realistic (account creation with 24 Chromebooks on school Wi-Fi)? Where are the likely blow-ups?

**Agent 2 — Curriculum Writer.** Triages each concern as Fix / Defend / Escalate. Bound by: no inventions (every activity traces to H&L workbook chapter/page, Powerskills module, S&S col 5, BLS/CareerOneStop, or Irving ISD pathways); no new activities, reshaped timing, or TEKS changes without S&S support; no scripting; preserve Support/Extension/ELL + Spanish vocab; 45–55 min/day at H2 header level; `mkdocs build --strict` must still pass. Writer proposes exact `old_string`/`new_string` edits for Fix rows.

**Triage rules:** **Fix** when valid + resolvable without changing activity purpose or scope (extend by 3 min, add transition sentence, sharpen a warm-up, clarify deliverable). **Defend** when the concern is opinion not defect — write one sentence of intentionality. **Escalate** when a real classroom is needed to resolve or S&S alignment is at stake.

### Parent agent workflow

1. **Pick 3–5 weeks max.** Never all 36 in one pass. Use the Tier 1–3 queue in §10. First priorities historically: 1SW Wk0 (campus-routine breathing room), 5SW Wk1 Architecture (prototype — if it drifts, everything inheriting from it drifts), writer-reach weeks (2SW Wk5, 3SW Wk3, 6SW Wk5).
2. **Per week:** spawn Teacher Implementer → get concern list → spawn Curriculum Writer with the list + non-negotiables → get triage table → you make final call → apply Fix rows with `Edit` → leave Defend/Escalate rows in the report.
3. **Consolidate** per-week results into `cce-curriculum/notes/instinct-review.md`.
4. **Verify** with the preservation loop in §10.
5. **Commit surgically** — one commit per week, message explaining week + concerns + fixes + escalations.

### Guardrails

- **No rewrites.** >15 lines touched in a single day file = redesign, not fix → escalate.
- **No invented activities or imported warm-ups.** Stay grounded in H&L + supplemental materials.
- **No touch to frozen clinical outputs** (`vetting-report.md`, P0 commit `d207fb1`).
- **When to run:** after the first teacher-meeting feedback round, before assigning to a new cohort, after a six-weeks block gets substantive edits, whenever 5SW Wk1 changes (all 35 others inherited from it).

### Sub-agent boilerplates (paste-ready)

**Teacher Implementer prompt:**

```
You are a 7th-grade VILS lab teacher at an Irving ISD middle school. You just received a new CCE course curriculum and you have 60 minutes to decide whether you can teach {week path} starting Monday morning. You do not know Hats & Ladders deeply. You are reading the curriculum through the lens of "will this actually work with my real students."

```
You are a 7th-grade VILS lab teacher at an Irving ISD middle school. You just received a new CCE course curriculum and you have 60 minutes to decide whether you can teach {week path} starting Monday morning. You do not know Hats & Ladders deeply. You are reading the curriculum through the lens of "will this actually work with my real students."

Read:
- docs/{block}/{week}/overview.md
- docs/{block}/{week}/day1.md through day5.md
- 5SW Wk1 Architecture (overview + day1) as the prototype reference
- PLANNING.md §3 (format rules)
- docs/resources/resources-status.md (what's missing)

Apply the teacher-instinct checks in PLANNING.md §8 (fit-the-time, warm-up landing, real variety, transitions, deliverable realism, facilitation realism, likely blow-ups). Do NOT edit anything. Do NOT apply clinical checks (timings adding up, DOK markers present, scripting regressions) — those are already verified in cce-curriculum/notes/vetting-report.md.

Return a concern list in this format:

## Week: {week path}

### Concerns
1. **[{day}: {activity}]** — {concrete concern}. {What you think a real classroom will actually experience vs. what the plan says.} Cite the specific file:line.
2. ...

Be specific. "This activity might run long" is useless; "On day 3 Activity 2 the TinkerCAD skill builder gives 4 skills in 10 minutes but students will spend 8 of those minutes logging in on the first day — leaves 2 minutes for 4 skills" is useful.

Budget: read ~6 files (1 overview + 5 days + 1 prototype for reference). Return under 600 words.
```

**Curriculum Writer prompt:**

```
You are the curriculum writer who built {week path} in the CCE Curriculum. A teacher has reviewed your week and lobbed a concern list. Your job is to triage each concern: Fix, Defend, or Escalate.

Non-negotiables:
- Every activity must trace to H&L workbook (chapter + page), H&L Powerskills (module), scope-and-sequence, BLS/CareerOneStop/Code.org, or Irving ISD pathways. No inventions.
- Timing at H2 activity-header level must stay in 45-55 min per day.
- Every day must keep its DOK 2-4 marker, Support/Extension/ELL differentiation bullets, and Spanish vocabulary pairs.
- No teacher scripting. No "> **Teacher:" blocks.
- mkdocs build --strict must still pass after your edits.

Read:
- docs/{block}/{week}/overview.md
- docs/{block}/{week}/day1.md through day5.md
- cce-curriculum/scope-and-sequence.md (the row for this week)
- cce-curriculum/resources/reference-pdfs/HatsandLadders.txt (grep the relevant chapter; never read PDF directly)
- PLANNING.md §3 (format rules) and §5 (token-efficient editing)

For each concern, return a row in this format:

| # | Concern summary | Triage | Response | Proposed edit (for Fix only) |
|---|-----------------|--------|----------|------------------------------|
| 1 | {1-line paraphrase} | Fix | {why valid + what to change} | File: {path}, old_string: {exact string}, new_string: {exact string} |
| 2 | {...} | Defend | {1-sentence justification of current choice} | — |
| 3 | {...} | Escalate | {why this needs a real teacher to resolve} | — |

If a Fix row's edit touches more than ~15 lines of a single file, downgrade it to Escalate — that's a redesign, not a fix.

Budget: ~20 tool calls. Return the table only, no preamble.
```

---

## 9. Resource Backlog (slides, worksheets, CFAs, teacher edition)

The **daily plans describe the flow and facilitation** of each week, but a turnkey teacher experience also needs:

- **Presentation slide decks** (per week or per day) for projecting warm-ups, vocabulary, activity directions, and exit tickets
- **Student worksheets** that are not photocopiable from the H&L workbook (e.g., Transferable Skills Matrix, Skilled Trades Comparison, Personal Budget Template, Capstone presentation rubric)
- **Common Formative Assessments (CFAs)** at the end of each six-weeks block measuring TEKS mastery for that block
- **Teacher edition / answer keys** for worksheets and CFAs
- **Substitute plans** per week

These are tracked as a living checklist on the main site at [`docs/resources/resources-status.md`](https://elbrielle.github.io/cce-curriculum/resources/resources-status/) so every teacher who opens the curriculum can see what's built, what's partial, and what's still to be authored. When you notice a resource that's missing while teaching, log it there (or open a GitHub issue tagged `resource-backlog`).

**Scope rule:** video integration is explicitly deferred and out of scope until after the first round of teacher feedback — per team direction on 2026-04-14 — to avoid shoehorning videos that don't fit the instructional flow.

**Priority order for backlog resources (working assumption until teacher feedback changes it):**
1. Student worksheets for the highest-stakes summatives (6SW Wk6 Capstone rubric, 4SW Wk2 Career Plan, 5SW Wk5 Budget) — these are the artifacts teachers will be most frustrated improvising
2. Presentation slide decks for the prototype week (5SW Wk1 Architecture) as the format reference, then the other weeks
3. CFAs for 1SW and 6SW blocks first (mid-point + end of year), then fill in the middle blocks
4. Teacher edition / answer keys once worksheets exist

This ordering is a working assumption. Teacher feedback tomorrow will change it.

---

## 10. Session Log & Next-Agent Handoff

### Current state (updated 2026-04-14 evening)

`main` HEAD: `38ba01b` (PLANNING §10 session log for em dash sweep). Working tree may have uncommitted prune-pass edits. `gh-pages` HEAD: `2287a17` (pre-em-dash-sweep — not pushed this session). Live site: <https://elbrielle.github.io/cce-curriculum/latest/>, versioned via mike with `teacher-meeting-2026-04-15` as the preserved milestone. **14 of 36 weeks instinct-reviewed, 22 remaining.** Track B paused until after the teacher meeting tomorrow (2026-04-15). Today's work: Wk0 compression + mike deploy + em dash sweep + reference-doc prune.

---

### Recent sessions (most recent first)

**2026-04-14 evening — reference-doc prune.** This session. Collapsed §10 session logs (deleted 326-line pasted em dash handoff kept "for history" + triple-duplicate Wk0 headers), compressed 17 lessons to one-liners + added lessons 18-20 from em dash work, tightened §5 and §8 to point at `editing-heuristics.md` and `instinct-review.md` rather than duplicate them. PLANNING.md roughly halved. Prep for teacher meeting 2026-04-15.

**2026-04-14 afternoon — em dash + AI cliché sweep (`c2d94e1`, `38ba01b`).** Retroactively applied memory `feedback_prose_style.md` Rule 1 to pre-existing content. Bulk pass via `build/em_dash_sweep.py` (4-5 regex patterns for bullet glossaries, parentheticals, period splits, TEKS refs) + targeted fixup subagent for comma splices and heading regressions. **Em dashes: 2,283 → 195 (91.5% removal)** — all 195 remaining are load-bearing (85 H1 + 83 H2/H3 headings + 27 prose keeps like school-name parentheticals). Cliché counts barely moved and that's correct — most flagged hits were load-bearing (`vital signs` medical term, `hone` real skill-drill verb, `My Career Journey` artifact name). ~5 actual decorative clichés resolved. All 6 preservation checks clean. Lessons 18-20 below.

**2026-04-14 morning — Wk0 compression + mike versioned docs (`32c21e6`, `f3cf47e`, `9a2a68b`, `5f8f8db`).** Compressed 1SW Wk0 to 3 core days + 2 flex days per teacher mandate ("better to make teachers adapt in that they need to pad and elongate rather than feel rushed"). Day 1 (Flex: Lab Routines) + Day 2 (Core A: H&L Setup + RIASEC) + Day 3 (Core B: Work Values + Building Blocks) + Day 4 (Core C: My Career Journey Reflection, summative moved from old Day 5) + Day 5 (Flex: Catch-Up + Your Choice). Xello Wk0 quizzes moved from core to Day 5 flex with `[VERIFY]` flag — district requirement unclear, teacher meeting question. Downstream audit confirmed 4SW Wk1 and 6SW Wk6 don't consume Wk0 Xello output, so safe to move. **Flex-day structural convention established:** flex-day files use H2 option headers WITHOUT `(N min)` parentheticals so the timing-sum regex skips them (guarded by `[ -n "$s" ]`). Reusable for any future buffer-week compression. Same morning: mike 2.2.0 switchover for versioned docs (gh-pages from scratch, `/latest/` + `/teacher-meeting-2026-04-15/` milestone, Material theme version dropdown enabled, GitHub Pages flipped to `legacy` / `gh-pages` branch). Old deep-link URLs without `/latest/` prefix now 404 (deferred redirect fix).

**2026-04-14 night — pattern retirement + pathway audit + Track B #14 (`40bb868` → `17f8758`, ~25 commits).** Three user-feedback rounds in one long night: (a) 6SW Wk6 reframe tightening (em dashes, length, dead intro paragraphs → memory `feedback_prose_style.md` Rules 1-4, commits `7ccdce2` + `e153c09` + `bd119fd`); (b) **Teacher Prep Checklist pattern RETIRED across 16 weeks** (commit `40bb868`) — pattern was net-negative, content-specific authoring info preserved as Materials annotations where needed (lesson 17); (c) **PATHWAYS.md definitive rewrite from Irving ISD canonical CTE pages + 18-file pathway re-audit** — old PATHWAYS.md had fabricated Singley pathways (Real Estate, Sales Mgmt, Administrative Mgmt, Entrepreneurship — all actually at MacArthur/Nimitz). Key corrections: Real Estate at MacArthur; MacArthur ACE school with 4 sub-pathways; Cardwell vs. Ratteree distinction restored; HVAC/Electrical/Plumbing reframed as "no current Irving ISD home" (5SW Wk4 Day 4 restructured); Medical Billing reframed as not-a-current-pathway in 2SW Wk4. New editing-heuristics rule 11 + memory Rule 6: **never cite an Irving ISD pathway without verifying against the canonical website.** Track B: 5SW Wk6 Real Estate instinct-reviewed (4 Fix / 3 Defend) — shipped with wrong pathway initially, fixed in the audit. A4 PII paper-artifact sweep applied to 1SW Wk3. Day-file lesson 17 sweep (5 meta-commentary hits).

**2026-04-14 afternoon — Track B session 4 (teacher-meeting-prep, 3 weeks + 6SW Wk6 reframe) (`043f718` → `01627b1`).**

| Commit | Week | Concerns → Result |
|---|---|---|
| `043f718` | **6SW Wk4 Sales/Presentations** (Dim 9 skill-week pass) | 10 → 8 Fix / 2 Defend. Student-facing announcement of Friday cap rule closed the "earned enforcement" gap. |
| `2f2a1af` | **5SW Wk2 Civil Engineering** (writer-reach yellow flag) | 8 → 6 Fix / 2 Defend. Writer-reach hypothesis partly falsified — H&L Ch 8 anchor is real. **Lesson 13 reframe** on Day 5 bridge-challenge public ranking. |
| `a9ec5a9` | **2SW Wk1 Legal Studies** (calibration week) | 6 → 3 Fix / 3 Defend. Low-drift as expected. Day 3 retimed 55→50. **Lesson 13 reframe** on Day 4 AI-ethics debate. |
| `01627b1` | **6SW Wk6 Capstone** (structural reframe, not instinct review) | TEKS audit confirmed every code has upstream coverage → rewrote buffer admonition in Wk0-flexibility-plan style. **Introduced lesson 14** (fully-optional-week reframe). |

**2026-04-14 earlier evening — Track B instinct review, 3 weeks (`002b955` → `3948d98`).**

| Commit | Week | Result |
|---|---|---|
| `002b955` | **2SW Wk5 Powerskills-Communication** (slot week, blank S&S Topic) | 8 → 6 Fix / 2 folded |
| `5275409` | **6SW Wk5 Job Skills/Mock Interview** (heaviest TEKS week) | 6 → 6 Fix. A4 PII pattern introduced. |
| `3948d98` | **4SW Wk2 Course Mapping** (d(8)(C) artifact week) | 5 → 2 Fix / 3 Defend. Clinical catch: Day 5 was summing to 53 min, trimmed A1 10→7 to restore 50. |

**Earlier 2026-04-14 sessions (breadcrumbs; full prose in `instinct-review.md` + commit log):**

| Session | Commits | Headline |
|---|---|---|
| Morning — instinct review + Wk0 flex framework | `6745afa` → `435f837` | 1SW Wk0, 5SW Wk1, 4SW Wk1, 6SW Wk6. 42 concerns → 20 Fix / 11 Defend / 11 Escalate. Wk0 Flexibility Framework `!!! abstract` verb menu accepted after prescriptive-playbook first pass rejected. |
| Afternoon — prose + math + Dimension 9 | `cd2ea60` → `bfb4cac` | Presentation math sweep DONE. Dimension 9 (Skill-Before-Enforcement) added to §4 + editing-heuristics rules 8-9. First retroactive Dim 9 sweep. |
| Late afternoon — Track A sweeps | `fc1c4dd`, `fb08bde` | Teacher Prep Checklist A1 propagation to 9 tech-tool weeks (later RETIRED — see night session). Directive→Suggestion verified no-op. 2 Dim 1 tech-tool drifts → escalation queue. |

**Pattern-propagation status:** ✅ presentation math; ❌ Teacher Prep Checklist (retired); ⏭️ Directive→Suggestion (no-op); ✅ Dim 9 declarative fluff; ⏳ A4 PII paper-artifact (partial — 1SW Wk3 + 6SW Wk5 applied, more candidates).

---

### Weeks still to instinct-review (22 of 36 remaining)

**Reviewed (14):** 1SW Wk0, 4SW Wk1, 5SW Wk1, 6SW Wk6, 2SW Wk5, 6SW Wk5, 4SW Wk2, 5SW Wk5, 3SW Wk3, 2SW Wk4, 6SW Wk4, 5SW Wk2, 2SW Wk1, 5SW Wk6.

**Tier 1 — next session priority (lesson 13 / recent-edit / tech-dependency risk):**

1. **2SW Wk2 Law Enforcement/EMT** — lesson 13 watchlist (criminal-justice content, same failure mode as 2SW Wk1 AI ethics). Cross-cluster (Law + Health Science EMT). Singley anchor.
2. **3SW Wk5 Cosmetology** — lesson 13 watchlist (body image, beauty standards). Ratteree anchor. Day 3 route table just touched for Ratteree naming but not instinct-reviewed.
3. **5SW Wk4 HVAC/Electrical/Plumbing** — Day 4 restructured during pathway audit (post-HS apprenticeship research). Needs fresh pass to verify activity flow.
4. **4SW Wk5 Automotive** — Day 4 retitled during pathway audit (Cardwell/Ratteree → Ratteree only). Needs fresh pass.
5. **3SW Wk6 Entrepreneurship** — MacArthur + Cardwell anchors. Check for activity overlap with 2SW Wk5 Powerskills + 6SW Wk4 Sales pitch activities.

**Tier 2 — secondary content weeks:** 2SW Wk3 Nursing, 2SW Wk6 Biomedical, 3SW Wk1 Vet Science, 3SW Wk2 Plant Science (lesson 13 risk: ag labor + food deserts), 3SW Wk4 Culinary, 4SW Wk3 Aviation, 4SW Wk4 Drone, 4SW Wk6 Trades Capstone, 5SW Wk3 Construction, 6SW Wk1 Education, 6SW Wk2 Resume (**PII risk** — apply 1SW Wk3 / 6SW Wk5 pattern), 6SW Wk3 Business/Marketing.

**Tier 3 — likely stable (1SW IT block):** 1SW Wk1 Robotics, Wk2 Programming, Wk3 CS/IT, Wk4 Tech Support, Wk5 Cybersecurity. **1SW Wk3 Day 3 has PII fixes from `55986e8` that have not been instinct-reviewed** — pull forward if slack.

**Budget:** 3-5 weeks per session. ~7-8 sessions to finish. Track B is the default for every session until done. Rotate weeks if one turns out clean under instinct review.

---

### Escalation queue (decisions needing a human, not an edit)

- **1SW Wk0 Day 3 conceptual density** — should Building Blocks move to Day 4?
- **1SW Wk0 artifacts "not yet built"** in `resources-status.md` — Lab Safety Contract template, My Career Journey handout, Building Blocks word bank
- **1SW Wk0 cluster posters + Xello quiz names** — district verification needed
- **Xello Wk0 district requirement** — Xello moved from core to Day 5 flex with `[VERIFY]`. Is Wk0 onboarding district-required? If yes, S&S col 8 update; if no, keep as flex.
- **5SW Wk1 Day 5 eDynamic Unit 3.1** — district verification needed
- **4SW Wk1 Day 3/4 `[VERIFY IN Xello/eDynamic]`** — Quick Sims "The Real Game", Unit 8.1
- **4SW Wk1 early-week formative checkpoint** — Day 2 should verify Day 1 output before proceeding?
- **6SW Wk6 Days 3/4 co-facilitator staffing** — district admin/counselor/second teacher for the 4 capstone presentation periods?
- **6SW Wk6 Day 5 H&L persistence mitigation** — "pull out Wk0 folder if H&L is unavailable" note?
- **1SW Wk3 Sphero tech-tool drift** (A1) — S&S col 7 says "RVR+" but implementation uses paper wireframing + emerging tech research. Reinstate or update S&S?
- **3SW Wk6 Glowforge tech-tool drift** (A1) — S&S col 7 says "Glowforge: Cut logo" but week is paper investor pitch. Reinstate or update S&S?
- **Buffer-week intent vs. implementation** — 4SW Wk1 and 4SW Wk2 still framed as buffers with load-bearing pieces. Should they get the 6SW Wk6 fully-optional treatment? Blocked by d(8) structural risk below.
- **d(8)(A)/(B)/(C) structural buffer-week risk** — every d(8) week is a buffer (4SW Wk1, 4SW Wk2, 6SW Wk6). If a teacher loses both STAAR-season and end-of-year buffers, d(8) is uncovered. "Content cannot move between weeks" rule blocks the obvious fix. Options: (a) accept risk + communicate, (b) redesign 4SW buffers to keep d(8) compact, (c) accept some students may not get d(8).
- **Curriculum-density pattern** — several reviewed weeks feel rushed because all H&L + all Xello + all eDynamic + all TEKS were implemented at full fidelity. Root-cause decision ("what should we CUT from H&L default") is not Claude's call.
- **HVAC/Electrical/Plumbing "Coming 2027" campus placement** — district-wide or specific campus? 2027 timing? 5SW Wk4 Day 4 currently generic apprenticeship research with `[VERIFY]`.
- **2SW Wk4 Medical Billing home school** — Singley webpage doesn't list it but S&S week title includes it. Verify with Singley Health Sciences coordinator.

### Non-instinct-review work queued

- Resource backlog authoring (§9 + `resources-status.md`). Priority: high-stakes summative worksheets (6SW Wk6 Capstone rubric, 4SW Wk2 Career Plan template, 5SW Wk5 Budget + DFW cost reference) → presentation slides (5SW Wk1 prototype first) → CFAs (1SW + 6SW first) → teacher edition last.
- Post-teacher-meeting feedback triage (§7 P0/P1/P2, GitHub issues tagged by week + dimension).
- Clinical P1 items from frozen `vetting-report.md` (TEKS format normalization, d(4)(E) community service expansion, d(4)(D) resolution, remaining VERIFY flags).

**Out of scope per user direction 2026-04-14:** video integration. Revisit after first teacher feedback round.

---

### Non-negotiables for the next agent

- **Read before editing:** `CLAUDE.md`, `PLANNING.md §4 Dimensions 1-9`, `PLANNING.md §8 instinct-review protocol`, `cce-curriculum/notes/editing-heuristics.md`, `cce-curriculum/notes/instinct-review.md`.
- `cce-curriculum/notes/vetting-report.md` is **frozen** — never edit.
- **3-5 weeks max per instinct-review session.** Track A sweeps can touch more files because each edit is small.
- **≤15 lines per day file per edit.** More = redesign = escalate.
- **No new activities.** Stay grounded in H&L workbook + Powerskills + S&S col 5 + BLS + Irving ISD pathways.
- **No scripting** (`> **Teacher:` stays at 0 globally).
- **No declarative fluff.** "This is real X", "This builds real Y", "Real conferences cut speakers off", "most important skill they will learn" — all banned. Rule 9 in editing-heuristics.md.
- **No surprise discipline.** Never add or keep a hard-enforcement facilitation tip unless the week teaches the skill AND students are warned in advance. Rule 8 in editing-heuristics.md + Dimension 9 in §4.
- **Preserve Support / Extension / ELL + Spanish vocab pairs** on every daily plan.
- **Timing 45-55 min** at H2 activity-header level. **Never edit the `(N min)` parenthetical** unless it's a minute-count change (lesson 12).
- **No em dashes in teacher-facing `docs/` body prose** (memory `feedback_prose_style.md` Rule 1; retroactively applied 2026-04-14 in commit `c2d94e1`). H1/H2 titles and quoted attribution blocks are fine. Rule does NOT apply to PLANNING.md, CLAUDE.md, or notes files — those are developer-facing.
- **Irving ISD pathway claims must be verified against the canonical website**, never trusted from PATHWAYS.md alone (memory Rule 6 + editing-heuristics rule 11).
- **Never touch Wk0 Day 2-5 data-seeding activities** (RIASEC, Work Values, Building Blocks, Career Journey reflection) or their downstream consumers at 4SW Wk1 / 6SW Wk6 without reading how the chain fits together.
- **After every edit batch, run the preservation loop.** All six checks below must be clean before committing.
- **No `--no-verify`, `--force`, or any flag that skips hooks.** Fix the underlying issue.
- **No push without explicit user permission.** Exception: user says "AFK, do me proud" → operate autonomously including push.
- **End-of-session:** update §10 Current state + add a new recent-session bullet. Keep it short — full detail lives in commits and `instinct-review.md`.

---

### Lessons learned

Read carefully before editing. Each lesson is a rule with a one-sentence rationale. Full context in the commits referenced or in `instinct-review.md`.

1. **Verb menu > prescriptive playbook** for flexibility framing. Use load-bearing/flex split + 4-verb menu (cut, compress, substitute, skip). No "Scenario A / Scenario B" constructions. Rejected first-pass: `46e19f7`. Accepted: `435f837`.
2. **Name load-bearing vs. flex explicitly.** Teachers can route around the flex stuff with campus knowledge.
3. **Buffer weeks need explicit flex framing.** When S&S Topic is empty/sparse/supplemental-only, the week is a buffer — add flex admonition naming what can be cut if periods are lost. Buffers: 1SW Wk0 (`!!! abstract` full Flexibility Framework), 4SW Wk1-Wk2 (`!!! note` buffer), 6SW Wk6 (`!!! abstract` fully-optional — see lesson 14).
4. **Admonitions > dense prose** for important advisory content. `!!! abstract | warning | tip | note`. 15+ lines of advisory → wrap it.
5. **Language softening without timing softening is incomplete.** When you soften a directive, check whether the time allocation needs to soften too.
6. **Cross-week data dependencies are silent until they break.** Wk0 seeds Climber Profile → 4SW Wk1 / 6SW Wk6 consume it. Whenever a week references something from an earlier week, verify the earlier week explicitly preserves it.
7. **Presentation math almost never works without adjustment.** (student count × per-student minutes) ≤ (activity budget − feedback − transition). Pattern: `!!! warning` naming the math + three compression options. See 5SW Wk1 Day 5, 6SW Wk6 Day 3.
8. **Clinical pass ≠ instinct pass.** Clinical checks (scripting=0, DOK, timing, differentiation) are necessary but insufficient. They can't tell you whether a week will hold a classroom. Run both.
9. **Dimension 9 — skill before enforcement.** Before adding any hard-discipline facilitation tip, verify the skill is taught that week AND students are warned in advance in the activity text. Same words in a skill week = earned enforcement; in a content week = surprise discipline.
10. **Don't over-use sub-agents.** They cost real tokens. Only spin them up for adversarial dialog where persona separation is the point, or for large mechanical passes with focused lenses. For grep sweeps, pattern propagation, targeted edits: do it directly.
11. **Check your own recent diff for the patterns you're hunting.** In `bfb4cac` a commit 30 min earlier introduced exactly the fluff being hunted. Grep your own recent diff before claiming a clean sweep.
12. **Never edit the parenthetical inside an H2 activity header unless the edit is a minute-count change.** The timing-sum regex `^## .* \([0-9]+ min\)` only matches headers ending in `(N min)` with nothing else inside. Conditional/optional language belongs in the activity body. Caught 2026-04-14 when 2SW Wk4 Day 4 silently dropped from 50→42 min after a header edit to `(8 min, optional)`.
13. **Emotional-safety reframes (student-family implication category).** Before shipping any facilitation tip, table row, or discussion prompt that categorizes careers/lifestyles/outcomes as good/bad/declining/failed, ask: *"Could a student in this class have a parent in the bad column?"* If yes, reframe as "changing" / "adapting" / "trade-off" — keep the rigor, drop the judgment. Also applies to public ranking of student work (5SW Wk2 bridge-challenge), high-stakes outcomes (5SW Wk5 negative balance), and family-criminal-justice framing (2SW Wk1 AI ethics → system-level). 4 of 6 weeks in sessions 3+4 needed one — this is systematic, not rare.
14. **Fully-optional-week reframe for buffer windows.** When a buffer window is severe (end-of-year, STAAR) AND every TEKS is upstream-covered, escalate from "buffer week with load-bearing pieces" to "fully optional week": audit every TEKS → confirm upstream home → name upstream per TEKS → `!!! abstract` Wk0-flexibility-plan style → verb menu → "zero days is fine." Soften contradictory body claims (`CAPSTONE WEEK` → `capstone pass`, `official artifact` → `polish pass`). Only valid when upstream coverage really holds — otherwise it's a scope violation. Reference: 6SW Wk6 `01627b1`.
15. **Teacher-facing prose discipline** (memory `feedback_prose_style.md` Rules 1-4). No em dashes in `docs/` body prose; admonitions ≤12 visible lines (match Wk0 profile); full-file redundancy audit after any framing change; no prescriptive playbooks. Applies to `docs/` only, not developer-facing notes. Retroactively applied to pre-existing content in commit `c2d94e1` (lesson 18).
16. **Dead intro paragraphs.** Any paragraph immediately before a bullet list / numbered list / table: ask *"if I deleted this, would teachers lose specific information the title and bullets don't already carry?"* If no, delete. Admonition titles + bullets usually carry the meaning on their own; lead-in sentences are throat-clearing.
17. **Individual week pages are operational, not self-referential** (memory Rule 5). No Teacher Prep Checklist admonitions. No platform-generic prep notes ("verify X loads," "submit IT whitelist request"). No meta-commentary ("highest-stakes week," "most print-heavy week"). Content-specific authoring info goes as short parenthetical annotations in the Materials list. Pattern RETIRED across 16 weeks in commit `40bb868`. Retroactive application is always valid — cut admonitions that violate this rule even if a prior session added them.
18. **Bulk regex is right for prose-pattern sweeps where ~90% of cases fit 4-5 predictable patterns.** The em dash sweep handoff mandated file-by-file edits and was wrong for the task — a Python script (`build/em_dash_sweep.py`) with targeted patterns + a regex-findable fixup pass produced a result indistinguishable from hundreds of manual Edits at a fraction of the token cost. **When to prefer bulk:** (a) target is mechanical, (b) most cases fit a small pattern set, (c) failure modes are greppable post-hoc. **When to prefer file-by-file:** (a) judgment depends on reading multiple sentences, (b) failure modes are subjective and ungreppable, (c) factual-content changes are possible. The em dash sweep conflated these; don't repeat the mistake.
19. **When a bulk script has a fallback rule, the fallback IS the quality ceiling.** `em_dash_sweep.py` Pattern 7 (`any remaining em dash → comma`) generated all the quality problems because it commas-spliced where period/colon was correct. A better default would re-implement rubric rules in regex — at which point you're building a parser. Pragmatic lesson: budget a fixup pass for the fallback's failures; do not try to make the fallback perfect.
20. **Raw cliché grep counts in a handoff are near-useless without per-hit classification.** The em dash handoff said "~130 AI cliché hits"; actual resolved was ~5. The remaining 125 were load-bearing (`vital signs` medical term, `hone` real skill-drill verb, `My Career Journey` artifact name). Before baking a grep count into a handoff scope claim, spot-check 20-30 sample hits and classify load-bearing vs. filler.

---

### Editing workflow

**Source of truth:** `docs/`. Path pattern: `docs/{1-6}sw/wkN-topic/{overview.md, day1.md … day5.md}`.

**Do not edit:**
- `cce-curriculum/guides/` (legacy, not wired to site)
- `site/`, `output/` (gitignored build artifacts)
- `cce-curriculum/notes/vetting-report.md` (frozen)
- Root `.docx`/`.xlsx` files (reference copies)

**Preservation loop** (run after every edit batch; all six must be clean):

```bash
cd "/Users/elishalucero/Coding Projects/27 CCR Planning"
python3 -m mkdocs build --strict
grep -rn "> \*\*Teacher:" docs/
for f in docs/*/*/day*.md; do grep -q "DOK [2-4]" "$f" || echo "MISS DOK $f"; done
for f in docs/*/*/day*.md; do
  s=$(grep -E "^## .* \([0-9]+ min\)" "$f" | grep -oE "[0-9]+ min" | awk '{s+=$1} END {print s}')
  if [ -n "$s" ] && { [ "$s" -lt 45 ] || [ "$s" -gt 55 ]; }; then echo "OUTLIER $s $f"; fi
done
grep -L "\*\*Support:\*\*" docs/*/*/day*.md
grep -L "\*\*ELL:\*\*"     docs/*/*/day*.md
grep -rn "This is real\|This builds real\|This is what real\|Real conferences\|Real interviews" docs/
```

**Commit granularity:** one commit per week reviewed, or one per targeted fix. Commit messages explain which week, top concerns, what was fixed, what was escalated. Always include the `Co-Authored-By` trailer.

**Deploy:** push to `main` → GitHub Actions runs `mike deploy --push latest` → `gh-pages` updates `/latest/`. Watch with `gh run list --limit 3` + `gh run watch <run-id>`. Verify with `curl -s https://elbrielle.github.io/cce-curriculum/latest/<path>`. Tell the user to hard-refresh (⌘⇧R). Tag milestones via Actions UI → "Run workflow" → `milestone_name` field (descriptive + dated, not versioned numerically).

**Local preview:** `python3 -m mkdocs serve` → `http://127.0.0.1:8000/`. Live-reloads on save.
