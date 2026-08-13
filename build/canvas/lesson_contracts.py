#!/usr/bin/env python3
"""Canonical Topic, Objective, TEKS, and DOL contracts for Canvas lessons.

The day Markdown files are the editable source. This module turns their existing
lesson target/evidence into a consistent contract without changing the lesson's
instructional intent. When an older day has no explicit objective, the objective
uses the exact verb of the current 19 TAC §127.2 expectation named by that day.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"

TEKS = {
    "d(1)(A)": "analyze and discuss the initial results of career assessments",
    "d(1)(B)": "explore and describe the CTE career clusters",
    "d(1)(C)": "identify career opportunities within one or more career clusters",
    "d(1)(D)": "research and evaluate emerging occupations related to career interest areas",
    "d(2)(A)": "research and describe academic, technical, certification, and training requirements for one or more careers in an identified career cluster",
    "d(2)(B)": "use available resources to research and evaluate educational and training options for one or more careers in an identified career cluster",
    "d(3)(A)": "describe academic requirements for moving from middle school to high school and from high school to a career or postsecondary education",
    "d(3)(B)": "explore and list opportunities for earning college credit in high school",
    "d(3)(C)": "investigate and describe methods available to pay for college and other postsecondary training",
    "d(3)(D)": "discuss the impact of effective college and career planning",
    "d(3)(E)": "identify how performance on college, career, and readiness assessments can affect personal academic and career goals",
    "d(3)(F)": "investigate and describe how extended learning experiences can strengthen college applications or resumes",
    "d(3)(G)": "investigate and report the steps required to participate or enroll in career and educational opportunities",
    "d(3)(H)": "identify professional associations affiliated with a career pathway",
    "d(3)(I)": "define entrepreneurship and identify entrepreneurial opportunities in a field of personal interest",
    "d(4)(A)": "demonstrate effective time-management and goal-setting strategies",
    "d(4)(B)": "identify skills that transfer among a variety of careers",
    "d(4)(C)": "give an oral professional presentation about career and college exploration using appropriate technology",
    "d(4)(D)": "apply core academic skills to meet personal, academic, and career goals",
    "d(4)(E)": "explain the value of community service and volunteerism",
    "d(4)(F)": "define and identify workplace examples of work ethic, integrity, dedication, and perseverance",
    "d(5)(A)": "analyze labor-market trends related to a career of interest",
    "d(5)(B)": "classify evidence of high-skill, high-wage, or high-demand occupations using labor-market information",
    "d(5)(C)": "analyze how changing employment trends, societal needs, and economic conditions affect career choices",
    "d(5)(D)": "prepare a personal budget that reflects a desired lifestyle",
    "d(5)(E)": "use resources to compare the salaries of at least three careers in an interest area",
    "d(6)(A)": "identify the steps of an effective job search",
    "d(6)(B)": "describe appropriate appearance for an interview",
    "d(6)(C)": "participate in a mock interview",
    "d(7)(A)": "write a resume",
    "d(7)(B)": "write appropriate business correspondence such as a cover letter or thank-you letter",
    "d(7)(C)": "complete sample job applications",
    "d(7)(D)": "explain how to select and use references",
    "d(8)(A)": "select a career pathway in a desired field",
    "d(8)(B)": "document high-school courses and postsecondary requirements for a selected career pathway",
    "d(8)(C)": "write a plan for starting a career after high school and any postsecondary education",
}

TOPIC_BY_TEKS = {
    "d(1)(A)": "Career Assessment",
    "d(1)(B)": "Career Clusters",
    "d(1)(C)": "Career Opportunities",
    "d(1)(D)": "Emerging Careers",
    "d(2)(A)": "Career Preparation",
    "d(2)(B)": "Training Options",
    "d(3)(A)": "Academic Transitions",
    "d(3)(B)": "College Credit",
    "d(3)(C)": "Paying for Education",
    "d(3)(D)": "Career Planning",
    "d(3)(E)": "Assessment Impact",
    "d(3)(F)": "Extended Learning",
    "d(3)(G)": "Enrollment Steps",
    "d(3)(H)": "Professional Associations",
    "d(3)(I)": "Entrepreneurship",
    "d(4)(A)": "Goals and Time",
    "d(4)(B)": "Transferable Skills",
    "d(4)(C)": "Professional Presentation",
    "d(4)(D)": "Academic Skills",
    "d(4)(E)": "Service and Volunteerism",
    "d(4)(F)": "Professional Character",
    "d(5)(A)": "Labor Trends",
    "d(5)(B)": "Labor Classification",
    "d(5)(C)": "Changing Careers",
    "d(5)(D)": "Personal Budget",
    "d(5)(E)": "Salary Comparison",
    "d(6)(A)": "Job Search",
    "d(6)(B)": "Interview Appearance",
    "d(6)(C)": "Mock Interview",
    "d(7)(A)": "Resume Writing",
    "d(7)(B)": "Business Correspondence",
    "d(7)(C)": "Job Applications",
    "d(7)(D)": "Professional References",
    "d(8)(A)": "Career Pathway",
    "d(8)(B)": "Course Planning",
    "d(8)(C)": "Career Launch Plan",
}

SOURCE_CONTRACT_RE = re.compile(
    r"\n?<!-- CCE DAILY CONTRACT START -->.*?<!-- CCE DAILY CONTRACT END -->\n?",
    re.S,
)

OVERRIDES = {
    "docs/1sw/wk0-classroom-routines/day1.md": {
        "topic": "Lab Routines",
        "teks": "d(4)(A)",
        "objective": "Students will demonstrate time-management and goal-setting strategies by learning the lab routines, confirming course access, and recording an after-high-school goal.",
    },
    "docs/3sw/wk1-vet-science/day4.md": {
        "topic": "Transferable Skills",
        "teks": "d(4)(B)",
        "objective": "Students will identify how one skill transfers between veterinary work and another career by completing Xello Skills and a private evidence reflection.",
    },
    "docs/3sw/wk1-vet-science/day5.md": {
        "topic": "Veterinary Pathways",
        "teks": "d(2)(A), d(3)(A)",
        "objective": "Students will describe middle-school-to-high-school and high-school-to-postsecondary requirements for one veterinary career route using FYF and career evidence.",
    },
}


@dataclass(frozen=True)
class LessonContract:
    week: str
    day: int
    source: Path
    topic: str
    objective: str
    teks: str
    dol: str


def _field(text: str, names: tuple[str, ...]) -> str:
    choices = "|".join(map(re.escape, names))
    table = re.search(
        rf"^\|\s*\*\*(?:{choices})\*\*\s*\|\s*(.*?)\s*\|\s*$",
        text,
        re.MULTILINE | re.IGNORECASE,
    )
    if table:
        return table.group(1).strip()
    plain = re.search(
        rf"^(?:-\s*)?\*\*(?:{choices}):\*\*\s*(.+?)\s*$",
        text,
        re.MULTILINE | re.IGNORECASE,
    )
    return plain.group(1).strip() if plain else ""


def _topic(title: str) -> str:
    title = re.sub(r"^Day\s+[1-5]:\s*", "", title, flags=re.IGNORECASE)
    title = re.split(r"\s+[—–-]\s+|\s*\+\s*|:", title, maxsplit=1)[0]
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9/&'-]*", title)
    stop = {"a", "an", "and", "for", "from", "in", "the", "that", "through", "to", "of", "with", "your"}
    kept = [word for word in words if word.lower() not in stop][:4]
    return " ".join(kept) or "Career Exploration"


def _codes(teks: str) -> list[str]:
    found: list[str] = []
    for group, item, range_end in re.findall(
        r"d\((\d)\)\(([A-I])(?:-([A-I]))?\)", teks, re.I
    ):
        start = ord(item.upper())
        end = ord(range_end.upper()) if range_end else start
        for letter_code in range(start, end + 1):
            code = f"d({group})({chr(letter_code)})"
            if code in TEKS and code not in found:
                found.append(code)
    for code in re.findall(r"d\(\d\)\([A-I]\)", teks, re.I):
        normalized = code[0].lower() + code[1:-2] + code[-2:].upper()
        if normalized in TEKS and normalized not in found:
            found.append(normalized)
    return found


def _fallback_objective(teks: str, topic: str) -> str:
    codes = _codes(teks)
    if not codes:
        return f"Students will use the lesson evidence to explain their learning about {topic.lower()}."
    clauses = [TEKS[code] for code in codes[:2]]
    if len(clauses) == 1:
        action = clauses[0]
    else:
        action = f"{clauses[0]} and {clauses[1]}"
    return f"Students will {action} using evidence from {topic}."


def _plain(value: str) -> str:
    value = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"[*_`]+", "", value)
    return re.sub(r"\s+", " ", value).strip()


def load_contracts() -> list[LessonContract]:
    contracts: list[LessonContract] = []
    for path in sorted(DOCS.glob("[1-6]sw/wk*/day[1-5].md")):
        raw_text = path.read_text(encoding="utf-8")
        contract_match = SOURCE_CONTRACT_RE.search(raw_text)
        contract_text = contract_match.group(0) if contract_match else ""
        text = SOURCE_CONTRACT_RE.sub("\n", raw_text, count=1)
        heading = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
        if not heading:
            raise ValueError(f"Missing day heading: {path}")
        day_match = re.search(r"day([1-5])\.md$", path.name)
        week_match = re.search(r"/([1-6]sw)/wk(\d+)-", path.as_posix())
        if not day_match or not week_match:
            raise ValueError(path)
        teks = _field(contract_text, ("TEKS",)) or _field(text, ("TEKS",)) or "Course routine / supporting evidence"
        codes = _codes(teks)
        topic = _field(contract_text, ("Topic",)) or _field(text, ("Topic",)) or (
            TOPIC_BY_TEKS[codes[0]] if codes else _topic(heading.group(1))
        )
        dol = _field(contract_text, ("Demonstration of Learning", "DOL", "Evidence", "Deliverable")) or _field(text, ("Demonstration of Learning", "DOL", "Evidence", "Deliverable"))
        if not dol:
            evidence_section = re.search(
                r"^##\s+Evidence[^\n]*\n+(.*?)(?=^##\s+|\Z)",
                text,
                re.MULTILINE | re.DOTALL | re.IGNORECASE,
            )
            bullets = (
                re.findall(r"^-\s+(.+?)\s*$", evidence_section.group(1), re.MULTILINE)
                if evidence_section
                else []
            )
            if bullets:
                dol = "; ".join(bullets[:2])
            elif evidence_section:
                paragraph = re.search(r"\S.*?(?=\n\s*\n|\Z)", evidence_section.group(1), re.DOTALL)
                if paragraph:
                    dol = re.sub(r"\s+", " ", paragraph.group(0)).strip()
            else:
                raise ValueError(f"Missing evidence/deliverable: {path}")
            if not dol:
                raise ValueError(f"Missing evidence/deliverable: {path}")
        dol = _plain(dol)
        if dol[-1] not in ".!?":
            dol += "."
        objective = _plain(_field(contract_text, ("Objective", "Objectives", "Target")) or _field(text, ("Objective", "Objectives", "Target")))
        # Multi-item legacy objectives frequently list the whole day's agenda.
        # The daily objective needs one observable, TEKS-aligned learning claim;
        # the flow and DOL carry the procedural detail.
        if not objective or len(objective.split()) > 45 or objective.count(";") > 1:
            objective = _fallback_objective(teks, topic)
        elif re.match(r"I can\b", objective, re.I):
            objective = re.sub(r"^I can\b", "Students will", objective, flags=re.I)
        elif not re.match(r"Students?\s+will\b", objective, re.I):
            objective = f"Students will {objective[0].lower()}{objective[1:]}"
        if objective[-1] not in ".!?":
            objective += "."
        override = OVERRIDES.get(str(path.relative_to(ROOT)))
        if override:
            topic = override.get("topic", topic)
            teks = override.get("teks", teks)
            objective = override.get("objective", objective)
        contracts.append(
            LessonContract(
                week=f"{week_match.group(1).upper()} Wk{week_match.group(2)}",
                day=int(day_match.group(1)),
                source=path,
                topic=topic,
                objective=objective,
                teks=teks,
                dol=dol,
            )
        )
    return contracts


def contract_html(contract: LessonContract, role: str) -> str:
    if role not in {"teacher", "student"}:
        raise ValueError(role)
    if role == "teacher":
        objective = contract.objective
        dol = contract.dol
        heading = "Daily Learning Contract"
        rows = (
            ("Topic", contract.topic),
            ("Objective", objective),
            ("TEKS", contract.teks),
            ("Demonstration of Learning", dol),
        )
    else:
        objective = re.sub(r"^Students? will\s+", "I can ", contract.objective, flags=re.I)
        student_dol = contract.dol
        if not re.match(r"^(Xello|H&L|FYF|Canvas|Code\.org)\b", student_dol):
            student_dol = student_dol[0].lower() + student_dol[1:]
        dol = f"I will show my learning by completing: {student_dol}"
        heading = "Today\'s Learning"
        rows = (("Topic", contract.topic), ("Objective", objective), ("Show Your Learning", dol))
    rendered = "".join(
        f'<p style="margin:6px 0"><strong>{html.escape(label, quote=False)}:</strong> '
        f'{html.escape(value, quote=False)}</p>'
        for label, value in rows
    )
    return (
        '<section data-cce-lesson-contract="1" style="border:2px solid #166c7d;border-radius:10px;'
        'padding:14px 16px;margin:16px 0;background:#f3fbfc">'
        f'<h2 style="margin:0 0 8px;color:#166c7d;font-size:22px">{heading}</h2>{rendered}</section>'
    )


if __name__ == "__main__":
    rows = load_contracts()
    print(f"contracts={len(rows)} teacher={len(rows)} student={len(rows)}")
