from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parents[1]))
from scripts.validate_session_state import validate


class SessionStateTests(unittest.TestCase):
    def test_closeout_template_is_not_a_canonical_state_record(self) -> None:
        result = validate(Path(__file__).parents[1] / "templates/closeout-report.yaml")
        self.assertFalse(result["valid"])
        self.assertIn("change.yaml", " ".join(result["errors"]))

    def test_valid_change_record_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "change.yaml"
            path.write_text("operation: audit\nchanged_paths: []\nvalidation: []\npromotion: none\n", encoding="utf-8")
            result = validate(path)
            self.assertTrue(result["valid"])


if __name__ == "__main__":
    unittest.main()
