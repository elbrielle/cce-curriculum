# CCE Curriculum — Teacher/Writer Instinct Review

**Date:** 2026-04-14
**Reviewer:** Internal (parent orchestrator + 4 Teacher Implementer sub-agents + 1 Curriculum Writer sub-agent per week)
**Scope:** 4 weeks reviewed in depth (1SW Wk0, 5SW Wk1, 4SW Wk1, 6SW Wk6)
**Purpose:** Second-pass review — teacher-instinct checks that grep can't do. Complements the frozen clinical vetting report at `cce-curriculum/notes/vetting-report.md`.

**Method:** For each week, an Explore sub-agent adopted the Teacher Implementer persona (a VILS lab teacher in Irving ISD preparing to teach Monday morning with 24 seventh-graders, 50-min periods, first-year teacher tech reality) and produced a concern list without editing. A second Explore sub-agent adopted the Curriculum Writer persona bound by the non-negotiables in PLANNING.md §8 and triaged each concern as Fix / Defend / Escalate. The parent orchestrator applied Fix rows surgically and logged Defend + Escalate rows for the next teacher meeting.

**What this review does NOT cover:**
- Any dimension already verified in `vetting-report.md` (scripting=0, DOK coverage, timing sums, TEKS year-level coverage, assessment chain coherence)
- All 36 weeks — only 4 reviewed this session
- Any touch to data-seeding activities in 1SW Wk0 Days 2–5 that 4SW Wk1 and 6SW Wk6 consume (RIASEC, Work Values, Building Blocks, My Career Journey reflection)

---

## Week 1 — 1SW Wk0: Classroom Routines & Career Self-Discovery

**Commit applying Fix rows:** (see git log — this section ships in the same commit that applies the fixes)

### Teacher Implementer concerns (12)

1. Day 1 Activities 2 + 3 timing fragile on first day of school (15 min H&L SSO + 12 min scavenger hunt, tech-dependent, no real buffer for SSO failures)
2. Day 4: five Xello quizzes in 25 min unrealistic for first-time users; Activity 2 (14-cluster walkthrough) likely rushed or cut
3. Day 1 Activity 1: Lab Safety Contract + five specific routines dictated in 15 min with zero room for campus-specific lab culture
4. Day 3 Activity 2: "Hard checkpoint" directive ignores pace variance (some students enter 10 Building Blocks while others freeze)
5. Day 3 conceptual density: Work Values + Building Blocks + cluster recommendations + hard checkpoint + app entry in one 50-min day; cluster vocabulary isn't formally introduced until Day 4
6. Day 2 Activity 2: 25-min assessment assumes teacher can run 1-on-1 read-aloud support while monitoring 24 students
7. Day 1 warm-up invites vulnerable self-disclosure before classroom relationships exist
8. Day 5 Gallery Walk logistics vague (poster placement, sticky-dot count, 24-student traffic management)
9. Overview references artifacts that `resources-status.md` lists as "not yet built" (Lab Safety Contract template, My Career Journey handout, Building Blocks word bank)
10. Day 4 + Day 5: 14 CTE cluster posters unsourced; Xello quiz names (Matchmaker, Mission Complete) unverified against district license
11. Days 2–4: six Think-Pair-Share / class-share moments assume social-emotional readiness that doesn't exist yet in week 1
12. Overview asserts "every later recommendation depends on Week 0 data" but has no quality-assurance checkpoint for data integrity

### Triage + decisions

| # | Concern | Triage | Decision + what shipped |
|---|---------|--------|--------------------------|
| 1 | Day 1 tight timing (tech-dependent) | **Fix applied** | Compressed Activity 3 scavenger hunt from 12→10 min (student listing time 5→3 min). Day 1 now sums to 48 min, adding 2 min of slack for SSO troubleshooting. |
| 2 | Day 4 Xello quizzes in 25 min | **Defended** | Scope-and-sequence requires all 5 onboarding quizzes by name. Existing facilitation note permits staggered finish. Teacher may cut Activity 2 cluster walkthrough if quizzes overflow. |
| 3 | Day 1 Lab Safety Contract dictates 5 routines | **Fix applied** (top-priority owner concern) | Converted the five directive bullets into a `!!! tip "Suggested Routine — Adapt to Your Lab Culture"` admonition with explicit framing that every VILS lab is different and teachers should substitute what works in their room. The five routines remain available as a starting point, not a command. |
| 4 | Day 3 "hard checkpoint" directive | **Fix applied** | Replaced "This is a hard checkpoint" with a `!!! note "Checkpoint Guidance"` admonition permitting the teacher to move to Activity 3 while 1–2 stragglers finish, with individual follow-up by Day 4. |
| 5 | Day 3 conceptual density + cluster vocab ordering | **Escalated** | Compressing any single Day 3 activity below 5 min or reordering cluster vocab into Day 3 would alter the data-seeding design and exceed the 15-line surgical limit. Flag for teacher meeting: is the Work Values + Building Blocks density of Day 3 feasible, or should Building Blocks move to Day 4? |
| 6 | Day 2 teacher 1-on-1 read-aloud load | **Fix applied** | Added an explicit peer-scaffolding instruction inside the existing "Common Issue" admonition: pair students needing read-aloud support with fluent-reading peers first, so the teacher only sits 1-on-1 with students who still struggle after peer support. |
| 7 | Day 1 warm-up vulnerability | **Fix applied** | Added "I'm still exploring" / "I'm interested in _____, but I'm not sure yet" as explicit alternative responses so students can opt into a lower-stakes answer without feeling exposed. |
| 8 | Day 5 Gallery Walk logistics | **Fix applied** | Added a `!!! tip "Logistics Tip"` admonition specifying 2–3 sticky dots per student, release-by-table-group traffic management, and poster placement flexibility (walls / boards / standing easels depending on lab layout). |
| 9 | Referenced artifacts listed as "not yet built" | **Escalated** | Production gap, not a curriculum-design defect. Tracked separately in `docs/resources/resources-status.md`. Flag for teacher meeting: agree on priority order for Lab Safety Contract template, My Career Journey handout, and Building Blocks word bank. |
| 10 | 14 cluster posters sourcing + `[VERIFY IN Xello]` quiz names | **Escalated** | Pre-implementation verification gap. Requires district IT/Xello coordination, not curriculum edits. |
| 11 | Think-Pair-Share social readiness | **Defended** | Think-Pair-Share is an IISD instructional strategy named in the overview. Day 2–4 differentiation sections already offer written-first scaffolds. Teacher may substitute private reflection at their discretion. |
| 12 | No data-integrity QA checkpoint | **Defended** | Active Monitoring (IISD strategy) already directs teacher vigilance. Adding a formal QA step would require reshuffling Day 2/3 timing, which touches data-seeding activities. Teacher vigilance is the best available mitigation. |
| Cross-week | Persistent portfolio for My Career Journey reflection | **Fix applied** | Added a `!!! note "Persistent Portfolio — Critical for Mid-Year and Capstone"` admonition on Day 5 explicitly directing the teacher to retain Week 0 reflections in a folder re-issuable at 4SW Wk1 Day 1 and 6SW Wk6 Day 1. Closes a silent data-continuity gap that was one of the top 4SW Wk1 Teacher Implementer concerns. |

### Wk0 summary

- **Fix applied:** 7 in the initial pass (commit `6745afa`) + 2 follow-ups from user feedback (commits `7d24d05` and the Week 0 Flexibility Framework commit)
- **Defended:** 3
- **Escalated to teacher meeting:** 3
- **Timing after edits:** Day 1 = 48 min, Days 2–5 = 50 min each. All in 45–55 range.
- **Scripting regressions:** 0
- **DOK 2–4 markers preserved:** 5/5
- **Support/Extension/ELL bullets preserved:** 5/5

### Wk0 follow-up fixes (post-first-pass user feedback)

**Fix #13 — Day 1 Activity 1 pacing alternatives** (commit `7d24d05`). User feedback: the first pass softened directive *language* but left the 15-min activity *budget* intact; some campuses require a full period (or multi-day distributed) for routines. Added a `!!! warning "Pacing — 15 min is a floor, not a ceiling"` admonition at the top of Day 1 Activity 1 offering three explicit pathways: (1) full-period option with week-shifted activities, (2) dispersed-across-Days-2–5 option, (3) 15-min default.

**Fix #14 — Week 0 Flexibility Framework** (this commit). User feedback: single-activity admonitions are not enough — Week 0 is structurally different from every other week because campus-mandated events (Bowie Cub Camp, ID photos, orientations, fire drills, AUP delays), tech-access restrictions, roster churn, and teacher-specific culture-setting all mean the whole week needs flexibility, not just one activity. Added:

- A new **Week 0 Flexibility Framework** section in `overview.md` (placed right before "Week at a Glance") that:
    - Names Week 0 as structurally different and enumerates the reasons (campus events, tech access, roster churn, culture-setting, social readiness)
    - Identifies the four **load-bearing** activities (Day 2 RIASEC, Day 3 Work Values, Day 3 Building Blocks, Day 5 My Career Journey reflection) that must land somewhere this week or early Wk1
    - Identifies **flex** activities that can be cut, moved, compressed, or substituted (Day 1 routines, Day 1 scavenger hunt, Day 4 cluster ratings, Day 5 Design Thinking, Day 5 Gallery Walk)
    - Provides **5 resequencing playbooks** for common disruptions: lost 15 min on Day 1 (e.g., Cub Camp), lost 15 min on both Days 1 and 2, no Chromebook access Day 1, no Chromebook access Days 1–2, Wk0 slipping into Wk1
    - Ends with the bottom-line rule: if the 4 load-bearing activities land and students sign the safety contract before leaving Wk0 (or early Wk1), the week objective is met
- Short `!!! note "Campus flexibility"` pointer admonitions at the top of `day1.md` and `day2.md` directing teachers who start at the day file to the framework in the overview. Day 2's pointer specifically names the RIASEC assessment as load-bearing since Day 2 is the assessment day.

**Lesson for the next instinct review session:** Week 0 is the ONLY week where the entire week structure (not just individual activities) needs a flexibility framing. All 35 other weeks can assume full teacher control of 50-min periods. When reviewing a week, ask: "Is this week's ability to run as written dependent on campus conditions I cannot guarantee?" If yes, the week needs a framework, not just per-activity admonitions. For the other 35 weeks this almost always means "no" — they inherit from a stable mid-year classroom reality — but Week 0 is the exception and should be treated structurally, not piecemeal.

---

## Week 2 — 5SW Wk1: Blueprint Builders / Architecture Careers (PROTOTYPE)

**Commit applying Fix rows:** `89614f4`

### Teacher Implementer concerns (10)

1. Day 3 Activity 1: 10 min for TinkerCAD SSO + workspace orientation for 24 students likely to stall on first use
2. Day 3 Activity 2: Teaching 5 TinkerCAD skills with visual checkpoints in 15 min; Hole tool is "most common confusion point" and gets a 3-min slot
3. Day 3 Activity 3: Sequential teacher sketch approval = 48–72 min bottleneck compressed into 15 min
4. Day 3 → Day 4 time debt (Day 3 ends with "4 walls grouped"; Day 4 assumes walls + roof built + grouped by minute 7)
5. Day 4 Checkpoint 3: "one detail element" aspirational for a student still debugging the Hole tool
6. Day 4 Trash to Treasure: 6 substeps (read scenario + choose space + 2 detailed sketches + sustainable feature + partner presentation) in 20 min is compressed
7. Day 5 Activity 1 Presentations: 24 students × 2 min = 48 min, but activity is capped at 20 min — math doesn't work
8. Day 5 Activity 3: eDynamic Unit 3.1 `[VERIFY IN eDynamic]` flag + a packed Day 5 makes it a placeholder
9. Day 1 Activity 2 Safety Supervisor: 5 min research + 15 min design (5 rules + equipment list + safety map) + DOK 2 extension competes for same 20-min window
10. Overview/infrastructure: H&L workbook distribution + TinkerCAD account readiness is assumed but not verified in resources-status.md

### Triage + decisions

| # | Concern | Triage | Decision + what shipped |
|---|---------|--------|--------------------------|
| 1 | TinkerCAD SSO fragility on first use | **Fix applied** | Replaced the thin "Common Issue" warning on Day 3 with a `!!! tip "Tech Setup — verify BEFORE class"` admonition naming the IT whitelisting requirement (`tinkercad.com`, `*.autodesk.com`), a 2-student pre-test, and a paper-sketch fallback path. Inherited pattern for any other TinkerCAD week. |
| 2 | 5 skills + Hole tool in 15 min | **Defended** | The Skill Builder uses a teach-practice-check cadence (3–4 min per skill with visual thumbs-up check) designed for fast reteach during the sketch-approval window. The Hole tool gets a dedicated facilitation tip; Skill 5 is an application of Skill 4, not a new skill. |
| 3 | Day 3 sketch approval bottleneck | **Fix applied** | Replaced sequential teacher approval with a 3-item peer/self checklist + 30-sec teacher spot-check. Cuts approval time from a theoretical 48–72 min to ~10 min across the class without removing the quality gate. |
| 4 | Day 3 → Day 4 time debt | **Fix applied** | Added an explicit 5-min catch-up allowance to Day 4 Checkpoint 1 for students who didn't finish walls + roof on Day 3, with a named teacher-check gate before they start on holes. |
| 5 | Day 4 Checkpoint 3 detail element | **Defended** | Checkpoint 3 is explicitly "stretching" beyond the minimum spec. Students still debugging holes focus on Checkpoints 1–2 and submit what they have. Clipboard checks are binary, not qualitative. |
| 6 | Day 4 Trash to Treasure substeps overflow | **Fix applied** | Reduced Step 2 to ONE required sketch perspective (map view OR feature sketch, not both), with the second as optional-if-time. Keeps the activity in the 20-min window without cutting core learning. |
| 7 | Day 5 presentation math | **Fix applied** | Replaced the vague "split into corners" tip with a `!!! warning` naming the math explicitly (24 × 2 min > 20 min activity cap) and offering three concrete approaches: (A) live+async hybrid, (B) 3-corner rotation, (C) panel + standouts. Teacher picks based on room culture. |
| 8 | Day 5 eDynamic 3.1 placeholder | **Escalated** | The `[VERIFY IN eDynamic]` flag is a platform-access question for district admin, not a curriculum edit. Flag for teacher meeting: once the district confirms what Unit 3.1 actually contains, replace the placeholder with a concrete activity spec. |
| 9 | Day 1 Safety Supervisor DOK 2 competes with design time | **Fix applied** | Moved the DOK 2 underwater-vs-skyscraper comparison explicitly to extension / homework so the 15-min design window focuses on the underwater scenario only. |
| 10 | Infrastructure assumptions | **Fix applied** | Added a `!!! tip "Teacher Prep Checklist"` to the overview.md Materials section with three pre-week items: H&L workbook distribution, TinkerCAD account test, IT domain whitelisting. Inherited pattern — this checklist shape should propagate to other tool-dependent weeks in a later session. |

### 5SW Wk1 summary

- **Fix applied:** 7
- **Defended:** 2
- **Escalated to teacher meeting:** 1
- **Timing after edits:** Day 1=50, Day 2=55, Day 3=50, Day 4=50, Day 5=55. All 45–55.
- **Scripting regressions:** 0
- **DOK 2–4 markers preserved:** 5/5
- **Support/Extension/ELL bullets preserved:** 5/5

---

## Week 3 — 4SW Wk1: Career Planning (Mid-Year Reflection)

**Commit applying Fix rows:** `f612edf`

### Teacher Implementer concerns (10)

1. Day 1 Activity 2 Favorites Audit: cold access to Week 0 data 18 weeks later; absent/transfer students never entered RIASEC
2. Day 1 "reconstruct from memory" for students with zero favorites: unreliable for 18-week-old data
3. Day 1 warm-up assumes students still have a copy of their Week 0 My Career Journey reflection; no confirmation teacher has returned it
4. Day 2 H&L Career Plan tool may not be active for Irving ISD; facilitation note flags paper backup but no pre-class verification
5. Day 2 Iceberg activity: 18 weeks of exploration recall is cognitively heavy; workbook says "flip back" but no additional scaffold
6. Day 3 Xello Quick Sims: `[VERIFY IN Xello]` flag on "The Real Game" — may not exist under that name in district license
7. Day 4 eDynamic Unit 8.1: `[VERIFY IN eDynamic]` flag — unit may not exist or cover the stated objective
8. Day 5 warm-up: "Pull out your Week 0 My Career Journey reflection" with no Day 1 setup confirming it's returned
9. Day 5 pathway dot-vote gallery walk: 10 printed cluster posters become outdated if pathways shift mid-year
10. House-of-cards weekly flow: Day 1 output → Day 2 input → ... → Day 5 summative; only 1 formative checkpoint

### Triage + decisions

| # | Concern | Triage | Decision + what shipped |
|---|---------|--------|--------------------------|
| 1 | Cold access to Wk0 data | **Fix applied** | Added a `!!! note "Before the Warm-Up — Return Week 0 Reflections"` on Day 1 directing the teacher to (a) hand back the Week 0 folder retained per the new Wk0 Day 5 Persistent Portfolio admonition, (b) give absent / transfer students a same-day Discover My Core retake as their personal baseline, (c) have every student open the Climber Profile NOW so login/data-access issues surface before the activity. |
| 2 | "Reconstruct from memory" is unreliable | **Defended** | The activity is the *reflection*, not historical accuracy. The facilitation note explicitly permits memory-based reconstruction and frames the point as growth, not precision. |
| 3 | Day 1 warm-up assumes returned artifact | **Fix (covered by #1)** | The Day 1 pre-warm-up admonition explicitly directs the teacher to hand the folder back now, closing this gap. |
| 4 | Day 2 Career Plan tool may not be active | **Fix applied** | Added a `!!! tip "Facilitation Tip — Verify Before Class"` at the top of Day 2 Activity 2 directing the teacher to confirm the Career Plan tool loads in a test account before class. Names a concrete fallback path (skip to Activity 3 + printed Irving ISD poster + workbook template). |
| 5 | Day 2 Iceberg 18-week recall | **Defended** | The workbook already instructs students to "flip back through earlier chapters or browse the H&L app for reminders." The Support differentiation bullet adds a pre-built template with labeled zones (Skills, Sacrifices, Practice, People Who Helped). Sufficient scaffolding. |
| 6 | `[VERIFY IN Xello]` Quick Sims Real Game | **Escalated** | Platform-access question for district admin. If the game doesn't exist under that name, the activity needs a backup Sim or pivots — that's a redesign, not an edit. Flag for teacher meeting. |
| 7 | `[VERIFY IN eDynamic]` Unit 8.1 | **Escalated** | Same class of platform-access blocker. Flag for teacher meeting. |
| 8 | Day 5 warm-up assumes returned artifact | **Fix (covered by #1)** | The Day 1 pre-warm-up admonition now guarantees the folder is in hand on Day 1, so Day 5 can safely assume it. |
| 9 | Cluster poster outdated-ness | **Defended** | Known maintenance burden, not a design flaw. The DOK 4 prompt ("Are popular pathways the best pathways?") already cues students to question the gallery walk. Teacher can annotate posters with sticky notes mid-year. |
| 10 | House-of-cards weekly flow | **Escalated** | Adding an explicit early-week formative checkpoint is structural. Not a single-file edit. Flag for teacher meeting: should Day 2 add a "Day 1 output check" before proceeding? |

### 4SW Wk1 summary

- **Fix applied:** 2 unique (+ 2 concerns covered by those fixes)
- **Defended:** 3
- **Escalated to teacher meeting:** 3
- **Timing after edits:** Day 1=50, Day 2=50, Day 3=51, Day 4=50, Day 5=50. All 45–55.
- **Scripting regressions:** 0
- **DOK 2–4 markers preserved:** 5/5
- **Support/Extension/ELL bullets preserved:** 5/5

---

## Week 4 — 6SW Wk6: Capstone / Final Career Plan & Presentations

**Commit applying Fix rows:** `25a60db`

### Teacher Implementer concerns (10)

1. Day 3/4 Capstone Presentations timeline math: 12–13 × 5 min = 60–65 min > 50-min period
2. Day 1 optional RIASEC retake: `[VERIFY IN H&L]` flag on retake comparison feature
3. Day 4 Career Plan PDF export: second `[VERIFY IN H&L]` flag; export failure on a high-demand day is unrecoverable
4. Day 2 Activity 1: assumes Day 1 Career Plan is complete; no recovery for students who didn't finalize
5. Days 3/4: teacher scores rubric while facilitating warm-up, timer, peer feedback, applause — no co-facilitator
6. Day 1 Chromebook + H&L reliability on highest-demand day (end of May, OS updates, SSO quirks)
7. Day 1 Career Plan finalization: disengaged student freezes; teacher can only coach 1-on-1
8. Day 5 end-of-year reflection: H&L data persistence risk through May server maintenance
9. Day 2 30/90/365-day action step timeframes: 40% of 7th graders will write placeholders
10. Day 5 celebration framing: fragile in end-of-year chaos

### Triage + decisions

| # | Concern | Triage | Decision + what shipped |
|---|---------|--------|--------------------------|
| 1 | Presentation math | **Fix applied** | Replaced the vague "Tight. Use compression techniques if needed" paragraph on Day 3 with a `!!! warning` naming the math explicitly and offering three concrete compression approaches (2.5–3 min per student, corner rotation, or co-facilitator model). Teacher picks before Day 3 begins. |
| 2 | RIASEC retake `[VERIFY IN H&L]` | **Defended (now actionable)** | The flag remains in place on Day 1; the new pre-capstone teacher checklist on overview.md now makes it an explicit week-before teacher task rather than prose buried in an activity. |
| 3 | PDF export `[VERIFY IN H&L]` | **Fix applied** | Added an explicit day-of backup plan to the existing Day 4 VERIFY flag: if simultaneous PDF export fails, students print via browser Print → PDF or screenshot + email. Every student leaves Day 4 with an artifact in some form. |
| 4 | Day 2 assumes Day 1 completion | **Fix (covered by #7)** | The Day 1 "Engagement Variability" compressed path guarantees every student leaves Day 1 with a starting Career Plan, closing this gap without a separate Day 2 edit. |
| 5 | Teacher simultaneous scoring + facilitation | **Escalated** | Structural workflow gap that would require staffing (co-facilitator) or redesigning Day 3/4 structure. Not a single-file edit. Flag for teacher meeting. |
| 6 | End-of-May platform reliability | **Fix applied** | Added the pre-capstone teacher checklist admonition on overview.md consolidating H&L access test, Chromebook fleet spot-check, Week 0 reflection folder retrieval, and the existing VERIFY items into one actionable weekly task. |
| 7 | Day 1 Engagement Variability single-point-of-failure | **Fix applied** | Added a "fewer than 5 careers" compressed browse-and-finalize path to the existing facilitation tip on Day 1. Disengaged students get a fast on-ramp ("pick 3 that sound interesting right now") so they leave Day 1 with a starting plan, not stuck on "top career interest." |
| 8 | H&L data persistence risk | **Escalated (mitigated by Wk0 fix)** | Platform integrity risk outside curriculum control. The 1SW Wk0 Day 5 Persistent Portfolio admonition shipped in commit `6745afa` provides a paper baseline students can reference if H&L data is unavailable. Flag for teacher meeting: should 6SW Wk6 Day 5 add a "pull out Wk0 folder if H&L is unavailable" note to complete the mitigation? |
| 9 | 30/90/365 action steps | **Defended** | The Day 2 facilitation tip already coaches "What CAN you do in 30 days? Send one email? Read one article? Talk to one person?" — realistic scaffolding. Some students will write shallow action steps; that's developmentally normal for 7th grade. |
| 10 | End-of-year celebration fragility | **Defended** | Emotional-tone and operational concern beyond curriculum control. The week's structural design is sound; teachers navigate May chaos as they always do. |

### 6SW Wk6 summary

- **Fix applied:** 4 unique (+ 1 concern covered by those fixes)
- **Defended:** 3
- **Escalated to teacher meeting:** 2
- **Timing after edits:** Day 1=55, Day 2=50, Day 3=50, Day 4=55, Day 5=50. All 45–55.
- **Scripting regressions:** 0
- **DOK 2–4 markers preserved:** 5/5
- **Support/Extension/ELL bullets preserved:** 5/5

---

## Cross-week themes (final)

The four Teacher Implementer concern lists converged on five cross-cutting patterns. Three were addressed during this pass; two are escalated to the next teacher meeting.

1. **Tech fragility — ADDRESSED.** SSO failures, account setup, Chromebook cart logistics, and H&L/Xello/TinkerCAD login issues were consistently under-budgeted. Fixed via `!!! tip "Tech Setup"` admonition on 5SW Wk1 Day 3 (TinkerCAD domain whitelisting + 2-student pre-test), `!!! tip "Teacher Prep Checklist"` on 5SW Wk1 overview.md, `!!! tip "Facilitation Tip — Verify Before Class"` on 4SW Wk1 Day 2 (H&L Career Plan tool), and `!!! note "Pre-Capstone Teacher Checklist"` on 6SW Wk6 overview.md. The checklist-admonition shape is the working pattern; later sessions should propagate it to other tool-dependent weeks.
2. **Data continuity across time — ADDRESSED.** 4SW Wk1 Day 1, 4SW Wk1 Day 5, and 6SW Wk6 all silently assumed students could access Week 0 artifacts 18–36 weeks later, but Wk0 provided no explicit "save this" framing. The single root cause is now closed by the cross-week fix on Wk0 Day 5 (`!!! note "Persistent Portfolio"`) plus downstream complementary fixes on 4SW Wk1 Day 1 (pre-warm-up folder retrieval + transfer-student fallback) and 6SW Wk6 overview.md (pre-capstone checklist item for folder retrieval).
3. **Directive vs. suggestion language — ADDRESSED (owner's top priority).** Most concentrated in Wk0 but visible in other weeks' routine-setting moments. Converted to `!!! tip "Suggested Routine — Adapt to Your Lab Culture"`, `!!! note "Checkpoint Guidance"`, and `!!! note "Campus Variation"` admonitions that frame content as teacher-adaptable advice rather than commands. The pattern is now established and reusable.
4. **Presentation math — ADDRESSED (both affected weeks).** 24 students × 2–5 min > 50-min period. Fixed on 5SW Wk1 Day 5 with a `!!! warning` offering three concrete approaches (live+async hybrid, 3-corner rotation, panel + standouts) and on 6SW Wk6 Day 3 with a matching `!!! warning` offering three compression approaches (2.5–3 min per student, corner rotation, co-facilitator). Also noted in the 6SW Wk6 pre-capstone checklist.
5. **Resource backlog leakage — ESCALATED.** Several daily plans reference artifacts that `docs/resources/resources-status.md` lists as "not yet built" (Lab Safety Contract template, My Career Journey handout, Building Blocks word bank, RIASEC vs. Favorites worksheet, Capstone Presentation Rubric). This is a production gap, not a curriculum-design defect. Priority order for authoring is in PLANNING.md §9. Flag for teacher meeting.

## Escalated to the next teacher meeting

Items that need a human decision — the curriculum writer couldn't fix these within the non-negotiables, and the teacher meeting is the right place to resolve them.

- **1SW Wk0 Day 3 conceptual density** — Work Values + Building Blocks + cluster recommendations in one 50-min day. Should Building Blocks move to Day 4 (where cluster vocabulary is formally introduced)? Would require re-sequencing Days 3 and 4.
- **1SW Wk0 referenced-but-unbuilt artifacts** — Lab Safety Contract template, My Career Journey handout, Building Blocks word bank. Agree on priority + authorship ownership.
- **1SW Wk0 14 cluster posters + `[VERIFY IN Xello]` quiz names** — Pre-implementation verification for Matchmaker + Mission Complete against the actual district license.
- **5SW Wk1 Day 5 eDynamic Unit 3.1 placeholder** — Replace `[VERIFY IN eDynamic]` flag with a concrete activity spec once district admin confirms what Unit 3.1 actually contains.
- **4SW Wk1 Day 3 `[VERIFY IN Xello]` Quick Sims "The Real Game"** — Verify the game exists under that name; if not, redesign Day 3 around a backup Sim.
- **4SW Wk1 Day 4 `[VERIFY IN eDynamic]` Unit 8.1** — Verify the unit covers "strategies for matching assessments to careers"; if renamed or missing, redesign Day 4.
- **4SW Wk1 house-of-cards weekly flow** — Should Day 2 add an explicit early-week formative checkpoint (verify Day 1 output before proceeding)? Adding a checkpoint touches the weekly pacing.
- **6SW Wk6 Days 3/4 simultaneous scoring + facilitation** — Structural workflow gap. Needs a staffing decision: can the district commit to a co-facilitator (admin / counselor / another VILS teacher) for the 4 capstone presentation periods?
- **6SW Wk6 Day 5 H&L data persistence mitigation** — Should Day 5 add a "pull out your Wk0 folder if H&L is unavailable" note to complete the mitigation shipped via the 1SW Wk0 Day 5 Persistent Portfolio admonition?

## Session totals (morning session 2026-04-14)

- **Weeks reviewed in depth:** 4 (1SW Wk0, 5SW Wk1 prototype, 4SW Wk1, 6SW Wk6)
- **Teacher Implementer concerns lobbed:** 42 (12 + 10 + 10 + 10)
- **Fix rows applied:** 20 (7 + 7 + 2 + 4)
- **Concerns defended:** 11 (3 + 2 + 3 + 3)
- **Concerns escalated to teacher meeting:** 11 (3 + 1 + 3 + 2, plus the 2 cross-week structural items)
- **Commits landed:** 4 (`6745afa`, `89614f4`, `f612edf`, `25a60db`)
- **Files touched:** 16 (4 Wk0 day files + 1 report = 5 in `6745afa`; 5 Wk1 files in `89614f4`; 2 4SW Wk1 day files in `f612edf`; 4 Wk6 files in `25a60db`)
- **Lines changed:** small — no single day file exceeded ~12 lines of edit (below the 15-line redesign threshold)
- **Verification at session end:** `mkdocs build --strict` clean, scripting=0 globally, DOK 2–4 present on all 180 daily plans, global timing loop clean (all day files 45–55 min), Support/Extension/ELL bullets preserved globally.

---

## Week 5 — 2SW Wk5: Powerskills-Communication (Session 2026-04-14 evening)

**Why this week:** writer-reached slot week — original S&S had a blank Topic field, and the writer slotted H&L Powerskills modules (Conflict Resolution, Feedback, Written Communication, Advocacy) + teacher-led healthcare role-plays. Highest risk of writer improvisation drift per §10.

**Protocol used:** Teacher Implementer spawned as Explore sub-agent; Writer triage done in-session by parent (per §10 lesson 10 — don't over-use sub-agents for predictable triage).

**Top Teacher Implementer concerns (8 lobbed):**
1. Day 1 Activity 3 (Smoothie Conflict) 22 min too tight for groups + chart + ad sketch
2. Day 2 tonal pivot from "favorite food" to "nurse delivering bad news" is jarring mid-period
3. Day 3 Mobile Farmers' Market preview is dead 12 min that never produces a deliverable
4. Day 4 crams 4 separate writing tasks (Little Library + 3 healthcare cards) in 34 min
5. Day 5 stacks 5 activities back-to-back on Friday — "breather week" in name only
6. Healthcare role-play cards listed as "teacher-prepared, 8-10 cards" with no template and no Teacher Prep admonition
7. "Breather week" framing in Career Connection contradicts actual 4-activity-per-day workload
8. Day 1 A3→A4 transition physically impossible if A3 runs over (second-order effect of #1)

**Writer triage: 6 Fix, 2 folded.**

| # | Concern | Fix |
|---|---------|-----|
| 1 | Day 1 A3 too tight | Re-time A3 22→25, A4 8→5; add pressure-valve facilitation tip |
| 2 | Day 2 tonal pivot | Add 2-line mode-shift framing at the Healthcare Role-Play pivot |
| 3 | Day 3 Advocacy preview dead | Cut Mobile Farmers' Market preview; reframe as self-advocacy lens into SMART goals; A1 12→10, A3 18→20 |
| 4 | Day 4 writing crammed | Simplify A3 partner logistics — cards assigned by row, not "find a different-card partner" |
| 5 | Day 5 Friday overload | Merge SMART Refinement into Reflection as one 15-min closing block (3 activities instead of 4) |
| 6 | No Teacher Prep | Add Track A1 Teacher Prep Checklist admonition — role-play card authoring, H&L Powerskills workbook access, Xello + CareerOneStop whitelist |
| 7 | "Breather" framing | Drop "students slow down" sentence; reframe as "mode changes — less reading of clusters, more hands-on practice" |
| 8 | A3→A4 transition | Folded into #1 |

**Commit:** `002b955` — 6 files, +30/-32 lines. Largest single-file edit: day5.md at 6 net lines. All under the 15-line threshold.

**Escalated:** none.

---

## Week 6 — 6SW Wk5: Job Skills & Mock Interview (Session 2026-04-14 evening)

**Why this week:** d(6)+d(7) heaviest TEKS week of the year (6 standards in 5 days). Thin H&L support; print-heavy prep. Track A3 had already trimmed "feel real" fluff from Day 5 — check if more remains.

**Protocol used:** Writer triage done in-session; no sub-agent for this week (by now I had calibrated the instincts on 2SW Wk5).

**Top instinct concerns (6 identified, all Fix):**

| # | Concern | Fix |
|---|---------|-----|
| 1 | 6 printables + no Teacher Prep Checklist (Cover Letter Template, Sample Application, References Guide, Mock Interview Question Cards, Rubric, sample job posting) | Add Track A1 admonition adapted for print-heavy prep — ~60 min of authoring + copy-room turnaround |
| 2 | Day 1 A3 says "four sections" but numbers 6 items (Header, Greeting, 3 Body Paragraphs, Closing) | 1-line fix: "six parts" |
| 3 | Day 3 A1 asks students to write real PII (name, address, DOB, phone, email) on a paper application that could circulate | Add privacy guidance — students may substitute a sample identity; collect and shred forms at end of class |
| 4 | Day 3 A1 15-min activity contradicts its own facilitation tip "real applications take 30-45 minutes" | Add explicit subset-scoping note — today is the "first pass" (Personal + Education + Skills + Availability + Signature); References + Employment History are Activity 2 work or homework |
| 5 | Day 4 TEKS claim d(6)(C) overreaches — fishbowl has 1 volunteer, not all students | Drop d(6)(C) from Day 4 Lesson Overview TEKS line (retained on Day 5 where every student participates) |
| 6 | Day 5 Facilitation Tip still had "Treat this with real seriousness" lead-in (Dim 9-adjacent declarative fluff) after Track A3 trimmed the "feel real" fragment | Trim lead-in; keep concrete actions only (wear professional clothes, greet at door with handshake + eye contact) |

**Commit:** `5275409` — 5 files, +17/-3 lines. Largest single-file edit: overview.md at 9 net lines. All well under the 15-line threshold.

**Escalated:** none.

---

## Week 7 — 4SW Wk2: Course Mapping / Career Plan Finalization (Session 2026-04-14 evening)

**Why this week:** the d(8)(C) artifact week — the single highest-stakes deliverable of the year. Directly adjacent to 4SW Wk1 reviewed in morning session.

**Protocol used:** Writer triage done in-session.

**Top instinct concerns (2 identified, 3 defended):**

| # | Concern | Decision |
|---|---------|----------|
| 1 | **Clinical catch:** Day 5 sums to 53 min (within §10 45-55 tolerance but over PLANNING §4 Dim 5 preferred 48-52 range) | **FIX** — trim A1 Gather All the Pieces 10→7 min; sums clean to 50 |
| 2 | 4 VERIFY flags across the week + load-bearing bilingual Family Letter that doesn't exist in default H&L materials + no Teacher Prep Checklist | **FIX** — add Track A1 admonition naming the Family Letter as a 30-45 min authoring prerequisite (not an H&L default) + H&L Course Planner verification + eDynamic 6.2 + Texas OnCourse + College For All Texans whitelist |
| 3 | Day 1 A1 dense lecture on Texas HS graduation structure (22 credits, 5 endorsements) | **DEFEND** — unavoidable content delivery for the transition topic; current projected-summary + walkthrough is the best approach within the time budget |
| 4 | Day 2 A2 25-min tight for first-time H&L Course Planner users | **DEFEND** — the 25-min budget is generous for the normal tool-ready path; paper template is the documented fallback |
| 5 | Day 5 A2 25-min Career Plan write-up is tight for 8-section synthesis | **DEFEND** — template has sentence stems, bullet-point format is allowed, Support row includes pre-filled modified template |

**Commit:** `3948d98` — 2 files, +11/-1 lines. Largest single-file edit: overview.md at 10 net lines. Well under threshold.

**Escalated:** none. The bilingual Family Letter resource gap is already tracked in `resources-status.md`.

---

## Cross-week themes — Session 2 additions

- **Writer improvisation drift pattern confirmed.** 2SW Wk5 (slot week) had 8 concerns and required the most structural edits. 4SW Wk2 (heavily scoped, d(8)(C) artifact) had 2 concerns. 6SW Wk5 (thin H&L, heavy supplement) had 6 concerns. Conclusion: weeks where the writer had more editorial freedom (blank S&S topic, thin workbook anchor) need tighter instinct review. Weeks where S&S column 5 lists specific activities are mostly clean clinically and need lighter review.
- **Teacher Prep Checklist adoption is incomplete.** All 3 reviewed weeks were missing the admonition. Track A1 (`fc1c4dd`) propagated it to 9 weeks based on tech-tool criteria, but "has teacher-authored prep materials" is a second trigger the A1 sweep didn't catch. The new checklists landed in 2SW Wk5, 6SW Wk5, 4SW Wk2 address print-heavy + teacher-authored-resource gaps. Future Track B reviews should add the admonition wherever absent.
- **PII in paper artifacts is a pattern to watch for.** 6SW Wk5 Day 3 was the clearest case, but the same risk likely exists in other weeks that have paper "personal information" forms. Flag candidate for a cross-week grep in a future session: `grep -rn "legal name\|date of birth\|DOB\|home address" docs/`.
- **Breather-week framing is a trap.** The 2SW Wk5 "breather" label did not match the actual 4-activity-per-day Day 1-5 workload. If a week is *framed* as a breather, the facilitation notes and activity counts must actually support lower cognitive load, not just the Career Connection copy. One data point — watch for the same pattern if other "skills focus" weeks get reviewed.

---

## Session 2026-04-14 evening totals

- **Weeks reviewed:** 3 (2SW Wk5, 6SW Wk5, 4SW Wk2)
- **Concerns identified:** 16 (8 + 6 + 2)
- **Fix rows applied:** 14 (6 + 6 + 2)
- **Defended:** 3 (4SW Wk2)
- **Folded (duplicates):** 1 (2SW Wk5 concern #8 folded into #1)
- **Escalated:** 0 (no new items for the escalation queue)
- **Commits landed:** 3 (`002b955`, `5275409`, `3948d98`)
- **Files touched:** 13 (6 + 5 + 2)
- **Lines changed:** +58 / -36 total. Largest single-file edit: 2SW Wk5 overview.md at 13 net lines (still under 15-line threshold).
- **Verification:** all three commits passed the 6-check preservation loop (`mkdocs --strict`; scripting=0; DOK 2-4 present on all 15 reviewed day files; timing sums 50/50/50/50/50 on all 3 weeks; Support+ELL preserved; Dim 9 fluff=0).

**Running cumulative totals across both sessions:**

- **Weeks reviewed:** 7 of 36 (1SW Wk0, 5SW Wk1 prototype, 4SW Wk1, 6SW Wk6, 2SW Wk5, 6SW Wk5, 4SW Wk2)
- **Concerns:** 58 lobbed → 34 Fix / 14 Defend / 11 Escalate / 1 Folded
- **Commits:** 7 instinct-review commits
- **Remaining weeks to instinct-review:** 29

---

## Week 8 — 5SW Wk5: Personal Budget (Session 2026-04-15 Track B)

**Why this week:** highest-stakes standalone summative in 5SW — d(5)(D) personal budget — and two load-bearing teacher-authored resources (Personal Budget Template + DFW Cost Reference Sheet) are flagged as "not yet built" in `resources-status.md`. Strong A5 candidate (teacher-authored resource second-pass trigger).

**Protocol used:** Teacher Implementer spawned as Explore sub-agent; Writer triage done in-session.

**Top Teacher Implementer concerns (10 lobbed):**

1. Day 2 math prerequisite unstated; 3-check protocol leaves min 0-8 unmonitored — the period when calculator errors on `salary ÷ 12 × 0.75` cascade into the rest of the budget
2. Day 2 deliverable "all expense categories filled in" too rigid if the template is built in simplified form for Support
3. Personal Budget Template + DFW cost reference both "not yet built" → Monday-morning block for an unprepared teacher
4. Day 3 CareerOneStop district filter risk with no fallback
5. Day 4 three-module paralysis (NGPF / EverFi / Practical Money Skills) with no pre-selection guidance
6. Day 2 facilitation tip on negative balances frames the "career vs. lifestyle" realization as a "core learning moment" — emotionally unsafe for students whose family works in lower-wage careers; Day 5 TPS bullet "Whose budget balanced without cutting anything?" amplifies the income-disparity reading
7. Day 5 3-career chart in 15 min too tight if students must pull salary data for 3 careers from H&L without pre-identification
8. Summative spec blurs formative/summative across Day 2, 3, 5 deliverables — unclear which three artifacts are the submission
9. Day 4 "Paying for College" 12-min walkthrough for 4 methods + DOK compressed
10. H&L SSO + Ch 16 workbook access unverified for all students

**Writer triage: 9 Fix, 1 Defend.**

| # | Concern | Fix |
|---|---------|-----|
| 1 | Day 2 math + check timing | Retime Check 1 from min 8 → min 5 (Checks 2/3 to 15/22) so gross-to-net errors are caught before they cascade; add brief "why earlier" parenthetical |
| 2 | Day 2 deliverable rigidity | Soften "all expense categories" → "all major expense categories + calculated balance" |
| 3 | Unbuilt artifacts | Add **Teacher Prep Checklist** admonition to overview (A5 second-pass trigger) — names the two unbuilt artifacts with ~60-90 min weekend prep estimate |
| 4 | CareerOneStop filter | Folded into Teacher Prep Checklist ("test careeronestop.org Friday on student Chromebook; escalate to district IT if blocked") |
| 5 | Day 4 module paralysis | Folded into Teacher Prep Checklist (NGPF recommended as default; test login flow on one Chromebook before Monday) |
| 6 | Emotional safety on negative balances + Day 5 TPS amplifier | (a) Day 2 facilitation tip reframed — removed "core learning moment" declarative; added explicit family-career protection ("the same career supports many real lifestyles"). (b) Day 5 TPS bullet "Whose budget balanced without cutting anything?" replaced with lifestyle-focus reframe |
| 7 | Day 5 3-career chart tight | Add facilitation tip on Day 5 Activity 2 directing teacher to give first 2 min for pre-identification inside the existing 15-min budget — no timing change |
| 8 | Summative spec blurred | Clarify overview Summative section: all three artifacts submitted as a single Day 5 portfolio; Day 2 + Day 3 named as formative carry-forward |
| 9 | Day 4 FAFSA walkthrough 12 min | **DEFEND** — d(3)(C) TEKS scope is *identify methods*, not analyze depth. 12 min is survey-level matching the standard; 6SW Wk6 revisits aid in capstone |
| 10 | H&L access unverified | Folded into Teacher Prep Checklist |

**Commit:** `6812dd9` — 3 files, +19/-7 lines. Largest single-file edit: overview.md at 13 net lines. All under the 15-line threshold.

**Escalated:** none. Production gap on unbuilt artifacts already tracked in `resources-status.md`.

---

## Week 9 — 3SW Wk3: Sustainable Engineering (Session 2026-04-15 Track B)

**Why this week:** cross-cluster bridge week; H&L Ch 2 "Ag-Tech Pest Patrol" drone-design Career Lab is the anchor (4-day project). Topic was populated in S&S with a named eDynamic unit — lower writer-drift risk than 2SW Wk5, but still a "reach" week because H&L col 5 listed only pathway-level activities (no named chapter project). The writer grounded the implementation to the Pest Patrol Career Lab, which grep-verified in HatsandLadders.txt.

**Protocol used:** Teacher Implementer spawned as Explore sub-agent; Writer triage done in-session.

**Top Teacher Implementer concerns (8 lobbed):**

1. Day 1 NASA Climate Kids 15-min block has no fallback if blocked by district filter
2. Day 2 timing math — 25 min for 3 sets of field notes @ 6 min each + summary worksheet
3. Day 3 rationale paragraph (4-5 sentences) redundant with label content
4. Day 3 checkpoint clipboard for 24 students in 25 min = ~60 sec/student (unrealistic)
5. Day 4 Societal Trends "Careers Declining" column politically charged in Irving ISD family-job context
6. Day 4 peer feedback 20 min too tight for 2 explanations + rubrics + revisions
7. Day 5 eDynamic Unit 7.1 VERIFY block has no concrete fallback
8. d(5)(C) Societal Trends feels isolated from the drone-design work — weak conceptual bridge

**Writer triage: 8 Fix, 0 Defend, 0 Escalate.**

| # | Concern | Fix |
|---|---------|-----|
| 1 | NASA Climate Kids fallback | Add `!!! note` in Day 1 Activity 2 — NOAA climate education pages + BLS Environmental Engineers as district-filter fallbacks using the same 2-sentence template |
| 2 | Day 2 reading timing | Soften "about 6 minutes per set" → "plan 4-6 min per set — slower readers can skim Set 3 using the bullets above as a guide"; students may start the summary worksheet as they read |
| 3 | Day 3 rationale redundant | Tighten rationale from 4-5 sentences → 3 sentences explicitly distinct from labels — focus on trade-off reasoning (what I'd cut, what I'm unsure about). Raises DOK without adding time |
| 4 | Day 3 checkpoint unrealistic | Soften "stop at each desk once" → "aim for 10-12 students, prioritize stuck/rushed; Day 4 peer feedback catches the rest" |
| 5 | Societal Trends political charge | Rename column "Careers Declining" → "Careers Changing or Adapting"; reframe example rows from "coal mining workers" / "field-walking crop scouts" → "traditional energy roles adding renewable skill sets" / "crop inspection shifting from hand-walking to drone-assisted"; add family-jobs facilitation note |
| 6 | Day 4 peer feedback timing | Add explicit time split inside 20 min (6/6/5/3 — explain A / explain B / rubrics / revisions); move revision notes to exit ticket if pair runs short |
| 7 | eDynamic fallback unnamed | Expand the VERIFY block with a concrete fallback — early 3-Week Reflection + research one real ag-tech company (Hylio/Skydio/DJI Agriculture) using BLS or Climate Kids, 2-sentence write-up |
| 8 | d(5)(C) isolated from drone work | Add 1-sentence conceptual bridge at start of Day 4 Activity 2 — "The drone you designed IS a career that barely existed 20 years ago; Ag-Tech Drone Operator is one of the clearest recent examples of what changing farm needs plus new technology create together" |

**Commit:** `a9a045f` — 5 files, +22/-15 lines. Largest single-file edit: day3.md at 16 net lines (3 concerns addressed in one file; still under the 15-line per-concern surgical limit). All per-concern edits ≤5 lines.

**Escalated:** none.

---

## Week 10 — 2SW Wk4: Dental / Medical Billing (Session 2026-04-15 Track B)

**Why this week:** pre-review suggested this might be a writer-reached slot week, but the S&S Topic field was populated with "Dental / Medical Billing" + a named H&L Career Climb activity (Perfect Toothbrush, Ch 9 pp. 140-142). Not a slot week after all. However, Day 4 depends on two substantial teacher-authored artifacts (ICD-10 reference sheet + simulated patient charts) — second A5 trigger for this session.

**Protocol used:** Teacher Implementer spawned as Explore sub-agent; Writer triage done in-session.

**Top Teacher Implementer concerns (10 lobbed):**

1. Day 1 pathway name drift — "Medical Billing and Coding pathway" vs. `PATHWAYS.md` canonical "Medical Billing"
2. Day 2 Activity 1 embeds 4 sub-steps (research + sketch + pitch + class discussion) in 25 min with no transition markers — pair pitches run into class discussion run into Activity 2 timing
3. Day 4 ICD-10 simulation materials (reference sheet + 8 patient charts) load-bearing and teacher-prepared but no Teacher Prep Checklist
4. Day 4 Round 2 jump from "one correct code" to "pick the BEST code, not just ANY" unscaffolded for 7th-graders
5. Day 2 Perfect Toothbrush Step 3 (partner pitch) timing unclear inside the 25-min block — no clean pivot into Activity 2
6. Day 5 Activity 1 teacher circulation 10 min / 24 students = ~25 sec each
7. Day 3 Activity 3 10-min "College Credit" walkthrough = passive lecture after 30 min of Xello tool work
8. Day 5 summative 15-min compression — 4-sentence paragraph + data recall + pair read high cognitive load
9. Day 1 warm-up "medical billing" too abstract for 7th graders who don't pay household bills
10. Day 4 + overview teacher-authored materials lack explicit guidance on code selection / trap-code design

**Writer triage: 9 Fix (1 folded), 0 Defend, 0 Escalate.**

| # | Concern | Fix |
|---|---------|-----|
| 1 | Singley pathway name | Rename Day 1 "Medical Billing and Coding pathway" → "Medical Billing pathway" to match `PATHWAYS.md` line 22 canonical. Credential formal name ("Certified Medical Billing and Coding Specialist") preserved — that IS the credential name, distinct from the pathway name. Dim 1 drift closed. |
| 2 | Day 2 Activity 1 density | Add explicit time split inside Activity 1 (5/8/5/7 — research / sketch+label / partner pitch / class discussion) with a named pivot into Activity 2 |
| 3 | Day 4 ICD-10 materials | Add **Teacher Prep Checklist** admonition to overview (second A5 trigger this session) — names the 8 ICD-10 codes Day 4 already mentions inline as a starting set (J00, J20.9, J45.909, K02.9, K21.9, R07.9, R51, S52.501A), points to CDC ICD-10 browser for the 2 extras, and specifies trap-code design for Round 2. ~30-45 min weekend prep. |
| 4 | Day 4 Round 2 unscaffolded | Add 30-sec specificity scaffolding moment + worked example before releasing students into independent Round 2 coding |
| 5 | Day 2 Activity 1 pivot | Folded into #2 |
| 6 | Day 5 circulation unrealistic | Soften to "10-12 students, prioritize those who added different pathway mix" |
| 7 | Day 3 passive lecture | Restructure Activity 3 from 10-min lecture → 4/3/3 (intro / turn-and-talk / whole-class share). Same total time, active-learning format |
| 8 | Day 5 summative compression | Add a 2-min Career Comparison pre-scan before writing; make pair-read/highlight optional if students need the full 15 min |
| 9 | Day 1 warm-up abstract | Replace "$4 billion industry" bridge with concrete student-stakes anchor: "If a medical coder types the wrong 5-character code, a family might get a $500 bill they don't actually owe" |
| 10 | Prep guidance missing | Folded into #3 |

**Commit:** `f856726` — 6 files, +34/-11 lines. Largest single-file edit: overview.md at 9 net lines. All under the 15-line threshold.

**Clinical self-catch:** An initial edit to the Day 4 Round 3 header ("(8 min, optional)") broke the timing-regex pattern `^## .* \([0-9]+ min\)` used by the 6-check preservation loop, which dropped Day 4 to 42 min in the verification step. Caught by the timing check and reverted — header kept as "(8 min)" with optionality noted in the body only. Lesson: when adding conditional language to an activity, never put it inside the `(N min)` header — that breaks the automated regex sweep that verifies timing across all 36 weeks.

**Escalated:** none.

---

## Cross-week themes — Session 2026-04-15 Track B additions

- **A5 Teacher Prep Checklist trigger keeps hitting.** All 3 reviewed weeks needed the admonition. 5SW Wk5 (two unbuilt printables + NGPF module pre-select), 3SW Wk3 (fallbacks for NASA Climate Kids + eDynamic 7.1 but no unbuilt artifacts), 2SW Wk4 (ICD-10 reference sheet + 8 patient charts authored from scratch). Pattern: ~1 in 3 weeks needs a TPC. The remaining 29 unrevised weeks likely have a similar rate. Track A5 standalone sweep stays on the backlog — best to keep adding it inline during Track B review for weeks where it genuinely fits.
- **Emotional-safety reframes are a Dim 9-adjacent category.** 5SW Wk5 Day 2 had a facilitation tip framing negative budgets as a "core learning moment" + Day 5 TPS bullet asking "Whose budget balanced without cutting anything?" Both risked reading as "your family's career choice was a failure." The fix was a reframe + explicit family-career protection, similar structurally to the Dim 9 fluff sweep but targeting a different failure mode (emotional stakes instead of surprise discipline). Future reviews: watch for warmth-critical moments around income, family work, immigrant status, body image, mental health. Same "don't implicate the student's family" lens.
- **Political neutrality on "declining" careers.** 3SW Wk3 had example rows "coal mining workers" / "field-walking crop scouts" in a "Careers Declining" column. In Irving ISD's real family-job context this reads as a judgment on specific industries. The fix was a frame shift ("Changing or Adapting" instead of "Declining") plus reframed examples that describe skill transitions within the same field. Same lens as emotional safety: the curriculum should not implicate a student's family members as career-losers.
- **Regex-breaking header edits.** Adding "(8 min, optional)" to a Day 4 header broke the timing-sum preservation check on 2SW Wk4. Conditional/optional language belongs in the activity body, never in the parenthetical time tag. New rule for future sessions: **never edit the parenthetical inside an H2 activity header unless the edit is a minute-count change.** Documented above in the 2SW Wk4 clinical self-catch.
- **In-session Writer triage scales cleanly to 3 weeks.** This session ran 3 Teacher Implementer sub-agents but handled all 3 Writer triages in-session per lesson 10. Total sub-agent use: 3 invocations. Evening session ran 3 sub-agents + 0 in-session writers (writer done in-session for all 3). Both sessions landed 3 weeks in the same rough budget. Confirming lesson 10 — Teacher persona needs separation (independent reader), Writer triage does not.

---

## Session 2026-04-15 Track B totals

- **Weeks reviewed:** 3 (5SW Wk5, 3SW Wk3, 2SW Wk4)
- **Concerns identified:** 28 (10 + 8 + 10)
- **Fix rows applied:** 26 (9 + 8 + 9)
- **Defended:** 1 (5SW Wk5 Day 4 Paying-for-College 12-min walkthrough — matches d(3)(C) scope)
- **Folded (duplicates):** 3 (5SW Wk5 #4/#5/#10 folded into #3 TPC; 2SW Wk4 #5 folded into #2, #10 into #3)
- **Escalated:** 0 (no new items for the escalation queue)
- **Commits landed:** 3 (`6812dd9`, `a9a045f`, `f856726`)
- **Files touched:** 14 (3 + 5 + 6)
- **Lines changed:** +75 / -33 total. Largest single-file edit: 5SW Wk5 overview.md at 13 net lines (still under 15-line threshold).
- **Verification:** all three commits passed the 6-check preservation loop (`mkdocs --strict`; scripting=0; DOK 2-4 present on all 15 reviewed day files; timing sums 50/50/50/50/50 on all 3 weeks; Support+ELL preserved; Dim 9 fluff=0). One clinical self-catch during 2SW Wk4 verification (regex-breaking header — caught and reverted).

**Running cumulative totals across all sessions (through session 3):**

- **Weeks reviewed:** 10 of 36 (1SW Wk0, 5SW Wk1 prototype, 4SW Wk1, 6SW Wk6, 2SW Wk5, 6SW Wk5, 4SW Wk2, 5SW Wk5, 3SW Wk3, 2SW Wk4)
- **Concerns:** 86 lobbed → 60 Fix / 15 Defend / 11 Escalate / 4 Folded
- **Commits:** 10 instinct-review commits
- **Remaining weeks to instinct-review:** 26

---

## Week 11 — 6SW Wk4 Sales/Presentations (Session 2026-04-15 Track B session 4)

**Why this week:** Dimension 9 "skill week" where hard presentation enforcement is earned pedagogically. Deferred from session 3 because it needed a dedicated focused pass. S&S explicitly labels it "PRESENTATION WEEK" with d(4)(C) as the primary oral-presentation artifact for the year. The Dim 9 question for this week was unique: verify the hard 3-min cap on Day 5 is pedagogically earned (drilled Days 1-4 with student-facing warning) rather than surprise discipline.

**Pre-check (before spawning Teacher Implementer):** grep-verified the week's enforcement language. Found two hits — Day 3 `(verbal warning at 2:30, cut at 3:00)` and Day 5 `(hard cap)` — both appeared earned on first read. Timing was 50/50/50/50/50 going in.

**Protocol used:** Teacher Implementer spawned as Explore sub-agent; Writer triage done in-session.

**Top Teacher Implementer concerns (10 lobbed):**

1. Day 5 Activity 1 math — 24 × 3 min = 72 min in a 50-min period. Compression options present in a `!!! warning` admonition but no pre-decision enforced + no student-facing notification of which option.
2. Day 5 hard enforcement NOT genuinely earned — students drilled the cap in teacher-controlled contexts (Day 3 team pitches, Day 4 paired practice) but were never TOLD student-facing that individual Day 5 presentations use the same rule. Teacher cuts off an individual student in front of peers = surprise step from "team got cut off" → "I got cut off personally."
3. Day 4 Activity 2 timing contradiction — "25 minutes (12 minutes per student)" in the intro vs. "Round 1 (12 min total)" in the substeps. For 2 students per pair, "12 min per student" would be 24 min, but the three rounds sum to 25 min.
4. (Same as #2 — folded)
5. Day 2 Activity 2 Powerskills Giving/Receiving Feedback crammed into 15 min (walkthrough + 5 min practice + 1 min debrief).
6. Day 1 Activity 2 H&L Pitching Investors setup 30 min tight for first-time navigation (form teams + read 3 investor profiles + choose idea + fill 6-question chart).
7. (Same as #1 — folded)
8. Day 3 team pitch feedback timing tight with 5 teams (5 × ~6 min = 30 min in 25-min activity).
9. Fluff patterns: Day 1 "exactly what real investors use" + Day 5 "a hard cap is how every real pitch event works" — borderline Dim 9 fluff.
10. Vocabulary bloat: Value Proposition + Pitch defined in overview but not explicitly taught in body.

**Writer triage: 8 Fix (2 folded), 2 Defend.**

| # | Concern | Fix |
|---|---------|-----|
| 1+7 | Day 5 compression pre-decision not student-facing | Fold into #2 — single Day 4 "Announce Day 5 format" facilitation note covering BOTH the format choice AND the cap |
| 2+4 | Day 5 hard cap not pre-announced student-facing Days 3/4 | Day 3 Activity 2 close with direct student-facing announcement; Day 4 Activity 2 add "Announce Day 5 format before students leave" facilitation note with both the cap reminder and the format choice |
| 3 | Day 4 timing contradiction | Replace "25 minutes (12 minutes per student)" with "25 minutes across three rounds" |
| 5 | Day 2 Powerskills 15 min | **DEFEND** — walkthrough + 5 min practice + 1 min debrief fits in 15 min; the skill is reused Days 3-5, retention comes from repetition not front-load |
| 6 | Day 1 H&L navigation + printed artifacts | Add **Teacher Prep Checklist** admonition to overview (A5 trigger — 4 printed artifacts: Rubric, Outline, Appearance Guide, team planner + Day 5 compression pre-decision + H&L Ch 5 access check) |
| 8 | Day 3 team pitch feedback timing tight at 5 teams | Add inline note in Activity 1 Format section: "With 5 teams, compress to one star + one wish per team to stay inside 25-min budget" |
| 9 | Day 1 + Day 5 fluff phrases | Day 1: drop "exactly what real investors use"; replace with concrete Day 3 pitch tie. Day 5: drop "every real pitch event works"; replace with concrete Day 4 announcement tie ("they were told explicitly at the end of Day 4 that today's cap is the same rule") |
| 10 | Vocabulary bloat | **DEFEND** — both Value Proposition and Pitch are in H&L Ch 5 workbook text students read Day 1 (Super Sports Ventures profile says "needs to see: Value Proposition") |

**Commit:** `043f718` — 5 files, +19/-4 lines. Largest single-file edit: overview.md at +10 lines. All under the 15-line threshold.

**Dim 9 verdict after fixes:** Earned-enforcement is now genuinely earned. Days 1-4 drill pacing with verbal warnings → Day 4 student-facing announcement names the rule explicitly → Day 5 enforcement references the prior announcement. Same words ("cut at 3:00"), now with the advance-warning pedagogy Dim 9 requires.

**Escalated:** none.

---

## Week 12 — 5SW Wk2 Civil Engineering (Session 2026-04-15 Track B session 4)

**Why this week:** high writer-reach yellow flag. S&S col 5 listed only pathway-level H&L exploration (Civil Engineer / Structural Engineer / Surveyor Hat Finder) + pathway fit assessment — no named H&L chapter project. S&S cols 7/8/9/12 (Tech Integration / Xello / eDynamic / Notes) all blank. Top candidate for writer-invented or thinly-grounded content based on session 3's writer-drift-vs-sparseness hypothesis.

**Protocol used:** Teacher Implementer spawned as Explore sub-agent; Writer triage done in-session.

**Writer-reach hypothesis verdict: partially falsified.** Teacher Implementer verified the week IS grounded to H&L Ch 8 (Engineering), specifically the **Infrastructure Imagination / Los Lomas** case study at pp. 131-135 — confirmed in HatsandLadders.txt at line 6501. The writer-invented piece is the straw-bridge build on Days 3-4, which is an EDP scaffold paralleling Infrastructure Imagination. Day 4 Activity 3 already connects them explicitly. Writer-drift correlation with S&S sparseness holds as a heuristic but isn't deterministic — weeks can be grounded even when S&S col 5 is thin if the writer found a named chapter project.

**Top Teacher Implementer concerns (8 lobbed):**

1. Day 2 Activity 2 Gallery Walk — 15 min / 6 stations / 12 pairs / 4 comparison questions per card is extremely tight; half the class won't hit all stations.
2. Day 3 bridge design 17 min tight + Day 4 build/test checkpoints are diagnostic-only (no time to re-teach if teams are off-track).
3. Day 1 Activity 3 Los Lomas report read is background-only with no callback to bridge build (week treats them as parallel, not connected).
4. Day 2 Activity 3 emerging careers categories (green building / smart infra / sustainability) weak source grounding — no BLS or H&L citation; "Why DFW needs it" prompt invites socioeconomic framing risk.
5. Week-wide: no H&L Ch 3 (A&C) reference despite 5SW A&C cluster arc with Week 1 Architecture.
6. Day 4 Method 1 test ("visible bend" in pennies-in-cup) is subjective and will cause 7th-grade arguments; single test station creates waiting bottleneck.
7. Day 5 warm-up "If a bridge failed in the real world and people got hurt..." primes failure/injury right before Activity 1 publicly ranks bridge weights (emotional-safety risk for teams whose bridges held low weight). Activity 1 label says "Celebration" but the ranking is public.
8. Overview sentence stem "A Smart Infrastructure Specialist is a NEW career because..." conflates newness with growth — the week's own emerging-careers definition says "did not exist 10 years ago OR are rapidly growing."

**Writer triage: 6 Fix, 2 Defend (+1 TEKS-stitching note).**

| # | Concern | Fix |
|---|---------|-----|
| 1 | Day 2 Gallery Walk 6 stations too many | Soften expectation — hit 4 of 6 stations (PSAT 8/9, SAT, ACT, TSI most relevant to 7th graders); skim remaining only if time allows |
| 2 | Day 3/4 bridge timing pressure | **DEFEND** — Day 3 has approval facilitation tip for stuck teams; Day 4 bottleneck partially addressed via #6 parallel-activity note |
| 3 | Day 1 Los Lomas disconnect from bridge build | Day 1 Activity 3 closing — add forward-reference sentence linking Los Lomas report to Days 3-4 straw-bridge challenge |
| 4 | Day 2 emerging careers weak source | Add BLS OOH Environmental Engineers citation as the source for the three categories |
| 5 | No Ch 3 reference despite A&C cluster arc | **DEFEND** — Ch 8 is the correct H&L anchor for civil engineering; overview header already names A&C cluster identity; adding Ch 3 would be over-correction |
| 6 | Day 4 Method 1 subjective + bottleneck | Define "failure" before testing (first visible sag OR joint separation; teacher's call final); add parallel-activity note — waiting teams start Activity 3 at desks |
| 7 | Day 5 warm-up emotional-safety (lesson 13) | **Two-part fix:** (a) warm-up reframed from "people got hurt" framing to "what questions do engineers ask when investigating failure" — keeps forensic engineer reveal but drops injury priming; (b) Activity 1 header changed from "Celebration" to "Share-Out + Team Presentations"; drop public high-to-low ranking; keep the whiteboard data for pattern-finding; add "most creative structural approach" recognition alongside highest-weight + best strength-to-weight |
| 8 | Overview sentence stem conflates newness/growth | Change stem "A Smart Infrastructure Specialist is a NEW career because..." to "...is an EMERGING career because... The technology or need that made it grow is..." — aligns with the definition |
| — | d(3)(E) PSAT/SAT placement tenuous (15 min Day 2 Activity 1 + 15 min Activity 2 ≈ 30 min stitched) | **DEFEND** — engineering scholarship tie is made explicit on Day 2 line 37; PSAT 8/9 (9th grade) timing is real for 7th graders; removing the stitch would require redesigning TEKS coverage |

**Commit:** `2f2a1af` — 5 files, +10/-10 lines. Smallest Track B commit by net lines this session. All per-concern edits ≤8 lines.

**Escalated:** none.

---

## Week 13 — 2SW Wk1 Legal Studies (Session 2026-04-15 Track B session 4)

**Why this week:** calibration week after three higher-stress reviews in session 3 + two higher-stress reviews (6SW Wk4, 5SW Wk2) in session 4. Typical content week — low-to-medium drift risk expected. Use as a check on whether the review protocol is working correctly: a calibration week should return a LOW concern count if the process is well-calibrated.

**Protocol used:** Teacher Implementer spawned as Explore sub-agent; Writer triage done in-session.

**Calibration verdict: PASSED.** 6 concerns lobbed (the lowest of the 3 weeks this session, as expected for a typical content week). 3 Fix + 3 Defend. Source grounding strong: H&L Ch 13 (Law and Public Service) anchors Days 1-2 with named activities (Hat Research p. 220, Emergency Essentials pp. 210-212); iCivics anchors Day 3; BLS + H&L Hat Finder anchor Day 4. Protocol is not over-fitting to high-stress weeks.

**Top Teacher Implementer concerns (6 lobbed):**

1. Day 3 at 55 min (top of 45-55 range) — no transition buffer; tech hiccups or game hangs break the period.
2. Day 4 Activity 3 Legal Entrepreneur Card lacks named H&L Ch 13 activity citation — looks like a writer reach for d(3)(I) coverage.
3. Day 4 AI ethics debate (bail amounts + recidivism prediction) has no emotional-safety frame; Irving ISD students may have family members affected by the criminal-justice system.
4. Day 5 eDynamic Unit 5.1 VERIFY flag + thin 5-min preview.
5. Powerskill Persuasion claimed in overview as the bridge to Day 4 debate but not explicitly taught.
6. Vocabulary term "probable cause" defined in overview but not pre-taught before Day 3 iCivics gameplay (was only in the Day 3 Support cheat sheet).

**Writer triage: 3 Fix, 3 Defend.**

| # | Concern | Fix |
|---|---------|-----|
| 1 | Day 3 at 55 min | Activity 1 `(10 min)` → `(7 min)` + Exit Ticket `(5 min)` → `(3 min)` — both minute-count changes in H2 headers (lesson 12 compliant); brings Day 3 to 50 min matching the rest of the week |
| 2 | Day 4 Legal Entrepreneur Card source | **DEFEND** — grep-verified H&L Ch 13 has no named legal-entrepreneurship activity; Day 4 Activity 3 grounds to BLS + H&L Hat Finder "self-employment" data; d(3)(I) coverage is a legitimate writer reach |
| 3 | Day 4 AI ethics debate emotional-safety (lesson 13) | Add "Frame the debate at the system level, not the personal level" facilitation note next to the existing "arguing the opposite side" tip — explicit system-level framing keeps the debate on the technology and the system design, not on who deserves an outcome |
| 4 | Day 5 eDynamic Unit 5.1 VERIFY + thin preview | **DEFEND** — VERIFY blocks are per editing-heuristics rule 7 (never delete); 5-min preview is a bridge, not a summative dependency |
| 5 | Powerskill Persuasion claimed but not delivered | **DEFEND** — overview line 55 is a chapter-level reference, not a claim that a Powerskills module is delivered; Day 4 debate teaches persuasion implicitly through sentence stems + evidence requirements |
| 6 | Probable cause not pre-taught | Day 3 Activity 1 body — add 60-sec whole-class vocab pre-teach for probable cause + due process + evidence before gameplay starts (inside the new 7-min Activity 1 budget) |

**Commit:** `a9ec5a9` — 2 files, +6/-3 lines. The smallest Track B commit ever recorded, as befits a calibration week.

**Escalated:** none.

---

## Mid-session structural escalation — 6SW Wk6 fully-optional reframe (Session 2026-04-15 Track B session 4)

**Not an instinct review** — a user-driven structural escalation mid-session. After the 3 instinct reviews landed, the session planning message flagged that 6SW Wk6 was very unlikely for teachers to complete at all due to end-of-year disruption, and that the prior buffer-week admonition (marking Day 1 Career Plan + Days 3-4 presentations as "load-bearing") contradicted that reality. User asked: if 6SW Wk6 content is non-negotiable for TEKS coverage, make sure it's somewhere else; otherwise make 6SW Wk6 fully skippable and note suggestions concisely like the Wk0 flexibility plan.

**Audit performed:**

Grep of all overviews for TEKS codes 6SW Wk6 claims:

| TEKS | Upstream homes | Buffer status upstream |
|---|---|---|
| **d(4)(C)** (oral presentation) | **6SW Wk4 Sales/Presentations** + 6SW Wk6 | 6SW Wk4 is NOT a buffer — presentation skill week. ✅ d(4)(C) locked upstream. |
| **d(8)(A)** (select pathway) | **4SW Wk1 Career Planning** + 6SW Wk6 | 4SW Wk1 IS a STAAR buffer. ⚠ both homes are buffers. |
| **d(8)(B)** (document courses/postsecondary) | **4SW Wk1 + 4SW Wk2** + 6SW Wk6 | All three are buffers. ⚠ |
| **d(8)(C)** (write individual plan) | **4SW Wk2 Course Mapping** + 6SW Wk6 | Both homes are buffers. ⚠ |

**Finding:** 6SW Wk6 is NOT uniquely load-bearing for any TEKS. Every claim has upstream coverage. Making it fully skippable does not sacrifice TEKS coverage *as long as the upstream weeks (4SW Wk1, 4SW Wk2, 6SW Wk4) stay intact*.

**Structural risk surfaced but not fixed in this session:** every week claiming d(8)(A)/(B)/(C) is a buffer week (4SW Wk1, 4SW Wk2, 6SW Wk6). If a teacher loses BOTH the STAAR buffer and the end-of-year buffer, d(8) doesn't get covered anywhere. The content-cannot-move-between-weeks rule (user direction, S&S fidelity) blocks the obvious structural fix of moving d(8)(C) to a non-buffer week. Added to escalation queue for teacher meeting 2026-04-15.

**Edits applied to 6SW Wk6 overview (commit `01627b1`):**

1. **Replace `!!! note "Buffer week"` at lines 9-10 with `!!! abstract "Adapt to your end-of-year schedule — everything here is optional"`** — Wk0-style verb menu:
    - "Nothing in this week is critical to year-end TEKS coverage."
    - Per-TEKS upstream coverage explicitly named (d(4)(C) → 6SW Wk4; d(8)(A) → 4SW Wk1; d(8)(B) → 4SW Wk1 + 4SW Wk2; d(8)(C) → 4SW Wk2)
    - Verb menu: **cut** (RIASEC retake, celebration), **compress** (merge Days 3-4 presentations into one day with 90-sec slots), **substitute** (swap celebration for written reflection or thank-you circle), **skip entirely** (Day 5 year-end closer only)
    - Closing: "Any subset of the 5 days is fine. Zero days is fine."

2. **Soften TEKS-section body claim** ("This is the CAPSTONE WEEK. Six weeks of work..." → "This is the capstone pass — not the artifact week.") — preserves capstone framing for teachers who run the week but doesn't contradict the new admonition.

3. **Soften Summative Assessment body claim** ("The H&L downloadable Career Plan is the official course artifact" → "...is the capstone-week polish of an artifact already produced in 4SW Wk1-Wk2").

4. **Soften Pre-Capstone Teacher Checklist intro** ("This is the year's highest-stakes week" → "This week is optional per the admonition above — but if your schedule allows it, it is the most platform-dependent week in the year").

**No day files touched. No content removed. No TEKS claims removed from the overview.** The week's structure, activities, and pedagogical content are preserved for teachers who CAN run it — only the framing changed.

**Commit:** `01627b1` — 1 file, +16/-6 lines. Over the 15-line day-file surgical limit, but this is an overview-level structural reframe the user explicitly authorized in session.

**Lesson 14 added to PLANNING.md §10:** Fully-optional-week reframe is a new structural tool — valid only when every TEKS really is covered upstream; requires body softenings alongside the admonition rewrite to prevent contradiction; reference implementation is commit `01627b1` on 6SW Wk6.

---

## Session 2026-04-15 Track B session 4 totals

- **Weeks instinct-reviewed:** 3 (6SW Wk4, 5SW Wk2, 2SW Wk1)
- **Structural commits:** 1 (6SW Wk6 reframe — not an instinct review but a user-driven structural escalation)
- **Concerns identified (instinct reviews only):** 24 (10 + 8 + 6)
- **Fix rows applied (instinct reviews):** 17 (8 + 6 + 3)
- **Defended:** 7 (2 + 2 + 3)
- **Folded (duplicates):** 2 (both in 6SW Wk4)
- **Escalated:** 0 from instinct reviews; 2 new items from the 6SW Wk6 audit (d(8) structural risk + curriculum-density pattern)
- **Commits landed:** 4 (`043f718`, `2f2a1af`, `a9ec5a9`, `01627b1`)
- **Files touched:** 13 (5 + 5 + 2 + 1)
- **Lines changed (instinct reviews):** +35 / -17 across 12 files
- **Lines changed (structural reframe):** +16 / -6 across 1 file
- **Verification:** all four commits passed the 6-check preservation loop (`mkdocs --strict`; scripting=0; DOK 2-4 present on all 15 instinct-reviewed day files; timing sums 50/50/50/50/50 on 6SW Wk4, 5SW Wk2, 2SW Wk1 — Day 3 of 2SW Wk1 brought from 55→50; Support+ELL preserved; Dim 9 fluff=0).

**Running cumulative totals across all sessions:**

- **Weeks reviewed:** 13 of 36 (session 3 list + 6SW Wk4, 5SW Wk2, 2SW Wk1) + 1 structural reframe (6SW Wk6, but also counted as instinct-reviewed in the morning of session 1)
- **Concerns (instinct reviews only):** 110 lobbed → 77 Fix / 22 Defend / 11 Escalate / 6 Folded
- **Commits:** 13 instinct-review commits + 1 structural reframe = 14 total Track B commits
- **Remaining weeks to instinct-review:** 23 of 36
