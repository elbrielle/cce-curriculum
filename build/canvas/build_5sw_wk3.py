"""Build the unpublished 5SW Week 3 Construction evidence module."""

import asyncio
import json
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
        "OBJECTIVE": "Students will organize construction evidence and deliver a clear individual professional briefing.",
        "TEKS": "d(1)(C), d(4)(C)",
        "DOL": "Individual evidence report + live, private recorded, teacher-conference, or accommodation-aligned oral/AAC briefing.",
        "I_CAN": "turn careful evidence into a clear report and brief one finding through an approved private route.",
        "SHOW": "Submit the formative evidence report and one 30–45 second oral/AAC briefing with a visible clue, cautious possibility, limit, next role, and work product.",
    },
}


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    found = next((module for module in modules if module["name"] == MODULE_NAME), None)
    data = {"module[published]": "false"}
    if found:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data=data)
    data["module[name]"] = MODULE_NAME
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


async def mapped_minor_assignment(client):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    matches = [entry for entry in assignments if entry.get("name") == CLASSIFY_TITLE]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one existing mapped Minor assignment named {CLASSIFY_TITLE!r}; found {len(matches)}"
        )
    found = matches[0]
    if float(found.get("points_possible") or 0) != 100:
        raise RuntimeError(
            f"Refusing to modify {CLASSIFY_TITLE!r}: expected 100 points, found {found.get('points_possible')}"
        )
    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group = next((entry for entry in groups if entry.get("id") == found.get("assignment_group_id")), None)
    if not group or group.get("name") != "Minor Assessments (40%)":
        raise RuntimeError(
            f"Refusing to modify {CLASSIFY_TITLE!r}: expected Minor Assessments (40%) group"
        )
    return found


async def require_minor_assignment(client, description, attachment_id):
    found = await mapped_minor_assignment(client)
    return await common.api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{found['id']}",
        data={
            "assignment[name]": CLASSIFY_TITLE,
            "assignment[description]": description,
            "assignment[published]": "false",
            "assignment[points_possible]": "100",
            "assignment[grading_type]": "points",
            "assignment[submission_types][]": ["student_annotation", "online_upload", "online_text_entry"],
            "assignment[annotatable_attachment_id]": str(attachment_id),
        },
    )


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")

    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        # Fail before module, folder, file, page, or practice-assignment writes.
        await mapped_minor_assignment(client)
        module = await ensure_module(client)
        support_path = "course files/CCR Materials/5SW/Wk3"
        support_folder = await common.ensure_folder(client, support_path)
        worksheet_names = {
            "CAREER": "5sw-wk3-construction-career-evidence.pdf",
            "ROUTES": "5sw-wk3-routes-and-organizations.pdf",
            "CLASSIFY": "5sw-wk3-labor-classification.pdf",
            "REPORT": "5sw-wk3-fictional-evidence-report.pdf",
            "RUBRIC": "5sw-wk3-construction-classification-rubric.pdf",
            "REPORT_RUBRIC": "5sw-wk3-construction-evidence-rubric.pdf",
        }
        files = {
            key: await common.upload(client, ROOT / "docs/resources/worksheets" / name, support_path)
            for key, name in worksheet_names.items()
        }

        visual_path = "course files/CCR Materials/5SW/Wk3/Day 4 Licensed Visuals"
        await common.ensure_folder(client, visual_path)
        visual_names = {
            "image1": "spot-problem-image-1.jpg",
            "image2": "spot-problem-image-2.jpg",
            "image3": "spot-problem-image-3.jpg",
            "image4": "spot-problem-image-4.jpg",
            "image5": "spot-problem-image-5.jpg",
            "thermal": "fyf-p178-thermal-comparison.jpg",
        }
        visual_files = {
            key: await common.upload(client, ASSETS / "day4" / name, visual_path)
            for key, name in visual_names.items()
        }

        career = await common.upsert_assignment(
            client,
            CAREER_TITLE,
            "<p>Annotate or upload the fixed construction career evidence, type labeled responses, or use paper.</p>",
            ["student_annotation", "online_upload", "online_text_entry"],
            files["CAREER"]["id"],
        )
        routes = await common.upsert_assignment(
            client,
            ROUTES_TITLE,
            "<p>Compare two dated education or training routes and identify one organization type, access step, and value.</p>",
            ["student_annotation", "online_upload", "online_text_entry"],
            files["ROUTES"]["id"],
        )
        classify = await require_minor_assignment(
            client,
            "<p>Use the fixed May 2024 U.S. evidence and published classroom comparison rule. Submit four supported classifications, a trend comparison, recommendation, and evidence limitation.</p>",
            files["CLASSIFY"]["id"],
        )
        report = await common.upsert_assignment(
            client,
            REPORT_TITLE,
            "<p>Submit the private fictional evidence report and a 30–45 second live, private audio/video, teacher-conference, or accommodation-aligned oral/AAC briefing. This remains formative, worth 0 points, omitted from the final grade, and unpublished.</p>",
            ["online_upload", "online_text_entry", "media_recording"],
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
                "TODAY": "<ul><li>complete five report blocks;</li><li>write a thermal-evidence boundary;</li><li>prepare a 30–45 second briefing;</li><li>submit privately.</li></ul>",
                "READY": f'<p>Reopen {link(files["REPORT"]["id"], "the shared five-page evidence report")} from Day 4 and {link(files["REPORT_RUBRIC"]["id"], "the formative report feedback guide")}. Revise the same findings; do not recopy them into a second packet.</p>',
                "MEDIA": "",
                "LANGUAGE": "<p><strong>Word bank:</strong> finding/hallazgo · corroborate/confirmar con otra evidencia · briefing/informe breve · client/cliente · next professional/siguiente profesional.</p><p><strong>Use this frame:</strong> In [image/area], I observe [clue]. It could indicate [possibility], but the image cannot prove [limit]. A qualified [role] should check next.</p>",
                "STEPS": step(1, "Complete each finding", "<p>Use observation, possible meaning, evidence limit, and next qualified professional. Do not add prices, purchase advice, or a diagnosis.</p>")
                + step(2, "Write the thermal boundary", "<p>Explain what the temperature pattern shows and what corroboration would still be needed.</p>")
                + step(3, "Prepare the briefing", "<p>Choose one finding. In 30–45 seconds, deliver the evidence, careful claim, limit, next role, and the work product that worker would create or use. Use a live teacher conference, private audio/video, or accommodation-aligned oral/AAC route.</p>")
                + step(4, "Submit privately", f'<p><a href="{urls["report"]}">Submit the report and briefing evidence</a>. Public speaking is not required.</p>'),
                "EXIT": "<p>Explain how careful evidence language protects both the client and the qualified worker who checks next.</p>",
                "DONE": "<ul><li>five expanded finding blocks;</li><li>thermal boundary;</li><li>one complete individual oral/AAC briefing;</li><li>qualified role and work product named;</li><li>private submission and feedback-guide self-check.</li></ul>",
                "SUPPORT": "<p>finding = hallazgo · corroborate = confirmar con otra evidencia · briefing = informe breve · client = cliente · next professional = siguiente profesional.</p>",
                "FALLBACK": "<p>Complete the same report independently from the embedded Day 4 images. Use a live teacher conference, private audio/video, or accommodation-aligned oral/AAC route. If an accommodation changes the evidence mode, the teacher records the d(4)(C) decision separately.</p>",
            },
        }

        teacher = {
            1: {
                "TITLE": "Construction Careers and Preparation",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(2)(A)",
                "ALERT": "<strong>Use current names and bounded claims.</strong> MacArthur currently lists Construction within ACE. Do not present the older workbook label, NCCER, SkillsUSA, or one trade license ladder as a current universal district guarantee.",
                "PREP": f'<ul><li>Post {link(files["CAREER"]["id"], "the three-page fixed career packet")} and annotation activity.</li><li>Model occupation, source, date, geography, measure, and preparation boundary.</li><li>Keep H&amp;L optional.</li></ul>',
                "EVIDENCE": "<p>Formative three-career comparison, route judgment, and verification question.</p>",
                "FLOW": flow("#315f4c", "Current pathway · 5", "Construction within ACE.") + flow("#4c8b38", "Career cards · 15", "Work, preparation, pay, outlook.") + flow("#8a4f2b", "Compare · 15", "Three routes and boundaries.") + flow("#d39b22", "Decision · 10", "Evidence-based fit and question.") + flow("#315f4c", "Exit · 5", "Career, preparation, boundary."),
                "MONITOR": "<p>Full credit keeps high-school pathway, postsecondary training, Registered Apprenticeship, and trade-specific licensing distinct. Do not accept invented DFW starting pay or a universal apprentice–journeyworker–master sequence.</p>",
                "RESOURCES": '<p><a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte/macarthur-high-school">Irving ISD MacArthur CTE</a> · current BLS occupation pages in the packet. FYF claims are historical workbook context unless separately verified.</p>',
                "SUPPORT": "<p>Read one card at a time. The packet gives dedicated response lines rather than a cramped multi-career grid. Accept typed, enlarged, dictated, or paper responses.</p>",
                "FALLBACK": "<p>No platform login, open search, or partner is required.</p>",
            },
            2: {
                "TITLE": "Training Routes and Career Organizations",
                "SUBTITLE": "50 minutes · TEKS d(3)(G), d(3)(H)",
                "ALERT": "<strong>Students do not apply.</strong> They compare dated route cards and sequence steps; no contact form, account, or personal data is entered.",
                "PREP": f'<ul><li>Post {link(files["ROUTES"]["id"], "the four-page routes and organizations packet")} and annotation activity.</li><li>Review the two dated route cards.</li><li>Model the difference among a union, association, CTSO, and credential body.</li></ul>',
                "EVIDENCE": "<p>Formative two-route comparison, ordered application/enrollment steps, organization classification, access, and value.</p>",
                "FLOW": flow("#315f4c", "Stable facts · 5", "What Registered Apprenticeship is.") + flow("#4c8b38", "Two routes · 12", "Dated cards, variable terms.") + flow("#8a4f2b", "Compare/sequence · 23", "Eligibility through next verification.") + flow("#d39b22", "Organization · 7", "Type, access, value.") + flow("#315f4c", "Exit · 3", "Two steps and one organization."),
                "MONITOR": "<p>Accept multiple route judgments when the student uses the published facts. Registered Apprenticeship is paid and structured; sponsor eligibility, length, wage, cost, schedule, and license relationship vary. An industry certification is not automatically college credit. For d(3)(H), students must identify AGC as a professional/trade association, explain access through a future participating college chapter, and name one documented value.</p>",
                "RESOURCES": '<p><a href="https://www.apprenticeship.gov/career-seekers">Apprenticeship.gov Career Seekers</a> · <a href="https://www.dallascollege.edu/study/construction-technology/">Dallas College Construction Technology</a> · <a href="https://www.agc.org/connect/chapters/student-chapters">AGC Student Chapters</a>. Current provider steps and the AGC access/value boundary are dated in the packet.</p>',
                "SUPPORT": "<p>Use arrows or numbered cards for sequencing. Students may respond privately; no cold contact or public sharing.</p>",
                "FALLBACK": "<p>Fixed cards replace live provider browsing and remain usable after absence or a site change.</p>",
            },
            3: {
                "TITLE": "Classify Four Construction Careers",
                "SUBTITLE": "50 minutes · TEKS d(5)(A), d(5)(B)",
                "ALERT": "<strong>The labels are a published classroom comparison rule.</strong> They are not official BLS or TWC designations and do not prove a DFW shortage.",
                "PREP": f'<ul><li>Post {link(files["CLASSIFY"]["id"], "the four-page classification packet")}, {link(files["RUBRIC"]["id"], "the Minor 3 rubric")}, and annotation activity.</li><li>Project the three comparison thresholds.</li><li>Model one supported yes/no and one limitation.</li></ul>',
                "EVIDENCE": "<p><strong>Minor 3 in the 5SW assessment map:</strong> four supported classifications, trend comparison, recommendation, and evidence limitation. The importer protects the existing 100-point assignment in Minor Assessments (40%).</p>",
                "FLOW": flow("#315f4c", "Rule · 5", "Same basis and transparent thresholds.") + flow("#4c8b38", "Model · 8", "One label with evidence.") + flow("#8a4f2b", "Four careers · 27", "Two labeled records per landscape page.") + flow("#d39b22", "Compare · 7", "Trend and limitation.") + flow("#315f4c", "Exit · 3", "What could change."),
                "MONITOR": "<p>Key: Construction Manager = yes/yes/yes; Carpenter = course-rule judgment on skill with evidence, yes wage, yes demand; Equipment Operator = course-rule judgment on skill, yes wage, yes demand; Masonry Worker = course-rule judgment on skill, yes wage, no demand. Require the packet's preparation rule and accept defensible nuance.</p>",
                "RESOURCES": '<p><a href="https://www.bls.gov/emp/tables/occupational-projections-and-characteristics.htm">BLS projection characteristics</a> and dated occupation pages. Same basis: May 2024 U.S. median and 2024–34 national projections.</p>',
                "SUPPORT": "<p>Two occupations share each landscape response page, with one labeled line for each evidence job and a separate limitation area. Read numbers aloud, allow calculator or typed response, and score reasoning rather than English mechanics.</p>",
                "FALLBACK": "<p>The packet is the complete dataset. Students never estimate missing data or depend on H&amp;L.</p>",
            },
            4: {
                "TITLE": "Fictional Visual Observation Lab",
                "SUBTITLE": "50 minutes · TEKS d(1)(C)",
                "ALERT": "<strong>This is not a home inspection.</strong> Students analyze supplied fictional images only and never touch a real panel, inspect a home, diagnose a defect, estimate repairs, or advise a buyer.",
                "PREP": f'<ul><li>Have students open FYF pp. 176–178, then post {link(files["REPORT"]["id"], "the shared five-page evidence report")} and annotation activity.</li><li>Open the five locked photos and thermal page.</li><li>Model observation → possibility → limit → qualified role.</li></ul>',
                "EVIDENCE": "<p>Formative draft of Findings 1–5 plus the thermal comparison in the same report students revise on Day 5. Students do not complete a second observation packet.</p>",
                "FLOW": flow("#315f4c", "Boundary · 5", "Fictional image analysis only.") + flow("#4c8b38", "Model · 8", "Observation before inference.") + flow("#8a4f2b", "Five images · 25", "Roomy record per image.") + flow("#d39b22", "Thermal · 7", "Pattern and corroboration.") + flow("#315f4c", "Exit · 5", "Complete evidence chain."),
                "MONITOR": "<p>Key: #1 no visible concern required from this image; #2 visibly worn/damaged shingles; #3 ceiling/wall staining; #4 open service panel with visible cables, but image alone does not prove a violation; #5 damaged/swollen under-sink cabinet base consistent with possible moisture. Thermal differences suggest a location to investigate, not a diagnosis. Accept other careful interpretations tied to visible evidence.</p>",
                "RESOURCES": '<p>Licensed Climber Notes photos and FYF p.178 remain in authenticated Canvas. <a href="https://www.trec.texas.gov/become-licensed/professional-real-estate-inspector">TREC inspector licensing</a> establishes the professional boundary.</p>',
                "SUPPORT": "<p>Use zoom and neutral read-aloud descriptions. Do not encode the answer in alt text. Accept dictation, typed response, enlarged print, and explicit no-visible-concern judgments.</p>",
                "FALLBACK": "<p>All six visuals are embedded. An absent student can complete the identical individual route without a live projection.</p>",
            },
            5: {
                "TITLE": "Evidence Report and Individual Briefing",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(4)(C)",
                "ALERT": "<strong>Formative inspection report and professional briefing.</strong> Use the report and briefing for feedback; they are not one of the two mapped 5SW majors. Keep unpublished and ungraded until the review gate passes.",
                "PREP": f'<ul><li>Reopen {link(files["REPORT"]["id"], "the shared five-page report")}, {link(files["REPORT_RUBRIC"]["id"], "the formative report feedback guide")}, and private Assignment.</li><li>Keep Day 4 visuals available.</li><li>Offer live teacher-conference, private audio/video, and accommodation-aligned oral/AAC briefing routes.</li></ul>',
                "EVIDENCE": "<p>Five expanded findings, thermal boundary, and one individual 30–45 second evidence briefing that names the qualified role and the professional work product used next. Group delivery never substitutes for individual evidence.</p>",
                "FLOW": flow("#315f4c", "Reopen evidence · 5", "Images and Day 4 draft.") + flow("#4c8b38", "Model revision · 5", "Careful language and next role.") + flow("#8a4f2b", "Revise/report · 25", "Five findings, thermal boundary, summary.") + flow("#d39b22", "Briefings · 12", "Individual oral/AAC routes.") + flow("#315f4c", "Exit · 3", "Why language matters."),
                "MONITOR": "<p>Check visible evidence, bounded inference, evidence limit, correct next role, that worker's next work product, organization, and clarity. Do not score accent, confidence, artistic layout, platform choice, or English mechanics unless meaning is unclear.</p>",
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
            item = next(item for item in items if matches_item(item, kind, key))
            await common.api(
                client,
                "PUT",
                f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}",
                data={"module_item[position]": position, "module_item[title]": title},
            )

        final_items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        if len(final_items) != len(order):
            raise RuntimeError(f"Expected {len(order)} Week 3 module items; found {len(final_items)}")
        ordered_final = sorted(final_items, key=lambda entry: entry.get("position", 0))
        for position, ((kind, key, _title), entry) in enumerate(zip(order, ordered_final), 1):
            if entry.get("position") != position or not matches_item(entry, kind, key):
                raise RuntimeError(f"Week 3 module order mismatch at position {position}")
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        print(json.dumps({
            "module": {"id": module["id"], "published": module["published"]},
            "assignments": {
                name: {"id": value["id"], "published": value.get("published"), "submission_types": value.get("submission_types")}
                for name, value in {"career": career, "routes": routes, "classify": classify, "report": report}.items()
            },
            "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
            "files": {key: value["id"] for key, value in files.items()},
            "visuals": {key: value["id"] for key, value in visual_files.items()},
            "pages": {str(day): {kind: {"url": value["url"], "published": value["published"]} for kind, value in pair.items()} for day, pair in pages.items()},
            "items": [{"position": item["position"], "type": item["type"], "title": item["title"]} for item in final_items],
        }, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
