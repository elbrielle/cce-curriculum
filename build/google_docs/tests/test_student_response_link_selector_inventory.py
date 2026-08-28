from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GENERATOR = (
    ROOT / "build/google_docs/build_student_response_link_selector_inventory.py"
)
INVENTORY = ROOT / "build/google_docs/student_response_link_selector_inventory.json"


class StudentResponseLinkSelectorInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.generator_source = GENERATOR.read_text(encoding="utf-8")
        cls.inventory_source = INVENTORY.read_text(encoding="utf-8")
        cls.payload = json.loads(cls.inventory_source)

    def test_generator_uses_no_optional_html_parser_dependency(self) -> None:
        self.assertNotIn("from bs4", self.generator_source)
        self.assertNotIn("BeautifulSoup", self.generator_source)
        self.assertIn("from html.parser import HTMLParser", self.generator_source)

    def test_reviewed_inventory_has_exact_180_day_185_selector_contract(self) -> None:
        summary = self.payload["summary"]
        self.assertEqual(self.payload["review_status"], "reviewed")
        self.assertEqual(summary["day_count"], 180)
        self.assertEqual(summary["selector_count"], 185)
        self.assertEqual(summary["days_with_selectors"], 166)
        self.assertEqual(summary["days_without_selectors"], 14)
        self.assertEqual(
            summary["selector_multiplicity"],
            {"0": 14, "1": 151, "2": 12, "3": 2, "4": 1},
        )
        self.assertEqual(
            summary["classification_counts"],
            {
                "daily_exit_ticket_pdf": 8,
                "student_response_work_pdf": 177,
            },
        )
        self.assertEqual(summary["reviewed_anchor_text_replacement_count"], 2)

    def test_every_selector_is_exact_unique_and_href_only(self) -> None:
        selectors = [
            selector
            for day in self.payload["days"]
            for selector in day["selectors"]
        ]
        self.assertEqual(len(selectors), 185)
        self.assertEqual(len({row["selector_id"] for row in selectors}), 185)
        for selector in selectors:
            self.assertRegex(selector["expected_old_href_complete_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(selector["normalized_anchor_signature_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(
                selector["replacement_href"],
                r"^https://docs\.google\.com/document/d/[A-Za-z0-9_-]+/copy$",
            )
            self.assertNotIn("?", selector["expected_old_href_canonical"])
            self.assertTrue(selector["source_evidence"]["authored_line_candidates"])

    def test_two_pdf_specific_labels_have_reviewed_replacements(self) -> None:
        replacements = {
            (day["day_key"], selector["anchor_text"]): selector[
                "replacement_anchor_text"
            ]
            for day in self.payload["days"]
            for selector in day["selectors"]
            if selector["replacement_anchor_text"] is not None
        }
        self.assertEqual(
            replacements,
            {
                (
                    "1SW-Wk1-Day1",
                    "View the Day 1 exit ticket PDF reference",
                ): "Open the Day 1 exit ticket",
                (
                    "1SW-Wk1-Day4",
                    "open the printable Robots for Crayons action plan",
                ): "Open the Robots for Crayons action plan",
            },
        )

    def test_verifier_capabilities_are_not_committed(self) -> None:
        self.assertNotRegex(self.inventory_source, r"[?&]verifier=")
        self.assertFalse(
            self.payload["privacy"]["canvas_verifier_queries_committed"]
        )

    def test_four_reference_only_discrepancy_routes_remain_unselected(self) -> None:
        by_day = {row["day_key"]: row for row in self.payload["days"]}
        reference_only = {
            "3SW-Wk1-Day1",
            "3SW-Wk2-Day1",
            "3SW-Wk3-Day1",
            "4SW-Wk4-Day2",
        }
        for day_key in reference_only:
            self.assertEqual(by_day[day_key]["selectors"], [])
            self.assertEqual(
                by_day[day_key]["no_selector_review"]["reason_code"],
                "only_excluded_pdf_links_are_present",
            )

    def test_no_selector_days_have_reviewed_insertion_landmarks_only(self) -> None:
        without = [row for row in self.payload["days"] if not row["selectors"]]
        self.assertEqual(len(without), 14)
        for row in without:
            review = row["no_selector_review"]
            insertion = review[
                "suggested_bare_button_insertion_if_separately_approved"
            ]
            self.assertEqual(
                insertion["authorization"], "not_authorized_by_href_only_rule"
            )
            self.assertEqual(
                insertion["insert_immediately_after_heading"],
                insertion["heading_signature"]["text"],
            )
            self.assertEqual(insertion["heading_signature"]["tag"], "h3")
            self.assertRegex(
                insertion["heading_signature"]["element_sha256"],
                r"^[0-9a-f]{64}$",
            )


if __name__ == "__main__":
    unittest.main()
