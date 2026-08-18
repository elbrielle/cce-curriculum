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
const workspace = path.join(root, "tmp/day4-source-clone");
const starterPath = path.join(workspace, "template-starter.pptx");
const outputPath = path.join(root, "cce-curriculum/resources/avid-reference/source/derived/cce-week1-day4-source-grounded.pptx");
const previewDir = path.join(workspace, "final-preview");
const layoutDir = path.join(workspace, "final-layout/final");

const { FileBlob, PresentationFile } = await importRuntimeModule("@oai/artifact-tool");
await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.rm(previewDir, { recursive: true, force: true });
await fs.rm(layoutDir, { recursive: true, force: true });
await fs.mkdir(previewDir, { recursive: true });
await fs.mkdir(layoutDir, { recursive: true });

const presentation = await PresentationFile.importPptx(await FileBlob.load(starterPath));
const initial = await presentation.inspect({ kind: "slide,shape,textbox,image,notes", maxChars: 500_000 });
const records = initial.ndjson.split("\n").filter(Boolean).map((line) => JSON.parse(line));

function recordFor(kind, slide, predicate = () => true) {
  const record = records.find((item) => item.kind === kind && item.slide === slide && predicate(item));
  if (!record) throw new Error(`Missing ${kind} on output slide ${slide}`);
  return record;
}

function setText(slide, before, after) {
  presentation.resolve(recordFor("textbox", slide, (item) => item.text === before).id).text.set(after);
}

function setParagraphs(slide, before, items, fontSize = "20pt") {
  presentation.resolve(recordFor("textbox", slide, (item) => item.text === before).id).text.set(
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

function deleteImage(slide, predicate) {
  presentation.resolve(recordFor("image", slide, predicate).id).delete();
}

function setNotes(slide, lines) {
  presentation.resolve(recordFor("notes", slide).id).setText(lines.join("\n"));
}

setText(1, "Week 1.5", "CCE Day 4");
setText(1, "AVID 2\nMs. Hainlen", "My Career Journey\nCareer Assessment");

setText(2, "Thursday / Friday", "Thursday");

setText(3, "Pencil\nName Tent\nGet ready to share an answer ——> ", "Chromebook + FYF workbook\nOpen your Climber Profile\nOpen Day 2-3 notes\nPrivate response first");
setText(3, "Today’s Lesson\nRead: article\nReview scenarios\nGame", "Today’s Lesson\nRetrieve your evidence\nBuild one career connection\nRevise and submit your reflection");
setText(3, "Discussion\n\nWhat is the perfect amount of pancakes to you?", "Discussion\n\nWhat does your profile know now that it did not know on Day 2?\n\nWrite privately. Share only if you choose.");
deleteImage(3, () => true);
deleteEmptySourceShape(3, "Google Shape;320;p36");
deleteEmptySourceShape(3, "Google Shape;327;p36");

setText(4, "Get out your Paper Crane Notes!", "Open Your Career Evidence");
deleteImage(4, (item) => item.bbox?.[2] > 300 && item.bbox?.[2] < 350);
const notebookImage = presentation.resolve(recordFor("image", 4, (item) => item.bbox?.[2] > 350).id);
notebookImage.frame = { left: 295, top: 132, width: 370, height: 285 };

const reflectionBody = "Seat 4 is writing for the group:\nAs a group, discuss whether each of you was successful in building your crane. What were the reasons for your success or challenges?\nFor those who were successful, what common strategies or approaches do you think helped achieve that success?\nFor those who faced difficulties, what could you have done differently, and what ideas does the group have for improving the process next time?\nHow does this relate to studying and notetaking?\nSeat 5 be prepared to share verbally.";

setText(5, "Reflection Questions", "Gather Five Pieces of Evidence");
setParagraphs(5, reflectionBody, [
  { text: "Point to each source:", bold: true },
  { text: "Core personality + one meaningful phrase", bullet: "•" },
  { text: "Top work values", bullet: "•" },
  { text: "Three Building Blocks + skills", bullet: "•" },
  { text: "Available cluster recommendations", bullet: "•" },
  { text: "Your Day 2 prediction", bullet: "•" },
  { text: "DONE WHEN: everything is open or marked pending. Do not recopy.", bold: true, spaceBefore: 14 },
]);

setText(6, "Reflection Questions", "Complete Model: Evidence → Curiosity");
setParagraphs(6, reflectionBody, [
  { text: "Career: Veterinary Technician", bold: true },
  { text: "My Helper core type fits because I like supporting living things. Relationships is one of my work values. Caring for my dog is a Building Block that has taught me patience.", spaceBefore: 14 },
  { text: "I am curious about this career, but I still need to learn the required education and daily work before deciding whether it fits.", spaceBefore: 14 },
]);

setText(7, "Reflection Questions", "Non-Model: What Is Missing?");
setParagraphs(7, reflectionBody, [
  { text: "“Health Science because it fits me.”", bold: true },
  { text: "What needs fixing?", bold: true, spaceBefore: 14 },
  { text: "Health Science is a cluster, not a career.", bullet: "•" },
  { text: "“Fits me” does not name evidence.", bullet: "•" },
  { text: "Fix it by naming one career, at least two pieces of evidence, and one thing you still need to learn.", spaceBefore: 14 },
]);

setText(8, "Reflection Questions", "How Your Reflection Is Scored");
setParagraphs(8, reflectionBody, [
  { text: "Complete evidence", bold: true },
  "All eight sections answer the prompt. Items 1-5 match an open source.",
  { text: "Accurate self-awareness", bold: true, spaceBefore: 14 },
  "Your words match your actual results. Uncertainty is allowed.",
  { text: "Supported career connection", bold: true, spaceBefore: 14 },
  "Item 6 names a career, uses evidence, and says what is still unknown.",
]);

setText(9, "Reflection Questions", "Work Chunk 1: Items 1-5");
setParagraphs(9, reflectionBody, [
  { text: "Use the source that is already open.", bold: true },
  { text: "Core personality result + phrase", bullet: "•" },
  { text: "Top work values", bullet: "•" },
  { text: "Three Building Blocks + skills", bullet: "•" },
  { text: "Available cluster recommendations", bullet: "•" },
  { text: "Original Day 2 prediction", bullet: "•" },
  { text: "Do not answer from memory. Mark one missing result pending.", bold: true, spaceBefore: 14 },
]);

setText(10, "Reflection Questions", "Work Chunk 2: Item 6");
setParagraphs(10, reflectionBody, [
  { text: "Name a career, not only a cluster. Write at least two evidence-based sentences.", bold: true },
  { text: "Use this frame if helpful:", bold: true, spaceBefore: 14 },
  "I am curious about ____ because my ____ result says ____ and my ____ shows ____. I still need to learn ____ before deciding whether it fits.",
]);

setText(11, "Reflection Questions", "Work Chunk 3: Items 7-8");
setParagraphs(11, reflectionBody, [
  { text: "Item 7: Name one surprise, question, or result you want to understand better.", bold: true },
  { text: "Item 8: Name three support roles or people.", bold: true, spaceBefore: 14 },
  { text: "Privacy choices: a role, initials, a trusted person, or a fictional support role.", spaceBefore: 14 },
  { text: "Full names and personal relationships are never required publicly.", bold: true, spaceBefore: 14 },
]);

setText(12, "Reflection Questions", "Self-Check + One Visible Revision");
setParagraphs(12, reflectionBody, [
  { text: "Check your reflection once:", bold: true },
  { text: "All eight sections are complete or one missing result is marked pending.", bullet: "✓" },
  { text: "Item 6 names a career and uses two pieces of evidence.", bullet: "✓" },
  { text: "Item 8 includes three support roles or people.", bullet: "✓" },
  { text: "Make one visible revision: add evidence, make a sentence clearer, or name what is still unknown.", bold: true, spaceBefore: 14 },
]);

setText(13, "Reflection Questions", "Submit Your Reflection Once");
setParagraphs(13, reflectionBody, [
  { text: "Choose one way to turn it in:", bold: true },
  { text: "FILE: upload the two-page reflection as one file.", bullet: "•" },
  { text: "TEXT: use exact labels 1-8.", bullet: "•" },
  { text: "PAPER: hand in one labeled paper.", bullet: "•" },
  { text: "Turn in only this reflection. Do not submit your Day 2-3 pages.", bold: true, spaceBefore: 14 },
  { text: "Missing one result? Mark pending and finish it Friday.", spaceBefore: 10 },
]);

const notes = [
  ["Time: 0:00-0:30", "Teacher move: Open the lesson and name the purpose: today turns three saved inputs into one reflection.", "Student action: Open the Climber Profile, FYF workbook, and Day 2-3 notes.", "Look-for: Students know this is reflection and submission, not another assessment.", "Recovery/access: Read the subtitle aloud and point to the three evidence sources.", "Pivot/trim: Do not cut orientation; keep it under 30 seconds.", "[Sources]", "- Jenna Hainlen, AVID Week 1.5 slide 1, cover layout; owner-authorized reuse.", "- CCE Day 4 canonical lesson, accessed 2026-08-15.", "[/Sources]"],
  ["Time: 0:30-1:00", "Teacher move: Use as the Thursday divider while students open materials.", "Student action: Finish opening the required sources.", "Look-for: Profile, workbook, and notes are visible.", "Recovery/access: Point to the open-materials list in the Student Guide as needed.", "Pivot/trim: Keep this transition under 30 seconds.", "[Sources]", "- Jenna Hainlen, AVID Week 1.5 slide 16, day-divider layout.", "[/Sources]"],
  ["Time: 1:00-5:00", "Teacher move: Run the private profile warm-up, then preview the four lesson moves. Do not require public disclosure.", "Student action: Privately answer what the profile knows now that it did not know on Day 2.", "Look-for: Students identify one new result or mark a result pending.", "Recovery/access: Accept a word, phrase, typed response, or oral rehearsal.", "Pivot/trim: If entry takes longer, sample no more than two voluntary answers.", "[Sources]", "- Jenna Hainlen, AVID Week 1.5 slide 17, Welcome/Get Ready/Today's Lesson choreography.", "- CCE Day 4 profile warm-up.", "[/Sources]"],
  ["Time: 5:00-9:00", "Teacher move: Preserve Jenna's retrieval move: students open existing notes before being asked to apply them. Check access, not neatness.", "Student action: Open their core type, work values, Building Blocks, recommendations, and Day 2 prediction.", "Look-for: Students point to existing evidence rather than copying it into a new holding sheet.", "Recovery/access: Pair a student with the exact source location; allow pending for one unavailable result.", "Pivot/trim: If the platform is slow, use saved notebook/FYF evidence and keep moving.", "[Sources]", "- Jenna Hainlen, AVID Week 1.5 slide 9, retrieve-notes choreography and retained notebook visual; owner-authorized reuse.", "- CCE Day 4 gather-the-evidence step.", "[/Sources]"],
  ["Time: 9:00-13:00", "Teacher move: Read the five-item checklist and make one active-monitoring lap.", "Student action: Point to each source and mark any missing item pending.", "Look-for: By minute 13, every student has all sources open or a visible pending mark.", "Recovery/access: Read the five labels aloud; do not require recopying.", "Pivot/trim: Record access problems for Friday rather than troubleshooting all period.", "[Sources]", "- Jenna Hainlen, AVID Week 1.5 slide 13, group reflection/action frame.", "- H&L Climber Profile outputs from Days 2-3; district-licensed, authenticated use only.", "[/Sources]"],
  ["Time: 13:00-15:00", "Teacher move: Read the complete model once. Ask students to point to the type, value, Building Block, career, and unknown.", "Student action: Identify how evidence supports the career curiosity.", "Look-for: Students can distinguish a career from a cluster.", "Recovery/access: Keep the model projected and read the evidence nouns aloud.", "Pivot/trim: Protect this model; shorten student discussion instead.", "[Sources]", "- CCE Day 4 complete model.", "- Jenna Hainlen, AVID Week 1.5 slide 13, reflect-and-apply choreography.", "[/Sources]"],
  ["Time: 15:00-16:00", "Teacher move: Show the non-model and elicit the two missing pieces before revealing the fix.", "Student action: Name that Health Science is a cluster and fits me is unsupported.", "Look-for: Students use career and evidence precisely.", "Recovery/access: Offer the frame: A stronger answer would name ___ and evidence from ___.", "Pivot/trim: If time is tight, state both fixes in 30 seconds.", "[Sources]", "- CCE Day 4 non-model.", "- Jenna Hainlen, AVID Week 1.5 slide 13, reflection frame.", "[/Sources]"],
  ["Time: 16:00-18:00", "Teacher move: Translate the 12-point rubric into three student checks without adding a second assignment.", "Student action: Locate which section of the reflection shows each criterion.", "Look-for: Students understand uncertainty can be accurate self-awareness.", "Recovery/access: Read each heading and one example; keep the rubric available in the Student Guide.", "Pivot/trim: Protect criteria; shorten explanation to one example per heading.", "[Sources]", "- CCE Day 4 12-point student rubric.", "- Jenna Hainlen, AVID Week 1.5 slide 13, reflection frame.", "[/Sources]"],
  ["Time: 18:00-25:00", "Teacher move: Launch items 1-5. Lap 1 checks that answers match an open source rather than memory.", "Student action: Complete items 1-5 from their saved evidence.", "Look-for: Exact result language and pending marks where needed.", "Recovery/access: Allow speech-to-text, dictation, or bilingual support; do not change the evidence requirement.", "Pivot/trim: Students with one missing result complete every independent item.", "[Sources]", "- CCE Day 4 work chunk, items 1-5.", "- H&L Climber Profile outputs from Days 2-3; district-licensed, authenticated use only.", "[/Sources]"],
  ["Time: 25:00-33:00", "Teacher move: Launch item 6 and make Lap 2. If one third stalls, annotate one anonymous example once.", "Student action: Name one career and connect it to at least two pieces of evidence.", "Look-for: A career, two evidence-based sentences, and one remaining question.", "Recovery/access: Keep the complete sentence frame visible; accept oral rehearsal before writing.", "Pivot/trim: Do not repeat the explanation desk by desk; pause once for a whole-group repair.", "[Sources]", "- CCE Day 4 item 6 criteria and complete model.", "- Jenna Hainlen, AVID Week 1.5 slide 13, reflect-and-apply choreography.", "[/Sources]"],
  ["Time: 33:00-40:00", "Teacher move: Launch items 7-8 and make Lap 3. State the privacy routes aloud.", "Student action: Record one surprise/question and three support roles or people.", "Look-for: Three supports; roles, initials, trusted people, or fictional roles all count.", "Recovery/access: Never require full names or public disclosure of relationships.", "Pivot/trim: If time is short, protect item 8 and let item 7 be one sentence.", "[Sources]", "- Find Your Future p. 22, Building a Career Community; district-licensed, authenticated use only.", "- CCE Day 4 privacy rule.", "[/Sources]"],
  ["Time: 40:00-46:00", "Teacher move: Ask students to use the rubric and make one visible revision. Verify change, not neatness.", "Student action: Self-check and revise one response.", "Look-for: Added evidence, clearer sentence, corrected career/cluster label, or named unknown.", "Recovery/access: Speech-to-text, dictation to an adult, bilingual support, or oral rehearsal may support the writing.", "Pivot/trim: Protect one revision even if only three minutes remain.", "[Sources]", "- CCE Day 4 self-check and revise step.", "- Jenna Hainlen, AVID Week 1.5 slide 13, reflection choreography.", "[/Sources]"],
  ["Time: 46:00-50:00", "Teacher move: Verify one approved route and repeat the exact grading language: Minor 1, not a Major. Store it for later retrieval.", "Student action: Upload one file, use exact labels 1-8 in text, or hand in one labeled paper.", "Look-for: One submission only; no duplicate notebook page or exit ticket.", "Recovery/access: A student missing one result marks pending and uses Friday catch-up before scoring.", "Pivot/trim: Protect submission confirmation. Cut any whole-group share.", "[Sources]", "- CCE Day 4 Demonstration of Learning and submission routes.", "- Jenna Hainlen, AVID Week 1.5 slide 13, reflection/close frame.", "[/Sources]"],
];

if (notes.length !== presentation.slides.items.length) throw new Error("Notes/slide count mismatch");
notes.forEach((entry, index) => setNotes(index + 1, entry));

const minutes = [0.5, 0.5, 4, 4, 4, 2, 1, 2, 7, 8, 7, 6, 4];
if (minutes.reduce((sum, value) => sum + value, 0) !== 50) throw new Error("Day 4 timing does not total 50 minutes");

const result = await finalize({ PresentationFile }, presentation, { workspace, outputPath, expectedCount: 13, allow: [] });
console.log(JSON.stringify(result, null, 2));
