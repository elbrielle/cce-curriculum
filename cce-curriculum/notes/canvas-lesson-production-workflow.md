# Canvas Lesson Production Workflow

**Status:** BINDING. This is the repeatable workflow for Codex, Claude, and future curriculum agents building the official CCR Canvas course.

**Approved reference implementation:** 1SW Wk0 Day 2. Source templates and the idempotent importer live in `build/canvas/`.

## 1. Delivery contract

Every instructional day receives two coordinated Canvas pages.

### Teacher Facilitator Guide

The teacher page is a classroom dashboard, not a pasted copy of the public lesson plan. It must contain:

1. before-class preparation;
2. materials and exact source pages;
3. learning target and student evidence;
4. a time-boxed lesson flow;
5. concise facilitation language and active-monitoring targets;
6. grading guidance and any answer key;
7. evidence-based language and reading supports;
8. a platform, equipment, and absence fallback; and
9. a direct link to the matching student guide.

Teacher-only pages remain unpublished when the student module is eventually published.

### Student Guide

The student page must work during class and as an independent absence/catch-up path. It must contain:

1. one plain-language purpose statement;
2. a short “Today you will” list;
3. materials or “Get ready” list;
4. short numbered steps in 6th-7th-grade-accessible language;
5. only the screenshots, workbook crops, or examples that remove real ambiguity;
6. exact platform navigation;
7. what to write, create, or submit;
8. a visible “You are done when” checklist; and
9. an expandable absence/platform-failure route.

Keep required directions visible. Use native `<details><summary>` sections only for optional help, examples, vocabulary, sentence frames, early-finishers, or catch-up directions. Do not use legacy `enhanceable_content tabs`.

## 2. Source and licensing boundary

Use sources in this order:

1. the matching `docs/<six-weeks>/<week>/dayN.md` lesson plan;
2. the *Find Your Future* workbook;
3. the named Climber Notes deck or H&L teacher resource;
4. the live Xello Grade 8 completion configuration and captured licensed documents;
5. district pathway and platform references; and
6. supplemental platforms only where the scope and sequence assigns them.

Licensed source binaries and rendered screenshots never enter GitHub. Store local Canvas-only visuals under:

`cce-curriculum/resources/canvas-licensed/<six-weeks>/<week>/<day>/`

That directory is gitignored. Upload those assets to a locked Canvas folder under:

`course files/CCR Materials/<six-weeks>/<week>/<day> Visuals`

Do not upload licensed files to the public MkDocs site. Do not extract or rehost streamed video unless the vendor supplies a downloadable file or the district has explicit permission.

## 3. Select and render visuals

Do not decorate for decoration’s sake. A visual earns a place when it helps a student locate a source, understand a step, compare options, recognize a screen, or recover after an absence.

### Workbook pages

The FYF printed page number is six less than the PDF page number:

`PDF page = printed page + 6`

Render only the needed page or region. Example:

```bash
pdftoppm -f 27 -l 27 -singlefile -png -r 150 \
  cce-curriculum/resources/reference-pdfs/IrvingFindYourFuture2026.pdf \
  cce-curriculum/resources/canvas-licensed/1sw/wk0/day2/irving-isd-ccmr-programs-of-study
```

### Climber Notes decks

Render the complete source deck, inspect every slide, then copy only the selected slide image into the Canvas-only asset folder. Use the bundled presentation runtime described by the current presentation skill; do not use a random screenshot of PowerPoint in edit mode.

If the bundled renderer or montage helper reports that `pdf2image` is missing, supply that helper dependency without altering the deck:

```bash
uv run --with pdf2image python <presentation-skill>/container_tools/render_slides.py \
  "<source-deck>.pptx" --output_dir "<temporary-render-folder>"
```

### Visual QA before upload

Inspect each selected PNG at original resolution. Reject it if text is unreadable, the crop removes needed context, the screenshot includes private student data, or the image does not add instructional value. Use a descriptive filename and prepare useful alt text before authoring the page.

## 4. Author the page pair

Use the approved templates as the structural reference:

- `build/canvas/templates/wk0-day2-teacher.html`
- `build/canvas/templates/wk0-day2-student.html`

Preserve the design grammar:

- one strong title banner;
- one-column responsive layout;
- clear numbered headings;
- restrained Irving/H&L-aligned purple, green, teal, and gold accents;
- normal HTML lists and links;
- images at `width: 100%`, `height: auto`, and a reasonable `max-width`;
- meaningful alt text on every image;
- native disclosure sections; and
- no layout tables, unsupported JavaScript, fake UI, or decorative button clutter.

Write naturally. Student directions should sound like a capable teacher giving a student the next clear step. Teacher directions should be concise enough to scan while teaching.

## 5. Build safely through the Canvas API

Use an idempotent importer under `build/canvas/`. It should:

1. create or locate the locked Canvas file folder;
2. upload assets with `on_duplicate=overwrite`;
3. resolve existing supporting files by exact display name;
4. replace all template tokens;
5. update an existing page by stable URL or create it once;
6. keep pages and modules unpublished;
7. update or create module items at explicit positions; and
8. print only non-secret IDs and status information.

Never write the Canvas token to disk. Never place it in the command string. Read it with terminal echo disabled and pipe it to the importer on standard input:

```bash
stty -echo
IFS= read -r CCR_CANVAS_TOKEN
stty echo
printf '%s\n' "$CCR_CANVAS_TOKEN" | uv run --with httpx python build/canvas/build_wk0_day2.py
unset CCR_CANVAS_TOKEN
```

Do not print, log, commit, or repeat the token.

## 6. Verification gate

No page pair is complete until all checks pass.

### Saved-state/API checks

- teacher page exists and is unpublished;
- student page exists and is unpublished;
- module remains unpublished;
- licensed asset folder remains locked;
- every template token was replaced;
- every required Canvas file exists and opens;
- teacher and student items appear in the intended module order; and
- rerunning the importer does not create duplicate pages or module items.

### Content and accessibility checks

- student prose is near the 6th-7th-grade target;
- headings do not skip levels;
- every image has useful alt text;
- every `<details>` has a `<summary>`;
- required directions are not hidden in a disclosure;
- links have meaningful visible text;
- there are no layout tables or `enhanceable_content tabs`; and
- bilingual support follows the evidence-based support policy rather than automatic full translation.

### Visual browser checks

Open the page through its module-item URL, not only the bare Pages URL. Verify:

1. desktop layout and hierarchy;
2. mobile-width layout with no horizontal overflow;
3. every image loads at the point where it is used;
4. disclosure sections open and remain readable;
5. the exit-ticket/resource links resolve;
6. teacher page can be scanned during instruction; and
7. the student page can be completed through the written absence path.

Run Canvas Student View before publication. Use the Canvas accessibility checker when final editing begins.

## 7. Record and publish the source work

After Canvas verification:

1. update `cce-curriculum/notes/canvas-build-log.md` with course, module, page, item, folder, and file IDs;
2. update the relevant asset manifest when licensed sources were added;
3. run `git diff --check`;
4. run the strict MkDocs build;
5. stage only tracked source, templates, scripts, and notes;
6. confirm licensed visuals are ignored;
7. commit with a neutral curriculum-production message;
8. push the working branch and `main`; and
9. deploy the MkDocs review site when public documentation changed.

## 8. Efficient scaling pattern

Build one week at a time rather than one isolated page across the whole year.

1. Audit all five day plans and list the exact teacher/student assets.
2. Render the week’s source visuals in one batch.
3. Author five teacher/student page pairs from the approved pattern.
4. Use one idempotent week importer to upload and place the full set.
5. Run automated HTML/API checks across all ten pages.
6. Run visual QA on every page, with deeper desktop/mobile checks on the most complex day.
7. Fix the week as a unit and record one complete build-log entry.

This preserves quality while reducing repeated API setup and asset-upload overhead.

## 9. Definition of done

A lesson is Canvas-ready only when a teacher can teach it without reconstructing missing directions and an absent student can complete the core task from the student page. “The page exists” is not completion.
