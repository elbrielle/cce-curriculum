# PLANNING.md — CCE Curriculum Post-Meeting State

**Last updated:** 2026-04-28 (sixth session: PDF pipeline + Round 1/2/3 designs integrated; all 173 exit tickets ship as printable PDFs)
**Purpose:** Brief any agent on the current state of the CCE curriculum project after the 2026-04-15 teacher meeting.

---

## 0. Next Agent — Start Here

### TL;DR (read this first)

**The 36-week CCE curriculum is fully piloted AND reconciled AND printable.** 35 of 35 auditable weeks passed the TEKS audit + exit-ticket rewrite (Wk0 skipped per user). All 173 daily exit tickets now ship as printable PDFs from a Playwright + Jinja2 + design-CSS pipeline. Current state:

- Every day has an audited TEKS tag + rewritten exit ticket (6th-7th grade ESL, ≥3 distinct formats per week, DOK 2+)
- `docs/resources/teks-coverage-matrix.md` truthfully reflects every day's TEKS tags
- Coverage: **36 of 37 TEKS codes Explicit (97%)**; only d(4)(D) remains Implicit (by design — core academic skills are embedded throughout)
- **All 173 daily exit tickets render as per-format structured PDFs** at `docs/resources/exit-tickets/`. Linked from every day file. Pipeline notes: `cce-curriculum/notes/exit-ticket-pdf-pipeline.md`.
- Preservation loop clean across all touched files

**No pilot or pipeline work remains.** The next agent's choices are either coordinator-dependent unblocks (see Priority list) or brand-new work (Wk0 pilot, a second CFA pass, summative worksheets, etc.).

### Read in this order before editing

1. **`CLAUDE.md`** — project rules (ESL rule for tickets, TEKS audit gate, authoring-rulebook locations, source grounding, special markers).
2. **`PLANNING.md`** §3 (format rules), §8 (non-negotiables), §9 (preservation loop), §10 (lessons learned).
3. **`cce-curriculum/notes/editing-heuristics.md`** — dependency-scope protocol, grep recipes, 11-item "never do X without reading more" list, full-file redundancy audit protocol.
4. **For exit-ticket / objective / DOL edits:** `cce-curriculum/notes/teks-audit-process.md` (6-step audit + audit log) + `cce-curriculum/notes/exit-ticket-templates.md` (10-format bank).
5. **For CFA edits:** `cce-curriculum/notes/cfa-template.md`.
6. **For PDF pipeline / printable artifacts:** `cce-curriculum/notes/exit-ticket-pdf-pipeline.md` — operating instructions, per-format status, design-team rounds 1–3.

### What shipped — don't redo this work

- **35-week pilot pass.** TEKS audit + exit-ticket rewrite across every auditable week. Details in the "Pilot-pass status table" below and commit-by-commit in the `teks-audit-process.md` audit log. Wk0 intentionally skipped.
- **Matrix reconciliation.** 15 row-level mismatches corrected; every day file's TEKS tags now match `docs/resources/teks-coverage-matrix.md`. Commit `5bc6a9f`.
- **Round-2 TEKS deepening.** All three Implicit-only codes closed: d(3)(F) promoted E via 4SW Wk1 Day 4 framing + exit-ticket extension; d(4)(E) tier corrected I→E (6SW Wk1 Day 4 LO already explicit) + third touchpoint at 4SW Wk6 Day 3; d(3)(D) tier promoted I→E via re-read of existing 4SW Wk2 Day 5 exit-ticket probe.
- **Exit-ticket PDF pipeline.** Built the markdown-to-PDF generator (`build/build_pdfs.py`) plus the link injector (`build/inject_pdf_links.py`). Integrated three rounds of design work from the design team: Round 1 (4 canonical formats), Round 2 (6 canonical formats), Round 3 (6 variants). 173 of 173 tickets render with a per-format structured component (167 canonical + 6 variants); zero markdown fallbacks. Full operating manual in `cce-curriculum/notes/exit-ticket-pdf-pipeline.md`.

### Priority list (agent picks ONE to work next)

1. **Coordinator review unblock (BLOCKED on coordinator response).** Milestone publication of the full pilot and the H&L-vs-TEKS structural escalation wait on coordinator review of the 2SW Wk2 pilot at `https://elbrielle.github.io/cce-curriculum/exit-ticket-pilot/`. No agent action until the review returns.

2. **Wk0 Classroom Routines pilot pass (UNBLOCKED; only remaining TEKS-audit target).** Wk0 was skipped during the 35-week pass per user directive. If the user wants full 36-week coverage, run the 6-step audit + exit-ticket rewrite over Wk0's 5 days. Estimated 90 min. Value is lower than the 35 already done because Wk0 is classroom-routines scaffolding, not career content. After the audit, re-run `python3 build/build_pdfs.py docs/1sw/wk0-classroom-routines/day*.md` and `python3 build/inject_pdf_links.py` to generate the 5 new exit-ticket PDFs.

3. **CFA rollout for 2SW-6SW (BLOCKED on round-2 teacher feedback on the 1SW CFA sample).** Template in `cce-curriculum/notes/cfa-template.md`. Do not build 2SW-6SW CFAs until the 1SW sample returns with teacher comments.

4. **Round 3 visual polish (UNBLOCKED but low priority).** Three Round 3 variants (F05c Procedural Decision Tree, F06b Prose-Follow-up Ranked, F07b Feedback Sandwich) had their Jinja branches authored from the design team's CSS contract alone after the design agent's session ran out. Rendered PDFs look right at first read; a future design pass should review them against the CSS comments and tighten any layout drift. See `cce-curriculum/notes/exit-ticket-pdf-pipeline.md` "Future work" section.

5. **Whole-week polish reviews (BLOCKED on user priority call).** Some 4SW+5SW+6SW weeks had retags batched without detailed per-week audit log entries (see the 13-week batch entry in `teks-audit-process.md`). If the coordinator requests individual-week audit-log detail for review, reconstruct from git commits.

6. **New teacher feedback rounds (BLOCKED on teacher scheduling).** When the next teacher-feedback round arrives, sort with §4.6 triage protocol.

### Starter task (only if user approves Wk0 pilot)

No systematic pass is pending. If the user directs a Wk0 pilot pass:

1. Read the 5 Wk0 day files in `docs/1sw/wk0-classroom-routines/`.
2. Apply the 6-step TEKS audit + exit-ticket rewrite pattern used across the other 35 weeks. Wk0 is shorter on career content (routines + classroom norms), so expect lighter retags.
3. Use `cce-curriculum/notes/exit-ticket-templates.md` for format picks; honor the ≥3 distinct formats per 5-day week rule.
4. Preservation loop + `AUDIT: Wk0 Classroom Routines` commit.

**Commit-message rule:** Write commit messages in plain English that a teacher can read. Describe what changed and why in complete sentences; avoid jargon; skip file-level bullet lists unless a reviewer needs them.

**Estimated time:** 90 min.

### Recent sessions (don't redo)

- **Sessions 1–5 (through 2026-04-17): pilot pass.** All 35 auditable weeks audited + exit tickets rewritten + matrix reconciled + Round-2 TEKS deepening (three Implicit-only codes closed). Coverage: 36 of 37 TEKS Explicit. Detail in `cce-curriculum/notes/teks-audit-process.md` audit log.
- **Session 6 (2026-04-28): PDF pipeline + Round 1/2/3 designs integrated.** Built the markdown-to-PDF generator and integrated three rounds of design-team output. All 173 daily exit tickets ship as printable PDFs at `docs/resources/exit-tickets/` and are linked from every day file. 100% structured (167 canonical + 6 Round 3 variants). Pipeline operating manual: `cce-curriculum/notes/exit-ticket-pdf-pipeline.md`.

### Durable systems (the foundation for any future work)

- **Exit ticket authoring system.** 10-format bank in `cce-curriculum/notes/exit-ticket-templates.md`. Format picker by objective-verb at the top of that file.
- **TEKS audit process.** 6-step audit in `cce-curriculum/notes/teks-audit-process.md`. Audit log covers all 35 weeks.
- **Exit-ticket PDF pipeline.** `build/build_pdfs.py` + `build/inject_pdf_links.py` + `build/exit_ticket_template/` (CSS, logo, Jinja2 template). Operating manual at `cce-curriculum/notes/exit-ticket-pdf-pipeline.md`. Reusable for any future printable artifact (summative worksheets, slides) by adding new per-format Jinja branches and CSS.
- **Authoring rulebooks** live in `cce-curriculum/notes/`, not `docs/resources/`. The `docs/resources/` folder is for student- and teacher-facing matrices, references, and generated PDFs (`docs/resources/exit-tickets/`).
- **Pilot milestone** (`exit-ticket-pilot`) live at `https://elbrielle.github.io/cce-curriculum/exit-ticket-pilot/`. Coordinator review still the gate for milestone publication of the full pilot.

### Key insights baked into the system

- **Exit tickets = mastery probes, not engagement activities.** Strictly aligned to a TEKS code ON THAT DAY. Variety across a week (≥3 distinct formats per 5 days). DOK 2+. Investigative or problem-solving, not recall. Under 5 min.
- **ESL reading level (6th-7th grade) for exit-ticket student-facing text.** Short sentences, concrete examples, scaffold word lists for abstract concepts, no nested clauses or idioms, no TEK codes in the ticket itself.
- **TEKS "such as" language = examples, not exhaustive.** d(4)(F) lists work ethic / integrity / dedication / perseverance "such as"; any genuine workplace characteristic counts.
- **H&L vs TEKS is an overlay relationship.** Some TEKS align natively (d(1)(C)). Others require CCE-authored overlay content (d(4)(F)). When the overlay is thin on a given day, drop the TEKS claim from that day rather than forcing the exit ticket to pretend.
- **Four recurring retag patterns** emerged across 35 weeks (documented in the audit log batch entry):
    1. **d(8)(A) "select pathway" over-claim on Favorites days** → retag to d(1)(C); d(8)(A) Explicit is locked to 4SW Wk1 Day 2 + 6SW Wk6.
    2. **d(5)(A) "labor market trends" over-claim on community-design days** → community data ≠ labor-market data; retag to d(1)(C) or d(5)(B).
    3. **d(4)(F) over-claim on soft-skills days** → communication/feedback practice = d(4)(B), not d(4)(F).
    4. **Xello + CareerOneStop self-assessments are d(1)(A) Implicit anchors** — every week with Interests / Learning Styles / Skills Matcher gained a d(1)(A) Implicit row.

### Open for coordinator decision (blocked on user emails)

- **H&L-vs-TEKS structural question.** Some TEKS that the scope-and-sequence claims are covered by a given H&L chapter are only covered by CCE's overlay, not by H&L content itself. Coordinator input needed on whether to (a) add supplementary content closing the gap, (b) accept overlay-dependent assessment as sufficient, or (c) retag weeks to match what's actually taught. Specific flagged weeks documented in prior PLANNING.md sessions — see §6.

### Branch + push state

- **Branch:** `claude/read-md-files-handoff-WKBeb` is the active development branch for this pilot pass. Every `AUDIT:` commit is on that branch.
- **Remote state:** pushed; last commit is the PLANNING/audit-log update for this handoff.
- **Not merged to main:** the branch is intentionally not merged to `main` yet — merging is the user's decision, not an agent action. Per project branch directive: never push to main without explicit permission.
- **Full commit list of the pilot pass:** `git log --oneline | grep "^[a-f0-9]\{7\} AUDIT:"` returns all 38 audit commits.

### Pilot-pass status table (reference — all rows DONE except Wk0 SKIP)

| Block | Week | Status |
|---|---|---|
| 1SW | Wk0 Classroom Routines | SKIP (per user, candidate for future pass) |
| 1SW | Wk1 Robotics / Manufacturing | DONE (commit `3d024f8`) |
| 1SW | Wk2 Programming / IT | DONE (commit `3b3e67d`) |
| 1SW | Wk3 Computer Science / IT | DONE (commit `c8fb241`) |
| 1SW | Wk4 Tech Support / IT | DONE (commit `a1c2232`) |
| 1SW | Wk5 Cybersecurity | DONE (commit `a5b3772`) |
| 2SW | Wk1 Legal Studies | DONE (commit `a1a6711`) |
| 2SW | Wk2 Law Enforcement / EMT | DONE (commits `0455a0d` → `4aa6467`) |
| 2SW | Wk3 Nursing / Health Science | DONE (commit `3f83586`) |
| 2SW | Wk4 Dental / Medical Billing | DONE (commit `68db8e2`) |
| 2SW | Wk5 Powerskills / Communication | DONE (commit `ac97ce3`) |
| 2SW | Wk6 Biomedical / Health Science | DONE (commit `64a80fa`) |
| 3SW | Wk1 Vet Science | DONE (commit `d459d47`) |
| 3SW | Wk2 Plant Science | DONE (commit `364e7bd`) |
| 3SW | Wk3 Sustainable Engineering | DONE (commit `8d3b834`) |
| 3SW | Wk4 Culinary / Hospitality | DONE (commit `db6198d`) |
| 3SW | Wk5 Cosmetology | DONE (commit `e7b7208`) |
| 3SW | Wk6 Entrepreneurship | DONE (commit `87127f7`) |
| 4SW | Wk1 Career Planning | DONE (commit `926e4ed`) |
| 4SW | Wk2 Course Mapping | DONE (commit `9b5de54`) |
| 4SW | Wk3 Aviation | DONE (commit `5202311`) |
| 4SW | Wk4 Drone Engineering | DONE (commit `0970466`) |
| 4SW | Wk5 Automotive | DONE (commit `4b34af4`) |
| 4SW | Wk6 Trades Capstone | DONE (commit `75ffb7e`) |
| 5SW | Wk1 Architecture | DONE (commit `a2783d4`) |
| 5SW | Wk2 Civil Engineering | DONE (commit `3beb71d`) |
| 5SW | Wk3 Construction Trades | DONE (commit `e3e086b`) |
| 5SW | Wk4 HVAC / Electrical / Plumbing | DONE (commit `b614571`) |
| 5SW | Wk5 Personal Budget | DONE (commits `f608640` → `8b39366`) |
| 5SW | Wk6 Real Estate | DONE (commits `8931c98` → `3d656fd`) |
| 6SW | Wk1 Education | DONE (commits `b67016e` → `be966d3`) |
| 6SW | Wk2 Resume / Graphic Design | DONE (commits `c7304a8` → `180a1d1`) |
| 6SW | Wk3 Business / Marketing | DONE (commit `e67e590`) |
| 6SW | Wk4 Sales / Presentations | DONE (commit `7a68f35`) |
| 6SW | Wk5 Job Skills / Mock Interview | DONE (commit `a52babc`) |
| 6SW | Wk6 Capstone | DONE (commit `0d43f68`) |

**Side tasks (still unblocked):**

- **§4.3 C5 Xello vs H&L platform overlap** — blocks on user SSO hands, not on Claude.
- **CFA rollout for 2SW-6SW** — blocks on round-2 teacher feedback on the 1SW CFA.

### Do NOT

- Touch `v1-teacher-review` milestone — preserved pre-feedback baseline
- Overwrite `exit-ticket-pilot` milestone without user intent (it's the current coordinator review snapshot)
- Start on B4 or H&L workbook timeline — still blocked on team email response (§4.2)
- Build 2SW-6SW CFAs yet — waiting on round-2 teacher feedback on the 1SW sample
- Hand-edit the design CSS files in `build/exit_ticket_template/` (`exit-tickets.css`, `exit-tickets-round2.css`, `exit-tickets-round3.css`). They are the design team's source of truth. Pipeline-level fit overrides go in the inline `<style>` block of `template.html.j2`.
- Roll any new printable artifact (summative worksheets, slides, parent-facing handouts) without reading `cce-curriculum/notes/exit-ticket-pdf-pipeline.md` first. Reuse the existing pipeline pattern; do not start a parallel reportlab-style toolchain.
- Rewrite an exit ticket without running the TEKS audit first
- Treat "sentence stem + word bank" as the endorsed exit-ticket pattern — that was one week's rewrite (C3/C4), not universal. Variety + investigation + mastery-of-objective is the real feedback.
- Push to main without running the §9 preservation loop first
- Push without explicit user permission

---

## 1. What This Project Is

A **36-week Career and College Explorations (CCE)** course for grade 7 across **Irving ISD VILS Labs**, Texas. Aligned to **TEKS 127.2 (Adopted 2023)**. Delivered as a static MkDocs Material website. Each week has 1 overview + 5 daily plans = **252 markdown files total** in `docs/`.

**Platform stack:** Hats & Ladders (core, 282pp workbook + 221pp Powerskills), Xello (supplemental), eDynamic Learning (supplemental), VILS tech (Sphero, TinkerCAD, Canva, Glowforge, micro:bit, drones, LEGO).

**Current deployment:** Live at `https://elbrielle.github.io/cce-curriculum/latest/`. Versioned via mike; `v1-teacher-review` preserved as the pre-feedback baseline (do not modify this version).

---

## 2. Repo Layout

```
27 CCR Planning/
├── CLAUDE.md                          ← project rules (READ FIRST)
├── PLANNING.md                        ← this file
├── mkdocs.yml                         ← site config + full nav
├── PATHWAYS.md                        ← Irving ISD CTE pathway reference
├── PLATFORMS.md                       ← H&L / Xello / eDynamic / VILS details
│
├── docs/                              ← THE WEBSITE (source of truth)
│   ├── index.md
│   ├── scope-and-sequence.md
│   ├── 1sw/ ... 6sw/                  ← six-weeks blocks
│   │   └── wkN-topic/
│   │       ├── overview.md
│   │       └── day1.md ... day5.md
│   └── resources/
│
├── cce-curriculum/                    ← reference data (not the website)
│   ├── scope-and-sequence.md          ← master pacing guide (authoritative)
│   ├── resources/reference-pdfs/      ← H&L workbook PDFs + .txt extracts
│   └── notes/
│       ├── editing-heuristics.md      ← READ before any substantive edit
│       ├── instinct-review.md         ← adversarial review results (14 weeks done)
│       ├── vetting-report.md          ← FROZEN clinical pass
│       └── revision-plan.md           ← H&L chapter-to-week crosswalk
│
├── build/                             ← Python build scripts
└── site/                              ← built MkDocs site (gitignored)
```

**Critical:** `docs/` is the website source of truth. Edits go in `docs/`.

---

## 3. Format Rules (summary)

Full rules in `CLAUDE.md`. Key points:

- **No teacher scripting.** Never `> **Teacher:** "..."`. Use facilitation prose.
- **Source-ground everything.** H&L cites chapter + page. Xello cites S&S col 8 name. eDynamic cites unit number.
- **Concrete deliverables per day.** Specific artifact, not "students explore."
- **Prototype to match:** `docs/5sw/wk1-architecture/` (overview + day1-5).
- **No em dashes** in teacher-facing `docs/` body prose.
- **Timing 45-55 min** at H2 activity-header level per day.
- **Support / Extension / ELL + Spanish vocab** on every daily plan.

---

## 4. Teacher Meeting Feedback Intake (2026-04-15)

Three sources of feedback collected: Google Form (2 responses, E. O'Connor), handwritten notes from the meeting (~15 items), and the H&L scope notes spreadsheet (their vision for the personalized IISD workbook). Feedback sorted into jurisdiction buckets before action.

### 4.1 US JURISDICTION — Elisha + Claude decide and implement

**All 14 items shipped across sessions 2-3** (DOK audit, facilitation strategies page, CFA template + 1SW sample, TEKS coverage map, engineering notebook supply, Medical Billing cut, JROTC audit, PT/Sonography placeholders, "What is CTE" Xello module, various Hour-of-Code fixes, Irving ISD pathway rewording). Full commit-by-commit history in git log filtered by prefix `git log --oneline --all | grep -E "(fea941b|1b7ec9b|5879218|575be17|a87d597|6da8060|2ace0bf|4a80740|d9ad853|08524c3)"`.

**Round-2 follow-ups to watch for:**
- 1SW CFA results: if >30% of students score ≤2 on any part, the CFA template's reteach triggers fire. Data back-flows into the 2SW block plan.
- ~~Three TEKS deepening candidates~~ CLOSED 2026-04-17 (see §0 "What shipped").

### 4.2 TEAM JURISDICTION — Email and block on their input

- **B4 Drone / Robotics overlap** — 1SW Wk1 (Robotics) and 4SW Wk4 (Drone Engineering) have significant instructional overlap. Combine into one week (freeing a week for another topic) or sharpen the instructional distinction (manufacturing robotics vs. aerial autonomous systems) so H&L can build a clear differentiation in the personalized workbook?
- **H&L personalized workbook timeline** — expected delivery date? Determines how much editing effort to invest in weeks H&L will overwrite with new activities.

### 4.3 HYBRID — Investigate first, then decide

- **C5 Xello vs H&L platform overlap** (career cluster favoriting and similar). Prep: audit each platform for prerequisite chains (what must be completed in Xello to unlock other Xello content? Same for H&L? Where are pre-req traps?). Compare effectiveness per purpose. Once prereq map and effectiveness comparison exist, make the call ourselves. Escalate only if analysis surfaces a hard constraint.

### 4.4 DEFERRED — Not actionable yet

- **C6 H&L teaching guide page references** — blocked on H&L delivering the teaching guide (we only have the student workbook).
- **Full workbook re-sync pass** — when personalized IISD workbook arrives, all `[description coming soon]` activities in the H&L spreadsheet become real content to cite. Do not invest heavy editing in affected weeks until then.

### 4.5 H&L Activity Cross-Reference

H&L's scope notes reference both existing workbook activities and future IISD-personalized content.

**Already in the current example workbook** (can cite now): Mission to Mars, Task Bot in Action, Emergency Essentials: Kit Design, Perfect Toothbrush, Trash to Treasure, Safety Supervisor, Infrastructure Imagination, Protecting Wildlife, Pack Your Bags / Local Tourism Campaign, Hotel Rescue, Pitch Your Idea. Motivation and Creativity are in current Powerskills.

**NOT in the current workbook** (coming with IISD personalization): Digital Fingerprint Analysis, Digital Disguise, Drafting a Law, Mock Trial (Citizens v. Oakhaven), Bike Path Emergency, Heat Detective, Triage Experts, Dental Detectives, Codebook in Action, Mini Medics, Med Safe Packaging, Patient Learning, Grow System Rescue, Rebranding a Menu, Special Effects Makeup, Skincare Science, Prompt Engineering for Makeup Artists, Million Dollar Idea, Build Your Business Blueprint, Build it Better, Energy Escape, Survive the Depths, Water Line Crisis, Flight Line Fixers, Crash Crew, Brake Pad Investigation, Safety Squad. New Powerskills: Resilience, Tolerance to Ambiguity, Nonverbal Communication, Analytical Reasoning.

**H&L's "What is Happening at Irving ISD?" pattern** already aligns with our existing pathway/certification sections. When the personalized workbook ships, our sections will sync naturally; for now, reword only to tighten language.

### 4.6 Triage Protocol (for future feedback rounds)

1. **Collect** into a single doc: Teacher | Week | Dimension | Feedback | Priority | Status
2. **Sort** into us / team / hybrid / deferred
3. **Priority within us-jurisdiction:**
   - **P0 (2 days):** factual errors, missing TEKS, broken materials, safety
   - **P1 (1 week):** rigor/engagement/timing, differentiation, activity replacements
   - **P2 (backlog):** nice-to-have, stylistic preferences
4. **Batch edits by type** across weeks (e.g., all exit ticket DOK rewrites in one pass)
5. **Close the loop** with teachers when their specific feedback ships

---

## 5. Instinct Review Status

**Superseded by the 35-week pilot pass.** The instinct-review pass covered 14 weeks (1SW Wk0, 4SW Wk1, 5SW Wk1, 6SW Wk6, 2SW Wk5, 6SW Wk5, 4SW Wk2, 5SW Wk5, 3SW Wk3, 2SW Wk4, 6SW Wk4, 5SW Wk2, 2SW Wk1, 5SW Wk6) via adversarial Teacher-Implementer / Curriculum-Writer dialog. Subsequent sessions replaced it with the systematic TEKS audit + exit-ticket rewrite applied to all 35 auditable weeks. Instinct-review findings are documented in `cce-curriculum/notes/instinct-review.md`; insights from that pass are baked into the pilot formats and are not a separate pending queue.

---

## 6. Escalation Queue

Decisions needing a human, not an edit:

**From teacher meeting 2026-04-15 (needs email):**
- **B4 Drone / Robotics overlap** — combine 1SW Wk1 + 4SW Wk4 into one week, or sharpen instructional distinction for H&L's personalized workbook?
- **H&L personalized workbook timeline** — expected delivery date?

**From 2SW Wk2 exit-ticket pilot 2026-04-16 (user emailing coordinators):**
- **H&L-vs-TEKS alignment structural question.** H&L is career-exploration content; TEKS alignment is CCE's overlay. Some days claim TEKS coverage that comes only from the overlay, not from H&L. Coordinator decision: add supplementary content to close gaps, accept overlay-dependent assessment as sufficient, or retag. Full reasoning in the `exit-ticket-pilot` milestone and in `cce-curriculum/notes/teks-audit-process.md`.

**From 2SW Wk2 instinct-review fix pass 2026-04-17:**
- **Day 4 teacher scoring load (structural).** Day 4 of 2SW Wk2 asks a single teacher to score the week's summative (team Citywide Emergency Plan + live 3-minute team presentation, rubric on role logic + d(4)(F) traits + Silver Ridge resource use) *plus* a dilemma-analysis exit ticket, *plus* continue to collect individual role plans from Day 3-4. Estimated load on a 30-student roster: 6-8 team presentations evaluated live, 30 individual dilemma exit tickets, and 30 individual role plans — all on the same class period. The load is not specific to 2SW Wk2; it is the pattern wherever a team-performance summative shares a day with an individual exit-ticket summative. Coordinator decision paths: (a) split summative scoring across two days (Day 4 presentation, Day 5 scored-reflection review), (b) offload the individual role plan to Day 3 formative-only and keep Day 4 summative to the team artifact + exit ticket, or (c) accept the load and staff Day 4 with a co-facilitator for live scoring. Flagged the same way as the 6SW Wk6 capstone co-facilitator question (§6 pre-existing).

**Pre-existing:**
- **Xello Wk0 district requirement** — moved from core to Day 5 flex with `[VERIFY]`. District-required?
- **5SW Wk1 Day 5 eDynamic Unit 3.1** — district verification needed
- **4SW Wk1 Day 3/4 `[VERIFY IN Xello/eDynamic]`** — Quick Sims "The Real Game", Unit 8.1
- **6SW Wk6 Days 3/4 co-facilitator staffing** — district admin/counselor for capstone presentations?
- **1SW Wk3 Sphero tech-tool drift** — S&S col 7 says "RVR+" but implementation uses paper wireframing
- **3SW Wk6 Glowforge tech-tool drift** — S&S col 7 says "Glowforge: Cut logo" but week is paper investor pitch
- **d(8)(A)/(B)/(C) buffer-week risk** — every d(8) week is a buffer. If teacher loses buffers, d(8) uncovered.
- **Curriculum-density pattern** — several weeks feel rushed from implementing all H&L + Xello + eDynamic at full fidelity. What to cut is not Claude's call.
- **HVAC/Electrical/Plumbing "Coming 2027"** — district-wide or specific campus?
- **2SW Wk4 Medical Billing** — Singley webpage doesn't list it but S&S includes it (resolved by B1 cut)

---

## 7. Resource Backlog

Tracked at `docs/resources/resources-status.md`.

**Shipping today:**

- **Daily exit-ticket worksheets.** Every daily exit ticket renders as a printable PDF at `docs/resources/exit-tickets/<Nsw>-wk<N>-day<N>-<slug>.pdf`. 173 of 173 tickets, 100% structured (167 canonical + 6 Round 3 variants). Linked from every day file. Operating manual: `cce-curriculum/notes/exit-ticket-pdf-pipeline.md`.

**Pipeline available — content/design work needed:**

1. **Summative worksheets** for high-stakes assessments (6SW Wk6 Capstone rubric, 4SW Wk2 Career Plan, 5SW Wk5 Budget). The exit-ticket PDF pipeline (`build/build_pdfs.py`) can be reused for summative worksheets, but each worksheet type needs its own design template (per-format Jinja branch + CSS additions). Coordinate with the design team before authoring.
2. **Presentation slides** (5SW Wk1 prototype first). Same pipeline could render slide PDFs from markdown if a slide template were authored.
3. **Teacher edition / answer keys** for the high-stakes summatives — once those summative worksheet templates exist.

**Content-actionable (can build in markdown today):**

4. **CFAs for 2SW–6SW** — template exists in `cce-curriculum/notes/cfa-template.md`. Still gated on round-2 teacher feedback on the 1SW CFA.

**Out of scope:** video integration (deferred until after teacher feedback round).

**Worksheet production principle** (per user 2026-04-16): printable worksheets should include visuals / diagrams / matching / MCQ item types that approximate STAAR exposure for grade 7. The existing PDF pipeline supports this — see how the design-team CSS handles tables, SVG diagrams, MCQ option lists, ruled writing slots, etc. in `build/exit_ticket_template/`.

---

## 8. Non-Negotiables

- **Read before editing:** `CLAUDE.md`, this file, `editing-heuristics.md`. For exit-ticket / objective / DOL edits, also `teks-audit-process.md` + `exit-ticket-templates.md`. For PDF pipeline edits, also `cce-curriculum/notes/exit-ticket-pdf-pipeline.md`.
- `vetting-report.md` is **frozen**.
- **3-5 weeks max** per instinct-review session.
- **15 lines max** per day file per edit. More = redesign = escalate.
- **No new activities.** Stay grounded in H&L + Powerskills + S&S + BLS + Irving ISD pathways.
- **No scripting** (`> **Teacher:` stays at 0).
- **No declarative fluff.** "This is real X", "Real conferences cut speakers off" = banned.
- **No surprise discipline.** Hard enforcement only if the skill is taught AND students are warned.
- **Preserve** Support / Extension / ELL + Spanish vocab on every daily plan.
- **Timing 45-55 min** at H2 level. Never edit `(N min)` parenthetical unless changing minutes.
- **No em dashes** in `docs/` body prose. H1/H2 titles fine. Developer-facing files (`cce-curriculum/notes/`) fine.
- **6th-7th grade ESL reading level** for exit-ticket student-facing text.
- **TEKS audit gate.** Never rewrite an exit ticket, lesson objective, or DOL without first running the audit in `teks-audit-process.md`. TEKS tags are not inheritable; they must be honestly supported by the day's activities. "Such as" TEK language means named items are examples, not exhaustive.
- **Authoring rulebooks live in `cce-curriculum/notes/`, not `docs/resources/`.** Templates, CFA specs, audit processes are dev-facing. If the link points to a template bank from a teacher-facing file, it is a bug.
- **Irving ISD pathways** must be verified against the canonical website, not PATHWAYS.md alone.
- **Never touch Wk0 Day 2-5 data-seeding activities** without reading 4SW Wk1 / 6SW Wk6 chain.
- **Reuse the PDF pipeline** (`build/build_pdfs.py` + design CSS) for any new printable artifact. Do not start a parallel reportlab-style toolchain. The design CSS files in `build/exit_ticket_template/` are the design team's source of truth and must not be hand-edited; pipeline-level fit overrides go in the inline `<style>` block of `template.html.j2`.
- **Re-run `python3 build/inject_pdf_links.py`** after generating new exit-ticket PDFs so day files carry the canonical `· [Printable PDF](...)` links.
- **Preservation loop** after every edit batch (all 6 must pass before commit).
- **No `--no-verify`, `--force`.** Fix the underlying issue.
- **No push** without explicit user permission.

---

## 9. Preservation Loop

Run after every edit batch. All six must be clean before committing.

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

---

## 10. Lessons Learned

Each lesson is a rule with a one-sentence rationale. Full context in commits and `instinct-review.md`.

1. **Verb menu > prescriptive playbook** for flexibility framing. 4-verb menu (cut, compress, substitute, skip). No "Scenario A / B."
2. **Name load-bearing vs. flex explicitly.** Teachers route around flex stuff with campus knowledge.
3. **Buffer weeks need explicit flex framing.** Add flex admonition naming what can be cut.
4. **Admonitions > dense prose** for advisory content. `!!! abstract | warning | tip | note`.
5. **Language + timing softening together.** Softening a directive without adjusting time allocation is incomplete.
6. **Cross-week data dependencies are silent until they break.** Wk0 seeds Climber Profile consumed by 4SW Wk1 / 6SW Wk6.
7. **Presentation math almost never works.** (students x minutes) must fit (budget minus feedback minus transition). Use `!!! warning` with compression options.
8. **Clinical pass is not instinct pass.** Both are necessary.
9. **Skill before enforcement (Dimension 9).** Hard discipline only if skill is taught that week AND students warned.
10. **Don't over-use sub-agents.** Only for adversarial dialog or large mechanical passes.
11. **Check your own recent diff** for patterns you're hunting.
12. **Never edit H2 `(N min)` parenthetical** unless changing the minute count.
13. **Emotional-safety reframes.** Before shipping anything that categorizes careers as good/bad, ask: "Could a student have a parent in the bad column?"
14. **Fully-optional-week reframe** for severe buffer windows with upstream TEKS coverage.
15. **Teacher-facing prose discipline.** No em dashes, admonitions 12 lines max, full-file redundancy audit after framing changes.
16. **Dead intro paragraphs.** If deleting the paragraph loses nothing the title + bullets don't carry, delete.
17. **Week pages are operational, not self-referential.** No Teacher Prep Checklist admonitions. No meta-commentary.
18. **Bulk regex for prose-pattern sweeps** when ~90% of cases fit 4-5 patterns. File-by-file when judgment matters.
19. **Bulk script fallback rule IS the quality ceiling.** Budget a fixup pass.
20. **Raw cliche grep counts are useless without per-hit classification.** Spot-check 20-30 hits before scoping.
21. **TEKS tags are author claims, not facts.** Audit before writing the assessment. H&L is career-exploration content, not natively TEKS-aligned; CCE is the overlay. Use `teks-audit-process.md` before rewriting any exit ticket, objective, or DOL. Session 3 example: 4 of 5 days in 2SW Wk2 had over-claimed or weak tags until audited.
22. **"Teacher-facing" is a real constraint, not a label.** If a document tells the reader how to author something ("insert this admonition," "pick a format from the list"), it is for the author, not the teacher. Move to `cce-curriculum/notes/`. First violations shipped in session 2: exit-ticket-templates.md and cfa-template.md originally in `docs/resources/` with author-voice pattern instructions visible to teachers; relocated session 3.
23. **Variety > single endorsed exit-ticket template.** Teacher feedback's "sentence stem + word bank" (commits `d9ad853`, `1b7ec9b`) was a specific-week rewrite, not the universal rule. The durable rule is variety + investigation + mastery-of-day's-objective. Apply `exit-ticket-templates.md` format picker; ≥3 distinct formats per 5-day week.
24. **ESL reading level is a first-class constraint for exit tickets.** 6th-7th grade ESL: short sentences, concrete examples, scaffolded word lists for abstract concepts. Nested clauses and idioms block comprehension in this population.

---

## 11. Deploy Workflow

Push to `main` triggers GitHub Actions `mike deploy --push latest` on `gh-pages`. Verify with `gh run list --limit 3`. Local preview: `python3 -m mkdocs serve`.

### Versioning convention

- **`latest`** — rolling pointer, always the current in-progress state. Every push to `main` updates this.
- **Named milestones** — frozen snapshots for review. Created via Actions UI "Run workflow" with `milestone_name` input, or via `gh workflow run deploy-site.yml -f milestone_name=<name>`. Naming is descriptor-based, chosen to match the review scope.
  - `v1-teacher-review` — state presented at the 2026-04-15 teacher meeting (pre-feedback baseline). Do not touch.
  - `exit-ticket-pilot` — 2SW Wk2 exit-ticket pilot + TEKS audit work from 2026-04-16, for coordinator review.
- **`YYYY-MM-DD`** — automatic daily snapshots from the nightly cron if `docs/` changed that day (noise — ignore unless debugging).

### When to tag a new milestone

Create a new named snapshot:
- Before a teacher / coordinator review session (capture "what they saw")
- After a major feedback round ships
- Before a risky refactor (rollback anchor)

If a milestone name is wrong after the fact, delete and redeploy: `mike delete <name> --push` (requires `git fetch origin gh-pages` first), then `gh workflow run deploy-site.yml -f milestone_name=<correct-name>`.

Never rename or delete `v1-teacher-review` — it's the historical record of what went in front of teachers on 2026-04-15.
