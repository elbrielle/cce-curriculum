# 6SW + Year-Level Assessment Infrastructure — Day-1 Readiness Findings

Auditor scope: `docs/6sw/` (all 6 weeks, 36 files) + whole-repo assessment infrastructure (CFAs, semester assessment, gradebook guidance, rubrics roll-up).

Read in full: all 36 files of `docs/6sw/`, `docs/resources/resources-status.md`, `docs/1sw/cfa.md`, `cce-curriculum/notes/cfa-template.md`, both resource `INDEX.md` files, and FYF printed pp. 6, 22, 214-217, 225, 229, 244-245, 277-280, 287-289, 297-300 from the tracked extract.

**Blanket note applied throughout:** no artifact named "Printed X (CCE artifact)" exists anywhere in the repo. `git ls-files` returns zero template/handout/worksheet/rubric/card files. `docs/resources/` holds five markdown pages and 178 exit-ticket PDFs, nothing else. Every "MISSING-PRINTABLE" below is an authoring task, not a printing task.

---

## Week 1 — wk1-education

| Code | Day | Item | Evidence (file:line) | What's needed |
|---|---|---|---|---|
| MISSING-PRINTABLE | 1 | Community Classroom poster template | `docs/6sw/wk1-education/overview.md:34`; `day1.md:12,65,106` | Half-sheet poster frame: headline band + 3 pre-labeled bullet sections (concept / why teachers should book it / learning goals met) + bilingual stem strip. Chart paper is the stated alternative, so this is the low-lift one. |
| MISSING-PRINTABLE | 2 | Education Pathway Comparison worksheet | `overview.md:34`; `day2.md:12,57` | 6-row × 2-column table (time from HS, cost, when earning starts, one advantage, one disadvantage, shortage subjects) × Traditional / Alt-Cert. **Mitigated:** the exact table is reproduced at `day2.md:59-66`, so a teacher can build it in 5 minutes. Support version needs the Traditional column pre-filled (`day2.md:146`). |
| MISSING-PRINTABLE | 2 | CCE career research worksheet | `overview.md:35`; `day2.md:12,70-77` | Six fields, "taught in Wk0." **This is the year's most-reused missing artifact** — see cross-cutting P1. Fields are fully specced in-page. |
| MISSING-PRINTABLE | 3 | Practice Job Posting handout, 2 per student | `overview.md:36`; `day3.md:12,50-55` | Seven capture fields (title, location, where found, 2-3 responsibilities, skills, qualifications, education, experience). Must mirror the FYF Rung 5 layout exactly, because Wk5 grades the real rung pages against the same form. |
| MISSING-PRINTABLE | 3 | One completed Job Posting record as a model | `overview.md:111`; `day3.md:103` | A filled exemplar (an Irving ISD educational-aide posting is the named case). Nobody has written it. |
| MISSING-PRINTABLE | 4 | Community Service Reflection handout | `overview.md:37`; `day4.md:12,70-78` | Three-part page: 2-3 service experiences → skill each built → three sentence stems. Bilingual variant also promised (`day4.md:113`). |
| MISSING-PRINTABLE | 5 | "Education Hat" cheat sheet, 6 careers + salaries | `overview.md:110`; `day5.md:124` | Support scaffold for students who cannot navigate the app. No file. |
| STRUCTURE | 5 | Irving ISD CTE Pathways handout | `overview.md:48`(wk6); `day5.md:12,26,51` | The source is `PATHWAYS.md` at repo root — **not in `docs/`, not in mkdocs nav**. A site-reading teacher cannot reach it. `day5.md:51` also asks students to write "on the back of the handout," so a two-sided printable is assumed. |
| MISSING-DECK | 1 | Sample persuasive poster to project for 30 seconds | `day1.md:72` | No image exists; Climber INDEX has no Education deck. Teacher must source one cold. |
| MISSING-SETUP | 3 | A live local education job posting to project | `day3.md:30` | The anchor example for the whole 12-minute chunk is "a paraprofessional or educational aide opening on the Irving ISD careers page." If no such opening is live that week, the model dies. No cached/printed backup posting. |
| MISSING-SETUP | 3 | Xello: Discover Learning Pathways lesson | `day3.md:65-73` | No account-provisioning or lesson-assignment path on the page. No offline fallback. |
| MISSING-SETUP | 5 | eDynamic Unit 7.2 access | `day5.md:55-65` | Same. (The `[VERIFY IN eDynamic]` at `day5.md:65` is a known open item, not counted as a finding.) |
| MISSING-SUPPLY | 1,4 | Sticky notes (two days), chart paper/poster board + markers, scissors, tape per pair | `overview.md:31-32`; `day4.md:12` | Scissors are load-bearing on Day 4 — the fine-motor target skill IS cutting (`day4.md:34`), so one pair of scissors per pair of students, not one per class. |
| MISSING-RUBRIC-OR-KEY | 5 | Education Career Portfolio summative | `overview.md:103` | Five submitted pieces scored on three named dimensions with no instrument, no levels, no points. |

**Prep actions (roll-up):** Day 1: print poster templates; source and cue a sample persuasive poster; cue the H&L Education cluster tour video and mark the two Stop-and-Jot pause points; sticky notes on tables. · Day 2: print Pathway Comparison + career research worksheets (and the one-column-pre-filled support version); pull up the TEA certification page and Teach.org to project. · Day 3: print 2 Job Posting handouts per student + one completed model; **find a live Irving ISD aide/paraprofessional posting and have it open before the bell**; pre-bookmark the careers page and one job board on student Chromebooks (`day3.md:103`); confirm Xello logins. · Day 4: print Community Service Reflection handouts; lay out chart paper, markers, scissors, tape per pair; mark floor space for each pair's balancing test (`overview.md:81`); designate the supply return spot. · Day 5: print the Irving ISD CTE Pathways handout two-sided and the Education Hat cheat sheet; confirm eDynamic 7.2 is enabled; open the CTE-coordinator question on the Early Childhood credential (`day5.md:45`).

**Verdict:** RUNNABLE-WITH-PRINTING — but "printing" here means authoring five handouts first. No day is content-blocked; every artifact is fully specced in prose, and the two workbook Career Climbs (Community Classroom, Teach Through Play) run straight from the student book.

---

## Week 2 — wk2-graphic-design-resume

| Code | Day | Item | Evidence (file:line) | What's needed |
|---|---|---|---|---|
| MISSING-SETUP | 2,3,5 | Xello Resume Builder — **no working fallback** | `day2.md:12,63-78`; `day3.md:63`; `day5.md:75` | Days 2, 3, and 5 all run on the Xello Resume Builder, and the resume is the week's d(7)(A) summative. The stated fallback is the "printed Resume Template" (`day2.md:111`) **which does not exist**. If Xello logins fail on Day 2, a 28-minute activity has nothing behind it. This is the week's single point of failure. |
| MISSING-PRINTABLE | 2 | Resume Template (backup for Xello) | `overview.md:36`; `day2.md:12,111` | Six pre-labeled sections (header, career objective, education, skills, activities & awards, community service) + 20 sample skills menu (`day2.md:111`) + bilingual variant with Spanish headers (`overview.md:116`). |
| MISSING-PRINTABLE | 3 | Peer review form (Two Stars and a Wish) | `day3.md:12,77` | Two star lines + one wish line with the stems already posted at `overview.md:73`. **Mitigated:** "OR students write feedback directly on a sticky note" is an explicit alternative. |
| MISSING-PRINTABLE | 3 | Resume Revision Checklist | `day3.md:122`; `overview.md:73` | Five yes/no self-check questions, fully written in-page. Also used as the teacher's Day 2 clipboard (`overview.md:73`), so it needs a teacher-side copy too. |
| MISSING-PRINTABLE | 4 | Game Design Document template | `day4.md:132` | Nine pre-labeled fields (title through music & audio, `day4.md:46-55`) + sentence starters. Google Doc counts. |
| MISSING-PRINTABLE | 1 | Podcast episode outline template with the p. 271 checklist pre-laid | `overview.md:106`; `day1.md:127` | **Mitigated:** the checklist is printed in the student workbook (FYF p. 271, verified). This is a convenience layout, plus the sample interview questions named at `day1.md:127`. |
| MISSING-SETUP | 5 | Canva for Education accounts | `overview.md:29`; `day5.md:12,55` | Canva for Education requires teacher verification and a class join link. No setup path anywhere in the week. Adobe Express (`overview.md:30`) same. Day 5 Step 4 names Canva first and paper second, so paper is a real fallback here — unlike Xello on Day 2. |
| MISSING-SETUP | 4 | eDynamic Unit 8.2 access | `day4.md:93-95` | No access path. |
| MISSING-SUPPLY | 1,5 | Chart paper (one sheet per group of 3-4), sticky notes ×2 days | `overview.md:27` | Day 1's deliverable IS the chart-paper outline. |
| STRUCTURE | 1-5 | Climber Notes deck "Capturing the Feeling" | `cce-curriculum/resources/climber-notes/INDEX.md` (Decks with no counterpart) | INDEX flags it as an unidentified four-image photo-prompt deck, "Arts/AV candidate." 6SW Wk2 is the course's only Arts/AV week and never mentions it. Low confidence, but if it belongs anywhere it belongs here — and a site-reading teacher would never know a deck exists. |
| MISSING-RUBRIC-OR-KEY | 5 | Resume + Design Portfolio summative | `overview.md:98` | Three pieces, three named scoring dimensions, no instrument. |

**Prep actions (roll-up):** Day 1: chart paper per group, sticky notes, cue the Arts/AV cluster tour video and name both pause points, have the BLS Graphic Designers page ready (`day1.md:43`). · Day 2: **test Xello logins with 2-3 student accounts before the bell**; print Resume Template backups; have a fictional-student resume ready to build live on the projector (`day2.md:28`). · Day 3: print peer review forms + Resume Revision Checklists; prepare the first audio cue rewrite to model live (`day3.md:53`). · Day 4: print GDD templates; confirm eDynamic 8.2. · Day 5: confirm Canva for Education class link; find a well-known band/team shirt image for the 3-second-rule demo (`day5.md:63`); have FYF pp. 274-275 ready to project (`day5.md:86`).

**Verdict:** RUNNABLE-WITH-PRINTING **conditional on Xello.** If Xello Resume Builder is not confirmed live before Monday, Day 2 is BLOCKED — the named paper fallback does not exist.

---

## Week 3 — wk3-business-marketing

| Code | Day | Item | Evidence (file:line) | What's needed |
|---|---|---|---|---|
| MISSING-PRINTABLE | 1 | Blank ad mock-up sheet, 1 per student | `overview.md:32`; `day1.md:12,97` | Three pre-drawn labeled boxes (headline / short description / CTA) plus two margin lines for the placement and emphasis decisions (`day1.md:95`). Support version = same sheet with boxes labeled (`day1.md:131`). |
| MISSING-PRINTABLE | 1 | Twelve pre-written CTAs (3 per product), labeled by type | `overview.md:105`; `day1.md:131` | The named support scaffold requires a bank of exemplar CTAs across the four workbook products. Nobody has written a single one. This is a content gap, not a layout gap. |
| MISSING-PRINTABLE | 2 | Economic Conditions Analysis chart | `overview.md:36`; `day2.md:12,77` | **Mitigated:** the 5-row × 2-column table is reproduced at `day2.md:79-85`. Support version needs the "strong economy" column pre-filled (`day2.md:130`). |
| MISSING-PRINTABLE | 4 | Marketing career research worksheet | `overview.md:34`; `day4.md:12,41-48` | Same six-field CCE worksheet as Wk1 Day 2. See cross-cutting P1. |
| MISSING-PRINTABLE | 5 | Fill-in-the-blank pitch template | `day5.md:106` | Four-blank frame, written out in-page. Low lift. |
| MISSING-SETUP | 1-5 | Canva for Education | `overview.md:37`; `day1.md:12`; `day2.md:52`; `day3.md:12,53` | Used for ad mock-ups, the Little Library social post, and the Expert Edge logo. Paper is offered alongside in all three, so this degrades rather than fails. |
| MISSING-SETUP | 4 | Xello: School Subjects at Work | `day4.md:101-107` | No access path. |
| MISSING-SETUP | 5 | eDynamic Unit 4.1 | `day5.md:53-61` | No access path. |
| MISSING-SUPPLY | 2,3 | Sticky notes (Expert Edge skill brainstorm + Little Library brainstorm) | `overview.md:33`; `day2.md:12`; `day3.md:12` | |
| PREP-ACTION | 4 | Pre-highlight the two largest numbers per column in the FYF data tables | `overview.md:107`; `day4.md:142` | The tables are in the student book (verified, FYF p. 229). The support move means either pre-marking 30 workbooks or projecting a marked-up copy — neither exists. |
| MISSING-RUBRIC-OR-KEY | 5 | Marketing Plan Pitch summative | `overview.md:100` | Five-part 1-minute pitch scored on three named dimensions, no instrument, no levels. |

**Not a finding (good design, recorded so it isn't re-flagged):** the FYF page-transposition warning (pp. 228/230 swapped) is called out three times, once in the overview and once at each point of use (`overview.md:67-68`, `day1.md:49-50`, `day4.md:65-66`). Verified against the extract. This is the model for how workbook defects should be surfaced.

**Prep actions (roll-up):** Day 1: print ad mock-up sheets; **write the 12 exemplar CTAs** if you intend to run the support scaffold; cue the Business/Marketing cluster tour video and name both pause points; project FYF p. 254 during app navigation (`day1.md:41`). · Day 2: print Economic Conditions charts; find one real Instagram caption to project (`day2.md:67`); sticky notes. · Day 3: sticky notes; confirm Canva; be ready to rewrite one volunteer's offer live on the projector (`day3.md:55`). · Day 4: print marketing career research worksheets; pre-mark or project the highlighted data tables; confirm Xello. · Day 5: 60-second visible timer; notecards; confirm eDynamic 4.1; plan the parallel small-group pitch layout (`day5.md:42`).

**Verdict:** RUNNABLE-WITH-PRINTING. Four of the five workbook activities (Click Factor, Written Communication, Expert Edge, Data-Informed Decision Making) run entirely from the student book — the ads, data tables, and partner feedback form are all printed in FYF (verified pp. 225, 229, and p. 224 respectively). Only the CCE overlay is missing.

---

## Week 4 — wk4-sales-presentations

| Code | Day | Item | Evidence (file:line) | What's needed |
|---|---|---|---|---|
| **MISSING-RUBRIC-OR-KEY** | 3,4,5 | **Career Presentation Rubric** | `overview.md:32,98`; `day3.md:12,69,88`; `day4.md:12,68,83,127`; `day5.md:12,26,37,105` | Cited **11 times across four files** and it does not exist. The site names four criteria (content accuracy, organization, delivery, career connection — `overview.md:98`) and supplies level descriptors for **one** of them, borrowed from the FYF Presenter Delivery row (`day3.md:88`, verified FYF p. 280). Three of four criteria have no levels and no point values anywhere in the repo. Day 5 is the **year's primary d(4)(C) artifact** (`overview.md:98`). Students are also asked to self-rate on it (`day5.md:105`) and to peer-score with it (`day4.md:68`). **Top-5 gap.** |
| **MISSING-PRINTABLE** | 5 | **Rung 4 Strengths Interview take-home packet** | `day5.md:77`; `overview.md:66,100`; cross-ref `wk6-capstone/day1.md:56,68` | Rung 4 is assigned take-home; students write the adult's name in class and "everything else happens outside class." **The instructions, the five questions, the two-own-questions space, the Interview Notes box, and the Make Meaning page all live only on FYF pp. 287-289** (verified). With a *class set* of workbooks, the book cannot go home — and Wk6 Day 1 Active Monitoring lap 1 explicitly checks "the interview notes are actually written on page 288" (`wk6-capstone/day1.md:68`), which requires the book to have travelled. Needs a one-page take-home reproducing FYF p. 287's five questions + p. 288's notes space, plus an adult-facing cover note explaining what a Strengths Interview is and roughly how long it takes. **Top-5 gap.** |
| MISSING-PRINTABLE | 4 | Interview Appearance Guide, 1 per student | `overview.md:33`; `day4.md:12,26,40-46,126` | Four prompts (casual / business-casual / business-professional top-bottom-shoes, plus 5 things to avoid). `day4.md:29` states plainly this is **"the only place this course teaches d(6)(B)."** A standard rides entirely on a handout that does not exist. Support version needs one column pre-filled (`day4.md:126`). |
| MISSING-PRINTABLE | 3 | Career Presentation Outline template | `day3.md:12,69,131`; `overview.md:106` | Three-part frame (intro 30s / three key facts 2min / conclusion 30s). **Mitigated:** structure fully specced at `day3.md:73-85`. Partially-filled support version and bilingual version with Spanish starters also promised (`day3.md:131,133`). |
| MISSING-PRINTABLE | 3,4,5 | Bilingual presentation outline template | `overview.md:120`; `day3.md:133` | ELL scaffold, no file. |
| MISSING-DECK | 3 | 30-second teacher model of each presentation part | `day3.md:71` | "Deliver a 30 second teacher model of each part on the projector using a career the class has already studied." No worked model exists. Teacher improvises three of them cold. |
| MISSING-SUPPLY | 3 | Sticky notes for the BrainBoost brainstorm (10+ per group) | `overview.md:29`; `day3.md:12,46` | Ten notes per group is a real quantity. |
| MISSING-SETUP | — | CareerOneStop Practice Interview Questions | `overview.md:30` | Listed in Materials but never used by any Day 1-5 activity. Either wire it in or drop it — a teacher gathering materials will chase it. Minor REVISE. |
| PREP-ACTION | 5 | Choose the Day 5 compression approach in advance | `day5.md:42-49`; `day4.md:86` | Three options with the math worked (split groups / two days / 90-second slots). Well handled; the announcement requirement on Day 4 is explicit. |

**Not a finding (good design):** Day 5's timing admonition does the arithmetic (25 × 3 min vs. a 40-min activity) and gives three named approaches with a recommendation. `day4.md:86` requires announcing the chosen format before students leave Thursday. This is the strongest presentation-logistics writing in the block.

**Prep actions (roll-up):** Day 1: cue the FYF SparkClean example to read aloud twice (`day1.md:58`); BLS Sales Managers page. · Day 2: timer; have the SparkClean example ready to reproject with the benefit sentence underlined (`day2.md:47`); pick two anonymous drafts to read at 30s and 55s (`day2.md:50`). · Day 3: **author the Career Presentation Rubric**; print outline templates + rubrics; sticky notes ×10 per group; prepare three 30-second teacher models. · Day 4: **author and print the Interview Appearance Guide**; timer; decide and announce the Day 5 format. · Day 5: huge visible timer; rubric clipboard; **print the Rung 4 take-home packet + adult cover note**; help students who cannot name a trusted adult identify one on campus before they leave (`day5.md:113`).

**Verdict:** BLOCKED. Two named blockers: (1) the Career Presentation Rubric does not exist and Day 5 is the year's primary graded d(4)(C) artifact; (2) the Interview Appearance Guide does not exist and is the sole d(6)(B) carrier in the week. Days 1-3 of the workbook content run fine.

---

## Week 5 — wk5-job-skills-mock-interview

The repo's own status page already names this week as the one that needs "a **print packet**, not supplies: seven CCE artifacts per student, one set of Mock Interview Question Cards per pair, and a timer" (`docs/resources/resources-status.md:79`). Confirmed: **all seven are missing.** `overview.md:59` states the week is "the most workbook-independent week in the course" and that the printed templates "are the source, not the book."

| Code | Day | Item | Evidence (file:line) | What's needed |
|---|---|---|---|---|
| **MISSING-RUBRIC-OR-KEY** | 4,5 | **Mock Interview Rubric** | `overview.md:38,93,103`; `day4.md:12,80,88`; `day5.md:12,26,36,59,60,105` | Cited **12 times**. Four distinct uses of an instrument that does not exist: students score peers with it (`day5.md:36`), fishbowl observers score with it (`day4.md:88`), the teacher scores 2-3 students with it (`day5.md:60`), and Active Monitoring lap 3 checks "the interviewer is scoring the rubric" (`day5.md:59`). The nearest thing supplied is four observation categories with no levels and no points (`day4.md:90-93`). This is the **d(6)(C) summative instrument.** The eight H&L teacher resources contain no interview rubric (INDEX verified). **Top-5 gap.** |
| MISSING-PRINTABLE | 1,2 | Cover Letter Template | `overview.md:33`; `day1.md:12,83-91`; `day2.md:12,80,128` | Six labeled parts. **Best-supported of the seven:** a complete worked model letter is written out at `day2.md:30-67`. Sentence-by-sentence fill-in support version (`day2.md:128`) and bilingual version (`day2.md:130`) also promised. |
| MISSING-PRINTABLE | 3 | Sample Job Application form matching CareerOneStop fields | `overview.md:34`; `day3.md:12,26,79` | Seven sections specced at `day3.md:39-77`. **Partly mitigated:** the free CareerOneStop online practice application is offered alongside and "either one is the d(7)(C) artifact" (`day3.md:30`) — but `day3.md:34`'s privacy protocol (collect and shred all paper) assumes the paper form. |
| MISSING-PRINTABLE | 3 | References Guide | `overview.md:35`; `day3.md:12,118-122` | Three tasks (3 references + rationale each + draft permission email). Sample email supplied at `day3.md:126-131`. Bilingual variant promised (`day3.md:182`). |
| MISSING-PRINTABLE | 4 | Interview Readiness Guide | `overview.md:36`; `day4.md:12,26,28-33` | Four topics (six dress rules, getting ready, remote/phone interviews, follow up). `day4.md:28` says "it is the only place in the course where appearance for an interview is taught, so do not skip it" — a d(6)(B) carrier alongside Wk4's Appearance Guide, and neither exists. |
| MISSING-PRINTABLE | 4,5 | Interview Question Set | `overview.md:36`; `day4.md:12,46,50-72`; `day5.md:12` | Eight questions with per-question coaching tips, all written out in-page. Lowest-lift of the seven. |
| MISSING-PRINTABLE | 4,5 | Mock Interview Question Cards, 1 set per pair | `overview.md:38`; `day4.md:12,86`; `day5.md:12,36` | **Two-sided cards:** front = the question, back = "suggested answer frameworks" (`overview.md:115`) and Spanish translations (`overview.md:127`, `day5.md:139`). Nobody has written the answer frameworks or the translations. Quantity: one set per pair, ~13 sets. |
| MISSING-PRINTABLE | 5 | Thank-You Letter form / template | `day5.md:12,86,137` | **Mitigated:** the six rules and a complete sample are at `day5.md:77-103`. Fill-in-the-blank support version promised (`day5.md:137`). |
| MISSING-PRINTABLE | 1 | Printed sample job posting (Pecan Creek Vet Clinic) | `day1.md:12,71-79` | **Mitigated:** the full posting text is in-page at `day1.md:73-79`, copy-paste ready. |
| MISSING-PRINTABLE | 1 | Seven-step job search reference card with icons | `day1.md:133` | Support scaffold, no file. |
| MISSING-RUBRIC-OR-KEY | 3 | Rung 5 completeness score | `overview.md:107`; `day3.md:28` | "Collected at the start of Day 3 and scored for completeness" across seven fields × two postings. A field checklist is stated in prose; there is no scale, no point total, no partial-credit rule. |
| MISSING-RUBRIC-OR-KEY | 5 | Mock Interview + Professional Documents Portfolio | `overview.md:97-105` | Five submitted pieces verifying **six TEKS standards in one portfolio** — with no scoring instrument for any of them beyond the missing Mock Interview Rubric. |
| MISSING-SETUP | — | Xello Job Interviews lesson | `overview.md:30,122` | Listed in Materials; used only as an extension. No access path. |
| MISSING-SUPPLY | 5 | Timer; shredder access | `overview.md:40`; `day3.md:34` | The privacy protocol ("collect and shred all completed forms at end of class, do not send them home") requires a shredder the teacher may not have. |

**Not a finding (good design):** `day3.md:32-35` is the best safeguard writing in the block — an explicit student-privacy protocol (substitute a fictional identity, collect and shred, never leave on desks) plus an honest scope note that real applications take 30-45 minutes and this class has 15. Copy this pattern elsewhere.

**Prep actions (roll-up):** Day 1: **author and print all seven artifacts before the week starts**; print sample job posting; pre-load two Irving-area postings for students who get zero search results (`day1.md:133`); H&L logins. · Day 2: Google Doc open on the projector to build the cover letter live (`day2.md:28`); clipboard for the three monitoring laps. · Day 3: **collect Rung 5 pages at the door**; print application forms + References Guides; project CareerOneStop's practice application beside the paper form; secure a shredder. · Day 4: print Interview Readiness Guides + Question Sets; cut and assemble question card sets (~13); recruit a confident student volunteer for the fishbowl (`day4.md:104`). · Day 5: timer; question cards and rubrics distributed; **wear professional clothes and greet students at the door with a handshake** (`day5.md:65`); pair mixed (confident + nervous, ESL + bilingual).

**Verdict:** BLOCKED. Seven print artifacts named as "the entire source" for the week; zero exist. Days 2-5 have no student-facing material to run on. The specs are complete enough that a full day of authoring would unblock it, and Day 2's worked cover letter and Day 4's eight questions with tips mean two of the seven are nearly written already.

---

## Week 6 — wk6-capstone

Verified against the workbook extract: FYF p. 278 (eight rungs previewed), p. 279 (seven presentation formats + open option), **p. 280 (8 categories × 4 levels = 32 points)**, pp. 287-289 (Rung 4), pp. 297-298 (Rung 8), p. 299 (Prepare & Present: three-question check, the eight required presentation elements, four delivery tips), p. 300 (Final Reflection: four closing questions). Every site claim about these pages is accurate.

**Can a teacher actually grade with what's provided? Qualified yes.**

- The 32-point rubric **is** in the student workbook, so a teacher holding a class set has the instrument. The site does **not** reproduce it (`overview.md:45` explicitly instructs "Do not print a second CCE rubric"), and only the Presenter Delivery row's four levels appear anywhere in `docs/` (`wk4/day3.md:88`).
- What's missing is the **teacher side**: no score-recording sheet for 8 categories × 4 levels × 25 students, so a teacher scores live off a page in a student's book while that student is presenting. That is not workable at 12-13 presenters a day.
- `docs/resources/resources-status.md:118` still lists "**6SW Wk6: Capstone Career Plan presentation rubric**" as a needed artifact, which contradicts `overview.md:45`'s "do not print a second rubric." One of the two is stale.

**Presentation-day logistics: partially there.** Both days give worked timing math and three named compression approaches each (`day3.md:50-57`, `day4.md:30-37`); Time, Voice, Body defines presenter position and feedback-slip placement; the Pre-Capstone Teacher Checklist (`overview.md:94-104`) covers H&L access testing, Rung 4 counts, the Career Plan export dry-run, and Chromebook fleet coordination. **What's absent:** a running order / sign-up artifact, the feedback slips themselves, and a per-format tech checklist (who cues the video, where podcast audio plays, whether the document camera works).

| Code | Day | Item | Evidence (file:line) | What's needed |
|---|---|---|---|---|
| **MISSING-PRINTABLE** | 2 | **Written Career Plan template, eight sections** | `overview.md:44,129`; `day2.md:12,36,157` | The artifact that **goes home to the 9th-grade counselor** (`day2.md:36`, `day5.md:88`). Fully specced at `day2.md:40-88`, including the 4-year course grid with required courses already listed. Support version pre-fills the grid (`day2.md:157`); bilingual version with Spanish rung headers promised (`day2.md:159`, `overview.md:156`). **Top-5 gap** — this is the highest-value single printable in the block. |
| MISSING-RUBRIC-OR-KEY | 3,4 | Teacher score-recording sheet for the FYF 32-point rubric | `overview.md:45,75`; `day3.md:46`; `day4.md:40` | The rubric exists in the book; the teacher's tally sheet does not. Needs one row per student × eight category columns × 4/3/2/1, with a total-of-32 column. |
| MISSING-PRINTABLE | 5 | End-of-Year Reflection handout | `overview.md:46`; `day5.md:12,28` | Six sections specced at `day5.md:30-63`, wrapping FYF p. 300's four closing questions inside a 36-week review. Simplified guided version (`day5.md:134`) and bilingual version (`day5.md:136`) also promised. |
| MISSING-PRINTABLE | 3,4 | Peer feedback slips (Two Stars and a Wish) | `day3.md:59`; `day4.md:43` | TVB says "define... where feedback slips go." No slip exists. |
| MISSING-PRINTABLE | 3,4 | Presentation running order / sign-up sheet | `day3.md:28`; `day4.md:28` | "First half" and "second half" are named but never assigned. With three compression options in play, the teacher needs a posted order before Day 3 starts. |
| MISSING-PRINTABLE | 1 | Iceberg template | `day1.md:12,35` | **Mitigated well:** FYF pp. 7-8 print two blank iceberg frames (Electrician, Nurse), and `day1.md:129` names the Electrician frame as the lower-lift alternative. The CCE spec (3 items on top, 10 underneath) is in-page. |
| MISSING-PRINTABLE | 5 | Certificates of Completion | `overview.md:50`; `day5.md:76` | Explicitly optional and self-describing ("your school logo, 'CCE Course Completion 2026,' teacher signature"). Bilingual version promised (`overview.md:157`). |
| STRUCTURE | 1 | Week 0 My Career Journey reflections from the class folder | `overview.md:43,101`; `day1.md:12,18` | Day 1's warm-up opens on them. They depend on the 1SW Wk0 Day 5 Persistent Portfolio admonition having been executed nine months earlier, possibly by a different teacher. A first-year teacher will not have them. **Well flagged** at `overview.md:101`, but there is no stated substitute for Day 1 if the folder is empty (unlike the Rung 4 contingency at `day1.md:74-75`, which is excellent). |
| STRUCTURE | 5 | Irving ISD CTE Pathways guide (`PATHWAYS.md` printed) | `overview.md:48` | Repo-root file, not in `docs/`, not in mkdocs nav. Invisible from the site. |
| MISSING-SETUP | 3,4 | Document camera + speakers for comic / video / podcast formats | `day3.md:12,30`; `day4.md:12` | Students choose from seven formats on Day 2; three of them need playback hardware named only in the Materials line. No fallback if the room lacks a doc cam. |
| MISSING-SUPPLY | 2-4 | Paper, markers, rulers for comic/storyboard students; snacks (optional) | `overview.md:49`; `day5.md:12` | Quantity depends on Day 2's format choices, so this cannot be ordered until Day 2 ends. Worth a note in the plan. |
| REVISE | — | Rubric guidance contradicts the backlog | `overview.md:45` vs. `docs/resources/resources-status.md:118` | "Do not print a second CCE rubric" vs. "6SW Wk6: Capstone Career Plan presentation rubric" listed as needed. Reconcile — the correct answer is probably "the FYF rubric is the standard; what's needed is a teacher tally sheet." |

**Not findings (strong design, recorded so they aren't re-flagged):** the "Adapt to your end-of-year schedule" admonition (`overview.md:13-22`) proves every TEKS this week claims is already covered upstream and says "Zero days is fine" — the most honest piece of writing in the block. The Career Plan export contingency (`day4.md:62`) names the exact failure mode (24 simultaneous exports) and two fallbacks (browser print-to-PDF, screenshots emailed home) so "every student leaves with an artifact." That is the pattern the rest of the curriculum's platform dependencies should copy. The Rung 4 no-interview contingency (`day1.md:74-75`) is equally good.

**Prep actions (roll-up):** Before Day 1: run the entire Pre-Capstone Teacher Checklist (`overview.md:96-102`) — test H&L logins on 2-3 accounts, count completed Rung 4 interviews, line up a counselor/coach for the students with none, dry-run the Career Plan PDF export and document the steps, coordinate with tech to block OS updates, retrieve the Wk0 reflection folder, pick the Day 3/4 compression approach. · Day 1: print iceberg templates (or flag FYF p. 7); have Wk0 reflections sorted by student. · Day 2: **print Career Plan templates** (plus pre-filled-grid and bilingual variants); project FYF pp. 279-280; timer for 30-second test runs. · Day 3: post the running order; build the teacher tally sheet; print feedback slips; test doc cam and speakers; invite an administrator or counselor (`day3.md:62`); wear professional clothes. · Day 4: same tech check; protect the 17 minutes for Career Plan download + Rung 8; get photo permissions (`day4.md:48`). · Day 5: print End-of-Year Reflection handouts + certificates; queue soft instrumental music (`day5.md:66`); snacks.

**Verdict:** RUNNABLE-WITH-PRINTING. Grading is genuinely possible because the FYF rubric is in every student's hands, but the teacher needs a tally sheet and the Career Plan template authored first. The week is explicitly declared optional and TEKS-redundant, which lowers the stakes on everything above.

---

# PART 2 — Year-Level Assessment Infrastructure

## (a) CFAs — 1 of 6 exist

| | |
|---|---|
| **Spec** | `cce-curriculum/notes/cfa-template.md` — 4-part structure (Identify / Compare / Connect to Self / Forward Action), 20 minutes, ECR style, 4-level rubric plus 0, "score each part 0-4, then take the lowest score across all four parts as the overall CFA score." |
| **Built** | **One.** `docs/1sw/cfa.md` — complete and genuinely usable: stimulus, four parts with TEKS tags and per-part timing, four separate 4-level rubric tables (`cfa.md:63-89`), and teacher follow-up thresholds tied to specific reteach slots ("If >30% score ≤2 on Part C, the Wk0 → 1SW bridge is broken", `cfa.md:95-98`). |
| **Missing** | **Five.** 2SW, 3SW, 4SW, 5SW, and **6SW** are all ⬜ at `docs/resources/resources-status.md:147-151`. The 6SW CFA would need to cover d(1)(C), d(4)(C,E), d(6)(A-C), d(7)(A-D), d(8)(A-C). |
| **Discoverability** | mkdocs nav exposes exactly one line: `1SW CFA — Your IT Future: 1sw/cfa.md` (`mkdocs.yml:70`). There is no CFA landing page, and `cfa-template.md` lives in `cce-curriculum/notes/` (developer-facing, not on the site). A teacher browsing the site finds one CFA sitting under 1SW with no explanation of why 2SW-6SW have none, unless they happen to read the Resources Status page. |

**Two blockers on the 6SW CFA specifically:**

1. `resources-status.md:157` poses an unresolved design question that is exactly 6SW's problem: *"How do we handle CFAs for d(4)(C) oral presentation and d(6)(C) mock interview (performance rubrics rather than written items)?"* Both standards are 6SW's, and both of their performance rubrics are among the missing artifacts above. The 6SW CFA cannot be written until that is answered.
2. `cfa-template.md` has an explicit sequencing rule that has not been honored: *"Ship the first CFA, administer it, then collect teacher notes on timing, clarity, and rubric calibration before building 2SW-6SW. Do not batch-ship all six before any have been used."* School has not started, so the 1SW CFA has never been administered. By its own spec, CFAs 2-6 are correctly blocked — this is deliberate, not neglect.

**REVISE (stale spec):** `cfa-template.md` says "RIASEC" three times (Part C description, rubric level 4 descriptor, and the design note "Build the self-knowledge spiral into Part C"). `CLAUDE.md` and `cce-curriculum/resources/climber-notes/INDEX.md` both state that H&L's framework is *core personality types* (Doer, Analyzer, Creator, Helper, Persuader, Organizer) and that RIASEC letter codes must never appear in student-facing text. The shipped `docs/1sw/cfa.md` correctly uses "core personality type." The template is stale relative to the one CFA built from it, and whoever writes CFAs 2-6 will inherit the error.

## (b) Semester exams / final — none exist, none promised

Searched `docs/`, `cce-curriculum/scope-and-sequence.md`, and `PLANNING.md` for `semester exam`, `final exam`, `semester assessment`, `midterm`, `semester final`, `benchmark`. **Zero hits.** Every "semester" hit in `docs/` is either an incidental usage ("one semester of student teaching") or a goal-setting time horizon ("by the end of this semester, I will...").

- The scope-and-sequence has **no assessment column at all** — its 13 columns are Six Weeks, Week, CCE Topic, H&L Cluster, H&L Specific Activities, Supplemental Resources, Tech Integration, Xello Standards, eDynamic Unit, TEKS Standards, TEKS Codes, Notes, Facilitator Guide Filename.
- Nearest instruments: the **Mid-Year Growth Reflection** at `docs/4sw/wk6-trades-capstone/overview.md:95` (six-part reflection, not an exam, no rubric) and the **Three-Part Capstone Assessment** at `docs/6sw/wk6-capstone/overview.md:127-131` (written Career Plan + presentation + Final Reflection).
- The Capstone is the closest thing to a final, and the week it sits in is explicitly declared cuttable: *"Nothing here is critical to year-end TEKS coverage"* / *"Zero days is fine"* (`wk6-capstone/overview.md:15,22`).

**Finding:** if Irving ISD requires a semester exam grade or a final exam grade for a CTE elective, nothing in this repo produces one, and nothing in this repo says whether one is required. The absence is undocumented in either direction — that is the actual finding, not the absence itself.

## (c) Gradebook guidance — absent

All **36 of 36** weekly overviews carry a `## Formative Assessment` section and a `## Summative Assessment` section. Both are prose. Neither is enough to set up a gradebook.

- **Point values: 2 of 36 overviews, both in 1SW.** `docs/1sw/wk1-robotics-manufacturing/overview.md:100` ("5 points each, 20 points total," via the H&L Daily Performance rubric) and `docs/1sw/wk3-computer-science-it/overview.md:91` ("four criteria scored 4 to 1, 16 points total"). **Zero 6SW overviews carry a point value.**
- **Zero hits** across `docs/` for: `gradebook`, `grade book`, `weighting` (in a grading sense), `grading categor*`, `percent of the grade`, `points possible`, `major grade`, `minor grade`, `daily grade`, `test grade`.
- Nowhere does the repo state how many grades a six-weeks should produce, how a Formative item relates to a Summative item in a gradebook, or what proportion of the grade each carries.
- **178 exit tickets, no grading policy.** Every day but two produces a printable exit ticket, and nothing anywhere says whether they are graded, completion-scored, or diagnostic-only.
- The one place a data-use policy exists is the CFA — `cfa-template.md`'s "if more than 30% of students score 2 or below on any part, reteach that concept in the first two days of the next block" and `cfa.md:95-98`'s four named reteach triggers. That instrumentation exists for exactly one assessment out of the year's hundreds.

**Verdict:** a teacher setting up their gradebook in mid-August has to invent the entire scheme — category names, weights, point values, and how 178 exit tickets and 36 summatives map into six-weeks grades. Nothing in the repo helps.

## (d) Rubrics roll-up — every distinct rubric referenced anywhere in `docs/`

**In-page markdown table or a repo file = EXISTS. A bare mention = MISSING.**

### Exists and usable

| # | Rubric | Where it lives | Cited by | Note |
|---|---|---|---|---|
| 1 | **FYF Capstone Rubric** — 8 categories × 4 levels, 32 pts | Student workbook, FYF p. 280 (verified) | `6sw/wk6/overview.md:75`, `day2.md:120`, `day3.md:46`, `day4.md:40`; `6sw/wk4` delivery row only (`overview.md:64`, `day3.md:88`, `day5.md:37`); `1sw/wk5/overview.md:71`, `day3.md:63`; `4sw/wk2/overview.md:69` | EXISTS in the book, **not reproduced anywhere in `docs/`**. No teacher tally sheet. The course's only published multi-criterion rubric, and four separate weeks lean on it. |
| 2 | **1SW CFA per-part rubric** — 4 parts × 4 levels | `docs/1sw/cfa.md:63-89` | `docs/1sw/cfa.md` | EXISTS as in-page markdown. |
| 3 | **CFA 4-level ECR rubric spec** | `cce-curriculum/notes/cfa-template.md` | the CFA process | EXISTS but **developer-facing, not on the site**. |
| 4 | **H&L Daily Performance & Career Skills Rubric** — 4 categories × 5 levels, 20 pts/day | `cce-curriculum/resources/hl-teacher-resources/` | `1sw/wk1/overview.md:35`, `day5.md:77`; `2sw/wk2/overview.md:37`, `day4.md:81` | EXISTS but **repo-only → STRUCTURE**. Never cited by any 6SW day, though it fits several. |
| 5 | **H&L Project Assessment** — 100 pts across 5 weighted sections | `cce-curriculum/resources/hl-teacher-resources/` | **nothing in `docs/`** | EXISTS, repo-only, **entirely unused**. Would cover 6SW Wk1's Education Career Portfolio, Wk2's Resume + Design Portfolio, and Wk3's Marketing Plan Pitch with light adaptation. |
| 6 | **H&L Student/Teacher Assessment** — 100 pts, side-by-side self + teacher | `cce-curriculum/resources/hl-teacher-resources/` | **nothing in `docs/`** | EXISTS, repo-only, unused. |
| 7 | **H&L Daily Participation Assessment** | `cce-curriculum/resources/hl-teacher-resources/` | **nothing in `docs/`** | EXISTS, repo-only, unused. |
| 8 | **2SW Wk3 Day 4 "quick rubric"** — 3 yes/no checks | `docs/2sw/wk3-nursing-health-science/day4.md:83-87` | in-page | EXISTS (minimal, projector-ready). |
| 9 | **2SW Wk3 Day 3 3-checkpoint rubric** | `docs/2sw/wk3-nursing-health-science/day3.md:83-87` | in-page | EXISTS (minimal). |
| 10 | **6SW Wk1 Day 4 three-checkpoint clipboard** (Teach Through Play) | `docs/6sw/wk1-education/day4.md:58` | in-page | EXISTS (minimal). Explicitly authored because "the workbook prints no rubric for this activity." Good pattern. |
| 11 | **FYF podcast checklist as rubric** (5 parts) | Student workbook, FYF p. 271 | `6sw/wk2/day1.md:89` ("The workbook checklist IS the rubric") | EXISTS in the book. |
| 12 | **FYF Expert Edge partner feedback form** — rating + Clarity/Creativity/Persuasiveness | Student workbook, FYF p. 224 (verified) | `6sw/wk3/day3.md:59` | EXISTS in the book. |

### Partial — criteria named, no level descriptors

| # | Rubric | Where | Gap |
|---|---|---|---|
| 13 | **1SW Wk3 CCE 4-criteria presentation rubric, 16 pts** | `docs/1sw/wk3-computer-science-it/overview.md:91` | Four criteria named and a point total given; **no level descriptors written.** |
| 14 | **6SW Wk5 Rung 5 completeness score** | `6sw/wk5/overview.md:107`; `day3.md:28` | Seven fields × 2 postings named in prose; no scale, no total, no partial-credit rule. |

### Missing — bare mention only

| # | Rubric | Cited at | Consequence |
|---|---|---|---|
| 15 | **Career Presentation Rubric** | `6sw/wk4` × 11 references (`overview.md:32,98`; `day3.md:12,69,88`; `day4.md:12,68,83,127`; `day5.md:12,26,37,105`) | The **year's primary d(4)(C)** artifact has no instrument. Three of its four criteria have no levels anywhere. |
| 16 | **Mock Interview Rubric** | `6sw/wk5` × 12 references (`overview.md:38,93,103`; `day4.md:12,80,88`; `day5.md:12,26,36,59,60,105`) | The **d(6)(C)** summative has no instrument, and it is used four different ways (peer, observer, teacher, monitoring target). |
| 17 | **Position Paper rubric** | `docs/resources/resources-status.md:109` (2SW Wk1 Day 5) | Outside my week scope; listed in the roll-up for completeness. |
| 18 | **6SW Wk1 Education Career Portfolio** | `6sw/wk1/overview.md:103` | 5 pieces, 3 dimensions, no instrument. |
| 19 | **6SW Wk2 Resume + Design Portfolio** | `6sw/wk2/overview.md:98` | 3 pieces, 3 dimensions, no instrument. |
| 20 | **6SW Wk3 Marketing Plan Pitch** | `6sw/wk3/overview.md:100` | 3 dimensions, no instrument. |
| 21 | **6SW Wk5 Mock Interview + Professional Documents Portfolio** | `6sw/wk5/overview.md:97-105` | 5 pieces verifying **six TEKS standards**, no instrument. |
| 22 | **6SW Wk6 written Career Plan** | `6sw/wk6/overview.md:129` | Submitted Day 2; FYF p. 280 scores the *presentation*, not the written plan. |
| 23 | **6SW Wk6 Final Reflection** | `6sw/wk6/overview.md:131` | Submitted Day 5, no instrument. |
| 24 | **CFA rubrics, 2SW-6SW** | `docs/resources/resources-status.md:147-151` | Five missing (the rubric ships with the CFA, so this is one gap, not two). |
| 25 | **Teacher tally sheet for the FYF 32-pt rubric** | implied by `6sw/wk6/day3.md:46`, `day4.md:40` | The instrument exists; the recording sheet does not. |

**Bottom line on rubrics:** the course references **25 distinct scoring instruments**. Twelve exist (four of those only inside the student workbook, four more only inside the repo where a site-reading teacher cannot see them), two are half-written, and eleven are bare mentions. **Every one of 6SW's six weekly summatives except Wk6's is scored on named dimensions with no instrument** — and Wk6's works only because it borrows the workbook's published rubric.

---

## Scope summary

### Counts by code

| Code | 6SW weeks | Part 2 | Total |
|---|---|---|---|
| MISSING-PRINTABLE | 32 | — | **32** |
| MISSING-RUBRIC-OR-KEY | 10 | 11 (roll-up) | **21** |
| MISSING-SETUP | 12 | — | **12** |
| MISSING-SUPPLY | 7 | — | **7** |
| STRUCTURE | 5 | 4 (repo-only rubrics + CFA template) | **9** |
| MISSING-DECK | 3 | — | **3** |
| REVISE | 2 | 2 (stale RIASEC in `cfa-template.md`; rubric guidance contradiction) | **4** |
| PREP-ACTION | ~34 (rolled into per-week lists) | — | **~34** |
| VAGUE-SPEC | 0 | — | **0** |

**VAGUE-SPEC is genuinely zero, and that is the block's biggest strength.** Every missing artifact is specced well enough in the surrounding prose that a builder could produce it without a design conversation. The gap is authoring volume, not authoring ambiguity.

### The 5 worst gaps

1. **6SW Wk5's seven-artifact print packet does not exist, and the week has nothing else to teach from.** `overview.md:59` states outright that the printed CCE templates "are the source, not the book," because FYF prints no interview, application, cover letter, references, or thank-you content anywhere in 300 pages. Days 2-5 have zero student-facing material. `resources-status.md:79` already names this exactly right.
2. **The Mock Interview Rubric (12 references) and the Career Presentation Rubric (11 references) are both bare mentions** — and between them they carry **d(6)(C)** and the **year's primary d(4)(C)** artifact. The two highest-stakes performance assessments in the course have no scoring instrument. The Mock Interview Rubric is worse because four different actors are told to score with it (peer, fishbowl observer, teacher, and the monitoring lap target).
3. **Rung 4 Strengths Interview is assigned take-home with no take-home handout.** Assigned at `6sw/wk4/day5.md:77`; every instruction, question, notes box, and reflection prompt lives only on FYF pp. 287-289. With a class set of workbooks, the book cannot go home — and `6sw/wk6/day1.md:68` explicitly checks that the notes are written *on page 288*. Needs a one-page reproduction plus an adult-facing cover note. This one is small to fix and silently breaks the capstone's fourth rung if missed.
4. **The 6SW Wk6 written Career Plan template does not exist**, and it is the artifact the course sends home to the 9th-grade counselor for course registration (`day2.md:36`, `day5.md:88`). Eight sections including a pre-fillable 4-year course grid, all specced at `day2.md:40-88`. Highest value-per-hour printable in the block.
5. **No gradebook scheme exists at any level.** 36 formative sections and 36 summative sections of prose, 2 of 36 overviews with any point value (both in 1SW, none in 6SW), zero mentions of weighting or categories, 178 exit tickets with no stated grading status, and no semester or final assessment either existing or promised. A teacher opening the site in mid-August cannot set up a gradebook from anything in this repo.

### Cross-cutting patterns (named once, not 36 times)

- **P1 — One missing worksheet blocks a dozen-plus days.** The CCE career research worksheet (six fields: Name of Career / What Interests You / Brief Job Description / Education-Training Needed / Average Salary / Tools-Equipment-Skills) is described as "taught in Wk0" and reused by nearly every cluster week across all six blocks. In 6SW alone it is required at Wk1 Day 2 and Wk3 Day 4. It has never been built. It is the single highest-leverage artifact in the repo.
- **P2 — "Printed X" in a Materials list means "author this," and the page never says so.** 6SW names roughly 20 distinct CCE printables across six Materials lists; zero exist. `docs/index.md:8` and `resources-status.md` are honest about this, but neither is where a teacher looks on Monday morning. A line like "Printed Cover Letter Template (CCE artifact, 1 per student)" reads as *go to the shelf*, not *write this yourself*. Consider marking unbuilt artifacts inline.
- **P3 — Every 6SW summative names scoring dimensions and supplies no instrument.** Six weeks, six summatives; the only one a teacher can actually score is Wk6, and only because the workbook publishes its own rubric. See roll-up rows 18-23.
- **P4 — Platform dependency without a fallback, except once.** H&L, Xello, eDynamic, Canva for Education, and CareerOneStop are all assumed live. No week gives an account-provisioning path, and only one place in the entire block names a failure mode and a Plan B: the Career Plan export contingency at `6sw/wk6/day4.md:62` ("if simultaneous PDF export fails for 24 students... print to PDF via the browser dialog, OR take full-page screenshots... Every student leaves with an artifact"). That is the template the other dependencies need — most urgently 6SW Wk2 Day 2, where Xello carries a 28-minute activity and the named paper fallback does not exist.
- **P5 — Repo-only resources are invisible from the site.** `PATHWAYS.md` (cited as a printed handout in two 6SW weeks), the 17 Climber Notes decks, the 8 H&L teacher resources (**including three ready-to-use generic rubrics that would cover four of the six missing 6SW summatives**), and `cfa-template.md` are all absent from mkdocs nav. The H&L Project Assessment and Student/Teacher Assessment are cited by *nothing anywhere in `docs/`* despite being exactly the instruments the portfolio summatives need.
- **P6 — Prep actions are embedded in prose and never collected.** Cue this video, pre-bookmark that page, print 30 of these, find a live job posting, line up a counselor, block OS updates, secure a shredder. Only 6SW Wk6 has a consolidated checklist (`overview.md:94-104`) and it is excellent — the other five weeks would each benefit from the same treatment. The per-week prep roll-ups above are a first draft of those lists.
- **P7 — The block's writing quality is high and its safeguards are real.** Recorded so a fix pass does not flatten them: the FYF page-transposition warnings repeated at point of use (Wk3), the student-privacy and shred protocol on the practice application (`wk5/day3.md:32-35`), the worked timing math with three named compression options on three separate presentation days (Wk4 Day 5, Wk6 Days 3-4), the Rung 4 no-interview contingency (`wk6/day1.md:74-75`), and the "Zero days is fine" honesty of the capstone week's adaptation admonition (`wk6/overview.md:13-22`).
