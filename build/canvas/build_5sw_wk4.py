"""Build the unpublished 5SW Week 4 skilled-trades evidence module."""

import asyncio
import json
import sys

import httpx

import build_5sw_wk1 as prior


common = prior.common
COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/5sw/wk4"
MODULE_NAME = "5SW Wk4: Skilled Trades — Evidence, Routes, and Communication"

ASSIGNMENT_TITLES = {
    1: "PRACTICE: Skilled-Trades Career Evidence",
    2: "PRACTICE: HVAC Evidence-First Field Notes",
    3: "MAJOR 1 EVIDENCE: Part A — Skilled-Trades Labor Classification",
    4: "PRACTICE: Current Entry Routes",
    5: "MAJOR 1: Skilled-Trades Classification and Individual Response",
}


CONTRACTS = {
    1: {
        "TOPIC": "Career Opportunities",
        "OBJECTIVE": "Students will identify career opportunities within one or more career clusters and research and describe academic, technical, certification, and training requirements for one or more careers in an identified career cluster using evidence from Career Opportunities.",
        "TEKS": "d(1)(C), d(2)(A)",
        "DOL": "four-career preparation record.",
        "I_CAN": "identify four skilled-trades careers and keep each occupation, training route, license, and credential separate.",
        "SHOW": "Complete the four-career preparation record with accurate boundaries, two differences, and one official-source question.",
    },
    2: {
        "TOPIC": "Transferable Skills",
        "OBJECTIVE": "Students will identify skills that transfer among a variety of careers using evidence from Transferable Skills.",
        "TEKS": "d(4)(B)",
        "DOL": "four fictional service notes and one transfer sentence.",
        "I_CAN": "turn supplied HVAC evidence into careful notes and explain how evidence-first writing transfers to another career.",
        "SHOW": "Complete four fictional service notes using the workbook fields with safer labels, then explain one career transfer.",
    },
    3: {
        "TOPIC": "Labor Trends",
        "OBJECTIVE": "Students will analyze labor-market trends related to a career of interest and classify evidence of high-skill, high-wage, or high-demand occupations using labor-market information using evidence from Labor Trends.",
        "TEKS": "d(5)(A), d(5)(B)",
        "DOL": "four-career classification and limitation.",
        "I_CAN": "use one dated evidence set and a published classroom rule to classify four skilled-trades careers.",
        "SHOW": "Submit Major 1 Part A with four supported classifications, a trend comparison, and one local-data limitation.",
    },
    4: {
        "TOPIC": "Career Preparation",
        "OBJECTIVE": "Students will research and describe academic, technical, certification, and training requirements for one or more careers in an identified career cluster and investigate and report the steps required to participate or enroll in career and educational opportunities using evidence from Career Preparation.",
        "TEKS": "d(2)(A), d(3)(G)",
        "DOL": "two-route comparison and ordered next steps.",
        "I_CAN": "compare two current preparation routes and put the verification and enrollment steps in order.",
        "SHOW": "Complete the route comparison, evidence-based choice, three ordered actions, and one condition that must be rechecked.",
    },
    5: {
        "TOPIC": "Career Opportunities",
        "OBJECTIVE": "Students will identify career opportunities within one or more career clusters and give an oral professional presentation about career and college exploration using appropriate technology using evidence from Career Opportunities.",
        "TEKS": "d(1)(C), d(4)(C)",
        "DOL": "fictional response plan and individual 30–45 second briefing.",
        "I_CAN": "use a fictional response plan to brief one priority, supplied clue, qualified role, and professional boundary.",
        "SHOW": "Submit the individual response companion and complete a 30–45 second live, private recorded, teacher-conference, or accommodation-aligned oral/AAC briefing.",
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


async def mapped_major_assignment(client):
    assignments = await common.paged(client, f"/courses/{COURSE_ID}/assignments")
    title = ASSIGNMENT_TITLES[5]
    matches = [entry for entry in assignments if entry.get("name") == title]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one existing mapped Major assignment named {title!r}; found {len(matches)}")
    found = matches[0]
    if float(found.get("points_possible") or 0) != 100:
        raise RuntimeError(f"Refusing to modify {title!r}: expected 100 points, found {found.get('points_possible')}")
    groups = await common.paged(client, f"/courses/{COURSE_ID}/assignment_groups")
    group = next((entry for entry in groups if entry.get("id") == found.get("assignment_group_id")), None)
    if not group or group.get("name") != "Major Assessments (60%)":
        raise RuntimeError(f"Refusing to modify {title!r}: expected Major Assessments (60%) group")
    return found


async def require_major_assignment(client, description, attachment_id):
    found = await mapped_major_assignment(client)
    return await common.api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{found['id']}",
        data={
            "assignment[name]": ASSIGNMENT_TITLES[5],
            "assignment[description]": description,
            "assignment[published]": "false",
            "assignment[points_possible]": "100",
            "assignment[grading_type]": "points",
            "assignment[assignment_group_id]": str(found["assignment_group_id"]),
            "assignment[omit_from_final_grade]": "false",
            "assignment[submission_types][]": [
                "student_annotation",
                "online_upload",
                "online_text_entry",
                "media_recording",
            ],
            "assignment[annotatable_attachment_id]": str(attachment_id),
        },
    )


def student_content(files, visuals, urls):
    link, step = common.file_link, common.step
    day2_media = (
        '<h3 style="color:#1f6073;border-bottom:3px solid #b8d5dd">Licensed visual references</h3>'
        + prior.image_tag(visuals["parts"]["id"], "Find Your Future page showing labeled HVAC system parts and their purposes")
        + '<div style="border-left:5px solid #d39b22;background:#fff8e7;padding:12px 16px;margin:14px 0"><strong>Read the model carefully:</strong> the workbook model uses more certain diagnosis/action language. In this lesson, your image note must use evidence, a cautious possibility, a limit, and a qualified next check.</div>'
        + prior.image_tag(visuals["model"]["id"], "Find Your Future HVAC field-note example with location, concern, observations, diagnosis, and action fields")
        + "".join(
            f'<h4>Fictional Ticket {number}</h4>' + prior.image_tag(
                visuals[f"ticket{number}"]["id"],
                f"Fictional HVAC service ticket {number} with a location, complaint, extra information, and equipment photo",
            )
            for number in range(1, 5)
        )
    )
    day5_media = (
        '<h3 style="color:#1f6073;border-bottom:3px solid #b8d5dd">Licensed scenario references</h3>'
        + prior.image_tag(visuals["plumbing_roles"]["id"], "Find Your Future page introducing a fictional plumbing response scenario and team roles")
        + prior.image_tag(visuals["plumbing_plan"]["id"], "Find Your Future page with a fictional water-line site plan, planning steps, twist, and presentation prompt")
    )
    return {
        1: {
            "TITLE": "Four Skilled-Trades Careers",
            "PURPOSE": "Compare four careers without confusing an occupation, training route, license, credential, or salary measure.",
            "TODAY": "<ul><li>read four fixed career cards;</li><li>record work and preparation;</li><li>compare two routes;</li><li>write one official-source question.</li></ul>",
            "READY": f'<p>Open {link(files["CAREER"]["id"], "the three-page career evidence packet")} or <a href="{urls[1]}">the Canvas annotation activity</a>.</p>',
            "MEDIA": "",
            "STEPS": step(1, "Keep the labels separate", "<p>An occupation is the job. Apprenticeship or college is a route. A state license or employer credential is a separate boundary.</p>")
            + step(2, "Record four careers", "<p>Use the packet for Electrician, Plumber/Pipefitter/Steamfitter, HVAC Mechanic/Installer, and Welder. Keep every number with its geography, year, and measure.</p>")
            + step(3, "Compare preparation", "<p>Explain two real differences. Do not force every trade into one apprentice–journeyworker–master ladder.</p>")
            + step(4, "Submit privately", f'<p>Use <a href="{urls[1]}">the practice activity</a>, typed labeled responses, or paper.</p>'),
            "EXIT": "<p>Name one career, one accurate preparation fact, and one boundary the evidence does not prove.</p>",
            "DONE": "<ul><li>four careers recorded;</li><li>two preparation differences;</li><li>one official-source question;</li><li>one evidence-based next interest.</li></ul>",
            "SUPPORT": "<p><strong>Word bank:</strong> occupation/ocupación · route/ruta de formación · license/licencia · credential/credencial · verify/verificar.</p><p><strong>Use this frame:</strong> I would investigate ___ because the evidence shows ___. I still need to verify ___ with ___.</p>",
            "FALLBACK": "<p>The fixed packet is the full route. H&amp;L, Xello, open search, screenshots, and a partner are not required.</p>",
        },
        2: {
            "TITLE": "HVAC Evidence-First Field Notes",
            "PURPOSE": "Turn supplied complaints and images into useful written notes without pretending one photo proves a diagnosis.",
            "TODAY": "<ul><li>use HVAC parts vocabulary;</li><li>analyze four fictional tickets;</li><li>write evidence, possibility, limit, and next check;</li><li>transfer the skill to another career.</li></ul>",
            "READY": f'<p>Open your FYF workbook to pp. 185–190. Use {link(files["HVAC"]["id"], "the six-page safe-label fallback")} or <a href="{urls[2]}">the Canvas annotation activity</a> only if you do not have the workbook or need the enlarged scaffold. Do not complete both.</p>',
            "MEDIA": day2_media,
            "STEPS": step(1, "Use the workbook fields with safer labels", "<p>On FYF pp. 187–190, keep <strong>Observation</strong>. Treat <strong>Diagnosed problems</strong> as <strong>Supported possibility</strong>. Treat <strong>Action</strong> as <strong>Evidence limit + qualified next check</strong>.</p>")
            + step(2, "Start with supplied evidence", "<p>Record the location, complaint, extra information, and only the details the ticket states or the image visibly shows.</p>")
            + step(3, "Use cautious language", "<p>Write <em>could be consistent with</em>. Then state what one image cannot prove and what a qualified HVAC professional evaluates next.</p>")
            + step(4, "Transfer the writing skill", f'<p>In <a href="{urls[2]}">the private practice activity</a>, name another career that creates notes for the next person and explain why accuracy matters. Upload workbook pages, type labeled responses, or use the safe-label fallback.</p>'),
            "EXIT": "<p>Rewrite one vague note as an evidence-first note and name who uses it next.</p>",
            "DONE": "<ul><li>four complete ticket pages;</li><li>evidence separated from diagnosis;</li><li>one limit per ticket;</li><li>qualified next check;</li><li>one career transfer.</li></ul>",
            "SUPPORT": "<p><strong>Word bank:</strong> complaint/problema reportado · visible evidence/evidencia visible · could be consistent with/podría ser consistente con · limit/límite · qualified/calificado.</p><p><strong>Use this frame:</strong> The ticket states or shows ___. This could be consistent with ___, but it does not prove ___. A qualified HVAC professional should check ___.</p>",
            "FALLBACK": "<p>All four tickets and both workbook references are embedded here. Use zoom, read-aloud, typed response, dictation, or paper.</p>",
        },
        3: {
            "TITLE": "Classify Four Skilled-Trades Careers",
            "PURPOSE": "Use one comparable national dataset and a published classroom rule to classify labor evidence.",
            "TODAY": "<ul><li>read the classroom comparison rule;</li><li>classify four careers;</li><li>cite a fact for each label;</li><li>state a local-data limitation.</li></ul>",
            "READY": f'<p>Open {link(files["CLASSIFY"]["id"], "the four-page classification packet")} or <a href="{urls[3]}">Major 1 Part A in Canvas</a>. Keep this evidence available for the final score on Day 5; you will not need to copy it into a second packet.</p>',
            "MEDIA": "",
            "STEPS": step(1, "Read the rule", "<p>High wage means above $49,500 May 2024 U.S. median. High demand means growth above 3.1%. High skill uses the packet's documented preparation rule. These are classroom labels.</p>")
            + step(2, "Classify each occupation", "<p>Cite preparation, median, or growth evidence for every yes/no decision.</p>")
            + step(3, "Compare growth and openings", "<p>Annual openings include replacement needs. A large openings number can appear beside slower growth.</p>")
            + step(4, "State the limit", "<p>Explain why national medians and projections do not prove DFW starting pay, a live vacancy, or a worker shortage.</p>"),
            "EXIT": "<p>State one supported conclusion and one limitation.</p>",
            "DONE": "<ul><li>four careers classified;</li><li>evidence cited for every label;</li><li>growth/openings comparison;</li><li>one national-to-local limitation.</li></ul>",
            "SUPPORT": "<p><strong>Word bank:</strong> classification/clasificación · median/mediana · growth/crecimiento · annual openings/vacantes anuales · limitation/limitación.</p><p><strong>Use this frame:</strong> ___ is or is not high-___ under the course rule because the evidence shows ___. This does not prove ___.</p>",
            "FALLBACK": "<p>All required data is in the packet. Never estimate a missing value; mark not available or not comparable.</p>",
        },
        4: {
            "TITLE": "Current Entry Routes",
            "PURPOSE": "Compare two route types and put the real verification and enrollment steps in order.",
            "TODAY": "<ul><li>compare trade-specific Texas boundaries;</li><li>read two dated route cards;</li><li>choose a route for a fictional student;</li><li>sequence three next actions.</li></ul>",
            "READY": f'<p>Open {link(files["ROUTES"]["id"], "the four-page current entry-routes packet")} or <a href="{urls[4]}">the Canvas annotation activity</a>.</p>',
            "MEDIA": "",
            "STEPS": step(1, "Compare state boundaries", "<p>Electrical, plumbing, HVAC, and welding do not use one universal license ladder.</p>")
            + step(2, "Read both route cards", "<p>Compare a Registered Apprenticeship route with current Dallas College Electrical Technology examples. Published time and cost are estimates, not promises.</p>")
            + step(3, "Decide for fictional Jordan", "<p>Use two card details and name one advantage of the route not selected.</p>")
            + step(4, "Put actions in order", "<p>Write three exact future steps and the official source that must be rechecked. Do not submit a real application.</p>"),
            "EXIT": "<p>Name one route, two exact steps, one variable condition, and the official source to recheck.</p>",
            "DONE": "<ul><li>state boundaries compared;</li><li>two route cards completed;</li><li>evidence-based decision;</li><li>three ordered actions;</li><li>one variable condition.</li></ul>",
            "SUPPORT": "<p><strong>Word bank:</strong> apprenticeship/aprendizaje registrado · eligibility/requisitos · estimated cost/costo estimado · enrollment/inscripción · official source/fuente oficial.</p><p><strong>Use this frame:</strong> I recommend ___ for Jordan because the card says ___ and ___. The other route may be stronger when ___.</p>",
            "FALLBACK": "<p>The fixed dated cards replace open-web searching. Do not create an account, enter personal data, contact a sponsor, or apply in class.</p>",
        },
        5: {
            "TITLE": "Fictional Water-Line Response",
            "PURPOSE": "Build a communication and evidence plan for a fictional event, then brief one priority without giving real technical directions.",
            "TODAY": "<ul><li>assign functional team roles;</li><li>mark a fictional site plan;</li><li>sequence communication priorities;</li><li>deliver one individual evidence briefing.</li></ul>",
            "READY": f'<p>Open FYF pp. 194–195, {link(files["WATER"]["id"], "the two-page individual response companion")}, {link(files["CLASSIFY"]["id"], "your Day 3 classification evidence")}, and {link(files["RUBRIC"]["id"], "the two-page rubric")}. Your teacher scores the Day 3 evidence where you already submitted or turned it in; do not copy it again.</p>',
            "MEDIA": day5_media,
            "STEPS": step(1, "Use FYF for the team plan", "<p>Complete the role and priority work on FYF pp. 194–195. A team may use chart paper for the sketch. The sketch communicates supplied boundaries and evidence; it is not a repair or excavation plan.</p>")
            + step(2, "Stay inside the simulation boundary", "<p>Students do not locate utilities, enter a street, direct traffic, shut a valve, excavate, choose repair materials, use tools, or create real repair instructions.</p>")
            + step(3, "Complete your individual response", "<p>Use the two-page companion to record one priority, supplied clue, qualified role and work product, professional boundary, and crowd/time-pressure response.</p>")
            + step(4, "Complete the oral/AAC briefing", f'<p>Use <a href="{urls[5]}">the private Major activity</a>. Give the 30–45 second briefing live, in a teacher conference, through private audio/video, or through an accommodation-aligned oral/AAC route. A written plan or transcript may support the briefing but does not by itself demonstrate d(4)(C).</p>'),
            "EXIT": "<p>Name one A&amp;C career involved and the work product that person supplies.</p>",
            "DONE": "<ul><li>Day 3 classification evidence is available to the teacher;</li><li>FYF team plan completed;</li><li>individual priority, clue, role/work product, and boundary recorded;</li><li>crowd/time-pressure response;</li><li>individual 30–45 second oral/AAC briefing.</li></ul>",
            "SUPPORT": "<p><strong>Word bank:</strong> priority/prioridad · supplied evidence/evidencia proporcionada · authorized/autorizado · boundary/límite · briefing/informe breve.</p><p><strong>Use this frame:</strong> Our first priority is ___ because the supplied clue shows ___. A qualified ___ owns ___. Our student team cannot ___.</p>",
            "FALLBACK": "<p>Complete the same fictional response independently. Use a private live, teacher-conference, audio/video, or accommodation-aligned oral/AAC route. A planning transcript supports access but is not labeled oral evidence by itself.</p>",
        },
    }


def teacher_content(files):
    link, flow = common.file_link, common.flow
    color = "#1f6073"
    return {
        1: {
            "TITLE": "Four Skilled-Trades Careers", "SUBTITLE": "50 minutes · TEKS d(1)(C), d(2)(A)",
            "ALERT": "<strong>Keep occupation, route, and license separate.</strong> H&amp;L is optional; fixed evidence carries the lesson. Do not invent a universal trade ladder or DFW starting salary.",
            "PREP": f'<ul><li>Post {link(files["CAREER"]["id"], "the three-page career packet")} and annotation activity.</li><li>Project one labeled source/date/geography/measure example.</li><li>Keep current MacArthur Construction and Welding labels bounded. Do not promise a credential or placement.</li></ul>',
            "EVIDENCE": "<p>Formative four-career preparation record, two differences, and one official-source verification question.</p>",
            "FLOW": flow(color, "Warm-up · 5", "Building systems and connected roles.") + flow("#4c8b38", "Boundaries · 8", "Occupation, route, license, credential.") + flow("#b35d2e", "Career cards · 22", "Four fixed occupations.") + flow("#d39b22", "Compare · 10", "Differences and verification.") + flow(color, "Exit · 5", "Career, fact, boundary."),
            "MONITOR": "<p>Electrician: HS typical; most learn through apprenticeship; Texas license eligibility through TDLR. Plumbing: HS typical; most learn through apprenticeship; TSBPE governs registration/license. HVAC: postsecondary nondegree award typical plus long-term OJT; TDLR technician/contractor boundaries. Welding: technical/OJT routes; no one universal Texas license.</p>",
            "RESOURCES": '<p><a href="https://www.bls.gov/ooh/construction-and-extraction/electricians.htm">BLS Electricians</a> · <a href="https://www.bls.gov/ooh/construction-and-extraction/plumbers-pipefitters-and-steamfitters.htm">BLS Plumbing/Pipefitting</a> · <a href="https://www.bls.gov/ooh/installation-maintenance-and-repair/heating-air-conditioning-and-refrigeration-mechanics-and-installers.htm">BLS HVAC</a> · <a href="https://www.bls.gov/ooh/production/welders-cutters-solderers-and-brazers.htm">BLS Welding</a>.</p>',
            "SUPPORT": "<p>The four-career record uses short lines only for short facts; all reasoning prompts have dedicated multi-line blocks. Accept typed, enlarged, dictated, or paper responses.</p>",
            "FALLBACK": "<p>No live platform, open search, partner, or screenshot is required.</p>",
        },
        2: {
            "TITLE": "HVAC Evidence-First Field Notes", "SUBTITLE": "50 minutes · TEKS d(4)(B)",
            "ALERT": "<strong>Images do not authorize diagnosis or repair.</strong> The FYF model uses stronger diagnosis/action language than this lesson. Students use evidence, possibility, limit, and qualified next check.",
            "PREP": f'<ul><li>Have students open FYF pp. 185–190. Post {link(files["HVAC"]["id"], "the six-page safe-label fallback")} only for no-workbook, absence, or enlarged access.</li><li>Open the six locked visuals in the student guide.</li><li>Model the three workbook relabels before students begin.</li></ul>',
            "EVIDENCE": "<p>Formative set of four workbook service notes using safer labels and one private written-communication transfer. Students use either FYF pp. 187–190 or the fallback, not both.</p>",
            "FLOW": flow(color, "Warm-up · 5", "Useful notes for the next person.") + flow("#4c8b38", "Evidence language · 8", "Complaint, clue, possibility, limit.") + flow("#b35d2e", "Parts · 7", "Vocabulary, not authorization.") + flow("#d39b22", "Four tickets · 25", "One page per ticket.") + flow(color, "Exit · 5", "Rewrite and transfer."),
            "MONITOR": "<p>Ticket 1: visible ice and weak cooling/airflow; root cause not proven. Ticket 2: heavy dust/debris on indoor coil and uneven airflow. Ticket 3: visibly dirty filter with supplied weak/dusty airflow. Ticket 4: weathered/dirty outdoor unit; image does not prove a failed component. Accept other careful interpretations tied to visible/supplied evidence.</p>",
            "RESOURCES": "<p>Licensed Climber Notes tickets and FYF pages remain in locked Canvas. No real HVAC check, reset, cleaning, or repair is assigned.</p>",
            "SUPPORT": "<p>Neutral alt text does not reveal the key. Offer zoom, read-aloud, dictation, typed response, workbook, or the enlarged safe-label fallback.</p>",
            "FALLBACK": "<p>Every load-bearing visual is embedded. An absent student completes the same individual route.</p>",
        },
        3: {
            "TITLE": "Classify Four Skilled-Trades Careers", "SUBTITLE": "50 minutes · TEKS d(5)(A), d(5)(B)",
            "ALERT": "<strong>Classroom comparison rule, not a government label.</strong> National projections do not prove a DFW shortage, current vacancy, or starting salary.",
            "PREP": f'<ul><li>Post {link(files["CLASSIFY"]["id"], "the four-page classification packet")} and annotation activity.</li><li>Project all three rule thresholds.</li><li>Model one yes/no with evidence and one limitation.</li></ul>',
            "EVIDENCE": "<p><strong>Major 1, Part A, in the 5SW assessment map:</strong> four supported classifications, trend/openings comparison, and national-to-local limitation. Day 3 remains a 0-point evidence collector; the mapped 100-point Major is the Day 5 assignment.</p>",
            "FLOW": flow(color, "Warm-up · 5", "Growth versus openings.") + flow("#4c8b38", "Rule · 8", "Transparent thresholds.") + flow("#b35d2e", "Model · 7", "Fact for every label.") + flow("#d39b22", "Classify · 25", "Two occupations per evidence page.") + flow(color, "Exit · 5", "Conclusion and limit."),
            "MONITOR": "<p>All four medians exceed $49,500. Electrician, plumbing/pipefitting, and HVAC growth exceed 3.1%; welding growth does not. High-skill decisions must cite the published preparation rule. Openings include replacement needs.</p>",
            "RESOURCES": '<p>May 2024 U.S. medians and 2024–34 national projections from current BLS occupation pages. Same basis across all four rows.</p>',
            "SUPPORT": "<p>Two occupations per landscape evidence page keep the packet to four pages while preserving labeled rows and full-width conclusion space. Read numbers aloud and score evidence/reasoning rather than English mechanics.</p>",
            "FALLBACK": "<p>All data is fixed. Never ask students to estimate a missing number or depend on H&amp;L.</p>",
        },
        4: {
            "TITLE": "Current Entry Routes", "SUBTITLE": "50 minutes · TEKS d(2)(A), d(3)(G)",
            "ALERT": "<strong>No real applications or personal data.</strong> Students compare dated route cards and practice verification steps only.",
            "PREP": f'<ul><li>Post {link(files["ROUTES"]["id"], "the four-page route packet")} and annotation activity.</li><li>Review TDLR, TSBPE, Apprenticeship.gov, and Dallas College boundaries.</li><li>Use fictional Jordan for the decision.</li></ul>',
            "EVIDENCE": "<p>Formative trade-specific boundary record, two-route comparison, evidence-based choice, and three ordered next steps.</p>",
            "FLOW": flow(color, "Warm-up · 5", "What must be verified?") + flow("#4c8b38", "State boundaries · 10", "Four trades, different rules.") + flow("#b35d2e", "Route cards · 15", "Apprenticeship and college examples.") + flow("#d39b22", "Sequence · 15", "Three actions and one tradeoff.") + flow(color, "Exit · 5", "Route, steps, variable, source."),
            "MONITOR": "<p>Registered Apprenticeship combines paid work, structured instruction, mentoring, progressive wages, and a portable credential; sponsor terms vary. Dallas College costs/times are published estimates. Accept either fictional choice when supported by two card details.</p>",
            "RESOURCES": '<p><a href="https://www.apprenticeship.gov/career-seekers">Apprenticeship.gov</a> · <a href="https://www.dallascollege.edu/study/electrical-tech/">Dallas College Electrical Technology</a> · <a href="https://www.tdlr.texas.gov/electricians/apply/individuals/journeyman-electrician.htm">TDLR Journeyman Electrician</a> · <a href="https://tsbpe.texas.gov/license-types/">TSBPE license types</a>.</p>',
            "SUPPORT": "<p>Allow arrows, numbered cards, typed response, dictation, or paper. The comparison table records short facts; the decision has seven full writing lines.</p>",
            "FALLBACK": "<p>Fixed route cards replace live browsing. No account, provider contact, or application is required.</p>",
        },
        5: {
            "TITLE": "Fictional Water-Line Response", "SUBTITLE": "50 minutes · TEKS d(1)(C), d(4)(C)",
            "ALERT": "<strong>Communication simulation only.</strong> Students do not locate utilities, enter a street, direct traffic, operate a valve, excavate, choose materials, use tools, or produce real repair instructions.",
            "PREP": f'<ul><li>Have students open FYF pp. 194–195. Post {link(files["WATER"]["id"], "the two-page individual response companion")}, {link(files["RUBRIC"]["id"], "the rubric")}, and private Major Assignment.</li><li>Keep Day 3 classification submissions available in a second SpeedGrader tab or collect the labeled paper packets; students do not resubmit them.</li><li>Offer live, teacher-conference, private audio/video, and accommodation-aligned oral/AAC briefing routes.</li></ul>',
            "EVIDENCE": "<p><strong>Major 1, Part B, in the 5SW assessment map:</strong> workbook team plan, individual response companion, and every student's 30–45 second oral/AAC briefing. The importer preserves the single mapped 100-point Major in Major Assessments (60%).</p>",
            "FLOW": flow(color, "Warm-up · 5", "Information and authority connections.") + flow("#4c8b38", "Roles · 8", "Functional jobs and supplied context.") + flow("#b35d2e", "Plan · 20", "Sketch, priorities, twist.") + flow("#d39b22", "Briefings · 12", "Individual equivalent routes.") + flow(color, "Exit · 5", "Career and work product."),
            "MONITOR": "<p>Strong plans begin with authorized alert/coordination, public protection, and evidence records. They do not begin with a student-authored technical repair move. Briefings must include priority, supplied evidence, qualified role, and boundary. Do not grade art, accent, confidence, or group popularity.</p>",
            "RESOURCES": "<p>Licensed FYF pages remain in authenticated Canvas. The packet explicitly corrects the boundary: the sketch is for communication and evidence planning, not utility locating or technical response.</p>",
            "SUPPORT": "<p>FYF holds the team role, priorities, and chart-paper sketch. The two-page companion gives each student dedicated writing and briefing-planning space. An independent route is equal.</p>",
            "FALLBACK": "<p>No H&amp;L favorite, Xello task, eDynamic activity, partner attendance, or public speaking is required.</p>",
        },
    }


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        # Fail before module, folder, file, page, or practice-assignment writes.
        await mapped_major_assignment(client)
        module = await ensure_module(client)
        support_path = "course files/CCR Materials/5SW/Wk4"
        support_folder = await common.ensure_folder(client, support_path)
        worksheet_names = {
            "CAREER": "5sw-wk4-skilled-trades-career-evidence.pdf",
            "HVAC": "5sw-wk4-hvac-evidence-first-field-notes.pdf",
            "CLASSIFY": "5sw-wk4-skilled-trades-classification.pdf",
            "ROUTES": "5sw-wk4-current-entry-routes.pdf",
            "WATER": "5sw-wk4-fictional-water-line-response.pdf",
            "RUBRIC": "5sw-wk4-skilled-trades-evidence-rubric.pdf",
        }
        files = {key: await common.upload(client, ROOT / "docs/resources/worksheets" / name, support_path) for key, name in worksheet_names.items()}

        visual_path = "course files/CCR Materials/5SW/Wk4/Locked Licensed Visuals"
        await common.ensure_folder(client, visual_path)
        visual_specs = {
            "parts": ("day2", "fyf-p185-hvac-parts.jpg"),
            "model": ("day2", "fyf-p186-field-note-model.jpg"),
            "ticket1": ("day2", "hvac-ticket-1.jpg"),
            "ticket2": ("day2", "hvac-ticket-2.jpg"),
            "ticket3": ("day2", "hvac-ticket-3.jpg"),
            "ticket4": ("day2", "hvac-ticket-4.jpg"),
            "plumbing_roles": ("day5", "fyf-p194-plumbing-response.jpg"),
            "plumbing_plan": ("day5", "fyf-p195-plumbing-plan.jpg"),
        }
        visuals = {key: await common.upload(client, ASSETS / folder / name, visual_path) for key, (folder, name) in visual_specs.items()}

        attachments = {1: "CAREER", 2: "HVAC", 3: "CLASSIFY", 4: "ROUTES", 5: "WATER"}
        descriptions = {
            1: "Annotate or upload the fixed career/preparation record, type labeled responses, or use paper.",
            2: "Use FYF pp. 187–190 with the safer field labels, or use this enlarged fallback. Complete four evidence-first HVAC notes and one transfer response. Do not complete both surfaces, diagnose, or perform a real check or repair.",
            3: "Complete Major 1 Part A with the fixed May 2024 U.S. evidence and classroom comparison rule. Submit it here once or use the labeled paper route; your teacher will score it with the Day 5 individual response, so do not copy it into a second packet.",
            4: "Compare two fixed route cards and sequence future verification/enrollment steps. Do not submit a real application.",
            5: "This is the single Major 1 gradebook entry. Submit the individual fictional-response companion and complete a 30–45 second live, teacher-conference, private audio/video, or accommodation-aligned oral/AAC briefing. A written plan or transcript may support access but does not by itself demonstrate d(4)(C). Your teacher also scores the Day 3 classification where it was already submitted or turned in; do not resubmit it here.",
        }
        assignments = {}
        for day in range(1, 5):
            assignments[day] = await common.upsert_assignment(
                client,
                ASSIGNMENT_TITLES[day],
                f"<p>{descriptions[day]}</p>",
                ["student_annotation", "online_upload", "online_text_entry"],
                files[attachments[day]]["id"],
            )
        assignments[5] = await require_major_assignment(
            client,
            f"<p>{descriptions[5]}</p>",
            files["WATER"]["id"],
        )
        urls = {day: f"/courses/{COURSE_ID}/assignments/{assignment['id']}" for day, assignment in assignments.items()}

        student = student_content(files, visuals, urls)
        teacher = teacher_content(files)
        day_names = {1: "Four Skilled-Trades Careers", 2: "HVAC Evidence-First Field Notes", 3: "Classify Four Skilled-Trades Careers", 4: "Current Entry Routes", 5: "Fictional Water-Line Response"}
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await prior.upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 5SW Wk4 Day {day} - {day_names[day]}"
            student_page = await common.upsert_page(
                client,
                student_title,
                common.render(
                    "5sw-wk4-student.html",
                    {"COURSE_ID": COURSE_ID, "DAY": day, **CONTRACTS[day], **student[day]},
                ),
            )
            teacher_title = f"TEACHER: 5SW Wk4 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(
                client,
                teacher_title,
                common.render(
                    "5sw-wk4-teacher.html",
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
            await prior.upsert_item(client, module["id"], "Assignment", assignments[day]["id"], ASSIGNMENT_TITLES[day])
            order.extend([("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title), ("Assignment", assignments[day]["id"], ASSIGNMENT_TITLES[day])])
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
            raise RuntimeError(f"Expected {len(order)} Week 4 module items; found {len(final_items)}")
        ordered_final = sorted(final_items, key=lambda entry: entry.get("position", 0))
        for position, ((kind, key, _title), entry) in enumerate(zip(order, ordered_final), 1):
            if entry.get("position") != position or not matches_item(entry, kind, key):
                raise RuntimeError(f"Week 4 module order mismatch at position {position}")
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        print(json.dumps({
            "module": {"id": module["id"], "published": module["published"]},
            "assignments": {str(day): {"id": value["id"], "published": value.get("published"), "submission_types": value.get("submission_types")} for day, value in assignments.items()},
            "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
            "files": {key: value["id"] for key, value in files.items()},
            "visuals": {key: value["id"] for key, value in visuals.items()},
            "pages": {str(day): {kind: {"url": value["url"], "published": value["published"]} for kind, value in pair.items()} for day, pair in pages.items()},
            "items": [{"position": item["position"], "type": item["type"], "title": item["title"]} for item in final_items],
        }, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
