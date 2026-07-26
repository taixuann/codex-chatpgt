#!/usr/bin/env python3
"""Validate a Franky entrypoint or nested pipeline contract."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required to validate workflow YAML") from exc


REQUIRED_STEP_FIELDS = {"id", "skill", "operation", "inputs", "outputs", "validation", "approval_gate", "on_failure"}
FORBIDDEN_KEYS = {"model", "executor", "provider", "backend"}
REQUIRED_APPROVAL_FIELDS = {"required", "reason"}


def walk_forbidden(value: object, path: str = "workflow") -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in FORBIDDEN_KEYS:
                return f"forbidden key {key!r} at {path}"
            found = walk_forbidden(child, f"{path}.{key}")
            if found:
                return found
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found = walk_forbidden(child, f"{path}[{index}]")
            if found:
                return found
    return None


def validate_document(data: object, path: Path, *, nested: bool = False) -> list[Path]:
    if not isinstance(data, dict):
        raise ValueError("workflow must be a mapping")
    if not data.get("id") or not data.get("name") or not isinstance(data.get("steps"), list):
        raise ValueError("workflow requires id, name, and steps")
    if not isinstance(data.get("version"), int) or data["version"] < 1:
        raise ValueError("workflow requires a positive integer version")
    if data.get("invocation_policy") != "workflow_only":
        raise ValueError("workflow invocation_policy must be workflow_only")
    if nested and not isinstance(data.get("branch"), dict):
        raise ValueError("nested pipeline requires branch metadata")
    if "branch" in data:
        branch = data["branch"]
        if not isinstance(branch, dict) or not isinstance(branch.get("key"), str) or not isinstance(branch.get("value"), str):
            raise ValueError("branch requires string key and value")
    seen: set[str] = set()
    for step in data["steps"]:
        if not isinstance(step, dict):
            raise ValueError("each step must be a mapping")
        missing = REQUIRED_STEP_FIELDS - step.keys()
        if missing:
            raise ValueError(f"step missing fields: {', '.join(sorted(missing))}")
        if step["id"] in seen:
            raise ValueError(f"duplicate step id: {step['id']}")
        seen.add(step["id"])
        if step["on_failure"] != "return_to_human":
            raise ValueError(f"step {step['id']} must return_to_human on failure")
        if not isinstance(step["skill"], str) or not step["skill"]:
            raise ValueError(f"step {step['id']} skill must be a non-empty string")
        if not isinstance(step["operation"], str) or not step["operation"]:
            raise ValueError(f"step {step['id']} operation must be a non-empty string")
        for field in ("inputs", "outputs", "validation"):
            if not isinstance(step[field], list):
                raise ValueError(f"step {step['id']} {field} must be a list")
        gate = step["approval_gate"]
        if not isinstance(gate, dict) or REQUIRED_APPROVAL_FIELDS - gate.keys():
            raise ValueError(f"step {step['id']} approval_gate must contain required and reason")
        if not isinstance(gate["required"], bool) or not isinstance(gate["reason"], str):
            raise ValueError(f"step {step['id']} approval_gate has invalid types")
        skill_path = Path("/Users/tai/.codex/skills") / step["skill"] / "SKILL.md"
        if not skill_path.is_file():
            raise ValueError(f"step {step['id']} references unavailable skill: {step['skill']}")
        if "condition" in step and not isinstance(step["condition"], str):
            raise ValueError(f"step {step['id']} condition must be a string")
    pipelines = data.get("pipelines", [])
    nested_paths: list[Path] = []
    if pipelines:
        if not isinstance(pipelines, list):
            raise ValueError("pipelines must be a list")
        seen_branches: set[tuple[str, str]] = set()
        for entry in pipelines:
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not isinstance(entry.get("branch"), dict):
                raise ValueError("each pipeline requires path and branch")
            branch = entry["branch"]
            key_value = (branch.get("key"), branch.get("value"))
            if not all(isinstance(item, str) and item for item in key_value):
                raise ValueError("pipeline branch requires non-empty string key and value")
            if key_value in seen_branches:
                raise ValueError(f"duplicate pipeline branch: {key_value}")
            seen_branches.add(key_value)
            nested_path = (path.parent / entry["path"]).resolve()
            if not nested_path.is_file():
                raise ValueError(f"missing nested pipeline: {entry['path']}")
            nested_data = yaml.safe_load(nested_path.read_text(encoding="utf-8"))
            validate_document(nested_data, nested_path, nested=True)
            if nested_data.get("branch") != branch:
                raise ValueError(f"branch metadata mismatch: {entry['path']}")
            nested_paths.append(nested_path)
    forbidden = walk_forbidden(data)
    if forbidden:
        raise ValueError(forbidden)
    return nested_paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow", type=Path)
    args = parser.parse_args()
    try:
        data = yaml.safe_load(args.workflow.read_text(encoding="utf-8"))
        nested_paths = validate_document(data, args.workflow)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL {args.workflow}: {exc}")
        return 1
    suffix = f"; {len(nested_paths)} nested pipelines" if nested_paths else ""
    print(f"OK {args.workflow}: {data['id']} ({len(data['steps'])} steps{suffix})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
