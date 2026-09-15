"""Build the unpublished 6SW Week 6 career-evidence capstone module."""

import asyncio
import json
import sys

import httpx

import build_5sw_wk1 as prior
from configure_assessment_map import SUBMISSION_LINK_MARKER


common = prior.common
COURSE_ID = common.COURSE_ID
STUDENT_GOOGLE_COPY_URLS = {
    1: "https://docs.google.com/document/d/1Q8kcr9JEk9wFTzoDcetKxlTK_7c2Q-omwX_07xP2h_s/copy",
    2: "https://docs.google.com/document/d/1xiJUSknBxEzKotlNMfx190WjoZG53394F0GKvruHLoM/copy",
    3: "https://docs.google.com/document/d/1ycAgpMpdiEtEFGWijh-mh3ZbXkC7KZPSnXjg3ekU2XI/copy",
    4: "https://docs.google.com/document/d/1HwYLdogWDuV55UpLya5XqbbAohqMm9oc7BRrgwa6aMw/copy",
    5: "https://docs.google.com/document/d/1geEUPCgXGQuwXyoCjrEBrJiG9q9W6eXSho3IzwVo8Nw/copy",
}


# One Google Doc per worksheet (build/google_docs/student_worksheet_docs.json).
# Keyed by (day, anchor label) so a worksheet button never opens the day's exit ticket.
STUDENT_WORKSHEET_COPY_URLS = {
    (1, 'the two-page inventory and recovery plan'): "https://docs.google.com/document/d/1921t3P10WjG032OWiJFQr2edshy_6QwWYmE2-4KqlpI/copy",
    (2, 'the four-page individual career plan'): "https://docs.google.com/document/d/1f7mFTf2FwoUr6NjfAYTRmtydTIf2zhFDeClsYT3bqGU/copy",
    (3, 'the two-page brief and rehearsal plan'): "https://docs.google.com/document/d/1TaYLV9Wh9I0oKn5r6nbMHa5hMwzmTkEYk91ODE0lFNk/copy",
    (4, 'the two-page delivery and revision record'): "https://docs.google.com/document/d/1efYTwbvPZWCF4ovurvAwTxr1ePeRO2iRmMj97nDN9hU/copy",
    (5, 'the two-page reflection and transfer plan'): "https://docs.google.com/document/d/1mZyUOqrN4_iHVEzIiAnKtLbA3-ohf0jz6r3GZdn83tc/copy",
}


def student_copy_link(day, label):
    url = STUDENT_WORKSHEET_COPY_URLS.get((day, label), STUDENT_GOOGLE_COPY_URLS[day])
    return f'<a href="{url}">{label}</a>'

ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/6sw/wk6"
MODULE_NAME = "6SW Wk6: Career Evidence Capstone"
TITLES = {
    # Retain the existing Canvas assignment names so a rebuild updates the
    # teacher's current objects instead of leaving four stale orphan copies.
    1: "CAPSTONE: Evidence Inventory and Recovery",
    2: "CAPSTONE: Individual Career Plan",
    3: "CAPSTONE: Presentation Plan and Rehearsal",
    4: "MAJOR 2: Individual Career Plan and Communicated Capstone",
    5: "CAPSTONE: Final Course Reflection",
}

CONTRACTS = {
    1: {
        "TOPIC": "Evidence Audit",
        "OBJECTIVE": "Students will select a current career pathway or direction using self and career evidence, identify one missing or uncertain evidence job, and document an honest recovery action.",
        "TEKS": "d(8)(A)",
        "DOL": "Two-page career-evidence inventory and recovery plan.",
        "I_CAN": "select a current career direction, identify one evidence gap, and recover it honestly.",
        "SHOW": "Complete the two-page career-evidence inventory and recovery plan.",
    },
    2: {
        "TOPIC": "Career Plan",
        "OBJECTIVE": "Students will select a career pathway or direction, document high-school and postsecondary or training requirements, and write an individual plan for starting the career after high school and any postsecondary education.",
        "TEKS": "d(8)(A), d(8)(B), d(8)(C)",
        "DOL": "Four-page individual career plan with current evidence, source limits, route questions, three actions, support, and backup.",
        "I_CAN": "use current evidence to select a career direction, document high-school and training requirements, and write a flexible action plan.",
        "SHOW": "Complete the four-page individual career plan with source labels, route questions, three actions, support, and backup.",
    },
    3: {
        "TOPIC": "Presentation Planning",
        "OBJECTIVE": "Students will plan and rehearse an oral professional presentation about career and college exploration using appropriate technology, source-labeled evidence, and a privacy-safe route.",
        "TEKS": "prepares d(4)(C)",
        "DOL": "Two-page oral/AAC career-evidence brief and rehearsal plan with two timed attempts and one visible revision.",
        "I_CAN": "plan and rehearse a concise oral or AAC career brief using appropriate technology and source-labeled evidence.",
        "SHOW": "Complete the two-page brief and rehearsal plan with two timed attempts, a technology backup, and one visible revision.",
    },
    4: {
        "TOPIC": "Professional Presentation",
        "OBJECTIVE": "Students will give an oral professional presentation about career and college exploration using appropriate technology, then use feedback to revise one evidence gap.",
        "TEKS": "d(4)(C), d(8)(B), d(8)(C)",
        "DOL": "Private 2-3-minute oral/AAC career brief, two-page delivery/revision record, visible revision, transfer action, and six-criterion Major 2 self-score; the Day 2 plan remains in its original location.",
        "I_CAN": "use appropriate technology to communicate my career plan, respond to feedback, and revise one evidence gap.",
        "SHOW": "Submit the private 2-3-minute oral/AAC brief, two-page delivery/revision record, visible revision, transfer action, and self-score; keep the Day 2 plan in its original location.",
    },
    5: {
        "TOPIC": "Plan Revision",
        "OBJECTIVE": "Students will use specific course evidence to revise an individual plan for starting a career after high school and any postsecondary education, then choose a realistic next action and support.",
        "TEKS": "d(8)(C)",
        "DOL": "Two-page private final reflection and transfer plan with then/now evidence, three transferable skills, a dated next action, support, and flexibility note.",
        "I_CAN": "use specific course evidence to explain my growth and choose a realistic next action, support, and backup.",
        "SHOW": "Complete the two-page private reflection and transfer plan with then/now evidence, three transferable skills, a dated action, support, and flexibility note.",
    },
}


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    matches = [module for module in modules if module.get("name") == MODULE_NAME]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one {MODULE_NAME!r} module; found {len(matches)}")
    data = {"module[name]": MODULE_NAME, "module[published]": "false"}
    if matches:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{matches[0]['id']}", data=data)
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


async def mapped_major_assignment(client):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == TITLES[4]]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one existing mapped Major named {TITLES[4]!r}; found {len(matches)}")
    found = matches[0]
    if float(found.get("points_possible") or 0) != 100:
        raise RuntimeError(f"Refusing to modify Career Capstone Major: expected 100 points, found {found.get('points_possible')}")
    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group = next((entry for entry in groups if entry.get("id") == found.get("assignment_group_id")), None)
    if not group or group.get("name") != "Major Assessments (60%)":
        raise RuntimeError("Refusing to modify Career Capstone Major outside Major Assessments (60%)")
    return found


async def require_major_assignment(client, found, description, attachment_id):
    scoring_note = (
        '<div data-cce-rubric-note="cce-advisory-rubric-v1" style="border-left:4px solid #6b318f;padding:10px 14px;margin:16px 0">'
        '<p><strong>How this is scored:</strong> Use the student-visible six-criterion profile. Add the ratings out of 24, use the published performance-band conversion, and enter the percentage as the score out of 100.</p>'
        '<p>The Day 2 plan stays in its original Canvas or labeled-paper location. Students submit only the Day 4 communicated evidence, two-page record, and self-score here; score the complete profile across the two locations.</p></div>'
    )
    return await common.api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{found['id']}",
        data={
            "assignment[name]": TITLES[4],
            "assignment[description]": description + scoring_note,
            "assignment[published]": "false",
            "assignment[points_possible]": "100",
            "assignment[grading_type]": "points",
            "assignment[omit_from_final_grade]": "false",
            "assignment[submission_types][]": ["media_recording", "student_annotation", "online_upload", "online_text_entry"],
            "assignment[annotatable_attachment_id]": str(attachment_id),
        },
    )


def student_content(files, visuals, urls):
    link, step = common.file_link, common.step
    def media(pairs):
        return (
            '<details style="border:1px solid #d8c2e5;border-radius:8px;padding:12px 16px;margin:18px 0;background:#fbf7fd">'
            '<summary style="font-weight:700;color:#6b318f;cursor:pointer">Optional FYF workbook orientation</summary>'
            + "".join(prior.image_tag(visuals[key]["id"], alt) for key, alt in pairs)
            + "</details>"
        )
    submission = (
        f'<section data-cce-marker="{SUBMISSION_LINK_MARKER}" style="border:2px solid #6b318f;border-radius:12px;padding:18px 20px;margin:24px 0;background:#fbf7fd">'
        '<h3 style="margin:0 0 8px;color:#6b318f">Submit Major 2 communicated evidence</h3>'
        '<p style="margin:0 0 14px">Submit the private oral/AAC evidence, two-page delivery/revision record, and self-score here. Your Day 2 plan stays where you first submitted or turned it in.</p>'
        f'<p style="margin:0"><a href="{urls[4]}" style="display:inline-block;background:#6b318f;color:#fff;padding:11px 18px;border-radius:6px;text-decoration:none;font-weight:700" data-api-endpoint="/api/v1{urls[4]}" data-api-returntype="Assignment">Open {TITLES[4]}</a></p></section>'
    )
    return {
        1: {
            "TITLE": "Evidence Audit and Recovery",
            "PURPOSE": "Start the capstone with current evidence, recover one gap, and keep unsupported claims visible.",
            "TODAY": "<ul><li>name a current direction and alternative;</li><li>mark eight evidence jobs ready, revise, or recover;</li><li>recover one gap honestly;</li><li>choose four pieces to carry forward.</li></ul>",
            "READY": f'<p>Open {student_copy_link(1, "the two-page inventory and recovery plan")} and <a href="{urls[1]}">the private annotation or submission route</a>. Use one route; do not complete the same work twice.</p>',
            "MEDIA": media([("p277", "FYF capstone opener about changing paths and repairing broken steps"), ("p278", "FYF Career Ladder rungs used as an optional evidence reminder")]),
            "SUPPORT": '<p><strong>Word bank:</strong> evidence/evidencia · recover/recuperar · source/fuente · limitation/limitación · pathway/ruta.</p><p><strong>Use this frame in Step 3:</strong> I recovered <strong>[evidence]</strong> from <strong>[source]</strong>. It supports <strong>[claim]</strong>, but it does not prove <strong>[limit]</strong>.</p>',
            "STEPS": step(1, "Name the current direction", "<p>Write one reason the direction changed or stayed stable. Add a flexible alternative.</p>") + step(2, "Audit eight evidence jobs", "<p>Mark ready, revise, or recover. Name where the item lives or how it can be rebuilt.</p>") + step(3, "Recover one gap", "<p>Use a supplied source, prior Canvas work, staff conference, or supervised catch-up. Record what the evidence supports and cannot prove.</p>") + step(4, "Build the Day 2 map", "<p>Choose four pieces to carry forward, one conflict, and the next priority.</p>"),
            "SUBMISSION": "",
            "EXIT": "<p>Name the conflict and the first action needed to resolve it.</p>",
            "DONE": "<ul><li>current direction and alternative;</li><li>eight evidence statuses;</li><li>one documented recovery;</li><li>four-piece map;</li><li>conflict and Day 2 priority.</li></ul>",
            "FALLBACK": "<p>A missing old page, family interview, H&amp;L login, partner, or platform does not erase learning. Use the supplied source, prior Canvas work, staff conference, or supervised catch-up. Do not submit private profile screenshots or contact/family data.</p>",
        },
        2: {
            "TITLE": "Individual Career Plan",
            "PURPOSE": "Turn current evidence into a specific, flexible plan with source labels, questions, actions, support, and backup.",
            "TODAY": "<ul><li>connect self evidence to a direction and alternative;</li><li>label preparation and labor evidence;</li><li>separate confirmed routes from questions;</li><li>write three dated actions and a backup.</li></ul>",
            "READY": f'<p>Open {student_copy_link(2, "the four-page individual career plan")} and <a href="{urls[2]}">the private Canvas route</a>. Keep this plan in its original location; Day 4 will not ask you to upload it again.</p>',
            "MEDIA": "",
            "SUPPORT": '<p><strong>Word bank:</strong> direction/dirección · preparation/preparación · requirement/requisito · verify/verificar · backup/plan alterno.</p><p><strong>Use this frame in Step 4:</strong> I will <strong>[action]</strong> by <strong>[date]</strong> with help from <strong>[support]</strong>. If <strong>[obstacle]</strong> happens, I will <strong>[backup]</strong>.</p>',
            "STEPS": step(1, "Connect self and career", "<p>Name a current direction, flexible alternative, career task, and the self evidence behind the choice.</p>") + step(2, "Label the research", "<p>Keep salary or trend amount, measure, geography, date, source, and limitation visible.</p>") + step(3, "Build the route", "<p>Name the current high-school connection, one item to verify, postsecondary or training route, and the credential/cost/time boundary.</p>") + step(4, "Act flexibly", "<p>Write three actions, dates, obstacle, backup, support request, strongest evidence, and uncertainty.</p>"),
            "SUBMISSION": "",
            "EXIT": "<p>Name the strongest evidence and the most important uncertainty.</p>",
            "DONE": "<ul><li>direction and alternative;</li><li>career task and self evidence;</li><li>preparation and labor labels;</li><li>high-school and training route;</li><li>three actions, support, obstacle, and backup.</li></ul>",
            "FALLBACK": "<p>Type, annotate, dictate, use enlarged print, or use paper. Use current verified labels and keep unresolved questions visible. No pathway, admission, salary, credential, schedule, or employment outcome is guaranteed.</p>",
        },
        3: {
            "TITLE": "Career Evidence Brief and Rehearsal",
            "PURPOSE": "Plan and rehearse a concise oral or AAC career-and-college brief without turning it into a design project.",
            "TODAY": "<ul><li>choose an oral/AAC route and appropriate technology;</li><li>organize six evidence jobs;</li><li>rehearse twice;</li><li>apply one revision and name a backup.</li></ul>",
            "READY": f'<p>Open {student_copy_link(3, "the two-page brief and rehearsal plan")} and <a href="{urls[3]}">the private Canvas route</a>. Short evidence notes are enough; do not write a full script unless it is an approved access support.</p>',
            "MEDIA": media([("p279", "FYF presentation-format choices used as optional route inspiration"), ("p280", "FYF presentation rubric orientation; the current CCE rubric controls scoring")]),
            "SUPPORT": '<p><strong>Word bank:</strong> audience/audiencia · source/fuente · limitation/limitación · rehearse/ensayar · revision/revisión.</p><p><strong>Use this opening frame:</strong> My current direction is <strong>[direction]</strong>. I chose it because <strong>[self evidence]</strong> connects to <strong>[career task]</strong>.</p>',
            "STEPS": step(1, "Choose the route", "<p>Select live, small group, teacher conference, private recording, or authorized AAC. Name the Canvas recording, evidence card, teacher-approved visual, or AAC technology.</p>") + step(2, "Organize six speaking jobs", "<p>Use direction, task, preparation/labor, route, action/support, and limitation/close. Keep source labels visible.</p>") + step(3, "Rehearse twice", "<p>Target 2-3 minutes. Use specific feedback or the self-check after Attempt 1.</p>") + step(4, "Revise and protect the route", "<p>Show one before/after change and name a technology or access backup.</p>"),
            "SUBMISSION": "",
            "EXIT": "<p>Confirm the final route, appropriate technology, backup, and visible revision.</p>",
            "DONE": "<ul><li>route, audience, technology, and privacy plan;</li><li>six evidence jobs;</li><li>two timed attempts;</li><li>specific feedback or self-check;</li><li>visible revision and backup.</li></ul>",
            "FALLBACK": "<p>Public speaking and camera use are not required. Visual polish and expensive tools are not scored. A written outline supports the brief but does not by itself demonstrate d(4)(C).</p>",
        },
        4: {
            "TITLE": "Communicated Capstone and Revision",
            "PURPOSE": "Communicate the career plan through a private oral or AAC route, use feedback, and revise one evidence gap.",
            "TODAY": "<ul><li>complete the six-job final check;</li><li>deliver a 2-3-minute career brief using appropriate technology;</li><li>record feedback and revise one gap;</li><li>self-score and submit the Day 4 evidence once.</li></ul>",
            "READY": f'<p>Open {student_copy_link(4, "the two-page delivery and revision record")}, {link(files["RUBRIC"]["id"], "the two-page Major 2 evidence profile")}, and your Day 3 plan. Your Day 2 career plan stays in its original location.</p>',
            "MEDIA": media([("p299", "FYF prepare-and-present reminders and completion questions")]),
            "SUPPORT": '<p><strong>Word bank:</strong> communicate/comunicar · audience/audiencia · feedback/retroalimentación · revision/revisión · transfer/transferir.</p><p><strong>Use this frame after feedback:</strong> After <strong>[feedback]</strong>, I changed <strong>[before]</strong> to <strong>[after]</strong>. This improved <strong>[criterion]</strong> because <strong>[reason]</strong>.</p>',
            "STEPS": step(1, "Complete the final check", "<p>Confirm six evidence jobs, source labels, route, appropriate technology, backup, and privacy boundary.</p>") + step(2, "Deliver through the assigned route", "<p>Use small group, teacher conference, private audio/video, or authorized AAC. Keep the evidence within 2-3 minutes.</p>") + step(3, "Use feedback", "<p>Record one effective choice and one exact gap. Show a before/after revision and explain the improvement.</p>") + step(4, "Transfer and self-score", "<p>Name one item or question to carry forward, score all six criteria, revise the weakest available evidence, and submit once.</p>"),
            "SUBMISSION": submission,
            "EXIT": "<p>Name the strongest evidence and the revision that made the plan more usable.</p>",
            "DONE": "<ul><li>assessable 2-3-minute oral/AAC evidence using appropriate technology;</li><li>two-page delivery/revision record;</li><li>specific feedback and visible revision;</li><li>transfer item or question;</li><li>six-criterion self-score and one Day 4 submission.</li></ul>",
            "FALLBACK": "<p>Use the assigned private live, small-group, teacher-conference, recording, or authorized AAC route. A written plan or transcript may scaffold access but does not replace oral/AAC evidence unless an authorized accommodation defines the route.</p>",
        },
        5: {
            "TITLE": "Reflection and Transfer Forward",
            "PURPOSE": "Close the course with specific evidence, transferable skills, and one realistic action instead of a forced final-career declaration.",
            "TODAY": "<ul><li>compare then and now;</li><li>map one example from each six weeks;</li><li>connect three transferable skills to new contexts;</li><li>choose a dated action, support, and flexibility response.</li></ul>",
            "READY": f'<p>Open {student_copy_link(5, "the two-page reflection and transfer plan")} and <a href="{urls[5]}">the private Canvas route</a>. Use the module list if you need help remembering the year.</p>',
            "MEDIA": media([("p297", "FYF motivation and support prompts"), ("p298", "FYF picture-your-future reflection"), ("p300", "FYF final reflection prompts")]),
            "SUPPORT": '<p><strong>Word bank:</strong> reflection/reflexión · transferable/transferible · checkpoint/punto de control · support/apoyo · flexible/flexible.</p><p><strong>Use this frame in Step 4:</strong> I will use <strong>[skill]</strong> from <strong>[course evidence]</strong> when I <strong>[new context]</strong>. My next action is <strong>[action]</strong> by <strong>[date]</strong>.</p>',
            "STEPS": step(1, "Compare then and now", "<p>Use one specific piece of evidence to explain the change or stable result.</p>") + step(2, "Map the year", "<p>Name one activity, decision, or artifact from each six weeks and what it helped you understand.</p>") + step(3, "Transfer three skills", "<p>Connect each skill to course evidence and another school, career, community, or personal context.</p>") + step(4, "Choose the next action", "<p>Add the date, support role, request, realism check, and what you will do if the plan changes.</p>"),
            "SUBMISSION": "",
            "EXIT": "<p>Record one open question and the person or source that could help answer it.</p>",
            "DONE": "<ul><li>then/now evidence;</li><li>one example from each six weeks;</li><li>three skill transfers;</li><li>dated next action and support;</li><li>flexibility note, advice, and open question.</li></ul>",
            "FALLBACK": "<p>Perfect memory, forced positivity, public sharing, a family detail, top-career declaration, and H&amp;L login are not required. Type, annotate, dictate, use enlarged print, or use paper.</p>",
        },
    }


def teacher_content(files):
    link, flow = common.file_link, common.flow
    color = "#6b318f"
    common_support = "<p>Point-of-use word banks and complete frames appear before the evidence job. Accept typing, annotation, dictation, enlarged print, paper, teacher conference, private recording, and authorized AAC. Short fields request labels; every explanation has proportional writing space.</p>"
    common_fallback = "<p>A missing old page, family interview, H&amp;L login, partner, camera, or public route does not block completion. Use prior Canvas work, a supplied source, staff conference, or supervised catch-up. Do not require private profile screenshots, contact/family data, unsupported pathway guarantees, or decorative production.</p>"
    return {
        1: {"TITLE": "Evidence Audit and Recovery", "SUBTITLE": "50 minutes · Two-page record", "ALERT": "<strong>Recovery, not punishment:</strong> A missing old artifact triggers a current evidence route. It does not become an automatic point loss.", "PREP": f'<ul><li>Post {link(files["INVENTORY"]["id"], "the two-page inventory and recovery plan")} and private annotation route; default printing is zero.</li><li>Have one supplied source and one staff-conference option ready.</li><li>Open the coordinated Student Guide.</li></ul>', "EVIDENCE": "<p>Collect a current direction and alternative, eight evidence statuses, one completed recovery, four-piece map, conflict, and Day 2 priority.</p>", "FLOW": (
            flow(color, "Minutes 0-5 - Welcome and evidence audit readiness warm-up", '''<p>Welcome students to Week 6 of 6SW (Career Evidence Capstone) and project the portfolio audit prompt.</p><ul><li>Ask students: <em>“As we reach the culmination of our year in College and Career Exploration, how has your understanding of your own strengths, skills, and postsecondary aspirations evolved since August? If you find a gap in your past evidence or an uncompleted project, why is recovery a standard professional workflow rather than a penalty?”</em></li><li>Collect 2-3 student thoughts: Our interests changed as we learned about real careers; professionals update and repair missing records when auditing their portfolios!</li><li>Bridge with, <em>“The capstone is an honest, evidence-based synthesis of your growth under TEKS d(8)(A). Today we audit our 8 core course evidence artifacts, identify any missing components, execute a targeted in-class recovery route, and map our primary and alternative career directions.”</em></li></ul>''')
            + flow("#4c8b38", "Minutes 5-13 - Modeling portfolio auditing &amp; recovery protocols", '''<p>Display the 8 Core Portfolio Evidence Jobs on the main screen:</p><ul><li>1. <strong>Self-Knowledge:</strong> Holland RIASEC personality themes &amp; work values (1SW).</li><li>2. <strong>Labor Market Evidence:</strong> BLS May 2024 median wages &amp; 10-year growth projections (2SW).</li><li>3. <strong>Postsecondary Pathways:</strong> Comparing college, technical school, apprenticeships &amp; military (3SW).</li><li>4. <strong>Financial Literacy:</strong> High school endorsement budgets, net pay &amp; loan debt (4SW).</li><li>5. <strong>Cluster Investigations:</strong> STEM, Health Science, Architecture/Construction, Real Estate (5SW).</li><li>6. <strong>Employability Artifacts:</strong> Professional resume, cover letter &amp; job search trace (6SW).</li><li>7. <strong>Interview Evidence:</strong> STAR responses &amp; mock interview checkoff (6SW).</li><li>8. <strong>High School Transition:</strong> Irving ISD 4-year endorsement plan &amp; CTE pathways (6SW).</li><li>Model the 3 Evidence Statuses: <strong>Ready</strong> (verified in Canvas/folder), <strong>Revise</strong> (needs updated labels or numbers), <strong>Recover</strong> (missing/absent; immediately complete using supplied BLS cards or teacher conference).</li></ul>''')
            + flow("#155d7a", "Minutes 13-30 - Portfolio inventory &amp; targeted recovery sprint", '''<p>Students conduct their inventory on the 2-page record:</p><ul><li>Section 1: Audit all 8 evidence jobs; mark each as Ready, Revise, or Recover.</li><li>Section 2: Execute In-Class Recovery: For any missing item, select a supplied fallback profile card or consult teacher to complete verified evidence.</li><li>Section 3: Synthesize Primary Direction vs. Flexible Alternative: Document Career Pathway A and Career Pathway B to ensure long-term adaptability.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 19): Ensure students identify missing evidence without fear; provide fallback cards immediately.<br>• Lap 2 (Minute 26): Verify that students document both a primary direction and a flexible alternative.</li></ul>''')
            + flow("#d39b22", "Minutes 30-45 - Elbow partner audit &amp; Day 2 priority selection", '''<p>Elbow partners compare their 4-piece evidence maps:</p><ul><li>Partner checks: 'Are your BLS median wages labeled with May 2024 dates and national geography?'</li><li>Document Day 2 Planning Priority: Identify the primary high school CTE pathway and postsecondary route to flesh out tomorrow.</li></ul>''')
            + flow(color, "Minutes 45-50 - Submit Day 1 Inventory and wrap-up", '''<p>Students submit their completed 2-page inventory in Canvas or place paper copies in the collection tray.</p><ul><li><strong>Safe Trim:</strong> Shorten partner review; fiercely protect 8-job inventory, completed recovery route, primary/alternative pathways, and private exit.</li></ul>''')
        ), "MONITOR": "<p><strong>Full evidence:</strong> recovery is completed today and names what the source supports and cannot prove. A promise to look later is not recovered evidence. Preserve recovery and the four-piece map; trim partner talk first.</p>", "SUPPORT": common_support, "FALLBACK": common_fallback},
        2: {"TITLE": "Individual Career Plan", "SUBTITLE": "50 minutes · Four-page plan", "ALERT": "<strong>Specific and revisable:</strong> The student chooses a current direction and alternative. The plan is not a permanent declaration or a pathway guarantee.", "PREP": f'<ul><li>Post {link(files["PLAN"]["id"], "the four-page career plan")} and private annotation route.</li><li>Keep each student\'s Day 1 map available.</li><li>State that this original Day 2 location is used for Major 2 scoring; no Day 4 duplicate upload.</li></ul>', "EVIDENCE": "<p>Collect current direction/alternative, career task, preparation/labor labels and limit, current high-school/training route and questions, three actions, dates, obstacle, backup, support, and flexible close.</p>", "FLOW": (
            flow(color, "Minutes 0-5 - Welcome and actionable career roadmap warm-up", '''<p>Welcome students, seat them with devices or the 4-page career plan, and project the career planning prompt.</p><ul><li>Ask students: <em>“Why is an individual career plan called a ‘living roadmap’ rather than a permanent contract? How does having a clear high school pathway with built-in flexible alternatives protect you if your interests change or college costs shift?”</em></li><li>Collect 2-3 student thoughts: Life changes and you need a Plan B; knowing the required classes early prevents wasted time!</li><li>Bridge with, <em>“Strategic career planning balances clear, immediate high school goals with long-term flexibility under TEKS d(8)(A), (B), and (C). Today we author our comprehensive 4-page Individual Career Plan—the cornerstone written component of Major 2.”</em></li></ul>''')
            + flow("#4c8b38", "Minutes 5-13 - 4-page career plan structure &amp; district CTE alignment", '''<p>Display the 4 Core Sections of the Individual Career Plan on the screen:</p><ul><li>1. <strong>Section 1 (Career Direction &amp; Daily Duties):</strong> Primary occupation target, alternative pathway, specific daily work products, and required technical tools.</li><li>2. <strong>Section 2 (Labor Market Reality Check):</strong> Sourced BLS May 2024 median wage, 2024-34 outlook percentage, annual openings, and explicit recognition of local entry-level limitations.</li><li>3. <strong>Section 3 (High School &amp; Postsecondary Pathway):</strong> Irving ISD high school endorsement (e.g., STEM, Business &amp; Industry, Public Services) at Singley Academy, Nimitz, MacArthur, Irving High, or Cardwell; required 9th-grade courses; postsecondary training (associates, bachelors, apprenticeship, military).</li><li>4. <strong>Section 4 (3-Year Action Pipeline &amp; Obstacle Mitigation):</strong> 3 concrete transition steps with target completion dates; identifying 1 realistic academic/financial obstacle and pairing it with a specific campus support resource.</li></ul>''')
            + flow("#155d7a", "Minutes 13-35 - Individual career plan authoring sprint (4-page plan)", '''<p>Students construct their 4-page career plan on their packet (or Canvas):</p><ul><li>Complete Sections 1 through 4 using verified evidence from Day 1.</li><li>Ensure all postsecondary degree, certification, and apprenticeship requirements match state standards.</li><li>Detail concrete high school course sequences from the Irving ISD Academic Planning Guide.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 21): Verify students include a viable alternative pathway (Pathway B) alongside their primary choice.<br>• Lap 2 (Minute 29): Ensure labor data includes full statistical labels and the local entry-level boundary.</li></ul>''')
            + flow("#d39b22", "Minutes 35-45 - Partner roadmap review &amp; obstacle mitigation check", '''<p>Elbow partners audit each other's career plans:</p><ul><li>Partner checks: 'Is the 3-step action plan realistic? Does the obstacle plan name a real school resource like a counselor or tutoring?'</li><li>Execute One Visible Plan Revision: Clarify high school course titles or sharpen the obstacle contingency.</li></ul>''')
            + flow(color, "Minutes 45-50 - Submit Day 2 Plan and wrap-up", '''<p>Students submit their completed 4-page plan in Canvas or file paper packets.</p><ul><li>Remind students: This submission is retained for Major 2 scoring; no duplicate upload on Day 4!</li><li><strong>Safe Trim:</strong> Provide pre-formatted Irving ISD high school pathway reference sheets; fiercely protect all 4 sections, alternative pathway, labor labels, and private submission.</li></ul>''')
        ), "MONITOR": "<p><strong>Watch for:</strong> national median relabeled as local starting pay; pathway label treated as admission; certification treated as degree/license; projection treated as guarantee. Score the evidence basis, not the career preference. Preserve all four pages; trim sharing first.</p>", "SUPPORT": common_support, "FALLBACK": common_fallback},
        3: {"TITLE": "Career Evidence Brief and Rehearsal", "SUBTITLE": "50 minutes · Two-page rehearsal plan", "ALERT": "<strong>Communication, not production:</strong> No public speech, camera, expensive design tool, or high-production video is required.", "PREP": f'<ul><li>Post {link(files["PRESENT"]["id"], "the two-page brief and rehearsal plan")} and private annotation route.</li><li>Assign live, small-group, conference, recording, and AAC routes before rehearsal.</li><li>Confirm one appropriate technology and one backup per route.</li></ul>', "EVIDENCE": "<p>Collect route/audience/privacy, appropriate technology, six speaking jobs, two timed attempts, feedback or self-check, visible revision, and backup.</p>", "FLOW": (
            flow(color, "Minutes 0-5 - Welcome and professional capstone briefing warm-up", '''<p>Welcome students, seat them with devices or the 2-page rehearsal plan, and project the oral briefing prompt.</p><ul><li>Ask students: <em>“When summarizing a complex, multi-year career plan in a concise 2-3 minute professional briefing, why must you lead with evidence and clear structure rather than rambling through every detail? How does using an evidence card or visual aid keep your delivery poised and authoritative?”</em></li><li>Collect 2-3 student thoughts: People tune out if you ramble; having notes keeps your numbers accurate and your timing sharp!</li><li>Bridge with, <em>“Executive briefings require concise synthesis and disciplined timing under TEKS d(4)(C). Today we map the 6 core speaking jobs of our capstone brief, select our technology route, and execute two timed rehearsals.”</em></li></ul>''')
            + flow("#4c8b38", "Minutes 5-13 - The 6 core speaking jobs &amp; technology routes", '''<p>Display the 6 Core Speaking Jobs of the Capstone Brief on the screen:</p><ul><li>1. <strong>Opening &amp; Direction (20s):</strong> Name primary career target and flexible alternative.</li><li>2. <strong>Core Job Duties &amp; Value (25s):</strong> Explain what the worker produces and who benefits.</li><li>3. <strong>Labor Market Evidence (30s):</strong> State May 2024 BLS median wage, 10-year growth projection, and local wage reality limit.</li><li>4. <strong>High School &amp; Training Route (35s):</strong> Name high school endorsement, CTE courses, and postsecondary requirements.</li><li>5. <strong>Next Action &amp; Contingency Plan (25s):</strong> Describe immediate 9th-grade goal, potential obstacle, and support system.</li><li>6. <strong>Closing &amp; Q&amp;A Prompt (15s):</strong> Conclude courteously and open the floor for questions.</li><li>Technology Route Options: (1) Small-group live presentation, (2) Teacher conference brief, (3) Private Canvas recording, (4) Speech-generating AAC device.</li></ul>''')
            + flow("#155d7a", "Minutes 13-30 - Brief planning &amp; script drafting sprint", '''<p>Students draft their concise briefing notes on page 1 of the rehearsal plan:</p><ul><li>Author structured talking points for all 6 speaking jobs (use bullet notes, not dense paragraphs!).</li><li>Prepare evidence cue card or approved digital visual with key data points.</li><li>Confirm primary communication route and test backup technology plan.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 19): Verify students write talking cues rather than essays to be read verbatim.<br>• Lap 2 (Minute 26): Confirm students record the labor data limitation in their speaking notes.</li></ul>''')
            + flow("#d39b22", "Minutes 30-45 - Timed Rehearsals 1 &amp; 2 and visible delivery revision", '''<p>Students execute two timed rehearsals with partners or recording devices:</p><ul><li>Rehearsal 1 (Minutes 30-37): Partner timer logs exact elapsed time (target: 2-3 minutes). Partner provides 1 specific strength and 1 delivery fix.</li><li>Visible Revision (Minutes 37-40): Edit speaking notes to adjust pacing or clarify confusing transitions.</li><li>Rehearsal 2 (Minutes 40-45): Run second rehearsal; verify timing and note improvement.</li></ul>''')
            + flow(color, "Minutes 45-50 - Submit Day 3 Rehearsal Plan and wrap-up", '''<p>Students submit their completed rehearsal plan in Canvas and prepare for Day 4 capstone presentations.</p><ul><li><strong>Safe Trim:</strong> Focus peer feedback on timing; fiercely protect 6-job outline, both timed rehearsals, visible revision, and private submission.</li></ul>''')
        ), "MONITOR": "<p><strong>Model order:</strong> direction/alternative; career task; preparation/labor; high-school/training; next action/support; limitation/close. Appropriate technology can be a private Canvas recording, evidence card, teacher-approved visual, or AAC technology. Preserve both attempts and revision; trim decoration first.</p>", "SUPPORT": common_support, "FALLBACK": common_fallback},
        4: {"TITLE": "Communicated Capstone and Revision", "SUBTITLE": "50 minutes · Major 2", "ALERT": "<strong>One new submission:</strong> The Day 2 plan stays in its original location. Students submit only Day 4 oral/AAC evidence, the two-page record, and self-score here.", "PREP": f'<ul><li>Post {link(files["DELIVERY"]["id"], "the two-page delivery/revision record")}, {link(files["RUBRIC"]["id"], "the two-page Major 2 profile")}, and the mapped private Major.</li><li>Confirm each communication route, appropriate technology, feedback source, and make-up route before class.</li><li>Do not run a serial whole-class roster.</li></ul>', "EVIDENCE": "<p>Score the Day 2 plan from its original location plus the Day 4 2-3-minute oral/AAC evidence, source labels, appropriate technology, feedback, visible revision, transfer action, and self-score.</p>", "FLOW": (
            flow(color, "Minutes 0-5 - Welcome and Major 2 capstone readiness gate", '''<p>Welcome students, execute the Major 2 capstone readiness gate, and project the presentation protocol.</p><ul><li><strong>Readiness Gate (Minutes 0-4):</strong> Confirm student presentation stations, parallel small groups, conference queue, recording spaces, and AAC setups. Review the 24-point Major 2 rubric.</li><li>Ask students: <em>“What does delivering this capstone represent for your high school transition? Why is the ability to articulate your career goals and back them with labor data a defining life skill?”</em></li><li>Collect 2-3 student thoughts: It shows we have a real plan and know what classes to take next year!</li><li>Bridge with, <em>“Today is Major 2: Communicated Capstone and Revision under TEKS d(4)(C) and d(8)(A)-(C)! Every student will communicate their capstone brief across assigned routes, receive feedback, execute a visible revision, and complete their 24-point self-score.”</em></li></ul>''')
            + flow("#4c8b38", "Minutes 5-32 - Dedicated parallel capstone delivery window", '''<p>Manage the parallel presentation stations, recording rooms, and teacher conference queue:</p><ul><li>Station 1 (Teacher Conference): Individual student presentations and oral checkoffs at the teacher desk.</li><li>Station 2 (Parallel Small Groups): Groups of 3-4 rotate delivering 2-3 minute briefs and logging peer feedback.</li><li>Station 3 (Private Digital Recordings &amp; AAC): Students recording on Chromebooks or utilizing speech-generating devices in designated quiet zones.</li><li>Teacher Logs Capstone Checkoff: Record student name, career, route, exact elapsed time, technology used, oral completion, and written delivery record status.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 12): Ensure quiet respectful environments across all parallel presentation pods.<br>• Lap 2 (Minute 24): Verify that student delivery times remain within the 2-3 minute window.</li></ul>''')
            + flow("#155d7a", "Minutes 32-42 - Feedback synthesis, visible revision &amp; self-scoring", '''<p>Students complete page 2 of their Delivery and Revision Record:</p><ul><li>Document 1 specific piece of feedback received (from teacher, peer, or recording review).</li><li>Execute One Visible Revision: Edit their career roadmap or presentation script to repair an identified gap.</li><li>Self-Score on the 24-Point Major 2 Rubric: Evaluate Career Plan Completeness, Labor Evidence Accuracy, Oral Presentation Structure, Technology Use, and Revision.</li></ul>''')
            + flow("#d39b22", "Minutes 42-50 - Submit Major 2 Package and wrap-up", '''<p>Students submit their completed 2-page delivery record and recorded media (if applicable) in Canvas.</p><ul><li>Teacher reminds class: Day 2 plan is scored from its original location; do not duplicate upload!</li><li>Congratulate students on successfully delivering their Career Evidence Capstone!</li><li><strong>Safe Trim:</strong> Shorten small-group feedback comments; fiercely protect oral/AAC evidence checkoff, visible revision, 24-point self-score, and private submission.</li></ul>''')
        ), "MONITOR": "<p><strong>Score:</strong> evidence, organization, labels, audience/time fit, appropriate technology, and revision. Do not score accent, eye contact, camera, public confidence, memorization, disability, or visual polish. Written planning supports but does not replace oral/AAC evidence unless an authorized accommodation defines the route. Preserve revision and self-score; trim celebration first.</p>", "SUPPORT": common_support, "FALLBACK": common_fallback},
        5: {"TITLE": "Reflection and Transfer Forward", "SUBTITLE": "50 minutes · Two-page private reflection", "ALERT": "<strong>Evidence over forced positivity:</strong> A student may name uncertainty, a changed direction, or a plan that still needs verification.", "PREP": f'<ul><li>Post {link(files["REFLECT"]["id"], "the two-page reflection and transfer plan")} and private annotation route.</li><li>Display the six module titles as a memory scaffold.</li><li>Keep celebration or public sharing optional and consent-based.</li></ul>', "EVIDENCE": "<p>Collect then/now evidence, one example per six weeks, three skill transfers, dated next action, support request, flexibility response, advice, and open question.</p>", "FLOW": (
            flow(color, "Minutes 0-5 - Welcome and year-long CCE retrospective warm-up", '''<p>Welcome students to the final day of College and Career Exploration! Project the course retrospective on the screen.</p><ul><li>Ask students: <em>“Think back to Day 1 of Week 0 when you first walked into this classroom. What did you think 'career exploration' meant back then versus what you know today? Which skill—researching labor data, drafting a resume, pitching a product, or mock interviewing—will serve you most in high school and beyond?”</em></li><li>Collect 2-3 student thoughts: We thought it was just taking surveys, but it was learning real-world workplace skills!</li><li>Bridge with, <em>“True career exploration is about discovering who you are, mastering transferable skills, and taking charge of your own future. Today we complete our final 2-page CCE Reflection and Transfer Plan under TEKS d(8)(C), documenting our journey across all 6 Six-Weeks and setting our high school launchpad.”</em></li></ul>''')
            + flow("#4c8b38", "Minutes 5-15 - Mapping the year across all 6 Six-Weeks", '''<p>Display the 6 Six-Weeks Milestone Retrospective on the main screen:</p><ul><li>1. <strong>1SW (Self-Knowledge &amp; Careers):</strong> Holland RIASEC personality themes &amp; work values (1SW).</li><li>2. <strong>2SW (Labor Market Evidence):</strong> BLS occupational data, wages, training levels, and future trends (2SW).</li><li>3. <strong>3SW (Postsecondary Pathways):</strong> College, technical degrees, military, apprenticeships, and financial aid literacy (3SW).</li><li>4. <strong>4SW (Financial Literacy &amp; Budgeting):</strong> Gross vs. net income, payroll deductions, housing costs, and emergency funds (4SW).</li><li>5. <strong>5SW (High-Demand Clusters):</strong> Health science, STEM engineering, architecture/trades, and real estate economics (5SW).</li><li>6. <strong>6SW (Career Launch &amp; Capstone):</strong> Professional resumes, cover letters, mock interviews, and individual career plans (6SW).</li><li>Students reflect on one breakthrough artifact from each six-weeks period.</li></ul>''')
            + flow("#155d7a", "Minutes 15-35 - Final reflection &amp; transfer plan authoring sprint", '''<p>Students author their 2-page final reflection in Canvas (or paper):</p><ul><li>Part 1 (Then vs. Now): Compare August beliefs with May accomplishments using concrete evidence.</li><li>Part 2 (Transferable Workforce Skills): Detail how 3 core CCE skills (critical data analysis, professional written communication, and structured oral pitching) will transfer to 9th-grade high school courses.</li><li>Part 3 (Immediate 9th-Grade Action Plan): Document one specific academic goal for August, one campus club/activity to join, and one school support resource (e.g., counselor, CTE coach).</li><li>Part 4 (Advice to Future CCE Students): Author a thoughtful piece of advice for incoming 8th graders starting this course next year.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 22): Verify students cite specific evidence rather than generic statements like 'I learned a lot.'<br>• Lap 2 (Minute 30): Confirm students name concrete high school support resources and specific goals.</li></ul>''')
            + flow("#d39b22", "Minutes 35-45 - Optional celebratory pair share &amp; open question formulation", '''<p>Students pair up for an optional, consent-based share-out:</p><ul><li>Share 9th-grade transition goals and favorite project memories with an elbow partner.</li><li>Formulate One Final Open Question: What is one question about high school or future careers you still want to investigate?</li></ul>''')
            + flow(color, "Minutes 45-50 - Submit Final Reflection, course completion &amp; farewell", '''<p>Students submit their completed 2-page reflection in Canvas and celebrate course completion.</p><ul><li>Teacher delivers closing words of encouragement: <em>“You have built a verified portfolio of career research, professional communication, and strategic planning. High school is your launchpad—own your journey!”</em></li><li><strong>Safe Trim:</strong> Keep celebratory sharing brief; fiercely protect Then/Now reflection, 3 transferable skills, 9th-grade action plan, and private submission.</li></ul>''')
        ), "MONITOR": "<p>Students may use module titles, old work, or a teacher conference to prompt recall. Do not require a class photo, family detail, public share, top-career declaration, H&amp;L login, or perfect memory. Preserve the dated action and skill transfer; trim optional sharing first.</p>", "SUPPORT": common_support, "FALLBACK": common_fallback},
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
        "INVENTORY": "6sw-wk6-career-evidence-inventory.pdf",
        "PLAN": "6sw-wk6-individual-career-plan.pdf",
        "PRESENT": "6sw-wk6-capstone-presentation-plan.pdf",
        "DELIVERY": "6sw-wk6-capstone-delivery-record.pdf",
        "REFLECT": "6sw-wk6-final-course-reflection.pdf",
        "RUBRIC": "6sw-wk6-capstone-rubric.pdf",
    }
    support_paths = {key: ROOT / "docs/resources/worksheets" / name for key, name in names.items()}
    visual_paths = {f"p{number}": ASSETS / f"fyf-p{number}.jpg" for number in [277, 278, 279, 280, 297, 298, 299, 300]}
    missing = [str(path) for path in [*support_paths.values(), *visual_paths.values()] if not path.is_file()]
    if missing:
        raise RuntimeError(f"Refusing partial Canvas write; missing upload dependencies: {missing}")

    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        mapped_major = await mapped_major_assignment(client)  # fail before any write
        module = await ensure_module(client)
        folder_path = "course files/CCR Materials/6SW/Wk6"
        folder = await common.ensure_folder(client, folder_path)
        files = {key: await common.upload(client, path, folder_path) for key, path in support_paths.items()}
        visual_folder_path = "course files/CCR Materials/6SW/Wk6/Locked Licensed Visuals"
        visual_folder = await common.ensure_folder(client, visual_folder_path)
        visuals = {key: await common.upload(client, path, visual_folder_path) for key, path in visual_paths.items()}

        assignments = {}
        for day, key in {1: "INVENTORY", 2: "PLAN", 3: "PRESENT", 5: "REFLECT"}.items():
            assignments[day] = await common.upsert_assignment(
                client,
                TITLES[day],
                "<p>Complete privately by Canvas annotation, upload, typed labeled responses, dictation, or paper. This practice is 0 points, omitted from the final grade, and unpublished for teacher transfer.</p>",
                ["student_annotation", "online_upload", "online_text_entry"],
                files[key]["id"],
            )
        major_description = f'<p>Submit {common.file_link(files["DELIVERY"]["id"], "the two-page delivery and revision record")}, private 2-3-minute oral/AAC evidence using appropriate technology, and {common.file_link(files["RUBRIC"]["id"], "the six-criterion self-score")}. The Day 2 plan stays where first submitted or turned in; do not upload it again.</p>'
        assignments[4] = await require_major_assignment(client, mapped_major, major_description, files["DELIVERY"]["id"])
        urls = {day: f"/courses/{COURSE_ID}/assignments/{assignment['id']}" for day, assignment in assignments.items()}
        students = student_content(files, visuals, urls)
        teachers = teacher_content(files)
        labels = {1: "Evidence Audit and Recovery", 2: "Individual Career Plan", 3: "Career Evidence Brief and Rehearsal", 4: "Communicated Capstone and Revision", 5: "Reflection and Transfer Forward"}
        order, pages = [], {}
        for day in range(1, 6):
            header_title = f"Day {day} · {labels[day]}"
            header = await prior.upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 6SW Wk6 Day {day} - {labels[day]}"
            student_page = await common.upsert_page(client, student_title, common.render("6sw-wk6-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, **CONTRACTS[day], **students[day]}))
            teacher_title = f"TEACHER: 6SW Wk6 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(client, teacher_title, common.render("6sw-wk6-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **CONTRACTS[day], **teachers[day]}))
            await prior.upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await prior.upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            await prior.upsert_item(client, module["id"], "Assignment", assignments[day]["id"], TITLES[day])
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title), ("Assignment", assignments[day]["id"], TITLES[day])]
            pages[day] = {"teacher": teacher_page, "student": student_page}

        def matches_item(entry, kind, key):
            return entry.get("type") == kind and ((kind == "SubHeader" and entry.get("id") == key) or (kind == "Page" and entry.get("page_url") == key) or (kind == "Assignment" and entry.get("content_id") == key))

        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        keep_ids = set()
        for kind, key, _title in order:
            match = next((entry for entry in items if entry["id"] not in keep_ids and matches_item(entry, kind, key)), None)
            if not match:
                raise RuntimeError(f"Missing expected Career Capstone module item: {kind} {key}")
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
            raise RuntimeError(f"Expected {len(order)} Career Capstone module items; found {len(ordered)}")
        for position, ((kind, key, _title), entry) in enumerate(zip(order, ordered), 1):
            if entry.get("position") != position or not matches_item(entry, kind, key):
                raise RuntimeError(f"Career Capstone module order mismatch at position {position}")

        folder_files = await lock_every_file_in_folder(client, folder)
        visual_files = await lock_every_file_in_folder(client, visual_folder)
        folder = await common.api(client, "GET", f"/folders/{folder['id']}")
        visual_folder = await common.api(client, "GET", f"/folders/{visual_folder['id']}")
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        if module.get("published") or not folder.get("locked") or not visual_folder.get("locked") or any(not record.get("locked") for record in [*folder_files, *visual_files]):
            raise RuntimeError("Career Capstone module must stay unpublished and every support/visual file and folder locked")
        for day in [1, 2, 3, 5]:
            assignment = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignments[day]['id']}")
            required_routes = {"student_annotation", "online_upload", "online_text_entry"}
            if assignment.get("published") or float(assignment.get("points_possible") or 0) != 0 or assignment.get("grading_type") != "percent" or not assignment.get("omit_from_final_grade"):
                raise RuntimeError(f"Day {day} practice assignment grading/publish mismatch")
            if not required_routes.issubset(set(assignment.get("submission_types") or [])) or assignment.get("annotatable_attachment_id") is None:
                raise RuntimeError(f"Day {day} practice assignment private-route mismatch")
            assignments[day] = assignment
        major = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignments[4]['id']}")
        required_major_routes = {"media_recording", "student_annotation", "online_upload", "online_text_entry"}
        if major.get("published") or float(major.get("points_possible") or 0) != 100 or major.get("grading_type") != "points" or major.get("omit_from_final_grade"):
            raise RuntimeError("Career Capstone Major grading/publish mismatch")
        if not required_major_routes.issubset(set(major.get("submission_types") or [])) or major.get("annotatable_attachment_id") is None:
            raise RuntimeError("Career Capstone Major private-route mismatch")
        assignments[4] = major
        if any(page.get("published") for pair in pages.values() for page in pair.values()):
            raise RuntimeError("Every Career Capstone page must remain unpublished")
        print(json.dumps({"module": {"id": module["id"], "published": module["published"]}, "folder": {"id": folder["id"], "locked": folder["locked"], "files_locked": len(folder_files)}, "visual_folder": {"id": visual_folder["id"], "locked": visual_folder["locked"], "files_locked": len(visual_files)}, "files": {key: record["id"] for key, record in files.items()}, "visuals": {key: record["id"] for key, record in visuals.items()}, "assignments": {str(day): {"id": assignment["id"], "published": assignment.get("published"), "points": assignment.get("points_possible"), "grading_type": assignment.get("grading_type"), "omit": assignment.get("omit_from_final_grade")} for day, assignment in assignments.items()}, "pages": {str(day): {kind: {"url": page["url"], "published": page["published"]} for kind, page in pair.items()} for day, pair in pages.items()}, "items": [{"position": entry["position"], "type": entry["type"], "title": entry["title"]} for entry in ordered]}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
