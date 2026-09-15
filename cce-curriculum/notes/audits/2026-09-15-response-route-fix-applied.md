# Response-route fix — applied 2026-09-15 (source course 98060)

Companion to `2026-09-14-response-route-and-grounding-audit.md`. Everything below was applied to the live course and to the repo working tree; QA (`build/canvas/qa_response_routes.py`) passed against the pre-fix dump: no HQIM on any student or teacher page, all 177 worksheet buttons open their own Doc, exactly one route panel per facilitator guide, and no module, item, or page changed publication state.

## What changed

| Layer | Change |
|---|---|
| Source text | HQIM removed from 87 curriculum files (docs, templates, builders, worksheet sources) and replaced with the specific thing: Hats & Ladders / H&L (7), "Hats & Ladders or Xello" / "the app" for the localized salary figure (91), "your *Find Your Future* workbook" (119). Student-surface jargon stripped (DOL, TEKS codes, "licensed"). ~65 workbook page citations added to student pages after verification against the FYF text. 1SW Wk2 Day 1 cites p. 38; Day 2 no longer does; Day 3 links bls.gov. |
| Google Docs | 166 worksheet Docs created (one per response-route worksheet, in each week's `Google Masters/`), rendered from `build/worksheet_sources/*.md` by `build/google_docs/render_worksheet_gdoc_html.py`. Registry: `build/google_docs/student_worksheet_docs.json`. The 180 exit-ticket Docs are unchanged. |
| Builders / templates | Every worksheet anchor now targets its worksheet Doc (templates edited directly; the 27 builders that generate anchors gained `STUDENT_WORKSHEET_COPY_URLS` keyed by (day, label)). Exit-ticket anchors unchanged. |
| PDFs | 8 worksheet PDFs regenerated (the ones that carried HQIM/"licensed") and re-uploaded to Canvas with new file ids. |
| Canvas pages | All 37 modules re-pushed body-only with `build/canvas/run_builder_body_only.py`; then `build/canvas/apply_response_routes.py --apply` added the **Student response routes** panel to all 180 facilitator guides (Google Doc copy + teacher master, printable PDF, OneNote status, and the one-line retarget instruction). |
| Quiz | 4SW Wk5 practice quiz question renamed "Q1 - HQIM and current source" → "Q1 - Workbook and current source" (name only). |
| Rules | `CLAUDE.md` (one button per response artifact; naming rule; body-only runner + routes pass) and `build/codex-skills/cce-module-authoring/SKILL.md` v1.1.0 §0. |

## Repo state on the Mac

The patch was applied to the working tree of `main` (not committed; the sandbox cannot write `.git/index`). 37 files were already modified before this work (builders, `sync_student_google_doc_links.py`, its test, and an untracked `build/google_docs/style_standards.py`), so review those alongside. Suggested:

```bash
git checkout -b codex/response-route-fix-20260915
git add -A
git commit -m "Fix student response routes: one Google Doc per worksheet, route panels on facilitator guides, HQIM named specifically, workbook pages on student pages"
```

## Rollout order (owner decision 2026-09-14)

1. **Source course 98060** — done (this note). Spot-check: 1SW Wk2 Day 2 and Day 3 student pages; any facilitator guide top panel.
2. **Commons master** — in Canvas: Course → Commons → find the shared CCE course → *Update* from course 98060 so the Commons copy picks up the new page bodies, the 8 re-uploaded PDFs, and the quiz rename. Commons updates do not carry publication state, which is what we want.
3. **Fleet Parity skill (Codex)** — the repo copy is updated (`build/codex-skills/cce-module-authoring/SKILL.md` §0). Sync the same section into the skill Codex loads locally. Add to its checklist: after any builder run on a course, run `apply_response_routes.py --apply --weeks <week>` and then `qa_response_routes.py`.
4. **Other teachers' courses** — for each course: import the updated Commons module(s) (or run the builders against that course id with the body-only runner), then `apply_response_routes.py --apply` against that course id and `qa_response_routes.py`. Both scripts take `COURSE_ID` from the constant at the top; parameterize before fleet use. The Google Docs are shared masters (`/copy` links), so no per-course Doc work is needed.

## Still open

- **OneNote route**: `onenote.status` is `pending` for all 180 days. When a CCE Work template page exists per day, write `build/google_docs/student_onenote_routes.json` (`{day_key: url}`) and re-run `apply_response_routes.py`; the panel picks it up.
- **Wk0 Day 1 goal sheet** has a `.docx` source, not markdown; its Doc was already correct and was left alone.
- **1SW Wk2 Day 2 packet source line**: the worksheet's own intro still says "H&L or Xello" (student-visible in the Doc); acceptable, but "Hats & Ladders or Xello" on first mention would match the rule exactly.
- **Orphan student pages** (23, one published) and the two never-uploaded wk5 PDFs from the audit were out of scope tonight.
- Builders re-upload with `on_duplicate=overwrite`, which assigns new file ids. `apply_response_routes.py` resolves PDF ids live by name, but any other page that hard-linked an old id would need a rebuild.
