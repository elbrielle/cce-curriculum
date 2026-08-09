#!/usr/bin/env python3
"""Import the remaining 4SW-6SW Canvas modules with one token from stdin.

The token is passed only through child-process stdin. It is never placed in a
command-line argument, written to a file, or included in summary output.
"""

from __future__ import annotations

import json
import py_compile
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANVAS_DIR = Path(__file__).resolve().parent
IMPORTERS = [
    *(CANVAS_DIR / f"build_4sw_wk{week}.py" for week in range(2, 7)),
    *(CANVAS_DIR / f"build_5sw_wk{week}.py" for week in range(1, 7)),
    *(CANVAS_DIR / f"build_6sw_wk{week}.py" for week in range(1, 7)),
]


def preflight() -> int:
    errors: list[str] = []
    missing = [str(path.relative_to(ROOT)) for path in IMPORTERS if not path.is_file()]
    if missing:
        errors.append("Missing importer(s): " + ", ".join(missing))

    for importer in IMPORTERS:
        if not importer.is_file():
            continue
        try:
            py_compile.compile(str(importer), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{importer.relative_to(ROOT)}: {exc.msg}")

    dependency_roots = (
        ROOT / "docs/resources/worksheets",
        ROOT / "docs/resources/exit-tickets",
        ROOT / "cce-curriculum/resources/canvas-licensed",
        CANVAS_DIR / "templates",
    )
    dependency_index = {
        path.name
        for directory in dependency_roots
        for path in directory.rglob("*")
        if path.is_file()
    }
    dependency_pattern = re.compile(
        r'''["']([^"']+\.(?:pdf|png|jpe?g|html))["']''', re.IGNORECASE
    )
    named_dependencies: set[str] = set()
    for importer in IMPORTERS:
        if not importer.is_file():
            continue
        for reference in dependency_pattern.findall(importer.read_text()):
            if reference.startswith("http") or "{" in reference:
                continue
            name = Path(reference).name
            named_dependencies.add(name)
            if name not in dependency_index:
                errors.append(
                    f"{importer.relative_to(ROOT)}: local dependency not found: {reference}"
                )

    template_dir = CANVAS_DIR / "templates"
    student_templates = sorted(
        path
        for prefix in ("4sw-", "5sw-", "6sw-")
        for path in template_dir.glob(f"{prefix}*-student.html")
    )
    teacher_templates = sorted(
        path
        for prefix in ("4sw-", "5sw-", "6sw-")
        for path in template_dir.glob(f"{prefix}*-teacher.html")
    )
    if len(student_templates) != 18 or len(teacher_templates) != 18:
        errors.append(
            "Expected 18 coordinated student and teacher templates; found "
            f"{len(student_templates)} student and {len(teacher_templates)} teacher"
        )
    expected_headings = (
        '<h3 style="margin:0 0 8px;font-size:20px">Today you will</h3>',
        '<h3 style="margin:0 0 8px;font-size:20px">Exit check</h3>',
        '<h3 style="margin:0 0 8px;font-size:20px">You are done when</h3>',
    )
    for template in student_templates:
        text = template.read_text()
        for heading in expected_headings:
            if heading not in text:
                errors.append(
                    f"{template.relative_to(ROOT)}: missing semantic callout heading {heading}"
                )
        if "enhanceable_content" in text:
            errors.append(f"{template.relative_to(ROOT)}: legacy Canvas tabs are not allowed")
        if text.count("<details") != text.count("<summary"):
            errors.append(
                f"{template.relative_to(ROOT)}: every disclosure must have one summary"
            )

    teacher_headings = ("Before class", "50-minute flow")
    for template in teacher_templates:
        text = template.read_text()
        for heading in teacher_headings:
            if heading not in text:
                errors.append(
                    f"{template.relative_to(ROOT)}: missing teacher scan heading {heading}"
                )
        if "enhanceable_content" in text:
            errors.append(f"{template.relative_to(ROOT)}: legacy Canvas tabs are not allowed")
        if text.count("<details") != text.count("<summary"):
            errors.append(
                f"{template.relative_to(ROOT)}: every disclosure must have one summary"
            )

    html_sources = [*IMPORTERS, *student_templates, *teacher_templates]
    literal_images = 0
    for source in html_sources:
        for image_tag in re.findall(
            r"<img\b[^>]*>", source.read_text(), flags=re.IGNORECASE | re.DOTALL
        ):
            literal_images += 1
            if not re.search(r"\balt\s*=", image_tag, flags=re.IGNORECASE):
                errors.append(
                    f"{source.relative_to(ROOT)}: literal image is missing alt text"
                )

    if errors:
        print("Preflight failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2

    print(
        f"Preflight passed: {len(IMPORTERS)} builders compile and "
        f"{len(student_templates)} teacher/student template pairs meet the accessibility contract; "
        f"{len(named_dependencies)} named local dependencies resolve; "
        f"{literal_images} literal image renderers include alt text."
    )
    return 0


def redact(value: str, token: str) -> str:
    return value.replace(token, "[REDACTED]") if token else value


def summarize(payload: object) -> str:
    if not isinstance(payload, dict):
        return "completed; builder returned non-object JSON"
    module = payload.get("module", {})
    module_id = module.get("id", "unknown") if isinstance(module, dict) else "unknown"
    published = module.get("published", "unknown") if isinstance(module, dict) else "unknown"
    items = payload.get("items", [])
    pages = payload.get("pages", {})
    interactions = payload.get("interactions", payload.get("assignments", {}))
    return (
        f"module_id={module_id} published={published} "
        f"items={len(items) if isinstance(items, list) else 'unknown'} "
        f"page_days={len(pages) if isinstance(pages, dict) else 'unknown'} "
        f"interactions={len(interactions) if isinstance(interactions, dict) else 'unknown'}"
    )


def main() -> int:
    if "--preflight" in sys.argv[1:]:
        return preflight()

    check = preflight()
    if check:
        return check

    token = sys.stdin.readline().strip()
    if not token:
        print("Canvas token required on stdin", file=sys.stderr)
        return 2

    total = len(IMPORTERS)
    for index, importer in enumerate(IMPORTERS, start=1):
        label = importer.stem.removeprefix("build_").replace("_", " ").upper()
        print(f"[{index}/{total}] {label}", flush=True)
        result = subprocess.run(
            [sys.executable, str(importer)],
            cwd=ROOT,
            input=token + "\n",
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            print(redact(result.stderr or result.stdout, token), file=sys.stderr)
            print(f"Stopped at {label}; later modules were not attempted.", file=sys.stderr)
            return result.returncode
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(redact(result.stdout[-4000:], token), file=sys.stderr)
            print(f"Stopped at {label}; builder output was not valid JSON.", file=sys.stderr)
            return 3
        print("  " + summarize(payload), flush=True)

    print(f"Imported {total} module packages. Run API/browser QA before publishing anything.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
