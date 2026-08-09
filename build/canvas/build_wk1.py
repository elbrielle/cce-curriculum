"""Build the unpublished 1SW Week 1 teacher/student Canvas module."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
import httpx

BASE="https://learn.irvingisd.net"; COURSE_ID=98060
MODULE_NAME="1SW Wk1: Built by Bots - Robotics and Manufacturing Careers"
REFLECTION_TITLE="PRACTICE: 1SW Wk1 Matchmaker Reflection"
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
async def upsert_assignment(c,title,description):
    assignments=await paged(c,f"/courses/{COURSE_ID}/assignments"); found=next((a for a in assignments if a.get("name")==title),None)
    data={"assignment[name]":title,"assignment[description]":description,"assignment[submission_types][]":["online_text_entry","media_recording"],"assignment[grading_type]":"not_graded","assignment[points_possible]":"0","assignment[published]":"false"}
    return await api(c,"PUT" if found else "POST",f"/courses/{COURSE_ID}/assignments/{found['id']}" if found else f"/courses/{COURSE_ID}/assignments",data=data)
async def upsert_item(c,module_id,kind,key,title):
    items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items")
    item=next((i for i in items if (kind=="SubHeader" and i.get("type")=="SubHeader" and i.get("title")==title) or (kind=="Page" and i.get("page_url")==key) or (kind=="Assignment" and i.get("content_id")==key)),None)
    if item:return await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",data={"module_item[title]":title})
    data={"module_item[type]":kind,"module_item[title]":title}
    if kind=="Page": data["module_item[page_url]"]=key
    elif kind=="Assignment": data["module_item[content_id]"]=key
    return await api(c,"POST",f"/courses/{COURSE_ID}/modules/{module_id}/items",data=data)

def flow(color,title,text): return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'

async def main():
    token=sys.stdin.readline().strip()
    if not token: raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"},timeout=120) as c:
        module=await ensure_module(c); module_id=module["id"]
        reflection=await upsert_assignment(c,REFLECTION_TITLE,"<p>Respond privately in three labeled parts: (1) one Matchmaker result that surprised you and why, (2) what Find out why showed about one career match, and (3) one example of an interest raising or lowering a match. You may type or record audio. Do not submit a profile screenshot. This practice remains unpublished and ungraded.</p>")
        support_names={
          "PATHWAYS":"manufacturing-pathways-scaffold.pdf","TECH":"technician-checklist-scaffold.pdf","RESEARCH":"career-research-worksheet.pdf","RESEARCH_EX":"career-research-worksheet-example-welder.pdf","RESEARCH_BI":"career-research-worksheet-bilingual.pdf","PLAN":"1sw-wk1-robots-for-crayons-action-plan.pdf",
          "E1":"1sw-wk1-day1-manufacturing-cluster-tour-more-than-assembly-lines.pdf","E2":"1sw-wk1-day2-machine-breakdown-mystery-career-research.pdf","E3":"1sw-wk1-day3-super-sports-manufacturing-design-build-test.pdf"}
        support_folder="course files/CCR Materials/1SW/Wk1"; await ensure_folder(c,support_folder)
        files={}
        for key,name in support_names.items():
            source_dir=ROOT/"docs/resources/exit-tickets" if key.startswith("E") else ROOT/"docs/resources/worksheets"
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
          4:{"PROBLEMS_IMAGE_ID":uploads[4]["robots-for-crayons-problems.png"]["id"],"MACHINES_IMAGE_ID":uploads[4]["how-the-machines-work.png"]["id"],"SHIFT_IMAGE_ID":uploads[4]["shift-notes-and-impact-report.png"]["id"],"PLAN_FILE_ID":files["PLAN"]["id"]},
          5:{"REFLECTION_URL":f"/courses/{COURSE_ID}/assignments/{reflection['id']}"}}
        student_titles={1:"STUDENT: 1SW Wk1 Day 1 - Manufacturing Cluster Tour",2:"STUDENT: 1SW Wk1 Day 2 - Machine Breakdown Mystery",3:"STUDENT: 1SW Wk1 Day 3 - Design Build Test",4:"STUDENT: 1SW Wk1 Day 4 - Robots for Crayons Action Plan",5:"STUDENT: 1SW Wk1 Day 5 - Xello Matchmaker"}
        student_urls={1:slugify(student_titles[1]),2:slugify(student_titles[2]),3:slugify(student_titles[3]),4:"student-1sw-wk1-day-4-sphero-and-robots-for-crayons",5:"student-1sw-wk1-day-5-test-solve-present"}
        teacher_data={
          1:{"TITLE":"Manufacturing Cluster Tour","SUBTITLE":"50 minutes - required Xello and district HQIM","TOPIC":"Career Clusters","OBJECTIVE":"Students will explore and describe CTE career clusters and identify Manufacturing opportunities using Xello, FYF, and H&L evidence.","TEKS":"d(1)(B), d(1)(C)","DOL":"Submitted What is CTE response, two Stop and Jot notes, and a two-career comparison with one task and one preparation fact for each.","ALERT":"<strong>Protect the ten-minute Xello task.</strong> What is CTE is a required submission, not an optional link. Keep the H&amp;L exploration focused enough to close in 15 minutes.","PREP":f'<ul><li>Preview the current Xello What is CTE prompt and open the Completion Standards report.</li><li>Open FYF pp. 199 and 212 and H&amp;L Manufacturing.</li><li>Post the <a href="/courses/{COURSE_ID}/files/{files["PATHWAYS"]["id"]}/preview">pathways scaffold</a> and <a href="/courses/{COURSE_ID}/files/{files["E1"]["id"]}/preview">exit ticket</a>.</li></ul>',"EVIDENCE":"<p>Xello submission, Stop and Jot notes, and two-career comparison. Keep formative unless it is already one of the mapped Minor checkpoints.</p>","FLOW_TITLE":"50-minute flow","FLOW":flow("#5a2d91","Warm-up - 5 minutes","Trace one morning product through design, production, programming, and quality control.")+flow("#4a9d2f","Xello What is CTE - 10 minutes","Students open the assigned task and submit the current district prompt.")+flow("#1f617a","FYF Manufacturing opener - 15 minutes","Use p. 199, the weld-quality decision, pathways, and district-customized FYF details.")+flow("#5a2d91","H&L cluster exploration - 15 minutes","Run two Stop and Jot pauses, one pathway rating, and three Hat ratings.")+flow("#e3ad19","Exit - 5 minutes","Compare two Manufacturing careers."),"MONITOR":"<p>Verify the Xello submission first. In H&amp;L, check for two career notes, one pathway, and three actual Hat ratings. Any salary note keeps the career, geography, salary label, and date viewed attached. Do not overwrite a district HQIM figure with a differently defined national median.</p>","SUPPORT":"<p>Use the pathway sheet, sentence frames, read-aloud, and H&amp;L visual context. Pre-teach pathway, welder, maintenance, electronics, and automation.</p>","FALLBACK":"<p>The pathway scaffold and FYF opener support the Manufacturing evidence if H&amp;L is unavailable. What is CTE still moves to supervised Xello catch-up and is verified through the report.</p>"},
          2:{"TITLE":"Machine Breakdown Mystery + Career Research","SUBTITLE":"50 minutes - TEKS d(1)(C), d(2)(A)","TOPIC":"Career Opportunities","OBJECTIVE":"Students will use a five-stage troubleshooting process and research the preparation required for one Manufacturing career.","TEKS":"d(1)(C), d(2)(A)","DOL":"Completed Machine Breakdown Mystery checklist and one Manufacturing career research worksheet.","ALERT":"<strong>Do not reveal the likely cause too early.</strong> Students need to connect the newly installed label roll to the failure before discussion.","PREP":f'<ul><li>Open FYF pp. 207-208.</li><li>Post the <a href="/courses/{COURSE_ID}/files/{files["TECH"]["id"]}/preview">checklist scaffold</a>, <a href="/courses/{COURSE_ID}/files/{files["RESEARCH"]["id"]}/preview">career sheet</a>, and <a href="/courses/{COURSE_ID}/files/{files["E2"]["id"]}/preview">exit ticket</a>.</li><li>Open H&amp;L Manufacturing; keep BLS only as a separately labeled cross-check.</li></ul>',"EVIDENCE":"<p>Five-stage checklist, six-field career sheet, and Jamie scenario. Grade source accuracy and reasoning, not whether H&amp;L and a national source display the same number.</p>","FLOW_TITLE":"50-minute flow","FLOW":flow("#5a2d91","Warm-up - 5 minutes","Connect a broken personal object to troubleshooting.")+flow("#4a9d2f","Machine Breakdown Mystery - 25 minutes","Teach the five stages, release pairs, then discuss the strongest clue.")+flow("#1f617a","Career research - 15 minutes","Students choose one Manufacturing Hat and keep the HQIM source labels with every figure.")+flow("#e3ad19","Exit - 5 minutes","Recommend a career using two training steps and a timeline."),"MONITOR":"<p>Likely cause: the new label roll is wrong, misloaded, or jamming the feed. Strong plans inspect it before unrelated electrical parts, test after adjustment, and prevent recurrence. If sources differ, check geography and measure rather than declaring the HQIM wrong.</p>","SUPPORT":"<p>Use the modeled first stage, Welder example, bilingual field labels, and oral rehearsal. Allow notes in the student’s strongest language.</p>","FALLBACK":"<p>If H&amp;L is unavailable, complete the mystery and use a saved teacher Hat card. Schedule platform exploration later instead of pretending an external occupation page is the same source.</p>"},
          3:{"TITLE":"Super Sports Manufacturing - Design, Build, Test","SUBTITLE":"50 minutes - TEKS d(1)(C)","TOPIC":"Career Opportunities","OBJECTIVE":"Students will apply Welder design choices by selecting materials and joints, then build and test a bike-rack prototype.","TEKS":"d(1)(C)","DOL":"Top-and-side-view bike-rack sketch with labeled welds plus one prototype test and named revision.","ALERT":"<strong>Run glue stations, not free-roaming glue guns.</strong> Use heat mats and gloves, and unplug every gun at the five-minute warning.","PREP":f'<ul><li>Open FYF pp. 204-206 and the <a href="/courses/{COURSE_ID}/files/{files["E3"]["id"]}/preview">exit ticket</a>.</li><li>Set pair kits: sticks, straws, scissors, gloves, and scrap tray.</li><li>Test the equal dry-fit and masking-tape route.</li></ul>',"EVIDENCE":"<p>Sketch with two views, material reason, labeled welds, and one tested prototype. Score design reasoning, not craftsmanship or tool access.</p>","FLOW_TITLE":"50-minute flow","FLOW":flow("#5a2d91","Warm-up - 5 minutes","Trace a 100-rack order through design and production.")+flow("#4a9d2f","Design and choices - 28 minutes","Sketch, choose metal, select welds, and label joints.")+flow("#1f617a","Build and test - 12 minutes","Build one rack, test balance and joints, and name one revision.")+flow("#e3ad19","Exit - 5 minutes","Rank metals, identify a weak point, and connect another career."),"MONITOR":"<p>No single metal is automatically correct. Strong reasoning weighs corrosion, strength, weight, price, and coating. Fillet or corner welds fit angled rack joints better than surfacing welds.</p>","SUPPORT":"<p>Offer a pre-drawn rack, pre-cut materials, bilingual labels, and the frame “I chose ___ because ___ even though ___.”</p>","FALLBACK":"<p>Dry-fit and tape each joint, then label the real weld it represents. Absent students complete the full design and test prediction.</p>"},
          4:{"TITLE":"Robots for Crayons Evidence and Action Plan","SUBTITLE":"50 minutes - TEKS d(1)(C)","TOPIC":"Manufacturing Troubleshooting","OBJECTIVE":"Students will identify Manufacturing careers and explain how workers use case evidence to respond to two production problems.","TEKS":"d(1)(C)","DOL":"Two complete problem plans with clues, testable solution, ordered steps, tools or adjustments, time, production effect, and next check.","ALERT":"<strong>Evidence before fixes.</strong> Students read all three FYF source sections before choosing solutions. Sphero is an optional later extension, not today’s required path.","PREP":f'<ul><li>Open FYF pp. 200-203 and the embedded licensed visuals.</li><li>Post the <a href="/courses/{COURSE_ID}/files/{files["PLAN"]["id"]}/preview">three-page action plan</a>.</li><li>Prepare sticky notes and assign the four factory-role lenses.</li></ul>',"EVIDENCE":"<p>Collect the two-problem plan and an individual two-to-three-sentence career-role response. The packet gives each reasoning job honest writing space.</p>","FLOW_TITLE":"50-minute flow","FLOW":flow("#5a2d91","Warm-up - 5 minutes","Choose the first evidence-based check after a replacement part fails.")+flow("#4a9d2f","Factory brief and machine reference - 10 minutes","Read the two problems and sort supported causes.")+flow("#1f617a","Shift evidence - 10 minutes","Mark two clues per problem through one role lens.")+flow("#5a2d91","Both action plans - 20 minutes","Choose, explain, sequence, time, and plan the next check.")+flow("#e3ad19","Individual check - 5 minutes","Name one role, first action, and source clue."),"MONITOR":"<p><strong>Color Confusion:</strong> first check the replacement sensor’s compatibility, installation, and controlled test. <strong>Slowpoke Robot:</strong> first check the replaced belt’s size or tension, then retest the arm and conveyor together. Accept another safe plan when students cite the source and name what result triggers the next check.</p>","SUPPORT":"<p>Read shift notes aloud, use bilingual labels, permit speech-to-text, and give each student one role lens. At minute 10 check both evidence sections; at minute 16 check the second ordered-step set.</p>","FALLBACK":"<p>The embedded images and packet are the complete independent and absence route. No robot or presentation is required.</p>"},
          5:{"TITLE":"Xello Matchmaker and Career-Match Reflection","SUBTITLE":"50 minutes - required Grade 8 Xello completion","TOPIC":"Career Interests","OBJECTIVE":"Students will analyze their first career-assessment results by connecting one result to an interest and one career detail.","TEKS":"d(1)(A)","DOL":"Matchmaker Phase 1 completed plus a private three-part reflection with one surprise, one Find out why connection, and one interest-to-match example.","ALERT":"<strong>Protect the full Matchmaker lesson.</strong> The licensed guide gives 30-35 minutes for the first 39 questions. After high school goal is the prerequisite. Do not rush students or require profile screenshots.","PREP":f'<ul><li>Confirm After high school goal completion in the report.</li><li>Open a student demo account and the licensed <a href="/courses/{COURSE_ID}/files/{(await find_file(c,"matchmaker-assessment.pdf"))["id"]}/preview">Matchmaker educator guide</a>.</li><li>Open the unpublished private reflection Assignment.</li><li>Prepare a four-status roster: complete, prerequisite missing, access issue, absent.</li></ul>',"EVIDENCE":"<p>The Completion Standards report verifies Phase 1. The private reflection captures analysis without exposing profile data. This is formative practice, not another Major or Minor.</p>","FLOW_TITLE":"50-minute flow","FLOW":flow("#5a2d91","Warm-up - 5 minutes","Name one liked task and one avoided task.")+flow("#4a9d2f","Scale and Find out why - 7 minutes","Model the full response scale and one demo-account result.")+flow("#1f617a","Matchmaker lesson - 28 minutes","Complete the first 39 questions and inspect one match.")+flow("#e3ad19","Private reflection - 7 minutes","Answer three labeled prompts in Canvas.")+flow("#1f617a","Report and catch-up - 3 minutes","Verify completion or schedule supervised recovery."),"MONITOR":"<p>Lap 1: correct About Me task. Lap 2: full response scale. Lap 3: one career plus Find out why. Score the reflection’s reasoning, not whether the student likes the match. A teacher sample may support a blocked student’s reflection, but it does not count as Xello completion.</p>","SUPPORT":"<p>Read scale labels aloud, reduce visual distractions, provide three sentence frames, and allow typing, speech-to-text, audio, or a private teacher conference.</p>","FALLBACK":"<p>A paper interest sort supports learning but does not replace Matchmaker. Use supervised catch-up for prerequisite, login, absence, or incomplete assessment.</p>"}}
        day_names={1:"Manufacturing Cluster Tour",2:"Machine Breakdown Mystery",3:"Design Build Test",4:"Robots for Crayons Action Plan",5:"Xello Matchmaker"}
        pages={}; order=[]
        for day in range(1,6):
            header_title=f"Day {day} · {day_names[day]}"; header=await upsert_item(c,module_id,"SubHeader",None,header_title); order.append(("SubHeader",header["id"],header_title))
            st=student_titles[day]; su=student_urls[day]; values={"COURSE_ID":COURSE_ID,**student_values[day]}; student=await upsert_page(c,st,render(f"wk1-day{day}-student.html",values),su)
            tt=f"TEACHER: 1SW Wk1 Day {day} Facilitator Guide"; tu=slugify(tt); teacher=await upsert_page(c,tt,render("wk1-teacher.html",{"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student["url"],**teacher_data[day]}),tu)
            await upsert_item(c,module_id,"Page",teacher["url"],tt); await upsert_item(c,module_id,"Page",student["url"],st); pages[day]={"teacher":teacher,"student":student}; order.extend([("Page",teacher["url"],tt),("Page",student["url"],st)])
            if day==5: await upsert_item(c,module_id,"Assignment",reflection["id"],REFLECTION_TITLE); order.append(("Assignment",reflection["id"],REFLECTION_TITLE))
        items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items")
        obsolete_headers={f"Day {day}" for day in range(1,6)}
        for item in [entry for entry in items if entry.get("type")=="SubHeader" and entry.get("title") in obsolete_headers]:
            await api(c,"DELETE",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}")
        items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items")
        for position,(kind,key,title) in enumerate(order,start=1):
            item=next(i for i in items if (kind=="SubHeader" and i.get("id")==key) or (kind=="Page" and i.get("page_url")==key) or (kind=="Assignment" and i.get("content_id")==key))
            await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",data={"module_item[position]":position,"module_item[title]":title})
        final=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); module=await api(c,"GET",f"/courses/{COURSE_ID}/modules/{module_id}")
        print(json.dumps({"module":{"id":module_id,"published":module["published"]},"assignment":{"id":reflection["id"],"published":reflection.get("published")},"folders":{str(d):{"id":f["id"],"locked":f["locked"]} for d,f in folders.items()},"pages":{str(d):{k:{"url":v["url"],"published":v["published"]} for k,v in p.items()} for d,p in pages.items()},"items":[{"id":i["id"],"position":i["position"],"title":i["title"],"type":i["type"],"page_url":i.get("page_url")} for i in final]},indent=2))

asyncio.run(main())
