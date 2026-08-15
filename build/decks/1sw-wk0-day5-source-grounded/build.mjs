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
const workspace = path.join(root, "tmp/day5-source-clone");
const starterPath = path.join(workspace, "template-starter.pptx");
const outputPath = path.join(root, "cce-curriculum/resources/avid-reference/source/derived/cce-week1-day5-source-grounded.pptx");
const previewDir = path.join(workspace, "final-preview");
const layoutDir = path.join(workspace, "final-layout/final");

const { FileBlob, PresentationFile } = await importRuntimeModule("@oai/artifact-tool");
await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.rm(previewDir, { recursive: true, force: true });
await fs.rm(layoutDir, { recursive: true, force: true });
await fs.mkdir(previewDir, { recursive: true });
await fs.mkdir(layoutDir, { recursive: true });

const presentation = await PresentationFile.importPptx(await FileBlob.load(starterPath));
const initial = await presentation.inspect({ kind: "slide,shape,textbox,image,notes", maxChars: 600_000 });
const records = initial.ndjson.split("\n").filter(Boolean).map((line) => JSON.parse(line));

function recordFor(kind, slide, predicate = () => true) {
  const record = records.find((item) => item.kind === kind && item.slide === slide && predicate(item));
  if (!record) throw new Error(`Missing ${kind} on output slide ${slide}`);
  return record;
}

function textShape(slide, before) {
  return presentation.resolve(recordFor("textbox", slide, (item) => item.text === before).id);
}

function setText(slide, before, after) {
  textShape(slide, before).text.set(after);
}

function setParagraphs(slide, before, items, fontSize = "14pt") {
  textShape(slide, before).text.set(
    items.map((item) => {
      const entry = typeof item === "string" ? { text: item } : item;
      return {
        ...(entry.spaceBefore ? { spaceBefore: entry.spaceBefore } : {}),
        ...(entry.bullet ? { bulletCharacter: entry.bullet, marginLeft: 22, indent: -12 } : {}),
        runs: [{ run: entry.text, textStyle: { fontSize, ...(entry.bold ? { bold: true } : {}) } }],
      };
    }),
  );
}

function deleteEmptySourceShape(slide, name) {
  presentation.resolve(recordFor("shape", slide, (item) => item.name === name).id).delete();
}

function deleteImage(slide, predicate = () => true) {
  presentation.resolve(recordFor("image", slide, predicate).id).delete();
}

function setNotes(slide, lines) {
  presentation.resolve(recordFor("notes", slide).id).setText(lines.join("\n"));
}

setText(1, "Week 1.6", "CCE Day 5");
setText(1, "AVID 2\nMs. Hainlen", "Catch Up, Xello,\nand Perks & Quirks");

setText(2, "Friday", "Friday");

setText(3, "Pencil\nName Tent\nGet ready to share an answer ——> ", "Chromebook + FYF workbook\nOpen your notebook page\nCheck your private starting path\nWrite before sharing");
setText(3, "Today’s Lesson\nFour Corners", "Today’s Lesson\nPlan one first priority\nFinish one visible result\nVerify before moving on");
setText(3, "Discussion\n\n", "Discussion\n\nWhich unfinished CCE task must happen first today?\n\nWrite it privately. Do not choose the easiest task.");
deleteImage(3);
deleteEmptySourceShape(3, "Google Shape;421;p51");
deleteEmptySourceShape(3, "Google Shape;428;p51");

setText(4, "Pomodoro work time", "Friday Focus Plan");
setParagraphs(4, "Write this information on a sticky note\nIdentify 3 different tasks you want to accomplish during the 4 POMODORO work periods you will have today.\nIdentify 2 “No Zone” activities. These are usually distractions that you should avoid that keep you from staying productive.", [
  { text: "Write three priorities. Circle the one that must happen first.", bold: true },
  { text: "1. Earliest missing core task", spaceBefore: 12 },
  "2. Required Xello login + goal",
  "3. FYF Perks & Quirks only when ready",
  { text: "Then name two No-Zone distractions. This may stay private.", spaceBefore: 12 },
]);
setParagraphs(4, "Name / Period\n\n \n \n\n---------------------------------------\n\n", [
  { text: "MY FIRST PRIORITY", bold: true },
  { text: "1. __________________", spaceBefore: 12 },
  "2. __________________",
  "3. __________________",
  { text: "Circle the task that must happen first.", bold: true, spaceBefore: 12 },
], "12pt");
setText(4, "NO ZONE", "NO-ZONE x2");
deleteEmptySourceShape(4, "Google Shape;300;p43");

const focusTitle = "Pomodoro work time";
const focusBody = "Expectations: \nYou are working. \nSitting with your grades open doing nothing else is not working.\nI have grammar practice if you don’t have anything to do.\nHave your sticky note where I can see it as I walk around– the edge of the table. \nWe will be working silently the first 15 minutes. Your table will gain/lose points for focused/off-task behavior.\nAdditionally, being on task is a grade today. ";

setText(5, focusTitle, "Focus Block: First Task");
setParagraphs(5, focusBody, [
  { text: "Protected focus window: minutes 5-25 (20 minutes).", bold: true },
  { text: "Start on the task the teacher assigned first.", bullet: "•" },
  { text: "Keep your focus plan visible.", bullet: "•" },
  { text: "Work quietly; ask for help when the route is unclear.", bullet: "•" },
  { text: "Show one visible result before opening a second task.", bullet: "•" },
  { text: "No behavior grade or points system. A platform outage is not missing effort.", bold: true, spaceBefore: 14 },
]);

setText(6, focusTitle, "Path 1: Core Catch-Up");
setParagraphs(6, focusBody, [
  { text: "Start here if any core input is missing:", bold: true },
  { text: "Discover Your Core", bullet: "•" },
  { text: "Work Values", bullet: "•" },
  { text: "Building Blocks / profile saves", bullet: "•" },
  { text: "Recommendations", bullet: "•" },
  { text: "Minor 1 reflection", bullet: "•" },
  { text: "Complete the earliest missing input. If Minor 1 is pending, add the result, revise, and submit the same reflection. No replacement packet.", spaceBefore: 14 },
]);

setText(7, focusTitle, "Path 2: Required Xello");
setParagraphs(7, focusBody, [
  { text: "Start here only after core work is ready.", bold: true },
  "1. Enter through district SSO.",
  "2. Confirm the dashboard loads.",
  "3. Open About Me.",
  "4. Choose one goal: Not sure yet; More school or training; or Alternate route.",
  { text: "Do not run Matchmaker today. The goal may change later.", bold: true, spaceBefore: 14 },
]);

setText(8, focusTitle, "Path 3: FYF Only When Ready");
setParagraphs(8, focusBody, [
  { text: "Use this path only when core work AND required Xello are ready.", bold: true },
  "1. Open Find Your Future pp. 4-5.",
  "2. Study the Pest Control Technician example.",
  "3. Choose one Hat and begin the first six-detail table.",
  "4. Mark each detail perk, neutral, or quirk for you.",
  "5. Name the source.",
  { text: "A second Hat is an extension, not the minimum.", bold: true, spaceBefore: 14 },
]);

setText(9, "Evaluate: Share and Learn", "Minute 25: Verify Before Moving");
setText(9, "It is more important to be happy than successful.", "What visible result do you have right now?");
setText(9, "STRONGLY AGREE", "CORE");
setText(9, "AGREE", "XELLO");
setText(9, "STRONGLY\nDISAGREE", "FYF");
setText(9, "DISAGREE", "PENDING");
setParagraphs(9, "Identify a spokesperson who will summarize your group’s position for the rest of the groups. \nShare and engage in a debate with each other. \nBefore a group shares their next point, they must summarize the point of the group that preceded them.​", [
  { text: "Show the teacher one visible result.", bullet: "•" },
  { text: "Move to a second priority only after the first one is verified.", bullet: "•", spaceBefore: 8 },
  { text: "If a platform failed, name the exact outage and use the assigned recovery path.", bullet: "•", spaceBefore: 8 },
], "11pt");

setText(10, focusTitle, "Second Priority Block");
setParagraphs(10, focusBody, [
  { text: "Minutes 25-40: continue after the checkpoint. Move only after your first result is verified.", bold: true },
  { text: "Core catch-up continues or moves to Xello.", bullet: "•" },
  { text: "Xello moves to FYF pp. 4-5 when finished.", bullet: "•" },
  { text: "FYF completes at least one six-detail Hat table.", bullet: "•" },
  { text: "Do not transfer FYF answers to another worksheet or open an unsourced web search today.", bold: true, spaceBefore: 14 },
]);

const quickTitle = "Four Corners – Quickwrite";
const quickLeft = "Write down which position you want to take from the list below and explain why:\nStrongly agree\nAgree\nDisagree\nStrongly disagree ";
const quickCenter = "It is more important to be happy than successful.";
const quickWordBank = "Word Bank: \nHappy                            successful\n              Important                                goals\nMoney                            stress\n                            Family                   career\nBalance                       achievement";

setText(11, quickTitle, "Complete Model: Perks & Quirks");
setParagraphs(11, quickLeft, [
  { text: "Hat: Veterinary Technician", bold: true },
  { text: "Detail: Works with animals and their owners in clinics.", spaceBefore: 12 },
  { text: "My mark: PERK", bold: true, spaceBefore: 12 },
  { text: "Why: I value relationships and have a Building Block caring for my dog.", spaceBefore: 12 },
], "13pt");
setText(11, quickCenter, "Evidence makes the mark personal.");
setParagraphs(11, quickWordBank, [
  { text: "Source: Hats & Ladders career page", bold: true },
  { text: "Still verify: required education + current pay", spaceBefore: 12 },
], "12pt");

setText(12, quickTitle, "Non-Model: What Is Missing?");
setParagraphs(12, quickLeft, [
  { text: "“Good job. Perk. Google.”", bold: true },
  { text: "What needs fixing?", bold: true, spaceBefore: 12 },
  { text: "No career detail", bullet: "•" },
  { text: "No personal reason", bullet: "•" },
  { text: "No usable source", bullet: "•" },
  { text: "Rewrite with a specific detail, your mark, why it matters to you, and the source.", spaceBefore: 12 },
], "13pt");
setText(12, quickCenter, "A label alone is not evidence.");
setParagraphs(12, quickWordBank, [
  { text: "Use the FYF table:", bold: true },
  "DETAIL",
  "MARK + WHY",
  "SOURCE",
  "STILL TO VERIFY",
], "12pt");

setText(13, focusTitle, "FYF Ready Path: Done When");
setParagraphs(13, focusBody, [
  { text: "Your first Hat table has:", bold: true },
  { text: "one Hat named", bullet: "✓" },
  { text: "six actual career details", bullet: "✓" },
  { text: "each detail marked perk, neutral, or quirk for you", bullet: "✓" },
  { text: "a reason for your thinking", bullet: "✓" },
  { text: "the source named", bullet: "✓" },
  { text: "Finish one complete table before starting a second Hat. A second Hat is an extension.", bold: true, spaceBefore: 14 },
]);

setText(14, "Skills Check", "Verify One Result");
const verifyShape = textShape(14, "Each week, we will check in on our grades, planners, and goals.\n\nCheck your grades. If you don’t have a grade yet, write “N/A” for “not available.”\nGet your planner out. Answer the questions honestly.\nGet out your goal from last week. Look at it and reflect on your progress.\nCreate a new academic goal. ");
verifyShape.text.set([
  { runs: [{ run: "Show one confirmed result:", textStyle: { bold: true, fontSize: "18pt" } }] },
  { bulletCharacter: "•", marginLeft: 22, indent: -12, runs: [{ run: "H&L or Minor 1 work completed", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "•", marginLeft: 22, indent: -12, runs: [{ run: "Required Xello login + after-high-school goal completed", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "•", marginLeft: 22, indent: -12, runs: [{ run: "One FYF p. 5 Hat table completed with marks and a source", textStyle: { fontSize: "18pt" } }] },
  { spaceBefore: 18, runs: [{ run: "Review your first-week goal:", textStyle: { bold: true, fontSize: "18pt" } }] },
  { runs: [{ run: "What progress did you make? What is your next small action?", textStyle: { fontSize: "18pt" } }] },
  { spaceBefore: 18, runs: [{ run: "A platform outage is an access problem, not missing effort.", textStyle: { fontSize: "18pt" } }] }
]);
verifyShape.frame = { left: 24, top: 115, width: 886, height: 395 };
deleteImage(14);

setText(15, "Exit: Debrief – Initiating Student Ownership in the Classroom", "Close: Name Your Next CCE Action");
setParagraphs(15, "What was your role in ensuring that this activity was successful? \nIn what ways do you feel more confident as a result of this activity? \nWhat can you do differently next time to ensure that similar activities are even more successful and beneficial?", [
  { text: "Finish in your current notebook page or on the FYF page:", bold: true },
  { text: "This week I completed ____.", spaceBefore: 16 },
  { text: "My next CCE action is ____.", spaceBefore: 16 },
  { text: "I will find it in ____.", spaceBefore: 16 },
  { text: "No new upload. Keep goals, career uncertainty, and access problems private.", bold: true, spaceBefore: 16 },
], "14pt");

const notes = [
  ["Time: 0:00-0:30", "Teacher move: Open the Friday lesson and name the outcome: one verified result, not three half-finished tasks.", "Students: Open the notebook page, Chromebook, and FYF workbook.", "Look-for: Students know Friday is prioritized catch-up plus required Xello, not free choice.", "Support: Read the three pathway names aloud.", "Pivot/trim/recovery: Do not cut orientation; keep it under 30 seconds.", "[Sources]", "- Jenna Hainlen, AVID Week 1.6 slide 1, cover layout; owner-authorized reuse.", "- CCE Day 5 canonical lesson, accessed 2026-08-15.", "[/Sources]"],
  ["Time: 0:30-1:00", "Teacher move: Use as the Friday divider while students open materials.", "Students: Finish opening the required materials.", "Look-for: Chromebook, FYF workbook, and notebook page are ready.", "Support: Point to the Student Guide materials list.", "Pivot/trim/recovery: Keep this transition under 30 seconds.", "[Sources]", "- Jenna Hainlen, AVID Week 1.6 slide 16, Friday divider.", "[/Sources]"],
  ["Time: 1:00-3:00", "Teacher move: Privately assign each student to core catch-up, Xello required, or FYF ready. Preview that the first result must be verified before moving.", "Students: Write the unfinished task that must happen first.", "Look-for: Students do not choose the easiest path.", "Support: Hand a student the exact first path privately rather than projecting names.", "Pivot/trim/recovery: If readiness data is incomplete, begin with the earliest visible missing core input.", "[Sources]", "- Jenna Hainlen, AVID Week 1.6 slide 17, Welcome/Get Ready/Today's Lesson choreography.", "- CCE Day 5 private readiness list.", "[/Sources]"],
  ["Time: 3:00-5:00", "Teacher move: Preserve Jenna's planning routine: three priorities, two No-Zone distractions, one first task. Remove points and compliance scoring.", "Students: Number three priorities, circle the first, and name two private distractions to set aside.", "Look-for: The circled task matches the teacher-assigned path.", "Support: Students may use the projected list rather than invent all three tasks.", "Pivot/trim/recovery: If behind, require only the circled first priority and two No-Zone items.", "[Sources]", "- Jenna Hainlen, AVID Week 1.6 slide 9, focus-plan routine; owner-authorized reuse.", "- CCE Day 5 readiness check and focus plan.", "[/Sources]"],
  ["Time: 5:00-7:00", "Teacher move: State focus expectations and launch the protected 20-minute block, which runs from minute 5 through minute 25. No points, table rewards, or behavior grade.", "Students: Begin only the first assigned priority.", "Look-for: The focus plan stays visible and no student opens three tasks.", "Support: Offer a quiet/private work route and headphones only if campus policy allows.", "Pivot/trim/recovery: If a route fails, redirect within two minutes rather than troubleshooting all period.", "[Sources]", "- Jenna Hainlen, AVID Week 1.6 slides 9-10, bounded focus expectations.", "- CCE Day 5 protected focus block.", "[/Sources]"],
  ["Time: 7:00-13:00", "Teacher move: Conference first with core catch-up students. Assign the earliest missing input, not the entire Friday menu.", "Students: Complete the earliest missing core task or finish the same pending Minor 1 reflection.", "Look-for: One saved/finished result, not a replacement packet.", "Support: A missing platform result may be marked pending while independent sections continue.", "Pivot/trim/recovery: Broad H&L outage moves affected students to the verified offline/FYF route and records catch-up.", "[Sources]", "- CCE Day 5 core catch-up path.", "- H&L core profile sequence; district-licensed, authenticated use only.", "[/Sources]"],
  ["Time: 13:00-19:00", "Teacher move: Work with students whose core is ready but Xello is incomplete. Verify district SSO, dashboard load, About Me, and one goal only.", "Students: Complete required Xello login and choose one after-high-school goal.", "Look-for: Not sure yet, More school or training, or Alternate route is selected; Matchmaker is not opened.", "Support: State that the goal may change later and stays private.", "Pivot/trim/recovery: Record access errors exactly; do not mark an outage as missing effort.", "[Sources]", "- Bowie Grade 8 Xello Completion Standards, district-configured login and after-high-school goal requirement.", "- CCE Day 5 Xello boundary.", "[/Sources]"],
  ["Time: 19:00-25:00", "Teacher move: Launch FYF only for students whose core and required Xello are ready. Model how to enter the first table from the Pest Control Technician example.", "Students: Choose one Hat and begin the first six-detail table.", "Look-for: Actual career details, personal marks, and a named source.", "Support: Read the six actions aloud and keep the complete model available later in the deck.", "Pivot/trim/recovery: No workbook uses one accepted notebook/paper table with no later recopying.", "[Sources]", "- Find Your Future pp. 4-5, Perks and Quirks; district-licensed, authenticated use only.", "- CCE Day 5 ready path.", "[/Sources]"],
  ["Time: 25:00 checkpoint (no added minutes)", "Teacher move: Run the canonical minute-25 look-for without creating a separate work block. Verify one visible result before anyone changes tasks.", "Students: Show a core, Xello, FYF, or documented pending result.", "Look-for: One visible result, not three partially opened tasks.", "Support: Let students point to the result instead of explaining publicly.", "Pivot/trim/recovery: A platform outage goes in Pending with the exact recovery route; move immediately into the minute 25-40 block.", "[Sources]", "- Jenna Hainlen, AVID Week 1.6 slide 20, evaluate/share checkpoint frame.", "- CCE Day 5 minute 25 look-for.", "[/Sources]"],
  ["Time: 25:00-26:00", "Teacher move: Launch the second-priority window, which runs from minute 25 through minute 40, and restate the movement rule.", "Students: Continue or move one step in the required order after verification.", "Look-for: Core moves to Xello; Xello moves to FYF; FYF finishes one table.", "Support: Keep each student's next path private and specific.", "Pivot/trim/recovery: Protect the first required result; a second Hat is the first trim.", "[Sources]", "- Jenna Hainlen, AVID Week 1.6 slide 10, focused-work expectations frame.", "- CCE Day 5 second priority block.", "[/Sources]"],
  ["Time: 26:00-30:00", "Teacher move: Read the complete FYF model and point to detail, mark, why, source, and still-to-verify.", "Students: Identify why the mark is personal rather than universally good or bad.", "Look-for: Students can name a usable source and an unanswered question.", "Support: Keep the five-part model visible for FYF students; others continue assigned work.", "Pivot/trim/recovery: If few students are ready for FYF, teach the model to that small group.", "[Sources]", "- CCE Day 5 complete model.", "- Find Your Future pp. 4-5, Perks and Quirks; district-licensed, authenticated use only.", "[/Sources]"],
  ["Time: 30:00-32:00", "Teacher move: Show the non-model and ask what evidence is missing.", "Students: Identify missing detail, personal reason, and usable source.", "Look-for: Students stop writing Good job or Google as evidence.", "Support: Read the five table labels aloud.", "Pivot/trim/recovery: If behind, state the three fixes in 30 seconds.", "[Sources]", "- CCE Day 5 non-model.", "- Jenna Hainlen, AVID Week 1.6 slide 18, quickwrite/model frame.", "[/Sources]"],
  ["Time: 32:00-40:00", "Teacher move: Keep the second-priority block running until minute 40. Check the one-table minimum and redirect any student who started an unsourced search or second Hat early.", "Students: Finish one complete six-detail Hat table or the assigned required result.", "Look-for: FYF work has six details, six personal marks, reasons, and a source; other paths show their required result.", "Support: Accept the no-workbook fallback without later recopying.", "Pivot/trim/recovery: Cut the second Hat and any whole-group share first; stop work at minute 40 for final verification.", "[Sources]", "- Find Your Future pp. 4-5, Perks and Quirks; district-licensed, authenticated use only.", "- CCE Day 5 FYF minimum and second-priority block.", "[/Sources]"],
  ["Time: 40:00-45:00", "Teacher move: Verify one end-of-week result and ask for a brief first-week goal review. Record remaining access problems.", "Students: Show one result and name one next small action.", "Look-for: The verified result matches one of the three Demonstration of Learning routes.", "Support: A platform outage is documented as an access problem, not missing effort.", "Pivot/trim/recovery: Protect verification; skip any voluntary sharing.", "[Sources]", "- Jenna Hainlen, AVID Week 1.6 slide 6, weekly skills/goal review structure.", "- CCE Day 5 Demonstration of Learning.", "[/Sources]"],
  ["Time: 45:00-50:00", "Teacher move: Run the three-line close and name the exact catch-up location for any remaining requirement.", "Students: Complete the sentence in the current notebook/FYF page; no new upload.", "Look-for: Completed result, next action, and where to find it.", "Support: Read the three stems aloud; keep goals and access problems private.", "Pivot/trim/recovery: Protect the next-action line even in a shortened period.", "[Sources]", "- Jenna Hainlen, AVID Week 1.6 slide 21, debrief/ownership close.", "- Jeswin Thomas, man in brown sweater sitting on chair, https://unsplash.com/photos/man-in-brown-sweater-sitting-on-chair--hgJu2ykh4E, Unsplash License, accessed 2026-08-15; source-deck image and on-slide credit retained.", "- CCE Day 5 close.", "[/Sources]"],
];

if (notes.length !== presentation.slides.items.length) throw new Error("Notes/slide count mismatch");
notes.forEach((entry, index) => setNotes(index + 1, entry));

const schedule = [
  { phase: "readiness", start: 0, end: 0.5, label: "Time: 0:00-0:30" },
  { phase: "readiness", start: 0.5, end: 1, label: "Time: 0:30-1:00" },
  { phase: "readiness", start: 1, end: 3, label: "Time: 1:00-3:00" },
  { phase: "readiness", start: 3, end: 5, label: "Time: 3:00-5:00" },
  { phase: "protected", start: 5, end: 7, label: "Time: 5:00-7:00" },
  { phase: "protected", start: 7, end: 13, label: "Time: 7:00-13:00" },
  { phase: "protected", start: 13, end: 19, label: "Time: 13:00-19:00" },
  { phase: "protected", start: 19, end: 25, label: "Time: 19:00-25:00" },
  { phase: "checkpoint", start: 25, end: 25, label: "Time: 25:00 checkpoint (no added minutes)" },
  { phase: "second", start: 25, end: 26, label: "Time: 25:00-26:00" },
  { phase: "second", start: 26, end: 30, label: "Time: 26:00-30:00" },
  { phase: "second", start: 30, end: 32, label: "Time: 30:00-32:00" },
  { phase: "second", start: 32, end: 40, label: "Time: 32:00-40:00" },
  { phase: "verify", start: 40, end: 45, label: "Time: 40:00-45:00" },
  { phase: "close", start: 45, end: 50, label: "Time: 45:00-50:00" },
];
schedule.forEach((entry, index) => {
  if (entry.end < entry.start) throw new Error(`Day 5 schedule reverses on slide ${index + 1}`);
  if (index > 0 && entry.start < schedule[index - 1].end) throw new Error(`Day 5 schedule overlaps on slide ${index + 1}`);
  if (notes[index][0] !== entry.label) throw new Error(`Day 5 note timing drift on slide ${index + 1}`);
});
const phaseMinutes = schedule.reduce((totals, entry) => ({
  ...totals,
  [entry.phase]: (totals[entry.phase] || 0) + entry.end - entry.start,
}), {});
if (schedule.at(-1).end !== 50) throw new Error("Day 5 schedule does not end at minute 50");
if (phaseMinutes.readiness !== 5 || phaseMinutes.protected !== 20 || phaseMinutes.second !== 15 || phaseMinutes.verify !== 5 || phaseMinutes.close !== 5) {
  throw new Error(`Day 5 phase timing drift: ${JSON.stringify(phaseMinutes)}`);
}

const finalInspect = await presentation.inspect({ kind: "slide,textbox,image,notes", maxChars: 600_000 });
await fs.writeFile(path.join(workspace, "final.inspect.ndjson"), finalInspect.ndjson);
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
console.log(JSON.stringify({ outputPath, slideCount: presentation.slides.items.length, previewDir, layoutDir }, null, 2));
