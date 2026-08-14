#!/usr/bin/env python3
"""Run the deterministic Franky agent-contract oracle.

This is an evaluation oracle, not a runtime router. Native host selection and
model-mediated capability choice remain separate evidence gates.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import yaml


def classify(case: dict) -> dict:
    prompt = case["prompt"].lower()
    if case["invocation"] == "automatic":
        return {"admission": "parent_capability_first"}
    if "pytorch" in prompt or "phd sop" in prompt:
        return {
            "admission": "route_out",
            "route_target": "prometheus/research" if "pytorch" in prompt else "parent",
        }
    if case.get("runtime_skill_loading") == "unavailable":
        packet = case.get("task_packet") or {}
        required_capabilities = packet.get("required_capabilities") or []
        if packet.get("kind") != "franky.task.v1" or "control-plane-audit" not in required_capabilities:
            raise ValueError(f"{case['id']}: unavailable skill loading requires a Franky task packet with control-plane-audit")
        return {
            "admission": "in_scope",
            "operation_class": "control_plane_audit",
            "primary_capability": "control-plane-audit",
            "supporting_capabilities": [
                capability for capability in required_capabilities if capability != "control-plane-audit"
            ],
            "lifecycle_capability": "shared-session-closeout",
            "fallback_capability_path": "task_packet",
            "fallback_capability": "control-plane-audit",
        }
    if "rename skill" in prompt:
        return {
            "admission": "in_scope",
            "operation_class": "skill_rename_with_documentation",
            "primary_capability": "skill-authoring-and-quality",
            "supporting_capabilities": ["instruction-maintenance"],
            "lifecycle_capability": "shared-session-closeout",
        }
    if "fix skill description" in prompt:
        return {
            "admission": "in_scope",
            "operation_class": "skill_contract_repair",
            "primary_capability": "skill-authoring-and-quality",
            "supporting_capabilities": [],
            "lifecycle_capability": "shared-session-closeout",
        }
    if "arrhenius" in prompt or "research project" in prompt:
        return {"admission": "route_out"}
    if "audit" in prompt:
        return {
            "admission": "in_scope",
            "operation_class": "control_plane_audit",
            "primary_capability": "control-plane-audit",
            "supporting_capabilities": ["instruction-maintenance"],
            "lifecycle_capability": "shared-session-closeout",
        }
    if "repair" in prompt and "skill" in prompt:
        result = {
            "admission": "in_scope",
            "operation_class": "skill_contract_repair",
            "primary_capability": "skill-authoring-and-quality",
            "mutation_authority_required": True,
            "supporting_capabilities": ["control-plane-audit"],
            "lifecycle_capability": "shared-session-closeout",
        }
        if case.get("mutation_authority") != "allowed":
            result["admission"] = "blocked_without_mutation_authority"
        return result
    if "agent adapter" in prompt or "codex agent" in prompt:
        result = {
            "operation_class": "runtime_adapter_change",
            "primary_capability": "runtime-adapter-management",
            "mutation_authority_required": True,
            "supporting_capabilities": ["control-plane-audit"],
            "lifecycle_capability": "shared-session-closeout",
        }
        if case.get("mutation_authority") != "allowed":
            result["admission"] = "blocked_without_mutation_authority"
        else:
            result["admission"] = "in_scope"
        return result
    raise ValueError(f"no deterministic oracle branch for case: {case['id']}")


def validate(path: Path) -> int:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if document.get("oracle_boundary") != "deterministic contract oracle only; not a runtime router":
        raise ValueError("fixture must declare its non-router boundary")
    failures = []
    for case in document.get("cases", []):
        actual = classify(case)
        expected = case["expected"]
        for key, value in expected.items():
            if actual.get(key) != value:
                failures.append(f"{case['id']}.{key}: expected {value!r}, got {actual.get(key)!r}")
    if failures:
        raise ValueError("; ".join(failures))
    print(f"OK franky-agent-evaluation: {len(document.get('cases', []))} contract cases")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args()
    try:
        return validate(args.fixture)
    except (OSError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL franky-agent-evaluation: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
