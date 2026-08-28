from __future__ import annotations

import unittest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

CANVAS_DIR = Path(__file__).resolve().parents[1]
if str(CANVAS_DIR) not in sys.path:
    sys.path.insert(0, str(CANVAS_DIR))

import normalize_embedded_image_access as normalizer


class VisibilityTests(unittest.TestCase):
    def test_availability_dates_are_restrictions(self) -> None:
        self.assertFalse(
            normalizer.file_is_visible(
                {
                    "locked": False,
                    "hidden": False,
                    "lock_at": None,
                    "unlock_at": "2026-09-01T12:00:00Z",
                }
            )
        )

    def test_course_folder_map_rejects_foreign_context(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "foreign context"):
            normalizer.validated_course_folders(
                [{"id": 7, "context_type": "Course", "context_id": 11111}],
                98060,
            )


class CourseContainmentTests(unittest.IsolatedAsyncioTestCase):
    async def test_foreign_file_aborts_before_any_write(self) -> None:
        writes: list[str] = []

        async def fake_api(client, method: str, path: str, **kwargs):
            if method == "GET" and path == "/files/42":
                return {
                    "id": 42,
                    "folder_id": 7,
                    "content-type": "image/png",
                    "locked": True,
                    "hidden": False,
                }
            if method == "PUT":
                writes.append(path)
            raise AssertionError((method, path, kwargs))

        with (
            patch.object(
                normalizer,
                "discover",
                AsyncMock(return_value=(None, {42})),
            ),
            patch.object(
                normalizer,
                "paged",
                AsyncMock(
                    return_value=[
                        {
                            "id": 8,
                            "context_type": "Course",
                            "context_id": 98060,
                            "parent_folder_id": None,
                        }
                    ]
                ),
            ),
            patch.object(normalizer, "api", fake_api),
        ):
            with self.assertRaisesRegex(RuntimeError, "outside course 98060"):
                await normalizer.normalize(
                    object(),
                    check_only=False,
                    manage_home=False,
                )

        self.assertEqual(writes, [])


if __name__ == "__main__":
    unittest.main()
