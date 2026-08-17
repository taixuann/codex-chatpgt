import unittest

from ops.scripts.evaluate_merge_readiness import evaluate_merge_readiness


def record(**overrides):
    value = {
        "head_commit": "abc123",
        "ci_status": "PASS",
        "executor_status": "DONE",
        "review": {
            "outcome": "APPROVED",
            "head_commit": "abc123",
            "unresolved_material_findings": [],
        },
        "decision": {"outcome": "APPROVED", "head_commit": "abc123"},
        "authorization": {"status": "AUTHORIZED", "authorized_by": "human", "rationale": "human approval"},
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
                "unresolved_material_findings": ["P1"],
            })
        )
        self.assertEqual(result["status"], "NOT_MERGE_READY")

    def test_authorized_waiver_is_explicit(self):
        result = evaluate_merge_readiness(
            record(
                review={
                    "outcome": "APPROVED",
                    "head_commit": "abc123",
                    "unresolved_material_findings": ["P1"],
                },
                authorization={"status": "WAIVED", "authorized_by": "human", "rationale": "human accepted limitation"},
            )
        )
        self.assertEqual(result["status"], "READY")

    def test_stale_review_blocks_merge(self):
        result = evaluate_merge_readiness(
            record(review={
                "outcome": "APPROVED",
                "head_commit": "old456",
                "unresolved_material_findings": [],
            })
        )
        self.assertEqual(result["status"], "NOT_MERGE_READY")
        self.assertTrue(any("stale" in reason for reason in result["reasons"]))

    def test_review_decision_authorization_are_distinct(self):
        result = evaluate_merge_readiness(
            record(decision={"outcome": "APPROVED", "head_commit": "abc123"}, authorization={})
        )
        self.assertEqual(result["status"], "NOT_MERGE_READY")
        self.assertTrue(any("authorization" in reason for reason in result["reasons"]))
        self.assertNotEqual(record()["review"], record()["decision"])

    def test_negative_review_outcomes_block_merge(self):
        for outcome in ("REJECTED", "CHANGES_REQUESTED"):
            result = evaluate_merge_readiness(
                record(
                    review={"outcome": outcome, "head_commit": "abc123", "unresolved_material_findings": []},
                    decision={"outcome": outcome, "head_commit": "abc123"},
                )
            )
            self.assertEqual(result["status"], "NOT_MERGE_READY")


if __name__ == "__main__":
    unittest.main()
