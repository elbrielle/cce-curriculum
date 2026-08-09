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

### Package Xello resources for the teacher

For each required Xello task, inspect the authenticated Completion Standards resource drawer and Xello's official teaching-resource library. Capture the downloadable materials that actually support that task, which may include a facilitator guide, slide deck, student worksheet or directions, and a downloadable student-facing video. Upload licensed downloads only to the locked week folder in Canvas.

Do not make the teacher rediscover the Xello library during prep. On the teacher page, label each resource by its classroom job, such as “2-minute student launch,” “teacher demo steps,” “full extension lesson,” or “catch-up directions.” On the student page, embed only the asset that removes a real navigation or understanding barrier. If the resource is broader than the district completion minimum, state both the district minimum and the resource's extended lesson time.

An official hosted video may be embedded when streaming is district-accessible and captions are present. Rehost only a vendor-supplied downloadable file. Never screen-record, scrape, or download a protected stream. Every video needs a visible text route that covers the same required directions.

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
uv run --with pdf2image --with pillow python <presentation-skill>/container_tools/render_slides.py \
  "<source-deck>.pptx" --output_dir "<temporary-render-folder>"
```

Use the same `uv run --with pdf2image --with pillow` prefix for the presentation skill's montage helper. This keeps slide rendering reproducible when the system Python does not include either helper library.

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

### Choose the Canvas interaction on purpose

Do not assume every student artifact should become a printed worksheet or a static page. Before authoring, choose the Canvas surface that removes the most teacher work without weakening the learning target:

- **Page:** directions, examples, source images, absence recovery, and content students need to revisit.
- **Assignment:** individual work that needs one submission location, a visible rubric, feedback, reassessment, or a durable gradebook record.
- **Discussion:** genuine peer response, critique, or comparison where students need to read and answer one another. Always provide a private or self-check route when public posting, attendance, or an accommodation makes the discussion inappropriate.
- **Quiz:** short selected-response or technology-enhanced checks where automatic feedback and item analysis save time. Do not turn design, reflection, argument, or career-fit judgment into forced multiple choice merely because the tool exists.
- **External tool or licensed platform:** use Xello, H&amp;L, Canva, Adobe Express, Code.org, eDynamic, or another approved integration for the interaction it already does well. Keep the Canvas page as the launch, directions, evidence, and recovery layer.

Use the least complicated surface that fits the evidence. Paper remains an equal route when handwriting, sketching, manipulatives, device access, or an accommodation makes it the better tool. Before creating graded Canvas objects, confirm the course's Minor/Major assignment groups and weights; never place a grade into an arbitrary imported or default group.

When a printable or downloadable worksheet is justified, size every response area from the response job, not from the visual symmetry of a table. A label, number, or phrase may use one line; a reason or comparison normally needs two to three full-width lines; a multi-sentence explanation needs its own full-width block; and a sketch needs a box large enough to draw and label. Do not hide several writing jobs in one narrow table cell. Run the worksheet builder with `--strict`, render every page, and inspect a contact sheet. If the packet overflows, rebalance page breaks or increase the honest page count; do not shrink the writing space until the warning disappears. In Canvas, prefer labeled text-entry fields, an annotation assignment, or a private media response when those routes remove printing without weakening the evidence.

For five-day modules, use a native Canvas `SubHeader` before each Teacher/Student pair. Keep one chronological route: Day header, Teacher Guide, Student Guide, then any interaction used that day. The generic module verifier accepts and records these headers. This gives teachers and students a fast visual scan without creating extra pages or competing navigation systems.

### Run a periodic engagement and organization scan

At the start of each six-weeks block, and again when a week feels repetitive, make a short research pass through current Canvas documentation, accessibility guidance, practitioner discussions, and a small sample of teacher communities such as Reddit. Treat practitioner posts as leads and implementation warnings, not as research evidence. Confirm features in current official documentation and then verify that Irving ISD has enabled or licensed the feature before making it load-bearing.

Use the scan to widen the interaction menu beyond pages, quizzes, and discussions:

- **Student annotation:** students mark a supplied PDF or image in Canvas when circling evidence, labeling a diagram, or annotating a model is the learning target. Confirm Chromebook, iPad, and screen-reader routes before use.
- **Peer review:** use a submitted draft plus a short rubric when students need private, assigned critique. Do not add peer review when a simple partner conference is faster or when late work would strand students without a reviewer.
- **Choice board:** offer two or three equal ways to practice or show evidence, such as a typed response, audio explanation, annotated visual, or paper sketch. Keep the same success criteria across routes.
- **Module requirements:** use "view," "submit," or "score at least" requirements only when sequence matters and the requirement will not lock out an absent student or a student waiting for manual grading.
- **Audio or video response:** allow a brief recording when oral explanation is the target or writing mechanics would obscure the evidence. Always provide a text route and captions or transcript expectations.
- **Embedded simulation or interactive:** use an approved district tool when it does the authentic work better than a worksheet. Canvas remains the launch, evidence, privacy boundary, and catch-up layer.
- **Mastery Paths:** consider only after district availability, SIS behavior, and teacher workflow are verified. Start with a small pilot because manual-grading delays can lock later module items.

For every proposed interaction, record four answers in the week audit:

1. What student action improves?
2. What teacher work disappears?
3. What access, privacy, moderation, or late-work problem appears?
4. What equal fallback works without pretending the platform task was completed?

Reject a tool when the only benefit is novelty. The student should still have one obvious starting point in the weekly module, consistent day labels, and a visible completion checklist. This follows the recurring practitioner signal that students lose time when course materials are split across Pages, Files, Assignments, and external sites without a module-first route.

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

Run Canvas importers through `uv run --with httpx`; a bare `python` invocation is not portable because the system Python may not include `httpx`. A dependency failure before the token prompt does not touch Canvas, but it wastes a build pass and can leave the operator unsure whether anything changed.

Do not print, log, commit, or repeat the token.

### Classic Quiz practice checks

Use a Classic Quiz when a brief, automatically scored misconception check will save teacher time and immediate feedback is more useful than a printed response sheet. Keep a practice check ungraded and unpublished until review. A reliable importer should:

1. locate or create the quiz by its exact neutral title;
2. set `quiz_type` to `practice_quiz`, keep `published` false, and allow unlimited attempts when retrying is part of the lesson;
3. create questions with stable exact names so reruns can update rather than duplicate them;
4. include answer-specific or general feedback that explains the misconception;
5. add the Quiz as an explicit module item only after the student page that prepares students for it; and
6. verify quiz state and question count through `qa_canvas_module.py`.

Selected-response items should check bounded facts, safety decisions, labels, or source interpretation. Use an Assignment, Discussion, or teacher-reviewed artifact for design, reflection, argument, and career-fit judgment.

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
- every writing prompt has response space matched to its required output: a word or number may use a short field, a sentence needs at least one full-width ruled line, multi-part reasoning needs separate labeled lines, and a labeled design needs a genuinely usable drawing area;
- headings do not skip levels;
- every image has useful alt text;
- every raster image is large enough for its instructional text or labels to remain readable but not materially larger than the displayed need; record unusually large files for the Canvas image-performance backlog instead of applying blind batch compression;
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

If an image is slow on first load, treat that as a performance defect even when it eventually appears. Record its Canvas file ID, source dimensions, byte size, page, and whether it is reused. Test an optimized copy against the original at desktop and 390-pixel viewport widths, including close inspection of the smallest instructional text. Replace the Canvas copy only after the optimized version remains equally usable; keep the licensed source original unchanged in the local gitignored archive.

## 7. Record and publish the source work

After Canvas verification:

1. update `cce-curriculum/notes/canvas-build-log.md` with course, module, page, item, folder, and file IDs;
2. update the relevant asset manifest when licensed sources were added;
3. run `git diff --check`;
4. run the Canvas template, API, browser, accessibility, mobile-layout, permissions, and Student View checks appropriate to the change;
5. stage only tracked source, templates, scripts, and notes;
6. confirm licensed visuals are ignored;
7. commit with a neutral curriculum-production message; and
8. push the source as a GitHub backup.

Canvas is the sole active production and review environment. MkDocs is a legacy archive: do not build, QA, or deploy it unless the user explicitly requests legacy-site work.

Run local checks through an explicit temporary dependency environment so future agents do not depend on whichever Python packages happen to be installed globally:

```bash
uv run --with beautifulsoup4 --with textstat python build/canvas/qa_templates.py 'wkN-*.html'
```

For generic HTML templates that still contain placeholder prose, calculate reading level from each fully rendered page body. A reading score from unreplaced tokens is not meaningful.

### Rendering and QA fallbacks confirmed on macOS

- Resolve presentation helpers relative to the directory that contains the selected presentation skill's `SKILL.md`. In the bundled runtime, `render_slides.py` and `create_montage.py` are under that skill directory's `container_tools/` folder, not the plugin package root.
- When either presentation helper reports a missing `pdf2image` or Pillow import, run it through `uv run --with pdf2image --with pillow python ...`; do not patch the skill's bundled runtime or alter the source deck.
- `pdftoppm` zero-pads page suffixes when the source PDF has many pages (`-054.png`, not `-54.png`). List the rendered directory before copying selected pages instead of guessing filenames.
- ImageMagick's `montage` command may not be installed. For a worksheet/PDF contact sheet, use the bundled workspace Python plus Pillow to thumbnail and tile the already-rendered PNGs. This is a QA artifact only; keep it in a temporary directory.
- Do not call the Canvas template QA script with an arbitrary system Python. Use the documented `uv run --with beautifulsoup4 --with textstat ...` command so `bs4` and `textstat` are present.
- Xello presentation objects may receive different runtime IDs each time a deck is opened or imported. Resolve the live object by its visible text and slide context before editing; do not hard-code an ID copied from a static inspection. Render the final deck again after the edit and run both template-fidelity and overflow checks.
- Exit-ticket rendering derives the output filename from the day-page H1. When a day title changes, use the canonical `**EXIT TICKET** (Format):` marker, regenerate, run `build/inject_pdf_links.py`, and review the newly named PDF. Restore timestamp-only churn from unrelated tickets before staging.
- For repeated PDF QA renders, create a new task-specific directory with `mktemp -d` instead of deleting a wildcard set from a shared temp folder. This avoids unsafe cleanup patterns and prevents stale page images from being mistaken for the latest render.
- The 2026 *Find Your Future* reference PDF has six front-matter pages before its printed page numbering. When extracting a printed workbook page with `pdftoppm`, use physical PDF index = printed page + 6, then visually confirm the printed page number in the rendered footer before naming or uploading the delivery asset.

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

When the module includes a Discussion, the importer must find the existing topic from the unfiltered discussion-topic list before creating one. Repeated runs must not create duplicate topics or module items. Normalize mixed Page/Discussion positions in ascending order, then run `qa_canvas_module.py`; the verifier accepts unpublished Discussions and still requires one consecutive 1..N module sequence.

## 9. Definition of done

A lesson is Canvas-ready only when a teacher can teach it without reconstructing missing directions and an absent student can complete the core task from the student page. “The page exists” is not completion.
