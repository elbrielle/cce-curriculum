# Platform Reference

The CCE curriculum uses four technology platforms. This file describes what each one does so agents and editors understand references to them in the facilitator guides.

## Hats & Ladders (H&L)

**Role:** Primary career exploration platform used every week.

- Students are called "Climbers"; careers are called "Hats"
- **Assessments:** RIASEC Core Personality Assessment, Work Values Survey, Building Blocks activity
- **Features:** Cluster tour videos, pathway exploration, Myth Busters videos, From the Field interview videos, Hat profiles (perks/quirks/job gear/salary), Climber Profile page, Ladder Builder (career planning tool)
- **Login:** app.hatsandladders.com via Clever/ClassLink SSO
- **Teacher view:** Coach Dashboard (class roster, progress tracking, student results)
- **Data:** Education requirements, career descriptions, and growth information. Do not make DFW-localized salary data from H&L a dependency unless it is verified in the live account. Use Xello for district-localized salary work, with BLS or CareerOneStop as the independent source check.

Guides reference H&L with two markers:
- `[H&L PLATFORM]` — instruction that requires the platform (blue callout in docx)
- `[VERIFY IN H&L]` — content that could not be confirmed from the public website and needs teacher verification in the live platform (orange callout in docx)

## Xello

**Role:** Required career and college planning spine. Xello completion standards are spiraled across the year even when the week's main career content comes from FYF or H&L.

- **Assessments and profile tasks:** Use the district-configured Grade 8 Completion Standards view as the authoritative list. Matchmaker, Personality Style, Learning Style, Add Interests, Add Skills, and Favorite Clusters are confirmed Grade 8 tasks from the 2026-08-06 educator view. Do not assume a task is assigned to Grade 8 because it exists in Xello.
- **Features:** Career profiles, DFW-area salary and labor-market information, saved careers and clusters, experiences, goals, plans, postsecondary exploration, course planning, resumes, and completion reporting
- **Educator resources:** Each completion-standard task may include prerequisites, facilitator guides, lesson resources, worksheets, slide decks, and shareable videos. Inventory these from the educator view before writing the lesson.
- **Login:** District SSO
- **Curriculum rule:** The FYF realignment does not replace Xello completion standards. S&S column 8 assigns the yearlong sequence; daily plans must preserve the prerequisite chain and give teachers the attached Xello resources.
- **Canvas handling:** Use Xello-provided downloads and official shareable video links inside the authenticated Canvas course. Do not scrape or publicly rehost proprietary video streams.

## eDynamic Learning

**Role:** Supplemental online course content mapped to specific curriculum units. eDynamic is not a replacement for a required Xello completion standard.

- **Format:** Self-paced online modules with built-in assessments
- **Unit structure:** Each unit has a full title, cluster alignment, and key objectives
- **Mapping:** See `resources/edynamic-unit-map.md` for the full unit-to-week mapping

Guides reference eDynamic with:
- `[VERIFY IN eDynamic]` — content that needs verification in the eDynamic course platform (purple callout in docx)

## VILS Technology Integration

**Role:** Hands-on technology tools used for project-based learning activities. Irving ISD VILS Labs share a common baseline: Cricut machines, 3D printers, iPads, Snap Circuits, micro:bits, Sphero RVR robots, and either a Glowforge or xTool laser cutter. A weekly guide still states quantities, setup, safety checks, and a fallback because a shared baseline does not prove every device is charged, available, or working that day.

- **Sphero RVR+ / SpheroEDU** — robotics and coding activities (1SW: Manufacturing, Programming)
- **micro:bit / MakeCode** — physical boards are standard VILS equipment; MakeCode simulator remains the no-device fallback
- **Cricut / Glowforge / xTool** — fabrication tools; guides must distinguish cutter-specific setup and safety steps
- **3D Printers** — design and prototyping projects
- **Canva and Adobe Express** — district-approved design and generative-image tools
- **iPads / Snap Circuits** — available across VILS Labs when a module calls for mobile capture or circuit prototyping
- **Google Workspace** — Slides, Docs, Sheets for student deliverables

## Canvas

**Role:** Final official course home once the facilitator guides, student materials, grading tools, and platform sequence pass the teacher-readiness gate.

- Public GitHub Pages remains the development and review surface.
- Canvas holds teacher-facing copyrighted decks, licensed platform resources, modules, assignments, and student materials behind district authentication.
- Do not begin the production import until the module-readiness audit is substantially green and Elisha supplies an API token for that import session.
- Never store a Canvas token in the repository, documentation, shell history, or generated course package.

## Flag Color Reference

| Flag | Background | Text Color | Meaning |
|---|---|---|---|
| `[H&L PLATFORM]` | #E8F0FE (light blue) | #7030A0 (purple) | Requires H&L platform |
| `[VERIFY IN H&L]` | #FFF3E0 (orange) | #E65100 (dark orange) | Unverified H&L content |
| `[VERIFY IN eDynamic]` | #F3E5F5 (light purple) | #6A1B9A (dark purple) | Unverified eDynamic content |
