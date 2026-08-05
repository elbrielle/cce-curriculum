# District Expectations 2026-27 — Overlay Rulebook

**Status:** BINDING for the district-expectations overlay pass. Ratified as Decision **D-12** in `fyf-realignment-plan.md` §6.
**Audience:** implementer agents and Elisha. Dev-facing. Em dashes are fine in this file; they are not fine in anything this file tells you to paste into `docs/`.
**Read alongside:** `editing-heuristics.md` (dependency scope + grep recipes), `teks-audit-process.md` (the 6-step gate), `fyf-realignment-plan.md` §8 (which weeks get touched, in what order), `PLANNING.md` §8-9 (non-negotiables + preservation loop).

---

## §1 Purpose

Three Irving ISD documents landed for 2026-27:

| Short name | File | What it is |
|---|---|---|
| **5E doc** | `District Expectations Docs/5E Lesson Model_ Teacher and Student.docx` | Two tables (What the Teacher Does / What the Student Does) of should and should-NOT bullets for each of five phases. Adapted from Bybee 1997 via NSTA *Picture-Perfect Science Lessons* ch. 4, pp. 30-31. |
| **Continuum** | `District Expectations Docs/MASTER Instructional Strategies Implementation Continuum .docx` | Five instructional moves rated Developing / Proficient / Distinguished, grouped into three bands, with separate Teacher and Students descriptors at every level. |
| **CTE exemplar** | `District Expectations Docs/CTE_Design_Lab_PD_Lesson_Plan.docx` | The PD session ("CTE Design Lab: Solving the Classroom Case, Case #204") written up in the district's exemplar lesson-plan format. It is both a lesson plan and the model for what a CTE plan should contain. |

Plain-text extracts of all three live in the session scratchpad (`5E.txt`, `CONTINUUM.txt`, `CTE_PD.txt`). The `.docx` originals win any dispute.

**This rulebook governs one thing:** how those expectations get overlaid onto 36 weeks of existing CCE lesson plans without restructuring them. It is not a redesign spec. The overlay is additive and surgical, and it rides along with each week's FYF realignment pass rather than running as a separate sweep.

### Caveat block — read before writing anything teacher-facing

> **None of the three district documents mentions TIA or T-TESS.** Verified: `T-TESS` and `TIA` return zero real hits across all three extracts (the only `TIA` matches in the repo are the letters inside "Differentiation"). The linkage between these expectations and TIA is **verbal, from admin**. It is not written down in anything we hold.
>
> **The continuum is not a T-TESS rubric.** It rates three levels (Developing / Proficient / Distinguished). T-TESS rates five (Improvement Needed / Developing / Proficient / Accomplished / Distinguished). The shared word "Distinguished" is not evidence of a shared scale, and the continuum's Distinguished descriptors are behavior counts (90%+ of students do X), not T-TESS dimension language.
>
> **Rules that follow from this:**
> 1. Do not write "TIA", "T-TESS", "appraisal", or "evaluation rubric" into any file under `docs/`.
> 2. Do not build or imply a crosswalk from these moves to TIA rubric dimensions anywhere, in `docs/` or in `notes/`.
> 3. §5 of this file is an **admin-visibility crosswalk**: it maps district vocabulary to repo locations so a teacher can answer "show me" during a walkthrough. It is not an appraisal artifact, and it stays dev-facing.
> 4. If a future document arrives that does establish the TIA linkage in writing, that is a new decision. Escalate; do not infer it.

---

## §2 Canonical terminology reference

Everything in §2 is transcribed or tightly paraphrased from the three sources. When you need a word, take it from here rather than from memory.

### 2.1 The five instructional moves

Canonical spellings are the continuum's, with the docx's line-break artifact ("Think-Pair- Share") repaired. These exact strings go into `docs/`:

`Think-Pair-Share` · `Stop and Jot` · `Active Monitoring` · `Chunking` · `Time, Voice, Body (TVB)`

| Move | Continuum band | Distinguished, in one line |
|---|---|---|
| **Think-Pair-Share** | Response Strategies | Complex open-ended question with a directed 30-second Think, differentiated sentence stems tuned to varying language proficiency and cognitive demand, Partner A and Partner B each guided for 30 seconds, and two or more pairs sharing out while the teacher actively monitors and listens to responses; 90%+ of students discuss and students adapt or extend the stems. |
| **Stop and Jot** | Response Strategies | Complex, open-ended DOK 2-3 prompt aligned to the objective, with a defined time frame, explicit expectations for depth, differentiated stems, and exemplars of strong responses, while the teacher actively monitors writing, gives in-the-moment feedback, and uses the responses to adjust instruction; 90%+ complete it with reasoning or evidence. |
| **Active Monitoring** | Gathering and Responding to Data | Strategic circulation through multiple laps, each lap targeting specific success criteria aligned to the objective, with feedback for common misconceptions scripted in advance, immediate and actionable feedback delivered individually, in small group, or whole class, and monitoring data driving in-the-moment decisions (reteach, extend, regroup) with feedback reaching a wide range of students; 90%+ receive timely, actionable feedback. |
| **Chunking** | Scaffolding Instruction | Content sequenced into intentional chunks that build toward the objective, with the purpose of each chunk stated and connected to the goal, frequent purposeful checks between chunks (Stop and Jot, Think-Pair-Share), targeted scaffolds and exemplars inside each chunk, real-time adjustment between chunks based on student data (2nd Teach, extend), and gradual release across chunks; 90%+ clear each chunk before moving on. |
| **Time, Voice, Body (TVB)** | Scaffolding Instruction | Task time, voice level, and body expectations consistently stated and reinforced before and during instruction and transitions, with reminders, pacing, and supports proactively adjusted to student needs, expected behaviors reinforced in real time before concerns escalate, and behavior-specific praise and positive narration carrying the routine; 90%+ follow the expectations independently, can explain them, and self-monitor. |

Notes that matter for implementers:

- **Bands are not evenly loaded.** Response Strategies holds Think-Pair-Share and Stop and Jot; Gathering and Responding to Data holds only Active Monitoring; Scaffolding Instruction holds Chunking and TVB.
- **Gather-and-respond behavior is not confined to its band.** Every Distinguished descriptor contains a data-response clause: Think-Pair-Share ("actively monitoring and listening to student responses"), Stop and Jot ("uses responses to adjust instruction"), Chunking ("adjusts instruction in real time between chunks based on student data"), TVB ("proactively adjusts reminders, pacing, and supports based on student needs"). That is why §3(b) requires a gather-and-respond clause in **all five** bullets, not only the Active Monitoring one.
- **Sentence stems and modeling are inside the moves, not beside them.** Differentiated stems are named in the Distinguished rows for Think-Pair-Share and Stop and Jot; modeling and exemplars are named in Stop and Jot and Chunking. When you replace an existing `## IISD Instructional Strategies` bullet named "Sentence Stems" or "Modeling", the content moves inside the relevant move bullet. It does not get deleted.
- **Percent thresholds are the level tell.** <60% = Developing, 60-90% = Proficient, 90%+ = Distinguished, in every row.

### 2.2 The 5E phases, per the district doc

The district doc uses **Extend**. It does not use "Elaborate" anywhere. Write `Extend`.

| Phase | Teacher does | Teacher must NOT | Student signal |
|---|---|---|---|
| **Engage** | Generate interest and curiosity, raise questions, assess current knowledge including misconceptions | Explain concepts, give definitions and conclusions, lecture | Asks "why did this happen, what do I already know" and shows interest |
| **Explore** | Provide time for students to work together, observe and listen as they interact, ask probing questions to redirect investigations | Explain how to work the problem, give answers, tell students they are wrong | Thinks creatively within the limits of the activity, tests predictions, records observations |
| **Explain** | Ask for evidence and clarification, build on students' previous experiences, have students explain in their own words before supplying the formal vocabulary | Skip soliciting student explanations, accept unjustified explanations, introduce unrelated concepts | Explains possible solutions to others, listens critically, uses recorded observations as evidence |
| **Extend** | Expect students to apply concepts, skills, and vocabulary to new situations; remind and refer students to alternative explanations | Provide definite answers, lead step-by-step through new problems, lecture | Applies new labels, definitions, and skills in new but similar situations; uses prior information to ask questions and make decisions |
| **Evaluate** | Observe and assess students applying new concepts and skills, allow self-assessment of learning and group process, ask open-ended questions | Test vocabulary and isolated facts, introduce new concepts, run open-ended discussion unrelated to the concept | Demonstrates understanding, answers open-ended questions with evidence, evaluates own progress |

Two cautions:

1. **The source is science-framed.** It says "scientific explanations and vocabulary" and "hypotheses" because it is adapted from a science-methods book. CCE is career exploration. Translate: "evidence" is a salary figure, a BLS education requirement, or a workbook artifact; "hypothesis" is a prediction about a career or a design choice.
2. **The doc gives no phase durations and no required order.** Do not invent minute budgets per phase, and do not force a day into E-E-E-E-E order when the real day runs Engage then Explain then Explore.

### 2.3 Voice levels (CTE exemplar)

| Level | Name | District's example use |
|---|---|---|
| 0 | Silence | Independent work |
| 1 | Whisper | Quick partner questions |
| 2 | Conversational | Group work |
| 3 | Presenting | Whole-group volume |

Time and Body, same source: **Time** is pacing and urgency, and the named hack is a visible countdown timer displayed on screen for every timed phase. **Body** is movement and physical space, and the named hack is defining exactly where extra items go.

### 2.4 Active Monitoring framework: Pathway, Target, Feedback, Pivot

The CTE exemplar **names** these four terms and never defines them. Do not present a definition as the district's. The working definitions below are derived from the continuum's Distinguished Active Monitoring row and are what implementers should encode as behavior:

| Term | Working definition (derived from the continuum, not quoted from the district) |
|---|---|
| **Pathway** | The planned route and number of laps through the room. Not "circulating"; a deliberate path, walked more than once. |
| **Target** | The one success criterion each lap is checking, tied to the learning objective. Different laps, different targets. |
| **Feedback** | Immediate, specific, actionable response tied to the objective. The continuum expects the responses to common misconceptions to be scripted before class. General praise ("good job") is the Developing behavior. |
| **Pivot** | The in-the-moment instructional decision the monitoring data forces: reteach, extend, regroup, or pause the class to clarify. |

### 2.5 Exemplar plan elements, and what CCE adopts

| Element in the CTE exemplar | Adopted by this overlay? | Where it lands |
|---|---|---|
| Learning Target ("I Can...") | **Yes** | `overview.md`, under Lesson Objective. §3(a) |
| Success Criteria ("I Will Know I Am Successful When...") | **Yes** | `overview.md`, under Lesson Objective. §3(a) |
| TEKS Connection | Already present | `overview.md` `## TEKS Alignment`. No change. |
| Materials | Already present | `overview.md` `## Materials Needed` and each day's Lesson Overview. No change. |
| Instructional Sequence with `(Time: 15m \| Voice: Level 2 \| Body: in groups)` annotations | **No** | Forbidden. §3(f) |
| Teacher Actions / Student Actions split | **No** | CCE uses facilitation prose. No change. |
| Irving ISD Instructional Moves Embedded checklist | **Yes, re-shaped** | Becomes the five-bullet `## IISD Instructional Strategies` block. §3(b) |
| Formative Assessment | Already present | `overview.md` `## Formative Assessment`. No change. |
| Closure Reflection Prompt | Already covered | The daily Exit Ticket is the closure artifact. No change. |
| 5E phase labeling | **Yes** | `overview.md` Week at a Glance column + one row per day file. §3(c), §3(d) |

**Terms of art** worth recognizing in conversation with admin, none of which belong in `docs/`: **Dynamic Loop** (Mini-Lesson → Teacher Demo → Lab → Reflection, with moves embedded at each transition) versus **flatline sequence** (Bell Ringer → 25m Lecture → 25m Lab → Exit Quiz); **2nd Teach** (the re-teach between chunks, named in the Chunking Distinguished row, never defined); **5 Zones** (Before Class, Instruction, Processing, Collaboration, Assessment).

---

## §3 The overlay spec

**Binding. These design decisions are ratified. Do not expand scope, do not add elements from §2.5's "No" rows, do not propose a fuller 5E restructure.**

Per-week diff budget: `overview.md` gains roughly 12 net lines. Each day file gains **one** table row plus at most three inline move labels, which keeps every day file far inside PLANNING §8's 15-line cap.

### (a) overview.md — Learning Target and Success Criteria

Directly under the existing `## Lesson Objective` content, before `## Demonstration of Learning`, add exactly two lines:

```
**Learning Target:** I can ...

**Success Criteria:** I will know I am successful when ...
```

Rules:

1. **Blank line between them.** Adjacent lines merge into one paragraph in MkDocs. Two paragraphs is the required render.
2. **Exact openers.** `**Learning Target:** I can ` and `**Success Criteria:** I will know I am successful when `. Lowercase "I can" after the bold label, matching the exemplar's "I Can..." prompt in sentence position. These strings are grepped in §6.
3. **Re-voiced, never re-scoped.** Both lines are built from the week's existing `## Lesson Objective` paragraph and `## Demonstration of Learning` quote. You are converting third-person objective prose into first-person student voice. You are not adding a skill, a career, a platform, or a deliverable that the week does not already teach. If the objective and the DOL disagree, the DOL wins for the Learning Target and the week's real deliverables win for the Success Criteria.
4. **Success Criteria are observable artifacts.** Pull the concrete specs already in the week: worksheet columns, design specs ("4 walls, roof, 1 door, 2 windows"), counts ("at least three careers"). Avoid "understand", "appreciate", "be able to".
5. **Reading level.** These lines are teacher-facing in the repo but student-facing when posted. Hold them to the same 6th-7th grade ESL standard as exit tickets: short sentences, no nested clauses, no idioms. No TEK codes.
6. **TEKS gate.** For a week whose TEKS claims are gated, write these lines **only after** the 6-step audit in `teks-audit-process.md` passes for that week. The Learning Target restates the objective, and restating an unaudited objective launders an unverified claim. Gated weeks per `fyf-realignment-plan.md` D-10: `1sw/wk1-robotics-manufacturing`, `1sw/wk3-computer-science-it`, `2sw/wk6-biomedical-health-science`, `6sw/wk4-*`, `6sw/wk5-job-skills-mock-interview`. For all other weeks, no audit is required for (a) because nothing about the claim changes.

### (b) overview.md — replace the IISD Instructional Strategies block

Every one of the 36 overviews currently carries a `## IISD Instructional Strategies` section holding a flat list of 3 to 5 bullets with inconsistent labels (`Modeling`, `Sentence Stems`, `Jigsaw`, `5-Second Test`, plus some real move names). **Replace the entire bullet list** with exactly five bullets, one per canonical move, in this order:

1. `**Think-Pair-Share:**`
2. `**Stop and Jot:**`
3. `**Active Monitoring:**`
4. `**Chunking:**`
5. `**Time, Voice, Body (TVB):**`

Each bullet must contain three things, in this order:

- **Where it lands.** The specific day and the specific activity or artifact from that week ("Day 4, Activity 1, the three timed TinkerCAD checkpoints"). Never "throughout the week", never "during group work".
- **What Distinguished looks like there.** Not the continuum's abstract language re-typed. The continuum's Distinguished behavior instantiated on this week's content: the actual stems, the actual time counts, the actual checkpoints, the actual misconceptions.
- **The gather-and-respond clause.** What the teacher collects during the move and what they change because of it. Every bullet, not just Active Monitoring. Prefer a conditional: "If most jots land on X, pull the next segment toward Y."

Further rules:

7. **Do not lose load-bearing content.** If the old block named a sentence stem, a modeling step, or a checkpoint rubric, that content is folded into the matching move bullet (stems into Think-Pair-Share or Stop and Jot, modeling and exemplars into Chunking or Stop and Jot, clipboard rubrics into Active Monitoring). Deleting a week's only recorded sentence stems is a regression.
8. **Non-canonical strategies do not survive as bullets.** `Jigsaw`, `5-Second Test`, `Modeling`, `Gallery Walk` and similar are not among the five district moves. If the technique is genuinely load-bearing for the week, it stays as a phrase inside the relevant move bullet ("chunked as a jigsaw, one marketing role per team"), not as a sixth bullet.
9. **Anchor to real activities only.** If a week has no partner talk anywhere, you do not invent one to host Think-Pair-Share. You anchor Think-Pair-Share on the closest existing paired or shared moment (a peer review, a partner check, a share-out) and describe how to run that existing moment at Distinguished. If literally no such moment exists across five days, stop and escalate; that is a week-design problem, not an overlay problem.
10. **Voice levels may be named in prose** inside the TVB bullet ("Voice 0 while the file loads, Voice 3 for the presenter"). They must never become a table column or a per-activity annotation in a day file. See (f).
11. **Section heading is unchanged.** It stays `## IISD Instructional Strategies`. Do not rename it to "Instructional Moves" or anything else; 36 files and the offline export depend on the string.
12. **No em dashes, no scripting, no TEK codes.** This block is `docs/` body prose.

### (c) overview.md — 5E column in Week at a Glance

Append **one column** to the `## Week at a Glance` table as the **final** column, header exactly `5E`. Update the separator row to match the new column count.

- **Phase names only.** Separate with ` · ` (middot with spaces, the same separator already used on exit-ticket lines). No activity names, no times, no explanations. The table stays narrow.
- **Order follows the day's real flow**, not the canonical E-order. A day that runs warm-up, then teacher-modeled skills, then student build, then ticket is `Engage · Explain · Explore · Evaluate`. That is correct and must not be "fixed".
- **Typical mapping:** Warm-Up = Engage; main activities = Explore or Explain; an activity that applies the week's skills to a new situation or context = Extend; Exit Ticket = Evaluate.
- **Include Extend only when a day genuinely applies concepts to a new situation.** Presentation, capstone, transfer-to-new-scenario, and cross-platform-application days often carry Extend. Skill-introduction days usually do not.
- **A phase may repeat or be absent.** Do not pad a day to five phases.

### (d) day files — one row in the Lesson Overview table

Add exactly one row to the two-column Lesson Overview table at the top of each day file. **Insert immediately after the `**TEKS**` row and before the `**Deliverable**` row.** Format:

```
| **5E Phases** | Engage: Warm-Up · Explore: [activity] · Explain: [debrief/share] · Evaluate: Exit Ticket |
```

- Adjust to the day's real shape. Include `Extend:` only when genuinely present. Drop a phase the day does not contain.
- Keep each phase's descriptor to a short noun phrase pulled from the day's own headings ("Cluster tour and Safety Supervisor plan"), not a sentence.
- One line. No pipes inside cell text, no line breaks, or the table breaks.
- The cell must agree with that day's entry in the overview's Week at a Glance 5E column. Same phases, same order.

### (e) day files — inline move naming, existing moments only

Name a move inline **only where the existing facilitation prose already performs that move**. This is a labeling pass, not an authoring pass.

| Existing prose already does this | Label it | Add, at most |
|---|---|---|
| A pair or partner discussion of a prompt | `**Think-Pair-Share:**` | Directed 30-second Think, Partner A then Partner B, and who shares out |
| A quick write, jot, notebook capture, or video pause-and-write | `**Stop and Jot:**` | The time box and a stem |
| Circulating, a clipboard check, a checkpoint sweep, a "verify before moving on" | Active Monitoring, using Pathway / Target / Feedback / Pivot vocabulary | The lap's target and the pivot condition |
| Skills or steps taught one at a time with checks between | `**Chunking:**` | What each chunk's check is |
| A stated work time, voice expectation, or movement rule | Time, Voice, Body vocabulary | The voice level and where materials go |

Rules:

13. **Never invent a classroom moment to host a move.** If Day 3 has no partner talk, Day 3 gets no Think-Pair-Share. Coverage of all five moves is a **week-level** requirement (the overview's five bullets), never a day-level one.
14. **Never change what students do.** You may name and tighten (add "30 seconds", "Partner A then Partner B"). You may not add a step, swap an activity, or change an activity's purpose.
15. **Leave correct existing labels alone.** Several day files already carry `**Stop and Jot:**` and `Think-Pair-Share` in the right places. Do not re-label, re-bold, or re-word them.
16. **Three inline labels per day file, maximum.** Past three, the day reads as a compliance document instead of a lesson plan.
17. **Timing is untouchable.** Do not edit any `(N min)` H2 parenthetical, and do not let an added "30 seconds" imply the activity got longer. See PLANNING §10 lesson 12.

### (f) Forbidden

- **No `Time | Voice | Body` columns**, in any table, in any file under `docs/`. No `(Time: 15m | Voice: Level 2 | Body: in groups)` annotations on activities. Voice levels appear in prose only, in the overview's TVB bullet and at most one inline mention per day file.
- **No restructuring day files into 5E sections.** `## Warm-Up`, `## Activity 1..N`, `## Exit Ticket`, `## Differentiation` stay exactly as they are. 5E is a label on the existing structure, never a replacement for it. D-12 says explicitly: not a full 5E restructure of 180 day files.
- **No teacher scripting.** `> **Teacher:** "..."` stays at zero. Naming a move never licenses a quoted line.
- **No em dashes** in `docs/` body prose. H1 and H2 titles are the only exception, and this overlay does not touch titles.
- **No TEK codes in student-facing text.** The overlay adds none.
- **No timing changes.** No minute tags edited, no activity lengthened or shortened.
- **No new activities, no new platforms, no new deliverables.** PLANNING §8 still binds.
- **No exit-ticket text changes.** This overlay does not touch exit tickets, so no `build_pdfs.py` or `inject_pdf_links.py` run is required. If you find yourself editing an exit ticket, you have left this spec.
- **No TIA or T-TESS language** anywhere. See §1.

---

## §4 Worked example: `docs/5sw/wk1-architecture`

Derived from that week's real content. **Do not apply these edits to the week's files as part of reading this rulebook.** The example lives here only; 5SW Wk1 gets its overlay in its own Phase C pass.

Source content this example is built from: objective and DOL (`overview.md`), Day 1 Activity 1 cluster-tour video pauses and the Ch 3 p. 38 "Making Connections" prompt, Day 3 Activity 2 five-skill builder with thumbs checks, Day 4 Activity 1 three timed checkpoints, Day 5 Activity 1 presentations with the star-and-wish routine.

### 4.1 Learning Target and Success Criteria

Paste under the existing `## Lesson Objective` paragraph:

```markdown
**Learning Target:** I can describe the Architecture and Construction career cluster, compare the education and salary pathways of at least three A&C careers, and design a 3D building model in TinkerCAD that meets the client specs.

**Success Criteria:** I will know I am successful when I can name three A&C careers and what each one does, when my research worksheet lists years of education, cost, and DFW salary for at least three careers, and when my TinkerCAD building has 4 walls, a roof, 1 door, and 2 windows and is exported as a PNG.
```

Both lines trace to existing content: the DOL supplies the three verbs, the Day 2 worksheet supplies the three comparison columns, the Day 3 design challenge supplies the build spec, and Day 4 supplies the PNG export. Nothing new was added.

### 4.2 Replacement `## IISD Instructional Strategies` block

Replace the four existing bullets (Modeling, Chunking, Sentence Stems, Active Monitoring) with this entire block. The old Modeling bullet survives inside Chunking; the old Sentence Stems bullet survives inside Think-Pair-Share and Stop and Jot; the old Active Monitoring checkpoint rubric survives inside Active Monitoring.

```markdown
## IISD Instructional Strategies

- **Think-Pair-Share:** Day 1, Activity 1, the workbook "Making Connections" prompt (Ch 3, p. 38). Distinguished: pose the prompt to the whole group, hold a silent 30 second Think, then time Partner A for 30 seconds and Partner B for 30 seconds, and post two stems at different levels: "These careers work together because _____" and "A building for _____ looks different from a building for _____ because _____." Ask two pairs to share, not one. While pairs talk, listen for which pairs can name a second career in the build chain, and pick your two share-out pairs from what you heard rather than from raised hands.
- **Stop and Jot:** Day 1, Activity 1, the two pauses during the H&L cluster tour video. Distinguished: name both stop points before the video starts, give 45 seconds per jot with the prompt on screen, and offer two stems: "One career I did not expect in this cluster is _____" and "One thing I still want to know about _____ is _____." Read jots over shoulders during both pauses and track which careers students name. If most jots say Architect only, steer the Hat Finder browse that follows toward Drafter, Urban Planner, and Landscape Architect so Day 2 research is not four rows of the same career.
- **Active Monitoring:** Day 4, Activity 1, the three timed TinkerCAD checkpoints. Distinguished: walk a fixed pathway three times, one lap per checkpoint, each lap with a single target (minute 7 walls and roof grouped, minute 14 door and window holes cut, minute 20 one detail element added), marking the clipboard rubric as you go. Have the feedback ready for the two known misconceptions before class starts: shapes selected but not grouped, and a hole shape that never overlapped the wall. If more than a handful of students miss the minute 14 target, pivot and reproject the hole sequence to the whole room instead of repeating it desk by desk.
- **Chunking:** Day 3, Activity 2, the five core TinkerCAD skills. Distinguished: teach one skill at a time on the projector, say what each skill is for before modeling it (resize makes a wall, hole makes a door or a window), and close each chunk with the thumbs check already written into the plan before releasing the next one. Note which skill drew the most thumbs down. That skill becomes a 5 minute re-teach at the start of Day 4 Activity 1, and students who cleared all five chunks start their detail element early instead of waiting.
- **Time, Voice, Body (TVB):** Day 5, Activity 1, the building presentations. Distinguished: post the three blocks before the first presenter, Voice 0 while each PNG loads, Voice 3 for the presenter, Voice 1 for the star and wish partner talk, and run a visible 2 minute countdown for every presenter. Define where presenters stand and where the star and wish slips go so transitions do not eat presentation time. Narrate the students who are meeting the expectation rather than correcting the ones who are not. If the rotation is running long by the third presenter, trim partner talk to one star only and announce the change before the next presenter begins.
```

### 4.3 Week at a Glance with the 5E column

```markdown
## Week at a Glance

| Day | Focus | Key Activities | Deliverable | 5E |
|-----|-------|---------------|-------------|-----|
| 1 | A&C Cluster Exploration | H&L cluster tour + Safety Supervisor activity (Ch 3) | Completed safety plan | Engage · Explore · Explain · Evaluate |
| 2 | Career Research + Salary | Hat Research template (Ch 3) + salary comparison worksheet + Xello Education Experiences | Completed research worksheet | Engage · Explore · Explain · Extend · Evaluate |
| 3 | TinkerCAD Introduction | Account setup, 4-skill builder (drag/resize/align/group + holes), begin design challenge | Paper sketch + TinkerCAD progress | Engage · Explain · Explore · Evaluate |
| 4 | TinkerCAD Iteration + H&L | Design checkpoints + Trash to Treasure activity (Ch 3) | PNG screenshot + Trash to Treasure sketch | Engage · Explore · Extend · Evaluate |
| 5 | Presentations + Favorites | Building presentations + H&L favorites + eDynamic 3.1 | Presentation + updated Career Plan | Engage · Explain · Extend · Evaluate |
```

Why Day 3 reads `Engage · Explain · Explore · Evaluate`: the teacher-modeled five-skill builder comes before the open design challenge, so Explain precedes Explore. That is the day's real flow and it stays that way. Why Day 2 and Day 4 carry Extend: Xello Education Experiences applies the week's career thinking to the student's own school subjects, and Trash to Treasure applies architecture thinking to a landscape scenario the week has not covered. Why Day 5 has no Explore: nothing new is investigated; students present, transfer, and record.

### 4.4 Day-file Lesson Overview table with the 5E row (`day1.md`)

```markdown
| | |
|---|---|
| **Time** | 50 minutes |
| **Objectives** | Explore the Architecture & Construction cluster; identify A&C career pathways and education requirements; complete the Safety Supervisor workbook activity |
| **TEKS** | d(1)(B), d(1)(C) |
| **5E Phases** | Engage: Warm-Up · Explore: Cluster tour and Safety Supervisor plan · Explain: Making Connections and partner debrief · Evaluate: Exit Ticket |
| **Deliverable** | Completed Safety Supervisor safety plan (digital or on paper) |
| **Materials** | Chromebooks, H&L accounts, H&L Workbook Ch 3 (pp. 37-54), projector |
```

The phases match Day 1's row in 4.3, in the same order.

### 4.5 Inline move naming on Day 1: allowed versus forbidden

**Allowed** (the pair discussion already exists in Activity 1, step 3):

```markdown
3. **Read the "Making Connections" prompt** from the workbook (Ch 3, p. 38): *"How do you think these careers work together to make buildings functional and strong? Why do buildings often look different depending on their purpose?"* **Think-Pair-Share:** 30 seconds silent Think, then Partner A for 30 seconds, then Partner B for 30 seconds. Two pairs share with the whole class.
```

**Already correct, leave alone:** Activity 1 step 1 already reads "students use **Stop and Jot:** pause twice to write down one career that surprised them and one question they have." Do not re-label or re-word it.

**Forbidden:** adding a Think-Pair-Share to Day 3's account-setup steps, which are individual work with no partner moment. Forbidden: converting Day 4's checkpoint tip into a `(Time: 20m | Voice: Level 1 | Body: at your station)` annotation. Forbidden: adding a sixth "Modeling" bullet back into the overview block.

---

## §5 Admin-visibility crosswalk

Where each district expectation becomes demonstrable in the repo **after** a week's overlay lands. Dev-facing; see the §1 caveat before repeating any of this in a document that leaves the repo.

| District expectation | Repo location after the overlay | Example (5SW Wk1) | Walkthrough answer |
|---|---|---|---|
| **Think-Pair-Share** | `overview.md` › `## IISD Instructional Strategies`, bullet 1; plus the labeled moment in the day file named in that bullet | Bullet 1 → `day1.md` Activity 1, Making Connections | "Planned in the week overview, run on Day 1 during the Making Connections prompt." |
| **Stop and Jot** | Same section, bullet 2; plus the labeled jot in the day file | Bullet 2 → `day1.md` Activity 1, video pauses | "Two planned jots inside the cluster-tour video, with stems." |
| **Active Monitoring** | Same section, bullet 3; plus the circulate-and-check prose in the day file | Bullet 3 → `day4.md` Activity 1, three timed checkpoints and the clipboard tip | "Three laps, one target each, clipboard rubric, pivot condition written down." |
| **Chunking** | Same section, bullet 4; plus the stepped activity in the day file | Bullet 4 → `day3.md` Activity 2, five skills with thumbs checks | "Five chunks, a check after each, and the 2nd Teach is planned for the next day." |
| **Time, Voice, Body** | Same section, bullet 5; plus the one inline mention in the day file | Bullet 5 → `day5.md` Activity 1, presentation blocks | "Voice levels, a visible countdown, and where students stand, set before the first presenter." |
| **5E, week level** | `overview.md` › `## Week at a Glance`, final `5E` column | 4.3 above | "Every day's phase flow is on one line of the week table." |
| **5E, day level** | `day*.md` › Lesson Overview table › `**5E Phases**` row | 4.4 above | "Top of every daily plan, above the deliverable." |
| **Learning Target** | `overview.md` › under `## Lesson Objective` | 4.1 above | "Posted from the week overview; it is the DOL in student voice." |
| **Success Criteria** | `overview.md` › under `## Lesson Objective` | 4.1 above | "Three observable artifacts, all of them things students turn in this week." |
| **Formative assessment tied to the moves** | `overview.md` › `## Formative Assessment` (already present, unchanged) | Checkpoint and worksheet rows | "Already in the plan; the moves bullets say what data gets collected during them." |

---

## §6 QA checklist for implementers

Run per week after the overlay edits, before the PLANNING §9 preservation loop. All paths relative to repo root. Checks 1-9 should print nothing (or the expected count) when clean.

```bash
W=docs/5sw/wk1-architecture      # set to the week you just touched
```

1. **Canonical spellings, all five moves, in the week overview.**
   ```bash
   for m in "Think-Pair-Share" "Stop and Jot" "Active Monitoring" "Chunking" "Time, Voice, Body (TVB)"; do
     grep -qF -- "$m" "$W/overview.md" || echo "MISS: $m in $W/overview.md"
   done
   ```
2. **Exactly five bullets in the IISD section.**
   ```bash
   awk '/^## IISD Instructional Strategies/{f=1;next}/^## /{f=0}f&&/^- \*\*/{c++}END{print c" bullets"}' "$W/overview.md"
   ```
3. **"Extend", never "Elaborate".**
   ```bash
   grep -rn "Elaborate" docs/          # must return nothing
   ```
4. **No off-spelling variants anywhere in docs.**
   ```bash
   grep -rnE "Stop *& *Jot|Think Pair Share|Think/Pair/Share|Time/Voice/Body|TVB\)" docs/ | grep -v "Time, Voice, Body (TVB)"
   ```
5. **Learning Target and Success Criteria openers are exact.**
   ```bash
   grep -c "^\*\*Learning Target:\*\* I can " "$W/overview.md"                              # expect 1
   grep -c "^\*\*Success Criteria:\*\* I will know I am successful when " "$W/overview.md"  # expect 1
   ```
6. **5E column exists in Week at a Glance, and the separator row matches.**
   ```bash
   awk '/^## Week at a Glance/{f=1}f&&/^\|/{print;n++}n==2{exit}' "$W/overview.md"
   ```
   Header must end in `| 5E |` and the separator row must have the same pipe count.
7. **Every day file has the 5E Phases row, in the right slot.**
   ```bash
   grep -L "| \*\*5E Phases\*\* |" $W/day*.md          # must list nothing
   grep -A1 "^| \*\*TEKS\*\* |" $W/day*.md | grep -c "5E Phases"   # expect 5
   ```
8. **No Time/Voice/Body columns or per-activity annotations.**
   ```bash
   grep -rnE "\(Time: *[0-9]+|Voice: *Level|\| *\*\*Voice\*\* *\|" docs/
   ```
9. **No scripting regression.**
   ```bash
   grep -rn "> \*\*Teacher:" docs/                     # must stay at 0
   ```
10. **No em dashes added to docs/ body prose.**
    ```bash
    git diff -U0 -- docs/ | grep "^+" | grep "—"       # must return nothing
    ```
11. **No timing changes and no exit-ticket changes.**
    ```bash
    git diff -U0 -- docs/ | grep -E "^[+-]## .*\([0-9]+ min\)"   # must return nothing
    git diff --stat -- docs/resources/exit-tickets/              # must be empty
    ```
12. **Day-file diff budget.** `git diff --numstat -- $W/day*.md` should show roughly 1 to 4 changed lines per day file. Anything approaching 15 is a redesign; stop and escalate per `editing-heuristics.md`.

Then run the full PLANNING §9 preservation loop, including `python3 -m mkdocs build --strict`. No PDF regeneration is needed if check 11 is clean.
