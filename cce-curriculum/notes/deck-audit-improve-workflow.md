# Post-week deck audit and improve workflow

Status: adopted 2026-08-18 (owner rulings in section 6). Applies from 1SW Wk1 onward. Week 0 was the pilot.

## 1. Who does what

| Step | Owner | Tool |
|---|---|---|
| Language audit (slides, Student Guide, Facilitator Guide) | Claude | `build/decks/lib/slide_lint.mjs` (extended), Canvas page lint |
| Image audit and capture | Claude, owner signs in | in-app browser, owner Google/ClassLink account or the demo student account |
| Fixes | Claude | edit `build/decks/<week>/build.mjs` and `dayN.json`; never hand-edit a `.pptx` |
| Rebuild + gate | Claude | `node build/decks/qa_week0_decks.mjs` pattern, one gate script per week |
| Canvas reconcile | Claude | token via stdin only |
| Drive files.update on existing IDs | Codex | Drive and Slides API |
| Drive verification + parity contract | Claude | Drive connector (read only), `build/google_workspace/verify_parity.py` from the main workspace |

Reason for the split: the Claude Drive connector cannot upload from a local path, replace file content, touch Slides, or read revisions (`create_file` = inline base64 only; `update_file` = title and parentId only). It can verify sizes, slide text, folder contents, and trash state.

## 2. Pass 1: language scoping audit

Three tiers (owner decision 2026-08-18, see `week0-live-launch-lessons-learned.md`):

1. Projected slides: student-facing only. Assume the teacher's route. No route menus, fallbacks, minute ranges, gradebook admin, teacher moves.
2. Student Guide (Canvas): student actions and support. Platform-down route only inside the expandable absence section.
3. Facilitator Guide and speaker notes: routes, fallbacks, pivots, timing, grading.

Audit scope per week: 5 daily decks, weekly Lucero deck, 5 Student Guide pages, 5 Facilitator Guide pages.

Checks:

- Tier 1 banned patterns (`BANNED_SLIDE_PATTERNS`) over every slide text object. Already enforced; builders throw.
- Tier 2 banned patterns over Student Guide HTML outside the absence `<details>` block: teacher moves, "Minor/Major", minute ranges, "if the platform is down", "route", honorific errors.
- Tier 3 required labels in the Facilitator Guide and speaker notes (`REQUIRED_NOTES_LABELS`).
- Student readability over slides and Student Guide: sentence length cap 15 words, one verb per instruction line, no idioms from a small banned list, no TEK codes in student text, Spanish stems present where the Do Now uses a stem.
- Honorific and name check: Ms. Lucero on private decks only; shared masters carry no teacher name.

Output: `cce-curriculum/notes/audits/<sw>-<wk>-language-audit.md`. Hits listed by artifact, slide or line, reason, sample. Owner approves the list before fixes land.

Enforcement: deck builders block on tier 1 (already). Canvas builders run tier 2 and 3 as report-only for the first audited week, then flip to blocking.

## 3. Pass 2: image audit

Classify every slide: (a) platform screenshot, (b) real-world photo for context, (c) diagram, (d) text-only is right.

Source priority:

1. Live screenshot captured in the in-app browser. Store under `cce-curriculum/resources/owner-authenticated-source/<platform>/<capture-date>/` or `canvas-licensed/<sw>/<wk>/`. Gitignored. Never on the public site.
2. FYF, Climber Notes, and H&L teacher-resource images already in the repo.
3. Attributed free photos (Unsplash, Pexels, Wikimedia CC0/CC-BY). Credit line on the slide plus a `credits.json` per deck folder: file, author, source URL, license, date pulled.
4. Generated diagram only when no real artifact exists.

Existing store as of 2026-08-18: 41 H&L screens (`hats-and-ladders/screens/` and `hats-and-ladders/2026-08-17/screenshots/`), 2 OneNote, 1 Xello, plus `canvas-licensed/` sets for most weeks. Check the store before capturing.

GIFs: PowerPoint plays them; Google Slides import does not reliably. No GIFs on masters. Use two or three sequential screenshots on one slide and link the official platform video in the Facilitator Guide.

Gate additions to the week QA script:

- every image slide has alt text
- every non-licensed image has a `credits.json` entry
- image byte cap per slide (reuse the Canvas image-performance thresholds)
- screenshots carry a capture date in the deck manifest so stale UI is flagged next year

## 4. Pass 3: rebuild through the builders

Fixes go into `build.mjs` or `dayN.json`. Rebuild, run the week gate, regenerate the weekly Lucero deck from the masters. Never hand-edit a `.pptx`, never rasterize, never rebuild the gated Week 0 masters outside their builders.

## 5. Pass 4: distribution and parity

1. Canvas reconcile (Claude, token via stdin).
2. Hand Codex the ID list, local paths, sha256 from `google-workspace-parity-manifest.json`. Codex runs files.update on the same IDs, no duplicates.
3. Claude verifies through the connector: raw byte size equals local, native slide count and text, temp files trashed.
4. `verify_parity.py` from the main workspace. Parity is claimed only when Canvas, Drive, and the public mirror all pass against the same source hashes.

## 6. Owner rulings 2026-08-18

- Claude may sign in with the owner's Irving Google or ClassLink account, or the demo student account, to capture screens. Owner approves the sign-in in the browser; Claude never types credentials.
- Prefer already-captured screenshots; capture only what is missing.
- Canvas page lint starts report-only for one week, then blocks.
