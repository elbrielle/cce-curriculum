"""Build the unpublished 4SW Week 4 drone systems module."""

import asyncio
import json
import sys

import httpx

import build_4sw_wk1 as common


COURSE_ID = common.COURSE_ID
ROOT = common.ROOT
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/4sw/wk4"
MODULE_NAME = "4SW Wk4: Drone Systems, Rules, and Iteration"
DESIGN_TITLE = "PRACTICE: Wildlife-Tracking Drone Design"
CAREER_QUIZ_TITLE = "PRACTICE: Label the Career Evidence"
RULE_QUIZ_TITLE = "PRACTICE: Indoor, Outdoor, or Part 107?"
TEST_TITLE = "PRACTICE: Drone Systems Test and Iteration"
BRIEF_TITLE = "DRAFT: Drone Systems Evidence Brief"


async def ensure_module(client):
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    found = next((m for m in modules if m["name"] == MODULE_NAME), None)
    data = {"module[published]": "false"}
    if found:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data=data)
    data["module[name]"] = MODULE_NAME
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


async def upsert_item(client, module_id, kind, key, title):
    items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    found = next((item for item in items if
        (kind == "SubHeader" and item.get("title") == title) or
        (kind == "Page" and item.get("page_url") == key) or
        (kind in ("Assignment", "Quiz") and item.get("content_id") == key)), None)
    if found:
        return await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module_id}/items/{found['id']}", data={"module_item[title]": title})
    data = {"module_item[type]": kind, "module_item[title]": title}
    if kind == "Page":
        data["module_item[page_url]"] = key
    elif kind in ("Assignment", "Quiz"):
        data["module_item[content_id]"] = key
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data=data)


QUIZZES = {
    CAREER_QUIZ_TITLE: [
        ("Q1 - Salary label", "Which label is accurate for $51,940 in the supplied Surveying and Mapping Technicians card?", "May 2024 U.S. national median pay", ["DFW starting salary", "Guaranteed first-year pay", "Hourly wage for every technician"], "Correct. Keep year, geography, and measure with the number.", "The card reports a national median, not a local starting salary."),
        ("Q2 - High wage", "Which comparison supports a high-wage classification in this activity?", "The occupation's May 2024 national median is above the same-source all-occupations median.", ["The career sounds technical.", "One website calls it a good job.", "The occupation uses a drone."], "Correct. The comparison uses the same source, geography, year, and measure.", "Using a drone does not by itself prove high wage."),
        ("Q3 - High demand", "Which evidence is needed for the class high-demand rule?", "Projected growth and annual openings from the dated occupation card", ["A single job advertisement", "The student's career preference", "Whether the work is outdoors"], "Correct. Both trend and openings matter.", "Preference and setting do not establish labor demand."),
    ],
    RULE_QUIZ_TITLE: [
        ("Q1 - Indoor gym", "A microdrone stays inside a closed gym. Which statement is accurate?", "FAA Part 107 does not apply to an indoor-only operation, but campus and model safety rules still apply.", ["Part 107 automatically authorizes it.", "No safety checks apply indoors.", "Calling it educational removes every rule."], "Correct. Federal operating rules and campus safety are separate checks.", "Indoor-only does not mean no safety process."),
        ("Q2 - Outdoor lesson", "A middle-school class plans an outdoor educational flight. What should happen first?", "The school identifies the applicable operating route and obtains required district/campus approval.", ["Fly because every educational flight is automatically exempt.", "Use the indoor checklist as authorization.", "Ask a student to choose the rule."], "Correct. Educational purpose alone does not settle the operating route.", "An indoor checklist cannot authorize an outdoor operation."),
        ("Q3 - Paid inspection", "Which rule is the likely federal starting point for a paid roof inspection?", "Part 107, followed by verification of the operation's current requirements", ["The recreational exception", "No FAA rule because the aircraft is small", "The classroom tabletop route"], "Correct. The operation is work, and the exact details still need verification.", "A paid inspection is not a recreational classroom scenario."),
    ],
}


async def upsert_quiz(client, title, questions):
    quizzes = await common.paged(client, f"/courses/{COURSE_ID}/quizzes")
    found = next((q for q in quizzes if q.get("title") == title), None)
    data = {"quiz[title]": title, "quiz[description]": "<p>Ungraded, retryable practice with immediate feedback. Use the feedback to repair labels or rule decisions before the exit check.</p>", "quiz[quiz_type]": "practice_quiz", "quiz[published]": "false", "quiz[allowed_attempts]": "-1", "quiz[show_correct_answers]": "true", "quiz[shuffle_answers]": "false"}
    endpoint = f"/courses/{COURSE_ID}/quizzes/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes"
    quiz = await common.api(client, "PUT" if found else "POST", endpoint, data=data)
    existing = await common.paged(client, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    for position, (name, prompt, correct, wrong, yes, no) in enumerate(questions, 1):
        prior = next((q for q in existing if q.get("question_name") == name), None)
        payload = {"question": {"question_name": name, "question_text": prompt, "question_type": "multiple_choice_question", "position": position, "points_possible": 1, "correct_comments": yes, "incorrect_comments": no, "answers": [{"answer_text": correct, "answer_weight": 100}] + [{"answer_text": answer, "answer_weight": 0} for answer in wrong]}}
        path = f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{prior['id']}" if prior else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"
        await common.api(client, "PUT" if prior else "POST", path, json=payload)
    return await common.api(client, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


def image_tag(file_id, alt):
    return f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" style="display:block;width:100%;max-width:700px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        module = await ensure_module(client)
        support_path = "course files/CCR Materials/4SW/Wk4"
        support_folder = await common.ensure_folder(client, support_path)
        names = {
            "DESIGN": "4sw-wk4-wildlife-tracking-drone-design.pdf",
            "CAREERS": "4sw-wk4-drone-enabled-occupations.pdf",
            "RULES": "4sw-wk4-drone-operation-decision-readiness.pdf",
            "TEST": "4sw-wk4-drone-systems-test.pdf",
            "BRIEF": "4sw-wk4-drone-systems-evidence-brief.pdf",
            "RUBRIC": "4sw-wk4-drone-systems-evidence-rubric.pdf",
        }
        files = {key: await common.upload(client, ROOT / "docs/resources/worksheets" / name, support_path) for key, name in names.items()}
        selected = {1: ["fyf-protecting-wildlife-requirements.jpg"], 5: ["fyf-drone-engineering-program.jpg"]}
        visuals, visual_folders = {}, {}
        for day, image_names in selected.items():
            folder_path = f"course files/CCR Materials/4SW/Wk4/Day {day} Visuals"
            visual_folders[day] = await common.ensure_folder(client, folder_path)
            visuals[day] = {name: await common.upload(client, ASSETS / f"day{day}" / name, folder_path) for name in image_names}

        quizzes = {title: await upsert_quiz(client, title, questions) for title, questions in QUIZZES.items()}
        design = await common.upsert_assignment(client, DESIGN_TITLE, "<p>Annotate or upload the wildlife-system blueprint, type a labeled response, or use paper. Art quality is not scored.</p>", ["student_annotation", "online_upload", "online_text_entry"], files["DESIGN"]["id"])
        test = await common.upsert_assignment(client, TEST_TITLE, "<p>Submit the systems test log by Canvas annotation, upload, or text. Live indoor microdrone, simulator, and tabletop routes are equal.</p>", ["student_annotation", "online_upload", "online_text_entry"], files["TEST"]["id"])
        brief = await common.upsert_assignment(client, BRIEF_TITLE, "<p>Submit the private evidence brief by upload, text, media, or paper. Keep unpublished and ungraded until the Minor group and 40/60 weighting are verified.</p>", ["online_upload", "online_text_entry", "media_recording"])
        urls = {
            "design": f"/courses/{COURSE_ID}/assignments/{design['id']}",
            "career_quiz": f"/courses/{COURSE_ID}/quizzes/{quizzes[CAREER_QUIZ_TITLE]['id']}",
            "rule_quiz": f"/courses/{COURSE_ID}/quizzes/{quizzes[RULE_QUIZ_TITLE]['id']}",
            "test": f"/courses/{COURSE_ID}/assignments/{test['id']}",
            "brief": f"/courses/{COURSE_ID}/assignments/{brief['id']}",
        }
        media = {
            1: image_tag(visuals[1]["fyf-protecting-wildlife-requirements.jpg"]["id"], "Find Your Future Protecting Wildlife scenario and robot mission requirements"),
            2: "", 3: "", 4: "",
            5: image_tag(visuals[5]["fyf-drone-engineering-program.jpg"]["id"], "Find Your Future programs of study page with Engineering Design and Drone Engineering workbook context"),
        }
        link, step, flow = common.file_link, common.step, common.flow
        student = {
            1: {"TITLE":"Design a Wildlife-Tracking Drone System","PURPOSE":"Turn a fictional conservation need into testable system requirements and a labeled design.","TODAY":"<ul><li>identify needs and constraints;</li><li>write four requirements;</li><li>label six system jobs;</li><li>redesign for a changed mission.</li></ul>","READY":f'<p>Open {link(files["DESIGN"]["id"], "the five-page design packet")} or <a href="{urls["design"]}">the Canvas annotation activity</a>.</p>',"STEPS":step(1,"Read the user need","<p>Separate what the conservationist needs from rain-forest and animal-behavior constraints.</p>")+step(2,"Write requirements","<p>State what flight, data, communication, and wildlife-protection systems must do.</p>")+step(3,"Design and explain","<p>Label six system jobs. Name one assumption and one tradeoff.</p>")+step(4,"Change the mission","<p>For sea turtles at night, keep one component, change one, and cite mission evidence.</p>"),"EXIT":"<p>Name one change, the evidence that requires it, and one occupation that would help.</p>","DONE":"<ul><li>four requirements;</li><li>six labeled system jobs;</li><li>assumption and tradeoff;</li><li>evidence-based redesign;</li><li>occupation connection.</li></ul>","SUPPORT":"<p>requirement = requisito · constraint = restricción · payload = carga útil · tradeoff = ventaja y costo. Each explanation has its own full-width writing area.</p>","FALLBACK":"<p>The embedded scenario and packet are the complete independent route. Canvas annotation, typed labels, upload, and paper are equal.</p>"},
            2: {"TITLE":"Compare Drone-Enabled Occupations","PURPOSE":"Compare three real occupations without turning “uses a drone” into a made-up career category.","TODAY":"<ul><li>compare daily work and preparation;</li><li>keep labels with pay and outlook;</li><li>classify with a published classroom rule;</li><li>name one limitation.</li></ul>","READY":f'<p>Open {link(files["CAREERS"]["id"], "the four-page occupation guide")}. Figures are dated U.S. national BLS evidence, not DFW starting salaries.</p>',"STEPS":step(1,"Compare the work","<p>Read Surveying and Mapping Technician, Cartographer/Photogrammetrist, and Aerospace Engineering and Operations Technologist/Technician.</p>")+step(2,"Apply the class rule","<p>Compare preparation, May 2024 national median pay, 2024-34 growth, and annual openings using the same source.</p>")+step(3,"Keep one limitation","<p>An occupation may use drones without every worker flying one. Local pay and employer demand may differ.</p>")+step(4,"Check the labels",f'<p><a href="{urls["career_quiz"]}">Use the retryable practice Quiz</a> before the exit matrix.</p>'),"EXIT":"<p>Classify all three and recommend which occupation fictional Taylor should investigate first using evidence.</p>","DONE":"<ul><li>three occupation comparisons;</li><li>source/date/geography/measure labels;</li><li>three classifications;</li><li>one limitation;</li><li>source-based recommendation.</li></ul>","SUPPORT":"<p>median = mediana · growth = crecimiento · openings = vacantes anuales · classification = clasificación. Read one occupation card at a time.</p>","FALLBACK":"<p>The fixed cards replace live search and H&amp;L. Do not relabel a national median as local or entry pay.</p>"},
            3: {"TITLE":"Decide Which Drone Rule Applies","PURPOSE":"Separate federal operating rules from campus and model-specific safety approval.","TODAY":"<ul><li>compare indoor, outdoor educational, and paid work;</li><li>sequence current Remote Pilot requirements;</li><li>complete a readiness gate;</li><li>apply the decision process.</li></ul>","READY":f'<p>Open {link(files["RULES"]["id"], "the five-page Decision and Readiness guide")}. This is decision practice, not flight authorization.</p>',"STEPS":step(1,"Classify three situations","<p>Indoor-only, outdoor educational, and paid inspection do not use one automatic rule.</p>")+step(2,"Read the current sequence","<p>Age, English, condition, test, application/TSA vetting, and recurring training are separate requirements.</p>")+step(3,"Use the readiness gate","<p>Choose live indoor microdrone, simulator, or tabletop only after the appropriate checks.</p>")+step(4,"Repair a decision",f'<p><a href="{urls["rule_quiz"]}">Complete the retryable rule Quiz</a>, then explain why an indoor checklist cannot authorize an outdoor flight.</p>'),"EXIT":"<p>Name the first rule or source for three scenarios and one campus/model check that still matters.</p>","DONE":"<ul><li>three rule decisions;</li><li>current certificate sequence;</li><li>readiness gate;</li><li>new-scenario decision;</li><li>authorized source named.</li></ul>","SUPPORT":"<p>indoor only = solo interior · operating route = vía legal de operación · authorization = autorización · verify = verificar.</p>","FALLBACK":"<p>No live aircraft is required. Simulator and tabletop decision routes are equal. Outdoor student flight is not part of this lesson.</p>"},
            4: {"TITLE":"Test and Improve an Inspection System","PURPOSE":"Run controlled trials, change one variable, and use evidence to choose a next test.","TODAY":"<ul><li>select an equal test route;</li><li>complete three trials or two plus a written third;</li><li>record breakdowns and revisions;</li><li>connect one skill to two occupations.</li></ul>","READY":f'<p>Open {link(files["TEST"]["id"], "the five-page Test and Iteration log")} or <a href="{urls["test"]}">the Canvas activity</a>. Live indoor microdrone, simulator, and tabletop routes use the same evidence.</p>',"STEPS":step(1,"Set the mission","<p>Inspect a marked panel, stay inside the boundary, and return one usable observation.</p>")+step(2,"Test one variable","<p>Run, log the result and limitation, then change only one main variable.</p>")+step(3,"Choose the next action","<p>Use run-log evidence to decide whether to run again or investigate blurry evidence.</p>")+step(4,"Write individually","<p>State the revision, expected evidence, and how one transferable skill appears in two occupations.</p>"),"EXIT":"<p>Compare a fast rerun with pausing to investigate. Choose one and cite the log.</p>","DONE":"<ul><li>three trials or two plus written third;</li><li>one variable at a time;</li><li>result and limitation each trial;</li><li>individual next-test note;</li><li>two-occupation skill connection.</li></ul>","SUPPORT":"<p>trial = prueba · variable = variable · breakdown = falla · evidence = evidencia. Operator, spotter, logger, and communication checker are equal roles.</p>","FALLBACK":"<p>No student is graded on flight, speed, hardware, speaking, or art. If live flight is not teacher-cleared, move directly to simulator or tabletop.</p>"},
            5: {"TITLE":"Drone Systems Evidence Brief","PURPOSE":"Synthesize design, occupation, rule, and test evidence into one accurate private brief.","TODAY":"<ul><li>reopen Days 1-4 evidence;</li><li>write four evidence sections;</li><li>self-score and revise;</li><li>submit privately.</li></ul>","READY":f'<p>Open {link(files["BRIEF"]["id"], "the six-page Evidence Brief")} and {link(files["RUBRIC"]["id"], "the two-page 16-point rubric")}.</p>',"STEPS":step(1,"Design reasoning","<p>Connect a user need to a system response and explain one constraint or tradeoff.</p>")+step(2,"Occupation and classification","<p>Use an exact occupation title and keep source/date/geography/measure with the evidence.</p>")+step(3,"Rule and iteration","<p>Make one bounded rule/safety decision and one test-based revision.</p>")+step(4,"Audit and submit",f'<p>Remove or correct one unsupported claim, revise the weakest section, then <a href="{urls["brief"]}">submit privately</a>.</p>'),"EXIT":"<p>List three accurate source/rule labels, two occupations connected by one skill, and one claim you corrected.</p>","DONE":"<ul><li>all four brief sections;</li><li>accurate labels;</li><li>classification limitation;</li><li>test-based revision;</li><li>self-score and visible revision;</li><li>private submission.</li></ul>","SUPPORT":"<p>synthesize = integrar · accurate = preciso · limitation = limitación · revise = revisar. Text, speech-to-text, media, and paper answer the same evidence jobs.</p>","FALLBACK":"<p>Missing flight evidence uses the tabletop model log. H&amp;L is optional. Canvas failure means paper or later upload without penalty.</p>"},
        }
        teacher = {
            1: {"TITLE":"Design a Wildlife-Tracking Drone System","SUBTITLE":"50 minutes · TEKS d(1)(B), d(1)(C)","ALERT":"<strong>Engineering design, not a flight lesson.</strong> The conservation problem is fictional, and students are not asked to collect real animal, location, or environmental data.","PREP":f'<ul><li>Post {link(files["DESIGN"]["id"], "the design packet")} and annotation activity.</li><li>Project the embedded FYF pp. 104-105 scenario.</li><li>Prepare one labeled system model.</li></ul>',"EVIDENCE":"<p>Four requirements, six labeled system jobs, assumption, tradeoff, changed-mission redesign, and occupation connection. Formative.</p>","FLOW":flow("#5a2d91","Launch · 5","User, need, and constraint.")+flow("#4a9d2f","Workbook scenario · 8","Wildlife problem and requirements.")+flow("#1f617a","System model · 7","Six component jobs.")+flow("#e3ad19","Design · 20","Blueprint and explanation.")+flow("#4a9d2f","Changed mission · 5","Sea-turtle redesign.")+flow("#1f617a","Exit · 5","Change, evidence, occupation."),"MONITOR":"<p>Require measurable system jobs, not decorative labels. Strong tradeoffs name both the advantage and the cost. Score reasoning, not drawing quality.</p>","RESOURCES":"<p>Licensed FYF supplies the fictional Protecting Wildlife problem. The CCE packet adds system boundaries and the independent changed-mission check.</p>","SUPPORT":"<p>Model need versus requirement. Allow labeled list, drawing, typed response, speech-to-text, or annotation. The packet gives a full page to the blueprint.</p>","FALLBACK":"<p>No platform or drone is required. Annotation, upload, text, and paper are equal.</p>"},
            2: {"TITLE":"Compare Drone-Enabled Occupations","SUBTITLE":"50 minutes · TEKS d(1)(D), d(2)(A), d(5)(B)","ALERT":"<strong>Use one evidence basis.</strong> All pay is May 2024 U.S. national median; all outlook is 2024-34 BLS. Do not call these DFW or starting figures.","PREP":f'<ul><li>Post {link(files["CAREERS"]["id"], "the occupation guide")}.</li><li>Open the unpublished practice Quiz.</li><li>Keep live H&amp;L optional.</li></ul>',"EVIDENCE":"<p>Three occupation comparisons, same-source classifications, limitation, and source-based recommendation. Formative.</p>","FLOW":flow("#5a2d91","Warm-up · 5","Job title versus tool.")+flow("#4a9d2f","Evidence cards · 12","Work and preparation.")+flow("#1f617a","Classify · 18","Skill, wage, demand.")+flow("#e3ad19","Recommend · 10","Evidence and limitation.")+flow("#1f617a","Practice/exit · 5","Repair labels."),"MONITOR":"<p>Reference values: Surveying/Mapping Tech $51,940, 5%, 7,600 openings; Cartographer/Photogrammetrist $78,380, 6%, 1,000; Aerospace Engineering/Operations Tech $79,830, 8%, 900. All-occupations comparison: $49,500 median and 3% growth.</p>","RESOURCES":'<p><a href="https://www.bls.gov/ooh/architecture-and-engineering/surveying-and-mapping-technicians.htm">BLS Surveying/Mapping</a> · <a href="https://www.bls.gov/ooh/architecture-and-engineering/cartographers-and-photogrammetrists.htm">BLS Cartographers</a> · <a href="https://www.bls.gov/ooh/architecture-and-engineering/aerospace-engineering-and-operations-technicians.htm">BLS Aerospace Technologists/Technicians</a></p>',"SUPPORT":"<p>Chunk one occupation at a time. The fixed cards keep source labels beside each number and provide separate explanation space.</p>","FALLBACK":"<p>No open search is required. H&amp;L remains supplemental and cannot replace the fixed classification evidence.</p>"},
            3: {"TITLE":"Decide Which Drone Rule Applies","SUBTITLE":"50 minutes · TEKS d(2)(A)","ALERT":"<strong>No outdoor student flight.</strong> This lesson practices decisions. Indoor-only operations still require campus and model approval; an indoor checklist never authorizes outdoor operation.","PREP":f'<ul><li>Post {link(files["RULES"]["id"], "the Decision and Readiness guide")}.</li><li>Open current FAA source pages and the unpublished practice Quiz.</li><li>Select live indoor, simulator, or tabletop route before class.</li></ul>',"EVIDENCE":"<p>Three rule decisions, current Remote Pilot sequence, readiness gate, and applied decision. Formative.</p>","FLOW":flow("#5a2d91","Warm-up · 5","Federal rule versus campus rule.")+flow("#4a9d2f","Three situations · 12","Indoor, outdoor educational, paid work.")+flow("#1f617a","Certificate · 10","Current requirements and recurrence.")+flow("#e3ad19","Readiness/apply · 18","Campus gate and new scenario.")+flow("#1f617a","Exit · 5","Rule, source, safety check."),"MONITOR":"<p>Key: indoor-only—Part 107 does not apply, campus/model rules remain; outdoor school lesson—verify a legal operating route and district approval; paid roof inspection—Part 107 is the likely starting point. Do not present the guide as authorization.</p>","RESOURCES":'<p><a href="https://www.faa.gov/faq/do-faa-rules-and-regulations-apply-commercial-uas-or-drone-operations-conducted-indoors-only">FAA indoor FAQ</a> · <a href="https://www.faa.gov/uas/educational_users">Educational Users</a> · <a href="https://www.faa.gov/uas/commercial_operators/become_a_drone_pilot">Remote Pilot Certificate</a> · <a href="https://www.faa.gov/newsroom/small-unmanned-aircraft-systems-uas-regulations-part-107">Part 107</a></p>',"SUPPORT":"<p>Use the decision sequence: location, purpose, organization/route, current source, campus/model approval. Students may type or dictate.</p>","FALLBACK":"<p>Simulator and tabletop are equal. Live indoor flight only after campus/model SOP, teacher authorization/training, equipment inspection, clear zone, and stop procedure.</p>"},
            4: {"TITLE":"Test and Improve an Inspection System","SUBTITLE":"50 minutes · TEKS d(1)(C), d(4)(B)","ALERT":"<strong>Live flight is optional.</strong> Use it only after the Day 3 readiness gate. Do not grade flight, speed, hardware access, speaking, or art.","PREP":f'<ul><li>Post {link(files["TEST"]["id"], "the Test and Iteration log")} and Canvas activity.</li><li>Set up one teacher-cleared route: live indoor microdrone, simulator, or tabletop.</li><li>Mark boundary, target, observation point, and stop procedure.</li></ul>',"EVIDENCE":"<p>Three trials or two plus written third, one-variable revisions, individual next-test note, and skill transfer to two occupations. Formative.</p>","FLOW":flow("#5a2d91","Readiness · 5","Confirm route and stop condition.")+flow("#4a9d2f","Model · 8","Goal, result, breakdown, revision.")+flow("#1f617a","Three trials · 24","Eight minutes each; written third if needed.")+flow("#e3ad19","Individual note · 8","Evidence and next test.")+flow("#1f617a","Exit · 5","Tradeoff decision."),"MONITOR":"<p>Change one main variable. A strong result describes usable evidence, not merely completion time. Stop live operation immediately for boundary, control, equipment, or authorization failure.</p>","RESOURCES":"<p>The classroom inspection is fictional and does not train or certify a real inspection operation. Manufacturer/campus SOP controls the exact hardware route.</p>","SUPPORT":"<p>Operator/mover, spotter, logger, and communication checker are equal. Use the written-model route for absent students or anyone not participating in live operation.</p>","FALLBACK":"<p>If any live-flight check fails, switch immediately to simulator or tabletop. No student penalty and no teacher fabrication or flight outside the 50-minute lesson.</p>"},
            5: {"TITLE":"Drone Systems Evidence Brief","SUBTITLE":"50 minutes · TEKS d(1)(D), d(2)(A), d(4)(B), d(5)(B)","ALERT":"<strong>Minor 2 in the 4SW assessment map.</strong> Keep the Assignment unpublished and ungraded until the Minor group and 40/60 weighting are verified.","PREP":f'<ul><li>Post {link(files["BRIEF"]["id"], "the Evidence Brief")} and {link(files["RUBRIC"]["id"], "the student-visible rubric")}.</li><li>Open the private unpublished Assignment.</li><li>Return or provide model evidence from Days 1-4.</li></ul>',"EVIDENCE":"<p>Private design, occupation/classification, rule/safety, and test/transfer synthesis with self-score and revision. Minor 2, scored with the 16-point rubric and converted to 100 gradebook points.</p>","FLOW":flow("#5a2d91","Warm-up · 5","Fact, inference, unsupported claim.")+flow("#4a9d2f","Showcases · 8","Two evidence moves, no public presentation requirement.")+flow("#1f617a","Reopen evidence · 10","Source and rule labels.")+flow("#e3ad19","Brief · 20","Four sections.")+flow("#1f617a","Audit/submit · 7","Revise weakest section."),"MONITOR":"<p>Suggested conversion after local approval: 15-16 Masters, 13-14 Meets, 12 Approaches, 10-11 Needs Improvement; below 10 follows campus policy. Score evidence and reasoning, not career preference, flight, hardware, speaking, art, H&amp;L, or grammar unless meaning is unclear.</p>","RESOURCES":'<p>Current public Irving CTE information lists <a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte/irving-high-school">Drone Engineering at Irving High</a>. Workbook wording is context; course access and current sequence still require district verification.</p>',"SUPPORT":"<p>The six-page brief separates every reasoning job. Offer text, speech-to-text, teacher scribe, private media, or paper.</p>","FALLBACK":"<p>Use model tabletop evidence when a prior artifact is missing. Canvas failure means paper or later upload without penalty.</p>"},
        }
        day_names = {1:"Wildlife-Tracking System Design", 2:"Drone-Enabled Occupations", 3:"Drone Rules and Readiness", 4:"Systems Test and Iteration", 5:"Drone Systems Evidence Brief"}
        pages, order = {}, []
        for day in range(1, 6):
            header_title = f"Day {day} · {day_names[day]}"
            header = await upsert_item(client, module["id"], "SubHeader", None, header_title)
            order.append(("SubHeader", header["id"], header_title))
            student_title = f"STUDENT: 4SW Wk4 Day {day} - {day_names[day]}"
            student_page = await common.upsert_page(client, student_title, common.render("4sw-wk4-student.html", {"COURSE_ID": COURSE_ID, "DAY": day, "MEDIA": media[day], **student[day]}))
            teacher_title = f"TEACHER: 4SW Wk4 Day {day} Facilitator Guide"
            teacher_page = await common.upsert_page(client, teacher_title, common.render("4sw-wk4-teacher.html", {"COURSE_ID": COURSE_ID, "DAY": day, "STUDENT_PAGE_URL": student_page["url"], **teacher[day]}))
            await upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            order += [("Page", teacher_page["url"], teacher_title), ("Page", student_page["url"], student_title)]
            pages[day] = {"teacher": teacher_page, "student": student_page}
            extras = {1: [("Assignment", design["id"], DESIGN_TITLE)], 2: [("Quiz", quizzes[CAREER_QUIZ_TITLE]["id"], CAREER_QUIZ_TITLE)], 3: [("Quiz", quizzes[RULE_QUIZ_TITLE]["id"], RULE_QUIZ_TITLE)], 4: [("Assignment", test["id"], TEST_TITLE)], 5: [("Assignment", brief["id"], BRIEF_TITLE)]}[day]
            for kind, key, title in extras:
                await upsert_item(client, module["id"], kind, key, title)
                order.append((kind, key, title))
        items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(i for i in items if (kind == "SubHeader" and i.get("id") == key) or (kind == "Page" and i.get("page_url") == key) or (kind in ("Assignment", "Quiz") and i.get("content_id") == key))
            await common.api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}", data={"module_item[position]": position, "module_item[title]": title})
        final_items = await common.paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        module = await common.api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        print(json.dumps({
            "module": {"id": module["id"], "published": module["published"]},
            "quizzes": {title: {"id": quiz["id"], "published": quiz.get("published"), "quiz_type": quiz.get("quiz_type"), "allowed_attempts": quiz.get("allowed_attempts")} for title, quiz in quizzes.items()},
            "assignments": {"design": {"id": design["id"], "published": design.get("published"), "submission_types": design.get("submission_types"), "annotatable_attachment_id": design.get("annotatable_attachment_id")}, "test": {"id": test["id"], "published": test.get("published"), "submission_types": test.get("submission_types"), "annotatable_attachment_id": test.get("annotatable_attachment_id")}, "brief": {"id": brief["id"], "published": brief.get("published"), "submission_types": brief.get("submission_types"), "grading_type": brief.get("grading_type")}},
            "support_folder": {"id": support_folder["id"], "locked": support_folder["locked"]},
            "visual_folders": {str(day): {"id": folder["id"], "locked": folder["locked"]} for day, folder in visual_folders.items()},
            "files": {key: value["id"] for key, value in files.items()},
            "visuals": {str(day): {name: value["id"] for name, value in entries.items()} for day, entries in visuals.items()},
            "pages": {str(day): {kind: {"url": value["url"], "published": value["published"]} for kind, value in pair.items()} for day, pair in pages.items()},
            "items": [{"position": i["position"], "type": i["type"], "title": i["title"]} for i in final_items],
        }, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
