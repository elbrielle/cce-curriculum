# Coursewide Source-Grounding and Next-Day-Readiness Audit

**Audit date:** 2026-08-09  
**Scope:** 36 unpublished instructional modules, 180 Teacher/Student day pairs  
**Status:** Structural inventory complete; source-by-source semantic verification in progress

## What this audit proves, and what it does not

This static pass proves whether the authored Canvas source visibly contains the implementation contract a teacher needs. It does **not** treat the presence of a citation as proof that the page number, activity, Xello minimum, labor-market figure, pathway claim, or TEKS alignment is correct. Those items remain in the manual grounding queue until checked against the authoritative source.

## Coursewide structural baseline

- Coordinated teacher/student pair detected: **180/180**
- TEKS visible in the teacher guide: **139/180**
- 50-minute flow visible: **180/180**
- Before-class preparation visible: **180/180**
- Monitoring/key guidance visible: **150/180**
- Concrete language/reading/participation support detected: **169/180**
- Absence/platform recovery route detected: **180/180**
- Student start/done contract detected: **147/180**
- Teacher guide explicitly labels **Topic**: **11/180**
- Teacher guide explicitly labels **Objective**: **0/180**
- Teacher guide explicitly labels **Demonstration of Learning / DOL**: **0/180**

The last three counts are intentionally strict. A title, `Today you will`, or `Target and evidence` may contain the right substance, but the district-facing labels are not consistently scannable yet.

## Confirmed first-pass findings

### P0 - Xello prerequisite chain is broken in the current 1SW Canvas sequence

The authenticated Grade 8 configuration requires **After high school goal -> Matchmaker quiz -> Personality Style quiz**. The current Canvas source protects After high school goal in 1SW Wk0 and Personality Style in 1SW Wk2, but neither `build_wk0.py` nor `build_wk1.py` protects Matchmaker. A teacher can therefore reach the polished Week 2 guide with students who are blocked by a missing prerequisite. The authoritative S&S is also stale: it still lists the old Wk0 quiz pileup and assigns Favorite Clusters to Wk2 even though the repaired Canvas pages place Personality Style there.

### P0 - The authoritative S&S and production Canvas disagree across all six 1SW Xello windows

The intended repaired sequence is Log in/After high school goal, What is CTE/Matchmaker, Personality Style, Learning Style, Add interests/Add skills, Favorite clusters. Current Canvas largely follows that order except for the missing What is CTE/Matchmaker block. Current S&S columns still show the legacy pileup, Favorite Clusters in Wk2, Add Skills in Wk3, a blank Wk4 cell, and Save Careers in Wk5. This must be reconciled before lesson-by-lesson grounding can be called complete.

### P1 - District scan labels are not explicit

Every guide needs a fast teacher-facing block for Topic, Objective, TEKS, and Demonstration of Learning. The current title, subtitle, `Today you will`, and `Target and evidence` usually contain the ingredients, but the required labels are not consistent enough for an evaluator or a teacher scanning during class.

### P1 - Projection readiness is not the same as one slide deck per lesson

Separate decks are intentionally optional. A lesson passes when the teacher guide itself is projection-ready or embeds the exact load-bearing workbook page, Climber slide, Xello launch asset, model, timer/prompt, and key needed for whole-class delivery. The manual review must record that outcome day by day.

### P1 - Two backup lesson sources still carry unresolved eDynamic markers

The remaining markers are 1SW Wk1 Day 5 (`Unit 2.1`) and 2SW Wk1 Day 5 (`Unit 5.1`). Canvas already treats eDynamic as supplemental in those lessons, so these markers should either be resolved to a verified optional classroom job or removed from the core route. They cannot remain ambiguous in the copy-ready source package.

### P1 - Artifact layout needs visual, not textual, acceptance

The strict worksheet build is a useful overflow gate, but it does not prove that a sixth- or seventh-grade student has enough room for the requested thinking. Every packet still needs rendered-page inspection against the response job: phrases, sentences, multi-part reasoning, and labeled sketches require different amounts of space.

## Manual grounding progress

### 1SW Wk0 licensed workbook check - verified

- Day 1 correctly uses FYF printed pp. 2-3 for `Classroom Career Hunt`.
- Day 3 correctly uses FYF printed pp. 9-11 for `My Building Blocks`; printed p. 11 provides a full-page reflection area.
- Day 4 correctly uses FYF printed p. 22 for `Building a Career Community`, with the custom My Career Journey artifact carrying the larger evidence job.
- Day 5 correctly uses FYF printed pp. 4-5 for `Perks and Quirks`. The workbook's research-note cells are too shallow for full explanations, but the Canvas route adds a one-career-per-page worksheet with dedicated full-width response lines. That is an appropriate scaffold rather than a duplicate decoration.
- Days 2-3 correctly treat the personality/work-values instruction as H&L plus Climber Notes because FYF does not print those assessments.

**Wk0 verdict:** workbook page grounding passes. The week is not fully copy-ready until the Xello Matchmaker prerequisite gap and the district Topic/Objective/DOL scan block are repaired.

## Immediate gates before teacher-copy readiness

1. Verify all 180 days against the authoritative S&S and the exact licensed source. Presence is not accuracy.
2. Standardize the teacher scan block so Topic, Objective, TEKS, and Demonstration of Learning are explicit without duplicating prose.
3. Confirm each day uses at least one purposeful district move where it improves learning. Variety matters; a mechanical checklist does not.
4. Cold-read every page pair and artifact as a teacher who has not seen the source files. Record hidden prep, missing models/keys, and timing collisions.
5. Render every worksheet and inspect response space against the amount and type of writing requested.
6. Keep separate slide decks optional. Require a projection-ready Canvas route or embedded licensed visual whenever the live lesson depends on whole-class display.

Unresolved `[VERIFY]`/`[TODO]`/`[TBD]` markers detected on **2 day(s)**. Days with no named instructional move detected: **0**. Both lists appear below.

## Day-by-day ledger

| Week | Day | Pair | TEKS | 50 min | Prep | Key/monitor | EB support | Recovery | Student contract | District moves | Sources | Markers |
| --- | ---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- | --- | --- |
| 1SW Wk0 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring, TVB | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 1SW Wk0 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Stop and Jot, Active Monitoring, TVB | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 1SW Wk0 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Think-Pair-Share / Turn and Talk, Active Monitoring, TVB | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 1SW Wk0 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring, TVB | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 1SW Wk0 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring, TVB | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 1SW Wk1 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Stop and Jot, Think-Pair-Share / Turn and Talk, Active Monitoring, Chunking | FYF, Xello, H&L, BLS / current primary source |  |
| 1SW Wk1 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Stop and Jot, Active Monitoring, Chunking | FYF, Xello, H&L, BLS / current primary source |  |
| 1SW Wk1 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Stop and Jot, Active Monitoring, Chunking, TVB | FYF, Xello, H&L, BLS / current primary source |  |
| 1SW Wk1 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Stop and Jot, Active Monitoring, Chunking | FYF, Xello, H&L, BLS / current primary source |  |
| 1SW Wk1 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Stop and Jot, Active Monitoring, Chunking | FYF, Climber Notes, Xello, H&L, BLS / current primary source | [VERIFY IN eDynamic] |
| 1SW Wk2 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Stop and Jot, Think-Pair-Share / Turn and Talk, Active Monitoring, Chunking | FYF, Xello, H&L, BLS / current primary source |  |
| 1SW Wk2 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Stop and Jot, Think-Pair-Share / Turn and Talk, Active Monitoring, Chunking | FYF, Xello, H&L, BLS / current primary source |  |
| 1SW Wk2 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Stop and Jot, Think-Pair-Share / Turn and Talk, Active Monitoring, Chunking | FYF, Xello, H&L, BLS / current primary source |  |
| 1SW Wk2 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Stop and Jot, Think-Pair-Share / Turn and Talk, Active Monitoring, Chunking, TVB | FYF, Xello, H&L, BLS / current primary source |  |
| 1SW Wk2 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Stop and Jot, Think-Pair-Share / Turn and Talk, Active Monitoring, Chunking | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 1SW Wk3 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Stop and Jot, Active Monitoring | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 1SW Wk3 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Stop and Jot, Active Monitoring | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 1SW Wk3 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Think-Pair-Share / Turn and Talk, Active Monitoring | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 1SW Wk3 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Active Monitoring | Climber Notes, Xello, H&L, BLS / current primary source |  |
| 1SW Wk3 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Active Monitoring, TVB | Climber Notes, Xello, H&L, BLS / current primary source |  |
| 1SW Wk4 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Stop and Jot, Active Monitoring, Chunking | FYF, Xello, H&L, BLS / current primary source |  |
| 1SW Wk4 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Active Monitoring, Chunking | FYF, Xello, H&L, BLS / current primary source |  |
| 1SW Wk4 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Active Monitoring, Chunking | FYF, Xello, H&L, BLS / current primary source |  |
| 1SW Wk4 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Think-Pair-Share / Turn and Talk, Active Monitoring, Chunking | FYF, Xello, H&L, BLS / current primary source |  |
| 1SW Wk4 | 5 | Yes | Yes | Yes | Yes | Yes | NO | Yes | NO | Active Monitoring, Chunking, TVB | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 1SW Wk5 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Stop and Jot, Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 1SW Wk5 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Active Monitoring, Chunking | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 1SW Wk5 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Think-Pair-Share / Turn and Talk, Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 1SW Wk5 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Active Monitoring, TVB | FYF, Xello, H&L, BLS / current primary source |  |
| 1SW Wk5 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Active Monitoring, TVB | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 2SW Wk1 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Stop and Jot, Think-Pair-Share / Turn and Talk, Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 2SW Wk1 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Think-Pair-Share / Turn and Talk, Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 2SW Wk1 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 2SW Wk1 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Active Monitoring, TVB | FYF, Xello, H&L, BLS / current primary source |  |
| 2SW Wk1 | 5 | Yes | Yes | Yes | Yes | Yes | NO | Yes | NO | Active Monitoring | FYF, Climber Notes, Xello, H&L, BLS / current primary source | [VERIFY IN eDynamic] |
| 2SW Wk2 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 2SW Wk2 | 2 | Yes | Yes | Yes | Yes | Yes | NO | Yes | NO | Active Monitoring | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 2SW Wk2 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Active Monitoring | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 2SW Wk2 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 2SW Wk2 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 2SW Wk3 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Think-Pair-Share / Turn and Talk, Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 2SW Wk3 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Stop and Jot, Active Monitoring | Xello, H&L, BLS / current primary source |  |
| 2SW Wk3 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Active Monitoring | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 2SW Wk3 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | NO | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 2SW Wk3 | 5 | Yes | Yes | Yes | Yes | Yes | NO | Yes | NO | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 2SW Wk4 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Climber Notes, H&L, BLS / current primary source |  |
| 2SW Wk4 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF |  |
| 2SW Wk4 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | Xello, BLS / current primary source |  |
| 2SW Wk4 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | **REVIEW** |  |
| 2SW Wk4 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | Xello, H&L, BLS / current primary source |  |
| 2SW Wk5 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF |  |
| 2SW Wk5 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF |  |
| 2SW Wk5 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF |  |
| 2SW Wk5 | 4 | Yes | Yes | Yes | Yes | Yes | NO | Yes | Yes | Active Monitoring | FYF |  |
| 2SW Wk5 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | Xello |  |
| 2SW Wk6 | 1 | Yes | Yes | Yes | Yes | Yes | NO | Yes | Yes | Stop and Jot, Active Monitoring | H&L, BLS / current primary source |  |
| 2SW Wk6 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring, Chunking, TVB | FYF |  |
| 2SW Wk6 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Think-Pair-Share / Turn and Talk, Active Monitoring | FYF, BLS / current primary source |  |
| 2SW Wk6 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Think-Pair-Share / Turn and Talk, Active Monitoring | FYF |  |
| 2SW Wk6 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring, Chunking | FYF, Xello, H&L |  |
| 3SW Wk1 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Think-Pair-Share / Turn and Talk, Active Monitoring | FYF, H&L, BLS / current primary source |  |
| 3SW Wk1 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Stop and Jot, Active Monitoring | BLS / current primary source |  |
| 3SW Wk1 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Stop and Jot, Active Monitoring, Chunking | FYF |  |
| 3SW Wk1 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring, Chunking | Xello |  |
| 3SW Wk1 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, H&L, BLS / current primary source |  |
| 3SW Wk2 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, H&L |  |
| 3SW Wk2 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Think-Pair-Share / Turn and Talk, Active Monitoring | FYF |  |
| 3SW Wk2 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF |  |
| 3SW Wk2 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | BLS / current primary source |  |
| 3SW Wk2 | 5 | Yes | NO | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | Xello |  |
| 3SW Wk3 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Think-Pair-Share / Turn and Talk, Active Monitoring | H&L, BLS / current primary source |  |
| 3SW Wk3 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring, Chunking | FYF |  |
| 3SW Wk3 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF |  |
| 3SW Wk3 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring, TVB | BLS / current primary source |  |
| 3SW Wk3 | 5 | Yes | NO | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Xello |  |
| 3SW Wk4 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, H&L |  |
| 3SW Wk4 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 3SW Wk4 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF |  |
| 3SW Wk4 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF |  |
| 3SW Wk4 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 3SW Wk5 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, H&L |  |
| 3SW Wk5 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF |  |
| 3SW Wk5 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, BLS / current primary source |  |
| 3SW Wk5 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF |  |
| 3SW Wk5 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 3SW Wk6 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, H&L, BLS / current primary source |  |
| 3SW Wk6 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF |  |
| 3SW Wk6 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF |  |
| 3SW Wk6 | 4 | Yes | Yes | Yes | Yes | Yes | NO | Yes | Yes | Active Monitoring | FYF |  |
| 3SW Wk6 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring, Chunking | Xello, H&L |  |
| 4SW Wk1 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Think-Pair-Share / Turn and Talk, Active Monitoring | Xello, H&L |  |
| 4SW Wk1 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | **REVIEW** |  |
| 4SW Wk1 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | Xello, H&L, BLS / current primary source |  |
| 4SW Wk1 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | BLS / current primary source |  |
| 4SW Wk1 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | **REVIEW** |  |
| 4SW Wk2 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Stop and Jot, Active Monitoring | BLS / current primary source |  |
| 4SW Wk2 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring, Chunking | FYF, Xello, BLS / current primary source |  |
| 4SW Wk2 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Think-Pair-Share / Turn and Talk, Active Monitoring | BLS / current primary source |  |
| 4SW Wk2 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF |  |
| 4SW Wk2 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring, Chunking, TVB | FYF, Xello, BLS / current primary source |  |
| 4SW Wk3 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Think-Pair-Share / Turn and Talk, Active Monitoring | FYF, H&L |  |
| 4SW Wk3 | 2 | Yes | Yes | Yes | Yes | Yes | NO | Yes | Yes | Active Monitoring, Chunking | FYF, Climber Notes, H&L, BLS / current primary source |  |
| 4SW Wk3 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | **REVIEW** |  |
| 4SW Wk3 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring, Chunking | **REVIEW** |  |
| 4SW Wk3 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | Xello, H&L, BLS / current primary source |  |
| 4SW Wk4 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, H&L |  |
| 4SW Wk4 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring, Chunking | H&L, BLS / current primary source |  |
| 4SW Wk4 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | **REVIEW** |  |
| 4SW Wk4 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | **REVIEW** |  |
| 4SW Wk4 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | H&L, BLS / current primary source |  |
| 4SW Wk5 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Think-Pair-Share / Turn and Talk, Active Monitoring | FYF, H&L |  |
| 4SW Wk5 | 2 | Yes | Yes | Yes | Yes | Yes | NO | Yes | Yes | Active Monitoring | H&L, BLS / current primary source |  |
| 4SW Wk5 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | Xello, H&L, BLS / current primary source |  |
| 4SW Wk5 | 4 | Yes | Yes | Yes | Yes | Yes | NO | Yes | Yes | Active Monitoring | FYF, BLS / current primary source |  |
| 4SW Wk5 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | Xello, H&L, BLS / current primary source |  |
| 4SW Wk6 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF |  |
| 4SW Wk6 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | **REVIEW** |  |
| 4SW Wk6 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | BLS / current primary source |  |
| 4SW Wk6 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | H&L |  |
| 4SW Wk6 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | **REVIEW** |  |
| 5SW Wk1 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, H&L |  |
| 5SW Wk1 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | Xello, H&L, BLS / current primary source |  |
| 5SW Wk1 | 3 | Yes | NO | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | BLS / current primary source |  |
| 5SW Wk1 | 4 | Yes | NO | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | **REVIEW** |  |
| 5SW Wk1 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Climber Notes, H&L, BLS / current primary source |  |
| 5SW Wk2 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 5SW Wk2 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | BLS / current primary source |  |
| 5SW Wk2 | 3 | Yes | NO | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | **REVIEW** |  |
| 5SW Wk2 | 4 | Yes | NO | Yes | Yes | Yes | NO | Yes | Yes | Active Monitoring | **REVIEW** |  |
| 5SW Wk2 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 5SW Wk3 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | Xello, H&L, BLS / current primary source |  |
| 5SW Wk3 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | **REVIEW** |  |
| 5SW Wk3 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring, Chunking | H&L, BLS / current primary source |  |
| 5SW Wk3 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Climber Notes |  |
| 5SW Wk3 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L |  |
| 5SW Wk4 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 5SW Wk4 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 5SW Wk4 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 5SW Wk4 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 5SW Wk4 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Climber Notes, Xello, H&L, BLS / current primary source |  |
| 5SW Wk5 | 1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 5SW Wk5 | 2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 5SW Wk5 | 3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 5SW Wk5 | 4 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 5SW Wk5 | 5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 5SW Wk6 | 1 | Yes | NO | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | Xello, H&L, BLS / current primary source |  |
| 5SW Wk6 | 2 | Yes | NO | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | Xello, H&L, BLS / current primary source |  |
| 5SW Wk6 | 3 | Yes | NO | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 5SW Wk6 | 4 | Yes | NO | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring, Chunking | Xello, H&L, BLS / current primary source |  |
| 5SW Wk6 | 5 | Yes | NO | Yes | Yes | Yes | Yes | Yes | Yes | Active Monitoring | Xello, H&L, BLS / current primary source |  |
| 6SW Wk1 | 1 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 6SW Wk1 | 2 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | Xello, H&L, BLS / current primary source |  |
| 6SW Wk1 | 3 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | Xello, H&L, BLS / current primary source |  |
| 6SW Wk1 | 4 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 6SW Wk1 | 5 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 6SW Wk2 | 1 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 6SW Wk2 | 2 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | Xello, H&L, BLS / current primary source |  |
| 6SW Wk2 | 3 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 6SW Wk2 | 4 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | Xello, H&L, BLS / current primary source |  |
| 6SW Wk2 | 5 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 6SW Wk3 | 1 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Think-Pair-Share / Turn and Talk, Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 6SW Wk3 | 2 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 6SW Wk3 | 3 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 6SW Wk3 | 4 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | FYF, Xello, H&L, BLS / current primary source |  |
| 6SW Wk3 | 5 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | Xello, H&L, BLS / current primary source |  |
| 6SW Wk4 | 1 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | FYF, H&L, BLS / current primary source |  |
| 6SW Wk4 | 2 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | H&L, BLS / current primary source |  |
| 6SW Wk4 | 3 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | FYF, H&L, BLS / current primary source |  |
| 6SW Wk4 | 4 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | H&L, BLS / current primary source |  |
| 6SW Wk4 | 5 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | H&L, BLS / current primary source |  |
| 6SW Wk5 | 1 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | Xello, H&L |  |
| 6SW Wk5 | 2 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | Xello, H&L |  |
| 6SW Wk5 | 3 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring, Chunking | Xello, H&L |  |
| 6SW Wk5 | 4 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | Xello, H&L |  |
| 6SW Wk5 | 5 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | Xello, H&L |  |
| 6SW Wk6 | 1 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | H&L |  |
| 6SW Wk6 | 2 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | H&L |  |
| 6SW Wk6 | 3 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | H&L |  |
| 6SW Wk6 | 4 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | H&L |  |
| 6SW Wk6 | 5 | Yes | NO | Yes | Yes | NO | Yes | Yes | Yes | Active Monitoring | H&L |  |

## Exact district-label gap

- 1SW Wk0 Day 1: Topic, Objective, DOL
- 1SW Wk0 Day 2: Topic, Objective, DOL
- 1SW Wk0 Day 3: Topic, Objective, DOL
- 1SW Wk0 Day 4: Topic, Objective, DOL
- 1SW Wk0 Day 5: Topic, Objective, DOL
- 1SW Wk1 Day 1: Topic, Objective, DOL
- 1SW Wk1 Day 2: Topic, Objective, DOL
- 1SW Wk1 Day 3: Topic, Objective, DOL
- 1SW Wk1 Day 4: Topic, Objective, DOL
- 1SW Wk1 Day 5: Topic, Objective, DOL
- 1SW Wk2 Day 1: Topic, Objective, DOL
- 1SW Wk2 Day 2: Topic, Objective, DOL
- 1SW Wk2 Day 3: Topic, Objective, DOL
- 1SW Wk2 Day 4: Topic, Objective, DOL
- 1SW Wk2 Day 5: Topic, Objective, DOL
- 1SW Wk3 Day 1: Topic, Objective, DOL
- 1SW Wk3 Day 2: Topic, Objective, DOL
- 1SW Wk3 Day 3: Topic, Objective, DOL
- 1SW Wk3 Day 4: Topic, Objective, DOL
- 1SW Wk3 Day 5: Topic, Objective, DOL
- 1SW Wk4 Day 1: Topic, Objective, DOL
- 1SW Wk4 Day 2: Topic, Objective, DOL
- 1SW Wk4 Day 3: Topic, Objective, DOL
- 1SW Wk4 Day 4: Topic, Objective, DOL
- 1SW Wk4 Day 5: Topic, Objective, DOL
- 1SW Wk5 Day 1: Topic, Objective, DOL
- 1SW Wk5 Day 2: Topic, Objective, DOL
- 1SW Wk5 Day 3: Topic, Objective, DOL
- 1SW Wk5 Day 4: Topic, Objective, DOL
- 1SW Wk5 Day 5: Topic, Objective, DOL
- 2SW Wk1 Day 1: Topic, Objective, DOL
- 2SW Wk1 Day 2: Topic, Objective, DOL
- 2SW Wk1 Day 3: Topic, Objective, DOL
- 2SW Wk1 Day 4: Topic, Objective, DOL
- 2SW Wk1 Day 5: Topic, Objective, DOL
- 2SW Wk2 Day 1: Topic, Objective, DOL
- 2SW Wk2 Day 2: Topic, Objective, DOL
- 2SW Wk2 Day 3: Topic, Objective, DOL
- 2SW Wk2 Day 4: Topic, Objective, DOL
- 2SW Wk2 Day 5: Topic, Objective, DOL
- 2SW Wk3 Day 1: Topic, Objective, DOL
- 2SW Wk3 Day 2: Topic, Objective, DOL
- 2SW Wk3 Day 3: Topic, Objective, DOL
- 2SW Wk3 Day 4: Topic, Objective, DOL
- 2SW Wk3 Day 5: Topic, Objective, DOL
- 2SW Wk4 Day 1: Topic, Objective, DOL
- 2SW Wk4 Day 2: Topic, Objective, DOL
- 2SW Wk4 Day 3: Topic, Objective, DOL
- 2SW Wk4 Day 4: Topic, Objective, DOL
- 2SW Wk4 Day 5: Topic, Objective, DOL
- 2SW Wk5 Day 1: Topic, Objective, DOL
- 2SW Wk5 Day 2: Topic, Objective, DOL
- 2SW Wk5 Day 3: Topic, Objective, DOL
- 2SW Wk5 Day 4: Objective, DOL
- 2SW Wk5 Day 5: Topic, Objective, DOL
- 2SW Wk6 Day 1: Topic, Objective, DOL
- 2SW Wk6 Day 2: Topic, Objective, DOL
- 2SW Wk6 Day 3: Topic, Objective, DOL
- 2SW Wk6 Day 4: Topic, Objective, DOL
- 2SW Wk6 Day 5: Topic, Objective, DOL
- 3SW Wk1 Day 1: Topic, Objective, DOL
- 3SW Wk1 Day 2: Topic, Objective, DOL
- 3SW Wk1 Day 3: Topic, Objective, DOL
- 3SW Wk1 Day 4: Topic, Objective, DOL
- 3SW Wk1 Day 5: Topic, Objective, DOL
- 3SW Wk2 Day 1: Topic, Objective, DOL
- 3SW Wk2 Day 2: Topic, Objective, DOL
- 3SW Wk2 Day 3: Topic, Objective, DOL
- 3SW Wk2 Day 4: Topic, Objective, DOL
- 3SW Wk2 Day 5: Topic, Objective, DOL
- 3SW Wk3 Day 1: Topic, Objective, DOL
- 3SW Wk3 Day 2: Topic, Objective, DOL
- 3SW Wk3 Day 3: Topic, Objective, DOL
- 3SW Wk3 Day 4: Topic, Objective, DOL
- 3SW Wk3 Day 5: Topic, Objective, DOL
- 3SW Wk4 Day 1: Topic, Objective, DOL
- 3SW Wk4 Day 2: Topic, Objective, DOL
- 3SW Wk4 Day 3: Topic, Objective, DOL
- 3SW Wk4 Day 4: Topic, Objective, DOL
- 3SW Wk4 Day 5: Topic, Objective, DOL
- 3SW Wk5 Day 1: Topic, Objective, DOL
- 3SW Wk5 Day 2: Topic, Objective, DOL
- 3SW Wk5 Day 3: Topic, Objective, DOL
- 3SW Wk5 Day 4: Topic, Objective, DOL
- 3SW Wk5 Day 5: Topic, Objective, DOL
- 3SW Wk6 Day 1: Topic, Objective, DOL
- 3SW Wk6 Day 2: Topic, Objective, DOL
- 3SW Wk6 Day 3: Topic, Objective, DOL
- 3SW Wk6 Day 4: Topic, Objective, DOL
- 3SW Wk6 Day 5: Topic, Objective, DOL
- 4SW Wk1 Day 1: Topic, Objective, DOL
- 4SW Wk1 Day 2: Topic, Objective, DOL
- 4SW Wk1 Day 3: Topic, Objective, DOL
- 4SW Wk1 Day 4: Topic, Objective, DOL
- 4SW Wk1 Day 5: Topic, Objective, DOL
- 4SW Wk2 Day 1: Topic, Objective, DOL
- 4SW Wk2 Day 2: Topic, Objective, DOL
- 4SW Wk2 Day 3: Topic, Objective, DOL
- 4SW Wk2 Day 4: Topic, Objective, DOL
- 4SW Wk2 Day 5: Topic, Objective, DOL
- 4SW Wk3 Day 1: Topic, Objective, DOL
- 4SW Wk3 Day 2: Topic, Objective, DOL
- 4SW Wk3 Day 3: Topic, Objective, DOL
- 4SW Wk3 Day 4: Topic, Objective, DOL
- 4SW Wk3 Day 5: Topic, Objective, DOL
- 4SW Wk4 Day 1: Topic, Objective, DOL
- 4SW Wk4 Day 2: Topic, Objective, DOL
- 4SW Wk4 Day 3: Topic, Objective, DOL
- 4SW Wk4 Day 4: Topic, Objective, DOL
- 4SW Wk4 Day 5: Topic, Objective, DOL
- 4SW Wk5 Day 1: Topic, Objective, DOL
- 4SW Wk5 Day 2: Topic, Objective, DOL
- 4SW Wk5 Day 3: Topic, Objective, DOL
- 4SW Wk5 Day 4: Topic, Objective, DOL
- 4SW Wk5 Day 5: Topic, Objective, DOL
- 4SW Wk6 Day 1: Topic, Objective, DOL
- 4SW Wk6 Day 2: Topic, Objective, DOL
- 4SW Wk6 Day 3: Topic, Objective, DOL
- 4SW Wk6 Day 4: Topic, Objective, DOL
- 4SW Wk6 Day 5: Topic, Objective, DOL
- 5SW Wk1 Day 1: Topic, Objective, DOL
- 5SW Wk1 Day 2: Topic, Objective, DOL
- 5SW Wk1 Day 3: Topic, Objective, DOL
- 5SW Wk1 Day 4: Topic, Objective, DOL
- 5SW Wk1 Day 5: Topic, Objective, DOL
- 5SW Wk2 Day 1: Topic, Objective, DOL
- 5SW Wk2 Day 2: Topic, Objective, DOL
- 5SW Wk2 Day 3: Topic, Objective, DOL
- 5SW Wk2 Day 4: Topic, Objective, DOL
- 5SW Wk2 Day 5: Topic, Objective, DOL
- 5SW Wk3 Day 1: Topic, Objective, DOL
- 5SW Wk3 Day 2: Topic, Objective, DOL
- 5SW Wk3 Day 3: Topic, Objective, DOL
- 5SW Wk3 Day 4: Topic, Objective, DOL
- 5SW Wk3 Day 5: Topic, Objective, DOL
- 5SW Wk4 Day 1: Topic, Objective, DOL
- 5SW Wk4 Day 2: Topic, Objective, DOL
- 5SW Wk4 Day 3: Topic, Objective, DOL
- 5SW Wk4 Day 4: Topic, Objective, DOL
- 5SW Wk4 Day 5: Topic, Objective, DOL
- 5SW Wk5 Day 1: Topic, Objective, DOL
- 5SW Wk5 Day 2: Topic, Objective, DOL
- 5SW Wk5 Day 3: Topic, Objective, DOL
- 5SW Wk5 Day 4: Topic, Objective, DOL
- 5SW Wk5 Day 5: Topic, Objective, DOL
- 5SW Wk6 Day 1: Topic, Objective, DOL
- 5SW Wk6 Day 2: Topic, Objective, DOL
- 5SW Wk6 Day 3: Topic, Objective, DOL
- 5SW Wk6 Day 4: Topic, Objective, DOL
- 5SW Wk6 Day 5: Topic, Objective, DOL
- 6SW Wk1 Day 1: Topic, Objective, DOL
- 6SW Wk1 Day 2: Topic, Objective, DOL
- 6SW Wk1 Day 3: Topic, Objective, DOL
- 6SW Wk1 Day 4: Topic, Objective, DOL
- 6SW Wk1 Day 5: Topic, Objective, DOL
- 6SW Wk2 Day 1: Objective, DOL
- 6SW Wk2 Day 2: Objective, DOL
- 6SW Wk2 Day 3: Objective, DOL
- 6SW Wk2 Day 4: Objective, DOL
- 6SW Wk2 Day 5: Objective, DOL
- 6SW Wk3 Day 1: Objective, DOL
- 6SW Wk3 Day 2: Objective, DOL
- 6SW Wk3 Day 3: Objective, DOL
- 6SW Wk3 Day 4: Objective, DOL
- 6SW Wk3 Day 5: Objective, DOL
- 6SW Wk4 Day 1: Topic, Objective, DOL
- 6SW Wk4 Day 2: Topic, Objective, DOL
- 6SW Wk4 Day 3: Topic, Objective, DOL
- 6SW Wk4 Day 4: Topic, Objective, DOL
- 6SW Wk4 Day 5: Topic, Objective, DOL
- 6SW Wk5 Day 1: Topic, Objective, DOL
- 6SW Wk5 Day 2: Topic, Objective, DOL
- 6SW Wk5 Day 3: Topic, Objective, DOL
- 6SW Wk5 Day 4: Topic, Objective, DOL
- 6SW Wk5 Day 5: Topic, Objective, DOL
- 6SW Wk6 Day 1: Topic, Objective, DOL
- 6SW Wk6 Day 2: Topic, Objective, DOL
- 6SW Wk6 Day 3: Topic, Objective, DOL
- 6SW Wk6 Day 4: Topic, Objective, DOL
- 6SW Wk6 Day 5: Topic, Objective, DOL

## Unresolved verification markers

- 1SW Wk1 Day 5: [VERIFY IN eDynamic]
- 2SW Wk1 Day 5: [VERIFY IN eDynamic]

## Manual grounding protocol

For each day, record a verdict for: S&S topic/activity; exact FYF printed page and section; exact Climber deck/slide; exact Xello task/time/minimum/prerequisite; supplemental-platform boundary; current pathway and labor-data claims; TEKS verb/action/evidence; teacher cold-start readiness; student clarity; EB supports; district move; artifact response space; and absence/platform route.

A day is **Copy-ready** only when every load-bearing item is verified and the teacher can run the lesson without inventing directions, examples, answers, data, materials, or timing decisions.
