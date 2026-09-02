#!/usr/bin/env python3
"""Validate the small Intent reference-selection contract."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


PROFILES = {"issue_light", "issue_focused", "issue_deep", "idea_light", "idea_focused", "idea_deep"}
METADATA = {"class", "purpose", "trigger", "required_observables", "negative_boundary"}
CLASSES = {"procedural", "output_contract", "matrix", "schema_reference"}


def validate(data: Any, root: Path) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        return ["schema_version must be 1"]
    profiles = data.get("profiles")
    references = data.get("references")
    stages = data.get("stage_procedures")
    if not isinstance(profiles, dict) or set(profiles) != PROFILES:
        errors.append("profiles must cover all six origin/depth profiles")
        profiles = profiles if isinstance(profiles, dict) else {}
    if not isinstance(references, dict) or not references:
        errors.append("references must be a non-empty mapping")
        references = references if isinstance(references, dict) else {}
    used: set[str] = set()
    if not isinstance(stages, dict) or not stages:
        errors.append("stage_procedures must be a non-empty mapping")
        stages = stages if isinstance(stages, dict) else {}
    for profile, names in profiles.items():
        if not isinstance(names, list) or not names:
            errors.append(f"profile {profile} must select at least one reference")
            continue
        for name in names:
            if name not in references:
                errors.append(f"profile {profile} names unknown reference: {name}")
    for stage, names in stages.items():
        if not isinstance(names, list) or not names:
            errors.append(f"stage {stage} must select at least one procedure")
            continue
        for name in names:
            used.add(name)
            if name not in references:
                errors.append(f"stage {stage} names unknown reference: {name}")
    matrix_path = root / "requirement-matrix.yaml"
    if matrix_path.is_file():
        try:
            matrix = yaml.safe_load(matrix_path.read_text(encoding="utf-8"))
            required_stages = set(matrix.get("stages", [])) if isinstance(matrix, dict) else set()
            missing_stages = required_stages - set(stages)
            if missing_stages:
                errors.append(f"required matrix stages have no procedure mapping: {sorted(missing_stages)}")
        except yaml.YAMLError as exc:
            errors.append(f"requirement matrix is invalid: {exc}")
    for name, metadata in references.items():
        if not (root / name).is_file():
            errors.append(f"reference does not exist: {name}")
        if not isinstance(metadata, dict) or not METADATA <= set(metadata):
            errors.append(f"reference metadata incomplete: {name}")
            continue
        if metadata.get("class") not in CLASSES:
            errors.append(f"reference class invalid: {name}")
        observables = metadata.get("required_observables")
        if not isinstance(observables, list) or any(not isinstance(item, str) or not item.strip() for item in observables):
            errors.append(f"reference required_observables must be a list of strings: {name}")
        if metadata.get("class") == "procedural" and name not in used:
            errors.append(f"dead procedural reference is not selected by any stage: {name}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("policy", nargs="?", type=Path, default=Path(__file__).parents[1] / "references/reference-selection.yaml")
    args = parser.parse_args()
    try:
        data = yaml.safe_load(args.policy.read_text(encoding="utf-8"))
        errors = validate(data, args.policy.parent)
    except (OSError, yaml.YAMLError) as exc:
        print(f"FAIL reference selection: {exc}")
        return 1
    if errors:
        for error in errors:
            print(f"FAIL reference selection: {error}")
        return 1
    print("OK reference selection: six profiles, stage procedures, metadata, and no dead references")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
