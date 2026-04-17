# TEKS Audit Process

A reusable process for auditing whether a day's (or week's) TEKS tags are honestly supported by the lesson content, and for resolving misalignment. Informed by the 2SW Wk2 exit-ticket pilot (2026-04-16), which surfaced that 4 of 5 days had over-claimed or weak TEKS tags.

This is an authoring process, not a teacher-facing doc. Lives in `cce-curriculum/notes/` alongside `editing-heuristics.md` and `exit-ticket-templates.md`.

---

## When to run a TEKS audit

1. **During a week pilot** (like 2SW Wk2). Audit all 5 days' tags before shipping.
2. **When rewriting exit tickets** for a week. You cannot write a strictly-aligned ticket without first verifying the TEKS tag is itself strictly supported.
3. **Scheduled round** (e.g., before the next teacher-review milestone). Batch audit several weeks.
4. **On teacher feedback** flagging a specific day as "not really teaching what the objective says."

## Scope per run

- **Single-day audit** is too narrow (misses the week's distribution of TEKS across days). Don't do this.
- **Single-week audit** is the minimum useful unit. All 5 days + overview + CFA alignment.
- **Multi-week audit** only when batching scheduled rounds; keep to ≤3 weeks per pass to stay in the preservation-loop budget.

## The 6-step process (per day within a week audit)

**Step 1 — Read the day's Lesson Objective and TEKS tag.** Verbatim from the day.md header.

**Step 2 — Read the TEK language.** Pull the full text of each claimed TEKS code from the curriculum docs or the H&L scope mapping (starts around line 13400 in `cce-curriculum/resources/reference-pdfs/HatsandLadders.txt`). Pay special attention to qualifier language — "such as" means the named items are EXAMPLES, not an exhaustive list. "Including" means the named items are required. The distinction matters for exit-ticket alignment.

**Step 3 — List what the day actually teaches.** Walk the 3-5 activities. What skill, knowledge, or artifact does each activity build? Be concrete: "students fill in a comparison table with training times" not "students learn about careers."

**Step 4 — Match lesson content to claimed TEKS.** For each TEKS code on the day:

- **STRICT match:** the activity directly builds the skill / produces the artifact the TEK asks for. Keep the tag.
- **OVER-CLAIM:** the activity is thematically related but doesn't build the specific skill. Example: Day 4 of the 2SW Wk2 pilot claimed d(2)(A) "training requirements" but zero Day 4 activities touched training specifics (those live on Days 1 and 5). Drop the tag from that day; the week-level overview can still carry the code if another day covers it.
- **WEAK match:** the overlay (CCE-authored Career Connection paragraph, activity framing) carries the code but H&L content alone does not. Keep the tag if the overlay is substantial. Rewrite the exit ticket to assess the overlay content specifically (not the H&L content).
- **GAP:** the activity doesn't cover the code at all. Either drop the tag or add supplementary content.

**Step 5 — Write the exit ticket after the tags are cleaned.** The ticket should strictly assess AT LEAST ONE tag on the day. Use `exit-ticket-templates.md` for format selection. Honor the TEKS language (especially "such as" — don't treat named examples as exhaustive).

**Step 6 — Update downstream artifacts.** If a tag dropped from a day:

- `day.md` TEKS row header: drop the code
- `overview.md` Formative or Summative Assessment section: remove claims that tied the code to THIS day
- `teks-coverage-matrix.md`: leave the week-level listing if another day in the week still covers the code; remove the week from Explicit Weeks if no day covers it

## Decision rules (quick reference)

| Situation | Rule |
|---|---|
| TEK uses "such as" | Named items are examples; any equivalent concept counts |
| TEK uses "including" | Named items are required |
| H&L content doesn't teach the TEK, CCE overlay does | Overlay must be substantial (a Career Connection paragraph + activity framing); otherwise drop |
| Activity is thematically related but doesn't build the skill | Over-claim; drop |
| Multiple days in the week cover the same code | Fine; tag only the days where assessment happens |
| Overview lists code but no day strictly covers it | Real gap; either drop from week or add content |

## Escalation to coordinators

Escalate when:

- A TEK is systematically unsupported across multiple weeks where the scope-and-sequence claims coverage. This is an H&L-vs-TEKS structural gap, not an authoring fix.
- An H&L chapter fundamentally doesn't teach a code we've been claiming in every cluster (e.g., d(4)(F) integrity is not in H&L Ch 13; the claim comes entirely from CCE overlay).
- Fixing the misalignment requires cutting H&L content that teachers expect or adding content that would break the 45-55 min day budget repeatedly.

Escalation output: a short memo naming the TEK, the affected weeks, and the three decision paths (retag / add content / accept overlay-dependent assessment).

## Integration with the preservation loop

Add two checks to `cce-curriculum/notes/editing-heuristics.md` grep recipes (not yet added, candidate for round-2):

```bash
# For any week being audited, list day-level TEKS tags:
for f in docs/<sw>/<week>/day*.md; do
  echo "--- $f"
  grep -E "^\| \*\*TEKS\*\*" "$f"
done

# Cross-check against week overview TEKS claims:
grep -E "d\([1-9]\)\([A-Z]\)" docs/<sw>/<week>/overview.md
```

The audit itself is NOT a preservation-loop check (too judgment-heavy for a grep). It's a pre-ship review step for any week touching exit tickets or lesson objectives.

## Artifact checklist for a week audit

Per week, produce (or update):

- [ ] Audit notes (in this file or a sibling, briefly: "2SW Wk2 audited 2026-04-16, Day 4 d(2)(A) dropped")
- [ ] Updated `day.md` TEKS headers
- [ ] Updated `overview.md` Formative / Summative claims
- [ ] Updated exit tickets per the audit
- [ ] Updated `teks-coverage-matrix.md` if week-level coverage changes
- [ ] Preservation loop clean
- [ ] Commit with an "AUDIT:" prefix in the subject so it's filterable in git log

## Audit log (append as audits happen)

- **2026-04-16 — 2SW Wk2.** All 5 days audited. Day 4 d(2)(A) dropped (activities don't engage training specifics; d(2)(A) coverage for the week lives on Days 1 and 5). Exit tickets for Days 1-5 rewritten at 6th-7th ESL reading level with strict alignment to cleaned TEKS set. Key insight: d(4)(F) "such as" language means the 4 named traits are examples, not exhaustive — quality-pick probes using a broader vocabulary set (calm / fair / brave / honest / caring / clear-thinking) satisfy the TEK honestly.

- **2026-04-17 — 3SW Wk5 Cosmetology.** All 5 days audited. Significant retagging: Day 1 d(2)(A) dropped (Stress Toolkit + cluster tour doesn't teach training requirements) and replaced with d(1)(B) + d(1)(C). Day 2 d(3)(G) dropped (interview skills are not "steps to enroll"; the TEK fit is employability) and replaced with d(6)(C) mock interview + d(7)(B) thank-you email — both promoted from Implicit to Explicit in teks-coverage-matrix.md. Day 3 d(2)(A) + d(3)(G) kept (TDLR 3-route comparison is a strict fit; 3SW Wk5 Day 3 added to d(2)(A) Explicit Weeks column in the matrix where it had been absent). Day 4 d(3)(I) kept (salon concept). Day 5 d(2)(A) + d(3)(G) + d(3)(I) all dropped (Xello Career Factors + H&L favorites don't strictly support any of them) and replaced with d(1)(A) Xello assessment (Implicit) + d(1)(C) H&L favorites. Exit tickets rewritten in 5 distinct formats at 6th-7th ESL reading level (Comparison Matrix / Mini-Case / Ranked Justification / Decision Tree / Concept Map). Key insight: wrap-up days that bundle multiple platforms (Xello + eDynamic + H&L favorites) tend to over-claim TEKS; each platform's artifact only honestly lands ONE code and the day's tag should reflect the strongest-evidence pair, not the sum of all themes touched.
