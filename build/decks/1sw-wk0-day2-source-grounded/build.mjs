import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const runtimeHelperPath = process.env.CODEX_PRESENTATIONS_RUNTIME_HELPER;
if (!runtimeHelperPath) {
  throw new Error("Set CODEX_PRESENTATIONS_RUNTIME_HELPER to the presentations runtime_helpers.mjs path.");
}
const { importRuntimeModule } = await import(pathToFileURL(path.resolve(runtimeHelperPath)).href);

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../../..");
const workspace = path.join(root, "tmp/cce-week1-day2-source-clone");
const starterPath = path.join(workspace, "template-starter.pptx");
const outputPath = path.join(
  root,
  "cce-curriculum/resources/avid-reference/source/derived/cce-week1-day2-source-grounded.pptx",
);
const previewDir = path.join(workspace, "final-preview");
const layoutDir = path.join(workspace, "final-layout");
const routeImagePath = path.join(
  root,
  "cce-curriculum/resources/canvas-licensed/1sw/wk0/day2/open-hats-and-ladders-discover-your-core.png",
);
const assets = {
  typesChart: path.join(
    root,
    "cce-curriculum/resources/canvas-licensed/1sw/wk0/day2/six-core-personality-types.png",
  ),
  ccmrPage: path.join(
    root,
    "cce-curriculum/resources/canvas-licensed/1sw/wk0/day2/irving-isd-ccmr-programs-of-study.png",
  ),
  goalReasonAction: path.join(
    root,
    "cce-curriculum/resources/owner-authenticated-source/onenote/screens/first-week-goal-reason-and-action.png",
  ),
  goalSupport: path.join(
    root,
    "cce-curriculum/resources/owner-authenticated-source/onenote/screens/first-week-goal-support.png",
  ),
  dashboard: path.join(
    root,
    "cce-curriculum/resources/owner-authenticated-source/hats-and-ladders/screens/dashboard-profile-climbs.png",
  ),
  jumpstart: path.join(
    root,
    "cce-curriculum/resources/owner-authenticated-source/hats-and-ladders/screens/jumpstart-profile-start.png",
  ),
  jumpstartQuestion: path.join(
    root,
    "cce-curriculum/resources/owner-authenticated-source/hats-and-ladders/screens/jumpstart-starting-point-question.png",
  ),
  coreStart: path.join(
    root,
    "cce-curriculum/resources/owner-authenticated-source/hats-and-ladders/screens/discover-your-core-start.png",
  ),
  coreQuestion: path.join(
    root,
    "cce-curriculum/resources/owner-authenticated-source/hats-and-ladders/screens/discover-your-core-question.png",
  ),
  coreComplete: path.join(
    root,
    "cce-curriculum/resources/owner-authenticated-source/hats-and-ladders/screens/core-complete-badge.png",
  ),
};

const { FileBlob, PresentationFile } = await importRuntimeModule("@oai/artifact-tool");
const sharpModule = await importRuntimeModule("sharp");
const sharp = sharpModule.default ?? sharpModule;
await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.mkdir(previewDir, { recursive: true });
await fs.mkdir(layoutDir, { recursive: true });

const presentation = await PresentationFile.importPptx(await FileBlob.load(starterPath));
const initial = await presentation.inspect({
  kind: "slide,textbox,image,notes",
  maxChars: 500_000,
});
const records = initial.ndjson
  .split("\n")
  .filter(Boolean)
  .map((line) => JSON.parse(line));

function recordFor(kind, slide, predicate = () => true) {
  const record = records.find(
    (item) => item.kind === kind && item.slide === slide && predicate(item),
  );
  if (!record) throw new Error(`Missing ${kind} on output slide ${slide}`);
  return record;
}

function textbox(slide, text) {
  return presentation.resolve(recordFor("textbox", slide, (item) => item.text === text).id);
}

function setText(slide, before, after) {
  textbox(slide, before).text.set(after);
}

function setNotes(slide, lines) {
  const notes = presentation.resolve(recordFor("notes", slide).id);
  notes.setText(lines.join("\n"));
}

function addText(slide, text, position, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontSize: style.fontSize ?? 20,
    bold: style.bold ?? false,
    color: style.color ?? "#202331",
    fontFamily: "Aptos",
  };
  return shape;
}

function coverSlide(slideNumber, title, kicker = "CCE WEEK 1 · TUESDAY") {
  const slide = presentation.slides.items[slideNumber - 1];
  [...slide.images.items].forEach((image) => image.delete());
  slide.shapes.deleteAll();
  slide.shapes.add({
    geometry: "rect",
    position: { left: 0, top: 0, width: 960, height: 540 },
    fill: "#C9D0EF",
    line: { style: "solid", fill: "#C9D0EF", width: 0 },
  });
  const pill = slide.shapes.add({
    geometry: "roundRect",
    position: { left: 28, top: 24, width: 204, height: 30 },
    fill: "#FFD357",
    line: { style: "solid", fill: "#A86600", width: 1 },
    borderRadius: "rounded-full",
  });
  pill.text = kicker;
  pill.text.style = { fontSize: 12, bold: true, color: "#553400", fontFamily: "Aptos" };
  addText(slide, title, { left: 60, top: 64, width: 840, height: 48 }, { fontSize: 30, bold: true });
  return slide;
}

async function addGuidedScreen(slideNumber, config) {
  const slide = coverSlide(slideNumber, config.title, config.kicker);
  slide.shapes.add({
    geometry: "roundRect",
    position: { left: 28, top: 122, width: 330, height: 380 },
    fill: "#FFFFFF",
    line: { style: "solid", fill: "#8390C4", width: 1 },
    borderRadius: "rounded-xl",
  });
  addText(slide, "WHAT YOU SEE", { left: 48, top: 140, width: 280, height: 24 }, { fontSize: 12, bold: true, color: "#6350A8" });
  addText(slide, config.screen, { left: 48, top: 166, width: 280, height: 70 }, { fontSize: 17, bold: true });
  addText(slide, "DO THIS", { left: 48, top: 238, width: 280, height: 22 }, { fontSize: 12, bold: true, color: "#6350A8" });
  addText(slide, config.action, { left: 48, top: 262, width: 280, height: 104 }, { fontSize: 17 });
  slide.shapes.add({
    geometry: "roundRect",
    position: { left: 46, top: 382, width: 294, height: 96 },
    fill: "#FFF4C5",
    line: { style: "solid", fill: "#D69B00", width: 1 },
    borderRadius: "rounded-lg",
  });
  addText(slide, "DONE WHEN", { left: 62, top: 394, width: 250, height: 22 }, { fontSize: 12, bold: true, color: "#7A4A00" });
  addText(slide, config.done, { left: 62, top: 418, width: 250, height: 56 }, { fontSize: 15, bold: true });
  slide.shapes.add({
    geometry: "roundRect",
    position: { left: 394, top: 122, width: 538, height: 380 },
    fill: "#FFFFFF",
    line: { style: "solid", fill: "#8390C4", width: 1 },
    borderRadius: "rounded-xl",
  });
  slide.images.add({
    blob: await fs.readFile(config.filePath),
    contentType: "image/png",
    alt: config.alt,
    fit: config.fit ?? "contain",
    position: { left: 410, top: 138, width: 506, height: 348 },
  });
  const arrow = slide.shapes.add({
    geometry: "rightArrow",
    position: { left: 344, top: 273, width: 62, height: 42 },
    fill: "#FFD357",
    line: { style: "solid", fill: "#A86600", width: 1 },
  });
  arrow.text = config.callout ?? "";
  arrow.text.style = { fontSize: 10, bold: true, color: "#553400", fontFamily: "Aptos" };
}

function addGuidedText(slideNumber, title, body, done, kicker = "CCE WEEK 1 · TUESDAY") {
  const slide = coverSlide(slideNumber, title, kicker);
  slide.shapes.add({
    geometry: "roundRect",
    position: { left: 70, top: 140, width: 820, height: 238 },
    fill: "#FFFFFF",
    line: { style: "solid", fill: "#8390C4", width: 1 },
    borderRadius: "rounded-xl",
  });
  addText(slide, body, { left: 100, top: 174, width: 760, height: 180 }, { fontSize: 24 });
  slide.shapes.add({
    geometry: "roundRect",
    position: { left: 170, top: 410, width: 620, height: 72 },
    fill: "#FFF4C5",
    line: { style: "solid", fill: "#D69B00", width: 1 },
    borderRadius: "rounded-lg",
  });
  addText(slide, `DONE WHEN: ${done}`, { left: 192, top: 428, width: 576, height: 38 }, { fontSize: 19, bold: true });
}

async function addTypesChartHalf(slideNumber, { title, top, height, prompt, done, includeHeader = false }) {
  const slide = coverSlide(slideNumber, title);
  const body = await sharp(assets.typesChart)
    .extract({ left: 30, top, width: 1540, height })
    .png()
    .toBuffer();
  let crop = body;
  if (includeHeader) {
    const header = await sharp(assets.typesChart)
      .extract({ left: 30, top: 145, width: 1540, height: 80 })
      .png()
      .toBuffer();
    crop = await sharp({
      create: { width: 1540, height: height + 80, channels: 4, background: "#FFFFFF" },
    })
      .composite([{ input: header, left: 0, top: 0 }, { input: body, left: 0, top: 80 }])
      .png()
      .toBuffer();
  }
  slide.images.add({
    blob: crop,
    contentType: "image/png",
    alt: `${title} rows from the Canvas six Core personality types chart`,
    fit: "contain",
    position: { left: 36, top: 120, width: 888, height: 300 },
  });
  slide.shapes.add({
    geometry: "rect",
    position: { left: 36, top: 438, width: 888, height: 64 },
    fill: "#5A2D91",
    line: { style: "solid", fill: "#5A2D91", width: 0 },
  });
  addText(slide, `DO THIS: ${prompt}`, { left: 56, top: 448, width: 848, height: 22 }, { fontSize: 16, bold: true, color: "#FFFFFF" });
  addText(slide, `DONE WHEN: ${done}`, { left: 56, top: 473, width: 848, height: 22 }, { fontSize: 15, bold: true, color: "#FFD357" });
}

async function addCcmrContextSlide() {
  const slide = presentation.slides.items[5];
  [...slide.images.items].forEach((image) => image.delete());
  slide.shapes.deleteAll();
  slide.shapes.add({ geometry: "rect", position: { left: 0, top: 0, width: 960, height: 540 }, fill: "#C9D0EF", line: { style: "solid", fill: "#C9D0EF", width: 0 } });
  const pill = slide.shapes.add({ geometry: "roundRect", position: { left: 28, top: 24, width: 204, height: 30 }, fill: "#FFD357", line: { style: "solid", fill: "#A86600", width: 1 }, borderRadius: "rounded-full" });
  pill.text = "CCE WEEK 1 · TUESDAY";
  pill.text.style = { fontSize: 12, bold: true, color: "#553400", fontFamily: "Aptos" };
  addText(slide, "Why explore careers now?", { left: 60, top: 64, width: 840, height: 48 }, { fontSize: 30, bold: true });
  slide.shapes.add({ geometry: "roundRect", position: { left: 28, top: 122, width: 360, height: 380 }, fill: "#FFFFFF", line: { style: "solid", fill: "#8390C4", width: 1 }, borderRadius: "rounded-xl" });
  addText(slide, "WHAT YOU SEE", { left: 48, top: 140, width: 300, height: 24 }, { fontSize: 12, bold: true, color: "#6350A8" });
  addText(slide, "Find Your Future p. 21\nThis is not an H&L screen.", { left: 48, top: 166, width: 300, height: 64 }, { fontSize: 17, bold: true });
  addText(slide, "DO THIS", { left: 48, top: 238, width: 300, height: 22 }, { fontSize: 12, bold: true, color: "#6350A8" });
  addText(slide, "Listen to the CCMR definition. Turn and talk: Why think about future goals before high school?", { left: 48, top: 264, width: 300, height: 104 }, { fontSize: 17 });
  slide.shapes.add({ geometry: "roundRect", position: { left: 46, top: 382, width: 324, height: 96 }, fill: "#FFF4C5", line: { style: "solid", fill: "#D69B00", width: 1 }, borderRadius: "rounded-lg" });
  addText(slide, "DONE WHEN", { left: 62, top: 394, width: 280, height: 22 }, { fontSize: 12, bold: true, color: "#7A4A00" });
  addText(slide, "You can give one reason career exploration helps now.", { left: 62, top: 418, width: 280, height: 56 }, { fontSize: 15, bold: true });
  slide.shapes.add({ geometry: "roundRect", position: { left: 414, top: 122, width: 518, height: 380 }, fill: "#FFFFFF", line: { style: "solid", fill: "#8390C4", width: 1 }, borderRadius: "rounded-xl" });
  slide.images.add({
    blob: await fs.readFile(assets.ccmrPage),
    contentType: "image/png",
    alt: "Find Your Future page 21 with the yellow What is CCMR note highlighted as today's only reading target",
    fit: "contain",
    position: { left: 430, top: 138, width: 178, height: 348 },
  });
  slide.shapes.add({ geometry: "roundRect", position: { left: 626, top: 144, width: 286, height: 336 }, fill: "#FFF4A8", line: { style: "solid", fill: "#D69B00", width: 1 }, borderRadius: "rounded-lg" });
  addText(slide, "READ ONLY THE YELLOW NOTE", { left: 646, top: 162, width: 246, height: 26 }, { fontSize: 13, bold: true, color: "#6B3B87", align: "center" });
  addText(slide, "What is CCMR?", { left: 646, top: 198, width: 246, height: 34 }, { fontSize: 22, bold: true, color: "#5A2D91", align: "center" });
  addText(slide, "College, Career, and Military Readiness means preparing now for education, training, military service, or work after high school.", { left: 650, top: 244, width: 238, height: 132 }, { fontSize: 17, bold: true, align: "center" });
  addText(slide, "WHY IT MATTERS\nCareer exploration helps you make informed choices before those choices become urgent.", { left: 650, top: 392, width: 238, height: 72 }, { fontSize: 13, bold: true, color: "#553400", align: "center" });
}

async function replaceRouteImage(slide) {
  const image = presentation.resolve(recordFor("image", slide).id);
  const oldFrame = image.frame;
  const oldCrop = image.crop;
  const oldGeometry = image.geometry;
  const oldBorderRadius = image.borderRadius;
  const oldRotation = image.rotation;
  const oldFlipHorizontal = image.flipHorizontal;
  const oldFlipVertical = image.flipVertical;
  const oldLockAspectRatio = image.lockAspectRatio;
  image.replace({
    blob: await fs.readFile(routeImagePath),
    contentType: "image/png",
    alt: "Authenticated Hats & Ladders Discover Your Core directions used in the CCE lesson",
    fit: "contain",
  });
  image.frame = oldFrame;
  image.crop = oldCrop;
  image.fit = "contain";
  image.geometry = oldGeometry;
  image.borderRadius = oldBorderRadius;
  image.rotation = oldRotation;
  image.flipHorizontal = oldFlipHorizontal;
  image.flipVertical = oldFlipVertical;
  image.lockAspectRatio = oldLockAspectRatio;
}

setText(1, "Wednesday/ Thursday", "Tuesday");

addGuidedText(2, "Open CCE Work", "OneNote → private notebook → CCE Work\n\nOPEN:\n• Notebook Setup + First-Week Goal\n• Core Personality – Day 2\n\nCanvas or paper today? Use that route instead.", "both response pages are open");
await addGuidedScreen(3, { title: "Finish reason + action", screen: "Your private First-Week CCE Goal page in OneNote", action: "Complete WHY IT MATTERS. Then write ONE ACTION you control. If these are already finished, skip ahead.", done: "Both boxes contain a specific answer for this week.", filePath: assets.goalReasonAction, alt: "OneNote first-week goal template showing why it matters and one action fields" });
await addGuidedScreen(4, { title: "If needed · Finish confidence and support", screen: "The bottom of the same OneNote goal page", action: "Choose your confidence rating. Name one person, tool, or plan that can help. If finished, skip ahead.", done: "A confidence number and one support are recorded.", filePath: assets.goalSupport, alt: "OneNote first-week goal template showing confidence and support fields" });
addGuidedText(5, "Check the plan", "Read the answers once.\n\nCan you do the action?\nIs the checkpoint real?\nCan you use the support?\n\nLeave this page open. Do not start a second copy.", "the plan is usable and the Core activity can begin");
await addCcmrContextSlide();
await addTypesChartHalf(7, { title: "Doer · Analyzer · Creator", top: 145, height: 410, prompt: "Core types are H&L interest patterns. Read one row and point to a clue.", done: "you can explain one type with a real-life example" });
await addTypesChartHalf(8, { title: "Core types 4–6", top: 535, height: 335, prompt: "Core types are not grades or permanent labels. Read one row and point to a clue.", done: "you can explain one type with a real-life example", includeHeader: true });
addGuidedText(9, "Predict one—for now", "On OneNote → CCE Work → Core Personality – Day 2, write:\n\nMy prediction is ____ because I often ____.\n\nDo not open H&L yet. This is only a guess; your result may include more than one type.", "one predicted type and one real-life clue are recorded");
await addGuidedScreen(10, { title: "Step 1 · Open Profile Climbs", screen: "The Hats & Ladders dashboard after Sign in with Google", action: "Find the yellow Profile Climbs column. Click Jumpstart Your Profile.", done: "The Jumpstart start screen is open.", filePath: assets.dashboard, alt: "Hats and Ladders dashboard with the yellow Profile Climbs column and Jumpstart Your Profile card", callout: "CLICK" });
await addGuidedScreen(11, { title: "Step 2 · Start Jumpstart", screen: "The Jumpstart Your Profile start card", action: "Read the short introduction. Click Start when you are ready.", done: "You see the first starting-point question.", filePath: assets.jumpstart, alt: "Hats and Ladders Jumpstart Your Profile start screen with Start button", callout: "GO" });
await addGuidedScreen(12, { title: "Step 3 · Answer the starting-point question", screen: "A Jumpstart question with five choices", action: "Choose the answer that best describes you now. Then click Next.", done: "Your choice is selected and the next screen opens.", filePath: assets.jumpstartQuestion, alt: "Hats and Ladders Jumpstart starting-point question with five answer choices", callout: "NEXT" });
await addGuidedScreen(13, { title: "Step 4 · Start Core", screen: "The Discover Your Core start card", action: "Read the directions. Click Start. Answer as yourself—not as the person you think you should be.", done: "The first thumbs-down or thumbs-up statement is open.", filePath: assets.coreStart, alt: "Hats and Ladders Discover Your Core start screen showing Start button", callout: "GO" });
await addGuidedScreen(14, { title: "Step 5 · Answer honestly", screen: "One Discover Your Core statement with thumbs down and thumbs up", action: "Read the whole statement. Choose thumbs down or thumbs up. Use the arrow for the next statement.", done: "The progress bar moves after each answer.", filePath: assets.coreQuestion, alt: "Hats and Ladders Discover Your Core question with thumbs down and thumbs up choices", callout: "PICK" });
await addGuidedScreen(15, { title: "Record the result", screen: "The Core Complete badge in H&L", action: "Keep H&L open. Go to OneNote → private notebook → CCE Work → Core Personality – Day 2. Record the result + ONE interpretation.", done: "Result + one phrase, question, or career curiosity.", filePath: assets.coreComplete, alt: "Hats and Ladders Core Complete badge confirming Core Personality was completed in Profile", callout: "NOTE" });
addGuidedText(16, "DOL · Mark your stopping point", "Choose ONE:\n\n• Core complete + private note\n• Still in Jumpstart or Core\n• Need sign-in help\n\nReturn your device. Tomorrow, bring your Core result to Work Values.", "your stopping point is recorded and your device is returned");

const revisedNotes = [
  ["0:00–0:30", "Hold the Tuesday divider while students open OneNote and the Day 2 Student Guide.", "Students are in their own notebook.", "Read the setup list aloud.", "Canvas remains the absence route.", "Jenna Hainlen, AVID day-divider layout."],
  ["0:30–1:00", "Project the exact OneNote path and confirm the two pages were distributed before students arrived: private notebook → CCE Work → Monday goal page and Core Personality – Day 2.", "Students can locate both pages without searching H&L or FYF for the response page.", "Point to the path; do not troubleshoot individual notebooks from the projector.", "Use the Canvas or physical equivalent in the same order when OneNote is unavailable.", "Microsoft Class Notebook private-section and Distribute Page workflow; CCE Day 2 response-home clarification."],
  ["1:00–4:00", "Model a reason and one controllable action, then release students to the private OneNote page.", "Reason explains why; action begins with a verb and can happen this week.", "Offer one fictional CCE example without requiring personal disclosure.", "Canvas or paper may hold the answer if OneNote is unavailable; no recopying.", "Owner-authenticated OneNote first-week goal template V5; Jenna Hainlen AVID goal sheet, adapted for CCE."],
  ["4:00–7:00", "Students select confidence and name one usable support.", "Confidence is a number; support is a person, tool, or plan.", "Offer the categories teacher, classmate, directions, or extra time.", "A fictional support is acceptable.", "Owner-authenticated OneNote first-week goal template V5."],
  ["7:00–8:00", "Run a fast quality check; tell students to leave the page open and not make another copy.", "Action, checkpoint, and support are specific.", "Confer with students who wrote only try harder or do better.", "Do not add a separate retrieval test today.", "CCE revised Tuesday classroom flow."],
  ["8:00–9:00", "Name the visual correctly as Find Your Future p. 21, not H&L. Read only the yellow CCMR definition aloud, then ask the printed question: why think about future goals before high school?", "Students can give one reason career exploration helps now.", "Take one turn-and-talk response; do not read the Programs of Study or CTE Center boxes today.", "If the visual does not load, read the CCMR definition from the speaker notes and continue.", "Find Your Future p. 21, Irving ISD CCMR and Programs of Study page; used for a one-minute purpose bridge."],
  ["9:00–10:00", "Define Core types as H&L interest patterns, then use the Canvas chart crop to introduce Doer, Analyzer, and Creator. Point to the type, what it likes to do, and one current-life example.", "Students understand the result is not a grade or permanent label and can explain one type with a real-life clue.", "Read one row aloud and let students scan the other two.", "Accept pointing, oral explanation, or private reading.", "Climber Notes, Learning Your Core Personality Types; Canvas six-type reference visual."],
  ["10:00–11:00", "Use the second Canvas chart crop to introduce Helper, Persuader, and Organizer with the same three-column routine. Remind students people may match more than one type.", "Students can explain one type with a real-life clue and avoid stereotypes.", "Read one row aloud and let students scan the other two.", "Accept pointing, oral explanation, or private reading.", "Climber Notes, Learning Your Core Personality Types; Canvas six-type reference visual."],
  ["11:00–12:00", "Direct students to record one prediction and one clue on Core Personality – Day 2 before opening H&L.", "The prediction contains a type and a because-clue; students know it may differ from the result.", "Model one neutral example if students copy only a label.", "Canvas or paper may hold the same two fields when OneNote is unavailable.", "Jennifer Stanley As You Enter prediction choreography, adapted to the verified OneNote page and H&L route."],
  ["12:00–16:00", "Demonstrate Sign in with Google, then point to the yellow Profile Climbs column and Jumpstart Your Profile.", "Every student is in their own account and on the yellow card.", "Reproject the screen if one third is off route.", "Record login problems; never use another student's account.", "Owner-authenticated H&L dashboard screenshot; Jennifer Stanley slide 18 explicit login choreography, adapted to the verified route."],
  ["16:00–19:00", "Read the Jumpstart introduction and click Start once.", "Students see the first question rather than clicking around the dashboard.", "Narrate only the visible Start button.", "Keep students with account problems on the six-type chart.", "Owner-authenticated Jumpstart start screenshot."],
  ["19:00–22:00", "Model selecting one starting-point answer and waiting for Next to activate.", "Students read all five choices.", "Read the choices aloud when needed.", "Do not invent an item count; the screen does not show one.", "Owner-authenticated Jumpstart question screenshot."],
  ["22:00–24:00", "Introduce Discover Your Core and the honest-answer rule, then click Start.", "Students begin the thumbs-choice activity.", "Explain that neither thumb is the better answer.", "Use the provisional class chart if the app fails.", "Owner-authenticated Discover Your Core start screenshot."],
  ["24:00–40:00", "Protect quiet completion time. Circulate for careful reading, not result disclosure.", "The progress bar moves; stop rapid clicking.", "Pause for a read-aloud if one third is stuck on language.", "Keep app problems pending for Friday; no duplicate worksheet.", "Owner-authenticated Discover Your Core question screenshot; Jennifer Stanley slide 19 screenshot-plus-honesty pattern."],
  ["40:00–48:00", "Verify the Core Complete badge. Keep the H&L result open while students move to OneNote → private notebook → CCE Work → Core Personality – Day 2. Students record the result and choose one interpretation route.", "The H&L result remains in the app; OneNote holds the result plus one phrase, real question, or career curiosity.", "Students still in Jumpstart or Core keep working; record the exact stopping point.", "Use a provisional type plus one interpretation in the Canvas or physical equivalent when H&L or OneNote is unavailable.", "Owner-authenticated Core Complete badge screenshot; CCE revised Tuesday response-home boundary."],
  ["48:00–50:00", "Use the three choices as the DOL, record who is complete, working, or blocked, and preview that Wednesday adds Work Values to the same Core result.", "Every student identifies an accurate stopping point and can name the next-day connection.", "Take account problems privately.", "The Friday catch-up list uses this DOL; students keep their available Core result for Wednesday.", "Jennifer Stanley slide 20 sentence-starter exit-ticket pattern; CCE revised Tuesday DOL and Day 3 bridge."],
].map(([time, teacher, monitor, pivot, recovery, source], index) => [
  `Time: ${time}`,
  `Teacher move: ${teacher}`,
  `Student action: ${[
    "Open private notebook → CCE Work → the Monday goal page and Core Personality – Day 2.",
    "Locate both private pages and name which work belongs in H&L and which belongs in OneNote.",
    "Finish the missing reason, action, and checkpoint fields on the same page.",
    "Choose confidence and one usable support on the same page.",
    "Check the action, checkpoint, and support; fix one missing part.",
    "Listen to the FYF p. 21 CCMR definition and give one reason career exploration helps before high school.",
    "Read the Doer, Analyzer, and Creator rows and identify one recognizable clue.",
    "Read the Helper, Persuader, and Organizer rows and identify one recognizable clue.",
    "Record one predicted type and one real-life clue on Core Personality – Day 2.",
    "Select Sign in with Google, confirm the account, and open Profile Climbs.",
    "Open Jumpstart Your Profile and click Start.",
    "Read the choices and answer the Jumpstart starting-point question.",
    "Open Discover Your Core and click Start.",
    "Read and answer each Core question honestly.",
    "Keep the H&L result open, then record the result and one interpretation on Core Personality – Day 2 in OneNote.",
    "Complete at least one private result, phrase, question, or career-curiosity DOL and return the assigned device.",
  ][index]}`,
  `Look-for: ${monitor}`,
  `Pivot/trim: ${pivot}`,
  `Recovery/access: ${recovery}`,
  "[Sources]",
  `- ${source}`,
  "[/Sources]",
]);
if (revisedNotes.length !== presentation.slides.items.length) {
  throw new Error(`Notes count ${revisedNotes.length} does not match slide count ${presentation.slides.items.length}`);
}
revisedNotes.forEach((notes, index) => setNotes(index + 1, notes));

const inspect = await presentation.inspect({
  kind: "slide,textbox,image,notes",
  maxChars: 500_000,
});
await fs.writeFile(path.join(workspace, "final.inspect.ndjson"), inspect.ndjson);

for (let index = 0; index < presentation.slides.items.length; index += 1) {
  const slide = presentation.slides.items[index];
  const number = String(index + 1).padStart(2, "0");
  const png = await presentation.export({ slide, format: "png", scale: 2 });
  await fs.writeFile(
    path.join(previewDir, `final-slide-${number}.png`),
    Buffer.from(await png.arrayBuffer()),
  );
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(
    path.join(layoutDir, `final-slide-${number}.layout.json`),
    await layout.text(),
  );
}

const montage = await presentation.export({ format: "png", montage: true, scale: 1 });
await fs.writeFile(
  path.join(workspace, "final-montage.png"),
  Buffer.from(await montage.arrayBuffer()),
);
const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(outputPath);
console.log(JSON.stringify({ outputPath, slideCount: presentation.slides.items.length, previewDir }, null, 2));
