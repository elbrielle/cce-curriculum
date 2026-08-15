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

const { FileBlob, PresentationFile } = await importRuntimeModule("@oai/artifact-tool");
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

setText(2, "Pencil\nGet ready to share an answer ——> ", "Chromebook\nFind Your Future workbook\nOpen your private CCE notebook");
setText(2, "Ball Toss\nFinish Successful Student Poster", "Predict your type\nSet up Profile + Discover Your Core\nSave one private interpretation");
await replaceRouteImage(2);

setText(3, "Think", "Think");
setText(3, "What are some behaviors that successful students do?\n", "Choose ONE word that sounds most like you right now:\n\nDoer  •  Analyzer  •  Creator  •  Helper  •  Persuader  •  Organizer\n\nWrite your prediction. Do not look anything up yet.");

setText(4, "stand-share-sit", "Share or stay private");
setText(4, "Everyone stand.\n\nShare with your partner: What are some behaviors that successful students do?\n\nOnce you share, sit down. \n", "Choose one route.\n\nShare seated or standing: Which word did you predict, and what clue made you choose it?\n\nOr write your answer privately. When you finish, look up.");

setText(5, "Let’s write!", "Why are we doing this now?");
setText(5, "Seat 1- Writer", "CCMR\nCollege, Career, and Military Readiness means preparing for life after high school.");
setText(5, "Question\n\nOf the nine soft skills described in the article, which one does your table think is the most important for success in high school right now? Explain your reasoning.\n\nMinimum: 3 sentences", "PROGRAM OF STUDY\n\nA sequence of related courses that combines classroom learning, hands-on experience, and skill development.\n\nDiscuss: Why start thinking about future goals before high school?");

setText(6, "Let’s write!", "Three Hats & Ladders words");
setText(6, "Seat 2- Speaker", "CLIMBER\nYou\nHAT\nA career you can explore");
setText(6, "Question\n\nOf the nine soft skills described in the article, which one does your table think is the most important for success in high school right now? Explain your reasoning.\n\nMinimum: 3 sentences", "CLUSTER\nA group of related careers\n\nYour Climber Profile gathers what you learn about yourself. It grows across our three Core Days.");

setText(7, "Think", "Think");
setText(7, "What are some behaviors that successful students do?\n", "Why do some activities feel natural while others feel like a chore?\n\nPersonality types can help explain the difference. Most people match more than one type.");

setText(8, "Let’s write!", "Meet the six core types");
setText(8, "Seat 1- Writer", "DOER\nHands, tools, real problems\nANALYZER\nResearch, observe, ask why\nCREATOR\nArt, music, writing");
setText(8, "Question\n\nOf the nine soft skills described in the article, which one does your table think is the most important for success in high school right now? Explain your reasoning.\n\nMinimum: 3 sentences", "HELPER\nSupport, teach, connect with people\n\nPERSUADER\nLead, influence, motivate\n\nORGANIZER\nData, numbers, systems, accuracy");

setText(9, "Let’s write!", "Try a quick match");
setText(9, "Seat 2- Speaker", "With a partner or privately:\nChoose a likely top type.\nName one clue.\nMore than one answer may fit.");
setText(9, "Question\n\nOf the nine soft skills described in the article, which one does your table think is the most important for success in high school right now? Explain your reasoning.\n\nMinimum: 3 sentences", "Which core type might fit a nurse?\n\nA chef?\n\nA pilot?\n\nWhy can one career need more than one type?");

setText(10, "Welcome!", "Open Hats & Ladders");
setText(10, "Get Ready", "Campus login");
setText(10, "Today’s Lesson", "Exact route");
setText(10, "Pencil\nGet ready to share an answer ——> ", "Use your campus SSO.\nStay in your own account.");
setText(10, "Ball Toss\nFinish Successful Student Poster", "Open Profile.\nChoose Discover Your Core.\nKeep it open for your result.");
await replaceRouteImage(10);

setText(11, "Let’s write!", "Set up your Climber Profile");
setText(11, "Seat 1- Writer", "1. Open Profile.\n2. Check your name and grade.\n3. Choose an avatar or photo only if campus rules allow.");
setText(11, "Question\n\nOf the nine soft skills described in the article, which one does your table think is the most important for success in high school right now? Explain your reasoning.\n\nMinimum: 3 sentences", "Notice that the profile is mostly empty.\n\nAcross Core Days A, B, and C, it becomes a snapshot of you as a career explorer.\n\nToday begins with personality.");

setText(12, "Let’s write!", "Discover Your Core");
setText(12, "Seat 2- Speaker", "Profile → Discover Your Core\nRead slowly.\nAnswer honestly.");
setText(12, "Question\n\nOf the nine soft skills described in the article, which one does your table think is the most important for success in high school right now? Explain your reasoning.\n\nMinimum: 3 sentences", "When your result appears:\n\n1. Read the description.\n2. Choose one phrase that fits or surprises you.\n3. Open Core Personality — Day 2 in your private CCE notebook.");

setText(13, "Think", "Work honestly");
setText(13, "What are some behaviors that successful students do?\n", "There are no wrong answers and no better types.\n\nSlow down enough to understand each question. Ask for a read-aloud when you need it.\n\nIf H&L will not open, choose a provisional type from the class chart and label it provisional.");

setText(14, "Let’s write!", "Complete model");
setText(14, "Seat 1- Writer", "RESULT = my top type\nEVIDENCE = phrase from the description\nQUESTION = what I still wonder\nCAREER CONNECTION = one curiosity");
setText(14, "Question\n\nOf the nine soft skills described in the article, which one does your table think is the most important for success in high school right now? Explain your reasoning.\n\nMinimum: 3 sentences", "My result is Organizer. The phrase “likes clear systems” fits because I keep group projects on track. I wonder whether Organizers can also enjoy art. I am curious about event planning because it mixes systems with creative choices.");

setText(15, "Let’s write!", "Your private interpretation");
setText(15, "Seat 2- Speaker", "Result: My top type is ____.\nEvidence: One phrase that fits or surprises me is ____.\nQuestion: One real question I have is ____.");
setText(15, "Question\n\nOf the nine soft skills described in the article, which one does your table think is the most important for success in high school right now? Explain your reasoning.\n\nMinimum: 3 sentences", "Career connection: One career I am now curious about is ____ because ____.\n\nSave the page. Close or refresh. Reopen it.\n\nShow only that the page opens. Your private content stays private.");

setText(16, "Evaluate: Planner Set-Up", "Close: prediction vs. result");
setText(16, "From now until the next class, be sure to continue updating your planner.", "Compare your warm-up prediction with your result.\nWhat matched? What surprised you? What might explain the difference?\nTomorrow, you will connect your Core result to career clusters.");

const noteSets = [
  ["Timing: 0:00-0:30.", "Purpose: Hold this divider while students enter and open the Day 2 Canvas Student Guide.", "Monitor: Chromebooks out; no one begins in another student’s account.", "Pivot: If devices are not ready, keep the slide up and begin the oral materials check.", "Trim: Do not trim; this is a 30-second transition.", "Recovery: Canvas Student Guide remains the accessible/absence route.", "[Sources]", "- Jenna Hainlen, AVID Week 1.2 slide 25, day-divider layout.", "[/Sources]"],
  ["Timing: 0:30-1:00.", "Purpose: Preview the whole 50-minute arc before the prediction begins.", "Monitor: Students can name the three materials and the final private output.", "Pivot: If H&L login status is uncertain, quietly prepare the provisional six-type route.", "Trim: Read only the bold action words; do not explain each step yet.", "Recovery: Students who arrive late start from the Canvas Day 2 guide and join at the current slide.", "[Sources]", "- Jenna Hainlen, AVID Week 1.2 slide 26, Welcome/Get Ready/Today’s Lesson choreography.", "- CCE Day 2 canonical lesson, accessed 2026-08-15.", "- Authenticated H&L Discover Your Core screenshot.", "[/Sources]"],
  ["Timing: 1:00-4:00.", "Purpose: Capture a genuine prediction before instruction or the assessment changes it.", "Monitor: One word selected plus a short reason; no searching.", "Pivot: Read the six words aloud and point to each one for students who need language access.", "Trim: Accept the word only if time is tight.", "Recovery: A student may record the prediction on paper or in Canvas if the notebook is unavailable.", "[Sources]", "- CCE Day 2 warm-up.", "- Jenna Hainlen, AVID Week 1.2 slide 14, private Think routine.", "[/Sources]"],
  ["Timing: 4:00-5:00.", "Purpose: Preserve Jenna’s fast share choreography while making seated, standing, and private routes equal.", "Monitor: Students share the prediction and one clue or write privately; no debate about a “best” type.", "Pivot: Keep everyone seated if movement would cost time; private writing remains equal.", "Trim: One partner speaks instead of both.", "Recovery: Students may write one reason rather than disclose aloud.", "[Sources]", "- Jenna Hainlen, AVID Week 1.2 slide 15, stand-share-sit routine, minimally adapted for equal access.", "[/Sources]"],
  ["Timing: 5:00-9:00.", "Purpose: Frame CCE as the middle-school on-ramp to pathways without stealing time from the assessment.", "Monitor: Students can explain CCMR and Program of Study in plain language.", "Pivot: Point to FYF p. 21 and read only the two definitions if the class needs a concrete anchor.", "Trim: Ask the discussion question as a quick show of hands.", "Recovery: Absent students use FYF pp. 21-22 and answer the same question in the Canvas guide.", "[Sources]", "- Find Your Future pp. 21-22, What Is Happening at My District?", "- Jenna Hainlen, AVID Week 1.2 slide 22, paired writing frame.", "[/Sources]"],
  ["Timing: 9:00-10:00.", "Purpose: Teach the three H&L words students will hear all year.", "Monitor: Students point to themselves for Climber, name one Hat, and understand cluster as related careers.", "Pivot: Give one familiar cluster example only if needed; do not launch a career-cluster lesson.", "Trim: Read the three definitions and move on.", "Recovery: The same definitions remain in the Canvas Student Guide.", "[Sources]", "- CCE Day 2 H&L orientation.", "- Jenna Hainlen, AVID Week 1.2 slide 23, paired writing frame.", "[/Sources]"],
  ["Timing: 10:00-12:00.", "Purpose: Use the Climber Notes hook to make personality types feel relevant rather than diagnostic.", "Monitor: Students can name one activity that feels natural and one that feels effortful without labeling either as good or bad.", "Pivot: Offer school and out-of-school examples if the room is quiet.", "Trim: Read the first question and the final sentence only.", "Recovery: Students may think privately; no personal disclosure is required.", "[Sources]", "- Climber Notes: Learning Your Core Personality Types, slide 2.", "- Jenna Hainlen, AVID Week 1.2 slide 14, Think frame.", "[/Sources]"],
  ["Timing: 12:00-15:00.", "Purpose: Give students enough language to understand the app result without turning the six types into stereotypes.", "Monitor: Students hear all six types and understand that most people match more than one.", "Pivot: Pair the English terms with the prepared Spanish glossary when useful.", "Trim: Read only each type name and the first phrase.", "Recovery: Keep this slide available for the provisional route if H&L is down.", "[Sources]", "- Climber Notes: Learning Your Core Personality Types, slide 3.", "- Jenna Hainlen, AVID Week 1.2 slide 22, paired writing frame.", "[/Sources]"],
  ["Timing: 15:00-17:00.", "Purpose: Practice evidence-based matching before students see their own result.", "Monitor: Students give one clue and accept that multiple types may fit one career.", "Pivot: Model nurse as Helper plus Analyzer if students insist on one correct answer.", "Trim: Discuss one career only.", "Recovery: A private written answer counts equally.", "[Sources]", "- Climber Notes: Learning Your Core Personality Types, slide 5.", "- Jenna Hainlen, AVID Week 1.2 slide 23, paired writing frame.", "[/Sources]"],
  ["Timing: 17:00-20:00.", "Purpose: Make the exact authenticated app route visible before students click.", "Monitor: Every student is in their own account and can locate Profile.", "Pivot: If the district route differs, follow the teacher’s tested campus SSO path; do not improvise credentials.", "Trim: Project the screenshot and state only Profile → Discover Your Core.", "Recovery: If H&L is unavailable, switch to the six-type chart and mark results provisional; protect Friday catch-up.", "[Sources]", "- Authenticated private Canvas screenshot: Open the Hats & Ladders App / Discover Your Core.", "- Climber Notes: Learning Your Core Personality Types, slide 4.", "- Jenna Hainlen, AVID Week 1.2 slide 26, agenda/image frame.", "[/Sources]"],
  ["Timing: 20:00-27:00.", "Purpose: Establish the Climber Profile as the yearlong H&L home before the assessment begins.", "Monitor: Lap 1: each student has opened Profile and checked name/grade; avatar/photo follows campus policy.", "Pivot: Skip avatar/photo if it creates privacy, upload, or time problems.", "Trim: Check name/grade and move directly to Discover Your Core.", "Recovery: Record account issues; never use a peer’s account for a personal result.", "[Sources]", "- CCE Day 2 Climber Profile orientation.", "- Jenna Hainlen, AVID Week 1.2 slide 22, paired writing frame.", "[/Sources]"],
  ["Timing: 27:00-31:00, then students continue independently through 42:00.", "Purpose: Give the exact app-to-notebook sequence before work time.", "Monitor: Students read questions rather than rapid-clicking; results remain open until the description is read.", "Pivot: Read questions aloud or pair students with fluent readers before the teacher becomes the only support route.", "Trim: State the three numbered result steps and release students.", "Recovery: Use the provisional six-type route if H&L fails, then schedule the individual app activity for Friday.", "[Sources]", "- Climber Notes: Learning Your Core Personality Types, slides 3-4.", "- CCE Day 2 canonical app task.", "- Jenna Hainlen, AVID Week 1.2 slide 23, paired writing frame.", "[/Sources]"],
  ["Timing: 31:00-42:00 during app work.", "Purpose: Keep assessment conditions honest, readable, and nonjudgmental.", "Monitor: Lap 1 target is slow reading; stop and reset rapid click-through. Lap 2 target is a result description open on screen.", "Pivot: If one third of the class is stuck on language, pause for a whole-group read-aloud of one sample question.", "Trim: Do not trim the individual app runway; trim discussion instead.", "Recovery: Students without access choose a provisional type with one supporting phrase.", "[Sources]", "- CCE Day 2 active-monitoring and outage guidance.", "- Climber Notes: Learning Your Core Personality Types, slide 4.", "- Jenna Hainlen, AVID Week 1.2 slide 14, single-action prompt frame.", "[/Sources]"],
  ["Timing: 42:00-45:00.", "Purpose: Model one short H&L result interpretation before students write; this is not the full AVID focused-note-taking lesson.", "Monitor: Students can point to the result, evidence phrase, question, and career connection in the model.", "Pivot: Read the model sentence by sentence and label each prompt aloud.", "Trim: Read only the Organizer model once.", "Recovery: Students may dictate to speech-to-text or use the Canvas text route.", "[Sources]", "- CCE Day 2 complete H&L interpretation model.", "- Jenna Hainlen, AVID Week 1.2 slide 22, model/writing frame only.", "[/Sources]"],
  ["Timing: 45:00-49:00.", "Purpose: Capture the private interpretation the app and workbook do not already save without inventing a second packet or calling it AVID focused notes.", "Monitor: Lap 2 target is all four prompts; if one third writes only the type name, model choosing one meaningful phrase again.", "Pivot: Provide the four sentence stems or speech-to-text; students do not need to reveal private content.", "Trim: Require result + evidence phrase + career connection; carry the real question to the next class if needed.", "Recovery: Paper or Canvas response counts equally; label outage-based results provisional.", "[Sources]", "- CCE Day 2 private H&L interpretation and save check.", "- Jenna Hainlen, AVID Week 1.2 slide 23, writing frame only.", "[/Sources]"],
  ["Timing: 49:00-50:00.", "Purpose: Close the loop between prediction and result and preview Core Day B.", "Monitor: Students can reopen the page; they show only that it opens, not the private content.", "Pivot: Take one silent thumb signal for match/surprise if verbal discussion would expose personal results.", "Trim: Ask only: match or surprise?", "Recovery: The Canvas Student Guide preserves the comparison prompt for absent students.", "[Sources]", "- CCE Day 2 DOK 2 comparison and Day 3 bridge.", "- Jenna Hainlen, AVID Week 1.2 slide 50, evaluation/close frame; Jess Bailey photo attribution retained on-slide.", "[/Sources]"],
];
noteSets.forEach((notes, index) => setNotes(index + 1, notes));

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
