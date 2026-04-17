# PLANNING.md — CCE Curriculum Post-Meeting State

**Last updated:** 2026-04-17 (fourth session: 2SW Wk2 instinct-review follow-ups + 3SW Wk5 + 4SW Wk5 TEKS audits and exit-ticket pilot rewrites)
**Purpose:** Brief any agent on the current state of the CCE curriculum project after the 2026-04-15 teacher meeting.

---

## 0. Next Agent — Start Here

### Read in this order before editing

1. **`CLAUDE.md`** — project rules (updated this session with ESL rule, TEKS audit gate, authoring-rulebook locations)
2. **`PLANNING.md`** §3 (format rules), §8 (non-negotiables), §9 (preservation loop), §10 (lessons learned)
3. **`cce-curriculum/notes/editing-heuristics.md`** — dependency-scope protocol and grep recipes
4. **For exit-ticket / objective / DOL edits:** `cce-curriculum/notes/teks-audit-process.md` + `exit-ticket-templates.md` (new this session)
5. **For CFA edits:** `cce-curriculum/notes/cfa-template.md`

### What shipped this session (2026-04-17, fourth session)

Two Tier-1 week audits + 2SW Wk2 instinct-review follow-ups. PDFs deferred per the 2026-04-16 "do NOT invest in reportlab polish" rule; this session produced markdown-only exit tickets for the two new weeks.

- **2SW Wk2 follow-up fixes (commit `4aa6467`).** Six non-exit-ticket fixes from the original pilot instinct review shipped: EMT pathway added to overview (Singley School of Health Science, EMT-B cert); Day 2 Activity 3 peer-argument norm scaffolded (3 rules + 4-min budget); Day 3 Activity 1 Silver Ridge brief chunked into 3 passes (zones, buildings, constraints hunt); Day 4 Activity 1 per-role integrity dilemma scaffold (5 role templates); Day 4 Activity 3 presentation-time compression options keyed to class size; Day 5 Activity 4 AI-ethics dead reference removed. PLANNING §6 picked up a new Day 4 teacher-scoring-load structural escalation alongside the H&L-vs-TEKS question.
- **3SW Wk5 Cosmetology audit + pilot rewrite (commit `e7b7208`).** All 5 days audited. Days 1, 2, and 5 retagged (d(2)(A) + d(3)(G) + d(3)(I) over-claims dropped and replaced with d(1)(B), d(1)(C), d(6)(C), d(7)(B), d(1)(A)); Days 3 + 4 tags kept. Matrix promotions: d(6)(C) + d(7)(B) moved Implicit → Explicit at 3SW Wk5 Day 2; d(2)(A) Explicit Weeks list extended to include 3SW Wk5 Day 3 (was missing). Exit tickets rewritten in 5 distinct formats (Comparison Matrix / Mini-Case / Ranked Justification / Decision Tree / Concept Map) at 6th-7th ESL reading level.
- **4SW Wk5 Automotive audit + pilot rewrite (commit TBD — this session).** All 5 days audited. Only Day 5 retag needed — d(2)(A) + d(2)(B) + d(8)(A) over-claims dropped. Key discipline: d(8)(A) "select a career pathway" is easy to over-claim on H&L Favorites days because favoriting LOOKS like pathway selection; per the matrix, d(8)(A) is Explicit only at 4SW Wk1 Day 2 and 6SW Wk6. Favorites are d(1)(C), not d(8). Day 5 replaced with d(5)(E) + d(1)(C). Matrix picked up d(3)(G) at 4SW Wk5 Day 4 (Ratteree vs. trade school) and d(5)(E) at 4SW Wk5 Day 5 (cross-cluster presentation). Exit tickets rewritten in 5 distinct formats (Venn Diagram / Trade-off Dilemma / Comparison Matrix / Diagnostic MCQ with Misconception Distractors / Concept Map).

### Prior-session durable systems (still the foundation)

- **Exit ticket authoring system.** Ten-format bank in `cce-curriculum/notes/exit-ticket-templates.md`.
- **TEKS audit process.** Six-step audit in `cce-curriculum/notes/teks-audit-process.md`. Audit log in that file now has three entries (2SW Wk2, 3SW Wk5, 4SW Wk5).
- **Authoring rulebooks** live in `cce-curriculum/notes/`, not `docs/resources/`.
- **2SW Wk2 pilot milestone** (`exit-ticket-pilot`) still live at `https://elbrielle.github.io/cce-curriculum/exit-ticket-pilot/`. Not re-deployed this session; coordinator review still the gate for PDF tooling revisit.
- **Pilot PDFs.** Exist for 2SW Wk2 only; none produced for 3SW Wk5 or 4SW Wk5 this session (markdown only). Per prior guidance, do NOT invest in reportlab polish; revisit tooling (Figma + data merge, or CSS-print HTML) after coordinator review.

### Key insights baked into the system

- **Exit tickets = mastery probes, not engagement activities.** Strictly aligned to a TEKS code ON THAT DAY. Variety across a week (≥3 distinct formats per 5 days). DOK 2+. Investigative or problem-solving, not recall. Under 5 min.
- **ESL reading level (6th-7th grade) for exit-ticket student-facing text.** Short sentences, concrete examples, scaffold word lists for abstract concepts, no TEK codes in the ticket itself.
- **TEKS "such as" language = examples, not exhaustive.** d(4)(F) lists work ethic / integrity / dedication / perseverance "such as" — any genuine workplace characteristic counts. Quality-pick probes with open lists are valid d(4)(F) assessments.
- **H&L vs TEKS is an overlay relationship.** Some TEKS align natively (d(1)(C) career identification). Others require CCE-authored overlay content (d(4)(F) integrity). When the overlay is thin on a given day, drop the TEKS claim from that day rather than forcing the exit ticket to pretend.

### Open for coordinator decision (user is emailing)

- **H&L-vs-TEKS structural question.** Some TEKS that the scope-and-sequence claims are covered by a given H&L chapter are only covered by CCE's overlay, not by the H&L content itself. Coordinator input needed on whether to (a) add supplementary content closing the gap, (b) accept overlay-dependent assessment as sufficient, or (c) retag specific weeks to match what's actually taught.

### Recommended next tasks

**SYSTEMATIC PILOT PASS (current strategy, set 2026-04-17).** Work top-down through every week, running the TEKS audit + exit-ticket rewrite per the 2SW Wk2 pilot pattern. Skip Wk0 and the three already-piloted weeks.

**Pilot-pass order and status:**

| Block | Week | Status |
|---|---|---|
| 1SW | Wk0 Classroom Routines | SKIP (per user) |
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
| 2SW | Wk6 Biomedical / Health Science | DONE (this commit) |
| 3SW | Wk1 Vet Science | DONE (commit `d459d47`) |
| 3SW | Wk2 Plant Science | DONE (commit `364e7bd`) |
| 3SW | Wk3 Sustainable Engineering | DONE (commit `8d3b834`) |
| 3SW | Wk4 Culinary / Hospitality | PENDING |
| 3SW | Wk5 Cosmetology | DONE (commit `e7b7208`) |
| 3SW | Wk6 Entrepreneurship | PENDING |
| 4SW | Wk1 Career Planning | PENDING |
| 4SW | Wk2 Course Mapping | PENDING |
| 4SW | Wk3 Aviation | PENDING |
| 4SW | Wk4 Drone Engineering | PENDING |
| 4SW | Wk5 Automotive | DONE (commit `4b34af4`) |
| 4SW | Wk6 Trades Capstone | PENDING |
| 5SW | Wk1 Architecture | PENDING |
| 5SW | Wk2 Civil Engineering | PENDING |
| 5SW | Wk3 Construction Trades | PENDING |
| 5SW | Wk4 HVAC / Electrical / Plumbing | PENDING |
| 5SW | Wk5 Personal Budget | PENDING |
| 5SW | Wk6 Real Estate | PENDING |
| 6SW | Wk1 Education | PENDING |
| 6SW | Wk2 Resume / Graphic Design | PENDING |
| 6SW | Wk3 Business / Marketing | PENDING |
| 6SW | Wk4 Sales / Presentations | PENDING |
| 6SW | Wk5 Job Skills / Mock Interview | PENDING |
| 6SW | Wk6 Capstone | PENDING |

**Per-week protocol** (applied in sequence, one week at a time):

1. Read the week's overview + 5 day files.
2. Run the 6-step TEKS audit per day (`cce-curriculum/notes/teks-audit-process.md`).
3. Retag any day whose TEKS claims fail the audit; update overview TEKS + Formative Assessment to match.
4. Rewrite all 5 exit tickets using ≥3 distinct formats from `cce-curriculum/notes/exit-ticket-templates.md`, at 6th-7th grade ESL reading level, strictly assessing the day's cleaned TEKS tag.
5. Update `docs/resources/teks-coverage-matrix.md` for any Implicit → Explicit promotions or new day-level claims.
6. Append an entry to the audit log in `teks-audit-process.md`.
7. Run the §9 preservation loop; commit with `AUDIT:` subject prefix; push.

**Deferred in this pass** (per 2026-04-16 decision): PDF production, milestone publication, and the H&L-vs-TEKS structural escalation. Each remains open until coordinator review of the 2SW Wk2 pilot returns.

**Side tasks (non-pilot, still unblocked):**

- **Round-2 TEKS deepening** — three Implicit codes (d(3)D, d(3)F, d(4)E) with specific suggested edits in `docs/resources/teks-coverage-matrix.md`.
- **§4.3 C5 Xello vs H&L platform overlap** — blocks on user SSO hands.
- **CFA rollout for 2SW-6SW** — blocks on round-2 teacher feedback on the 1SW CFA.
- **PDF tooling revisit** — blocks on coordinator review.

### Do NOT

- Touch `v1-teacher-review` milestone — preserved pre-feedback baseline
- Overwrite `exit-ticket-pilot` milestone without user intent (it's the current coordinator review snapshot)
- Start on B4 or H&L workbook timeline — still blocked on team email response (§4.2)
- Build 2SW-6SW CFAs yet — waiting on round-2 teacher feedback on the 1SW sample
- Ship "student worksheets" as-if — there is no PDF / docx production pipeline out of markdown. Worksheet backlog (§7) is infrastructure-blocked, not content-blocked.
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

**STATUS: All items shipped (2026-04-16 session 2).** See §0 for commit-by-commit log.

- ~~**A1 Exit ticket DOK audit**~~ — 20 recall-only tickets rewritten as DOK 2-3 (commit `1b7ec9b`)
- ~~**A2/A3 Facilitation strategies resource page**~~ — shipped (commit `fea941b`)
- ~~**A4/A7 CFA template + first 1SW sample**~~ — template + 1SW CFA "Your IT Future" (commit `5879218`). 2SW-6SW deferred to round-2 feedback
- ~~**A5 TEKS coverage depth map**~~ — three-tier upgrade (commit `575be17`)
- ~~**A6 Engineering notebook as standard supply**~~ — added to Wk0 + 2 exemplars (commit `a87d597`)
- ~~**B1 Medical billing cut**~~ — 2SW Wk4 dental-primary restructure (commit `6da8060`)
- ~~**B2 JROTC light audit**~~ — 2 new military-adjacent touchpoints (commit `2ace0bf`)
- ~~**B3 PT / Sonography / Sports Medicine placeholders**~~ — scaffolding file with `SOURCE_PENDING` tags (commit `4a80740`)
- ~~**B5 "What is CTE" Xello module**~~ — slotted into Wk0 Day 2 (commit `fea941b`)
- ~~**C1 Jigsaw tip for 1SW Wk1 Day 1**~~ — first A3 pattern use case (commit `fea941b`)
- ~~**C2 Wk0 Day 1 menu hallucination**~~ — reworded (commit `fea941b`)
- ~~**C3 Hour of Code exit ticket rewrite**~~ — sentence stem + word bank (commit `d9ad853`)
- ~~**C4 Hour of Code Day 2 sentence stem formatting**~~ — long underlines + word bank (commit `d9ad853`)
- ~~**Irving ISD pathway section rewording**~~ — renamed to "What is Happening at Irving ISD?" across 34 files (commit `08524c3`)

**Round-2 follow-ups to watch for:**
- 1SW CFA results: if >30% of students score ≤2 on any part, the CFA template's reteach triggers fire. Data back-flows into the 2SW block plan.
- Three TEKS deepening candidates flagged in `docs/resources/teks-coverage-matrix.md`: d(3)D (impact of planning), d(3)F (co-curricular), d(4)E (community service).

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

14 of 36 weeks reviewed via adversarial Teacher Implementer / Curriculum Writer dialog. 22 remaining.

**Reviewed:** 1SW Wk0, 4SW Wk1, 5SW Wk1, 6SW Wk6, 2SW Wk5, 6SW Wk5, 4SW Wk2, 5SW Wk5, 3SW Wk3, 2SW Wk4, 6SW Wk4, 5SW Wk2, 2SW Wk1, 5SW Wk6.

**Tier 1 priority:** 2SW Wk2 (Law/EMT), 3SW Wk5 (Cosmetology), 5SW Wk4 (HVAC), 4SW Wk5 (Automotive), 3SW Wk6 (Entrepreneurship).

**Paused** until teacher feedback is triaged. Teacher feedback may reprioritize the queue.

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

**Infrastructure-blocked (no markdown → printable pipeline exists):**

1. **Student worksheets** for high-stakes summatives (6SW Wk6 Capstone rubric, 4SW Wk2 Career Plan, 5SW Wk5 Budget). Building these requires a PDF / docx export pipeline. Do not ship markdown worksheet drafts as-if they are the final artifact.
2. **Presentation slides** (5SW Wk1 prototype first). Same infrastructure gap.

**Content-actionable (can build in markdown today):**

3. **CFAs for 2SW–6SW** — template exists in `cce-curriculum/notes/cfa-template.md`. Still gated on round-2 teacher feedback on the 1SW CFA.
4. **Teacher edition / answer keys** — only once worksheets exist (blocked).

**Out of scope:** video integration (deferred until after teacher feedback round).

**Worksheet production principle** (per user 2026-04-16): when we build real worksheets, include visuals / diagrams / matching / MCQ item types that approximate STAAR exposure for grade 7. Markdown alone cannot represent those richly; plan for the richer production pipeline.

---

## 8. Non-Negotiables

- **Read before editing:** `CLAUDE.md`, this file, `editing-heuristics.md`. For exit-ticket / objective / DOL edits, also `teks-audit-process.md` + `exit-ticket-templates.md`.
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
