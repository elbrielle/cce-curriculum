"""Build the unpublished 1SW Week 5 teacher/student Canvas module."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
import httpx

BASE="https://learn.irvingisd.net"; COURSE_ID=98060
MODULE_NAME="1SW Wk5: Cybersecurity, Favorite Clusters, and Capstone"
MODULE_ALIASES={MODULE_NAME,"1SW Wk5: Cyber Defenders - Cybersecurity Careers and Capstone","1SW Wk5: Cyber Defenders — Cybersecurity Careers and Capstone"}
MAPPED_MAJOR_TITLE="MAJOR 2: Cybersecurity Capstone Evidence Portfolio"
MAJOR_GROUP_NAME="Major Assessments (60%)"
RUBRIC_NOTE_MARKER='data-cce-rubric-note="cce-advisory-rubric-v1"'
MAJOR_SUBMISSION_TYPES={"online_upload","online_text_entry","media_recording"}
ROOT=Path(__file__).resolve().parents[2]; TEMPLATES=Path(__file__).parent/"templates"; ASSETS=ROOT/"cce-curriculum/resources/canvas-licensed/1sw/wk5"
SUPPORT_NAMES={"ROUTE":"wk5-cyberseek-pathway.pdf","CHECK":"wk5-red-flag-checklist.pdf","PLAN":"wk5-bootcamp-planning-template.pdf","MODEL":"wk5-bootcamp-model.pdf","CONNECTION":"wk5-favorite-cluster-connection.pdf","RUBRIC":"wk5-capstone-portfolio-rubric.pdf","REFLECTION":"wk5-reflection-update-template.pdf","REFLECTION_BI":"wk5-reflection-update-bilingual.pdf"}
REQUIRED_VISUALS={
    1:("irving-it-programs.png",),
    2:("safe-or-spoofed-red-flags.jpg",*(f"slide-{number}.jpg" for number in range(2,9))),
    3:("community-cybersecurity-bootcamp.jpg","integrity-and-original-work.png"),
    4:("it-app-exploration.png",),
    5:("postsecondary-options.png",),
}
DAY2_DECK=ASSETS/"day2/optional-whole-group/safe-or-spoofed-lesson-presentation.pptx"

def preferred_images(folder):
    return sorted(
        path for path in folder.iterdir()
        if path.suffix.lower() in {".png",".jpg",".jpeg"}
        and not (path.suffix.lower()==".png" and (path.with_suffix(".jpg").exists() or path.with_suffix(".jpeg").exists()))
    )

def preflight():
    required=[
        *(TEMPLATES/name for name in ("wk5-teacher.html",*(f"wk5-day{day}-student.html" for day in range(1,6)))),
        *(ROOT/"docs/resources/worksheets"/name for name in SUPPORT_NAMES.values()),
        *(ASSETS/f"day{day}"/name for day,names in REQUIRED_VISUALS.items() for name in names),
        DAY2_DECK,
    ]
    missing=[str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing: raise FileNotFoundError(f"1SW Wk5 preflight missing required files: {missing}")

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
    if len(module_matches)!=1: raise RuntimeError(f"Expected one 1SW Wk5 module across accepted aliases; found {len(module_matches)}")
    module=module_matches[0]
    if module.get("published") is not False: raise RuntimeError("Refusing to modify a published 1SW Wk5 module")
    groups=await paged(c,f"/courses/{COURSE_ID}/assignment_groups")
    group_matches=[entry for entry in groups if entry.get("name")==MAJOR_GROUP_NAME]
    if len(group_matches)!=1: raise RuntimeError(f"Expected one {MAJOR_GROUP_NAME!r} group; found {len(group_matches)}")
    assignments=await paged(c,f"/courses/{COURSE_ID}/assignments")
    major_matches=[entry for entry in assignments if entry.get("name")==MAPPED_MAJOR_TITLE]
    if len(major_matches)!=1: raise RuntimeError(f"Expected one mapped assignment {MAPPED_MAJOR_TITLE!r}; found {len(major_matches)}")
    major=major_matches[0]; failures=[]
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
    if folder: folder=await api(c,"GET",f"/folders/{folder['id']}")
    if not folder or folder.get("locked") is not True: raise RuntimeError(f"Canvas folder did not remain locked: {path}")
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
    unlocked=[file["id"] for file in verified if not file.get("locked")]
    if folder.get("locked") is not True or missing or unlocked:
        raise ValueError(f"Canvas folder {folder['id']} invariant failed: missing={sorted(missing)} unlocked={unlocked}")
    return folder,verified
async def find_file(c,name):
    files=await paged(c,f"/courses/{COURSE_ID}/files",{"search_term":name}); matches=[f for f in files if f.get("display_name")==name]
    if len(matches)!=1: raise ValueError(f"Expected one Canvas file named {name!r}; found {len(matches)}")
    current=await api(c,"GET",f"/files/{matches[0]['id']}")
    if current.get("locked") is not True: current=await api(c,"PUT",f"/files/{current['id']}",data={"locked":"true"})
    if current.get("locked") is not True: raise RuntimeError(f"Referenced Canvas file did not remain locked: {name}")
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
    if len(final)!=16: raise RuntimeError(f"Expected literal 16-item 1SW Wk5 module; found {len(final)}")
    for position,(item,(kind,key,title)) in enumerate(zip(final,expected),start=1):
        if item.get("position")!=position or item.get("title")!=title or item.get("published") is not False or not item_matches(item,kind,key,title):
            raise RuntimeError(f"1SW Wk5 item mismatch at position {position}: {item}")
    return final
def flow(color,title,text): return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'
def image_details(course_id,uploads):
    descriptions={2:"Email 1: free tablet prize message",3:"Email 2: Amazon order warning",4:"Email 3: company open-enrollment reminder",5:"Email 4: urgent benefits update",6:"Email 5: urgent account suspension",7:"Email 6: IT password-expiration notice",8:"Email 7: ordinary team-meeting reminder"}
    parts=[]
    for slide in range(2,9):
        file=uploads[f"slide-{slide}.jpg"]; num=slide-1
        parts.append(f'<details style="border:1px solid #cfc5dd;border-radius:8px;padding:12px 16px;margin:12px 0"><summary style="font-weight:700;color:#5a2d91;cursor:pointer">Email {num}</summary><img loading="lazy" src="/courses/{course_id}/files/{file["id"]}/preview" alt="{descriptions[slide]}" style="display:block;width:100%;max-width:760px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{course_id}/files/{file["id"]}" data-api-returntype="File"></details>')
    return "".join(parts)

async def main():
    preflight()
    token=sys.stdin.readline().strip()
    if not token: raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"},timeout=120) as c:
        existing_module,mapped_major,major_group=await canvas_preflight(c)
        module=await ensure_module(c,existing_module); module_id=module["id"]
        support_folder="course files/CCR Materials/1SW/Wk5"; support_folder_info=await ensure_folder(c,support_folder); files={}
        for key,name in SUPPORT_NAMES.items(): files[key]=await upload(c,ROOT/"docs/resources/worksheets"/name,support_folder)
        files["XELLO"]=await find_file(c,"my-career-clusters.pdf")
        xello_folder_id=files["XELLO"].get("folder_id")
        if not xello_folder_id:
            raise ValueError("Xello my-career-clusters.pdf did not report a folder_id")
        xello_folder=await api(c,"GET",f"/folders/{xello_folder_id}")
        await lock_folder_files(c,xello_folder,("my-career-clusters.pdf",))
        files["XELLO"]=await find_file(c,"my-career-clusters.pdf")
        if not files["XELLO"].get("locked"):
            raise ValueError("Xello my-career-clusters.pdf did not remain locked")
        uploads={}; folders={}
        for day in range(1,6):
            folder_path=f"course files/CCR Materials/1SW/Wk5/Day {day} Visuals"; folders[day]=await ensure_folder(c,folder_path); uploads[day]={}
            day_dir=ASSETS/f"day{day}"
            if day_dir.exists():
                for path in preferred_images(day_dir):
                    uploads[day][path.name]=await upload(c,path,folder_path)
        files["DAY2_DECK"]=await upload(c,DAY2_DECK,"course files/CCR Materials/1SW/Wk5/Day 2 Visuals")
        if not files["DAY2_DECK"].get("locked"):
            files["DAY2_DECK"]=await api(c,"PUT",f"/files/{files['DAY2_DECK']['id']}",data={"locked":"true"})
        support_folder_info,support_folder_files=await lock_folder_files(c,support_folder_info,SUPPORT_NAMES.values())
        folder_files={}
        for day,folder in folders.items():
            required=[path.name for path in preferred_images(ASSETS/f"day{day}")]
            if day==2: required.append(DAY2_DECK.name)
            folders[day],folder_files[day]=await lock_folder_files(c,folder,required)
        student_values={
          1:{"PROGRAM_IMAGE_ID":uploads[1]["irving-it-programs.png"]["id"],"ROUTE_FILE_ID":files["ROUTE"]["id"]},
          2:{"FLAGS_IMAGE_ID":uploads[2]["safe-or-spoofed-red-flags.jpg"]["id"],"CHECK_FILE_ID":files["CHECK"]["id"],"EMAIL_DETAILS":image_details(COURSE_ID,uploads[2])},
          3:{"BOOTCAMP_IMAGE_ID":uploads[3]["community-cybersecurity-bootcamp.jpg"]["id"],"PLAN_IMAGE_ID":uploads[3]["integrity-and-original-work.png"]["id"],"PLAN_FILE_ID":files["PLAN"]["id"],"MODEL_FILE_ID":files["MODEL"]["id"]},
          4:{"PROFILE_IMAGE_ID":uploads[4]["it-app-exploration.png"]["id"],"CONNECTION_FILE_ID":files["CONNECTION"]["id"]},
          5:{"OPTIONS_IMAGE_ID":uploads[5]["postsecondary-options.png"]["id"],"REFLECTION_FILE_ID":files["REFLECTION"]["id"],"REFLECTION_BI_FILE_ID":files["REFLECTION_BI"]["id"],"RUBRIC_FILE_ID":files["RUBRIC"]["id"]}}
        student_titles={1:"STUDENT: 1SW Wk5 Day 1 - Cybersecurity Career Routes",2:"STUDENT: 1SW Wk5 Day 2 - Safe or Spoofed Inbox",3:"STUDENT: 1SW Wk5 Day 3 - Community Cybersecurity Bootcamp",4:"STUDENT: 1SW Wk5 Day 4 - Xello Favorite Clusters",5:"STUDENT: 1SW Wk5 Day 5 - Capstone Goal and Reflection"}
        teacher_data={
          1:{"TITLE":"Emerging Cybersecurity Work","SUBTITLE":"50 minutes - TEKS d(1)(D)","ALERT":"<strong>Use the dated route guide as the core.</strong> H&amp;L and CyberSeek are optional live exploration. Do not promise a fixed ladder, DFW pay, or an entry-level Information Security Analyst job.","PREP":f'<ul><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["ROUTE"]["id"]}/preview">Cybersecurity Career Route Guide</a>.</li><li>Open FYF pp. 36-38 and the official BLS Information Security Analysts profile.</li><li>If using CyberSeek or H&amp;L, preflight on a student Chromebook and record the retrieval date.</li></ul>',"EVIDENCE":"<p>Formative/minor option: completed emerging-career evaluation and possible route. Full evidence includes two source facts, one source limitation, a judgment, and a current interest decision. Live vendor access is not graded.</p>","FLOW":flow("#5a2d91","Security warm-up - 5 minutes","Name a digital risk and the person or team that could help.")+flow("#4a9d2f","Source labels - 8 minutes","Distinguish program from job, national median from starting/local pay, and projection from guarantee.")+flow("#1f617a","Three-role route guide - 22 minutes","Compare support, network administration, and information security analyst; build one possible route.")+flow("#e3ad19","Emerging-career evaluation - 10 minutes","Use two facts and name one limitation of the evidence.")+flow("#1f617a","Close - 5 minutes","Share one judgment and one next research question."),"MONITOR":"<p>BLS key: Information Security Analysts protect networks and systems; typical preparation is a bachelor's degree plus related experience, although other routes exist; May 2024 national median $124,910; projected growth 29% for 2024-34 compared with about 3% for all occupations. Valid limitation: national rather than DFW-local, median rather than starting pay, or projection rather than guarantee. Accept varied routes when the student labels them as possible.</p>","SUPPORT":"<p>Pre-teach median, projected, related experience, certification, and program of study. Let students highlight the two exact facts before writing, choose a source-limit phrase, and rehearse the judgment orally.</p>","FALLBACK":"<p>The dated guide is the normal no-web route and supports absence recovery. If a live title or count differs, record the date rather than forcing it to match the worksheet.</p>"},
          2:{"TITLE":"Safe or Spoofed? Phishing Investigation","SUBTITLE":"50 minutes - TEKS d(1)(C)","ALERT":"<strong>Practice never gets sent.</strong> Use fictional people and example.com addresses only. No real credentials, links, QR codes, attachments, or district impersonation.","PREP":f'<ul><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["CHECK"]["id"]}/preview">Phishing Red-Flag Checklist</a>.</li><li>Open the seven locked Canvas email images and FYF pp. 24-25.</li><li>Post the response: Pause, verify independently, report, delete.</li></ul>',"EVIDENCE":"<p>Formative/minor option: seven decisions plus the hardest-call explanation and safe response. Do not score a student on whether their first call matches; score the evidence and revision.</p>","FLOW":flow("#5a2d91","First clue warm-up - 5 minutes","Name one clue without clicking anything.")+flow("#4a9d2f","Five red flags - 10 minutes","Model sender, urgency, private information, link/file, and writing clues.")+flow("#1f617a","Seven-email investigation - 22 minutes","Open one image at a time; students mark evidence and decide.")+flow("#e3ad19","Safe practice draft - 8 minutes","Paper/assigned-document only; use two red flags and strict fictional boundaries.")+flow("#1f617a","Response close - 5 minutes","Pause, verify independently, report, delete."),"MONITOR":"<p><strong>Key:</strong> 1 spoofed (prize, odd sender/link); 2 spoofed (amaz0n and order-check domain); 3 safe-looking (company HR, no link/private request; still verify through portal/known HR); 4 spoofed (.co sender, TODAY, update link); 5 spoofed (urgent suspension and unrelated fix domain); 6 spoofed (.co sender and portal-login link); 7 safe-looking (ordinary manager note; verify through known channel if uncertain). A polished message is not automatically safe. Hover previews a desktop URL; it does not verify the sender.</p>","SUPPORT":"<p>Read the sender and visible domain aloud, color-code each flag, let pairs talk before individual decisions, and use the sentence frame: 'I marked ___ because ___.' Do not require full translations.</p>","FALLBACK":"<p>All seven images and the checklist are in the student guide for absences. On touch devices, use visible domains and independent verification; do not require long-pressing an unknown link.</p>"},
          3:{"TITLE":"Community Cybersecurity Bootcamp","SUBTITLE":"50 minutes - TEKS d(4)(F), d(5)(A)","ALERT":"<strong>Major evidence begins:</strong> plan and flyer. Treat workbook percentages as scenario text, not current verified statistics. Canva, Adobe Express, and paper are equal.","PREP":f'<ul><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["PLAN"]["id"]}/preview">two-page Bootcamp Plan</a>.</li><li>Open FYF pp. 34-35 and prepare one teacher-made model for a fictional audience.</li><li>Confirm Canva/Adobe access only if offering those routes; paper is ready from the start.</li></ul>',"EVIDENCE":f'<p><strong>Major grade:</strong> Bootcamp Plan and Flyer supply 8 of 16 points on the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">capstone rubric</a>. Peer feedback is formative.</p>',"FLOW":flow("#5a2d91","Audience and need - 5 minutes","Choose one named audience and one unsafe choice.")+flow("#4a9d2f","Bootcamp plan - 20 minutes","Finish goals, activity, place/time, accurate advice, and safe sign-up route.")+flow("#1f617a","Flyer prototype - 18 minutes","Paper, Canva, or Adobe; original/credited content and no personal contact details.")+flow("#e3ad19","One-note feedback and revision - 7 minutes","One clear part, one next revision; absent-peer route uses self-check."),"MONITOR":"<p>Look for one audience, two actions participants can do, and a matching activity. Accept fictional 'sign up with your teacher/library desk' language. Reject real student/family contact details and guarantees such as 'this stops every scam.'</p>","SUPPORT":"<p>Offer an audience/need choice bank, sentence starters, a teacher model, and oral planning before writing. Students may label a diagram instead of producing long prose.</p>","FALLBACK":"<p>Paper is equal, not a lesser backup. If absent, complete the same plan and paper flyer; use the checklist instead of peer feedback.</p>"},
          4:{"TITLE":"Xello Favorite Clusters","SUBTITLE":"50 minutes - TEKS d(1)(C), d(3)(A)","ALERT":"<strong>Required district task:</strong> protect 40 minutes for Favorite clusters and verify at least one saved cluster. Save Careers belongs later. H&amp;L is optional.","PREP":f'<ul><li>Check rosters and the Completion Standards report.</li><li>Open the licensed <a href="/courses/{COURSE_ID}/files/{files["XELLO"]["id"]}/preview">My career clusters teacher guide</a> as optional background. It is an expanded 90-minute lesson with extra prerequisites; do not impose those extras today.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["CONNECTION"]["id"]}/preview">Favorite Cluster Connection</a>.</li></ul>',"EVIDENCE":"<p>Required completion evidence: at least one saved Favorite cluster in the Xello report. The connection sheet is formative or a coherent minor checkpoint; login success itself is not graded.</p>","FLOW":flow("#5a2d91","Cluster launch - 5 minutes","Define a career cluster as a family of related careers and model About Me navigation.")+flow("#4a9d2f","Explore clusters and careers - 30 minutes","Read descriptions, inspect example careers, and compare more than one cluster.")+flow("#1f617a","Save and verify - 5 minutes","Save at least one Favorite cluster and confirm it appears.")+flow("#e3ad19","Career connection - 10 minutes","Name one career, a reason, and a high school experience to investigate."),"MONITOR":"<p>Navigation: district SSO &gt; Xello &gt; About Me &gt; Favorite clusters. Minimum: one saved cluster. Do not require Matchmaker, three saved careers, two clusters, or a Xello Assignment for this 40-minute district minimum.</p>","SUPPORT":"<p>Read cluster descriptions aloud, provide cluster/career/reason stems, pair for navigation, and accept an oral reason recorded by the teacher before the student writes.</p>","FALLBACK":"<p>Record access issues. Student completes the paper connection with a known cluster, then completes the required Xello save during the next catch-up block. Do not create a second account.</p>"},
          5:{"TITLE":"Capstone Goal, Original Symbol, and Reflection","SUBTITLE":"50 minutes - TEKS d(1)(C), d(3)(A), d(4)(F)","ALERT":"<strong>One 16-point major grade:</strong> score the durable packet, not the gallery, public speaking, platform clicks, fabrication, or Evidence Log. Paper and digital artifacts are equal.","PREP":f'<ul><li>Return Week 0 reflections and the Day 3 plan/flyer.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["REFLECTION"]["id"]}/preview">one-page update</a> and <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">16-point rubric</a>.</li><li>Remind students to retrieve the CCE Six-Weeks Evidence Log from the CCE binder or teacher-designated digital folder named in Week 0. It stays with the student.</li><li>Provide paper/markers. Canva or Adobe is optional. If demonstrating a campus laser, only a trained authorized operator uses the machine under the current campus SOP and manufacturer guidance.</li></ul>',"EVIDENCE":f'<p><strong>Major grade:</strong> Plan, Flyer, Postsecondary Goal/Original Symbol, and Career Reflection, 16 points. Convert using the district-band table on the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">rubric</a>. This is one major, not four assignments. Entry 1 is a 2- to 3-minute transfer into the student-owned Evidence Log, not a fifth artifact, upload, or grade.</p>',"FLOW":flow("#5a2d91","Goal before tool - 5 minutes","Complete the goal sentence and name a course/program/experience to investigate.")+flow("#4a9d2f","Original symbol - 20 minutes","Combine simple shapes on paper, Canva, or Adobe; no traced institutional marks.")+flow("#1f617a","Career Journey update - 20 minutes","Compare Week 0, cite one specific activity/result, state current direction and next step.")+flow("#e3ad19","Packet check - 5 minutes","Plan, flyer, symbol/goal, reflection; copy five short phrases from the open update into Evidence Log Entry 1 or an Entry 1 hold note."),"MONITOR":"<p>Full-credit evidence is specific, not necessarily enthusiastic about IT. The artifact must explain a goal and name a route to investigate. Fabrication does not affect points. During the packet check, look for five short Entry 1 phrases copied from the open update: artifact, skill, visible action, revision or recovery, and next step. Students return the log to the named CCE storage place; do not collect or grade it. Use the rubric conversion: 16/15 Masters, 14/13 Meets, 12 Approaches, 11/10 Needs Improvement; 9 or below follows campus insufficient-evidence/reassessment practice.</p>","SUPPORT":"<p>Use a two-shape menu, complete the goal sentence orally first, place Week 0 and Week 5 pages side by side, and offer sentence stems or speech-to-text. Do not require a blanket translation.</p>","FALLBACK":"<p>No design tool: paper. No laser: no change. Absent: complete the same four-piece packet privately. Missing earlier evidence triggers the campus reassessment/catch-up route, not a machine or attendance penalty. If the Evidence Log is missing, students copy the same five short phrases from the open Career Journey Update under <strong>Entry 1 hold</strong> in the CCE notebook or teacher-designated digital folder, then transfer them later. Do not reconstruct or upload old work.</p>"}}
        teacher_data[2].update({
          "TITLE":"Safe or Spoofed? Phishing and Integrity",
          "SUBTITLE":"50 minutes - TEKS d(4)(F)",
          "PREP":f'<ul><li>Open the <a href="/courses/{COURSE_ID}/files/{files["DAY2_DECK"]["id"]}/preview">optional whole-group lesson presentation</a>; it carries the bellringer, model, paced email reveals, midpoint check, and close.</li><li>Post or print the <a href="/courses/{COURSE_ID}/files/{files["CHECK"]["id"]}/preview">Phishing Red-Flag Checklist</a>. Default printing is one checklist per student only when students are not annotating digitally.</li><li>Confirm FYF pp. 24-25 and the seven locked email images are available. Post the response: Pause, verify independently, report, delete.</li></ul>',
          "EVIDENCE":"<p>Formative/minor option: seven decisions, hardest-call explanation, independent verification response, and integrity explanation. Score visible evidence and revision, not whether the student's first call matches the key.</p>",
          "MONITOR":"<p><strong>Key:</strong> 1 spoofed (prize, odd sender/link); 2 spoofed (amaz0n and order-check domain); 3 safe-looking (company HR, no link/private request; still verify through portal/known HR); 4 spoofed (.co sender, TODAY, update link); 5 spoofed (urgent suspension and unrelated fix domain); 6 spoofed (.co sender and portal-login link); 7 safe-looking (ordinary manager note; verify through known channel if uncertain). Safe-looking is not proven safe. A practice message sent to a real person would be dishonest and could cause harm; it stays fictional and private.</p>"})
        teacher_data[3].update({
          "SUBTITLE":"50 minutes - TEKS d(4)(F)",
          "PREP":f'<ul><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["PLAN"]["id"]}/preview">two-page Bootcamp Plan</a> and open the <a href="/courses/{COURSE_ID}/files/{files["MODEL"]["id"]}/preview">completed teacher model</a>.</li><li>Open FYF pp. 34-35.</li><li>Confirm Canva/Adobe access only if offering those routes; paper is ready from the start.</li></ul>',
          "EVIDENCE":f'<p><strong>Major grade:</strong> Bootcamp Plan and Flyer supply 8 of 16 points on the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">capstone rubric</a>. Full evidence includes accurate advice, one behind-the-scenes work task, and one privacy/integrity rule. Peer feedback is formative.</p>',
          "FLOW":flow("#5a2d91","Audience and need - 5 minutes","Choose one named audience and one unsafe choice.")+flow("#4a9d2f","Model and criteria - 8 minutes","Notice how goals, activity, work ethic, and privacy fit one audience.")+flow("#1f617a","Bootcamp plan - 18 minutes","Complete all seven sections before designing.")+flow("#e3ad19","Flyer prototype - 14 minutes","Paper, Canva, or Adobe; original/credited content and safe sign-up.")+flow("#1f617a","Self-check and submit - 5 minutes","Use the checklist; partner feedback is optional if time remains."),
          "MONITOR":"<p>Look for one audience, two actions participants can do, a matching activity, an accurate safety action, one behind-the-scenes preparation task, and one privacy/integrity rule. Accept fictional 'sign up with your teacher/library desk' language. Reject real contact details and guarantees such as 'this stops every scam.'</p>"})
        teacher_data[4].update({
          "SUBTITLE":"50 minutes - TEKS d(1)(C)"})
        teacher_data[5].update({
          "TITLE":"Capstone Goal, Transitions, and Reflection",
          "SUBTITLE":"50 minutes - TEKS d(3)(A)",
          "PREP":f'<ul><li>Return Week 0 reflections and the Day 3 plan/flyer.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["REFLECTION"]["id"]}/preview">two-page update</a>, optional <a href="/courses/{COURSE_ID}/files/{files["REFLECTION_BI"]["id"]}/preview">bilingual language support</a>, and <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">16-point rubric</a>.</li><li>Remind students to retrieve the CCE Six-Weeks Evidence Log from the CCE binder or teacher-designated digital folder named in Week 0. It stays with the student.</li><li>Provide paper/markers. Canva or Adobe is optional. Laser fabrication is not part of the required lesson or grade.</li></ul>',
          "EVIDENCE":f'<p><strong>Major grade:</strong> Plan, Flyer, Postsecondary Goal/Original Symbol, and Career Reflection with two transition steps, 16 points. Convert using the district-band table on the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">rubric</a>. This is one major, not four assignments. Entry 1 is a 2- to 3-minute transfer into the student-owned Evidence Log, not a fifth artifact, upload, or grade.</p>',
          "FLOW":flow("#5a2d91","Goal before tool - 5 minutes","Complete the goal sentence and name a course, program, or experience to investigate.")+flow("#4a9d2f","Original symbol - 15 minutes","Combine simple shapes on paper, Canva, or Adobe; no traced institutional marks.")+flow("#1f617a","Career Journey update - 20 minutes","Cite one specific example and write both transition steps.")+flow("#e3ad19","Packet audit and submission - 10 minutes","Check four artifacts; use 2 to 3 minutes to copy five phrases from the open update into Evidence Log Entry 1 or an Entry 1 hold note."),
          "MONITOR":"<p>Full-credit evidence is specific, not necessarily enthusiastic about IT. The reflection must name one action before ninth grade and one high-school action that prepares for college, training, military service, or work. Fabrication does not affect points. During the packet audit, look for five short Entry 1 phrases copied from the open update: artifact, skill, visible action, revision or recovery, and next step. Students return the log to the named CCE storage place; do not collect or grade it. Use the rubric conversion: 16/15 Masters, 14/13 Meets, 12 Approaches, 11/10 Needs Improvement; 9 or below follows campus insufficient-evidence/reassessment practice.</p>",
          "SUPPORT":"<p>Use a two-shape menu, complete the goal sentence orally first, place Week 0 and Week 5 pages side by side, and offer the bilingual labels/stems or speech-to-text. The support page adds access without replacing the aligned evidence.</p>",
          "FALLBACK":"<p>No design tool: paper. Absent: complete the same four-piece packet privately. If the Week 0 page is missing, use the recovery box. Missing evidence triggers the campus reassessment/catch-up route, not an attendance or technology penalty. If the Evidence Log is missing, students copy the same five short phrases from the open Career Journey Update under <strong>Entry 1 hold</strong> in the CCE notebook or teacher-designated digital folder, then transfer them later. Do not reconstruct or upload old work.</p>"})
        contracts={
          1:{"TOPIC":"Emerging Cybersecurity Work","OBJECTIVE":"Students will research and evaluate Information Security Analyst as an emerging career using dated work, preparation, wage, and outlook evidence.","TEKS":"d(1)(D)","DOL":"Completed emerging-career evaluation with two source facts, one source limitation, a defensible judgment, and one possible career route."},
          2:{"TOPIC":"Phishing and Integrity","OBJECTIVE":"Students will define and identify work ethic and integrity by evaluating suspicious messages and choosing an ethical cybersecurity response.","TEKS":"d(4)(F)","DOL":"Seven evidence-based message decisions, a hardest-call explanation, an independent verification response, and an integrity explanation."},
          3:{"TOPIC":"Work Ethic","OBJECTIVE":"Students will define and identify work ethic and integrity by planning accurate, original, and privacy-safe work for a community cybersecurity lesson.","TEKS":"d(4)(F)","DOL":"Completed bootcamp plan and flyer prototype with accurate advice, one behind-the-scenes work task, and one privacy or integrity rule."},
          4:{"TOPIC":"Favorite Clusters","OBJECTIVE":"Students will identify a career opportunity within a career cluster and explain how it connects to an interest using Xello and a written connection.","TEKS":"d(1)(C)","DOL":"At least one saved Xello Favorite cluster and one written cluster-career-interest connection."},
          5:{"TOPIC":"Transition Planning","OBJECTIVE":"Students will describe actions that support the transition from middle school to high school and from high school to a postsecondary goal.","TEKS":"d(3)(A)","DOL":"Original goal symbol, two transition actions, and a specific Career Journey update submitted with the four-part capstone packet."}}
        pages={}
        for day in range(1,6):
            st=student_titles[day]; student=await upsert_page(c,st,render(f"wk5-day{day}-student.html",{"COURSE_ID":COURSE_ID,**student_values[day]}),slugify(st))
            tt=f"TEACHER: 1SW Wk5 Day {day} Facilitator Guide"; teacher=await upsert_page(c,tt,render("wk5-teacher.html",{"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student["url"],**contracts[day],**teacher_data[day]}),slugify(tt))
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
        support_folder_info,support_folder_files=await lock_folder_files(c,support_folder_info,SUPPORT_NAMES.values())
        for day,folder in folders.items():
            required=[path.name for path in preferred_images(ASSETS/f"day{day}")]
            if day==2: required.append(DAY2_DECK.name)
            folders[day],folder_files[day]=await lock_folder_files(c,folder,required)
        xello_folder,xello_folder_files=await lock_folder_files(c,xello_folder,("my-career-clusters.pdf",))
        files["XELLO"]=await find_file(c,"my-career-clusters.pdf")
        if final_failures: raise RuntimeError(f"1SW Wk5 final invariant failed: {final_failures}")
        print(json.dumps({"module":{"id":module_id,"published":module["published"]},"major":{"id":final_major["id"],"published":final_major.get("published"),"points":final_major.get("points_possible"),"group":final_major.get("assignment_group_id"),"grading_type":final_major.get("grading_type"),"omit_from_final_grade":final_major.get("omit_from_final_grade")},"support_folder":{"id":support_folder_info["id"],"locked":support_folder_info["locked"],"file_count":len(support_folder_files)},"folders":{str(d):{"id":f["id"],"locked":f["locked"],"file_count":len(folder_files[d])} for d,f in folders.items()},"files":{k:v["id"] for k,v in files.items()},"pages":{str(d):{k:{"url":v["url"],"published":v["published"]} for k,v in p.items()} for d,p in pages.items()},"items":[{"id":i["id"],"position":i["position"],"title":i["title"],"type":i["type"],"page_url":i.get("page_url"),"content_id":i.get("content_id"),"published":i.get("published")} for i in final]},indent=2))

if __name__=="__main__": asyncio.run(main())
