"""Build the unpublished 1SW Week 4 teacher/student Canvas module."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
import httpx

BASE="https://learn.irvingisd.net"; COURSE_ID=98060
MODULE_NAME="1SW Wk4: Tech Support Careers and MakeCode"
ROOT=Path(__file__).resolve().parents[2]; TEMPLATES=Path(__file__).parent/"templates"; ASSETS=ROOT/"cce-curriculum/resources/canvas-licensed/1sw/wk4"

def slugify(v): return re.sub(r"[^a-z0-9]+","-",v.lower().replace("&","and")).strip("-")
async def api(c,m,p,**kw):
    r=await c.request(m,f"{BASE}/api/v1{p}",**kw); r.raise_for_status(); return r.json() if r.content else None
async def paged(c,p,params=None):
    out=[]; url=f"{BASE}/api/v1{p}"; q={"per_page":100,**(params or {})}
    while url:
        r=await c.get(url,params=q); r.raise_for_status(); out+=r.json(); url=r.links.get("next",{}).get("url"); q=None
    return out
async def ensure_module(c):
    prior_name="1SW Wk4: Help Desk Heroes - Tech Support Careers and MakeCode"
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
    return folder
async def upload(c,path,folder):
    init=await api(c,"POST",f"/courses/{COURSE_ID}/files",data={"name":path.name,"parent_folder_path":folder,"on_duplicate":"overwrite"})
    r=await c.post(init["upload_url"],data=init["upload_params"],files={"file":(path.name,path.read_bytes(),mimetypes.guess_type(path.name)[0] or "application/octet-stream")},follow_redirects=True); r.raise_for_status(); uploaded=r.json()
    if not uploaded.get("locked"):
        uploaded=await api(c,"PUT",f"/files/{uploaded['id']}",data={"locked":"true"})
    if not uploaded.get("locked"):
        raise ValueError(f"Canvas file did not remain locked: {uploaded.get('display_name', path.name)}")
    return uploaded
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

async def main():
    token=sys.stdin.readline().strip()
    if not token: raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization":f"Bearer {token}"},timeout=120) as c:
        module=await ensure_module(c); module_id=module["id"]
        support_names={
          "CARDS":"wk4-it-support-career-cards.pdf","D1":"wk4-day1-career-interest-check.pdf","ROUTE":"wk4-route-data-guide.pdf","COMPARE":"wk4-education-pathway-comparison.pdf","COMPARE_BI":"wk4-education-pathway-comparison-bilingual.pdf","MODEL":"wk4-education-pathway-comparison-model.pdf","D2":"wk4-day2-route-decision.pdf","SCENARIOS":"wk4-help-desk-scenario-cards.pdf","STARTER":"wk4-makecode-starter-blocks.pdf","SORT":"wk4-troubleshooting-step-sort-cards.pdf","SORT_BI":"wk4-troubleshooting-step-sort-cards-bilingual.pdf","PROGRAM":"wk4-help-desk-program-evidence.pdf","E3":"1sw-wk4-day3-help-desk-simulator-makecode-day-1.pdf","ROLE":"wk4-help-desk-role-play-script.pdf","ROLE_BI":"wk4-help-desk-role-play-script-bilingual.pdf","CLIPBOARD":"clipboard-roster-grid.pdf","D4":"wk4-day4-customer-service-check.pdf","RUBRIC":"wk4-demo-rubric.pdf","CONNECTION":"wk4-day5-xello-skill-connection.pdf"}
        support_folder="course files/CCR Materials/1SW/Wk4"; await ensure_folder(c,support_folder); files={}
        for key,name in support_names.items():
            source_dir=ROOT/"docs/resources/exit-tickets" if name.startswith("1sw-") else ROOT/"docs/resources/worksheets"
            files[key]=await upload(c,source_dir/name,support_folder)
        files["X_INTERESTS"]=await find_file(c,"interests.pdf"); files["X_SKILLS"]=await find_file(c,"about-me.pdf")
        uploads={}; folders={}
        for day in range(1,6):
            folder_path=f"course files/CCR Materials/1SW/Wk4/Day {day} Visuals"; folders[day]=await ensure_folder(c,folder_path); uploads[day]={}
            day_dir=ASSETS/f"day{day}"
            if day_dir.exists():
                for path in sorted(day_dir.glob("*.png")): uploads[day][path.name]=await upload(c,path,folder_path)
        student_values={
          1:{"PROGRAM_IMAGE_ID":uploads[1]["irving-it-programs.png"]["id"],"APP_IMAGE_ID":uploads[1]["it-app-exploration.png"]["id"],"CARDS_FILE_ID":files["CARDS"]["id"],"CHECK_FILE_ID":files["D1"]["id"]},
          2:{"IBC_IMAGE_ID":uploads[2]["ibc-explainer.png"]["id"],"GUIDE_IMAGE_ID":uploads[2]["route-data-guide.png"]["id"],"GUIDE_FILE_ID":files["ROUTE"]["id"],"COMPARE_FILE_ID":files["COMPARE"]["id"],"COMPARE_BI_FILE_ID":files["COMPARE_BI"]["id"],"MODEL_FILE_ID":files["MODEL"]["id"],"DECISION_FILE_ID":files["D2"]["id"]},
          3:{"SCENARIO_IMAGE_ID":uploads[3]["help-desk-scenarios.png"]["id"],"STARTER_IMAGE_ID":uploads[3]["makecode-block-order-guide.png"]["id"],"SCENARIO_FILE_ID":files["SCENARIOS"]["id"],"STARTER_FILE_ID":files["STARTER"]["id"],"SORT_FILE_ID":files["SORT"]["id"],"SORT_BI_FILE_ID":files["SORT_BI"]["id"],"EVIDENCE_FILE_ID":files["PROGRAM"]["id"],"EXIT_FILE_ID":files["E3"]["id"]},
          4:{"ROLE_IMAGE_ID":uploads[4]["role-play-script.png"]["id"],"ROLE_FILE_ID":files["ROLE"]["id"],"ROLE_BI_FILE_ID":files["ROLE_BI"]["id"],"CHECK_FILE_ID":files["D4"]["id"]},
          5:{"RUBRIC_IMAGE_ID":uploads[5]["help-desk-evidence-rubric.png"]["id"],"RUBRIC_FILE_ID":files["RUBRIC"]["id"],"CONNECTION_FILE_ID":files["CONNECTION"]["id"]}}
        student_titles={1:"STUDENT: 1SW Wk4 Day 1 - IT Support Careers and Interests",2:"STUDENT: 1SW Wk4 Day 2 - Compare Education Routes",3:"STUDENT: 1SW Wk4 Day 3 - Build a Help Desk Sequence",4:"STUDENT: 1SW Wk4 Day 4 - Test and Role-Play",5:"STUDENT: 1SW Wk4 Day 5 - Add Skills and Submit Evidence"}
        teacher_data={
          1:{
            "TITLE":"IT Support Careers + Xello Add Interests",
            "SUBTITLE":"50 minutes - TEKS d(1)(C), d(2)(A)",
            "ALERT":"<strong>Required Xello spine:</strong> protect 15 minutes for Add Interests. H&amp;L is optional exploration; the career cards are the equal required route.",
            "PREP":f'<ul><li>For every two students, print one <a href="/courses/{COURSE_ID}/files/{files["CARDS"]["id"]}/preview">IT Support Career Cards</a> packet. Print one <a href="/courses/{COURSE_ID}/files/{files["D1"]["id"]}/preview">career/interest check</a> per student.</li><li>Plan one rostered Chromebook per student for the Xello block. Check rosters and open the licensed <a href="/courses/{COURSE_ID}/files/{files["X_INTERESTS"]["id"]}/preview">My Interests teacher guide</a>.</li><li>Open FYF pp. 36 and 38. Do not print the workbook pages unless an accommodation requires it.</li></ul>',
            "MODEL":"<p>Project one career card and mark the three evidence types in order: underline a <strong>task</strong>, circle <strong>common preparation</strong>, and box a <strong>transferable skill</strong>. Then have every student complete this response before comparing: <em>“A ___ does ___, and common preparation may include ___.”</em></p>",
            "EVIDENCE":"<p>Required completion evidence: at least one Xello interest in the Completion Standards report. The career/interest check is formative or one coherent minor option; platform access itself is not graded.</p>",
            "FLOW":flow("#5a2d91","Technology-help warm-up - 5 minutes","Name the problem, helper, and diagnostic action.")+flow("#4a9d2f","Four-role comparison - 20 minutes","Use one card packet per pair; choose two roles for the individual check.")+flow("#1f617a","Xello Add Interests - 15 minutes","Add or update at least one interest and review how it appears in About Me.")+flow("#e3ad19","Career-interest evidence - 10 minutes","Use a task and preparation fact, then connect one interest."),
            "TRIM":"<p>Move to Xello at minute 25 even if the optional H&amp;L browse has not happened. Move to the individual check at minute 40. Trim the H&amp;L browse and whole-class share first; do not trim the fixed career evidence, Xello time, or written connection. Use the last minute to close Xello tabs and collect checks.</p>",
            "MONITOR":"<p><strong>Lap 1 target:</strong> students mark a task, preparation, and skill rather than three tasks. <strong>Lap 2 target:</strong> preparation language keeps qualifiers such as “common,” “may,” and “some employers.” If several students turn the card into a guarantee, pause and reproject the exact preparation sentence before Xello. Help Desk covers first-line tickets and escalation; Desktop Support emphasizes setup and repair; Systems Administration carries wider system responsibility.</p>",
            "SUPPORT":"<p>Place this word bank beside the cards: <strong>task, preparation, certification, transferable skill</strong>. Students may highlight before writing, rehearse orally, use speech-to-text, or plan bilingually. Point-of-use frame: <em>“My interest in ___ connects to ___ because the worker ___.”</em></p>",
            "FALLBACK":"<p>The career cards replace H&amp;L completely. If Xello is unavailable, record the issue, complete the paper reflection with a current interest, and move required completion to the next Xello catch-up block.</p>"},
          2:{
            "TITLE":"Certification, Associate, and Bachelor Routes",
            "SUBTITLE":"50 minutes - TEKS d(2)(A), d(2)(B)",
            "ALERT":"<strong>Use the dated guide, not open search.</strong> Vendor prices, exam names, and roadmaps drift. BLS figures are national medians, not starting or DFW salaries.",
            "PREP":f'<ul><li>For every two students, print one <a href="/courses/{COURSE_ID}/files/{files["ROUTE"]["id"]}/preview">Route Data Guide</a>. Print one <a href="/courses/{COURSE_ID}/files/{files["COMPARE"]["id"]}/preview">comparison</a> and one <a href="/courses/{COURSE_ID}/files/{files["D2"]["id"]}/preview">route decision</a> per student.</li><li>Project the supplied <a href="/courses/{COURSE_ID}/files/{files["MODEL"]["id"]}/preview">completed model column</a>; print one per pair only for students who need it at the desk.</li><li>Open FYF p. 37. CompTIA exploration is optional and comes only after the required decision.</li></ul>',
            "MODEL":"<p>Use the supplied Computer User Support Specialist column. Point to the labels <strong>common preparation</strong>, <strong>May 2024 U.S. median</strong>, and <strong>tradeoff</strong>. Check all students with: <em>“This route may ___, but ___; employer requirements can vary.”</em> Do not ask the teacher to build another example.</p>",
            "EVIDENCE":"<p>Formative/minor option: complete three-route comparison plus evidence-based route decision. Cost is not required without a current official source.</p>",
            "FLOW":flow("#5a2d91","Certification warm-up - 5 minutes","Distinguish industry evidence from a degree and from a participation award.")+flow("#4a9d2f","IBC and supplied model - 10 minutes","Read median pay, entry preparation, and the meaning of “typical.”")+flow("#1f617a","Three-route comparison - 25 minutes","Complete common preparation, time, 2024 median, and tradeoff.")+flow("#e3ad19","Route decision - 10 minutes","Recommend with a preparation fact, benefit, and tradeoff."),
            "TRIM":"<p>Remove optional CompTIA browsing and shorten the whole-class share to one response. At minute 40, every student moves to the Route Decision. Do not cut the third route, the source labels, or the written recommendation. Collect both pages together at the bell.</p>",
            "MONITOR":"<p><strong>Lap 1 target:</strong> every pay number says May 2024 U.S. median. <strong>Lap 2 target:</strong> preparation uses BLS wording rather than a guarantee. <strong>Lap 3 target:</strong> the tradeoff contains both a benefit and a limit. If a third of the class writes “starting salary” or “DFW,” stop and correct the measure before students finish the recommendation. Key: user support, $60,340; network support, $73,340; software developer, $133,080.</p>",
            "SUPPORT":"<p>Keep the model column visible and color-code preparation, pay, and tradeoff. Point-of-use word bank: <strong>median, preparation, benefit, tradeoff, requirement</strong>. Complete frame: <em>“The student should investigate ___ because ___. A benefit is ___. A tradeoff is ___.”</em></p>",
            "FALLBACK":"<p>The dated guide is the normal no-web route. If BLS or CompTIA is blocked, no evidence changes. An absent student completes the same guide, comparison, and decision.</p>"},
          3:{
            "TITLE":"Help Desk Simulator - Build and Save",
            "SUBTITLE":"50 minutes - TEKS d(4)(B)",
            "ALERT":"<strong>Hardware is optional; durable evidence is required.</strong> Use MakeCode hardware, simulator, or paper trace. Update firmware only when a connection failure and official troubleshooting guidance point to it.",
            "PREP":f'<ul><li>Make teams of four. Per team, prepare one rostered Chromebook, one <a href="/courses/{COURSE_ID}/files/{files["SCENARIOS"]["id"]}/preview">scenario card</a>, one matching <a href="/courses/{COURSE_ID}/files/{files["SORT"]["id"]}/preview">three-card sort</a>, one <a href="/courses/{COURSE_ID}/files/{files["STARTER"]["id"]}/preview">block-order guide</a>, and one <a href="/courses/{COURSE_ID}/files/{files["PROGRAM"]["id"]}/preview">Program Evidence</a>. Print one <a href="/courses/{COURSE_ID}/files/{files["E3"]["id"]}/preview">Day 3 exit check</a> per student.</li><li>Assign Driver, Navigator, Tester, and Evidence Recorder. In a team of three, the Tester also records evidence. Use one micro:bit and one data-capable cable per team only when taking the hardware route.</li><li>Test makecode.microbit.org once on a student-filtered Chromebook. Project the supplied block-order guide and printer trace below; no teacher-created MakeCode project is required.</li><li>Choose one backup for the class: screenshot, share link, downloaded .hex, or signed paper trace. Label a turn-in location for paper evidence and hardware.</li></ul>',
            "MODEL":'<div style="border:1px solid #bad4df;border-radius:8px;padding:12px 16px;background:#f2f8fb"><p style="margin-top:0"><strong>Ready-to-project printer model</strong></p><ol><li>Step 1: Check power cable.</li><li>Step 2: Check paper tray.</li><li>Step 3: Restart printer.</li></ol><p><strong>Dry trace:</strong> Start step = 1; A shows 1, then 2, then 3, then 1; B shows FIXED.</p></div><p>Checks for every team: <em>“We put ___ first because it is ___.”</em> After the variable chunk, ask, “What value is step before the first press?” After Button A, every Tester traces A/A/A/A/B before the team continues.</p>',
            "EVIDENCE":"<p><strong>Minor 3 evidence begins:</strong> Program Evidence supplies Logical Sequence and Program Logic/Testing, 8 of 16 points. The Day 3 branching exit is formative.</p>",
            "FLOW":flow("#5a2d91","Troubleshooting order - 5 minutes","Choose the lowest-risk, fastest check first.")+flow("#4a9d2f","Team roles and naming - 10 minutes","One device and one evidence set per four students; exact project name.")+flow("#1f617a","Build or trace - 25 minutes","On start, three Button A branches, wrap to Step 1, Button B FIXED.")+flow("#e3ad19","Test, back up, exit, clean up - 10 minutes","Run A/A/A/A/B, record the backup, complete the exit, and return hardware."),
            "TRIM":"<p>At minute 35, a team without working Button A switches to the paper trace from its current progress; this is an equal route, not a penalty. At minute 40, all building stops. Use minutes 40-44 to test, 44-47 to save or sign the paper trace, 47-49 for the exit check, and 49-50 to close tabs, return the board and cable, and place evidence in the labeled turn-in location.</p>",
            "MONITOR":"<p><strong>Lap 1 target:</strong> the chosen first step is fast and low-risk. <strong>Lap 2 target:</strong> step starts at 1 and Button A shows the current branch before increasing the variable. <strong>Lap 3 target:</strong> A/A/A/A returns to Step 1 and B independently shows FIXED. If two teams make the same skip-to-Step-2 error, pause and point to block 11 on the supplied guide. The Wi-Fi scenario never restarts shared equipment when the evidence points to one device.</p>",
            "SUPPORT":"<p>Place this word bank beside the projected model: <strong>sequence, variable, branch, test, backup</strong>. Navigator reads one block at a time; Driver places it; Tester predicts and runs the result; Evidence Recorder writes what happened. Rotate Driver and Navigator after the Button A branches. Complete frame: <em>“Our first test showed ___. We changed ___ so ___.”</em> Allow screen magnification, Spanish step text, and dictated evidence.</p>",
            "FALLBACK":"<p>No board: simulator. Site blocked: arrange the cards, trace the block-order guide, and have another team initial A/A/A/A/B. Saved project missing: use the named backup or paper trace rather than rebuilding. Absent: use the paper route or join the assigned team’s durable evidence on return.</p>"},
          4:{
            "TITLE":"Swap Test + Customer Service Role-Play",
            "SUBTITLE":"50 minutes - TEKS d(4)(B)",
            "ALERT":"<strong>Finish core behavior before enhancements.</strong> Today must document one partner-test finding and one revision. Spoken performance has an equal written-chat route.",
            "PREP":f'<ul><li>Keep the Day 3 teams. Per team, set out one saved project or paper trace and one Program Evidence sheet. Pair each team with one neighboring test team.</li><li>For role-play, print one <a href="/courses/{COURSE_ID}/files/{files["ROLE"]["id"]}/preview">script</a> per pair and one <a href="/courses/{COURSE_ID}/files/{files["D4"]["id"]}/preview">Customer Service Check</a> per student. Offer the <a href="/courses/{COURSE_ID}/files/{files["ROLE_BI"]["id"]}/preview">bilingual script</a> at the same table, not after a student gets stuck.</li><li>Print one <a href="/courses/{COURSE_ID}/files/{files["CLIPBOARD"]["id"]}/preview">monitoring roster</a> for the teacher. Post a visible timer and the four customer-service rules.</li></ul>',
            "MODEL":"<p>Use the first three turns of the supplied script. Model one response that acknowledges the problem and asks one plain-language question: <em>“I understand this is frustrating. Let us check one thing at a time. What do you see on the screen?”</em> Every pair identifies the acknowledgment and the one diagnostic question before practice begins.</p>",
            "EVIDENCE":"<p>Minor 3 evidence adds the documented bug or confusion and revision. Individual role-play observation and the customer-service check are formative.</p>",
            "FLOW":flow("#5a2d91","Customer frustration warm-up - 5 minutes","Separate the technical problem from the communication problem.")+flow("#4a9d2f","Reopen and finish core - 15 minutes","Recover within three minutes; otherwise use the backup or paper trace.")+flow("#1f617a","Swap, test, revise - 10 minutes","Silent test, one clear part, one confusion, one documented change.")+flow("#e3ad19","Role-play and check - 20 minutes","One or two short rounds, then the individual customer-service check."),
            "TRIM":"<p>Cap file recovery at three minutes. If time is short, run one role-play round instead of two and remove the whole-class debrief. Do not cut the partner test, documented revision, or individual Customer Service Check. Begin the check by minute 40; use the final two minutes to collect scripts, checks, and team evidence and return any hardware.</p>",
            "MONITOR":"<p><strong>Lap 1 target:</strong> each test team records one clear part and one confusion. <strong>Lap 2 target:</strong> each build team documents a specific revision. <strong>Lap 3 target:</strong> each student acknowledges, uses plain language, gives one step, and explains what happens next. If several students skip acknowledgment, pause and replay only the supplied opening. Answer key: C. A corrects emotion; B assumes a cause; D abandons the user.</p>",
            "SUPPORT":"<p>Point-of-use word bank: <strong>acknowledge, diagnose, step, explain, escalate</strong>. Feedback frames: <em>“The order was clear because ___.”</em> and <em>“Change ___ to ___ so the user can ___.”</em> Customer frame: <em>“I understand ___. Let us try ___. If that does not work, ___.”</em> Use bilingual support, private or low-volume practice, speech-to-text, or a written chat route.</p>",
            "FALLBACK":"<p>Paper teams swap and trace the same sequence. If the saved file is missing, recover the backup or trace it; do not rebuild from memory. Absent students complete a written support exchange and revise from a supplied test result.</p>"},
          5:{
            "TITLE":"Lightning Demos + Xello Add Skills",
            "SUBTITLE":"50 minutes - TEKS d(1)(C), d(2)(A), d(4)(B)",
            "ALERT":"<strong>Required Xello spine:</strong> protect 20 minutes for Add Skills. H&amp;L favorites are optional. Return Minor 3 scores privately; do not post team totals.",
            "PREP":f'<ul><li>Per team, set out one Program Evidence sheet and the saved project or paper trace. Print one <a href="/courses/{COURSE_ID}/files/{files["CONNECTION"]["id"]}/preview">individual skill connection</a> per student. Project the <a href="/courses/{COURSE_ID}/files/{files["RUBRIC"]["id"]}/preview">16-point evidence rubric</a>; print one per team only if students need a desk copy.</li><li>Plan one rostered Chromebook per student for Xello. Check rosters and open the licensed <a href="/courses/{COURSE_ID}/files/{files["X_SKILLS"]["id"]}/preview">About Me teacher guide</a> at Add or Update Skill.</li><li>Order teams before class. Use one minute per team plus one transition minute after every three teams. If there are more than eight teams, prepare two gallery lanes or the written or private route before class.</li></ul>',
            "MODEL":"<p>Project this 45-second structure: <strong>scenario; A/A/A/A/B result; why Step 1 comes first; support career and common preparation; transferable skill.</strong> Then model one complete skill response: <em>“I used problem-solving when I traced the skipped step. A nurse also uses problem-solving to check information before deciding what happens next.”</em></p>",
            "EVIDENCE":"<p><strong>Minor 3:</strong> Program Evidence plus individual Xello Skill and Help Desk Connection, 16 points. Required completion evidence: at least one Xello skill in the report. The lightning demo is formative communication practice.</p>",
            "FLOW":flow("#5a2d91","Lightning demos - 20 minutes","One minute per team; use gallery, private, or written routes when the roster requires them.")+flow("#4a9d2f","Xello Add Skills - 20 minutes","Add or update at least one skill and one real example.")+flow("#1f617a","Individual connection and submission - 10 minutes","Connect the skill to IT and another career, then submit team and individual evidence."),
            "TRIM":"<p>Stop demos at minute 20. Move unfinished teams to the written or private route rather than taking Xello time. H&amp;L favorites and public share-outs are the first cuts. At minute 40, move every student to the individual connection. Use minutes 48-50 to close Xello, verify the named turn-in items, and collect team evidence.</p>",
            "MONITOR":"<p><strong>Demo target:</strong> each team shows the logic and first-step reason; do not live-score polish. <strong>Xello target:</strong> the skill includes a real example, not only a label. <strong>Submission target:</strong> each team has one Program Evidence sheet and each student has one connection sheet. If examples are vague, pause with the supplied complete response before students submit. Students may say IT support is not a fit and still earn full evidence credit.</p>",
            "SUPPORT":"<p>Point-of-use word bank: <strong>skill, evidence, transfer, preparation, example</strong>. Complete frame: <em>“I used ___ when I ___. An IT support worker uses it to ___. A ___ also uses it to ___.”</em> Allow one student to operate while another speaks, a written 45-second script, a private explanation, bilingual planning, and speech-to-text.</p>",
            "FALLBACK":"<p>Program failure uses the paper trace. Xello failure is recorded and moves to catch-up while the student completes the reflection with a known skill. An absent student submits a written lightning-demo script or explains it privately.</p>"}}
        contracts={
          1:{"TOPIC":"IT Support Careers","OBJECTIVE":"Students will identify IT support career opportunities and describe common preparation requirements using district HQIM and fixed career evidence.","TEKS":"d(1)(C), d(2)(A)","DOL":"Two-career evidence comparison, one interest-to-task connection, and at least one added or updated Xello interest."},
          2:{"TOPIC":"Education Routes","OBJECTIVE":"Students will research, describe, and evaluate education and training options for IT careers using common preparation, time, pay, and tradeoff evidence from a dated source guide.","TEKS":"d(2)(A), d(2)(B)","DOL":"Three-route comparison and recommendation using an accurate preparation fact, a benefit, and a tradeoff."},
          3:{"TOPIC":"Troubleshooting Logic","OBJECTIVE":"Students will identify problem-solving and communication skills that transfer among careers by building, testing, and explaining a three-step help desk sequence.","TEKS":"d(4)(B)","DOL":"Help Desk Program Evidence with an ordered sequence, Button A/B logic, recorded test, durable backup, and transferable-skill connection."},
          4:{"TOPIC":"Customer Service","OBJECTIVE":"Students will identify communication and problem-solving skills that transfer among careers by testing a support sequence, revising it from feedback, and responding to a frustrated user.","TEKS":"d(4)(B)","DOL":"One partner-test finding, one documented revision, and a customer-service response that follows four support rules and transfers the skill to another career."},
          5:{"TOPIC":"Career Skills","OBJECTIVE":"Students will identify an IT support career and common preparation and explain how one practiced skill transfers among careers using program evidence and their Xello profile.","TEKS":"d(1)(C), d(2)(A), d(4)(B)","DOL":"Team Help Desk Program Evidence, individual Xello Skill and Help Desk Connection, and at least one added or updated Xello skill."}}
        pages={}
        for day in range(1,6):
            st=student_titles[day]; student=await upsert_page(c,st,render(f"wk4-day{day}-student.html",{"COURSE_ID":COURSE_ID,**student_values[day]}),slugify(st))
            tt=f"TEACHER: 1SW Wk4 Day {day} Facilitator Guide"; teacher=await upsert_page(c,tt,render("wk4-teacher.html",{"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student["url"],**contracts[day],**teacher_data[day]}),slugify(tt))
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

if __name__ == "__main__":
    asyncio.run(main())
