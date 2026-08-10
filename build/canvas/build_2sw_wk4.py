"""Build the unpublished 2SW Week 4 teacher/student Canvas module and practice quiz."""

import asyncio, json, mimetypes, re, sys
from pathlib import Path
import httpx

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
MODULE_NAME = "2SW Wk4: Smile Squad - Dental Science and Health Data"
COLLEGE_QUIZ_TITLE = "PRACTICE: College Credit Opportunity Check"
ICD_QUIZ_TITLE = "PRACTICE: ICD-10-CM Evidence Check"
MINOR_TITLE = "MINOR 2: Health Career Evidence Check"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = Path(__file__).parent / "templates"
ASSETS = ROOT / "cce-curriculum/resources/canvas-licensed/2sw/wk4"


def slugify(v):
    return re.sub(r"[^a-z0-9]+", "-", v.lower().replace("&", "and")).strip("-")


async def api(c, m, p, **kw):
    r = await c.request(m, f"{BASE}/api/v1{p}", **kw)
    r.raise_for_status()
    return r.json() if r.content else None


async def paged(c, p, params=None):
    out = []
    url = f"{BASE}/api/v1{p}"
    q = {"per_page": 100, **(params or {})}
    while url:
        r = await c.get(url, params=q)
        r.raise_for_status()
        out += r.json()
        url = r.links.get("next", {}).get("url")
        q = None
    return out


async def ensure_module(c):
    modules = await paged(c, f"/courses/{COURSE_ID}/modules")
    found = next((m for m in modules if m["name"] == MODULE_NAME), None)
    if found:
        return await api(
            c,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{found['id']}",
            data={"module[name]": MODULE_NAME, "module[published]": "false"},
        )
    return await api(
        c,
        "POST",
        f"/courses/{COURSE_ID}/modules",
        data={"module[name]": MODULE_NAME, "module[published]": "false"},
    )


async def ensure_folder(c, path):
    current = ""
    folder = None
    for name in path.split("/")[1:]:
        target = f"{current}/{name}".strip("/")
        enc = httpx.URL("/" + target).raw_path.decode("ascii").lstrip("/")
        r = await c.get(f"{BASE}/api/v1/courses/{COURSE_ID}/folders/by_path/{enc}")
        if r.status_code == 200 and r.json():
            folder = r.json()[-1]
        else:
            folder = await api(
                c,
                "POST",
                f"/courses/{COURSE_ID}/folders",
                data={
                    "name": name,
                    "parent_folder_path": "course files"
                    + (f"/{current}" if current else ""),
                    "locked": "true",
                },
            )
        current = target
    if folder and not folder.get("locked"):
        folder = await api(
            c, "PUT", f"/folders/{folder['id']}", data={"locked": "true"}
        )
    return folder


async def upload(c, path, folder):
    init = await api(
        c,
        "POST",
        f"/courses/{COURSE_ID}/files",
        data={
            "name": path.name,
            "parent_folder_path": folder,
            "on_duplicate": "overwrite",
        },
    )
    r = await c.post(
        init["upload_url"],
        data=init["upload_params"],
        files={
            "file": (
                path.name,
                path.read_bytes(),
                mimetypes.guess_type(path.name)[0] or "application/octet-stream",
            )
        },
        follow_redirects=True,
    )
    r.raise_for_status()
    return r.json()


def render(name, values):
    text = (TEMPLATES / name).read_text()
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", str(v))
    unresolved = sorted(set(re.findall(r"\{\{[^}]+\}\}", text)))
    if unresolved:
        raise ValueError(f"Unresolved values in {name}: {unresolved}")
    return text


async def upsert_page(c, title, body, url):
    data = {
        "wiki_page[title]": title,
        "wiki_page[body]": body,
        "wiki_page[published]": "false",
        "wiki_page[editing_roles]": "teachers",
    }
    r = await c.get(f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{url}")
    if r.status_code == 200:
        return await api(c, "PUT", f"/courses/{COURSE_ID}/pages/{url}", data=data)
    if r.status_code != 404:
        r.raise_for_status()
    return await api(c, "POST", f"/courses/{COURSE_ID}/pages", data=data)


async def upsert_page_item(c, module_id, page, title):
    items = await paged(c, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    item = next((i for i in items if i.get("page_url") == page["url"]), None)
    if item:
        return await api(
            c,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            data={"module_item[title]": title},
        )
    return await api(
        c,
        "POST",
        f"/courses/{COURSE_ID}/modules/{module_id}/items",
        data={
            "module_item[type]": "Page",
            "module_item[page_url]": page["url"],
            "module_item[title]": title,
        },
    )


async def upsert_subheader(c, module_id, title):
    items = await paged(c, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    item = next(
        (i for i in items if i.get("type") == "SubHeader" and i.get("title") == title),
        None,
    )
    if item:
        return await api(
            c,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            data={"module_item[title]": title, "module_item[indent]": "0"},
        )
    return await api(
        c,
        "POST",
        f"/courses/{COURSE_ID}/modules/{module_id}/items",
        data={
            "module_item[type]": "SubHeader",
            "module_item[title]": title,
            "module_item[indent]": "0",
        },
    )


def file_link(file_id, label):
    return f'<a href="/courses/{COURSE_ID}/files/{file_id}/preview" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">{label}</a>'


def image_tag(file_id, alt, max_width=760):
    return f'<img loading="lazy" src="/courses/{COURSE_ID}/files/{file_id}/preview" alt="{alt}" style="display:block;width:100%;max-width:{max_width}px;height:auto;margin:14px auto;border:1px solid #ddd" data-api-endpoint="/api/v1/courses/{COURSE_ID}/files/{file_id}" data-api-returntype="File">'


def step(num, title, body, color="#5a2d91"):
    return f'<h3 style="color:{color};border-bottom:3px solid #d9c9ed">{num}. {title}</h3>{body}'


def flow(color, title, text):
    return f'<div style="border-left:5px solid {color};padding-left:16px;margin:18px 0"><h4 style="margin:0;color:{color}">{title}</h4><p>{text}</p></div>'


COLLEGE_QUIZ_QUESTIONS = [
    {
        "name": "Q1 - Dual-credit route",
        "text": "Which statement matches the current Irving ISD coursebook?",
        "correct": "English III Dual Credit (H) is listed for grades 10-12 after English II and awards high-school and college credit.",
        "wrong": [
            "Every Grade 8 student may enroll now.",
            "An industry certification is the same as dual credit.",
            "The course has no prerequisite.",
        ],
        "correct_comment": "Correct. Keep the grade range, prerequisite, and credit type together.",
        "incorrect_comment": "Check the English III Dual Credit card: grades 10-12, English II prerequisite, and both high-school and college credit.",
    },
    {
        "name": "Q2 - AP Biology route",
        "text": "Which preparation statement matches the current coursebook for AP Biology?",
        "correct": "Grades 11-12; Biology plus Chemistry completed or taken at the same time",
        "wrong": [
            "Grade 9 with no prerequisite",
            "Grades 10-12 after English II",
            "Any grade after one health-science course",
        ],
        "correct_comment": "Correct. The coursebook lists Biology and completed or concurrent Chemistry.",
        "incorrect_comment": "Use the AP Biology card, not a guess based on the course title.",
    },
    {
        "name": "Q3 - AP credit limit",
        "text": "Why should a student verify a college's AP policy?",
        "correct": "Each receiving institution decides what AP score or course evidence earns credit.",
        "wrong": [
            "Every AP course automatically gives the same college credit.",
            "AP is an industry certification.",
            "AP credit can only be earned at Singley Academy.",
        ],
        "correct_comment": "Correct. AP can lead to credit, but the receiving institution sets the policy.",
        "incorrect_comment": "An AP course does not guarantee the same credit at every college.",
    },
]
ICD_QUIZ_QUESTIONS = [
    {
        "name": "Q1 - Privacy boundary",
        "text": "Which record may be used in this classroom coding practice?",
        "correct": "A fictional chart supplied in the lesson",
        "wrong": [
            "My own health record",
            "A relative's discharge paper",
            "A classmate's symptoms",
        ],
        "correct_comment": "Correct. Every chart in the lab is fictional.",
        "incorrect_comment": "Do not use real personal or family health information.",
    },
    {
        "name": "Q2 - Exact documented diagnosis",
        "text": "A fictional chart documents dental caries, unspecified. Which supplied code is the best match?",
        "correct": "K02.9",
        "wrong": ["J20.9", "R51.9", "R07.9"],
        "correct_comment": "Correct. K02.9 exactly matches the documented diagnosis.",
        "incorrect_comment": "Match the documented diagnosis to the exact supplied description.",
    },
    {
        "name": "Q3 - Specificity",
        "text": "A chart mentions chest discomfort but documents gastro-esophageal reflux disease without esophagitis. Which supplied code is best?",
        "correct": "K21.9",
        "wrong": ["R07.9", "J00", "L30.9"],
        "correct_comment": "Correct. Use the supported diagnosis instead of a less-specific symptom code.",
        "incorrect_comment": "The chart documents reflux; K21.9 is more specific than the chest-pain symptom code.",
    },
    {
        "name": "Q4 - Career scope",
        "text": "Which statement matches Medical Billing and Coding in FYF?",
        "correct": "The work can include medical documentation, insurance processes, coding systems, and reimbursement procedures.",
        "wrong": [
            "Every worker diagnoses patients.",
            "Every student automatically earns the listed certification.",
            "The career guarantees remote work.",
        ],
        "correct_comment": "Correct. This matches the current FYF description.",
        "incorrect_comment": "Use the FYF description. Do not add diagnosis duties, credential guarantees, or work-setting guarantees.",
    },
    {
        "name": "Q5 - Pay label",
        "text": "What does $50,250 mean in the career guide?",
        "correct": "The May 2024 U.S. median comparison figure in the career guide",
        "wrong": [
            "Guaranteed DFW starting pay",
            "The salary every worker earns",
            "The cost of a certificate",
        ],
        "correct_comment": "Correct. Keep the year, geography, and measure attached.",
        "incorrect_comment": "It is a May 2024 U.S. median, not local or starting pay.",
    },
]


async def upsert_quiz(c, title, description, question_specs):
    quizzes = await paged(c, f"/courses/{COURSE_ID}/quizzes")
    quiz = next((q for q in quizzes if q.get("title") == title), None)
    data = {
        "quiz[title]": title,
        "quiz[description]": description,
        "quiz[quiz_type]": "practice_quiz",
        "quiz[published]": "false",
        "quiz[allowed_attempts]": "-1",
        "quiz[show_correct_answers]": "true",
        "quiz[shuffle_answers]": "false",
    }
    quiz = await api(
        c,
        "PUT" if quiz else "POST",
        f"/courses/{COURSE_ID}/quizzes/{quiz['id']}"
        if quiz
        else f"/courses/{COURSE_ID}/quizzes",
        data=data,
    )
    existing = await paged(c, f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions")
    for position, spec in enumerate(question_specs, start=1):
        found = next(
            (q for q in existing if q.get("question_name") == spec["name"]), None
        )
        answers = [{"answer_text": spec["correct"], "answer_weight": 100}] + [
            {"answer_text": v, "answer_weight": 0} for v in spec["wrong"]
        ]
        payload = {
            "question": {
                "question_name": spec["name"],
                "question_text": spec["text"],
                "question_type": "multiple_choice_question",
                "position": position,
                "points_possible": 1,
                "correct_comments": spec["correct_comment"],
                "incorrect_comments": spec["incorrect_comment"],
                "answers": answers,
            }
        }
        await api(
            c,
            "PUT" if found else "POST",
            f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions/{found['id']}"
            if found
            else f"/courses/{COURSE_ID}/quizzes/{quiz['id']}/questions",
            json=payload,
        )
    return await api(c, "GET", f"/courses/{COURSE_ID}/quizzes/{quiz['id']}")


async def upsert_quiz_item(c, module_id, quiz, title):
    items = await paged(c, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    item = next(
        (
            i
            for i in items
            if i.get("type") == "Quiz" and i.get("content_id") == quiz["id"]
        ),
        None,
    )
    if item:
        return await api(
            c,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            data={"module_item[title]": title},
        )
    return await api(
        c,
        "POST",
        f"/courses/{COURSE_ID}/modules/{module_id}/items",
        data={
            "module_item[type]": "Quiz",
            "module_item[content_id]": quiz["id"],
            "module_item[title]": title,
        },
    )


async def upsert_assignment_item(c, module_id, assignment):
    items = await paged(c, f"/courses/{COURSE_ID}/modules/{module_id}/items")
    item = next(
        (
            i
            for i in items
            if i.get("type") == "Assignment" and i.get("content_id") == assignment["id"]
        ),
        None,
    )
    if item:
        return await api(
            c,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
            data={"module_item[title]": MINOR_TITLE},
        )
    return await api(
        c,
        "POST",
        f"/courses/{COURSE_ID}/modules/{module_id}/items",
        data={
            "module_item[type]": "Assignment",
            "module_item[content_id]": assignment["id"],
            "module_item[title]": MINOR_TITLE,
        },
    )


async def update_minor_assignment(c, assignment, description):
    return await api(
        c,
        "PUT",
        f"/courses/{COURSE_ID}/assignments/{assignment['id']}",
        data={
            "assignment[name]": MINOR_TITLE,
            "assignment[description]": description,
            "assignment[published]": "false",
        },
    )


async def main():
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as c:
        module = await ensure_module(c)
        module_id = module["id"]
        college_quiz = await upsert_quiz(
            c,
            COLLEGE_QUIZ_TITLE,
            "<p>Ungraded practice using two current Irving ISD coursebook cards. Retry as needed. This check does not replace required Xello completion.</p>",
            COLLEGE_QUIZ_QUESTIONS,
        )
        icd_quiz = await upsert_quiz(
            c,
            ICD_QUIZ_TITLE,
            "<p>Ungraded practice for fictional records, code specificity, career scope, and data labels. Retry as needed.</p>",
            ICD_QUIZ_QUESTIONS,
        )
        assignments = await paged(c, f"/courses/{COURSE_ID}/assignments")
        minor = next((a for a in assignments if a.get("name") == MINOR_TITLE), None)
        if not minor:
            raise RuntimeError(f"Existing Canvas assignment not found: {MINOR_TITLE}")
        names = {
            "GUIDE": "2sw-wk4-dental-health-data-guide.pdf",
            "COMPARE": "2sw-wk4-career-evidence-comparison.pdf",
            "OBSERVE": "2sw-wk4-smile-squad-observation-record.pdf",
            "DESIGN": "2sw-wk4-toothbrush-design-brief.pdf",
            "XELLO_CHECK": "2sw-wk4-xello-experiences-checkpoint.pdf",
            "LAB": "2sw-wk4-icd10-training-lab.pdf",
            "RUBRIC": "2sw-wk4-evidence-check-rubric.pdf",
        }
        support_folder = "course files/CCR Materials/2SW/Wk4"
        core = await ensure_folder(c, support_folder)
        files = {
            k: await upload(c, ROOT / "docs/resources/worksheets" / v, support_folder)
            for k, v in names.items()
        }
        files["XELLO"] = await upload(
            c,
            ROOT
            / "cce-curriculum/resources/xello-licensed/prerequisites/experiences.pdf",
            support_folder,
        )
        uploads = {}
        folders = {}
        for day in range(1, 6):
            fp = f"course files/CCR Materials/2SW/Wk4/Day {day} Visuals"
            folders[day] = await ensure_folder(c, fp)
            uploads[day] = {}
            source = ASSETS / f"day{day}"
            if source.exists():
                for path in sorted(source.glob("*.png")):
                    uploads[day][path.name] = await upload(c, path, fp)
        minor = await update_minor_assignment(
            c,
            minor,
            f"""
<div style="max-width:860px;margin:0 auto;font-family:Arial,Helvetica,sans-serif;line-height:1.5;color:#24323d">
  <h2 style="color:#5a2d91">Health Career Evidence Check</h2>
  <div style="border:1px solid #bad4df;border-radius:9px;background:#f2f8fb;padding:14px 18px">
    <p><strong>Topic:</strong> Career Recommendation</p>
    <p><strong>Objective:</strong> Compare preparation and labor-market evidence for three Health Science careers and recommend one route for a fictional student.</p>
    <p><strong>Show your learning:</strong> Submit a three-career comparison and four-part recommendation.</p>
  </div>
  <h3>Use these sources</h3>
  <ul>
    <li>FYF pp. 84-85 for the Irving ISD Medical Billing and Coding program information</li>
    <li>{file_link(files["GUIDE"]["id"], "Dental Health and Career Evidence Guide")}</li>
    <li>{file_link(files["RUBRIC"]["id"], "16-point scoring rubric")}</li>
    <li>{file_link(files["COMPARE"]["id"], "optional print route")} only when your teacher assigns paper</li>
  </ul>
  <h3>Scenario</h3>
  <p>Jordan likes careful recordkeeping and helping people. Jordan prefers preparation shorter than a four-year degree and wants to compare wage and growth evidence.</p>
  <h3>Complete four sentence jobs</h3>
  <ol>
    <li>Recommend Dental Assistant, Dental Hygienist, or Medical Billing and Coding. Connect the choice to one of Jordan's needs.</li>
    <li>State the common preparation and one responsibility.</li>
    <li>Cite the pay and growth figures with their labels.</li>
    <li>Explain the classification and one trade-off or fact Jordan should verify.</li>
  </ol>
  <p><strong>Submit:</strong> Type the four responses here, or upload the completed paper route if your teacher assigned it.</p>
</div>
""".strip(),
        )
        college_quiz_url = f"/courses/{COURSE_ID}/quizzes/{college_quiz['id']}"
        icd_quiz_url = f"/courses/{COURSE_ID}/quizzes/{icd_quiz['id']}"
        minor_url = f"/courses/{COURSE_ID}/assignments/{minor['id']}"
        xray_help = (
            '<details style="border:1px solid #cfc5dd;border-radius:8px;padding:12px 16px;margin:18px 0"><summary style="font-weight:700;color:#5a2d91;cursor:pointer">Open the five training X-rays</summary>'
            + "".join(
                image_tag(
                    uploads[1][f"xray-{i}.png"]["id"],
                    f"Training X-ray {i}; describe visible light, dark, smooth, or uneven patterns without diagnosing",
                    620,
                )
                for i in range(1, 6)
            )
            + "</details>"
        )
        student = {
            1: {
                "TITLE": "Read Dental Evidence Carefully",
                "TOPIC": "Dental Evidence",
                "I_CAN": "Identify two dental careers and describe one preparation requirement for each.",
                "SHOW_LEARNING": "Complete FYF pp. 69-71 and the two-career comparison check.",
                "PURPOSE": "Describe what you can see. Leave diagnosis to trained professionals.",
                "TODAY": "<ul><li>record visible patterns from five training images;</li><li>make a prevention recommendation from workbook clues;</li><li>compare two dental careers.</li></ul>",
                "READY": f"<p>Open your assigned <strong>FYF workbook to pp. 69-71</strong>. Your teacher will project the {file_link(files['GUIDE']['id'], 'career evidence guide')}. Use the {file_link(files['OBSERVE']['id'], 'optional observation scaffold')} only if your teacher assigns it.</p>",
                "STEPS": step(
                    1,
                    "Read the reference chart",
                    image_tag(
                        uploads[1]["xray-reference-chart.png"]["id"],
                        "Reference chart showing healthy tooth, decay, filling, and plaque appearance patterns",
                        720,
                    ),
                )
                + step(
                    2,
                    "Record observations",
                    "<p>Write one visible pattern for each image. Use words such as bright, dark, smooth, uneven, or developing. Do not name a diagnosis.</p>"
                    + xray_help,
                )
                + step(
                    3,
                    "Use two workbook clues",
                    image_tag(
                        uploads[1]["fyf-smile-squad-2.png"]["id"],
                        "Find Your Future cavity-risk chart used to record evidence and a prevention recommendation",
                        700,
                    )
                    + "<p>Cite two clues and choose one low-risk prevention step.</p>",
                )
                + step(
                    4,
                    "Compare two careers",
                    "<p>Complete the Dental Assistant and Dental Hygienist rows. Keep <strong>May 2024 · U.S. · median</strong> attached to pay.</p>",
                ),
                "DONE": "<ul><li>five careful observations;</li><li>two clues and one recommendation;</li><li>two complete career rows.</li></ul>",
                "SUPPORT": "<p>observation = observación · evidence = evidencia · median = mediana. Frame: “I see ____. The closest chart pattern is ____, but this does not prove ____.”</p>",
                "FALLBACK": "<p>All images and facts are on this page. Complete the same record independently; no H&amp;L login is required.</p>",
            },
            2: {
                "TITLE": "Design a Toothbrush with Evidence",
                "TOPIC": "User-Centered Design",
                "I_CAN": "Connect an oral-health design to a user need and classify two Health Science careers.",
                "SHOW_LEARNING": "Complete the FYF p. 73 prototype and two evidence-based classifications.",
                "PURPOSE": "Build for a specific user need, then classify career evidence with one rule.",
                "TODAY": "<ul><li>choose a fictional user;</li><li>sketch and label four features;</li><li>classify two careers.</li></ul>",
                "READY": f"<p>Open your assigned <strong>FYF workbook to pp. 72-73</strong>. Use the {file_link(files['DESIGN']['id'], 'optional design scaffold')} only if your teacher assigns it. The career facts stay visible on this page.</p>",
                "STEPS": step(
                    1,
                    "Choose the user",
                    "<p>Choose a child learning to brush, a person with limited grip strength, or a student with braces. No personal health story is required.</p>",
                )
                + step(
                    2,
                    "Read the fixed design facts",
                    image_tag(
                        uploads[2]["fyf-perfect-toothbrush-1.png"]["id"],
                        "Find Your Future Perfect Toothbrush directions and research prompts",
                        700,
                    ),
                )
                + step(
                    3,
                    "Sketch and label",
                    image_tag(
                        uploads[2]["fyf-perfect-toothbrush-2.png"]["id"],
                        "Find Your Future toothbrush design box with space to explain feature choices",
                        700,
                    )
                    + "<p>Label bristles, head, handle, and one added feature. Explain how each helps your user.</p>",
                )
                + step(
                    4,
                    "Classify two careers",
                    "<p>Use the guide's course comparison rule. Cite the number or preparation fact that supports each label.</p>",
                ),
                "DONE": "<ul><li>four labeled features;</li><li>one fact connected to the user;</li><li>two careers classified with evidence.</li></ul>",
                "SUPPORT": "<p>bristles = cerdas · handle = mango · feature = característica. Frame: “I chose ____ because my user needs ____.”</p>",
                "FALLBACK": "<p>Draw on paper or describe the design with labeled words. Artistic quality is not graded.</p>",
            },
            3: {
                "TITLE": "Add Real Experiences in Xello",
                "TOPIC": "College Credit",
                "I_CAN": "Record real experiences and compare two current ways to earn college credit in high school.",
                "SHOW_LEARNING": "Meet the Xello completion requirements and finish the Canvas college-credit check.",
                "PURPOSE": "Record experiences that actually happened and compare two real college-credit opportunities.",
                "TODAY": "<ul><li>add one Education experience;</li><li>add at least one completed volunteer hour;</li><li>compare two current college-credit opportunities.</li></ul>",
                "READY": f"<p>Open ClassLink → Xello. The licensed {file_link(files['XELLO']['id'], 'My Experiences guide')} is available for help. The {file_link(files['XELLO_CHECK']['id'], 'one-page print check')} is only a Canvas-outage fallback.</p>",
                "STEPS": step(
                    1,
                    "Protect privacy",
                    "<p>Use real experiences, but do not enter client names, medical details, private contact information, or a public profile link.</p>",
                )
                + step(
                    2,
                    "Add an Education experience",
                    "<p>Xello → About Me → Experiences → Education. Add at least one actual experience and save.</p>",
                )
                + step(
                    3,
                    "Add Volunteer hours",
                    "<p>Add at least one hour you completed. If you have no completed hour, do not invent one; tell the teacher and join catch-up.</p>",
                )
                + step(
                    4,
                    "Compare two college-credit options",
                    f'<div style="border:1px solid #bad4df;border-radius:8px;padding:12px 16px;margin:12px 0"><p><strong>English III Dual Credit (H)</strong>: grades 10-12; prerequisite English II; earns high-school and college credit.</p><p><strong>AP Biology</strong>: grades 11-12; prerequisite Biology plus completed or concurrent Chemistry; college credit depends on the receiving institution.</p></div><p><a href="{college_quiz_url}">Open the College Credit Opportunity Check</a>. It is ungraded and gives feedback.</p>',
                ),
                "DONE": "<ul><li>Education experience saved;</li><li>Volunteer hour saved or catch-up recorded;</li><li>two sourced college-credit opportunities.</li></ul>",
                "SUPPORT": "<p>experience = experiencia · volunteer = voluntariado · prerequisite = prerrequisito. Frame: “The source lists ____ as ____ credit. One requirement is ____.”</p>",
                "FALLBACK": "<p>Use the one-page college-credit check now. Required Xello saves move to supervised catch-up; paper does not replace platform completion.</p>",
            },
            4: {
                "TITLE": "Try a Medical-Coding Evidence Lab",
                "TOPIC": "Health Information",
                "I_CAN": "Describe Medical Billing and Coding work and choose the most specific supported code.",
                "SHOW_LEARNING": "Complete the Medical Billing and Coding evidence row and individual fictional coding lab.",
                "PURPOSE": "Use complete fictional documentation to choose from a short current code list.",
                "TODAY": "<ul><li>finish the third career row;</li><li>code eight fictional charts;</li><li>retry an automatic practice check.</li></ul>",
                "READY": f"<p>Open {file_link(files['LAB']['id'], 'the ICD-10-CM Training Lab')}, {file_link(files['GUIDE']['id'], 'the career guide')}, and your comparison.</p>",
                "STEPS": step(
                    1,
                    "Keep every chart fictional",
                    "<p>Never use your own or another person's health information. This lab does not teach you to diagnose or bill.</p>",
                )
                + step(
                    2,
                    "Read the FYF Medical Billing route",
                    "<p>Use FYF pp. 84-85 for the work and pathway title. Add preparation, responsibility, and classification to row three. Use the labeled comparison figures in the guide.</p>",
                )
                + step(
                    3,
                    "Code Round 1",
                    "<p>Match three documented diagnoses to exact descriptions. Correct mistakes before Round 2.</p>",
                )
                + step(
                    4,
                    "Code Round 2",
                    "<p>Underline the documented diagnosis. Choose the most specific supported description, then explain one weaker option.</p>",
                )
                + step(
                    5,
                    "Retry the practice quiz",
                    f'<p><a href="{icd_quiz_url}">Open the ICD-10-CM Evidence Check</a>. It is ungraded and gives feedback.</p>',
                ),
                "DONE": "<ul><li>third career row complete;</li><li>eight fictional charts attempted;</li><li>one correction explained;</li><li>practice feedback reviewed.</li></ul>",
                "SUPPORT": "<p>documented = documentado · specific = específico · diagnosis code = código de diagnóstico. Use the five-code support list if assigned.</p>",
                "FALLBACK": "<p>The paper lab is the full no-device route. Complete the quiz later only if your teacher assigns it.</p>",
            },
            5: {
                "TITLE": "Recommend a Health Career with Evidence",
                "TOPIC": "Career Recommendation",
                "I_CAN": "Compare three Health Science careers and recommend one route using accurate evidence.",
                "SHOW_LEARNING": "Submit the Canvas Minor with a three-career comparison and four-part recommendation.",
                "PURPOSE": "Choose a route for Jordan and make the evidence easy to check.",
                "TODAY": "<ul><li>audit all three career rows;</li><li>write four sentence jobs;</li><li>self-score and revise.</li></ul>",
                "READY": f'<p>Open the <a href="{minor_url}">Health Career Evidence Check</a>. Use the {file_link(files["GUIDE"]["id"], "evidence guide")} and {file_link(files["RUBRIC"]["id"], "16-point rubric")}. The {file_link(files["COMPARE"]["id"], "optional print route")} is for students assigned paper.</p>',
                "STEPS": step(
                    1,
                    "Audit the evidence",
                    "<p>Every row needs responsibility, preparation, pay label, outlook, and source. Fix “starting” or “DFW” when the figure is a U.S. median.</p>",
                )
                + step(
                    2,
                    "Read Jordan's needs",
                    "<p>Jordan likes careful recordkeeping and helping people, prefers preparation shorter than four years, and wants a comparison of wage and growth evidence.</p>",
                )
                + step(
                    3,
                    "Write four sentence jobs",
                    "<ol><li>Recommend and connect to one need.</li><li>State preparation and responsibility.</li><li>Cite pay and growth with labels.</li><li>Explain classification and one trade-off or fact to verify.</li></ol>",
                )
                + step(
                    4,
                    "Self-score and revise",
                    "<p>Use all four rubric rows. Revise one weak label or reasoning sentence before submitting.</p>",
                ),
                "DONE": "<ul><li>all three rows audited;</li><li>four sentence jobs complete;</li><li>two accurate facts and a trade-off;</li><li>rubric self-check complete.</li></ul>",
                "SUPPORT": "<p>trade-off = decisión con ventajas y límites. Frame: “I recommend ____ because ____. The May 2024 U.S. median is ____. One trade-off is ____.”</p>",
                "FALLBACK": "<p>The fixed guide contains every required fact. No H&amp;L or Xello login is required for this checkpoint.</p>",
            },
        }
        teacher = {
            1: {
                "TITLE": "Read Dental Evidence Carefully",
                "TOPIC": "Dental Evidence",
                "OBJECTIVE": "Students will identify Dental Assistant and Dental Hygienist as Health Science careers and describe one preparation requirement for each career.",
                "TEKS": "d(1)(C), d(2)(A)",
                "DOL": "Completed FYF Smile Squad evidence response and two-career comparison check.",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(2)(A)",
                "ALERT": "<strong>Observation, not diagnosis.</strong> The licensed images are a training set. Students name visible patterns and uncertainty; they do not diagnose a patient.",
                "PREP": f"<ul><li>Open the embedded chart and X-rays.</li><li>Have students use FYF pp. 69-71. Project the {file_link(files['GUIDE']['id'], 'career guide')}.</li><li>Do not print the {file_link(files['OBSERVE']['id'], 'optional observation scaffold')} unless a student needs the access/no-workbook route.</li></ul>",
                "EVIDENCE": "<p>Monitor the completed FYF evidence response and collect the short two-career comparison check. Default printing: none.</p>",
                "FLOW": flow(
                    "#5a2d91",
                    "Observation or conclusion · 5",
                    "Separate visible fact from professional conclusion.",
                )
                + flow(
                    "#4a9d2f",
                    "Training images · 18",
                    "Record patterns; accept careful uncertainty.",
                )
                + flow("#1f617a", "Prevention evidence · 7", "Cite two workbook clues.")
                + flow(
                    "#e3ad19",
                    "Two careers · 15",
                    "Preparation, responsibility, labeled median.",
                )
                + flow(
                    "#1f617a",
                    "Exit · 5",
                    "Rewrite an overclaim and name a trained role.",
                ),
                "MONITOR": "<p>Expected patterns: X1 developing teeth/no obvious restoration; X2 developing teeth/darker area worth review; X3 bright restoration/crown and root line; X4-X5 multiple bright restorations. Do not require a diagnosis. Pay: Assistant $47,300/6%; Hygienist $94,260/7%.</p>",
                "SUPPORT": "<p>Read image descriptions aloud; allow dictation. Score evidence, not certainty or English mechanics.</p>",
                "FALLBACK": "<p>All images are embedded. No live site is load-bearing. Absent students use the same sequence.</p>",
            },
            2: {
                "TITLE": "Design a Toothbrush with Evidence",
                "TOPIC": "User-Centered Design",
                "OBJECTIVE": "Students will identify how oral-health workers respond to user needs and classify two Health Science careers using labor-market evidence.",
                "TEKS": "d(1)(C), d(5)(B)",
                "DOL": "Completed FYF toothbrush prototype and two evidence-based career classifications.",
                "SUBTITLE": "50 minutes · TEKS d(1)(C), d(5)(B)",
                "ALERT": "<strong>Design and classification are separate.</strong> A good toothbrush idea does not prove a career is high demand.",
                "PREP": f"<ul><li>Have students use FYF pp. 72-73.</li><li>Project the fixed design facts and career evidence.</li><li>Do not print the {file_link(files['DESIGN']['id'], 'optional design scaffold')} unless a student needs the access/no-workbook route.</li></ul>",
                "EVIDENCE": "<p>Monitor the FYF prototype and collect two short classification responses. Default printing: none.</p>",
                "FLOW": flow("#5a2d91", "Choose user · 5", "No personal disclosure.")
                + flow(
                    "#4a9d2f",
                    "Fixed facts · 8",
                    "Highlight the fact that fits the user.",
                )
                + flow("#1f617a", "Design · 18", "Four labels and explanation.")
                + flow("#e3ad19", "Feedback · 8", "Two questions, then revise.")
                + flow(
                    "#1f617a",
                    "Classify and exit · 11",
                    "Use the same-source wage and growth lines.",
                ),
                "MONITOR": "<p>Dental Assistant: below wage line, above growth line, specialized preparation/duties. Hygienist: above wage and growth lines, specialized preparation/licensure. Call these course evidence labels, not official designations.</p>",
                "SUPPORT": "<p>Allow verbal/tactile design description and oral rehearsal. Do not score drawing quality.</p>",
                "FALLBACK": "<p>Fixed facts remove open-search burden. The self-check replaces partner feedback when absent.</p>",
            },
            3: {
                "TITLE": "Add Real Experiences in Xello",
                "TOPIC": "College Credit",
                "OBJECTIVE": "Students will explore and list two current opportunities for earning college credit in high school.",
                "TEKS": "d(3)(B)",
                "DOL": "Xello Completion Standards evidence and completed Canvas college-credit opportunity check.",
                "SUBTITLE": "50 minutes · TEKS d(3)(B)",
                "ALERT": "<strong>Exact live requirements:</strong> Education experiences = add at least 1; Volunteer hours = add at least 1 completed hour. School subjects at work is supplemental, not Grade 8 completion.",
                "PREP": f'<ul><li>Preflight Xello through ClassLink and open Completion Standards.</li><li>Open the unpublished <a href="{college_quiz_url}">college-credit practice quiz</a>.</li><li>Keep the {file_link(files["XELLO_CHECK"]["id"], "one-page print fallback")} for a Canvas outage only.</li></ul>',
                "EVIDENCE": "<p>Verify Xello in the report and review the Canvas practice check. Industry certification is not college credit. Default printing: none.</p>",
                "FLOW": flow(
                    "#5a2d91",
                    "Privacy/honesty · 5",
                    "No invented hours or private details.",
                )
                + flow(
                    "#4a9d2f",
                    "Education experiences · 10",
                    "Add one actual experience.",
                )
                + flow(
                    "#1f617a",
                    "Volunteer hours · 15",
                    "Add one completed hour or record catch-up.",
                )
                + flow(
                    "#e3ad19",
                    "College credit · 15",
                    "Two current sourced opportunities.",
                )
                + flow("#1f617a", "Exit · 5", "Name type and requirement."),
                "MONITOR": "<p>At minute 15, Education should be saved. At minute 30, Volunteer is saved or catch-up recorded. Verify through the report. English III Dual Credit (H): grades 10-12 after English II, high-school and college credit. AP Biology: grades 11-12 after Biology with completed or concurrent Chemistry; receiving institutions set AP credit policy.</p>",
                "SUPPORT": "<p>Preview the navigation and give sentence frames. Do not require a full translation or public profile screenshot.</p>",
                "FALLBACK": "<p>Platform outage: use the paper checkpoint and schedule supervised Xello catch-up. Paper is not completion.</p>",
            },
            4: {
                "TITLE": "Medical Billing and ICD-10-CM Practice",
                "TOPIC": "Health Information",
                "OBJECTIVE": "Students will describe the Medical Billing and Coding pathway and classify related labor-market evidence while completing a bounded coding simulation.",
                "TEKS": "d(2)(A), d(5)(B)",
                "DOL": "Medical Billing and Coding evidence row and individual fictional coding lab.",
                "SUBTITLE": "50 minutes · TEKS d(2)(A), d(5)(B)",
                "ALERT": "<strong>Fictional records only.</strong> The lab is a bounded career simulation, not diagnosis, billing, or medical advice. Accuracy matters more than speed.",
                "PREP": f'<ul><li>Post {file_link(files["LAB"]["id"], "the lab")} and career guide.</li><li>Open the unpublished <a href="{icd_quiz_url}">practice quiz</a>.</li><li>Keep the five-code support route ready.</li></ul>',
                "EVIDENCE": "<p>Collect the third career row and individual lab. Quiz feedback is formative and ungraded.</p>",
                "FLOW": flow(
                    "#5a2d91",
                    "Career row · 10",
                    "Preparation, scope, $50,250 median, 7% growth.",
                )
                + flow(
                    "#4a9d2f",
                    "Model · 7",
                    "Match documented diagnosis to exact description.",
                )
                + flow("#1f617a", "Round 1 · 10", "J20.9, K02.9, R51.9.")
                + flow(
                    "#e3ad19", "Round 2 · 13", "K21.9, H66.90, L30.9, J02.9, S52.501A."
                )
                + flow(
                    "#1f617a",
                    "Quiz and exit · 10",
                    "Immediate misconception feedback plus career check.",
                ),
                "MONITOR": "<p>Round 1 key: J20.9, K02.9, R51.9. Round 2 key: K21.9, H66.90, L30.9, J02.9, S52.501A. R07.9 is weaker in case 4 because reflux is documented. Career figure is May 2024 U.S. median, not starting/local pay.</p>",
                "SUPPORT": "<p>Underline the documented diagnosis and limit assigned students to the five-code list. Each student records individual reasoning.</p>",
                "FALLBACK": "<p>Paper is the full no-device route. Do not use real charts. If time is short, cut the quiz, not Round 2 correction.</p>",
            },
            5: {
                "TITLE": "Recommend a Health Career with Evidence",
                "TOPIC": "Career Recommendation",
                "OBJECTIVE": "Students will compare preparation and labor-market evidence for three Health Science careers and recommend one route for a fictional student.",
                "TEKS": "d(2)(A), d(5)(B)",
                "DOL": "Submitted Canvas Minor with three-career comparison and four-part recommendation.",
                "SUBTITLE": "50 minutes · TEKS d(2)(A), d(5)(B)",
                "ALERT": "<strong>16-point Minor checkpoint.</strong> The existing Canvas assignment remains unpublished for teacher cloning and review.",
                "PREP": f'<ul><li>Open the existing <a href="{minor_url}">Health Career Evidence Check</a> and {file_link(files["RUBRIC"]["id"], "student-visible rubric")}.</li><li>Keep H&amp;L optional.</li><li>Use the current coursebook language for Health Science: Dental and Health Science: Medical Billing at Singley.</li></ul>',
                "EVIDENCE": "<p>Collect the three-row comparison and four-part Jordan recommendation. Score accuracy, classification, fit, and evidence/trade-off.</p>",
                "FLOW": flow("#5a2d91", "Audit · 8", "Correct all source labels.")
                + flow("#4a9d2f", "Scenario · 5", "Identify Jordan's constraints.")
                + flow("#1f617a", "Plan · 10", "Choose any defensible route.")
                + flow("#e3ad19", "Write · 15", "Four visible sentence jobs.")
                + flow(
                    "#1f617a",
                    "Self-score, revise, exit · 12",
                    "One evidence revision and trade-off.",
                ),
                "MONITOR": "<p>Any of the three careers may earn full credit if the scenario link and trade-off are defensible. Medical Billing and Coding is current FYF and district-coursebook content. Keep the fixed $50,250/7% evidence labeled as national comparison data and do not promise an individual credential outcome. Apply the 16-point district-band conversion on the rubric.</p>",
                "SUPPORT": "<p>Allow speech-to-text and sentence frames. Score career reasoning, not English mechanics.</p>",
                "FALLBACK": "<p>The fixed guide is the full absence route. No live H&amp;L or Xello login is required for this evidence check.</p>",
            },
        }
        pages = {}
        order = []
        for day in range(1, 6):
            header = await upsert_subheader(c, module_id, f"Day {day}")
            order.append(("SubHeader", header["id"], f"Day {day}"))
            st = f"STUDENT: 2SW Wk4 Day {day} - {student[day]['TITLE']}"
            sp = await upsert_page(
                c,
                st,
                render(
                    "2sw-wk4-student.html",
                    {"COURSE_ID": COURSE_ID, "DAY": day, **student[day]},
                ),
                slugify(st),
            )
            tt = f"TEACHER: 2SW Wk4 Day {day} Facilitator Guide"
            tp = await upsert_page(
                c,
                tt,
                render(
                    "2sw-wk4-teacher.html",
                    {
                        "COURSE_ID": COURSE_ID,
                        "DAY": day,
                        "STUDENT_PAGE_URL": sp["url"],
                        **teacher[day],
                    },
                ),
                slugify(tt),
            )
            await upsert_page_item(c, module_id, tp, tt)
            await upsert_page_item(c, module_id, sp, st)
            pages[day] = {"teacher": tp, "student": sp}
            order.extend([("Page", tp["url"], tt), ("Page", sp["url"], st)])
            if day == 3:
                await upsert_quiz_item(c, module_id, college_quiz, COLLEGE_QUIZ_TITLE)
                order.append(("Quiz", college_quiz["id"], COLLEGE_QUIZ_TITLE))
            if day == 4:
                await upsert_quiz_item(c, module_id, icd_quiz, ICD_QUIZ_TITLE)
                order.append(("Quiz", icd_quiz["id"], ICD_QUIZ_TITLE))
            if day == 5:
                await upsert_assignment_item(c, module_id, minor)
                order.append(("Assignment", minor["id"], MINOR_TITLE))
        items = await paged(c, f"/courses/{COURSE_ID}/modules/{module_id}/items")
        for position, (kind, key, title) in enumerate(order, start=1):
            item = next(
                i
                for i in items
                if (kind == "SubHeader" and i.get("id") == key)
                or (kind == "Page" and i.get("page_url") == key)
                or (kind in {"Quiz", "Assignment"} and i.get("content_id") == key)
            )
            await api(
                c,
                "PUT",
                f"/courses/{COURSE_ID}/modules/{module_id}/items/{item['id']}",
                data={"module_item[position]": position, "module_item[title]": title},
            )
        final = await paged(c, f"/courses/{COURSE_ID}/modules/{module_id}/items")
        college_questions = await paged(
            c, f"/courses/{COURSE_ID}/quizzes/{college_quiz['id']}/questions"
        )
        icd_questions = await paged(
            c, f"/courses/{COURSE_ID}/quizzes/{icd_quiz['id']}/questions"
        )
        module = await api(c, "GET", f"/courses/{COURSE_ID}/modules/{module_id}")
        print(
            json.dumps(
                {
                    "module": {"id": module_id, "published": module["published"]},
                    "quizzes": {
                        "college_credit": {
                            "id": college_quiz["id"],
                            "published": college_quiz["published"],
                            "type": college_quiz["quiz_type"],
                            "questions": len(college_questions),
                        },
                        "icd10": {
                            "id": icd_quiz["id"],
                            "published": icd_quiz["published"],
                            "type": icd_quiz["quiz_type"],
                            "questions": len(icd_questions),
                        },
                    },
                    "minor": {
                        "id": minor["id"],
                        "published": minor["published"],
                        "points": minor["points_possible"],
                    },
                    "folders": {
                        "core": {"id": core["id"], "locked": core["locked"]},
                        **{
                            str(d): {"id": f["id"], "locked": f["locked"]}
                            for d, f in folders.items()
                        },
                    },
                    "files": {k: v["id"] for k, v in files.items()},
                    "pages": {
                        str(d): {
                            k: {"url": v["url"], "published": v["published"]}
                            for k, v in p.items()
                        }
                        for d, p in pages.items()
                    },
                    "items": [
                        {
                            "id": i["id"],
                            "position": i["position"],
                            "title": i["title"],
                            "type": i["type"],
                            "page_url": i.get("page_url"),
                            "content_id": i.get("content_id"),
                        }
                        for i in final
                    ],
                },
                indent=2,
            )
        )


asyncio.run(main())
