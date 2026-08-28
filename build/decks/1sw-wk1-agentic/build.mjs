import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const helper = process.env.CODEX_PRESENTATIONS_RUNTIME_HELPER;
if (!helper) throw new Error("CODEX_PRESENTATIONS_RUNTIME_HELPER is required");
const { importRuntimeModule } = await import(pathToFileURL(path.resolve(helper)).href);
const { Presentation, PresentationFile } = await importRuntimeModule("@oai/artifact-tool");

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../../..");
const sourceDir = path.join(root, "build/decks/1sw-wk1-source-grounded");
const requested = process.argv.slice(2).map(Number).filter((day) => day >= 1 && day <= 5);
const days = requested.length ? requested : [1, 2, 3, 4, 5];
const previewRoot = process.env.CCE_AGENTIC_OUTPUT_DIR
  ? path.resolve(process.env.CCE_AGENTIC_OUTPUT_DIR)
  : path.join(root, "tmp/1sw-wk1-agentic-preview");

const C = {
  navy: "#14315C", teal: "#087F8C", gold: "#F3B61F", plum: "#6B3FA0",
  coral: "#E4545A", ink: "#17233A", muted: "#50647A", off: "#F7F8FB",
  cream: "#FFF8E8", paleTeal: "#EEF7F5", white: "#FFFFFF", line: "#D8E2EE",
};

const DECK = {
  1: {
    day: "MONDAY", title: "Manufacturing Careers", subtitle: "Explore the cluster. Compare two careers.", accent: C.gold,
    objective: "I can explore Manufacturing careers and compare two careers using one task and one preparation fact for each.",
    evidence: "A two-career comparison with one task and one preparation fact for each career.",
    hero: "cce-curriculum/resources/canvas-licensed/1sw/wk1/day1/hnl-manufacturing-cluster-current.png",
    layouts: ["A","C","B","D","G","E","F","F","E","K","G","G","F","L","N"],
  },
  2: {
    day: "TUESDAY", title: "Machine Breakdown Mystery", subtitle: "Use evidence before choosing a repair.", accent: C.coral,
    objective: "I can use a five-stage process to solve a machine problem and research one Manufacturing career.",
    evidence: "A Jamie recommendation with one career, two preparation steps, and a reasonable timeline.",
    hero: "cce-curriculum/resources/canvas-licensed/1sw/wk1/day2/machine-breakdown-clues.jpg",
    layouts: ["A","B","D","E","E","H","H","F","K","F","J","G","L","J","M","N"],
  },
  3: {
    day: "WEDNESDAY", title: "Super Sports Manufacturing", subtitle: "Design. Build. Test. Improve.", accent: C.teal,
    objective: "I can choose a material and weld, build a bike-rack model, test one weak point, and name a revision.",
    evidence: "A weak-point observation, reinforcement choice, and ranked-metal explanation.",
    hero: "cce-curriculum/resources/canvas-licensed/1sw/wk1/day3/build-and-test-prototype.jpg",
    layouts: ["A","C","B","D","E","I","F","F","F","J","K","H","L","L","M","N"],
  },
  4: {
    day: "THURSDAY", title: "Robots for Crayons", subtitle: "Use evidence. Plan a safe test.", accent: C.plum,
    objective: "I can use case evidence to build a safe, testable response plan for two factory problems.",
    evidence: "Two problem plans plus one individual role-and-clue response.",
    hero: "cce-curriculum/resources/canvas-licensed/1sw/wk1/day4/robots-for-crayons-problems.png",
    layouts: ["A","C","B","D","I","E","K","J","J","I","L","L","M"],
  },
  5: {
    day: "FRIDAY", title: "Xello Matchmaker", subtitle: "Notice a result. Explain what shaped it.", accent: C.teal,
    objective: "I can connect one Matchmaker result to an interest and explain how that interest affected a career match.",
    evidence: "Three private reflection responses plus Matchmaker Phase 1 completion.",
    hero: "cce-curriculum/resources/owner-authenticated-source/xello/2026-08-19/matchmaker-landing.png",
    layouts: ["A","C","B","D","E","G","H","G","G","L","L","J","L","M","N"],
  },
};

const TITLE_OVERRIDES = {
  "1:3":"Welcome!", "1:15":"Close: What Changed?",
  "1:6":"Manufacturing Goes Beyond Assembly",
  "2:1":"Machine Breakdown Mystery", "2:2":"Welcome!", "2:10":"Evidence Check", "2:16":"Close: Evidence Before Repair",
  "3:3":"Welcome!", "3:4":"Warm-Up: Follow the Product", "3:5":"Meet the Manufacturing Order", "3:6":"Requirements", "3:10":"Label Every Planned Weld", "3:13":"Build for 7 Minutes",
  "3:15":"Rank the Metals", "3:16":"Tomorrow: Robot Problem Solving",
  "4:3":"Welcome!", "4:11":"Color Confusion Action Plan", "4:12":"Slowpoke Robot Action Plan",
  "5:3":"Welcome!", "5:15":"Close: Result → Reason → Question",
};

const CONTENT_OVERRIDES = {
  "2:9": [
    "Name the exact problem.", "List two possible causes.", "Choose one safe first solution.",
    "Name the test result you need.", "Prevent a repeat.",
    "Use the clues. Show how the test proves or disproves the cause."
  ],
  "2:10": ["Which clue narrowed the cause most?", "Likely first check", "Label-roll size, type, alignment, or jammed feed"],
  "3:5": [
    "100 CUSTOM BIKE RACKS", "You are the expert welder at SuperSports Manufacturing.",
    "The rack must be durable, weather-resistant, and repeatable 100 times."
  ],
  "3:6": [
    "STRONG", "RAIN-READY", "COMPACT", "REPEATABLE",
    "Hold multiple bikes without bending.", "Use joints another team could build the same way."
  ],
  "3:11": [
    "Explain which design best meets the requirements.", "Point to the planned weld labels.",
    "Check whether the plan can be built and tested.", "Choose the design both partners can explain."
  ],
  "3:16": ["Next class: use evidence to diagnose two robot problems.", "Bring the same build-test-improve mindset."],
  "4:4": ["A failure begins right after one part is replaced.", "What should the team check first—and why?"],
  "4:5": [
    "COLOR CONFUSION", "Crayons are sorted into the wrong color boxes.",
    "SLOWPOKE ROBOT", "One robot pauses and slows the whole line."
  ],
  "4:7": [
    "Process Engineer: trace the workflow.", "Quality Inspector: compare the output to the standard.",
    "Name one clue and one possible cause.",
    "Maintenance Technician: inspect parts and signals.", "Packaging Specialist: trace what happens after sorting.",
    "Name one clue and one possible cause."
  ],
  "4:11": ["Use two clues.", "Choose one safe test.", "Name the result you expect.", "Plan the next check if the test fails."],
  "4:12": ["Use two clues.", "Put the safe test steps in order.", "Name the result you expect.", "Plan the next check if the test fails."],
  "4:13": ["Choose one Manufacturing role.", "Explain what that worker does first.", "Cite one clue from the case."],
  "5:9": ["Open ClassLink.", "Select Xello.", "Open About Me → Matchmaker.", "DONE WHEN: Matchmaker is open."]
};

const STEP_OVERRIDES = {
  "1:12": ["Write one new career", "Write one question"],
  "5:6": ["Answer the opening goal question", "Continue into Matchmaker"],
  "5:9": ["Open ClassLink", "Select Xello", "Open About Me → Matchmaker"],
};

const DONE_OVERRIDES = {
  "1:12": "One new career and one question are recorded on today's response page.",
  "2:13": "All six fields contain evidence from the Hat profile.",
  "3:13": "One rack is built and ready to test.",
  "3:14": "You named one weak point and one reinforcement.",
  "3:15": "Rank all three metals and explain #1 with one pro and one con.",
  "4:11": "The Color Confusion plan has two clues, one safe test, and an expected result.",
  "4:12": "The Slowpoke Robot plan has ordered test steps and an expected result.",
  "5:6": "The opening goal question is answered and Matchmaker continues.",
  "5:9": "Matchmaker is open.",
  "5:10": "Questions 1–20 are complete.",
  "5:11": "39 questions are complete, one career is open, and Find out why is selected.",
  "5:13": "All three reflections include a reason or example.",
};

const NEXT_OVERRIDES = {
  "1:15": "Tomorrow: solve a machine breakdown with evidence.",
  "2:16": "Tomorrow: design, build, test, and improve a prototype.",
  "3:16": "Tomorrow: use case evidence to solve two robot problems.",
};

const PARTNER_OVERRIDES = {
  "1:10": {
    a: ["Explain your choice for 30 seconds.", "I would ____ because ____."],
    b: ["Explain your choice for 30 seconds.", "Slowing down costs ____, but a bad weld costs ____."],
  },
};

const WORK_CHECKLIST_OVERRIDES = {
  "4:11": ["Two case clues", "One safe test", "Expected result", "Next check if it fails"],
  "4:12": ["Two case clues", "Ordered safe test", "Expected result", "Next check if it fails"],
};

const VISUAL_OVERRIDES = {
  "1:4": "cce-curriculum/resources/canvas-licensed/1sw/wk1/day1/manufacturing-chapter-opener.jpg",
  "1:6": "cce-curriculum/resources/canvas-licensed/1sw/wk1/day1/hnl-manufacturing-cluster-current.png",
  "1:9": "cce-curriculum/resources/canvas-licensed/1sw/wk1/day1/manufacturing-chapter-opener.jpg",
  "1:11": "cce-curriculum/resources/canvas-licensed/1sw/wk1/day1/hnl-manufacturing-cluster-current.png",
  "1:12": "cce-curriculum/resources/canvas-licensed/1sw/wk1/day1/hnl-manufacturing-cluster-current.png",
  "1:14": "cce-curriculum/resources/canvas-licensed/1sw/wk1/day1/hnl-robotics-hat-preview-current.png",
  "2:6": "cce-curriculum/resources/canvas-licensed/1sw/wk1/day2/machine-breakdown-clues.jpg",
  "2:7": "cce-curriculum/resources/canvas-licensed/1sw/wk1/day2/machine-breakdown-clues.jpg",
  "2:8": "cce-curriculum/resources/canvas-licensed/1sw/wk1/day2/machine-breakdown-clues.jpg",
  "2:15": "cce-curriculum/resources/canvas-licensed/1sw/wk1/day2/machine-breakdown-clues.jpg",
  "2:16": "cce-curriculum/resources/canvas-licensed/1sw/wk1/day2/machine-breakdown-clues.jpg",
  "3:8": "cce-curriculum/resources/canvas-licensed/1sw/wk1/day3/build-and-test-prototype.jpg",
  "3:9": "cce-curriculum/resources/canvas-licensed/1sw/wk1/day3/build-and-test-prototype.jpg",
  "3:14": "cce-curriculum/resources/canvas-licensed/1sw/wk1/day3/build-and-test-prototype.jpg",
  "4:11": "cce-curriculum/resources/canvas-licensed/1sw/wk1/day4/how-the-machines-work.png",
  "4:12": "cce-curriculum/resources/canvas-licensed/1sw/wk1/day4/how-the-machines-work.png",
  "5:4": "cce-curriculum/resources/owner-authenticated-source/xello/2026-08-19/matchmaker-landing.png",
  "5:6": "build/decks/1sw-wk1-agentic/assets/matchmaker-opening-question-clean.png",
  "5:9": "build/decks/1sw-wk1-agentic/assets/xello-classlink-tile.png",
  "5:10": "cce-curriculum/resources/owner-authenticated-source/xello/2026-08-19/support-site/img-dig-in-interests-question-scale.png",
  "5:11": "cce-curriculum/resources/owner-authenticated-source/xello/2026-08-19/support-site/img-dig-in-interests-question-scale.png",
  "5:12": "cce-curriculum/resources/owner-authenticated-source/xello/2026-08-19/support-site/img-find-out-why.png",
  "5:13": "cce-curriculum/resources/owner-authenticated-source/xello/2026-08-19/support-site/img-find-out-why.png",
  "5:14": "cce-curriculum/resources/owner-authenticated-source/xello/2026-08-19/support-site/img-find-out-why.png",
};

const VISUAL_FALLBACKS = {
  1: [
    "cce-curriculum/resources/canvas-licensed/1sw/wk1/day1/hnl-manufacturing-cluster-current.png",
    "cce-curriculum/resources/canvas-licensed/1sw/wk1/day1/manufacturing-chapter-opener.jpg",
    "cce-curriculum/resources/canvas-licensed/1sw/wk1/day1/hnl-manufacturing-pathways-current.png",
    "cce-curriculum/resources/canvas-licensed/1sw/wk1/day1/hnl-robotics-hat-preview-current.png",
  ],
  2: [
    "cce-curriculum/resources/canvas-licensed/1sw/wk1/day2/machine-breakdown-clues.jpg",
    "cce-curriculum/resources/canvas-licensed/1sw/wk1/day2/technician-checklist.png",
    "cce-curriculum/resources/canvas-licensed/1sw/wk1/day1/hnl-robotics-automation-pathway-current.png",
  ],
  3: [
    "cce-curriculum/resources/canvas-licensed/1sw/wk1/day3/bike-rack-design-brief.png",
    "cce-curriculum/resources/canvas-licensed/1sw/wk1/day3/metals-and-welding-methods.png",
    "cce-curriculum/resources/canvas-licensed/1sw/wk1/day3/build-and-test-prototype.jpg",
  ],
  4: [
    "cce-curriculum/resources/canvas-licensed/1sw/wk1/day4/robots-for-crayons-problems.png",
    "cce-curriculum/resources/canvas-licensed/1sw/wk1/day4/how-the-machines-work.png",
    "cce-curriculum/resources/canvas-licensed/1sw/wk1/day4/shift-notes-and-impact-report.png",
    "cce-curriculum/resources/canvas-licensed/1sw/wk1/day5/robots-for-crayons-action-plan.png",
  ],
  5: [
    "cce-curriculum/resources/owner-authenticated-source/xello/2026-08-19/matchmaker-landing.png",
    "cce-curriculum/resources/owner-authenticated-source/xello/2026-08-19/matchmaker-prerequisite-goal.png",
    "cce-curriculum/resources/owner-authenticated-source/xello/2026-08-19/support-site/img-dig-in-interests-question-scale.png",
    "cce-curriculum/resources/owner-authenticated-source/xello/2026-08-19/support-site/img-find-out-why.png",
    "cce-curriculum/resources/owner-authenticated-source/xello/2026-08-19/classlink-launchpad-xello-hl-tiles.png",
    "cce-curriculum/resources/owner-authenticated-source/xello/2026-08-19/xello-student-dashboard.png",
  ],
};

function contentType(file) {
  const ext = path.extname(file).toLowerCase();
  return ext === ".jpg" || ext === ".jpeg" ? "image/jpeg" : "image/png";
}
function cleanMarker(value) {
  return value.replace(/^\s*(?:[•●▪✓]|\d+[.)])\s*/, "").trim();
}
function lines(values) {
  return values
    .flatMap((value) => String(value ?? "").split("\n"))
    .flatMap((line) => {
      const parts = line.split(/\s+•\s+/).map((part) => part.trim()).filter(Boolean);
      if (parts.length <= 1) return parts;
      return [parts[0], ...parts.slice(1).map((part) => `• ${part}`)];
    })
    .map((line) => line.trim())
    .filter(Boolean);
}
function titleFor(day, slideNumber, raw) {
  return TITLE_OVERRIDES[`${day}:${slideNumber}`] ?? raw.texts[0];
}
function contentFor(day, slideNumber, raw, title) {
  if (CONTENT_OVERRIDES[`${day}:${slideNumber}`]) return CONTENT_OVERRIDES[`${day}:${slideNumber}`];
  const remove = new Set([title, "Welcome!", "Today’s Lesson", "Get Ready", "Discussion"]);
  return lines(raw.texts).filter((line) => !remove.has(line));
}
function visualFor(day, slideNumber, raw) {
  const record = [...(raw.images ?? []), ...(raw.addImages ?? [])][0];
  const override = VISUAL_OVERRIDES[`${day}:${slideNumber}`];
  const relative = override ?? record?.path ?? VISUAL_FALLBACKS[day][(slideNumber - 1) % VISUAL_FALLBACKS[day].length];
  return {
    path: path.join(root, relative),
    alt: record?.alt ?? `Instructional visual for Day ${day}, slide ${slideNumber}`,
    explicit: Boolean(record),
  };
}
function sourceNotes(rawConfig, raw) {
  return [...(rawConfig.sources ?? []), ...(raw.sources ?? [])];
}
function notesText(day, title, rawConfig, raw) {
  return [
    `Time: ${raw.timing}`,
    `Teacher move: Project ${title}. Model the visible action or example, then release students when the completion cue is clear.`,
    `Student action: Complete the action shown on the slide.`,
    `Look-for: ${raw.lookFor}`,
    `Pivot/trim: ${raw.pivot} Trim: ${raw.trim ?? "Model one example and protect student work time."}`,
    `Recovery/access: ${raw.recovery ?? rawConfig.recovery}`,
    "[Sources]",
    ...sourceNotes(rawConfig, raw).map((source) => `- ${source}`),
    "[/Sources]",
  ];
}

function shape(slide, name, position, fill, line = { style: "solid", fill: "none", width: 0 }, radius = "rounded-2xl") {
  return slide.shapes.add({ geometry: "roundRect", name, position, fill, line, borderRadius: radius });
}
function addText(slide, name, value, position, style = {}) {
  const item = slide.shapes.add({ geometry: "textbox", name, position, fill: "none", line: { style: "solid", fill: "none", width: 0 } });
  item.text = value;
  item.text.style = {
    typeface: "Arial", fontSize: 28, color: C.ink, autoFit: "none", wrap: "square",
    verticalAlignment: "top", insets: { top: 0, right: 0, bottom: 0, left: 0 }, ...style,
  };
  return item;
}
async function addImage(slide, visual, position, { fit = "contain", crop, radius = "rounded-2xl", name = "instructional-visual" } = {}) {
  const options = {
    blob: await fs.readFile(visual.path), contentType: contentType(visual.path), alt: visual.alt,
    fit, position, geometry: "roundRect", borderRadius: radius, name,
  };
  if (crop) options.crop = crop;
  return slide.images.add(options);
}
async function addBackground(slide, name) {
  await addImage(slide, { path: path.join(here, `assets/bg-${name}.png`), alt: "Decorative CCE background" }, { left: 0, top: 0, width: 1280, height: 720 }, { fit: "cover", radius: 0, name: "decorative-background" });
}
function addTitle(slide, day, title, accent) {
  const titleSize = title.length > 55 ? 36 : title.length > 42 ? 41 : title.length > 30 ? 46 : 50;
  addText(slide, "title", title, { left: 72, top: 48, width: 990, height: 72 }, { fontSize: titleSize, bold: true, color: C.navy, verticalAlignment: "middle" });
  shape(slide, "day-chip", { left: 1080, top: 46, width: 120, height: 42 }, C.navy, undefined, "rounded-xl");
  addText(slide, "day-chip-label", `DAY ${day}`, { left: 1080, top: 46, width: 120, height: 42 }, { fontSize: 18, bold: true, color: C.white, alignment: "center", verticalAlignment: "middle" });
  shape(slide, "title-accent", { left: 72, top: 30, width: 98, height: 9 }, accent, undefined, "rounded-xl");
}
function addFooter(slide, label) {
  addText(slide, "footer-label", label.toUpperCase(), { left: 76, top: 636, width: 500, height: 22 }, { fontSize: 14, bold: true, color: C.teal });
}
function addBodyParagraphs(slide, content, position, { fontSize = 27, max = 8, accent = C.teal } = {}) {
  const selected = content.slice(0, max);
  const paragraphs = selected.map((line) => {
    const bullet = /^[•●▪✓]/.test(line);
    const cleaned = cleanMarker(line);
    const label = /^[A-Z0-9 &+→-]{3,32}$/.test(cleaned) && !/[.!?]$/.test(cleaned);
    return {
      ...(bullet ? { bulletCharacter: "•", marginLeft: 24, indent: -14 } : {}),
      spaceAfter: label ? 4 : 13,
      runs: [{ run: cleaned, textStyle: { bold: label, color: label ? accent : C.ink } }],
    };
  });
  return addText(slide, "body", paragraphs, position, { fontSize, lineSpacing: 1.02 });
}
function extractSteps(content) {
  const numbered = content.filter((line) => /^\d+[.)]/.test(line));
  const candidates = numbered.length ? numbered : content.filter((line) => !/^(DONE WHEN|VOICE|SOURCE|EXAMPLE)/i.test(line));
  return candidates.slice(0, 5).map(cleanMarker);
}
function addStepRows(slide, steps, position, { fontSize = 29, accent = C.plum, start = 1 } = {}) {
  const rowH = Math.min(70, position.height / Math.max(steps.length, 1));
  steps.forEach((step, index) => {
    const top = position.top + index * rowH;
    const badge = shape(slide, `step-${index + 1}-number`, { left: position.left, top: top + 3, width: 42, height: 42 }, accent, undefined, "rounded-xl");
    addText(slide, `step-${index + 1}-number-label`, String(start + index), { left: position.left, top: top + 3, width: 42, height: 42 }, { fontSize: 20, bold: true, color: C.white, alignment: "center", verticalAlignment: "middle" });
    addText(slide, `step-${index + 1}-text`, step, { left: position.left + 58, top, width: position.width - 58, height: rowH - 4 }, { fontSize, bold: index === steps.length - 1, color: C.ink, verticalAlignment: "middle" });
  });
}
function addTimer(slide, raw, position, accent) {
  const match = String(raw.timing ?? "").match(/(\d+):(\d+)-(\d+):(\d+)/);
  let label = "WORK TIME";
  if (match) {
    const minutes = Number(match[3]) * 60 + Number(match[4]) - (Number(match[1]) * 60 + Number(match[2]));
    if (minutes > 0 && minutes <= 20) label = `${minutes} MINUTES`;
  }
  const timer = shape(slide, "timer", position, accent, undefined, "rounded-xl");
  timer.text = label;
  timer.text.style = { typeface: "Arial", fontSize: 20, bold: true, color: C.white, alignment: "center", verticalAlignment: "middle", autoFit: "none" };
}
function addDoneWhen(slide, content, position, override) {
  const doneIndex = content.findIndex((line) => /^DONE WHEN/i.test(line));
  let done = override ?? (doneIndex >= 0 ? content[doneIndex].replace(/^DONE WHEN\s*:?\s*/i, "") : "");
  if (!done && doneIndex >= 0) done = content.slice(doneIndex + 1, doneIndex + 4).map(cleanMarker).join(" • ");
  if (!done) done = content.at(-1) ?? "Complete the visible action.";
  const panel = shape(slide, "done-when", position, "#E7F5F2", { style: "solid", fill: "#B8DDD5", width: 1 }, "rounded-xl");
  panel.text = [{ runs: [{ run: "DONE WHEN  ", textStyle: { bold: true, color: C.teal } }, { run: cleanMarker(done), textStyle: { color: C.ink } }] }];
  panel.text.style = { typeface: "Arial", fontSize: done.length > 95 ? 17 : done.length > 70 ? 19 : 22, verticalAlignment: "middle", autoFit: "none", insets: { top: 6, right: 15, bottom: 6, left: 15 } };
}
function visualCrop(day, slideNumber, visual) {
  if (day === 1 && slideNumber === 7 && visual.path.includes("manufacturing-chapter-opener")) return { top: 0.50, left: 0.02, right: 0.02, bottom: 0.01 };
  if (day === 1 && slideNumber === 9 && visual.path.includes("manufacturing-chapter-opener")) return { top: 0.48, left: 0.02, right: 0.02, bottom: 0.01 };
  if (day === 2 && [6, 7, 8].includes(slideNumber) && visual.path.includes("machine-breakdown-clues")) return { top: 0.01, left: 0.01, right: 0.57, bottom: 0.64 };
  if (day === 2 && [15, 16].includes(slideNumber) && visual.path.includes("machine-breakdown-clues")) return { top: 0.71, left: 0.53, right: 0.02, bottom: 0.02 };
  if (day === 3 && [8, 9].includes(slideNumber) && visual.path.includes("build-and-test-prototype")) return { top: 0.02, left: 0.44, right: 0.02, bottom: 0.69 };
  if (day === 3 && slideNumber === 14 && visual.path.includes("build-and-test-prototype")) return { top: 0.53, left: 0.02, right: 0.56, bottom: 0.02 };
  return undefined;
}

async function renderCover(slide, day, meta) {
  await addBackground(slide, "split");
  addText(slide, "eyebrow", `${meta.day} · CCE 1SW`, { left: 78, top: 110, width: 500, height: 34 }, { fontSize: 18, bold: true, color: meta.accent });
  addText(slide, "cover-title", meta.title, { left: 76, top: 158, width: 560, height: 155 }, { fontSize: meta.title.length > 24 ? 56 : 62, bold: true, color: C.navy, verticalAlignment: "middle" });
  addText(slide, "cover-subtitle", meta.subtitle, { left: 80, top: 336, width: 520, height: 82 }, { fontSize: 28, color: C.muted });
  addText(slide, "cover-purpose", "Today: learn it → try it → show it", { left: 80, top: 520, width: 480, height: 44 }, { fontSize: 22, bold: true, color: C.teal });
  await addImage(slide, { path: path.join(root, meta.hero), alt: `${meta.title} lesson visual` }, { left: 690, top: 125, width: 474, height: 430 }, { fit: meta.hero.endsWith(".jpg") ? "cover" : "contain" });
}
async function renderContract(slide, day, meta) {
  await addBackground(slide, "split");
  addTitle(slide, day, "Today’s Learning", meta.accent); addFooter(slide, meta.day);
  const left = shape(slide, "objective-panel", { left: 78, top: 160, width: 530, height: 238 }, C.cream, { style: "solid", fill: "#F1D98F", width: 1 }, "rounded-2xl");
  left.text = [{ runs: [{ run: "I CAN\n", textStyle: { bold: true, color: C.gold } }, { run: meta.objective, textStyle: { color: C.ink } }] }];
  left.text.style = { typeface: "Arial", fontSize: 29, verticalAlignment: "middle", autoFit: "none", insets: { top: 22, right: 24, bottom: 22, left: 24 } };
  const right = shape(slide, "evidence-panel", { left: 644, top: 160, width: 530, height: 238 }, C.paleTeal, { style: "solid", fill: "#B8DDD5", width: 1 }, "rounded-2xl");
  right.text = [{ runs: [{ run: "SHOW YOUR LEARNING\n", textStyle: { bold: true, color: C.teal } }, { run: meta.evidence, textStyle: { color: C.ink } }] }];
  right.text.style = { typeface: "Arial", fontSize: 28, verticalAlignment: "middle", autoFit: "none", insets: { top: 22, right: 24, bottom: 22, left: 24 } };
  addText(slide, "roadmap", "1  GET READY     2  PRACTICE     3  SHOW WHAT YOU KNOW", { left: 132, top: 476, width: 1010, height: 60 }, { fontSize: 25, bold: true, color: C.navy, alignment: "center", verticalAlignment: "middle" });
}
async function renderWelcome(slide, day, title, content, visual, meta) {
  await addBackground(slide, "left-media"); addTitle(slide, day, title, meta.accent); addFooter(slide, "As You Enter");
  const midpoint = Math.ceil(content.length / 2);
  addText(slide, "ready-label", "GET READY", { left: 78, top: 150, width: 230, height: 30 }, { fontSize: 18, bold: true, color: C.teal });
  addBodyParagraphs(slide, content.slice(0, midpoint), { left: 78, top: 194, width: 500, height: 210 }, { fontSize: 25, max: 5, accent: C.teal });
  addText(slide, "lesson-label", "TODAY", { left: 78, top: 430, width: 230, height: 30 }, { fontSize: 18, bold: true, color: C.plum });
  addBodyParagraphs(slide, content.slice(midpoint), { left: 78, top: 470, width: 520, height: 140 }, { fontSize: 24, max: 4, accent: C.plum });
  await addImage(slide, visual, { left: 730, top: 178, width: 440, height: 330 }, { fit: "contain" });
}
async function renderDoNow(slide, day, title, content, visual, meta, raw) {
  await addBackground(slide, "left-media"); addTitle(slide, day, title, meta.accent); addFooter(slide, "Do Now");
  const question = content.filter((line) => !/^Word Bank/i.test(line)).slice(0, 4);
  addBodyParagraphs(slide, question, { left: 80, top: 164, width: 540, height: 290 }, { fontSize: 30, max: 4, accent: meta.accent });
  addTimer(slide, raw, { left: 82, top: 512, width: 200, height: 58 }, meta.accent);
  await addImage(slide, visual, { left: 720, top: 176, width: 456, height: 342 }, { fit: "contain" });
}
async function renderConcept(slide, day, title, content, visual, meta) {
  await addBackground(slide, "left-media"); addTitle(slide, day, title, meta.accent); addFooter(slide, "Learn");
  addBodyParagraphs(slide, content, { left: 78, top: 160, width: 540, height: 430 }, { fontSize: content.length > 6 ? 24 : 29, max: 9, accent: meta.accent });
  await addImage(slide, visual, { left: 704, top: 168, width: 478, height: 360 }, { fit: visual.path.endsWith(".jpg") ? "cover" : "contain" });
}
async function renderSource(slide, day, title, content, visual, meta, slideNumber) {
  await addBackground(slide, "right-media"); addTitle(slide, day, title, meta.accent); addFooter(slide, "Source Zoom");
  const crop = visualCrop(day, slideNumber, visual);
  await addImage(slide, visual, { left: 82, top: 158, width: 520, height: 430 }, { fit: crop ? "cover" : "contain", crop });
  addBodyParagraphs(slide, content, { left: 662, top: 164, width: 510, height: 410 }, { fontSize: content.length > 7 ? 23 : 28, max: 9, accent: meta.accent });
}
async function renderPlatform(slide, day, slideNumber, title, content, visual, meta, raw) {
  await addBackground(slide, title.toLowerCase().includes("tour") ? "video" : "left-media"); addTitle(slide, day, title, meta.accent); addFooter(slide, "Exact Path");
  const steps = STEP_OVERRIDES[`${day}:${slideNumber}`] ?? extractSteps(content);
  addStepRows(slide, steps.length ? steps : content.slice(0, 4), { left: 80, top: 160, width: 530, height: 280 }, { fontSize: steps.length > 4 ? 25 : 29, accent: meta.accent });
  addDoneWhen(slide, content, { left: 78, top: 512, width: 530, height: 80 }, DONE_OVERRIDES[`${day}:${slideNumber}`]);
  const crop = visualCrop(day, slideNumber, visual);
  await addImage(slide, visual, { left: 710, top: 178, width: 460, height: 330 }, { fit: crop ? "cover" : "contain", crop });
  if (title.toLowerCase().includes("tour")) addTimer(slide, raw, { left: 710, top: 535, width: 210, height: 56 }, meta.accent);
}
async function renderProcess(slide, day, slideNumber, title, content, visual, meta) {
  await addBackground(slide, "left-media"); addTitle(slide, day, title, meta.accent); addFooter(slide, "Process");
  const steps = extractSteps(content);
  const rangeStart = Number(title.match(/(?:Checklist:\s*)?(\d+)\s*[–-]\s*\d+/)?.[1] ?? 1);
  addStepRows(slide, steps.length ? steps : content.slice(0, 5), { left: 80, top: 160, width: 560, height: 400 }, { fontSize: steps.length > 4 ? 25 : 29, accent: meta.accent, start: rangeStart });
  const crop = visualCrop(day, slideNumber, visual);
  await addImage(slide, visual, { left: 726, top: 182, width: 432, height: 330 }, { fit: crop ? "cover" : "contain", crop });
}
async function renderCompare(slide, day, title, content, visual, meta) {
  await addBackground(slide, "split"); addTitle(slide, day, title, meta.accent); addFooter(slide, "Compare");
  const mid = Math.max(1, Math.ceil(content.length / 2));
  addBodyParagraphs(slide, content.slice(0, mid), { left: 88, top: 166, width: 500, height: 400 }, { fontSize: 25, max: 8, accent: meta.accent });
  shape(slide, "column-divider", { left: 628, top: 164, width: 4, height: 390 }, meta.accent, undefined, 0);
  addBodyParagraphs(slide, content.slice(mid), { left: 672, top: 166, width: 500, height: 400 }, { fontSize: 25, max: 8, accent: meta.accent });
}
async function renderModel(slide, day, title, content, visual, meta) {
  await addBackground(slide, "right-media"); addTitle(slide, day, title, meta.accent); addFooter(slide, "Worked Model");
  await addImage(slide, visual, { left: 82, top: 166, width: 485, height: 390 }, { fit: "contain" });
  const model = shape(slide, "model-panel", { left: 620, top: 156, width: 560, height: 420 }, C.cream, { style: "solid", fill: "#F1D98F", width: 1 }, "rounded-2xl");
  model.text = content.slice(0, 8).map((line) => ({ spaceAfter: 10, runs: [{ run: cleanMarker(line), textStyle: { bold: /^[A-Z0-9 &+→-]{3,32}$/.test(cleanMarker(line)), color: C.ink } }] }));
  model.text.style = { typeface: "Arial", fontSize: content.join(" ").length > 380 ? 21 : 25, lineSpacing: 1.0, autoFit: "none", insets: { top: 22, right: 24, bottom: 22, left: 24 } };
}
async function renderPartner(slide, day, slideNumber, title, content, visual, meta, raw) {
  await addBackground(slide, "split"); addTitle(slide, day, title, meta.accent); addFooter(slide, "Partner Check");
  const override = PARTNER_OVERRIDES[`${day}:${slideNumber}`];
  const mid = Math.max(1, Math.ceil(content.length / 2));
  const aLines = override?.a ?? content.slice(0, mid).map(cleanMarker);
  const bLines = override?.b ?? content.slice(mid).map(cleanMarker);
  const a = shape(slide, "partner-a", { left: 78, top: 160, width: 520, height: 330 }, C.paleTeal, { style: "solid", fill: "#B8DDD5", width: 1 }, "rounded-2xl");
  a.text = [{ runs: [{ run: "PARTNER A\n", textStyle: { bold: true, color: C.teal } }, { run: aLines.join("\n"), textStyle: { color: C.ink } }] }];
  a.text.style = { typeface: "Arial", fontSize: 26, autoFit: "none", insets: { top: 22, right: 24, bottom: 22, left: 24 } };
  const b = shape(slide, "partner-b", { left: 654, top: 160, width: 520, height: 330 }, "#EEE7F5", { style: "solid", fill: "#D5C2E3", width: 1 }, "rounded-2xl");
  b.text = [{ runs: [{ run: "PARTNER B\n", textStyle: { bold: true, color: C.plum } }, { run: bLines.join("\n"), textStyle: { color: C.ink } }] }];
  b.text.style = { typeface: "Arial", fontSize: 26, autoFit: "none", insets: { top: 22, right: 24, bottom: 22, left: 24 } };
  addTimer(slide, raw, { left: 520, top: 528, width: 240, height: 58 }, meta.accent);
}
async function renderWork(slide, day, slideNumber, title, content, visual, meta, raw) {
  await addBackground(slide, "left-media"); addTitle(slide, day, title, meta.accent); addFooter(slide, "Work Block");
  const doneIndex = content.findIndex((line) => /^DONE WHEN/i.test(line));
  const workContent = doneIndex >= 0 ? content.slice(0, doneIndex) : content;
  addBodyParagraphs(slide, workContent, { left: 78, top: 158, width: 550, height: 330 }, { fontSize: workContent.length > 8 ? 22 : 26, max: 10, accent: meta.accent });
  addTimer(slide, raw, { left: 82, top: 530, width: 220, height: 58 }, meta.accent);
  const checklist = WORK_CHECKLIST_OVERRIDES[`${day}:${slideNumber}`];
  if (checklist) {
    const panel = shape(slide, "response-home-panel", { left: 690, top: 168, width: 500, height: 338 }, C.paleTeal, { style: "solid", fill: "#B8DDD5", width: 1 }, "rounded-2xl");
    addText(slide, "response-home-label", "IN TODAY'S RESPONSE PAGE", { left: 724, top: 196, width: 430, height: 34 }, { fontSize: 18, bold: true, color: C.teal, alignment: "center" });
    checklist.forEach((item, index) => {
      shape(slide, `work-check-${index + 1}`, { left: 730, top: 252 + index * 57, width: 30, height: 30 }, C.white, { style: "solid", fill: meta.accent, width: 2 }, "rounded-md");
      addText(slide, `work-check-${index + 1}-text`, item, { left: 778, top: 247 + index * 57, width: 370, height: 42 }, { fontSize: 23, bold: index === 0, verticalAlignment: "middle" });
    });
  } else {
    await addImage(slide, visual, { left: 716, top: 176, width: 450, height: 330 }, { fit: visual.path.endsWith(".jpg") ? "cover" : "contain" });
  }
  addDoneWhen(slide, [...content, `DONE WHEN: ${raw.lookFor}`], { left: 690, top: 526, width: 500, height: 70 }, DONE_OVERRIDES[`${day}:${slideNumber}`]);
}
async function renderComplete(slide, day, slideNumber, title, content, visual, meta) {
  await addBackground(slide, "left-media"); addTitle(slide, day, title, meta.accent); addFooter(slide, "Show Your Learning");
  const checks = content.filter((line) => !/^(EACH|DONE|WORK BLOCK)/i.test(line)).slice(0, 4).map(cleanMarker);
  checks.forEach((check, index) => {
    const top = 166 + index * 86;
    shape(slide, `check-${index + 1}`, { left: 82, top, width: 44, height: 44 }, C.white, { style: "solid", fill: meta.accent, width: 3 }, "rounded-md");
    addText(slide, `check-${index + 1}-text`, check, { left: 146, top: top - 3, width: 480, height: 68 }, { fontSize: 25, bold: index === 0, verticalAlignment: "middle" });
  });
  const crop = visualCrop(day, slideNumber, visual);
  await addImage(slide, visual, { left: 720, top: 176, width: 452, height: 330 }, { fit: crop ? "cover" : "contain", crop });
  addDoneWhen(slide, [meta.evidence], { left: 708, top: 526, width: 480, height: 74 }, DONE_OVERRIDES[`${day}:${slideNumber}`]);
}
async function renderClose(slide, day, slideNumber, title, content, visual, meta) {
  await addBackground(slide, "left-media"); addTitle(slide, day, title, meta.accent); addFooter(slide, "Close");
  const stems = content.filter((line) => !/^Photo by|^Image by/i.test(line)).slice(0, 4);
  stems.forEach((stem, index) => {
    const top = 170 + index * 98;
    addText(slide, `reflection-${index + 1}`, cleanMarker(stem), { left: 84, top, width: 570, height: 70 }, { fontSize: 28, bold: index === 0, color: index === 0 ? C.navy : C.ink });
    shape(slide, `reflection-line-${index + 1}`, { left: 84, top: top + 66, width: 530, height: 3 }, meta.accent, undefined, 0);
  });
  const crop = visualCrop(day, slideNumber, visual);
  await addImage(slide, visual, { left: 720, top: 176, width: 450, height: 330 }, { fit: crop || visual.path.endsWith(".jpg") ? "cover" : "contain", crop });
  addText(slide, "next-label", "NEXT", { left: 720, top: 534, width: 90, height: 28 }, { fontSize: 16, bold: true, color: C.teal });
  addText(slide, "next-text", NEXT_OVERRIDES[`${day}:${slideNumber}`] ?? meta.subtitle, { left: 810, top: 530, width: 360, height: 50 }, { fontSize: 20, bold: true, color: C.navy });
}

async function renderSlide(presentation, day, slideNumber, rawConfig, raw, meta) {
  const layout = meta.layouts[slideNumber - 1];
  const slide = presentation.slides.add();
  const title = titleFor(day, slideNumber, raw);
  const content = contentFor(day, slideNumber, raw, title);
  const visual = visualFor(day, slideNumber, raw);
  if (layout === "A") await renderCover(slide, day, meta);
  else if (layout === "C") await renderContract(slide, day, meta);
  else if (layout === "B") await renderWelcome(slide, day, title, content, visual, meta);
  else if (layout === "D") await renderDoNow(slide, day, title, content, visual, meta, raw);
  else if (layout === "E") await renderConcept(slide, day, title, content, visual, meta);
  else if (layout === "F") await renderSource(slide, day, title, content, visual, meta, slideNumber);
  else if (layout === "G") await renderPlatform(slide, day, slideNumber, title, content, visual, meta, raw);
  else if (layout === "H") await renderProcess(slide, day, slideNumber, title, content, visual, meta);
  else if (layout === "I") await renderCompare(slide, day, title, content, visual, meta);
  else if (layout === "J") await renderModel(slide, day, title, content, visual, meta);
  else if (layout === "K") await renderPartner(slide, day, slideNumber, title, content, visual, meta, raw);
  else if (layout === "L") await renderWork(slide, day, slideNumber, title, content, visual, meta, raw);
  else if (layout === "M") await renderComplete(slide, day, slideNumber, title, content, visual, meta);
  else if (layout === "N") await renderClose(slide, day, slideNumber, title, content, visual, meta);
  else throw new Error(`Unknown layout ${layout} for Day ${day} slide ${slideNumber}`);
  slide.speakerNotes.textFrame.setText(notesText(day, title, rawConfig, raw));
}

for (const day of days) {
  const rawConfig = JSON.parse(await fs.readFile(path.join(sourceDir, `day${day}.json`), "utf8"));
  const meta = DECK[day];
  if (rawConfig.slides.length !== meta.layouts.length) throw new Error(`Day ${day} layout map mismatch`);
  const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
  for (let index = 0; index < rawConfig.slides.length; index += 1) {
    await renderSlide(presentation, day, index + 1, rawConfig, rawConfig.slides[index], meta);
  }
  const dayDir = path.join(previewRoot, `day${day}`);
  const renderDir = path.join(dayDir, "artifact-render");
  const layoutDir = path.join(dayDir, "layout");
  await fs.rm(dayDir, { recursive: true, force: true });
  await fs.mkdir(renderDir, { recursive: true });
  await fs.mkdir(layoutDir, { recursive: true });
  for (let index = 0; index < presentation.slides.items.length; index += 1) {
    const slide = presentation.slides.items[index];
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    const png = await presentation.export({ slide, format: "png", scale: 2 });
    await fs.writeFile(path.join(renderDir, `${stem}.png`), Buffer.from(await png.arrayBuffer()));
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(path.join(layoutDir, `${stem}.layout.json`), await layout.text());
  }
  const pptxPath = path.join(dayDir, `cce-1sw-wk1-day${day}-manufacturing-agentic.pptx`);
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(pptxPath);
  console.log(JSON.stringify({ day, pptxPath, slides: presentation.slides.items.length, renderDir, layoutDir }));
}
