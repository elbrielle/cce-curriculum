"""Build the unpublished 4SW Week 2 counseling-ready course-planning module."""

import asyncio
import json
import sys

import httpx

import build_4sw_wk1 as common


BASE = common.BASE
COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/4sw/wk2"
MODULE_NAME = "4SW Wk2: Build a Counseling-Ready High School Plan"
QUIZ_TITLE = "PRACTICE: What Does This Assessment Affect?"
ANNOTATION_TITLE = "DRAFT: Four-Year Course Plan Annotation"
PLAN_TITLE = "DRAFT: Individual High School and Career Plan"


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    found = next((entry for entry in modules if entry["name"] == MODULE_NAME), None)
    data = {"module[published]": "false"}
    if found:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data=data)
    data["module[name]"] = MODULE_NAME
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


QUESTIONS = [
    (
        "Q1 - End-of-course assessment",
        "Which assessment result is most directly connected to Texas high school graduation requirements?",
        "A required STAAR End-of-Course assessment, subject to current state rules and approved alternatives.",
        ["The PSAT only.", "Any industry certification exam.", "The ASVAB only."],
        "Correct. End-of-Course requirements are part of the Texas graduation framework.",
        "PSAT, ASVAB, and industry certifications serve different purposes. Check current TEA graduation rules.",
    ),
    (
        "Q2 - College placement",
        "A student has been admitted to a Texas college but needs to know whether they can begin in college-level reading and math. What should the student verify?",
        "The institution's current college-readiness and placement rules, including TSIA exemptions or alternatives.",
        ["Only the ASVAB score.", "Only the student's industry certification.", "Whether the student passed an AP art course."],
        "Correct. TSIA and approved exemptions or alternatives can affect placement, not every student's admission decision.",
        "Admission, placement, military qualification, and credentialing are different decisions.",
    ),
    (
        "Q3 - Military options",
        "Which assessment can support career exploration and may affect military qualification and job options during an enlistment process?",
        "ASVAB",
        ["TSIA", "AP exam", "STAAR English I EOC only"],
        "Correct. The ASVAB has a distinct career-exploration and military role.",
        "The other assessments do not replace the ASVAB in an enlistment process.",
    ),
    (
        "Q4 - Industry certification",
        "What is the safest planning claim about an industry certification assessment?",
        "It measures requirements for a specific credential and does not replace every college or graduation assessment.",
        ["It is a universal college entrance exam.", "It guarantees a job in the field.", "Every CTE student takes the same certification."],
        "Correct. Keep the credential name, eligibility, and current requirements attached to the claim.",
        "A certification is specific. It does not guarantee employment or replace unrelated assessments.",
    ),
]


async def upsert_quiz(client):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    quiz = next((entry for entry in quizzes if entry.get("title") == QUIZ_TITLE), None)
    data = {
        "quiz[title]": QUIZ_TITLE,
        "quiz[description]": "<p>Ungraded practice. Retry and use the feedback to separate graduation, admission, placement, career-exploration, military, and credential decisions.</p>",
        "quiz[quiz_type]": "practice_quiz",
        "quiz[published]": "false",
        "quiz[allowed_attempts]": "-1",
        "quiz[show_correct_answers]": "true",
        "quiz[shuffle_answers]": "false",
    }
    path = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}" if quiz else f"/courses/{COURSE_ID}/quizzes"
    quiz = await common.api(client, "PUT" if quiz else "POST", path, data=data)
    existing = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    for position, (name, text, correct, wrong, correct_comment, incorrect_comment) in enumerate(QUESTIONS, 1):
        found = next((entry for entry in existing if entry.get("question_name") == name), None)
        payload = {
            "question": {
                "question_name": name,
                "question_text": text,
                "question_type": "multiple_choice_question",
                "position": position,
                "points_possible": 1,
                "correct_comments": correct_comment,
                "incorrect_comments": incorrect_comment,
                "answers": [{"answer_text": correct, "answer_weight": 100}]
                + [{"answer_text": answer, "answer_weight": 0} for answer in wrong],
            }
        }
        question_path = (
            f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{found['id']}"
            if found
            else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        )
        await common.api(client, "PUT" if found else "POST", question_path, json=payload)
    return await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


async def upsert_item(client, module_id, kind, key, title):
    items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    found = next(
        (
            item
            for item in items
            if (kind == "SubHeader" and item.get("title") == title)
            or (kind == "Page" and item.get("page_url") == key)
            or (kind in ("Assignment", "Quiz") and item.get("content_id") == key)
        ),
        None,
    )
    if found:
        return await common.api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{found['id']}",
            data={"module_item[title]": title},
        )
    data = {"module_item[type]": kind, "module_item[title]": title}
    if kind == "Page":
        data["module_item[page_url]"] = key
    elif kind in ("Assignment", "Quiz"):
        data["module_item[content_id]"] = key
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data=data)


def image_tag(file_id, alt):
    return (
        f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" '
        'style="display:block;width:100%;max-width:700px;height:auto;margin:14px auto;border:1px solid #ddd" '
        f'data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'
    )


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        module = await ensure_module(client)
        support_path = "course files/CCR Materials/4SW/Wk2"
        support_folder = await common.ensure_folder(client, support_path)
        worksheet_names = {
            "TRANSITION": "4sw-wk2-transition-and-assessment-decisions.pdf",
            "COURSE": "4sw-wk2-four-year-course-plan-draft.pdf",
            "CREDIT": "4sw-wk2-college-credit-and-family-conversation.pdf",
            "SMART": "4sw-wk2-smart-experience-action-plan.pdf",
            "PLAN": "4sw-wk2-individual-high-school-career-plan.pdf",
            "RUBRIC": "4sw-wk2-high-school-career-plan-rubric.pdf",
        }
        files = {
            key: await common.upload(client, ROOT / "docs/resources/worksheets" / name, support_path)
            for key, name in worksheet_names.items()
        }

        selected = {
            2: ["fyf-rung7-classes-to-consider.jpg", "fyf-rung7-plan-in-action.jpg"],
            4: ["fyf-rung6-smart-goals.jpg", "fyf-rung6-goal-check.jpg"],
            5: ["fyf-rung7-opportunities.jpg"],
        }
        visuals, visual_folders = {}, {}
        for day, names in selected.items():
            folder_path = f"course files/CCR Materials/4SW/Wk2/Day {day} Visuals"
            visual_folders[day] = await common.ensure_folder(client, folder_path)
            visuals[day] = {
                name: await common.upload(client, ASSETS / f"day{day}" / name, folder_path)
                for name in names
            }

        quiz = await upsert_quiz(client)
        annotation = await common.upsert_assignment(
            client,
            ANNOTATION_TITLE,
            "<p>Complete the counseling-ready four-year draft by Canvas annotation, file upload, text entry, or paper. Do not submit official course requests. Mark uncertain entries for counselor verification.</p>",
            ["student_annotation", "online_upload", "online_text_entry"],
            files["COURSE"]["id"],
        )
        plan_assignment = await common.upsert_assignment(
            client,
            PLAN_TITLE,
            "<p>Submit the private Individual High School and Career Plan by file upload, text entry, or media recording. The student-visible 16-point rubric is attached in the guide. The Assignment remains unpublished and ungraded until the Major assignment group and 40/60 weighting are verified.</p>",
            ["online_upload", "online_text_entry", "media_recording"],
        )
        quiz_url = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        annotation_url = f"/courses/{COURSE_ID}/assignments/{annotation['id']}"
        plan_url = f"/courses/{COURSE_ID}/assignments/{plan_assignment['id']}"

        media = {
            1: "",
            2: image_tag(
                visuals[2]["fyf-rung7-classes-to-consider.jpg"]["id"],
                "Find Your Future Rung 7 blank table for classes and how each class may support a goal",
            )
            + image_tag(
                visuals[2]["fyf-rung7-plan-in-action.jpg"]["id"],
                "Find Your Future Rung 7 prompts for local opportunities and actions during high school",
            ),
            3: "",
            4: image_tag(
                visuals[4]["fyf-rung6-smart-goals.jpg"]["id"],
                "Find Your Future Rung 6 SMART goal definitions and short-term goal form",
            )
            + image_tag(
                visuals[4]["fyf-rung6-goal-check.jpg"]["id"],
                "Find Your Future Rung 6 medium-term and long-term goal forms with realism and challenge check",
            ),
            5: image_tag(
                visuals[5]["fyf-rung7-opportunities.jpg"]["id"],
                "Find Your Future Rung 7 tables for clubs, organizations, activities, programs, and opportunities",
            ),
        }

        file_link = common.file_link
        step = common.step
        flow = common.flow
        student = {
            1: {
                "TITLE": "Graduation and Assessment Decisions",
                "PURPOSE": "Separate graduation, admission, placement, career-exploration, military, and credential decisions before you plan.",
                "TODAY": "<ul><li>read the current Texas graduation framework;</li><li>identify one endorsement question;</li><li>analyze two assessment scenarios.</li></ul>",
                "READY": f'<p>Open {file_link(files["TRANSITION"]["id"], "the Transition and Assessment Decisions packet")}. Your teacher will also post the current TEA Graduation Toolkit.</p>',
                "STEPS": step(1, "Record the two planning levels", "<p>Write the 22-credit foundation baseline and what the 26-credit endorsement plan adds. Keep the source and year.</p>")
                + step(2, "Write a counseling-ready endorsement statement", "<p>Name one possible endorsement and one question. Do not write “always” unless a current source proves it.</p>")
                + step(3, "Match the decision, not just the test name", "<p>For each scenario, name what the result may affect, a next step, and one fact to verify.</p>")
                + step(4, "Check your thinking", f'<p><a href="{quiz_url}">Open the four-question practice check</a>. Retry and use the feedback.</p>'),
                "EXIT": "<p>Correct Jordan's claim that the SAT, TSIA, and an industry certification are all the same kind of test.</p>",
                "DONE": "<ul><li>graduation framework and source;</li><li>possible endorsement plus question;</li><li>assessment purpose table;</li><li>two scenario decisions;</li><li>one current verification source or person.</li></ul>",
                "SUPPORT": "<p>graduation = graduación · admission = admisión · placement = colocación · credential = credencial. Sort the six purpose cards before writing.</p>",
                "FALLBACK": "<p>The packet and TEA source card are the complete route. If the live page is unavailable, use the dated card and keep your verification question.</p>",
            },
            2: {
                "TITLE": "Four-Year Course Plan Draft",
                "PURPOSE": "Build a source-checked draft for a future counselor conversation, not an official schedule.",
                "TODAY": "<ul><li>find current course information;</li><li>draft Grades 9-12;</li><li>explain one prerequisite chain;</li><li>keep a backup and counselor questions.</li></ul>",
                "READY": f'<p>Open {file_link(files["COURSE"]["id"], "the five-page course-plan draft")} or <a href="{annotation_url}">open the Canvas annotation activity</a>. Use the current Irving ISD coursebook posted by your teacher.</p>',
                "STEPS": step(1, "Keep the source with the course", "<p>Record the exact title, grade level, prerequisite, source, and access date.</p>")
                + step(2, "Draft one year at a time", "<p>Complete Grades 9-12. A blank marked for verification is better than an invented course.</p>")
                + step(3, "Explain the sequence", "<p>Show one prerequisite chain and why an earlier choice matters later.</p>")
                + step(4, "Protect the goal", "<p>Add a backup and two counselor questions about access, application, transportation, capacity, or sequence.</p>"),
                "EXIT": "<p>What do you do when a course title is current but its grade level, campus, or prerequisite is unclear?</p>",
                "DONE": "<ul><li>source and access date;</li><li>four-year draft;</li><li>one prerequisite chain;</li><li>one item marked for verification;</li><li>one backup;</li><li>two counselor questions.</li></ul>",
                "SUPPORT": "<p>prerequisite = requisito previo · verify = verificar · backup = alternativa. Use the fictional model to see the structure, not to copy course names.</p>",
                "FALLBACK": "<p>Use the dated course cards and paper or text-entry route. Do not submit course requests. The official Xello tasks wait for the counseling window.</p>",
            },
            3: {
                "TITLE": "College Credit and Plan Conversation",
                "PURPOSE": "Compare AP and dual credit, then test your plan with a question or reflection.",
                "TODAY": "<ul><li>compare AP and dual credit;</li><li>document one current local option;</li><li>explain one part of your plan;</li><li>record what you will keep, change, or verify.</li></ul>",
                "READY": f'<p>Open {file_link(files["CREDIT"]["id"], "the College Credit and Conversation packet")}. Your teacher will post the current TEA AP, dual-credit, and Irving coursebook pages.</p>',
                "STEPS": step(1, "Compare the routes", "<p>AP uses an exam and receiving-college policy. Dual credit is a college course that gives high school and college credit after successful completion.</p>")
                + step(2, "Document one current option", "<p>Keep the exact name, type, grade level, prerequisite, possible credit, source/date, and one limitation or question.</p>")
                + step(3, "Choose an equal conversation route", "<p>Use a family member, trusted adult, counselor, teacher, private writing, or private audio. A signature is not required.</p>")
                + step(4, "Revise honestly", "<p>Record one part you will keep, change, or verify because of the question or reflection.</p>"),
                "EXIT": "<p>Add one accurate fact to AP only, both, and dual credit only. Then write one verification question.</p>",
                "DONE": "<ul><li>accurate source comparison;</li><li>one current local option;</li><li>one limitation or question;</li><li>equal conversation or private route;</li><li>one keep, change, or verify decision.</li></ul>",
                "SUPPORT": "<p>exam score = puntaje de examen · college course = curso universitario · transfer = transferencia · eligibility = elegibilidad. Rehearse with the two sentence frames before writing.</p>",
                "FALLBACK": "<p>Use the dated source cards and complete the private written reflection. No family signature, partner, or live search is required.</p>",
            },
            4: {
                "TITLE": "SMART Experience Action Plan",
                "PURPOSE": "Turn one possible experience into a realistic action with support and a backup.",
                "TODAY": "<ul><li>evaluate one experience;</li><li>write all five SMART parts;</li><li>check access, support, obstacle, and backup;</li><li>choose one action within seven days.</li></ul>",
                "READY": f'<p>Open {file_link(files["SMART"]["id"], "the three-page SMART Experience Action Plan")}.</p>',
                "STEPS": step(1, "Choose a real or clearly unverified experience", "<p>Use a club, activity, service, project, responsibility, work, job-shadow, or portfolio option. Do not contact an unfamiliar adult or workplace.</p>")
                + step(2, "Name the value", "<p>Record the skill it builds and how the same skill transfers to a second career.</p>")
                + step(3, "Write the five SMART parts", "<p>Specific, Measurable, Achievable, Relevant, and Time-Bound.</p>")
                + step(4, "Protect the plan", "<p>Add support, likely obstacle, backup, and one first action within seven days.</p>"),
                "EXIT": "<p>Rank measure, access, time, support, and backup. Revise the weakest part now.</p>",
                "DONE": "<ul><li>experience and source;</li><li>skill plus second-career transfer;</li><li>all five SMART parts;</li><li>support and obstacle;</li><li>backup;</li><li>seven-day action.</li></ul>",
                "SUPPORT": "<p>specific = específico · measurable = medible · achievable = alcanzable · relevant = pertinente · time-bound = con fecha. Use “By [date], I will...” and “If [obstacle], I will...”</p>",
                "FALLBACK": "<p>The PDF and embedded workbook pages are the full independent route. Use an independent project or current responsibility if a club or program cannot be verified.</p>",
            },
            5: {
                "TITLE": "Individual High School and Career Plan",
                "PURPOSE": "Combine your evidence into a current direction, course and preparation plan, backup, and revision rule.",
                "TODAY": "<ul><li>gather Days 1-4 evidence;</li><li>write the individual plan;</li><li>self-score with the rubric;</li><li>revise and submit privately.</li></ul>",
                "READY": f'<p>Open {file_link(files["PLAN"]["id"], "the four-page Individual Plan")} and {file_link(files["RUBRIC"]["id"], "the two-page 16-point rubric")}.</p>',
                "STEPS": step(1, "Direction and self-evidence", "<p>Name a current direction, two pieces of self-evidence, and evidence that would make you reconsider.</p>")
                + step(2, "Course and preparation evidence", "<p>Bring forward the four-year draft, prerequisite chain, one verification item, preparation after high school, and one advanced or college-credit option.</p>")
                + step(3, "Action and revision", "<p>Write actions for seven days, the next counseling meeting, and Grade 9. Add support, backup, and a revision rule.</p>")
                + step(4, "Self-score and submit", f'<p>Circle one rubric level in each row, revise one weak section, then <a href="{plan_url}">submit the private plan</a> or hand in paper.</p>'),
                "EXIT": "<p>List three evidence-supported parts, two counseling questions, and one condition that would make you revise.</p>",
                "DONE": "<ul><li>all seven plan sections;</li><li>source/date labels kept;</li><li>backup and revision rule;</li><li>student-visible rubric check;</li><li>one visible revision;</li><li>private submission.</li></ul>",
                "SUPPORT": "<p>direction = dirección · evidence = evidencia · revision = revisión. Use “My current direction is... because...” and “I will revise this plan if...” Text, speech-to-text, and media answer the same jobs.</p>",
                "FALLBACK": "<p>Use the matching Student Guide and dated source cards to rebuild a missing section. Canvas failure means paper or later upload without penalty. This is not an official course request.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Graduation and Assessment Decisions",
                "SUBTITLE": "50 minutes · TEKS d(3)(A), d(3)(E)",
                "ALERT": "<strong>Use the current TEA framework.</strong> The foundation baseline is 22 credits; the endorsement plan shown in the 2025 toolkit totals 26. Do not teach the stale 4-math, 4-science, 4-social foundation list.",
                "PREP": f'<ul><li>Post {file_link(files["TRANSITION"]["id"], "the transition packet")} and the <a href="https://tea.texas.gov/about-tea/newsroom/brochures/tea-graduation-toolkit-2025.pdf">TEA 2025 Graduation Toolkit</a>.</li><li>Open the unpublished four-question practice Quiz.</li><li>Prepare six assessment-purpose cards.</li></ul>',
                "EVIDENCE": "<p>Current graduation framework, possible endorsement plus verification question, purpose table, two assessment scenarios, and one source/person to verify. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "High school question and likely decision.")
                + flow("#4a9d2f", "Graduation framework · 12", "Foundation versus endorsement plan.")
                + flow("#1f617a", "Endorsement question · 10", "Possible connection without an always claim.")
                + flow("#e3ad19", "Assessment scenarios · 18", "Decision, next step, and verification.")
                + flow("#1f617a", "Exit · 5", "Correct the all-tests-are-the-same misconception."),
                "MONITOR": "<p>Key boundary: EOC for graduation rules; PSAT for practice/feedback and some scholarship programs; SAT/ACT when admission or scholarships use them; TSIA for college readiness/placement with exemptions or alternatives; ASVAB for exploration and military qualification/job options; certification assessments for a named credential. One test does not plan the full route.</p>",
                "RESOURCES": "<p>The TEA Graduation Toolkit and current institutional policies control. The practice Quiz provides immediate feedback and item-level misconception data.</p>",
                "SUPPORT": "<p>Use purpose cards and icons, read one scenario at a time, and allow oral rehearsal. The packet gives separate full-width lines for each scenario job.</p>",
                "FALLBACK": "<p>The dated TEA source card and printed packet are complete. Do not require live test-registration sites or private scores.</p>",
            },
            2: {
                "TITLE": "Four-Year Course Plan Draft",
                "SUBTITLE": "50 minutes · TEKS d(8)(B), d(3)(A)",
                "ALERT": "<strong>Draft, not requests.</strong> Do not open Xello Submit course requests or parent approval until counselors confirm the local window and process.",
                "PREP": f'<ul><li>Post {file_link(files["COURSE"]["id"], "the five-page draft")} and the <a href="https://www.irvingisd.net/departments-services/curriculum-and-instruction/middle-school-and-high-school-course-descriptions">current Irving coursebook</a>.</li><li>Open the unpublished annotation Assignment.</li><li>Prepare dated course cards and one fictional model.</li></ul>',
                "EVIDENCE": "<p>Four-year draft, current source/date, one prerequisite chain, one verification label, backup, and two counselor questions. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "What prerequisite errors can cause.")
                + flow("#4a9d2f", "Source model · 10", "Exact title, grade, prerequisite, question, backup.")
                + flow("#1f617a", "Draft · 25", "Grades 9-12 and sequence check.")
                + flow("#e3ad19", "Audit · 5", "Source, sequence, verification.")
                + flow("#1f617a", "Exit · 5", "Branch when a detail is unclear."),
                "MONITOR": "<p>Lap 1 checks title/source/date. Lap 2 checks the prerequisite chain. Lap 3 checks verification labels, backup, and questions. Do not grade a guessed course as more complete than an honest unknown.</p>",
                "RESOURCES": "<p>Authenticated Xello configuration: 4-year course plan 30 min; Make plans 30 min/add at least one plan; Submit course requests 20 min/Grade 8 only; parent approval 15 min/current due May 1, 2027. These remain counselor-window tasks.</p>",
                "SUPPORT": "<p>Use a fictional model and complete one Grade 9 row together. Canvas annotation, upload, text, and paper are equal; the five-page packet preserves writing space.</p>",
                "FALLBACK": "<p>Dated course cards replace live search. Platform failure never authorizes an invented course or false Xello completion.</p>",
            },
            3: {
                "TITLE": "College Credit and Plan Conversation",
                "SUBTITLE": "50 minutes · TEKS d(3)(B), d(3)(D)",
                "ALERT": "<strong>No automatic credit or free-course promise.</strong> AP depends on exam performance and receiving-college policy. Dual credit has eligibility, completion, transfer, cost, and local-availability questions.",
                "PREP": f'<ul><li>Post {file_link(files["CREDIT"]["id"], "the college-credit packet")}.</li><li>Open current <a href="https://tea.texas.gov/student-readiness-and-high-school/college-career-and-military-prep/advanced-placement">TEA AP</a>, <a href="https://tea.texas.gov/student-readiness-and-high-school/college-career-and-military-prep/dual-credit">TEA Dual Credit</a>, and Irving coursebook pages.</li><li>Prepare one dated local option card.</li></ul>',
                "EVIDENCE": "<p>Accurate comparison, one current local option with source/date, limitation or question, and one keep/change/verify reflection. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Question before choosing college-credit work.")
                + flow("#4a9d2f", "Compare · 12", "AP and dual-credit evidence.")
                + flow("#1f617a", "Current option · 15", "Name, type, eligibility, possible credit, limitation.")
                + flow("#e3ad19", "Plan conversation · 13", "Equal adult or private route.")
                + flow("#1f617a", "Exit · 5", "AP-only, both, dual-only, question."),
                "MONITOR": "<p>Full response keeps source/date and a limitation. FAST may support eligible students at participating institutions; it does not make every dual-credit course free. Industry certification is not college credit without a current articulation agreement.</p>",
                "RESOURCES": "<p>Use TEA for the route definitions and current Irving sources for local availability. A receiving college or counselor answers transfer and operational questions.</p>",
                "SUPPORT": "<p>Use a two-column source card, oral rehearsal, and the packet's separate writing areas. Family, trusted adult, counselor, teacher, private writing, and private audio are equal.</p>",
                "FALLBACK": "<p>No signature is required. The dated source card and private reflection route complete the lesson without a partner or family conversation.</p>",
            },
            4: {
                "TITLE": "SMART Experience Action Plan",
                "SUBTITLE": "50 minutes · TEKS d(3)(F), d(8)(C)",
                "ALERT": "<strong>Verify access before naming an opportunity.</strong> Do not promise a CTSO chapter, internship, job shadow, transportation route, or adult contact from workbook context alone.",
                "PREP": f'<ul><li>Post {file_link(files["SMART"]["id"], "the SMART Action Plan")}.</li><li>Project FYF pp. 292-293.</li><li>Prepare one current campus option, one independent project, and one service or responsibility-based option.</li></ul>',
                "EVIDENCE": "<p>Evaluated experience, transferable skill, all five SMART parts, access check, support, obstacle, backup, and seven-day action. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Experience and skill.")
                + flow("#4a9d2f", "SMART model · 8", "Weak versus source-checked goal.")
                + flow("#1f617a", "Evaluate experience · 10", "Skill, second career, access, alternative.")
                + flow("#e3ad19", "Write plan · 17", "Five SMART parts and protection.")
                + flow("#4a9d2f", "Self-check · 5", "Underline each part.")
                + flow("#1f617a", "Exit · 5", "Rank and revise the weak part."),
                "MONITOR": "<p>Lap 1 checks real or clearly unverified. Lap 2 checks the five SMART parts. Lap 3 checks access, obstacle, and backup. A platform-neutral independent project is equal to a club or program.</p>",
                "RESOURCES": "<p>Licensed Rung 6 pages are embedded. Rung 7 supplies opportunity categories, but current campus information controls availability.</p>",
                "SUPPORT": "<p>Use SMART icons and sentence frames. The packet gives a separate full-width response area for every reasoning job.</p>",
                "FALLBACK": "<p>No eDynamic unit is required. An absent student can complete the packet with the embedded visuals and one source-checked option card.</p>",
            },
            5: {
                "TITLE": "Individual High School and Career Plan",
                "SUBTITLE": "50 minutes · TEKS d(8)(B), d(8)(C), d(3)(D)",
                "ALERT": "<strong>Major 2 in the 4SW assessment map.</strong> Keep the Assignment unpublished and ungraded until the Major group and 40/60 weighting are verified.",
                "PREP": f'<ul><li>Post {file_link(files["PLAN"]["id"], "the four-page plan")} and {file_link(files["RUBRIC"]["id"], "the two-page student rubric")}.</li><li>Open the private unpublished Assignment.</li><li>Have Days 1-4 packets and dated source cards available.</li></ul>',
                "EVIDENCE": "<p>Private individual plan with self-evidence, course and preparation evidence, college-credit evidence, timed actions, support, backup, and revision rule. Major 2, scored with the 16-point rubric and converted to 100 gradebook points.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Supported part and open question.")
                + flow("#4a9d2f", "Gather · 5", "Days 1-4 evidence set.")
                + flow("#1f617a", "Write · 28", "Three chunks with checks.")
                + flow("#e3ad19", "Self-score · 7", "Circle, revise, and retain evidence labels.")
                + flow("#1f617a", "Submit · 5", "Private 3-2-1 and plan."),
                "MONITOR": "<p>Suggested conversion after local approval: 15-16 Masters, 13-14 Meets, 12 Approaches, 10-11 Needs Improvement; below 10 follows campus policy. Score evidence and reasoning, not family availability, adult agreement, grammar unless meaning is unclear, handwriting, art, accent, or submission mode.</p>",
                "RESOURCES": "<p>The plan prepares students for the counselor-controlled Xello planning tasks. It does not count as 4-year course plan, Make plans, Submit course requests, or parent approval completion.</p>",
                "SUPPORT": "<p>Use one numbered prompt per evidence job, speech-to-text, teacher scribe, or private media recording. The PDFs preserve full-width space.</p>",
                "FALLBACK": "<p>Missing prior work is rebuilt from the matching Student Guide and source card. Canvas failure means paper or later upload without penalty.</p>",
            },
        }

        day_names = {
            1: "Graduation and Assessment Decisions",
            2: "Four-Year Course Plan Draft",
            3: "College Credit and Plan Conversation",
            4: "SMART Experience Action Plan",
            5: "Individual High School and Career Plan",
        }
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 4SW Wk2 Day {day} - {day_names[day]}"
            student_page = await common.upsert_page(
                client,
                student_title,
                common.render(
                    "4sw-wk2-student.html",
                    {"COURSE_ID": COURSE_ID, "DAY": day, "MEDIA": media[day], **student[day]},
                ),
            )
            teacher_title = f"TEACHER: 4SW Wk2 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(
                client,
                teacher_title,
                common.render(
                    "4sw-wk2-teacher.html",
                    {
                        "COURSE_ID": COURSE_ID,
                        "DAY": day,
                        "STUDENT_PAGE_URL": student_page["url"],
                        **teacher[day],
                    },
                ),
            )
            await upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            order.extend(
                [
                    ("Page", teacher_page["url"], teacher_title),
                    ("Page", student_page["url"], student_title),
                ]
            )
            pages[day] = {"teacher": teacher_page, "student": student_page}
            if day == 1:
                await upsert_item(client, module["id"], "Quiz", quiz["id"], QUIZ_TITLE)
                order.append(("Quiz", quiz["id"], QUIZ_TITLE))
            if day == 2:
                await upsert_item(client, module["id"], "Assignment", annotation["id"], ANNOTATION_TITLE)
                order.append(("Assignment", annotation["id"], ANNOTATION_TITLE))
            if day == 5:
                await upsert_item(client, module["id"], "Assignment", plan_assignment["id"], PLAN_TITLE)
                order.append(("Assignment", plan_assignment["id"], PLAN_TITLE))

        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(
                entry
                for entry in items
                if (kind == "SubHeader" and entry.get("id") == key)
                or (kind == "Page" and entry.get("page_url") == key)
                or (kind in ("Assignment", "Quiz") and entry.get("content_id") == key)
            )
            await common.api(
                client,
                "PUT",
                f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}",
                data={"module_item[position]": position, "module_item[title]": title},
            )

        final_items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        print(
            json.dumps(
                {
                    "module": {"id": module["id"], "published": module["published"]},
                    "quiz": {
                        "id": quiz["id"],
                        "published": quiz.get("published"),
                        "quiz_type": quiz.get("quiz_type"),
                        "allowed_attempts": quiz.get("allowed_attempts"),
                    },
                    "annotation": {
                        "id": annotation["id"],
                        "published": annotation.get("published"),
                        "submission_types": annotation.get("submission_types"),
                        "annotatable_attachment_id": annotation.get("annotatable_attachment_id"),
                    },
                    "plan_assignment": {
                        "id": plan_assignment["id"],
                        "published": plan_assignment.get("published"),
                        "submission_types": plan_assignment.get("submission_types"),
                        "grading_type": plan_assignment.get("grading_type"),
                    },
                    "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
                    "visual_folders": {
                        str(day): {"id": folder["id"], "locked": folder["locked"]}
                        for day, folder in visual_folders.items()
                    },
                    "files": {key: value["id"] for key, value in files.items()},
                    "visuals": {
                        str(day): {name: value["id"] for name, value in entries.items()}
                        for day, entries in visuals.items()
                    },
                    "pages": {
                        str(day): {
                            kind: {"url": value["url"], "published": value["published"]}
                            for kind, value in pair.items()
                        }
                        for day, pair in pages.items()
                    },
                    "items": [
                        {"position": item["position"], "type": item["type"], "title": item["title"]}
                        for item in final_items
                    ],
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
