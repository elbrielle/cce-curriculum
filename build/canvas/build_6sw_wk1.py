"""Build the unpublished 6SW Week 1 Education evidence module."""

import asyncio
import json
import re
import sys

import httpx

import build_5sw_wk1 as prior


common = prior.common
COURSE_ID = common.COURSE_ID
STUDENT_GOOGLE_COPY_URLS = {
    1: "https://docs.google.com/document/d/1TV9Sj7HsZ_OSw73MHqmPiJfWuEJipFdFPvI6G9vk93E/copy",
    2: "https://docs.google.com/document/d/1y2ffBfWG9mMv1zQOSZYtEAlVE07ln48OaQaqnq1Yi34/copy",
    3: "https://docs.google.com/document/d/1V57pXkBKDWimyDlim2mItsQnpcb_0xQ-rD-qZakaoCc/copy",
    4: "https://docs.google.com/document/d/1ZmIBGhpL-cFm2sOa_iFC8Knx4TesO-cfy5L9Yr5hIkQ/copy",
    5: "https://docs.google.com/document/d/18aepfO9FqoYL-awRHJDTXyzDlTOJgN0vGfu1mgL4UL0/copy",
}


# One Google Doc per worksheet (build/google_docs/student_worksheet_docs.json).
# Keyed by (day, anchor label) so a worksheet button never opens the day's exit ticket.
STUDENT_WORKSHEET_COPY_URLS = {
    (1, 'the two-page evidence surface'): "https://docs.google.com/document/d/1mBACaAW-QhXxHkzDK1UYZAssiJ8lmLuylNlQ-6IP17U/copy",
    (2, 'the three-page route guide'): "https://docs.google.com/document/d/1ccSaH0aO_Vcnrq-T0SlLzpm682BLqWCgq6Y3h9HxD74/copy",
    (3, 'the two-page pathway support'): "https://docs.google.com/document/d/1xkxPVzqNV25rM_wr-9mtUEaKT3TY9LEialnhVaCyHYA/copy",
    (4, 'the two-page revision and service surface'): "https://docs.google.com/document/d/1shoevXcuFjVHFKFthGyPx9QoVb2FBtqeYPrjIixfPjI/copy",
    (5, 'the three-page portfolio'): "https://docs.google.com/document/d/1__QjsEwlfWNwpHvOvZMi_2s9PEy-BJg6KFP_4C8a0mI/copy",
}


def student_copy_link(day, label):
    url = STUDENT_WORKSHEET_COPY_URLS.get((day, label), STUDENT_GOOGLE_COPY_URLS[day])
    return f'<a href="{url}">{label}</a>'

ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/6sw/wk1"
MODULE_NAME = "6SW Wk1: Education — Learning Design, Routes, and Service"
RUBRIC_NOTE_MARKER = 'data-cce-rubric-note="cce-advisory-rubric-v1"'
WORKSHEET_FILES = {
    "CLASSROOM": "6sw-wk1-community-classroom-plan.pdf",
    "ROUTES": "6sw-wk1-texas-education-routes.pdf",
    "POSTINGS": "6sw-wk1-education-job-evidence.pdf",
    "PLAY": "6sw-wk1-teach-through-play-service.pdf",
    "PORTFOLIO": "6sw-wk1-education-evidence-portfolio.pdf",
    "RUBRIC": "6sw-wk1-education-portfolio-rubric.pdf",
}
VISUAL_FILES = {f"p{page}": f"fyf-p{page}.jpg" for page in range(213, 220)}
TITLES = {
    1: "PRACTICE: Community Classroom Learning-Space Plan",
    2: "PRACTICE: Texas Education Career Routes",
    3: "SUPPORT: Discover Learning Pathways",
    4: "PRACTICE: Teach Through Play and Service",
    5: "MINOR 1: Education Evidence Portfolio",
}
MINOR_ALIASES = ("MINOR 1: Education Career Evidence Portfolio",)


def preflight():
    required = [
        ROOT / "build/canvas/templates/6sw-wk1-student.html",
        ROOT / "build/canvas/templates/6sw-wk1-teacher.html",
        *(ROOT / "docs/resources/worksheets" / name for name in WORKSHEET_FILES.values()),
        *(ASSETS / name for name in VISUAL_FILES.values()),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"6SW Wk1 preflight missing required files: {missing}")

CONTRACTS = {
    1: {"TOPIC": "Learning Design", "OBJECTIVE": "Students will describe the Education and Training cluster and identify how two careers contribute to a learning-space design.", "TEKS": "d(1)(B), d(1)(C)", "DOL": "FYF team concept plus a two-page individual career-and-design explanation.", "I_CAN": "describe the Education and Training cluster and explain how two careers contribute to a learning-space design.", "SHOW": "Use the FYF concept once, then submit the two-page individual career-and-design explanation."},
    2: {"TOPIC": "Career Preparation", "OBJECTIVE": "Students will describe common Texas classroom-teacher requirements, compare two preparation patterns, and identify provider evidence needed before choosing a route.", "TEKS": "d(2)(A), d(2)(B)", "DOL": "Three-page Texas Education Career Routes comparison and evidence-based recommendation.", "I_CAN": "separate common Texas teacher requirements from provider details and compare two preparation patterns.", "SHOW": "Complete the three-page route comparison and make a recommendation that names the evidence still needed."},
    3: {"TOPIC": "Education Pathways", "OBJECTIVE": "Students will compare learning pathways to three careers and explain which pathway they would investigate first.", "TEKS": "d(2)(A), d(2)(B)", "DOL": "Completed Xello Discover learning pathways lesson plus one evidence-based pathway comparison.", "I_CAN": "compare learning pathways to three careers and explain which pathway I would investigate first.", "SHOW": "Complete Discover learning pathways in Xello and explain one pathway choice, benefit, and question."},
    4: {"TOPIC": "Service Learning", "OBJECTIVE": "Students will identify an early-childhood education work product, revise it from test evidence, and explain how service benefits a community while building skills transferable to two careers.", "TEKS": "d(1)(C), d(4)(E)", "DOL": "FYF activity plus a two-page individual revision and service analysis.", "I_CAN": "design and revise a child-friendly activity, then explain how service builds a skill used in two careers.", "SHOW": "Create and test the FYF activity once, then submit the two-page individual revision and service analysis."},
    5: {"TOPIC": "Career Evidence", "OBJECTIVE": "Students will synthesize career, preparation, learning-pathway, learning-design, and service evidence to justify an Education and Training direction and next action.", "TEKS": "d(1)(B), d(1)(C), d(2)(A), d(2)(B), d(4)(E)", "DOL": "Three-page Education Career Evidence Portfolio plus a visible one-page 16-point rubric.", "I_CAN": "use this week's evidence to justify an Education and Training direction, limitation, and next action.", "SHOW": "Submit the three-page portfolio, self-score with the one-page rubric, and make one visible revision."},
}


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    matches = [module for module in modules if module.get("name") == MODULE_NAME]
    if len(matches) > 1:
        raise RuntimeError(f"Expected at most one module named {MODULE_NAME!r}; found {len(matches)}")
    found = matches[0] if matches else None
    data = {"module[published]": "false", "module[name]": MODULE_NAME}
    if found:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data=data)
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


async def mapped_minor_assignment(client):
    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group_matches = [entry for entry in groups if entry.get("name") == "Minor Assessments (40%)"]
    if len(group_matches) != 1:
        raise RuntimeError(
            "Expected exactly one assignment group named 'Minor Assessments (40%)'; "
            f"found {len(group_matches)}"
        )
    group = group_matches[0]
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    accepted = {TITLES[5], *MINOR_ALIASES}
    matches = [entry for entry in assignments if entry.get("name") in accepted]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one existing mapped Education Minor named in {sorted(accepted)!r}; found {len(matches)}")
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
            f"Mapped Education Minor invariant failed before module writes: published={found.get('published')}, "
            f"points={found.get('points_possible')}, group={found.get('assignment_group_id')}, "
            f"grading={found.get('grading_type')}, omit={found.get('omit_from_final_grade')}, "
            f"rubric_note={rubric_note is not None}"
        )
    return found, group, rubric_note.group(0)


async def assert_annotation_assignment(client, assignment, source_attachment_id, *, mapped=False):
    assignment = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignment['id']}")
    source_file = await common.api(client, "GET", f"/files/{source_attachment_id}")
    annotation_id = int(assignment.get("annotatable_attachment_id") or 0)
    annotation_file = await common.api(client, "GET", f"/files/{annotation_id}") if annotation_id else {}
    if annotation_file and not annotation_file.get("locked"):
        annotation_file = await common.api(client, "PUT", f"/files/{annotation_id}", data={"locked": "true"})
    required_routes = {"student_annotation", "online_upload", "online_text_entry"}
    failures = {
        "published": assignment.get("published") is not False,
        "points": float(assignment.get("points_possible") or 0) != (100 if mapped else 0),
        "grading": assignment.get("grading_type") != ("points" if mapped else "percent"),
        "omit": assignment.get("omit_from_final_grade") is not (False if mapped else True),
        "routes": set(assignment.get("submission_types") or []) != required_routes,
        "annotation_missing": not annotation_id,
        "source_locked": source_file.get("locked") is not True,
        "clone_locked": annotation_file.get("locked") is not True,
        "clone_name": annotation_file.get("filename") != source_file.get("filename"),
        "clone_size": int(annotation_file.get("size") or -1) != int(source_file.get("size") or -2),
    }
    failed = [name for name, value in failures.items() if value]
    if failed:
        raise RuntimeError(f"Education annotation Assignment invariant failed for {assignment.get('name')!r}: {failed}")
    return assignment


async def assert_folder_files(client, folder, expected_names):
    """Require the current package and lock every file already in its module folder."""
    folder = await common.lock_folder_files(client, folder)
    files = await common.paged(client, f"/folders/{folder['id']}/files")
    actual = {record.get("display_name") or record.get("filename") for record in files}
    if folder.get("locked") is not True or any(record.get("locked") is not True for record in files):
        raise RuntimeError(f"Education folder lock invariant failed for {folder['id']}")
    missing = set(expected_names) - actual
    if missing:
        raise RuntimeError(
            f"Education folder is missing required files for {folder['id']}: "
            f"missing={sorted(missing)!r}, actual={sorted(actual)!r}"
        )
    return folder, files


async def upsert_practice_assignment(client, title, description, attachment_id):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == title]
    if len(matches) > 1:
        raise RuntimeError(f"Duplicate assignments named {title!r}: {[entry['id'] for entry in matches]}")
    found = matches[0] if matches else None
    assignment = await common.api(
        client,
        "PUT" if found else "POST",
        f"/courses/{COURSE_ID}/assignments/{found['id']}" if found else f"/courses/{COURSE_ID}/assignments",
        data={
            "assignment[name]": title,
            "assignment[description]": description,
            "assignment[published]": "false",
            "assignment[points_possible]": "0",
            "assignment[grading_type]": "percent",
            "assignment[omit_from_final_grade]": "true",
            "assignment[submission_types][]": ["student_annotation", "online_upload", "online_text_entry"],
            "assignment[annotatable_attachment_id]": str(attachment_id),
        },
    )
    return await assert_annotation_assignment(client, assignment, attachment_id)


async def require_minor_assignment(client, found, group, rubric_note, description, attachment_id):
    assignment = await common.api(client, "PUT", f"/courses/{COURSE_ID}/assignments/{found['id']}", data={
        "assignment[name]": TITLES[5],
        "assignment[description]": description + rubric_note,
        "assignment[published]": "false",
        "assignment[points_possible]": "100",
        "assignment[grading_type]": "points",
        "assignment[omit_from_final_grade]": "false",
        "assignment[assignment_group_id]": str(group["id"]),
        "assignment[submission_types][]": ["student_annotation", "online_upload", "online_text_entry"],
        "assignment[annotatable_attachment_id]": str(attachment_id),
    })
    assignment = await assert_annotation_assignment(client, assignment, attachment_id, mapped=True)
    if assignment.get("assignment_group_id") != group["id"] or RUBRIC_NOTE_MARKER not in (assignment.get("description") or ""):
        raise RuntimeError("Education Minor group/rubric invariant failed after update")
    return assignment


def student_content(files, visuals, urls):
    link, step = common.file_link, common.step
    media = lambda pairs: '<h3 style="color:#126b68;border-bottom:3px solid #a9d8d5">Workbook pages</h3>' + ''.join(prior.image_tag(visuals[key]["id"], alt) for key, alt in pairs)
    return {
        1: {"TITLE": "Community Classroom", "PURPOSE": "Turn the FYF brief into a learning-space concept that supports a real science goal.", "TODAY": "<ul><li>describe the cluster;</li><li>choose a learning goal;</li><li>map two Education careers;</li><li>explain and revise one design choice.</li></ul>", "READY": f'<p><strong>Read the FYF brief on pp. 213-215.</strong> Build the team concept once in FYF. Then record only your individual reasoning in {student_copy_link(1, "the two-page evidence surface")} or <a href="{urls[1]}">the private annotation activity</a>. Do not redraw the team poster.</p>', "MEDIA": media([("p213", "Education and Training cluster opener with three example careers"), ("p214", "Community Classroom scenario, requirements, goals, and science topics"), ("p215", "Community Classroom brainstorm, poster, presentation, and reflection steps")]), "STEPS": step(1, "Choose the learning goal", "<p>Name what third graders will learn, not only a decoration theme.</p>") + step(2, "Map two career contributions", "<p>Name what each worker produces or decides.</p>") + step(3, "Explain one design choice", "<p>Use the team FYF concept; explain how one choice supports learning, access, safety, or clarity.</p>") + step(4, "Write and revise", "<p>Add one feedback note and one individual revision recommendation.</p>"), "EXIT": "<p>Name one career, its contribution, one design choice, and the learning goal it supports.</p>", "DONE": "<ul><li>one team FYF concept;</li><li>one two-page individual explanation;</li><li>two distinct career contributions;</li><li>one evidence-based revision.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> learning goal/meta de aprendizaje · contribute/contribuir · investigate/investigar · access/acceso.</p><p><strong>Use this frame:</strong> The ___ contributes ___ so students can ___.</p>", "FALLBACK": "<p><strong>Complete no-team concept — Soil Detectives Lab:</strong> Third graders compare sealed soil samples, record observations, and explain how soil affects plant growth. The teacher sets the investigation sequence; the museum educator creates picture-based specimen prompts. Low materials shelves, wide table paths, sealed trays, and picture labels support access and safety. Headline: <em>Investigate soil like a scientist.</em> Feedback: the station labels look too similar. Recommended revision: add a different large picture and texture cue to each station. Use these facts for the same two-page individual questions. H&amp;L is not required.</p>"},
        2: {"TITLE": "Texas Education Career Routes", "PURPOSE": "Separate Texas requirements from the provider details a student still has to verify.", "TODAY": "<ul><li>read the five common requirements;</li><li>protect the Educational Aide I boundary;</li><li>compare two route patterns;</li><li>recommend what Jordan should verify.</li></ul>", "READY": f'<p>Open {student_copy_link(2, "the three-page route guide")} or <a href="{urls[2]}">the private annotation activity</a>.</p>', "MEDIA": "", "STEPS": step(1, "Mark statewide evidence", "<p>Keep TEA requirements separate from one provider's details.</p>") + step(2, "Read the Aide boundary", "<p>A pathway name alone does not guarantee certification.</p>") + step(3, "Compare route patterns", "<p>Degree timing differs; program quality, clinical route, cost, aid, and timing still require provider evidence.</p>") + step(4, "Advise Jordan", "<p>Cannot decide yet is valid when you name the missing evidence.</p>"), "EXIT": "<p>One statewide requirement, one provider-variable detail, and one question before enrollment.</p>", "DONE": "<ul><li>two common requirements;</li><li>Educational Aide I condition;</li><li>current Irving boundary;</li><li>three provider questions;</li><li>supported recommendation.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> requirement/requisito · provider/proveedor · varies/varía · verify/verificar.</p><p><strong>Use this frame:</strong> Jordan cannot choose from the route label alone. Jordan should compare ___ because ___.</p>", "FALLBACK": "<p>The fixed TEA and Irving evidence is complete. No application, provider contact, payment, Xello, eDynamic, or H&amp;L is required.</p>"},
        3: {"TITLE": "Xello Discover Learning Pathways", "PURPOSE": "Compare more than one way to prepare for careers that interest you.", "TODAY": "<ul><li>check three saved careers;</li><li>complete Discover learning pathways;</li><li>compare possible pathways;</li><li>explain one current preference and question.</li></ul>", "READY": f'<p>Open <strong>ClassLink &gt; Xello &gt; Home &gt; Lessons &gt; Discover learning pathways</strong>. Keep {student_copy_link(3, "the two-page pathway support")} open for the point-of-use word bank or the teacher-assigned no-device learning route.</p>', "MEDIA": "", "STEPS": step(1, "Check the prerequisite", "<p>The lesson needs three saved careers. If fewer than three appear, save three careers you are willing to compare. This is only the prerequisite for today’s assigned lesson.</p>") + step(2, "Complete the lesson", "<p>Compare university, community college, technical school, apprenticeship, straight-to-work, military, and other pathways Xello shows.</p>") + step(3, "Evaluate a pathway", "<p>Choose one career and explain one pathway benefit plus one question or concern.</p>") + step(4, "Finish privately", "<p>Your teacher verifies the lesson in the Completion Standards report. Do not submit a profile screenshot.</p>"), "EXIT": "<p>Name one career, one possible pathway, one benefit, and one question.</p>", "DONE": "<ul><li>three saved careers available;</li><li>Discover learning pathways completed;</li><li>one pathway benefit explained;</li><li>one question or limitation named.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> pathway/ruta · apprenticeship/aprendizaje · technical school/escuela técnica · university/universidad.</p><p><strong>Use this frame:</strong> A possible pathway to ___ is ___. It may fit because ___, but I still need to learn ___.</p>", "FALLBACK": "<p>If Xello is unavailable, use page 2 of the pathway support for the learning comparison. Tell your teacher so the required Xello lesson can move to supervised recovery. Paper does not count as completion.</p>"},
        4: {"TITLE": "Teach Through Play and Service", "PURPOSE": "Design and revise a child-friendly activity, then connect service to skills used across careers.", "TODAY": "<ul><li>use the FYF targets;</li><li>create the activity once;</li><li>record test evidence and revisions;</li><li>connect service to two careers.</li></ul>", "READY": f'<p><strong>Read the FYF brief on pp. 216-217.</strong> Create and test the activity once in FYF. Then record only your individual evidence in {student_copy_link(4, "the two-page revision and service surface")} or <a href="{urls[4]}">the private annotation activity</a>. Do not copy the full plan or map again.</p>', "MEDIA": media([("p216", "Teach Through Play scenario and gross and fine motor target skills"), ("p217", "Teach Through Play planning, test, improvement, and discussion steps")]), "STEPS": step(1, "Create one safe activity", "<p>Use FYF for the activity steps and provide a seated, supported, pre-cut, tear, trace, or other access-equivalent option.</p>") + step(2, "Test the activity", "<p>Partner, tabletop, teacher conference, or individual simulation are equal.</p>") + step(3, "Record evidence and revise", "<p>Name one point of confusion or access need and two evidence-based revisions.</p>") + step(4, "Analyze service", "<p>Use a real, planned, or supplied tutoring scenario without private disclosure.</p>"), "EXIT": "<p>Name one revision, one community benefit, and one skill used in two careers.</p>", "DONE": "<ul><li>one FYF activity created and tested;</li><li>one two-page individual evidence surface;</li><li>two evidence-based revisions;</li><li>community benefit;</li><li>two-career skill transfer.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> gross motor/motricidad gruesa · fine motor/motricidad fina · service/servicio · revision/revisión.</p><p><strong>Use this frame:</strong> Service benefits the community by ___. In a ___ career, the skill helps ___.</p>", "FALLBACK": "<p>The authenticated FYF images provide the brief. If the workbook or team is unavailable, use the complete teacher-supplied activity scenario; use individual simulation and the supplied library-tutoring scenario for the same two-page evidence route.</p>"},
        5: {"TITLE": "Education Evidence Portfolio", "PURPOSE": "Use five evidence types to justify a direction, limitation, and next action.", "TODAY": "<ul><li>read the current Irving evidence strip;</li><li>assemble the week's evidence;</li><li>self-score;</li><li>make one visible revision;</li><li>copy short portfolio phrases into Evidence Log Entry 6.</li></ul>", "READY": f'<p>Open {student_copy_link(5, "the three-page portfolio")}, {link(files["RUBRIC"]["id"], "the one-page rubric")}, and <a href="{urls[5]}">the private Minor 1 Assignment</a>. Retrieve the CCE Six-Weeks Evidence Log from your CCE binder or the teacher-designated digital folder. The log stays with you and is not part of Minor 1.</p>', "MEDIA": media([("p218", "Workbook Education and Training program context and I Am Next spotlight"), ("p219", "Workbook program, Educational Aide I, TAFE, endorsement, and field-experience context")]), "STEPS": step(1, "Keep current and workbook claims labeled", "<p>The portfolio includes a current Irving strip. FYF pp. 218-219 remain district-workbook context; time-sensitive promises need verification.</p>") + step(2, "Assemble five evidence types", "<p>Use career, preparation, learning-pathway, design/revision, and service evidence. The missing-work strip is an honest fallback.</p>") + step(3, "Conclude with a limit", "<p>Career preference is valid but is not the evidence being scored.</p>") + step(4, "Self-score and repair", "<p>Revise the weakest criterion before private submission.</p>") + step(5, "Submit, then transfer Entry 6", "<p>Submit the portfolio through the one private route your teacher names. During the final 2-3 minutes of the existing submit-and-cleanup block, copy short phrases from the completed portfolio: <strong>Artifact or task</strong> = Education Career Evidence Portfolio; <strong>Transferable skill</strong> = one skill you used; <strong>Evidence</strong> = one visible action from your strongest portfolio evidence; <strong>Revision or recovery move</strong> = your visible revision; <strong>Next step</strong> = the next action in your conclusion. Save the log in your CCE binder or teacher-designated digital folder. Do not upload it.</p>"), "EXIT": "<p>One supported conclusion, one limitation, and one next action.</p>", "DONE": "<ul><li>three-page portfolio;</li><li>current source/date and boundary;</li><li>five evidence types;</li><li>rubric self-score;</li><li>visible revision;</li><li>Entry 6 saved in your CCE binder or teacher-designated digital folder, not submitted or scored.</li></ul>", "SUPPORT": "<p><strong>Word bank:</strong> evidence/evidencia · pathway/programa de estudio · limitation/limitación · next action/próximo paso.</p><p><strong>Use this frame:</strong> The strongest evidence is ___. A limit is ___. My next action is ___ because ___.</p>", "FALLBACK": "<p>The portfolio contains a current Irving strip and a fixed missing-work strip. Day 3 learning-pathway evidence may come from completed Xello work or the fixed no-device comparison; H&amp;L and eDynamic 7.2 remain optional.</p><p><strong>If your Evidence Log is unavailable:</strong> write these five labels and short phrases in your CCE notebook or teacher-designated digital folder: artifact/task, skill, visible action, revision/recovery, next step. Transfer them into Entry 6 when the log returns. Do not reconstruct old work or submit this as another assignment.</p>"},
    }


def teacher_content(files):
    link, flow = common.file_link, common.flow
    color = "#126b68"
    sources = '<p><a href="https://tea.texas.gov/educators/certification/initial-certification/becoming-classroom-teacher-texas">TEA Classroom Teacher</a> · <a href="https://tea.texas.gov/educators/certification/becoming-educational-aide-texas">TEA Educational Aide</a> · <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte">Irving High School CTE</a>.</p>'
    support = '<p>Point to the visible word bank and complete frame before students write. Accept typing, dictation, annotation, enlarged print, bilingual labels, paper, private rehearsal, and teacher scribing. Score evidence and reasoning, not English mechanics unless meaning is unclear.</p>'
    fallback = '<p>Locked FYF images and fixed companions are the complete absence/platform route. No application, provider contact, public Discussion, personal volunteer disclosure, H&amp;L, Xello, eDynamic, or live job-board work is required.</p>'
    return {
        1: {"TITLE": "Community Classroom", "SUBTITLE": "50 minutes · FYF pp. 213-215 first", "ALERT": "<strong>Trim point:</strong> protect the learning goal, career contributions, and design reasoning; trim decorative poster work first.", "PREP": f'<ul><li><strong>Default:</strong> one device and FYF workbook per student, one projector, zero prints. Post {link(files["CLASSROOM"]["id"], "the two-page individual evidence companion")} and private annotation route.</li><li><strong>Paper:</strong> print one two-page companion per student; set one collection tray. Students use either paper or Canvas, not both.</li><li>Teams create the concept once in FYF. The companion is individual reasoning only. Optional partner feedback needs no extra materials; poster board is not required.</li></ul>', "EVIDENCE": "<p>Score the team FYF concept in place. Collect only the two-page individual goal, two career contributions, design-choice explanation, booking explanation, feedback, and revision.</p>", "MODEL": '<div style="border:1px solid #a9d8d5;border-radius:8px;padding:12px 16px;background:#f1fbfa"><p><strong>Complete fallback concept — Soil Detectives Lab:</strong> Third graders compare sealed soil samples, record observations, and explain how soil affects plant growth. The teacher sets the investigation sequence; the museum educator creates picture-based specimen prompts. Low materials shelves, wide table paths, sealed trays, and picture labels support access and safety. <strong>Headline:</strong> “Investigate soil like a scientist.” <strong>Feedback:</strong> the station labels look too similar. <strong>Revision:</strong> add a different large picture and texture cue to each station.</p><p><strong>Non-example:</strong> “Add blue walls because blue is calm.” Decoration alone does not show a learning purpose.</p></div>', "FLOW": (
            flow(color, "Minutes 0-5 - Welcome and classroom environment design warm-up", '''<p>Welcome students to Week 1 of 6SW (Education &amp; Training Cluster) and project the learning space prompt.</p><ul><li>Ask students: <em>“Think back to your favorite elementary classroom or an interactive science museum. What intentional choices did the educator make regarding furniture arrangement, accessible supplies, visual signage, and safety lanes to help every child learn?”</em></li><li>Collect 2-3 student thoughts: Low reachable shelves, clear walkways, visual picture labels, and organized learning stations!</li><li>Bridge with, <em>“Education professionals design experiences that empower diverse learners. Today we explore the Education &amp; Training cluster, analyze FYF pp. 213-215, and collaborate on an inclusive Community Classroom learning concept.”</em></li></ul>''')
            + flow("#4c8b38", "Minutes 5-14 - Specialized educator roles &amp; universal learning design modeling", '''<p>Deconstruct the 3 Specialized Roles and Universal Design Principles on the screen:</p><ul><li>1. <strong>Classroom Teacher:</strong> Plans curriculum objectives, guides direct instruction, and manages formative assessments.</li><li>2. <strong>Museum / Community Educator:</strong> Designs hands-on, object-based interactive learning exhibits and public outreach programs.</li><li>3. <strong>Instructional Designer:</strong> Develops learning materials, multimedia modules, and accessibility adaptations for diverse student populations.</li><li>Universal Learning Design Criteria: Spaces must have low, reachable material bins, wide pathways for wheelchair access, clear visual cues/labels, and physical safety boundaries.</li><li>Model the 'Soil Detectives Lab' Exemplar: Third graders investigate soil samples; the classroom teacher sets the investigation sequence while the museum educator designs tactile, picture-cued specimen prompts.</li></ul>''')
            + flow("#1f617a", "Minutes 14-35 - FYF Community Classroom concept design sprint (FYF pp. 213-215)", '''<p>Teams design their 3rd-grade science learning concept in FYF while each student completes their companion:</p><ul><li>Define One Concrete Learning Target: What measurable science skill will 3rd-grade students master?</li><li>Assign Specialized Educator Contributions: Document the distinct work products provided by the Teacher and the Museum Educator.</li><li>Detail Two Inclusive Physical Design Features: Explain how furniture layout and visual cues accommodate students with mobility or sensory differences.</li><li>Author the Booking Pitch Headline: Create a compelling 1-sentence headline explaining the educational value to a visiting school principal.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 21): Ensure student choices focus on pedagogical learning goals rather than superficial paint colors.<br>• Lap 2 (Minute 30): Check that every student documents accessibility features (e.g., wide aisles, sensory cues).</li></ul>''')
            + flow("#d39b22", "Minutes 35-45 - Booking evaluation, peer feedback &amp; concept revision", '''<p>Elbow partners evaluate their classroom concepts against the professional design standard:</p><ul><li>Partners provide one specific critique (e.g., 'Station labels look too similar and could confuse emergent readers').</li><li>Students execute an immediate design revision: Add high-contrast icons and tactile texture cues to enhance clarity.</li></ul>''')
            + flow(color, "Minutes 45-50 - Submit Day 1 Companion and folder storage", '''<p>Students submit their completed two-page companion in Canvas or place paper copies in the collection tray.</p><ul><li><strong>Safe Trim:</strong> Skip whole-class presentations; fiercely protect the 3rd-grade learning goal, two educator roles, accessibility design reasoning, and private exit.</li></ul>''')
        ), "MONITOR": "<ul><li><strong>Minute 12:</strong> every student has a third-grade science goal and two distinct Education roles. If one-third lists decorations only, project the model and rebuild one choice as goal → worker → design.</li><li><strong>Minute 30:</strong> each team FYF concept shows the learning action; each student has explained one design choice and one access or safety need. Students behind use the complete Soil Detectives Lab concept and continue the same individual questions.</li><li><strong>Minute 43:</strong> the booking explanation names learning, not just appearance, and one evidence-based revision.</li><li><strong>Trim/recovery:</strong> cut partner sharing and poster polish. Protect goal, roles, design reasoning, revision, submission, and cleanup. Save the same two-page artifact for recovery.</li></ul>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        2: {"TITLE": "Texas Education Career Routes", "SUBTITLE": "50 minutes · state requirements and provider evidence", "ALERT": "<strong>Accuracy boundary:</strong> do not call one preparation route automatically cheaper, faster, paid, unpaid, easier, or better.", "PREP": f'<ul><li><strong>Default:</strong> one device per student, one projector, zero prints. Post {link(files["ROUTES"]["id"], "the three-page fixed guide")} and annotation route.</li><li><strong>Paper:</strong> print one three-page guide per student and set one collection tray.</li><li>Students work individually. Open the current TEA teacher and Educational Aide pages for teacher reference only. Students do not open applications, contact providers, submit data, or pay fees.</li></ul>', "EVIDENCE": "<p>Collect statewide requirements, Educational Aide boundary, provider questions, and Jordan's evidence-based recommendation.</p>", "MODEL": '<div style="border:1px solid #a9d8d5;border-radius:8px;padding:12px 16px;background:#f1fbfa"><p><strong>Model:</strong> “Both routes must use an approved educator preparation program. Jordan still needs each provider\'s admission rules, clinical placement, total cost/aid, and timeline. The route label alone does not support a choice.”</p><p><strong>Non-example:</strong> “Alternative certification is always faster and cheaper.” Those facts vary by provider and candidate.</p></div>', "FLOW": (
            flow(color, "Minutes 0-5 - Welcome and educator preparation pathway myths warm-up", '''<p>Welcome students, seat them with devices or the 3-page guide, and project the teaching credential prompt.</p><ul><li>Ask students: <em>“To become a certified public school teacher in Texas, do you have to follow just one traditional 4-year education degree path, or can someone with an engineering or business degree switch into teaching later? What mandatory legal steps are required by the state?”</em></li><li>Collect 2-3 student thoughts: Traditional university degrees vs. post-baccalaureate alternative certification programs!</li><li>Bridge with, <em>“Texas needs dedicated educators across all subjects. Today we examine official Texas Education Agency (TEA) certification standards and compare the pathways to becoming a classroom teacher or educational aide.”</em></li></ul>''')
            + flow("#4c8b38", "Minutes 5-15 - TEA 5-step teacher certification &amp; educational aide rules", '''<p>Deconstruct TEA Certification Requirements on the main display:</p><ul><li>1. <strong>Five Common Requirements for Texas Classroom Teachers:</strong><br>• Step 1: Obtain a Bachelor's Degree from an accredited college or university.<br>• Step 2: Complete an Approved Educator Preparation Program (EPP) — either university-based or alternative certification.<br>• Step 3: Pass Texas Certification Exams (TExES Core Subjects / Content &amp; Pedagogy and Professional Responsibilities [PPR]).<br>• Step 4: Submit a State Teaching Application to TEA.<br>• Step 5: Complete Fingerprinting and National Background Review.</li><li>2. <strong>Educational Aide I Credentialing:</strong> High school diploma/GED, age 18+, completed district education courses or 30 college hours, written school superintendent verification, state application, and background check.</li><li>Route Neutrality Rule: Traditional and Alternative routes have different candidate profiles; one is not automatically 'better' or 'easier.' Provider admission rules, tuition costs, and clinical placement structures must be verified independently.</li></ul>''')
            + flow("#1f617a", "Minutes 15-29 - Statewide requirements vs. provider-variable audit sprint", '''<p>Students analyze the two routes in their fixed guide (or Canvas):</p><ul><li>Part 1: Categorize State Invariants vs. Provider Variables: Identify which 5 elements are legally mandated statewide vs. which vary by program (tuition cost, internship stipend, clinical teaching duration).</li><li>Part 2: Document Educational Aide I Boundary Conditions: Explain why graduating high school does NOT automatically grant an Educational Aide certificate.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 22): Verify students list all 5 TEA legal requirements.<br>• Lap 2 (Minute 27): Check that students identify superintendent verification for educational aides.</li></ul>''')
            + flow("#d39b22", "Minutes 29-42 - Fictional Jordan recommendation &amp; provider verification questions", '''<p>Students evaluate fictional Jordan's career pathway:</p><ul><li>Jordan has a bachelor's degree in Biology and wants to transition into teaching 8th-grade science while earning a salary. Which EPP model fits Jordan, and what 3 provider-specific details (tuition, mentor support, hiring district) must Jordan confirm before signing a contract?</li><li>Author 3 specific verification questions for an EPP admissions advisor.</li></ul>''')
            + flow(color, "Minutes 42-50 - Submit Day 2 Guide and wrap-up", '''<p>Students submit their completed guide in Canvas or turn in paper packets.</p><ul><li><strong>Safe Trim:</strong> Shorten partner sharing; fiercely protect the 5 TEA requirements, Educational Aide conditions, Jordan analysis, and private submission.</li></ul>''')
        ), "MONITOR": "<ul><li><strong>Minute 13:</strong> students can name two of the five common requirements and mark one provider-variable field. If one-third treats a route label as proof, sort four statements together.</li><li><strong>Minute 29:</strong> Educational Aide evidence includes age 18+, course/credit/grade conditions, written superintendent verification, and the application/background-review boundary without promising certification.</li><li><strong>Minute 42:</strong> Jordan response names three exact provider facts and may honestly say cannot decide yet.</li><li><strong>Trim/recovery:</strong> cut sharing, never the statewide/provider distinction, Aide boundary, decision, submission, or cleanup. Save the same guide for recovery.</li></ul>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        3: {"TITLE": "Xello Discover Learning Pathways", "SUBTITLE": "50 minutes · required Grade 7 Xello lesson", "ALERT": "<strong>Required task:</strong> protect Discover learning pathways. The actual prerequisite is at least three saved careers; students missing it save three careers only to enter the lesson.", "PREP": f'<ul><li><strong>Devices:</strong> one per student. Test ClassLink &gt; Xello &gt; Home &gt; Lessons &gt; Discover learning pathways in a demo account.</li><li>Open the Completion Standards report to the Grade 7 task and check the three-saved-careers prerequisite.</li><li>Post {link(files["POSTINGS"]["id"], "the two-page pathway support")}. Page 2 is the no-device learning route and does not create Xello completion.</li><li>Prepare a private status list: ready, prerequisite missing, access issue, absent, or complete.</li></ul>', "EVIDENCE": "<p>Verify Discover learning pathways in the Completion Standards report and check one career-pathway-benefit-question comparison. Do not collect profile screenshots or report a separate Save careers completion task.</p>", "MODEL": '<div style="border:1px solid #a9d8d5;border-radius:8px;padding:12px 16px;background:#f1fbfa"><p><strong>Model:</strong> “A possible pathway to instructional design is university study in education, design, or technology. It may fit because the work combines teaching and media, but I still need to compare program cost, course content, and experience requirements.”</p><p><strong>Non-example:</strong> “University is always best.” The route must fit the career and evidence.</p></div>', "FLOW": (
            flow(color, "Minutes 0-5 - Welcome and postsecondary pathway comparison warm-up", '''<p>Welcome students, seat them at Chromebooks, and project the Xello pathway prompt.</p><ul><li>Ask students: <em>“When high school seniors prepare for the workforce, what are the distinct differences between enrolling in a 4-year university, attending a 2-year community college technical program, entering an apprenticeship, or directly joining the military or workforce?”</em></li><li>Collect 2-3 student thoughts: Degrees, technical certificates, on-the-job training, tuition costs, and career timelines!</li><li>Bridge with, <em>“Every career has multiple educational doorways. Today we complete the required Grade 7 Xello lesson: 'Discover Learning Pathways,' connecting diverse training routes to your saved careers.”</em></li></ul>''')
            + flow("#4c8b38", "Minutes 5-15 - Xello login, prerequisite check &amp; navigation modeling", '''<p>Guide students through the ClassLink launch to Xello on the screen:</p><ul><li>Click Path: ClassLink &rarr; Xello &rarr; Home &rarr; Lessons &rarr; 'Discover Learning Pathways.'</li><li>Prerequisite Gate: This lesson requires at least 3 saved careers in Xello. If a student is missing this prerequisite, guide them to quickly search and save 3 careers of interest before starting the module.</li><li>Deconstruct the 4 Core Postsecondary Pathways in Xello:<br>• 1. <strong>University / 4-Year College:</strong> Bachelor's degrees, broad academic disciplines, professional credentials.<br>• 2. <strong>Community / Technical College:</strong> Associate degrees, 1-year career certificates, practical trade labs.<br>• 3. <strong>Apprenticeship:</strong> Paid on-the-job training under skilled mentors + evening technical coursework.<br>• 4. <strong>Direct Workforce / On-the-Job Training:</strong> Immediate employment with employer-provided training.</li></ul>''')
            + flow("#1f617a", "Minutes 15-45 - Independent Xello lesson completion sprint", '''<p>Students navigate and complete the interactive 'Discover Learning Pathways' module in Xello:</p><ul><li>Investigate how different learning pathways prepare workers for varied levels of responsibility and pay.</li><li>Compare educational requirements across at least two saved careers in their personal profile.</li><li>Synthesize Pathway Benefits: Identify one unique advantage and one potential tradeoff of university study vs. technical training.</li><li>Offline / Absence Fallback: Students unable to access Xello complete page 2 of the fixed pathway support packet.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 23): Verify all students have cleared the prerequisite and are actively progressing through lesson screens.<br>• Lap 2 (Minute 38): Monitor completion progress on the Xello educator dashboard; assist students with vocabulary or screen prompts.</li></ul>''')
            + flow(color, "Minutes 45-50 - Dashboard completion check and wrap-up", '''<p>Teacher verifies 100% completion on the Xello Completion Standards report:</p><ul><li>Students record one career pathway insight and log off devices safely.</li><li><strong>Safe Trim:</strong> Protect the 30-minute Xello interactive completion window; trim open-class discussion.</li></ul>''')
        ), "MONITOR": "<ul><li><strong>Minute 8:</strong> every student is in the assigned lesson or has a named prerequisite/access barrier.</li><li><strong>Minute 15:</strong> students can access three saved careers. If several are missing them, model one save without ranking or public sharing.</li><li><strong>Minute 30:</strong> students compare pathways rather than only naming careers.</li><li><strong>Minute 45:</strong> lesson completion is visible or supervised recovery is recorded.</li><li><strong>Trim/recovery:</strong> shorten the warm-up discussion, not the assigned lesson. Paper supports learning but does not count as completion.</li></ul>", "RESOURCES": '<p><a href="https://help.xello.world/en-us/content/Knowledge-Base/Xello-6-12/Lessons/List-of-Lessons.htm">Xello lesson list and prerequisites</a> · <a href="https://help.xello.world/en-us/content/Resources/PDFs/Lesson-Resources-6-12/Discover-Learning-Pathways.pdf">Xello Discover learning pathways lesson overview</a></p>', "SUPPORT": support, "FALLBACK": "<p>Use page 2 of the pathway support for the learning comparison when Xello is unavailable. Record the barrier and schedule supervised completion; paper does not count as Xello completion.</p>"},
        4: {"TITLE": "Teach Through Play and Service", "SUBTITLE": "50 minutes · FYF pp. 216-217 first", "ALERT": "<strong>Access boundary:</strong> physical performance, cutting skill, disability, artistry, disclosure, and partner attendance are not scored.", "PREP": f'<ul><li><strong>Default:</strong> one device and FYF workbook per student, one projector, zero prints. Post {link(files["PLAY"]["id"], "the two-page individual evidence companion")} and private annotation route.</li><li><strong>Paper:</strong> print one two-page companion per student and set one collection tray. Students use either paper or Canvas, not both.</li><li><strong>Optional physical test, per pair:</strong> one pair of teacher-approved scissors and two sheets of scrap paper. Clear one safe tabletop or movement lane. Tabletop, teacher-conference, and individual simulation need no physical materials.</li></ul>', "EVIDENCE": "<p>Score the FYF activity plan in place. Collect only the two-page individual test evidence, two revisions, community benefit, and two-career skill transfer.</p>", "MODEL": '<div style="border:1px solid #a9d8d5;border-radius:8px;padding:12px 16px;background:#f1fbfa"><p><strong>Model:</strong> “Children carry a picture card to the matching station, then tear or trace a matching shape. During a tabletop test, the station labels were too similar. I added one large picture and one texture cue to each station. This improves clarity and access.”</p><p><strong>Service model:</strong> “The library volunteer helps a child finish their own work and practices breaking directions into steps. Teachers and museum educators both use that skill with different audiences.”</p><p><strong>Non-example:</strong> “The partner liked it, so no revision is needed.”</p></div>', "FLOW": (
            flow(color, "Minutes 0-5 - Welcome and early childhood learning activity warm-up", '''<p>Welcome students, seat them with FYF workbooks (pp. 216-217) or companions, and project the play-based learning prompt.</p><ul><li>Ask students: <em>“When toddlers and kindergarteners play with building blocks or sorting games, what foundational cognitive and physical skills are they actually developing? How do educators use play to teach problem-solving and motor coordination?”</em></li><li>Collect 2-3 student thoughts: Spatial reasoning, gross and fine motor control, sharing, and language development!</li><li>Bridge with, <em>“Play is the primary vehicle through which young children learn. Today we complete FYF pp. 216-217, design a structured 'Teach Through Play' activity, test and revise it, and analyze how community service builds workforce skills under TEKS d(4)(E).”</em></li></ul>''')
            + flow("#4c8b38", "Minutes 5-11 - Learning targets, child safety &amp; accessibility modeling", '''<p>Display Activity Design Constraints and Child Safety Standards on the screen:</p><ul><li>1. <strong>Dual Motor Skill Targets:</strong> Every activity must target either Gross Motor Skills (large muscle movement: running, jumping, balancing) OR Fine Motor Skills (small muscle coordination: pinching, tracing, grasping).</li><li>2. <strong>Inclusive Accessibility Adaptations:</strong> Design adaptations for children with sensory processing sensitivities or motor impairments (e.g., enlarged grips, high-contrast visual cues).</li><li>3. <strong>Child Safety Boundaries:</strong> No choking hazards (&lt;1.25 inches), no sharp edges, non-toxic materials only, and clear adult supervision rules.</li><li>TEKS d(4)(E) Service Connection: Volunteering at libraries, summer camps, or youth sports builds transferable skills (patience, active listening, de-escalation, clear instruction) valued in every high-wage profession.</li></ul>''')
            + flow("#1f617a", "Minutes 11-28 - FYF activity design &amp; prototype sprint (FYF pp. 216-217)", '''<p>Teams author their activity on FYF pp. 216-217 while each student records on their companion:</p><ul><li>Define Activity Name, Age Group (Ages 3-5), and Targeted Motor Skill.</li><li>List Step-by-Step Child Instructions: Use clear, simple language with visual icon prompts.</li><li>Document Materials and Inclusive Modifications: Explain how a child with physical or visual limitations can participate equally.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 18): Verify activities contain specific motor targets and zero safety hazards.<br>• Lap 2 (Minute 25): Check that directions are written in child-friendly, actionable language.</li></ul>''')
            + flow("#d39b22", "Minutes 28-38 - Tabletop simulation, peer testing &amp; two revisions", '''<p>Partners conduct a 5-minute tabletop test of the activity:</p><ul><li>Partner acts as a 4-year-old following the instructions: Where did confusion or physical difficulty occur?</li><li>Record Two Evidence-Based Revisions: Document the test observation and explain how the revision improves clarity or safety (e.g., 'Added color-coded floor circles to prevent crowding').</li></ul>''')
            + flow("#1f617a", "Minutes 38-45 - Community service &amp; workforce skill transfer synthesis (TEKS d(4)(E))", '''<p>Students analyze the community volunteerism case study on page 2 of their companion:</p><ul><li>Identify One Community Need addressed by youth volunteerism (e.g., library reading programs).</li><li>Demonstrate Transferable Skill Mapping: Explain how managing children during community service directly develops workforce competencies required by healthcare workers, teachers, or corporate managers.</li></ul>''')
            + flow(color, "Minutes 45-50 - Submit Day 4 Companion and wrap-up", '''<p>Students submit their completed companion in Canvas or hand in paper packets.</p><ul><li><strong>Safe Trim:</strong> Use tabletop simulation rather than physical movement; fiercely protect the 2 test revisions, service analysis, and private submission.</li></ul>''')
        ), "MONITOR": "<ul><li><strong>Minute 11:</strong> the FYF activity includes a gross-motor target and fine-motor or access-equivalent target. If one-third treats access as an afterthought, model the picture/texture cue.</li><li><strong>Minute 27:</strong> every team has one testable FYF activity; students can name the action, materials, and one safety/access support without recopied plans.</li><li><strong>Minute 38:</strong> each student's two revisions name test evidence and why each helps.</li><li><strong>Minute 45:</strong> service analysis names a community benefit and one skill used in two careers; redirect personal disclosure to the supplied library scenario.</li><li><strong>Trim/recovery:</strong> use individual simulation and cut sharing. Protect two revisions, service transfer, submission, and material cleanup. Save the same two-page artifact for recovery.</li></ul>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback},
        5: {"TITLE": "Education Evidence Portfolio", "SUBTITLE": "50 minutes · Minor 1 evidence synthesis", "ALERT": "<strong>Minor 1:</strong> score the three-page portfolio with the visible 16-point rubric. Do not score career preference, private history, platform access, artwork, or Evidence Log Entry 6.", "PREP": f'<ul><li><strong>Default:</strong> one device per student, one projector, zero prints. Post {link(files["PORTFOLIO"]["id"], "the three-page portfolio")}, {link(files["RUBRIC"]["id"], "the one-page rubric")}, and private Minor 1 Assignment.</li><li><strong>Paper:</strong> print one three-page portfolio and one one-page landscape rubric per student; set one collection tray.</li><li>Have students retrieve the CCE Six-Weeks Evidence Log from the paper CCE binder or teacher-designated digital folder. Do not attach it to Minor 1 or print a second copy by default.</li><li>Students submit individually. Open current Irving evidence and FYF pp. 218-219. Missing earlier work uses the fixed strip, not reconstruction of four lessons.</li></ul>', "EVIDENCE": "<p>Collect one self-contained portfolio with career/source, preparation/learning-pathway, design/revision/service, conclusion/limitation/action, self-score, and revision. Entry 6 is a separate student-kept transfer and is not part of the Minor 1 evidence or score.</p>", "MODEL": '<div style="border:1px solid #a9d8d5;border-radius:8px;padding:12px 16px;background:#f1fbfa"><p><strong>Complete model strip:</strong> “The August 2026 Irving page lists Education and Training at Irving High, MacArthur, and Nimitz, but it does not guarantee admission or certification. A teacher commonly needs an approved EPP; provider cost and clinical placement still need verification. Xello showed university and alternative learning pathways to education-related careers, but I still need to compare program cost and requirements. My learning-space revision added picture cues after the test showed confusing labels. Tutoring service builds the skill of breaking directions into steps. Education currently fits because I value explaining ideas, but I still need to verify a program and observe the daily work.”</p><p><strong>Non-example:</strong> “I like teaching, so the pathway guarantees me a job.”</p></div>', "FLOW": (
            flow(color, "Minutes 0-7 - Welcome and Irving ISD Education pathways model warm-up", '''<p>Welcome students, seat them with their Week 1 artifacts or fixed facts, and project the CTE pathway prompt.</p><ul><li>Ask students: <em>“When reviewing the Irving ISD high school coursebook for Education &amp; Training at Irving High, MacArthur, Nimitz, or Cardwell, what does a public pathway listing guarantee, and what does it NOT guarantee?”</em></li><li>Collect 2-3 student thoughts: It lists course options, but does not guarantee automatic college credit, job placement, or teacher certification without passing exams!</li><li>Bridge with, <em>“Today is Minor 1: Education Evidence Portfolio! We synthesize our research on education careers, state certification routes, Xello learning pathways, and community service into a comprehensive 3-page portfolio scored against our 16-point rubric.”</em></li></ul>''')
            + flow("#4c8b38", "Minutes 7-12 - Portfolio architecture &amp; 16-point Minor 1 rubric deconstruction", '''<p>Display the 4 Core Portfolio Sections on the main screen:</p><ul><li>1. <strong>Career &amp; Source Labeling:</strong> Document one education occupation with complete statistical labels and local Irving ISD CTE pathway details.</li><li>2. <strong>Preparation &amp; Learning Pathway:</strong> Synthesize the 5-step TEA teacher certification route and compare postsecondary learning pathways explored in Xello.</li><li>3. <strong>Design, Revision &amp; Service:</strong> Document the 'Teach Through Play' activity, two evidence-based revisions, and transferable workforce skills built through community service (TEKS d(4)(E)).</li><li>4. <strong>Conclusion, Limitation &amp; Action:</strong> Author an evidence-based career fit judgment, acknowledge one preparation challenge, and state a concrete next action.</li><li>Review the 16-Point Rubric across all 4 criteria: Masters, Meets, Approaches, Needs Improvement.</li></ul>''')
            + flow("#1f617a", "Minutes 12-33 - Independent Minor 1 Portfolio assembly sprint", '''<p>Students complete their 3-page Minor 1 Portfolio in Canvas (or paper packet):</p><ul><li>Section 1: Connect career profiles to Irving High, MacArthur, Nimitz, or Cardwell high school sequences.</li><li>Section 2: Detail TEA bachelor's + EPP + TExES requirements and evaluate Xello pathway trade-offs.</li><li>Section 3: Record activity prototype testing, two revisions, and library volunteer skill transfer.</li><li>Section 4: Author personal conclusion, limitation, and concrete next step for high school course selection.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 18): Check that students cite specific facts from Days 1-4.<br>• Lap 2 (Minute 27): Verify conclusion includes an evidence limit and next action.</li></ul>''')
            + flow("#d39b22", "Minutes 33-43 - Rubric self-score &amp; visible portfolio revision", '''<p>Students evaluate their portfolio against the 16-point rubric:</p><ul><li>Score each of the 4 sections honestly.</li><li>Execute a 2-minute visible revision: Elevate the evidence in their lowest-scoring section by adding specific data or clarifying a boundary.</li></ul>''')
            + flow(color, "Minutes 43-50 - Submit Minor 1, transfer Entry 6 &amp; Week 1 wrap-up", '''<p>Students submit Minor 1 in Canvas and complete their student-kept log:</p><ul><li>Submit completed portfolio in Canvas or hand in paper packets.</li><li><strong>Evidence Log Transfer (Final 3 Minutes, Min 47-50):</strong> Retrieve the CCE Six-Weeks Evidence Log from binder; copy five short phrases into Entry 6 (Artifact: 6SW Minor 1 Portfolio; Transferable Skill: Activity Design &amp; Instruction; Visible Evidence: 2 test revisions; Revision: Rubric self-check; Next Step: Irving CTE high school course selection). Store log in binder!</li><li><strong>Safe Trim:</strong> Skip general debrief; fiercely protect all 4 portfolio sections, rubric self-audit, and private submission.</li></ul>''')
        ), "MONITOR": "<ul><li><strong>Minute 10:</strong> every student has prior evidence or the fixed missing-work strip and one source/date boundary.</li><li><strong>Minute 25:</strong> preparation/pathway and design/revision/service evidence are visible. If one-third writes preference only, project the complete model strip.</li><li><strong>Minute 38:</strong> conclusion uses four evidence types, one limit, and one specific next action. Labeled bullets are acceptable; do not cut a rubric job.</li><li><strong>Minute 45:</strong> all four self-scores and one visible revision are complete.</li><li><strong>Minute 48:</strong> the portfolio is submitted and five short phrases are saved in Entry 6 or the named fallback location. This early 6SW transfer gives the later résumé and interview lessons an evidence source without requiring another upload.</li><li><strong>Trim/recovery:</strong> cut sharing and workbook rereading. Protect every rubric criterion, revision, private submission, the short Entry 6 transfer, and cleanup. Save the same portfolio for a scheduled recovery window; do not add a second packet.</li></ul>", "RESOURCES": sources, "SUPPORT": support, "FALLBACK": fallback + '<p><strong>Day 5 Evidence Log fallback:</strong> if the log is unavailable, the student saves five labeled short phrases in the CCE notebook or teacher-designated digital folder and transfers them when the log returns. Do not collect the fallback, reconstruct old work, or create another submission.</p>'},
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
    preflight()
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        # Validate the weighted object before the first Canvas mutation.
        mapped_minor, minor_group, rubric_note = await mapped_minor_assignment(client)
        module = await ensure_module(client)
        path = "course files/CCR Materials/6SW/Wk1"
        folder = await common.ensure_folder(client, path)
        files = {key: await common.upload(client, ROOT / "docs/resources/worksheets" / name, path) for key, name in WORKSHEET_FILES.items()}
        folder, folder_files = await assert_folder_files(client, folder, WORKSHEET_FILES.values())
        visual_path = "course files/CCR Materials/6SW/Wk1/Locked Licensed Visuals"
        visual_folder = await common.ensure_folder(client, visual_path)
        visuals = {key: await common.upload(client, ASSETS / name, visual_path) for key, name in VISUAL_FILES.items()}
        visual_folder, visual_folder_files = await assert_folder_files(client, visual_folder, VISUAL_FILES.values())
        assignments = {}
        for day, key in {1: "CLASSROOM", 2: "ROUTES", 4: "PLAY"}.items():
            assignments[day] = await upsert_practice_assignment(client, TITLES[day], "<p>Complete privately by annotation, upload, typed labeled responses, or paper. Use one response route, not all routes. This practice is worth 0 points, omitted from the final grade, and unpublished.</p>", files[key]["id"])
        assignments[5] = await require_minor_assignment(client, mapped_minor, minor_group, rubric_note, "<p>Submit the private three-page Education Evidence Portfolio by annotation, upload, or typed labeled response; the teacher may collect the same labeled paper portfolio. Use the visible 16-point rubric. Career preference, artwork, platform access, English mechanics unless meaning is unclear, private service history, and submission mode do not determine the score.</p>", files["PORTFOLIO"]["id"])
        urls = {day: f"/courses/{COURSE_ID}/assignments/{assignment['id']}" for day, assignment in assignments.items()}
        students = student_content(files, visuals, urls)
        teachers = teacher_content(files)
        labels = {1: "Community Classroom", 2: "Texas Education Career Routes", 3: "Xello Discover Learning Pathways", 4: "Teach Through Play and Service", 5: "Education Evidence Portfolio"}
        interactions = {1: ("Assignment", assignments[1]["id"], TITLES[1]), 2: ("Assignment", assignments[2]["id"], TITLES[2]), 4: ("Assignment", assignments[4]["id"], TITLES[4]), 5: ("Assignment", assignments[5]["id"], TITLES[5])}
        order, pages = [], {}
        for day in range(1, 6):
            header_title = f"Day {day} · {labels[day]}"
            header = await prior.upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 6SW Wk1 Day {day} - {labels[day]}"
            student_page = await common.upsert_page(client, student_title, common.render("6sw-wk1-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, **CONTRACTS[day], **students[day]}))
            teacher_title = f"TEACHER: 6SW Wk1 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(client, teacher_title, common.render("6sw-wk1-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **CONTRACTS[day], **teachers[day]}))
            await prior.upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await prior.upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title)]
            if day in interactions:
                kind, key, title = interactions[day]
                await prior.upsert_item(client, module["id"], kind, key, title)
                order.append((kind, key, title))
            pages[day] = {"teacher": teacher_page, "student": student_page}

        ordered = await prior.reconcile_module_items(client, module["id"], order)
        if len(ordered) != 19:
            raise RuntimeError(f"Expected 19 exact Education module items; found {len(ordered)}")

        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
        if module.get("published") or len([entry for entry in modules if entry.get("name") == MODULE_NAME]) != 1:
            raise RuntimeError(f"Final Education module invariant failed: published={module.get('published')}")
        for day, pair in pages.items():
            for kind, page in pair.items():
                fresh = await common.api(client, "GET", f"/courses/{COURSE_ID}/pages/{page['url']}")
                if fresh.get("published"):
                    raise RuntimeError(f"Education Day {day} {kind} page is published")
                pair[kind] = fresh
        for day, key in {1: "CLASSROOM", 2: "ROUTES", 4: "PLAY"}.items():
            assignments[day] = await assert_annotation_assignment(client, assignments[day], files[key]["id"])
        assignments[5] = await assert_annotation_assignment(client, assignments[5], files["PORTFOLIO"]["id"], mapped=True)
        if assignments[5].get("assignment_group_id") != minor_group["id"] or RUBRIC_NOTE_MARKER not in (assignments[5].get("description") or ""):
            raise RuntimeError("Final Education Minor group/rubric invariant failed")
        folder, folder_files = await assert_folder_files(client, folder, WORKSHEET_FILES.values())
        visual_folder, visual_folder_files = await assert_folder_files(client, visual_folder, VISUAL_FILES.values())
        print(json.dumps({"module": {"id": module["id"], "published": module["published"]}, "folder": {"id": folder["id"], "locked": folder["locked"], "files_locked": len(folder_files)}, "visual_folder": {"id": visual_folder["id"], "locked": visual_folder["locked"], "files_locked": len(visual_folder_files)}, "files": {key: record["id"] for key, record in files.items()}, "visuals": {key: record["id"] for key, record in visuals.items()}, "assignments": {str(day): {"id": assignment["id"], "published": assignment.get("published"), "points": assignment.get("points_possible"), "grading_type": assignment.get("grading_type"), "omit_from_final_grade": assignment.get("omit_from_final_grade")} for day, assignment in assignments.items()}, "pages": {str(day): {kind: {"url": page["url"], "published": page["published"]} for kind, page in pair.items()} for day, pair in pages.items()}, "items": [{"position": entry["position"], "type": entry["type"], "title": entry["title"]} for entry in ordered]}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
