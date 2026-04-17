# PLANNING.md — CCE Curriculum Post-Meeting State

**Last updated:** 2026-04-16 (third session: exit-ticket pilot + TEKS audit process + authoring rulebook relocation)
**Purpose:** Brief any agent on the current state of the CCE curriculum project after the 2026-04-15 teacher meeting.

---

## 0. Next Agent — Start Here

### Read in this order before editing

1. **`CLAUDE.md`** — project rules (updated this session with ESL rule, TEKS audit gate, authoring-rulebook locations)
2. **`PLANNING.md`** §3 (format rules), §8 (non-negotiables), §9 (preservation loop), §10 (lessons learned)
3. **`cce-curriculum/notes/editing-heuristics.md`** — dependency-scope protocol and grep recipes
4. **For exit-ticket / objective / DOL edits:** `cce-curriculum/notes/teks-audit-process.md` + `exit-ticket-templates.md` (new this session)
5. **For CFA edits:** `cce-curriculum/notes/cfa-template.md`

### What shipped this session (2026-04-16, third session)

Three durable systems + one pilot week:

- **Exit ticket authoring system** (new). Ten-format bank in `cce-curriculum/notes/exit-ticket-templates.md` (Diagnostic MCQ with Misconception Distractors, Comparison Matrix, Venn, Mini-Case, Decision Tree, Trade-off / Dilemma, Concept Map, Ranked Justification, 3-2-1 Reflective, Short Constructed Response). Informed by Dylan Wiliam hinge-question research.
- **TEKS audit process** (new). Six-step audit documented in `cce-curriculum/notes/teks-audit-process.md`. Surfaced that H&L is career-exploration content, not natively TEKS-aligned; alignment is CCE's overlay. Audit-gated now: before writing or revising any exit ticket / objective / DOL, confirm the TEKS tag is honestly supported by the day's activities.
- **Authoring rulebooks moved out of teacher-facing space.** `exit-ticket-templates.md` and `cfa-template.md` relocated from `docs/resources/` → `cce-curriculum/notes/`. Nav entries removed. These are dev rulebooks for me, not teacher resources.
- **2SW Wk2 pilot (Law Enforcement / EMT).** All 5 exit tickets rewritten at 6th-7th grade ESL reading level with strict TEKS alignment. Day 4 d(2)(A) tag dropped after audit (activities don't engage training specifics). Milestone tag `exit-ticket-pilot` published for coordinator review at `https://elbrielle.github.io/cce-curriculum/exit-ticket-pilot/`. Commits `0455a0d` → `d4c0795`.
- **Pilot PDFs shipped** at `docs/resources/exit-tickets/2sw-wk2-day{1..5}-*.pdf`, linked from each day's Exit Ticket section. reportlab-generated, sufficient for coordinator preview but confirmed not the long-term tool: writing lines too narrow for middle-school handwriting, page bottoms empty, no visual polish. Next-agent: do NOT invest in reportlab polish; revisit tooling (Figma template + data merge, or rich CSS-print HTML) after coordinator review. See `memory/project_worksheet_production.md`.

### Key insights baked into the system

- **Exit tickets = mastery probes, not engagement activities.** Strictly aligned to a TEKS code ON THAT DAY. Variety across a week (≥3 distinct formats per 5 days). DOK 2+. Investigative or problem-solving, not recall. Under 5 min.
- **ESL reading level (6th-7th grade) for exit-ticket student-facing text.** Short sentences, concrete examples, scaffold word lists for abstract concepts, no TEK codes in the ticket itself.
- **TEKS "such as" language = examples, not exhaustive.** d(4)(F) lists work ethic / integrity / dedication / perseverance "such as" — any genuine workplace characteristic counts. Quality-pick probes with open lists are valid d(4)(F) assessments.
- **H&L vs TEKS is an overlay relationship.** Some TEKS align natively (d(1)(C) career identification). Others require CCE-authored overlay content (d(4)(F) integrity). When the overlay is thin on a given day, drop the TEKS claim from that day rather than forcing the exit ticket to pretend.

### Open for coordinator decision (user is emailing)

- **H&L-vs-TEKS structural question.** Some TEKS that the scope-and-sequence claims are covered by a given H&L chapter are only covered by CCE's overlay, not by the H&L content itself. Coordinator input needed on whether to (a) add supplementary content closing the gap, (b) accept overlay-dependent assessment as sufficient, or (c) retag specific weeks to match what's actually taught.

### Recommended next tasks (post-coordinator email)

1. **Finish 2SW Wk2 pilot** — 6 non-exit-ticket fixes still pending from the instinct review on this week: AI ethics dead reference on Day 5 Activity 4; EMT pathway omission in overview; peer-argument norm on Day 2 Activity 3; Silver Ridge dense read on Day 3; integrity dilemma scaffold on Day 4; presentation math on Day 4. One escalation item (Day 4 teacher scoring load, structural).
2. **Audit another Tier 1 pathway-specific week** using the new TEKS audit + exit-ticket templates: 3SW Wk5 Cosmetology, 4SW Wk5 Automotive, 5SW Wk4 HVAC, or 3SW Wk6 Entrepreneurship.
3. **Round-2 TEKS deepening** — three Implicit codes (d(3)D impact of planning, d(3)F co-curricular, d(4)E community service) have specific suggested edits in `docs/resources/teks-coverage-matrix.md`.
4. **§4.3 C5 Xello vs H&L platform overlap** — hybrid investigation, needs user as Xello SSO hands (described in §4.3).
5. **CFA rollout for 2SW-6SW** — still blocked on round-2 teacher feedback on the 1SW CFA.

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
