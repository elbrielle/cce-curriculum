# Canvas fleet parity: CCE runbook

Read this from the `canvas-fleet-parity` skill (its `references/cce-handoff.md` points here) before any CCE fleet audit or apply. This file is the CCE-side truth; the skill's generic engine (`fleet_audit.py`) is optional for CCE because the repo carries its own bounded tooling, written and proven on 2026-09-15 against all five teacher courses.

## Fleet

Source (Commons master): 98060 (Lucero). Fleet: Goebel 97247, Griffin 97981, Ross 97931, Stanley 97813, Steinbring 98637. Commons resource: "Irving ISD College and Career Exploration".

## Rule

Write page bodies and titles only. Never write modules, module items, assignments, quizzes, files' lock state, or publication state, and never touch anything a teacher created. A page is written only when the teacher's copy still equals the source as it was before the change being propagated (`same_as_prefix`) or is explicitly allow-listed as a stale bulk import. Anything else is `teacher_edited` and is reported, not written.

## Tooling (all in `build/canvas/`)

| Script | Role |
|---|---|
| `dump_course.py <course_id>` | Snapshot pages, modules, files, folders, assignments, quizzes, discussions to `.tmp/fleet-dumps/canvas-<id>/` |
| `fleet_parity_analyze.py` | Classify every fleet page: same_as_prefix / same_as_current / teacher_edited / missing (normalizes course, file, assignment ids and page slugs) |
| `fleet_parity_apply.py` | Push source page bodies into a fleet course with links remapped; `--apply` required to write; `--reupload` for regenerated PDFs; `--allow` for reviewed stale pages |
| `qa_response_routes.py` | Read-only gate: no HQIM, worksheet buttons correct, one routes panel per teacher guide, publication unchanged vs baseline (`CCE_COURSE_ID=<id>`) |

The token is read from stdin (`< ~/.canvas_token`). Never print it, never write it into a report.

## Recipe

```bash
S=.tmp/fleet-dumps; mkdir -p $S
python3 build/canvas/dump_course.py 98060 < ~/.canvas_token          # current source
python3 build/canvas/dump_course.py <fleet_id> < ~/.canvas_token
python3 build/canvas/fleet_parity_analyze.py $S/canvas-<fleet_id> <prefix dump> $S/canvas-98060 --out analysis.json
python3 build/canvas/fleet_parity_apply.py --course <fleet_id> --source-dump $S/canvas-98060 --prefix-dump <prefix dump> --fleet-dump $S/canvas-<fleet_id> [--reupload a.pdf,b.pdf] [--allow stale.json] < ~/.canvas_token      # dry run first
# add --apply only after the dry-run report is reviewed
CCE_COURSE_ID=<fleet_id> python3 build/canvas/qa_response_routes.py --baseline $S/canvas-<fleet_id> < ~/.canvas_token
```

The prefix dump is the source course as it was before the change being propagated. Take a `dump_course.py 98060` before every source edit and keep it; without it the next run cannot tell "teacher edited" from "not yet updated".

## Known fleet quirks (as of 2026-09-15)

- Ross, Stanley, Steinbring still use older slugs for 1SW Wk1 Day 4/5 and `teacher-build-xello-grade-8-licensed-resources`. The apply script matches these by module position and writes the right body; the QA script reports "page missing" for them, which is expected.
- Teacher-created modules seen and left alone: Goebel "Week 1: [Dates Here]"; Ross "Mbot Coding: iPad Modules" plus Wk0 items; Stanley "1SW Wk5/Wk6: Cybersecurity and Capstone" and per-module "Slides for the Week"; Steinbring "Daily Warm Up".
- Griffin lacks 7 source pages (off-module older slugs); Griffin and Steinbring had stale bulk imports that were allow-listed once. Do not carry those allow-lists forward without re-checking.
- Per-teacher pages (welcome, schedule, meet-your-teacher, TSA) and Lucero-only lesson images are never synced.

Run log: `cce-curriculum/notes/audits/2026-09-15-fleet-parity-run.md`.
