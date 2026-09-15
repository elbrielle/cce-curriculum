"""Build the unpublished 1SW Week 3 teacher/student Canvas module."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
import httpx

BASE="https://learn.irvingisd.net"; COURSE_ID=98060
MODULE_NAME="1SW Wk3: Computer Science and Networking Careers"
ROOT=Path(__file__).resolve().parents[2]; TEMPLATES=Path(__file__).parent/"templates"; ASSETS=ROOT/"cce-curriculum/resources/canvas-licensed/1sw/wk3"
XELLO_LESSON=ROOT/"cce-curriculum/resources/xello-licensed/lessons/explore-learning-styles.pdf"

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
def flow(color,title,text): return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0 0 6px;color:{color}">{title}</h4>{text}</div>'

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
        files["XELLO"]=await upload(c,XELLO_LESSON,support_folder)
        await lock_folder_files(c,support_folder_record,(*support_names.values(),XELLO_LESSON.name))
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
        student_titles={1:"STUDENT: 1SW Wk3 Day 1 - Compare Networking Careers",2:"STUDENT: 1SW Wk3 Day 2 - Audit a Website",3:"STUDENT: 1SW Wk3 Day 3 - Build Four App Screens",4:"STUDENT: 1SW Wk3 Day 4 - Research an Emerging IT Career",5:"STUDENT: 1SW Wk3 Day 5 - Learning Style Quiz and Lesson"}
        teacher_data={
          1:{
            "TITLE":"Networking Careers + Transferable Skills","SUBTITLE":"50 minutes - TEKS d(1)(C), d(4)(B)",
            "ALERT":"<strong>H&amp;L is optional.</strong> The career cards carry all required evidence. Use Xello for current local salary when available; never grade an unverified live salary figure.",
            "PREP":f'<ul><li>Print or post the <a href="/courses/{COURSE_ID}/files/{files["CARDS"]["id"]}/preview">four career cards</a>, <a href="/courses/{COURSE_ID}/files/{files["SKILLS"]["id"]}/preview">transferable-skills list</a>, and <a href="/courses/{COURSE_ID}/files/{files["E1"]["id"]}/preview">exit ticket</a>.</li><li>If using H&amp;L or Xello, test one optional related-role search on a student Chromebook. Exact live titles are not required.</li></ul>',
            "EVIDENCE":"<p>Formative evidence: four-role comparison plus Venn exit. Grade the career-task and transferable-skill reasoning, not platform completion or local salary.</p>",
            "FLOW":(
              flow("#5a2d91","Minutes 0-5 - Welcome and school network warm-up",'''<p>Welcome students to class and project the daily warm-up question.</p><ul><li>Ask, <em>“If the school Wi-Fi went down right now, whose job would it be to fix it? What do you think they would actually DO to fix it?”</em></li><li>Collect two or three quick ideas. If students say 'the IT person,' push deeper: <em>“What would that person check first? Cables? A router? The main server?”</em></li><li>Bridge with, <em>“Today we explore the people who design, maintain, and secure the network infrastructure that connects everything.”</em></li></ul>''')+
              flow("#4a9d2f","Minutes 5-27 - Compare four networking and data careers",'''<p>Distribute the Networking Career Cards and open H&amp;L Information Technology.</p><ul><li>Introduce the four roles: <strong>Network Administrator</strong> (operates and troubleshoots daily systems), <strong>Network Architect</strong> (designs networks from scratch), <strong>Database Administrator</strong> (secures and organizes stored data), and <strong>Systems Analyst</strong> (bridges business needs and tech solutions).</li><li>Students complete the four-row comparison chart: career name, one technical task, one transferable skill, and why that skill matters in the role.</li><li>Contrast networking vs. tech support: networking builds and protects the shared digital highways; tech support helps individual users with their devices and apps.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 10): Confirm all students have their cards or digital profiles open and have started role 1.<br>• Lap 2 (Minute 18): Check that students are recording concrete technical tasks rather than general descriptions.<br>• Lap 3 (Minute 24): Verify that students have articulated why each transferable skill matters for that specific job.</li></ul>''')+
              flow("#1f617a","Minutes 27-42 - Transferable skills cross-pathway analysis",'''<p>Guide students to compare ONE programming career from Week 2 with ONE networking role from today.</p><ul><li>Ask, <em>“What skills help a professional succeed in BOTH careers, even though the coding and technical tasks are different?”</em></li><li>Capture student suggestions on the board: problem-solving, written and oral communication, attention to detail, time management, teamwork, curiosity, and patience under pressure.</li><li>Define <strong>transferable skills</strong>: high-value capabilities that apply across multiple jobs and industries.</li><li>Conduct a 60-second Stop and Jot using the stem: <em>“[Skill] transfers across [Programming role] and [Networking role] because both workers must [action].”</em></li></ul>''')+
              flow("#e3ad19","Minutes 42-47 - Programming vs. networking Venn diagram DOL",'''<p>Direct students to the Day 1 Exit Ticket Venn diagram.</p><ul><li>Students record two skills unique to Programming, two skills unique to Networking, and two shared transferable skills.</li><li>Students write their supported conclusion explaining which career path fits someone who prefers building new software versus someone who prefers designing and troubleshooting system infrastructure.</li></ul>''')+
              flow("#24323d","Minutes 47-50 - Save, close, and trim point",'''<p>Conclude the lesson and organize materials.</p><ul><li>Collect the exit tickets and have students return career cards to the table center.</li><li>Ensure Chromebooks are docked and charging.</li><li><strong>Safe Trim:</strong> If the four-role comparison takes longer, reduce whole-group sharing on transferable skills. Protect the complete four-role record and the Venn diagram DOL.</li></ul>''')
            ),
            "MONITOR":"<p>Programming: coding, debugging, application logic, software testing. Networking/data: network design, traffic monitoring, accounts, routers, databases, backups, and requirements. Shared: problem-solving, communication, attention to detail, teamwork, time management, and patience. Accept another overlap when the student connects it to a real task in both roles.</p>",
            "SUPPORT":"<p>Pre-teach network, database, systems, administrator, architect, and transferable. Students may circle skills before writing and rehearse the final sentence orally.</p>",
            "FALLBACK":"<p>The printed career cards are the complete route. An absent student completes the same comparison and Venn exit without a platform catch-up requirement.</p>"},
          2:{
            "TITLE":"Website Revamp - UX Audit","SUBTITLE":"50 minutes - TEKS d(1)(C)",
            "ALERT":"<strong>Preflight the practice site.</strong> Open Paws and Claws through the student filter and complete the checkout path. The student guide includes a locked, captured homepage if the live site is unavailable.",
            "PREP":f'<ul><li>Open the student guide and test pawsandclaws.hatsandladders.com.</li><li>Print the optional <a href="/courses/{COURSE_ID}/files/{files["UX"]["id"]}/preview">UX scaffold</a> and <a href="/courses/{COURSE_ID}/files/{files["E2"]["id"]}/preview">Rosa exit ticket</a>.</li><li>Open the embedded captured homepage once so it is ready if the live practice site is blocked.</li></ul>',
            "EVIDENCE":"<p>Formative/minor option: three strengths, five problems, three fixes with user benefits, and a redesign sketch. The exit ticket is formative.</p>",
            "FLOW":(
              flow("#5a2d91","Minutes 0-5 - Welcome and best/worst website warm-up",'''<p>Welcome students and project the daily website critique prompt.</p><ul><li>Ask, <em>“Think of the BEST website you use and the WORST website you have ever visited. What made the good one great? What made the bad one unbearable?”</em></li><li>Sort student responses on the board into two clear columns: Good UX (fast, clean, intuitive, clear buttons) vs. Bad UX (cluttered, slow, confusing menus, broken links).</li><li>Bridge with, <em>“Today you are UX Designers. Your job is to identify what is frustrating users on a real site and design the fixes.”</em></li></ul>''')+
              flow("#4a9d2f","Minutes 5-17 - Learn about UX and analyze core design rules",'''<p>Open FYF p. 28 and read Step 1 together to establish UX industry foundations.</p><ul><li>Define User Experience (UX): the overall ease, logic, and satisfaction a user feels when navigating a digital product.</li><li>Present the client scenario: a company is losing online customers because their website is confusing, and they hired you to revamp it.</li><li>Model the UX Designer problem-to-solution chain on the board: <strong>Observable Problem &rarr; Specific Fix &rarr; Measurable User Benefit</strong>.</li><li>Emphasize: <em>“A design critique is about how easily a user finishes a task, not personal taste about colors or pictures.”</em></li></ul>''')+
              flow("#1f617a","Minutes 17-44 - Practice site investigation, audit, and redesign",'''<p>Direct students to the Paws and Claws practice site (or the locked fallback images in Canvas).</p><ul><li><strong>Step 2 (5 min):</strong> Students click through as first-time pet owners trying to book a grooming appointment. Run a 90-second Stop and Jot on sticky notes: <em>“The first thing I tried to do was...”</em> and <em>“I got stuck when...”</em></li><li><strong>Step 3 (9 min):</strong> Students record at least 3 things that work well and at least 5 observable UX problems in their workbook (FYF p. 29).</li><li><strong>Step 4 (9 min):</strong> Students select 3 problems and complete the three-column table: Problem, Fix, and How Your Fix Will Help Users.</li><li><strong>Step 5 (4 min):</strong> On plain paper or template, students sketch an improved page layout incorporating one of their fixes.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 23): Verify students have identified at least 5 distinct problems (e.g. low-contrast buttons, buried signup, cluttered text).<br>• Lap 2 (Minute 32): Target column 3—check that students explain the user benefit (e.g. 'users can book in two clicks') rather than just cosmetic tweaks.<br>• Lap 3 (Minute 40): Check that redesign sketches include clear navigation labels and call-to-action buttons.</li></ul>''')+
              flow("#e3ad19","Minutes 44-48 - Rosa tutoring site mini-case DOL",'''<p>Direct students to the Day 2 Exit Ticket: Rosa's tutoring business has a confusing one-page website with buried buttons and vague labels.</p><ul><li>Students identify two specific UX problems using today's vocabulary.</li><li>Students write their recommended fix and explain why that fix will bring Rosa the most new students.</li></ul>''')+
              flow("#24323d","Minutes 48-50 - Save, close, and trim point",'''<p>Organize student audit sheets and clean workspaces.</p><ul><li>Collect exit tickets and ensure redesign sketches are stored in student folders.</li><li>Dock Chromebooks properly.</li><li><strong>Safe Trim:</strong> If site navigation takes extra time, reduce the redesign sketch to a simple wireframe box layout. Protect the five identified problems, three user-benefit fixes, and the Rosa DOL.</li></ul>''')
            ),
            "MONITOR":"<p>Accept vague menu labels, buried or low-contrast Sign Up, hobbies before services, and one long unstructured page. A strong fix names the user action made easier—not only a color or decoration change.</p>",
            "SUPPORT":"<p>Use the scaffold’s categories and sentence stem: ‘This helps users because they can now…’ Students may sketch before writing the explanation.</p>",
            "FALLBACK":"<p>Use the locked captured homepage already embedded in the student guide. The audit fields and grading stay identical. An absent student can work from the embedded workbook pages and saved example without waiting for the live site.</p>"},
          3:{
            "TITLE":"From Wireframe to Wow","SUBTITLE":"50 minutes - TEKS d(1)(C)",
            "ALERT":"<strong>Major-grade evidence starts today.</strong> Print four wireframe sheets per supported student and show where packets will be collected. Drawing quality is not scored.",
            "PREP":f'<ul><li>Print the <a href="/courses/{COURSE_ID}/files/{files["WIRE"]["id"]}/preview">wireframe template</a> or <a href="/courses/{COURSE_ID}/files/{files["WIRE_BI"]["id"]}/preview">bilingual version</a>, four pages per student who uses it.</li><li>Post the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">16-point major rubric</a>.</li><li>Decide packet labels, collection, and return.</li></ul>',
            "EVIDENCE":"<p><strong>Major grade, 16 points total:</strong> today supplies App Plan, Screen Design, and Response to Feedback. Day 4 supplies Emerging Career Evidence. Hold or staple the pieces together.</p>",
            "FLOW":(
              flow("#5a2d91","Minutes 0-5 - Welcome and app efficiency warm-up",'''<p>Welcome students and project the mobile app interaction prompt.</p><ul><li>Ask, <em>“Open your favorite app in your mind. How many taps does it take to do the MAIN thing you use it for? Where is the primary menu button?”</em></li><li>Invite two students to describe their app's user flow.</li><li>Bridge with, <em>“Yesterday you audited someone else's site. Today you become mobile app designers, creating every screen from scratch before a single line of code is written.”</em></li></ul>''')+
              flow("#4a9d2f","Minutes 5-12 - Choose app brief and plan core features",'''<p>Open FYF p. 30 and introduce the three client design briefs.</p><ul><li>Option A: <strong>Food Connection App</strong> (connects restaurants/stores with food banks to eliminate food waste).</li><li>Option B: <strong>Stress-Less App</strong> (schedule organizer with 5-minute screen-free destress tools for students).</li><li>Option C: <strong>Passion Project App</strong> (hobby and project incubator for teenagers).</li><li>Students select one brief and complete Step 2 planning: App Name, Target Audience, and 2-3 Core Features.</li><li>Review the standard wireframe symbol key: box with an X (image/media), horizontal lines (text/copy), solid rectangle/oval (clickable button), and three horizontal bars (hamburger menu).</li></ul>''')+
              flow("#1f617a","Minutes 12-36 - Sketch four-screen wireframe user flow",'''<p>Distribute the wireframe templates (or FYF pp. 31-32) and start the 24-minute build timer.</p><ul><li>Students design four connected screens: (1) <strong>Home Screen</strong> (welcome &amp; identity), (2) <strong>Main Menu</strong> (selectable features), (3) <strong>Action Screen</strong> (interactive task execution), and (4) <strong>Success Screen</strong> (confirmation of completion).</li><li>Rule: Every screen must have a labeled next-click action so a user is never trapped.</li><li>Remind students: <em>“Wireframes are blueprints, not finished artwork. Focus on button placement, clear labels, and logical user flow.”</em></li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 18): Confirm all students have named their app, defined their user, and completed Screen 1.<br>• Lap 2 (Minute 26): Check Screen 3 (Action)—ensure it shows what happens when a user taps a feature.<br>• Lap 3 (Minute 32): Check Screen 4 (Success)—ensure it differs clearly from Home and confirms the result.</li></ul>''')+
              flow("#e3ad19","Minutes 36-47 - Partner usability testing and revision",'''<p>Partners trade wireframe packets for a structured usability test (FYF p. 33).</p><ul><li>Each partner silently walks through the screens and verbalizes where they would tap to complete a task.</li><li>Provide stems: <em>“On Screen [X] I did not know where to tap next,”</em> and <em>“Your Success screen confirms [X], but it does not tell the user [Y].”</em></li><li>Partners record written feedback directly in the packet.</li><li>Students review feedback and star at least TWO specific improvements made to their wireframes (e.g. added a back button, clarified a label).</li></ul>''')+
              flow("#24323d","Minutes 47-50 - Collect Major 1 draft and close",'''<p>Collect and organize student app design packets.</p><ul><li>Staple or clip the app plan, four wireframe screens, and partner feedback sheet together—these form the first half of <strong>Major 1</strong>.</li><li><strong>Safe Trim:</strong> Shorten partner feedback to 6 minutes (3 min per partner). Protect the four complete wireframes and two starred revisions.</li></ul>''')
            ),
            "MONITOR":"<p>Home shows identity/first action; Menu shows selectable features; Action shows what happens; Success confirms a result and differs from Home. Every screen has a next click. Both starred revisions trace to written feedback.</p>",
            "SUPPORT":"<p>Keep the symbol key visible. Use preprinted frames, bilingual labels, oral partner feedback, and a teacher/peer walkthrough for an absent partner.</p>",
            "FALLBACK":"<p>Plain paper works. An absent student uses a teacher, catch-up partner, or recorded peer comment for the same feedback-and-revision evidence.</p>"},
          4:{
            "TITLE":"Emerging Tech Research","SUBTITLE":"50 minutes - TEKS d(1)(C), d(1)(D)",
            "ALERT":"<strong>Use the supplied dated evidence guide.</strong> BLS numbers are national. Students must label the exact occupation, closest occupation, or proxy. Xello may add a separately labeled DFW salary only when the exact title, geography, measure, and date are visible.",
            "PREP":f'<ul><li>Post the <a href="/courses/{COURSE_ID}/files/{files["LINKS"]["id"]}/preview">dated Emerging IT Career Evidence Guide</a>.</li><li>Print or post the <a href="/courses/{COURSE_ID}/files/{files["RESEARCH"]["id"]}/preview">research sheet</a>, <a href="/courses/{COURSE_ID}/files/{files["COMPARE"]["id"]}/preview">career comparison</a>, and rubric.</li><li>No employer-posting scavenger hunt or teacher-created source packet is required.</li></ul>',
            "EVIDENCE":"<p><strong>Major-grade criterion:</strong> BLS occupation, national pay, growth, typical preparation, exact/proxy label and limit, and an evidence-based emerging-work claim. Attach this sheet to the Day 3 packet.</p>",
            "FLOW":(
              flow("#5a2d91","Minutes 0-5 - Welcome and emerging technology warm-up",'''<p>Welcome students and project the technology evolution prompt.</p><ul><li>Ask, <em>“Name one technology you use every single day that did NOT exist when your parents or teachers were in middle school.”</em></li><li>Collect examples: smartphones, AI chatbots, streaming algorithms, smartwatches, cloud drives.</li><li>Bridge with, <em>“New technology can create brand-new career titles, or it can radically transform older jobs. Today you research emerging IT careers and evaluate labor evidence.”</em></li></ul>''')+
              flow("#4a9d2f","Minutes 5-13 - Choose career and model exact vs. proxy data",'''<p>Project the six emerging IT career options from the dated evidence guide.</p><ul><li>The six options: (1) AI/Machine Learning Engineer, (2) Cloud Architect, (3) Information Security Analyst, (4) Data Scientist, (5) UX Designer, and (6) Drone Software Developer.</li><li>Teach the essential distinction between an <strong>exact BLS match</strong> vs. a <strong>proxy occupation</strong>: Data Scientist is an exact BLS title; AI Engineer uses Computer and Information Research Scientists as a broader proxy.</li><li>Ask, <em>“Why is a proxy helpful, and what is its limitation?”</em> Listen for: it gives useful context for related work, but it is not an exact wage guarantee for that specific title.</li></ul>''')+
              flow("#1f617a","Minutes 13-43 - Controlled source research on emerging careers",'''<p>Students open the Emerging IT Career Evidence Guide and the research template.</p><ul><li>Students complete the eight required fields: chosen title, BLS occupation used, exact vs. proxy label, work tasks, entry preparation, national median pay + year, growth rate + projection years, and the technology change driving emergence.</li><li>Guide students to keep national median figures separate from any optional local Xello ranges.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 18): Confirm every student has chosen a career and correctly identified whether it is an exact match or a proxy.<br>• Lap 2 (Minute 28): Check that students are recording the specific technology or demand change (e.g. AI automation, cloud migration) driving the job.<br>• Lap 3 (Minute 37): Verify that median pay and growth rates have their dates and geography properly labeled.</li></ul>''')+
              flow("#e3ad19","Minutes 43-48 - Evidence comparison DOL",'''<p>Direct students to the Emerging and Established Career Comparison sheet.</p><ul><li>Students compare their emerging career against an established IT role on pay, growth, and preparation.</li><li>Students answer the prompt: would you recommend this emerging pathway to a student entering the workforce in ten years? Support with two dated facts.</li></ul>''')+
              flow("#24323d","Minutes 48-50 - Collect and attach to Major 1 packet",'''<p>Finalize the research phase of Major 1.</p><ul><li>Students attach today's completed research sheet to yesterday's wireframe packet.</li><li>Store packets for tomorrow's final Major 1 portfolio turn-in.</li><li><strong>Safe Trim:</strong> If research runs long, omit the second comparison career and evaluate only the primary emerging role. Protect the exact/proxy label, growth data, and emerging-work rationale.</li></ul>''')
            ),
            "MONITOR":"<p>AI/ML uses Computer and Information Research Scientists as a proxy; Cloud Architect uses Computer Network Architects as a proxy; Drone Software Developer uses Software Developers as a proxy. Information Security Analyst and Data Scientist are exact BLS occupations. UX Designer uses Web and Digital Interface Designers as the closest occupation. A missing standalone title is not proof of emergence.</p>",
            "SUPPORT":"<p>Start students with an exact-match career, prefill the BLS occupation, and highlight pay, growth, and preparation on the guide. Allow oral rehearsal before the evidence claim.</p>",
            "FALLBACK":"<p>The dated evidence guide is the complete source route. H&amp;L and Xello are optional on this day. Absent students use the same packet without waiting for platform access.</p>"},
          5:{
            "TITLE":"Xello Learning Style Quiz and Learning Styles Lesson","SUBTITLE":"50 minutes - TEKS d(1)(A)",
            "ALERT":"<strong>Protect both Grade 7 tasks.</strong> Learning Style uses 20 minutes and the Learning styles lesson uses 30 minutes. Week 2 supplied the three saved-career dependency. Collect the completed Major 1 packet before students open Xello; do not squeeze the former pitch into this block.",
            "PREP":f'<ul><li>Check Xello rosters, the Completion Standards report, and whether each student has three saved careers from Week 2.</li><li>Open the licensed <a href="/courses/{COURSE_ID}/files/{files["XELLO"]["id"]}/preview">Grade 7 Learning styles guide</a> and the teacher demo account.</li><li>Print the <a href="/courses/{COURSE_ID}/files/{files["REFLECTION"]["id"]}/preview">Method-to-Task Connection</a>; its built-in visual, auditory, and tactile chart is the complete no-Xello content route.</li><li>Post one collection location for the completed Major 1 packet.</li></ul>',
            "EVIDENCE":"<p><strong>Major grade:</strong> App Design Packet + Emerging Career Evidence, 16 points, collected before the Xello block. Separate Grade 7 evidence is the Learning Style quiz, Learning styles lesson, and one method-to-task connection. The method-chart route completes today's learning evidence when Xello is blocked without creating false platform completion.</p>",
            "FLOW":(
              flow("#5a2d91","Minutes 0-5 - Welcome and learning methods launch",'''<p>Welcome students, collect the completed Major 1 packets, and project the learning styles agenda.</p><ul><li>Collect the combined App Design + Emerging Career packets (Major 1, 16 points).</li><li>Introduce today's dual Xello tasks: the <strong>Learning Style quiz</strong> (20 min) and the <strong>Learning styles lesson</strong> (30 min).</li><li>Preview the three method categories: Visual (watching/reading), Auditory (listening/speaking), and Tactile (hands-on/movement).</li><li>Emphasize: <em>“A learning style is a set of strategies you can test, not a box that defines your intelligence or limits what you can achieve.”</em></li></ul>''')+
              flow("#4a9d2f","Minutes 5-23 - Complete Xello Learning Style quiz",'''<p>Direct students to ClassLink &gt; Xello &gt; About Me &gt; Learning Style.</p><ul><li>Students complete the 20-question quiz privately and review their resulting style profile.</li><li>Students compare their initial prediction to the result card.</li><li>If any student lacks the Week 2 prerequisite (three saved careers) or has a platform block, immediately provide the printed Method-to-Task Connection sheet with the built-in method chart.</li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 10): Ensure all students have launched the correct quiz.<br>• Lap 2 (Minute 18): Verify students have finished and are reading their strategy profile.</li></ul>''')+
              flow("#1f617a","Minutes 23-45 - Complete Xello Learning styles interactive lesson",'''<p>Direct students to Dashboard &gt; View all lessons &gt; Learning styles.</p><ul><li>Students work through the interactive lesson exploring how visual, auditory, and tactile techniques apply to schoolwork and career tasks.</li><li>Students complete the <strong>Method-to-Task Connection</strong> sheet: identifying one preferred method, one school or IT task where it helps, one potential obstacle, and one concrete study habit to test.</li><li>Model the reflection stem: <em>“I will try tactile modeling when I debug code because building physical diagrams helps me trace data flow.”</em></li><li><strong>Active Monitoring Checkpoints:</strong><br>• Lap 1 (Minute 28): Confirm students are in the lesson, not browsing the dashboard.<br>• Lap 2 (Minute 38): Check that written connection sheets name specific academic or career tasks rather than vague statements.</li></ul>''')+
              flow("#24323d","Minutes 45-50 - Weekly wrap-up and documentation",'''<p>Close out the week and check off student completion standards.</p><ul><li>Check the educator dashboard for quiz and lesson completion; record any students needing supervised catch-up.</li><li>Collect the Method-to-Task Connection sheets.</li><li>Dock and plug in all Chromebooks.</li><li><strong>Safe Trim:</strong> If lesson reading takes longer, allow students to complete the final reflection question as an exit check. Protect both Xello module completions and the connection sheet.</li></ul>''')
            ),
            "MONITOR":"<p>Lap 1: correct Learning Style quiz. Lap 2: quiz complete and the Learning styles lesson open. Lap 3: the connection names a specific method and task rather than a fixed label. If three saved careers are missing or Xello is blocked, move the student to the method chart and connection sheet and record one supervised catch-up list.</p>",
            "SUPPORT":"<p>Show examples for watching/reading, listening/speaking, and hands-on/movement before naming the three styles. Keep the word bank visual, auditory, tactile, method, obstacle, and strategy beside the connection. Allow oral rehearsal or speech-to-text.</p>",
            "FALLBACK":"<p>The built-in method chart and connection sheet are the complete learning-evidence route for the day. Record the access or three-career dependency need and schedule the Grade 7 quiz and lesson separately. Do not delay the Major 1 submission or mark paper work as Xello completion.</p>"}}
        contracts={
          1:{"TOPIC":"Networking Careers","OBJECTIVE":"Students will identify four networking and data career opportunities in the Information Technology cluster and compare transferable skills used in networking and programming work.","TEKS":"d(1)(C), d(4)(B)","DOL":"Completed four-role comparison plus a Venn diagram with two role-specific skills on each side, two shared transferable skills, and one evidence-based explanation."},
          2:{"TOPIC":"User Experience","OBJECTIVE":"Students will identify UX design as an Information Technology career opportunity by analyzing how a website supports or blocks a user's goal and proposing evidence-based improvements.","TEKS":"d(1)(C)","DOL":"UX audit with three strengths, five observable problems, three fixes with user benefits, one redesign sketch, and a supported Rosa mini-case response."},
          3:{"TOPIC":"App Wireframes","OBJECTIVE":"Students will identify app design as an Information Technology career opportunity by planning, testing, and revising a four-screen user flow for a specific audience.","TEKS":"d(1)(C)","DOL":"App plan, four labeled wireframes with clear next actions, written walkthrough feedback, and two starred revisions tied to that feedback."},
          4:{"TOPIC":"Emerging IT Work","OBJECTIVE":"Students will research and evaluate one emerging or rapidly changing Information Technology occupation by distinguishing an exact occupation from a proxy and using dated evidence about work, preparation, pay, and projected growth.","TEKS":"d(1)(C), d(1)(D)","DOL":"Completed emerging-career research and comparison with the BLS occupation, exact/proxy status, dated national pay and growth, preparation, source limit, and changing-work explanation."},
          5:{"TOPIC":"Learning Methods","OBJECTIVE":"Students will analyze the initial results of a learning-style assessment and select one learning method to test in school or career preparation.","TEKS":"d(1)(A)","DOL":"Grade 7 Xello Learning Style quiz and Learning styles lesson completed, plus one learning method and one school or IT task recorded on the connection sheet."}}
        pages={}
        for day in range(1,6):
            st=student_titles[day]; student=await upsert_page(c,st,render(f"wk3-day{day}-student.html",{"COURSE_ID":COURSE_ID,**student_values[day]}),slugify(st))
            tt=f"TEACHER: 1SW Wk3 Day {day} Facilitator Guide"; teacher=await upsert_page(c,tt,render("wk3-teacher.html",{"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student["url"],**contracts[day],**teacher_data[day]}),slugify(tt))
            await upsert_item(c,module_id,teacher,tt); await upsert_item(c,module_id,student,st); pages[day]={"teacher":teacher,"student":student}
        items=await paged(c,f"/courses/{COURSE_ID}/modules/{module_id}/items")
        stale_titles={"STUDENT: 1SW Wk3 Day 5 - Learning Style and IT Connection"}
        for item in items:
            if item.get("type")=="Page" and item.get("title") in stale_titles:
                await api(c,"DELETE",f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}")
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
