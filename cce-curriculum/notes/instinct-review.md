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

## Session totals

- **Weeks reviewed in depth:** 4 (1SW Wk0, 5SW Wk1 prototype, 4SW Wk1, 6SW Wk6)
- **Teacher Implementer concerns lobbed:** 42 (12 + 10 + 10 + 10)
- **Fix rows applied:** 20 (7 + 7 + 2 + 4)
- **Concerns defended:** 11 (3 + 2 + 3 + 3)
- **Concerns escalated to teacher meeting:** 11 (3 + 1 + 3 + 2, plus the 2 cross-week structural items)
- **Commits landed:** 4 (`6745afa`, `89614f4`, `f612edf`, `25a60db`)
- **Files touched:** 16 (4 Wk0 day files + 1 report = 5 in `6745afa`; 5 Wk1 files in `89614f4`; 2 4SW Wk1 day files in `f612edf`; 4 Wk6 files in `25a60db`)
- **Lines changed:** small — no single day file exceeded ~12 lines of edit (below the 15-line redesign threshold)
- **Verification at session end:** `mkdocs build --strict` clean, scripting=0 globally, DOK 2–4 present on all 180 daily plans, global timing loop clean (all day files 45–55 min), Support/Extension/ELL bullets preserved globally.
