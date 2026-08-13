import tempfile
import unittest
from pathlib import Path

import yaml

from ops.scripts.validate_franky_contracts import (
    DEFAULT_REPERTOIRE,
    DEFAULT_RESULT,
    DEFAULT_TASK,
    validate,
)

ROOT = Path(__file__).resolve().parents[3]


class FrankyContractTests(unittest.TestCase):
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

    def test_mutation_requires_explicit_authority(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = yaml.safe_load(DEFAULT_RESULT.read_text(encoding="utf-8"))
        task["authority"]["mutation"] = "approval_required"
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "explicit mutation authority"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_unexplained_not_assessed_cannot_be_acceptance_ready(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = yaml.safe_load(DEFAULT_RESULT.read_text(encoding="utf-8"))
        result["closure"]["proof"] = "NOT_ASSESSED"
        result["unresolved"]["limitations"] = []
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "NOT_ASSESSED closure"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_lifecycle_result_uses_canonical_capability(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = yaml.safe_load(DEFAULT_RESULT.read_text(encoding="utf-8"))
        result["routing"]["lifecycle_capability"] = "session-closeout"
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "shared-session-closeout"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_nonconsequential_result_may_omit_lifecycle(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = yaml.safe_load(DEFAULT_RESULT.read_text(encoding="utf-8"))
        task["intent"] = {"mode": "audit", "completion": "bounded"}
        result["routing"].pop("lifecycle_capability")
        tmp, task_path, result_path = self._write_case(task, result)
        validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_repertoire_rejects_unknown_capability_reference(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        task["required_capabilities"].append("unregistered-capability")
        tmp, task_path, result_path = self._write_case(task, yaml.safe_load(DEFAULT_RESULT.read_text(encoding="utf-8")))
        with self.assertRaisesRegex(ValueError, "not in Franky repertoire"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_acceptance_ready_requires_independent_review(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = yaml.safe_load(DEFAULT_RESULT.read_text(encoding="utf-8"))
        result["review"] = {"required": True, "status": "PASS", "reviewer": "franky"}
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "non-self reviewer"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_acceptance_ready_requires_complete_lifecycle_evidence(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = yaml.safe_load(DEFAULT_RESULT.read_text(encoding="utf-8"))
        result["lifecycle"]["evidence"] = result["lifecycle"]["evidence"][:-1]
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "ordered evidence"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_acceptance_ready_rejects_blocked_closure(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = yaml.safe_load(DEFAULT_RESULT.read_text(encoding="utf-8"))
        result["closure"]["references"] = "BLOCKED"
        result["lifecycle"]["evidence"] = result["lifecycle"]["evidence"][:-1]
        result["lifecycle"]["evidence"][-1]["status"] = "BLOCKED"
        result["lifecycle"]["state"] = "CLOSURE"
        result["status"] = "blocked"
        result["review"] = {"required": True, "status": "NOT_ASSESSED"}
        tmp, task_path, result_path = self._write_case(task, result)
        validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_consequential_routing_requires_supporting_capability(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = yaml.safe_load(DEFAULT_RESULT.read_text(encoding="utf-8"))
        result["routing"]["supporting_capabilities"] = []
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "impact-triggered supporting"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_impact_evidence_must_bind_to_validation_source_state(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = yaml.safe_load(DEFAULT_RESULT.read_text(encoding="utf-8"))
        result["routing"]["impact_evidence"]["source_state"] = "stale-state"
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "match validation source_state"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_result_cannot_downgrade_task_required_review(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = yaml.safe_load(DEFAULT_RESULT.read_text(encoding="utf-8"))
        result["review"] = {"required": False, "status": "NOT_APPLICABLE", "reviewer": "Athena"}
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "downgrade"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()

    def test_blocked_result_requires_ordered_lifecycle_prefix(self):
        task = yaml.safe_load(DEFAULT_TASK.read_text(encoding="utf-8"))
        result = yaml.safe_load(DEFAULT_RESULT.read_text(encoding="utf-8"))
        result["status"] = "blocked"
        result["lifecycle"] = {
            "state": "ROUTING",
            "evidence": [{"state": "VALIDATION", "status": "BLOCKED", "source": "test"}],
        }
        tmp, task_path, result_path = self._write_case(task, result)
        with self.assertRaisesRegex(ValueError, "ordered evidence prefix"):
            validate(task_path, result_path, DEFAULT_REPERTOIRE)
        tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
