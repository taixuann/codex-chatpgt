import unittest
from pathlib import Path
import sys
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "ops/scripts"))
import validate_archive_index as validator


class ArchiveIndexTests(unittest.TestCase):
    def test_checked_in_archive_is_reversible_and_complete(self):
        validator.validate(ROOT / "documentation/archive/20260826/ARCHIVE-INDEX.yaml")

    def test_missing_archived_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            index_dir = root / "documentation/archive/20260826"
            index_dir.mkdir(parents=True)
            index = ROOT / "documentation/archive/20260826/ARCHIVE-INDEX.yaml"
            data = yaml.safe_load(index.read_text(encoding="utf-8"))
            data["entries"] = [{
                "original_path": "documentation/plans/missing.md",
                "archived_path": "documentation/archive/20260826/plans/missing.md",
                "status": "completed",
                "reason": "test",
            }]
            temp = index_dir / "ARCHIVE-INDEX.yaml"
            temp.write_text(yaml.safe_dump(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                validator.validate(temp)


if __name__ == "__main__":
    unittest.main()
