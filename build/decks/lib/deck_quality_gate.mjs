#!/usr/bin/env node

// Fail-closed structural QA for editable PowerPoint decks.
//
// The gate deliberately inspects two different representations:
//   1. artifact-tool `layout` JSON for rendered geometry and line wrapping;
//   2. the exported PPTX's OOXML for paragraph/bullet/run metadata, alt text,
//      and speaker-note labels.
//
// Usage:
//   node build/decks/lib/deck_quality_gate.mjs \
//     --layout-dir tmp/.../final-layout \
//     --pptx path/to/deck.pptx \
//     --require-notes-label 'Time:' \
//     --require-notes-label 'Teacher move:' \
//     --require-sources \
//     --json tmp/deck-quality.json
//
// Intentional text/image overlaps must be declared, never silently ignored:
//   --allow-zone '7:570,112.5,337.5,300'
//
// The equivalent config-file shape is documented by `--help`.

import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { execFileSync } from "node:child_process";
import { pathToFileURL } from "node:url";

const DEFAULTS = Object.freeze({
  minCollisionArea: 64,
  minCollisionRatio: 0.01,
  minInstructionalImageWidth: 288,
  minInstructionalImageHeight: 162,
  instructionalImagePattern:
    "(?:screenshot|screen|workbook|worksheet|page|classlink|xello|hats?\\s*&\\s*ladders|find your future|fyf|launchpad)",
  ignoredCollisionImagePattern: "^Decorative CCE background$",
  requireOoxmlAltText: true,
  allowedCollisionZones: [],
  allowedSmallImages: [],
  allowedWrappedTitles: [],
  requiredNotesLabels: [],
  requireSources: false,
  sourceOpenLabel: "[Sources]",
  sourceCloseLabel: "[/Sources]",
});

function usage() {
  return `Usage:
  node build/decks/lib/deck_quality_gate.mjs --layout-dir DIR --pptx FILE [options]

Required:
  --layout-dir DIR              Directory of artifact-tool *.layout.json files
  --pptx FILE                   Exported editable PowerPoint to inspect

Options:
  --config FILE                 JSON configuration (keys match defaults below)
  --allow-zone S:X,Y,W,H        Allow a declared collision zone on slide S (repeatable)
  --require-notes-label LABEL   Require a speaker-note label on every slide (repeatable)
  --require-sources             Require [Sources] and [/Sources] on every slide
  --json FILE                   Write the complete machine-readable report
  --help                        Show this help

Config example:
{
  "minCollisionArea": 64,
  "minCollisionRatio": 0.01,
  "minInstructionalImageWidth": 288,
  "minInstructionalImageHeight": 162,
  "instructionalImagePattern": "(?:screenshot|screen|workbook|page|xello)",
  "allowedCollisionZones": [
    { "slide": 7, "x": 570, "y": 112.5, "width": 337.5, "height": 300,
      "textId": "754", "imageId": "755", "reason": "intentional callout" }
  ],
  "allowedSmallImages": [{ "slide": 4, "imageId": "99", "reason": "app icon" }],
  "allowedWrappedTitles": [{ "slide": 1, "titleId": "2", "reason": "approved lockup" }],
  "requiredNotesLabels": ["Time:", "Teacher move:", "Student action:", "Look-for:"],
  "requireSources": true,
  "sourceOpenLabel": "[Sources]",
  "sourceCloseLabel": "[/Sources]"
}

Exit status is 0 only when no issues are found; content defects exit 1 and
configuration/runtime errors exit 2.`;
}

function xmlDecode(value = "") {
  return String(value)
    .replace(/&#x([0-9a-f]+);/gi, (_, hex) => String.fromCodePoint(Number.parseInt(hex, 16)))
    .replace(/&#([0-9]+);/g, (_, decimal) => String.fromCodePoint(Number(decimal)))
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&");
}

function attributes(fragment = "") {
  const result = {};
  for (const match of fragment.matchAll(/([\w:.-]+)="([^"]*)"/g)) {
    result[match[1]] = xmlDecode(match[2]);
  }
  return result;
}

function elementBlocks(xml, qualifiedName) {
  const escaped = qualifiedName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const expression = new RegExp(`<${escaped}(?:\\s[^>]*)?>[\\s\\S]*?<\\/${escaped}>`, "g");
  return [...String(xml).matchAll(expression)].map((match) => match[0]);
}

function textFromXml(xml) {
  return [...String(xml).matchAll(/<a:t(?:\s[^>]*)?>([\s\S]*?)<\/a:t>|<a:t\s*\/>/g)]
    .map((match) => xmlDecode(match[1] ?? ""))
    .join("");
}

function parseRunStyle(paragraphXml) {
  const runBlocks = elementBlocks(paragraphXml, "a:r");
  const fieldBlocks = elementBlocks(paragraphXml, "a:fld");
  const styles = [...runBlocks, ...fieldBlocks]
    .map((runXml) => {
      const rPr = runXml.match(/<a:rPr\b([^>]*)\/?\s*>/);
      if (!rPr) return { fontSize: null, bold: null };
      const attrs = attributes(rPr[1]);
      return {
        fontSize: attrs.sz === undefined ? null : Number(attrs.sz) / 100,
        bold: attrs.b === undefined ? null : attrs.b === "1" || attrs.b === "true",
      };
    })
    .filter((style) => style.fontSize !== null || style.bold !== null);
  return {
    fontSizes: [...new Set(styles.map((style) => style.fontSize).filter((value) => value !== null))],
    boldValues: [...new Set(styles.map((style) => style.bold).filter((value) => value !== null))],
    firstFontSize: styles.find((style) => style.fontSize !== null)?.fontSize ?? null,
    firstBold: styles.find((style) => style.bold !== null)?.bold ?? null,
  };
}

function parseParagraph(paragraphXml, paragraphIndex) {
  const pPrMatch = paragraphXml.match(/<a:pPr\b([^>]*)>([\s\S]*?)<\/a:pPr>|<a:pPr\b([^>]*)\/>/);
  const pPrAttrs = attributes(pPrMatch?.[1] ?? pPrMatch?.[3] ?? "");
  const pPrBody = pPrMatch?.[2] ?? "";
  const bulletChar = pPrBody.match(/<a:buChar\b[^>]*char="([^"]*)"/);
  const autoNum = pPrBody.match(/<a:buAutoNum\b([^>]*)\/?\s*>/);
  const bullet = /<a:buNone\b/.test(pPrBody)
    ? { type: "none", char: null }
    : bulletChar
      ? { type: "char", char: xmlDecode(bulletChar[1]) }
      : autoNum
        ? { type: "auto", char: null, ...attributes(autoNum[1]) }
        : { type: "inherited", char: null };
  return {
    index: paragraphIndex,
    text: textFromXml(paragraphXml),
    level: pPrAttrs.lvl === undefined ? 0 : Number(pPrAttrs.lvl),
    bullet,
    ...parseRunStyle(paragraphXml),
  };
}

export function parseSlideXml(xml, slideNumber = null) {
  const shapes = elementBlocks(xml, "p:sp").map((shapeXml) => {
    const cNvPrMatch = shapeXml.match(/<p:cNvPr\b([^>]*)/);
    const cNvPr = attributes(cNvPrMatch?.[1] ?? "");
    const placeholderMatch = shapeXml.match(/<p:ph\b([^>]*)\/?\s*>/);
    const placeholder = attributes(placeholderMatch?.[1] ?? "");
    const paragraphs = elementBlocks(shapeXml, "a:p").map((paragraph, index) =>
      parseParagraph(paragraph, index + 1),
    );
    return {
      id: cNvPr.id ?? null,
      name: cNvPr.name ?? "",
      placeholderType: placeholder.type ?? null,
      placeholderIndex: placeholder.idx ?? null,
      paragraphs,
    };
  });
  const images = elementBlocks(xml, "p:pic").map((pictureXml) => {
    const cNvPrMatch = pictureXml.match(/<p:cNvPr\b([^>]*)/);
    const cNvPr = attributes(cNvPrMatch?.[1] ?? "");
    return {
      id: cNvPr.id ?? null,
      name: cNvPr.name ?? "",
      alt: (cNvPr.descr ?? cNvPr.title ?? "").trim(),
    };
  });
  return { slide: slideNumber, shapes, images };
}

function bboxObject(bbox) {
  const [x, y, width, height] = bbox.map(Number);
  return { x, y, width, height, right: x + width, bottom: y + height };
}

function intersection(aBox, bBox) {
  const a = bboxObject(aBox);
  const b = bboxObject(bBox);
  const x = Math.max(a.x, b.x);
  const y = Math.max(a.y, b.y);
  const right = Math.min(a.right, b.right);
  const bottom = Math.min(a.bottom, b.bottom);
  if (right <= x || bottom <= y) return null;
  return { x, y, width: right - x, height: bottom - y, area: (right - x) * (bottom - y) };
}

function zoneContains(zone, overlap) {
  const tolerance = 0.5;
  return (
    overlap.x >= Number(zone.x) - tolerance &&
    overlap.y >= Number(zone.y) - tolerance &&
    overlap.x + overlap.width <= Number(zone.x) + Number(zone.width) + tolerance &&
    overlap.y + overlap.height <= Number(zone.y) + Number(zone.height) + tolerance
  );
}

function allowedByObject(entries, slide, id, idKey) {
  return entries.some(
    (entry) =>
      Number(entry.slide) === Number(slide) &&
      (entry[idKey] === undefined || String(entry[idKey]) === String(id)),
  );
}

function allowedCollision(config, slide, text, image, overlap) {
  return config.allowedCollisionZones.some(
    (zone) =>
      Number(zone.slide) === Number(slide) &&
      (zone.textId === undefined || String(zone.textId) === String(text.id)) &&
      (zone.imageId === undefined || String(zone.imageId) === String(image.id)) &&
      zoneContains(zone, overlap),
  );
}

function isInstructionalImage(image, config) {
  const pattern = new RegExp(config.instructionalImagePattern, "i");
  return pattern.test(`${image.alt ?? ""} ${image.name ?? ""}`);
}

function ignoredCollisionImage(image, config) {
  const pattern = config.ignoredCollisionImagePattern
    ? new RegExp(config.ignoredCollisionImagePattern, "i")
    : null;
  return pattern?.test(`${image.alt ?? ""} ${image.name ?? ""}`.trim()) ?? false;
}

export function detectLayoutIssues(layout, config = DEFAULTS, titleShapeIds = new Set()) {
  const merged = { ...DEFAULTS, ...config };
  const slide = Number(layout?.slide?.slide ?? 0);
  const elements = Array.isArray(layout?.elements) ? layout.elements : [];
  const textElements = elements.filter(
    (element) =>
      ["shape", "textbox", "table"].includes(element.kind) &&
      String(element.text ?? "").trim() &&
      Array.isArray(element.bbox),
  );
  const images = elements.filter((element) => element.kind === "image" && Array.isArray(element.bbox));
  const issues = [];

  for (const text of textElements) {
    for (const image of images) {
      if (ignoredCollisionImage(image, merged)) continue;
      const overlap = intersection(text.bbox, image.bbox);
      if (!overlap) continue;
      const textArea = Number(text.bbox[2]) * Number(text.bbox[3]);
      const imageArea = Number(image.bbox[2]) * Number(image.bbox[3]);
      const ratio = overlap.area / Math.max(1, Math.min(textArea, imageArea));
      if (overlap.area < merged.minCollisionArea || ratio < merged.minCollisionRatio) continue;
      if (allowedCollision(merged, slide, text, image, overlap)) continue;
      issues.push({
        code: "TEXT_IMAGE_COLLISION_CANDIDATE",
        slide,
        objectId: text.id ?? text.aid ?? null,
        relatedObjectId: image.id ?? image.aid ?? null,
        message: `Text and image overlap by ${Math.round(overlap.area)} px² (${Math.round(ratio * 100)}% of the smaller object).`,
        evidence: { text: String(text.text).slice(0, 120), textBox: text.bbox, imageAlt: image.alt ?? "", imageBox: image.bbox, overlap },
      });
    }
  }

  for (const image of images) {
    if (!isInstructionalImage(image, merged)) continue;
    if (allowedByObject(merged.allowedSmallImages, slide, image.id, "imageId")) continue;
    const [, , width, height] = image.bbox.map(Number);
    if (width >= merged.minInstructionalImageWidth && height >= merged.minInstructionalImageHeight) continue;
    issues.push({
      code: "INSTRUCTIONAL_IMAGE_TOO_SMALL",
      slide,
      objectId: image.id ?? image.aid ?? null,
      message: `Instructional image is ${Math.round(width)}×${Math.round(height)} px; minimum is ${merged.minInstructionalImageWidth}×${merged.minInstructionalImageHeight} px.`,
      evidence: { alt: image.alt ?? "", bbox: image.bbox },
    });
  }

  for (const element of textElements) {
    const isTitle =
      titleShapeIds.has(String(element.id)) ||
      /(?:^|\s)title(?:\s|$)/i.test(String(element.name ?? "")) ||
      (Number(element.bbox[1]) < 110 && Number(element.resolvedFontSize ?? element.resolvedTextStyle?.fontSize ?? 0) >= 32);
    if (!isTitle || Number(element.textLayout?.lineCount ?? 1) <= 1) continue;
    if (allowedByObject(merged.allowedWrappedTitles, slide, element.id, "titleId")) continue;
    issues.push({
      code: "TITLE_WRAPS",
      slide,
      objectId: element.id ?? element.aid ?? null,
      message: `Title wraps to ${element.textLayout.lineCount} lines.`,
      evidence: { text: String(element.text).slice(0, 160), bbox: element.bbox },
    });
  }
  return issues;
}

function procedureParagraph(paragraph) {
  return (
    /^\s*\d+[.)]\s*/.test(paragraph.text) ||
    paragraph.bullet.type === "auto" ||
    (paragraph.bullet.type === "char" && /^\d+$/.test(paragraph.bullet.char ?? ""))
  );
}

function procedureStyleSignature(paragraph) {
  return {
    fontSize: paragraph.firstFontSize,
    bold: paragraph.firstBold ?? false,
  };
}

export function detectOoxmlIssues(parsedSlide, config = DEFAULTS) {
  const slide = parsedSlide.slide;
  const issues = [];
  const literalMarker = /^\s*(?:[•●▪◦\-–—]|\d+[.)]|[✓✔√☑])\s*/;
  const suspectBulletCharacter = /^(?:\d+|✓|✔|√|☑)$/;

  for (const image of parsedSlide.images) {
    if (config.requireOoxmlAltText === false) continue;
    if (image.alt) continue;
    issues.push({
      code: "IMAGE_ALT_TEXT_MISSING",
      slide,
      objectId: image.id,
      message: "Image has no OOXML title/description alternative text.",
      evidence: { name: image.name },
    });
  }

  for (const shape of parsedSlide.shapes) {
    for (const paragraph of shape.paragraphs) {
      const hasNativeBullet = ["char", "auto"].includes(paragraph.bullet.type);
      if (hasNativeBullet && literalMarker.test(paragraph.text)) {
        issues.push({
          code: "LITERAL_AND_NATIVE_LIST_MARKER",
          slide,
          objectId: shape.id,
          paragraph: paragraph.index,
          message: "Paragraph contains a literal list marker and native OOXML bullet/number metadata.",
          evidence: { text: paragraph.text.slice(0, 120), bullet: paragraph.bullet },
        });
      }
      if (paragraph.bullet.type === "char" && suspectBulletCharacter.test(paragraph.bullet.char ?? "")) {
        issues.push({
          code: "DIGIT_OR_CHECKMARK_BULLET_METADATA",
          slide,
          objectId: shape.id,
          paragraph: paragraph.index,
          message: `Paragraph inherited suspicious bullet character “${paragraph.bullet.char}”.`,
          evidence: { text: paragraph.text.slice(0, 120), bullet: paragraph.bullet },
        });
      }
    }

    const procedure = shape.paragraphs.filter((paragraph) => paragraph.text.trim() && procedureParagraph(paragraph));
    if (procedure.length < 2) continue;
    const styles = procedure.map((paragraph) => ({
      paragraph: paragraph.index,
      text: paragraph.text.slice(0, 80),
      ...procedureStyleSignature(paragraph),
    }));
    const fontSizes = new Set(styles.map((style) => style.fontSize === null ? "inherited" : String(style.fontSize)));
    const boldValues = new Set(styles.map((style) => String(style.bold)));
    if (fontSizes.size > 1) {
      issues.push({
        code: "PROCEDURE_FONT_SIZE_INCONSISTENT",
        slide,
        objectId: shape.id,
        message: "Numbered procedure steps do not share one explicit font size.",
        evidence: { styles },
      });
    }
    if (boldValues.size > 1) {
      issues.push({
        code: "PROCEDURE_BOLD_INCONSISTENT",
        slide,
        objectId: shape.id,
        message: "Numbered procedure steps do not share one bold treatment.",
        evidence: { styles },
      });
    }
  }
  return issues;
}

function zipList(pptxPath) {
  return execFileSync("unzip", ["-Z1", pptxPath], { encoding: "utf8", maxBuffer: 32 * 1024 * 1024 })
    .split(/\r?\n/)
    .filter(Boolean);
}

function zipRead(pptxPath, member) {
  return execFileSync("unzip", ["-p", pptxPath, member], {
    encoding: "utf8",
    maxBuffer: 32 * 1024 * 1024,
  });
}

function slideNumberFromMember(member) {
  return Number(member.match(/slide(\d+)\.xml$/)?.[1] ?? 0);
}

function noteMemberForSlide(pptxPath, members, slideNumber) {
  const relMember = `ppt/slides/_rels/slide${slideNumber}.xml.rels`;
  if (!members.includes(relMember)) return null;
  const relXml = zipRead(pptxPath, relMember);
  const relationship = [...relXml.matchAll(/<Relationship\b([^>]*)\/?\s*>/g)]
    .map((match) => attributes(match[1]))
    .find((rel) => /\/notesSlide$/.test(rel.Type ?? ""));
  if (!relationship?.Target) return null;
  // OOXML relationship targets may be package-absolute (`/ppt/...`) or
  // relative to the source part (`../notesSlides/...`). `path.join` does not
  // implement OPC package semantics for the leading slash, so handle both.
  const normalized = relationship.Target.startsWith("/")
    ? path.posix.normalize(relationship.Target.slice(1))
    : path.posix.normalize(path.posix.join("ppt/slides", relationship.Target));
  return members.includes(normalized) ? normalized : null;
}

function requiredNoteIssues(slide, noteText, config) {
  const issues = [];
  for (const label of config.requiredNotesLabels) {
    if (noteText.includes(label)) continue;
    issues.push({
      code: "NOTES_LABEL_MISSING",
      slide,
      objectId: null,
      message: `Speaker notes are missing required label “${label}”.`,
      evidence: { notePreview: noteText.slice(0, 160) },
    });
  }
  if (config.requireSources) {
    for (const label of [config.sourceOpenLabel, config.sourceCloseLabel]) {
      if (noteText.includes(label)) continue;
      issues.push({
        code: "SOURCE_LABEL_MISSING",
        slide,
        objectId: null,
        message: `Speaker notes are missing source label “${label}”.`,
        evidence: { notePreview: noteText.slice(0, 160) },
      });
    }
  }
  return issues;
}

async function loadLayouts(layoutDir) {
  const names = (await fs.readdir(layoutDir))
    .filter((name) => name.endsWith(".layout.json"))
    .sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
  if (!names.length) throw new Error(`No *.layout.json files found in ${layoutDir}`);
  return Promise.all(
    names.map(async (name) => ({
      name,
      layout: JSON.parse(await fs.readFile(path.join(layoutDir, name), "utf8")),
    })),
  );
}

function parseZone(value) {
  const match = String(value).match(/^(\d+):(-?[\d.]+),(-?[\d.]+),([\d.]+),([\d.]+)$/);
  if (!match) throw new Error(`Invalid --allow-zone “${value}”; expected S:X,Y,W,H`);
  return {
    slide: Number(match[1]),
    x: Number(match[2]),
    y: Number(match[3]),
    width: Number(match[4]),
    height: Number(match[5]),
    reason: "CLI-declared intentional overlap",
  };
}

function parseArgs(argv) {
  const args = { allowedCollisionZones: [], requiredNotesLabels: [] };
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--help" || token === "-h") args.help = true;
    else if (token === "--require-sources") args.requireSources = true;
    else if (token === "--layout-dir") args.layoutDir = argv[++index];
    else if (token === "--pptx") args.pptx = argv[++index];
    else if (token === "--config") args.configPath = argv[++index];
    else if (token === "--json") args.jsonPath = argv[++index];
    else if (token === "--allow-zone") args.allowedCollisionZones.push(parseZone(argv[++index]));
    else if (token === "--require-notes-label") args.requiredNotesLabels.push(argv[++index]);
    else throw new Error(`Unknown argument: ${token}`);
  }
  return args;
}

export async function inspectDeck({ layoutDir, pptx, config = {} }) {
  const merged = {
    ...DEFAULTS,
    ...config,
    allowedCollisionZones: [...DEFAULTS.allowedCollisionZones, ...(config.allowedCollisionZones ?? [])],
    allowedSmallImages: [...DEFAULTS.allowedSmallImages, ...(config.allowedSmallImages ?? [])],
    allowedWrappedTitles: [...DEFAULTS.allowedWrappedTitles, ...(config.allowedWrappedTitles ?? [])],
    requiredNotesLabels: [...DEFAULTS.requiredNotesLabels, ...(config.requiredNotesLabels ?? [])],
  };
  const layouts = await loadLayouts(layoutDir);
  const members = zipList(pptx);
  const slideMembers = members
    .filter((member) => /^ppt\/slides\/slide\d+\.xml$/.test(member))
    .sort((a, b) => slideNumberFromMember(a) - slideNumberFromMember(b));
  if (!slideMembers.length) throw new Error(`No slide OOXML found in ${pptx}`);

  const parsedSlides = new Map();
  const issues = [];
  for (const member of slideMembers) {
    const slideNumber = slideNumberFromMember(member);
    const parsed = parseSlideXml(zipRead(pptx, member), slideNumber);
    parsedSlides.set(slideNumber, parsed);
    issues.push(...detectOoxmlIssues(parsed, merged));
    if (merged.requiredNotesLabels.length || merged.requireSources) {
      const noteMember = noteMemberForSlide(pptx, members, slideNumber);
      const noteText = noteMember ? textFromXml(zipRead(pptx, noteMember)) : "";
      issues.push(...requiredNoteIssues(slideNumber, noteText, merged));
    }
  }

  const layoutSlides = new Set();
  for (const { name, layout } of layouts) {
    const slideNumber = Number(layout?.slide?.slide ?? 0);
    layoutSlides.add(slideNumber);
    const titleShapeIds = new Set(
      (parsedSlides.get(slideNumber)?.shapes ?? [])
        .filter((shape) => ["title", "ctrTitle"].includes(shape.placeholderType))
        .map((shape) => String(shape.id)),
    );
    const found = detectLayoutIssues(layout, merged, titleShapeIds);
    for (const issue of found) issue.layoutFile = name;
    issues.push(...found);
  }
  for (const slideNumber of parsedSlides.keys()) {
    if (layoutSlides.has(slideNumber)) continue;
    issues.push({
      code: "LAYOUT_JSON_MISSING",
      slide: slideNumber,
      objectId: null,
      message: "No artifact-tool layout JSON was supplied for this PPTX slide.",
      evidence: {},
    });
  }

  issues.sort((a, b) => a.slide - b.slide || a.code.localeCompare(b.code));
  const counts = {};
  for (const issue of issues) counts[issue.code] = (counts[issue.code] ?? 0) + 1;
  return {
    pass: issues.length === 0,
    checkedAt: new Date().toISOString(),
    layoutDir: path.resolve(layoutDir),
    pptx: path.resolve(pptx),
    slides: parsedSlides.size,
    thresholds: {
      minCollisionArea: merged.minCollisionArea,
      minCollisionRatio: merged.minCollisionRatio,
      minInstructionalImageWidth: merged.minInstructionalImageWidth,
      minInstructionalImageHeight: merged.minInstructionalImageHeight,
    },
    allowedCollisionZones: merged.allowedCollisionZones,
    counts,
    issues,
  };
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
    if (args.help) {
      console.log(usage());
      return;
    }
    if (!args.layoutDir || !args.pptx) throw new Error("Both --layout-dir and --pptx are required.");
    const fileConfig = args.configPath
      ? JSON.parse(await fs.readFile(path.resolve(args.configPath), "utf8"))
      : {};
    const config = {
      ...fileConfig,
      requireSources: args.requireSources ?? fileConfig.requireSources ?? false,
      allowedCollisionZones: [
        ...(fileConfig.allowedCollisionZones ?? []),
        ...args.allowedCollisionZones,
      ],
      requiredNotesLabels: [
        ...(fileConfig.requiredNotesLabels ?? []),
        ...args.requiredNotesLabels,
      ],
    };
    const report = await inspectDeck({
      layoutDir: path.resolve(args.layoutDir),
      pptx: path.resolve(args.pptx),
      config,
    });
    if (args.jsonPath) {
      const reportPath = path.resolve(args.jsonPath);
      await fs.mkdir(path.dirname(reportPath), { recursive: true });
      await fs.writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`);
    }
    for (const [code, count] of Object.entries(report.counts).sort()) {
      console.log(`${String(count).padStart(3)}  ${code}`);
    }
    console.log(`${report.pass ? "PASS" : "FAIL"}: ${path.basename(report.pptx)} (${report.slides} slides, ${report.issues.length} issues)`);
    if (!report.pass) process.exitCode = 1;
  } catch (error) {
    console.error(`ERROR: ${error.message}`);
    console.error(usage());
    process.exitCode = 2;
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  await main();
}
