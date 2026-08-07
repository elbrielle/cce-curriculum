"""Build the unpublished 2SW Week 3 teacher/student Canvas module and practice quiz."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
import httpx

BASE="https://learn.irvingisd.net"; COURSE_ID=98060
MODULE_NAME="2SW Wk3: Nursing Science - Routes, Simulation, and Handoff"
QUIZ_TITLE="PRACTICE: Vital Signs and Handoff Check"
ROOT=Path(__file__).resolve().parents[2]; TEMPLATES=Path(__file__).parent/"templates"; ASSETS=ROOT/"cce-curriculum/resources/canvas-licensed/2sw/wk3"

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
async def upsert_page_item(c,module_id,page,title):
    items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); item=next((i for i in items if i.get("page_url")==page["url"]),None)
    if item: return await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",data={"module_item[title]":title})
    return await api(c,"POST",f"/courses/{COURSE_ID}/modules/{module_id}/items",data={"module_item[type]":"Page","module_item[page_url]":page["url"],"module_item[title]":title})

QUIZ_QUESTIONS=[
  {"name":"Q1 - Simulator boundary","text":"What does the micro:bit program prove?","correct":"It displays fictional values from its code.","wrong":["It measures a classmate's heart rate.","It diagnoses a medical condition.","It replaces approved medical equipment."],"correct_comment":"Correct. The program is a training simulator.","incorrect_comment":"The program displays coded fictional values. It does not measure or diagnose."},
  {"name":"Q2 - Listen to the person","text":"A fictional patient reports dizziness even though the supplied numbers look ordinary. What is the best response in this lesson?","correct":"Record the symptom and make the supervised handoff.","wrong":["Ignore the symptom because the numbers look ordinary.","Diagnose the patient from the symptom.","Delete the numbers from the report."],"correct_comment":"Correct. The person's report belongs in the handoff.","incorrect_comment":"Normal-looking numbers do not erase a reported symptom, and students do not diagnose."},
  {"name":"Q3 - Device quality","text":"A device shows 75, 180, and 42 within 20 seconds while the fictional patient sits still. What should the worker notice first?","correct":"The readings conflict, so the device or process needs a recheck and report.","wrong":["The middle number must be correct.","The patient definitely has three conditions.","The readings should be hidden."],"correct_comment":"Correct. Conflicting readings are a data-quality signal.","incorrect_comment":"Recheck the device or process and report the conflict without diagnosing."},
  {"name":"Q4 - Salary label","text":"What does $93,600 mean on the route guide?","correct":"It is the May 2024 U.S. median wage for registered nurses.","wrong":["It is guaranteed DFW starting pay.","It is the salary every RN earns.","It is the cost of an RN degree."],"correct_comment":"Correct. Keep the year, geography, and measure attached.","incorrect_comment":"The figure is a May 2024 U.S. median, not a local or starting-pay guarantee."},
  {"name":"Q5 - Texas route check","text":"What should a student verify before enrolling in a Texas pre-licensure nursing program?","correct":"The program is approved by the Texas Board of Nursing.","wrong":["The program guarantees a job.","The program has the highest advertised salary.","The program skips the licensure process."],"correct_comment":"Correct. Program approval is a required route check.","incorrect_comment":"The Texas Board of Nursing directs students to verify program approval before enrolling."}
]

async def upsert_quiz(c):
    quizzes=await paged(c,f"/courses/{COURSE_ID}/quizzes"); quiz=next((q for q in quizzes if q.get("title")==QUIZ_TITLE),None)
    data={"quiz[title]":QUIZ_TITLE,"quiz[description]":"<p>Ungraded misconception check for fictional data, simulator limits, careful handoff, salary labels, and Texas nursing routes. Retry as needed.</p>","quiz[quiz_type]":"practice_quiz","quiz[published]":"false","quiz[allowed_attempts]":"-1","quiz[show_correct_answers]":"true","quiz[shuffle_answers]":"false"}
    quiz=await api(c,"PUT" if quiz else "POST",f"/courses/{COURSE_ID}/quizzes/{quiz['id']}" if quiz else f"/courses/{COURSE_ID}/quizzes",data=data)
    existing=await paged(c,f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    for position,spec in enumerate(QUIZ_QUESTIONS,start=1):
        found=next((q for q in existing if q.get("question_name")==spec["name"]),None)
        answers=[{"answer_text":spec["correct"],"answer_weight":100}]+[{"answer_text":v,"answer_weight":0} for v in spec["wrong"]]
        payload={"question":{"question_name":spec["name"],"question_text":spec["text"],"question_type":"multiple_choice_question","position":position,"points_possible":1,"correct_comments":spec["correct_comment"],"incorrect_comments":spec["incorrect_comment"],"answers":answers}}
        await api(c,"PUT" if found else "POST",f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions",json=payload)
    return await api(c,"GET",f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
async def upsert_quiz_item(c,module_id,quiz):
    items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); item=next((i for i in items if i.get("type")=="Quiz" and i.get("content_id")==quiz["id"]),None)
    if item: return await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",data={"module_item[title]":QUIZ_TITLE})
    return await api(c,"POST",f"/courses/{COURSE_ID}/modules/{module_id}/items",data={"module_item[type]":"Quiz","module_item[content_id]":quiz["id"],"module_item[title]":QUIZ_TITLE})
def flow(color,title,text): return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'

async def main():
    token=sys.stdin.readline().strip()
    if not token: raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"},timeout=120) as c:
        module=await ensure_module(c); module_id=module["id"]; quiz=await upsert_quiz(c)
        names={"ROUTE":"2sw-wk3-nursing-route-guide.pdf","COMPARE":"2sw-wk3-nursing-route-comparison.pdf","BUILD":"2sw-wk3-vital-signs-simulator-build.pdf","CARDS":"2sw-wk3-fictional-patient-cards.pdf","HANDOFF":"2sw-wk3-clinical-handoff-record.pdf","RUBRIC":"2sw-wk3-handoff-rubric.pdf","REFLECTION":"2sw-wk3-xello-save-careers-reflection.pdf"}
        support_folder="course files/CCR Materials/2SW/Wk3"; core=await ensure_folder(c,support_folder); files={k:await upload(c,ROOT/"docs/resources/worksheets"/v,support_folder) for k,v in names.items()}
        files["XELLO"]=await upload(c,ROOT/"cce-curriculum/resources/xello-licensed/prerequisites/careers.pdf",support_folder)
        uploads={}; folders={}
        for day in range(1,6):
            fp=f"course files/CCR Materials/2SW/Wk3/Day {day} Visuals"; folders[day]=await ensure_folder(c,fp); uploads[day]={}
            for path in sorted((ASSETS/f"day{day}").glob("*.png")): uploads[day][path.name]=await upload(c,path,fp)
        quiz_url=f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        student_values={
          1:{"OPENER_IMAGE_ID":uploads[1]["health-science-opener.png"]["id"],"PROGRAM_IMAGE_ID":uploads[1]["irving-health-programs.png"]["id"],"ROUTE_FILE_ID":files["ROUTE"]["id"],"COMPARE_FILE_ID":files["COMPARE"]["id"]},
          2:{"COMPARE_FILE_ID":files["COMPARE"]["id"]},
          3:{"BUILD_FILE_ID":files["BUILD"]["id"],"RESEARCH_IMAGE_ID":uploads[3]["vitals-research.png"]["id"],"TOOLS_IMAGE_ID":uploads[3]["vitals-tool-reference.png"]["id"]},
          4:{"CARDS_FILE_ID":files["CARDS"]["id"],"HANDOFF_FILE_ID":files["HANDOFF"]["id"],"RUBRIC_FILE_ID":files["RUBRIC"]["id"],"REPORT_IMAGE_ID":uploads[4]["vitals-report.png"]["id"],"QUIZ_URL":quiz_url},
          5:{"REFLECTION_FILE_ID":files["REFLECTION"]["id"],"APP_IMAGE_ID":uploads[5]["health-science-app.png"]["id"]}}
        titles={1:"STUDENT: 2SW Wk3 Day 1 - Compare Nursing Routes",2:"STUDENT: 2SW Wk3 Day 2 - Choose with Evidence",3:"STUDENT: 2SW Wk3 Day 3 - Build a Training Simulator",4:"STUDENT: 2SW Wk3 Day 4 - Write a Careful Handoff",5:"STUDENT: 2SW Wk3 Day 5 - Save Three Careers"}
        td={
          1:{"TITLE":"Health Science and Nursing Routes","SUBTITLE":"50 minutes · TEKS d(1)(B), d(1)(C)","ALERT":"<strong>Use the current pathway name.</strong> Irving ISD now lists Nursing Science at Singley Academy. The older workbook wording and any credential list are not current guarantees.","PREP":f'<ul><li>Open the two embedded workbook visuals.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["ROUTE"]["id"]}/preview">route guide</a> and <a href="/courses/{COURSE_ID}/files/{files["COMPARE"]["id"]}/preview">comparison</a>.</li><li>Optional: preflight Xello for a current local salary check.</li></ul>',"EVIDENCE":"<p>Collect the first two comparison rows. Pay facts must retain year, geography, and measure.</p>","FLOW":flow("#5a2d91","Healthcare worker warm-up · 5 minutes","List roles beyond physician and name one task.")+flow("#4a9d2f","Health fair decision · 10 minutes","Connect one booth to the worker who staffs it.")+flow("#1f617a","Four roles · 15 minutes","Preparation, responsibility, and scope differ.")+flow("#e3ad19","Read the pay label · 15 minutes","Circle May 2024, underline U.S., box median.")+flow("#1f617a","Comparison close · 5 minutes","Recommend a route with one table fact."),"MONITOR":"<p>Current source key: nursing assistant $39,530; LVN $62,340; RN $93,600; nurse practitioner $129,210. All are May 2024 U.S. medians. Do not call them starting or DFW pay.</p>","SUPPORT":"<p>Use role cards or highlight one preparation and one responsibility sentence. Accept oral rehearsal before writing.</p>","FALLBACK":"<p>The route guide is the full no-login route. Current Singley public evidence confirms Nursing Science but not a guaranteed credential.</p>"},
          2:{"TITLE":"Compare Nursing Education and Pay","SUBTITLE":"50 minutes · TEKS d(2)(A), d(2)(B), d(5)(E)","ALERT":"<strong>Do not turn the table into a forced ladder.</strong> Students may enter, stop, or change routes. A higher median does not erase time, cost, admission, license, or work-condition trade-offs.","PREP":f'<ul><li>Return the route guide.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["COMPARE"]["id"]}/preview">comparison and decision</a>.</li><li>Display the Texas Board of Nursing program-approval reminder.</li></ul>',"EVIDENCE":"<p>One four-role table plus one fictional-student recommendation using preparation, pay label, and a trade-off.</p>","FLOW":flow("#5a2d91","Decision-information warm-up · 5 minutes","Name the facts needed before choosing.")+flow("#4a9d2f","Finish four roles · 20 minutes","Use one consistent BLS salary basis.")+flow("#1f617a","Evaluate RN routes · 10 minutes","Associate and bachelor's routes; approval and licensure still matter.")+flow("#e3ad19","Recommend · 10 minutes","Use two facts and one trade-off.")+flow("#1f617a","Ranked close · 5 minutes","Defend Rank 1 and Rank 4."),"MONITOR":"<p>Full credit requires at least three careers in the salary comparison. Accept different recommendations when the evidence matches the fictional student's needs. Correct any claim that a degree guarantees a salary.</p>","SUPPORT":"<p>Offer the complete sentence frame and let students compare three roles before adding the fourth. Score evidence, not English mechanics.</p>","FALLBACK":"<p>All required facts are in the route guide. Calculators and live platforms are optional.</p>"},
          3:{"TITLE":"Build a Vital-Signs Training Simulator","SUBTITLE":"50 minutes · TEKS d(1)(C)","ALERT":"<strong>Simulation only.</strong> No student measurements, diagnoses, or medical-device claims. The physical micro:bit, browser simulator, and paper trace are equal routes.","PREP":f'<ul><li>Test MakeCode on the student network.</li><li>Open the workbook and tool-reference visuals.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["BUILD"]["id"]}/preview">build and test guide</a>.</li><li>Charge micro:bits only if using the optional hardware route.</li></ul>',"EVIDENCE":"<p>Collect the test record and screenshot, share link, or paper trace. Hardware access is not graded.</p>","FLOW":flow("#5a2d91","Measurement boundary · 5 minutes","Display is not measurement.")+flow("#4a9d2f","Tool research · 8 minutes","Match four tools to data.")+flow("#1f617a","Button A model · 10 minutes","Event, variable, random value, display, animation.")+flow("#e3ad19","Build and test · 22 minutes","Complete Button B and the three-checkpoint test.")+flow("#1f617a","Boundary close · 5 minutes","Explain why the program is not a medical device."),"MONITOR":"<p>Lap 1: Button A displays a value. Lap 2: Button B displays a temperature code. Lap 3: the student identifies the code, not a person, as the source. For the optional alert, &gt;100 displays R for report; it does not diagnose.</p>","SUPPORT":"<p>Provide a screenshot of Button A and let students build Button B. Pair a code reader and driver, but each student records the test explanation.</p>","FALLBACK":"<p>If MakeCode is blocked, use the paper block trace. If hardware is unavailable, remain in the browser simulator. Neither changes the score.</p>"},
          4:{"TITLE":"Document a Fictional Patient Handoff","SUBTITLE":"50 minutes · TEKS d(1)(C)","ALERT":"<strong>Fictional information only.</strong> Do not collect names, symptoms, temperatures, oxygen levels, blood pressure, or health histories from students. Record observations, not diagnoses.","PREP":f'<ul><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["CARDS"]["id"]}/preview">fictional cards</a>, <a href="/courses/{COURSE_ID}/files/{files["HANDOFF"]["id"]}/preview">handoff record</a>, and <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">rubric</a>.</li><li>Open the unpublished <a href="{quiz_url}">practice quiz</a>.</li><li>Decide whether the quiz or paper fallback fits the class.</li></ul>',"EVIDENCE":"<p>Collect one individual handoff. This is the recommended 16-point minor checkpoint when the gradebook groups are ready.</p>","FLOW":flow("#5a2d91","Observation or diagnosis · 5 minutes","Separate supplied fact from unsupported conclusion.")+flow("#4a9d2f","Five-part routine · 8 minutes","Situation, observations, comparison, handoff, reasoning.")+flow("#1f617a","Four case patterns · 17 minutes","Recovery, prompt symptoms, person plus numbers, conflicting device data.")+flow("#e3ad19","Individual handoff · 12 minutes","Use two case facts and a supervised next step.")+flow("#1f617a","Practice quiz and close · 8 minutes","Retry misconceptions; answer the device-quality mini-case."),"MONITOR":"<p>Card A shows recovery after rest. Card B requires prompt adult/emergency handoff in the scenario; do not diagnose. Card C requires the reported dizziness to remain in the handoff. Card D calls for device/process recheck and reporting the conflict. Quiz key: simulator displays coded values; record symptoms; recheck conflicting data; salary is a May 2024 U.S. median; verify Texas BON approval.</p>","SUPPORT":"<p>Color-code values, quoted symptoms, and inference. Use “The device displayed… The person reported… I would hand this to…”. A private written route is standard.</p>","FALLBACK":"<p>No equipment or partner is needed. Absent students use the same cards. Real health concerns follow the school nurse or emergency process, not the simulation.</p>"},
          5:{"TITLE":"Required Xello Save Careers","SUBTITLE":"50 minutes · TEKS d(1)(C)","ALERT":"<strong>Protect 30 minutes.</strong> The Grade 8 completion target is at least three saved careers. The Xello report is the completion record; paper reflection is temporary fallback only.","PREP":f'<ul><li>Confirm Xello launches through ClassLink.</li><li>Open the licensed <a href="/courses/{COURSE_ID}/files/{files["XELLO"]["id"]}/preview">My Careers teacher guide</a>.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["REFLECTION"]["id"]}/preview">Save Three Careers reflection</a>.</li><li>Open Completion Standards for the final check.</li></ul>',"EVIDENCE":"<p>Verify three saved careers in the Xello report and collect one individual comparison. Do not grade H&amp;L or eDynamic clicks.</p>","FLOW":flow("#5a2d91","Career and missing fact · 5 minutes","Name what still needs verification.")+flow("#4a9d2f","Xello Save careers · 30 minutes","Review and save at least three careers.")+flow("#1f617a","Individual comparison · 10 minutes","Fit, profile evidence, and next research question.")+flow("#e3ad19","Completion close · 5 minutes","Check saved list and report; record catch-up needs."),"MONITOR":"<p>At 15 minutes, each student should have at least one saved career and be reviewing another. Saving does not mean commitment. Accept careers from any cluster. Completion requires at least three saved careers.</p>","SUPPORT":"<p>Offer three teacher-selected career pages as the starting set. Use Xello audio and language support when available. Students may replace a suggested career after completing the minimum.</p>","FALLBACK":"<p>Access failure: complete the reflection with provided career data, record the student on the supervised catch-up list, and finish the Xello task later. H&amp;L/eDynamic are optional.</p>"}}
        pages={}; order=[]
        for day in range(1,6):
            st=titles[day]; student=await upsert_page(c,st,render(f"2sw-wk3-day{day}-student.html",{"COURSE_ID":COURSE_ID,**student_values[day]}),slugify(st))
            tt=f"TEACHER: 2SW Wk3 Day {day} Facilitator Guide"; teacher=await upsert_page(c,tt,render("2sw-wk3-teacher.html",{"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student["url"],**td[day]}),slugify(tt))
            await upsert_page_item(c,module_id,teacher,tt); await upsert_page_item(c,module_id,student,st); pages[day]={"teacher":teacher,"student":student}; order.extend([("Page",teacher["url"],tt),("Page",student["url"],st)])
            if day==4:
                await upsert_quiz_item(c,module_id,quiz); order.append(("Quiz",quiz["id"],QUIZ_TITLE))
        items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items")
        for position,(kind,key,title) in enumerate(order,start=1):
            item=next(i for i in items if (kind=="Page" and i.get("page_url")==key) or (kind=="Quiz" and i.get("content_id")==key))
            await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",data={"module_item[position]":position,"module_item[title]":title})
        final=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); questions=await paged(c,f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"); module=await api(c,"GET",f"/courses/{COURSE_ID}/modules/{module_id}")
        print(json.dumps({"module":{"id":module_id,"published":module["published"]},"quiz":{"id":quiz["id"],"published":quiz["published"],"type":quiz["quiz_type"],"questions":len(questions)},"folders":{"core":{"id":core["id"],"locked":core["locked"]},**{str(d):{"id":f["id"],"locked":f["locked"]} for d,f in folders.items()}},"files":{k:v["id"] for k,v in files.items()},"pages":{str(d):{k:{"url":v["url"],"published":v["published"]} for k,v in p.items()} for d,p in pages.items()},"items":[{"id":i["id"],"position":i["position"],"title":i["title"],"type":i["type"],"page_url":i.get("page_url"),"content_id":i.get("content_id")} for i in final]},indent=2))

asyncio.run(main())
