import unittest

from ops.scripts.evaluate_merge_readiness import evaluate_merge_readiness


def decision(**overrides):
    value = {
        "id": "decision-2",
        "outcome": "APPROVED",
        "head_commit": "abc123",
        "reviewer": "human",
        "decision_reason": "current evidence is sufficient",
        "decision_at": "2026-08-24T00:00:00Z",
        "revision": "2",
        "artifact_id": "artifact-1",
        "action": "merge",
        "scope_digest": "scope-sha256",
        "evidence_digest": "evidence-sha256",
        "upstream_ids": ["contract-v1"],
    }
    value.update(overrides)
    return value


def record(**overrides):
    current = {
        "artifact_id": "artifact-1",
        "action": "merge",
        "scope_digest": "scope-sha256",
        "evidence_digest": "evidence-sha256",
        "upstream_ids": ["contract-v1"],
    }
    latest = decision()
    value = {
        "head_commit": "abc123",
        "ci_status": "PASS",
        "executor_status": "DONE",
        "current": current,
        "review": {
            "outcome": "APPROVED",
            "head_commit": "abc123",
            "reviewer": "athena",
            "unresolved_material_findings": [],
        },
        "decision": latest,
        "decision_history": [
            decision(id="decision-1", outcome="CHANGES_REQUESTED", revision="1", decision_reason="revision required", decision_at="2026-08-23T00:00:00Z"),
            latest,
        ],
        "authorization": {
            "status": "AUTHORIZED",
            "authorized_by": "human",
            "rationale": "human approval",
            "authorized_at": "2026-08-24T00:01:00Z",
            "decision_id": "decision-2",
            "head_commit": "abc123",
            **current,
        },
    }
    value.update(overrides)
    return value


class MergeReadinessTests(unittest.TestCase):
    def test_current_approved_evidence_is_ready(self):
        self.assertEqual(evaluate_merge_readiness(record())["status"], "READY")

    def test_unresolved_material_review_blocks_merge(self):
        result = evaluate_merge_readiness(
            record(review={
                "outcome": "APPROVED",
                "head_commit": "abc123",
                "reviewer": "athena",
                "unresolved_material_findings": ["P1"],
            })
        )
        self.assertEqual(result["status"], "NOT_MERGE_READY")

    def test_authorized_waiver_is_explicit(self):
        base = record()
        result = evaluate_merge_readiness(
            record(
                review={
                    "outcome": "APPROVED",
                    "head_commit": "abc123",
                    "reviewer": "athena",
                    "unresolved_material_findings": ["P1"],
                },
                authorization={**base["authorization"], "status": "WAIVED", "rationale": "human accepted limitation"},
            )
        )
        self.assertEqual(result["status"], "READY")

    def test_stale_review_blocks_merge(self):
        result = evaluate_merge_readiness(
            record(review={
                "outcome": "APPROVED",
                "head_commit": "old456",
                "reviewer": "athena",
                "unresolved_material_findings": [],
            })
        )
        self.assertEqual(result["status"], "NOT_MERGE_READY")
        self.assertTrue(any("stale" in reason for reason in result["reasons"]))

    def test_review_decision_authorization_are_distinct(self):
        result = evaluate_merge_readiness(record(authorization={}))
        self.assertEqual(result["status"], "NOT_MERGE_READY")
        self.assertTrue(any("authorization" in reason for reason in result["reasons"]))
        self.assertNotEqual(record()["review"], record()["decision"])

    def test_negative_review_outcomes_block_merge(self):
        for outcome in ("REJECTED", "CHANGES_REQUESTED"):
            base = record()
            latest = decision(outcome=outcome)
            result = evaluate_merge_readiness(
                record(
                    review={"outcome": outcome, "head_commit": "abc123", "reviewer": "athena", "unresolved_material_findings": []},
                    decision=latest,
                    decision_history=[base["decision_history"][0], latest],
                )
            )
            self.assertEqual(result["status"], "NOT_MERGE_READY")

    def test_authorization_stale_head_blocks_merge(self):
        base = record()
        result = evaluate_merge_readiness(
            record(authorization={**base["authorization"], "head_commit": "old456"})
        )
        self.assertEqual(result["status"], "NOT_MERGE_READY")
        self.assertTrue(any("authorization evidence is stale" in reason for reason in result["reasons"]))

    def test_post_approval_scope_or_upstream_mutation_blocks_merge(self):
        for field, changed in (("scope_digest", "new-scope"), ("upstream_ids", ["new-contract"])):
            base = record()
            current = {**base["current"], field: changed}
            result = evaluate_merge_readiness(record(current=current))
            self.assertEqual(result["status"], "NOT_MERGE_READY")
            self.assertTrue(any("decision binding is stale" in reason for reason in result["reasons"]))

    def test_decision_requires_human_metadata_and_append_only_history(self):
        base = record()
        incomplete = {**base["decision"], "reviewer": ""}
        result = evaluate_merge_readiness(record(decision=incomplete))
        self.assertEqual(result["status"], "NOT_MERGE_READY")
        self.assertTrue(any("decision requires non-empty reviewer" in reason for reason in result["reasons"]))

        result = evaluate_merge_readiness(record(decision_history=[base["decision_history"][0]]))
        self.assertEqual(result["status"], "NOT_MERGE_READY")
        self.assertTrue(any("last append-only" in reason for reason in result["reasons"]))

    def test_history_final_entry_cannot_reuse_current_id_with_stale_content(self):
        base = record()
        stale_final = {
            **base["decision"],
            "outcome": "REJECTED",
            "head_commit": "old456",
            "decision_reason": "old decision",
            "decision_at": "2026-08-23T00:00:00Z",
            "revision": "1",
        }
        result = evaluate_merge_readiness(record(decision_history=[stale_final]))
        self.assertEqual(result["status"], "NOT_MERGE_READY")
        self.assertTrue(any("exactly match" in reason for reason in result["reasons"]))
        self.assertTrue(any("decision_history final entry evidence is stale" in reason for reason in result["reasons"]))

    def test_malformed_evidence_mapping_is_rejected_without_crashing(self):
        result = evaluate_merge_readiness(record(review=[]))
        self.assertEqual(result["status"], "NOT_MERGE_READY")
        self.assertTrue(any("review must be an object" in reason for reason in result["reasons"]))

        result = evaluate_merge_readiness([])
        self.assertEqual(result["status"], "NOT_MERGE_READY")
        self.assertTrue(any("record must be an object" in reason for reason in result["reasons"]))


if __name__ == "__main__":
    unittest.main()
