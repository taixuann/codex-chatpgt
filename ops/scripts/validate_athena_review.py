#!/usr/bin/env python3
"""Deterministic validation for Athena's thin request/result contracts."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
from typing import Any
import yaml

CLASSES = {"implementation", "architecture_contract", "readiness", "scientific_evidence", "risk_security"}
STATUSES = {"fulfilled", "partial", "unfulfilled", "not_assessed"}
RECOMMENDATIONS = {"clear_for_parent_decision", "issues_found", "insufficient_evidence"}
REASONS = {"ambiguous_criterion", "conflicting_authority", "critical_evidence_missing", "multiple_valid_consequential_interpretations", "authority_or_policy_change", "scientific_claim_exceeds_evidence", "producer_reviewer_material_disagreement", "explicit_policy_gate"}
REQUIRED_OUTPUT = {"criterion_results", "findings", "coverage", "limitations", "recommendation"}

def mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict): raise ValueError(f"{name} must be a mapping")
    return value

def strings(value: Any, name: str, minimum: int = 0) -> list[str]:
    if not isinstance(value, list) or len(value) < minimum or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ValueError(f"{name} must be a list of non-empty strings")
    return value

def validate_request(doc: dict[str, Any]) -> None:
    if doc.get("kind") != "athena.review.v1": raise ValueError("request kind must be athena.review.v1")
    target = mapping(doc.get("target"), "target")
    for key in ("ref", "revision"):
        if not isinstance(target.get(key), str) or not target[key].strip(): raise ValueError(f"target.{key} is required")
    if doc.get("review_class") not in CLASSES: raise ValueError("review_class is not supported")
    criteria = mapping(doc.get("criteria"), "criteria")
    strings(criteria.get("source"), "criteria.source", 1)
    if criteria.get("locked") is not True: raise ValueError("criteria.locked must be true")
    scope = mapping(doc.get("scope"), "scope"); strings(scope.get("include"), "scope.include"); strings(scope.get("exclude"), "scope.exclude")
    if not isinstance(doc.get("evidence"), list): raise ValueError("evidence must be a list")
    context = mapping(doc.get("context"), "context"); strings(context.get("optional_refs"), "context.optional_refs")
    authority = mapping(doc.get("authority"), "authority")
    if authority.get("mutation") != "denied" or authority.get("final_acceptance") != "denied": raise ValueError("Athena authority must deny mutation and final acceptance")
    output = mapping(doc.get("output"), "output")
    if not REQUIRED_OUTPUT.issubset(set(strings(output.get("require"), "output.require", 5))): raise ValueError("output.require is incomplete")

def validate_result(doc: dict[str, Any], expected_revision: str | None = None) -> None:
    if doc.get("kind") != "athena.review-result.v1": raise ValueError("result kind must be athena.review-result.v1")
    revision = doc.get("target_revision")
    if not isinstance(revision, str) or not revision.strip(): raise ValueError("target_revision is required")
    if expected_revision and revision != expected_revision: raise ValueError("result target revision is stale")
    coverage = mapping(doc.get("coverage"), "coverage"); strings(coverage.get("reviewed"), "coverage.reviewed"); strings(coverage.get("not_reviewed"), "coverage.not_reviewed")
    if not isinstance(coverage.get("complete"), bool): raise ValueError("coverage.complete must be boolean")
    criteria = doc.get("criteria")
    if not isinstance(criteria, list) or not criteria: raise ValueError("criteria must be a non-empty list")
    for item in criteria:
        c = mapping(item, "criterion")
        for key in ("id", "rationale"):
            if not isinstance(c.get(key), str) or not c[key].strip(): raise ValueError(f"criterion.{key} is required")
        if c.get("status") not in STATUSES: raise ValueError("invalid criterion status")
        if not isinstance(c.get("evidence"), list): raise ValueError("criterion.evidence must be a list")
    findings = doc.get("findings")
    if not isinstance(findings, list): raise ValueError("findings must be a list")
    for item in findings:
        f = mapping(item, "finding")
        for key in ("criterion", "location", "rationale", "suggested_action"):
            if not isinstance(f.get(key), str): raise ValueError(f"finding.{key} is required")
        if f.get("severity") not in {"critical", "high", "medium", "low"}: raise ValueError("invalid finding severity")
        if not isinstance(f.get("evidence"), list): raise ValueError("finding.evidence must be a list")
    rec = mapping(doc.get("recommendation"), "recommendation")
    if rec.get("status") not in RECOMMENDATIONS: raise ValueError("invalid recommendation")
    if any(c.get("status") == "not_assessed" for c in criteria) and rec.get("status") == "clear_for_parent_decision": raise ValueError("not_assessed criterion cannot yield clear recommendation")
    if not isinstance(doc.get("limitations"), list): raise ValueError("limitations must be a list")
    human = mapping(doc.get("human_review"), "human_review")
    if not isinstance(human.get("required"), bool): raise ValueError("human_review.required must be boolean")
    if human.get("required") and (human.get("reason_code") not in REASONS or not isinstance(human.get("question"), str) or not human["question"].strip()): raise ValueError("required human review needs reason_code and question")
    forbidden = {"system_accepted", "final_acceptance", "accepted"}
    if forbidden & set(doc): raise ValueError("result cannot encode final acceptance")

def validate_cases(path: Path) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    expected = {"implementation_complete", "architecture_contract", "readiness_stale_revision", "scientific_unsupported_claim", "risk_security", "missing_rubric", "missing_critical_evidence", "excluded_runtime_surface", "producer_persuasion", "trivial_change_not_required", "consequential_architecture_required", "conflicting_authority", "implementation_routes_prometheus", "missing_context_routes_argus", "control_plane_routes_franky", "result_cannot_accept", "mutation_denied", "material_mutation_requires_rereview", "fresh_context_no_history", "interactive_distinct_from_formal"}
    actual = set(strings(data.get("cases"), "cases"))
    if actual != expected: raise ValueError(f"case fixture mismatch: missing={sorted(expected-actual)} extra={sorted(actual-expected)}")

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--request", type=Path); parser.add_argument("--result", type=Path); parser.add_argument("--expected-revision"); parser.add_argument("--cases", type=Path)
    args = parser.parse_args()
    try:
        if args.request: validate_request(yaml.safe_load(args.request.read_text(encoding="utf-8")) or {})
        if args.result: validate_result(yaml.safe_load(args.result.read_text(encoding="utf-8")) or {}, args.expected_revision)
        if args.cases: validate_cases(args.cases)
        if not any((args.request, args.result, args.cases)): raise ValueError("provide --request, --result, or --cases")
    except (OSError, yaml.YAMLError, ValueError) as exc:
        print(f"FAIL athena review: {exc}"); return 1
    print("OK athena review contracts and representative cases"); return 0
if __name__ == "__main__": sys.exit(main())
