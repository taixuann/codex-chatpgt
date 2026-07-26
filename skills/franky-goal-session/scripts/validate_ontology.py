#!/usr/bin/env python3
"""Validate the shared role and goal-session ontology."""
from pathlib import Path
import argparse
import sys
import yaml

REQUIRED_NODE_FIELDS = {"id", "stable_id", "kind", "version", "owner_role", "workflow_id", "inputs", "outputs", "validation", "approval_gate", "on_failure"}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ontology", type=Path)
    parser.add_argument("--roles", type=Path)
    args = parser.parse_args()
    try:
        data = yaml.safe_load(args.ontology.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("schema") != "franky.goal-session.ontology":
            raise ValueError("invalid ontology schema")
        metadata = data.get("node_metadata", {})
        missing = REQUIRED_NODE_FIELDS - set(metadata.get("required", []))
        if missing:
            raise ValueError(f"node metadata missing: {', '.join(sorted(missing))}")
        if metadata.get("failure_values") != ["return_to_human"]:
            raise ValueError("failure policy must be return_to_human")
        roles = args.roles or args.ontology.parent / "roles"
        role_files = sorted(roles.glob("*.yaml"))
        if {p.stem for p in role_files} != {"franky", "feynman", "prometheus"}:
            raise ValueError("ontology must have exactly franky, feynman, and prometheus role references")
        stable_ids = set()
        for path in role_files:
            role = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(role, dict) or not role.get("role_id") or not role.get("stable_id"):
                raise ValueError(f"invalid role reference: {path.name}")
            if role["stable_id"] in stable_ids:
                raise ValueError(f"duplicate role stable_id: {role['stable_id']}")
            stable_ids.add(role["stable_id"])
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL {args.ontology}: {exc}")
        return 1
    print(f"OK {args.ontology}: ontology and {len(role_files)} roles")
    return 0

if __name__ == "__main__":
    sys.exit(main())
