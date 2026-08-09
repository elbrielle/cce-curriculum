"""Build the unpublished 2SW Week 1 teacher/student Canvas module."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
import httpx

BASE="https://learn.irvingisd.net"; COURSE_ID=98060
MODULE_NAME="2SW Wk1: Order in the Court - Legal Studies"
ROOT=Path(__file__).resolve().parents[2]; TEMPLATES=Path(__file__).parent/"templates"; ASSETS=ROOT/"cce-curriculum/resources/canvas-licensed/2sw/wk1"

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
async def upsert_item(c,module_id,page,title):
    items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); item=next((i for i in items if i.get("page_url")==page["url"]),None)
    if item: return await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",data={"module_item[title]":title})
    return await api(c,"POST",f"/courses/{COURSE_ID}/modules/{module_id}/items",data={"module_item[type]":"Page","module_item[page_url]":page["url"],"module_item[title]":title})
def flow(color,title,text): return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'
def detail_images(uploads,names,alts):
    parts=[]
    for index,name in enumerate(names,start=1):
        file=uploads[name]
        parts.append(f'<p><img loading="lazy" src="/courses/{COURSE_ID}/files/{file["id"]}/preview" alt="{alts[index-1]}" style="display:block;width:100%;max-width:680px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file["id"]}" data-api-returntype="File"></p>')
    return "".join(parts)

async def main():
    token=sys.stdin.readline().strip()
    if not token: raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"},timeout=120) as c:
        module=await ensure_module(c); module_id=module["id"]
        support_names={"CAREER":"career-research-worksheet.pdf","KIT":"2sw-wk1-emergency-kit-plan.pdf","TOWN":"2sw-wk1-city-council-plan.pdf","ARGUMENT":"2sw-wk1-policy-argument-and-evidence.pdf","ENTREPRENEUR":"2sw-wk1-legal-entrepreneur-card.pdf","RUBRIC":"2sw-wk1-position-paper-rubric.pdf","CONNECTION":"2sw-wk1-xello-life-experience-connection.pdf"}
        support_folder="course files/CCR Materials/2SW/Wk1"; await ensure_folder(c,support_folder); files={}
        for key,name in support_names.items(): files[key]=await upload(c,ROOT/"docs/resources/worksheets"/name,support_folder)
        files["XELLO"]=await find_file(c,"experiences.pdf")
        uploads={}; folders={}
        for day in range(1,6):
            folder_path=f"course files/CCR Materials/2SW/Wk1/Day {day} Visuals"; folders[day]=await ensure_folder(c,folder_path); uploads[day]={}
            for path in sorted((ASSETS/f"day{day}").glob("*.png")): uploads[day][path.name]=await upload(c,path,folder_path)
        student_values={
          1:{"OPENER_IMAGE_ID":uploads[1]["law-cluster-opener.png"]["id"],"PROGRAM_IMAGE_ID":uploads[1]["irving-legal-programs.png"]["id"],"CAREER_FILE_ID":files["CAREER"]["id"]},
          2:{"PAGE1_IMAGE_ID":uploads[2]["emergency-essentials-056.png"]["id"],"PAGE2_IMAGE_ID":uploads[2]["emergency-essentials-057.png"]["id"],"PLAN_FILE_ID":files["KIT"]["id"]},
          3:{"PAGE1_IMAGE_ID":uploads[3]["city-council-046.png"]["id"],"PLAN_FILE_ID":files["TOWN"]["id"],"SOURCE_IMAGES":detail_images(uploads[3],["city-council-047.png","city-council-048.png","city-council-049.png"],["Find Your Future town-design directions","Find Your Future problem scan and ordinance-drafting directions","Find Your Future partner-review directions"])},
          4:{"POLICY_IMAGE_ID":uploads[4]["policy-showdown-050.png"]["id"],"ARGUMENT_FILE_ID":files["ARGUMENT"]["id"],"ENTREPRENEUR_FILE_ID":files["ENTREPRENEUR"]["id"]},
          5:{"RUBRIC_FILE_ID":files["RUBRIC"]["id"],"CONNECTION_FILE_ID":files["CONNECTION"]["id"],"PROGRAM_IMAGE_ID":uploads[5]["irving-legal-programs.png"]["id"]}}
        student_titles={1:"STUDENT: 2SW Wk1 Day 1 - Explore Legal Careers",2:"STUDENT: 2SW Wk1 Day 2 - Emergency Kit Decisions",3:"STUDENT: 2SW Wk1 Day 3 - City Council Ordinances",4:"STUDENT: 2SW Wk1 Day 4 - Policy Showdown",5:"STUDENT: 2SW Wk1 Day 5 - Legal Career Evidence and Xello"}
        teacher_data={
          1:{"TITLE":"Law and Public Safety Cluster Tour","SUBTITLE":"50 minutes · TEKS d(1)(B), d(1)(C)","ALERT":"<strong>Keep the lesson source-controlled.</strong> H&amp;L is an optional browse, not the only research route. Salary claims need a source, geography, data year, and salary type.","PREP":f'<ul><li>Open FYF pp. 39 and 56-58 in the student guide.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["CAREER"]["id"]}/preview">Career Research Worksheet</a>.</li><li>Prepare two or three dated legal-career cards or approved profiles. Preflight H&amp;L only if you plan to offer it.</li></ul>',"EVIDENCE":"<p>Formative/minor option: one complete six-field career research sheet plus a two-career comparison. Platform access and career enthusiasm are not graded.</p>","FLOW":flow("#5a2d91","Safety-inspector warm-up · 5 minutes","Choose continue, delay, or stop; name information needed before deciding.")+flow("#4a9d2f","Cluster and Irving routes · 12 minutes","Read the opener and distinguish the broad cluster from Legal Studies and Criminal Justice programs.")+flow("#1f617a","Career research · 25 minutes","Use assigned dated sources; H&amp;L may supplement.")+flow("#e3ad19","Compare and close · 8 minutes","Compare preparation, one task, and one carefully labeled salary fact."),"MONITOR":"<p>Require career name, interest/not-interest reason, job description, preparation, salary label, and tools/skills. Reject “DFW starting salary” when the source only provides a national median. A career may connect to more than one program.</p>","SUPPORT":"<p>Model one row without completing the student's chosen career. Pre-teach paralegal, court reporter, ordinance, and due process. Let students dictate notes or highlight the exact source sentence before paraphrasing.</p>","FALLBACK":"<p>The embedded workbook pages and teacher-provided career cards are the normal no-login route. An absent student completes the same sheet without watching a vendor video.</p>"},
          2:{"TITLE":"Emergency Essentials Kit Design","SUBTITLE":"50 minutes · TEKS d(1)(C)","ALERT":"<strong>No open-web research is required.</strong> The licensed workbook list and decision plan contain the core task. Paper and an approved digital design are equal routes.","PREP":f'<ul><li>Open FYF pp. 50-51 in the student guide.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["KIT"]["id"]}/preview">Emergency Kit Decision Plan</a>.</li><li>Have paper and pencils ready; digital design is optional.</li></ul>',"EVIDENCE":"<p>Formative/minor option: exactly ten labeled items, three scenario-specific reasons, and one revision after feedback. Artistic polish does not affect the score.</p>","FLOW":flow("#5a2d91","Five-minute grab warm-up · 5 minutes","Name the first item and test whether it still helps if power or water fails.")+flow("#4a9d2f","Scenario and constraints · 8 minutes","Choose earthquake, fire evacuation, or flood; define the urgent problem.")+flow("#1f617a","Select, design, defend · 27 minutes","Choose exactly ten workbook items, label them, and defend the top three.")+flow("#e3ad19","Feedback and revision · 8 minutes","Partner or self-check; record one change.")+flow("#1f617a","Ranked close · 2 minutes","Name the most critical item and why."),"MONITOR":"<p>Count ten, then look for scenario fit. A plausible rationale matters more than one universal answer. Redirect comfort-only lists by asking which choice addresses water, first aid, signaling, shelter, breathing, or evacuation.</p>","SUPPORT":"<p>Read the item list aloud, provide scenario icons and the frame “I chose ___ because in a ___, people need ___.” Students may label instead of drawing detailed objects.</p>","FALLBACK":"<p>No device is needed. An absent student uses the embedded pages and self-check. Do not require a partner or a Canva account.</p>"},
          3:{"TITLE":"City Council in Action","SUBTITLE":"50 minutes · TEKS d(1)(C)","ALERT":"<strong>Protect the causal chain:</strong> town features create problems; problems create ordinances. A wish is not a law, and a consequence must be enforceable.","PREP":f'<ul><li>Open FYF pp. 40-43 in the student guide.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["TOWN"]["id"]}/preview">Town and Ordinance Plan</a>.</li><li>Prepare one model problem and ordinance for a town students are not using.</li></ul>',"EVIDENCE":"<p>Formative/minor option: town plan, four-problem scan, two ordinances with rule/reason/consequence, and one documented revision.</p>","FLOW":flow("#5a2d91","Rule warm-up · 5 minutes","Name a city rule and who has authority to make it.")+flow("#4a9d2f","Council role and three tests · 7 minutes","Clear, fair, and realistic to enforce.")+flow("#1f617a","Town, problems, and laws · 30 minutes","10 minutes town, 8 minutes problem scan, 12 minutes ordinances.")+flow("#e3ad19","Review and revise · 5 minutes","Partner or self-check one ordinance.")+flow("#1f617a","Career close · 3 minutes","Name a worker who would help explain, administer, or enforce one ordinance."),"MONITOR":"<p>Lap 1: town name, climate, transportation. Lap 2: all four problem rows. Lap 3: two rules with reasons and realistic consequences. Model a problem row for the class if several students stall.</p>","SUPPORT":"<p>Give one constraint, such as a snowy climate, to students who cannot start. Use the printed model row and the sentence frame in the student guide. Sketches and oral rehearsal are valid supports.</p>","FALLBACK":"<p>The Canvas images and printable contain the whole task. An absent student uses the self-check in place of peer feedback.</p>"},
          4:{"TITLE":"Policy Showdown and Legal Entrepreneurship","SUBTITLE":"50 minutes · TEKS d(3)(H), d(3)(I)","ALERT":"<strong>Use only the controlled hypothetical and evidence bank.</strong> Keep the discussion away from real cases and families. Written argument is an equal route to oral presentation.","PREP":f'<ul><li>Open FYF pp. 44-47 as the licensed protocol model.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["ARGUMENT"]["id"]}/preview">Legal Review Argument and Evidence Sheet</a> and <a href="/courses/{COURSE_ID}/files/{files["ENTREPRENEUR"]["id"]}/preview">Entrepreneur Card</a>.</li><li>Assign sides and prepare teacher-approved association/career sources. Do not require a five-minute Google search.</li></ul>',"EVIDENCE":f'<p><strong>Major evidence begins:</strong> final personal position plus Entrepreneur Card, scored with the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">16-point rubric</a>. Assigned-side speaking is practice, not graded performance.</p>',"FLOW":flow("#5a2d91","Initial decision · 5 minutes","Private one-sentence reaction; students may pass on sharing.")+flow("#4a9d2f","Protocol and policy · 8 minutes","Review support, oppose, judge, and revise roles.")+flow("#1f617a","Prepare, present/read, and judge · 20 minutes","Use three evidence notes and one ruling. Written exchange is equal.")+flow("#e3ad19","Entrepreneur and association card · 10 minutes","Use a teacher-approved source and record date.")+flow("#1f617a","Personal-position draft · 7 minutes","Students may differ from the assigned side."),"MONITOR":"<p>There is no required yes/no answer. Full evidence names a policy detail, explains why it matters, and addresses a benefit, risk, opposing idea, or safeguard. Association must plausibly serve the selected career; accept another verified association.</p>","SUPPORT":"<p>Read the policy aloud, color-code the two evidence columns, and provide the stems “This detail matters because…” and “I would revise the policy by…”. Permit speech-to-text or a teacher-scribed response when documented.</p>","FALLBACK":"<p>No live web or H&amp;L is required. An absent or non-speaking student reads both evidence columns and submits written arguments for both sides plus a ruling.</p>"},
          5:{"TITLE":"Position Revision and Xello Life Experiences","SUBTITLE":"50 minutes · TEKS d(1)(C), d(3)(H)","ALERT":"<strong>Required district task:</strong> protect 10 minutes for Xello Life experiences and verify at least one saved entry. H&amp;L and eDynamic are supplemental.","PREP":f'<ul><li>Open the Completion Standards report and check rosters.</li><li>Open the licensed <a href="/courses/{COURSE_ID}/files/{files["XELLO"]["id"]}/preview">My Experiences teacher plan</a> as background.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["CONNECTION"]["id"]}/preview">Life Experience Connection</a> and <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">position-paper rubric</a>.</li></ul>',"EVIDENCE":f'<p><strong>One major grade:</strong> final position plus Entrepreneur Card, 16 points. Required Xello completion is recorded separately as a completion checkpoint or embedded minor evidence; login success is not part of the major.</p>',"FLOW":flow("#5a2d91","Career-fit warm-up · 5 minutes","Interested, unsure, or not interested—with one job-detail reason.")+flow("#4a9d2f","Revise and submit · 10 minutes","Use rubric: position, two details, career connection, completed card.")+flow("#1f617a","Xello Life experiences · 10 minutes","About Me > Experiences; add and save at least one life experience.")+flow("#e3ad19","Experience-to-career connection · 15 minutes","Name what the experience shows and connect it to a task.")+flow("#1f617a","Report check and catch-up · 7 minutes","Verify saves; paper route for access issues.")+flow("#5a2d91","Close · 3 minutes","Name one next question about a legal career or route."),"MONITOR":"<p>Xello minimum: at least one saved life experience. Students control which non-private experience they share. A valid connection names what the student did or learned and a specific career task. A well-supported “not a fit” remains valid.</p>","SUPPORT":"<p>Offer examples by category—home responsibility, team, hobby, school project, club, volunteering—without requiring sensitive disclosure. Students may rehearse orally and use the printed frame.</p>","FALLBACK":"<p>If Xello fails, record the access issue and collect the paper connection. The required save moves to the next catch-up block. H&amp;L favorites and eDynamic preview may be omitted with no loss of core evidence.</p>"}}
        pages={}; order=[]
        for day in range(1,6):
            st=student_titles[day]; student=await upsert_page(c,st,render(f"2sw-wk1-day{day}-student.html",{"COURSE_ID":COURSE_ID,**student_values[day]}),slugify(st))
            tt=f"TEACHER: 2SW Wk1 Day {day} Facilitator Guide"; teacher=await upsert_page(c,tt,render("2sw-wk1-teacher.html",{"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student["url"],**teacher_data[day]}),slugify(tt))
            await upsert_item(c,module_id,teacher,tt); await upsert_item(c,module_id,student,st); pages[day]={"teacher":teacher,"student":student}; order.extend([(teacher["url"],tt),(student["url"],st)])
        items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); by_url={i.get("page_url"):i for i in items}
        for position,(url,title) in reversed(list(enumerate(order,start=1))): await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{by_url[url]['id']}",data={"module_item[position]":position,"module_item[title]":title})
        final=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); module=await api(c,"GET",f"/courses/{COURSE_ID}/modules/{module_id}")
        print(json.dumps({"module":{"id":module_id,"published":module["published"]},"folders":{str(d):{"id":f["id"],"locked":f["locked"]} for d,f in folders.items()},"files":{k:v["id"] for k,v in files.items()},"pages":{str(d):{k:{"url":v["url"],"published":v["published"]} for k,v in p.items()} for d,p in pages.items()},"items":[{"id":i["id"],"position":i["position"],"title":i["title"],"page_url":i.get("page_url")} for i in final]},indent=2))

asyncio.run(main())
