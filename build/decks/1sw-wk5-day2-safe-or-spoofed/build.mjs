import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { chromium } from "playwright";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const PROJECT_ROOT = process.env.CCE_PROJECT_ROOT;
const TMP_DIR = process.env.CCE_DECK_TMP;
const FINAL_DIR = process.env.CCE_DECK_FINAL;

if (!PROJECT_ROOT || !TMP_DIR || !FINAL_DIR) {
  throw new Error("Set CCE_PROJECT_ROOT, CCE_DECK_TMP, and CCE_DECK_FINAL.");
}

const htmlPath = path.join(
  PROJECT_ROOT,
  "build/decks/1sw-wk5-day2-safe-or-spoofed/deck.html",
);
const renderDir = path.join(TMP_DIR, "html-render");
const finalPptx = path.join(FINAL_DIR, "safe-or-spoofed-lesson-presentation.pptx");

const lessonSource =
  "Irving ISD College and Career Exploration, 1SW Wk5 Day 2 Teacher Facilitator Guide and Student Guide; local reviewed curriculum source.";
const hqimSource =
  "District-licensed HQIM; Find Your Future, pp. 24-25, Safe or Spoofed?; authenticated Canvas use only.";
const climberSource =
  "District-licensed HQIM; Hats & Ladders, Climber Notes: Safe or Spoofed?, slides 2-8; authenticated Canvas use only.";
const climberEmailSources = {
  1: "District-licensed HQIM; Hats & Ladders, Climber Notes: Safe or Spoofed?, slide 2, Email #1; authenticated Canvas use only.",
  2: "District-licensed HQIM; Hats & Ladders, Climber Notes: Safe or Spoofed?, slide 3, Email #2; authenticated Canvas use only.",
  3: "District-licensed HQIM; Hats & Ladders, Climber Notes: Safe or Spoofed?, slide 4, Email #3; authenticated Canvas use only.",
  4: "District-licensed HQIM; Hats & Ladders, Climber Notes: Safe or Spoofed?, slide 5, Email #4; authenticated Canvas use only.",
  5: "District-licensed HQIM; Hats & Ladders, Climber Notes: Safe or Spoofed?, slide 6, Email #5; authenticated Canvas use only.",
  6: "District-licensed HQIM; Hats & Ladders, Climber Notes: Safe or Spoofed?, slide 7, Email #6; authenticated Canvas use only.",
  7: "District-licensed HQIM; Hats & Ladders, Climber Notes: Safe or Spoofed?, slide 8, Email #7; authenticated Canvas use only.",
};
const cisaSource =
  "Cybersecurity and Infrastructure Security Agency, Secure Our World, Recognize and Report Phishing, https://www.cisa.gov/secure-our-world and https://www.cisa.gov/sites/default/files/2024-12/Secure-Our-World-Shop-Safely-Holiday-Season-Tip-Sheet.pdf; U.S. government resource; accessed 2026-08-10.";

function notes({ time, teacher, students, monitor, support, trim, sources }) {
  return [
    `Time: ${time}`,
    `Teacher move: ${teacher}`,
    `Students: ${students}`,
    `Monitor/listen for: ${monitor}`,
    `Support: ${support}`,
    `Trim/recovery: ${trim}`,
    "",
    "[Sources]",
    ...sources,
  ].join("\n");
}

const speakerNotes = [
  notes({time:"30 seconds",teacher:"Open the lesson and name the Topic. Do not teach the red flags yet.",students:"Get the workbook or Canvas guide and the red-flag checklist ready.",monitor:"Materials are open before the bellringer begins.",support:"Read the subtitle aloud; point to the three verbs.",trim:"Do not cut this orientation slide.",sources:[lessonSource]}),
  notes({time:"4 minutes total bellringer; hold this frame for 60 seconds before discussion",teacher:"Project Email 1. Ask for observations only. Take two responses, then save the decision for the model.",students:"Write one visible clue, then share one observation.",monitor:"Students point to sender, pressure, or link evidence without clicking.",support:"Read the sender string aloud and enlarge if needed.",trim:"Keep at least one written observation and one share.",sources:[climberEmailSources[1], lessonSource]}),
  notes({time:"1.5 minutes",teacher:"Read the objective and Demonstration of Learning in student language. Connect integrity to careful evidence and protecting people.",students:"Paraphrase what they will produce.",monitor:"Students understand this is not a guessing contest.",support:"Preteach integrity as honest, careful, and responsible use of access.",trim:"Do not cut the DOL preview.",sources:[lessonSource]}),
  notes({time:"2 minutes",teacher:"Model the difference between observation and decision with the two sentences. Ask which one can be pointed to in the message.",students:"Label one statement evidence and one statement decision.",monitor:"Students do not treat a conclusion as evidence.",support:"Use the complete frame: I can see ___. That supports the decision ___ because ___.",trim:"If behind, model only the two printed sentences.",sources:[climberEmailSources[1], lessonSource]}),
  notes({time:"30 seconds",teacher:"Preview the four lesson moves and check that every student has the response surface.",students:"Open the checklist/workbook page.",monitor:"No student is waiting for a live email account.",support:"Point to each verb as it is read.",trim:"Keep the four-step preview under 30 seconds.",sources:[lessonSource]}),
  notes({time:"5 minutes",teacher:"Teach one clue at a time from FYF p.24. After each clue, ask for a quick example from the projected fictional messages.",students:"Mark or track the five clue categories.",monitor:"Students understand that a typo is one clue, not proof.",support:"Read the list aloud; pair each term with the printed visual.",trim:"Combine clues 4 and 5 if needed, but preserve the boundary statements.",sources:[hqimSource, lessonSource]}),
  notes({time:"1.5 minutes",teacher:"Contrast a typo with a mismatched domain. Explain that stronger evidence is more directly connected to identity or destination.",students:"Identify which clue deserves more weight.",monitor:"Students stop treating grammar as the deciding feature.",support:"Say domain means the main web/address ending after the @ sign or in the link.",trim:"This slide can merge into the next Q-SSA if needed.",sources:[lessonSource, cisaSource]}),
  notes({time:"2 minutes",teacher:"Run Q-SSA: ask the question, students signal 1 or 2, use the complete stem with a partner, then sample two answers and pivot if fewer than about 80% choose 2.",students:"Signal, complete the stem, and share evidence.",monitor:"Most students select the mismatched domain and explain why it is stronger.",support:"Let students point before speaking; read the full stem aloud.",trim:"If time is short, keep signal plus one model response.",sources:[lessonSource]}),
  notes({time:"1.5 minutes",teacher:"State that polished is not proven safe. Model opening a known portal independently rather than using message contact details.",students:"Name one independent verification route.",monitor:"Students do not say reply, forward, or call the number inside the message.",support:"Offer: official app, typed website, known adult/teacher/IT contact.",trim:"Do not cut this safety boundary.",sources:[cisaSource, lessonSource]}),
  notes({time:"1.5 minutes",teacher:"Model the Inspect-Decide-Respond routine. Keep the decision labels Safe-looking and Spoofed.",students:"Practice the complete response frame once.",monitor:"Every answer includes evidence plus a route.",support:"Keep the frame projected during the first model.",trim:"If behind, read only the three verbs and the frame.",sources:[lessonSource]}),
  notes({time:"1 minute",teacher:"Assign pairs or let adjacent students use the two roles. Explain that talk is shared but every row is individual evidence.",students:"Choose the first role and prepare to switch after Email 4.",monitor:"No student becomes a passive recorder for the entire task.",support:"Independent students use both roles silently; low-vision route uses teacher-read observable details.",trim:"Use independent mode if pairing would cost more than one minute.",sources:[lessonSource]}),
  notes({time:"2 minutes",teacher:"Guide Email 1. Ask students to point to evidence, then make the decision and name the safe response.",students:"Complete row 1.",monitor:"Prize pressure, odd sender, and unrelated claim link appear; no clicks.",support:"Read the sender and visible link aloud.",trim:"Do not cut the guided model.",sources:[climberEmailSources[1], lessonSource]}),
  notes({time:"1 minute",teacher:"Reveal the model reasoning. Emphasize that the clues work together.",students:"Revise row 1 if their evidence was vague.",monitor:"Students replace it looks fake with a visible clue.",support:"Read the complete model sentence aloud.",trim:"If behind, state the three clues orally and move on.",sources:[climberEmailSources[1], lessonSource]}),
  notes({time:"2 minutes",teacher:"Release Email 2. After individual think time, sample one clue and one verification route. Key: spoofed; amaz0n uses a zero and order-check domain is not official.",students:"Complete row 2.",monitor:"Students use the official order history rather than message link.",support:"Read the sender/domain aloud.",trim:"Reduce partner share to one response if needed.",sources:[climberEmailSources[2], lessonSource]}),
  notes({time:"2 minutes",teacher:"Release Email 3. Key: safe-looking, but verify through known HR or official portal if uncertain.",students:"Complete row 3 and avoid proven-safe language.",monitor:"Students recognize ordinary message/no link while preserving verification boundary.",support:"Offer the label safe-looking on the board.",trim:"Keep the decision and one reason.",sources:[climberEmailSources[3], lessonSource]}),
  notes({time:"2 minutes",teacher:"Release Email 4. Key: spoofed; .co sender, TODAY pressure, unrelated update domain.",students:"Complete row 4, then prepare for partner check.",monitor:"Students weigh domain/route more than tone alone.",support:"Read sender and destination domain aloud.",trim:"Do not cut the row; shorten discussion.",sources:[climberEmailSources[4], lessonSource]}),
  notes({time:"2 minutes",teacher:"Run Think-Pair-Share. Partner B asks the printed evidence question. Sample one strong answer and one answer needing revision.",students:"Defend one decision and revise a weak reason.",monitor:"Students point to evidence and name a safe action.",support:"Keep the complete stem visible; accept oral rehearsal before writing.",trim:"Use one pair exchange and skip whole-group share if behind.",sources:[lessonSource]}),
  notes({time:"2 minutes",teacher:"Make one active-monitoring lap. Check four rows, visible clues, one independent route, and zero clicks. If more than five students rely only on grammar, pause and remodel the domain clue.",students:"Repair missing or weak evidence before continuing.",monitor:"The four printed targets are met.",support:"Point to the exact incomplete cell rather than asking for more detail generally.",trim:"Do not skip the check; shorten the practice draft instead.",sources:[lessonSource]}),
  notes({time:"2 minutes",teacher:"Release Email 5. Key: spoofed; urgent suspension, one-hour deadline, unrelated fix domain. Safe response: known IT support.",students:"Complete row 5.",monitor:"Pressure is paired with a sender/domain clue.",support:"Read sender and deadline aloud.",trim:"Keep individual record; cut share.",sources:[climberEmailSources[5], lessonSource]}),
  notes({time:"2 minutes",teacher:"Release Email 6. Key: spoofed; .co sender and portal-login link. Safe response: open known portal independently.",students:"Complete row 6.",monitor:"Students do not treat a familiar logo as proof.",support:"Read sender and portal domain aloud.",trim:"Keep individual record; cut share.",sources:[climberEmailSources[6], lessonSource]}),
  notes({time:"2 minutes",teacher:"Release Email 7. Key: safe-looking ordinary manager note with no link/private request; verify through known manager/channel if uncertain.",students:"Complete row 7 using safe-looking language.",monitor:"Students can explain why no visible flag is not a guarantee.",support:"Allow students to state no visible red flag and then name the verification route.",trim:"Keep the decision, evidence, and route.",sources:[climberEmailSources[7], lessonSource]}),
  notes({time:"2 minutes",teacher:"Teach the four-part response. Emphasize no reply, no forwarding, and no contact information from the suspicious message.",students:"Rehearse the sequence with one message.",monitor:"Students verify independently before reporting/deleting.",support:"Use hand motions or point to each verb; keep the four words visible.",trim:"Do not cut this safety sequence.",sources:[cisaSource, lessonSource]}),
  notes({time:"2 minutes optional sketch",teacher:"Launch only a two-line fictional sender/subject/message sketch with strict boundaries. This is the first trim point.",students:"Sketch on paper/private assigned document; never send or post.",monitor:"No live links, QR codes, attachments, real identities, credentials, or district impersonation.",support:"Students may label two red flags instead of drafting complete prose.",trim:"Primary trim point: omit this slide before cutting the DOL.",sources:[hqimSource, lessonSource]}),
  notes({time:"5 minutes",teacher:"Read all three prompts. Collect or verify the completed checklist/assigned response.",students:"Complete the hardest-call, safe-response, and integrity lines.",monitor:"One visible clue, one independent route, and one honest/protective behavior appear.",support:"Read stems aloud; accept speech-to-text or teacher-recorded oral response when assigned.",trim:"Protected DOL; do not cut.",sources:[lessonSource]}),
  notes({time:"1 minute",teacher:"Run the final check and state the absence/catch-up route. Collect only the assigned evidence surface.",students:"Confirm all four completion conditions and submit/close materials.",monitor:"No one submits a live phishing message or extra worksheet.",support:"Direct absent students to the seven locked images and checklist.",trim:"Keep the completion check even in a shortened period.",sources:[lessonSource]}),
  notes({time:"Teacher reference - not part of the 50-minute flow",teacher:"Do not project during instruction unless asked about sources. Exact licensed slide references appear on each email slide; direct URLs and an access date appear for the current public guidance.",students:"No action.",monitor:"N/A",support:"N/A",trim:"This slide may remain at the end without classroom discussion.",sources:[hqimSource, climberSource, cisaSource, lessonSource]}),
];

const slideMinutes = [0.5,4,1.5,2,0.5,5,1.5,2,1.5,1.5,1,2,1,2,2,2,2,2,2,2,2,2,2,5,1,0];
if (slideMinutes.length !== speakerNotes.length) {
  throw new Error(`Minute map ${slideMinutes.length} does not match notes count ${speakerNotes.length}.`);
}
const instructionalMinutes = slideMinutes.reduce((sum, value) => sum + value, 0);
if (instructionalMinutes !== 50) {
  throw new Error(`Instructional deck must total 50 minutes; found ${instructionalMinutes}.`);
}

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function renderHtmlSlides() {
  await fs.rm(renderDir, { recursive: true, force: true });
  await fs.mkdir(renderDir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(htmlPath).href, { waitUntil: "networkidle" });
  const slides = page.locator("section.slide");
  const count = await slides.count();
  if (count !== speakerNotes.length) {
    throw new Error(`Slide count ${count} does not match notes count ${speakerNotes.length}.`);
  }
  for (let i = 0; i < count; i += 1) {
    const output = path.join(renderDir, `slide-${String(i + 1).padStart(2, "0")}.png`);
    await slides.nth(i).screenshot({ path: output });
  }
  await browser.close();
  return count;
}

async function assemblePptx(count) {
  await fs.mkdir(FINAL_DIR, { recursive: true });
  const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
  for (let i = 0; i < count; i += 1) {
    const pngPath = path.join(renderDir, `slide-${String(i + 1).padStart(2, "0")}.png`);
    const bytes = await fs.readFile(pngPath);
    const slide = presentation.slides.add();
    slide.images.add({
      blob: bytes,
      contentType: "image/png",
      alt: `Safe or Spoofed lesson presentation, slide ${i + 1}`,
      fit: "contain",
      position: { left: 0, top: 0, width: 1280, height: 720 },
    });
    slide.speakerNotes.textFrame.setText(speakerNotes[i]);
    slide.speakerNotes.setVisible(true);
  }
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(finalPptx);
}

const count = await renderHtmlSlides();
await assemblePptx(count);
await fs.writeFile(
  path.join(TMP_DIR, "source-notes.txt"),
  [hqimSource, climberSource, cisaSource, lessonSource].join("\n\n"),
);
console.log(JSON.stringify({ slideCount: count, renderDir, finalPptx }, null, 2));
