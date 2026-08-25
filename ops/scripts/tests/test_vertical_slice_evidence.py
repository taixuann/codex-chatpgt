import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "ops/scripts"))
import validate_vertical_slice_evidence as validator


class VerticalSliceEvidenceTests(unittest.TestCase):
    def test_checked_in_packet_has_bound_authority_and_review(self):
        validator.validate(
            ROOT / "documentation/reviews/ISSUE-7-59-61-REAL-SCIENTIFIC-VERTICAL-SLICE.yaml",
            ROOT / "documentation/reviews/ISSUE-7-59-61-ATHENA-REVIEW.yaml",
        )


if __name__ == "__main__":
    unittest.main()
