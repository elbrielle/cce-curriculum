"""Build the unpublished 6SW Week 3 marketing module."""

import asyncio
import json
import sys
from urllib.parse import urlencode

import httpx

import build_5sw_wk1 as prior
from configure_assessment_map import SUBMISSION_LINK_MARKER


common = prior.common
COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/6sw/wk3"
MODULE_NAME = "6SW Wk3: Marketing - Audience, Entrepreneurship, and Data"
TITLES = {
    1: "PRACTICE: Click Factor Audience Test and Revision",
    2: "PRACTICE: Written Communication and Changing Conditions",
    3: "PRACTICE: Expert Edge Opportunity and Revision",
    4: "PRACTICE: Family Fun Pass Evidence Decision",
    5: "MINOR 3: Ethical Marketing Evidence Brief",
}
MINOR_ALIASES = ("MINOR 3: Marketing Evidence Brief",)

CONTRACTS = {
    1: {
        "TOPIC": "Audience and Message",
        "OBJECTIVE": "Students will identify a marketing career opportunity and use supplied product evidence to create, test, and revise a truthful audience-specific call to action.",
        "TEKS": "d(1)(C)",
        "DOL": "Completed FYF Click Factor work plus a two-page individual audience test, visible revision, and career/work-product connection.",
        "I_CAN": "identify a marketing career and use product evidence to create, test, and revise a truthful call to action for an audience.",
        "SHOW": "Complete Click Factor and the two-page companion with an audience-message chain, test evidence, visible revision, and career connection.",
    },
    2: {
        "TOPIC": "Changing Conditions",
        "OBJECTIVE": "Students will identify a marketing career opportunity and analyze how one economic condition and one societal or technology condition could change marketing work and preparation.",
        "TEKS": "d(1)(C), d(5)(C)",
        "DOL": "Completed FYF Little Library message plus a two-page individual revision, fixed-source condition comparison, preparation recommendation, and career connection.",
        "I_CAN": "identify a marketing career and explain how economic and societal or technology changes could affect the work and preparation.",
        "SHOW": "Complete the FYF message and two-page companion with a visible revision, two distinct condition effects, preparation recommendation, and career connection.",
    },
    3: {
        "TOPIC": "Entrepreneurship",
        "OBJECTIVE": "Students will identify a fictional entrepreneurial opportunity by connecting a skill, audience need, deliverable, responsibility, and risk to a marketing career.",
        "TEKS": "d(1)(C), d(3)(I)",
        "DOL": "Completed FYF Expert Edge plan plus a two-page individual opportunity, responsibility/risk, private test, revision, and career connection.",
        "I_CAN": "define entrepreneurship by connecting a need, deliverable, responsibility, and risk to a fictional opportunity and marketing career.",
        "SHOW": "Complete Expert Edge and the two-page companion with an opportunity chain, responsibility/risk/control, private test, visible revision, and career connection.",
    },
    4: {
        "TOPIC": "Data-Informed Decisions",
        "OBJECTIVE": "Students will identify how a marketing career uses preference, performance, and qualitative evidence to choose a strategy, name a limitation, and plan a next test.",
        "TEKS": "d(1)(C)",
        "DOL": "Completed FYF Family Fun Pass work plus a two-page individual goal, three-point evidence stack, decision rule, limitation, next test, and career connection.",
        "I_CAN": "explain how a marketing worker uses different evidence to choose a strategy, name a limit, and plan a next test.",
        "SHOW": "Complete the FYF decision and two-page companion with a goal, three evidence points, decision rule, limitation, next test, and career connection.",
    },
    5: {
        "TOPIC": "Ethical Marketing",
        "OBJECTIVE": "Students will create an evidence brief that identifies a marketing career and entrepreneurial opportunity, explains an ethical audience message and data-informed decision, and analyzes distinct effects of economic and societal or technology change.",
        "TEKS": "d(1)(C), d(3)(I), d(5)(C)",
        "DOL": "Private four-page Marketing Evidence Brief plus a 16-point self-score and one visible evidence-based revision.",
        "I_CAN": "use this week's evidence to explain an ethical marketing decision, entrepreneurial opportunity, career connection, and two different changing-condition effects.",
        "SHOW": "Submit the private four-page Marketing Evidence Brief, complete the 16-point self-score, and make one visible evidence-based revision.",
    },
}


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    matches = [module for module in modules if module.get("name") == MODULE_NAME]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one {MODULE_NAME!r} module; found {len(matches)}")
    data = {"module[published]": "false", "module[name]": MODULE_NAME}
    if matches:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{matches[0]['id']}", data=data)
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


async def mapped_minor_assignment(client):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    accepted = {TITLES[5], *MINOR_ALIASES}
    matches = [entry for entry in assignments if entry.get("name") in accepted]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one existing mapped Marketing Minor named in {sorted(accepted)!r}; found {len(matches)}")
    found = matches[0]
    if float(found.get("points_possible") or 0) != 100:
        raise RuntimeError(f"Refusing to modify Marketing Minor: expected 100 points, found {found.get('points_possible')}")
    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group = next((entry for entry in groups if entry.get("id") == found.get("assignment_group_id")), None)
    if not group or group.get("name") != "Minor Assessments (40%)":
        raise RuntimeError("Refusing to modify Marketing Minor outside Minor Assessments (40%)")
    return found


async def require_minor_assignment(client, description):
    found = await mapped_minor_assignment(client)
    scoring_note = (
        '<div data-cce-rubric-note="cce-advisory-rubric-v1" '
        'style="border-left:4px solid #155d7a;padding:10px 14px;margin:16px 0">'
        '<p><strong>How this is scored:</strong> Use the student-visible Canvas rubric. '
        'Add the raw criterion ratings out of 16, divide by 16, multiply by 100, and round '
        'to the nearest whole point. Enter that percentage as the score out of 100. A score '
        'below 60 follows campus recovery or reassessment policy.</p>'
        '<p>The rubric is advisory in Canvas so its raw total cannot silently replace the '
        '100-point district grade.</p></div>'
    )
    return await common.api(client, "PUT", f"/courses/{COURSE_ID}/assignments/{found['id']}", data={
        "assignment[name]": TITLES[5],
        "assignment[description]": description + scoring_note,
        "assignment[published]": "false",
        "assignment[points_possible]": "100",
        "assignment[grading_type]": "points",
        "assignment[omit_from_final_grade]": "false",
        "assignment[submission_types][]": ["online_upload", "online_text_entry"],
    })


QUESTIONS = [
    ("Q1 - ethical CTA", "Which call to action crosses the lesson boundary?", "Only 2 left - guaranteed! when neither claim is verified", ["See the five dessert skills you will practice.", "Compare the weekly snack-box options.", "Choose the car-wash plan that fits your schedule."], "Correct. Urgency, scarcity, and guarantees must be truthful.", "Accurate product information and direct comparison can support an informed choice."),
    ("Q2 - salary label", "What does the $76,950 figure mean in this lesson?", "BLS May 2024 U.S. median pay for Market Research Analysts and Marketing Specialists", ["Guaranteed DFW starting pay", "The pay for every marketing worker", "A student's expected first salary"], "Correct. Measure, date, geography, and occupation stay visible.", "It is a dated national median, not local starting pay or a guarantee."),
    ("Q3 - openings and growth", "Which statement uses the BLS evidence accurately?", "The occupation is projected to grow 7% from 2024-34 and average about 87,200 openings per year; these are different measures.", ["There will be exactly 87,200 new jobs every year.", "Every graduate has a 7% chance of a job.", "The figures prove a DFW shortage."], "Correct. Growth and average annual openings are different measures.", "The figures do not prove individual outcomes or a local shortage."),
    ("Q4 - changing conditions", "Which example is a societal or technology condition rather than an economic condition?", "Customers expect accessible mobile content and clear privacy choices.", ["A company cuts its campaign budget after customers spend less.", "A business delays hiring because sales fall.", "A store reduces promotion spending during a slowdown."], "Correct. Audience expectations, access, privacy, and tools are societal or technology conditions.", "Spending, budgets, demand, and hiring are economic effects in this comparison."),
    ("Q5 - platform boundary", "What counts as the required evidence this week?", "The private Canvas or paper reasoning and revision; H&L, Xello, eDynamic, Canva, and Adobe Express are optional supports.", ["Two H&L favorites", "A Xello School Subjects completion screen", "A public social-media post"], "Correct. Standards evidence is reasoning and revision, not a platform click.", "No public post or supplemental platform completion is required."),
]


async def upsert_quiz(client):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    matches = [quiz for quiz in quizzes if quiz.get("title") == TITLES[2]]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one {TITLES[2]!r} Quiz; found {len(matches)}")
    data = {
        "quiz[title]": TITLES[2],
        "quiz[description]": "<p>Ungraded, unlimited-retry practice on ethical communication, current source labels, changing conditions, and platform boundaries.</p>",
        "quiz[quiz_type]": "practice_quiz",
        "quiz[published]": "false",
        "quiz[allowed_attempts]": "-1",
        "quiz[show_correct_answers]": "true",
        "quiz[shuffle_answers]": "false",
    }
    quiz = await common.api(client, "PUT" if matches else "POST", f"/courses/{COURSE_ID}/quizzes/{matches[0]['id']}" if matches else f"/courses/{COURSE_ID}/quizzes", data=data)
    existing = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    desired_names = {name for name, *_rest in QUESTIONS}
    for question in existing:
        if question.get("question_name") not in desired_names:
            await common.api(client, "DELETE", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{question['id']}")
    existing = [entry for entry in existing if entry.get("question_name") in desired_names]
    seen = set()
    for question in existing:
        name = question.get("question_name")
        if name in seen:
            await common.api(client, "DELETE", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{question['id']}")
        else:
            seen.add(name)
    for position, (name, prompt, correct, wrong, yes, no) in enumerate(QUESTIONS, 1):
        old = next((question for question in existing if question.get("question_name") == name), None)
        payload = {"question": {"question_name": name, "question_text": prompt, "question_type": "multiple_choice_question", "position": position, "points_possible": 1, "correct_comments": yes, "incorrect_comments": no, "answers": [{"answer_text": correct, "answer_weight": 100}] + [{"answer_text": answer, "answer_weight": 0} for answer in wrong]}}
        path = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{old['id']}" if old else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        await common.api(client, "PUT" if old else "POST", path, json=payload)
    expected = [name for name, *_rest in QUESTIONS]
    final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    by_name = {entry.get("question_name"): entry for entry in final_questions}
    if set(by_name) != set(expected) or len(final_questions) != len(expected):
        raise RuntimeError("Marketing practice Quiz question set mismatch")
    fields = []
    for name in expected:
        fields.extend([("order[][id]", str(by_name[name]["id"])), ("order[][type]", "question")])
    await common.api(client, "POST", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/reorder", content=urlencode(fields), headers={"Content-Type": "application/x-www-form-urlencoded"})
    final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    if [entry.get("question_name") for entry in final_questions] != expected:
        raise RuntimeError("Marketing practice Quiz order mismatch")
    return await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


def student_content(files, visuals, urls):
    link, step = common.file_link, common.step
    media = lambda pairs: '<h3 style="color:#9a4d19;border-bottom:3px solid #efc5aa">Licensed workbook pages</h3>' + ''.join(prior.image_tag(visuals[key]["id"], alt) for key, alt in pairs)
    minor_panel = (
        f'<section data-cce-marker="{SUBMISSION_LINK_MARKER}" '
        'style="border:2px solid #155d7a;border-radius:12px;padding:18px 20px;margin:24px 0;background:#eef8fc">'
        '<h3 style="margin:0 0 8px;color:#155d7a">Submit your minor evidence</h3>'
        '<p style="margin:0 0 14px">Use the visible rubric to check your work, then submit through this private Canvas assignment. Your teacher will tell you whether to type, upload a file, or turn in the paper route.</p>'
        f'<p style="margin:0"><a href="{urls[5]}" style="display:inline-block;background:#155d7a;color:#fff;padding:11px 18px;border-radius:6px;text-decoration:none;font-weight:700" data-api-endpoint="/api/v1{urls[5]}" data-api-returntype="Assignment">Open {TITLES[5]}</a></p></section>'
    )
    return {
        1: {"TITLE": "Click Factor", "PURPOSE": "Use a supplied product brief to write, test, and revise a truthful call to action for one audience.", "TODAY": "<ul><li>compare five CTA approaches;</li><li>complete the workbook drafts and mock-up;</li><li>test the message;</li><li>revise and connect the work to a marketing career.</li></ul>", "READY": f'<p><strong>Start in FYF pp. 225-227 and 230.</strong> Use {link(files["CLICK"]["id"], "the two-page audience-test companion")} or <a href="{urls[1]}">the private annotation activity</a> for the evidence the workbook does not collect.</p>', "MEDIA": media([("p225", "Click Factor introduction with two ad examples"), ("p226", "Five CTA approaches and the Local Car Wash and Cooking Class prompts"), ("p227", "After-School Snack Box and Fishing Gear prompts"), ("p230", "Full-page ad mock-up requirements and planning space")]), "STEPS": step(1, "Compare the CTA approaches", "<p>Use only the product facts printed in FYF. Draft two different CTAs for each product.</p>") + step(2, "Build one ad", "<p>Complete the FYF mock-up with a headline, accurate description, CTA, clear hierarchy, and one access feature.</p>") + step(3, "Run the truth and three-second checks", "<p>Do not invent scarcity, discounts, popularity, testimonials, deadlines, or guarantees.</p>") + step(4, "Revise and connect", "<p>Keep the before and after. Name one marketing career, work product, and next use of the test evidence.</p>"), "EXIT": "<p>Name the career, work product, and revision that made the message clearer or more accurate.</p>", "DONE": "<ul><li>FYF work or complete no-workbook route;</li><li>audience-message chain;</li><li>truth/access check;</li><li>three-second test;</li><li>visible revision and career connection.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> audience/audiencia · accurate/exacto · benefit/beneficio · evidence/evidencia.</p><p><strong>Use this frame:</strong> This CTA fits <strong>[audience]</strong> because <strong>[supplied fact or need]</strong>. I changed <strong>[revision]</strong> so <strong>[audience effect]</strong>.</p>", "FALLBACK": "<p>The locked FYF pages plus the two-page companion are the complete no-workbook route. No real campaign, account, link, QR code, purchase, tracking, public post, H&amp;L, Xello, or design platform is required.</p>"},
        2: {"TITLE": "Written Communication and Changing Conditions", "PURPOSE": "Revise a clear fictional message and compare how two different conditions could change marketing work and preparation.", "TODAY": "<ul><li>complete and revise the Little Library message;</li><li>read current BLS evidence;</li><li>compare an economic condition with a societal or technology condition;</li><li>choose a preparation response.</li></ul>", "READY": f'<p><strong>Start in FYF pp. 147-148.</strong> Use {link(files["CHANGE"]["id"], "the two-page revision and changing-conditions companion")} for the evidence the workbook does not collect. The <a href="{urls[2]}">retryable practice Quiz</a> replaces the final five-minute check when your teacher assigns it.</p>', "MEDIA": media([("p147", "Written Communication Little Library scenario and brainstorm"), ("p148", "Four effective-writing moves and fictional social-message space")]), "STEPS": step(1, "Write for purpose and audience", "<p>State the fictional status, important detail, safe action, and one access need.</p>") + step(2, "Revise visibly", "<p>Record one clarity, privacy, or accessibility change.</p>") + step(3, "Read the career card", "<p>$76,950 May 2024 U.S. median; bachelor's typical; 7% projected growth, 2024-34; about 87,200 openings per year. These are not DFW starting pay or guarantees.</p>") + step(4, "Separate the conditions", "<p>Economic effects concern spending, budgets, demand, or hiring. Societal/technology effects concern audience behavior, tools, channels, access, or privacy.</p>"), "EXIT": "<p>Use the practice Quiz feedback or state one condition effect, one reason, and one preparation action.</p>", "DONE": "<ul><li>FYF message or complete no-workbook route;</li><li>visible revision;</li><li>bounded BLS conclusion;</li><li>two distinct condition effects;</li><li>preparation recommendation and career connection.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> purpose/propósito · budget/presupuesto · demand/demanda · channel/canal · privacy/privacidad.</p><p><strong>Use this frame:</strong> Economic pressure may change <strong>[work/hiring]</strong> because <strong>[evidence]</strong>. The societal or technology change instead requires <strong>[skill/action]</strong> because <strong>[reason]</strong>.</p>", "FALLBACK": "<p>The locked FYF pages plus the two-page companion are the complete route. Do not make a real post or enter real names, locations, handles, photos, or contact information. The Quiz is practice, not the only evidence.</p>"},
        3: {"TITLE": "Expert Edge", "PURPOSE": "Turn a skill into a fictional entrepreneurial opportunity while keeping responsibility, risk, and privacy visible.", "TODAY": "<ul><li>complete the FYF service plan;</li><li>define the opportunity;</li><li>name responsibility, risk, and control;</li><li>test, revise, and connect the plan to a marketing career.</li></ul>", "READY": f'<p><strong>Start in FYF pp. 222-224.</strong> Use {link(files["EXPERT"]["id"], "the two-page opportunity and revision companion")} or <a href="{urls[3]}">the private annotation activity</a> for the evidence the workbook does not collect.</p>', "MEDIA": media([("p222", "Expert Edge scenario and skill-to-need brainstorm"), ("p223", "Consulting service, mission, fictional price, and add-on plan"), ("p224", "Original logo, private pitch, feedback, and career discussion")]), "STEPS": step(1, "Build the FYF service", "<p>Connect a skill, audience, need, deliverable, mission, fictional unit/price, and add-on.</p>") + step(2, "Define the opportunity", "<p>Explain why the idea responds to a need rather than only naming a hobby or topic.</p>") + step(3, "Keep responsibility and risk visible", "<p>Name one owner responsibility, one uncertainty, and one control or boundary.</p>") + step(4, "Test and revise privately", "<p>Partner, teacher, or self-check. Oral delivery and logo polish are optional and not scored.</p>"), "EXIT": "<p>Explain why the idea is an opportunity and name one responsibility or risk control.</p>", "DONE": "<ul><li>FYF work or complete no-workbook route;</li><li>opportunity chain;</li><li>responsibility/risk/control;</li><li>private test and visible revision;</li><li>career/work-product connection.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> opportunity/oportunidad · deliverable/producto entregable · responsibility/responsabilidad · risk/riesgo.</p><p><strong>Use this frame:</strong> This is an opportunity because <strong>[audience]</strong> needs <strong>[deliverable]</strong>. The owner must <strong>[responsibility]</strong> and control <strong>[risk]</strong> by <strong>[action]</strong>.</p>", "FALLBACK": "<p>This is not a launch. No sale, payment, booking, contact, account, public promotion, client data, income promise, or copied mark is required. The locked pages and companion are the complete no-workbook route.</p>"},
        4: {"TITLE": "Family Fun Pass", "PURPOSE": "Use three evidence types to choose a strategy, explain a conflict, and plan the next test.", "TODAY": "<ul><li>read FYF p. 229, then p. 228;</li><li>name the campaign goal;</li><li>build a three-point evidence stack;</li><li>state a limitation, next test, and career connection.</li></ul>", "READY": f'<p><strong>Start with the data on FYF p. 229, then complete the decision work on p. 228.</strong> Use {link(files["FAMILY"]["id"], "the two-page evidence-decision companion")} or <a href="{urls[4]}">the private annotation activity</a> for the individual evidence the workbook does not collect.</p>', "MEDIA": media([("p229", "Family Fun Pass audience-preference and past-campaign tables with focus-group quotes"), ("p228", "Strategy choices, pitch space, and class-discussion prompts")]), "STEPS": step(1, "Set the goal first", "<p>Choose awareness, clicks, sales, trust, or broad age reach.</p>") + step(2, "Build an evidence stack", "<p>Use two exact numbers and one quote or pattern. State what each one supports.</p>") + step(3, "Resolve a conflict", "<p>Name the decision rule that makes one evidence type matter more for this goal.</p>") + step(4, "Keep uncertainty visible", "<p>Name one limit, one small next test, the result to measure, and the worker who would use it.</p>"), "EXIT": "<p>State the strategy, goal, strongest number, one limit, and one result to test next.</p>", "DONE": "<ul><li>FYF work or complete no-workbook route;</li><li>goal and three evidence points;</li><li>decision rule;</li><li>limitation and next test;</li><li>career/work-product connection.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> goal/meta · strategy/estrategia · measure/medida · evidence/evidencia · limitation/limitación.</p><p><strong>Use this frame:</strong> For the goal <strong>[goal]</strong>, I recommend <strong>[strategy]</strong> because <strong>[number]</strong> shows <strong>[meaning]</strong>. The limit is <strong>[limit]</strong>, so I would test <strong>[next result]</strong>.</p>", "FALLBACK": "<p>The locked FYF pages plus the two-page companion are the complete no-workbook route. The data are a fictional scenario, not a universal claim about age groups. No site, login, public pitch, or open-web research is required.</p>"},
        5: {"TITLE": "Ethical Marketing Evidence Brief", "PURPOSE": "Use the week's strongest evidence to explain an ethical marketing decision, entrepreneurial opportunity, career connection, and two different changing-condition effects.", "TODAY": "<ul><li>select evidence from the week;</li><li>complete four reasoning sections;</li><li>self-score with the 16-point rubric;</li><li>make one visible evidence-based revision.</li></ul>", "READY": f'<p>Open {link(files["BRIEF"]["id"], "the four-page Marketing Evidence Brief")} and {link(files["RUBRIC"]["id"], "the two-page Minor 3 rubric")}. Use completed FYF work and companions as evidence.</p>', "MEDIA": "", "STEPS": step(1, "Career, audience, and ethical message", "<p>Name the worker, work product, audience, message choice, boundary, and tested revision.</p>") + step(2, "Entrepreneurship and responsibility", "<p>State the opportunity, need, deliverable, responsibility, risk, control, and price limit.</p>") + step(3, "Data and changing conditions", "<p>Use two numbers and one quote/pattern, then keep economic and societal/technology effects distinct.</p>") + step(4, "Self-score and revise", "<p>Use all four criteria. Keep the original and changed evidence visible.</p>") + minor_panel, "EXIT": "<p>Name your strongest evidence, weakest criterion, and the revision that improved it.</p>", "DONE": "<ul><li>all four brief sections;</li><li>current source labels;</li><li>economic and societal/technology effects kept distinct;</li><li>16-point self-score;</li><li>visible revision and private submission.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> synthesis/síntesis · opportunity/oportunidad · strategy/estrategia · source/fuente · revise/revisar.</p><p><strong>Use this frame:</strong> My evidence supports <strong>[decision]</strong> because <strong>[number, quote, or test]</strong>. I revised <strong>[part]</strong> after checking <strong>[criterion]</strong>.</p>", "FALLBACK": "<p>The four-page brief includes recap prompts. Accept typing, dictation, annotation, enlarged print, or paper. No live/public pitch, H&amp;L favorite, Xello completion, eDynamic progress, real campaign, or personal business disclosure is required.</p>"},
    }


def teacher_content(files):
    link, flow = common.file_link, common.flow
    color = "#9a4d19"
    sources = '<p><a href="https://www.bls.gov/ooh/business-and-financial/market-research-analysts.htm">BLS Market Research Analysts and Marketing Specialists</a> · <a href="https://www.ftc.gov/business-guidance/advertising-marketing">FTC Advertising and Marketing</a> · <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte/macarthur-high-school">Irving ISD MacArthur High School CTE</a>.</p>'
    support = '<p>Each companion is one front-and-back sheet. Stable facts and the worked example are prefilled. Labels use short fields; reasons and comparisons receive 2-3 full-width lines; the final brief separates every sentence job. Point-of-use word banks and complete frames support the exact language function. Accept typing, dictation, annotation, enlarged print, or paper, and score evidence rather than English mechanics unless meaning is unclear.</p>'
    fallback = '<p>FYF is the default student work surface on Days 1-4. Locked workbook images plus the companion form the complete no-workbook route; students do not complete both routes twice. H&amp;L, Xello School Subjects at Work, eDynamic 4.1, Canva, Adobe Express, a public Discussion, real posting/sale/contact/payment, personal data, testimonials, tracking, and copied marks are not required.</p>'
    return {
        1: {"TITLE": "Click Factor", "SUBTITLE": "50 minutes · FYF pp. 225-227 and 230", "ALERT": "<strong>Truth boundary:</strong> supplied product facts only. Students do not invent urgency, scarcity, discounts, popularity, testimonials, deadlines, or guarantees.", "PREP": f'<ul><li>Have students open FYF pp. 225-227 and 230.</li><li>Post {link(files["CLICK"]["id"], "the two-page audience-test companion")} as Canvas-first with print fallback and the private annotation route.</li><li>Prepare one truthful CTA model and one unsupported contrast.</li></ul>', "EVIDENCE": "<p>Collect the FYF work plus individual audience-message chain, truth/access check, three-second test, visible revision, and marketing career/work-product connection.</p>", "FLOW": flow(color, "Audience/action warm-up · 5", "Identify what an ad asks a viewer to do.") + flow("#4c8b38", "Read and model · 8", "Contrast truthful audience fit with invented urgency.") + flow("#155d7a", "Draft and compare · 12", "Students write two CTA types for each FYF product.") + flow("#d39b22", "Build the FYF ad · 15", "Use p. 230; digital routes are optional and equal.") + flow("#155d7a", "Test and revise · 5", "Run the three-second check and keep before/after evidence.") + flow(color, "Exit · 5", "Career, work product, and revision."), "MONITOR": "<p><strong>Active-monitoring target:</strong> audience + supplied fact + clear next action. If several students add an unverified superlative or fake deadline, pause and repair that claim before design work continues. Strong revisions respond to test evidence, not decoration preference. Trim a second digital build or partner share first; preserve the individual test and revision.</p>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        2: {"TITLE": "Written Communication and Changing Conditions", "SUBTITLE": "50 minutes · FYF pp. 147-148 + practice Quiz", "ALERT": "<strong>Fictional message:</strong> no real account, name, location, handle, photo, hashtag needed for meaning, or contact information. The Quiz replaces the last five-minute check when used.", "PREP": f'<ul><li>Have students open FYF pp. 147-148.</li><li>Post {link(files["CHANGE"]["id"], "the two-page revision and conditions companion")} as Canvas-first with print fallback.</li><li>Open the retryable practice Quiz and one revised-message model.</li></ul>', "EVIDENCE": "<p>Collect the FYF message plus visible revision, bounded BLS conclusion, distinct economic and societal/technology effects, preparation recommendation, and marketing career connection. Quiz clicks alone are not the DOL.</p>", "FLOW": flow(color, "Clear-message warm-up · 5", "Compare a vague notice with a specific audience-ready notice.") + flow("#4c8b38", "Read four writing moves · 7", "Purpose, audience, important detail, and safe action.") + flow("#155d7a", "Draft and revise · 13", "Complete FYF and record one clarity, privacy, or access change.") + flow("#d39b22", "Read current evidence · 8", "Keep occupation, measure, date, geography, and limitation visible.") + flow("#155d7a", "Compare conditions · 12", "Separate economic pressure from societal or technology change.") + flow(color, "Practice Quiz/exit · 5", "Immediate misconception feedback or equivalent oral/written check."), "MONITOR": "<p><strong>Key:</strong> economic effects concern spending, budgets, demand, or hiring; societal/technology effects concern behavior, tools, channels, access, privacy, accuracy, copyright, or human review. The BLS figure is a May 2024 U.S. median, not DFW starting pay. If students blend both changes into generic 'technology makes jobs grow,' return them to the exact scenario evidence. Trim message decoration first.</p>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        3: {"TITLE": "Expert Edge", "SUBTITLE": "50 minutes · FYF pp. 222-224", "ALERT": "<strong>Classroom plan only:</strong> no sale, payment, booking, contact, account, client data, public promotion, income promise, or copied identity.", "PREP": f'<ul><li>Have students open FYF pp. 222-224.</li><li>Post {link(files["EXPERT"]["id"], "the two-page opportunity and revision companion")} as Canvas-first with print fallback and the private annotation route.</li><li>Prepare one completed opportunity-responsibility-risk model.</li></ul>', "EVIDENCE": "<p>Collect the FYF service plan plus individual opportunity chain, responsibility/risk/control, private test, visible revision, and marketing career/work-product connection.</p>", "FLOW": flow(color, "Skill-to-need warm-up · 5", "Name a skill, audience need, and useful deliverable.") + flow("#4c8b38", "Define entrepreneurship · 7", "Opportunity, resources, decisions, responsibility, and risk.") + flow("#155d7a", "Build the FYF service · 18", "Audience, need, deliverable, mission, fictional unit/price, and add-on.") + flow("#d39b22", "Responsibility and original mark · 8", "Record risk/control in the companion and sketch on FYF p. 224.") + flow("#155d7a", "Private test and revision · 7", "Partner, teacher, or self-check; oral delivery is optional.") + flow(color, "Exit · 5", "Opportunity plus one responsibility or risk control."), "MONITOR": "<p>A hobby/topic is not yet a deliverable. A fictional price needs a unit and remains classroom reasoning, not an income promise. Responsibility is an owner action; risk is an uncertainty; control is the response. If students jump directly to logo design, redirect to audience + need + deliverable. Trim logo polish or oral sharing first.</p>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        4: {"TITLE": "Family Fun Pass", "SUBTITLE": "50 minutes · FYF p. 229, then p. 228", "ALERT": "<strong>Fictional workbook data:</strong> preference, performance, and focus-group evidence support a classroom decision; they do not prove universal age-group behavior.", "PREP": f'<ul><li>Have students open FYF p. 229, then p. 228.</li><li>Post {link(files["FAMILY"]["id"], "the two-page landscape evidence-decision companion")} as Canvas-first with print fallback and the private annotation route.</li><li>Project the stated-goal example before students choose a strategy.</li></ul>', "EVIDENCE": "<p>Collect the FYF decision plus individual goal, two numbers and one quote/pattern, decision rule, limitation, next test, exact result to measure, and marketing career/work-product connection.</p>", "FLOW": flow(color, "Goal-before-metric warm-up · 5", "Choose awareness, clicks, sales, trust, or broad age reach.") + flow("#4c8b38", "Read three evidence types · 8", "Preferences, past performance, and quotes answer different questions.") + flow("#155d7a", "Compare strategies · 12", "Use two values/quotes for each FYF strategy.") + flow("#d39b22", "Choose and defend · 12", "Build a three-point evidence stack tied to the goal.") + flow("#155d7a", "Conflict and next test · 8", "State a decision rule, limitation, and exact result to measure.") + flow(color, "Exit · 5", "Strategy, goal, strongest number, limit, and next result."), "MONITOR": "<p>There is no single best strategy until the goal is named. In the supplied past-campaign table, Influencer has the most sales and Social has the most clicks; in-store and email are stronger in the 50+ preference row. Quotes add explanation but do not predict results. Score evidence and reasoning, not preference. Trim a third strategy detail first; preserve the decision, limitation, and test.</p>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        5: {"TITLE": "Ethical Marketing Evidence Brief", "SUBTITLE": "50 minutes · Minor 3", "ALERT": "<strong>Minor 3:</strong> private four-page brief, 16-point advisory rubric, and visible evidence-based revision. Keep unpublished for teacher transfer.", "PREP": f'<ul><li>Post {link(files["BRIEF"]["id"], "the four-page Marketing Evidence Brief")}, {link(files["RUBRIC"]["id"], "the two-page Minor 3 rubric")}, and the private Minor 3 Assignment.</li><li>Have Days 1-4 FYF work and companions available for reference.</li><li>Do not require a public pitch or supplemental platform completion.</li></ul>', "EVIDENCE": "<p>Score audience/communication, entrepreneurship reasoning, data-informed decision, and career/changing-conditions evidence. Require the self-score and one visible revision. Graphic polish, platform access, public speaking, personal business experience, and English mechanics unless meaning is unclear do not determine the score.</p>", "FLOW": flow(color, "Evidence inventory · 5", "Select Click Factor, Expert Edge, Family Fun Pass, and changing-condition evidence.") + flow("#4c8b38", "Career and audience · 8", "Worker, work product, audience, message, boundary, and tested revision.") + flow("#155d7a", "Entrepreneurship · 10", "Opportunity, deliverable, responsibility, risk, control, and price limit.") + flow("#d39b22", "Data and conditions · 12", "Two numbers, quote/pattern, decision, limit, test, and two distinct effects.") + flow("#155d7a", "Self-score and revise · 10", "Use all four criteria and keep the change visible.") + flow(color, "Submit · 5", "Private Canvas or teacher-approved paper route."), "MONITOR": "<p>The brief must make reasoning visible; platform clicks or artwork alone are not mastery evidence. Economic and societal/technology effects remain distinct. Source labels keep occupation, measure, date, geography, and limitation together. If a student is missing earlier work, use the brief's recap prompts rather than assigning every old packet again. Trim optional polish or oral sharing first; preserve self-score and revision.</p>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
    }


async def lock_every_file_in_folder(client, folder):
    records = await common.paged(client, f"/folders/{folder['id']}/files")
    locked = []
    for record in records:
        if not record.get("locked"):
            record = await common.api(client, "PUT", f"/files/{record['id']}", data={"locked": "true"})
        locked.append(record)
    return locked


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        # Validate the weighted object before the first Canvas mutation.
        await mapped_minor_assignment(client)
        module = await ensure_module(client)
        path = "course files/CCR Materials/6SW/Wk3"
        folder = await common.ensure_folder(client, path)
        names = {
            "CLICK": "6sw-wk3-click-factor-campaign.pdf",
            "CHANGE": "6sw-wk3-written-communication-and-change.pdf",
            "EXPERT": "6sw-wk3-expert-edge-plan.pdf",
            "FAMILY": "6sw-wk3-family-fun-pass-analysis.pdf",
            "BRIEF": "6sw-wk3-marketing-evidence-brief.pdf",
            "RUBRIC": "6sw-wk3-marketing-evidence-rubric.pdf",
        }
        files = {key: await common.upload(client, ROOT / "docs/resources/worksheets" / name, path) for key, name in names.items()}
        visual_path = "course files/CCR Materials/6SW/Wk3/Locked Licensed Visuals"
        visual_folder = await common.ensure_folder(client, visual_path)
        pageset = [147, 148, 222, 223, 224, 225, 226, 227, 228, 229, 230]
        visuals = {f"p{page}": await common.upload(client, ASSETS / f"fyf-p{page}.jpg", visual_path) for page in pageset}
        quiz = await upsert_quiz(client)
        assignments = {}
        for day, key in {1: "CLICK", 3: "EXPERT", 4: "FAMILY"}.items():
            assignments[day] = await common.upsert_assignment(client, TITLES[day], "<p>Complete privately by annotation, upload, typed labeled responses, or paper. Use the FYF workbook first and one companion route, not every route.</p>", ["student_annotation", "online_upload", "online_text_entry"], files[key]["id"])
        evidence_links = (
            f'<p>Submit {common.file_link(files["BRIEF"]["id"], "the private four-page Marketing Evidence Brief")} and '
            f'{common.file_link(files["RUBRIC"]["id"], "the visible 16-point self-score and revision record")}. '
            'Use prior FYF work and companions as evidence; do not submit a public post or supplemental platform screenshot. '
            'Audience fit, ethical communication, entrepreneurship reasoning, data use, source labels, career connection, and revision are scored. '
            'Graphic polish, platform access, public speaking, personal business experience, and English mechanics unless meaning is unclear do not determine the score.</p>'
        )
        assignments[5] = await require_minor_assignment(client, evidence_links)
        urls = {day: f"/courses/{COURSE_ID}/assignments/{assignment['id']}" for day, assignment in assignments.items()}
        urls[2] = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        students = student_content(files, visuals, urls)
        teachers = teacher_content(files)
        labels = {1: "Click Factor", 2: "Written Communication and Changing Conditions", 3: "Expert Edge", 4: "Family Fun Pass", 5: "Ethical Marketing Evidence Brief"}
        interactions = {1: ("Assignment", assignments[1]["id"], TITLES[1]), 2: ("Quiz", quiz["id"], TITLES[2]), 3: ("Assignment", assignments[3]["id"], TITLES[3]), 4: ("Assignment", assignments[4]["id"], TITLES[4]), 5: ("Assignment", assignments[5]["id"], TITLES[5])}
        order, pages = [], {}
        for day in range(1, 6):
            header_title = f"Day {day} · {labels[day]}"
            header = await prior.upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 6SW Wk3 Day {day} - {labels[day]}"
            student_page = await common.upsert_page(client, student_title, common.render("6sw-wk3-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, **CONTRACTS[day], **students[day]}))
            teacher_title = f"TEACHER: 6SW Wk3 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(client, teacher_title, common.render("6sw-wk3-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **CONTRACTS[day], **teachers[day]}))
            await prior.upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await prior.upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            kind, key, title = interactions[day]
            await prior.upsert_item(client, module["id"], kind, key, title)
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title), (kind, key, title)]
            pages[day] = {"teacher": teacher_page, "student": student_page}

        def matches_item(entry, kind, key):
            return entry.get("type") == kind and ((kind == "SubHeader" and entry.get("id") == key) or (kind == "Page" and entry.get("page_url") == key) or (kind in ("Assignment", "Quiz") and entry.get("content_id") == key))

        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        keep_ids = set()
        for kind, key, _title in order:
            match = next((entry for entry in items if entry["id"] not in keep_ids and matches_item(entry, kind, key)), None)
            if not match:
                raise RuntimeError(f"Missing expected Marketing module item: {kind} {key}")
            keep_ids.add(match["id"])
        for entry in items:
            if entry["id"] not in keep_ids:
                await common.api(client, "DELETE", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{entry['id']}")
        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(entry for entry in items if matches_item(entry, kind, key))
            await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}", data={"module_item[position]": position, "module_item[title]": title})
        final = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        ordered = sorted(final, key=lambda entry: entry.get("position", 0))
        if len(ordered) != len(order):
            raise RuntimeError(f"Expected {len(order)} Marketing module items; found {len(ordered)}")
        for position, ((kind, key, _title), entry) in enumerate(zip(order, ordered), 1):
            if entry.get("position") != position or not matches_item(entry, kind, key):
                raise RuntimeError(f"Marketing module order mismatch at position {position}")

        folder_files = await lock_every_file_in_folder(client, folder)
        visual_files = await lock_every_file_in_folder(client, visual_folder)
        folder = await common.api(client, "GET", f"/folders/{folder['id']}")
        visual_folder = await common.api(client, "GET", f"/folders/{visual_folder['id']}")
        if not folder.get("locked") or not visual_folder.get("locked") or any(not record.get("locked") for record in folder_files + visual_files):
            raise RuntimeError("Every Marketing support folder and file must remain locked")
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        print(json.dumps({"module": {"id": module["id"], "published": module["published"]}, "folder": {"id": folder["id"], "locked": folder["locked"]}, "visual_folder": {"id": visual_folder["id"], "locked": visual_folder["locked"]}, "files": {key: record["id"] for key, record in files.items()}, "visuals": {key: record["id"] for key, record in visuals.items()}, "quiz": {"id": quiz["id"], "published": quiz.get("published")}, "assignments": {str(day): {"id": assignment["id"], "published": assignment.get("published"), "points": assignment.get("points_possible"), "grading_type": assignment.get("grading_type"), "omit_from_final_grade": assignment.get("omit_from_final_grade")} for day, assignment in assignments.items()}, "pages": {str(day): {kind: {"url": page["url"], "published": page["published"]} for kind, page in pair.items()} for day, pair in pages.items()}, "items": [{"position": entry["position"], "type": entry["type"], "title": entry["title"]} for entry in ordered]}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
