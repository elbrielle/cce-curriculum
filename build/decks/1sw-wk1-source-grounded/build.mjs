import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { lintNotes, lintSlideText, notesMapFromRecords } from "../lib/slide_lint.mjs";

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
const CONFIG_TO_TEMPLATE_SCALE = 0.75;

function scaledPosition(position) {
  return Object.fromEntries(
    Object.entries(position).map(([key, value]) => [key, value * CONFIG_TO_TEMPLATE_SCALE]),
  );
}

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
    `Time: ${slide.timing}`,
    `Teacher move: Project ${title}, give the named direction or model, and release students only when the response location and completion cue are clear.`,
    `Student action: Complete the one visible action on this slide in the teacher-assigned response home or named platform.`,
    `Look-for: ${slide.lookFor}`,
    `Pivot/trim: ${slide.pivot} Trim: ${slide.trim ?? "Read the action and one example, then protect student work time."}`,
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
        left: frame.left + (adjustment.left ?? 0) * CONFIG_TO_TEMPLATE_SCALE,
        top: frame.top + (adjustment.top ?? 0) * CONFIG_TO_TEMPLATE_SCALE,
        width: frame.width + (adjustment.width ?? 0) * CONFIG_TO_TEMPLATE_SCALE,
        height: frame.height + (adjustment.height ?? 0) * CONFIG_TO_TEMPLATE_SCALE,
        };
      }
    });
    for (const replacement of slideConfig.images ?? []) {
      const imageRecord = (images.get(slideNumber) ?? [])[replacement.index ?? 0];
      if (imageRecord) {
        await replaceImage(presentation, imageRecord, replacement);
        if (config.visualTheme?.replacementImagePosition) {
          presentation.resolve(imageRecord.id).frame = scaledPosition(
            config.visualTheme.replacementImagePosition,
          );
        }
      } else {
        const sourcePath = path.join(root, replacement.path);
        presentation.slides.items[index].images.add({
          blob: await fs.readFile(sourcePath),
          contentType: contentType(sourcePath),
          alt: replacement.alt,
          fit: replacement.fit ?? "contain",
          position: scaledPosition(replacement.position ?? { left: 760, top: 150, width: 450, height: 400 }),
          geometry: replacement.geometry ?? "roundRect",
          borderRadius: replacement.borderRadius ?? "rounded-xl",
        });
      }
    }
    if (
      config.visualTheme?.shrinkBodyForReplacement &&
      (slideConfig.images ?? []).length > 0 &&
      slideTextboxes.length > 1
    ) {
      const body = presentation.resolve(slideTextboxes[1].id);
      body.frame = {
        ...body.frame,
        width: body.frame.width - 430 * CONFIG_TO_TEMPLATE_SCALE,
      };
    }
    const replacedImageIndexes = new Set((slideConfig.images ?? []).map((item) => item.index ?? 0));
    for (const imageIndex of slideConfig.removeImages ?? []) {
      if (replacedImageIndexes.has(imageIndex)) continue;
      const imageRecord = (images.get(slideNumber) ?? [])[imageIndex];
      if (!imageRecord) continue;
      presentation.resolve(imageRecord.id).delete();
    }
    if (slideConfig.background) {
      presentation.slides.items[index].background.fill = slideConfig.background;
    } else if (config.visualTheme?.backgrounds?.length) {
      presentation.slides.items[index].background.fill =
        config.visualTheme.backgrounds[index % config.visualTheme.backgrounds.length];
    }
    for (const added of slideConfig.addImages ?? []) {
      const sourcePath = path.join(root, added.path);
      presentation.slides.items[index].images.add({
        blob: await fs.readFile(sourcePath),
        contentType: contentType(sourcePath),
        alt: added.alt,
        fit: added.fit ?? "contain",
        position: scaledPosition(added.position),
        geometry: added.geometry ?? "roundRect",
        borderRadius: added.borderRadius ?? "rounded-xl",
        ...(added.crop ? { crop: added.crop } : {}),
      });
    }
    for (const added of slideConfig.addTextboxes ?? []) {
      const box = presentation.slides.items[index].shapes.add({
        geometry: added.geometry ?? "roundRect",
        name: added.name,
        position: scaledPosition(added.position),
        fill: added.fill ?? "#5A2D91",
        line: added.line ?? { style: "solid", fill: "none", width: 0 },
        borderRadius: added.borderRadius ?? "rounded-xl",
      });
      box.text = added.text;
      box.text.style = {
        fontSize: 20,
        bold: true,
        color: "#FFFFFF",
        alignment: "center",
        verticalAlignment: "middle",
        ...(added.textStyle ?? {}),
      };
    }
    for (const shapeName of slideConfig.removeShapes ?? []) {
      const shapeRecord = (shapes.get(slideNumber) ?? []).find((record) => record.name === shapeName);
      if (!shapeRecord) continue;
      presentation.resolve(shapeRecord.id).delete();
    }
    const noteRecord = (notes.get(slideNumber) ?? [])[0];
    if (!noteRecord) throw new Error(`Day ${day} slide ${slideNumber} missing notes`);
    presentation.resolve(noteRecord.id).setText(notesFor(day, slideNumber, slideConfig, config).join("\n"));
  }

  const inspect = await presentation.inspect({ kind: "slide,textbox,image,notes", maxChars: 800_000 });
  await fs.writeFile(path.join(workspace, "final.inspect.ndjson"), inspect.ndjson);
  const finalRecords = inspect.ndjson.split("\n").filter(Boolean).map((line) => JSON.parse(line));
  const slideLintFailures = lintSlideText(finalRecords);
  const notesLintFailures = lintNotes(notesMapFromRecords(finalRecords));
  if (slideLintFailures.length || notesLintFailures.length) {
    throw new Error(
      `Day ${day} lint failed: projected=${JSON.stringify(slideLintFailures)} notes=${JSON.stringify(notesLintFailures)}`,
    );
  }
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
