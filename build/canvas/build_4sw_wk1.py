"""Build the unpublished 4SW Week 1 Mid-Year Career Blueprint Canvas module."""

import asyncio
import json
import mimetypes
import re
import sys
from pathlib import Path

import httpx

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
MODULE_NAME = "4SW Wk1: Build Your Mid-Year Career Blueprint"
ANNOTATION_TITLE = "PRACTICE: Career Iceberg Annotation"
BLUEPRINT_TITLE = "DRAFT: Mid-Year Career Blueprint"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/4sw/wk1"


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


async def api(client, method, path, **kwargs):
    response = await client.request(method, f"{BASE}/api/v1{path}", **kwargs)
    response.raise_for_status()
    return response.json() if response.content else None


async def paged(client, path, params=None):
    output, url, query = [], f"{BASE}/api/v1{path}", {"per_page": 100, **(params or {})}
    while url:
        response = await client.get(url, params=query)
        response.raise_for_status()
        output += response.json()
        url, query = response.links.get("next", {}).get("url"), None
    return output


async def ensure_module(client):
    modules = await paged(client, f"/courses/{COURSE_ID}/modules")
    found = next((entry for entry in modules if entry["name"] == MODULE_NAME), None)
    if found:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data={"module[published]": "false"})
    return await api(client, "POST", f"/courses/{COURSE_ID}/modules", data={"module[name]": MODULE_NAME, "module[published]": "false"})


async def ensure_folder(client, path):
    current, folder = "", None
    for name in path.split("/")[1:]:
        target = f"{current}/{name}".strip("/")
        encoded = httpx.URL("/" + target).raw_path.decode("ascii").lstrip("/")
        response = await client.get(f"{BASE}/api/v1/courses/{COURSE_ID}/folders/by_path/{encoded}")
        if response.status_code == 200 and response.json():
            folder = response.json()[-1]
        else:
            folder = await api(client, "POST", f"/courses/{COURSE_ID}/folders", data={"name": name, "parent_folder_path": "course files" + (f"/{current}" if current else ""), "locked": "true"})
        current = target
    if folder and not folder.get("locked"):
        folder = await api(client, "PUT", f"/folders/{folder['id']}", data={"locked": "true"})
    return folder


async def upload(client, path, folder_path):
    start = await api(client, "POST", f"/courses/{COURSE_ID}/files", data={"name": path.name, "parent_folder_path": folder_path, "on_duplicate": "overwrite"})
    response = await client.post(start["upload_url"], data=start["upload_params"], files={"file": (path.name, path.read_bytes(), mimetypes.guess_type(path.name)[0] or "application/octet-stream")}, follow_redirects=True)
    response.raise_for_status()
    uploaded = response.json()
    return await api(client, "PUT", f"/files/{uploaded['id']}", data={"locked": "false"})


def render(template, values):
    text = (TEMPLATES / template).read_text()
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    unresolved = sorted(set(re.findall(r"\{\{[^}]+\}\}", text)))
    if unresolved:
        raise ValueError(f"Unresolved values in {template}: {unresolved}")
    return text


async def upsert_page(client, title, body):
    url = slugify(title)
    data = {"wiki_page[title]": title, "wiki_page[body]": body, "wiki_page[published]": "false", "wiki_page[editing_roles]": "teachers"}
    response = await client.get(f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{url}")
    if response.status_code == 200:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/pages/{url}", data=data)
    if response.status_code != 404:
        response.raise_for_status()
    return await api(client, "POST", f"/courses/{COURSE_ID}/pages", data=data)


async def upsert_assignment(client, title, description, submission_types, attachment_id=None):
    assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
    found = next((entry for entry in assignments if entry.get("name") == title), None)
    data = {
        "assignment[name]": title,
        "assignment[description]": description,
        "assignment[submission_types][]": submission_types,
        "assignment[grading_type]": "not_graded",
        "assignment[points_possible]": "0",
        "assignment[published]": "false",
    }
    if attachment_id:
        data["assignment[annotatable_attachment_id]"] = str(attachment_id)
    endpoint = f"/courses/{COURSE_ID}/assignments/{found['id']}" if found else f"/courses/{COURSE_ID}/assignments"
    return await api(client, "PUT" if found else "POST", endpoint, data=data)


async def upsert_item(client, module_id, kind, key, title):
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    found = next((item for item in items if (kind == "SubHeader" and item.get("title") == title) or (kind == "Page" and item.get("page_url") == key) or (kind == "Assignment" and item.get("content_id") == key)), None)
    if found:
        return await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module_id}/items/{found['id']}", data={"module_item[title]": title})
    data = {"module_item[type]": kind, "module_item[title]": title}
    if kind == "Page":
        data["module_item[page_url]"] = key
    elif kind == "Assignment":
        data["module_item[content_id]"] = key
    return await api(client, "POST", f"/courses/{COURSE_ID}/modules/{module_id}/items", data=data)


def file_link(file_id, label):
    return f'<a href="/courses/{COURSE_ID}/files/{file_id}/preview" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">{label}</a>'


def image_tag(file_id, alt):
    return f'<img src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" style="display:block;width:100%;max-width:700px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'


def step(number, title, body):
    return f'<h3 style="color:#5a2d91;border-bottom:3px solid #d9c9ed">{number}. {title}</h3>{body}'


def flow(color, title, text):
    return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=120) as client:
        module = await ensure_module(client)
        support = "course files/CCR Materials/4SW/Wk1"
        support_folder = await ensure_folder(client, support)
        names = {
            "AUDIT": "4sw-wk1-midyear-profile-audit.pdf",
            "ICEBERG": "4sw-wk1-career-iceberg-and-goal.pdf",
            "DEEP": "4sw-wk1-career-deep-dive.pdf",
            "PATHWAY": "4sw-wk1-pathway-and-ctso-decision.pdf",
            "BLUEPRINT": "4sw-wk1-midyear-career-blueprint.pdf",
            "RUBRIC": "4sw-wk1-midyear-blueprint-rubric.pdf",
        }
        files = {key: await upload(client, ROOT / "docs/resources/worksheets" / name, support) for key, name in names.items()}

        visuals, folders = {}, {}
        selected = {
            1: ["fyf-rung-1-who-you-are.jpg"],
            2: ["fyf-career-iceberg-model.jpg", "fyf-rung-2-career-goal.jpg", "fyf-rung-2-career-snapshot.jpg"],
            3: ["fyf-rung-3-career-deep-dive.jpg", "fyf-rung-3-skills-check.jpg"],
            5: ["fyf-career-thinker-and-doer.jpg"],
        }
        for day, image_names in selected.items():
            folder_path = f"course files/CCR Materials/4SW/Wk1/Day {day} Visuals"
            folders[day], visuals[day] = await ensure_folder(client, folder_path), {}
            for name in image_names:
                visuals[day][name] = await upload(client, ASSETS / f"day{day}" / name, folder_path)

        annotation = await upsert_assignment(client, ANNOTATION_TITLE, "<p>Label the Career Iceberg directly in Canvas, upload the completed file, type a labeled response, or use the paper copy. Art quality is not scored.</p>", ["student_annotation", "online_upload", "online_text_entry"], files["ICEBERG"]["id"])
        blueprint = await upsert_assignment(client, BLUEPRINT_TITLE, "<p>Submit the private Mid-Year Career Blueprint by file upload, text entry, or media recording. The 16-point rubric is visible in the student packet. This draft remains unpublished and ungraded until the Major assignment group and 40/60 weighting are verified.</p>", ["online_upload", "online_text_entry", "media_recording"])
        annotation_url = f"/courses/{COURSE_ID}/assignments/{annotation['id']}"
        blueprint_url = f"/courses/{COURSE_ID}/assignments/{blueprint['id']}"

        media = {
            1: image_tag(visuals[1]["fyf-rung-1-who-you-are.jpg"]["id"], "Find Your Future Rung 1 prompts for interests, strengths, skills, work values, and personality evidence"),
            2: image_tag(visuals[2]["fyf-career-iceberg-model.jpg"]["id"], "Find Your Future Career Iceberg worked example showing visible results above water and hidden effort below") + image_tag(visuals[2]["fyf-rung-2-career-goal.jpg"]["id"], "Find Your Future Rung 2 career goal prompts") + image_tag(visuals[2]["fyf-rung-2-career-snapshot.jpg"]["id"], "Find Your Future Rung 2 career snapshot prompts"),
            3: image_tag(visuals[3]["fyf-rung-3-career-deep-dive.jpg"]["id"], "Find Your Future Rung 3 education, salary, and outlook prompts") + image_tag(visuals[3]["fyf-rung-3-skills-check.jpg"]["id"], "Find Your Future Rung 3 career skills check"),
            4: "",
            5: image_tag(visuals[5]["fyf-career-thinker-and-doer.jpg"]["id"], "Find Your Future Career Thinker and Doer reflection and career community prompts"),
        }

        student = {
            1: {"TITLE":"Mid-Year Profile Audit","PURPOSE":"Use current evidence to examine how your career thinking has changed or stayed the same.","TODAY":"<ul><li>review one earlier result or idea;</li><li>collect three current pieces of evidence;</li><li>defend one conclusion.</li></ul>","READY":f'<p>Open {file_link(files["AUDIT"]["id"], "the Mid-Year Profile Audit")}. You may also use a notebook, H&amp;L, Xello, or an earlier portfolio item. A private screenshot is not required.</p>',"STEPS":step(1,"Choose the earlier result","<p>Record one earlier assessment result, work value, Building Block, career idea, or clearly labeled current baseline.</p>")+step(2,"Collect three pieces of evidence","<p>Use specific activities, choices, feedback, or profile results from different sources.</p>")+step(3,"Analyze the pattern","<p>Decide whether the evidence supports, complicates, or changes the earlier result. Explain why.</p>"),"EXIT":"<p>What is one conclusion you can defend now, and what evidence supports it?</p>","DONE":"<ul><li>one baseline;</li><li>three specific pieces of evidence;</li><li>one pattern;</li><li>one defensible conclusion.</li></ul>","SUPPORT":"<p>evidence = evidencia · earlier = anterior · current = actual · pattern = patrón. Use the sentence frames and speak your explanation before writing.</p>","FALLBACK":"<p>The PDF is the complete independent route. If earlier evidence is missing, use today's self-evidence inventory and label it as your baseline.</p>"},
            2: {"TITLE":"Career Iceberg and Goal","PURPOSE":"Show the visible and hidden work behind one career, then decide whether it remains a useful direction.","TODAY":"<ul><li>study an iceberg model;</li><li>label one career iceberg;</li><li>write a working career goal.</li></ul>","READY":f'<p>Open {file_link(files["ICEBERG"]["id"], "the Career Iceberg and Goal sheet")} or <a href="{annotation_url}">open the Canvas annotation activity</a>. Paper, typed labels, drawing, and file upload are equal routes.</p>',"STEPS":step(1,"Name the visible work","<p>Add at least three things people can see above the waterline.</p>")+step(2,"Name the hidden work","<p>Add at least eight specific skills, tools, training steps, responsibilities, challenges, or supports below the waterline.</p>")+step(3,"Make a working decision","<p>Use two Day 1 facts, one hidden requirement, and one research question. This is a current direction, not a permanent promise.</p>"),"EXIT":"<p>Name one hidden requirement that changed how you see the career. Does it strengthen, weaken, or complicate your interest?</p>","DONE":"<ul><li>three visible items;</li><li>eight hidden items across the labeled categories;</li><li>two self-evidence connections;</li><li>one research question.</li></ul>","SUPPORT":"<p>visible = visible · hidden = oculto · training = capacitación · responsibility = responsabilidad. Drawing skill is not scored.</p>","FALLBACK":"<p>Download the PDF, type a labeled list, record an audio response, or use paper. The embedded images explain the full task for an absent student.</p>"},
            3: {"TITLE":"Career Deep Dive","PURPOSE":"Research one career without losing the place, year, and meaning attached to a number.","TODAY":"<ul><li>identify daily work and preparation;</li><li>record pay and outlook accurately;</li><li>choose one realistic first step.</li></ul>","READY":f'<p>Open {file_link(files["DEEP"]["id"], "the Career Deep Dive")}. Use a current Xello result, BLS, an official training provider, or the dated career card your teacher supplies.</p>',"STEPS":step(1,"Name the work","<p>Record two common tasks and one work condition.</p>")+step(2,"Document preparation","<p>Record common education or training and any license or certification the source names.</p>")+step(3,"Label every number","<p>Keep place, year, and measure with salary and outlook. Median is not starting pay; national is not DFW.</p>")+step(4,"Plan from the evidence","<p>Name the requirement that needs the most planning and one first step.</p>"),"EXIT":"<p>Which requirement will take the most planning for you? Cite the evidence and name one first step.</p>","DONE":"<ul><li>tasks and condition;</li><li>preparation evidence;</li><li>fully labeled salary and outlook;</li><li>source title or URL;</li><li>one first step.</li></ul>","SUPPORT":"<p>median = mediana · outlook = perspectiva · source = fuente · measure = medida. Complete one source field at a time.</p>","FALLBACK":"<p>Use the teacher's dated career card if a site or login does not work. Do not invent or relabel a number.</p>"},
            4: {"TITLE":"Irving Pathway and CTSO Decision","PURPOSE":"Compare current local options and explain how one student organization could help you prepare.","TODAY":"<ul><li>read current Irving ISD program information;</li><li>compare and rank pathways;</li><li>connect one CTSO benefit.</li></ul>","READY":f'<p>Open {file_link(files["PATHWAY"]["id"], "the Pathway and CTSO Decision sheet")}. Use the current district CTE hub and course-description page your teacher posts.</p>',"STEPS":step(1,"Record exact current names","<p>Capture the pathway or program, location when verified, one connection, and one course, requirement, or question.</p>")+step(2,"Compare before ranking","<p>Use fit and evidence, not popularity. It is acceptable to write “not yet confirmed.”</p>")+step(3,"Add a CTSO benefit","<p>Select a plausible organization and explain one specific preparation benefit. Confirm local chapter availability before claiming it exists.</p>"),"EXIT":"<p>Name your current first choice, one verified fact, one unanswered question, and one way a CTSO could help.</p>","DONE":"<ul><li>three current options, or two with support;</li><li>sources and access date;</li><li>evidence-based ranking;</li><li>one CTSO benefit;</li><li>one verification question.</li></ul>","SUPPORT":"<p>pathway = trayectoria · requirement = requisito · verified = verificado · organization = organización. Read one program card at a time.</p>","FALLBACK":"<p>If the district site is unavailable, use the dated pathway cards and mark details that need later verification.</p>"},
            5: {"TITLE":"Mid-Year Career Blueprint","PURPOSE":"Turn the week's evidence into a current plan, a backup direction, and one next action.","TODAY":"<ul><li>gather Days 1-4 evidence;</li><li>build a private Blueprint;</li><li>self-score and revise.</li></ul>","READY":f'<p>Open {file_link(files["BLUEPRINT"]["id"], "the Mid-Year Career Blueprint")} and {file_link(files["RUBRIC"]["id"], "the 16-point rubric")}.</p>',"STEPS":step(1,"Gather","<p>Bring forward self-evidence, the iceberg insight, career preparation and data, and one verified pathway fact.</p>")+step(2,"Build","<p>Name a current direction, backup, next six-week action, and question for a trusted adult or professional.</p>")+step(3,"Self-score and revise","<p>Check all four criteria. Revise one weak area before you submit.</p>")+step(4,"Submit privately",f'<p><a href="{blueprint_url}">Open the private Blueprint assignment</a>, or hand in the paper copy.</p>'),"EXIT":"<p>My plan is stronger now because I used evidence from ____ to change or confirm ____.</p>","DONE":"<ul><li>all seven Blueprint jobs;</li><li>source labels retained;</li><li>specific backup and next action;</li><li>private rubric check;</li><li>one visible revision.</li></ul>","SUPPORT":"<p>blueprint = plan · backup = plan alternativo · next action = próxima acción. Text, speech-to-text, and media recording answer the same sentence jobs.</p>","FALLBACK":"<p>Use the fallback evidence box if an earlier artifact is missing. Canvas failure does not change the task or score; submit paper or upload later.</p>"},
        }

        teacher = {
            1: {"TITLE":"Mid-Year Profile Audit","SUBTITLE":"50 minutes · TEKS d(1)(A)","ALERT":"<strong>Do not require a retake.</strong> Students analyze earlier evidence against current evidence; a private screenshot is never required.","PREP":f'<ul><li>Post {file_link(files["AUDIT"]["id"], "the audit packet")}.</li><li>Make earlier portfolio evidence available when practical.</li><li>Keep the no-prior-evidence baseline route ready.</li></ul>',"EVIDENCE":"<p>One earlier result or baseline, three specific current facts, one pattern, and one defensible conclusion. Formative.</p>","FLOW":flow("#5a2d91","Warm-up · 5","Name one changed interest and its cause.")+flow("#4a9d2f","Evidence model · 10","Move from labels to specific evidence.")+flow("#1f617a","Audit · 20","Baseline, three facts, pattern, conclusion.")+flow("#e3ad19","Discuss · 10","Structured partner or private written route.")+flow("#1f617a","Exit · 5","Defend one conclusion."),"MONITOR":"<p>Full evidence names a choice, activity, task, feedback point, or result. “I like technology” is too broad. Do not score whether the student's interests changed in the direction an adult expected.</p>","RESOURCES":"<p>Licensed FYF Rung 1 is embedded. H&amp;L, Xello, notebooks, and earlier work are optional evidence sources.</p>","SUPPORT":"<p>Offer the evidence bank, sentence frames, oral rehearsal, and speech-to-text. The PDF gives multiple lines for every explanation.</p>","FALLBACK":"<p>A new or absent student uses the current baseline inventory. No platform history is required.</p>"},
            2: {"TITLE":"Career Iceberg and Goal","SUBTITLE":"50 minutes · TEKS d(1)(A), d(8)(A)","ALERT":"<strong>Annotation is one route.</strong> File, text, media, and paper routes produce equal evidence; art polish is not graded.","PREP":f'<ul><li>Post {file_link(files["ICEBERG"]["id"], "the iceberg packet")} and open the unpublished annotation activity.</li><li>Project the licensed model.</li><li>Have paper copies ready.</li></ul>',"EVIDENCE":"<p>Three visible items, eight hidden items across categories, two self-evidence links, one requirement, and one research question. Formative.</p>","FLOW":flow("#5a2d91","Warm-up · 5","What work does success hide?")+flow("#4a9d2f","Model · 10","Visible versus hidden evidence.")+flow("#1f617a","Build · 18","Label the iceberg.")+flow("#e3ad19","Goal · 12","Use Day 1 evidence and one question.")+flow("#1f617a","Exit · 5","Explain one changed perception."),"MONITOR":"<p>At minute 10 of building, require at least one item in skill, tool, training, responsibility, challenge, and support. Accept uncertainty. Do not force a permanent career commitment.</p>","RESOURCES":"<p>Licensed FYF Career Iceberg and Rung 2 pages are embedded. Canvas DocViewer annotation is a purposeful practice interaction.</p>","SUPPORT":"<p>Use labeled underwater zones and allow typed labels or oral description. The packet reserves a full page for the iceberg.</p>","FALLBACK":"<p>If annotation fails, use upload, text, media, or paper. An absent student has the full model and directions in the Student Guide.</p>"},
            3: {"TITLE":"Career Deep Dive","SUBTITLE":"50 minutes · TEKS d(8)(B)","ALERT":"<strong>Keep the label with the number.</strong> National median, DFW range, and starting salary are different measures.","PREP":f'<ul><li>Post {file_link(files["DEEP"]["id"], "the Deep Dive")}.</li><li>Test sources and prepare one dated career card.</li><li>Model place, year, and measure.</li></ul>',"EVIDENCE":"<p>Tasks, work condition, preparation, license/certification when applicable, fully labeled salary and outlook, source, and first step. Formative.</p>","FLOW":flow("#5a2d91","Warm-up · 5","Label place, year, measure.")+flow("#4a9d2f","Source model · 10","Read one evidence card.")+flow("#1f617a","Deep dive · 25","Research and record.")+flow("#e3ad19","Evidence check · 5","Repair one incomplete claim.")+flow("#1f617a","Exit · 5","Plan from one requirement."),"MONITOR":"<p>Reject unlabeled numbers, not student preferences. Salary research does not satisfy personal-budget TEKS. A full response distinguishes a common route from a universal requirement.</p>","RESOURCES":'<p><a href="https://www.bls.gov/ooh/">BLS Occupational Outlook Handbook</a> for national evidence. Xello may add localized evidence when its geography, date, and measure remain visible.</p>',"SUPPORT":"<p>Read one source field at a time, pre-highlight labels, and offer the fixed card. The packet provides separate multi-line areas for interpretation.</p>","FALLBACK":"<p>The fixed career card is the complete no-login route. H&amp;L is supplemental.</p>"},
            4: {"TITLE":"Irving Pathway and CTSO Decision","SUBTITLE":"50 minutes · TEKS d(3)(F), d(8)(A)","ALERT":"<strong>Verify local claims.</strong> TEA recognition of a CTSO does not prove a chapter exists at a particular campus.","PREP":f'<ul><li>Post {file_link(files["PATHWAY"]["id"], "the comparison packet")}.</li><li>Open the current Irving CTE hub and 2026-27 course descriptions.</li><li>Prepare dated pathway cards as fallback.</li></ul>',"EVIDENCE":"<p>Three current options, source labels, evidence-based ranking, one CTSO benefit, and one verification question. Formative.</p>","FLOW":flow("#5a2d91","Warm-up · 5","Facts and people needed before choosing.")+flow("#4a9d2f","Current source route · 12","Program names, locations, course information.")+flow("#1f617a","Compare · 18","Three options using fit and evidence.")+flow("#e3ad19","CTSO connection · 10","One specific preparation benefit.")+flow("#1f617a","Exit · 5","Choice, fact, question, benefit."),"MONITOR":"<p>Accept “not yet confirmed.” Do not collapse a program, certification, course, and career into one label. Full d(3)(F) evidence explains a preparation benefit, not merely the CTSO name.</p>","RESOURCES":'<p><a href="https://www.irvingisd.net/departments-services/career-and-technical-education-cte/high-school-cte">Irving ISD High School CTE</a> · <a href="https://www.irvingisd.net/departments-services/curriculum-and-instruction/middle-school-and-high-school-course-descriptions">2026-27 course descriptions</a> · <a href="https://tea.texas.gov/student-readiness-and-high-school/college-career-and-military-prep/career-and-technical-education/career-and-technical-education-student-organizations">TEA CTSOs</a></p>',"SUPPORT":"<p>Compare two options with all evidence fields when documented support calls for reduced quantity. Use source cards with text and icons, not color alone.</p>","FALLBACK":"<p>If live sites fail, use dated captured cards and mark facts for later verification. No vendor unit is load-bearing.</p>"},
            5: {"TITLE":"Mid-Year Career Blueprint","SUBTITLE":"50 minutes · TEKS d(1)(A), d(8)(A), d(8)(B)","ALERT":"<strong>Recommended 16-point major, not yet configured.</strong> Keep the Assignment unpublished and ungraded until the Major group and 40/60 weighting are verified.","PREP":f'<ul><li>Post {file_link(files["BLUEPRINT"]["id"], "the Blueprint")} and {file_link(files["RUBRIC"]["id"], "the student-visible rubric")}.</li><li>Open the private unpublished Assignment.</li><li>Have missing-artifact fallback evidence ready.</li></ul>',"EVIDENCE":"<p>Private synthesis of self, career, pathway, backup, next action, and question. Recommended 16-point major.</p>","FLOW":flow("#5a2d91","Warm-up · 5","Revision versus quitting.")+flow("#4a9d2f","Career thinker · 8","Notice, choose, act, revise.")+flow("#1f617a","Blueprint · 22","Complete all seven jobs.")+flow("#e3ad19","Review · 10","Self, teacher, label-only partner, or audio route.")+flow("#1f617a","Submit · 5","Private exit sentence and submission."),"MONITOR":"<p>Suggested conversion after local approval: 15-16 Masters, 13-14 Meets, 12 Approaches, 10-11 Needs Improvement; below 10 follows campus policy. Score evidence and reasoning, not grammar, art, accent, or submission mode unless meaning is unclear.</p>","RESOURCES":"<p>Licensed FYF Career Thinker and Doer excerpt is embedded. The four earlier packets supply the complete evidence set.</p>","SUPPORT":"<p>Use numbered sentence jobs, speech-to-text, teacher scribe, or media recording. The printable has full-width writing space matched to the requested response.</p>","FALLBACK":"<p>A missing earlier artifact does not force a restart. Use the fallback box. Canvas failure means paper or later upload without penalty.</p>"},
        }

        day_names = {1:"Profile Audit",2:"Career Iceberg",3:"Career Deep Dive",4:"Pathway and CTSO Decision",5:"Mid-Year Career Blueprint"}
        pages, order = {}, []
        for day in range(1, 6):
            title = f"Day {day} · {day_names[day]}"
            header = await upsert_item(client, module["id"], "SubHeader", None, title)
            order.append(("SubHeader", header["id"], title))
            student_title = f"STUDENT: 4SW Wk1 Day {day} - {day_names[day]}"
            student_page = await upsert_page(client, student_title, render("4sw-wk1-student.html", {"COURSE_ID":COURSE_ID,"DAY":day,"MEDIA":media[day],**student[day]}))
            teacher_title = f"TEACHER: 4SW Wk1 Day {day} Facilitator Guide"
            teacher_page = await upsert_page(client, teacher_title, render("4sw-wk1-teacher.html", {"COURSE_ID":COURSE_ID,"DAY":day,"STUDENT_PAGE_URL":student_page["url"],**teacher[day]}))
            await upsert_item(client, module["id"], "Page", teacher_page["url"], teacher_title)
            await upsert_item(client, module["id"], "Page", student_page["url"], student_title)
            order += [("Page",teacher_page["url"],teacher_title),("Page",student_page["url"],student_title)]
            pages[day] = {"teacher":teacher_page,"student":student_page}
            if day == 2:
                await upsert_item(client, module["id"], "Assignment", annotation["id"], ANNOTATION_TITLE)
                order.append(("Assignment",annotation["id"],ANNOTATION_TITLE))
            if day == 5:
                await upsert_item(client, module["id"], "Assignment", blueprint["id"], BLUEPRINT_TITLE)
                order.append(("Assignment",blueprint["id"],BLUEPRINT_TITLE))

        items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        for position, (kind, key, title) in enumerate(order, 1):
            item = next(entry for entry in items if (kind == "SubHeader" and entry.get("id") == key) or (kind == "Page" and entry.get("page_url") == key) or (kind == "Assignment" and entry.get("content_id") == key))
            await api(client, "PUT", f"/courses/{COURSE_ID}/modules/{module['id']}/items/{item['id']}", data={"module_item[position]":position,"module_item[title]":title})

        final_items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
        module = await api(client, "GET", f"/courses/{COURSE_ID}/modules/{module['id']}")
        print(json.dumps({
            "module":{"id":module["id"],"published":module["published"]},
            "annotation":{"id":annotation["id"],"published":annotation.get("published"),"submission_types":annotation.get("submission_types"),"annotatable_attachment_id":annotation.get("annotatable_attachment_id")},
            "blueprint":{"id":blueprint["id"],"published":blueprint.get("published"),"submission_types":blueprint.get("submission_types"),"grading_type":blueprint.get("grading_type")},
            "support_folder":{"id":support_folder["id"],"locked":support_folder["locked"]},
            "visual_folders":{str(day):{"id":folder["id"],"locked":folder["locked"]} for day,folder in folders.items()},
            "files":{key:value["id"] for key,value in files.items()},
            "visuals":{str(day):{name:value["id"] for name,value in entries.items()} for day,entries in visuals.items()},
            "pages":{str(day):{kind:{"url":value["url"],"published":value["published"]} for kind,value in pair.items()} for day,pair in pages.items()},
            "items":[{"position":item["position"],"type":item["type"],"title":item["title"]} for item in final_items],
        }, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
