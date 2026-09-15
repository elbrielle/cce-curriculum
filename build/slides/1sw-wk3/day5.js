// CCE · 1SW Wk3 · Day 5 · Xello Learning Style quiz + Learning styles lesson + method-to-task connection
const path = require("path");
const D = require("../lib");
const isPublic = process.env.CCE_PUBLIC === "1";
const d = D.deck({ public: isPublic, assetDir: path.join(__dirname, "assets") });
const { C } = D;
const CV = D.SRC.canvas("2026-09-15");
const XL = D.SRC.xello("My Learning Styles lesson prerequisites, pp. 1-2");
const XNAV = D.SRC.xello("Biases and career choices teacher slides, navigation slide (Home menu capture)");
const OUT = path.join(__dirname, "../../../docs/resources/slides", isPublic ? "public" : "", "1sw-wk3-day5.pptx");

d.title("Learning styles", "Xello quiz, then the lesson.", "College and Career Exploration · Week 3 · Day 5",
  "Bring your Chromebook. Turn in your Major 1 packet if you have not.",
  "Have this up as students walk in. Collect any late Major 1 packets before Xello opens. Run time 50 minutes: A/B/C prediction inside the first quiz block, quiz 20 (Voice 0, visible timer), lesson 30 (Voice 1 for the partner rehearsal inside it), connection sheet at the end of the lesson block.", XL);

// 2 · As you enter: A / B / C (Xello's own pre-quiz move)
{
  const s = d.slide("As you enter: A, B, or C?");
  d.image(s, "xello-abc.jpg", 64, 200, 700, 285, { licensed: true, placeholder: "Three lists of study habits\n(Xello lesson guide)" });
  d.card(s, 800, 200, 416, 285);
  d.label(s, "Which one is you?", 824, 214, 380);
  d.body(s, "Read all three. Pick the one you actually do when you have to learn something new, not the one that sounds smart.", 824, 262, 370, 130, 18);
  d.body(s, "Write the letter and one example from your own life in your notebook.", 824, 392, 370, 80, 18, { bold: true });
  d.stem(s, "I am mostly ____. Last time I learned something new, I ________.", 64, 520, 1150, "Say it like this", 22);
  d.notes(s, "0-3 min, inside the quiz block. Do not name the three styles yet; the lesson names them later and the quiz should not be primed. Two voices, then open Xello.", XL);
}

// 3 · Today you will
{
  const s = d.slide("Today you will");
  d.numbered(s, ["Take the Xello Learning Style quiz (20 minutes, Voice 0).", "Do the Learning styles lesson (30 minutes).", "Pick one learning method and connect it to a real school task on the Method-to-Task sheet."], 64, 205, 1152, 100, 24);
  d.meta(s, "Your result is not a grade and does not measure ability. It is a starting point for choosing a method.", 64, 540);
  d.notes(s, "30 seconds. Say the last line aloud; students who see a 'style' as a label stop trying other methods, which is the opposite of the lesson.", XL);
}

// 4 · Open Xello
{
  const s = d.slide("Open Xello", "ClassLink → Xello → About Me → Learning Style");
  d.image(s, "xello-home-menu.jpg", 64, 200, 620, 363, { licensed: true, placeholder: "Xello Home menu\n(see the Day 5 Canvas page)" });
  d.meta(s, "Xello's Home menu. About Me is the next tab to the right.", 64, 570, 620, 15);
  d.numbered(s, ["Open ClassLink and click the Xello tile.", "Click About Me at the top.", "Click Learning Style and start the quiz.", "Stuck for two minutes? Raise a hand and start the Method-to-Task sheet while you wait."], 720, 200, 496, 96, 16);
  d.notes(s, "3-5 min. Model the three clicks on the projector before Chromebooks open. Devices flat while you model. If Xello does not launch for a student after a two-minute check, move them to the connection sheet; it carries the method chart so the thinking target still gets done. Add a live About Me > Learning Style screenshot here when a student demo login is available; the current image is the Home menu from the Xello teacher slides.", XNAV);
}

// 5 · Quiz work slide
{
  const s = d.slide("Learning Style quiz", "20 minutes · Voice 0 · Private");
  d.card(s, 64, 200, 720, 300);
  d.label(s, "Answer honestly", 88, 214, 680);
  d.body(s, "There are no right answers. Pick what you actually do, not what you wish you did.\nRead each choice fully before you click.\nWhen you finish, read your result page once, then close the lid halfway and wait.", 88, 262, 680, 220, 20);
  d.card(s, 820, 200, 396, 300);
  d.label(s, "Timer", 844, 214, 360, C.pink);
  d.body(s, "20:00 on the board.\n\nDone early? Reread your result and find one line you disagree with.", 844, 262, 350, 220, 19);
  d.meta(s, "Devices flat while directions are given. Voice 0 until the timer ends.", 64, 520);
  d.notes(s, "5-25 min. Walk once at minute 5 for stuck logins and once at minute 15 for finished students. The result page is the only thing worth reading twice.", XL);
}

// 6 · Lesson
{
  const s = d.slide("Learning styles lesson", "30 minutes · Dashboard → View all lessons → Learning styles");
  d.numbered(s, ["Click Dashboard, then View all lessons.", "Open Learning styles and work through it in order.", "When the lesson asks you to talk to a partner, that is Voice 1 for that part only.", "Finish the lesson's own reflection question inside Xello."], 64, 205, 720, 90, 17);
  d.card(s, 820, 205, 396, 340);
  d.label(s, "Three methods", 844, 219, 360);
  d.body(s, "Visual: diagrams, models, color coding, written steps\nAuditory: read aloud, explain to a partner, record and replay\nTactile: build, sort, trace, act out, practice by doing", 844, 263, 350, 270, 16);
  d.meta(s, "30:00 on the board. Voice 0 except the partner part.", 64, 580);
  d.notes(s, "25-50 min, with the connection sheet inside the last part of this block. The method chart on the right is the same one printed on the Method-to-Task sheet, so a student who cannot load the lesson still has it.", XL);
}

// 7 · Talk, then write: method to task
{
  const s = d.slide("Talk, then write", "Method-to-Task Connection · last 8 minutes of the lesson block");
  d.image(s, "cv-d5-connection.png", 64, 200, 420, 100);
  d.namedRows(s, [["Talk", "Voice 1, 60 seconds each. Tell your partner one method from the chart and one real task this week you will try it on."], ["Write", "Voice 0. Fill in the frame on the sheet. Name the task and how you will know it helped."]], 64, 320, 720, 118, 130, 18, [C.pink, C.blue]);
  d.card(s, 820, 200, 396, 356);
  d.label(s, "Say it like this", 844, 214, 360);
  d.body(s, "A method I can test is ____.\n\nI will use it when I ____.\n\nI will know it helped if ____.", 844, 262, 350, 280, 19);
  d.wordBank(s, ["visual", "auditory", "tactile", "method", "obstacle", "strategy"], 64, 580, 720);
  d.notes(s, "42-50 min. The button opens a copy of the connection sheet. Talk before write is deliberate: emergent bilingual students rehearse the sentence out loud, then write it. Speech-to-text is fine. The sheet is Day 5 formative evidence; the quiz and lesson are checked separately in the Xello Completion Standards report and do not change the Major 1 score.", CV + " " + XL);
}

// 8 · Before you go
{
  const s = d.slide("Before you go");
  d.numbered(s, ["Learning Style quiz finished in Xello.", "Learning styles lesson finished, reflection answered.", "Method-to-Task sheet submitted."], 64, 205, 1152, 100, 24);
  d.body(s, "Next week: Tech Support careers. Bring your Find Your Future workbook.", 64, 540, 1150, 60, 22, { bold: true });
  d.notes(s, "Last minute. Chromebooks docked. Check the Xello Completion Standards report tonight for the quiz and lesson.", XL);
}

d.write(OUT);
