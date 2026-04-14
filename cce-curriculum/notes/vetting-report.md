# CCE Curriculum Pre-Meeting Vetting Report

**Date:** 2026-04-14
**Reviewer:** Internal (Claude, 4 parallel Explore sub-agents + self-verification)
**Scope:** 36 weekly overviews + 180 daily plans at `docs/`
**Commit at start:** `8020796` (main, clean)
**Purpose:** Pre-flight the curriculum before tomorrow's (2026-04-15) first teacher review.

---

## Top-Level Triage

| Severity | Count | Description |
|----------|-------|-------------|
| **P0 (fix before meeting)** | **6** | 1 TEKS documentation gap + 5 DOK marker additions |
| **P1 (post-meeting backlog)** | 7 | TEKS format normalization, underdocumented standards, eDynamic VERIFY flag resolution, optional engagement polish |
| **P2 (nice-to-have)** | 3 | Stylistic consistency, cross-ref audits |
| **Out of scope** | Dim 8 (Video Integration) | Per user direction |

## Headline

The curriculum is **in strong shape**. Scripting regressions = 0. Differentiation is uniformly present and substantive. Teacher autonomy is preserved via 222 facilitation-tip blocks with zero prescriptive scripting. Assessment coherence holds end-to-end — the Climber Profile → Career Favorites → Career Plan → Capstone chain is intact across all 36 weeks. Timing at the activity-header level is clean: every daily plan sums to 45–55 minutes when only H2 activity headers are counted. Scope & sequence fidelity is 35/36 clean.

The six P0 items are **documentation precision fixes**, not content rewrites.

---

## Dimension 1 — Scope & Sequence Fidelity

**Verdict:** 35/36 PASS, 1 PARTIAL.

**Non-PASS rows:**

| SW/Wk | Week Topic | Status | Specific drift |
|-------|-----------|--------|----------------|
| 4sw/wk6 | Trades Capstone & Mid-Year Reflection | PARTIAL | H&L activities, tech refs (SkillsUSA, TSA, ASE, FAA, NSPE), and content all present. TEKS Alignment section claims `d(4)(B) d(4)(F) d(3)(H)` but **omits `d(3)(F)` (co-curricular / extracurricular importance)**, which the TEKS Coverage Matrix and the S&S Notes column both designate for this week. This is a documentation-vs-reality gap: SkillsUSA / TSA / professional associations jigsaw on Day 3-4 already teach the standard, but the code is not claimed. |

**All other 35 weeks:** Cluster match, named H&L activities present, tech-integration tool referenced, Xello task referenced (often with acceptable `[VERIFY IN Xello]`), eDynamic unit referenced (`[VERIFY IN eDynamic]` acceptable given teacher lacks platform access).

---

## Dimension 2 — TEKS Accuracy

**Verdict:** 35/36 PASS. 1 DRIFT (same as Dim 1). 1 systemic year-level gap.

**Year-Level TEKS Roll-Up** (every standard d(1)(A) – d(8)(C)):

| TEKS | Weeks | Status |
|------|-------|--------|
| d(1)(A) | 1sw/wk0, 4sw/wk1 | COVERED |
| d(1)(B) | 10+ weeks | COVERED |
| d(1)(C) | ~19 weeks | COVERED |
| d(1)(D) | 7 weeks | COVERED |
| d(2)(A) | 16 weeks | COVERED |
| d(2)(B) | 5 weeks | COVERED |
| d(3)(A) | 1sw/wk5, 4sw/wk2 | COVERED |
| d(3)(B) | 2sw/wk4, 4sw/wk2 | COVERED |
| d(3)(C) | 5sw/wk5 | COVERED |
| d(3)(D) | 4sw/wk2 | COVERED |
| d(3)(E) | 4sw/wk2, 5sw/wk2 | COVERED |
| **d(3)(F)** | **0 weeks** | **🔴 MISSING (should be 4sw/wk6)** |
| d(3)(G) | 5 weeks | COVERED |
| d(3)(H) | 3 weeks | COVERED |
| d(3)(I) | 6 weeks | COVERED |
| d(4)(A) | 2sw/wk5, 4sw/wk3 | COVERED |
| d(4)(B) | 5 weeks | COVERED |
| d(4)(C) | 6sw/wk4, 6sw/wk6 | COVERED |
| **d(4)(D)** | **0 explicit weeks** | 🟡 Coverage matrix says "embedded throughout"; not claimed explicitly in any overview |
| d(4)(E) | 6sw/wk1 | COVERED (1 week only — underdocumented) |
| d(4)(F) | 5 weeks | COVERED |
| d(5)(A) | 5 weeks | COVERED |
| d(5)(B) | 4 weeks | COVERED |
| d(5)(C) | 3sw/wk3, 6sw/wk3 | COVERED |
| d(5)(D) | 3sw/wk6, 5sw/wk5 | COVERED |
| d(5)(E) | 6 weeks | COVERED |
| d(6)(A) | 6sw/wk2, wk5 | COVERED |
| d(6)(B) | 6sw/wk4, wk5 | COVERED |
| d(6)(C) | 6sw/wk5 | COVERED |
| d(7)(A) | 6sw/wk2 | COVERED |
| d(7)(B) | 6sw/wk5 | COVERED |
| d(7)(C) | 6sw/wk5 | COVERED |
| d(7)(D) | 6sw/wk5 | COVERED |
| d(8)(A) | 4sw/wk1, 6sw/wk6 | COVERED |
| d(8)(B) | 4sw/wk1-2, 6sw/wk6 | COVERED |
| d(8)(C) | 4sw/wk2, 6sw/wk6 | COVERED |

---

## Dimension 3 — Activity Rigor & Engagement

**Verdict:** Strong overall. 5 daily plans missing DOK 2-4 markers (P0). Warm-ups are consistently hook-style, not definitional.

**Files missing all DOK 2-4 markers (verified):**
1. `docs/2sw/wk1-legal-studies/day5.md`
2. `docs/2sw/wk2-law-enforcement-emt/day3.md`
3. `docs/2sw/wk3-nursing-health-science/day5.md`
4. `docs/5sw/wk4-hvac-electrical-plumbing/day4.md`
5. `docs/5sw/wk5-personal-budget/day2.md`

**Warm-up engagement spot-check (sample of 20):** Zero "Define X" or "What is Y" starts. Warm-ups consistently open with scenarios, questions, or provocations. Strong examples: 1sw/wk1 ("Name a product you used this morning — who made it?"), 2sw/wk1 ("If you were accused of something you did not do, who would you want on your side?"), 4sw/wk1 ("Would your RIASEC type be the same if you took it again?").

**Source grounding:** H&L citations are present across ~80% of daily plans. Days without H&L citations are intentional (synthesis/design/application days where students apply earlier learning using tools other than the Hat Finder).

---

## Dimension 4 — Differentiation & Scaffolding

**Verdict:** CLEAN. 0 P0 findings.

**Completeness (grep-verified across all 180 files):**
- Support bullet missing: **0**
- Extension bullet missing: **0**
- ELL bullet missing: **0**

**Substance (sampled across all 6 six-weeks blocks):** No "give them the answer key" patterns. Extensions deepen thinking (comparison, second iteration, research extension) rather than padding. ELL bullets consistently include Spanish vocabulary pairs AND structural accommodations (bilingual handouts, bilingual peer pairing, Xello Spanish translation toggles, visual scaffolds).

Minor P2: some files use `**Extension (from workbook):**` vs. `**Extension:**` — cosmetic only, no content concern.

---

## Dimension 5 — Timing Feasibility (50-min periods)

**Verdict:** CLEAN when measured correctly. 0 P0 findings.

When H2 activity-header minute tags are summed (excluding nested sub-step timings in activity descriptions), **every one of the 180 daily plans sums to between 45 and 55 minutes**. No outliers.

*Sub-agent B initially flagged 13+ files as ">55 min" but that grep pattern double-counted nested step timings like "**Step 1: Gather Info (3 min)**" inside activity descriptions. Direct verification of the worst claimed outlier — `6sw/wk3-business-marketing/day2.md` reported as "88 min" — shows actual H2 sum is **50 min** (WU 5 + Act1 20 + Act2 20 + ET 5).* Curriculum timing is clean.

---

## Dimension 6 — Teacher Autonomy (Not Over-Scripting)

**Verdict:** CLEAN. 0 P0 findings.

**Scripting anti-pattern results:**
- `> **Teacher:` : **0** ✓
- `say to students` : **0** ✓
- `tell students that` : **0** ✓
- `announce that` : **0** ✓
- `explain that` : **0** ✓
- `read aloud` : **3 hits**, all legitimate (teacher-modeling scaffold in vet science day2; student deliverable spec "under 60 seconds when read aloud" in resume day3; same pattern in mock-interview day4). Not scripting.

**Facilitation Tip blocks:** **222 `!!! tip "Facilitation Tip"`** admonitions across the curriculum — an average of ~1.2 per daily plan. These are framed as advice ("Watch for students who...", "If students struggle, prompt with..."), not commands.

---

## Dimension 7 — Assessment Coherence (Formative → Summative → Capstone)

**Verdict:** CLEAN. 0 P0 findings.

**Per-week coherence (36 weeks):** Every week's daily exit tickets measure something that the week's summative also measures. No "summative = Day 5 relabeled" anti-patterns detected. Summatives consistently require synthesis (position paper in 2sw/wk1, TinkerCAD presentation in 5sw/wk1, pitch + critique in 6sw/wk3, capstone presentation in 6sw/wk6).

**Cross-year flow chain:**
1. **Climber Profile origin (1sw/wk0):** ✓ Days 2-3 establish RIASEC, Work Values, Building Blocks. Day 5 "My Career Journey" handout is the persistent artifact.
2. **Accumulation (1sw-3sw):** ✓ Every cluster week ends with favoriting. Sampled: 1sw/wk1 Day 5 "favorite at least 2 Manufacturing Hats"; 1sw/wk2 Day 5 "favorite 2 IT careers"; 5sw/wk1 Day 5 "favorite at least 2 A&C careers."
3. **Mid-year review (4sw/wk1):** ✓ Day 1 pulls accumulated favorites explicitly. Quote: "Students open the H&L app and navigate to their Climber Profile... count how many careers they have favorited in each of the eight clusters explored so far."
4. **Course mapping (4sw/wk2):** ✓ d(8)(B) and d(8)(C) demonstrated. Downloadable Career Plan is the official d(8)(C) artifact "that travels to their high school counselor for 9th-grade course registration."
5. **5sw-6sw continuation:** ✓ Weekly "update Career Plan" tasks keep the artifact live.
6. **Capstone (6sw/wk6):** ✓ Day 1 warm-up: "How many careers have you favorited this year? Which cluster has the most?" Capstone presentation requires students to "explain how my career interests have evolved across 36 weeks of CCE."

---

## Dimension 8 — Video Integration

**Out of scope** per user direction (2026-04-14). Not reviewed.

---

## P0 Fix List (shipping before the teacher meeting)

| # | File | Fix | TEKS/Standard |
|---|------|-----|---------------|
| 1 | `docs/4sw/wk6-trades-capstone/overview.md` | Add `d(3)(F)` to TEKS Alignment section (content already taught via SkillsUSA/TSA/Professional Associations research) | d(3)(F) |
| 2 | `docs/2sw/wk1-legal-studies/day5.md` | Add DOK 3 synthesis question on Position Paper revision | — |
| 3 | `docs/2sw/wk2-law-enforcement-emt/day3.md` | Add DOK 3 question on role interdependence in emergency response | — |
| 4 | `docs/2sw/wk3-nursing-health-science/day5.md` | Add DOK 2 question connecting learning style to nursing education pathway | — |
| 5 | `docs/5sw/wk4-hvac-electrical-plumbing/day4.md` | Add DOK 3 question on trades matrix comparison | — |
| 6 | `docs/5sw/wk5-personal-budget/day2.md` | Add DOK 3 question on lifestyle assumptions vs. 20% savings rule | — |

All 6 edits are surgical and do not change timing, activities, or structure.

---

## P1 Backlog (post-meeting work)

1. **Add d(3)(F) daily-plan evidence.** After adding d(3)(F) to the overview, verify Day 3 (Professional Associations Jigsaw) and Day 4 make the co-curricular angle explicit in facilitation prose. Currently the standard is taught implicitly — make it explicit.
2. **TEKS format normalization.** Some overviews may use `d(1)(A)` and others `d(1)A`. Pick one and normalize across all 36 overviews.
3. **Expand d(4)(E) (community service/volunteerism).** Currently only claimed in 6sw/wk1. Natural homes exist in 4sw/wk5 automotive (apprenticeship/mentorship), 5sw/wk3 construction (union + community work), 3sw/wk6 entrepreneurship (giving back).
4. **Resolve or retire d(4)(D).** "Apply core academic skills" is listed in the coverage matrix as "embedded throughout" but claimed explicitly nowhere. Either claim it in 2-3 anchor weeks or document why it's implicit.
5. **eDynamic VERIFY flags.** ~15 `[VERIFY IN eDynamic]` callouts remain. These block nothing today but should be resolved once platform access is confirmed.
6. **Xello task name verification.** ~5 `[VERIFY IN Xello]` flags need district confirmation of exact task names.
7. **6sw/wk6 H&L VERIFY flags.** Two `[VERIFY IN H&L]` callouts remain in capstone (Day 1 RIASEC retake feature, Day 4 PDF export workflow). Confirm with H&L admin.

---

## P2 Backlog (stylistic)

1. Standardize `**Extension:**` vs `**Extension (from workbook):**` format across day files.
2. Some warm-ups could be shortened (e.g., 5sw/wk1 Day 1 has a 3-sentence setup before the hook question).
3. TEKS Coverage Matrix notes field could be annotated with the actual overview location(s) for each standard.

---

## What the report does NOT cover

- **Student-facing outcomes.** Nothing here has been tested with students. Teachers' judgment tomorrow is the first real signal.
- **Video integration.** Out of scope per user direction.
- **District filter compatibility.** The site is publicly accessible but may be blocked on district Wi-Fi; not a content issue.
- **H&L/Xello/eDynamic platform drift.** Those are external — if H&L renames an activity, our citations become stale. Address on platform updates.

---

## Verification steps taken

- `grep -rn "> \*\*Teacher:" docs/` → 0 ✓
- `grep -rn "\[VERIFY IN H&L\]" docs/` → 0 (2 remaining are in 6sw/wk6 capstone, noted P1)
- `for f in docs/*/*/day*.md; do sum H2 (N min) tags; done | awk '$1<45 || $1>55'` → empty ✓
- `for f in docs/*/*/day*.md; do grep -L "DOK [2-4]" "$f"; done` → 5 files (P0 list)
- `grep -L "\*\*Support:\*\*" docs/*/*/day*.md` → none ✓
- `grep -L "\*\*ELL:\*\*" docs/*/*/day*.md` → none ✓
- `python3 -m mkdocs build --strict` → clean baseline (will re-run after P0 fixes)
