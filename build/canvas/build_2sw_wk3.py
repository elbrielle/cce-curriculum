"""Build the unpublished 2SW Week 3 teacher/student Canvas module and practice quiz."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
from urllib.parse import urlencode
import httpx

BASE="https://learn.irvingisd.net"; COURSE_ID=98060
MODULE_NAME="2SW Wk3: Nursing Science - Routes, Simulation, and Handoff"
QUIZ_TITLE="PRACTICE: Vital Signs and Handoff Check"
MODEL_QUIZ_TITLE="PRACTICE: Nursing Assistant and LVN Model Check"
ROUTE_QUIZ_TITLE="PRACTICE: Nursing Route Evidence Check"
MINOR_TITLE="MINOR 1: Nursing Route and Handoff"
ROOT=Path(__file__).resolve().parents[2]; TEMPLATES=Path(__file__).parent/"templates"; ASSETS=ROOT/"cce-curriculum/resources/canvas-licensed/2sw/wk3"

def slugify(v): return re.sub(r"[^a-z0-9]+","-",v.lower().replace("&","and")).strip("-")
def preferred_images(folder):
    return sorted(
        path
        for path in folder.iterdir()
        if path.suffix.lower() in {".png", ".jpg", ".jpeg"}
        and not (
            path.suffix.lower() == ".png"
            and (path.with_suffix(".jpg").exists() or path.with_suffix(".jpeg").exists())
        )
    )
async def api(c,m,p,**kw):
    r=await c.request(m,f"{BASE}/api/v1{p}",**kw); r.raise_for_status(); return r.json() if r.content else None
async def paged(c,p,params=None):
    out=[]; url=f"{BASE}/api/v1{p}"; q={"per_page":100,**(params or {})}
    while url:
        r=await c.get(url,params=q); r.raise_for_status(); out+=r.json(); url=r.links.get("next",{}).get("url"); q=None
    return out
async def ensure_module(c):
    modules=await paged(c,f"/courses/{COURSE_ID}/modules"); found=next((m for m in modules if m["name"]==MODULE_NAME),None)
    if found: return await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{found['id']}",data={"module[name]":MODULE_NAME,"module[published]":"false"})
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
    r=await c.post(init["upload_url"],data=init["upload_params"],files={"file":(path.name,path.read_bytes(),mimetypes.guess_type(path.name)[0] or "application/octet-stream")},follow_redirects=True); r.raise_for_status()
    uploaded=await api(c,"PUT",f"/files/{r.json()['id']}",data={"locked":"true"})
    if not uploaded.get("locked"):
        raise RuntimeError(f"Canvas did not lock uploaded file {path.name!r}")
    return uploaded

async def lock_folder_files(c,folder):
    current=await api(c,"GET",f"/folders/{folder['id']}")
    if not current.get("locked"):
        current=await api(c,"PUT",f"/folders/{folder['id']}",data={"locked":"true"})
    if not current.get("locked"):
        raise RuntimeError(f"Canvas did not lock folder {folder.get('full_name') or folder['id']}")
    for entry in await paged(c,f"/folders/{folder['id']}/files"):
        if not entry.get("locked"):
            await api(c,"PUT",f"/files/{entry['id']}",data={"locked":"true"})
    final=await paged(c,f"/folders/{folder['id']}/files")
    unlocked=[entry.get("display_name") or entry.get("filename") for entry in final if not entry.get("locked")]
    if unlocked:
        raise RuntimeError(f"Unlocked files remain in folder {folder['id']}: {unlocked}")
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
async def upsert_page_item(c,module_id,page,title):
    items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); item=next((i for i in items if i.get("page_url")==page["url"]),None)
    if item: return await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",data={"module_item[title]":title})
    return await api(c,"POST",f"/courses/{COURSE_ID}/modules/{module_id}/items",data={"module_item[type]":"Page","module_item[page_url]":page["url"],"module_item[title]":title})
async def upsert_subheader(c,module_id,title):
    items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); item=next((i for i in items if i.get("type")=="SubHeader" and i.get("title")==title),None)
    if item: return item
    return await api(c,"POST",f"/courses/{COURSE_ID}/modules/{module_id}/items",data={"module_item[type]":"SubHeader","module_item[title]":title,"module_item[indent]":"0"})

async def upsert_assignment_item(c,module_id,assignment):
    items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items")
    item=next((i for i in items if i.get("type")=="Assignment" and i.get("content_id")==assignment["id"]),None)
    if item:
        return await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",data={"module_item[title]":MINOR_TITLE})
    return await api(c,"POST",f"/courses/{COURSE_ID}/modules/{module_id}/items",data={"module_item[type]":"Assignment","module_item[content_id]":assignment["id"],"module_item[title]":MINOR_TITLE})

async def require_minor_preflight(c):
    assignments=await paged(c,f"/courses/{COURSE_ID}/assignments")
    matches=[entry for entry in assignments if entry.get("name")==MINOR_TITLE]
    if len(matches)!=1:
        raise RuntimeError(f"Expected one existing mapped Minor assignment named {MINOR_TITLE!r}; found {len(matches)}")
    found=matches[0]
    if float(found.get("points_possible") or 0)!=100:
        raise RuntimeError(f"Refusing to modify {MINOR_TITLE!r}: expected 100 points, found {found.get('points_possible')}")
    groups=await paged(c,f"/courses/{COURSE_ID}/assignment_groups")
    group=next((entry for entry in groups if entry.get("id")==found.get("assignment_group_id")),None)
    if not group or group.get("name")!="Minor Assessments (40%)":
        raise RuntimeError(f"Refusing to modify {MINOR_TITLE!r}: expected Minor Assessments (40%) group")
    return found

async def update_minor_assignment(c,assignment,description,attachment_id):
    existing=assignment.get("description") or ""
    note=re.search(r'<div data-cce-rubric-note="cce-advisory-rubric-v1".*?</div>',existing,flags=re.DOTALL)
    if note and "cce-advisory-rubric-v1" not in description:
        description=description.rstrip()+note.group(0)
    updated=await api(c,"PUT",f"/courses/{COURSE_ID}/assignments/{assignment['id']}",data={
        "assignment[name]":MINOR_TITLE,
        "assignment[description]":description,
        "assignment[published]":"false",
        "assignment[points_possible]":"100",
        "assignment[grading_type]":"points",
        "assignment[submission_types][]":["student_annotation","online_upload","online_text_entry","media_recording"],
        "assignment[annotatable_attachment_id]":str(attachment_id),
    })
    if updated.get("published") or float(updated.get("points_possible") or 0)!=100:
        raise RuntimeError(f"Mapped Minor invariant failed for {MINOR_TITLE!r}")
    return updated

async def prepare_quiz_questions(c,quiz_id,desired_names):
    existing=await paged(c,f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions")
    keep=[]; seen=set()
    for question in existing:
        name=question.get("question_name")
        if name not in desired_names or name in seen:
            await api(c,"DELETE",f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions/{question['id']}")
        else:
            seen.add(name); keep.append(question)
    return keep

async def finalize_quiz_order(c,quiz_id,expected_names):
    final=await paged(c,f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions")
    by_name={entry.get("question_name"):entry for entry in final}
    if set(by_name)!=set(expected_names) or len(final)!=len(expected_names):
        raise RuntimeError(f"Quiz {quiz_id} question mismatch: {[entry.get('question_name') for entry in final]}")
    fields=[]
    for name in expected_names:
        fields.extend([("order[][id]",str(by_name[name]["id"])),("order[][type]","question")])
    await api(c,"POST",f"/courses/{COURSE_ID}/quizzes/{quiz_id}/reorder",content=urlencode(fields),headers={"Content-Type":"application/x-www-form-urlencoded"})
    ordered=await paged(c,f"/courses/{COURSE_ID}/quizzes/{quiz_id}/questions")
    actual=[entry.get("question_name") for entry in ordered]
    if actual!=expected_names:
        raise RuntimeError(f"Quiz {quiz_id} order mismatch: expected {expected_names}, found {actual}")

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
    expected=[spec["name"] for spec in QUIZ_QUESTIONS]
    existing=await prepare_quiz_questions(c,quiz["id"],set(expected))
    for position,spec in enumerate(QUIZ_QUESTIONS,start=1):
        found=next((q for q in existing if q.get("question_name")==spec["name"]),None)
        answers=[{"answer_text":spec["correct"],"answer_weight":100}]+[{"answer_text":v,"answer_weight":0} for v in spec["wrong"]]
        payload={"question":{"question_name":spec["name"],"question_text":spec["text"],"question_type":"multiple_choice_question","position":position,"points_possible":1,"correct_comments":spec["correct_comment"],"incorrect_comments":spec["incorrect_comment"],"answers":answers}}
        await api(c,"PUT" if found else "POST",f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions",json=payload)
    await finalize_quiz_order(c,quiz["id"],expected)
    return await api(c,"GET",f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
async def upsert_quiz_item(c,module_id,quiz):
    items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); item=next((i for i in items if i.get("type")=="Quiz" and i.get("content_id")==quiz["id"]),None)
    title=quiz["title"]
    if item: return await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",data={"module_item[title]":title})
    return await api(c,"POST",f"/courses/{COURSE_ID}/modules/{module_id}/items",data={"module_item[type]":"Quiz","module_item[content_id]":quiz["id"],"module_item[title]":title})

ROUTE_QUIZ_QUESTIONS=[
  {"name":"Q1 - Order the evidence","type":"multiple_choice_question","text":"Which sequence orders the four May 2024 U.S. median wages from lowest to highest?","correct":"Nursing assistant $39,530; LVN $62,340; RN $93,600; nurse practitioner $129,210","wrong":["LVN $62,340; nursing assistant $39,530; nurse practitioner $129,210; RN $93,600","Nursing assistant $39,530; RN $93,600; LVN $62,340; nurse practitioner $129,210","RN $93,600; LVN $62,340; nursing assistant $39,530; nurse practitioner $129,210"]},
  {"name":"Q2 - Preparation difference","type":"essay_question","text":"Name one preparation difference between the RN and nurse practitioner routes. Use the frame if it helps: An RN commonly ________, while a nurse practitioner must also ________."},
  {"name":"Q3 - Responsibility difference","type":"essay_question","text":"Name one responsibility difference. Do not say only that one role has more responsibility. Use the frame if it helps: The RN is responsible for ________. In contrast, the nurse practitioner ________."},
  {"name":"Q4 - Verify before choosing","type":"multiple_choice_question","text":"Which set contains facts Avery should verify before choosing an RN program?","correct":"Program approval, length, cost and aid, admission, transfer options, and employer preferences","wrong":["Only the highest advertised salary","A promise that every graduate gets a job","Whether the program lets students skip licensure"]},
  {"name":"Q5 - Recommend with evidence","type":"essay_question","text":"Choose Jordan, Avery, or Sam. Recommend one nursing route. Include preparation or license evidence, the pay figure with year/geography/measure, and one trade-off or fact to verify. Frame: I recommend ________ for ________ because ________. The pay evidence is ________. One trade-off or fact to verify is ________."}
]

async def upsert_route_quiz(c):
    quizzes=await paged(c,f"/courses/{COURSE_ID}/quizzes"); quiz=next((q for q in quizzes if q.get("title")==ROUTE_QUIZ_TITLE),None)
    description='''<div style="max-width:820px"><p><strong>Canvas-first response:</strong> use the route guide and the evidence on this page. The printable packet is an optional access or no-device fallback, not a required class set.</p><div style="border-left:5px solid #f3c63c;background:#fff8dd;padding:10px 14px"><strong>Comparison words:</strong> both · while · however · requires · higher/lower · a key difference · in contrast<br><strong>Decision words:</strong> advantage · trade-off · verify · official source</div><p>Questions 2, 3, and 5 are read by the teacher. Complete thoughts matter more than English mechanics when meaning is clear.</p></div>'''
    data={"quiz[title]":ROUTE_QUIZ_TITLE,"quiz[description]":description,"quiz[quiz_type]":"practice_quiz","quiz[published]":"false","quiz[allowed_attempts]":"-1","quiz[show_correct_answers]":"true","quiz[shuffle_answers]":"false"}
    quiz=await api(c,"PUT" if quiz else "POST",f"/courses/{COURSE_ID}/quizzes/{quiz['id']}" if quiz else f"/courses/{COURSE_ID}/quizzes",data=data)
    expected=[spec["name"] for spec in ROUTE_QUIZ_QUESTIONS]
    existing=await prepare_quiz_questions(c,quiz["id"],set(expected))
    for position,spec in enumerate(ROUTE_QUIZ_QUESTIONS,start=1):
        found=next((q for q in existing if q.get("question_name")==spec["name"]),None)
        answers=[]
        if spec["type"]=="multiple_choice_question":
            answers=[{"answer_text":spec["correct"],"answer_weight":100}]+[{"answer_text":v,"answer_weight":0} for v in spec["wrong"]]
        payload={"question":{"question_name":spec["name"],"question_text":spec["text"],"question_type":spec["type"],"position":position,"points_possible":1,"answers":answers}}
        await api(c,"PUT" if found else "POST",f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions",json=payload)
    await finalize_quiz_order(c,quiz["id"],expected)
    return await api(c,"GET",f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")

async def upsert_model_quiz(c):
    quizzes=await paged(c,f"/courses/{COURSE_ID}/quizzes"); quiz=next((q for q in quizzes if q.get("title")==MODEL_QUIZ_TITLE),None)
    description='''<p><strong>Day 1 model check:</strong> use the completed nursing assistant model and the LVN evidence bank. This short Canvas check replaces routine packet printing. Use the print scaffold only when paper is the better access route.</p><p><strong>Words:</strong> preparation · responsibility · median · verify</p>'''
    data={"quiz[title]":MODEL_QUIZ_TITLE,"quiz[description]":description,"quiz[quiz_type]":"practice_quiz","quiz[published]":"false","quiz[allowed_attempts]":"-1","quiz[show_correct_answers]":"true","quiz[shuffle_answers]":"false"}
    quiz=await api(c,"PUT" if quiz else "POST",f"/courses/{COURSE_ID}/quizzes/{quiz['id']}" if quiz else f"/courses/{COURSE_ID}/quizzes",data=data)
    specs=[
      {"name":"Q1 - Mark the LVN evidence","type":"multiple_choice_question","text":"Which answer labels the LVN evidence correctly?","correct":"Preparation: state-approved vocational nursing program and licensure; Pay: $62,340 May 2024 U.S. median; Responsibility: provide basic medical care and document patient status","wrong":["Preparation: $62,340; Pay: document patient status; Responsibility: vocational nursing program","Preparation: provide basic care; Pay: vocational nursing program; Responsibility: $62,340","Preparation: guaranteed job; Pay: guaranteed starting wage; Responsibility: skip licensure"]},
      {"name":"Q2 - Compare the routes","type":"essay_question","text":"What changes from the nursing assistant route to the LVN route? Use the frame if it helps: The LVN route requires ________, while the nursing assistant route ________."}
    ]
    expected=[spec["name"] for spec in specs]
    existing=await prepare_quiz_questions(c,quiz["id"],set(expected))
    for position,spec in enumerate(specs,start=1):
        found=next((q for q in existing if q.get("question_name")==spec["name"]),None); answers=[]
        if spec["type"]=="multiple_choice_question": answers=[{"answer_text":spec["correct"],"answer_weight":100}]+[{"answer_text":v,"answer_weight":0} for v in spec["wrong"]]
        payload={"question":{"question_name":spec["name"],"question_text":spec["text"],"question_type":spec["type"],"position":position,"points_possible":1,"answers":answers}}
        await api(c,"PUT" if found else "POST",f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{found['id']}" if found else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions",json=payload)
    await finalize_quiz_order(c,quiz["id"],expected)
    return await api(c,"GET",f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")
def flow(color,title,text): return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'

async def main():
    opener=ASSETS/"day1/health-science-opener.jpg"
    if not opener.is_file():
        raise FileNotFoundError(f"2SW Wk3 preflight missing required delivery image: {opener}")
    token=sys.stdin.readline().strip()
    if not token: raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"},timeout=120) as c:
        minor=await require_minor_preflight(c)
        module=await ensure_module(c); module_id=module["id"]; quiz=await upsert_quiz(c); model_quiz=await upsert_model_quiz(c); route_quiz=await upsert_route_quiz(c)
        names={"ROUTE":"2sw-wk3-nursing-route-guide.pdf","COMPARE":"2sw-wk3-nursing-route-comparison.pdf","BUILD":"2sw-wk3-vital-signs-simulator-build.pdf","CARDS":"2sw-wk3-fictional-patient-cards.pdf","HANDOFF":"2sw-wk3-clinical-handoff-record.pdf","RUBRIC":"2sw-wk3-handoff-rubric.pdf","REFLECTION":"2sw-wk3-xello-save-careers-reflection.pdf"}
        support_folder="course files/CCR Materials/2SW/Wk3"; core=await ensure_folder(c,support_folder); files={k:await upload(c,ROOT/"docs/resources/worksheets"/v,support_folder) for k,v in names.items()}
        files["XELLO"]=await upload(c,ROOT/"cce-curriculum/resources/xello-licensed/prerequisites/careers.pdf",support_folder)
        uploads={}; folders={}
        for day in range(1,6):
            fp=f"course files/CCR Materials/2SW/Wk3/Day {day} Visuals"; folders[day]=await ensure_folder(c,fp); uploads[day]={}
            for path in preferred_images(ASSETS/f"day{day}"): uploads[day][path.name]=await upload(c,path,fp)
        await lock_folder_files(c,core)
        for folder in folders.values():
            await lock_folder_files(c,folder)
        minor_description=f'''<div style="max-width:860px;margin:0 auto;font-family:Arial,Helvetica,sans-serif;line-height:1.5;color:#24323d">
  <h2 style="color:#5a2d91">Nursing Route and Handoff</h2>
  <div style="border:1px solid #bad4df;border-radius:9px;background:#f2f8fb;padding:14px 18px">
    <p><strong>Evidence already completed:</strong> your Day 2 Nursing Route Evidence Check and your Day 4 fictional clinical handoff.</p>
    <p><strong>Do not redo the route Quiz.</strong> Submit only the Day 4 handoff here. Your teacher uses the Day 2 Quiz for route accuracy and trade-off reasoning, then this handoff for observation and evidence.</p>
  </div>
  <h3>Submit your handoff</h3>
  <p>Annotate the attached handoff record, upload a completed copy or clear image, type the five labeled parts, or use an approved audio/AAC response with the same evidence jobs.</p>
  <h3>Before submitting</h3>
  <ul><li>Use only the supplied fictional case.</li><li>Separate displayed values, reported symptoms, and unsupported inference.</li><li>Name the supervised nursing-related role receiving or using the handoff.</li><li>Use at least two case facts and explain why they matter.</li></ul>
  <p><a href="/courses/{COURSE_ID}/files/{files['RUBRIC']['id']}/preview">Open the 16-point scoring guide</a>.</p>
</div>'''
        minor=await update_minor_assignment(c,minor,minor_description,files["HANDOFF"]["id"])
        minor_url=f"/courses/{COURSE_ID}/assignments/{minor['id']}"
        quiz_url=f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"; model_quiz_url=f"/courses/{COURSE_ID}/quizzes/{model_quiz['id']}"; route_quiz_url=f"/courses/{COURSE_ID}/quizzes/{route_quiz['id']}"
        student_values={
          1:{"OPENER_IMAGE_ID":uploads[1]["health-science-opener.jpg"]["id"],"PROGRAM_IMAGE_ID":uploads[1]["irving-health-programs.png"]["id"],"ROUTE_FILE_ID":files["ROUTE"]["id"],"COMPARE_FILE_ID":files["COMPARE"]["id"],"MODEL_QUIZ_URL":model_quiz_url},
          2:{"COMPARE_FILE_ID":files["COMPARE"]["id"],"ROUTE_FILE_ID":files["ROUTE"]["id"],"ROUTE_QUIZ_URL":route_quiz_url},
          3:{"BUILD_FILE_ID":files["BUILD"]["id"],"RESEARCH_IMAGE_ID":uploads[3]["vitals-research.png"]["id"],"TOOLS_IMAGE_ID":uploads[3]["vitals-tool-reference.png"]["id"]},
          4:{"CARDS_FILE_ID":files["CARDS"]["id"],"HANDOFF_FILE_ID":files["HANDOFF"]["id"],"RUBRIC_FILE_ID":files["RUBRIC"]["id"],"REPORT_IMAGE_ID":uploads[4]["vitals-report.png"]["id"],"QUIZ_URL":quiz_url,"MINOR_URL":minor_url},
          5:{"REFLECTION_FILE_ID":files["REFLECTION"]["id"],"APP_IMAGE_ID":uploads[5]["health-science-app.png"]["id"]}}
        titles={1:"STUDENT: 2SW Wk3 Day 1 - Compare Nursing Routes",2:"STUDENT: 2SW Wk3 Day 2 - Choose with Evidence",3:"STUDENT: 2SW Wk3 Day 3 - Build a Training Simulator",4:"STUDENT: 2SW Wk3 Day 4 - Write a Careful Handoff",5:"STUDENT: 2SW Wk3 Day 5 - Save Three Careers"}
        td={
          1:{"TITLE":"Health Science and Nursing Routes","SUBTITLE":"50 minutes · TEKS d(1)(B), d(1)(C)","ALERT":"<strong>Keep each source label attached.</strong> FYF pp. 84-85 are the assigned district-customized HQIM snapshot. The current Singley Academy webpage is a separately dated cross-check. A difference does not make the workbook response wrong or guarantee a student outcome.","PREP":f'<ul><li>Open the two embedded workbook visuals and display the <a href="/courses/{COURSE_ID}/files/{files["ROUTE"]["id"]}/preview">route guide</a>.</li><li>Open the <a href="{model_quiz_url}">two-question Canvas model check</a>.</li><li>Keep pages 1-2 of the <a href="/courses/{COURSE_ID}/files/{files["COMPARE"]["id"]}/preview">print scaffold</a> available only as an access fallback.</li><li><strong>Default printing: none.</strong></li></ul>',"EVIDENCE":"<p>Review the two-question Canvas model check: one correct LVN evidence classification and one nursing-assistant/LVN comparison. Pay facts must retain year, geography, and measure. Accept pages 1-2 of the print scaffold under the same criteria.</p>","FLOW":flow("#5a2d91","Healthcare worker warm-up · 5 minutes","List roles beyond physician and name one task.")+flow("#4a9d2f","Health fair decision · 10 minutes","Connect one booth to the worker who staffs it.")+flow("#1f617a","See one and try one · 15 minutes","Use the completed nursing assistant model, then guide the LVN evidence marks.")+flow("#e3ad19","Read the pay label · 15 minutes","Circle May 2024, underline U.S., box median, then complete the Canvas model check.")+flow("#1f617a","Comparison close · 5 minutes","Rehearse one route difference before submitting."),"MONITOR":"<p>Source key: nursing assistant $39,530; LVN $62,340; RN $93,600; nurse practitioner $129,210. All are May 2024 U.S. medians. Do not call them starting or DFW pay. The LVN evidence marks are P for program/licensure, $ for the median, and R for the responsibility.</p>","SUPPORT":"<p>Use the completed model before the Canvas check. Let students rehearse Question 2 with a partner, then submit their own response. Keep preparation/preparación and responsibility/responsabilidad visible. Score the evidence difference, not English mechanics.</p>","FALLBACK":"<p>If Canvas is unavailable, use pages 1-2 of the print scaffold. The assigned FYF page remains valid HQIM; a current website check is a separate source note.</p>"},
          2:{"TITLE":"Compare Nursing Education and Pay","SUBTITLE":"50 minutes · TEKS d(2)(A), d(2)(B), d(5)(E)","ALERT":"<strong>Canvas is the default response surface.</strong> Do not print the four-page comparison as a class set. Use it only as an optional print/access fallback. Do not turn the routes into a forced ladder.","PREP":f'<ul><li>Open the route guide beside the <a href="{route_quiz_url}">Nursing Route Evidence Check</a>.</li><li>Keep the <a href="/courses/{COURSE_ID}/files/{files["COMPARE"]["id"]}/preview">four-page scaffold</a> available only for students who need or prefer print.</li><li>Display the Texas Board of Nursing program-approval reminder.</li><li><strong>Default printing: none.</strong></li></ul>',"EVIDENCE":"<p>Review the Canvas response for the four-career order, two evidence differences, RN route check, and fictional-student recommendation. Accept the optional print version under the same success criteria.</p>","FLOW":flow("#5a2d91","Decision-information warm-up · 5 minutes","Name the facts needed before choosing.")+flow("#4a9d2f","Compare independently · 20 minutes","Use the route guide and Canvas check to order all four medians and explain two differences.")+flow("#1f617a","Evaluate RN routes · 10 minutes","Use Avery's priorities to choose a route to investigate first and name a fact to verify.")+flow("#e3ad19","Recommend · 10 minutes","Use preparation, pay, and one trade-off or unanswered question.")+flow("#1f617a","Ranked close · 5 minutes","Defend Rank 1 and Rank 4."),"MONITOR":"<p>Full credit requires at least three careers in the salary comparison. Accept different recommendations when the evidence matches the fictional student's needs. Correct any claim that a degree guarantees a salary. For the RN route check, program approval is required; length, cost, admission, transfer, and employer preferences still need a current program-specific source.</p>","SUPPORT":"<p>Keep the point-of-use word banks and complete frames visible in the Canvas check. Students may rehearse Questions 2, 3, and 5 orally before typing. Offer the four-page scaffold only when print or enlarged handwriting space improves access. Score evidence, not English mechanics.</p>","FALLBACK":"<p>If Canvas is unavailable, use the four-page scaffold. All required facts are in the route cards and guide; no Xello or H&amp;L login is required for this DOL.</p>"},
          3:{"TITLE":"Build a Vital-Signs Training Simulator","SUBTITLE":"50 minutes · TEKS d(1)(C)","ALERT":"<strong>Simulation only.</strong> No student measurements, diagnoses, or medical-device claims. The physical micro:bit, browser simulator, and paper trace are equal routes.","PREP":f'<ul><li>Test MakeCode on the student network and open the completed Button A model already embedded in the Student Guide.</li><li><strong>Default grouping:</strong> pairs, one connected device per pair. Use one optional micro:bit per pair only when hardware is ready; the browser simulator is the default.</li><li>Post the <a href="/courses/{COURSE_ID}/files/{files["BUILD"]["id"]}/preview">two-page build and test guide</a>. Provide one copy per student only when paper is the response route.</li><li>Assign Driver and Code Reader. Switch roles after Button A passes.</li></ul>',"EVIDENCE":"<p>Collect one test record per student plus one screenshot/share link per pair, or one completed paper block trace per student. Hardware access is not graded.</p>","FLOW":flow("#5a2d91","Measurement boundary · 4 minutes","Display is not measurement.")+flow("#4a9d2f","Tool research · 6 minutes","Match four tools to data.")+flow("#1f617a","Button A model · 8 minutes","Read the supplied model top to bottom; test once.")+flow("#e3ad19","Build, switch, and test · 21 minutes","Driver builds A; switch roles for B; run the four checks.")+flow("#1f617a","Explain and collect · 7 minutes","Save one team artifact; each student completes the boundary and career explanation.")+flow("#24323d","Cleanup · 4 minutes","Confirm links/screenshots, return hardware, close MakeCode, and collect paper records."),"MONITOR":"<p><strong>Lap 1—Button A:</strong> target = event, fictional-value variable, and display blocks in sequence. Feedback: “Point to the block that creates the value.” If three or more pairs cannot identify it, pause and reread the embedded model top to bottom. <strong>Lap 2—Button B:</strong> target = 970-1005 range and a displayed temperature code. If several students type 97-100.5, model why this micro:bit build uses whole-number codes. <strong>Lap 3—Explanation:</strong> target = code as the source, not a person. If students claim measurement or diagnosis, return to the boundary frame before collection.</p><p><strong>Safe trim:</strong> cut the optional &gt;100 alert and pulse animation refinement first. Protect both button tests, the simulator boundary, and the nursing-role connection.</p>","SUPPORT":"<p>The Student Guide supplies the completed Button A visual, point-of-use words, and a full test/revision frame. Partners may rehearse the boundary explanation, but each student records a complete thought. Do not make the Code Reader a passive observer; that student points to the next block and checks the test record.</p>","FALLBACK":"<p>MakeCode failure: use the completed paper block trace in the same two-page guide and test the written sequence against the same four checks. Hardware failure: remain in the browser simulator. Recovery: rename the project, take a screenshot before closing, and copy the share link into the assigned submission or class collection location. Neither route changes the score.</p>"},
          4:{"TITLE":"Document a Fictional Patient Handoff","SUBTITLE":"50 minutes · TEKS d(1)(C)","ALERT":"<strong>Fictional information only.</strong> Do not collect names, symptoms, temperatures, oxygen levels, blood pressure, or health histories from students. Record observations, not diagnoses.","PREP":f'<ul><li><strong>Default grouping:</strong> pairs for card analysis; individual writing for the handoff.</li><li>Print one four-card <a href="/courses/{COURSE_ID}/files/{files["CARDS"]["id"]}/preview">fictional-card set</a> per eight students (four pairs), cut into four cards. Print one two-page <a href="/courses/{COURSE_ID}/files/{files["HANDOFF"]["id"]}/preview">handoff record</a> per student.</li><li>Project the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">rubric</a>; print individual rubric copies only when students will mark them.</li><li>Open the unpublished <a href="{quiz_url}">practice quiz</a>. Use it after the handoff, not as a replacement.</li></ul>',"EVIDENCE":"<p>Collect one individual handoff per student. One pair may share a card, but not a response. This is the recommended 16-point minor checkpoint when the gradebook groups are ready.</p>","FLOW":flow("#5a2d91","Observation or diagnosis · 5 minutes","Stop and jot, then compare supplied fact with unsupported conclusion.")+flow("#4a9d2f","Five-part model · 8 minutes","Model one Card A line with the supplied complete frame.")+flow("#1f617a","Pair case analysis · 14 minutes","Read one assigned card; partners identify facts and likely inference.")+flow("#e3ad19","Individual handoff · 13 minutes","Use two case facts and a supervised next step.")+flow("#1f617a","Practice and revise · 7 minutes","Use quiz feedback or the misconception check to revise one sentence.")+flow("#24323d","Collect · 3 minutes","Attach the card letter, submit the individual record, and return reusable cards."),"MONITOR":"<p><strong>Lap 1—evidence sort:</strong> target = values and exact reported words are marked separately from inference. Feedback: “Which words came directly from the card?” If several pairs diagnose, pause and revise one statement together. <strong>Lap 2—handoff:</strong> target = two case facts, a supervised receiver, and no diagnosis. If several students omit the person’s report, display the complete frame and require that sentence before they continue. <strong>Lap 3—reasoning:</strong> target = action supported by two facts, not urgency guessed from one number.</p><p>Card A = recovery after rest. Card B = prompt supervised handoff without diagnosis. Card C = retain the reported dizziness. Card D = recheck the device/process and report the conflict. <strong>Safe trim:</strong> cut or move the practice quiz to the next opening; protect the individual handoff and one evidence-based revision.</p>","SUPPORT":"<p>The complete handoff frame and bilingual terms now sit beside the five-part routine in the Student Guide. Color-code values, quoted symptoms, and inference. Students may rehearse with a partner or use speech-to-text, but submit a private individual response. Score evidence, not English mechanics.</p>","FALLBACK":"<p>No equipment is needed. Absent students use one fictional card and the same individual record. If printing is unavailable, students type the five labeled parts in Canvas. Real health concerns follow the school nurse or emergency process, not the simulation.</p>"},
          5:{"TITLE":"Required Xello Save Careers","SUBTITLE":"50 minutes · TEKS d(1)(C)","ALERT":"<strong>Protect 30 minutes.</strong> The Grade 8 completion target is at least three saved careers. The Xello report is the completion record; paper reflection is temporary fallback only.","PREP":f'<ul><li>Confirm Xello launches through ClassLink and open Completion Standards before class.</li><li><strong>Default grouping:</strong> individual work, one device per student. Seat a peer navigator nearby when a student needs navigation support; students still save in their own accounts.</li><li>Open the licensed <a href="/courses/{COURSE_ID}/files/{files["XELLO"]["id"]}/preview">My Careers teacher guide</a>. Preselect three varied career pages as a recovery starting set.</li><li>Provide one <a href="/courses/{COURSE_ID}/files/{files["REFLECTION"]["id"]}/preview">Save Three Careers reflection</a> per student as paper or digital annotation. Do not print a second packet.</li></ul>',"EVIDENCE":"<p>Verify at least three saved careers per student in the Xello report and collect one individual comparison. Record access/catch-up needs before students leave. Do not grade H&amp;L or eDynamic clicks.</p>","FLOW":flow("#5a2d91","Launch and missing fact · 5 minutes","Open Xello and name what still needs verification.")+flow("#4a9d2f","Xello Save careers · 30 minutes","Review and save at least three careers.")+flow("#1f617a","Individual comparison · 9 minutes","Use the supplied frame for fit, evidence, and the next fact.")+flow("#e3ad19","Verify and collect · 4 minutes","Check the report; collect reflection; record catch-up.")+flow("#24323d","Close · 2 minutes","Confirm saves, sign out, and close personal account screens."),"MONITOR":"<p><strong>Minute 10:</strong> target = each student has opened a career detail page. If several students remain on the dashboard, pause for one navigation reset. <strong>Minute 15:</strong> target = one saved career. If not, move the student to a teacher-selected page and check the Save control. <strong>Minute 30:</strong> target = at least three saved careers or a named access barrier on the catch-up list. <strong>Final check:</strong> use the Completion Standards report; a screenshot or paper reflection is not platform completion.</p><p><strong>Safe trim:</strong> shorten the comparison to one career, one evidence statement, and one fact to verify. Do not cut the 30-minute Xello block or the report/catch-up check.</p>","SUPPORT":"<p>The point-of-use comparison frame is visible beside the reflection link. Offer three teacher-selected career pages as the starting set, Xello audio/language support when available, and a peer navigator who does not control the account. Students may replace a suggested career after completing the minimum.</p>","FALLBACK":"<p>Access failure: complete the one-page reflection with the provided career data, record the exact barrier on the supervised catch-up list, and finish the Xello task later. At the catch-up window, recheck the Completion Standards report. H&amp;L/eDynamic are optional.</p>"}}
        contracts={
          1:{"TOPIC":"Health Science Careers","OBJECTIVE":"Students will describe the Health Science cluster and identify nursing-related career opportunities by comparing preparation and responsibility evidence.","TEKS":"d(1)(B), d(1)(C)","DOL":"Completed two-question Canvas nursing assistant/LVN model check or pages 1-2 of the optional print scaffold."},
          2:{"TOPIC":"Nursing Route Choices","OBJECTIVE":"Students will compare preparation requirements and salaries across four nursing-related careers and evaluate two RN education routes using source-labeled evidence.","TEKS":"d(2)(A), d(2)(B), d(5)(E)","DOL":"Completed Canvas Nursing Route Evidence Check or optional print scaffold."},
          3:{"TOPIC":"Training Simulation","OBJECTIVE":"Students will identify how nursing workers use monitored data by building and testing a fictional simulator and explaining the career connection.","TEKS":"d(1)(C)","DOL":"Vital Signs Simulator Build and Test record, nursing-work connection, and screenshot, share link, or paper trace."},
          4:{"TOPIC":"Clinical Handoff","OBJECTIVE":"Students will identify a nursing documentation and handoff responsibility by separating supplied observations, reported symptoms, and unsupported inference.","TEKS":"d(1)(C)","DOL":"Individual Observation and Clinical Handoff Record with a named nursing-role connection."},
          5:{"TOPIC":"Saved Career Evidence","OBJECTIVE":"Students will identify at least three career opportunities in Xello and explain one current fit using task, preparation, work-condition, or profile evidence.","TEKS":"d(1)(C)","DOL":"Xello record with at least three saved careers plus Xello Save Three Careers Reflection."}}
        pages={}
        for day in range(1,6):
            st=titles[day]; student=await upsert_page(c,st,render(f"2sw-wk3-day{day}-student.html",{"COURSE_ID":COURSE_ID,**student_values[day]}),slugify(st))
            tt=f"TEACHER: 2SW Wk3 Day {day} Facilitator Guide"; teacher=await upsert_page(c,tt,render("2sw-wk3-teacher.html",{"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student["url"],**contracts[day],**td[day]}),slugify(tt))
            await upsert_page_item(c,module_id,teacher,tt); await upsert_page_item(c,module_id,student,st); await upsert_subheader(c,module_id,f"Day {day}"); pages[day]={"teacher":teacher,"student":student}
            if day==1: await upsert_quiz_item(c,module_id,model_quiz)
            if day==2: await upsert_quiz_item(c,module_id,route_quiz)
            if day==4:
                await upsert_quiz_item(c,module_id,quiz)
                await upsert_assignment_item(c,module_id,minor)
        order=[]
        for day in range(1,6):
            order.append(("SubHeader",f"Day {day}",f"Day {day}"))
            order.append(("Page",pages[day]["teacher"]["url"],f"TEACHER: 2SW Wk3 Day {day} Facilitator Guide"))
            order.append(("Page",pages[day]["student"]["url"],titles[day]))
            if day==1:
                order.append(("Quiz",model_quiz["id"],MODEL_QUIZ_TITLE))
            if day==2:
                order.append(("Quiz",route_quiz["id"],ROUTE_QUIZ_TITLE))
            if day==4:
                order.append(("Quiz",quiz["id"],QUIZ_TITLE))
                order.append(("Assignment",minor["id"],MINOR_TITLE))

        def matches_item(entry,kind,key):
            return entry.get("type")==kind and (
                (kind=="SubHeader" and entry.get("title")==key)
                or (kind=="Page" and entry.get("page_url")==key)
                or (kind in {"Quiz","Assignment"} and entry.get("content_id")==key)
            )

        items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items")
        keep_ids=set()
        for kind,key,_title in order:
            match=next((entry for entry in items if entry["id"] not in keep_ids and matches_item(entry,kind,key)),None)
            if not match:
                raise RuntimeError(f"Missing expected module item: {kind} {key}")
            keep_ids.add(match["id"])
        for entry in items:
            if entry["id"] not in keep_ids:
                await api(c,"DELETE",f"/courses/{COURSE_ID}/modules/{module_id}/items/{entry['id']}")
        items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items")
        for position,(kind,key,title) in enumerate(order,start=1):
            item=next(entry for entry in items if matches_item(entry,kind,key))
            await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",data={"module_item[position]":position,"module_item[title]":title})
        final=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); questions=await paged(c,f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions"); model_questions=await paged(c,f"/courses/{COURSE_ID}/quizzes/{model_quiz['id']}/questions"); route_questions=await paged(c,f"/courses/{COURSE_ID}/quizzes/{route_quiz['id']}/questions"); module=await api(c,"GET",f"/courses/{COURSE_ID}/modules/{module_id}")
        if module.get("published"):
            raise RuntimeError("Week 3 module unexpectedly published")
        if len(final)!=len(order):
            raise RuntimeError(f"Expected {len(order)} Week 3 module items; found {len(final)}")
        ordered=sorted(final,key=lambda entry:entry.get("position",0))
        for position,((kind,key,_title),entry) in enumerate(zip(order,ordered),start=1):
            if entry.get("position")!=position or not matches_item(entry,kind,key):
                raise RuntimeError(f"Week 3 module order mismatch at position {position}")
        print(json.dumps({"module":{"id":module_id,"published":module["published"]},"quizzes":{"model":{"id":model_quiz["id"],"published":model_quiz["published"],"type":model_quiz["quiz_type"],"questions":len(model_questions)},"route":{"id":route_quiz["id"],"published":route_quiz["published"],"type":route_quiz["quiz_type"],"questions":len(route_questions)},"handoff":{"id":quiz["id"],"published":quiz["published"],"type":quiz["quiz_type"],"questions":len(questions)}},"minor":{"id":minor["id"],"published":minor["published"],"points":minor["points_possible"],"group":minor["assignment_group_id"]},"folders":{"core":{"id":core["id"],"locked":core["locked"]},**{str(d):{"id":f["id"],"locked":f["locked"]} for d,f in folders.items()}},"files":{k:v["id"] for k,v in files.items()},"pages":{str(d):{k:{"url":v["url"],"published":v["published"]} for k,v in p.items()} for d,p in pages.items()},"items":[{"id":i["id"],"position":i["position"],"title":i["title"],"type":i["type"],"page_url":i.get("page_url"),"content_id":i.get("content_id")} for i in final]},indent=2))

if __name__ == "__main__":
    asyncio.run(main())
