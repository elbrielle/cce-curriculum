# Overnight Autonomous Goal: Continue Refining the Grade 7 CCE Curriculum

> **Historical record — do not execute.** This August 13 run prompt is superseded by current `AGENTS.md`, `cce-owner-expectations-and-decisions-log.md`, and `canvas-lesson-production-workflow.md`. In particular, its referenced-file locking rule is obsolete: module publication is the student release gate, while every referenced file and ancestor folder must stay accessible. Current lesson sources later implemented the Evidence Log only as a bounded, student-owned, ungraded retrieval record; this old prompt is not the authority for that implementation.

Use this prompt as the governing goal for an autonomous overnight curriculum-development run in:

`/Users/elishalucero/Coding Projects/27 CCR Planning`

## Goal

Continue improving Irving ISD's Grade 7 Career and College Explorations (CCE/CCR) curriculum as a coherent, teacher-runnable, student-accessible 36-week course. Build on the current curriculum rather than redesigning it from scratch. Fold in the strongest relevant routines, activity structures, models, and assignments from Jenna Hainlen's teacher-created AVID materials when they close a verified CCE gap, while adapting them carefully for Grade 7, the CCE TEKS, the existing Find Your Future/Xello/course sequence, and the privacy and delivery constraints of this course.

Work autonomously through the night within the authority below. Make meaningful progress, verify it rigorously, and leave a durable evidence-backed handoff. Do not confuse activity volume with quality. The objective is a more complete and usable CCE course, not a larger one.

## Owner intent and quality philosophy

The owner wants the benefit of an experienced AVID teacher's handcrafted practice without gutting that work and replacing it with generic AI curriculum. Preserve useful human choices: classroom rhythm, concrete examples, productive repetition, conceptual tension, humor, natural teacher language, and routines that reduce preparation. Adapt only where the source is too old, too advanced, AVID-specific, unsafe, private, legally restricted, or misaligned to Grade 7 CCE.

Use AI to do the unglamorous integration work well: analyze alignment, reconcile sources, adapt reading level, supply missing access supports, repair collection routes, harden Canvas importers, render artifacts, and find defects. Do not use AI as an excuse to manufacture replacement worksheets, filler activities, generic reflection questions, decorative frameworks, or unnecessary slide decks.

The course should feel like an experienced teacher assembled and improved it over time—not like a model generated 180 isolated lessons.

## Required reorientation before substantive work

1. Read `AGENTS.md`, `CLAUDE.md`, and `PLANNING.md`.
2. Read `cce-curriculum/notes/canvas-lesson-production-workflow.md` completely.
3. Read the current AVID/CCE analysis:
   - `cce-curriculum/notes/avid-to-ccr-reconciliation.md`
   - `cce-curriculum/resources/avid-reference/README.md`
4. Inspect current `git status`, recent diffs, active agents/tasks, and live Canvas evidence before deciding what remains.
5. Treat current builders, canonical lesson files, rendered PDFs, assessment maps, and live unpublished Canvas state as evidence. Do not trust an old planning note over current source or live state.
6. Check whether a prior run left a secure terminal waiting for the Canvas token or a Canvas reconciliation already running. Never start a second overlapping Canvas write.

## Current handoff state as of August 13, 2026

The following preservation-first slices were implemented locally and passed author plus independent gates before Canvas staging:

- Wk0 recurring routines:
  - Plan → Do → Recover → Reflect
  - Capture → Label → Question → Use evidence notes
  - a fair Locate and Use check
  - a two-page `CCE Six-Weeks Evidence Log`
- 2SW Wk5 self-advocacy:
  - nine curated, Grade-7-safe scenarios adapted from Jenna's classroom structure
  - Notice / Need / Reason / Next step
  - explicit trusted-adult and emergency boundaries
  - no new graded artifact
- 4SW Wk2 postsecondary exploration:
  - preserved individual read, group compare/contrast, overlap marking, summarizing, station/question trail, and backup-plan structures
  - rebuilt with fixed, current, Grade-7-safe route evidence and private/seated parity
- 6SW Wk2 résumé work:
  - preserved a teacher-created weak-sample comparison
  - replaced adult identity/history with a fictional Grade 7 example
  - uses one Evidence Log entry as a source, not another submission
- 6SW Wk5 interview preparation:
  - uses Evidence Log evidence as a prompt, not a resubmission
  - includes a concrete Situation/Task → Action → Result/Reflection model
  - has explicit written plus oral/AAC evidence protocols for recorded, live, conference, and AAC routes

All local responsive renders, changed PDF pages, 180 lesson contracts, 30 assessment-map entries, 30 advisory rubrics, importer dependencies, compilation, source links, and diff checks passed at the initial freeze. The 2SW Wk5 Markdown-blank PDF defect was repaired and independently cleared.

Do not treat those earlier GOs as permanent after additional edits. A later read-only audit identified narrow follow-on work listed below. Any slice touched after its prior gate must be rerendered and independently regated before Canvas mutation.

The earlier untouched secure token prompt was canceled after later edits made its gate stale; terminal echo was restored, no Canvas write occurred, and no overlapping Canvas process remained. Reverify process and live state before reopening a secure prompt.

A later governance check found a pre-existing ignored `.secrets/canvas.env` inside the workspace. With owner approval, it was moved unopened to macOS Trash, where it remains recoverable until Trash is emptied. Do not restore, open, source, print, or use that file during this run.

## Latest audited follow-on work and no-change decisions

Complete these in order, but only after verifying that the current files have not already closed them.

### 1. Ratify Wk0's d(4)(A) evidence cleanly

The useful Jenna structure is one specific action plus when/checkpoint and a recovery move—not a weekly planner-compliance grade. Wk0's routine card already contains this structure, but a later audit found that the visible Day 1 Student Guide and authoritative TEKS records were not fully synchronized.

The intended narrow repair is:

- the student record explicitly captures the evidence job or goal, next action, when/checkpoint, and recovery strategy;
- the Teacher and Student Guides agree;
- the Wk0 scope-and-sequence row and TEKS coverage matrix name d(4)(A) only after the student evidence truly supports it;
- no additional planner sheet, binder grade, or separate submission is added.

The local source may already contain this repair. If so, do not rewrite it. Run contract/template/compile/diff QA, render the changed Day 1 Teacher and Student pages at desktop and mobile, inspect them, and obtain an independent narrow GO.

### 2. Make the Six-Weeks Evidence Log operational without turning it into compliance work

The log should receive one short 2–3 minute transfer from an artifact already open at each six-weeks close. Students copy short phrases; they do not do new analysis, reconstruct missing old work, submit the log, or upload old artifacts again.

Audited candidate moments:

- Entry 1: 1SW Wk5 Day 5, from the Career Journey Update during the existing packet check;
- Entry 2: 2SW Wk5 Day 5, from the Communication and Goal Synthesis during the existing submit/check;
- Entry 3: 3SW Wk6 Day 5, from the revised Budget/Scholarship Plan, replacing an optional closing prompt;
- Entry 4: 4SW Wk6 Day 4, from the Personal Evidence Audit already open;
- Entry 5: 5SW Wk6 Day 5, from the existing Six-Weeks Reflection;
- Entry 6: 6SW Wk1 Day 5, from the Education Career Evidence Portfolio so the source exists before the résumé and interview consumers.

Before implementing each moment, prove that the host lesson has a safe 2–3 minute replacement or trim. Update the coordinated Teacher and Student Guides, name paper/digital storage, and give a missing-log fallback that preserves the short evidence phrases without creating an Assignment. Do not change the assessment map. Independently gate each changed week before Canvas.

### 3. Repair career-research scaffold parity in place

The current canonical career-research worksheet requires salary evidence with a number or range, measure/type, geography, source, and data year. Several active scaffolds still teach only an unlabeled “Average Salary.” Bring the existing variants into exact evidence parity rather than creating a new worksheet:

- `build/worksheet_sources/career-research-worksheet-example.md`
- `build/worksheet_sources/career-research-worksheet-bilingual.md`
- `build/worksheet_sources/career-research-worksheet-example-welder.md`
- `build/worksheet_sources/wk2-career-research-web-developer.md`

Use dated, sourced model figures and state the important limitation. Strict-build and inspect every changed PDF page. Preserve the existing worksheet identities and links.

### 4. Add one positive accessible professional opening and close to 6SW Wk5

The current interview work appropriately rejects handshake, eye-contact, clothing, body-language, camera, and paid-work norms. The remaining narrow gap is a positive accessible model inside the existing rehearsal/checkoff:

- opening: greeting + first name or fictional identity + role/purpose + thanks;
- close: thanks + an appropriate next-step question or respectful close;
- speech, AAC, text-to-speech, interpreter, and private conference are equal routes.

Do not add a packet, grade, rubric criterion, public performance, adult-signature hunt, or employer contact. Rebuild only the existing interview-readiness/mock-interview artifacts and coordinated Canvas guides that need the model, then rerender and independently regate.

### 5. Repair planning-governance drift

`PLANNING.md` may still claim that d(7)(A) résumé coverage rests entirely on Xello. Current course truth is that the private Canvas/paper first-résumé evidence in 6SW Wk2 carries the TEKS; Xello copying is supplemental only. Correct the planning statement without changing the approved lesson or creating another résumé task.

### 6. Preserve these explicit no-change decisions

Do not import or reproduce the full AVID Skills Check, weekly binder/planner/grade checks, 21-slide Time Management lesson, full Cornell/FNT decks, paper-crane sequence, generic learning journal, NGPF Plan After High School packet, military eligibility self-screening packet, college-worth debate, Career Bingo, Career Cluster Poster, or Student Résumé Template.

Their useful instructional ideas are already represented more safely and efficiently in the current CCE routines. Wholesale reuse would add compliance grading, private disclosure, outdated/currentness risk, licensing uncertainty, duplicate work, or high-school/adult complexity without closing a verified Grade 7 CCE gap.

## Latest executed checkpoint — August 13, 2026

The audited follow-on work above is now implemented locally and frozen:

- Wk0 d(4)(A) is synchronized across the actual student evidence, Teacher/Student Guides, scope and sequence, and TEKS matrix.
- Six-Weeks Evidence Log Entries 1–6 are embedded as two-to-three-minute transfers from already-open artifacts; the log remains student-owned, unsubmitted, ungraded, and outside the assessment map.
- All four career-research support variants now match the main salary-evidence fields; the three worked examples use dated, correctly labeled May 2024 U.S. median annual-wage models, while the bilingual support remains an intentionally blank scaffold.
- 6SW Wk5 now includes one exact accessible professional opening and close inside the existing rehearsal/checkoff, with speech, AAC, text-to-speech, interpreter, private-conference, recorded, and teacher-checkoff collection routes aligned.
- `PLANNING.md`, the AVID/CCE reconciliation note, the private-source README, and temporary-output ignore rules now match current course and licensing truth.

Current independent verdicts:

- Wk0 plus Evidence Log Entries 1–6: strict GO after 36 responsive views and all three Wk0 routine PDF pages were inspected at original detail.
- Career-research scaffolds plus 6SW Wk5 interview access: strict GO after the two narrow cross-artifact wording defects were repaired, the four-page mock-interview record was rebuilt at zero warnings, and the current PDF plus Day 5 Teacher desktop/mobile views were independently rechecked.
- A coursewide source-link gate found one stale Irving ISD School Choice URL in 4SW Wk1. It was replaced with the current official Schools of Choice page, the source-link gate now reports zero confirmed stale links, and fresh Day 4 Teacher desktop/mobile views are clean. The 4SW Wk1 builder is included in the frozen Canvas reconciliation scope.
- Governance/licensing/documentation: curriculum findings GO. With owner approval, the pre-existing `.secrets/canvas.env` was moved unopened to macOS Trash and remains recoverable until Trash is emptied.
- Coursewide static checks pass: 180/180 Teacher and Student contracts, 30 mapped assessments, 30 advisory rubrics, 17 builders, 18 template pairs, 189 named dependencies, compilation, token guards, and `git diff --check`.
- The secure runner is pinned to an exact 75-file freeze, including the deep-QA verifier and image normalizer themselves; it stages and deep-checks 11 affected modules, runs the strict 36-module coursewide gate, and then produces 220 current live Teacher/Student desktop/mobile views for manifest checks and original-detail human inspection.

The first live reconciliation attempt passed the strict 36-module unpublished safety guard and completed the 30-assignment bootstrap, then stopped in Wk0 before page updates because the two new routine PDFs were absent from Canvas storage. The independently gated repair uploaded and locked those PDFs on the second attempt, which again passed the safety guard/bootstrap but stopped before page/item work when a legacy coursewide filename search found four copies of the common career-research sheet. The exact-folder repair passed storage on the third attempt and safely upserted the eight edited lesson pages/items as unpublished, then stopped during ordering because a stale legacy overview URL was not an actual module item. A fresh read-only Wk0 snapshot then proved that the approved module contract is 16 typed items, not ten total: five Day 1–5 SubHeaders, ten Teacher/Student Pages, and the mapped Day 4 Minor immediately after the Day 4 Student Guide. The fourth full-run attempt stopped at its first read-only coursewide safety pass, before the assessment bootstrap or any new write, because the eight safely unpublished Wk0 pages from the partial third run had not yet reached the later contract-normalization step. A separate echo-disabled read-only diagnostic confirmed the module debt is exactly 36 missing-contract-panel/label messages on those eight known Wk0 pages; the other 35 modules, orientation, and global checks pass. The fifth attempt also stopped at that first read-only pass because the assessment sub-audit identified the second expected consequence of the same interruption: the mapped Minor itself, its 18/12 group structure, all 30 rubrics, and all 30 assignment identities are correct, but the overwritten Day 4 Student Guide lacks its one mapped submission panel and assignment link because the run stopped before assessment reconciliation. The runner now permits either a completely clean 36/36 preflight or only that exact bounded recovery state: the 36 known Wk0 contract messages plus those two exact Wk0 assessment-panel messages, with every other module, orientation, grading, rubric, group, assignment identity, publication, ordering, and global check clean. Any extra problem still fails before mutation. Wk0 itself preflights exact dependencies before token input; verifies the unique unpublished module and exact unpublished/100-point/points-graded/Minor-40%/omit-false/rubric-marked Minor before any write; uploads only the approved support/visual allowlists; resolves support only inside the exact locked Wk0 folder; and reconciles the exact 16 typed identities, titles, numeric positions, and unpublished states while removing only true duplicates or stale module links. Re-freeze and independently gate this recovery allowance before restarting the full sequence; do not skip ahead from any partial run.

The sixth full run passed that bounded recovery guard, completed all 30 assessment bootstrap records, ran all 11 builders, reconciled all 30 mapped assessments and rubrics, normalized all 360 daily contracts and image-loading state, and passed deep QA for the first ten affected modules. It then stopped at the eleventh deep check, 6SW Wk5, because the verifier generically required Canvas `media_recording` on every Major even though this lesson's approved two-part protocol intentionally uses file upload for the written record plus private media together, or annotation/upload/text/paper for the written record paired with the named live/conference/AAC teacher checkoff. Adding standalone `media_recording` would weaken collection because Canvas submission types are alternatives and would permit media without the required written portfolio. The verifier is therefore part of the freeze and must require exact per-module route sets plus the explicit written-and-oral two-part language in both the mapped Assignment description and the one Student submission panel. Missing upload, missing checkoff language, missing written-plus-media language, extra standalone media, text-only, or an unrelated oral assignment must fail closed. Re-freeze and independently gate this verifier repair before restarting the complete runner; do not resume after the failed deep check.

The seventh full run passed a completely clean 36/36 live safety preflight, all 30 assessment bootstrap records, all 11 builders, all 30 assessment and rubric reconciliations, and the 360-page contract normalizer. It then stopped before deep QA when the coursewide image normalizer encountered a transient HTTPX failure whose empty exception string produced only `Image normalization failed:`. All eleven builders had already returned their exact unpublished module identities; no publication or grading change was reported. The image normalizer must remain idempotent and unpublished-only, but its Canvas requests now need a bounded retry for connection/read/write/protocol failures and HTTP 429/500/502/503/504 responses. Retry at most three times with a short bounded delay; repeat only identical GET requests or identical unpublished page-body PUTs; fail with the method and exception class after exhaustion; never retry non-transient 4xx responses. Include the normalizer in the freeze, prove these behaviors with no-network hostile fixtures, and independently gate the refreshed freeze before restarting the entire runner.

The eighth full run again passed a clean 36/36 safety preflight and all 30 assessment bootstrap records. Wk0 completed cleanly, then the 1SW Wk5 builder stopped on a transient Canvas `502 Bad Gateway` during its final fresh-read of the mapped Major. The builder had already performed its idempotent page/file/lock reconciliation but did not return a success payload, so the runner stopped before starting the remaining nine builders. A transient can occur in any child process, not only the image normalizer. The audited parent runner must therefore retry an entire token-fed child process at most three times only when its captured output contains one of the exact approved transient HTTP statuses or exception classes. All live child processes in this sequence are independently idempotent, unpublished-only builders/reconcilers/normalizers, read-only QA, or local responsive renders. A retry must pass the same token through hidden child stdin and repeat the exact script/arguments; redact the token before matching or reporting output; print only a redacted retry checkpoint. Allowed logical return codes remain final, and any curriculum, identity, publication, grading, lock, duplicate, route, rendering, or other non-transient failure must stop on the first attempt. Prove transient success-after-retry, exhausted retry, immediate logical failure, allowed recovery return, and token redaction with no-network fixtures; independently gate the runner before restarting the full sequence.

The ninth full run stopped at its first read-only live safety pass, before the assessment bootstrap or any new write, because the partial 1SW Wk5 builder from Attempt 8 had safely overwritten its ten unpublished lesson pages but had not reached the later coursewide contract and assessment normalizers. A hidden-input read-only 36-module diagnostic proved the exact combined debt: Wk0 retains its approved 36 contract-panel messages and two mapped submission-panel/link messages; 1SW Wk5 has exactly twenty contract messages (one missing canonical marker plus one still-present legacy panel on each of ten exact pages) and two mapped submission-panel/link messages. The other 34 modules, orientation, global checks, 18/12 assessment-group counts, all 30 mapped assignment identities, and all 30 rubrics pass. Extend the recovery assertion only to this exact 34/36 state: Wk0 ID 542880 with 16 items/10 pages/1 interaction and its exact 36-message set; 1SW Wk5 ID 542984 with 16 items/10 pages/1 interaction and its exact twenty-message set; assessment passed=false with exactly the four named Wk0/Wk5 panel/link messages and 18 Minor/12 Major/30 rubrics/30 assignment rows; all other modules passed with no problems; orientation and globals clean; top-level passed=false. Any missing, extra, duplicated, substituted, re-ordered-count, wrong-ID, wrong-item/page/interaction count, publication, other-module, assessment, orientation, or global problem must fail before mutation. Independently hostile-test and gate this bounded recovery before restarting the complete runner.

No token prompt or overlapping Canvas writer is currently open. The owner explicitly authorized reuse of the chat-provided token after accepting that it would appear again in an internal tool-input record. The audited reconciliation runner kept terminal echo disabled and did not place the token in the repository or a command-line argument. Earlier, an audit command mistakenly reused the credential as a search pattern; it returned no match and did not print the value, but the invocation was logged. Later, a standalone read-only Wk0 QA command was launched outside the audited runner and did not disable terminal echo, so the token appeared in captured tool output. Do not claim pristine token handling or no prior output exposure. Do not repeat the value again. The next run must use only the echo-disabled audited runner and redact the token from all child output.

## Source preservation and licensing rules

- Jenna's private source library is under `cce-curriculum/resources/avid-reference/source/` and must remain Git-ignored.
- Treat supplied AVID files as private reference material unless rights are clear. Do not publish them to the public site or Git.
- The purchased `Mock Job Interview Resources Career Readiness Partner Activity` by Stacey Wassif/TPT is a single-user commercial resource. Do not copy, rewrite, merge, upload, or distribute its protected content as CCE curriculum.
- Teacher-created Jenna materials may inform or be adapted into the authenticated curriculum when appropriate, but document the source and adaptation rationale. Remove real names, adult work histories, private disclosures, dated local announcements, and AVID-only compliance language.
- Licensed Find Your Future, Xello, H&L, and Climber Notes binaries/screenshots stay outside Git and the legacy public site. They may be uploaded only to authenticated Canvas. Under current policy, any file referenced by course content and every ancestor folder must remain accessible to enrolled students; module publication remains the release gate.
- Prefer current primary sources for factual claims: TEA/THECB, district pages, BLS, licensing agencies, official program/provider pages, and official platform documentation.
- Keep measures exact. Do not relabel national medians as local or starting pay; distinguish percent growth, numeric employment change, and annual openings; date current claims.

## Preservation-first decision test

Before changing or adding anything, answer these questions in writing or in the handoff evidence:

1. What exact Grade 7 CCE/TEKS or teacher-operability gap exists?
2. Does the current lesson already teach or collect this evidence adequately?
3. What useful human-authored structure from Jenna's materials addresses the gap?
4. Can it be adapted inside an existing lesson/artifact instead of creating another packet, assignment, quiz, or reflection?
5. What must change for Grade 7 reading load, privacy, accessibility, CCE framing, current facts, or a 50-minute period?
6. What must remain recognizable from the teacher-crafted source?
7. How will a teacher run it tomorrow without inventing examples, supplies, timing, or recovery procedures?

If the current lesson is already strong, preserve it. A documented decision not to change something is valid progress.

## High-value integration priorities

Continue only where current evidence supports the need. Likely high-value areas include:

### 1. Recurring organization and reflection routines

- Use the existing CCE Six-Weeks Evidence Log as the stable six-week spiral.
- One entry per six weeks is enough.
- The log records: Artifact or task; Transferable skill; Evidence: What did you do?; Revision or recovery move; Next step.
- It lives in the student's CCE binder or one teacher-designated digital folder.
- It is not a separate Canvas Assignment and is not submitted in Wk0.
- Later résumé, interview, portfolio, and capstone lessons may read it as a source but must not require students to re-upload old artifacts.

### 2. Planner, journal, binder, and notes practices

- These can fit CCE when they teach planning, locating evidence, using feedback, recovery, study habits, self-management, or transfer—not when they grade binder appearance or cross-class compliance.
- Prefer short recurring use checks over weekly paperwork quotas.
- A planner check should ask whether a student can identify the task, next action, deadline or checkpoint, needed resource, and recovery move.
- A binder/digital-folder check should assess whether the student can locate and use evidence, not decoration, tab count, or neatness.
- Focused notes should have a real purpose and a use step: Capture → Label → Question → Use. Do not impose a generic Cornell-notes packet on every lesson.
- Journal/reflection prompts must connect to actual CCE evidence, decision-making, revision, or next action. Avoid diary-style disclosure and generic “what did you learn?” filler.

### 3. Self-advocacy and transferable skills

- Build practice around realistic Grade 7 school, group, classroom, workplace-simulation, and project situations.
- Preserve privacy. Students may use fictional examples and should not disclose health, family, discipline, immigration, financial, or traumatic experiences.
- Harassment, threats, safety, medical, or emergency situations route to a trusted adult; they are not solved with a communication sentence stem.
- Use complete point-of-use language frames and models, then fade support when appropriate.

### 4. Postsecondary and career-route thinking

- Teach flexible investigation and next steps, not premature commitment to a college, military, credential, or career route.
- Do not ask middle-school students to self-screen for adult eligibility, disclose family finances, or make public preference statements.
- Preserve strong compare/contrast, station, overlap, summarizing, and evidence-backed decision structures.
- Maintain counselor verification windows and label provider/program facts by date.

### 5. Résumé, portfolio, interview, and employment readiness

- Use true school, project, activity, service, responsibility, or simulation evidence. Paid work is not required.
- Weak/strong comparisons should show what evidence is missing, not mock a student.
- Never reward invented roles, hours, awards, tools, results, dates, or experience.
- Reuse the Evidence Log to locate evidence; do not make students reconstruct or resubmit prior work.
- Oral/AAC evidence must have an exact collection protocol. Written-only work is not oral evidence.
- Recorded routes must define how written and media evidence arrive together. Live/conference/AAC routes need a named teacher checkoff with the same rubric evidence.
- No public résumé, public interview recording, real application, employer contact, or external personal-data entry is required.

## Lesson quality standard

Every changed lesson must remain a coordinated Canvas Teacher Facilitator Guide and Student Guide with one exact daily contract:

- Topic
- Objective
- TEKS
- Demonstration of Learning / Show Your Learning

The Teacher Guide must be executable the next day and include:

- exact per-student, per-pair, or per-team quantities;
- default device/print/workbook route and equal fallback route;
- grouping and individual-evidence expectations;
- supplied complete model and useful nonexample where needed;
- an exact 50-minute flow with realistic transitions;
- timed monitoring checkpoints with concrete look-fors;
- a misconception threshold and class pivot;
- a safe trim that protects the DOL and assessment criteria;
- collection, return, reset, and cleanup directions;
- absence, no-device, no-workbook, and incomplete-work recovery;
- privacy, safety, and platform boundaries.

The Student Guide must:

- use Grade 7 plain language without talking down to students;
- make the evidence job and submission home unmistakable;
- place word banks, complete sentence frames, models, and visual cues next to the task where students use them;
- provide English-learner and accessibility supports without creating a second easier curriculum;
- offer private, paper, digital, dictation/speech-to-text, and AAC routes where appropriate;
- clearly distinguish required evidence from optional extension;
- avoid redundant packets, duplicate submissions, and platform scavenger hunts.

## Assessment and artifact rules

- Respect the approved assessment map: three Minors and two Majors per six weeks where mapped. Do not invent an additional graded artifact.
- Canvas mapped assessments remain 100 gradebook points, points-graded, in the exact Minor 40% or Major 60% group, `omit_from_final_grade=false`, and unpublished.
- Student-facing rubrics retain their raw-point totals and exact raw-to-100 conversion note.
- Formative practices remain 0 points, grade-neutral/omitted, private, and unpublished.
- A quiz is justified only when immediate misconception feedback saves teacher time. Do not add a quiz merely to satisfy tooling.
- Keep one response home per evidence job. If paper is allowed, name collection and labeling. If text entry is allowed, provide exact labels. If media/AAC is required, define how the teacher records it.
- Prefer revising an existing worksheet in place over adding another packet. Preserve student response space proportional to the thinking requested.

## Canvas production rules

Canvas is the sole active production, review, and delivery environment. Git is source control and backup. MkDocs is a legacy archive; do not build, QA, or deploy it unless the owner explicitly asks.

Before any Canvas mutation:

1. Run local dependency and syntax preflight before requesting or reading the token.
2. Run assessment-map/rubric/template/contract/importer preflights.
3. Freeze the content slice and receive an independent read-only GO.
4. Resolve exact target module, page, Assignment, Quiz, and folder identities.
5. Fail closed on duplicate names or unsafe published/grading state.

Canvas token handling is non-negotiable:

- never place a token in chat, a command string, command-line argument, script, file, environment dump, Git, or output log;
- read it once through terminal standard input with echo disabled;
- retain it only in process memory for the approved run;
- unset it immediately after the run;
- never repeat a token that appeared in conversation.

Required live order for affected weeks:

1. assessment-map bootstrap;
2. scoped week builders;
3. assessment-map reconciliation;
4. rubric reconciliation;
5. lesson-contract normalization;
6. unpublished image-loading normalization;
7. deep affected-module QA;
8. 36-module coursewide unpublished QA;
9. current live responsive visual verification of changed pages.

All Canvas objects must remain unpublished during overnight work. **Superseded safety rule:** this historical prompt required referenced folders and files to remain locked; current policy instead requires every referenced file and ancestor folder to remain accessible while the module stays unpublished. Builders must be idempotent and fail closed on grading, publication, duplicate, clone, attachment, ordering, or storage violations.

Do not publish, conclude the course is launch-ready, or change due dates without explicit owner approval.

## PDF, responsive, and visual QA

For every changed worksheet source:

- strict-build the PDF;
- require zero warnings;
- confirm expected page count;
- render every page to PNG;
- inspect every page at original detail;
- verify no clipping, overlap, blank pages, swallowed Markdown blanks, broken frames, tiny unusable response cells, or disproportionate writing space;
- use render-safe bracket prompts instead of raw underscore blanks.

For every changed Canvas lesson pair:

- render Teacher and Student pages at desktop and mobile widths;
- wait for lazy images to load and stable page height;
- open image disclosures used by the lesson;
- fail on incomplete images or horizontal overflow;
- inspect complete page tails, not just contact sheets;
- verify the current builder output, including `.update(...)` mutations, rather than a stale preview fixture.

Optional teacher whole-group decks are projection aids, not student delivery. Build one only after source grounding and the Teacher/Student pair are stable and only when a real whole-group projection/modeling gap remains. Start with the strongest existing teacher deck if one exists. Preserve useful slides and teacher moves. Use course-specific visual language, not generic AI branding. The Canvas Student Guide remains the accessible and absence route.

## Autonomous working method

You are authorized to use parallel subagents for bounded independent slices when concurrency is available. Use one author/owner per slice and a different read-only agent for the final gate. Do not let multiple agents edit the same files concurrently.

Operate in this loop:

1. Pin the current source of truth and inspect existing work.
2. State the exact gap and preservation decision.
3. Implement the smallest coherent repair.
4. Compile and run scoped static QA.
5. Strict-build and inspect artifacts.
6. Render and inspect responsive Teacher/Student pages.
7. Freeze exact files and hashes/inventory.
8. Run an independent adversarial gate.
9. Repair confirmed blockers, rerender only what is genuinely stale, and regate.
10. Stage to Canvas only after GO, then run deep and coursewide live QA.

Keep commentary concise but do not go silent during long work. Give checkpoint updates with concrete findings, not percentages or vague “still working” messages.

Maintain a durable working buffer during the run. After each meaningful freeze, record:

- the last verified source state;
- the exact files changed;
- the exact render/PDF inventories inspected;
- the static and independent-gate results;
- whether Canvas was untouched, partially written with publication state preserved and referenced resources accessible, or fully reconciled and verified;
- the next safe action and any authority still needed.

Choose natural pause points: after a frozen local slice, after an independent verdict, or after live deep/coursewide QA—not halfway through a write or before recording evidence. If interrupted or compacted, recover from the current worktree, active process/session state, live Canvas reads, and the working buffer before repeating work or asking the owner to restate context.

If the Canvas token is unavailable, keep making safe local progress and leave a secure ready-to-run command sequence; do not weaken token handling or substitute the token into a tool argument. If a token prompt is waiting while later edits make a prior gate stale, cancel the untouched waiting session, revalidate the changed slices, and only then reopen the secure prompt. Never let a stale local gate race a Canvas write.

Make reasonable in-scope decisions autonomously. Do not stop for minor wording choices that can be resolved from the project rules. Stop and ask only when:

- the choice changes assessment identity, grading, TEKS, or required evidence;
- licensing or ownership is unclear and copying would be irreversible;
- a required district/platform source is unavailable and alternatives materially change the lesson;
- Canvas targets cannot be resolved uniquely;
- the token cannot be supplied through the secure terminal path;
- any object is unexpectedly published;
- a write would require deletion, broad movement, publication, or a new due date;
- unrelated user work blocks a safe edit.

## Worktree and Git boundaries

- Preserve unrelated modified and untracked files.
- Use `rg`/`rg --files` for discovery and `apply_patch` for source edits.
- Do not stage broadly.
- Do not commit, push, open a PR, delete, reset, or publish unless explicitly authorized.
- Keep licensed/private source binaries ignored.
- Record exact changed files in the final handoff.

## Overnight priorities after the current Canvas reconciliation

If the five current AVID/CCE slices stage and pass live QA, continue with a read-only gap audit before making more changes:

1. Map Jenna's remaining teacher-created materials to the 36-week CCE sequence and exact TEKS/evidence jobs.
2. Identify only gaps that are not already covered by FYF, Xello, current CCE companions, or the new recurring routines.
3. Rank candidates:
   - P0: collection/safety/assessment/importer defect;
   - P1: next-day teacher-operability or missing model/access route;
   - P2: optional enrichment or polish.
4. Implement P0s and well-supported P1s. Leave P2 ideas documented unless they materially improve instruction without increasing burden.
5. Favor spiraling a stable routine into an existing lesson over creating a standalone “study skills week.”
6. Do not add a weekly planner/binder grade by default. First prove the TEKS/evidence value and avoid grading privilege, supplies, neatness, or compliance.
7. Do not generate slide decks simply because none exist. Add or adapt a deck only when projection materially improves modeling, source chunking, orchestration, or discussion.

## Required final handoff

Leave one concise but evidence-rich report containing:

- outcome first: what is complete, what is on Canvas, and what remains;
- exact preserved Jenna structures and how they were adapted;
- exact files changed and new artifacts;
- source/licensing decisions and excluded materials;
- PDF inventory and pages personally inspected;
- responsive render inventory and views personally inspected;
- static QA commands and results;
- independent GO/NO-GO verdicts and repaired blockers;
- Canvas module/Assignment/Quiz/folder IDs for changed slices;
- proof that modules/pages/items/assessments preserve owner publication state and that referenced files/folders are accessible under the current resource-access policy;
- deep affected-module and 36-module coursewide QA results;
- any remaining P1/P2 ideas, clearly separated from blockers;
- confirmation that the secure run caused no additional token storage or exposure, disclosure of the pre-existing stored-file and chat/log conditions, and confirmation that no Git publish action occurred.

Do not report “done” merely because files were edited or a builder returned success. Done means the teacher can run the lesson, the student can complete and submit the evidence through an exact route, artifacts render correctly, Canvas is safe and unpublished, and independent verification found no release blocker.
