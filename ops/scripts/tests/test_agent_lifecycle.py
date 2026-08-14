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

    def test_missing_ids_and_unrelated_chain_are_rejected(self):
        with self.assertRaises(ValueError):
            validator.validate_evidence_chain({"evidence": [{}], "claims": [], "reviews": [], "decisions": [], "artifacts": [], "promotions": []})
        unrelated = {"artifacts": [{"artifact_id": "a", "lifecycle_state": "ACCEPTED", "owner": "parent", "producer": "prometheus", "reviewer": "athena", "authority_status": "accepted", "evidence_ids": ["e1"], "claim_ids": ["c1"], "review_ids": ["r1"], "decision_id": "d1"}], "evidence": [{"id": "e1"}, {"id": "e2"}], "claims": [{"id": "c1", "evidence_ids": ["e2"]}], "reviews": [{"id": "r1", "reviewer": "athena", "outcome": "PASS", "claim_ids": ["c1"]}], "decisions": [{"id": "d1", "review_ids": ["r1"], "claim_ids": ["c1"], "outcome": "ACCEPT"}], "promotions": []}
        with self.assertRaises(ValueError):
            validator.validate_artifacts(unrelated)
            validator.validate_evidence_chain(unrelated)

    def test_accepted_artifact_requires_matching_pass_reviewer(self):
        doc = {"artifacts": [{"artifact_id": "a", "lifecycle_state": "ACCEPTED", "owner": "parent", "producer": "prometheus", "reviewer": "athena", "authority_status": "accepted", "previous_state": "REVIEWED", "evidence_ids": ["e"], "claim_ids": ["c"], "review_ids": ["r"], "decision_id": "d"}], "evidence": [{"id": "e"}], "claims": [{"id": "c", "evidence_ids": ["e"]}], "reviews": [{"id": "r", "reviewer": "prometheus", "outcome": "REQUEST_CHANGES", "claim_ids": ["c"]}], "decisions": [{"id": "d", "review_ids": ["r"], "claim_ids": ["c"], "outcome": "ACCEPT"}], "promotions": []}
        with self.assertRaises(ValueError):
            validator.validate_artifacts(doc)
            validator.validate_evidence_chain(doc)

    def test_non_draft_artifact_requires_predecessor(self):
        doc = {"artifacts": [{"artifact_id": "a", "lifecycle_state": "VALIDATED", "owner": "parent", "producer": "prometheus", "reviewer": None, "authority_status": "process_validated", "evidence_ids": [], "claim_ids": [], "review_ids": []}]}
        with self.assertRaises(ValueError):
            validator.validate_artifacts(doc)


if __name__ == "__main__":
    unittest.main()
