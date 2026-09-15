// CCE classroom deck library (pptxgenjs). One visual language for every CCE deck.
// Tokens come from the approved VILS Graphic Design exemplars ("Your Pop Art name tag"):
// paper background, ink text, blue accents, pink for the second voice, yellow for early-finisher boxes,
// Arial Black titles, white cards. Slides are 1280x720 px (13.333 x 7.5 in); every position is in px.
//
// Usage in a deck script:
//   const D = require("../lib");            // from build/slides/<week>/dayN.js
//   const deck = D.deck({ public: process.env.CCE_PUBLIC === "1" });
//   const s = deck.slide("As you enter");   // title + optional subtitle
//   deck.card(s, x, y, w, h); deck.body(s, text, x, y, w, h, size, opts); ...
//   deck.write("../../../docs/resources/slides/1sw-wk3-day1.pptx");
//
// public: true swaps every licensed image (workbook page crops, Climber Notes, Xello lesson pages)
// for a plain "See Find Your Future p. N" card so the same script builds the rights-clean twin
// that the public planning site may carry. Pass { licensed: true, fyfPage: N } on deck.image().
const pptxgen = require("pptxgenjs");
const path = require("path");
const fs = require("fs");

const C = { paper: "FAF7EF", ink: "191919", blue: "1955DB", pink: "D71A65", yellow: "F4D941", muted: "5F6368", white: "FFFFFF", green: "1E7A46" };
const px = (v) => v / 96;

function deck(opts = {}) {
  const pres = new pptxgen();
  pres.defineLayout({ name: "PX1280", width: 13.333, height: 7.5 });
  pres.layout = "PX1280";
  const assetDir = opts.assetDir || process.cwd();
  const isPublic = !!opts.public;
  const api = { pres, C, px, isPublic };

  api.slide = (title, sub) => {
    const s = pres.addSlide();
    s.background = { color: C.paper };
    s.addText(title, { x: px(64), y: px(38), w: px(1150), h: px(96), fontFace: "Arial Black", fontSize: title.length > 34 ? 36 : 42, color: C.ink, bold: true, isTextBox: true, margin: 0, valign: "middle" });
    if (sub) s.addText(sub, { x: px(66), y: px(136), w: px(1146), h: px(50), fontFace: "Arial", fontSize: 21, color: C.ink, isTextBox: true, margin: 0, valign: "middle" });
    return s;
  };
  api.title = (big, sub, line3, line4, teach, sources) => {
    const s = pres.addSlide(); s.background = { color: C.paper };
    s.addText(big, { x: px(64), y: px(200), w: px(1150), h: px(120), fontFace: "Arial Black", fontSize: big.length > 26 ? 50 : 60, color: C.ink, bold: true, isTextBox: true, margin: 0 });
    s.addText(sub, { x: px(66), y: px(330), w: px(1100), h: px(60), fontFace: "Arial", fontSize: 30, color: C.blue, bold: true, isTextBox: true, margin: 0 });
    s.addText(line3, { x: px(66), y: px(410), w: px(1100), h: px(40), fontFace: "Arial", fontSize: 22, color: C.ink, isTextBox: true, margin: 0 });
    if (line4) s.addText(line4, { x: px(66), y: px(470), w: px(1100), h: px(60), fontFace: "Arial", fontSize: 20, color: C.muted, isTextBox: true, margin: 0 });
    if (teach) api.notes(s, teach, sources);
    return s;
  };
  api.label = (s, t, x, y, w = 520, color = C.blue) =>
    s.addText(t, { x: px(x), y: px(y), w: px(w), h: px(42), fontFace: "Arial Black", fontSize: 23, color, bold: true, isTextBox: true, margin: 0, valign: "middle" });
  api.body = (s, t, x, y, w, h, size = 20, o = {}) =>
    s.addText(t, { x: px(x), y: px(y), w: px(w), h: px(h), fontFace: "Arial", fontSize: size, color: C.ink, isTextBox: true, margin: 0, valign: "top", ...o });
  api.card = (s, x, y, w, h, fill = C.white) =>
    s.addShape(pres.shapes.RECTANGLE, { x: px(x), y: px(y), w: px(w), h: px(h), fill: { color: fill }, line: { color: fill, width: 0 } });
  api.numbered = (s, items, x, y, w, rowH = 96, size = 22) => {
    items.forEach((t, i) => {
      api.card(s, x, y + i * rowH, w, rowH - 14);
      s.addShape(pres.shapes.OVAL, { x: px(x + 20), y: px(y + 16 + i * rowH), w: px(48), h: px(48), fill: { color: C.blue }, line: { color: C.blue, width: 0 } });
      s.addText(String(i + 1), { x: px(x + 20), y: px(y + 16 + i * rowH), w: px(48), h: px(48), fontFace: "Arial Black", fontSize: 20, color: C.white, bold: true, align: "center", valign: "middle", isTextBox: true, margin: 0 });
      api.body(s, t, x + 88, y + 12 + i * rowH, w - 110, rowH - 34, size, { valign: "middle" });
    });
  };
  // Named rows: [["Think", "text"], ...] with the name in Arial Black on the left of each card.
  api.namedRows = (s, rows, x, y, w, rowH = 118, nameW = 160, size = 19, color = C.blue) => {
    rows.forEach(([who, t], i) => {
      api.card(s, x, y + i * rowH, w, rowH - 14);
      s.addText(who, { x: px(x + 24), y: px(y + 12 + i * rowH), w: px(nameW), h: px(rowH - 38), fontFace: "Arial Black", fontSize: 22, color: Array.isArray(color) ? color[i] : color, bold: true, isTextBox: true, margin: 0, valign: "middle" });
      api.body(s, t, x + 24 + nameW + 12, y + 12 + i * rowH, w - nameW - 60, rowH - 38, size, { valign: "middle" });
    });
  };
  // Sentence stem block: blue label + the stem in large type. Use once or twice a lesson, where students talk or write.
  api.stem = (s, stemText, x = 64, y = 560, w = 1150, labelText = "Say it like this", size = 24) => {
    api.label(s, labelText, x, y, Math.min(600, w));
    api.body(s, stemText, x, y + 46, w, 60, size);
  };
  // Word bank: muted label + words separated by dots.
  api.wordBank = (s, words, x, y, w = 1150, labelText = "Words you will need") => {
    api.label(s, labelText, x, y, Math.min(600, w));
    api.body(s, words.join("  ·  "), x, y + 46, w, 50, 20);
  };
  // Small muted line (timers, voice level, caption).
  api.meta = (s, t, x, y, w = 1150, size = 17) => api.body(s, t, x, y, w, 40, size, { color: C.muted });
  // Yellow early-finisher / extension box.
  api.extension = (s, t, x, y, w, h) => { api.card(s, x, y, w, h, C.yellow); api.body(s, t, x + 20, y + 16, w - 40, h - 32, 17, { bold: true, valign: "middle" }); };
  // Real image. Licensed images become a placeholder card in the public twin.
  api.image = (s, file, x, y, w, h, o = {}) => {
    if (isPublic && o.licensed) {
      api.card(s, x, y, w, h);
      api.body(s, o.placeholder || (o.fyfPage ? `Find Your Future\np. ${o.fyfPage}` : "Licensed page image\n(see the Canvas course)"), x + 20, y + 20, w - 40, h - 40, 22, { align: "center", valign: "middle", color: C.muted, bold: true });
      return;
    }
    s.addImage({ path: path.join(assetDir, file), x: px(x), y: px(y), w: px(w), h: px(h) });
  };
  api.notes = (s, teach, sources) => s.addNotes(`${teach}\n\n[Sources]\n${sources}`);
  api.write = async (out) => {
    fs.mkdirSync(path.dirname(out), { recursive: true });
    await pres.writeFile({ fileName: out });
    console.log("wrote", out);
  };
  return api;
}

// Standard source strings. Every slide's notes end with a [Sources] block built from these.
const SRC = {
  fyf: (pages) => `Find Your Future (Irving ISD / Hats & Ladders, ©2026), printed pp. ${pages}; district-licensed workbook page images from the CCE Canvas course, not for public distribution.`,
  canvas: (date) => `Canvas page renders of CCE course 98060 student pages, captured ${date}.`,
  site: (name, url, date) => `${name} (${url}), screenshot captured ${date}; UI orientation only.`,
  bls: (title, url, date) => `U.S. Bureau of Labor Statistics, Occupational Outlook Handbook, "${title}" (${url}), screenshot captured ${date}. Public domain.`,
  xello: (doc) => `Xello, "${doc}" (district-licensed teacher resource), not for public distribution.`,
  climber: (deckName) => `Climber Notes: "${deckName}" (Hats & Ladders teacher deck, district-licensed), not for public distribution.`,
};

module.exports = { deck, C, px, SRC };
