import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { finalize } from "../lib/slide_kit.mjs";

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

function setParagraphs(slide, before, items, fontSize = "20pt") {
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

function setFrame(slide, before, frame) {
  textShape(slide, before).frame = frame;
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
textShape(1, "AVID 2\nMs. Hainlen").text.set([
  { runs: [{ run: "Career Perks, Neutrals\n& Quirks", textStyle: { fontSize: "24pt", bold: true, color: "#24323d" } }] },
]);

setText(2, "Friday", "Friday");

setText(3, "Pencil\nName Tent\nGet ready to share an answer ——> ", "Chromebook + FYF workbook\nOpen Day 5 Student Guide\nHave workbook on pp. 4-5\nThink before sharing");
textShape(3, "Today’s Lesson\nFour Corners").text.set([
  { bulletCharacter: " ", marginLeft: 0, indent: 0, runs: [{ run: "Today’s Lesson", textStyle: { fontSize: "24pt", bold: true, color: "#003865" } }] },
  { bulletCharacter: " ", marginLeft: 0, indent: 0, runs: [{ run: "Learn Perk / Neutral / Quirk", textStyle: { fontSize: "19pt" } }] },
  { bulletCharacter: " ", marginLeft: 0, indent: 0, runs: [{ run: "Study a complete model", textStyle: { fontSize: "19pt" } }] },
  { bulletCharacter: " ", marginLeft: 0, indent: 0, runs: [{ run: "Analyze one career", textStyle: { fontSize: "19pt" } }] },
]);
setText(3, "Discussion\n\n", "Discussion\n\nThink about working outside in the Texas summer heat.\n\nIs that a Perk, Neutral, or Quirk for you? Why?");
deleteImage(3);
deleteEmptySourceShape(3, "Google Shape;421;p51");
deleteEmptySourceShape(3, "Google Shape;428;p51");

setText(4, "Pomodoro work time", "Today's Learning");
setParagraphs(4, "Write this information on a sticky note\nIdentify 3 different tasks you want to accomplish during the 4 POMODORO work periods you will have today.\nIdentify 2 “No Zone” activities. These are usually distractions that you should avoid that keep you from staying productive.", [
  { text: "Analyze real career details:", bold: true },
  { text: "Learn Perk, Neutral, and Quirk on FYF p. 4", bullet: "•", spaceBefore: 10 },
  { text: "Study a complete evidence-based model", bullet: "•" },
  { text: "Complete one career table on FYF p. 5", bullet: "•" },
  { text: "Explain how job details match your personal work values.", spaceBefore: 10 },
]);
setParagraphs(4, "Name / Period\n\n \n \n\n---------------------------------------\n\n", [
  { text: "TODAY'S GOALS", bold: true },
  { text: "FYF p. 5 Career Table", bullet: "•", spaceBefore: 12 },
  { text: "4+ Specific Career Details", bullet: "•" },
  { text: "P / N / Q Mark + Personal Reason", bullet: "•" },
  { text: "One response home today.", bold: true, spaceBefore: 12 },
], "16pt");
setText(4, "NO ZONE", "CCE GOALS");
deleteEmptySourceShape(4, "Google Shape;300;p43");

const focusTitle = "Pomodoro work time";
const focusBody = "Expectations: \nYou are working. \nSitting with your grades open doing nothing else is not working.\nI have grammar practice if you don’t have anything to do.\nHave your sticky note where I can see it as I walk around– the edge of the table. \nWe will be working silently the first 15 minutes. Your table will gain/lose points for focused/off-task behavior.\nAdditionally, being on task is a grade today. ";

setText(5, focusTitle, "Three Ways to Mark It");
setParagraphs(5, focusBody, [
  { text: "PERK 👍", bold: true },
  { text: "A detail that fits what you value or prefer.", spaceBefore: 6 },
  { text: "NEUTRAL ➖", bold: true, spaceBefore: 14 },
  { text: "A detail that neither attracts nor discourages you.", spaceBefore: 6 },
  { text: "QUIRK 👎", bold: true, spaceBefore: 14 },
  { text: "A demanding or unusual detail that may not fit you.", spaceBefore: 6 },
], "24pt");
setFrame(5, focusBody, { left: 42, top: 122, width: 872, height: 360 });

setText(6, focusTitle, "One Fact, Three Viewpoints");
setParagraphs(6, focusBody, [
  { text: "Career detail: Work hours change from week to week.", bold: true },
  { text: "PERK: “I value variety and dislike repetitive routines.”", bullet: "•", spaceBefore: 12 },
  { text: "NEUTRAL: “Changing hours would not affect my decision.”", bullet: "•" },
  { text: "QUIRK: “I value a predictable daytime schedule.”", bullet: "•" },
  { text: "The fact stayed the same. The person’s preferences changed the mark.", bold: true, spaceBefore: 14 },
], "23pt");
setFrame(6, focusBody, { left: 42, top: 122, width: 872, height: 350 });

setText(7, focusTitle, "The Evidence Formula");
setParagraphs(7, focusBody, [
  { text: "SPECIFIC CAREER FACT", bold: true },
  { text: "↓", spaceBefore: 6 },
  { text: "PERK / NEUTRAL / QUIRK", bold: true, spaceBefore: 6 },
  { text: "↓", spaceBefore: 6 },
  { text: "PERSONAL VALUE OR PREFERENCE", bold: true, spaceBefore: 6 },
  { text: "↓  Name the source.", bold: true, spaceBefore: 6 },
], "24pt");
setFrame(7, focusBody, { left: 42, top: 122, width: 872, height: 350 });

setText(8, focusTitle, "Find Specific Career Facts");
setParagraphs(8, focusBody, [
  { text: "Record what the worker actually does, uses, studies, or experiences:", bold: true },
  { text: "Daily duties", bullet: "•", spaceBefore: 10 },
  { text: "Schedule and work setting", bullet: "•" },
  { text: "Education or training", bullet: "•" },
  { text: "Tools, technology, and safety conditions", bullet: "•" },
  { text: "Avoid vague labels such as “fun,” “easy,” or “good money.”", bold: true, spaceBefore: 14 },
], "23pt");
setFrame(8, focusBody, { left: 42, top: 122, width: 872, height: 350 });

setText(9, "Evaluate: Share and Learn", "FYF p. 4 Model: Pest Control");
setText(9, "It is more important to be happy than successful.", "How does the model classify each detail?");
setText(9, "STRONGLY AGREE", "DUTIES");
setText(9, "AGREE", "HOURS");
setText(9, "STRONGLY\nDISAGREE", "TOOLS");
setText(9, "DISAGREE", "TRAINING");
setParagraphs(9, "Identify a spokesperson who will summarize your group’s position for the rest of the groups. \nShare and engage in a debate with each other. \nBefore a group shares their next point, they must summarize the point of the group that preceded them.​", [
  { text: "Independent work = Perk (likes working alone)", bullet: "•" },
  { text: "Dealing with insects = Quirk (challenging work)", bullet: "•", spaceBefore: 8 },
  { text: "Emergency calls = Quirk (unpredictable schedule)", bullet: "•", spaceBefore: 8 },
], "13pt");

setText(10, focusTitle, "A Complete Career Table");
setParagraphs(10, focusBody, [
  { text: "Model: Veterinary Technician on FYF p. 5", bold: true },
  { text: "Detail 1: Works with animals in clinics → PERK (values relationships)", bullet: "•" },
  { text: "Detail 2: Evening/weekend emergency shifts → QUIRK (prefers set hours)", bullet: "•" },
  { text: "Detail 3: 2-year associate degree → NEUTRAL (fits future plan)", bullet: "•" },
  { text: "Detail 4: Uses diagnostic lab tools → PERK (likes hands-on tech)", bullet: "•" },
  { text: "Source: Hats & Ladders career card", bold: true, spaceBefore: 14 },
], "19pt");
setFrame(10, focusBody, { left: 42, top: 122, width: 872, height: 350 });

const quickTitle = "Four Corners – Quickwrite";
const quickLeft = "Write down which position you want to take from the list below and explain why:\nStrongly agree\nAgree\nDisagree\nStrongly disagree ";
const quickCenter = "It is more important to be happy than successful.";
const quickWordBank = "Word Bank: \nHappy                            successful\n              Important                                goals\nMoney                            stress\n                            Family                   career\nBalance                       achievement";

setText(11, quickTitle, "Complete Model: Perks & Quirks");
setParagraphs(11, quickLeft, [
  { text: "Career: Veterinary Technician", bold: true },
  { text: "Detail: Works with animals and owners in clinics.", spaceBefore: 12 },
  { text: "My mark: PERK", bold: true, spaceBefore: 12 },
  { text: "Why: I value relationships and have a Building Block in animal care.", spaceBefore: 12 },
], "17pt");
setText(11, quickCenter, "Evidence makes the mark personal.");
setParagraphs(11, quickWordBank, [
  { text: "Source: Hats & Ladders career profile", bold: true },
  { text: "Still verify: required license + current pay", spaceBefore: 12 },
], "15pt");

setText(12, quickTitle, "Non-Model: What Is Missing?");
setParagraphs(12, quickLeft, [
  { text: "“Career: Vet. Detail: Good job. Mark: Perk. Why: I like it.”", bold: true, bullet: "•" },
  { text: "What needs fixing?", bold: true, bullet: "•", spaceBefore: 12 },
  { text: "No specific job duty or work setting", bullet: "•" },
  { text: "No evidence-based personal reason", bullet: "•" },
  { text: "No usable career source", bullet: "•" },
  { text: "Write specific duties, real marks, reasons citing work values, and sources.", bullet: "•", spaceBefore: 12 },
], "17pt");
setText(12, quickCenter, "A label alone is not evidence.");
setParagraphs(12, quickWordBank, [
  { text: "Use the FYF table:", bold: true },
  "CAREER DETAIL",
  "MARK (P / N / Q)",
  "REASON (WHY)",
  "SOURCE",
], "15pt");

setText(13, focusTitle, "FYF Table: Done When");
setParagraphs(13, focusBody, [
  { text: "Your Table 1 on FYF p. 5 has:", bold: true },
  { text: "at least four specific career details", bullet: "✓", spaceBefore: 10 },
  { text: "a P / N / Q mark and personal reason for every detail", bullet: "✓" },
  { text: "the information source clearly named", bullet: "✓" },
  { text: "A second career table is optional.", bold: true, spaceBefore: 14 },
], "24pt");

setText(14, "Skills Check", "Demonstration of Learning");
const verifyShape = textShape(14, "Each week, we will check in on our grades, planners, and goals.\n\nCheck your grades. If you don’t have a grade yet, write “N/A” for “not available.”\nGet your planner out. Answer the questions honestly.\nGet out your goal from last week. Look at it and reflect on your progress.\nCreate a new academic goal. ");
verifyShape.text.set([
  { runs: [{ run: "Demonstration of Learning:", textStyle: { bold: true, fontSize: "18pt" } }] },
  { bulletCharacter: "✓", marginLeft: 22, indent: -12, runs: [{ run: "At least four specific career details", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "✓", marginLeft: 22, indent: -12, runs: [{ run: "A P/N/Q mark and personal reason for every detail", textStyle: { fontSize: "18pt" } }] },
  { bulletCharacter: "✓", marginLeft: 22, indent: -12, runs: [{ run: "Information source clearly named", textStyle: { fontSize: "18pt" } }] },
  { spaceBefore: 18, runs: [{ run: "Check your work before packing up:", textStyle: { bold: true, fontSize: "18pt" } }] },
  { runs: [{ run: "Did you explain WHY each detail is a perk, neutral, or quirk for you?", textStyle: { fontSize: "18pt" } }] },
  { spaceBefore: 18, runs: [{ run: "Return workbooks to the class shelf and close tabs.", textStyle: { fontSize: "18pt" } }] }
]);
verifyShape.frame = { left: 24, top: 115, width: 886, height: 395 };
deleteImage(14);

setText(15, "Exit: Debrief – Initiating Student Ownership in the Classroom", "Wrap-Up: First Week Complete!");
setParagraphs(15, "What was your role in ensuring that this activity was successful? \nIn what ways do you feel more confident as a result of this activity? \nWhat can you do differently next time to ensure that similar activities are even more successful and beneficial?", [
  { text: "Congratulations on completing Week 0!", bold: true },
  { text: "This week you discovered your Core type, work values, and Building Blocks.", spaceBefore: 14 },
  { text: "You completed your My Career Journey reflection and analyzed a career tradeoff.", spaceBefore: 14 },
  { text: "Next week: We launch Cluster 1 — Manufacturing & Robotics!", spaceBefore: 14 },
  { text: "Return workbooks and Chromebooks before dismissal.", bold: true, spaceBefore: 16 },
], "18pt");

const notes = [
  ["Time: 0:00-1:00", "Teacher move: Welcome students and name the single response home: FYF p. 5.", "Student action: Open the workbook to pp. 4-5.", "Look-for: Every student has the correct page or equivalent paper route.", "Recovery/access: Point to the Student Guide response-home box.", "Pivot/trim: Keep setup to one minute.", "[Sources]", "- CCE Day 5 canonical lesson, revised 2026-08-24.", "[/Sources]"],
  ["Time: 1:00-3:00", "Teacher move: Guide materials setup and preview today's three steps.", "Student action: Prepare the workbook, pencil, and approved career source.", "Look-for: Materials are ready before the Do Now discussion.", "Recovery/access: Provide the teacher profile to students without a source.", "Pivot/trim: Start the prompt by minute 3.", "[Sources]", "- CCE Day 5 canonical lesson.", "[/Sources]"],
  ["Time: 3:00-5:00", "Teacher move: Ask whether outdoor Texas-summer work is a perk, neutral, or quirk and take two contrasting reasons.", "Student action: Decide silently, signal with a hand cue, and explain a preference.", "Look-for: Students notice the same fact can receive different marks.", "Recovery/access: Use thumbs up, flat hand, and thumbs down.", "Pivot/trim: Take no more than two shares.", "[Sources]", "- CCE Day 5 Do Now.", "[/Sources]"],
  ["Time: 5:00-8:00", "Teacher move: State the learning target and one-response-home rule.", "Student action: Review the three goals and FYF p. 5 deliverable.", "Look-for: Students can name where they will write.", "Recovery/access: Point directly to the first table on p. 5.", "Pivot/trim: Move to vocabulary by minute 8.", "[Sources]", "- CCE Day 5 Daily Learning Contract.", "[/Sources]"],
  ["Time: 8:00-12:00", "Teacher move: Define perk, neutral, and quirk with the visual hand cues.", "Student action: Repeat the three marks and connect each to a meaning.", "Look-for: Students do not use quirk as a synonym for universally bad.", "Recovery/access: Use the focused word bank and optional home-language equivalents.", "Pivot/trim: Protect the neutral definition.", "[Sources]", "- Find Your Future pp. 4-5.", "[/Sources]"],
  ["Time: 12:00-15:00", "Teacher move: Show how one changing-schedule fact can receive three different marks.", "Student action: Compare the reasons and identify the preference behind each.", "Look-for: Students separate the objective fact from the personal judgment.", "Recovery/access: Read each reason aloud.", "Pivot/trim: Ask one quick check question.", "[Sources]", "- CCE Day 5 guided example.", "[/Sources]"],
  ["Time: 15:00-20:00", "Teacher move: Teach the evidence formula: fact, mark, personal reason, source.", "Student action: Rehearse the optional sentence stem with a partner.", "Look-for: Oral responses name a value or preference.", "Recovery/access: Keep the formula visible during writing.", "Pivot/trim: Call on one pair only.", "[Sources]", "- CCE Day 5 complete-model routine.", "[/Sources]"],
  ["Time: 20:00-25:00", "Teacher move: Identify useful fact types on FYF p. 4 and reject vague labels.", "Student action: Locate a duty, schedule, work-setting, training, or tools fact.", "Look-for: Students can point to a specific career fact.", "Recovery/access: Provide the teacher profile if needed.", "Pivot/trim: Transition to Table 1 at minute 25.", "[Sources]", "- Find Your Future pp. 4-5.", "[/Sources]"],
  ["Time: 25:00 checkpoint (no added minutes)", "Teacher move: Verify that every student has selected a career and opened Table 1.", "Student action: Point to the career name and first row.", "Look-for: Every student is ready to write.", "Recovery/access: Assign the teacher-provided career profile.", "Pivot/trim: Begin the full model immediately.", "[Sources]", "- CCE Day 5 minute-25 checkpoint.", "[/Sources]"],
  ["Time: 25:00-28:00", "Teacher move: Walk through the four-detail Veterinary Technician model.", "Student action: Identify the fact, mark, reason, and source in each row.", "Look-for: Students see that marks are supported, not guessed.", "Recovery/access: Read one row aloud and point to each part.", "Pivot/trim: Highlight the source field.", "[Sources]", "- CCE Day 5 complete model.", "[/Sources]"],
  ["Time: 28:00-31:00", "Teacher move: Zoom in on one complete model row and think aloud about predictable hours.", "Student action: Explain how the preference supports the mark.", "Look-for: Students use because to connect mark and preference.", "Recovery/access: Offer the sentence stem.", "Pivot/trim: Move to the non-model after one share.", "[Sources]", "- CCE Day 5 model row.", "[/Sources]"],
  ["Time: 31:00-33:00", "Teacher move: Show the non-model and ask, 'What information is missing?'", "Student action: Name the missing specific fact, personal reason, or source.", "Look-for: Students reject vague praise as evidence.", "Recovery/access: Point to the four-part formula.", "Pivot/trim: Spend two minutes maximum.", "[Sources]", "- CCE Day 5 non-model.", "[/Sources]"],
  ["Time: 33:00-45:00", "Teacher move: Monitor Table 1 and ask, 'What does the worker actually do, use, study, or experience?'", "Student action: Complete at least four rows with marks, reasons, and a source.", "Look-for: Specific facts and personal work-value connections.", "Recovery/access: Provide word bank, oral rehearsal, and the teacher profile.", "Pivot/trim: At minute 40, students star and rehearse their strongest row.", "[Sources]", "- Find Your Future p. 5.", "- CCE Day 5 independent practice.", "[/Sources]"],
  ["Time: 45:00-48:00", "Teacher move: Run the three-item Done When check and ask one student to finish the reflection stem.", "Student action: Verify four facts, complete reasons, and a named source.", "Look-for: One complete FYF p. 5 table.", "Recovery/access: Teacher checks the strongest starred row first.", "Pivot/trim: Do not add a second submission.", "[Sources]", "- CCE Day 5 Demonstration of Learning.", "[/Sources]"],
  ["Time: 48:00-50:00", "Teacher move: Preview Week 1 and guide the established cleanup routine.", "Student action: Return workbooks and devices to the assigned locations.", "Look-for: FYF p. 5 remains open for a quick scan.", "Recovery/access: Collect equivalent paper tables in the class folder.", "Pivot/trim: Protect the two-minute close.", "[Sources]", "- CCE Day 5 wrap-up.", "[/Sources]"],
];

if (notes.length !== presentation.slides.items.length) throw new Error("Notes/slide count mismatch");
notes.forEach((entry, index) => setNotes(index + 1, entry));

const schedule = [
  { phase: "readiness", start: 0, end: 1, label: "Time: 0:00-1:00" },
  { phase: "readiness", start: 1, end: 3, label: "Time: 1:00-3:00" },
  { phase: "readiness", start: 3, end: 5, label: "Time: 3:00-5:00" },
  { phase: "framework", start: 5, end: 8, label: "Time: 5:00-8:00" },
  { phase: "framework", start: 8, end: 12, label: "Time: 8:00-12:00" },
  { phase: "framework", start: 12, end: 15, label: "Time: 12:00-15:00" },
  { phase: "framework", start: 15, end: 20, label: "Time: 15:00-20:00" },
  { phase: "framework", start: 20, end: 25, label: "Time: 20:00-25:00" },
  { phase: "checkpoint", start: 25, end: 25, label: "Time: 25:00 checkpoint (no added minutes)" },
  { phase: "practice", start: 25, end: 28, label: "Time: 25:00-28:00" },
  { phase: "practice", start: 28, end: 31, label: "Time: 28:00-31:00" },
  { phase: "practice", start: 31, end: 33, label: "Time: 31:00-33:00" },
  { phase: "practice", start: 33, end: 45, label: "Time: 33:00-45:00" },
  { phase: "verify", start: 45, end: 48, label: "Time: 45:00-48:00" },
  { phase: "close", start: 48, end: 50, label: "Time: 48:00-50:00" },
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
if (phaseMinutes.readiness !== 5 || phaseMinutes.framework !== 20 || phaseMinutes.practice !== 20 || phaseMinutes.verify !== 3 || phaseMinutes.close !== 2) {
  throw new Error(`Day 5 phase timing drift: ${JSON.stringify(phaseMinutes)}`);
}

const result = await finalize({ PresentationFile }, presentation, { workspace, outputPath, expectedCount: 15, allow: [/Alternate route/] });
console.log(JSON.stringify(result, null, 2));
