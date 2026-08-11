# Canvas Build Log

This log records the official Canvas build without storing access credentials or licensed files in GitHub.

## 2026-08-09 — Teacher-owned publication boundary (current)

- The user clarified that course 98060 is the district master/template. It must contain the full course while leaving publication decisions to each teacher after cloning.
- Returned the reviewed home page, orientation, Teacher Build resources, all 36 instructional week modules, every module item, and their page/assignment/discussion/quiz content to unpublished state. No content was deleted. Canvas requires one published page to retain its front-page designation, so the unused generic `Welcome!` page is the inert technical placeholder; the course opens to Modules and Pages remains hidden from student navigation.
- Relocked the complete `course files/CCR Materials` and `course files/Licensed` trees. The course default view is Modules; the lean Home, Modules, and Grades navigation remains as an organizational choice.
- Removed the two auto-publication utilities. Added `build/canvas/stage_course_template.py` as the recovery guardrail for imports or accidental publication.
- The district-master gate is `build/canvas/qa_remaining_unpublished.py`. `qa_course_publication.py` is only for a teacher-owned clone after that teacher has chosen what to publish.

## 2026-08-09 — Superseded launch-shell experiment

This visibility experiment was reverted the same day after the teacher-owned publication boundary was clarified. It remains here as incident history, not current Canvas state.

- Replaced the generic template home with `Career and College Exploration Home` and set the course home layout to the reviewed Pages front page.
- Published `START HERE: CCE Course Orientation` with its one student page. `Teacher Build: Licensed Resources` remains unpublished.
- Reduced student navigation to Home, Modules, and Grades. Instructor-only internal tools remain available to teachers, while integrations are launched from the lesson that gives them a specific job.
- Unpublished the five unused template pages: `Welcome!`, `Meet Your Teacher`, `Quick Links`, `Schedule`, and `Syllabus`. No pages were deleted.
- Published `1SW Wk0: Classroom Routines and Career Self-Discovery` as the first instructional pilot. Students see five Day headers, five Student Guides, and `MINOR 1: My Career Journey Reflection`; all five Teacher Facilitator Guides remain unpublished.
- Unlocked only the `CCR Materials/1SW/Wk0` delivery chain required for authenticated student access. Sibling week folders and the teacher-only licensed Xello library remain locked.
- Student View verified the replacement home, orientation-first sequence, Week 0 module order, hidden teacher pages, direct Student Guide route, mobile-width layout with no horizontal overflow, and the mapped 100-point Minor.
- Canvas publication behavior is now recorded in the production workflow: publishing a parent module cascades publication to every child, so teacher pages must be re-hidden afterward; file access also requires the parent folder chain to be available.
- Launch-shell automation: `build/canvas/configure_course_launch_shell.py`
- Reviewed-module publisher: `build/canvas/publish_reviewed_module.py`
- Publication audit: `build/canvas/qa_course_publication.py`

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
- Browser QA: all ten pages rendered correctly in Canvas. Every locked workbook and slide-deck visual loaded after normal viewport scrolling, including the disclosure-based Quality Check set. The most complex student and teacher pages had no horizontal overflow at a 390-pixel viewport.
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
- Browser QA: all ten pages rendered correctly in Canvas with no unresolved template fields or desktop overflow. Every embedded workbook image loaded at its expected 1275-pixel source width after normal viewport scrolling. The Day 3 student guide and Day 5 teacher guide had no horizontal overflow at a 390-pixel viewport.
- Importer: `build/canvas/build_wk2.py`

## 2026-08-06 — 1SW Week 3 paired lesson set

- Module: `1SW Wk3: Network Ninjas - Computer Science and Networking Careers` (542972)
- State: unpublished
- Teacher item IDs: Day 1 5295220, Day 2 5295222, Day 3 5295224, Day 4 5295226, Day 5 5295228
- Student item IDs: Day 1 5295221, Day 2 5295223, Day 3 5295225, Day 4 5295227, Day 5 5295229
- Locked Canvas visual folders:
  - Day 1: 1152541
  - Day 2: 1152542
  - Day 3: 1152543
  - Day 4: 1152544
  - Day 5: 1152545
- All ten pages and the parent module are unpublished. A second importer run returned the same module, folder, page, and item IDs without duplicates.
- District-sequence correction applied: Week 3 uses the required 20-minute Xello Learning Style quiz. Add Skills remains assigned to Week 4. The licensed My Learning Styles teacher guide is linked from the facilitator page.
- Supplemental-platform correction applied: Day 1 has a complete four-career card route, H&L is optional, and Day 4 uses BLS plus a teacher-approved local employer source. Xello is the preferred local-salary source when the exact career is available.
- Evidence correction applied: BLS proxy occupations are labeled as proxies, and a missing standalone BLS title is not treated as proof that a career is emerging.
- Major-grade package revised to the App Design Packet plus Emerging Tech Research, 16 points. The small-group pitch remains communication practice so one teacher is not expected to score several simultaneous presentations.
- Automated template QA: no skipped headings, missing alt text, unlabeled disclosure sections, layout tables, legacy Canvas tabs, or unresolved structural fields. Student reading levels ranged from FK 5.0 to 9.4; the Day 4 guide is the highest because it preserves necessary BLS/source vocabulary.
- New and revised PDFs were rendered, page-count checked, and visually inspected.
- Browser QA: all ten pages rendered correctly through their module-item routes. Every page remained unpublished, no unresolved template fields appeared, all disclosure sections were labeled, and all embedded visuals loaded at full source resolution. No lesson body overflowed on desktop. The Day 3 student guide and Day 5 teacher guide had no horizontal overflow at a 390-pixel viewport. Week 3 has passed the publication-readiness gate but remains unpublished for owner review.
- Importer: `build/canvas/build_wk3.py`

## 2026-08-06 — 1SW Week 4 paired lesson set

- Module: `1SW Wk4: Help Desk Heroes - Tech Support Careers and MakeCode` (542973)
- State: unpublished
- Teacher item IDs: Day 1 5295240, Day 2 5295242, Day 3 5295244, Day 4 5295246, Day 5 5295248
- Student item IDs: Day 1 5295241, Day 2 5295243, Day 3 5295245, Day 4 5295247, Day 5 5295249
- Locked Canvas visual folders:
  - Day 1: 1152547
  - Day 2: 1152548
  - Day 3: 1152549
  - Day 4: 1152550
  - Day 5: 1152551
- All ten pages and the parent module are unpublished. A second importer run returned the same module, folder, page, and item IDs without duplicates.
- District-sequence correction applied: Day 1 protects the required Xello Add Interests task and Day 5 protects the required Xello Add Skills task. The matching licensed Xello teacher resources are embedded in the facilitator guides. H&L remains optional.
- Source correction applied: the education-route lesson uses a dated BLS guide with May 2024 national medians and labels the figures as neither starting pay nor DFW-localized salary. Drift-prone CompTIA names, prices, and roadmaps are not load-bearing lesson evidence.
- Access correction applied: the MakeCode lesson accepts hardware, simulator, or paper trace as equal routes. Students save durable test evidence, and the customer-service lesson includes a written-chat alternative to spoken role-play.
- Major-grade package revised to the Help Desk Program Evidence plus each student's Xello Skill and Help Desk Connection, 16 points. The one-minute lightning demo is formative so the teacher does not have to live-score ten to fifteen teams while they present.
- Automated template QA: no skipped headings, missing alt text, unlabeled disclosure sections, layout tables, legacy Canvas tabs, or unresolved structural fields. Student reading levels ranged from FK 6.2 to 11.8; the Day 2 guide is highest because it preserves necessary pathway, median-pay, and credential vocabulary.
- New and revised PDFs were rendered and visually inspected.
- Browser QA: all ten pages rendered correctly through their module-item routes. Every page remained unpublished, all eight embedded workbook visuals loaded at full 1275-by-1650 source resolution, and teacher/student disclosures opened correctly. No page overflowed on desktop. The Day 3 student guide and Day 5 teacher guide had no horizontal overflow at a 390-pixel viewport. Week 4 passed the publication-readiness gate and remains unpublished for owner review.
- Importer: `build/canvas/build_wk4.py`

## 2026-08-06 — 1SW Week 5 paired lesson set

- Module: `1SW Wk5: Cyber Defenders - Cybersecurity Careers and Capstone` (542984)
- State: unpublished
- Teacher item IDs: Day 1 5295315, Day 2 5295317, Day 3 5295319, Day 4 5295321, Day 5 5295323
- Student item IDs: Day 1 5295316, Day 2 5295318, Day 3 5295320, Day 4 5295322, Day 5 5295324
- Locked Canvas visual folders:
  - Day 1: 1152553
  - Day 2: 1152554
  - Day 3: 1152555
  - Day 4: 1152556
  - Day 5: 1152557
- All ten pages and the parent module are unpublished. A second importer run returned the same module, folder, page, and item IDs without duplicates.
- District-sequence correction applied: Day 4 protects the required 40-minute Xello Favorite clusters task and requires at least one saved cluster. Save Careers remains in its later district window. The licensed 90-minute My career clusters lesson is linked as optional teacher background, with its additional prerequisites explicitly excluded from the core minimum.
- Cybersecurity-source correction applied: the dated route guide uses BLS May 2024 national medians and 2024-34 projections. CyberSeek and H&L are optional live exploration; neither a fixed CyberSeek ladder nor unverified DFW salary is load-bearing.
- Phishing-safety correction applied: the complete seven-email source set is embedded in locked Canvas, the teacher guide includes the exact answer key, and practice messages remain fictional and unsent with no real credentials, links, QR codes, attachments, or district impersonation.
- Workload and equipment correction applied: the capstone no longer requires teachers to run a laser queue outside class. Paper, Canva, Adobe Express, SVG, and PNG are equal evidence routes. Any laser example is optional, model-specific, and handled by an authorized trained operator under campus procedures.
- Major-grade package revised to one four-part, 16-point capstone: Bootcamp Plan, Flyer/Integrity, Postsecondary Goal/Original Symbol, and Career Reflection. The rubric uses the district Masters, Meets, Approaches, and Needs Improvement bands; platform access, gallery participation, and fabrication are not graded.
- Automated template/API QA: no skipped headings, missing alt text, unlabeled disclosures, layout tables, legacy Canvas tabs, unresolved structural fields, missing file references, or published pages. All 19 referenced Canvas files resolved.
- PDF QA: six revised/new Week 5 student and teacher PDFs were page-count checked, text-extracted, rendered, and visually inspected. The one-page reflection no longer creates a blank second page.
- Browser QA: all ten pages rendered through their module-item routes with no unresolved fields or desktop overflow. All 12 student-page visuals loaded at full source resolution, including the seven individual email slides. The phishing student guide and capstone teacher guide had no horizontal overflow at a 390-pixel viewport; disclosures and responsive images rendered cleanly.
- Importer: `build/canvas/build_wk5.py`

## 2026-08-06 — 2SW Week 1 paired lesson set

- Module: `2SW Wk1: Order in the Court - Legal Studies` (542987)
- State: unpublished
- Teacher item IDs: Day 1 5295340, Day 2 5295342, Day 3 5295344, Day 4 5295346, Day 5 5295348
- Student item IDs: Day 1 5295341, Day 2 5295343, Day 3 5295345, Day 4 5295347, Day 5 5295349
- Locked Canvas visual folders:
  - Day 1: 1152560
  - Day 2: 1152561
  - Day 3: 1152562
  - Day 4: 1152563
  - Day 5: 1152564
- All ten pages and the parent module are unpublished. A second importer run returned the same module, folder, page, file, and item IDs without duplicates.
- Six missing classroom artifacts are now supplied: Emergency Kit Decision Plan, City Council Town and Ordinance Plan, Legal Review Argument and Evidence Sheet, Legal Entrepreneur and Association Card, Legal Policy Position Paper Rubric, and Xello Life Experience Connection. The existing Career Research Worksheet is reused.
- Day 1 no longer requires H&amp;L or treats every salary as DFW starting pay. Students use dated teacher-approved sources and label salary type, geography, and data year.
- Day 4 uses a controlled hypothetical and balanced evidence bank. Students do not research real cases or family experiences, and written argument is equal to oral presentation. The major grade is one 16-point durable evidence set rather than live debate performance.
- Day 5 protects the configured 10-minute Xello Life experiences task and verifies at least one saved experience. H&amp;L and eDynamic remain supplemental. Access issues move to a supervised catch-up block and do not reduce the major grade.
- Canvas-interaction review: the current course has four unweighted/default assignment groups and no confirmed Minor/Major groups. Graded Canvas Assignments and rubric objects remain deferred until the 40/60 gradebook structure is established. The production workflow now requires choosing Pages, Assignments, Discussions, Quizzes, or integrations by instructional purpose instead of defaulting every task to print.
- Automated template/API QA: no skipped headings, missing alt text, unlabeled disclosures, layout tables, legacy Canvas tabs, unresolved fields, missing file references, nonconsecutive item order, or published content. All referenced files resolved.
- PDF QA: all six new printables were rendered, page-count checked, text-extracted, and visually inspected. The three-page ordinance plan uses deliberate page breaks so no heading or response area clips.
- Browser QA: all ten pages rendered through their module-item routes with no unresolved fields or desktop overflow. All locked workbook images loaded at full 1148-by-1485 source resolution after opening the relevant disclosure. The Day 3 student guide and Day 5 teacher guide had no horizontal overflow at a 390-pixel viewport.
- Importer: `build/canvas/build_2sw_wk1.py`
- Read-only verifier: `build/canvas/qa_canvas_module.py 542987`

## 2026-08-06 — 2SW Week 2 paired lesson set

- Module: `2SW Wk2: First Responders - Evidence, Response, and Handoff` (542988)
- State: unpublished
- Teacher item IDs: Day 1 5295350, Day 2 5295352, Day 3 5295355, Day 4 5295357, Day 5 5295359
- Student item IDs: Day 1 5295351, Day 2 5295353, Day 3 5295356, Day 4 5295358, Day 5 5295360
- Unpublished practice Discussion: `PRACTICE: Clinton Lake Counterevidence Exchange` (topic 369615, item 5295363)
- Locked Canvas folders:
  - Core Week 2 files: 1152565
  - Day 1 visuals: 1152566
  - Day 2 visuals: 1152567
  - Day 3 visuals: 1152568
  - Day 4 visuals: 1152569
  - Day 5 visuals: 1152570
- All ten pages, the practice Discussion, and the parent module are unpublished. The final module has 11 consecutive items.
- Six new classroom artifacts are supplied: dated First Responder Route Guide, Clinton Lake Evidence Tracker, controlled Trail Simulation Record, fictional Patient Care Report and Safety Plan, 16-point report rubric, and individual Career and Integrity Reflection.
- Career-source correction: the route guide labels May 2024 BLS figures as U.S. medians rather than starting or DFW pay. Xello may add a current local figure only when geography, date, and measure are recorded. H&amp;L remains optional.
- District-program correction: the current Singley Academy page verifies Law Enforcement and Emergency Medical - EMT. The lesson does not promise a specific credential, academy length, or job outcome.
- Evidence correction: all six Clinton Lake files are embedded individually with descriptive alt text. The teacher key distinguishes strong evidence of harm from weaker evidence about source and preserves the unresolved containment-testing gap.
- Safety/access correction: the trail activity is explicitly a simulation, not first-aid certification. A model/mannequin, consenting uninjured partner, and observer/documenter are equal routes; no student practices on an injury or is graded on touch or physical technique.
- Wilderness decision correction: students are not asked to cross fast water or outrun lightning. The safety plan uses no-entry, communication, alternate-route/higher-ground, and appropriate-shelter decisions.
- Canvas interaction: the Day 2 Discussion provides a genuine counterevidence exchange with a private written alternative. It is ungraded because the course still lacks confirmed 40/60 Minor/Major assignment groups.
- Automated template/API QA: no missing alt text, unresolved fields, legacy Canvas tabs, missing file references, nonconsecutive module positions, or published content. All 20 referenced files resolved; the practice Discussion is supported by the generic module verifier.
- PDF QA: six worksheets and five revised exit tickets were rendered, page-count checked, and visually inspected. Extra blank pages were removed from the trail, reflection, and patient-report sets.
- Browser QA: the signed-in module sequence shows one Discussion item; the Day 2 student guide contains six embedded licensed evidence images with descriptive alt text; and the Day 4 teacher dashboard renders cleanly at normal desktop width.
- Importer: `build/canvas/build_2sw_wk2.py`
- Read-only verifier: `build/canvas/qa_canvas_module.py 542988`

## 2026-08-06 — 2SW Week 3 paired lesson set

- Module: `2SW Wk3: Nursing Science - Routes, Simulation, and Handoff` (542989)
- State: unpublished
- Teacher item IDs: Day 1 5295364, Day 2 5295366, Day 3 5295368, Day 4 5295370, Day 5 5295373
- Student item IDs: Day 1 5295365, Day 2 5295367, Day 3 5295369, Day 4 5295371, Day 5 5295374
- Unpublished Classic practice Quiz: `PRACTICE: Vital Signs and Handoff Check` (quiz 281449, item 5295372). It contains five multiple-choice questions, immediate feedback, and unlimited retries.
- Locked Canvas folders:
  - Core Week 3 files: 1152571
  - Day 1 visuals: 1152572
  - Day 2 visuals: 1152573
  - Day 3 visuals: 1152574
  - Day 4 visuals: 1152575
  - Day 5 visuals: 1152576
- All ten pages, the practice Quiz, and the parent module are unpublished. The final module has 11 consecutive items. A second importer run returned the same module, folder, page, file, quiz, and item IDs without duplicates.
- District-sequence correction: Day 5 protects 30 minutes for the required Xello Save careers task and requires at least three saved careers. H&amp;L remains supplemental, and failed access moves to supervised Xello catch-up rather than paper being counted as platform completion.
- Program correction: the week uses the current Irving ISD Nursing Science name. It does not promise a specific credential or job outcome. Texas students are directed to verify program approval and the correct licensure examination with the Texas Board of Nursing.
- Career-data correction: the route guide labels the four May 2024 BLS figures as U.S. medians, not starting pay or DFW-localized salary. Xello may add localized evidence only when the geography, measure, and date are recorded.
- Privacy and safety correction: all patient records and device values are fictional. Students do not collect peer health information, make diagnoses, or treat the micro:bit/browser program as a medical device. Physical micro:bit, browser simulator, and paper trace are equal evidence routes.
- Canvas interaction: the Day 4 Quiz checks bounded misconceptions about simulated data, symptom reporting, conflicting readings, salary labels, and program approval. The individual fictional handoff remains the recommended 16-point minor checkpoint because judgment and documentation do not belong in forced multiple choice.
- Automated template/API QA: no skipped headings, missing alt text, unlabeled disclosures, layout tables, legacy Canvas tabs, unresolved fields, missing file references, nonconsecutive module positions, or published content. All 14 referenced Canvas files resolved; the generic verifier confirms the unpublished Quiz and five-question count.
- PDF QA: seven classroom artifacts and five structured exit tickets were rendered, page-count checked, text-extracted, and visually inspected. No response area or heading clips.
- Browser QA: the signed-in module shows all 11 items in the intended order. The Day 3 and Day 4 student pages render without desktop overflow; licensed visuals load at full source resolution after opening their optional disclosures. The Day 4 student link opens the correct practice Quiz, whose teacher preview contains all five intended questions.
- Importer: `build/canvas/build_2sw_wk3.py`
- Read-only verifier: `build/canvas/qa_canvas_module.py 542989`

## 2026-08-06 — 2SW Week 4 paired lesson set

- Module: `2SW Wk4: Smile Squad - Dental Science and Health Data` (542990)
- State: unpublished
- Teacher item IDs: Day 1 5295375, Day 2 5295377, Day 3 5295379, Day 4 5295381, Day 5 5295384
- Student item IDs: Day 1 5295376, Day 2 5295378, Day 3 5295380, Day 4 5295382, Day 5 5295385
- Unpublished Classic practice Quiz: `PRACTICE: ICD-10-CM Evidence Check` (quiz 281450, item 5295383). It contains five multiple-choice questions, answer feedback, and unlimited retries.
- All ten pages, the practice Quiz, and the parent module are unpublished. The signed-in module view confirms all 11 items in the intended order.
- Seven missing classroom artifacts are now supplied: current dental/medical-records evidence guide, cumulative three-career comparison, Smile Squad observation record, toothbrush design brief, Xello Experiences checkpoint, complete fictional ICD-10-CM lab, and student-visible 16-point rubric.
- Xello sequence correction: Day 3 protects the required Education experiences catch-up and Volunteer hours task. Students record only actual experiences; no student invents an hour. School Subjects at Work is labeled supplemental, and paper is temporary scaffolding rather than platform completion.
- Source correction: the core comparison uses one May 2024 U.S. median basis and a transparent same-source classroom rule. Xello may add a local figure only when geography, date, and measure are visible. H&amp;L remains optional.
- Program correction (superseded 2026-08-09): FYF and the 2026-27 High School Course Work list Health Science: Dental and Health Science: Medical Billing at Singley. The rebuilt module uses Medical Billing and Coding as the student-facing career and treats national BLS data only as a labeled comparison source.
- Privacy and safety correction: the Smile Squad images are observation training, not student diagnosis. The medical-records lab uses fictional charts only and a ten-code FY 2027 ICD-10-CM set checked against CMS descriptions effective October 1, 2026.
- Canvas interaction: the Day 4 Quiz checks bounded misconceptions about privacy, exact code matching, specificity, career scope, and salary labels. Individual career comparison and recommendation remain teacher-reviewed evidence.
- Grading: Day 5 is a recommended 16-point minor checkpoint. No graded Canvas Assignment was created because the course still lacks confirmed weighted Minor/Major assignment groups.
- PDF QA: seven artifacts and five structured exit tickets were rendered and visually inspected. No response area, table, or heading clips; the rubric fits on two landscape pages.
- Browser QA: the signed-in module is unpublished with 11 ordered items. The Day 1 student page and Day 4 teacher page render cleanly with no unresolved tokens or desktop overflow. The student guide has no horizontal overflow at a 390-pixel viewport. The Quiz edit surface reports 5 points, Not Published, and the five intended question names.
- Importer: `build/canvas/build_2sw_wk4.py`

## 2026-08-08 - 2SW Week 5 paired lesson set

- Module: `2SW Wk5: Communication and Goal Setting` (544296)
- State: unpublished
- Teacher item IDs: Day 1 5311184, Day 2 5311186, Day 3 5311189, Day 4 5311191, Day 5 5311194
- Student item IDs: Day 1 5311185, Day 2 5311187, Day 3 5311190, Day 4 5311192, Day 5 5311195
- Unpublished Classic practice Quiz: `PRACTICE: Active Listening Evidence Check` (quiz 281850, item 5311188). It contains five multiple-choice questions with feedback.
- Unpublished practice Discussion: `PRACTICE: Little Library Message Lab` (topic 370735, item 5311193). A private written route remains equal.
- Locked Canvas folders:
  - Core Week 5 files: 1155164
  - Day 1 visuals: 1155165
  - Day 2 visuals: 1155166
  - Day 3 visuals: 1155167
  - Day 4 visuals: 1155168
- All ten pages, both practice interactions, and the parent module are unpublished. The generic API verifier passed all 12 items in consecutive order with no unresolved fields, unsupported item types, missing files, or published content.
- Seven classroom artifacts are supplied: PowerSkills Transfer Guide, Conflict Resolution Plan, Active Listening Lab, Advocacy SMART Goal and Time Plan, Written Message Lab, Work Experience and Skills Synthesis, and the student-visible 16-point Communication and Goal rubric.
- Xello sequence correction: Day 5 protects the required Grade 8 Work experiences task for 10 minutes and requires at least one authentic experience. Time Management remains supplemental. Paper may scaffold an access failure but does not replace Completion Standards evidence.
- Xello resource packaging: the licensed `My experiences` facilitator guide is embedded directly on the Day 5 teacher page. The production workflow now requires agents to inspect and capture the aligned Xello activity plan, facilitator guide, slide deck, worksheet, student directions, and downloadable video when Xello supplies them, then place those files only in locked Canvas.
- Safety and privacy correction: all health and workplace cases are fictional. Students do not diagnose, give treatment advice, invent charting, share personal health details, or post Xello, CareerOneStop, goal, or skill results publicly.
- Canvas interaction review: the Day 2 Quiz provides immediate misconception feedback; the Day 4 Discussion supports a genuine reader-feedback exchange without making public participation mandatory. Durable individual evidence remains in the worksheet/synthesis rather than being replaced by clicks.
- Grading: the week closes with a recommended 16-point minor checkpoint across goal and time planning, practiced transferable skill, two-career transfer, and a specific next action. Daily tickets and practice interactions remain formative.
- Browser QA: the signed-in Day 2 student guide rendered both licensed FYF visuals with descriptive alt text. The Day 4 student guide preserved the fictional-message and no-clinical-advice boundaries. The Day 5 teacher page linked the synthesis, rubric, and licensed Xello guide. The Day 4 student guide had no horizontal overflow at a 390-pixel viewport.
- Importer: `build/canvas/build_2sw_wk5.py`
- Read-only verifier: `build/canvas/qa_canvas_module.py 544296`

## 2026-08-08 - 2SW Week 6 paired lesson set

- Module: `2SW Wk6: Science Meets Medicine` (544297)
- State: unpublished
- Teacher item IDs: Day 1 5311197, Day 2 5311199, Day 3 5311201, Day 4 5311204, Day 5 5311206
- Student item IDs: Day 1 5311198, Day 2 5311200, Day 3 5311202, Day 4 5311205, Day 5 5311207
- Unpublished Classic practice Quiz: `PRACTICE: Outbreak Evidence Check` (quiz 281851, item 5311203). It contains four multiple-choice questions, immediate feedback, and unlimited retries.
- Unpublished private Assignment: `PRACTICE: Explore Career Matches Reflection` (assignment 3093978, item 5311208). It is ungraded and accepts private text entry or file upload; students are told not to submit profile screenshots.
- Locked Canvas folders:
  - Core Week 6 files: 1155170
  - Day 1 visuals: 1155171
  - Day 2 visuals: 1155172
  - Day 3 visuals: 1155173
  - Day 4 visuals: 1155174
  - Day 5 visuals: 1155175
- Core worksheet file IDs after the final space-audit sync: career guide 14561442, cover-letter lab 14561443, Mini Medics record 14561444, investigation record 14561445, response plan 14561446, and Xello reflection 14561447.
- All ten pages, both practice interactions, and the parent module are unpublished. The generic API verifier passed all 12 items in consecutive order with no unresolved fields, unsupported item types, missing file references, or published content.
- Six classroom artifacts are supplied: Biomedical Career Evidence Guide, Cover Letter Lab, Mini Medics Design Record, Outbreak Investigation Record, Outbreak Response Plan, and Xello Career Matches Reflection.
- Career-source correction: the shared evidence guide uses May 2024 BLS U.S. medians, education routes, 2024-34 outlook, and annual openings. It does not call national medians DFW or starting pay. Xello may add a localized figure only when geography, date, and measure are visible. H&amp;L remains optional.
- Safety and evidence correction: the job posting, Mini Medics design challenge, and outbreak case are controlled fictional tasks. Students do not submit a real application, diagnose a resident, invent public-health instructions, or use classroom material as official emergency guidance.
- Canvas interaction review: the Day 3 Quiz gives bounded feedback on comparison groups, claim limits, immediate action versus prevention, and the real-event boundary. The Day 5 Assignment provides a private reflection route without making career-assessment results public.
- Xello resource packaging: Day 5 embeds the licensed facilitator guide, an Irving-adapted six-slide teacher deck, one-page student directions, and the official student-facing video. The live Grade 8 minimum remains Explore career matches for 35 minutes, with Matchmaker and at least three saved careers as prerequisites. The full guide is clearly labeled as an extended 120-minute option.
- Grading: Week 6 is formative synthesis and adds no new grade. The 2SW map remains two majors in Weeks 1 and 2 and three minors in Weeks 3-5.
- PDF QA: all six artifacts and five revised exit tickets were rendered, page-count checked, text-extracted, and visually inspected. A prompt-to-space audit enlarged the Mini Medics drawing field, moved the career comparison explanation to a two-line area, expanded outbreak evidence responses, replaced cramped action tables with full-width response fields, and expanded the evidence-ranking ticket. The six core artifacts contain eleven pages with no blank last page, clipped heading, or prompt that asks for sentence reasoning in a phrase-sized field.
- Presentation QA: the adapted Xello deck preserves the source visual system, removes the authoring-instructions slide, replaces Google SSO with ClassLink &gt; Xello, and passes slide overflow checks. All six slides were rendered and inspected.
- Browser QA: the signed-in module shows all 12 items in the intended order. The Day 2 student guide renders the three licensed workbook visuals with descriptive alt text. The Day 5 teacher guide exposes the full Xello resource package, the student page embeds the official video, and the student guide remains usable at a 390-by-844 viewport.
- Importer: `build/canvas/build_2sw_wk6.py`
- Read-only verifier: `build/canvas/qa_canvas_module.py 544297`

## 2026-08-08 - Canvas-only production decision

- Canvas is the sole active production, review, and delivery environment for teachers and students.
- GitHub is retained for source control, automation history, and backup only.
- The MkDocs/GitHub Pages site is a legacy archive. It is not a teacher review surface, may be stale, and is no longer part of the routine QA or release gate.
- The GitHub Pages workflow is manual-only. Routine pushes to `main` do not deploy the legacy site.
- Default closeout is now Canvas template/API/browser/accessibility/mobile/permissions/Student View verification followed by a source-backup commit and push.
- Rehost a video file in Canvas only when Xello supplies a downloadable file or the district has explicit permission for that video.
- Do not extract a media file from a hosted stream merely because it plays in the browser.

## 2026-08-08 - 3SW Week 1 paired lesson set

- Module: `3SW Wk1: Veterinary Science` (544298)
- State: unpublished
- Teacher item IDs: Day 1 5311210, Day 2 5311213, Day 3 5311216, Day 4 5311220, Day 5 5311224
- Student item IDs: Day 1 5311211, Day 2 5311214, Day 3 5311217, Day 4 5311221, Day 5 5311225
- Native Day `SubHeader` items: 5311209, 5311212, 5311215, 5311219, 5311223. The module uses one chronological route: day header, teacher guide, student guide, then that day's interaction.
- Unpublished Classic practice Quiz: `PRACTICE: Veterinary Triage Evidence Check` (quiz 281852, item 5311218). Four multiple-choice questions provide immediate feedback and unlimited retries.
- Unpublished private Assignment: `PRACTICE: Xello Skills Reflection` (assignment 3093979, item 5311222). It is ungraded, accepts private text or file submission, and forbids profile screenshots.
- Locked Canvas folders: core Week 1 1155181; Day 1 1155182; Day 2 1155183; Day 3 1155184; Day 4 1155185; Day 5 1155186.
- Core artifact file IDs: career evidence 14561450, comparison 14561451, triage record 14561452, Xello reflection 14561453, pathway brief 14561454, and rubric 14561455.
- Xello file IDs: Skills facilitator guide 14561456, Irving ClassLink slide deck 14561467, and optional Spanish support deck 14561458.
- Xello sequence correction: Day 4 protects the required Grade 8 Skills lesson for 35 minutes with at least three saved careers as the prerequisite. Life experiences and Volunteer hours are not repeated. The six-page guide's 85-minute sequence is extended teacher support, not the district minimum.
- Career evidence correction: the fixed guide uses May 2024 BLS U.S. medians, typical entry education, 2024-34 outlook, and annual openings for Veterinary Assistant, Veterinary Technician, and Veterinarian. No figure is called DFW-localized or starting pay.
- Program correction: Day 5 uses the current Nimitz public program names and treats certification opportunities and the 300-hour CVA internship route as opportunities with requirements, not guarantees. Workbook district pages are labeled curriculum context.
- Safety correction: the licensed triage case is fictional. Students observe, compare, prioritize, and report; they do not diagnose, prescribe, or give treatment advice.
- Grading: the comparison, triage reasoning, and pathway brief form a recommended 16-point minor evidence packet. Quiz attempts, Xello clicks, design polish, and platform access are not separate grades.
- Worksheet QA: six PDFs totaling eleven pages were rendered, text-extracted, and visually checked. Sentence reasoning has full-width ruled space, multi-part prompts have separate labeled areas, the pathway brief uses short sections rather than a forced paragraph, and the custom triage record supplies decision space missing from the workbook case page.
- Presentation QA: the six-slide official Xello deck removes the authoring slide, changes Google sign-on to ClassLink &gt; Xello, repairs the agenda, and adds an independent/private exit route. All slides were rendered and inspected; overflow and template checks passed.
- API/browser QA: the generic verifier passed all 17 consecutive items with no unresolved fields, missing file references, unsupported types, or published content. Signed-in browser QA confirmed the day-header hierarchy, descriptive image alt text, PDF and Quiz links, and clean desktop rendering. Student View correctly showed no modules because the course content remains unpublished, and the test session was exited.
- Importer: `build/canvas/build_3sw_wk1.py`
- Read-only verifier: `build/canvas/qa_canvas_module.py 544298`

## 2026-08-08 - 3SW Week 2 paired lesson set

- Module: `3SW Wk2: Plant Science and Agricultural Communication` (544301)
- State: unpublished
- Teacher item IDs: Day 1 5311245, Day 2 5311248, Day 3 5311251, Day 4 5311254, Day 5 5311259
- Student item IDs: Day 1 5311246, Day 2 5311249, Day 3 5311252, Day 4 5311255, Day 5 5311260
- Native Day `SubHeader` items: 5311244, 5311247, 5311250, 5311253, 5311259. The module uses one chronological route: day header, teacher guide, student guide, then that day's interaction when present.
- Unpublished Classic practice Quiz: `PRACTICE: Emerging Plant-Tech Evidence Check` (quiz 281854). Four multiple-choice questions provide immediate misconception feedback and unlimited retries.
- Unpublished private assignments: `PRACTICE: Plant Science Evidence Packet` (3093993) and `PRACTICE: Xello Biases Reflection` (3093994). Both remain ungraded during review.
- Locked Canvas folders: core Week 2 1155187; Day 1 1155188; Day 2 1155189; Day 3 1155190; Day 4 1155191; Day 5 1155192.
- Core artifact file IDs: career evidence 14561484, Farm-to-Table planner 14561485, major rubric 14561486, emerging-tech evidence 14561487, emerging-tech evaluation 14561488, and Xello reflection 14561489.
- Xello file IDs: facilitator guide 14561490, official introduction deck 14561491, Career Trailblazers directions 14561492, and Non-traditional Career Matches directions 14561493.
- Xello sequence correction: Day 5 protects the required Grade 8 Biases and career choices Activity 2 for 30 minutes. The other two activities in the 80-minute facilitator package are optional extensions. Work experiences is not repeated.
- Career evidence correction: fixed BLS/USDA guides replace open search and avoid treating national medians as DFW-local or starting pay. Plant Science at Nimitz and the Nimitz Floral Studio are current district facts; unsupported credential claims are omitted.
- Canvas interaction review: Day 4 uses an unlimited-retry practice quiz for evidence boundaries. Day 5 uses a private reflection assignment; students never post personal Xello results publicly. Canva, Adobe Express, and paper are equal build routes.
- Grading safety: the infographic and emerging-tech evaluation form a recommended 16-point major packet. Because course 98060 has active enrollments and `apply_assignment_group_weights` is currently false, no assignment-group weights or live grade calculations were changed during module production.
- Worksheet QA: six PDFs were rendered and visually inspected. The infographic planner includes a full-page 7.25-inch sketch field; the emerging-tech evaluation includes ten ruled lines for a 4-6 sentence response; the Xello reflection has three separate three-line response areas; sentence reasoning is not placed in phrase-sized table cells.
- API/browser QA: the generic verifier passed all 18 consecutive items with no unresolved fields, missing file references, unsupported types, or published content. Signed-in Chrome confirmed the Day 2 licensed visuals and alt text, the complete Day 5 Xello teacher package, the Day 4 Quiz/Assignment route, and a clean 390-pixel student layout with no horizontal overflow. Canvas stripped CSS `aspect-ratio` from the optional BLS video; the builder now supplies explicit 760-by-428 dimensions and the live player renders at that size. Student View showed no modules because every module remains unpublished, and the test session was exited.
- Permissions QA: core folder 1155187 and Day 1-5 visual folders 1155188-1155192 all report `locked: true` through the Canvas API.
- Importer: `build/canvas/build_3sw_wk2.py`
- Read-only verifier: `build/canvas/qa_canvas_module.py 544301`

## 2026-08-08 - 3SW Week 3 paired lesson set

- Module: `3SW Wk3: Sustainable Engineering and Pest Patrol` (544302)
- State: unpublished
- The module contains five native Day `SubHeader` items, ten coordinated teacher/student pages, and three unpublished practice assignments in chronological order.
- Unpublished private assignments: `PRACTICE: Pest Patrol Drone Draft` (3093995), `PRACTICE: Sustainable Engineering Evidence Packet` (3093996), and `PRACTICE: Xello Set Goals Reflection` (3093997). The drone draft supports manual teacher-assigned peer review; automatic peer assignment is off. All three remain ungraded during review.
- Locked Canvas folders: core Week 3 1155193; Day 1 1155194; Day 2 1155195; Day 3 1155196; Day 4 1155197; Day 5 1155198.
- Core artifact file IDs: career/problem guide 14561503, Pest Patrol field notes 14561504, drone design brief 14561505, peer review and revision record 14561506, societal-trends evidence 14561507, societal-trends evaluation 14561508, major rubric 14561509, and Xello goals plan 14561510.
- Xello sequence correction: Day 5 protects the required Grade 8 `Set goals` activity for 20 minutes and requires at least two saved goals. The licensed `My Goals` guide is an extended 25-30 minute route that asks for three goals; the live Completion Standards configuration controls the district minimum.
- Xello resource packaging: licensed `goals.pdf` is Canvas file 14561511 in the locked Week 3 support folder and is embedded on the teacher page. No aligned Xello student video, deck, worksheet, or student-interface screenshots were present in the captured package, so the student page uses explicit native Canvas directions rather than invented assets.
- Licensed FYF visuals: five workbook crops are stored only in locked Canvas Day 2-5 folders as files 14561512-14561516. They remain gitignored and are not part of the source backup.
- Career and trends evidence correction: fixed dated BLS, USDA, EPA, and NASA evidence replaces open searching and distinguishes salary measure, geography, preparation, outlook, and limitations. H&amp;L remains optional rather than load-bearing.
- Canvas interaction review: Day 3 uses a private draft assignment, Day 4 supports intentional manual peer review with paper/self/teacher alternatives, and Day 5 uses a private Xello reflection. Students do not post personal Xello goals or profile screenshots publicly.
- Grading: the final drone design, revision record, and societal-trends evaluation form a recommended student-visible 16-point major evidence packet. Platform choice, artwork polish, and peer-review availability do not determine the score.
- Worksheet QA: eight PDFs were rendered and visually inspected. Multi-sentence prompts use full-width ruled areas, the drone sketch has a dedicated full page, peer feedback and revision decisions have separate writing fields, and the goal plan gives each goal, task, obstacle, backup, and reflection its own usable space.
- API/browser QA: the generic verifier passed all 18 consecutive items with no unresolved fields, missing file references, unsupported types, or published content. Signed-in Chrome confirmed the Day 2 workbook visuals, Day 3 disclosure panels, Day 4 teacher guide, and a 390-pixel student layout without horizontal overflow. Student View correctly hid the unpublished module.
- Importer: `build/canvas/build_3sw_wk3.py`
- Read-only verifier: `build/canvas/qa_canvas_module.py 544302`

## 2026-08-08 - 3SW Week 4 paired lesson set

- Module: `3SW Wk4: Culinary Arts and Hospitality` (544304)
- State: unpublished
- Teacher item IDs: Day 1 5311294, Day 2 5311298, Day 3 5311302, Day 4 5311305, Day 5 5311308
- Student item IDs: Day 1 5311295, Day 2 5311299, Day 3 5311303, Day 4 5311306, Day 5 5311309
- Native Day `SubHeader` items: 5311293, 5311297, 5311301, 5311304, 5311307. The module uses one chronological route: day header, teacher guide, student guide, then that day's interaction when present.
- Unpublished Canvas student-annotation Assignment: `PRACTICE: Culinary Twist Menu Design` (3093999, item 5311296). It annotates the supplied menu brief and also accepts file upload or text entry. Paper, Canva, and Adobe Express remain equal routes because Canvas identifies file/text entry as the more accessible commenting route.
- Unpublished Classic practice Quiz: `PRACTICE: Motivation Check` (281855, item 5311300). Four multiple-choice questions provide immediate feedback and unlimited retries on intrinsic/extrinsic motivation, individual response to incentives, and salary-measure labels.
- Unpublished private Assignment: `PRACTICE: Hospitality Career and Business Recommendation` (3094000, item 5311310). It remains ungraded until the live Minor assignment group and 40/60 weighting are verified.
- Locked Canvas folders: core Week 4 1155199; Day 1 1155201; Day 2 1155202; Day 3 1155203; Day 4 1155204; Day 5 1155205.
- Core artifact file IDs: career evidence 14561537, Culinary Twist brief 14561538, motivation comparison 14561539, Hotel Rescue cards 14561540, Hotel Rescue response 14561541, Cater and Create brief 14561542, recommendation 14561543, and rubric 14561544.
- Licensed FYF visuals: ten workbook crops are stored only in locked Canvas Day 1-5 folders as files 14561546-14561555. They remain gitignored and are not part of the source backup.
- Sequence correction: Xello Decision Making, eDynamic 6.1, H&amp;L App Exploration, and Restaurant Rebrand are optional extensions. No required Grade 8 Xello task is displaced or invented in this placement.
- Career evidence correction: the fixed three-career guide uses May 2024 BLS U.S. medians, common preparation, 2024-34 outlook, annual openings, and work conditions for Chef or Head Cook, Lodging Manager, and Meeting/Convention/Event Planner. No figure is called DFW-localized or starting pay.
- Program correction: local planning language uses current Irving ISD Culinary Arts, Hospitality Services, Lodging and Resort Management, and FireBird Cafe Catering wording without promising admission, credentials, jobs, or salary.
- Safety and privacy correction: students design fictional menu and event concepts without preparing food, guaranteeing allergen safety, collecting real client information, or making unverified hotel promises. Hotel Rescue requires each student to produce individual role and transfer evidence.
- Grading: Day 5 is a recommended student-visible 16-point minor. Daily designs, Quiz attempts, tool choice, public speaking, art polish, and team availability do not become separate grades.
- Worksheet QA: eight PDFs totaling twenty-one pages passed strict rendering with zero warnings, text extraction, page-count checks, and visual inspection. Sentence reasoning uses full-width ruled areas, the menu and event briefs reserve full pages for labeled design work, team and individual Hotel Rescue evidence are separated, and the final five-to-seven-sentence recommendation has ten writing lines.
- Image-performance pilot: the decorative/full-page Day 1 opener was reduced from 789,795 bytes to 338,898 bytes while retaining a readable 935-by-1210 image. The original remains in the licensed local archive. Canvas lazy-loads the optimized image only when it approaches the viewport; detail-heavy workbook crops were not blindly batch-compressed.
- API/browser QA: the generic verifier passed all 18 consecutive items with no unresolved fields, missing file references, unsupported types, or published content. Signed-in Chrome confirmed the annotation submission modes, all four Quiz questions, Day 1 lazy-loaded visuals and alt text, Day 5 teacher resources, and a 390-pixel student layout without horizontal overflow. Student View showed no modules because all course modules remain unpublished, and the test session was exited.
- Importer: `build/canvas/build_3sw_wk4.py`
- Read-only verifier: `build/canvas/inspect_3sw_wk4.py` and `build/canvas/qa_canvas_module.py 544304`

## 2026-08-08 - 3SW Week 5 paired lesson set

- Module: `3SW Wk5: Style, Service, and Cosmetology Careers` (544308)
- State: unpublished
- Teacher item IDs: Day 1 5311349, Day 2 5311352, Day 3 5311355, Day 4 5311359, Day 5 5311362
- Student item IDs: Day 1 5311350, Day 2 5311353, Day 3 5311356, Day 4 5311360, Day 5 5311363
- Native Day `SubHeader` item IDs: 5311348, 5311351, 5311354, 5311358, 5311361. The module uses one chronological route: day header, teacher guide, student guide, then that day's interaction when present.
- Unpublished Classic practice Quiz: `PRACTICE: Texas Cosmetology License and Safety Check` (quiz 281856, item 5311357). Five multiple-choice questions provide immediate feedback and unlimited retries on licensing, source boundaries, and classroom safety.
- Unpublished private Assignment: `PRACTICE: Cosmetology Career and Business Recommendation` (3094012, item 5311364). It remains ungraded and accepts file upload, text entry, or media recording; paper remains equal.
- Locked Canvas folders: core Week 5 1155206; Day 1 1155207; Day 2 1155208; Day 3 1155209; Day 4 1155210; Day 5 1155211.
- Core artifact file IDs: SFX concept/lab brief 14561572, quality revision 14561573, Texas evidence guide 14561574, pathway decision 14561575, salon/wellness campaign 14561576, recommendation 14561577, and minor rubric 14561578.
- Licensed FYF visuals: nine workbook images are stored only in locked Canvas Day 1-5 folders as files 14561579-14561587. They remain gitignored and are not part of the source backup.
- Sequence correction: Xello Career Factors, eDynamic 4.2, H&amp;L exploration, and the workbook's student-enterprise prompts are optional context. No supplemental platform task displaces required Grade 8 Xello work.
- Licensing and program correction: the fixed guide uses current TDLR requirements and the current Irving ISD campus list. It does not present cosmetology apprenticeship as a Texas operator-license route or promise local cost, schedule, transportation, admission, hours, credentials, jobs, or salary.
- Safety and privacy correction: the core SFX build is dry relief or digital. Optional adhesive work requires a teacher-cleared material and operating plan; no classroom material goes on a student's skin, hair, clothing, face, or body. The wellness campaign uses a fictional business and remains private, with no diagnosis, treatment advice, guaranteed result, real account, or personal disclosure.
- Grading: Day 5 is a recommended student-visible 16-point minor. The SFX build route, art polish, Quiz attempts, platform access, and partner availability do not determine the score.
- Worksheet QA: seven PDFs totaling sixteen pages passed strict rendering with zero warnings, text extraction, page-count checks, and visual inspection. Sentence and multi-part reasoning use separate full-width ruled fields, and the concept map, revision drawing, business sketch, campaign post, and six-to-eight-sentence recommendation have proportional space.
- Image-performance QA: all nine delivery images are 144,771-260,856 bytes at 1,148 by 1,485 pixels, use native lazy loading, and remain readable at an approximately 344-pixel mobile display width. Desktop and 390-pixel checks found no horizontal overflow. No further Week 5 compression is warranted; the measurements are recorded in `canvas-image-performance-backlog.md` for comparison with the first-six-weeks audit.
- API/browser QA: the generic verifier passed all 17 consecutive items with no unresolved fields, missing file references, unsupported types, or published content. Signed-in Chrome confirmed teacher monitoring/key disclosures, student alt text and linked artifacts, all five Quiz questions, the private Assignment submission routes, progressive image loading, and clean desktop/mobile rendering. Student View remains protected by the unpublished module state.
- Importer: `build/canvas/build_3sw_wk5.py`
- Read-only verifier: `build/canvas/qa_canvas_module.py 544308`

## 2026-08-08 - 3SW Week 6 paired lesson set

- Module: `3SW Wk6: Build, Test, and Pitch a Business Idea` (544318)
- State: unpublished
- Teacher item IDs: Day 1 5311386, Day 2 5311389, Day 3 5311392, Day 4 5311396, Day 5 5311399
- Student item IDs: Day 1 5311387, Day 2 5311390, Day 3 5311393, Day 4 5311397, Day 5 5311400
- Native Day `SubHeader` item IDs: 5311385, 5311388, 5311391, 5311395, 5311398. The route remains day header, teacher guide, student guide, then the day's interaction.
- Unpublished Classic practice Quiz: `PRACTICE: Entrepreneurship Evidence Check` (quiz 281857, item 5311394). Five questions provide immediate feedback and unlimited retries on opportunity structure, customer evidence, Abandon It, source labels, and revenue.
- Unpublished private Assignment: `DRAFT: Entrepreneurship Portfolio` (3094018, item 5311401). It remains ungraded and accepts file upload, text entry, or media recording until the Major assignment group and 40/60 weighting are verified.
- Locked Canvas folders: core Week 6 1155212; Day 1 1155213; Day 2 1155214; Day 3 1155215.
- Core artifact file IDs: opportunity guide 14561631, idea support packet 14561632, venture/pitch record 14561633, living-cost guide 14561634, budget/Scholarship plan 14561635, and portfolio rubric 14561636.
- Xello file IDs: English Scholarships Guide 14561637 and Spanish Scholarships Guide 14561638. The official 2:02 Xello student video is embedded from its supplied YouTube player.
- Licensed FYF visuals: five small workbook JPEGs are stored only in locked Canvas folders as files 14561639-14561643. They remain gitignored and are not part of the source backup.
- Sequence correction: Day 5 protects the required Grade 8 Scholarship profile for 20 minutes. Save careers is not repeated. Teachers verify the Completion Standards report; students do not submit profile screenshots or private answers.
- Source correction: the budget uses the MIT Dallas County one-adult/no-children scenario updated February 15, 2026. The $3,450 monthly amount is a rounded living-cost scenario, not DFW starting pay, a salary guarantee, or tax advice. H&amp;L salary is not load-bearing.
- Program correction: the teacher guide uses current Irving ISD Business program names and treats workbook district pages as historical context without promising admission, credentials, placements, or salary.
- Interaction review: a Quiz saves time on bounded misconceptions; the final portfolio stays private; no Discussion exposes student ideas, budgets, or scholarship information. Live, recorded, private, and written pitch routes use the same evidence.
- Grading: the individual four-criterion 16-point portfolio is the recommended major. Group attendance, class popularity, public-speaking confidence, design polish, platform access, and the venture verdict do not determine the score.
- Worksheet QA: six PDFs totaling seventeen pages passed strict rendering with zero warnings and visual inspection. The first render exposed orphaned response lines; the final layout uses deliberate page breaks, short fields for short phrases, separate calculation cells, and full-width space for multi-sentence reasoning.
- Image-performance QA: all five delivery images are 116-262 KB. Desktop and 390-pixel browser checks found no horizontal overflow. Canvas did not preserve the source `loading="lazy"` attribute in the rendered DOM, so this module relies on small, targeted delivery files rather than assumed lazy loading.
- API/browser QA: the generic verifier passed all 17 consecutive items with no unresolved fields, missing file references, unsupported item types, or published content. Signed-in Chrome confirmed the module heading, teacher/student link, official Xello video and PDF routes, image alt text and dimensions, and clean desktop/mobile rendering.
- Importer: `build/canvas/build_3sw_wk6.py`
- Read-only verifier: `build/canvas/qa_canvas_module.py 544318`

## 2026-08-08 - 4SW Week 1 paired lesson set

- Module: `4SW Wk1: Build Your Mid-Year Career Blueprint` (544320)
- State: unpublished
- The module contains five native Day `SubHeader` items, ten coordinated teacher/student pages, one unpublished Student Annotation assignment, and one unpublished private Blueprint assignment in a 17-item chronological route.
- Unpublished annotation Assignment: `PRACTICE: Career Iceberg Annotation` (3094020, item 5311442). It annotates the supplied Career Iceberg PDF and also accepts file upload or text entry. Paper, typed labels, drawing, and oral/media routes remain equal evidence routes.
- Unpublished private Assignment: `DRAFT: Mid-Year Career Blueprint` (3094021, item 5311452). It remains ungraded and accepts file upload, text entry, or media recording until the live Major assignment group and 40/60 weighting are verified.
- Locked Canvas folder: core Week 1 1155217. The four Day visual folders are also locked. Delivery files remain available inside unpublished pages because individual file locks prevent the embedded visuals from rendering even in teacher preview; the locked parent folders and unpublished content are the access boundary during review.
- Core artifact file IDs: Profile Audit 14561654, Career Iceberg 14561655, Career Deep Dive 14561656, Pathway and CTSO Decision 14561657, Mid-Year Career Blueprint 14561658, and rubric 14561659.
- Licensed FYF visuals: seven focused workbook JPEGs are stored only in the locked Canvas Day folders as files 14561660-14561666. They remain gitignored and are not part of the public source backup.
- Sequence correction: supplemental Xello Quick Sims and the unverified eDynamic 8.1 unit were removed from the required path. H&amp;L and Xello may supply student-selected evidence but are not login-dependent completion gates. No private profile screenshot is required.
- Standards correction: d(5)(D) was removed because salary research is not a personal budget. Day 3 now carries d(8)(B) through documented preparation, pay, outlook, and source labels; Day 4 retains d(3)(F) through a specific CTSO preparation benefit without promising a local chapter.
- Current-local correction: Irving ISD High School CTE and 2026-27 course-description pages control program names. TEA's CTSO list establishes recognized organizations but not campus availability.
- Grading: Days 1-4 are formative. Day 5 is the recommended student-visible 16-point major; self-evidence, source accuracy, pathway reasoning, and a realistic next action are scored. Grammar, art, accent, platform access, and submission mode do not determine the score.
- Worksheet QA: six PDFs totaling nineteen pages passed strict rendering with zero warnings and visual inspection. The iceberg receives a full page, multi-sentence prompts use full-width ruled areas, and short phrase fields are not used for paragraph-length reasoning.
- Image-performance QA: all seven delivery images are 92-193 KB. Desktop and 390-pixel checks found no horizontal overflow; images display at about 342 pixels on mobile and load as the student reaches them. The downloadable packet preserves the readable text route.
- API/browser QA: the generic verifier passed all 17 consecutive items with no unresolved fields, missing references, unsupported item types, or published content. Signed-in Chrome confirmed module order, embedded visuals and alt text, the annotation and Blueprint submission routes, disclosure headings, and clean desktop/mobile rendering. Canvas produced only its own non-blocking publishing-context warning.
- Importer: `build/canvas/build_4sw_wk1.py`
- Read-only verifier: `build/canvas/qa_canvas_module.py 544320`

## 2026-08-08 - 4SW Weeks 2-6 pre-import production record

- State: local production complete; Canvas import and API/browser verification pending. All importers create unpublished modules, pages, assignments, quizzes, and locked support folders.
- Week 2: `4SW Wk2: Build a Counseling-Ready High School Plan`. Five paired guides, one retryable decision Quiz, one annotation activity, and one private plan Assignment. The course plan is counseling-ready evidence, not a promise of admission, credit, or scheduling.
- Week 3: `4SW Wk3: Aviation Routes, Systems, and Action Planning`. Five paired guides, one retryable survey/evidence Quiz, one design-lab Assignment, and one private action-plan Assignment. Military and civilian routes remain distinct; no student flight or private profile screenshot is required.
- Week 4: `4SW Wk4: Drone Systems, Rules, and Iteration`. Five paired guides, two retryable rule/evidence Quizzes, two annotation Assignments, and one private evidence brief. Indoor live, simulator, and tabletop routes are equal; no outdoor flight is authorized by the lesson.
- Week 5: `4SW Wk5: Automotive Evidence and Training Routes`. Five paired guides, two retryable evidence Quizzes, two annotation Assignments, and one private evidence brief. Vehicle cases are fictional visible-evidence exercises, not diagnosis or repair directions.
- Week 6: `4SW Wk6: Skills That Transfer and Mid-Year Evidence`. Five paired guides, two retryable evidence Quizzes, two annotation Assignments, and one private multimodal reflection. SkillsUSA/TSA are identified as CTSOs, NSPE/AOPA as professional associations, ASE as a credentialing nonprofit, and FAA as a federal agency.
- Worksheet-space QA: all Week 2-6 packets were generated in strict mode and visually inspected. Multi-sentence reasoning has full-width ruled space or dedicated response pages; short fields are reserved for short evidence labels. Canvas annotation, upload, typed, media, and paper routes are offered only where the evidence remains equivalent.
- Image-performance QA: Week 2-6 use targeted delivery images rather than full-resolution source pages. Baselines and post-import mobile checks are tracked in `canvas-image-performance-backlog.md`; originals remain unchanged in the licensed local archive.
- Importers: `build/canvas/build_4sw_wk2.py` through `build/canvas/build_4sw_wk6.py`.

## 2026-08-08 - 5SW Week 1 local production record

- Module target: `5SW Wk1: Blueprint Builders — Architecture Evidence`.
- State: facilitator/student sequence, six core artifacts, paired templates, and Canvas importer complete locally; API/browser verification pending.
- Sequence correction: no repeated Xello Education experiences task, required H&amp;L favorite count, or unverified eDynamic 3.1 block. Supplemental platforms cannot displace the fixed evidence or design work.
- Structure correction: Days 3-4 protect one individual Tinkercad or equal paper concept instead of colliding with a second required landmark product. Day 5 uses Unexpected Architecture as a short group synthesis with individual evidence.
- Current-evidence correction: Day 2 compares Architect, Drafter, and Interior Designer with May 2024 U.S. BLS medians and preparation labels. Architecture registration uses education, documented experience, and examination rather than one universal year count.
- Privacy/safety correction: Tinkercad uses a teacher-managed Classroom/class-code route; no universal minor self-signup or public full-name filename. Safety Supervisor is explicitly fictional and non-operational.
- Worksheet QA: six PDFs totaling twenty-two pages pass strict rendering with zero warnings. The first visual pass caught spilled drawing boxes and an unusably shallow two-view table; the corrected render gives top/front/side drawings dedicated pages and multi-sentence reasoning full-width lines.
- Licensed delivery media: seven optimized images are stored only in the gitignored Canvas-licensed folder. The sideways city-goals slide was rendered, rotated in the delivery copy, and visually verified without changing the source PPTX.
- Canvas interaction plan: Day 1 Safety Supervisor annotation, Day 2 unlimited-retry career-evidence Quiz, Day 3 concept annotation, Day 4 test/revision annotation, and Day 5 private multimodal portfolio. The importer creates five native Day subheaders and ten paired pages in a 20-item chronological route.
- Importer: `build/canvas/build_5sw_wk1.py`.

## 2026-08-08 - 5SW Week 2 local production record

- Module target: `5SW Wk2: Civil Engineering — Systems, Evidence, and Design`.
- State: facilitator/student sequence, six core artifacts, paired templates, and Canvas importer complete locally; API/browser verification pending.
- Current-evidence correction: Day 1 uses the May 2024 BLS Civil Engineers U.S. median, typical preparation, 2024-34 outlook, annual openings, and a bounded licensure statement. It distinguishes the current public MacArthur `Engineering` label from the 2026-27 IISD coursebook's `Civil Engineering` label instead of forcing either into a promise.
- Assessment correction: Day 2 replaces outdated test-card claims with bounded PSAT 8/9, SAT/ACT, TSIA2, and ASVAB uses plus an explicit verification question. The retryable Quiz corrects PSAT 8/9 timing/admissions, enhanced ACT science, TSIA2 exemptions, and emerging-work evidence.
- Emerging-work correction: students compare the recognized O*NET Transportation Engineers and Water/Wastewater Engineers specialties, identify the driver for change, and state one evidence limitation. No invented futuristic title or unlabeled DFW salary is required.
- Safety/equity correction: the bridge activity uses one staged-load and stop protocol only if the full safety gate passes. Textbooks, unstable desks, student load placement, improvised scales on the bridge, public team ranking, and an unmeasured strength-to-weight ratio are excluded. The fictional three-sample dataset is an equal evidence route.
- Worksheet QA: six PDFs totaling twenty-seven pages passed strict rendering with zero warnings and visual inspection. Each bridge option has separate full-size top and side views; the kitchen system and fictional rover each have dedicated drawing pages; multi-sentence reasoning receives full-width ruled space.
- Licensed delivery media: five focused progressive JPEGs are stored only in the gitignored Canvas-licensed folder. Each is 102-240 KB; the original FYF PDF is unchanged.
- Canvas interaction plan: Day 1 systems annotation, Day 2 unlimited-retry assessment/evidence Quiz, Day 3 two-option design annotation, Day 4 controlled-test/fixed-data annotation, and Day 5 private multimodal portfolio. The importer creates five native Day subheaders and ten paired pages in a 20-item chronological route.
- Importer: `build/canvas/build_5sw_wk2.py`.

## 2026-08-08 - 5SW Week 3 local production record

- Module target: `5SW Wk3: Construction — Routes, Evidence, and Observation`.
- State: facilitator/student sequence, six core artifacts, paired templates, locked visual set, and Canvas importer complete locally; API/browser verification pending.
- Current-program correction: MacArthur's current public pathway label is Construction within the School of Architecture, Construction and Civil Engineering. Older workbook Construction Technology, NCCER, SkillsUSA, credential, and facility claims are historical context unless a current district source confirms them.
- Route correction: Registered Apprenticeship is taught through its stable paid-work, instruction, mentoring, progressive-wage, and portable-credential structure. Eligibility, duration, wage, cost, schedule, application, and license relationship remain sponsor- and trade-specific; students compare dated route cards without submitting real applications or personal data.
- Labor-evidence correction: Day 3 uses one May 2024 U.S. BLS wage basis and 2024-34 national projection basis. The high-skill/high-wage/high-demand labels are explicitly a transparent classroom comparison rule, not official BLS/TWC designations or proof of a DFW shortage.
- Safety and professional-boundary correction: Days 4-5 are fictional visual-evidence exercises. Students separate observation, possible meaning, evidence limit, and next qualified role; they do not inspect a home, touch equipment, diagnose a defect, estimate repairs, or advise a purchase.
- Worksheet QA: six PDFs totaling thirty-one pages passed strict rendering with zero warnings and visual inspection. Each classified occupation, image record, and report finding has its own page; multi-sentence reasoning and the individual briefing have full-width writing space.
- Licensed delivery media: five original Climber Notes source photos and one focused FYF thermal-comparison page are stored only in the gitignored Canvas-licensed folder. The six JPEG delivery copies are 145-340 KB; the PPTX and workbook originals are unchanged.
- Canvas interaction plan: Day 1 career-evidence annotation, Day 2 route/organization annotation, Day 3 labor-classification annotation, Day 4 visual-observation annotation with six embedded licensed visuals, and Day 5 private multimodal report/briefing. The importer creates five native Day subheaders and ten paired pages in a 20-item chronological route.
- Grading boundary: Day 3 is Minor 3 in the locked 5SW map. Day 5 is formative. Both remain unpublished and ungraded until the review gate and Minor-group configuration are verified.
- Importer: `build/canvas/build_5sw_wk3.py`.

## 2026-08-08 - 5SW Week 4 local production record

- Module target: `5SW Wk4: Skilled Trades — Evidence, Routes, and Communication`.
- State: facilitator/student sequence, six core artifacts, paired templates, eight locked licensed visuals, and Canvas importer complete locally; API/browser verification pending.
- Current-evidence correction: Electrician, Plumbing/Pipefitting/Steamfitting, HVAC, and Welding use one May 2024 U.S. BLS median basis and 2024-34 national projection basis. H&amp;L is supplemental and does not supply load-bearing DFW pay.
- Route correction: occupation, Registered Apprenticeship, technical-college route, state registration/license, and employer credential remain distinct. Day 4 uses dated Apprenticeship.gov and Dallas College route cards; students never submit a real application or personal data.
- Safety/professional-boundary correction: HVAC tickets are fictional image-writing exercises, not diagnosis or repair directions. The water-line plan is a communication/evidence simulation; students do not locate utilities, enter a street, direct traffic, operate a valve, excavate, select materials, use tools, or write a real repair procedure.
- Workbook-model correction: FYF p.186 is embedded with an explicit warning that its stronger diagnosis/action language is not the scoring model. The CCE form requires supplied evidence, cautious possibility, evidence limit, and qualified next check.
- Worksheet QA: six PDFs totaling twenty-eight pages passed strict rendering with zero warnings and visual inspection. The first render exposed three nearly blank overflow pages; the final packets intentionally use one full page per HVAC ticket, one landscape page per labor classification, a dedicated site-plan sketch page, and full-width multi-sentence response blocks.
- Licensed delivery media: four original Climber Notes ticket images and four focused FYF pages are stored only in the gitignored Canvas-licensed folder. Day 2 carries six images totaling about 1.04 MB; Day 5 carries two images totaling about 380 KB. Source PPTX/workbook files remain unchanged.
- Canvas interaction plan: Days 1-4 use private Student Annotation/upload/text activities. Day 5 uses a private multimodal response with live, teacher-conference, audio, recorded, equivalent written, and AAC briefing routes. The importer creates five native Day subheaders and ten paired pages in a 20-item chronological route.
- Grading boundary: Days 3 and 5 combine as Major 1 in the locked 5SW map. Both remain unpublished and ungraded until the Major group, 60% weighting, combined rubric, and review gate are verified.
- Importer: `build/canvas/build_5sw_wk4.py`.

## 2026-08-08 - 5SW Week 5 local production record

- Module target: `5SW Wk5: MoneySkills — Budget, Location, and Career Evidence`.
- State: facilitator/student sequence, six core artifacts, paired templates, two locked licensed workbook reminders, one retryable practice Quiz, and Canvas importer complete locally; API/browser verification pending.
- Sequence correction: the week does not repeat Xello Scholarship profile, add a supplemental Xello Careers and Lifestyle Costs lesson, or require H&amp;L. Xello is the preferred source for a separately labeled local salary cross-check; fixed evidence carries every lesson when a login or comparable local measure is unavailable.
- Salary correction: no page converts a median, starting figure, range, national value, or local value into another measure. The final three-career fallback uses May 2024 U.S. BLS medians on one comparison basis and keeps the Dallas County living-cost target separate.
- Living-cost correction: Days 2-3 use MIT Living Wage Calculator scenarios updated February 15, 2026. Dallas, Tulsa, Los Angeles, and New York County all hold the household at one adult with no children. The figures are instructional scenarios, not personalized financial advice or claims that one location is best.
- Aid/privacy correction: Day 4 distinguishes FAFSA application, eligibility, aid offer, acceptance, and repayment. It teaches the current Texas FAFSA/TASFA/authorized opt-out routes without requiring any real application or collecting SSNs, tax data, family income, immigration information, FSA IDs, banking information, or signatures.
- Interaction plan: Days 1-3 use private annotation/upload/text activities; Day 4 uses a five-question unpublished unlimited-retry Classic practice Quiz with immediate feedback; Day 5 uses a private upload/text/media portfolio. No public Discussion exposes financial priorities or family circumstances.
- Worksheet QA: six PDFs totaling twenty-nine pages passed strict rendering with zero warnings and final visual inspection. Initial renders exposed nearly blank overflow pages; the corrected set reserves short fields for labels and calculations while each budget tradeoff, location recommendation, career comparison, and revision receives a dedicated full-width response area.
- Licensed delivery media: two prior FYF Rung 3 reminder pages are reused from the gitignored Canvas-licensed archive at 105 KB and 172 KB. Canvas labels them as optional reminders, not current salary proof; the original workbook remains unchanged.
- Grading boundary: Day 5 is Major 2 in the locked 5SW map and remains unpublished and ungraded until the Major group, 60% weighting, and review gate are verified. Career preference, family income, Quiz attempts, grammar, and submission mode do not determine the score.
- Canvas package: five native Day subheaders, ten paired teacher/student pages, and five interactions in a 20-item chronological route. All local page renders passed with no unresolved template fields.
- Importer: `build/canvas/build_5sw_wk5.py`.

## 2026-08-08 - 5SW Week 6 local production record

- Module target: `5SW Wk6: Real Estate — Licensing, Variable Income, and Evidence`.
- State: repaired five-day sequence, six core artifacts, paired templates, three locked licensed FYF visuals, one five-question retryable practice Quiz, and Canvas importer complete locally; API/browser verification pending.
- Xello/platform correction: duplicate Save careers was removed. H&amp;L and live housing/search sites are supplemental; no favorite, screenshot, or open-web fact hunt is load-bearing.
- Licensing correction: TREC is the current source of record. Sales Agent, Broker, Property Appraiser/Assessor, and Property Manager duties and regulatory boundaries remain separate. The current public Irving label is Real Estate Marketing at MacArthur; it does not promise admission, schedule, transportation, license completion, exam eligibility, placement, or employment.
- Compensation correction: classroom percentages and splits are explicitly fictional. Students distinguish transaction gross, supplied split, taxes/expenses/timing, and take-home rather than learning one negotiable commission as a universal standard.
- Labor correction: Day 4 uses May 2024 U.S. BLS medians of $56,320 for Sales Agents and $72,280 for Brokers, 3% combined growth for 2024-34, and about 46,300 annual openings. It states that BLS wage data exclude self-employed workers and that national evidence does not prove DFW starting pay, a live vacancy, shortage, or future home price.
- Licensed activity correction: *Flip This House* retains the workbook's $25,000 scenario and buyer evidence while labeling all costs/value increases as simplified fictional inputs. Students calculate net change, cite supplied buyer evidence, and state real-world limits; they do not use real addresses, family property, bids, appraisal, financing, tax, or purchase advice.
- Communication correction: Day 5 oral evidence uses private live, teacher-conference, audio, recorded, or AAC routes. A transcript may support planning, but written-only work is not automatically labeled d(4)(C) oral evidence. Public presentation is optional celebration only.
- Worksheet QA: six PDFs totaling twenty-eight pages passed strict rendering with zero warnings and visual inspection. The first render exposed accidental overflow pages in the rubric, ROI plan, and reflection; the final layout preserves full-width multi-sentence fields without blank spill pages.
- Licensed media: three progressive FYF JPEGs for pp. 238-240 are 130-240 KB each and appear only on Day 3. All required numbers and response jobs also appear in the accessible packet/native Canvas text.
- Grading boundary: Day 5 is recovery/replacement evidence only because the locked 5SW map already contains three minors and two majors. It remains unpublished and ungraded until a teacher authorizes a specific recovery use. Platform access, career preference, family finances, accent, public-speaking confidence, grammar, partner attendance, drawing quality, and submission mode do not determine the score.
- Canvas package: five Day subheaders, ten paired pages, and five interactions in a 20-item chronological route. All local renders passed without unresolved template fields.
- Importer: `build/canvas/build_5sw_wk6.py`.

## 2026-08-08 - 6SW Week 1 local production record

- Module target: `6SW Wk1: Education — Learning Design, Routes, and Service`.
- State: repaired five-day sequence, six core artifacts, paired templates, eight locked licensed FYF visuals, one five-question retryable practice Quiz, and Canvas importer complete locally; API/browser verification pending.
- Sequence correction: no new required Grade 8 Xello task belongs here. Discover learning pathways, H&amp;L exploration, and eDynamic 7.2 are supplemental only and cannot displace fixed evidence or create graded click requirements.
- Preparation correction: current TEA guidance supplies five common classroom-teacher requirements while university, post-baccalaureate, alternative, residency, internship, clinical, price, aid, and timing details remain provider-specific. The packet does not teach either route as universally cheaper, faster, paid, unpaid, easier, or better.
- Local correction: current Irving public evidence names Education and Training at Irving High, MacArthur, and Nimitz and Early Childhood Education at Cardwell. The page does not by itself guarantee admission, course sequence, travel, credential, placement, or employment. Educational Aide I retains its current TEA age/course/grade/credit/district/application/background boundaries.
- Job-evidence correction: Day 3 uses three fixed fictional posting cards rather than changing job-board searches. Students distinguish responsibility, skill, qualification, preparation, experience, and preferred language and state the evidence limitation.
- Safety/privacy correction: Teach Through Play has partner, tabletop, teacher-conference, and individual written-simulation routes. Physical performance, cutting skill, personal volunteer disclosure, platform access, artistry, and partner attendance are not scored.
- Worksheet QA: six PDFs totaling thirty-two pages passed strict rendering with zero warnings after oversized drawing boxes and declared-page mismatches were repaired. Visual inspection confirmed readable rubric text and full-width writing space for every multi-sentence job.
- Licensed media: eight FYF pages are 152-278 KB each at a 1,300-pixel long edge. Days 1, 4, and 5 carry only their relevant pages; native Canvas text and downloadable packets are the independent completion route.
- Grading boundary: Day 5 is Minor 1 in the locked 6SW map and remains unpublished/ungraded until the Minor group, 40% weighting, and review gate are verified.
- Canvas package: five Day subheaders, ten paired pages, and five interactions in a 20-item chronological route. All local renders passed without unresolved template fields.
- Importer: `build/canvas/build_6sw_wk1.py`.

## 2026-08-08 - 6SW Week 2 local production record

- Module target: `6SW Wk2: Arts/AV — First Resume and Design Evidence`.
- State: repaired five-day sequence, six core artifacts, paired templates, eight locked FYF visuals, one five-question retryable practice Quiz, and Canvas importer complete locally; API/browser verification pending.
- Resume correction: d(7)(A) no longer rests entirely on supplemental Xello. The required résumé is a private Canvas/paper artifact; optional Xello copying is an extension. Students do not exchange devices/logins or include home address, personal phone/email, birth date, IDs, photo, family data, or reference contacts.
- Workload correction: the required Game On group product was removed from the core week so students can plan one podcast, draft/revise one résumé, learn a complete job-search sequence, and build/test one original visual design. Arts enrichment remains available after required evidence.
- Job-search correction: Day 4 teaches seven distinct steps and uses a fictional opportunity. Students do not apply, register, upload, contact an employer, or submit personal data; job-board results are screened and verified through an official employer route or known adult.
- Copyright/platform correction: Behind the Microphone is a plan rather than a required public recording. Merch Mode uses original fictional identity; real band marks, album art, characters, and trademarks are excluded. Canva, Adobe Express, and paper are equal, while H&amp;L and eDynamic remain supplemental.
- Current evidence: current Irving pages name Graphic Design and Digital Communication at Irving High, MacArthur, and Nimitz. BLS Graphic Designers uses a May 2024 U.S. median of $61,300, typical bachelor's preparation, 2% 2024-34 growth, and about 20,000 annual openings; none is relabeled DFW starting pay or a guarantee.
- Worksheet QA: six PDFs totaling thirty-five pages passed strict rendering with zero warnings after declared-page mismatches were repaired. Visual checks confirmed a privacy-forward résumé first page and dedicated full-page design sketch regions.
- Licensed media: eight FYF delivery images are 137-307 KB at a 1,300-pixel long edge. Required content is repeated in native text and accessible packets.
- Grading boundary: Day 5 is Minor 2 in the locked 6SW map and remains unpublished/ungraded until the Minor group, 40% weighting, and review gate are verified.
- Importer: `build/canvas/build_6sw_wk2.py`.

## 2026-08-08 - 6SW Week 3 local production record

- Module target: `6SW Wk3: Marketing - Audience, Entrepreneurship, and Data`.
- State: repaired five-day sequence, six core artifacts, paired templates, eleven locked FYF visuals, one five-question retryable practice Quiz, and Canvas importer staged and verified in the live course. All objects remain unpublished for teacher transfer.
- Sequence correction: no new required Grade 8 Xello task belongs here. School Subjects at Work, H&amp;L exploration, eDynamic 4.1, Google Applied Digital Skills, Canva, and Adobe Express remain supplemental and cannot displace required evidence.
- Privacy/ethics correction: all campaigns, businesses, messages, prices, and data are classroom scenarios. Students do not create a real account, ad, post, sale, payment, contact form, link, QR code, testimonial, tracking claim, scarcity claim, or collection of personal data.
- Current-evidence correction: BLS Market Research Analysts uses a May 2024 U.S. median of $76,950, typical bachelor's preparation, 7% projected 2024-34 growth, and about 87,200 annual openings. Growth and openings remain distinct and none is relabeled DFW starting pay, a local shortage, or a guarantee.
- Data correction: the Family Fun Pass tables and quotes are labeled fictional workbook evidence. Students state a campaign goal before selecting a metric, compare three strategies, cite multiple values, identify conflicting evidence, and plan a next test; there is no teacher-preferred universal answer.
- Entrepreneurship correction: Expert Edge distinguishes need, audience, deliverable, opportunity, fictional unit/price, responsibility, risk, and control. Logo polish and oral delivery are optional and not scored.
- Worksheet QA: six PDFs totaling fourteen pages passed strict rendering with zero warnings. Days 1-4 each use one two-page companion only for evidence the FYF workbook does not collect. Day 5 uses a four-page brief and two-page rubric. All fourteen final pages passed visual review for readable hierarchy, proportional response space, point-of-use language support, and student-safe scoring language.
- Licensed media: eleven progressive FYF JPEGs for pp. 147-148 and 222-230 are 111-300 KB at a 1,300-pixel long edge. Required instructions/data also appear in native Canvas text and accessible packets.
- Grading boundary: Day 5 is Minor 3 in the locked 6SW map and remains unpublished/ungraded until the Minor group, 40% weighting, and review gate are verified.
- Canvas package: five Day subheaders, ten paired pages, one Quiz, and four private Assignments in a 20-item chronological route. All local renders passed without unresolved template fields.
- Importer: `build/canvas/build_6sw_wk3.py`.
- Owner-style release gate: all 20 responsive Canvas renders and all 14 printable pages passed after exact DOL capitalization was synchronized and rubric page 2 was clarified to require only the brief plus rubric/self-score. Earlier FYF work and companions remain reference evidence rather than extra uploads.
- Recoverable Git checkpoints: `50888760` (pre-staging package), `06e99c68` (submission-evidence clarification), and `9debbf1e` (release-gate closure).
- Live Canvas module: 544416, unpublished, with exactly 20 consecutive items. Ten Teacher/Student pages remain unpublished.
- Live practice: Classic Quiz 281902 is unpublished, unlimited-retry, and contains exactly five questions in the managed order. Assignments 3101883, 3101884, and 3101885 are unpublished, worth 0 points, and omitted from the final grade.
- Live Minor 3: assignment 3094808 remains unpublished, worth 100 points, counted in `Minor Assessments (40%)`, with exactly one durable submission panel on the Day 5 Student Guide.
- Locked files: support folder 1155261 contains six locked PDFs (14578331, 14578332, 14578333, 14578335, 14578336, 14578337); licensed-visual folder 1155262 contains eleven locked FYF JPEGs (14562719-14562729). Live generic and week-specific API verification returned no problems.

## 2026-08-10 - 6SW Week 4 sales, revision, and career-oral-evidence repair

- Reconciled the week to FYF 30 Seconds to Sell pp. 241-243, FYF BrainBoost pp. 244-247, the FYF Strengths Interview preview on pp. 280 and 299, and fixed dated career evidence. FYF remains the default student work surface. H&amp;L, Xello, eDynamic, public posting, live sales, and family-adult participation are not required.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. Day 2 carries transferable oral-revision evidence; Day 4 uses appropriate private technology for interview rehearsal; Day 5 carries the complete career oral-evidence brief.
- Repaired the oral-presentation boundary. A written outline or transcript may scaffold preparation but does not independently demonstrate d(4)(C). Live, teacher-conference, private audio/video, and authorized oral/AAC routes use the same evidence requirements; accent, speech difference, camera use, eye contact, public confidence, clothing cost, and English mechanics are not scored unless meaning is unclear.
- Replaced the impossible serial-presentation plan with bounded 60-90-second evidence built across the week. The Teacher Guides include ready-to-use appearance, source-label, and oral-route models, explicit monitoring look-fors, transition points, and a complete absence/platform route.
- Reduced the coordinated printable set from thirty pages to twelve intentional pages: six two-page artifacts with point-of-use bilingual vocabulary, complete response frames, and revision, rehearsal, and delivery space sized to the requested work. No artifact exposes teacher-only scoring guidance.
- Kept sales, campaign, and audience work fictional and private. Students do not sell, post, link, collect data, use real contact/payment information, or make unsupported health, income, popularity, scarcity, or career-pay claims. Fixed labor figures retain occupation, measure, date, U.S. geography, and limitation.
- Ran the required separate owner-style adversarial gate. The reviewer inspected all twenty responsive Canvas renders, all twelve PDF pages plus footer crops, exact contract parity, source/TEKS truth, EB supports, response space, appropriate-technology evidence, grade neutrality, and importer safeguards. Earlier oral-standard and lazy-render blockers were repaired; the final gate returned GO. Backup commit `68bd5fc8` was pushed before Canvas staging.
- Reconciled unpublished module 544417 to twenty consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, three private practice Assignments, one five-question practice Quiz, and the private formative Career Oral Evidence Brief. All ten pages, five interactives, and the module remain unpublished.
- Live API verification confirms practice assignments 3094809, 3094810, and 3102878 and formative assignment 3094812 are worth 0 points, omitted from the final grade, and unpublished. Quiz 281903 is unpublished, allows unlimited attempts, shows correct answers, and contains exactly five questions in the managed order. The Day 5 Student Guide contains exactly one durable submission panel.
- Live storage verification confirms support folder 1155263 and licensed-visual folder 1155264 are locked. All six support PDFs 14579336-14579341 and all nine FYF visuals 14562740-14562748 are locked. The expanded module verifier reports zero problems.
- Importer: `build/canvas/build_6sw_wk4.py`.

## 2026-08-08 - 6SW Week 5 local production record

- Module target: `6SW Wk5: Job Search, Applications, and Interviews`.
- State: repaired five-day sequence, six core artifacts, paired templates, one five-question retryable practice Quiz, and Canvas importer complete locally; API/browser verification pending.
- Privacy correction: the core week uses the complete fictional Pecan Creek Animal Care / Jordan Rivera case. Students never enter or submit a real address, phone/email, birth date, Social Security/student/driver ID, banking/tax/signature data, family data, availability constraints, protected information, or another person's contact information. No application, permission request, cover letter, thank-you note, or employer contact is sent.
- Platform correction: live job boards, FYF Rung 5, H&amp;L, and Xello Job Interviews are extensions only. They are not required evidence or district Xello completion standards and cannot make a login, changing posting, or real applicant record load-bearing.
- Correspondence correction: the cover letter and thank-you note use supplied facts, specific evidence, concise plain language, and visible revision. They do not reward invented enthusiasm, unsupported employer facts, inflated credentials/results, or generic formulaic prose.
- Reference correction: students identify appropriate reference roles and firsthand evidence without entering real names/contact information. Permission-before-sharing is explicit; the classroom permission request is drafted but not sent.
- Interview/access correction: appearance uses workplace, task, safety, format, technology, and accommodation context rather than expensive, gendered, body-based, cultural, religious, disability-based, eye-contact, handshake, or camera rules. Paired live, small group, teacher conference, private recording, and AAC routes are supported.
- Worksheet QA: six PDFs totaling thirty-nine pages passed strict rendering with zero warnings and visual inspection. Initial renders exposed three unintended continuation pages; the final set gives a full draft page to each letter, eight spacious application/reference pages, four pages for eight interview questions, and separate role/revision records.
- Grading boundary: Day 5 is Major 1 in the locked 6SW map and remains unpublished/ungraded until the Major group, 60% weighting, and review gate are verified. Accent, camera use, eye contact, clothing cost/style, disability, public confidence, English mechanics, and submission route are not grading criteria unless meaning is unclear.
- Canvas package: five Day subheaders, ten paired pages, one Quiz, and four private Assignments in a 20-item chronological route. All local content structures compile and render without unresolved fields.
- Importer: `build/canvas/build_6sw_wk5.py`.

## 2026-08-08 - 6SW Week 6 local production record

- Module target: `6SW Wk6: Career Evidence Capstone`.
- State: repaired flexible five-day sequence, six core artifacts, paired templates, eight locked licensed workbook visuals, and Canvas importer complete locally; API/browser verification pending.
- Missing-evidence correction: a lost old workbook page, incomplete family interview, H&amp;L failure, missing partner, or absent prior artifact triggers a documented fixed-source, staff-conference, role-card, or supervised-catch-up route. It does not automatically reduce mastery.
- Presentation correction: the former serial whole-class presentation plan could exceed the available schedule. The core route is a 2-3-minute individual brief through parallel small groups, teacher conference, private recording, AAC, or authorized multimodal evidence; whole-class delivery is optional celebration.
- Plan correction: the eight-page career plan distinguishes current evidence, career direction and alternative, task/work product, preparation, labeled labor evidence, current Irving connection, unresolved verification question, postsecondary/training boundary, three action goals, obstacle, backup, support, and flexible conclusion.
- Privacy/access correction: no private profile screenshot, address/contact/ID data, family finances, health/immigration information, family-adult dependency, public speech, camera, presentation platform, costly visual production, class photo, or pathway guarantee is required.
- Worksheet QA: six PDFs totaling thirty-six pages passed strict rendering with zero warnings and visual inspection. Every major evidence job receives a dedicated page; the first rubric render exposed one unintended continuation page and the final four-page landscape rubric fits cleanly.
- Licensed media: eight FYF orientation pages for pp. 277-280 and 297-300 are 112-241 KB each at readable delivery resolution. Native Canvas directions and the accessible packets independently carry every required evidence job.
- Grading boundary: Day 4 is Major 2 in the locked 6SW map and remains unpublished/ungraded until the Major group, 60% weighting, and review gate are verified. Missing prior artifacts, platform access, visual polish, public speaking, partner/family attendance, accent, eye contact, disability, camera use, English mechanics, and submission route are not mastery criteria unless meaning is unclear.
- Canvas package: five Day subheaders, ten paired pages, and five private Assignments in a 20-item chronological route. All local content structures compile and render without unresolved fields.
- Importer: `build/canvas/build_6sw_wk6.py`.

## 2026-08-08 - coursewide assessment-map lock

- Source of truth: `docs/resources/six-weeks-assessment-map.md`.
- Gradebook architecture: three equally weighted 100-point Minor entries in a 40% group and two equally weighted 100-point Major entries in a 60% group for every six weeks. Raw rubric totals convert through student-visible percentage tables before Canvas entry.
- Governance correction: weekly products not named in the map remain formative, rehearsal, enrichment, or teacher-approved recovery/replacement evidence. A complete rubric no longer makes a weekly product an automatic grade.
- Placement corrections: 1SW uses Wk0/Wk2/Wk4 minors and Wk3/Wk5 majors; 2SW retains the existing Wk3/Wk4/Wk5 minors and Wk1/Wk2 majors; 3SW uses Wk1/Wk4/Wk5 minors and Wk2/Wk3 majors; 4SW uses Wk3/Wk4/Wk5 minors and Wk1/Wk2 majors; 5SW uses Wk1/Wk2/Wk3 minors and Wk4/Wk5 majors; 6SW uses Wk1/Wk2/Wk3 minors and Wk5/Wk6 majors.
- Grade-inflation correction: 3SW Wk6, 5SW Wk6, and 4SW Wk6 are recovery/replacement artifacts rather than extra grades. 6SW Wk4 is structured rehearsal rather than a fourth minor or third major.
- 1SW scoring-tool repair: the Wk0, Wk2, Wk3, and Wk4 rubrics now use district performance-band language, publish exact raw-score-to-percent conversions, and match their Minor/Major placements. Four PDFs totaling eight pages passed strict rendering and visual inspection.
- Canvas gate: assignment groups, weights, 100-point assignments, attached rubrics, student-view submission routes, hidden keys, and absence/platform fallbacks must be verified before any mapped grade is published.

## 2026-08-08 - Canvas image optimization pilot

- Baseline: 284 Canvas-only raster assets totaling 100.3 MB; 68 files exceeded 500 KB and 9 exact-duplicate groups contained 19 redundant copies.
- Pilot: the 1SW Wk1 Day 1 manufacturing opener and seven 1SW Wk5 Day 2 email images now have quality-82 JPEG delivery copies at their original dimensions.
- Result: active pilot delivery weight fell from 7.99 MB to 1.65 MB, a 6.34 MB / 79.4% reduction. Side-by-side visual inspection confirmed readable workbook copy, email sender/domain clues, and task labels.
- Importer behavior: `build_wk1.py` and `build_wk5.py` prefer same-stem JPEG files and skip the larger PNG during upload. Originals remain available outside Git for regeneration.
- Next priority: consolidate exact shared IT/Xello images into one locked Canvas shared folder after unpublished-page reference testing; do not delete live Canvas files during the migration.

## 2026-08-08 - remaining-module import orchestration

- Added `build/canvas/import_remaining_unpublished.py` for 4SW Wk2 through 6SW Wk6, 17 unpublished module packages total.
- The orchestrator reads one token from standard input, passes it only through each child builder's standard input, redacts it from failure output, stops on the first failed build, and writes no credential or import-state file.
- 4SW Wk1 is intentionally excluded because it already exists in the live course. Individual week builders retain idempotent upsert behavior and remain the unit of retry.
- Local checks: script compiles; empty-input test exits 2 with `Canvas token required on stdin`; live import remains pending secure token input.
- The orchestrator now supports `--preflight` without a credential. The current pass confirms all 17 builders compile, all 18 coordinated 4SW-6SW teacher/student template pairs meet the scan-heading/semantic-callout/disclosure/no-legacy-tabs contract, and all 184 statically named local dependencies resolve before the token prompt. The dependency set includes 102 PDFs, 48 licensed JPEGs, and 34 HTML templates; dynamic page-number loops remain covered by each builder's asset-folder checks and the recorded visual manifests.

## 2026-08-08 - Canvas builder grading-label reconciliation

- Reconciled all 4SW-6SW teacher-guide evidence labels and Canvas activity titles against `docs/resources/six-weeks-assessment-map.md` before live import.
- 5SW now exposes Wk1/Wk2/Wk3 as Minor 1/2/3, Wk4 as the two-part Major 1, Wk5 as Major 2, and Wk6 as recovery/replacement evidence.
- 6SW now exposes Wk1/Wk2/Wk3 as Minor 1/2/3, Wk4 as formative oral rehearsal, Wk5 as Major 1, and Wk6 Day 4 as Major 2.
- All imported interactions remain unpublished and ungraded; the labels establish instructional intent but do not bypass live assignment-group, weight, rubric, or student-view verification.
- Validation uses `uv run --with httpx` because the system Python can compile the builders but cannot import them without the Canvas runtime dependency. Compile, rendered-content label checks, and `git diff --check` pass.
- Import preflight checked all 17 builder files and all 102 named worksheet PDFs. It caught and repaired the 5SW Wk6 licensed-visual path so the three FYF images resolve from `canvas-licensed/5sw/wk6/day3/` before any live API mutation.
- Live Canvas verification: course 98060 now contains empty `Minor Assessments (40%)` and `Major Assessments (60%)` groups. Weighted assignment groups are enabled and the reopened settings show 40, 60, and Total 100%. Existing and future assignments remain unpublished and have not yet been moved into these groups.

## 2026-08-08 - live Canvas structure and image check

- Opened the approved 1SW Wk0 Day 2 student reference and the live 4SW Wk1 Day 1 teacher/student pair through their module-item URLs. All checked pages and modules remain unpublished.
- The reference disclosure behavior is working: the 1,600 by 900 personality chart remains unloaded while its optional help section is closed, then loads at 888 by 500 pixels when the disclosure opens. This thin placeholder is expected lazy-loading behavior, not a missing image.
- The 4SW Wk1 teacher page exposes before-class prep, target/evidence, a complete 50-minute flow, monitoring/grading, sources, supports, platform/privacy, and absence guidance. Its matching student page exposes the core task, linked packet, evidence jobs, exit check, and absence route. The linked audit packet has a live Canvas file record and is 200 KB.
- Accessibility correction: the 4SW-6SW student template family now marks `Today you will`, `Exit check`, and `You are done when` as real level-three headings instead of bold text alone. Eighteen templates passed the structural check; all 4SW-6SW builders still compile, and MkDocs strict passes.
- Live first-six-weeks performance evidence: Canvas file 14519003 is still the 1.49 MB `manufacturing-chapter-opener.png`; the second Day 1 image is 172 KB. The visually approved JPEG delivery copy is 571 KB, but the authenticated browser upload control did not open its file chooser and no upload occurred. Keep the live page unchanged until the API importer or a browser with file-URL upload permission can upload the delivery copy and update the unpublished page reference.
- Canvas file preview verification limitation: normal Canvas file records open and expose filenames/sizes, but this browser connection blocks the signed CDN download target. Treat the record check as proof that the file exists, not as the final Student View download/print check.

## 2026-08-08 - remaining-builder external source check

- Extracted and checked all 109 unique external URLs used by the full set of 36 Canvas week builders, from 1SW Wk0 through 6SW Wk6.
- Three confirmed stale routes were repaired: Dallas College Construction Technology now uses `/study/construction-technology/`, Dallas College Electrical Technology uses `/study/electrical-tech/`, and TDLR Journeyman Electrician uses the current `/electricians/apply/individuals/journeyman-electrician.htm` route. All three replacements returned HTTP 200 and were verified against current official search results.
- Added `build/canvas/check_canvas_source_links.py` as a repeatable course-production check. It fails on confirmed 404/410 responses and separates 403/timeouts for manual review so BLS anti-automation responses are not mislabeled as broken teacher links.
- Current whole-course result: 109 checked, 65 directly reachable through the automated request, zero stale, and 44 manual-review responses. Forty-one are current BLS pages returning 403 to the checker; Autodesk and NIFA timed out; CDC returned 403.
- Manual browser follow-up on August 8 confirmed that the Autodesk Children's Privacy Statement loads at the linked route and is effective April 2026; it explicitly covers Tinkercad, school-authorized child access, and Classroom Safe Mode. The current CDC NERD Academy outbreak-investigation module, February 2026 NIFA specialty-crop automation page, and representative BLS Architect, Information Security Analyst, Veterinarian, and Agricultural and Food Scientist pages also loaded at their exact linked routes. Keep the remaining BLS 403 responses in the manual-review class rather than rewriting current official links to avoid an automated access policy.

## 2026-08-08 - bulk preflight and response-space verification

- Strengthened the credential-free 4SW-6SW preflight so it also scans every literal image tag emitted by the 17 remaining builders and 36 paired templates. The current pass verifies six literal image renderers and rejects any one that omits an `alt` attribute.
- Ran the worksheet source contract across all 250 worksheet Markdown files in strict dry-run mode. Parsing and declared-page validation completed with zero warnings through the isolated `uv` runtime documented in the production workflow.
- Rebuilt and visually inspected a representative high-writing-load set: the seven-page 5SW Wk3 visual-observation log, four-page 6SW Wk6 capstone rubric, and eight-page 6SW Wk6 individual career plan. Across nineteen pages, no heading, table, response area, or drawing region clipped or overlapped.
- Response-space findings: each inspection image receives a dedicated page with separate observation, possible meaning, evidence/confidence, and qualified-role blocks; the career plan gives each evidence job its own page and full-width ruled areas; the capstone rubric separates its performance matrix, band record, access/privacy boundary, teacher notes, and revision record across four landscape pages.
- Chromium refreshes PDF creation/modification metadata during a rebuild even when the rendered layout and file size are unchanged. The production workflow now calls out that distinction so a future agent does not mistake a timestamp-only binary change for a content revision.

## 2026-08-08 - coursewide unpublished-transfer verifier

- Added `build/canvas/qa_remaining_unpublished.py`, a read-only post-import verifier for the 17-module 4SW Wk2-6SW Wk6 batch. It derives the exact expected module names from the builders instead of maintaining a second hand-written title list.
- The verifier requires each expected module exactly once and rejects renamed/duplicate modules sharing the same six-weeks/week prefix; checks unpublished module, item, page, Quiz, Discussion, and Assignment state; checks consecutive item positions and Day 1-5 subheaders; requires one teacher and one student page per day; confirms each teacher page links to its paired student page; rejects unresolved template fields and legacy Canvas tabs; and checks the approved teacher/student scan labels, image alt text, file resolution, assignment submission routes, practice-Quiz questions, and locked parent folders.
- The bulk importer now runs this verifier automatically with the same stdin-only credential after all 17 builders complete. A build may create/update unpublished content, but it does not report a successful transfer unless the coursewide QA also passes. Browser, mobile, and Student View checks remain a separate human-visible publication gate.
- Both scripts pass formatting, lint, compilation, and credential-free preflight. The live API path remains intentionally unrun until the secure token prompt receives input.

## 2026-08-08 - teacher-facing status reconciliation

- Updated the public Resources Status page from its August 6 partial-build snapshot to the current Canvas-first state: 250 verified printable artifacts, paired production packages for all 36 weeks, live unpublished Canvas content through 4SW Wk1, and 17 remaining packages staged behind the import/QA gate.
- Reclassified a separate slide deck for every week as optional projection support rather than a duplicate required deliverable. Native Canvas pages carry the stable directions; licensed Climber Notes and Xello media are embedded only where they remove a real barrier.
- Replaced the stale list of "missing" position-paper, planning, trades, budget, résumé, interview, and capstone packets with the completed production sets. The universal student supplement is intentionally replaced by just-in-time Canvas/print routes.
- Marked the August 5 Day-1 readiness backlog as a historical baseline. Future agents must check the live status ledger, assessment map, build log, and filesystem before reopening an old missing-resource claim.

## 2026-08-08 - course orientation package

- Added an unpublished course-level orientation package so the quality of the daily guides does not depend on teachers or students already understanding the project. The package contains `TEACHER: CCE Course Launch Guide` in the existing unpublished Teacher Build module and a first-position `START HERE: CCE Course Orientation` module containing `STUDENT: Start Here - How CCE Works`.
- The teacher launch dashboard covers Modules-first navigation, the 40/60 three-minor/two-major boundary, Xello versus supplemental-platform roles, equipment/readiness checks, the publication sequence, Student View, equal fallbacks, currently visible optional integrations, and a short classroom-feedback record.
- The student page covers the one-route daily grammar, evidence/submission choices, private-information boundaries, absence/platform recovery, completion check, and recurring vocabulary. Required directions remain visible; only the glossary is disclosed.
- The bulk importer now builds orientation before the 17 remaining weeks. The read-only coursewide verifier requires the student orientation module first and unpublished, the Teacher Build module unpublished, both pages present/unpublished, the teacher-to-student link, the required scan labels, and no legacy tabs or unresolved fields.
- Live Canvas staging: created the unpublished `START HERE: CCE Course Orientation` module, attached `STUDENT: Start Here - How CCE Works` as its only unpublished item, and moved the module to the first course position. Added `TEACHER: CCE Course Launch Guide` to the existing unpublished `Teacher Build: Licensed Resources` module. The signed-in browser showed exactly one module, one student module-item link, and one teacher module-item link; both pages displayed the intended headings, route/fallback guidance, and unpublished state. The API importer remains responsible for idempotent reconciliation and the full coursewide verification pass.

## 2026-08-08 - live Canvas navigation audit

- Read-only Settings > Navigation inspection found that Home, Announcements, Assignments, Discussions, Grades, People, Pages, Files, Syllabus, Outcomes, Rubrics, Quizzes, Modules, and twenty district LTI links are all in the enabled list. Only TestOut, Flipgrid, MyLab and Mastering, Nearpod, Packback, and Cengage are disabled.
- This is a publication-gate risk, not an immediate change request. Pages and Files can bypass the Modules-first route, and the long enabled-LTI list adds choices that most CCR lessons do not use. The course is published and currently has enrolled students, so navigation must not be changed merely to simplify the teacher view.
- After the remaining unpublished modules import, run Student View and determine the smallest student-facing menu that still supports the course. Preserve Home, Modules, Grades, and any required live integration; evaluate Pages, Files, Quizzes, People, Outcomes, Rubrics, Syllabus, and unused LTIs individually. Record the before/after list and verify direct module links before saving any change.

## 2026-08-08 - unpublished course-home replacement

- Student View proved the current learner state: the Home page is the Modules index and reports `No modules have been defined for this course` because every curriculum module remains unpublished. The enabled Pages link opens the published `Welcome!` front page, which still contains `Grade / Subject` and `Teacher Name` placeholders, image-only button labels, and layout tables from the generic Bowie template.
- Added `Career and College Exploration Home` to the idempotent course-orientation builder and coursewide verifier. The replacement uses native headings and links, has no images or layout tables, launches Modules as the primary action, links the Student Start Here page and Grades, and carries absence/platform, grading, and privacy guidance without duplicating daily lesson directions.
- Staged the replacement page manually in Canvas and verified its unpublished state, three functional course links, heading structure, and desktop rendering. It is not the front page and is not visible to students. Replacing the current published front page remains a deliberate publication-gate action after the remaining modules, Student View, navigation, and enrolled-student impact are reviewed together.

## 2026-08-08 - Student View publication snapshot

- Student View currently shows no instructional modules because every curriculum module is intentionally unpublished. The learner navigation menu exposes Assignments, Discussions, Grades, People, Pages, Files, Syllabus, Quizzes, BigBlueButton, Collaborations, Zoom, Launchpad, Home Access, Office 365, Discovery Education, Canva, IXL, GradeCam, Lucid, McGraw Hill, and Extempore in addition to Home.
- Assignments reports no assignment groups and Discussions reports no topics to the test student. Files exposes only the old `course_image` and `template-images` folders; the locked `CCR Materials` licensed-resource tree is not visible through the learner Files index. The new replacement home page returns Access Denied in Student View, confirming its unpublished boundary.
- Syllabus is empty but displays three legacy `Assignments` groups and one `Imported Assignments` group at 0%, followed by the correct `Minor Assessments (40%)` and `Major Assessments (60%)` groups. This is learner-facing clutter to reconcile after verifying that the legacy groups contain no needed published work.
- Added executable read-only `build/canvas/qa_course_publication.py`. It snapshots the active front page, placeholder/layout-table risk, 36-week module inventory, published module state, orientation/teacher boundary, active navigation tabs, assignment groups, replacement home page, and published pages. It is separate from the unpublished-transfer verifier because a correctly staged import is expected to fail the final publication gate until an opening sequence is intentionally reviewed and published.

## 2026-08-08 - full-course unpublished verification scope

- Expanded `qa_remaining_unpublished.py` from the 17 incoming 4SW Wk2-6SW Wk6 packages to all 36 instructional weeks. The importer still mutates only the 17 remaining packages, but it cannot report a successful coursewide transfer unless the previously built 1SW-4SW Wk1 modules pass the same module-name, unpublished-state, chronological-position, Day 1-5, paired-page, link, interaction, file, folder-lock, alt-text, and fallback checks.
- Strengthened Assignment verification so Canvas `submission_types` containing only `none` or `not_graded` do not count as a usable evidence route. The signed-in Career Iceberg activity was checked directly and correctly exposes student annotation, file upload, and text entry despite the Assignments index summarizing it as `No submission`.
- The teacher Assignments index also contains eight unpublished generic IMSCC placeholders under `Imported Assignments`, including `[Title Here]` and weekday assignments. They are not student-visible today. Keep them in the publication cleanup ledger; do not confuse those template objects with completed CCR activities or delete them until exact group contents and recovery source are recorded.
- Pre-import image-performance check found the 4SW Wk2-5SW Wk1 delivery images already range from roughly 32-272 KB, so no additional lossy compression is justified before browser QA. Added native `loading="lazy"` to the six incoming builders that embed those images so off-screen licensed visuals do not all compete during first page load.
- Signed-in DOM inspection of the staged replacement home exposed two H1 headings: Canvas renders the page title as H1 and the orientation shell repeated an H1 inside the page body. Changed the shared orientation shell to H2 and added live QA that rejects body-level H1s on the teacher launch, student orientation, and replacement home pages.
- Added `normalize_unpublished_image_loading.py`, an idempotent token-on-stdin repair for the exact 36 instructional modules. It refuses any published module, item, or page, preserves existing image policies, and only adds `loading="lazy"` where missing. The 17-module orchestrator runs it before final QA, and the verifier now rejects instructional images without native deferred loading. Updated the earlier 1SW-4SW Wk1 builders so future reruns preserve the same contract.
- Added `configure_assessment_map.py` to close the empty-gradebook-group gap. The script stages the approved six-weeks map as 30 unpublished 100-point Assignments: 18 Minors in the 40% group and 12 Majors in the 60% group. It renames known draft/practice aliases, creates missing early-course submission objects, inserts each object into its mapped week, preserves existing descriptions/routes, and does not set due dates or fabricate native rubric criteria. The coursewide verifier now checks every mapped title, group, weight, point value, unpublished state, submission route, and module membership; the publication audit checks the 18/12 group totals.
- Corrected 1SW Wk2 teacher copy from an outdated Major label to the locked Minor 2 placement. Canonical mapped titles now live in the 3SW-6SW builders so an idempotent rebuild does not recreate old `PRACTICE`, `DRAFT`, `1A/1B`, or shortened gradebook aliases.

## 2026-08-09 - complete unpublished Canvas transfer and coursewide pass

- Imported the orientation plus all seventeen remaining 4SW Wk2-6SW Wk6 packages into course 98060. The final live inventory is thirty-six instructional modules, all unpublished, plus the unpublished student orientation and teacher-build modules.
- The first import stopped safely at 5SW Wk6 because its licensed Day 3 asset root already included `day3/` and the builder added that segment a second time. Corrected the three literal paths and strengthened the bulk preflight to resolve the exact literal path expression passed to each upload call, preventing a basename-only check from missing the same class of error.
- Configured the approved weighted assessment map: eighteen 100-point Minor assignments in the 40% group and twelve 100-point Major assignments in the 60% group. Attached thirty student-visible 0-4 rubrics without letting Canvas raw rubric totals silently replace the district 100-point grade.
- Repaired an async form-encoding incompatibility in the rubric configurator by sending a dictionary payload instead of a tuple iterator. Offline async transport testing and the live thirty-rubric attachment pass both succeeded.
- Normalized the earlier 1SW-2SW modules to the current Day 1-5 structure. The migration preserved each teacher/student pair and interaction within its day, removed only the obsolete Week 0 module-item copy of the teacher overview, added missing student scan/fallback blocks without replacing activity directions, and reduced the Week 0 Day 2 flow from fifty-five to fifty minutes.
- Image-loading normalization scanned thirty-six modules and 361 pages before the legacy overview item was removed; zero pages required changes because every instructional image already carried `loading="lazy"`. Signed-in review of the repaired 5SW Wk6 lesson confirmed all three 1020x1320 licensed workbook visuals load when scrolled into view and retain useful alt text.
- Final read-only verification passes: thirty-six of thirty-six instructional modules; 658 ordered module items; 360 paired pages; 118 Canvas interactions; 552 referenced files in locked folders; course orientation; the 18/12 assessment map; and all thirty attached rubrics. No module, page, assignment, quiz, or discussion in the instructional transfer is published.
- Browser QA confirmed the complete teacher module list, the repaired 1SW Wk1 Day 3 student structure, the 5SW Wk6 Day 3 visual lesson, 6SW Major 1 and Major 2 private submission routes, and the full district-band rubric display. Student View reports no instructional modules, which is the correct prepublication boundary.
- Publication remains a separate gate. The current learner-facing `Welcome!` page is still the generic published template, the reviewed replacement home and orientation are unpublished, and the student navigation remains intentionally untrimmed. Do not publish week modules or change enrolled-student navigation until the opening sequence and front-page replacement are reviewed together.

## 2026-08-09 - 1SW Week 1 source-grounding and Xello-sequence repair

- Reconciled 1SW Week 1 against the district-customized FYF Manufacturing chapter and the authenticated Grade 8 Xello completion sequence. District HQIM now remains the student-facing source of truth; external labor-market and district-web material is kept separate as a dated teacher cross-check instead of silently replacing workbook, H&L, or Xello content.
- Rebuilt Day 1 around required Xello `What is CTE`, the FYF Manufacturing opener, and a bounded H&L career exploration. Rebuilt Day 4 around FYF `Robots for Crayons` pages 200-203 with an exact teacher key and a two-page action-plan packet. Rebuilt Day 5 as the required Xello Matchmaker lesson with 39 questions, `Find out why`, report verification, and private reflection assignment 3095755. The previous load-bearing Sphero route is superseded.
- Repaired the Canvas lesson-contract normalizer so it reads each explicit Topic, Objective, TEKS, and Demonstration/Show Your Learning contract before considering legacy overview tables. Coursewide contract QA now passes 180 teacher/student pairs with no missing or mismatched contracts.
- Idempotently reconciled unpublished module 542948 to sixteen exact items: five named day subheaders, five teacher guides, five student guides, and the private Matchmaker reflection. All pages, items, the module, and the assignment remain unpublished; visual folders remain locked.
- Live visual QA confirmed one canonical learning contract per repaired student page, clear student directions, no broken images after native lazy loading, and useful alt text. Read-only module QA returned no problems. The full local gate also passes: 180 lesson contracts, Week 1 template readability/accessibility, Python compilation, 18-template-pair preflight, 187 named dependencies, and source-grounding audit generation.

## 2026-08-09 - 1SW Week 2 HQIM and Personality Style repair

- Reconciled the source guide and unpublished Canvas package to the required Xello sequence: Day 5 now protects the 20-minute Personality Style task and Matchmaker prerequisite. The stale eight-minute Favorite Clusters block is removed; Favorite clusters remains in 1SW Wk5.
- Applied the district HQIM rule to career evidence. H&L or Xello supplies the source-labeled localized figure used in the student experience; BLS remains a separately labeled national cross-check. The lesson no longer describes BLS as silently confirming or replacing a different career, geography, date, or salary measure.
- Rebuilt the salary-comparison fallback around the actual writing job. The five-page core packet gives each of three careers a full evidence page, then separates comparison reasoning and the Day 5 reflection. The two-page model teaches source labels without freezing salary numbers, and the three-page bilingual support provides field labels, vocabulary, and sentence frames instead of a cramped full translation. All three pass strict page-count QA and visual inspection.
- Reconciled unpublished module 542950 to sixteen ordered items: five named subheaders, five teacher guides, five student guides, and the existing Minor 2 assignment. All pages, items, the assignment, and the module remain unpublished; folders remain locked.
- Coursewide contract normalization again verified all 360 paired pages. Module-specific QA returned no problems. Signed-in visual QA confirmed one Career Fit contract, correctly capitalized Xello language, Minor 2 wording, no Favorite Clusters residue, no broken images, and the unpublished boundary.

## 2026-08-09 - 1SW Week 3 source grounding and Learning Style repair

- Reconciled the week to FYF printed pp. 28-33 and 38, Climber Notes `Website Revamp` slide 2, and the authenticated Grade 8 Xello sequence. Day 5 now protects the required 20-minute Learning Style quiz; `Add Skills` remains in 1SW Wk4 and the separate 70-minute Xello lesson remains optional because it assumes additional prerequisites.
- Checked `pawsandclaws.hatsandladders.com` live and added a locked captured homepage as the Day 2 no-network route. The source lesson preserves the exact HQIM activity: three strengths, five observable problems, three fixes with user benefits, and one redesign sketch.
- Rebuilt the Day 1 four-career comparison as a complete BLS-grounded route so H&L browsing and Xello localization can add context without becoming fragile graded state. Day 4 now uses six dated evidence cards and requires students to distinguish an exact BLS occupation, closest occupation, or proxy.
- Standardized Day 4 labor evidence to May 2024 U.S. median annual pay and 2024-34 projected growth. Optional Xello DFW evidence stays in a separate box with exact occupation, geography, measure, and date rather than replacing or relabeling the national figure.
- Rebuilt the Day 4 research artifact as two intentional pages. The second page gives five lines to explain the changing work, six lines for a two-fact evaluation and source limit, a separate local-evidence box, and a short one-minute pitch map. Four revised Week 3 PDFs passed strict rendering and full-page visual inspection.
- Integrated the optional whole-group deck acceptance gate: teacher-ready instructional sequence, course-specific visual language, concrete-before-abstract student language, in-place EB supports, 1280x720 HTML/CSS source, exact 2x rendering, flattened PowerPoint, notes-level source attribution, exported-PPT inspection, and review before Canvas attachment.
- Reconciled live unpublished module 542972 to sixteen ordered items: five Day subheaders, five teacher guides, five student guides, and the existing Major 1 assignment. All module items, pages, and the assignment remain unpublished; five licensed visual folders remain locked.
- The first live verifier exposed Day subheaders interleaved between paired pages. The importer now owns the full item order and the plain module title `1SW Wk3: Computer Science and Networking Careers`; the second import restored Day header -> Teacher Guide -> Student Guide for all five days and preserved the Major assignment last.
- Module-specific API QA returned no problems: ten pages resolve with no template tokens or legacy tabs, twenty-two referenced files resolve, item positions are consecutive, and the Major assignment retains upload, text-entry, and media-recording routes. Local QA also passes 180 lesson contracts, Week 3 HTML structure/readability, Python compilation, and clean-diff checks.
- Signed-in Chrome QA confirmed the Day 1 teacher contract and readable visual hierarchy, the Day 2 student contract and three progressive licensed visuals, and the Day 4 plain-language exact/proxy explanation. The Day 2 workbook and Climber images loaded after scroll; opening the absence disclosure loaded the 1280x1570 captured Paws and Claws page without a broken image.

## 2026-08-09 - 1SW Week 4 source grounding and Add Skills repair

- Reconciled the week to FYF pp. 36-38, the authenticated Grade 8 Xello sequence, official micro:bit troubleshooting guidance, and dated BLS career evidence. Day 1 protects required Xello `Add interests` for 15 minutes; Day 5 protects required Xello `Add skills` for 20 minutes. H&L remains a supplemental exploration route rather than graded platform state.
- Rebuilt the three-route comparison around one consistent evidence basis: May 2024 U.S. median pay and common preparation for Computer User Support Specialist, Computer Network Support Specialist, and Software Developer. The guide explicitly says the figures are not starting pay, DFW-localized pay, or promises, and the optional local check remains separately labeled.
- Preserved the district-customized FYF page as HQIM while separating current-source cross-checks. The current Irving site confirms Technology Support Services at Singley Academy; the lesson does not silently overwrite workbook, H&L, or Xello language when those student-facing tools show different measures.
- Reframed the MakeCode work so micro:bit hardware, simulator, and paper trace are equal evidence routes. Firmware is no longer a routine setup demand; the teacher uses the official troubleshooting path only when a verified connection issue points to it. Students must retain a screenshot, share link, downloaded file, or paper trace before leaving.
- Rebuilt Minor 3 as the durable team Program Evidence plus each student's individual Xello Skill and Help Desk Connection, 16 points. The one-minute lightning demonstration is formative communication practice rather than a live-scored major. Day 4 now requires documentation and appropriate escalation when the issue remains unresolved, and the skill-transfer prompt reaches beyond IT support.
- Repaired six Week 4 printables and visually checked all eleven pages. The bilingual route comparison now has usable response space; the Program Evidence question no longer splits across pages; the two-page MakeCode guide and role-play scripts preserve writing room; and the customer-service check fits one page.
- Reconciled live unpublished module 542973 to sixteen ordered items under the plain title `1SW Wk4: Tech Support Careers and MakeCode`: five Day subheaders, five teacher guides, five student guides, and the existing Minor 3 assignment. The module, pages, items, and assignment remain unpublished; the five visual folders remain locked.
- Module-specific API QA returned no problems: ten pages resolve without template tokens or legacy tabs, twenty-nine referenced files resolve, item positions are consecutive, and the assignment retains file-upload, text-entry, and media-recording routes. Local QA also passes all 180 lesson contracts, Week 4 template structure/readability, and Python compilation.
- Signed-in Chrome QA confirmed the exact Day header -> Teacher Guide -> Student Guide order, revised Minor 3 language, the Day 2 bilingual route and source guide, the Day 3 daily contract and firmware boundary, the Day 4 documentation/escalation role-play, and the Day 5 Xello Add Skills workflow. Student pages had no body overflow on desktop or at a 390-pixel viewport. The revised 98 KB role-play image and other deferred visuals loaded successfully; image-load timing remains in the coursewide performance backlog for a later comparative pass.

## 2026-08-09 - 1SW Week 5 source grounding and capstone repair

- Reconciled the week to FYF pp. 24-25 and 34-38, the seven locked `Safe or Spoofed` Climber Notes images, the authenticated Grade 8 Xello sequence, and a dated BLS/CISA cross-check. District HQIM remains the student-facing starting point; current external evidence is labeled rather than silently replacing workbook, H&L, or Xello content.
- Day 1 now directly earns d(1)(D): students evaluate Information Security Analyst as an emerging occupation with two dated facts and one source limitation. The fixed guide distinguishes national median pay from starting/DFW pay and projection from guarantee; CyberSeek and H&L remain optional live exploration.
- Day 2 now directly earns d(4)(F). All seven email images are embedded through individual disclosures, the teacher key distinguishes `safe-looking` from proven safe, and the response protocol is pause, independently verify, report, and delete. Any practice message remains fictional, private, unsent, and free of working links, QR codes, attachments, credentials, or district impersonation.
- Day 3 now uses a completed two-page teacher model and a two-page student plan with adequate writing space. The major evidence requires accurate advice, one behind-the-scenes work-ethic task, one privacy/integrity rule, an original or credited flyer, and a privacy-safe sign-up route. Paper, Canva, and Adobe Express remain equal.
- Day 4 protects the exact required Xello `Favorite clusters` minimum: 40 minutes and at least one saved cluster. The licensed 90-minute `My career clusters` lesson remains optional teacher background and its Matchmaker/three-saved-career prerequisites are not imposed on the district minimum. `Save careers` remains in 2SW Wk3.
- Day 5 now directly earns d(3)(A) through one middle-school-to-high-school action and one high-school-to-postsecondary action. The two-page reflection includes a Week 0 recovery box, bilingual labels and full sentence frames are available, and the four-part 16-point Major 2 packet remains the single graded object. Laser fabrication, gallery participation, public speaking, and platform clicks do not affect the score.
- Rebuilt and visually inspected fifteen pages across eight revised/new PDFs. Page counts match every front-matter contract; response regions now match the requested writing; the stale three-page app-favorites support sheet is replaced by a two-page language scaffold.
- Reconciled live unpublished module 542984 under the plain title `1SW Wk5: Cybersecurity, Favorite Clusters, and Capstone`. Its sixteen ordered items are five Day subheaders, five teacher guides, five student guides, and `MAJOR 2: Cybersecurity Capstone Evidence Portfolio` last. All pages, the assignment, and the module remain unpublished; visual folders remain locked.
- Local QA passes all 180 teacher/student lesson contracts, Week 5 template structure/readability, Python compilation, and clean-diff checks. Module-specific API QA returned no problems: ten pages, sixteen consecutive items, the existing Major 2 submission routes, and all referenced files resolve.
- Signed-in Chrome QA confirmed the module order, exact daily learning contracts, all seven 1600x900 email images after progressive disclosure, both 1275x1650 bootcamp visuals, the completed-model link, bilingual Friday support, and the unpublished boundary. The Week 5 module remains open in Canvas for owner review.

## 2026-08-09 - 2SW Week 1 source grounding and legal-evidence repair

- Reconciled the week to FYF pp. 39-58, including the Law and Public Safety opener, Emergency Essentials, City Council in Action, Policy Showdown, district pages, and App Exploration. Required Xello `Life experiences` retains its exact ten-minute window and at-least-one-save minimum. H&L remains supplemental exploration; the unverified eDynamic preview and marker were removed from the core route.
- Supplied a two-page Legal Career Evidence Card set for Lawyer, Paralegal/Legal Assistant, and Court Reporter/Simultaneous Captioner. It uses May 2024 U.S. national medians and common preparation from BLS on one consistent basis, while H&L or Xello may add a separately labeled district-local view. Students no longer depend on an improvised teacher source hunt.
- Rebuilt the Legal Entrepreneur and Association Card as a two-page artifact with a fixed bank for the State Bar of Texas, NALA, and NCRA. The card distinguishes association membership, certification, and licensing and removes the previous hidden teacher-prep requirement.
- Closed the Day 2 and Day 3 artifact-alignment gaps. The Emergency Kit now captures the firefighter/emergency-management planning task; the ordinance packet now names a specific worker and task in creating, reviewing, explaining, or enforcing an ordinance. Those durable responses make the claimed d(1)(C) evidence visible.
- Added the non-negotiable Topic, Objective, TEKS, and Demonstration of Learning to every teacher page and the student-friendly Topic, I can, and Show my learning contract to every student page. All five student pages keep a visible Done When check and an absence/platform route.
- Rendered and visually inspected fifteen intentional pages across eight lesson PDFs. Removed the blank spill pages and the nearly empty Career Research second page, while preserving full-page drawing space, multi-sentence argument space, and clearly labeled response jobs.
- Reconciled unpublished module 542987 under the plain title `2SW Wk1: Legal Studies and Policy Evidence`. Its sixteen ordered items are five Day subheaders, five teacher guides, five student guides, and `MAJOR 1: Legal Policy Position Evidence` last. The assignment retains upload, text-entry, and media-recording routes; all pages, items, assignment, and module remain unpublished.
- Local QA passes all 180 source lesson contracts, Week 1 HTML structure/readability, Python compilation, clean-diff checks, and the regenerated coursewide grounding audit with zero unresolved verification markers. Module-specific API QA returned no problems across ten pages, sixteen ordered items, and nineteen referenced files.
- Signed-in Chrome QA confirmed the exact module order, unpublished boundary, learning contracts, full-resolution deferred workbook visuals, no unresolved template values, desktop layout, and zero horizontal overflow at a 390-pixel viewport. The revised module remains open in Canvas for owner review.

## 2026-08-09 - 2SW Week 2 source grounding and first-responder evidence repair

- Reconciled the week to FYF pp. 48-58, the licensed Clinton Lake and Injured on the Trail Climber Notes, the current scope and sequence, and dated BLS/Army COOL cross-checks. The workbook and district platforms remain the student-facing HQIM; external evidence is labeled as a current cross-check rather than substituted silently.
- Rebuilt the First Responder Route Guide as four intentional pages: a dated five-career guide, three full-width career comparisons, a military-versus-civilian law-enforcement route comparison, and a district/cluster connection. The route language now makes clear that civilian requirements vary and military training does not automatically transfer into a civilian academy, license, certification, or agency appointment.
- Added the non-negotiable Topic, Objective, exact TEKS, and Demonstration of Learning to every teacher guide and the matching student-friendly Topic, I can, and Show my learning contract to every student guide. Day 2 now carries the integrity evidence it actually assesses; Day 4 names the EMT/search-and-rescue documentation role needed for the claimed career-opportunity evidence.
- Corrected the Day 1 source boundary. FYF pp. 56-57 show Legal Studies/Criminal Justice and dual-credit context, while the current Singley page separately lists Law Enforcement and Emergency Medical - EMT. Canvas states that distinction instead of attributing current pathway labels to the workbook image.
- Rebuilt and visually inspected thirteen intentional pages across six printables. The four-page route guide, two-page Patient Care Report, scenario tracker, simulation record, rubric, and reflection now provide response space proportionate to the requested phrases, comparisons, explanations, and report writing.
- Reprocessed the six portrait Clinton Lake evidence pages into upright 900x1600 Canvas-only derivatives without altering their text. The student page uses the upright files with deferred image loading; the original licensed assets remain in the locked authenticated resource tree and out of Git.
- Reconciled unpublished module 542988 to seventeen ordered items: five Day subheaders, five teacher guides, five student guides, the optional Day 2 counterevidence Discussion, and `MAJOR 2: Patient Care Report and Complication Plan` last. The Discussion, assignment, pages, items, and module remain unpublished; the assignment retains upload, text-entry, and media-recording routes.
- Local QA passes all 180 source lesson contracts, Week 2 template structure/readability, Python compilation, clean-diff checks, and the regenerated coursewide grounding audit. Module-specific API QA returned no problems across ten pages, seventeen ordered items, two unpublished interactives, and twenty referenced files.

## 2026-08-09 - 2SW Week 3 source grounding and scaffolded worksheet repair

- Reconciled the week to FYF printed pp. 59-61 and 84-86, Climber Notes `Vitals in Motion` slide 2, and the authenticated Grade 8 Xello sequence. Day 5 protects required Xello `Save careers` for thirty minutes and at least three saved careers; H&L remains supplemental.
- Preserved the district HQIM source boundary. FYF pp. 84-85 remain the student-facing district-customized snapshot, while the current Singley webpage is a separately labeled dated cross-check rather than a replacement answer key.
- Added a research-grounded worksheet design standard and linked it from the Canvas lesson workflow. The gate now requires a thinking-job-first layout, worked or partially worked models, graduated scaffolds, point-of-use language support, purposeful attributed visuals, response areas tested against large middle-school handwriting, strict rendering, and visual inspection.
- Added an artifact-surface gate before worksheet design: assigned workbook first, required Xello/H&L task second, Canvas-native response third, and a new printable only when those surfaces do not capture the work well. A packet longer than two pages must be labeled and justified; source guides are embedded or projected rather than automatically printed.
- Rebuilt the Nursing Route Comparison as a four-page `See one -> Try one -> Compare -> Decide` access scaffold. It includes a CC0 nursing-workplace visual, durable attribution, task-specific word banks and cognates, oral rehearsal, complete comparison/decision frames, and expanded handwriting space. It is **not** the default class-set artifact.
- Rebuilt and visually inspected all four changed printables: the four-page optional route scaffold, two-page route guide, two-page simulator build, and two-page clinical handoff record. All passed strict page-count and overflow checks with writing space matched to the requested response.
- Added the non-negotiable Topic, Objective, exact TEKS, and Demonstration of Learning to all five teacher guides and the matching Topic, I can, and Show my learning contract to all five student guides. Every student page retains a visible absence/platform route, and deferred image loading remains native.
- Made Canvas the default route-comparison work surface. Day 1 now uses a two-question Nursing Assistant/LVN model check; Day 2 uses a five-question route evidence check with point-of-use word banks and complete frames. Both are unlimited-attempt practice quizzes, and the teacher pages explicitly say `Default printing: none`. The optional four-page PDF carries the equivalent enlarged/no-device route.
- Reconciled unpublished module 542989 to nineteen ordered items: five Day subheaders, five teacher guides, five student guides, three practice Quizzes, and the existing Minor assignment. All pages, items, interactives, and the module remain unpublished; licensed-resource folders remain locked.
- Module-specific API QA returned no problems across ten pages, nineteen consecutive items, the two new Canvas-first checks, the preserved handoff Quiz, the preserved Minor submission routes, and all referenced files. Signed-in Canvas review previously confirmed the daily contracts, HQIM/source distinction, and responsive page behavior; local PDF rendering verifies the optional scaffold because the browser's PDF preview extension blocks the Canvas CDN preview.

## 2026-08-09 - 2SW Week 4 HQIM grounding and Medical Billing repair

- Reconciled the week to FYF pp. 69-73 and 84-86, the licensed `Smile Squad` training images, the authenticated Xello Grade 8 sequence, and the 2026-27 Irving ISD High School Course Work. FYF and the coursebook now control the teacher- and student-facing names: Health Science: Dental and Health Science: Medical Billing at Singley.
- Removed the stale website-only conclusion that Medical Billing had no Irving pathway home. National BLS figures remain a labeled comparison source, but they no longer rename the workbook career or create a competing pathway story in the lesson pages.
- Kept FYF as the default student work surface for Smile Squad and Perfect Toothbrush. The observation record and toothbrush brief are optional access/no-workbook routes, not additional class-set packets. Day 3 uses Xello's Completion Standards report plus one short Canvas college-credit check; paper cannot replace the required Xello saves.
- Rebuilt the justified artifacts around their actual thinking jobs. The two-page optional career comparison separates classification from a four-part recommendation, the two-page coding lab uses fictional charts and a controlled current code list, and the one-page college-credit fallback does not duplicate Xello. All seven Week 4 PDFs pass strict page-count and overflow QA; the changed comparison, guide, rubric, and coding lab were rendered and visually inspected.
- Reconciled unpublished module 542990 to eighteen ordered items: five Day subheaders, five teacher guides, five student guides, two unpublished practice Quizzes, and the existing `MINOR 2: Health Career Evidence Check` assignment. No graded object was duplicated.
- Updated assignment 3094828 in place. It remains unpublished and worth 100 points, retains upload, text-entry, and media-recording routes, and now directs students to FYF pp. 84-85 and Medical Billing and Coding. The five day-visual folders and the Week 4 support folder remain locked.
- Local QA passes all 180 lesson contracts, Week 4 template structure/readability, Python compilation, strict worksheet builds, and clean-diff checks. Module-specific API QA returned no problems across ten pages, eighteen consecutive items, both quizzes, the existing Minor, and seventeen referenced files.

## 2026-08-09 - 2SW Week 5 Canvas contract and artifact-surface repair

- Reconciled the Canvas package to the already-grounded FYF sequence: pp. 144-145 remain the Day 1 conflict work, pp. 62-63 remain the Day 2 listening work, pp. 134-135 support Day 3 advocacy, and pp. 147-148 remain the Day 4 Little Library work. Required Xello `Work experiences` remains Day 5; Xello Time Management stays supplemental.
- Added the non-negotiable Topic, Objective, exact TEKS, and Demonstration of Learning to all five teacher guides and the matching Topic, I can, and Show my learning contract to all five student guides.
- Removed automatic duplicate printing. FYF is the default student work surface on Days 1, 2, and 4. The separate two-page conflict, listening, and written-message PDFs are now clearly labeled no-workbook, absence, or extended-practice routes. The Powerskills guide is projected or posted rather than automatically printed.
- Updated existing assignment 3094829 in place as `MINOR 3: Communication and Goal Synthesis`. It remains unpublished and worth 100 points, retains upload, text-entry, and media-recording routes, and now carries four visible response jobs plus the 16-point rubric. The two-page synthesis PDF is the assigned paper fallback rather than a required class set.
- Reconciled unpublished module 544296 to eighteen ordered items: five Day subheaders, five teacher guides, five student guides, one unpublished retryable practice Quiz, one unpublished optional Discussion, and the existing Minor assignment. No graded object was duplicated.
- The first live QA exposed a Canvas distinction between a locked parent folder and an uploaded file whose own `locked` field remained false. The importer now explicitly locks each uploaded file record. The second live QA passed with all sixteen referenced files locked, all page and interactive positions consecutive, and no unresolved fields or publication leaks.
- Local QA passes all 180 lesson contracts, Python compilation, formatting, and clean-diff checks. The live module, ten pages, Quiz, Discussion, Minor, and all file records remain unpublished or locked for teacher cloning and review.

## 2026-08-09 - 2SW Week 6 workbook-surface and career-evidence repair

- Visually compared FYF pp. 74-81 with the six existing Week 6 artifacts before changing the delivery plan. FYF already supplies usable planning, drawing, outbreak-report, and response-plan space. The separate Mini Medics, investigation, and response records remain available as no-workbook, absence, or extended-reasoning routes rather than automatic class sets.
- Day 1 retains the two justified CCE artifacts because the workbook does not supply the fixed three-career evidence comparison or the fictional five-part cover-letter practice. Day 5 uses the private Canvas reflection by default and keeps its one-page PDF as the assigned paper route.
- Added the non-negotiable Topic, Objective, exact TEKS, and Demonstration of Learning to all five teacher guides and the matching Topic, I can, and Show my learning contract to all five student guides.
- Tightened Days 2-4 so d(1)(C) is visible in the student evidence instead of inferred from doing a science-themed activity. Day 2 names a biomedical career and work product; Day 3 names an epidemiologist investigation work product and downstream user; Day 4 names one public-health worker and the test, communication, or response product that person creates.
- Updated the existing ungraded assignment 3093978 in place. It remains unpublished, accepts private text entry or file upload, and now gives students four visible before-and-after response jobs without requesting a profile screenshot.
- Reconciled unpublished module 544297 to seventeen ordered items: five Day subheaders, five teacher guides, five student guides, one unpublished retryable practice Quiz, and the existing ungraded private Assignment. No interaction or assignment was duplicated.
- The importer now forces the module unpublished on every run and explicitly locks each uploaded file record. Live module QA passed with all seventeen referenced files locked, ten unpublished pages, two unpublished interactives, consecutive positions, and no unresolved fields or unsupported items.
- Local QA passes all 180 lesson contracts, Week 6 template structure/readability, Python compilation, formatting, and clean-diff checks.

## 2026-08-09 - 3SW Week 1 veterinary source-grounding and owner-style gate

- Reconciled the week to FYF p. 87, veterinary triage pp. 96-99, district pathway pp. 100-101, the authenticated Grade 8 Xello Skills lesson, and one dated BLS evidence set. FYF/H&amp;L remain the district HQIM; the public Nimitz page is teacher background rather than a competing student source.
- Added the non-negotiable Topic, Objective, exact TEKS, and Demonstration of Learning to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. Day-level claims now match the evidence students actually produce.
- Kept FYF p. 99 as the default triage writing surface. The separate triage record is an optional structured or absence route. Day 3 and Day 5 now place each licensed workbook page beside the step that uses it and provide a full-size Canvas preview link for narrow screens.
- Rebuilt six coordinated printables with point-of-use bilingual word banks, complete response frames, and writing regions sized to the requested evidence. The career comparison, evidence guide, rubric, pathway recommendation, triage scaffold, and Xello reflection pass strict page-count and overflow checks and full-page visual inspection.
- Ran the required separate owner-style adversarial review twice. The first pass blocked staging on a stale TEKS preview, hidden language supports, the Day 2 trade-off mismatch, and a teacher-only rubric exposed to students. The repair pass found Markdown-swallowed response blanks in four PDFs. After bracketed response labels replaced the underscores, the final visual gate returned GO.
- Added the adversarial review and Git checkpoint requirement to the production workflow. Backup commit `d68a87ef` was pushed before Canvas staging.
- Reconciled unpublished module 544298 in place. Its eighteen consecutive items are five Day subheaders, five teacher guides, five student guides, one four-question practice Quiz, one private ungraded Xello reflection, and the existing `MINOR 1: Veterinary Pathway Evidence Packet` assignment. All pages, interactives, the module, and the Minor remain unpublished; all sixteen referenced files remain locked.
- Updated only the Veterinary Minor rubric from its audited Markdown source. The rubric remains student-visible and advisory at 16 raw points while the unpublished assignment remains worth 100 points with private upload, text-entry, and media-recording routes. The rubric automation now supports one-assignment updates and verifies the live association after Canvas writes.
- Final QA passes all 180 lesson contracts, both Week 1 templates, Python compilation, clean-diff checks, six strict worksheet builds, desktop/mobile visual inspection, the separate owner-style gate, and live module API verification with zero problems.

## 2026-08-10 - 3SW Week 2 plant-science source grounding and private skill-transfer check

- Reconciled the week to FYF Grow System Rescue pp. 88-90, Farm to Table pp. 91-92, the authenticated Grade 8 Xello `Biases and career choices` lesson, and fixed BLS/USDA evidence. FYF and Xello remain the student-facing HQIM; public sources are dated, labeled cross-checks rather than replacement curriculum.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. Day 1 now collects a career preparation fact, Day 2 explicitly identifies the Agricultural Communications Specialist role, and Day 3 is the sole d(4)(B) carrier.
- Preserved the workbook as the default work surface. FYF p. 92 retains its existing interview-question boxes; the two-page Farm-to-Table planner adds only a four-step plan, career connection, and full-page sketch. The other five printables remain one or two pages. All six pass strict page-count and overflow checks and full-page visual inspection.
- Added `FORMATIVE: Communication Skill Transfer` as a private, unpublished, not-graded Canvas Assignment accepting text or media recording. It sits immediately after the Day 3 Student Guide and gives the two-career d(4)(B) response an unambiguous collection home without adding another Major criterion or printed worksheet.
- Replaced the always-visible Day 4 YouTube iframe with a closed optional disclosure. The fixed evidence guide carries every required fact, so a blocked video no longer creates a blank mobile screen or delays the core lesson.
- Ran the required separate owner-style adversarial gate. The first pass blocked staging on contract drift, missing preparation and role evidence, an uncollected transfer response, and the mobile video gap. After repair and exact canonical synchronization, the final gate returned GO. Backup commit `b4568dd8` was pushed before Canvas staging.
- Reconciled unpublished module 544301 to nineteen consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, the private transfer check, one four-question practice Quiz, the existing `MAJOR 1: Farm-to-Table and Emerging Plant-Tech Evidence`, and the private Xello reflection. All pages, interactives, and the module remain unpublished; all seventeen referenced files are locked.
- Updated the existing Major assignment 3093993 in place. It remains worth 100 points in `Major Assessments (60%)`, retains upload, text-entry, and media-recording routes, and uses advisory rubric 32308 with four criteria and 16 raw points. The transfer check is explicitly outside that rubric.
- Final QA passes all 180 lesson contracts, both Week 2 templates, Python compilation, clean-diff checks, six strict worksheet builds, desktop/mobile visual inspection, the separate owner-style gate, and live module API verification with zero problems.

## 2026-08-10 - 3SW Week 3 sustainable-engineering evidence and Xello goal-setting repair

- Reconciled the week to FYF Ag-Tech Pest Patrol pp. 93-95, FYF Adaptability p. 146, the authenticated Grade 8 Xello `Set goals` requirement, and fixed BLS, USDA, EPA, and NASA evidence. FYF and Xello remain the student-facing HQIM; external evidence is dated and labeled rather than replacing district curriculum.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. Day 2 now identifies design constraints as an agricultural engineer's work product, Day 3 names the career role, work product, and user, and Day 5 directly carries d(4)(A) through two saved goals plus a private planning reflection.
- Preserved FYF p. 95 as the default peer-review surface. The one-page CCE revision record captures only the decision and proof, while paper, Canva, and Adobe Express remain equal design routes. The private Xello Goal Check avoids copying full goals out of Xello and does not request a profile screenshot.
- Rebuilt five coordinated printables with point-of-use word banks, complete response frames, and response regions sized to the writing or sketch job. The two-page field notes, two-page design brief, one-page revision record, two-page student-visible rubric, and one-page goal check pass strict page-count and overflow checks. The three existing evidence resources also passed the visual gate, for eight PDFs and fourteen pages total.
- Ran the required separate owner-style adversarial gate. The first pass blocked staging on repeated `I can` text, stale Xello navigation, suspicious responsive renders, and a rubric criterion that depended on a formative sheet outside the submitted packet. After repair and full rerendering, the final gate returned GO. Backup commit `f4a24302` was pushed before Canvas staging.
- Reconciled unpublished module 544302 to eighteen consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, the private not-graded Pest Patrol draft, the existing `MAJOR 2: Sustainable Engineering Design and Trends Evidence`, and the private not-graded Xello reflection. All pages, assignments, and the module remain unpublished; all fourteen referenced files are locked.
- Updated existing Major assignment 3093996 in place. It remains worth 100 points in `Major Assessments (60%)`, retains upload, text-entry, and media-recording routes, and uses advisory rubric 32309 with four criteria and 16 raw points. Practice assignments 3093995 and 3093997 remain unpublished and not graded.
- Final QA passes all 180 lesson contracts, both Week 3 templates, Python compilation, clean-diff checks, five strict worksheet builds, twenty desktop/mobile page renders, the separate owner-style gate, and live module API verification with zero problems.

## 2026-08-10 - 3SW Week 4 hospitality workbook-first and Minor evidence repair

- Reconciled the week to FYF Culinary Twist pp. 112-113, Hotel Rescue pp. 117-118, Cater and Create pp. 119-120, Motivation p. 122, and one fixed BLS career-evidence set. FYF remains the default student work surface; dated public evidence is a labeled comparison source rather than a replacement curriculum.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. The canonical Day 4 and Day 5 lesson language now uses the district 5E phase `Extend`.
- Removed duplicate class-set packet work. Day 1 uses FYF pp. 112-113 by default and keeps the three-page menu brief as a no-workbook route. Day 2 uses FYF p. 122 plus a two-page comparison; Day 3 uses FYF p. 118 plus a two-page individual response; Day 4 uses FYF pp. 119-120 plus a one-page companion. Role and crisis cards are projected or printed once per team.
- Rebuilt the six changed printables around the evidence missing from the workbook. Point-of-use word banks and complete frames sit beside the task that uses them, and response areas match the required writing or design job. All eight Week 4 PDFs pass strict rendering with zero warnings: seventeen pages total, with substantially lower routine per-student printing.
- Added semantic headings for Today you will, Exit check, and You are done when. All twenty refreshed desktop/mobile page renders are clean with no clipping or overflow, and required directions remain visible rather than hidden in disclosures.
- Ran the required separate owner-style adversarial gate. The first Week 4-specific pass blocked staging on the three nonsemantic labels and stale `Elaborate` wording. After repair and rerendering, the final gate returned GO. Backup commit `090c28f5` was pushed before Canvas staging.
- Reconciled unpublished module 544304 to eighteen consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, the private not-graded Culinary Twist annotation, the four-question unlimited-attempt Motivation practice Quiz, and the existing `MINOR 2: Hospitality Career and Business Recommendation`. All pages, interactives, and the module remain unpublished; all eighteen referenced files and six Week 4 folders are locked.
- Updated existing Minor assignment 3094000 in place. It remains worth 100 points in `Minor Assessments (40%)`, retains upload, text-entry, and media-recording routes, and uses advisory rubric 32306 with four criteria and 16 raw points. Practice assignment 3093999 remains unpublished and not graded.
- Final QA passes all 180 lesson contracts, both Week 4 templates, Python compilation, clean-diff checks, eight strict worksheet builds, twenty desktop/mobile page renders, the separate owner-style gate, and live module API verification with zero problems.

## 2026-08-10 - 3SW Week 5 cosmetology workbook-first and pathway evidence repair

- Reconciled the week to FYF Human Services and SFX pp. 127-133, district cosmetology context pp. 136-137, the current Texas Cosmetology Operator requirements, and the current Irving ISD high-school CTE list. FYF remains the student-facing HQIM; TDLR, Irving ISD, and BLS evidence is dated and labeled rather than substituted silently.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. Day 1 earns the Human Services cluster and career evidence, Day 2 records an SFX career work product, Day 3 carries preparation and enrollment evidence, Day 4 carries entrepreneurship, and Day 5 synthesizes the four strands.
- Preserved the workbook as the default work surface. FYF pp. 128-129 hold the Day 1 research and concept map; the three-page brief is only a no-workbook route. FYF p. 131 holds the Day 3 quality check; the enlarged sheet is optional. FYF p. 133 holds the three-post campaign; the companion collects only business, safety, revision, and trust evidence the workbook does not ask for.
- Added a one-page SFX Build and Test Record for the Day 2 evidence job and rebuilt the remaining justified artifacts around their actual thinking work. All eight Week 5 PDFs pass strict page-count and overflow checks and full-page visual inspection: fifteen pages total, with point-of-use word banks, complete frames, and writing or sketch regions sized to the requested response.
- Set the turnkey SFX route to dry relief or a digital mockup. Classroom materials never go on a student, clothing, face, arm, hair, or skin. Adhesive work is optional only after the campus product-label, SDS, allergy, ventilation, supervision, storage, and cleanup gate.
- Ran the required separate owner-style adversarial gate. The first pass blocked staging because the Day 1 absence disclosure called the three-page no-workbook brief a two-page brief. After the wording repair and a full rerender, the narrow recheck returned GO. Backup commit `c5c40fa2` was pushed before Canvas staging.
- Reconciled unpublished module 544308 to seventeen consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, the five-question unlimited-attempt Texas license and safety practice Quiz, and the existing `MINOR 3: Cosmetology Career and Business Recommendation`. All pages, interactives, and the module remain unpublished; all seventeen referenced files are locked.
- Updated existing Minor assignment 3094012 in place. It remains worth 100 points in `Minor Assessments (40%)`, retains upload, text-entry, and media-recording routes, and uses advisory rubric 32307 with four criteria and 16 raw points. Practice Quiz 281856 remains unpublished and ungraded.
- Final QA passes all 180 lesson contracts, both Week 5 templates, Python compilation, clean-diff checks, eight strict worksheet builds, twenty desktop/mobile page renders, the separate owner-style gate, and live module API verification with zero problems.

## 2026-08-10 - 3SW Week 6 entrepreneurship, budget, and Xello recovery repair

- Reconciled the week to FYF Business, Marketing, and Finance p. 221 and Million Dollar Idea pp. 234-237, the authenticated Grade 8 Xello `Scholarship profile` requirement, and one dated Dallas County living-cost scenario. FYF and Xello remain the student-facing HQIM; public Irving ISD, MIT, and Dallas College material is labeled teacher cross-check or fixed evidence rather than a competing student answer key.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. The final owner-gate repair changed the canonical Day 5 Topic from `Entrepreneurship` to the accurate `Personal Budget`, matching the builder and both rendered contracts.
- Preserved FYF as the default work surface on Days 2-3. The four-page Million Dollar Idea packet is only a no-workbook, absence, or enlarged-scaffold route; students do not complete both. Day 4 printing is split intentionally: Venture Brief pp. 1-2 once per team and individual evidence pp. 3-4 once per student.
- Reduced the Personal Budget and Xello Scholarship Plan from four pages to three. Pages 1-2 contain the budget work; p. 3 contains only the no-device Xello directions and supervised catch-up check. The package does not collect Scholarship profile answers or screenshots, and paper does not substitute for required Xello completion.
- Protected the exact Xello requirement on Day 5: twenty minutes to complete the matching Scholarship profile, verified through the Completion Standards report. The official 2:02 student video remains optional and collapsed; the English and Spanish Xello guides are the equal text route.
- Recast the existing portfolio as `RECOVERY: Entrepreneurship Portfolio`. Assignment 3094018 is renamed in place, remains unpublished, worth 0 points, not graded, and accepts upload, text-entry, or media-recording evidence. It is available only for teacher-approved recovery or replacement and is not a third automatic Major in a six weeks that already has three minors and two majors.
- Ran the required separate owner-style adversarial gate in narrow evidence passes. The reviewer inspected the representative responsive set and all twelve pages across the budget, venture, support, and recovery-rubric PDFs; the sole contract blocker was repaired before the final GO. Writing regions, group-versus-individual evidence, Xello privacy, point-of-use language support, and mobile fit passed.
- Backup commit `99190a98` was pushed before Canvas staging. Reconciled unpublished module 544318 to seventeen consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, the five-question unlimited-attempt practice Quiz, and the recovery Assignment. All pages, interactives, and the module remain unpublished; all thirteen referenced files are locked.
- Final QA passes all 180 lesson contracts, both Week 6 templates, Python compilation, clean-diff checks, the 30-assessment and 30-rubric preflights, the importer dependency/accessibility preflight, twenty desktop/mobile renders, the separate owner-style gate, and live module API verification with zero problems.

## 2026-08-10 - 4SW Week 1 workbook-first mid-year planning repair

- Reconciled the week to FYF Career Iceberg pp. 6-8, Career Thinker and Doer p. 22, and Capstone Rungs 1-3 pp. 281-286. FYF remains the default student work surface on Days 2-3. The enlarged Career Iceberg and Career Deep Dive packets are no-workbook, absence, or access routes; students do not complete both surfaces.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. Point-of-use word banks and complete response frames sit beside the task that uses them.
- Made Day 4 a private Canvas-first Pathway and CTSO Decision. Practice assignment 3095964 is unpublished, worth 0 points, not graded, and accepts upload, text-entry, or media-recording evidence. The four-page packet remains the paper, enlarged, and no-platform route rather than an automatic class set.
- Tightened Day 5 to one submitted artifact. Students submit only the three-page Mid-Year Career Blueprint; Days 1-4 remain source material in the portfolio, not four additional uploads. The two-page rubric is student-safe and scores the Blueprint evidence rather than teacher process notes.
- Protected the assessment map in code. The importer refuses to update the Blueprint unless exactly one existing assignment has the correct title, 100-point value, and `Major Assessments (60%)` group. Assignment 3094021 passed that gate, remains unpublished, retains upload, text-entry, and media-recording routes, and uses advisory rubric 32313 with four criteria and 16 raw points.
- Kept the HQIM boundary visible. FYF, H&L, and Xello remain the student-facing curriculum evidence. Current Irving ISD pathway and course pages confirm or extend exact campus, course, application, and access details; teachers record a conflict for follow-up rather than asking students to reconcile competing sources during class.
- Rebuilt and visually inspected the changed Blueprint, rubric, and pathway PDFs. The final six-PDF set totals nineteen pages with writing and sketch regions sized to the requested response. All twenty responsive Teacher and Student Guide renders pass desktop and mobile inspection without clipping, collision, or horizontal overflow.
- Ran the required separate owner-style adversarial gate. The reviewer checked the full responsive set, all six PDFs, contract parity, workbook-first routing, EB supports, response space, grading safeguards, unpublished state, and locked-file behavior. The gate returned GO with no release blocker. Backup commit `d955bfc9` was pushed before Canvas staging.
- Reconciled unpublished module 544320 to eighteen consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, the existing Career Iceberg annotation, the new private Pathway and CTSO practice, and `MAJOR 1: Mid-Year Career Blueprint`. All pages, assignments, and the module remain unpublished; all thirteen referenced files and six Week 1 folders are locked.
- Final QA passes all 180 lesson contracts, both Week 1 templates, Python compilation, clean-diff checks, the 30-assessment and 30-rubric preflights, twenty responsive renders, the separate owner-style gate, and live module API verification with zero problems.

## 2026-08-10 - 4SW Week 2 counseling-ready planning and current graduation-rule repair

- Reconciled the week to FYF Rung 6 SMART Goals pp. 292-293, FYF Rung 7 course-planning and opportunity pages, the current 2026-27 Irving ISD coursebook, and the August 2026 TEA Chapter 74 graduation framework. The lesson now distinguishes the current rule from the 2025 Graduation Toolkit's prior-cohort wording and explicitly states that current Grade 8 students enter high school after the 2026-27 start date.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. Point-of-use decision words and complete response frames sit beside the task that uses them.
- Reduced printing and duplicate work. Day 2 uses the Canvas Student Annotation by default and keeps the three-page course-plan PDF as the paper or enlarged route. Day 3 uses one two-page College Credit and Plan Check. Day 4 keeps FYF pp. 292-293 as the default SMART-goal work surface and adds only a one-page experience-action companion. Day 5 submits only the four-page Individual High School and Career Plan.
- Protected the assessment map in code. The importer refuses to update the final plan unless exactly one existing assignment has the correct title, 100-point value, and `Major Assessments (60%)` group. Assignment 3094757 passed that gate, remains unpublished, retains upload, text-entry, and media-recording routes, and uses advisory rubric 32314 with four criteria and 16 raw points.
- Added an unpublished four-question unlimited-attempt practice Quiz that separates graduation, placement, military, and credential decisions. The Day 2 annotation assignment 3094756 remains unpublished, worth 0 points, and not graded; its Canvas-generated annotatable attachment is also locked.
- Rebuilt and visually inspected all six Week 2 PDFs. The final set totals fifteen intentional pages, down from twenty, with writing regions sized to the requested response and no accidental blank pages, clipping, or overflow. All twenty responsive Teacher and Student Guide renders also pass desktop and mobile inspection.
- Ran the required separate owner-style adversarial gate. The first pass blocked staging because a 2025 toolkit was treated as the current sole authority after the August 2026 Chapter 74 amendment. A narrow second pass caught cohort wording that could sound exclusive. After the current-rule and follow-on-cohort repairs, the final gate returned GO. Backup commit `3a733d71` was pushed before Canvas staging.
- Reconciled unpublished module 544403 to eighteen consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, the practice Quiz, the ungraded annotation, and `MAJOR 2: Individual High School and Career Plan`. All pages, interactives, assignments, and the module remain unpublished; all eleven page-referenced files, the annotation attachment copy, and all four Week 2 folders are locked.
- Final QA passes all 180 lesson contracts, both Week 2 templates, Python compilation, clean-diff checks, six strict worksheet builds, twenty responsive renders, the separate owner-style gate, and live module API verification with zero problems.

## 2026-08-10 - 4SW Week 3 aviation routes, systems, and action-planning repair

- Reconciled the week to FYF Transportation Cluster and Survey Project pp. 166-167, FYF Flight Line Fixers and Aviation Maintenance context, the authenticated district platform boundary, and current FAA, Air Force, BLS, and Irving ISD evidence. FYF remains the student-facing HQIM; dated public evidence supports route decisions without silently replacing the workbook or district applications.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. Day 1 captures survey quality, Day 2 captures a source-based route tradeoff, Days 3-4 separate team airport evidence from individual career and revision evidence, and Day 5 carries the private route and timed-action decision.
- Restored the full FYF survey process, including Step 4 Campaign. One shared three-page survey packet serves each team, while a private Canvas practice Quiz supplies individual survey-quality evidence. Accountable team roles reduce passive participation without turning the task into five duplicate packets.
- Reduced duplicate writing on Day 2. The two-page aviation route reference is posted or projected, and students record only the selected step, tradeoff, verification question, and recommendation in the four-page Aviation Route and Action Plan. Flight Line Fixers and Day 5 H&L App Exploration remain collapsed optional extensions.
- Rebuilt the Airport Design and Simulation Lab as four intentional pages. Pages 1-2 hold shared team planning and test evidence; pages 3-4 hold each student's role, work-product, timed iteration, scenario response, and revision reasoning. The separate one-page scenario card set is printed once per team.
- Rebuilt and visually inspected all six Week 3 PDFs. The coordinated set totals sixteen intentional pages with point-of-use word banks, complete response frames, and writing, mapping, and revision regions sized to the requested work. Default printing remains lower because the route guide is posted or projected and team materials are shared.
- Ran the required separate owner-style adversarial gate. The reviewer checked all twenty responsive renders, all sixteen PDF pages, exact contract parity, FYF campaign continuity, group-versus-individual evidence, optional disclosures, grading safeguards, and unpublished file-lock behavior. The gate returned GO with no release blocker. Backup commit `3ef5f4bb` was pushed before Canvas staging.
- Reconciled unpublished module 544404 to eighteen consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, the four-question unlimited-attempt survey practice Quiz, the private not-graded Airport Design and Simulation Lab, and `MINOR 1: Aviation Route and Action Plan`. All pages, interactives, assignments, and the module remain unpublished.
- Protected the assessment map in code. The importer refuses to update the route plan unless exactly one existing assignment has the correct title, 100-point value, and `Minor Assessments (40%)` group. Assignment 3094759 passed that gate and retains upload, text-entry, and media-recording routes. Lab assignment 3094758 remains worth 0 points and not graded; its Canvas-generated annotatable attachment is locked.
- Final QA passes all 180 lesson contracts, both Week 3 templates, Python compilation, clean-diff checks, six strict worksheet builds, twenty responsive renders, the separate owner-style gate, module API QA, and an independent live Canvas state check. All twelve page-referenced files, the annotation attachment, and all four Week 3 folders are locked.

## 2026-08-10 - 4SW Week 4 drone systems, rules, and evidence repair

- Reconciled the week to FYF Protecting Wildlife pp. 103-105, FYF Engineering Design and Drone Engineering context pp. 108-109, current FAA indoor, educational, and Part 107 boundaries, and one fixed BLS occupation-evidence set. FYF remains the district HQIM and default student surface; current FAA and BLS evidence supplies bounded rule and labor details without replacing the workbook story.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. Day 2 uses an individual five-question evidence check, Day 3 uses a four-question rules check plus a team gate only when needed, and Day 4 separates shared trials from individual iteration and two-occupation transfer evidence.
- Reduced the coordinated printable set from twenty-seven pages to seventeen. Day 1 uses FYF p. 105 by default and keeps the three-page Design Companion for no-workbook, enlarged, or annotation access. Day 2's two-page occupation reference is posted or projected. Day 3 prints only one readiness page per team when a test route is used. Day 4 uses two team pages plus one individual page. Day 5 keeps four distinct response jobs and a two-page student-visible rubric.
- Rebuilt all six Week 4 PDFs with point-of-use word banks, bilingual vocabulary cues, complete response frames, and task-proportional writing or drawing regions. All seventeen pages pass strict page-count and overflow checks and full-page visual inspection. The two licensed FYF images used in Canvas are each under 205 KB.
- Kept live flight optional and outside the grade. No outdoor student flight is part of the week. Indoor operation still requires campus and model approval; simulator and tabletop routes produce equal evidence; the Remote Pilot Certificate is described as a current pathway rather than a credential this lesson awards.
- Ran the required separate owner-style adversarial gate. The reviewer inspected all twenty responsive renders, all seventeen PDF pages, contract parity, workbook-first routing, EB supports, writing space, print burden, FAA boundaries, and grading safeguards. The gate returned GO before staging. Backup commit `f1cb36a3` was pushed before the first Canvas write.
- Reconciled unpublished module 544405 to twenty consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, two unlimited-attempt practice Quizzes, two private not-graded practice Assignments, and `MINOR 2: Drone Systems Evidence Brief`. All pages, interactives, assignments, and the module remain unpublished; all eight page-referenced files and all three Week 4 folders are locked.
- Protected the assessment map in code. The importer refuses to update the Evidence Brief unless exactly one existing assignment has the correct title, 100-point value, and `Minor Assessments (40%)` group. Assignment 3094762 passed that gate and retains upload, text-entry, and media-recording routes. Practice assignments 3094760 and 3094761 remain worth 0 points and not graded.
- The first live API QA exposed two obsolete Career Quiz questions retained from an earlier draft. The importer now deletes questions outside each builder-owned Quiz's exact managed set before updating or creating desired questions. The narrow independent recheck confirmed the cleanup is scoped and idempotent; backup commit `7c1b4c36` was pushed. Final live QA confirms exactly five Career Quiz questions and four Rule Quiz questions with zero module problems.
- Final QA passes all 180 lesson contracts, both Week 4 templates, Python compilation, clean-diff checks, six strict worksheet builds, twenty responsive renders, the separate owner-style gates, current Canvas API endpoint verification, and live module API verification with zero problems.

## 2026-08-10 - 4SW Week 5 automotive evidence and training-route repair

- Reconciled the week to FYF Crash Crew pp. 150-152 and the Irving automotive program context on pp. 168-169. FYF remains the student-facing HQIM and default work surface. Current ASE, TWC, TCC, BLS, and Irving ISD sources answer bounded credential, tuition, labor, campus, and enrollment questions without renaming the workbook programs.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. The exact 20-field canonical contract comparison and the coursewide 180-lesson contract QA both pass with zero issues.
- Reduced the custom printable set from twenty-seven pages to seventeen. Day 1 uses FYF p. 151 by default and keeps the three-page Crash Crew companion for no-workbook, enlarged, or annotation access. Days 2 and 4 use Canvas practice Quizzes first and keep their three-page and two-page packets as no-device routes. Day 3 retains a fixed three-career comparison, and Day 5 retains the four-part Minor brief plus student-visible rubric.
- Rebuilt all six Week 5 PDFs with point-of-use bilingual vocabulary, complete response frames, and writing regions sized to the requested evidence. All seventeen pages pass strict page-count and overflow checks and full-page visual inspection. The five licensed FYF images embedded in Canvas range from 115,941 to 195,261 bytes and use deferred loading.
- Kept credential and safety boundaries explicit. ASE Entry-Level is separated from professional ASE certification; employer learning is not automatically a Registered Apprenticeship; tuition figures retain year, residency, and exclusions; image evidence does not become a real vehicle diagnosis or repair procedure. H&L and Xello career browsing remain optional, and the earlier required Xello Save careers task is not repeated.
- Ran the required separate owner-style adversarial gate. The reviewer personally inspected all twenty responsive Canvas renders and all seventeen PDF pages, including response space, point-of-use EB help, workbook and Quiz routing, student-safe rubric language, and grading safeguards. The gate returned GO before staging. Backup commit `5fbe5bbf` was pushed before the Canvas write.
- Reconciled unpublished module 544406 to twenty consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, two unlimited-attempt practice Quizzes, two private not-graded practice Assignments, and `MINOR 3: Automotive Evidence Brief`. All pages, interactives, assignments, and the module remain unpublished.
- Protected the assessment map in code. The importer refuses to update the Evidence Brief unless exactly one existing assignment has the correct title, 100-point value, and `Minor Assessments (40%)` group. Assignment 3094765 passed that gate and retains upload, text-entry, and media-recording routes. Practice assignments 3094763 and 3094764 remain worth 0 points and not graded.
- Live QA confirms the ASE Quiz has exactly four multiple-choice items plus one essay response, and the source-evidence Quiz has exactly three multiple-choice items plus one essay response. All eleven referenced files, both Canvas-generated annotation attachments, and all three Week 5 folders are locked. Module API QA reports zero problems.
- Final QA passes both Week 5 templates, Python compilation, clean-diff checks, six strict worksheet builds, twenty responsive renders with zero horizontal overflow, the separate owner-style gate, and live Canvas API verification with every exact state check true.

## 2026-08-10 - 4SW Week 6 transferable-skills evidence and recovery repair

- Reconciled the week to FYF analytical-reasoning and truck-evidence work on pp. 153-155, current SkillsUSA, TSA, ASE, FAA, NSPE, and AOPA organization boundaries, and the 4SW assessment map. FYF remains the default student work surface on Day 1; H&L is optional, and no required Xello or eDynamic task is inserted into the week.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. The repaired evidence jobs directly demonstrate transfer among careers, organization type and access, and the four professional characteristics in d(4)(F).
- Reduced the fallback printable set from thirty-one pages to nineteen. Day 1 uses FYF pp. 154-155 by default; Days 2-4 use private Canvas responses or practice Quizzes first; Day 5 opens only for teacher-approved recovery or replacement. The PDFs remain enlarged, no-workbook, absence, or no-device routes rather than an automatic class print stack.
- Rebuilt all six Week 6 PDFs with point-of-use bilingual vocabulary, complete bracketed response frames, and response regions sized to the requested evidence. The owner-style gate caught Markdown swallowing nine underscore blanks; after replacing them with explicit prompts, all nineteen PDF pages passed the narrow visual recheck. All twenty responsive Canvas renders also passed.
- Recast the old draft reflection as `RECOVERY: Private Mid-Year Evidence Reflection`. Assignment 3094768 remains unpublished, worth 0 points, not graded, and accepts upload, private text, or private media. It is not an automatic third Major or fourth Minor. Practice assignments 3094766 and 3094767 are also unpublished and not graded.
- Added two unpublished, unlimited-attempt practice Quizzes. Quiz 281894 contains exactly four multiple-choice items plus one essay decision; Quiz 281895 contains exactly five multiple-choice items plus one essay evidence audit. Both stay outside the grade map.
- Ran the required separate owner-style and source-safety gates. The first passes blocked release on missing contract rendering, stale Quiz questions, broken PDF frames, and unsafe module cleanup. The final importer renders the exact contracts, prunes obsolete Quiz questions, retains exactly one typed module item per desired tuple, deletes retired or duplicate links, and verifies exact count and order. Backup commits `d98b3e0b` and `0e603c49` were pushed before the final Canvas write.
- Reconciled unpublished module 544407 to twenty consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, two practice Quizzes, two private not-graded practice Assignments, and the private recovery Assignment. All ten pages, five interactives, and the module remain unpublished. All nine page-referenced files, both Canvas-generated annotation attachments, and the Week 6 folders are locked.
- Final QA passes all 180 lesson contracts, both Week 6 templates, Python compilation, clean-diff checks, six strict worksheet builds, twenty responsive renders, nineteen PDF pages, both independent gates, and live module API verification with zero problems.

## 2026-08-10 - 5SW Week 1 architecture evidence and workbook-first repair

- Reconciled the week to FYF Architecture & Construction, Safety Supervisor, and Unexpected Architecture work; one consistent May 2024 BLS salary basis; bounded architecture-registration evidence; and the current MacArthur ACE pathway labels. FYF remains the default student surface. Public evidence is dated and labeled instead of silently replacing district HQIM.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. Day 2 carries the scored preparation-and-pay comparison; Days 3-4 collect direct career-role work-product evidence; Day 5 closes with a three-role cluster synthesis.
- Reduced duplicate printing and platform dependence. Days 1 and 5 use FYF first. Canvas and paper are the immediately available Day 3-4 routes; Tinkercad remains optional behind district approval, a tested teacher-managed Classroom, and a working export path. No improvised student account creation is required.
- Rebuilt the seven coordinated printable artifacts around missing evidence rather than reprinting workbook tasks. The final set totals nineteen intentional pages, with a four-page landscape Minor comparison, point-of-use bilingual vocabulary and complete frames, and drawing or writing space sized to the requested response. The Day 5 fallback is two pages and does not ask students to redraw the team design.
- Protected the assessment map in code. The importer refuses to update `MINOR 1: Three-Career Architecture Comparison` unless exactly one existing assignment is worth 100 points in `Minor Assessments (40%)`. Assignment 3094769 passed that gate and remains unpublished. Practice assignments 3094770-3094772 and formative portfolio 3094773 remain unpublished, worth 0 points, and not graded; Week 1 has no Major.
- Added unpublished practice Quiz 281896 with unlimited attempts and exactly four multiple-choice evidence checks. Two live import attempts exposed a nullable `position` field and an asynchronous form-encoding edge case. The repaired importer uses Canvas's Classic Quiz reorder endpoint with an interleaved form payload, reloads, and fails closed unless the four question names return in exact order. Backup commits `ac0a20d1` and `06333c03` preserve the repairs.
- Ran the required separate owner-style and importer-safety gates. The first pass blocked staging on a conditional ungraded statement and a stale fallback-page description. After repair, the visual gate returned GO. The Quiz transport repair also received an independent GO after exact encoding and idempotence review.
- Reconciled unpublished module 544408 to twenty-one consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, four private not-graded practice or formative Assignments, the mapped Minor, and the practice Quiz. All ten pages, six interactives, and the module remain unpublished. All fourteen referenced files and all three Week 1 folders are locked.
- Final QA passes all 180 lesson contracts, both Week 1 templates, Python compilation, clean-diff checks, seven strict worksheet builds, twenty responsive renders, nineteen PDF pages, both independent gates, exact live assignment and Quiz safeguards, and live module API verification with zero problems.

## 2026-08-10 - 5SW Week 2 civil-engineering systems and evidence repair

- Reconciled the week to FYF Engineering and systems-thinking pp. 103 and 174-175, FYF Mission to Mars pp. 106-107, dated civil-engineering and emerging-specialty evidence, and current bounded assessment guidance. FYF remains the default student work surface on Days 1 and 5. H&L remains optional, and no new Xello or eDynamic requirement is inserted.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. Day 2 carries assessment-impact and emerging-work evidence; Days 3-4 collect direct role, work-product, test, and revision evidence; Day 5 is a private formative synthesis rather than an unplanned Major.
- Made the fixed three-sample bridge dataset the complete Day 4 route. Physical testing is only an optional teacher demonstration after a separate tested kit, safety, objective-stop, and scheduling gate; fabrication and live testing do not determine the grade.
- Rebuilt the seven coordinated printables as nineteen intentional pages. The Day 2 Minor packet was reduced from four pages to three without shrinking its response jobs. Point-of-use bilingual vocabulary, complete response frames, and drawing or writing regions match the requested work.
- Ran independent code and owner-style visual gates. The visual gate caught a fixed-result table printed above the prediction prompt and a response line touching a footer. The final packet separates prediction on p. 1 from the teacher-timed result reveal on p. 2, and the narrow recheck returned GO. Backup commit `c79ec491` was pushed before Canvas staging.
- Reconciled unpublished module 544409 to twenty-one consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, four private not-graded practice or formative Assignments, `MINOR 2: Assessment and Emerging-Specialty Evidence`, and one unlimited-attempt practice Quiz. All pages, interactives, and the module remain unpublished.
- Protected the assessment map in code. Assignment 3094774 remains worth 100 points in `Minor Assessments (40%)`; practice and formative assignments 3094775-3094778 remain worth 0 points and not graded. Quiz 281897 is unpublished, has unlimited attempts, and contains exactly four ordered questions after stale and duplicate cleanup.
- Final live QA confirms module 544409 has exactly twenty-one ordered items, ten unpublished pages, the correct Minor group and weight, zero module problems, a locked support folder, and all twelve referenced FYF and printable files locked. Coursewide contract QA remains at 180 Teacher and 180 Student contracts with zero issues.

## 2026-08-10 - 5SW Week 3 construction routes, labor evidence, and observation repair

- Reconciled the week to FYF Construction context and Spot the Problem work, the current MacArthur ACE pathway label, dated Registered Apprenticeship and career-organization evidence, and one fixed May 2024 BLS comparison basis. FYF remains the student-facing HQIM. H&L stays optional, and no new Xello or eDynamic completion task is inserted.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. Day 2 now carries ordered enrollment and organization-access evidence, Day 3 carries the scored labor classification, and Days 4-5 separate visual observation from professional inference and individual oral communication.
- Rebuilt seven coordinated printable artifacts as twenty-seven intentional pages. Day 1 uses three fixed career cards; Day 2 compares two documented routes and one professional association; Day 3 uses four same-basis occupations and a published classroom comparison rule; Days 4-5 share one five-page fictional evidence report. The seven-page enlarged observation log remains an optional support and is not linked or printed by default.
- Kept the visual-observation task within a middle-school professional boundary. Students describe what is visible, state what it could indicate, name a qualified next role and work product, and record what the image cannot prove. The activity does not become a real home inspection, diagnosis, repair recommendation, cost estimate, or purchase decision.
- Protected the assessment map in code. Assignment 3094781 remains worth 100 points in `Minor Assessments (40%)`, uses upload, text-entry, and student-annotation routes, and stays unpublished. Practice assignments 3094779-3094780 and formative report assignment 3094783 remain unpublished and worth 0 points. Because Canvas removes online submission routes when Display Grade is set to Not Graded, these private evidence collectors use Percentage with zero points and `Do not count this assignment toward the final grade` enabled.
- Ran the required separate owner-style adversarial gate. The reviewer personally inspected all twenty responsive Canvas renders and all twenty-seven PDF pages. The sole visual blocker was a clipped even-page footer. After the shared print-CSS repair and a full rebuild, the narrow recheck returned GO. Backup commits `75a7e01c` and `7219580a` were pushed before the final Canvas write.
- Reconciled unpublished module 544410 to nineteen consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, two private practice Assignments, `MINOR 3: Construction Labor-Evidence Classification`, and the shared formative report Assignment. All ten pages, four assignments, and the module remain unpublished. Support folder 1155248 is locked; six printable files 14570242-14570248 and six licensed visual files 14562600-14562605 are locked through the importer.
- Final live Canvas verification confirms the exact nineteen-item order, Teacher and Student contract rendering with no unresolved tokens, Minor 3 at 100 points in `Minor Assessments (40%)`, all three zero-point formative collectors omitted from the final grade, private upload/text/media routes restored where intended, and module 544410 unpublished.

## 2026-08-10 - 5SW Week 4 skilled-trades evidence and professional-communication repair

- Reconciled the week to FYF Skilled Trades and HVAC context, FYF water-line response work on pp. 185-190 and 194-195, current route and labor evidence, and bounded middle-school professional communication. FYF remains the default work surface on Days 2 and 5; custom companions supply only the evidence, safety boundary, or individual response the workbook does not capture.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. Point-of-use bilingual vocabulary and complete response frames appear before the step that uses them rather than in a collapsed support block.
- Reduced the six coordinated printable artifacts from twenty-eight pages to twenty-one. Day 2's six-page safe-label route is an absence, no-workbook, or enlarged-access scaffold rather than automatic duplicate printing. Day 5 uses FYF pp. 194-195 for the team response and a two-page individual companion for the scored evidence.
- Kept the Day 5 communication standard oral. Students may brief live, in a teacher conference, through a private audio/video recording, or with an accommodation-aligned oral/AAC route. A written plan or transcript may scaffold access but does not by itself demonstrate d(4)(C).
- Protected the assessment map in code. Assignment 3094788 remains the single `MAJOR 1: Skilled-Trades Classification and Individual Response`, worth 100 points in `Major Assessments (60%)`, and unpublished. Days 1-4 practice collectors remain private, zero-point, omitted from the final grade, and unpublished.
- Ran the required separate owner-style release gate. The reviewer inspected all twenty responsive Canvas renders and all twenty-one PDF pages, including workbook-first routing, point-of-use EB support, proportional response space, the oral-evidence boundary, grading safeguards, locked files, and exact module cleanup. The gate returned GO before staging. Backup commits `8bafb69b`, `311cb82c`, and `8850c7f9` were pushed before or during the controlled Canvas write.
- Reconciled the unpublished `5SW Wk4: Skilled Trades — Evidence, Routes, and Communication` module to twenty ordered items: five Day subheaders, five Teacher Guides, five Student Guides, four private practice Assignments, and the mapped Major. The importer keeps exactly one typed item for each expected object, removes stale or duplicate module links, reloads, repositions, and asserts the exact count and order.
- Live signed-in Canvas verification confirms the exact module name and twenty-item structure, the rendered Day 5 Student contract, assignment 3094788 at 100 points, private annotation/upload/text/media submission routes, the student-safe advisory rubric, and unpublished state. All six support PDFs and eight licensed visuals remain in locked Canvas folders.

## 2026-08-10 - 5SW Week 5 personal-budget evidence and financial-aid literacy repair

- Reconciled the week to FYF Rung 3 career and lifestyle evidence, Xello as the preferred localized salary source, fixed May 2024 BLS comparison cards, a dated February 2026 Dallas County cost scenario, and current Federal Student Aid, TEA, and Registered Apprenticeship boundaries. HQIM remains the student-facing starting point; public evidence fills labeled data gaps without relabeling the workbook or platform.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. Days 1-3 build the budget evidence progressively, Day 4 separates reduce-cost, earn-money, and borrow-money routes, and Day 5 carries d(5)(D) and d(5)(E) through one self-contained three-career portfolio.
- Kept all scenarios fictional and bounded. Students do not convert a career median into take-home pay, disclose family finances, complete a live FAFSA or TASFA, enter account or immigration data, or treat a positive salary-minus-target screen as proof of affordability or career fit.
- Rebuilt the six coordinated printables as eighteen intentional pages: three-page source/lifestyle target, four-page Dallas County budget, two-page location comparison, three-page paying-for-training guide, four-page portfolio, and two-page student-safe rubric. Point-of-use bilingual vocabulary, complete response frames, and writing space match each evidence job. A shared print-CSS footer repair keeps continuation-page labels visible.
- Ran the required separate owner-style adversarial gate. The reviewer personally inspected all twenty responsive Canvas renders and all eighteen PDF pages, then verified contract parity, grading safeguards, exact Quiz cleanup and order, typed module cleanup, locking, and unpublished state. The gate returned GO. Backup commit `8501b940` was pushed before Canvas staging.
- Reconciled unpublished module 544412 to twenty consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, three private grade-neutral practice Assignments, the five-question unlimited-attempt practice Quiz, and `MAJOR 2: Personal Budget Evidence Portfolio`. All pages, interactives, assignments, and the module remain unpublished.
- Protected the assessment map in code. Assignment 3094792 remains worth 100 points in `Major Assessments (60%)`, is counted in the final grade, retains annotation, upload, text-entry, and media-recording routes, and has four rubric criteria. Practice assignments 3094789-3094791 remain worth 0 points, omitted from the final grade, and unpublished. Quiz 281898 is an unpublished practice Quiz with unlimited attempts and exactly five ordered questions.
- Live API verification confirms the exact twenty-item order, ten unpublished pages, correct Major group and weight, zero module problems, locked support folder 1155252, six locked printable files 14570333-14570338, and two locked FYF visual files 14562634-14562635. Coursewide contract QA remains at 180 Teacher and 180 Student contracts with zero issues.

## 2026-08-10 - 5SW Week 6 real-estate licensing, labor evidence, and formative synthesis repair

- Reconciled the week to FYF Flip This House pp. 238-239, the current Texas Sales Agent route, bounded property-management and appraisal distinctions, dated BLS labor evidence, and the current MacArthur Real Estate Marketing label. FYF remains the student-facing HQIM. H&L and eDynamic remain optional, and no repeat Xello requirement is inserted.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. Day 5 is formative synthesis only: it is not a third Major and does not replace a prior grade.
- Reduced the printable package from twenty-six pages to ten student-work pages plus a one-page rubric. Day 3 uses FYF pp. 238-239 first and adds only a one-page math and entrepreneurship audit. Day 4 uses one two-page fixed evidence guide plus the retryable Quiz as feedback rather than a duplicate five-page packet.
- Added point-of-use bilingual vocabulary, complete response frames, calculators and formulas where used, private asynchronous audio/recorded/AAC routes, and response regions sized to the requested work. The Day 5 oral evidence may be submitted privately; a written plan may scaffold but does not substitute for d(4)(C).
- Ran the required separate owner-style adversarial gate. The reviewer inspected all twenty responsive Canvas renders and all eleven PDF pages. The first pass caught a TREC route list already printed in answer order. The repaired packet now presents a genuinely mixed sequence, and the teacher key matches the row order. A second narrow gate approved the folder-wide lock repair. Backup commits `215987ef`, `da22a038`, and `cdf0e4ad` were pushed before the final Canvas write.
- Reconciled unpublished module 544413 to twenty consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, three private grade-neutral practice Assignments, the five-question unlimited-attempt practice Quiz, and the private formative Evidence Brief. All ten pages, five interactives, and the module remain unpublished.
- Practice assignments 3094793-3094795 and formative assignment 3094796 remain worth 0 points, use Percentage only to preserve private online submission routes, are omitted from the final grade, and remain unpublished. Quiz 281899 remains unpublished, unlimited-attempt, and contains exactly five ordered questions.
- Live API verification confirms the exact twenty-item order, ten unpublished pages, zero module problems, locked support folder 1155254, locked licensed-visual folder 1155255, six locked printable files 14572251-14572306, and locked FYF visual files 14562672-14562673. The importer also locked the older unlinked p. 240 visual left in the folder, so all nine Week 6 files are private. Coursewide contract QA remains at 180 Teacher and 180 Student contracts with zero issues.

## 2026-08-10 - 6SW Week 1 education routes, service, and evidence-portfolio repair

- Reconciled the week to FYF Community Classroom pp. 213-215, Teach Through Play pp. 216-217, and Education program context pp. 218-219. FYF remains the student-facing HQIM and default work surface on Days 1 and 4. FYF p. 220 H&L exploration, Xello Discover learning pathways, and eDynamic 7.2 remain optional extensions rather than required completion evidence.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. Current TEA classroom-teacher and Educational Aide boundaries and the current Irving public CTE listing are labeled by source, date, and evidence limit.
- Rebuilt the six coordinated printable artifacts as fifteen intentional pages: three-page Community Classroom companion, three-page Texas Education Routes guide, two-page job-evidence comparison, three-page Teach Through Play and Service companion, three-page Education Evidence Portfolio, and one-page student-visible rubric. Every multi-sentence or drawing job has proportional space, point-of-use bilingual vocabulary, and a complete bracketed response frame.
- Kept each response route necessary and nonduplicative. Students use the FYF workbook first where it supplies the task, then choose one Canvas, annotation, paper, enlarged, or absence companion route. The Day 3 fixed cards and retryable Quiz divide written evidence from immediate feedback rather than asking students to answer the same items twice. A supplied library-tutoring scenario and a fixed missing-work evidence strip prevent partner attendance, prior absence, or personal disclosure from blocking the lesson.
- Protected the assessment map in code. Assignment 3094800 remains worth 100 points in `Minor Assessments (40%)`, is counted in the final grade, retains annotation, upload, text-entry, and media-recording routes, and includes the advisory raw-16-to-100 conversion note. Practice assignments 3094797-3094799 remain unpublished, worth 0 points, and omitted from the final grade.
- Ran the required separate owner-style adversarial gate. The reviewer personally inspected all twenty responsive Canvas renders and all fifteen PDF pages. The gate blocked release on one stale p. 220 requirement and on builder-only loss of the rubric conversion note. Both were repaired; the narrow recheck returned GO. Backup commit `bfff7723` was pushed before the Canvas write.
- Reconciled unpublished module 544414 to twenty consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, three private grade-neutral practice Assignments, the five-question unlimited-attempt practice Quiz, and `MINOR 1: Education Evidence Portfolio`. All pages, interactives, assignments, and the module remain unpublished.
- Live API verification confirms the exact twenty-item order, ten unpublished pages, correct Minor group and weight, the live scoring note, exactly five ordered Quiz questions, zero module problems, locked support folder 1155257, locked licensed-visual folder 1155258, six locked printable files 14573872-14573877, and seven locked FYF files 14562684-14562690. Coursewide contract QA remains at 180 Teacher and 180 Student contracts with zero issues.

## 2026-08-10 - 6SW Week 2 resume, revision, and job-search evidence repair

- Reconciled the week to FYF Behind the Microphone pp. 270-271, FYF Attention to Detail audio-cue work pp. 272-273, FYF Merch Mode pp. 256-258, CareerOneStop resume guidance, current BLS Graphic Designers evidence, and the current Irving Digital Communication and Graphic Design pathway label. FYF remains the student-facing HQIM and default work surface on Days 1, 3, and 5. Xello Resume Builder and eDynamic job-search content remain supplemental rather than required completion evidence.
- Added exact Topic, Objective, TEKS, and Demonstration of Learning contracts to all five Teacher Facilitator Guides and matching Topic, I can, and Show my learning contracts to all five Student Guides. The Day 5 contract explicitly includes the authorized next action required by the Minor evidence package.
- Reduced the coordinated printable set from thirty-five pages to thirteen intentional pages. The six final artifacts supply only missing individual evidence, a fictional resume model and actual one-page assembly surface, a fixed fictional opportunity, a seven-step trace, an audience test, and a student-visible rubric. Point-of-use bilingual vocabulary, complete response frames, and writing regions match each response job.
- Kept the resume and job-search work private and bounded. Students do not publish a resume, enter sensitive contact or reference data, create an external account, contact an employer, or apply through the fictional posting. Paid work is not required; true school, project, activity, service, and responsibility evidence is accepted. Merch Mode remains formative and does not add a second scored design artifact.
- Protected the assessment map in code. Assignment 3094804 remains worth 100 points in `Minor Assessments (40%)`, is counted in the final grade, stays unpublished, and includes the advisory raw-16-to-100 conversion note. Practice assignments 3100128, 3094802, and 3094803 remain unpublished, worth 0 points, and omitted from the final grade. Quiz 281901 is an unpublished unlimited-attempt practice Quiz with exactly five ordered questions.
- Ran the required separate owner-style adversarial gate. The reviewer personally inspected all twenty responsive Canvas renders and all thirteen PDF pages. The gate caught a missing Day 5 next-action phrase and an inaccurate plural in the current district pathway label. Both were repaired, and the narrow recheck returned GO. Backup commit `87f9ec39` was pushed before Canvas staging.
- Reconciled unpublished module 544415 to twenty consecutive items: five Day subheaders, five Teacher Guides, five Student Guides, three private grade-neutral practice Assignments, the five-question practice Quiz, and `MINOR 2: Resume, Revision, and Job-Search Evidence`. All ten pages, five interactives, and the module remain unpublished. Support folder 1155259 and licensed-visual folder 1155260 are locked; all six printable files 14575253-14575304 and all eight FYF visual files 14562702-14562709 are locked.
- Added a durable mapped-assignment submission panel to the Day 5 Student Guide. The first coursewide audit showed that page rebuilds could erase this panel and that its text scanner recognized only older student-contract labels. The importer now recreates exactly one panel and one normalized Canvas Assignment link, while the verifier accepts both `Objective`/`Show your learning` and the approved `I can`/`Show my learning` labels. Older modules still carry separate submission-panel and legacy-page cleanup work; that coursewide backlog is not reported as a Week 2 pass.
- Final module QA reports zero problems, exact item order, ten unpublished pages, the protected Minor state, five Quiz questions, fourteen locked referenced files, and one live mapped-submission panel. Coursewide contract QA remains at 180 Teacher and 180 Student contracts with zero issues.
