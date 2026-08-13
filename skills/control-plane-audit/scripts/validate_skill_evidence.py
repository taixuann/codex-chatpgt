#!/usr/bin/env python3
"""Validate the separate behavioral skill-evidence envelope."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


STATUSES = {"PASS", "FAIL", "NOT_ASSESSED", "BLOCKED", "READY"}
REQUIRED = {
    "invocation_policy",
    "provenance",
    "routing_benchmark",
    "utility_ab",
    "efficiency_interference",
    "adapt_tournament",
    "regression_harvesting",
}


def validate_evidence(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["evidence must be a mapping"]
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if data.get("status") not in STATUSES:
        errors.append("status must be a recognized evidence status")
    missing = REQUIRED - set(data)
    errors.extend(f"missing evidence dimension: {name}" for name in sorted(missing))

    policy = data.get("invocation_policy", {})
    if not isinstance(policy, dict) or not isinstance(policy.get("host_field"), str):
        errors.append("invocation_policy.host_field is required")
    else:
        rules = policy.get("rules")
        if not isinstance(rules, dict):
            errors.append("invocation_policy.rules is required")
        else:
            for name in ("ADAPT", "EXPLICIT_ONLY", "REFERENCE_ONLY", "MERGE", "RETIRE"):
                if rules.get(name) is not False:
                    errors.append(f"invocation policy for {name} must be false")
            if rules.get("KEEP_without_behavioral_PASS") is not False:
                errors.append("KEEP_without_behavioral_PASS must be false")

    provenance = data.get("provenance", {})
    if not isinstance(provenance, dict):
        errors.append("provenance must be a mapping")
    else:
        for field in ("runtime", "model", "trace_format"):
            if not str(provenance.get(field, "")).strip():
                errors.append(f"provenance.{field} is required")

    routing = data.get("routing_benchmark", {})
    if not isinstance(routing, dict):
        errors.append("routing_benchmark must be a mapping")
    else:
        active = routing.get("co_loaded_active_set")
        cases = routing.get("cases")
        per_skill = routing.get("cases_per_canonical_skill")
        if not isinstance(active, list) or len(active) != 6:
            errors.append("routing benchmark requires six co-loaded active skills")
        if not isinstance(cases, int) or cases < 60:
            errors.append("routing benchmark requires at least 60 cases")
        if not isinstance(per_skill, int) or per_skill < 10:
            errors.append("routing benchmark requires at least 10 cases per active skill")
        if not isinstance(routing.get("repeats_requested"), int) or routing["repeats_requested"] < 3:
            errors.append("routing benchmark requires at least three repeats")

    utility = data.get("utility_ab", {})
    if not isinstance(utility, dict):
        errors.append("utility_ab must be a mapping")
    else:
        for field in ("protocol", "with_condition", "without_condition"):
            if not str(utility.get(field, "")).strip():
                errors.append(f"utility_ab.{field} is required")

    efficiency = data.get("efficiency_interference", {})
    if not isinstance(efficiency, dict) or not isinstance(efficiency.get("measures"), list):
        errors.append("efficiency_interference.measures is required")

    tournament = data.get("adapt_tournament", {})
    if not isinstance(tournament, dict) or not isinstance(tournament.get("first_round"), list) or len(tournament["first_round"]) != 3:
        errors.append("adapt tournament first_round must contain the first three candidates")

    regression = data.get("regression_harvesting", {})
    if not isinstance(regression, dict):
        errors.append("regression_harvesting must be a mapping")
    else:
        if regression.get("governance") != "OBSERVE -> PROPOSE -> REVIEW -> ACCEPT -> UPDATE":
            errors.append("regression harvesting governance is incomplete")
        if regression.get("catalog_or_description_self_mutation") is not False:
            errors.append("regression harvesting must not self-mutate catalog or descriptions")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        data = yaml.safe_load(args.manifest.read_text(encoding="utf-8")) or {}
        errors = validate_evidence(data)
    except (OSError, yaml.YAMLError) as exc:
        print(f"FAIL skill evidence: {exc}")
        return 1
    if errors:
        for error in errors:
            print(f"FAIL skill evidence: {error}")
        return 1
    print("OK skill evidence envelope: routing, utility, efficiency, interference, tournament, and regression dimensions present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
