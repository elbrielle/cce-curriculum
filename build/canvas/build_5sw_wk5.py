"""Build the unpublished 5SW Week 5 MoneySkills evidence module."""

import asyncio
import json
import re
import sys
from urllib.parse import urlencode

import httpx

import build_5sw_wk1 as prior


common = prior.common
COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/4sw/wk1/day3"
MODULE_NAME = "5SW Wk5: MoneySkills — Budget, Location, and Career Evidence"
RUBRIC_NOTE_MARKER = 'data-cce-rubric-note="cce-advisory-rubric-v1"'
WORKSHEET_FILES = {
    "SOURCE": "5sw-wk5-salary-source-and-lifestyle-target.pdf",
    "BUDGET": "5sw-wk5-dallas-county-personal-budget.pdf",
    "LOCATION": "5sw-wk5-location-cost-comparison.pdf",
    "AID": "5sw-wk5-paying-for-education-and-training.pdf",
    "PORTFOLIO": "5sw-wk5-three-career-budget-portfolio.pdf",
    "RUBRIC": "5sw-wk5-budget-portfolio-rubric.pdf",
}
VISUAL_FILES = {
    "career": "fyf-rung-3-career-deep-dive.jpg",
    "skills": "fyf-rung-3-skills-check.jpg",
}

DAY_TITLES = {
    1: "PRACTICE: Salary Source and Lifestyle Target",
    2: "PRACTICE: Dallas County Personal Budget",
    3: "PRACTICE: Location Cost Comparison",
    4: "PRACTICE: Paying for Education and Training Check",
    5: "MAJOR 2: Personal Budget Evidence Portfolio",
}


def preflight():
    required = [
        ROOT / "build/canvas/templates/5sw-wk5-student.html",
        ROOT / "build/canvas/templates/5sw-wk5-teacher.html",
        *(ROOT / "docs/resources/worksheets" / name for name in WORKSHEET_FILES.values()),
        *(ASSETS / name for name in VISUAL_FILES.values()),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"5SW Wk5 preflight missing required files: {missing}")


CONTRACTS = {
    1: {
        "TOPIC": "Labor Trends",
        "OBJECTIVE": "Students will analyze a current labor-market trend and use accurate salary evidence to build a fictional lifestyle target.",
        "TEKS": "d(5)(A), d(5)(D)",
        "DOL": "source-labeled salary and trend evidence, fictional lifestyle target, and three ranked priorities.",
        "I_CAN": "label salary and trend evidence, then use it to build a fictional lifestyle target and rank three priorities.",
        "SHOW": "Complete the source label, trend conclusion, lifestyle target, three priorities, and one evidence limitation.",
    },
    2: {
        "TOPIC": "Personal Budget",
        "OBJECTIVE": "Students will prepare and revise a fictional personal budget that reflects a desired lifestyle.",
        "TEKS": "d(5)(D)",
        "DOL": "fictional Dallas County monthly budget with balance, one $300 event response, and one evidence-based revision.",
        "I_CAN": "use a fixed Dallas County scenario to build, check, and revise a fictional monthly budget.",
        "SHOW": "Complete the $4,200 monthly plan, calculate the balance, respond to the $300 event, and explain one revision.",
    },
    3: {
        "TOPIC": "Personal Budget",
        "OBJECTIVE": "Students will compare one fixed income across three locations and explain how cost targets change a personal budget decision.",
        "TEKS": "d(5)(D)",
        "DOL": "same-$70,000-offer, three-location comparison and Jordan recommendation.",
        "I_CAN": "hold one fictional job offer constant and explain how three location-cost targets change a budget decision.",
        "SHOW": "Calculate three offer-minus-target gaps, recommend one location for Jordan, and name one unanswered question.",
    },
    4: {
        "TOPIC": "Paying for Education",
        "OBJECTIVE": "Students will investigate and describe current methods for paying for college and other postsecondary training.",
        "TEKS": "d(3)(C)",
        "DOL": "funding-method decision guide plus retryable Canvas practice check.",
        "I_CAN": "separate ways to reduce cost, earn money, and borrow money, then verify the conditions before deciding.",
        "SHOW": "Sort seven methods, decide for two fictional students, repair three claims, and use the Quiz feedback.",
    },
    5: {
        "TOPIC": "Personal Budget",
        "OBJECTIVE": "Students will compare salaries for at least three careers on one evidence basis and use the comparison to revise a fictional personal budget.",
        "TEKS": "d(5)(D), d(5)(E)",
        "DOL": "three-career same-basis comparison, tradeoff recommendation, revised budget, and private portfolio.",
        "I_CAN": "compare three careers on one salary basis and use the evidence to revise a fictional budget decision.",
        "SHOW": "Submit the private four-page portfolio with three career records, a tradeoff recommendation, three budget-screen calculations, and one revision.",
    },
}


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    matches = [module for module in modules if module.get("name") == MODULE_NAME]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one module named {MODULE_NAME!r}; found {len(matches)}")
    found = matches[0] if matches else None
    data = {"module[published]": "false"}
    if found:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data=data)
    data["module[name]"] = MODULE_NAME
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


async def mapped_major_assignment(client):
    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group_matches = [entry for entry in groups if entry.get("name") == "Major Assessments (60%)"]
    if len(group_matches) != 1:
        raise RuntimeError(
            "Expected exactly one assignment group named 'Major Assessments (60%)'; "
            f"found {len(group_matches)}"
        )
    group = group_matches[0]
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    title = DAY_TITLES[5]
    matches = [entry for entry in assignments if entry.get("name") == title]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one existing mapped Major assignment named {title!r}; found {len(matches)}")
    found = matches[0]
    rubric_note = re.search(
        r'<div data-cce-rubric-note="cce-advisory-rubric-v1".*?</div>',
        found.get("description") or "",
        flags=re.I | re.S,
    )
    if (
        found.get("published")
        or float(found.get("points_possible") or 0) != 100
        or found.get("assignment_group_id") != group["id"]
        or found.get("grading_type") != "points"
        or found.get("omit_from_final_grade") is not False
        or rubric_note is None
    ):
        raise RuntimeError(
            f"Mapped Major invariant failed before module writes: published={found.get('published')}, "
            f"points={found.get('points_possible')}, group={found.get('assignment_group_id')}, "
            f"grading={found.get('grading_type')}, omit={found.get('omit_from_final_grade')}, "
            f"rubric_note={rubric_note is not None}"
        )
    return found, group


async def assert_annotation_assignment(client, assignment, source_attachment_id, *, mapped=False):
    assignment = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignment['id']}")
    source_file = await common.api(client, "GET", f"/files/{source_attachment_id}")
    annotation_attachment_id = int(assignment.get("annotatable_attachment_id") or 0)
    annotation_file = await common.api(client, "GET", f"/files/{annotation_attachment_id}") if annotation_attachment_id else {}
    if annotation_file and not annotation_file.get("locked"):
        annotation_file = await common.api(client, "PUT", f"/files/{annotation_attachment_id}", data={"locked": "true"})
    required_routes = {"student_annotation", "online_upload", "online_text_entry"}
    failures = {
        "published": assignment.get("published") is not False,
        "points_possible": float(assignment.get("points_possible") or 0) != (100 if mapped else 0),
        "grading_type": assignment.get("grading_type") != ("points" if mapped else "percent"),
        "omit_from_final_grade": assignment.get("omit_from_final_grade") is not (False if mapped else True),
        "submission_types": set(assignment.get("submission_types") or []) != required_routes,
        "annotatable_attachment_missing": not annotation_attachment_id,
        "source_file_locked": source_file.get("locked") is not True,
        "annotation_file_locked": annotation_file.get("locked") is not True,
        "annotation_filename": annotation_file.get("filename") != source_file.get("filename"),
        "annotation_size": int(annotation_file.get("size") or -1) != int(source_file.get("size") or -2),
    }
    failed = [name for name, value in failures.items() if value]
    if failed:
        raise RuntimeError(f"Annotation Assignment invariant failed for {assignment.get('name')!r}: {failed}")
    return assignment


async def upsert_practice_assignment(client, title, description, attachment_id):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == title]
    if len(matches) > 1:
        raise RuntimeError(f"Duplicate assignments named {title!r}: {[entry['id'] for entry in matches]}")
    found = matches[0] if matches else None
    data = {
        "assignment[name]": title,
        "assignment[description]": description,
        "assignment[published]": "false",
        "assignment[points_possible]": "0",
        "assignment[grading_type]": "percent",
        "assignment[omit_from_final_grade]": "true",
        "assignment[submission_types][]": ["student_annotation", "online_upload", "online_text_entry"],
        "assignment[annotatable_attachment_id]": str(attachment_id),
    }
    assignment = await common.api(
        client,
        "PUT" if found else "POST",
        f"/courses/{COURSE_ID}/assignments/{found['id']}" if found else f"/courses/{COURSE_ID}/assignments",
        data=data,
    )
    return await assert_annotation_assignment(client, assignment, attachment_id)


async def require_major_assignment(client, found, group, description, attachment_id):
    rubric_note = re.search(
        r'<div data-cce-rubric-note="cce-advisory-rubric-v1".*?</div>',
        found.get("description") or "",
        flags=re.I | re.S,
    )
    if rubric_note is None:
        raise RuntimeError(f"Mapped Major is missing required rubric conversion note: {DAY_TITLES[5]!r}")
    assignment = await common.api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{found['id']}",
        data={
            "assignment[name]": DAY_TITLES[5],
            "assignment[description]": description + rubric_note.group(0),
            "assignment[published]": "false",
            "assignment[points_possible]": "100",
            "assignment[grading_type]": "points",
            "assignment[assignment_group_id]": str(group["id"]),
            "assignment[omit_from_final_grade]": "false",
            "assignment[submission_types][]": [
                "student_annotation",
                "online_upload",
                "online_text_entry",
            ],
            "assignment[annotatable_attachment_id]": str(attachment_id),
        },
    )
    assignment = await assert_annotation_assignment(client, assignment, attachment_id, mapped=True)
    if (
        assignment.get("assignment_group_id") != group["id"]
        or RUBRIC_NOTE_MARKER not in (assignment.get("description") or "")
    ):
        raise RuntimeError(f"Major group/rubric invariant failed after update for {DAY_TITLES[5]!r}")
    return assignment


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
    matches = [quiz for quiz in quizzes if quiz.get("title") == DAY_TITLES[4]]
    if len(matches) > 1:
        raise RuntimeError(f"Duplicate quizzes named {DAY_TITLES[4]!r}: {[entry['id'] for entry in matches]}")
    found = matches[0] if matches else None
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
    desired_names = {name for name, *_rest in QUESTIONS}
    for prior_question in existing:
        if prior_question.get("question_name") not in desired_names:
            await common.api(
                client,
                "DELETE",
                f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior_question['id']}",
            )
    existing = [entry for entry in existing if entry.get("question_name") in desired_names]
    unique = []
    seen_names = set()
    for prior_question in existing:
        name = prior_question.get("question_name")
        if name in seen_names:
            await common.api(
                client,
                "DELETE",
                f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior_question['id']}",
            )
        else:
            seen_names.add(name)
            unique.append(prior_question)
    existing = unique
    for position, (name, prompt, correct, wrong, yes, no) in enumerate(QUESTIONS, 1):
        old = next((question for question in existing if question.get("question_name") == name), None)
        payload = {"question": {"question_name": name, "question_text": prompt, "question_type": "multiple_choice_question", "position": position, "points_possible": 1, "correct_comments": yes, "incorrect_comments": no, "answers": [{"answer_text": correct, "answer_weight": 100}] + [{"answer_text": answer, "answer_weight": 0} for answer in wrong]}}
        path = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{old['id']}" if old else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        await common.api(client, "PUT" if old else "POST", path, json=payload)
    expected = [name for name, *_rest in QUESTIONS]
    final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    final_by_name = {entry.get("question_name"): entry for entry in final_questions}
    if set(final_by_name) != set(expected) or len(final_questions) != len(expected):
        actual = [entry.get("question_name") for entry in final_questions]
        raise RuntimeError(f"MoneySkills Quiz mismatch: expected {expected}, found {actual}")
    reorder_fields = []
    for name in expected:
        reorder_fields.extend(
            [("order[][id]", str(final_by_name[name]["id"])), ("order[][type]", "question")]
        )
    await common.api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/reorder",
        content=urlencode(reorder_fields),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    actual = [entry.get("question_name") for entry in final_questions]
    if actual != expected:
        raise RuntimeError(f"MoneySkills Quiz mismatch: expected {expected}, found {actual}")
    quiz = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
    if (
        quiz.get("published")
        or quiz.get("quiz_type") != "practice_quiz"
        or int(quiz.get("allowed_attempts") or 0) != -1
        or quiz.get("shuffle_answers") is not False
    ):
        raise RuntimeError(
            f"MoneySkills Quiz invariant failed: published={quiz.get('published')}, "
            f"type={quiz.get('quiz_type')}, attempts={quiz.get('allowed_attempts')}, "
            f"shuffle={quiz.get('shuffle_answers')}"
        )
    return quiz


def student_content(files, visuals, urls):
    link, step = common.file_link, common.step
    rung_media = (
        '<h3 style="color:#315f4c;border-bottom:3px solid #bdd6cb">Optional workbook reminder</h3>'
        '<div style="border-left:5px solid #d39b22;background:#fff8e7;padding:12px 16px;margin:14px 0"><strong>Source-label repair:</strong> the workbook page is a reminder of prior career work, not current salary proof. For scored evidence, record the exact occupation, geography, year/date, and measure shown in Xello or use the fixed fallback card.</div>'
        + prior.image_tag(visuals["career"]["id"], "Find Your Future Rung 3 page prompting a deeper look at one career, including work tasks, training, and salary fields")
        + prior.image_tag(visuals["skills"]["id"], "Find Your Future Rung 3 skills-check page with lifestyle, schedule, education, and priority prompts")
    )
    return {
        1: {"TITLE":"Salary Source and Lifestyle Target","PURPOSE":"Keep a salary number attached to its source and decide which parts of a fictional lifestyle matter most.","TODAY":"<ul><li>audit one salary label;</li><li>read a fixed career card;</li><li>build a fictional lifestyle target;</li><li>rank three current priorities.</li></ul>","READY":f'<p>Open {link(files["SOURCE"]["id"], "the three-page Salary Source and Lifestyle Target packet")} or <a href="{urls[1]}">the private annotation activity</a>.</p>',"MEDIA":rung_media,"STEPS":step(1,"Audit the label","<p>Write the exact occupation, geography, year or access date, salary measure, and source. Keep a median labeled as a median.</p>")+step(2,"Read the fallback card","<p>Use the fixed BLS Electricians card when Xello does not display a usable local figure.</p>")+step(3,"Build the fictional lifestyle","<p>Describe housing, transportation, basic needs, connection, interests, and savings without sharing family income or bills.</p>")+step(4,"Rank priorities and read the trend","<p>Rank three priorities. Use one exact trend fact, then name what the source cannot answer.</p>"),"EXIT":"<p>Name one salary label you repaired and one lifestyle priority the number alone cannot decide.</p>","DONE":"<ul><li>complete source audit;</li><li>one fixed-card or Xello interpretation;</li><li>fictional lifestyle target;</li><li>three ranked priorities;</li><li>trend conclusion and limitation.</li></ul>","SUPPORT":"<p><strong>Word bank:</strong> salary measure/tipo de salario · median/mediana · geography/ubicación · priority/prioridad · limitation/limitación.</p><p><strong>Use this frame:</strong> My source shows ___ for ___ in ___. It does not prove ___.</p>","FALLBACK":"<p>The fixed card is complete evidence. Xello is the preferred local cross-check when available; H&amp;L and open search are optional. No personal financial disclosure is required.</p>"},
        2: {"TITLE":"Build a Dallas County Personal Budget","PURPOSE":"Use one fixed adult scenario to build and revise a monthly plan without exposing anyone's real finances.","TODAY":"<ul><li>read a dated Dallas County scenario;</li><li>use the fixed $4,200 monthly income;</li><li>build and check a monthly plan;</li><li>respond to one $300 event.</li></ul>","READY":f'<p>Open {link(files["BUDGET"]["id"], "the four-page Dallas County budget packet")} or <a href="{urls[2]}">the private annotation activity</a>. The scenario is fictional and uses one adult with no children.</p>',"MEDIA":"","STEPS":step(1,"Read the fixed scenario","<p>The MIT scenario requires about $48,489 before tax and about $41,399 after tax each year. The rounded monthly basic-cost plan is about $3,450.</p>")+step(2,"Use the supplied monthly income","<p>Build from $4,200. Do not convert a career salary into take-home pay.</p>")+step(3,"Build and check the plan","<p>Complete each row, show income minus spending, and connect the plan to the Day 1 priorities.</p>")+step(4,"Respond to the $300 event","<p>Reduce the fictional monthly income by $300. Protect one priority, revise one choice, and calculate the new balance.</p>"),"EXIT":"<p>State the final balance, one revision, and one missing factor.</p>","DONE":"<ul><li>all budget rows completed;</li><li>math checked;</li><li>$300 event response;</li><li>one revision explained;</li><li>one limit named.</li></ul>","SUPPORT":"<p><strong>Word bank:</strong> income/ingreso · expense/gasto · balance/saldo · surplus/superávit · shortage/déficit.</p><p><strong>Use this frame:</strong> My plan has a ___ of $ ___. After the event, I changed ___ because ___.</p>","FALLBACK":"<p>Use the supplied scenario only. Do not submit family wages, rent, debt, immigration information, aid status, or real account data.</p>"},
        3: {"TITLE":"Compare the Same Offer Across Locations","PURPOSE":"Hold one fictional $70,000 offer constant and see how three location-cost targets change the decision.","TODAY":"<ul><li>compare one adult/no children in four counties;</li><li>calculate three offer-minus-target gaps;</li><li>identify nonfinancial factors;</li><li>recommend one location for Jordan.</li></ul>","READY":f'<p>Open {link(files["LOCATION"]["id"], "the two-page Location Cost Comparison packet")} or <a href="{urls[3]}">the private annotation activity</a>.</p>',"MEDIA":"","STEPS":step(1,"Keep the scenario constant","<p>Every county uses one adult with no children from MIT's February 15, 2026 update. Jordan's fictional offer stays $70,000 in every location.</p>")+step(2,"Calculate three gaps","<p>Choose Dallas and two other locations. Subtract each supplied annual before-tax target from $70,000. Do not rebuild the annual target from the rounded hourly display.</p>")+step(3,"Add what money misses","<p>Consider support network, transportation access, climate, job availability, community, and personal goals.</p>")+step(4,"Recommend for fictional Jordan","<p>Use three calculated gaps, two nonfinancial factors, and one question the table cannot answer.</p>"),"EXIT":"<p>Name one numerical finding and one reason it cannot decide where a person should live.</p>","DONE":"<ul><li>three location calculations;</li><li>gaps checked;</li><li>two nonfinancial factors;</li><li>evidence-based recommendation;</li><li>one unanswered question.</li></ul>","SUPPORT":"<p><strong>Word bank:</strong> fixed offer/oferta fija · annual target/meta anual · gap/diferencia · nonfinancial/no financiero.</p><p><strong>Use this frame:</strong> I recommend ___ for Jordan because the gap is ___ and ___. Jordan still needs to investigate ___.</p>","FALLBACK":"<p>All numbers are supplied. A calculator, typed work, dictation, or paper is allowed. No student must disclose a real home plan or family situation.</p>"},
        4: {"TITLE":"Paying for Education and Training","PURPOSE":"Separate methods that reduce cost, earn money, and borrow money, then verify the conditions before deciding.","TODAY":"<ul><li>sort seven funding and training methods;</li><li>decide for two fictional students;</li><li>repair three common claims;</li><li>practice with feedback.</li></ul>","READY":f'<p>Open {link(files["AID"]["id"], "the three-page Paying for Education and Training guide")} and <a href="{urls[4]}">the retryable practice Quiz</a>.</p>',"MEDIA":"","STEPS":step(1,"Sort the methods","<p>Record which methods reduce cost, earn money, or borrow money. Keep the provider conditions attached.</p>")+step(2,"Decide for two fictional students","<p>Use Taylor and Jordan. Choose a first method, explain why, and state what must be verified.</p>")+step(3,"Repair three claims","<p>FAFSA is an application, not an automatic loan or award. For Texas public-school seniors in grade 12, current authorized routes are FAFSA, TASFA when applicable, or an authorized signed opt-out. Middle-school students complete none of them here.</p>")+step(4,"Use feedback","<p>Complete the five-step sequence, then retake the Quiz until every explanation makes sense. Quiz attempts are not graded.</p>"),"EXIT":"<p>Correct one misconception and name the official source you would verify next.</p>","DONE":"<ul><li>seven methods sorted;</li><li>two fictional decisions;</li><li>three claims repaired;</li><li>five-step sequence;</li><li>Quiz feedback reviewed.</li></ul>","SUPPORT":"<p><strong>Word bank:</strong> grant/subvención · scholarship/beca · work-study/trabajo-estudio · loan/préstamo · repayment/reembolso.</p><p><strong>Use this frame:</strong> ___ can ___, but the student still needs to verify ___.</p>","FALLBACK":"<p>The packet contains the full route. Do not enter a Social Security number, tax data, family income, immigration details, FSA ID, bank information, or application data.</p>"},
        5: {"TITLE":"Personal Budget and Career Evidence Portfolio","PURPOSE":"Compare three careers on one salary basis and revise a fictional budget decision using accurate labels and an honest tradeoff.","TODAY":"<ul><li>compare three careers;</li><li>recommend one and name the tradeoff;</li><li>run three before-tax budget screens;</li><li>audit and revise before private submission.</li></ul>","READY":f'<p>Open {link(files["PORTFOLIO"]["id"], "the four-page portfolio")} and {link(files["RUBRIC"]["id"], "the two-page rubric")}. Days 1–4 may help as references, but you do not attach those formative packets again.</p>',"MEDIA":"","STEPS":step(1,"Use one salary basis","<p>Use exact Xello labels for all three careers only when they are comparable. Otherwise use the fixed May 2024 U.S. BLS medians in the packet.</p>")+step(2,"Compare and recommend","<p>Use two exact evidence details, one current priority, and one disadvantage or cost of the choice.</p>")+step(3,"Run the budget screen","<p>Show annual salary minus the Dallas annual before-tax target for all three careers. Explain why a positive result does not prove affordability or fit.</p>")+step(4,"Audit and submit privately",f'<p>Record the revised fictional monthly result. Use <a href="{urls[5]}">the private portfolio Assignment</a> and revise the weakest rubric criterion before submitting.</p>'),"EXIT":"<p>Name one repaired source label, one budget revision, and one unsupported claim you removed.</p>","DONE":"<ul><li>three comparable career records;</li><li>evidence-based recommendation and tradeoff;</li><li>three visible salary-minus-target calculations;</li><li>revised fictional monthly result;</li><li>source limitation;</li><li>self-audit and revision.</li></ul>","SUPPORT":"<p><strong>Word bank:</strong> comparable/comparable · preparation/preparación · tradeoff/compensación · annual target/meta anual · limitation/limitación.</p><p><strong>Use this frame:</strong> I currently recommend ___ because ___ and ___. The tradeoff is ___.</p>","FALLBACK":"<p>The fixed three-career evidence is complete. The Day 5 packet is self-contained. No public discussion, Xello screenshot, family budget, prior-packet attachment, or H&amp;L favorite is required.</p>"},
    }


def teacher_content(files):
    link, flow = common.file_link, common.flow
    c = "#315f4c"
    return {
        1: {
            "TITLE": "Salary Source and Lifestyle Target",
            "SUBTITLE": "50 minutes · TEKS d(5)(A), d(5)(D)",
            "ALERT": "<strong>Keep the source label attached.</strong> Median, starting, range, local, and national are different measures. Xello is the preferred local source; the fixed BLS card is the no-login route.",
            "PREP": f'<ul><li><strong>Default:</strong> one device per student, one projector, zero prints. Post {link(files["SOURCE"]["id"], "the three-page source and lifestyle packet")} and private annotation activity.</li><li><strong>Paper:</strong> print one three-page packet per student and place one collection tray by the door.</li><li>Students work individually; a 45-second turn-and-talk may help them test a source label, but every student submits a private response.</li><li>Do not request real family financial information.</li></ul>',
            "EVIDENCE": "<p>Formative source audit, trend interpretation, fictional lifestyle target, three priorities, and limitation.</p>",
            "MODEL": '<div style="border:1px solid #bdd6cb;border-radius:8px;background:#f2f8f5;padding:12px 16px"><p><strong>Complete model:</strong> “BLS reports a May 2024 U.S. median of $62,350 for Electricians. It projects 9% national growth from 2024-34 and about 81,000 openings each year. I would protect emergency savings first because it helps with an unexpected cost. This evidence does not prove DFW starting pay or that I would get a job.”</p><p><strong>Non-example:</strong> “Electricians start at $62,350 in Dallas.” The measure and geography have been changed.</p></div>',
            "FLOW": flow(c, "Warm-up · 5", "An ordinary day at age 25.") + flow("#4c8b38", "Source audit/model · 10", "Occupation, place, date, measure.") + flow("#8a4f2b", "Lifestyle target · 18", "Fictional choices only.") + flow("#d39b22", "Priorities/trend · 12", "Rank, interpret, limit.") + flow(c, "Submit/cleanup · 5", "Private response and device/material return."),
            "MONITOR": "<ul><li><strong>Minute 12:</strong> every source label has occupation, geography, date/year, measure, and source. If more than one-quarter of the class is missing two labels, pause and annotate the fixed card together.</li><li><strong>Minute 28:</strong> page 2 describes a fictional scenario without family details. Redirect personal disclosures to the supplied scenario.</li><li><strong>Minute 42:</strong> three priorities, one exact trend fact, and one limit are visible. Students who are behind use the fixed card and labeled bullets.</li><li><strong>Trim/recovery:</strong> cut partner sharing, never the source label, priorities, trend, or limit. At minute 47, save/submit online or place the named packet in the tray; continue the same artifact during recovery, not a new worksheet.</li><li>The fallback $62,350 is the May 2024 U.S. median for Electricians--not DFW or starting pay. The 9% projection and 81,000 annual openings are national 2024-34 evidence. Score reasoning, not the chosen priorities.</li></ul>",
            "RESOURCES": '<p><a href="https://www.bls.gov/ooh/construction-and-extraction/electricians.htm">BLS Electricians</a>. Xello local values require the exact displayed geography, measure, and access date.</p>',
            "SUPPORT": "<p>Three pages separate the source label, fictional lifestyle, and priority/trend reasoning. Each writing job has its own word bank and complete frame. Accept typing, dictation, annotation, or paper.</p>",
            "FALLBACK": "<p>Fixed evidence replaces any failed login. H&amp;L, open search, screenshots, and personal disclosure are not required. Absent students open the same Student Guide and private Assignment; paper students receive the same three pages.</p>",
        },
        2: {
            "TITLE": "Build a Dallas County Personal Budget",
            "SUBTITLE": "50 minutes · TEKS d(5)(D)",
            "ALERT": "<strong>Use the fictional $4,200 monthly income.</strong> Students do not estimate take-home pay or reveal family income, housing costs, debt, aid, immigration status, or financial stress.",
            "PREP": f'<ul><li><strong>Default:</strong> one device and calculator per student (a calculator may be shared by a pair), one projector, zero prints. Post {link(files["BUDGET"]["id"], "the four-page budget packet")} and private annotation activity.</li><li><strong>Paper:</strong> print one four-page packet per student and set one collection tray by the door.</li><li>Students work individually. Project the supplied model before releasing the build.</li></ul>',
            "EVIDENCE": "<p>Formative fictional monthly plan, visible math, $300 event response, evidence-based revision, and one limitation.</p>",
            "MODEL": '<div style="border:1px solid #bdd6cb;border-radius:8px;background:#f2f8f5;padding:12px 16px"><p><strong>Worked model:</strong> $3,450 basic costs + $300 emergency savings + $200 long-term goal + $250 wants = $4,200, so the balance is $0. After the income drops to $3,900, protect $300 emergency savings, reduce wants from $250 to $0, and reduce the long-term goal from $200 to $150. New spending is $3,900 and the balance is $0.</p><p><strong>Non-example:</strong> “$48,489 ÷ 12 is my take-home pay.” The MIT before-tax target is not the supplied monthly income.</p></div>',
            "FLOW": flow(c, "Warm-up · 5", "Largest fixed category and why.") + flow("#4c8b38", "Scenario/model · 10", "Dated evidence and units.") + flow("#8a4f2b", "Build/check · 22", "$4,200 plan and balance.") + flow("#d39b22", "Event/revise · 8", "Protect, change, recalculate.") + flow(c, "Submit/cleanup · 5", "Balance, revision, limit."),
            "MONITOR": "<ul><li><strong>Minute 12:</strong> income is $4,200 monthly and no annual salary has been converted to take-home pay. If more than one-quarter mixes units, stop and label annual versus monthly together.</li><li><strong>Minute 27:</strong> all basic rows and at least one savings row are filled; totals are visible. Pair-check arithmetic, not lifestyle choices.</li><li><strong>Minute 40:</strong> the $300 event shows new income, a protected priority, a revision, and a recalculated balance. Students behind use the worked baseline; do not remove the revision reasoning.</li><li><strong>Trim/recovery:</strong> cut optional peer comparison. Protect the original balance, event response, limit, submission, and calculator/device return. Save the same packet for recovery.</li><li>MIT Dallas County, one adult/no children, updated Feb. 15, 2026: $23.31/hour, $41,399 required after tax, and $48,489 before tax annually. A shortage is valid evidence when the math and revision are clear.</li></ul>",
            "RESOURCES": '<p><a href="https://livingwage.mit.edu/counties/48113">MIT Living Wage Calculator -- Dallas County</a>. This is an illustrative scenario, not individualized financial advice.</p>',
            "SUPPORT": "<p>Four pages separate the source/model, budget table, balance reasoning, and event revision. Every explanation has full-width lines, a word bank, and a complete frame.</p>",
            "FALLBACK": "<p>Use the supplied scenario only. Paper, typed, dictated, and annotation routes are equal.</p>",
        },
        3: {
            "TITLE": "Compare the Same Offer Across Locations",
            "SUBTITLE": "50 minutes · TEKS d(5)(D)",
            "ALERT": "<strong>Hold the household and offer constant.</strong> Jordan's $70,000 offer is fictional. This is a cost-target comparison, not a claim that one location or lifestyle is best.",
            "PREP": f'<ul><li><strong>Default:</strong> one device and calculator per student (a calculator may be shared by a pair), one projector, zero prints. Post {link(files["LOCATION"]["id"], "the two-page location packet")} and private annotation activity.</li><li><strong>Paper:</strong> print one two-page landscape packet per student and set one collection tray by the door.</li><li>Students work individually. Project the supplied Dallas subtraction before students choose two comparison locations.</li></ul>',
            "EVIDENCE": "<p>Formative three-location calculations, two nonfinancial factors, Jordan recommendation, and one unanswered question.</p>",
            "MODEL": '<div style="border:1px solid #bdd6cb;border-radius:8px;background:#f2f8f5;padding:12px 16px"><p><strong>Complete model:</strong> Dallas: $70,000 - $48,489 = $21,511 above the supplied target. “Dallas is Jordan\'s strongest current choice because the offer is $21,511 above the target and Jordan has a support network there. Jordan still needs to investigate transportation and job stability.”</p><p><strong>Non-example:</strong> Recomputing $23.31 × 2,080 and replacing the official annual target. The displayed hourly figure is rounded; use the supplied official annual target.</p></div>',
            "FLOW": flow(c, "Prediction/model · 7", "Same household, offer, date; Dallas subtraction.") + flow("#4c8b38", "Evidence read · 6", "Supplied annual targets.") + flow("#8a4f2b", "Compare/check · 18", "Three offer-minus-target gaps.") + flow("#d39b22", "Recommend · 14", "Numbers plus nonfinancial factors.") + flow(c, "Submit/cleanup · 5", "Finding, limit, and material return."),
            "MONITOR": "<ul><li><strong>Minute 10:</strong> students have circled one adult/no children, February 15, 2026, and $70,000 before tax. If the scenario changes, reset it before calculation.</li><li><strong>Minute 25:</strong> three calculations use the supplied annual targets. Do not accept hourly×2,080 replacements for the official targets.</li><li><strong>Minute 40:</strong> the recommendation includes three gaps, two nonfinancial factors, and one unresolved question. If more than one-quarter omits a factor, project the complete frame and let students finish in labeled bullets.</li><li><strong>Trim/recovery:</strong> cut prediction sharing, never the three gaps, recommendation evidence, question, or submission. Save the same response for recovery.</li><li>Annual targets: Tulsa $44,165; Dallas $48,489; Los Angeles $60,161; New York County $79,469. Expected gaps: $25,835; $21,511; $9,839; and -$9,469.</li></ul>",
            "RESOURCES": '<p><a href="https://livingwage.mit.edu/">MIT Living Wage Calculator</a>, one adult/no children, updated Feb. 15, 2026. The $70,000 offer is a fictional classroom control.</p>',
            "SUPPORT": "<p>The two-page landscape packet puts the calculation table on page 1 and gives the recommendation full-width space on page 2. Calculator, typed response, dictation, and paper are allowed.</p>",
            "FALLBACK": "<p>All numbers are fixed; no live search or personal relocation plan is required.</p>",
        },
        4: {
            "TITLE": "Paying for Education and Training",
            "SUBTITLE": "50 minutes · TEKS d(3)(C)",
            "ALERT": "<strong>Financial-aid literacy, not application completion.</strong> Do not collect or enter SSNs, tax data, family income, immigration information, FSA IDs, bank details, or signatures.",
            "PREP": f'<ul><li><strong>Default:</strong> one device per student, one projector, zero prints. Post {link(files["AID"]["id"], "the three-page guide")} and unpublished unlimited-retry Quiz.</li><li><strong>Paper:</strong> print one three-page guide per student; students mark the same guide and place it in one collection tray. Keep the paper five-question check available only for a Canvas outage.</li><li>Students work individually after one brief table sort with a partner. Open current Federal Student Aid and TEA sources; use fictional cases only.</li></ul>',
            "EVIDENCE": "<p>Formative seven-method sort, two fictional decisions, three claim repairs, five-step sequence, and Quiz feedback.</p>",
            "MODEL": '<div style="border:1px solid #bdd6cb;border-radius:8px;background:#f2f8f5;padding:12px 16px"><p><strong>Taylor model:</strong> investigate scholarships and grants first because both may reduce cost without repayment when conditions are met; verify each deadline, eligibility rule, and aid offer.</p><p><strong>Jordan model:</strong> verify a current Registered Apprenticeship opening, age/eligibility, wage, schedule, sponsor, and classroom requirement; compare it with a technical-college route.</p><p><strong>Non-example:</strong> “FAFSA is a loan every Texas seventh grader must complete.” FAFSA is an application, and the Texas completion/opt-out requirement applies in grade 12.</p></div>',
            "FLOW": flow(c, "Warm-up · 5", "Reduce, earn, or borrow?") + flow("#4c8b38", "Method sort/model · 10", "Aid and training options.") + flow("#8a4f2b", "Two cases · 11", "First step and verification.") + flow("#d39b22", "Claims/sequence · 14", "Repair before deciding.") + flow(c, "Quiz/submit · 10", "Feedback, exit, material return."),
            "MONITOR": "<ul><li><strong>Minute 13:</strong> every student has one reduce-cost method, one earn-through-work method, and one borrowed-money method. If categories blur, sort grant/work-study/loan together.</li><li><strong>Minute 25:</strong> both fictional cases name a first step and a condition to verify. Redirect any family or immigration disclosure to the fictional case.</li><li><strong>Minute 37:</strong> all three claims are repaired and the sequence begins with research/application, not accepting or borrowing.</li><li><strong>Quiz gate at minute 40:</strong> take one attempt, read feedback, and retry only missed ideas. If Canvas fails, use the guide orally or on paper; do not create an account.</li><li><strong>Trim/recovery:</strong> cut partner reporting and extra retries. Protect the guide, one feedback pass, exit, submission, and device/material return.</li><li>Key: federal categories are grants, work-study, and loans; scholarships are broader aid. Texas public-school seniors in grade 12 may satisfy the current requirement through FAFSA, TASFA when applicable, or an authorized signed opt-out.</li></ul>",
            "RESOURCES": '<p><a href="https://studentaid.gov/articles/fafsa-student-steps/">Federal Student Aid FAFSA steps</a> · <a href="https://studentaid.gov/articles/fafsa-submission-summary/">FAFSA Submission Summary</a> · <a href="https://tea.texas.gov/student-readiness-and-high-school/college-career-and-military-prep/financial-aid-requirement">TEA financial-aid requirement</a> · <a href="https://www.apprenticeship.gov/career-seekers">Apprenticeship.gov</a>.</p>',
            "SUPPORT": "<p>Three pages keep the reference table, two fictional cases, and claim-repair sequence separate. Word banks and complete frames sit beside each response job. Quiz feedback can be read aloud.</p>",
            "FALLBACK": "<p>The packet works offline. No real FAFSA, TASFA, scholarship, loan, provider, or apprenticeship application is completed.</p>",
        },
        5: {
            "TITLE": "Personal Budget and Career Evidence Portfolio",
            "SUBTITLE": "50 minutes · TEKS d(5)(D), d(5)(E)",
            "ALERT": "<strong>Major 2 in the 5SW assessment map.</strong> Keep the assignment unpublished. Career preference, family finances, and a positive or negative screening result are not scored.",
            "PREP": f'<ul><li><strong>Default:</strong> one device and calculator per student (a calculator may be shared by a pair), one projector, zero prints. Post {link(files["PORTFOLIO"]["id"], "the four-page portfolio")}, {link(files["RUBRIC"]["id"], "the two-page rubric")}, and private Assignment.</li><li><strong>Paper:</strong> print one four-page landscape portfolio and one two-page rubric per student; set one collection tray by the door.</li><li>Students complete and submit individual evidence. Keep the fixed three-career fallback and supplied model visible.</li><li>Do not require students to attach Days 1-4 or reopen those formative submissions to score this Major.</li></ul>',
            "EVIDENCE": "<p><strong>Major 2:</strong> one self-contained portfolio with three comparable career records, evidence-based recommendation and tradeoff, three salary-minus-target screens, revised fictional monthly result, source limitation, and revision.</p>",
            "MODEL": '<div style="border:1px solid #bdd6cb;border-radius:8px;background:#f2f8f5;padding:12px 16px"><p><strong>Complete model strip:</strong> “I currently recommend Civil Engineer. The May 2024 U.S. median is $99,590, and a bachelor\'s degree is the typical entry preparation. The tradeoff is the time and cost of that education. $99,590 - $48,489 = $51,101 above the screening target. That is not take-home pay and does not prove a local opening or fit. In my fictional $4,200 monthly plan, I would keep emergency savings and reduce wants by $100 until I verify local pay and education cost.”</p><p><strong>Non-example:</strong> rank one Xello local range beside two national medians, choose the largest number, and attach Days 1-4 again.</p></div>',
            "FLOW": flow(c, "Gate/model · 6", "Comparable basis and complete evidence strip.") + flow("#4c8b38", "Career records · 16", "Three careers, same basis.") + flow("#8a4f2b", "Recommend/tradeoff · 8", "Two facts and one cost.") + flow("#d39b22", "Screen/revise · 13", "Three calculations, monthly result, audit.") + flow(c, "Submit/cleanup · 7", "Rubric check and one private submission."),
            "MONITOR": "<ul><li><strong>Minute 8:</strong> all three career records use the same geography, date, and wage measure. Students with mixed Xello labels switch to the fixed card before continuing.</li><li><strong>Minute 22:</strong> three careers, salaries, preparation facts, and evidence limits are present.</li><li><strong>Minute 32:</strong> recommendation includes two exact facts and an honest tradeoff; the highest salary is not required.</li><li><strong>Minute 42:</strong> three salary-minus-target calculations, revised monthly result, correction, and remaining limit are visible. Students behind use the fixed fallback and labeled bullets; do not cut a rubric criterion.</li><li><strong>Trim/recovery:</strong> cut warm-up sharing and decorative formatting. Protect every rubric job, the final self-check, private submission, and calculator/device return. If incomplete at minute 47, save the same portfolio and schedule recovery; do not add homework or resubmit Days 1-4.</li><li>Fixed May 2024 U.S. medians: Architects $96,690; Civil Engineers $99,590; Electricians $62,350. Dallas annual before-tax target: $48,489. Expected differences: $48,201; $51,101; $13,861.</li></ul>",
            "RESOURCES": '<p><a href="https://www.bls.gov/ooh/architecture-and-engineering/architects.htm">BLS Architects</a> · <a href="https://www.bls.gov/ooh/architecture-and-engineering/civil-engineers.htm">BLS Civil Engineers</a> · <a href="https://www.bls.gov/ooh/construction-and-extraction/electricians.htm">BLS Electricians</a> · <a href="https://livingwage.mit.edu/counties/48113">MIT Dallas County</a>.</p>',
            "SUPPORT": "<p>The four-page landscape portfolio gives each career a labeled evidence block, then separates comparison from budget screening. Word banks and complete frames sit beside the response. Accept annotation, upload, typed labeled responses, speech-to-text within the document or text route, or the labeled paper portfolio.</p>",
            "FALLBACK": "<p>Use fixed career evidence when Xello is unavailable or labels are not comparable. No public Discussion, private profile screenshot, family budget, prior-packet attachment, or H&amp;L favorite is required.</p>",
        },
    }


async def main():
    preflight()
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        # Fail closed before the first Canvas mutation. The assessment-map assignment
        # must already exist as exactly one 100-point Major in the correct group.
        mapped_major, major_group = await mapped_major_assignment(client)
        module = await ensure_module(client)
        support_path = "course files/CCR Materials/5SW/Wk5"
        support_folder = await common.ensure_folder(client, support_path)
        files = {key: await common.upload(client, ROOT / "docs/resources/worksheets" / name, support_path) for key, name in WORKSHEET_FILES.items()}
        support_folder = await common.lock_folder_files(client, support_folder)
        visual_path = "course files/CCR Materials/5SW/Wk5/Locked Licensed Visuals"
        visual_folder = await common.ensure_folder(client, visual_path)
        visuals = {key: await common.upload(client, ASSETS / name, visual_path) for key, name in VISUAL_FILES.items()}
        visual_folder = await common.lock_folder_files(client, visual_folder)
        quiz = await upsert_quiz(client)
        attachments = {1:"SOURCE",2:"BUDGET",3:"LOCATION"}
        assignments = {}
        for day in range(1, 4):
            assignments[day] = await upsert_practice_assignment(
                client,
                DAY_TITLES[day],
                "<p>Complete privately by annotation, upload, typed labeled responses, or paper. Do not disclose real family financial information. This practice is worth 0 points, omitted from the final grade, and unpublished.</p>",
                files[attachments[day]]["id"],
            )
        assignments[5] = await require_major_assignment(
            client,
            mapped_major,
            major_group,
            "<p>Submit the private, self-contained four-page portfolio by annotation, upload, or typed labeled response; the teacher may collect the same labeled paper portfolio. This is the mapped 100-point Major 2. Keep it unpublished for teacher review.</p>",
            files["PORTFOLIO"]["id"],
        )
        urls = {1:f"/courses/{COURSE_ID}/assignments/{assignments[1]['id']}",2:f"/courses/{COURSE_ID}/assignments/{assignments[2]['id']}",3:f"/courses/{COURSE_ID}/assignments/{assignments[3]['id']}",4:f"/courses/{COURSE_ID}/quizzes/{quiz['id']}",5:f"/courses/{COURSE_ID}/assignments/{assignments[5]['id']}"}
        student, teacher = student_content(files, visuals, urls), teacher_content(files)
        names = {1:"Salary Source and Lifestyle Target",2:"Build a Dallas County Personal Budget",3:"Compare the Same Offer Across Locations",4:"Paying for Education and Training",5:"Personal Budget and Career Evidence Portfolio"}
        pages, order = {}, []
        interactions = {1:("Assignment",assignments[1]["id"],DAY_TITLES[1]),2:("Assignment",assignments[2]["id"],DAY_TITLES[2]),3:("Assignment",assignments[3]["id"],DAY_TITLES[3]),4:("Quiz",quiz["id"],DAY_TITLES[4]),5:("Assignment",assignments[5]["id"],DAY_TITLES[5])}
        for day in range(1, 6):
            header_title = f"Day {day} · {names[day]}"
            header = await prior.upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 5SW Wk5 Day {day} - {names[day]}"
            student_page = await common.upsert_page(client, student_title, common.render("5sw-wk5-student.html", {"COURSE_ID":COURSE_ID,"DAY":day,**CONTRACTS[day],**student[day]}))
            teacher_title = f"TEACHER: 5SW Wk5 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(client, teacher_title, common.render("5sw-wk5-teacher.html", {"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student_page["url"],**CONTRACTS[day],**teacher[day]}))
            await prior.upsert_item(client,module["id"],"Page",teacher_page["url"],teacher_title)
            await prior.upsert_item(client,module["id"],"Page",student_page["url"],student_title)
            kind,key,title = interactions[day]
            await prior.upsert_item(client,module["id"],kind,key,title)
            order.extend([("Page",teacher_page["url"],teacher_title),("Page",student_page["url"],student_title),(kind,key,title)])
            pages[day] = {"teacher":teacher_page,"student":student_page}
        final_items = await prior.reconcile_module_items(client, module["id"], order)
        if len(final_items) != 20:
            raise RuntimeError(f"Expected 20 exact Week 5 module items; found {len(final_items)}")
        module = await common.api(client,"GET",f"/courses/{COURSE_ID}/modules/{module['id']}")
        modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
        if module.get("published") or len([entry for entry in modules if entry.get("name") == MODULE_NAME]) != 1:
            raise RuntimeError(f"Final module invariant failed: published={module.get('published')}")
        for day, pair in pages.items():
            for kind, page in pair.items():
                fresh = await common.api(client, "GET", f"/courses/{COURSE_ID}/pages/{page['url']}")
                if fresh.get("published"):
                    raise RuntimeError(f"Day {day} {kind} page is published")
                pair[kind] = fresh
        for day in range(1, 4):
            assignments[day] = await assert_annotation_assignment(client, assignments[day], files[attachments[day]]["id"])
        assignments[5] = await assert_annotation_assignment(client, assignments[5], files["PORTFOLIO"]["id"], mapped=True)
        if (
            assignments[5].get("assignment_group_id") != major_group["id"]
            or RUBRIC_NOTE_MARKER not in (assignments[5].get("description") or "")
        ):
            raise RuntimeError(f"Final Major group/rubric invariant failed for {DAY_TITLES[5]!r}")
        quiz = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
        if quiz.get("published") or quiz.get("quiz_type") != "practice_quiz" or int(quiz.get("allowed_attempts") or 0) != -1:
            raise RuntimeError(f"Final Quiz invariant failed for {DAY_TITLES[4]!r}")
        support_folder = await common.lock_folder_files(client, support_folder)
        visual_folder = await common.lock_folder_files(client, visual_folder)
        print(json.dumps({"module":{"id":module["id"],"published":module["published"]},"support_folder":{"id":support_folder["id"],"locked":support_folder["locked"]},"visual_folder":{"id":visual_folder["id"],"locked":visual_folder["locked"]},"files":{key:value["id"] for key,value in files.items()},"visuals":{key:value["id"] for key,value in visuals.items()},"quiz":{"id":quiz["id"],"published":quiz.get("published")},"assignments":{str(day):{"id":value["id"],"published":value.get("published"),"points":value.get("points_possible"),"group_id":value.get("assignment_group_id"),"submission_types":value.get("submission_types")} for day,value in assignments.items()},"pages":{str(day):{kind:{"url":value["url"],"published":value["published"]} for kind,value in pair.items()} for day,pair in pages.items()},"items":[{"position":item["position"],"type":item["type"],"title":item["title"]} for item in final_items]},indent=2))


if __name__ == "__main__":
    asyncio.run(main())
