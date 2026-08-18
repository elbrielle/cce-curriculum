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
const dailyRoot = path.join(root, "cce-curriculum/resources/avid-reference/source/derived");
const outputPath = path.join(
  root,
  "cce-curriculum/resources/owner-authenticated-source/weekly-slides/Lucero CCE Week 1 - Classroom Routines and Career Self-Discovery.pptx",
);
const workspace = path.join(root, "tmp/cce-week1-weekly-source-grounded");
const previewDir = path.join(workspace, "final-preview");

const dailyFiles = [
  ["Monday", "cce-week1-day1-source-grounded.pptx", 15],
  ["Tuesday", "cce-week1-day2-source-grounded.pptx", 16],
  ["Wednesday", "cce-week1-day3-source-grounded.pptx", 16],
  ["Thursday", "cce-week1-day4-source-grounded.pptx", 13],
  ["Friday", "cce-week1-day5-source-grounded.pptx", 15],
];

const { FileBlob, Presentation, PresentationFile } = await importRuntimeModule("@oai/artifact-tool");
await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

const weekly = Presentation.create({ slideSize: { width: 960, height: 540 } });
const provenance = [];
let weeklySlideNumber = 0;

function normalizeNotesSchema(notes) {
  return notes
    .replace(/^Timing:/m, "Time:")
    .replace(/^Students:/m, "Student action:")
    .replace(/^Support:/m, "Recovery/access:")
    .replace(/^Pivot\/trim\/recovery:/m, "Pivot/trim:");
}

for (const [dayName, filename, expectedCount] of dailyFiles) {
  const dailyPath = path.join(dailyRoot, filename);
  const daily = await PresentationFile.importPptx(await FileBlob.load(dailyPath));
  if (daily.slides.items.length !== expectedCount) {
    throw new Error(`${filename} has ${daily.slides.items.length} slides; expected ${expectedCount}`);
  }
  const notesInspection = await daily.inspect({ kind: "notes", maxChars: 1_000_000 });
  const notesBySlide = new Map(
    notesInspection.ndjson
      .split("\n")
      .filter(Boolean)
      .map((line) => JSON.parse(line))
      .map((record) => [record.slide, record.text ?? ""]),
  );

  for (let index = 0; index < daily.slides.items.length; index += 1) {
    const dailySlide = daily.slides.items[index];
    const dailyNumber = index + 1;
    const notes = normalizeNotesSchema(notesBySlide.get(dailyNumber) ?? "");
    const requiredNotesLabels = ["Time:", "Teacher move:", "Student action:", "Look-for:", "Pivot/trim:", "Recovery/access:", "[Sources]", "[/Sources]"];
    if (!notes.trim() || requiredNotesLabels.some((label) => !notes.includes(label))) {
      throw new Error(`${filename} slide ${dailyNumber} is missing the full speaker-note schema`);
    }

    const rendered = await daily.export({ slide: dailySlide, format: "png", scale: 2 });
    const renderedBytes = Buffer.from(await rendered.arrayBuffer());
    if (renderedBytes.length === 0) {
      throw new Error(`${filename} slide ${dailyNumber} rendered to zero bytes`);
    }
    const weeklySlide = weekly.slides.add();
    weeklySlide.images.add({
      blob: renderedBytes,
      contentType: "image/png",
      alt: `${dayName} daily master slide ${dailyNumber}`,
      fit: "fill",
      position: { left: 0, top: 0, width: 960, height: 540 },
    });
    weeklySlide.speakerNotes.textFrame.setText(notes);
    weeklySlide.speakerNotes.setVisible(true);

    weeklySlideNumber += 1;
    const preview = await weekly.export({ slide: weeklySlide, format: "png", scale: 1 });
    await fs.writeFile(
      path.join(previewDir, `weekly-slide-${String(weeklySlideNumber).padStart(2, "0")}.png`),
      Buffer.from(await preview.arrayBuffer()),
    );
    provenance.push({ weeklySlide: weeklySlideNumber, day: dayName, dailySlide: dailyNumber, source: filename });
  }
}

if (weekly.slides.items.length !== 75) {
  throw new Error(`Weekly deck has ${weekly.slides.items.length} slides; expected 75`);
}

const inspection = await weekly.inspect({ kind: "slide,image,notes", maxChars: 2_000_000 });
await fs.writeFile(path.join(workspace, "final.inspect.ndjson"), inspection.ndjson);
await fs.writeFile(path.join(workspace, "slide-provenance.json"), JSON.stringify(provenance, null, 2));
const montage = await weekly.export({ format: "png", montage: true, scale: 1 });
await fs.writeFile(path.join(workspace, "final-montage.png"), Buffer.from(await montage.arrayBuffer()));
const pptx = await PresentationFile.exportPptx(weekly);
await pptx.save(outputPath);

console.log(JSON.stringify({ outputPath, slideCount: weekly.slides.items.length, previewDir }, null, 2));
