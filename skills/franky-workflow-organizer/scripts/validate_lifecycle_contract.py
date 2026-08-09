#!/usr/bin/env python3
"""Validate Franky's shared lifecycle contract and compatibility entrypoints."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required to validate lifecycle contracts") from exc


REQUIRED_HANDOFF_FIELDS = {
    "source_workflow_id",
    "source_workflow_version",
    "target_workflow_id",
    "target_workflow_version",
    "purpose",
    "selected_branch",
    "change_id",
    "input_artifact_ids",
    "output_artifact_ids",
}
GOVERNANCE_SEQUENCE = [
    "qualify",
    "audit",
    "preview",
    "approve",
    "apply",
    "validate",
    "overview",
    "write-change-record",
    "local-git-finalize",
]
CANONICAL_ID = "WF-FRANKY-CANONICAL"


def load(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a mapping")
    return data


def validate(root: Path) -> None:
    contract_path = root / "lifecycle-contract.yaml"
    contract = load(contract_path)
    if contract.get("id") != "WF-FRANKY-CANONICAL-LIFECYCLE":
        raise ValueError("canonical lifecycle ID is incorrect")
    if contract.get("version") != 1:
        raise ValueError("canonical lifecycle version must be 1")
    if [step.get("id") for step in contract.get("steps", [])] != GOVERNANCE_SEQUENCE:
        raise ValueError("canonical lifecycle sequence does not match governance sequence")
    required = set(contract.get("handoff", {}).get("required_fields", []))
    missing = REQUIRED_HANDOFF_FIELDS - required
    if missing:
        raise ValueError(f"canonical lifecycle handoff fields missing: {', '.join(sorted(missing))}")

    canonical = load(root / "franky.yaml")
    if canonical.get("id") != CANONICAL_ID or canonical.get("canonical") is not True:
        raise ValueError("franky.yaml must be the canonical Franky entrypoint")
    if canonical.get("authority_scope") != "franky_control_plane" or canonical.get("semantic_authority") != "specialized_control_plane":
        raise ValueError("franky.yaml must declare specialized control-plane authority")
    if canonical.get("global_semantic_source") != "../../documentation/OPERATING-WORKFLOW.md":
        raise ValueError("franky.yaml must point to the global semantic lifecycle")
    if contract.get("authority_scope") != "franky_control_plane" or contract.get("semantic_authority") != "specialized_control_plane":
        raise ValueError("lifecycle contract must declare specialized control-plane authority")
    lifecycle = canonical.get("lifecycle_ref")
    if lifecycle != {"path": "lifecycle-contract.yaml", "workflow_id": contract["id"], "workflow_version": contract["version"]}:
        raise ValueError("franky.yaml lifecycle_ref does not match the canonical contract")
    if set(canonical.get("retired_entrypoint_ids", [])) != {"WF-FRANKY-INSTALL", "WF-FRANKY-MAINTENANCE"}:
        raise ValueError("franky.yaml must record all retired entrypoint IDs")
    apply_steps = [step for step in canonical.get("steps", []) if step.get("id") == "apply"]
    if len(apply_steps) != 1:
        raise ValueError("canonical workflow must contain exactly one apply step")
    apply_step = apply_steps[0]
    if "lifecycle handoff envelope" not in apply_step.get("outputs", []):
        raise ValueError("canonical apply step must emit a lifecycle handoff envelope")
    if "lifecycle target is explicit" not in apply_step.get("validation", []):
        raise ValueError("canonical apply step must validate its lifecycle target")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    try:
        validate(args.root)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL {args.root}: {exc}")
        return 1
    print(f"OK {args.root}: canonical lifecycle and compatibility entrypoints agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
