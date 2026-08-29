import copy
import tempfile
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
    def test_undeclared_request_field_rejected(self):
        value = copy.deepcopy(self.request); value["workflow_step"] = "repair"
        with self.assertRaisesRegex(ValueError, "undeclared"):
            validator.validate_request(value)
    def test_undeclared_result_field_rejected(self):
        value = copy.deepcopy(self.result); value["system_accepted"] = False
        with self.assertRaisesRegex(ValueError, "undeclared"):
            validator.validate_result(value)
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
    def _mutated_case_is_rejected(self, case_id, mutate):
        cases = yaml.safe_load((ROOT / "scripts/fixtures/athena-review-cases.yaml").read_text())
        case = next(item for item in cases["cases"] if item["id"] == case_id)
        mutate(case)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as handle:
            yaml.safe_dump(cases, handle)
            handle.flush()
            with self.assertRaises(ValueError): validator.validate_cases(Path(handle.name))
    def test_conflicting_authority_fields_are_all_guarded(self):
        for field, value in (("human_required", False), ("human_reason", "wrong"), ("human_question", "")):
            self._mutated_case_is_rejected("conflicting_authority", lambda c, f=field, v=value: c["result"].__setitem__(f, v))
    def test_trivial_review_required_flag_is_guarded(self):
        self._mutated_case_is_rejected("trivial_change_not_required", lambda c: c["result"].__setitem__("review_required", True))
    def test_excluded_surface_fields_are_guarded(self):
        self._mutated_case_is_rejected("excluded_runtime_surface", lambda c: c["result"].__setitem__("not_reviewed", []))
        self._mutated_case_is_rejected("excluded_runtime_surface", lambda c: c["result"].__setitem__("limitations", []))
    def test_every_parent_route_and_spawn_flag_is_guarded(self):
        for case_id in ("implementation_routes_prometheus", "missing_context_routes_argus", "control_plane_routes_franky"):
            self._mutated_case_is_rejected(case_id, lambda c: c["result"].__setitem__("spawned", True))
            self._mutated_case_is_rejected(case_id, lambda c: c["result"].__setitem__("handoff", "wrong"))
    def test_final_acceptance_and_mutation_denial_are_guarded(self):
        self._mutated_case_is_rejected("result_cannot_accept", lambda c: c["result"].__setitem__("final_acceptance", True))
        self._mutated_case_is_rejected("mutation_denied", lambda c: c["request"].__setitem__("authority_mutation", "allowed"))

if __name__ == "__main__": unittest.main()
