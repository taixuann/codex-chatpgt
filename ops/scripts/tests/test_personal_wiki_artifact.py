import unittest
from pathlib import Path
import sys
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "ops/scripts"))
import validate_personal_wiki_artifact as validator


class PersonalWikiArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.example = yaml.safe_load((ROOT / "ops/schemas/examples/personal-wiki-artifact.yaml").read_text())

    def validate_document(self, document):
        with tempfile.NamedTemporaryFile("w", suffix=".yaml") as handle:
            yaml.safe_dump(document, handle)
            handle.flush()
            validator.validate(Path(handle.name))

    def test_checked_in_example(self):
        validator.validate(ROOT / "ops/schemas/examples/personal-wiki-artifact.yaml")

    def test_project_authority_cannot_be_claimed(self):
        document = dict(self.example)
        document["authority_status"] = "PROJECT_AUTHORITY"
        with self.assertRaises(ValueError):
            self.validate_document(document)

    def test_scientific_wiki_target_is_rejected(self):
        document = dict(self.example)
        document["promotion"] = dict(document["promotion"], target="scientific_wiki")
        with self.assertRaises(ValueError):
            self.validate_document(document)

    def test_missing_provenance_is_rejected(self):
        document = dict(self.example)
        document["provenance"] = {"source_refs": []}
        with self.assertRaises(ValueError):
            self.validate_document(document)

    def test_future_consumer_requires_explicit_authorization(self):
        document = dict(self.example)
        document["context_consumption"] = dict(document["context_consumption"], authorized_consumers=["feynman", "future_consumer"])
        self.validate_document(document)

    def test_automatic_mutation_attempt_is_rejected(self):
        document = dict(self.example)
        document["promotion"] = dict(document["promotion"], write_performed=True)
        with self.assertRaises(ValueError):
            self.validate_document(document)


if __name__ == "__main__":
    unittest.main()
