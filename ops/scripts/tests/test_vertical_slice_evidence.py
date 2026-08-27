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

    def test_rejects_missing_independent_binding_criterion(self):
        self._mutated(review_mutator=lambda r: r["criteria_refs"].remove("independent_review_revision_binding"))

    def test_rejects_incomplete_lifecycle_coverage(self):
        self._mutated(review_mutator=lambda r: r["coverage"].update(lifecycle_review_binding="NOT_ASSESSED"))

    def test_rejects_missing_authority_path(self):
        self._mutated(packet_mutator=lambda p: p["project_context"]["authority_sources"].pop())

    def test_rejects_stale_packet_digest(self):
        self._mutated(packet_mutator=lambda p: p["lifecycle"]["athena_review"].update(reviewed_target_digest="sha256:" + "0" * 64))

    def test_rejects_stale_review_target_revision(self):
        self._mutated(review_mutator=lambda r: r.update(reviewed_target_revision="sha256:" + "0" * 64))

    def test_rejects_malformed_authority_container(self):
        self._mutated(packet_mutator=lambda p: p["project_context"].update(authority_sources={}))

    def test_rejects_malformed_yaml_container(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo" / "documentation" / "reviews"
            root.mkdir(parents=True)
            packet_file = root / self.packet_path.name
            review_file = root / self.review_path.name
            packet_file.write_text("- not-a-mapping\n")
            review_file.write_text(self.review_path.read_text())
            with self.assertRaises(ValueError):
                validator.validate(packet_file, review_file)


if __name__ == "__main__":
    unittest.main()
