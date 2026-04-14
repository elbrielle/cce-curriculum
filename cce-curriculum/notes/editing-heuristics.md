# Editing Heuristics — Read This Before Editing Curriculum

**Purpose:** strike the balance between reading too little (risk breaking logical flow or source grounding) and reading too much (wasted tokens). This is the trace-back protocol referenced from `CLAUDE.md`.

**Core rule:** when in doubt, read more; when certain, grep. Read the minimum set of files whose state you need to understand to not break logical flow — not the whole curriculum, not just the target file.

---

## The Dependency-Scope Principle

Every curriculum file has a **dependency scope** — the minimum set of other files (or sections within files) whose state you need to understand before editing it safely.

Examples:
- A warm-up depends on Activity 1 (the hook has to land into it), but not on Activity 2 or other days.
- A timing change depends on every other H2 activity header in the same file, but not on other day files.
- A TEKS alignment change depends on the scope-and-sequence row + the daily-plan evidence, and possibly on `teks-coverage-matrix.md`.
- A cross-year chain change (e.g., something Wk0 establishes that later weeks consume) depends on every week that consumes the data structure — and if you can't list those weeks, you don't understand the scope, so stop.

**You have read enough when you can answer "if I make this edit, what else might break?" without guessing.** If you're guessing, grep more. If you're rereading material you already grepped, you've gone too far.

---

## Decision Table: Before Editing X, Read Y

| You are editing… | You MUST read (or grep) | You can SKIP |
|---|---|---|
| A daily plan's **Warm-Up** prompt | The warm-up + Activity 1 header of the same file (hooks must bridge into the first activity) | Other activities, Differentiation, other day files |
| A daily plan's **single activity body** | The activity being edited + the Lesson Overview header table (to know TEKS + time budget) | Other activities, other day files unless the activity cross-references them |
| A daily plan's **Deliverable** spec | The activity that produces the deliverable + the overview's Summative Assessment section (to check end-of-week alignment) | Other activities |
| A daily plan's **Differentiation** section | Just Differentiation + Lesson Overview header | Activity bodies |
| A daily plan's **Exit Ticket** | Exit Ticket + Lesson Overview header; if it's Day 5, also the overview's Summative | Activity bodies |
| A daily plan's **minute tags / timing** | All H2 activity headers in the same file (to re-sum the 45–55 min budget) | Bodies of unchanged activities |
| A daily plan's **DOK question** | The activity the DOK follows + the TEKS in the Lesson Overview header | Other activities |
| An **overview's TEKS Alignment** | The overview's TEKS section + the week's `scope-and-sequence.md` row (grep it) + spot-check 1–2 day files for evidence of demonstration | All 5 day files in full, other weeks |
| An **overview's Week at a Glance** table | The overview's table + each day file's Lesson Overview header (grep the 2-column tables) | Day file bodies |
| An **overview's Materials / Vocabulary / Career Connection** | Just the overview section being edited | Day files |
| An **overview's Bridge to Theory (H&L)** paragraph | The overview section + `HatsandLadders.txt` grep for the chapter the week cites | The PDF, other weeks |
| An **overview's Formative / Summative Assessment** | Both sections + sample of the 5 day files' exit tickets (grep) | Day file bodies |
| **Any TEKS code change in an overview** | `scope-and-sequence.md` row + `teks-coverage-matrix.md` + the full affected overview + grep day files for demonstration evidence | Other weeks |
| **Any H&L activity citation change** | `HatsandLadders.txt` grep for the activity name + targeted `pdftotext` page-range extraction for the specific chapter | The full 116MB PDF, other chapters |
| **Any cross-week dependency** (e.g., changing how Wk0 seeds RIASEC, or changing 4SW/wk1 mid-year review's inputs, or changing 6SW/wk6 capstone's synthesis) | **STOP.** This is a redesign, not an edit. Escalate to the user. | — |

---

## Grep Recipes (paste-ready)

Every recipe below works with the `Grep` tool or with the `Bash` tool. Use them INSTEAD of full file reads when you can.

### Scope & Sequence lookups

```bash
# What's the S&S row for this week? (replace slug)
grep -n "wk5-personal-budget" cce-curriculum/scope-and-sequence.md

# What TEKS codes does the S&S assign to each week in 5SW?
grep -A1 "5th Six Weeks" cce-curriculum/scope-and-sequence.md
```

### TEKS auditing

```bash
# What TEKS does an overview claim?
grep -A10 "^## TEKS Alignment" docs/5sw/wk5-personal-budget/overview.md

# Which weeks claim a specific TEKS code?
grep -l "d(5)(D)" docs/*/*/overview.md

# Does the week demonstrate a TEKS it claims?
grep -l "budget" docs/5sw/wk5-personal-budget/day*.md

# Full TEKS inventory across all overviews (unique codes)
grep -rhoE "d\([1-8]\)\([A-Z]\)" docs/*/*/overview.md | sort -u
```

### Timing & rigor checks

```bash
# Sum H2 activity-header minute tags for ONE file
grep -E "^## .* \([0-9]+ min\)" docs/5sw/wk5-personal-budget/day2.md \
  | grep -oE "[0-9]+ min" | awk '{s+=$1} END {print s}'

# Find any day file whose H2 sum is outside 45-55 min
for f in docs/*/*/day*.md; do
  s=$(grep -E "^## .* \([0-9]+ min\)" "$f" | grep -oE "[0-9]+ min" | awk '{s+=$1} END {print s}')
  if [ "$s" -lt 45 ] || [ "$s" -gt 55 ]; then echo "$s $f"; fi
done

# Find any day file missing a DOK 2-4 marker
for f in docs/*/*/day*.md; do
  grep -q "DOK [2-4]" "$f" || echo "$f"
done
```

### Differentiation & autonomy checks

```bash
# Any day file missing a Support / Extension / ELL bullet?
grep -L "\*\*Support:\*\*"   docs/*/*/day*.md
grep -L "\*\*Extension:"     docs/*/*/day*.md  # matches both **Extension:** and **Extension (from workbook):**
grep -L "\*\*ELL:\*\*"       docs/*/*/day*.md

# Scripting regressions (must always return zero)
grep -rn "> \*\*Teacher:" docs/

# Soft scripting hits — each one needs context check
grep -rn "say to students\|tell students that\|read aloud\|explain that\|announce that" docs/
```

### H&L workbook lookups

```bash
# Find a specific H&L activity in the workbook text
grep -n -i "safety supervisor" cce-curriculum/resources/reference-pdfs/HatsandLadders.txt

# Extract a specific H&L chapter as text (pages 37-54 = Architecture)
pdftotext -f 37 -l 54 cce-curriculum/resources/reference-pdfs/HatsandLadders.pdf -

# Find a Powerskills module
grep -n -i "time management" cce-curriculum/resources/reference-pdfs/Powerskills.txt

# Which weeks reference a given H&L chapter?
grep -rl "H&L Ch 16\|Ch 16:" docs/
```

### Cross-file relationship checks

```bash
# Which day files reference the Climber Profile?
grep -rln "Climber Profile" docs/

# Which files does an activity cross-reference?
grep -rn "Trash to Treasure" docs/
```

### Redundancy audit after a structural framing change

Run these after writing any new framing admonition, softening any body claim, or reframing a week as optional/required/buffer. See "Never do these" rule 10.

```bash
# (1) OLD-framing hits still in place — each is a candidate for softening
grep -nE "OFFICIAL|CAPSTONE|highest-stakes|primary artifact|official course artifact|MUST|REQUIRED" docs/path/to/overview.md

# (2) Restatement phrases — each is a candidate for DELETION (dead paragraph)
grep -nE "per the admonition above|optional per|as noted above|as mentioned above|as stated above" docs/path/to/overview.md

# (3) Any framing-adjacent claim you might have missed (use the specific terms
# from your new admonition, not a generic list)
grep -nE "your new admonition's key terms here" docs/path/to/overview.md
```

Then visual-scan: any prose paragraph immediately before a bullet list or table — apply the "does this paragraph add specific information, or only set up the list" test. See PLANNING.md §10 lesson 16.

---

## Never Do These Without Reading More

These edits break curriculum soundness if you don't pull the full dependency scope:

1. **Never change a week's timing without re-summing all 5 day files.** A 5-min extension to Day 1 Activity 2 means you have to trim 5 min somewhere else in Day 1 to stay in the 45–55 min budget. Use the Timing recipe above.

2. **Never change a TEKS code claim without checking all three sources.** The authoritative source for which TEKS a week claims is `scope-and-sequence.md` col 11. The supporting source is `teks-coverage-matrix.md`. The evidence source is the day files themselves — a TEKS is not legitimately claimed unless at least one day demonstrates it.

3. **Never rewrite a named H&L activity without grep-verifying its chapter/page in `HatsandLadders.txt` first.** If you can't find the activity name in the `.txt`, you're about to invent or misattribute content — both of which break source grounding.

4. **Never edit 1SW Wk0 Day 2–5 without also checking how later weeks consume the data.** Wk0 establishes the Climber Profile, RIASEC type, Work Values, and Building Blocks that 4SW Wk1 (mid-year review) and 6SW Wk6 (capstone) pull back. If you change what Wk0 produces, those downstream weeks break.

5. **Never edit an overview's Summative Assessment without checking the 5 exit tickets.** The formative → summative chain has to hold.

6. **Never add a new activity that's not in the scope-and-sequence column 5 H&L activity list.** If the activity you want isn't there, it's out of scope.

7. **Never delete the `[VERIFY IN eDynamic]` or `[VERIFY IN Xello]` callouts.** They're placeholders for platform-access gaps that need district admin confirmation, not editorial noise.

8. **Never add or keep a "cut students off mid-sentence" / "no exceptions" enforcement tip without checking whether the enforced skill is taught this week.** This is Dimension 9 in PLANNING.md (Skill-Before-Enforcement). Before writing or keeping any hard-discipline facilitation tip, verify: (a) is the skill in the week's Lesson Objective or DOL? (b) do Days 1-4 include explicit practice of the skill? (c) are students warned in advance in the activity text? If any are No, either soften to a schedule-fairness framing or move the hard enforcement to a skill week (6SW Wk4 Sales/Presentations, 6SW Wk6 Capstone). Grep recipe: `grep -rn "mid-sentence\|no exceptions\|cut .* off at" docs/`.

9. **Never write "This is real X" / "This builds real Y" / "This is what real Z do" filler.** These phrases are declarative fluff — they sound muscular but tell the teacher nothing. Either replace with a concrete curriculum tie ("prepares students for Day 5 presentations" / "aligned with H&L Powerskill Z") or delete. Grep recipe: `grep -rn "This is real\|This builds real\|This is what real\|Real conferences\|Real interviews" docs/`. Related: avoid "This is uncomfortable but [X]" and "This is the most important [X] they will learn" for the same reason.

10. **Never ship a structural framing change without a full-file redundancy audit.** A structural framing change is any edit that (a) adds a new admonition establishing a thesis, (b) softens a body claim to match a new framing, or (c) reframes a week as optional/required/buffer/non-buffer. After you write the change but BEFORE you run the 6-check preservation loop, audit the whole file for redundancy and contradiction. Three passes:
    - **(a) Old-framing contradictions** — grep for hits of the old frame that still need softening: `grep -nE "OFFICIAL|CAPSTONE|highest-stakes|primary artifact|official course artifact|MUST|REQUIRED" <file>`. Any hit that directly contradicts the new framing must be softened to match.
    - **(b) Dead-paragraph restatements** — grep for phrases that signal a paragraph only exists to echo the new framing: `grep -nE "per the admonition above|optional per|as noted above|as mentioned above|as stated above" <file>`. Each hit is a candidate for deletion (not softening — delete if the paragraph would lose nothing).
    - **(c) Visual scan of any prose paragraph immediately before a bullet list or table.** Apply the "does this paragraph add specific information, or only set up the list" test from PLANNING.md §10 lesson 16. If the paragraph only sets up the list, delete it. Admonition titles + bullets usually carry the meaning on their own.

    Session 4 example: commit `01627b1` rewrote the 6SW Wk6 buffer admonition but missed all three classes of redundancy. Commit `7ccdce2` caught internal redundancy inside the admonition after user flagged "too long." Commit `e153c09` caught a dead intro paragraph (Pre-Capstone Teacher Checklist) + a pre-existing "OFFICIAL d(8) artifact" contradiction (Bridge to Theory section) after user flagged the intro. Two full user round-trips to land one framing change. Running the audit proactively in the initial commit would have collapsed both follow-up commits into the first one. See the Grep Recipes "Redundancy audit" section above.

---

## When You've Read Enough

You have read enough when you can answer these without guessing:

1. What does this edit change in the student experience?
2. What other files or sections reference the thing I'm about to edit?
3. If this edit lands, what's the next downstream artifact that will use it, and will it still work?
4. Does the scope-and-sequence still support this week after my edit?

If any answer is "I don't know," grep for the answer before editing. If you have to read a whole day file to answer one of them, read only the sections that matter — use `Read` with `offset`/`limit` or use `grep -A N` to pull just the relevant block.

---

## When You've Read Too Much

You've read too much when:

- You read all 5 day files of a week to change one line in one day
- You read full overviews for weeks you are not editing
- You opened `HatsandLadders.pdf` directly (use `HatsandLadders.txt` or `pdftotext -f N -l M`)
- You read every TEKS reference in the repo to verify a single TEKS code change
- You re-read a file you already grepped for the same information

If you catch yourself doing any of these, stop and use the grep recipes above.

---

## Escalate Rather Than Edit

If any of these apply, STOP and escalate to the user instead of editing:

- **>15 lines touched in a single day file** — that's a redesign, not a fix
- **A new activity being invented from scratch** — you don't have the source grounding
- **A TEKS code that contradicts scope-and-sequence col 11** — you're changing the spec, not fixing the docs
- **A timing reshuffle that can't stay in the 45-55 min budget** — the activity doesn't fit in the period
- **A cross-week dependency change** — this is a scope shift
- **Any edit that would require breaking a `[VERIFY IN eDynamic]` or `[VERIFY IN Xello]` block** — those block on platform access, not your judgment

Escalation is a feature, not a failure. The user sees the concern and decides whether to change scope. Your job is to flag the decision point clearly.
