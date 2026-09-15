// CCE · 1SW Wk3 · Day 1 · Networking and data careers + transferable skills (FYF p. 38 optional)
const path = require("path");
const D = require("../lib");
const isPublic = process.env.CCE_PUBLIC === "1";
const d = D.deck({ public: isPublic, assetDir: path.join(__dirname, "assets") });
const { C } = D;
const FYF = D.SRC.fyf("38");
const CV = D.SRC.canvas("2026-09-15");
const BLS = D.SRC.bls("Network and Computer Systems Administrators", "https://www.bls.gov/ooh/computer-and-information-technology/network-and-computer-systems-administrators.htm", "2026-09-15");
const CARDS = "Networking Career Cards (CCE-authored, build/worksheet_sources/wk3-networking-career-cards.md; BLS OOH accessed 2026-08-09).";
const OUT = path.join(__dirname, "../../../docs/resources/slides", isPublic ? "public" : "", "1sw-wk3-day1.pptx");

d.title("Who keeps the Wi-Fi up?", "Networking and data careers.", "College and Career Exploration · Week 3 · Day 1",
  "Bring your notebook, a pencil, and your Chromebook. Find Your Future workbook only if you finish early (p. 38).",
  "Have this up as students walk in. Networking Career Cards printed or open on the Day 1 page. Run time 50 minutes: warm-up 5, compare four careers 22, transferable skills 15, exit ticket 8.", FYF);

// 2 · As you enter
{
  const s = d.slide("As you enter");
  d.card(s, 64, 200, 1152, 190);
  d.body(s, "If the school Wi-Fi went down right now, whose job would it be to fix it?\nWhat do you think they would actually DO to fix it?", 92, 224, 1100, 150, 28, { bold: true });
  d.stem(s, "First they would check ________, because ________.", 64, 430, 1150, "Say it like this", 26);
  d.meta(s, "Be specific: student devices, login accounts, access points, network cables, the server. Two people share.", 64, 540);
  d.notes(s, "0-5 min. Push past 'the IT guy'. You want a checklist verb: check the access point, restart the server, look at the login system. That checklist is what a Network Administrator does on a bad morning.", FYF);
}

// 3 · Today you will
{
  const s = d.slide("Today you will");
  d.numbered(s, ["Compare four careers that keep systems running: Network Administrator, Network Architect, Database Administrator, Systems Analyst.", "Record one technical task and one transferable skill for each.", "Stop and Jot: name a skill that transfers between two careers.", "Exit ticket: a Venn diagram, programming vs. networking."], 64, 205, 1152, 100, 22);
  d.meta(s, "Word of the day: transferable skill. A skill you can carry from one job to another.", 64, 625);
  d.notes(s, "30 seconds.", FYF);
}

// 4 · Four careers
{
  const s = d.slide("Four careers, one network", "Networking Career Cards · link on the Day 1 page");
  const cards = [["Network Administrator", "Keeps the network running day to day: accounts, monitoring, troubleshooting, updates."], ["Network Architect", "Plans and designs the network: equipment, capacity, security, cost tradeoffs."], ["Database Administrator", "Organizes, protects, and backs up data so users get reliable answers."], ["Systems Analyst", "Studies how an organization works and recommends technology changes; translates between tech and non-tech teams."]];
  cards.forEach(([h, t], i) => {
    const x = 64 + (i % 2) * 588, y = 200 + Math.floor(i / 2) * 150;
    d.card(s, x, y, 564, 136);
    d.body(s, h, x + 20, y + 12, 530, 34, 20, { bold: true, color: C.blue });
    d.body(s, t, x + 20, y + 50, 530, 80, 16);
  });
  d.image(s, "bls-netadmin.jpg", 64, 512, 458, 180);
  d.body(s, "Where the cards come from: the BLS Occupational Outlook Handbook, the same site you will use on Day 4.\nThe cards give typical preparation for each career. Typical means common, not required by every employer.", 550, 520, 666, 160, 16, { color: C.muted });
  d.notes(s, "5-9 min. Read the four cards once. Do not put salary numbers on the board today; the cards carry tasks and preparation only, and the exact salary work happens on Day 4 with dated figures. The BLS page shown is the source for the Network Administrator card.", CARDS + " " + BLS);
}

// 5 · Work slide: compare
{
  const s = d.slide("Compare the four roles", "22 minutes · Voice 0 · Card set or notebook entry labeled 1SW Wk3 Networking");
  d.namedRows(s, [["Task", "One technical task this person does. Copy a verb from the card: monitor, back up, design, interview."], ["Skill", "One transferable skill this person needs, and why it matters in this job."]], 64, 200, 720, 120, 130, 18, [C.blue, C.pink]);
  d.body(s, "Four rows: Network Administrator, Network Architect, Database Administrator, Systems Analyst. If you note a salary, keep the job title, place, and date next to it.", 64, 460, 720, 70, 16, { color: C.muted });
  d.card(s, 820, 200, 396, 320);
  d.label(s, "Skills to pick from", 844, 214, 360);
  d.body(s, "problem-solving\ncommunication\nattention to detail\ntime management\nteamwork\ncuriosity\npatience under pressure", 844, 258, 350, 250, 18);
  d.extension(s, "Finished early? Find Your Future p. 38: open Hats & Ladders, Clusters, Information Technology, and do the App Exploration checklist.", 64, 550, 1152, 80);
  d.notes(s, "9-31 min. Four rows, one per career. Lap 1 at minute 8: every student has a task verb for two careers. Lap 2 at minute 18: the skill column says why, not just the skill name. Students who record on the printed cards or in the notebook both count; use the response route your class set up in Week 0. The ten-skill list Doc is linked on the Day 1 page for students who want more choices than the seven on this slide.", CARDS + " " + CV + " " + FYF);
}

// 6 · What is a transferable skill
{
  const s = d.slide("What transfers?", "A transferable skill moves with you from job to job");
  d.card(s, 64, 200, 564, 300);
  d.label(s, "Technical skill", 88, 214, 520, C.pink);
  d.body(s, "Belongs to one job.\nConfigure a router. Restore a database backup. Write a network diagram.", 88, 258, 520, 220, 20);
  d.card(s, 652, 200, 564, 300);
  d.label(s, "Transferable skill", 676, 214, 520, C.green);
  d.body(s, "Goes with you anywhere.\nExplain a problem to someone who is not technical. Notice the small detail that breaks everything. Stay calm when the system is down.", 676, 258, 520, 220, 20);
  d.body(s, "Employers hire for the technical skill. They keep people for the transferable ones.", 64, 530, 1150, 50, 22, { bold: true });
  d.notes(s, "31-34 min. One minute of teaching before the jot. Ask for one example of each from a student's own row before moving on.", CARDS);
}

// 7 · Stop and Jot
{
  const s = d.slide("Stop and Jot", "60 seconds · Voice 0 · In your notebook");
  d.card(s, 64, 200, 1152, 170);
  d.body(s, "Pick a skill from your rows that TWO of the four careers need.\nWrite one complete sentence.", 92, 224, 1100, 130, 26, { bold: true });
  d.stem(s, "________ transfers across ________ and ________\nbecause both workers must ________.", 64, 400, 1150, "Say it like this", 24);
  d.wordBank(s, ["problem-solving", "communication", "attention to detail", "time management", "teamwork", "curiosity", "patience under pressure"], 64, 560);
  d.notes(s, "34-46 min including the discussion. 60 seconds silent, then three students read their sentence. Listen for the 'because' clause; a sentence without it is two job titles and a skill name. Board capture: write each skill students name and tally repeats. That tally is what the exit-ticket Venn draws from.", CARDS);
}

// 8 · Exit ticket: Venn
{
  const s = d.slide("Exit ticket: programming vs. networking", "Open the Day 1 exit ticket on the Canvas page · 8 minutes");
  d.card(s, 64, 200, 720, 330);
  d.body(s, "Pick one programming career from Week 2 (Software Dev, Web Dev, App Dev, or Game Dev).\nPick one networking career from today.", 88, 216, 680, 90, 19);
  d.body(s, "Left: 2 skills only the programmer uses.\nRight: 2 skills only the networking career uses.\nMiddle: 2 skills BOTH need (soft skills, not technical).\nBottom line: why do employers care about the middle as much as the technical sides? One sentence.", 88, 316, 680, 200, 18);
  d.image(s, "cv-d1-exit.png", 820, 200, 396, 140);
  d.meta(s, "The button opens your own copy of the Venn diagram.", 820, 350, 396, 15);
  d.stem(s, "Employers care about ________ because ________.", 64, 560, 1150, "Say it like this", 24);
  d.notes(s, "42-50 min. The button opens a copy of the Venn Doc. The middle must be soft skills; a student who writes 'coding' in the middle has the wrong idea about transfer. Grade the bottom line, not the count.", CV);
}

// 9 · Before you go
{
  const s = d.slide("Before you go");
  d.numbered(s, ["Four rows done: a task and a skill for each career.", "Your Stop and Jot sentence in your notebook.", "Exit ticket submitted."], 64, 205, 1152, 100, 24);
  d.body(s, "Tomorrow: you become a UX designer and audit a real website. Bring your Find Your Future workbook.", 64, 540, 1150, 60, 22, { bold: true });
  d.notes(s, "Last minute. Chromebooks docked. Keep the card sets if students wrote on them; they are Day 1 evidence.", CARDS);
}

d.write(OUT);
