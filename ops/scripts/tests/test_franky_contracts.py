import tempfile
import unittest
from pathlib import Path

import yaml

from ops.scripts.validate_franky_contracts import (
    DEFAULT_REPERTOIRE,
    DEFAULT_RESULT,
    DEFAULT_TASK,
    validate as validate_contract,
)

ROOT = Path(__file__).resolve().parents[3]


def validate(task_path, result_path, repertoire_path):
    return validate_contract(
        task_path,
        result_path,
        repertoire_path,
        allow_fixture_review_record=True,
    )


class FrankyContractTests(unittest.TestCase):
    def _validate(self, task_path, result_path):
        return validate(
            task_path,
            result_path,
            DEFAULT_REPERTOIRE,
            allow_fixture_review_record=True,
        )

    def test_contracts_remain_thin_and_non_executable(self):
        task_schema = yaml.safe_load((ROOT / "ops/schemas/franky-task.schema.yaml").read_text(encoding="utf-8"))
        result_schema = yaml.safe_load((ROOT / "ops/schemas/franky-result.schema.yaml").read_text(encoding="utf-8"))
        self.assertNotIn("transitions", task_schema["properties"])
        self.assertNotIn("workflow_state", task_schema["properties"])
        lifecycle_properties = result_schema["properties"]["lifecycle"]["properties"]
        self.assertEqual(set(lifecycle_properties), {"state", "evidence"})
        self.assertNotIn("transition", lifecycle_properties)
        self.assertNotIn("persistence", lifecycle_properties)

    def test_checked_in_contracts_pass(self):
        validate(DEFAULT_TASK, DEFAULT_RESULT, DEFAULT_REPERTOIRE)

    def _write_case(self, task, result):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        task_path = root / "task.yaml"
        result_path = root / "result.yaml"
        task_path.write_text(yaml.safe_dump(task, sort_keys=False), encoding="utf-8")
        result_path.write_text(yaml.safe_dump(result, sort_keys=False), encoding="utf-8")
        return tmp, task_path, result_path

    def _acceptance_result(self):
        result = yaml.safe_load(DEFAULT_RESULT.read_text(encoding="utf-8"))
        if result["lifecycle"]["state"] == "ACCEPTANCE_READY":
            result["review"]["review_record"] = "ops/scripts/fixtures/athena-review-pass.yaml"
            return result
        result["status"] = "acceptance_ready"
        result["lifecycle"]["state"] = "ACCEPTANCE_READY"
        result["lifecycle"]["evidence"][-1]["status"] = "PASS"
        result["lifecycle"]["evidence"][-1]["state"] = "CLOSURE"
        result["lifecycle"]["evidence"][-1]["source"] = "closure-matrix"
        result["lifecycle"]["evidence"][-1]["provenance"]["result"] = "PASS"
        result["lifecycle"]["evidence"].append({
            "state": "ACCEPTANCE_READY",
            "status": "PASS",
            "source": "parent-review-boundary",
            "provenance": {
                "source_state": "review-record",
                "commit": "HEAD",
                "observed_at": "2026-08-13T13:00:00Z",
                "result": "PASS",
            },
        })
        result["closure"]["proof"] = "PASS"
        result["review"]["status"] = "PASS"
        result["review"]["review_record"] = "ops/scripts/fixtures/athena-review-pass.yaml"
        result["unresolved"]["blockers"] = []
        return result

    def test_mutation_requires_explicit_authority(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = self._acceptance_result()
        task["authority"]["mutation"] = "approval_required"
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "explicit mutation authority"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_task_schema_rejects_missing_scope(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = yaml.safe_load(DEFAULT_RESULT.read_text(encoding="utf-8"))
        task.pop("scope")
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "missing required field.*scope"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_task_schema_rejects_missing_authority(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = yaml.safe_load(DEFAULT_RESULT.read_text(encoding="utf-8"))
        task.pop("authority")
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "missing required field.*authority"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_architecture_change_requires_review_flag(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = yaml.safe_load(DEFAULT_RESULT.read_text(encoding="utf-8"))
        task["authority"]["architecture_change"] = "allowed"
        task.pop("review")
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "architecture-change request"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_unexplained_not_assessed_cannot_be_acceptance_ready(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = self._acceptance_result()
        result["closure"]["proof"] = "NOT_ASSESSED"
        result["unresolved"]["limitations"] = []
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "NOT_ASSESSED closure"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_lifecycle_result_uses_canonical_capability(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = self._acceptance_result()
        result["routing"]["lifecycle_capability"] = "session-closeout"
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "shared-session-closeout"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_nonconsequential_result_may_omit_lifecycle(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = self._acceptance_result()
        task["intent"] = {"mode": "audit", "completion": "bounded"}
        result["routing"].pop("lifecycle_capability")
        tmp, task_path, result_path = self._write_case(task, result)
        validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_repertoire_rejects_unknown_capability_reference(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        task["required_capabilities"].append("unregistered-capability")
        tmp, task_path, result_path = self._write_case(task, self._acceptance_result())
        with self.assertRaisesRegex(ValueError, "not in Franky repertoire"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_acceptance_ready_requires_independent_review(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = self._acceptance_result()
        result["review"] = {
            "required": True,
            "status": "PASS",
            "reviewer": "franky",
            "reviewer_id": "franky",
            "reviewer_role": "independent_reviewer",
            "review_session_id": "019ffb72-d034-7193-aefb-f36a240b091f",
            "review_record": "documentation/reviews/ISSUE-57-ATHENA-REVIEW.yaml",
            "scope": ["contract"],
            "not_reviewed": [],
        }
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "bound non-self reviewer"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_acceptance_ready_requires_complete_lifecycle_evidence(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = self._acceptance_result()
        result["lifecycle"]["evidence"] = result["lifecycle"]["evidence"][:-1]
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "ordered evidence"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_acceptance_ready_rejects_blocked_closure(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = self._acceptance_result()
        result["closure"]["references"] = "BLOCKED"
        result["lifecycle"]["evidence"] = result["lifecycle"]["evidence"][:-1]
        result["lifecycle"]["evidence"][-1]["status"] = "BLOCKED"
        result["lifecycle"]["evidence"][-1]["provenance"]["result"] = "BLOCKED"
        result["lifecycle"]["state"] = "CLOSURE"
        result["status"] = "blocked"
        result["review"] = {
            "required": True,
            "status": "NOT_ASSESSED",
            "reviewer_id": "parent-control-plane",
            "reviewer_role": "parent_acceptance",
            "review_session_id": "019ffb72-d034-7193-aefb-f36a240b091f",
            "review_record": "documentation/reviews/ISSUE-57-ATHENA-REVIEW.yaml",
            "scope": ["contract"],
            "not_reviewed": [],
        }
        tmp, task_path, result_path = self._write_case(task, result)
        validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_consequential_routing_requires_supporting_capability(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = self._acceptance_result()
        result["routing"]["supporting_capabilities"] = []
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "impact-triggered supporting"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_impact_evidence_must_bind_to_validation_source_state(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = self._acceptance_result()
        result["routing"]["impact_evidence"]["source_state"] = "stale-state"
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "match validation source_state"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_result_cannot_downgrade_task_required_review(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = self._acceptance_result()
        result["review"] = {
            "required": False,
            "status": "NOT_APPLICABLE",
            "reviewer": "Athena",
            "reviewer_id": "athena",
            "reviewer_role": "independent_reviewer",
            "review_session_id": "019ffb72-d034-7193-aefb-f36a240b091f",
            "review_record": "documentation/reviews/ISSUE-57-ATHENA-REVIEW.yaml",
            "scope": ["contract"],
            "not_reviewed": [],
        }
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "downgrade"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_blocked_result_requires_ordered_lifecycle_prefix(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = self._acceptance_result()
        result["status"] = "blocked"
        result["lifecycle"] = {
            "state": "ROUTING",
            "evidence": [{
                "state": "VALIDATION",
                "status": "BLOCKED",
                "source": "test",
                "provenance": {
                    "source_state": "test",
                    "commit": "HEAD",
                    "observed_at": "2026-08-13T13:00:00Z",
                    "result": "BLOCKED",
                },
            }],
        }
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "ordered evidence prefix"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_provenance_must_match_evidence_freshness_commit(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = self._acceptance_result()
        result["lifecycle"]["evidence"][0]["provenance"]["commit"] = "stale"
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "provenance must share"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_validation_after_mutation_invalidates_acceptance(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = self._acceptance_result()
        result["evidence_freshness"]["mutation_free_since_validation"] = False
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "stale after mutation"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_routing_requires_explanations(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = self._acceptance_result()
        result["routing"]["supporting_reasons"] = []
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "supporting reasons"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_review_record_session_mismatch_is_rejected(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = self._acceptance_result()
        result["review"]["review_session_id"] = "019ffb77-f475-7c43-b692-9fa3ad066580"
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "review_record session"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_review_record_request_changes_cannot_accept(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = self._acceptance_result()
        result["review"]["review_record"] = "ops/scripts/fixtures/athena-review-request-changes.yaml"
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "PASS independent review record"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
