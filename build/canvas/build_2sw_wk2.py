"""Build the unpublished 2SW Week 2 teacher/student Canvas module."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
import httpx

BASE="https://learn.irvingisd.net"; COURSE_ID=98060
MODULE_NAME="2SW Wk2: First Responders - Evidence, Response, and Handoff"
DISCUSSION_TITLE="PRACTICE: Clinton Lake Counterevidence Exchange"
MAPPED_MAJOR_TITLE="MAJOR 2: Patient Care Report and Complication Plan"
MAJOR_GROUP_NAME="Major Assessments (60%)"
RUBRIC_NOTE_MARKER='data-cce-rubric-note="cce-advisory-rubric-v1"'
MAJOR_SUBMISSION_TYPES={"online_upload","online_text_entry"}
LEGACY_MAJOR_SUBMISSION_TYPES={"online_upload","online_text_entry","media_recording"}
ROOT=Path(__file__).resolve().parents[2]; TEMPLATES=Path(__file__).parent/"templates"; ASSETS=ROOT/"cce-curriculum/resources/canvas-licensed/2sw/wk2"

SUPPORT_NAMES={"ROUTE":"2sw-wk2-first-responder-route-guide.pdf","TRACKER":"2sw-wk2-clinton-lake-evidence-tracker.pdf","SIM":"2sw-wk2-trail-simulation-record.pdf","PCR":"2sw-wk2-patient-care-report.pdf","RUBRIC":"2sw-wk2-pcr-rubric.pdf","REFLECTION":"2sw-wk2-integrity-career-reflection.pdf"}
CLUSTER_OPENER=ROOT/"cce-curriculum/resources/canvas-licensed/2sw/wk1/day1/law-cluster-opener.jpg"
VISUAL_PATHS={
    1:(CLUSTER_OPENER,ASSETS/"day1/irving-first-responder-programs.png"),
    2:tuple(ASSETS/f"day2/{name}" for name in (
        "file-1-upright.png","file-2-upright.png","file-3-upright.png",
        "file-4-upright.png","slide-6.png","file-6-upright.png",
    )),
    3:tuple(ASSETS/f"day3/{name}" for name in ("injured-trail-intro.png","slide-2.png","slide-3.png")),
    4:tuple(ASSETS/f"day4/{name}" for name in ("injured-trail-complications.png","injured-trail-report.png")),
    5:(ASSETS/"day5/law-public-safety-app.png",),
}

def preflight():
    required=[
        *(TEMPLATES/name for name in ("2sw-wk2-teacher.html",*(f"2sw-wk2-day{day}-student.html" for day in range(1,6)))),
        *(ROOT/"docs/resources/worksheets"/name for name in SUPPORT_NAMES.values()),
        *(path for paths in VISUAL_PATHS.values() for path in paths),
    ]
    missing=[str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing: raise FileNotFoundError(f"2SW Wk2 preflight missing required files: {missing}")

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
    matches=[entry for entry in modules if entry.get("name")==MODULE_NAME]
    if len(matches)!=1: raise RuntimeError(f"Expected one {MODULE_NAME!r} module; found {len(matches)}")
    module=matches[0]
    if module.get("published") is not False: raise RuntimeError("Refusing to modify a published 2SW Wk2 module")
    items=await paged(c,f"/courses/{COURSE_ID}/modules/{module['id']}/items")
    if any(item.get("published") is not False for item in items): raise RuntimeError("Refusing to modify 2SW Wk2 with a published module item")
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
    current_routes=frozenset(major.get("submission_types") or [])
    if current_routes not in {frozenset(MAJOR_SUBMISSION_TYPES),frozenset(LEGACY_MAJOR_SUBMISSION_TYPES)}: failures.append("submission_types")
    if RUBRIC_NOTE_MARKER not in (major.get("description") or ""): failures.append("rubric_marker")
    if failures: raise RuntimeError(f"Mapped Major preflight failed: {failures}")
    topics=await paged(c,f"/courses/{COURSE_ID}/discussion_topics")
    discussion_matches=[entry for entry in topics if entry.get("title")==DISCUSSION_TITLE]
    if len(discussion_matches)>1: raise RuntimeError(f"Expected at most one {DISCUSSION_TITLE!r}; found {len(discussion_matches)}")
    if discussion_matches and (discussion_matches[0].get("published") is not False or discussion_matches[0].get("assignment_id")):
        raise RuntimeError("Practice discussion must be unpublished and ungraded before mutation")
    return module,major,group_matches[0],discussion_matches[0] if discussion_matches else None

async def ensure_module(c,module):
    return await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module['id']}",data={"module[name]":MODULE_NAME,"module[published]":"false"})
async def normalize_major_assignment(c,major,group):
    marker=re.search(r'<div data-cce-rubric-note="cce-advisory-rubric-v1".*?</div>',major.get("description") or "",flags=re.I|re.S)
    if marker is None: raise RuntimeError("Mapped Major rubric marker disappeared before normalization")
    description=(
        '<p><strong>Mapped Major assessment.</strong> Submit the completed two-page Patient Care Report and Safety Plan '
        'through private text entry or file upload. A labeled paper copy is teacher-collected. Speaking and physical '
        'technique are not graded, and a media recording alone is not this evidence.</p>'
        + marker.group(0)
    )
    data={
        "assignment[name]":MAPPED_MAJOR_TITLE,
        "assignment[description]":description,
        "assignment[assignment_group_id]":str(group["id"]),
        "assignment[points_possible]":"100",
        "assignment[grading_type]":"points",
        "assignment[omit_from_final_grade]":"false",
        "assignment[published]":"false",
        "assignment[submission_types][]":["online_upload","online_text_entry"],
    }
    await api(c,"PUT",f"/courses/{COURSE_ID}/assignments/{major['id']}",data=data)
    current=await api(c,"GET",f"/courses/{COURSE_ID}/assignments/{major['id']}")
    failures=[]
    if current.get("published") is not False: failures.append("published")
    if float(current.get("points_possible") or 0)!=100: failures.append("points_possible")
    if current.get("grading_type")!="points": failures.append("grading_type")
    if current.get("omit_from_final_grade") is not False: failures.append("omit_from_final_grade")
    if current.get("assignment_group_id")!=group.get("id"): failures.append("assignment_group")
    if set(current.get("submission_types") or [])!=MAJOR_SUBMISSION_TYPES: failures.append("submission_types")
    if RUBRIC_NOTE_MARKER not in (current.get("description") or ""): failures.append("rubric_marker")
    if failures: raise RuntimeError(f"Mapped Major normalization failed: {failures}")
    return current
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
    if uploaded.get("locked") is not True: await api(c,"PUT",f"/files/{uploaded['id']}",data={"locked":"true"})
    current=await api(c,"GET",f"/files/{uploaded['id']}")
    if current.get("locked") is not True: raise RuntimeError(f"Canvas file did not remain locked: {path.name}")
    return current
async def lock_folder_files(c,folder,required_names=()):
    current=await api(c,"GET",f"/folders/{folder['id']}")
    if current.get("locked") is not True: current=await api(c,"PUT",f"/folders/{folder['id']}",data={"locked":"true"})
    files=await paged(c,f"/folders/{folder['id']}/files")
    for file in files:
        if file.get("locked") is not True: await api(c,"PUT",f"/files/{file['id']}",data={"locked":"true"})
    current=await api(c,"GET",f"/folders/{folder['id']}"); verified=await paged(c,f"/folders/{folder['id']}/files")
    names={file.get("display_name") or file.get("filename") for file in verified}; missing=set(required_names)-names
    unlocked=[file.get("id") for file in verified if file.get("locked") is not True]
    if current.get("locked") is not True or missing or unlocked: raise RuntimeError(f"2SW Wk2 folder invariant failed for {folder['id']}: missing={sorted(missing)} unlocked={unlocked}")
    return current,verified
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
async def upsert_discussion(c,found):
    message='<p><strong>Use the fictional Clinton Lake evidence only.</strong></p><ol><li>Name the file you think carries the strongest evidence.</li><li>Explain what it directly shows.</li><li>Name one limitation or missing fact.</li></ol><p>Then reply to one classmate with a different file that complicates, qualifies, or challenges the conclusion. A private written response to the same prompts is an equal route.</p>'
    data={"title":DISCUSSION_TITLE,"message":message,"discussion_type":"threaded","published":"false","require_initial_post":"true"}
    if found: discussion=await api(c,"PUT",f"/courses/{COURSE_ID}/discussion_topics/{found['id']}",data=data)
    else: discussion=await api(c,"POST",f"/courses/{COURSE_ID}/discussion_topics",data=data)
    current=await api(c,"GET",f"/courses/{COURSE_ID}/discussion_topics/{discussion['id']}")
    if current.get("published") is not False or current.get("assignment_id") or current.get("discussion_type")!="threaded" or current.get("require_initial_post") is not True:
        raise RuntimeError(f"Practice discussion invariant failed after update: {current}")
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
        elif kind in {"Discussion","Assignment"}: data["module_item[content_id]"]=key
        created=await api(c,"POST",f"/courses/{COURSE_ID}/modules/{module_id}/items",data=data); keep.append(created["id"])
    for item in items:
        if item["id"] not in keep: await api(c,"DELETE",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}")
    for position,(item_id,(kind,key,title)) in enumerate(zip(keep,expected),start=1):
        await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item_id}",data={"module_item[position]":position,"module_item[title]":title,"module_item[published]":"false"})
    final=sorted(await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"),key=lambda entry:entry.get("position") or 0)
    if len(final)!=17: raise RuntimeError(f"Expected literal 17-item 2SW Wk2 module; found {len(final)}")
    for position,(item,(kind,key,title)) in enumerate(zip(final,expected),start=1):
        if item.get("position")!=position or item.get("title")!=title or item.get("published") is not False or not item_matches(item,kind,key,title):
            raise RuntimeError(f"2SW Wk2 item mismatch at position {position}: {item}")
    return final
def flow(color,title,text): return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'
def evidence_images(uploads):
    evidence={
        1:("file-1-upright.png","Lake Water Report: severe low oxygen, high nitrates, detected chemical contaminants, murky water, chemical odor, and ecological warnings."),
        2:("file-2-upright.png","Landfill Inspection Note: a routine inspection reports normal operations, while relying partly on a major check from three months earlier."),
        3:("file-3-upright.png","Weather Report: 12.5 inches of rain, severe flooding, backed-up sewers, and failed street drainage."),
        4:("file-4-upright.png","City Statement: officials report routine monitoring and containment testing with no evidence of leakage, but provide no raw test results or independent verification."),
        5:("slide-6.png","Citizen Environmental Note: unusual storm-drain substances and chemical odors were observed; illegal household-chemical dumping is identified as a possibility."),
        6:("file-6-upright.png","Wildlife Report: a rapid fish-population crash and signs of chemical exposure in aquatic species."),
    }
    cards=[]
    for number,(filename,description) in evidence.items():
        file_id=uploads[filename]["id"]
        cards.append(
            f'<details style="border:1px solid #cfc5dd;border-radius:8px;padding:12px 16px;margin:12px 0">'
            f'<summary style="font-weight:700;color:#5a2d91;cursor:pointer">File {number}</summary>'
            f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{description}" style="display:block;width:100%;max-width:680px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'
            f'<p style="margin:8px 0"><strong>Source summary:</strong> {description}</p>'
            f'<p style="margin:8px 0"><a href="/courses/{COURSE_ID}/files/{file_id}/preview" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">Open File {number} full size</a>.</p>'
            '</details>'
        )
    return "".join(cards)

async def main():
    preflight()
    token=sys.stdin.readline().strip()
    if not token: raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"},timeout=120) as c:
        existing_module,mapped_major,major_group,existing_discussion=await canvas_preflight(c)
        mapped_major=await normalize_major_assignment(c,mapped_major,major_group)
        module=await ensure_module(c,existing_module); module_id=module["id"]; discussion=await upsert_discussion(c,existing_discussion)
        support_folder="course files/CCR Materials/2SW/Wk2"; support_folder_record=await ensure_folder(c,support_folder); files={k:await upload(c,ROOT/"docs/resources/worksheets"/v,support_folder) for k,v in SUPPORT_NAMES.items()}
        support_folder_record,support_folder_files=await lock_folder_files(c,support_folder_record,SUPPORT_NAMES.values())
        uploads={}; folders={}
        for day in range(1,6):
            fp=f"course files/CCR Materials/2SW/Wk2/Day {day} Visuals"; folders[day]=await ensure_folder(c,fp); uploads[day]={}
            visual_paths=VISUAL_PATHS[day]
            for path in visual_paths: uploads[day][path.name]=await upload(c,path,fp)
            await lock_folder_files(c,folders[day],[path.name for path in visual_paths])
        student_values={
          1:{"OPENER_IMAGE_ID":uploads[1]["law-cluster-opener.jpg"]["id"],"PROGRAM_IMAGE_ID":uploads[1]["irving-first-responder-programs.png"]["id"],"ROUTE_FILE_ID":files["ROUTE"]["id"]},
          2:{"TRACKER_FILE_ID":files["TRACKER"]["id"],"EVIDENCE_IMAGES":evidence_images(uploads[2]),"DISCUSSION_URL":f"/courses/{COURSE_ID}/discussion_topics/{discussion['id']}"},
          3:{"SIM_FILE_ID":files["SIM"]["id"],"INTRO_IMAGE_ID":uploads[3]["injured-trail-intro.png"]["id"],"SUPPLY_IMAGE_ID":uploads[3]["slide-2.png"]["id"],"EXAMPLE_IMAGE_ID":uploads[3]["slide-3.png"]["id"]},
          4:{"PCR_FILE_ID":files["PCR"]["id"],"RUBRIC_FILE_ID":files["RUBRIC"]["id"],"REPORT_IMAGE_ID":uploads[4]["injured-trail-report.png"]["id"],"COMPLICATION_IMAGE_ID":uploads[4]["injured-trail-complications.png"]["id"]},
          5:{"REFLECTION_FILE_ID":files["REFLECTION"]["id"],"APP_IMAGE_ID":uploads[5]["law-public-safety-app.png"]["id"]}}
        titles={1:"STUDENT: 2SW Wk2 Day 1 - First Responder Routes",2:"STUDENT: 2SW Wk2 Day 2 - Clinton Lake Evidence",3:"STUDENT: 2SW Wk2 Day 3 - Trail Response Simulation",4:"STUDENT: 2SW Wk2 Day 4 - Patient Report and Safety Plan",5:"STUDENT: 2SW Wk2 Day 5 - Career and Integrity Reflection"}
        td={
          1:{"TITLE":"Compare First Responder Routes","SUBTITLE":"50 minutes · TEKS d(1)(B), d(1)(C), d(2)(A)","ALERT":"<strong>Do not mix salary types or promise credential transfer.</strong> The guide uses May 2024 U.S. medians. Military experience may build related skills and credentials, but students must verify the exact civilian agency, academy, license, or certification requirement.","PREP":f'<ul><li>Open the reused FYF p. 39 cluster overview and FYF p. 56 district-program page embedded in the Student Guide. FYF p. 57 is not needed for today\'s evidence, and the optional p. 58 app route belongs to Day 5.</li><li>Print/post all four pages of the <a href="/courses/{COURSE_ID}/files/{files["ROUTE"]["id"]}/preview">route guide</a>.</li><li>Preflight Xello/H&amp;L only if offering them as optional extensions.</li></ul>',"EVIDENCE":"<p>Collect three career comparisons, the civilian/military route analysis, two district connections, and the cluster description. Platform access and career enthusiasm are not graded.</p>","FLOW":flow("#5a2d91","911 system warm-up · 5 minutes","Sort workers into call-taking, response, care, investigation, and documentation.")+flow("#4a9d2f","Read salary labels · 8 minutes","Circle year, underline geography, box median.")+flow("#1f617a","Compare three careers · 17 minutes","One task, preparation step, and careful pay interpretation per career.")+flow("#e3ad19","Compare routes and connect to Singley · 15 minutes","One route-system similarity, difference, and transfer question; then Law Enforcement and Emergency Medical - EMT connections.")+flow("#1f617a","Rank and describe the cluster · 5 minutes","Defend a preparation ranking and name one responsibility shared by two careers."),"MONITOR":"<p>Accept varied career routes that preserve the source's locality or agency caveat. Reject fixed promises. Current BLS medians: patrol officer $76,290; detective $93,580; firefighter $59,530; EMT $41,340; telecommunicator $50,730. For military/civilian comparison, require verification of the receiving civilian requirement rather than assuming transfer.</p>","SUPPORT":"<p>Pre-teach route, academy, license, certification, median, locality, and transfer. Let students complete two careers before adding the third. Use the complete-thought route-system frame from the student guide.</p>","FALLBACK":"<p>The four-page route guide is the complete no-login route. Optional Xello/H&amp;L research can be omitted.</p>"},
          2:{"TITLE":"Clinton Lake - Weigh the Evidence","SUBTITLE":"50 minutes · TEKS d(4)(F)","ALERT":"<strong>Do not force a culprit.</strong> The packet strongly shows harm but does not directly prove a containment failure. Score source evaluation and uncertainty.","PREP":f'<ul><li>Open all six licensed images in the student guide.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["TRACKER"]["id"]}/preview">evidence tracker</a>.</li><li>Choose whether to use the optional unpublished counterevidence discussion or private written route.</li></ul>',"EVIDENCE":"<p>Six tracker rows and a conclusion using three files plus one gap. The optional Discussion is ungraded practice.</p>","FLOW":flow("#5a2d91","Evidence-question warm-up · 5 minutes","Sort questions into harm, timing, source, and missing test.")+flow("#4a9d2f","Four-question routine · 7 minutes","Show, producer, limit, strength.")+flow("#1f617a","Six-file review · 23 minutes","Pause after Files 2 and 4 for source limits.")+flow("#e3ad19","Careful conclusion · 10 minutes","Use three files and preserve uncertainty.")+flow("#1f617a","Integrity close · 5 minutes","Report inconvenient evidence rather than hiding it."),"MONITOR":"<p>Files 1 and 6 strongly establish harm. File 3 shows the storm; File 5 raises outside dumping. File 2 is limited because it is a routine inspection and partly relies on an older major check. File 4 is the City's own summary: it reports monitoring and testing with no leakage evidence, but supplies no raw results or independent verification. No file directly proves landfill leakage.</p>","SUPPORT":"<p>Read each file aloud or use its visible source summary. Students may highlight before paraphrasing. Provide the complete sentence frames “File ___ directly shows ___” and “It cannot prove ___ because ___.” A private written conclusion is equal to posting.</p>","FALLBACK":"<p>All six files, source summaries, and full-size links are embedded. An absent student completes the same tracker. Skip the Discussion if public posting is inappropriate.</p>"},
          3:{"TITLE":"Injured on the Trail - Controlled Simulation","SUBTITLE":"50 minutes · TEKS d(1)(C)","ALERT":"<strong>Career role-play only.</strong> Never practice on an injury or force movement. Offer model/mannequin, consenting uninjured partner, and observer/documenter routes before grouping.","PREP":f'<ul><li>Open FYF pp. 52-53 and both deck visuals.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["SIM"]["id"]}/preview">simulation record</a>.</li><li>Prepare paper models or mannequins alongside optional supplies.</li></ul>',"EVIDENCE":"<p>Research and two-round observation record. Non-contact participation earns identical credit; physical technique is not certified or graded.</p>","FLOW":flow("#5a2d91","Remote-response warm-up · 5 minutes","Name distance, terrain, weather, time, and communication constraints.")+flow("#4a9d2f","Career research · 12 minutes","SAR/WFR responsibility, limit, and documentation reason.")+flow("#1f617a","Materials and boundaries · 10 minutes","Permission, narration, loose placement, comfort check, stop.")+flow("#e3ad19","Two short rounds · 18 minutes","Observe, explain, and improve; switch only when appropriate.")+flow("#1f617a","Safety close · 5 minutes","Tingling means stop, remove/loosen, check, and notify."),"MONITOR":"<p>Look for permission, no force, loose placement, comfort checks, and response to feedback. Stop immediately for pain, tingling, numbness, color change, distress, or a request to stop.</p>","SUPPORT":"<p>Read the boundary aloud. Students may narrate, point, sketch, or document instead of handling materials. Use the Canvas images as labeled visual cards.</p>","FALLBACK":"<p>No supplies: use paper models. Absence: complete the record from the embedded visuals. Real injuries go to the nurse/911 process.</p>"},
          4:{"TITLE":"Patient Report and Safety Plan","SUBTITLE":"50 minutes · TEKS d(1)(C), d(4)(F)","ALERT":"<strong>Fictional documentation only.</strong> Do not collect real names or medical information. Students record observations, not diagnoses.","PREP":f'<ul><li>Open FYF pp. 53-54.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["PCR"]["id"]}/preview">report and plan</a> plus the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">16-point rubric</a>.</li><li>Post the three safety-first complication reminders.</li></ul>',"EVIDENCE":"<p>One individual 16-point durable evidence set: five-part report, specific EMT or Search and Rescue documentation connection, and complication plan. Speaking and physical technique are not graded.</p>","FLOW":flow("#5a2d91","Missing-handoff warm-up · 5 minutes","Sort facts into scene, observations, actions, reasoning, handoff.")+flow("#4a9d2f","Write the report and career connection · 20 minutes","Use fictional facts, avoid diagnoses, and name the documentation responsibility represented.")+flow("#1f617a","Plan for one complication · 15 minutes","First action, communication, reassessment trigger, alternative.")+flow("#e3ad19","Rubric review and revision · 7 minutes","Revise one sentence for safety or accuracy.")+flow("#1f617a","Trade-off close · 3 minutes","Do not enter fast water; communicate and reroute."),"MONITOR":"<p>Thunder: seek a substantial building or hard-topped vehicle. Fast/unknown water: do not enter. Anxiety: communicate calmly and honestly. Full reports separate observation from inference, name the documentation or handoff responsibility, and provide an organized handoff.</p>","SUPPORT":"<p>Use “I observed…,” “Our team represented…,” and “We would stop and reassess if…”. Speech-to-text or teacher scribing may be used when documented.</p>","FALLBACK":"<p>No simulation is required. An absent student uses the fictional images and completes the same report independently.</p>"},
          5:{"TITLE":"Career and Integrity Reflection","SUBTITLE":"50 minutes · TEKS d(1)(C), d(2)(A), d(4)(F)","ALERT":"<strong>Core evidence first.</strong> H&amp;L, Xello, and Roadtrip Nation are optional this week; there is no required Grade 8 Xello completion task here.","PREP":f'<ul><li>Return the route guide, evidence tracker, and report.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["REFLECTION"]["id"]}/preview">individual reflection</a>.</li><li>Open optional platforms only after the core work is ready.</li></ul>',"EVIDENCE":"<p>Collect one five-part individual reflection. Day 4 remains the week's 16-point durable evidence set; do not add a second major for platform clicks.</p>","FLOW":flow("#5a2d91","Private interest check · 5 minutes","Interested, unsure, or not interested—with one reason.")+flow("#4a9d2f","Correct route evidence · 12 minutes","Remove starting/local overclaims.")+flow("#1f617a","Integrity synthesis · 10 minutes","Who relies on accurate evidence and handoff facts?")+flow("#e3ad19","Individual reflection · 18 minutes","Route fact, work fact, integrity moment, next step.")+flow("#1f617a","Concept-map close · 5 minutes","Information, worker, dependent person, consequence."),"MONITOR":"<p>Detectives typically begin as police officers; do not require a fixed 3-5 year ladder. Accept informed “not interested.” Strong integrity answers name the information, who relies on it, and a plausible consequence.</p>","SUPPORT":"<p>Pre-teach route, responsibility, observation, handoff, integrity, and reassess. Oral rehearsal is allowed; each student submits individual evidence.</p>","FALLBACK":"<p>The Canvas/paper reflection is the normal route. Optional platforms and video can be omitted with no loss of target.</p>"}}
        contracts={
          1:{"TOPIC":"First Responder Routes","OBJECTIVE":"Students will describe the Law, Public Safety, Corrections and Security cluster; compare civilian and military law-enforcement route systems; and identify first-responder careers and preparation requirements.","TEKS":"d(1)(B), d(1)(C), d(2)(A)","DOL":"Three career comparisons, a civilian/military route analysis, two district connections, and a cluster description.","STUDENT_OBJECTIVE":"I can compare first-responder careers and explain how civilian and military route systems differ.","STUDENT_DOL":"I will compare three careers, analyze both route systems, connect two district pathways, and describe the cluster."},
          2:{"TOPIC":"Evidence Integrity","OBJECTIVE":"Students will demonstrate integrity by separating observations from claims, evaluating source limits, and reporting a conclusion that includes inconvenient evidence and uncertainty.","TEKS":"d(4)(F)","DOL":"Clinton Lake Evidence Tracker with six source evaluations and a conclusion using three files plus one uncertainty.","STUDENT_OBJECTIVE":"I can report what the evidence supports without hiding a file or pretending uncertainty is proof.","STUDENT_DOL":"I will complete all six evidence rows and write a conclusion that uses three files and names one uncertainty."},
          3:{"TOPIC":"Response Communication","OBJECTIVE":"Students will identify Search and Rescue and Wilderness First Responder responsibilities and demonstrate safe communication, consent, observation, and documentation in a controlled career simulation.","TEKS":"d(1)(C)","DOL":"Injured on the Trail Simulation Record with career research, two observation rounds, and one documented improvement.","STUDENT_OBJECTIVE":"I can explain response-career responsibilities and practice safe communication and documentation in a simulation.","STUDENT_DOL":"I will finish the career research, both observation rounds, and one safety or communication improvement."},
          4:{"TOPIC":"Professional Documentation","OBJECTIVE":"Students will identify EMT and Search and Rescue documentation responsibilities, write an accurate fictional Patient Care Report, and choose a safety-first response to one wilderness complication.","TEKS":"d(1)(C), d(4)(F)","DOL":"Fictional Patient Care Report and Safety Plan with one specific career-role connection.","STUDENT_OBJECTIVE":"I can document a fictional response accurately and make a safety-first handoff decision.","STUDENT_DOL":"I will complete the report, career-role connection, complication plan, and one evidence-based revision."},
          5:{"TOPIC":"Career Integrity","OBJECTIVE":"Students will compare first-responder preparation, identify one career opportunity, and explain how accurate reporting and integrity protect people who rely on professional information.","TEKS":"d(1)(C), d(2)(A), d(4)(F)","DOL":"Completed First Responder Route Guide and five-part Career and Integrity Reflection using specific week evidence.","STUDENT_OBJECTIVE":"I can use route, work, and integrity evidence to make an informed first-responder career decision.","STUDENT_DOL":"I will finish the route guide and a five-part reflection with one realistic next step."}}
        pages={}
        for day in range(1,6):
            st=titles[day]; student=await upsert_page(c,st,render(f"2sw-wk2-day{day}-student.html",{"COURSE_ID":COURSE_ID,**contracts[day],**student_values[day]}),slugify(st))
            tt=f"TEACHER: 2SW Wk2 Day {day} Facilitator Guide"; teacher=await upsert_page(c,tt,render("2sw-wk2-teacher.html",{"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student["url"],**contracts[day],**td[day]}),slugify(tt))
            pages[day]={"teacher":teacher,"student":student}
        expected=[]
        for day in range(1,6):
            expected.append(("SubHeader",None,f"Day {day}"))
            for page_kind in ("teacher","student"):
                page=pages[day][page_kind]
                expected.append(("Page",page["url"],page["title"]))
            if day==2: expected.append(("Discussion",discussion["id"],DISCUSSION_TITLE))
            if day==4: expected.append(("Assignment",mapped_major["id"],MAPPED_MAJOR_TITLE))
        final=await reconcile_module_items(c,module_id,expected)
        module=await api(c,"GET",f"/courses/{COURSE_ID}/modules/{module_id}")
        final_major=await api(c,"GET",f"/courses/{COURSE_ID}/assignments/{mapped_major['id']}")
        final_discussion=await api(c,"GET",f"/courses/{COURSE_ID}/discussion_topics/{discussion['id']}")
        final_pages=[await api(c,"GET",f"/courses/{COURSE_ID}/pages/{page['url']}") for day in range(1,6) for page in pages[day].values()]
        final_failures=[]
        if module.get("published") is not False: final_failures.append("module_published")
        if any(page.get("published") is not False for page in final_pages): final_failures.append("page_published")
        if final_discussion.get("published") is not False or final_discussion.get("assignment_id") or final_discussion.get("discussion_type")!="threaded" or final_discussion.get("require_initial_post") is not True: final_failures.append("discussion_state")
        if final_major.get("published") is not False or float(final_major.get("points_possible") or 0)!=100 or final_major.get("grading_type")!="points" or final_major.get("omit_from_final_grade") is not False: final_failures.append("major_grading")
        if final_major.get("assignment_group_id")!=major_group.get("id") or set(final_major.get("submission_types") or [])!=MAJOR_SUBMISSION_TYPES or RUBRIC_NOTE_MARKER not in (final_major.get("description") or ""): final_failures.append("major_identity")
        support_folder_record,support_folder_files=await lock_folder_files(c,support_folder_record,SUPPORT_NAMES.values())
        folder_files={}
        for day,folder in folders.items(): folders[day],folder_files[day]=await lock_folder_files(c,folder,(path.name for path in VISUAL_PATHS[day]))
        if final_failures: raise RuntimeError(f"2SW Wk2 final invariant failed: {final_failures}")
        print(json.dumps({"module":{"id":module_id,"published":module["published"]},"major":{"id":final_major["id"],"published":final_major.get("published"),"points":final_major.get("points_possible"),"group":final_major.get("assignment_group_id"),"grading_type":final_major.get("grading_type"),"omit_from_final_grade":final_major.get("omit_from_final_grade")},"discussion":{"id":final_discussion["id"],"published":final_discussion.get("published"),"assignment_id":final_discussion.get("assignment_id")},"support_folder":{"id":support_folder_record["id"],"locked":support_folder_record["locked"],"file_count":len(support_folder_files)},"folders":{str(d):{"id":f["id"],"locked":f["locked"],"file_count":len(folder_files[d])} for d,f in folders.items()},"files":{k:v["id"] for k,v in files.items()},"pages":{str(d):{k:{"url":v["url"],"published":v["published"]} for k,v in p.items()} for d,p in pages.items()},"items":[{"id":i["id"],"position":i["position"],"title":i["title"],"type":i["type"],"page_url":i.get("page_url"),"content_id":i.get("content_id"),"published":i.get("published")} for i in final]},indent=2))

if __name__=="__main__": asyncio.run(main())
