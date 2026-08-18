# Week 0 Live Launch Lessons Learned

**Dates:** launch 2026-08-17; retrospective 2026-08-18
**Scope:** 1SW Wk0 (Ms. Lucero's CCE Week 1 onboarding sequence), the five daily projection decks, her generated weekly deck, the Day 1-3 Canvas pairs, Drive copies, and the public mirror
**Owner rulings recorded here:** 2026-08-17 (no student autosave test; Google sign-in; screenshot rule) and 2026-08-18 (shared masters vs. teacher pacing; three language tiers; editable weekly deck)

## The one-paragraph version

The launch materials were built quickly and reached three destinations, but two things went wrong that a rebuild had to undo. First, one teacher's Monday pacing was written into the shared Day 1-2 lessons, decks, and Canvas pages, and facilitator language ("Canvas or paper today? Use that route instead", "Minutes 25-40", "Minor 1, not a Major") landed on projected student slides. Second, the combined weekly deck was assembled by rasterizing every daily slide into a PNG, so the teacher could not edit her own slides. Both failures came from the same root cause: no explicit rule about which audience each artifact serves and no gate that checked it. The rules and gates below are now code (`build/decks/lib/slide_lint.mjs`, `build/decks/qa_week0_decks.mjs`) and workflow text (`canvas-lesson-production-workflow.md`), not memory.

## What actually happened in the room

The planned Monday (5 welcome, 8 tools, 12 notebook, 17 goal, 5 check, 3 close) met first-day reality: assigned-device check-out and return, first-use OneNote navigation, and the Do Now consumed the period. Students began the first goal sentence; most did not reach the plan fields. On Tuesday, Hats & Ladders was unavailable in class and the teacher pivoted. Neither fact changes the shared scope and sequence. Both belong in the teacher's weekly deck notes and facilitator guide as pacing evidence.

## Lessons and the rule each one produced

### 1. Planned pacing is a hypothesis; observed pacing is evidence, and it has one home

Record what students completed, the last reliable stopping point, and the first action for the next class. That record goes to the affected teacher's weekly deck (speaker notes) and to an optional teacher move in the facilitator guide. It does not rewrite the shared daily lesson, the daily deck, the Canvas pair, or the module order unless the owner rules the change course-wide.

**Rule:** shared masters take universal, quality-driven changes only. Teacher-specific pacing lives in that teacher's weekly deck notes and the facilitator guide's optional moves.

### 2. Three language tiers, enforced

- **Projected slides:** student-facing. Assume the teacher's chosen route (OneNote for Ms. Lucero). No route menus, fallbacks, minute ranges, gradebook admin, teacher pivots, or policy sentences.
- **Student Guide (Canvas):** student actions and support; the platform-down or absence route only inside the expandable absence section.
- **Facilitator Guide and speaker notes:** routes, fallbacks, pivots, timing, differentiation, grading language.

**Rule:** every deck builder runs `lintSlideText` over the final slide text and fails on facilitator language; the notes must carry the full schema (Time, Teacher move, Student action, Look-for, Pivot/trim, Recovery/access, Sources). The Day 2 slide "Canvas or paper today? Use that route instead." is the canonical example of what the lint now blocks.

### 3. The student OneNote reopen test did not teach the objective

Once students could open and type on the distributed page, closing or refreshing it spent class time without improving the goal evidence. A teacher preflight tests distribution and editability from a student test account. Students never prove autosave.

### 4. A large screenshot is not instruction

A slide with only a screenshot depends on teacher improvisation and fails absent students. Every screenshot slide states **WHAT YOU SEE**, **DO THIS**, **DONE WHEN**. Exact item counts appear only when the source or platform specifies them. Day 3 slide 10 had shipped as a single rasterized PNG; it is now editable text beside the workbook crop.

### 5. Official platform evidence and teacher exemplars come before slide authoring

Owner-authenticated H&L student screens established the current Google sign-in route, the Profile Climbs cards, question formats, and completion badges. Teacher reference decks (Jenna Hainlen's AVID Week 1.2 and 1.6; Jennifer Stanley's Week 0/1) showed end-to-end choreography and also carried obsolete ClassLink, paper-journal, and personal details that must not be copied. Inspect both kinds of evidence before storyboarding.

### 6. Adapt strong teacher-created material minimally

Keep the As You Enter setup, direct Do Now, literal route demonstration, honest-answer reminder, visible result-recording job, completion cue, early-finisher direction, and exit step. Drop ClassLink, personal names, paper-journal requirements, and unrelated counts. A new worksheet or framework is justified only when no assigned platform, workbook page, notebook page, Canvas interaction, or teacher-created source already does the evidence job.

### 7. Daily decks are authoritative; the weekly deck is generated, and it must stay editable

The five daily decks are the review units. The weekly deck is assembled from them in Monday-Friday order by an object-level merge (`build/decks/1sw-wk0-weekly-source-grounded/build.mjs`), never by inserting one image per slide. When a daily master changes: rebuild that daily deck, rerun the gate, then rebuild and hash the weekly deck. The weekly builder throws if any slide has no editable text shape.

### 8. Parity is a three-destination claim, verified, not narrated

"Perfect parity" means the same source hash is what Canvas serves, what the raw Drive PowerPoint and the native Slides deck contain, and what the public mirror links to. Each destination is checked separately: Canvas file ID and page bodies (with a live-body diff before overwriting, so owner edits are never clobbered), Drive revision/size, and the public mirror build plus rights grep. On 2026-08-18 the local decks were rebuilt and gated, the mirror was rebuilt and verified, and the manifests were updated with an explicit `sync_status` marking Canvas and Drive as stale until the owner-run sync completes. That is the honest state; it is not parity.

### 9. Private source preservation and public indexing are separate jobs

Owner-authenticated screenshots, H&L PDFs, teacher decks, and the weekly deck live only under gitignored `cce-curriculum/resources/owner-authenticated-source/` and `canvas-licensed/` and in authenticated Canvas. The tracked `OWNER_AUTHENTICATED_SOURCE_INDEX.md` records filename, source, capture date, purpose, and rights boundary. The public mirror's verifier and a `git ls-files` grep for those paths run in the gate.

### 10. Live classroom feedback is a formal change input

Record the date, observed completion state, affected daily contract, and next-day recovery action. Decide first whether the evidence is teacher-specific or course-wide. Route it per lesson 1.

### 11. Stale phrases hide in builders and hand-edited manifests

The reopen test survived in a builder after the lesson text changed; the "13hsWv5" Google copy link survived in a page; a hand-added manifest entry made three QA scripts fail the next time the generator ran. Fixes: builder-level lint for obsolete strings (ClassLink, reopen/refresh, Mr. Lucero), a read-only gate over the OUTPUT files, and generated inventories that model every artifact type explicitly (the weekly deck is now `teacher_private: true` and the generator includes it).

### 12. Context discipline: one inventory, one build, one gate, one handoff

Read the state once (git branches, builders, assets, manifests, live page metadata), write the plan to disk, build each artifact once, run one consolidated gate, and hand off with exact links and blockers. Do not rerun overlapping audits or re-inspect the same deck three times.

### 13. Credentials and permissions are part of the plan, not a surprise at the end

The Canvas token can only be used through stdin by an operator whose environment permits it; the Drive connector must be authorized to the account that owns the IISD-restricted files. Confirm both before promising a same-session sync. When they are unavailable, deliver everything local, record `sync_status` in the manifests, and hand the operator the exact commands.

## Enforceable checklist (also in `canvas-lesson-production-workflow.md`)

- [ ] Current app route verified from an owner-authenticated student view (screens dated in the source index)
- [ ] Every screenshot slide has WHAT YOU SEE / DO THIS / DONE WHEN
- [ ] Every slide has an explicit completion cue
- [ ] Projected slides pass `slide_lint` (no routes, fallbacks, minute ranges, gradebook admin, teacher moves)
- [ ] Speaker notes carry the full schema on every slide
- [ ] Live pacing recorded in the affected teacher's weekly notes and facilitator guide only
- [ ] Daily decks rebuilt and gated before the weekly deck is rebuilt
- [ ] Weekly deck editable on every slide (gate throws otherwise)
- [ ] `node build/decks/qa_week0_decks.mjs` PASS; hashes recorded in the parity manifest and inventory
- [ ] Canvas: live-body diff before overwrite; publication states unchanged; Student View loads every image
- [ ] Drive: raw PowerPoint replaced in place (same ID) and native Slides re-synchronized (same ID); revision recorded
- [ ] Public mirror built and verified; `git ls-files` and the built site contain no licensed paths
- [ ] Manifests carry `sync_status`; no parity claim until Canvas, Drive, and the mirror all pass

## Completion boundary for the 2026-08-18 revision

Claimed: shared Day 1-2 lessons and Canvas templates restored to the scope-and-sequence sequence with universal fixes kept; five daily decks rebuilt as student-facing editable masters; weekly deck generated and editable (75/75); consolidated gate PASS; public mirror rebuilt and verified; manifests, ledger, buffer, and source index updated with current hashes and sync status. Not claimed: Canvas file/page sync and Drive raw/native sync, which were blocked in the build session (Canvas token use denied by the operator's permission classifier; Drive connector not authorized to the IISD account). Those two steps and their verification are the open items.
