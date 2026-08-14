import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "ops/scripts"))
import validate_agent_lifecycle as validator


class AgentLifecycleTests(unittest.TestCase):
    def test_registry_and_fixture(self):
        validator.validate(ROOT / "ops/scripts/fixtures/agent-lifecycle.yaml")

    def test_direct_artifact_promotion_is_rejected(self):
        doc = {"artifacts": [{"artifact_id": "a", "lifecycle_state": "VALIDATED", "owner": "p", "producer": "prometheus", "reviewer": None, "authority_status": "process_validated", "evidence_ids": [], "claim_ids": [], "review_ids": []}], "promotions": [{"artifact_id": "a", "target": "canonical-state", "status": "ALLOWED"}]}
        with self.assertRaises(ValueError):
            validator.validate_artifacts(doc)
            validator.validate_evidence_chain(doc)

    def test_shared_contract_requires_provenance(self):
        with self.assertRaises(ValueError):
            validator.validate_shared_contract({"kind": "result.v1", "id": "r", "agent": "prometheus", "provenance": {}, "evidence": [], "claims": [], "unknowns": [], "conflicts": [], "readiness": "READY", "validation_status": "PASS"})

    def test_accepted_artifact_requires_independent_decision_binding(self):
        doc = {"artifacts": [{"artifact_id": "a", "lifecycle_state": "ACCEPTED", "owner": "parent", "producer": "prometheus", "reviewer": "athena", "authority_status": "accepted", "evidence_ids": ["e"], "claim_ids": ["c"], "review_ids": ["r"], "decision_id": "wrong"}], "evidence": [{"id": "e"}], "claims": [{"id": "c", "evidence_ids": ["e"]}], "reviews": [{"id": "r", "reviewer": "athena", "outcome": "PASS", "claim_ids": ["c"]}], "decisions": [{"id": "d", "review_ids": ["r"], "outcome": "ACCEPT"}], "promotions": [{"artifact_id": "a", "decision_id": "d", "target": "canonical-state", "status": "ALLOWED"}]}
        with self.assertRaises(ValueError):
            validator.validate_artifacts(doc)
            validator.validate_evidence_chain(doc)


if __name__ == "__main__":
    unittest.main()
