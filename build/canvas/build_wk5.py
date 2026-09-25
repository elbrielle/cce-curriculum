"""Build the unpublished 1SW Week 5 teacher/student Canvas module."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
import httpx

BASE="https://learn.irvingisd.net"; COURSE_ID=98060
MODULE_NAME="1SW Wk5: Cybersecurity and Capstone"
MODULE_ALIASES={MODULE_NAME,"1SW Wk5: Cybersecurity, Favorite Clusters, and Capstone","1SW Wk5: Cyber Defenders - Cybersecurity Careers and Capstone","1SW Wk5: Cyber Defenders — Cybersecurity Careers and Capstone"}
MAPPED_MAJOR_TITLE="MAJOR 2: Canva Cybersecurity Bootcamp Flyer"
MAJOR_GROUP_NAME="Major Assessments (60%)"
RUBRIC_NOTE_MARKER='data-cce-rubric-note="cce-advisory-rubric-v1"'
MAJOR_SUBMISSION_TYPES={"online_upload"}
ROOT=Path(__file__).resolve().parents[2]; TEMPLATES=Path(__file__).parent/"templates"; ASSETS=ROOT/"cce-curriculum/resources/canvas-licensed/1sw/wk5"
SUPPORT_NAMES={"ROUTE":"wk5-cyberseek-pathway.pdf","CHECK":"wk5-red-flag-checklist.pdf","PLAN":"wk5-bootcamp-planning-template.pdf","MODEL":"wk5-bootcamp-model.pdf","RUBRIC":"wk5-capstone-portfolio-rubric.pdf","REFLECTION":"wk5-reflection-update-template.pdf","REFLECTION_BI":"wk5-reflection-update-bilingual.pdf"}
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

def flow(color,title,text): return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0 0 6px;color:{color}">{title}</h4>{text}</div>'

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
          1:{"PROGRAM_IMAGE_ID":uploads[1]["irving-it-programs.png"]["id"],"FLAGS_IMAGE_ID":uploads[2]["safe-or-spoofed-red-flags.jpg"]["id"],"ROUTE_FILE_ID":files["ROUTE"]["id"]},
          2:{"FLAGS_IMAGE_ID":uploads[2]["safe-or-spoofed-red-flags.jpg"]["id"],"CHECK_FILE_ID":files["CHECK"]["id"],"EMAIL_DETAILS":image_details(COURSE_ID,uploads[2])},
          3:{"BOOTCAMP_IMAGE_ID":uploads[3]["community-cybersecurity-bootcamp.jpg"]["id"],"PLAN_IMAGE_ID":uploads[3]["integrity-and-original-work.png"]["id"],"PLAN_FILE_ID":files["PLAN"]["id"],"MODEL_FILE_ID":files["MODEL"]["id"],"MAJOR_ASSIGNMENT_ID":mapped_major["id"]},
          4:{"PROFILE_IMAGE_ID":uploads[4]["it-app-exploration.png"]["id"],"ROUTE_FILE_ID":files["ROUTE"]["id"]},
          5:{"OPTIONS_IMAGE_ID":uploads[1]["irving-it-programs.png"]["id"],"ROUTE_FILE_ID":files["ROUTE"]["id"],"REFLECTION_FILE_ID":files["REFLECTION"]["id"],"REFLECTION_BI_FILE_ID":files["REFLECTION_BI"]["id"],"RUBRIC_FILE_ID":files["RUBRIC"]["id"],"MAJOR_ASSIGNMENT_ID":mapped_major["id"]}}
        student_titles={1:"STUDENT: 1SW Wk5 Day 1 - Cybersecurity Career Routes",2:"STUDENT: 1SW Wk5 Day 2 - Safe or Spoofed Inbox",3:"STUDENT: 1SW Wk5 Day 3 - Canva Cybersecurity Bootcamp Flyer",4:"STUDENT: 1SW Wk5 Day 4 - Strengthen Cybersecurity Career Evidence",5:"STUDENT: 1SW Wk5 Day 5 - Improve and Submit the Canva Flyer"}
        student_urls={3:"student-1sw-wk5-day-3-canva-cybersecurity-bootcamp-flyer",5:"student-1sw-wk5-day-5-improve-and-submit-the-canva-flyer"}
        teacher_data={
          1:{
            "TITLE":"Emerging Cybersecurity Work","SUBTITLE":"50 minutes - TEKS d(1)(D)",
            "ALERT":"<strong>Use the dated route guide as the core.</strong> H&amp;L and CyberSeek are optional live exploration. Do not promise a fixed ladder, DFW pay, or an entry-level Information Security Analyst job.",
            "PREP":f'<ul><li>Print/post the one-page <a href="/courses/{COURSE_ID}/files/{files["ROUTE"]["id"]}/preview">Cybersecurity Career Route Guide</a>.</li><li>Open FYF p. 24 and pp. 36-37. Project the dated analyst snapshot; students do not need a live BLS page.</li><li>If using CyberSeek or H&amp;L, preflight on a student Chromebook and record the retrieval date.</li></ul>',
            "EVIDENCE":"<p>Formative/minor option: the same one-page guide holds the growth comparison, one duty or preparation fact, one data limit, three possible preparation stages, and a current interest judgment. Live vendor access is not graded.</p>",
            "FLOW":(
              flow("#5a2d91","Minutes 0-10 - Begin with the workbook's cybersecurity task",'''<p>Welcome students and open FYF p. 24. Ask, <em>“A message says your account closes today unless you click a link. What can an analyst actually see that should make them pause?”</em> Give one minute to point to the workbook red flags, then hear two answers. Distinguish a visible clue from an unproved conclusion. Tell students they will use p. 25 once tomorrow for the seven-email investigation.</p>''')+
              flow("#4a9d2f","Minutes 10-20 - District program and one data model",'''<p>Open FYF pp. 36-37 and identify Irving ISD's Cybersecurity program of study. Distinguish a high-school program, a paid occupation, and a credential. Project the one-page Route Guide and model its analyst snapshot. The $129,180 May 2025 U.S. median is a middle wage, not Irving starting pay; 21% growth for 2025-35 is a projection, not a promised job. Ask, <em>“What does this source tell us, and what does it leave unanswered?”</em> Students do not navigate BLS or copy a second table.</p>''')+
              flow("#1f617a","Minutes 20-40 - Compare roles and sketch one possible route",'''<p>Students use the Route Guide's three short work descriptions to name one duty or preparation fact. They complete the emerging-career judgment using the printed growth comparison, circle one data limit, and sketch three stages: now, high school, and after high school. The three roles are examples, not a required ladder. At minute 30, check the growth label and one plausible school step. Accept an interested, unsure, or not-interested judgment.</p>''')+
              flow("#e3ad19","Minutes 40-45 - Partner evidence check",'''<p>Partner A reads one fact and the route it supports. Partner B asks, <em>“What does that fact not prove?”</em> Switch. Students repair one unsupported or overstated claim on the same guide.</p>''')+
              flow("#24323d","Minutes 45-50 - Evaluate and close",'''<p>Students explain why Information Security Analyst may be an emerging occupation using the dated growth figure, one work or preparation fact, and a source limitation. Collect the same Route Guide for Day 4. Leave FYF p. 25 blank for tomorrow's investigation.</p>''')
            ),
            "MONITOR":"<p>BLS key: Information Security Analysts protect networks and systems; typical preparation is a bachelor's degree plus related experience, although other routes exist; May 2025 U.S. median $129,180; projected growth 21% for 2025-35 compared with about 3% for all occupations. Valid limitation: national rather than Irving pay, median rather than starting pay, or projection rather than guarantee. Accept varied routes when the student labels them as possible.</p>",
            "SUPPORT":"<p>Pre-teach median, projected, related experience, certification, and program of study. Let students highlight the two exact facts before writing, choose a source-limit phrase, and rehearse the judgment orally.</p>",
            "FALLBACK":"<p>The dated guide is the normal no-web route and supports absence recovery. If a live title or count differs, record the date rather than forcing it to match the worksheet.</p>"},
          2:{
            "TITLE":"Safe or Spoofed? Phishing Investigation","SUBTITLE":"50 minutes - TEKS d(1)(C)",
            "ALERT":"<strong>Practice never gets sent.</strong> Use fictional people and example.com addresses only. No real credentials, links, QR codes, attachments, or district impersonation.",
            "PREP":f'<ul><li>Open FYF p. 25 as the class writing surface. Keep the <a href="/courses/{COURSE_ID}/files/{files["CHECK"]["id"]}/preview">Phishing Red-Flag Checklist</a> only for a student who needs an alternate surface; never assign both.</li><li>Open the seven authenticated Canvas email images and FYF pp. 24-25.</li><li>Post the response: Pause, verify independently, report, delete.</li></ul>',
            "EVIDENCE":"<p>Formative/minor option: seven decisions plus the hardest-call explanation and safe response. Do not score a student on whether their first call matches; score the evidence and revision.</p>",
            "FLOW":(
              flow("#5a2d91","Minutes 0-5 - Welcome and visible evidence warm-up",'''<p>Welcome students and project Email 1 on the screen without clicking any links.</p><ul><li>Ask, <em>“Look closely at Email 1. Name ONE visible clue that should make you pause, without deciding whether it's real yet.”</em></li><li>Take two student observations. Distinguish raw <strong>observation</strong> (e.g. 'the sender address ends in @prize-center123.net') from the final <strong>decision</strong> ('it is a phishing scam').</li><li>Bridge with, <em>“Cybersecurity analysts evaluate hard evidence before making a security call. Today we investigate seven suspicious emails.”</em></li></ul>''')+
              flow("#4a9d2f","Minutes 5-15 - Five phishing red flags and response protocol",'''<p>Open FYF p. 24 and teach the Five Phishing Red Flags systematically:</p><ul><li>1. <strong>Suspicious Sender Address</strong> (look past the display name to the actual email domain).</li><li>2. <strong>Urgency or Emotional Pressure</strong> ('ACT NOW', threats of account suspension).</li><li>3. <strong>Requests for Private Information</strong> (passwords, SSNs, credit card verification).</li><li>4. <strong>Unusual Links or Attachments</strong> (hovering reveals mismatched URLs).</li><li>5. <strong>Spelling, Grammar, or Formatting Inconsistencies</strong>.</li><li>Post the standard enterprise response protocol: <strong>Pause &rarr; Verify Independently &rarr; Report &rarr; Delete</strong>.</li></ul>''')+
              flow("#1f617a","Minutes 15-38 - Seven-email structured investigation",'''<p>Open the seven authenticated Canvas email images in sequence.</p><ul><li>Students inspect each email and record one decision and reason on FYF p. 25 before the next email. The optional checklist replaces p. 25 for a student who needs it.</li><li>Run Think-Pair-Share after Email 4: <em>“The strongest red flag is [clue] because [reason]. The safe professional response is [action].”</em></li><li>Remind students: 'Safe-looking' (Emails 3 &amp; 7) does not mean proven safe. In a real workplace, unexpected corporate emails are verified through official internal portals or known HR contacts.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 20): Check Email 2—verify students catch the spoofed spelling ('amaz0n' with a zero).<br>• Lap 2 (Minute 28): Check Email 5—verify students identify the false one-hour deadline and unrelated URL.<br>• Lap 3 (Minute 34): Confirm students evaluate visible evidence rather than guessing.</li></ul>''')+
              flow("#e3ad19","Minutes 38-46 - Professional response and integrity DOL",'''<p>Use the class discussion questions at the bottom of FYF p. 25. Students explain the hardest call and a safe action orally, then write one margin sentence: A cybersecurity worker shows integrity by ___ because ___.</p><ul><li>Ask: Which email was hardest, and what visible evidence decided your choice?</li><li>Ask: Why would you check through a known app or contact instead of replying to the message?</li><li>Check the margin sentence for an honest, protective action and a reason.</li></ul>''')+
              flow("#24323d","Minutes 46-50 - Safe practice review and close",'''<p>Review findings and conclude the investigation.</p><ul><li>Review the seven decisions on FYF p. 25 and the four-step protocol aloud. Collect only a student’s alternate checklist when that is the assigned writing surface.</li><li>Dock Chromebooks properly.</li><li><strong>Safe Trim:</strong> If time runs short, shorten partner discussion and the optional practice draft. Keep all seven workbook decisions and the margin integrity sentence.</li></ul>''')
            ),
            "MONITOR":"<p><strong>Key:</strong> 1 spoofed (prize, odd sender/link); 2 spoofed (amaz0n and order-check domain); 3 safe-looking (company HR, no link/private request; still verify through portal/known HR); 4 spoofed (.co sender, TODAY, update link); 5 spoofed (urgent suspension and unrelated fix domain); 6 spoofed (.co sender and portal-login link); 7 safe-looking (ordinary manager note; verify through known channel if uncertain). A polished message is not automatically safe. Hover previews a desktop URL; it does not verify the sender.</p>",
            "SUPPORT":"<p>Read the sender and visible domain aloud, color-code each flag, let pairs talk before individual decisions, and use the sentence frame: 'I marked ___ because ___.' Do not require full translations.</p>",
            "FALLBACK":"<p>All seven images are in the student guide. FYF p. 25 is the normal writing surface; the checklist is an alternate for a student without an accessible workbook. On touch devices, use visible domains and independent verification; do not require long-pressing an unknown link.</p>"},
          3:{
            "TITLE":"Canva Cybersecurity Bootcamp Flyer","SUBTITLE":"50 minutes - TEKS d(4)(F)",
            "ALERT":"<strong>Plan once.</strong> FYF p. 35 is the default planning space. Keep the bootcamp packet's flyer checklist as design criteria and its planning prompts as an alternative scaffold. Students draft in Canva today and submit one final flyer to Major 2 on Day 5.",
            "PREP":f'<ul><li>Open FYF pp. 34-35, the <a href="/courses/{COURSE_ID}/files/{files["PLAN"]["id"]}/preview">bootcamp planning and flyer checklist packet</a>, and the <a href="/courses/{COURSE_ID}/files/{files["MODEL"]["id"]}/preview">completed teacher model</a>. Project the checklist; give the packet planning spaces only to students who need them instead of FYF p. 35.</li><li>Confirm school-account Canva access and demonstrate a portrait flyer design with sample text replaced.</li><li>Open the <a href="/courses/{COURSE_ID}/assignments/{mapped_major["id"]}">Canva flyer assignment</a> and <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">16-point flyer rubric</a>.</li><li>Prepare a fictional sign-up example such as Ask your teacher; no real student contact information.</li></ul>',
            "EVIDENCE":f'<p>FYF p. 35 holds six formative planning answers. Students save one Canva draft today and submit one final PNG or PDF to <a href="/courses/{COURSE_ID}/assignments/{mapped_major["id"]}">Major 2</a> on Day 5. The flyer alone is scored with the 16-point rubric; peer feedback is formative.</p>',
            "FLOW":(
              flow("#5a2d91","Minutes 0-5 - Welcome and work-ethic question",'''<p>Define <strong>work ethic</strong> as doing careful work and following through, and <strong>integrity</strong> as acting honestly even when no one sees the choice. Ask, <em>“Before teaching someone how to spot a scam, what would you check?”</em> Take two workplace examples, such as an analyst testing a demonstration, checking safety advice, or removing private information. Ask which example shows work ethic and which shows integrity; a strong answer names the action and why it matters.</p>''')+
              flow("#4a9d2f","Minutes 5-13 - Read the FYF need and name safety boundaries",'''<p>Open FYF p. 34. Students choose one audience and one printed safety topic. Tell them the percentages on this page are part of the scenario and should not be reused as current statistics on the flyer. Model one cautious action, such as opening a known app rather than a link in a suspicious message. Ask why a promise to stop every scam would be misleading.</p>''')+
              flow("#1f617a","Minutes 13-25 - Plan once",'''<p>Students answer the six workbook questions on FYF p. 35. Students who need more structure use the existing bootcamp packet's planning prompts instead of the workbook spaces. Model two learning goals as actions participants can practice. At minute 18, check that each student has one audience and two actions. At minute 23, ask whether the proposed activity practices the promised goals. Use the FYF class discussion prompt to identify one behind-the-scenes work-ethic action and one privacy or integrity choice. Keep that discussion oral.</p>''')+
              flow("#e3ad19","Minutes 25-45 - Build a Canva draft",'''<p>Project the packet's Flyer Checklist so students can check clear criteria without filling another sheet. Demonstrate opening Canva with a school account, searching for a portrait flyer, replacing sample text and graphics, enlarging the event title, and choosing readable contrast. Students create one-page drafts with the program name, audience, topic, time/place, teacher-approved sign-up method, two accurate safety actions, and one relevant visual. At minute 34, check advice; at minute 42, check for private contact details and unsupported claims. A template supplies layout, not facts.</p>''')+
              flow("#24323d","Minutes 45-50 - Peer check and save",'''<p>Partners name one clear element and one change that would help the audience read or trust the flyer. Students save their Canva drafts and state one revision to make on Day 5. Show the Major 2 assignment link so students know where the final file goes. Do not collect the workbook plan through Canvas.</p>''')
            ),
            "MONITOR":"<p>Work ethic is visible through checking facts, preparing, and revising. Integrity is visible through original or credited work, cautious claims, and a privacy-safe sign-up. Look for one audience, two actionable safety tips, readable event details, and no personal student phone number, email, or address.</p>",
            "SUPPORT":"<p>Read the six FYF questions aloud. Offer the packet's planning spaces as the student's one response home when extra prompts are needed; everyone may view its flyer checklist. Offer the word bank audience, action, sign-up, check, credit. Rehearse: Our audience can ___ to stay safer because ___. Show one Canva edit at a time.</p>",
            "FALLBACK":"<p>If Canva is inaccessible for an individual student, choose an accessible flyer design format and score the same evidence. An absent student uses FYF pp. 34-35 and the Student Guide. The alternate replaces Canva for that student and is not a second product.</p>"},
          4:{
            "TITLE":"Which Cybersecurity Work Fits Me?","SUBTITLE":"50 minutes - TEKS d(1)(C)",
            "ALERT":"<strong>Write once in FYF p. 38.</strong> The one-page Day 1 guide is a reference. No new BLS collection, second guide, profile action, or personal career disclosure is required.",
            "PREP":f'<ul><li>Open FYF pp. 36-38 and the three work descriptions on the <a href="/courses/{COURSE_ID}/files/{files["ROUTE"]["id"]}/preview">Day 1 Cybersecurity Career Route Guide</a>.</li><li>Project three tasks: helping a user, maintaining a network, and investigating a suspicious message.</li><li>Test ClassLink to the H&amp;L Information Technology Cluster only if offering the app exploration.</li></ul>',
            "EVIDENCE":"<p>The reflection space on FYF p. 38 holds one role the student might try or reject, a reason grounded in the work, and one next question or school action. A drawing or emoji may support the words. The Day 1 BLS snapshot is not reassigned.</p>",
            "FLOW":(
              flow("#5a2d91","Minutes 0-5 - Welcome and match the work",'''<p>Welcome students and project the three short tasks. Ask, <em>“Which task would you try for one day, and why?”</em> Invite a reasoned “none of these” answer. Students tell a partner one thought without committing to a career.</p>''')+
              flow("#4a9d2f","Minutes 5-15 - Find the school connection in FYF",'''<p>Open FYF pp. 36-37. Ask students to point to the Cybersecurity program of study and one school option that might help them test an interest. Explain that a Personal Graduation Plan can change as interests change. Ask, <em>“Which option could you investigate while you are still in school?”</em> Students use the page as the source; they do not copy it into another sheet.</p>''')+
              flow("#1f617a","Minutes 15-30 - Compare the three roles",'''<p>Use the three short work descriptions on the Day 1 guide. Match each projected task to user support, network administration, or information security analysis. Model one interest with a limitation: <em>“I am curious about investigating suspicious messages, but I want to know how often analysts explain findings to other people.”</em> Partner A names a role and a duty; Partner B asks, <em>“What would you need to learn or try before deciding?”</em> Switch. Students may name a role they do not want.</p>''')+
              flow("#e3ad19","Minutes 30-45 - Optional app exploration and workbook reflection",'''<p>If H&amp;L works, open it through ClassLink and follow FYF p. 38: Information Technology Cluster, Cluster Tour, Game Time, and a Hat that fits or does not fit. Stop the app work by minute 40. If the app is not available, return to the three work tasks and FYF pp. 36-37. In either case, students write in the <strong>Jot down your thoughts</strong> space on FYF p. 38: one role they might try or reject, one reason, and one next question or school action. An emoji or sketch may support the reason but not replace it.</p>''')+
              flow("#24323d","Minutes 45-50 - Close with one useful next step",'''<p>Ask, <em>“What could you do in school to learn whether this work fits you?”</em> Invite students to share a question or action without revealing a private career preference. Check FYF p. 38 for the role, reason, and next question or action. Do not collect a second BLS comparison or guide.</p>''')
            ),
            "MONITOR":"<p>User support helps people solve computer problems; network administration maintains systems; information security analysis protects systems and investigates risks. A school program is a way to explore, not a guaranteed job. Accept interested, unsure, or not interested when the student gives a reason from the work. If salary comes up, remind students that the Day 1 snapshot was a national median, not proof of fit.</p>",
            "SUPPORT":"<p>Read each task aloud and let students point before speaking. Offer help, maintain, protect, and investigate as a word bank. Use the stem: <em>“I might try ___ because ___. I still want to know ___.”</em> Allow oral rehearsal, a small drawing, or a dictated p. 38 response.</p>",
            "FALLBACK":"<p>FYF pp. 36-38 and the three printed role descriptions provide the complete absent-student path. H&amp;L is optional. If the workbook space is inaccessible, record the same thought in the student's assigned accessible format and collect it once.</p>"},
          5:{
            "TITLE":"Improve and Submit the Canva Flyer","SUBTITLE":"50 minutes - TEKS d(3)(A)",
            "ALERT":"<strong>One Major 2 flyer submission.</strong> Students describe one high-school graduation requirement and one typical career preparation requirement in FYF p. 36, improve their Canva design, and confirm one Canvas upload. No four-part portfolio or Evidence Log is required.",
            "PREP":f'<ul><li>Open FYF p. 36, the saved Canva drafts, and the <a href="/courses/{COURSE_ID}/files/{files["ROUTE"]["id"]}/preview">Day 1 career guide</a>.</li><li>Model the two transitions: high-school courses must meet graduation requirements; the guide says an information security analyst typically needs a bachelor\'s degree plus related experience, while other routes exist.</li><li>Open the <a href="/courses/{COURSE_ID}/assignments/{mapped_major["id"]}">flyer assignment</a> and <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">rubric</a>. Demonstrate Canva Share &rarr; Download and the Canvas upload confirmation.</li><li>Prepare the teacher-selected accessible design and submission process for individual students who need it.</li></ul>',
            "EVIDENCE":f'<p>Two FYF p. 36 margin statements describe requirements for middle-to-high-school planning and high-school-to-career preparation; they are formative evidence for d(3)(A). The final one-page flyer is the only <a href="/courses/{COURSE_ID}/assignments/{mapped_major["id"]}">Major 2</a> submission. Add the four rubric ratings, divide by 16, multiply by 100, and round to the nearest whole point for the 100-point gradebook entry. Do not ask for a separate portfolio, symbol, copied plan, or Evidence Log.</p>',
            "FLOW":(
              flow("#5a2d91","Minutes 0-5 - Welcome and flexible planning",'''<p>Ask, <em>“Why might someone update a Personal Graduation Plan?”</em> Open FYF p. 36 and take one example. Explain that the next action can be specific even when the student's career interest may change.</p>''')+
              flow("#4a9d2f","Minutes 5-15 - Describe two academic requirements",'''<p>Students read the PGP explanation on FYF p. 36. Show the Day 1 career guide beside it. Model: <em>“To finish high school, my plan must include courses that meet graduation requirements, such as English.”</em> Then model the guide's typical analyst preparation: a bachelor's degree plus related experience, noting that other routes exist. In the FYF margin, students describe both requirements in their own words. Partners check that each statement names a requirement rather than only an aspiration such as “go to college.”</p>''')+
              flow("#1f617a","Minutes 15-40 - Improve the Canva flyer",'''<p>Students open their Day 3 drafts and the four rubric criteria: audience/event information, accurate safety actions, readability, and integrity/privacy. Give 15 minutes for one visible improvement from feedback. At minute 30, inspect a sample for scenario percentages used as current facts, tiny body text, and personal sign-up details. At minute 38, ask students to zoom out and check whether the action and sign-up method can be found quickly.</p>''')+
              flow("#24323d","Minutes 40-50 - Export, upload, and confirm",'''<p>Students choose Canva Share &rarr; Download and export one page as PNG or PDF. They open Major 2, upload the file, submit, and read back the Canvas confirmation. A download alone is not a submission. If a student revises after uploading, they resubmit under the same assignment. Collect a teacher-approved accessible design once through the documented individual path.</p>''')
            ),
            "MONITOR":"<p>The two workbook statements must describe a high-school graduation course requirement and a typical postsecondary or career preparation requirement. Accept a different sourced career path. A hope or vague action is not a requirement, and the example analyst route is not a career promise. The flyer should show one visible improvement and meet the four rubric criteria; check Canvas submission status.</p>",
            "SUPPORT":"<p>Use course, graduation requirement, degree, experience, and training beside the two prompts. Offer oral rehearsal or dictation. In Canva, model one edit at a time: title size, contrast, safety action, or sign-up method.</p>",
            "FALLBACK":"<p>An absent student uses FYF p. 36 and the saved Canva draft. Select a private accessible flyer format and submission process for an individual who needs one, with the same rubric and one score.</p>"}}
        teacher_data[2].update({
          "TITLE":"Safe or Spoofed? Phishing and Integrity",
          "SUBTITLE":"50 minutes - TEKS d(4)(F)",
          "PREP":f'<ul><li>Open the <a href="/courses/{COURSE_ID}/files/{files["DAY2_DECK"]["id"]}/preview">optional whole-group lesson presentation</a>; it carries the bellringer, model, paced email reveals, midpoint check, and close.</li><li>Keep the <a href="/courses/{COURSE_ID}/files/{files["CHECK"]["id"]}/preview">Phishing Red-Flag Checklist</a> available only for a student who needs a different writing surface. FYF p. 25 holds the seven class decisions; do not assign both.</li><li>Confirm FYF pp. 24-25 and the seven locked email images are available. Post the response: Pause, verify independently, report, delete.</li></ul>',
          "EVIDENCE":"<p>Formative evidence: seven decisions and reasons on FYF p. 25, the hardest-call explanation, a safe response, and one integrity sentence in the workbook margin. Score visible evidence and revision, not whether the first call matches the key.</p>",
          "MONITOR":"<p><strong>Key:</strong> 1 spoofed (prize, odd sender/link); 2 spoofed (amaz0n and order-check domain); 3 safe-looking (company HR, no link/private request; still verify through portal/known HR); 4 spoofed (.co sender, TODAY, update link); 5 spoofed (urgent suspension and unrelated fix domain); 6 spoofed (.co sender and portal-login link); 7 safe-looking (ordinary manager note; verify through known channel if uncertain). Safe-looking is not proven safe. A practice message sent to a real person would be dishonest and could cause harm; it stays fictional and private.</p>"})
        contracts={
          1:{"TOPIC":"Emerging Cybersecurity Work","OBJECTIVE":"Students will evaluate Information Security Analyst as an emerging career using a teacher-modeled, dated career snapshot and one possible preparation path.","TEKS":"d(1)(D)","DOL":"One-page guide with a growth comparison, one work or preparation fact, one data limit, a judgment, and three possible preparation stages."},
          2:{"TOPIC":"Phishing and Integrity","OBJECTIVE":"Students will define and identify work ethic and integrity by evaluating suspicious messages and choosing an ethical cybersecurity response.","TEKS":"d(4)(F)","DOL":"Seven evidence-based message decisions, a hardest-call explanation, an independent verification response, and an integrity explanation."},
          3:{"TOPIC":"Work Ethic and Integrity","OBJECTIVE":"Students will identify work ethic and integrity by planning accurate safety teaching in FYF and beginning a privacy-safe Canva flyer.","TEKS":"d(4)(F)","DOL":"FYF p. 35 plan and a saved Canva draft with an audience, two accurate safety actions, event details, and safe sign-up information."},
          4:{"TOPIC":"Cybersecurity Career Fit","OBJECTIVE":"Students will compare IT work and district pathways, then explain one career interest or question using evidence already studied.","TEKS":"d(1)(C)","DOL":"FYF p. 38 thought with one role they might try or reject, a work-based reason, and one next question or school action."},
          5:{"TOPIC":"Transition Planning and Digital Communication","OBJECTIVE":"Students will describe academic requirements for high school and a career path, then revise and submit a Canva flyer.","TEKS":"d(3)(A)","DOL":"Two formative requirements in the FYF p. 36 margin and one final flyer uploaded to the existing Major 2 assignment."}}
        glances={
          1:{"WORKBOOK":"FYF p. 24 and pp. 36-37","PLATFORM":"None required; H&amp;L or CyberSeek optional","NOTEBOOK":"None","SLIDES":"No separate deck; project the workbook and analyst snapshot","SCAFFOLDS":"One-page Career Route Guide with supplied data, teacher model, and oral rehearsal","EXIT_EVIDENCE":"Emerging-career judgment, one data limit, and three possible preparation stages on the same guide"},
          2:{"WORKBOOK":"FYF pp. 24-25; seven decisions and reasons on p. 25","PLATFORM":"None required; seven fictional email images in Canvas","NOTEBOOK":"None","SLIDES":f'<a href="/courses/{COURSE_ID}/files/{files["DAY2_DECK"]["id"]}/preview">Optional whole-group presentation</a>',"SCAFFOLDS":"Read-aloud, visible clue frame, and alternate checklist only when the workbook is inaccessible","EXIT_EVIDENCE":"Seven p. 25 decisions plus one integrity sentence in the workbook margin"},
          3:{"WORKBOOK":"FYF pp. 34-35; six planning answers on p. 35, or the packet planning spaces as one alternative","PLATFORM":"Canva with the student's school account","NOTEBOOK":"None","SLIDES":"No separate deck; project FYF, the packet checklist, and a teacher Canva flyer model","SCAFFOLDS":f'<a href="/courses/{COURSE_ID}/files/{files["PLAN"]["id"]}/preview">Bootcamp packet</a> checklist and optional planning prompts, completed model, oral rehearsal, and one safety-action stem',"EXIT_EVIDENCE":"One FYF or packet plan and one saved Canva flyer draft; final file goes to Major 2 on Day 5"},
          4:{"WORKBOOK":"FYF pp. 36-38; write in the p. 38 thought space","PLATFORM":"H&amp;L Information Technology Cluster through ClassLink optional","NOTEBOOK":"None","SLIDES":"No separate deck; project the three work tasks and FYF pages","SCAFFOLDS":"Day 1 role descriptions, four-word bank, partner rehearsal, and one sentence stem","EXIT_EVIDENCE":"One p. 38 role choice or rejection, reason, and next question or school action"},
          5:{"WORKBOOK":"FYF p. 36; two academic requirements in the PGP margin","PLATFORM":"Canva Share to Download, then Canvas file upload","NOTEBOOK":"None","SLIDES":"No separate deck; project FYF, the Day 1 career guide, and upload model","SCAFFOLDS":"Two requirement stems, Day 1 career guide, flyer rubric, and teacher Canva export model","EXIT_EVIDENCE":"Two formative workbook requirements and one final PNG or PDF flyer in Major 2"}}
        pages={}
        for day in range(1,6):
            st=student_titles[day]; student=await upsert_page(c,st,render(f"wk5-day{day}-student.html",{"COURSE_ID":COURSE_ID,**student_values[day]}),student_urls.get(day,slugify(st)))
            tt=f"TEACHER: 1SW Wk5 Day {day} Facilitator Guide"; teacher=await upsert_page(c,tt,render("wk5-teacher.html",{"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student["url"],**contracts[day],**glances[day],**teacher_data[day]}),slugify(tt))
            pages[day]={"teacher":teacher,"student":student}
        expected=[]
        for day in range(1,6):
            expected.append(("SubHeader",None,f"Day {day}"))
            for page_kind in ("teacher","student"):
                page=pages[day][page_kind]
                expected.append(("Page",page["url"],page["title"]))
            if day==3: expected.append(("Assignment",mapped_major["id"],MAPPED_MAJOR_TITLE))
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
        if final_failures: raise RuntimeError(f"1SW Wk5 final invariant failed: {final_failures}")
        print(json.dumps({"module":{"id":module_id,"published":module["published"]},"major":{"id":final_major["id"],"published":final_major.get("published"),"points":final_major.get("points_possible"),"group":final_major.get("assignment_group_id"),"grading_type":final_major.get("grading_type"),"omit_from_final_grade":final_major.get("omit_from_final_grade")},"support_folder":{"id":support_folder_info["id"],"locked":support_folder_info["locked"],"file_count":len(support_folder_files)},"folders":{str(d):{"id":f["id"],"locked":f["locked"],"file_count":len(folder_files[d])} for d,f in folders.items()},"files":{k:v["id"] for k,v in files.items()},"pages":{str(d):{k:{"url":v["url"],"published":v["published"]} for k,v in p.items()} for d,p in pages.items()},"items":[{"id":i["id"],"position":i["position"],"title":i["title"],"type":i["type"],"page_url":i.get("page_url"),"content_id":i.get("content_id"),"published":i.get("published")} for i in final]},indent=2))

if __name__=="__main__": asyncio.run(main())
