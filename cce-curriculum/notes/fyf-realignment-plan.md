# FYF Realignment Plan — Official Irving Workbook

**Date:** 2026-08-05 · **Status:** DRAFT, awaiting ratification of the Decision Register (§6)
**Supersedes:** the generic-workbook citation layer that `revision-plan.md` built. That file stays as history; this file governs the 2026-27 re-sync.

## 1. Situation

The official Irving ISD workbook arrived 2026-08-05: **"Find Your Future" (FYF)**, © 2026 Hats & Ladders, 308-page PDF, student edition. It replaces the generic 17-chapter H&L workbook as the book in students' hands. It is a different book, not a revision: 16 career-cluster "Career Climb" chapters mirroring the CCE scope and sequence, 57 career activities, 23 embedded Powerskill lessons, 14 Irving-specific "What is Happening at My District?" pages, 13 "App Exploration" pages, and an 11-part Capstone (Rungs 1-8 + Prepare & Present + Final Reflection).

Files: `cce-curriculum/resources/reference-pdfs/IrvingFindYourFuture2026.pdf` (gitignored) + `IrvingFindYourFuture2026.txt` (tracked extract; form-feed page breaks, segment N = PDF page N).

## 2. Citation rules (binding)

1. **Convention:** `(FYF p. N: "Section Name")` — printed page numbers. **Printed = PDF − 6**, constant across the body (body = PDF 7-306 = printed 1-300).
2. **Never cite chapter or tab numbers.** The printed side-tabs for chapters 13/14 are physically swapped (Education & Training carries tab 14, Business carries tab 13).
3. **Never trust the book's own TOC folios.** They are misprinted in four offset bands (0 / +142 / +114 / +116). Section list and order are correct; the numbers are not.
4. **Known print errata** (full memo drafted 2026-08-05): printed pp. 228/230 transposed; double footer on p. 65; broken step numbering in 8 activities (Ultrasound Detectives, Smile Squad, Crash Crew, Safety Supervisor, Million Dollar Idea, Machine Breakdown Mystery, Transportation Survey Project, Data-Informed Decision Making). Lesson prose that walks students through steps must use the *actual* sequence, not the printed numbering.
5. **Reading level:** FYF body text measures ~FK 10. Never lift FYF prose into student-facing text; paraphrase down to the 6th-7th ESL standard.
6. **Climber Notes** (teacher decks, delivered 2026-08-05): cite as `(Climber Notes: "Deck Name", slide N)` — teacher-facing references only, never in student-facing text. Index + tracked extracts: `cce-curriculum/resources/climber-notes/INDEX.md`. App-instruction slides in the decks give exact H&L app paths; use those for `[H&L PLATFORM]` lines instead of inventing navigation.

## 3. Scale of the change

The citation inventory found **2,266 workbook-dependent lines** across all 36 weeks (the documented `(H&L Ch N, p. X)` convention covers ~1% of them; 366 lines are activity-name-only with no citation token, mostly day-file H1 titles). These collapse to **~204 distinct dispositions + 119 heading renames**:

| Disposition | Count | Meaning |
|---|---|---|
| RECITE | 75 | Near-equivalent exists; mechanical re-point to `(FYF p. N: "Name")` |
| REWRITE | 56 | Activity exists but content drifted, or a different FYF activity fills the slot; lesson prose changes |
| DROP | 65 | No FYF equivalent; lesson leans on H&L app, Xello, or eDynamic instead |
| KEEP-PS | 8 | Cites the separate Powerskills supplement; pending Decision D-11 |
| HEADING | 119 | Day-file titles embedding old activity names |

Week sizing: **8 S** (re-cite only), **13 M** (some rewrites), **15 L** (structural). Tier C platform markers (38) and Tier D soft mentions (851) need no per-line work.

## 4. Per-week rollup

Full per-week disposition tables live in the session crosswalk (`realignment_crosswalk.md`, session scratchpad; re-derivable from the two inventories). Rollup:

| # | Week | New home (printed pp.) | Size | Flags |
|---|---|---|---|---|
| 1 | 1sw/wk0-classroom-routines | Ch1 World of Work 1-22 | L | RIASEC + Work Values + 14-cluster rating all absent from FYF |
| 2 | 1sw/wk1-robotics-manufacturing | Manufacturing 199-212 | M | TEKS d(7)(D) gate; Climber Notes |
| 3 | 1sw/wk2-programming-it | IT 23-38 | M | IT chapter thin: 5 sections across 4 weeks |
| 4 | 1sw/wk3-computer-science-it | IT 23-38 | L | TEKS d(7)(C) gate; no networking content |
| 5 | 1sw/wk4-tech-support-it | IT 23-38 | S | No dedicated activity available |
| 6 | 1sw/wk5-cybersecurity-it | IT 23-38 | L | Old 3-day flagship gone; Work Ethic (34-35) is cybersecurity-themed (D-4) |
| 7 | 2sw/wk1-legal-studies | Law 39-58 | M | Two new activities to absorb (City Council in Action, Policy Showdown) |
| 8 | 2sw/wk2-law-enforcement-emt | Law 39-58 | L | Both multi-day activities replaced (Clinton Lake Case, Injured on the Trail) |
| 9 | 2sw/wk3-nursing-health-science | Health 59-86 | S | Gains 7pp content |
| 10 | 2sw/wk4-dental-medical-billing | Health 59-86 | S | Climber Notes |
| 11 | 2sw/wk5-powerskills-communication | Powerskills in Action 139-148 + Ch1/Ch4/Ch8 | L | Decision D-11; Giving/Receiving Feedback has no equivalent |
| 12 | 2sw/wk6-biomedical-health-science | Health 59-86 | L | TEKS gate; Outbreak Investigators takes the Farm Fresh Express slot (D-3) |
| 13 | 3sw/wk1-vet-science | Ag 87-102 | M | Vet triage content is an upgrade |
| 14 | 3sw/wk2-plant-science | Ag 87-102 | S | Cleanest week |
| 15 | 3sw/wk3-sustainable-engineering | Ag 87-102 + Ch9 | M | Activity shrank 8pp to 3pp |
| 16 | 3sw/wk4-culinary-hospitality | Hospitality 111-126 | M | No tourism content in FYF |
| 17 | 3sw/wk5-cosmetology | Human Services 127-138 | L | Interviews lost; Special Effects Makeup reshapes the week (D-3) |
| 18 | 3sw/wk6-entrepreneurship | Business 221-254 | L | Both old flagships gone; Million Dollar Idea lands here (D-7) |
| 19 | 4sw/wk1-career-planning | Capstone Rungs 1-3 + Ch1 + Ch9 | M | Career Iceberg moved to Ch1 (D-2) |
| 20 | 4sw/wk2-course-mapping | Capstone 292-296 | S | Rung 7 names CTSOs and campuses; upgrade |
| 21 | 4sw/wk3-aviation | Transportation 149-170 | M | Flight Line Fixers 6pp available (D-9) |
| 22 | 4sw/wk4-drone-engineering | Engineering 103-110 | S | Engineering chapter thin |
| 23 | 4sw/wk5-automotive | Transportation 149-170 | M | Delivery Connection App gone |
| 24 | 4sw/wk6-trades-capstone | Transportation 153-155 + Capstone | S | Takes Analytical Reasoning, not Work Ethic (D-4) |
| 25 | 5sw/wk1-architecture | A&C 171-198 | M | Trash to Treasure + Power Pitch gone (D-5) |
| 26 | 5sw/wk2-civil-engineering | Engineering 103-110 + A&C 174-175 | L | Worst deficit; no civil content exists in FYF |
| 27 | 5sw/wk3-construction-trades | A&C 171-198 | L | 35 Power Pitch lines, no replacement (D-5) |
| 28 | 5sw/wk4-hvac-electrical-plumbing | A&C 185-195 + Manufacturing 204-206 | M | Biggest gain: 0 to 8pp on-topic |
| 29 | 5sw/wk5-personal-budget | Capstone 285-286 + Business 238-240 | L | Week is named after deleted Lifestyle Snapshot |
| 30 | 5sw/wk6-real-estate | Business 221-254 | S | Gains 2 exact-match activities |
| 31 | 6sw/wk1-education | Ed&Training 213-220 + Ch1 | L | 8pp/2 activities vs 107 dependency lines; Leadership borrowed from Ch1 |
| 32 | 6sw/wk2-graphic-design-resume | Arts 255-276 | M | Arts over-supplied; good problem |
| 33 | 6sw/wk3-business-marketing | Business 221-254 + Ch9 | M | pp. 228/230 transposition sits here; Expert Edge lands here (D-7) |
| 34 | 6sw/wk4-sales-presentations | Business 241-251 + Capstone | L | 3-day team pitch gone; 30 Seconds to Sell is individual (D-5) |
| 35 | 6sw/wk5-job-skills-mock-interview | Capstone 287-291 + Business 248-253 | L | Most concentrated loss: 4 activities absent; TEKS gate |
| 36 | 6sw/wk6-capstone | Capstone 277-300 + Ch1 | M | Gains 32-pt rubric + 7 presentation modalities |

## 5. The Ch-16 spine redistribution

Old Ch 16 "My Next Steps" was cited in 17 weeks (98 lines). FYF concentrates that content in the Capstone chapter. Redistribution:

- **Rungs 1-3** anchor 4SW Wk1 (mid-year review); **Rungs 6-7** anchor 4SW Wk2 (course mapping); **Rung 4** (Strengths Interview, needs an out-of-class adult) assigned take-home in 6SW Wk4, debriefed 6SW Wk6; **Rung 5** (Local Connections) practiced 6SW Wk1 Day 3, graded 6SW Wk5 (see D-6); **Requirements + rubric (277-280), Rung 8, Prepare & Present (299), Final Reflection (300)** anchor 6SW Wk6.
- Old Iceberg Cartoon → "The Career Iceberg" (pp. 6-8), which moved to Chapter 1 (D-2). Old Lifestyle Snapshot → no successor (drives 5SW Wk5's L rating).
- The other 12 Ch-16-citing weeks keep their Day-5 Career Plan ritual as `[H&L PLATFORM]` app instructions (no workbook citation), use that cluster's App Exploration page for app steps, and add a one-line forward reference to the rung the week feeds.

## 6. Decision Register (Elisha ratifies)

| # | Decision | Recommendation |
|---|---|---|
| D-1 | "Hat Research" template cited 187x across ~20 weeks; absent from FYF | Retire the citation form. Teach the research format once in Wk0 from `(FYF pp. 4-5: "Perks and Quirks")`; weekly app steps cite each cluster's App Exploration page; keep the printed worksheet as a CCE-original artifact |
| D-2 | Career Iceberg moved from year-end to FYF Ch1 (pp. 6-8); worked example changed trophy → nurse | Keep CCE's mid-year + capstone placements; cite pp. 6-8 both places; strike "final chapter" framing |
| D-3 | Advocacy (134-135) contended by three weeks | 2SW Wk5 gets Advocacy; 2SW Wk6 → Outbreak Investigators (74-78); 3SW Wk5 → Special Effects Makeup (128-131); 6SW Wk4 drops its thin reference |
| D-4 | Work Ethic (34-35) scenario is a cybersecurity bootcamp | Award to 1SW Wk5 (cybersecurity); 4SW Wk6 takes Analytical Reasoning (153-155), matching its S&S line |
| D-5 | Old Power Pitch / team Pitching Investors gone; only individual "30 Seconds to Sell" (241-243) exists | 5SW Wk3 keeps a CCE-original self-pitch citing Prepare & Present (299) for delivery; 6SW Wk4 adopts 30 Seconds to Sell |
| D-6 | Rung 5 used twice (practiced 6SW Wk1, graded 6SW Wk5); Rung 4 as take-home | Confirm both sequencings or pick single owners |
| D-7 | Two entrepreneurship activities, two hungry weeks | Million Dollar Idea (234-237) → 3SW Wk6; Expert Edge (222-224) → 6SW Wk3 |
| D-8 | Adopt all 14 District pages + 13 App Exploration pages (~27 never-cited pages) as standing per-week content | Adopt; it changes what a cluster-tour day looks like but is the highest-value new content in the book |
| D-9 | Flight Line Fixers (160-165) as 4SW Wk3 spine turns an M week into an L rewrite | Conservative default: keep as extension, not spine |
| D-10 | Drops break TEKS d(7)(C) (job applications) and d(7)(D) (references) | Mandatory 6-step TEKS audit for 1SW Wk1, 1SW Wk3, 2SW Wk6, 6SW Wk4, 6SW Wk5 before shipping |
| D-11 | Do students still receive the separate Powerskills supplement? 8 KEEP-PS citations + all of 2SW Wk5 hang on this | Unknown; if FYF-only, 2SW Wk5 re-anchors on Powerskills in Action (139-148) + cluster-embedded lessons |
| D-12 | District-expectations integration approach (from 2026-08-04 audit) | Overlay upgrade in the same per-week pass: continuum-specific IISD Instructional Strategies sections, 5E phase mapping annotations, exemplar-plan elements; NOT a full 5E restructure of 180 day files |

## 7. Blockers and risks

1. **Climber Notes packet — RESOLVED 2026-08-05.** All 14 referenced decks delivered, plus three decks with no student-book counterpart: "Exploring Your Work Values" and "Learning Your Core Personality Types" (the Work Values and RIASEC-equivalent content Wk0 lost; the six H&L core types are Doer, Analyzer, Creator, Helper, Persuader, Organizer — never use RIASEC letter codes in student-facing text) and "Capturing the Feeling" (image-only, unidentified, inspect visually). See `cce-curriculum/resources/climber-notes/INDEX.md`. Wk0's L rating softens accordingly.
2. **Teaching guide** still undelivered (no answer keys, timing, differentiation in the student edition). Partially mitigated: Climber Notes speaker notes carry some facilitation guidance, and 8 general teacher resources arrived with them (`cce-curriculum/resources/hl-teacher-resources/INDEX.md`).
3. **Thin chapters.** Engineering (8pp) and Education & Training (8pp) cannot carry their weeks; IT (16pp) spans 4-5 weeks. The workbook is a supplement; H&L app + Xello + eDynamic remain the load-bearing platforms for those weeks.
4. **Both scope-and-sequence copies** (`docs/` and `cce-curriculum/`) carry old citations and must be re-synced together (the `cce-curriculum/` copy is authoritative).
5. **Exit-ticket PDFs:** any exit-ticket text change requires `python3 build/build_pdfs.py` + `inject_pdf_links.py` regeneration. Note: mkdocs/build tooling lives under `/usr/bin/python3`, not Homebrew python3.

## 8. Implementation phases

Each week's pass bundles: dispositions from the crosswalk → heading renames → TEKS audit where gated (D-10) → district-expectations overlay (D-12) → ESL check on student-facing text → preservation loop → strict build → PDF regeneration if exit tickets changed.

- **Phase A (urgent, school start): 1SW block** — Wk0 through Wk5 (1 S, 2 M, 3 L). Wk0 also gets its long-planned audit pass (old exit-ticket convention, DOK-1 recall).
- **Phase B: 2SW + 3SW** (12 weeks; includes the 2SW Wk5 Powerskills re-anchor pending D-11).
- **Phase C: 4SW + 5SW + 6SW** (18 weeks; includes the spine redistribution §5).

Post-pass: refresh `docs/resources/resources-status.md`, `revision-plan.md` header note, PLANNING §4.x closure, and re-export the offline teacher-review HTML.
