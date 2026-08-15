# Day-1 Readiness Backlog — 2026-08-05 baseline audit

> **Historical baseline, not current completion status.** This file preserves the original evidence and workstream decomposition that drove the structure revision. Since this audit, the course gained 250 verified worksheet/rubric/reference PDFs, a locked three-minor/two-major map for every six weeks, an authenticated Xello sequence, paired Canvas build packages for all 36 weeks, and live unpublished Canvas content through 4SW Wk1. Use `docs/resources/resources-status.md`, `docs/resources/six-weeks-assessment-map.md`, and `cce-curriculum/notes/canvas-build-log.md` for current state. Do not reopen a missing-artifact claim here without checking those sources and the current filesystem first.

**The question this answers:** can a brand-new teacher open the live site Monday morning — with the site, a class set of the "Find Your Future" workbook, the printed exit tickets, and standard classroom stock — and teach the day? Five parallel auditors swept all 36 weeks (145 teaching days), the workbook's own teacher-provisioning assumptions, the site's onboarding surface, and the year-level assessment infrastructure.

**Detail files (per-finding evidence with file:line):** `day1-audit/day1-findings-{1sw, 2sw-3sw, 4sw-5sw, 6sw-assessment, crosscut}.md`

**Relationship to `docs/resources/resources-status.md`:** that page remains the site-facing status ledger and already names many of these items. This document is the prioritized work plan behind it; task S6 below syncs the two. Do not maintain two divergent ledgers — resources-status gets the status flags, this file holds the plan.

---

## 1. The verdict map

At the time of the August 5 audit, zero of 36 weeks were turnkey. Eighteen were RUNNABLE-WITH-PRINTING and eighteen had at least one blocked day. The table below records that original baseline; it is not the August 8 Canvas-production verdict.

| Block | Blocked | Why (dominant cause) |
|---|---|---|
| 1SW | Wk0, Wk1, Wk3 (D2 only), Wk4, Wk5 | Missing keystone printables (Wk0); Sphero/micro:bit/Glowforge with no inventory check or fallback; repo-only decks; one missing URL (Wk3 D2 — one-line fix) |
| 2SW | Wk2, Wk3 (D3-4), Wk4 (D1, D4) | Clinton Lake + Injured on the Trail decks repo-only; micro:bit; the medical-coding day's charts and answer key were never authored |
| 3SW | Wk2 (D3), Wk5 | Canva for Education unprovisioned; SFX consumable order (~150 silicone skins) unquantified with allergy-screen lead time |
| 4SW | Wk2, Wk3, Wk4 | d(8)(C) course-map week has no course-sequence source by either route; LEGO sets + aircraft; drones + flight space |
| 5SW | Wk2, Wk3, Wk4 | Straw-bridge kits (400+ straws/section); Spot the Problem + Written Communication decks repo-only; Wk3 D5 jigsaw presentations never assigned by any earlier day |
| 6SW | Wk4, Wk5 | Career Presentation Rubric (11 refs) and Interview Appearance Guide don't exist; the Wk5 seven-artifact interview packet — "the source, not the book" — doesn't exist |

**Aggregate finding counts:** MISSING-PRINTABLE 216 · MISSING-SETUP 76 · MISSING-RUBRIC-OR-KEY 64 · MISSING-SUPPLY 60 · STRUCTURE 49 · REVISE 23 · MISSING-DECK 12 · VAGUE-SPEC 12 · plus per-day prep actions rolled up per week in the detail files.

**The good news, verified independently by all five auditors:** the specs are done. VAGUE-SPEC is near zero everywhere (0 in 4SW-6SW). Nearly every missing artifact is described in the day pages down to fields, rows, and worked examples. This is production volume, not design work — and the PDF factory (`build/build_pdfs.py`: Chromium render, Irving branding, 16 designed formats) already exists and needs only a worksheet input contract and a multi-page rule.

---

## 2. The seven headline gaps (largest blast radius first)

1. **The CCE career research worksheet does not exist.** ~22 files across all six blocks hand it out as "the same six-field format students learned in Wk0" (69 references in 2SW-3SW alone, in five different layout shapes). Wk0 Day 5 — where it is taught — also misdescribes its fields relative to FYF p. 5 (two fields are CCE-new, four workbook fields are dropped), so it must be built from the corrected spec in `day1-audit/day1-findings-1sw.md`, not from the Wk0 page.
2. **The 17 Climber Notes decks are reachable by no one but Elisha.** Gitignored `.pptx`, off-site directory, and the tracked extracts hold image *counts*, not images. Fourteen workbook activities have no content without them (FYF literally prints "Get Climber Notes from your teacher"); the two orphan decks are the sole source for Wk0's personality/work-values days; the Safe or Spoofed phishing emails and Spot the Problem inspection images are unrecoverable from anything tracked. `resources-status.md` says five times they are "already in the repo" — false from any machine but Elisha's.
3. **Assessment instruments are incomplete.** The six-weeks gradebook structure is now set at 40% minor and 60% major, with at least 3 minor and 2 major grades. However, 25 distinct rubrics are referenced; 12 exist and 11 are bare mentions, including the Mock Interview Rubric and Career Presentation Rubric. All 36 weekly summatives except about 3 have criteria but no performance levels. About 7 objectively scored workbook activities still lack a key. Semester assessment policy remains open.
4. **Hardware availability is confirmed, but operating readiness and Plan B are not.** Every VILS lab has the same device classes: Cricut, 3D printers, iPads, Snap Circuits, micro:bits, RVRs, and a Glowforge or xTool laser cutter. The curriculum still lacks per-room counts, condition, charging, consumables, setup, and reduced-device routes. The Glowforge cut-queue arithmetic also needs correction. Free fallbacks exist for Sphero and micro:bit and are not consistently named.
5. **Localized salary source — RESOLVED 2026-08-06.** Xello is the district source for localized salary information, with BLS or CareerOneStop as the independent check. H&L salary data is supplemental and must not remain load-bearing unless verified in the live account. The affected 4SW-5SW lesson references still need a reconciliation pass.
6. **The site has no teacher onboarding.** No start-here page, no 2026-27 pacing calendar (nothing binds week numbers to dates), no platform setup path (H&L rostering, Xello licensing, eDynamic enrollment, Code.org sections, Canva/TinkerCAD classrooms — including TinkerCAD's under-13 account gate), no syllabus, no parent letter (load-bearing: Rung 4 requires a home interview), no substitute plans, no print manifest, no materials order list.
7. **4SW Wk2 cannot produce the year's d(8)(C) artifact by any route.** The H&L District Course Planner is `[VERIFY]`-gated and the paper fallback cites an "Irving ISD CTE poster" with course sequences that exists nowhere — `PATHWAYS.md` holds pathway names only, no courses. The bilingual Family Career Plan Letter the same week `[VERIFY]`-flags does not exist either.

---

## 3. Workstreams

Every task is tagged for the Canvas end-state: **[TG]** = lands in the future per-lesson Teacher Guide · **[SA]** = student-facing Activity module material (follows ESL 6th-7th rules) · **[SITE]** = site/infrastructure.

### Workstream A — STRUCTURE: make what exists reachable (one decision, many fixes)

- **A1 [SITE]** Put the 17 Climber decks, 8 H&L teacher PDFs, and the required Grade 8 Xello documents in authenticated Canvas modules. Upload the files to Canvas and embed them at the point of use; do not publish licensed binaries on the public site.
- **A2 [SITE]** Build a teacher-materials index and Canvas asset manifest that states which weeks require each deck and resource, the Canvas Files location, the intended audience, and the module page where it is embedded. The public site may list the dependency without exposing the licensed file.
- **A3 [SITE]** Put `PLATFORMS.md`, `PATHWAYS.md`, and the eDynamic unit map on the site (move/mirror into `docs/resources/`). PATHWAYS fixes eight days' "CTE Pathways poster" dependency in 4SW-5SW alone.
- **A4 [SITE]** One-line fix: put `pawsandclaws.hatsandladders.com` on 1SW Wk3 D2 (currently locked inside a gitignored deck; the whole day hangs on it). Verified 2026-08-05: the site is live, H&L-hosted ("Paws & Claws Pet Supply"), district-agnostic — not a Bowie or Irving asset; same URL for every campus.
- **A5 [SITE]** Reconcile the diverged duplicates: `free-resource-directory.md` and `teks-coverage-matrix.md` each exist in two drifted copies (docs/ vs cce-curriculum/). Site copy wins.
- **A6 [SITE]** Correct `resources-status.md`'s five "already in the repo" claims and the capstone-rubric contradiction (overview says "do not print a second rubric"; status page lists one as needed — the right answer is a teacher tally sheet, workstream C).
- **A7 [TG + SA] Dual lesson package standard:** every Canvas lesson needs two coordinated surfaces, not one pasted lesson plan. The **Teacher Facilitator Guide** carries before-class prep, materials, timing, exact platform paths, facilitation moves, evidence to collect, grading, supports, and the outage/absence fallback. The **Student Guide** carries a short purpose statement, what students need, numbered steps in 6th-7th-grade ESL-accessible language, cropped workbook or platform visuals, what to submit, a visible "done" check, and an independent catch-up route for an absent student.
- **A8 [SA] Canvas visual pattern and Week 0 pilot:** use the attached 2027 VILS IMSCC as a visual reference for strong headers, short callouts, embedded images, and step-by-step lesson flow. Do **not** copy its old `enhanceable_content tabs` implementation as the course standard: 37 of its 70 HTML pages use that pattern, but [current Canvas community guidance](https://community.canvaslms.com/t5/Canvas-Developers-Group/HTML-to-Create-Tabs-That-Work-for-Keyboard-Navigation/m-p/618344) identifies it as unsupported, inaccessible by keyboard, and unreliable in the mobile apps. Build the reusable pattern with plain headings, responsive single-column blocks, and native `<details><summary>` disclosures for optional help, examples, vocabulary, and extensions. Essential directions and submission requirements remain visible without opening a disclosure.
- **A9 [SA + SITE] Screenshot and image workflow:** for each student guide, identify the exact workbook excerpt or approved platform screen that removes ambiguity; crop to the relevant step; upload it to the authenticated Canvas course; add useful alt text; record source, license, capture date, and the lesson that consumes it; and recheck platform screenshots when the interface changes. Never publish licensed workbook or Xello imagery on the public MkDocs site.
- **A10 [TG + SA] Pilot and acceptance gate:** revise the unpublished 1SW Wk0 Canvas module first. Split each day into a teacher-facing guide and a student-facing Start Here page, add the Wk0 workbook/worksheet visuals, then test the complete flow as a student on desktop, mobile-width, keyboard-only, and an absence/catch-up scenario. Use the approved Wk0 package as the template for the remaining 35 weeks.

### Workstream B — BUILD: printables (the factory run)

- **B1 [SA] THE KEYSTONE: the CCE career research worksheet** + its four layout variants (2-career, career-ladder, comparison, emerging-career) + worked-example and bilingual versions. Clears ~a third of all printable references. Build from the corrected six-field spec; fix the Wk0 Day 5 prose in the same pass (workstream E).
- **B2 [SA] Universal templates** (build once, reuse all year): Active-Monitoring clipboard roster grid (closes the "clipboard already built" pattern in ~6 weeks), presentation listening grid (5+ days), notes-sheet/reference grid, peer feedback slip (Two Stars and a Wish).
- **B3 [SA] Wk0 foundation set** (school starts here): Lab Safety Contract (+Spanish), My Career Journey handout (+stem +bilingual variants; reused at mid-year and capstone), Building Blocks word bank, career-hunt scaffold.
- **B4 [SA] 6SW Wk5 seven-artifact interview packet** (cover letter template, job application form, references guide, interview readiness guide, question set, two-sided question cards with answer frameworks + Spanish backs, thank-you letter form). The week's own overview: the printed templates "are the source, not the book." Two of seven are nearly written already (worked cover letter, eight questions with tips).
- **B5 [SA] Capstone spine printables:** Rung 4 Strengths Interview take-home packet + adult-facing cover note (the book can't go home with a class set; Wk6 checks notes "on page 288"); the 8-section written Career Plan template (goes home to the 9th-grade counselor — highest value-per-hour printable in 6SW); End-of-Year Reflection handout; peer feedback slips + running-order sheet.
- **B6 [SA] Per-week worksheet packs, in calendar order** — the remaining ~100 base sheets, all fully specced in their day pages (each detail file lists them with field-level specs). Includes the one genuine content-authoring job: 2SW Wk4 D4's ICD-10 sheet, 8 patient charts, and answer key (hours of authoring, not layout).
- **B7 [SITE] Variant policy — RESOLVED 2026-08-06:** build evidence-based supports matched to the task, not automatic full translations. Prefer visuals, bilingual labels or glossaries, chunked directions, sentence frames, word banks, modeled examples, and structured peer support. Use full translations for safety, family communication, consent/legal needs, or a documented requirement.
- **B8 [SITE] Pipeline extension:** add a worksheet input contract (new marker or source dir) + multi-page pagination to `build/build_pdfs.py`. The renderer, branding, and CSS need nothing. Read `exit-ticket-pdf-pipeline.md` first; PDF regen is not byte-idempotent.
- **B9 [TG] Missing projected assets (12):** Texas hazard map, IISD college-credit slide, SFX texture photos ×4, Foundation HS Program one-pager, airport aerials ×3, conservation drone image, bridge-type comparison, teacher presentation models. Small sourcing/typesetting jobs, one list.

### Workstream C — BUILD: assessment instruments

- **C1 [TG]** **Mock Interview Rubric** and **Career Presentation Rubric** first — the two highest-stakes performance instruments in the course (d(6)(C), d(4)(C)), both bare mentions today. Clone the 4-level pattern from `docs/1sw/cfa.md` (the one complete instrument in the repo).
- **C2 [TG]** **FYF 32-point tally sheet** for capstone scoring (instrument exists in every student's book; the teacher recording sheet does not — 8 categories × 25 students can't be scored live off a presenting student's book).
- **C3 [TG]** Weekly summative rubric library, in calendar order. Shortcut: the three unused H&L rubrics (Project Assessment 100pt, Student/Teacher Assessment 100pt, Daily Participation) cover the portfolio-style summatives with light adaptation — ratify and adapt rather than author ~36 from scratch. The two in-repo exemplars to copy: 3SW Wk1 D3's "What the Evidence Should Show" key and 3SW Wk6's "Abandon It earns full credit" rule.
- **C4 [TG]** Answer keys for the objectively-checkable activities: Spot the Problem decoys, Smile Squad cavity risk, Ultrasound Detectives, Flight Line Fixers, truck diagnoses, HVAC tickets #2-4, sling/splint procedure, TDLR route values, Safe or Spoofed. The supplied Climber Notes and speaker notes are the full available set. Check those files, then author and verify any missing key.
- **C5 [TG]** Gradebook scheme: **framework resolved 2026-08-06** at 40% minor and 60% major, with at least 3 minor and 2 major grades per six weeks. Performance bands are Needs Improvement 60-69, Approaches 70-79, Meets 80-89, and Masters 90-100. Next build the block-by-block assessment map and confirm semester-exam policy.
- **C6 [SITE]** Fix stale RIASEC ×3 in `cfa-template.md`. CFAs 2-6 stay deliberately deferred per the template's own administer-first rule — but resolve the performance-CFA design question (resources-status line 157) before 6SW's is needed.

### Workstream D — BUILD: onboarding + logistics

- **D1 [SITE]** "Start Here" page: get access → order supplies → print the packet → read the prototype week. Replaces the status dashboard as a new teacher's first landing.
- **D2 [SITE]** 2026-27 pacing calendar: week numbers → real dates, six-weeks boundaries, holidays, testing windows. **Needs the district calendar from Elisha.** Second most time-sensitive artifact after the supply order.
- **D3 [SITE]** Platform setup guide: H&L class creation/rostering/SSO + teacher account, Xello Grade 8 completion/reporting workflow, eDynamic enrollment, Code.org sections, Canva for Education, TinkerCAD Classroom (under-13 flow), NGPF/EverFi, and escalation contacts. The authenticated Xello task inventory is complete; other district-specific provisioning details still need named blanks.
- **D4 [TG]** Consolidated materials order list, quantified per section, with lead times: the crosscut master table + per-week supply rows are the raw input (sticky notes ~21 workbook pages, chart paper ~12, engineering notebooks, first-aid sets ×15, SFX kit + ~150 silicone skins with allergy-screen-first sequencing, 400+ straws/section, calculators ×30, headphones ×30, stopwatches, sticker dots, Glowforge stock, batteries).
- **D5 [TG]** Per-six-weeks print manifest (what to print, how many, when) + combined per-week PDFs so 178+ individual links become one copy-room job.
- **D6 [SA]** Syllabus + bilingual parent/guardian letter (the letter also pre-seeds Rung 4's home interview and the practice-application privacy note).
- **D7 [TG]** Substitute guidance: one generic workbook-only sub day + per-week "safe to sub" flags.
- **D8 [TG]** Weekly "Before Monday" prep lists — the audit's per-week roll-ups are the first draft; publish one per week, modeled on 6SW Wk6's existing Pre-Capstone checklist (the only one that exists).

### Workstream E — REVISE: in-page fixes (~35 items, all located)

- **E1** Hardware fallbacks, one sentence each: SpheroEDU simulator (1SW Wk1), MakeCode simulator (1SW Wk4, 2SW Wk3), named drone-sim app (4SW Wk4), Glowforge fallback + **re-plan the cut queue whose math doesn't close** (1SW Wk5).
- **E2** Propagate the platform-fallback pattern the repo already does well (3SW Wk3's Climate Kids/eDynamic blocks, 6SW Wk6's export contingency) to the ~20 platform blocks that have none — most urgently 6SW Wk2 D2 (Xello Resume Builder, 28 min, named paper fallback doesn't exist → B-workstream builds it), 2SW Wk4 D3, 4SW Wk1 D3.
- **E3** Broken logic: 5SW Wk3 D5 jigsaw presentations never assigned by any earlier day; 4SW Wk3 D4's "bilingual ATC command card from Day 1" that Day 1 never issued; 5SW Wk6 Day-3-optional/Day-4-required news-article contradiction.
- **E4** Timing: 5 period overruns (53-55 min), 2 internal contradictions — all line-cited in the detail files.
- **E5** Accuracy/safety: Wk0 D5 field-set claim (with B1); 1SW Wk1 heading misconception + "turn 90°" wording; 2SW Wk3 D4 activity-restriction note (asthma/cardiac/opt-out role); 2SW Wk2 latex note; mark unbuilt artifacts inline until built ("author before class" vs. implying a shelf copy).

### Workstream F — AUDIT/VERIFY: questions only Elisha or the district can answer

- **F1** **Localized salary source — RESOLVED:** use Xello, with BLS or CareerOneStop as the independent check. H&L is optional unless live verification supports it.
- **F2** VILS hardware baseline — PARTIALLY RESOLVED: all labs have Cricut, 3D printers, iPads, Snap Circuits, micro:bits, RVRs, and a Glowforge or xTool laser cutter. Still record quantities, working condition, consumables, charging, venting, device policy, and fallbacks per module.
- **F3** Obtain real Irving ISD CTE course sequences (counselor/coordinator) — unblocks 4SW Wk2's d(8)(C) artifact by either route.
- **F4** Deck evidence boundary — RESOLVED: the supplied Climber Notes and speaker notes are the full set. If a key is absent, author and verify it. "Capturing the Feeling" and the Safe or Spoofed answer set still need content review.
- **F5** The standing coordinator list (~10 `[VERIFY with CTE coordinator]` flags) + remaining district policy: semester exam requirement, scores below 60, and photo/media release process. Gradebook weights are resolved. Canva and Adobe Express generative tools are approved.
- **F6** Platform provisioning reality: Xello Grade 8 student-launch and reporting workflow, eDynamic seats, H&L Coach Dashboard access, Canva for Education verification, Code.org, and the TinkerCAD under-13 path. Xello educator access and the live completion configuration were verified 2026-08-06.
- **F7** **Campus-specificity sweep (Elisha directive 2026-08-05):** the course serves ALL Irving ISD middle schools, not just Bowie. Sweep docs/ for prose that assumes one campus or feeder pattern (e.g., 3SW Wk1's "Nimitz HS course catalog" extension, single-campus pathway framings) and make it feeder-neutral or all-campus, matching how the FYF district pages list programs by campus. Vendor-hosted assets (H&L practice sites, decks) are district-agnostic and fine.

---

## 4. Suggested waves (school starts mid-August; stay ahead of the calendar)

- **Wave 0 — this week (unblock Wk0-Wk1):** A1-A4 · A7-A10 Week 0 Canvas pilot · B1 (keystone worksheet) · B3 (Wk0 set) · E1 (Sphero fallback) + F2 Sphero count · D2 calendar + D4 order list drafted (procurement lead time) · F1.
- **Wave 1 — before school starts:** apply the approved A7-A10 package to the rest of 1SW · B8 pipeline extension → B6 packs for 1SW · B2 universals · D1/D3/D5/D6 · E-pass on 1SW · C-instruments for 1SW summatives + the CFA-adjacent C6.
- **Wave 2 — first weeks of school (before 2SW):** B6/C3 for 2SW-3SW in calendar order · B4/B5 can wait but are cheap to do early · D7/D8 rolling · F3-F6 as answers arrive.
- **Ongoing:** each six-weeks' packs + rubrics land at least two weeks before the block starts; resources-status.md updated as items ship (A6/S-sync).

**Decisions still needed from Elisha or the district before the full launch:** district calendar (D2) · semester-exam and below-60 policy (C5/F5) · course sequences (F3) · platform-specific provisioning that cannot be seen without the authenticated educator account. Variant policy, licensed-material hosting, grading weights, AI tools, and the hardware baseline were resolved 2026-08-06.
