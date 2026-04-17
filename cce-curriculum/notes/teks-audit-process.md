# TEKS Audit Process

A reusable process for auditing whether a day's (or week's) TEKS tags are honestly supported by the lesson content, and for resolving misalignment. Informed by the 2SW Wk2 exit-ticket pilot (2026-04-16), which surfaced that 4 of 5 days had over-claimed or weak TEKS tags.

This is an authoring process, not a teacher-facing doc. Lives in `cce-curriculum/notes/` alongside `editing-heuristics.md` and `exit-ticket-templates.md`.

---

## When to run a TEKS audit

1. **During a week pilot** (like 2SW Wk2). Audit all 5 days' tags before shipping.
2. **When rewriting exit tickets** for a week. You cannot write a strictly-aligned ticket without first verifying the TEKS tag is itself strictly supported.
3. **Scheduled round** (e.g., before the next teacher-review milestone). Batch audit several weeks.
4. **On teacher feedback** flagging a specific day as "not really teaching what the objective says."

## Scope per run

- **Single-day audit** is too narrow (misses the week's distribution of TEKS across days). Don't do this.
- **Single-week audit** is the minimum useful unit. All 5 days + overview + CFA alignment.
- **Multi-week audit** only when batching scheduled rounds; keep to ≤3 weeks per pass to stay in the preservation-loop budget.

## The 6-step process (per day within a week audit)

**Step 1 — Read the day's Lesson Objective and TEKS tag.** Verbatim from the day.md header.

**Step 2 — Read the TEK language.** Pull the full text of each claimed TEKS code from the curriculum docs or the H&L scope mapping (starts around line 13400 in `cce-curriculum/resources/reference-pdfs/HatsandLadders.txt`). Pay special attention to qualifier language — "such as" means the named items are EXAMPLES, not an exhaustive list. "Including" means the named items are required. The distinction matters for exit-ticket alignment.

**Step 3 — List what the day actually teaches.** Walk the 3-5 activities. What skill, knowledge, or artifact does each activity build? Be concrete: "students fill in a comparison table with training times" not "students learn about careers."

**Step 4 — Match lesson content to claimed TEKS.** For each TEKS code on the day:

- **STRICT match:** the activity directly builds the skill / produces the artifact the TEK asks for. Keep the tag.
- **OVER-CLAIM:** the activity is thematically related but doesn't build the specific skill. Example: Day 4 of the 2SW Wk2 pilot claimed d(2)(A) "training requirements" but zero Day 4 activities touched training specifics (those live on Days 1 and 5). Drop the tag from that day; the week-level overview can still carry the code if another day covers it.
- **WEAK match:** the overlay (CCE-authored Career Connection paragraph, activity framing) carries the code but H&L content alone does not. Keep the tag if the overlay is substantial. Rewrite the exit ticket to assess the overlay content specifically (not the H&L content).
- **GAP:** the activity doesn't cover the code at all. Either drop the tag or add supplementary content.

**Step 5 — Write the exit ticket after the tags are cleaned.** The ticket should strictly assess AT LEAST ONE tag on the day. Use `exit-ticket-templates.md` for format selection. Honor the TEKS language (especially "such as" — don't treat named examples as exhaustive).

**Step 6 — Update downstream artifacts.** If a tag dropped from a day:

- `day.md` TEKS row header: drop the code
- `overview.md` Formative or Summative Assessment section: remove claims that tied the code to THIS day
- `teks-coverage-matrix.md`: leave the week-level listing if another day in the week still covers the code; remove the week from Explicit Weeks if no day covers it

## Decision rules (quick reference)

| Situation | Rule |
|---|---|
| TEK uses "such as" | Named items are examples; any equivalent concept counts |
| TEK uses "including" | Named items are required |
| H&L content doesn't teach the TEK, CCE overlay does | Overlay must be substantial (a Career Connection paragraph + activity framing); otherwise drop |
| Activity is thematically related but doesn't build the skill | Over-claim; drop |
| Multiple days in the week cover the same code | Fine; tag only the days where assessment happens |
| Overview lists code but no day strictly covers it | Real gap; either drop from week or add content |

## Escalation to coordinators

Escalate when:

- A TEK is systematically unsupported across multiple weeks where the scope-and-sequence claims coverage. This is an H&L-vs-TEKS structural gap, not an authoring fix.
- An H&L chapter fundamentally doesn't teach a code we've been claiming in every cluster (e.g., d(4)(F) integrity is not in H&L Ch 13; the claim comes entirely from CCE overlay).
- Fixing the misalignment requires cutting H&L content that teachers expect or adding content that would break the 45-55 min day budget repeatedly.

Escalation output: a short memo naming the TEK, the affected weeks, and the three decision paths (retag / add content / accept overlay-dependent assessment).

## Integration with the preservation loop

Add two checks to `cce-curriculum/notes/editing-heuristics.md` grep recipes (not yet added, candidate for round-2):

```bash
# For any week being audited, list day-level TEKS tags:
for f in docs/<sw>/<week>/day*.md; do
  echo "--- $f"
  grep -E "^\| \*\*TEKS\*\*" "$f"
done

# Cross-check against week overview TEKS claims:
grep -E "d\([1-9]\)\([A-Z]\)" docs/<sw>/<week>/overview.md
```

The audit itself is NOT a preservation-loop check (too judgment-heavy for a grep). It's a pre-ship review step for any week touching exit tickets or lesson objectives.

## Artifact checklist for a week audit

Per week, produce (or update):

- [ ] Audit notes (in this file or a sibling, briefly: "2SW Wk2 audited 2026-04-16, Day 4 d(2)(A) dropped")
- [ ] Updated `day.md` TEKS headers
- [ ] Updated `overview.md` Formative / Summative claims
- [ ] Updated exit tickets per the audit
- [ ] Updated `teks-coverage-matrix.md` if week-level coverage changes
- [ ] Preservation loop clean
- [ ] Commit with an "AUDIT:" prefix in the subject so it's filterable in git log

## Audit log (append as audits happen)

- **2026-04-16 — 2SW Wk2.** All 5 days audited. Day 4 d(2)(A) dropped (activities don't engage training specifics; d(2)(A) coverage for the week lives on Days 1 and 5). Exit tickets for Days 1-5 rewritten at 6th-7th ESL reading level with strict alignment to cleaned TEKS set. Key insight: d(4)(F) "such as" language means the 4 named traits are examples, not exhaustive — quality-pick probes using a broader vocabulary set (calm / fair / brave / honest / caring / clear-thinking) satisfy the TEK honestly.

- **2026-04-17 — 3SW Wk5 Cosmetology.** All 5 days audited. Significant retagging: Day 1 d(2)(A) dropped (Stress Toolkit + cluster tour doesn't teach training requirements) and replaced with d(1)(B) + d(1)(C). Day 2 d(3)(G) dropped (interview skills are not "steps to enroll"; the TEK fit is employability) and replaced with d(6)(C) mock interview + d(7)(B) thank-you email — both promoted from Implicit to Explicit in teks-coverage-matrix.md. Day 3 d(2)(A) + d(3)(G) kept (TDLR 3-route comparison is a strict fit; 3SW Wk5 Day 3 added to d(2)(A) Explicit Weeks column in the matrix where it had been absent). Day 4 d(3)(I) kept (salon concept). Day 5 d(2)(A) + d(3)(G) + d(3)(I) all dropped (Xello Career Factors + H&L favorites don't strictly support any of them) and replaced with d(1)(A) Xello assessment (Implicit) + d(1)(C) H&L favorites. Exit tickets rewritten in 5 distinct formats at 6th-7th ESL reading level (Comparison Matrix / Mini-Case / Ranked Justification / Decision Tree / Concept Map). Key insight: wrap-up days that bundle multiple platforms (Xello + eDynamic + H&L favorites) tend to over-claim TEKS; each platform's artifact only honestly lands ONE code and the day's tag should reflect the strongest-evidence pair, not the sum of all themes touched.

- **2026-04-17 — 4SW Wk5 Automotive.** All 5 days audited. Retagging lighter than 3SW Wk5 because Days 1-4 already matched honest claims. Day 5 d(2)(A) + d(2)(B) + d(8)(A) all dropped. d(8)(A) "select a career pathway" was an over-claim — H&L Favoriting is cluster-level exploration, not pathway selection (per the matrix, d(8)(A) lives explicitly only at 4SW Wk1 Day 2 and 6SW Wk6). d(2)(A) + d(2)(B) were ambient themes in the presentation, not strictly probed. Day 5 replaced with d(5)(E) cross-cluster salary + d(1)(C) H&L Favorites. Matrix updated: d(3)(G) picks up 4SW Wk5 Day 4 (Ratteree vs. trade school); d(5)(E) picks up 4SW Wk5 Day 5 (cross-cluster presentation). Exit tickets rewritten in 5 distinct formats (Venn Diagram / Trade-off Dilemma / Comparison Matrix / Diagnostic MCQ with Misconception Distractors / Concept Map). Key insight: d(8)(A) "select a career pathway" is easy to over-claim on H&L Favorites days because favoriting LOOKS like pathway selection. Matrix-anchored discipline: if a week is not already in the d(8)(A) Explicit Weeks list, do not tag individual days with d(8)(A); Favorites are d(1)(C) not d(8).

- **2026-04-17 — 1SW Wk1 Robotics / Manufacturing.** First week of the systematic pilot pass (top-down, skipping Wk0 and already-piloted weeks). All 5 days audited. Retag: Day 3 d(2)(A) dropped and replaced with d(7)(D) — the Job References H&L activity is the perfect d(7)(D) fit, already listed in the matrix under d(7)(D) Explicit Weeks but missing from the day file's TEKS header. Days 4-5 d(2)(A) dropped (Sphero programming + Task Bot presentations don't research training specifics; d(2)(A) coverage for the week lives on Day 2). Days 1 and 2 tags kept. Exit tickets rewritten in 5 distinct formats (Comparison Matrix / Mini-Case / Ranked Justification / Decision Tree / Concept Map). Week-level overview added d(7)(D). Key insight: matrix-listed claims must match day-file tags. When the matrix says a TEK is Explicit in a specific day but the day's file doesn't tag it, that's a disconnect to reconcile during audit, not a reason to leave the tag off.

- **2026-04-17 — 1SW Wk2 Programming / IT.** All 5 days audited. Only Day 5 needed retag: d(5)(A) dropped (no labor market trends work today) and replaced with d(1)(A) for the H&L Pathway Fit assessment (which IS an assessment-result analysis by definition). Matrix picked up 1SW Wk2 Day 5 in the d(1)(A) Implicit column. Days 1-4 tags kept. Exit tickets rewritten in 5 distinct formats (Venn Diagram / Mini-Case / Comparison Matrix / Short Constructed Response / Concept Map) at 6th-7th ESL level. Overview TEKS expanded to reflect the full week-level claim set (d(1)(A), d(1)(B), d(1)(C), d(2)(A), d(5)(A), d(5)(E)); previously missed d(1)(A) and d(2)(A) at week level despite day-level coverage. Key insight: Pathway Fit / Career Factor / Cluster Matcher platform assessments are d(1)(A) natives. When a day has H&L Pathway Fit or Xello career-fit work, d(1)(A) is almost always the right implicit tag.

- **2026-04-17 — 1SW Wk3 Computer Science / IT.** All 5 days audited. Only Day 3 needed retag: d(2)(A) dropped (Job Applications form doesn't research training; it practices filling in a sample form) and replaced with d(7)(C) "Complete sample job applications" — already listed in the matrix as Implicit at 1SW Wk3 Day 3. Days 1, 2, 4, 5 tags kept. Overview dropped d(2)(A) from week-level (no day uses it), added d(7)(C). Exit tickets rewritten in 4 distinct formats (Venn Diagram / Mini-Case / Comparison Matrix / Concept Map); Day 3 kept its deliverable-only format (rich wireframe+application submission stands as the mastery evidence, no 3-min exit ticket budget). Key insight: some H&L activities live at a different TEK than the surrounding week-level claim (Job Applications is d(7)(C), not d(2)(A)); audit-gated retag closes the gap. Also: deliverable-only days are a legitimate format when the day's artifact IS the mastery evidence and adding a 3-min exit ticket would force timing cuts elsewhere.

- **2026-04-17 — 1SW Wk4 Tech Support / IT.** All 5 days audited. Retags: Day 3 d(2)(A) dropped (MakeCode + micro:bit programming doesn't research training; it builds a tool) — day now tagged d(4)(B) only; Day 5 d(2)(A) + d(2)(B) dropped (demos + favorites don't research training; they identify careers) and replaced with d(1)(C) for the H&L IT Support Favorites. Days 1, 2, 4 tags kept. Overview added d(1)(C) at week level. Exit tickets rewritten in 5 distinct formats (Comparison Matrix / Ranked Justification / Decision Tree / Diagnostic MCQ / Concept Map). Key insight: student-facing exit-ticket text should carry at most the cleaned TEKS tag parenthetical — Day 2's original ticket cited three codes including d(5)(B), which was neither the day's claim nor the week's claim, just an authoring drift.

- **2026-04-17 — 1SW Wk5 Cybersecurity.** All 5 days audited (final 1SW week). Retags: Day 2 d(1)(D) + d(4)(F) both dropped (Cyber Safety Creator is design role-play, not emerging-career research or integrity work — integrity lands Day 3). Day 2 replaced with d(1)(C). Day 3 d(1)(D) dropped (peer feedback + integrity discussion don't research emerging careers); kept d(4)(F) — integrity IS the day. Day 5 d(1)(D) + d(4)(F) dropped (the capstone reflection is cluster / career / postsecondary synthesis, not emerging-career research or integrity work); kept d(3)(A), added d(1)(C). Days 1 and 4 kept. Overview TEKS now d(1)(C), d(1)(D), d(4)(F), d(3)(A). Exit tickets rewritten in 4 distinct formats (Ranked Justification / Mini-Case / Trade-off Dilemma / Decision Tree); Day 5 kept its deliverable-only format (the My Career Journey reflection is the summative). Key insight: capstone-week days spread TEKS thinly across many themes; audit discipline is to pick the ONE or TWO codes a day's activities honestly probe, not the union of themes touched. 3-2-1 Reflective format reserved for later weeks; the existing My Career Journey structured reflection already serves the Day 5 wrap role.

- **2026-04-17 — 2SW Wk1 Legal Studies.** All 5 days audited. Retags: Day 2 d(1)(B) dropped (Emergency Kit design is a skill-building activity, not a cluster-exploration activity); kept d(1)(C) via the Firefighter role-play. Day 4 d(1)(C) dropped (entrepreneurship + association are the anchors; cluster ID is peripheral); kept d(3)(I) + d(3)(H). Day 5 d(3)(I) dropped (position-paper polish doesn't probe entrepreneurship on Day 5; that mastery already landed Day 4); kept d(1)(C) + d(3)(H). Days 1 and 3 kept. Exit tickets rewritten in 5 distinct formats (Comparison Matrix / Ranked Justification / Decision Tree / Short Constructed Response / Concept Map); Day 4's SCR preserves the AI Ethics Position Paper structure as the reserved category for a short structured written response. Key insight: skill-building days like Emergency Kit Design often claim cluster-exploration tags (d(1)(B)) they don't earn; the honest anchor is the career role the day embeds students in (Firefighter = d(1)(C)), not the ambient cluster label.

- **2026-04-17 — 2SW Wk3 Nursing / Health Science.** All 5 days audited. Retags: Day 4 d(2)(A) dropped (micro:bit monitor refinement doesn't research training; the mention of Singley cert in presentation is ambient framing, not a probe); kept d(1)(C). Day 5 added d(1)(A) for the Xello Learning Styles self-assessment (promoted to Implicit in the matrix). Days 1, 2, 3 kept. Exit tickets rewritten in 5 distinct formats (Comparison Matrix / Ranked Justification / Decision Tree / Mini-Case / Concept Map). Overview TEKS expanded to add d(1)(A) at week level. Key insight: Xello self-assessment lessons (Learning Styles, Career Factors, Pathway Fit) are reliable d(1)(A) anchors and the matrix should capture them as Implicit Weeks; three weeks now carry that pattern (1SW Wk2 Day 5, 2SW Wk3 Day 5, 3SW Wk5 Day 5).

- **2026-04-17 — 2SW Wk4 Dental / Medical Billing.** All 5 days audited. Retags: Day 2 d(2)(A) dropped (toothbrush design + Hat Research refresh; training research already landed Day 1); kept d(1)(C), d(5)(B). Day 3 added d(1)(A) for the Xello Education Experience self-assessment — four Xello-self-assessment Implicit entries now (pattern: every Xello lesson that asks students to reflect on their own skills/factors/experience rolls up to d(1)(A)). Days 1, 4, 5 kept. Overview TEKS expanded to add d(1)(A) + d(1)(C) at the week level. Exit tickets rewritten in 5 distinct formats (Mini-Case / Comparison Matrix / Short Constructed Response / Diagnostic MCQ / 3-2-1 Reflective). 3-2-1 Reflective used here for Day 5 -- legitimate mid-cluster reflection; reserved from other 2SW weeks this six-weeks per the "once per six-weeks" rule. Key insight: classification-style days (d(5)(B)) benefit from Comparison Matrix exit tickets with check-mark cells, which make the "triple-threat high-skill/wage/demand" concept visible at a glance.

- **2026-04-17 — 2SW Wk5 Powerskills / Communication.** All 5 days audited. Retags: d(4)(F) dropped from Days 1, 2, 4, and 5 (none of the communication-skills days strictly probe work ethic / integrity / dedication / perseverance; these are transferable-skill days = d(4)(B)). Day 5 added d(1)(A) for the CareerOneStop Skills Matcher self-assessment. Day 3 tags kept unchanged. Overview TEKS trimmed to remove d(4)(F) (no day earns it, so the week-level claim drops); added d(1)(A). Exit tickets rewritten in 5 distinct formats (Decision Tree / Mini-Case / Short Constructed Response / Trade-off Dilemma / Concept Map). Key insight: d(4)(F) "work ethic / integrity / dedication / perseverance" is easy to over-claim on any soft-skills week; the honest fit for communication-skills practice is d(4)(B) transferable skills, not d(4)(F). CareerOneStop Skills Matcher joins the Xello-self-assessment pattern for d(1)(A) Implicit coverage — CareerOneStop tools count alongside Xello lessons wherever students rate themselves and receive career recommendations.

- **2026-04-17 — 2SW Wk6 Biomedical / Health Science.** All 5 days audited (final 2SW week). Retags: Day 1 d(2)(A) dropped (Cover Letter activity does not research training; it writes correspondence); added d(7)(B) — the H&L "Cover Letter: The Golden Ticket" is a clean d(7)(B) probe now promoted to matrix Explicit. Day 2 d(2)(A) dropped (PT workout plan design does not research training; the DPT education note is ambient). Days 3 + 4 d(5)(A) dropped (Farm Fresh Express is community-data + food-desert design, not strictly labor-market-trend analysis). Day 5 kept all three (d(1)(D) + d(2)(A) + d(5)(A)) — the Emerging Career Research template IS the labor-market-trend probe. Overview TEKS expanded to add d(1)(C) + d(7)(B) at the week level. Matrix: 2SW Wk6 Day 1 added to d(7)(B) Explicit Weeks. Exit tickets rewritten in 5 distinct formats (Mini-Case / Comparison Matrix / Ranked Justification / Venn Diagram / Concept Map). Key insight: community-design days (food desert, public-health-flavored activities) often get auto-tagged d(5)(A) labor-market-trends because "community data" sounds like market analysis — the audit-discipline distinction is that d(5)(A) is about career / industry labor trends, not neighborhood / demographic data.

- **2026-04-17 — 3SW Wk1 Vet Science.** All 5 days audited. Retags: Day 4 d(2)(B) dropped (Life Experiences and Volunteer Hours are not about evaluating training options); added d(1)(A) (Life Experiences IS a Xello self-reflection) + d(4)(E) (Volunteer Hours logging directly covers "community service and volunteerism"). Kept d(1)(C). Days 1, 2, 3, 5 kept. Overview TEKS expanded to add d(1)(A) + d(4)(E) at the week level. Matrix updates: 3SW Wk1 Day 4 added to d(1)(A) Implicit (the "Xello-self-assessment" pattern is now six weeks deep) and to d(4)(E) Implicit (a second systematic d(4)(E) touchpoint). Exit tickets rewritten in 5 distinct formats (Mini-Case / Comparison Matrix / Decision Tree / Short Constructed Response / Concept Map). Key insight: Xello Volunteer Hours is a direct d(4)(E) probe that the matrix had missed; any week with a logged-hours component where students name a community service they perform can carry d(4)(E) Implicit.

- **2026-04-17 — 3SW Wk2 Plant Science.** All 5 days audited. Retags: Day 1 added d(1)(B) (two-pathway tour fits cluster-exploration). Day 5 dropped d(1)(D) (no emerging-career research today) and added d(1)(A) (Xello Work Experiences self-reflection). Days 2, 3, 4 kept. Overview TEKS expanded to add d(1)(A) + d(1)(B) + d(2)(B) at the week level (previously only d(1)(C) + d(1)(D) listed). Matrix updated: 3SW Wk2 Day 5 added to d(1)(A) Implicit (seven Xello-self-assessment entries now). Exit tickets rewritten in 5 distinct formats (Comparison Matrix / Mini-Case / Venn Diagram / Ranked Justification / Concept Map). Key insight: 2-pathway introduction days reliably earn d(1)(B) alongside d(1)(C); the week-level should capture both even when only one day strictly leads with cluster exploration.

- **2026-04-17 — 3SW Wk3 Sustainable Engineering.** All 5 days audited. Retags: Days 1, 2, 3 d(1)(D) dropped (environmental career exploration and Pest Patrol drone design are role-play, not emerging-career research — that mastery lives on Day 4 societal trends chart); replaced with d(1)(C) on each day. Day 4 kept d(1)(D) + d(5)(C) (the chart explicitly probes new/changing careers tied to societal trends). Day 5 dropped d(1)(D) + d(5)(C) (reflection + Xello are not primary trend-analysis probes) and replaced with d(1)(A) (Xello Interests) + d(1)(C) (favorite-career reflection). Overview TEKS expanded to add d(1)(A) + d(1)(C) at the week level. Exit tickets rewritten in 5 distinct formats (Mini-Case / Ranked Justification / Short Constructed Response / Comparison Matrix / Concept Map). Matrix: 3SW Wk3 Day 5 added to d(1)(A) Implicit (eight entries). Key insight: when d(1)(D) "emerging occupations" is the week-level tag, the audit must find the DAY where emerging careers are EXPLICITLY researched / charted — not the whole week. Multi-day design projects like Pest Patrol are career-role practice (d(1)(C)), not d(1)(D) research.

- **2026-04-17 — 3SW Wk4 Culinary / Hospitality.** All 5 days audited. Retags: Day 1 added d(1)(B) (3-pathway cluster tour earns it). Day 2 dropped d(1)(C) (motivation + salary are primarily transferable-skill + comparison probes) and added d(4)(B) for the Powerskill Motivation chart. Day 4 dropped d(3)(I) (Tourism Director is a government / marketing role, not entrepreneurship; the Silverbrook campaign doesn't probe small-business entrepreneurship). Days 3, 5 kept. Overview TEKS expanded to add d(1)(B) + d(4)(B) at the week level. Exit tickets rewritten in 5 distinct formats (Mini-Case / Comparison Matrix / Decision Tree / Short Constructed Response / Concept Map). Key insight: H&L Powerskill modules (Motivation, Conflict Resolution, etc.) fit d(4)(B) transferable-skills cleanly; when a Powerskill module appears on a day alongside a salary comparison, the cleanest pair is d(4)(B) + d(5)(E) rather than d(1)(C) + d(5)(E).

- **2026-04-17 — 3SW Wk6 Entrepreneurship.** All 5 days audited (last 3SW week; strongest d(3)(I) week of the year). Only Day 5 retag: d(4)(F) dropped (budget + Xello reflection don't probe work ethic specifically; work ethic lands Day 4). Days 1-4 kept. Exit tickets rewritten in 5 distinct formats (Mini-Case / Short Constructed Response / Comparison Matrix / Trade-off Dilemma / Concept Map). MILESTONE: with this week, 1SW (all 5) + 2SW (all 6) + 3SW (all 6) + 4SW Wk5 = 18 weeks through the pilot pattern. Key insight: high-value single-TEK weeks like 3SW Wk6 (d(3)(I)-heavy) don't need much retagging — the discipline is confirming the week-level TEK lands on every day (it does here), then focusing the exit-ticket rewrite on format variety + ESL level.
