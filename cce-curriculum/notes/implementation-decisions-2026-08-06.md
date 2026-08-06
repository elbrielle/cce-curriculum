# Implementation Decisions: 2026-08-06

**Status:** BINDING. Elisha supplied these decisions after the day-1 readiness audit. They close or narrow several items in `day1-readiness-backlog.md` and govern the next implementation pass.

## D-13: Xello is a required completion spine

The FYF workbook realignment did not replace Xello. FYF and H&L carry career-exploration content; the district-configured Xello completion standards carry a yearlong student profile and planning sequence.

- Use the Grade 8 column in Xello's Completion Standards educator view as the authoritative task list.
- Preserve instructional time, prerequisites, completion evidence, and attached educator resources.
- S&S column 8 must map every required Grade 8 task to a workable place in the year.
- eDynamic Learning, Canva, Adobe Express, Code.org, and other tools remain supplemental unless the S&S assigns them for a specific purpose.
- Xello is the default district source for localized salary information. Verify major salary claims against BLS or CareerOneStop. H&L salary data may supplement the lesson but is not load-bearing unless verified in the live account.

## D-14: Canvas is the official delivery home

Canvas will become the official teacher and student course when the curriculum is ready for import. The public MkDocs site remains a development and review surface.

- Put licensed H&L decks and Xello classroom resources in authenticated Canvas modules, not on public GitHub Pages.
- Xello's current terms permit district users to use, download, copy, modify, perform, or display supplied educational materials for noncommercial in-class instruction during the license term.
- Prefer Xello-provided downloads and official shareable video or YouTube links. Do not rip hosted video streams.
- Delay the Canvas API import until the teacher-readiness gate is substantially green.
- Never store an API token in the repository or curriculum documents.

## D-15: VILS hardware baseline

All VILS Labs have a comparable baseline that includes Cricut machines, 3D printers, iPads, Snap Circuits, micro:bits, Sphero RVR robots, and either a Glowforge or xTool laser cutter.

This resolves whether the device class exists. It does not resolve quantity, maintenance, charging, consumables, room setup, or device-policy issues. Each hardware module still needs a Before Monday check and a no-device or reduced-device route.

## D-16: Multilingual support policy

Do not produce full translations by default. Use evidence-based language supports matched to the task:

- visuals and labeled examples
- chunked directions
- bilingual labels or short glossaries
- sentence frames and word banks
- partially completed models
- structured bilingual peer support
- read-aloud or audio support when available

Use a full translation for safety documents, family communication, consent/legal material, or a documented district requirement. Existing full translations stay available until reviewed; do not delete them mechanically.

## D-17: Six-weeks grading structure

- Minor grades: **40%** of the six-weeks grade, with at least **3** minor grades.
- Major grades: **60%** of the six-weeks grade, with at least **2** major grades.
- Performance bands: **Needs Improvement 60-69**, **Approaches 70-79**, **Meets 80-89**, **Masters 90-100**.
- Scores below 60 follow campus or district grading policy; no additional performance label is inferred here.

Exit tickets are primarily formative evidence. Do not create 30 separate daily grades by default. The assessment-mapping pass will select coherent checkpoints, platform completion evidence, weekly products, CFAs, and performance tasks to satisfy the 3-minor/2-major minimum.

## D-18: Approved generative tools

Canva and Adobe Express generative tools are approved. When FYF or a CCE lesson requires AI-assisted image generation, use one of those tools and retain a non-generative sketch or collage fallback.

## D-19: Climber Notes evidence boundary

The Climber Notes and speaker notes already supplied in the project folder are the full set Elisha has. Stop treating unseen speaker notes as a possible answer-key source. Where the delivered files do not contain an answer key, author and verify the key as a CCE teacher resource.

## What remains genuinely open

1. Obtain or verify Irving ISD course sequences for the 4-year course-map artifact.
2. Confirm the counseling window for Grade 8 course requests and the operational family-approval process. The live Xello configuration shows a May 1, 2027 parent-approval due date.
3. Confirm per-room quantities and working condition for hardware-heavy modules.
4. Confirm semester-exam requirements and how scores below 60 are labeled or recovered.
5. Obtain the 2026-27 pacing calendar and testing windows.
6. Import to Canvas only after the course passes the module-readiness gate and Elisha provides a token for the import session.

The authenticated Xello inventory is complete. See `xello-grade-8-reconciliation.md` and the teacher-facing `docs/resources/xello-grade-8-implementation.md`.
