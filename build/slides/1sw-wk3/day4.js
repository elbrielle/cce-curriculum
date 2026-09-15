// CCE · 1SW Wk3 · Day 4 · Emerging IT careers with dated BLS evidence (no workbook pages)
const path = require("path");
const D = require("../lib");
const isPublic = process.env.CCE_PUBLIC === "1";
const d = D.deck({ public: isPublic, assetDir: path.join(__dirname, "assets") });
const { C } = D;
const CV = D.SRC.canvas("2026-09-15");
const BLS = D.SRC.bls("Data Scientists", "https://www.bls.gov/ooh/math/data-scientists.htm", "2026-09-15");
const GUIDE = "Emerging IT Career Evidence Guide (CCE-authored, build/worksheet_sources/wk3-emerging-careers-link-sheet.md; BLS OOH accessed 2026-08-09, May 2024 medians, 2024-34 projections).";
const OUT = path.join(__dirname, "../../../docs/resources/slides", isPublic ? "public" : "", "1sw-wk3-day4.pptx");

d.title("New job, or new name?", "Emerging IT careers, with evidence.", "College and Career Exploration · Week 3 · Day 4",
  "Bring your Chromebook and your Major 1 packet. No workbook today.",
  "Have this up as students walk in. Run time 50 minutes: warm-up 5, choose and model 8, research 30, evidence comparison exit 7. The Emerging IT Career Evidence Guide and the Research Template are both on the Day 4 page.", GUIDE);

// 2 · As you enter
{
  const s = d.slide("As you enter");
  d.card(s, 64, 200, 1152, 190);
  d.body(s, "Name one technology you use today that did NOT exist when your parents were in middle school.", 92, 224, 1100, 150, 28, { bold: true });
  d.stem(s, "________ did not exist then. Somebody had to ________ it, so a new job appeared: ________.", 64, 430, 1150, "Say it like this", 22);
  d.meta(s, "Smartphones, video calls, streaming, AI chatbots. Two people share.", 64, 560);
  d.notes(s, "0-5 min. The third blank is the point: a new technology creates new work, and today's question is whether the government's job data has caught up with that work yet.", GUIDE);
}

// 3 · Today you will
{
  const s = d.slide("Today you will");
  d.numbered(s, ["Learn what 'emerging' means and the exact-or-proxy rule.", "Choose one of six changing IT careers.", "Research it with the dated evidence guide: tasks, preparation, median pay, growth, and the date of every number.", "Compare it to a traditional IT career on the exit ticket."], 64, 205, 1152, 100, 22);
  d.meta(s, "Word of the day: proxy. A broader job used to stand in when your exact job title is not listed.", 64, 625);
  d.notes(s, "30 seconds.", GUIDE);
}

// 4 · What emerging means + exact vs proxy
{
  const s = d.slide("Exact match or proxy?", "The Bureau of Labor Statistics does not list every new job title");
  d.image(s, "bls-datasci.jpg", 64, 200, 700, 275);
  d.meta(s, "A BLS Quick Facts box. Every number has a year next to it. Copy the year every time.", 64, 480, 700, 15);
  d.namedRows(s, [["Exact", "BLS lists your job by name. Data Scientist is exact."], ["Proxy", "BLS lists a broader job that includes yours. Cloud Architect uses Computer Network Architects."], ["None", "A cool job title with no BLS page is not proof the job is new. It is a missing source."]], 800, 200, 416, 100, 120, 15, [C.green, C.blue, C.pink]);
  d.body(s, "Emerging means the work is new or changing fast because of new technology. A new-sounding name by itself is not evidence.", 64, 530, 1150, 60, 20, { bold: true });
  d.notes(s, "5-13 min. Model with the Data Scientists page on the projector: point at the median, the growth rate, and the years next to each. Then say the rule: exact if BLS names your job, proxy if it names a bigger job that includes yours. The evidence guide labels every choice already; students copy the label, they do not decide it.", BLS + " " + GUIDE);
}

// 5 · Choose one of six
{
  const s = d.slide("Choose one career", "Emerging IT Career Evidence Guide · link on the Day 4 page");
  const six = [["AI / Machine Learning Engineer", "proxy"], ["Cloud Architect", "proxy"], ["Information Security Analyst", "exact"], ["Data Scientist", "exact"], ["UX Designer", "closest match"], ["Drone Software Developer", "proxy"]];
  six.forEach(([h, tag], i) => {
    const x = 64 + (i % 3) * 392, y = 200 + Math.floor(i / 3) * 130;
    d.card(s, x, y, 368, 116);
    d.body(s, h, x + 20, y + 14, 330, 60, 19, { bold: true, color: C.blue });
    d.body(s, `BLS label: ${tag}`, x + 20, y + 74, 330, 30, 15, { color: tag === "exact" ? C.green : C.pink });
  });
  d.image(s, "cv-d4-guide.png", 64, 480, 500, 70);
  d.body(s, "The guide carries the BLS occupation, the page link, and the dated numbers for each. Take the choice you can explain in one sentence.", 600, 480, 616, 90, 17, { color: C.muted });
  d.notes(s, "Part of 5-13 min. One minute to choose. Assign a career to anyone still deciding at the minute mark. Six careers across the room is fine; three students on one career is fine.", GUIDE + " " + CV);
}

// 6 · Research work slide
{
  const s = d.slide("Research with dated evidence", "30 minutes · Voice 0 · Open the Emerging Tech Research Template");
  d.image(s, "cv-d4-template.png", 64, 200, 420, 100);
  d.numbered(s, ["Copy the BLS occupation and its label (exact or proxy) from the guide.", "Open the BLS page from the guide. Record tasks, preparation, median pay, growth.", "Write the YEAR next to every number. Guide and website disagree? Use the newer one and say so.", "Explain in two sentences why this work is new or changing."], 64, 310, 720, 72, 14);
  d.card(s, 820, 200, 396, 330);
  d.label(s, "Check yourself", 844, 214, 360);
  d.body(s, "Minute 10: occupation and label written.\nMinute 22: the 'why it is changing' sentences started.", 844, 258, 350, 120, 17);
  d.label(s, "You are done when", 844, 380, 360, C.green);
  d.body(s, "every number has a year, the label matches the guide, and your two sentences name a technology.", 844, 424, 350, 100, 16);
  d.extension(s, "Finished early? Open the Similar Occupations tab on your BLS page and record one job that could be a second proxy.", 64, 610, 1152, 64);
  d.notes(s, "13-43 min. Lap 1 at minute 10 (occupation plus label), lap 2 at minute 22 (the emerging-work explanation). A median is not starting pay and a national number is not a Dallas salary; say it once when you see the first salary written down. Note for you: the printed guide was built from the May 2024 BLS release; the live site now shows 2025 medians and 2025-35 projections. That mismatch is the lesson working as designed (date your sources), but the guide should be regenerated before this week runs again.", GUIDE + " " + BLS + " " + CV);
}

// 7 · Turn and tell
{
  const s = d.slide("Turn and tell", "60 seconds each · Voice 1");
  d.card(s, 64, 200, 1152, 150);
  d.body(s, "Tell your partner which career you chose and whether your evidence is exact or a proxy. Your partner repeats it back in one sentence.", 92, 224, 1100, 110, 24, { bold: true });
  d.stem(s, "BLS reports this exact career.\nBLS reports a related occupation that helps us understand this career.", 64, 380, 1150, "Say it like this", 22);
  d.wordBank(s, ["occupation", "task", "preparation", "median pay", "growth", "exact match", "proxy"], 64, 530);
  d.notes(s, "43-45 min. Two minutes total. Listen for the word proxy used correctly; that is the d(1)(D) evidence for the day.", GUIDE);
}

// 8 · Exit: comparison matrix
{
  const s = d.slide("Exit ticket: emerging vs. traditional", "Open the Emerging/Established IT Career Comparison · 7 minutes");
  d.image(s, "cv-d4-compare.png", 64, 200, 500, 100);
  d.card(s, 64, 320, 720, 240);
  d.body(s, "Your emerging career vs. one traditional IT career (Software Developer, Web Developer, Network Administrator, or Database Administrator).\n\nRows: what they do · median salary (BLS, with year) · growth rate (BLS, with years) · why did this career exist 20 years ago?", 88, 336, 680, 210, 18);
  d.card(s, 820, 200, 396, 360);
  d.label(s, "Bottom line", 844, 214, 360);
  d.body(s, "Which of the two is growing faster right now? Use the growth rates from your matrix to back it up in one sentence.", 844, 258, 350, 200, 19);
  d.stem(s, "________ is growing faster: ____% vs. ____% (BLS, ______).", 64, 580, 1150, "Say it like this", 22);
  d.notes(s, "43-50 min. The button opens a copy of the comparison Doc. The traditional career's numbers come from the Week 2 salary work or the same BLS site; both are fine if dated. Collect this sheet into the Major 1 packet; it is the Emerging Career Evidence rubric row.", CV + " " + GUIDE);
}

// 9 · Before you go
{
  const s = d.slide("Before you go");
  d.numbered(s, ["Research template finished, every number dated.", "Comparison submitted and added to your Major 1 packet.", "Packet turned in: plan, four screens, partner notes, starred changes, evidence sheet."], 64, 205, 1152, 100, 22);
  d.body(s, "Tomorrow is Xello: a quiz about how you learn, then a short lesson. No packet needed.", 64, 540, 1150, 60, 22, { bold: true });
  d.notes(s, "Last minute. Score the packets with the 16-point rubric before Day 5's Xello block; the rubric is on the Day 3 page.", GUIDE);
}

d.write(OUT);
