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

- **Fix applied:** 7 (including the cross-week continuity note)
- **Defended:** 3
- **Escalated to teacher meeting:** 3
- **Timing after edits:** Day 1 = 48 min, Days 2–5 = 50 min each. All in 45–55 range.
- **Scripting regressions:** 0
- **DOK 2–4 markers preserved:** 5/5
- **Support/Extension/ELL bullets preserved:** 5/5

---

## Week 2 — 5SW Wk1: Blueprint Builders / Architecture Careers (PROTOTYPE)

*Pending — Curriculum Writer triage in progress.*

---

## Week 3 — 4SW Wk1: Career Planning (Mid-Year Reflection)

*Pending — Curriculum Writer triage in progress.*

---

## Week 4 — 6SW Wk6: Capstone / Final Career Plan & Presentations

*Pending — Curriculum Writer triage in progress.*

---

## Cross-week themes

The Teacher Implementer concern lists converged on five cross-cutting patterns:

1. **Tech fragility** — SSO failures, account setup, Chromebook cart logistics, and H&L/Xello/TinkerCAD login issues are consistently under-budgeted. Week 0, 5SW Wk1 (TinkerCAD), and 6SW Wk6 (end-of-year app drift) all flagged this.
2. **Data continuity across time** — 4SW Wk1 Day 1 and Day 5 warm-ups both ask students to reference Week 0 artifacts 18 weeks later, but Wk0 provides no explicit "save this" framing for the teacher. **Addressed by the cross-week Fix on Wk0 Day 5 shipped in this pass.** 6SW Wk6 has a similar dependency (36 weeks later) that may need a parallel fix when that week is triaged.
3. **Directive vs. suggestion language** — Especially in Wk0, but also in routine-setting moments across other weeks. `!!! tip "Suggested Routine"` and `!!! note "Campus Variation"` are the working pattern for converting directives to advice.
4. **Presentation math** — 24 students × 2–5 min > 50 min period. Flagged in 5SW Wk1 Day 5 and 6SW Wk6 Days 3–4. These will be primary fixes in Phase C.
5. **Resource backlog leakage** — Daily plans reference artifacts that `docs/resources/resources-status.md` lists as "not yet built" (worksheets, posters, rubrics). Not a curriculum defect; a tracking/communication issue. Will be called out in the final user summary.
