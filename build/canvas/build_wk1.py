"""Build the unpublished 1SW Week 1 teacher/student Canvas module."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
import httpx

BASE="https://learn.irvingisd.net"; COURSE_ID=98060
MODULE_NAME="1SW Wk1: Built by Bots - Robotics and Manufacturing Careers"
ROOT=Path(__file__).resolve().parents[2]; TEMPLATES=Path(__file__).parent/"templates"; ASSETS=ROOT/"cce-curriculum/resources/canvas-licensed/1sw/wk1"

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
    r=await c.post(init["upload_url"],data=init["upload_params"],files={"file":(path.name,path.read_bytes(),mimetypes.guess_type(path.name)[0] or "application/octet-stream")},follow_redirects=True); r.raise_for_status(); return r.json()
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
    if r.status_code==200:return await api(c,"PUT",f"/courses/{COURSE_ID}/pages/{url}",data=data)
    if r.status_code!=404:r.raise_for_status()
    return await api(c,"POST",f"/courses/{COURSE_ID}/pages",data=data)
async def upsert_item(c,module_id,page,title):
    items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); item=next((i for i in items if i.get("page_url")==page["url"]),None)
    if item:return await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",data={"module_item[title]":title})
    return await api(c,"POST",f"/courses/{COURSE_ID}/modules/{module_id}/items",data={"module_item[type]":"Page","module_item[page_url]":page["url"],"module_item[title]":title})

def flow(color,title,text): return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'

async def main():
    token=sys.stdin.readline().strip()
    if not token: raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"},timeout=120) as c:
        module=await ensure_module(c); module_id=module["id"]
        support_names={
          "PATHWAYS":"manufacturing-pathways-scaffold.pdf","TECH":"technician-checklist-scaffold.pdf","RESEARCH":"career-research-worksheet.pdf","RESEARCH_EX":"career-research-worksheet-example-welder.pdf","RESEARCH_BI":"career-research-worksheet-bilingual.pdf","RUBRIC":"wk1-presentation-rubric.pdf","CLIPBOARD":"clipboard-roster-grid.pdf",
          "E1":"1sw-wk1-day1-manufacturing-cluster-tour-more-than-assembly-lines.pdf","E2":"1sw-wk1-day2-machine-breakdown-mystery-career-research.pdf","E3":"1sw-wk1-day3-super-sports-manufacturing-design-build-test.pdf","E4":"1sw-wk1-day4-sphero-factory-floor-robots-for-crayons-part-1.pdf","E5":"1sw-wk1-day5-sphero-run-through-robots-for-crayons-presentations-manufacturing-favorites.pdf"}
        support_folder="course files/CCR Materials/1SW/Wk1"; await ensure_folder(c,support_folder)
        files={}
        for key,name in support_names.items():
            source_dir=ROOT/"docs/resources/exit-tickets" if name.startswith("1sw-") else ROOT/"docs/resources/worksheets"
            files[key]=await upload(c,source_dir/name,support_folder)
        uploads={}; folders={}
        for day in range(1,6):
            folder_path=f"course files/CCR Materials/1SW/Wk1/Day {day} Visuals"; folders[day]=await ensure_folder(c,folder_path); uploads[day]={}
            day_dir=ASSETS/f"day{day}"
            for path in sorted(p for p in day_dir.iterdir() if p.suffix.lower() in {".png",".jpg",".jpeg"}):
                if path.suffix.lower()==".png" and (day_dir/f"{path.stem}.jpg").exists(): continue
                uploads[day][path.name]=await upload(c,path,folder_path)
        student_values={
          1:{"OPENER_IMAGE_ID":uploads[1]["manufacturing-chapter-opener.jpg"]["id"],"APP_IMAGE_ID":uploads[1]["manufacturing-app-exploration.png"]["id"],"PATHWAYS_FILE_ID":files["PATHWAYS"]["id"],"EXIT_FILE_ID":files["E1"]["id"]},
          2:{"CHECKLIST_IMAGE_ID":uploads[2]["technician-checklist.png"]["id"],"CLUES_IMAGE_ID":uploads[2]["machine-breakdown-clues.png"]["id"],"TECH_SCAFFOLD_FILE_ID":files["TECH"]["id"],"RESEARCH_FILE_ID":files["RESEARCH"]["id"],"RESEARCH_EXAMPLE_FILE_ID":files["RESEARCH_EX"]["id"],"RESEARCH_BILINGUAL_FILE_ID":files["RESEARCH_BI"]["id"],"EXIT_FILE_ID":files["E2"]["id"]},
          3:{"DESIGN_IMAGE_ID":uploads[3]["bike-rack-design-brief.png"]["id"],"METALS_IMAGE_ID":uploads[3]["metals-and-welding-methods.png"]["id"],"BUILD_IMAGE_ID":uploads[3]["build-and-test-prototype.png"]["id"],"EXIT_FILE_ID":files["E3"]["id"]},
          4:{"PROBLEMS_IMAGE_ID":uploads[4]["robots-for-crayons-problems.png"]["id"],"MACHINES_IMAGE_ID":uploads[4]["how-the-machines-work.png"]["id"],"SHIFT_IMAGE_ID":uploads[4]["shift-notes-and-impact-report.png"]["id"],"EXIT_FILE_ID":files["E4"]["id"]},
          5:{"PLAN_IMAGE_ID":uploads[5]["robots-for-crayons-action-plan.png"]["id"],"RUBRIC_FILE_ID":files["RUBRIC"]["id"],"EXIT_FILE_ID":files["E5"]["id"],"QUALITY_CHECK_IMAGES":"".join(f'<img src="/courses/{COURSE_ID}/files/{uploads[5][f"slide-{n}.png"]["id"]}/preview" alt="Quality Check factory image {n-1} for identifying product, equipment, cleanliness, or safety problems" style="display:block;width:100%;height:auto;margin:12px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{uploads[5][f"slide-{n}.png"]["id"]}" data-api-returntype="File">' for n in range(2,6))}}
        student_titles={1:"STUDENT: 1SW Wk1 Day 1 - Manufacturing Cluster Tour",2:"STUDENT: 1SW Wk1 Day 2 - Machine Breakdown Mystery",3:"STUDENT: 1SW Wk1 Day 3 - Design Build Test",4:"STUDENT: 1SW Wk1 Day 4 - Sphero and Robots for Crayons",5:"STUDENT: 1SW Wk1 Day 5 - Test Solve Present"}
        teacher_data={
          1:{"TITLE":"Manufacturing Cluster Tour","SUBTITLE":"50 minutes - TEKS d(1)(B), d(1)(C)","ALERT":"<strong>Keep the cluster broad.</strong> If every student names Welder, redirect the Hat browse toward automation, mechatronics, electronics, maintenance, and quality careers.","PREP":f'<ul><li>Open workbook pages 199 and 212 and H&amp;L Manufacturing.</li><li>Prepare the <a href="/courses/{COURSE_ID}/files/{files["PATHWAYS"]["id"]}/preview">pathways scaffold</a> and <a href="/courses/{COURSE_ID}/files/{files["E1"]["id"]}/preview">exit ticket</a>.</li><li>Write both Stop-and-Jot prompts before the video starts.</li></ul>',"EVIDENCE":"<p>Collect the notebook entry (two careers, two questions), pathway/Hat ratings, and comparison exit ticket. Minor-grade option: completion plus a specific career-to-personality explanation.</p>","FLOW_TITLE":"50-minute flow","FLOW":flow("#5a2d91","Warm-up - 5 minutes","Trace one morning product through design, production, programming, and quality control.")+flow("#4a9d2f","Chapter opener and pathways - 15 minutes","Read page 199, run the weld-quality dilemma, and compare the six H&L pathways.")+flow("#1f617a","H&L cluster exploration - 20 minutes","Run the two Stop-and-Jot pauses, then require one pathway and three Hat ratings.")+flow("#e3ad19","Share and exit - 10 minutes","Check two careers, two questions, then complete the comparison matrix."),"MONITOR":"<p>Check for a named career at both video pauses, three actual ratings, and training/salary details copied from a Hat rather than guessed. Accept either weld-decision answer when the consequence is explained.</p>","SUPPORT":"<p>Use the pathways sheet, sentence stems, read-aloud, and H&amp;L visual context. Pre-teach pathway, welder, maintenance, electronics, and automation.</p>","FALLBACK":"<p>If H&amp;L fails, use the chapter opener and pathway scaffold for the notebook and exit work. Record students who still owe the video, Game Time, and ratings.</p>"},
          2:{"TITLE":"Machine Breakdown Mystery + Career Research","SUBTITLE":"50 minutes - TEKS d(1)(C), d(2)(A)","ALERT":"<strong>Do not reveal the likely cause too early.</strong> Students need to connect the newly installed label roll to the failure before the class discussion.","PREP":f'<ul><li>Open workbook pages 207-208.</li><li>Print the <a href="/courses/{COURSE_ID}/files/{files["TECH"]["id"]}/preview">checklist scaffold</a>, <a href="/courses/{COURSE_ID}/files/{files["RESEARCH"]["id"]}/preview">career sheet</a>, and <a href="/courses/{COURSE_ID}/files/{files["E2"]["id"]}/preview">exit ticket</a>.</li><li>Open H&amp;L Manufacturing and BLS Production Occupations.</li></ul>',"EVIDENCE":"<p>Collect the five-stage checklist, six-field career research sheet, and Jamie scenario. Minor-grade option: accuracy of the troubleshooting sequence and verified training evidence.</p>","FLOW_TITLE":"50-minute flow","FLOW":flow("#5a2d91","Warm-up - 5 minutes","Connect a broken personal object to troubleshooting.")+flow("#4a9d2f","Machine Breakdown Mystery - 25 minutes","Teach the five stages, release pairs to solve, then discuss the strongest clue.")+flow("#1f617a","Career research - 15 minutes","Students choose one Manufacturing Hat and confirm pay/training with BLS.")+flow("#e3ad19","Exit ticket - 5 minutes","Recommend a career to Jamie using two training steps and a total timeline."),"MONITOR":"<p>Likely cause: the new label roll is wrong, misloaded, or jamming the feed. Strong plans inspect the roll before replacing electrical parts, test after adjustment, and prevent recurrence with a compatibility/setup check.</p>","SUPPORT":"<p>Use the modeled first stage, Welder example, bilingual field labels, and oral rehearsal. Allow checklist notes in the student’s strongest language.</p>","FALLBACK":"<p>If H&amp;L is down, students complete the mystery first and research through BLS. If BLS is blocked, use saved teacher career pages and verify figures later.</p>"},
          3:{"TITLE":"Super Sports Manufacturing - Design, Build, Test","SUBTITLE":"50 minutes - TEKS d(1)(C)","ALERT":"<strong>Run glue stations, not free-roaming glue guns.</strong> Set stations by safe outlets, use heat mats and gloves, and unplug every gun at the five-minute warning.","PREP":f'<ul><li>Open workbook pages 204-206 and the <a href="/courses/{COURSE_ID}/files/{files["E3"]["id"]}/preview">exit ticket</a>.</li><li>Set pair kits: sticks, straws, scissors, gloves, and scrap tray.</li><li>Place one glue gun on each heat-safe station mat and test outlets.</li><li>Post Voice 1 build / Voice 0 test and the 7-minute timer.</li></ul>',"EVIDENCE":"<p>Collect the sketch with top/side views, material reason, and named weld labels. Observe one tested prototype per pair. Minor-grade option: design evidence plus explanation, not craftsmanship alone.</p>","FLOW_TITLE":"50-minute flow","FLOW":flow("#5a2d91","Warm-up - 5 minutes","Trace a 100-rack order through design and production.")+flow("#4a9d2f","Design and choices - 28 minutes","Sketch, choose metal, select welds, and label joints.")+flow("#1f617a","Build and strength test - 12 minutes","Pairs build one rack, test balance/joints, and identify one revision.")+flow("#e3ad19","Exit ticket - 5 minutes","Rank metals, name the weak spot/weld, and connect another Manufacturing career."),"MONITOR":"<p>No single metal is automatically correct. Strong reasoning weighs outdoor corrosion, strength, weight, price, and coating. Fillet/corner welds fit angled rack joints better than a surfacing weld.</p>","SUPPORT":"<p>Offer a pre-drawn rack, pre-cut materials, the stem “I chose ___ because ___ even though ___,” and Spanish labels for metals and prototype.</p>","FALLBACK":"<p>Without glue, dry-fit and tape the joints, then label the real weld each taped joint represents. Absent students complete the full design/choice/test prediction and join a peer test later.</p>"},
          4:{"TITLE":"Sphero Factory Floor + Robots for Crayons","SUBTITLE":"50 minutes - TEKS d(1)(C)","ALERT":"<strong>Verify devices before class.</strong> Charge RVR+ batteries, clear firmware prompts, test one Chromebook, and confirm SpheroEDU/Bluetooth. The simulator is the equal-content fallback.","PREP":f'<ul><li>Build the taped Start-to-Delivery course with obstacles.</li><li>Color-match robots and Chromebooks.</li><li>Open SpheroEDU, workbook pages 200-202, and the <a href="/courses/{COURSE_ID}/files/{files["E4"]["id"]}/preview">exit ticket</a>.</li><li>Print the <a href="/courses/{COURSE_ID}/files/{files["CLIPBOARD"]["id"]}/preview">monitoring roster</a>.</li></ul>',"EVIDENCE":"<p>Observe a run/revision cycle; collect team roles, marked case evidence, and the decision-tree exit ticket. Minor-grade option: participation plus evidence-based first action.</p>","FLOW_TITLE":"50-minute flow","FLOW":flow("#5a2d91","Warm-up and teams - 5 minutes","Connect industrial robots to student experience and assign Coder, Tester, Navigator.")+flow("#4a9d2f","Course and pairing - 8 minutes","Connect one assigned robot per team or open the simulator.")+flow("#1f617a","Block basics - 15 minutes","Chunk Roll, Heading, Wait, Stop; run the three-block challenge.")+flow("#5a2d91","Robots for Crayons - 15 minutes","Read problems, machine reference, shift notes, impact report, and assign production roles.")+flow("#e3ad19","Exit/transition - 7 minutes","Record clues, first actions, and the role-to-role handoff."),"MONITOR":"<p>Program misconception: Heading 90 is an absolute start-direction, not a relative 90-degree turn. Case evidence: new color sensor/software point to Color Confusion; changed belt and mismatched speeds point to Slowpoke Robot.</p>","SUPPORT":"<p>Teach one block at a time, use thumbs checks, pair readers, pre-assign production roles, and allow oral explanation before written evidence.</p>","FALLBACK":"<p>Use the built-in SpheroEDU simulator with the identical code. If the case reading is interrupted, prioritize pages 201-202 and record roles; finish programming at Day 5 launch.</p>"},
          5:{"TITLE":"Sphero Run-Through + Robots for Crayons Presentations","SUBTITLE":"50 minutes - TEKS d(1)(B), d(1)(C)","ALERT":"<strong>Formative team performance.</strong> Use the two fault plans and presentation rubric for feedback. The 1SW assessment map protects individual evidence and does not turn this team task into a sixth grade.","PREP":f'<ul><li>Reset the course and open programs/simulator.</li><li>Print the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">presentation feedback rubric</a>, <a href="/courses/{COURSE_ID}/files/{files["CLIPBOARD"]["id"]}/preview">monitoring roster</a>, and <a href="/courses/{COURSE_ID}/files/{files["E5"]["id"]}/preview">exit ticket</a>.</li><li>Place sticky notes at each team and open workbook pages 202-203.</li><li>Open H&amp;L Manufacturing favorites; keep Quality Check slides ready only for early finishers.</li></ul>',"EVIDENCE":"<p><strong>Formative evidence:</strong> Problem Diagnosis, Solution Reasoning, Repair Plan Detail, and Career Connection/Delivery. Official run, H&amp;L favorites, and the exit ticket are completion or feedback evidence, not separate grades.</p>","FLOW_TITLE":"50-minute flow","FLOW":flow("#5a2d91","Warm-up - 5 minutes","Teams name yesterday’s failure and today’s first change.")+flow("#4a9d2f","Refine and official run - 15 minutes","Two practice runs, one official floor/simulator run.")+flow("#1f617a","Brainstorm and plan - 15 minutes","Generate 15 ideas, then complete both six-row fault plans.")+flow("#5a2d91","Present, favorite, exit - 15 minutes","Two-minute presentations, constructive feedback, two Manufacturing favorites, and the concept-map exit."),"MONITOR":"<p>Ready plans name a specific cause, tool/adjustment, sequence, estimated time, and production improvement. If a team cannot name a tool and time, its idea is not ready. Do not require optional Xello work before the rubric evidence.</p>","SUPPORT":"<p>Allow a written two-paragraph plan instead of live speaking, use bilingual presentation stems, and let students present in pairs while keeping the same evidence requirements.</p>","FALLBACK":"<p>Run every official program in the simulator if hardware fails. An absent presenter may submit the written plan and record or present during catch-up; score only evidence the student contributed.</p>"}}
        pages={}; order=[]
        for day in range(1,6):
            st=student_titles[day]; su=slugify(st); values={"COURSE_ID":COURSE_ID,**student_values[day]}; student=await upsert_page(c,st,render(f"wk1-day{day}-student.html",values),su)
            tt=f"TEACHER: 1SW Wk1 Day {day} Facilitator Guide"; tu=slugify(tt); teacher=await upsert_page(c,tt,render("wk1-teacher.html",{"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student["url"],**teacher_data[day]}),tu)
            await upsert_item(c,module_id,teacher,tt); await upsert_item(c,module_id,student,st); pages[day]={"teacher":teacher,"student":student}; order.extend([(teacher["url"],tt),(student["url"],st)])
        items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); by_url={i.get("page_url"):i for i in items}
        for position,(url,title) in reversed(list(enumerate(order,start=1))): await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{by_url[url]['id']}",data={"module_item[position]":position,"module_item[title]":title})
        final=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); module=await api(c,"GET",f"/courses/{COURSE_ID}/modules/{module_id}")
        print(json.dumps({"module":{"id":module_id,"published":module["published"]},"folders":{str(d):{"id":f["id"],"locked":f["locked"]} for d,f in folders.items()},"pages":{str(d):{k:{"url":v["url"],"published":v["published"]} for k,v in p.items()} for d,p in pages.items()},"items":[{"id":i["id"],"position":i["position"],"title":i["title"],"page_url":i.get("page_url")} for i in final]},indent=2))

asyncio.run(main())
