"""Build the unpublished 1SW Week 3 teacher/student Canvas module."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
import httpx

BASE="https://learn.irvingisd.net"; COURSE_ID=98060
MODULE_NAME="1SW Wk3: Computer Science and Networking Careers"
ROOT=Path(__file__).resolve().parents[2]; TEMPLATES=Path(__file__).parent/"templates"; ASSETS=ROOT/"cce-curriculum/resources/canvas-licensed/1sw/wk3"

def slugify(v): return re.sub(r"[^a-z0-9]+","-",v.lower().replace("&","and")).strip("-")
async def api(c,m,p,**kw):
    r=await c.request(m,f"{BASE}/api/v1{p}",**kw); r.raise_for_status(); return r.json() if r.content else None
async def paged(c,p,params=None):
    out=[]; url=f"{BASE}/api/v1{p}"; q={"per_page":100,**(params or {})}
    while url:
        r=await c.get(url,params=q); r.raise_for_status(); out+=r.json(); url=r.links.get("next",{}).get("url"); q=None
    return out
async def ensure_module(c):
    prior_name="1SW Wk3: Network Ninjas - Computer Science and Networking Careers"
    modules=await paged(c,f"/courses/{COURSE_ID}/modules"); found=next((m for m in modules if m["name"] in {MODULE_NAME,prior_name}),None)
    if found: return await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{found['id']}",data={"module[name]":MODULE_NAME,"module[published]":"false"})
    return await api(c,"POST",f"/courses/{COURSE_ID}/modules",data={"module[name]":MODULE_NAME,"module[published]":"false"})
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
    if uploaded.get("locked") is not True: uploaded=await api(c,"PUT",f"/files/{uploaded['id']}",data={"locked":"true"})
    if uploaded.get("locked") is not True: raise RuntimeError(f"Canvas file did not remain locked: {path.name}")
    return uploaded
async def find_file(c,name):
    files=await paged(c,f"/courses/{COURSE_ID}/files",{"search_term":name}); matches=[f for f in files if f.get("display_name")==name]
    if len(matches)!=1: raise ValueError(f"Expected one Canvas file named {name!r}; found {len(matches)}")
    current=await api(c,"GET",f"/files/{matches[0]['id']}")
    if current.get("locked") is not True: current=await api(c,"PUT",f"/files/{current['id']}",data={"locked":"true"})
    if current.get("locked") is not True: raise RuntimeError(f"Referenced Canvas file did not remain locked: {name}")
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
    if current.get("locked") is not True or missing or unlocked: raise RuntimeError(f"1SW Wk3 folder invariant failed for {folder['id']}: missing={sorted(missing)} unlocked={unlocked}")
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
async def upsert_item(c,module_id,page,title):
    items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); item=next((i for i in items if i.get("page_url")==page["url"]),None)
    if item: return await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",data={"module_item[title]":title})
    return await api(c,"POST",f"/courses/{COURSE_ID}/modules/{module_id}/items",data={"module_item[type]":"Page","module_item[page_url]":page["url"],"module_item[title]":title})
def flow(color,title,text): return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'

async def main():
    token=sys.stdin.readline().strip()
    if not token: raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"},timeout=120) as c:
        module=await ensure_module(c); module_id=module["id"]
        support_names={
          "CARDS":"wk3-networking-career-cards.pdf","SKILLS":"wk3-transferable-skills-list.pdf","UX":"wk3-ux-audit-scaffold.pdf","WIRE":"wk3-wireframe-template.pdf","WIRE_BI":"wk3-wireframe-template-bilingual.pdf","RESEARCH":"wk3-emerging-tech-research-template.pdf","LINKS":"wk3-emerging-careers-link-sheet.pdf","RUBRIC":"wk3-app-design-rubric.pdf","COMPARE":"wk3-day4-career-comparison.pdf","REFLECTION":"wk3-day5-learning-style-connection.pdf",
          "E1":"1sw-wk3-day1-networking-systems-pathway-transferable-skills.pdf","E2":"1sw-wk3-day2-website-revamp-audit-a-real-site.pdf"}
        support_folder="course files/CCR Materials/1SW/Wk3"; support_folder_record=await ensure_folder(c,support_folder); files={}
        for key,name in support_names.items():
            source_dir=ROOT/"docs/resources/exit-tickets" if name.startswith("1sw-") else ROOT/"docs/resources/worksheets"
            files[key]=await upload(c,source_dir/name,support_folder)
        files["XELLO"]=await find_file(c,"learning-styles.pdf")
        await lock_folder_files(c,support_folder_record,support_names.values())
        uploads={}; folders={}
        for day in range(1,6):
            folder_path=f"course files/CCR Materials/1SW/Wk3/Day {day} Visuals"; folders[day]=await ensure_folder(c,folder_path); uploads[day]={}
            day_dir=ASSETS/f"day{day}"
            if day_dir.exists():
                for path in sorted(day_dir.glob("*.png")): uploads[day][path.name]=await upload(c,path,folder_path)
            required_names=[path.name for path in sorted(day_dir.glob("*.png"))] if day_dir.exists() else []
            await lock_folder_files(c,folders[day],required_names)
        student_values={
          1:{"APP_IMAGE_ID":uploads[1]["it-app-exploration.png"]["id"],"CARDS_FILE_ID":files["CARDS"]["id"],"SKILLS_FILE_ID":files["SKILLS"]["id"],"EXIT_FILE_ID":files["E1"]["id"]},
          2:{"PAGE28_IMAGE_ID":uploads[2]["website-revamp-034.png"]["id"],"PAGE29_IMAGE_ID":uploads[2]["website-revamp-035.png"]["id"],"SLIDE_IMAGE_ID":uploads[2]["website-revamp-climber-slide.png"]["id"],"FALLBACK_IMAGE_ID":uploads[2]["paws-and-claws-home.png"]["id"],"SCAFFOLD_FILE_ID":files["UX"]["id"],"EXIT_FILE_ID":files["E2"]["id"]},
          3:{"P30_IMAGE_ID":uploads[3]["wireframe-workbook-036.png"]["id"],"P31_IMAGE_ID":uploads[3]["wireframe-workbook-037.png"]["id"],"P32_IMAGE_ID":uploads[3]["wireframe-workbook-038.png"]["id"],"P33_IMAGE_ID":uploads[3]["wireframe-workbook-039.png"]["id"],"TEMPLATE_FILE_ID":files["WIRE"]["id"],"BILINGUAL_FILE_ID":files["WIRE_BI"]["id"],"RUBRIC_FILE_ID":files["RUBRIC"]["id"]},
          4:{"LINKS_FILE_ID":files["LINKS"]["id"],"RESEARCH_FILE_ID":files["RESEARCH"]["id"],"EXIT_FILE_ID":files["COMPARE"]["id"]},
          5:{"REFLECTION_FILE_ID":files["REFLECTION"]["id"],"RUBRIC_FILE_ID":files["RUBRIC"]["id"]}}
        student_titles={1:"STUDENT: 1SW Wk3 Day 1 - Compare Networking Careers",2:"STUDENT: 1SW Wk3 Day 2 - Audit a Website",3:"STUDENT: 1SW Wk3 Day 3 - Build Four App Screens",4:"STUDENT: 1SW Wk3 Day 4 - Research an Emerging IT Career",5:"STUDENT: 1SW Wk3 Day 5 - Learning Style and IT Connection"}
        teacher_data={
          1:{"TITLE":"Networking Careers + Transferable Skills","SUBTITLE":"50 minutes - TEKS d(1)(C), d(4)(B)","ALERT":"<strong>H&amp;L is optional.</strong> The career cards carry all required evidence. Use Xello for current local salary when available; never grade an unverified live salary figure.","PREP":f'<ul><li>Print or post the <a href="/courses/{COURSE_ID}/files/{files["CARDS"]["id"]}/preview">four career cards</a>, <a href="/courses/{COURSE_ID}/files/{files["SKILLS"]["id"]}/preview">transferable-skills list</a>, and <a href="/courses/{COURSE_ID}/files/{files["E1"]["id"]}/preview">exit ticket</a>.</li><li>If using H&amp;L or Xello, test one optional related-role search on a student Chromebook. Exact live titles are not required.</li></ul>',"EVIDENCE":"<p>Formative evidence: four-role comparison plus Venn exit. Grade the career-task and transferable-skill reasoning, not platform completion or local salary.</p>","FLOW":flow("#5a2d91","Network failure warm-up - 5 minutes","Students name a likely system check, not only ‘call IT.’")+flow("#4a9d2f","Four-career comparison - 22 minutes","Use career cards as the complete route; platforms may add exploration.")+flow("#1f617a","Transferable-skill connections - 15 minutes","Compare one programming and one networking role.")+flow("#e3ad19","Venn exit - 8 minutes","Two unique skills per side, two shared skills, and one evidence-based bottom line."),"MONITOR":"<p>Programming: coding, debugging, application logic, software testing. Networking/data: network design, traffic monitoring, accounts, routers, databases, backups, and requirements. Shared: problem-solving, communication, attention to detail, teamwork, time management, and patience. Accept another overlap when the student connects it to a real task in both roles.</p>","SUPPORT":"<p>Pre-teach network, database, systems, administrator, architect, and transferable. Students may circle skills before writing and rehearse the final sentence orally.</p>","FALLBACK":"<p>The printed career cards are the complete route. An absent student completes the same comparison and Venn exit without a platform catch-up requirement.</p>"},
          2:{"TITLE":"Website Revamp - UX Audit","SUBTITLE":"50 minutes - TEKS d(1)(C)","ALERT":"<strong>Preflight the practice site.</strong> Open Paws and Claws through the student filter and complete the checkout path. The student guide includes a locked, captured homepage if the live site is unavailable.","PREP":f'<ul><li>Open the student guide and test pawsandclaws.hatsandladders.com.</li><li>Print the optional <a href="/courses/{COURSE_ID}/files/{files["UX"]["id"]}/preview">UX scaffold</a> and <a href="/courses/{COURSE_ID}/files/{files["E2"]["id"]}/preview">Rosa exit ticket</a>.</li><li>Open the embedded captured homepage once so it is ready if the live practice site is blocked.</li></ul>',"EVIDENCE":"<p>Formative/minor option: three strengths, five problems, three fixes with user benefits, and a redesign sketch. The exit ticket is formative.</p>","FLOW":flow("#5a2d91","Best/worst UX warm-up - 5 minutes","Sort examples into easy, clear, fast versus cluttered, vague, broken.")+flow("#4a9d2f","UX rules - 12 minutes","Read the workbook examples and model one problem/fix/user-benefit chain.")+flow("#1f617a","Audit and redesign - 27 minutes","Three strengths, five problems, three fixes, one sketch.")+flow("#e3ad19","Rosa exit - 6 minutes","Name two problems and explain the highest-impact fix."),"MONITOR":"<p>Accept vague menu labels, buried or low-contrast Sign Up, hobbies before services, and one long unstructured page. A strong fix names the user action made easier—not only a color or decoration change.</p>","SUPPORT":"<p>Use the scaffold’s categories and sentence stem: ‘This helps users because they can now…’ Students may sketch before writing the explanation.</p>","FALLBACK":"<p>Use the locked captured homepage already embedded in the student guide. The audit fields and grading stay identical. An absent student can work from the embedded workbook pages and saved example without waiting for the live site.</p>"},
          3:{"TITLE":"From Wireframe to Wow","SUBTITLE":"50 minutes - TEKS d(1)(C)","ALERT":"<strong>Major-grade evidence starts today.</strong> Print four wireframe sheets per supported student and show where packets will be collected. Drawing quality is not scored.","PREP":f'<ul><li>Print the <a href="/courses/{COURSE_ID}/files/{files["WIRE"]["id"]}/preview">wireframe template</a> or <a href="/courses/{COURSE_ID}/files/{files["WIRE_BI"]["id"]}/preview">bilingual version</a>, four pages per student who uses it.</li><li>Post the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">16-point major rubric</a>.</li><li>Decide packet labels, collection, and return.</li></ul>',"EVIDENCE":"<p><strong>Major grade, 16 points total:</strong> today supplies App Plan, Screen Design, and Response to Feedback. Day 4 supplies Emerging Career Evidence. Hold or staple the pieces together.</p>","FLOW":flow("#5a2d91","App-use warm-up - 4 minutes","Count taps to the app’s main action.")+flow("#4a9d2f","Choose and plan - 7 minutes","Brief, name, specific target user, and two or three features.")+flow("#1f617a","Four wireframes - 24 minutes","Home, Main Menu, Action, and Success with a next click on every screen.")+flow("#e3ad19","Partner test and revision - 15 minutes","Written confusion, then two starred changes."),"MONITOR":"<p>Home shows identity/first action; Menu shows selectable features; Action shows what happens; Success confirms a result and differs from Home. Every screen has a next click. Both starred revisions trace to written feedback.</p>","SUPPORT":"<p>Keep the symbol key visible. Use preprinted frames, bilingual labels, oral partner feedback, and a teacher/peer walkthrough for an absent partner.</p>","FALLBACK":"<p>Plain paper works. An absent student uses a teacher, catch-up partner, or recorded peer comment for the same feedback-and-revision evidence.</p>"},
          4:{"TITLE":"Emerging Tech Research","SUBTITLE":"50 minutes - TEKS d(1)(C), d(1)(D)","ALERT":"<strong>Use the supplied dated evidence guide.</strong> BLS numbers are national. Students must label the exact occupation, closest occupation, or proxy. Xello may add a separately labeled DFW salary only when the exact title, geography, measure, and date are visible.","PREP":f'<ul><li>Post the <a href="/courses/{COURSE_ID}/files/{files["LINKS"]["id"]}/preview">dated Emerging IT Career Evidence Guide</a>.</li><li>Print or post the <a href="/courses/{COURSE_ID}/files/{files["RESEARCH"]["id"]}/preview">research sheet</a>, <a href="/courses/{COURSE_ID}/files/{files["COMPARE"]["id"]}/preview">career comparison</a>, and rubric.</li><li>No employer-posting scavenger hunt or teacher-created source packet is required.</li></ul>',"EVIDENCE":"<p><strong>Major-grade criterion:</strong> BLS occupation, national pay, growth, typical preparation, exact/proxy label and limit, and an evidence-based emerging-work claim. Attach this sheet to the Day 3 packet.</p>","FLOW":flow("#5a2d91","Technology-change warm-up - 5 minutes","Name one technology or work task that changed.")+flow("#4a9d2f","Choose and model source labels - 8 minutes","Show the Data Scientist exact match and AI/ML proxy.")+flow("#1f617a","Controlled research - 30 minutes","Complete eight fields from the dated guide and named BLS page.")+flow("#e3ad19","Evidence comparison - 7 minutes","Compare two growth rates and state the proxy limit."),"MONITOR":"<p>AI/ML uses Computer and Information Research Scientists as a proxy; Cloud Architect uses Computer Network Architects as a proxy; Drone Software Developer uses Software Developers as a proxy. Information Security Analyst and Data Scientist are exact BLS occupations. UX Designer uses Web and Digital Interface Designers as the closest occupation. A missing standalone title is not proof of emergence.</p>","SUPPORT":"<p>Start students with an exact-match career, prefill the BLS occupation, and highlight pay, growth, and preparation on the guide. Allow oral rehearsal before the evidence claim.</p>","FALLBACK":"<p>The dated evidence guide is the complete source route. H&amp;L and Xello are optional on this day. Absent students use the same packet without waiting for platform access.</p>"},
          5:{"TITLE":"Emerging Career Pitches + Xello Learning Style","SUBTITLE":"50 minutes - TEKS d(1)(C), d(1)(D)","ALERT":"<strong>Required Xello spine:</strong> Learning Style is the Week 3 task and needs 20 protected minutes. Add Skills belongs in Week 4. Use the 15-20 minute My Learning Styles prerequisite guide; the separate 70-minute lesson is optional and assumes additional prerequisites.","PREP":f'<ul><li>Check Xello rosters and the Completion Standards report.</li><li>Open the licensed <a href="/courses/{COURSE_ID}/files/{files["XELLO"]["id"]}/preview">My Learning Styles prerequisite guide</a>.</li><li>Print the <a href="/courses/{COURSE_ID}/files/{files["REFLECTION"]["id"]}/preview">Learning Style connection sheet</a>.</li><li>Return Day 4 research sheets and organize groups of four or five.</li></ul>',"EVIDENCE":"<p><strong>Major grade:</strong> App Design Packet + Emerging Career Evidence, 16 points. Required Xello evidence is Learning Style quiz completion in the report. The one-minute pitch and Learning Style connection are formative.</p>","FLOW":flow("#5a2d91","Pitch setup and rehearsal - 4 minutes","Highlight the BLS occupation, work, preparation, dated numbers, source match, and changing-work reason.")+flow("#4a9d2f","Small-group lightning pitches - 20 minutes","One minute each plus one evidence-based star and one question; no simultaneous live scoring burden.")+flow("#1f617a","Xello Learning Style - 20 minutes","Complete the quiz, review the result, and record one useful strategy.")+flow("#e3ad19","Career connection - 6 minutes","Connect the result or known strategy to one IT task and final interest call."),"MONITOR":"<p>Pitch: selected title, BLS occupation, work, preparation, dated pay and growth, exact/proxy label, and changing-work reason. Xello: correct Learning Style task, result reviewed, one usable strategy. Students may decide IT is not a fit and still earn full evidence credit.</p>","SUPPORT":"<p>Provide complete-thought pitch frames, permit reading from the research sheet, support Xello navigation, read result descriptions aloud, and offer private audio or written pitch routes with the same content criteria.</p>","FALLBACK":"<p>Record the Xello access issue. The student completes the connection sheet with a learning strategy that already works; the required quiz moves to the next supervised catch-up block. Absent students may give the pitch to the teacher or a catch-up group.</p>"}}
        contracts={
          1:{"TOPIC":"Networking Careers","OBJECTIVE":"Students will identify four networking and data career opportunities in the Information Technology cluster and compare transferable skills used in networking and programming work.","TEKS":"d(1)(C), d(4)(B)","DOL":"Completed four-role comparison plus a Venn diagram with two role-specific skills on each side, two shared transferable skills, and one evidence-based explanation."},
          2:{"TOPIC":"User Experience","OBJECTIVE":"Students will identify UX design as an Information Technology career opportunity by analyzing how a website supports or blocks a user's goal and proposing evidence-based improvements.","TEKS":"d(1)(C)","DOL":"UX audit with three strengths, five observable problems, three fixes with user benefits, one redesign sketch, and a supported Rosa mini-case response."},
          3:{"TOPIC":"App Wireframes","OBJECTIVE":"Students will identify app design as an Information Technology career opportunity by planning, testing, and revising a four-screen user flow for a specific audience.","TEKS":"d(1)(C)","DOL":"App plan, four labeled wireframes with clear next actions, written walkthrough feedback, and two starred revisions tied to that feedback."},
          4:{"TOPIC":"Emerging IT Work","OBJECTIVE":"Students will research and evaluate one emerging or rapidly changing Information Technology occupation by distinguishing an exact occupation from a proxy and using dated evidence about work, preparation, pay, and projected growth.","TEKS":"d(1)(C), d(1)(D)","DOL":"Completed emerging-career research and comparison with the BLS occupation, exact/proxy status, dated national pay and growth, preparation, source limit, and changing-work explanation."},
          5:{"TOPIC":"Career Evidence","OBJECTIVE":"Students will identify and evaluate an emerging or rapidly changing Information Technology occupation by presenting dated work, preparation, pay, growth, and exact/proxy evidence from their research.","TEKS":"d(1)(C), d(1)(D)","DOL":"One-minute evidence pitch plus required Xello Learning Style quiz completion and the Learning Style/IT connection sheet."}}
        pages={}
        for day in range(1,6):
            st=student_titles[day]; student=await upsert_page(c,st,render(f"wk3-day{day}-student.html",{"COURSE_ID":COURSE_ID,**student_values[day]}),slugify(st))
            tt=f"TEACHER: 1SW Wk3 Day {day} Facilitator Guide"; teacher=await upsert_page(c,tt,render("wk3-teacher.html",{"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student["url"],**contracts[day],**teacher_data[day]}),slugify(tt))
            await upsert_item(c,module_id,teacher,tt); await upsert_item(c,module_id,student,st); pages[day]={"teacher":teacher,"student":student}
        items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); by_url={i.get("page_url"):i for i in items}
        desired=[]; used=set()
        for day in range(1,6):
            header=next((i for i in items if i.get("type")=="SubHeader" and i.get("title")==f"Day {day}"),None)
            if header: desired.append(header["id"]); used.add(header["id"])
            for page_kind in ("teacher","student"):
                item=by_url[pages[day][page_kind]["url"]]; desired.append(item["id"]); used.add(item["id"])
        desired.extend(i["id"] for i in sorted(items,key=lambda item:item["position"]) if i["id"] not in used)
        for position,item_id in reversed(list(enumerate(desired,start=1))): await api(c,"PUT",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item_id}",data={"module_item[position]":position})
        final=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items"); module=await api(c,"GET",f"/courses/{COURSE_ID}/modules/{module_id}")
        print(json.dumps({"module":{"id":module_id,"published":module["published"]},"folders":{str(d):{"id":f["id"],"locked":f["locked"]} for d,f in folders.items()},"pages":{str(d):{k:{"url":v["url"],"published":v["published"]} for k,v in p.items()} for d,p in pages.items()},"items":[{"id":i["id"],"position":i["position"],"title":i["title"],"page_url":i.get("page_url")} for i in final]},indent=2))

asyncio.run(main())
