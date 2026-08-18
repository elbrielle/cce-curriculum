// Consolidated read-only gate for the Week 0 daily masters and the generated weekly deck.
//
// Checks each OUTPUT .pptx (not the builders): expected slide count, 16:9 size,
// every slide editable (has text shapes; no whole-slide raster), projected-slide
// language lint, full speaker-note schema, zero "Mr. Lucero"/"ClassLink"/reopen
// wording, and prints SHA-256 + bytes for the manifests.
//
// Usage: node build/decks/qa_week0_decks.mjs [--json out.json]
// Env: CODEX_PRESENTATIONS_RUNTIME_HELPER, RUNTIME_NODE_MODULES

import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import { loadRuntime } from "./lib/slide_kit.mjs";
import { lintSlideText, lintNotes, notesMapFromRecords } from "./lib/slide_lint.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../..");
const derived = path.join(root, "cce-curriculum/resources/avid-reference/source/derived");
const weeklyPath = path.join(root, "cce-curriculum/resources/owner-authenticated-source/weekly-slides/Lucero CCE Week 1 - Classroom Routines and Career Self-Discovery.pptx");

const DECKS = [
  { key: "1sw-wk0-day1-source-grounded-slides", file: path.join(derived, "cce-week1-day1-source-grounded.pptx"), expected: 15 },
  { key: "1sw-wk0-day2-source-grounded-slides", file: path.join(derived, "cce-week1-day2-source-grounded.pptx"), expected: 16 },
  { key: "1sw-wk0-day3-source-grounded-slides", file: path.join(derived, "cce-week1-day3-source-grounded.pptx"), expected: 16 },
  { key: "1sw-wk0-day4-source-grounded-slides", file: path.join(derived, "cce-week1-day4-source-grounded.pptx"), expected: 13 },
  { key: "1sw-wk0-day5-source-grounded-slides", file: path.join(derived, "cce-week1-day5-source-grounded.pptx"), expected: 15 },
  { key: "1sw-wk0-lucero-weekly-slides", file: weeklyPath, expected: 75 },
];
const ALLOW = [/Alternate route/];
const OBSOLETE = [/\bmr\.?\s*lucero\b|\bmister\s+lucero\b/i, /classlink/i, /\b(reopen|re-open|refresh)\b[^.]{0,60}\b(page|onenote|notebook)\b/i];

const runtime = await loadRuntime();
const { FileBlob, PresentationFile } = runtime;
const report = { checked_on: new Date().toISOString().slice(0, 10), decks: [], pass: true };

for (const deck of DECKS) {
  const bytes = await fs.readFile(deck.file);
  const sha256 = crypto.createHash("sha256").update(bytes).digest("hex");
  const presentation = await PresentationFile.importPptx(await FileBlob.load(deck.file));
  const count = presentation.slides.items.length;
  const inspection = await presentation.inspect({ kind: "slide,textbox,shape,table,image,notes", maxChars: 4_000_000 });
  const records = inspection.ndjson.split("\n").filter(Boolean).map((line) => JSON.parse(line));
  const protoSlide = presentation.toProto().slides[0] ?? {};
  const width = protoSlide.widthEmu ? Math.round(protoSlide.widthEmu / 12700) : null; // EMU -> pt
  const height = protoSlide.heightEmu ? Math.round(protoSlide.heightEmu / 12700) : null;
  const sixteenNine = width && height ? Math.abs(width / height - 16 / 9) < 0.01 : null;

  const nonEditable = [];
  for (let n = 1; n <= count; n += 1) {
    const hasText = records.some((r) => r.slide === n && ["textbox", "shape", "table"].includes(r.kind) && String(r.text ?? "").trim());
    if (!hasText) nonEditable.push(n);
  }
  const slideFailures = lintSlideText(records, { allow: ALLOW });
  const noteFailures = lintNotes(notesMapFromRecords(records));
  const obsoleteHits = [];
  for (const r of records) {
    const text = String(r.text ?? "");
    if (!text) continue;
    for (const pattern of OBSOLETE) if (pattern.test(text)) obsoleteHits.push({ slide: r.slide, kind: r.kind, sample: text.slice(0, 80) });
  }
  const problems = [];
  if (count !== deck.expected) problems.push(`slide count ${count} != ${deck.expected}`);
  if (sixteenNine === false) problems.push(`slide size ${width}x${height} is not 16:9`);
  if (nonEditable.length) problems.push(`non-editable slides: ${nonEditable.join(",")}`);
  if (slideFailures.length) problems.push(`slide language: ${JSON.stringify(slideFailures.slice(0, 5))}`);
  if (noteFailures.length) problems.push(`notes schema: ${JSON.stringify(noteFailures.slice(0, 5))}`);
  if (obsoleteHits.length) problems.push(`obsolete wording: ${JSON.stringify(obsoleteHits.slice(0, 5))}`);
  if (problems.length) report.pass = false;
  report.decks.push({ key: deck.key, path: path.relative(root, deck.file), sha256, bytes: bytes.length, slides: count, size: width && height ? `${width}x${height}` : "unknown", editable_slides: count - nonEditable.length, mr_lucero_hits: obsoleteHits.filter((h) => /lucero/i.test(h.sample)).length, problems });
}

const jsonFlag = process.argv.indexOf("--json");
if (jsonFlag !== -1 && process.argv[jsonFlag + 1]) {
  await fs.mkdir(path.dirname(path.resolve(process.argv[jsonFlag + 1])), { recursive: true });
  await fs.writeFile(path.resolve(process.argv[jsonFlag + 1]), JSON.stringify(report, null, 2));
}
for (const d of report.decks) console.log(`${d.problems.length ? "FAIL" : "ok  "} ${d.key} slides=${d.slides} size=${d.size} editable=${d.editable_slides} sha256=${d.sha256.slice(0, 12)}… bytes=${d.bytes}${d.problems.length ? "\n     " + d.problems.join("\n     ") : ""}`);
console.log(report.pass ? "PASS: Week 0 deck gate" : "FAIL: Week 0 deck gate");
if (!report.pass) process.exit(1);
