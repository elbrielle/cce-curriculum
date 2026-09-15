// CCE · 1SW Wk3 · Day 3 · From Wireframe to Wow (FYF pp. 30-33)
const path = require("path");
const D = require("../lib");
const isPublic = process.env.CCE_PUBLIC === "1";
const d = D.deck({ public: isPublic, assetDir: path.join(__dirname, "assets") });
const { C } = D;
const FYF = D.SRC.fyf("30-33");
const CV = D.SRC.canvas("2026-09-15");
const OUT = path.join(__dirname, "../../../docs/resources/slides", isPublic ? "public/1sw-wk3-day3-public.pptx" : "1sw-wk3-day3.pptx");

d.title("From Wireframe to Wow", "Design an app before anyone writes code.", "College and Career Exploration · Week 3 · Day 3",
  "Bring your Find Your Future workbook (open to p. 30), a pencil, and your phone-sized imagination. No Chromebook today.",
  "Have this up as students walk in. Sticky notes and pencils on tables; wireframe template printouts for students who want them. Run time 50 minutes: warm-up 5, choose 3, plan 5, wireframe 17, partner test 10, improve 10. No exit ticket today; the packet is the evidence.", FYF);

// 2 · As you enter
{
  const s = d.slide("As you enter");
  d.card(s, 64, 200, 1152, 190);
  d.body(s, "Think of the app you use most on your phone.\nHow many taps does it take to do the main thing you use it for? Where is the menu button?", 92, 224, 1100, 150, 28, { bold: true });
  d.stem(s, "In ________ it takes ________ taps to ________. The menu is ________.", 64, 430, 1150, "Say it like this", 24);
  d.meta(s, "Write it in your notebook. Two people share.", 64, 560);
  d.notes(s, "0-5 min. Two voices. Point out that somebody counted those taps on purpose; that person is an app designer, and today the students are that person.", FYF);
}

// 3 · Today you will
{
  const s = d.slide("Today you will");
  d.numbered(s, ["Choose one of three app briefs and plan it on sticky notes (p. 30).", "Draw four screens with the wireframe symbols: Home, Main Menu, Action, Success (pp. 31-32).", "Test your screens with a partner and answer their three questions (p. 33).", "Make at least 2 improvements and star them. Turn in the packet."], 64, 205, 1152, 100, 24);
  d.meta(s, "Word of the day: wireframe. A quick sketch that shows where buttons, text, and pictures go.", 64, 625);
  d.notes(s, "30 seconds. This is the Major 1 packet day; say that once, plainly, and move on.", FYF);
}

// 4 · Choose your app (Step 1)
{
  const s = d.slide("Choose your app", "Find Your Future p. 30 · Step 1 · Check one box");
  d.image(s, "p30-briefs.jpg", 64, 200, 720, 280, { licensed: true, fyfPage: 30 });
  d.card(s, 820, 200, 396, 280);
  d.label(s, "Pick one", 844, 214, 360);
  d.body(s, "Food Connection\nStress-Less\nPassion Project\n\nYou have 3 minutes. Do not trade later.", 844, 262, 350, 200, 21);
  d.image(s, "p30-hero.jpg", 64, 500, 1152, 199, { licensed: true, fyfPage: 30 });
  d.notes(s, "5-8 min. Read the three briefs aloud once. Three minutes and a checked box; a student who cannot choose gets Stress-Less, because every 7th grader has an opinion about screen-free breaks.", FYF);
}

// 5 · Plan your app (Step 2)
{
  const s = d.slide("Plan your app", "Find Your Future p. 30 · Step 2 · Sticky notes");
  d.image(s, "p30-plan.jpg", 64, 200, 620, 189, { licensed: true, fyfPage: 30 });
  d.namedRows(s, [["Name", "What is your app called?"], ["User", "Who is it for? Be specific: a 7th grader who forgets homework, a restaurant manager at closing time."], ["Does", "2 or 3 features that make it useful or fun. One per sticky note."]], 720, 200, 496, 100, 120, 17);
  d.meta(s, "5 minutes  ·  Voice 0  ·  Stick the notes on p. 30", 64, 520);
  d.notes(s, "8-13 min. Three stickies minimum: name, user, one feature. The user line is where weak apps start; push 'for everyone' toward one real person.", FYF);
}

// 6 · The four symbols and the four screens (Step 3)
{
  const s = d.slide("Wireframe symbols", "Find Your Future p. 31 · Step 3");
  d.image(s, "p31-symbols.jpg", 64, 200, 720, 242, { licensed: true, fyfPage: 31 });
  d.card(s, 820, 200, 396, 242);
  d.label(s, "Every app needs", 844, 214, 360);
  d.body(s, "1  Home screen\n2  Main Menu\n3  Action screen\n4  Success screen", 844, 258, 350, 170, 22);
  d.card(s, 64, 462, 1152, 150);
  d.body(s, "Box with an X = picture or video.   Lines = text.   Rectangle or oval = button.   Three stacked lines = menu.\nBoxes and labels, not art. A designer can read your screen in five seconds.", 88, 480, 1100, 120, 20);
  d.notes(s, "13-15 min. Draw the four symbols on the board once. The Success screen is the one students forget or copy from Home; say now that Success shows what happens after the user finishes something, like a 'Great job' pop-up.", FYF);
}

// 7 · Work slide: draw the screens
{
  const s = d.slide("Draw your four screens", "Find Your Future pp. 31-32 · 17 minutes");
  d.image(s, "p31-screens12.jpg", 64, 200, 420, 423, { licensed: true, fyfPage: 31 });
  d.card(s, 520, 200, 696, 200);
  d.label(s, "Check yourself", 544, 214, 660);
  d.body(s, "Minute 8: Home and Main Menu are boxed and labeled.\nMinute 18: Action shows what the user did; Success shows what happened next.", 544, 258, 650, 130, 19);
  d.card(s, 520, 420, 696, 110);
  d.label(s, "You are done when", 544, 432, 660, C.green);
  d.body(s, "all four screens have labels, a first-time user could find the next button on each one, and Success is not a copy of Home.", 544, 474, 650, 50, 17);
  d.extension(s, "Finished early? Add a fifth screen (settings, profile, or search) and write which screen it connects to.", 520, 550, 696, 80);
  d.meta(s, "Voice 0  ·  Template printouts at the front if you want the frame drawn for you", 64, 640);
  d.notes(s, "15-32 min. Walk one fixed route twice: lap 1 at minute 8 (Home and Main Menu boxed and labeled), lap 2 at minute 18 (Action and Success show cause and effect). Two known misses: art instead of labeled boxes, and a Success screen that repeats Home. If more than a handful miss lap 1, reproject the four symbols instead of fixing desk by desk. The wireframe template Doc and bilingual PDF are linked on the Day 3 page.", FYF + " " + CV);
}

// 8 · Think, pair, share: partner test (Step 4)
{
  const s = d.slide("Think, pair, share: test your app", "Find Your Future p. 33 · Step 4 · Trade workbooks");
  d.namedRows(s, [["Think", "30 seconds, silent. Read your partner's four screens in order. Do not explain your own yet."], ["Pair", "Partner A: 30 seconds. Partner B: 30 seconds. Answer the three questions from p. 33 about the OTHER person's app."], ["Share", "Two pairs tell the class one confusion they found. Not a compliment."]], 64, 200, 720, 118, 130, 18);
  d.image(s, "p33-test.jpg", 820, 200, 396, 275, { licensed: true, fyfPage: 33 });
  d.meta(s, "The three questions, p. 33", 820, 480, 396, 15);
  d.stem(s, "On Screen ____ I did not know where to click next.\nYour Success screen tells the user ____, but it does not tell them ____.", 64, 560, 1150, "Say it like this", 20);
  d.notes(s, "32-42 min. Time each part out loud. Listen for who names a missing screen rather than a missing label, and pick share-out pairs from what you heard, not from raised hands. Third stem if a pair is stuck: 'I think this app is missing a ____ screen.'", FYF);
}

// 9 · Improve (Step 5)
{
  const s = d.slide("Improve your design", "Find Your Future p. 33 · Step 5 · At least 2 changes");
  d.image(s, "p33-improve.jpg", 64, 200, 620, 231, { licensed: true, fyfPage: 33 });
  d.image(s, "p33-sketch.jpg", 720, 200, 300, 282, { licensed: true, fyfPage: 33 });
  d.card(s, 64, 460, 1152, 140);
  d.label(s, "Star each change", 88, 474, 500);
  d.body(s, "Draw a star next to every improvement and write one line: what your partner said, and what you changed. Two stars minimum. That line is what gets graded.", 88, 518, 1100, 70, 19);
  d.meta(s, "10 minutes  ·  Voice 0", 64, 620);
  d.notes(s, "42-50 min. The starred line is the Response to Feedback rubric row (4 of the 16 points). No star, no evidence. Collect the packet at the bell: p. 30 plan, four screens, partner notes, two starred changes.", FYF);
}

// 10 · Turn in
{
  const s = d.slide("Turn in your packet", "Major 1 · 16 points · App Design Packet");
  d.numbered(s, ["App plan (p. 30 with your sticky notes)", "Four labeled screens (pp. 31-32)", "Partner walkthrough notes and 2 starred improvements (p. 33)"], 64, 205, 720, 100, 20);
  d.image(s, "cv-d3-rubric.png", 820, 205, 396, 130);
  d.card(s, 820, 350, 396, 160);
  d.body(s, "App Plan · Screen Design · Response to Feedback · Emerging Career Evidence (tomorrow)\n4 points each", 844, 366, 350, 130, 17);
  d.meta(s, "The rubric is on the Day 3 Canvas page. Tomorrow's evidence sheet joins this packet.", 64, 540);
  d.notes(s, "Last minute. Packets stay with you until Day 4 adds the emerging-career evidence sheet, then score with the 16-point rubric before the Day 5 Xello block.", FYF + " " + CV);
}

d.write(OUT);
