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
- Program correction: the current public district name is Dental at Singley Academy. Medical Records Specialist remains career exploration; the module does not promise a current Irving Medical Billing program or credential.
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
