import unittest
from pathlib import Path

import yaml

from ops.scripts.runtime_materialization import (
    MaterializationError,
    execute,
    resolve_context,
    transition_artifact,
    validate_artifact,
)


ROOT = Path(__file__).resolve().parents[3]


class RuntimeMaterializationTests(unittest.TestCase):
    def context(self, skill="control-plane-audit", **permissions):
        return resolve_context(
            agent="franky",
            skill=skill,
            authority="issue-56",
            permissions={"read": True, "mutate": False, **permissions},
            agents_root=ROOT / "agents",
            catalog_path=ROOT / "manifests/skill-catalog.yaml",
        )

    def test_session_packet_management_is_admitted_for_franky(self):
        context = self.context(skill="session-packet-management")
        self.assertEqual(context["skill"], "session-packet-management")

    def input_artifact(self):
        return {
            "request_id": "req-56-001",
            "agent": "franky",
            "skill": "control-plane-audit",
            "provenance": {"source": "fixture"},
            "lifecycle_state": "DRAFT",
            "validation_result": "PASS",
        }

    def test_valid_agent_selection_and_execution_artifact(self):
        context = self.context()
        self.assertEqual(context["validation_state"], "RESOLVED")
        output = execute(context, self.input_artifact(), request_id="req-56-001")
        self.assertEqual(output["lifecycle_state"], "VALIDATED")
        self.assertEqual(output["validation_result"], "PASS")
        self.assertIn("input_digest", output["provenance"])

    def test_invalid_skill_selection(self):
        with self.assertRaisesRegex(MaterializationError, "canonical_active"):
            resolve_context(
                agent="franky",
                skill="scientific-evidence-synthesis",
                authority="issue-56",
                permissions={"read": True},
                agents_root=ROOT / "agents",
                catalog_path=ROOT / "manifests/skill-catalog.yaml",
            )

    def test_missing_provenance(self):
        artifact = self.input_artifact()
        artifact["provenance"] = {}
        with self.assertRaisesRegex(MaterializationError, "provenance.source"):
            validate_artifact(artifact)

    def test_forbidden_mutation_is_rejected(self):
        output = execute(self.context(), self.input_artifact(), request_id="req-56-001", mutation_requested=True)
        self.assertEqual(output["validation_result"], "REJECT")
        self.assertEqual(output["execution"]["reason"], "mutation_not_authorized")

    def test_audit_requires_read_permission(self):
        output = execute(
            self.context(read=False), self.input_artifact(), request_id="req-56-001"
        )
        self.assertEqual(output["validation_result"], "REJECT")
        self.assertEqual(output["execution"]["reason"], "read_not_authorized")

    def test_audit_rejects_missing_read_permission(self):
        context = resolve_context(
            agent="franky",
            skill="control-plane-audit",
            authority="issue-56",
            permissions={"mutate": False},
            agents_root=ROOT / "agents",
            catalog_path=ROOT / "manifests/skill-catalog.yaml",
        )
        output = execute(context, self.input_artifact(), request_id="req-56-001")
        self.assertEqual(output["validation_result"], "REJECT")
        self.assertEqual(output["execution"]["reason"], "read_not_authorized")

    def test_unsupported_action_is_rejected(self):
        with self.assertRaisesRegex(MaterializationError, "unsupported execution action"):
            execute(self.context(), self.input_artifact(), request_id="req-56-001", action="linked-project-write")

    def test_input_identity_must_match_context(self):
        artifact = self.input_artifact()
        artifact["agent"] = "prometheus"
        with self.assertRaisesRegex(MaterializationError, "identity"):
            execute(self.context(), artifact, request_id="req-56-001")

    def test_non_boolean_permission_is_rejected(self):
        with self.assertRaisesRegex(MaterializationError, "permission values must be boolean"):
            self.context(mutate="false")

    def test_invalid_artifact_transition(self):
        with self.assertRaisesRegex(MaterializationError, "invalid artifact transition"):
            transition_artifact(self.input_artifact(), "ACCEPTED")

    def test_transition_artifact_records_transition_evidence(self):
        output = transition_artifact(self.input_artifact(), "VALIDATED")
        self.assertEqual(output["previous_state"], "DRAFT")
        self.assertEqual(output["transition"], "DRAFT->VALIDATED")

    def test_nested_mapping_order_does_not_change_digest(self):
        first = self.input_artifact()
        second = self.input_artifact()
        first["provenance"] = {"source": "fixture", "nested": {"a": 1, "b": 2}}
        second["provenance"] = {"nested": {"b": 2, "a": 1}, "source": "fixture"}
        first_output = execute(self.context(), first, request_id="req-56-001")
        second_output = execute(self.context(), second, request_id="req-56-001")
        self.assertEqual(
            first_output["provenance"]["input_digest"],
            second_output["provenance"]["input_digest"],
        )

    def test_checked_in_artifact_evidence_is_valid(self):
        fixture = yaml.safe_load(
            (ROOT / "ops/schemas/examples/runtime-materialization-v1.yaml").read_text(encoding="utf-8")
        )
        validate_artifact(fixture["output_artifact"])
        self.assertEqual(fixture["forbidden_mutation"]["validation_result"], "REJECT")


if __name__ == "__main__":
    unittest.main()
