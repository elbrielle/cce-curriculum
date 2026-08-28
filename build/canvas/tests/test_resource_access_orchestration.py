from __future__ import annotations

import ast
import importlib.util
import sys
import unittest
from pathlib import Path


CANVAS_DIR = Path(__file__).resolve().parents[1]
IMPORT_SCRIPT = CANVAS_DIR / "import_remaining_unpublished.py"
WRAPPER_SCRIPT = CANVAS_DIR / "run_builder_with_resource_access.py"
WK0_RECONCILER = CANVAS_DIR / "reconcile_wk0_day2_day3.py"


def load_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


remaining = load_script("import_remaining_unpublished", IMPORT_SCRIPT)
wrapper = load_script("run_builder_with_resource_access", WRAPPER_SCRIPT)


def subprocess_targets(path: Path) -> list[str]:
    """Return the first-argument source for subprocess.run calls in main order."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    main = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    calls = [
        node
        for node in ast.walk(main)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ]
    calls.sort(key=lambda node: (node.lineno, node.col_offset))
    return [ast.get_source_segment(source, call.args[0]) or "" for call in calls]


def passing_result(course_id: int) -> list[dict]:
    return [
        {
            "course_id": course_id,
            "passed": True,
            "publication_states_unchanged": True,
            "restricted_after": {"files": 0, "folders": 0},
        }
    ]


class ResourceAccessResultTests(unittest.TestCase):
    def test_both_orchestrators_accept_only_complete_success_proof(self) -> None:
        for module in (remaining, wrapper):
            with self.subTest(module=module.__name__):
                result = module.validated_resource_access_result(
                    passing_result(98060), 98060
                )
                self.assertEqual(result["course_id"], 98060)

    def test_both_orchestrators_fail_closed_on_incomplete_proof(self) -> None:
        mutations = (
            ("wrong course", {"course_id": 11111}),
            ("not passed", {"passed": False}),
            ("publication drift", {"publication_states_unchanged": False}),
            ("restricted file", {"restricted_after": {"files": 1, "folders": 0}}),
            ("restricted folder", {"restricted_after": {"files": 0, "folders": 1}}),
        )
        for module in (remaining, wrapper):
            for label, mutation in mutations:
                with self.subTest(module=module.__name__, case=label):
                    payload = passing_result(98060)
                    payload[0].update(mutation)
                    with self.assertRaises(ValueError):
                        module.validated_resource_access_result(payload, 98060)


class OrchestrationOrderTests(unittest.TestCase):
    def test_coursewide_import_finalizes_after_builders_and_before_qa(self) -> None:
        targets = subprocess_targets(IMPORT_SCRIPT)
        finalizer_index = next(
            index
            for index, target in enumerate(targets)
            if "RESOURCE_ACCESS_FINALIZER" in target
        )
        qa_index = next(
            index for index, target in enumerate(targets) if "QA_SCRIPT" in target
        )
        importer_index = next(
            index for index, target in enumerate(targets) if "str(importer)" in target
        )
        reconciliation_index = max(
            index
            for index, target in enumerate(targets)
            if any(
                name in target
                for name in (
                    "ASSESSMENT_CONFIGURATOR",
                    "RUBRIC_CONFIGURATOR",
                    "LESSON_CONTRACT_NORMALIZER",
                    "IMAGE_NORMALIZER",
                )
            )
        )
        self.assertLess(importer_index, finalizer_index)
        self.assertLess(reconciliation_index, finalizer_index)
        self.assertLess(finalizer_index, qa_index)
        self.assertIn('"--apply"', targets[finalizer_index])
        self.assertIn('"--course-id"', targets[finalizer_index])

    def test_single_builder_wrapper_finalizes_after_builder(self) -> None:
        targets = subprocess_targets(WRAPPER_SCRIPT)
        builder_index = next(
            index for index, target in enumerate(targets) if "str(builder)" in target
        )
        finalizer_index = next(
            index for index, target in enumerate(targets) if "RESOURCE_FIX" in target
        )
        self.assertLess(builder_index, finalizer_index)
        self.assertIn('"--apply"', targets[finalizer_index])
        self.assertIn('"--course-id"', targets[finalizer_index])

    def test_orchestrators_do_not_construct_publication_mutation_payloads(self) -> None:
        forbidden = (
            "wiki_page[published]",
            "module[published]",
            "module_item[published]",
            "assignment[published]",
            "published=true",
            "published=false",
        )
        for path in (IMPORT_SCRIPT, WRAPPER_SCRIPT):
            source = path.read_text(encoding="utf-8").lower()
            for fragment in forbidden:
                with self.subTest(path=path.name, fragment=fragment):
                    self.assertNotIn(fragment, source)

    def test_importers_with_legacy_lock_helpers_are_covered_by_finalizer(self) -> None:
        lock_using_importers = [
            importer
            for importer in remaining.IMPORTERS
            if "lock_folder_files" in importer.read_text(encoding="utf-8")
        ]
        self.assertTrue(lock_using_importers)
        self.assertEqual(remaining.RESOURCE_ACCESS_FINALIZER, wrapper.RESOURCE_FIX)

    def test_week0_reconciler_finishes_with_publication_neutral_access_repair(self) -> None:
        source = WK0_RECONCILER.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(WK0_RECONCILER))
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "normalize_resource_access"
        ]
        self.assertEqual(len(calls), 1)
        keywords = {keyword.arg: keyword.value for keyword in calls[0].keywords}
        self.assertIsInstance(keywords.get("manage_home"), ast.Constant)
        self.assertIs(keywords["manage_home"].value, False)
        self.assertIsInstance(keywords.get("check_only"), ast.Constant)
        self.assertIs(keywords["check_only"].value, False)


if __name__ == "__main__":
    unittest.main()
