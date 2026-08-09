#!/usr/bin/env python3
"""Attach student-visible advisory rubrics to the 30 mapped Canvas assessments.

The token is read from stdin. Rubric criteria come from the versioned Markdown
scoring tools, while Canvas assignments remain unpublished and worth 100
gradebook points. Rubric totals are advisory because each raw total must be
converted to a percentage before it is entered in the district gradebook.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from configure_assessment_map import ASSESSMENTS, COURSE_ID


BASE = "https://learn.irvingisd.net"
ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "build/worksheet_sources"
RUBRIC_PREFIX = "CCE | "
NOTE_MARKER = "cce-advisory-rubric-v1"


@dataclass(frozen=True)
class RubricSpec:
    assignment_title: str
    source: str
    points: int


RUBRICS = (
    RubricSpec("MINOR 1: My Career Journey Reflection", "wk0-career-journey-rubric.md", 12),
    RubricSpec("MINOR 2: IT Salary Comparison and Career-Fit Reflection", "wk2-salary-hoc-rubric.md", 20),
    RubricSpec("MINOR 3: Help Desk Program Evidence and Career Connection", "wk4-demo-rubric.md", 16),
    RubricSpec("MAJOR 1: App Design and Emerging-Career Evidence Packet", "wk3-app-design-rubric.md", 16),
    RubricSpec("MAJOR 2: Cybersecurity Capstone Evidence Portfolio", "wk5-capstone-portfolio-rubric.md", 16),
    RubricSpec("MINOR 1: Nursing Route and Handoff", "2sw-wk3-handoff-rubric.md", 16),
    RubricSpec("MINOR 2: Health Career Evidence Check", "2sw-wk4-evidence-check-rubric.md", 16),
    RubricSpec("MINOR 3: Communication and Goal Synthesis", "2sw-wk5-communication-goal-rubric.md", 16),
    RubricSpec("MAJOR 1: Legal Policy Position Evidence", "2sw-wk1-position-paper-rubric.md", 16),
    RubricSpec("MAJOR 2: Patient Care Report and Complication Plan", "2sw-wk2-pcr-rubric.md", 16),
    RubricSpec("MINOR 1: Veterinary Pathway Evidence Packet", "3sw-wk1-veterinary-evidence-rubric.md", 16),
    RubricSpec("MINOR 2: Hospitality Career and Business Recommendation", "3sw-wk4-hospitality-minor-rubric.md", 16),
    RubricSpec("MINOR 3: Cosmetology Career and Business Recommendation", "3sw-wk5-cosmetology-minor-rubric.md", 16),
    RubricSpec("MAJOR 1: Farm-to-Table and Emerging Plant-Tech Evidence", "3sw-wk2-plant-science-major-rubric.md", 16),
    RubricSpec("MAJOR 2: Sustainable Engineering Design and Trends Evidence", "3sw-wk3-sustainable-engineering-major-rubric.md", 16),
    RubricSpec("MINOR 1: Aviation Route and Action Plan", "4sw-wk3-route-action-rubric.md", 16),
    RubricSpec("MINOR 2: Drone Systems Evidence Brief", "4sw-wk4-drone-systems-evidence-rubric.md", 16),
    RubricSpec("MINOR 3: Automotive Evidence Brief", "4sw-wk5-automotive-evidence-rubric.md", 16),
    RubricSpec("MAJOR 1: Mid-Year Career Blueprint", "4sw-wk1-midyear-blueprint-rubric.md", 16),
    RubricSpec("MAJOR 2: Individual High School and Career Plan", "4sw-wk2-high-school-career-plan-rubric.md", 16),
    RubricSpec("MINOR 1: Three-Career Architecture Comparison", "5sw-wk1-architecture-comparison-rubric.md", 16),
    RubricSpec("MINOR 2: Assessment and Emerging-Specialty Evidence", "5sw-wk2-assessment-emerging-rubric.md", 16),
    RubricSpec("MINOR 3: Construction Labor-Evidence Classification", "5sw-wk3-construction-classification-rubric.md", 16),
    RubricSpec("MAJOR 1: Skilled-Trades Classification and Individual Response", "5sw-wk4-skilled-trades-evidence-rubric.md", 16),
    RubricSpec("MAJOR 2: Personal Budget Evidence Portfolio", "5sw-wk5-budget-portfolio-rubric.md", 16),
    RubricSpec("MINOR 1: Education Evidence Portfolio", "6sw-wk1-education-portfolio-rubric.md", 16),
    RubricSpec("MINOR 2: Resume, Revision, and Job-Search Evidence", "6sw-wk2-resume-design-rubric.md", 16),
    RubricSpec("MINOR 3: Ethical Marketing Evidence Brief", "6sw-wk3-marketing-evidence-rubric.md", 16),
    RubricSpec("MAJOR 1: Job Skills, Application, and Mock Interview Portfolio", "6sw-wk5-job-skills-rubric.md", 24),
    RubricSpec("MAJOR 2: Individual Career Plan and Communicated Capstone", "6sw-wk6-capstone-rubric.md", 24),
)


def cells(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def clean_text(value: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("**", "").replace("`", "")
    return re.sub(r"\s+", " ", value).strip()


def rating_points(header: str) -> float:
    explicit = re.search(r"\((\d+(?:\.\d+)?)\s*pts?", header, re.I)
    if explicit:
        return float(explicit.group(1))
    number = re.search(r"(?:^|\s)(\d+(?:\.\d+)?)(?:\s|$)", header)
    if not number:
        raise ValueError(f"rating header has no point value: {header!r}")
    return float(number.group(1))


def frontmatter_title(text: str) -> str:
    match = re.search(r"(?m)^title:\s*(.+?)\s*$", text)
    if not match:
        raise ValueError("rubric source has no title in front matter")
    return match.group(1).strip()


def parse_standard_table(text: str) -> list[dict]:
    lines = text.splitlines()
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if line.lstrip().startswith(("| Criterion |", "| Dimension |"))
        ),
        None,
    )
    if start is None:
        return []
    headers = cells(lines[start])
    if len(headers) < 3:
        raise ValueError("rubric table needs at least two rating columns")
    rows: list[list[str]] = []
    for line in lines[start + 2 :]:
        if not line.lstrip().startswith("|"):
            break
        row = cells(line)
        if len(row) != len(headers):
            raise ValueError(f"rubric row has {len(row)} cells; expected {len(headers)}")
        rows.append(row)
    criteria = []
    for row in rows:
        ratings = []
        for header, detail in zip(headers[1:], row[1:]):
            points = rating_points(header)
            label = clean_text(header)
            ratings.append(
                {
                    "description": label,
                    "long_description": clean_text(detail),
                    "points": points,
                }
            )
        if not any(rating["points"] == 0 for rating in ratings):
            ratings.append(
                {
                    "description": "0 - Insufficient Evidence",
                    "long_description": "Blank, off-topic, copied without evidence, or no assessable submission.",
                    "points": 0.0,
                }
            )
        ratings.sort(key=lambda rating: rating["points"], reverse=True)
        criteria.append(
            {
                "description": clean_text(row[0]),
                "long_description": "Use the evidence descriptor for the selected rating.",
                "points": max(rating["points"] for rating in ratings),
                "ratings": ratings,
            }
        )
    return criteria


def parse_week_zero(text: str) -> list[dict]:
    criteria = []
    parts = re.split(r"(?m)^## Dimension \d+:\s*", text)[1:]
    for part in parts:
        name, _, body = part.partition("\n")
        lines = body.splitlines()
        start = next(
            (index for index, line in enumerate(lines) if line.startswith("| Level |")),
            None,
        )
        if start is None:
            raise ValueError(f"Week 0 dimension {name!r} has no level table")
        ratings = []
        for line in lines[start + 2 :]:
            if not line.startswith("|"):
                break
            row = cells(line)
            if len(row) < 2:
                continue
            ratings.append(
                {
                    "description": clean_text(row[0]),
                    "long_description": clean_text(row[1]),
                    "points": rating_points(row[0]),
                }
            )
        ratings.append(
            {
                "description": "0 - Insufficient Evidence",
                "long_description": "Blank, off-topic, copied without evidence, or no assessable submission.",
                "points": 0.0,
            }
        )
        criteria.append(
            {
                "description": clean_text(name),
                "long_description": "Score the student's own evidence; the example wording is not required.",
                "points": 4.0,
                "ratings": ratings,
            }
        )
    return criteria


def parse_rubric(path: Path) -> tuple[str, list[dict]]:
    text = path.read_text(encoding="utf-8")
    title = frontmatter_title(text)
    criteria = parse_week_zero(text) if path.name.startswith("wk0-") else parse_standard_table(text)
    if not criteria:
        raise ValueError(f"no rubric criteria parsed from {path.relative_to(ROOT)}")
    return title, criteria


def conversion_note(raw_points: int) -> str:
    return (
        f'<div data-cce-rubric-note="{NOTE_MARKER}" style="border-left:4px solid #0b5f8a;padding:10px 14px;margin:16px 0">'
        "<p><strong>How this is scored:</strong> Use the student-visible Canvas rubric. "
        f"Add the raw criterion ratings out of {raw_points}, divide by {raw_points}, "
        "multiply by 100, and round to the nearest whole point. Enter that percentage "
        "as the score out of 100. A score below 60 follows campus recovery or reassessment policy.</p>"
        "<p>The rubric is advisory in Canvas so its raw total cannot silently replace the "
        "100-point district grade.</p></div>"
    )


def with_conversion_note(description: str | None, raw_points: int) -> str:
    body = description or ""
    body = re.sub(
        rf'<div data-cce-rubric-note="{re.escape(NOTE_MARKER)}".*?</div>',
        "",
        body,
        flags=re.I | re.S,
    ).rstrip()
    return body + conversion_note(raw_points)


def rubric_payload(
    title: str, criteria: list[dict], assignment_id: int, *, include_association: bool
) -> dict[str, str]:
    # httpx.AsyncClient requires an async-compatible request body. A list of
    # tuples becomes a synchronous iterator in current httpx; Canvas does not
    # need duplicate form keys here, so a mapping is both correct and portable.
    data: dict[str, str] = {
        "rubric[title]": title,
        "rubric[free_form_criterion_comments]": "true",
    }
    if include_association:
        data.update(
            {
                "rubric_association[association_id]": str(assignment_id),
                "rubric_association[association_type]": "Assignment",
                "rubric_association[use_for_grading]": "false",
                "rubric_association[hide_score_total]": "false",
                "rubric_association[purpose]": "grading",
            }
        )
    for criterion_index, criterion in enumerate(criteria):
        prefix = f"rubric[criteria][{criterion_index}]"
        data.update(
            {
                f"{prefix}[description]": criterion["description"],
                f"{prefix}[long_description]": criterion["long_description"],
                f"{prefix}[points]": str(criterion["points"]),
                f"{prefix}[criterion_use_range]": "false",
            }
        )
        for rating_index, rating in enumerate(criterion["ratings"]):
            rating_prefix = f"{prefix}[ratings][{rating_index}]"
            data.update(
                {
                    f"{rating_prefix}[description]": rating["description"],
                    f"{rating_prefix}[long_description]": rating["long_description"],
                    f"{rating_prefix}[points]": str(rating["points"]),
                }
            )
    return data


async def request(client: httpx.AsyncClient, method: str, path: str, *, data=None):
    response = await client.request(method, f"{BASE}/api/v1{path}", data=data)
    response.raise_for_status()
    return response.json() if response.content else None


async def paged(client: httpx.AsyncClient, path: str) -> list[dict]:
    records: list[dict] = []
    url: str | None = f"{BASE}/api/v1{path}"
    params = {"per_page": 100}
    while url:
        response = await client.get(url, params=params)
        response.raise_for_status()
        records.extend(response.json())
        url = response.links.get("next", {}).get("url")
        params = None
    return records


async def ensure_association(
    client: httpx.AsyncClient, rubric: dict, assignment: dict
) -> dict:
    detail = await request(
        client,
        "GET",
        f"/courses/{COURSE_ID}/rubrics/{rubric['id']}?include[]=associations",
    )
    associations = detail.get("associations") or []
    assignment_associations = [
        entry
        for entry in associations
        if entry.get("association_type") == "Assignment"
    ]
    wrong = [
        entry
        for entry in assignment_associations
        if int(entry.get("association_id")) != int(assignment["id"])
    ]
    if wrong:
        raise ValueError(
            f"rubric {rubric['title']!r} is already associated with another assignment"
        )
    matches = [
        entry
        for entry in assignment_associations
        if int(entry.get("association_id")) == int(assignment["id"])
    ]
    association_data = {
        "rubric_association[rubric_id]": str(rubric["id"]),
        "rubric_association[association_id]": str(assignment["id"]),
        "rubric_association[association_type]": "Assignment",
        "rubric_association[title]": assignment["name"],
        "rubric_association[use_for_grading]": "false",
        "rubric_association[hide_score_total]": "false",
        "rubric_association[purpose]": "grading",
    }
    if len(matches) > 1:
        raise ValueError(f"assignment has duplicate associations for {rubric['title']!r}")
    if matches:
        return await request(
            client,
            "PUT",
            f"/courses/{COURSE_ID}/rubric_associations/{matches[0]['id']}",
            data=association_data,
        )
    return await request(
        client,
        "POST",
        f"/courses/{COURSE_ID}/rubric_associations",
        data=association_data,
    )


async def run(token: str) -> dict:
    parsed = {
        spec.assignment_title: (*parse_rubric(SOURCE_DIR / spec.source), spec)
        for spec in RUBRICS
    }
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as client:
        assignments = await paged(client, f"/courses/{COURSE_ID}/assignments")
        rubrics = await paged(client, f"/courses/{COURSE_ID}/rubrics")
        results = []
        for assessment in ASSESSMENTS:
            matches = [
                item for item in assignments if item.get("name") == assessment.title
            ]
            if len(matches) != 1:
                raise ValueError(
                    f"expected one mapped assignment {assessment.title!r}; found {len(matches)}"
                )
            assignment = matches[0]
            if assignment.get("published") or float(assignment.get("points_possible") or 0) != 100:
                raise ValueError(
                    f"mapped assignment must be unpublished and 100 points: {assessment.title}"
                )
            source_title, criteria, spec = parsed[assessment.title]
            raw_total = int(sum(float(item["points"]) for item in criteria))
            if raw_total != spec.points:
                raise ValueError(
                    f"{spec.source} totals {raw_total}; expected {spec.points}"
                )
            title = RUBRIC_PREFIX + assessment.title
            existing = [rubric for rubric in rubrics if rubric.get("title") == title]
            if len(existing) > 1:
                raise ValueError(f"duplicate Canvas rubrics named {title!r}")
            if existing:
                response = await request(
                    client,
                    "PUT",
                    f"/courses/{COURSE_ID}/rubrics/{existing[0]['id']}",
                    data={
                        **rubric_payload(
                            title,
                            criteria,
                            assignment["id"],
                            include_association=False,
                        ),
                        "rubric[skip_updating_points_possible]": "true",
                    },
                )
                rubric = response.get("rubric") or existing[0]
                association = await ensure_association(client, rubric, assignment)
            else:
                response = await request(
                    client,
                    "POST",
                    f"/courses/{COURSE_ID}/rubrics",
                    data=rubric_payload(title, criteria, assignment["id"], include_association=True),
                )
                rubric = response.get("rubric") or response
                association = response.get("rubric_association")
                if not association:
                    association = await ensure_association(client, rubric, assignment)
                rubrics.append(rubric)
            updated = await request(
                client,
                "PUT",
                f"/courses/{COURSE_ID}/assignments/{assignment['id']}",
                data={
                    "assignment[description]": with_conversion_note(
                        assignment.get("description"), raw_total
                    ),
                    "assignment[points_possible]": "100",
                    "assignment[grading_type]": "points",
                    "assignment[published]": "false",
                },
            )
            if updated.get("published") or float(updated.get("points_possible") or 0) != 100:
                raise ValueError(f"rubric operation changed assignment state: {assessment.title}")
            results.append(
                {
                    "assignment_id": assignment["id"],
                    "rubric_id": rubric["id"],
                    "association_id": association["id"],
                    "title": assessment.title,
                    "source": spec.source,
                    "criteria": len(criteria),
                    "raw_points": raw_total,
                    "use_for_grading": bool(association.get("use_for_grading")),
                }
            )
        return {"rubrics": results}


def preflight() -> int:
    errors: list[str] = []
    mapped = {assessment.title for assessment in ASSESSMENTS}
    configured = {spec.assignment_title for spec in RUBRICS}
    if len(RUBRICS) != 30 or mapped != configured:
        errors.append(
            f"rubric map drift: entries={len(RUBRICS)} missing={sorted(mapped - configured)} extra={sorted(configured - mapped)}"
        )
    for spec in RUBRICS:
        path = SOURCE_DIR / spec.source
        if not path.is_file():
            errors.append(f"missing rubric source: {spec.source}")
            continue
        try:
            _, criteria = parse_rubric(path)
        except ValueError as exc:
            errors.append(f"{spec.source}: {exc}")
            continue
        total = sum(float(item["points"]) for item in criteria)
        if total != spec.points:
            errors.append(f"{spec.source}: parsed total {total:g}; expected {spec.points}")
        for criterion in criteria:
            if len(criterion["ratings"]) < 5:
                errors.append(
                    f"{spec.source}: {criterion['description']!r} has fewer than five ratings"
                )
            if criterion["ratings"][-1]["points"] != 0:
                errors.append(
                    f"{spec.source}: {criterion['description']!r} has no zero-point rating"
                )
    if errors:
        print("Preflight failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2
    print("Preflight passed: 30 mapped advisory rubrics parse with 0-point ratings and expected totals.")
    return 0


def main() -> int:
    if sys.argv[1:] == ["--preflight"]:
        return preflight()
    if sys.argv[1:]:
        print("usage: configure_assessment_rubrics.py [--preflight]", file=sys.stderr)
        return 2
    check = preflight()
    if check:
        return check
    global httpx
    try:
        import httpx
    except ModuleNotFoundError:
        print(
            "httpx is required for live Canvas rubric setup; run through `uv run --with httpx`",
            file=sys.stderr,
        )
        return 2
    token = sys.stdin.readline().strip()
    if not token:
        print("Canvas token required on stdin", file=sys.stderr)
        return 2
    try:
        result = asyncio.run(run(token))
    except (httpx.HTTPError, ValueError) as exc:
        print(f"Rubric setup failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
