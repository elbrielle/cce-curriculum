// Shared slide kit for the Week 0 daily projection decks.
//
// Every helper draws EDITABLE shapes (no rasterized slides). Slide text is
// student-facing; teacher language goes into speaker notes via `notes()`.
// Runtime: Codex presentations `@oai/artifact-tool`, loaded through
// CODEX_PRESENTATIONS_RUNTIME_HELPER + RUNTIME_NODE_MODULES (see plan note).

import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { lintSlideText, lintNotes, notesMapFromRecords } from "./slide_lint.mjs";

export const CANVAS = { width: 960, height: 540 };
export const COLORS = {
  bg: "#C9D0EF",
  ink: "#202331",
  purple: "#5A2D91",
  purpleSoft: "#6350A8",
  card: "#FFFFFF",
  cardLine: "#8390C4",
  gold: "#FFD357",
  goldLine: "#A86600",
  goldInk: "#553400",
  doneFill: "#FFF4C5",
  doneLine: "#D69B00",
  doneInk: "#7A4A00",
  green: "#2E7D32",
  greenSoft: "#E6F2E7",
  teal: "#1F617A",
};
export const FONT = "Aptos";

export async function loadRuntime() {
  const helperPath = process.env.CODEX_PRESENTATIONS_RUNTIME_HELPER;
  if (!helperPath) throw new Error("Set CODEX_PRESENTATIONS_RUNTIME_HELPER to the presentations runtime_helpers.mjs path.");
  if (!process.env.RUNTIME_NODE_MODULES) throw new Error("Set RUNTIME_NODE_MODULES to the Codex runtime node_modules path.");
  const { importRuntimeModule } = await import(pathToFileURL(path.resolve(helperPath)).href);
  const artifactTool = await importRuntimeModule("@oai/artifact-tool");
  return { ...artifactTool, importRuntimeModule };
}

export function normalizeText(value) {
  return String(value ?? "").replace(/[ ​]/g, " ").replace(/\s+/g, " ").trim();
}

/** Open a starter deck and return the presentation plus text-matching helpers. */
export async function openStarter(runtime, starterPath) {
  const { FileBlob, PresentationFile } = runtime;
  const presentation = await PresentationFile.importPptx(await FileBlob.load(starterPath));
  const initial = await presentation.inspect({ kind: "slide,textbox,image,notes", maxChars: 800_000 });
  const records = initial.ndjson.split("\n").filter(Boolean).map((line) => JSON.parse(line));
  const recordFor = (kind, slide, predicate = () => true) => {
    const record = records.find((item) => item.kind === kind && item.slide === slide && predicate(item));
    if (!record) throw new Error(`Missing ${kind} on starter slide ${slide}`);
    return record;
  };
  const textbox = (slide, text) => {
    const target = normalizeText(text);
    return presentation.resolve(recordFor("textbox", slide, (item) => normalizeText(item.text) === target).id);
  };
  const setText = (slide, before, after) => textbox(slide, before).text.set(after);
  const replaceOnlyImage = async (slide, filePath, alt, fit = "contain") => {
    const image = presentation.resolve(recordFor("image", slide).id);
    const keep = {
      frame: image.frame, geometry: image.geometry, borderRadius: image.borderRadius, rotation: image.rotation,
      flipHorizontal: image.flipHorizontal, flipVertical: image.flipVertical, lockAspectRatio: image.lockAspectRatio,
    };
    image.replace({ blob: await fs.readFile(filePath), contentType: "image/png", alt, fit });
    image.frame = keep.frame; image.fit = fit; image.crop = { left: 0, top: 0, right: 0, bottom: 0 };
    image.geometry = keep.geometry; image.borderRadius = keep.borderRadius; image.rotation = keep.rotation;
    image.flipHorizontal = keep.flipHorizontal; image.flipVertical = keep.flipVertical; image.lockAspectRatio = keep.lockAspectRatio;
  };
  return { presentation, records, recordFor, textbox, setText, replaceOnlyImage };
}

export function slideAt(presentation, number) {
  const slide = presentation.slides.items[number - 1];
  if (!slide) throw new Error(`Slide ${number} does not exist`);
  return slide;
}

export function addText(slide, text, position, style = {}) {
  const shape = slide.shapes.add({ geometry: "textbox", name: style.name, position, fill: "none", line: { style: "solid", fill: "none", width: 0 } });
  shape.text = text;
  shape.text.style = {
    fontSize: style.fontSize ?? 20,
    bold: style.bold ?? false,
    color: style.color ?? COLORS.ink,
    fontFamily: FONT,
    ...(style.alignment ? { alignment: style.alignment } : {}),
  };
  return shape;
}

export function box(slide, position, fill, line = COLORS.cardLine, radius = "rounded-xl", name) {
  return slide.shapes.add({ geometry: "roundRect", name, position, fill, line: { style: "solid", fill: line, width: 1 }, borderRadius: radius });
}

/** Clear a starter slide and draw the shared header (kicker pill + title). */
export function cover(slide, title, kicker) {
  [...slide.images.items].forEach((image) => image.delete());
  slide.shapes.deleteAll();
  slide.shapes.add({ geometry: "rect", name: "background", position: { left: 0, top: 0, width: CANVAS.width, height: CANVAS.height }, fill: COLORS.bg, line: { style: "solid", fill: COLORS.bg, width: 0 } });
  const pill = box(slide, { left: 28, top: 22, width: 250, height: 30 }, COLORS.gold, COLORS.goldLine, "rounded-full", "kicker");
  pill.text = kicker;
  pill.text.style = { fontSize: 12, bold: true, color: COLORS.goldInk, fontFamily: FONT, alignment: "center" };
  addText(slide, title, { left: 56, top: 60, width: 860, height: 52 }, { fontSize: 30, bold: true, name: "title" });
  return slide;
}

function doneBanner(slide, text, position = { left: 150, top: 440, width: 660, height: 60 }) {
  box(slide, position, COLORS.doneFill, COLORS.doneLine, "rounded-lg", "done-when");
  addText(slide, `DONE WHEN: ${text}`, { left: position.left + 20, top: position.top + 12, width: position.width - 40, height: position.height - 20 }, { fontSize: 18, bold: true });
}

/** Screenshot slide: WHAT YOU SEE / DO THIS / DONE WHEN beside a real capture. */
export async function guidedScreen(slide, config) {
  cover(slide, config.title, config.kicker);
  box(slide, { left: 28, top: 122, width: 330, height: 380 }, COLORS.card, COLORS.cardLine, "rounded-xl", "text-panel");
  addText(slide, "WHAT YOU SEE", { left: 48, top: 138, width: 290, height: 22 }, { fontSize: 12, bold: true, color: COLORS.purpleSoft });
  addText(slide, config.screen, { left: 48, top: 160, width: 292, height: 66 }, { fontSize: 17, bold: true });
  addText(slide, "DO THIS", { left: 48, top: 230, width: 290, height: 22 }, { fontSize: 12, bold: true, color: COLORS.purpleSoft });
  addText(slide, config.action, { left: 48, top: 252, width: 292, height: 124 }, { fontSize: config.action.length > 150 ? 15 : 17 });
  box(slide, { left: 46, top: 384, width: 294, height: 96 }, COLORS.doneFill, COLORS.doneLine, "rounded-lg", "done-when");
  addText(slide, "DONE WHEN", { left: 62, top: 394, width: 250, height: 22 }, { fontSize: 12, bold: true, color: COLORS.doneInk });
  addText(slide, config.done, { left: 62, top: 416, width: 262, height: 60 }, { fontSize: 15, bold: true });
  box(slide, { left: 394, top: 122, width: 538, height: 380 }, COLORS.card, COLORS.cardLine, "rounded-xl", "image-panel");
  slide.images.add({ blob: await fs.readFile(config.image), contentType: "image/png", alt: config.alt, fit: config.fit ?? "contain", position: { left: 410, top: 138, width: 506, height: 348 } });
  const arrow = slide.shapes.add({ geometry: "rightArrow", name: "callout-arrow", position: { left: 344, top: 273, width: 62, height: 42 }, fill: COLORS.gold, line: { style: "solid", fill: COLORS.goldLine, width: 1 } });
  arrow.text = config.callout ?? "";
  arrow.text.style = { fontSize: 10, bold: true, color: COLORS.goldInk, fontFamily: FONT, alignment: "center" };
  return slide;
}

/** Plain direction slide with one job and a completion cue. */
export function guidedText(slide, config) {
  cover(slide, config.title, config.kicker);
  box(slide, { left: 70, top: 130, width: 820, height: 290 }, COLORS.card, COLORS.cardLine, "rounded-xl", "body-panel");
  addText(slide, config.body, { left: 100, top: 156, width: 760, height: 244 }, { fontSize: config.bodySize ?? 24 });
  doneBanner(slide, config.done);
  return slide;
}

/** As You Enter: materials on the left, Do Now on the right. */
export function doNow(slide, config) {
  cover(slide, config.title ?? "As You Enter", config.kicker);
  box(slide, { left: 28, top: 122, width: 300, height: 380 }, COLORS.card, COLORS.cardLine, "rounded-xl", "get-ready-panel");
  addText(slide, "GET READY", { left: 48, top: 138, width: 260, height: 22 }, { fontSize: 12, bold: true, color: COLORS.purpleSoft });
  addText(slide, config.materials.map((m) => `• ${m}`).join("\n"), { left: 48, top: 164, width: 266, height: 320 }, { fontSize: 17 });
  box(slide, { left: 350, top: 122, width: 582, height: 380 }, COLORS.card, COLORS.cardLine, "rounded-xl", "do-now-panel");
  addText(slide, "DO NOW", { left: 372, top: 138, width: 300, height: 22 }, { fontSize: 12, bold: true, color: COLORS.purpleSoft });
  addText(slide, config.prompt, { left: 372, top: 164, width: 540, height: 150 }, { fontSize: 22, bold: true });
  if (config.stem) addText(slide, config.stem, { left: 372, top: 318, width: 540, height: 60 }, { fontSize: 20, color: COLORS.teal });
  box(slide, { left: 366, top: 392, width: 550, height: 90 }, COLORS.doneFill, COLORS.doneLine, "rounded-lg", "done-when");
  addText(slide, "DONE WHEN", { left: 384, top: 400, width: 250, height: 22 }, { fontSize: 12, bold: true, color: COLORS.doneInk });
  addText(slide, config.done, { left: 384, top: 422, width: 516, height: 56 }, { fontSize: 16, bold: true });
  return slide;
}

/** Today: student objective + TEKS chip + numbered agenda. */
export function agenda(slide, config) {
  cover(slide, config.title ?? "Today", config.kicker);
  box(slide, { left: 28, top: 122, width: 440, height: 380 }, COLORS.card, COLORS.cardLine, "rounded-xl", "objective-panel");
  addText(slide, "I CAN", { left: 48, top: 138, width: 300, height: 22 }, { fontSize: 12, bold: true, color: COLORS.purpleSoft });
  addText(slide, config.objective, { left: 48, top: 164, width: 404, height: 200 }, { fontSize: 22, bold: true });
  if (config.teks) {
    const chip = box(slide, { left: 48, top: 430, width: 396, height: 44 }, COLORS.greenSoft, COLORS.green, "rounded-lg", "teks-chip");
    chip.text = config.teks;
    chip.text.style = { fontSize: 13, bold: true, color: COLORS.green, fontFamily: FONT, alignment: "center" };
  }
  box(slide, { left: 490, top: 122, width: 442, height: 380 }, COLORS.card, COLORS.cardLine, "rounded-xl", "agenda-panel");
  addText(slide, "TODAY’S PLAN", { left: 510, top: 138, width: 300, height: 22 }, { fontSize: 12, bold: true, color: COLORS.purpleSoft });
  addText(slide, config.steps.map((s, i) => `${i + 1}. ${s}`).join("\n"), { left: 510, top: 164, width: 404, height: 260 }, { fontSize: 20 });
  if (config.done) {
    box(slide, { left: 506, top: 426, width: 410, height: 60 }, COLORS.doneFill, COLORS.doneLine, "rounded-lg", "done-when");
    addText(slide, `DONE WHEN: ${config.done}`, { left: 522, top: 436, width: 380, height: 44 }, { fontSize: 15, bold: true });
  }
  return slide;
}

/** Recap: the grouped steps students keep in view during work time. */
export function recap(slide, config) {
  cover(slide, config.title, config.kicker);
  box(slide, { left: 70, top: 122, width: 820, height: 300 }, COLORS.card, COLORS.cardLine, "rounded-xl", "recap-panel");
  addText(slide, config.steps.map((s, i) => `${i + 1}. ${s}`).join("\n"), { left: 100, top: 146, width: 760, height: 260 }, { fontSize: 22 });
  doneBanner(slide, config.done);
  return slide;
}

/** Talk: a short accountable partner structure with a private option. */
export function talk(slide, config) {
  cover(slide, config.title, config.kicker);
  box(slide, { left: 28, top: 122, width: 440, height: 300 }, COLORS.card, COLORS.cardLine, "rounded-xl", "partner-a");
  addText(slide, "PARTNER A", { left: 48, top: 138, width: 300, height: 22 }, { fontSize: 12, bold: true, color: COLORS.purpleSoft });
  addText(slide, config.partnerA, { left: 48, top: 164, width: 404, height: 120 }, { fontSize: 20 });
  addText(slide, "PARTNER B", { left: 48, top: 286, width: 300, height: 22 }, { fontSize: 12, bold: true, color: COLORS.purpleSoft });
  addText(slide, config.partnerB, { left: 48, top: 312, width: 404, height: 100 }, { fontSize: 20 });
  box(slide, { left: 490, top: 122, width: 442, height: 300 }, COLORS.card, COLORS.cardLine, "rounded-xl", "private-option");
  addText(slide, "OR ON YOUR OWN", { left: 510, top: 138, width: 300, height: 22 }, { fontSize: 12, bold: true, color: COLORS.purpleSoft });
  addText(slide, config.privateOption, { left: 510, top: 164, width: 404, height: 240 }, { fontSize: 20 });
  doneBanner(slide, config.done);
  return slide;
}

/** DOL / exit step: literal instructions and the completion cue. */
export function dol(slide, config) {
  cover(slide, config.title, config.kicker);
  box(slide, { left: 70, top: 122, width: 820, height: 300 }, COLORS.card, COLORS.purple, "rounded-xl", "dol-panel");
  addText(slide, "SHOW YOUR LEARNING", { left: 100, top: 138, width: 400, height: 22 }, { fontSize: 12, bold: true, color: COLORS.purpleSoft });
  addText(slide, config.body, { left: 100, top: 164, width: 760, height: 250 }, { fontSize: config.bodySize ?? 22 });
  doneBanner(slide, config.done);
  return slide;
}

/** Speaker-note schema. All fields required. */
export function noteText({ time, move, student, lookFor, pivot, recovery, sources }) {
  const missing = Object.entries({ time, move, student, lookFor, pivot, recovery }).filter(([, v]) => !v).map(([k]) => k);
  if (missing.length || !sources?.length) throw new Error(`Note schema incomplete: ${missing.join(", ")}${sources?.length ? "" : " sources"}`);
  return [
    `Time: ${time}`,
    `Teacher move: ${move}`,
    `Student action: ${student}`,
    `Look-for: ${lookFor}`,
    `Pivot/trim: ${pivot}`,
    `Recovery/access: ${recovery}`,
    "[Sources]",
    ...sources.map((s) => `- ${s}`),
    "[/Sources]",
  ].join("\n");
}

export function setNotes(slide, spec) {
  slide.speakerNotes.textFrame.setText(typeof spec === "string" ? spec : noteText(spec));
  slide.speakerNotes.setVisible(true);
}

/**
 * Inspect, lint (slide language + notes schema + honorific), render previews,
 * export the .pptx, and write final.inspect.ndjson next to the previews.
 */
export async function finalize(runtime, presentation, { workspace, outputPath, expectedCount, previewScale = 2, allow = [] }) {
  const { PresentationFile } = runtime;
  const previewDir = path.join(workspace, "final-preview");
  await fs.rm(previewDir, { recursive: true, force: true });
  await fs.mkdir(previewDir, { recursive: true });
  await fs.mkdir(path.dirname(outputPath), { recursive: true });

  const count = presentation.slides.items.length;
  if (expectedCount && count !== expectedCount) throw new Error(`Slide count ${count} != expected ${expectedCount}`);
  const size = presentation.slides.items[0]?.size ?? presentation.slideSize;

  const inspection = await presentation.inspect({ kind: "slide,textbox,shape,table,image,notes", maxChars: 2_000_000 });
  const records = inspection.ndjson.split("\n").filter(Boolean).map((line) => JSON.parse(line));
  const slideFailures = lintSlideText(records, { allow });
  const noteFailures = lintNotes(notesMapFromRecords(records));
  const slidesWithoutText = [];
  for (let n = 1; n <= count; n += 1) {
    const hasText = records.some((r) => r.slide === n && ["textbox", "shape", "table"].includes(r.kind) && String(r.text ?? "").trim());
    if (!hasText) slidesWithoutText.push(n);
  }
  if (slideFailures.length || noteFailures.length || slidesWithoutText.length) {
    throw new Error(`Deck lint failed\n${JSON.stringify({ slideFailures, noteFailures, slidesWithoutText }, null, 2)}`);
  }

  for (let index = 0; index < count; index += 1) {
    const slide = presentation.slides.items[index];
    const png = await presentation.export({ slide, format: "png", scale: previewScale });
    await fs.writeFile(path.join(previewDir, `final-slide-${String(index + 1).padStart(2, "0")}.png`), Buffer.from(await png.arrayBuffer()));
  }
  const montage = await presentation.export({ format: "png", montage: true, scale: 1 });
  await fs.writeFile(path.join(workspace, "final-montage.png"), Buffer.from(await montage.arrayBuffer()));
  await fs.writeFile(path.join(workspace, "final.inspect.ndjson"), inspection.ndjson);

  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(outputPath);
  return { outputPath, slideCount: count, previewDir, size };
}
