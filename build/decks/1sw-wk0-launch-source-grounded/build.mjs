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
const workspace = path.join(root, "tmp/cce-week1-source-clone");
const starterPath = path.join(workspace, "template-starter.pptx");
const outputPath = path.join(
  root,
  "cce-curriculum/resources/avid-reference/source/derived/cce-week1-day1-source-grounded.pptx",
);
const previewDir = path.join(workspace, "final-preview");
const layoutDir = path.join(workspace, "final-layout");
const goalImagePath = path.join(root, "tmp/cce-first-week-goal-render-20260815-v3/page-1.png");

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
  const record = records.find((item) => item.kind === kind && item.slide === slide && predicate(item));
  if (!record) throw new Error(`Missing ${kind} on output slide ${slide}`);
  return record;
}

function textbox(slide, text) {
  return presentation.resolve(recordFor("textbox", slide, (item) => item.text === text).id);
}

function setText(slide, before, after) {
  textbox(slide, before).text.set(after);
}

function setParagraphs(slide, before, paragraphs) {
  textbox(slide, before).text.set(paragraphs);
}

function setNotes(slide, lines) {
  const notes = presentation.resolve(recordFor("notes", slide).id);
  notes.setText(lines.join("\n"));
}

setText(1, "Week 1.2", "CCE Week 1");
setText(1, "AVID 2\nMs. Hainlen", "Career & College Explorations\nMr. Lucero");

setText(2, "Friday", "Monday");

setText(3, "Pencil\nGet out any school supplies you brought for this class\nGet ready to share an answer ——> ", "Chromebook\nFind Your Future workbook\nOpen Canvas: Day 1 Student Guide\nChoose partner-share or private response");
setParagraphs(3, "Set up Binders & Planners", [
  { runs: [{ run: "TEKS d(4)(A): ", textStyle: { bold: true, fontSize: "14pt" } }, { run: "Set up a notebook you can reopen and plan one action for this week.", textStyle: { fontSize: "14pt" } }] },
  { spaceBefore: 6, runs: [{ run: "Today: ", textStyle: { bold: true, fontSize: "14pt" } }, { run: "Find the guide and tools → set up the notebook → make a goal → save and reopen the page.", textStyle: { fontSize: "14pt" } }] },
]);
const agendaImage = presentation.resolve(recordFor("image", 3).id);
const agendaFrame = agendaImage.frame;
const agendaCrop = agendaImage.crop;
const agendaGeometry = agendaImage.geometry;
const agendaBorderRadius = agendaImage.borderRadius;
agendaImage.replace({
  blob: await fs.readFile(goalImagePath),
  contentType: "image/png",
  alt: "CCE first-week goal page used during today's lesson",
  fit: "contain",
});
agendaImage.frame = agendaFrame;
agendaImage.crop = agendaCrop;
agendaImage.fit = "contain";
agendaImage.geometry = agendaGeometry;
agendaImage.borderRadius = agendaBorderRadius;

setText(4, "Think", "Do Now");
setText(4, "What are some behaviors that successful students do?\n", "You are starting a new class. What is one thing a student can do to make the first week go well?\n\nSentence stem: A student can _____.");

setText(5, "stand-share-sit", "Share or stay private");
setText(5, "Everyone stand.\n\nShare with your partner: What are some behaviors that successful students do?\n\nOnce you share, sit down. \n", "Choose one route:\n\nShare one answer with a partner.\n\nOr keep your response private. Sitting or standing are both fine.");

setText(6, "Let’s Set Up your Binders!", "Choose Your CCE Notebook");
setParagraphs(6, "Get out your 3 ring binder & tabs OR your folders for class.\nYou need: \nYour first AND last name on the front of binder/folders. (I have sharpies you can borrow.)\nYour 8 tabs or folders labeled with each of your class names. (Example: Write “English” on the tab and not “1st period”)\nAll of your AVID papers 3-hole punched and in the AVID section.\nSecure all your papers in your binder. No papers should be loose.\nExtra Notebook paper (or spiral notebook) at the front.\nPencils & highlighters should be in a designated spot. (either in a pencil pouch or a specific pocket of your backpack)", [
  { runs: [{ run: "Choose the route that works today:", textStyle: { bold: true, fontSize: "21pt", color: "#172554" } }] },
  { bulletCharacter: "•", marginLeft: 22, indent: -12, runs: [{ run: "Digital: ", textStyle: { bold: true, fontSize: "18pt" } }, { run: "OneNote Class Notebook, if the tested class route opens", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "•", marginLeft: 22, indent: -12, runs: [{ run: "Physical: ", textStyle: { bold: true, fontSize: "18pt" } }, { run: "spiral, composition book, binder section, or class folder", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "•", marginLeft: 22, indent: -12, runs: [{ run: "Recovery: ", textStyle: { bold: true, fontSize: "18pt" } }, { run: "Canvas response or one paper page", textStyle: { fontSize: "18pt" } }] },
  { spaceBefore: 10, runs: [{ run: "No purchase, special brand, decoration, or recopying is required.", textStyle: { bold: true, fontSize: "18pt" } }] },
  { spaceBefore: 10, runs: [{ run: "Every route uses: ", textStyle: { bold: true, fontSize: "18pt" } }, { run: "CCE Work • Focused Notes • Evidence & Reflection", textStyle: { fontSize: "18pt" } }] },
]);
const notebookImage = presentation.resolve(recordFor("image", 6).id);
notebookImage.frame = { left: 748, top: 8, width: 190, height: 136 };

setText(7, "Get out your Planner!", "Set Up Your Digital or Physical Notebook");
setParagraphs(7, "You can use a physical planner. (I have extras!)\nOr you can use a digital planner you can access on your school computer.\nI suggest either Google calendar, Canvas’ calendar, or your iCloud calendar. ", [
  { bulletCharacter: "•", marginLeft: 22, indent: -12, runs: [{ run: "OneNote: ", textStyle: { bold: true, fontSize: "22pt" } }, { run: "open your private notebook; create or locate the same three sections.", textStyle: { fontSize: "22pt" } }] },
  { bulletCharacter: "•", marginLeft: 22, indent: -12, spaceBefore: 16, runs: [{ run: "Physical: ", textStyle: { bold: true, fontSize: "22pt" } }, { run: "label the same three sections in your spiral, binder section, or folder.", textStyle: { fontSize: "22pt" } }] },
  { bulletCharacter: "•", marginLeft: 22, indent: -12, spaceBefore: 16, runs: [{ run: "Today’s page: ", textStyle: { bold: true, fontSize: "22pt" } }, { run: "CCE Work → Notebook Setup + First-Week Goal", textStyle: { fontSize: "22pt" } }] },
]);

setText(8, "Evaluate: Planner Expectations", "How to Know Where to Work");
setParagraphs(8, "Academic Content\nYou must have something written down for every class every day.\nHomework/after school responsibilities\nIf no homework/after school responsibilities, a short note about what you did in class\nNote: even if you were absent, you need to have recorded something for each class. Make sure you ask what you missed!", [
  { runs: [{ run: "Follow today’s guide", textStyle: { bold: true, fontSize: "20pt" } }] },
  { bulletCharacter: "✓", marginLeft: 20, indent: -10, runs: [{ run: "Start in the Canvas Student Guide", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "✓", marginLeft: 20, indent: -10, runs: [{ run: "Open the activity named in the directions", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "✓", marginLeft: 20, indent: -10, runs: [{ run: "Use your notebook when the directions ask for it", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "✓", marginLeft: 20, indent: -10, runs: [{ run: "Turn in only the work named in the guide", textStyle: { bold: true, fontSize: "18pt" } }] },
]);
setParagraphs(8, "Organization\nLegible to you and your teacher\nPrevious tasks are checked or crossed off\nColors, highlights, or symbols are used if wanted", [
  { runs: [{ run: "Check before you move on", textStyle: { bold: true, fontSize: "20pt" } }] },
  { bulletCharacter: "✓", marginLeft: 20, indent: -10, runs: [{ run: "You can reopen today’s page", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "✓", marginLeft: 20, indent: -10, runs: [{ run: "Page title and date make sense to you", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "✓", marginLeft: 20, indent: -10, runs: [{ run: "You know where tomorrow’s directions live", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "✓", marginLeft: 20, indent: -10, runs: [{ run: "Digital and physical routes count equally", textStyle: { fontSize: "18pt" } }] },
]);

setText(9, "Skills Check", "First-Week Goal");
setText(9, "Each week, we will check in on our grades, planners, and goals. I want you to pick a goal for THIS week. Something small but meaningful!\n\nHere are some ideas (but you can create your own!)\n☐ Turn in all assignments on time\n☐ Bring my supplies to every class\n☐ Write down homework every day\n☐ Participate at least once in each class\n☐ Ask questions when I need help\n☐ Study or review notes for at least 15 minutes each night\n☐ Keep my binder or folders organized\n☐ Check my grades this week\n☐ Get to class on time every day\n☐ Limit distractions during class", "Choose one small CCE goal for this week. Make it meaningful and realistic.\n\nYour goal page follows a teacher-built first-week sequence:\n✓ Goal\n✓ Why it matters\n✓ One specific action\n✓ When or checkpoint\n✓ Confidence 1–5\n✓ Support or recovery route\n\nA course-only or fictional goal is always allowed.");
const goalImage = presentation.resolve(recordFor("image", 9).id);
const oldFrame = goalImage.frame;
const oldCrop = goalImage.crop;
const oldFit = goalImage.fit;
const oldGeometry = goalImage.geometry;
const oldBorderRadius = goalImage.borderRadius;
goalImage.replace({
  blob: await fs.readFile(goalImagePath),
  contentType: "image/png",
  alt: "CCE First Week Goal-Setting sheet with goal, reason, action, checkpoint, confidence, and support fields",
  fit: "contain",
});
goalImage.frame = oldFrame;
goalImage.crop = oldCrop;
goalImage.fit = oldFit ?? "contain";
goalImage.geometry = oldGeometry;
goalImage.borderRadius = oldBorderRadius;

setText(10, "Think", "Make it small and specific");
setText(10, "What are some behaviors that successful students do?\n", "Choose one goal you can complete by Friday.\n\nExamples: read every H&L question carefully • ask when a word or direction is unclear • reopen today’s goal page without a new link • choose another goal for this class");

setText(11, "Let’s write!", "Complete model");
setText(11, "Seat 1- Writer", "Goal → action → checkpoint");
setParagraphs(11, "Question\n\nOf the nine soft skills described in the article, which one does your table think is the most important for success in high school right now? Explain your reasoning.\n\nMinimum: 3 sentences", [
  { runs: [{ run: "Goal: ", textStyle: { bold: true, fontSize: "17pt" } }, { run: "Complete Discover Your Core carefully by Friday.", textStyle: { fontSize: "17pt" } }] },
  { spaceBefore: 7, runs: [{ run: "Why: ", textStyle: { bold: true, fontSize: "17pt" } }, { run: "I want the result to be based on my real answers.", textStyle: { fontSize: "17pt" } }] },
  { spaceBefore: 7, runs: [{ run: "Action: ", textStyle: { bold: true, fontSize: "17pt" } }, { run: "Read every question; ask if a word is unclear.", textStyle: { fontSize: "17pt" } }] },
  { spaceBefore: 7, runs: [{ run: "Checkpoint: ", textStyle: { bold: true, fontSize: "17pt" } }, { run: "Tuesday H&L block.", textStyle: { fontSize: "17pt" } }] },
  { spaceBefore: 7, runs: [{ run: "Confidence: ", textStyle: { bold: true, fontSize: "17pt" } }, { run: "4", textStyle: { fontSize: "17pt" } }] },
  { spaceBefore: 7, runs: [{ run: "Support: ", textStyle: { bold: true, fontSize: "17pt" } }, { run: "teacher check-in + fallback route", textStyle: { fontSize: "17pt" } }] },
]);

setText(12, "Let’s write!", "Your turn");
setText(12, "Seat 2- Speaker", "Open today’s goal page");
setText(12, "Question\n\nOf the nine soft skills described in the article, which one does your table think is the most important for success in high school right now? Explain your reasoning.\n\nMinimum: 3 sentences", "Complete all six fields:\n\n1. My first-week CCE goal\n2. Why this goal matters to me\n3. One specific action I will take\n4. When or which class checkpoint\n5. Confidence right now: 1 2 3 4 5\n6. What will help: calendar/planner • teacher check-in • classmate • reminder/alarm • fallback route");

setText(13, "stand-share-sit", "partner or private check");
setParagraphs(13, "Everyone stand.\n\nShare with your partner: What are some behaviors that successful students do?\n\nOnce you share, sit down. \n", [
  { runs: [{ run: "Share only your action and checkpoint with a partner—or stay private and self-check:", textStyle: { fontSize: "21pt" } }] },
  { bulletCharacter: "•", marginLeft: 22, indent: -12, spaceBefore: 12, runs: [{ run: "Can someone see what I will do?", textStyle: { bold: true, fontSize: "22pt" } }] },
  { bulletCharacter: "•", marginLeft: 22, indent: -12, runs: [{ run: "Did I name when I will do it?", textStyle: { bold: true, fontSize: "22pt" } }] },
  { bulletCharacter: "•", marginLeft: 22, indent: -12, runs: [{ run: "Did I choose a support or recovery route?", textStyle: { bold: true, fontSize: "22pt" } }] },
  { spaceBefore: 14, runs: [{ run: "You never have to share the goal or why it matters.", textStyle: { fontSize: "18pt" } }] },
]);

setText(14, "Think", "Save + reopen test");
setText(14, "What are some behaviors that successful students do?\n", "Type or write: “The place I will use for CCE work is ____. If it does not open, I will use ____.”\n\nClose or refresh. Reopen the page. If it fails, use Canvas or paper today—no recopying later.");

setText(15, "Evaluate: Planner Set-Up", "Close: Find it again tomorrow");
setParagraphs(15, "From now until the next class, be sure to continue updating your planner.", [
  { bulletCharacter: "•", marginLeft: 22, indent: -12, runs: [{ run: "Point to today’s goal entry. Then point to where tomorrow’s directions will be.", textStyle: { fontSize: "20pt" } }] },
  { bulletCharacter: "•", marginLeft: 22, indent: -12, spaceBefore: 18, runs: [{ run: "Tomorrow: ", textStyle: { bold: true, fontSize: "20pt" } }, { run: "Hats & Ladders begins building your Climber Profile. The notebook holds only the short thinking the app and workbook do not already save.", textStyle: { fontSize: "20pt" } }] },
]);

function noteBlock({ timing, move, action, lookFor, pivot, recovery, sources }) {
  return [
    `Timing: ${timing}`,
    `Teacher move: ${move}`,
    `Student action: ${action}`,
    `Look-for: ${lookFor}`,
    `Pivot/trim: ${pivot}`,
    `Recovery/access: ${recovery}`,
    "[Sources]",
    ...sources.map((source) => `- ${source}`),
    "[/Sources]",
  ];
}

const noteSets = [
  noteBlock({
    timing: "Before students arrive.",
    move: "Open Canvas Day 1, test the OneNote route, and keep the complete Canvas/paper route ready. Do not distribute the retired routine card or Evidence Log.",
    action: "No student action; this is the teacher preflight frame.",
    lookFor: "Canvas Student Guide opens, the chosen notebook route is usable, and the goal page or paper copy is ready.",
    pivot: "If OneNote is untested, announce Canvas/paper as today's route before students enter; do not spend class installing or repairing it.",
    recovery: "Keep the same six goal fields in Canvas or on paper so students never have to recopy later.",
    sources: ["Jenna Hainlen, AVID Week 1.2 slide 1, cover layout and visual language.", "CCE Day 1 canonical lesson, accessed 2026-08-15."],
  }),
  noteBlock({
    timing: "0:00-0:30.",
    move: "Leave the divider up while students enter, then advance promptly.",
    action: "Enter, sit in the accessible location that works, and open the Chromebook.",
    lookFor: "Students are entering rather than copying the projected title.",
    pivot: "Advance as soon as most students are seated; do not narrate the decorative frame.",
    recovery: "Skip this divider after a late transition; no learning evidence is attached to it.",
    sources: ["Jenna Hainlen, AVID Week 1.2 slide 42, day-divider layout."],
  }),
  noteBlock({
    timing: "0:30-5:00.",
    move: "Review the TEKS-linked objective and agenda: find today’s directions and tools, set up and test the notebook, make one first-week goal, then save and reopen the page.",
    action: "Open the Canvas Day 1 Student Guide and prepare the Chromebook and FYF workbook.",
    lookFor: "By minute 5, at least 80% have the Student Guide open and can name the next step on the agenda.",
    pivot: "If fewer than 80% can locate the guide, model the route once from the student view and have students mirror it.",
    recovery: "Use the projected map and paper/FYF materials if a login fails; record the account issue for later.",
    sources: ["Jenna Hainlen, AVID Week 1.2 slide 43, Welcome/Get Ready/Today's Lesson choreography.", "CCE Day 1, Welcome to CCE."],
  }),
  noteBlock({
    timing: "5:00-7:00.",
    move: "Preserve the source slide’s silent Think routine. Ask what one thing a student can do to make the first week in a new class go well.",
    action: "Think of one concrete action. Use the stem ‘A student can _____.’ if helpful.",
    lookFor: "Students name an action such as ask a question, read the directions, try the activity, or ask for help.",
    pivot: "If students stall, reread the stem and accept a one-word action before moving to partner or private response.",
    recovery: "Accept pointing, dictation, AAC, or an oral response to the teacher instead of writing.",
    sources: ["Jenna Hainlen, AVID Week 1.2 slide 14, private Think routine."],
  }),
  noteBlock({
    timing: "7:00-9:00.",
    move: "Preserve Jenna’s partner-share rhythm while keeping seated and private participation equal.",
    action: "Share one first-week action with a partner or keep the response private.",
    lookFor: "Every student chooses a route; no one is waiting for permission to remain seated or private.",
    pivot: "If movement is distracting or inaccessible, keep the entire class seated and use partner or private responses.",
    recovery: "Accept a teacher check, written response, or AAC response; never require public disclosure.",
    sources: ["Jenna Hainlen, AVID Week 1.2 slide 15, stand-share-sit rhythm, minimally adapted for equal access."],
  }),
  noteBlock({
    timing: "9:00-13:00.",
    move: "Name OneNote as the pilot default only when the tested route opens; present physical and Canvas routes as equivalent.",
    action: "Choose the working route and identify where CCE Work, Focused Notes, and Evidence & Reflection will live.",
    lookFor: "Every student can name a usable route without being asked to buy, decorate, or recopy a notebook.",
    pivot: "If one third of the class cannot open OneNote, move the whole class to Canvas/paper for today.",
    recovery: "Record access problems and preserve the completed page in the fallback route; migrate later only if the student chooses.",
    sources: ["Jenna Hainlen, AVID Week 1.2 slide 46, route-setup structure.", "Microsoft Support, Class Notebook organization and page distribution, accessed 2026-08-14."],
  }),
  noteBlock({
    timing: "13:00-20:00.",
    move: "Model the digital and physical routes while students create or locate the same three sections.",
    action: "Create or locate the sections and open CCE Work -> Notebook Setup + First-Week Goal.",
    lookFor: "By minute 20, at least 80% have a retrievable private page or a named physical/Canvas location.",
    pivot: "If one third is blocked, stop individual troubleshooting and demonstrate the complete fallback path to everyone.",
    recovery: "Students use Canvas or one paper page today; account repair happens after class, not during the learning block.",
    sources: ["Jenna Hainlen, AVID Week 1.2 slide 47, physical/digital tool choice structure.", "CCE Day 1 OneNote pilot and equal physical route."],
  }),
  noteBlock({
    timing: "20:00-25:00.",
    move: "Teach only locate-and-use expectations. State that notebook type, neatness, tabs, decoration, and handwriting are not graded.",
    action: "Identify one response home and show how today's page can be reopened.",
    lookFor: "Students can explain where today's directions live and where their one response will stay.",
    pivot: "If attention drops, ask two checks only: 'Where do directions live?' and 'Where does this response live?'",
    recovery: "Use a labeled paper folder or Canvas page when the preferred notebook route is not working.",
    sources: ["Jenna Hainlen, AVID Week 1.2 slide 48, expectations comparison layout.", "CCE owner decision: notebook is a workspace, not a compliance system."],
  }),
  noteBlock({
    timing: "25:00-27:00.",
    move: "Open or distribute the source-derived goal page and state that it is private practice, not a second Canvas submission.",
    action: "Open the six-field goal page in the chosen route.",
    lookFor: "Every student has the same six response fields visible by minute 27.",
    pivot: "If page distribution fails, use the identical fields printed in the Student Guide or the one-page paper copy.",
    recovery: "Allow a course-only or fictional goal and a paper, dictation, or speech-to-text response.",
    sources: ["Jenna Hainlen, AVID 26-27 Skills Check, First Week Goal-Setting Sheet.", "Jenna Hainlen, AVID Week 1.2 slide 13, Skills Check framing.", "CCE First Week Goal-Setting Sheet, minimally adapted 2026-08-15."],
  }),
  noteBlock({
    timing: "27:00-30:00.",
    move: "Think aloud while shrinking one vague intention into a specific action and checkpoint. Read the concrete first-week choices before students select or adapt one.",
    action: "Choose one goal for this class that can be completed by Friday.",
    lookFor: "Students name an observable action rather than a wish such as 'do better.'",
    pivot: "If many goals remain vague, revise one anonymous example with the class before students write independently.",
    recovery: "Offer the three projected examples and permit a fictional course goal without personal disclosure.",
    sources: ["Jenna Hainlen, AVID Week 1.2 slide 14, Think structure.", "Jenna Hainlen, AVID Week 1.3 time-management goal revision sequence."],
  }),
  noteBlock({
    timing: "30:00-33:00.",
    move: "Read the complete model once and ask what makes it observable and scheduled.",
    action: "Identify the model's action, checkpoint, and fallback support.",
    lookFor: "Students can point to the exact action and when it will happen.",
    pivot: "If students name the goal instead of the evidence, highlight only Action, Checkpoint, and Support.",
    recovery: "Read the model aloud and allow students to follow by listening rather than copying it.",
    sources: ["CCE Day 1 complete model.", "Jenna Hainlen, AVID Week 1.2 slide 22, model/writing frame."],
  }),
  noteBlock({
    timing: "33:00-42:00.",
    move: "Release students to complete all six fields; circulate in three laps for route, action/checkpoint, and support.",
    action: "Complete goal, why, one action, checkpoint, confidence 1-5, and support/recovery.",
    lookFor: "By minute 38, every response has an action and checkpoint; by minute 42, all six fields are complete or the student is using an accommodation.",
    pivot: "If one third is still vague at minute 38, pause for one anonymous model revision, then restart work.",
    recovery: "Use speech-to-text, dictation, AAC, a scribe, or the paper/Canvas page; do not require personal grades or circumstances.",
    sources: ["Jenna Hainlen, AVID First Week Goal-Setting Sheet, preserved field sequence.", "Jenna Hainlen, AVID Week 1.2 slide 23, writing frame."],
  }),
  noteBlock({
    timing: "42:00-47:00.",
    move: "Run the partner-or-private self-check without collecting the private goal or reason.",
    action: "Share only action and checkpoint, or privately check action, time, and support.",
    lookFor: "Every student confirms an observable action, a real checkpoint, and one support/recovery route.",
    pivot: "If sharing is slow, move everyone to the three-question private check.",
    recovery: "Teacher conference, writing, or AAC counts equally; no public sharing is required.",
    sources: ["Jenna Hainlen, AVID Week 1.2 slide 15, share/check rhythm.", "CCE Day 1 partner or private check."],
  }),
  noteBlock({
    timing: "47:00-49:00.",
    move: "Require the save-and-reopen proof before celebrating completion.",
    action: "Close or refresh, reopen the same page, and name the fallback route.",
    lookFor: "Every student can reopen the page or point to the exact labeled paper/Canvas location.",
    pivot: "If one third cannot reopen, stop troubleshooting and direct those students to the complete Canvas/paper route.",
    recovery: "Keep completed work in the fallback route and repair OneNote later; never require recopying.",
    sources: ["CCE Day 1 save/reopen recovery requirement.", "Jenna Hainlen, AVID Week 1.2 slide 14, single-action prompt structure."],
  }),
  noteBlock({
    timing: "49:00-50:00.",
    move: "Protect the close: point to today's entry and tomorrow's Canvas Student Guide.",
    action: "Point to the saved goal and the place where Tuesday's directions will appear.",
    lookFor: "Students can name what they will open first tomorrow without exposing their private goal.",
    pivot: "Use a whole-class point-and-name check if the partner/private block ran long.",
    recovery: "Give absent or unfinished students the exact Day 1 Student Guide location for catch-up; do not add a new submission.",
    sources: ["Jenna Hainlen, AVID Week 1.2 slide 50, evaluation/close layout; Jess Bailey photo attribution retained on-slide.", "CCE Day 1 close and Tuesday H&L bridge."],
  }),
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
  await fs.writeFile(path.join(previewDir, `final-slide-${number}.png`), Buffer.from(await png.arrayBuffer()));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(layoutDir, `final-slide-${number}.layout.json`), await layout.text());
}

const montage = await presentation.export({ format: "png", montage: true, scale: 1 });
await fs.writeFile(path.join(workspace, "final-montage.png"), Buffer.from(await montage.arrayBuffer()));
const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(outputPath);
console.log(JSON.stringify({ outputPath, slideCount: presentation.slides.items.length, previewDir }, null, 2));
