import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const runtimeHelperPath = process.env.CODEX_PRESENTATIONS_RUNTIME_HELPER;
if (!runtimeHelperPath) {
  throw new Error("Set CODEX_PRESENTATIONS_RUNTIME_HELPER to the presentations runtime_helpers.mjs path.");
}
const { importRuntimeModule } = await import(pathToFileURL(path.resolve(runtimeHelperPath)).href);
const { FileBlob, PresentationFile } = await importRuntimeModule("@oai/artifact-tool");

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../../..");
const requestedDays = process.argv.slice(2).map(Number).filter((day) => day >= 1 && day <= 5);
const days = requestedDays.length ? requestedDays : [1, 2, 3, 4, 5];

function contentType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === ".jpg" || ext === ".jpeg") return "image/jpeg";
  if (ext === ".webp") return "image/webp";
  return "image/png";
}

function groupBySlide(records, kind) {
  const grouped = new Map();
  for (const record of records.filter((item) => item.kind === kind)) {
    const items = grouped.get(record.slide) ?? [];
    items.push(record);
    grouped.set(record.slide, items);
  }
  return grouped;
}

function titleFor(texts) {
  return texts.find((text) => text && !["Welcome!", "Get Ready", "Today’s Lesson", "Discussion"].includes(text)) ?? "next lesson action";
}

function notesFor(day, slideNumber, slide, config) {
  const title = titleFor(slide.texts);
  const sources = [...config.sources, ...(slide.sources ?? [])];
  return [
    `Timing: ${slide.timing}`,
    `Purpose: Project ${title} as one clear action in the canonical 1SW Wk1 Day ${day} Manufacturing lesson.`,
    `Monitor: ${slide.lookFor}`,
    `Pivot: ${slide.pivot}`,
    `Trim: ${slide.trim ?? "Read the action and one example, then protect student work time."}`,
    `Recovery/access: ${slide.recovery ?? config.recovery}`,
    "[Sources]",
    ...sources.map((source) => `- ${source}`),
    "[/Sources]",
  ];
}

async function replaceImage(presentation, record, replacement) {
  const image = presentation.resolve(record.id);
  const sourcePath = path.join(root, replacement.path);
  const previous = {
    frame: image.frame,
    crop: image.crop,
    geometry: image.geometry,
    borderRadius: image.borderRadius,
    rotation: image.rotation,
    flipHorizontal: image.flipHorizontal,
    flipVertical: image.flipVertical,
    lockAspectRatio: image.lockAspectRatio,
  };
  image.replace({
    blob: await fs.readFile(sourcePath),
    contentType: contentType(sourcePath),
    alt: replacement.alt,
    fit: replacement.fit ?? "contain",
  });
  Object.assign(image, previous);
  image.fit = replacement.fit ?? "contain";
}

for (const day of days) {
  const configPath = path.join(here, `day${day}.json`);
  const config = JSON.parse(await fs.readFile(configPath, "utf8"));
  const workspace = path.join(root, `tmp/1sw-wk1-deck-sprint/day${day}-template`);
  const starterPath = path.join(workspace, "template-starter.pptx");
  const outputPath = path.join(
    root,
    `cce-curriculum/resources/avid-reference/source/derived/cce-1sw-wk1-day${day}-manufacturing-source-grounded.pptx`,
  );
  const previewDir = path.join(workspace, "final-preview");
  const layoutDir = path.join(workspace, "final-layout");
  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  await fs.rm(previewDir, { recursive: true, force: true });
  await fs.rm(layoutDir, { recursive: true, force: true });
  await fs.mkdir(previewDir, { recursive: true });
  await fs.mkdir(layoutDir, { recursive: true });

  const presentation = await PresentationFile.importPptx(await FileBlob.load(starterPath));
  const initial = await presentation.inspect({ kind: "slide,shape,textbox,image,notes", maxChars: 800_000 });
  const records = initial.ndjson.split("\n").filter(Boolean).map((line) => JSON.parse(line));
  const textboxes = groupBySlide(records, "textbox");
  const images = groupBySlide(records, "image");
  const notes = groupBySlide(records, "notes");
  const shapes = groupBySlide(records, "shape");

  if (presentation.slides.items.length !== config.slides.length) {
    throw new Error(`Day ${day} slide count ${presentation.slides.items.length} != config ${config.slides.length}`);
  }

  for (let index = 0; index < config.slides.length; index += 1) {
    const slideNumber = index + 1;
    const slideConfig = config.slides[index];
    const slideTextboxes = textboxes.get(slideNumber) ?? [];
    if (slideTextboxes.length !== slideConfig.texts.length) {
      throw new Error(`Day ${day} slide ${slideNumber} textbox count ${slideTextboxes.length} != config ${slideConfig.texts.length}`);
    }
    slideTextboxes.forEach((record, textboxIndex) => {
      const textbox = presentation.resolve(record.id);
      textbox.text.set(slideConfig.texts[textboxIndex]);
      const adjustment = slideConfig.frameAdjustments?.[String(textboxIndex)];
      if (adjustment) {
        const frame = textbox.frame;
        textbox.frame = {
          left: frame.left + (adjustment.left ?? 0),
          top: frame.top + (adjustment.top ?? 0),
          width: frame.width + (adjustment.width ?? 0),
          height: frame.height + (adjustment.height ?? 0),
        };
      }
    });
    for (const replacement of slideConfig.images ?? []) {
      const imageRecord = (images.get(slideNumber) ?? [])[replacement.index ?? 0];
      if (!imageRecord) throw new Error(`Day ${day} slide ${slideNumber} missing image ${replacement.index ?? 0}`);
      await replaceImage(presentation, imageRecord, replacement);
    }
    for (const imageIndex of slideConfig.removeImages ?? []) {
      const imageRecord = (images.get(slideNumber) ?? [])[imageIndex];
      if (!imageRecord) throw new Error(`Day ${day} slide ${slideNumber} missing removable image ${imageIndex}`);
      presentation.resolve(imageRecord.id).delete();
    }
    for (const shapeName of slideConfig.removeShapes ?? []) {
      const shapeRecord = (shapes.get(slideNumber) ?? []).find((record) => record.name === shapeName);
      if (!shapeRecord) throw new Error(`Day ${day} slide ${slideNumber} missing removable shape ${shapeName}`);
      presentation.resolve(shapeRecord.id).delete();
    }
    const noteRecord = (notes.get(slideNumber) ?? [])[0];
    if (!noteRecord) throw new Error(`Day ${day} slide ${slideNumber} missing notes`);
    presentation.resolve(noteRecord.id).setText(notesFor(day, slideNumber, slideConfig, config).join("\n"));
  }

  const inspect = await presentation.inspect({ kind: "slide,textbox,image,notes", maxChars: 800_000 });
  await fs.writeFile(path.join(workspace, "final.inspect.ndjson"), inspect.ndjson);
  for (let index = 0; index < presentation.slides.items.length; index += 1) {
    const slide = presentation.slides.items[index];
    const number = String(index + 1).padStart(2, "0");
    const png = await presentation.export({ slide, format: "png", scale: 2 });
    await fs.writeFile(path.join(previewDir, `final-slide-${number}.png`), Buffer.from(await png.arrayBuffer()));
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(path.join(layoutDir, `final-slide-${number}.layout.json`), await layout.text());
  }
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(outputPath);
  console.log(JSON.stringify({ day, outputPath, slides: presentation.slides.items.length, previewDir }));
}
