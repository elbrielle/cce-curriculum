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

**Authoritative editing protocol:** see `cce-curriculum/notes/editing-heuristics.md`. That doc contains the full decision table for "before editing X, read Y," paste-ready grep recipes, "never edit without reading more" rules, and escalation criteria. CLAUDE.md links to it from the "How to Edit the Curriculum" section. Load it before a substantive editing session.

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

**This handoff is DIFFERENT from the clinical vetting pass in Section 4.**

The clinical pass is **done**. Commit `d207fb1` on main shipped the P0s and `cce-curriculum/notes/vetting-report.md` documents the result. We know, with evidence, that:

- Scripting regressions = 0
- Every daily plan has a Support + Extension + ELL bullet
- Every daily plan has a DOK 2-4 marker
- Every daily plan sums to 45-55 min at the H2 activity-header level
- Assessment chain holds from Climber Profile (1SW Wk0) through Capstone (6SW Wk6)
- TEKS §127.2(d)(1)-(d)(8) all claimed in at least one week

**But clinical checks can't tell you whether the curriculum will actually hold a classroom of 7th graders.** That's the work of THIS handoff.

### What this review is for

The clinical pass answered: "Do the timings add up? Is the differentiation present? Is a DOK question written somewhere on the page?"

This review answers: "Will an activity that *claims* to take 20 minutes actually take 20 minutes with real students? Will a warm-up that's *technically* a hook actually land as a hook for a 7th grader in 2nd period on a Tuesday? Does the *nature* of the activity match the time the writer gave it? Is there enough variety across 5 days, or does the week collapse into the same activity shape repeating?"

These are instinct checks. Grep can't do them. You need to read a week the way a teacher reads it.

### How to run the review — two agents in dialogue

Spawn two sub-agents (or personas in sequence — either works) and put them in an adversarial dialogue:

#### Agent 1 — Teacher Implementer
Their job is to simulate a VILS lab teacher in an Irving ISD middle school who has just been handed this curriculum and is preparing to teach it Monday morning. They don't know H&L intimately. They have 60 minutes to read a week and decide whether they can run it.

**Their instincts to apply:**
- **Will this activity fit the time?** Not "do the minutes add up" but "can a class of 24 seventh-graders realistically set up, execute, and clean up this activity in 20 minutes?"
- **Will the warm-up actually land?** A warm-up that is technically a hook can still be a dud if the prompt requires context students don't have, or if it asks for a vulnerable share too early in the day.
- **Is the variety real?** Across 5 days, do students have different modes of engagement — direct instruction, hands-on, research, partner/small group, presentation/reflection — or does the week secretly become five days of "read something then type in the H&L app"?
- **Do the transitions work?** Activity 1 ends with a partner share; Activity 2 requires silent individual work. Can a teacher actually make that pivot in the 30 seconds implied?
- **Does the deliverable spec match the time?** "Design a building with at least 4 walls, a roof, 1 door, and 2 windows" in 20 minutes on TinkerCAD — is that realistic for students who have never used TinkerCAD before?
- **Is the facilitation realistic?** "Walk students through the setup by projecting the sign-up screen." How long does account creation actually take with 24 Chromebooks on school Wi-Fi? Is that baked into the time?
- **Where are the likely blow-ups?** What's the one thing that will take longer than planned, the one student whose question will derail the activity, the one technology dependency that will fail?

**What they produce:** a week review in natural prose with specific line:column callouts. Their job is to **lob concerns**, not fix anything. They are not allowed to edit files. They are allowed to read any file in the curriculum plus `scope-and-sequence.md`, H&L `.txt` extracts via grep, `docs/resources/resources-status.md`, and `PLANNING.md`. They are NOT allowed to read the 116MB `HatsandLadders.pdf` directly.

#### Agent 2 — Curriculum Writer
Their job is to triage each concern: **fix**, **defend**, or **escalate**.

**Triage rules:**
- **Fix** — the concern is valid and has an obvious resolution that does not change the activity's purpose or pull it off scope-and-sequence. Examples: extending a too-short activity by 3 minutes, adding a transition sentence, replacing a vague warm-up with a sharper hook of the same length, clarifying a deliverable spec. Writer must propose the exact old_string/new_string so the parent orchestrator can apply it with the `Edit` tool.
- **Defend** — the concern is the teacher's opinion, not a defect. Write one sentence explaining why the current choice is intentional. Examples: "This is a 25-minute hands-on build because the H&L workbook specifies 25 minutes; shortening breaks source grounding." "We deliberately leave the transition loose so the teacher can read the room."
- **Escalate** — the concern needs a teacher in the actual classroom to resolve, or pulls at scope-and-sequence alignment. Examples: "Students may not finish this deliverable; splitting across 2 days changes the pacing for the whole week." "This activity works in a lab with 1:1 Chromebooks but not in a shared-cart classroom."

**Writer is bound by these non-negotiables:**
- Every activity must trace to a source: H&L workbook chapter + page, H&L Powerskills module, scope-and-sequence column, BLS/CareerOneStop/Code.org/etc., or Irving ISD pathway reference. No inventions.
- No new activities, no reshaped timing, no TEKS changes, without scope-and-sequence support.
- No teacher scripting (`> **Teacher:` blocks are banned). Facilitation notes stay in natural prose.
- Every daily plan keeps Support + Extension + ELL bullets with Spanish vocabulary.
- Total weekly timing stays at 45-55 min/day at the H2 activity-header level.
- Writer's fixes must leave `python3 -m mkdocs build --strict` passing and `grep -rn "> \*\*Teacher:" docs/` returning 0.

**Writer produces:** a triage table that mirrors the Teacher Implementer's concern list, one row per concern, with the triage category (Fix/Defend/Escalate) and the specific response. For Fix rows, include the exact edit (file path, old_string, new_string).

### How the parent agent runs the dialogue

The parent agent (you, reading this handoff) is the orchestrator.

**Step 1 — Pick a week to review.** Do NOT review all 36 weeks in one pass. Pick 3-5 weeks, chosen for maximum signal:

- **FIRST PRIORITY: 1SW Wk0 Classroom Routines & Career Self-Discovery.** This is the single highest-priority week for instinct review. The original scope-and-sequence intentionally kept Wk0 light because *campus routines, lab expectations, and classroom culture are teacher- and campus-specific* — every VILS lab is different, and teachers need room to set up their own routines. The current Wk0 daily plans have a documented concern from the project owner: **some of the content does not give enough breathing time for a teacher to establish routines, and the expectations/routines are written as dictates ("do X on Day 2") rather than as suggestions teachers can adapt to their own lab culture.** When the Teacher Implementer agent reviews Wk0, pass it this specific lens in addition to the general instincts: *"Where does this week tell me HOW to run my lab instead of WHAT my students need to learn? Where does it over-fill a day that should leave room for campus-specific routine-setting?"* When the Curriculum Writer agent triages, it should prefer Fix responses that convert directives into optional suggestions (`!!! tip "Suggested Routine"` framing), compress dense content to free breathing room, and preserve the RIASEC / Work Values / Building Blocks data-seeding activities since those are the Climber Profile artifacts consumed by 4SW Wk1 and 6SW Wk6 downstream.
- **5SW Wk1 Architecture** — the prototype. If the prototype has instinct issues, so does every week built from it.
- **One week from each of the 6 six-weeks blocks** that has the most complex day-by-day activity variety. High-bar examples: 4SW Wk1 (mid-year RIASEC reconciliation — the consumer of Wk0's data), 6SW Wk6 (capstone presentations).
- **One week where the writer was most likely to reach** — e.g., 2SW Wk5 Powerskills-Communication (slot week that the writer created from a blank Topic field), 3SW Wk3 Sustainable Engineering (cross-cluster week), 6SW Wk5 Mock Interview (d(6)+d(7) heavy, thin H&L support).

**Step 2 — For each picked week, run one teacher-writer cycle:**
1. Spawn the Teacher Implementer sub-agent, feed it the week path (overview + 5 day files) and the instincts list above. Ask for the concern list.
2. Spawn the Curriculum Writer sub-agent, feed it the concern list + the same week files + the non-negotiables. Ask for the triage table.
3. Read the triage table yourself. You make the final call — the writer is advisory, not authoritative.
4. Apply the Fix rows with the `Edit` tool. Leave Defend and Escalate rows in the report.

**Step 3 — Consolidate across weeks.** Write a single report at `cce-curriculum/notes/instinct-review.md` with one section per week reviewed, each section containing: the Teacher Implementer's concerns, the Writer's triage, your decisions (Fix applied / Defended / Escalated to teacher meeting), and links to the commits that applied any Fix rows.

**Step 4 — Verify.** After every edit batch, run:
```bash
python3 -m mkdocs build --strict
grep -rn "> \*\*Teacher:" docs/              # must be 0
grep -rL "DOK [2-4]" docs/*/*/day*.md         # every file must still have a DOK 2-4
for f in docs/*/*/day*.md; do
  s=$(grep -E "^## .* \([0-9]+ min\)" "$f" | grep -oE "[0-9]+ min" | awk '{s+=$1} END {print s}')
  if [ "$s" -lt 45 ] || [ "$s" -gt 55 ]; then echo "$s $f"; fi
done                                           # must print nothing
```

**Step 5 — Commit surgically.** One commit per week reviewed is the right granularity — the commit message explains which week was reviewed, the teacher's top concerns, what you fixed, and what you escalated.

### What this review will NOT produce

- **A rewrite of any week.** If you find yourself rewriting more than ~15 lines in a single day file, stop. That's not a fix, that's a redesign. Escalate to the teacher meeting instead.
- **New activities invented from scratch.** Stay grounded in H&L + supplemental materials at all times. When in doubt, grep `HatsandLadders.txt` with line ranges.
- **New warm-ups imported from other curricula.** If a warm-up needs replacement, the new prompt must still connect to the day's activity and match its time budget.
- **Any touch to clinical pass outputs.** The vetting-report.md and the P0 commit `d207fb1` are frozen.

### Boilerplate to paste into the Teacher Implementer sub-agent

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

### Boilerplate to paste into the Curriculum Writer sub-agent

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

### When to run this review

- Before any round-2 teacher meeting after the first teacher review has surfaced feedback
- Before the curriculum is assigned to a new cohort of VILS teachers who haven't seen it yet
- When a six-weeks block has been edited substantially and needs a fresh classroom-instinct pass
- Whenever the prototype week (5SW Wk1 Architecture) is changed — all 35 other weeks inherited from it, so any structural shift there implies a re-review

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

### Current state (updated 2026-04-15 — Track B session 4, teacher-meeting-prep)

`main` HEAD: `01627b1`. Live site: https://elbrielle.github.io/cce-curriculum/. **Thirteen** weeks instinct-reviewed (**1SW Wk0**, **4SW Wk1**, **5SW Wk1**, **6SW Wk6**, **2SW Wk5**, **6SW Wk5**, **4SW Wk2**, **5SW Wk5**, **3SW Wk3**, **2SW Wk4**, **6SW Wk4**, **5SW Wk2**, **2SW Wk1**) + Dimension 9 live + six prose/sweep passes shipped + buffer-week flex admonitions on 4SW Wk1 / 4SW Wk2 + **6SW Wk6 rewritten as fully-optional week** (every TEKS upstream-covered; no unique anchors). **23 of 36 weeks still awaiting instinct review.** Clinical `vetting-report.md` remains frozen. The 2026-04-15 Track B session 4 added 3 instinct-reviewed weeks plus a structural 6SW Wk6 reframe driven by user concern that end-of-year disruption makes the capstone week unlikely to run at all. New lesson 14 added on the fully-optional-week reframe pattern. Two new escalation items surfaced: d(8) structural buffer-week risk and curriculum-density pattern — both routed to the teacher meeting 2026-04-15.

### Session 2026-04-15 Track B session 4 (teacher-meeting-prep afternoon, 3 weeks + 6SW Wk6 reframe)

Commits `043f718` → `01627b1` on `main`. Executed Track B per the §10 priority list from session 3 handoff: one dedicated Dim 9 skill-week pass (deferred from session 3), one high writer-reach yellow flag, one calibration week. Three instinct-review commits landed (22 Fix rows applied across 12 files, 7 defended, 0 escalated) plus a structural 6SW Wk6 reframe commit surfaced mid-session by user concern about buffer-week non-negotiability. Full per-week detail appended to `cce-curriculum/notes/instinct-review.md` as Weeks 11-13 + the Wk6 reframe section.

| Commit | Week | Concerns | Fixes |
|---|---|---|---|
| `043f718` | **6SW Wk4 Sales/Presentations** (dedicated Dim 9 skill-week pass) | 10 lobbed, 8 Fix (2 folded), 2 Defend | Overview: **Teacher Prep Checklist** (A5 trigger — 4 printed artifacts + Day 5 compression pre-decision + H&L access check); Day 1 tighten "exactly what real investors use" fluff → concrete Day 3 pitch tie; Day 3 Activity 1 5-team feedback compression note (one star + one wish to stay in 25-min budget); Day 3 Activity 2 **student-facing announcement** closing Activity 2 — Friday's individual cap is the same rule as team pitches (Dim 9 earned-enforcement gap closure); Day 4 Activity 2 fix "(12 min per student)" contradiction → "25 min across 3 rounds"; Day 4 Activity 2 add "Announce Day 5 format" facilitation note (cap + compression choice) before students leave Thursday; Day 5 Activity 1 tighten "every real pitch event works" fluff → concrete Day 4 announcement tie. **Defended:** Day 2 Activity 2 Powerskills 15 min (skill reused Days 3-5); vocabulary terms (Value Proposition, Pitch — both in H&L Ch 5 workbook text students read Day 1). **Dim 9 verdict:** enforcement is now genuinely earned — drilled + student-warned. |
| `2f2a1af` | **5SW Wk2 Civil Engineering** (high writer-reach yellow flag) | 8 lobbed, 6 Fix, 2 Defend (+1 TEKS-stitching note) | Writer-reach concern was partially unfounded — week IS grounded to H&L Ch 8 (Infrastructure Imagination / Los Lomas pp. 131-135). Bridge build (Days 3-4) is writer-invented EDP scaffold but Day 4 already connects it to Infrastructure Imagination explicitly. Overview: sentence stem "NEW career" → "EMERGING career" (aligns with the definition); Day 1 Activity 3 closing forward-reference linking Los Lomas report to Days 3-4 straw-bridge challenge (closes the "background only with no callback" disconnect); Day 2 Activity 2 soften gallery-walk expectation (hit 4 of 6 stations realistic for 15 min / 12 pairs); Day 2 Activity 3 BLS OOH Environmental Engineers citation grounds the three emerging categories; Day 4 Activity 2 define "failure" before testing (first visible sag OR joint separation — teacher's call final) to defuse subjective-"visible bend" argument; Day 4 Activity 2 parallel-activity note — waiting teams start Activity 3 at desks; Day 5 **emotional-safety reframe (lesson 13)** — drop "people got hurt" warm-up framing + drop "Celebration" label + "rank highest to lowest" public ranking, reframe as share-out + pattern discussion + recognize most-creative-structural-approach. **Defended:** no Ch 3 reference (Ch 8 is correct), d(3)(E) PSAT/SAT placement tenuous but engineering-scholarship tie is explicit, Day 3 bridge design 17 min tight (approval facilitation tip already handles stuck teams). |
| `a9ec5a9` | **2SW Wk1 Legal Studies** (calibration week) | 6 lobbed, 3 Fix, 3 Defend | Low-drift calibration week as expected — source grounding is strong (H&L Ch 13 anchors Days 1-2 with named activities; iCivics anchors Day 3; BLS + H&L Hat Finder anchor Day 4). Day 3 was at 55 min — Activity 1 `(10 min)` → `(7 min)` + Exit Ticket `(5 min)` → `(3 min)` trim Day 3 to 50 min matching the rest of the week (both minute-count changes, lesson 12 compliant); Day 3 Activity 1 add 60-sec vocab pre-teach for probable cause + due process + evidence before gameplay starts (previously only in Support cheat sheet); Day 4 Activity 1 add **emotional-safety framing note (lesson 13)** — reframe AI ethics debate as system-level / technology question, not about specific cases or students' families (bail amounts + recidivism framing touched family-criminal-justice territory for Irving ISD students). **Defended:** Legal Entrepreneur Card lacks named H&L Ch 13 activity (grep-verified; d(3)(I) coverage is legitimate writer reach via BLS + H&L Hat Finder self-employment data); eDynamic Unit 5.1 VERIFY block preserved per editing-heuristics rule 7; Powerskill Persuasion overview reference is a chapter-level claim, not a delivered-module claim. |
| `01627b1` | **6SW Wk6 Capstone** (structural reframe, not instinct review) | User-driven escalation mid-session | **Not an instinct review — a structural framing rewrite.** User raised concern that 6SW Wk6 is very unlikely for teachers to complete at all due to end-of-year disruption, and that the prior buffer-week admonition (which marked Day 1 Career Plan + Days 3-4 presentations as "load-bearing") contradicted that reality. Audit: every TEKS 6SW Wk6 claims has upstream coverage — d(4)(C) at 6SW Wk4 (non-buffer), d(8)(A) at 4SW Wk1, d(8)(B) at 4SW Wk1 + 4SW Wk2, d(8)(C) at 4SW Wk2. 6SW Wk6 is not uniquely load-bearing for any TEKS. Rewrote the buffer admonition in `!!! abstract` Wk0-flexibility-plan style: every TEKS explicitly named with its upstream home, verb menu (cut / compress / substitute / skip entirely), "any subset of the 5 days is fine; zero days is fine." Also softened two contradicting body claims ("This is the CAPSTONE WEEK" → "capstone pass — not the artifact week"; "official course artifact" → "capstone-week polish of an artifact already produced in 4SW Wk1-Wk2") and the Pre-Capstone Teacher Checklist intro ("highest-stakes week" → "only if you can run this week"). No day files touched. No content removed. No TEKS claims removed. Just reframed so teachers see this week as genuinely optional polish. Introduced **lesson 14** on the fully-optional-week reframe pattern. |

**All four commits passed the 6-check preservation loop:** `mkdocs --strict` clean; scripting=0; DOK 2-4 present on all 15 reviewed day files across the 3 instinct-reviewed weeks; timing sums 50/50/50/50/50 on 6SW Wk4, 5SW Wk2, 2SW Wk1 (2SW Wk1 Day 3 was brought from 55→50 by the Slot 3 fix); Support+ELL bullets preserved; Dimension 9 fluff grep = 0.

**Cross-week patterns surfaced this session:**

1. **Lesson 13 emotional-safety reframes keep triggering.** 2 of 3 weeks this session needed one (5SW Wk2 Day 5 "people got hurt" → celebration framing; 2SW Wk1 Day 4 AI ethics debate → system-level framing). Cumulative across sessions 3+4: 4 of 6 weeks. Pattern suggests this is not a rare edge case — it's a systematic blindspot in the original writing. Keep watching.
2. **Dim 9 earned-enforcement requires student-facing announcement, not just teacher drill.** 6SW Wk4 had the drill (Day 3 verbal warning + Day 4 paired practice) but never told students in their own words that Friday's cap was the same rule. Same pattern probably applies to any future skill-before-enforcement edit: verify (a) the skill is drilled AND (b) students are explicitly told the rule in advance in the activity text, not just the facilitation tip.
3. **Writer-reach hypothesis was partly falsified on 5SW Wk2.** The week was flagged high-risk based on blank S&S columns, but Teacher Implementer verified the H&L Ch 8 anchor is real and the writer-invented bridge build is explicitly connected to Infrastructure Imagination. Writer-drift correlation with S&S sparseness holds as a heuristic but isn't deterministic — weeks can be grounded even when S&S is thin if the writer found a named chapter project.
4. **Fully-optional-week reframe (lesson 14) is a new structural tool.** When a week is in a predictable-disruption window (end-of-year, STAAR, etc.) AND every TEKS it claims is covered elsewhere, the right framing is not "buffer week with load-bearing pieces" but "fully optional polish pass — name every upstream home, give a verb menu, make it explicit that zero days is fine." See the 6SW Wk6 commit `01627b1`. Similar treatment is justified for 4SW Wk1 / 4SW Wk2 IF audit shows their TEKS claims are also upstream-covered — but content-cannot-move-between-weeks rule limits how far this can go; remaining structural risk goes to the escalation queue.



| Commit | Week | Concerns | Fixes |
|---|---|---|---|
| `6812dd9` | **5SW Wk5 Personal Budget** (highest-stakes d(5)(D) summative) | 10 lobbed, 9 Fix, 1 Defend, 3 folded | Overview: **Teacher Prep Checklist** (A5 second-pass trigger) naming Personal Budget Template + DFW Cost Reference Sheet as weekend-prep + Day 4 module pre-select + H&L/CareerOneStop access checks; Summative clarified as Day 5 portfolio of 3 artifacts; Day 2 retimed 3-check protocol (8/16/24 → 5/15/22) to catch gross-to-net math errors early; Day 2 deliverable softened "all" → "all major" categories; Day 2 **emotional reframe** of negative-balance facilitation tip with explicit family-career protection ("the same career supports many real lifestyles"); Day 5 TPS "Whose budget balanced without cutting anything?" income-disparity amplifier replaced with lifestyle-focus bullet; Day 5 Activity 2 pre-identify-careers facilitation tip inside 15-min budget. **Defended:** Day 4 FAFSA walkthrough 12 min (matches d(3)(C) "identify methods" scope). |
| `a9a045f` | **3SW Wk3 Sustainable Engineering** (cross-cluster bridge, H&L Ch 2 Pest Patrol) | 8 lobbed, 8 Fix | Day 1 NASA Climate Kids district-filter fallback (NOAA + BLS Environmental Engineers); Day 2 reading time softened ("plan 4-6 min per set, slower readers skim Set 3 using bullets"); Day 3 rationale paragraph tightened 4-5 sentences → 3 trade-off-focused sentences explicitly distinct from labels; Day 3 checkpoint clipboard softened (10-12 students not all 24, Day 4 peer feedback catches the rest); Day 4 **Societal Trends reframed** to defuse Irving ISD family-job political charge — column "Declining" → "Changing or Adapting"; example rows swapped from "coal mining workers"/"field-walking crop scouts" to "traditional energy roles adding renewable skill sets"/"crop inspection shifting to drone-assisted"; family-jobs facilitation note added; Day 4 peer feedback explicit 6/6/5/3 time split; Day 4 **conceptual bridge** at Activity 2 — "the drone you designed IS a career that barely existed 20 years ago"; Day 5 eDynamic 7.1 VERIFY block expanded with concrete fallback (ag-tech company research). |
| `f856726` | **2SW Wk4 Dental/Medical Billing** (Health Science mid-cluster) | 10 lobbed, 9 Fix, 2 folded | Overview: **Teacher Prep Checklist** (A5 second trigger this session) for Day 4 ICD-10 reference sheet + 8 patient charts with concrete starting set from the 8 codes already named inline in Day 4 (J00/J20.9/J45.909/K02.9/K21.9/R07.9/R51/S52.501A) + CDC ICD-10 browser pointer + trap-code design for Round 2; Day 1 **pathway name alignment** ("Medical Billing and Coding pathway" → "Medical Billing" to match `PATHWAYS.md` canonical — Dim 1 drift closed; credential formal name preserved); Day 1 warm-up reframed from abstract "$4 billion industry" to concrete student-stakes anchor ("wrong 5-character code = $500 bill a family doesn't actually owe"); Day 2 Activity 1 explicit 5/8/5/7 time split with named pivot into Activity 2; Day 3 Activity 3 restructured from 10-min lecture → 4/3/3 intro + turn-and-talk + whole-class share (same total time, active-learning format); Day 4 Round 2 specificity scaffolding moment added (worked example before independent coding); Day 4 Round 3 marked optional in body (header preserved as `(8 min)` for regex); Day 5 Activity 1 circulation softened to 10-12 students; Day 5 Activity 3 adds 2-min Career Comparison pre-scan before writing + makes pair-read optional. **Clinical self-catch:** an initial Day 4 Round 3 header edit to `(8 min, optional)` broke the timing-regex pattern during verification (Day 4 dropped to 42 min); reverted to `(8 min)` with optionality in body only. Documented as new lesson 12. |

**All three commits passed the 6-check preservation loop** after the 2SW Wk4 regex catch: `mkdocs --strict` clean; scripting=0; DOK 2-4 present on all 15 reviewed day files; timing sums 50/50/50/50/50 on all 3 weeks; Support+ELL bullets preserved; Dimension 9 fluff grep = 0.

**Cross-week patterns surfaced this session (detail in instinct-review.md Weeks 8-10 + cross-week section):**

1. **A5 Teacher Prep Checklist pattern keeps triggering.** 2 of 3 weeks needed it (5SW Wk5 had two unbuilt printables + Day 4 module pre-select; 2SW Wk4 had Day 4 teacher-authored ICD-10 simulation materials). Both landed the admonition inline during Track B review. The remaining 26 unrevised weeks likely have a ~1-in-3 A5 rate; keep adding inline rather than running a standalone sweep.
2. **Emotional-safety reframes are a new Dim 9-adjacent category.** 5SW Wk5 Day 2 negative-balance tip + Day 5 TPS "balanced without cutting" bullet risked implicating students' family careers as failures. Same lens at 3SW Wk3 with "declining" industries. Future reviews: watch for warmth-critical moments around income, family work, immigrant status, body image, mental health. Same "don't implicate the student's family" rule.
3. **Regex-breaking header edits are a new failure mode.** Documented as lesson 12 below. Never edit the parenthetical inside an H2 activity header unless the edit is a minute-count change; conditional/optional language belongs in the body, not the header.

### Session 2026-04-14 (evening — Track B instinct review, 3 weeks)

Commits `002b955` → `3948d98` on `main`. Executed Track B per the §10 priority list: one writer-reached slot week (highest drift risk), one thin-H&L heavy-TEKS week, one d(8)(C) artifact week. Three commits landed, 14 Fix rows applied across 13 files, 3 defended, 0 escalated (escalation queue unchanged). Full per-week detail appended to `cce-curriculum/notes/instinct-review.md`.

| Commit | Week | Concerns | Fixes |
|---|---|---|---|
| `002b955` | **2SW Wk5 Powerskills-Communication** (slot week, highest writer-drift risk) | 8 lobbed, 6 Fix, 2 folded | Day 1 A3 re-time (22→25) + A4 trim (8→5) + pressure-valve tip; Day 2 mode-shift framing at healthcare role-play pivot; Day 3 cut Mobile Farmers' Market dead-preview + reframe as self-advocacy bridge into SMART goals; Day 4 simplify A3 partner logistics; Day 5 merge SMART Refinement + Reflection into single 15-min closing block; Overview: add Teacher Prep Checklist + drop "breather week" performative framing |
| `5275409` | **6SW Wk5 Job Skills/Mock Interview** (heaviest TEKS week — 6 standards) | 6 identified, 6 Fix | Overview: Teacher Prep Checklist adapted for print-heavy prep (6 printables, ~60 min authoring); Day 1 A3 "four sections"→"six parts" typo; Day 3 A1 privacy guidance (sample identity option + form shredding) + subset-scoping note resolving the 15-min-vs-30-45-min contradiction; Day 4 TEKS line: drop d(6)(C) overreach (fishbowl ≠ every-student participation); Day 5 trim "Treat this with real seriousness" lead-in (Dim 9-adjacent fluff remnant) |
| `3948d98` | **4SW Wk2 Course Mapping** (d(8)(C) artifact week) | 5 identified, 2 Fix, 3 Defend | **Clinical catch:** Day 5 was summing to 53 min — A1 Gather All the Pieces trimmed 10→7 to restore 50-min target; Overview: Teacher Prep Checklist naming the bilingual Family Career Plan Letter as a 30-45 min pre-week authoring prerequisite (not an H&L default), plus H&L Course Planner verification + eDynamic 6.2 + Texas OnCourse whitelist |

**All three commits passed the full 6-check preservation loop:** `mkdocs --strict` clean; scripting=0; DOK 2-4 present on all 15 reviewed day files; timing sums 50/50/50/50/50 on all 3 weeks; Support+ELL bullets preserved; Dimension 9 fluff grep = 0.

**Three cross-week patterns surfaced (detail in instinct-review.md):**

1. **Writer-drift correlates with S&S column 5 emptiness.** 2SW Wk5 (blank Topic field) had 8 concerns; 4SW Wk2 (tightly scoped) had 2. Weeks where S&S col 5 lists specific H&L activities need lighter instinct review; weeks where the writer reached need tighter.
2. **Teacher Prep Checklist propagation is incomplete.** Track A1 (`fc1c4dd`) used "has external tech tool" as the trigger. A second trigger is "has teacher-authored prep materials or load-bearing resources not in H&L defaults" — this session added the admonition to 3 more weeks. Future Track B reviews should keep adding it where absent.
3. **PII in paper artifacts is a pattern to watch for.** 6SW Wk5 Day 3 was the clearest case; likely exists in other weeks. Candidate for a cross-week grep in a future session: `grep -rn "legal name\|date of birth\|DOB\|home address" docs/`.

### Earlier 2026-04-14 sessions (condensed — full detail in `instinct-review.md` + `git log`)

Four prior sessions landed on `main` before the evening Track B pass. Summarized here as breadcrumbs; full prose in `cce-curriculum/notes/instinct-review.md` (morning session's 4 weeks) and in each commit's message.

| Session | Commits | Headline |
|---|---|---|
| **Morning — instinct review + Wk0 flex framework** | `6745afa` `89614f4` `f612edf` `25a60db` `bc3c757` `7d24d05` `46e19f7` `435f837` | Teacher/Writer adversarial review on **1SW Wk0**, **5SW Wk1** (prototype), **4SW Wk1**, **6SW Wk6**. 42 Teacher Implementer concerns → 20 Fix / 11 Defend / 11 Escalate. Wk0 got the `!!! abstract` Flexibility Framework (verb menu, load-bearing/flex split) after an initial prescriptive-playbook pass was rejected. Consolidated report: `cce-curriculum/notes/instinct-review.md`. |
| **Afternoon — prose + math + Dimension 9** | `cd2ea60` `b14b1d2` `95081fe` `bfb4cac` | Prose sweep (dropped AI-cliche "X is not Y — it is Z" constructions across 6 day files). Presentation math sweep DONE (all overrunning presentation days carry `!!! warning` admonitions with compression options). **Dimension 9 added to §4** (Skill-Before-Enforcement) + editing-heuristics.md rules 8 and 9. First retroactive Dim 9 sweep removed "mid-sentence cut" surprise discipline from 3 content weeks (drone / HVAC / marketing) and trimmed fluff from 3 more. |
| **Late afternoon — Track A sweeps** | `fc1c4dd` `fb08bde` | Teacher Prep Checklist propagation to 9 tech-tool weeks (A1 — `fc1c4dd`). Directive → Suggestion sweep verified as no-op after grep-sampling (A2 — "Walk students through" / "project the" are the recommended register per CLAUDE.md, not fluff). Second-pass declarative fluff trim on 3 facilitation tips (A3 — `fb08bde`). Found 2 Dim 1 tech-tool drifts (1SW Wk3 Sphero, 3SW Wk6 Glowforge) → escalation queue. |

**Pattern propagation status across all sessions (closed as of evening session):**

- ✅ Presentation math sweep
- ✅ Teacher Prep Checklist propagation (tech-tool trigger) — 9 weeks via `fc1c4dd`, + 3 more via evening session (teacher-authored-resource trigger)
- ⏭️ Directive → Suggestion — verified no-op; strike from future priority lists unless a new pattern is identified
- ✅ Declarative fluff sweep — post-sweep grep on all listed Dim 9 patterns returns 0
- ⏳ **A4 — PII paper-artifact sweep (new, surfaced in evening session 2026-04-14)** — still on the queue; no standalone sweep has been run. See "Priority order for the next session" below.
- 🔄 **A5 — Teacher Prep Checklist second-pass (teacher-authored-resource trigger)** — now being applied **inline during Track B review** rather than as a standalone sweep. Evening session added it to 3 weeks (2SW Wk5, 6SW Wk5, 4SW Wk2); 2026-04-15 session added it to 2 more (5SW Wk5, 2SW Wk4). Pattern: ~1 in 3 Track B weeks needs the admonition. Keep adding inline during review.

Every commit listed above passed the 6-check preservation loop (mkdocs --strict, scripting=0, DOK 2-4, timing 45-55, Support/ELL, Dim 9 fluff=0).

### Weeks still to instinct-review (23 of 36 remaining)

Reviewed: **1SW Wk0**, **4SW Wk1**, **5SW Wk1**, **6SW Wk6**, **2SW Wk5**, **6SW Wk5**, **4SW Wk2**, **5SW Wk5**, **3SW Wk3**, **2SW Wk4**, **6SW Wk4**, **5SW Wk2**, **2SW Wk1**.

Remaining by six-weeks block:

- **1SW:** Wk1 Robotics/Manufacturing, Wk2 Programming/IT, Wk3 CS/IT, Wk4 Tech Support, Wk5 Cybersecurity
- **2SW:** Wk2 Law Enforcement/EMT, Wk3 Nursing, Wk6 Biomedical
- **3SW:** Wk1 Vet Science, Wk2 Plant Science, Wk4 Culinary, Wk5 Cosmetology, Wk6 Entrepreneurship
- **4SW:** Wk3 Aviation, Wk4 Drone Engineering, Wk5 Automotive, Wk6 Trades Capstone
- **5SW:** Wk3 Construction, Wk4 HVAC/Electrical/Plumbing, Wk6 Real Estate
- **6SW:** Wk1 Education, Wk2 Resume, Wk3 Business/Marketing

**Priority order for the next session:**

**Track A is DONE.** All three sub-sweeps are closed. No cheap pattern-propagation sweep currently on the queue. However, the evening Track B session surfaced **two Track A candidates** that could be profitably run as bulk sweeps:

- **A4 — PII paper-artifact sweep** (new, surfaced from 6SW Wk5 review). Run `grep -rn "legal name\|date of birth\|DOB\|home address" docs/` to find other weeks where students are asked to write real PII on paper forms. Apply the 6SW Wk5 Day 3 pattern: sample-identity option + collect-and-shred guidance. Est. 3-6 weeks affected.
- **A5 — Teacher Prep Checklist second-pass propagation** (remaining gap after `fc1c4dd`). Track A1 used "has external tech tool" as the trigger; a second trigger is "has load-bearing teacher-authored resources not in H&L defaults" (e.g., printable templates, rubrics, bilingual letters, role-play cards). Evening session added the admonition to 2SW Wk5, 6SW Wk5, 4SW Wk2. Candidate weeks to check: any week with 3+ printed handouts listed in Materials but no `!!! tip "Teacher Prep Checklist"` admonition. Run `grep -rL "Teacher Prep Checklist" docs/*/*/overview.md` to find unchecked overviews, then cross-reference Materials sections.

**Track B — instinct review (default for the next session; 3-5 weeks max):**

1. **5SW Wk6 Real Estate** — Standalone real-estate week in 5SW; commission-based income is an unusual framing and should be watched under lesson 13 (emotional-safety reframes) for income-disparity risk. Low-medium drift risk but check that the Day 5 cluster wrap-up connects to the 5SW A&C cluster arc. Deferred from session 4 priority list.
2. **3SW Wk1 Vet Science** — 3SW cluster opener. S&S Topic populated, BLS-grounded, but Notes col 12 is empty. Low-risk calibration week. Deferred from session 4 priority list.
3. **6SW Wk2 Resume** — Heavy d(4)(A) coverage + likely multiple printed artifacts (resume template, cover letter template). Probable A5 Teacher Prep Checklist trigger. Watch for PII risk (legal name / address in resume drafts) — this is the same pattern as 6SW Wk5 Day 3.
4. **4SW Wk5 Automotive** — 4SW Transportation cluster; S&S populated with Xello + BLS. Low-medium drift risk; a non-buffer week in an otherwise buffer-heavy 4SW block — good calibration opportunity.
5. **5SW Wk3 Construction** — 5SW A&C cluster continuation; sister-week to 5SW Wk1 Architecture + 5SW Wk2 Civil Engineering (both reviewed). Low-medium drift risk.

**Cumulative Track B progress:** 13 of 36 weeks reviewed, 23 remaining. Average edit size per instinct-reviewed week across sessions 3+4: ~4.7 files touched, ~8-10 lines changed. At this pace, full Track B completion is ~8 more sessions of 3 weeks each.

**Track B is the default now.** If a week in the queue above turns out to already be clean under instinct review, rotate in the next week on the remaining list and keep going until budget runs out.

### Escalation queue — items needing a human decision

These came out of the morning instinct-review pass and need a teacher/curriculum-team decision, not a curriculum edit. Full detail in `cce-curriculum/notes/instinct-review.md`. Short version:

- **1SW Wk0 Day 3 conceptual density** — should Building Blocks move to Day 4?
- **1SW Wk0 artifacts marked "not yet built"** in `resources-status.md` — Lab Safety Contract template, My Career Journey handout, Building Blocks word bank
- **1SW Wk0 cluster posters + `[VERIFY IN Xello]` quiz names** — district verification needed
- **5SW Wk1 Day 5 eDynamic Unit 3.1** — district verification needed
- **4SW Wk1 Day 3/4 `[VERIFY IN Xello/eDynamic]`** — Quick Sims "The Real Game", Unit 8.1
- **4SW Wk1 early-week formative checkpoint** — should Day 2 verify Day 1 output before proceeding?
- **6SW Wk6 Days 3/4 co-facilitator staffing** — can the district commit an admin/counselor/second teacher for the 4 capstone presentation periods?
- **6SW Wk6 Day 5 H&L persistence mitigation** — should Day 5 add a "pull out Wk0 folder if H&L is unavailable" note?
- **1SW Wk3 CS/IT tech-tool drift** (found during Track A1, `fc1c4dd`) — S&S col 7 lists "RVR+ / SpheroEDU" but the week implementation uses paper wireframing + emerging tech research. Decision: reinstate Sphero in the week or update `scope-and-sequence.md` col 7 to match.
- **3SW Wk6 Entrepreneurship tech-tool drift** (found during Track A1, `fc1c4dd`) — S&S col 7 lists "Glowforge: Cut logo for clothing company" but the week is a paper investor pitch + MVP design + personal budget. Same decision: reinstate Glowforge or update S&S col 7.
- **Buffer-week intent vs. implementation (raised 2026-04-14 evening, substantially advanced in session 4)** — The original S&S left **4SW Wk1** and **4SW Wk2** light (Xello completions + eDynamic only, no new cluster) as a STAAR/testing-season buffer, and **6SW Wk6** was left entirely blank as an end-of-year-events buffer. Morning and evening sessions implemented substantive content in all three. Evening session added `!!! note "Buffer week"` flex admonitions. **Session 4 (2026-04-15) went further on 6SW Wk6 at user direction:** audited that every TEKS 6SW Wk6 claims has upstream coverage elsewhere and rewrote the admonition in `!!! abstract` Wk0-flexibility-plan style — explicit "nothing in this week is critical to year-end TEKS coverage," verb menu, "zero days is fine." Commit `01627b1`. **Still needs a human decision at the teacher meeting:** whether 4SW Wk1 and 4SW Wk2 should get the same fully-optional reframe (their current admonitions still frame them as buffers with load-bearing pieces), and the broader d(8) structural risk below.
- **d(8)(A)/(B)/(C) structural buffer-week risk (new, session 4 2026-04-15)** — Every week claiming d(8)(A), d(8)(B), or d(8)(C) is a buffer week: 4SW Wk1 (STAAR buffer, claims d(8)(A) + d(8)(B)), 4SW Wk2 (STAAR buffer, claims d(8)(B) + d(8)(C)), 6SW Wk6 (end-of-year buffer, now fully optional). If a teacher loses BOTH the STAAR-season buffer and the end-of-year buffer, d(8) is not covered anywhere in the course. The rule "content cannot move between weeks" (S&S fidelity, user direction 2026-04-15) blocks the obvious structural fix of moving d(8)(C) to a non-buffer week. **Options for the teacher meeting:** (a) accept the structural risk and communicate to teachers that 4SW buffers should be preserved for d(8) even during STAAR crunch; (b) redesign 4SW Wk1 and/or 4SW Wk2 to keep d(8) content more compact so it fits within a shortened STAAR-season schedule (a redesign is allowed under the S&S-fidelity rule as long as H&L grounding is preserved); (c) accept that d(8) may be uncovered for some students and adjust the course-completion framing accordingly.
- **Curriculum-density pattern (raised by user 2026-04-15)** — Several instinct-reviewed weeks feel rushed because all H&L pathways + all Xello completion requirements + all eDynamic supplements + all TEKS codes the S&S assigns were implemented at full fidelity. The density concentrates in writer-reach weeks (2SW Wk5 Powerskills slot week, 5SW Wk2 Civil Engineering d(3)(E) PSAT stitch, 5SW Wk5 Personal Budget with 3 unbuilt printables + FAFSA walkthrough, 2SW Wk4 Dental/Medical Billing with 45-min Day 4 prep). Track B instinct reviews have been trimming these symptomatically — emotional-safety reframes, realism-of-timing fixes, Teacher Prep Checklist admonitions — but the root-cause decision ("what should we CUT from the H&L default curriculum to make room?") is not Claude's call. Teacher meeting 2026-04-15 should decide: are there H&L pathways, Xello quizzes, or TEKS-stitching blocks that can be dropped or made optional without failing the scope-and-sequence spec?

### Non-instinct-review work still queued

- **Resource backlog authoring** — per §9 and `docs/resources/resources-status.md`. Priority: worksheets for highest-stakes summatives (6SW Wk6 Capstone rubric, 4SW Wk2 Career Plan template, 5SW Wk5 Budget + DFW cost reference), then presentation slides (start with 5SW Wk1 prototype), then CFAs for 1SW + 6SW first, then teacher edition last.
- **Post-teacher-meeting feedback triage** — when teachers surface feedback, use the P0/P1/P2 framework in §7. GitHub issues tagged by week + dimension.
- **Clinical P1 items from frozen `vetting-report.md`** — TEKS format normalization, d(4)(E) community service expansion, d(4)(D) resolution, remaining eDynamic/Xello VERIFY flags (district-dependent).

**Out of scope per user direction 2026-04-14:** video integration. Revisit after first teacher feedback round.

### Non-negotiables for the next agent

- **Read before editing:** `CLAUDE.md`, `PLANNING.md §8` (instinct-review protocol) and **§4 Dimensions 1-9** (vetting dimensions — Dimension 9 is new and catches surprise-discipline + declarative fluff), `cce-curriculum/notes/editing-heuristics.md` (decision table, grep recipes, "never do X without reading more" rules including **new rules 8 and 9**), `cce-curriculum/notes/instinct-review.md`.
- `cce-curriculum/notes/vetting-report.md` is **frozen** — never edit.
- **3-5 weeks max per instinct-review session.** Track A sweeps can touch more files because each edit is small.
- **≤~15 lines per day file per edit.** More = redesign, not fix = escalate.
- **No new activities.** Stay grounded in H&L workbook + Powerskills supplement + scope-and-sequence col 5 + BLS + Irving ISD pathways.
- **No scripting** (`> **Teacher:` stays at 0 globally).
- **No declarative fluff** — "This is real X", "This builds real Y", "Real conferences cut speakers off", "This is the most important skill they will learn" are all banned. Use concrete curriculum ties or delete. Rule 9 in editing-heuristics.md.
- **No surprise discipline** — never add or keep a hard-enforcement facilitation tip ("cut students off mid-sentence", "no exceptions") unless the week teaches the skill and students are warned in advance. Rule 8 in editing-heuristics.md + Dimension 9 in §4.
- **Preserve Support/Extension/ELL + Spanish vocab pairs** on every daily plan.
- **Timing 45-55 min** at H2 activity-header level.
- **After every edit batch, run the preservation loop:** `python3 -m mkdocs build --strict`, scripting grep, DOK preservation grep, timing sum check, Support/ELL grep. All five must be clean before committing.
- **No push without explicit user permission.** Exception: the user has said "AFK, do me proud" → operate autonomously including push. Otherwise stage + ask.
- **Never touch 1SW Wk0 Day 2-5 data-seeding activities** (RIASEC, Work Values, Building Blocks, My Career Journey reflection) or their downstream consumers at 4SW Wk1 / 6SW Wk6 without reading how the chain fits together. Dependency map in `editing-heuristics.md`.
- **Never use `--no-verify`, `--force`, or any flag that skips hooks.** Fix the underlying issue instead.
- **When ending your session, update this §10 with a fresh session log entry** so the next agent can pick up where you left off.

### Lessons learned — read carefully

1. **Verb menu > prescriptive playbook.** When a week needs flexibility, give teachers a load-bearing / flex split and a short verb menu (cut, move, compress, substitute). Do NOT write step-by-step scenario playbooks. User rejected a first-pass Wk0 Flexibility Framework in commit `46e19f7` that had 5 prescriptive scenarios; the accepted version in `435f837` is a verb menu wrapped in `!!! abstract`. If you find yourself writing "Scenario A: do X. Scenario B: do Y," stop and convert.

2. **Load-bearing vs flex.** For any flexibility framing, name what the downstream year depends on (load-bearing) and what can be cut/moved/compressed (flex). Let teachers route around the flex stuff with campus knowledge.

3. **Buffer weeks need explicit flex framing, not just Wk0.** The original scope-and-sequence spreadsheet intentionally left three weeks light as *buffers* for predictable disruptions that no curriculum can plan around: **1SW Wk0** (first-week chaos — campus events, tech-access gates, roster churn, culture-setting), **4SW Wk1–Wk2** (STAAR / state testing season — periods get pulled, shortened, or canceled), and **6SW Wk6** (end-of-year events — field day, yearbook, awards, early release). The original S&S for 4SW Wk1–Wk2 had only Xello completions + eDynamic supplements (no new cluster), and 6SW Wk6 was left entirely blank. The morning and evening sessions implemented substantive content in all three 4SW Wk1 / 4SW Wk2 / 6SW Wk6, but the *buffer-week intent from the original S&S was not forwarded into the implementations* — and the clinical vetting pass could not catch this because the S&S was the only place it was documented. Evening session closed the gap with `!!! note "Buffer week"` admonitions on those three overviews naming load-bearing vs. flex content. **Rule going forward:** when you review or create a week, check the original `cce-curriculum/scope-and-sequence.md` row. If the S&S Topic field is empty, sparse, or marked as supplemental-only, flag the implementation as a buffer week and add a flex admonition naming what can be cut if periods are lost. Wk0 got the full `!!! abstract` Flexibility Framework (verb menu + load-bearing/flex split); the other buffer weeks got the lighter `!!! note "Buffer week"` framing because the disruption pattern is different (predictable testing/events vs. unpredictable culture-setting). Do not escalate this framing further without user sign-off — the weight is calibrated to the risk.

4. **Admonitions > dense prose** for important advisory content. `!!! abstract`, `!!! warning`, `!!! tip`, `!!! note` render as visually distinct callouts in MkDocs Material. If you're adding 15+ lines of advisory content, wrap it.

5. **Language softening without timing softening is incomplete.** First Wk0 pass softened "Walk students through [rigid list]" to a Suggested Routine admonition but left the 15-min time budget intact. When you soften a directive, also check whether the time allocation needs to soften too.

6. **Cross-week data dependencies are silent until they break.** Wk0 seeds Climber Profile data. 4SW Wk1 and 6SW Wk6 consume it 18 and 36 weeks later. Wk0 never said "save this folder"; downstream weeks silently assumed it would be there. Closed by `6745afa` + `f612edf` + `25a60db`. Whenever you see a week REFERENCE something from an earlier week, check whether the earlier week explicitly instructs the teacher to preserve it.

7. **Presentation math almost never works without adjustment.** 24 students × 2-5 min > 50 min is the standard failure. The presentation math sweep (commit `b14b1d2`) closed the remaining overruns in docs/, but if you ADD new presentation activities, always verify: (student count × per-student minutes) ≤ (activity budget - feedback - transition). Pattern: `!!! warning` naming the math + three compression options (see 5SW Wk1 Day 5 and 6SW Wk6 Day 3).

8. **Clinical pass ≠ instinct pass.** Clinical checks (scripting=0, DOK present, timing sums, differentiation bullets) are necessary but not sufficient. They can't tell you whether a week will hold a classroom. The instinct pass catches things like "this warm-up asks for a vulnerable share before students know each other" or "24 TinkerCAD logins in 10 min is aspirational." Run both. Never treat a clean clinical pass as proof a week is ready to teach.

9. **Dimension 9 is the newest check.** Before adding any hard-discipline facilitation tip, verify the skill is taught that week. "Cut students off mid-sentence" in a drone engineering content week is surprise discipline. The same words in 6SW Wk4 Sales/Presentations are earned reinforcement. Same words, different pedagogy. Caught in commit `bfb4cac`. When adding new tips, check Dimension 9 first.

10. **Don't over-use sub-agents.** Each Teacher Implementer / Curriculum Writer sub-agent cycle costs real tokens. For a 4-week review pass, that's 8 agent invocations minimum. Only spin them up for the adversarial dialog where persona separation is the point. For grep sweeps, pattern propagation, and targeted edits, do the work directly.

11. **Check your own recently-added content for the patterns you're hunting.** In `bfb4cac` I caught myself: a commit 30 minutes earlier had introduced "Reinforces real presentation discipline" on 4SW Wk5 Day 5 — exactly the fluff I was being asked to hunt. If you just finished a commit and the user flags a pattern, grep your own recent diff before claiming a clean sweep.

12. **Never edit the parenthetical inside an H2 activity header unless the edit is a minute-count change.** The timing-sum preservation check in the 6-check loop uses the regex `^## .* \([0-9]+ min\)` — it matches only headers ending in `(N min)` with nothing else inside the parentheses. Adding conditional/optional language inside the tag (e.g., `## Activity 4: Coding Simulation Round 3 — Speed (8 min, optional)`) silently drops that activity from the timing sum, making the day appear 8 min short on verification. Caught in the 2026-04-15 2SW Wk4 verification step: Day 4 dropped from 50 → 42 min with no other changes. Fix: keep the header as `(N min)` and move optionality into the activity body ("Round 3 is optional — if Round 2 runs long, cut it and move to the Exit Ticket"). The regex is the contract with the verification pipeline; the header is for the contract, the body is for the nuance. Same rule for any future H2 header convention — they are automated check targets, not free-form prose.

13. **Emotional-safety reframes are a Dim 9-adjacent category.** Dim 9 catches surprise discipline + declarative fluff. A sister category is *student-family implication* — curriculum language that asks students to analyze an outcome (negative budget balance, "declining" careers, income disparities, family job loss) in a way that frames a specific student's family situation as a failure. The 5SW Wk5 "core learning moment" on negative budgets and the 3SW Wk3 "Careers Declining" column were both caught in the 2026-04-15 session. Rule: before shipping any facilitation tip, table row, or discussion prompt that categorizes careers, lifestyles, or outcomes as good/bad/declining/failed, ask "could a student in this class have a parent in the bad column?" If yes, reframe as "changing" / "adapting" / "trade-off reasoning" — keep the analytic rigor, drop the judgment. Same lens as Dim 9: don't make the first encounter with a student's own family situation a failure moment. **Session 4 addition (2026-04-15):** the pattern extends beyond career/income framing to any high-stakes outcome that can be publicly ranked. 5SW Wk2 Day 5 had a "Celebration + Team Presentations" activity that ranked bridge-build results from highest weight to lowest publicly — reframed as share-out + pattern discussion + "most creative structural approach" recognition. Same lens: don't make the first encounter with a student's own work a public failure moment. Also: 2SW Wk1 Day 4 AI ethics debate on bail/recidivism triggered the same lens — reframed as system-level/technology question, not about specific cases or students' families.

14. **Fully-optional-week reframe is a new structural tool.** The earlier "buffer week with load-bearing pieces" framing (sessions 1-3) fails when the buffer window is severe enough that the entire week is unlikely to run. The session-4 6SW Wk6 case — end-of-year chaos makes the capstone week genuinely unlikely for most teachers — required escalating the admonition from "buffer week" to "fully optional week." The correct pattern is: **audit every TEKS code the week claims → confirm each has upstream coverage elsewhere → explicitly name the upstream home per TEKS → write the admonition in `!!! abstract` Wk0-flexibility-plan style → verb menu (cut / compress / substitute / skip entirely) → "any subset of the 5 days is fine; zero days is fine."** Also soften any body claims that contradict the new framing ("official course artifact," "highest-stakes week," "CAPSTONE WEEK"). This pattern is ONLY valid when every TEKS really is covered upstream — otherwise it's a scope violation. Commit `01627b1` on 6SW Wk6 is the reference implementation. 4SW Wk1 and 4SW Wk2 are candidates for the same treatment per the escalation queue, but require user sign-off and are also blocked by the d(8) structural risk (see queue). The pattern is also applicable in reverse: when YOU review a week that reframes itself as "optional," verify the upstream coverage claim before accepting it — don't take the week's own word for it.

### Editing workflow

Source of truth for the live site: everything under `docs/`. Path pattern: `docs/{1-6}sw/wkN-topic/{overview.md, day1.md ... day5.md}`.

Do **not** edit:
- `cce-curriculum/guides/` (legacy format, not wired to the site)
- `site/`, `output/` (gitignored build artifacts)
- `cce-curriculum/notes/vetting-report.md` (frozen)
- Root `.docx` and `.xlsx` files (reference copies)

Preservation loop after every edit batch:

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
# Dimension 9 (declarative fluff)
grep -rn "This is real\|This builds real\|This is what real\|Real conferences\|Real interviews" docs/
```

All six must be clean.

Commit granularity: one commit per week reviewed, or one commit per targeted fix. Commit messages explain which week, top teacher concerns, what was fixed, what was escalated. Always include trailer `Co-Authored-By: Claude [model name and version] <noreply@anthropic.com>`.

Deploy pipeline: push to `main` → GitHub Actions → GitHub Pages. Completes in ~40-60 sec. Watch with `gh run list --limit 3` / `gh run watch <run-id> --exit-status`. Verify live with `curl -s https://elbrielle.github.io/cce-curriculum/<path> | grep "<expected text>"`. Remind the user to hard-refresh (⌘⇧R).

Local preview without committing: `python3 -m mkdocs serve` → `http://127.0.0.1:8000/`. Live-reloads on save.
