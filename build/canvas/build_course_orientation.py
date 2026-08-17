#!/usr/bin/env python3
"""Build unpublished teacher and student course-orientation pages in Canvas."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import build_4sw_wk1 as common
import httpx

COURSE_ID = common.COURSE_ID
ORIENTATION_MODULE = "START HERE: CCE Course Orientation"
TEACHER_MODULE = "Teacher Build: Licensed Resources"
TEACHER_TITLE = "TEACHER: CCE Course Launch Guide"
STUDENT_TITLE = "STUDENT: Start Here - How CCE Works"
HOME_TITLE = "Career and College Exploration Home"
ROOT = Path(__file__).resolve().parents[2]
HOME_ASSET_DIR = Path(__file__).parent / "assets" / "course-home"
HOME_ASSET_FOLDER = "course files/CCR Materials/Course Home"
HOME_ASSETS = {
    "modules": "modules.png",
    "onenote": "onenote.png",
    "hats_ladders": "hats-ladders.png",
    "xello": "xello.png",
}
ONENOTE_URL = (
    "https://irvingisdnet-my.sharepoint.com/personal/"
    "elucero_irvingisd_net/Documents/Class%20Notebooks/"
    "CCE%202026-27%20%C2%B7%20Lucero"
)
HATS_LADDERS_URL = "https://app.hatsandladders.com/"
CLASSLINK_URL = "https://launchpad.classlink.com/irvingtx"
TEACHER_EMAIL = "elucero@irvingisd.net"


def preflight_home_assets() -> None:
    missing = [
        str((HOME_ASSET_DIR / name).relative_to(ROOT))
        for name in HOME_ASSETS.values()
        if not (HOME_ASSET_DIR / name).is_file()
    ]
    if missing:
        raise FileNotFoundError(f"Course-home preflight missing assets: {missing}")


def canvas_icon_urls(files: dict[str, dict]) -> dict[str, str]:
    return {
        key: f"/courses/{COURSE_ID}/files/{files[key]['id']}/preview"
        for key in HOME_ASSETS
    }


async def upload_home_assets(client: httpx.AsyncClient) -> tuple[dict, dict[str, dict]]:
    folder = await common.ensure_folder(client, HOME_ASSET_FOLDER)
    files = {
        key: await common.upload(client, HOME_ASSET_DIR / filename, HOME_ASSET_FOLDER)
        for key, filename in HOME_ASSETS.items()
    }
    # The shared upload helpers correctly lock instructional and licensed files,
    # but these four images are part of the published course home. Canvas checks
    # the whole folder chain when a student requests an image, so both Course
    # Home and its CCR Materials parent must be visible. Child six-weeks folders
    # retain their own locks and module publication is not changed here.
    parent = await common.api(client, "GET", f"/folders/{folder['parent_folder_id']}")
    visible_folders: dict[int, dict] = {}
    for current in (parent, folder):
        if current.get("locked") or current.get("hidden"):
            current = await common.api(
                client,
                "PUT",
                f"/folders/{current['id']}",
                data={"locked": "false", "hidden": "false"},
            )
        if current.get("locked") or current.get("hidden"):
            raise RuntimeError(
                f"Canvas did not publish course-home folder "
                f"{current.get('full_name') or current['id']}"
            )
        visible_folders[current["id"]] = current

    visible_files: dict[str, dict] = {}
    for key, file in files.items():
        if file.get("locked") or file.get("hidden"):
            file = await common.api(
                client,
                "PUT",
                f"/files/{file['id']}",
                data={"locked": "false", "hidden": "false"},
            )
        if file.get("locked") or file.get("hidden"):
            raise RuntimeError(
                f"Canvas did not publish course-home file "
                f"{file.get('display_name') or file['id']}"
            )
        visible_files[key] = file

    return visible_folders[folder["id"]], visible_files


def shell(title: str, subtitle: str, color: str, body: str) -> str:
    return f"""
<div style="max-width:900px;margin:0 auto;font-family:Arial,Helvetica,sans-serif;color:#202124;line-height:1.55">
  <div style="background:{color};color:#fff;padding:28px 30px;border-radius:14px;margin-bottom:20px">
    <h2 style="margin:0 0 6px;font-size:30px;line-height:1.2">{title}</h2>
    <p style="margin:0;font-size:17px">{subtitle}</p>
  </div>
  {body}
</div>
""".strip()


def panel(title: str, body: str, color: str = "#5a2d91") -> str:
    return f"""
<section style="border:1px solid #d8d8d8;border-left:7px solid {color};border-radius:10px;padding:18px 20px;margin:18px 0;background:#fff">
  <h2 style="margin:0 0 10px;color:{color};font-size:23px">{title}</h2>
  {body}
</section>
""".strip()


def teacher_body(student_url: str) -> str:
    student_link = f"/courses/{COURSE_ID}/pages/{student_url}"
    return shell(
        "CCE Course Launch Guide",
        "The shortest reliable path from an unpublished build to a classroom-ready course.",
        "#4b287d",
        panel(
            "Before the course opens",
            """
<ol>
  <li><strong>Stay in Modules.</strong> Confirm that every week opens with Day 1-5 headers and paired Teacher/Student guides.</li>
  <li><strong>Keep the review boundary.</strong> Do not use Publish All. Open only the weeks students need, after Student View passes.</li>
  <li><strong>Check the gradebook.</strong> Minor Assessments = 40% with three entries; Major Assessments = 60% with two entries. Practice, draft, recovery, Xello clicks, and equipment success are not extra grades.</li>
  <li><strong>Test required access.</strong> Open Xello through the student route and confirm Completion Standards/reporting. H&amp;L and eDynamic are supplemental unless the lesson names a verified job for them.</li>
  <li><strong>Check the room.</strong> Confirm devices, charging, consumables, safety procedures, and the equal low-tech route named in the Teacher Guide.</li>
</ol>
""",
            "#4b287d",
        )
        + panel(
            "How one instructional day works",
            """
<ol>
  <li>Open the <strong>Teacher Facilitator Guide</strong> before class. Its first screen names prep, evidence, the 50-minute flow, and the trim point.</li>
  <li>Students open the matching <strong>Student Guide</strong>. Required directions stay visible; disclosures hold optional examples, vocabulary, or catch-up help.</li>
  <li>Students complete one durable evidence job through the named Canvas interaction, approved platform, or equal paper route.</li>
  <li>Use the exit check to decide tomorrow's support. Do not turn every exit ticket into a separate grade.</li>
</ol>
""",
            "#166c7d",
        )
        + panel(
            "Publication sequence",
            """
<ol>
  <li>Run the importer and read-only module verifier.</li>
  <li>Open the Teacher and Student pages, linked files, Quiz/Assignment/Discussion, and any licensed visual.</li>
  <li>Check desktop and a 390-pixel viewport. Verify headings, alt text, keyboard route, captions/transcript, response space, and no horizontal overflow.</li>
  <li>Enter Student View. Prove the module route, file opening, submission instructions, absence route, and privacy boundary.</li>
  <li>Publish only the reviewed student-facing items and week. Teacher Build and teacher-only resources remain unpublished.</li>
</ol>
""",
            "#2f7d32",
        )
        + panel(
            "When the planned route fails",
            """
<ul>
  <li><strong>Canvas:</strong> use the verified paper/download route and accept later upload without penalty.</li>
  <li><strong>Xello:</strong> continue the reflection or scaffold, record supervised catch-up, and do not claim paper as platform completion.</li>
  <li><strong>Equipment:</strong> grade the same planning, evidence, design, or analysis—not fabrication or device success.</li>
  <li><strong>Partner or prior artifact:</strong> use the individual/absence route supplied in the page and packet.</li>
</ul>
""",
            "#a05a00",
        )
        + f"""
<p style="margin:22px 0"><a href="{student_link}" style="display:inline-block;background:#166c7d;color:#fff;text-decoration:none;padding:12px 18px;border-radius:8px;font-weight:700">Open the matching Student Start Here page</a></p>
<details style="border:1px solid #d8d8d8;border-radius:10px;padding:12px 16px;margin:18px 0">
  <summary style="font-weight:700;cursor:pointer">Optional integrations currently visible in this course</summary>
  <p>Canvas Studio, Canva for Education, Lucid Whiteboard, Office 365, Collaborations, Zoom, and other district tools appear in instructor navigation. Presence does not prove student provisioning, privacy fit, accessibility, mobile behavior, or grade passback. Pilot before requiring any integration.</p>
</details>
<details style="border:1px solid #d8d8d8;border-radius:10px;padding:12px 16px;margin:18px 0">
  <summary style="font-weight:700;cursor:pointer">Teacher feedback record</summary>
  <p>After teaching, record the actual setup time, timing/trim decision, student confusion point, access failure, strongest evidence, and one change worth carrying forward. Classroom evidence should revise the course; novelty alone should not.</p>
</details>
""",
    )


def student_body() -> str:
    return shell(
        "Start Here: How CCE Works",
        "One clear route for class, catch-up, and showing what you know.",
        "#166c7d",
        """
<section style="background:#eef7f8;border-radius:10px;padding:18px 20px;margin:18px 0">
  <h2 style="margin:0 0 8px;color:#166c7d;font-size:23px">Today you will</h2>
  <ul><li>learn where each day's work begins;</li><li>know how to submit work safely;</li><li>know what to do if you are absent or a platform fails.</li></ul>
</section>
"""
        + panel(
            "1. Start in Modules",
            "<p>Open the current six-weeks module, then the current week. Each day has a Day header, a Student Guide, and—when needed—one activity. Do not hunt through Files for your directions.</p>",
            "#4b287d",
        )
        + panel(
            "2. Open the Student Guide",
            "<p>Read the purpose, <strong>Today you will</strong>, and <strong>Get ready</strong> sections. Follow the numbered steps in order. Optional help may be inside a disclosure; required directions stay visible.</p>",
            "#166c7d",
        )
        + panel(
            "3. Complete the evidence job",
            """
<p>Your evidence may be a typed response, annotated PDF, uploaded file, short private recording, approved platform task, or paper copy. The guide tells you what counts. Software polish, device success, and public confidence do not replace the learning target.</p>
""",
            "#2f7d32",
        )
        + panel(
            "4. Protect private information",
            """
<ul>
  <li>Do not post private Xello results, family income, health information, passwords, student IDs, or personal contact information.</li>
  <li>Practice applications, messages, budgets, properties, patients, and businesses use fictional or teacher-provided information.</li>
  <li>Use a private submission unless the lesson clearly explains why peer sharing improves the work. A private alternative is available when needed.</li>
</ul>
""",
            "#a05a00",
        )
        + panel(
            "5. If you were absent or a platform failed",
            """
<p>Open the catch-up section in the Student Guide. Use the linked packet, native directions, and individual route. If required Xello work could not be completed, finish the learning scaffold and join the supervised catch-up route; paper does not become a fake Xello completion.</p>
""",
            "#a05a00",
        )
        + """
<section style="background:#f0f7ec;border:1px solid #b9d8a9;border-radius:10px;padding:18px 20px;margin:18px 0">
  <h2 style="margin:0 0 8px;color:#2f6d24;font-size:23px">You are done when</h2>
  <ul>
    <li>you can find today's Student Guide from Modules;</li>
    <li>you know the evidence and submission route;</li>
    <li>you know the privacy boundary;</li>
    <li>you know where to find the absence/platform route.</li>
  </ul>
</section>
<section style="background:#fff7e6;border:1px solid #e7c679;border-radius:10px;padding:18px 20px;margin:18px 0">
  <h2 style="margin:0 0 8px;color:#7a4a00;font-size:23px">Exit check</h2>
  <p>In one sentence: where will you start tomorrow, and what will you check before submitting?</p>
</section>
<details style="border:1px solid #d8d8d8;border-radius:10px;padding:12px 16px;margin:18px 0">
  <summary style="font-weight:700;cursor:pointer">Words you will see often</summary>
  <p><strong>evidence / evidencia:</strong> what shows your thinking or skill · <strong>submit / entregar:</strong> send work privately to the teacher · <strong>revision / revisión:</strong> improve work using evidence or feedback · <strong>fallback / alternativa:</strong> an equal route when the first route is unavailable.</p>
</details>
""",
    )


def home_body(icons: dict[str, str]) -> str:
    modules_url = f"/courses/{COURSE_ID}/modules"
    return f"""
<div style="max-width:860px;margin:0 auto;font-family:Arial,Helvetica,sans-serif;color:#202124;line-height:1.45">
  <header style="padding:8px 0 24px">
    <h2 style="margin:0;font-size:32px;line-height:1.2;color:#202124">Career and College Exploration</h2>
  </header>
  <section aria-labelledby="cce-start-title" style="margin:0 0 34px">
    <a href="{modules_url}" style="display:flex;align-items:center;gap:18px;background:#26364d;color:#fff;text-decoration:none;padding:20px 22px;border:1px solid #26364d;border-radius:10px">
      <img src="{icons['modules']}" alt="" style="display:block;width:64px;height:64px;flex:0 0 64px" />
      <span style="display:block;min-width:0;flex:1 1 auto">
        <strong id="cce-start-title" style="display:block;font-size:24px;line-height:1.2">Open Modules</strong>
        <span style="display:block;margin-top:4px;font-size:16px">Start today's lesson.</span>
      </span>
      <span aria-hidden="true" style="font-size:28px;line-height:1">&#8594;</span>
    </a>
  </section>
  <section aria-labelledby="cce-tools-title">
    <h2 id="cce-tools-title" style="margin:0 0 4px;font-size:24px;line-height:1.3;color:#202124">Course tools</h2>
    <ul style="list-style:none;margin:0;padding:0;border-top:1px solid #d6d9dd">
      <li style="margin:0;border-bottom:1px solid #d6d9dd">
        <a href="{ONENOTE_URL}" target="_blank" rel="noopener" style="display:flex;align-items:center;gap:20px;padding:20px 4px;color:#202124;text-decoration:none">
          <span style="display:block;flex:0 1 190px;min-width:120px"><img src="{icons['onenote']}" alt="" style="display:block;width:100%;max-width:180px;height:auto" /></span>
          <span style="display:block;flex:1 1 auto;min-width:0"><strong style="display:block;font-size:19px">Open OneNote</strong><span style="display:block;margin-top:2px;color:#5f6368;font-size:15px">CCE notebook</span></span>
          <span aria-hidden="true" style="font-size:24px;line-height:1;color:#4b5563">&#8594;</span>
        </a>
      </li>
      <li style="margin:0;border-bottom:1px solid #d6d9dd">
        <a href="{HATS_LADDERS_URL}" target="_blank" rel="noopener" style="display:flex;align-items:center;gap:20px;padding:20px 4px;color:#202124;text-decoration:none">
          <span style="display:block;flex:0 1 190px;min-width:120px"><img src="{icons['hats_ladders']}" alt="" style="display:block;width:100%;max-width:180px;height:auto" /></span>
          <span style="display:block;flex:1 1 auto;min-width:0"><strong style="display:block;font-size:19px">Open Hats &amp; Ladders</strong><span style="display:block;margin-top:2px;color:#5f6368;font-size:15px">Sign in with Google.</span></span>
          <span aria-hidden="true" style="font-size:24px;line-height:1;color:#4b5563">&#8594;</span>
        </a>
      </li>
      <li style="margin:0;border-bottom:1px solid #d6d9dd">
        <a href="{CLASSLINK_URL}" target="_blank" rel="noopener" style="display:flex;align-items:center;gap:20px;padding:20px 4px;color:#202124;text-decoration:none">
          <span style="display:block;flex:0 1 190px;min-width:120px"><img src="{icons['xello']}" alt="" style="display:block;width:100%;max-width:180px;height:auto" /></span>
          <span style="display:block;flex:1 1 auto;min-width:0"><strong style="display:block;font-size:19px">Open Xello</strong><span style="display:block;margin-top:2px;color:#5f6368;font-size:15px">Use ClassLink.</span></span>
          <span aria-hidden="true" style="font-size:24px;line-height:1;color:#4b5563">&#8594;</span>
        </a>
      </li>
    </ul>
  </section>
  <section aria-labelledby="cce-course-title" style="margin:38px 0 0;padding-top:28px;border-top:1px solid #d6d9dd">
    <h2 id="cce-course-title" style="margin:0 0 10px;font-size:24px;line-height:1.3;color:#202124">About this course</h2>
    <p style="margin:0;font-size:16px;color:#3c4043">Career and College Exploration is a Grade 7 course. You will learn how your interests and skills connect to careers. You will compare ways to prepare for work, practice useful skills, and make a plan that can change as you learn more.</p>
    <ul style="margin:14px 0 0;padding-left:22px;color:#3c4043;font-size:16px">
      <li style="margin:6px 0">Explore career clusters and jobs.</li>
      <li style="margin:6px 0">Compare high school, college, and training options.</li>
      <li style="margin:6px 0">Practice research, communication, planning, and teamwork.</li>
    </ul>
  </section>
  <section aria-labelledby="cce-teacher-title" style="margin:32px 0 0;padding-top:28px;border-top:1px solid #d6d9dd">
    <h2 id="cce-teacher-title" style="margin:0 0 10px;font-size:24px;line-height:1.3;color:#202124">About Ms. Lucero</h2>
    <p style="margin:0;font-size:16px;color:#3c4043">I am Ms. Lucero, Bowie Middle School's Teacher of the Year and a district finalist. I studied Cognitive Systems at UBC, the University of British Columbia. The program combines AI, computers, and how people think. I like technology and cats in equal measure.</p>
    <p style="margin:12px 0 0;font-size:16px"><a href="mailto:{TEACHER_EMAIL}" style="color:#245493">{TEACHER_EMAIL}</a></p>
  </section>
</div>
""".strip()


async def find_or_create_module(client: httpx.AsyncClient, name: str) -> dict:
    modules = await common.paged(client, f"/courses/{COURSE_ID}/modules")
    found = next((module for module in modules if module.get("name") == name), None)
    data = {"module[published]": "false"}
    if found:
        return await common.api(
            client, "PUT", f"/courses/{COURSE_ID}/modules/{found['id']}", data=data
        )
    data["module[name]"] = name
    return await common.api(client, "POST", f"/courses/{COURSE_ID}/modules", data=data)


def page_state(page: dict) -> dict:
    return {
        "page_id": page.get("page_id"),
        "url": page.get("url"),
        "title": page.get("title"),
        "published": page.get("published"),
        "front_page": page.get("front_page"),
        "editing_roles": page.get("editing_roles"),
    }


async def stage_home_only(client: httpx.AsyncClient) -> dict:
    """Update the replacement home and make it the default without changing publication."""

    preflight_home_assets()
    course_before = await common.api(client, "GET", f"/courses/{COURSE_ID}")
    if course_before.get("id") != COURSE_ID:
        raise RuntimeError(f"Course preflight resolved unexpected id {course_before.get('id')}")

    pages = await common.paged(client, f"/courses/{COURSE_ID}/pages")
    home_matches = [page for page in pages if page.get("title") == HOME_TITLE]
    if len(home_matches) != 1:
        raise RuntimeError(f"Expected one existing page {HOME_TITLE!r}; found {len(home_matches)}")

    home_before = await common.api(
        client, "GET", f"/courses/{COURSE_ID}/pages/{home_matches[0]['url']}"
    )
    front_before = await common.api(client, "GET", f"/courses/{COURSE_ID}/front_page")
    before_state = page_state(home_before)
    front_state = page_state(front_before)
    course_state = {
        "id": course_before.get("id"),
        "name": course_before.get("name"),
        "default_view": course_before.get("default_view"),
        "workflow_state": course_before.get("workflow_state"),
    }

    folder, files = await upload_home_assets(client)
    body = home_body(canvas_icon_urls(files))
    await common.api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/pages/{home_before['url']}",
        data={"wiki_page[body]": body},
    )
    can_set_front_page = bool(home_before.get("published"))
    if can_set_front_page:
        await common.api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/pages/{home_before['url']}",
            data={"wiki_page[front_page]": "true"},
        )
        await common.api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}",
            data={"course[default_view]": "wiki"},
        )

    course_after = await common.api(client, "GET", f"/courses/{COURSE_ID}")
    home_after = await common.api(
        client, "GET", f"/courses/{COURSE_ID}/pages/{home_before['url']}"
    )
    front_after = await common.api(client, "GET", f"/courses/{COURSE_ID}/front_page")
    after_state = page_state(home_after)
    final_course_state = {
        "id": course_after.get("id"),
        "name": course_after.get("name"),
        "default_view": course_after.get("default_view"),
        "workflow_state": course_after.get("workflow_state"),
    }
    expected_home_state = dict(before_state)
    if can_set_front_page:
        expected_home_state["front_page"] = True
    if after_state != expected_home_state:
        raise RuntimeError(
            "Course-home state did not match the approved front-page change: "
            f"expected={expected_home_state}, after={after_state}"
        )
    old_front_after = None
    if can_set_front_page and page_state(front_after) != after_state:
        raise RuntimeError("Canvas did not resolve the replacement home as its active front page")
    if can_set_front_page and front_state.get("url") != before_state.get("url"):
        old_front_after = await common.api(
            client, "GET", f"/courses/{COURSE_ID}/pages/{front_state['url']}"
        )
        old_front_state = page_state(old_front_after)
        expected_old_front_state = dict(front_state)
        expected_old_front_state["front_page"] = False
        if old_front_state != expected_old_front_state:
            raise RuntimeError(
                "Previous front-page state changed beyond removing its front-page designation: "
                f"expected={expected_old_front_state}, after={old_front_state}"
            )
    if not can_set_front_page and page_state(front_after) != front_state:
        raise RuntimeError("Active front-page state changed during the body-only update")
    expected_course_state = dict(course_state)
    if can_set_front_page:
        expected_course_state["default_view"] = "wiki"
    if final_course_state != expected_course_state:
        raise RuntimeError(
            "Course state changed beyond the approved wiki default: "
            f"expected={expected_course_state}, after={final_course_state}"
        )

    required_links = {
        f"/courses/{COURSE_ID}/modules",
        ONENOTE_URL,
        HATS_LADDERS_URL,
        CLASSLINK_URL,
        f"mailto:{TEACHER_EMAIL}",
    }
    final_body = home_after.get("body") or ""
    missing_links = sorted(link for link in required_links if link not in final_body)
    missing_files = sorted(
        file["id"] for file in files.values() if f"/files/{file['id']}/preview" not in final_body
    )
    if missing_links or missing_files:
        raise RuntimeError(
            f"Course-home saved-body verification failed: missing_links={missing_links}, missing_files={missing_files}"
        )
    if folder.get("locked") or folder.get("hidden"):
        raise RuntimeError("Course-home folder is not student-visible")
    if any(file.get("locked") or file.get("hidden") for file in files.values()):
        raise RuntimeError("Course-home icon file is not student-visible")

    return {
        "course": final_course_state,
        "replacement_home": after_state,
        "active_front_page": page_state(front_after),
        "previous_front_page": page_state(old_front_after) if old_front_after else None,
        "folder": {
            "id": folder.get("id"),
            "full_name": folder.get("full_name"),
            "locked": folder.get("locked"),
            "hidden": folder.get("hidden"),
        },
        "files": {
            key: {
                "id": file.get("id"),
                "display_name": file.get("display_name"),
                "locked": file.get("locked"),
                "hidden": file.get("hidden"),
            }
            for key, file in files.items()
        },
        "publication_state_preserved": True,
        "replacement_home_is_front_page": bool(after_state.get("front_page")),
        "default_view_is_wiki": final_course_state.get("default_view") == "wiki",
        "owner_action_required": (
            None
            if can_set_front_page
            else "Publish this page in Canvas, then rerun --home-only to make it the front page."
        ),
    }


async def main() -> None:
    if sys.argv[1:] not in ([], ["--home-only"]):
        raise SystemExit("usage: build_course_orientation.py [--home-only]")
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as client:
        if sys.argv[1:] == ["--home-only"]:
            print(json.dumps(await stage_home_only(client), indent=2))
            return
        preflight_home_assets()
        orientation_module = await find_or_create_module(client, ORIENTATION_MODULE)
        teacher_module = await find_or_create_module(client, TEACHER_MODULE)
        student_page = await common.upsert_page(client, STUDENT_TITLE, student_body())
        teacher_page = await common.upsert_page(
            client, TEACHER_TITLE, teacher_body(student_page["url"])
        )
        _, home_files = await upload_home_assets(client)
        home_page = await common.upsert_page(
            client,
            HOME_TITLE,
            home_body(canvas_icon_urls(home_files)),
        )
        student_item = await common.upsert_item(
            client,
            orientation_module["id"],
            "Page",
            student_page["url"],
            STUDENT_TITLE,
        )
        teacher_item = await common.upsert_item(
            client, teacher_module["id"], "Page", teacher_page["url"], TEACHER_TITLE
        )
        await common.api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{orientation_module['id']}",
            data={"module[position]": "1", "module[published]": "false"},
        )
        await common.api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{orientation_module['id']}/items/{student_item['id']}",
            data={"module_item[position]": "1"},
        )
        await common.api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{teacher_module['id']}/items/{teacher_item['id']}",
            data={"module_item[position]": "1"},
        )
        print(
            json.dumps(
                {
                    "module": {
                        "id": orientation_module["id"],
                        "name": ORIENTATION_MODULE,
                        "published": False,
                    },
                    "teacher_module": {
                        "id": teacher_module["id"],
                        "name": TEACHER_MODULE,
                        "published": False,
                    },
                    "pages": {
                        "teacher": teacher_page,
                        "student": student_page,
                        "home": home_page,
                    },
                    "items": [student_item, teacher_item],
                }
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
