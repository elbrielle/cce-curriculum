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
          "PROGRAMS":"wk2-it-programs-scaffold.pdf","RESEARCH":"career-research-worksheet.pdf","EXAMPLE":"wk2-career-research-web-developer.pdf","BILINGUAL":"career-research-worksheet-bilingual.pdf","SALARY":"wk2-it-salary-comparison.pdf","MODEL":"wk2-it-salary-comparison-model.pdf","SALARY_BI":"wk2-it-salary-comparison-bilingual.pdf","GUIDE":"wk2-bls-data-guide.pdf","FLIP":"wk2-flip-the-failure-scaffold.pdf","RUBRIC":"wk2-salary-hoc-rubric.pdf","CLIPBOARD":"clipboard-roster-grid.pdf","D5":"wk2-day5-it-pathway-decision.pdf",
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
          2:{"APP_IMAGE_ID":uploads[2]["it-app-exploration.png"]["id"],"RESEARCH_FILE_ID":files["RESEARCH"]["id"],"EXAMPLE_FILE_ID":files["EXAMPLE"]["id"],"BILINGUAL_FILE_ID":files["BILINGUAL"]["id"],"EXIT_FILE_ID":files["E2"]["id"]},
          3:{"SCENARIO_IMAGE_ID":uploads[3]["resilience-scenario.png"]["id"],"CHART_IMAGE_ID":uploads[3]["flip-the-failure-chart.png"]["id"],"FLIP_FILE_ID":files["FLIP"]["id"],"SALARY_FILE_ID":files["SALARY"]["id"],"MODEL_FILE_ID":files["MODEL"]["id"],"GUIDE_FILE_ID":files["GUIDE"]["id"],"BILINGUAL_FILE_ID":files["SALARY_BI"]["id"],"EXIT_FILE_ID":files["E3"]["id"]},
          4:{"EXIT_FILE_ID":files["E4"]["id"]},
          5:{"APP_IMAGE_ID":uploads[5]["it-app-exploration.png"]["id"],"RUBRIC_FILE_ID":files["RUBRIC"]["id"],"EXIT_FILE_ID":files["D5"]["id"]}}
        student_titles={1:"STUDENT: 1SW Wk2 Day 1 - Map the IT Cluster",2:"STUDENT: 1SW Wk2 Day 2 - Compare Programming Careers",3:"STUDENT: 1SW Wk2 Day 3 - Resilience and Salary Showdown",4:"STUDENT: 1SW Wk2 Day 4 - Test a Programming Concept",5:"STUDENT: 1SW Wk2 Day 5 - Personality Style and IT Decision"}
        teacher_data={
          1:{"TITLE":"IT Cluster Tour + Four Irving Programs","SUBTITLE":"50 minutes - TEKS d(1)(B), d(1)(C)","ALERT":"<strong>Preflight H&amp;L from a student Chromebook.</strong> Confirm the IT tour, Game Time, and Hat profiles before class; Day 1 has a complete paper fallback.","PREP":f'<ul><li>Open FYF pp. 23 and 36-38.</li><li>Print the <a href="/courses/{COURSE_ID}/files/{files["PROGRAMS"]["id"]}/preview">programs/Stop-and-Jot scaffold</a> and <a href="/courses/{COURSE_ID}/files/{files["E1"]["id"]}/preview">exit ticket</a>.</li><li>Post the two video pause prompts.</li></ul>',"EVIDENCE":"<p>Formative/minor option: one new career and one question, fit/not-fit reasons, three Hat ratings, and the Venn exit ticket. Do not grade each exit ticket as a separate minor.</p>","FLOW":flow("#5a2d91","Security decision - 8 minutes","Silent think, partner reasoning, two shares focused on user and company consequences.")+flow("#4a9d2f","Irving programs - 12 minutes","Name all four programs and connect each to one kind of work.")+flow("#1f617a","H&L exploration - 22 minutes","Tour, Game Time, fit/not-fit choices, and three Hat ratings.")+flow("#e3ad19","Venn exit - 8 minutes","Compare Programming & Software Development with Cybersecurity."),"MONITOR":"<p>Programming only: coding, program structure, debugging, testing, application design. Cybersecurity only: network protection, data security, risk response. Shared: technical problem solving, software/systems, testing. Programming is the stronger choice when the stated job is writing and testing code.</p>","SUPPORT":"<p>Use the program scaffold, read the decision aloud, provide the two Stop-and-Jot stems, and pre-teach cybersecurity, software, debugging, and pathway.</p>","FALLBACK":"<p>Use workbook pp. 23 and 36-38 plus the scaffold. Students complete all written evidence and finish the live video/game/ratings during catch-up.</p>"},
          2:{"TITLE":"Programming Pathway Deep-Dive","SUBTITLE":"50 minutes - TEKS d(1)(C), d(2)(A)","ALERT":"<strong>Verify the four named Hats live.</strong> If a title differs or is unavailable, students record the exact available programming Hat. Keep H&amp;L and any BLS cross-check as separate source records.","PREP":f'<ul><li>Open H&amp;L IT &gt; Programming and Software Development.</li><li>Pre-open BLS Software Developers and Web Developers as optional national cross-checks.</li><li>Print the <a href="/courses/{COURSE_ID}/files/{files["RESEARCH"]["id"]}/preview">career sheet</a>, optional <a href="/courses/{COURSE_ID}/files/{files["EXAMPLE"]["id"]}/preview">model</a>, and <a href="/courses/{COURSE_ID}/files/{files["E2"]["id"]}/preview">exit ticket</a>.</li></ul>',"EVIDENCE":"<p>Formative/minor option: four-row Hat table plus the six-field career sheet with each fact attached to its source. The mobile-game exit is formative.</p>","FLOW":flow("#5a2d91","Warm-up - 5 minutes","Sort familiar apps/sites/games by who builds them.")+flow("#4a9d2f","Four-Hat comparison - 25 minutes","Students record the exact Hat title, preparation, local pay, demand, and one reaction for each role.")+flow("#1f617a","One-career research - 15 minutes","Complete six fields from the Hat; add BLS only as a separately labeled cross-check.")+flow("#e3ad19","Hiring case - 5 minutes","Select the best-fit available programming career and support the decision with a task or tool from the evidence."),"MONITOR":"<p>Every row needs an exact career title, preparation, localized salary with source details, demand, and reaction. Do not supply generalized claims when the live Hat differs.</p>","SUPPORT":"<p>Use the Web Developer model, bilingual field labels, and oral rehearsal before writing. Keep platform vocabulary on the board.</p>","FALLBACK":"<p>Use the worked model and teacher-provided dated source cards for one complete career sheet and exit ticket. Rebuild the four H&amp;L rows in catch-up before Day 3.</p>"},
          3:{"TITLE":"Powerskill Resilience + IT Salary Showdown","SUBTITLE":"50 minutes - TEKS d(1)(C), d(5)(A), d(5)(E)","ALERT":"<strong>Keep the measures separate.</strong> H&amp;L and Xello are district HQIM sources for localized career data. BLS is a dated national cross-check. Never overwrite one with the other.","PREP":f'<ul><li>Open FYF pp. 26-27, the live H&amp;L or Xello career profiles, and three clean BLS occupation pages.</li><li>Record source, career, geography, measure, and date for every teacher-model figure.</li><li>Print the <a href="/courses/{COURSE_ID}/files/{files["SALARY"]["id"]}/preview">salary sheet</a>, <a href="/courses/{COURSE_ID}/files/{files["GUIDE"]["id"]}/preview">BLS guide</a>, and <a href="/courses/{COURSE_ID}/files/{files["E3"]["id"]}/preview">exit ticket</a>.</li></ul>',"EVIDENCE":"<p>The salary sheet plus Day 5 Career Fit Reflection is a 20-point <strong>Minor 2 grade</strong>. Today, collect and return the sheet for the reflection. Flip the Failure and the exit matrix are formative.</p>","FLOW":flow("#5a2d91","Warm-up - 5 minutes","Name a setback and a specific next move.")+flow("#4a9d2f","Flip the Failure - 15 minutes","Four failures, each with one technical fix and one resilience action.")+flow("#1f617a","Salary comparison - 25 minutes","Chunk the HQIM localized figure, BLS national median, preparation, outlook, and job count while preserving every label.")+flow("#e3ad19","Evidence claim - 5 minutes","Choose a career using a cited salary or growth figure and name the source."),"MONITOR":"<p>Strong fixes name an owner, action, and next check. Pivot if students confuse annual/hourly pay, local range/national median, or outlook percent/job count. A source difference must remain visible.</p>","SUPPORT":"<p>Use the prefilled resilience row, Software Developer model, BLS extraction guide, bilingual headers, and read-aloud for the scenario.</p>","FALLBACK":"<p>If a live source fails, use the teacher’s dated key and name the source on the sheet. Absent students receive the Day 2 model data and complete two remaining careers.</p>"},
          4:{"TITLE":"Programming Concept Lab","SUBTITLE":"50 minutes - TEKS d(1)(C)","ALERT":"<strong>Code.org is supplemental.</strong> Use one verified tutorial when available, but keep the same concept evidence through a no-login or paper block-code route.","PREP":f'<ul><li>Test one approved tutorial on a student-filtered Chromebook.</li><li>Prepare a no-login or paper block-sequence fallback.</li><li>Print the <a href="/courses/{COURSE_ID}/files/{files["CLIPBOARD"]["id"]}/preview">monitoring roster</a> and <a href="/courses/{COURSE_ID}/files/{files["E4"]["id"]}/preview">exit ticket</a>.</li><li>Decide screenshot show/submit location before class.</li></ul>',"EVIDENCE":"<p>Formative/minor option: one working or correctly traced block sequence plus a specific explanation of sequence, loop, or conditional logic. Tutorial completion is not scored.</p>","FLOW":flow("#5a2d91","Concept launch - 8 minutes","Model sequence, loop, and conditional with one visible block set.")+flow("#4a9d2f","Route setup - 7 minutes","Place students in the verified tutorial or equal paper/no-login route.")+flow("#1f617a","Build and explain - 28 minutes","Fixed monitoring laps: progress, concept explanation, and persistence.")+flow("#e3ad19","Career exit - 7 minutes","Connect the chosen concept to a plausible job task."),"MONITOR":"<p>Sequence must describe ordered steps; loop must repeat without duplicated blocks; conditional must respond to a condition. Model one step when needed, then return the reasoning to the student.</p>","SUPPORT":"<p>Pair driver/navigator roles, allow muted tutorials, provide vocabulary cards, and accept an oral explanation recorded by the teacher before the student writes.</p>","FALLBACK":"<p>Use the teacher block sequence. Students trace output, name the concept, explain it, and complete the same exit ticket. No vendor account or certificate is required.</p>"},
          5:{"TITLE":"Xello Personality Style + IT Pathway Decision","SUBTITLE":"50 minutes - TEKS d(1)(C), d(5)(A), d(5)(E)","ALERT":"<strong>Required Xello spine:</strong> Personality Style is the Week 2 task (20 minutes) and requires Matchmaker. Favorite Clusters belongs later. Code.org may continue only after required work.","PREP":f'<ul><li>Check the Xello Completion Standards report for Matchmaker prerequisites.</li><li>Embed/open the licensed <a href="/courses/{COURSE_ID}/files/{files["XELLO"]["id"]}/preview">Personality Style teacher resource</a>.</li><li>Return Day 3 salary sheets and print the <a href="/courses/{COURSE_ID}/files/{files["D5"]["id"]}/preview">IT Pathway Decision</a> and <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">Minor 2 rubric</a>.</li></ul>',"EVIDENCE":"<p><strong>Minor 2 grade:</strong> IT Salary Comparison + Career Fit Reflection, 20 points. Required completion evidence: Xello Personality Style in the report. H&amp;L pathway rating and the IT decision sheet are formative.</p>","FLOW":flow("#5a2d91","Xello Personality Style - 20 minutes","Complete the quiz, review results, and record one trait/example.")+flow("#4a9d2f","H&amp;L pathway decision - 12 minutes","Complete Pathway Possibilities, rate one pathway, and review two Hats.")+flow("#1f617a","Minor reflection - 10 minutes","Add pathway, salary fact, career-fit reasoning, and final IT call.")+flow("#e3ad19","Decision exit - 8 minutes","Connect Personality Style to the current IT career decision."),"MONITOR":"<p>Check Matchmaker prerequisite, Personality Style completion, one trait with a real example, one rated IT pathway, two reviewed Hats, and all four Career Fit sentences. Students may reject the cluster and still earn full evidence credit.</p>","SUPPORT":"<p>Read result descriptions aloud, provide trait/example stems, pair students for navigation, and accept oral rehearsal. Do not require a full translation of the task.</p>","FALLBACK":"<p>Record the Xello access issue for campus follow-up. Student completes the paper trait reflection, workbook pathway review, Minor 2 reflection, and decision sheet; platform completion moves to catch-up.</p>"}}
        day_headers={1:"Day 1 — Map the IT Cluster",2:"Day 2 — Compare Programming Careers",3:"Day 3 — Resilience and Salary Showdown",4:"Day 4 — Test a Programming Concept",5:"Day 5 — Personality Style and IT Decision"}
        pages={}; order=[]
        for day in range(1,6):
            st=student_titles[day]; su=slugify(st); student=await upsert_page(c,st,render(f"wk2-day{day}-student.html",{"COURSE_ID":COURSE_ID,**student_values[day]}),su)
            tt=f"TEACHER: 1SW Wk2 Day {day} Facilitator Guide"; tu=slugify(tt); teacher=await upsert_page(c,tt,render("wk2-teacher.html",{"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student["url"],**teacher_data[day]}),tu)
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
