# Resources Status & Backlog

**What this page is:** a living checklist of teacher-facing resources that are **ready to use**, **partially built**, or **still to be created** for the CCE Curriculum. This is the page to check when you want to know "what's missing before I can teach this week" or "what should I expect my teammates to build next."

**Last updated:** 2026-08-05 (Phase B FYF realignment closeout, 2SW + 3SW blocks)

---

## Legend

- ✅ **Ready**: built, verified, and linked from the daily plans
- 🟡 **Partial**: exists but needs teacher polish, district customization, or platform confirmation
- ⬜ **Not yet built**: planned but not started; this is where we need decisions and authorship
- 🚫 **Out of scope**: intentionally not included

---

## Built & Ready (the current live site)

| Resource | Status | Where |
|----------|--------|-------|
| 36 Weekly Overviews (objectives, TEKS, materials, Week at a Glance, assessments, differentiation) | ✅ | `docs/{1-6}sw/wkN-*/overview.md` |
| 180 Daily Lesson Plans (warm-up, 2-4 activities with facilitation notes, exit ticket, differentiation) | ✅ | `docs/{1-6}sw/wkN-*/dayN.md` |
| Master Scope & Sequence (13-column pacing guide) | ✅ | [Scope & Sequence](../scope-and-sequence.md) |
| TEKS Coverage Matrix (every d(1)–d(8) standard mapped to its weeks) | ✅ | [TEKS Coverage Matrix](teks-coverage-matrix.md) |
| Free Resource Directory (BLS, Code.org, Canva, iCivics, etc.) | ✅ | [Free Resource Directory](free-resource-directory.md) |
| Source grounding (every workbook activity cites a page) | ✅ | Throughout daily plans. 1SW, 2SW, and 3SW cite the Irving *Find Your Future* workbook; 4SW-6SW still cite the generic H&L workbook pending Phase C |
| Differentiation (Support / Extension / ELL + Spanish vocab) on every day | ✅ | Every daily plan |
| Facilitation Tip blocks (222 across the curriculum) | ✅ | Throughout daily plans |
| Printable exit-ticket PDFs (178, one per daily exit ticket, Irving ISD branded) | ✅ | `docs/resources/exit-tickets/`, linked from every day page |
| 1SW Common Formative Assessment (stimulus, 4 parts, 4-level rubric) | ✅ | [1SW CFA](../1sw/cfa.md) |

### Exit-ticket PDF pipeline

Every daily exit ticket renders to a printable, Irving ISD branded PDF. 178 PDFs cover all 180 daily plans except 1SW Wk3 Day 3 and 1SW Wk5 Day 5, which have no exit ticket. Each day page carries a `[Printable PDF]` link next to its `**EXIT TICKET**` marker.

```bash
python3 build/build_pdfs.py         # regenerate every exit-ticket PDF
python3 build/inject_pdf_links.py   # refresh the [Printable PDF] links in day files
```

Operating manual: `cce-curriculum/notes/exit-ticket-pdf-pipeline.md`. Do not hand-edit the generated PDFs or the design CSS in `build/exit_ticket_template/`.

### Reference assets on hand

| Asset | What it is | Where |
|---|---|---|
| *Find Your Future* (FYF) workbook | The official Irving ISD student workbook, 308 pp., © 2026 Hats & Ladders. Tracked text extract alongside the gitignored PDF | `cce-curriculum/resources/reference-pdfs/IrvingFindYourFuture2026.txt` |
| Climber Notes decks | 17 teacher slide decks from H&L, including the two that carry the personality-type and work-values content the workbook does not print | `cce-curriculum/resources/climber-notes/` (see `INDEX.md`) |
| H&L teacher resources | 8 general teacher documents (rubrics, conversation starters, early-finisher activities, classroom displays) | `cce-curriculum/resources/hl-teacher-resources/` (see `INDEX.md`) |
| H&L generic workbook + Powerskills supplement | The pre-FYF source, still cited by 4SW-6SW until Phase C lands | `cce-curriculum/resources/reference-pdfs/` |

A Hats & Ladders **teaching guide** (answer keys, timing, differentiation) has not been delivered. The Climber Notes speaker notes carry some facilitation guidance in its place.

### New hard dependencies from the Phase B realignment (2026-08-05)

Realigning 2SW and 3SW to *Find Your Future* introduced three supply requirements that did not exist before. These are not "nice to have" enrichment; the named days do not run without them.

| Week | What it needs | Why |
|---|---|---|
| **2SW Wk2 Days 2-4** (Law Enforcement / EMT) | The **Clinton Lake Case** Climber Notes deck (six evidence files, slides 2-7) and the **Injured on the Trail** Climber Notes deck (supply table plus the sling and finger-splint technique photos, slides 2-3) | Both decks are teacher-side only. The evidence files and the technique photos are not printed in the student workbook, so Days 2 through 4 have no content without them. Decks are on hand at `cce-curriculum/resources/climber-notes/` |
| **2SW Wk2 Days 3-4** (Law Enforcement / EMT) | **Per-pair first-aid supplies**: one triangular bandage or equivalent cloth for the sling, tape, and a popsicle stick or similar rigid splint for the finger | Students take turns as responder and injured hiker and physically apply a sling and a splint. Budget one set per pair, not one per class |
| **3SW Wk5 Days 1-3** (Cosmetology) | **Special effects makeup supplies**: tissue or cotton for texture, liquid latex or a school-safe adhesive alternative, cream or water-based color, tweezers, and a skin-safe base surface | Special Effects Makeup is the only FYF activity the workbook itself splits across three days, and Day 2 is a hands-on build. Check student allergies before ordering; the latex substitute is the usual accommodation |

Two Climber Notes decks are also now load-bearing in Health Science: **Vitals in Motion** (2SW Wk3, the tool reference and the fever, blood pressure, and pulse oximeter charts) and **Smile Squad** (2SW Wk4, Mia's five X-rays). Both are already in the repo.

---

## Still Needed (the teacher implementation backlog)

The daily plans describe WHAT students do and give the facilitation approach, but they intentionally do **not** include the student-facing artifacts that teachers would photocopy, project, or print. Those are the items below. A week is not fully "turnkey" for a new teacher until its checklist here is green.

### 🟡 Presentation Slides (per week)

**Status:** ⬜ Not yet built.

**What's needed:** A slide deck per week (or per day) the teacher can project for warm-ups, cluster tour videos, vocabulary introductions, activity directions, and the exit ticket. Right now the daily plans say things like "project the Safety Supervisor scenario on the board" without an actual slide to project.

**Open questions for the teacher review:**

- Do teachers want one deck per week or one per day?
- Google Slides or Canva? (Canva matches 6SW Wk2 content; Google Slides is faster to edit and shares cleanly on district accounts.)
- Should slides include the warm-up prompt, vocabulary, activity directions, and exit ticket, or just the visuals?
- Do teachers prefer branded slides (IISD logo, CCE title) or minimal?

---

### 🟡 Assessment Worksheets (non-photocopiable artifacts)

**Status:** 🟡 Partially addressed. Exit tickets are covered by the PDF pipeline above. Daily plans also reference specific workbook pages (photocopiable when allowed by the H&L license), but some activities require separate worksheets that do not live in the workbook.

**Examples from the curriculum that need a printable artifact:**

- **1SW Wk0 Days 4-5**: My Career Journey reflection handout (persistent across the year) + the CCE career research worksheet reused by every cluster week
- **2SW Wk1 Day 5**: Position Paper rubric + final-draft template
- **4SW Wk1 Day 1**: RIASEC vs. Favorites reconciliation worksheet
- **4SW Wk2 Day 5**: Individual Career Plan template (the official d(8)(C) artifact)
- **4SW Wk6**: Transferable Skills Matrix, STEM Program planning chart, Professional Associations Jigsaw template, Mid-Year Reflection template
- **5SW Wk1 Day 2**: Architecture Career Research worksheet
- **5SW Wk4 Days 1–4**: Skilled Trades Comparison Matrix (the week's summative)
- **5SW Wk5 Days 1–4**: Personal Budget Template + DFW cost reference sheet
- **6SW Wk2**: Resume Builder template (Xello-native, but printable backup needed)
- **6SW Wk5**: Cover Letter template, Mock Interview rubric, Reference sheet
- **6SW Wk6**: Capstone Career Plan presentation rubric

**Open questions:**

- Which of these can be photocopied directly from the H&L workbook (and under what license)?
- Which need to be recreated as standalone Google Docs / printable PDFs?
- Should we build one master "Student Artifacts" folder in the Drive, organized by week?

---

### 🟡 Common Formative Assessments (CFAs)

**Status:** 🟡 Partial. 1 of 6 built.

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

### 🟡 Teacher Edition / Facilitator Guide (companion doc)

**Status:** ⬜ Not yet built.

**What's needed:** A teacher-only companion doc (not on the public site) that contains the items below. Partially mitigated by the 8 H&L teacher resources and the 17 Climber Notes decks now in `cce-curriculum/resources/`, which carry rubrics and some facilitation guidance but no answer keys.

- Answer keys for every worksheet and CFA
- "Things that go wrong" notes from classroom experience (once we have them)
- Bell schedule variants (if any VILS lab runs a different period length)
- Substitute-teacher plans for each week
- Materials ordering checklist per six-weeks block

---

### 🟡 Student Packet / Workbook Supplement

**Status:** ⬜ Not yet built (and possibly not needed).

**What's needed:** A short printed packet with the handouts for the weeks where students need paper artifacts the H&L workbook does not cover. Could be a single-semester packet or a per-six-weeks stapled mini-packet.

**Open questions:**

- Do we want to print and distribute packets at the start of each six-weeks block, or lean on just-in-time single worksheets?
- Does H&L allow us to photocopy their workbook pages into a consolidated teacher packet, or is their license individual-use only?

---

### 🟡 Video library (optional supplement)

**Status:** 🚫 Out of scope for now. Explicitly deferred by the team (2026-04-14) to avoid shoehorning videos that do not fit. Revisit after the first round of teacher feedback.

---

### 🟡 eDynamic + Xello platform verification

**Status:** 🟡 Partial. ~15 `[VERIFY IN eDynamic]` callouts and ~5 `[VERIFY IN Xello]` callouts remain in the daily plans. Each is a platform-access question: "confirm this unit/task still exists and is enabled in the district license." Resolution requires district admin login, not curriculum writing.

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
