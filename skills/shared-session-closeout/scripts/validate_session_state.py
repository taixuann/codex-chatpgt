#!/usr/bin/env python3
"""Validate the minimum shape of a routine change or AI Labs goal package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate(path: Path) -> dict[str, object]:
    path = path.resolve()
    errors: list[str] = []
    kind = "unknown"
    if path.is_file() and path.name == "change.yaml":
        kind = "routine_change"
        text = path.read_text(encoding="utf-8")
        for marker in ("operation:", "changed_paths:", "validation:", "promotion:"):
            if marker not in text:
                errors.append(f"missing change record field: {marker[:-1]}")
    elif path.is_dir() and path.name.startswith("GOAL-"):
        kind = "goal_package"
        for name in ("GOAL.md", "PLAN.md", "TASKS.md"):
            if not (path / name).is_file():
                errors.append(f"missing goal package file: {name}")
    else:
        errors.append("path must be a change.yaml file or GOAL-* directory")
    return {"path": str(path), "kind": kind, "valid": not errors, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    result = validate(args.path)
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
