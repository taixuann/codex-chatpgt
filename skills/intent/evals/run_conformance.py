#!/usr/bin/env python3
"""Review observable Intent conformance without exposing reviewer expectations."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).parents[1]
POLICY = ROOT / "references/reference-selection.yaml"


def load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def expected_refs(policy: dict[str, Any], profile: str, material_relationships: bool = False) -> set[str]:
    refs = set(policy["profiles"][profile])
    conditional = policy.get("conditional", {}).get("relationship-audit.md", {})
    if profile in conditional.get("profiles", []) and not material_relationships:
        refs.discard("relationship-audit.md")
    if profile in conditional.get("profiles", []) and material_relationships:
        refs.add("relationship-audit.md")
    return refs


def review(case: dict[str, Any], observation: dict[str, Any] | None, policy: dict[str, Any]) -> dict[str, Any]:
    if observation is None:
        return {
            "id": case["id"],
            "prompt": case["prompt"],
            "level": "L4_NATIVE_ROUTING",
            "result": "NOT_ASSESSED",
            "limitations": ["host does not expose isolated native skill/reference selection"],
        }
    profile = f"{'issue' if case['origin'] == 'github_issue' else 'idea'}_{case['depth']}"
    expected = expected_refs(policy, profile, bool(case.get("material_relationships")))
    observed = set(observation.get("observed_references", []))
    missing = sorted(expected - observed)
    extra = sorted(observed - expected)
    required = set(observation.get("required_observables", []))
    actual = set(observation.get("observables", []))
    missing_observables = sorted(required - actual)
    routing_ok = observation.get("observed_capability") == case["capability"]
    result = "pass" if routing_ok and not missing and not extra and not missing_observables and not observation.get("unnecessary_actions") else "fail"
    return {
        "id": case["id"],
        "prompt": case["prompt"],
        "origin": case["origin"],
        "depth": case["depth"],
        "level": "L2_DETERMINISTIC_CONFORMANCE",
        "routing": {"expected": case["capability"], "observed": observation.get("observed_capability"), "result": "pass" if routing_ok else "fail"},
        "references": {"expected": sorted(expected), "observed": sorted(observed), "missing": missing, "unnecessary": extra},
        "steps": {"required": sorted(required), "observed": sorted(actual), "missing": missing_observables},
        "questions": observation.get("questions", []),
        "artifacts": observation.get("artifacts", {}),
        "unnecessary_actions": observation.get("unnecessary_actions", []),
        "missing_actions": observation.get("missing_actions", []),
        "limitations": observation.get("limitations", []),
        "overall": result,
    }


def run(cases: dict[str, Any], observations: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    results = []
    for case in cases.get("cases", []):
        obs = observations.get("cases", {}).get(case["id"])
        if obs is not None and "required_observables" not in obs:
            obs["required_observables"] = []
        results.append(review(case, obs, policy))
    return {
        "schema_version": 1,
        "reviewer": observations.get("reviewer", "independent-deterministic-reviewer"),
        "execution": {
            "mode": "deterministic_fixture",
            "blind_prompts": True,
            "native_routing": "NOT_ASSESSED",
            "reason": "the local host exposes no isolated agent transcript/tool-selection events",
        },
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=Path(__file__).with_name("cases.yaml"))
    parser.add_argument("--observations", type=Path, default=Path(__file__).with_name("conformance.yaml"))
    args = parser.parse_args()
    try:
        report = run(load(args.cases), load(args.observations), load(POLICY))
    except (OSError, KeyError, TypeError, yaml.YAMLError, ValueError) as exc:
        print(f"FAIL intent conformance: {exc}")
        return 1
    print(yaml.safe_dump(report, sort_keys=False).rstrip())
    return 0 if all(item.get("overall", item.get("result")) in {"pass", "NOT_ASSESSED"} for item in report["results"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
