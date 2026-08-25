import unittest
from pathlib import Path
import sys
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "ops/scripts"))
import validate_vertical_slice_evidence as validator


class VerticalSliceEvidenceTests(unittest.TestCase):
    packet_path = ROOT / "documentation/reviews/ISSUE-7-59-61-REAL-SCIENTIFIC-VERTICAL-SLICE.yaml"
    review_path = ROOT / "documentation/reviews/ISSUE-7-59-61-ATHENA-REVIEW.yaml"

    def test_checked_in_packet_has_bound_authority_and_review(self):
        validator.validate(self.packet_path, self.review_path)

    def _mutated(self, packet_mutator=lambda _: None, review_mutator=lambda _: None):
        packet = yaml.safe_load(self.packet_path.read_text())
        review = yaml.safe_load(self.review_path.read_text())
        packet_mutator(packet)
        review_mutator(review)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            review_dir = root / "documentation" / "reviews"
            review_dir.mkdir(parents=True)
            packet_file = review_dir / self.packet_path.name
            review_file = review_dir / self.review_path.name
            packet_file.write_text(yaml.safe_dump(packet, sort_keys=False))
            review_file.write_text(yaml.safe_dump(review, sort_keys=False))
            with self.assertRaises(ValueError):
                validator.validate(packet_file, review_file)

    def test_rejects_malformed_authority_blob(self):
        self._mutated(lambda p: p["project_context"]["authority_sources"][0].update(git_blob="bogus"))

    def test_rejects_unbound_review_project_commit(self):
        self._mutated(review_mutator=lambda r: r.update(reviewed_project_commit="0" * 40))

    def test_rejects_missing_review_criteria(self):
        self._mutated(review_mutator=lambda r: r.pop("criteria_refs"))


if __name__ == "__main__":
    unittest.main()
