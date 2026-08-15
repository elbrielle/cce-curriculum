#!/usr/bin/env python3
"""Fail when a daily learning contract is absent, vague, or structurally weak."""

from __future__ import annotations

import json
import re

from lesson_contracts import TEKS, load_contracts


WEAK_DOL = re.compile(r"\b(work on|continue|participate|understanding)\b", re.I)
OBSERVABLE = re.compile(
    r"\b(analy[sz]e|ask|build|classify|communicate|compare|complete|create|"
    r"deliver|demonstrate|describe|design|document|evaluate|explain|explore|identify|investigate|"
    r"make|match|plan|prepare|present|record|research|revise|separate|select|"
    r"show|state|submit|turn|use|write)\b",
    re.I,
)


def main() -> int:
    rows = load_contracts()
    issues: list[dict[str, str]] = []
    for row in rows:
        if not 1 <= len(row.topic.split()) <= 4:
            issues.append({"lesson": f"{row.week} D{row.day}", "issue": "topic length"})
        if not re.match(r"Students? will\b", row.objective, re.I):
            issues.append({"lesson": f"{row.week} D{row.day}", "issue": "objective stem"})
        if not OBSERVABLE.search(row.objective):
            issues.append({"lesson": f"{row.week} D{row.day}", "issue": "objective has no observable action"})
        if len(row.objective.split()) > 55:
            issues.append({"lesson": f"{row.week} D{row.day}", "issue": "objective too long"})
        if WEAK_DOL.search(row.dol) and not OBSERVABLE.search(row.dol):
            issues.append({"lesson": f"{row.week} D{row.day}", "issue": "DOL is activity-only"})
        if not re.search(r"\bd\(\d\)\([A-I](?:-[A-I])?\)", row.teks, re.I):
            issues.append({"lesson": f"{row.week} D{row.day}", "issue": "missing exact TEKS"})
    payload = {
        "lessons": len(rows),
        "teacher_contracts": len(rows),
        "student_contracts": len(rows),
        "official_expectations_loaded": len(TEKS),
        "issues": issues,
    }
    print(json.dumps(payload, indent=2))
    return 0 if len(rows) == 180 and not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
