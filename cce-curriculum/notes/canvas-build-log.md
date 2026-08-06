# Canvas Build Log

This log records the official Canvas build without storing access credentials or licensed files in GitHub.

## 2026-08-06 — CCR course foundation and Week 0

**Course:** `S1 - CC EXPLOR - LUCERO` (Canvas course 98060)

### Licensed Xello resource library

- Locked folders: 1152475-1152480 under `course files/Licensed/Xello/Grade 8/`
- Unpublished module: `Teacher Build: Licensed Resources` (542875)
- Unpublished page: `Teacher Build: Xello Grade 8 Licensed Resources`
- Module item: 5293961
- Imported files: 20 (Canvas file IDs 14517237-14517256; see the Xello asset manifest for the file-level map)

### 1SW Wk0 module

- Module: `1SW Wk0: Classroom Routines and Career Self-Discovery` (542880)
- State: unpublished
- Locked file folder: `course files/CCR Materials/1SW/Wk0` (1152485)
- Imported course-created files: 17 (Canvas file IDs 14517420-14517436)
- Module items: 5294054-5294059
- Pages:
  - `1sw-wk0-teacher-guide`
  - `1sw-wk0-day-1-lab-routines-and-xello-setup`
  - `1sw-wk0-day-2-h-and-l-setup-and-discover-your-core`
  - `1sw-wk0-day-3-work-values-and-building-blocks`
  - `1sw-wk0-day-4-my-career-journey-reflection`
  - `1sw-wk0-day-5-catch-up-and-career-research`

### Verification

- Module is unpublished.
- All six pages are unpublished.
- The course-materials folder is locked.
- All relative worksheet, rubric, and exit-ticket links were replaced with Canvas file-preview links.
- Existing published course pages and the existing template module were not edited.

### Week 0 Day 2 paired-page pilot

- Teacher page: `teacher-day-2-facilitator-guide` (module item 5294056)
- Student page: `student-1sw-wk0-day-2-who-are-you-at-work` (module item 5294521)
- Locked visuals folder: `course files/CCR Materials/1SW/Wk0/Day 2 Visuals` (1152498)
- Canvas visuals:
  - 14518758 - FYF page 21, Irving ISD CCMR and Programs of Study
  - 14518759 - Climber Notes Discover Your Core directions
  - 14518760 - Climber Notes six core personality types chart
- Both pages are unpublished. The parent module remains unpublished.
- Student page checks: FK grade 5.1; no skipped heading levels; three images with alt text; three native disclosure sections; no layout tables; no legacy Canvas tabs.
- Teacher page checks: FK grade 7.5; no skipped heading levels; one image with alt text; four native disclosure sections; no layout tables.
- Browser QA: desktop layout rendered correctly; 390-pixel mobile width had no horizontal overflow; disclosure sections opened; all images loaded; module navigation resolved.
- Workflow source: `cce-curriculum/notes/canvas-lesson-production-workflow.md`.

### Week 0 complete paired-page module

- Module 542880 remains unpublished and now contains 11 items: the week overview followed by a Teacher Facilitator Guide and Student Guide for Days 1-5.
- Existing teacher item IDs retained: Day 1 5294055, Day 2 5294056, Day 3 5294057, Day 4 5294058, Day 5 5294059.
- Student item IDs: Day 1 5294832, Day 2 5294521, Day 3 5294833, Day 4 5294834, Day 5 5294835.
- Locked Canvas visual folders:
  - Day 1: 1152504 (files 14518975-14518976)
  - Day 2: 1152498 (files 14518758-14518760)
  - Day 3: 1152505 (files 14518977-14518980)
  - Day 4: 1152506 (file 14518982)
  - Day 5: 1152507 (files 14518983-14518984)
- All ten teacher/student pages are unpublished. The week importer completed a second run with the same folder, file, page, and item IDs and no duplicate module items.
- Automated template QA: no skipped headings, missing image alt text, unlabeled disclosure sections, layout tables, legacy Canvas tabs, or unresolved template fields. Student reading levels ranged from FK 5.1 to 7.6.
- Browser QA: every new page rendered in its module route; all licensed visuals loaded; teacher-to-student navigation resolved; the most complex student and teacher pages had no horizontal overflow at a 390-pixel viewport.

## 2026-08-06 — 1SW Week 1 paired lesson set

- Module: `1SW Wk1: Built by Bots - Robotics and Manufacturing Careers` (542948)
- State: unpublished
- Module structure: five Teacher Facilitator Guide and Student Guide pairs, in Day 1-5 order
- Teacher item IDs: Day 1 5294957, Day 2 5294959, Day 3 5294961, Day 4 5294963, Day 5 5294965
- Student item IDs: Day 1 5294958, Day 2 5294960, Day 3 5294962, Day 4 5294964, Day 5 5294966
- Locked Canvas visual folders:
  - Day 1: 1152509
  - Day 2: 1152510
  - Day 3: 1152511
  - Day 4: 1152512
  - Day 5: 1152513
- Supporting PDFs, exit tickets, scaffolds, worksheets, rubric, and monitoring roster are stored in the locked `course files/CCR Materials/1SW/Wk1` hierarchy.
- All ten pages and the parent module are unpublished. Running the Week 1 importer a second time returned the same module, folder, page, and item IDs without duplicate module items.
- Automated template QA found no skipped headings, missing image alt text, unlabeled disclosure sections, layout tables, legacy Canvas tabs, or unresolved template fields.
- Student guides include the hardware-independent Sphero simulator route. Day 5 identifies the Robots for Crayons presentation as the major evidence and keeps Xello/H&L profile work secondary to the required presentation.
- Browser QA: Day 1 student and Day 5 student/teacher pages rendered correctly in Canvas; locked workbook and slide-deck visuals loaded, including the disclosure-based Quality Check set; the Day 5 student and teacher pages had no horizontal overflow at a 390-pixel viewport. Remaining Day 2-4 browser spot checks are required before publication.
- Importer: `build/canvas/build_wk1.py`

## 2026-08-06 — 1SW Week 2 paired lesson set

- Module: `1SW Wk2: Code Your Future - Programming Careers in IT` (542950)
- State: unpublished
- Teacher item IDs: Day 1 5294967, Day 2 5294969, Day 3 5294971, Day 4 5294973, Day 5 5294975
- Student item IDs: Day 1 5294968, Day 2 5294970, Day 3 5294972, Day 4 5294974, Day 5 5294976
- Locked Canvas visual folders:
  - Day 1: 1152515
  - Day 2: 1152516
  - Day 3: 1152517
  - Day 4: 1152518
  - Day 5: 1152519
- All ten pages and the parent module are unpublished. A second importer run returned the same module, folder, page, and item IDs without duplicates.
- District-sequence correction applied in Canvas: Week 2 uses the required Xello Personality Style task (Matchmaker prerequisite); Favorite Clusters remains assigned to the later district window.
- Supplemental-tool correction applied: Code.org is an optional programming-practice route with an equal no-login/paper evidence path. Vendor tutorial completion is not part of the major grade.
- Salary-source correction applied: Xello is the default localized salary source; H&L is allowed only when the teacher records a dated, live-verified local range. BLS remains the national source.
- Major-grade package revised to the IT Salary Comparison plus Career Fit Reflection, 20 points. The rubric explicitly identifies it as one of the six weeks' major grades.
- Automated template QA: no skipped headings, missing alt text, unlabeled disclosure sections, layout tables, legacy Canvas tabs, or unresolved structural fields. Student template reading levels ranged from FK 6.2 to 8.6 before live Canvas rendering.
- Browser QA is still required before publication because the Chrome session had already been finalized when this module finished building.
- Importer: `build/canvas/build_wk2.py`
