#!/usr/bin/env python3
"""Validate the compact skill-creator routing/lifecycle case contract."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import yaml


REQUIRED_ROUTING = {
    "route-explicit-positive",
    "route-implicit-positive",
    "route-contextual-positive",
    "route-adjacent-negative",
    "route-sibling-conflict",
}
REQUIRED_BEHAVIOR = {
    "create-local-upstream",
    "create-multimode-one-skill",
    "create-no-skill",
    "update-bounded",
    "update-substantive",
    "maintain-upstream-drift",
    "maintain-overlap",
    "maintain-localize",
    "maintain-retire",
    "evaluate-good",
    "evaluate-broad-description",
    "evaluate-sibling-collision",
    "evaluate-decorative-resources",
    "evaluate-skipped-process",
}


def validate(path: Path) -> list[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    cases = data.get("cases")
    if data.get("schema_version") != 1 or data.get("skill") != "skill-creator":
        return ["schema_version 1 and skill skill-creator are required"]
    if not isinstance(cases, list):
        return ["cases must be a list"]
    seen = {case.get("id") for case in cases if isinstance(case, dict)}
    errors = [f"missing case: {case_id}" for case_id in sorted((REQUIRED_ROUTING | REQUIRED_BEHAVIOR) - seen)]
    if len(seen) != len(cases):
        errors.append("case IDs must be unique and every case must be a mapping")
    for case in cases:
        if not isinstance(case, dict) or not case.get("prompt") or not case.get("kind"):
            errors.append("every case requires kind and prompt")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", type=Path)
    args = parser.parse_args()
    try:
        errors = validate(args.cases)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        print(f"FAIL eval cases: {exc}")
        return 1
    if errors:
        for error in errors:
            print(f"FAIL eval cases: {error}")
        return 1
    print(f"OK eval cases: {len(REQUIRED_ROUTING)} routing and {len(REQUIRED_BEHAVIOR)} behavioral cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
