#!/usr/bin/env python3
"""Stage the approved 3-minor/2-major assessment map in Canvas.

The script reads a Canvas token from stdin, keeps every mapped assignment
unpublished, and is idempotent. It creates missing gradebook assignments,
renames known draft aliases, assigns 100 points, and places assignments in the
40/60 groups. It does not publish, set due dates, or fabricate rubric criteria.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import httpx

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
ROOT = Path(__file__).resolve().parents[2]
MAP_PATH = ROOT / "docs/resources/six-weeks-assessment-map.md"


MINOR_GROUP = "Minor Assessments (40%)"
MAJOR_GROUP = "Major Assessments (60%)"
SUBMISSION_LINK_MARKER = "cce-mapped-assignment-link-v1"


@dataclass(frozen=True)
class Assessment:
    module: str
    title: str
    group: str
    day: int
    aliases: tuple[str, ...] = ()


ASSESSMENTS = (
    Assessment(
        "1SW Wk0: Classroom Routines and Career Self-Discovery",
        "MINOR 1: My Career Journey Reflection",
        MINOR_GROUP,
        4,
    ),
    Assessment(
        "1SW Wk2: Code Your Future - Programming Careers in IT",
        "MINOR 2: IT Salary Comparison and Career-Fit Reflection",
        MINOR_GROUP,
        5,
    ),
    Assessment(
        "1SW Wk4: Help Desk Heroes - Tech Support Careers and MakeCode",
        "MINOR 3: Help Desk Program Evidence and Career Connection",
        MINOR_GROUP,
        5,
    ),
    Assessment(
        "1SW Wk3: Network Ninjas - Computer Science and Networking Careers",
        "MAJOR 1: App Design and Emerging-Career Evidence Packet",
        MAJOR_GROUP,
        5,
    ),
    Assessment(
        "1SW Wk5: Cyber Defenders - Cybersecurity Careers and Capstone",
        "MAJOR 2: Cybersecurity Capstone Evidence Portfolio",
        MAJOR_GROUP,
        5,
    ),
    Assessment(
        "2SW Wk3: Nursing Science - Routes, Simulation, and Handoff",
        "MINOR 1: Nursing Route and Handoff",
        MINOR_GROUP,
        5,
    ),
    Assessment(
        "2SW Wk4: Smile Squad - Dental Science and Health Data",
        "MINOR 2: Health Career Evidence Check",
        MINOR_GROUP,
        5,
    ),
    Assessment(
        "2SW Wk5: Communication and Goal Setting",
        "MINOR 3: Communication and Goal Synthesis",
        MINOR_GROUP,
        5,
    ),
    Assessment(
        "2SW Wk1: Legal Studies and Policy Evidence",
        "MAJOR 1: Legal Policy Position Evidence",
        MAJOR_GROUP,
        5,
    ),
    Assessment(
        "2SW Wk2: First Responders - Evidence, Response, and Handoff",
        "MAJOR 2: Patient Care Report and Complication Plan",
        MAJOR_GROUP,
        5,
    ),
    Assessment(
        "3SW Wk1: Veterinary Science",
        "MINOR 1: Veterinary Pathway Evidence Packet",
        MINOR_GROUP,
        5,
    ),
    Assessment(
        "3SW Wk4: Culinary Arts and Hospitality",
        "MINOR 2: Hospitality Career and Business Recommendation",
        MINOR_GROUP,
        5,
        ("PRACTICE: Hospitality Career and Business Recommendation",),
    ),
    Assessment(
        "3SW Wk5: Style, Service, and Cosmetology Careers",
        "MINOR 3: Cosmetology Career and Business Recommendation",
        MINOR_GROUP,
        5,
        ("PRACTICE: Cosmetology Career and Business Recommendation",),
    ),
    Assessment(
        "3SW Wk2: Plant Science and Agricultural Communication",
        "MAJOR 1: Farm-to-Table and Emerging Plant-Tech Evidence",
        MAJOR_GROUP,
        5,
        ("PRACTICE: Plant Science Evidence Packet",),
    ),
    Assessment(
        "3SW Wk3: Sustainable Engineering and Pest Patrol",
        "MAJOR 2: Sustainable Engineering Design and Trends Evidence",
        MAJOR_GROUP,
        5,
        ("PRACTICE: Sustainable Engineering Evidence Packet",),
    ),
    Assessment(
        "4SW Wk3: Aviation Routes, Systems, and Action Planning",
        "MINOR 1: Aviation Route and Action Plan",
        MINOR_GROUP,
        5,
        ("DRAFT: Aviation Route and Action Plan",),
    ),
    Assessment(
        "4SW Wk4: Drone Systems, Rules, and Iteration",
        "MINOR 2: Drone Systems Evidence Brief",
        MINOR_GROUP,
        5,
        ("DRAFT: Drone Systems Evidence Brief",),
    ),
    Assessment(
        "4SW Wk5: Automotive Evidence and Training Routes",
        "MINOR 3: Automotive Evidence Brief",
        MINOR_GROUP,
        5,
        ("DRAFT: Automotive Evidence Brief",),
    ),
    Assessment(
        "4SW Wk1: Build Your Mid-Year Career Blueprint",
        "MAJOR 1: Mid-Year Career Blueprint",
        MAJOR_GROUP,
        5,
        ("DRAFT: Mid-Year Career Blueprint",),
    ),
    Assessment(
        "4SW Wk2: Build a Counseling-Ready High School Plan",
        "MAJOR 2: Individual High School and Career Plan",
        MAJOR_GROUP,
        5,
        ("DRAFT: Individual High School and Career Plan",),
    ),
    Assessment(
        "5SW Wk1: Blueprint Builders — Architecture Evidence",
        "MINOR 1: Three-Career Architecture Comparison",
        MINOR_GROUP,
        2,
    ),
    Assessment(
        "5SW Wk2: Civil Engineering — Systems, Evidence, and Design",
        "MINOR 2: Assessment and Emerging-Specialty Evidence",
        MINOR_GROUP,
        2,
    ),
    Assessment(
        "5SW Wk3: Construction — Routes, Evidence, and Observation",
        "MINOR 3: Construction Labor-Evidence Classification",
        MINOR_GROUP,
        3,
        ("MINOR 3: Construction Labor-Market Classification",),
    ),
    Assessment(
        "5SW Wk4: Skilled Trades — Evidence, Routes, and Communication",
        "MAJOR 1: Skilled-Trades Classification and Individual Response",
        MAJOR_GROUP,
        5,
        ("MAJOR 1B: Fictional Water-Line Response and Briefing",),
    ),
    Assessment(
        "5SW Wk5: MoneySkills — Budget, Location, and Career Evidence",
        "MAJOR 2: Personal Budget Evidence Portfolio",
        MAJOR_GROUP,
        5,
        ("MAJOR 2: Personal Budget and Career Evidence Portfolio",),
    ),
    Assessment(
        "6SW Wk1: Education — Learning Design, Routes, and Service",
        "MINOR 1: Education Evidence Portfolio",
        MINOR_GROUP,
        5,
        ("MINOR 1: Education Career Evidence Portfolio",),
    ),
    Assessment(
        "6SW Wk2: Arts/AV — First Resume and Design Evidence",
        "MINOR 2: Resume, Revision, and Job-Search Evidence",
        MINOR_GROUP,
        5,
        ("MINOR 2: Resume and Merch Design Evidence",),
    ),
    Assessment(
        "6SW Wk3: Marketing - Audience, Entrepreneurship, and Data",
        "MINOR 3: Ethical Marketing Evidence Brief",
        MINOR_GROUP,
        5,
        ("MINOR 3: Marketing Evidence Brief",),
    ),
    Assessment(
        "6SW Wk5: Job Search, Applications, and Interviews",
        "MAJOR 1: Job Skills, Application, and Mock Interview Portfolio",
        MAJOR_GROUP,
        5,
        ("MAJOR 1: Mock Interview and Follow-Up",),
    ),
    Assessment(
        "6SW Wk6: Career Evidence Capstone",
        "MAJOR 2: Individual Career Plan and Communicated Capstone",
        MAJOR_GROUP,
        4,
        ("MAJOR 2: Communicated Career Capstone",),
    ),
)


async def api(client: httpx.AsyncClient, method: str, path: str, *, data=None):
    response = await client.request(method, f"{BASE}/api/v1{path}", data=data)
    response.raise_for_status()
    return response.json() if response.content else None


async def paged(client: httpx.AsyncClient, path: str) -> list[dict]:
    records, url = [], f"{BASE}/api/v1{path}"
    params = {"per_page": 100}
    while url:
        response = await client.get(url, params=params)
        response.raise_for_status()
        records.extend(response.json())
        url = response.links.get("next", {}).get("url")
        params = None
    return records


async def ensure_group(client, groups: list[dict], name: str, weight: int) -> dict:
    matches = [group for group in groups if group.get("name") == name]
    if len(matches) > 1:
        raise ValueError(f"duplicate assignment group {name!r}")
    data = {
        "name": name,
        "group_weight": str(weight),
        "position": "1" if weight == 40 else "2",
    }
    if matches:
        return await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/assignment_groups/{matches[0]['id']}",
            data=data,
        )
    return await api(
        client, "POST", f"/courses/{COURSE_ID}/assignment_groups", data=data
    )


def default_description(assessment: Assessment) -> str:
    label = "Minor" if assessment.group == MINOR_GROUP else "Major"
    return (
        f"<p><strong>Mapped {label} assessment.</strong> Submit the evidence named in "
        "the matching Student Guide through private text, file upload, approved media, "
        "or the documented paper route. Use the student-visible scoring tool before "
        "submitting. This assignment remains unpublished until its rubric, absence "
        "route, and Student View check pass.</p>"
    )


async def ensure_student_submission_link(
    client, student_item: dict, assignment: dict, assessment: Assessment
) -> None:
    """Add one visible, repeat-safe submission route to the matching Student Guide."""
    page_url = student_item.get("page_url")
    if not page_url:
        raise ValueError(f"student page URL missing for {assessment.title!r}")
    page = await api(client, "GET", f"/courses/{COURSE_ID}/pages/{page_url}")
    body = page.get("body") or ""
    body = re.sub(
        rf'\s*<section[^>]+data-cce-marker="{SUBMISSION_LINK_MARKER}"[\s\S]*?</section>',
        "",
        body,
    ).rstrip()
    label = "minor" if assessment.group == MINOR_GROUP else "major"
    panel = (
        f'<section data-cce-marker="{SUBMISSION_LINK_MARKER}" '
        'style="border:2px solid #1f617a;border-radius:12px;padding:18px 20px;'
        'margin:24px 0;background:#f2f8fb">'
        f'<h3 style="margin:0 0 8px;color:#1f617a">Submit your {label} evidence</h3>'
        '<p style="margin:0 0 14px">Use the scoring tool to check your work, then '
        'submit through this private Canvas assignment. Your teacher will tell you '
        'whether to type, upload a file, record approved media, or turn in the paper route.</p>'
        f'<p style="margin:0"><a href="/courses/{COURSE_ID}/assignments/{assignment["id"]}" '
        'style="display:inline-block;background:#1f617a;color:#fff;padding:11px 18px;'
        'border-radius:6px;text-decoration:none;font-weight:700" '
        f'data-api-endpoint="/api/v1/courses/{COURSE_ID}/assignments/{assignment["id"]}" '
        'data-api-returntype="Assignment">'
        f'Open {assessment.title}</a></p></section>'
    )
    await api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/pages/{page_url}",
        data={
            "wiki_page[title]": page["title"],
            "wiki_page[body]": f"{body}\n{panel}",
            "wiki_page[published]": "false",
            "wiki_page[editing_roles]": "teachers",
        },
    )


async def ensure_module_item(
    client, module: dict, assignment: dict, assessment: Assessment
) -> None:
    items = await paged(client, f"/courses/{COURSE_ID}/modules/{module['id']}/items")
    student = next(
        (
            item
            for item in items
            if item.get("type") == "Page"
            and (item.get("title") or "").startswith("STUDENT:")
            and f"Day {assessment.day}" in (item.get("title") or "")
        ),
        None,
    )
    if not student:
        raise ValueError(
            f"student Day {assessment.day} page not found in {assessment.module}"
        )
    found = next(
        (
            item
            for item in items
            if item.get("type") == "Assignment"
            and item.get("content_id") == assignment["id"]
        ),
        None,
    )
    if found:
        await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/modules/{module['id']}/items/{found['id']}",
            data={"module_item[title]": assessment.title},
        )
        await ensure_student_submission_link(client, student, assignment, assessment)
        return
    created = await api(
        client,
        "POST",
        f"/courses/{COURSE_ID}/modules/{module['id']}/items",
        data={
            "module_item[type]": "Assignment",
            "module_item[content_id]": str(assignment["id"]),
            "module_item[title]": assessment.title,
        },
    )
    await api(
        client,
        "PUT",
        f"/courses/{COURSE_ID}/modules/{module['id']}/items/{created['id']}",
        data={"module_item[position]": str(student["position"] + 1)},
    )
    await ensure_student_submission_link(client, student, assignment, assessment)


async def run(token: str) -> dict:
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=90
    ) as client:
        modules = await paged(client, f"/courses/{COURSE_ID}/modules")
        modules_by_name: dict[str, list[dict]] = {}
        for module in modules:
            modules_by_name.setdefault(module.get("name") or "", []).append(module)
        assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
        groups = await paged(client, f"/courses/{COURSE_ID}/assignment_groups")
        minor = await ensure_group(client, groups, MINOR_GROUP, 40)
        major = await ensure_group(client, groups, MAJOR_GROUP, 60)
        group_ids = {MINOR_GROUP: minor["id"], MAJOR_GROUP: major["id"]}
        await api(
            client,
            "PUT",
            f"/courses/{COURSE_ID}",
            data={"course[apply_assignment_group_weights]": "true"},
        )

        configured = []
        for assessment in ASSESSMENTS:
            module_matches = modules_by_name.get(assessment.module, [])
            if len(module_matches) != 1 or module_matches[0].get("published"):
                raise ValueError(
                    f"expected one unpublished target module {assessment.module!r}; "
                    f"found {len(module_matches)}"
                )
            module = module_matches[0]
            candidates = [
                entry for entry in assignments if entry.get("name") == assessment.title
            ]
            if not candidates:
                candidates = [
                    entry
                    for entry in assignments
                    if entry.get("name") in assessment.aliases
                ]
            if len(candidates) > 1:
                raise ValueError(
                    f"multiple assignment candidates for {assessment.title!r}"
                )
            existing = candidates[0] if candidates else None
            description = (existing or {}).get("description") or default_description(
                assessment
            )
            data = {
                "assignment[name]": assessment.title,
                "assignment[description]": description,
                "assignment[assignment_group_id]": str(group_ids[assessment.group]),
                "assignment[points_possible]": "100",
                "assignment[grading_type]": "points",
                "assignment[published]": "false",
            }
            if not existing:
                data["assignment[submission_types][]"] = [
                    "online_upload",
                    "online_text_entry",
                    "media_recording",
                ]
            endpoint = (
                f"/courses/{COURSE_ID}/assignments/{existing['id']}"
                if existing
                else f"/courses/{COURSE_ID}/assignments"
            )
            assignment = await api(
                client, "PUT" if existing else "POST", endpoint, data=data
            )
            await ensure_module_item(client, module, assignment, assessment)
            configured.append(
                {
                    "id": assignment["id"],
                    "title": assessment.title,
                    "group": assessment.group,
                    "module": assessment.module,
                }
            )
            assignments.append(assignment) if not existing else None

        return {
            "minor_group": {"id": minor["id"], "weight": 40},
            "major_group": {"id": major["id"], "weight": 60},
            "assignments": configured,
        }


def preflight() -> int:
    titles = [item.title for item in ASSESSMENTS]
    modules = [item.module for item in ASSESSMENTS]
    minors = sum(item.group == MINOR_GROUP for item in ASSESSMENTS)
    majors = sum(item.group == MAJOR_GROUP for item in ASSESSMENTS)
    if (
        len(ASSESSMENTS) != 30
        or len(set(titles)) != 30
        or len(set(modules)) != 30
        or (minors, majors) != (18, 12)
    ):
        print(
            f"Preflight failed: entries={len(ASSESSMENTS)} unique_titles={len(set(titles))} unique_modules={len(set(modules))} minor={minors} major={majors}",
            file=sys.stderr,
        )
        return 2
    documented: dict[str, str] = {}
    six_weeks = None
    for line in MAP_PATH.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"## ([1-6])(?:st|nd|rd|th) Six Weeks", line)
        if heading:
            six_weeks = int(heading.group(1))
            continue
        row = re.match(
            r"\| (Minor|Major) ([1-3]) \| Week ([0-6]) \| ([^|]+?) \|",
            line,
        )
        if not row or six_weeks is None:
            continue
        category, number, week, product = row.groups()
        title = f"{category.upper()} {number}: {product.strip()}"
        documented[title] = f"{six_weeks}SW Wk{week}:"
    configured = {item.title: item.module for item in ASSESSMENTS}
    if set(documented) != set(configured):
        missing = sorted(set(documented) - set(configured))
        extra = sorted(set(configured) - set(documented))
        print(
            f"Preflight failed: assessment-map drift; missing={missing} extra={extra}",
            file=sys.stderr,
        )
        return 2
    wrong_modules = [
        title
        for title, prefix in documented.items()
        if not configured[title].startswith(prefix)
    ]
    if wrong_modules:
        print(
            f"Preflight failed: mapped week mismatch for {wrong_modules}",
            file=sys.stderr,
        )
        return 2
    print("Preflight passed: 30 unique mapped assessments (18 minor, 12 major).")
    return 0


def main() -> int:
    if sys.argv[1:] == ["--preflight"]:
        return preflight()
    if sys.argv[1:]:
        print("usage: configure_assessment_map.py [--preflight]", file=sys.stderr)
        return 2
    token = sys.stdin.readline().strip()
    if not token:
        print("Canvas token required on stdin", file=sys.stderr)
        return 2
    try:
        result = asyncio.run(run(token))
    except (httpx.HTTPError, ValueError) as exc:
        print(f"Assessment-map setup failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
