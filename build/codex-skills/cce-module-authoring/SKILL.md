---
name: CCE Module Authoring Harness
slug: cce-module-authoring
version: 1.0.0
description: "Use whenever writing, revising, or auditing a CCE Canvas Teacher Facilitator Guide, Student Guide, projected deck, or journal page. Forces the module shape teachers expect, the three language tiers, journal restraint, real images with credits, editable decks, and a printed self-audit before handoff."
---

# CCE Module Authoring Harness

You are writing for two readers. A teacher opens the Facilitator Guide and must see in one screen: what students learn, how they show it, which workbook pages, which platform tasks, whether a notebook page is needed, what scaffolds exist, and where the slides are. A student opens the Student Guide and must be able to do the lesson without the teacher reading it to them. Nothing else belongs on either page.

Read first: `CLAUDE.md`, `cce-curriculum/notes/canvas-lesson-production-workflow.md`, `cce-curriculum/notes/teacher-voice-standard.md`, `cce-curriculum/notes/deck-audit-improve-workflow.md`. Reference pair: `build/canvas/templates/wk0-day2-*.html` (shape), with the corrections in section 6 below applied.

## 1. Facilitator Guide: required shape, in this order

1. Title line: week, day, lesson title. Time. TEKS codes.
2. **At a glance** block (this is the part teachers read standing up):
   - Objective: one sentence, student-facing "I can" form.
   - Demonstration of learning: what the student produces and where it lives (H&L profile, FYF page, notebook page, Canvas submission). One line.
   - Workbook: exact FYF printed pages, or "none today".
   - Platform: exact H&L or Xello tasks by their in-app names, or "none today".
   - Notebook page: "none" or the page title plus the one to three sentence stems it holds. Physical or digital is the teacher's call; say that once, not per step.
   - Slides: download and Google copy links. One line.
   - Scaffolds and differentiation: word bank, bilingual stems, model, sentence frames, read-aloud, private response. Name only what exists and is linked.
   - Exit evidence: the DOL artifact or the exit ticket name and link.
3. Before students arrive: three to five bullets, each an action.
4. Complete model and non-model.
5. Timed flow: Do Now, numbered segments, minutes, the teacher move per segment, the checkpoint.
6. Pivot and recovery: platform down, no workbook, short class, absent students. This is the only place outage and absence logic lives.
7. Access and privacy.

Each section fits on one screen. If it does not, cut.

## 2. Student Guide: required shape, in this order

1. Title as a question students can answer by the end.
2. One line: what you will do today and why.
3. "Today you will": at most four bullets, verb first.
4. Do Now with the Spanish stem directly under it.
5. Numbered steps. One action per line. Each platform step names the exact button or card ("Profile Climbs → Discover Your Work Values"). A model appears right where students need it.
6. "You are done when": at most three checks.
7. Optional "Absent? Start here": student actions only. Never mention a platform being down, the teacher's route, provisional marks, catch-up days, or grading.

Caps: no step has more than four lines; one Spanish stem per writing job; no paragraph longer than two sentences.

## 3. Language tiers (binding)

| Tier | May contain | Must not contain |
|---|---|---|
| Projected slides | student actions, WHAT YOU SEE / DO THIS / DONE WHEN, stems, models | routes, fallbacks, minute ranges, Minor/Major, teacher moves, outage logic |
| Student Guide | student actions, stems, models, links, done-when | everything in the right column above, plus the words in the student banned list |
| Facilitator Guide and speaker notes | timing, moves, pivots, grading, outage and absence logic, sources | build and implementation narration |

Student banned list (rewrite on sight): provisional, pending (except the exact "cluster pending" label H&L work requires), catch-up, fixed list, verification, recopy, autosave, distribute, Content Library, table cell, template, module, page ID, embed, publish, route, fallback, platform unavailable, "if H&L is not working", TEKS codes, internal codes such as "Core B", any honorific with a teacher name on shared material.

Teacher banned list (rewrite on sight): "this guide contains the full lesson", "speaker notes include", "default copies: 0", "native 1×1 table cell", "accept without a separate verification or recopying step", "distribute the page", Canvas API or HTML talk, file IDs, build notes, anything that explains how the page was made instead of how to teach.

Test: if a sentence would make sense only to the person who built the Canvas page, it is implementer language. Delete it or move the teachable part into a teacher action.

## 3b. Platform access facts (binding)

- Students open Hats & Ladders and Xello through ClassLink. ClassLink passes the sign-in token; a direct "Sign in with Google" on the H&L site does not work for IISD students. Every student step, slide, and Canvas link to H&L or Xello goes through ClassLink. Never write "Sign in with Google" or a bare app.hatsandladders.com link. Owner ruling 2026-08-19.
- Xello's educator library supplies lesson slides (PPTX, some with Irving versions), student instruction PDFs, and videos. Check `cce-curriculum/resources/xello-licensed/` first and use those slides and screens before building new ones. Embed official video players; never rehost a video file.

## 4. Journals: restraint rule

H&L and FYF already capture most evidence. Before adding a notebook page ask: is there a required student product that no platform or workbook page stores? Only then create a page.

- At most one notebook page per day. At most three writing jobs on it. Each job is a sentence stem.
- The "template" is the stems. No table specs, no formatting instructions, no OneNote mechanics on teacher or student pages. If a teacher needs the OneNote setup, link the one existing setup note; do not restate it.
- A prediction, a one-sentence interpretation, or the DOL sentence are good notebook jobs. Re-recording an H&L result that H&L already stores is not.
- Say "notebook page or paper, teacher's choice" once in the Facilitator Guide, never in student steps.

## 5. Images and decks

- Every slide is classified: platform screenshot, real-world photo, diagram, or text-only by design. Text-only must be a deliberate choice, not a default. Do Now, model, and every platform step carry an image.
- Source priority: (1) screenshot captured from the owner's demo student profile or owner account, stored under `cce-curriculum/resources/owner-authenticated-source/<platform>/<date>/` or `canvas-licensed/<sw>/<wk>/`; (2) FYF, Climber Notes, H&L teacher-resource images already in the repo; (3) free licensed photo (Unsplash, Pexels, Wikimedia CC0/CC-BY) with the credit on the slide and an entry in the deck folder `credits.json` (file, author, URL, license, date); (4) generated diagram only when no real artifact exists.
- If a slide references a notebook page, the slide shows the page (a OneNote or paper screenshot), not a description of it.
- Never rasterize. Never hand-edit a `.pptx`. Decks come from `build/decks/<week>/build.mjs` and must pass the deck lint and editability gate. No GIFs on masters.
- Check the existing image store before capturing. Capture only gaps.
- Look before you click. For platform visuals the order is: (1) what the repo already has; (2) the vendor's own help site and educator library (Xello: help.xello.world learning modules and Knowledge Base; H&L: teacher resources and Climber Notes), which already publish student-screen images, embeddable videos, and lesson slides; (3) a live click-through in the demo student account only for a specific screen nothing else shows, such as the exact completion badge or a "done when" state. Do not photograph every step of a flow.

## 6. Known slips to fix on sight (from the Week 0 audit, 2026-08-18)

- "Sign in with Google" on H&L steps (Week 0 Day 2 and 3 decks, guides, and day pages): wrong route, must be ClassLink. Also the Canvas home page H&L link must point at the ClassLink H&L tile, not app.hatsandladders.com.
- Student Guide "Were you absent or is H&L unavailable?" block: outage logic on a student page. Replace with "Absent? Start here" and student actions only, or drop it.
- "marked provisional", "marked for catch-up", "fixed value list", "same private notebook page" in student steps: teacher logic. Rewrite as the action the student takes.
- Facilitator Guide OneNote block that specifies table cells and distribution mechanics: journal overload. Replace with the page title and its stems.
- "Accept the original response without a separate verification or recopying step": implementer residue. Delete.
- "Presentation: ... Speaker notes include ... This guide contains the full lesson": narration about the artifact. Keep the two links only.
- Facilitator Guide missing a labeled Objective / DOL / Workbook / Platform / Notebook / Scaffolds / Exit evidence block: add the At a glance block from section 1.
- Notebook jobs that duplicate what H&L stores (re-writing the Work Values result): cut to the single connection stem.

## 7. Self-audit you must print before handoff

Print this table filled in, one row per page or deck. Do not hand off with a blank cell.

| Check | Result |
|---|---|
| Facilitator Guide has the At a glance block with all eight lines | |
| Student Guide: steps ≤ 7, done-when ≤ 3, no step > 4 lines | |
| Student banned list: 0 hits (list any) | |
| Teacher banned list: 0 hits (list any) | |
| Notebook page: none, or title + ≤ 3 stems, and each stem captures evidence not stored elsewhere | |
| Every slide classified; image source and credit recorded | |
| Deck built by the builder, lint + editability gate passed | |
| AI cliche pass run (teacher-voice-standard.md): hits and rewrites | |
| FYF pages cited as printed pages, H&L tasks named as in the app | |
| Differentiation names only scaffolds that exist and are linked | |

Then list what you could not verify and why. Do not claim parity or completion beyond what the table shows.
