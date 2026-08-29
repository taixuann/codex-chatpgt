import copy
import unittest
from pathlib import Path
import sys
import yaml
sys.path.insert(0, str(Path(__file__).parents[1]))
import validate_athena_review as validator

ROOT = Path(__file__).parents[2]

class AthenaReviewContractTests(unittest.TestCase):
    def setUp(self):
        self.request = yaml.safe_load((ROOT / "scripts/fixtures/athena-review-request.yaml").read_text())
        self.result = yaml.safe_load((ROOT / "scripts/fixtures/athena-review-result.yaml").read_text())
    def test_request_contract(self): validator.validate_request(self.request)
    def test_result_contract(self): validator.validate_result(self.result, self.result["target_revision"])
    def test_stale_revision_rejected(self):
        with self.assertRaisesRegex(ValueError, "stale"):
            validator.validate_result(self.result, "different")
    def test_missing_rubric_rejected(self):
        value = copy.deepcopy(self.request); value["criteria"]["source"] = []
        with self.assertRaises(ValueError): validator.validate_request(value)
    def test_not_assessed_cannot_clear(self):
        value = copy.deepcopy(self.result); value["recommendation"]["status"] = "clear_for_parent_decision"
        with self.assertRaises(ValueError): validator.validate_result(value)
    def test_final_acceptance_forbidden(self):
        value = copy.deepcopy(self.result); value["system_accepted"] = True
        with self.assertRaises(ValueError): validator.validate_result(value)
    def test_case_fixture(self): validator.validate_cases(ROOT / "scripts/fixtures/athena-review-cases.yaml")

if __name__ == "__main__": unittest.main()
