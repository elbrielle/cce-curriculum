from __future__ import annotations

import unittest
from pathlib import Path

from lesson_contracts import LessonContract, contract_html
from normalize_canvas_lesson_contracts import (
    CONTRACT_RE,
    insert_contract,
    legacy_contract_count,
    legacy_contract_span,
    without_contracts,
)


TEACHER_PANEL = (
    '<section data-cce-lesson-contract="1"><strong>Topic:</strong> New topic '
    '<strong>Objective:</strong> New objective <strong>TEKS:</strong> d(1)(A) '
    '<strong>Demonstration of Learning:</strong> New evidence</section>'
)
STUDENT_PANEL = (
    '<section data-cce-lesson-contract="1"><strong>Topic:</strong> New topic '
    '<strong>Objective:</strong> I can do it '
    '<strong>Show Your Learning:</strong> New evidence</section>'
)


class LessonContractNormalizationTest(unittest.TestCase):
    def test_contract_text_quotes_match_canvas_round_trip(self) -> None:
        contract = LessonContract(
            week="1SW Wk1",
            day=2,
            source=Path("day2.md"),
            topic="Career Opportunities",
            objective='Students will complete the "Machine & Method" check.',
            teks="d(1)(C)",
            dol='A labeled "Machine & Method" response.',
        )
        rendered = contract_html(contract, "teacher")
        self.assertIn('the "Machine &amp; Method" check', rendered)
        self.assertIn('A labeled "Machine &amp; Method" response', rendered)
        self.assertNotIn("&quot;", rendered)

    def assert_normalized(
        self,
        original: str,
        panel: str,
        role: str,
        expected_prefix: str,
        expected_suffix: str,
    ) -> str:
        result = insert_contract(original, panel, role)
        self.assertEqual(1, len(CONTRACT_RE.findall(result)))
        self.assertEqual(0, legacy_contract_count(result, role))
        self.assertEqual(result, insert_contract(result, panel, role))
        self.assertEqual(
            without_contracts(original, role),
            without_contracts(result, role),
        )
        self.assertTrue(result.startswith(expected_prefix + panel))
        self.assertTrue(result.endswith(expected_suffix))
        return result

    def test_flat_teacher_panel(self) -> None:
        prefix = '<main><h1>Teacher</h1><p class="keep">before</p>'
        legacy = (
            '<div class="contract"><strong>Topic:</strong> Old topic '
            '<strong>Objective:</strong> Old objective '
            '<strong>TEKS:</strong> d(1)(A) '
            '<strong>Demonstration of Learning:</strong> Old evidence</div>'
        )
        suffix = '<p data-exact="yes">after</p></main>'
        original = prefix + legacy + suffix
        self.assertEqual(
            (len(prefix), len(prefix) + len(legacy)),
            legacy_contract_span(original, "teacher"),
        )
        self.assert_normalized(
            original, TEACHER_PANEL, "teacher", prefix, suffix
        )

    def test_flat_student_panel(self) -> None:
        prefix = '<main><h1>Student</h1>'
        legacy = (
            '<div class="contract"><strong>Topic</strong> Old topic '
            '<strong>Today’s learning:</strong> I can do the old job '
            '<strong>Show my learning</strong> Old evidence</div>'
        )
        suffix = '<ol><li>Keep this direction exactly.</li></ol></main>'
        original = prefix + legacy + suffix
        self.assertEqual(
            (len(prefix), len(prefix) + len(legacy)),
            legacy_contract_span(original, "student"),
        )
        self.assert_normalized(
            original, STUDENT_PANEL, "student", prefix, suffix
        )

    def test_marked_panel_plus_legacy_panel(self) -> None:
        prefix = '<main><h1>Student</h1>'
        marked = (
            '<section data-cce-lesson-contract="1"><strong>Topic:</strong> Stale '
            '<strong>Objective:</strong> Stale '
            '<strong>Show Your Learning:</strong> Stale</section>'
        )
        bridge = '<p class="keep">This must remain byte-for-byte.</p>'
        legacy = (
            '<div class="legacy"><strong>Topic:</strong> Duplicate '
            '<strong>I can:</strong> Duplicate '
            '<strong>Show my learning:</strong> Duplicate</div>'
        )
        suffix = '<footer>keep</footer></main>'
        result = insert_contract(
            prefix + marked + bridge + legacy + suffix,
            STUDENT_PANEL,
            "student",
        )
        self.assertEqual(prefix + STUDENT_PANEL + bridge + suffix, result)
        self.assertEqual(1, len(CONTRACT_RE.findall(result)))
        self.assertEqual(0, legacy_contract_count(result, "student"))
        self.assertEqual(result, insert_contract(result, STUDENT_PANEL, "student"))

    def test_three_cell_grid_removes_shared_wrapper(self) -> None:
        prefix = '<main><h1>Student</h1><p>before</p>'
        grid = (
            '<div style="display:grid;gap:10px">'
            '<div><strong>Topic</strong><br>Old topic</div>'
            '<div><strong>I can</strong><br>Old objective</div>'
            '<div><strong>Show my learning</strong><br>Old evidence</div>'
            '</div>'
        )
        suffix = '<section class="steps">Keep every step.</section></main>'
        original = prefix + grid + suffix
        self.assertEqual(
            (len(prefix), len(prefix) + len(grid)),
            legacy_contract_span(original, "student"),
        )
        result = self.assert_normalized(
            original, STUDENT_PANEL, "student", prefix, suffix
        )
        self.assertNotIn("display:grid", result)
        self.assertNotIn("<div></div>", result)

    def test_page_wrapper_is_not_guessed_as_contract(self) -> None:
        body = (
            '<div class="page"><h1>Teacher guide</h1>'
            '<p><strong>Topic:</strong> A label mentioned in prose</p>'
            '<h2><strong>Objective:</strong> A later section</h2>'
            '<p><strong>TEKS:</strong> d(1)(A)</p>'
            '<p><strong>Demonstration of Learning:</strong> A later note</p>'
            '</div>'
        )
        self.assertIsNone(legacy_contract_span(body, "teacher"))

    def test_single_quoted_marked_scope_is_not_legacy(self) -> None:
        prefix = '<div><p class="before">keep before</p>'
        marked = (
            "<section data-cce-lesson-contract='1'>"
            '<div><strong>Topic:</strong> Canonical '
            '<strong>Objective:</strong> Canonical '
            '<strong>Show Your Learning:</strong> Canonical</div>'
            '</section>'
        )
        suffix = '<p class="after">keep after</p></div>'
        body = prefix + marked + suffix
        self.assertIsNone(legacy_contract_span(body, "student"))
        result = insert_contract(body, STUDENT_PANEL, "student")
        self.assertEqual(prefix + STUDENT_PANEL + suffix, result)
        self.assertEqual(1, len(CONTRACT_RE.findall(result)))
        self.assertEqual(0, legacy_contract_count(result, "student"))
        self.assertEqual(result, insert_contract(result, STUDENT_PANEL, "student"))
        self.assertEqual(
            without_contracts(body, "student"),
            without_contracts(result, "student"),
        )


if __name__ == "__main__":
    unittest.main()
