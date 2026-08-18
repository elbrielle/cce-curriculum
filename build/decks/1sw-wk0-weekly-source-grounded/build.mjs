// Ms. Lucero's combined Week 1 teaching deck, GENERATED from the five daily masters.
//
// Every slide is copied at the object level (presentation proto merge), so the
// weekly deck stays fully editable in PowerPoint and Google Slides. Nothing is
// rasterized. The daily decks remain the authoritative review units; edit them and
// rebuild this file. Teacher-specific pacing lives ONLY in speaker notes here
// (see LUCERO_NOTES_OVERLAY), never on the slide canvas.

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadRuntime } from "../lib/slide_kit.mjs";
import { lintSlideText, lintNotes, notesMapFromRecords } from "../lib/slide_lint.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../../..");
const dailyRoot = path.join(root, "cce-curriculum/resources/avid-reference/source/derived");
const outputPath = path.join(
  root,
  "cce-curriculum/resources/owner-authenticated-source/weekly-slides/Lucero CCE Week 1 - Classroom Routines and Career Self-Discovery.pptx",
);
const workspace = path.join(root, "tmp/cce-week1-weekly-source-grounded");
const previewDir = path.join(workspace, "final-preview");

// Daily masters in Monday-Friday order with their expected slide counts.
export const DAILY_FILES = [
  ["Monday", "cce-week1-day1-source-grounded.pptx", 15],
  ["Tuesday", "cce-week1-day2-source-grounded.pptx", 16],
  ["Wednesday", "cce-week1-day3-source-grounded.pptx", 16],
  ["Thursday", "cce-week1-day4-source-grounded.pptx", 13],
  ["Friday", "cce-week1-day5-source-grounded.pptx", 15],
];
const EXPECTED_TOTAL = DAILY_FILES.reduce((sum, [, , count]) => sum + count, 0);

// Owner-specific pacing notes keyed by "Day:slide" (1-based daily slide number).
// Canvas text is never changed here; these lines are appended to the speaker notes.
const LUCERO_NOTES_OVERLAY = {
  "Monday:14": [
    "Lucero pacing (observed 2026-08-17): Monday ended after device routines, OneNote navigation, and the first goal sentence; most students did not reach the plan fields. Record the last field reached; do not distribute a second goal page.",
  ],
  "Tuesday:2": [
    "Lucero pacing: if the class did not finish Monday's goal page, take up to five minutes from the Discover Your Core block here to finish only the missing fields on the same page. Do not require a reopen/autosave test.",
  ],
  "Tuesday:8": [
    "Lucero note (2026-08-18): Hats & Ladders was unavailable in class on Tuesday. If it is still down, use the provisional-type route (slides 4-6) and protect Friday catch-up; do not switch sign-in methods.",
  ],
};

const runtime = await loadRuntime();
const { FileBlob, Presentation, PresentationFile } = runtime;
await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.rm(previewDir, { recursive: true, force: true });
await fs.mkdir(previewDir, { recursive: true });

// Rewrite the path-based part ids so five decks can share one package.
function prefixPartIds(value, tag) {
  if (value == null || typeof value !== "object") return;
  if (ArrayBuffer.isView(value) || value instanceof ArrayBuffer) return;
  const rewrite = (text) => text
    .replace(/^\/ppt\/slideLayouts\//, `/ppt/slideLayouts/${tag}`)
    .replace(/^\/ppt\/slideMasters\//, `/ppt/slideMasters/${tag}`)
    .replace(/^\/ppt\/media\//, `/ppt/media/${tag}`);
  if (Array.isArray(value)) {
    for (let index = 0; index < value.length; index += 1) {
      if (typeof value[index] === "string") value[index] = rewrite(value[index]);
      else prefixPartIds(value[index], tag);
    }
    return;
  }
  for (const key of Object.keys(value)) {
    const item = value[key];
    if (typeof item === "string") value[key] = rewrite(item);
    else prefixPartIds(item, tag);
  }
}

let merged = null;
const provenance = [];
let weeklyIndex = 0;

for (let dayIndex = 0; dayIndex < DAILY_FILES.length; dayIndex += 1) {
  const [dayName, filename, expectedCount] = DAILY_FILES[dayIndex];
  const dailyPath = path.join(dailyRoot, filename);
  const daily = await PresentationFile.importPptx(await FileBlob.load(dailyPath));
  if (daily.slides.items.length !== expectedCount) {
    throw new Error(`${filename} has ${daily.slides.items.length} slides; expected ${expectedCount}`);
  }
  const proto = daily.toProto();
  const tag = `d${dayIndex + 1}-`;
  if (merged === null) {
    merged = proto;
  } else {
    prefixPartIds(proto, tag);
    const fontNames = new Set(merged.fonts.map((font) => font.name));
    for (const font of proto.fonts) if (!fontNames.has(font.name)) { merged.fonts.push(font); fontNames.add(font.name); }
    merged.layouts.push(...proto.layouts);
    merged.images.push(...proto.images);
    for (const slide of proto.slides) { slide.id = `${tag}${slide.id}`; merged.slides.push(slide); }
  }
  for (let slideIndex = 0; slideIndex < expectedCount; slideIndex += 1) {
    weeklyIndex += 1;
    provenance.push({ weeklySlide: weeklyIndex, day: dayName, dailySlide: slideIndex + 1, source: filename });
  }
}
merged.slides.forEach((slide, index) => { slide.index = index; });
if (merged.slides.length !== EXPECTED_TOTAL) throw new Error(`Merged ${merged.slides.length} slides; expected ${EXPECTED_TOTAL}`);

const weekly = Presentation.load(merged);

// Append the owner pacing overlay to speaker notes (canvas untouched).
for (const record of provenance) {
  const extra = LUCERO_NOTES_OVERLAY[`${record.day}:${record.dailySlide}`];
  if (!extra) continue;
  const slide = weekly.slides.items[record.weeklySlide - 1];
  const inspection = await weekly.inspect({ kind: "notes", target: undefined, maxChars: 200_000 });
  const current = inspection.ndjson.split("\n").filter(Boolean).map((line) => JSON.parse(line)).find((row) => row.slide === record.weeklySlide)?.text ?? "";
  const withOverlay = current.replace("[Sources]", `${extra.join("\n")}\n[Sources]`);
  if (withOverlay === current) throw new Error(`Weekly slide ${record.weeklySlide} notes lack a [Sources] anchor for the overlay`);
  slide.speakerNotes.textFrame.setText(withOverlay);
  slide.speakerNotes.setVisible(true);
}

// Gate: every slide editable (has text shapes), lint clean, notes schema complete, honorific clean.
const inspection = await weekly.inspect({ kind: "slide,textbox,shape,table,image,notes", maxChars: 4_000_000 });
const records = inspection.ndjson.split("\n").filter(Boolean).map((line) => JSON.parse(line));
const slideFailures = lintSlideText(records, { allow: [/Alternate route/] });
const noteFailures = lintNotes(notesMapFromRecords(records));
const nonEditable = [];
for (let n = 1; n <= EXPECTED_TOTAL; n += 1) {
  const hasText = records.some((r) => r.slide === n && ["textbox", "shape", "table"].includes(r.kind) && String(r.text ?? "").trim());
  if (!hasText) nonEditable.push(n);
}
if (slideFailures.length || noteFailures.length || nonEditable.length) {
  throw new Error(`Weekly gate failed\n${JSON.stringify({ slideFailures, noteFailures, nonEditable }, null, 2)}`);
}

for (let index = 0; index < weekly.slides.items.length; index += 1) {
  const png = await weekly.export({ slide: weekly.slides.items[index], format: "png", scale: 1 });
  await fs.writeFile(path.join(previewDir, `weekly-slide-${String(index + 1).padStart(2, "0")}.png`), Buffer.from(await png.arrayBuffer()));
}
await fs.writeFile(path.join(workspace, "final.inspect.ndjson"), inspection.ndjson);
await fs.writeFile(path.join(workspace, "slide-provenance.json"), JSON.stringify(provenance, null, 2));
const pptx = await PresentationFile.exportPptx(weekly);
await pptx.save(outputPath);

console.log(JSON.stringify({ outputPath, slideCount: weekly.slides.items.length, editableSlides: EXPECTED_TOTAL - nonEditable.length, previewDir }, null, 2));
