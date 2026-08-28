import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "build/canvas/verify_student_response_link_sources.py"
SPEC = importlib.util.spec_from_file_location("verify_student_response_link_sources", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class StudentResponseLinkSourceTests(unittest.TestCase):
    def test_reviewed_one_button_contract(self):
        self.assertEqual(
            MODULE.verify(),
            {
                "route_count": 180,
                "selector_count": 185,
                "template_selector_count": 48,
                "builder_selector_count": 137,
                "point_of_use_button_count": 14,
                "template_button_count": 10,
                "builder_button_count": 4,
            },
        )


if __name__ == "__main__":
    unittest.main()
