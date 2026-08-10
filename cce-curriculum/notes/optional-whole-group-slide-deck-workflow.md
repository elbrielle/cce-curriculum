# Optional Whole-Group Lesson Deck Workflow

**Status:** BINDING when an optional teacher slide deck is produced for the
CCR Canvas course.

**Sequence:** Finish the lesson's source-grounding pass and coordinated Canvas
Teacher/Student pair first. Build the deck from that reviewed lesson contract;
do not use a deck to stabilize unfinished curriculum.

## 1. Job of the deck

The deck is an optional projection and facilitation tool. It should let a
teacher whole-group teach the complete lesson from the bellringer through the
Demonstration of Learning without reconstructing directions, inventing an
example, or opening several unrelated files while students wait.

The Canvas Teacher Facilitator Guide remains the instructional source of truth.
The Student Guide remains the accessible, independent, and absence route. A
deck may simplify what is projected, but it may not change the objective,
evidence, timing, source sequence, platform minimum, or success criteria.

## 2. Production order

1. Confirm the exact Scope and Sequence row, daily TEKS, Topic, Objective, and
   Demonstration of Learning.
2. Verify the workbook pages, Climber Notes slides, H&L task, Xello completion
   standard, and any supplemental resource used that day.
3. Cold-read the Canvas Teacher/Student pair for timing, hidden prep, answer
   guidance, supports, and platform or absence recovery.
4. Write the slide sequence and speaker-note plan from the reviewed lesson.
5. Build each slide as a fixed 16:9 HTML/CSS frame.
6. Render each frame to PNG, then place each PNG edge-to-edge on its PowerPoint
   slide. This raster-first route is intentional: it protects the reviewed
   HTML/CSS layout from PowerPoint font and object reflow.
7. Add teacher facilitation notes and source records to PowerPoint speaker notes.
8. Render the finished PPTX back to images, inspect every slide, and compare it
   with the approved HTML render before uploading the deck to locked Canvas.

## 3. Technical contract

- Use a 16:9 fixed canvas, preferably 1600 x 900 or 1920 x 1080 pixels.
- Do not rely on responsive reflow inside a slide. The render viewport and the
  slide dimensions are part of the layout contract.
- Use HTML/CSS for visible composition and Chromium/Playwright for deterministic
  PNG capture.
- Use the current presentation skill and `@oai/artifact-tool` to assemble the
  PPTX. Do not use `python-pptx`.
- Place one rendered PNG as the full-slide visual. Keep visible text out of
  PowerPoint text boxes unless a specific accessibility or teacher-editing need
  outweighs the formatting-stability goal.
- Keep the HTML/CSS source and license-clear assets in Git. Keep workbook, Xello,
  H&L, and other district-licensed source images in the gitignored Canvas-only
  asset tree. A deck containing those licensed images is uploaded only to
  authenticated, locked Canvas and is not committed to Git.
- Speaker notes are not optional. They carry the facilitation layer and the
  source record that should not crowd the student-facing projection.
- Optimize images for the display size before packaging. Preserve the original
  licensed source in the local Canvas-only archive; never improve load time by
  destroying the only source-quality copy.

## 4. Whole-lesson slide grammar

Use the smallest sequence that can carry the full lesson. A typical deck
includes:

1. **Topic/title:** a clean opening visual and the day's short Topic.
2. **Bellringer:** one prompt, response mode, and visible time expectation.
3. **Today's learning:** student-friendly Objective and Show Your Learning;
   include the TEKS code where it helps the teacher, not as unexplained student
   clutter.
4. **Road map and materials:** what students will do and what they need ready.
5. **Mini-lesson chunks:** one instructional job or important idea per slide.
6. **Models and non-models:** a worked example, annotated source, decision path,
   or misconception check wherever the teacher guide expects one.
7. **Engagement at the point of use:** dedicated Stop and Jot, Think-Pair-Share,
   Turn and Talk, Q-SSA, TVB, chunking pause, or active-monitoring checkpoint.
   Name the student action; do not project a strategy label with no directions.
8. **Work launch:** numbered directions, the exact source page or platform path,
   expected artifact, time cue, and a visible `Done when` checklist.
9. **Mid-work checkpoint:** what students should have completed and what the
   teacher should correct before students continue.
10. **Demonstration of Learning:** the exact exit task or collected artifact that
    matches the objective.
11. **Close/next step:** submission, cleanup, catch-up location, or meaningful
    early-finisher route. Do not end on a generic thank-you slide.
12. **Credits:** compact human-readable asset credits, with the full record in
    speaker notes.

Put transitions, timers, collaboration directions, and material changes on the
slide where they happen. Keep trim points in teacher notes so an interruption
does not force the teacher to cut the Demonstration of Learning.

## 5. Speaker-note contract

For each slide, record only what helps a teacher facilitate it:

- approximate time and transition;
- what the teacher says, models, or reveals;
- what students do, say, write, or submit;
- what to monitor or listen for;
- answer guidance, likely misconception, or acceptable variation;
- language, reading, sensory, or participation support;
- the safe trim point or recovery move; and
- a `[Sources]` block for every external visual and every non-trivial external
  claim.

The `[Sources]` record should include creator or organization, asset title or
description, direct source URL, license or usage basis, and access date. For a
district-licensed source, use a record such as `District-licensed HQIM; available
only in authenticated Canvas` plus the exact workbook page, platform screen, or
vendor resource title.

## 6. Image sourcing and licensing

Google Images may help discover an asset, but Google is not the source and does
not grant permission to use it. Follow the result to the original publisher and
record the actual rights information.

Prefer, in order:

1. district-licensed HQIM or vendor assets already assigned to the lesson;
2. official government, museum, university, or organization media with a clear
   reuse statement;
3. Creative Commons or public-domain media with the required attribution;
4. reputable stock libraries with a license that permits educational reuse; or
5. a purpose-built original or generated visual when a sourced image would add
   noise, rights ambiguity, or factual risk.

Do not use a random search-result thumbnail, remove a watermark, or treat a lack
of visible copyright text as permission. Do not scrape or screen-record a
protected stream. Xello, H&L, workbook, and Climber Notes screenshots stay in
the authenticated Canvas delivery boundary.

## 7. Student-slide design standard

- Give each slide one instructional job.
- Use a direct takeaway or action title rather than a generic chapter label.
- Keep the title slide minimal.
- Default minimums are 50 pt deck title, 35 pt slide title, 24 pt subheading,
  and 16 pt body text; for whole-class projection, prefer 24-32 pt body text
  whenever the room and content allow it.
- Shorten the copy or split the slide before reducing the type.
- Use high contrast, generous spacing, and meaningful imagery. Avoid dense card
  grids, decorative badges, unexplained icons, and visual clutter that competes
  with the task.
- Do not rely on color alone. Caption visual evidence and explain what students
  should inspect.
- Keep prompts visible long enough to complete. Place required instructions on
  the slide, not only in speaker notes.
- Avoid projecting answer keys with the prompt. Use a later reveal slide or a
  teacher-only note.
- Preserve the Canvas Student Guide as the accessible text route because a
  raster-first PowerPoint is primarily a projection aid, not the sole student
  document.

At production time, make a focused best-practice research pass for the audience,
content type, and delivery setting. Current official documentation and
accessibility guidance govern features and requirements. Reddit and teacher
communities may surface classroom friction or useful patterns, but practitioner
posts are leads and implementation warnings rather than authoritative evidence.

## 8. Quality gate

The deck is ready for locked Canvas only when:

- the Scope and Sequence, HQIM pages, platform task, Objective, and DOL match the
  reviewed Teacher/Student pair exactly;
- the sequence can carry the complete planned class period, including the
  bellringer, modeling, student work, collaboration, and close;
- all answer guidance, monitoring notes, supports, and trim points exist;
- every external claim and visual has a `[Sources]` note;
- licensed assets and the packaged deck have stayed out of Git;
- every HTML slide and final PPT slide has been rendered and inspected at full
  size for clipping, blur, overlap, awkward wrapping, and unreadable labels;
- the PPTX passes the presentation overflow check;
- the smallest instructional text remains readable from the back of a typical
  classroom and on the teacher's projected Canvas preview;
- the file size and first-load behavior are reasonable for Canvas; and
- the deck, file folder, page links, and module item remain unpublished/locked.

Record the final deck name, Canvas file ID, linked lesson, credits status, and QA
date in the Canvas build log. The neutral user-facing label is **Optional
Whole-Group Lesson Deck** or **Lesson Presentation**.
