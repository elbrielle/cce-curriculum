"""Build the unpublished 5SW Week 3 Construction evidence module."""

import asyncio
import json
import re
import sys

import httpx

import build_5sw_wk1 as prior


common = prior.common
COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/5sw/wk3"
MODULE_NAME = "5SW Wk3: Construction — Routes, Evidence, and Observation"

CAREER_TITLE = "PRACTICE: Construction Career Evidence"
ROUTES_TITLE = "PRACTICE: Construction Routes and Organizations"
CLASSIFY_TITLE = "MINOR 3: Construction Labor-Evidence Classification"
REPORT_TITLE = "FORMATIVE: Construction Evidence Report and Briefing"
RUBRIC_NOTE_MARKER = 'data-cce-rubric-note="cce-advisory-rubric-v1"'
WORKSHEET_FILES = {
    "CAREER": "5sw-wk3-construction-career-evidence.pdf",
    "ROUTES": "5sw-wk3-routes-and-organizations.pdf",
    "CLASSIFY": "5sw-wk3-labor-classification.pdf",
    "REPORT": "5sw-wk3-fictional-evidence-report.pdf",
    "RUBRIC": "5sw-wk3-construction-classification-rubric.pdf",
    "REPORT_RUBRIC": "5sw-wk3-construction-evidence-rubric.pdf",
}
VISUAL_FILES = {
    "image1": "spot-problem-image-1.jpg",
    "image2": "spot-problem-image-2.jpg",
    "image3": "spot-problem-image-3.jpg",
    "image4": "spot-problem-image-4.jpg",
    "image5": "spot-problem-image-5.jpg",
    "thermal": "fyf-p178-thermal-comparison.jpg",
}


def preflight():
    required = [
        ROOT / "build/canvas/templates/5sw-wk3-student.html",
        ROOT / "build/canvas/templates/5sw-wk3-teacher.html",
        *(ROOT / "docs/resources/worksheets" / name for name in WORKSHEET_FILES.values()),
        *(ASSETS / "day4" / name for name in VISUAL_FILES.values()),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"5SW Wk3 preflight missing required files: {missing}")


CONTRACTS = {
    1: {
        "TOPIC": "Career Opportunities",
        "OBJECTIVE": "Students will identify construction career opportunities and compare documented preparation requirements.",
        "TEKS": "d(1)(C), d(2)(A)",
        "DOL": "Individual career/preparation evidence card.",
        "I_CAN": "identify construction careers and compare what preparation each route requires.",
        "SHOW": "Complete the individual career/preparation evidence card with three careers, one route decision, and one source limit.",
    },
    2: {
        "TOPIC": "Enrollment Steps",
        "OBJECTIVE": "Students will investigate enrollment steps for two career-preparation routes and identify an affiliated career organization.",
        "TEKS": "d(3)(G), d(3)(H)",
        "DOL": "Individual route and organization comparison.",
        "I_CAN": "compare two training routes, put their steps in order, and explain how one career organization helps.",
        "SHOW": "Complete the route comparison with ordered steps, one organization type, its access route, and its value.",
    },
    3: {
        "TOPIC": "Labor Trends",
        "OBJECTIVE": "Students will analyze construction labor trends and classify four occupations using a published evidence rule.",
        "TEKS": "d(5)(A), d(5)(B)",
        "DOL": "Individual four-career classification and evidence limitation.",
        "I_CAN": "use the same dated evidence to classify four construction careers and explain one limitation.",
        "SHOW": "Submit Minor 3 with four supported classifications, a trend comparison, recommendation, and evidence limit.",
    },
    4: {
        "TOPIC": "Career Opportunities",
        "OBJECTIVE": "Students will separate visible evidence from inference and identify the qualified construction role that should evaluate a possible concern.",
        "TEKS": "d(1)(C)",
        "DOL": "Five-image evidence draft and thermal-image boundary.",
        "I_CAN": "describe what an image shows, use cautious language, and name who should check next.",
        "SHOW": "Draft five evidence findings and one thermal-image boundary without diagnosing or giving repair advice.",
    },
    5: {
        "TOPIC": "Professional Communication",
        "OBJECTIVE": "Students will organize construction evidence and deliver a clear individual oral/AAC professional briefing using an appropriate evidence or assistive technology.",
        "TEKS": "d(1)(C), d(4)(C)",
        "DOL": "Individual evidence report + 30-45 second oral/AAC briefing using the report/evidence card, a private recording, or an AAC/speech-generating device.",
        "I_CAN": "turn careful evidence into a clear report and use an appropriate evidence or assistive technology to brief one finding.",
        "SHOW": "Submit the formative evidence report and one 30-45 second oral/AAC briefing with a visible clue, cautious possibility, limit, next role, work product, and appropriate technology choice.",
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


async def require_minor_preflight(client):
    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group_matches = [entry for entry in groups if entry.get("name") == "Minor Assessments (40%)"]
    if len(group_matches) != 1:
        raise RuntimeError(
            "Expected exactly one assignment group named 'Minor Assessments (40%)'; "
            f"found {len(group_matches)}"
        )
    group = group_matches[0]
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == CLASSIFY_TITLE]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one existing mapped Minor assignment named {CLASSIFY_TITLE!r}; found {len(matches)}"
        )
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
            f"Mapped Minor invariant failed before module writes: published={found.get('published')}, "
            f"points={found.get('points_possible')}, group={found.get('assignment_group_id')}, "
            f"grading={found.get('grading_type')}, omit={found.get('omit_from_final_grade')}, "
            f"rubric_note={rubric_note is not None}"
        )
    return found, group


async def update_minor_assignment(client, found, group, description, attachment_id):
    rubric_note = re.search(
        r'<div data-cce-rubric-note="cce-advisory-rubric-v1".*?</div>',
        found.get("description") or "",
        flags=re.I | re.S,
    )
    if rubric_note is None:
        raise RuntimeError(f"Mapped Minor is missing required rubric conversion note: {CLASSIFY_TITLE!r}")
    assignment = await common.api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{found['id']}",
        data={
            "assignment[name]": CLASSIFY_TITLE,
            "assignment[description]": description + rubric_note.group(0),
            "assignment[published]": "false",
            "assignment[points_possible]": "100",
            "assignment[grading_type]": "points",
            "assignment[omit_from_final_grade]": "false",
            "assignment[submission_types][]": ["student_annotation", "online_upload", "online_text_entry"],
            "assignment[annotatable_attachment_id]": str(attachment_id),
        },
    )
    assignment = await assert_annotation_assignment(client, assignment, attachment_id, mapped=True)
    if (
        assignment.get("assignment_group_id") != group["id"]
        or RUBRIC_NOTE_MARKER not in (assignment.get("description") or "")
    ):
        raise RuntimeError(f"Minor group/rubric invariant failed after update for {CLASSIFY_TITLE!r}")
    return assignment


async def assert_annotation_assignment(client, assignment, source_attachment_id, *, mapped=False, media=False):
    assignment = await common.api(client, "GET", f"/courses/{COURSE_ID}/assignments/{assignment['id']}")
    source_file = await common.api(client, "GET", f"/files/{source_attachment_id}")
    annotation_attachment_id = int(assignment.get("annotatable_attachment_id") or 0)
    annotation_file = await common.api(client, "GET", f"/files/{annotation_attachment_id}") if annotation_attachment_id else {}
    if annotation_file and not annotation_file.get("locked"):
        annotation_file = await common.api(client, "PUT", f"/files/{annotation_attachment_id}", data={"locked": "true"})
    required_routes = {"student_annotation", "online_upload", "online_text_entry"}
    if media:
        required_routes.add("media_recording")
    failures = {
        "published": assignment.get("published") is not False,
        "points_possible": float(assignment.get("points_possible") or 0) != (100 if mapped else 0),
        "grading_type": assignment.get("grading_type") != ("points" if mapped else "percent"),
        "omit_from_final_grade": assignment.get("omit_from_final_grade") is not (False if mapped else True),
        "submission_types": not required_routes.issubset(set(assignment.get("submission_types") or [])),
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


async def upsert_annotation_assignment(client, title, description, attachment_id, *, media=False):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == title]
    if len(matches) > 1:
        raise RuntimeError(f"Duplicate assignments named {title!r}: {[entry['id'] for entry in matches]}")
    found = matches[0] if matches else None
    routes = ["student_annotation", "online_upload", "online_text_entry"]
    if media:
        routes.append("media_recording")
    data = {
        "assignment[name]": title,
        "assignment[description]": description,
        "assignment[submission_types][]": routes,
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
    return await assert_annotation_assignment(client, assignment, attachment_id, media=media)


async def main():
    preflight()
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")

    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        # Fail before module, folder, file, page, or practice-assignment writes.
        mapped_minor, minor_group = await require_minor_preflight(client)
        module = await ensure_module(client)
        support_path = "course files/CCR Materials/5SW/Wk3"
        support_folder = await common.ensure_folder(client, support_path)
        files = {
            key: await common.upload(client, ROOT / "docs/resources/worksheets" / name, support_path)
            for key, name in WORKSHEET_FILES.items()
        }
        support_folder = await common.lock_folder_files(client, support_folder)

        visual_path = "course files/CCR Materials/5SW/Wk3/Day 4 Licensed Visuals"
        visual_folder = await common.ensure_folder(client, visual_path)
        visual_files = {
            key: await common.upload(client, ASSETS / "day4" / name, visual_path)
            for key, name in VISUAL_FILES.items()
        }
        visual_folder = await common.lock_folder_files(client, visual_folder)

        career = await upsert_annotation_assignment(
            client,
            CAREER_TITLE,
            "<p>Annotate or upload the fixed construction career evidence, type labeled responses, or use paper.</p>",
            files["CAREER"]["id"],
        )
        routes = await upsert_annotation_assignment(
            client,
            ROUTES_TITLE,
            "<p>Compare two dated education or training routes and identify one organization type, access step, and value.</p>",
            files["ROUTES"]["id"],
        )
        classify = await update_minor_assignment(
            client,
            mapped_minor,
            minor_group,
            "<p>Use the fixed May 2024 U.S. evidence and published classroom comparison rule. Submit four supported classifications, a trend comparison, recommendation, and evidence limitation.</p>",
            files["CLASSIFY"]["id"],
        )
        report = await upsert_annotation_assignment(
            client,
            REPORT_TITLE,
            "<p>Use one shared Days 4-5 report. Submit the private fictional evidence report and a 30-45 second individual oral/AAC briefing using one appropriate technology: keep the report/evidence card visible during a live or teacher-conference briefing, make a private audio/video recording, or use an accommodation-aligned AAC/speech-generating device. A written report or transcript may support preparation but does not by itself demonstrate oral/AAC evidence. This remains formative, worth 0 points, omitted from the final grade, and unpublished.</p>",
            files["REPORT"]["id"],
            media=True,
        )

        urls = {
            "career": f"/courses/{COURSE_ID}/assignments/{career['id']}",
            "routes": f"/courses/{COURSE_ID}/assignments/{routes['id']}",
            "classify": f"/courses/{COURSE_ID}/assignments/{classify['id']}",
            "report": f"/courses/{COURSE_ID}/assignments/{report['id']}",
        }
        link, step, flow = common.file_link, common.step, common.flow
        alt = {
            "image1": "Interior wall with decorative paneling beside a window and radiator cover",
            "image2": "Exterior roof with several shingles whose photographed edges appear uneven or curled around a small roof structure",
            "image3": "Interior ceiling and upper wall with irregular discoloration and staining",
            "image4": "Open electrical service panel with visible breakers and yellow cables entering the enclosure",
            "image5": "Cabinet floor below a sink with an uneven, darkened, and discolored photographed surface",
            "thermal": "Find Your Future page comparing a visible-light window image with a thermal image showing temperature differences",
        }
        day4_media = "".join(
            f"<h4>Image {index}</h4>" + prior.image_tag(visual_files[f"image{index}"]["id"], alt[f"image{index}"])
            for index in range(1, 6)
        ) + "<h4>Thermal comparison</h4>" + prior.image_tag(visual_files["thermal"]["id"], alt["thermal"])

        student = {
            1: {
                "TITLE": "Construction Careers and Preparation",
                "PURPOSE": "Use fixed evidence to identify construction careers and distinguish current district, education, training, and license boundaries.",
                "TODAY": "<ul><li>read the current MacArthur pathway label;</li><li>compare three careers;</li><li>record preparation accurately;</li><li>make one evidence-based route judgment.</li></ul>",
                "READY": f'<p>Open {link(files["CAREER"]["id"], "the three-page construction career packet")} or <a href="{urls["career"]}">the Canvas annotation activity</a>.</p>',
                "MEDIA": "",
                "LANGUAGE": "<p><strong>Word bank:</strong> preparation/preparación · median/mediana · opening/vacante · license/licencia · boundary/límite.</p><p><strong>Use this frame:</strong> I would choose [role] because [work/preparation evidence]. I would accept [tradeoff], and I still need to verify [question].</p>",
                "STEPS": step(1, "Read the pathway boundary", "<p>MacArthur currently lists Construction within ACE. A high-school pathway supports preparation; it does not replace later training or a trade-specific license.</p>")
                + step(2, "Compare three careers", "<p>Keep occupation, work, typical preparation, May 2024 U.S. median, outlook, and source together.</p>")
                + step(3, "Choose a route", "<p>Use the evidence—not a salary guess or platform favorite—to explain one fit and one question to verify.</p>")
                + step(4, "Submit privately", f'<p>Submit through <a href="{urls["career"]}">the practice activity</a> or use the paper route.</p>'),
                "EXIT": "<p>Name one career, one accurate preparation requirement, and one boundary that still needs verification.</p>",
                "DONE": "<ul><li>three careers compared;</li><li>source/date/measure kept visible;</li><li>one route judgment;</li><li>one verification question.</li></ul>",
                "SUPPORT": "<p>preparation = preparación · pathway = programa de estudio · license = licencia · median = mediana · verify = verificar.</p>",
                "FALLBACK": "<p>The fixed cards are the full route. H&amp;L, Xello, open search, and a partner are not required.</p>",
            },
            2: {
                "TITLE": "Training Routes and Career Organizations",
                "PURPOSE": "Compare two real route types and identify the exact steps and organization support a student would verify next.",
                "TODAY": "<ul><li>separate Registered Apprenticeship from a universal trade ladder;</li><li>compare two routes;</li><li>sequence enrollment steps;</li><li>classify an organization.</li></ul>",
                "READY": f'<p>Open {link(files["ROUTES"]["id"], "the four-page routes and organizations packet")} or <a href="{urls["routes"]}">the Canvas annotation activity</a>.</p>',
                "MEDIA": "",
                "LANGUAGE": "<p><strong>Word bank:</strong> apprenticeship/aprendizaje registrado · sponsor/patrocinador · eligibility/requisitos · association/asociación · credential/credencial.</p><p><strong>Use this frame:</strong> [Organization] is a [type]. A student can access it by [step], and one documented value is [value].</p>",
                "STEPS": step(1, "Use the stable apprenticeship facts", "<p>Registered Apprenticeship combines paid work, instruction, mentoring, progressive wages, and a portable credential. Sponsor rules vary.</p>")
                + step(2, "Compare two dated routes", "<p>Record the documented start steps, paid-work status, credential type, and the time, cost, aid, transfer, or eligibility questions a current listing must answer.</p>")
                + step(3, "Classify the organization", "<p>Distinguish union, professional or trade association, CTSO, and credential body. Name how a student can access one and what value it offers.</p>")
                + step(4, "Submit the individual evidence", f'<p>Use <a href="{urls["routes"]}">the practice activity</a>; never submit a real application or contact form for class.</p>'),
                "EXIT": "<p>State two accurate application or enrollment steps and one organization type, access route, and value.</p>",
                "DONE": "<ul><li>two routes compared;</li><li>steps in order;</li><li>variable claims labeled;</li><li>organization correctly classified;</li><li>one next verification.</li></ul>",
                "SUPPORT": "<p>apprenticeship = aprendizaje registrado · sponsor = patrocinador · eligibility = requisitos · association = asociación · credential = credencial.</p>",
                "FALLBACK": "<p>The fixed dated cards replace open-web scavenger hunts. Do not enter personal data or apply to any program.</p>",
            },
            3: {
                "TITLE": "Classify Four Construction Careers",
                "PURPOSE": "Use one comparable national evidence basis and a published classroom rule to classify four construction careers.",
                "TODAY": "<ul><li>read the classroom comparison rule;</li><li>analyze four careers;</li><li>cite a number for each label;</li><li>state one limitation.</li></ul>",
                "READY": f'<p>Open {link(files["CLASSIFY"]["id"], "the four-page labor classification packet")} and {link(files["RUBRIC"]["id"], "the student-visible Minor 3 rubric")}, or use <a href="{urls["classify"]}">the Canvas annotation activity</a>.</p>',
                "MEDIA": "",
                "LANGUAGE": "<p><strong>Word bank:</strong> classification/clasificación · high wage/salario alto · high demand/alta demanda · annual opening/vacante anual · limitation/limitación.</p><p><strong>Use this frame:</strong> I classify [occupation] as [label] because [exact fact/number]. This national evidence does not prove [local or starting-pay claim].</p>",
                "STEPS": step(1, "Read the rule", "<p>High wage means above the May 2024 U.S. all-occupation median of $49,500. High demand means projected growth above the 3.1% all-occupation comparison. High skill uses the documented preparation rule in the packet.</p>")
                + step(2, "Classify each career", "<p>Use the same geography, year, and measure. Annual openings are useful context but do not prove a DFW worker shortage.</p>")
                + step(3, "Cite the evidence", "<p>Record one number or preparation fact for every yes/no classification.</p>")
                + step(4, "State the limitation", "<p>Explain what this national dataset cannot tell you about one local employer, opening, or starting salary.</p>"),
                "EXIT": "<p>Choose one classification that might change with a different geography or year and explain why.</p>",
                "DONE": "<ul><li>four complete career records;</li><li>same evidence basis;</li><li>supported classifications;</li><li>one comparison;</li><li>one limitation.</li></ul>",
                "SUPPORT": "<p>classification = clasificación · high wage = salario alto · high demand = alta demanda · opening = vacante anual · limitation = limitación.</p>",
                "FALLBACK": "<p>All required numbers are in the packet. Do not estimate a missing value; write not available or not comparable.</p>",
            },
            4: {
                "TITLE": "Fictional Visual Observation Lab",
                "PURPOSE": "Separate what an image visibly shows from what it could mean and who is qualified to check next.",
                "TODAY": "<ul><li>inspect five licensed images;</li><li>record visible clues;</li><li>state a possible concern without diagnosing;</li><li>name the next qualified role.</li></ul>",
                "READY": f'<p>Open FYF pp. 176–178 first. Begin Findings 1–5 and the thermal boundary in {link(files["REPORT"]["id"], "the shared five-page evidence report")} through <a href="{urls["report"]}">the one Days 4–5 Canvas Assignment</a>. Do not create a second submission.</p>',
                "MEDIA": day4_media,
                "LANGUAGE": "<p><strong>Word bank:</strong> observe/observar · could indicate/podría indicar · qualified/calificado · evidence limit/límite de evidencia · thermal/térmico.</p><p><strong>Use this frame:</strong> I observe [visible clue]. This could indicate [possibility]. The image cannot prove [limit]. A qualified [role] should evaluate it next.</p>",
                "STEPS": step(1, "Stay inside the boundary", "<p>This is a fictional image-analysis exercise. Do not inspect a real home, touch a panel, diagnose a defect, estimate repairs, or advise a purchase.</p>")
                + step(2, "Observe before inferring", "<p>Write only what you can point to in the image. It is acceptable to say no visible concern in this image.</p>")
                + step(3, "State a possibility and limit", "<p>Use could indicate, then name what the image cannot prove.</p>")
                + step(4, "Route the next check", f'<p>Name the qualified inspector or trade professional who should evaluate next. Treat the thermal pattern as a clue, not proof. Save the draft in <a href="{urls["report"]}">the shared Days 4–5 Assignment</a>; final submission is on Day 5.</p>'),
                "EXIT": "<p>Write one observation, one possible meaning, one limit, and one next qualified role.</p>",
                "DONE": "<ul><li>five image records;</li><li>thermal comparison;</li><li>observation separated from inference;</li><li>qualified role named;</li><li>no diagnosis or repair advice.</li></ul>",
                "SUPPORT": "<p>observation = observación · could indicate = podría indicar · qualified = calificado · evidence limit = límite de evidencia · thermal = térmico.</p>",
                "FALLBACK": "<p>Every image is embedded here with neutral adjacent text. Use zoom, enlarged print, teacher read-aloud, dictation, or written description.</p>",
            },
            5: {
                "TITLE": "Evidence Report and Individual Briefing",
                "PURPOSE": "Turn the visual evidence into a careful fictional report and communicate one finding clearly.",
                "TODAY": "<ul><li>complete five report blocks;</li><li>write a thermal-evidence boundary;</li><li>choose an appropriate evidence or assistive technology;</li><li>deliver and submit a 30-45 second oral/AAC briefing privately.</li></ul>",
                "READY": f'<p>Reopen {link(files["REPORT"]["id"], "the shared five-page evidence report")} from Day 4 and {link(files["REPORT_RUBRIC"]["id"], "the formative report feedback guide")}. Revise the same findings; do not recopy them into a second packet.</p>',
                "MEDIA": "",
                "LANGUAGE": "<p><strong>Word bank:</strong> finding/hallazgo · corroborate/confirmar con otra evidencia · briefing/informe breve · client/cliente · next professional/siguiente profesional.</p><p><strong>Use this frame:</strong> In [image/area], I observe [clue]. It could indicate [possibility], but the image cannot prove [limit]. A qualified [role] should check next.</p><p><strong>Name your technology:</strong> I will use [visible report/evidence card, private recording, or AAC/speech-generating device] to support my oral/AAC briefing.</p>",
                "STEPS": step(1, "Complete each finding", "<p>Use observation, possible meaning, evidence limit, and next qualified professional. Do not add prices, purchase advice, or a diagnosis.</p>")
                + step(2, "Write the thermal boundary", "<p>Explain what the temperature pattern shows and what corroboration would still be needed.</p>")
                + step(3, "Choose the technology and prepare", "<p>Choose one finding. Use one appropriate technology: the visible report/evidence card during a live or teacher-conference briefing, a private Canvas recording, or an AAC/speech-generating device. In 30-45 seconds, deliver the evidence, careful claim, limit, next role, and work product.</p>")
                + step(4, "Submit privately", f'<p><a href="{urls["report"]}">Submit the report and briefing evidence</a>. Public speaking is not required.</p>'),
                "EXIT": "<p>Explain how careful evidence language protects both the client and the qualified worker who checks next.</p>",
                "DONE": "<ul><li>five expanded finding blocks;</li><li>thermal boundary;</li><li>one complete individual oral/AAC briefing using an appropriate technology choice;</li><li>qualified role and work product named;</li><li>private submission and feedback-guide self-check.</li></ul>",
                "SUPPORT": "<p>finding = hallazgo · corroborate = confirmar con otra evidencia · briefing = informe breve · client = cliente · next professional = siguiente profesional.</p>",
                "FALLBACK": "<p>Complete the same report independently from the embedded Day 4 images. Live and teacher-conference routes use the visible report/evidence card; other choices are private audio/video or accommodation-aligned oral/AAC technology. A written report or transcript may scaffold but does not by itself demonstrate oral evidence. If an accommodation changes the evidence mode, the teacher records the d(4)(C) decision separately.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Construction Careers and Preparation",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(2)(A)",
                "ALERT": "<strong>Use current names and bounded claims.</strong> MacArthur currently lists Construction within ACE. Do not present the older workbook label, NCCER, SkillsUSA, or one trade license ladder as a current universal district guarantee.",
                "PREP": f'<ul><li><strong>Default:</strong> one device per student, one projector, zero prints. Post {link(files["CAREER"]["id"], "the three-page fixed career packet")} and the private annotation activity.</li><li><strong>Paper:</strong> one three-page packet and one pencil per student; one collection tray per class.</li><li>Students work individually. A partner may compare one preparation difference, but each student submits one card. Keep H&amp;L optional.</li></ul>',
                "EVIDENCE": "<p>Formative three-career comparison, route judgment, and verification question.</p>",
                "FLOW": flow("#315f4c", "Current pathway · 5", "Construction within ACE.") + flow("#4c8b38", "Career cards · 15", "Work, preparation, pay, outlook.") + flow("#8a4f2b", "Compare · 15", "Three routes and boundaries.") + flow("#d39b22", "Decision · 10", "Evidence-based fit and question.") + flow("#315f4c", "Exit · 5", "Career, preparation, boundary."),
                "MODEL": '<div style="border:1px solid #b7d1c5;border-radius:8px;padding:14px 18px;background:#f3f8f5"><p><strong>Complete model:</strong> I selected Carpenter. Two work products are a measured wall frame and installed door or window components. BLS lists a high-school diploma as typical and says carpenters learn on the job or through apprenticeship. The May 2024 U.S. median annual wage is $59,310. That figure does not prove DFW starting pay or a guaranteed wage. For fictional Jordan, this route fits because Jordan wants to earn while learning, but Jordan must accept physical work and verify the terms of a current sponsor listing.</p><p><strong>Non-example:</strong> “Carpenters make good money and become masters after apprenticeship.” This drops the source labels and invents a universal ladder.</p></div>',
                "MONITOR": '<ul><li><strong>CFU at minute 8:</strong> students label $59,310 as Carpenter, May 2024, U.S., median annual wage, BLS. Reteach if any label is missing in three of five samples.</li><li><strong>Lap 1, minutes 15-22:</strong> check two concrete work products and one bounded preparation route.</li><li><strong>Lap 2, minutes 28-35:</strong> require one source limit before students make a fit decision.</li><li><strong>Pivot:</strong> color-code the complete model into work, preparation, number, limit, and tradeoff before students continue.</li><li><strong>Trim:</strong> cut the partner comparison, not the individual route decision or final submission. Collect paper in the class tray during the final five minutes.</li></ul>',
                "RESOURCES": '<p><a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte/macarthur-high-school">Irving ISD MacArthur CTE</a> · current BLS occupation pages in the packet. FYF claims are historical workbook context unless separately verified.</p>',
                "SUPPORT": "<p>Read one card at a time. The packet gives dedicated response lines rather than a cramped multi-career grid. Accept typed, enlarged, dictated, or paper responses.</p>",
                "FALLBACK": "<p>No platform login, open search, or partner is required.</p>",
            },
            2: {
                "TITLE": "Training Routes and Career Organizations",
                "SUBTITLE": "50 minutes · TEKS d(3)(G), d(3)(H)",
                "ALERT": "<strong>Students do not apply.</strong> They compare dated route cards and sequence steps; no contact form, account, or personal data is entered.",
                "PREP": f'<ul><li><strong>Default:</strong> one device per student, one projector, zero prints. Post {link(files["ROUTES"]["id"], "the four-page routes and organizations packet")} and the private annotation activity.</li><li><strong>Paper:</strong> one four-page packet and one pencil per student; one collection tray per class.</li><li>Students work individually. Use pairs only to rehearse the order of route steps. No account, contact form, or real application is opened.</li></ul>',
                "EVIDENCE": "<p>Formative two-route comparison, ordered application/enrollment steps, organization classification, access, and value.</p>",
                "FLOW": flow("#315f4c", "Stable facts · 5", "What Registered Apprenticeship is.") + flow("#4c8b38", "Two routes · 12", "Dated cards, variable terms.") + flow("#8a4f2b", "Compare/sequence · 23", "Eligibility through next verification.") + flow("#d39b22", "Organization · 7", "Type, access, value.") + flow("#315f4c", "Exit · 3", "Two steps and one organization."),
                "MODEL": '<div style="border:1px solid #b7d1c5;border-radius:8px;padding:14px 18px;background:#f3f8f5"><p><strong>Complete Jordan model:</strong> Jordan should investigate a Registered Apprenticeship first because it is a paid job with structured learning. Jordan would search by occupation and location, open a sponsor listing, record eligibility and documents, and apply through that sponsor only when eligible. The advantage of Dallas College is a published certificate or A.A.S. route with advising; Jordan still must verify current cost, credit status, campus, and transfer limits. AGC is a professional/trade association. A future student could access a student chapter through a participating accredited college, and one documented value is learning with industry leaders.</p><p><strong>Non-example:</strong> “Apprenticeship is free and leads from apprentice to master.” Sponsor terms and ladders vary.</p></div>',
                "MONITOR": '<ul><li><strong>CFU at minute 10:</strong> students identify the employer or sponsor, not the government website, as the future application destination.</li><li><strong>Checkpoint at minute 22:</strong> each route has at least two ordered start steps and one variable marked for verification.</li><li><strong>Lap, minutes 24-35:</strong> reject invented wage, length, cost, transfer, or license claims.</li><li><strong>Checkpoint at minute 43:</strong> organization type, future access route, and one documented value are all present.</li><li><strong>Pivot:</strong> give students the five numbered step cards and have them sequence before writing. <strong>Trim:</strong> cut pair rehearsal, not the individual route comparison or organization evidence. Collect paper at minute 47.</li></ul>',
                "RESOURCES": '<p><a href="https://www.apprenticeship.gov/career-seekers">Apprenticeship.gov Career Seekers</a> · <a href="https://www.dallascollege.edu/study/construction-technology/">Dallas College Construction Technology</a> · <a href="https://www.agc.org/connect/chapters/student-chapters">AGC Student Chapters</a>. Current provider steps and the AGC access/value boundary are dated in the packet.</p>',
                "SUPPORT": "<p>Use arrows or numbered cards for sequencing. Students may respond privately; no cold contact or public sharing.</p>",
                "FALLBACK": "<p>Fixed cards replace live provider browsing and remain usable after absence or a site change.</p>",
            },
            3: {
                "TITLE": "Classify Four Construction Careers",
                "SUBTITLE": "50 minutes · TEKS d(5)(A), d(5)(B)",
                "ALERT": "<strong>The labels are a published classroom comparison rule.</strong> They are not official BLS or TWC designations and do not prove a DFW shortage.",
                "PREP": f'<ul><li><strong>Default:</strong> one device per student, one projector, zero prints. Post {link(files["CLASSIFY"]["id"], "the four-page classification packet")}, {link(files["RUBRIC"]["id"], "the Minor 3 rubric")}, and the mapped Minor annotation activity.</li><li><strong>Paper:</strong> one four-page packet and one two-page rubric per student; one collection tray per class.</li><li>This is individual graded evidence. Seat partners may clarify a direction, but no row or recommendation is shared.</li></ul>',
                "EVIDENCE": "<p><strong>Minor 3 in the 5SW assessment map:</strong> four supported classifications, trend comparison, recommendation, and evidence limitation. The importer protects the existing 100-point assignment in Minor Assessments (40%).</p>",
                "FLOW": flow("#315f4c", "Rule · 5", "Same basis and transparent thresholds.") + flow("#4c8b38", "Model · 8", "One label with evidence.") + flow("#8a4f2b", "Four careers · 27", "Two labeled records per landscape page.") + flow("#d39b22", "Compare · 7", "Trend and limitation.") + flow("#315f4c", "Exit · 3", "What could change."),
                "MODEL": '<div style="border:1px solid #b7d1c5;border-radius:8px;padding:14px 18px;background:#f3f8f5"><p><strong>One complete classification:</strong> Carpenter = high-skill YES because BLS lists apprenticeship as the typical training category; high-wage YES because $59,310 is above $49,500; high-demand YES because 4% is above 3.1%. The 74,100 annual openings are context, not the high-demand rule and not proof of a DFW shortage.</p><p><strong>Trend model:</strong> Carpenters have more annual openings than construction managers even though managers have faster growth. Openings include replacement needs, while growth measures percentage change in employment.</p><p><strong>Jordan model:</strong> I recommend Carpenter because the route can include apprenticeship, the May 2024 U.S. median is $59,310, and projected growth is 4%. This national evidence does not prove DFW starting pay, a current sponsor opening, or that the work fits Jordan.</p></div>',
                "MONITOR": '<ul><li><strong>Key:</strong> all four meet the course high-skill rule and high-wage threshold. Construction Manager, Carpenter, and Construction Equipment Operator meet the high-demand rule; Masonry Worker does not.</li><li><strong>CFU at minute 8:</strong> students classify the Carpenter wage and demand rows and name the exact threshold for each.</li><li><strong>Checkpoint at minute 20:</strong> Construction Manager and Carpenter have three labels with evidence, not only YES/NO circles.</li><li><strong>Checkpoint at minute 33:</strong> all four occupations are complete and annual openings have not been used as the demand rule.</li><li><strong>Lap, minutes 34-42:</strong> require two occupations in the growth/openings comparison and all four evidence jobs in Jordan’s recommendation.</li><li><strong>Pivot:</strong> students annotate the complete model by circling rule, evidence, and limitation. <strong>Trim:</strong> cut the separate exit discussion, not the rubric self-check or Minor submission. If the network fails, collect the paper packet in the class tray.</li></ul>',
                "RESOURCES": '<p><a href="https://www.bls.gov/emp/tables/occupational-projections-and-characteristics.htm">BLS projection characteristics</a> and dated occupation pages. Same basis: May 2024 U.S. median and 2024–34 national projections.</p>',
                "SUPPORT": "<p>Two occupations share each landscape response page, with one labeled line for each evidence job and a separate limitation area. Read numbers aloud, allow calculator or typed response, and score reasoning rather than English mechanics.</p>",
                "FALLBACK": "<p>The packet is the complete dataset. Students never estimate missing data or depend on H&amp;L.</p>",
            },
            4: {
                "TITLE": "Fictional Visual Observation Lab",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>This is not a home inspection.</strong> Students analyze supplied fictional images only and never touch a real panel, inspect a home, diagnose a defect, estimate repairs, or advise a buyer.",
                "PREP": f'<ul><li><strong>Default:</strong> one FYF workbook and one device per student, one projector, zero prints. Open pp. 176-178, then {link(files["REPORT"]["id"], "the shared five-page evidence report")} and the one Days 4-5 annotation activity.</li><li><strong>Paper:</strong> print one five-page report per student once for both days; provide one pencil per student and one collection tray per class. Do not also print the seven-page enlarged log unless a student needs the one-image-per-page accommodation.</li><li>Students work individually. Project one image at a time for about four minutes. No real property, tools, panels, mold, roofs, or repair work enters the lesson.</li></ul>',
                "EVIDENCE": "<p>Formative draft of Findings 1–5 plus the thermal comparison in the same report students revise on Day 5. Students do not complete a second observation packet.</p>",
                "FLOW": flow("#315f4c", "Boundary · 5", "Fictional image analysis only.") + flow("#4c8b38", "Model · 8", "Observation before inference.") + flow("#8a4f2b", "Five images · 25", "Roomy record per image.") + flow("#d39b22", "Thermal · 7", "Pattern and corroboration.") + flow("#315f4c", "Exit · 5", "Complete evidence chain."),
                "MODEL": '<div style="border:1px solid #b7d1c5;border-radius:8px;padding:14px 18px;background:#f3f8f5"><p><strong>Complete Image 3 model:</strong> I observe irregular brown discoloration where the ceiling meets the upper wall. This could indicate current or past moisture. The image cannot prove the source, whether the area is wet now, or whether mold is present. A Texas-licensed Professional Real Estate Inspector should evaluate the property, then route any confirmed roof or plumbing concern to the appropriate qualified trade professional.</p><p><strong>Non-example:</strong> “The roof leaks and there is mold.” The photograph does not prove either diagnosis.</p></div>',
                "MONITOR": '<ul><li><strong>CFU at minute 10:</strong> students sort “brown ceiling ring” as observation and “roof leak” as inference. Reteach if more than one-third reverse them.</li><li><strong>Image checkpoints, minutes 17/21/25/29/33:</strong> each finding has an observation before a possibility.</li><li><strong>Lap, minutes 20-35:</strong> stop any repair advice, safety clearance, purchase advice, or claim of mold/code violation.</li><li><strong>Checkpoint at minute 40:</strong> the thermal record names a visible pattern and evidence still needed.</li><li><strong>Pivot:</strong> use only the neutral alt description, then ask students to underline what is visible and bracket the cautious possibility. <strong>Trim:</strong> cut whole-class sharing, not the five findings, thermal boundary, or saved report. Collect paper in the class tray and return it on Day 5.</li></ul>',
                "RESOURCES": '<p>Licensed Climber Notes photos and FYF p.178 remain in authenticated Canvas. <a href="https://www.trec.texas.gov/become-licensed/professional-real-estate-inspector">TREC inspector licensing</a> establishes the professional boundary.</p>',
                "SUPPORT": "<p>Use zoom and neutral read-aloud descriptions. Do not encode the answer in alt text. Accept dictation, typed response, enlarged print, and explicit no-visible-concern judgments.</p>",
                "FALLBACK": "<p>All six visuals are embedded. An absent student can complete the identical individual route without a live projection.</p>",
            },
            5: {
                "TITLE": "Evidence Report and Individual Briefing",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(4)(C)",
                "ALERT": "<strong>Formative inspection report and professional briefing.</strong> Use the report and briefing for feedback; they are not one of the two mapped 5SW majors. Keep unpublished and ungraded until the review gate passes.",
                "PREP": f'<ul><li><strong>Default:</strong> one device and retained Day 4 report per student, one projector, zero new prints. Reopen {link(files["REPORT"]["id"], "the same shared five-page report")}, {link(files["REPORT_RUBRIC"]["id"], "the formative feedback guide")}, and the one private Days 4-5 Assignment.</li><li><strong>Paper:</strong> return the retained five-page report; print one replacement only for an absent/missing-copy student. Use one collection tray per class. Print the two-page feedback guide only when a student needs paper.</li><li>For private recording, one device with a working microphone and headphones per recording student; live teacher conference and accommodation-aligned oral/AAC routes need no recording. Public presentation is optional.</li></ul>',
                "EVIDENCE": "<p>Five expanded findings, thermal boundary, and one individual 30-45 second oral/AAC evidence briefing that names the qualified role, the professional work product used next, and an appropriate technology choice. Group delivery and written-only work do not substitute for individual oral/AAC evidence.</p>",
                "FLOW": flow("#315f4c", "Reopen evidence · 5", "Images and Day 4 draft.") + flow("#4c8b38", "Model revision · 5", "Careful language and next role.") + flow("#8a4f2b", "Revise/report · 25", "Five findings, thermal boundary, summary.") + flow("#d39b22", "Briefings · 12", "Individual oral/AAC routes.") + flow("#315f4c", "Exit · 3", "Why language matters."),
                "MODEL": '<div style="border:1px solid #b7d1c5;border-radius:8px;padding:14px 18px;background:#f3f8f5"><p><strong>Technology choice:</strong> visible report/evidence card during a teacher conference.</p><p><strong>30-45 second briefing model:</strong> “For Image 3, I observed irregular brown discoloration where the ceiling meets the wall. It could indicate current or past moisture, but the image cannot prove the source or whether the area is wet now. A Texas-licensed Professional Real Estate Inspector should evaluate it next and document the observation in an inspection report. If the inspector confirms a roof or plumbing concern, the report can direct the client to the appropriate qualified trade professional.”</p><p><strong>Non-example:</strong> “The roof leaks, so replace it.” This diagnoses a cause and gives repair advice without enough evidence.</p></div>',
                "MONITOR": '<ul><li><strong>Checkpoint at minute 12:</strong> every student has five image labels and at least one complete evidence chain.</li><li><strong>Lap 1, minutes 15-25:</strong> check “could/may,” one limit, and a qualified role in all five findings.</li><li><strong>Checkpoint at minute 30:</strong> thermal boundary and overall limitation are present. Students who are behind switch to labeled bullets; do not cut a rubric job.</li><li><strong>Briefing gate at minute 38:</strong> students choose their strongest complete finding, highlight the five briefing jobs, and name the technology choice. Live/conference students keep the report or evidence card visible.</li><li><strong>Do not score:</strong> visual polish, camera use, eye contact, accent, or speech difference. A written report or transcript may scaffold but does not independently demonstrate oral/AAC evidence.</li><li><strong>Trim/recovery:</strong> cut public sharing and decorative formatting. Protect the report, individual briefing, submission, and material return. If either evidence piece is incomplete at minute 47, save/collect it and schedule the same private recovery route; do not assign a second report or homework packet.</li></ul>',
                "RESOURCES": "<p>The report is explicitly a fictional visual evidence report, not a TREC inspection report. No repair-price research, purchase recommendation, or real property/student legal name is required.</p>",
                "SUPPORT": "<p>The shared five-page report gives each finding a labeled block and avoids recopying Day 4 work. Let students use a fictional analyst ID, speech-to-text for the report, private audio/video, or accommodation-aligned oral/AAC evidence.</p>",
                "FALLBACK": "<p>No team attendance, public speaking, H&amp;L favorite, Xello task, or eDynamic completion is required.</p>",
            },
        }

        day_names = {
            1: "Construction Careers and Preparation",
            2: "Training Routes and Career Organizations",
            3: "Classify Four Construction Careers",
            4: "Fictional Visual Observation Lab",
            5: "Evidence Report and Individual Briefing",
        }
        extras = {
            1: ("Assignment", career["id"], CAREER_TITLE),
            2: ("Assignment", routes["id"], ROUTES_TITLE),
            3: ("Assignment", classify["id"], CLASSIFY_TITLE),
            4: ("Assignment", report["id"], REPORT_TITLE),
        }
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await prior.upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 5SW Wk3 Day {day} - {day_names[day]}"
            student_page = await common.upsert_page(
                client,
                student_title,
                common.render(
                    "5sw-wk3-student.html",
                    {"COURSE_ID": COURSE_ID, "DAY": day, **CONTRACTS[day], **student[day]},
                ),
            )
            teacher_title = f"TEACHER: 5SW Wk3 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(
                client,
                teacher_title,
                common.render(
                    "5sw-wk3-teacher.html",
                    {
                        "COURSE_ID": COURSE_ID,
                        "DAY": day,
                        "STUDENT_PAGE_URL": student_page["url"],
                        **CONTRACTS[day],
                        **teacher[day],
                    },
                ),
            )
            await prior.upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await prior.upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            order.extend([("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title)])
            pages[day] = {"teacher": teacher_page, "student": student_page}
            if day in extras:
                kind, key, title = extras[day]
                await prior.upsert_item(client, module["id"], kind, key, title)
                order.append((kind, key, title))

        final_items = await prior.reconcile_module_items(client, module["id"], order)
        if len(final_items) != 19:
            raise RuntimeError(f"Expected 19 exact Week 3 module items; found {len(final_items)}")
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
        if module.get("published") or len([entry for entry in modules if entry.get("name") == MODULE_NAME]) != 1:
            raise RuntimeError(f"Final module invariant failed: published={module.get('published')}")
        for day, pair in pages.items():
            for kind, page in pair.items():
                fresh = await common.api(client, "GET", f"/courses/{COURSE_ID}/pages/{page['url']}")
                if fresh.get("published"):
                    raise RuntimeError(f"Day {day} {kind} page is published")
                pair[kind] = fresh
        career = await assert_annotation_assignment(client, career, files["CAREER"]["id"])
        routes = await assert_annotation_assignment(client, routes, files["ROUTES"]["id"])
        classify = await assert_annotation_assignment(client, classify, files["CLASSIFY"]["id"], mapped=True)
        if (
            classify.get("assignment_group_id") != minor_group["id"]
            or RUBRIC_NOTE_MARKER not in (classify.get("description") or "")
        ):
            raise RuntimeError(f"Final Minor group/rubric invariant failed for {CLASSIFY_TITLE!r}")
        report = await assert_annotation_assignment(client, report, files["REPORT"]["id"], media=True)
        support_folder = await common.lock_folder_files(client, support_folder)
        visual_folder = await common.lock_folder_files(client, visual_folder)
        print(json.dumps({
            "module": {"id": module["id"], "published": module["published"]},
            "assignments": {
                name: {"id": value["id"], "published": value.get("published"), "submission_types": value.get("submission_types")}
                for name, value in {"career": career, "routes": routes, "classify": classify, "report": report}.items()
            },
            "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
            "visual_folder": {"id": visual_folder["id"], "locked": visual_folder["locked"]},
            "files": {key: value["id"] for key, value in files.items()},
            "visuals": {key: value["id"] for key, value in visual_files.items()},
            "pages": {str(day): {kind: {"url": value["url"], "published": value["published"]} for kind, value in pair.items()} for day, pair in pages.items()},
            "items": [{"position": item["position"], "type": item["type"], "title": item["title"]} for item in final_items],
        }, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
