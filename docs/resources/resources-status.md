# Resources Status & Backlog

**What this page is:** a living checklist of teacher-facing resources that are **ready to use**, **partially built**, or **still to be created** for the CCE Curriculum. This is the page to check when you want to know "what's missing before I can teach this week" or "what should I expect my teammates to build next."

**Last updated:** 2026-08-08. **All 36 weeks are realigned to the official *Find Your Future* workbook, have paired Canvas production packages, and have printable evidence sets.** Canvas is the official delivery environment; this site is the public review and backup surface. The live unpublished course is populated through 4SW Wk1. The 17 remaining 4SW Wk2-6SW Wk6 packages have passed credential-free preflight and are queued for unpublished import plus coursewide API/browser verification.

---

## Legend

- ✅ **Ready**: built, verified, and linked from the daily plans
- 🟡 **Partial**: exists but needs teacher polish, district customization, or platform confirmation
- ⬜ **Not yet built**: planned but not started; this is where we need decisions and authorship
- 🚫 **Out of scope**: intentionally not included

---

## Built & Ready (the current production set)

| Resource | Status | Where |
|----------|--------|-------|
| 36 Weekly Overviews (objectives, TEKS, materials, Week at a Glance, assessments, differentiation) | ✅ | `docs/{1-6}sw/wkN-*/overview.md` |
| 180 Daily Lesson Plans (warm-up, 2-4 activities with facilitation notes, exit ticket, differentiation) | ✅ | `docs/{1-6}sw/wkN-*/dayN.md` |
| Master Scope & Sequence (13-column pacing guide) | ✅ | [Scope & Sequence](../scope-and-sequence.md) |
| TEKS Coverage Matrix (every d(1)–d(8) standard mapped to its weeks) | ✅ | [TEKS Coverage Matrix](teks-coverage-matrix.md) |
| Free Resource Directory (BLS, Code.org, Canva, iCivics, etc.) | ✅ | [Free Resource Directory](free-resource-directory.md) |
| Source grounding (every workbook activity cites a page) | ✅ | Throughout daily plans. All six blocks cite the Irving *Find Your Future* workbook (realignment completed 2026-08-05) |
| Differentiation (Support / Extension / ELL + Spanish vocab) on every day | ✅ | Every daily plan |
| Facilitation Tip blocks (222 across the curriculum) | ✅ | Throughout daily plans |
| Printable exit-ticket PDFs (178, one per daily exit ticket, Irving ISD branded) | ✅ | `docs/resources/exit-tickets/`, linked from every day page |
| Printable worksheets, rubrics, references, and scaffolds for all 36 weeks (250 PDFs; strict source validation currently reports zero warnings) | ✅ | `docs/resources/worksheets/`; paired Canvas packages link or attach the aligned set |
| 1SW Common Formative Assessment (stimulus, 4 parts, 4-level rubric) | ✅ | [1SW CFA](../1sw/cfa.md) |
| Six-weeks grading framework (40% minor, 60% major; minimum 3 minor and 2 major grades) | ✅ | [Six-Weeks Grading Framework](grading-framework.md) |
| Authenticated Grade 8 Xello task list, prerequisite order, and teacher setup path | ✅ | [Xello Grade 8 Implementation Guide](xello-grade-8-implementation.md) |

### Exit-ticket PDF pipeline

Every daily exit ticket renders to a printable, Irving ISD branded PDF. 178 PDFs cover all 180 daily plans except 1SW Wk3 Day 3 and 1SW Wk5 Day 5, which have no exit ticket. Each day page carries a `[Printable PDF]` link next to its `**EXIT TICKET**` marker.

```bash
python3 build/build_pdfs.py         # regenerate every exit-ticket PDF
python3 build/inject_pdf_links.py   # refresh the [Printable PDF] links in day files
```

Operating manual: `cce-curriculum/notes/exit-ticket-pdf-pipeline.md`. Do not hand-edit the generated PDFs or the design CSS in `build/exit_ticket_template/`.

### Worksheet PDF pipeline (new 2026-08-05)

Classroom printables (worksheets, rubrics, contracts, references, and scaffolds) have their own generator. Sources are markdown files in `build/worksheet_sources/`; output lands in `docs/resources/worksheets/` with the same Irving ISD branding as the exit tickets. The current verified set has 250 PDFs and covers all 36 weeks. Response-space QA sizes fields from the writing or drawing job instead of forcing sentence reasoning into narrow table cells.

```bash
python3 build/build_worksheets.py            # regenerate every worksheet PDF
python3 build/build_worksheets.py --strict   # fail on page-fit warnings
```

Same operating manual, "Worksheet pipeline" section. Do not hand-edit the generated PDFs or `build/worksheet_template/`.

### Reference assets on hand

| Asset | What it is | Where |
|---|---|---|
| *Find Your Future* (FYF) workbook | The official Irving ISD student workbook, 308 pp., © 2026 Hats & Ladders. Tracked text extract alongside the gitignored PDF | `cce-curriculum/resources/reference-pdfs/IrvingFindYourFuture2026.txt` |
| Climber Notes decks | 17 teacher slide decks from H&L, including the two that carry the personality-type and work-values content the workbook does not print | `cce-curriculum/resources/climber-notes/` (see `INDEX.md`) |
| H&L teacher resources | 8 general teacher documents (rubrics, conversation starters, early-finisher activities, classroom displays) | `cce-curriculum/resources/hl-teacher-resources/` (see `INDEX.md`) |
| H&L generic workbook + Powerskills supplement | The pre-FYF source. **Retired as of 2026-08-05**: no week in `docs/` cites it any longer. Kept for history only | `cce-curriculum/resources/reference-pdfs/` |

A Hats & Ladders **teaching guide** (answer keys, timing, differentiation) has not been delivered. The Climber Notes speaker notes carry some facilitation guidance in its place.

### New hard dependencies from the Phase B realignment (2026-08-05)

Realigning 2SW and 3SW to *Find Your Future* introduced three supply requirements that did not exist before. These are not "nice to have" enrichment; the named days do not run without them.

| Week | What it needs | Why |
|---|---|---|
| **2SW Wk2 Days 2-4** (Law Enforcement / EMT) | The **Clinton Lake Case** Climber Notes deck (six evidence files, slides 2-7) and the **Injured on the Trail** Climber Notes deck (supply table plus the sling and finger-splint technique photos, slides 2-3) | Both decks are teacher-side only. The evidence files and the technique photos are not printed in the student workbook, so Days 2 through 4 have no content without them. Decks are on hand at `cce-curriculum/resources/climber-notes/` |
| **2SW Wk2 Days 3-4** (Law Enforcement / EMT) | **Per-pair first-aid supplies**: one triangular bandage or equivalent cloth for the sling, tape, and a popsicle stick or similar rigid splint for the finger | Students take turns as responder and injured hiker and physically apply a sling and a splint. Budget one set per pair, not one per class |
| **3SW Wk5 Days 1-3** (Cosmetology) | **Special effects makeup supplies**: tissue or cotton for texture, liquid latex or a school-safe adhesive alternative, cream or water-based color, tweezers, and a skin-safe base surface | Special Effects Makeup is the only FYF activity the workbook itself splits across three days, and Day 2 is a hands-on build. Check student allergies before ordering; the latex substitute is the usual accommodation |

Two Climber Notes decks are also load-bearing in Health Science: **Vitals in Motion** (2SW Wk3, the tool reference and the fever, blood pressure, and pulse oximeter charts) and **Smile Squad** (2SW Wk4, Mia's five X-rays). Their selected instructional visuals are embedded in the locked, unpublished Canvas modules with teacher guidance and accessible student routes. The source `.pptx` binaries remain gitignored and are not exposed on this public site.

### New hard dependencies from the Phase C realignment (2026-08-05)

Realigning 4SW, 5SW, and 6SW added four more deck dependencies and one scheduling load. Every deck named here has a gitignored Canvas-only delivery set and a paired module package; the 4SW Wk2-6SW Wk6 assets remain unpublished and await the live batch import/verification gate. Source `.pptx` binaries cannot be retrieved from the repo or public site.

| Week | What it needs | Why |
|---|---|---|
| **5SW Wk3 Days 4-5** (Construction Trades) | The **Spot the Problem** deck (five inspection images plus the regular-vs-thermal wall comparison, slides 2-6) | The home inspection images are teacher-side only. Without the projected images there is nothing for students to inspect, and the written inspection report on Day 5 has no source |
| **5SW Wk4 Day 2** (HVAC / Electrical / Plumbing) | The **PowerSkill Written Communication** deck (four service ticket photos, slides 2-5) | Students write four technician field notes from the photos. The workbook prints the format and the worked example but not the tickets |
| **5SW Wk4 Day 5** (HVAC / Electrical / Plumbing) | The **Plumbing Under Pressure** deck (slide 2) plus chart paper or poster board and markers, one set per team of 3 | Teams sketch and label the work zone before presenting the emergency plan |
| **4SW Wk3 Day 2** (Aviation) | The **Flight Line Fixers** deck (aircraft inspection photos, slides 2-6) | This is the only aviation activity in the workbook and it runs as an extension. If the deck is unavailable, skip the extension rather than improvising photos |
| **4SW Wk5** (Automotive) | The **Safety Squad** deck (crash evidence images, slides 2-5) | Enrichment block only, roughly two periods. Not required to run the scheduled five days |
| **5SW Wk1 Day 4** (Architecture) | The **Unexpected Architecture** deck (city goals, slide 2) | Firms design to the city council's stated goals, which are on the slide, not the page |
| **6SW Wk5 Days 1-5** (Job Skills / Mock Interview) | A **print packet**, not supplies: seven CCE artifacts per student, one set of Mock Interview Question Cards per pair, and a timer | This is the most workbook-independent week in the course. *Find Your Future* prints no interview, application, cover letter, or thank-you content, so the printed CCE artifacts are the entire source. Interviews are peer-to-peer, so no outside volunteers are needed, but pairs run in parallel and the room has to hold that |

---

## Still Needed (the teacher implementation backlog)

The paired Canvas packages and printable evidence sets now cover the core instructional route. The remaining backlog is live import/verification, publication setup, district-specific provisioning, materials/equipment readiness, and classroom-feedback refinements. A week is not fully "turnkey" until its Canvas package, files, interactions, and fallbacks pass teacher and Student View review.

### 🟡 Canvas Lesson Packages: Teacher Guide + Student Guide

**Status:** 🟡 All 36 paired packages are authored. The unpublished live course is populated and verified through 4SW Wk1; 4SW Wk2-6SW Wk6 remain queued for the credentialed batch import and live QA gate.

Every lesson needs two coordinated Canvas surfaces:

- **Teacher Facilitator Guide:** before-class setup, materials, learning target, time-boxed sequence, exact workbook and platform paths, what evidence to collect, grading, likely trouble spots, evidence-based language supports, and a platform/absence fallback.
- **Student Guide:** a plain-language purpose, materials, short numbered directions, a relevant screenshot or workbook excerpt, what to turn in, a "done" checklist, and enough support for an absent student to complete the activity without reconstructing the teacher's explanation.

The attached 2027 VILS Canvas export is the layout reference, especially its strong headers, visual cues, embedded examples, and short task blocks. Its legacy `enhanceable_content tabs` code is **not** the implementation standard because [current Canvas community guidance](https://community.canvaslms.com/t5/Canvas-Developers-Group/HTML-to-Create-Tabs-That-Work-for-Keyboard-Navigation/m-p/618344) identifies mobile and keyboard-accessibility problems. Use a readable single-column page and native disclosure sections for optional help, examples, vocabulary, or extensions. Keep essential directions visible.

**Reference implementation:** 1SW Wk0 Day 2 passed the desktop/mobile, disclosure, visual, and absence-route review and became the production grammar. Later packages add native Day subheaders, private multimodal Assignments, Student Annotation, retryable practice Quizzes, and limited Discussions where those interactions remove teacher work without weakening the evidence.

**Image rule:** screenshots and workbook crops must be instructionally necessary, tightly cropped, given useful alt text, and stored in authenticated Canvas when the source is licensed. Record the source and capture date so platform screenshots can be refreshed later.

### 🟡 Presentation and projection support

**Status:** 🟡 Integrated at the point of use; a separate deck for every week is intentionally not a universal requirement.

The native Canvas Student Guide can serve as the projection surface for warm-ups, numbered directions, source images, checks, and exit prompts. Licensed Climber Notes and Xello decks are embedded only where they carry unique evidence or materially reduce teacher explanation. A separate weekly deck should be added only when it improves pacing or visibility beyond the Canvas page; it is not a second copy of the same directions.

**Teacher-review question:** after classroom use, identify the small number of weeks where a projection deck would remove repeated scrolling or improve whole-class pacing. Build those from the existing Canvas content rather than maintaining 36 duplicate decks.

---

### 🟡 Assessment Worksheets (non-photocopiable artifacts)

**Status:** ✅ The 250-PDF production set covers the standalone worksheets, rubrics, reference cards, evidence packets, and scaffolds named by the 36-week Canvas build. Licensed workbook/deck pages remain in authenticated Canvas rather than being copied into the public set.

Completed examples include the 2SW Wk1 position-paper tools, 4SW Wk1 profile audit and blueprint rubric, 4SW Wk2 individual plan, 4SW Wk6 transfer/evidence set, 5SW architecture/trades/budget sets, 6SW résumé and job-skills packets, and the 6SW career-plan/capstone set. Keep print as an equal route, but prefer native Canvas annotation, typed, upload, or private media submission when that reduces copying and preserves the same evidence.

---

### 🟡 Common Formative Assessments (CFAs)

**Status:** 🟡 Pilot only. The 1SW CFA is drafted; 2SW-6SW are deliberately deferred until the first CFA is administered and teachers report on timing, clarity, item behavior, and scoring calibration.

**What's needed:** A Common Formative Assessment at the end of each six-weeks block (six total) that measures TEKS mastery for that block and produces data all VILS teachers share, so the district can see where the curriculum is and isn't landing.

**Scope per CFA:**

- 8–12 items measuring the TEKS standards claimed by that six-weeks block
- Mix of multiple-choice + short constructed response
- Answer key and scoring rubric
- Shared Google Form or printable version
- Teacher data-collection sheet (optional)

**Specifically needed:**

| Six Weeks | Weeks Covered | TEKS Standards to Measure | Status |
|-----------|--------------|----------------------------|--------|
| 1SW | Wk 0–5 (IT/Mfg + Career Self-Discovery) | d(1)(A-D), d(2)(A-B), d(5)(A,E), d(4)(B,F) | ✅ [1SW CFA](../1sw/cfa.md) |
| 2SW | Wk 1–6 (Law + Health Science) | d(1)(B-C), d(2)(A-B), d(3)(B-I), d(4)(A-F), d(5)(B,E) | ⬜ |
| 3SW | Wk 1–6 (Ag + Human Services + Business) | d(1)(C-D), d(3)(G-I), d(5)(C-E) | ⬜ |
| 4SW | Wk 1–6 (Career Planning + Transportation + STEM) | d(1)(C-D), d(3)(A-G), d(4)(A-B,F), d(8)(A-C) | ⬜ |
| 5SW | Wk 1–6 (Architecture/Construction + Finance) | d(1)(B-D), d(2)(A), d(3)(C-H), d(5)(A-E) | ⬜ |
| 6SW | Wk 1–6 (Education + Arts + Marketing + Capstone) | d(1)(C), d(4)(C,E), d(6)(A-C), d(7)(A-D), d(8)(A-C) | ⬜ |

**Open questions for teacher review:**

- Should the CFA be a 1-day pause at the end of each six-weeks block, or homework-style?
- Google Form auto-graded, or paper/pencil for data integrity?
- How do we handle CFAs for d(4)(C) oral presentation and d(6)(C) mock interview (performance rubrics rather than written items)?

---

### 🟡 Teacher Facilitator Guides and implementation support

**Status:** 🟡 Paired Teacher Facilitator Guides are authored for all 36 weeks; live import/verification is complete through 4SW Wk1 and pending for the remaining 17 modules.

The Teacher Guide page is the companion, so teachers do not have to cross-reference a separate book while teaching. It carries before-class setup, exact resources, the 50-minute flow and trim point, monitoring/key guidance, grading boundary, supports, and platform/equipment/absence routes. Remaining implementation support belongs in Canvas or a maintained teacher index rather than another disconnected document.

- classroom-tested "things that go wrong" notes after the first administration;
- bell-schedule variants if campuses use a different period length;
- substitute-teacher routes and a consolidated materials/equipment readiness list; and
- teacher feedback on which optional enhancements actually save time.

---

### 🟡 Student Packet / Workbook Supplement

**Status:** 🚫 A universal supplement is not planned. Use the 250 just-in-time printables or their Canvas submission equivalents.

Teachers may print a week-level packet when that fits the campus copy workflow, but Canvas remains the source of directions and files. Do not combine licensed H&L/Xello pages into a public or Git-tracked packet.

---

### 🟡 Video library (optional supplement)

**Status:** 🚫 Out of scope for now. Explicitly deferred by the team (2026-04-14) to avoid shoehorning videos that do not fit. Revisit after the first round of teacher feedback.

---

### 🟡 eDynamic + Xello platform verification

**Status:** 🟡 Xello's authenticated Grade 8 completion spine and captured resource set are reconciled. eDynamic and H&L remain supplemental unless a specific live activity is verified and assigned for an instructional purpose. Required Xello completion always remains a real platform task with supervised catch-up; paper supports learning but does not falsely count as completion.

**Action owner:** District admin / VILS program coordinator.

---

## How to add resources to this backlog

If you notice something missing while teaching, open a GitHub issue at [github.com/elbrielle/cce-curriculum/issues](https://github.com/elbrielle/cce-curriculum/issues) with the label `resource-backlog`. Include:

- What resource is needed
- Which week or day it connects to
- What you would use instead, temporarily
- Who should author it

The maintainer triages the backlog every 1–2 weeks and updates this page.

---

## What's NOT in the backlog (and why)

- **New activities**: the 180 daily plans are intentionally fixed until teacher feedback comes in. We fix what teachers say is broken, not what we imagine might be broken.
- **New weeks**: the scope and sequence is locked at 36 weeks aligned to TEKS §127.2. We do not extend without district curriculum approval.
- **Workbook rewrites**: the *Find Your Future* workbook is the source material. We cite it and defer to it; we don't rewrite it.
- **Video curation**: explicitly deferred (see above).
