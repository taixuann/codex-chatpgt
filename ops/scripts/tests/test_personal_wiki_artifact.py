import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "ops/scripts"))
import validate_personal_wiki_artifact as validator


class PersonalWikiArtifactTests(unittest.TestCase):
    def test_checked_in_example(self):
        validator.validate(ROOT / "ops/schemas/examples/personal-wiki-artifact.yaml")

    def test_project_authority_cannot_be_claimed(self):
        document = __import__("yaml").safe_load((ROOT / "ops/schemas/examples/personal-wiki-artifact.yaml").read_text())
        document["authority_status"] = "PROJECT_AUTHORITY"
        path = ROOT / "ops/schemas/examples/.tmp-invalid-personal-wiki.yaml"
        path.write_text(__import__("yaml").safe_dump(document))
        try:
            with self.assertRaises(ValueError):
                validator.validate(path)
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
