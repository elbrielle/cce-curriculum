---
name: cce-slide-decks
version: 1.0.0
description: Build teacher-ready classroom slide decks for one CCE instructional day from the existing lesson plan, the Canvas student page, and real visuals (workbook page crops, live site and BLS screenshots, Canvas button renders). Use when a week needs slides, when a teacher-received deck needs to be brought up to the CCE standard, or when a lesson plan changes and its deck must follow. Do not use for Canvas page authoring (cce-module-authoring) or for the owner's personal one-off decks.
---

# CCE slide decks

One deck per instructional day. The deck is the projected version of the lesson plan: same pacing, same workbook pages, same IISD strategy, same buttons the student page already has. It never adds content the plan does not have, and it never explains an assignment the students have not seen yet.

Reference deck: `build/slides/1sw-wk3/day2.js` (Website Revamp). Library: `build/slides/lib.js`. Gate: `build/slides/qa_deck.py`. Assets: `build/slides/<week>/assets/`. Output: `docs/resources/slides/<week>-dayN.pptx` plus a rights-clean twin in `docs/resources/slides/public/`.

## 0. Rules that do not bend

- **Real visuals only.** Workbook page crops from the FYF PDF, screenshots of the actual site or tool, BLS OOH pages, renders of the Canvas student page buttons. No generated art, no stock icons, no clip art. A slide with no real visual available gets white cards and text, not a decoration.
- **Licensed images are placeholders in the public twin.** Every `d.image()` of a workbook page, Climber Notes slide, or Xello lesson page passes `{ licensed: true, fyfPage: N }`. `CCE_PUBLIC=1` swaps them for a "Find Your Future p. N" card. The public site never carries the licensed deck.
- **One deck, one day, one lesson boundary.** No pulling next week's content forward.
- **Never write HQIM, TEKS codes, 5E phase names, or "Minute 0-5" on a slide.** Pacing lives in the speaker notes. Name the thing: "Find Your Future p. 28", "Hats & Ladders", "Xello".
- **Every slide has speaker notes ending in a `[Sources]` block.** Use `D.SRC.*` so the block names the workbook pages, the site URL and capture date, the BLS page, or the Canvas capture date.
- **Speaker notes are the teacher's minute-by-minute.** Pacing, the lap targets from the plan's Active Monitoring, the two known misconceptions, what to trim if time slips, and where the buttons live.
- **Plain teacher voice.** No "you've got this", no "let's dive in", no closing platitudes. A "Before you go" slide lists what should be done and names tomorrow. Nothing else.

## 1. Read before building

1. `docs/<sw>/<week>/dayN.md` and `overview.md`: pacing, workbook pages, the IISD strategy assigned to that day with its stems verbatim, the word bank, the exit ticket text, the deliverable.
2. The Canvas student page for that day (`build/canvas/templates/<week>-dayN-student.html` or the live page via `build/slides/crop.py fetch`): every button label and what it opens. The slide names the button by its exact label.
3. `build/worksheet_sources/<week>-*.md`: the worksheet rows students fill in.
4. The FYF text extract for the printed pages (`cce-curriculum/resources/reference-pdfs/IrvingFindYourFuture2026.txt`, printed = PDF − 6). Quote the workbook's own step text on the slide; do not paraphrase a numbered step.
5. Live sources named in the plan (the practice site, BLS pages, Xello lesson). Screenshot them the day you build and record the date. If a live number disagrees with a printed guide, the slide shows the live page, the notes flag the drift, and the guide gets a regeneration ticket.

## 2. Deck shape (10 slides is typical; 8 to 12)

1. **Title**: big title in the day's plain words, blue subtitle, "College and Career Exploration · Week N · Day N", what to bring.
2. **As you enter**: the plan's warm-up question verbatim on a white card, one sentence stem, "Two people share."
3. **Today you will**: 3 or 4 numbered lines with page numbers. Word of the day underneath.
4..n. **The lesson, one workbook step or activity per slide**: the workbook crop on the left, the instruction card on the right, a muted line with minutes and voice level. Work slides carry "Check yourself" (the plan's lap targets, rewritten for students), "You are done when", and a yellow "Finished early?" box.
- **The strategy slide**: whichever the plan assigns that day (Stop and Jot, Think-Pair-Share, Turn and Tell, Talk then Write, Chunking shows up as one-step-per-slide). Use the plan's stems verbatim. One or two per deck, where students talk or write. Not every slide needs a stem.
- **Exit ticket**: the Canvas button render, the scenario or prompt verbatim, minutes, one stem.
- **Before you go**: three numbered checks and one line naming tomorrow.

## 3. Build

```bash
mkdir -p build/slides/<week>/assets && cd build/slides/<week>
# workbook pages (printed 28 = PDF 34); the PDF is gitignored, render on the machine that has it
pdftoppm -r 170 -f 34 -l 34 -jpeg -jpegopt quality=92 cce-curriculum/resources/reference-pdfs/IrvingFindYourFuture2026.pdf assets/fyf-p28
python3 ../crop.py crop assets/fyf-p28.jpg assets/p28-goodbad.jpg 80 850 1400 1620          # region crop, optional --box for the pink look-here mark
python3 ../crop.py fetch 98060 student-<slug> assets/pages/dayN.html < ~/.canvas_token      # Canvas page with images inlined
python3 ../crop.py element assets/pages/dayN.html assets/cv-dN-exit.png "text=Open the Day N exit ticket" --pad 24
cp ../1sw-wk3/day2.js dayN.js   # then rewrite every slide from the plan
node dayN.js && CCE_PUBLIC=1 node dayN.js
python3 ../qa_deck.py ../../../docs/resources/slides/<week>-dayN.pptx
```

`build_week.sh <week>` builds every day, both twins, and runs the gate on each.

Library calls: `d.title`, `d.slide(title, sub)`, `d.card`, `d.body`, `d.label`, `d.numbered`, `d.namedRows` (Think/Pair/Share, Task/Skill), `d.stem`, `d.wordBank`, `d.meta`, `d.extension` (yellow box), `d.image(file, x, y, w, h, {licensed, fyfPage})`, `d.notes(s, teach, sources)`. Slides are 1280×720 px; content starts at y=200 under the subtitle; left column 64..784, right column 820..1216.

## 4. QA gate, then a human look

`qa_deck.py` fails on: missing notes, missing or duplicated `[Sources]`, anything outside the canvas, text painted over text, and banned strings. It also renders a contact sheet. The contact sheet is not optional: look at every slide for a wrapped label, a squished image, a crop that cut a heading, a card with more whitespace than text. Then read the speaker notes of the strategy slide and the work slide aloud once; if they do not sound like a teacher, rewrite them.

## 5. Deliver (only after the owner approves the deck)

Decks are teacher-facing curriculum, so they follow the same parity rules as pages: the source course gets them first, the fleet gets them through `canvas-fleet-parity-cce-runbook.md`, and the public site gets the twin.

`python3 build/slides/publish_week.py <week> --apply < ~/.canvas_token` does, for each day:
1. uploads the full `.pptx` to Canvas Files under `Slides/<week>/` (overwrite by name),
2. uploads the same `.pptx` to the unit's `Google Masters/` Drive folder converted to Google Slides and keeps the `.pptx` beside it in `Download Releases/`,
3. adds a **Slides** row to that day's facilitator guide response-routes panel (Google Slides link, PowerPoint download, both labels fixed) through a page-body PUT only; nothing is published or unpublished,
4. copies the public twin into the public site's static assets so `public-site/build_site.py` can link it.
Then run `build/canvas/fleet_parity_apply.py` for the fleet (page bodies only) and `qa_response_routes.py`.

## 6. What to flag while building

Building a deck reads the lesson closely, so it finds gaps. Record each in the run note (`cce-curriculum/notes/audits/<date>-<week>-slides.md`) and do not silently fix curriculum in the deck: a worksheet students write in that has no Doc button, a printed guide whose numbers no longer match the live source, a workbook step the plan skips, a Canvas page whose button label differs from the plan's name for the thing. The deck reflects the plan as it is; the note is what gets the plan fixed.
