#!/usr/bin/env python3
"""Evaluate merge-readiness evidence without performing a merge.

This is a deterministic evidence gate, not a workflow engine.  It keeps CI,
review, decision, authorization, and merge as distinct records and rejects
stale or materially unresolved review evidence.
"""

from __future__ import annotations

from typing import Any

import argparse
from pathlib import Path
import sys
import yaml


REVIEW_OUTCOMES = {"APPROVED", "REJECTED", "CHANGES_REQUESTED"}
DECISION_OUTCOMES = {"APPROVED", "REJECTED", "CHANGES_REQUESTED"}


def evaluate_merge_readiness(record: dict[str, Any]) -> dict[str, Any]:
    """Return ``READY`` or ``NOT_MERGE_READY`` with deterministic reasons.

    Required record keys deliberately describe observed evidence, so callers
    must supply current-head and authorization facts rather than infer them
    from a green CI result or an implementation-side status.
    """
    reasons: list[str] = []
    review = record.get("review") or {}
    decision = record.get("decision") or {}
    authorization = record.get("authorization") or {}

    if record.get("ci_status") != "PASS":
        reasons.append("CI is not PASS")
    outcome = review.get("outcome")
    if outcome not in REVIEW_OUTCOMES:
        reasons.append("review outcome must be APPROVED, REJECTED, or CHANGES_REQUESTED")
    if review.get("head_commit") != record.get("head_commit"):
        reasons.append("review evidence is stale for the current head")
    if review.get("unresolved_material_findings"):
        waived = (
            authorization.get("status") == "WAIVED"
            and bool(authorization.get("authorized_by"))
            and bool(authorization.get("rationale"))
        )
        if not waived:
            reasons.append("material review findings remain unresolved without an authorized waiver")
    elif authorization.get("status") != "AUTHORIZED" or not authorization.get("authorized_by"):
        reasons.append("merge requires explicit authorization evidence")
    if decision.get("outcome") not in DECISION_OUTCOMES:
        reasons.append("decision outcome must be explicit")
    if decision.get("outcome") != outcome:
        reasons.append("decision and review outcomes disagree")
    if decision.get("head_commit") != record.get("head_commit"):
        reasons.append("decision evidence is stale for the current head")
    if outcome != "APPROVED" or decision.get("outcome") != "APPROVED":
        reasons.append("merge requires an explicit APPROVED review and decision")
    if record.get("executor_status") == "DONE":
        # DONE is useful execution evidence but never substitutes for review
        # and authorization; the checks above remain mandatory.
        pass
    return {
        "status": "READY" if not reasons else "NOT_MERGE_READY",
        "reasons": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        record = yaml.safe_load(args.record.read_text(encoding="utf-8"))
        result = evaluate_merge_readiness(record)
    except (OSError, yaml.YAMLError, TypeError, ValueError) as exc:
        print(f"FAIL {args.record}: {exc}")
        return 1
    print(f"{result['status']} {args.record}")
    for reason in result["reasons"]:
        print(f"- {reason}")
    return 0 if result["status"] == "READY" else 2


if __name__ == "__main__":
    sys.exit(main())
