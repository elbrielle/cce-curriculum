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
const workspace = path.join(root, "tmp/cce-week1-day3-source-clone");
const starterPath = path.join(workspace, "template-starter.pptx");
const outputPath = path.join(
  root,
  "cce-curriculum/resources/avid-reference/source/derived/cce-week1-day3-source-grounded.pptx",
);
const previewDir = path.join(workspace, "final-preview");
const layoutDir = path.join(workspace, "final-layout");

const assets = {
  climberCover: path.join(workspace, "climber-notes-renders/slide-1.png"),
  climberHook: path.join(workspace, "climber-notes-renders/slide-2.png"),
  workValuesRoute: path.join(
    root,
    "cce-curriculum/resources/canvas-licensed/1sw/wk0/day3/open-hats-and-ladders-discover-your-work-values.png",
  ),
  buildingBlocksIntro: path.join(
    root,
    "cce-curriculum/resources/canvas-licensed/1sw/wk0/day3/my-building-blocks-introduction.png",
  ),
  workValuesCard: path.join(root, "cce-curriculum/resources/owner-authenticated-source/hats-and-ladders/screens/work-values-profile-card.png"),
  workValuesStart: path.join(root, "cce-curriculum/resources/owner-authenticated-source/hats-and-ladders/screens/work-values-start.png"),
  workValuesQuestion: path.join(root, "cce-curriculum/resources/owner-authenticated-source/hats-and-ladders/screens/work-values-question.png"),
  workValuesResult: path.join(root, "cce-curriculum/resources/owner-authenticated-source/hats-and-ladders/screens/work-values-result.png"),
  buildingBlockStart: path.join(root, "cce-curriculum/resources/owner-authenticated-source/hats-and-ladders/screens/building-block-introduction.png"),
  buildingBlockChoose: path.join(root, "cce-curriculum/resources/owner-authenticated-source/hats-and-ladders/screens/building-block-choose.png"),
  buildingBlockDescribe: path.join(root, "cce-curriculum/resources/owner-authenticated-source/hats-and-ladders/screens/building-block-describe.png"),
  buildingBlockReflect: path.join(root, "cce-curriculum/resources/owner-authenticated-source/hats-and-ladders/screens/building-block-reflect.png"),
  buildingBlockSaved: path.join(root, "cce-curriculum/resources/owner-authenticated-source/hats-and-ladders/screens/profile-building-block-saved.png"),
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

function normalizeText(value) {
  return value
    .replace(/[\u00a0\u200b]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function textbox(slide, text) {
  const target = normalizeText(text);
  return presentation.resolve(
    recordFor("textbox", slide, (item) => normalizeText(item.text ?? "") === target).id,
  );
}

function setText(slide, before, after) {
  textbox(slide, before).text.set(after);
}

async function replaceOnlyImage(slide, filePath, alt, fit = "contain") {
  const imageRecord = recordFor("image", slide);
  const image = presentation.resolve(imageRecord.id);
  const frame = image.frame;
  const geometry = image.geometry;
  const borderRadius = image.borderRadius;
  const rotation = image.rotation;
  const flipHorizontal = image.flipHorizontal;
  const flipVertical = image.flipVertical;
  const lockAspectRatio = image.lockAspectRatio;
  image.replace({
    blob: await fs.readFile(filePath),
    contentType: "image/png",
    alt,
    fit,
  });
  image.frame = frame;
  image.fit = fit;
  image.crop = { left: 0, top: 0, right: 0, bottom: 0 };
  image.geometry = geometry;
  image.borderRadius = borderRadius;
  image.rotation = rotation;
  image.flipHorizontal = flipHorizontal;
  image.flipVertical = flipVertical;
  image.lockAspectRatio = lockAspectRatio;
}

function setNotes(slideNumber, lines) {
  const slide = presentation.slides.items[slideNumber - 1];
  slide.speakerNotes.textFrame.setText(lines.join("\n"));
  slide.speakerNotes.setVisible(true);
}

function addText(slide, text, position, style = {}) {
  const shape = slide.shapes.add({ geometry: "textbox", position, fill: "none", line: { style: "solid", fill: "none", width: 0 } });
  shape.text = text;
  shape.text.style = { fontSize: style.fontSize ?? 20, bold: style.bold ?? false, color: style.color ?? "#202331", fontFamily: "Aptos" };
  return shape;
}

function coverSlide(slideNumber, title, kicker = "CCE WEEK 1 · WEDNESDAY") {
  const slide = presentation.slides.items[slideNumber - 1];
  [...slide.images.items].forEach((image) => image.delete());
  slide.shapes.deleteAll();
  slide.shapes.add({ geometry: "rect", position: { left: 0, top: 0, width: 960, height: 540 }, fill: "#C9D0EF", line: { style: "solid", fill: "#C9D0EF", width: 0 } });
  const pill = slide.shapes.add({ geometry: "roundRect", position: { left: 28, top: 24, width: 228, height: 30 }, fill: "#FFD357", line: { style: "solid", fill: "#A86600", width: 1 }, borderRadius: "rounded-full" });
  pill.text = kicker;
  pill.text.style = { fontSize: 12, bold: true, color: "#553400", fontFamily: "Aptos" };
  addText(slide, title, { left: 60, top: 64, width: 840, height: 48 }, { fontSize: 30, bold: true });
  return slide;
}

async function addGuidedScreen(slideNumber, config) {
  const slide = coverSlide(slideNumber, config.title, config.kicker);
  slide.shapes.add({ geometry: "roundRect", position: { left: 28, top: 122, width: 330, height: 380 }, fill: "#FFFFFF", line: { style: "solid", fill: "#8390C4", width: 1 }, borderRadius: "rounded-xl" });
  addText(slide, "WHAT YOU SEE", { left: 48, top: 140, width: 280, height: 24 }, { fontSize: 12, bold: true, color: "#6350A8" });
  addText(slide, config.screen, { left: 48, top: 166, width: 280, height: 70 }, { fontSize: 17, bold: true });
  addText(slide, "DO THIS", { left: 48, top: 238, width: 280, height: 22 }, { fontSize: 12, bold: true, color: "#6350A8" });
  addText(slide, config.action, { left: 48, top: 262, width: 280, height: 104 }, { fontSize: 17 });
  slide.shapes.add({ geometry: "roundRect", position: { left: 46, top: 382, width: 294, height: 96 }, fill: "#FFF4C5", line: { style: "solid", fill: "#D69B00", width: 1 }, borderRadius: "rounded-lg" });
  addText(slide, "DONE WHEN", { left: 62, top: 394, width: 250, height: 22 }, { fontSize: 12, bold: true, color: "#7A4A00" });
  addText(slide, config.done, { left: 62, top: 418, width: 250, height: 56 }, { fontSize: 15, bold: true });
  slide.shapes.add({ geometry: "roundRect", position: { left: 394, top: 122, width: 538, height: 380 }, fill: "#FFFFFF", line: { style: "solid", fill: "#8390C4", width: 1 }, borderRadius: "rounded-xl" });
  slide.images.add({ blob: await fs.readFile(config.filePath), contentType: "image/png", alt: config.alt, fit: config.fit ?? "contain", position: { left: 410, top: 138, width: 506, height: 348 } });
  const arrow = slide.shapes.add({ geometry: "rightArrow", position: { left: 344, top: 273, width: 62, height: 42 }, fill: "#FFD357", line: { style: "solid", fill: "#A86600", width: 1 } });
  arrow.text = config.callout ?? "";
  arrow.text.style = { fontSize: 10, bold: true, color: "#553400", fontFamily: "Aptos" };
}

function addGuidedText(slideNumber, title, body, done, kicker = "CCE WEEK 1 · WEDNESDAY") {
  const slide = coverSlide(slideNumber, title, kicker);
  slide.shapes.add({ geometry: "roundRect", position: { left: 70, top: 140, width: 820, height: 238 }, fill: "#FFFFFF", line: { style: "solid", fill: "#8390C4", width: 1 }, borderRadius: "rounded-xl" });
  addText(slide, body, { left: 100, top: 174, width: 760, height: 180 }, { fontSize: 24 });
  slide.shapes.add({ geometry: "roundRect", position: { left: 170, top: 410, width: 620, height: 72 }, fill: "#FFF4C5", line: { style: "solid", fill: "#D69B00", width: 1 }, borderRadius: "rounded-lg" });
  addText(slide, `DONE WHEN: ${done}`, { left: 192, top: 428, width: 576, height: 38 }, { fontSize: 19, bold: true });
}

async function flattenBuildingBlocksPlanSlide() {
  const slide = presentation.slides.items[9];
  const screenshot = (await fs.readFile(assets.buildingBlocksIntro)).toString("base64");
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540">
      <rect width="960" height="540" fill="#C9D0EF"/>
      <rect x="28" y="24" width="228" height="30" rx="15" fill="#FFD357" stroke="#A86600"/>
      <text x="43" y="44" font-family="Arial" font-size="12" font-weight="700" fill="#553400">CCE WEEK 1 · WEDNESDAY</text>
      <text x="60" y="98" font-family="Arial" font-size="30" font-weight="700" fill="#202331">Plan 3 Building Blocks</text>
      <rect x="28" y="122" width="330" height="380" rx="12" fill="#FFFFFF" stroke="#8390C4"/>
      <text x="48" y="157" font-family="Arial" font-size="12" font-weight="700" fill="#6350A8">WHAT YOU SEE</text>
      <text x="48" y="188" font-family="Arial" font-size="17" font-weight="700" fill="#202331">FYF pp. 9–11:</text>
      <text x="48" y="210" font-family="Arial" font-size="17" font-weight="700" fill="#202331">My Building Blocks</text>
      <text x="48" y="254" font-family="Arial" font-size="12" font-weight="700" fill="#6350A8">DO THIS</text>
      <text x="48" y="290" font-family="Arial" font-size="17" fill="#202331">List three real experiences.</text>
      <text x="48" y="314" font-family="Arial" font-size="17" fill="#202331">Name one skill beside each.</text>
      <rect x="46" y="382" width="294" height="96" rx="10" fill="#FFF4C5" stroke="#D69B00"/>
      <text x="62" y="414" font-family="Arial" font-size="12" font-weight="700" fill="#7A4A00">DONE WHEN</text>
      <text x="62" y="443" font-family="Arial" font-size="15" font-weight="700" fill="#202331">FYF shows 3 experiences</text>
      <text x="62" y="464" font-family="Arial" font-size="15" font-weight="700" fill="#202331">and 3 skills.</text>
      <path d="M344 273h40v-13l22 34-22 34v-13h-40z" fill="#FFD357" stroke="#A86600"/>
      <text x="355" y="299" font-family="Arial" font-size="10" font-weight="700" fill="#553400">DO</text>
      <rect x="394" y="122" width="538" height="380" rx="12" fill="#FFFFFF" stroke="#8390C4"/>
      <image x="410" y="138" width="506" height="348" href="data:image/png;base64,${screenshot}" preserveAspectRatio="xMidYMid meet"/>
    </svg>`;
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  [...slide.images.items].forEach((image) => image.delete());
  slide.shapes.deleteAll();
  slide.images.add({
    blob: png,
    contentType: "image/png",
    alt: "Directions for recording three Building Blocks in Find Your Future pages 9 through 11",
    fit: "fill",
    position: { left: 0, top: 0, width: 960, height: 540 },
  });
}

setText(1, "Week 1.6", "CCE Day 3");
textbox(1, "AVID 2\nMs. Hainlen").delete();
const day3Subtitle = addText(
  presentation.slides.items[0],
  "Work Values + Building Blocks\nCareer & College Explorations",
  { left: 150, top: 294, width: 675, height: 78 },
  { fontSize: 20, bold: true, color: "#5A2D91" },
);
day3Subtitle.text.style = { fontSize: 20, bold: true, color: "#5A2D91", fontFamily: "Aptos", alignment: "center" };

setText(2, "Friday", "Wednesday");

setText(
  3,
  "Today’s Lesson\nFour Corners",
  "Today’s Lesson\nWork Values\nBuilding Blocks\nOne Connection",
);
setText(
  3,
  "Pencil\nName Tent\nGet ready to share an answer ——>",
  "Open H&L\nFYF workbook to pp. 9–11\nOpen Work Values + Building Blocks — Day 3\nChoose partner-share or private response",
);
await replaceOnlyImage(
  3,
  assets.climberCover,
  "Climber Notes cover for Exploring Your Work Values",
);

setText(4, "Four Corners – Quickwrite", "Quickwrite: Which would you choose?");
setText(
  4,
  "Write down which position you want to take from the list below and explain why:\nStrongly agree\nAgree\nDisagree\nStrongly disagree",
  "Write one choice and explain why:\nHigher pay while working alone\nLower pay with a team you enjoy",
);
setText(
  4,
  "It is more important to be happy than successful.",
  "Which choice fits what matters to you right now?",
);
setText(
  4,
  "Word Bank:\nHappy                            successful\nImportant                                goals\nMoney\nstress\nFamily                   career\nBalance\nachievement",
  "Word Bank:\npay     team     independence\nsupport     fun     stress\nbalance     goals     relationships",
);

setText(5, "Engage: Move and Discuss", "Choose How You Respond");
setText(
  5,
  "It is more important to be happy than successful.",
  "Higher pay + work alone\nOR\nlower pay + a team you enjoy?",
);
setText(5, "STRONGLY AGREE", "MOVE TO A");
setText(5, "AGREE", "MOVE TO B");
setText(5, "DISAGREE", "STAY SEATED");
setText(5, "STRONGLY DISAGREE", "PRIVATE CHECK");
setText(
  5,
  "Move to the corner that most accurately represents your stance.\nEngage in a group discussion justifying why you chose your corner.",
  "Choose one route:\nMove or point to A/B.\nStay seated and hold up 1/2.\nKeep your written answer private.\nEvery route counts.",
);

setText(6, "Evaluate: Share and Learn", "Share and Name the Value");
setText(
  6,
  "It is more important to be happy than successful.",
  "What value is inside your reason?",
);
setText(6, "STRONGLY AGREE", "PAY");
setText(6, "AGREE", "TEAM");
setText(6, "DISAGREE", "OWN WAY");
setText(6, "STRONGLY DISAGREE", "SUPPORT");
setText(
  6,
  "Identify a spokesperson who will summarize your group’s position for the rest of the groups.\nShare and engage in a debate with each other.\nBefore a group shares their next point, they must summarize the point of the group that preceded them.",
  "Partner A: share your reason for 30 seconds.\nPartner B: name the value you hear.\nSwitch.\nA written self-check or private teacher check counts.",
);

setText(7, "Skills Check", "Six Starter Values");
setText(
  7,
  "Here are some ideas (but you can create your own!)\n☐ Turn in all assignments on time\n☐ Bring my supplies to every class\n☐ Write down homework every day\n☐ Participate at least once in each class\n☐ Ask questions when I need help\n☐ Study or review notes for at least 15 minutes each night\n☐ Keep my binder or folders organized\n☐ Check my grades this week\n☐ Get to class on time every day\n☐ Limit distractions during class",
  "Achievement — goals and results\nIndependence — choices and your own way\nRecognition — noticed and rewarded\nRelationships — helping and working with people\nSupport — clear help and guidance\nWorking Conditions — schedule, tasks, environment, and security",
);
await replaceOnlyImage(
  7,
  assets.climberHook,
  "Climber Notes explanation of how work values reveal preferred work environments",
);

setText(8, "Pomodoro work time", "Discover Your Work Values");
setText(
  8,
  "Expectations:\nYou are working.\nSitting with your grades open doing nothing else is not working.\nI have grammar practice if you don’t have anything to do.\nHave your sticky note where I can see it as I walk around– the edge of the table.\nWe will be working silently the first 15 minutes. Your table will gain/lose points for focused/off-task behavior.\nAdditionally, being on task is a grade today.",
  "Open H&L → Profile → Discover Your Work Values.\nRead each choice. Do not rapid-click.\nComplete the activity honestly.\nLeave your result open.\nIf the app is unavailable, use the six starter values for a provisional choice.",
);

setText(9, "Skills Check", "Your Result");
setText(
  9,
  "Each week, we will check in on our grades, planners, and goals.\nCheck your grades. If you don’t have a grade yet, write “N/A” for “not available.”\nGet your planner out. Answer the questions honestly.\nGet out your goal from last week. Look at it and reflect on your progress.\nCreate a new academic goal.",
  "In Work Values + Building Blocks — Day 3, write:\nMy top work values are ____.\nI expected / was surprised by ____ because ____.\nYour result is one clue, not a final answer.",
);
await replaceOnlyImage(
  9,
  assets.workValuesRoute,
  "Hats & Ladders route showing Profile and Discover Your Work Values",
);

setText(10, "Welcome!", "Building Blocks");
setText(
  10,
  "Get Ready\n",
  "Open FYF pp. 9–11",
);
setText(
  10,
  "Pencil\nName Tent\nGet ready to share an answer ——>",
  "Experience is more than paid work.\nSchool • home • community • interests",
);
setText(
  10,
  "Today’s Lesson\nFlex Time",
  "Today’s Lesson\nName what you did.\nName the skill it built.",
);
setText(
  10,
  "Discussion\n\n",
  "FYF pp. 9–11",
);
await replaceOnlyImage(
  10,
  assets.buildingBlocksIntro,
  "Find Your Future page 9 introducing My Building Blocks",
);

setText(11, "Pomodoro work time", "Model / Not Yet");
setText(
  11,
  "Expectations:\nYou are working.\nSitting with your grades open doing nothing else is not working.\nI have grammar practice if you don’t have anything to do.\nHave your sticky note where I can see it as I walk around– the edge of the table.\nWe will be working silently the first 15 minutes. Your table will gain/lose points for focused/off-task behavior.\nAdditionally, being on task is a grade today.",
  "COMPLETE\nI help my younger cousin with homework.\nSkill: explaining clearly and patience.\nPossible cluster: Education & Training.\nNOT YET\n“I play games. It builds gaming. Any cluster.”\nRepair it: name the action—planning, teamwork, persistence, or communication.",
);

setText(12, "Pomodoro work time", "Record three Building Blocks");
setText(
  12,
  "Write this information on a sticky note\nIdentify 3 different tasks you want to accomplish during the 4 POMODORO work periods you will have today.\nIdentify 2 “No Zone” activities. These are usually distractions that you should avoid that keep you from staying productive.",
  "Open FYF pp. 9–11.\nRecord at least three real experiences. Beside each one, name a visible skill.\nUse school, home, community, or interests. A school, hobby, or fictional example is allowed.",
);
setText(
  12,
  "Name / Period\n---------------------------------------",
  "EXPERIENCE\nWHAT I DID\nSKILL I BUILT",
);
setText(12, "NO ZONE", "3 BLOCKS");

setText(13, "Evaluate: Share and Learn", "Partner Skill Spotter");
setText(
  13,
  "It is more important to be happy than successful.",
  "One experience.\nOne skill.\nThen switch.",
);
setText(13, "STRONGLY AGREE", "PARTNER A");
setText(13, "AGREE", "SHARE");
setText(13, "DISAGREE", "PARTNER B");
setText(13, "STRONGLY DISAGREE", "NAME THE SKILL");
setText(
  13,
  "Identify a spokesperson who will summarize your group’s position for the rest of the groups.\nShare and engage in a debate with each other.\nBefore a group shares their next point, they must summarize the point of the group that preceded them.",
  "Partner A shares one Building Block for 30 seconds.\nPartner B names the skill they hear.\nSwitch.\nA private teacher check or written self-check counts.",
);

setText(14, "Pomodoro work time", "Save the profile inputs");
setText(
  14,
  "Expectations:\nYou are working.\nSitting with your grades open doing nothing else is not working.\nI have grammar practice if you don’t have anything to do.\nHave your sticky note where I can see it as I walk around– the edge of the table.\nWe will be working silently the first 15 minutes. Your table will gain/lose points for focused/off-task behavior.\nAdditionally, being on task is a grade today.",
  "Return to H&L.\nSave at least three Building Blocks.\nLocate any first cluster recommendations.\nTreat recommendations as starting suggestions.\nNo recommendations yet? Do not invent them. Mark “cluster pending” and return Friday.",
);

setText(
  15,
  "Exit: Debrief – Initiating Student Ownership in the Classroom",
  "Connect one value to one experience",
);
setText(
  15,
  "What was your role in ensuring that this activity was successful?\nIn what ways do you feel more confident as a result of this activity?\nWhat can you do differently next time to ensure that similar activities are even more successful and beneficial?",
  "In your private CCE page, complete:\nOne value I care about is ____.\nOne Building Block that shows a related skill is ____.\nA cluster I may investigate is ____ because ____.\nNo recommendation yet? Write “cluster pending.”",
);

setText(16, "Week 1.6", "Thursday");
setText(
  16,
  "AVID 2\nMs. Hainlen",
  "Bring your saved results, FYF pp. 9–11,\nand your private connection.",
);

addGuidedText(3, "Today: 4 steps", "TEKS §127.2(d)(1)(A), (B)\n\n1. Discover your top work values in H&L.\n2. Record three experiences and skills in FYF pp. 9–11.\n3. Save the same three in H&L.\n4. Write one private connection.", "your profile shows 3 Building Blocks and your DOL is complete");
addGuidedText(4, "Do Now · Which matters more to you?", "Choose ONE: doing work your own way OR working closely with a team.\n\nWrite one reason in your private OneNote page.\n\nSentence starter: I chose ____ because ____.", "you chose one and explained why");
addGuidedText(5, "Share or stay private", "Partner: read your reason. Your partner names the value. Switch.\n\nPrivate: underline the word that shows what matters.", "you named one value");
await addGuidedScreen(6, { title: "Step 1 · Open Discover Your Work Values", screen: "The Work Values card in your H&L Profile Climbs", action: "Click Discover Your Work Values.", done: "The Work Values start screen is open.", filePath: assets.workValuesCard, alt: "Hats and Ladders Profile Climbs card labeled Discover Your Work Values", callout: "CLICK" });
await addGuidedScreen(7, { title: "Step 2 · Start Work Values", screen: "The Discover Your Work Values start card", action: "Read the directions. Click Start when you are ready.", done: "The first pair of choices is open.", filePath: assets.workValuesStart, alt: "Hats and Ladders Discover Your Work Values start screen with Start button", callout: "GO" });
await addGuidedScreen(8, { title: "Step 3 · Choose the better fit", screen: "Two work choices side by side", action: "Read both. Choose the one that fits you better. Click Next and keep going.", done: "The progress bar moves after each choice.", filePath: assets.workValuesQuestion, alt: "Hats and Ladders Work Values question with two choices and Next button", callout: "PICK" });
await addGuidedScreen(9, { title: "Step 4 · Record 2 values", screen: "Your Work Values result with two value names", action: "In OneNote, write: My top work values are ____ and ____. Then click Continue.", done: "Both values are in OneNote and H&L returns to your profile.", filePath: assets.workValuesResult, alt: "Hats and Ladders Work Values result showing two top values and Continue button", callout: "NOTE" });
await addGuidedScreen(10, { title: "Plan 3 Building Blocks", screen: "FYF pp. 9–11: My Building Blocks", action: "List three real experiences. Name one skill beside each.", done: "FYF shows 3 experiences and 3 skills.", filePath: assets.buildingBlocksIntro, alt: "Find Your Future page introducing My Building Blocks", callout: "DO" });
await flattenBuildingBlocksPlanSlide();
addGuidedText(11, "Name the action", "STRONG: I help my cousin with homework.\nSkill: explain clearly and show patience.\n\nTOO VAGUE: I play games. Skill: gaming.\n\nREPAIR: name what you did—plan, communicate, solve, lead, practice, or persist.", "each Building Block names an action");
addGuidedText(12, "Step 2 · Record 3 in FYF", "On FYF pp. 9–11, write THREE real experiences.\n\nBeside each, name ONE visible skill.\n\nSchool, home, community, interests, or a fictional example may be used.", "FYF shows 3 experiences and 1 skill beside each");
addGuidedText(13, "Check the same 3", "Point to each FYF entry.\n\n1. What did you do?\n2. What skill does it show?\n3. Are these the same three you will save in H&L?", "all 3 FYF entries are ready for H&L");
await addGuidedScreen(14, { title: "Step 3 · Save FYF Block 1", screen: "Step 1 of 4: Choose", action: "Use FYF entry 1. Choose the closest honest category and activity. Click Next.", done: "FYF entry 1 is selected in H&L.", filePath: assets.buildingBlockChoose, alt: "Hats and Ladders Building Block Choose screen, step 1 of 4", callout: "PICK" });
await addGuidedScreen(15, { title: "Save the same 3", screen: "Step 2 of 4: Describe", action: "Describe the same FYF entry, Reflect, review, and save. Repeat for entries 2 and 3.", done: "The same 3 FYF Building Blocks are saved in H&L.", filePath: assets.buildingBlockDescribe, alt: "Hats and Ladders Building Block Describe screen, step 2 of 4", callout: "SAVE" });
await addGuidedScreen(16, { title: "DOL · 3 saved blocks", screen: "Your H&L Profile and Building Blocks count", action: "Repeat until the count is 3. Then write one value-to-block connection in OneNote. Keep these inputs—you will use them in My Career Journey tomorrow.", done: "The count is 3 and the private sentence is complete.", filePath: assets.buildingBlockSaved, alt: "Hats and Ladders profile showing a saved Building Block and the Building Blocks count", callout: "DONE" });

const noteSets = [
  [
    "[Timing] Before class",
    "[Teacher move] Open this Day 3 source-grounded deck, verify H&L, set FYF pp. 9–11 at each seat, and open the Student Guide and private response page. The required Climber Notes frames are already embedded here.",
    "[Look-for] One workbook per student and the fixed six-value list available without another packet.",
    "[Pivot] If H&L is down, prepare the provisional-value route before students enter.",
    "[Trim] Do not trim prep that protects the H&L/FYF response homes.",
    "[Recovery] Paper or Canvas may hold the private connection; no recopying is required later.",
    "[Sources]",
    "- Jenna Hainlen, AVID Week 1.6 slide 1, botanical cover layout.",
    "- CCE 1SW Wk0 Day 3 canonical lesson, accessed 2026-08-15.",
    "[/Sources]",
  ],
  [
    "[Timing] 0:00–0:10",
    "[Teacher move] Use as the Wednesday divider while students settle.",
    "[Look-for] Students move toward H&L, FYF pp. 9–11, and the private page.",
    "[Pivot] If setup is slow, advance immediately to the Welcome slide.",
    "[Trim] This slide may be shown for only a few seconds.",
    "[Recovery] The Welcome slide carries the complete setup list.",
    "[Sources]",
    "- Jenna Hainlen, AVID Week 1.6 slide 16, floral day-divider layout.",
    "[/Sources]",
  ],
  [
    "[Timing] 0:10–0:40",
    "[Teacher move] Name the three response homes: H&L stores values/profile data; FYF holds Building Blocks; the private page holds one short synthesis.",
    "[Look-for] Students record only the evidence named in the Day 3 guide.",
    "[Pivot] Direct students without a device to FYF and the fixed-value provisional route.",
    "[Trim] Keep the one-response-home explanation even if setup is fast.",
    "[Recovery] Canvas or one paper page is equal to the digital private page.",
    "[Sources]",
    "- Jenna Hainlen, AVID Week 1.6 slide 17, Welcome/Get Ready/Today's Lesson choreography.",
    "- Climber Notes, Exploring Your Work Values, slide 1, cover image.",
    "[/Sources]",
  ],
  [
    "[Timing] 0:40–2:30",
    "[Teacher move] Give silent private think time. Ask students to choose one option and name why.",
    "[Look-for] A reason that reveals pay, independence, relationships, support, balance, or another value.",
    "[Pivot] Read the two options aloud and let students circle one.",
    "[Trim] One phrase is enough; do not turn this into a paragraph.",
    "[Recovery] A fictional worker may answer if a student does not want to disclose a personal preference.",
    "[Sources]",
    "- Jenna Hainlen, AVID Week 1.6 slide 18, Four Corners quickwrite structure and word-bank placement.",
    "- CCE Day 3 work-value opener.",
    "[/Sources]",
  ],
  [
    "[Timing] 2:30–4:00",
    "[Teacher move] Offer movement, pointing, seated 1/2, and private written routes as equal options.",
    "[Look-for] Every student chooses a route; no one is pressured to move or disclose.",
    "[Pivot] If movement will cost time, keep everyone seated and use fingers 1/2 or the private page.",
    "[Trim] Skip corner movement before trimming the private choice.",
    "[Recovery] The written quickwrite is complete evidence for this step.",
    "[Sources]",
    "- Jenna Hainlen, AVID Week 1.6 slide 19, Four Corners move-and-discuss layout.",
    "- CCE Day 3 equal seated/private response route.",
    "[/Sources]",
  ],
  [
    "[Timing] 4:00–5:00",
    "[Teacher move] Ask two students or one partner pair to name the value inside a reason. Keep reasons private unless volunteered.",
    "[Look-for] Students name a value rather than repeating the choice.",
    "[Pivot] Model one: choosing the team may point to relationships or support.",
    "[Trim] One teacher model may replace public sharing.",
    "[Recovery] A student may write the value or use a private teacher check.",
    "[Sources]",
    "- Jenna Hainlen, AVID Week 1.6 slide 20, share-and-learn structure.",
    "- CCE Day 3 work-value opener and private-think/partner-discuss rhythm.",
    "[/Sources]",
  ],
  [
    "[Timing] 5:00–9:00",
    "[Teacher move] Introduce the six source-grounded starter values. Explain that H&L may return different words.",
    "[Look-for] Students can distinguish a value from a skill or personality type.",
    "[Pivot] Read only the bold value names, then give one example students request.",
    "[Trim] Do not cut the six words; shorten definitions first.",
    "[Recovery] Keep this slide projected if H&L is unavailable so students can make a provisional choice.",
    "[Sources]",
    "- Jenna Hainlen, AVID Week 1.6 slide 7, idea-list plus source image layout.",
    "- Climber Notes, Exploring Your Work Values, slide 2, work-values hook.",
    "- H&L legacy source excerpt, Discovering My Work Values, six common values; used only to preserve the approved fixed-list scaffold.",
    "[/Sources]",
  ],
  [
    "[Timing] 9:00–18:00",
    "[Teacher move] Demonstrate the verified route, then release students. Limit explanation to the first four minutes of the 15-minute work-values block.",
    "[Look-for] By minute 20, every student is in the correct activity or has a provisional value from the fixed list.",
    "[Pivot] If one third is off-route, pause and reproject Profile → Discover Your Work Values.",
    "[Trim] Shorten partner talk; do not cut the honest completion of the activity.",
    "[Recovery] Never enter personal results in another student's account. Use the provisional list if H&L is down.",
    "[Sources]",
    "- Jenna Hainlen, AVID Week 1.6 slide 10, expectations layout.",
    "- Climber Notes, Exploring Your Work Values, slide 3, verified H&L route.",
    "[/Sources]",
  ],
  [
    "[Timing] 18:00–20:00",
    "[Teacher move] Students leave the result open and write only the expected/surprised response in the private CCE page.",
    "[Look-for] A named value and one because-reason; no full result is required aloud.",
    "[Pivot] If writing is slow, accept the sentence stem with one phrase in each blank.",
    "[Trim] Do not add a separate exit ticket or reflection sheet.",
    "[Recovery] Use a provisional value and mark it for Friday if the app did not load.",
    "[Sources]",
    "- Jenna Hainlen, AVID Week 1.6 slide 6, title/body/source-image instructional pattern.",
    "- Climber Notes, Exploring Your Work Values, slide 3.",
    "- Authenticated H&L route screenshot from the Day 3 Canvas asset folder.",
    "[/Sources]",
  ],
  [
    "[Timing] 20:00–23:00",
    "[Teacher move] Open FYF pp. 9–11. Explain that experience includes ordinary school, home, community, and interest activities.",
    "[Look-for] Students begin from things they actually do, not job titles they hope to have.",
    "[Pivot] Name one ordinary example from each category.",
    "[Trim] Read the category names; let the authentic workbook page carry the detail.",
    "[Recovery] Students may use school, hobby, community, or fictional examples rather than private family details.",
    "[Sources]",
    "- Jenna Hainlen, AVID Week 1.6 slide 13, Welcome/Get Ready/Today's Lesson pattern.",
    "- Find Your Future p. 9, My Building Blocks, authenticated page image.",
    "[/Sources]",
  ],
  [
    "[Timing] 23:00–26:00",
    "[Teacher move] Read the complete model, then contrast it with the non-model. Ask students to name the action hiding inside 'gaming.'",
    "[Look-for] Skills are actions students can explain, not only vague traits.",
    "[Pivot] Model one more ordinary experience if one third of the class is blank.",
    "[Trim] Keep one complete model and one non-model; do not add more examples.",
    "[Recovery] A student may use the complete model as a structure but must substitute their own or a fictional experience.",
    "[Sources]",
    "- Jenna Hainlen, AVID Week 1.6 slide 10, focused-work expectations pattern.",
    "- CCE Day 3 complete model and non-model.",
    "- Find Your Future pp. 9–11, My Building Blocks, model grounded in the canonical Day 3 plan.",
    "[/Sources]",
  ],
  [
    "[Timing] 26:00–34:00",
    "[Teacher move] Students record at least three real experiences and a visible skill beside each on FYF pp. 9–11.",
    "[Look-for] By minute 34, students have three experiences and a skill beside each.",
    "[Pivot] If one third is blank, pause and model one ordinary experience rather than distribute another packet.",
    "[Trim] Reduce the number of categories discussed; do not cut the three Building Blocks.",
    "[Recovery] Without FYF, use one paper/notebook page with the four categories and accept it without later recopying.",
    "[Sources]",
    "- Jenna Hainlen, AVID Week 1.6 slide 9, focused work-planning layout.",
    "- Find Your Future pp. 9–11, My Building Blocks.",
    "[/Sources]",
  ],
  [
    "[Timing] 34:00–37:00",
    "[Teacher move] Partner A shares one Building Block for 30 seconds; Partner B names the skill; switch.",
    "[Look-for] The listener names evidence from the experience rather than guessing a personality type.",
    "[Pivot] Use a teacher-led anonymous example if partner talk stalls.",
    "[Trim] One round is the protected minimum before profile saving.",
    "[Recovery] A private teacher check or written self-check is equal to partner sharing.",
    "[Sources]",
    "- Jenna Hainlen, AVID Week 1.6 slide 20, structured share-and-learn choreography.",
    "- CCE Day 3 Partner A/Partner B skill-spotter routine.",
    "[/Sources]",
  ],
  [
    "[Timing] 37:00–45:00",
    "[Teacher move] Students return to H&L, save at least three Building Blocks, and locate any first cluster recommendations.",
    "[Look-for] Saved profile inputs, not invented recommendations.",
    "[Pivot] If H&L has consumed more than 20 total minutes, defer profile saves and recommendations to Friday.",
    "[Trim] Defer recommendations before cutting the three FYF Building Blocks or final connection.",
    "[Recovery] Mark app saves/recommendations for Friday; keep the completed FYF evidence.",
    "[Sources]",
    "- Jenna Hainlen, AVID Week 1.6 slide 10, focused-work expectations pattern.",
    "- CCE Day 3 save-profile-inputs and recommendations step.",
    "[/Sources]",
  ],
  [
    "[Timing] 45:00–49:40",
    "[Teacher move] Students complete the value-to-Building-Block-to-cluster sentence in the private CCE page, then clean up.",
    "[Look-for] One value, one related skill from a Building Block, and one possible cluster with a because-reason.",
    "[Pivot] If recommendations are missing, students write 'cluster pending' and complete the reason after access returns.",
    "[Trim] Protect this synthesis; shorten public sharing or recommendations instead.",
    "[Recovery] Accept a school, hobby, or fictional example and do not require family, health, financial, immigration, or caregiving disclosure.",
    "[Sources]",
    "- Jenna Hainlen, AVID Week 1.6 slide 21, reflection/close layout.",
    "- CCE Day 3 final private connection.",
    "- Jeswin Thomas on Unsplash, classroom photo; original on-slide attribution preserved.",
    "[/Sources]",
  ],
  [
    "[Timing] 49:40–50:00",
    "[Teacher move] Preview Thursday: students will bring these saved inputs into My Career Journey.",
    "[Look-for] FYF stays in the room and students know where their private page is saved.",
    "[Pivot] If time expires, show this while students exit.",
    "[Trim] Do not add a new task.",
    "[Recovery] Thursday begins with retrieval of the same three inputs.",
    "[Sources]",
    "- Jenna Hainlen, AVID Week 1.6 slide 1, botanical cover layout reused as a transition.",
    "- CCE Day 3 to Day 4 bridge.",
    "[/Sources]",
  ],
];

const revisedNotes = [
  ["0:00–0:15", "Open the Day 3 source-grounded deck, H&L, FYF pp. 9–11, and the private OneNote page.", "Materials are ready without another worksheet.", "Prepare the provisional-value route if H&L is down.", "Paper or Canvas may hold the private connection; no recopying.", "Jenna Hainlen, AVID botanical cover layout; CCE Day 3 canonical lesson."],
  ["0:15–0:30", "Use the Wednesday divider while students settle.", "Students move toward H&L, FYF, and OneNote.", "Advance immediately if setup is already complete.", "The agenda carries the full setup list.", "Jenna Hainlen, AVID day-divider layout."],
  ["0:30–1:00", "Name the four actions and the exact end state: 3 saved Building Blocks plus one private connection.", "Students can name the work order.", "Point to the numbered actions; do not explain each app screen yet.", "Without H&L, protect FYF and the private connection.", "Jennifer Stanley, Career Exploration slide 3 Need/Do Now choreography; CCE Day 3 canonical contract."],
  ["1:00–4:00", "Give silent think time for one work-preference choice and one reason.", "The reason reveals something the student values.", "Read both choices aloud and offer the sentence starter.", "A fictional worker may answer instead of personal disclosure.", "Jennifer Stanley, Career Exploration slides 3 and 21, Do Now pattern; CCE work-value opener."],
  ["4:00–5:00", "Offer partner share and private underline routes as equal choices.", "Students name a value inside the reason.", "Model one: choosing a team may point to relationships or support.", "A written self-check counts.", "Jenna Hainlen structured share routine, adapted for equal access."],
  ["5:00–7:00", "Demonstrate Sign in with Google, then click Discover Your Work Values in Profile Climbs.", "Every student is in the correct card in their own account.", "Reproject if one third is off route.", "Record account problems; never use another student's account.", "Owner-authenticated H&L Work Values card screenshot; Jennifer Stanley slide 22 route choreography, adapted to the verified route."],
  ["7:00–9:00", "Read the short introduction and click Start once.", "Students see the first pair of choices.", "Narrate only the visible Start button.", "Use the provisional six-value list if the app fails.", "Owner-authenticated Work Values start screenshot."],
  ["9:00–18:00", "Protect quiet completion time; circulate for careful reading rather than rapid clicking.", "The progress bar moves and students choose the better fit.", "Read one pair aloud if language blocks one third of the class.", "Do not invent an item count; the screen does not show one.", "Owner-authenticated Work Values question screenshot; Jennifer Stanley slide 19 honest-answer pattern."],
  ["18:00–20:00", "Students record the two visible value names in OneNote, then click Continue.", "Both value names are recorded; no public disclosure is required.", "Accept the two names only if writing is slow.", "Use two provisional values and mark pending if H&L is unavailable.", "Owner-authenticated Work Values result screenshot; Jennifer Stanley slide 22 result-to-notebook pattern, adapted for the private OneNote page."],
  ["20:00–23:00", "Open FYF pp. 9–11 and explain that ordinary experiences count.", "Students begin from things they actually do, not future job titles.", "Name one school, home, community, and interest example.", "A fictional example is acceptable when privacy matters.", "Find Your Future pp. 9–11; Jennifer Stanley slides 24–25 workbook-page enlargement pattern."],
  ["23:00–26:00", "Model the difference between an activity label and an observable skill.", "Students can repair one vague example before independent work.", "Model one ordinary experience if one third is blank.", "A fictional example is acceptable when privacy matters.", "Find Your Future pp. 9–11; CCE complete model and non-model."],
  ["26:00–34:00", "Students record three experiences and one visible skill beside each on FYF pp. 9–11.", "By minute 34, FYF has 3 experiences and a skill beside each.", "Model one ordinary experience if one third is blank.", "Without FYF, use one accepted notebook or paper table with no later recopying.", "Find Your Future pp. 9–11; Jennifer Stanley slides 24–25 one-workbook-action-per-slide pattern."],
  ["34:00–37:00", "Run a fast three-entry check before students return to H&L.", "The same three FYF experiences are ready to save in the app.", "Ask only what did you do and what skill does it show.", "A private teacher or self-check counts.", "Find Your Future pp. 9–11; CCE Day 3 same-three parity rule."],
  ["37:00–40:00", "Open Add a Building Block and choose the category/activity that match the first FYF entry.", "The first FYF experience is selected before Next.", "Use the closest honest label if there is no exact match.", "Do not invent a different app experience; preserve the FYF list for Friday if H&L fails.", "Owner-authenticated Building Block Choose screenshot."],
  ["40:00–45:00", "Describe, reflect, review, and save the same FYF entry; repeat for entries 2 and 3.", "H&L shows the same three experiences recorded in FYF.", "Keep descriptions brief and use the FYF skill sentence as support.", "Mark the exact saved count for Friday if app time expires.", "Owner-authenticated Building Block Describe screenshot; CCE Day 3 same-three parity rule."],
  ["45:00–50:00", "Students repeat until H&L shows 3 Building Blocks, complete the private value-to-experience sentence, and hear that these inputs return in My Career Journey tomorrow.", "H&L count is 3 and the sentence names one value, one Building Block, and because-reason.", "Protect the third Building Block, DOL, and Thursday bridge; trim public sharing first.", "If app time expires, mark the exact count for Friday and keep the FYF evidence for My Career Journey.", "Owner-authenticated saved Building Block profile screenshot; Jennifer Stanley slides 26–27 three-block target and sentence-starter DOL, adapted to the current contract; CCE Day 3 to Day 4 bridge."],
].map(([time, teacher, monitor, pivot, recovery, source], index) => [
  `Time: ${time}`,
  `Teacher move: ${teacher}`,
  `Student action: ${[
    "No student action; this is the before-class setup frame.",
    "Settle with H&L, FYF pp. 9–11, and the private response page ready.",
    "Name the four-step work order and the three-Building-Block end state.",
    "Choose one work preference and write one reason.",
    "Share the reason with a partner or underline the value privately.",
    "Use Sign in with Google and open Discover Your Work Values.",
    "Read the introduction and click Start.",
    "Read each pair and choose the better fit.",
    "Record the two visible Work Values and continue.",
    "Open FYF pp. 9–11 and identify ordinary experiences that count.",
    "Record three experiences and one visible skill beside each.",
    "Record three experiences and one visible skill beside each on FYF pp. 9–11.",
    "Check that the same three FYF entries are ready to save in H&L.",
    "Choose the category and activity that match the first FYF example.",
    "Describe, reflect, review, and save the same FYF example; repeat for entries 2 and 3.",
    "Repeat until three Building Blocks are saved; complete the private connection, DOL, and cleanup.",
  ][index]}`,
  `Look-for: ${monitor}`,
  `Pivot/trim: ${pivot}`,
  `Recovery/access: ${recovery}`,
  "[Sources]",
  `- ${source}`,
  "[/Sources]",
]);
if (revisedNotes.length !== presentation.slides.items.length) {
  throw new Error(
    `Notes count ${revisedNotes.length} does not match slide count ${presentation.slides.items.length}`,
  );
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

console.log(
  JSON.stringify(
    { outputPath, slideCount: presentation.slides.items.length, previewDir, layoutDir },
    null,
    2,
  ),
);
