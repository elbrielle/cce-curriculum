# Facilitator Guide Markdown Format

Every facilitator guide in `cce-curriculum/guides/` must follow this exact structure. The build script parses these headings and markers to produce formatted `.docx` files.

## Frontmatter

```yaml
---
six_weeks: "1st Six Weeks"
week: "Week 0"
title: "Who Am I? My Career Journey Begins"
subtitle: "Classroom Routines, Safety Procedures, and Career Self-Discovery"
topic: "Classroom Routines, Lab Safety, and Career Self-Assessment"
length: "5 class periods (45-60 minutes each)"
cluster: "Onboarding / Cross-Cluster"
pathways: "All Irving ISD CTE Pathways (overview introduction)"
---
```

All fields are required. The `cluster` field maps to one of the 14 Hats & Ladders clusters. The `pathways` field lists the specific Irving ISD pathways covered (see PATHWAYS.md).

## Required Sections (in order)

These must appear as `##` headings in exactly this order:

1. **Lesson Objective** — 1-2 sentence description of what students will do/learn.
2. **Demonstration of Learning** — An "I can..." statement in a blockquote.
3. **TEKS Alignment** — Bullet list of TEKS codes with descriptions: `- **d(1)(A):** Description here.`
4. **Materials Needed** — Bullet list of required materials.
5. **Career Connection** — 1-2 paragraphs connecting the week's topic to real careers. Ends with `**Irving ISD Pathway:** ...`
6. **Vocabulary** — Bullet list of bold terms with definitions: `- **Term:** Definition here.`
7. **Bridge to Theory (Hats & Ladders)** — How H&L connects to this week's content.
8. **IISD Instructional Strategies** — Bullet list of bold strategy names with descriptions.
9. **Lesson Sequence** — The day-by-day lesson plan (see below).
10. **Formative Assessment** — Bullet list of observation/check opportunities with TEKS codes.
11. **Summative Assessment** — Description of the collected/graded artifact.
12. **Differentiation** — Three subsections (see below).

## Lesson Sequence Structure

```markdown
## Lesson Sequence

### Day 1: Title Here

**WARM-UP:** Prompt text here.

#### Activity Name (15 min)

> **Teacher:** "Scripting text in quotes."

Activity description paragraph.

> [H&L PLATFORM] Platform-specific instruction.

> [VERIFY IN H&L] Verification note.

**DOK 2:** Question text here.

**EXIT TICKET:** Prompt text here.
```

### Heading levels
- `### Day N: Title` — one per class period (typically Day 1-5)
- `#### Activity Name (time)` — activities within a day

### Special markers
All of these are detected by the build script for colored formatting:

| Marker | Format in markdown | DOCX styling |
|---|---|---|
| Teacher script | `> **Teacher:** "quoted text"` | Blue label, italic quote |
| H&L instruction | `> [H&L PLATFORM] text` | Blue background (#E8F0FE) |
| H&L verify | `> [VERIFY IN H&L] text` | Orange background (#FFF3E0) |
| eDynamic verify | `> [VERIFY IN eDynamic] text` | Purple background (#F3E5F5) |
| Warm-up | `**WARM-UP:** text` | Yellow background (#FFF8E1) |
| Exit ticket | `**EXIT TICKET:** text` | Green background (#E8F5E9) |
| DOK question | `**DOK N:** text` | Red label (#D84315), italic |
| EDP step | `**EDP:** text` | Purple italic (#7B1FA2) |

## Differentiation Section

Always three `###` subsections:

```markdown
## Differentiation

### Scaffolded Learning
- Support strategy 1
- Support strategy 2

### Extensions
- Challenge activity 1
- Challenge activity 2

### ELL Language Support
- Language support 1
- Language support 2
```

## File Naming Convention

Pattern: `wk{N}-{topic-slug}.md`
- Week number matches the `week` frontmatter field
- Topic slug is lowercase, hyphenated, derived from the primary topic
- Example: `wk3-computer-science-it.md` for Week 3 Computer Science

## Common Mistakes to Avoid

- Do not use `#` (h1) — the title comes from frontmatter, not an h1 heading
- Do not reorder sections — the build script expects them in the listed order
- Do not nest `####` inside `##` sections other than Lesson Sequence — only days get `###` and activities get `####`
- Exception: Differentiation uses `###` for its three subsections
- Do not use unicode bullet characters — use standard markdown `-` lists
- Keep teacher scripting in blockquotes with the exact `> **Teacher:** "..."` format
- Keep flag markers in blockquotes: `> [H&L PLATFORM]`, `> [VERIFY IN H&L]`, etc.
