"""Build the unpublished 1SW Week 2 teacher/student Canvas module."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
import httpx

BASE="https://learn.irvingisd.net"; COURSE_ID=98060
MODULE_NAME="1SW Wk2: Code Your Future - Programming Careers in IT"
MODULE_ALIASES={MODULE_NAME}
MAPPED_MINOR_TITLE="MINOR 2: IT Salary Comparison and Career-Fit Reflection"
MINOR_GROUP_NAME="Minor Assessments (40%)"
RUBRIC_NOTE_MARKER='data-cce-rubric-note="cce-advisory-rubric-v1"'
MINOR_SUBMISSION_TYPES={"online_upload","online_text_entry","media_recording"}
ROOT=Path(__file__).resolve().parents[2]; TEMPLATES=Path(__file__).parent/"templates"; ASSETS=ROOT/"cce-curriculum/resources/canvas-licensed/1sw/wk2"

SUPPORT_NAMES={
  "PROGRAMS":"wk2-it-programs-scaffold.pdf","EXAMPLE":"wk2-career-research-web-developer.pdf","SALARY":"wk2-it-salary-comparison.pdf","MODEL":"wk2-it-salary-comparison-model.pdf","SALARY_BI":"wk2-it-salary-comparison-bilingual.pdf","GUIDE":"wk2-bls-data-guide.pdf","FLIP":"wk2-flip-the-failure-scaffold.pdf","RUBRIC":"wk2-salary-hoc-rubric.pdf","CLIPBOARD":"clipboard-roster-grid.pdf","D5":"wk2-day5-it-pathway-decision.pdf",
  "E1":"1sw-wk2-day1-it-cluster-tour-four-irving-programs-of-study.pdf","E2":"1sw-wk2-day2-programming-pathway-deep-dive-software-web-app-game.pdf","E3":"1sw-wk2-day3-powerskill-resilience-it-salary-showdown.pdf","E4":"1sw-wk2-day4-code-org-hour-of-code-day-1.pdf",
}
REQUIRED_VISUALS={
  1:("it-chapter-opener.jpg","irving-it-programs-page-1.png","it-app-exploration.png"),
  2:("it-app-exploration.png",),
  3:("resilience-scenario.jpg","flip-the-failure-chart.jpg"),
  4:(),
  5:("it-app-exploration.png",),
}

def preflight():
    required=[
        *(TEMPLATES/name for name in ("wk2-teacher.html",*(f"wk2-day{day}-student.html" for day in range(1,6)))),
        *(ROOT/("docs/resources/exit-tickets" if name.startswith("1sw-") else "docs/resources/worksheets")/name for name in SUPPORT_NAMES.values()),
        *(ASSETS/f"day{day}"/name for day,names in REQUIRED_VISUALS.items() for name in names),
    ]
    missing=[str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing: raise FileNotFoundError(f"1SW Wk2 preflight missing required files: {missing}")

def preferred_images(folder):
    return sorted(
        path for path in folder.iterdir()
        if path.suffix.lower() in {".png",".jpg",".jpeg"}
        and not (path.suffix.lower()==".png" and (path.with_suffix(".jpg").exists() or path.with_suffix(".jpeg").exists()))
    )

def slugify(v): return re.sub(r"[^a-z0-9]+","-",v.lower().replace("&","and")).strip("-")
async def api(c,m,p,**kw):
    r=await c.request(m,f"{BASE}/api/v1{p}",**kw); r.raise_for_status(); return r.json() if r.content else None
async def paged(c,p,params=None):
    out=[]; url=f"{BASE}/api/v1{p}"; q={"per_page":100,**(params or {})}
    while url:
        r=await c.get(url,params=q); r.raise_for_status(); out+=r.json(); url=r.links.get("next",{}).get("url"); q=None
    return out
async def canvas_preflight(c):
    modules=await paged(c,f"/courses/{COURSE_ID}/modules")
    module_matches=[entry for entry in modules if entry.get("name") in MODULE_ALIASES]
    if len(module_matches)!=1: raise RuntimeError(f"Expected one 1SW Wk2 module across accepted aliases; found {len(module_matches)}")
    module=module_matches[0]
    if module.get("published") is not False: raise RuntimeError("Refusing to modify a published 1SW Wk2 module")
    groups=await paged(c,f"/courses/{COURSE_ID}/assignment_groups")
    group_matches=[entry for entry in groups if entry.get("name")==MINOR_GROUP_NAME]
    if len(group_matches)!=1: raise RuntimeError(f"Expected one {MINOR_GROUP_NAME!r} group; found {len(group_matches)}")
    assignments=await paged(c,f"/courses/{COURSE_ID}/assignments")
    minor_matches=[entry for entry in assignments if entry.get("name")==MAPPED_MINOR_TITLE]
    if len(minor_matches)!=1: raise RuntimeError(f"Expected one mapped assignment {MAPPED_MINOR_TITLE!r}; found {len(minor_matches)}")
    minor=minor_matches[0]; failures=[]
    if minor.get("published") is not False: failures.append("published")
    if float(minor.get("points_possible") or 0)!=100: failures.append("points_possible")
    if minor.get("grading_type")!="points": failures.append("grading_type")
    if minor.get("omit_from_final_grade") is not False: failures.append("omit_from_final_grade")
    if minor.get("assignment_group_id")!=group_matches[0].get("id"): failures.append("assignment_group")
    if set(minor.get("submission_types") or [])!=MINOR_SUBMISSION_TYPES: failures.append("submission_types")
    if RUBRIC_NOTE_MARKER not in (minor.get("description") or ""): failures.append("rubric_marker")
    if failures: raise RuntimeError(f"Mapped Minor preflight failed: {failures}")
    return module,minor,group_matches[0]
async def ensure_module(c,module):
    return await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module['id']}",data={"module[name]":MODULE_NAME,"module[published]":"false"})
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
async def lock_folder_files(c,folder,required_names=()):
    folder=await api(c,"GET",f"/folders/{folder['id']}")
    if not folder.get("locked"):
        folder=await api(c,"PUT",f"/folders/{folder['id']}",data={"locked":"true"})
    if not folder.get("locked"):
        raise ValueError(f"Canvas folder did not remain locked: {folder['id']}")
    existing=await paged(c,f"/folders/{folder['id']}/files")
    for file in existing:
        if not file.get("locked"):
            await api(c,"PUT",f"/files/{file['id']}",data={"locked":"true"})
    folder=await api(c,"GET",f"/folders/{folder['id']}"); verified=await paged(c,f"/folders/{folder['id']}/files")
    names={file.get("display_name") or file.get("filename") for file in verified}
    missing=set(required_names)-names
    unlocked=[]
    for file in verified:
        if file.get("locked") is not True:
            refreshed=await api(c,"GET",f"/files/{file['id']}")
            if refreshed.get("locked") is not True:
                unlocked.append(file.get("display_name") or file.get("filename"))
    if folder.get("locked") is not True or missing or unlocked:
        raise ValueError(f"1SW Wk2 folder invariant failed for {folder['id']}: missing={sorted(missing)} unlocked={unlocked}")
    return folder,verified
async def find_file(c,name):
    files=await paged(c,f"/courses/{COURSE_ID}/files",{"search_term":name}); matches=[f for f in files if f.get("display_name")==name]
    if len(matches)!=1: raise ValueError(f"Expected one Canvas file named {name!r}; found {len(matches)}")
    current=await api(c,"GET",f"/files/{matches[0]['id']}")
    if current.get("locked") is not True: current=await api(c,"PUT",f"/files/{current['id']}",data={"locked":"true"})
    if current.get("locked") is not True: raise ValueError(f"Referenced Canvas file is not locked: {name}")
    return current
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
def item_matches(item,kind,key,title):
    if item.get("type")!=kind: return False
    if kind=="SubHeader": return item.get("title")==title
    if kind=="Page": return item.get("page_url")==key
    return item.get("content_id")==key
async def reconcile_module_items(c,module_id,expected):
    items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); keep=[]
    for kind,key,title in expected:
        matches=[entry for entry in items if item_matches(entry,kind,key,title) and entry.get("id") not in keep]
        if matches: keep.append(matches[0]["id"]); continue
        data={"module_item[type]":kind,"module_item[title]":title,"module_item[published]":"false"}
        if kind=="Page": data["module_item[page_url]"]=key
        elif kind=="Assignment": data["module_item[content_id]"]=key
        created=await api(c,"POST",f"/courses/{COURSE_ID}/modules/{module_id}/items",data=data); keep.append(created["id"])
    for item in items:
        if item["id"] not in keep: await api(c,"DELETE",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}")
    for position,(item_id,(kind,key,title)) in enumerate(zip(keep,expected),start=1):
        await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item_id}",data={"module_item[position]":position,"module_item[title]":title,"module_item[published]":"false"})
    final=sorted(await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"),key=lambda entry:entry.get("position") or 0)
    if len(final)!=16: raise RuntimeError(f"Expected literal 16-item 1SW Wk2 module; found {len(final)}")
    for position,(item,(kind,key,title)) in enumerate(zip(final,expected),start=1):
        if item.get("position")!=position or item.get("title")!=title or item.get("published") is not False or not item_matches(item,kind,key,title):
            raise RuntimeError(f"1SW Wk2 item mismatch at position {position}: {item}")
    return final

def flow(color,title,text): return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0 0 6px;color:{color}">{title}</h4>{text}</div>'

async def main():
    preflight()
    token=sys.stdin.readline().strip()
    if not token: raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"},timeout=120) as c:
        existing_module,mapped_minor,minor_group=await canvas_preflight(c)
        module=await ensure_module(c,existing_module); module_id=module["id"]
        support_folder="course files/CCR Materials/1SW/Wk2"; support_folder_info=await ensure_folder(c,support_folder); files={}
        for key,name in SUPPORT_NAMES.items():
            source_dir=ROOT/"docs/resources/exit-tickets" if name.startswith("1sw-") else ROOT/"docs/resources/worksheets"
            files[key]=await upload(c,source_dir/name,support_folder)
        support_folder_info,support_folder_files=await lock_folder_files(c,support_folder_info,SUPPORT_NAMES.values())
        files["XELLO"]=await find_file(c,"personality-styles.pdf")
        uploads={}; folders={}; folder_files={}
        for day in range(1,6):
            folder_path=f"course files/CCR Materials/1SW/Wk2/Day {day} Visuals"; folders[day]=await ensure_folder(c,folder_path); uploads[day]={}
            day_dir=ASSETS/f"day{day}"; day_images=preferred_images(day_dir) if day_dir.exists() else []
            for path in day_images: uploads[day][path.name]=await upload(c,path,folder_path)
            folders[day],folder_files[day]=await lock_folder_files(c,folders[day],(path.name for path in day_images))
        student_values={
          1:{"OPENER_IMAGE_ID":uploads[1]["it-chapter-opener.jpg"]["id"],"DISTRICT1_IMAGE_ID":uploads[1]["irving-it-programs-page-1.png"]["id"],"APP_IMAGE_ID":uploads[1]["it-app-exploration.png"]["id"],"PROGRAMS_FILE_ID":files["PROGRAMS"]["id"],"EXIT_FILE_ID":files["E1"]["id"]},
          2:{"APP_IMAGE_ID":uploads[2]["it-app-exploration.png"]["id"],"SALARY_FILE_ID":files["SALARY"]["id"],"EXAMPLE_FILE_ID":files["EXAMPLE"]["id"],"EXIT_FILE_ID":files["E2"]["id"]},
          3:{"SCENARIO_IMAGE_ID":uploads[3]["resilience-scenario.jpg"]["id"],"CHART_IMAGE_ID":uploads[3]["flip-the-failure-chart.jpg"]["id"],"FLIP_FILE_ID":files["FLIP"]["id"],"SALARY_FILE_ID":files["SALARY"]["id"],"MODEL_FILE_ID":files["MODEL"]["id"],"GUIDE_FILE_ID":files["GUIDE"]["id"],"BILINGUAL_FILE_ID":files["SALARY_BI"]["id"],"EXIT_FILE_ID":files["E3"]["id"]},
          4:{"EXIT_FILE_ID":files["E4"]["id"]},
          5:{"APP_IMAGE_ID":uploads[5]["it-app-exploration.png"]["id"],"RUBRIC_FILE_ID":files["RUBRIC"]["id"],"EXIT_FILE_ID":files["D5"]["id"]}}
        student_titles={1:"STUDENT: 1SW Wk2 Day 1 - Map the IT Cluster",2:"STUDENT: 1SW Wk2 Day 2 - Compare Programming Careers",3:"STUDENT: 1SW Wk2 Day 3 - Resilience and Salary Showdown",4:"STUDENT: 1SW Wk2 Day 4 - Test a Programming Concept",5:"STUDENT: 1SW Wk2 Day 5 - Personality Style and IT Decision"}
        contracts={
          1:{"TOPIC":"IT Career Cluster","OBJECTIVE":"Students will explore and describe the CTE career clusters and identify career opportunities within one or more career clusters using workbook and H&amp;L evidence.","TEKS":"d(1)(B), d(1)(C)","DOL":"Stop-and-Jot notes, one IT program selected for further exploration, and the Programming/Cybersecurity Venn diagram."},
          2:{"TOPIC":"Programming Careers","OBJECTIVE":"Students will identify programming career opportunities and research the work and preparation for three careers using Hats &amp; Ladders or Xello (the district-localized app figure).","TEKS":"d(1)(C), d(2)(A)","DOL":"Lightweight four-Hat notes, the Day 2 app-evidence sections on pages 1-3 of the salary packet, and a supported hiring decision."},
          3:{"TOPIC":"Resilience and Labor-Market Evidence","OBJECTIVE":"Students will plan a specific response to a failed technology test and analyze labor-market evidence for three IT careers without mixing unlike salary measures.","TEKS":"d(1)(C), d(5)(A), d(5)(E)","DOL":"Four-row Flip the Failure chart, pages 1-4 of the three-career salary packet, and one claim supported by a labeled number."},
          4:{"TOPIC":"Programming Concepts","OBJECTIVE":"Students will identify how a sequence, loop, or conditional controls program behavior and connect the concept to a programming career task.","TEKS":"d(1)(C)","DOL":"One working or correctly traced programming example plus a concept-and-career explanation."},
          5:{"TOPIC":"Career Fit","OBJECTIVE":"Students will analyze one Personality Style result and use career evidence to make an Information Technology fit decision.","TEKS":"d(1)(A), d(1)(C), d(5)(A), d(5)(E)","DOL":"Five-page IT Salary Comparison and Career Fit Reflection packet submitted as Minor 2; when Xello is accessible, Personality Style is complete and three researched careers are saved for next week's Grade 7 lesson."}}
        teacher_data={
          1:{
            "TITLE":"IT Cluster Tour + Four Irving Programs","SUBTITLE":"50 minutes · TEKS d(1)(B), d(1)(C)",
            "ALERT":"<strong>Preflight H&amp;L from one student Chromebook.</strong> Confirm the IT tour, Game Time, and Hat profiles. If the route fails, the embedded workbook pages and support sheet carry the complete written lesson.",
            "PREP":f'<ul><li>Open FYF pp. 23 and 36-38 and the coordinated Student Guide.</li><li>Test H&amp;L once through the student filter.</li><li>Post the two Stop-and-Jot prompts. No teacher-created model is needed.</li></ul>',
            "LOGISTICS":f'<ul><li><strong>Devices:</strong> 1 Chromebook per student; 1 projector for the opener and program page.</li><li><strong>Grouping:</strong> individual notebook/workbook evidence; one assigned elbow partner for two 30-second turns.</li><li><strong>Print:</strong> 1 <a href="/courses/{COURSE_ID}/files/{files["E1"]["id"]}/preview">exit ticket</a> per enrolled student plus 2 spares. Print the <a href="/courses/{COURSE_ID}/files/{files["PROGRAMS"]["id"]}/preview">programs/Stop-and-Jot scaffold</a> only for students who need enlarged or structured notes.</li></ul>',
            "EVIDENCE":"<p>Collect one new career and one question, fit/not-fit reasons, three Hat ratings, one selected IT program, and the Venn comparison. All work is formative; do not make a separate grade from this exit ticket.</p>",
            "FLOW":(
              flow("#5a2d91","Minutes 0-5 - Welcome and phone app warm-up",'''<p>Welcome students to class and project the daily warm-up question while students take their seats.</p><ul><li>Ask, <em>“Every app on your phone was built by someone. Pick ONE app you use every day and guess: How many people do you think it took to build it from scratch?”</em></li><li>Collect two or three quick estimates from the room. Most students will guess 5 to 20 people.</li><li>Reveal the industry reality: a major app requires hundreds of specialized professionals—designers, front-end and back-end developers, security analysts, and quality assurance testers.</li><li>Bridge with, <em>“Today we meet the entire IT cluster. Every one of those career roles lives right here in Irving ISD.”</em></li></ul>''')+
              flow("#4a9d2f","Minutes 5-17 - Explore the IT cluster and Irving programs of study",'''<p>Open FYF p. 23 and read the chapter opener together to frame how Information Technology powers modern society.</p><ul><li>Read the three opener Hats aloud: <strong>DevOps Engineer</strong>, <strong>Information Security Analyst</strong>, and <strong>Robot Personality Designer</strong>. Ask students which area of IT each role belongs to and why.</li><li>Project the <strong>Be the Decision Maker</strong> scenario (FYF p. 23): a critical security vulnerability is detected in an app with millions of active users.</li><li>Facilitate a structured Think-Pair-Share: 30 seconds of silent thinking, Partner A speaks for 30 seconds, then Partner B speaks for 30 seconds.</li><li>Ask, <em>“If a company quietly fixes a bug without alerting anyone, who bears the risk? What happens if they shut the app down immediately?”</em> Listen for students who weigh customer privacy against business downtime.</li><li>Project Irving ISD's four IT programs of study (FYF p. 36): (1) Computer Science, (2) Programming &amp; Software Development, (3) Technology Support, and (4) Cybersecurity. Explain that Week 2 focuses directly on Programming.</li></ul>''')+
              flow("#1f617a","Minutes 17-40 - H&L IT cluster exploration and Stop and Jot",'''<p>Direct students to ClassLink, open Hats &amp; Ladders, and navigate to the Information Technology cluster.</p><ul><li>Students watch the IT Cluster Tour video and complete two Stop and Jot pauses in their workbook margin: <strong>Stop 1:</strong> one new IT career never heard of before; <strong>Stop 2:</strong> one question about IT careers.</li><li>Students play Game Time, then browse Hat profiles to identify one Hat that fits their personality and one Hat that does NOT feel like a fit.</li><li>Require students to write an evidence-based job-task reason for both fit choices rather than just stating a career name.</li><li>Students rate at least 3 Hats and jot summary impressions.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 22): Confirm all students have successfully launched the IT cluster tour video.<br>• Lap 2 (Minute 30): Verify students have paused to record both Stop and Jot entries in their workbook margin.<br>• Lap 3 (Minute 36): Stop students who are clicking through profiles without reading; ask them to read one job task and education requirement aloud.</li></ul>''')+
              flow("#e3ad19","Minutes 40-47 - Venn diagram comparison DOL",'''<p>Distribute or project the Day 1 Exit Ticket comparing <strong>Programming &amp; Software Development</strong> with <strong>Cybersecurity</strong>.</p><ul><li>Students record two unique characteristics for each program and two shared traits using their workbook notes and H&amp;L exploration.</li><li>Model the comparison frame: <em>“Both programs use coding and technical systems, but Programming focuses on designing and testing software while Cybersecurity focuses on safeguarding networks and data.”</em></li><li>Have students answer the bottom-line prompt: which program of study fits someone who wants to spend the workday writing and debugging code?</li></ul>''')+
              flow("#24323d","Minutes 47-50 - Save, close, and trim point",'''<p>Guide students through dismissal procedures and clean device management.</p><ul><li>Students submit the completed exit ticket, close H&amp;L, and return workbooks to their designated class shelf.</li><li>Check that Chromebooks are plugged into matching charging slots.</li><li><strong>Safe Trim:</strong> If login or video buffering takes longer than anticipated, reduce whole-group sharing from two pairs to one. Protect the three Hat ratings, both fit reasons, and the Venn DOL.</li></ul>''')
            ),
            "MONITOR":"<p><strong>CFU:</strong> students hold up 1-4 fingers as each program is named, then explain one program in a phrase. <strong>Lap target:</strong> one completed career/question jot, then both fit reasons. <strong>Pivot:</strong> if more than one quarter of the class cannot distinguish programming from cybersecurity, reproject the four-program page and sort two job tasks together. <strong>Trim:</strong> take one whole-group share instead of two; do not cut the three Hat ratings or Venn DOL.</p>",
            "SUPPORT":"<p>Point-of-use word banks and complete frames appear beside the security decision and Venn comparison. Read the decision aloud, offer the structured note sheet, and let students rehearse before writing.</p>",
            "FALLBACK":"<p>Use embedded FYF pp. 23 and 36-38 plus the scaffold. Students complete the decision, notes, program selection, and Venn DOL. Log H&amp;L video, game, and rating completion for the next supervised catch-up block.</p>"},
          2:{
            "TITLE":"Programming Pathway Deep-Dive","SUBTITLE":"50 minutes · TEKS d(1)(C), d(2)(A)",
            "ALERT":"<strong>Verify live titles, then preserve them.</strong> If one of the four named Hats differs or is unavailable, students record the exact available programming title. Keep BLS closed today; Day 3 adds the national cross-check to the same packet.",
            "PREP":f'<ul><li>Open H&amp;L Information Technology &gt; Programming and Software Development and verify the available Hats.</li><li>Open the coordinated Student Guide, the five-page salary packet, and the <a href="/courses/{COURSE_ID}/files/{files["EXAMPLE"]["id"]}/preview">Web Developer model</a> only if a student needs help locating a task or preparation detail.</li><li>Keep BLS closed today. Day 3 adds the national cross-check to the same packet.</li></ul>',
            "LOGISTICS":f'<ul><li><strong>Devices:</strong> 1 Chromebook per student.</li><li><strong>Grouping:</strong> all packet evidence is individual; use one elbow partner for a 45-second oral rehearsal before the hiring case.</li><li><strong>Print:</strong> 1 five-page <a href="/courses/{COURSE_ID}/files/{files["SALARY"]["id"]}/preview">salary packet</a> per student (3 sheets if duplex) and 1 <a href="/courses/{COURSE_ID}/files/{files["E2"]["id"]}/preview">exit ticket</a> per student plus 2 spares. Do not print the separate six-field research sheet.</li></ul>',
            "EVIDENCE":"<p>Students keep lightweight four-Hat browse notes, then choose three careers and complete only the Day 2 app-evidence section on pages 1-3 of the salary packet. The mobile-game hiring case is formative. BLS is saved for Day 3.</p>",
            "FLOW":(
              flow("#5a2d91","Minutes 0-4 - Welcome and app creator warm-up",'''<p>Welcome students and project the daily warm-up question as class begins.</p><ul><li>Ask, <em>“If you could create ANY app or video game, what would it be, and who would use it?”</em></li><li>Take two or three quick verbal responses and highlight the real-world utility and creativity behind their ideas.</li><li>Bridge with, <em>“The people who turn those software ideas into functioning reality have specific job titles and training paths. Today you research four of them.”</em></li></ul>''')+
              flow("#4a9d2f","Minutes 4-16 - Browse four programming Hats in H&L",'''<p>Direct students to H&amp;L &gt; Information Technology &gt; Programming and Software Development pathway.</p><ul><li>Introduce the four target careers: <strong>Software Developer</strong>, <strong>Web Developer</strong>, <strong>Mobile App Developer</strong>, and <strong>Game Developer</strong>.</li><li>Students spend approximately 3 minutes per Hat. In their CCE notebook route, they record each exact displayed title and one authentic job task or personal reaction.</li><li>Notice: If a student gravitates immediately to Game Developer, ask, <em>“What does the profile say about entry training and demand compared to Software Developer?”</em> Guide them to evaluate evidence, not just the gaming label.</li><li>Conduct a quick CFU before releasing the packet: project page 1 and have students point to the platform, geography, measure, and date fields.</li></ul>''')+
              flow("#1f617a","Minutes 16-40 - Complete Day 2 app-evidence sections on pages 1-3",'''<p>Students select three careers from their browse and open the five-page IT Salary Comparison packet. Where possible, those three careers should come from the Hats students rated on FYF p. 38 yesterday.</p><ul><li>Students complete ONLY the <strong>Day 2 - Hats &amp; Ladders or Xello career evidence</strong> section on pages 1-3 for their three chosen careers: exact title, platform/date, job task, and common preparation.</li><li>Explicit instruction: <em>“Leave the Day 3 BLS national section completely blank today. We will cross-reference national labor market data tomorrow.”</em></li><li>Provide the preparation word bank: <em>degree, certificate, certification, training, experience, skill</em>, and model the frame: <em>“A [career] commonly prepares by [training/education].”</em></li><li>Refer students needing support to the Web Developer model to distinguish a daily task from preparation requirements.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 22): Confirm every student has chosen three distinct careers and recorded exact displayed titles.<br>• Lap 2 (Minute 30): Check that students are recording specific job tasks rather than generic phrases like 'works on computers.'<br>• Lap 3 (Minute 36): Verify that preparation entries name concrete credentials (e.g. bachelor's degree, coding bootcamp, portfolio).</li></ul>''')+
              flow("#e3ad19","Minutes 40-47 - Mobile game hiring scenario DOL",'''<p>Direct students to the Day 2 Exit Ticket mini-case: an Irving business wants to hire one person to build a reading game for iOS and Android.</p><ul><li>Give students 45 seconds for an oral rehearsal with their elbow partner: <em>“Which of your three researched careers would you hire, and what tool or language would they need?”</em></li><li>Students write their recommendation using evidence from pages 1-3: career name, specific job task reason, and required programming tool or language.</li><li>Model the writing frame: <em>“I recommend a [career] because the project needs someone who can [task]. H&amp;L shows this worker uses [tool].”</em></li></ul>''')+
              flow("#24323d","Minutes 47-50 - Collect, save, and close",'''<p>Close the lesson and secure student research packets for tomorrow's labor cross-check.</p><ul><li>Collect all five-page salary packets into the class tray or digital folder—these will be returned on Day 3.</li><li>Collect the exit tickets and have students log off and dock Chromebooks.</li><li><strong>Safe Trim:</strong> If student browsing runs slow, reduce the browse to three Hats instead of four. Protect the three completed app-evidence packet sections and the hiring scenario DOL.</li></ul>''')
            ),
            "MONITOR":"<p><strong>CFU:</strong> project one packet page; students point to the exact title, platform, geography, measure, figure, and date fields. <strong>Lap target:</strong> page 1 source labels, then pages 2-3 task and preparation. <strong>Pivot:</strong> if more than five students copy a number without its measure or geography, pause and model one label set for the room. <strong>Trim:</strong> browse only three available Hats if access runs long; do not cut the three selected app-evidence records, hiring DOL, or close.</p>",
            "SUPPORT":"<p>The Student Guide places a preparation word bank and complete hiring frame beside the task. Use the Web Developer model only to show where a task or preparation detail lives, then return students to their own packet.</p>",
            "FALLBACK":"<p>Use the verified Web Developer model for one career and any available Hats &amp; Ladders Hat pages for the other two. Complete only the Day 2 sections of pages 1-3 and the hiring case. Record live H&amp;L browsing for supervised catch-up.</p>"},
          3:{
            "TITLE":"Powerskill Resilience + IT Salary Showdown","SUBTITLE":"50 minutes · TEKS d(1)(C), d(5)(A), d(5)(E)",
            "ALERT":"<strong>Keep each measure attached to its label.</strong> Hats &amp; Ladders or Xello supplies the district-localized app figure; BLS supplies a separately labeled national cross-check. A five-page packet is the Minor 2 evidence, not five separate assignments.",
            "PREP":f'<ul><li>Open FYF pp. 26-27, the two fixed BLS pages, and the BLS IT index for each student-selected third career.</li><li>Return each student’s Day 2 salary packet. Open the <a href="/courses/{COURSE_ID}/files/{files["MODEL"]["id"]}/preview">evidence-label model</a> and <a href="/courses/{COURSE_ID}/files/{files["GUIDE"]["id"]}/preview">four-field BLS guide and fixed career card</a>.</li><li>Set one class tray or digital folder for collecting the packet until Day 5.</li></ul>',
            "LOGISTICS":f'<ul><li><strong>Devices:</strong> 1 Chromebook per student; pairs are used only for the two timed Share and Compare turns.</li><li><strong>Print:</strong> no new whole-class packet. Return the packet started on Day 2. Print the scaffold, bilingual headers, or data guide only for students who need them.</li><li><strong>Writing surface:</strong> Flip the Failure stays in the student workbook. Do not print a second chart for the whole class.</li></ul>',
            "EVIDENCE":"<p>Pages 1-4 of the salary packet plus the Day 5 Career Fit Reflection form one 20-point <strong>Minor 2</strong>. The resilience chart is formative. Use the separate matrix exit only when it adds useful evidence; do not require students to copy the same three numbers twice.</p>",
            "FLOW":(
              flow("#5a2d91","Minutes 0-5 - Welcome and resilience warm-up",'''<p>Welcome students and project the daily warm-up prompt.</p><ul><li>Ask, <em>“Think about a time you practiced hard or worked hard on something and it still flopped. What was the very first thing you did right after it happened?”</em></li><li>Collect two quick responses. Highlight unhelpful reactions (blaming, quitting) versus constructive habits (pausing, diagnosing what failed).</li><li>Bridge with, <em>“Today you are the team leader of a cybersecurity team whose security system just failed its big test. Your job is not to feel bad; your job is to lead the bounce-back.”</em></li></ul>''')+
              flow("#4a9d2f","Minutes 5-18 - Powerskill: Flip the Failure",'''<p>Open FYF pp. 26-27 and read the definition of resilience: pausing, analyzing what went wrong, and planning a new approach.</p><ul><li>Read the four failed-test breakdown items aloud: slow alert system, unpatched password, misread test warning, and communication breakdown.</li><li>Model the difference between an unhelpful wish (<em>“work harder”</em>) and an actionable protocol (<em>“schedule automatic weekly software patches”</em>).</li><li>Students complete the four-row <strong>Flip the Failure</strong> chart in their workbook, writing concrete bounce-back ideas and team resilience tips for each failure.</li><li>Run Think-Pair-Share: 30 seconds silent reflection, Partner A reads one row for 30 seconds, Partner B reads a different row for 30 seconds, then partners identify one point of agreement.</li></ul>''')+
              flow("#1f617a","Minutes 18-40 - BLS national cross-check on pages 1-3",'''<p>Return each student's Day 2 salary packet and introduce the Bureau of Labor Statistics (BLS) cross-check.</p><ul><li>Conduct a 60-second prediction: <em>“Do all programming jobs pay the same? Which of your three careers will have the highest national median?”</em> Students record predictions in the margin.</li><li>Project the BLS website and demonstrate where to locate the four critical fields in the Quick Facts box: (1) BLS occupation title, (2) National median pay + data year, (3) Typical entry-level education, and (4) Job outlook percentage + projection years.</li><li>Teach students the crucial distinction: local app starting ranges vs. national median wages. Emphasize: <em>“Median pay is not starting pay, and a national figure is not a local guarantee.”</em></li><li>Students navigate to the BLS pages for Software Developers, Web Developers, and their third chosen career, recording all four fields on pages 1-3.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 24): Confirm students have navigated to official BLS.gov pages, not commercial blog posts.<br>• Lap 2 (Minute 31): Thumbs check on locating entry education and outlook percentages.<br>• Lap 3 (Minute 36): Check that students have labeled 'May 2024 national median' rather than treating it as DFW starting pay.</li></ul>''')+
              flow("#e3ad19","Minutes 40-47 - Salary comparison DOL",'''<p>Direct students to page 4 of the salary packet to evaluate their three careers.</p><ul><li>Students compare the national median pay, required education, and projected job growth across all three careers.</li><li>Prompt: <em>“Which career offers the strongest combination of high pay and fast growth? Does the higher-paying career always require more education?”</em></li><li>Students write their supported comparison claim on page 4 using exact numbers from their chart.</li></ul>''')+
              flow("#24323d","Minutes 47-50 - Collect, save, and close",'''<p>Gather materials and store student evidence.</p><ul><li>Collect the five-page packets back into the class bin; students will use them for the final time on Day 5.</li><li>Collect exit checks and inspect Chromebook return.</li><li><strong>Safe Trim:</strong> Skip the separate standalone matrix exit ticket; page 4 of the packet serves as the complete, authoritative DOL. Protect the four-row resilience chart and BLS cross-check.</li></ul>''')
            ),
            "MONITOR":"<p><strong>CFU:</strong> after each BLS field, thumbs up/side/down for whether students can locate it. <strong>Lap target:</strong> BLS occupation title first, then median/year, education, and outlook percent/years. <strong>Pivot:</strong> if more than one quarter mix annual/hourly, range/median, or outlook percent/years, stop and repair one row with the supplied model. <strong>Trim:</strong> skip the duplicate matrix exit and score page 4 as the DOL; do not add jobs/openings, employer research, or duplicate descriptions.</p>",
            "SUPPORT":"<p>The Student Guide places the resilience and comparison frames beside the writing jobs. Use the prefilled resilience row, evidence model, extraction guide, bilingual headers, and scenario read-aloud only where needed.</p>",
            "FALLBACK":"<p>If a live source fails, use the student's Day 2 app record and the fixed career card inside the BLS guide. Keep the source and date visible. An absent student completes the workbook chart and the same packet without making a separate replacement worksheet.</p>"},
          4:{
            "TITLE":"Programming Concept Lab","SUBTITLE":"50 minutes · TEKS d(1)(C)",
            "ALERT":"<strong>Code.org is supplemental.</strong> The Student Guide now includes a complete delivery-robot trace. A teacher does not need to create block cards, a backup program, accounts, or a Code.org section for this one-period lesson.",
            "PREP":f'<ul><li>If using Code.org, test one no-login tutorial on a student-filtered Chromebook and post that exact route. Do not run a tutorial-choice browse.</li><li>Open the supplied delivery-robot trace in the Student Guide as the default recovery route.</li><li>Choose show-the-teacher or screenshot as the evidence route before class; no separate upload is required.</li></ul>',
            "LOGISTICS":f'<ul><li><strong>Devices:</strong> 1 Chromebook per student. Headphones are optional; run tutorials muted when no class set exists.</li><li><strong>Grouping:</strong> individual evidence with one adjacent coding buddy for questions. Students do not share a login or one graded product.</li><li><strong>Print:</strong> 1 <a href="/courses/{COURSE_ID}/files/{files["E4"]["id"]}/preview">exit ticket</a> per student and 1 <a href="/courses/{COURSE_ID}/files/{files["CLIPBOARD"]["id"]}/preview">monitoring roster</a> per class period. The trace stays in Canvas and may be projected.</li></ul>',
            "EVIDENCE":"<p>Collect one working or correctly traced example plus a specific explanation of sequence, loop, or conditional logic and one connected career task. Tutorial percentage, account status, badge, and certificate are not scored.</p>",
            "FLOW":(
              flow("#5a2d91","Minutes 0-6 - Welcome and coding experience poll",'''<p>Welcome students and project the daily coding launch question.</p><ul><li>Ask, <em>“Raise your hand if you have ever written code on Scratch, Code.org, Roblox Studio, or anywhere else. If yes, what did you create? If no, what do you THINK writing code feels like?”</em></li><li>Take two quick responses from experienced and new coders alike.</li><li>Set the classroom expectation: <em>“Today we test fundamental programming logic. Finishing a vendor tutorial is optional; being able to explain how the code works is your demonstration of learning.”</em></li></ul>''')+
              flow("#4a9d2f","Minutes 6-12 - Trace the delivery-robot model",'''<p>Project the delivery-robot program trace from the Canvas Student Guide on the main screen.</p><ul><li>Walk through the three core concepts: (1) <strong>Sequence</strong> (commands run in order from top to bottom), (2) <strong>Loop</strong> (repeating blocks to eliminate redundant code), and (3) <strong>Conditional</strong> (if/then/else decision logic).</li><li>Have students use finger signals (1 for sequence, 2 for loop, 3 for conditional) as you highlight each block in the delivery-robot code.</li><li>Ask, <em>“Why would a developer use a repeat loop of 3 instead of writing 'move forward' three separate times?”</em> Listen for efficiency, fewer bugs, and cleaner code.</li></ul>''')+
              flow("#1f617a","Minutes 12-40 - Hands-on coding lab and concept explanation",'''<p>Release students to the verified no-login tutorial or the delivery-robot trace in Canvas.</p><ul><li>Set Time, Voice, Body norms: Voice 0 for independent coding, Voice 1 only for a 30-second peer consultation with an adjacent coding buddy.</li><li>Students build through levels or trace program execution, focusing on identifying where sequences, loops, or conditionals occur.</li><li>Students capture one working screenshot or demonstrate their working trace to the teacher.</li><li><strong>Active Monitoring Checkpoints (using Clipboard Roster):</strong><br>• Lap 1 (Minute 18 - Progress Check): Verify every student has launched the tutorial or trace route without login roadblocks.<br>• Lap 2 (Minute 27 - Concept Check): Pause individual students and ask, <em>“What is that block doing? Is it a sequence, a loop, or a conditional? Why did you use it here?”</em><br>• Lap 3 (Minute 34 - Frustration Check): Intervene with students stuck on a level for &gt;3 minutes. Apply the Day 3 resilience habit: <em>“What did you just try? What do you think went wrong? What is one change you can test?”</em></li></ul>''')+
              flow("#e3ad19","Minutes 40-47 - Career connection DOL",'''<p>Direct students to the Day 4 Exit Ticket connecting programming logic to real career tasks.</p><ul><li>Students circle the concept they used most today (sequence, loop, or conditional).</li><li>Students select one career from Day 2's research (e.g. Software Developer, Game Developer) and describe an authentic task where that worker uses that exact concept.</li><li>Model the frame: <em>“A Game Developer uses a loop when the program needs to spawn 50 obstacles without writing 50 separate lines of code.”</em></li></ul>''')+
              flow("#24323d","Minutes 47-50 - Save and close",'''<p>Organize student workspace and equipment return.</p><ul><li>Students save their code or screenshot, close browsers, and submit the exit ticket.</li><li>Collect headphones and ensure Chromebooks are properly stored.</li><li><strong>Safe Trim:</strong> Cut the coding build strictly at Minute 39 regardless of student level progress. Protect the career connection DOL and closing discussion.</li></ul>''')
            ),
            "MONITOR":"<p><strong>CFU:</strong> students show 1 for sequence, 2 for loop, or 3 for conditional as each part of the supplied trace is highlighted. <strong>Lap targets:</strong> route started by minute 11, concept named by minute 25, explanation rehearsed by minute 39. <strong>Pivot:</strong> if more than five students stall on the same level or the site takes more than three minutes to load, move the class to the supplied trace. <strong>Trim:</strong> end the tutorial build at minute 39; never cut the career explanation or three-minute close.</p>",
            "SUPPORT":"<p>The Student Guide places definitions, a worked trace, and complete concept and career frames beside the task. Allow oral rehearsal, speech-to-text, or a teacher-recorded explanation before writing.</p>",
            "FALLBACK":"<p>Use the supplied delivery-robot trace in the Student Guide. Students name the sequence, loop, and conditional, explain the output, and complete the same career exit. No account, site, certificate, or extra handout is required.</p>"},
          5:{
            "TITLE":"Xello Personality Style + IT Pathway Decision","SUBTITLE":"50 minutes · TEKS d(1)(A), d(1)(C), d(5)(A), d(5)(E)",
            "ALERT":"<strong>Protect the Grade 7 Personality Style task and next week's dependency.</strong> Personality Style takes about 20 minutes and requires Matchmaker. Students then save three careers from their completed research so the Grade 7 Learning styles lesson can open. The three saved careers are prerequisite support, not a completion standard or grade.",
            "PREP":f'<ul><li>Check the Xello Completion Standards report and list students whose Matchmaker dependency is missing.</li><li>Open the licensed <a href="/courses/{COURSE_ID}/files/{files["XELLO"]["id"]}/preview">Personality Style teacher resource</a> and prepare one sample result for the written route.</li><li>Return each student’s five-page salary packet, ask students to mark three researched careers, and display the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">Minor 2 rubric</a>.</li></ul>',
            "LOGISTICS":f'<ul><li><strong>Devices:</strong> 1 Chromebook per student; keep the Xello report open on the teacher device.</li><li><strong>Grouping:</strong> Xello results and Minor 2 evidence are individual and private. Navigation help may use an adjacent peer without sharing assessment answers.</li><li><strong>Print:</strong> no new whole-class packet. Return the Day 3 packet. Use the one-page <a href="/courses/{COURSE_ID}/files/{files["D5"]["id"]}/preview">IT Pathway Decision</a> only for a lost-packet, enlarged-print, or catch-up route.</li></ul>',
            "EVIDENCE":"<p><strong>Minor 2:</strong> the five-page IT Salary Comparison and Career Fit Reflection packet, 20 raw rubric points converted to 100 in Canvas. Personality Style completion is checked separately. Three saved careers are a prerequisite-support action for next week's lesson, not another completion standard or grade. The sample-result route completes the Minor evidence when Xello is blocked.</p>",
            "FLOW":(
              flow("#5a2d91","Minutes 0-5 - Welcome and launch Personality Style",'''<p>Welcome students, project the launch agenda, and return their five-page IT salary packets.</p><ul><li>Introduce the day's dual purpose: completing Xello Personality Style and finalizing the Minor 2 Career Fit Reflection.</li><li>Review the prerequisite boundary: <em>“Personality Style requires Matchmaker. If your Matchmaker is incomplete, you will use our teacher sample profile for today's reflection so you can finish your Minor grade without stress.”</em></li><li>Immediately transition any students with login or dependency blocks to the paper sample route.</li></ul>''')+
              flow("#4a9d2f","Minutes 5-25 - Complete Xello Personality Style",'''<p>Direct eligible students to ClassLink &gt; Xello &gt; About Me &gt; Personality Style.</p><ul><li>Students complete the 28-question assessment privately and review their personality style result card.</li><li>Students select ONE trait that resonates with them and record one real-world example from school, home, sports, or hobbies that illustrates that trait.</li><li>Emphasize: <em>“Assessment results are interest patterns and clues, not permanent life labels or grades. A surprising result is an invitation to explore, not a limitation.”</em></li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 10): Ensure students are in Personality Style, not another quiz or free-browsing careers.<br>• Lap 2 (Minute 16): Check completion progress across the room.<br>• Lap 3 (Minute 21): Privately check that each student has identified one trait and drafted a real-life example in their own words.</li></ul>''')+
              flow("#1f617a","Minutes 25-42 - Save three careers & finalize Minor 2 reflection",'''<p>Guide students through prerequisite career saves, then transition to page 5 of the packet.</p><ul><li>Students search for their three researched careers in Xello (Explore Careers) and click 'Save' on each one. Explain that this unlocks next week's Grade 7 Learning Styles lesson.</li><li>Students turn to page 5 of their salary packet: the <strong>Career Fit Reflection</strong>.</li><li>Students complete all four required prompts: (1) the IT pathway rated, (2) one salary or job-growth fact from their research, (3) whether their top career fits their interests, and (4) their final decision on whether they could see themselves working in IT.</li><li>Reinforce: Students may decide IT is NOT a fit and still earn 100% on the Minor if their reasoning cites specific labor evidence and personality traits.</li></ul>''')+
              flow("#e3ad19","Minutes 42-47 - Minor 2 packet audit and submission",'''<p>Students conduct a self-audit of all five packet pages against the Minor 2 rubric before turning it in.</p><ul><li>Page 1: Career 1 complete with app and BLS data.</li><li>Page 2: Career 2 complete with app and BLS data.</li><li>Page 3: Career 3 complete with app and BLS data.</li><li>Page 4: IT Salary Comparison and prediction check.</li><li>Page 5: Complete Career Fit Reflection with evidence.</li><li>Students staple or organize pages 1-5 and submit the completed Minor 2 portfolio.</li></ul>''')+
              flow("#24323d","Minutes 47-50 - Close and weekly wrap-up",'''<p>Facilitate the weekly wrap-up and record any student catch-up needs.</p><ul><li>Log any students who need supervised catch-up for Xello Matchmaker or Personality Style.</li><li>Ask for one closing takeaway: <em>“What was the most surprising thing you learned about Information Technology careers this week?”</em></li><li>Collect all materials and complete device dock checks.</li><li><strong>Safe Trim:</strong> Shorten independent Xello profile browsing. Under no circumstances trim the page 5 reflection, self-audit, or packet submission window.</li></ul>''')
            ),
            "MONITOR":"<p><strong>CFU:</strong> ask students to point to the trait label and example box without sharing private results aloud. <strong>Lap targets:</strong> correct Personality Style task, one trait in the student's own words, then three saved careers that match the research packet. <strong>Pivot:</strong> if more than four students lack Matchmaker or Xello fails, move them to the sample-result page 5 route and record one supervised catch-up roster. <strong>Trim:</strong> shorten career-profile reading, not the Minor reflection or submission.</p>",
            "SUPPORT":"<p>The Student Guide places a fit word bank and complete frame beside page 5. Read result descriptions aloud, allow a student to keep unchosen traits private, and accept oral rehearsal or speech-to-text.</p>",
            "FALLBACK":"<p>Record the Xello issue and complete page 5 with the teacher-supplied sample result and the student's existing career evidence. This completes the Minor 2 route. Add Personality Style and three-career saving to the next supervised catch-up block. Use the one-page decision sheet only if the original packet is unavailable.</p>"}}
        day_headers={1:"Day 1 — Map the IT Cluster",2:"Day 2 — Compare Programming Careers",3:"Day 3 — Resilience and Salary Showdown",4:"Day 4 — Test a Programming Concept",5:"Day 5 — Personality Style and IT Decision"}
        pages={}
        for day in range(1,6):
            st=student_titles[day]; su=slugify(st); student=await upsert_page(c,st,render(f"wk2-day{day}-student.html",{"COURSE_ID":COURSE_ID,**student_values[day]}),su)
            tt=f"TEACHER: 1SW Wk2 Day {day} Facilitator Guide"; tu=slugify(tt); teacher=await upsert_page(c,tt,render("wk2-teacher.html",{"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student["url"],**contracts[day],**teacher_data[day]}),tu)
            pages[day]={"teacher":teacher,"student":student}
        expected=[]
        for day in range(1,6):
            expected.append(("SubHeader",None,day_headers[day]))
            for page_kind in ("teacher","student"):
                page=pages[day][page_kind]
                expected.append(("Page",page["url"],page["title"]))
        expected.append(("Assignment",mapped_minor["id"],MAPPED_MINOR_TITLE))
        final=await reconcile_module_items(c,module_id,expected)
        module=await api(c,"GET",f"/courses/{COURSE_ID}/modules/{module_id}")
        final_minor=await api(c,"GET",f"/courses/{COURSE_ID}/assignments/{mapped_minor['id']}")
        final_pages=[await api(c,"GET",f"/courses/{COURSE_ID}/pages/{page['url']}") for day in range(1,6) for page in pages[day].values()]
        final_failures=[]
        if module.get("published") is not False: final_failures.append("module_published")
        if any(page.get("published") is not False for page in final_pages): final_failures.append("page_published")
        if final_minor.get("published") is not False or float(final_minor.get("points_possible") or 0)!=100 or final_minor.get("grading_type")!="points" or final_minor.get("omit_from_final_grade") is not False: final_failures.append("minor_grading")
        if final_minor.get("assignment_group_id")!=minor_group.get("id") or set(final_minor.get("submission_types") or [])!=MINOR_SUBMISSION_TYPES or RUBRIC_NOTE_MARKER not in (final_minor.get("description") or ""): final_failures.append("minor_identity")
        support_folder_info,support_folder_files=await lock_folder_files(c,support_folder_info,SUPPORT_NAMES.values())
        for day,folder in folders.items():
            day_dir=ASSETS/f"day{day}"; folders[day],folder_files[day]=await lock_folder_files(c,folder,(path.name for path in preferred_images(day_dir)) if day_dir.exists() else ())
        if final_failures: raise RuntimeError(f"1SW Wk2 final invariant failed: {final_failures}")
        print(json.dumps({"module":{"id":module_id,"published":module["published"]},"minor":{"id":final_minor["id"],"published":final_minor.get("published"),"points":final_minor.get("points_possible"),"group":final_minor.get("assignment_group_id"),"grading_type":final_minor.get("grading_type"),"omit_from_final_grade":final_minor.get("omit_from_final_grade")},"support_folder":{"id":support_folder_info["id"],"locked":support_folder_info["locked"],"file_count":len(support_folder_files)},"folders":{str(d):{"id":f["id"],"locked":f["locked"],"file_count":len(folder_files[d])} for d,f in folders.items()},"files":{k:v["id"] for k,v in files.items()},"pages":{str(d):{k:{"url":v["url"],"published":v["published"]} for k,v in p.items()} for d,p in pages.items()},"items":[{"id":i["id"],"position":i["position"],"title":i["title"],"type":i["type"],"page_url":i.get("page_url"),"content_id":i.get("content_id"),"published":i.get("published")} for i in final]},indent=2))

if __name__=="__main__": asyncio.run(main())
