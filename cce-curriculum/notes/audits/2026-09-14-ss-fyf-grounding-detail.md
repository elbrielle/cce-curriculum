# Scope-and-Sequence / FYF Grounding Audit — CCE (Canvas course 98060)

Date: 2026-09-14 · Read-only audit · Canvas snapshot: `.tmp/canvas-dump-20260914/`
Sources: `cce-curriculum/scope-and-sequence.md` (byte-identical to `docs/scope-and-sequence.md`, no divergence),
`docs/<n>sw/wk<k>-*/overview.md` + `day1..5.md` (180 day files, all present),
Canvas `modules.json` / `pages.json` / `files.json` / `assignments.json`,
FYF extract `cce-curriculum/resources/reference-pdfs/IrvingFindYourFuture2026.txt` (309 segments; printed page = PDF page − 6).

Machine-readable companion: `fyf-citation-check.csv` (415 rows), `extract.json`, `alignment.json`, `fyf_page_index.json`.

## 0. Headline

- **Structure is sound.** 36 weeks + Wk0 map 1:1 onto 37 Canvas modules in S&S order, each with exactly 5 STUDENT pages, 5 TEACHER guides, and a graded spine. No missing or extra week. No day file missing.
- **Page numbers are sound.** 369 distinct printed-page references were resolved against the FYF extract. **Zero wrong page numbers.** Every cited printed page exists and carries content consistent with the week's cluster. The 13 "partial" rows are multi-page activities where the named section title sits on the first page of the range (e.g. "Hotel Rescue" titled on p. 117, cited again on p. 118) — benign.
- **The gap is delivery, not accuracy.** The workbook grounding lives in `day.md`. It very often does not reach the STUDENT Canvas page. 33 days cite FYF in `day.md` and cite nothing on the student page; whole weeks (2SW Wk1, Wk2, Wk3; 5SW Wk5, Wk6) put **no workbook page in front of students at all**.
- **H&L platform instruction has collapsed to 1SW Wk0–Wk2.** Only 6 `[H&L PLATFORM]` markers exist in the entire 180-day corpus, all in 1SW. Only 9 student pages mention Hats & Ladders, all in 1SW Wk0–Wk2. S&S assigns H&L app work in 2SW Wk1–Wk2, 2SW Wk3, 3SW, 4SW and 6SW; none of it reaches students.
- **Decision D-8 is not delivered.** D-8 ("adopt all 14 District pages + 13 App Exploration pages as standing per-week content") is only partly honored: of 13 App Exploration pages, `day.md` cites 4 (38, 58, 212, 254) and student pages show 2 (38, 254). Of 14 District pages, `day.md` cites 9 and student pages show 6.
- **Citation form is not standardized.** Only 26 references across 15 of 180 days use the mandated `(FYF p. N: "Section Name")` form. The rest use bare `FYF p. N`, `FYF pp. N-M`, `*Find Your Future* workbook pp. N-M`, or unlabeled "workbook p. N".

## 1. Module / week alignment table

Legend: "student pages omit S&S pp. X" = the week's five STUDENT Canvas pages never name those workbook pages, though S&S assigns them.
| Wk | S&S topic / cluster | S&S FYF pages | Canvas module (pub) | Canvas Day 1-5 student titles | docs overview.md | Graded items | Flags |
|---|---|---|---|---|---|---|---|
| 1SW wk0 | CCE Routines & Career Self-Discovery / Onboarding (Cross-Cluster) | 4-5,9-11,21-22 | 1SW Wk0: Classroom Routines and Career Self-Discovery (pub) | CCE Notebook and First-Week Goal · Who Are You at Work? · Work Values and Building Blocks · My Career Journey · Career Perks, Neutrals, and Quirks | 1SW Wk0: CCE Routines and Career Self-Discovery | MINOR 1: My Career Journey Reflection | student pages omit S&S pp. 4,22 |
| 1SW wk1 | Robotics / Manufacturing / Manufacturing | 199-212 | 1SW Wk1: Built by Bots - Robotics and Manufacturing Careers (pub) | Manufacturing Cluster Tour · Machine Breakdown Mystery · Design Build Test · Robots for Crayons Action Plan · Xello Matchmaker | Week 1: Built by Bots — Robotics & Manufacturing Careers | PRACTICE: 1SW Wk1 Matchmaker Reflection | student pages omit S&S pp. 199,203,209-212 |
| 1SW wk2 | Programming / IT / Information Technology | 23,26-27,36-38 | 1SW Wk2: Code Your Future - Programming Careers in IT (pub) | Map the IT Cluster · Compare Programming Careers · Resilience and Salary Showdown · Test a Programming Concept · Personality Style and IT Decision | Week 2: Code Your Future — Programming Careers in IT | MINOR 2: IT Salary Comparison and Career-Fit Reflection | student pages omit S&S pp. 27,36-38 |
| 1SW wk3 | Computer Science / IT / Information Technology | 28-33,38 | 1SW Wk3: Computer Science and Networking Careers (unpub) | Compare Networking Careers · Audit a Website · Build Four App Screens · Research an Emerging IT Career · Learning Style Quiz and Lesson | Week 3: Computer Science & Networking Careers | MAJOR 1: App Design and Emerging-Career Evidence Packet | student pages omit S&S pp. 38 |
| 1SW wk4 | Tech Support / IT / Information Technology | 36-38 | 1SW Wk4: Tech Support Careers and MakeCode (unpub) | IT Support Careers and Interests · Compare Education Routes · Build a Help Desk Sequence · Test and Role-Play · Add Skills and Submit Evidence | Week 4: Tech Support Careers and MakeCode | MINOR 3: Help Desk Program Evidence and Career Connection | student pages omit S&S pp. 36-38; NO workbook page on any student page |
| 1SW wk5 | Cybersecurity / IT / Information Technology | 24-25,34-38 | 1SW Wk5: Cybersecurity and Capstone (unpub) | Cybersecurity Career Routes · Safe or Spoofed Inbox · Community Cybersecurity Bootcamp · Strengthen Cybersecurity Career Evidence · Capstone Goal and Reflection | Week 5: Cybersecurity and Capstone | MAJOR 2: Cybersecurity Capstone Evidence Portfolio | student pages omit S&S pp. 24-25,34-35 |
| 2SW wk1 | Legal Studies / Law, Public Safety, Corrections & Security | 39-47,50-51,56-58 | 2SW Wk1: Legal Studies and Policy Evidence (unpub) | Explore Legal Careers · Emergency Kit Decisions · City Council Ordinances · Policy Showdown · Legal Career Evidence and Xello | Week 1: Order in the Court — Legal Careers | MAJOR 1: Legal Policy Position Evidence | student pages omit S&S pp. 39-47,50-51,56-58; NO workbook page on any student page |
| 2SW wk2 | Law Enforcement / EMT / Law, Public Safety, Corrections & Security | 48-49,52-58 | 2SW Wk2: First Responders - Evidence, Response, and Handoff (unpub) | First Responder Routes · Clinton Lake Evidence · Trail Response Simulation · Patient Report and Safety Plan · Career and Integrity Reflection | Week 2: First Responders — Evidence, Response, and Handoff | PRACTICE: Clinton Lake Counterevidence Exchange ; MAJOR 2: Patient Care Report and Complication Plan | student pages omit S&S pp. 48-49,52-58; NO workbook page on any student page |
| 2SW wk3 | Nursing / Health Science | 59-61,64-68,84-86 | 2SW Wk3: Nursing Science - Routes, Simulation, and Handoff (unpub) | Compare Nursing Routes · Choose with Evidence · Build a Training Simulator · Write a Careful Handoff · Build a Nursing Career Evidence Map | Week 3: Nursing Science - Routes, Simulation, and Handoff | PRACTICE: Nursing Assistant and LVN Model Check ; PRACTICE: Nursing Route Evidence Check ; PRACTICE: Vital Signs and Handoff Check ; MINOR 1: Nursing Route and Handoff | student pages omit S&S pp. 59-61,64-68,84-86; NO workbook page on any student page |
| 2SW wk4 | Dental Science / Health Data / Health Science | 69-73,84-85 | 2SW Wk4: Smile Squad - Dental Science and Health Data (unpub) | Read Dental Evidence Carefully · Design a Toothbrush with Evidence · Connect School Subjects to Work · Try a Medical-Coding Evidence Lab · Recommend a Health Career with Evidence | Week 4: Dental Science and Health Data | PRACTICE: College Credit Opportunity Check ; PRACTICE: ICD-10-CM Evidence Check ; MINOR 2: Health Career Evidence Check | ok |
| 2SW wk5 | PowerSkills: Communication / Cross-cluster skills focus | 12-14,62-63,134-135,139,144-145,147-148 | 2SW Wk5: Communication and Goal Setting (unpub) | Conflict Resolution · Active Listening · Advocacy and SMART Time Plan · Written Message Lab · Communication Skills and Goal Synthesis | Week 5: Communication and Goal Setting | PRACTICE: Active Listening Evidence Check ; PRACTICE: Little Library Message Lab ; MINOR 3: Communication and Goal Synthesis | student pages omit S&S pp. 12-14,134-135,139 |
| 2SW wk6 | Biomedical / Health Science | 74-83 | 2SW Wk6: Science Meets Medicine (unpub) | Biomedical Careers and Cover Letter · Mini Medics Design · Outbreak Evidence · Outbreak Response · Biomedical Career Evidence Reflection | Week 6: Science Meets Medicine | PRACTICE: Outbreak Evidence Check ; PRACTICE: Biomedical Career Evidence Reflection | student pages omit S&S pp. 82-83 |
| 3SW wk1 | Vet Science / Agriculture, Food & Natural Resources | 87,96-102 | 3SW Wk1: Veterinary Science (unpub) | Meet the Veterinary Team · Compare Veterinary Career Paths · Veterinary Triage · Transferable Skills · Veterinary Pathway Recommendation | 3SW Week 1: Veterinary Science | PRACTICE: Veterinary Triage Evidence Check ; PRACTICE: Transferable Skills Reflection ; MINOR 1: Veterinary Pathway Evidence Packet | student pages omit S&S pp. 87,102 |
| 3SW wk2 | Plant Science / Agriculture, Food & Natural Resources | 88-92 | 3SW Wk2: Plant Science and Agricultural Communication (unpub) | Diagnose a Grow System · Plan a Farm-to-Table Infographic · Build and Test the Infographic · Evaluate Emerging Plant-Tech Work · Plant-Tech Evidence and Fair Career Investigation | Week 2: Plant Science and Agricultural Communication | PRACTICE: Plant Career Connection ; FORMATIVE: Communication Skill Transfer ; PRACTICE: Emerging Plant-Tech Evidence Check ; MAJOR 1: Farm-to-Table and Emerging Plant-Tech Evidence ; PRACTICE: Plant-Career Evidence Reflection | ok |
| 3SW wk3 | Sustainable Engineering / Agriculture, Food & Natural Resources | 93-95,146 | 3SW Wk3: Sustainable Engineering and Pest Patrol (unpub) | Careers and Resource Problems · Field Reports and Constraints · Pest Patrol Drone Design · Review, Revision, and Trends · Xello Interests | Week 3: Sustainable Engineering and Pest Patrol | PRACTICE: Sustainable Career Match ; PRACTICE: Pest Patrol Drone Draft ; MAJOR 2: Sustainable Engineering Design and Trends Evidence ; PRACTICE: Xello Interests Reflection | student pages omit S&S pp. 93-94,146 |
| 3SW wk4 | Culinary Arts / Hospitality / Hospitality & Tourism | 111-113,117-125 | 3SW Wk4: Culinary Arts and Hospitality (unpub) | Culinary Twist Menu Design · Motivation and Career Comparison · Hotel Rescue · Cater and Create · Hospitality Recommendation | Week 4: Culinary Arts and Hospitality | PRACTICE: Culinary Twist Menu Design ; PRACTICE: Motivation Check ; MINOR 2: Hospitality Career and Business Recommendation | student pages omit S&S pp. 111,121,123-125 |
| 3SW wk5 | Cosmetology / Human Services | 127-133,136-138 | 3SW Wk5: Style, Service, and Cosmetology Careers (unpub) | Human Services and SFX Concept · Build and Test the Texture Model · Quality and Texas Pathways · Salon and Wellness Campaign · Career and Business Recommendation | Week 5: Style, Service, and Cosmetology Careers | PRACTICE: Texas Cosmetology License and Safety Check ; MINOR 3: Cosmetology Career and Business Recommendation | student pages omit S&S pp. 130,136-138 |
| 3SW wk6 | Entrepreneurship / Business Management & Administration | 221,234-237,252-254 | 3SW Wk6: Build, Test, and Pitch a Business Idea (unpub) | Entrepreneurship Opportunities · Problem and Idea Sprint · Stress-Test and Decide · Venture Brief and Pitch · Build and Revise a Personal Budget | Week 6: Build, Test, and Pitch a Business Idea | PRACTICE: Entrepreneurship Evidence Check ; RECOVERY: Entrepreneurship Portfolio | student pages omit S&S pp. 221,252-253 |
| 4SW wk1 | Career Planning: Mid-Year Review / Cross-Cluster (Planning Tools) | 6-8,22,281-286 | 4SW Wk1: Build Your Mid-Year Career Blueprint (unpub) | Profile Audit · Career Iceberg · Xello Save Quick Sims · Pathway and CTSO Decision · Mid-Year Career Blueprint | Week 1: Build Your Mid-Year Career Blueprint | PRACTICE: Career Iceberg Annotation ; PRACTICE: Pathway and CTSO Decision ; MAJOR 1: Mid-Year Career Blueprint | student pages omit S&S pp. 22,281-282,285-286 |
| 4SW wk2 | Career Planning: Course Mapping / Cross-Cluster (Planning Tools) | 292-296 | 4SW Wk2: Build a Counseling-Ready High School Plan (unpub) | Graduation and Assessment Decisions · Four-Year Course Plan Draft · Postsecondary Route Trail and College Credit · SMART Experience Action Plan · Individual High School and Career Plan | Week 2: Mapping My Future - High School Course Planning | PRACTICE: What Does This Assessment Affect? ; DRAFT: Four-Year Course Plan Annotation ; MAJOR 2: Individual High School and Career Plan | student pages omit S&S pp. 294-296 |
| 4SW wk3 | Aviation / Air Traffic / Transportation, Distribution & Logistics | 149,160-170 | 4SW Wk3: Aviation Routes, Systems, and Action Planning (unpub) | Transportation Cluster and Survey Design · Aviation Careers and Pilot Routes · Design a Classroom Airport Map · Test, Communicate, and Revise · Aviation Route and Action Plan | Week 3: Cleared for Takeoff - Aviation Routes and Airport Operations | PRACTICE: Is This Survey Useful? ; PRACTICE: Airport Design and Simulation Lab ; MINOR 1: Aviation Route and Action Plan | student pages omit S&S pp. 149,160-165,168-170 |
| 4SW wk4 | Drone Engineering / Engineering / Transportation | 103-105,108-110 | 4SW Wk4: Drone Systems, Rules, and Iteration (unpub) | Wildlife-Tracking System Design · Drone-Enabled Occupations · Drone Rules and Readiness · Systems Test and Iteration · Drone Systems Evidence Brief | Week 4: Drone Engineering: Design, Evidence, and Responsible Testing | PRACTICE: Wildlife-Tracking Drone Design ; PRACTICE: Label the Career Evidence ; PRACTICE: Indoor, Outdoor, or Part 107? ; PRACTICE: Drone Systems Test and Iteration ; MINOR 2: Drone Systems Evidence Brief | student pages omit S&S pp. 103,108-110 |
| 4SW wk5 | Automotive Evidence and Training Routes / Transportation, Distribution & Logistics | 150-152,168-169 | 4SW Wk5: Automotive Evidence and Training Routes (unpub) | Crash Crew Visible Evidence · ASE and Training Routes · Three Automotive Occupations · Automotive Route Decision · Automotive Evidence Brief | Week 5: Automotive Evidence and Training Routes | PRACTICE: Crash Crew Evidence and Preliminary Plan ; PRACTICE: ASE and Training Route Check ; PRACTICE: Compare Three Automotive Occupations ; PRACTICE: What Does This Source Prove? ; MINOR 3: Automotive Evidence Brief | ok |
| 4SW wk6 | Skills That Transfer / Mid-Year Evidence / Cross-cluster synthesis | 153-155 | 4SW Wk6: Skills That Transfer and Mid-Year Evidence (unpub) | What the Clues Support · Prove a Skill Transfers · Career Organization Types · Integrity and Accurate Records · Recovery: Private Mid-Year Reflection | Week 6: Skills That Transfer: Evidence, Organizations, and Mid-Year Reflection | PRACTICE: Truck Evidence and Priority ; PRACTICE: Transferable Skills Evidence ; PRACTICE: Career Organization Type Check ; PRACTICE: Integrity and Accurate Records ; RECOVERY: Private Mid-Year Evidence Reflection | ok |
| 5SW wk1 | Architecture / Architecture & Construction | 171-173,182-184 | 5SW Wk1: Blueprint Builders — Architecture Evidence (unpub) | Cluster Roles and Safety Supervisor · Career Preparation and Pay · Concept Modeling Foundations · Build, Test, Revise, and Submit · Unexpected Architecture and Synthesis | Week 1: Blueprint Builders — Architecture Careers | PRACTICE: Safety Supervisor Evidence Plan ; MINOR 1: Three-Career Architecture Comparison ; PRACTICE: Architecture Career Evidence Check ; PRACTICE: Community Learning Space Concept ; PRACTICE: Building Test and Revision ; FORMATIVE: Architecture Evidence Portfolio | ok |
| 5SW wk2 | Civil Engineering / Architecture & Construction / STEM | 103,106-107,174-175 | 5SW Wk2: Civil Engineering — Systems, Evidence, and Design (unpub) | Civil Engineering Careers and Systems · Assessment Impact and Emerging Work · Bridge Design — Two Options · Fixed-Data Test and Redesign · Mars Transfer and Weekly Synthesis | Week 2: Building Strong — Civil Engineering Evidence | PRACTICE: Civil Engineering and Systems Evidence ; MINOR 2: Assessment and Emerging-Specialty Evidence ; PRACTICE: Assessment and Emerging Work Evidence Check ; PRACTICE: Bridge Design Evidence ; PRACTICE: Bridge Test and Redesign Evidence ; FORMATIVE: Civil Engineering Evidence Portfolio | student pages omit S&S pp. 174 |
| 5SW wk3 | Construction Evidence / Architecture & Construction | 176-179 | 5SW Wk3: Construction — Routes, Evidence, and Observation (unpub) | Construction Careers and Preparation · Training Routes and Career Organizations · Classify Four Construction Careers · Fictional Visual Observation Lab · Evidence Report and Individual Briefing | Week 3: Built to Last — Construction Evidence | PRACTICE: Construction Career Evidence ; PRACTICE: Construction Routes and Organizations ; MINOR 3: Construction Labor-Evidence Classification ; FORMATIVE: Construction Evidence Report and Briefing | student pages omit S&S pp. 179 |
| 5SW wk4 | Skilled-Trades Evidence: HVAC / Electrical / Plumbing / Welding / Architecture & Construction | 185-190,194-195 | 5SW Wk4: Skilled Trades — Evidence, Routes, and Communication (unpub) | Four Skilled-Trades Careers · HVAC Evidence-First Field Notes · Classify Four Skilled-Trades Careers · Current Entry Routes · Fictional Water-Line Response | Week 4: Power, Water, and Heat: Skilled-Trades Evidence | PRACTICE: Skilled-Trades Career Evidence ; PRACTICE: HVAC Evidence-First Field Notes ; MAJOR 1 EVIDENCE: Part A — Skilled-Trades Labor Classification ; PRACTICE: Current Entry Routes ; MAJOR 1: Skilled-Trades Classification and Individual Response | ok |
| 5SW wk5 | MoneySkills: Personal Budget / Cross-cluster financial planning | 285-286 | 5SW Wk5: MoneySkills — Budget, Location, and Career Evidence (unpub) | Salary Source and Lifestyle Target · Build a Dallas County Personal Budget · Compare the Same Offer Across Locations · Paying for Education and Training · Personal Budget and Career Evidence Portfolio | Week 5: MoneySkills — Build a Budget That Explains Your Choices | PRACTICE: Salary Source and Lifestyle Target ; PRACTICE: Dallas County Personal Budget ; PRACTICE: Location Cost Comparison ; PRACTICE: Paying for Education and Training Check ; MAJOR 2: Personal Budget Evidence Portfolio | student pages omit S&S pp. 285-286; NO workbook page on any student page |
| 5SW wk6 | Real Estate: Licensing, Variable Income, and Evidence / Business, Marketing & Finance | 238-239 | 5SW Wk6: Real Estate: Licensing, Variable Income, and Evidence (unpub) | Four Real-Estate Careers and Boundaries · TREC Route and Variable-Income Math · Flip This House: ROI and Entrepreneurship · Real-Estate Labor Evidence · Private Evidence Brief and Reflection | Week 6: Real Estate: Licensing, Variable Income, and Evidence | PRACTICE: Real-Estate Career Boundaries ; PRACTICE: TREC Route and Variable-Income Math ; PRACTICE: Flip This House Evidence Plan ; PRACTICE: Real-Estate Labor Evidence Check ; FORMATIVE: Fifth Six Weeks Evidence Brief | student pages omit S&S pp. 238-239; NO workbook page on any student page |
| 6SW wk1 | Education / Education & Training | 213-220 | 6SW Wk1: Education — Learning Design, Routes, and Service (unpub) | Community Classroom · Texas Education Career Routes · Xello Discover Learning Pathways · Teach Through Play and Service · Education Evidence Portfolio | Week 1: Teaching Tomorrow — Education & Training | PRACTICE: Community Classroom Learning-Space Plan ; PRACTICE: Texas Education Career Routes ; PRACTICE: Teach Through Play and Service ; MINOR 1: Education Evidence Portfolio | student pages omit S&S pp. 220 |
| 6SW wk2 | Graphic Design / Digital Communication / Arts, A/V Technology & Communications | 255-258,270-273 | 6SW Wk2: Arts/AV — First Resume and Design Evidence (unpub) | Behind the Microphone · Write a First Resume · Complete Xello Resume and Revise · Seven Steps of an Effective Job Search · Merch Mode and Final Resume Evidence | Week 2: Design Your Brand - Arts/AV + First Resume | PRACTICE: Podcast Production Evidence ; PRACTICE: First Resume Draft ; PRACTICE: Seven-Step Job Search ; MINOR 2: Resume, Revision, and Job-Search Evidence | student pages omit S&S pp. 270-273 |
| 6SW wk3 | Marketing: Audience, Entrepreneurship, and Data / Marketing | 147-148,222-227,229 | 6SW Wk3: Marketing - Audience, Entrepreneurship, and Data (unpub) | Click Factor · Written Communication and Changing Conditions · Expert Edge · Family Fun Pass · Ethical Marketing Evidence Brief | Week 3: Marketing - Audience, Entrepreneurship, and Data | PRACTICE: Click Factor Audience Test and Revision ; PRACTICE: Written Communication and Changing Conditions ; PRACTICE QUIZ: Marketing Evidence and Boundaries ; PRACTICE: Expert Edge Opportunity and Revision ; PRACTICE: Family Fun Pass Evidence Decision ; MINOR 3: Ethical Marketing Evidence Brief | ok |
| 6SW wk4 | Sales and Career Oral Evidence / Marketing / Business Management | 241-247,280,299 | 6SW Wk4: Sales and Career Oral Evidence (unpub) | Audience and Sales Pitch Plan · Deliver, Test, and Revise · BrainBoost Decision and Career Outline · Interview Appearance and Rehearsal · Career Oral Evidence Brief | Week 4: Sales and Career Oral Evidence | PRACTICE: Audience and Sales Pitch Plan ; PRACTICE: Oral Pitch Delivery and Revision ; PRACTICE: BrainBoost Decision and Career Outline ; PRACTICE: Interview Appearance and Rehearsal Record ; FORMATIVE: Career Oral Evidence Brief | student pages omit S&S pp. 280,299 |
| 6SW wk5 | Job Search, Applications, and Interviews / Cross-Cluster Career Readiness | - | 6SW Wk5: Job Search, Applications, and Interviews (unpub) | Job Search and Posting Screen · Tailored Cover Letter · Sample Application and References · Interview Preparation · Mock Interview and Follow-Up | Week 5: Job Search, Applications, and Interviews | PRACTICE: Job Search and Posting Evidence ; PRACTICE: Tailored Cover Letter ; PRACTICE: Application and References ; PRACTICE: Interview Readiness Planner ; MAJOR 1: Job Skills, Application, and Mock Interview Portfolio | ok |
| 6SW wk6 | Career Evidence Capstone / Cross-Cluster Final Plan | 277-280 | 6SW Wk6: Career Evidence Capstone (unpub) | Evidence Audit and Recovery · Individual Career Plan · Career Evidence Brief and Rehearsal · Communicated Capstone and Revision · Reflection and Transfer Forward | Week 6: Career Evidence Capstone | CAPSTONE: Evidence Inventory and Recovery ; CAPSTONE: Individual Career Plan ; CAPSTONE: Presentation Plan and Rehearsal ; MAJOR 2: Individual Career Plan and Communicated Capstone ; CAPSTONE: Final Course Reflection | student pages omit S&S pp. 277-280; NO workbook page on any student page |
### Topic / ordering / assessment notes on the table

- **Topic alignment: no week is on the wrong cluster.** Canvas module names and docs `overview.md` titles are paraphrases of the S&S CCE Topic in all 37 rows. Day titles differ in wording from `day.md` headings on ~35 days (e.g. 1SW Wk2 D1 `docs` "IT Cluster Tour — Four Irving Programs of Study" vs Canvas "Map the IT Cluster"); these are cosmetic, not topical.
- **Three weeks teach workbook activities in reverse of the S&S / workbook order:**
  - 1SW Wk1: Day 3 = Super Sports Manufacturing (pp. 204-206), Day 4 = Robots for Crayons (pp. 200-203). S&S lists Robots for Crayons first.
  - 2SW Wk1: Day 2 = Emergency Essentials Kit (pp. 50-51), Days 3-4 = City Council (40-43) / Policy Showdown (44-47). S&S lists City Council → Policy Showdown → Kit Design.
  - 2SW Wk6: Day 2 = Mini Medics (pp. 79-81) before Days 3-4 = Outbreak Investigators (pp. 74-78). S&S lists Outbreak first (and D-3 awards Outbreak the flagship slot).
- **Assessment naming is internally consistent and does not conflict with S&S** — S&S has no assessment column, so there is nothing to contradict. Each six-weeks carries Minor 1-3 plus Major 1-2 plus PRACTICE/FORMATIVE/RECOVERY/CAPSTONE items; numbering is sequential within each six-weeks with no duplicates and no gaps. One naming oddity: 5SW Wk4 has both `MAJOR 1 EVIDENCE: Part A — Skilled-Trades Labor Classification` (Day 3) and `MAJOR 1: Skilled-Trades Classification and Individual Response` (Day 5) — two gradebook items sharing the "MAJOR 1" label.
- **Xello:** every week whose S&S Xello column names a required task has at least one student page that mentions Xello (1SW Wk1 Matchmaker, 1SW Wk2 Personality Style, 1SW Wk3 Learning Style, 1SW Wk4 Add Skills, 2SW Wk1 Life Experiences, 2SW Wk4 Education Experiences, 3SW Wk3 Interests, 4SW Wk1 Save Quick Sims, 6SW Wk1 Discover Learning Pathways, 6SW Wk2 Resume). No required Xello task is missing from student-facing content. 13 weeks whose S&S column says "None required / supplemental" still mention Xello on a student page; the language there is catch-up/optional, so this is low severity but worth a pass.

## 2. FYF page grounding per day

### 2a. Coverage of the check

All 180 days were machine-checked, not sampled: every `FYF p./pp.`, `Find Your Future p.`, and `workbook p.` reference in all 180 `day.md` files and all 181 module-linked STUDENT Canvas pages was extracted and resolved against the FYF text extract at PDF page = printed + 6. That exceeds the requested "all of 1SW plus 2 days per week." Results are in `fyf-citation-check.csv`:

| result | rows | meaning |
|---|---|---|
| yes | 369 | cited printed page exists and its content matches the week's cluster/activity |
| partial | 13 | multi-page activity; named section title sits on the first page of the cited range |
| n/a | 33 | student page cites no workbook page while `day.md` does |

**No row came back "no."** There is no wrong page number and no named section that does not exist in the book.

### 2b. Days where `day.md` cites FYF and the STUDENT page cites nothing (33)

1sw-wk0-day4, 1sw-wk1-day1, 1sw-wk2-day2, 1sw-wk3-day1, 1sw-wk4-day1, 1sw-wk4-day2,
1sw-wk5-day1, 1sw-wk5-day2, 1sw-wk5-day3, 2sw-wk1-day1, 2sw-wk1-day2, 2sw-wk1-day3,
2sw-wk1-day4, 2sw-wk1-day5, 2sw-wk2-day1, 2sw-wk2-day2, 2sw-wk2-day3, 2sw-wk2-day4,
2sw-wk2-day5, 2sw-wk3-day1, 2sw-wk3-day3, 2sw-wk3-day4, 2sw-wk5-day3, 2sw-wk6-day5,
3sw-wk1-day1, 3sw-wk3-day2, 3sw-wk3-day3, 3sw-wk3-day5, 3sw-wk6-day4, 4sw-wk2-day2,
4sw-wk3-day2, 5sw-wk5-day1, 5sw-wk6-day3

Entire weeks with **zero** workbook page reaching students: **2SW Wk1 (S&S pp. 39-58), 2SW Wk2 (pp. 48-58), 2SW Wk3 (pp. 59-86), 5SW Wk5 (pp. 285-286), 5SW Wk6 (pp. 238-239)**, and 1SW Wk4 (pp. 36-38).

### 2c. Days where `day.md` and the student page disagree on which pages to open (17)

| day_key | day.md | student page | note |
|---|---|---|---|
| 1sw-wk1-day2 | 207,208,212 | 207,208 | App Exploration p. 212 not surfaced |
| 1sw-wk1-day4 | 200-203 | 200-202 | p. 203 (Step 5: Create a Plan) missing from student page |
| 1sw-wk2-day1 | 23,36,38 | 23 | district pp. 36-37 and App Exploration p. 38 not surfaced |
| 1sw-wk2-day3 | 26,27 | 26 | p. 27 (Step 2: Flip the Failure) missing, though the student task *is* "flip the failure" |
| 1sw-wk3-day3 | 30-33,280 | 30-33 | rubric p. 280 teacher-only, acceptable |
| 2sw-wk5-day1 | 12-14,144,145 | 144,145 | Powerskills reference chart pp. 12-14 not surfaced |
| 2sw-wk6-day3 | 74-77 | 74-76 | p. 77 handed to Day 4 |
| 3sw-wk4-day1 | 111-116 | 112,113 | day.md pulls in Restaurant Rebrand pp. 114-116, which S&S calls an optional extension |
| 3sw-wk4-day2 | 121-123 | 122 | Powerskill: Motivation opener p. 121 and p. 123 not surfaced |
| **3sw-wk5-day2** | **130** | **129** | **student page sends students to p. 129 (Day 1 Concept Card); day.md and the workbook's own "DAY 2" header are on p. 130** |
| 3sw-wk5-day4 | 127,132,133 | 132,133 | cluster opener p. 127 not surfaced |
| 3sw-wk6-day1 | 221,252,253,254 | 254 | students get only App Exploration p. 254, which S&S marks *optional*; the required opener p. 221 and district pp. 252-253 are not surfaced |
| 4sw-wk2-day4 | 292-296 | 292,293 | Rung 7 pp. 294-296 not surfaced |
| 4sw-wk3-day1 | 149,166,167 | 166,167 | cluster opener p. 149 not surfaced |
| 4sw-wk4-day1 | 103,104,105 | 104,105 | Engineering opener p. 103 not surfaced |
| 4sw-wk5-day1 | 149,150,151 | 150,151,152 | student page adds p. 152 (Step 4: Repair Plan); day.md stops at 151 |
| 6sw-wk3-day3 | 224 | 222,223,224 | day.md under-cites Expert Edge; student page is correct per D-7 |

### 2d. Days where only the student page cites a workbook page (5, module-linked)

3sw-wk2-day3 (p. 92), 6sw-wk3-day1 (pp. 225-227), 6sw-wk3-day2 (pp. 147-148), 6sw-wk3-day4 (p. 229), 6sw-wk4-day2 (pp. 241-243). In each case `day.md` for that day has no FYF reference at all — 6SW Wk3 in particular has student pages fully grounded (147-148, 222-227, 229) while its `day.md` files cite only p. 224.

### 2e. S&S-assigned pages that never reach students (by week)

| week | assigned by S&S but absent from all 5 student pages |
|---|---|
| 1SW Wk0 | 4, 22 |
| 1SW Wk1 | 199, 203, 209, 210, 211, 212 |
| 1SW Wk2 | 27, 36, 37, 38 |
| 1SW Wk3 | 38 |
| 1SW Wk4 | 36, 37, 38 (week has no workbook page at all) |
| 1SW Wk5 | 24, 25, 34, 35 |
| 2SW Wk1 | 39-47, 50, 51, 56, 57, 58 (all) |
| 2SW Wk2 | 48, 49, 52-58 (all) |
| 2SW Wk3 | 59, 60, 61, 64-68, 84, 85, 86 (all) |
| 2SW Wk5 | 12, 13, 14, 134, 135, 139 |
| 2SW Wk6 | 82, 83 |
| 3SW Wk1 | 87, 102 |
| 3SW Wk3 | 93, 94, 146 |
| 3SW Wk4 | 111, 121, 123, 124, 125 |
| 3SW Wk5 | 130, 136, 137, 138 |
| 3SW Wk6 | 221, 252, 253 |
| 4SW Wk1 | 22, 281, 282 |
| 4SW Wk2 | 294, 295, 296 |
| 4SW Wk3 | 149, 160-165, 168, 169, 170 |
| 4SW Wk4 | 103, 108, 109, 110 |
| 5SW Wk2 | 174 (students open p. 175 "Step 2" with no opener) |
| 5SW Wk3 | 179 |
| 5SW Wk5 | 285, 286 (all) |
| 5SW Wk6 | 238, 239 (all — the "required workbook spine" per S&S) |
| 6SW Wk1 | 220 |
| 6SW Wk2 | 270, 271 |
| 6SW Wk4 | 280, 299 (teacher references per S&S, acceptable) |
| 6SW Wk6 | 277, 278, 279, 280 (S&S calls these "locked Canvas orientation") |

Clean weeks (student pages cover every S&S-assigned page): 2SW Wk4, 3SW Wk2, 4SW Wk5, 4SW Wk6, 5SW Wk1, 5SW Wk4, 6SW Wk3.

### 2f. S&S page-range typos noticed while parsing

- 3SW Wk6 (6SW Wk3 row in the realignment plan) S&S text reads "Data-Informed Decision Making pp. 229 and 228" — the transposition flagged in `fyf-realignment-plan.md` row 33 is still in the S&S file. p. 228 reaches neither `day.md` nor any student page.
- 6SW Wk3 S&S reads "Click Factor pp. 225-227 and 230"; p. 230 is cited nowhere in the course.

## 3. Owner's specific questions

### 3a. What FYF p. 38 actually contains

Verified directly (PDF page 44). **p. 38 is the Information Technology chapter's "App Exploration" page.** Its literal student instructions are:

1. Open the Hats & Ladders app. **Go to Clusters. Click on the Information Technology Cluster.**
2. Watch the **"Cluster Tour"** video.
3. Click **"Game Time"** and play the game; write one thing you learned.
4. Find **1 Hat** that matches your personality or interests; say why.
5. Find **1 Hat** that feels like **NOT** a fit; say why.
6. Click **"Pathway Possibilities"** and answer the questions, then explore and **rate at least 1 pathway**.
7. **Rate at least 3 Hats.**
8. Jot down thoughts on the cluster (emojis/pictures/words).

**Does 1SW Wk2 Day 2's student page match it? No.** `docs/1sw/wk2-programming-it/day2.md` carries the citation `(FYF p. 38: "App Exploration")` on Activity 1, but the activity it introduces is: "navigate to the Programming and Software Development pathway in the H&L app … use the **Hat Finder** to browse **four** Hats and locate job tasks." The Canvas student page `student-1sw-wk2-day-2-compare-programming-careers` repeats that: "Open H&L > Information Technology > Programming and Software Development > Hat Finder. … make four short rows."

Mismatches against the actual p. 38:
- p. 38 routes through **Clusters → Information Technology**, not through a Programming and Software Development *pathway*.
- p. 38 never mentions **Hat Finder**.
- p. 38 asks for **1 fit Hat + 1 non-fit Hat + rate 3 Hats + rate 1 pathway**, not "browse four Hats and record a title and a task."
- p. 38's **Cluster Tour video**, **Game Time**, and **Pathway Possibilities** steps are absent from Day 2 entirely. They appear instead on **1SW Wk2 Day 1** ("Map the IT Cluster"), which is where the p. 38 routine is actually being taught.
- The Day 2 **student page cites no workbook page at all**, so students are never told to open p. 38; the citation exists only in the teacher-side `day.md`.

Net: the p. 38 citation on Wk2 Day 2 is a label attached to a CCE-original H&L browse, not an instruction set drawn from p. 38. The genuine p. 38 routine sits on Day 1 (uncited on the student page there too).

### 3b. Where BLS is actually taught to students

Student pages that teach or require BLS evidence (median pay, entry education, job outlook, or a bls.gov link):

| day key | page | what it does |
|---|---|---|
| **1sw-wk2-day3** | Resilience and Salary Showdown | **First and only explicit BLS *lesson*.** Teaches the four extraction fields: BLS occupation title, national median + data year, typical entry education, job outlook % + projection years; teaches keeping national vs. local figures in separate labeled sections; links a "BLS guide" file |
| 1sw-wk2-day2 | Compare Programming Careers | BLS named only as "keep BLS closed / leave the Day 3 BLS section blank" |
| 1sw-wk3-day4 | Research an Emerging IT Career | reuses the Day 3 BLS fields on an emerging occupation |
| 1sw-wk3-day5 | Learning Style Quiz and Lesson | brief BLS reference |
| 1sw-wk4-day2 | Compare Education Routes | median pay / entry education by route |
| 1sw-wk5-day1 | Cybersecurity Career Routes | BLS evidence for cyber occupations |
| 2sw-wk1-day1 | Explore Legal Careers | BLS + median pay |
| 2sw-wk2-day1 | First Responder Routes | BLS + median pay (3 refs) |
| 2sw-wk3-day1 | Compare Nursing Routes | BLS + median |
| 2sw-wk3-day2 | Choose with Evidence | median pay (4 refs) |
| 3sw-wk1-day2 | Compare Veterinary Career Paths | median pay |
| 3sw-wk2-day4 | Evaluate Emerging Plant-Tech Work | BLS |
| 3sw-wk3-day1 | Careers and Resource Problems | median pay |
| 4sw-wk1-day3 | Xello Save Quick Sims | (BLS + bls.gov link is on the ORPHAN page `student-4sw-wk1-day-3-career-deep-dive`, not the module page) |
| 4sw-wk2-day3 | Postsecondary Route Trail and College Credit | BLS (4 refs) |
| 4sw-wk3-day2 | Aviation Careers and Pilot Routes | median pay |
| 4sw-wk5-day3 | Three Automotive Occupations | BLS + median |
| 4sw-wk5-day5 | Automotive Evidence Brief | median pay |
| 5sw-wk1-day2 | Career Preparation and Pay | BLS + median (3 refs) |
| 5sw-wk5-day1 | Salary Source and Lifestyle Target | BLS (2 refs) |
| 5sw-wk5-day5 | Personal Budget and Career Evidence Portfolio | BLS |
| 5sw-wk6-day1 | Four Real-Estate Careers and Boundaries | BLS |
| 5sw-wk6-day4 | Real-Estate Labor Evidence | BLS (3 refs) |
| 6sw-wk3-day2 | Written Communication and Changing Conditions | BLS (2 refs) |
| 6sw-wk4-day3 | BrainBoost Decision and Career Outline | BLS |

**Answer: yes, 1SW Wk2 Day 3 is the first explicit BLS lesson, and it is the only day that *teaches* BLS** (what the fields are, how to label them, how not to mix national and local figures). Every later day *applies* BLS as an already-known evidence source and never re-teaches it. One caveat: **no module-linked student page links `bls.gov` directly.** Only two pages in the whole course contain a bls.gov URL, and both are orphans not attached to any module (`student-1sw-wk0-day-5-catch-up-or-research-careers`, `student-4sw-wk1-day-3-career-deep-dive`). 1SW Wk2 Day 3 routes students to an uploaded "BLS guide" Canvas file instead.

## 4. H&L activity grounding

Named H&L activities found on student pages, and whether `day.md`/S&S agree:

| day key | student page names | `day.md` `[H&L PLATFORM]` marker | verdict |
|---|---|---|---|
| 1sw-wk0-day1 | Discover Your Core | none | student page assigns H&L work with no `[H&L PLATFORM]` marker in `day.md` |
| 1sw-wk0-day2 | Discover Your Core | Discover Your Core (2 markers) | agrees |
| 1sw-wk0-day3 | Building Blocks, Work Values | none | no marker |
| 1sw-wk0-day4 | Building Blocks, Career Journey, Work Values | none | no marker |
| 1sw-wk0-day5 | Career Journey, **Hat Finder**, Work Values | none | **student page adds Hat Finder, which neither `day.md` nor S&S assigns** |
| 1sw-wk1-day1 | Cluster Tour, Game Time, Pathway Possibilities | same 3 | agrees (this is the p. 212 App Exploration routine, though p. 212 is not cited to students) |
| 1sw-wk1-day2 | — | Hat Finder | `day.md` assigns Hat Finder; student page does not |
| 1sw-wk2-day1 | Cluster Tour, Game Time, Pathway Possibilities | same 3 | agrees; this is the p. 38 routine (see 3a) |
| 1sw-wk2-day2 | Hat Finder | Hat Finder | agree with each other, **but neither matches the cited p. 38** (see 3a) |
| 1sw-wk5-day5 | Career Journey | none | no marker |
| 4sw-wk1-day5, 4sw-wk2-day5, 4sw-wk6-day4, 6sw-wk6-day2, 6sw-wk6-day4 | H&L "Career Plan" | none | S&S lists Career Plan as *optional evidence/export*; no `[H&L PLATFORM]` marker anywhere |

Structural findings:

- The **entire course contains 6 `[H&L PLATFORM]` markers**, in 5 files, all in 1SW: `1sw/wk0-.../day2.md`, `1sw/wk1-.../day1.md`, `1sw/wk1-.../day2.md`, `1sw/wk2-.../day1.md`, `1sw/wk2-.../day2.md`. 2SW-6SW have **zero**.
- Only **9 student pages** mention Hats & Ladders at all, all in 1SW Wk0-Wk2.
- S&S explicitly assigns H&L app work that never appears on any student page, including: 2SW Wk1 ("Law and Public Safety cluster tour; Explore Hats: Lawyer, Paralegal, Judge, Court Reporter; Favorite 2 Law Hats"), 2SW Wk2 ("Explore Hats: Police Officer, EMT, Firefighter, Detective; Favorite Law Hats"), 2SW Wk3 ("optional Health Science cluster and Hat exploration"), 1SW Wk1 ("H&L Manufacturing cluster exploration"), 1SW Wk3-Wk5 ("H&L IT exploration", "H&L supplemental").
- **Decision D-8 shortfall** — App Exploration pages present in FYF: 38, 58, 86, 102, 110, 126, 138, 170, 198, 212, 220, 254, 276. Cited in `day.md`: 38, 58, 212, 254. Reaching students: **38, 254 only**. District pages present: 21, 36, 56, 84, 100, 108, 124, 136, 168, 196, 210, 218, 252, 274. Cited in `day.md`: 21, 36, 56, 84, 100, 168, 210, 218, 252. Reaching students: 21, 36, 84, 100, 168, 218.
- No day flagged for the reverse case (student page inventing an H&L activity the curriculum forbids), except 1sw-wk0-day5's Hat Finder.

## 5. Published-state sanity

**24 module items are published**, in exactly 3 modules: 1SW Wk0 (all 16 items), 1SW Wk1 (2 items), 1SW Wk2 (6 items). All other 34 modules are fully unpublished, which matches the CLAUDE.md "unpublished is the intended handoff state" rule.

| module | published items |
|---|---|
| 1SW Wk0 | 5 SubHeaders, 5 TEACHER guides, 5 STUDENT pages, MINOR 1 assignment — complete week |
| 1SW Wk1 | STUDENT Day 1, STUDENT Day 2 only |
| 1SW Wk2 | SubHeaders Day 1-3, STUDENT Day 1, Day 2, Day 3 |

File-link check on every published STUDENT and TEACHER page: **all clean.** 41 distinct `/files/<id>/` references across the 24 published items; every id exists in `files.json`; none has `locked`, `hidden`, `locked_for_user`, `hidden_for_user`, `unlock_at`, or `lock_at` set. Internal `/pages/` and `/assignments/` links from published pages all resolve to published targets — no broken link, no published page pointing at an unpublished page or assignment.

Two publication-consistency issues, neither a locked-file failure:

1. **1SW Wk1 and 1SW Wk2 publish STUDENT pages without their TEACHER Facilitator Guides.** 1SW Wk1 Days 1-2 and 1SW Wk2 Days 1-3 are live to students; every matching `TEACHER: … Facilitator Guide` is unpublished. 1SW Wk1 also publishes Days 1-2 but not Days 3-5, and 1SW Wk2 publishes Days 1-3 but not Days 4-5 — partial weeks.
2. **One published orphan page.** `student-1sw-wk0-day-5-xello-and-career-perks-and-quirks` is `published=True` but belongs to **no module**, so it is reachable by direct URL / Pages index while not being part of the course flow.

### Orphan student pages (23 of 204 student pages are not in any module)

Unpublished unless noted. These are competing/superseded versions of module days and are the likely cause of several "student page cites no workbook page" findings, because the grounded content lives on the orphan:

`student-1sw-wk0-day-1-welcome-to-the-cce-lab`, `student-1sw-wk0-day-5-catch-up-or-research-careers` (has the only Wk0 bls.gov link), **`student-1sw-wk0-day-5-xello-and-career-perks-and-quirks` (PUBLISHED)**, `student-1sw-wk3-day-5-learning-style-and-it-connection`, `student-2sw-wk3-day-5-save-three-careers`, `student-3sw-wk1-day-4-xello-skills`, `student-3sw-wk3-day-5-xello-set-goals`, **`student-4sw-wk1-day-3-career-deep-dive` (holds FYF Rungs 2-3 pp. 283-286 and a bls.gov link; the module page `…-xello-save-quick-sims` cites no workbook page)**, `student-4sw-wk2-day-3-college-credit-and-plan-conversation`, `student-4sw-wk6-day-5-private-mid-year-reflection`, `student-5sw-wk2-day-4-controlled-test-or-equal-data-analysis`, `student-5sw-wk5-day-3-compare-the-same-household-across-locations`, `student-6sw-wk1-day-3-read-education-job-evidence`, **`student-6sw-wk2-day-3-attention-to-detail-and-resume-revision` (holds FYF pp. 272-273, which S&S assigns to 6SW Wk2; the module page cites no workbook page)**, `student-6sw-wk3-day-4-family-fun-pass-data-analysis`, `student-6sw-wk4-day-3-brainboost-rescue-and-career-outline`, `student-6sw-wk5-day-1-job-search-and-posting-evidence`, `student-6sw-wk5-day-3-application-and-references`, `student-6sw-wk5-day-4-interview-readiness`, `student-6sw-wk6-day-1-evidence-inventory-and-recovery`, `student-6sw-wk6-day-3-presentation-plan-and-rehearsal`, `student-6sw-wk6-day-4-communicated-career-capstone`, `student-6sw-wk6-day-5-final-course-reflection`.

## 6. Top 10 concrete discrepancies

1. **1sw-wk2-day2** — cites `(FYF p. 38: "App Exploration")` for an activity p. 38 does not describe (Programming pathway + Hat Finder + four Hats vs. p. 38's Clusters → IT → Cluster Tour / Game Time / 1 fit Hat / 1 non-fit Hat / rate 3 Hats / Pathway Possibilities). Student page cites no workbook page at all.
2. **2sw-wk1-day1 … 2sw-wk3-day4 (13 consecutive days)** — S&S assigns FYF pp. 39-86 across 2SW Wk1-Wk3; **not one workbook page reaches a student page** in those three weeks, though `day.md` cites them correctly.
3. **3sw-wk5-day2** — student page sends students to FYF p. 129; the workbook's own "DAY 2" build page and the `day.md` citation are p. 130. Off-by-one against the workbook's own day labeling.
4. **3sw-wk6-day1** — the only workbook page on the student page is p. 254, which S&S marks *optional* App Exploration support. The required Business/Marketing opener p. 221 and district pp. 252-253 never reach students.
5. **5sw-wk6-day3** — S&S calls FYF pp. 238-239 (Flip This House) "the required workbook spine"; `day.md` cites it, and the student page cites no workbook page. Same for the whole of 5SW Wk6 and 5SW Wk5 (pp. 285-286).
6. **4sw-wk1-day3 / 6sw-wk2-day3** — the FYF-grounded version of the day lives on an orphan page outside the module (`…-career-deep-dive` with pp. 283-286 + bls.gov; `…-attention-to-detail-and-resume-revision` with pp. 272-273), while the module-linked page carries no workbook reference.
7. **H&L collapse** — 6 `[H&L PLATFORM]` markers in 180 day files, all in 1SW; 9 student pages mention H&L, all in 1SW Wk0-Wk2. S&S H&L assignments for 2SW Wk1, 2SW Wk2, 2SW Wk3, 1SW Wk1, 1SW Wk3-Wk5, 3SW, 4SW, 6SW reach no student page.
8. **D-8 App Exploration shortfall** — 13 App Exploration pages exist; 4 are cited in `day.md`; 2 reach students. 9 of the 13 (86, 102, 110, 126, 138, 170, 198, 220, 276) are cited nowhere in the course.
9. **Published student pages without published teacher guides** — 1SW Wk1 Days 1-2 and 1SW Wk2 Days 1-3 are live to students; all matching Facilitator Guides are unpublished, and both weeks are partially published (Wk1 stops at Day 2, Wk2 at Day 3).
10. **Published orphan** — `student-1sw-wk0-day-5-xello-and-career-perks-and-quirks` is published but in no module, one of two competing Wk0 Day 5 pages alongside the module's `…-career-perks-neutrals-and-quirks`.

Runners-up: 1sw-wk1-day3/day4 teach Super Sports (204-206) before Robots for Crayons (200-203), inverting S&S; 2sw-wk1-day2 teaches Emergency Kit (50-51) before City Council (40-43); 5sw-wk2-day1 opens students on p. 175 ("Step 2: Plan the Cabinets") with no p. 174 opener; 5SW Wk4 has two gradebook items labeled "MAJOR 1"; the S&S "pp. 229 and 228" transposition flagged in `fyf-realignment-plan.md` is still unfixed and p. 228 / p. 230 are cited nowhere.

## 7. What the audit did not check

- TEKS tag correctness (out of scope here; `teks-audit-process.md` owns it).
- Climber Notes slide citations, Xello task-level configuration in the live product, and eDynamic unit numbers.
- Teacher Facilitator Guide content against `day.md` (only student pages were compared for workbook grounding).
- Whether a cited page's *activity steps* were reproduced faithfully on the student page. That was done only for FYF p. 38 (section 3a), where the answer was no. The same check on the other 369 references may surface more p. 38-style label/instruction mismatches.
