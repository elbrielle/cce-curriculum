#!/usr/bin/env python3
"""Import the remaining 4SW-6SW Canvas modules with one token from stdin.

The token is passed only through child-process stdin. It is never placed in a
command-line argument, written to a file, or included in summary output.
"""

from __future__ import annotations

import ast
import json
import py_compile
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANVAS_DIR = Path(__file__).resolve().parent
ORIENTATION_IMPORTER = CANVAS_DIR / "build_course_orientation.py"
IMPORTERS = [
    *(CANVAS_DIR / f"build_4sw_wk{week}.py" for week in range(2, 7)),
    *(CANVAS_DIR / f"build_5sw_wk{week}.py" for week in range(1, 7)),
    *(CANVAS_DIR / f"build_6sw_wk{week}.py" for week in range(1, 7)),
]
ALL_IMPORTERS = [ORIENTATION_IMPORTER, *IMPORTERS]
ASSESSMENT_CONFIGURATOR = CANVAS_DIR / "configure_assessment_map.py"
RUBRIC_CONFIGURATOR = CANVAS_DIR / "configure_assessment_rubrics.py"
IMAGE_NORMALIZER = CANVAS_DIR / "normalize_unpublished_image_loading.py"
LESSON_CONTRACT_NORMALIZER = CANVAS_DIR / "normalize_canvas_lesson_contracts.py"
QA_SCRIPT = CANVAS_DIR / "qa_remaining_unpublished.py"


def literal_path(expression: ast.expr, names: dict[str, Path]) -> Path | None:
    """Resolve a Path expression made only from known names and `/` literals."""
    if isinstance(expression, ast.Name):
        return names.get(expression.id)
    if isinstance(expression, ast.Constant) and isinstance(expression.value, str):
        return Path(expression.value)
    if isinstance(expression, ast.BinOp) and isinstance(expression.op, ast.Div):
        left = literal_path(expression.left, names)
        right = literal_path(expression.right, names)
        if left is not None and right is not None:
            return left / right
    return None


def exact_upload_dependencies(importer: Path) -> set[Path]:
    """Find fully literal local paths passed to an importer upload helper."""
    tree = ast.parse(importer.read_text(), filename=str(importer))
    names = {"ROOT": ROOT, "CANVAS_DIR": CANVAS_DIR}
    for statement in tree.body:
        if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
            continue
        targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
        value = statement.value
        if value is None:
            continue
        resolved = literal_path(value, names)
        if resolved is None:
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                names[target.id] = resolved

    dependencies: set[Path] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or len(node.args) < 2:
            continue
        function_name = (
            node.func.attr if isinstance(node.func, ast.Attribute) else None
        )
        if function_name != "upload":
            continue
        resolved = literal_path(node.args[1], names)
        if resolved is not None and resolved.is_absolute():
            dependencies.add(resolved)
    return dependencies


def preflight() -> int:
    errors: list[str] = []
    missing = [
        str(path.relative_to(ROOT)) for path in ALL_IMPORTERS if not path.is_file()
    ]
    if not QA_SCRIPT.is_file():
        missing.append(str(QA_SCRIPT.relative_to(ROOT)))
    if not IMAGE_NORMALIZER.is_file():
        missing.append(str(IMAGE_NORMALIZER.relative_to(ROOT)))
    if not LESSON_CONTRACT_NORMALIZER.is_file():
        missing.append(str(LESSON_CONTRACT_NORMALIZER.relative_to(ROOT)))
    if not ASSESSMENT_CONFIGURATOR.is_file():
        missing.append(str(ASSESSMENT_CONFIGURATOR.relative_to(ROOT)))
    if not RUBRIC_CONFIGURATOR.is_file():
        missing.append(str(RUBRIC_CONFIGURATOR.relative_to(ROOT)))
    if missing:
        errors.append("Missing importer(s): " + ", ".join(missing))

    for importer in ALL_IMPORTERS:
        if not importer.is_file():
            continue
        try:
            py_compile.compile(str(importer), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{importer.relative_to(ROOT)}: {exc.msg}")
    if QA_SCRIPT.is_file():
        try:
            py_compile.compile(str(QA_SCRIPT), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{QA_SCRIPT.relative_to(ROOT)}: {exc.msg}")
    if IMAGE_NORMALIZER.is_file():
        try:
            py_compile.compile(str(IMAGE_NORMALIZER), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{IMAGE_NORMALIZER.relative_to(ROOT)}: {exc.msg}")
    if ASSESSMENT_CONFIGURATOR.is_file():
        try:
            py_compile.compile(str(ASSESSMENT_CONFIGURATOR), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{ASSESSMENT_CONFIGURATOR.relative_to(ROOT)}: {exc.msg}")
    if RUBRIC_CONFIGURATOR.is_file():
        try:
            py_compile.compile(str(RUBRIC_CONFIGURATOR), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{RUBRIC_CONFIGURATOR.relative_to(ROOT)}: {exc.msg}")

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
        r"""["']([^"']+\.(?:pdf|png|jpe?g|html))["']""", re.IGNORECASE
    )
    named_dependencies: set[str] = set()
    for importer in ALL_IMPORTERS:
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
        for dependency in exact_upload_dependencies(importer):
            if not dependency.is_file():
                errors.append(
                    f"{importer.relative_to(ROOT)}: exact upload path not found: "
                    f"{dependency.relative_to(ROOT)}"
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
            errors.append(
                f"{template.relative_to(ROOT)}: legacy Canvas tabs are not allowed"
            )
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
            errors.append(
                f"{template.relative_to(ROOT)}: legacy Canvas tabs are not allowed"
            )
        if text.count("<details") != text.count("<summary"):
            errors.append(
                f"{template.relative_to(ROOT)}: every disclosure must have one summary"
            )

    html_sources = [*ALL_IMPORTERS, *student_templates, *teacher_templates]
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
        f"Preflight passed: course orientation and {len(IMPORTERS)} week builders compile; "
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
    published = (
        module.get("published", "unknown") if isinstance(module, dict) else "unknown"
    )
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

    print("[START] COURSE ORIENTATION", flush=True)
    orientation = subprocess.run(
        [sys.executable, str(ORIENTATION_IMPORTER)],
        cwd=ROOT,
        input=token + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    if orientation.returncode:
        print(redact(orientation.stderr or orientation.stdout, token), file=sys.stderr)
        print(
            "Stopped at course orientation; week modules were not attempted.",
            file=sys.stderr,
        )
        return orientation.returncode
    try:
        orientation_payload = json.loads(orientation.stdout)
    except json.JSONDecodeError:
        print(redact(orientation.stdout[-4000:], token), file=sys.stderr)
        print(
            "Stopped at course orientation; builder output was not valid JSON.",
            file=sys.stderr,
        )
        return 3
    print("  " + summarize(orientation_payload), flush=True)

    # Week builders protect mapped assessments in place. Configure the approved
    # map before any builder runs so a clean course has those guarded objects.
    print("Configuring the approved 30-entry assessment map...", flush=True)
    assessment_setup = subprocess.run(
        [sys.executable, str(ASSESSMENT_CONFIGURATOR)],
        cwd=ROOT,
        input=token + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    if assessment_setup.returncode:
        print(
            redact(assessment_setup.stderr or assessment_setup.stdout, token),
            file=sys.stderr,
        )
        print(
            "Assessment-map setup failed; week builders were not attempted.",
            file=sys.stderr,
        )
        return assessment_setup.returncode
    try:
        assessment_payload = json.loads(assessment_setup.stdout)
    except json.JSONDecodeError:
        print(redact(assessment_setup.stdout[-4000:], token), file=sys.stderr)
        print("Assessment-map output was not valid JSON.", file=sys.stderr)
        return 3
    print(
        "  "
        f"minor={sum(1 for item in assessment_payload.get('assignments', []) if item.get('group') == 'Minor Assessments (40%)')} "
        f"major={sum(1 for item in assessment_payload.get('assignments', []) if item.get('group') == 'Major Assessments (60%)')}",
        flush=True,
    )

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
            print(
                f"Stopped at {label}; later modules were not attempted.",
                file=sys.stderr,
            )
            return result.returncode
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(redact(result.stdout[-4000:], token), file=sys.stderr)
            print(
                f"Stopped at {label}; builder output was not valid JSON.",
                file=sys.stderr,
            )
            return 3
        print("  " + summarize(payload), flush=True)

    print("Attaching 30 student-visible advisory rubrics...", flush=True)
    rubric_setup = subprocess.run(
        [sys.executable, str(RUBRIC_CONFIGURATOR)],
        cwd=ROOT,
        input=token + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    if rubric_setup.returncode:
        print(
            redact(rubric_setup.stderr or rubric_setup.stdout, token),
            file=sys.stderr,
        )
        print(
            "Assessment groups were staged, but rubric setup failed. Nothing was published.",
            file=sys.stderr,
        )
        return rubric_setup.returncode
    try:
        rubric_payload = json.loads(rubric_setup.stdout)
    except json.JSONDecodeError:
        print(redact(rubric_setup.stdout[-4000:], token), file=sys.stderr)
        print("Rubric-setup output was not valid JSON.", file=sys.stderr)
        return 3
    rubric_rows = rubric_payload.get("rubrics", [])
    print(
        "  "
        f"rubrics={len(rubric_rows)} "
        f"criteria={sum(item.get('criteria', 0) for item in rubric_rows)} "
        f"advisory={sum(not item.get('use_for_grading') for item in rubric_rows)}",
        flush=True,
    )

    print("Applying 180 paired daily learning contracts...", flush=True)
    contract_normalization = subprocess.run(
        [sys.executable, str(LESSON_CONTRACT_NORMALIZER)],
        cwd=ROOT,
        input=token + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    if contract_normalization.returncode:
        print(
            redact(contract_normalization.stderr or contract_normalization.stdout, token),
            file=sys.stderr,
        )
        print(
            "Builders ran, but daily-contract normalization failed. Nothing was published.",
            file=sys.stderr,
        )
        return contract_normalization.returncode
    try:
        contract_payload = json.loads(contract_normalization.stdout)
    except json.JSONDecodeError:
        print(redact(contract_normalization.stdout[-4000:], token), file=sys.stderr)
        print("Daily-contract output was not valid JSON.", file=sys.stderr)
        return 3
    print(
        "  "
        f"contracts={contract_payload.get('contracts')} "
        f"paired_pages={contract_payload.get('paired_pages_verified')} "
        f"updated={contract_payload.get('pages_updated')}",
        flush=True,
    )

    print("Normalizing image loading across all 36 unpublished modules...", flush=True)
    normalization = subprocess.run(
        [sys.executable, str(IMAGE_NORMALIZER)],
        cwd=ROOT,
        input=token + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    if normalization.returncode:
        print(
            redact(normalization.stderr or normalization.stdout, token),
            file=sys.stderr,
        )
        print(
            "All builders ran, but image normalization failed. Nothing was published.",
            file=sys.stderr,
        )
        return normalization.returncode
    try:
        normalization_payload = json.loads(normalization.stdout)
    except json.JSONDecodeError:
        print(redact(normalization.stdout[-4000:], token), file=sys.stderr)
        print("Image-normalization output was not valid JSON.", file=sys.stderr)
        return 3
    print(
        "  "
        f"pages={normalization_payload.get('pages_seen')} "
        f"updated={normalization_payload.get('pages_updated')} "
        f"images={normalization_payload.get('images_updated')}",
        flush=True,
    )

    print("Running read-only 36-week coursewide Canvas QA...", flush=True)
    verification = subprocess.run(
        [sys.executable, str(QA_SCRIPT)],
        cwd=ROOT,
        input=token + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    if verification.returncode:
        print(
            redact(verification.stderr or verification.stdout, token), file=sys.stderr
        )
        print(
            "All builders ran, but coursewide QA failed. Nothing was published.",
            file=sys.stderr,
        )
        return verification.returncode
    try:
        qa = json.loads(verification.stdout)
    except json.JSONDecodeError:
        print(redact(verification.stdout[-4000:], token), file=sys.stderr)
        print("Coursewide QA output was not valid JSON.", file=sys.stderr)
        return 3
    print(
        "QA passed: "
        f"orientation={qa.get('orientation', {}).get('passed')} "
        f"assessment_map={qa.get('assessment_map', {}).get('passed')} "
        f"modules={qa.get('passed_modules')}/{qa.get('expected_modules')} "
        f"items={qa.get('items')} pages={qa.get('pages')} "
        f"interactions={qa.get('interactions')} "
        f"referenced_files={qa.get('referenced_files')}",
        flush=True,
    )
    print(
        f"Imported and verified the course orientation plus {total} unpublished week packages. "
        "Run signed-in browser and Student View QA before publishing anything."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
