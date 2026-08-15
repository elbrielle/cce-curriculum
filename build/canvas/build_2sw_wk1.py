"""Build the unpublished 2SW Week 1 teacher/student Canvas module."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
import httpx

BASE="https://learn.irvingisd.net"; COURSE_ID=98060
MODULE_NAME="2SW Wk1: Legal Studies and Policy Evidence"
MODULE_ALIASES={MODULE_NAME,"2SW Wk1: Order in the Court - Legal Studies","2SW Wk1: Order in the Court — Legal Studies"}
MAPPED_MAJOR_TITLE="MAJOR 1: Legal Policy Position Evidence"
MAJOR_GROUP_NAME="Major Assessments (60%)"
RUBRIC_NOTE_MARKER='data-cce-rubric-note="cce-advisory-rubric-v1"'
MAJOR_SUBMISSION_TYPES={"online_upload","online_text_entry","media_recording"}
ROOT=Path(__file__).resolve().parents[2]; TEMPLATES=Path(__file__).parent/"templates"; ASSETS=ROOT/"cce-curriculum/resources/canvas-licensed/2sw/wk1"

SUPPORT_NAMES={"CAREER":"career-research-worksheet.pdf","CAREER_CARDS":"2sw-wk1-legal-career-cards.pdf","KIT":"2sw-wk1-emergency-kit-plan.pdf","TOWN":"2sw-wk1-city-council-plan.pdf","ARGUMENT":"2sw-wk1-policy-argument-and-evidence.pdf","ENTREPRENEUR":"2sw-wk1-legal-entrepreneur-card.pdf","RUBRIC":"2sw-wk1-position-paper-rubric.pdf","CONNECTION":"2sw-wk1-xello-life-experience-connection.pdf"}
REQUIRED_VISUALS={
    1:("law-cluster-opener.jpg","irving-legal-programs.png"),
    2:("emergency-essentials-056.png","emergency-essentials-057.png"),
    3:("city-council-046.png","city-council-047.png","city-council-048.png","city-council-049.png"),
    4:("policy-showdown-050.png",),
    5:("irving-legal-programs.png",),
}

def preflight():
    required=[
        *(TEMPLATES/name for name in ("2sw-wk1-teacher.html",*(f"2sw-wk1-day{day}-student.html" for day in range(1,6)))),
        *(ROOT/"docs/resources/worksheets"/name for name in SUPPORT_NAMES.values()),
        *(ASSETS/f"day{day}"/name for day,names in REQUIRED_VISUALS.items() for name in names),
    ]
    missing=[str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing: raise FileNotFoundError(f"2SW Wk1 preflight missing required files: {missing}")

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
    if len(module_matches)!=1: raise RuntimeError(f"Expected one 2SW Wk1 module across accepted aliases; found {len(module_matches)}")
    module=module_matches[0]
    if module.get("published") is not False: raise RuntimeError("Refusing to modify a published 2SW Wk1 module")
    groups=await paged(c,f"/courses/{COURSE_ID}/assignment_groups")
    group_matches=[entry for entry in groups if entry.get("name")==MAJOR_GROUP_NAME]
    if len(group_matches)!=1: raise RuntimeError(f"Expected one {MAJOR_GROUP_NAME!r} group; found {len(group_matches)}")
    assignments=await paged(c,f"/courses/{COURSE_ID}/assignments")
    major_matches=[entry for entry in assignments if entry.get("name")==MAPPED_MAJOR_TITLE]
    if len(major_matches)!=1: raise RuntimeError(f"Expected one mapped assignment {MAPPED_MAJOR_TITLE!r}; found {len(major_matches)}")
    major=major_matches[0]
    failures=[]
    if major.get("published") is not False: failures.append("published")
    if float(major.get("points_possible") or 0)!=100: failures.append("points_possible")
    if major.get("grading_type")!="points": failures.append("grading_type")
    if major.get("omit_from_final_grade") is not False: failures.append("omit_from_final_grade")
    if major.get("assignment_group_id")!=group_matches[0].get("id"): failures.append("assignment_group")
    if set(major.get("submission_types") or [])!=MAJOR_SUBMISSION_TYPES: failures.append("submission_types")
    if RUBRIC_NOTE_MARKER not in (major.get("description") or ""): failures.append("rubric_marker")
    if failures: raise RuntimeError(f"Mapped Major preflight failed: {failures}")
    return module,major,group_matches[0]

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
    r=await c.post(init["upload_url"],data=init["upload_params"],files={"file":(path.name,path.read_bytes(),mimetypes.guess_type(path.name)[0] or "application/octet-stream")},follow_redirects=True); r.raise_for_status()
    uploaded=await api(c,"PUT",f"/files/{r.json()['id']}",data={"locked":"true"})
    if uploaded.get("locked") is not True: raise RuntimeError(f"Canvas did not lock uploaded file {path.name!r}")
    return uploaded
async def lock_folder_files(c,folder,required_names=()):
    current=await api(c,"GET",f"/folders/{folder['id']}")
    if current.get("locked") is not True: current=await api(c,"PUT",f"/folders/{folder['id']}",data={"locked":"true"})
    for entry in await paged(c,f"/folders/{folder['id']}/files"):
        if entry.get("locked") is not True: await api(c,"PUT",f"/files/{entry['id']}",data={"locked":"true"})
    current=await api(c,"GET",f"/folders/{folder['id']}"); files=await paged(c,f"/folders/{folder['id']}/files")
    names={entry.get("display_name") or entry.get("filename") for entry in files}
    missing=set(required_names)-names
    unlocked=[entry.get("display_name") or entry.get("filename") for entry in files if entry.get("locked") is not True]
    if current.get("locked") is not True or missing or unlocked: raise RuntimeError(f"2SW Wk1 folder invariant failed for {folder['id']}: missing={sorted(missing)} unlocked={unlocked}")
    return current,files
async def find_file(c,name):
    files=await paged(c,f"/courses/{COURSE_ID}/files",{"search_term":name}); match=next((f for f in files if f.get("display_name")==name),None)
    if not match: raise ValueError(f"Canvas file not found: {name}")
    current=await api(c,"GET",f"/files/{match['id']}")
    if current.get("locked") is not True: raise RuntimeError(f"Referenced Canvas file is not locked: {name}")
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
    if len(final)!=16: raise RuntimeError(f"Expected literal 16-item 2SW Wk1 module; found {len(final)}")
    for position,(item,(kind,key,title)) in enumerate(zip(final,expected),start=1):
        if item.get("position")!=position or item.get("title")!=title or item.get("published") is not False or not item_matches(item,kind,key,title):
            raise RuntimeError(f"2SW Wk1 item mismatch at position {position}: {item}")
    return final
def flow(color,title,text): return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'
def detail_images(uploads,names,alts):
    parts=[]
    for index,name in enumerate(names,start=1):
        file=uploads[name]
        parts.append(f'<p><img loading="lazy" src="/courses/{COURSE_ID}/files/{file["id"]}/preview" alt="{alts[index-1]}" style="display:block;width:100%;max-width:680px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file["id"]}" data-api-returntype="File"></p>')
    return "".join(parts)

async def main():
    preflight()
    token=sys.stdin.readline().strip()
    if not token: raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"},timeout=120) as c:
        existing_module,mapped_major,major_group=await canvas_preflight(c)
        module=await ensure_module(c,existing_module); module_id=module["id"]
        support_folder_path="course files/CCR Materials/2SW/Wk1"; support_folder=await ensure_folder(c,support_folder_path); files={}
        for key,name in SUPPORT_NAMES.items(): files[key]=await upload(c,ROOT/"docs/resources/worksheets"/name,support_folder_path)
        files["XELLO"]=await find_file(c,"experiences.pdf")
        uploads={}; folders={}
        for day in range(1,6):
            folder_path=f"course files/CCR Materials/2SW/Wk1/Day {day} Visuals"; folders[day]=await ensure_folder(c,folder_path); uploads[day]={}
            for path in preferred_images(ASSETS/f"day{day}"): uploads[day][path.name]=await upload(c,path,folder_path)
        support_folder,support_folder_files=await lock_folder_files(c,support_folder,SUPPORT_NAMES.values())
        folder_files={}
        for day,folder in folders.items():
            folders[day],folder_files[day]=await lock_folder_files(c,folder,(path.name for path in preferred_images(ASSETS/f"day{day}")))
        student_values={
          1:{"OPENER_IMAGE_ID":uploads[1]["law-cluster-opener.jpg"]["id"],"PROGRAM_IMAGE_ID":uploads[1]["irving-legal-programs.png"]["id"],"CAREER_FILE_ID":files["CAREER"]["id"],"CAREER_CARDS_FILE_ID":files["CAREER_CARDS"]["id"]},
          2:{"PAGE1_IMAGE_ID":uploads[2]["emergency-essentials-056.png"]["id"],"PAGE2_IMAGE_ID":uploads[2]["emergency-essentials-057.png"]["id"],"PLAN_FILE_ID":files["KIT"]["id"]},
          3:{"PAGE1_IMAGE_ID":uploads[3]["city-council-046.png"]["id"],"PLAN_FILE_ID":files["TOWN"]["id"],"SOURCE_IMAGES":detail_images(uploads[3],["city-council-047.png","city-council-048.png","city-council-049.png"],["Find Your Future town-design directions","Find Your Future problem scan and ordinance-drafting directions","Find Your Future partner-review directions"])},
          4:{"POLICY_IMAGE_ID":uploads[4]["policy-showdown-050.png"]["id"],"ARGUMENT_FILE_ID":files["ARGUMENT"]["id"],"ENTREPRENEUR_FILE_ID":files["ENTREPRENEUR"]["id"]},
          5:{"RUBRIC_FILE_ID":files["RUBRIC"]["id"],"CONNECTION_FILE_ID":files["CONNECTION"]["id"],"PROGRAM_IMAGE_ID":uploads[5]["irving-legal-programs.png"]["id"]}}
        student_titles={1:"STUDENT: 2SW Wk1 Day 1 - Explore Legal Careers",2:"STUDENT: 2SW Wk1 Day 2 - Emergency Kit Decisions",3:"STUDENT: 2SW Wk1 Day 3 - City Council Ordinances",4:"STUDENT: 2SW Wk1 Day 4 - Policy Showdown",5:"STUDENT: 2SW Wk1 Day 5 - Legal Career Evidence and Xello"}
        teacher_data={
          1:{"TITLE":"Law and Public Safety Cluster Tour","SUBTITLE":"50 minutes · TEKS d(1)(B), d(1)(C)","ALERT":"<strong>Use the supplied cards as the dependable core.</strong> H&amp;L and Xello may add the district-local view, but students must not mix local ranges, starting pay, and national medians as though they are the same measure.","PREP":f'<ul><li>Open FYF pp. 39 and 56-58 in the student guide.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["CAREER_CARDS"]["id"]}/preview">Legal Career Evidence Cards</a> and <a href="/courses/{COURSE_ID}/files/{files["CAREER"]["id"]}/preview">Career Research Worksheet</a>.</li><li>Preflight H&amp;L or Xello only if offering the optional local cross-check.</li></ul>',"EVIDENCE":"<p>Formative/minor option: one complete six-field career research sheet plus the two-career comparison on the evidence cards. Platform access and career enthusiasm are not graded.</p>","FLOW":flow("#5a2d91","Safety-inspector warm-up · 5 minutes","Choose continue, delay, or stop; name information needed before deciding.")+flow("#4a9d2f","Cluster and Irving routes · 12 minutes","Read the opener and distinguish the broad cluster from the district program snapshots.")+flow("#1f617a","Career evidence and research · 25 minutes","Compare the three supplied cards, choose one career, and complete the research sheet.")+flow("#e3ad19","Compare and close · 8 minutes","Compare preparation, one task, and one carefully labeled salary fact."),"MONITOR":"<p>Require career name, fit reason, job description, preparation, salary label, tools/skills, source, and date. The fixed wage key is May 2024 U.S. median: lawyer $151,160; paralegal/legal assistant $61,010; court reporter/simultaneous captioner $67,310. These are not DFW starting salaries. A career may connect to more than one program.</p>","SUPPORT":"<p>Read the three career cards aloud or assign one per pair, highlight the exact evidence before paraphrasing, and use the complete-thought frame on page 2. Students may dictate notes or use speech-to-text.</p>","FALLBACK":"<p>The embedded workbook pages and Legal Career Evidence Cards are the normal no-login route. An absent student completes the same sheet without watching a vendor video.</p>"},
          2:{"TITLE":"Emergency Essentials Kit Design","SUBTITLE":"50 minutes · TEKS d(1)(C)","ALERT":"<strong>No open-web research is required.</strong> The licensed workbook list and decision plan contain the core task. Paper and an approved digital design are equal routes.","PREP":f'<ul><li>Open FYF pp. 50-51 in the student guide.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["KIT"]["id"]}/preview">Emergency Kit Decision Plan</a>.</li><li>Have paper and pencils ready; digital design is optional.</li></ul>',"EVIDENCE":"<p>Formative/minor option: exactly ten labeled items, three scenario-specific reasons, one revision, and one firefighter or emergency-management planning connection. Artistic polish does not affect the score.</p>","FLOW":flow("#5a2d91","Five-minute grab warm-up · 5 minutes","Name the first item and test whether it still helps if power or water fails.")+flow("#4a9d2f","Scenario and constraints · 8 minutes","Choose earthquake, fire evacuation, or flood; define the urgent problem.")+flow("#1f617a","Select, design, defend · 25 minutes","Choose exactly ten workbook items, label them, and defend the top three.")+flow("#e3ad19","Feedback and revision · 7 minutes","Partner or self-check; record one change.")+flow("#1f617a","Career connection · 5 minutes","Name the planning task this activity models."),"MONITOR":"<p>Count ten, then look for scenario fit. A plausible rationale matters more than one universal answer. Redirect comfort-only lists by asking which choice addresses water, first aid, signaling, shelter, breathing, or evacuation. The career connection must name planning before an emergency, not only responding afterward.</p>","SUPPORT":"<p>Read the item list aloud, provide scenario icons and the frame “I chose ___ because in a ___, people need ___.” Students may label instead of drawing detailed objects. Offer the career frame visible in the student guide.</p>","FALLBACK":"<p>No device is needed. An absent student uses the embedded pages and self-check. Do not require a partner or a Canva account.</p>"},
          3:{"TITLE":"City Council in Action","SUBTITLE":"50 minutes · TEKS d(1)(C)","ALERT":"<strong>Protect the causal chain:</strong> town features create problems; problems create ordinances. A wish is not a law, and a consequence must be enforceable.","PREP":f'<ul><li>Open FYF pp. 40-43 in the student guide.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["TOWN"]["id"]}/preview">Town and Ordinance Plan</a>.</li><li>Use the printed model problem on page 1; no separate exemplar is required.</li></ul>',"EVIDENCE":"<p>Formative/minor option: town plan, four-problem scan, two ordinances with rule/reason/consequence, one documented revision, and one specific worker/task connection.</p>","FLOW":flow("#5a2d91","Rule warm-up · 5 minutes","Name a city rule and who has authority to make it.")+flow("#4a9d2f","Council role and three tests · 7 minutes","Clear, fair, and realistic to enforce.")+flow("#1f617a","Town, problems, and laws · 28 minutes","9 minutes town, 7 minutes problem scan, 12 minutes ordinances.")+flow("#e3ad19","Review and revise · 5 minutes","Partner or self-check one ordinance.")+flow("#1f617a","Career connection · 5 minutes","Name a worker and the exact task that worker would do."),"MONITOR":"<p>Lap 1: town name, climate, transportation. Lap 2: all four problem rows. Lap 3: two rules with reasons and realistic consequences. Model the printed problem row if several students stall. Accept multiple workers when the task is plausible: council member creates/votes, city attorney reviews, clerk records, public-information officer explains, or an authorized worker enforces.</p>","SUPPORT":"<p>Give one constraint, such as a snowy climate, to students who cannot start. Use the printed model row and sentence frame. Sketches, oral rehearsal, and speech-to-text are valid supports.</p>","FALLBACK":"<p>The Canvas images and printable contain the whole task. An absent student uses the self-check in place of peer feedback.</p>"},
          4:{"TITLE":"Policy Showdown and Legal Entrepreneurship","SUBTITLE":"50 minutes · TEKS d(3)(H), d(3)(I)","ALERT":"<strong>Use only the controlled hypothetical and evidence bank.</strong> Keep the discussion away from real cases and families. Written argument is an equal route to oral presentation.","PREP":f'<ul><li>Open FYF pp. 44-47 as the licensed protocol model.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["ARGUMENT"]["id"]}/preview">Legal Review Argument and Evidence Sheet</a> and <a href="/courses/{COURSE_ID}/files/{files["ENTREPRENEUR"]["id"]}/preview">Entrepreneur Card</a>.</li><li>Assign sides. Page 2 of the Entrepreneur Card supplies the career and association bank; no source hunt is required.</li></ul>',"EVIDENCE":f'<p><strong>Major evidence begins:</strong> final personal position plus Entrepreneur Card, scored with the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">16-point rubric</a>. Assigned-side speaking is practice, not graded performance.</p>',"FLOW":flow("#5a2d91","Initial decision · 5 minutes","Private one-sentence reaction; students may pass on sharing.")+flow("#4a9d2f","Protocol and policy · 8 minutes","Review support, oppose, judge, and revise roles.")+flow("#1f617a","Prepare, present/read, and judge · 20 minutes","Use three evidence notes and one ruling. Written exchange is equal.")+flow("#e3ad19","Entrepreneur and association card · 10 minutes","Use the fixed bank and record the selected source/date.")+flow("#1f617a","Personal-position draft · 7 minutes","Students may differ from the assigned side."),"MONITOR":"<p>There is no required yes/no answer. Full evidence names a policy detail, explains why it matters, and addresses a benefit, risk, opposing idea, or safeguard. Association key: State Bar of Texas for lawyers, NALA for paralegals/legal assistants, NCRA for court reporters/captioners. Accept another verified association. Membership does not replace a license or certification.</p>","SUPPORT":"<p>Read the policy aloud, color-code the two evidence columns, and provide the complete stems “This detail matters because…” and “I would revise the policy by… because…”. Permit speech-to-text or a teacher-scribed response when documented.</p>","FALLBACK":"<p>No live web or H&amp;L is required. An absent or non-speaking student reads both evidence columns and submits written arguments for both sides plus a ruling.</p>"},
          5:{"TITLE":"Position Revision and Xello Life Experiences","SUBTITLE":"50 minutes · TEKS d(1)(C), d(3)(H)","ALERT":"<strong>Required district task:</strong> protect 10 minutes for Xello Life experiences and verify at least one saved entry. H&amp;L is supplemental.","PREP":f'<ul><li>Open the Completion Standards report and check rosters.</li><li>Open the licensed <a href="/courses/{COURSE_ID}/files/{files["XELLO"]["id"]}/preview">My Experiences teacher plan</a> as background.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["CONNECTION"]["id"]}/preview">Life Experience Connection</a> and <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">position-paper rubric</a>.</li></ul>',"EVIDENCE":f'<p><strong>One major grade:</strong> final position plus Entrepreneur Card, 16 points. Required Xello completion is recorded separately as a completion checkpoint or embedded minor evidence; login success is not part of the major.</p>',"FLOW":flow("#5a2d91","Career-fit warm-up · 5 minutes","Interested, unsure, or not interested—with one job-detail reason.")+flow("#4a9d2f","Revise and submit · 10 minutes","Use rubric: position, two details, career connection, completed card.")+flow("#1f617a","Xello Life experiences · 10 minutes","About Me > Experiences; add and save at least one authentic life experience.")+flow("#e3ad19","Experience-to-career connection · 15 minutes","Name what the experience shows and connect it to a specific task.")+flow("#1f617a","Report check and catch-up · 7 minutes","Verify saves; paper route for access issues.")+flow("#5a2d91","Close · 3 minutes","Name one next question about a legal career or route."),"MONITOR":"<p>Xello minimum: at least one saved life experience. Students control which non-private experience they share. A valid connection names what the student did or learned and a specific career task. A well-supported “not a fit” remains valid.</p>","SUPPORT":"<p>Offer examples by category—home responsibility, team, hobby, school project, club, volunteering—without requiring sensitive disclosure. Students may rehearse orally, use the printed English/Spanish labels, or use speech-to-text.</p>","FALLBACK":"<p>If Xello fails, record the access issue and collect the paper connection. The required save moves to the next catch-up block. H&amp;L may be omitted with no loss of core evidence.</p>"}}
        contracts={
          1:{"TOPIC":"Legal Careers","OBJECTIVE":"Students will explore the Law, Public Safety, Corrections and Security cluster and identify legal career opportunities using dated work, preparation, wage, and skill evidence.","TEKS":"d(1)(B), d(1)(C)","DOL":"Completed six-field career research sheet and two-career comparison using the fixed evidence cards.","STUDENT_OBJECTIVE":"I can compare legal careers by their work, preparation, pay evidence, and skills.","STUDENT_DOL":"I will complete all six career fields and use evidence to explain one career choice."},
          2:{"TOPIC":"Emergency Planning","OBJECTIVE":"Students will identify a public-safety career opportunity by designing and defending a scenario-specific emergency kit and explaining the planning task it models.","TEKS":"d(1)(C)","DOL":"Emergency Kit Plan with exactly ten labeled items, three reasons, one revision, and one firefighter or emergency-management planning connection.","STUDENT_OBJECTIVE":"I can make emergency-kit decisions and explain how public-safety workers plan before an emergency.","STUDENT_DOL":"I will submit ten labeled items, three reasons, one revision, and one career-planning connection."},
          3:{"TOPIC":"Local Ordinances","OBJECTIVE":"Students will identify legal and public-service career opportunities by drafting clear, fair, enforceable ordinances and connecting one worker to the process.","TEKS":"d(1)(C)","DOL":"Town plan, four-problem scan, two complete ordinances, one revision, and one specific worker/task connection.","STUDENT_OBJECTIVE":"I can write two workable town ordinances and explain who would create, review, explain, or enforce one of them.","STUDENT_DOL":"I will complete the town plan, two ordinances, one revision, and one worker/task connection."},
          4:{"TOPIC":"Legal Entrepreneurship","OBJECTIVE":"Students will define entrepreneurship, identify a plausible independent-work opportunity in the legal field, and explain how one professional association supports that pathway.","TEKS":"d(3)(I), d(3)(H)","DOL":"Controlled-evidence policy argument and personal position plus a complete Legal Entrepreneur and Association Card.","STUDENT_OBJECTIVE":"I can evaluate a policy from both sides and connect one legal business opportunity to a professional association.","STUDENT_DOL":"I will submit evidence for both sides, my own position, and a complete career-and-association card."},
          5:{"TOPIC":"Experience Connections","OBJECTIVE":"Students will identify one legal career opportunity, explain how a professional association supports it, and connect one authentic life experience to a specific career task.","TEKS":"d(1)(C), d(3)(H)","DOL":"Final legal-policy evidence, completed association card, at least one saved Xello Life experience, and a specific experience-to-career connection.","STUDENT_OBJECTIVE":"I can connect a life experience and a professional association to one legal career.","STUDENT_DOL":"I will submit the final evidence, save one Xello Life experience, and explain one specific career connection."}}
        pages={}
        for day in range(1,6):
            st=student_titles[day]; student=await upsert_page(c,st,render(f"2sw-wk1-day{day}-student.html",{"COURSE_ID":COURSE_ID,**contracts[day],**student_values[day]}),slugify(st))
            tt=f"TEACHER: 2SW Wk1 Day {day} Facilitator Guide"; teacher=await upsert_page(c,tt,render("2sw-wk1-teacher.html",{"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student["url"],**contracts[day],**teacher_data[day]}),slugify(tt))
            pages[day]={"teacher":teacher,"student":student}
        expected=[]
        for day in range(1,6):
            expected.append(("SubHeader",None,f"Day {day}"))
            for page_kind in ("teacher","student"):
                page=pages[day][page_kind]
                expected.append(("Page",page["url"],page["title"]))
        expected.append(("Assignment",mapped_major["id"],MAPPED_MAJOR_TITLE))
        final=await reconcile_module_items(c,module_id,expected)
        module=await api(c,"GET",f"/courses/{COURSE_ID}/modules/{module_id}")
        final_major=await api(c,"GET",f"/courses/{COURSE_ID}/assignments/{mapped_major['id']}")
        final_pages=[await api(c,"GET",f"/courses/{COURSE_ID}/pages/{page['url']}") for day in range(1,6) for page in pages[day].values()]
        final_failures=[]
        if module.get("published") is not False: final_failures.append("module_published")
        if any(page.get("published") is not False for page in final_pages): final_failures.append("page_published")
        if final_major.get("published") is not False or float(final_major.get("points_possible") or 0)!=100 or final_major.get("grading_type")!="points" or final_major.get("omit_from_final_grade") is not False: final_failures.append("major_grading")
        if final_major.get("assignment_group_id")!=major_group.get("id") or set(final_major.get("submission_types") or [])!=MAJOR_SUBMISSION_TYPES or RUBRIC_NOTE_MARKER not in (final_major.get("description") or ""): final_failures.append("major_identity")
        support_folder,support_folder_files=await lock_folder_files(c,support_folder,SUPPORT_NAMES.values())
        for day,folder in folders.items(): folders[day],folder_files[day]=await lock_folder_files(c,folder,(path.name for path in preferred_images(ASSETS/f"day{day}")))
        if final_failures: raise RuntimeError(f"2SW Wk1 final invariant failed: {final_failures}")
        print(json.dumps({"module":{"id":module_id,"published":module["published"]},"major":{"id":final_major["id"],"published":final_major.get("published"),"points":final_major.get("points_possible"),"group":final_major.get("assignment_group_id"),"grading_type":final_major.get("grading_type"),"omit_from_final_grade":final_major.get("omit_from_final_grade")},"support_folder":{"id":support_folder["id"],"locked":support_folder["locked"],"file_count":len(support_folder_files)},"folders":{str(d):{"id":f["id"],"locked":f["locked"],"file_count":len(folder_files[d])} for d,f in folders.items()},"files":{k:v["id"] for k,v in files.items()},"pages":{str(d):{k:{"url":v["url"],"published":v["published"]} for k,v in p.items()} for d,p in pages.items()},"items":[{"id":i["id"],"position":i["position"],"title":i["title"],"type":i["type"],"page_url":i.get("page_url"),"content_id":i.get("content_id"),"published":i.get("published")} for i in final]},indent=2))

if __name__=="__main__": asyncio.run(main())
