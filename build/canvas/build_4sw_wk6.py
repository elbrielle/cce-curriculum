"""Build the unpublished 4SW Week 6 evidence-synthesis Canvas module."""

import asyncio
import json
import re
import sys
from urllib.parse import urlencode

import httpx

import build_4sw_wk1 as common


COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/4sw/wk6"
MODULE_NAME = "4SW Wk6: Skills That Transfer and Mid-Year Evidence"
TRUCK_TITLE = "PRACTICE: Truck Evidence and Priority"
SKILLS_TITLE = "PRACTICE: Transferable Skills Evidence"
ORG_QUIZ_TITLE = "PRACTICE: Career Organization Type Check"
INTEGRITY_QUIZ_TITLE = "PRACTICE: Integrity and Accurate Records"
REFLECTION_TITLE = "DRAFT: Private Mid-Year Evidence Reflection"
LEGACY_REFLECTION_TITLE = REFLECTION_TITLE
REFLECTION_TITLE = "RECOVERY: Private Mid-Year Evidence Reflection"
TEMPLATES = ROOT / "build/canvas/templates"
WORKSHEET_NAMES = {
    "TRUCK": "4sw-wk6-truck-evidence-and-priority.pdf",
    "SKILLS": "4sw-wk6-transferable-skills-evidence.pdf",
    "ORGS": "4sw-wk6-career-organization-types.pdf",
    "INTEGRITY": "4sw-wk6-integrity-and-evidence-audit.pdf",
    "REFLECTION": "4sw-wk6-mid-year-evidence-reflection.pdf",
    "RUBRIC": "4sw-wk6-mid-year-evidence-rubric.pdf",
}
VISUAL_NAMES = (
    "fyf-analytical-reasoning-tools.jpg",
    "fyf-truck-clue-sets.jpg",
    "fyf-truck-priority-and-plan.jpg",
)


def preflight():
    required = [
        TEMPLATES / "4sw-wk6-student.html",
        TEMPLATES / "4sw-wk6-teacher.html",
        *(ROOT / "docs/resources/worksheets" / name for name in WORKSHEET_NAMES.values()),
        *(ASSETS / "day1" / name for name in VISUAL_NAMES),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"4SW Wk6 preflight missing required files: {missing}")


async def canvas_preflight(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    module_matches = [entry for entry in modules if entry.get("name") == MODULE_NAME]
    if len(module_matches) > 1:
        raise RuntimeError(f"Duplicate Canvas modules named {MODULE_NAME!r}: {[entry['id'] for entry in module_matches]}")
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    for title in (TRUCK_TITLE, SKILLS_TITLE, REFLECTION_TITLE, LEGACY_REFLECTION_TITLE):
        matches = [entry for entry in assignments if entry.get("name") == title]
        if len(matches) > 1:
            raise RuntimeError(f"Duplicate assignments named {title!r}: {[entry['id'] for entry in matches]}")
    recovery_matches = [
        entry for entry in assignments
        if entry.get("name") in {REFLECTION_TITLE, LEGACY_REFLECTION_TITLE}
    ]
    if len(recovery_matches) > 1:
        raise RuntimeError(f"Expected at most one Week 6 recovery reflection; found {len(recovery_matches)}")
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    for title in QUIZZES:
        matches = [entry for entry in quizzes if entry.get("title") == title]
        if len(matches) > 1:
            raise RuntimeError(f"Duplicate quizzes named {title!r}: {[entry['id'] for entry in matches]}")



CONTRACTS = {
    1: {
        "TOPIC": "Transferable Skills",
        "OBJECTIVE": "Students will separate observations from conclusions, choose a safe inspection priority using evidence, and explain how analytical reasoning transfers to another career task.",
        "TEKS": "d(4)(B)",
        "DOL": "Completed FYF pp. 154-155 priority and plan plus one clue-limit-safe-action and cross-career transfer response.",
        "I_CAN": "separate a clue from a conclusion, choose a safe priority, and show how analytical reasoning transfers to another career task.",
        "SHOW": "Complete FYF pp. 154-155, then write one clue-limit-safe-action and cross-career transfer response.",
    },
    2: {
        "TOPIC": "Transferable Skills",
        "OBJECTIVE": "Students will use specific job tasks to show how four skills transfer among six careers.",
        "TEKS": "d(4)(B)",
        "DOL": "Four transferable-skill comparisons, a three-example pattern claim, and an independent two-career transfer response.",
        "I_CAN": "use specific tasks to prove that a skill transfers among different careers.",
        "SHOW": "Complete four skill comparisons, a three-example claim, and one independent two-career transfer response.",
    },
    3: {
        "TOPIC": "Extended Learning",
        "OBJECTIVE": "Students will distinguish CTSOs, professional associations, a credentialing organization, and a government agency; explain how one realistic student opportunity supports career exploration and development.",
        "TEKS": "d(3)(F), d(3)(H)",
        "DOL": "Four-question practice Quiz and one Sam decision with an accurate type, benefit, access boundary, and career-development value.",
        "I_CAN": "tell what four organization types do and explain how one student opportunity supports career development.",
        "SHOW": "Complete the four-question practice Quiz and recommend one school-based opportunity now and one professional network to investigate later, using facts and an access boundary.",
    },
    4: {
        "TOPIC": "Professional Character",
        "OBJECTIVE": "Students will identify work ethic, integrity, dedication, and perseverance in four fictional workplace decisions and connect one trait to prior class evidence.",
        "TEKS": "d(4)(F)",
        "DOL": "Five selected-response practice checks plus one justified workplace decision and personal class-artifact evidence audit.",
        "I_CAN": "identify four professional characteristics and connect one to a visible action in my class work.",
        "SHOW": "Complete five feedback questions, then justify one workplace decision and audit one prior class artifact in the final response.",
    },
    5: {
        "TOPIC": "Evidence Reflection",
        "OBJECTIVE": "Students will use fixed and personal evidence to explain one change in career thinking, prove two transferable skills, evaluate one professional association and its membership boundary, and set two supported next actions.",
        "TEKS": "d(4)(B), d(3)(H)",
        "DOL": "Teacher-assigned private four-part recovery reflection, self-score, and visible revision.",
        "I_CAN": "use evidence to explain a change, prove two skills, evaluate one professional association, and plan two next actions.",
        "SHOW": "When assigned for recovery or replacement, submit a private four-part reflection with a self-score and one visible revision.",
    },
}


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    matches = [entry for entry in modules if entry.get("name") == MODULE_NAME]
    if len(matches) > 1:
        raise RuntimeError(f"Duplicate Canvas modules named {MODULE_NAME!r}: {[entry['id'] for entry in matches]}")
    found = matches[0] if matches else None
    data = {"module[published]": "false"}
    if found:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data=data)
    data["module[name]"] = MODULE_NAME
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


async def upsert_item(client, module_id, kind, key, title):
    items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    found = next(
        (
            item
            for item in items
            if item.get("type") == kind and ((kind == "SubHeader" and item.get("title") == title)
            or (kind == "Page" and item.get("page_url") == key)
            or (kind in ("Assignment", "Quiz") and item.get("content_id") == key))
        ),
        None,
    )
    if found:
        return await common.api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{found['id']}",
            data={"module_item[title]": title, "module_item[published]": "false"},
        )
    data = {"module_item[type]": kind, "module_item[title]": title, "module_item[published]": "false"}
    if kind == "Page":
        data["module_item[page_url]"] = key
    elif kind in ("Assignment", "Quiz"):
        data["module_item[content_id]"] = key
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data=data)


async def upload_locked(client, path, folder_path):
    uploaded = await common.upload(client, path, folder_path)
    record = await common.api(client, "GET", f"/files/{uploaded['id']}")
    if not record.get("locked"):
        record = await common.api(client, "PUT", f"/files/{uploaded['id']}", data={"locked": "true"})
    if not record.get("locked"):
        raise RuntimeError(f"Canvas did not lock uploaded file {path.name!r}")
    return record


async def lock_folder_files(client, folder):
    current = await common.api(client, "GET", f"/folders/{folder['id']}")
    if not current.get("locked"):
        current = await common.api(client, "PUT", f"/folders/{folder['id']}", data={"locked": "true"})
    if not current.get("locked"):
        raise RuntimeError(f"Canvas did not lock folder {folder['id']}")
    for entry in await common.paged(client, f"/folders/{folder['id']}/files"):
        if not entry.get("locked"):
            await common.api(client, "PUT", f"/files/{entry['id']}", data={"locked": "true"})
    final = await common.paged(client, f"/folders/{folder['id']}/files")
    unlocked = [entry.get("display_name") or entry.get("filename") for entry in final if not entry.get("locked")]
    if unlocked:
        raise RuntimeError(f"Unlocked files remain in folder {folder['id']}: {unlocked}")
    return current, len(final)


QUIZZES = {
    ORG_QUIZ_TITLE: [
        {
            "name": "Q1 - CTSO",
            "prompt": "Which pair contains two career and technical student organizations?",
            "correct": "SkillsUSA and TSA",
            "wrong": ["ASE and FAA", "NSPE and FAA", "AOPA and ASE"],
            "yes": "Correct. Both are school-connected CTSOs.",
            "no": "SkillsUSA and TSA are the CTSOs in this evidence set.",
        },
        {"name": "Q2 - Credentialing", "prompt": "Which organization assesses and credentials automotive knowledge and experience?", "correct": "ASE", "wrong": ["FAA", "TSA", "NSPE"], "yes": "Correct. ASE is an independent nonprofit credentialing organization.", "no": "ASE develops automotive assessments and credentials; it is not a school club."},
        {"name": "Q3 - Government", "prompt": "Which organization is a federal government agency rather than a membership association?", "correct": "FAA", "wrong": ["AOPA", "NSPE", "SkillsUSA"], "yes": "Correct. The FAA is part of the U.S. Department of Transportation.", "no": "The FAA regulates aviation and is not an association a student joins."},
        {"name": "Q4 - Access", "prompt": "What is the strongest first step for a student interested in SkillsUSA?", "correct": "Ask a CTE teacher or counselor whether the school has a chapter and what access requires.", "wrong": ["Assume every campus has a free chapter.", "Register for an ASE professional test instead.", "Join the FAA."], "yes": "Correct. School access and local requirements must be verified.", "no": "A national organization page does not prove a particular campus chapter."},
        {"name": "Q5 - Sam decision", "type": "essay_question", "prompt": "Fictional Sam wants a school-based leadership and competition opportunity now and an aviation professional network to investigate later. Recommend one organization for now and one for later. Use one card fact for each, explain how the school opportunity supports career exploration or development, and name one access, eligibility, cost, or privacy question."},
    ],
    INTEGRITY_QUIZ_TITLE: [
        {"name": "Q1 - Pressure to sign", "prompt": "A worker is asked to sign an inspection they did not complete. What is the strongest action?", "correct": "Do not sign; record the incomplete status accurately and use the supervisor or authorized handoff route.", "wrong": ["Sign now and fix it later.", "Delete the record.", "Guess that the inspection passed."], "yes": "Correct. Integrity protects both the work and the record.", "no": "A signature must not claim work that was not completed."},
        {"name": "Q2 - Conflicting data", "prompt": "Two approved classroom measurements conflict. What should the team record?", "correct": "Both results, the conflict, and the approved next verification step", "wrong": ["Only the result that looks best", "The average as a guaranteed truth", "No result at all"], "yes": "Correct. Honest uncertainty is usable evidence.", "no": "Do not hide or relabel a conflicting measurement."},
        {"name": "Q3 - Perseverance", "prompt": "Which statement best describes perseverance?", "correct": "Continue through difficulty while keeping safety, quality, and authorization boundaries.", "wrong": ["Continue any task even when it becomes unsafe.", "Hide a mistake to finish on time.", "Never ask for help."], "yes": "Correct. Persistence does not erase professional boundaries.", "no": "Unsafe persistence is not professional perseverance."},
        {"name": "Q4 - Evidence", "prompt": "Which statement is personal evidence of work ethic in class?", "correct": "I completed every required evidence row, noticed one weak explanation, and revised it before submitting.", "wrong": ["I have good work ethic.", "My favorite career is automotive.", "I opened the website."], "yes": "Correct. The statement names visible action and revision.", "no": "A trait label or click is not evidence by itself."},
        {"name": "Q5 - Dedication", "prompt": "Which statement best shows dedication?", "correct": "I kept improving the required product because quality mattered, while still following the deadline and safety rules.", "wrong": ["I refused every revision because the first version was already finished.", "I continued an unsafe task because stopping would look weak.", "I hid the incomplete part so the product looked finished."], "yes": "Correct. Dedication is sustained commitment to quality and purpose within professional boundaries.", "no": "Dedication does not erase deadlines, safety, honesty, or revision."},
        {"name": "Q6 - Evidence audit", "type": "essay_question", "prompt": "Choose one fictional case and one prior class artifact. For the case, name the characteristic, trustworthy action, accurate record or handoff, and harm prevented. For the artifact, name one visible action that proves a professional characteristic and one honest revision still needed."},
    ],
}


async def upsert_quiz(client, title, questions):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    matches = [quiz for quiz in quizzes if quiz.get("title") == title]
    if len(matches) > 1:
        raise RuntimeError(f"Duplicate quizzes named {title!r}: {[entry['id'] for entry in matches]}")
    found = matches[0] if matches else None
    data = {
        "quiz[title]": title,
        "quiz[description]": "<p>Ungraded, unlimited-retry evidence check with immediate feedback.</p>",
        "quiz[quiz_type]": "practice_quiz",
        "quiz[published]": "false",
        "quiz[allowed_attempts]": "-1",
        "quiz[show_correct_answers]": "true",
        "quiz[shuffle_answers]": "false",
    }
    endpoint = f"/courses/{COURSE_ID}/quizzes/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes"
    quiz = await common.api(client, "PUT" if found else "POST", endpoint, data=data)
    existing = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    desired_names = [question["name"] for question in questions]
    seen = set()
    for prior in existing:
        name = prior.get("question_name")
        if name not in desired_names or name in seen:
            await common.api(client, "DELETE", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior['id']}")
        else:
            seen.add(name)
    existing = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    for position, question in enumerate(questions, 1):
        prior = next((entry for entry in existing if entry.get("question_name") == question["name"]), None)
        item = {
            "question_name": question["name"],
            "question_text": question["prompt"],
            "question_type": question.get("type", "multiple_choice_question"),
            "position": position,
            "points_possible": 1,
        }
        if item["question_type"] == "multiple_choice_question":
            item.update(
                {
                    "correct_comments": question["yes"],
                    "incorrect_comments": question["no"],
                    "answers": [{"answer_text": question["correct"], "answer_weight": 100}]
                    + [{"answer_text": answer, "answer_weight": 0} for answer in question["wrong"]],
                }
            )
        payload = {"question": item}
        path = (
            f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior['id']}"
            if prior
            else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        )
        await common.api(client, "PUT" if prior else "POST", path, json=payload)
    final_questions = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    by_name = {entry.get("question_name"): entry for entry in final_questions}
    if set(by_name) != set(desired_names) or len(final_questions) != len(desired_names):
        raise RuntimeError(f"Quiz {quiz['id']} question mismatch")
    fields = []
    for name in desired_names:
        fields.extend([("order[][id]", str(by_name[name]["id"])), ("order[][type]", "question")])
    await common.api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/reorder",
        content=urlencode(fields),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    ordered = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    if [entry.get("question_name") for entry in ordered] != desired_names:
        raise RuntimeError(f"Quiz {quiz['id']} order mismatch")
    final = await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
    if final.get("published") or final.get("quiz_type") != "practice_quiz" or int(final.get("allowed_attempts") or 0) != -1:
        raise RuntimeError(f"Practice quiz invariant failed for {title!r}")
    return final


async def upsert_recovery_assignment(client, description):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [
        entry
        for entry in assignments
        if entry.get("name") in {REFLECTION_TITLE, LEGACY_REFLECTION_TITLE}
    ]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one Week 6 recovery reflection; found {len(matches)}")
    if matches:
        found = matches[0]
    else:
        found = await common.upsert_assignment(
            client,
            REFLECTION_TITLE,
            description,
            ["online_upload", "online_text_entry", "media_recording"],
        )
    assignment = await common.api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{found['id']}",
        data={
            "assignment[name]": REFLECTION_TITLE,
            "assignment[description]": description,
            "assignment[submission_types][]": ["online_upload", "online_text_entry", "media_recording"],
            "assignment[grading_type]": "not_graded",
            "assignment[points_possible]": "0",
            "assignment[omit_from_final_grade]": "true",
            "assignment[published]": "false",
        },
    )
    assignment = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignment['id']}")
    if (
        assignment.get("published")
        or float(assignment.get("points_possible") or 0) != 0
        or assignment.get("grading_type") != "not_graded"
        or assignment.get("omit_from_final_grade") is not True
    ):
        raise RuntimeError(f"Recovery assignment invariant failed for {REFLECTION_TITLE!r}")
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
        "assignment[submission_types][]": ["student_annotation", "online_upload", "online_text_entry"],
        "assignment[annotatable_attachment_id]": str(attachment_id),
        "assignment[grading_type]": "percent",
        "assignment[points_possible]": "0",
        "assignment[omit_from_final_grade]": "true",
        "assignment[published]": "false",
    }
    assignment = await common.api(
        client,
        "PUT" if found else "POST",
        f"/courses/{COURSE_ID}/assignments/{found['id']}" if found else f"/courses/{COURSE_ID}/assignments",
        data=data,
    )
    assignment = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignment['id']}")
    if (
        assignment.get("published")
        or float(assignment.get("points_possible") or 0) != 0
        or assignment.get("grading_type") != "percent"
        or assignment.get("omit_from_final_grade") is not True
    ):
        raise RuntimeError(f"Practice assignment invariant failed for {title!r}")
    source_file = await common.api(client, "GET", f"/files/{attachment_id}")
    clone_id = int(assignment.get("annotatable_attachment_id") or 0)
    clone_file = await common.api(client, "GET", f"/files/{clone_id}") if clone_id else {}
    if clone_file and not clone_file.get("locked"):
        clone_file = await common.api(client, "PUT", f"/files/{clone_id}", data={"locked": "true"})
    if (
        not clone_id
        or source_file.get("locked") is not True
        or clone_file.get("locked") is not True
        or clone_file.get("filename") != source_file.get("filename")
        or int(clone_file.get("size") or -1) != int(source_file.get("size") or -2)
    ):
        raise RuntimeError(f"Annotation attachment invariant failed for {title!r}")
    return assignment


def image_tag(file_id, alt):
    return (
        f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" '
        'style="display:block;width:100%;max-width:700px;height:auto;margin:14px auto;border:1px solid #ddd" '
        f'data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'
    )


async def main():
    preflight()
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        await canvas_preflight(client)
        module = await ensure_module(client)
        support_path = "course files/CCR Materials/4SW/Wk6"
        support_folder = await common.ensure_folder(client, support_path)
        files = {
            key: await upload_locked(client, ROOT / "docs/resources/worksheets" / name, support_path)
            for key, name in WORKSHEET_NAMES.items()
        }
        visual_path = "course files/CCR Materials/4SW/Wk6/Day 1 Visuals"
        visual_folder = await common.ensure_folder(client, visual_path)
        visuals = {}
        for name in VISUAL_NAMES:
            visuals[name] = await upload_locked(client, ASSETS / "day1" / name, visual_path)
        support_folder, support_file_count = await lock_folder_files(client, support_folder)
        visual_folder, visual_file_count = await lock_folder_files(client, visual_folder)

        quizzes = {title: await upsert_quiz(client, title, questions) for title, questions in QUIZZES.items()}
        truck = await upsert_practice_assignment(
            client,
            TRUCK_TITLE,
            f'<p><strong>Workbook first:</strong> complete FYF pp. 154-155, then write the clue-limit-safe-action exit response. Use the <a href="/courses/{COURSE_ID}/files/{files["TRUCK"]["id"]}/preview">three-page fallback</a> only for no-workbook, enlarged, absence, or Canvas-annotation access. This is a fictional evidence task, not a real diagnosis or repair.</p>',
            files["TRUCK"]["id"],
        )
        skills = await upsert_practice_assignment(
            client,
            SKILLS_TITLE,
            f'<p>Use the six fixed career-task cards. Type the four labeled comparisons, three-example claim, and independent transfer response, or use the <a href="/courses/{COURSE_ID}/files/{files["SKILLS"]["id"]}/preview">four-page paper or enlarged fallback</a>. Task evidence matters more than the number of checked boxes.</p>',
            files["SKILLS"]["id"],
        )
        reflection_description = (
            f'<p><strong>Open only for teacher-approved recovery or replacement evidence.</strong> This is not an automatic third Major or fourth Minor. '
            f'Use the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">student-visible rubric</a>. '
            'Submit the private four-part reflection by upload, text, approved private media, or paper.</p>'
        )
        reflection = await upsert_recovery_assignment(client, reflection_description)
        urls = {
            "truck": f"/courses/{COURSE_ID}/assignments/{truck['id']}",
            "skills": f"/courses/{COURSE_ID}/assignments/{skills['id']}",
            "orgs": f"/courses/{COURSE_ID}/quizzes/{quizzes[ORG_QUIZ_TITLE]['id']}",
            "integrity": f"/courses/{COURSE_ID}/quizzes/{quizzes[INTEGRITY_QUIZ_TITLE]['id']}",
            "reflection": f"/courses/{COURSE_ID}/assignments/{reflection['id']}",
        }
        media = {
            1: image_tag(visuals["fyf-analytical-reasoning-tools.jpg"]["id"], "Find Your Future Analytical Reasoning introduction and code-reader and dashboard-light tool limits")
            + image_tag(visuals["fyf-truck-clue-sets.jpg"]["id"], "Four fictional truck clue sets for oil, battery, temperature, and tire-pressure issues")
            + image_tag(visuals["fyf-truck-priority-and-plan.jpg"]["id"], "Find Your Future issue-priority scale and two-issue planning prompts; the repeated Issue 3 label at lower right should read Issue 4"),
            2: '''<div style="border:1px solid #bad4df;border-radius:10px;padding:14px 18px;margin:18px 0;background:#f8fbfc"><h3 style="margin-top:0;color:#1f617a">Six career-task cards</h3><ul><li><strong>Software developer:</strong> tests a change, explains an issue, and coordinates a release.</li><li><strong>Nurse:</strong> verifies supplied information, communicates a handoff, and works with a care team.</li><li><strong>Lawyer:</strong> reviews evidence, explains a position, and prepares with a legal team.</li><li><strong>Pilot:</strong> uses checklists, evaluates supplied flight information, and communicates with authorized personnel.</li><li><strong>Drone systems technician:</strong> tests a system, records results, and explains a revision.</li><li><strong>Automotive service technician:</strong> follows inspection steps, documents findings, and explains supported next steps.</li></ul><p><strong>Model:</strong> “They all need attention to detail” is only a claim. “A software developer checks a code change; an automotive technician follows an inspection checklist” gives visible task evidence.</p><p style="font-size:14px;color:#52616b">These cards are classroom examples, not complete job descriptions.</p></div>''',
            3: '''<div style="border:1px solid #bad4df;border-radius:10px;padding:14px 18px;margin:18px 0;background:#f8fbfc"><h3 style="margin-top:0;color:#1f617a">Read the organization cards</h3><p><strong>SkillsUSA: CTSO.</strong> Middle- and high-school participation runs through a school chapter or approved local plan. Ask a CTE teacher or counselor about local access. The national page does not prove a particular campus chapter or free activity.</p><p><strong>TSA: CTSO.</strong> Middle- and high-school STEM participation runs through a school-affiliated chapter and advisor. The national page does not prove a particular campus chapter, fee, or event.</p><p><strong>ASE: credentialing organization.</strong> ASE develops automotive assessments and credentials. Professional certification requires the applicable test and approved experience or substitution. ASE is not a school club.</p><p><strong>FAA: government agency.</strong> The FAA is part of the U.S. Department of Transportation. It regulates aviation and issues certificates in authorized contexts. It is not a membership association.</p><p><strong>NSPE: professional association.</strong> Current student membership requires qualifying full-time college, graduate, or formal pre-engineering transfer-program enrollment. It is a later professional network, not blanket middle-school membership.</p><p><strong>AOPA: professional association.</strong> AOPA currently advertises free high-school membership for U.S. residents ages 13-20. A student still follows family and district privacy rules before creating an account. AOPA does not issue FAA certificates.</p><p style="font-size:14px;color:#52616b">Official source pages checked August 10, 2026. The teacher guide includes direct links.</p></div>''',
            4: '''<div style="border:1px solid #bad4df;border-radius:10px;padding:14px 18px;margin:18px 0;background:#f8fbfc"><h3 style="margin-top:0;color:#1f617a">Four characteristics and four fictional cases</h3><ul><li><strong>Work ethic:</strong> reliable effort and responsibility.</li><li><strong>Integrity:</strong> honest action and records, even when no one is watching.</li><li><strong>Dedication:</strong> sustained commitment to quality and purpose.</li><li><strong>Perseverance:</strong> continuing through difficulty while keeping safety and quality boundaries.</li></ul><ol><li>A technician notices a blank checklist field after the item moved to the next station. A supervisor is available.</li><li>A team receives two conflicting approved classroom measurements. A teammate wants to report only the better result.</li><li>A worker reaches shift change with one observation not yet verified.</li><li>A worker is pressured to sign an inspection they did not complete.</li></ol><p><strong>Boundary:</strong> Perseverance never means continuing an unsafe or unauthorized task.</p><p><strong>Supplied class-artifact model:</strong> Artifact: Day 2 transfer comparison. Visible action: used two exact task cards and repaired a general claim. Honest limitation: one career task is still too broad. Next action: replace it with the exact card action before submitting.</p></div>''',
            5: '''<div style="border:1px solid #bad4df;border-radius:10px;padding:14px 18px;margin:18px 0;background:#f8fbfc"><h3 style="margin-top:0;color:#1f617a">Recovery evidence strip when prior work is missing</h3><p><strong>Fictional Morgan model:</strong> Earlier assumption: a career title tells most of the job. Current direction: compare daily tasks and preparation before choosing. Class evidence: Day 2 task comparison and Day 4 accurate-record case. Professional association fact: AOPA currently advertises a free U.S. high-school category for ages 13-20. Boundary: Morgan must verify eligibility and follow family/district privacy rules before any account. Unanswered question: Which school or counselor-supported aviation opportunity is available locally?</p><p>Use this fixed strip only when the teacher assigns recovery and personal prior evidence is missing. Analyze Morgan's evidence; do not claim Morgan's experience as your own.</p></div>''',
        }
        link, step, flow = common.file_link, common.step, common.flow

        student = {
            1: {
                "TITLE": "Analytical Reasoning: What the Clues Support",
                "PURPOSE": "Separate supplied clues from conclusions and choose a safe inspection priority.",
                "TODAY": "<ul><li>read four fictional clue sets;</li><li>name broad system concerns;</li><li>rank inspection priority;</li><li>write safe next steps.</li></ul>",
                "READY": f'<p><strong>Workbook first:</strong> open FYF pp. 153-155. Your teacher checks pp. 154-155 during work time; submit only the clue-limit-safe-action and transfer exit in <a href="{urls["truck"]}">the private practice Assignment</a>. Use {link(files["TRUCK"]["id"], "the three-page no-workbook fallback")} only for no-workbook, enlarged, absence, or annotation access. The workbook repeats Issue 3; the tire-pressure box is Issue 4.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> clue = supplied fact · concern = broad system to inspect · conclusion = claim that still needs proof · priority = order for responding.</p><p><strong>Use this frame:</strong> The clue shows ___. It does not prove ___. The safe next step is ___ because ___. A ___ also uses analytical reasoning when the worker ___.</p></div>',
                "STEPS": step(1, "Keep the boundary", "<p>A light or code points toward a system; it does not prove a failed part, repair, or safe-to-drive decision.</p>")
                + step(2, "Complete four evidence rows", "<p>Use two clues, one broad concern, one unproved conclusion, and one evidence need per case.</p>")
                + step(3, "Rank priority", "<p>Rank quickest stop-and-inspect response. A lower rank does not mean safe to ignore.</p>")
                + step(4, "Write authorized next steps", "<p>Stop/protect, notify/hand off, and identify the evidence a trained person still needs. Do not prescribe a repair.</p>"),
                "EXIT": "<p>Correct the claim that a code already proves the broken part, then name one different career task that uses the same clue-to-conclusion reasoning.</p>",
                "DONE": "<ul><li>FYF pp. 154-155 complete;</li><li>four ranks;</li><li>two safe next-step plans;</li><li>one clue-limit-safe-action and cross-career transfer response.</li></ul>",
                "SUPPORT": "<p>clue = pista · conclusion = conclusión · inspect = inspeccionar · priority = prioridad. Read one clue set at a time and highlight only supplied facts.</p>",
                "FALLBACK": "<p>The three-page fallback and adjacent image descriptions are the complete independent route when the workbook is unavailable. Do not print it by default. No partner, open search, vehicle, or personal car knowledge is required.</p>",
            },
            2: {
                "TITLE": "Prove That a Skill Transfers",
                "PURPOSE": "Use specific tasks to show how four skills transfer among six careers.",
                "TODAY": "<ul><li>read six fixed career cards;</li><li>compare four skills;</li><li>build a three-example claim;</li><li>complete an independent transfer check.</li></ul>",
                "READY": f'<p><a href="{urls["skills"]}">Open the private Canvas response</a>. Keep {link(files["SKILLS"]["id"], "the four-page paper or enlarged fallback")} available without printing it for everyone.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> task = tarea · skill = habilidad · common = en común · setting = entorno.</p><p><strong>Use this frame:</strong> ___ and ___ both use ___ when they ___. The common behavior is ___. The technical setting changes ___ because ___.</p></div>',
                "STEPS": step(1, "Move from claim to proof", "<p>A skill label is not proof. Name the visible task where the worker uses it.</p>")
                + step(2, "Compare four skills", "<p>For each skill, use two careers, common behavior, and a technical-setting difference.</p>")
                + step(3, "Build a pattern claim", "<p>Use three task examples and one honest limit.</p>")
                + step(4, "Check independently", "<p>Choose two careers from different clusters and prove one transfer.</p>"),
                "EXIT": "<p>Name two careers, one transferable skill, one task in each, and the common behavior.</p>",
                "DONE": "<ul><li>four skill comparisons;</li><li>specific task evidence;</li><li>three-example claim;</li><li>independent transfer response.</li></ul>",
                "SUPPORT": "<p>task = tarea · skill = habilidad · common = en común · technical = técnico. Phrases are acceptable in evidence boxes.</p>",
                "FALLBACK": "<p>The four-page fallback includes the fixed cards and every response job. Do not print it by default. No 48-cell grid, partner, live research, or login is required.</p>",
            },
            3: {
                "TITLE": "Career Organizations: Type, Access, and Value",
                "PURPOSE": "Distinguish CTSOs and professional associations from credentialing and government organizations.",
                "TODAY": "<ul><li>learn four organization types;</li><li>read six dated cards;</li><li>recommend one now and one later opportunity;</li><li>repair inaccurate labels.</li></ul>",
                "READY": f'<p>Open the six dated cards in this guide and <a href="{urls["orgs"]}">the five-question practice Quiz</a>. Keep {link(files["ORGS"]["id"], "the three-page paper fallback")} available without printing it for everyone.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> chapter = capítulo local · membership = membresía · credential = credencial · agency = agencia.</p><p><strong>Use this frame:</strong> Sam should ask about ___ now because ___. This could support career development by ___. Later, Sam could investigate ___, but first Sam must verify ___.</p></div>',
                "STEPS": step(1, "Sort by main job", "<p>CTSO, professional association, credentialing organization, or government agency.</p>")
                + step(2, "Read access before benefits", "<p>Record who can access the named opportunity and what the source does not prove.</p>")
                + step(3, "Decide for Sam", "<p>Recommend a school-based opportunity now and a professional network to investigate later.</p>")
                + step(4, "Practice and decide", f'<p><a href="{urls["orgs"]}">Complete four feedback questions and the individual Sam decision</a>.</p>'),
                "EXIT": "<p>Use the Quiz's Sam decision as the exit check. Do not submit the same answer twice.</p>",
                "DONE": "<ul><li>four feedback questions;</li><li>school-based organization, source fact, and career-development value;</li><li>later professional organization and source fact;</li><li>one access, eligibility, cost, or privacy question.</li></ul>",
                "SUPPORT": "<p>membership = membresía · student organization = organización estudiantil · credential = credencial · government agency = agencia gubernamental.</p>",
                "FALLBACK": "<p>The three-page fallback contains the same cards and questions. Do not print it by default. No dense public website, group jigsaw, public presentation, or personal membership is required.</p>",
            },
            4: {
                "TITLE": "Work Ethic and Integrity: Document the Decision",
                "PURPOSE": "Apply four professional characteristics to accurate actions and records.",
                "TODAY": "<ul><li>distinguish four characteristics;</li><li>solve four fictional cases;</li><li>audit one class artifact;</li><li>repair misconceptions.</li></ul>",
                "READY": f'<p>Open the four fictional cases in this guide and <a href="{urls["integrity"]}">the six-item practice Quiz</a> with five feedback questions and one evidence-audit response. Keep {link(files["INTEGRITY"]["id"], "the three-page paper fallback")} available without printing it for everyone.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> integrity = integridad · record = registro · verify = verificar · supervisor = supervisor.</p><p><strong>Use this frame:</strong> This case requires ___. The worker should ___ and record or report ___. This prevents ___ because ___.</p></div>',
                "STEPS": step(1, "Name the characteristic", "<p>Work ethic, integrity, dedication, or perseverance.</p>")
                + step(2, "Choose the trustworthy action", "<p>Name what the worker should do and what the record should say.</p>")
                + step(3, "Audit personal evidence", "<p>Use one class artifact, one visible action, one honest limitation, and one next step.</p>")
                + step(4, "Practice and audit", f'<p><a href="{urls["integrity"]}">Complete five feedback questions and the private evidence-audit response</a>.</p>'),
                "EXIT": "<p>Use the Quiz's final case-and-artifact response as the exit check. Do not submit a second copy.</p>",
                "DONE": "<ul><li>five feedback questions;</li><li>one justified case decision;</li><li>accurate record or supervisor route;</li><li>personal evidence audit.</li></ul>",
                "SUPPORT": "<p>integrity = integridad · record = registro · verify = verificar · supervisor = supervisor. Employment history is not required.</p>",
                "FALLBACK": "<p>The three-page fallback contains the same cases and response jobs. Do not print it by default. H&amp;L is optional; no private Career Plan or screenshot is required.</p>",
            },
            5: {
                "TITLE": "Recovery: Private Mid-Year Evidence Reflection",
                "PURPOSE": "When your teacher assigns recovery or replacement evidence, use specific course evidence to show a change, two transferable skills, one professional-association decision, and two next actions.",
                "TODAY": "<ul><li>build an evidence strip;</li><li>complete four response jobs;</li><li>self-score and revise;</li><li>submit privately.</li></ul>",
                "READY": f'<p><strong>Open this task only when your teacher assigns it for recovery or replacement.</strong> Use the private Canvas response and {link(files["RUBRIC"]["id"], "the two-page rubric")}. Keep {link(files["REFLECTION"]["id"], "the four-page paper fallback")} available when needed.</p>',
                "LANGUAGE": '<div style="border-left:5px solid #1f617a;background:#f2f8fb;padding:14px 18px;margin:18px 0"><p><strong>Word bank:</strong> reflection = reflexión · evidence = evidencia · association = asociación · revision = revisión.</p><p><strong>Use this frame:</strong> At first, I thought ___. After ___, I now think ___. The evidence that mattered was ___ because ___. The professional association I would investigate is ___, but I still need to verify ___.</p></div>',
                "STEPS": step(1, "Gather bounded evidence", "<p>Use one earlier assumption, current direction, two class tasks, one accurate professional-association fact, and one membership question.</p>")
                + step(2, "Write four parts", "<p>Change in thinking; two skills; professional-association decision; two next actions.</p>")
                + step(3, "Self-score and revise", "<p>Revise the weakest criterion. Longer personal stories are not required.</p>")
                + step(4, "Submit privately", f'<p><a href="{urls["reflection"]}">Submit by upload, text, private media, or paper</a>.</p>'),
                "EXIT": "<p>Record three accurate labels, two evidence moves, and one revision.</p>",
                "DONE": "<ul><li>four reflection parts;</li><li>specific evidence labels;</li><li>two timed actions with support and backup;</li><li>visible revision;</li><li>private submission.</li></ul>",
                "SUPPORT": "<p>reflection = reflexión · evidence = evidencia · route = ruta · revision = revisión. Bullet points are allowed in Parts 2 and 4.</p>",
                "FALLBACK": "<p>The four-page paper route is complete when Canvas is unavailable. Use the generic evidence strip when earlier work is missing. No public sharing, profile screenshot, or partner disclosure is required.</p>",
            },
        }

        student[4].update(
            {
                "READY": student[4]["READY"]
                + "<p><strong>Evidence Log:</strong> open Entry 4 from your CCE binder or teacher-designated "
                "digital folder. Keep it with you; it is not another submission.</p>",
                "STEPS": student[4]["STEPS"]
                + step(
                    5,
                    "Transfer Entry 4",
                    "<p>Use the Personal Evidence Audit already open. Copy short phrases for artifact or task, "
                    "transferable skill, visible action, revision or recovery move, and next step. Keep the log "
                    "in your CCE binder or teacher-designated digital folder.</p>",
                ),
                "EXIT": student[4]["EXIT"]
                + "<p>Then transfer the five audit phrases to Entry 4. This is not a second Quiz response or upload.</p>",
                "DONE": student[4]["DONE"].replace(
                    "</ul>",
                    "<li>Evidence Log Entry 4 saved with me, or five fallback phrases saved for later transfer.</li></ul>",
                ),
                "FALLBACK": student[4]["FALLBACK"]
                + "<p>If the Evidence Log is missing, save the five short phrases in your CCE notebook or "
                "teacher-designated digital folder and transfer them later. Do not reconstruct earlier work.</p>",
            }
        )

        teacher = {
            1: {
                "TITLE": "Analytical Reasoning: What the Clues Support",
                "SUBTITLE": "50 minutes · TEKS d(4)(B)",
                "ALERT": "<strong>Fictional evidence task only.</strong> Students do not diagnose or repair a real vehicle, prescribe a part, or declare it safe to drive.",
                "PREP": f'<ul><li>Place one FYF workbook per student and one device per student for the private exit; no grouping is required.</li><li>Keep {link(files["TRUCK"]["id"], "the three-page fallback")} for no-workbook, enlarged, absence, or annotation access; print one only for each student using that route.</li><li>Project the three FYF pages, name the repeated Issue 3 typo, and use the supplied temperature-light clue/limit/safe-action model.</li><li>During work time, initial pp. 154-155 after the four ranks and two plans are present. Students submit only the private exit; fallback students turn in one packet.</li></ul>',
                "EVIDENCE": "<p>Completed FYF pp. 154-155 priority and plan plus one clue-limit-safe-action and cross-career transfer response. Formative.</p>",
                "FLOW": flow("#5a2d91", "Clue or conclusion · 5", "Sort three statements.")
                + flow("#4a9d2f", "Tool limits · 7", "Light and code-reader boundaries.")
                + flow("#1f617a", "Four clue sets · 18", "Evidence before conclusion.")
                + flow("#e3ad19", "Priority and plan · 15", "Stop, notify, inspect.")
                + flow("#1f617a", "Exit · 5", "Clue, limit, safe action."),
                "MONITOR": "<p><strong>Minute 12:</strong> students label supplied clues without naming a failed part. If more than one-third diagnose, rework the supplied model together. <strong>Minute 28:</strong> all four concerns and ranks are present. <strong>Minute 42:</strong> two plans name stop/protect, handoff, and missing evidence. Pivot to the fixed packet text if images or workbooks fail. Safe trim: complete two full evidence rows, rank all four, and protect both plans plus the private exit; the other rows may be completed during recovery. Broad accepted concerns: lubrication/engine-temperature; electrical/charging; cooling/temperature; tire/steering. Collect only the exit/assigned packet; students close devices and return workbooks.</p>",
                "RESOURCES": "<p>Licensed FYF pp. 153-155 carry the default task. The fallback corrects the Issue 4 label and removes open repair research without replacing the workbook.</p>",
                "SUPPORT": "<p>Keep the point-of-use word bank and full frame visible. Read clue sets aloud, highlight supplied facts, and allow typing, dictation, annotation, or paper.</p>",
                "FALLBACK": "<p>No vehicle, partner, personal story, or site is required. The three delivery images total about 508 KB; the three-page fallback is the independent text route.</p>",
            },
            2: {
                "TITLE": "Prove That a Skill Transfers",
                "SUBTITLE": "50 minutes · TEKS d(4)(B)",
                "ALERT": "<strong>Task evidence, not box count.</strong> The former 48-cell grid was removed because it demanded cramped repetitive writing without improving the standard evidence.",
                "PREP": f'<ul><li>Provide one device per student; no grouping is required. Print one {link(files["SKILLS"]["id"], "four-page fallback")} only for each paper/enlarged-route student.</li><li>Project the supplied software-developer/automotive-technician claim-versus-proof model and the six fixed cards.</li><li>Students submit one private Canvas response or one complete packet. Do not collect a separate exit.</li></ul>',
                "EVIDENCE": "<p>Four skills compared across six careers, two task examples per skill, three-example pattern claim, and independent transfer. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "One skill plus one task.")
                + flow("#4a9d2f", "Evidence model · 8", "Claim versus proof.")
                + flow("#1f617a", "Compare · 25", "Four skills across six cards.")
                + flow("#e3ad19", "Pattern claim · 7", "Three tasks and one limit.")
                + flow("#1f617a", "Exit · 5", "Two-cluster transfer."),
                "MONITOR": "<p><strong>Minute 13:</strong> every response names tasks, not titles alone. If one-third still list only skills, annotate the supplied model. <strong>Minute 29:</strong> two comparisons are complete; <strong>minute 41:</strong> all four and three task examples are present. Safe trim: preserve all four comparisons, then allow the pattern claim and independent exit to use the same strongest three examples rather than inventing new ones. If Canvas fails, move to one packet per student. Collect one route only; close devices.</p>",
                "RESOURCES": "<p>The six fixed task cards are course-derived examples, not complete occupation descriptions. Live research is unnecessary.</p>",
                "SUPPORT": "<p>Keep the point-of-use word bank and full frame visible. Read one card and skill at a time. Accept phrases in comparison fields; require a complete final claim.</p>",
                "FALLBACK": "<p>Annotation, upload, text, and paper are equal. The four-page fallback is complete and should not be printed by default. No partner or login is required.</p>",
            },
            3: {
                "TITLE": "Career Organizations: Type, Access, and Value",
                "SUBTITLE": "50 minutes · TEKS d(3)(F), d(3)(H)",
                "ALERT": "<strong>Corrected organization types.</strong> FAA is government; ASE is credentialing; SkillsUSA/TSA are CTSOs; NSPE/AOPA are professional associations.",
                "PREP": f'<ul><li>Provide one device per student; no grouping or live account creation is required. The six dated cards and five-item Quiz are supplied.</li><li>Print one {link(files["ORGS"]["id"], "three-page paper fallback")} only for each no-device or enlarged-route student.</li><li>Project the Sam model frame. Students submit the Quiz, including Q5, or one paper packet; Q5 is the exit.</li></ul>',
                "EVIDENCE": "<p>Four selected-response checks plus an individual Sam recommendation using two card facts, career-development value, and one access, eligibility, cost, or privacy question. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Membership, test, or rule?")
                + flow("#4a9d2f", "Four types · 10", "Main job and access.")
                + flow("#1f617a", "Six cards · 18", "Classify and preserve limits.")
                + flow("#e3ad19", "Feedback checks · 7", "Repair four labels.")
                + flow("#1f617a", "Sam decision and exit · 10", "School opportunity now, network later."),
                "MONITOR": "<p><strong>Minute 12:</strong> students can separate membership, credentialing, and government. If one-third misclassify FAA or ASE, reshow the four-type chart. <strong>Minute 30:</strong> each student has classified all six cards. <strong>Minute 42:</strong> Sam's response includes now/later, two facts, career-development value, and a boundary. Safe trim: read only the bold lead sentence on each card, but protect all four feedback questions and Q5. SkillsUSA/TSA require a school route; NSPE is not blanket middle-school membership; AOPA remains investigate-with-family/district-privacy, not direct signup. Collect the Quiz or one packet only.</p>",
                "RESOURCES": '<p><a href="https://www.skillsusa.org/join/how-to-join/">SkillsUSA How to Join</a> · <a href="https://tsaweb.org/membership/membership-faq">TSA Membership FAQ</a> · <a href="https://ase.com/about/">ASE About</a> · <a href="https://www.faa.gov/about">FAA About</a> · <a href="https://www.nspe.org/membership/types-membership/student-membership">NSPE Student Membership</a> · <a href="https://www.aopa.org/account/studentjoinform">AOPA High School Membership</a></p>',
                "SUPPORT": "<p>Keep the point-of-use word bank and full frame visible. Use the four-type chart and one card at a time. The practice Quiz gives immediate corrective feedback before the individual decision.</p>",
                "FALLBACK": "<p>The three-page fallback is the complete no-web route and should not be printed by default. No group jigsaw, public presentation, or personal membership data is required.</p>",
            },
            4: {
                "TITLE": "Work Ethic and Integrity: Document the Decision",
                "SUBTITLE": "50 minutes · TEKS d(4)(F)",
                "ALERT": "<strong>Accuracy before drama.</strong> Use fictional bounded cases; do not invent real repair, aviation, clinical, or inspection procedures.",
                "PREP": f'<ul><li>Provide one device per student; no grouping or employment history is required. The four cases, six-item Quiz, and class-artifact model are supplied.</li><li>Print one {link(files["INTEGRITY"]["id"], "three-page paper fallback")} only for each no-device or enlarged-route student.</li><li>Project the supplied Day 2 artifact model. Students submit the Quiz, including Q6, or one packet; Q6 is the exit.</li></ul>',
                "EVIDENCE": "<p>Five selected-response checks, one justified case decision, and one personal class-artifact evidence audit. Formative.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Hard work versus trustworthy work.")
                + flow("#4a9d2f", "Four traits · 8", "Definitions and boundaries.")
                + flow("#1f617a", "Four cases · 15", "Action, record, harm prevented.")
                + flow("#e3ad19", "Feedback checks · 10", "Repair five decisions.")
                + flow("#1f617a", "Case, artifact, and exit · 12", "Complete Q6 once."),
                "MONITOR": "<p><strong>Minute 12:</strong> students distinguish integrity from perseverance. If one-third select persistence without the safety boundary, repair Case 4 together. <strong>Minute 30:</strong> five feedback items are complete; <strong>minute 42:</strong> Q6 names a trait, action, record/handoff, harm prevented, artifact evidence, and honest revision. Safe trim: analyze two cases instead of four, but protect all feedback checks and Q6. Collect one route only; close devices. Integrity requires an accurate action and record, not only “tell the truth.”</p>",
                "RESOURCES": "<p>The CCE fictional cases are the complete source. H&amp;L career browse is optional and never graded.</p>",
                "SUPPORT": "<p>Keep the point-of-use word bank and full frame visible. Use characteristic/action/record/harm labels, oral rehearsal, and private response modes.</p>",
                "FALLBACK": "<p>The three-page fallback contains the same cases and response jobs and should not be printed by default. No screenshot, profile history, partner, or workplace experience is required.</p>",
            },
            5: {
                "TITLE": "Recovery: Private Mid-Year Evidence Reflection",
                "SUBTITLE": "50 minutes · TEKS d(4)(B), d(3)(H)",
                "ALERT": "<strong>Recovery or replacement only.</strong> This is not an automatic third Major or fourth Minor. Keep the Assignment unpublished, worth zero points, and not graded until a teacher assigns it for an approved recovery decision.",
                "PREP": f'<ul><li>Keep the recovery Assignment unpublished until an approved teacher decision identifies the student and replaced evidence; this is never whole-class automatic work.</li><li>For each assigned student, provide one device and {link(files["RUBRIC"]["id"], "the student-visible rubric")}; print one {link(files["REFLECTION"]["id"], "four-page paper fallback")} only for a paper/enlarged route.</li><li>Project the supplied fictional Morgan evidence strip only when prior artifacts are missing. Students analyze it without claiming the fictional experience as their own.</li><li>Collect one private Canvas submission or one paper packet and rubric. No public share is required.</li></ul>',
                "EVIDENCE": "<p>Teacher-assigned private four-part recovery reflection, self-score, visible revision, and two supported actions. Zero points and not graded by default.</p>",
                "FLOW": flow("#5a2d91", "Warm-up · 5", "Before/now assumption.")
                + flow("#4a9d2f", "Evidence strip · 8", "Bounded facts and question.")
                + flow("#1f617a", "Reflection · 27", "Four separate response jobs.")
                + flow("#e3ad19", "Self-score · 5", "Revise weakest criterion.")
                + flow("#1f617a", "Private submit · 5", "Text, upload, media, or paper."),
                "MONITOR": "<p><strong>Minute 13:</strong> evidence strip has the six required entries. <strong>Minute 24:</strong> Parts 1-2 are present; <strong>minute 36:</strong> Parts 3-4 are present; <strong>minute 45:</strong> self-score and visible revision are complete. If prior evidence is missing, use the supplied Morgan strip; if time is short, accept bullets in Parts 2/4 and one strong sentence per required job, then schedule completion rather than deleting a rubric criterion. Score only after an approved recovery decision. Close the private task after collection.</p>",
                "RESOURCES": "<p>Days 1-4 evidence is the source base. Day 5 specifically requires a professional-association fact and membership boundary for d(3)(H). The generic strip prevents missing earlier artifacts from becoming a failure point.</p>",
                "SUPPORT": "<p>Keep the point-of-use word bank and complete frame visible. Use bullet points in Parts 2/4, speech-to-text, private media, teacher scribe, or paper. Every multi-sentence job has a full-width block.</p>",
                "FALLBACK": "<p>No sharing circle or partner disclosure is required. Canvas failure means paper or later upload without penalty.</p>",
            },
        }

        teacher[4].update(
            {
                "PREP": teacher[4]["PREP"].replace(
                    "</ul>",
                    "<li>Ask students to open Entry 4 of the CCE Six-Weeks Evidence Log from their CCE binder "
                    "or teacher-designated digital folder. Do not collect it.</li></ul>",
                ),
                "FLOW": teacher[4]["FLOW"].replace(
                    "Complete Q6 once.",
                    "Complete Q6 once; transfer Entry 4 during the same block.",
                ),
                "MONITOR": (
                    "<p><strong>Minute 12:</strong> students distinguish integrity from perseverance. If one-third "
                    "select persistence without the safety boundary, repair Case 4 together. <strong>Minute 30:</strong> "
                    "five feedback items are complete. <strong>Minute 42:</strong> Q6 names a trait, action, record or "
                    "handoff, harm prevented, artifact evidence, and honest revision. Use the final 3 minutes of the "
                    "12-minute case/artifact block for Entry 4; this replaces optional H&amp;L browsing. If the log is "
                    "missing, students save the five short phrases in their CCE notebook or teacher-designated "
                    "digital folder and transfer them later. Safe trim: analyze two cases instead of four, but protect "
                    "all five checks, Q6, and the Entry 4 transfer. Collect one Quiz or packet only; do not collect or "
                    "score the Evidence Log.</p>"
                ),
            }
        )

        day_names = {
            1: "What the Clues Support",
            2: "Prove a Skill Transfers",
            3: "Career Organization Types",
            4: "Integrity and Accurate Records",
            5: "Recovery: Private Mid-Year Reflection",
        }
        extras = {
            1: ("Assignment", truck["id"], TRUCK_TITLE),
            2: ("Assignment", skills["id"], SKILLS_TITLE),
            3: ("Quiz", quizzes[ORG_QUIZ_TITLE]["id"], ORG_QUIZ_TITLE),
            4: ("Quiz", quizzes[INTEGRITY_QUIZ_TITLE]["id"], INTEGRITY_QUIZ_TITLE),
            5: ("Assignment", reflection["id"], REFLECTION_TITLE),
        }
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 4SW Wk6 Day {day} - {day_names[day]}"
            student_page = await common.upsert_page(
                client,
                student_title,
                common.render(
                    "4sw-wk6-student.html",
                    {"COURSE_ID": COURSE_ID, "DAY": day, "MEDIA": media[day], **CONTRACTS[day], **student[day]},
                ),
            )
            teacher_title = f"TEACHER: 4SW Wk6 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(
                client,
                teacher_title,
                common.render(
                    "4sw-wk6-teacher.html",
                    {
                        "COURSE_ID": COURSE_ID,
                        "DAY": day,
                        "STUDENT_PAGE_URL": student_page["url"],
                        **CONTRACTS[day],
                        **teacher[day],
                    },
                ),
            )
            await upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title)]
            pages[day] = {"teacher": teacher_page, "student": student_page}
            kind, key, title = extras[day]
            await upsert_item(client, module["id"], kind, key, title)
            order.append((kind, key, title))

        if len(order) != 20:
            raise RuntimeError(f"Week 6 module contract requires exactly 20 items; built {len(order)}")

        def matches_item(entry, kind, key):
            return entry.get("type") == kind and (
                (kind == "SubHeader" and entry.get("id") == key)
                or (kind == "Page" and entry.get("page_url") == key)
                or (kind in ("Assignment", "Quiz") and entry.get("content_id") == key)
            )

        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        keep_ids = set()
        for kind, key, _title in order:
            match = next(
                (entry for entry in items if entry["id"] not in keep_ids and matches_item(entry, kind, key)),
                None,
            )
            if not match:
                raise RuntimeError(f"Missing expected module item: {kind} {key}")
            keep_ids.add(match["id"])
        for entry in items:
            if entry["id"] not in keep_ids:
                await common.api(
                    client,
                    "DELETE",
                    f"/courses/{COURSE_ID}/modules/{module['id']}/items/{entry['id']}",
                )
        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(entry for entry in items if matches_item(entry, kind, key))
            await common.api(
                client,
                "PUT",
                f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}",
                data={"module_item[position]": position, "module_item[title]": title},
            )
        final_items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        if len(final_items) != len(order):
            raise RuntimeError(f"Expected {len(order)} Week 6 module items; found {len(final_items)}")
        ordered_final = sorted(final_items, key=lambda entry: entry.get("position", 0))
        for position, ((kind, key, title), entry) in enumerate(zip(order, ordered_final), 1):
            if (
                entry.get("position") != position
                or not matches_item(entry, kind, key)
                or entry.get("title") != title
                or entry.get("published") is not False
            ):
                raise RuntimeError(f"Week 6 module order mismatch at position {position}")
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        if module.get("published"):
            raise RuntimeError("Week 6 module unexpectedly published")
        quizzes = {
            title: await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
            for title, quiz in quizzes.items()
        }
        for title, quiz in quizzes.items():
            if quiz.get("published") or quiz.get("quiz_type") != "practice_quiz" or int(quiz.get("allowed_attempts") or 0) != -1:
                raise RuntimeError(f"Final practice quiz invariant failed for {title!r}")
            questions = await common.paged(
                client,
                f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions",
            )
            expected_names = [question["name"] for question in QUIZZES[title]]
            if [question.get("question_name") for question in questions] != expected_names:
                raise RuntimeError(f"Final practice quiz question order failed for {title!r}")
        truck = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{truck['id']}")
        skills = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{skills['id']}")
        reflection = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{reflection['id']}")
        for title, assignment in ((TRUCK_TITLE, truck), (SKILLS_TITLE, skills)):
            if (
                assignment.get("published")
                or float(assignment.get("points_possible") or 0) != 0
                or assignment.get("grading_type") != "percent"
                or assignment.get("omit_from_final_grade") is not True
                or set(assignment.get("submission_types") or []) != {"student_annotation", "online_upload", "online_text_entry"}
            ):
                raise RuntimeError(f"Final practice assignment invariant failed for {title!r}")
        if (
            reflection.get("published")
            or float(reflection.get("points_possible") or 0) != 0
            or reflection.get("grading_type") != "not_graded"
            or reflection.get("omit_from_final_grade") is not True
            or set(reflection.get("submission_types") or []) != {"online_upload", "online_text_entry", "media_recording"}
        ):
            raise RuntimeError(f"Final recovery assignment invariant failed for {REFLECTION_TITLE!r}")
        for title, assignment, source in (
            (TRUCK_TITLE, truck, files["TRUCK"]),
            (SKILLS_TITLE, skills, files["SKILLS"]),
        ):
            clone_id = int(assignment.get("annotatable_attachment_id") or 0)
            clone = await common.api(client, "GET", f"/files/{clone_id}") if clone_id else {}
            source = await common.api(client, "GET", f"/files/{source['id']}")
            if (
                not clone_id
                or source.get("locked") is not True
                or clone.get("locked") is not True
                or clone.get("filename") != source.get("filename")
                or int(clone.get("size") or -1) != int(source.get("size") or -2)
            ):
                raise RuntimeError(f"Final annotation attachment invariant failed for {title!r}")
        for day, pair in pages.items():
            for kind, value in pair.items():
                page = await common.api(client, "GET", f"/courses/{COURSE_ID}/pages/{value['url']}")
                if page.get("published"):
                    raise RuntimeError(f"Published Week 6 {kind} page on Day {day}")
        support_folder, support_file_count = await lock_folder_files(client, support_folder)
        visual_folder, visual_file_count = await lock_folder_files(client, visual_folder)
        print(
            json.dumps(
                {
                    "module": {"id": module["id"], "published": module["published"]},
                    "quizzes": {
                        title: {
                            "id": quiz["id"],
                            "published": quiz.get("published"),
                            "quiz_type": quiz.get("quiz_type"),
                            "allowed_attempts": quiz.get("allowed_attempts"),
                        }
                        for title, quiz in quizzes.items()
                    },
                    "assignments": {
                        "truck": {
                            "id": truck["id"],
                            "published": truck.get("published"),
                            "submission_types": truck.get("submission_types"),
                            "annotatable_attachment_id": truck.get("annotatable_attachment_id"),
                        },
                        "skills": {
                            "id": skills["id"],
                            "published": skills.get("published"),
                            "submission_types": skills.get("submission_types"),
                            "annotatable_attachment_id": skills.get("annotatable_attachment_id"),
                        },
                        "reflection": {
                            "id": reflection["id"],
                            "published": reflection.get("published"),
                            "submission_types": reflection.get("submission_types"),
                            "grading_type": reflection.get("grading_type"),
                        },
                    },
                    "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
                    "visual_folder": {"id": visual_folder["id"], "locked": visual_folder["locked"]},
                    "files": {key: value["id"] for key, value in files.items()},
                    "visuals": {key: value["id"] for key, value in visuals.items()},
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
