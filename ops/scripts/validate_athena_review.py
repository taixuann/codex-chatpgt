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
REQUEST_KEYS = {"kind", "target", "review_class", "criteria", "scope", "evidence", "context", "authority", "output"}
TARGET_KEYS = {"ref", "revision"}
CRITERIA_KEYS = {"source", "locked"}
SCOPE_KEYS = {"include", "exclude"}
CONTEXT_KEYS = {"optional_refs"}
AUTHORITY_KEYS = {"mutation", "final_acceptance"}
OUTPUT_KEYS = {"require"}
RESULT_KEYS = {"kind", "target_revision", "coverage", "criteria", "findings", "recommendation", "limitations", "human_review"}
COVERAGE_KEYS = {"reviewed", "not_reviewed", "complete"}
CRITERION_KEYS = {"id", "status", "evidence", "rationale"}
FINDING_KEYS = {"severity", "criterion", "location", "evidence", "rationale", "suggested_action"}
RECOMMENDATION_KEYS = {"status"}
HUMAN_KEYS = {"required", "reason_code", "question"}

def mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict): raise ValueError(f"{name} must be a mapping")
    return value

def strings(value: Any, name: str, minimum: int = 0) -> list[str]:
    if not isinstance(value, list) or len(value) < minimum or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ValueError(f"{name} must be a list of non-empty strings")
    return value

def exact_keys(value: dict[str, Any], allowed: set[str], name: str) -> None:
    unknown = set(value) - allowed
    if unknown:
        raise ValueError(f"{name} has undeclared field(s): {', '.join(sorted(unknown))}")

def validate_request(doc: dict[str, Any], expected_revision: str | None = None) -> None:
    doc = mapping(doc, "request")
    exact_keys(doc, REQUEST_KEYS, "request")
    if doc.get("kind") != "athena.review.v1": raise ValueError("request kind must be athena.review.v1")
    target = mapping(doc.get("target"), "target")
    exact_keys(target, TARGET_KEYS, "target")
    for key in ("ref", "revision"):
        if not isinstance(target.get(key), str) or not target[key].strip(): raise ValueError(f"target.{key} is required")
    if expected_revision and target["revision"] != expected_revision: raise ValueError("request target revision is stale")
    if doc.get("review_class") not in CLASSES: raise ValueError("review_class is not supported")
    criteria = mapping(doc.get("criteria"), "criteria")
    exact_keys(criteria, CRITERIA_KEYS, "criteria")
    strings(criteria.get("source"), "criteria.source", 1)
    if criteria.get("locked") is not True: raise ValueError("criteria.locked must be true")
    scope = mapping(doc.get("scope"), "scope"); strings(scope.get("include"), "scope.include"); strings(scope.get("exclude"), "scope.exclude")
    exact_keys(scope, SCOPE_KEYS, "scope")
    if not isinstance(doc.get("evidence"), list): raise ValueError("evidence must be a list")
    context = mapping(doc.get("context"), "context"); exact_keys(context, CONTEXT_KEYS, "context"); strings(context.get("optional_refs"), "context.optional_refs")
    authority = mapping(doc.get("authority"), "authority")
    exact_keys(authority, AUTHORITY_KEYS, "authority")
    if authority.get("mutation") != "denied" or authority.get("final_acceptance") != "denied": raise ValueError("Athena authority must deny mutation and final acceptance")
    output = mapping(doc.get("output"), "output")
    exact_keys(output, OUTPUT_KEYS, "output")
    if not REQUIRED_OUTPUT.issubset(set(strings(output.get("require"), "output.require", 5))): raise ValueError("output.require is incomplete")

def validate_result(doc: dict[str, Any], expected_revision: str | None = None) -> None:
    doc = mapping(doc, "result")
    exact_keys(doc, RESULT_KEYS, "result")
    if doc.get("kind") != "athena.review-result.v1": raise ValueError("result kind must be athena.review-result.v1")
    revision = doc.get("target_revision")
    if not isinstance(revision, str) or not revision.strip(): raise ValueError("target_revision is required")
    if expected_revision and revision != expected_revision: raise ValueError("result target revision is stale")
    coverage = mapping(doc.get("coverage"), "coverage"); exact_keys(coverage, COVERAGE_KEYS, "coverage"); strings(coverage.get("reviewed"), "coverage.reviewed"); strings(coverage.get("not_reviewed"), "coverage.not_reviewed")
    if not isinstance(coverage.get("complete"), bool): raise ValueError("coverage.complete must be boolean")
    criteria = doc.get("criteria")
    if not isinstance(criteria, list) or not criteria: raise ValueError("criteria must be a non-empty list")
    for item in criteria:
        c = mapping(item, "criterion")
        exact_keys(c, CRITERION_KEYS, "criterion")
        for key in ("id", "rationale"):
            if not isinstance(c.get(key), str) or not c[key].strip(): raise ValueError(f"criterion.{key} is required")
        if c.get("status") not in STATUSES: raise ValueError("invalid criterion status")
        if not isinstance(c.get("evidence"), list): raise ValueError("criterion.evidence must be a list")
    findings = doc.get("findings")
    if not isinstance(findings, list): raise ValueError("findings must be a list")
    for item in findings:
        f = mapping(item, "finding")
        exact_keys(f, FINDING_KEYS, "finding")
        for key in ("criterion", "location", "rationale", "suggested_action"):
            if not isinstance(f.get(key), str): raise ValueError(f"finding.{key} is required")
        if f.get("severity") not in {"critical", "high", "medium", "low"}: raise ValueError("invalid finding severity")
        if not isinstance(f.get("evidence"), list): raise ValueError("finding.evidence must be a list")
    rec = mapping(doc.get("recommendation"), "recommendation")
    exact_keys(rec, RECOMMENDATION_KEYS, "recommendation")
    if rec.get("status") not in RECOMMENDATIONS: raise ValueError("invalid recommendation")
    if any(c.get("status") != "fulfilled" for c in criteria) and rec.get("status") == "clear_for_parent_decision": raise ValueError("non-fulfilled criterion cannot yield clear recommendation")
    if not isinstance(doc.get("limitations"), list): raise ValueError("limitations must be a list")
    human = mapping(doc.get("human_review"), "human_review")
    exact_keys(human, HUMAN_KEYS, "human_review")
    if not isinstance(human.get("required"), bool): raise ValueError("human_review.required must be boolean")
    if human.get("required") and (human.get("reason_code") not in REASONS or not isinstance(human.get("question"), str) or not human["question"].strip()): raise ValueError("required human review needs reason_code and question")

def validate_request_result_pair(request: dict[str, Any], result: dict[str, Any], expected_revision: str | None = None) -> None:
    if expected_revision is None:
        request_target = mapping(request, "request").get("target")
        result_revision = mapping(result, "result").get("target_revision")
        request_revision = mapping(request_target, "target").get("revision")
        if request_revision != result_revision:
            raise ValueError("request and result target revisions must match")
        expected_revision = request_revision
    validate_request(request, expected_revision)
    validate_result(result, expected_revision)

def validate_cases(path: Path) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    expected = {"implementation_complete", "architecture_contract", "readiness_stale_revision", "scientific_unsupported_claim", "risk_security", "missing_rubric", "missing_critical_evidence", "excluded_runtime_surface", "producer_persuasion", "trivial_change_not_required", "consequential_architecture_required", "conflicting_authority", "implementation_routes_prometheus", "missing_context_routes_argus", "control_plane_routes_franky", "result_cannot_accept", "mutation_denied", "material_mutation_requires_rereview", "fresh_context_no_history", "interactive_distinct_from_formal"}
    cases = data.get("cases")
    if not isinstance(cases, list): raise ValueError("cases must be a list of behavior mappings")
    actual = set()
    for case in cases:
        item = mapping(case, "case")
        exact_keys(item, {"id", "request", "result", "expect"}, "case")
        if not isinstance(item.get("id"), str) or not item["id"].strip(): raise ValueError("case.id is required")
        actual.add(item["id"])
        mapping(item.get("request"), f"case {item['id']}.request")
        mapping(item.get("result"), f"case {item['id']}.result")
        mapping(item.get("expect"), f"case {item['id']}.expect")
    if actual != expected: raise ValueError(f"case fixture mismatch: missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    by_id = {item["id"]: item for item in cases}
    for case_id, case in by_id.items():
        req, result, expect = case["request"], case["result"], case["expect"]
        if req.get("review_class") not in CLASSES: raise ValueError(f"case {case_id}: invalid review class")
        if req.get("criteria_locked") is not True and case_id != "missing_rubric": raise ValueError(f"case {case_id}: criteria must be locked")
        if not isinstance(req.get("target_revision"), str) or not req["target_revision"]: raise ValueError(f"case {case_id}: target revision required")
        if result.get("recommendation") not in RECOMMENDATIONS: raise ValueError(f"case {case_id}: invalid recommendation")
        if not isinstance(result.get("criterion_statuses"), list) or not result["criterion_statuses"] or not set(result["criterion_statuses"]).issubset(STATUSES): raise ValueError(f"case {case_id}: invalid criterion statuses")
        if not isinstance(result.get("coverage_complete"), bool): raise ValueError(f"case {case_id}: coverage_complete must be boolean")
        if any(status == "not_assessed" for status in result["criterion_statuses"]) and result["recommendation"] == "clear_for_parent_decision": raise ValueError(f"case {case_id}: missing evidence cannot clear")
        if case_id == "implementation_complete" and (result.get("recommendation") != "clear_for_parent_decision" or result.get("coverage_complete") is not True or result.get("criterion_statuses") != ["fulfilled"] or result.get("review_required") is not True): raise ValueError("implementation case outcome is incomplete")
        if case_id == "architecture_contract" and (result.get("recommendation") != "issues_found" or result.get("coverage_complete") is not True or result.get("criterion_statuses") != ["partial"] or result.get("review_required") is not True): raise ValueError("architecture case outcome is incomplete")
        if case_id == "readiness_stale_revision" and not expect.get("stale_revision"): raise ValueError("stale revision case must assert stale_revision")
        if case_id == "readiness_stale_revision" and (result.get("recommendation") != "insufficient_evidence" or result.get("coverage_complete") is not False or "not_assessed" not in result["criterion_statuses"]): raise ValueError("stale revision must remain insufficient and not assessed")
        if case_id == "producer_persuasion" and expect.get("artifact_text_is_data") is not True: raise ValueError("persuasion case must assert artifact text is data")
        if case_id == "scientific_unsupported_claim" and expect.get("human_reason") != "scientific_claim_exceeds_evidence": raise ValueError("unsupported scientific claim must escalate with exact reason")
        if case_id == "risk_security" and (result.get("recommendation") != "issues_found" or "unfulfilled" not in result["criterion_statuses"]): raise ValueError("security risk must remain an issues-found unfulfilled outcome")
        if case_id == "missing_rubric" and expect.get("admission") != "insufficient_contract": raise ValueError("missing rubric must fail admission as insufficient contract")
        if case_id == "missing_critical_evidence" and expect.get("admission") != "insufficient_evidence": raise ValueError("missing critical evidence must fail admission as insufficient evidence")
        if case_id in {"implementation_routes_prometheus", "missing_context_routes_argus", "control_plane_routes_franky"} and (result.get("spawned") is not False or expect.get("parent_routes_only") is not True or result.get("handoff") != expect.get("route")): raise ValueError(f"case {case_id}: exact parent-only route assertion missing")
        if case_id == "conflicting_authority" and (result.get("human_required") is not True or result.get("human_reason") != "conflicting_authority" or not isinstance(result.get("human_question"), str) or not result["human_question"].strip() or expect.get("human_required") is not True or expect.get("human_reason") != "conflicting_authority" or expect.get("human_question_bounded") is not True): raise ValueError("conflicting authority must require a bounded human question")
        if case_id == "trivial_change_not_required" and (req.get("consequence") != "trivial" or result.get("review_required") is not False or expect.get("review_required") is not False): raise ValueError("trivial change must explicitly skip Athena")
        if case_id == "consequential_architecture_required" and (req.get("consequence") != "consequential" or expect.get("review_required") is not True): raise ValueError("consequential architecture must require Athena")
        if case_id == "excluded_runtime_surface" and (not result.get("not_reviewed") or not result.get("limitations") or not any("NOT_ASSESSED" in str(item) for item in result["limitations"]) or expect.get("limitation_visible") is not True): raise ValueError("excluded runtime surface must remain visible")
        if case_id == "material_mutation_requires_rereview" and (req.get("target_mutated") is not True or result.get("fresh_review_required") is not True or expect.get("fresh_review_required") is not True or expect.get("stale_result_not_accepted") is not True): raise ValueError("mutation case must require fresh review and reject stale result")
        if case_id == "result_cannot_accept" and (result.get("final_acceptance") is not False or expect.get("final_acceptance_field_absent") is not True or expect.get("recommendation_not_acceptance") is not True): raise ValueError("result must not encode final acceptance")
        if case_id == "mutation_denied" and (req.get("authority_mutation") != "denied" or result.get("mutation_denied") is not True or expect.get("mutation") != "denied" or expect.get("mutation_denied") is not True): raise ValueError("mutation-denial outcome must be explicit")
        if case_id == "fresh_context_no_history" and (req.get("producer_history_included") is not False or expect.get("fresh_context") is not True): raise ValueError("fresh-context case assertion missing")
        if case_id == "interactive_distinct_from_formal" and (req.get("mode") != "interactive_critique" or expect.get("formal_mode_distinct") is not True): raise ValueError("interactive/formal distinction missing")

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--request", type=Path); parser.add_argument("--result", type=Path); parser.add_argument("--expected-revision"); parser.add_argument("--cases", type=Path)
    args = parser.parse_args()
    try:
        request = yaml.safe_load(args.request.read_text(encoding="utf-8")) or {} if args.request else None
        result = yaml.safe_load(args.result.read_text(encoding="utf-8")) or {} if args.result else None
        expected_revision = args.expected_revision
        if request is not None and result is not None:
            validate_request_result_pair(request, result, expected_revision)
        elif request is not None:
            validate_request(request, expected_revision)
        elif result is not None:
            validate_result(result, expected_revision)
        if args.cases: validate_cases(args.cases)
        if not any((args.request, args.result, args.cases)): raise ValueError("provide --request, --result, or --cases")
    except (OSError, yaml.YAMLError, ValueError) as exc:
        print(f"FAIL athena review: {exc}"); return 1
    print("OK athena review contracts and representative cases"); return 0
if __name__ == "__main__": sys.exit(main())
