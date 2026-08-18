# Week 0 Live-Pacing Sync — Redo Plan (2026-08-18)

> **For agentic workers:** execute task-by-task with `superpowers:executing-plans`. Steps use checkbox syntax. Owner approved the design on 2026-08-18 (see "Owner decisions"). Branch: `claude/cce-week-sync-98c340` (contains the two `codex/week0-live-pacing-sync` commits; PR #12 is superseded, do not merge it).

**Goal:** Rebuild the five Week 0 daily projection decks as clean student-facing masters, generate Ms. Lucero's editable 75-slide weekly deck from them, un-leak her Monday pacing from the shared canonical lessons/templates, and re-synchronize Canvas, Drive, and the public mirror with a single consolidated gate and a durable retrospective.

**Architecture:** The five daily builders under `build/decks/1sw-wk0-*/build.mjs` (Codex `@oai/artifact-tool` runtime, run from plain `node`) remain the authoritative slide sources; each is edited so its slide text passes a shared language-scoping lint (`build/decks/lib/slide_lint.mjs`). A new weekly builder merges the five daily `.pptx` outputs at the object level (proto merge, no rasterization) so every slide stays editable. Canonical `docs/` and Canvas templates carry only universal fixes; teacher-specific pacing lives in the weekly deck's speaker notes and the facilitator guide.

**Tech stack / runtime:** `node` 25 + Codex presentations runtime (`CODEX_PRESENTATIONS_RUNTIME_HELPER`, `RUNTIME_NODE_MODULES`, see "Runtime env" below); `uv run --with pillow` for contact sheets; `uv run --with httpx` for Canvas importers (token on stdin); Claude Drive connector for metadata; Claude-in-Chrome for Drive "Manage versions" uploads; `public-site/build_site.py` + `verify_site.py` for the mirror.

---

## Owner decisions (2026-08-18, chat)

1. Shared masters (canonical `docs/`, daily decks, Canvas templates) take **universal, quality-driven** changes only. Ms. Lucero's pacing (Monday ended after the first goal sentence; Tuesday resumes that page) belongs in **her weekly deck / notes**, not in the shared Day 1-2 contract.
2. Three language tiers, enforced: **projected slides** = student-facing, assume the teacher's chosen route (OneNote for Lucero), no route menus/fallbacks/minute ranges/gradebook admin; **Student Guide** = student actions + support, platform-down route only in the expandable absence section; **Facilitator Guide + speaker notes** = routes, fallbacks, pivots, timing, differentiation.
3. Weekly deck must be **editable at the object level** and **generated from the daily masters**. No invented Tue-Fri pacing (H&L was down 2026-08-18; owner's live sequence unknown). Owner edits by hand or supplies her sequence later.
4. Day 1-3: full slide pass. Day 4-5: language-scoping + screenshot-rule pass only.
5. Canvas: owner supplied a token in chat for this session; pass it on stdin via a shell variable, never echo/write/commit it. Owner regenerates afterward.
6. Drive: the Claude Drive connector cannot replace file content in place (`update_file` = title/parent only). Use Drive web "Manage versions → Upload new version" (keeps IDs) through Claude-in-Chrome; fallback = create-and-relink or a 2-minute owner checklist. Never create a second weekly deck.

## Runtime env (every deck build command)

```bash
export CODEX_PRESENTATIONS_RUNTIME_HELPER=/Users/elishalucero/.codex/plugins/cache/openai-primary-runtime/presentations/26.813.12317/skills/presentations/container_tools/runtime_helpers.mjs
export RUNTIME_NODE_MODULES=/Users/elishalucero/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules
```

The worktree symlinks `tmp/`, `cce-curriculum/resources/owner-authenticated-source`, `canvas-licensed`, and `avid-reference/source` to the main workspace (local `.git/info/exclude`). Daily builders read their starter decks from `tmp/<day>-source-clone/template-starter.pptx` (AVID teacher-deck clones, gitignored) and write to `cce-curriculum/resources/avid-reference/source/derived/cce-week1-dayN-source-grounded.pptx`.

## File map

| File | Responsibility |
|---|---|
| `build/decks/lib/slide_lint.mjs` (new) | Exported `lintSlideText(records)`; banned-phrase list for projected slides; used by all daily builders and the weekly builder |
| `build/decks/1sw-wk0-launch-source-grounded/build.mjs` | Day 1 daily master (15 slides) |
| `build/decks/1sw-wk0-day2-source-grounded/build.mjs` | Day 2 daily master (16 slides) |
| `build/decks/1sw-wk0-day3-source-grounded/build.mjs` | Day 3 daily master (16 slides) |
| `build/decks/1sw-wk0-day4-source-grounded/build.mjs` | Day 4 daily master (13 slides) — language pass |
| `build/decks/1sw-wk0-day5-source-grounded/build.mjs` | Day 5 daily master (15 slides) — language pass |
| `build/decks/1sw-wk0-weekly-source-grounded/build.mjs` | Rewrite: proto merge of the five daily outputs → editable 75-slide weekly deck + notes + provenance |
| `build/decks/qa_week0_decks.mjs` (new) | Consolidated gate: slide counts, 16:9, editability, lint, notes schema, Mr. Lucero = 0, contact sheets |
| `docs/1sw/wk0-classroom-routines/day1.md`, `day2.md`, `overview.md` | Restore general Day 1-2 sequence; keep universal fixes |
| `build/canvas/templates/wk0-day1-*.html`, `wk0-day2-*.html` | Same un-leak; facilitator guides carry the recovery block as an option |
| `build/canvas/reconcile_wk0_day2_day3.py` | Reuse for Day 1-3 page/file overwrite; add live-body diff guard |
| `cce-curriculum/notes/week0-live-launch-lessons-learned.md` | Rewrite retrospective (12 required topics) |
| `cce-curriculum/notes/canvas-lesson-production-workflow.md`, `cce-owner-expectations-and-decisions-log.md` | Enforceable checks (language tiers, screenshot rule, daily-before-weekly, hash checks, Student View, rights boundary, no parity claim until 3/3) |
| Manifests: `google-workspace-parity-manifest.json`, `google-workspace-distribution-inventory.json`, `avid-source-and-provenance-ledger.md`, `cce-launch-working-buffer.md`, `canvas-build-log.md` | Current IDs, hashes, sizes, revisions |

---

## Task 1: Slide-language lint (shared)

**Files:** Create `build/decks/lib/slide_lint.mjs`

- [ ] Write the module:

```js
// build/decks/lib/slide_lint.mjs
// Language-tier lint for PROJECTED slide text. Facilitator language belongs in
// speaker notes and the Teacher Facilitator Guide, never on the slide canvas.
export const BANNED_SLIDE_PATTERNS = [
  [/canvas or paper/i, "route menu on a projected slide"],
  [/\broute\b/i, "route language belongs in notes/facilitator guide"],
  [/fallback/i, "fallback language belongs in notes/facilitator guide"],
  [/\bminutes?\s+\d+\s*[–-]\s*\d+/i, "minute ranges belong in notes"],
  [/\bminor\b|\bmajor\b/i, "gradebook admin belongs in the facilitator guide"],
  [/mr\.?\s*lucero|mister lucero/i, "wrong honorific"],
  [/classlink/i, "obsolete sign-in route"],
  [/\b(reopen|refresh)\b.*\b(page|onenote|notebook)/i, "obsolete autosave test"],
  [/do not transfer|unsourced web search/i, "teacher policy language on a slide"],
  [/digital and physical routes/i, "route language on a slide"],
];
export function lintSlideText(records, { allow = [] } = {}) {
  const failures = [];
  for (const r of records) {
    if (!["textbox", "shape", "table"].includes(r.kind)) continue;
    const text = String(r.text ?? "");
    if (!text.trim()) continue;
    for (const [pattern, reason] of BANNED_SLIDE_PATTERNS) {
      if (pattern.test(text) && !allow.some((a) => a.test(text))) {
        failures.push({ slide: r.slide, id: r.id, reason, sample: text.slice(0, 120) });
      }
    }
  }
  return failures;
}
```

- [ ] Smoke test from the scratchpad: import the module, feed `[{kind:"textbox",slide:2,id:"x",text:"Canvas or paper today? Use that route instead."}]`, expect 2 failures; feed `"DONE WHEN: your page is open"`, expect 0.
- [ ] Commit: `git add build/decks/lib/slide_lint.mjs && git commit -m "Add projected-slide language lint for Week 0 deck builders"`

## Task 2: Un-leak Lucero pacing from canonical Day 1-2 + templates

**Files:** `docs/1sw/wk0-classroom-routines/day1.md`, `day2.md`, `overview.md`; `build/canvas/templates/wk0-day1-teacher.html`, `wk0-day1-student.html`, `wk0-day2-teacher.html`, `wk0-day2-student.html`

- [ ] `git diff 9f187749 HEAD -- docs/1sw/wk0-classroom-routines/ build/canvas/templates/wk0-day1-*.html build/canvas/templates/wk0-day2-*.html` and classify every hunk: **KEEP** (universal: reopen test removed, Google sign-in, distribute/editability preflight, screenshot explanations, six-type intro, tool ownership) vs **REVERT** (Lucero pacing: "finish only the first sentence", "Tuesday resumes this page", 0-8 min goal-recovery block replacing the general Day 2 opener, "Tomorrow, we will finish the goal plan first").
- [ ] Apply: general Day 2 opener restored (Do Now + objective + agenda), goal-recovery block moved to the **teacher** template/day2 facilitator prose as an *optional* "if students did not finish Monday's goal page" move (≤ 5 lines), not on the student page.
- [ ] Run: `uv run --with beautifulsoup4 --with textstat python build/canvas/qa_templates.py 'wk0-*.html'` and `python3 build/canvas/qa_lesson_contracts.py`; expected: PASS.
- [ ] Commit: `git commit -am "Restore the shared Day 1-2 lesson sequence; keep universal Week 0 fixes"`

## Task 3: Day 3 daily master (tomorrow's lesson first)

**Files:** `build/decks/1sw-wk0-day3-source-grounded/build.mjs`

- [ ] Read `docs/1sw/wk0-classroom-routines/day3.md` (canonical timing/contract) and the current builder end-to-end.
- [ ] Apply the shared skeleton: divider → **As You Enter** (materials + Do Now with sentence stem) → **Today** ("I can…" + small TEKS chip + 4-step agenda) → steps, one action per slide, every screenshot with WHAT YOU SEE / DO THIS / DONE WHEN → **grouped recap** before independent work → talk slide only where day3.md has one → **DOL** with literal instructions → close/device return.
- [ ] Replace the flattened slide 10 (whole-slide PNG) with editable text + the FYF p.9 crop as an image element.
- [ ] Remove facilitator language from canvas text; move it to notes. Notes schema on every slide: `Time:`, `Teacher move:`, `Student action:`, `Look-for:`, `Pivot/trim:`, `Recovery/access:`, `[Sources]…[/Sources]`.
- [ ] Wire `lintSlideText` into the builder after the final inspect; throw on failures.
- [ ] Build: `node build/decks/1sw-wk0-day3-source-grounded/build.mjs`; render contact sheet (`uv run --with pillow python` over `tmp/cce-week1-day3-source-clone/final-preview/*.png`); inspect every slide image.
- [ ] Commit builder: `git commit -am "Rebuild Week 0 Day 3 deck as a student-facing master"`

## Task 4: Day 2 daily master

**Files:** `build/decks/1sw-wk0-day2-source-grounded/build.mjs`

- [ ] Same skeleton. Add Do Now + Today/agenda slides. Six core types: one slide with the official H&L six-type chart (`canvas-licensed/1sw/wk0/day2/six-core-personality-types.png`; verify it exists, else render from Climber Notes "Learning Your Core Personality Types" slides 2-5) plus a one-line plain definition; prediction slide only after it. Tool-ownership slide: H&L = the assessment and result; OneNote (`Core Personality – Day 2`, Ms. Lucero's private page) = your written interpretation; FYF p.21 only for the CCMR framing. Remove slides 3-5 goal-recovery from the master (their content moves to weekly-deck notes + facilitator guide). Remove "Canvas or paper today".
- [ ] Build, contact sheet, inspect, commit: `git commit -am "Rebuild Week 0 Day 2 deck as a student-facing master"`

## Task 5: Day 1 daily master

**Files:** `build/decks/1sw-wk0-launch-source-grounded/build.mjs`

- [ ] Restore the general Day 1: device routine, notebook setup, complete goal page (six fields) at the canonical pace; keep "no reopen test"; remove "Digital and physical routes count equally", "Tuesday continues on this same page", "Mark Your Stopping Point" as a shared step (a stopping-point check is fine as the DOL wording only if day1.md carries it — otherwise DOL = point to completed action + checkpoint fields).
- [ ] Build, contact sheet, inspect, commit.

## Task 6: Day 4 + Day 5 language pass

**Files:** `build/decks/1sw-wk0-day4-source-grounded/build.mjs`, `build/decks/1sw-wk0-day5-source-grounded/build.mjs`

- [ ] Dump slide text; for each lint hit rewrite the canvas text to student language and move the removed sentence into that slide's notes. Any screenshot slide missing WHAT YOU SEE / DO THIS / DONE WHEN gets the three labels.
- [ ] Build both, contact sheets, inspect, commit.

## Task 7: Editable weekly builder

**Files:** Rewrite `build/decks/1sw-wk0-weekly-source-grounded/build.mjs`

- [ ] Replace the PNG loop with the proto merge (validated 2026-08-18 in the scratchpad `merge-test.mjs`): load each daily `.pptx`, `toProto()`, for decks 2-5 walk all string values and prefix `/ppt/slideLayouts/`, `/ppt/slideMasters/`, `/ppt/media/` ids with `dK-` (binary-safe walker: skip `ArrayBuffer.isView`), dedupe fonts by name, concatenate `layouts`, `images`, `slides` (re-index), `Presentation.load(merged)`, `exportPptx`. Keep the notes normalization + notes-schema assertion + expected slide counts. Add `lintSlideText` over the merged inspect. Write provenance JSON + contact sheets to `tmp/cce-week1-weekly-source-grounded/`.
- [ ] Add a `LUCERO_NOTES_OVERLAY` map (weekly slide index → extra notes lines) holding the Monday stopping-point note and the "if students did not finish Monday's goal page, finish it before Jumpstart" recovery move on the Tuesday opener; nothing on the canvas.
- [ ] Build; assert 75 slides, all editable except none; render every slide; inspect day dividers and Mon/Tue/Wed transitions.
- [ ] Commit: `git commit -am "Generate the editable Lucero weekly deck from the five daily masters"`

## Task 8: Consolidated gate

**Files:** Create `build/decks/qa_week0_decks.mjs`

- [ ] Script: for the five daily decks + weekly: import, assert slide size 960×540 (16:9), expected counts (15/16/16/13/15/75), every slide has ≥1 textbox/shape (no whole-slide raster), lint = 0, notes schema present, `mr\.? lucero` = 0 across text+notes, `classlink` = 0; print SHA-256 + bytes per file as JSON for the manifests.
- [ ] Run; expected: `PASS` and a hash table. Save the hash JSON to `tmp/week0-deck-hashes.json`.
- [ ] Commit the QA script.

## Task 9: Canvas sync (token via stdin only)

- [ ] Read-only inventory first: `curl -s -H "Authorization: Bearer $T" .../pages/<url>` for the six Day 1-3 pages; save live bodies to `tmp/canvas-live-bodies/`; diff against rendered templates; if a live body has owner edits not in the template, STOP and report before overwriting.
- [ ] Preflight: `python3 build/canvas/import_remaining_unpublished.py --preflight` (compiles builders; no token).
- [ ] Run the scoped reconciler with the token piped from a shell variable: `T='…'; printf '%s\n' "$T" | uv run --with httpx python build/canvas/reconcile_wk0_day2_day3.py; unset T` — it overwrites Day 1-3 page bodies, re-uploads the three daily decks + route images with `on_duplicate=overwrite`, preserves publication states.
- [ ] Verify with `qa_canvas_module.py` (token on stdin) and a Student View check of every `<img>` on the Day 1-3 student pages (masquerade `as_user_id` or Student View API); record file IDs + page revisions.
- [ ] Update `cce-curriculum/notes/canvas-build-log.md`.

## Task 10: Drive sync (existing IDs, no duplicates)

- [ ] Resolve IDs from `google-workspace-parity-manifest.json` (Day 1-5 raw + native; weekly raw `1-UM-4aiY5S7O2QnTpnfXhnho1BO4IUVh`, weekly native `1SYEtPzUOhl67-fjwttCb7pAodx9BIAU8ZgLuMPgaV6o`).
- [ ] Raw PPTX in place: Claude-in-Chrome → Drive file → ⋮ → Manage versions → Upload new version (`file_upload`), for the five daily + weekly raw files. Confirm `get_file_metadata` shows a new `modifiedTime`/size.
- [ ] Native Slides in place: Slides UI → select all → delete → File → Import slides → the updated raw PPTX → all slides. If the UI route proves too fragile for 75 slides, create the converted native copy from the raw PPTX, trash the old native file, and update every link (public site day pages, Canvas pages, manifests) in the same commit — and say so in the report.
- [ ] Record revision/size/hash in the two manifests; run `python3 build/google_workspace/qa_parity_manifest.py` and `qa_drive_distribution.py`.

## Task 11: Public mirror + rights check

- [ ] `UV_CACHE_DIR=/tmp/cce-site-uv uv run --with markdown --with beautifulsoup4 python public-site/build_site.py` then `... verify_site.py`; expected PASS.
- [ ] `git ls-files | grep -i -E "hats-and-ladders|owner-authenticated|canvas-licensed|avid-reference/source|CleanShot"` → empty; grep the built site for the same → empty.

## Task 12: Retrospective + workflow checks

- [ ] Rewrite `cce-curriculum/notes/week0-live-launch-lessons-learned.md` covering the 12 required topics (pacing vs observed; reopen test unnecessary; screenshot-only slides; WYS/DT/DW; official evidence before authoring; adapt teacher material minimally; daily authoritative/weekly generated; 3-destination parity verification; private preservation vs public indexing; live feedback as change input; stale strings in builders; context-window discipline) plus the new lesson: language tiers.
- [ ] Add the enforceable checklist to `canvas-lesson-production-workflow.md` (new "Projected deck language tiers and gate" subsection) and the owner-expectations log.
- [ ] Update `avid-source-and-provenance-ledger.md`, `cce-launch-working-buffer.md`, `OWNER_AUTHENTICATED_SOURCE_INDEX.md` hashes.

## Task 13: Commit, push, PR, deploy check

- [ ] `git status` shows only intended tracked files (never the six pre-existing untracked files listed in the handoff, never symlinks/binaries).
- [ ] Commit in plain English; push `claude/cce-week-sync-98c340`; open PR against `main` superseding #12; wait for the Pages workflow; verify the deployed mirror shows the Day 1-3 changes; report links (Canvas pages, Drive files, commit/PR, site, retrospective).

## Definition of done (owner's list)

Canonical Day 1-3 reflect the shared sequence with universal fixes; five daily decks rebuilt and inspected; weekly deck editable, generated, inspected; Canvas pairs + files match and Student View loads images; Drive raw + native match; public mirror rebuilt; no licensed binaries/screenshots in Git or site; manifests current; gate passes; git diff clean; retrospective + workflow checks in; final report links everything. No "perfect parity" claim until Canvas, Drive, and the mirror all pass.
