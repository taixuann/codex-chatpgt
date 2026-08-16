#!/usr/bin/env python3
"""Deterministic guardrails and bounded packet qualification for Feynman v1.

The policy fixtures check calibration, provenance/routing signals, and
adversarial shape. The qualification packets exercise a small bounded response
surface against evidence/context packets. Neither decides scientific truth or
proves native host dispatch.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import yaml


STATUSES = {
    "SUPPORTED",
    "PARTIALLY_SUPPORTED",
    "INSUFFICIENT_EVIDENCE",
    "CONFLICTING_EVIDENCE",
    "REQUIRES_ADDITIONAL_MEASUREMENT",
}
ROUTES = {"NONE", "ARGUS", "PROMETHEUS", "FRANKY", "ATHENA", "HUMAN"}


def evaluate_case(case: dict) -> dict[str, str]:
    evidence = case.get("evidence") or []
    claim = case.get("claim") or {}
    failure = case.get("failure")
    if failure:
        route = {
            "context_gap": "ARGUS",
            "provenance_gap": "ARGUS",
            "implementation_gap": "PROMETHEUS",
            "control_plane_gap": "FRANKY",
            "consequential_ambiguity": "ATHENA",
        }.get(failure, "HUMAN")
        return {"status": "INSUFFICIENT_EVIDENCE", "route": route}
    if case.get("stale_reference"):
        return {"status": "INSUFFICIENT_EVIDENCE", "route": "PROMETHEUS"}
    if case.get("aggregation_mismatch"):
        return {"status": "INSUFFICIENT_EVIDENCE", "route": "HUMAN"}
    if case.get("source_support") is False:
        return {"status": "INSUFFICIENT_EVIDENCE", "route": "HUMAN"}
    if case.get("fit_r2", 0) >= 0.98 and len(case.get("candidate_mechanisms") or []) > 1:
        return {"status": "REQUIRES_ADDITIONAL_MEASUREMENT", "route": "HUMAN"}
    if case.get("contradictory_new_evidence"):
        return {"status": "CONFLICTING_EVIDENCE", "route": "ATHENA"}
    if claim.get("type") == "mechanistic" and not any(item.get("category") == "sourced_claim" for item in evidence):
        return {"status": "INSUFFICIENT_EVIDENCE", "route": "HUMAN"}
    if not evidence:
        return {"status": "INSUFFICIENT_EVIDENCE", "route": "NONE"}
    if any(item.get("conflicts") for item in evidence):
        return {"status": "CONFLICTING_EVIDENCE", "route": "ATHENA"}
    if any(item.get("supports") for item in evidence):
        return {"status": "SUPPORTED", "route": "NONE"}
    return {"status": "PARTIALLY_SUPPORTED", "route": "NONE"}


def validate(path: Path) -> None:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if document.get("kind") != "feynman.policy-fixtures.v1":
        raise ValueError("fixture kind must be feynman.policy-fixtures.v1")
    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a non-empty list")
    seen: set[str] = set()
    for case in cases:
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise ValueError("case ids must be non-empty and unique")
        seen.add(case_id)
        expected = case.get("expected") or {}
        if expected.get("status") not in STATUSES or expected.get("route") not in ROUTES:
            raise ValueError(f"{case_id}: invalid expected status/route")
        actual = evaluate_case(case)
        if actual != expected:
            raise ValueError(f"{case_id}: expected {expected}, got {actual}")


def qualify_packet(packet: dict) -> dict[str, object]:
    """Produce bounded observable outputs from a scientific context packet."""
    context = packet.get("context") or {}
    evidence = packet.get("evidence") or []
    claim = packet.get("claim") or {}
    alternatives = packet.get("alternatives") or []
    review = packet.get("review") or {}
    implementation = packet.get("implementation") or {}

    if not context.get("project_manifest") or any(not item.get("provenance") for item in evidence):
        return {"status": "INSUFFICIENT_EVIDENCE", "alternatives_preserved": True, "abstained": True, "route": "ARGUS"}
    if implementation.get("ready") is False:
        return {"status": "INSUFFICIENT_EVIDENCE", "alternatives_preserved": True, "abstained": True, "route": "PROMETHEUS"}
    if review.get("required") and not review.get("independent"):
        return {"status": "INSUFFICIENT_EVIDENCE", "alternatives_preserved": True, "abstained": True, "route": "ATHENA"}
    if claim.get("type") == "mechanistic" and claim.get("fit_r2", 0) >= 0.98 and len(alternatives) > 1:
        return {"status": "REQUIRES_ADDITIONAL_MEASUREMENT", "alternatives_preserved": True, "abstained": True, "route": "HUMAN"}
    if any(item.get("conflicts") for item in evidence):
        return {"status": "CONFLICTING_EVIDENCE", "alternatives_preserved": True, "abstained": True, "route": "ATHENA"}
    supported = any(claim.get("id") in (item.get("supports") or []) for item in evidence)
    return {"status": "SUPPORTED" if supported else "INSUFFICIENT_EVIDENCE", "alternatives_preserved": bool(alternatives), "abstained": not supported, "route": "NONE" if supported else "HUMAN"}


def validate_qualification(path: Path) -> None:
    """Validate captured bounded outputs against their supplied packets."""
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if document.get("kind") != "feynman.behavior-qualification.v1":
        raise ValueError("qualification kind must be feynman.behavior-qualification.v1")
    if document.get("native_runtime") != "NOT_ASSESSED":
        raise ValueError("native runtime qualification must remain NOT_ASSESSED")
    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("qualification cases must be a non-empty list")
    seen: set[str] = set()
    for case in cases:
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise ValueError("qualification case ids must be non-empty and unique")
        seen.add(case_id)
        packet = case.get("packet") or {}
        captured = case.get("captured_output") or {}
        actual = qualify_packet(packet)
        if actual != captured:
            raise ValueError(f"{case_id}: captured output {captured} != bounded result {actual}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--qualification", type=Path)
    args = parser.parse_args()
    try:
        validate(args.fixture)
        if args.qualification:
            validate_qualification(args.qualification)
    except (OSError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL feynman-v1: {exc}")
        return 1
    print("OK feynman-v1: policy guardrails and bounded packet qualification")
    return 0


if __name__ == "__main__":
    sys.exit(main())
