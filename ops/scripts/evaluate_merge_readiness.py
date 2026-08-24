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
AUTHORIZATION_STATUSES = {"AUTHORIZED", "WAIVED"}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _identifier_list(value: Any) -> bool:
    """Return whether an optional dependency list is well-formed.

    An action can have no relevant upstream decision, so an empty list is
    valid.  When dependencies are declared, however, duplicate or anonymous
    identifiers would make stale-approval detection ambiguous.
    """
    return (
        isinstance(value, list)
        and all(_nonempty(item) for item in value)
        and len(set(value)) == len(value)
    )


def _human_decision_reasons(decision: dict[str, Any]) -> list[str]:
    required = ("id", "reviewer", "decision_reason", "decision_at", "revision")
    return [f"decision requires non-empty {field}" for field in required if not _nonempty(decision.get(field))]


def _binding_reasons(
    name: str,
    item: dict[str, Any],
    current: dict[str, Any],
    head_commit: Any,
    decision_id: Any | None = None,
) -> list[str]:
    """Validate an authorization/decision against the current evidence snapshot."""
    reasons: list[str] = []
    for field in ("artifact_id", "action", "scope_digest", "evidence_digest"):
        if not _nonempty(item.get(field)):
            reasons.append(f"{name} requires non-empty {field}")
        elif item.get(field) != current.get(field):
            reasons.append(f"{name} binding is stale for current {field}")
    if item.get("head_commit") != head_commit:
        reasons.append(f"{name} evidence is stale for the current head")
    if not _identifier_list(item.get("upstream_ids")):
        reasons.append(f"{name} upstream_ids must be a duplicate-free list of non-empty identifiers")
    elif item.get("upstream_ids") != current.get("upstream_ids"):
        reasons.append(f"{name} binding is stale for current upstream_ids")
    if decision_id is not None and item.get("decision_id") != decision_id:
        reasons.append(f"{name} is not bound to the current decision")
    return reasons


def evaluate_merge_readiness(record: dict[str, Any]) -> dict[str, Any]:
    """Return ``READY`` or ``NOT_MERGE_READY`` with deterministic reasons.

    Required record keys deliberately describe observed evidence, so callers
    must supply current-head and authorization facts rather than infer them
    from a green CI result or an implementation-side status.
    """
    if not isinstance(record, dict):
        return {"status": "NOT_MERGE_READY", "reasons": ["merge-readiness record must be an object"]}

    reasons: list[str] = []
    review = record.get("review") if isinstance(record.get("review"), dict) else {}
    decision = record.get("decision") if isinstance(record.get("decision"), dict) else {}
    authorization = record.get("authorization") if isinstance(record.get("authorization"), dict) else {}
    current = record.get("current") if isinstance(record.get("current"), dict) else {}
    history = record.get("decision_history")

    for name in ("review", "decision", "authorization", "current"):
        if not isinstance(record.get(name), dict):
            reasons.append(f"{name} must be an object")

    if record.get("ci_status") != "PASS":
        reasons.append("CI is not PASS")
    outcome = review.get("outcome")
    if outcome not in REVIEW_OUTCOMES:
        reasons.append("review outcome must be APPROVED, REJECTED, or CHANGES_REQUESTED")
    if review.get("head_commit") != record.get("head_commit"):
        reasons.append("review evidence is stale for the current head")
    if not _nonempty(review.get("reviewer")):
        reasons.append("review requires a non-empty reviewer")
    if not isinstance(review.get("unresolved_material_findings"), list):
        reasons.append("review unresolved_material_findings must be a list")
    if review.get("unresolved_material_findings"):
        waived = authorization.get("status") == "WAIVED"
        if not waived:
            reasons.append("material review findings remain unresolved without an authorized waiver")
    elif authorization.get("status") != "AUTHORIZED":
        reasons.append("merge requires explicit authorization evidence")
    if decision.get("outcome") not in DECISION_OUTCOMES:
        reasons.append("decision outcome must be explicit")
    if decision.get("outcome") != outcome:
        reasons.append("decision and review outcomes disagree")
    if decision.get("head_commit") != record.get("head_commit"):
        reasons.append("decision evidence is stale for the current head")
    reasons.extend(_human_decision_reasons(decision))
    for field in ("artifact_id", "action", "scope_digest", "evidence_digest"):
        if not _nonempty(current.get(field)):
            reasons.append(f"current snapshot requires non-empty {field}")
    if not _identifier_list(current.get("upstream_ids")):
        reasons.append("current snapshot upstream_ids must be a duplicate-free list of non-empty identifiers")
    reasons.extend(_binding_reasons("review", review, current, record.get("head_commit")))
    reasons.extend(_binding_reasons("decision", decision, current, record.get("head_commit")))

    if authorization.get("status") not in AUTHORIZATION_STATUSES:
        reasons.append("authorization status must be AUTHORIZED or WAIVED")
    for field in ("authorized_by", "rationale", "authorized_at"):
        if not _nonempty(authorization.get(field)):
            reasons.append(f"authorization requires non-empty {field}")
    reasons.extend(
        _binding_reasons(
            "authorization", authorization, current, record.get("head_commit"), decision.get("id")
        )
    )

    if not isinstance(history, list) or not history:
        reasons.append("decision_history requires an append-only ordered decision record")
    else:
        history_ids = []
        for index, item in enumerate(history):
            if not isinstance(item, dict):
                reasons.append(f"decision_history[{index}] must be an object")
                continue
            history_ids.append(item.get("id"))
            reasons.extend(
                f"decision_history[{index}]: {reason}" for reason in _human_decision_reasons(item)
            )
        if any(not _nonempty(item) for item in history_ids) or len(history_ids) != len(set(history_ids)):
            reasons.append("decision_history decision ids must be non-empty and unique")
        elif isinstance(history[-1], dict):
            final_fields = (
                "id", "outcome", "head_commit", "reviewer", "decision_reason", "decision_at", "revision",
                "artifact_id", "action", "scope_digest", "evidence_digest", "upstream_ids",
            )
            if any(history[-1].get(field) != decision.get(field) for field in final_fields):
                reasons.append("current decision must exactly match the last append-only decision_history entry")
            reasons.extend(_binding_reasons("decision_history final entry", history[-1], current, record.get("head_commit")))
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
