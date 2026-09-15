# CCE Canvas Grounding Audit — 2026-09-14

Scope: live Canvas course 98060 (dumped 2026-09-14), repo `27 CCR Planning` at `de9f195d`, the 180 student Google Docs, and the FYF workbook extract. Read-only. No Canvas, Drive, or git writes were made.

Detail reports (same folder, `.tmp/audit-20260914/`):
- `response-route-collapse.md` + `.csv` — 180-row table, one row per day
- `hqim-terminology.md` + `hqim-occurrences.csv` — 286 occurrences classified
- `ss-fyf-grounding.md` + `fyf-citation-check.csv` — 415 citation checks

---

## 1. The Wk2 salary packet is not one gap. It is the design of the response-route migration.

**Mechanism (confirmed in code and live pages).** On 2026-08-26, `build/canvas/repair_student_google_copy_buttons.py` retargeted every "student response work PDF" anchor on every STUDENT page to that day's single Google Doc `/copy` URL (registry: `build/google_docs/student_response_route_registry.json`, one doc per day, 180 docs). The docs were generated from the exit-ticket template only. Every one of the 180 docs is a one-page exit ticket / mini-case (the live 1SW Wk2 Day 2 doc is exactly the "local Irving business wants to hire ONE person" scenario you described). No doc reproduces a worksheet.

**1SW Wk2, as students see it right now:**

| Day | Button label on student page | What it actually opens |
|---|---|---|
| Day 2 | "Open the five-page salary packet" | Day 2 exit ticket (Google Doc `15MLWoa…`) |
| Day 2 | "Open the Day 2 exit ticket" | same Google Doc |
| Day 3 | "Open the Flip the Failure scaffold" | Day 3 comparison-matrix exit ticket (`1jua53…`) |
| Day 3 | "Open your five-page salary packet" | same Google Doc |
| Day 3 | "Day 3 comparison matrix" | same Google Doc |
| Day 5 | (Minor 2 asks for the five-page packet, p. 5 reflection) | packet linked nowhere |

The packet itself exists: `docs/resources/worksheets/wk2-it-salary-comparison.pdf` (5 pages, source `build/worksheet_sources/wk2-it-salary-comparison.md`, "Use this same packet on Days 2, 3, and 5") and is uploaded to Canvas as file **14580354**, unlocked. It is linked from exactly one page in the course: the (unpublished) Day 2 Teacher Facilitator Guide. The Day 3 and Day 5 facilitator guides do not link it either. OneNote status in the registry is `pending` for 180/180 days, so there is no OneNote copy.

**Coursewide numbers.**
- 185 anchors were retargeted; **177 pointed at worksheets**, 8 at exit tickets.
- **170 of 180 days lost at least one student-reachable artifact.** 193 distinct PDFs are now reachable from no student page (183 worksheets, 7 exit tickets, 3 on no page at all). Clean days: 1SW Wk0 D2/D3/D5, Wk1 D3/D5; 3SW Wk1 D1, Wk2 D1, Wk3 D1; 4SW Wk4 D2.
- 15 days had 2–4 different PDFs collapsed onto one doc (1SW Wk1 D1; Wk2 D1/D2/D3; Wk3 D1/D2/D4; Wk4 D2/D3/D4; 2SW Wk1 D4; 3SW Wk3 D4; 3SW Wk5 D3; 5SW Wk4 D5; 6SW Wk2 D5, where four packets share one branding mini-case).
- **Broken multi-day chains** (a later day says "reopen the packet from Day N" and the packet is on no student page): 1SW Wk2 D3/D5 → salary packet; 2SW Wk5 D5; 3SW Wk6 D3; 4SW Wk3 D5 → four-page Action Plan; 5SW Wk3 D5 → five-page evidence report; 5SW Wk4 D3; 6SW Wk6 D2. 53 student pages carry "keep this / same packet" cues; 51 of them lost the artifact that day.
- Of 262 worksheet PDFs, 149 are now teacher-guide-only, 8 are on no page at all, 2 were never uploaded (`wk5-flyer-peer-feedback.pdf`, `wk5-integrity-reflection-stems.pdf`).

**Why nobody else flagged it.** 1SW Wk0–Wk2 are the only published modules; Wk2 Day 2 is the first day whose worksheet is a multi-day, graded packet rather than a same-day scaffold. Everything earlier degrades gracefully.

**Stale-snapshot note.** The subagent flagged five docs (1SW Wk0 D3/D4/D5, Wk3 D3, Wk5 D5) as containing the Wk0 Day 2 "Who Are You at Work?" ticket. I checked live: those were regenerated 2026-08-26 00:34 and are correct now. The rest of the snapshot matches live on every doc I spot-checked (2SW Wk2 D2, 4SW Wk3 D2, 1SW Wk2 D2/D3).

## 2. BLS is taught once, and the only bls.gov links are on orphan pages

1SW Wk2 Day 3 is the first and only day that teaches BLS extraction (occupation title, national median + year, typical entry education, outlook % + years, and the "keep national and local figures separately labeled" rule). 24 later days apply BLS without re-teaching it. No module-linked student page links bls.gov; Wk2 Day 3 routes students to the uploaded "BLS guide" PDF (file 14580356) instead. The only two bls.gov links sit on orphan pages (`…wk0-day-5-catch-up-or-research-careers`, `…4sw-wk1-day-3-career-deep-dive`). The teacher-facing day.md links bls.gov; that never made it to the student template.

## 3. "HQIM" — 286 occurrences, and it means three different things

| Class | Meaning | Count | Right replacement |
|---|---|---|---|
| A | Hats & Ladders specifically | 7 | "Hats & Ladders" / "H&L" |
| B | The app's localized salary figure, H&L **or** Xello (the packet field literally prints `Platform: H&L / Xello`) | 91 | needs a phrasing call: "Hats & Ladders or Xello", or "the app" |
| C | District policy term in dev notes / CLAUDE.md / S&S | 69 | leave |
| D | The printed *Find Your Future* workbook (always beside an `FYF pp.` cite: "District HQIM \| FYF pp. 24-25", "Use the HQIM program names") | 119 | "your workbook" / "Find Your Future" — replacing with H&L would be wrong |

Where it lives: Canvas student pages 15 (1SW Wk2 D2 ×6, D3 ×4, 4SW Wk5 D4 ×5), Canvas teacher pages 26, student PDFs 15, builders/templates 118, lesson markdown 50. Zero in the Google Docs, assignments, quizzes, module titles, or exit-ticket PDFs. **Every Canvas occurrence traces to a repo source**, so the fix is source-side plus re-push, not hand edits: `templates/wk2-day2-student.html`, `wk2-day3-student.html`, `build_wk2.py` L189–268, `build_wk1.py` L205–206, `build_wk4.py` L180, `build_2sw_wk3.py`, `build_4sw_wk2.py`, `build_4sw_wk4.py`, `build_4sw_wk5.py` L601–667 and L747–761, plus 12 day.md files and the Safe-or-Spoofed deck source credits.

Other student-facing jargon found on the way: "Demonstration of Learning"/DOL on 15 student pages; TEKS codes on 4 student pages (and 309 times inside rubric PDFs); "licensed workbook pages / licensed images / licensed brief" on 28 student pages, mostly 5SW–6SW; 5E phase names: zero (clean).

## 4. Scope & sequence and FYF grounding: structure is right, delivery to students is not

**Grounded.** 36 weeks + Wk0 map 1:1 to 37 Canvas modules in S&S order, each with 5 student pages, 5 facilitator guides, coherent Minor/Major spine. `cce-curriculum/scope-and-sequence.md` and `docs/scope-and-sequence.md` are byte-identical. All 369 printed-page citations across all 180 day.md files resolve to the right FYF page (PDF = printed + 6); zero wrong page numbers.

**Not grounded at the student surface.**
- 33 days cite FYF pages in day.md and cite nothing on the student page; 17 more disagree on which pages to open. Six whole weeks put no workbook page in front of students: 1SW Wk4, 2SW Wk1, Wk2, Wk3, 5SW Wk5, Wk6.
- H&L platform instruction collapses after 1SW Wk2: only 6 `[H&L PLATFORM]` markers exist in 180 day files (all 1SW) and only 9 student pages mention Hats & Ladders at all. Decision D-8 (App Exploration / District pages) reaches students on 2 of 13 and 6 of 14 pages.
- **1SW Wk2 Day 2's p. 38 citation is misapplied.** FYF p. 38 (PDF 44) is the IT "App Exploration": Clusters → Information Technology → Cluster Tour video → Game Time → 1 fit / 1 non-fit Hat → Pathway Possibilities → rate 3 Hats. That is what Wk2 **Day 1** teaches. Day 2 sends students to Programming and Software Development → Hat Finder for four Hats, which p. 38 never names, and the Day 2 student page cites no workbook page at all. This matches what you observed: the class is doing p. 38 work while the plan claims it is a different day.
- Specific misfires: 3SW Wk5 D2 student page says p. 129, day.md and the workbook's own "DAY 2" header say p. 130; 3SW Wk6 D1 gives students only the optional p. 254 and drops required p. 221 and pp. 252–253; 5SW Wk6 D3's "required workbook spine" pp. 238–239 is absent from the student page; 4SW Wk1 D3 and 6SW Wk2 D3 have their FYF-grounded version on an orphan page outside the module.
- 23 orphan student pages exist outside any module; one (`student-1sw-wk0-day-5-xello-and-career-perks-and-quirks`) is published.
- 1SW Wk1 D1–2 and Wk2 D1–3 are published to students while every facilitator guide is unpublished. Fine for your section; the other teachers importing this see student pages with no teacher guide.

Published-state check: 24 published items in 3 modules; all 41 linked files exist, none locked or hidden.

---

## 5. Proposed fix plan (nothing executed; needs your call)

**Decision 1 — what a student "response home" is.** The one-button-per-day rule in CLAUDE.md was applied as "one document per day." Multi-day packets and same-day scaffolds cannot survive that. Options:
- (a) Keep one Google Doc per day, but regenerate each doc from the day's *response-route worksheet* (the registry already flags `is_response_route_candidate: true`) with the exit ticket appended as the last section. Multi-day packets (Wk2 salary packet, 4SW Wk3 action plan, 5SW Wk3 evidence report, 6SW Wk2 resume set) get one doc that Days 2/3/5 all point at. Fewest student clicks; biggest regeneration job.
- (b) Restore the original PDF anchors on every student page (the repair script kept an immutable pre-panel backup at `~/.config/canvas-fleet-parity/cce/source-response-routes/backups/…20260826T010841.json`) and keep the Google Doc button strictly as the exit ticket. Fastest, fully reversible, students get the packet as a Canvas file preview again. Loses the "type in a Google Doc" affordance for worksheets.
- (c) (b) now for the three published weeks so Wk2 stops being broken this week, then (a) as the durable fix before 1SW Wk3 publishes.
My recommendation is (c). It is the only option that fixes what students see today without a 180-doc regeneration in the critical path.

**Decision 2 — HQIM wording.** Proposed: class A → "Hats & Ladders" (first mention) / "H&L"; class D → "your *Find Your Future* workbook" on student surfaces and "FYF workbook" on teacher surfaces; class B → "Hats & Ladders or Xello" in teacher text and "the app" in student text, keeping the `Platform: H&L / Xello` field on the packet as the label students actually fill in. Class C untouched. All edits at source (templates, builders, day.md, worksheet sources), then re-run the affected builders through `run_builder_with_resource_access.py`. I would also strip DOL and the four TEKS codes from student pages in the same pass since they hit the same files.

**Decision 3 — Wk2 Day 2 / p. 38.** Either re-cite Day 2 to the Programming pathway section of the IT chapter (need to confirm which printed page carries "Pathway Possibilities" for Programming; I will grep before editing) or move the p. 38 App Exploration to Day 1's citation and give Day 2 the Hat Finder steps with no workbook page. The student page should name the page it wants open either way.

**Decision 4 — student-surface FYF/H&L delivery.** Larger and not this week: push day.md's FYF citations and `[H&L PLATFORM]` steps into the student templates for the 50 mismatched days, starting with the six blank weeks. I can generate the diff list from `fyf-citation-check.csv` and do it week by week as each module approaches publication.

**Guardrails for any of the above.** Body-only page PUTs, no publication-state changes (your Commons master rule), builders re-run through the resource-access wrapper, every step reversible from the 08-26 backups, and I show you the plan diff before the first write.
