#!/usr/bin/env python3
"""Static coursewide source-grounding and next-day-readiness inventory.

This audit does not claim that a citation is correct merely because it exists.
It identifies the evidence a human reviewer must verify against the authoritative
scope and sequence, FYF printed pages, Climber Notes, Xello configuration, and
current primary sources. It makes no Canvas API calls and writes no Canvas data.
"""

from __future__ import annotations

import ast
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANVAS = ROOT / "build/canvas"
DOCS = ROOT / "docs"
REPORT = ROOT / "cce-curriculum/notes/coursewide-source-grounding-audit-2026-08-09.md"
DATA = ROOT / "cce-curriculum/notes/coursewide-source-grounding-audit-2026-08-09.json"

BUILDERS = [
    *(CANVAS / f"build_wk{week}.py" for week in range(6)),
    *(CANVAS / f"build_{block}sw_wk{week}.py" for block in range(2, 7) for week in range(1, 7)),
]

MOVE_PATTERNS = {
    "Stop and Jot": r"stop[- ]and[- ]jot|stop[- ]&[- ]jot",
    "Think-Pair-Share / Turn and Talk": r"think[- ]pair[- ]share|turn[- ]and[- ]talk|partner (?:talk|share|reason|compare|check|discussion)",
    "QSSA": r"\bqssa\b|question,? signal,? stem,? answer",
    "Active Monitoring": r"active[- ]monitor|monitoring target|monitor\b|lap [123]",
    "Chunking": r"\bchunk(?:ing|ed)?\b|one (?:step|block|part) at a time",
    "TVB": r"time[, /]+voice[, /]+body|\btvb\b",
}

SUPPORT_PATTERN = re.compile(
    r"sentence (?:frame|stem)|word bank|bilingual|glossary|oral rehearsal|"
    r"read aloud|read-aloud|speech-to-text|chunk|model(?:ed)?|visual|partner|"
    r"pre-teach|icons?|labels?|screen magnification|large print|tactile",
    re.IGNORECASE,
)

SOURCE_PATTERNS = {
    "FYF": re.compile(r"FYF\s+p{1,2}\.? ?\s*\d|Find Your Future", re.I),
    "Climber Notes": re.compile(r"Climber Notes|Climber|licensed (?:slide|deck)", re.I),
    "Xello": re.compile(r"\bXello\b|Completion Standards", re.I),
    "H&L": re.compile(r"H&amp;L|H&L|Hats\s*&\s*Ladders", re.I),
    "BLS / current primary source": re.compile(r"\bBLS\b|Occupational Outlook|current (?:district|official)|source/date|dated source", re.I),
}


@dataclass
class DayAudit:
    week: str
    module: str
    day: int
    source_file: str
    builder: str
    pair_present: bool
    explicit_topic: bool
    explicit_objective: bool
    explicit_dol: bool
    teks_visible: bool
    fifty_minute_flow: bool
    before_class_prep: bool
    answer_key_or_monitoring: bool
    concrete_eb_support: bool
    absence_or_platform_route: bool
    student_start_and_done_contract: bool
    instructional_moves: list[str]
    source_families: list[str]
    fyf_citations: list[str]
    unresolved_markers: list[str]
    manual_checks: list[str]


def literal_assignment(tree: ast.Module, name: str) -> str | None:
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(isinstance(target, ast.Name) and target.id == name for target in targets):
            continue
        value = node.value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return value.value
    return None


def day_dict_segments(tree: ast.Module, source: str, name: str) -> dict[int, str]:
    """Return raw source for integer-keyed day dictionaries without evaluating f-strings."""
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(isinstance(target, ast.Name) and target.id == name for target in targets):
            continue
        if not isinstance(node.value, ast.Dict):
            continue
        result: dict[int, str] = {}
        for key, value in zip(node.value.keys, node.value.values):
            if isinstance(key, ast.Constant) and isinstance(key.value, int):
                result[key.value] = ast.get_source_segment(source, value) or ""
        return result
    return {}


def first_day_dict(tree: ast.Module, source: str, names: tuple[str, ...]) -> dict[int, str]:
    for name in names:
        values = day_dict_segments(tree, source, name)
        if values:
            return values
    return {}


def builder_week(builder: Path) -> tuple[str, Path]:
    match = re.fullmatch(r"build_(?:(\d)sw_)?wk(\d)\.py", builder.name)
    if not match:
        raise ValueError(builder.name)
    block = int(match.group(1) or 1)
    week = int(match.group(2))
    candidates = sorted((DOCS / f"{block}sw").glob(f"wk{week}-*"))
    if len(candidates) != 1:
        raise ValueError(f"Expected one docs directory for {block}SW Wk{week}; found {candidates}")
    return f"{block}SW Wk{week}", candidates[0]


def template_texts(builder: Path, week: str) -> tuple[str, dict[int, str]]:
    block, wk = re.fullmatch(r"(\d)SW Wk(\d)", week).groups()
    if block == "1":
        prefix = f"wk{wk}"
    else:
        prefix = f"{block}sw-wk{wk}"
    teacher_paths = sorted((CANVAS / "templates").glob(f"{prefix}*teacher.html"))
    teacher = "\n".join(path.read_text(encoding="utf-8") for path in teacher_paths)
    students: dict[int, str] = {}
    for path in sorted((CANVAS / "templates").glob(f"{prefix}*student.html")):
        day_match = re.search(r"day([1-5])", path.name)
        if day_match:
            students[int(day_match.group(1))] = path.read_text(encoding="utf-8")
        else:
            generic = path.read_text(encoding="utf-8")
            for day in range(1, 6):
                students.setdefault(day, generic)
    return teacher, students


def unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item.strip() for item in items if item.strip()))


def audit_builder(builder: Path) -> list[DayAudit]:
    source = builder.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(builder))
    week, docs_dir = builder_week(builder)
    module = literal_assignment(tree, "MODULE_NAME") or "MISSING MODULE_NAME"
    teacher_template, student_templates = template_texts(builder, week)
    teacher_days = first_day_dict(tree, source, ("teacher_data", "td", "teacher"))
    student_days = first_day_dict(tree, source, ("student_data", "student"))
    student_titles = first_day_dict(tree, source, ("student_titles", "titles", "day_names"))

    audits: list[DayAudit] = []
    for day in range(1, 6):
        day_file = docs_dir / f"day{day}.md"
        day_source = day_file.read_text(encoding="utf-8") if day_file.is_file() else ""
        # Newer builders generate their day dictionaries inside helper functions.
        # When a day literal is not available as a top-level assignment, scan the
        # full builder for structural contract evidence and leave semantic truth
        # to the mandatory manual grounding check.
        teacher = teacher_template + "\n" + (teacher_days.get(day) or source)
        student = student_templates.get(day, "") + "\n" + (student_days.get(day) or source)
        combined = "\n".join((teacher, student, day_source))

        moves = [label for label, pattern in MOVE_PATTERNS.items() if re.search(pattern, combined, re.I)]
        sources = [label for label, pattern in SOURCE_PATTERNS.items() if pattern.search(combined)]
        citations = unique(re.findall(r"FYF\s+p{1,2}\.? ?\s*\d+(?:\s*[-–]\s*\d+)?", combined, re.I))
        markers = unique(re.findall(r"\[(?:VERIFY|TODO|TBD)[^\]]*\]", combined, re.I))

        manual: list[str] = [
            "Verify each cited FYF printed page and named activity against the licensed source.",
            "Verify TEKS verb, student action, and collected evidence against the current standard.",
            "Cold-read the teacher and student pair for next-day implementation burden.",
            "Render and inspect every writing artifact for honest response space.",
        ]
        if "Xello" in sources:
            manual.append("Verify exact Xello task name, time, minimum, prerequisite, report evidence, and catch-up route.")
        if "Climber Notes" in sources:
            manual.append("Verify exact licensed deck/slide, projection order, and teacher-only answer guidance.")
        if not moves:
            manual.append("Add or name at least one purposeful district instructional move; do not add all moves mechanically.")
        if markers:
            manual.append("Resolve the remaining verification marker before the module is copy-ready.")

        audits.append(
            DayAudit(
                week=week,
                module=module,
                day=day,
                source_file=str(day_file.relative_to(ROOT)) if day_file.is_file() else "MISSING",
                builder=str(builder.relative_to(ROOT)),
                pair_present=bool(teacher_template and student_templates.get(day)),
                explicit_topic=bool(re.search(r"\btopic\b", teacher, re.I)),
                explicit_objective=bool(re.search(r"lesson objective|\bobjective\b", teacher, re.I)),
                explicit_dol=bool(re.search(r"demonstration of learning|\bDOL\b", teacher, re.I)),
                teks_visible=bool(re.search(r"\bTEKS?\s+d\(", teacher, re.I)),
                fifty_minute_flow=bool(re.search(r"50[- ]minute (?:lesson )?flow", teacher, re.I)),
                before_class_prep=bool(re.search(r"before (?:class|students arrive)", teacher, re.I)),
                answer_key_or_monitoring=bool(re.search(r"monitoring|answer guidance|teacher key|accepted answer|misconception", teacher, re.I)),
                concrete_eb_support=bool(SUPPORT_PATTERN.search(teacher)),
                absence_or_platform_route=bool(re.search(r"absent|platform|site did not work|fallback|no-login", combined, re.I)),
                student_start_and_done_contract=bool(re.search(r"Today you will|What you will do", student, re.I) and re.search(r"You are done when|Done when", student, re.I)),
                instructional_moves=moves,
                source_families=sources,
                fyf_citations=citations,
                unresolved_markers=markers,
                manual_checks=manual,
            )
        )
    return audits


def mark(value: bool) -> str:
    return "Yes" if value else "NO"


def write_report(audits: list[DayAudit]) -> None:
    totals = Counter()
    for audit in audits:
        for field in (
            "pair_present", "explicit_topic", "explicit_objective", "explicit_dol",
            "teks_visible", "fifty_minute_flow", "before_class_prep",
            "answer_key_or_monitoring", "concrete_eb_support",
            "absence_or_platform_route", "student_start_and_done_contract",
        ):
            totals[field] += bool(getattr(audit, field))

    marker_days = [audit for audit in audits if audit.unresolved_markers]
    no_move_days = [audit for audit in audits if not audit.instructional_moves]
    report = [
        "# Coursewide Source-Grounding and Next-Day-Readiness Audit",
        "",
        "**Audit date:** 2026-08-09  ",
        "**Scope:** 36 unpublished instructional modules, 180 Teacher/Student day pairs  ",
        "**Status:** Structural inventory complete; source-by-source semantic verification in progress",
        "",
        "## What this audit proves, and what it does not",
        "",
        "This static pass proves whether the authored Canvas source visibly contains the implementation contract a teacher needs. It does **not** treat the presence of a citation as proof that the page number, activity, Xello minimum, labor-market figure, pathway claim, or TEKS alignment is correct. Those items remain in the manual grounding queue until checked against the authoritative source.",
        "",
        "## Coursewide structural baseline",
        "",
        f"- Coordinated teacher/student pair detected: **{totals['pair_present']}/180**",
        f"- TEKS visible in the teacher guide: **{totals['teks_visible']}/180**",
        f"- 50-minute flow visible: **{totals['fifty_minute_flow']}/180**",
        f"- Before-class preparation visible: **{totals['before_class_prep']}/180**",
        f"- Monitoring/key guidance visible: **{totals['answer_key_or_monitoring']}/180**",
        f"- Concrete language/reading/participation support detected: **{totals['concrete_eb_support']}/180**",
        f"- Absence/platform recovery route detected: **{totals['absence_or_platform_route']}/180**",
        f"- Student start/done contract detected: **{totals['student_start_and_done_contract']}/180**",
        f"- Teacher guide explicitly labels **Topic**: **{totals['explicit_topic']}/180**",
        f"- Teacher guide explicitly labels **Objective**: **{totals['explicit_objective']}/180**",
        f"- Teacher guide explicitly labels **Demonstration of Learning / DOL**: **{totals['explicit_dol']}/180**",
        "",
        "The last three counts are intentionally strict. A title, `Today you will`, or `Target and evidence` may contain the right substance, but the district-facing labels are not consistently scannable yet.",
        "",
        "## Confirmed first-pass findings",
        "",
        "### P0 - Xello prerequisite chain is broken in the current 1SW Canvas sequence",
        "",
        "The authenticated Grade 8 configuration requires **After high school goal -> Matchmaker quiz -> Personality Style quiz**. The current Canvas source protects After high school goal in 1SW Wk0 and Personality Style in 1SW Wk2, but neither `build_wk0.py` nor `build_wk1.py` protects Matchmaker. A teacher can therefore reach the polished Week 2 guide with students who are blocked by a missing prerequisite. The authoritative S&S is also stale: it still lists the old Wk0 quiz pileup and assigns Favorite Clusters to Wk2 even though the repaired Canvas pages place Personality Style there.",
        "",
        "### P0 - The authoritative S&S and production Canvas disagree across all six 1SW Xello windows",
        "",
        "The intended repaired sequence is Log in/After high school goal, What is CTE/Matchmaker, Personality Style, Learning Style, Add interests/Add skills, Favorite clusters. Current Canvas largely follows that order except for the missing What is CTE/Matchmaker block. Current S&S columns still show the legacy pileup, Favorite Clusters in Wk2, Add Skills in Wk3, a blank Wk4 cell, and Save Careers in Wk5. This must be reconciled before lesson-by-lesson grounding can be called complete.",
        "",
        "### P1 - District scan labels are not explicit",
        "",
        "Every guide needs a fast teacher-facing block for Topic, Objective, TEKS, and Demonstration of Learning. The current title, subtitle, `Today you will`, and `Target and evidence` usually contain the ingredients, but the required labels are not consistent enough for an evaluator or a teacher scanning during class.",
        "",
        "### P1 - Projection readiness is not the same as one slide deck per lesson",
        "",
        "Separate decks are intentionally optional. A lesson passes when the teacher guide itself is projection-ready or embeds the exact load-bearing workbook page, Climber slide, Xello launch asset, model, timer/prompt, and key needed for whole-class delivery. The manual review must record that outcome day by day.",
        "",
        "### P1 - Two backup lesson sources still carry unresolved eDynamic markers",
        "",
        "The remaining markers are 1SW Wk1 Day 5 (`Unit 2.1`) and 2SW Wk1 Day 5 (`Unit 5.1`). Canvas already treats eDynamic as supplemental in those lessons, so these markers should either be resolved to a verified optional classroom job or removed from the core route. They cannot remain ambiguous in the copy-ready source package.",
        "",
        "### P1 - Artifact layout needs visual, not textual, acceptance",
        "",
        "The strict worksheet build is a useful overflow gate, but it does not prove that a sixth- or seventh-grade student has enough room for the requested thinking. Every packet still needs rendered-page inspection against the response job: phrases, sentences, multi-part reasoning, and labeled sketches require different amounts of space.",
        "",
        "## Manual grounding progress",
        "",
        "### 1SW Wk0 licensed workbook check - verified",
        "",
        "- Day 1 correctly uses FYF printed pp. 2-3 for `Classroom Career Hunt`.",
        "- Day 3 correctly uses FYF printed pp. 9-11 for `My Building Blocks`; printed p. 11 provides a full-page reflection area.",
        "- Day 4 correctly uses FYF printed p. 22 for `Building a Career Community`, with the custom My Career Journey artifact carrying the larger evidence job.",
        "- Day 5 correctly uses FYF printed pp. 4-5 for `Perks and Quirks`. The workbook's research-note cells are too shallow for full explanations, but the Canvas route adds a one-career-per-page worksheet with dedicated full-width response lines. That is an appropriate scaffold rather than a duplicate decoration.",
        "- Days 2-3 correctly treat the personality/work-values instruction as H&L plus Climber Notes because FYF does not print those assessments.",
        "",
        "**Wk0 verdict:** workbook page grounding passes. The week is not fully copy-ready until the Xello Matchmaker prerequisite gap and the district Topic/Objective/DOL scan block are repaired.",
        "",
        "## Immediate gates before teacher-copy readiness",
        "",
        "1. Verify all 180 days against the authoritative S&S and the exact licensed source. Presence is not accuracy.",
        "2. Standardize the teacher scan block so Topic, Objective, TEKS, and Demonstration of Learning are explicit without duplicating prose.",
        "3. Confirm each day uses at least one purposeful district move where it improves learning. Variety matters; a mechanical checklist does not.",
        "4. Cold-read every page pair and artifact as a teacher who has not seen the source files. Record hidden prep, missing models/keys, and timing collisions.",
        "5. Render every worksheet and inspect response space against the amount and type of writing requested.",
        "6. Keep separate slide decks optional. Require a projection-ready Canvas route or embedded licensed visual whenever the live lesson depends on whole-class display.",
        "",
        f"Unresolved `[VERIFY]`/`[TODO]`/`[TBD]` markers detected on **{len(marker_days)} day(s)**. Days with no named instructional move detected: **{len(no_move_days)}**. Both lists appear below.",
        "",
        "## Day-by-day ledger",
        "",
        "| Week | Day | Pair | TEKS | 50 min | Prep | Key/monitor | EB support | Recovery | Student contract | District moves | Sources | Markers |",
        "| --- | ---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- | --- | --- |",
    ]
    for audit in audits:
        report.append(
            "| {week} | {day} | {pair} | {teks} | {flow} | {prep} | {key} | {support} | {recovery} | {contract} | {moves} | {sources} | {markers} |".format(
                week=audit.week,
                day=audit.day,
                pair=mark(audit.pair_present),
                teks=mark(audit.teks_visible),
                flow=mark(audit.fifty_minute_flow),
                prep=mark(audit.before_class_prep),
                key=mark(audit.answer_key_or_monitoring),
                support=mark(audit.concrete_eb_support),
                recovery=mark(audit.absence_or_platform_route),
                contract=mark(audit.student_start_and_done_contract),
                moves=", ".join(audit.instructional_moves) or "**REVIEW**",
                sources=", ".join(audit.source_families) or "**REVIEW**",
                markers="; ".join(audit.unresolved_markers),
            )
        )

    report.extend(["", "## Exact district-label gap", ""])
    for audit in audits:
        missing = []
        if not audit.explicit_topic:
            missing.append("Topic")
        if not audit.explicit_objective:
            missing.append("Objective")
        if not audit.explicit_dol:
            missing.append("DOL")
        if missing:
            report.append(f"- {audit.week} Day {audit.day}: {', '.join(missing)}")

    if marker_days:
        report.extend(["", "## Unresolved verification markers", ""])
        for audit in marker_days:
            report.append(f"- {audit.week} Day {audit.day}: {'; '.join(audit.unresolved_markers)}")

    report.extend(
        [
            "",
            "## Manual grounding protocol",
            "",
            "For each day, record a verdict for: S&S topic/activity; exact FYF printed page and section; exact Climber deck/slide; exact Xello task/time/minimum/prerequisite; supplemental-platform boundary; current pathway and labor-data claims; TEKS verb/action/evidence; teacher cold-start readiness; student clarity; EB supports; district move; artifact response space; and absence/platform route.",
            "",
            "A day is **Copy-ready** only when every load-bearing item is verified and the teacher can run the lesson without inventing directions, examples, answers, data, materials, or timing decisions.",
        ]
    )
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    DATA.write_text(json.dumps([asdict(audit) for audit in audits], indent=2) + "\n", encoding="utf-8")


def main() -> None:
    audits = [audit for builder in BUILDERS for audit in audit_builder(builder)]
    if len(audits) != 180:
        raise SystemExit(f"Expected 180 day audits, found {len(audits)}")
    write_report(audits)
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    print(f"Wrote {DATA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
