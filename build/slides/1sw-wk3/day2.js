// CCE · 1SW Wk3 · Day 2 · Website Revamp (FYF pp. 28-29)
// node day2.js            -> docs/resources/slides/1sw-wk3-day2.pptx (full deck, licensed images)
// CCE_PUBLIC=1 node day2.js -> docs/resources/slides/public/1sw-wk3-day2.pptx (rights-clean twin)
const path = require("path");
const D = require("../lib");
const isPublic = process.env.CCE_PUBLIC === "1";
const d = D.deck({ public: isPublic, assetDir: path.join(__dirname, "assets") });
const { C } = D;
const FYF = D.SRC.fyf("28-29");
const SITE = D.SRC.site("Paws & Claws Pet Supply (Hats & Ladders practice site)", "https://pawsandclaws.hatsandladders.com", "2026-09-15");
const CV = D.SRC.canvas("2026-09-15");
const OUT = path.join(__dirname, "../../../docs/resources/slides", isPublic ? "public" : "", "1sw-wk3-day2.pptx");

// 1 · Title
d.title("Website Revamp", "You are the UX designer.", "College and Career Exploration · Week 3 · Day 2",
  "Bring your Find Your Future workbook (open to p. 28), a pencil, and your Chromebook (closed until we need it).",
  "Have this up as students walk in. Sticky notes on every table (about 4 per student today). Run time 50 minutes: warm-up 5, learn about UX 12, investigate 5, strengths and problems 9, fixes 9, sketch 4, exit ticket 6.", FYF);

// 2 · As you enter
{
  const s = d.slide("As you enter");
  d.card(s, 64, 200, 1152, 190);
  d.body(s, "Pick the BEST website you have ever used and the WORST one.\nWhat made the good one good? What made the bad one bad?", 92, 224, 1100, 150, 28, { bold: true });
  d.stem(s, "The best site I use is ________ because I can ________ fast.\nThe worst is ________ because I could not find ________.", 64, 430, 1150, "Say it like this", 22);
  d.meta(s, "Write one of each in your notebook. Two people share.", 64, 600);
  d.notes(s, "0-5 min. Take two voices. Listen for verbs: 'I could not find', 'it took forever', 'the button did nothing'. Those verbs are the whole lesson; you will point back to them in Step 1.", FYF);
}

// 3 · Today you will
{
  const s = d.slide("Today you will");
  d.numbered(s, ["Learn what good and bad UX look like (p. 28).", "Investigate a real practice website and catch your first reactions on sticky notes.", "List 3 things that work and 5 problems, then fix 3 of them (p. 29).", "Sketch a better version of one page, then finish the Rosa exit ticket."], 64, 205, 1152, 100, 24);
  d.meta(s, "Word of the day: UX (user experience). How a website makes you feel while you use it.", 64, 625);
  d.notes(s, "30 seconds. Read the four lines and move on.", FYF);
}

// 4 · Learn about UX (Step 1)
{
  const s = d.slide("Good UX, bad UX", "Find Your Future p. 28 · Step 1");
  d.image(s, "p28-goodbad.jpg", 64, 200, 700, 408, { licensed: true, fyfPage: 28 });
  d.meta(s, "Read along on p. 28", 64, 614, 700, 15);
  d.card(s, 800, 200, 416, 408);
  d.label(s, "Good UX", 824, 214, 380, C.green);
  d.body(s, "Menus are labeled.\nButtons stand out and do what they say.\nYou finish in a few steps.", 824, 258, 370, 120, 18);
  d.label(s, "Bad UX", 824, 392, 380, C.pink);
  d.body(s, "Links are hidden.\nToo much stuff on the page.\nButtons with confusing names.\nBroken or slow pages.", 824, 436, 370, 160, 18);
  d.notes(s, "5-17 min. Read the laptop box aloud from p. 28, then the two short lists on the right. Connect one warm-up answer to each list: 'Marcus said he could not find the menu; that is Confusing Navigation.' Chunking rule for the rest of the period: one step opens at a time, and you say what the step is for before it opens.", FYF);
}

// 5 · Investigate (Step 2) + Stop and Jot
{
  const s = d.slide("Investigate the website", "Find Your Future p. 28 · Step 2 · pawsandclaws.hatsandladders.com");
  d.image(s, "paws-home.jpg", 64, 200, 690, 342);
  d.meta(s, "Paws & Claws Pet Supply. Type the address exactly. You are a customer trying to buy something.", 64, 548, 690, 15);
  d.card(s, 790, 200, 426, 342);
  d.label(s, "Stop and Jot", 814, 214, 390);
  d.body(s, "90 seconds. Click around. Do not list anything yet.\n\nOne thought per sticky note.", 814, 260, 380, 120, 19);
  d.body(s, "The first thing I tried to do was ________.\n\nI got stuck when ________.", 814, 380, 380, 150, 20, { bold: true });
  d.meta(s, "5 minutes  ·  Voice 0  ·  Chromebooks open now", 64, 600);
  d.notes(s, "17-22 min. Open the site on the projector, then release Chromebooks. Give 90 seconds before any list-making; one thought per sticky. Read stickies over shoulders. If most name colors and fonts instead of navigation, pull the room back for 30 seconds and re-read the Easy Navigation and Clear Buttons rows from Step 1 before the lists open. The site is the practice store named on the Climber Notes deck; if it is blocked, the Day 2 student page has a full-page capture under 'Practice site unavailable or absent?'.", FYF + " " + SITE + " " + D.SRC.climber("Website Revamp"));
}

// 6 · Be a UX detective (Step 3)
{
  const s = d.slide("Be a UX detective", "Find Your Future p. 29 · Step 3 · Write in your workbook");
  d.image(s, "p29-step3.jpg", 64, 200, 520, 450, { licensed: true, fyfPage: 29 });
  d.card(s, 620, 200, 596, 200);
  d.label(s, "3 things that work", 644, 214, 560, C.green);
  d.body(s, "Something a customer can do easily. Name where it is on the page.", 644, 260, 550, 120, 19);
  d.card(s, 620, 420, 596, 230);
  d.label(s, "5 problems you can see", 644, 434, 560, C.pink);
  d.body(s, "A problem is something you can point at: a button that looks different from the others, a menu that goes nowhere, a page that is mostly empty.\n\"It's ugly\" is an opinion, not a problem.", 644, 480, 550, 160, 18);
  d.meta(s, "9 minutes  ·  strengths first, then problems  ·  Voice 0", 64, 660);
  d.notes(s, "22-31 min. Release strengths first; check by asking two students to read one strength. Then release problems. Lap at minute 12 of the block: every student has five problems, not two. If the room stalls at five, project the site and ask 'what happens when you click Shop?' without answering it.", FYF);
}

// 7 · Fix the problem (Step 4)
{
  const s = d.slide("Fix the problem", "Find Your Future p. 29 · Step 4 · Choose 3 of your 5 problems");
  d.image(s, "p29-step4.jpg", 64, 200, 720, 269, { licensed: true, fyfPage: 29 });
  d.card(s, 820, 200, 396, 269);
  d.label(s, "Each row needs", 844, 214, 360);
  d.body(s, "the problem you saw\n→ your fix\n→ what a user can now do", 844, 258, 350, 190, 21);
  d.stem(s, "This helps users because they can now ________.", 64, 500, 1150, "Say it like this", 26);
  d.meta(s, "9 minutes  ·  Ask your partner at Voice 1 if you are stuck on a fix", 64, 620);
  d.notes(s, "31-40 min. Model one row on the projector using a problem from a student's list (not your own). The third column is the one that matters; lap at minute 20 of the block and read that column only. A fix without a user benefit is not done. Optional scaffold Doc on the Day 2 page for students who need a worked model.", FYF);
}

// 8 · Sketch a better page (Step 5)
{
  const s = d.slide("Sketch a better page", "Find Your Future p. 29 · Step 5 · Plain paper");
  d.image(s, "p29-step5.jpg", 64, 200, 300, 223, { licensed: true, fyfPage: 29 });
  d.card(s, 400, 200, 816, 223);
  d.label(s, "Pick ONE page and redraw it", 424, 214, 780);
  d.body(s, "Boxes and labels, not art. Show where the menu, the search, and the main button go.\nCircle the fix you are proudest of and write its number from Step 4 next to it.", 424, 260, 770, 150, 20);
  d.meta(s, "4 minutes  ·  Keep the sketch. It goes in your folder with p. 29.", 64, 450);
  d.extension(s, "Finished early? Answer one Class Discussion question from p. 29 in your notebook: which improvement would make the biggest difference, and why?", 64, 510, 1152, 90);
  d.notes(s, "40-44 min. Four minutes is enough for boxes and labels. If time is short, the sketch is the thing to trim, never the three fixes.", FYF);
}

// 9 · Exit ticket: Rosa
{
  const s = d.slide("Exit ticket: Rosa's tutoring site", "Open the Day 2 exit ticket on the Canvas page");
  d.card(s, 64, 200, 720, 300);
  d.body(s, "Rosa is 16 and just opened a small tutoring business. Her website has one long page. The \"Sign Up\" button is gray and sits at the very bottom, under three paragraphs about her hobbies. The menu at the top says \"Stuff,\" \"More Stuff,\" and \"Click Here.\" Parents keep phoning Rosa instead of signing up online.", 88, 220, 680, 270, 19);
  d.image(s, "cv-d2-exit.png", 820, 200, 396, 140);
  d.numbered(s, ["Name TWO bad UX problems. Use words from today's lists.", "Pick one. Write your fix and how it helps users.", "Which fix brings Rosa the most new students? Why?"], 820, 350, 396, 100, 16);
  d.meta(s, "6 minutes  ·  Voice 0", 64, 520);
  d.notes(s, "44-50 min. The button opens a copy of the exit-ticket Doc. Look for list words (Confusing Navigation, Cluttered Design, Unclear Instructions) and a fix that names what the user can now do.", FYF + " " + CV);
}

// 10 · Before you go
{
  const s = d.slide("Before you go");
  d.numbered(s, ["Workbook p. 29 finished: 3 strengths, 5 problems, 3 fixes.", "Your sketch in your folder.", "Exit ticket submitted."], 64, 205, 1152, 100, 24);
  d.body(s, "Tomorrow you design an app from scratch. Bring the same workbook.", 64, 540, 1150, 60, 22, { bold: true });
  d.notes(s, "Last minute. Chromebooks docked. Collect nothing today; the p. 29 page and sketch go in the Major 1 folder on Day 3.", FYF);
}

d.write(OUT);
