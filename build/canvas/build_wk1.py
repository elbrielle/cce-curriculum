"""Build the unpublished 1SW Week 1 teacher/student Canvas module."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
import httpx

from lesson_contracts import contract_html, load_contracts
from normalize_canvas_lesson_contracts import insert_contract

BASE="https://learn.irvingisd.net"; COURSE_ID=98060
MODULE_NAME="1SW Wk1: Built by Bots - Robotics and Manufacturing Careers"
MODULE_ALIASES={MODULE_NAME}
REFLECTION_TITLE="PRACTICE: 1SW Wk1 Matchmaker Reflection"
REFLECTION_ROUTES={"online_text_entry","media_recording"}
ROOT=Path(__file__).resolve().parents[2]; TEMPLATES=Path(__file__).parent/"templates"; ASSETS=ROOT/"cce-curriculum/resources/canvas-licensed/1sw/wk1"
XELLO_GUIDE=ROOT/"cce-curriculum/resources/xello-licensed/prerequisites/matchmaker-assessment.pdf"
SUPPORT_NAMES={
  "PATHWAYS":"manufacturing-pathways-scaffold.pdf","TECH":"technician-checklist-scaffold.pdf","RESEARCH":"career-research-worksheet.pdf","RESEARCH_EX":"career-research-worksheet-example-welder.pdf","RESEARCH_BI":"career-research-worksheet-bilingual.pdf","PLAN":"1sw-wk1-robots-for-crayons-action-plan.pdf",
  "E1":"1sw-wk1-day1-manufacturing-cluster-tour-more-than-assembly-lines.pdf","E2":"1sw-wk1-day2-machine-breakdown-mystery-career-research.pdf","E3":"1sw-wk1-day3-super-sports-manufacturing-design-build-test.pdf"}
REQUIRED_VISUALS={
  1:("manufacturing-chapter-opener.jpg","manufacturing-app-exploration.png"),
  2:("technician-checklist.png","machine-breakdown-clues.jpg"),
  3:("bike-rack-design-brief.png","metals-and-welding-methods.png","build-and-test-prototype.jpg"),
  4:("robots-for-crayons-problems.png","how-the-machines-work.png","shift-notes-and-impact-report.png"),
}
CONTRACTS={(row.week,row.day):row for row in load_contracts()}

def preflight():
    required=[
        *(TEMPLATES/name for name in ("wk1-teacher.html",*(f"wk1-day{day}-student.html" for day in range(1,6)))),
        *(ROOT/("docs/resources/exit-tickets" if key.startswith("E") else "docs/resources/worksheets")/name for key,name in SUPPORT_NAMES.items()),
        *(ASSETS/f"day{day}"/name for day,names in REQUIRED_VISUALS.items() for name in names),
        XELLO_GUIDE,
    ]
    missing=[str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing: raise FileNotFoundError(f"1SW Wk1 preflight missing required files: {missing}")

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
    if len(module_matches)!=1: raise RuntimeError(f"Expected one 1SW Wk1 module across accepted aliases; found {len(module_matches)}")
    module=module_matches[0]
    if module.get("published") is not False: raise RuntimeError("Refusing to modify a published 1SW Wk1 module")
    assignments=await paged(c,f"/courses/{COURSE_ID}/assignments")
    reflection_matches=[entry for entry in assignments if entry.get("name")==REFLECTION_TITLE]
    if len(reflection_matches)!=1: raise RuntimeError(f"Expected one reflection assignment {REFLECTION_TITLE!r}; found {len(reflection_matches)}")
    reflection=reflection_matches[0]; failures=[]
    if reflection.get("published") is not False: failures.append("published")
    if float(reflection.get("points_possible") or 0)!=0: failures.append("points_possible")
    if reflection.get("grading_type")!="not_graded": failures.append("grading_type")
    if set(reflection.get("submission_types") or [])!=REFLECTION_ROUTES: failures.append("submission_types")
    if failures: raise RuntimeError(f"Matchmaker reflection preflight failed: {failures}")
    return module,reflection
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
    if not uploaded.get("locked"): uploaded=await api(c,"PUT",f"/files/{uploaded['id']}",data={"locked":"true"})
    if uploaded.get("locked") is not True: raise RuntimeError(f"Canvas file did not remain locked: {path.name}")
    return uploaded
async def lock_folder_files(c,folder,required_names=()):
    folder=await api(c,"GET",f"/folders/{folder['id']}")
    if not folder.get("locked"): folder=await api(c,"PUT",f"/folders/{folder['id']}",data={"locked":"true"})
    if folder.get("locked") is not True: raise RuntimeError(f"Canvas folder did not remain locked: {folder['id']}")
    existing=await paged(c,f"/folders/{folder['id']}/files")
    for file in existing:
        if file.get("locked") is not True: await api(c,"PUT",f"/files/{file['id']}",data={"locked":"true"})
    folder=await api(c,"GET",f"/folders/{folder['id']}"); verified=await paged(c,f"/folders/{folder['id']}/files")
    names={file.get("display_name") or file.get("filename") for file in verified}
    missing=set(required_names)-names
    unlocked=[file.get("display_name") or file.get("filename") for file in verified if file.get("locked") is not True]
    if folder.get("locked") is not True or missing or unlocked:
        raise RuntimeError(f"1SW Wk1 folder invariant failed for {folder['id']}: missing={sorted(missing)} unlocked={unlocked}")
    return folder,verified
async def find_file(c,name):
    files=await paged(c,f"/courses/{COURSE_ID}/files",{"search_term":name}); matches=[f for f in files if f.get("display_name")==name]
    if len(matches)!=1: raise ValueError(f"Expected one Canvas file named {name!r}; found {len(matches)}")
    current=await api(c,"GET",f"/files/{matches[0]['id']}")
    if current.get("locked") is not True: raise ValueError(f"Referenced Canvas file is not locked: {name}")
    return current
def render(name,values):
    text=(TEMPLATES/name).read_text()
    for k,v in values.items(): text=text.replace("{{"+k+"}}",str(v))
    unresolved=sorted(set(re.findall(r"\{\{[^}]+\}\}",text)))
    if unresolved: raise ValueError(f"Unresolved values in {name}: {unresolved}")
    return text
def render_page(name,values,day,role):
    contract=CONTRACTS.get(("1SW Wk1",day))
    if contract is None: raise RuntimeError(f"Missing canonical 1SW Wk1 Day {day} contract")
    return insert_contract(render(name,values),contract_html(contract,role),role)
async def upsert_page(c,title,body,url):
    data={"wiki_page[title]":title,"wiki_page[body]":body,"wiki_page[published]":"false","wiki_page[editing_roles]":"teachers"}; r=await c.get(f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{url}")
    if r.status_code==200:return await api(c,"PUT",f"/courses/{COURSE_ID}/pages/{url}",data=data)
    if r.status_code!=404:r.raise_for_status()
    return await api(c,"POST",f"/courses/{COURSE_ID}/pages",data=data)
async def normalize_reflection(c,reflection,description):
    data={"assignment[name]":REFLECTION_TITLE,"assignment[description]":description,"assignment[submission_types][]":sorted(REFLECTION_ROUTES),"assignment[grading_type]":"not_graded","assignment[points_possible]":"0","assignment[omit_from_final_grade]":"true","assignment[published]":"false"}
    await api(c,"PUT",f"/courses/{COURSE_ID}/assignments/{reflection['id']}",data=data)
    current=await api(c,"GET",f"/courses/{COURSE_ID}/assignments/{reflection['id']}")
    failures=[]
    if current.get("published") is not False: failures.append("published")
    if float(current.get("points_possible") or 0)!=0: failures.append("points_possible")
    if current.get("grading_type")!="not_graded": failures.append("grading_type")
    if current.get("omit_from_final_grade") is not True: failures.append("omit_from_final_grade")
    if set(current.get("submission_types") or [])!=REFLECTION_ROUTES: failures.append("submission_types")
    if failures: raise RuntimeError(f"Matchmaker reflection normalization failed: {failures}")
    return current
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
    if len(final)!=16: raise RuntimeError(f"Expected literal 16-item 1SW Wk1 module; found {len(final)}")
    for position,(item,(kind,key,title)) in enumerate(zip(final,expected),start=1):
        if item.get("position")!=position or item.get("title")!=title or item.get("published") is not False or not item_matches(item,kind,key,title):
            raise RuntimeError(f"1SW Wk1 item mismatch at position {position}: {item}")
    return final

def flow(color,title,text): return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'

async def main():
    preflight()
    token=sys.stdin.readline().strip()
    if not token: raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"},timeout=120) as c:
        existing_module,existing_reflection=await canvas_preflight(c)
        module=await ensure_module(c,existing_module); module_id=module["id"]
        reflection=await normalize_reflection(c,existing_reflection,"<p>Respond privately in three labeled parts: (1) one Matchmaker result that surprised you and why, (2) what Find out why showed about one career match, and (3) one example of an interest raising or lowering a match. You may type or record audio. Do not submit a profile screenshot. This practice remains unpublished, worth zero points, and omitted from the final grade.</p>")
        support_folder="course files/CCR Materials/1SW/Wk1"; support_folder_info=await ensure_folder(c,support_folder)
        files={}
        for key,name in SUPPORT_NAMES.items():
            source_dir=ROOT/"docs/resources/exit-tickets" if key.startswith("E") else ROOT/"docs/resources/worksheets"
            files[key]=await upload(c,source_dir/name,support_folder)
        support_folder_info,support_folder_files=await lock_folder_files(c,support_folder_info,SUPPORT_NAMES.values())
        uploads={}; folders={}; folder_files={}
        for day,names in REQUIRED_VISUALS.items():
            folder_path=f"course files/CCR Materials/1SW/Wk1/Day {day} Visuals"; folders[day]=await ensure_folder(c,folder_path); uploads[day]={}
            day_dir=ASSETS/f"day{day}"
            day_images=preferred_images(day_dir)
            selected=[path for path in day_images if path.name in names]
            if {path.name for path in selected}!=set(names): raise RuntimeError(f"1SW Wk1 Day {day} preferred image set drifted")
            for path in selected: uploads[day][path.name]=await upload(c,path,folder_path)
            folders[day],folder_files[day]=await lock_folder_files(c,folders[day],names)
        student_values={
          1:{"OPENER_IMAGE_ID":uploads[1]["manufacturing-chapter-opener.jpg"]["id"],"APP_IMAGE_ID":uploads[1]["manufacturing-app-exploration.png"]["id"],"PATHWAYS_FILE_ID":files["PATHWAYS"]["id"],"EXIT_FILE_ID":files["E1"]["id"]},
          2:{"CHECKLIST_IMAGE_ID":uploads[2]["technician-checklist.png"]["id"],"CLUES_IMAGE_ID":uploads[2]["machine-breakdown-clues.jpg"]["id"],"TECH_SCAFFOLD_FILE_ID":files["TECH"]["id"],"RESEARCH_FILE_ID":files["RESEARCH"]["id"],"RESEARCH_EXAMPLE_FILE_ID":files["RESEARCH_EX"]["id"],"RESEARCH_BILINGUAL_FILE_ID":files["RESEARCH_BI"]["id"],"EXIT_FILE_ID":files["E2"]["id"]},
          3:{"DESIGN_IMAGE_ID":uploads[3]["bike-rack-design-brief.png"]["id"],"METALS_IMAGE_ID":uploads[3]["metals-and-welding-methods.png"]["id"],"BUILD_IMAGE_ID":uploads[3]["build-and-test-prototype.jpg"]["id"],"EXIT_FILE_ID":files["E3"]["id"]},
          4:{"PROBLEMS_IMAGE_ID":uploads[4]["robots-for-crayons-problems.png"]["id"],"MACHINES_IMAGE_ID":uploads[4]["how-the-machines-work.png"]["id"],"SHIFT_IMAGE_ID":uploads[4]["shift-notes-and-impact-report.png"]["id"],"PLAN_FILE_ID":files["PLAN"]["id"]},
          5:{"REFLECTION_URL":f"/courses/{COURSE_ID}/assignments/{reflection['id']}"}}
        student_titles={1:"STUDENT: 1SW Wk1 Day 1 - Manufacturing Cluster Tour",2:"STUDENT: 1SW Wk1 Day 2 - Machine Breakdown Mystery",3:"STUDENT: 1SW Wk1 Day 3 - Design Build Test",4:"STUDENT: 1SW Wk1 Day 4 - Robots for Crayons Action Plan",5:"STUDENT: 1SW Wk1 Day 5 - Xello Matchmaker"}
        student_urls={day:slugify(title) for day,title in student_titles.items()}
        teacher_data={
          1:{"TITLE":"Manufacturing Cluster Tour","SUBTITLE":"50 minutes - required Xello and district HQIM","TOPIC":"Career Clusters","OBJECTIVE":"Students will explore and describe CTE career clusters and identify Manufacturing opportunities using Xello, FYF, and H&L evidence.","TEKS":"d(1)(B), d(1)(C)","DOL":"Submitted What is CTE response, two Stop and Jot notes, and a two-career comparison with one task and one preparation fact for each.","ALERT":"<strong>Protect the ten-minute Xello task.</strong> What is CTE is a required submission, not an optional link. Keep the H&amp;L exploration focused enough to close in 15 minutes.","PREP":f'<ul><li>Preview the current Xello What is CTE prompt and open the Completion Standards report.</li><li>Open FYF pp. 199 and 212 and H&amp;L Manufacturing.</li><li>Post the <a href="/courses/{COURSE_ID}/files/{files["PATHWAYS"]["id"]}/preview">pathways scaffold</a> and <a href="/courses/{COURSE_ID}/files/{files["E1"]["id"]}/preview">exit ticket</a>.</li></ul>',"EVIDENCE":"<p>Xello submission, Stop and Jot notes, and two-career comparison. This week is formative; do not create or attach a mapped Minor or Major.</p>","FLOW_TITLE":"50-minute flow","FLOW":flow("#5a2d91","Warm-up - 5 minutes","Trace one morning product through design, production, programming, and quality control.")+flow("#4a9d2f","Xello What is CTE - 10 minutes","Students open the assigned task and submit the current district prompt.")+flow("#1f617a","FYF Manufacturing opener - 15 minutes","Use p. 199, the weld-quality decision, pathways, and district-customized FYF details.")+flow("#5a2d91","H&L cluster exploration - 15 minutes","Run two Stop and Jot pauses, one pathway rating, and three Hat ratings.")+flow("#e3ad19","Exit - 5 minutes","Compare two Manufacturing careers."),"MONITOR":"<p>Verify the Xello submission first. In H&amp;L, check for two career notes, one pathway, and three actual Hat ratings. Any salary note keeps the career, geography, salary label, and date viewed attached. Do not overwrite a district HQIM figure with a differently defined national median.</p>","SUPPORT":"<p>Use the pathway sheet, sentence frames, read-aloud, and H&amp;L visual context. Pre-teach pathway, welder, maintenance, electronics, and automation.</p>","FALLBACK":"<p>The pathway scaffold and FYF opener support the Manufacturing evidence if H&amp;L is unavailable. What is CTE still moves to supervised Xello catch-up and is verified through the report.</p>"},
          2:{"TITLE":"Machine Breakdown Mystery + Career Research","SUBTITLE":"50 minutes - TEKS d(1)(C), d(2)(A)","TOPIC":"Career Opportunities","OBJECTIVE":"Students will use a five-stage troubleshooting process and research the preparation required for one Manufacturing career.","TEKS":"d(1)(C), d(2)(A)","DOL":"Completed Machine Breakdown Mystery checklist and one Manufacturing career research worksheet.","ALERT":"<strong>Do not reveal the likely cause too early.</strong> Students need to connect the newly installed label roll to the failure before discussion.","PREP":f'<ul><li>Open FYF pp. 207-208.</li><li>Post the <a href="/courses/{COURSE_ID}/files/{files["TECH"]["id"]}/preview">checklist scaffold</a>, <a href="/courses/{COURSE_ID}/files/{files["RESEARCH"]["id"]}/preview">career sheet</a>, and <a href="/courses/{COURSE_ID}/files/{files["E2"]["id"]}/preview">exit ticket</a>.</li><li>Open H&amp;L Manufacturing; keep BLS only as a separately labeled cross-check.</li></ul>',"EVIDENCE":"<p>Five-stage checklist, six-field career sheet, and Jamie scenario. Grade source accuracy and reasoning, not whether H&amp;L and a national source display the same number.</p>","FLOW_TITLE":"50-minute flow","FLOW":flow("#5a2d91","Warm-up - 5 minutes","Connect a broken personal object to troubleshooting.")+flow("#4a9d2f","Machine Breakdown Mystery - 25 minutes","Teach the five stages, release pairs, then discuss the strongest clue.")+flow("#1f617a","Career research - 15 minutes","Students choose one Manufacturing Hat and keep the HQIM source labels with every figure.")+flow("#e3ad19","Exit - 5 minutes","Recommend a career using two training steps and a timeline."),"MONITOR":"<p>Likely cause: the new label roll is wrong, misloaded, or jamming the feed. Strong plans inspect it before unrelated electrical parts, test after adjustment, and prevent recurrence. If sources differ, check geography and measure rather than declaring the HQIM wrong.</p>","SUPPORT":"<p>Use the modeled first stage, Welder example, bilingual field labels, and oral rehearsal. Allow notes in the student’s strongest language.</p>","FALLBACK":"<p>If H&amp;L is unavailable, complete the mystery and use a saved teacher Hat card. Schedule platform exploration later instead of pretending an external occupation page is the same source.</p>"},
          3:{"TITLE":"Super Sports Manufacturing - Design, Build, Test","SUBTITLE":"50 minutes - TEKS d(1)(C)","TOPIC":"Career Opportunities","OBJECTIVE":"Students will apply Welder design choices by selecting materials and joints, then build and test a bike-rack prototype.","TEKS":"d(1)(C)","DOL":"Top-and-side-view bike-rack sketch with labeled welds plus one prototype test and named revision.","ALERT":"<strong>Run glue stations, not free-roaming glue guns.</strong> Use heat mats and gloves, and unplug every gun at the five-minute warning.","PREP":f'<ul><li>Open FYF pp. 204-206 and the <a href="/courses/{COURSE_ID}/files/{files["E3"]["id"]}/preview">exit ticket</a>.</li><li>Set pair kits: sticks, straws, scissors, gloves, and scrap tray.</li><li>Test the equal dry-fit and masking-tape route.</li></ul>',"EVIDENCE":"<p>Sketch with two views, material reason, labeled welds, and one tested prototype. Score design reasoning, not craftsmanship or tool access.</p>","FLOW_TITLE":"50-minute flow","FLOW":flow("#5a2d91","Warm-up - 5 minutes","Trace a 100-rack order through design and production.")+flow("#4a9d2f","Design and choices - 28 minutes","Sketch, choose metal, select welds, and label joints.")+flow("#1f617a","Build and test - 12 minutes","Build one rack, test balance and joints, and name one revision.")+flow("#e3ad19","Exit - 5 minutes","Rank metals, identify a weak point, and connect another career."),"MONITOR":"<p>No single metal is automatically correct. Strong reasoning weighs corrosion, strength, weight, price, and coating. Fillet or corner welds fit angled rack joints better than surfacing welds.</p>","SUPPORT":"<p>Offer a pre-drawn rack, pre-cut materials, bilingual labels, and the frame “I chose ___ because ___ even though ___.”</p>","FALLBACK":"<p>Dry-fit and tape each joint, then label the real weld it represents. Absent students complete the full design and test prediction.</p>"},
          4:{"TITLE":"Robots for Crayons Evidence and Action Plan","SUBTITLE":"50 minutes - TEKS d(1)(C)","TOPIC":"Manufacturing Troubleshooting","OBJECTIVE":"Students will identify Manufacturing careers and explain how workers use case evidence to respond to two production problems.","TEKS":"d(1)(C)","DOL":"Two complete problem plans with clues, testable solution, ordered steps, tools or adjustments, time, production effect, and next check.","ALERT":"<strong>Evidence before fixes.</strong> Students read all three FYF source sections before choosing solutions. Sphero is an optional later extension, not today’s required path.","PREP":f'<ul><li>Open FYF pp. 200-203 and the embedded licensed visuals.</li><li>Post the <a href="/courses/{COURSE_ID}/files/{files["PLAN"]["id"]}/preview">three-page action plan</a>.</li><li>Prepare sticky notes and assign the four factory-role lenses.</li></ul>',"EVIDENCE":"<p>Collect the two-problem plan and an individual two-to-three-sentence career-role response. The packet gives each reasoning job honest writing space.</p>","FLOW_TITLE":"50-minute flow","FLOW":flow("#5a2d91","Warm-up - 5 minutes","Choose the first evidence-based check after a replacement part fails.")+flow("#4a9d2f","Factory brief and machine reference - 10 minutes","Read the two problems and sort supported causes.")+flow("#1f617a","Shift evidence - 10 minutes","Mark two clues per problem through one role lens.")+flow("#5a2d91","Both action plans - 20 minutes","Choose, explain, sequence, time, and plan the next check.")+flow("#e3ad19","Individual check - 5 minutes","Name one role, first action, and source clue."),"MONITOR":"<p><strong>Color Confusion:</strong> first check the replacement sensor’s compatibility, installation, and controlled test. <strong>Slowpoke Robot:</strong> first check the replaced belt’s size or tension, then retest the arm and conveyor together. Accept another safe plan when students cite the source and name what result triggers the next check.</p>","SUPPORT":"<p>Read shift notes aloud, use bilingual labels, permit speech-to-text, and give each student one role lens. At minute 10 check both evidence sections; at minute 16 check the second ordered-step set.</p>","FALLBACK":"<p>The embedded images and packet are the complete independent and absence route. No robot or presentation is required.</p>"},
          5:{"TITLE":"Xello Matchmaker and Career-Match Reflection","SUBTITLE":"50 minutes - required Grade 8 Xello completion","TOPIC":"Career Interests","OBJECTIVE":"Students will analyze their first career-assessment results by connecting one result to an interest and one career detail.","TEKS":"d(1)(A)","DOL":"Matchmaker Phase 1 completed plus a private three-part reflection with one surprise, one Find out why connection, and one interest-to-match example.","ALERT":"<strong>Protect the full Matchmaker lesson.</strong> The licensed guide gives 30-35 minutes for the first 39 questions. After high school goal is the prerequisite. Do not rush students or require profile screenshots.","PREP":f'<ul><li>Confirm After high school goal completion in the report.</li><li>Open a student demo account and the licensed <a href="/courses/{COURSE_ID}/files/{(await find_file(c,"matchmaker-assessment.pdf"))["id"]}/preview">Matchmaker educator guide</a>.</li><li>Open the unpublished private reflection Assignment.</li><li>Prepare a four-status roster: complete, prerequisite missing, access issue, absent.</li></ul>',"EVIDENCE":"<p>The Completion Standards report verifies Phase 1. The private reflection captures analysis without exposing profile data. This is formative practice, not another Major or Minor.</p>","FLOW_TITLE":"50-minute flow","FLOW":flow("#5a2d91","Warm-up - 5 minutes","Name one liked task and one avoided task.")+flow("#4a9d2f","Scale and Find out why - 7 minutes","Model the full response scale and one demo-account result.")+flow("#1f617a","Matchmaker lesson - 28 minutes","Complete the first 39 questions and inspect one match.")+flow("#e3ad19","Private reflection - 7 minutes","Answer three labeled prompts in Canvas.")+flow("#1f617a","Report and catch-up - 3 minutes","Verify completion or schedule supervised recovery."),"MONITOR":"<p>Lap 1: correct About Me task. Lap 2: full response scale. Lap 3: one career plus Find out why. Score the reflection’s reasoning, not whether the student likes the match. A teacher sample may support a blocked student’s reflection, but it does not count as Xello completion.</p>","SUPPORT":"<p>Read scale labels aloud, reduce visual distractions, provide three sentence frames, and allow typing, speech-to-text, audio, or a private teacher conference.</p>","FALLBACK":"<p>A paper interest sort supports learning but does not replace Matchmaker. Use supervised catch-up for prerequisite, login, absence, or incomplete assessment.</p>"}}
        logistics={
          1:"<ul><li><strong>Default:</strong> one device and one FYF workbook per student; projector for the opening and Xello navigation.</li><li><strong>Print:</strong> one exit ticket per student plus two spares. Print the pathways scaffold only for students who need the larger response route.</li><li><strong>Grouping:</strong> individual Xello and written evidence; one assigned elbow partner for each timed Stop and Jot share.</li><li><strong>Collection:</strong> verify What is CTE in the Xello report, then collect the two-career comparison in the class tray or established private digital location.</li></ul>",
          2:"<ul><li><strong>Default:</strong> one device, one FYF workbook, one troubleshooting checklist, one career sheet, and one exit ticket per student.</li><li><strong>Grouping:</strong> pairs may discuss the mystery, but every student records the five stages and completes one career record.</li><li><strong>Materials:</strong> project the clues; keep the bilingual career sheet available only where it improves access.</li><li><strong>Collection:</strong> students clip or submit the checklist and career sheet together; collect exits in the same tray before dismissal.</li></ul>",
          3:"<ul><li><strong>Default:</strong> one FYF workbook and one design/exit response per student; one prototype per pair.</li><li><strong>Pair kit:</strong> 12 craft sticks, 8 paper straws, one pair of scissors, masking tape, two craft gloves, and one scrap tray. If hot glue is approved, use one supervised station per working outlet with a heat mat.</li><li><strong>Roles:</strong> Designer labels the two views; Builder manages materials. Both students test the prototype and record their own revision.</li><li><strong>Collection and reset:</strong> unplug glue at the five-minute warning, return reusable tools by tray, discard scraps, and collect each student response with the pair prototype label.</li></ul>",
          4:"<ul><li><strong>Default:</strong> one FYF workbook and one three-page action plan per student; no robot is required.</li><li><strong>Grouping:</strong> teams of four use the Operator, Technician, Engineer, and Supervisor lenses, but each student completes both plans and the individual career-role check.</li><li><strong>Team materials:</strong> one projected or embedded source set, eight sticky notes, and one collection tray.</li><li><strong>Collection:</strong> return sticky notes to the tray and collect every student plan before dismissal; the packet remains the single response home.</li></ul>",
          5:"<ul><li><strong>Default:</strong> one device per student, projector, student demo account, and teacher Completion Standards report; zero default printing.</li><li><strong>Grouping:</strong> assessment and reflection are individual and private. Do not require students to compare results.</li><li><strong>Collection:</strong> verify Phase 1 in the report and collect the three labeled reflection parts in the private Assignment.</li><li><strong>Recovery:</strong> use the four-status roster to schedule a supervised catch-up window; a paper interest sort supports access but is not recorded as Xello completion.</li></ul>"}
        models={
          1:"<div style='background:#f2f8fb;border-left:5px solid #1f617a;padding:12px 16px'><p><strong>Complete comparison model:</strong> “A welder joins metal parts and checks the joint. Preparation can include welding classes and supervised practice. An industrial maintenance technician inspects and repairs production equipment. Preparation can include technical training and supervised practice. I would investigate maintenance first because I like finding why a system stopped working.”</p><p><strong>Non-example:</strong> “Welder is better because it pays more.” It gives no task, preparation evidence, source label, or reason connected to the student.</p></div>",
          2:"<div style='background:#f2f8fb;border-left:5px solid #1f617a;padding:12px 16px'><p><strong>Five-stage model:</strong> Identify: labels stop feeding after a new roll is installed. Diagnose: the roll may be the wrong size, loaded backward, or jamming the feed. Plan: compare the part number and reload the roll correctly. Implement: adjust only the roll path. Evaluate: run five labels and check spacing. Prevent: add a roll-number and threading check to setup.</p><p><strong>Non-example:</strong> “Replace the motor.” It ignores the timing of the failure and does not name a test.</p></div>",
          3:"<div style='background:#f2f8fb;border-left:5px solid #1f617a;padding:12px 16px'><p><strong>Design model:</strong> “I chose coated carbon steel because it is strong and less expensive, even though the coating must be maintained. I labeled fillet welds where the angled rack meets the base. In the model, the base joint twisted during the side-push test, so I would add a diagonal brace and retest the same push.”</p><p><strong>Non-example:</strong> “Stainless steel is best because it is strong.” It has no trade-off, joint choice, test result, or revision.</p></div>",
          4:"<div style='background:#f2f8fb;border-left:5px solid #1f617a;padding:12px 16px'><p><strong>Color Confusion model:</strong> Clue: the problem began after the sensor replacement. Solution: verify compatibility and installation before changing unrelated parts. Steps: compare the replacement number, inspect alignment and wiring, run a controlled color test, then record the result. Tools/adjustments: manual, alignment marks, and test crayons. Production effect: a short stop prevents a longer run of incorrect boxes. Next check: if the controlled test still fails, inspect the signal path.</p><p><strong>Non-example:</strong> “Update the software.” It is not tied to the source evidence and gives no result that controls the next step.</p></div>",
          5:"<div style='background:#f2f8fb;border-left:5px solid #1f617a;padding:12px 16px'><p><strong>Fictional demo result:</strong> “Industrial designer surprised me because I expected only art careers. Find out why connected the match to improving how products work for people. My interest in creating and revising ideas raised the match, while my dislike of repetitive sorting lowered another match.”</p><p><strong>Non-example:</strong> “I got engineer and it was cool.” It does not explain the surprise, use Find out why, or connect an interest to a match.</p></div>"}
        monitoring={
          1:"<p><strong>Timed checks:</strong> By minute 8, every student should be in the assigned What is CTE task; by minute 25, students should have two FYF career notes; by minute 42, they should have one task and one preparation fact for each comparison career. If one-third of the class is on the wrong Xello screen, stop and re-project the exact path. Trim the third Hat rating or second partner share—not the Xello task or two-career comparison.</p>",
          2:"<p><strong>Timed checks:</strong> By minute 12, students should have Identify and Diagnose tied to the new label roll; by minute 28, the plan should include a controlled test; by minute 42, the career sheet should include its labeled source fields. If one-third of pairs jump to unrelated electrical repairs, project the supplied cause-test model and have them underline the clue that changed their plan. Trim whole-group sharing, not the five stages or career record.</p>",
          3:"<p><strong>Timed checks:</strong> By minute 14, each student should have two views, a material, and labeled joints; by minute 32, each pair should have a testable prototype; by minute 45, every student should have one observed weak point and revision. If one-third cannot match a joint to the sketch, project the supplied model and ask students to circle the base joint before building. Trim decoration and public sharing, not the test or revision.</p>",
          4:"<p><strong>Timed checks:</strong> By minute 15, each student should have two source clues per problem; by minute 32, the first plan should include a test and next check; by minute 45, both plans should be complete. If one-third propose fixes without source evidence, project the Color Confusion model and ask, “What result would make you keep or change this plan?” Trim the team report-out, not either action plan or the individual role check.</p>",
          5:"<p><strong>Timed checks:</strong> By minute 12, students should be in the correct Matchmaker phase and using the full scale; by minute 35, most should be near the end of the 39 questions; by minute 44, they should have opened one match and Find out why. If one-third have a missing prerequisite or access problem, move those students to the supported interest-analysis route and record supervised catch-up instead of rushing the assessment. Trim optional browsing, not Phase 1, the three-part reflection, or report verification.</p>"}
        day_names={1:"Manufacturing Cluster Tour",2:"Machine Breakdown Mystery",3:"Design Build Test",4:"Robots for Crayons Action Plan",5:"Xello Matchmaker"}
        pages={}; expected=[]
        for day in range(1,6):
            header_title=f"Day {day} · {day_names[day]}"
            st=student_titles[day]; su=student_urls[day]; values={"COURSE_ID":COURSE_ID,**student_values[day]}
            student=await upsert_page(c,st,render_page(f"wk1-day{day}-student.html",values,day,"student"),su)
            tt=f"TEACHER: 1SW Wk1 Day {day} Facilitator Guide"; tu=slugify(tt)
            teacher_values={"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student["url"],**teacher_data[day],"LOGISTICS":logistics[day],"MODEL":models[day],"MONITOR":teacher_data[day]["MONITOR"]+monitoring[day]}
            teacher=await upsert_page(c,tt,render_page("wk1-teacher.html",teacher_values,day,"teacher"),tu)
            pages[day]={"teacher":teacher,"student":student}
            expected.extend([("SubHeader",None,header_title),("Page",teacher["url"],tt),("Page",student["url"],st)])
            if day==5: expected.append(("Assignment",reflection["id"],REFLECTION_TITLE))
        final=await reconcile_module_items(c,module_id,expected)
        module=await api(c,"GET",f"/courses/{COURSE_ID}/modules/{module_id}")
        reflection=await api(c,"GET",f"/courses/{COURSE_ID}/assignments/{reflection['id']}")
        if module.get("published") is not False: raise RuntimeError("1SW Wk1 module became published")
        reflection_failures=[]
        if reflection.get("published") is not False: reflection_failures.append("published")
        if float(reflection.get("points_possible") or 0)!=0: reflection_failures.append("points_possible")
        if reflection.get("grading_type")!="not_graded": reflection_failures.append("grading_type")
        if reflection.get("omit_from_final_grade") is not True: reflection_failures.append("omit_from_final_grade")
        if set(reflection.get("submission_types") or [])!=REFLECTION_ROUTES: reflection_failures.append("submission_types")
        if reflection_failures: raise RuntimeError(f"Matchmaker reflection final invariant failed: {reflection_failures}")
        fresh_pages={}
        for day,pair in pages.items():
            fresh_pages[day]={}
            for role,page in pair.items():
                current=await api(c,"GET",f"/courses/{COURSE_ID}/pages/{page['url']}")
                if current.get("published") is not False: raise RuntimeError(f"1SW Wk1 {role} page became published: Day {day}")
                fresh_pages[day][role]=current
        support_folder_info,support_folder_files=await lock_folder_files(c,support_folder_info,SUPPORT_NAMES.values())
        for day,names in REQUIRED_VISUALS.items(): folders[day],folder_files[day]=await lock_folder_files(c,folders[day],names)
        xello_guide=await find_file(c,"matchmaker-assessment.pdf")
        print(json.dumps({"module":{"id":module_id,"published":module["published"]},"assignment":{"id":reflection["id"],"published":reflection.get("published"),"points_possible":reflection.get("points_possible"),"grading_type":reflection.get("grading_type"),"omit_from_final_grade":reflection.get("omit_from_final_grade"),"submission_types":reflection.get("submission_types")},"support_folder":{"id":support_folder_info["id"],"locked":support_folder_info["locked"],"files":len(support_folder_files)},"folders":{str(d):{"id":f["id"],"locked":f["locked"],"files":len(folder_files[d])} for d,f in folders.items()},"xello_guide":{"id":xello_guide["id"],"locked":xello_guide["locked"]},"pages":{str(d):{k:{"url":v["url"],"published":v["published"]} for k,v in p.items()} for d,p in fresh_pages.items()},"items":[{"id":i["id"],"position":i["position"],"title":i["title"],"type":i["type"],"page_url":i.get("page_url"),"published":i.get("published")} for i in final]},indent=2))

if __name__ == "__main__":
    asyncio.run(main())
