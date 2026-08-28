from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "repair_student_google_copy_buttons.py"
)
SPEC = importlib.util.spec_from_file_location(
    "repair_student_google_copy_buttons", SCRIPT
)
assert SPEC and SPEC.loader
repair = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = repair
SPEC.loader.exec_module(repair)


class SelectorMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.selectors, cls.registry, cls.backup = repair.load_inputs(
            allow_historical_registry=True
        )
        cls.by_route = {
            row["route_id"]: row for row in cls.selectors["routes"]
        }
        cls.backup_by_route = {
            row["route_id"]: row
            for row in cls.backup["pages"]
            if row["role"] == "student"
        }

    def test_reviewed_map_has_exact_owner_contract(self) -> None:
        self.assertEqual(
            self.selectors["summary"],
            {
                "bare_button_route_count": 14,
                "hold_count": 0,
                "retarget_anchor_count": 185,
                "retarget_route_count": 166,
                "route_count": 180,
            },
        )
        self.assertEqual(set(self.by_route), repair.expected_day_keys())
        self.assertEqual(
            self.selectors["applied_source_plan"]["sha256"],
            repair.APPLIED_SOURCE_PLAN_SHA256,
        )
        self.assertEqual(
            repair.sha256_file(repair.APPLIED_SOURCE_PLAN),
            repair.APPLIED_SOURCE_PLAN_SHA256,
        )

    def test_historical_registry_cannot_authorize_prepare_or_apply(self) -> None:
        with self.assertRaisesRegex(repair.RepairError, "cannot authorize"):
            repair.load_inputs()

    def test_reference_only_dispute_is_resolved_to_bare_buttons(self) -> None:
        reference_only = {
            "3SW-Wk1-Day1",
            "3SW-Wk2-Day1",
            "3SW-Wk3-Day1",
            "4SW-Wk4-Day2",
        }
        for route_id in reference_only:
            with self.subTest(route_id=route_id):
                self.assertEqual(
                    self.by_route[route_id]["strategy"],
                    "insert_bare_copy_button",
                )

    def test_no_selector_targets_assignment_rubric_word_bank_or_reference(self) -> None:
        forbidden_fragments = (
            "rubric",
            "word-bank",
            "bilingual",
            "-model.",
            "career-evidence-guide.pdf",
            "occupation-reference",
        )
        for route in self.selectors["routes"]:
            for selector in route.get("selectors", []):
                name = selector["source_file_display_name"].lower()
                with self.subTest(route_id=route["route_id"], name=name):
                    self.assertTrue(name.endswith(".pdf"))
                    self.assertFalse(
                        any(fragment in name for fragment in forbidden_fragments)
                    )

    def test_exact_selectors_still_match_immutable_source_backup(self) -> None:
        for route_id, route in self.by_route.items():
            if route["strategy"] != "retarget_response_work_pdf_anchor":
                continue
            records = repair.anchor_records(self.backup_by_route[route_id]["body"])
            for selector in route["selectors"]:
                matches = []
                for record in records:
                    file_match = repair.re.search(r"/files/(\d+)", record["href"])
                    if (
                        record["text"] == selector["anchor_text"]
                        and file_match
                        and int(file_match.group(1)) == selector["source_file_id"]
                        and repair.sha256_text(record["href"])
                        == selector["source_href_sha256"]
                        and repair.sha256_text(record["open_tag"])
                        == selector["source_open_tag_sha256"]
                    ):
                        matches.append(record)
                with self.subTest(route_id=route_id, text=selector["anchor_text"]):
                    self.assertEqual(len(matches), 1)


class DesiredBodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        selectors, _, backup = repair.load_inputs(allow_historical_registry=True)
        cls.routes = {row["route_id"]: row for row in selectors["routes"]}
        cls.pages = {
            row["route_id"]: row
            for row in backup["pages"]
            if row["role"] == "student"
        }

    def test_all_180_desired_bodies_are_compact_and_exactly_routed(self) -> None:
        anchor_total = 0
        bare_total = 0
        for route_id in sorted(self.routes):
            route = self.routes[route_id]
            desired, proof = repair.desired_body(
                self.pages[route_id]["body"], route
            )
            anchor_total += proof["retargeted_anchor_count"]
            bare_total += proof["retargeted_anchor_count"] == 0
            with self.subTest(route_id=route_id):
                self.assertNotIn(f'id="{repair.BLOCK_ID}"', desired)
                self.assertNotIn(
                    "Type in your copy and submit or share it the way your teacher directs",
                    desired,
                )
                self.assertEqual(
                    sum(
                        record["href"] == route["copy_url"]
                        for record in repair.anchor_records(desired)
                    ),
                    len(route.get("selectors", [])) or 1,
                )
        self.assertEqual(anchor_total, 185)
        self.assertEqual(bare_total, 14)

    def test_selected_anchor_keeps_text_style_and_location(self) -> None:
        route = self.routes["1SW-Wk0-Day1"]
        before = self.pages["1SW-Wk0-Day1"]["body"]
        after, _ = repair.desired_body(before, route)
        old = next(
            record
            for record in repair.anchor_records(before)
            if record["text"] == "Open the CCE First Week Goal-Setting Sheet"
        )
        new = next(
            record
            for record in repair.anchor_records(after)
            if record["text"] == old["text"]
        )
        self.assertIn("display:inline-block", new["open_tag"].replace(" ", ""))
        self.assertEqual(new["href"], route["copy_url"])
        self.assertNotIn("data-api-endpoint", new["open_tag"])
        self.assertNotIn("data-api-returntype", new["open_tag"])
        self.assertEqual(before[: old["start"]], after[: new["start"]])

    def test_unselected_resource_links_remain_byte_exact(self) -> None:
        route_id = "1SW-Wk0-Day4"
        before = self.pages[route_id]["body"]
        after, _ = repair.desired_body(before, self.routes[route_id])
        for label in (
            "Open the 12-point rubric",
            "Open the sentence-stem version",
            "open bilingual support",
        ):
            old = next(
                record for record in repair.anchor_records(before) if record["text"] == label
            )
            new = next(
                record for record in repair.anchor_records(after) if record["text"] == label
            )
            with self.subTest(label=label):
                self.assertEqual(new["open_tag"], old["open_tag"])
                self.assertEqual(new["inner"], old["inner"])

    def test_bare_button_has_no_route_menu_or_process_prose(self) -> None:
        route = self.routes["1SW-Wk0-Day2"]
        body, proof = repair.desired_body(
            self.pages["1SW-Wk0-Day2"]["body"], route
        )
        self.assertEqual(proof["retargeted_anchor_count"], 0)
        self.assertIn(route["button_label"], repair.visible_text(body))
        self.assertNotIn("Response Home</strong>", body)
        self.assertNotIn("Complete this work in one place only", body)
        self.assertIn("background:#1f617a", body)
        self.assertNotIn("background:#1a73e8", body)

    def test_wk0_bare_buttons_use_reviewed_point_of_use_headings(self) -> None:
        expected = {
            "1SW-Wk0-Day2": "6. Move the result to your private response",
            "1SW-Wk0-Day3": "4. Make one connection",
            "1SW-Wk0-Day5": "2. Complete your career table",
        }
        for route_id, heading in expected.items():
            route = self.routes[route_id]
            desired, _ = repair.desired_body(self.pages[route_id]["body"], route)
            button_position = desired.index(route["button_label"])
            heading_position = desired.index(heading)
            _, heading_end = repair.exact_heading_range(desired, route)
            with self.subTest(route_id=route_id):
                self.assertLess(heading_position, button_position)
                self.assertEqual(route["insertion_heading"]["text"], heading)
                self.assertTrue(desired[heading_end:].lstrip().startswith("<p><a "))

    def test_reviewed_pdf_specific_labels_are_corrected(self) -> None:
        expected = {
            "1SW-Wk1-Day1": "Open the Day 1 exit ticket",
            "1SW-Wk1-Day4": "Open the Robots for Crayons action plan",
        }
        for route_id, label in expected.items():
            desired, _ = repair.desired_body(
                self.pages[route_id]["body"], self.routes[route_id]
            )
            copy_labels = [
                record["text"]
                for record in repair.anchor_records(desired)
                if record["href"] == self.routes[route_id]["copy_url"]
            ]
            with self.subTest(route_id=route_id):
                self.assertIn(label, copy_labels)

    def test_no_copy_link_label_claims_pdf_or_printable(self) -> None:
        for route_id, route in self.routes.items():
            desired, _ = repair.desired_body(self.pages[route_id]["body"], route)
            for record in repair.anchor_records(desired):
                if record["href"] != route["copy_url"]:
                    continue
                with self.subTest(route_id=route_id, label=record["text"]):
                    self.assertIsNone(
                        repair.re.search(r"\b(?:PDF|printable)\b", record["text"], repair.re.I)
                    )

    def test_body_only_payload_never_sends_publication_or_dates(self) -> None:
        self.assertEqual(
            repair.body_only_payload("<p>desired</p>"),
            {"wiki_page[body]": "<p>desired</p>"},
        )


class ArtifactTests(unittest.TestCase):
    def test_private_immutable_writer_is_create_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "plan.json"
            repair.write_private_immutable(path, {"ok": True})
            self.assertEqual(path.stat().st_mode & 0o777, 0o400)
            with self.assertRaises(FileExistsError):
                repair.write_private_immutable(path, {"ok": False})


class ResumeGuardTests(unittest.IsolatedAsyncioTestCase):
    def sample_target(self) -> dict:
        return {
            "route_id": "1SW-Wk1-Day1",
            "page_id": 101,
            "page_url": "student-page",
            "page_title": "STUDENT: Sample",
            "before_body": "<p>before</p>",
            "after_body": "<p>after</p>",
            "publication_and_date_guard": {
                "published": False,
                "front_page": False,
                "dates": {field: None for field in repair.PAGE_DATE_FIELDS},
            },
        }

    def live(self, body: str) -> dict:
        return {
            "page_id": 101,
            "url": "student-page",
            "title": "STUDENT: Sample",
            "body": body,
            "published": False,
            "front_page": False,
            **{field: None for field in repair.PAGE_DATE_FIELDS},
        }

    def test_resume_classifies_exact_before_and_exact_after(self) -> None:
        target = self.sample_target()
        self.assertEqual(
            repair.classify_live_body(target, self.live(target["before_body"])),
            "before",
        )
        self.assertEqual(
            repair.classify_live_body(target, self.live(target["after_body"])),
            "after",
        )

    def test_prepare_accepts_only_known_bad_or_desired(self) -> None:
        self.assertEqual(
            repair.classify_prepare_body("bad", "bad", "desired"), "before"
        )
        self.assertEqual(
            repair.classify_prepare_body("desired", "bad", "desired"), "after"
        )
        with self.assertRaisesRegex(repair.RepairError, "neither known"):
            repair.classify_prepare_body("teacher edit", "bad", "desired")

    def test_third_body_and_guard_change_fail_closed(self) -> None:
        target = self.sample_target()
        with self.assertRaisesRegex(repair.RepairError, "third body"):
            repair.classify_live_body(target, self.live("<p>teacher edit</p>"))
        changed = self.live(target["before_body"])
        changed["published"] = True
        with self.assertRaisesRegex(repair.RepairError, "guard changed"):
            repair.classify_live_body(target, changed)
        changed_title = self.live(target["before_body"])
        changed_title["title"] = "Renamed by teacher"
        with self.assertRaisesRegex(repair.RepairError, "title changed"):
            repair.classify_live_body(target, changed_title)

    async def test_readback_retries_only_stale_before(self) -> None:
        target = self.sample_target()
        sequence = [self.live(target["before_body"]), self.live(target["after_body"])]
        with mock.patch.object(
            repair, "get_page", new=mock.AsyncMock(side_effect=sequence)
        ) as get_page:
            result = await repair.readback_after(object(), target)
        self.assertEqual(result["body"], target["after_body"])
        self.assertEqual(get_page.await_count, 2)

    async def test_readback_does_not_retry_a_third_body(self) -> None:
        target = self.sample_target()
        with mock.patch.object(
            repair,
            "get_page",
            new=mock.AsyncMock(return_value=self.live("<p>teacher edit</p>")),
        ) as get_page:
            with self.assertRaisesRegex(repair.RepairError, "third body"):
                await repair.readback_after(object(), target)
        self.assertEqual(get_page.await_count, 1)


if __name__ == "__main__":
    unittest.main()
