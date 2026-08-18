// CCE 1SW Wk0 Day 1 daily master: CCE Notebook and First-Week Goal.
// Source of truth: docs/1sw/wk0-classroom-routines/day1.md (50-minute flow:
// 5 welcome/Do Now + 8 tools + 12 notebook + 17 goal + 5 check + 3 close).
// Starter: AVID Week 1.2 clone (Jenna Hainlen); the AVID slide structures are kept
// and re-texted with editable paragraphs. Projected text is student-facing and
// teacher-neutral ("your teacher"); teacher moves live in the speaker notes.

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadRuntime, openStarter, slideAt, setNotes, finalize } from "../lib/slide_kit.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../../..");
const workspace = path.join(root, "tmp/cce-week1-source-clone");
const starterPath = path.join(workspace, "template-starter.pptx");
const outputPath = path.join(root, "cce-curriculum/resources/avid-reference/source/derived/cce-week1-day1-source-grounded.pptx");
const goalImagePath = path.join(root, "tmp/cce-first-week-goal-render-20260815-v3/page-1.png");

const runtime = await loadRuntime();
const { presentation, recordFor, textbox, setText } = await openStarter(runtime, starterPath);
const S = (n) => slideAt(presentation, n);
const setParagraphs = (slide, before, paragraphs) => textbox(slide, before).text.set(paragraphs);
const P = (runs, extra = {}) => ({ ...extra, runs: runs.map(([run, textStyle]) => ({ run, textStyle })) });
const bullet = (char, run, size = "18pt", extra = {}) => ({ bulletCharacter: char, marginLeft: 26, indent: -12, ...extra, runs: [{ run, textStyle: { fontSize: size } }] });

async function swapImage(slide, filePath, alt) {
  const image = presentation.resolve(recordFor("image", slide).id);
  const keep = { frame: image.frame, crop: image.crop, geometry: image.geometry, borderRadius: image.borderRadius };
  image.replace({ blob: await fs.readFile(filePath), contentType: "image/png", alt, fit: "contain" });
  image.frame = keep.frame; image.crop = keep.crop; image.fit = "contain"; image.geometry = keep.geometry; image.borderRadius = keep.borderRadius;
}

// 1-2: cover and Monday divider
setText(1, "Week 1.2", "CCE Week 1");
setText(1, "AVID 2\nMs. Hainlen", "Career & College Explorations\nClassroom Routines and Career Self-Discovery");
setText(2, "Friday", "Monday");

// 3: As You Enter (Get Ready + Today's Lesson + goal page thumbnail)
setText(3, "Pencil\nGet out any school supplies you brought for this class\nGet ready to share an answer ——> ", "Wait for the device cue\nOpen Canvas: Day 1 Student Guide\nHave a pencil ready");
setParagraphs(3, "Set up Binders & Planners", [
  P([["I can: ", { bold: true, fontSize: "14pt" }], ["set up my CCE notebook, find the course tools, and plan one specific first-week action.", { fontSize: "14pt" }]]),
  P([["Today: ", { bold: true, fontSize: "14pt" }], ["Do Now → devices and course tools → notebook setup → first-week goal → partner or private check.", { fontSize: "14pt" }]], { spaceBefore: 6 }),
]);
await swapImage(3, goalImagePath, "CCE first-week goal page used during today's lesson");

// 4: Do Now
setText(4, "Think", "Do Now");
setParagraphs(4, "What are some behaviors that successful students do?\n", [
  P([["You are starting a new class. What is one thing a student can do to make the first week go well?", { fontSize: "24pt" }]]),
  P([["Sentence stem: A student can _____.", { bold: true, fontSize: "22pt" }]], { spaceBefore: 18 }),
  P([["Español: Un estudiante puede _____.", { fontSize: "18pt", color: "#1F617A" }]], { spaceBefore: 8 }),
]);

// 5: Share or stay private
setText(5, "stand-share-sit", "Share or stay private");
setText(5, "Everyone stand.\n\nShare with your partner: What are some behaviors that successful students do?\n\nOnce you share, sit down. \n", "Choose one:\n\nShare one answer with a partner.\n\nOr keep your response private. Sitting or standing both count.");

// 6: Check out your device (VILS assigned-device routine)
setText(6, "Let’s Set Up your Binders!", "Check Out Your Device");
setParagraphs(6, "Get out your 3 ring binder & tabs OR your folders for class.\nYou need: \nYour first AND last name on the front of binder/folders. (I have sharpies you can borrow.)\nYour 8 tabs or folders labeled with each of your class names. (Example: Write “English” on the tab and not “1st period”)\nAll of your AVID papers 3-hole punched and in the AVID section.\nSecure all your papers in your binder. No papers should be loose.\nExtra Notebook paper (or spiral notebook) at the front.\nPencils & highlighters should be in a designated spot. (either in a pencil pouch or a specific pocket of your backpack)", [
  P([["Use only the Chromebook assigned to you.", { bold: true, fontSize: "21pt", color: "#172554" }]]),
  bullet("1", "Find the device number your teacher names."),
  bullet("2", "Check the device and charger before moving."),
  bullet("3", "Carry it with two hands and place it flat on the desk."),
  bullet("4", "Report a missing, damaged, or uncharged device before signing in."),
  P([["DONE WHEN: ", { bold: true, fontSize: "18pt" }], ["your assigned device and charger are at your seat.", { fontSize: "18pt" }]], { spaceBefore: 10 }),
]);
presentation.resolve(recordFor("image", 6).id).frame = { left: 748, top: 8, width: 190, height: 136 };

// 7: Find your course tools (canonical section 2)
setText(7, "Get out your Planner!", "Find Your Course Tools");
setParagraphs(7, "You can use a physical planner. (I have extras!)\nOr you can use a digital planner you can access on your school computer.\nI suggest either Google calendar, Canvas’ calendar, or your iCloud calendar. ", [
  bullet("1", "Canvas: open the Day 1 Student Guide. Every day starts here.", "20pt"),
  bullet("2", "Find Your Future workbook: hold it up. Do not write in it yet.", "20pt", { spaceBefore: 10 }),
  bullet("3", "Hats & Ladders and Xello: find the links in the guide. Do not start them today.", "20pt", { spaceBefore: 10 }),
  P([["DONE WHEN: ", { bold: true, fontSize: "20pt" }], ["you can get back to the Day 1 Student Guide without asking for the link.", { fontSize: "20pt" }]], { spaceBefore: 12 }),
]);

// 8: Open your CCE notebook (WYS / DO THIS / DONE WHEN)
setText(8, "Evaluate: Planner Expectations", "Open Your CCE Notebook");
setParagraphs(8, "Academic Content\nYou must have something written down for every class every day.\nHomework/after school responsibilities\nIf no homework/after school responsibilities, a short note about what you did in class\nNote: even if you were absent, you need to have recorded something for each class. Make sure you ask what you missed!", [
  P([["WHAT YOU SEE", { bold: true, fontSize: "20pt" }]]),
  bullet("✓", "Your private OneNote Class Notebook", "18pt", { marginLeft: 20, indent: -10 }),
  bullet("✓", "Sections: CCE Work, Focused Notes, Evidence & Reflection", "18pt", { marginLeft: 20, indent: -10 }),
  P([["DO THIS", { bold: true, fontSize: "20pt" }]]),
  bullet("1", "Open CCE Work → Notebook Setup + First-Week Goal.", "16pt"),
  bullet("2", "Type: The place I will use for CCE work is ____. If it does not open, I will use ____.", "16pt"),
]);
setParagraphs(8, "Organization\nLegible to you and your teacher\nPrevious tasks are checked or crossed off\nColors, highlights, or symbols are used if wanted", [
  P([["DONE WHEN", { bold: true, fontSize: "20pt" }]]),
  bullet("✓", "The goal page is open", "18pt", { marginLeft: 20, indent: -10 }),
  bullet("✓", "Your notebook-location sentence is typed", "18pt", { marginLeft: 20, indent: -10 }),
  bullet("✓", "You know what to use if the notebook does not open", "18pt", { marginLeft: 20, indent: -10 }),
]);

// 9: Find the six goal fields
setText(9, "Skills Check", "Six Goal Fields");
setParagraphs(9, "Each week, we will check in on our grades, planners, and goals. I want you to pick a goal for THIS week. Something small but meaningful!\n\nHere are some ideas (but you can create your own!)\n☐ Turn in all assignments on time\n☐ Bring my supplies to every class\n☐ Write down homework every day\n☐ Participate at least once in each class\n☐ Ask questions when I need help\n☐ Study or review notes for at least 15 minutes each night\n☐ Keep my binder or folders organized\n☐ Check my grades this week\n☐ Get to class on time every day\n☐ Limit distractions during class", [
  P([["WHAT YOU SEE", { bold: true, fontSize: "14pt", color: "#6350A8" }]]),
  P([["The First-Week Goal page with six fields: goal, why, action, checkpoint, confidence, support.", { fontSize: "16pt" }]]),
  P([["DO THIS", { bold: true, fontSize: "14pt", color: "#6350A8" }]], { spaceBefore: 10 }),
  P([["Point to each field as your teacher reads it.", { fontSize: "16pt" }]]),
  P([["DONE WHEN", { bold: true, fontSize: "14pt", color: "#7A4A00" }]], { spaceBefore: 10 }),
  P([["You can find all six fields on your own page.", { bold: true, fontSize: "16pt" }]]),
]);
await swapImage(9, goalImagePath, "CCE First Week Goal-Setting sheet with goal, reason, action, checkpoint, confidence, and support fields");

// 10: Choose one goal for Friday
setText(10, "Think", "Choose One Goal for Friday");
setParagraphs(10, "What are some behaviors that successful students do?\n", [
  P([["Turn your Do Now habit into one goal you can finish by Friday.", { fontSize: "22pt" }]]),
  P([["My first-week CCE goal: By Friday, I will _____.", { bold: true, fontSize: "24pt" }]], { spaceBefore: 16 }),
  P([["A course-only or made-up goal is okay.", { fontSize: "18pt" }]], { spaceBefore: 12 }),
  P([["DONE WHEN: ", { bold: true, fontSize: "18pt" }], ["your sentence names one clear CCE action.", { fontSize: "18pt" }]], { spaceBefore: 12 }),
]);

// 11: Complete model
setText(11, "Let’s write!", "Model: a complete goal plan");
setText(11, "Seat 1- Writer", "All six fields");
setParagraphs(11, "Question\n\nOf the nine soft skills described in the article, which one does your table think is the most important for success in high school right now? Explain your reasoning.\n\nMinimum: 3 sentences", [
  P([["Goal: ", { bold: true, fontSize: "17pt" }], ["By Friday, I will complete Discover Your Core carefully.", { fontSize: "17pt" }]]),
  P([["Why: ", { bold: true, fontSize: "17pt" }], ["I want the result to be based on my real answers.", { fontSize: "17pt" }]], { spaceBefore: 4 }),
  P([["Action: ", { bold: true, fontSize: "17pt" }], ["I will read every question and ask for help if a word is unclear.", { fontSize: "17pt" }]], { spaceBefore: 4 }),
  P([["Checkpoint: ", { bold: true, fontSize: "17pt" }], ["Tuesday during the Hats & Ladders block.", { fontSize: "17pt" }]], { spaceBefore: 4 }),
  P([["Confidence: ", { bold: true, fontSize: "17pt" }], ["4", { fontSize: "17pt" }]], { spaceBefore: 4 }),
  P([["Support: ", { bold: true, fontSize: "17pt" }], ["Teacher check-in.", { fontSize: "17pt" }]], { spaceBefore: 4 }),
]);

// 12: Write all six fields (work slide)
setText(12, "Let’s write!", "Write Your Goal Plan");
setText(12, "Seat 2- Speaker", "Six fields, same page");
setParagraphs(12, "Question\n\nOf the nine soft skills described in the article, which one does your table think is the most important for success in high school right now? Explain your reasoning.\n\nMinimum: 3 sentences", [
  P([["1. Goal: By Friday, I will ____.", { fontSize: "19pt" }]]),
  P([["2. Why this goal matters to me: ____.", { fontSize: "19pt" }]], { spaceBefore: 3 }),
  P([["3. One specific action I will take: ____.", { fontSize: "19pt" }]], { spaceBefore: 3 }),
  P([["4. When or at which checkpoint: ____.", { fontSize: "19pt" }]], { spaceBefore: 3 }),
  P([["5. My confidence right now: 1 2 3 4 5", { fontSize: "19pt" }]], { spaceBefore: 3 }),
  P([["6. What will help me follow through: ____.", { fontSize: "19pt" }]], { spaceBefore: 3 }),
  P([["Español: Mi meta es ____. Es importante porque ____. Voy a ____.", { fontSize: "16pt", color: "#1F617A" }]], { spaceBefore: 10 }),
]);

// 13: Partner or private check
setText(13, "stand-share-sit", "Partner or Private Check");
setParagraphs(13, "Everyone stand.\n\nShare with your partner: What are some behaviors that successful students do?\n\nOnce you share, sit down. \n", [
  P([["Share only your action and checkpoint with a partner, or check privately:", { bold: true, fontSize: "20pt" }]]),
  bullet("•", "Can someone see what I will do?", "21pt", { spaceBefore: 10, marginLeft: 22 }),
  bullet("•", "Did I name when I will do it?", "21pt", { marginLeft: 22 }),
  bullet("•", "Did I choose a support?", "21pt", { marginLeft: 22 }),
  P([["Fix one missing part.", { fontSize: "18pt" }]], { spaceBefore: 12 }),
]);

// 14: DOL
setText(14, "Think", "Show Your Learning");
setParagraphs(14, "What are some behaviors that successful students do?\n", [
  P([["SHOW: ", { bold: true, fontSize: "22pt" }], ["point to your action and your checkpoint on your goal page.", { fontSize: "22pt" }]]),
  P([["SAY: ", { bold: true, fontSize: "22pt" }], ["where you will find tomorrow’s directions (Canvas → Day 2 Student Guide).", { fontSize: "22pt" }]], { spaceBefore: 14 }),
  P([["DONE WHEN: ", { bold: true, fontSize: "20pt" }], ["all six fields are filled in and you can name tomorrow’s starting point.", { fontSize: "20pt" }]], { spaceBefore: 14 }),
]);

// 15: Close and return devices
setText(15, "Evaluate: Planner Set-Up", "Close: Return Your Device");
setParagraphs(15, "From now until the next class, be sure to continue updating your planner.", [
  bullet("1", "Close the Chromebook when your teacher gives the cue.", "20pt"),
  bullet("2", "Carry the device and charger to the assigned slot.", "20pt", { spaceBefore: 8 }),
  bullet("3", "Connect the charger exactly as shown.", "20pt", { spaceBefore: 8 }),
  P([["Tomorrow: ", { bold: true, fontSize: "20pt" }], ["Hats & Ladders begins building your Climber Profile.", { fontSize: "20pt" }]], { spaceBefore: 14 }),
]);

// Speaker notes (full schema on every slide)
const SRC_LESSON = "CCE 1SW Wk0 Day 1 canonical lesson, docs/1sw/wk0-classroom-routines/day1.md";
const SRC_AVID12 = (slide, what) => `Jenna Hainlen, AVID Week 1.2 slide ${slide}, ${what} (teacher-provided; structure only)`;
const SRC_GOAL = "Jenna Hainlen, AVID 26-27 Skills Check, First Week Goal-Setting Sheet; CCE minimal reframing 2026-08-15";
const RECOVERY_NB = "OneNote will not open: Canvas response or the paper goal page is equal; a student who uses the fallback does not recopy later.";
const notes = [
  { time: "Before class", move: "Distribute the Notebook Setup + First-Week Goal page to each student's CCE Work section and confirm the fields accept typing from a student test account. Do not run a student autosave/reopen test in class.", student: "None yet.", lookFor: "View distributed pages shows one copy per student.", pivot: "If distribution fails, use the Canvas/paper page all period; do not repair OneNote during class.", recovery: RECOVERY_NB, sources: [SRC_AVID12(1, "cover layout"), SRC_LESSON] },
  { time: "0:00-0:00", move: "Day divider while students enter and wait for the device cue.", student: "Sit; wait for the cue.", lookFor: "Students not opening devices before the cue.", pivot: "Show for seconds only.", recovery: "None needed.", sources: [SRC_AVID12(42, "day-divider layout")] },
  { time: "0:00-0:01", move: "Read the I-can statement and today's five parts once. Point to the goal page thumbnail: that is where today ends.", student: "Read along.", lookFor: "Students can name the last part (goal plan).", pivot: "Do not re-explain.", recovery: "Absent students use the Day 1 Student Guide.", sources: [SRC_AVID12(43, "Welcome/Get Ready/Today's Lesson choreography"), SRC_LESSON] },
  { time: "0:01-0:03", move: "Do Now. Silent think time. Connect the answer to the goal page later: one useful habit becomes a specific action and checkpoint.", student: "Write one sentence with the stem.", lookFor: "A concrete habit, not 'be good'.", pivot: "Offer two examples aloud if the room stalls.", recovery: "Paper page is equal.", sources: [SRC_AVID12(14, "private Think routine"), SRC_LESSON] },
  { time: "0:03-0:05", move: "Optional partner share, seated/private response equal. Model the daily routine: start in Canvas, open the named activity, notebook only when asked, turn in only what the guide names.", student: "Share one answer or keep it private.", lookFor: "Students can name where the daily directions live.", pivot: "Skip the share if devices are late.", recovery: "None needed.", sources: [SRC_AVID12(15, "stand-share-sit rhythm, adapted for equal access"), SRC_LESSON] },
  { time: "0:05-0:09", move: "Assigned-device check-out. Name the device number pattern; students report problems before signing in.", student: "Get the assigned Chromebook and charger; report issues.", lookFor: "Every student with the right number; nothing carried one-handed.", pivot: "If numbers are not set yet, use the seating chart order for today.", recovery: "A student without a working device pairs for the tools tour and uses the paper goal page.", sources: [SRC_AVID12(46, "procedure-launch structure"), SRC_LESSON] },
  { time: "0:09-0:13", move: "Course-tool tour: Canvas Day 1 Student Guide, FYF workbook, H&L and Xello links. Nothing is started today.", student: "Open the guide; hold up the workbook; find the two links.", lookFor: "By minute 13, 80 percent can return to the Day 1 guide without the link.", pivot: "If fewer than 80 percent can return, repeat the navigation once on the projector; do not add tools.", recovery: "Paper copy of the guide for a device-less student.", sources: [SRC_AVID12(47, "step-by-step procedure structure"), SRC_LESSON] },
  { time: "0:13-0:25", move: "Notebook setup. Show OneNote once: CCE Work → Notebook Setup + First-Week Goal. Students type the location sentence. Demonstrate Immersive Reader once if available. Do not spend time proving autosave.", student: "Open the page; type the location sentence.", lookFor: "By minute 25 every student has a confirmed digital page or a named physical/Canvas route.", pivot: "Record account problems and move on; do not troubleshoot live.", recovery: RECOVERY_NB, sources: ["Microsoft Support, Class Notebook page distribution, accessed 2026-08-17", SRC_LESSON] },
  { time: "0:25-0:27", move: "Read the six field names aloud once while students point. Keep the source field order.", student: "Point to each field.", lookFor: "Students locating field 6 (support).", pivot: "One pass only.", recovery: "Paper page has the same six fields.", sources: [SRC_GOAL, SRC_AVID12(13, "Skills Check framing")] },
  { time: "0:27-0:29", move: "Students turn the Do Now habit into one Friday goal sentence. Course-only or fictional goals allowed; no disclosure required.", student: "Write the goal sentence.", lookFor: "One clear CCE action with a Friday stop.", pivot: "Offer the model on the next slide early if many stall.", recovery: "Paper page equal.", sources: [SRC_AVID12(14, "Think structure"), SRC_LESSON] },
  { time: "0:29-0:31", move: "Show the complete model, then the non-model in words: 'Do better / try harder later / confidence 5' - ask what is missing (action, checkpoint, support). Make the plan smaller and more specific rather than telling students to want it more.", student: "Compare the model to their own sentence.", lookFor: "Students naming the missing action/checkpoint.", pivot: "Revise one anonymous vague example together if a third of the room is vague.", recovery: "None needed.", sources: [SRC_LESSON, SRC_AVID12(22, "model/writing frame")] },
  { time: "0:31-0:42", move: "Work time with the six fields projected. Lap: by minute 38 every goal has an action and a checkpoint.", student: "Fill in all six fields on the same page.", lookFor: "Action + checkpoint present; support chosen.", pivot: "If a third of the room is still vague at minute 38, pause and revise one anonymous example together.", recovery: RECOVERY_NB, sources: [SRC_GOAL, SRC_LESSON] },
  { time: "0:42-0:47", move: "Partner or private check on action and checkpoint only; students never have to share the goal or why. Students fix one missing part.", student: "Share action + checkpoint or self-check privately.", lookFor: "One repair made where needed.", pivot: "Cut to the private self-check if time is short.", recovery: "Private teacher check counts.", sources: [SRC_AVID12(15, "check rhythm"), SRC_LESSON] },
  { time: "0:47-0:49", move: "DOL: students point to action and checkpoint and name tomorrow's starting point. If most of a class stopped before the plan fields, record the last field reached and finish those fields in the first five minutes of Day 2 without a second goal page (pacing note for that class only).", student: "Show the fields; say where tomorrow's directions live.", lookFor: "All six fields filled, or the last field reached recorded.", pivot: "Protect this DOL; trim the check before trimming this.", recovery: RECOVERY_NB, sources: [SRC_LESSON, SRC_AVID12(14, "single-action prompt structure")] },
  { time: "0:49-0:50", move: "Run the device-return routine and preview tomorrow: H&L begins building the Climber Profile; the notebook holds only the short thinking the app and workbook do not already save.", student: "Return the device and charger correctly.", lookFor: "Slot, charger, and device checked.", pivot: "None.", recovery: "None needed.", sources: [SRC_AVID12(50, "evaluation/close layout; Jess Bailey photo attribution retained on-slide"), SRC_LESSON] },
];
notes.forEach((spec, index) => setNotes(S(index + 1), spec));

const result = await finalize(runtime, presentation, { workspace, outputPath, expectedCount: 15 });
console.log(JSON.stringify(result, null, 2));
