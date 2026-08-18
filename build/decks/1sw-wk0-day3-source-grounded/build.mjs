// CCE 1SW Wk0 Day 3 daily master: Work Values + Building Blocks.
// Source of truth: docs/1sw/wk0-classroom-routines/day3.md (50-minute flow).
// Starter: AVID Week 1.6 clone (Jenna Hainlen) for the cover and day divider only;
// every content slide is redrawn with editable shapes from build/decks/lib/slide_kit.mjs.
// Projected text is student-facing; teacher moves live in speaker notes.

import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadRuntime, openStarter, slideAt, addText, doNow, agenda, talk, guidedText, guidedScreen, recap, dol, setNotes, finalize,
} from "../lib/slide_kit.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../../..");
const workspace = path.join(root, "tmp/cce-week1-day3-source-clone");
const starterPath = path.join(workspace, "template-starter.pptx");
const outputPath = path.join(root, "cce-curriculum/resources/avid-reference/source/derived/cce-week1-day3-source-grounded.pptx");
const KICKER = "CCE WEEK 1 · WEDNESDAY";
const PAGE = "Work Values + Building Blocks – Day 3";

const hl = (name) => path.join(root, "cce-curriculum/resources/owner-authenticated-source/hats-and-ladders/screens", name);
const licensed = (name) => path.join(root, "cce-curriculum/resources/canvas-licensed/1sw/wk0/day3", name);
const assets = {
  workValuesCard: hl("work-values-profile-card.png"),
  workValuesStart: hl("work-values-start.png"),
  workValuesQuestion: hl("work-values-question.png"),
  workValuesResult: hl("work-values-result.png"),
  buildingBlockChoose: hl("building-block-choose.png"),
  buildingBlockDescribe: hl("building-block-describe.png"),
  fyfBuildingBlocks: licensed("my-building-blocks-introduction.png"),
};

const runtime = await loadRuntime();
const { presentation, textbox, setText } = await openStarter(runtime, starterPath);
const S = (n) => slideAt(presentation, n);

// 1-2: keep the AVID cover and day divider (structure credit in notes).
setText(1, "Week 1.6", "CCE Day 3");
textbox(1, "AVID 2\nMs. Hainlen").delete();
const subtitle = addText(S(1), "Work Values + Building Blocks\nCareer & College Explorations", { left: 150, top: 294, width: 675, height: 78 }, { fontSize: 20, bold: true, color: "#5A2D91" });
subtitle.text.style = { fontSize: 20, bold: true, color: "#5A2D91", fontFamily: "Aptos", alignment: "center" };
setText(2, "Friday", "Wednesday");

// 3: As You Enter + Do Now
doNow(S(3), {
  kicker: KICKER,
  materials: ["Your assigned Chromebook", "Find Your Future workbook, pp. 9–11", `OneNote → CCE Work → ${PAGE}`],
  prompt: "Which would you choose?\nHigher pay, working alone\nOR\nLower pay, with a team you enjoy",
  stem: "Write one reason: I chose ____ because ____.",
  done: "one choice and one reason are written on your Day 3 page.",
});

// 4: Today (objective + agenda)
agenda(S(4), {
  kicker: KICKER,
  objective: "I can use my Hats & Ladders work-values result and my own experiences to name one career cluster I may explore.",
  teks: "TEKS 127.2 (d)(1)(A) and (d)(1)(B)",
  steps: [
    "Discover Your Work Values in Hats & Ladders",
    "Record 3 Building Blocks in Find Your Future pp. 9–11",
    "Save the same 3 Building Blocks in Hats & Ladders",
    "Write one connection on your Day 3 page",
  ],
  done: "your H&L profile shows 3 Building Blocks and your connection is written",
});

// 5: Turn and talk on the Do Now
talk(S(5), {
  kicker: KICKER,
  title: "Share the value inside your reason",
  partnerA: "Read your Do Now reason out loud. About 30 seconds.",
  partnerB: "Name the value you hear: pay, team, independence, support, balance, or another word. Then switch.",
  privateOption: "Underline the word in your reason that shows what matters most to you.\n\nShow it to your teacher when asked.",
  done: "you can name one value inside your reason.",
});

// 6: The six work values (Climber Notes hook, plain words)
guidedText(S(6), {
  kicker: KICKER,
  title: "Six work values",
  bodySize: 21,
  body: "Achievement: reaching goals and seeing results\nIndependence: making your own choices\nRecognition: being noticed and rewarded\nRelationships: helping and working with people\nSupport: clear help and guidance\nWorking Conditions: schedule, tasks, place, and security\n\nWhich two sound most like you? Keep them in mind.",
  done: "you can say which two values sound most like you.",
});

// 7-10: Step 1, one action per screen
await guidedScreen(S(7), { kicker: KICKER, title: "Step 1 · Open Discover Your Work Values", screen: "The Work Values card in your H&L Profile Climbs", action: "Sign in with Google if you are not signed in.\nClick Discover Your Work Values.", done: "The Work Values start screen is open.", image: assets.workValuesCard, alt: "Hats and Ladders Profile Climbs card labeled Discover Your Work Values", callout: "CLICK" });
await guidedScreen(S(8), { kicker: KICKER, title: "Step 1 · Start", screen: "The Discover Your Work Values start card", action: "Read the directions.\nClick Start.", done: "The first pair of choices is open.", image: assets.workValuesStart, alt: "Hats and Ladders Discover Your Work Values start screen with Start button", callout: "GO" });
await guidedScreen(S(9), { kicker: KICKER, title: "Step 1 · Choose the better fit", screen: "Two work choices side by side", action: "Read both. Pick the one that fits you better. Click Next.\nAnswer honestly, not fast.", done: "The progress bar moves after each choice.", image: assets.workValuesQuestion, alt: "Hats and Ladders Work Values question with two choices and Next button", callout: "PICK" });
await guidedScreen(S(10), { kicker: KICKER, title: "Step 1 · Record your result", screen: "Your Work Values result with two value names", action: "On your Day 3 page write:\nMy top work values are ____ and ____.\nI expected / was surprised by ____ because ____.\nThen click Continue.", done: "Both values are on your page and H&L is back at your profile.", image: assets.workValuesResult, alt: "Hats and Ladders Work Values result showing two top values and Continue button", callout: "NOTE" });

// 11-13: Step 2, Building Blocks in FYF
await guidedScreen(S(11), { kicker: KICKER, title: "Step 2 · Open Find Your Future pp. 9–11", screen: "Find Your Future page 9: My Building Blocks", action: "Read the top box with your teacher.\nExperience is more than a paid job. School, home, community, and interests all count.", done: "You can name one thing you already do that counts as experience.", image: assets.fyfBuildingBlocks, alt: "Find Your Future page 9 introducing My Building Blocks", callout: "READ" });
guidedText(S(12), {
  kicker: KICKER,
  title: "Name what you did",
  bodySize: 22,
  body: "STRONG: I help my cousin with homework.\nSkill: explaining clearly and being patient.\n\nTOO VAGUE: I play games. Skill: gaming.\n\nBETTER: I plan moves with my team in a game.\nSkill: planning and teamwork.",
  done: "each Building Block names an action and a skill.",
});
recap(S(13), {
  kicker: KICKER,
  title: "Step 2 · Record 3 Building Blocks",
  steps: [
    "Open Find Your Future pp. 9–11.",
    "Write 3 real experiences: school, home, community, or interests. A hobby or a made-up example is okay.",
    "Beside each one, write 1 skill it shows.",
    "Partner check: read one Building Block. Your partner names the skill. Switch.",
  ],
  done: "your workbook shows 3 experiences and a skill beside each.",
});

// 14-15: Step 3, save the same three in H&L
await guidedScreen(S(14), { kicker: KICKER, title: "Step 3 · Save Building Block 1", screen: "Add a Building Block, Step 1 of 4: Choose", action: "In Profile Climbs, add a Building Block.\nUse your first workbook entry. Pick the closest category and activity. Click Next.", done: "Your first entry is chosen in H&L.", image: assets.buildingBlockChoose, alt: "Hats and Ladders Building Block Choose screen, step 1 of 4", callout: "PICK" });
await guidedScreen(S(15), { kicker: KICKER, title: "Step 3 · Describe, reflect, save. Repeat ×3", screen: "Step 2 of 4: Describe", action: "Describe the same entry in one or two sentences.\nFinish Reflect and Review, then Save.\nRepeat for entries 2 and 3.", done: "Your profile shows 3 Building Blocks.", image: assets.buildingBlockDescribe, alt: "Hats and Ladders Building Block Describe screen, step 2 of 4", callout: "SAVE" });

// 16: Step 4, DOL + device return
dol(S(16), {
  kicker: KICKER,
  title: "Step 4 · One connection, then return your device",
  bodySize: 21,
  body: "On your Day 3 page, finish:\nOne value I care about is ____.\nOne Building Block that shows a related skill is ____.\nA career cluster I may explore is ____ because ____.\n\nNo cluster suggestion in H&L yet? Write “cluster pending.”\nThen return your device the way the class practiced.",
  done: "your connection is written and your device is returned.",
});

// Speaker notes (full schema on every slide)
const SRC_LESSON = "CCE 1SW Wk0 Day 3 canonical lesson, docs/1sw/wk0-classroom-routines/day3.md";
const SRC_AVID = "Jenna Hainlen, AVID Week 1.6 (teacher-provided), cover/divider structure only";
const SRC_CN = "Climber Notes, Exploring Your Work Values, slides 1-4";
const SRC_HL = "Owner-authenticated Hats & Ladders student-view captures, 2026-08-17";
const SRC_FYF = "Find Your Future pp. 9-11, My Building Blocks";
const RECOVERY_HL = "H&L down: students choose a provisional value from the six on slide 6 and continue with FYF; app saves move to Friday catch-up. Paper or a private Canvas response is equal to OneNote; no recopying later.";

const notes = [
  { time: "Before class", move: "Open this deck, the Day 3 Student Guide, and the private response page. Test Sign in with Google → Profile Climbs → Discover Your Work Values. Set FYF pp. 9-11 at each seat, one workbook per student.", student: "None yet.", lookFor: "One workbook per student; the six-value list visible without another packet.", pivot: "If H&L is down before class, plan the provisional-value move now and protect Friday catch-up.", recovery: RECOVERY_HL, sources: [SRC_LESSON, SRC_AVID] },
  { time: "0:00-0:01", move: "Day divider while students check out devices.", student: "Check out the assigned device and sit.", lookFor: "Devices out; workbooks at seats.", pivot: "Show for seconds only.", recovery: "None needed.", sources: [SRC_AVID] },
  { time: "0:00-0:05", move: "Do Now. Give silent private think time, then two quick shares. Name the value inside each reason.", student: "Open the Day 3 page and write one choice and one reason.", lookFor: "A reason that reveals pay, independence, relationships, support, or balance.", pivot: "Read the two options aloud and let students point to one; one phrase is enough.", recovery: "A fictional worker may answer if a student does not want to disclose a preference. Paper page is equal.", sources: [SRC_LESSON, "Jenna Hainlen, AVID Week 1.6 quickwrite structure"] },
  { time: "0:05-0:06", move: "Read the I-can statement and the four steps once. Point to where each step happens: H&L, workbook, H&L, Day 3 page.", student: "Read along; locate the three places.", lookFor: "Students can point to H&L, the workbook pages, and the private page.", pivot: "Do not re-explain; the recap slide returns during work time.", recovery: "Absent students use the Student Guide, which carries the same four steps.", sources: [SRC_LESSON] },
  { time: "0:06-0:08", move: "Structured partner talk (teacher-created AVID routine). Circulate; name one value you hear for the room.", student: "Partner A reads; Partner B names the value; switch. Private option: underline the word.", lookFor: "Students naming a value word, not repeating the choice.", pivot: "If pairs stall, model one exchange with a student.", recovery: "Seated or private response is equal to sharing aloud.", sources: [SRC_LESSON, "Jenna Hainlen, AVID Week 1 partner-share routine"] },
  { time: "0:08-0:10", move: "Read the six values in one pass; do not teach them one by one. Ask students to hold two in mind.", student: "Read; pick two that sound like you.", lookFor: "Students can point to two values.", pivot: "Cut to one minute if the app is ready.", recovery: "This slide is the provisional route if H&L is down: students choose one value here.", sources: [SRC_CN] },
  { time: "0:10-0:12", move: "Show the real Profile Climbs card. Students who are not signed in use Sign in with Google.", student: "Open Profile Climbs; click Discover Your Work Values.", lookFor: "Start screen open on most devices.", pivot: "If sign-in fails for a few, seat them by a partner and record names; do not use another student's account.", recovery: RECOVERY_HL, sources: [SRC_HL, SRC_LESSON] },
  { time: "0:12-0:13", move: "Read the start card together; click Start.", student: "Click Start.", lookFor: "First pair of choices open.", pivot: "Skip if students are already inside.", recovery: RECOVERY_HL, sources: [SRC_HL] },
  { time: "0:13-0:20", move: "Lap 1: students read both choices rather than rapid-click. Stop and reset a rapid-clicker.", student: "Choose the better fit each time; click Next.", lookFor: "Progress bar moving at a reading pace.", pivot: "If H&L consumes more than 20 minutes total, move to FYF and finish app saves Friday.", recovery: RECOVERY_HL, sources: [SRC_HL, SRC_LESSON] },
  { time: "0:18-0:20", move: "Students record the two values and one expected/surprised sentence, then Continue.", student: "Write both values and one sentence on the Day 3 page.", lookFor: "Two value names on the page, not just a screenshot.", pivot: "One sentence only; do not extend.", recovery: "Provisional value if H&L is down; label it provisional.", sources: [SRC_HL, SRC_LESSON] },
  { time: "0:20-0:23", move: "Read the FYF p. 9 intro box aloud. Explain that experience is broader than paid work.", student: "Follow along on pp. 9-11.", lookFor: "Students can name one ordinary thing they do that counts.", pivot: "Keep to two minutes.", recovery: "No workbook: one paper page with the four categories; give the workbook later without recopying.", sources: [SRC_FYF, SRC_LESSON] },
  { time: "0:23-0:25", move: "Model strong vs. too vague; repair the vague one aloud. Do not require family or private disclosure.", student: "Listen; think of one experience.", lookFor: "Students naming an action, not a trait.", pivot: "Model a second ordinary example if a third of the room is blank.", recovery: "School, hobby, or fictional example allowed.", sources: [SRC_LESSON] },
  { time: "0:25-0:37", move: "Work time with this recap up. Lap 2: three ordinary experiences. Lap 3: skills are actions students can explain. Partner check in the last three minutes.", student: "Write 3 experiences and a skill beside each; partner check.", lookFor: "By minute 37 every student has three entries and a skill each.", pivot: "Reduce partner share to one round if short on time; do not cut the three Building Blocks.", recovery: "Optional word bank / bilingual support for idea retrieval; default copies 0.", sources: [SRC_FYF, SRC_LESSON, "Jenna Hainlen, AVID Week 1 partner routine"] },
  { time: "0:37-0:40", move: "Show the real Choose screen. Students save entry 1 first.", student: "Add a Building Block; choose category and activity; Next.", lookFor: "First entry chosen in H&L.", pivot: "If H&L is slow, save one now and the rest Friday.", recovery: RECOVERY_HL, sources: [SRC_HL] },
  { time: "0:40-0:45", move: "Students finish Describe, Reflect, Review, Save and repeat for entries 2 and 3. Frame any cluster suggestions as starting ideas.", student: "Save all three; look for cluster suggestions.", lookFor: "Profile count reaches 3.", pivot: "Defer suggestions if none appear; do not invent them.", recovery: RECOVERY_HL, sources: [SRC_HL, SRC_LESSON] },
  { time: "0:45-0:50", move: "DOL: one connection sentence on the private page. Then run the device-return routine.", student: "Write the connection; return the device.", lookFor: "A value, a Building Block, and a cluster or 'cluster pending' with a reason.", pivot: "If time is short, the connection sentence is protected; cut nothing else here.", recovery: "Paper or private Canvas response is equal; 'cluster pending' allowed.", sources: [SRC_LESSON] },
];
notes.forEach((spec, index) => setNotes(S(index + 1), spec));

const result = await finalize(runtime, presentation, { workspace, outputPath, expectedCount: 16 });
console.log(JSON.stringify(result, null, 2));
