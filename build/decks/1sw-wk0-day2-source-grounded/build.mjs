// CCE 1SW Wk0 Day 2 daily master: H&L Setup and Discover Your Core (Core Day A).
// Source of truth: docs/1sw/wk0-classroom-routines/day2.md (50-minute flow).
// Starter: AVID Week 1.2 clone (Jenna Hainlen) for the day divider only; every
// content slide is redrawn with editable shapes from build/decks/lib/slide_kit.mjs.
// Projected text is student-facing; teacher moves live in speaker notes.

import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadRuntime, openStarter, slideAt, doNow, agenda, talk, guidedText, guidedScreen, recap, rowsSlide, dol, setNotes, finalize,
} from "../lib/slide_kit.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../../..");
const workspace = path.join(root, "tmp/cce-week1-day2-source-clone");
const starterPath = path.join(workspace, "template-starter.pptx");
const outputPath = path.join(root, "cce-curriculum/resources/avid-reference/source/derived/cce-week1-day2-source-grounded.pptx");
const KICKER = "CCE WEEK 1 · TUESDAY";
const PAGE = "Core Personality – Day 2";

const hl = (name) => path.join(root, "cce-curriculum/resources/owner-authenticated-source/hats-and-ladders/screens", name);
const licensed = (name) => path.join(root, "cce-curriculum/resources/canvas-licensed/1sw/wk0/day2", name);
const assets = {
  typesChart: licensed("six-core-personality-types.png"),
  ccmrPage: licensed("irving-isd-ccmr-programs-of-study.png"),
  dashboard: hl("dashboard-profile-climbs.png"),
  jumpstart: hl("jumpstart-profile-start.png"),
  jumpstartQuestion: hl("jumpstart-starting-point-question.png"),
  coreStart: hl("discover-your-core-start.png"),
  coreQuestion: hl("discover-your-core-question.png"),
  coreComplete: hl("core-complete-badge.png"),
};

const runtime = await loadRuntime();
const { presentation, setText } = await openStarter(runtime, starterPath);
const S = (n) => slideAt(presentation, n);

// 1: keep the AVID day divider (structure credit in notes)
setText(1, "Wednesday/ Thursday", "Tuesday");

// 2: As You Enter + Do Now (the six types in plain words, before the labels)
doNow(S(2), {
  kicker: KICKER,
  materials: ["Your assigned Chromebook", `OneNote → CCE Work → ${PAGE}`, "Your IISD Google account (for Hats & Ladders)"],
  prompt: "Which one sounds most like you?\nbuild or fix things · figure out how things work · make art, music, or stories · help people · lead a group · organize plans and details",
  stem: "Day 2 page: I picked ____ because I often ____.\nEspañol: Elegí ____ porque a menudo ____.",
  done: "one choice and one clue are written on your Day 2 page.",
});

// 3: Today (objective + agenda + where each step happens)
agenda(S(3), {
  kicker: KICKER,
  objective: "I can complete Discover Your Core in Hats & Ladders and explain my result with one detail from my Core description.",
  teks: "TEKS 127.2 (d)(1)(A)",
  steps: [
    "Meet the six Core types and predict one (Day 2 page)",
    "Why explore careers now? (Find Your Future p. 21)",
    "Sign in with Google and finish Jumpstart Your Profile (H&L)",
    "Complete Discover Your Core (H&L)",
    "Record your result and one interpretation (Day 2 page)",
  ],
  done: "H&L shows Core Complete and your Day 2 page has your result + one interpretation",
});

// 4-5: The six Core types in plain words (Climber Notes chart, paraphrased; the official chart stays in the Student Guide)
rowsSlide(S(4), {
  kicker: KICKER,
  title: "The six Core types (1 of 2)",
  lineSize: 18,
  rows: [
    { head: "Doer", lines: ["Likes to: work with hands, tools, machines, or animals; solve real, physical problems.", "Right now: you are the one who actually builds the project."] },
    { head: "Analyzer", lines: ["Likes to: research, observe, and figure out how things work; ask why and how.", "Right now: science or math clicks for you, or you love figuring things out."] },
    { head: "Creator", lines: ["Likes to: express ideas through art, music, writing, or performance.", "Right now: you doodle, write stories, or play an instrument."] },
  ],
  done: "you can point to one type and say one real-life clue.",
});
rowsSlide(S(5), {
  kicker: KICKER,
  title: "The six Core types (2 of 2)",
  lineSize: 18,
  rows: [
    { head: "Helper", lines: ["Likes to: connect with, support, and teach people.", "Right now: you are the friend people come to when something is wrong."] },
    { head: "Persuader", lines: ["Likes to: lead, influence, and motivate others.", "Right now: you step up in group projects and get people on board."] },
    { head: "Organizer", lines: ["Likes to: work with data, numbers, and systems; bring order and accuracy.", "Right now: your notes are organized and you like a clear process."] },
  ],
  done: "you found the type that matches your Do Now answer. Types are interest patterns, not grades.",
});

// 6: Predict one type
guidedText(S(6), {
  kicker: KICKER,
  title: "Predict one type",
  bodySize: 22,
  body: "Doer · Analyzer · Creator · Helper · Persuader · Organizer\n\nAdd the type name to your Do Now line on your Day 2 page:\nMy prediction is ____ because I often ____.\nEspañol: Mi predicción es ____ porque a menudo ____.\n\nThis is a guess, not a grade. Do not open H&L yet.",
  done: "one predicted type and one clue are on your Day 2 page.",
});

// 7: Why explore careers now? (FYF p. 21, teacher reads only the yellow box)
await guidedScreen(S(7), {
  kicker: KICKER,
  title: "Why explore careers now?",
  screen: "Find Your Future page 21. Your teacher reads only the yellow What is CCMR? box.",
  action: "Listen to what CCMR means: College, Career, and Military Readiness.\nTurn and talk: Why is it helpful to think about future goals before high school?",
  done: "You can give one reason career exploration helps you now.",
  image: assets.ccmrPage,
  alt: "Find Your Future page 21 defining College, Career, and Military Readiness and Programs of Study in Irving ISD",
  callout: "TALK",
});

// 8-11: Hats & Ladders, one action per screen
await guidedScreen(S(8), { kicker: KICKER, title: "Step 3 · Sign in with Google", screen: "The Hats & Ladders home after you sign in", action: "Go to app.hatsandladders.com.\nClick Sign in with Google and use your IISD account.\nCheck that the name at the top is yours.", done: "Your name is at the top and the yellow Profile Climbs card is on the screen.", image: assets.dashboard, alt: "Hats and Ladders home showing the yellow Profile Climbs card after Google sign-in", callout: "SIGN IN" });
await guidedScreen(S(9), { kicker: KICKER, title: "Step 3 · Jumpstart Your Profile", screen: "The Jumpstart Your Profile start card", action: "In the yellow Profile Climbs card, click Jumpstart Your Profile.\nClick Start. Answer the short starting-point questions, then Next.", done: "Jumpstart is complete and you are back at Profile Climbs.", image: assets.jumpstart, alt: "Hats and Ladders Jumpstart Your Profile start card with Start button", callout: "GO" });
await guidedScreen(S(10), { kicker: KICKER, title: "Step 4 · Start Discover Your Core", screen: "The Discover Your Core start card", action: "In Profile Climbs, click Discover Your Core.\nRead the directions. Click Start.\nAnswer as yourself, not as who you think you should be.", done: "The first thumbs-down / thumbs-up statement is open.", image: assets.coreStart, alt: "Hats and Ladders Discover Your Core start screen with Start button", callout: "GO" });
await guidedScreen(S(11), { kicker: KICKER, title: "Step 4 · Answer honestly", screen: "One Discover Your Core statement with thumbs down and thumbs up", action: "Read the whole statement.\nChoose thumbs down or thumbs up.\nUse the arrow for the next one. No rushing.", done: "The progress bar moves after each answer.", image: assets.coreQuestion, alt: "Hats and Ladders Discover Your Core statement with thumbs down and thumbs up buttons", callout: "PICK" });

// 12: Recap during work time
recap(S(12), {
  kicker: KICKER,
  title: "While you work: Steps 3 and 4",
  steps: [
    "Sign in with Google → check your name → open Profile Climbs.",
    "Jumpstart Your Profile → Start → answer the short questions.",
    "Discover Your Core → Start → read each statement → thumbs down or thumbs up.",
    "When you see Core Complete, keep it open and go to your Day 2 page.",
  ],
  done: "you see the Core Complete badge in H&L.",
});

// 13-14: Record the result and one interpretation
await guidedScreen(S(13), { kicker: KICKER, title: "Step 5 · Record your result", screen: "The Core Complete badge and your result in H&L", action: "Keep H&L open.\nOn your Day 2 page write:\nMy H&L Core result is ____.", done: "Your result is on your Day 2 page.", image: assets.coreComplete, alt: "Hats and Ladders Core Complete badge screen", callout: "NOTE" });
guidedText(S(14), {
  kicker: KICKER,
  title: "Step 5 · Choose ONE interpretation",
  bodySize: 21,
  body: "Finish ONE on your Day 2 page:\n• A phrase from my description that fits or surprises me is ____ because ____.\n• One real question I have is ____.\n• One career I am now curious about is ____ because ____.\n\nEspañol: Una frase que me describe es ____ porque ____.",
  done: "one interpretation is written under your result.",
});

// 15: Compare prediction and result (analyze and discuss)
talk(S(15), {
  kicker: KICKER,
  title: "Compare your prediction and your result",
  partnerA: "Say your prediction and your result. Same or different?",
  partnerB: "Ask: What might explain the match or the difference? Then switch.",
  privateOption: "Write one sentence on your Day 2 page:\nMy result was the same as / different from my prediction because ____.",
  done: "you can say one reason your result matched or differed.",
});

// 16: DOL + device return
dol(S(16), {
  kicker: KICKER,
  title: "Show your learning, then return your device",
  bodySize: 21,
  body: "When your teacher comes by, point to your Day 2 page:\n1. your H&L Core result\n2. your one interpretation\n\nIf H&L did not open today, write provisional next to the type you chose from the chart. You will finish H&L on Friday.\n\nThen return your device the way the class practiced.",
  done: "your Day 2 page shows your result + one interpretation and your device is returned.",
});

// Speaker notes (full schema on every slide)
const SRC_LESSON = "CCE 1SW Wk0 Day 2 canonical lesson, docs/1sw/wk0-classroom-routines/day2.md";
const SRC_AVID = "Jenna Hainlen, AVID Week 1.2 (teacher-provided), day-divider structure only";
const SRC_CN = "Climber Notes, Learning Your Core Personality Types, slides 2-5 (hook and six-type chart)";
const SRC_HL = "Owner-authenticated Hats & Ladders student-view captures, 2026-08-17";
const SRC_FYF = "Find Your Future p. 21, What is Happening at My District? (yellow CCMR box only)";
const RECOVERY_HL = "H&L down or account not found: never use another student's account. Student chooses a provisional type from the chart with one supporting phrase; record the name and protect Friday catch-up. Paper or a private Canvas response is equal to OneNote; no recopying later.";

const notes = [
  { time: "0:00-0:01", move: "Day divider while students check out assigned devices. Before class: test Sign in with Google → Profile Climbs → Jumpstart and Discover Your Core; distribute the Day 2 response page.", student: "Check out the device and sit.", lookFor: "Devices out; Day 2 page open.", pivot: "Show for seconds only.", recovery: RECOVERY_HL, sources: [SRC_AVID, SRC_LESSON] },
  { time: "0:00-0:03", move: "Do Now in plain words. Silent think time; students write one activity phrase and one clue. This primes the six types before the labels appear.", student: "Write one choice and one clue on the Day 2 page.", lookFor: "A concrete clue (I often ...), not just the choice.", pivot: "Read the six phrases aloud once if students stall.", recovery: "Paper page is equal. A school or hobby example is fine.", sources: [SRC_LESSON, SRC_CN, "Jenna Hainlen, AVID Week 1.2 opener rhythm"] },
  { time: "0:03-0:04", move: "Read the I-can statement and the five steps once. Point to where each step happens: Day 2 page, workbook page projected, H&L, H&L, Day 2 page.", student: "Read along.", lookFor: "Students can point to H&L vs. their Day 2 page.", pivot: "Do not re-explain; the recap returns during work time.", recovery: "The Student Guide carries the same five steps for absent students.", sources: [SRC_LESSON] },
  { time: "0:04-0:05", move: "Introduce Doer, Analyzer, Creator from the official Climber Notes chart in plain words; connect each to the Do Now phrases (build/fix, figure out, make). Say plainly they are interest patterns, not grades or labels.", student: "Find the type that matches the Do Now answer.", lookFor: "Students pointing to a type and giving a real-life clue.", pivot: "One minute per slide; the full chart stays in the Student Guide.", recovery: "These two slides are the provisional route if H&L is down.", sources: [SRC_CN, SRC_LESSON] },
  { time: "0:05-0:06", move: "Introduce Helper, Persuader, Organizer the same way (help, lead, organize). Most people match more than one type.", student: "Find the type that matches the Do Now answer.", lookFor: "Students can name one type and one clue.", pivot: "One minute.", recovery: "Provisional route if H&L is down.", sources: [SRC_CN, SRC_LESSON] },
  { time: "0:06-0:07", move: "Students add the type name to their Do Now line. Take two or three quick verbal responses. Say it is a guess, not a grade.", student: "Write: My prediction is ____ because I often ____.", lookFor: "One type name and one clue on the page.", pivot: "One line only.", recovery: "Paper page is equal.", sources: [SRC_LESSON] },
  { time: "0:07-0:11", move: "Project FYF p. 21 and name the source (not an H&L screen). Read only the yellow CCMR box aloud; ask the printed question; take one turn-and-talk. Frame CCE as the on-ramp to Irving ISD CTE pathways that begin in 8th grade. Transition: H&L will give us one clue about the kinds of work that may interest us.", student: "Listen; turn and talk once.", lookFor: "One reason career exploration helps now.", pivot: "Do not read the Programs of Study or CTE Center boxes today.", recovery: "None needed; workbook stays closed.", sources: [SRC_FYF, SRC_LESSON] },
  { time: "0:11-0:14", move: "Model Sign in with Google once on the projector. Students confirm the displayed name is theirs.", student: "Sign in; check the name; find Profile Climbs.", lookFor: "Yellow Profile Climbs card visible on most screens.", pivot: "Account not found: seat the student by a partner, record the name, move on. Do not switch methods mid-lesson.", recovery: RECOVERY_HL, sources: [SRC_HL, SRC_LESSON] },
  { time: "0:14-0:21", move: "Show the real Jumpstart card. Students click Jumpstart Your Profile, Start, and finish the short starting-point questions. Circulate; no profile photos today.", student: "Open Jumpstart; Start; answer; Next; return to Profile Climbs.", lookFor: "Students back at Profile Climbs by minute 21.", pivot: "Skip if profiles are already jumpstarted; if Jumpstart is slow for a few, they move to Discover Your Core as soon as it opens.", recovery: RECOVERY_HL, sources: [SRC_HL, SRC_LESSON] },
  { time: "0:21-0:23", move: "Show the real Discover Your Core start card. Say: read every statement; honest answers are more useful than fast answers; no type is better than another.", student: "Open Discover Your Core; read; Start.", lookFor: "First statement open.", pivot: "None.", recovery: RECOVERY_HL, sources: [SRC_HL, SRC_LESSON] },
  { time: "0:23-0:40", move: "Lap 1: every student is reading, not clicking through; stop and reset a rapid-clicker. Sit with a student who rushes and read aloud. Pair read-aloud needs with fluent-reading peers first.", student: "Answer each statement; keep going.", lookFor: "Progress bar moving at a reading pace.", pivot: "If a third of the class is done early, use the discussion frame: which type fits a nurse, a chef, a pilot? Why more than one type?", recovery: RECOVERY_HL, sources: [SRC_HL, SRC_LESSON] },
  { time: "0:23-0:40 (leave up)", move: "Keep this recap projected during work time. Point to the current step when a student loses the thread.", student: "Follow the four steps to Core Complete.", lookFor: "Students who finish keep H&L open and move to the Day 2 page.", pivot: "None.", recovery: RECOVERY_HL, sources: [SRC_LESSON] },
  { time: "0:40-0:42", move: "Students record the result. Lap 2: the notebook interpretation begins; if a third of the class copies only the type name, read one description aloud and model choosing a meaningful phrase.", student: "Write: My H&L Core result is ____.", lookFor: "Result name on the page.", pivot: "One line.", recovery: "Provisional result labeled if H&L was unavailable.", sources: [SRC_HL, SRC_LESSON] },
  { time: "0:42-0:46", move: "Students choose one interpretation. Complete model: 'My H&L result is Organizer. The phrase likes clear systems fits because I keep group projects on track.'", student: "Write one interpretation.", lookFor: "A phrase, question, or career curiosity with a because.", pivot: "Do not add a second interpretation or a separate exit ticket.", recovery: "Paper or private Canvas response is equal.", sources: [SRC_LESSON] },
  { time: "0:46-0:48", move: "Partner talk (teacher-created AVID routine) on the DOK 2 question: how is your result different from or the same as your prediction, and what might explain it? Private written option is equal.", student: "Compare prediction and result with a partner or in writing.", lookFor: "A reason, not just same/different.", pivot: "Cut to one exchange if short on time.", recovery: "Seated/private response equal to sharing aloud.", sources: [SRC_LESSON, "Jenna Hainlen, AVID Week 1 partner-share routine"] },
  { time: "0:48-0:50", move: "DOL: students point to the result and interpretation privately; they do not display content to the class. Then run the device-return routine.", student: "Show the page when asked; return the device.", lookFor: "Result + one interpretation on every page, or provisional label.", pivot: "Protect this DOL; trim talk time before trimming this.", recovery: "Provisional route recorded; Friday catch-up protected.", sources: [SRC_LESSON] },
];
notes.forEach((spec, index) => setNotes(S(index + 1), spec));

const result = await finalize(runtime, presentation, { workspace, outputPath, expectedCount: 16 });
console.log(JSON.stringify(result, null, 2));
