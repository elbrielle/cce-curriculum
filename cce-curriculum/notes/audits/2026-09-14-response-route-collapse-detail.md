# Response-Route Collapse Audit — Canvas course 98060 (Irving ISD CCE)

Read-only audit, 2026-09-14. Sources: `.tmp/canvas-dump-20260914/canvas/` (live dump, 448 pages / 1267 files),
`build/google_docs/student_response_link_selector_inventory.json`, `build/google_docs/student_response_route_registry.json`,
`.tmp/docs-trusted-read/20260825-current/<DAY>/document-text.md`, `docs/resources/worksheets/`, `build/worksheet_sources/`.

## Headline numbers

- 180 day routes, 180 student pages, 180 Google Docs. Trusted-read doc text present for **180/180** days (no missing docs).
- **199 `docs.google.com/.../copy` anchors** across the 180 student pages; **185 anchors** are recorded in the selector inventory as retargeted response-work links.
- Of the 185 retargeted anchors, **177 pointed at worksheet PDFs** (`docs/resources/worksheets/`) and **8 at exit-ticket PDFs** (`docs/resources/exit-tickets/`).
- **Every one of the 180 Google Docs is a single-page exit ticket / mini-case.** Body text ranges 906–1840 characters (median 1236). None reproduces a worksheet's section headings; the maximum heading-overlap score against any retargeted worksheet source was below 0.3, and 176/177 scored below 0.3.
- **170 of 180 days** lose at least one artifact: the retargeted PDF is neither reproduced in the Google Doc nor still linked from the student page. **193 distinct PDF artifacts** are unreachable for students (183 worksheets + 7 exit tickets still on a teacher page; 3 not on any page at all).
- **15 days** are multi-anchor collapses (2+ distinct PDFs retargeted to the same single Doc).
- OneNote status is `pending` for **180/180** routes, so there is no alternate response home.

## Flag definitions

- `COLLAPSED-MULTI` — 2 or more distinct PDFs on that day now point at one Google Doc.
- `COLLAPSED` — one retargeted PDF (or an `is_response_route_candidate=true` worksheet) is absent from the Doc content and no longer linked from the student page.
- `docMatch` — fraction of that worksheet's `##` section headings found in the Google Doc body text. 0.00 means none of the worksheet's structure survived into the Doc.

## 1. Full 180-day table

| # | day_key | Google Doc title | Doc actually contains | Retargeted PDFs -> student-page reachability | is_response_route_candidate worksheets | OneNote | Flag |
|---|---|---|---|---|---|---|---|
| 1 | 1SW-Wk0-Day1 | CCE First-Week Goal Setting | exit-ticket-only (⟦EMPTY PARAGRAPH⟧; 1544 chars body) | cce-first-week-goal-setting.pdf [worksheet] #14615030 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | (none) | pending | COLLAPSED |
| 2 | 1SW-Wk0-Day2 | CCE \| 1SW Wk0 Day 2 \| Who Are You at Work? | exit-ticket-only (H&L Setup and Discover Your Core; 1840 chars body) | (none) | (none) | pending | - |
| 3 | 1SW-Wk0-Day3 | CCE \| 1SW Wk0 Day 3 \ **WRONG-DAY CONTENT (= 1SW Wk0 Day 2 ticket)** | Work Values and Building Blocks | exit-ticket-only (H&L Setup and Discover Your Core; 1840 chars body) | (none) | (none) | pending | - |
| 4 | 1SW-Wk0-Day4 | CCE \| 1SW Wk0 Day 4 \ **WRONG-DAY CONTENT (= 1SW Wk0 Day 2 ticket)** | My Career Journey Reflection | exit-ticket-only (H&L Setup and Discover Your Core; 1840 chars body) | my-career-journey.pdf [worksheet/2p] #14615031 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | (none) | pending | COLLAPSED |
| 5 | 1SW-Wk0-Day5 | CCE \| 1SW Wk0 Day 5 \ **WRONG-DAY CONTENT (= 1SW Wk0 Day 2 ticket)** | Career Perks, Neutrals, and Quirks | exit-ticket-only (H&L Setup and Discover Your Core; 1840 chars body) | (none) | (none) | pending | - |
| 6 | 1SW-Wk1-Day1 | CCE \| 1SW Wk1 Day 1 \| Manufacturing Cluster Tour - More Than Assembly Lines | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1153 chars body) | 1sw-wk1-day1-manufacturing-cluster-tour-more-than-assembly-lines.pdf [exit-ticket] #14518997 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 \|\| manufacturing-pathways-scaffold.pdf [worksheet/1p] #14518990 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | manufacturing-pathways-scaffold.pdf/1p #14518990 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED-MULTI |
| 7 | 1SW-Wk1-Day2 | CCE \| 1SW Wk1 Day 2 \| Machine Breakdown Mystery + Hat Research | exit-ticket-only (Career and College Explorations - Mini-Case; 1106 chars body) | (none) | career-research-worksheet.pdf/1p #14517430,14565289,14580290,14580292 inDoc=no student=NOT-LINKED teacher=LINKED \|\| technician-checklist-scaffold.pdf/1p #14518991 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 8 | 1SW-Wk1-Day3 | CCE \| 1SW Wk1 Day 3 \| Designing Metalworks + Job References | exit-ticket-only (Career and College Explorations - Ranked Justification; 1283 chars body) | (none) | (none) | pending | - |
| 9 | 1SW-Wk1-Day4 | CCE \| 1SW Wk1 Day 4 \| Sphero Factory Floor + Task Bot in Action (Part 1) | exit-ticket-only (Career and College Explorations - Decision Tree; 1347 chars body) | 1sw-wk1-robots-for-crayons-action-plan.pdf [worksheet/2p] #14564524 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 1sw-wk1-robots-for-crayons-action-plan.pdf/2p #14564524 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 10 | 1SW-Wk1-Day5 | CCE \| 1SW Wk1 Day 5 \| Sphero Run-Through + Task Bot Presentations + Manufacturing Favorites | exit-ticket-only (Career and College Explorations - Concept Map; 1505 chars body) | (none) | (none) | pending | - |
| 11 | 1SW-Wk2-Day1 | CCE \| 1SW Wk2 Day 1 \| IT Cluster Tour - The 5 Pathways | exit-ticket-only (Career and College Explorations - Venn Diagram; 1116 chars body) | 1sw-wk2-day1-it-cluster-tour-four-irving-programs-of-study.pdf [exit-ticket] #14519034 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 \|\| wk2-it-programs-scaffold.pdf [worksheet/1p] #14519022 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | wk2-it-programs-scaffold.pdf/1p #14519022 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED-MULTI |
| 12 | 1SW-Wk2-Day2 | CCE \| 1SW Wk2 Day 2 \| Programming Pathway Deep-Dive - Software, Web, App, Game | exit-ticket-only (Career and College Explorations - Mini-Case; 1250 chars body) | 1sw-wk2-day2-programming-pathway-deep-dive-software-web-app-game.pdf [exit-ticket] #14519035 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 \|\| wk2-it-salary-comparison.pdf [worksheet/5p] #14580354 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | wk2-it-salary-comparison.pdf/5p #14580354 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED-MULTI |
| 13 | 1SW-Wk2-Day3 | CCE \| 1SW Wk2 Day 3 \| IT Salary Showdown - Comparing 3 Programming Careers | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1148 chars body) | 1sw-wk2-day3-powerskill-resilience-it-salary-showdown.pdf [exit-ticket] #14519036 -> student:NOT-LINKED; teacher:no docMatch=0.00 \|\| wk2-flip-the-failure-scaffold.pdf [worksheet/1p] #14519030 -> student:NOT-LINKED; teacher:no docMatch=0.00 \|\| wk2-it-salary-comparison.pdf [worksheet/5p] #14580354 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | wk2-bls-data-guide.pdf/2p #14580356 inDoc=no student=LINKED teacher=LINKED \|\| wk2-flip-the-failure-scaffold.pdf/1p #14519030 inDoc=no student=NOT-LINKED teacher=no \|\| wk2-it-salary-comparison.pdf/5p #14580354 inDoc=yes student=NOT-LINKED teacher=LINKED | pending | COLLAPSED-MULTI |
| 14 | 1SW-Wk2-Day4 | CCE \| 1SW Wk2 Day 4 \| Code.org Hour of Code (Day 1) | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1060 chars body) | 1sw-wk2-day4-code-org-hour-of-code-day-1.pdf [exit-ticket] #14519037 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | (none) | pending | COLLAPSED |
| 15 | 1SW-Wk2-Day5 | CCE \| 1SW Wk2 Day 5 \| Hour of Code (Day 2) + Pathway Fit + IT Favorites | exit-ticket-only (Career and College Explorations - Concept Map; 1327 chars body) | (none) | wk2-day5-it-pathway-decision.pdf/1p #14519033 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 16 | 1SW-Wk3-Day1 | CCE \| 1SW Wk3 Day 1 \| Networking Systems Pathway + Transferable Skills | exit-ticket-only (Career and College Explorations - Venn Diagram; 1058 chars body) | 1sw-wk3-day1-networking-systems-pathway-transferable-skills.pdf [exit-ticket] #14519360 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 \|\| wk3-transferable-skills-list.pdf [worksheet/1p] #14519351 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | wk3-networking-career-cards.pdf/2p #14580294 inDoc=yes student=LINKED teacher=LINKED \|\| wk3-transferable-skills-list.pdf/1p #14519351 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED-MULTI |
| 17 | 1SW-Wk3-Day2 | CCE \| 1SW Wk3 Day 2 \| Website Design (Part 1) - Read, Plan, Choose | exit-ticket-only (Career and College Explorations - Mini-Case; 1265 chars body) | 1sw-wk3-day2-website-revamp-audit-a-real-site.pdf [exit-ticket] #14519361 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 \|\| wk3-ux-audit-scaffold.pdf [worksheet/1p] #14519352 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | wk3-ux-audit-scaffold.pdf/1p #14519352 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED-MULTI |
| 18 | 1SW-Wk3-Day3 | CCE \| 1SW Wk3 Day 3 \ **WRONG-DAY CONTENT (= 1SW Wk0 Day 2 ticket)** | From Wireframe to Wow — Build the Screens | exit-ticket-only (H&L Setup and Discover Your Core; 1840 chars body) | wk3-wireframe-template.pdf [worksheet/1p] #14519353 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | wk3-wireframe-template.pdf/1p #14519353 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 19 | 1SW-Wk3-Day4 | CCE \| 1SW Wk3 Day 4 \| Emerging Tech Research - AI, Cloud, Data Science | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1301 chars body) | wk3-day4-career-comparison.pdf [worksheet/1p] #14519358 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 \|\| wk3-emerging-tech-research-template.pdf [worksheet/2p] #14580295 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | wk3-day4-career-comparison.pdf/1p #14519358 inDoc=no student=NOT-LINKED teacher=LINKED \|\| wk3-emerging-tech-research-template.pdf/2p #14580295 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED-MULTI |
| 20 | 1SW-Wk3-Day5 | CCE \| 1SW Wk3 Day 5 \| Mini-Presentations + Xello Skills + Wk3 Wrap-Up | exit-ticket-only (Career and College Explorations - Concept Map; 1431 chars body) | wk3-day5-learning-style-connection.pdf [worksheet/1p] #14662874 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | wk3-day5-learning-style-connection.pdf/1p #14662874 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 21 | 1SW-Wk4-Day1 | CCE \| 1SW Wk4 Day 1 \| IT Support Pathway Exploration | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1282 chars body) | wk4-day1-career-interest-check.pdf [worksheet/1p] #14662886 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | wk4-day1-career-interest-check.pdf/1p #14662886 inDoc=no student=NOT-LINKED teacher=LINKED \|\| wk4-it-support-career-cards.pdf/2p #14519372 inDoc=yes student=LINKED teacher=LINKED | pending | COLLAPSED |
| 22 | 1SW-Wk4-Day2 | CCE \| 1SW Wk4 Day 2 \| Certification Deep-Dive - CompTIA Roadmap | exit-ticket-only (Career and College Explorations - Ranked Justification; 1235 chars body) | wk4-day2-route-decision.pdf [worksheet/1p] #14519377 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 \|\| wk4-education-pathway-comparison.pdf [worksheet/2p] #14519375 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | wk4-day2-route-decision.pdf/1p #14519377 inDoc=no student=NOT-LINKED teacher=LINKED \|\| wk4-education-pathway-comparison.pdf/2p #14519375 inDoc=yes student=NOT-LINKED teacher=LINKED | pending | COLLAPSED-MULTI |
| 23 | 1SW-Wk4-Day3 | CCE \| 1SW Wk4 Day 3 \| Help Desk Simulator (MakeCode Day 1) | exit-ticket-only (Career and College Explorations - Decision Tree; 1168 chars body) | 1sw-wk4-day3-help-desk-simulator-makecode-day-1.pdf [exit-ticket] #14519383 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 \|\| wk4-help-desk-program-evidence.pdf [worksheet/2p] #14565268 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 \|\| wk4-troubleshooting-step-sort-cards.pdf [worksheet/1p] #14519380 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | wk4-help-desk-program-evidence.pdf/2p #14565268 inDoc=no student=NOT-LINKED teacher=LINKED \|\| wk4-help-desk-scenario-cards.pdf/1p #14519378 inDoc=no student=LINKED teacher=LINKED \|\| wk4-makecode-starter-blocks.pdf/2p #14565267 inDoc=no student=LINKED teacher=LINKED \|\| wk4-troubleshooting-step-sort-cards.pdf/1p #14519380 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED-MULTI |
| 24 | 1SW-Wk4-Day4 | CCE \| 1SW Wk4 Day 4 \| Refine the Help Desk Tool + Customer Service Role-Play | exit-ticket-only (Career and College Explorations - Diagnostic MCQ; 1367 chars body) | wk4-day4-customer-service-check.pdf [worksheet/1p] #14565271 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 \|\| wk4-help-desk-role-play-script.pdf [worksheet/2p] #14565269 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | wk4-day4-customer-service-check.pdf/1p #14565271 inDoc=no student=NOT-LINKED teacher=LINKED \|\| wk4-help-desk-role-play-script.pdf/2p #14565269 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED-MULTI |
| 25 | 1SW-Wk4-Day5 | CCE \| 1SW Wk4 Day 5 \| Help Desk Demos + H&L IT Support Favorites | exit-ticket-only (Career and College Explorations - Concept Map; 1486 chars body) | wk4-day5-xello-skill-connection.pdf [worksheet/1p] #14519389 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | wk4-day5-xello-skill-connection.pdf/1p #14519389 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 26 | 1SW-Wk5-Day1 | CCE \| 1SW Wk5 Day 1 \| Cybersecurity Pathway + CyberSeek Career Map | exit-ticket-only (Career and College Explorations - Ranked Justification; 1365 chars body) | wk5-cyberseek-pathway.pdf [worksheet/2p] #14565274 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | wk5-cyberseek-pathway.pdf/2p #14565274 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 27 | 1SW-Wk5-Day2 | CCE \| 1SW Wk5 Day 2 \| Cybersecurity in Action - Cyber Safety Creator (Day 1) | exit-ticket-only (Career and College Explorations - Mini-Case; 1119 chars body) | wk5-red-flag-checklist.pdf [worksheet/2p] #14565275 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | wk5-red-flag-checklist.pdf/2p #14565275 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 28 | 1SW-Wk5-Day3 | CCE \| 1SW Wk5 Day 3 \| Cyber Safety Peer Feedback + Integrity in the Workplace | exit-ticket-only (Career and College Explorations - Trade-off; 1287 chars body) | wk5-bootcamp-planning-template.pdf [worksheet/2p] #14565276 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | wk5-bootcamp-planning-template.pdf/2p #14565276 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 29 | 1SW-Wk5-Day4 | CCE \| 1SW Wk5 Day 4 \| Glowforge College - Career Logo Design | exit-ticket-only (Career and College Explorations - Decision Tree; 1245 chars body) | wk5-cyberseek-pathway.pdf [worksheet/2p] #14565274 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | wk5-cyberseek-pathway.pdf/2p #14565274 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 30 | 1SW-Wk5-Day5 | CCE \| 1SW Wk5 Day 5 \ **WRONG-DAY CONTENT (= 1SW Wk0 Day 2 ticket)** | Capstone Goal, Transitions, and Reflection | exit-ticket-only (H&L Setup and Discover Your Core; 1840 chars body) | wk5-reflection-update-template.pdf [worksheet/2p] #14565280 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | wk5-reflection-update-template.pdf/2p #14565280 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 31 | 2SW-Wk1-Day1 | CCE \| 2SW Wk1 Day 1 \| Law Cluster Tour + Legal Services Pathway | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1177 chars body) | career-research-worksheet.pdf [worksheet/1p] #14565289 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk1-legal-career-cards.pdf/2p #14565290 inDoc=no student=LINKED teacher=LINKED \|\| career-research-worksheet.pdf/1p #14517430,14565289,14580290,14580292 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 32 | 2SW-Wk1-Day2 | CCE \| 2SW Wk1 Day 2 \| Emergency Essentials Kit Design | exit-ticket-only (Career and College Explorations - Ranked Justification; 1049 chars body) | (none) | 2sw-wk1-emergency-kit-plan.pdf/2p #14565291 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 33 | 2SW-Wk1-Day3 | CCE \| 2SW Wk1 Day 3 \| iCivics - Justice in Action | exit-ticket-only (Career and College Explorations - Decision Tree; 1277 chars body) | 2sw-wk1-city-council-plan.pdf [worksheet/3p] #14565292 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk1-city-council-plan.pdf/3p #14565292 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 34 | 2SW-Wk1-Day4 | CCE \| 2SW Wk1 Day 4 \| AI Ethics Debate + Legal Entrepreneurship | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1124 chars body) | 2sw-wk1-legal-entrepreneur-card.pdf [worksheet/2p] #14565294 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 \|\| 2sw-wk1-policy-argument-and-evidence.pdf [worksheet/2p] #14565293 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk1-legal-entrepreneur-card.pdf/2p #14565294 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 2sw-wk1-policy-argument-and-evidence.pdf/2p #14565293 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED-MULTI |
| 35 | 2SW-Wk1-Day5 | CCE \| 2SW Wk1 Day 5 \| Cluster Wrap-Up + Xello Life Experience | exit-ticket-only (Career and College Explorations - Concept Map; 1584 chars body) | 2sw-wk1-xello-life-experience-connection.pdf [worksheet/1p] #14565296 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk1-xello-life-experience-connection.pdf/1p #14565296 inDoc=yes student=NOT-LINKED teacher=LINKED | pending | - |
| 36 | 2SW-Wk2-Day1 | CCE \| 2SW Wk2 Day 1 \| First Responder Pathways | exit-ticket-only (Career and College Explorations - Mini-Case; 1106 chars body) | 2sw-wk2-first-responder-route-guide.pdf [worksheet/4p] #14606186 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk2-first-responder-route-guide.pdf/4p #14606186 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 37 | 2SW-Wk2-Day2 | CCE \| 2SW Wk2 Day 2 \| Missing Painting - Detective Scenario | exit-ticket-only (Career and College Explorations - Diagnostic MCQ; 1340 chars body) | 2sw-wk2-clinton-lake-evidence-tracker.pdf [worksheet/2p] #14580298 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk2-clinton-lake-evidence-tracker.pdf/2p #14580298 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 38 | 2SW-Wk2-Day3 | CCE \| 2SW Wk2 Day 3 \| Local Risk Response - Task Force Setup | exit-ticket-only (Career and College Explorations - Decision Tree; 1223 chars body) | 2sw-wk2-trail-simulation-record.pdf [worksheet/2p] #14580299 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk2-trail-simulation-record.pdf/2p #14580299 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 39 | 2SW-Wk2-Day4 | CCE \| 2SW Wk2 Day 4 \| Local Risk Response - Citywide Emergency Plan | exit-ticket-only (Career and College Explorations - Trade-off; 1357 chars body) | 2sw-wk2-patient-care-report.pdf [worksheet/2p] #14565301 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk2-patient-care-report.pdf/2p #14565301 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 40 | 2SW-Wk2-Day5 | CCE \| 2SW Wk2 Day 5 \| Cluster Wrap-Up + Reflection | exit-ticket-only (Career and College Explorations - Concept Map; 1172 chars body) | 2sw-wk2-integrity-career-reflection.pdf [worksheet/1p] #14580301 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk2-integrity-career-reflection.pdf/1p #14580301 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 41 | 2SW-Wk3-Day1 | CCE \| 2SW Wk3 Day 1 \| Health Science Cluster + CNA - LVN | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1167 chars body) | (none) | 2sw-wk3-nursing-route-comparison.pdf/4p #14565338 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 2sw-wk3-nursing-route-guide.pdf/2p #14565337 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED |
| 42 | 2SW-Wk3-Day2 | CCE \| 2SW Wk3 Day 2 \| Climbing the Nursing Ladder | exit-ticket-only (Career and College Explorations - Ranked Justification; 1274 chars body) | (none) | 2sw-wk3-nursing-route-comparison.pdf/4p #14565338 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 2sw-wk3-nursing-route-guide.pdf/2p #14565337 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 43 | 2SW-Wk3-Day3 | CCE \| 2SW Wk3 Day 3 \| Vital Signs Monitor - Build Phase | exit-ticket-only (Career and College Explorations - Decision Tree; 1374 chars body) | 2sw-wk3-vital-signs-simulator-build.pdf [worksheet/2p] #14580359 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk3-vital-signs-simulator-build.pdf/2p #14580359 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 44 | 2SW-Wk3-Day4 | CCE \| 2SW Wk3 Day 4 \| Vital Signs Monitor - Test + Present | exit-ticket-only (Career and College Explorations - Mini-Case; 1405 chars body) | 2sw-wk3-clinical-handoff-record.pdf [worksheet/2p] #14565340 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk3-clinical-handoff-record.pdf/2p #14565340,14580361 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 2sw-wk3-handoff-rubric.pdf/2p #14580360 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED |
| 45 | 2SW-Wk3-Day5 | CCE \| 2SW Wk3 Day 5 \| Reflection + Xello Learning Styles + eDynamic | exit-ticket-only (Career and College Explorations - Concept Map; 1500 chars body) | 2sw-wk3-xello-save-careers-reflection.pdf [worksheet/1p] #14662872 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk3-xello-save-careers-reflection.pdf/1p #14662872 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 46 | 2SW-Wk4-Day1 | CCE \| 2SW Wk4 Day 1 \| Dental Pathway Intro + Hat Research | exit-ticket-only (Career and College Explorations - Mini-Case; 1380 chars body) | 2sw-wk4-smile-squad-observation-record.pdf [worksheet/2p] #14565344 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk4-dental-health-data-guide.pdf/2p #14565342 inDoc=no student=LINKED teacher=LINKED \|\| 2sw-wk4-smile-squad-observation-record.pdf/2p #14565344 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 47 | 2SW-Wk4-Day2 | CCE \| 2SW Wk4 Day 2 \| Perfect Toothbrush + Dental Career Pathway | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1296 chars body) | 2sw-wk4-toothbrush-design-brief.pdf [worksheet/2p] #14565345 -> student:NOT-LINKED; teacher:LINKED docMatch=0.20 | 2sw-wk4-toothbrush-design-brief.pdf/2p #14565345 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 48 | 2SW-Wk4-Day3 | CCE \| 2SW Wk4 Day 3 \| Xello Education Experience + School Subjects at Work | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1284 chars body) | 2sw-wk4-xello-experiences-checkpoint.pdf [worksheet/1p] #14662881 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk4-xello-experiences-checkpoint.pdf/1p #14662881 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 49 | 2SW-Wk4-Day4 | CCE \| 2SW Wk4 Day 4 \| Health Informatics + Medical Coding Simulation | exit-ticket-only (Career and College Explorations - Diagnostic MCQ; 1278 chars body) | 2sw-wk4-icd10-training-lab.pdf [worksheet/2p] #14565347 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk4-dental-health-data-guide.pdf/2p #14565342 inDoc=no student=LINKED teacher=LINKED \|\| 2sw-wk4-icd10-training-lab.pdf/2p #14565347 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 50 | 2SW-Wk4-Day5 | CCE \| 2SW Wk4 Day 5 \| Health Science Mid-Point + Recommendation | exit-ticket-only (Career and College Explorations - 3-2-1 Reflective; 1298 chars body) | 2sw-wk4-career-evidence-comparison.pdf [worksheet/2p] #14565343 -> student:NOT-LINKED; teacher:no docMatch=0.25 | 2sw-wk4-career-evidence-comparison.pdf/2p #14565343,14580364 inDoc=no student=NOT-LINKED teacher=no \|\| 2sw-wk4-dental-health-data-guide.pdf/2p #14565342 inDoc=no student=LINKED teacher=LINKED \|\| 2sw-wk4-evidence-check-rubric.pdf/2p #14580362 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED |
| 51 | 2SW-Wk5-Day1 | CCE \| 2SW Wk5 Day 1 \| Powerskills Intro + Conflict Resolution | exit-ticket-only (Career and College Explorations - Decision Tree; 1289 chars body) | 2sw-wk5-conflict-resolution-plan.pdf [worksheet/2p] #14580365 -> student:NOT-LINKED; teacher:LINKED docMatch=0.17 | 2sw-wk5-conflict-resolution-plan.pdf/2p #14580365 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 2sw-wk5-powerskills-transfer-guide.pdf/2p #14561406 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED |
| 52 | 2SW-Wk5-Day2 | CCE \| 2SW Wk5 Day 2 \| Giving and Receiving Feedback | exit-ticket-only (Career and College Explorations - Feedback Sandwich; 1139 chars body) | 2sw-wk5-active-listening-lab.pdf [worksheet/2p] #14580366 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk5-active-listening-lab.pdf/2p #14580366 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 53 | 2SW-Wk5-Day3 | CCE \| 2SW Wk5 Day 3 \| Advocacy + SMART Goals | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1106 chars body) | 2sw-wk5-advocacy-smart-time-plan.pdf [worksheet/2p] #14611251 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk5-advocacy-smart-time-plan.pdf/2p #14611251 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 2sw-wk5-communication-goal-rubric.pdf/2p #14662898 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED |
| 54 | 2SW-Wk5-Day4 | CCE \| 2SW Wk5 Day 4 \| Written Communication - Little Library Post | exit-ticket-only (Career and College Explorations - Trade-off; 1288 chars body) | 2sw-wk5-written-message-lab.pdf [worksheet/1p] #14580368 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk5-written-message-lab.pdf/1p #14580368 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 55 | 2SW-Wk5-Day5 | CCE \| 2SW Wk5 Day 5 \| Xello Time Management + Reflection | exit-ticket-only (Career and College Explorations - Concept Map; 1411 chars body) | 2sw-wk5-work-experience-skills-synthesis.pdf [worksheet/2p] #14662897 -> student:NOT-LINKED; teacher:LINKED docMatch=0.17 | 2sw-wk5-communication-goal-rubric.pdf/2p #14662898 inDoc=no student=LINKED teacher=LINKED \|\| 2sw-wk5-work-experience-skills-synthesis.pdf/2p #14580371,14662897 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 56 | 2SW-Wk6-Day1 | CCE \| 2SW Wk6 Day 1 \| Biomedical Pathway + Cover Letter | exit-ticket-only (Career and College Explorations - Mini-Case; 1392 chars body) | 2sw-wk6-cover-letter-lab.pdf [worksheet/2p] #14561443 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk6-biomedical-career-evidence-guide.pdf/2p #14561442 inDoc=no student=LINKED teacher=LINKED \|\| 2sw-wk6-cover-letter-lab.pdf/2p #14561443 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 57 | 2SW-Wk6-Day2 | CCE \| 2SW Wk6 Day 2 \| Physical Therapy in Action | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1257 chars body) | 2sw-wk6-mini-medics-design-record.pdf [worksheet/2p] #14580372 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk6-mini-medics-design-record.pdf/2p #14580372 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 58 | 2SW-Wk6-Day3 | CCE \| 2SW Wk6 Day 3 \| Farm Fresh Express - Setup | exit-ticket-only (Career and College Explorations - Ranked Justification; 1314 chars body) | 2sw-wk6-outbreak-investigation-record.pdf [worksheet/2p] #14561445 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk6-outbreak-investigation-record.pdf/2p #14561445 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 59 | 2SW-Wk6-Day4 | CCE \| 2SW Wk6 Day 4 \| Farm Fresh Express - Design + Present | exit-ticket-only (Career and College Explorations - Venn Diagram; 1096 chars body) | 2sw-wk6-outbreak-response-plan.pdf [worksheet/2p] #14561446 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk6-outbreak-response-plan.pdf/2p #14561446 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 60 | 2SW-Wk6-Day5 | CCE \| 2SW Wk6 Day 5 \| Emerging Career Research + 2SW Wrap-Up | exit-ticket-only (Career and College Explorations - Concept Map; 1481 chars body) | 2sw-wk6-xello-career-matches-reflection.pdf [worksheet/1p] #14662910 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 2sw-wk6-biomedical-career-evidence-guide.pdf/2p #14561442 inDoc=no student=LINKED teacher=LINKED \|\| 2sw-wk6-xello-career-matches-reflection.pdf/1p #14662910 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 61 | 3SW-Wk1-Day1 | CCE \| 3SW Wk1 Day 1 \| Ag Cluster Tour + Animal Systems Hats | exit-ticket-only (Career and College Explorations - Mini-Case; 1263 chars body) | (none) | 3sw-wk1-veterinary-career-evidence-guide.pdf/2p #14580373 inDoc=no student=LINKED teacher=LINKED | pending | - |
| 62 | 3SW-Wk1-Day2 | CCE \| 3SW Wk1 Day 2 \| Vet Tech vs. Veterinarian - Career Deep-Dive | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1093 chars body) | 3sw-wk1-veterinary-career-comparison.pdf [worksheet/2p] #14580374 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk1-veterinary-career-comparison.pdf/2p #14580374 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 63 | 3SW-Wk1-Day3 | CCE \| 3SW Wk1 Day 3 \| Candy Conundrum - Food Science Teamwork | exit-ticket-only (Career and College Explorations - Decision Tree; 1341 chars body) | 3sw-wk1-veterinary-triage-record.pdf [worksheet/2p] #14565357 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk1-veterinary-triage-record.pdf/2p #14565357 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 64 | 3SW-Wk1-Day4 | CCE \| 3SW Wk1 Day 4 \| Xello Life Experiences + Volunteer Hours | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1160 chars body) | 3sw-wk1-xello-skills-reflection.pdf [worksheet/1p] #14662922 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk1-veterinary-career-evidence-guide.pdf/2p #14580373 inDoc=no student=LINKED teacher=LINKED \|\| 3sw-wk1-xello-skills-reflection.pdf/1p #14662922 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 65 | 3SW-Wk1-Day5 | CCE \| 3SW Wk1 Day 5 \| Nimitz Vet Pathway + H&L Favorites | exit-ticket-only (Career and College Explorations - Concept Map; 1295 chars body) | 3sw-wk1-veterinary-pathway-brief.pdf [worksheet/2p] #14662923 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk1-veterinary-evidence-rubric.pdf/2p #14565360 inDoc=no student=LINKED teacher=LINKED \|\| 3sw-wk1-veterinary-pathway-brief.pdf/2p #14662923 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 66 | 3SW-Wk2-Day1 | CCE \| 3SW Wk2 Day 1 \| Plant Science + Environmental Pathway Hats | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1054 chars body) | (none) | 3sw-wk2-plant-career-evidence-guide.pdf/2p #14565362 inDoc=no student=LINKED teacher=LINKED | pending | - |
| 67 | 3SW-Wk2-Day2 | CCE \| 3SW Wk2 Day 2 \| Farm to Table - Brainstorm + Sketch | exit-ticket-only (Career and College Explorations - Mini-Case; 1139 chars body) | 3sw-wk2-farm-to-table-planner.pdf [worksheet/2p] #14565363 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk2-farm-to-table-planner.pdf/2p #14565363 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 3sw-wk2-plant-science-major-rubric.pdf/2p #14565364 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED |
| 68 | 3SW-Wk2-Day3 | CCE \| 3SW Wk2 Day 3 \| Farm to Table - Build in Canva | exit-ticket-only (Career and College Explorations - Venn Diagram; 1251 chars body) | 3sw-wk2-farm-to-table-planner.pdf [worksheet/2p] #14565363 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk2-farm-to-table-planner.pdf/2p #14565363 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 3sw-wk2-plant-science-major-rubric.pdf/2p #14565364 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED |
| 69 | 3SW-Wk2-Day4 | CCE \| 3SW Wk2 Day 4 \| Emerging Ag Career Research | exit-ticket-only (Career and College Explorations - Ranked Justification; 1111 chars body) | 3sw-wk2-emerging-plant-tech-evaluation.pdf [worksheet/2p] #14565366 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk2-emerging-plant-tech-evaluation.pdf/2p #14565366 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 3sw-wk2-emerging-plant-tech-evidence.pdf/2p #14565365 inDoc=no student=LINKED teacher=LINKED \|\| 3sw-wk2-plant-science-major-rubric.pdf/2p #14565364 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 70 | 3SW-Wk2-Day5 | CCE \| 3SW Wk2 Day 5 \| Xello Work Experiences + Nimitz Plant Science Pathway | exit-ticket-only (Career and College Explorations - Concept Map; 1404 chars body) | 3sw-wk2-xello-biases-reflection.pdf [worksheet/1p] #14662934 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk2-emerging-plant-tech-evidence.pdf/2p #14565365 inDoc=no student=LINKED teacher=LINKED \|\| 3sw-wk2-xello-biases-reflection.pdf/1p #14662934 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 71 | 3SW-Wk3-Day1 | CCE \| 3SW Wk3 Day 1 \| Environmental Careers + Climate Connection | exit-ticket-only (Career and College Explorations - Mini-Case; 1327 chars body) | (none) | 3sw-wk3-sustainable-career-problem-guide.pdf/2p #14561503 inDoc=no student=LINKED teacher=LINKED | pending | - |
| 72 | 3SW-Wk3-Day2 | CCE \| 3SW Wk3 Day 2 \| Pest Patrol - Read the Field Notes | exit-ticket-only (Career and College Explorations - Ranked Justification; 1053 chars body) | 3sw-wk3-pest-patrol-field-notes.pdf [worksheet/2p] #14565368 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk3-pest-patrol-field-notes.pdf/2p #14565368 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 73 | 3SW-Wk3-Day3 | CCE \| 3SW Wk3 Day 3 \| Pest Patrol - Drone Sketch + Labels | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1121 chars body) | 3sw-wk3-drone-design-brief.pdf [worksheet/2p] #14565369 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk3-drone-design-brief.pdf/2p #14565369 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 3sw-wk3-sustainable-engineering-major-rubric.pdf/2p #14565371 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED |
| 74 | 3SW-Wk3-Day4 | CCE \| 3SW Wk3 Day 4 \| Pest Patrol - Peer Feedback + Societal Trends | exit-ticket-only (Career and College Explorations - Comparison Matrix; 912 chars body) | 3sw-wk3-peer-review-revision.pdf [worksheet/1p] #14565370 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 \|\| 3sw-wk3-societal-trends-evaluation.pdf [worksheet/2p] #14591629 -> student:NOT-LINKED; teacher:LINKED docMatch=0.20 | 3sw-wk3-peer-review-revision.pdf/1p #14565370 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 3sw-wk3-societal-trends-evaluation.pdf/2p #14591629 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 3sw-wk3-societal-trends-evidence.pdf/2p #14561507 inDoc=no student=LINKED teacher=LINKED \|\| 3sw-wk3-sustainable-engineering-major-rubric.pdf/2p #14565371 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED-MULTI |
| 75 | 3SW-Wk3-Day5 | CCE \| 3SW Wk3 Day 5 \| Xello Interests + eDynamic Unit 7.1 | exit-ticket-only (Career and College Explorations - Concept Map; 1339 chars body) | 3sw-wk3-xello-goals-plan.pdf [worksheet/1p] #14662948 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk3-xello-goals-plan.pdf/1p #14662948 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 76 | 3SW-Wk4-Day1 | CCE \| 3SW Wk4 Day 1 \| Hospitality Cluster + Culinary Twist | exit-ticket-only (Career and College Explorations - Mini-Case; 1221 chars body) | 3sw-wk4-culinary-twist-menu-brief.pdf [worksheet/3p] #14591631 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk4-culinary-twist-menu-brief.pdf/3p #14561545,14591631 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 77 | 3SW-Wk4-Day2 | CCE \| 3SW Wk4 Day 2 \| Powerskill Motivation + Salary Comparison | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1223 chars body) | 3sw-wk4-motivation-career-comparison.pdf [worksheet/2p] #14591632 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk4-hospitality-career-evidence-guide.pdf/2p #14565373 inDoc=no student=LINKED teacher=LINKED \|\| 3sw-wk4-motivation-career-comparison.pdf/2p #14591632 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 78 | 3SW-Wk4-Day3 | CCE \| 3SW Wk4 Day 3 \| Hotel Rescue - Team Problem Solving | exit-ticket-only (Career and College Explorations - Decision Tree; 1478 chars body) | 3sw-wk4-hotel-rescue-response.pdf [worksheet/2p] #14565376 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk4-hotel-rescue-cards.pdf/3p #14561560 inDoc=no student=LINKED teacher=LINKED \|\| 3sw-wk4-hotel-rescue-response.pdf/2p #14565376 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 79 | 3SW-Wk4-Day4 | CCE \| 3SW Wk4 Day 4 \| Pack Your Bags - Tourism Campaign Career Lab | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1146 chars body) | 3sw-wk4-cater-create-event-brief.pdf [worksheet/1p] #14591633 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk4-cater-create-event-brief.pdf/1p #14591633 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 80 | 3SW-Wk4-Day5 | CCE \| 3SW Wk4 Day 5 \| Xello Decision Making + eDynamic 6.1 + H&L Favorites | exit-ticket-only (Career and College Explorations - Concept Map; 1317 chars body) | 3sw-wk4-hospitality-recommendation.pdf [worksheet/2p] #14591634 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk4-hospitality-career-evidence-guide.pdf/2p #14565373 inDoc=no student=LINKED teacher=LINKED \|\| 3sw-wk4-hospitality-minor-rubric.pdf/2p #14591635 inDoc=no student=LINKED teacher=LINKED \|\| 3sw-wk4-hospitality-recommendation.pdf/2p #14591634 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 81 | 3SW-Wk5-Day1 | CCE \| 3SW Wk5 Day 1 \| Human Services Cluster + Stress Toolkit | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1151 chars body) | 3sw-wk5-sfx-concept-lab-brief.pdf [worksheet/3p] #14565386 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk5-sfx-concept-lab-brief.pdf/3p #14565386 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 82 | 3SW-Wk5-Day2 | CCE \| 3SW Wk5 Day 2 \| Job Interviews - Prep + Practice | exit-ticket-only (Career and College Explorations - Mini-Case; 1152 chars body) | 3sw-wk5-sfx-build-test-record.pdf [worksheet/1p] #14565387 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk5-sfx-build-test-record.pdf/1p #14565387 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 83 | 3SW-Wk5-Day3 | CCE \| 3SW Wk5 Day 3 \| Texas TDLR Cosmetology Licensing Deep-Dive | exit-ticket-only (Career and College Explorations - Ranked Justification; 1139 chars body) | 3sw-wk5-cosmetology-pathway-decision.pdf [worksheet/2p] #14591641 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 \|\| 3sw-wk5-sfx-quality-revision.pdf [worksheet/2p] #14591640 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk5-cosmetology-pathway-decision.pdf/2p #14591641 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 3sw-wk5-sfx-quality-revision.pdf/2p #14591640 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 3sw-wk5-texas-cosmetology-evidence-guide.pdf/2p #14565389 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED-MULTI |
| 84 | 3SW-Wk5-Day4 | CCE \| 3SW Wk5 Day 4 \| Salon Entrepreneurship + Get Out and Move! | exit-ticket-only (Career and College Explorations - Decision Tree; 1246 chars body) | 3sw-wk5-salon-wellness-campaign.pdf [worksheet/2p] #14565391 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk5-salon-wellness-campaign.pdf/2p #14565391 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 85 | 3SW-Wk5-Day5 | CCE \| 3SW Wk5 Day 5 \| Xello Career Factors + eDynamic 4.2 + H&L Favorites | exit-ticket-only (Career and College Explorations - Concept Map; 1328 chars body) | 3sw-wk5-cosmetology-recommendation.pdf [worksheet/2p] #14565392 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk5-cosmetology-minor-rubric.pdf/1p #14565393 inDoc=no student=LINKED teacher=LINKED \|\| 3sw-wk5-cosmetology-recommendation.pdf/2p #14565392 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 3sw-wk5-texas-cosmetology-evidence-guide.pdf/2p #14565389 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED |
| 86 | 3SW-Wk6-Day1 | CCE \| 3SW Wk6 Day 1 \| Business Cluster Tour + Defining Entrepreneurship | exit-ticket-only (Career and College Explorations - Mini-Case; 1293 chars body) | 3sw-wk6-entrepreneurship-opportunity-guide.pdf [worksheet/2p] #14561631 -> student:NOT-LINKED; teacher:LINKED docMatch=0.17 | 3sw-wk6-entrepreneurship-opportunity-guide.pdf/2p #14561631 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 87 | 3SW-Wk6-Day2 | CCE \| 3SW Wk6 Day 2 \| Think Inside the Box - MVP Design | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1081 chars body) | 3sw-wk6-million-dollar-idea-support-packet.pdf [worksheet/4p] #14591642 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk6-million-dollar-idea-support-packet.pdf/4p #14591642 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 88 | 3SW-Wk6-Day3 | CCE \| 3SW Wk6 Day 3 \| Pitching Investors - Build the Business Plan | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1142 chars body) | 3sw-wk6-million-dollar-idea-support-packet.pdf [worksheet/4p] #14591642 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 3sw-wk6-million-dollar-idea-support-packet.pdf/4p #14591642 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 89 | 3SW-Wk6-Day4 | CCE \| 3SW Wk6 Day 4 \| Pitching Investors - Pitch Day | exit-ticket-only (Career and College Explorations - Trade-off; 1122 chars body) | 3sw-wk6-venture-brief-and-pitch-record.pdf [worksheet/4p] #14561633 -> student:NOT-LINKED; teacher:LINKED docMatch=0.09 | 3sw-wk6-entrepreneurship-portfolio-rubric.pdf/1p #14561636 inDoc=no student=LINKED teacher=LINKED \|\| 3sw-wk6-venture-brief-and-pitch-record.pdf/4p #14561633 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 90 | 3SW-Wk6-Day5 | CCE \| 3SW Wk6 Day 5 \| Lifestyle Snapshot Personal Budget + Xello Save Careers | exit-ticket-only (Career and College Explorations - Concept Map; 1332 chars body) | 3sw-wk6-budget-and-scholarship-plan.pdf [worksheet/3p] #14663175 -> student:NOT-LINKED; teacher:LINKED docMatch=0.17 | 3sw-wk6-budget-and-scholarship-plan.pdf/3p #14663175 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 3sw-wk6-dallas-county-living-cost-guide.pdf/2p #14561634 inDoc=no student=LINKED teacher=LINKED \|\| 3sw-wk6-entrepreneurship-portfolio-rubric.pdf/1p #14561636 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 91 | 4SW-Wk1-Day1 | CCE \| 4SW Wk1 Day 1 \| H&L Core personality Revisit + Favorites Audit | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1209 chars body) | 4sw-wk1-midyear-profile-audit.pdf [worksheet/2p] #14565910 -> student:NOT-LINKED; teacher:LINKED docMatch=0.17 | 4sw-wk1-midyear-profile-audit.pdf/2p #14565910 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 92 | 4SW-Wk1-Day2 | CCE \| 4SW Wk1 Day 2 \| H&L Career Plan + Iceberg Cartoon | exit-ticket-only (Career and College Explorations - Concept Map; 1219 chars body) | 4sw-wk1-career-iceberg-and-goal.pdf [worksheet/4p] #14565911 -> student:NOT-LINKED; teacher:LINKED docMatch=0.12 | 4sw-wk1-career-iceberg-and-goal.pdf/4p #14561667,14565911 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 93 | 4SW-Wk1-Day3 | CCE \| 4SW Wk1 Day 3 \| Xello Quick Sims - The Real Game | exit-ticket-only (Career and College Explorations - Trade-off; 1207 chars body) | 4sw-wk1-career-deep-dive.pdf [worksheet/2p] #14662863 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk1-career-deep-dive.pdf/2p #14662863 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 94 | 4SW-Wk1-Day4 | CCE \| 4SW Wk1 Day 4 \| eDynamic 8.1 - Choosing a Career Path | exit-ticket-only (Career and College Explorations - Ranked Justification; 1335 chars body) | 4sw-wk1-pathway-and-ctso-decision.pdf [worksheet/4p] #14591646 -> student:NOT-LINKED; teacher:LINKED docMatch=0.14 | 4sw-wk1-pathway-and-ctso-decision.pdf/4p #14591646 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 95 | 4SW-Wk1-Day5 | CCE \| 4SW Wk1 Day 5 \| Mid-Year Reflection + Pathway Gallery Walk | exit-ticket-only (Career and College Explorations - 3-2-1 Reflective; 1006 chars body) | 4sw-wk1-midyear-career-blueprint.pdf [worksheet/3p] #14662864 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk1-midyear-blueprint-rubric.pdf/2p #14662865 inDoc=no student=LINKED teacher=LINKED \|\| 4sw-wk1-midyear-career-blueprint.pdf/3p #14662864 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 96 | 4SW-Wk2-Day1 | CCE \| 4SW Wk2 Day 1 \| MS-to-HS Transition + Texas Endorsements | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1314 chars body) | 4sw-wk2-transition-and-assessment-decisions.pdf [worksheet/3p] #14591648 -> student:NOT-LINKED; teacher:LINKED docMatch=0.14 | 4sw-wk2-transition-and-assessment-decisions.pdf/3p #14591648 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 97 | 4SW-Wk2-Day2 | CCE \| 4SW Wk2 Day 2 \| H&L District Course Planner - 4-Year Mapping | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1235 chars body) | 4sw-wk2-four-year-course-plan-draft.pdf [worksheet/3p] #14662869 -> student:NOT-LINKED; teacher:LINKED docMatch=0.17 | 4sw-wk2-four-year-course-plan-draft.pdf/3p #14562515,14662869 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 98 | 4SW-Wk2-Day3 | CCE \| 4SW Wk2 Day 3 \| Family Engagement - Sharing the Plan | exit-ticket-only (Career and College Explorations - Decision Tree; 1201 chars body) | 4sw-wk2-college-credit-and-family-conversation.pdf [worksheet/2p] #14611265 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk2-college-credit-and-family-conversation.pdf/2p #14611265 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 99 | 4SW-Wk2-Day4 | CCE \| 4SW Wk2 Day 4 \| eDynamic 6.2 - Gaining Experience | exit-ticket-only (Career and College Explorations - Ranked Justification; 1109 chars body) | 4sw-wk2-smart-experience-action-plan.pdf [worksheet/1p] #14565921 -> student:NOT-LINKED; teacher:LINKED docMatch=0.25 | 4sw-wk2-smart-experience-action-plan.pdf/1p #14565921 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 100 | 4SW-Wk2-Day5 | CCE \| 4SW Wk2 Day 5 \| Career Plan Write-Up | exit-ticket-only (Career and College Explorations - Concept Map; 1210 chars body) | 4sw-wk2-individual-high-school-career-plan.pdf [worksheet/4p] #14611266 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk2-high-school-career-plan-rubric.pdf/2p #14611267 inDoc=no student=LINKED teacher=LINKED \|\| 4sw-wk2-individual-high-school-career-plan.pdf/4p #14611266 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 101 | 4SW-Wk3-Day1 | CCE \| 4SW Wk3 Day 1 \| Transportation Cluster + "Transportation Troubles" | exit-ticket-only (Career and College Explorations - Mini-Case; 1247 chars body) | 4sw-wk3-transportation-survey-design.pdf [worksheet/3p] #14591653 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk3-transportation-survey-design.pdf/3p #14591653 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 102 | 4SW-Wk3-Day2 | CCE \| 4SW Wk3 Day 2 \| Aviation Hat Research + Military vs. Civilian Pathways | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1163 chars body) | 4sw-wk3-aviation-route-action-plan.pdf [worksheet/4p] #14591657 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk3-aviation-careers-and-pilot-routes.pdf/2p #14591654 inDoc=no student=LINKED teacher=LINKED \|\| 4sw-wk3-aviation-route-action-plan.pdf/4p #14591657 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 103 | 4SW-Wk3-Day3 | CCE \| 4SW Wk3 Day 3 \| LEGO ATC - Build the Airport | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1058 chars body) | 4sw-wk3-airport-design-simulation-lab.pdf [worksheet/4p] #14591655 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk3-airport-design-simulation-lab.pdf/4p #14562528,14591655 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 104 | 4SW-Wk3-Day4 | CCE \| 4SW Wk3 Day 4 \| LEGO ATC - Run the Simulation + Powerskill Creativity | exit-ticket-only (Career and College Explorations - Decision Tree; 1216 chars body) | 4sw-wk3-airport-design-simulation-lab.pdf [worksheet/4p] #14591655 -> student:NOT-LINKED; teacher:LINKED docMatch=0.14 | 4sw-wk3-airport-design-simulation-lab.pdf/4p #14562528,14591655 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 4sw-wk3-classroom-scenario-cards.pdf/1p #14591656 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED |
| 105 | 4SW-Wk3-Day5 | CCE \| 4SW Wk3 Day 5 \| ATC Presentations + Aviation Goal Plan | exit-ticket-only (Career and College Explorations - Concept Map; 1378 chars body) | 4sw-wk3-aviation-route-action-plan.pdf [worksheet/4p] #14591657 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk3-aviation-route-action-plan.pdf/4p #14591657 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 4sw-wk3-route-action-rubric.pdf/2p #14565931 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED |
| 106 | 4SW-Wk4-Day1 | CCE \| 4SW Wk4 Day 1 \| H&L Engineering Cluster + "Protecting Wildlife" | exit-ticket-only (Career and College Explorations - Mini-Case; 1272 chars body) | 4sw-wk4-wildlife-tracking-drone-design.pdf [worksheet/3p] #14565933 -> student:NOT-LINKED; teacher:LINKED docMatch=0.20 | 4sw-wk4-wildlife-tracking-drone-design.pdf/3p #14562537,14565933 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 107 | 4SW-Wk4-Day2 | CCE \| 4SW Wk4 Day 2 \| UAS Industry Jigsaw Research | exit-ticket-only (Career and College Explorations - Ranked Justification; 1236 chars body) | (none) | 4sw-wk4-drone-enabled-occupations.pdf/2p #14565934 inDoc=no student=LINKED teacher=LINKED | pending | - |
| 108 | 4SW-Wk4-Day3 | CCE \| 4SW Wk4 Day 3 \| FAA Part 107 + Drone Flight Basics | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1126 chars body) | 4sw-wk4-drone-operation-decision-readiness.pdf [worksheet/3p] #14565935 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk4-drone-operation-decision-readiness.pdf/3p #14565935 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 109 | 4SW-Wk4-Day4 | CCE \| 4SW Wk4 Day 4 \| Drone Navigation Challenge | exit-ticket-only (Career and College Explorations - Trade-off; 1152 chars body) | 4sw-wk4-drone-systems-test.pdf [worksheet/3p] #14591659 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk4-drone-systems-test.pdf/3p #14562538,14591659 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 110 | 4SW-Wk4-Day5 | CCE \| 4SW Wk4 Day 5 \| Jigsaw Presentations + Career Classification | exit-ticket-only (Career and College Explorations - Concept Map; 1348 chars body) | 4sw-wk4-drone-systems-evidence-brief.pdf [worksheet/4p] #14565937 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk4-drone-systems-evidence-brief.pdf/4p #14565937 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 4sw-wk4-drone-systems-evidence-rubric.pdf/2p #14565938 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED |
| 111 | 4SW-Wk5-Day1 | CCE \| 4SW Wk5 Day 1 \| H&L "Delivery Connection App" + Automotive Pathway Browse | exit-ticket-only (Career and College Explorations - Venn Diagram; 1015 chars body) | 4sw-wk5-crash-crew-evidence-and-preliminary-plan.pdf [worksheet/3p] #14591661 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk5-crash-crew-evidence-and-preliminary-plan.pdf/3p #14562546,14591661 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 112 | 4SW-Wk5-Day2 | CCE \| 4SW Wk5 Day 2 \| ASE Certification + Apprenticeship vs. College | exit-ticket-only (Career and College Explorations - Trade-off; 1271 chars body) | 4sw-wk5-ase-and-automotive-training-routes.pdf [worksheet/3p] #14591662 -> student:NOT-LINKED; teacher:LINKED docMatch=0.14 | 4sw-wk5-ase-and-automotive-training-routes.pdf/3p #14591662 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 113 | 4SW-Wk5-Day3 | CCE \| 4SW Wk5 Day 3 \| Automotive Salary Showdown | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1256 chars body) | 4sw-wk5-three-automotive-occupations.pdf [worksheet/3p] #14591663 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk5-three-automotive-occupations.pdf/3p #14562547,14591663 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 114 | 4SW-Wk5-Day4 | CCE \| 4SW Wk5 Day 4 \| Ratteree Automotive Pathway Deep-Dive | exit-ticket-only (Career and College Explorations - Diagnostic MCQ; 1318 chars body) | 4sw-wk5-automotive-route-decision.pdf [worksheet/2p] #14591664 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk5-automotive-route-decision.pdf/2p #14591664 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 115 | 4SW-Wk5-Day5 | CCE \| 4SW Wk5 Day 5 \| Cross-Cluster Salary Presentation + H&L Favorites | exit-ticket-only (Career and College Explorations - Concept Map; 1259 chars body) | 4sw-wk5-automotive-evidence-brief.pdf [worksheet/4p] #14591665 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk5-automotive-evidence-brief.pdf/4p #14591665 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 4sw-wk5-automotive-evidence-rubric.pdf/2p #14591666 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED |
| 116 | 4SW-Wk6-Day1 | CCE \| 4SW Wk6 Day 1 \| H&L Powerskills "Work Ethic" + STEM Program Activity | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1176 chars body) | 4sw-wk6-truck-evidence-and-priority.pdf [worksheet/3p] #14565956 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk6-truck-evidence-and-priority.pdf/3p #14562557,14565956 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 117 | 4SW-Wk6-Day2 | CCE \| 4SW Wk6 Day 2 \| Transferable Skills Matrix | exit-ticket-only (Career and College Explorations - Ranked Justification; 1045 chars body) | 4sw-wk6-transferable-skills-evidence.pdf [worksheet/4p] #14565957 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk6-transferable-skills-evidence.pdf/4p #14562558,14565957 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 118 | 4SW-Wk6-Day3 | CCE \| 4SW Wk6 Day 3 \| Professional Associations Jigsaw | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1342 chars body) | 4sw-wk6-career-organization-types.pdf [worksheet/3p] #14565958 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk6-career-organization-types.pdf/3p #14565958 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 119 | 4SW-Wk6-Day4 | CCE \| 4SW Wk6 Day 4 \| Work Ethic in Action + H&L Career Plan Update | exit-ticket-only (Career and College Explorations - Mini-Case; 1341 chars body) | 4sw-wk6-integrity-and-evidence-audit.pdf [worksheet/3p] #14565959 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk6-integrity-and-evidence-audit.pdf/3p #14565959 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 120 | 4SW-Wk6-Day5 | CCE \| 4SW Wk6 Day 5 \| Mid-Year Growth Reflection + Sharing Circle | exit-ticket-only (Career and College Explorations - Concept Map; 1253 chars body) | 4sw-wk6-mid-year-evidence-reflection.pdf [worksheet/4p] #14591669 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 4sw-wk6-mid-year-evidence-reflection.pdf/4p #14591669 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 4sw-wk6-mid-year-evidence-rubric.pdf/2p #14565961 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED |
| 121 | 5SW-Wk1-Day1 | CCE \| 5SW Wk1 Day 1 \| A&C Cluster Tour + Safety Supervisor | exit-ticket-only (Career and College Explorations - Mini-Case; 1275 chars body) | 5sw-wk1-safety-supervisor-evidence-plan.pdf [worksheet/3p] #14565966 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk1-safety-supervisor-evidence-plan.pdf/3p #14562574,14565966 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 122 | 5SW-Wk1-Day2 | CCE \| 5SW Wk1 Day 2 \| Career Research + Salary Comparison | exit-ticket-only (Career and College Explorations - Ranked Justification; 979 chars body) | 5sw-wk1-three-career-evidence-comparison.pdf [worksheet/4p] #14565967 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk1-three-career-evidence-comparison.pdf/4p #14562573,14565967 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 123 | 5SW-Wk1-Day3 | CCE \| 5SW Wk1 Day 3 \| TinkerCAD Introduction - Learning 3D Design | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1126 chars body) | 5sw-wk1-concept-building-design.pdf [worksheet/4p] #14565968 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk1-concept-building-design.pdf/4p #14562575,14565968 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 124 | 5SW-Wk1-Day4 | CCE \| 5SW Wk1 Day 4 \| TinkerCAD Iteration + Trash to Treasure | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1136 chars body) | 5sw-wk1-design-test-and-revision.pdf [worksheet/3p] #14565969 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk1-design-test-and-revision.pdf/3p #14562576,14565969 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 125 | 5SW-Wk1-Day5 | CCE \| 5SW Wk1 Day 5 \| Presentations + A&C Favorites | exit-ticket-only (Career and College Explorations - Concept Map; 1410 chars body) | 5sw-wk1-unexpected-architecture-evidence.pdf [worksheet/2p] #14565970 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk1-architecture-portfolio-rubric.pdf/1p #14591672 inDoc=no student=LINKED teacher=LINKED \|\| 5sw-wk1-unexpected-architecture-evidence.pdf/2p #14565970 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 126 | 5SW-Wk2-Day1 | CCE \| 5SW Wk2 Day 1 \| Civil Engineering Cluster Tour + Infrastructure Imagination Kickoff | exit-ticket-only (Career and College Explorations - Mini-Case; 1353 chars body) | 5sw-wk2-civil-engineer-and-systems-evidence.pdf [worksheet/2p] #14568713 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk2-civil-engineer-and-systems-evidence.pdf/2p #14562590,14568713 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 127 | 5SW-Wk2-Day2 | CCE \| 5SW Wk2 Day 2 \| PSAT - SAT - ACT - Why They Matter + Emerging Engineering Careers | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1060 chars body) | 5sw-wk2-assessment-and-emerging-specialty.pdf [worksheet/3p] #14568714 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk2-assessment-and-emerging-specialty.pdf/3p #14562589,14568714 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 128 | 5SW-Wk2-Day3 | CCE \| 5SW Wk2 Day 3 \| Bridge Challenge - Design Phase | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1092 chars body) | 5sw-wk2-bridge-design-options.pdf [worksheet/4p] #14591677 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk2-bridge-design-options.pdf/4p #14562591,14591677 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 129 | 5SW-Wk2-Day4 | CCE \| 5SW Wk2 Day 4 \| Bridge Challenge - Build and Test | exit-ticket-only (Career and College Explorations - Ranked Justification; 1235 chars body) | 5sw-wk2-bridge-test-and-redesign.pdf [worksheet/4p] #14591678 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk2-bridge-test-and-redesign.pdf/4p #14562592,14591678 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 130 | 5SW-Wk2-Day5 | CCE \| 5SW Wk2 Day 5 \| Results + Engineering Favorites + Career Plan Update | exit-ticket-only (Career and College Explorations - Concept Map; 1356 chars body) | 5sw-wk2-engineering-synthesis.pdf [worksheet/3p] #14568718 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk2-engineering-evidence-rubric.pdf/1p #14568720 inDoc=no student=LINKED teacher=LINKED \|\| 5sw-wk2-engineering-synthesis.pdf/3p #14568718 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 131 | 5SW-Wk3-Day1 | CCE \| 5SW Wk3 Day 1 \| H&L Construction Pathway + Hat Research | exit-ticket-only (Career and College Explorations - Mini-Case; 1393 chars body) | 5sw-wk3-construction-career-evidence.pdf [worksheet/3p] #14570242 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk3-construction-career-evidence.pdf/3p #14562606,14570242 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 132 | 5SW-Wk3-Day2 | CCE \| 5SW Wk3 Day 2 \| Apprenticeships + Trade Unions | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1155 chars body) | 5sw-wk3-routes-and-organizations.pdf [worksheet/4p] #14570243 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk3-routes-and-organizations.pdf/4p #14562607,14570243 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 133 | 5SW-Wk3-Day3 | CCE \| 5SW Wk3 Day 3 \| Construction Career Classification | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1185 chars body) | 5sw-wk3-labor-classification.pdf [worksheet/4p] #14591683 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk3-labor-classification.pdf/4p #14562608,14591683 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 134 | 5SW-Wk3-Day4 | CCE \| 5SW Wk3 Day 4 \| NCCER + MacArthur Pathways + H&L Power Pitch | exit-ticket-only (Career and College Explorations - Ranked Justification; 1123 chars body) | 5sw-wk3-fictional-evidence-report.pdf [worksheet/5p] #14591684 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk3-fictional-evidence-report.pdf/5p #14591684,14591689 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 135 | 5SW-Wk3-Day5 | CCE \| 5SW Wk3 Day 5 \| Jigsaw Presentations + Power Pitch Practice + H&L Favorites | exit-ticket-only (Career and College Explorations - Concept Map; 1359 chars body) | 5sw-wk3-fictional-evidence-report.pdf [worksheet/5p] #14591684 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk3-construction-evidence-rubric.pdf/2p #14591685 inDoc=no student=LINKED teacher=LINKED \|\| 5sw-wk3-fictional-evidence-report.pdf/5p #14591684,14591689 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 136 | 5SW-Wk4-Day1 | CCE \| 5SW Wk4 Day 1 \| H&L Skilled Trades Exploration - HVAC, Electrical, Plumbing | exit-ticket-only (Career and College Explorations - Ranked Justification; 982 chars body) | 5sw-wk4-skilled-trades-career-evidence.pdf [worksheet/3p] #14570309 -> student:NOT-LINKED; teacher:LINKED docMatch=0.17 | 5sw-wk4-skilled-trades-career-evidence.pdf/3p #14562624,14570309 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 137 | 5SW-Wk4-Day2 | CCE \| 5SW Wk4 Day 2 \| Welding Careers + Jigsaw Research | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1067 chars body) | 5sw-wk4-hvac-evidence-first-field-notes.pdf [worksheet/6p] #14570310 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk4-hvac-evidence-first-field-notes.pdf/6p #14562625,14570310 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 138 | 5SW-Wk4-Day3 | CCE \| 5SW Wk4 Day 3 \| DFW Labor Market Analysis | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1057 chars body) | 5sw-wk4-skilled-trades-classification.pdf [worksheet/4p] #14570311 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk4-skilled-trades-classification.pdf/4p #14562626,14570311 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 139 | 5SW-Wk4-Day4 | CCE \| 5SW Wk4 Day 4 \| Post-HS Apprenticeship Pathways + Matrix Completion | exit-ticket-only (Career and College Explorations - Mini-Case; 1518 chars body) | 5sw-wk4-current-entry-routes.pdf [worksheet/4p] #14570312 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk4-current-entry-routes.pdf/4p #14562627,14570312 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 140 | 5SW-Wk4-Day5 | CCE \| 5SW Wk4 Day 5 \| Jigsaw Presentations + A&C Cluster Wrap-Up | exit-ticket-only (Career and College Explorations - Concept Map; 1254 chars body) | 5sw-wk4-fictional-water-line-response.pdf [worksheet/2p] #14591690 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 \|\| 5sw-wk4-skilled-trades-classification.pdf [worksheet/4p] #14570311 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk4-fictional-water-line-response.pdf/2p #14570319,14591690 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 5sw-wk4-skilled-trades-classification.pdf/4p #14562626,14570311 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 5sw-wk4-skilled-trades-evidence-rubric.pdf/2p #14591691 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED-MULTI |
| 141 | 5SW-Wk5-Day1 | CCE \| 5SW Wk5 Day 1 \| H&L Lifestyle Snapshot - Reflecting on Future Life | exit-ticket-only (Career and College Explorations - Short Constructed Response; 969 chars body) | 5sw-wk5-salary-source-and-lifestyle-target.pdf [worksheet/3p] #14662889 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk5-salary-source-and-lifestyle-target.pdf/3p #14562636,14662889 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 142 | 5SW-Wk5-Day2 | CCE \| 5SW Wk5 Day 2 \| Building My Personal Budget | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1202 chars body) | 5sw-wk5-dallas-county-personal-budget.pdf [worksheet/4p] #14570334 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk5-dallas-county-personal-budget.pdf/4p #14562637,14570334 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 143 | 5SW-Wk5-Day3 | CCE \| 5SW Wk5 Day 3 \| Cost of Living Comparison | exit-ticket-only (Career and College Explorations - Ranked Justification; 944 chars body) | 5sw-wk5-location-cost-comparison.pdf [worksheet/2p] #14596041 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk5-location-cost-comparison.pdf/2p #14562638,14596041 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 144 | 5SW-Wk5-Day4 | CCE \| 5SW Wk5 Day 4 \| NGPF - EverFi Financial Literacy + Paying for College | exit-ticket-only (Career and College Explorations - Mini-Case; 1376 chars body) | 5sw-wk5-paying-for-education-and-training.pdf [worksheet/3p] #14570336 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk5-paying-for-education-and-training.pdf/3p #14570336 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 145 | 5SW-Wk5-Day5 | CCE \| 5SW Wk5 Day 5 \| Budget Comparison + 3-Career Salary Analysis + A&C Wrap-Up | exit-ticket-only (Career and College Explorations - Concept Map; 1155 chars body) | 5sw-wk5-three-career-budget-portfolio.pdf [worksheet/4p] #14662892 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk5-budget-portfolio-rubric.pdf/2p #14570338 inDoc=no student=LINKED teacher=LINKED \|\| 5sw-wk5-three-career-budget-portfolio.pdf/4p #14570342,14662892 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 146 | 5SW-Wk6-Day1 | CCE \| 5SW Wk6 Day 1 \| Real Estate Career Exploration - H&L + Gallery Walk | exit-ticket-only (Career and College Explorations - Mini-Case; 1295 chars body) | 5sw-wk6-real-estate-career-boundaries.pdf [worksheet/2p] #14572251 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk6-real-estate-career-boundaries.pdf/2p #14562675,14572251 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 147 | 5SW-Wk6-Day2 | CCE \| 5SW Wk6 Day 2 \| TREC Licensing + Commission Math | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1257 chars body) | 5sw-wk6-trec-and-variable-income.pdf [worksheet/3p] #14572260 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk6-trec-and-variable-income.pdf/3p #14562676,14572260 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 148 | 5SW-Wk6-Day3 | CCE \| 5SW Wk6 Day 3 \| Entrepreneurship in Real Estate + DFW Market Analysis | exit-ticket-only (Career and College Explorations - Ranked Justification; 1119 chars body) | 5sw-wk6-flip-this-house-evidence-plan.pdf [worksheet/1p] #14572269 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk6-flip-this-house-evidence-plan.pdf/1p #14562677,14572269 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 149 | 5SW-Wk6-Day4 | CCE \| 5SW Wk6 Day 4 \| Market Trends Analysis + H&L Career Plan Update | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1155 chars body) | 5sw-wk6-real-estate-labor-evidence.pdf [worksheet/2p] #14572282 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk6-real-estate-labor-evidence.pdf/2p #14572282 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 150 | 5SW-Wk6-Day5 | CCE \| 5SW Wk6 Day 5 \| Real Estate Pitch + 5th Six Weeks Reflection | exit-ticket-only (Career and College Explorations - Concept Map; 1223 chars body) | 5sw-wk6-six-weeks-evidence-brief.pdf [worksheet/2p] #14596047 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 5sw-wk6-evidence-brief-rubric.pdf/1p #14596048 inDoc=no student=LINKED teacher=LINKED \|\| 5sw-wk6-six-weeks-evidence-brief.pdf/2p #14596047,14596052 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 151 | 6SW-Wk1-Day1 | CCE \| 6SW Wk1 Day 1 \| Education Cluster Tour + Community Classroom | exit-ticket-only (Career and College Explorations - Mini-Case; 1346 chars body) | 6sw-wk1-community-classroom-plan.pdf [worksheet/2p] #14596064 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk1-community-classroom-plan.pdf/2p #14562692,14596064 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 152 | 6SW-Wk1-Day2 | CCE \| 6SW Wk1 Day 2 \| Cert Pathways + Powerskills Leadership | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1170 chars body) | 6sw-wk1-texas-education-routes.pdf [worksheet/3p] #14596065 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk1-texas-education-routes.pdf/3p #14562693,14596065 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 153 | 6SW-Wk1-Day3 | CCE \| 6SW Wk1 Day 3 \| Job Search Scavenger Hunt + Xello Learning Pathways | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1332 chars body) | 6sw-wk1-education-job-evidence.pdf [worksheet/2p] #14662900 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk1-education-job-evidence.pdf/2p #14662900 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 154 | 6SW-Wk1-Day4 | CCE \| 6SW Wk1 Day 4 \| Teaching Toolbox + Community Service Reflection | exit-ticket-only (Career and College Explorations - Ranked Justification; 1199 chars body) | 6sw-wk1-teach-through-play-service.pdf [worksheet/2p] #14596066 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk1-teach-through-play-service.pdf/2p #14562694,14596066 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 155 | 6SW-Wk1-Day5 | CCE \| 6SW Wk1 Day 5 \| Irving ISD Pathways + eDynamic 7.2 + Education Favorites | exit-ticket-only (Career and College Explorations - Concept Map; 1409 chars body) | 6sw-wk1-education-evidence-portfolio.pdf [worksheet/3p] #14662901 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk1-education-evidence-portfolio.pdf/3p #14562695,14662901 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 6sw-wk1-education-portfolio-rubric.pdf/1p #14662902 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED |
| 156 | 6SW-Wk2-Day1 | CCE \| 6SW Wk2 Day 1 \| Arts - AV Cluster + Digital Storytelling | exit-ticket-only (Career and College Explorations - Mini-Case; 1429 chars body) | 6sw-wk2-podcast-production-plan.pdf [worksheet/2p] #14575253 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk2-podcast-production-plan.pdf/2p #14562710,14575253 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 157 | 6SW-Wk2-Day2 | CCE \| 6SW Wk2 Day 2 \| First Resume in Xello | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1301 chars body) | 6sw-wk2-first-resume-draft.pdf [worksheet/3p] #14611292 -> student:NOT-LINKED; teacher:LINKED docMatch=0.08 | 6sw-wk2-first-resume-draft.pdf/3p #14562711,14611292 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 158 | 6SW-Wk2-Day3 | CCE \| 6SW Wk2 Day 3 \| Attention to Detail + Resume Revision | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1004 chars body) | 6sw-wk2-audio-cue-and-resume-revision.pdf [worksheet/1p] #14662920 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk2-audio-cue-and-resume-revision.pdf/1p #14662920 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 159 | 6SW-Wk2-Day4 | CCE \| 6SW Wk2 Day 4 \| Game On! + Job Search Steps | exit-ticket-only (Career and College Explorations - Ranked Justification; 914 chars body) | 6sw-wk2-effective-job-search.pdf [worksheet/3p] #14575279 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk2-effective-job-search.pdf/3p #14562712,14575279 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 160 | 6SW-Wk2-Day5 | CCE \| 6SW Wk2 Day 5 \| Creative Entrepreneurs Branding Project | exit-ticket-only (Career and College Explorations - Concept Map; 1428 chars body) | 6sw-wk2-audio-cue-and-resume-revision.pdf [worksheet/1p] #14662920 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 \|\| 6sw-wk2-effective-job-search.pdf [worksheet/3p] #14575279 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 \|\| 6sw-wk2-first-resume-draft.pdf [worksheet/3p] #14611292 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 \|\| 6sw-wk2-merch-mode-design.pdf [worksheet/2p] #14575296 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk2-audio-cue-and-resume-revision.pdf/1p #14662920 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 6sw-wk2-effective-job-search.pdf/3p #14562712,14575279 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 6sw-wk2-first-resume-draft.pdf/3p #14562711,14611292 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 6sw-wk2-merch-mode-design.pdf/2p #14575296 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 6sw-wk2-resume-design-rubric.pdf/2p #14662921 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED-MULTI |
| 161 | 6SW-Wk3-Day1 | CCE \| 6SW Wk3 Day 1 \| Marketing Cluster + Marketing on the Move | exit-ticket-only (Career and College Explorations - Mini-Case; 1120 chars body) | 6sw-wk3-click-factor-campaign.pdf [worksheet/2p] #14596075 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk3-click-factor-campaign.pdf/2p #14562730,14596075 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 162 | 6SW-Wk3-Day2 | CCE \| 6SW Wk3 Day 2 \| Written Communication + Economic Conditions | exit-ticket-only (Career and College Explorations - Comparison Matrix; 1024 chars body) | 6sw-wk3-written-communication-and-change.pdf [worksheet/2p] #14578332 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk3-written-communication-and-change.pdf/2p #14578332,14596077 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 163 | 6SW-Wk3-Day3 | CCE \| 6SW Wk3 Day 3 \| Think Inside the Box - Subscription Box MVP | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1077 chars body) | 6sw-wk3-expert-edge-plan.pdf [worksheet/2p] #14578333 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk3-expert-edge-plan.pdf/2p #14562731,14578333 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 164 | 6SW-Wk3-Day4 | CCE \| 6SW Wk3 Day 4 \| Hat Research + Google Applied Digital Skills | exit-ticket-only (Career and College Explorations - Ranked Justification; 1082 chars body) | 6sw-wk3-family-fun-pass-analysis.pdf [worksheet/2p] #14578335 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk3-family-fun-pass-analysis.pdf/2p #14562732,14578335 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 165 | 6SW-Wk3-Day5 | CCE \| 6SW Wk3 Day 5 \| Marketing Plan Pitches + eDynamic 4.1 + H&L Favorites | exit-ticket-only (Career and College Explorations - Concept Map; 1320 chars body) | 6sw-wk3-marketing-evidence-brief.pdf [worksheet/4p] #14578336 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk3-marketing-evidence-brief.pdf/4p #14562733,14578336 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 6sw-wk3-marketing-evidence-rubric.pdf/2p #14578337 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED |
| 166 | 6SW-Wk4-Day1 | CCE \| 6SW Wk4 Day 1 \| Sales Pathway + Pitching Investors Setup | exit-ticket-only (Career and College Explorations - Mini-Case; 1331 chars body) | 6sw-wk4-sales-pitch-plan.pdf [worksheet/2p] #14579336 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk4-sales-pitch-plan.pdf/2p #14562749,14579336 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 167 | 6SW-Wk4-Day2 | CCE \| 6SW Wk4 Day 2 \| Slide Deck + Giving and Receiving Feedback | exit-ticket-only (Career and College Explorations - Multi-Question Diagnostic MCQ; 1364 chars body) | 6sw-wk4-pitch-delivery-record.pdf [worksheet/2p] #14579337 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk4-pitch-delivery-record.pdf/2p #14562750,14579337 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 168 | 6SW-Wk4-Day3 | CCE \| 6SW Wk4 Day 3 \| Investor Pitches + Career Presentation Outline | exit-ticket-only (Career and College Explorations - Short Constructed Response; 914 chars body) | 6sw-wk4-brainboost-and-career-outline.pdf [worksheet/2p] #14579338 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk4-brainboost-and-career-outline.pdf/2p #14562751,14579338 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 169 | 6SW-Wk4-Day4 | CCE \| 6SW Wk4 Day 4 \| Interview Appearance + Practice Presentations | exit-ticket-only (Career and College Explorations - Routed Decision Tree; 1148 chars body) | 6sw-wk4-appearance-and-rehearsal.pdf [worksheet/2p] #14596080 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk4-appearance-and-rehearsal.pdf/2p #14596080,14596086 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 170 | 6SW-Wk4-Day5 | CCE \| 6SW Wk4 Day 5 \| Career Presentations Day | exit-ticket-only (Career and College Explorations - 3-2-1 Reflective; 1262 chars body) | 6sw-wk4-career-oral-evidence.pdf [worksheet/2p] #14596081 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk4-career-oral-evidence.pdf/2p #14596081,14596087 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 6sw-wk4-career-oral-rubric.pdf/2p #14596082 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED |
| 171 | 6SW-Wk5-Day1 | CCE \| 6SW Wk5 Day 1 \| Job Search Steps + Admin Pathway | exit-ticket-only (Career and College Explorations - Seven-Bubble Ordered Concept Map; 1223 chars body) | 6sw-wk5-job-search-and-posting-evidence.pdf [worksheet/2p] #14579492 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk5-job-search-and-posting-evidence.pdf/2p #14562758,14579492 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 172 | 6SW-Wk5-Day2 | CCE \| 6SW Wk5 Day 2 \| Cover Letter Writing | exit-ticket-only (Career and College Explorations - Comparison Matrix; 947 chars body) | 6sw-wk5-cover-letter-simulation.pdf [worksheet/3p] #14579493 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk5-cover-letter-simulation.pdf/3p #14562759,14579493 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 6sw-wk5-job-skills-rubric.pdf/2p #14611301 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 173 | 6SW-Wk5-Day3 | CCE \| 6SW Wk5 Day 3 \| Job Application + References Protocol | exit-ticket-only (Career and College Explorations - Procedural Decision Tree; 1407 chars body) | 6sw-wk5-application-and-references.pdf [worksheet/4p] #14579494 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk5-application-and-references.pdf/4p #14562760,14579494 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 174 | 6SW-Wk5-Day4 | CCE \| 6SW Wk5 Day 4 \| Mock Interview Prep + Fishbowl Demo | exit-ticket-only (Career and College Explorations - Short Constructed Response; 956 chars body) | 6sw-wk5-interview-readiness.pdf [worksheet/3p] #14611299 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk5-interview-readiness.pdf/3p #14579523,14611299 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 175 | 6SW-Wk5-Day5 | CCE \| 6SW Wk5 Day 5 \| Mock Interview Day + Thank-You Letter | exit-ticket-only (Career and College Explorations - 3-2-1 Reflective; 1038 chars body) | 6sw-wk5-mock-interview-and-thank-you.pdf [worksheet/4p] #14611300 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk5-job-skills-rubric.pdf/2p #14611301 inDoc=no student=LINKED teacher=LINKED \|\| 6sw-wk5-mock-interview-and-thank-you.pdf/4p #14562761,14611300 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 176 | 6SW-Wk6-Day1 | CCE \| 6SW Wk6 Day 1 \| Iceberg Reflection + Finalize H&L Career Plan | exit-ticket-only (Career and College Explorations - Venn Diagram; 906 chars body) | 6sw-wk6-career-evidence-inventory.pdf [worksheet/2p] #14579639 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk6-career-evidence-inventory.pdf/2p #14562776,14579639 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 177 | 6SW-Wk6-Day2 | CCE \| 6SW Wk6 Day 2 \| Written Career Plan + Presentation Outline | exit-ticket-only (Career and College Explorations - Short Constructed Response; 1102 chars body) | 6sw-wk6-individual-career-plan.pdf [worksheet/4p] #14579640 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk6-individual-career-plan.pdf/4p #14562777,14579640 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 178 | 6SW-Wk6-Day3 | CCE \| 6SW Wk6 Day 3 \| Capstone Presentations Day 1 | exit-ticket-only (Career and College Explorations - Ranked Justification; 1219 chars body) | 6sw-wk6-capstone-presentation-plan.pdf [worksheet/2p] #14579641 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk6-capstone-presentation-plan.pdf/2p #14562778,14579641 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |
| 179 | 6SW-Wk6-Day4 | CCE \| 6SW Wk6 Day 4 \| Capstone Presentations Day 2 + Plan Download + Being a Career Thinker | exit-ticket-only (Career and College Explorations - Concept Map; 1224 chars body) | 6sw-wk6-capstone-delivery-record.pdf [worksheet/2p] #14579642 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk6-capstone-delivery-record.pdf/2p #14562780,14579642 inDoc=no student=NOT-LINKED teacher=LINKED \|\| 6sw-wk6-capstone-rubric.pdf/2p #14579644 inDoc=no student=LINKED teacher=LINKED | pending | COLLAPSED |
| 180 | 6SW-Wk6-Day5 | CCE \| 6SW Wk6 Day 5 \| End-of-Year Reflection + Celebration | exit-ticket-only (Career and College Explorations - 3-2-1 Reflective; 1091 chars body) | 6sw-wk6-final-course-reflection.pdf [worksheet/2p] #14579643 -> student:NOT-LINKED; teacher:LINKED docMatch=0.00 | 6sw-wk6-final-course-reflection.pdf/2p #14562779,14579643 inDoc=no student=NOT-LINKED teacher=LINKED | pending | COLLAPSED |

CSV of the same table: `.tmp/audit-20260914/response-route-collapse.csv`.

## 2. COLLAPSED days — what the student can no longer open

### 2a. Multi-anchor collapses (15 days)

| day_key | distinct PDFs pointed at the one Doc | student can no longer open |
|---|---|---|
| 1SW-Wk1-Day1 | 1sw-wk1-day1-manufacturing-cluster-tour-more-than-assembly-lines.pdf, manufacturing-pathways-scaffold.pdf | 1sw-wk1-day1-manufacturing-cluster-tour-more-than-assembly-lines.pdf, manufacturing-pathways-scaffold.pdf (1p) |
| 1SW-Wk2-Day1 | 1sw-wk2-day1-it-cluster-tour-four-irving-programs-of-study.pdf, wk2-it-programs-scaffold.pdf | 1sw-wk2-day1-it-cluster-tour-four-irving-programs-of-study.pdf, wk2-it-programs-scaffold.pdf (1p) |
| 1SW-Wk2-Day2 | 1sw-wk2-day2-programming-pathway-deep-dive-software-web-app-game.pdf, wk2-it-salary-comparison.pdf | 1sw-wk2-day2-programming-pathway-deep-dive-software-web-app-game.pdf, wk2-it-salary-comparison.pdf (5p) |
| 1SW-Wk2-Day3 | 1sw-wk2-day3-powerskill-resilience-it-salary-showdown.pdf, wk2-flip-the-failure-scaffold.pdf, wk2-it-salary-comparison.pdf | 1sw-wk2-day3-powerskill-resilience-it-salary-showdown.pdf, wk2-flip-the-failure-scaffold.pdf (1p) |
| 1SW-Wk3-Day1 | 1sw-wk3-day1-networking-systems-pathway-transferable-skills.pdf, wk3-transferable-skills-list.pdf | 1sw-wk3-day1-networking-systems-pathway-transferable-skills.pdf, wk3-transferable-skills-list.pdf (1p) |
| 1SW-Wk3-Day2 | 1sw-wk3-day2-website-revamp-audit-a-real-site.pdf, wk3-ux-audit-scaffold.pdf | 1sw-wk3-day2-website-revamp-audit-a-real-site.pdf, wk3-ux-audit-scaffold.pdf (1p) |
| 1SW-Wk3-Day4 | wk3-day4-career-comparison.pdf, wk3-emerging-tech-research-template.pdf | wk3-day4-career-comparison.pdf (1p), wk3-emerging-tech-research-template.pdf (2p) |
| 1SW-Wk4-Day2 | wk4-day2-route-decision.pdf, wk4-education-pathway-comparison.pdf | wk4-day2-route-decision.pdf (1p) |
| 1SW-Wk4-Day3 | 1sw-wk4-day3-help-desk-simulator-makecode-day-1.pdf, wk4-help-desk-program-evidence.pdf, wk4-troubleshooting-step-sort-cards.pdf | 1sw-wk4-day3-help-desk-simulator-makecode-day-1.pdf, wk4-help-desk-program-evidence.pdf (2p), wk4-troubleshooting-step-sort-cards.pdf (1p) |
| 1SW-Wk4-Day4 | wk4-day4-customer-service-check.pdf, wk4-help-desk-role-play-script.pdf | wk4-day4-customer-service-check.pdf (1p), wk4-help-desk-role-play-script.pdf (2p) |
| 2SW-Wk1-Day4 | 2sw-wk1-legal-entrepreneur-card.pdf, 2sw-wk1-policy-argument-and-evidence.pdf | 2sw-wk1-legal-entrepreneur-card.pdf (2p), 2sw-wk1-policy-argument-and-evidence.pdf (2p) |
| 3SW-Wk3-Day4 | 3sw-wk3-peer-review-revision.pdf, 3sw-wk3-societal-trends-evaluation.pdf | 3sw-wk3-peer-review-revision.pdf (1p), 3sw-wk3-societal-trends-evaluation.pdf (2p), 3sw-wk3-sustainable-engineering-major-rubric.pdf (2p) |
| 3SW-Wk5-Day3 | 3sw-wk5-cosmetology-pathway-decision.pdf, 3sw-wk5-sfx-quality-revision.pdf | 3sw-wk5-cosmetology-pathway-decision.pdf (2p), 3sw-wk5-sfx-quality-revision.pdf (2p) |
| 5SW-Wk4-Day5 | 5sw-wk4-fictional-water-line-response.pdf, 5sw-wk4-skilled-trades-classification.pdf | 5sw-wk4-fictional-water-line-response.pdf (2p), 5sw-wk4-skilled-trades-classification.pdf (4p) |
| 6SW-Wk2-Day5 | 6sw-wk2-audio-cue-and-resume-revision.pdf, 6sw-wk2-effective-job-search.pdf, 6sw-wk2-first-resume-draft.pdf, 6sw-wk2-merch-mode-design.pdf | 6sw-wk2-audio-cue-and-resume-revision.pdf (1p), 6sw-wk2-effective-job-search.pdf (3p), 6sw-wk2-first-resume-draft.pdf (3p), 6sw-wk2-merch-mode-design.pdf (2p) |

### 2b. All collapsed days, one line each (170 days)

- **1SW-Wk0-Day1** — student can no longer open: cce-first-week-goal-setting.pdf [still on a teacher page].
- **1SW-Wk0-Day4** — student can no longer open: my-career-journey.pdf (2p) [still on a teacher page].
- **1SW-Wk1-Day1** — student can no longer open: 1sw-wk1-day1-manufacturing-cluster-tour-more-than-assembly-lines.pdf [still on a teacher page], manufacturing-pathways-scaffold.pdf (1p) [still on a teacher page].
- **1SW-Wk1-Day2** — student can no longer open: career-research-worksheet.pdf (1p) [still on a teacher page], technician-checklist-scaffold.pdf (1p) [still on a teacher page].
- **1SW-Wk1-Day4** — student can no longer open: 1sw-wk1-robots-for-crayons-action-plan.pdf (2p) [still on a teacher page].
- **1SW-Wk2-Day1** — student can no longer open: 1sw-wk2-day1-it-cluster-tour-four-irving-programs-of-study.pdf [still on a teacher page], wk2-it-programs-scaffold.pdf (1p) [still on a teacher page].
- **1SW-Wk2-Day2** — student can no longer open: 1sw-wk2-day2-programming-pathway-deep-dive-software-web-app-game.pdf [still on a teacher page], wk2-it-salary-comparison.pdf (5p) [still on a teacher page].
- **1SW-Wk2-Day3** — student can no longer open: 1sw-wk2-day3-powerskill-resilience-it-salary-showdown.pdf [on NO page at all], wk2-flip-the-failure-scaffold.pdf (1p) [on NO page at all].
- **1SW-Wk2-Day4** — student can no longer open: 1sw-wk2-day4-code-org-hour-of-code-day-1.pdf [still on a teacher page].
- **1SW-Wk2-Day5** — student can no longer open: wk2-day5-it-pathway-decision.pdf (1p) [still on a teacher page].
- **1SW-Wk3-Day1** — student can no longer open: 1sw-wk3-day1-networking-systems-pathway-transferable-skills.pdf [still on a teacher page], wk3-transferable-skills-list.pdf (1p) [still on a teacher page].
- **1SW-Wk3-Day2** — student can no longer open: 1sw-wk3-day2-website-revamp-audit-a-real-site.pdf [still on a teacher page], wk3-ux-audit-scaffold.pdf (1p) [still on a teacher page].
- **1SW-Wk3-Day3** — student can no longer open: wk3-wireframe-template.pdf (1p) [still on a teacher page].
- **1SW-Wk3-Day4** — student can no longer open: wk3-day4-career-comparison.pdf (1p) [still on a teacher page], wk3-emerging-tech-research-template.pdf (2p) [still on a teacher page].
- **1SW-Wk3-Day5** — student can no longer open: wk3-day5-learning-style-connection.pdf (1p) [still on a teacher page].
- **1SW-Wk4-Day1** — student can no longer open: wk4-day1-career-interest-check.pdf (1p) [still on a teacher page].
- **1SW-Wk4-Day2** — student can no longer open: wk4-day2-route-decision.pdf (1p) [still on a teacher page].
- **1SW-Wk4-Day3** — student can no longer open: 1sw-wk4-day3-help-desk-simulator-makecode-day-1.pdf [still on a teacher page], wk4-help-desk-program-evidence.pdf (2p) [still on a teacher page], wk4-troubleshooting-step-sort-cards.pdf (1p) [still on a teacher page].
- **1SW-Wk4-Day4** — student can no longer open: wk4-day4-customer-service-check.pdf (1p) [still on a teacher page], wk4-help-desk-role-play-script.pdf (2p) [still on a teacher page].
- **1SW-Wk4-Day5** — student can no longer open: wk4-day5-xello-skill-connection.pdf (1p) [still on a teacher page].
- **1SW-Wk5-Day1** — student can no longer open: wk5-cyberseek-pathway.pdf (2p) [still on a teacher page].
- **1SW-Wk5-Day2** — student can no longer open: wk5-red-flag-checklist.pdf (2p) [still on a teacher page].
- **1SW-Wk5-Day3** — student can no longer open: wk5-bootcamp-planning-template.pdf (2p) [still on a teacher page].
- **1SW-Wk5-Day4** — student can no longer open: wk5-cyberseek-pathway.pdf (2p) [still on a teacher page].
- **1SW-Wk5-Day5** — student can no longer open: wk5-reflection-update-template.pdf (2p) [still on a teacher page].
- **2SW-Wk1-Day1** — student can no longer open: career-research-worksheet.pdf (1p) [still on a teacher page].
- **2SW-Wk1-Day2** — student can no longer open: 2sw-wk1-emergency-kit-plan.pdf (2p) [still on a teacher page].
- **2SW-Wk1-Day3** — student can no longer open: 2sw-wk1-city-council-plan.pdf (3p) [still on a teacher page].
- **2SW-Wk1-Day4** — student can no longer open: 2sw-wk1-legal-entrepreneur-card.pdf (2p) [still on a teacher page], 2sw-wk1-policy-argument-and-evidence.pdf (2p) [still on a teacher page].
- **2SW-Wk2-Day1** — student can no longer open: 2sw-wk2-first-responder-route-guide.pdf (4p) [still on a teacher page].
- **2SW-Wk2-Day2** — student can no longer open: 2sw-wk2-clinton-lake-evidence-tracker.pdf (2p) [still on a teacher page].
- **2SW-Wk2-Day3** — student can no longer open: 2sw-wk2-trail-simulation-record.pdf (2p) [still on a teacher page].
- **2SW-Wk2-Day4** — student can no longer open: 2sw-wk2-patient-care-report.pdf (2p) [still on a teacher page].
- **2SW-Wk2-Day5** — student can no longer open: 2sw-wk2-integrity-career-reflection.pdf (1p) [still on a teacher page].
- **2SW-Wk3-Day1** — student can no longer open: 2sw-wk3-nursing-route-comparison.pdf (4p) [still on a teacher page].
- **2SW-Wk3-Day2** — student can no longer open: 2sw-wk3-nursing-route-comparison.pdf (4p) [still on a teacher page], 2sw-wk3-nursing-route-guide.pdf (2p) [still on a teacher page].
- **2SW-Wk3-Day3** — student can no longer open: 2sw-wk3-vital-signs-simulator-build.pdf (2p) [still on a teacher page].
- **2SW-Wk3-Day4** — student can no longer open: 2sw-wk3-clinical-handoff-record.pdf (2p) [still on a teacher page].
- **2SW-Wk3-Day5** — student can no longer open: 2sw-wk3-xello-save-careers-reflection.pdf (1p) [still on a teacher page].
- **2SW-Wk4-Day1** — student can no longer open: 2sw-wk4-smile-squad-observation-record.pdf (2p) [still on a teacher page].
- **2SW-Wk4-Day2** — student can no longer open: 2sw-wk4-toothbrush-design-brief.pdf (2p) [still on a teacher page].
- **2SW-Wk4-Day3** — student can no longer open: 2sw-wk4-xello-experiences-checkpoint.pdf (1p) [still on a teacher page].
- **2SW-Wk4-Day4** — student can no longer open: 2sw-wk4-icd10-training-lab.pdf (2p) [still on a teacher page].
- **2SW-Wk4-Day5** — student can no longer open: 2sw-wk4-career-evidence-comparison.pdf (2p) [on NO page at all].
- **2SW-Wk5-Day1** — student can no longer open: 2sw-wk5-conflict-resolution-plan.pdf (2p) [still on a teacher page].
- **2SW-Wk5-Day2** — student can no longer open: 2sw-wk5-active-listening-lab.pdf (2p) [still on a teacher page].
- **2SW-Wk5-Day3** — student can no longer open: 2sw-wk5-advocacy-smart-time-plan.pdf (2p) [still on a teacher page].
- **2SW-Wk5-Day4** — student can no longer open: 2sw-wk5-written-message-lab.pdf (1p) [still on a teacher page].
- **2SW-Wk5-Day5** — student can no longer open: 2sw-wk5-work-experience-skills-synthesis.pdf (2p) [still on a teacher page].
- **2SW-Wk6-Day1** — student can no longer open: 2sw-wk6-cover-letter-lab.pdf (2p) [still on a teacher page].
- **2SW-Wk6-Day2** — student can no longer open: 2sw-wk6-mini-medics-design-record.pdf (2p) [still on a teacher page].
- **2SW-Wk6-Day3** — student can no longer open: 2sw-wk6-outbreak-investigation-record.pdf (2p) [still on a teacher page].
- **2SW-Wk6-Day4** — student can no longer open: 2sw-wk6-outbreak-response-plan.pdf (2p) [still on a teacher page].
- **2SW-Wk6-Day5** — student can no longer open: 2sw-wk6-xello-career-matches-reflection.pdf (1p) [still on a teacher page].
- **3SW-Wk1-Day2** — student can no longer open: 3sw-wk1-veterinary-career-comparison.pdf (2p) [still on a teacher page].
- **3SW-Wk1-Day3** — student can no longer open: 3sw-wk1-veterinary-triage-record.pdf (2p) [still on a teacher page].
- **3SW-Wk1-Day4** — student can no longer open: 3sw-wk1-xello-skills-reflection.pdf (1p) [still on a teacher page].
- **3SW-Wk1-Day5** — student can no longer open: 3sw-wk1-veterinary-pathway-brief.pdf (2p) [still on a teacher page].
- **3SW-Wk2-Day2** — student can no longer open: 3sw-wk2-farm-to-table-planner.pdf (2p) [still on a teacher page].
- **3SW-Wk2-Day3** — student can no longer open: 3sw-wk2-farm-to-table-planner.pdf (2p) [still on a teacher page].
- **3SW-Wk2-Day4** — student can no longer open: 3sw-wk2-emerging-plant-tech-evaluation.pdf (2p) [still on a teacher page], 3sw-wk2-plant-science-major-rubric.pdf (2p) [still on a teacher page].
- **3SW-Wk2-Day5** — student can no longer open: 3sw-wk2-xello-biases-reflection.pdf (1p) [still on a teacher page].
- **3SW-Wk3-Day2** — student can no longer open: 3sw-wk3-pest-patrol-field-notes.pdf (2p) [still on a teacher page].
- **3SW-Wk3-Day3** — student can no longer open: 3sw-wk3-drone-design-brief.pdf (2p) [still on a teacher page].
- **3SW-Wk3-Day4** — student can no longer open: 3sw-wk3-peer-review-revision.pdf (1p) [still on a teacher page], 3sw-wk3-societal-trends-evaluation.pdf (2p) [still on a teacher page], 3sw-wk3-sustainable-engineering-major-rubric.pdf (2p) [still on a teacher page].
- **3SW-Wk3-Day5** — student can no longer open: 3sw-wk3-xello-goals-plan.pdf (1p) [still on a teacher page].
- **3SW-Wk4-Day1** — student can no longer open: 3sw-wk4-culinary-twist-menu-brief.pdf (3p) [still on a teacher page].
- **3SW-Wk4-Day2** — student can no longer open: 3sw-wk4-motivation-career-comparison.pdf (2p) [still on a teacher page].
- **3SW-Wk4-Day3** — student can no longer open: 3sw-wk4-hotel-rescue-response.pdf (2p) [still on a teacher page].
- **3SW-Wk4-Day4** — student can no longer open: 3sw-wk4-cater-create-event-brief.pdf (1p) [still on a teacher page].
- **3SW-Wk4-Day5** — student can no longer open: 3sw-wk4-hospitality-recommendation.pdf (2p) [still on a teacher page].
- **3SW-Wk5-Day1** — student can no longer open: 3sw-wk5-sfx-concept-lab-brief.pdf (3p) [still on a teacher page].
- **3SW-Wk5-Day2** — student can no longer open: 3sw-wk5-sfx-build-test-record.pdf (1p) [still on a teacher page].
- **3SW-Wk5-Day3** — student can no longer open: 3sw-wk5-cosmetology-pathway-decision.pdf (2p) [still on a teacher page], 3sw-wk5-sfx-quality-revision.pdf (2p) [still on a teacher page].
- **3SW-Wk5-Day4** — student can no longer open: 3sw-wk5-salon-wellness-campaign.pdf (2p) [still on a teacher page].
- **3SW-Wk5-Day5** — student can no longer open: 3sw-wk5-cosmetology-recommendation.pdf (2p) [still on a teacher page].
- **3SW-Wk6-Day1** — student can no longer open: 3sw-wk6-entrepreneurship-opportunity-guide.pdf (2p) [still on a teacher page].
- **3SW-Wk6-Day2** — student can no longer open: 3sw-wk6-million-dollar-idea-support-packet.pdf (4p) [still on a teacher page].
- **3SW-Wk6-Day3** — student can no longer open: 3sw-wk6-million-dollar-idea-support-packet.pdf (4p) [still on a teacher page].
- **3SW-Wk6-Day4** — student can no longer open: 3sw-wk6-venture-brief-and-pitch-record.pdf (4p) [still on a teacher page].
- **3SW-Wk6-Day5** — student can no longer open: 3sw-wk6-budget-and-scholarship-plan.pdf (3p) [still on a teacher page], 3sw-wk6-entrepreneurship-portfolio-rubric.pdf (1p) [still on a teacher page].
- **4SW-Wk1-Day1** — student can no longer open: 4sw-wk1-midyear-profile-audit.pdf (2p) [still on a teacher page].
- **4SW-Wk1-Day2** — student can no longer open: 4sw-wk1-career-iceberg-and-goal.pdf (4p) [still on a teacher page].
- **4SW-Wk1-Day3** — student can no longer open: 4sw-wk1-career-deep-dive.pdf (2p) [still on a teacher page].
- **4SW-Wk1-Day4** — student can no longer open: 4sw-wk1-pathway-and-ctso-decision.pdf (4p) [still on a teacher page].
- **4SW-Wk1-Day5** — student can no longer open: 4sw-wk1-midyear-career-blueprint.pdf (3p) [still on a teacher page].
- **4SW-Wk2-Day1** — student can no longer open: 4sw-wk2-transition-and-assessment-decisions.pdf (3p) [still on a teacher page].
- **4SW-Wk2-Day2** — student can no longer open: 4sw-wk2-four-year-course-plan-draft.pdf (3p) [still on a teacher page].
- **4SW-Wk2-Day3** — student can no longer open: 4sw-wk2-college-credit-and-family-conversation.pdf (2p) [still on a teacher page].
- **4SW-Wk2-Day4** — student can no longer open: 4sw-wk2-smart-experience-action-plan.pdf (1p) [still on a teacher page].
- **4SW-Wk2-Day5** — student can no longer open: 4sw-wk2-individual-high-school-career-plan.pdf (4p) [still on a teacher page].
- **4SW-Wk3-Day1** — student can no longer open: 4sw-wk3-transportation-survey-design.pdf (3p) [still on a teacher page].
- **4SW-Wk3-Day2** — student can no longer open: 4sw-wk3-aviation-route-action-plan.pdf (4p) [still on a teacher page].
- **4SW-Wk3-Day3** — student can no longer open: 4sw-wk3-airport-design-simulation-lab.pdf (4p) [still on a teacher page].
- **4SW-Wk3-Day4** — student can no longer open: 4sw-wk3-airport-design-simulation-lab.pdf (4p) [still on a teacher page].
- **4SW-Wk3-Day5** — student can no longer open: 4sw-wk3-aviation-route-action-plan.pdf (4p) [still on a teacher page].
- **4SW-Wk4-Day1** — student can no longer open: 4sw-wk4-wildlife-tracking-drone-design.pdf (3p) [still on a teacher page].
- **4SW-Wk4-Day3** — student can no longer open: 4sw-wk4-drone-operation-decision-readiness.pdf (3p) [still on a teacher page].
- **4SW-Wk4-Day4** — student can no longer open: 4sw-wk4-drone-systems-test.pdf (3p) [still on a teacher page].
- **4SW-Wk4-Day5** — student can no longer open: 4sw-wk4-drone-systems-evidence-brief.pdf (4p) [still on a teacher page].
- **4SW-Wk5-Day1** — student can no longer open: 4sw-wk5-crash-crew-evidence-and-preliminary-plan.pdf (3p) [still on a teacher page].
- **4SW-Wk5-Day2** — student can no longer open: 4sw-wk5-ase-and-automotive-training-routes.pdf (3p) [still on a teacher page].
- **4SW-Wk5-Day3** — student can no longer open: 4sw-wk5-three-automotive-occupations.pdf (3p) [still on a teacher page].
- **4SW-Wk5-Day4** — student can no longer open: 4sw-wk5-automotive-route-decision.pdf (2p) [still on a teacher page].
- **4SW-Wk5-Day5** — student can no longer open: 4sw-wk5-automotive-evidence-brief.pdf (4p) [still on a teacher page].
- **4SW-Wk6-Day1** — student can no longer open: 4sw-wk6-truck-evidence-and-priority.pdf (3p) [still on a teacher page].
- **4SW-Wk6-Day2** — student can no longer open: 4sw-wk6-transferable-skills-evidence.pdf (4p) [still on a teacher page].
- **4SW-Wk6-Day3** — student can no longer open: 4sw-wk6-career-organization-types.pdf (3p) [still on a teacher page].
- **4SW-Wk6-Day4** — student can no longer open: 4sw-wk6-integrity-and-evidence-audit.pdf (3p) [still on a teacher page].
- **4SW-Wk6-Day5** — student can no longer open: 4sw-wk6-mid-year-evidence-reflection.pdf (4p) [still on a teacher page].
- **5SW-Wk1-Day1** — student can no longer open: 5sw-wk1-safety-supervisor-evidence-plan.pdf (3p) [still on a teacher page].
- **5SW-Wk1-Day2** — student can no longer open: 5sw-wk1-three-career-evidence-comparison.pdf (4p) [still on a teacher page].
- **5SW-Wk1-Day3** — student can no longer open: 5sw-wk1-concept-building-design.pdf (4p) [still on a teacher page].
- **5SW-Wk1-Day4** — student can no longer open: 5sw-wk1-design-test-and-revision.pdf (3p) [still on a teacher page].
- **5SW-Wk1-Day5** — student can no longer open: 5sw-wk1-unexpected-architecture-evidence.pdf (2p) [still on a teacher page].
- **5SW-Wk2-Day1** — student can no longer open: 5sw-wk2-civil-engineer-and-systems-evidence.pdf (2p) [still on a teacher page].
- **5SW-Wk2-Day2** — student can no longer open: 5sw-wk2-assessment-and-emerging-specialty.pdf (3p) [still on a teacher page].
- **5SW-Wk2-Day3** — student can no longer open: 5sw-wk2-bridge-design-options.pdf (4p) [still on a teacher page].
- **5SW-Wk2-Day4** — student can no longer open: 5sw-wk2-bridge-test-and-redesign.pdf (4p) [still on a teacher page].
- **5SW-Wk2-Day5** — student can no longer open: 5sw-wk2-engineering-synthesis.pdf (3p) [still on a teacher page].
- **5SW-Wk3-Day1** — student can no longer open: 5sw-wk3-construction-career-evidence.pdf (3p) [still on a teacher page].
- **5SW-Wk3-Day2** — student can no longer open: 5sw-wk3-routes-and-organizations.pdf (4p) [still on a teacher page].
- **5SW-Wk3-Day3** — student can no longer open: 5sw-wk3-labor-classification.pdf (4p) [still on a teacher page].
- **5SW-Wk3-Day4** — student can no longer open: 5sw-wk3-fictional-evidence-report.pdf (5p) [still on a teacher page].
- **5SW-Wk3-Day5** — student can no longer open: 5sw-wk3-fictional-evidence-report.pdf (5p) [still on a teacher page].
- **5SW-Wk4-Day1** — student can no longer open: 5sw-wk4-skilled-trades-career-evidence.pdf (3p) [still on a teacher page].
- **5SW-Wk4-Day2** — student can no longer open: 5sw-wk4-hvac-evidence-first-field-notes.pdf (6p) [still on a teacher page].
- **5SW-Wk4-Day3** — student can no longer open: 5sw-wk4-skilled-trades-classification.pdf (4p) [still on a teacher page].
- **5SW-Wk4-Day4** — student can no longer open: 5sw-wk4-current-entry-routes.pdf (4p) [still on a teacher page].
- **5SW-Wk4-Day5** — student can no longer open: 5sw-wk4-fictional-water-line-response.pdf (2p) [still on a teacher page], 5sw-wk4-skilled-trades-classification.pdf (4p) [still on a teacher page].
- **5SW-Wk5-Day1** — student can no longer open: 5sw-wk5-salary-source-and-lifestyle-target.pdf (3p) [still on a teacher page].
- **5SW-Wk5-Day2** — student can no longer open: 5sw-wk5-dallas-county-personal-budget.pdf (4p) [still on a teacher page].
- **5SW-Wk5-Day3** — student can no longer open: 5sw-wk5-location-cost-comparison.pdf (2p) [still on a teacher page].
- **5SW-Wk5-Day4** — student can no longer open: 5sw-wk5-paying-for-education-and-training.pdf (3p) [still on a teacher page].
- **5SW-Wk5-Day5** — student can no longer open: 5sw-wk5-three-career-budget-portfolio.pdf (4p) [still on a teacher page].
- **5SW-Wk6-Day1** — student can no longer open: 5sw-wk6-real-estate-career-boundaries.pdf (2p) [still on a teacher page].
- **5SW-Wk6-Day2** — student can no longer open: 5sw-wk6-trec-and-variable-income.pdf (3p) [still on a teacher page].
- **5SW-Wk6-Day3** — student can no longer open: 5sw-wk6-flip-this-house-evidence-plan.pdf (1p) [still on a teacher page].
- **5SW-Wk6-Day4** — student can no longer open: 5sw-wk6-real-estate-labor-evidence.pdf (2p) [still on a teacher page].
- **5SW-Wk6-Day5** — student can no longer open: 5sw-wk6-six-weeks-evidence-brief.pdf (2p) [still on a teacher page].
- **6SW-Wk1-Day1** — student can no longer open: 6sw-wk1-community-classroom-plan.pdf (2p) [still on a teacher page].
- **6SW-Wk1-Day2** — student can no longer open: 6sw-wk1-texas-education-routes.pdf (3p) [still on a teacher page].
- **6SW-Wk1-Day3** — student can no longer open: 6sw-wk1-education-job-evidence.pdf (2p) [still on a teacher page].
- **6SW-Wk1-Day4** — student can no longer open: 6sw-wk1-teach-through-play-service.pdf (2p) [still on a teacher page].
- **6SW-Wk1-Day5** — student can no longer open: 6sw-wk1-education-evidence-portfolio.pdf (3p) [still on a teacher page].
- **6SW-Wk2-Day1** — student can no longer open: 6sw-wk2-podcast-production-plan.pdf (2p) [still on a teacher page].
- **6SW-Wk2-Day2** — student can no longer open: 6sw-wk2-first-resume-draft.pdf (3p) [still on a teacher page].
- **6SW-Wk2-Day3** — student can no longer open: 6sw-wk2-audio-cue-and-resume-revision.pdf (1p) [still on a teacher page].
- **6SW-Wk2-Day4** — student can no longer open: 6sw-wk2-effective-job-search.pdf (3p) [still on a teacher page].
- **6SW-Wk2-Day5** — student can no longer open: 6sw-wk2-audio-cue-and-resume-revision.pdf (1p) [still on a teacher page], 6sw-wk2-effective-job-search.pdf (3p) [still on a teacher page], 6sw-wk2-first-resume-draft.pdf (3p) [still on a teacher page], 6sw-wk2-merch-mode-design.pdf (2p) [still on a teacher page].
- **6SW-Wk3-Day1** — student can no longer open: 6sw-wk3-click-factor-campaign.pdf (2p) [still on a teacher page].
- **6SW-Wk3-Day2** — student can no longer open: 6sw-wk3-written-communication-and-change.pdf (2p) [still on a teacher page].
- **6SW-Wk3-Day3** — student can no longer open: 6sw-wk3-expert-edge-plan.pdf (2p) [still on a teacher page].
- **6SW-Wk3-Day4** — student can no longer open: 6sw-wk3-family-fun-pass-analysis.pdf (2p) [still on a teacher page].
- **6SW-Wk3-Day5** — student can no longer open: 6sw-wk3-marketing-evidence-brief.pdf (4p) [still on a teacher page].
- **6SW-Wk4-Day1** — student can no longer open: 6sw-wk4-sales-pitch-plan.pdf (2p) [still on a teacher page].
- **6SW-Wk4-Day2** — student can no longer open: 6sw-wk4-pitch-delivery-record.pdf (2p) [still on a teacher page].
- **6SW-Wk4-Day3** — student can no longer open: 6sw-wk4-brainboost-and-career-outline.pdf (2p) [still on a teacher page].
- **6SW-Wk4-Day4** — student can no longer open: 6sw-wk4-appearance-and-rehearsal.pdf (2p) [still on a teacher page].
- **6SW-Wk4-Day5** — student can no longer open: 6sw-wk4-career-oral-evidence.pdf (2p) [still on a teacher page].
- **6SW-Wk5-Day1** — student can no longer open: 6sw-wk5-job-search-and-posting-evidence.pdf (2p) [still on a teacher page].
- **6SW-Wk5-Day2** — student can no longer open: 6sw-wk5-cover-letter-simulation.pdf (3p) [still on a teacher page], 6sw-wk5-job-skills-rubric.pdf (2p) [still on a teacher page].
- **6SW-Wk5-Day3** — student can no longer open: 6sw-wk5-application-and-references.pdf (4p) [still on a teacher page].
- **6SW-Wk5-Day4** — student can no longer open: 6sw-wk5-interview-readiness.pdf (3p) [still on a teacher page].
- **6SW-Wk5-Day5** — student can no longer open: 6sw-wk5-mock-interview-and-thank-you.pdf (4p) [still on a teacher page].
- **6SW-Wk6-Day1** — student can no longer open: 6sw-wk6-career-evidence-inventory.pdf (2p) [still on a teacher page].
- **6SW-Wk6-Day2** — student can no longer open: 6sw-wk6-individual-career-plan.pdf (4p) [still on a teacher page].
- **6SW-Wk6-Day3** — student can no longer open: 6sw-wk6-capstone-presentation-plan.pdf (2p) [still on a teacher page].
- **6SW-Wk6-Day4** — student can no longer open: 6sw-wk6-capstone-delivery-record.pdf (2p) [still on a teacher page].
- **6SW-Wk6-Day5** — student can no longer open: 6sw-wk6-final-course-reflection.pdf (2p) [still on a teacher page].

## 3. Cross-day dependency chains

53 student pages carry persistent-artifact or prior-day cues ('packet', 'from Day N', 'yesterday', 'same record', 'keep this'); 51 of them also lost an artifact that same day.

### Confirmed broken chains (the referenced artifact is linked from NO student page in the course)

| day_key | on-page instruction | referenced artifact | Canvas file id(s) | reachable from any student page? |
|---|---|---|---|---|
| 1SW-Wk2-Day3 | "add the BLS title, median/year, education, and outlook to yesterday's three records" / "Open your five-page salary packet" | wk2-it-salary-comparison.pdf (5p) | 14580354 | No — teacher page only |
| 1SW-Wk2-Day5 | "Turn in the five-page IT Salary Comparison packet with the Career Fit Reflection on page 5" | wk2-it-salary-comparison.pdf (5p) | 14580354 | No — teacher page only |
| 4SW-Wk3-Day5 | "Reopen the four-page Action Plan you started on Day 2" | 4sw-wk3-aviation-route-action-plan.pdf | 14591657 | No |
| 5SW-Wk3-Day5 | "Reopen the shared five-page evidence report from Day 4" | 5sw-wk3-fictional-evidence-report.pdf | 14591684, 14591689 | No |
| 5SW-Wk4-Day3 | "Keep this evidence available for the final score on Day 5" | 5sw-wk4-skilled-trades-classification.pdf | 14562626, 14570311 | No |
| 6SW-Wk6-Day2 | "Keep this plan in its original location; Day 4 will not ask you to upload it again" | 6sw-wk6-individual-career-plan.pdf | 14562777, 14579640 | No |
| 2SW-Wk5-Day5 | "Update the SMART goal, time block, and backup strategy from Day 3" | 2sw-wk5-work-experience-skills-synthesis.pdf | 14580371, 14662897 | No |
| 3SW-Wk6-Day3 | "...when you used the workbook yesterday" (support packet) | 3sw-wk6-million-dollar-idea-support-packet.pdf | 14591642 | No |

### All pages carrying cross-day / persistent-artifact cues

- **1SW-Wk0-Day2** (`student-1sw-wk0-day-2-who-are-you-at-work`) — lost here: none
    - "Follow along while your teacher uses the same chart shown below."
    - "Six-type chart · Keep this open Use this chart to compare what each type likes to do."
- **1SW-Wk0-Day4** (`student-1sw-wk0-day-4-my-career-journey`) — lost here: my-career-journey.pdf
    - "Do not start a different packet."
- **1SW-Wk2-Day2** (`student-1sw-wk2-day-2-compare-programming-careers`) — lost here: 1sw-wk2-day2-programming-pathway-deep-dive-software-web-app-game.pdf, wk2-it-salary-comparison.pdf
    - "# STUDENT: 1SW Wk2 Day 2 - Compare Programming Careers | published=True Week 2 · Day 2 Start your three-career evidence packet Browse four programming Hats, choose three careers, and record their HQIM work, preparation, and salary evidence."
    - "Response Home: Five-Page IT Salary Comparison Packet (pp."
    - "Keep this packet! Day 3 adds BLS evidence to the same three records."
- **1SW-Wk2-Day3** (`student-1sw-wk2-day-3-resilience-and-salary-showdown`) — lost here: 1sw-wk2-day3-powerskill-resilience-it-salary-showdown.pdf, wk2-flip-the-failure-scaffold.pdf
    - "eek 2 · Day 3 Flip the failure and add the national cross-check Plan how a cybersecurity team recovers, then add four BLS fields to the three careers you chose yesterday."
    - "26 (Flip the Failure) & Five-Page Salary Packet (pp."
    - "Today you will turn four setbacks into specific resilience actions in your workbook; add the BLS title, median/year, education, and outlook to yesterday’s three records; and make one evidence-based salary or growth comparison claim on page 4."
- **1SW-Wk2-Day5** (`student-1sw-wk2-day-5-personality-style-and-it-decision`) — lost here: wk2-day5-it-pathway-decision.pdf
    - "Response Home: Five-Page IT Salary Packet (p."
    - "Today you will complete and review Xello Personality Style; save three careers from your completed research packet; finish the four-part Career Fit Reflection on page 5; and submit the complete five-page Minor 2 packet."
    - "Minor 2 Evidence: Turn in the five-page IT Salary Comparison packet with the Career Fit Reflection on page 5."
- **1SW-Wk3-Day5** (`student-1sw-wk3-day-5-learning-style-quiz-and-lesson`) — lost here: wk3-day5-learning-style-connection.pdf
    - "Before you begin: Turn in the complete 16-point Major 1 packet (App Wireframes + Emerging Tech Research Sheet)."
    - "re done when the Learning Style quiz and Learning styles lesson are complete; your connection sheet names a method, task, obstacle, and next test; and your app packet and emerging-career research sheet are turned in together."
- **1SW-Wk4-Day5** (`student-1sw-wk4-day-5-add-skills-and-submit-evidence`) — lost here: wk4-day5-xello-skill-connection.pdf
    - "Minor 3 Submission: Today you turn in the complete 16-point Minor 3 packet (Team Program Evidence + Individual Skill Connection + Xello Verification)."
    - "orking logic; complete the required Add Skills task in Xello; complete your individual skill-to-career connection sheet; and submit your final Minor 3 evidence packet."
- **1SW-Wk5-Day5** (`student-1sw-wk5-day-5-capstone-goal-and-reflection`) — lost here: wk5-reflection-update-template.pdf
    - "published=False Week 5 · Day 5 Finish the 1st Six Weeks capstone Create an original postsecondary symbol, update your career thinking, and submit one evidence packet."
    - "Response Home: 1st Six Weeks Capstone Packet (Major 2: Bootcamp Plan + Flyer + Goal Symbol + Career Journey Update) & CCE Evidence Log Entry 1."
    - "1st Six Weeks Capstone Submission: Today you turn in the complete 16-point Major 2 Capstone packet and log Entry 1 in your CCE Evidence Log."
- **2SW-Wk1-Day1** (`student-2sw-wk1-day-1-explore-legal-careers`) — lost here: career-research-worksheet.pdf
    - "Complete the same worksheet on paper or by annotating the PDF."
- **2SW-Wk1-Day3** (`student-2sw-wk1-day-3-city-council-ordinances`) — lost here: 2sw-wk1-city-council-plan.pdf
    - "Response Home: Complete your work on the City Council Town and Ordinance Plan (digital annotation or printed packet)."
- **2SW-Wk1-Day4** (`student-2sw-wk1-day-4-policy-showdown`) — lost here: 2sw-wk1-legal-entrepreneur-card.pdf, 2sw-wk1-policy-argument-and-evidence.pdf
    - "Submit your written packet or digital annotation."
- **2SW-Wk1-Day5** (`student-2sw-wk1-day-5-legal-career-evidence-and-xello`) — lost here: none
    - "Response Home: Submit your completed Major 1 Packet (Position Paper + Legal Entrepreneur Card) to the Canvas assignment and complete your Xello Life Experience Connection Sheet ."
    - "” You are done when: Your final Major 1 packet (Position Paper + Entrepreneur Card) is submitted."
- **2SW-Wk2-Day1** (`student-2sw-wk2-day-1-first-responder-routes`) — lost here: 2sw-wk2-first-responder-route-guide.pdf
    - "Response Home: Complete your work on the First Responder Route Guide Comparison Sheet (digital annotation or printed packet)."
- **2SW-Wk2-Day5** (`student-2sw-wk2-day-5-career-and-integrity-reflection`) — lost here: 2sw-wk2-integrity-career-reflection.pdf
    - "Response Home: Complete and submit your work on the First Responder Career and Integrity Reflection (digital upload, text entry, or printed packet)."
- **2SW-Wk4-Day1** (`student-2sw-wk4-day-1-read-dental-evidence-carefully`) — lost here: 2sw-wk4-smile-squad-observation-record.pdf
    - "Complete the same record independently; no H&L login is required."
- **2SW-Wk5-Day5** (`student-2sw-wk5-day-5-communication-skills-and-goal-synthesis`) — lost here: 2sw-wk5-work-experience-skills-synthesis.pdf
    - "Revise the plan Update the SMART goal, time block, and backup strategy from Day 3."
- **3SW-Wk2-Day4** (`student-3sw-wk2-day-4-evaluate-emerging-plant-tech-work`) — lost here: 3sw-wk2-emerging-plant-tech-evaluation.pdf, 3sw-wk2-plant-science-major-rubric.pdf
    - "Then open the Plant Science Evidence Packet assignment and submit the saved infographic plus today's evaluation together, one time."
- **3SW-Wk2-Day5** (`student-3sw-wk2-day-5-plant-tech-evidence-and-fair-career-investigation`) — lost here: 3sw-wk2-xello-biases-reflection.pdf
    - "Then revise and submit the evidence packet if your teacher has not already collected it."
- **3SW-Wk3-Day2** (`student-3sw-wk3-day-2-field-reports-and-constraints`) — lost here: 3sw-wk3-pest-patrol-field-notes.pdf
    - "If you were absent or a platform did not work The embedded pages and packet are the complete absence route."
- **3SW-Wk3-Day4** (`student-3sw-wk3-day-4-review-revision-and-trends`) — lost here: 3sw-wk3-peer-review-revision.pdf, 3sw-wk3-societal-trends-evaluation.pdf, 3sw-wk3-sustainable-engineering-major-rubric.pdf
    - "” When complete, open the Sustainable Engineering Evidence Packet assignment ."
    - "You are done when: specific peer or self-review; one visible revision; two trends compared; two facts and one limit; packet submitted when complete."
- **3SW-Wk5-Day5** (`student-3sw-wk5-day-5-career-and-business-recommendation`) — lost here: 3sw-wk5-cosmetology-recommendation.pdf
    - "If you were absent or a platform did not work The fixed packet is the full route."
- **3SW-Wk6-Day2** (`student-3sw-wk6-day-2-problem-and-idea-sprint`) — lost here: 3sw-wk6-million-dollar-idea-support-packet.pdf
    - "Use the support and catch-up packet only when the workbook is unavailable or the enlarged scaffold is needed; do not complete both."
    - "If you were absent or a platform did not work The four-page packet is the full no-workbook or independent route."
- **3SW-Wk6-Day3** (`student-3sw-wk6-day-3-stress-test-and-decide`) — lost here: 3sw-wk6-million-dollar-idea-support-packet.pdf
    - "236-237 when you used the workbook yesterday."
    - "Continue the support packet only when that was your Day 2 route."
- **4SW-Wk1-Day2** (`student-4sw-wk1-day-2-career-iceberg`) — lost here: 4sw-wk1-career-iceberg-and-goal.pdf
    - "Use the enlarged support packet or the Canvas annotation only when the workbook is unavailable or you need that route."
    - "If you were absent or a platform did not work The support packet, Canvas annotation, typed list, or audio response replaces the workbook route."
- **4SW-Wk1-Day4** (`student-4sw-wk1-day-4-pathway-and-ctso-decision`) — lost here: 4sw-wk1-pathway-and-ctso-decision.pdf
    - "The paper packet is the complete no-platform response route."
- **4SW-Wk2-Day1** (`student-4sw-wk2-day-1-graduation-and-assessment-decisions`) — lost here: 4sw-wk2-transition-and-assessment-decisions.pdf
    - "Response Home: complete the Transition and Assessment Decisions packet and use evidence to correct a mixed-up assessment claim."
    - "Show my learning: complete the Transition and Assessment Decisions packet and use evidence to correct a mixed-up assessment claim."
    - "Get Ready Use one printed copy of the three-page Transition and Assessment Decisions packet ."
- **4SW-Wk3-Day1** (`student-4sw-wk3-day-1-transportation-cluster-and-survey-design`) — lost here: 4sw-wk3-transportation-survey-design.pdf
    - "166-167 with the three-page team Survey Project packet ."
    - "Your team needs one packet or shared digital copy."
    - "A reason or comparison gets its own full-width writing area in the packet."
- **4SW-Wk3-Day5** (`student-4sw-wk3-day-5-aviation-route-and-action-plan`) — lost here: 4sw-wk3-aviation-route-action-plan.pdf
    - "Get Ready Reopen the four-page Action Plan you started on Day 2 and the two-page 16-point rubric ."
- **4SW-Wk4-Day1** (`student-4sw-wk4-day-1-wildlife-tracking-system-design`) — lost here: 4sw-wk4-wildlife-tracking-drone-design.pdf
    - "105 or the access packet; assumption and tradeoff; evidence-based redesign; occupation work product."
- **5SW-Wk1-Day1** (`student-5sw-wk1-day-1-cluster-roles-and-safety-supervisor`) — lost here: 5sw-wk1-safety-supervisor-evidence-plan.pdf
    - "If you were absent or a site did not work The images, adjacent text, and packet are the full independent route."
- **5SW-Wk1-Day5** (`student-5sw-wk1-day-5-unexpected-architecture-and-synthesis`) — lost here: 5sw-wk1-unexpected-architecture-evidence.pdf
    - "You are done when: two city goals; individual contribution; three role explanations; one correctly labeled fact referenced from Day 2; Day 3-5 evidence submitted privately."
- **5SW-Wk2-Day2** (`student-5sw-wk2-day-2-assessment-impact-and-emerging-work`) — lost here: 5sw-wk2-assessment-and-emerging-specialty.pdf
    - "Get Ready Open the three-page assessment and specialty packet and the student-visible Minor 2 rubric ."
    - "Your packet or typed response is the demonstration of learning."
    - "Use typing, speech-to-text, read-aloud, enlarged print, or the paper packet."
- **5SW-Wk2-Day3** (`student-5sw-wk2-day-3-bridge-design-two-options`) — lost here: 5sw-wk2-bridge-design-options.pdf
    - "Get Ready Open the four-page bridge design packet or the Canvas annotation activity ."
- **5SW-Wk2-Day4** (`student-5sw-wk2-day-4-fixed-data-test-and-redesign`) — lost here: 5sw-wk2-bridge-test-and-redesign.pdf
    - "Get Ready Open the four-page fixed-data and redesign packet or the Canvas annotation activity ."
- **5SW-Wk2-Day5** (`student-5sw-wk2-day-5-mars-transfer-and-weekly-synthesis`) — lost here: 5sw-wk2-engineering-synthesis.pdf
    - "Do not re-upload the Day 2 Minor or the Day 3-4 packets."
- **5SW-Wk3-Day1** (`student-5sw-wk3-day-1-construction-careers-and-preparation`) — lost here: 5sw-wk3-construction-career-evidence.pdf
    - "Get Ready Open the three-page construction career packet or the Canvas annotation activity ."
- **5SW-Wk3-Day2** (`student-5sw-wk3-day-2-training-routes-and-career-organizations`) — lost here: 5sw-wk3-routes-and-organizations.pdf
    - "Get Ready Open the four-page routes and organizations packet or the Canvas annotation activity ."
- **5SW-Wk3-Day3** (`student-5sw-wk3-day-3-classify-four-construction-careers`) — lost here: 5sw-wk3-labor-classification.pdf
    - "Get Ready Open the four-page labor classification packet and the student-visible Minor 3 rubric , or use the Canvas annotation activity ."
    - "High skill uses the documented preparation rule in the packet."
    - "If you were absent or a site did not work All required numbers are in the packet."
- **5SW-Wk3-Day5** (`student-5sw-wk3-day-5-evidence-report-and-individual-briefing`) — lost here: 5sw-wk3-fictional-evidence-report.pdf
    - "Get Ready Reopen the shared five-page evidence report from Day 4 and the formative report feedback guide ."
    - "Revise the same findings; do not recopy them into a second packet."
- **5SW-Wk4-Day1** (`student-5sw-wk4-day-1-four-skilled-trades-careers`) — lost here: 5sw-wk4-skilled-trades-career-evidence.pdf
    - "Get Ready Open the three-page career evidence packet or the Canvas annotation activity ."
    - "Record four careers Use the packet for Electrician, Plumber/Pipefitter/Steamfitter, HVAC Mechanic/Installer, and Welder."
    - "Submit privately Use the practice activity , typed labeled responses, or the one paper packet your teacher collects."
- **5SW-Wk4-Day3** (`student-5sw-wk4-day-3-classify-four-skilled-trades-careers`) — lost here: 5sw-wk4-skilled-trades-classification.pdf
    - "Get Ready Open the four-page classification packet or Major 1 Part A in Canvas ."
    - "Keep this evidence available for the final score on Day 5; you will not need to copy it into a second packet."
    - "High skill uses the packet's documented preparation rule."
- **5SW-Wk4-Day4** (`student-5sw-wk4-day-4-current-entry-routes`) — lost here: 5sw-wk4-current-entry-routes.pdf
    - "Get Ready Open the four-page current entry-routes packet or the Canvas annotation activity ."
- **5SW-Wk5-Day1** (`student-5sw-wk5-day-1-salary-source-and-lifestyle-target`) — lost here: 5sw-wk5-salary-source-and-lifestyle-target.pdf
    - "Get Ready Open the three-page Salary Source and Lifestyle Target packet or the private annotation activity ."
- **5SW-Wk5-Day2** (`student-5sw-wk5-day-2-build-a-dallas-county-personal-budget`) — lost here: 5sw-wk5-dallas-county-personal-budget.pdf
    - "Get Ready Open the four-page Dallas County budget packet or the private annotation activity ."
- **5SW-Wk5-Day3** (`student-5sw-wk5-day-3-compare-the-same-offer-across-locations`) — lost here: 5sw-wk5-location-cost-comparison.pdf
    - "Get Ready Open the two-page Location Cost Comparison packet or the private annotation activity ."
- **5SW-Wk5-Day4** (`student-5sw-wk5-day-4-paying-for-education-and-training`) — lost here: 5sw-wk5-paying-for-education-and-training.pdf
    - "If you were absent or a site did not work The packet contains the full route."
- **5SW-Wk5-Day5** (`student-5sw-wk5-day-5-personal-budget-and-career-evidence-portfolio`) — lost here: 5sw-wk5-three-career-budget-portfolio.pdf
    - "Days 1–4 may help as references, but you do not attach those formative packets again."
    - "BLS medians in the packet so all three records are comparable."
    - "The Day 5 packet is self-contained."
- **5SW-Wk6-Day2** (`student-5sw-wk6-day-2-trec-route-and-variable-income-math`) — lost here: 5sw-wk6-trec-and-variable-income.pdf
    - "Get Ready Open the three-page TREC and math packet or the private annotation activity ."
- **6SW-Wk2-Day2** (`student-6sw-wk2-day-2-write-a-first-resume`) — lost here: 6sw-wk2-first-resume-draft.pdf
    - "If you were absent or a site did not work The packet includes the fictional privacy-safe Jordan model."
- **6SW-Wk2-Day5** (`student-6sw-wk2-day-5-merch-mode-and-final-resume-evidence`) — lost here: 6sw-wk2-audio-cue-and-resume-revision.pdf, 6sw-wk2-effective-job-search.pdf, 6sw-wk2-first-resume-draft.pdf, 6sw-wk2-merch-mode-design.pdf
    - "For Minor 2, review the resume packet , the revision record , the job-search trace , and the visible rubric ."
    - "Use the fixed packets for missing work."
- **6SW-Wk4-Day5** (`student-6sw-wk4-day-5-career-oral-evidence-brief`) — lost here: 6sw-wk4-career-oral-evidence.pdf
    - "Use your Day 3 career outline and Day 4 rehearsal as reference; do not submit every earlier packet."
- **6SW-Wk5-Day4** (`student-6sw-wk5-day-4-interview-preparation`) — lost here: 6sw-wk5-interview-readiness.pdf
    - "Your route is assigned before Day 5; private details are not written on the packet."
- **6SW-Wk6-Day2** (`student-6sw-wk6-day-2-individual-career-plan`) — lost here: 6sw-wk6-individual-career-plan.pdf
    - "Keep this plan in its original location; Day 4 will not ask you to upload it again."

## 4. Orphan check — `docs/resources/worksheets/*.pdf` in Canvas

262 worksheet PDFs on disk. **149** are present in Canvas but linked only from teacher/other pages; **8** are fully orphaned or absent from Canvas.

### Fully orphaned (uploaded to Canvas, linked from no student and no teacher page)

| worksheet | Canvas file id(s) |
|---|---|
| 2sw-wk4-career-evidence-comparison.pdf | 14565343, 14580364 |
| 5sw-wk3-visual-observation-log.pdf | 14562596, 14562609 |
| career-research-worksheet-example-welder.pdf | 14616741 |
| wk1-presentation-rubric.pdf | 14518995 |
| wk2-flip-the-failure-scaffold.pdf | 14519030 |
| wk5-favorite-cluster-connection.pdf | 14565278 |
| wk5-flyer-peer-feedback.pdf | NOT-IN-CANVAS |
| wk5-integrity-reflection-stems.pdf | NOT-IN-CANVAS |

### Teacher-only (linked from a teacher/other page, not from any student page)

| worksheet | Canvas file id(s) |
|---|---|
| 1sw-wk1-robots-for-crayons-action-plan.pdf | 14564524 |
| 2sw-wk1-city-council-plan.pdf | 14565292 |
| 2sw-wk1-emergency-kit-plan.pdf | 14565291 |
| 2sw-wk1-legal-entrepreneur-card.pdf | 14565294 |
| 2sw-wk1-policy-argument-and-evidence.pdf | 14565293 |
| 2sw-wk1-xello-life-experience-connection.pdf | 14565296 |
| 2sw-wk2-clinton-lake-evidence-tracker.pdf | 14580298 |
| 2sw-wk2-first-responder-route-guide.pdf | 14606186 |
| 2sw-wk2-integrity-career-reflection.pdf | 14580301 |
| 2sw-wk2-patient-care-report.pdf | 14565301 |
| 2sw-wk2-trail-simulation-record.pdf | 14580299 |
| 2sw-wk3-clinical-handoff-record.pdf | 14565340, 14580361 |
| 2sw-wk3-nursing-route-comparison.pdf | 14565338 |
| 2sw-wk3-vital-signs-simulator-build.pdf | 14580359 |
| 2sw-wk4-evidence-check-teacher-key.pdf | 14580363 |
| 2sw-wk4-icd10-training-lab.pdf | 14565347 |
| 2sw-wk4-smile-squad-observation-record.pdf | 14565344 |
| 2sw-wk4-toothbrush-design-brief.pdf | 14565345 |
| 2sw-wk4-xello-experiences-checkpoint.pdf | 14662881 |
| 2sw-wk5-active-listening-lab.pdf | 14580366 |
| 2sw-wk5-advocacy-smart-time-plan.pdf | 14611251 |
| 2sw-wk5-conflict-resolution-plan.pdf | 14580365 |
| 2sw-wk5-work-experience-skills-synthesis.pdf | 14580371, 14662897 |
| 2sw-wk5-written-message-lab.pdf | 14580368 |
| 2sw-wk6-cover-letter-lab.pdf | 14561443 |
| 2sw-wk6-mini-medics-design-record.pdf | 14580372 |
| 2sw-wk6-outbreak-investigation-record.pdf | 14561445 |
| 2sw-wk6-outbreak-response-plan.pdf | 14561446 |
| 2sw-wk6-xello-career-matches-reflection.pdf | 14662910 |
| 3sw-wk1-veterinary-career-comparison.pdf | 14580374 |
| 3sw-wk1-veterinary-pathway-brief.pdf | 14662923 |
| 3sw-wk1-veterinary-triage-record.pdf | 14565357 |
| 3sw-wk2-emerging-plant-tech-evaluation.pdf | 14565366 |
| 3sw-wk2-farm-to-table-planner.pdf | 14565363 |
| 3sw-wk2-xello-biases-reflection.pdf | 14662934 |
| 3sw-wk3-drone-design-brief.pdf | 14565369 |
| 3sw-wk3-peer-review-revision.pdf | 14565370 |
| 3sw-wk3-pest-patrol-field-notes.pdf | 14565368 |
| 3sw-wk3-societal-trends-evaluation.pdf | 14591629 |
| 3sw-wk4-cater-create-event-brief.pdf | 14591633 |
| 3sw-wk4-culinary-twist-menu-brief.pdf | 14561545, 14591631 |
| 3sw-wk4-hospitality-recommendation.pdf | 14591634 |
| 3sw-wk4-hotel-rescue-response.pdf | 14565376 |
| 3sw-wk4-motivation-career-comparison.pdf | 14591632 |
| 3sw-wk5-cosmetology-pathway-decision.pdf | 14591641 |
| 3sw-wk5-cosmetology-recommendation.pdf | 14565392 |
| 3sw-wk5-salon-wellness-campaign.pdf | 14565391 |
| 3sw-wk5-sfx-build-test-record.pdf | 14565387 |
| 3sw-wk5-sfx-concept-lab-brief.pdf | 14565386 |
| 3sw-wk5-sfx-quality-revision.pdf | 14591640 |
| 3sw-wk6-budget-and-scholarship-plan.pdf | 14663175 |
| 3sw-wk6-entrepreneurship-opportunity-guide.pdf | 14561631 |
| 3sw-wk6-million-dollar-idea-support-packet.pdf | 14591642 |
| 3sw-wk6-venture-brief-and-pitch-record.pdf | 14561633 |
| 4sw-wk1-career-iceberg-and-goal.pdf | 14561667, 14565911 |
| 4sw-wk1-midyear-career-blueprint.pdf | 14662864 |
| 4sw-wk1-midyear-profile-audit.pdf | 14565910 |
| 4sw-wk1-pathway-and-ctso-decision.pdf | 14591646 |
| 4sw-wk2-four-year-course-plan-draft.pdf | 14562515, 14662869 |
| 4sw-wk2-individual-high-school-career-plan.pdf | 14611266 |
| 4sw-wk2-smart-experience-action-plan.pdf | 14565921 |
| 4sw-wk2-transition-and-assessment-decisions.pdf | 14591648 |
| 4sw-wk3-airport-design-simulation-lab.pdf | 14562528, 14591655 |
| 4sw-wk3-aviation-route-action-plan.pdf | 14591657 |
| 4sw-wk3-transportation-survey-design.pdf | 14591653 |
| 4sw-wk4-drone-operation-decision-readiness.pdf | 14565935 |
| 4sw-wk4-drone-systems-evidence-brief.pdf | 14565937 |
| 4sw-wk4-drone-systems-test.pdf | 14562538, 14591659 |
| 4sw-wk4-wildlife-tracking-drone-design.pdf | 14562537, 14565933 |
| 4sw-wk5-ase-and-automotive-training-routes.pdf | 14591662 |
| 4sw-wk5-automotive-evidence-brief.pdf | 14591665 |
| 4sw-wk5-automotive-route-decision.pdf | 14591664 |
| 4sw-wk5-crash-crew-evidence-and-preliminary-plan.pdf | 14562546, 14591661 |
| 4sw-wk5-three-automotive-occupations.pdf | 14562547, 14591663 |
| 4sw-wk6-career-organization-types.pdf | 14565958 |
| 4sw-wk6-integrity-and-evidence-audit.pdf | 14565959 |
| 4sw-wk6-transferable-skills-evidence.pdf | 14562558, 14565957 |
| 4sw-wk6-truck-evidence-and-priority.pdf | 14562557, 14565956 |
| 5sw-wk1-concept-building-design.pdf | 14562575, 14565968 |
| 5sw-wk1-design-test-and-revision.pdf | 14562576, 14565969 |
| 5sw-wk1-safety-supervisor-evidence-plan.pdf | 14562574, 14565966 |
| 5sw-wk1-three-career-evidence-comparison.pdf | 14562573, 14565967 |
| 5sw-wk1-unexpected-architecture-evidence.pdf | 14565970 |
| 5sw-wk2-assessment-and-emerging-specialty.pdf | 14562589, 14568714 |
| 5sw-wk2-bridge-design-options.pdf | 14562591, 14591677 |
| 5sw-wk2-civil-engineer-and-systems-evidence.pdf | 14562590, 14568713 |
| 5sw-wk2-engineering-synthesis.pdf | 14568718 |
| 5sw-wk3-construction-career-evidence.pdf | 14562606, 14570242 |
| 5sw-wk3-fictional-evidence-report.pdf | 14591684, 14591689 |
| 5sw-wk3-labor-classification.pdf | 14562608, 14591683 |
| 5sw-wk3-routes-and-organizations.pdf | 14562607, 14570243 |
| 5sw-wk4-current-entry-routes.pdf | 14562627, 14570312 |
| 5sw-wk4-fictional-water-line-response.pdf | 14570319, 14591690 |
| 5sw-wk4-hvac-evidence-first-field-notes.pdf | 14562625, 14570310 |
| 5sw-wk4-skilled-trades-career-evidence.pdf | 14562624, 14570309 |
| 5sw-wk4-skilled-trades-classification.pdf | 14562626, 14570311 |
| 5sw-wk5-dallas-county-personal-budget.pdf | 14562637, 14570334 |
| 5sw-wk5-paying-for-education-and-training.pdf | 14570336 |
| 5sw-wk5-salary-source-and-lifestyle-target.pdf | 14562636, 14662889 |
| 5sw-wk5-three-career-budget-portfolio.pdf | 14570342, 14662892 |
| 5sw-wk6-flip-this-house-evidence-plan.pdf | 14562677, 14572269 |
| 5sw-wk6-real-estate-career-boundaries.pdf | 14562675, 14572251 |
| 5sw-wk6-real-estate-labor-evidence.pdf | 14572282 |
| 5sw-wk6-six-weeks-evidence-brief.pdf | 14596047, 14596052 |
| 5sw-wk6-trec-and-variable-income.pdf | 14562676, 14572260 |
| 6sw-wk1-community-classroom-plan.pdf | 14562692, 14596064 |
| 6sw-wk1-education-evidence-portfolio.pdf | 14562695, 14662901 |
| 6sw-wk1-teach-through-play-service.pdf | 14562694, 14596066 |
| 6sw-wk1-texas-education-routes.pdf | 14562693, 14596065 |
| 6sw-wk2-effective-job-search.pdf | 14562712, 14575279 |
| 6sw-wk2-first-resume-draft.pdf | 14562711, 14611292 |
| 6sw-wk2-merch-mode-design.pdf | 14575296 |
| 6sw-wk2-podcast-production-plan.pdf | 14562710, 14575253 |
| 6sw-wk3-click-factor-campaign.pdf | 14562730, 14596075 |
| 6sw-wk3-expert-edge-plan.pdf | 14562731, 14578333 |
| 6sw-wk3-marketing-evidence-brief.pdf | 14562733, 14578336 |
| 6sw-wk3-written-communication-and-change.pdf | 14578332, 14596077 |
| 6sw-wk4-appearance-and-rehearsal.pdf | 14596080, 14596086 |
| 6sw-wk4-career-oral-evidence.pdf | 14596081, 14596087 |
| 6sw-wk4-pitch-delivery-record.pdf | 14562750, 14579337 |
| 6sw-wk4-sales-pitch-plan.pdf | 14562749, 14579336 |
| 6sw-wk5-cover-letter-simulation.pdf | 14562759, 14579493 |
| 6sw-wk5-mock-interview-and-thank-you.pdf | 14562761, 14611300 |
| cce-first-week-goal-setting.docx | 14621434 |
| cce-first-week-goal-setting.pdf | 14615030 |
| clipboard-roster-grid.pdf | 14518996, 14519032, 14519386 |
| manufacturing-pathways-scaffold.pdf | 14518990 |
| my-career-journey.pdf | 14615031 |
| technician-checklist-scaffold.pdf | 14518991 |
| wk2-day5-it-pathway-decision.pdf | 14519033 |
| wk2-it-programs-scaffold.pdf | 14519022 |
| wk2-it-salary-comparison.pdf | 14580354 |
| wk3-day4-career-comparison.pdf | 14519358 |
| wk3-emerging-tech-research-template.pdf | 14580295 |
| wk3-transferable-skills-list.pdf | 14519351 |
| wk3-ux-audit-scaffold.pdf | 14519352 |
| wk3-wireframe-template.pdf | 14519353 |
| wk4-day1-career-interest-check.pdf | 14662886 |
| wk4-day2-route-decision.pdf | 14519377 |
| wk4-day4-customer-service-check.pdf | 14565271 |
| wk4-day5-xello-skill-connection.pdf | 14519389 |
| wk4-education-pathway-comparison.pdf | 14519375 |
| wk4-help-desk-program-evidence.pdf | 14565268 |
| wk4-help-desk-role-play-script.pdf | 14565269 |
| wk4-troubleshooting-step-sort-cards.pdf | 14519380 |
| wk5-bootcamp-planning-template.pdf | 14565276 |
| wk5-cyberseek-pathway.pdf | 14565274 |
| wk5-red-flag-checklist.pdf | 14565275 |
| wk5-reflection-update-template.pdf | 14565280 |

## 5. 1SW Wk2 in detail

`wk2-it-salary-comparison.pdf` = **5 pages** (`pdfinfo`, 226,903 bytes, Chromium/Skia). Canvas file **14580354**. Its source (`build/worksheet_sources/wk2-it-salary-comparison.md`) states: "Use this same packet on Days 2, 3, and 5."

Variants: `wk2-it-salary-comparison-model.pdf` (2p, file 14564638) and `wk2-it-salary-comparison-bilingual.pdf` (3p, file 14564639). Neither is the blank 5-page packet.

| Day | student page | files a student can open | Google Doc target | what the student cannot open |
|---|---|---|---|---|
| Day 1 | student-1sw-wk2-day-1-map-the-it-cluster | irving-it-programs-page-1.png (14519038), it-app-exploration.png (14519040), it-chapter-opener.jpg (14603834) | 1hoghFvnhWMpQ6wMHF_LKQQNf3zDoIpoFXzmRV7PGlJ4 (2 anchors) | wk2-it-programs-scaffold.pdf (14519022) and 1sw-wk2-day1-it-cluster-tour-... .pdf (14519034) — both teacher page only |
| Day 2 | student-1sw-wk2-day-2-compare-programming-careers | it-app-exploration.png (14519042), wk2-career-research-web-developer.pdf (14661630) | 15MLWoa58s8FZtLZQdWnwS2Mzj58HQCKY1Ric2hWDc2o (2 anchors, same doc) | **wk2-it-salary-comparison.pdf (14580354, 5p)** and 1sw-wk2-day2-programming-pathway-deep-dive-... .pdf (14519035) — teacher page only |
| Day 3 | student-1sw-wk2-day-3-resilience-and-salary-showdown | wk2-it-salary-comparison-model.pdf (14564638, 2p), wk2-it-salary-comparison-bilingual.pdf (14564639, 3p), wk2-bls-data-guide.pdf (14580356), flip-the-failure-chart.jpg (14606182), resilience-scenario.jpg (14606183) | 1jua53MPweEUjs4uBfVEoS71fyhtK3swtvcJNxj90k-8 (3 anchors, same doc) | **wk2-it-salary-comparison.pdf (14580354)** — the page says "Open your five-page salary packet"; also wk2-flip-the-failure-scaffold.pdf (14519030, fully orphaned) and 1sw-wk2-day3-powerskill-resilience-it-salary-showdown.pdf |
| Day 4 | student-1sw-wk2-day-4-test-a-programming-concept | (no Canvas files linked) | 1D-wBbboQZ9qkXvu91W__I_S2vfZOSowyhJrAdAmGc2I (1 anchor) | clipboard-roster-grid.pdf (14519032), 1sw-wk2-day4-code-org-hour-of-code-day-1.pdf (14519037) — teacher page only |
| Day 5 | student-1sw-wk2-day-5-personality-style-and-it-decision | wk2-salary-hoc-rubric.pdf (14564640) | 1GduEsG_eXneSB_mGsJqCUIA2VplZZ9M2GkPnSn5xhlA (1 anchor) | **wk2-it-salary-comparison.pdf (14580354)** — the page requires turning in page 5 of it as Minor 2; also wk2-day5-it-pathway-decision.pdf (14519033), personality-styles.pdf (14517255) |

Teacher facilitator guides: **yes**, the packet is still linked for teachers. `teacher-1sw-wk2-day-2-facilitator-guide` links file 14580354 (`wk2-it-salary-comparison.pdf`) alongside 14519035 and 14661630. `teacher-1sw-wk2-day-3-facilitator-guide` links the model (14564638) and BLS guide (14580356) but **not** 14580354. No teacher page for Day 5 links 14580354.

The three Wk2 Google Docs that the student buttons open are `1SW Wk2 Day 2: Programming Pathway Deep-Dive` (mini-case, 1 scenario + 3 prompts), `1SW Wk2 Day 3` (3-career salary/education/growth matrix + one bottom-line claim), and `1SW Wk2 Day 5` (personality-style + IT decision). None contains the packet's per-career evidence records.

## 6. Duplicate / wrong-day Google Doc content (separate defect found during the audit)

All 180 routes have distinct `google_doc.id` values, but **six of those docs have byte-identical body text**: the `1SW Wk0 Day 2 "Who Are You at Work?" — H&L Setup and Discover Your Core` ticket.

| day_key | google_doc.id | internal title of the doc the student opens |
|---|---|---|
| 1SW-Wk0-Day2 | 1vfmAFfDd9dR3rygesc0-FhFljoM6OLueUZjc8cxv8LM | CCE \| 1SW Wk0 Day 2 \| Who Are You at Work? |
| 1SW-Wk0-Day3 | 1NWbgTULXk-_2WflAccPMHGQRKeYFt8xu-41oMKczRhQ | CCE \| 1SW Wk0 Day 2 \| Who Are You at Work? |
| 1SW-Wk0-Day4 | 1zE7zuPdx5arGs0IoTFhXjRxVvz4JZ-TVdG7NO1nNsjU | CCE \| 1SW Wk0 Day 2 \| Who Are You at Work? |
| 1SW-Wk0-Day5 | 1nMR01dH0hSxJzcQqCwizzB1QDVS1payEx8a7bR01lsA | CCE \| 1SW Wk0 Day 2 \| Who Are You at Work? |
| 1SW-Wk3-Day3 | 1SyQB5eeYORonPaLr8_U3LKUp7bC2BnECxTpsRST7OuU | CCE \| 1SW Wk0 Day 2 \| Who Are You at Work? |
| 1SW-Wk5-Day5 | 1QKZLyhP4bQUoHRi27u4RX0RHaY6y0XCetS2akxlBeOg | CCE \| 1SW Wk0 Day 2 \| Who Are You at Work? |

`1SW-Wk0-Day2` is the legitimate one. The other five student pages send students to a copy of the Day 2 H&L setup ticket instead of their own day's response work. `1SW-Wk0-Day1` is a separate, milder mismatch: its doc is titled `CCE First Week Goal-Setting Sheet` (correct content, non-standard title, registry marks it `title_status: rename_pending`).

Caveat: this is measured from the 2026-08-25 trusted-read snapshot, not from a live Docs read today; the duplication could in principle be a snapshot defect rather than a live-document defect. It is worth a direct check of the five doc ids.

## Method notes / limits

- "Reachable from the student page" = the numeric Canvas file id appears in a `/files/<id>/` href in the dumped student page HTML. Duplicate uploads sharing a `display_name` were resolved together, so a second copy of the same worksheet counts as reachable.
- "Reproduced in the Google Doc" = worksheet title or >=50% of its `##` section headings appear in the Doc body text extracted from `document-text.md`. No Doc came close.
- Cross-day cue scan was regex over the dumped student page `.txt` files; it finds explicit textual references only, not implied continuity.
