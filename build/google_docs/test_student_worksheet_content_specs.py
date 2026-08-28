#!/usr/bin/env python3
"""Regression tests for the local CCE student-Doc content composer."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import build_student_worksheet_content_specs as composer  # noqa: E402


class MarkdownSemanticParsingTest(unittest.TestCase):
    def test_response_markers_and_comparison_table_become_native_blocks(self) -> None:
        blocks = composer.markdown_to_blocks(
            """---
title: Fixture
---

## Compare

Name: ____________________

| Career | Task | My reason |
|---|---|---|
| Welder | joins metal | |
| Developer | writes code | |

[[lines: 3]]

[[pagebreak]]

- [ ] I used both facts.
"""
        )
        types = [block["type"] for block in blocks]
        self.assertIn("inline_response", types)
        self.assertIn("table", types)
        self.assertIn("response_box", types)
        self.assertIn("page_break", types)
        self.assertIn("checklist", types)
        table = next(block for block in blocks if block["type"] == "table")
        self.assertTrue(table["native"])
        self.assertTrue(table["rows"][1][2]["response"])

    def test_student_rubric_is_reduced_to_highest_band_self_check(self) -> None:
        blocks = composer.markdown_to_blocks(
            """| Criterion | Needs - 1 | Meets - 3 | Masters - 4 |
|---|---|---|---|
| Evidence | missing | one fact | two labeled facts |
| Reasoning | opinion | reason | evidence and limit |
"""
        )
        compact = composer.compact_rubric("Evidence Rubric", blocks)
        self.assertEqual(compact[0]["text"], "Self-check: Evidence Rubric")
        self.assertEqual(
            compact[1]["items"],
            [
                "Evidence: two labeled facts",
                "Reasoning: evidence and limit",
            ],
        )

    def test_builder_ast_reader_does_not_execute_builder(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "builder.py"
            path.write_text(
                """raise RuntimeError('must not execute')
student = {
  1: {'TITLE': 'One', 'EXIT': '<p>Question?</p>', 'DONE': '<ul><li>one</li></ul>'},
  2: {'TITLE': 'Two', 'EXIT': '<p>Question?</p>', 'DONE': '<ul><li>two</li></ul>'},
  3: {'TITLE': 'Three', 'EXIT': '<p>Question?</p>', 'DONE': '<ul><li>three</li></ul>'},
  4: {'TITLE': 'Four', 'EXIT': '<p>Question?</p>', 'DONE': '<ul><li>four</li></ul>'},
  5: {'TITLE': 'Five', 'EXIT': '<p>Question?</p>', 'DONE': '<ul><li>five</li></ul>'},
}
""",
                encoding="utf-8",
            )
            values = composer.builder_student_values(path)
        self.assertEqual(values[1]["TITLE"], "One")
        self.assertEqual(values[5]["DONE"], "<ul><li>five</li></ul>")


class WholeFleetContentSpecTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = composer.build_payload()
        cls.by_key = {row["day_key"]: row for row in cls.payload["days"]}

    def test_strict_all_180(self) -> None:
        self.assertEqual(composer.validate_strict(self.payload), [])
        self.assertEqual(self.payload["summary"]["day_count"], 180)
        self.assertEqual(self.payload["summary"]["manual_day_count"], 7)
        self.assertEqual(self.payload["summary"]["automatic_day_count"], 173)

    def test_every_day_has_writable_native_response_surface(self) -> None:
        missing = [
            row["day_key"]
            for row in self.payload["days"]
            if not any(
                composer.block_has_writable_response(block) for block in row["blocks"]
            )
        ]
        self.assertEqual(missing, [])

    def test_known_stale_language_and_legacy_drive_path_are_absent(self) -> None:
        rendered = composer.render_payload(self.payload)
        for name, pattern in composer.STALE_PATTERNS.items():
            self.assertIsNone(pattern.search(rendered), name)
        noncanonical = [
            row["day_key"]
            for row in self.payload["days"]
            if not str(row["document_target"]["folder_path"]).startswith(
                "VILS27/Units_CCR/"
            )
        ]
        self.assertEqual(noncanonical, [])

    def test_manual_layout_contracts_keep_exact_structures(self) -> None:
        day2 = self.by_key["1SW-Wk0-Day2"]
        self.assertEqual(day2["subtitle"], "H&L Setup and Discover Your Core")
        day3 = self.by_key["1SW-Wk0-Day3"]
        self.assertEqual(len(day3["language_support"]["word_bank"]), 18)
        day4 = self.by_key["1SW-Wk0-Day4"]
        self.assertEqual(
            day4["sources"]["base_response_source"]["path"],
            "build/worksheet_sources/my-career-journey.md",
        )
        day5 = self.by_key["1SW-Wk0-Day5"]
        five_column = [
            block
            for block in day5["blocks"]
            if block["type"] == "table" and len(block["rows"][0]) == 5
        ]
        self.assertEqual(len(five_column), 1)
        wireframe = self.by_key["1SW-Wk3-Day3"]
        screens = [block["screen"] for block in wireframe["blocks"] if block["type"] == "screen_canvas"]
        self.assertEqual(screens, ["Home", "Main Menu", "Action", "Success"])
        capstone = self.by_key["1SW-Wk5-Day5"]
        self.assertEqual(
            capstone["sources"]["base_response_source"]["path"],
            "build/worksheet_sources/wk5-reflection-update-template.md",
        )
        self.assertIn(
            "The Evidence Log is a reminder and later-use record, not a fifth grade item or extra upload.",
            composer.blocks_plain_text(capstone["blocks"]),
        )

    def test_close_only_matchmaker_doc_has_exact_three_prompts(self) -> None:
        record = self.by_key["1SW-Wk1-Day5"]
        prompts = [
            block["prompt"]
            for block in record["blocks"]
            if block["type"] == "response_box" and block.get("prompt")
        ]
        self.assertEqual(
            prompts,
            [
                "What result surprised you, and why?",
                "What did Find out why show about one career match?",
                "Give one example of how an interest raised or lowered a career match.",
            ],
        )

    def test_reference_cards_excluded_and_student_rubrics_compacted(self) -> None:
        self.assertGreater(self.payload["summary"]["excluded_reference_card_count"], 0)
        self.assertGreater(self.payload["summary"]["compact_student_rubric_count"], 0)
        for row in self.payload["days"]:
            included = set(row["source_disposition"]["included_response_artifacts"])
            excluded = set(row["source_disposition"]["excluded_reference_cards"])
            self.assertTrue(included.isdisjoint(excluded), row["day_key"])

    def test_payload_is_deterministic(self) -> None:
        second = composer.build_payload()
        self.assertEqual(
            composer.render_payload(self.payload),
            composer.render_payload(second),
        )


if __name__ == "__main__":
    unittest.main()
