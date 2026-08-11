"""Build the unpublished 1SW Week 2 teacher/student Canvas module."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
import httpx

BASE="https://learn.irvingisd.net"; COURSE_ID=98060
MODULE_NAME="1SW Wk2: Code Your Future - Programming Careers in IT"
ROOT=Path(__file__).resolve().parents[2]; TEMPLATES=Path(__file__).parent/"templates"; ASSETS=ROOT/"cce-curriculum/resources/canvas-licensed/1sw/wk2"

def slugify(v): return re.sub(r"[^a-z0-9]+","-",v.lower().replace("&","and")).strip("-")
async def api(c,m,p,**kw):
    r=await c.request(m,f"{BASE}/api/v1{p}",**kw); r.raise_for_status(); return r.json() if r.content else None
async def paged(c,p,params=None):
    out=[]; url=f"{BASE}/api/v1{p}"; q={"per_page":100,**(params or {})}
    while url:
        r=await c.get(url,params=q); r.raise_for_status(); out+=r.json(); url=r.links.get("next",{}).get("url"); q=None
    return out
async def ensure_module(c):
    modules=await paged(c,f"/courses/{COURSE_ID}/modules"); found=next((m for m in modules if m["name"]==MODULE_NAME),None)
    return found or await api(c,"POST",f"/courses/{COURSE_ID}/modules",data={"module[name]":MODULE_NAME,"module[published]":"false"})
async def ensure_folder(c,path):
    current=""; folder=None
    for name in path.split("/")[1:]:
        target=f"{current}/{name}".strip("/"); enc=httpx.URL("/"+target).raw_path.decode("ascii").lstrip("/")
        r=await c.get(f"{BASE}/api/v1/courses/{COURSE_ID}/folders/by_path/{enc}")
        if r.status_code==200 and r.json(): folder=r.json()[-1]
        else: folder=await api(c,"POST",f"/courses/{COURSE_ID}/folders",data={"name":name,"parent_folder_path":"course files"+(f"/{current}" if current else ""),"locked":"true"})
        current=target
    if folder and not folder.get("locked"): folder=await api(c,"PUT",f"/folders/{folder['id']}",data={"locked":"true"})
    return folder
async def upload(c,path,folder):
    init=await api(c,"POST",f"/courses/{COURSE_ID}/files",data={"name":path.name,"parent_folder_path":folder,"on_duplicate":"overwrite"})
    r=await c.post(init["upload_url"],data=init["upload_params"],files={"file":(path.name,path.read_bytes(),mimetypes.guess_type(path.name)[0] or "application/octet-stream")},follow_redirects=True); r.raise_for_status(); uploaded=r.json()
    if not uploaded.get("locked"):
        uploaded=await api(c,"PUT",f"/files/{uploaded['id']}",data={"locked":"true"})
    if not uploaded.get("locked"):
        raise ValueError(f"Canvas file did not remain locked: {uploaded.get('display_name', path.name)}")
    return uploaded
async def find_file(c,name):
    files=await paged(c,f"/courses/{COURSE_ID}/files",{"search_term":name}); match=next((f for f in files if f.get("display_name")==name),None)
    if not match: raise ValueError(f"Canvas file not found: {name}")
    return match
def render(name,values):
    text=(TEMPLATES/name).read_text()
    for k,v in values.items(): text=text.replace("{{"+k+"}}",str(v))
    unresolved=sorted(set(re.findall(r"\{\{[^}]+\}\}",text)))
    if unresolved: raise ValueError(f"Unresolved values in {name}: {unresolved}")
    return text
async def upsert_page(c,title,body,url):
    data={"wiki_page[title]":title,"wiki_page[body]":body,"wiki_page[published]":"false","wiki_page[editing_roles]":"teachers"}; r=await c.get(f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{url}")
    if r.status_code==200: return await api(c,"PUT",f"/courses/{COURSE_ID}/pages/{url}",data=data)
    if r.status_code!=404: r.raise_for_status()
    return await api(c,"POST",f"/courses/{COURSE_ID}/pages",data=data)
async def upsert_item(c,module_id,kind,key,title,alias=None):
    items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items")
    item=next((i for i in items if (kind=="SubHeader" and i.get("type")=="SubHeader" and i.get("title") in {title,alias}) or (kind=="Page" and i.get("page_url")==key)),None)
    if item: return await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",data={"module_item[title]":title})
    data={"module_item[type]":kind,"module_item[title]":title}
    if kind=="Page": data["module_item[page_url]"]=key
    return await api(c,"POST",f"/courses/{COURSE_ID}/modules/{module_id}/items",data=data)
def flow(color,title,text): return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'

async def main():
    token=sys.stdin.readline().strip()
    if not token: raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"},timeout=120) as c:
        module=await ensure_module(c); module_id=module["id"]
        support_names={
          "PROGRAMS":"wk2-it-programs-scaffold.pdf","EXAMPLE":"wk2-career-research-web-developer.pdf","SALARY":"wk2-it-salary-comparison.pdf","MODEL":"wk2-it-salary-comparison-model.pdf","SALARY_BI":"wk2-it-salary-comparison-bilingual.pdf","GUIDE":"wk2-bls-data-guide.pdf","FLIP":"wk2-flip-the-failure-scaffold.pdf","RUBRIC":"wk2-salary-hoc-rubric.pdf","CLIPBOARD":"clipboard-roster-grid.pdf","D5":"wk2-day5-it-pathway-decision.pdf",
          "E1":"1sw-wk2-day1-it-cluster-tour-four-irving-programs-of-study.pdf","E2":"1sw-wk2-day2-programming-pathway-deep-dive-software-web-app-game.pdf","E3":"1sw-wk2-day3-powerskill-resilience-it-salary-showdown.pdf","E4":"1sw-wk2-day4-code-org-hour-of-code-day-1.pdf"}
        support_folder="course files/CCR Materials/1SW/Wk2"; await ensure_folder(c,support_folder); files={}
        for key,name in support_names.items():
            source_dir=ROOT/"docs/resources/exit-tickets" if name.startswith("1sw-") else ROOT/"docs/resources/worksheets"
            files[key]=await upload(c,source_dir/name,support_folder)
        files["XELLO"]=await find_file(c,"personality-styles.pdf")
        uploads={}; folders={}
        for day in range(1,6):
            folder_path=f"course files/CCR Materials/1SW/Wk2/Day {day} Visuals"; folders[day]=await ensure_folder(c,folder_path); uploads[day]={}
            day_dir=ASSETS/f"day{day}"
            if day_dir.exists():
                for path in sorted(day_dir.glob("*.png")): uploads[day][path.name]=await upload(c,path,folder_path)
        student_values={
          1:{"OPENER_IMAGE_ID":uploads[1]["it-chapter-opener.png"]["id"],"DISTRICT1_IMAGE_ID":uploads[1]["irving-it-programs-page-1.png"]["id"],"APP_IMAGE_ID":uploads[1]["it-app-exploration.png"]["id"],"PROGRAMS_FILE_ID":files["PROGRAMS"]["id"],"EXIT_FILE_ID":files["E1"]["id"]},
          2:{"APP_IMAGE_ID":uploads[2]["it-app-exploration.png"]["id"],"SALARY_FILE_ID":files["SALARY"]["id"],"EXAMPLE_FILE_ID":files["EXAMPLE"]["id"],"EXIT_FILE_ID":files["E2"]["id"]},
          3:{"SCENARIO_IMAGE_ID":uploads[3]["resilience-scenario.png"]["id"],"CHART_IMAGE_ID":uploads[3]["flip-the-failure-chart.png"]["id"],"FLIP_FILE_ID":files["FLIP"]["id"],"SALARY_FILE_ID":files["SALARY"]["id"],"MODEL_FILE_ID":files["MODEL"]["id"],"GUIDE_FILE_ID":files["GUIDE"]["id"],"BILINGUAL_FILE_ID":files["SALARY_BI"]["id"],"EXIT_FILE_ID":files["E3"]["id"]},
          4:{"EXIT_FILE_ID":files["E4"]["id"]},
          5:{"APP_IMAGE_ID":uploads[5]["it-app-exploration.png"]["id"],"RUBRIC_FILE_ID":files["RUBRIC"]["id"],"EXIT_FILE_ID":files["D5"]["id"]}}
        student_titles={1:"STUDENT: 1SW Wk2 Day 1 - Map the IT Cluster",2:"STUDENT: 1SW Wk2 Day 2 - Compare Programming Careers",3:"STUDENT: 1SW Wk2 Day 3 - Resilience and Salary Showdown",4:"STUDENT: 1SW Wk2 Day 4 - Test a Programming Concept",5:"STUDENT: 1SW Wk2 Day 5 - Personality Style and IT Decision"}
        contracts={
          1:{"TOPIC":"IT Career Cluster","OBJECTIVE":"Students will explore and describe the CTE career clusters and identify career opportunities within one or more career clusters using workbook and H&amp;L evidence.","TEKS":"d(1)(B), d(1)(C)","DOL":"Stop-and-Jot notes, one IT program selected for further exploration, and the Programming/Cybersecurity Venn diagram."},
          2:{"TOPIC":"Programming Careers","OBJECTIVE":"Students will identify programming career opportunities and research the work and preparation for three careers using a district HQIM source.","TEKS":"d(1)(C), d(2)(A)","DOL":"Lightweight four-Hat notes, the Day 2 HQIM sections on pages 1-3 of the salary packet, and a supported hiring decision."},
          3:{"TOPIC":"Resilience and Labor-Market Evidence","OBJECTIVE":"Students will plan a specific response to a failed technology test and analyze labor-market evidence for three IT careers without mixing unlike salary measures.","TEKS":"d(1)(C), d(5)(A), d(5)(E)","DOL":"Four-row Flip the Failure chart, pages 1-4 of the three-career salary packet, and one claim supported by a labeled number."},
          4:{"TOPIC":"Programming Concepts","OBJECTIVE":"Students will identify how a sequence, loop, or conditional controls program behavior and connect the concept to a programming career task.","TEKS":"d(1)(C)","DOL":"One working or correctly traced programming example plus a concept-and-career explanation."},
          5:{"TOPIC":"Career Fit","OBJECTIVE":"Students will analyze one Personality Style result and use career evidence to make an Information Technology fit decision.","TEKS":"d(1)(A), d(1)(C), d(5)(A), d(5)(E)","DOL":"Xello Personality Style completion plus the five-page IT Salary Comparison and Career Fit Reflection packet submitted as Minor 2."}}
        teacher_data={
          1:{
            "TITLE":"IT Cluster Tour + Four Irving Programs","SUBTITLE":"50 minutes · TEKS d(1)(B), d(1)(C)",
            "ALERT":"<strong>Preflight H&amp;L from one student Chromebook.</strong> Confirm the IT tour, Game Time, and Hat profiles. If the route fails, the embedded workbook pages and support sheet carry the complete written lesson.",
            "PREP":f'<ul><li>Open FYF pp. 23 and 36-38 and the coordinated Student Guide.</li><li>Test H&amp;L once through the student filter.</li><li>Post the two Stop-and-Jot prompts. No teacher-created model is needed.</li></ul>',
            "LOGISTICS":f'<ul><li><strong>Devices:</strong> 1 Chromebook per student; 1 projector for the opener and program page.</li><li><strong>Grouping:</strong> individual notebook/workbook evidence; one assigned elbow partner for two 30-second turns.</li><li><strong>Print:</strong> 1 <a href="/courses/{COURSE_ID}/files/{files["E1"]["id"]}/preview">exit ticket</a> per enrolled student plus 2 spares. Print the <a href="/courses/{COURSE_ID}/files/{files["PROGRAMS"]["id"]}/preview">programs/Stop-and-Jot scaffold</a> only for students who need enlarged or structured notes.</li></ul>',
            "EVIDENCE":"<p>Collect one new career and one question, fit/not-fit reasons, three Hat ratings, one selected IT program, and the Venn comparison. All work is formative; do not make a separate grade from this exit ticket.</p>",
            "FLOW":flow("#5a2d91","Launch · 5 minutes","App-team estimate and the security decision.")+flow("#4a9d2f","Decision and four programs · 12 minutes","Silent think, two timed partner turns, two shares, then name the four programs.")+flow("#1f617a","H&L exploration · 23 minutes","Tour, two jots, Game Time, fit/not-fit choices, and three Hat ratings.")+flow("#e3ad19","Venn DOL · 7 minutes","Compare Programming & Software Development with Cybersecurity.")+flow("#24323d","Save and close · 3 minutes","Submit the exit ticket, close H&L, and return the workbook to its class location."),
            "MONITOR":"<p><strong>CFU:</strong> students hold up 1-4 fingers as each program is named, then explain one program in a phrase. <strong>Lap target:</strong> one completed career/question jot, then both fit reasons. <strong>Pivot:</strong> if more than one quarter of the class cannot distinguish programming from cybersecurity, reproject the four-program page and sort two job tasks together. <strong>Trim:</strong> take one whole-group share instead of two; do not cut the three Hat ratings or Venn DOL.</p>",
            "SUPPORT":"<p>Point-of-use word banks and complete frames appear beside the security decision and Venn comparison. Read the decision aloud, offer the structured note sheet, and let students rehearse before writing.</p>",
            "FALLBACK":"<p>Use embedded FYF pp. 23 and 36-38 plus the scaffold. Students complete the decision, notes, program selection, and Venn DOL. Log H&amp;L video, game, and rating completion for the next supervised catch-up block.</p>"},
          2:{
            "TITLE":"Programming Pathway Deep-Dive","SUBTITLE":"50 minutes · TEKS d(1)(C), d(2)(A)",
            "ALERT":"<strong>Verify live titles, then preserve them.</strong> If one of the four named Hats differs or is unavailable, students record the exact available programming title. Keep BLS closed today; Day 3 adds the national cross-check to the same packet.",
            "PREP":f'<ul><li>Open H&amp;L Information Technology &gt; Programming and Software Development and verify the available Hats.</li><li>Open the coordinated Student Guide, the five-page salary packet, and the <a href="/courses/{COURSE_ID}/files/{files["EXAMPLE"]["id"]}/preview">Web Developer model</a> only if a student needs help locating a task or preparation detail.</li><li>Keep BLS closed today. Day 3 adds the national cross-check to the same packet.</li></ul>',
            "LOGISTICS":f'<ul><li><strong>Devices:</strong> 1 Chromebook per student.</li><li><strong>Grouping:</strong> all packet evidence is individual; use one elbow partner for a 45-second oral rehearsal before the hiring case.</li><li><strong>Print:</strong> 1 five-page <a href="/courses/{COURSE_ID}/files/{files["SALARY"]["id"]}/preview">salary packet</a> per student (3 sheets if duplex) and 1 <a href="/courses/{COURSE_ID}/files/{files["E2"]["id"]}/preview">exit ticket</a> per student plus 2 spares. Do not print the separate six-field research sheet.</li></ul>',
            "EVIDENCE":"<p>Students keep lightweight four-Hat browse notes, then choose three careers and complete only the Day 2 HQIM section on pages 1-3 of the salary packet. The mobile-game hiring case is formative. BLS is saved for Day 3.</p>",
            "FLOW":flow("#5a2d91","Launch · 4 minutes","Name an app or game and the user it serves.")+flow("#4a9d2f","Four-Hat browse · 12 minutes","About three minutes per Hat: exact title plus one task or reaction.")+flow("#1f617a","Three-career HQIM record · 24 minutes","Choose three careers and complete the Day 2 section on pages 1-3: source labels, one task, and common preparation.")+flow("#e3ad19","Hiring case · 7 minutes","Rehearse, choose the best-fit developer, and support the decision with one task or preparation fact.")+flow("#24323d","Save and close · 3 minutes","Submit the exit and store the packet for Day 3."),
            "MONITOR":"<p><strong>CFU:</strong> project one packet page; students point to the exact title, platform, geography, measure, figure, and date fields. <strong>Lap target:</strong> page 1 source labels, then pages 2-3 task and preparation. <strong>Pivot:</strong> if more than five students copy a number without its measure or geography, pause and model one label set for the room. <strong>Trim:</strong> browse only three available Hats if access runs long; do not cut the three selected HQIM records, hiring DOL, or close.</p>",
            "SUPPORT":"<p>The Student Guide places a preparation word bank and complete hiring frame beside the task. Use the Web Developer model only to show where a task or preparation detail lives, then return students to their own packet.</p>",
            "FALLBACK":"<p>Use the verified Web Developer model for one career and any available HQIM Hat pages for the other two. Complete only the Day 2 sections of pages 1-3 and the hiring case. Record live H&amp;L browsing for supervised catch-up.</p>"},
          3:{
            "TITLE":"Powerskill Resilience + IT Salary Showdown","SUBTITLE":"50 minutes · TEKS d(1)(C), d(5)(A), d(5)(E)",
            "ALERT":"<strong>Keep each measure attached to its label.</strong> H&amp;L or Xello supplies the district HQIM localized figure; BLS supplies a separately labeled national cross-check. A five-page packet is the Minor 2 evidence, not five separate assignments.",
            "PREP":f'<ul><li>Open FYF pp. 26-27, the two fixed BLS pages, and the BLS IT index for each student-selected third career.</li><li>Return each student’s Day 2 salary packet. Open the <a href="/courses/{COURSE_ID}/files/{files["MODEL"]["id"]}/preview">evidence-label model</a> and <a href="/courses/{COURSE_ID}/files/{files["GUIDE"]["id"]}/preview">BLS extraction guide</a>.</li><li>Set one class tray or digital folder for collecting the packet until Day 5.</li></ul>',
            "LOGISTICS":f'<ul><li><strong>Devices:</strong> 1 Chromebook per student; pairs are used only for the two timed Share and Compare turns.</li><li><strong>Print:</strong> no new whole-class packet. Return the packet started on Day 2. Print the scaffold, bilingual headers, or data guide only for students who need them.</li><li><strong>Writing surface:</strong> Flip the Failure stays in the student workbook. Do not print a second chart for the whole class.</li></ul>',
            "EVIDENCE":"<p>Pages 1-4 of the salary packet plus the Day 5 Career Fit Reflection form one 20-point <strong>Minor 2</strong>. The resilience chart is formative. Use the separate matrix exit only when it adds useful evidence; do not require students to copy the same three numbers twice.</p>",
            "FLOW":flow("#5a2d91","Prediction and labels · 5 minutes","Predict highest pay; distinguish localized range from national median.")+flow("#4a9d2f","Flip the Failure · 13 minutes","Four workbook rows, then two timed partner comparisons.")+flow("#1f617a","BLS cross-check · 22 minutes","Add only occupation title, national median/year, entry education, and outlook percent/years to pages 1-3.")+flow("#e3ad19","Comparison DOL · 7 minutes","Use page 4 of the packet for the supported claim; use the separate matrix only if needed.")+flow("#24323d","Collect and close · 3 minutes","Turn pages 1-4 into the class tray or named digital folder for Day 5."),
            "MONITOR":"<p><strong>CFU:</strong> after each BLS field, thumbs up/side/down for whether students can locate it. <strong>Lap target:</strong> BLS occupation title first, then median/year, education, and outlook percent/years. <strong>Pivot:</strong> if more than one quarter mix annual/hourly, range/median, or outlook percent/years, stop and repair one row with the supplied model. <strong>Trim:</strong> skip the duplicate matrix exit and score page 4 as the DOL; do not add jobs/openings, employer research, or duplicate descriptions.</p>",
            "SUPPORT":"<p>The Student Guide places the resilience and comparison frames beside the writing jobs. Use the prefilled resilience row, evidence model, extraction guide, bilingual headers, and scenario read-aloud only where needed.</p>",
            "FALLBACK":"<p>If a live source fails, use the student's Day 2 HQIM record and the fixed BLS pages. Keep the source and date visible. An absent student completes the workbook chart and the same packet without making a separate replacement worksheet.</p>"},
          4:{
            "TITLE":"Programming Concept Lab","SUBTITLE":"50 minutes · TEKS d(1)(C)",
            "ALERT":"<strong>Code.org is supplemental.</strong> The Student Guide now includes a complete delivery-robot trace. A teacher does not need to create block cards, a backup program, accounts, or a Code.org section for this one-period lesson.",
            "PREP":f'<ul><li>If using Code.org, test one no-login tutorial on a student-filtered Chromebook and post that exact route. Do not run a tutorial-choice browse.</li><li>Open the supplied delivery-robot trace in the Student Guide as the default recovery route.</li><li>Choose show-the-teacher or screenshot as the evidence route before class; no separate upload is required.</li></ul>',
            "LOGISTICS":f'<ul><li><strong>Devices:</strong> 1 Chromebook per student. Headphones are optional; run tutorials muted when no class set exists.</li><li><strong>Grouping:</strong> individual evidence with one adjacent coding buddy for questions. Students do not share a login or one graded product.</li><li><strong>Print:</strong> 1 <a href="/courses/{COURSE_ID}/files/{files["E4"]["id"]}/preview">exit ticket</a> per student and 1 <a href="/courses/{COURSE_ID}/files/{files["CLIPBOARD"]["id"]}/preview">monitoring roster</a> per class period. The trace stays in Canvas and may be projected.</li></ul>',
            "EVIDENCE":"<p>Collect one working or correctly traced example plus a specific explanation of sequence, loop, or conditional logic and one connected career task. Tutorial percentage, account status, badge, and certificate are not scored.</p>",
            "FLOW":flow("#5a2d91","Concept launch · 6 minutes","Trace sequence, loop, and conditional in the supplied delivery-robot model.")+flow("#4a9d2f","Route start · 5 minutes","Open the one verified tutorial or remain on the supplied trace.")+flow("#1f617a","Build or trace · 28 minutes","Three fixed laps: progress, concept explanation, and persistence.")+flow("#e3ad19","Career DOL · 8 minutes","Use the complete frame, then connect the concept to one programming career task.")+flow("#24323d","Save and close · 3 minutes","Show or save the evidence, close the site, and submit the exit ticket."),
            "MONITOR":"<p><strong>CFU:</strong> students show 1 for sequence, 2 for loop, or 3 for conditional as each part of the supplied trace is highlighted. <strong>Lap targets:</strong> route started by minute 11, concept named by minute 25, explanation rehearsed by minute 39. <strong>Pivot:</strong> if more than five students stall on the same level or the site takes more than three minutes to load, move the class to the supplied trace. <strong>Trim:</strong> end the tutorial build at minute 39; never cut the career explanation or three-minute close.</p>",
            "SUPPORT":"<p>The Student Guide places definitions, a worked trace, and complete concept and career frames beside the task. Allow oral rehearsal, speech-to-text, or a teacher-recorded explanation before writing.</p>",
            "FALLBACK":"<p>Use the supplied delivery-robot trace in the Student Guide. Students name the sequence, loop, and conditional, explain the output, and complete the same career exit. No account, site, certificate, or extra handout is required.</p>"},
          5:{
            "TITLE":"Xello Personality Style + IT Pathway Decision","SUBTITLE":"50 minutes · TEKS d(1)(A), d(1)(C), d(5)(A), d(5)(E)",
            "ALERT":"<strong>Protect the required Xello spine.</strong> Personality Style takes about 20 minutes and requires Matchmaker. Favorite Clusters belongs later. Page 5 of the existing salary packet is the Minor 2 reflection; do not assign a second whole-class decision sheet.",
            "PREP":f'<ul><li>Check the Xello Completion Standards report and list students whose Matchmaker prerequisite is missing.</li><li>Open the licensed <a href="/courses/{COURSE_ID}/files/{files["XELLO"]["id"]}/preview">Personality Style teacher resource</a>.</li><li>Return each student’s five-page salary packet and display the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">Minor 2 rubric</a>.</li></ul>',
            "LOGISTICS":f'<ul><li><strong>Devices:</strong> 1 Chromebook per student; keep the Xello report open on the teacher device.</li><li><strong>Grouping:</strong> Xello results and Minor 2 evidence are individual and private. Navigation help may use an adjacent peer without sharing assessment answers.</li><li><strong>Print:</strong> no new whole-class packet. Return the Day 3 packet. Use the one-page <a href="/courses/{COURSE_ID}/files/{files["D5"]["id"]}/preview">IT Pathway Decision</a> only for a lost-packet, enlarged-print, or catch-up route.</li></ul>',
            "EVIDENCE":"<p><strong>Minor 2:</strong> the five-page IT Salary Comparison and Career Fit Reflection packet, 20 raw rubric points converted to 100 in Canvas. Xello Personality Style completion is checked in the report. H&amp;L pathway rating is formative.</p>",
            "FLOW":flow("#5a2d91","Launch and prerequisite route · 5 minutes","Open Personality Style; move missing-prerequisite students to written work and the catch-up list.")+flow("#4a9d2f","Xello Personality Style · 20 minutes","Complete, review, and record one chosen trait with a real example.")+flow("#1f617a","H&L pathway check · 10 minutes","Rate one pathway and review two Hats; use the workbook route when the platform fails.")+flow("#e3ad19","Minor reflection · 10 minutes","Complete page 5 using one assessment result and one source-labeled career fact.")+flow("#24323d","Submit and close · 5 minutes","Submit all five pages, verify Xello status, and record any catch-up need."),
            "MONITOR":"<p><strong>CFU:</strong> ask students to point to the trait label and the example box without sharing private results aloud. <strong>Lap targets:</strong> correct Xello task, completion progress, then one trait in the student's own words. <strong>Pivot:</strong> if more than four students lack Matchmaker or Xello fails, move those students to page 5 and record one supervised catch-up roster. <strong>Trim:</strong> omit favoriting and shorten H&amp;L to one pathway plus one Hat; do not cut Xello Personality Style, the reflection, or submission.</p>",
            "SUPPORT":"<p>The Student Guide places a fit word bank and complete frame beside page 5. Read result descriptions aloud, allow a student to keep unchosen traits private, and accept oral rehearsal or speech-to-text.</p>",
            "FALLBACK":"<p>Record the Xello issue, complete page 5 and the workbook pathway check, and add platform completion to the next supervised catch-up block. Use the one-page decision sheet only if the original packet is unavailable.</p>"}}
        day_headers={1:"Day 1 — Map the IT Cluster",2:"Day 2 — Compare Programming Careers",3:"Day 3 — Resilience and Salary Showdown",4:"Day 4 — Test a Programming Concept",5:"Day 5 — Personality Style and IT Decision"}
        pages={}; order=[]
        for day in range(1,6):
            st=student_titles[day]; su=slugify(st); student=await upsert_page(c,st,render(f"wk2-day{day}-student.html",{"COURSE_ID":COURSE_ID,**student_values[day]}),su)
            tt=f"TEACHER: 1SW Wk2 Day {day} Facilitator Guide"; tu=slugify(tt); teacher=await upsert_page(c,tt,render("wk2-teacher.html",{"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student["url"],**contracts[day],**teacher_data[day]}),tu)
            header=await upsert_item(c,module_id,"SubHeader",None,day_headers[day],f"Day {day}")
            teacher_item=await upsert_item(c,module_id,"Page",teacher["url"],tt)
            student_item=await upsert_item(c,module_id,"Page",student["url"],st)
            pages[day]={"teacher":teacher,"student":student}; order.extend([(header["id"],day_headers[day]),(teacher_item["id"],tt),(student_item["id"],st)])
        items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items")
        minor=next((i for i in items if i.get("type")=="Assignment" and i.get("title")=="MINOR 2: IT Salary Comparison and Career-Fit Reflection"),None)
        if minor: order.append((minor["id"],minor["title"]))
        for position,(item_id,title) in reversed(list(enumerate(order,start=1))): await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item_id}",data={"module_item[position]":position,"module_item[title]":title})
        final=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); module=await api(c,"GET",f"/courses/{COURSE_ID}/modules/{module_id}")
        print(json.dumps({"module":{"id":module_id,"published":module["published"]},"folders":{str(d):{"id":f["id"],"locked":f["locked"]} for d,f in folders.items()},"pages":{str(d):{k:{"url":v["url"],"published":v["published"]} for k,v in p.items()} for d,p in pages.items()},"items":[{"id":i["id"],"position":i["position"],"title":i["title"],"page_url":i.get("page_url")} for i in final]},indent=2))

asyncio.run(main())
