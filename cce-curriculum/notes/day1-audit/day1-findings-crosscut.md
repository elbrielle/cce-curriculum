# Cross-Cutting Day-1 Readiness Findings

Scope: (1) workbook-side teacher-provisioning assumptions in *Find Your Future*, (2) the website's teacher-onboarding surface, (3) existing worksheet-production infrastructure and the teacher-facing pages already on the site.

Repo root: `/Users/elishalucero/Coding Projects/27 CCR Planning/.claude/worktrees/codebase-audit-school-year-398437`

Page convention throughout: **pr N** = printed page N in FYF (PDF page = pr + 6). Extract: `cce-curriculum/resources/reference-pdfs/IrvingFindYourFuture2026.txt`.

---

## Part 1 — Workbook-side assumption inventory

### 1.1 Master table: what the book assumes the teacher supplies

Every row is a place where *Find Your Future* itself hands work to the teacher. The book is a student edition and never provisions any of it.

| # | Printed p. | Activity | What the book assumes the teacher supplies | Book's exact hook |
|---|---|---|---|---|
| 1 | 25 | Safe or Spoofed? | Climber Notes deck — the sample inbox (phishing email images) | "Get Climber Notes from your teacher" |
| 2 | 28 | Website Revamp | Climber Notes deck — the website to audit; **plus a live browser to a real site** and sticky notes | "Get Climber Notes from your teacher. Use sticky notes…" |
| 3 | 48 | Clinton Lake Case | Climber Notes deck — 6 evidence files; sticky notes | "Get Climber Notes from your teacher" |
| 4 | 53 | Injured on the Trail | Climber Notes deck **and physical supplies** — sling cloth, finger splint, tape, one set per pair | "Get Climber Notes **and supplies** from your teacher" |
| 5 | 61 | Vitals in Motion | Climber Notes deck **and physical supplies** — blood pressure cuff, pulse oximeter, thermometer; chart paper or poster board for the nursing report | "Get Climber Notes **and supplies** from your teacher"; p.60 Step 1 asks students how to *use* a BP cuff and pulse ox |
| 6 | 64 | Ultrasound Detectives | Climber Notes deck — three ultrasound scan images | "Get Climber Notes from your teacher" |
| 7 | 69 | Smile Squad | Climber Notes deck — Mia's 5 dental X-rays + the risk-assessment reference chart | "Get Climber Notes from your teacher" |
| 8 | 156 | Safety Squad | Climber Notes deck — crash images for Vehicles A and B; sticky notes | "Get Climber Notes from your teacher" |
| 9 | 161 | Flight Line Fixers | Climber Notes deck — aircraft inspection images; sticky notes | "Get Climber Notes from your teacher" |
| 10 | 177 | Spot the Problem | Climber Notes deck — home inspection images **including the thermal/infrared pairs**; some images are decoys | "Get Climber Notes from your teacher. Study each image carefully. Some show real problems. Others are completely normal." |
| 11 | 182 | Unexpected Architecture | Climber Notes deck — the city's stated goals (the design brief) | "Get Climber Notes from your teacher. It will give you an overview of the city's goals" |
| 12 | 186 | Powerskill: Written Communication (HVAC) | Climber Notes deck — 4 AC service-ticket photos | "Get Climber Notes from your teacher" |
| 13 | 194 | Plumbing Under Pressure | Climber Notes deck — emergency plumbing basics | "Get Climber Notes from your teacher" |
| 14 | 209 | Quality Check | Climber Notes deck — frozen-pizza factory line images; sticky notes | "Get Climber Notes from your teacher" |
| 15 | 130 | Special Effects Makeup, DAY 2 | **The full SFX supply kit**, teacher-issued: liquid latex or eyelash glue, tissue paper/paper towels, pumpkin or sunflower seeds, dry pasta or lentils, coarse salt, tweezers, paint, and a **silicone practice skin** per student (table printed on p.129) | "Get your materials from your teacher" |
| 16 | 206 | Super Sports Manufacturing | **Hot glue gun and hot glue, scissors, craft gloves**, popsicle sticks, straws — the only power-tool-adjacent activity in the book | "Collect the following supplies: …" (the book lists them but assigns provisioning to nobody) |
| 17 | 217 | Teach Through Play | Chart paper, poster board, paper, markers, scissors, tape | "Use chart paper, poster board, and other art supplies" |
| 18 | 267 | Setting the Stage | Recycled materials + art supplies for a 3D prototype | "Use recycled materials and art supplies to build a small replica" |
| 19 | 82–83 | Patient Education | **A generative AI image tool** students can use. The book names no product, no login, no age gate, no district policy | "Use an AI tool to make an image from your prompt" (Steps 3 and 5) |
| 20 | 38, 58, 86, 102, 110, 126, 138, 170, 198, 212, 220, 254, 276 | App Exploration ×13 | 1:1 devices + working H&L logins + unblocked **Cluster Tour video** + the in-app **Game Time** minigame | "Get out your laptop. Open the Hats & Ladders app…" |
| 21 | 4–5 | Perks and Quirks | H&L app **plus "at least one additional source"** for salary/education research (open web) | "Research the details of each Hat using the Hats & Ladders app and at least one additional source" |
| 22 | 285–286 | Capstone Rung 3 | H&L app **plus** "other trusted sources, like career websites or job postings" | Step text |
| 23 | 290–291 | Capstone Rung 5 | **Live commercial job boards** on student devices; students search "[career] jobs near me" | "You can use job sites, company websites, or simple searches like…" |
| 24 | 287–289 | Capstone Rung 4 | **An outside adult** the student interviews (family member, teacher, coach, mentor). No in-class fallback printed | "Find a trusted adult to interview" |
| 25 | 22 | Building a Career Community | Three real named people in the student's life | Career-community list |
| 26 | 92, 166, 167, 260, 267 | Farm to Table · Transportation Survey · Visual Hook · Setting the Stage | A **"digital tool"** — infographic maker, survey builder (7 MCQ + 3 short answer), sketch/blueprint tool. The book names none | "Use a digital tool or chart paper…" |
| 27 | 28–29, 34, 50, 52, 60, 72, 115, 128, 152, 154, 157, 173, 205, 265 | 14 activities | **Open-web research time** on student devices, with no source list, no reading level filter, and no vetted-link set | "Conduct Research" / "Research Online" |
| 28 | 131, 271, 279 | SFX Day 3 ET · Behind the Microphone ET · Capstone options | **Recording + editing tools**: a 10-second close-up video, a recorded podcast episode, an "Unboxing My Future" video, and a **Website** as a capstone presentation option (i.e. web publishing) | Extra Time boxes + p.279 options list |
| 29 | 3, 16, 46–47, 49, 184, 224, 235, 243, 262, 263, 269 | 11 activities | **A visible countdown timer.** The book prints hard time limits (10-min career hunt, 5-min brainstorms, 1–2 min arguments, 3-min pitch, 30-min logo redesign, **exactly 10 minutes** to timebox on p.263, 30-second pitch) and provisions no clock | Step text |
| 30 | 117, 142, 268 | Hotel Rescue · Powerskill: Teamwork · Game On! | **Pre-assigned roles and groups.** Each student takes a distinct hotel role / studio role; the book assumes the grouping already happened | "Choose a Role" / "Build Your Team" |
| 31 | 61, 81, 90, 92, 95, 106, 173, 181, 183, 195, 271 | 11 activities | **Chart paper or poster board**, one sheet per student or per pair | "Use chart paper or poster board" |
| 32 | 28, 30, 92, 94, 104, 106, 135, 141, 147, 156, 161, 166, 183, 191, 202, 215, 217, 222, 246, 257, 260 | 21 activities | **Sticky notes** — the book's default brainstorming and annotation medium, used on 21 separate pages | "Use sticky notes…" |
| 33 | whole book | 57 activities + 23 Powerskill lessons | **Answer keys and scoring guidance.** The only rubric in 300 pages is the Capstone's 8-criterion / 32-point rubric on p.280 | — |

### 1.2 Findings

| Code | Where | Item | Evidence | What's needed |
|---|---|---|---|---|
| STRUCTURE | 14 activities (pr 25, 28, 48, 53, 61, 64, 69, 156, 161, 177, 182, 186, 194, 209) | Climber Notes `.pptx` decks are **gitignored** — a teacher who clones the repo gets only text extracts, never the images | `.gitignore:11-12` (`cce-curriculum/resources/climber-notes/*.pptx`); `git ls-files` returns 17 `.txt` + `INDEX.md`, zero `.pptx` | The decks are image-only (see 1.4). Host the actual decks somewhere a teacher can reach: Drive folder linked from the site, or committed as PDFs under `docs/resources/`. Until then 14 activities have no content on any machine but Elisha's. |
| STRUCTURE | same 14 | Even if the decks were shipped, `cce-curriculum/` is outside `docs_dir` and absent from `mkdocs.yml` nav — nothing under it renders on the site | `mkdocs.yml:19` `docs_dir: docs`; nav has no `cce-curriculum` entry | Either move the teacher-resource indexes into `docs/resources/` or publish a teacher-materials page that links out. |
| MISSING-SETUP | pr 82–83 (Patient Education, Health Science) | Activity requires students to run prompts through a **generative AI image tool**; the book names no product | pr 83 Step 3: "Use an AI tool to make an image from your prompt"; Step 5 regenerates | Name a district-approved tool, state the age/consent posture for 7th graders, and write an offline fallback (teacher-run generation projected, or hand-sketch the two iterations). This is the single highest-risk unprovisioned tech dependency in the book. |
| MISSING-SETUP | pr 38, 58, 86, 102, 110, 126, 138, 170, 198, 212, 220, 254, 276 | All 13 App Exploration pages assume 1:1 devices, live H&L logins, an unblocked in-app video, and a working Game Time minigame | Identical template text on all 13 pages | One reusable "App Exploration is blocked" fallback (partner at a working device, or the printed Hat cards) rather than 13 improvisations. |
| MISSING-SETUP | pr 290–291 (Capstone Rung 5) | Students search live commercial job boards from school devices | "job sites, company websites, or simple searches like '[career name] jobs near me'" | Named, filter-safe job sources (e.g. Texas Workforce / CareerOneStop job search) and a policy answer on commercial job boards. |
| MISSING-SUPPLY | pr 206 (Super Sports Manufacturing, Manufacturing) | **Hot glue guns + craft gloves + scissors**, per team | pr 206: "Collect the following supplies: Popsicle sticks and straws · Hot glue gun and hot glue · Scissors · Craft gloves" | Quantity decision, burn-safety protocol, and a low-temp or cold-build alternative. Not listed in `resources-status.md`'s supply table. |
| MISSING-SUPPLY | pr 60–61 (Vitals in Motion) | **Blood pressure cuffs, pulse oximeters, thermometers** — students are asked how to use each correctly, then to take real readings before/after activity | pr 60 Step 1 (four "correct way to use" questions); pr 61 Vital Signs Chart has Blood Pressure / Temperature / Pulse Rate / Oxygen Level rows | Count per class (one set per pair), a sanitation protocol, and a paper-simulation fallback if the tools aren't funded. `resources-status.md:65` calls this deck load-bearing but names no hardware. |
| MISSING-SUPPLY | pr 53 (Injured on the Trail) | Sling cloth + finger splint + tape, one set per pair | pr 53 Step 2; pr 53 Step 4 asks students to "Describe how you used the sling and splint" | Already tracked (`resources-status.md:62`). Included here for the roll-up. |
| MISSING-SUPPLY | pr 129–130 (Special Effects Makeup) | Full SFX kit **including a silicone practice skin per student** — the one item the repo's supply note does not name | pr 130 Step 2: "Apply a thin layer of adhesive to the **silicon practice skin**" | Add the practice skin to the ordering list; `resources-status.md:63` names "a skin-safe base surface" without specifying the consumable. |
| MISSING-SUPPLY | pr 61, 81, 90, 92, 95, 106, 173, 181, 183, 195, 271, 217 | Chart paper / poster board on **12 separate pages** | Grep of the extract | A single per-six-weeks chart-paper/poster-board count so it gets ordered once instead of scrounged 12 times. |
| MISSING-SUPPLY | 21 pages (pr 28, 30, 92, 94, 104, 106, 135, 141, 147, 156, 161, 166, 183, 191, 202, 215, 217, 222, 246, 257, 260) | Sticky notes are the book's default brainstorm medium on 21 pages | Grep of the extract | Sticky notes belong on the year-one consumables order, not in "standard classroom stock." At ~1 pad per student per six weeks this is a budget line. |
| MISSING-SUPPLY | pr 3, 16, 46–47, 49, 184, 224, 235, 243, 262, 263, 269 | **Visible countdown timer** for 11 timed activities, including a hard "exactly 10 minutes" timebox that is the entire point of Powerskill: Time Management | pr 263: "You and a partner have exactly 10 minutes"; pr 262: "You have 30 minutes"; pr 243: "Can you say it in about 30 seconds?" | One projected timer tool named once (site-wide), not per week. |
| MISSING-RUBRIC-OR-KEY | whole book | **80 of the book's 81 assessable sections have no key and no rubric.** Only the Capstone carries one (p.280, 8 criteria × 4 levels = 32 pts) | Workbook inventory §7.3; verified by grep — "rubric" appears only in the Capstone | At minimum, keys for the activities with objectively-checkable answers: Safe or Spoofed (which emails are spoofed), Smile Squad (cavity risk determination), Ultrasound Detectives (which condition), Spot the Problem (which images are decoys — pr 177 explicitly says some are normal), Flight Line Fixers (MEL Go/No-Go), Powerskill: Critical Thinking (vet vitals vs. normal ranges), Machine Breakdown Mystery. A teacher cannot grade these without knowing the intended answer. |
| MISSING-DECK | pr 25, 28, 48, 53, 61, 64, 69, 156, 161, 177, 182, 186, 194, 209 | The keys above would live in the decks — but the deck extracts contain **no answer text**, only image counts | e.g. `Climber Notes_ Smile Squad.txt` = 7 slides, five of them "X-Ray #N [1 image(s)]" and nothing else; `Climber Notes_ Clinton Lake Case.txt` = 6 evidence titles, no analysis | Confirm visually in the `.pptx` whether speaker notes carry answers. If they do not, the keys must be authored. |
| REVISE | pr 130 (SFX Day 2) | Latex allergy: the book's primary adhesive is "Liquid Latex or Eyelash Glue" and its material table names latex twice | pr 128–129 | Already flagged in `resources-status.md:63`. Keep the latex-free substitution prominent on the day page, not only in the backlog. |
| VAGUE-SPEC | pr 92, 166, 167, 260, 267 | "Use a digital tool" with no tool named — including a **survey builder** that must produce 7 MCQ + 3 short-answer items (pr 166) | Step text | Name the district tool per instance (Google Forms for the survey, Canva for the infographic). |
| PREP-ACTION | pr 117, 142, 268 | Roles must be pre-assigned before class (hotel roles, team roles, studio roles) | "Choose a Role" / "Build Your Team" | Goes in the weekly "Before Monday" list. |
| PREP-ACTION | pr 287–289 (Rung 4) | The Strengths Interview happens **outside class hours** with an adult the student must recruit | pr 287 | Needs a lead time (assign a week ahead), a parent-facing note, and an in-school fallback interviewer for students with no available adult. |

### 1.3 Climber Notes coverage story

**Every one of the 14 book callouts has a matching deck.** Cross-checking the workbook callout pages against `cce-curriculum/resources/climber-notes/INDEX.md`:

| Book callout (printed p.) | Activity | Deck in INDEX | Match |
|---|---|---|---|
| 25 | Safe or Spoofed? | Safe or Spoofed | ✅ |
| 28 | Website Revamp | Website Revamp | ✅ |
| 48 | Clinton Lake Case | Clinton Lake Case | ✅ |
| 53 | Injured on the Trail | Injured on the Trail | ✅ |
| 61 | Vitals in Motion | Vitals in Motion | ✅ |
| 64 | Ultrasound Detectives | Ultrasound Detectives | ✅ |
| 69 | Smile Squad | Smile Squad | ✅ |
| 156 | Safety Squad | Safety Squad | ✅ |
| 161 | Flight Line Fixers | Flight Line Fixers | ✅ |
| 177 | Spot the Problem | Spot the Problem | ✅ |
| 182 | Unexpected Architecture | Unexpected Architecture | ✅ |
| 186 | Powerskill: Written Communication (HVAC) | PowerSkill Written Communication | ✅ |
| 194 | Plumbing Under Pressure | Plumbing Under Pressure | ✅ |
| 209 | Quality Check | Quality Check | ✅ |

**Three decks have no book counterpart** and are therefore invisible to a teacher reading only the workbook:

- **Exploring Your Work Values** — carries the Work Values lesson driving the app task. FYF prints no work-values page at all.
- **Learning Your Core Personality Types** — the six core types (Doer, Analyzer, Creator, Helper, Persuader, Organizer). FYF prints no personality page.
- **Capturing the Feeling** — UNIDENTIFIED. Four image-only slides, no extractable text, no assigned week.

These two content-bearing orphans are the *only* source for Week 0's core personality and work-values instruction. If they are lost, 1SW Wk0 Days 2–3 have no content.

**The reachability problem (the real finding).** The decks are:
1. `.pptx` binaries **excluded by `.gitignore`** — they exist only on Elisha's local machine. A cloned repo has 17 `.txt` files and zero decks.
2. Under `cce-curriculum/`, which is **outside `docs_dir`** and absent from `mkdocs.yml` nav — so nothing there is on the website even if committed.
3. Represented in-repo by extracts that are **image counts, not images**. `Climber Notes_ Smile Squad.txt` is 7 slides of "X-Ray #N [1 image(s)]". `Climber Notes_ Clinton Lake Case.txt` is six evidence-file titles. The actual X-rays, evidence documents, crash photos, aircraft photos, inspection images, service-ticket photos, and factory-line photos — the entire substance of 14 activities — are recoverable from nowhere in the repository.

`docs/resources/resources-status.md` states five times that a deck is "already in the repo at `cce-curriculum/resources/climber-notes/`" (lines 61, 65, 69, 73–78). For a teammate cloning from GitHub, that statement is false. This is the most consequential STRUCTURE finding in my scope.

---

## Part 2 — Teacher onboarding surface

What the live site gives a brand-new teacher before day 1. Nav audited from `mkdocs.yml:21-…`; site pages are `docs/index.md`, `docs/scope-and-sequence.md`, and five pages under `docs/resources/`.

| Code | Where | Item | Evidence | What's needed |
|---|---|---|---|---|
| STRUCTURE | site nav | **No "Start Here" / course-orientation page.** `docs/index.md` is the closest thing, and it is a status dashboard (what's built, what isn't) plus a nav explainer — not an onboarding path | `docs/index.md` §"Current State", §"How to Navigate This Site"; `mkdocs.yml` nav opens straight into Scope & Sequence then 1SW | A first-page "Before You Teach Week 0" that sequences: get platform access → order supplies → print the packet → read the prototype week. Currently a new teacher's first instruction is "read 5SW Wk1 because it was built first" (`index.md`, last section), which is a *format* orientation, not a *start-of-year* orientation. |
| MISSING-PRINTABLE | site nav | **No 2026-27 pacing calendar.** Nothing in `docs/` maps a week number to a real date, names the six-weeks grading-period boundaries, or accounts for holidays, testing windows, or short weeks | Grep of `docs/` for august/september/january/school calendar/holiday break/benchmark window returns only prose references ("in January", "since September") inside lesson text — zero calendar artifacts | A one-page 2026-27 calendar: date ranges per six-weeks block, week-number → week-of mapping, the days that vanish (holidays, PD, testing), and where the slack is. School starts in ~2 weeks; without this, "1SW Wk0" is not locatable in time. |
| STRUCTURE | site nav | **`PLATFORMS.md` is not on the site.** It lives at repo root, outside `docs_dir`, and is not in nav | `mkdocs.yml:19` `docs_dir: docs`; `ls *.md` → PLATFORMS.md, PATHWAYS.md, GUIDE-FORMAT.md, PLANNING.md, README.md all at root | Move or mirror the platform reference into `docs/resources/`. Same applies to `PATHWAYS.md`, which is the Irving CTE pathway reference the district pages depend on. |
| MISSING-SETUP | site-wide | **No platform setup instructions.** Nothing tells a teacher how to get an H&L class created, how students are rostered, what a Coach Dashboard is, whether Xello is licensed for 7th grade, or how eDynamic units get enrolled | Setup guidance exists only as scattered prose inside `docs/1sw/wk0-classroom-routines/day2.md:44-58` and `overview.md:31-46` (SSO via Clever/ClassLink, "pre-rostered"), and `PLATFORMS.md` (off-site) names only `app.hatsandladders.com` + "District SSO" | A `docs/resources/platform-setup.md`: who to email for H&L access, how classes/rosters are created and by whom, the Coach Dashboard walkthrough, Xello license status for grade 7, eDynamic unit enrollment path, and the escalation contact for each. Every one of these is a first-week blocker, and `day2.md:55` even says to "Confirm campus SSO integration before this lesson" without saying with whom. |
| MISSING-PRINTABLE | site nav | **No syllabus and no parent/guardian letter** | No file in `docs/` matches; `resources-status.md` does not list either | A one-page syllabus (course description, what students produce, grading, platforms, the workbook) and a parent letter. The parent letter is load-bearing: Capstone Rung 4 requires students to interview an adult at home (FYF pr 287), and 6SW Wk5 Day 3 has students handle personal information on a practice job application. |
| MISSING-PRINTABLE | site nav | **No substitute guidance of any kind** | Grep for "substitute"/"sub plan" across `docs/` returns 9 hits — 8 are the verb "substitute X for Y" inside lesson prose; the only real reference is `docs/resources/resources-status.md:170`, which lists "Substitute-teacher plans for each week" as ⬜ not built | At minimum a generic "sub day" fallback that runs on the workbook alone (no logins, no decks, no supplies) plus a per-six-weeks note on which days are safe to hand a sub. A course this platform-dependent fails hardest on an unplanned absence. |
| MISSING-PRINTABLE | site nav | **No print-logistics guidance.** Nothing says how many copies of what, when | The 178 exit-ticket PDFs are linked individually from day pages with no aggregate print instruction; `resources-status.md:79` mentions "a print packet, seven CCE artifacts per student" for 6SW Wk5 only | A per-six-weeks print manifest: which PDFs, how many copies, single- vs double-sided, when to send to the copy room. 178 individual PDF links is a fine *reading* interface and an unusable *printing* interface. Consider a per-week or per-six-weeks combined PDF. |
| MISSING-PRINTABLE | site nav | **No materials-ordering checklist**, despite the supply dependencies now being known | `resources-status.md:171` lists "Materials ordering checklist per six-weeks block" as ⬜ not built; the Phase B/C dependency tables (lines 59-79) are the raw input for it but are prose, not an order form | A single consumables + equipment order list with quantities, derived from Part 1's table plus the per-week audits. Ordering lead time in a district is weeks; this is the most time-sensitive missing artifact after the calendar. |
| STRUCTURE | `docs/resources/` | Teacher-facing indexes for the two on-hand resource sets (17 Climber decks, 8 H&L teacher PDFs) exist only at `cce-curriculum/resources/*/INDEX.md`, off-site | Neither INDEX is in `mkdocs.yml` nav | Publish both indexes under `docs/resources/` so a site-reading teacher knows a Daily Performance & Career Skills Rubric and an early-finisher activity bank exist at all. |
| STRUCTURE | `cce-curriculum/resources/edynamic-unit-map.md` | `PLATFORMS.md` points at an eDynamic unit map that is not on the site | `PLATFORMS.md` §eDynamic: "See `resources/edynamic-unit-map.md`"; file is at `cce-curriculum/resources/`, not `docs/resources/` | Mirror onto the site or drop the pointer. |
| REVISE | `docs/index.md` | The homepage's own warning says slides, worksheets, and CFAs "are not yet built" and sends the teacher to the backlog page — accurate, but it is the *only* pre-teaching orientation, and it opens on what is missing rather than on what to do first | `docs/index.md` warning admonition | Keep the honesty; add the actionable path in front of it. |

**Onboarding surface, summarized.** The site has 6 non-lesson pages: `index.md`, `scope-and-sequence.md`, and `resources/{resources-status, teks-coverage-matrix, free-resource-directory, facilitation-strategies, health-science-extensions}.md`. Of those, exactly two (`facilitation-strategies.md`, `free-resource-directory.md`) are usable *by a teacher on day 1*. The rest are planning and audit artifacts. Nothing on the site tells a new teacher what date week 1 starts, how to get logins, what to buy, or what to print.

---

## Part 3 — Existing worksheet infrastructure

### 3.1 The three "worksheet" branches are already merged — there is nothing to revive

| Branch | `git log main..origin/<b>` | `git diff --stat main...origin/<b>` | Ancestor of main? |
|---|---|---|---|
| `origin/worksheet-pdf-pipeline` | empty | empty | **yes** — tip `357f8e4` (2026-04-28) |
| `origin/round-2-format-templates` | empty | empty | **yes** — tip `89033db` (2026-04-28) |
| `origin/round-3-format-variants` | empty | empty | **yes** — tip `07e9c4e` (2026-04-28) |

All three are historical development branches whose tips are commits on `main`. `main` has moved past all of them (three FYF-realignment commits dated 2026-08-05 sit on top). **Nothing exists on those branches that is not already on `main`.** The "worksheet-pdf-pipeline" name is slightly misleading: its commit series (`617aeec` → `357f8e4` → `91d635d` → `89033db` → `6c9b357` → `763f199`) *is* the exit-ticket pipeline now living at `build/build_pdfs.py`.

### 3.2 What the shipped pipeline actually is, and whether it can mass-produce worksheets

`build/build_pdfs.py` is 64.6 KB and does markdown → Jinja2 HTML → Playwright/Chromium → PDF. Supporting assets: `build/exit_ticket_template/{template.html.j2, exit-tickets.css, exit-tickets-round2.css, exit-tickets-round3.css, round2-mockups.html, round3-mockups.html, assets/}`. Output: 178 branded PDFs in `docs/resources/exit-tickets/`. `build/inject_pdf_links.py` writes the `[Printable PDF]` links back into day files.

It ships **10 base formats and 6 variants**, all with dedicated layout templates:

- F01 Diagnostic MCQ (+ `multi_q_mcq` variant) · F02 Comparison Matrix · F03 Venn Diagram · F04 Concept Map (+ `seven_bubble`) · F05 Decision Tree (+ `procedural_tree`, `routed_tree`) · F06 Ranked Justification (+ `prose_ranked`) · F07 Mini-Case (+ `feedback_sandwich`) · F08 Trade-off · F09 Short Constructed Response · F10 3-2-1 Reflective. Plus a `fallback` renderer for unstructured payloads.

**Assessment: this is a viable worksheet factory with two specific gaps.**

Reusable as-is: the Chromium render path, the Irving ISD branded chrome, the CSS design system (three rounds), the writing-slot/ruled-line rendering, the SVG glyph set, and the slug/output/link-injection plumbing. A worksheet generator does not need to be built from scratch.

The two gaps:
1. **Input coupling.** `parse_day_file()` scans day markdown for the `**EXIT TICKET** (Format Name)` marker via `EXIT_TICKET_RE`, one ticket per day file. A worksheet run needs a different source — either a new marker (`**WORKSHEET** (Format)`) or a standalone worksheet-source directory — plus a `collect_*` entry point. This is an additive change to a well-factored module, not a rewrite.
2. **Page budget.** Only 3 of 10 formats are half-page (`mcq`, `short_response`, `three_two_one`); the rest are full-page and were tuned to fit **one Letter page** (commit `763f199` "Tighten F01b and F05c so each fits on one Letter page"). Multi-page worksheets — the career research worksheet, the Individual Career Plan template, the Personal Budget template, the Skilled Trades Comparison Matrix — need pagination the template does not currently do.

Also carry forward the known operational quirk documented in CLAUDE.md: **PDF regeneration is not byte-idempotent** (Chromium stamps a creation date), so any mass run needs the verify-with-pdftotext-then-`git restore` cleanup step.

### 3.3 `docs/resources/` inventory on main — build on these, don't duplicate

| Page | Lines | What it is | Backlog relationship |
|---|---|---|---|
| `resources-status.md` | 220 | **The existing backlog.** Legend (✅/🟡/⬜/🚫), a Built & Ready table, the exit-ticket pipeline section, a reference-assets table, two "new hard dependencies" tables from the Phase B and Phase C FYF realignments (lines 55–79), then the Still Needed sections: presentation slides, assessment worksheets (with an 11-item named list, lines 108–118), CFAs (1 of 6 built, with a per-block TEKS table), teacher edition, student packet, video library, platform verification. Updated 2026-08-05. | **This is the page the Day-1 backlog must merge into, not replace.** It already names ~11 of the missing worksheets, already lists "substitute-teacher plans" and "materials ordering checklist" as unbuilt (lines 170–171), and already has an intake protocol (lines 202–211). Extend its tables; do not start a parallel backlog. |
| `facilitation-strategies.md` | 98 | Research-based discussion/reading structures (QSSA, Think-Pair-Share, RallyRobin, RoundRobin, Talk-Read-Talk-Write, Jigsaw, Stand Up Hand Up Pair Up) with time budgets, group sizes, DOK targets, and CCE fit notes | Genuinely day-1 usable. A substitute-plan or sub-friendly-day page should reference these rather than re-explain them. |
| `free-resource-directory.md` | 41 | Table of ~35 free external resources (BLS, CareerOneStop incl. practice job application / interview prep / resume guide, MyNextMove, AMLE Canva playbook, Roadtrip Nation, Code.org) with URL, type, best-for, cost, clusters | Directly answers several Part 1 gaps: CareerOneStop's job search is the filter-safe substitute for Rung 5's commercial job boards, and its practice job application backs 6SW Wk5. Extend this table rather than authoring new link lists. Note: a *different* copy exists at `cce-curriculum/resources/free-resource-directory.md` — the two files differ; reconcile before either is cited as canonical. |
| `teks-coverage-matrix.md` | 70 | Three-tier (Explicit / Implicit / Gap) map of every §127.2 d(1)–d(8) standard to its weeks | Out of Day-1 scope but is the right home for any CFA blueprint work. Also duplicated-and-drifted at `cce-curriculum/resources/teks-coverage-matrix.md`. |
| `health-science-extensions.md` | 83 | Placeholder content for PT/PTA and two other specialties, carrying a `SOURCE_PENDING` tag and an explicit "do not promote to primary content" instruction | Deliberate placeholder. Not a finding. |
| `exit-tickets/` | 178 PDFs | The generated exit-ticket worksheets | The only student-facing printables that exist today. |

| Code | Where | Item | Evidence | What's needed |
|---|---|---|---|---|
| STRUCTURE | `docs/resources/free-resource-directory.md` vs `cce-curriculum/resources/free-resource-directory.md` | Two copies of the resource directory that have diverged | `diff -q` → DIFFERS | Pick one canonical copy; the site copy should win. Same problem with `teks-coverage-matrix.md`. |
| VAGUE-SPEC | `build/build_pdfs.py` | No worksheet input path — the parser is hard-wired to one `**EXIT TICKET**` marker per day file | `EXIT_TICKET_RE` (line 144), `parse_day_file()` (line 168), `collect_day_files()` (line 1618) | If the backlog calls for mass worksheet production, spec the input contract first (marker vs. separate source dir) and the multi-page rule; the renderer itself is ready. |

---

## Scope summary

**Counts by code (cross-cutting scope only; per-week findings are the sibling agents'):**

| Code | Count |
|---|---|
| STRUCTURE | 8 |
| MISSING-PRINTABLE | 5 |
| MISSING-SETUP | 4 |
| MISSING-SUPPLY | 6 |
| MISSING-RUBRIC-OR-KEY | 1 (covering 80 workbook sections) |
| MISSING-DECK | 1 (covering 14 activities) |
| VAGUE-SPEC | 2 |
| PREP-ACTION | 2 |
| REVISE | 2 |
| **Total** | **31** |

**The five worst gaps:**

1. **The Climber Notes decks are unreachable by anyone but Elisha.** The `.pptx` are gitignored, `cce-curriculum/` is off-site, and the tracked `.txt` extracts contain image *counts*, not images. Fourteen activities across 1SW, 2SW, 4SW, 5SW have literally no content without them — plus the two orphan decks that are the sole source for Week 0's personality and work-values instruction. `resources-status.md` asserts five times that these are "already in the repo"; from a fresh clone that is false.
2. **No 2026-27 pacing calendar.** School starts in about two weeks and nothing in `docs/` binds a week number to a date, marks the six-weeks boundaries, or accounts for holidays and testing. Every other planning artifact depends on this one.
3. **No platform setup path anywhere on the site.** H&L class creation, rostering, the Coach Dashboard, Xello grade-7 licensing, and eDynamic enrollment are undocumented; the only guidance is prose buried in 1SW Wk0 Day 2 that says "confirm SSO before this lesson" without naming who to confirm with. `PLATFORMS.md` exists but sits at repo root, outside the site.
4. **No answer keys for 80 workbook sections.** The book's only rubric is the Capstone's 32-point one. At least seven activities have objectively-correct answers a teacher cannot verify — Spot the Problem literally plants decoy images and never says which are decoys. The decks that would hold the keys appear to be image-only.
5. **No print manifest and no materials order list.** 178 PDFs linked one-at-a-time is unusable as a printing interface, and the supply dependencies (hot glue guns, BP cuffs and pulse oximeters, silicone practice skins, sticky notes on 21 pages, chart paper on 12) have never been consolidated into something a teacher can hand to a purchasing clerk. District ordering lead time makes this the second most time-sensitive item after the calendar.

**Cross-cutting patterns worth naming once:**

- **The repo/site boundary is the single largest structural defect.** `mkdocs.yml` sets `docs_dir: docs`, so everything in `cce-curriculum/` and every root-level `.md` (PLATFORMS, PATHWAYS, GUIDE-FORMAT) is invisible to a site-reading teacher. Sibling auditors will flag day-page references to those paths as STRUCTURE findings repeatedly; the fix is one decision (publish a teacher-materials section under `docs/resources/`), not 36 fixes.
- **"Already in the repo" ≠ "available to the teacher."** Applies to the Climber decks, the H&L teacher-resource PDFs (also gitignored), and the reference PDFs. Every backlog line that says "already on hand" needs re-testing against a fresh clone.
- **The book's default media are sticky notes and chart paper** — 21 and 12 pages respectively. Treat both as year-one consumables, not classroom stock, and stop flagging them per-week.
- **Time limits are printed but clocks are not.** Eleven activities carry hard time budgets, one of which (Powerskill: Time Management, pr 263, "exactly 10 minutes") *is* the lesson. One named projected timer solves all eleven.
- **The worksheet factory already exists.** Do not spec a new PDF pipeline. `build/build_pdfs.py` plus the three CSS rounds and Jinja2 template render 16 designed formats to Irving-branded Letter pages today; it needs a new input contract and a multi-page rule, nothing more. All three "worksheet" branches are merged ancestors of `main` with zero unique content.
- **`docs/resources/resources-status.md` is the backlog and knows most of this already.** It lists substitute plans, the materials checklist, answer keys, slides, and 11 named worksheets as unbuilt. The Day-1 audit's job is to make those entries specific and quantified, not to open a second ledger.
