# Fleet parity run — 2026-09-15

Source: course 98060 (post-fix). Fleet: Goebel 97247, Griffin 97981, Ross 97931, Stanley 97813, Steinbring 98637. Tooling: `build/canvas/fleet_parity_analyze.py` (classify) → `build/canvas/fleet_parity_apply.py` (page bodies + titles only, links remapped into the fleet course, 8 regenerated PDFs re-uploaded) → `build/canvas/qa_response_routes.py` with `CCE_COURSE_ID`.

## Rule applied

Write a page only when the teacher's copy still equals the source as it was before the 2026-09-14 fix (or is an obviously stale bulk import, listed below). Never write modules, items, assignments, quizzes, publication state, or anything the teacher created. Classification after normalizing course/file/assignment ids and page slugs.

## Result per course

| Course | Pages written | Teacher-created modules (untouched) | Flags |
|---|---|---|---|
| Goebel 97247 | 352 | "Week 1: [Dates Here]" | QA PASS |
| Griffin 97981 | 352 (13 allow-listed: an older bulk import from 2026-09-03 22:40, not hand edits) | none | QA PASS. 7 source pages absent in this course (older slugs still in use, all off-module) |
| Ross 97931 | 352 | "Mbot Coding: iPad Modules"; many teacher-added items in 1SW Wk0 (Turn-Ins, Class Jobs, Help Activity, mobile-device law) | QA clean except the Wk1 Day 4 slug note below |
| Stanley 97813 | 352 | "1SW Wk5/Wk6: Cybersecurity and Capstone"; "Slides for the Week" items per module | same |
| Steinbring 98637 | 352 (5 allow-listed 6SW pages: 2026-08-26 import still carrying the removed lesson-contract block) | "Daily Warm Up" | same |

Wk1 Day 4 / Day 5 note (Ross, Stanley, Steinbring): these courses still use the older page slugs `student-1sw-wk1-day-4-sphero-and-robots-for-crayons` and `student-1sw-wk1-day-5-test-solve-present`. The current source bodies were written INTO those pages (matched by module position), so students see the right content; the QA script only reports "page missing" because it looks up the source slug. Same for `teacher-build-xello-grade-8-licensed-resources`.

Not synced anywhere (by design): the six `question-0N-tree-ai.png` / files-and-folders PNGs belong to a Lucero-only lesson page; TSA, welcome, schedule, and meet-your-teacher pages are per-teacher.

## Commons

Shared resource "Irving ISD College and Career Exploration" updated from 98060 on 2026-09-15 with version notes (share-to-all-of-Irving-ISD, Copyrighted, grade 7).

## Re-run recipe (Fleet Parity skill)

```bash
S=.tmp/fleet-dumps; mkdir -p $S
python3 <dump_course.py> 98060      # current source
python3 <dump_course.py> <fleet_id>
python3 build/canvas/fleet_parity_analyze.py $S/canvas-<fleet_id> <pre-change source dump> $S/canvas-98060 --out analysis.json
python3 build/canvas/fleet_parity_apply.py --course <fleet_id> --source-dump $S/canvas-98060 --prefix-dump <pre-change source dump> --fleet-dump $S/canvas-<fleet_id> [--reupload a.pdf,b.pdf] [--allow stale.json] --apply < ~/.canvas_token
CCE_COURSE_ID=<fleet_id> python3 build/canvas/qa_response_routes.py --baseline $S/canvas-<fleet_id> < ~/.canvas_token
```

The "prefix dump" is the source course as it was before the change being propagated; keep a dump before every source edit so the next fleet run can tell "teacher edited" from "not yet updated".
