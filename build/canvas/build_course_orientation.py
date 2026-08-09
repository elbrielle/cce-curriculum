#!/usr/bin/env python3
"""Build unpublished teacher and student course-orientation pages in Canvas."""

from __future__ import annotations

import asyncio
import json
import sys

import build_4sw_wk1 as common
import httpx

COURSE_ID = common.COURSE_ID
ORIENTATION_MODULE = "START HERE: CCE Course Orientation"
TEACHER_MODULE = "Teacher Build: Licensed Resources"
TEACHER_TITLE = "TEACHER: CCE Course Launch Guide"
STUDENT_TITLE = "STUDENT: Start Here - How CCE Works"
HOME_TITLE = "Career and College Exploration Home"


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


def home_body(student_url: str) -> str:
    modules_url = f"/courses/{COURSE_ID}/modules"
    student_link = f"/courses/{COURSE_ID}/pages/{student_url}"
    grades_url = f"/courses/{COURSE_ID}/grades"
    return shell(
        "Career and College Exploration",
        "Explore careers, practice workplace skills, and build evidence for your next step.",
        "#4b287d",
        f"""
<section style="background:#eef7f8;border:1px solid #b7d9de;border-radius:12px;padding:22px;margin:18px 0">
  <h2 style="margin:0 0 8px;color:#166c7d;font-size:25px">Start today's lesson</h2>
  <p style="margin:0 0 16px">Open Modules, choose the current six-weeks and week, then start with today's Student Guide.</p>
  <p style="margin:0"><a href="{modules_url}" style="display:inline-block;background:#166c7d;color:#fff;text-decoration:none;padding:13px 18px;border-radius:8px;font-weight:700">Open Course Modules</a></p>
</section>
"""
        + panel(
            "How this course works",
            f"""
<p>Each week follows one route: Day header → Student Guide → activity. The guide tells you what to do, what counts as evidence, and how to submit it.</p>
<p><a href="{student_link}">Read the Start Here guide</a> for privacy, submission, and platform-fallback directions.</p>
""",
            "#4b287d",
        )
        + panel(
            "If you were absent or technology failed",
            """
<p>Open the current Student Guide and use its absence or platform route. Complete the same learning evidence through the named individual, paper, typed, or teacher-approved option. Required Xello completion moves to supervised catch-up when Xello is unavailable.</p>
""",
            "#a05a00",
        )
        + panel(
            "Grades and feedback",
            f"""
<p>Practice and exit checks help you improve; they are not automatically separate grades. Each six-weeks uses three Minor Assessments and two Major Assessments. Open <a href="{grades_url}">Grades</a> for posted feedback and scores.</p>
""",
            "#2f7d32",
        )
        + """
<section style="background:#fff7e6;border:1px solid #e7c679;border-radius:10px;padding:18px 20px;margin:18px 0">
  <h2 style="margin:0 0 8px;color:#7a4a00;font-size:23px">Keep private information private</h2>
  <p style="margin:0">Do not post passwords, student IDs, private Xello results, family finances, health information, or personal contact information. Use fictional or teacher-provided information in practice tasks.</p>
</section>
""",
    )


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


async def main() -> None:
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as client:
        orientation_module = await find_or_create_module(client, ORIENTATION_MODULE)
        teacher_module = await find_or_create_module(client, TEACHER_MODULE)
        student_page = await common.upsert_page(client, STUDENT_TITLE, student_body())
        teacher_page = await common.upsert_page(
            client, TEACHER_TITLE, teacher_body(student_page["url"])
        )
        home_page = await common.upsert_page(
            client, HOME_TITLE, home_body(student_page["url"])
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
