# 4SW + 5SW Day-1 Readiness Findings

Scope: `docs/4sw/` (wk1-wk6) and `docs/5sw/` (wk1-wk6) — 12 weeks, 72 files, all read in full.
All paths below are relative to `/Users/elishalucero/Coding Projects/27 CCR Planning/.claude/worktrees/codebase-audit-school-year-398437/`.

**Verified before writing:** all 60 days in scope have an exit-ticket PDF in `docs/resources/exit-tickets/`. No worksheet, handout, template, poster, or slide file exists anywhere in the repo (`find` for `*worksheet*|*template*|*handout*|*organizer*` returns only the exit-ticket Jinja template and two authoring `.md` specs). `PATHWAYS.md` is in the repo root and is **not** in `mkdocs.yml` nav, so it is not on the website. `docs/resources/resources-status.md` already tracks the six Climber Notes deck dependencies in this scope and a partial worksheet backlog; findings that duplicate that page are marked **(tracked)**.

---

## Week 4SW-1 — wk1-career-planning

| Code | Day | Item | Evidence (file:line) | What's needed |
|---|---|---|---|---|
| MISSING-PRINTABLE | 1 | Core Types vs. Favorites worksheet **(tracked)** | `docs/4sw/wk1-career-planning/day1.md:12,70-74` | 4 columns fully specced in prose: A = Wk0 core type (Doer/Analyzer/Creator/Helper/Persuader/Organizer); B = favorite count per cluster, 8 named rows (Manufacturing, IT, Law & Public Service, Health Science, Agriculture, Hospitality, Human Services, Business); C = top 3 clusters ranked; D = match Yes/No/Sort of. Plus a one-sentence growth statement line. |
| MISSING-PRINTABLE | 2 | Blank iceberg template, 1/student | `overview.md:36`, `day2.md:12` | Title line, above-waterline section (≥3 items), below-waterline section (≥10 items). **Second variant** required by `day2.md:128`: underwater half pre-divided into 4 labeled zones — Skills, Tools, Training, Challenges. |
| MISSING-PRINTABLE | 3 | Real Game decision log, 1/student | `day3.md:12,34-44` | 8 rows (Career & Salary, Housing, Transportation, Food/Groceries, Phone/Internet, Entertainment, Savings, Insurance/Healthcare) × 4 columns (What I Chose, Monthly Cost, Running Budget Remaining). Support variant = categories pre-filled; reduced variant = 3 rows only. |
| MISSING-PRINTABLE | 4 | Pathway Ranking Sheet | `day4.md:12,54-58` | 3 rows × 5 columns (Rank, Irving ISD Pathway, Campus, 1-sentence rationale, Professional Organization). Also carries three eDynamic note lines (`day4.md:39-41`). Support variant = top-1 only. |
| MISSING-PRINTABLE | 5 | Mid-Year Update reflection template | `day5.md:12,46-52` | 5 numbered prompts, all specced. Pairs with the Wk0 sheet, stapled. ELL variant = Spanish sentence stems (`day5.md:123`). |
| MISSING-PRINTABLE | 5 | Printed cluster posters (10) for the dot-vote gallery walk | `day5.md:12,65-76` | Full content is written out at `day5.md:67-76` — 10 posters, one per cluster grouping, each listing pathways + campuses. Straight typesetting job, no research needed. |
| MISSING-SUPPLY | 5 | Colored sticker dots, 3 per student | `day5.md:12,78` | ~90 dots per section. Not classroom stock. |
| STRUCTURE | 1 | Irving ISD CTE Pathways poster "displayed in room" — no printable, no source on the site | `overview.md:37`, `day1.md` Materials, `day2.md:12,84-88`, `day4.md:12,57` | Named in Materials on 4 of 5 days and is the fallback source of truth when the H&L Career Plan tool is unavailable (`day2.md:55,76`). The data exists in root `PATHWAYS.md`, which is **not in mkdocs nav** — a site-reading teacher cannot see it. Needs either a printable poster asset or PATHWAYS.md added to the site. Recurs in 4SW Wk2 and every A&C week. |
| STRUCTURE | 1 | Climber Notes deck "Learning Your Core Personality Types" (slides 3-4) | `overview.md:32`, `day1.md:12,23` | Deck is a gitignored `.pptx` in `cce-curriculum/resources/climber-notes/`. Site-reading teacher cannot open it. Used as the 30-second type-table reprojection — degrades gracefully, but the plan names it as Materials. |
| MISSING-SETUP | 3 | Xello "Quick Sims: The Real Game" carries the whole 35-min block with **no offline fallback** | `day3.md:24-30` | `> [VERIFY IN Xello]` covers whether the Sim exists; it does not cover what the teacher runs if Xello logins fail on the day. Every other platform-dependent activity this week has a stated fallback (`day2.md:55,76`); this one does not. |
| MISSING-SETUP | 2 | Student drive folder "4SW Wk1 Career Plan" for screenshot saves | `day2.md:71` | Assumes a per-student Drive folder convention established earlier. No setup step named here or in the overview. |
| MISSING-PRINTABLE | 1-5 | Three named differentiation artifacts | `overview.md:103`, `day1.md:119`, `day5.md:121` | (a) "Simplified Career Plan navigation guide with screenshots" — requires someone to screenshot the live H&L app; (b) bilingual core-personality-type card (six terms given); (c) bilingual Mid-Year Update template. |
| MISSING-RUBRIC-OR-KEY | 5 | Mid-Year Reflection summative | `overview.md:96` | "Scored on evidence of self-awareness growth, pathway selection with rationale, and connection between assessment data and career choice" — three criteria, no levels, no exemplar. |
| REVISE | 1 | Wk0 artifact dependency | `day1.md:18-19` | Whole week hinges on the Week 0 My Career Journey sheet being retrievable from a class folder saved 18 weeks earlier. The admonition covers the absent/new student well; it does not cover the teacher who inherited the section and has no Wk0 folder. |

**Prep actions (roll-up):** Day 1: print Core Types vs. Favorites ×30, pull Wk0 reflection folder, open Climber deck to slide 3, pre-verify H&L logins · Day 2: print iceberg template ×30 (+ zoned variant), verify H&L Career Plan tool loads in a test account, confirm the Pathways poster is on the wall · Day 3: print Real Game decision log ×30, confirm Xello Quick Sims is enabled, bookmark BLS · Day 4: print Pathway Ranking Sheet ×30, confirm eDynamic 8.1 is assignable · Day 5: print Mid-Year template ×30, print + hang 10 cluster posters, count out 3 sticker dots ×30, return Wk0 sheets.

**Verdict:** RUNNABLE-WITH-PRINTING — 6 printables + a poster set. Day 3 is the fragile one (single-platform, no fallback), but this is a designated buffer week with explicit cut-or-condense guidance (`overview.md:14`).

---

## Week 4SW-2 — wk2-course-mapping

| Code | Day | Item | Evidence (file:line) | What's needed |
|---|---|---|---|---|
| MISSING-SETUP | 2 | **H&L District Course Planner loaded with Irving ISD course catalogs** — the week's load-bearing tool | `day2.md:34`, `overview.md:14,44` | `> [VERIFY in H&L]` asks the teacher to confirm the Planner carries catalogs for all six campuses. `overview.md:14` names Day 2 + Day 5 as the load-bearing pair producing the d(8)(C) artifact. If the data is not loaded, the whole week reroutes to paper. |
| MISSING-PRINTABLE | 2 | Irving ISD CTE pathway **course sequences** — the paper fallback has no source | `day2.md:66`, `overview.md:104` | Fallback says "fill in the CTE Pathway column with the actual course names from the Irving ISD CTE poster," and Differentiation names a "pre-printed list of Irving ISD CTE pathway course sequences." Neither exists. `PATHWAYS.md` carries pathway names and certification targets **only** — I grepped it: no course names anywhere (only "Architectural Design I"/"Revit" appear, and those are in `day2.md` prose, not PATHWAYS.md). Without a real course catalog, students cannot fill four years of a CTE column by any route. |
| MISSING-PRINTABLE | 3 | Bilingual Family Career Plan Letter — the plan itself flags it may not exist | `overview.md:36`, `day3.md:12,44-58,62` | `> [VERIFY]` at `day3.md:62` reads "Confirm that the bilingual Family Career Plan Letter exists in your CCE materials folder." It does not. Full spec is in prose: two-column EN/ES, greeting, 2-3 sentence course context, 5-field student personalization block, family invitation + signature lines, teacher contact. Support variant = teacher pre-fills type + pathway. |
| MISSING-PRINTABLE | 1 | MS-to-HS Transition worksheet | `day1.md:12,70-74,97-100` | 4 lines (#1 pathway, campus, endorsement, two 9th/10th CTE courses) + the standardized-test selection from Activity 3. Support variant = endorsement checklist; ELL variant = Spanish endorsement names (given at `day1.md:134`). |
| MISSING-PRINTABLE | 2 | 4-Year Course Map blank template | `overview.md:39`, `day2.md:12,59-64` | 4 rows (9th-12th) × 7 columns (English, Math, Science, Social Studies, CTE Pathway, Other). Support variant = core columns pre-filled; ELL variant = Spanish column headers (given at `day2.md:102`). |
| MISSING-PRINTABLE | 4 | Experience Action Plan template | `day4.md:12,58-62,71` | 3 rows × 4 columns (Action, When, How it connects to my pathway, + a "Resources and Support I Need" line per row per FYF Rung 6). |
| MISSING-PRINTABLE | 5 | Individual Career Plan template — the d(8)(C) artifact for the year **(tracked)** | `day5.md:12,49-58`, `overview.md:37` | 8 numbered sections, fully specced in prose. This is the single most important printable in the 4SW block. Support variant = sentence stems pre-filled (`day5.md:119`); ELL variant = bilingual. |
| MISSING-DECK | 1 | "Project a one-page summary of the Texas Foundation High School Program" | `day1.md:30-49` | No such one-pager exists. The 22-credit breakdown and the 5 endorsements are written out in the prose, so this is a typesetting job — but a teacher opening the page Monday has nothing to project. |
| MISSING-SETUP | 3 | H&L Career Plan PDF export | `day3.md:28` | Three fallback options are given (good), but option 1 needs district admin confirmation that export is enabled. Option 3 (photocopy FYF pp. 294-296) may run into the H&L photocopy license question flagged at `docs/resources/resources-status.md`. |
| STRUCTURE | 1 | Texas OnCourse "MapMyGrad" URL unverified | `day1.md:80` | `> [VERIFY]` on the URL. Known open item, recorded for completeness. |
| MISSING-RUBRIC-OR-KEY | 5 | Individual Career Plan summative | `overview.md:98` | Five scoring criteria named (completeness, quality of reasoning, MS-to-HS understanding, evidence of planning, college-credit awareness), no levels, no exemplar. This is the year's d(8)(C) artifact and the thing 6SW Wk6 asks students to present. |
| REVISE | 5 | Timing contradiction | `day5.md:24,26` | Header says "Activity 1: Gather All the Pieces (7 min)"; the body says "Students take 10 minutes." Period math with 10 min is 5+10+25+10+3 = 53. |

**Prep actions (roll-up):** Day 1: print MS-to-HS worksheet ×30, build/print the Foundation HS Program one-pager, confirm texasoncourse URL with counselor · Day 2: **test the H&L District Course Planner with a student account and confirm Irving ISD catalogs are loaded**, print 4-Year Course Map ×30, obtain an actual Irving ISD CTE course catalog for the fallback · Day 3: print the bilingual Family Letter ×30 (must be authored first), print students' Career Plan PDFs in class, verify export is enabled · Day 4: print Experience Action Plan ×30, confirm eDynamic 6.2 · Day 5: print Career Plan template ×30, lay out a checklist of the 9 prior artifacts.

**Verdict:** **BLOCKED** — two independent blockers. (1) The bilingual Family Career Plan Letter does not exist and the plan's own `[VERIFY]` says to check for it. (2) The paper fallback for Day 2 requires Irving ISD CTE course sequences that exist in no file in this repo, so if the H&L Course Planner is not loaded with district data, neither the tool path nor the paper path can produce the 4-year map that Day 5's d(8)(C) summative is built on.

---

## Week 4SW-3 — wk3-aviation

| Code | Day | Item | Evidence (file:line) | What's needed |
|---|---|---|---|---|
| MISSING-SUPPLY | 3-5 | **LEGO bricks and baseplates, 1 set per team of 3-4** | `overview.md:28`, `day3.md:12,30-36` | ~8 sets per section. Build spec requires ≥2 runways at ≥6-stud spacing, taxiways, a control tower, ≥4 gate spaces, and **one solid color brick line per runway** — so each set needs enough same-color bricks for 2+ runway lines. Not classroom stock, not in any known VILS inventory named on the site. Days 3, 4, and 5 all collapse without it. |
| MISSING-SUPPLY | 4-5 | **LEGO aircraft** — never listed in any Materials block | `day4.md:45-63,66-68` | Tier 3 needs 6 planes per team and Tier 4 needs 8. Day 4 has students "move LEGO planes following commands." Materials lists only "bricks and baseplates." Either the sets must include minifig-scale planes, or the build spec needs a "each team also builds 8 plane markers" step that no day contains. |
| MISSING-PRINTABLE | 3-4 | ATC scenario cards, 4 difficulty tiers, 1 set per team | `overview.md:30`, `day3.md:12`, `day4.md:12,43-63` | All four tiers are fully specced at `day4.md:45-63` (plane counts, weather, emergencies, VIP). Card-stock printing job. |
| MISSING-PRINTABLE | 4 | Simulation Run Log | `day4.md:12,77-82` | 6 fields per run × 3 runs (run number + tier, planes safely handled, collisions/near-misses, communication breakdowns, one change for next run). |
| MISSING-PRINTABLE | 4 | "8 Ideas in 8 Minutes" sheet | `day4.md:12,26` | 8 boxes on one page, prompt printed at the top. Trivial to build, does not exist. |
| MISSING-PRINTABLE | 3 | Airport Layout sketch page | `day3.md:12,62-67` | Must accommodate top-down view, labels (R1/R2, T-Alpha/T-Bravo, tower, gates), stud-spacing measurements, and compass directions. |
| MISSING-PRINTABLE | 2 | Military vs. Civilian Pathways comparison chart | `overview.md:31`, `day2.md:12,61-68` | 6 rows × 3 columns, fully specced with content at `day2.md:63-68`. Support variant = Time + Cost rows pre-filled; ELL variant = Spanish row labels. |
| MISSING-PRINTABLE | 1 | Transportation Survey template (10 questions + incentive) | `overview.md:32`, `day1.md:12,62-76` | 7 MC + 3 short-answer slots + an incentive line with a one-sentence justification. Support variant = 4 of 10 pre-drafted; ELL variant = Spanish question stems. |
| MISSING-PRINTABLE | 2 | Aviation career research worksheet (the shared CCE 6-field format) | `overview.md:33`, `day2.md:12,34-41` | Six fields specced. **Same artifact recurs in 5SW Wk1 D2, 5SW Wk2 D1, 5SW Wk3 D1, 5SW Wk6 D1** — build once, use five times in this scope. |
| MISSING-PRINTABLE | 5 | 3-Step Aviation Goal Plan template | `day5.md:12,48-52` | 3 rows × 3 columns (Goal horizon, Specific Action, When) with the horizons pre-labeled. |
| MISSING-PRINTABLE | 5 | Presentation listening grid | `day5.md:33` | 3 columns (most creative layout solution, smartest communication procedure, what I'd steal). Recurring pattern — see cross-cutting note. |
| MISSING-DECK | 3 | Real-airport reference images (DFW, Love Field, Hartsfield-Jackson) | `day3.md:12,55-60` | "Project images of real airports for reference" with four named patterns to notice. No image set exists; teacher must source and vet three aerial photos before class. |
| MISSING-SUPPLY | 1-2 | Sticky notes | `overview.md:34` | For the FYF p. 166 survey brainstorm and the Flight Line Fixers extension. |
| STRUCTURE | 2 | Climber Notes deck "Flight Line Fixers" (slides 2-6) **(tracked)** | `overview.md:35`, `day2.md:12,108` | Gitignored `.pptx`; site-reading teacher cannot open it. `resources-status.md` correctly says to skip the extension rather than improvise photos, so the scheduled week survives. |
| MISSING-SETUP | 5 | Xello "Jobs and Employers" | `day5.md:60` | `> [VERIFY IN Xello]` — extra-time activity only, low risk. |
| REVISE | 4 | Broken cross-reference: "the bilingual ATC command card from Day 1" | `day4.md:133` | Day 1 contains no ATC command card. The card is described only in `overview.md:122-123`. A teacher reading day4.md alone will go looking for something Day 1 never issued. |

**Prep actions (roll-up):** Day 1: print survey template ×30, sticky notes out, bookmark H&L cluster page · Day 2: print career research worksheet ×30 + Military/Civilian chart ×30, bookmark 3 BLS pages, open Flight Line Fixers deck if extension is running · Day 3: **source ~8 LEGO sets + baseplates and pre-sort same-color runway bricks**, print Airport Layout sketch pages, print + cut ATC scenario cards, find and vet 3 airport aerial images, decide where 8 airports get stored overnight · Day 4: print Simulation Run Log + 8-ideas sheet ×30, project the ATC sentence stems, confirm each team has 6-8 plane pieces, confirm eDynamic 2.2 · Day 5: print Goal Plan template ×30 + listening grid ×30, plan airport transport to the front of the room.

**Verdict:** **BLOCKED** — LEGO sets and LEGO aircraft. Three of five days (3, 4, 5) are built on a class set of LEGO that no Materials list quantifies, no page substitutes for, and no repo document confirms the VILS labs own.

---

## Week 4SW-4 — wk4-drone-engineering

| Code | Day | Item | Evidence (file:line) | What's needed |
|---|---|---|---|---|
| MISSING-SUPPLY | 3-4 | **Classroom drones, 1 per team of 3-4 (DJI Tello EDU or equivalent)** | `overview.md:27`, `day3.md:12`, `day4.md:12` | ~8 drones per section plus a 4th backup named at `day4.md:66`, plus spare batteries (named at `day3.md:68` but never in a Materials list). Two full days are hands-on flight. The only fallback offered is "flight simulator app" (`overview.md:101`, `day4.md:66`), and no specific free app is named or vetted. |
| MISSING-SETUP | 3-4 | Open indoor flight space | `day3.md:12,66` | "cleared classroom or gym" — a gym needs booking, and a cleared classroom means pushing 30 desks to the walls at the start of two consecutive periods and back before the bell. Neither is named as a prep action. |
| MISSING-SUPPLY | 3-4 | Masking tape (takeoff squares), cones/chairs/tape targets, stopwatches | `overview.md:34`, `day3.md:12`, `day4.md:12` | Day 4 course needs 5 stations marked. Stopwatches appear only in Day 4 Materials. |
| MISSING-PRINTABLE | 3 | Drone Safety Briefing handout (2 pages, with signature line) | `overview.md:32`, `day3.md:12,45-57` | Seven numbered rules, all written out at `day3.md:49-55`. **The signature is the gate to flying** ("no signature, no controller") so this printable is not optional. ELL variant = "visual safety briefing handout with diagrams and bilingual labels" (`overview.md:111`) requires diagrams that do not exist. |
| MISSING-PRINTABLE | 4 | Drone Navigation Course score sheet | `overview.md:33`, `day4.md:12,46-50` | 3 runs × 6 columns (takeoff clean, hover 5s, through gate, inspection no-touch, landing clean, time). |
| MISSING-PRINTABLE | 1 | Robot Blueprint sheet ("Protecting Wildlife" template) | `overview.md:29`, `day1.md:12,69-77` | Blank blueprint frame with a label legend for the 5 required components + bonus. Support variant = rotors and battery pre-drawn (`day1.md:122`); ELL variant = bilingual label sheet. |
| MISSING-PRINTABLE | 2 | UAS Industry Research Template, 1/student | `overview.md:31`, `day2.md:12,36-43` | 6 sections, fully specced. Support variant needs curated links — see next row. |
| MISSING-PRINTABLE | 5 | Career Classification template | `day5.md:12,49-58` | 8 fields specced including the three Y/N + evidence rows. This is the d(5)(B) summative artifact. |
| MISSING-PRINTABLE | 5 | Jigsaw listening grid (5 rows × 3 columns) | `day5.md:34` | Top career / Salary / Most surprising fact, one row per industry. |
| MISSING-SETUP | 2 | "Pre-selected research sources for each industry" | `overview.md:99`, `day2.md:106` | Differentiation promises "a curated list of 3-4 sources per industry" for 5 industries = ~18 vetted links. None exist. The plan flags Emergency Services as the hardest to research (`day2.md:66`), which is exactly where the curated list matters most. |
| MISSING-SETUP | 3 | Drone controller reference card / DJI demo video | `overview.md:100`, `day3.md:72,127` | "Drone controller reference card with visual diagrams" and "Project a short DJI Education video showing the basic 3-control method." Neither the card nor a specific video URL exists. |
| MISSING-DECK | 1 | Conservation drone image | `day1.md:82` | "Project a real conservation drone image (search 'wildlife conservation drone')" — teacher must find and vet an image live. |
| MISSING-RUBRIC-OR-KEY | 5 | UAS Jigsaw Presentation + Career Classification summative | `overview.md:94` | Three criteria, no levels. The classification claim requires evidence-quality judgment ("a team calling a field high-demand from a single news headline," `day2.md:68`) that a rubric would make consistent. |
| REVISE | 4 | Period overrun | `day4.md:16,24,42,72,84` | 3 + 8 + 35 + 3 + 4 = **53 min** in a 50-min period. Activity 2's own math (`day4.md:54-56`) computes 36 minutes of flight time against a 35-minute block. |

**Prep actions (roll-up):** Day 1: print Robot Blueprint ×30, sticky notes, find + vet one conservation drone image · Day 2: print UAS Research Template ×30, curate 3-4 links per industry ×5, bookmark BLS/FAA/DJI · Day 3: **charge every drone + spare battery the night before**, confirm/book the flight space, print + count Safety Briefings ×30, tape one 1ft takeoff square per team, cue the DJI control video, build the controller reference card · Day 4: set up the 5-station course (cones/chairs/tape targets), print score sheets ×30, charge batteries again, stage a 4th backup drone, source ~8 stopwatches · Day 5: print Career Classification template ×30 + listening grid ×30, project a 4-min timer.

**Verdict:** **BLOCKED** — ~8 classroom drones plus spares and batteries, plus a cleared flight space, carry Days 3 and 4. The stated fallback (an unnamed flight simulator app) is not specific enough to run on.

---

## Week 4SW-5 — wk5-automotive

| Code | Day | Item | Evidence (file:line) | What's needed |
|---|---|---|---|---|
| MISSING-PRINTABLE | 3 | Automotive Salary Comparison worksheet | `overview.md:37`, `day3.md:12,38-42` | 3 career rows (+1 optional) × 6 columns (DFW entry, DFW experienced, education time, education cost, 10-year demand) + a salary-to-education ratio line per row + a cross-cluster preview row. Support variant = one row pre-filled with all 3 sources; ELL variant = Spanish headers (given at `day3.md:94`). |
| MISSING-PRINTABLE | 2 | Apprenticeship vs. College comparison chart | `overview.md:38`, `day2.md:12,63-73` | 9 rows × 2 columns, all content written out at `day2.md:65-73`, plus a 3-sentence preference statement box. Support variant = Time/Cost/Credential rows pre-filled. |
| MISSING-PRINTABLE | 4 | Ratteree vs. Trade School comparison notes template | `overview.md:39`, `day4.md:12,44-50,62-68` | 2 columns × 6 rows (time, cost, credential, income during, employability after, best fit) + a 2-3 sentence comparison box. |
| MISSING-PRINTABLE | 5 | Cross-Cluster Comparison presentation note card | `day5.md:12,30-38` | 7 rows × 2 columns, with a talking-script area on the back. Support variant = salary/education pre-filled from Day 3. |
| MISSING-PRINTABLE | 5 | Presentation listening grid | `day5.md:65` | Which two careers compared / which one chosen / the presenter's additional criterion. |
| MISSING-PRINTABLE | 1 | Labeled car-parts diagram (Support) | `day1.md:119`, `overview.md:107` | Named as a support scaffold: "a labeled car diagram (hood, fender, bumper cover, headlight assembly, quarter panel) so students can name parts without hunting for vocabulary." The prose flags the Damaged Parts vs. Visible Damage confusion as the day's predictable error, so this scaffold is doing real work. |
| STRUCTURE | 4 | Ratteree program information — no source a teacher can reach | `day4.md:12,26,28,30-42`, `overview.md:106` | Materials name "Irving ISD Ratteree program info (district website)"; the `[VERIFY with CTE coordinator]` at `day4.md:28` says to confirm campus, schedule, transport format, and certification outcomes. Differentiation at `day4.md:102` concedes "students cannot easily research it" and asks the teacher to pre-fill the whole Ratteree column. So the teacher must produce content the repo does not hold. |
| STRUCTURE | — | Climber Notes deck "Safety Squad" (slides 2-5) **(tracked)** | `overview.md:32,110` | Gitignored `.pptx`. Enrichment block only — the scheduled five days run without it, as `resources-status.md` states. |
| MISSING-SUPPLY | 3 | Calculators | `day3.md:12,92` | "calculator (or phone calculator)" — phone use may be prohibited; the ratio math is the day's deliverable. |
| MISSING-SETUP | 5 | Xello "Save Careers" | `day5.md:82` | `> [VERIFY IN Xello]`. 7-minute closing activity, low risk. |
| MISSING-RUBRIC-OR-KEY | 5 | Cross-Cluster Salary Presentation summative | `overview.md:99` | Three criteria, no levels, no exemplar. |

**Notable positive:** `day5.md:49-54` contains a worked presentation-timing warning (25 students × 90s vs. a 28-min block) with three named alternatives. This is the model the other presentation days in this scope should follow.

**Prep actions (roll-up):** Day 1: project FYF pp. 150-152 damage images, print the labeled car diagram, pre-fill one Collision Report as a model · Day 2: print Apprenticeship vs. College chart ×30, bookmark ase.com + BLS · Day 3: print Salary Comparison worksheet ×30, source ~30 calculators, bookmark CareerOneStop Compare Occupations · Day 4: **pre-fill the Ratteree column yourself** (students cannot research it), print comparison notes ×30, verify Ratteree details with the CTE coordinator, bookmark UTI/Lincoln/TCC · Day 5: print note cards ×30 + listening grid ×30, pick the presentation format from the three options and set the timer.

**Verdict:** RUNNABLE-WITH-PRINTING — 6 printables and a calculator set. The soft spot is Day 4: the teacher has to author the Ratteree column from district sources the repo does not carry.

---

## Week 4SW-6 — wk6-trades-capstone

| Code | Day | Item | Evidence (file:line) | What's needed |
|---|---|---|---|---|
| MISSING-PRINTABLE | 2 | Transferable Skills Matrix (6 careers × 8 skills = 48 cells) **(tracked)** | `overview.md:37`, `day2.md:12,28-47,66` | Careers and skills both fully listed. Needs a cell large enough for "YES + example" or "NO + reason," plus a total-out-of-48 line and a closing sentence stem. Support variant = one full row pre-filled, or a reduced 4×6 grid; ELL variant = 8 Spanish skill labels (given at `day2.md:115`). |
| MISSING-PRINTABLE | 5 | Mid-Year Growth Reflection template, 2 pages **(tracked)** | `overview.md:39`, `day5.md:12,44-79` | 6 sections, fully specced. This is the **4SW summative artifact**. Support variant = the full sentence-stem paragraph is already written at `day5.md:138`; ELL variant = bilingual. |
| MISSING-PRINTABLE | 3 | Professional Associations Jigsaw research template **(tracked)** | `overview.md:38` (implied), `day3.md:12,40-49` | 8 fields specced. Support variant = "Full name" + "Who can join" pre-filled. |
| MISSING-PRINTABLE | 4 | Work Ethic Examples worksheet | `overview.md:38`, `day4.md:12,37-40` | 3 prompts (a task where work ethic matters, the consequence of poor work ethic, the system that enforces it). Support variant = one example completed. |
| MISSING-PRINTABLE | 3 | Jigsaw listening grid (5 associations × 3 columns) | `day3.md:72` | Purpose / benefits / who joins. |
| MISSING-PRINTABLE | 1 | Pre-filled diagnosis chart (Support) | `overview.md:103`, `day1.md:116` | Issue 1's Possible Problem + Explanation worked as a model so students copy the reasoning pattern. Requires an answer key for Issue 1 that no file holds — the FYF student edition prints the clue sets but no answers. |
| MISSING-RUBRIC-OR-KEY | 1 | No answer key for the four truck diagnoses | `day1.md:47-63` | The FYF student edition prints four clue sets with blank Possible Problem / Explanation columns. A brand-new teacher with no automotive background has no key for "dark oil + engine running hot" or for which two issues connect (the DOK 3 at `day1.md:86` asks exactly that). The facilitation tips coach the reasoning move but never state the expected answers. |
| MISSING-RUBRIC-OR-KEY | 5 | Mid-Year Growth Reflection summative | `overview.md:95` | Six required sections, three scoring criteria, no levels. |
| MISSING-DECK | 5 | "5SW Wk1 Architecture cover slide" | `day5.md:100` | Named for the six-weeks preview, hedged with "if available." No slide exists anywhere. Minor. |
| REVISE | 4 | Period overrun | `day4.md:16,24,46,73,81` | 5 + 15 + 25 + 5 + 5 = **55 min** in a 50-min period. |
| REVISE | 2 | Internal timing inconsistency | `day2.md:24,66` | Header says Activity 1 is 32 min; body says "After 28 minutes of filling in cells." |
| REVISE | 5 | Artifact-gathering dependency | `day5.md:26-34` | Day 5 asks students to lay out seven artifacts spanning Week 0 through this week, including two workbook sections and four CCE worksheets that do not yet exist as printables. |

**Prep actions (roll-up):** Day 1: project FYF pp. 153-155, pre-fill the Issue 1 model, be ready with an answer key for all four diagnoses · Day 2: print Transferable Skills Matrix ×30 (+ pre-filled row variant) · Day 3: print Jigsaw template ×30 + listening grid ×30, bookmark 5 association sites and pre-walk each navigation path (`day3.md:54`) · Day 4: print Work Ethic worksheet ×30, verify H&L Career Plan loads · Day 5: print the 2-page Mid-Year Growth Reflection ×30, collect the Wk0 reflection folder, arrange the sharing circle.

**Verdict:** RUNNABLE-WITH-PRINTING — 5 printables, no supplies, no platform blockers. Day 1's missing answer key is the real risk for a cold-start teacher.

---

## Week 5SW-1 — wk1-architecture (course prototype week)

**Software-setup assumptions, captured in full per the task brief:**

| # | Assumption | Evidence | Status |
|---|---|---|---|
| 1 | `tinkercad.com` and `*.autodesk.com` are whitelisted by IT ≥24 hrs before Day 3 | `day3.md:38` | **Named** — this is the best tech-setup admonition in the entire 12-week scope |
| 2 | Login tested with 2 student accounts on the school Chromebook network beforehand | `day3.md:38` | **Named** |
| 3 | A paper-sketch fallback exists if SSO fails | `day3.md:38` | **Named** (as a concept; no fallback sheet exists — see MISSING-PRINTABLE below) |
| 4 | Expected setup time 10 min if pre-verified, 20-30 min if domain access fails | `day3.md:38` | **Named** |
| 5 | Students sign in with the **school Google account** via "Join Now → Sign in with Google" | `day3.md:28-30` | **Named** |
| 6 | Students under 13 can create Autodesk/TinkerCAD accounts | — | **NOT named.** 7th graders are 12-13. Autodesk's under-13 flow requires either guardian consent or a teacher-created TinkerCAD Classroom with class codes/nicknames instead of individual Google SSO. The plan routes every student through individual Google SSO, which is the flow that stalls for under-13 users. |
| 7 | A **TinkerCAD Classroom** exists so the teacher can share a starter template | `day3.md:126` ("Share via TinkerCAD's classroom feature") | **NOT named as a setup step.** Creating the class, generating codes, and adding a roster is separate before-class work that appears nowhere. |
| 8 | The starter template itself (4 walls pre-grouped) has been authored | `overview.md:98`, `day3.md:126` | **NOT provided.** Teacher must build it in TinkerCAD first. |
| 9 | Chromebooks can run TinkerCAD's WebGL 3D editor at ~30 concurrent sessions | — | **NOT named.** Older Chromebooks throttle; the plan's only performance note is about SSO. |
| 10 | The PNG export path is "Send To → Download as PNG" | `day4.md:39-41` | **Named**, but unverified against the current TinkerCAD UI (Export/Send To has moved in past releases). No `[VERIFY]` marker on it. |
| 11 | Students can save `LastName_Building.png` somewhere the teacher can project on Day 5 | `day4.md:41`, `day5.md:12,26` | **Partially named.** "Save the file with their name" — no destination folder named; Day 5 requires the teacher to project each student's PNG. |
| 12 | Canva (extension option) | `overview.md` extensions elsewhere in 5SW | Not needed this week |

| Code | Day | Item | Evidence (file:line) | What's needed |
|---|---|---|---|---|
| MISSING-SETUP | 3-5 | TinkerCAD under-13 account flow + TinkerCAD Classroom setup + starter template | `day3.md:28-30,38,126`, `overview.md:98` | See rows 6-8 above. The strong `Tech Setup` admonition covers network and SSO but not age gating, not classroom provisioning, and not the template it tells the teacher to share. |
| STRUCTURE | 4 | **Climber Notes deck "Unexpected Architecture" (slide 2) is required, not optional** **(tracked)** | `overview.md:31`, `day4.md:12,60` | I checked the workbook: FYF p. 182 Step 2 reads "Get Climber Notes from your teacher. It will give you an overview of the city's goals." The student edition **prints no city goals**. Without the slide, Step 2 has no content and Step 4's blueprint has no design brief. The `.pptx` is gitignored — a site-reading teacher cannot open it. |
| MISSING-PRINTABLE | 2 | Career research worksheet + salary comparison worksheet **(tracked)** | `overview.md:36`, `day2.md:12,30-36,52-57` | Career research = the shared 6-field CCE format. Salary comparison = 4 career rows × 5 columns, with three rows pre-labeled (Architect, Drafter, Interior Designer) and a 4SW trades row. ELL variant = Spanish column headers. |
| MISSING-PRINTABLE | 1 | Pre-divided safety poster layout (Support) | `overview.md:101`, `day1.md:109` | Poster board pre-divided into three labeled boxes (top 5 rules, essential equipment, safety map) — the plan explicitly says "the barrier is layout, not content." |
| MISSING-PRINTABLE | 4 | Pre-divided firm poster board (Support) | `day4.md:95` | Front-view box + side-view box with a label line under each. |
| MISSING-PRINTABLE | 3 | Paper-sketch fallback sheet | `day3.md:38,84-88` | The Tech Setup note says to have one ready. Day 3's sketch spec (top-down floor plan + front view with roof, 1 door, 2 windows) plus the 3-item pair-check list at `day3.md:96` would fill it. Currently students sketch in engineering notebooks instead. |
| MISSING-SUPPLY | 1, 4 | **Chart paper / poster board: one sheet per student (Day 1) plus one per firm (Day 4)**, markers | `overview.md:29`, `day1.md:12`, `day4.md:12` | ~30 sheets on Day 1 alone, per section. Markers named on both days. |
| MISSING-SUPPLY | 3 | Engineering notebooks | `day3.md:12,84` | "open their engineering notebooks to a fresh page." First and only mention in 5SW; not classroom stock, and no earlier week in scope establishes them. |
| MISSING-SUPPLY | 4 | Sticky notes | `overview.md:30`, `day4.md:12,62` | FYF p. 183 Step 3 requires them by name. |
| MISSING-SETUP | 5 | eDynamic Unit 3.1 | `day5.md:75` | `> [VERIFY IN eDynamic]` — 10-min closing activity. |
| MISSING-RUBRIC-OR-KEY | 5 | TinkerCAD Building Presentation summative | `overview.md:93` | Four criteria (design quality, career knowledge, education/training accuracy, salary comparison data), no levels. The prototype week is the one most likely to be copied, so this rubric gap propagates. |
| MISSING-RUBRIC-OR-KEY | 4 | Firm pitch feedback chart is FYF-printed but has no rating scale defined | `day4.md:66`, FYF p. 184 | The workbook prints a 5-category chart with a "Rating" column and no scale. Students need to be told what the rating means (1-5? ✓/✗?). |
| REVISE | 2 | Period overrun | `day2.md:16,24,46,65,75` | 5 + 20 + 15 + 10 + 5 = **55 min** in a 50-min period. |
| REVISE | 5 | Period overrun | `day5.md:16,24,51,67,79` | 5 + 20 + 15 + 10 + 5 = **55 min**. Compounded by the presentation-math warning at `day5.md:38-45`, which already flags 24×2min = 48 min against a 20-min block and offers three fixes. |

**Prep actions (roll-up):** Day 1: cut/pre-divide ~30 poster boards, set out markers, print career-research worksheets, bookmark H&L A&C cluster · Day 2: print career research + salary comparison ×30, bookmark BLS Architects + Drafters, prep one modeled salary row · Day 3: **have IT whitelist tinkercad.com + \*.autodesk.com ≥24 hrs out, test 2 student logins, resolve the under-13 account flow, create the TinkerCAD Classroom, build and share the 4-wall starter template, print paper-sketch fallbacks**, confirm engineering notebooks are issued · Day 4: open the Unexpected Architecture deck to slide 2, pre-divide firm poster boards, sticky notes out, verify the Send To → PNG path yourself · Day 5: collect/stage every student PNG for projection, pick one of the three presentation formats, confirm eDynamic 3.1.

**Verdict:** RUNNABLE-WITH-PRINTING for Days 1-3 and 5. **Day 4 Activity 2 Step 2 is BLOCKED for a site-only teacher** — the city's goals exist solely on the Climber Notes slide, and the workbook explicitly defers to it.

---

## Week 5SW-2 — wk2-civil-engineering

| Code | Day | Item | Evidence (file:line) | What's needed |
|---|---|---|---|---|
| MISSING-SUPPLY | 3-4 | **Bridge-building kit per team of 2-3: 40 plastic drinking straws, 3 ft masking tape, 5 index cards, scissors** | `overview.md:29`, `day3.md:36-39`, `day4.md:12` | At 10-12 teams that is **400-480 straws**, ~35 ft of tape, 50-60 index cards, and 10-12 scissors per section — and again per section if you teach multiple. Days 3, 4, and half of Day 5 collapse without it. |
| MISSING-SUPPLY | 4 | Test weights + a 12-inch gap station + a stopwatch | `overview.md:29-30`, `day4.md:12,50-53` | Two named methods: a cup of pennies (needs a large penny supply and a cup per team) **or** a digital kitchen scale plus textbooks. Neither is classroom stock. The gap station is two desks or book stacks 12 in apart — free, but must be set up. |
| MISSING-PRINTABLE | 3 | Bridge Design sketch page | `overview.md:39`, `day3.md:12,79-84` | Must hold **two** designs, each with top-down view, side view, labeled structural elements, and predicted weak points. |
| MISSING-PRINTABLE | 4 | Test results sheet | `day4.md:12,62,70-74` | Max weight held, where it failed first, plus the three-part redesign statement (what failed / why / what you'd change). |
| MISSING-PRINTABLE | 2 | Six test comparison cards (PSAT 8/9, PSAT/NMSQT, SAT, ACT, ASVAB, TSI) | `day2.md:12,46` | "Before class, post 6 index cards around the room... Each card shows: when it is taken, what it measures, what it is used for, and who should take it." All six descriptions are written out at `day2.md:32-37`, so this is transcription, but nothing exists to print. |
| MISSING-PRINTABLE | 2 | PSAT/SAT/ACT Impact worksheet | `overview.md:37`, `day2.md:12,50-55` | 4 questions × up to 6 stations. Support variant = PSAT 8/9 and SAT rows pre-filled; ELL variant = bilingual comparison handout. |
| MISSING-PRINTABLE | 2 | Emerging Engineering Careers research template | `overview.md:38`, `day2.md:12,69-73` | 5 fields specced. This is a named piece of the week's summative (`day5.md:69`). |
| MISSING-PRINTABLE | 1 | Engineering career research worksheet | `overview.md:36`, `day1.md:12,45-50` | Shared 6-field CCE format again. |
| MISSING-PRINTABLE | 1 | Pre-marked kitchen floor plan (Support) | `overview.md:112`, `day1.md:108` | Sink/stove/fridge circled and the walking path drawn as a dotted line, overlaid on the FYF p. 174 plan. |
| MISSING-PRINTABLE | 3 | Truss/arch/beam bridge templates (Support) | `overview.md:108`, `day3.md:127` | "Bridge design templates showing truss, arch, and beam geometries with labeled parts." |
| MISSING-DECK | 3 | Bridge-type comparison visual | `day3.md:60` | "Project a quick 3-minute visual tour of bridge types... use PBS Design Squad **or a static comparison slide**." Neither a vetted PBS video URL nor the comparison slide exists. The triangle-vs-square load demonstration at `day3.md:58` also needs a physical or projected demo the plan does not supply. |
| MISSING-SUPPLY | 5 | Chart paper or sticky notes for the Mars rover brainstorm | `overview.md:31`, `day5.md:12,50` | FYF p. 106 Step 1 calls for them by name. |
| MISSING-RUBRIC-OR-KEY | 5 | Emerging Career Research + Bridge Challenge Report summative | `overview.md:103` | Four criteria across five submitted artifacts, no levels, no weighting. |

**Notable positive:** `day4.md:52` defines "failure" before testing starts ("STOP at the first visible sag OR the first taped joint that separates, teacher's call is final"), which pre-empts the arguing that always follows a bridge test. Worth copying.

**Prep actions (roll-up):** Day 1: print engineering career research worksheet ×30, print the pre-marked kitchen floor plan, bookmark H&L Engineering cluster · Day 2: **write and post 6 test comparison cards before students arrive**, print Impact worksheet + Emerging Careers template ×30, bookmark College Board + BLS Environmental Engineers · Day 3: **order/assemble ~12 bridge kits (400+ straws, tape, index cards, scissors)** but do not hand them out, print Bridge Design sketch pages ×12 teams, vet a PBS Design Squad clip or build the bridge-type slide, print truss/arch templates · Day 4: distribute kits, build the 12-inch gap test station, source pennies+cups or a digital kitchen scale, print test results sheets, put the class results whiteboard up · Day 5: chart paper/sticky notes for the rover, keep the Day 4 results board visible, project a 60-sec timer.

**Verdict:** **BLOCKED** — the straw-bridge consumable kit. Two full days plus half of Day 5 depend on ~400 straws, tape, index cards, scissors, and a weight-testing rig per section, none of which are confirmed on hand.

---

## Week 5SW-3 — wk3-construction-trades

| Code | Day | Item | Evidence (file:line) | What's needed |
|---|---|---|---|---|
| STRUCTURE | 4-5 | **Climber Notes deck "Spot the Problem" (slides 2-6) is the only source of the five inspection images** **(tracked)** | `overview.md:31,67`, `day4.md:12,62,74`, `day5.md:12,46` | The images are teacher-side only; FYF p. 177 prints observation boxes with nothing to observe. Day 4's 17-minute Activity 3 and Day 5's 12-minute inspection report both have zero content without the deck, and the report is a **named summative** (`overview.md:99`). Gitignored `.pptx`; unreachable from the website. |
| REVISE | 5 | **The Day 5 jigsaw trade teams are never assembled and the presentations are never assigned** | `day5.md:26` vs. `day2.md:58-64` | Day 5 opens "Teams assembled on Day 2 (by trade: Carpenter, Construction Manager, Mason, Heavy Equipment Operator) give their Jigsaw presentations." Day 2 assembles **union** research groups (IBEW, UA, UBC, LIUNA, IUOE), not trade teams. No day in the week forms trade teams, assigns the 6-point presentation format, or gives prep time for it. A cold-start teacher arrives Friday expecting prepared presentations that were never assigned. |
| MISSING-PRINTABLE | 3 | Construction Career Classification worksheet | `overview.md:35`, `day3.md:12,43-62` | 5 career rows × 6 fields, plus a 3-sentence cited justification box. Named summative. Support variant = Electrician row fully pre-filled; ELL variant = Spanish headers. |
| MISSING-PRINTABLE | 2 | Apprenticeship Pathway infographic (apprentice → journeyman → master) | `overview.md:36,105`, `day2.md:12,26` | Projected in Activity 1 and named again as an ELL/visual scaffold. Four stages with the wage numbers at `day2.md:35-37`. |
| MISSING-PRINTABLE | 2 | Apprenticeship vs. College comparison chart + Union Research Notes sheet | `day2.md:12,41-47,66-74` | Chart = 5 rows × 2 columns (content given). Notes sheet = 5 fields per union. ELL variant = bilingual union template. |
| MISSING-PRINTABLE | 1 | Construction career research worksheet | `overview.md:37`, `day1.md:12,58-65` | Shared 6-field CCE format. |
| MISSING-PRINTABLE | 4 | MacArthur pathway map handout | `day4.md:12,44-52` | Middle school → MacArthur Construction Technology → NCCER CORE → four named post-HS branches. All content is in the prose. |
| MISSING-PRINTABLE | 5 | Presentation note-taking sheet | `day5.md:12,35` | "one key fact per trade" across 4+ trades. |
| MISSING-PRINTABLE | 4-5 | Inspection report scaffolds (Support) | `overview.md:107`, `day4.md:115`, `day5.md:113` | Observation stem card for each image; findings table with the Image # column pre-filled and one row completed as a model. Both depend on the deck images. |
| MISSING-RUBRIC-OR-KEY | 4-5 | No answer key for the five inspection images | `day4.md:74-78`, `day5.md:48-53` | "Some images show real problems and some show a house in normal condition." A brand-new teacher with no construction background cannot confirm which is which, and Day 5's exit ticket names three specific defects (exposed wiring, foundation crack, missing shingles) that imply a known answer set. The Climber Notes speaker notes may carry this — but they are not on the site. |
| MISSING-SUPPLY | 5 | Graph paper + sticky notes (Powerskill: Creativity extension) | `overview.md:38`, `day5.md:114` | 12ft × 12ft wall at one square = one 6-inch tile means a 24×24 grid; ordinary graph paper works but must be stocked. Extension only. |
| MISSING-SETUP | 3 | "CareerOneStop Compare Occupations tool pre-loaded on classroom computers" | `overview.md:106` | Named as a scaffold; requires the teacher to open the tool on machines before class. |
| MISSING-RUBRIC-OR-KEY | 5 | Jigsaw + Classification + Inspection Report summative | `overview.md:99` | Five criteria across three artifacts including a d(4)(C) oral-presentation claim, no levels. |

**Prep actions (roll-up):** Day 1: print construction career research worksheet ×30, project FYF pp. 196-198 · Day 2: print apprenticeship infographic + comparison chart + union notes ×30, bookmark 5 union sites, **assign trade jigsaw teams here if Day 5 is to run as written** · Day 3: print Classification worksheet ×30, pre-load CareerOneStop, model the Electrician row · Day 4: **open the Spot the Problem deck and know which images show real problems**, print the MacArthur pathway map ×30, bookmark nccer.org, print observation stem cards · Day 5: reproject the deck, print the note-taking sheet ×30 and the pre-filled findings table, graph paper for the extension, project a 3-min countdown.

**Verdict:** **BLOCKED** — two independent blockers. (1) The Spot the Problem deck is the sole source for Days 4-5 and is unreachable from the site. (2) The Day 5 jigsaw trade presentations are referenced as prepared work that no earlier day ever assigns.

---

## Week 5SW-4 — wk4-hvac-electrical-plumbing

| Code | Day | Item | Evidence (file:line) | What's needed |
|---|---|---|---|---|
| STRUCTURE | 2 | **Climber Notes deck "PowerSkill Written Communication" (slides 2-5) is the only source of the four AC service-ticket photos** **(tracked)** | `overview.md:31,64`, `day2.md:12,47,66` | I checked FYF pp. 187-190: they print **blank Field Notes forms only** (Site / Observation / Diagnosed problems / Action), with no photos. The 30-minute Activity 2 — and the week's d(4)(B) deliverable — has nothing to observe without the deck. Gitignored `.pptx`. |
| STRUCTURE | 5 | Climber Notes deck "Plumbing Under Pressure" (slide 2, emergency basics) **(tracked)** | `overview.md:32`, `day5.md:12,38` | Step 2's entire content is the projected slide. The five protocol items are paraphrased at `day5.md:38`, so this one degrades better than Day 2's — but the deck is still named as required Materials and is unreachable from the site. |
| MISSING-PRINTABLE | 1-4 | Skilled Trades Comparison Matrix — the week's summative **(tracked)** | `overview.md:38`, `day1.md:12,52-63`, `day4.md:56-68` | 4 trade columns × 11 rows (apprenticeship length, licensing, certification names, DFW starting salary, DFW experienced salary, BLS outlook, three classification rows, perk, quirk). Built across Days 1, 2, and 4. Support variants = apprenticeship row pre-filled, or a reduced 2-trade version; ELL variant = Spanish headers. |
| MISSING-PRINTABLE | 3 | Labor Market Analysis worksheet | `overview.md:39`, `day3.md:12,55-64` | 8 fields × 4 trades. Modeled row (Electrician) is fully worked at `day3.md:28-40`. Named summative. |
| MISSING-PRINTABLE | 3-4 | "Pre-populated BLS data sheets" for each trade (Support) | `overview.md:104`, `day3.md:102` | Promised twice as the primary scaffold. Requires the teacher to pull BLS numbers for 4 trades and typeset them. |
| MISSING-PRINTABLE | 2 | Six-part AC table with "what can go wrong" pre-filled (Support) | `day2.md:105` | The full table content is at `day2.md:55-62`, so this is a straight cut of the existing table. |
| MISSING-PRINTABLE | 5 | Plumbing crew role cards (3 roles) | `day5.md:110` | "Print the three crew roles on cards with the 'what they do' column already filled in." Content is at `day5.md:32-36`. ELL variant = bilingual. |
| MISSING-SUPPLY | 5 | Chart paper or poster board + markers, 1 set per team of 3 **(tracked)** | `overview.md:33`, `day5.md:12,42` | ~10 sets per section for the labeled work-zone sketch. |
| MISSING-RUBRIC-OR-KEY | 2 | No answer key for the four service tickets | `day2.md:66-71` | Ticket #1 is modeled live from the photo, but Tickets #2-4 are independent work with a technical diagnosis (iced evap coil vs. clogged filter vs. low refrigerant) that a non-HVAC teacher cannot score confidently. The DOK 3 at `day2.md:73` explicitly asks students to distinguish two different causes of the same symptom. |
| MISSING-RUBRIC-OR-KEY | 5 | Two summatives, no rubrics | `overview.md:97,99` | The Matrix + Labor Market Analysis (three criteria) and the Plumbing team plan (d(1)(C) + d(4)(C), no criteria at all beyond a component list). |
| MISSING-SETUP | 3 | Indeed job-posting search as a data source | `day3.md:28,57` | "Search Indeed or BLS for 'Electrician DFW'" is modeled and then required in the student worksheet. Job-board sites are commonly filtered on district networks; no alternative is named for that row. |
| STRUCTURE | 4 | Irving ISD pathway placement + tiny-home focus question | `day4.md:47-50` | Two `[VERIFY with CTE coordinator]` items. Known open items, recorded for completeness. |

**Prep actions (roll-up):** Day 1: print the Skilled Trades Matrix ×30, bookmark 4 BLS pages + TDLR + TSBPE, pre-run the licensing searches yourself · Day 2: **open the PowerSkill Written Communication deck and confirm all four ticket photos display**, print the six-part AC table variant, model Ticket #1 in advance so you know the answer · Day 3: print the Labor Market Analysis worksheet ×30, pre-populate BLS data sheets for 4 trades, confirm Indeed is not filtered · Day 4: bookmark IBEW/UA Local 100/SMACNA + TCC/Dallas College + Lincoln/UTI, verify pathway placement with the CTE coordinator · Day 5: **open the Plumbing Under Pressure deck to slide 2**, print role cards, set out ~10 sets of chart paper + markers with a marker tray per table.

**Verdict:** **BLOCKED** — the PowerSkill Written Communication deck. Day 2's 30-minute core activity and the week's d(4)(B) deliverable have no content without the four photos, which exist only in a gitignored `.pptx`. Day 5 is degraded but survivable from the prose paraphrase.

---

## Week 5SW-5 — wk5-personal-budget (Rung 3 continuity)

**Continuity assumptions carried from 4SW Wk1 Day 3 (Rung 3), captured per the task brief:**

| # | Assumption | Evidence | Status |
|---|---|---|---|
| 1 | Students still physically hold their FYF workbook with pp. 285-286 filled in, ~15 weeks later | `day1.md:12,48` | Reasonable (consumable workbook stays with the student), but unstated. |
| 2 | Rung 3 was actually completed | `day1.md:59` | **Handled well:** "Students who did not finish Rung 3, or whose local number is blank, refresh it now from the Hat profile in the app and write it in." |
| 3 | A student absent on 4SW Wk1 Day 3 has a path | `day1.md:112`, `overview.md:104` | **Handled:** "hand over a completed Rung 3 example and have them fill in only the local salary line... No student should leave Day 1 without a salary number." |
| 4 | The set of completed Rung 3 examples exists | `overview.md:104`, `day1.md:112` | **NOT provided.** Named twice as the safety net; no such artifact exists in the repo. The teacher must author several worked Rung 3 pages before Day 1. |
| 5 | A student who **joined the class after mid-year** has a path | — | **NOT named.** Fallbacks 2 and 3 assume the student was present for the mid-year review. A student who has never seen the Capstone chapter has no Rung 3 pages at all; only the (nonexistent) example set covers them. |
| 6 | The "average in your area" line (FYF p. 286) is filled in | `day1.md:54,57`, `day2.md:79` | **This is the single point of failure.** `day1.md:57` states "The local average is the number the budget runs on" and `day2.md:79` says to use "the 'average in your area' figure." If that line is blank class-wide, every Day 2 budget, every Day 3 city comparison, and the Day 5 portfolio have no input. |
| 7 | H&L Hat profiles actually carry **DFW-localized** salary data | `day1.md:59`, and 4SW Wk1 `day3.md:60` | **NOT verified anywhere in either week.** DFW-localized H&L salary is asserted as the primary source in ~9 of the 12 weeks in this scope, and no `[VERIFY]` marker anywhere in 4SW or 5SW asks a district admin to confirm it. BLS gives national medians only, so if H&L does not localize, the "average in your area" line has no source. |
| 8 | Rung 3's career goal is still the student's career goal | `day1.md:59` | **Handled:** students may swap, but must redo the Rung 3 salary/outlook lines rather than guessing. |
| 9 | Career diversity across the room (for the Day 5 comparison) | `day1.md:62` | **Handled** with a circulate-and-suggest facilitation tip. |
| 10 | Students keep Day 2 and Day 3 artifacts through Friday | `overview.md:95` | **Handled:** "Students should keep them in a folder across the week so the Day 5 submission is complete." |

| Code | Day | Item | Evidence (file:line) | What's needed |
|---|---|---|---|---|
| MISSING-PRINTABLE | 1 | Lifestyle Target page | `overview.md:35`, `day1.md:12,30-35` | Four lifestyle questions + a top-3 priority ranking with a one-sentence rationale each + a copy-down block for the six Rung 3 numbers. ELL variant = bilingual. |
| MISSING-PRINTABLE | 2 | Personal Budget Template (6-10 categories) **(tracked)** | `overview.md:32`, `day2.md:12,43-52` | Gross→net block, needs block (7 named rows), savings block (2 rows), wants/leftover line, balance line. Support variant = 5-category simplified; ELL variant = Spanish category labels. |
| MISSING-PRINTABLE | 2 | DFW Cost Reference Sheet **(tracked)** | `overview.md:33`, `day2.md:12`, `overview.md:102` | 1-page handout of DFW averages for rent, utilities, car, insurance, groceries, phone. Sample values are already worked at `day2.md:45-52` ($1,200 rent, $150 utilities, $350 car, $175 insurance, $150 gas, $350 groceries, $75 phone). |
| MISSING-PRINTABLE | 1 | Completed Rung 3 example set | `overview.md:104`, `day1.md:112` | See continuity row 4. Needs several careers so students who use it do not all end up with the same budget. |
| MISSING-PRINTABLE | 2 | Pre-filled Electrician budget example | `overview.md:100` | The full worked example already exists in prose at `day2.md:30-64`; needs typesetting onto the template. |
| MISSING-PRINTABLE | 3 | Cost of Living Comparison worksheet | `overview.md:34`, `day3.md:12,55-63` | 7 rows × 3 city columns + a leftover-income calculation. Support variant = cities pre-selected and rent/salary pre-filled. |
| MISSING-PRINTABLE | 4 | Paying for College notes sheet | `day4.md:12,47,83` | Must hold the four primary methods (FAFSA, scholarships, grants, work-study) plus the three additional sources added at `day4.md:83` (apprenticeships, 529 college savings, employer tuition benefits), plus a 2-3 sentence module takeaway. |
| MISSING-PRINTABLE | 5 | 3-Career Salary Comparison chart | `day5.md:12,55-59` | 3 rows × 6 columns + a "Value Score" weighting box. Support variant = one career row pre-filled as a worked example. |
| MISSING-SETUP | 4 | **NGPF / EverFi / Practical Money Skills all require teacher account provisioning; none is named** | `day4.md:12,28-45` | NGPF requires a verified free educator account (approval is not instant). EverFi FutureSmart requires a teacher account plus a class code and student roster. Practical Money Skills is the only one that is truly open-access. The plan gives three options and says "Teacher selects the module based on what is available at the school" but names no signup step, no lead time, and no fallback if none is provisioned by Day 4. |
| MISSING-SETUP | 3 | CareerOneStop Cost of Living tool | `day3.md:12,26-31` | The tool is public and the plan models it well, but the whole 30-min block runs on one external tool with no offline fallback. `day3.md:68` correctly warns against students Googling rent instead. |
| MISSING-SUPPLY | 2-3 | Calculators | `day2.md:12`, `day3.md:12` | Two days of percentage and division math. Named in Materials both days but not in any prep list. |
| MISSING-RUBRIC-OR-KEY | 5 | Portfolio summative (budget + cost-of-living + salary analysis) | `overview.md:95` | Three criteria, no levels. The "Value Score" at `day5.md:61` is explicitly student-weighted ("No single right answer"), which makes a rubric more necessary, not less. |

**Prep actions (roll-up):** Day 1: **author and print a small set of completed Rung 3 examples**, print the Lifestyle Target page ×30, have students bring workbooks · Day 2: print the Personal Budget Template ×30 + the DFW Cost Reference Sheet ×30 + the pre-filled Electrician example, source ~30 calculators, pick a demo career few students chose · Day 3: pre-run the CareerOneStop comparison for your demo career, print the Cost of Living worksheet ×30, decide the city menus · Day 4: **provision an NGPF or EverFi teacher account well ahead of this day** (or default to Practical Money Skills), print the Paying for College notes sheet ×30 · Day 5: print the 3-career chart ×30 + a worked example, collect Day 2 and Day 3 artifacts for the portfolio.

**Verdict:** RUNNABLE-WITH-PRINTING — 8 printables. The continuity handling is the strongest in the scope (four separate fallbacks), but the fallback the plan leans on hardest (the completed Rung 3 example set) does not exist, and the unverified assumption that H&L carries DFW-localized salary sits under the whole week.

---

## Week 5SW-6 — wk6-real-estate

| Code | Day | Item | Evidence (file:line) | What's needed |
|---|---|---|---|---|
| MISSING-PRINTABLE | 1 | Gallery Walk career profile cards (Agent, Broker, Appraiser, Property Manager) | `day1.md:12,56-61` | "Before class, post four career profile cards around the room." Full content for all four is written out at `day1.md:58-61` (income model, DFW median, license). Support variant = pre-filled Gallery Walk notes for one career (`overview.md:100`); ELL variant = bilingual summary labels. |
| MISSING-PRINTABLE | 2 | TREC Licensing Requirements handout | `overview.md:33`, `day2.md:12,32-41` | 8-row table, all content written out at `day2.md:34-41`. ELL variant = Spanish headers. |
| MISSING-PRINTABLE | 2 | Commission vs. Salary Comparison worksheet | `overview.md:31`, `day2.md:12,58-79` | Four sections: per-sale math (4 home prices), annual income at 3 sales volumes, comparison to a $70K salaried role, and a written reflection. All numbers are worked in the prose, so an answer key falls out of it. Support variant = a fully worked example calculation. |
| MISSING-PRINTABLE | 1 | Real Estate Career Research Sheet | `overview.md:32`, `day1.md:12,80-86` | The shared CCE format with an added "Income Model" field. |
| MISSING-PRINTABLE | 3 | Entrepreneurship Reflection template (1 page) | `day3.md:12,77-82` | Four prompts specced. Support variant = 3 short-answer boxes instead of the 1-page format. |
| MISSING-PRINTABLE | 3 | DFW Market Analysis notes section | `day3.md:65-69` | Three reasons DFW is strong / one factor that could slow it / one career opportunity. Referenced as part of Activity 2 but not in the Materials list. |
| MISSING-PRINTABLE | 4 | Market Trends Analysis notes sheet | `day4.md:12,42-50` | 7 fields × source column, plus three open questions at `day4.md:54-56`. Support variant = BLS data and home-price numbers pre-filled. |
| MISSING-PRINTABLE | 5 | 5SW Reflection Journal template | `day5.md:12,52-73` | Five sections including a 6-week week-by-week list and a 2-5 career fit ranking with cluster, education timeline, and DFW salary per career. |
| MISSING-SETUP | 4 | **Zillow / Realtor.com as a required data source with no fallback** | `overview.md:30`, `day4.md:12,29,45` | "Median DFW home price | Zillow DFW market page" is a required worksheet row. Real-estate listing sites are routinely blocked by district content filters (commercial/shopping category). The Texas Real Estate Research Center is named for other rows and could substitute, but the plan never says so. |
| REVISE | 4 | Data source contradiction with Day 3 | `day4.md:40,47-48` vs. `day3.md:55-56` | Day 4 says students "pull data from BLS, Zillow, and **teacher-provided news articles**," and two of the seven worksheet rows (Factor 1 and Factor 2 driving demand) name "News article" as the only source. Day 3 explicitly frames those articles as "**optional** enrichment, not required." A teacher who takes Day 3 at its word arrives Day 4 with two unfillable rows. |
| MISSING-RUBRIC-OR-KEY | 5 | 5SW Portfolio Check summative | `overview.md:92` | Spans four artifacts across two weeks (Wk5 budget, Wk5 cost-of-living, Wk6 research, updated reflection), four criteria, no levels. |
| MISSING-SUPPLY | 2 | Calculators | `day2.md:12` | Commission math across four home prices and three sales volumes. |
| STRUCTURE | — | Real Estate certification claim | `overview.md:41` | `[VERIFY with CTE coordinator]` on whether the MacArthur Real Estate Marketing pathway actually ends in the Real Estate Sales Agent credential. Known open item. |

**Prep actions (roll-up):** Day 1: **write and post four Gallery Walk cards before students arrive**, print the Real Estate Career Research Sheet ×30, bookmark the H&L Business/Marketing/Finance cluster · Day 2: print the TREC handout ×30 + the Commission worksheet ×30, pre-walk trec.texas.gov navigation (Education → Sales Agent Licensing → Requirements), source calculators · Day 3: print the Entrepreneurship Reflection template ×30 + the DFW Market notes, **decide whether you are curating news articles — Day 4 depends on it**, bookmark BLS + recenter.tamu.edu · Day 4: **test whether Zillow loads on the school network and pick a substitute if not**, print the Market Trends sheet ×30 · Day 5: print the 5SW Reflection Journal ×30, post the four FYF p. 299 presentation tips, project a 2-min timer.

**Verdict:** RUNNABLE-WITH-PRINTING — 8 printables, no supplies beyond calculators, no decks. The two real risks are the Zillow network dependency and the Day 3/Day 4 news-article contradiction.

---

## Scope summary

### Counts by code (12 weeks, 60 days)

| Code | Count | Notes |
|---|---|---|
| MISSING-PRINTABLE | 78 | Includes ~24 support/ELL variants named in Differentiation. Every one is fully specced in prose — this is production work, not design work. |
| MISSING-SETUP | 17 | 6 are `[VERIFY]`-flagged platform questions (known open items); 11 are unflagged. |
| MISSING-SUPPLY | 14 | Concentrated in 4 weeks: 4SW Wk3 (LEGO), 4SW Wk4 (drones), 5SW Wk1 (poster board), 5SW Wk2 (bridge kits). |
| MISSING-RUBRIC-OR-KEY | 18 | 12 summative rubrics (one per week, zero exist) + 6 activity answer keys. |
| STRUCTURE | 11 | 6 Climber Notes deck dependencies + the PATHWAYS.md/Pathways-poster gap + 4 district-info gaps. |
| REVISE | 10 | 5 period overruns, 3 broken cross-references, 2 internal contradictions. |
| MISSING-DECK | 5 | Foundation HS Program one-pager, real-airport images, conservation drone image, bridge-type comparison, 5SW cover slide. |
| PREP-ACTION | 60 | One per day, rolled up per week above. |

### The 5 worst gaps in this scope

1. **Six Climber Notes decks are load-bearing and unreachable from the website.** For "Unexpected Architecture" (5SW Wk1 D4), "Spot the Problem" (5SW Wk3 D4-5), and "PowerSkill Written Communication" (5SW Wk4 D2) I verified against the workbook extract that the student edition prints **nothing** for the step in question — FYF p. 182 literally says "Get Climber Notes from your teacher," FYF p. 177 prints empty observation boxes, and FYF pp. 187-190 print blank field-note forms. These are not enrichment; three named summatives depend on them. The decks are gitignored `.pptx` files. `resources-status.md` correctly documents the dependency, but documenting it is not the same as a teacher being able to open the file.

2. **4SW Wk2 cannot produce the year's d(8)(C) artifact from anything in the repo.** The H&L District Course Planner path is `[VERIFY]`-gated, and the paper fallback tells the teacher to use "the actual course names from the Irving ISD CTE poster" — a document that does not exist. I grepped `PATHWAYS.md`: it carries pathway names and certification targets only, no course sequences. Both routes to the 4-year course map dead-end. The bilingual Family Career Plan Letter (Day 3) is separately flagged by the plan's own `[VERIFY]` as possibly not existing; it does not.

3. **Four weeks are gated on class-set consumables nobody has confirmed:** ~8 LEGO sets + 6-8 aircraft per team (4SW Wk3, three days), ~8 drones + spares + a cleared flight space (4SW Wk4, two days), ~12 straw-bridge kits at 400+ straws (5SW Wk2, two and a half days), and ~30 sheets of poster board on a single day (5SW Wk1 D1). Nothing on the site tells a teacher whether the VILS labs already own the LEGO or the drones, and the only fallbacks offered are an unnamed flight-simulator app and "skip the extension."

4. **Zero summative rubrics across 12 weeks.** Every overview ends with "Scored on: [three to five criteria]" and stops. That includes the d(8)(C) Individual Career Plan (4SW Wk2), the 4SW Mid-Year Growth Reflection, and the 5SW portfolio. `cce-curriculum/notes/cfa-template.md` holds a 4-level rubric spec and the H&L teacher resources include a Daily Performance & Career Skills Rubric — neither is referenced from any week in this scope. Six activities also have no answer key where one is genuinely needed (the four truck diagnoses, the four HVAC tickets, the five inspection images).

5. **"H&L carries DFW-localized salary data" is the load-bearing assumption of the whole scope and is verified nowhere.** It is named as the primary source in 4SW Wk3 D2, 4SW Wk5 D3, 5SW Wk1 D2, 5SW Wk2 D1, 5SW Wk3 D1/D3, 5SW Wk4 D1/D3, 5SW Wk5 D1, and 5SW Wk6 D1. It is the input to the FYF Rung 3 "average in your area" line, which 5SW Wk5 D1 explicitly calls "the number the budget runs on." There is a `[VERIFY]` marker on Xello task names, on eDynamic unit numbers, on the H&L Career Plan tool, and on the District Course Planner — but none on this. If H&L returns national figures only, roughly a third of the scope's deliverables lose their data source at once.

### Cross-cutting patterns (named once instead of 60 times)

- **One worksheet, five weeks.** The "CCE career research worksheet" (6-field format taught in Wk0) is required in 4SW Wk3 D2, 5SW Wk1 D2, 5SW Wk2 D1, 5SW Wk3 D1, and 5SW Wk6 D1. Building it once clears five MISSING-PRINTABLE rows.
- **Every printable implies three.** Each named artifact is accompanied by a "pre-filled" support variant and a "bilingual / Spanish headers" ELL variant in the Differentiation block. Roughly 24 of the 78 MISSING-PRINTABLE rows are these variants. Any production plan should decide up front whether variants ship with v1.
- **Every presentation day names a listening grid that does not exist.** 4SW Wk3 D5, 4SW Wk4 D5, 4SW Wk5 D5, 4SW Wk6 D3, and 5SW Wk3 D5 all say "the class fills in a quick listening grid" or "note-taking sheet." Five instances, one generic template.
- **"Project X" with no X.** Five days say to project something no file supplies (Foundation HS Program summary, real-airport aerials, a conservation drone photo, a bridge-type comparison, an architecture cover slide). This is the same gap `resources-status.md` records as "Presentation Slides — ⬜ Not yet built," surfacing per-day.
- **Period overruns cluster in the back half of weeks.** Five days sum past 50 minutes: 4SW Wk2 D5 (53 as written), 4SW Wk4 D4 (53), 4SW Wk6 D4 (55), 5SW Wk1 D2 (55), 5SW Wk1 D5 (55). Notably, three days in this scope (4SW Wk5 D5, 5SW Wk1 D5, 5SW Wk3 D3) already carry excellent worked timing warnings with named alternatives — that pattern just has not been applied to the overruns above.
- **The Pathways poster problem.** "Irving ISD CTE Pathways poster (displayed in room)" appears in the Materials of eight days in this scope and is the stated fallback source of truth whenever H&L is unavailable. The underlying data lives in root `PATHWAYS.md`, which is not in `mkdocs.yml` nav and therefore invisible to a site-reading teacher. One printable poster (or one nav entry) fixes eight rows.
- **Platform single points of failure without fallbacks.** Xello Real Game (4SW Wk1 D3, 35 min), CareerOneStop (5SW Wk5 D3, 30 min), Zillow (5SW Wk6 D4), Indeed (5SW Wk4 D3), and NGPF/EverFi (5SW Wk5 D4) each carry a large block with no stated offline path. By contrast, 4SW Wk1 D2 and 4SW Wk2 D2/D3 all name explicit fallbacks — the practice exists in the codebase, it is just applied unevenly.
