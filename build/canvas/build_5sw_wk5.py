"""Build the unpublished 5SW Week 5 MoneySkills evidence module."""

import asyncio
import json
import sys

import httpx

import build_5sw_wk1 as prior


common = prior.common
COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/4sw/wk1/day3"
MODULE_NAME = "5SW Wk5: MoneySkills — Budget, Location, and Career Evidence"

DAY_TITLES = {
    1: "PRACTICE: Salary Source and Lifestyle Target",
    2: "PRACTICE: Dallas County Personal Budget",
    3: "PRACTICE: Location Cost Comparison",
    4: "PRACTICE: Paying for Education and Training Check",
    5: "MAJOR 2: Personal Budget Evidence Portfolio",
}


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    found = next((module for module in modules if module["name"] == MODULE_NAME), None)
    data = {"module[published]": "false"}
    if found:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data=data)
    data["module[name]"] = MODULE_NAME
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


QUESTIONS = [
    (
        "Q1 - FAFSA purpose",
        "Which statement accurately describes the FAFSA?",
        "It is a free application used to determine eligibility for federal student aid; submitting it is not an automatic award or loan.",
        ["It is a loan every student must repay.", "It guarantees a full scholarship.", "It is a private lender application."],
        "Correct. Application, eligibility, offer, acceptance, and repayment are different steps.",
        "FAFSA means Free Application for Federal Student Aid. It is not itself an award, scholarship, or loan.",
    ),
    (
        "Q2 - grant and loan",
        "What is the strongest general distinction between a grant and a loan?",
        "A grant generally does not require repayment when its conditions are met; a loan is borrowed money repaid under its terms, usually with interest.",
        ["Both always require repayment with interest.", "A loan is always free money.", "A grant is guaranteed to every applicant."],
        "Correct. Students still verify the exact conditions of every offer.",
        "Keep the repayment obligation and offer-specific conditions visible.",
    ),
    (
        "Q3 - work-study",
        "Which statement stays within the current federal work-study evidence?",
        "An eligible student earns money through an approved job; the amount and available position depend on the award and school.",
        ["It automatically erases all tuition.", "It guarantees a campus job to every applicant.", "It is the same as a private loan."],
        "Correct. Work-study is earned through work and is not a guaranteed tuition discount.",
        "Availability, award amount, and job placement are not automatic.",
    ),
    (
        "Q4 - Texas requirement",
        "Under the current Texas public-school financial-aid requirement, what routes may satisfy the senior-year requirement?",
        "FAFSA, TASFA when applicable, or an authorized signed opt-out.",
        ["Only FAFSA, with no exceptions.", "Taking a private loan.", "Opening a bank account."],
        "Correct. A teacher should use current TEA and district guidance for the student's year.",
        "Texas provides more than one authorized route; the lesson does not require a real application.",
    ),
    (
        "Q5 - apprenticeship boundary",
        "Which statement accurately describes Registered Apprenticeship as a possible education-and-training route?",
        "It combines paid work and structured learning, while openings, eligibility, wages, schedule, and sponsor terms vary.",
        ["It is available immediately for every career and student.", "It always has identical wages and length.", "It is the same as completing the FAFSA."],
        "Correct. Verify an actual sponsor and current opportunity before treating it as available.",
        "The stable structure does not make every opportunity identical or currently open.",
    ),
]


async def upsert_quiz(client):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    found = next((quiz for quiz in quizzes if quiz.get("title") == DAY_TITLES[4]), None)
    data = {
        "quiz[title]": DAY_TITLES[4],
        "quiz[description]": "<p>Ungraded, unlimited-retry practice. Use the feedback to repair financial-aid and training-route claims. Do not enter personal financial information.</p>",
        "quiz[quiz_type]": "practice_quiz",
        "quiz[published]": "false",
        "quiz[allowed_attempts]": "-1",
        "quiz[show_correct_answers]": "true",
        "quiz[shuffle_answers]": "false",
    }
    endpoint = f"/courses/{COURSE_ID}/quizzes/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes"
    quiz = await common.api(client, "PUT" if found else "POST", endpoint, data=data)
    existing = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    for position, (name, prompt, correct, wrong, yes, no) in enumerate(QUESTIONS, 1):
        old = next((question for question in existing if question.get("question_name") == name), None)
        payload = {"question": {"question_name": name, "question_text": prompt, "question_type": "multiple_choice_question", "position": position, "points_possible": 1, "correct_comments": yes, "incorrect_comments": no, "answers": [{"answer_text": correct, "answer_weight": 100}] + [{"answer_text": answer, "answer_weight": 0} for answer in wrong]}}
        path = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{old['id']}" if old else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        await common.api(client, "PUT" if old else "POST", path, json=payload)
    return await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


def student_content(files, visuals, urls):
    link, step = common.file_link, common.step
    rung_media = (
        '<h3 style="color:#315f4c;border-bottom:3px solid #bdd6cb">Optional workbook reminder</h3>'
        '<div style="border-left:5px solid #d39b22;background:#fff8e7;padding:12px 16px;margin:14px 0"><strong>Source-label repair:</strong> the workbook page is a reminder of prior career work, not current salary proof. For scored evidence, record the exact occupation, geography, year/date, and measure shown in Xello or use the fixed fallback card.</div>'
        + prior.image_tag(visuals["career"]["id"], "Find Your Future Rung 3 page prompting a deeper look at one career, including work tasks, training, and salary fields")
        + prior.image_tag(visuals["skills"]["id"], "Find Your Future Rung 3 skills-check page with lifestyle, schedule, education, and priority prompts")
    )
    return {
        1: {"TITLE":"Salary Source and Lifestyle Target","PURPOSE":"Keep a salary number attached to its source and decide which lifestyle needs matter most to you.","TODAY":"<ul><li>audit one salary label;</li><li>read a fixed career card;</li><li>identify lifestyle needs;</li><li>rank three current priorities.</li></ul>","READY":f'<p>Open {link(files["SOURCE"]["id"], "the five-page Salary Source and Lifestyle Target packet")} or <a href="{urls[1]}">the private annotation activity</a>.</p>',"MEDIA":rung_media,"STEPS":step(1,"Audit the label","<p>Write the exact occupation, geography, year or access date, salary measure, and source. Never turn a median into starting pay.</p>")+step(2,"Read the fallback card","<p>Use the fixed BLS Information Security Analysts card when Xello does not display a comparable local figure.</p>")+step(3,"Name your lifestyle target","<p>Describe housing, transportation, food/health, time, and community needs without sharing family income or bills.</p>")+step(4,"Rank current priorities","<p>Choose three and explain why each matters now. A priority can change.</p>"),"EXIT":"<p>Name one salary label you repaired and one lifestyle priority the number alone cannot decide.</p>","DONE":"<ul><li>complete source audit;</li><li>one fixed-card interpretation;</li><li>five lifestyle areas considered;</li><li>three ranked priorities;</li><li>one evidence limitation.</li></ul>","SUPPORT":"<p>salary measure = tipo de salario · median = mediana · geography = ubicación · lifestyle priority = prioridad de estilo de vida · limitation = límite.</p>","FALLBACK":"<p>The fixed card is complete evidence. Xello is the preferred local cross-check when available; H&amp;L and open search are optional. No personal financial disclosure is required.</p>"},
        2: {"TITLE":"Build a Dallas County Personal Budget","PURPOSE":"Use one fixed adult scenario to build and revise a monthly plan without exposing anyone's real finances.","TODAY":"<ul><li>read a dated Dallas County scenario;</li><li>follow a worked reduction model;</li><li>build a balanced monthly plan;</li><li>explain tradeoffs and limits.</li></ul>","READY":f'<p>Open {link(files["BUDGET"]["id"], "the six-page Dallas County budget packet")} or <a href="{urls[2]}">the private annotation activity</a>. The scenario is fictional and uses one adult with no children.</p>',"MEDIA":"","STEPS":step(1,"Read before changing","<p>The MIT scenario requires about $48,489 before tax and about $41,399 after tax each year. The rounded monthly expense plan is about $3,450.</p>")+step(2,"Follow the model","<p>The model uses a fictional lower income and shows tradeoffs. It does not claim every reduction is realistic for every person.</p>")+step(3,"Build your plan","<p>Keep the starting amount fixed, calculate each row, and show whether income minus expenses balances.</p>")+step(4,"Explain the limits","<p>Name one realistic revision and one important need the simplified budget does not include.</p>"),"EXIT":"<p>State the final balance, one tradeoff, and one missing factor.</p>","DONE":"<ul><li>all budget rows completed;</li><li>math checked;</li><li>one revision explained;</li><li>one limit named;</li><li>private submission.</li></ul>","SUPPORT":"<p>income = ingreso · expense = gasto · balance = saldo · tradeoff = decisión con ventaja y costo · fixed scenario = escenario fijo.</p>","FALLBACK":"<p>Use the supplied scenario only. Do not submit family wages, rent, debt, immigration information, aid status, or real account data.</p>"},
        3: {"TITLE":"Compare the Same Household Across Locations","PURPOSE":"Compare four current living-cost scenarios without changing household size or inventing local salary claims.","TODAY":"<ul><li>compare one adult/no children in four counties;</li><li>calculate yearly gaps;</li><li>identify nonfinancial factors;</li><li>make a bounded recommendation.</li></ul>","READY":f'<p>Open {link(files["LOCATION"]["id"], "the five-page Location Cost Comparison packet")} or <a href="{urls[3]}">the private annotation activity</a>.</p>',"MEDIA":"","STEPS":step(1,"Keep the scenario constant","<p>Dallas, Tulsa, Los Angeles, and New York County all use one adult with no children from MIT's February 15, 2026 update.</p>")+step(2,"Calculate two comparisons","<p>Record the required annual before-tax income, yearly gap from Dallas, and whether Dallas is higher or lower.</p>")+step(3,"Add what money misses","<p>Consider family/support network, transportation access, climate, job availability, community, and personal goals.</p>")+step(4,"Recommend for fictional Jordan","<p>Use three numbers, two nonfinancial factors, and one question that still needs research.</p>"),"EXIT":"<p>Name one numerical finding and one reason it cannot decide where a person should live.</p>","DONE":"<ul><li>three location records;</li><li>yearly gaps checked;</li><li>two nonfinancial factors;</li><li>three-number recommendation;</li><li>one research question.</li></ul>","SUPPORT":"<p>same household = mismo hogar · yearly gap = diferencia anual · before tax = antes de impuestos · nonfinancial = no financiero.</p>","FALLBACK":"<p>All numbers are supplied. A calculator, typed work, dictation, or paper is allowed. No student must disclose a real home plan or family situation.</p>"},
        4: {"TITLE":"Paying for Education and Training","PURPOSE":"Distinguish aid and training routes, then build a verification sequence without completing a real application.","TODAY":"<ul><li>compare grants, scholarships, work-study, loans, savings, employer help, and apprenticeship;</li><li>repair common FAFSA claims;</li><li>build a five-step verification sequence;</li><li>practice with feedback.</li></ul>","READY":f'<p>Open {link(files["AID"]["id"], "the five-page Paying for Education and Training guide")} and <a href="{urls[4]}">the retryable practice Quiz</a>.</p>',"MEDIA":"","STEPS":step(1,"Compare route types","<p>Record what each route can help pay and what must be verified. Do not treat every route as equally available.</p>")+step(2,"Repair three claims","<p>FAFSA is an application, not an automatic loan or award. Texas currently permits FAFSA, TASFA when applicable, or an authorized signed opt-out.</p>")+step(3,"Build a sequence","<p>Use official sources, compare offers, identify repayment/conditions, verify the provider, and decide only after the evidence is clear.</p>")+step(4,"Use feedback","<p>Retake the Quiz until every explanation makes sense. Quiz attempts are not graded.</p>"),"EXIT":"<p>Correct one misconception and name the official source you would verify next.</p>","DONE":"<ul><li>seven route types compared;</li><li>three claims repaired;</li><li>five-step sequence;</li><li>Quiz feedback reviewed;</li><li>no real application submitted.</li></ul>","SUPPORT":"<p>grant = subvención · scholarship = beca · work-study = trabajo-estudio · loan = préstamo · repayment = reembolso · opt-out = exclusión autorizada.</p>","FALLBACK":"<p>The packet contains the full route. Do not enter a Social Security number, tax data, family income, immigration details, FSA ID, bank information, or application data.</p>"},
        5: {"TITLE":"Personal Budget and Career Evidence Portfolio","PURPOSE":"Compare three careers on one salary basis and revise a budget decision using accurate labels and your current priorities.","TODAY":"<ul><li>compare three careers;</li><li>publish the math;</li><li>connect evidence to lifestyle priorities;</li><li>audit and revise before private submission.</li></ul>","READY":f'<p>Open {link(files["PORTFOLIO"]["id"], "the six-page portfolio")} and {link(files["RUBRIC"]["id"], "the two-page rubric")}. Days 1–4 may help as references, but you do not attach those formative packets again.</p>',"MEDIA":"","STEPS":step(1,"Use one salary basis","<p>Use exact Xello labels for all three careers only when they are comparable. Otherwise use the fixed May 2024 U.S. BLS medians in the packet.</p>")+step(2,"Compare all three","<p>For each career record source/date/geography/measure, preparation, evidence, personal fit, and one limitation.</p>")+step(3,"Publish the math","<p>Show annual salary minus annual before-tax target for all three careers. Record the revised monthly planning result, then explain why a positive number does not prove affordability or fit.</p>")+step(4,"Audit and submit privately",f'<p>Use <a href="{urls[5]}">the private portfolio Assignment</a>. Revise the weakest rubric criterion before submitting this one self-contained packet by upload, text, media, or paper.</p>'),"EXIT":"<p>Name one repaired source label, one budget revision, and one unsupported claim you removed.</p>","DONE":"<ul><li>three comparable career records;</li><li>three visible salary-minus-target calculations;</li><li>revised monthly planning result;</li><li>priority-based decision;</li><li>source limitation;</li><li>self-audit and revision;</li><li>private submission.</li></ul>","SUPPORT":"<p>comparable = comparable · preparation = preparación · annual target = meta anual · evidence limitation = límite de evidencia · revise = revisar.</p>","FALLBACK":"<p>The fixed three-career evidence is complete. The Day 5 packet is self-contained. No public discussion, Xello screenshot, family budget, prior-packet attachment, or H&amp;L favorite is required.</p>"},
    }


def teacher_content(files):
    link, flow = common.file_link, common.flow
    c = "#315f4c"
    content = {
        1:{"TITLE":"Salary Source and Lifestyle Target","SUBTITLE":"50 minutes · TEKS d(5)(A), d(5)(D)","ALERT":"<strong>Do not convert salary labels.</strong> Median, starting, typical, range, local, and national are different measures. Xello is the preferred local source; the fixed BLS card is the no-login route.","PREP":f'<ul><li>Post {link(files["SOURCE"]["id"], "the source/lifestyle packet")} and annotation activity.</li><li>Project one complete source label.</li><li>Do not request real family financial information.</li></ul>',"EVIDENCE":"<p>Salary audit, fixed-card interpretation, lifestyle target, three priorities, and limitation. Practice/minor candidate.</p>","FLOW":flow(c,"Warm-up · 5","What one salary cannot decide.")+flow("#4c8b38","Source audit · 10","Occupation, place, date, measure.")+flow("#8a4f2b","Career card · 10","Fixed evidence and limitation.")+flow("#d39b22","Lifestyle target · 20","Needs and ranked priorities.")+flow(c,"Exit · 5","Label and missing decision."),"MONITOR":"<p>Full source labels retain occupation, geography, date/year, measure, and source. The fallback $124,910 is the May 2024 U.S. median for Information Security Analysts—not DFW or starting pay. Score reasoning, not the student's chosen priorities.</p>","RESOURCES":'<p><a href="https://www.bls.gov/ooh/computer-and-information-technology/information-security-analysts.htm">BLS Information Security Analysts</a>. Xello local values require the exact displayed geography, measure, and access date.</p>',"SUPPORT":"<p>Five packet pages deliberately separate short labels from multi-sentence lifestyle reasoning. Accept typing, dictation, annotation, or paper.</p>","FALLBACK":"<p>Fixed evidence replaces any failed login. H&amp;L, open search, screenshots, and personal disclosure are not required.</p>"},
        2:{"TITLE":"Build a Dallas County Personal Budget","SUBTITLE":"50 minutes · TEKS d(5)(D)","ALERT":"<strong>Use a fictional fixed scenario.</strong> Never ask students to reveal family income, housing costs, debt, aid, immigration status, or financial stress.","PREP":f'<ul><li>Post {link(files["BUDGET"]["id"], "the six-page budget packet")} and annotation activity.</li><li>Provide calculators.</li><li>Model one subtraction and one tradeoff.</li></ul>',"EVIDENCE":"<p>Balanced/revised monthly plan, visible math, two tradeoffs, and one limitation. Practice/minor candidate.</p>","FLOW":flow(c,"Warm-up · 5","Needs, wants, and unknowns.")+flow("#4c8b38","Scenario · 8","Dated Dallas County evidence.")+flow("#8a4f2b","Worked model · 10","Math and tradeoff.")+flow("#d39b22","Build/revise · 22","Individual fictional plan.")+flow(c,"Exit · 5","Balance, tradeoff, limit."),"MONITOR":"<p>MIT Dallas County, one adult/no children, updated Feb. 15, 2026: $23.31/hour and $48,489 before tax annually. Rounded monthly expense model totals about $3,450. A lower-income revision can reveal a gap; there is no required cheerful or balanced outcome.</p>","RESOURCES":'<p><a href="https://livingwage.mit.edu/counties/48113">MIT Living Wage Calculator — Dallas County</a>. This is an illustrative scenario, not individualized financial advice.</p>',"SUPPORT":"<p>Page 4 gives a roomy calculation table; Pages 5–6 provide separate lines for tradeoffs, missing needs, balance, and revision.</p>","FALLBACK":"<p>Use the supplied scenario only. Paper, typed, dictated, and annotation routes are equal.</p>"},
        3:{"TITLE":"Compare the Same Household Across Locations","SUBTITLE":"50 minutes · TEKS d(5)(D)","ALERT":"<strong>Hold household assumptions constant.</strong> This is a living-cost comparison, not a claim that one location or lifestyle is best.","PREP":f'<ul><li>Post {link(files["LOCATION"]["id"], "the five-page location packet")} and annotation activity.</li><li>Provide calculators.</li><li>Model Dallas versus one location.</li></ul>',"EVIDENCE":"<p>Three location records, calculated gaps, nonfinancial factors, and a bounded Jordan recommendation. Practice/minor candidate.</p>","FLOW":flow(c,"Warm-up · 5","What changes by location?")+flow("#4c8b38","Evidence table · 8","Same household and date.")+flow("#8a4f2b","Compare · 20","Three yearly gaps.")+flow("#d39b22","Recommend · 12","Numbers plus nonfinancial factors.")+flow(c,"Exit · 5","Finding and limitation."),"MONITOR":"<p>Required annual before-tax incomes: Dallas $48,489; Tulsa $44,165; Los Angeles $60,161; New York County $79,469. Expected gaps from Dallas: Tulsa −$4,324; Los Angeles +$11,672; New York +$30,980. Accept different recommendations when three figures, two nonfinancial factors, and one unresolved question are present.</p>","RESOURCES":'<p><a href="https://livingwage.mit.edu/">MIT Living Wage Calculator</a>, one adult/no children, updated Feb. 15, 2026. Do not compare different household types.</p>',"SUPPORT":"<p>Each location gets a full landscape page and eight writing lines. Calculator, typed response, dictation, and paper are allowed.</p>","FALLBACK":"<p>All numbers are fixed; no live search or personal relocation plan is required.</p>"},
        4:{"TITLE":"Paying for Education and Training","SUBTITLE":"50 minutes · TEKS d(3)(C)","ALERT":"<strong>Financial-aid literacy, not application completion.</strong> Do not collect or enter SSNs, tax data, family income, immigration information, FSA IDs, bank details, or signatures.","PREP":f'<ul><li>Post {link(files["AID"]["id"], "the five-page guide")} and unpublished Quiz.</li><li>Open current Federal Student Aid and TEA sources.</li><li>Use fictional cases only.</li></ul>',"EVIDENCE":"<p>Seven-route comparison, three claim repairs, a five-step verification sequence, and Quiz feedback. Formative.</p>","FLOW":flow(c,"Warm-up · 5","Application, award, or debt?")+flow("#4c8b38","Route types · 12","Aid and training options.")+flow("#8a4f2b","Claim repair · 10","FAFSA/Texas boundaries.")+flow("#d39b22","Cases/sequence · 18","Verify before deciding.")+flow(c,"Quiz/exit · 5","Feedback and next source."),"MONITOR":"<p>Key: FAFSA is free and supports eligibility review; it is not itself an award or automatic loan. Grants and scholarships have conditions. Work-study is earned through an eligible job. Loans require repayment under their terms. Registered Apprenticeship is paid work plus structured learning, but sponsor terms vary. Texas current routes include FAFSA, TASFA when applicable, or authorized signed opt-out.</p>","RESOURCES":'<p><a href="https://studentaid.gov/articles/fafsa-student-steps/">Federal Student Aid FAFSA steps</a> · <a href="https://studentaid.gov/sites/default/files/how-financial-aid-works.pdf">How Financial Aid Works</a> · <a href="https://tea.texas.gov/student-readiness-and-high-school/college-career-and-military-prep/financial-aid-requirement">TEA financial-aid requirement</a> · <a href="https://www.apprenticeship.gov/career-seekers">Apprenticeship.gov</a>.</p>',"SUPPORT":"<p>Required directions stay visible. The packet uses one route per row and separate full-page fictional cases. Quiz feedback can be read aloud.</p>","FALLBACK":"<p>The packet works offline. No real FAFSA, TASFA, scholarship, loan, provider, or apprenticeship application is completed.</p>"},
        5:{"TITLE":"Personal Budget and Career Evidence Portfolio","SUBTITLE":"50 minutes · TEKS d(5)(D), d(5)(E)","ALERT":"<strong>Major draft only.</strong> Keep unpublished and ungraded until the six-weeks assessment count and 40/60 groups are verified. Career preference and family finances are not scored.","PREP":f'<ul><li>Post {link(files["PORTFOLIO"]["id"], "the six-page portfolio")}, {link(files["RUBRIC"]["id"], "the rubric")}, and private Assignment.</li><li>Keep the fixed three-career fallback visible.</li><li>Have calculators available.</li><li>Do not require students to attach Days 1–4 or reopen those formative submissions to score this major.</li></ul>',"EVIDENCE":"<p>One self-contained portfolio: three comparable career records, three visible salary-minus-target calculations, revised monthly result, priority-based decision, source limitation, self-audit, and revision.</p>","FLOW":flow(c,"Warm-up · 5","Comparable evidence gate.")+flow("#4c8b38","Career records · 18","Three careers, same basis.")+flow("#8a4f2b","Math · 10","Three salary-minus-target calculations.")+flow("#d39b22","Decide/revise · 12","Priorities, monthly result, limit, audit.")+flow(c,"Submit · 5","One private equivalent-route submission."),"MONITOR":"<p>Fixed May 2024 U.S. medians: Architects $96,690; Civil Engineers $99,590; Electricians $62,350. Dallas annual before-tax target: $48,489. Expected differences: $48,201; $51,101; $13,861. A positive difference is not take-home pay and does not prove affordability, job availability, fit, or starting salary. Score four criteria at 0–4 using only the self-contained Day 5 portfolio: budget calculation/interpretation, source/measure accuracy, three-career comparison, and financial decision/revision.</p>","RESOURCES":'<p><a href="https://www.bls.gov/ooh/architecture-and-engineering/architects.htm">BLS Architects</a> · <a href="https://www.bls.gov/ooh/architecture-and-engineering/civil-engineers.htm">BLS Civil Engineers</a> · <a href="https://www.bls.gov/ooh/construction-and-extraction/electricians.htm">BLS Electricians</a> · <a href="https://livingwage.mit.edu/counties/48113">MIT Dallas County</a>.</p>',"SUPPORT":"<p>Each career has a full landscape page; calculations have dedicated rows; factor explanations and the final decision/revision use full-width lines. Accept upload, text, media, dictation, or paper.</p>","FALLBACK":"<p>Use fixed career evidence when Xello is unavailable or labels are not comparable. The Day 5 packet is self-contained. No public Discussion, private profile screenshot, family budget, prior-packet attachment, or H&amp;L favorite is required.</p>"},
    }
    # Canonical grading labels come from the locked six-weeks assessment map.
    content[1]["EVIDENCE"] = "<p>Formative salary audit, fixed-card interpretation, lifestyle target, three priorities, and limitation.</p>"
    content[2]["EVIDENCE"] = "<p>Formative balanced/revised monthly plan, visible math, two tradeoffs, and one limitation.</p>"
    content[3]["EVIDENCE"] = "<p>Formative three-location comparison, calculated gaps, nonfinancial factors, and a bounded Jordan recommendation.</p>"
    content[5]["ALERT"] = "<strong>Major 2 in the 5SW assessment map.</strong> Keep unpublished and ungraded until the Major group and 60% weighting are verified. Career preference and family finances are not scored."
    content[5]["EVIDENCE"] = "<p><strong>Major 2:</strong> three comparable career records, visible calculations, priority-based decision, source limitation, self-audit, and revision. Convert the 16-point rubric result to a 100-point grade only after the Major group is verified.</p>"
    return content


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        module = await ensure_module(client)
        support_path = "course files/CCR Materials/5SW/Wk5"
        support_folder = await common.ensure_folder(client, support_path)
        worksheet_names = {"SOURCE":"5sw-wk5-salary-source-and-lifestyle-target.pdf","BUDGET":"5sw-wk5-dallas-county-personal-budget.pdf","LOCATION":"5sw-wk5-location-cost-comparison.pdf","AID":"5sw-wk5-paying-for-education-and-training.pdf","PORTFOLIO":"5sw-wk5-three-career-budget-portfolio.pdf","RUBRIC":"5sw-wk5-budget-portfolio-rubric.pdf"}
        files = {key: await common.upload(client, ROOT / "docs/resources/worksheets" / name, support_path) for key, name in worksheet_names.items()}
        visual_path = "course files/CCR Materials/5SW/Wk5/Locked Licensed Visuals"
        await common.ensure_folder(client, visual_path)
        visuals = {"career": await common.upload(client, ASSETS / "fyf-rung-3-career-deep-dive.jpg", visual_path), "skills": await common.upload(client, ASSETS / "fyf-rung-3-skills-check.jpg", visual_path)}
        quiz = await upsert_quiz(client)
        attachments = {1:"SOURCE",2:"BUDGET",3:"LOCATION"}
        assignments = {}
        for day in range(1, 4):
            assignments[day] = await common.upsert_assignment(client, DAY_TITLES[day], "<p>Complete privately by annotation, upload, typed labeled responses, or paper. Do not disclose real family financial information.</p>", ["student_annotation","online_upload","online_text_entry"], files[attachments[day]]["id"])
        assignments[5] = await common.upsert_assignment(client, DAY_TITLES[5], "<p>Submit the private portfolio by upload, text, media, or paper. Keep unpublished and ungraded until the 40/60 assessment map is verified.</p>", ["online_upload","online_text_entry","media_recording"], files["PORTFOLIO"]["id"])
        urls = {1:f"/courses/{COURSE_ID}/assignments/{assignments[1]['id']}",2:f"/courses/{COURSE_ID}/assignments/{assignments[2]['id']}",3:f"/courses/{COURSE_ID}/assignments/{assignments[3]['id']}",4:f"/courses/{COURSE_ID}/quizzes/{quiz['id']}",5:f"/courses/{COURSE_ID}/assignments/{assignments[5]['id']}"}
        student, teacher = student_content(files, visuals, urls), teacher_content(files)
        names = {1:"Salary Source and Lifestyle Target",2:"Build a Dallas County Personal Budget",3:"Compare the Same Household Across Locations",4:"Paying for Education and Training",5:"Personal Budget and Career Evidence Portfolio"}
        pages, order = {}, []
        interactions = {1:("Assignment",assignments[1]["id"],DAY_TITLES[1]),2:("Assignment",assignments[2]["id"],DAY_TITLES[2]),3:("Assignment",assignments[3]["id"],DAY_TITLES[3]),4:("Quiz",quiz["id"],DAY_TITLES[4]),5:("Assignment",assignments[5]["id"],DAY_TITLES[5])}
        for day in range(1, 6):
            header_title = f"Day {day} · {names[day]}"
            header = await prior.upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 5SW Wk5 Day {day} - {names[day]}"
            student_page = await common.upsert_page(client, student_title, common.render("5sw-wk5-student.html", {"COURSE_ID":COURSE_ID,"DAY":day,**student[day]}))
            teacher_title = f"TEACHER: 5SW Wk5 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(client, teacher_title, common.render("5sw-wk5-teacher.html", {"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student_page["url"],**teacher[day]}))
            await prior.upsert_item(client,module["id"],"Page",teacher_page["url"],teacher_title)
            await prior.upsert_item(client,module["id"],"Page",student_page["url"],student_title)
            kind,key,title = interactions[day]
            await prior.upsert_item(client,module["id"],kind,key,title)
            order.extend([("Page",teacher_page["url"],teacher_title),("Page",student_page["url"],student_title),(kind,key,title)])
            pages[day] = {"teacher":teacher_page,"student":student_page}
        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position,(kind,key,title) in enumerate(order,1):
            item = next(item for item in items if (kind == "SubHeader" and item.get("id") == key) or (kind == "Page" and item.get("page_url") == key) or (kind in ("Assignment","Quiz") and item.get("content_id") == key))
            await common.api(client,"PUT",f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}",data={"module_item[position]":position,"module_item[title]":title})
        final_items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        module = await common.api(client,"GET",f"/courses/{COURSE_ID}/modules/{module['id']}")
        print(json.dumps({"module":{"id":module["id"],"published":module["published"]},"support_folder":{"id":support_folder["id"],"locked":support_folder["locked"]},"files":{key:value["id"] for key,value in files.items()},"visuals":{key:value["id"] for key,value in visuals.items()},"quiz":{"id":quiz["id"],"published":quiz.get("published")},"assignments":{str(day):{"id":value["id"],"published":value.get("published")} for day,value in assignments.items()},"pages":{str(day):{kind:{"url":value["url"],"published":value["published"]} for kind,value in pair.items()} for day,pair in pages.items()},"items":[{"position":item["position"],"type":item["type"],"title":item["title"]} for item in final_items]},indent=2))


if __name__ == "__main__":
    asyncio.run(main())
