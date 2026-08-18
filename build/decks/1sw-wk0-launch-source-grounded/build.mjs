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
setText(1, "AVID 2\nMs. Hainlen", "Career & College Explorations\nMs. Lucero");

setText(2, "Friday", "Monday");

setText(3, "Pencil\nGet out any school supplies you brought for this class\nGet ready to share an answer ——> ", "Wait for the assigned-device cue\nOpen Canvas: Day 1 Student Guide\nChoose partner-share or private response");
setParagraphs(3, "Set up Binders & Planners", [
  { runs: [{ run: "TEKS d(4)(A), introduced: ", textStyle: { bold: true, fontSize: "14pt" } }, { run: "Open your CCE workspace and begin one goal sentence.", textStyle: { fontSize: "14pt" } }] },
  { spaceBefore: 6, runs: [{ run: "Today: ", textStyle: { bold: true, fontSize: "14pt" } }, { run: "Learn the device routine → open OneNote → begin a first-week goal.", textStyle: { fontSize: "14pt" } }] },
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

setText(6, "Let’s Set Up your Binders!", "Check Out Your Device");
setParagraphs(6, "Get out your 3 ring binder & tabs OR your folders for class.\nYou need: \nYour first AND last name on the front of binder/folders. (I have sharpies you can borrow.)\nYour 8 tabs or folders labeled with each of your class names. (Example: Write “English” on the tab and not “1st period”)\nAll of your AVID papers 3-hole punched and in the AVID section.\nSecure all your papers in your binder. No papers should be loose.\nExtra Notebook paper (or spiral notebook) at the front.\nPencils & highlighters should be in a designated spot. (either in a pencil pouch or a specific pocket of your backpack)", [
  { runs: [{ run: "Use only the Chromebook assigned to you.", textStyle: { bold: true, fontSize: "21pt", color: "#172554" } }] },
  { bulletCharacter: "1", marginLeft: 28, indent: -14, runs: [{ run: "Find the device number Ms. Lucero names.", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "2", marginLeft: 28, indent: -14, runs: [{ run: "Check the device and charger before moving.", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "3", marginLeft: 28, indent: -14, runs: [{ run: "Carry it with two hands and place it flat on the desk.", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "4", marginLeft: 28, indent: -14, runs: [{ run: "Report a missing, damaged, or uncharged device before signing in.", textStyle: { fontSize: "18pt" } }] },
  { spaceBefore: 10, runs: [{ run: "DONE WHEN: ", textStyle: { bold: true, fontSize: "18pt" } }, { run: "your assigned device and charger are at your seat.", textStyle: { fontSize: "18pt" } }] },
]);
const notebookImage = presentation.resolve(recordFor("image", 6).id);
notebookImage.frame = { left: 748, top: 8, width: 190, height: 136 };

setText(7, "Get out your Planner!", "Practice the Return Routine");
setParagraphs(7, "You can use a physical planner. (I have extras!)\nOr you can use a digital planner you can access on your school computer.\nI suggest either Google calendar, Canvas’ calendar, or your iCloud calendar. ", [
  { bulletCharacter: "1", marginLeft: 28, indent: -14, runs: [{ run: "Close the Chromebook when Ms. Lucero gives the cue.", textStyle: { fontSize: "22pt" } }] },
  { bulletCharacter: "2", marginLeft: 28, indent: -14, spaceBefore: 14, runs: [{ run: "Carry the device and charger to the assigned slot.", textStyle: { fontSize: "22pt" } }] },
  { bulletCharacter: "3", marginLeft: 28, indent: -14, spaceBefore: 14, runs: [{ run: "Connect the charger exactly as shown.", textStyle: { fontSize: "22pt" } }] },
  { spaceBefore: 14, runs: [{ run: "DONE WHEN: ", textStyle: { bold: true, fontSize: "22pt" } }, { run: "device, slot, and charger are checked.", textStyle: { fontSize: "22pt" } }] },
]);

setText(8, "Evaluate: Planner Expectations", "Open Your CCE Notebook");
setParagraphs(8, "Academic Content\nYou must have something written down for every class every day.\nHomework/after school responsibilities\nIf no homework/after school responsibilities, a short note about what you did in class\nNote: even if you were absent, you need to have recorded something for each class. Make sure you ask what you missed!", [
  { runs: [{ run: "WHAT YOU SEE", textStyle: { bold: true, fontSize: "20pt" } }] },
  { bulletCharacter: "✓", marginLeft: 20, indent: -10, runs: [{ run: "Your private OneNote Class Notebook", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "✓", marginLeft: 20, indent: -10, runs: [{ run: "CCE Work, Focused Notes, and Evidence & Reflection", textStyle: { fontSize: "18pt" } }] },
  { runs: [{ run: "DO THIS", textStyle: { bold: true, fontSize: "20pt" } }] },
  { bulletCharacter: "1", marginLeft: 26, indent: -12, runs: [{ run: "Open CCE Work.", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "2", marginLeft: 26, indent: -12, runs: [{ run: "Open Notebook Setup + First-Week Goal.", textStyle: { fontSize: "18pt" } }] },
]);
setParagraphs(8, "Organization\nLegible to you and your teacher\nPrevious tasks are checked or crossed off\nColors, highlights, or symbols are used if wanted", [
  { runs: [{ run: "DONE WHEN", textStyle: { bold: true, fontSize: "20pt" } }] },
  { bulletCharacter: "✓", marginLeft: 20, indent: -10, runs: [{ run: "Today’s goal page is open", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "✓", marginLeft: 20, indent: -10, runs: [{ run: "You can point to the first goal field", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "✓", marginLeft: 20, indent: -10, runs: [{ run: "Digital and physical routes count equally", textStyle: { fontSize: "18pt" } }] },
]);

setText(9, "Skills Check", "Find the Goal Field");
setText(9, "Each week, we will check in on our grades, planners, and goals. I want you to pick a goal for THIS week. Something small but meaningful!\n\nHere are some ideas (but you can create your own!)\n☐ Turn in all assignments on time\n☐ Bring my supplies to every class\n☐ Write down homework every day\n☐ Participate at least once in each class\n☐ Ask questions when I need help\n☐ Study or review notes for at least 15 minutes each night\n☐ Keep my binder or folders organized\n☐ Check my grades this week\n☐ Get to class on time every day\n☐ Limit distractions during class", "WHAT YOU SEE\nThe First-Week Goal page with six fields.\n\nDO THIS\nOpen the page in CCE Work. Point to the first field: My first-week CCE goal.\n\nDONE WHEN\nThe page is open and you can point to the first goal field. Do not complete the rest yet.");
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

setText(10, "Think", "Choose One Goal for Friday");
setText(10, "What are some behaviors that successful students do?\n", "DO THIS: Finish only the first sentence today.\n\nMy first-week CCE goal: By Friday, I will _____.\n\nDONE WHEN: your sentence names one clear CCE action.\n\nTuesday continues on this same page.");

setText(11, "Let’s write!", "Model Goal Sentence");
setText(11, "Seat 1- Writer", "One sentence only");
setParagraphs(11, "Question\n\nOf the nine soft skills described in the article, which one does your table think is the most important for success in high school right now? Explain your reasoning.\n\nMinimum: 3 sentences", [
  { runs: [{ run: "MODEL", textStyle: { bold: true, fontSize: "19pt" } }] },
  { spaceBefore: 12, runs: [{ run: "By Friday, I will complete Discover Your Core carefully.", textStyle: { bold: true, fontSize: "22pt" } }] },
  { spaceBefore: 16, runs: [{ run: "WHY IT WORKS", textStyle: { bold: true, fontSize: "18pt" } }] },
  { bulletCharacter: "✓", marginLeft: 22, indent: -12, runs: [{ run: "It names one CCE task.", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "✓", marginLeft: 22, indent: -12, runs: [{ run: "It has a Friday stopping point.", textStyle: { fontSize: "18pt" } }] },
]);

setText(12, "Let’s write!", "Write Your Goal Sentence");
setText(12, "Seat 2- Speaker", "Stay on the same page");
setText(12, "Question\n\nOf the nine soft skills described in the article, which one does your table think is the most important for success in high school right now? Explain your reasoning.\n\nMinimum: 3 sentences", "Finish this sentence:\n\nBy Friday, I will ________________________________.\n\nA course-only or fictional goal is okay.\n\nStop after this first field. Do not rush the rest.");

setText(13, "stand-share-sit", "Mark Your Stopping Point");
setParagraphs(13, "Everyone stand.\n\nShare with your partner: What are some behaviors that successful students do?\n\nOnce you share, sit down. \n", [
  { runs: [{ run: "Point to the last field you reached.", textStyle: { bold: true, fontSize: "22pt" } }] },
  { spaceBefore: 14, runs: [{ run: "Tell Ms. Lucero one status:", textStyle: { fontSize: "21pt" } }] },
  { bulletCharacter: "•", marginLeft: 22, indent: -12, runs: [{ run: "Goal sentence started", textStyle: { bold: true, fontSize: "22pt" } }] },
  { bulletCharacter: "•", marginLeft: 22, indent: -12, runs: [{ run: "Page or access blocked", textStyle: { bold: true, fontSize: "22pt" } }] },
  { spaceBefore: 14, runs: [{ run: "Tuesday resumes this same page. No second goal page.", textStyle: { fontSize: "18pt" } }] },
]);

setText(14, "Think", "DOL: Show What Is Ready");
setText(14, "What are some behaviors that successful students do?\n", "SHOW: your notebook page is open and your goal sentence is started.\n\nSAY: goal started • page/access blocked • or device issue.\n\nDONE WHEN: Ms. Lucero records your exact Tuesday starting point.");

setText(15, "Evaluate: Planner Set-Up", "Close: Return devices correctly");
setParagraphs(15, "From now until the next class, be sure to continue updating your planner.", [
  { bulletCharacter: "•", marginLeft: 22, indent: -12, runs: [{ run: "Leave the goal page at your stopping point and follow the class device-return routine.", textStyle: { fontSize: "20pt" } }] },
  { bulletCharacter: "•", marginLeft: 22, indent: -12, spaceBefore: 18, runs: [{ run: "Tomorrow: ", textStyle: { bold: true, fontSize: "20pt" } }, { run: "finish the missing goal fields on this same page, then begin Hats & Ladders.", textStyle: { fontSize: "20pt" } }] },
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
    move: "Confirm assigned-device numbers, slots, chargers, and the problem-report route. Test the OneNote page for distribution and editability; keep Canvas/paper ready.",
    action: "No student action; this is the teacher preflight frame.",
    lookFor: "Every device has one known home, and the exact goal page accepts typing before students arrive.",
    pivot: "If OneNote is untested, use Canvas/paper from the start. Do not make students prove autosave.",
    recovery: "Keep the same goal page fields in the fallback so Tuesday resumes without recopying.",
    sources: ["Jenna Hainlen, AVID Week 1.2 slide 1, cover layout and visual language.", "CCE Day 1 live pacing revision, 2026-08-17."],
  }),
  noteBlock({
    timing: "0:00-0:30.",
    move: "Leave the divider up while students enter, then advance promptly.",
    action: "Enter, sit in the accessible location that works, and wait for the device cue.",
    lookFor: "Students are entering rather than copying the projected title.",
    pivot: "Advance as soon as most students are seated; do not narrate the decorative frame.",
    recovery: "Skip this divider after a late transition; no learning evidence is attached to it.",
    sources: ["Jenna Hainlen, AVID Week 1.2 slide 42, day-divider layout."],
  }),
  noteBlock({
    timing: "0:30-5:00.",
    move: "Preview the three jobs: assigned-device routine, OneNote navigation, and one goal sentence.",
    action: "Listen for the device cue and identify the first agenda action.",
    lookFor: "Students can name device first, notebook second, goal sentence third.",
    pivot: "Point to each agenda arrow; save platform explanations for the matching slide.",
    recovery: "The physical/Canvas notebook route remains equal when OneNote access is blocked.",
    sources: ["Jenna Hainlen, AVID Week 1.2 slide 43, Welcome/Get Ready/Today's Lesson choreography.", "CCE Day 1 live pacing revision, 2026-08-17."],
  }),
  noteBlock({
    timing: "1:00-3:00.",
    move: "Preserve the source slide’s silent Think routine. Ask what one thing a student can do to make the first week in a new class go well.",
    action: "Think of one concrete action. Use the stem ‘A student can _____.’ if helpful.",
    lookFor: "Students name an action such as ask a question, read the directions, try the activity, or ask for help.",
    pivot: "If students stall, reread the stem and accept a one-word action before moving to partner or private response.",
    recovery: "Accept pointing, dictation, AAC, or an oral response to the teacher instead of writing.",
    sources: ["Jenna Hainlen, AVID Week 1.2 slide 14, private Think routine."],
  }),
  noteBlock({
    timing: "3:00-5:00.",
    move: "Preserve Jenna’s partner-share rhythm while keeping seated and private participation equal.",
    action: "Share one first-week action with a partner or keep the response private.",
    lookFor: "Every student chooses a route; no one is waiting for permission to remain seated or private.",
    pivot: "If movement is distracting or inaccessible, keep the entire class seated and use partner or private responses.",
    recovery: "Accept a teacher check, written response, or AAC response; never require public disclosure.",
    sources: ["Jenna Hainlen, AVID Week 1.2 slide 15, stand-share-sit rhythm, minimally adapted for equal access."],
  }),
  noteBlock({
    timing: "5:00-12:00.",
    move: "Teach the assigned-device check-out sequence exactly as the room uses it.",
    action: "Locate the assigned device and charger, check condition, carry with two hands, and place it flat.",
    lookFor: "Students use their assigned numbers and report a problem before signing in.",
    pivot: "Repeat the physical sequence if one third is moving toward unassigned devices.",
    recovery: "Issue a spare only through the teacher's problem-report route; never borrow another student's device.",
    sources: ["CCE Day 1 observed device-management sequence, 2026-08-17.", "Jenna Hainlen, AVID Week 1.2 slide 46, procedure-launch structure."],
  }),
  noteBlock({
    timing: "12:00-20:00.",
    move: "Demonstrate the exact return cue, assigned slot, charger connection, and final teacher check.",
    action: "Practice the return sequence once, then bring the same device back to the seat for OneNote.",
    lookFor: "Device number, slot, and charger stay matched; students wait for the final check.",
    pivot: "Slow the physical practice if chargers or slots are mismatched. Protect the final return later.",
    recovery: "Record damaged or missing equipment; the device issue does not become a student discipline shortcut.",
    sources: ["CCE Day 1 observed device-management sequence, 2026-08-17.", "Jenna Hainlen, AVID Week 1.2 slide 47, step-by-step procedure structure."],
  }),
  noteBlock({
    timing: "20:00-28:00.",
    move: "Introduce OneNote as the default route and the physical/Canvas route as equal. Name the three private sections.",
    action: "Open the private notebook and locate CCE Work, Focused Notes, and Evidence & Reflection.",
    lookFor: "Students are in their own private notebook, not Collaboration Space or another student's page.",
    pivot: "If one third cannot open OneNote, move blocked students to the complete fallback without stopping the room.",
    recovery: "Keep completed work in the fallback; no later recopying.",
    sources: ["Microsoft Support, Class Notebook organization and page distribution, accessed 2026-08-17.", "CCE owner decision: notebook is a workspace, not a compliance system."],
  }),
  noteBlock({
    timing: "28:00-34:00.",
    move: "Open or distribute Notebook Setup + First-Week Goal and point to the page title and first field.",
    action: "Open the exact page in CCE Work or the equal fallback.",
    lookFor: "Every student has the same response page visible by minute 34.",
    pivot: "If page distribution fails, use the identical fields printed in the Student Guide or the one-page paper copy.",
    recovery: "Allow a course-only or fictional goal and a paper, dictation, or speech-to-text response.",
    sources: ["Jenna Hainlen, AVID 26-27 Skills Check, First Week Goal-Setting Sheet.", "Jenna Hainlen, AVID Week 1.2 slide 13, Skills Check framing.", "CCE First Week Goal-Setting Sheet, minimally adapted 2026-08-15."],
  }),
  noteBlock({
    timing: "34:00-40:00.",
    move: "Show the first goal field and state the stopping boundary: one sentence today, remaining fields Tuesday.",
    action: "Read the stem and choose one possible CCE goal for Friday.",
    lookFor: "Students can point to the first field and know they are not finishing the whole page Monday.",
    pivot: "Offer the projected example if students are still searching for a goal at minute 38.",
    recovery: "A course-only or fictional goal and oral rehearsal are allowed.",
    sources: ["Jenna Hainlen, AVID Week 1.2 slide 14, Think structure.", "CCE Day 1 live pacing boundary, 2026-08-17."],
  }),
  noteBlock({
    timing: "40:00-42:00.",
    move: "Read the one-sentence model and identify the named task and Friday boundary.",
    action: "Listen for what makes the goal specific enough to start.",
    lookFor: "Students can name the CCE task in the model.",
    pivot: "Highlight only the task and Friday phrase; save action/checkpoint instruction for Tuesday.",
    recovery: "Read the model aloud and permit students to adapt it.",
    sources: ["CCE Day 1 one-sentence model.", "Jenna Hainlen, AVID Week 1.2 slide 22, model/writing frame."],
  }),
  noteBlock({
    timing: "42:00-47:00.",
    move: "Release students to write only the first goal sentence. Circulate for page access and a specific CCE task.",
    action: "Finish: By Friday, I will _____. Stop after the first field.",
    lookFor: "By minute 47, each student has started the goal sentence or has marked the exact access blocker.",
    pivot: "If one third is blank, reread the model and provide two course-only options.",
    recovery: "Use speech-to-text, dictation, AAC, a scribe, or paper/Canvas; keep the same Tuesday continuation route.",
    sources: ["Jenna Hainlen, AVID First Week Goal-Setting Sheet, preserved field sequence.", "CCE Day 1 live pacing boundary, 2026-08-17."],
  }),
  noteBlock({
    timing: "47:00-48:00.",
    move: "Have students point to the last field reached and name goal started or access blocked.",
    action: "Mark the exact stopping point on the same page.",
    lookFor: "Teacher and student know the Tuesday starting point without opening another copy.",
    pivot: "Use a two-finger signal when verbal checks would take too long.",
    recovery: "Keep all existing work; Tuesday starts here.",
    sources: ["CCE Day 1 live pacing update, 2026-08-17.", "Jenna Hainlen, AVID Week 1.2 slide 15, check rhythm."],
  }),
  noteBlock({
    timing: "48:00-49:00.",
    move: "Run the DOL check: page open, goal sentence started, or exact blocker recorded.",
    action: "Show the teacher the page location and status without sharing private content.",
    lookFor: "The status list identifies who resumes normally and who needs access recovery Tuesday.",
    pivot: "Use a quick visual status check; do not inspect private goal content at the door.",
    recovery: "Record device, OneNote, or page problems separately so the correct fix is ready.",
    sources: ["CCE Day 1 Demonstration of Learning, revised 2026-08-17.", "Jenna Hainlen, AVID Week 1.2 slide 14, single-action prompt structure."],
  }),
  noteBlock({
    timing: "49:00-50:00.",
    move: "Protect the close: confirm the stopping point and run the established device-return routine.",
    action: "Leave the goal page at the stopping point, return the assigned device, and wait for the teacher check.",
    lookFor: "Devices are returned correctly and unfinished goal work is clearly marked for Tuesday.",
    pivot: "Skip verbal sharing and use the stopping-point signal if the goal block ran long.",
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
