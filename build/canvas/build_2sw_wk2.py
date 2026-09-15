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
    unlocked=[]
    for file in verified:
        if file.get("locked") is not True:
            refreshed=await api(c,"GET",f"/files/{file['id']}")
            if refreshed.get("locked") is not True:
                unlocked.append(file.get("id"))
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
def flow(color,title,text): return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0 0 6px;color:{color}">{title}</h4>{text}</div>'
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
          1:{
            "TITLE":"Compare First Responder Routes","SUBTITLE":"50 minutes · TEKS d(1)(B), d(1)(C), d(2)(A)",
            "ALERT":"<strong>Do not mix salary types or promise credential transfer.</strong> The guide uses May 2024 U.S. medians. Military experience may build related skills and credentials, but students must verify the exact civilian agency, academy, license, or certification requirement.",
            "PREP":f'<ul><li>Open the reused FYF p. 39 cluster overview and FYF p. 56 district-program page embedded in the Student Guide. FYF p. 57 is not needed for today\'s evidence, and the optional p. 58 app route belongs to Day 5.</li><li>Print/post all four pages of the <a href="/courses/{COURSE_ID}/files/{files["ROUTE"]["id"]}/preview">route guide</a>.</li><li>Preflight Xello/H&amp;L only if offering them as optional extensions.</li></ul>',
            "EVIDENCE":"<p>Collect three career comparisons, the civilian/military route analysis, two district connections, and the cluster description. Platform access and career enthusiasm are not graded.</p>",
            "FLOW":(
              flow("#5a2d91","Minutes 0-5 - Welcome and 911 responder sequence warm-up",'''<p>Welcome students to Week 2 of Law and Public Safety and project the 911 launch prompt.</p><ul><li>Ask, <em>“When someone dials 911 in an emergency, which professionals are involved before, during, and after responders reach the scene?”</em></li><li>Collect student responses. Guide students to sort the roles into a chronological response chain: call-taking (telecommunicator), dispatch/response (patrol officer, firefighter), care (paramedic/EMT), investigation (detective), and documentation/legal follow-up.</li><li>Bridge with, <em>“Every link in that chain requires specialized training and credentials. Today we compare first-responder career routes and preparation requirements.”</em></li></ul>''')+
              flow("#4a9d2f","Minutes 5-13 - Interpreting labor data and critical source labels",'''<p>Open the First Responder Route Guide and project the labor market summary.</p><ul><li>Model how to annotate labor statistics with precision: (1) circle the data year (May 2024), (2) underline the geography (national U.S.), (3) box the metric type (median), and (4) write <em>“not a starting salary guarantee”</em> beside the wage table.</li><li>Compare medians across roles: Patrol Officer ($76,290), Detective ($93,580), Firefighter ($59,530), EMT ($41,340), and Telecommunicator ($50,730). Emphasize: national median reflects experienced workers across all 50 states, not entry-level DFW pay.</li></ul>''')+
              flow("#1f617a","Minutes 13-30 - Comparative analysis of three first responder careers",'''<p>Students select THREE distinct first responder careers on their Route Guide.</p><ul><li>Students document: (1) one essential daily task, (2) typical entry preparation (e.g. state-licensed police academy, EMT basic certification, fire academy), and (3) an accurate interpretation of median earnings with source caveats.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 18): Verify students record daily duties specific to the selected role.<br>• Lap 2 (Minute 25): Stop students writing absolute claims like 'all academies take 6 months'—guide them to record that requirements vary by agency, municipality, and state.</li></ul>''')+
              flow("#e3ad19","Minutes 30-45 - Civilian vs. military routes and Irving ISD connections",'''<p>Students analyze the two major training pipelines on page 3 of the guide.</p><ul><li>Compare civilian academies with military law enforcement routes (Military Police / Security Forces). Require students to document: one key similarity (rigorous tactical and legal training), one difference (jurisdiction and military command structure), and one civilian credential that must be verified before assuming military training automatically transfers.</li><li>Connect to Irving ISD CTE programs at Singley Academy: <strong>Law Enforcement</strong> and <strong>Emergency Medical Technician (EMT)</strong>.</li></ul>''')+
              flow("#24323d","Minutes 45-50 - Ranked preparation DOL and close",'''<p>Direct students to the Day 1 Exit Ticket.</p><ul><li>Students rank their three investigated careers from most to least postsecondary training required and defend the top rank with specific evidence from the Route Guide.</li><li>Students state one shared ethical responsibility common across all first-responder careers.</li><li><strong>Safe Trim:</strong> At minute 40, stop optional web exploration; protect the 3-career comparison table and ranked justification exit ticket.</li></ul>''')
            ),
            "MONITOR":"<p>Accept varied career routes that preserve the source's locality or agency caveat. Reject fixed promises. Current BLS medians: patrol officer $76,290; detective $93,580; firefighter $59,530; EMT $41,340; telecommunicator $50,730. For military/civilian comparison, require verification of the receiving civilian requirement rather than assuming transfer.</p>",
            "SUPPORT":"<p>Pre-teach route, academy, license, certification, median, locality, and transfer. Let students complete two careers before adding the third. Use the complete-thought route-system frame from the student guide.</p>",
            "FALLBACK":"<p>The four-page route guide is the complete no-login route. Optional Xello/H&amp;L research can be omitted.</p>"},
          2:{
            "TITLE":"Clinton Lake - Weigh the Evidence","SUBTITLE":"50 minutes · TEKS d(4)(F)",
            "ALERT":"<strong>Do not force a culprit.</strong> The packet strongly shows harm but does not directly prove a containment failure. Score source evaluation and uncertainty.",
            "PREP":f'<ul><li>Open all six licensed images in the student guide.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["TRACKER"]["id"]}/preview">evidence tracker</a>.</li><li>Choose whether to use the optional unpublished counterevidence discussion or private written route.</li></ul>',
            "EVIDENCE":"<p>Six tracker rows and a conclusion using three files plus one gap. The optional Discussion is ungraded practice.</p>",
            "FLOW":(
              flow("#5a2d91","Minutes 0-5 - Welcome and lake contamination dilemma warm-up",'''<p>Welcome students and project the environmental crime launch prompt.</p><ul><li>Ask, <em>“Clinton Lake has experienced a sudden environmental disaster: low oxygen, dead fish, and chemical odors. What is the single most important question investigators must answer before publicly naming a culprit?”</em></li><li>Collect 2-3 responses. Group student questions into four categories: Harm (what happened?), Timing (when did it begin?), Source (who uses those chemicals?), and Missing Tests (what haven't we tested yet?).</li><li>Bridge with, <em>“In law enforcement and environmental investigation, jumping to conclusions ruins cases. Today we evaluate six pieces of evidence with strict objectivity.”</em></li></ul>''')+
              flow("#4a9d2f","Minutes 5-12 - Four-question evidence evaluation protocol",'''<p>Teach the 4-Question Forensic Audit Routine before revealing files:</p><ul><li>1. <strong>Direct Observation:</strong> What does the file directly and factually show?</li><li>2. <strong>Producer / Origin:</strong> Who created this document, and what is their interest or perspective?</li><li>3. <strong>Source Limitations:</strong> What can this document NOT prove by itself?</li><li>4. <strong>Evidentiary Weight:</strong> How strongly does this document link a specific suspect to the harm?</li><li>Project File 1 (Water Test Report) and model how to log facts versus assumptions.</li></ul>''')+
              flow("#1f617a","Minutes 12-35 - Six-file forensic evidence review",'''<p>Students inspect the six authentic Canvas evidence files and complete their Evidence Tracker.</p><ul><li>File 1: Lake Water Report (proves severe low oxygen and chemical contamination).</li><li>File 2: Landfill Inspection Note (routine check, but relies on an inspection from 3 months prior).</li><li>File 3: Weather Report (12.5 inches of rain, massive flooding, overwhelmed storm drains).</li><li>File 4: City Official Statement (claims containment is intact, but provides zero raw data or independent lab verification).</li><li>File 5: Citizen Environmental Tip (reports illegal chemical dumping into storm drains).</li><li>File 6: Wildlife Crash Report (documents rapid fish kill and chemical exposure).</li><li>Pause after File 4: Ask, <em>“Does the City Statement prove the landfill is innocent, or does it merely show that the City has not verified leakage?”</em></li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 18): Ensure students separate raw test data from theoretical claims.<br>• Lap 2 (Minute 27): Verify students note the limitation of File 2 (outdated inspection) and File 4 (unverified city claim).</li></ul>''')+
              flow("#e3ad19","Minutes 35-45 - Synthesizing a defensible conclusion",'''<p>Students draft a forensic conclusion using evidence from at least three files.</p><ul><li>Students formulate an evidence-based stance: Landfill failure, severe storm runoff/illegal dumping, mixed causes, or insufficient evidence to indict.</li><li>Enforce the standard: A defensible conclusion must name at least ONE major evidence gap that requires independent chemical testing before filing charges.</li></ul>''')+
              flow("#24323d","Minutes 45-50 - Integrity in reporting DOL and close",'''<p>Direct students to the Day 2 Exit Ticket.</p><ul><li>Scenario: <em>“An investigator intentionally leaves File 5 out of the case file because it complicates the department's theory against the landfill. What is the ethical violation, and what must happen next?”</em></li><li>Collect trackers and exit tickets.</li><li><strong>Safe Trim:</strong> Analyze four files instead of six (Files 1, 2, 3, and 4) if reading takes longer, while fiercely protecting the evidence tracker and ethical integrity exit response.</li></ul>''')
            ),
            "MONITOR":"<p>Files 1 and 6 strongly establish harm. File 3 shows the storm; File 5 raises outside dumping. File 2 is limited because it is a routine inspection and partly relies on an older major check. File 4 is the City's own summary: it reports monitoring and testing with no leakage evidence, but supplies no raw results or independent verification. No file directly proves landfill leakage.</p>",
            "SUPPORT":"<p>Read each file aloud or use its visible source summary. Students may highlight before paraphrasing. Provide the complete sentence frames “File ___ directly shows ___” and “It cannot prove ___ because ___.” A private written conclusion is equal to posting.</p>",
            "FALLBACK":"<p>All six files, source summaries, and full-size links are embedded. An absent student completes the same tracker. Skip the Discussion if public posting is inappropriate.</p>"},
          3:{
            "TITLE":"Injured on the Trail - Controlled Simulation","SUBTITLE":"50 minutes · TEKS d(1)(C)",
            "ALERT":"<strong>Career role-play only.</strong> Never practice on an injury or force movement. Offer model/mannequin, consenting uninjured partner, and observer/documenter routes before grouping.",
            "PREP":f'<ul><li>Open FYF pp. 52-53 and both deck visuals.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["SIM"]["id"]}/preview">simulation record</a>.</li><li>Prepare paper models or mannequins alongside optional supplies.</li></ul>',
            "EVIDENCE":"<p>Research and two-round observation record. Non-contact participation earns identical credit; physical technique is not certified or graded.</p>",
            "FLOW":(
              flow("#5a2d91","Minutes 0-5 - Welcome and remote wilderness emergency warm-up",'''<p>Welcome students and project the remote search-and-rescue dilemma.</p><ul><li>Ask, <em>“Imagine an injury occurs on a rocky mountain trail 5 miles from the nearest road with zero cell service. What factors make this radically different from an injury that happens inside a school gym?”</em></li><li>Collect student insights: evacuation time, environmental exposure, limited gear, communication delay, and reliance on partner assessment.</li><li>Bridge with, <em>“Search and Rescue (SAR) and Wilderness First Responders (WFR) must prioritize patient communication, consent, and careful observation. Today we conduct a controlled simulation.”</em></li></ul>''')+
              flow("#4a9d2f","Minutes 5-15 - SAR/WFR career scope and non-negotiable safety rules",'''<p>Establish the professional role-play boundaries before any materials are touched.</p><ul><li>Clarify scope: This is career communication practice, NOT medical certification or actual first-aid treatment. Never apply force to any limb; never manipulate an injured area.</li><li>Three equal participation pathways: (A) Model/mannequin/dowel route, (B) Consenting uninjured partner, or (C) Observer/Documenter.</li><li>Teach the 5-Step Protocol: (1) Verbal Consent &rarr; (2) Narration (explain every movement before doing it) &rarr; (3) Loose Placement &rarr; (4) Comfort Check &rarr; (5) Immediate Stop if any discomfort or request occurs.</li><li>Explain standard gear: Triangular bandage (sling/swathe simulation) and finger splint model.</li></ul>''')+
              flow("#1f617a","Minutes 15-35 - Two-round communication and documentation simulation",'''<p>Students conduct two structured 10-minute simulation rounds.</p><ul><li><strong>Round 1 (10 min):</strong> Partner A acts as First Responder (narrates actions, asks for consent, positions wrap loosely); Partner B acts as Patient (or holds model); Partner C/Observer logs communication clarity on the Simulation Record.</li><li>Pause for feedback: Observer names one communication strength and one specific safety improvement.</li><li><strong>Round 2 (10 min):</strong> Rotate roles or repeat with the documented communication adjustment.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 20): Confirm responders ask for explicit verbal consent before beginning.<br>• Lap 2 (Minute 28): Verify that all wraps and splints are placed loosely with continuous comfort checks. Intervene immediately if any student applies pressure.</li></ul>''')+
              flow("#e3ad19","Minutes 35-45 - Complete trail simulation record",'''<p>Students complete the three analysis fields on their Simulation Record.</p><ul><li>Document: (1) Primary responsibilities of a Wilderness First Responder, (2) Key limitations of wilderness response gear, and (3) Why accurate documentation is vital before handoff to medical transport.</li></ul>''')+
              flow("#24323d","Minutes 45-50 - Emergency branching decision DOL and close",'''<p>Direct students to the Day 3 Exit Ticket.</p><ul><li>Branching prompt: <em>“During a practice splint placement, a patient reports a tingling sensation or numbness. What is the mandatory immediate sequence of actions?”</em> (Correct: Stop immediately, loosen/remove material, assess sensation, report to instructor/medical lead).</li><li>Collect simulation records and secure all materials.</li><li><strong>Safe Trim:</strong> Run a single structured simulation round with a 5-minute debrief if transitions take longer, preserving individual simulation records and the safety exit ticket.</li></ul>''')
            ),
            "MONITOR":"<p>Look for permission, no force, loose placement, comfort checks, and response to feedback. Stop immediately for pain, tingling, numbness, color change, distress, or a request to stop.</p>",
            "SUPPORT":"<p>Read the boundary aloud. Students may narrate, point, sketch, or document instead of handling materials. Use the Canvas images as labeled visual cards.</p>",
            "FALLBACK":"<p>No supplies: use paper models. Absence: complete the record from the embedded visuals. Real injuries go to the nurse/911 process.</p>"},
          4:{
            "TITLE":"Patient Report and Safety Plan","SUBTITLE":"50 minutes · TEKS d(1)(C), d(4)(F)",
            "ALERT":"<strong>Fictional documentation only.</strong> Do not collect real names or medical information. Students record observations, not diagnoses.",
            "PREP":f'<ul><li>Open FYF pp. 53-54.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["PCR"]["id"]}/preview">report and plan</a> plus the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">16-point rubric</a>.</li><li>Post the three safety-first complication reminders.</li></ul>',
            "EVIDENCE":"<p>One individual 16-point durable evidence set: five-part report, specific EMT or Search and Rescue documentation connection, and complication plan. Speaking and physical technique are not graded.</p>",
            "FLOW":(
              flow("#5a2d91","Minutes 0-5 - Welcome and missing medical handoff warm-up",'''<p>Welcome students and project the emergency handoff launch prompt.</p><ul><li>Ask, <em>“An ambulance arrives at the trailhead. Responders hand over an injured patient to the flight paramedics with ZERO written notes and only say, 'He got hurt on the trail.' What critical information is missing, and what catastrophic errors could happen next?”</em></li><li>Collect student responses: unknown mechanism of injury, changes in vitals over time, applied treatments, allergies, and time elapsed.</li><li>Bridge with, <em>“In emergency medicine, if it wasn't documented, it didn't happen. Today you author a formal Patient Care Report (PCR) and wilderness safety plan.”</em></li></ul>''')+
              flow("#4a9d2f","Minutes 5-15 - Patient Care Report sections and objective evidence",'''<p>Project the standard 5-part Patient Care Report template (FYF pp. 53-54).</p><ul><li>Teach the core medical documentation rule: <strong>Record raw observations, never guesses or premature diagnoses.</strong> (Write <em>“patient displays swelling and discoloration on right index finger with pain upon movement,”</em> NOT <em>“compound fracture of the proximal phalanx”</em>).</li><li>Review the five required sections: (1) Incident/Scene Overview, (2) Chief Complaint &amp; Patient Statements, (3) Objective Observations, (4) Immediate Actions Taken &amp; Comfort Checks, and (5) Medical Handoff Summary.</li><li>Review the 16-point Major Rubric criteria.</li></ul>''')+
              flow("#1f617a","Minutes 15-35 - Complete Patient Care Report and complication safety plan",'''<p>Students author their fictional Patient Care Report based on the trail scenario.</p><ul><li>Complete all 5 report sections with factual, objective language.</li><li>Select ONE wilderness complication scenario: (A) Severe Approaching Thunderstorm, (B) Anxious / Hyperventilating Patient, or (C) Fast-Moving River Crossing between the team and the trailhead.</li><li>Formulate a 4-part Complication Protocol: Immediate Action, Team/Patient Communication, Reassessment Trigger, and Safe Alternative Route.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 20): Audit report language—eliminate speculative medical diagnoses in favor of observable signs.<br>• Lap 2 (Minute 28): Check complication plans—ensure students addressing the river crossing NEVER enter fast-moving water; ensure thunderstorm plans seek enclosed shelter away from open ridges.</li></ul>''')+
              flow("#e3ad19","Minutes 35-45 - Self-audit against rubric and revisions",'''<p>Students audit their draft against the 16-point rubric.</p><ul><li>Check criteria: Objective observations, clear timeline, safety-first complication protocol, and professional EMT documentation connection.</li><li>Students write at least ONE visible revision sentence improving clarity, precision, or safety.</li></ul>''')+
              flow("#24323d","Minutes 45-50 - Wilderness trade-off dilemma DOL and submission",'''<p>Direct students to the Day 4 Exit Ticket.</p><ul><li>Trade-off dilemma: <em>“Explain why attempting to cross a fast-moving swollen creek to save 30 minutes of hiking creates an unacceptable life-safety risk. What is the correct professional action, and what must dispatch be told?”</em></li><li>Collect all Patient Care Reports and Safety Plans for Major evaluation.</li><li><strong>Safe Trim:</strong> Prioritize Sections 1-4 of the PCR and the complication choice. Allow bulleted protocol steps in place of extended paragraphs if writing time is constrained.</li></ul>''')
            ),
            "MONITOR":"<p>Thunder: seek a substantial building or hard-topped vehicle. Fast/unknown water: do not enter. Anxiety: communicate calmly and honestly. Full reports separate observation from inference, name the documentation or handoff responsibility, and provide an organized handoff.</p>",
            "SUPPORT":"<p>Use “I observed…,” “Our team represented…,” and “We would stop and reassess if…”. Speech-to-text or teacher scribing may be used when documented.</p>",
            "FALLBACK":"<p>No simulation is required. An absent student uses the fictional images and completes the same report independently.</p>"},
          5:{
            "TITLE":"Career and Integrity Reflection","SUBTITLE":"50 minutes · TEKS d(1)(C), d(2)(A), d(4)(F)",
            "ALERT":"<strong>Core evidence first.</strong> H&amp;L, Xello, and Roadtrip Nation are optional this week; there is no required Xello completion task here.",
            "PREP":f'<ul><li>Return the route guide, evidence tracker, and report.</li><li>Print/post the <a href="/courses/{COURSE_ID}/files/{files["REFLECTION"]["id"]}/preview">individual reflection</a>.</li><li>Open optional platforms only after the core work is ready.</li></ul>',
            "EVIDENCE":"<p>Collect one five-part individual reflection. Day 4 remains the week's 16-point durable evidence set; do not add a second major for platform clicks.</p>",
            "FLOW":(
              flow("#5a2d91","Minutes 0-5 - Welcome and career fit reflection warm-up",'''<p>Welcome students, seat them with their weekly materials, and project the career fit prompt.</p><ul><li>Ask, <em>“After exploring 911 dispatch, patrol routes, forensic lake investigations, and wilderness medical rescues, where do you personally stand on first-responder careers: Interested, Unsure, or Not Interested? Name ONE specific job detail that explains your stance.”</em></li><li>Hear 2-3 student perspectives. Reiterate: A well-defended 'Not Interested' based on shift work, high stress, or physical demands earns full credit.</li><li>Bridge with, <em>“Today we assemble our first-responder evidence, synthesize the role of ethical integrity in emergency services, and map our next career steps.”</em></li></ul>''')+
              flow("#4a9d2f","Minutes 5-15 - Route evidence audit and labor cross-check",'''<p>Students retrieve their Day 1 Route Guide and audit their labor evidence.</p><ul><li>Verify that all salary figures are properly labeled with their May 2024 BLS national median context and caveat notes.</li><li>Clarify career progression realities: Detectives do not graduate directly into investigative roles; they typically begin as uniformed patrol officers and advance through departmental experience.</li></ul>''')+
              flow("#1f617a","Minutes 15-27 - Professional integrity across the first responder sector",'''<p>Conduct a whole-group synthesis on how accurate information protects lives and justice.</p><ul><li>Analyze the weekly thread: (1) 911 call details, (2) Clinton Lake chain-of-custody test logs, (3) Patient Care Report handoffs, and (4) Scene safety disclosures.</li><li>Ask, <em>“What happens in the justice system or an emergency room if a first responder conceals an inconvenient fact, alters a timeline, or exaggerates an observation?”</em></li><li>Students identify specific consequences: wrongful convictions, fatal medication errors, or compromised team safety.</li></ul>''')+
              flow("#e3ad19","Minutes 27-42 - Complete individual career & integrity reflection",'''<p>Distribute the First Responder Career and Integrity Reflection.</p><ul><li>Students complete the five required reflection prompts: (1) Verified career route fact, (2) Daily job reality, (3) Critical integrity moment from the week, (4) Personal career alignment decision, and (5) Actionable next step for high school planning.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 32): Confirm students articulate a concrete integrity scenario rather than vague generalities like 'be honest.'<br>• Lap 2 (Minute 38): Verify students state realistic next steps connected to Irving ISD offerings.</li></ul>''')+
              flow("#24323d","Minutes 42-50 - Concept map DOL, packet check, and collection",'''<p>Direct students to the Day 5 Exit Ticket Concept Map.</p><ul><li>Students complete the 4-part connection map: (1) Accurate Information Recorded &rarr; (2) First Responder Worker &rarr; (3) Dependent Person (patient, citizen, judge) &rarr; (4) Impact/Consequence of inaccurate records.</li><li>Collect completed reflection sheets and Day 1 route guides.</li><li><strong>Safe Trim:</strong> If discussion runs long, complete the 5-part reflection independently and use the concept map as the silent closing check. Omit optional vendor browsing.</li></ul>''')
            ),
            "MONITOR":"<p>Detectives typically begin as police officers; do not require a fixed 3-5 year ladder. Accept informed “not interested.” Strong integrity answers name the information, who relies on it, and a plausible consequence.</p>",
            "SUPPORT":"<p>Provide a vocabulary bank: route, responsibility, observation, handoff, integrity, reassess. Let students rehearse with a partner but submit their own evidence.</p>",
            "FALLBACK":"<p>The paper/Canvas reflection is the normal route. H&amp;L, Xello, and a video may be omitted without losing the target.</p>"}
        }
        contracts={
          1:{"TOPIC":"First Responder Routes","OBJECTIVE":"Students will describe the Law, Public Safety, Corrections and Security cluster, compare civilian and military law-enforcement route systems, and identify first-responder careers and preparation requirements.","TEKS":"d(1)(B), d(1)(C), d(2)(A)","DOL":"Three career comparisons, a civilian/military route analysis, two district connections, and a cluster description.","STUDENT_OBJECTIVE":"describe the Law, Public Safety, Corrections and Security cluster, compare civilian and military law-enforcement route systems, and identify first-responder careers and preparation requirements.","STUDENT_DOL":"Three career comparisons, a civilian/military route analysis, two district connections, and a cluster description."},
          2:{"TOPIC":"Evidence Integrity","OBJECTIVE":"Students will separate observations from claims, assess source limits, and write a conclusion that uses three files and names an uncertainty.","TEKS":"d(4)(F)","DOL":"Clinton Lake Evidence Tracker.","STUDENT_OBJECTIVE":"separate observations from claims, assess source limits, and write a conclusion that uses three files and names an uncertainty.","STUDENT_DOL":"Clinton Lake Evidence Tracker."},
          3:{"TOPIC":"Response Communication","OBJECTIVE":"Students will describe SAR/WFR responsibilities and demonstrate safe communication, consent, observation, and documentation in a career simulation.","TEKS":"d(1)(C)","DOL":"Injured on the Trail Simulation Record.","STUDENT_OBJECTIVE":"describe SAR/WFR responsibilities and demonstrate safe communication, consent, observation, and documentation in a career simulation.","STUDENT_DOL":"Injured on the Trail Simulation Record."},
          4:{"TOPIC":"Professional Documentation","OBJECTIVE":"Students will identify EMT and Search and Rescue documentation responsibilities, write an accurate fictional Patient Care Report, and choose a safety-first response to one wilderness complication.","TEKS":"d(1)(C), d(4)(F)","DOL":"Fictional Patient Care Report and Safety Plan with one specific career-role connection.","STUDENT_OBJECTIVE":"identify EMT and Search and Rescue documentation responsibilities, write an accurate fictional Patient Care Report, and choose a safety-first response to one wilderness complication.","STUDENT_DOL":"Fictional Patient Care Report and Safety Plan with one specific career-role connection."},
          5:{"TOPIC":"Career Integrity","OBJECTIVE":"Students will complete the career comparison, synthesize week evidence, and explain how accurate reporting protects people.","TEKS":"d(1)(C), d(2)(A), d(4)(F)","DOL":"First Responder Career and Integrity Reflection plus completed route guide.","STUDENT_OBJECTIVE":"complete the career comparison, synthesize week evidence, and explain how accurate reporting protects people.","STUDENT_DOL":"First Responder Career and Integrity Reflection plus completed route guide."}}
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
