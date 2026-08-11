"""Build the unpublished 6SW Week 4 sales and oral-evidence module."""

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
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/6sw/wk4"
MODULE_NAME = "6SW Wk4: Sales and Career Oral Evidence"
TITLES = {
    1: "PRACTICE: Audience and Sales Pitch Plan",
    2: "PRACTICE: Oral Pitch Delivery and Revision",
    3: "PRACTICE: BrainBoost Decision and Career Outline",
    4: "PRACTICE: Interview Appearance and Rehearsal",
    5: "FORMATIVE: Career Oral Evidence Brief",
}

CONTRACTS = {
    1: {
        "TOPIC": "Audience and Message",
        "OBJECTIVE": "Students will identify a sales or marketing career opportunity and use FYF pitch evidence to plan an accurate audience-specific hook, offer, benefit, and call to action.",
        "TEKS": "d(1)(C), d(4)(B)",
        "DOL": "Completed FYF 30 Seconds to Sell work plus a two-page individual audience/assumption check, ethical boundary, career/work-product connection, and selected oral route.",
        "I_CAN": "identify a sales or marketing career and use FYF evidence to plan an accurate pitch for a specific audience.",
        "SHOW": "Complete FYF 30 Seconds to Sell and the two-page companion with an audience/fact/assumption check, ethical boundary, career connection, and selected oral route.",
    },
    2: {
        "TOPIC": "Oral Revision",
        "OBJECTIVE": "Students will communicate an audience-specific pitch twice, use feedback to make one visible revision, and explain how the communication skill transfers to a second career.",
        "TEKS": "d(4)(B)",
        "DOL": "Two timed oral/AAC pitch attempts, one specific feedback point, a visible before/after revision, and a two-career transfer response.",
        "I_CAN": "deliver a short pitch twice, use specific feedback to revise it, and explain how the same communication skill works in another career.",
        "SHOW": "Record two timed oral/AAC attempts, specific feedback, a visible before/after revision, evidence of its effect, and a two-career transfer response.",
    },
    3: {
        "TOPIC": "Problem Solving",
        "OBJECTIVE": "Students will identify how a sales, marketing, or design career uses evidence to define a campaign problem, screen solutions, and organize a bounded career brief.",
        "TEKS": "d(1)(C), d(4)(B)",
        "DOL": "Completed FYF BrainBoost work plus a two-page individual cause statement, evidence-linked decision, fixed-source career outline, and cross-career problem-solving connection.",
        "I_CAN": "use campaign evidence to separate a cause from a result, choose a bounded solution, and connect the problem-solving move to two careers.",
        "SHOW": "Complete FYF BrainBoost and the two-page companion with a cause/evidence decision, rejected unsupported claim, career outline, and cross-career connection.",
    },
    4: {
        "TOPIC": "Interview Appearance",
        "OBJECTIVE": "Students will describe context-appropriate interview appearance across office, task-demonstration, and virtual settings, then rehearse a career brief twice using an appropriate private recording, Canvas evidence card, teacher-approved visual, or AAC technology route.",
        "TEKS": "d(6)(B), d(4)(C)",
        "DOL": "Three context decisions with verification questions, retryable practice Quiz feedback, two timed oral/AAC career rehearsals using one appropriate technology choice, and one visible revision.",
        "I_CAN": "choose interview preparation for the workplace, task, safety needs, format, and accommodation, then use appropriate technology to rehearse and revise my career brief.",
        "SHOW": "Complete three context decisions, review Quiz feedback, and record two timed oral/AAC rehearsals using one appropriate technology choice and one visible revision.",
    },
    5: {
        "TOPIC": "Career Oral Evidence",
        "OBJECTIVE": "Students will deliver a 60-90-second oral/AAC career brief using an appropriate private recording, Canvas evidence card, teacher-approved visual, or AAC technology route, with one duty, preparation evidence, a correctly labeled labor figure, and a bounded conclusion.",
        "TEKS": "d(1)(C), d(4)(B), d(4)(C)",
        "DOL": "Private 60-90-second oral/AAC career brief with one appropriate technology choice, two-page delivery record, two-career transfer reflection, 16-point self-score, and one visible revision note.",
        "I_CAN": "use appropriate technology to deliver a concise career brief with accurate source labels and explain how one communication skill works in two careers.",
        "SHOW": "Submit the private 60-90-second oral/AAC brief using one appropriate technology choice, two-page evidence record, two-career transfer reflection, self-score, and visible revision note.",
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


QUESTIONS = [
    (
        "Q1 - appearance context",
        "Which rule works across different interview settings?",
        "Prepare for the workplace, task, safety needs, format, and accommodations; choose clean, functional, role-aware clothing.",
        ["Every interview requires a suit.", "Expensive clothing earns a higher score.", "One gendered list works for everyone."],
        "Correct. Context and safety come before fashion rules.",
        "Appearance guidance is not universal, expensive, or gendered.",
    ),
    (
        "Q2 - skilled trade",
        "What should a student do before bringing or using tools or PPE for an interview task?",
        "Confirm the employer or site instructions and required safety route.",
        ["Bring any tools from home.", "Wear fashion footwear instead of safety gear.", "Assume every site uses the same PPE."],
        "Correct. Site and task requirements must be confirmed.",
        "PPE and tool rules are specific to the task and site.",
    ),
    (
        "Q3 - virtual",
        "Which preparation best supports a virtual interview?",
        "Test audio, lighting, background and privacy, notifications, and a backup connection route.",
        ["Require a camera regardless of access needs.", "Open every app during the interview.", "Share the meeting link publicly."],
        "Correct. Technology, privacy, and backup planning matter.",
        "Camera use is not always required, and privacy still applies.",
    ),
    (
        "Q4 - salary label",
        "Which label is accurate for the fixed Sales Managers figure?",
        "$138,060 May 2024 U.S. median; not DFW starting pay or a guarantee.",
        ["Guaranteed DFW entry salary", "The pay for every salesperson", "A live job opening"],
        "Correct. Measure, date, geography, and limitation stay visible.",
        "A national median is not local starting pay, a vacancy, or a personal outcome.",
    ),
    (
        "Q5 - oral route",
        "Which route can demonstrate the oral-presentation standard?",
        "A live, teacher-conference, recorded audio/video, or AAC brief with assessable oral or communicated evidence.",
        ["A written outline alone with no authorized accommodation", "A H&L favorite", "A public Discussion post"],
        "Correct. Several private oral and AAC routes can show the same evidence.",
        "Written planning supports oral evidence but is not automatically the same standard.",
    ),
]


async def upsert_quiz(client):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    matches = [quiz for quiz in quizzes if quiz.get("title") == TITLES[4]]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one {TITLES[4]!r} Quiz; found {len(matches)}")
    data = {
        "quiz[title]": TITLES[4],
        "quiz[description]": "<p>Ungraded, unlimited-retry practice on appearance context, safety, virtual readiness, source labels, and equivalent oral routes.</p>",
        "quiz[quiz_type]": "practice_quiz",
        "quiz[published]": "false",
        "quiz[allowed_attempts]": "-1",
        "quiz[show_correct_answers]": "true",
        "quiz[shuffle_answers]": "false",
    }
    quiz = await common.api(
        client,
        "PUT" if matches else "POST",
        f"/courses/{COURSE_ID}/quizzes/{matches[0]['id']}" if matches else f"/courses/{COURSE_ID}/quizzes",
        data=data,
    )
    existing = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    desired_names = {name for name, *_rest in QUESTIONS}
    for question in existing:
        if question.get("question_name") not in desired_names:
            await common.api(client, "DELETE", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{question['id']}")
    existing = [question for question in existing if question.get("question_name") in desired_names]
    seen = set()
    for question in existing:
        name = question.get("question_name")
        if name in seen:
            await common.api(client, "DELETE", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{question['id']}")
        else:
            seen.add(name)
    for position, (name, prompt, correct, wrong, yes, no) in enumerate(QUESTIONS, 1):
        old = next((question for question in existing if question.get("question_name") == name), None)
        payload = {
            "question": {
                "question_name": name,
                "question_text": prompt,
                "question_type": "multiple_choice_question",
                "position": position,
                "points_possible": 1,
                "correct_comments": yes,
                "incorrect_comments": no,
                "answers": [{"answer_text": correct, "answer_weight": 100}]
                + [{"answer_text": answer, "answer_weight": 0} for answer in wrong],
            }
        }
        path = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{old['id']}" if old else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        await common.api(client, "PUT" if old else "POST", path, json=payload)
    expected = [name for name, *_rest in QUESTIONS]
    final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    by_name = {question.get("question_name"): question for question in final_questions}
    if set(by_name) != set(expected) or len(final_questions) != len(expected):
        raise RuntimeError("Sales practice Quiz question set mismatch")
    fields = []
    for name in expected:
        fields.extend([("order[][id]", str(by_name[name]["id"])), ("order[][type]", "question")])
    await common.api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/reorder",
        content=urlencode(fields),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    if [question.get("question_name") for question in final_questions] != expected:
        raise RuntimeError("Sales practice Quiz order mismatch")
    return await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


def student_content(files, visuals, urls):
    link, step = common.file_link, common.step
    media = lambda pairs: '<h3 style="color:#245f69;border-bottom:3px solid #b9d9de">Licensed workbook pages</h3>' + "".join(prior.image_tag(visuals[key]["id"], alt) for key, alt in pairs)
    submission_panel = (
        f'<section data-cce-marker="{SUBMISSION_LINK_MARKER}" '
        'style="border:2px solid #245f69;border-radius:12px;padding:18px 20px;margin:24px 0;background:#f4fafb">'
        '<h3 style="margin:0 0 8px;color:#245f69">Submit your formative oral evidence</h3>'
        '<p style="margin:0 0 14px">Use the rubric to check your work. Submit the private oral/AAC evidence plus the two-page record and self-score through this Canvas assignment. Earlier FYF work and companions stay available as reference evidence.</p>'
        f'<p style="margin:0"><a href="{urls[5]}" style="display:inline-block;background:#245f69;color:#fff;padding:11px 18px;border-radius:6px;text-decoration:none;font-weight:700" data-api-endpoint="/api/v1{urls[5]}" data-api-returntype="Assignment">Open {TITLES[5]}</a></p></section>'
    )
    return {
        1: {
            "TITLE": "Audience and Sales Pitch Plan",
            "PURPOSE": "Use FYF evidence to plan a short fictional pitch for a specific audience without inventing claims.",
            "TODAY": "<ul><li>label the four pitch parts;</li><li>choose a fictional offer and audience;</li><li>complete the FYF plan and draft;</li><li>check accuracy and connect the work to a career.</li></ul>",
            "READY": f'<p><strong>Start in FYF pp. 241-243.</strong> Use {link(files["PLAN"]["id"], "the two-page audience and accuracy companion")} or <a href="{urls[1]}">the private annotation activity</a> for the evidence the workbook does not collect. Do not complete both work routes.</p>',
            "MEDIA": media([("p241", "30 Seconds to Sell pitch anatomy and SparkClean worked example"), ("p242", "Offer, audience, and four-part pitch planner"), ("p243", "Full pitch, practice, feedback, and discussion prompts")]),
            "STEPS": step(1, "Label the model", "<p>Find the hook, clear offer, audience benefit, and call to action. Mark any claim that would need verification.</p>") + step(2, "Choose the fictional offer and audience", "<p>Complete FYF Steps 2-3. Separate a supplied fact or logical reason from an audience assumption.</p>") + step(3, "Plan and write", "<p>Complete FYF Steps 4-5. Use benefits, not only features; keep the language accurate.</p>") + step(4, "Add the companion evidence", "<p>Record the ethical boundary, career/work product, transferable skill, and Day 2 oral route.</p>"),
            "EXIT": "<p>Name the career, work product, and one claim or assumption you kept bounded.</p>",
            "DONE": "<ul><li>FYF pitch or no-workbook route;</li><li>audience/fact/assumption check;</li><li>accuracy and privacy boundary;</li><li>career and transfer evidence;</li><li>selected oral route.</li></ul>",
            "SUPPORT": "<p><strong>Word bank:</strong> audience/audiencia · benefit/beneficio · evidence/evidencia · assumption/suposicion · accurate/exacto.</p><p><strong>Use this frame:</strong> The benefit fits <strong>[audience]</strong> because <strong>[fact or reason]</strong>. I should not assume <strong>[assumption]</strong>.</p>",
            "FALLBACK": "<p>The locked FYF images plus the two-page companion are the complete no-workbook route. No real sale, public post, link, payment, customer, account, H&amp;L, Xello, eDynamic, or design platform is required.</p>",
        },
        2: {
            "TITLE": "Deliver, Test, and Revise",
            "PURPOSE": "Deliver the FYF pitch twice through a private oral/AAC route and make one specific revision between attempts.",
            "TODAY": "<ul><li>check the pitch boundary;</li><li>deliver once;</li><li>collect specific feedback;</li><li>revise, deliver again, and transfer the skill.</li></ul>",
            "READY": f'<p><strong>Use your FYF pp. 241-243 pitch.</strong> Open {link(files["DELIVERY"]["id"], "the two-page delivery and revision record")} and <a href="{urls[2]}">the private media/annotation activity</a>.</p>',
            "MEDIA": media([("p243", "Practice, partner/small-group/class options, feedback record, and discussion")]),
            "STEPS": step(1, "Check the boundary", "<p>Remove unsupported urgency, guarantees, health, popularity, scarcity, or income claims.</p>") + step(2, "Deliver once", "<p>Use the route your teacher assigned: live partner/small group, teacher conference, private recording, or AAC. Keep it at 60 seconds or less.</p>") + step(3, "Get specific feedback", "<p>Name an exact word, sentence, pause, or organization choice to revise.</p>") + step(4, "Revise and deliver again", "<p>Keep the before/after language visible, record the time and effect, then compare how the skill works in two careers.</p>"),
            "EXIT": "<p>State the revision that changed clarity, accuracy, organization, or delivery/AAC output.</p>",
            "DONE": "<ul><li>two timed oral/AAC attempts;</li><li>specific feedback;</li><li>visible revision;</li><li>evidence of its effect;</li><li>two-career transfer response.</li></ul>",
            "SUPPORT": "<p><strong>Word bank:</strong> pace/ritmo · clear/claro · specific/especifico · revise/revisar · feedback/retroalimentacion.</p><p><strong>Use this frame:</strong> I changed <strong>[exact part]</strong> because the audience needs <strong>[clearer meaning or action]</strong>.</p>",
            "FALLBACK": "<p>Partner attendance and camera use are not required. Use a teacher conference, private recording, or AAC make-up. A written outline supports oral evidence but does not automatically replace it.</p>",
        },
        3: {
            "TITLE": "BrainBoost Decision and Career Outline",
            "PURPOSE": "Use FYF campaign evidence to separate a cause from a result, choose a bounded solution, and organize career evidence.",
            "TODAY": "<ul><li>analyze the supplied campaign;</li><li>generate and screen solutions;</li><li>complete the FYF campaign plan;</li><li>record individual problem-solving and career evidence.</li></ul>",
            "READY": f'<p><strong>Start in FYF pp. 244-247.</strong> Use {link(files["BRAIN"]["id"], "the two-page individual decision and career-outline companion")} or <a href="{urls[3]}">the private annotation activity</a> for the evidence the workbook does not collect.</p>',
            "MEDIA": media([("p244", "BrainBoost scenario and email evidence"), ("p245", "Social and in-store evidence, customer feedback, and problem statement"), ("p246", "Solution brainstorm and three-idea screening table"), ("p247", "Mini campaign plan, share and reflection prompts")]),
            "STEPS": step(1, "Find the cause", "<p>The campaign reached the stated audience. Low sales are the result; use the customer comments to name a possible message or value cause.</p>") + step(2, "Generate and screen", "<p>Complete FYF p. 246. Reject any solution that invents a health, nutrition, discount, scarcity, popularity, testimonial, or data claim.</p>") + step(3, "Build the FYF campaign plan", "<p>Complete p. 247, then record your own cause/evidence decision and cross-career problem-solving connection.</p>") + step(4, "Outline the career brief", "<p>Use one fixed BLS card or previously verified evidence. Keep the occupation, duty, preparation, measure, date, geography, and limitation together.</p>"),
            "EXIT": "<p>State the result, possible cause, evidence, and the next evidence step in a second career.</p>",
            "DONE": "<ul><li>FYF/no-workbook BrainBoost work;</li><li>individual cause and evidence decision;</li><li>rejected unsupported claim;</li><li>two-career transfer;</li><li>complete oral outline.</li></ul>",
            "SUPPORT": "<p><strong>Word bank:</strong> result/resultado · cause/causa · evidence/evidencia · screen/evaluar · limitation/limitacion.</p><p><strong>Use this frame:</strong> The result is <strong>[result]</strong>, but <strong>[evidence]</strong> suggests the cause may be <strong>[cause]</strong>. A <strong>[second career]</strong> would next check <strong>[evidence]</strong>.</p>",
            "FALLBACK": "<p>The locked FYF images plus the two-page companion are the complete no-workbook route. The fixed career cards remove the need for H&amp;L, prior portfolio work, or open-web research.</p>",
        },
        4: {
            "TITLE": "Interview Appearance and Rehearsal",
            "PURPOSE": "Choose interview preparation for the actual context, then rehearse and revise your career brief.",
            "TODAY": "<ul><li>compare office, task-demonstration, and virtual contexts;</li><li>complete a retryable Quiz;</li><li>rehearse once;</li><li>revise and rehearse again.</li></ul>",
            "READY": f'<p>Open {link(files["APPEAR"]["id"], "the two-page landscape appearance and rehearsal companion")} and <a href="{urls[4]}">the retryable practice Quiz</a>.</p>',
            "MEDIA": "",
            "STEPS": step(1, "Use the context", "<p>Base the choice on workplace, task, safety, format, and accommodation--not cost, body, gender, culture, religion, or disability.</p>") + step(2, "Make three decisions", "<p>Choose and explain preparation for an office/customer-facing interview, a skilled-trade task demonstration, and a virtual interview. Write one respectful question to verify for each.</p>") + step(3, "Use Quiz feedback", "<p>Check safety, source labels, virtual readiness, and the oral-route boundary. Retry after reading the feedback.</p>") + step(4, "Rehearse twice", "<p>Use a live, conference, private recording, or AAC route. Keep the revision visible between attempts.</p>"),
            "EXIT": "<p>Name one final content check and one final delivery/AAC check.</p>",
            "DONE": "<ul><li>three context decisions and questions;</li><li>access/safety reasoning;</li><li>Quiz feedback reviewed;</li><li>two timed oral/AAC career rehearsals;</li><li>one appropriate technology choice;</li><li>visible revision.</li></ul>",
            "SUPPORT": "<p><strong>Word bank:</strong> workplace/lugar de trabajo · task/tarea · safety/seguridad · accommodation/adaptacion · verify/verificar.</p><p><strong>Use this frame:</strong> For <strong>[context]</strong>, I would choose <strong>[functional choice]</strong> because <strong>[task, safety, or access reason]</strong>. I would verify <strong>[question]</strong>.</p>",
            "FALLBACK": "<p>No clothing modeling or personal body, cost, culture, religion, disability, or gender disclosure. Use a private rehearsal route. If video or bandwidth fails, use audio, phone, AAC, or an approved reschedule.</p>",
        },
        5: {
            "TITLE": "Career Oral Evidence Brief",
            "PURPOSE": "Deliver a concise career brief with accurate source labels, then use the feedback profile to plan one visible revision.",
            "TODAY": "<ul><li>run the final source and content check;</li><li>deliver 60-90 seconds through your assigned oral/AAC route;</li><li>record transfer evidence;</li><li>self-score and revise.</li></ul>",
            "READY": f'<p>Open {link(files["ORAL"]["id"], "the two-page Career Oral Evidence Brief")}, {link(files["RUBRIC"]["id"], "the two-page formative feedback profile")}, and the private submission below. Use your Day 3 career outline and Day 4 rehearsal as reference; do not submit every earlier packet.</p>',
            "MEDIA": '<details style="border:1px solid #b9d9de;border-radius:8px;padding:12px 16px;margin:18px 0"><summary style="font-weight:700;color:#245f69;cursor:pointer">Optional FYF presentation references</summary>' + "".join([prior.image_tag(visuals["p299"]["id"], "Prepare and Present checklist and presentation tips; this capstone page is a reference only"), prior.image_tag(visuals["p280"]["id"], "FYF capstone rubric including Presenter Delivery; this page is a reference only")]) + "</details>",
            "STEPS": step(1, "Check the source labels", "<p>Career, duty/work product, preparation, measure, amount, geography, date/source, limitation, bounded conclusion, and time.</p>") + step(2, "Deliver through your assigned route", "<p>Whole group, small group, teacher conference, private recording, or AAC. Use the appropriate technology choice recorded on your brief. The route changes; the evidence does not.</p>") + step(3, "Transfer the skill", "<p>Explain how one communication skill works in two different careers.</p>") + step(4, "Self-score and revise", "<p>Use all four criteria. Keep the before/after revision visible and submit only the brief plus rubric/self-score.</p>") + submission_panel,
            "EXIT": "<p>State your strongest exact evidence and the revision you would make next.</p>",
            "DONE": "<ul><li>60-90-second oral/AAC brief;</li><li>appropriate technology choice;</li><li>correct source labels and limitation;</li><li>delivery evidence;</li><li>two-career transfer;</li><li>self-score and visible revision.</li></ul>",
            "SUPPORT": "<p><strong>Word bank:</strong> work product/producto de trabajo · preparation/preparacion · median/mediana · limitation/limitacion · source/fuente.</p><p><strong>Use this frame:</strong> A <strong>[career]</strong> creates or studies <strong>[work product]</strong>. The source reports <strong>[measure and amount]</strong> for <strong>[geography/date]</strong>, but it does not prove <strong>[limit]</strong>.</p>",
            "FALLBACK": "<p>Use a supervised conference, private recording, or AAC make-up. Written-only work is not mislabeled oral evidence unless an accommodation changes the task. No public Discussion or family-adult dependency.</p>",
        },
    }


def teacher_content(files):
    link, flow = common.file_link, common.flow
    color = "#245f69"
    sources = '<p><a href="https://www.careeronestop.org/JobSearch/Interview/interview-and-negotiate.aspx">CareerOneStop Interview Guidance</a> · <a href="https://www.bls.gov/ooh/management/sales-managers.htm">BLS Sales Managers</a> · <a href="https://www.bls.gov/ooh/business-and-financial/market-research-analysts.htm">BLS Market Research Analysts</a> · <a href="https://www.bls.gov/ooh/arts-and-design/graphic-designers.htm">BLS Graphic Designers</a> · <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte/macarthur-high-school">Irving ISD MacArthur CTE</a>.</p>'
    support = "<p>Point-of-use word banks and complete sentence frames appear before the student steps. Companion prompts are sized for the requested answer: short labels use one line; reasons and transfer explanations use two or three full-width lines. Accept typing, dictation, annotation, enlarged print, live/private recording, or AAC. Score evidence and meaning, not English mechanics unless meaning is unclear.</p>"
    fallback = "<p>Locked FYF pages support projection and absence. Students use the workbook first and one companion route for evidence the workbook does not collect; do not make them complete both the workbook and a duplicate packet. H&amp;L, Xello, eDynamic, public Discussion, real sales/posts/accounts/data, clothing expense/modeling, family contact information, and camera use are not required.</p>"
    return {
        1: {
            "TITLE": "Audience and Sales Pitch Plan",
            "SUBTITLE": "50 minutes · FYF pp. 241-243",
            "ALERT": "<strong>Workbook first:</strong> FYF holds the seven-step pitch activity. The two-page companion adds audience/assumption, ethical, career, transfer, and oral-route evidence; it does not replace FYF for students who have the workbook.",
            "PREP": f'<ul><li>Have students open FYF pp. 241-243.</li><li>Post {link(files["PLAN"]["id"], "the two-page companion")} as Canvas-first with print fallback and open one fictional completed model.</li><li>Preassign Day 2 live, conference, recording, or AAC routes.</li></ul>',
            "EVIDENCE": "<p>Collect the FYF pitch plus the individual audience/fact/assumption check, accuracy/privacy boundary, career/work-product connection, transferable skill, and selected Day 2 oral route.</p>",
            "FLOW": flow(color, "Persuasion warm-up · 5", "Identify the hook, audience benefit, and requested action in one short model.") + flow("#4c8b38", "Read SparkClean · 8", "Label the four FYF parts and flag one claim that would need verification.") + flow("#8e4f7a", "Define offer and audience · 10", "Complete FYF Steps 2-3; separate evidence or logic from assumption.") + flow("#d39b22", "Plan four parts · 12", "Complete FYF Step 4 with concise, accurate language.") + flow(color, "Write and add evidence · 10", "Complete FYF Step 5 and the companion jobs the workbook does not collect.") + flow("#8e4f7a", "Exit · 5", "Career, work product, transferable skill, and one bounded claim."),
            "MONITOR": "<p><strong>Key:</strong> all four parts must be visible; the benefit must follow from a supplied fact or labeled reasoning; the call to action must be safe and specific. A product feature is what it has; a benefit is why that feature matters to the named audience. If students write before naming the audience, return them to FYF Step 3. Trim optional sharing first.</p>",
            "RESOURCES": sources,
            "SUPPORT": support,
            "FALLBACK": fallback,
        },
        2: {
            "TITLE": "Deliver, Test, and Revise",
            "SUBTITLE": "50 minutes · FYF p. 243",
            "ALERT": "<strong>Oral evidence with equal private routes:</strong> partner attendance and camera use are not requirements. A written draft supports the delivery but does not automatically replace oral/AAC evidence.",
            "PREP": f'<ul><li>Have students reopen the FYF pitch.</li><li>Post {link(files["DELIVERY"]["id"], "the two-page delivery and revision record")} and private media/annotation activity.</li><li>Set a visible 60-second timer and confirm live, conference, recorded, and AAC routes before class.</li></ul>',
            "EVIDENCE": "<p>Collect two timed oral/AAC attempts, one exact feedback point, visible before/after revision, evidence of its effect, and a two-career transfer response.</p>",
            "FLOW": flow(color, "Delivery model · 5", "Model understandable pace, clear organization, and a safe call to action.") + flow("#4c8b38", "Silent accuracy check · 5", "Remove unsupported urgency, guarantees, health, popularity, scarcity, or income claims.") + flow("#8e4f7a", "Attempt 1 · 10", "Record route, time, and one exact strength.") + flow("#d39b22", "Specific feedback · 8", "Name one exact word, sentence, pause, or organization choice to revise.") + flow(color, "Revise · 10", "Preserve the before/after language and the reason.") + flow("#4c8b38", "Attempt 2 · 7", "Apply the change and record its effect.") + flow("#8e4f7a", "Exit · 5", "Compare how the communication skill works in two careers."),
            "MONITOR": "<p>Feedback is specific enough to act on: 'change the call to action so the next step is clear' works; 'be more confident' does not. Score understandable meaning, organization, audience fit, accuracy, and revision. Do not score accent, eye contact, memorization, public confidence, or camera use. Trim class share-outs first; preserve Attempt 2.</p>",
            "RESOURCES": sources,
            "SUPPORT": support,
            "FALLBACK": fallback,
        },
        3: {
            "TITLE": "BrainBoost Decision and Career Outline",
            "SUBTITLE": "50 minutes · FYF pp. 244-247",
            "ALERT": "<strong>Workbook first:</strong> FYF holds the campaign analysis, brainstorm, three-solution table, and mini campaign plan. The companion adds individual cause/evidence, claim screening, transfer, and career-outline evidence.",
            "PREP": f'<ul><li>Have students open FYF pp. 244-247.</li><li>Post {link(files["BRAIN"]["id"], "the two-page companion")} as Canvas-first with print fallback.</li><li>Project one cause-versus-result model and the three fixed career cards.</li></ul>',
            "EVIDENCE": "<p>Collect FYF BrainBoost work plus an individual cause/evidence decision, rejected unsupported claim, cross-career problem-solving response, and complete fixed-source career outline. Oral evidence begins on Day 4; the outline itself is not mislabeled d(4)(C).</p>",
            "FLOW": flow(color, "Problem versus result · 5", "Low sales are a result; unclear value is a possible cause supported by supplied comments.") + flow("#4c8b38", "Analyze evidence · 8", "Review FYF message, visuals, stated audience, and customer comments.") + flow("#8e4f7a", "Generate and screen · 10", "Use FYF p. 246 and remove unsupported claims.") + flow("#d39b22", "Build the FYF rescue · 10", "Complete the three-solution plan and campaign concept.") + flow(color, "Choose career evidence · 7", "Use one fixed BLS card or equivalent verified prior evidence.") + flow("#4c8b38", "Outline the brief · 7", "Opening, duty, preparation, labeled labor evidence, limitation, and close.") + flow("#8e4f7a", "Exit · 3", "Result, possible cause, evidence, second career, and next check."),
            "MONITOR": "<p><strong>Key:</strong> the stated audience was reached. Strong problem statements name weak differentiation, unclear need, or unclear message as a possible cause. Several solutions can work when each answers supplied evidence and stays inside the product facts. Fixed BLS cards use May 2024 U.S. medians and 2024-34 projections; they are not DFW starting pay or shortages. Trim campaign sketch polish first.</p>",
            "RESOURCES": sources,
            "SUPPORT": support,
            "FALLBACK": fallback,
        },
        4: {
            "TITLE": "Interview Appearance and Rehearsal",
            "SUBTITLE": "50 minutes · Context-first CCE lesson",
            "ALERT": "<strong>Appearance is a job-context decision:</strong> workplace, task, safety, format, and accommodation determine the plan. Do not teach cost, body, gender, culture, religion, disability, or fashion taste as professionalism.",
            "PREP": f'<ul><li>Post {link(files["APPEAR"]["id"], "the two-page landscape companion")} and retryable practice Quiz.</li><li>Set oral/AAC rehearsal routes and a visible 60-90-second timer.</li><li>Project the three ready-to-use models in this guide; no additional model is needed.</li></ul>',
            "EVIDENCE": "<p>Collect three context decisions and respectful verification questions, Quiz-feedback review, two timed oral/AAC career rehearsals, one appropriate technology choice, visible revision, and evidence of what changed.</p>",
            "FLOW": flow(color, "Context-first warm-up · 5", "Compare how workplace, task, safety, format, and accommodation change preparation.") + flow("#4c8b38", "Three scenarios · 12", "Office/customer-facing, skilled-trade task demonstration, and virtual interview.") + flow("#8e4f7a", "Practice Quiz · 8", "Use immediate feedback on safety, source labels, virtual readiness, and oral routes.") + flow("#d39b22", "Rehearsal 1 · 8", "Capture content and delivery/AAC evidence.") + flow(color, "Feedback and revision · 7", "Name and apply one exact change.") + flow("#4c8b38", "Rehearsal 2 · 7", "Record time and the effect of the revision.") + flow("#8e4f7a", "Exit · 3", "One final content check and one delivery/AAC check."),
            "MONITOR": "<p><strong>Ready-to-use models:</strong></p><ul><li><strong>Office/customer-facing:</strong> clean, functional clothing that fits the role; verify workplace dress expectations and any access or accommodation needs.</li><li><strong>Skilled-trade task demonstration:</strong> clean work clothing with hair, jewelry, and loose items secured as the task requires; verify the exact PPE, tools, and arrival instructions before bringing or using anything.</li><li><strong>Virtual:</strong> clean, functional clothing, tested audio, a private background, notifications off, and a backup connection route; verify camera and access expectations.</li></ul><p><strong>Key:</strong> prepared, clean, functional, safe, and role-aware reasoning can look different across students and contexts. Task-required PPE or tools must be confirmed with the employer or site. Trim optional class modeling first.</p>",
            "RESOURCES": sources,
            "SUPPORT": support,
            "FALLBACK": fallback,
        },
        5: {
            "TITLE": "Career Oral Evidence Brief",
            "SUBTITLE": "50 minutes · Formative Week 4 evidence",
            "ALERT": "<strong>No separate Week 4 grade:</strong> this is planned formative rehearsal for the Week 5 interview and Week 6 capstone. Every student still needs assessable oral/AAC evidence through an assigned route.",
            "PREP": f'<ul><li>Post {link(files["ORAL"]["id"], "the two-page Career Oral Evidence Brief")}, {link(files["RUBRIC"]["id"], "the two-page feedback profile")}, and the private formative media Assignment.</li><li>Confirm each student\'s route before class and display the sequence or conference schedule.</li><li>Keep FYF p. 299 and the Presenter Delivery row on p. 280 as teacher references; do not assign the full capstone pages today.</li></ul>',
            "EVIDENCE": "<p>Collect a 60-90-second oral/AAC career brief with one appropriate technology choice, duty/work product, preparation, correctly labeled labor evidence, limitation, bounded conclusion, and understandable organization; add delivery evidence, two-career transfer, self-score, and one visible revision.</p>",
            "FLOW": flow(color, "Final evidence check · 5", "Career, duty, preparation, measure, amount, geography, date/source, limitation, conclusion, and time.") + flow("#4c8b38", "Oral/AAC evidence window · 35", "Use the preassigned route; students waiting complete private self-evidence and transfer reflection.") + flow("#8e4f7a", "Self-score and revise · 7", "Use all four criteria and keep one change visible.") + flow("#d39b22", "Week 5 preview · 3", "Private campus interview route; no family contact information is collected."),
            "MONITOR": "<p>The roster only closes when routes are planned before class. Parallel small groups, teacher conferences, private recordings, and AAC are equal evidence routes. A written-only response is not mislabeled oral evidence unless an accommodation changes the task. Do not score accent, speech difference, disability, camera use, eye contact, public confidence, or English mechanics unless meaning is unclear. Trim optional public sharing first.</p>",
            "RESOURCES": sources,
            "SUPPORT": support,
            "FALLBACK": fallback,
        },
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

    names = {
        "PLAN": "6sw-wk4-sales-pitch-plan.pdf",
        "DELIVERY": "6sw-wk4-pitch-delivery-record.pdf",
        "BRAIN": "6sw-wk4-brainboost-and-career-outline.pdf",
        "APPEAR": "6sw-wk4-appearance-and-rehearsal.pdf",
        "ORAL": "6sw-wk4-career-oral-evidence.pdf",
        "RUBRIC": "6sw-wk4-career-oral-rubric.pdf",
    }
    support_paths = {key: ROOT / "docs/resources/worksheets" / name for key, name in names.items()}
    pageset = [241, 242, 243, 244, 245, 246, 247, 280, 299]
    visual_paths = {f"p{page}": ASSETS / f"fyf-p{page}.jpg" for page in pageset}
    missing = [str(path) for path in [*support_paths.values(), *visual_paths.values()] if not path.is_file()]
    if missing:
        raise RuntimeError(f"Refusing partial Canvas write; missing upload dependencies: {missing}")

    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        module = await ensure_module(client)
        support_path = "course files/CCR Materials/6SW/Wk4"
        support_folder = await common.ensure_folder(client, support_path)
        files = {key: await common.upload(client, path, support_path) for key, path in support_paths.items()}
        visual_path = "course files/CCR Materials/6SW/Wk4/Locked Licensed Visuals"
        visual_folder = await common.ensure_folder(client, visual_path)
        visuals = {key: await common.upload(client, path, visual_path) for key, path in visual_paths.items()}

        quiz = await upsert_quiz(client)
        assignments = {}
        for day, key in {1: "PLAN", 2: "DELIVERY", 3: "BRAIN"}.items():
            assignments[day] = await common.upsert_assignment(
                client,
                TITLES[day],
                "<p>Complete privately by annotation, upload, typed labeled responses, or paper. Start in the FYF workbook and use one companion route for evidence the workbook does not collect.</p>",
                ["student_annotation", "online_upload", "online_text_entry", "media_recording"],
                files[key]["id"],
            )
        final_description = (
            f'<p>Submit {common.file_link(files["ORAL"]["id"], "the two-page Career Oral Evidence Brief")} and '
            f'{common.file_link(files["RUBRIC"]["id"], "the two-page feedback profile and self-score")} with the private 60-90-second oral/AAC evidence. '
            "Earlier FYF work and companions are reference evidence, not additional uploads. This assignment is formative, 0 points, not graded, and unpublished for teacher transfer.</p>"
        )
        assignments[5] = await common.upsert_assignment(
            client,
            TITLES[5],
            final_description,
            ["media_recording", "online_upload", "online_text_entry"],
            files["ORAL"]["id"],
        )
        urls = {day: f"/courses/{COURSE_ID}/assignments/{assignment['id']}" for day, assignment in assignments.items()}
        urls[4] = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"

        students = student_content(files, visuals, urls)
        teachers = teacher_content(files)
        labels = {
            1: "Audience and Sales Pitch Plan",
            2: "Deliver, Test, and Revise",
            3: "BrainBoost Decision and Career Outline",
            4: "Interview Appearance and Rehearsal",
            5: "Career Oral Evidence Brief",
        }
        interactions = {
            1: ("Assignment", assignments[1]["id"], TITLES[1]),
            2: ("Assignment", assignments[2]["id"], TITLES[2]),
            3: ("Assignment", assignments[3]["id"], TITLES[3]),
            4: ("Quiz", quiz["id"], TITLES[4]),
            5: ("Assignment", assignments[5]["id"], TITLES[5]),
        }
        order, pages = [], {}
        for day in range(1, 6):
            header_title = f"Day {day} · {labels[day]}"
            header = await prior.upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 6SW Wk4 Day {day} - {labels[day]}"
            student_page = await common.upsert_page(
                client,
                student_title,
                common.render("6sw-wk4-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, **CONTRACTS[day], **students[day]}),
            )
            teacher_title = f"TEACHER: 6SW Wk4 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(
                client,
                teacher_title,
                common.render("6sw-wk4-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **CONTRACTS[day], **teachers[day]}),
            )
            await prior.upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await prior.upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            kind, key, title = interactions[day]
            await prior.upsert_item(client, module["id"], kind, key, title)
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title), (kind, key, title)]
            pages[day] = {"teacher": teacher_page, "student": student_page}

        def matches_item(entry, kind, key):
            return entry.get("type") == kind and (
                (kind == "SubHeader" and entry.get("id") == key)
                or (kind == "Page" and entry.get("page_url") == key)
                or (kind in ("Assignment", "Quiz") and entry.get("content_id") == key)
            )

        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        keep_ids = set()
        for kind, key, _title in order:
            match = next((entry for entry in items if entry["id"] not in keep_ids and matches_item(entry, kind, key)), None)
            if not match:
                raise RuntimeError(f"Missing expected Sales module item: {kind} {key}")
            keep_ids.add(match["id"])
        for entry in items:
            if entry["id"] not in keep_ids:
                await common.api(client, "DELETE", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{entry['id']}")
        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(entry for entry in items if matches_item(entry, kind, key))
            await common.api(
                client,
                "PUT",
                f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}",
                data={"module_item[position]": position, "module_item[title]": title},
            )
        final = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        ordered = sorted(final, key=lambda entry: entry.get("position", 0))
        if len(ordered) != len(order):
            raise RuntimeError(f"Expected {len(order)} Sales module items; found {len(ordered)}")
        for position, ((kind, key, _title), entry) in enumerate(zip(order, ordered), 1):
            if entry.get("position") != position or not matches_item(entry, kind, key):
                raise RuntimeError(f"Sales module order mismatch at position {position}")

        support_files = await lock_every_file_in_folder(client, support_folder)
        visual_files = await lock_every_file_in_folder(client, visual_folder)
        support_folder = await common.api(client, "GET", f"/folders/{support_folder['id']}")
        visual_folder = await common.api(client, "GET", f"/folders/{visual_folder['id']}")
        if not support_folder.get("locked") or not visual_folder.get("locked") or any(not record.get("locked") for record in support_files + visual_files):
            raise RuntimeError("Every Sales support folder and file must remain locked")
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        if module.get("published"):
            raise RuntimeError("Sales module must remain unpublished")
        print(
            json.dumps(
                {
                    "module": {"id": module["id"], "published": module["published"]},
                    "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
                    "visual_folder": {"id": visual_folder["id"], "locked": visual_folder["locked"]},
                    "files": {key: record["id"] for key, record in files.items()},
                    "visuals": {key: record["id"] for key, record in visuals.items()},
                    "quiz": {"id": quiz["id"], "published": quiz.get("published")},
                    "assignments": {
                        str(day): {
                            "id": assignment["id"],
                            "published": assignment.get("published"),
                            "points": assignment.get("points_possible"),
                            "grading_type": assignment.get("grading_type"),
                            "omit_from_final_grade": assignment.get("omit_from_final_grade"),
                        }
                        for day, assignment in assignments.items()
                    },
                    "pages": {
                        str(day): {kind: {"url": page["url"], "published": page["published"]} for kind, page in pair.items()}
                        for day, pair in pages.items()
                    },
                    "items": [{"position": entry["position"], "type": entry["type"], "title": entry["title"]} for entry in ordered],
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
