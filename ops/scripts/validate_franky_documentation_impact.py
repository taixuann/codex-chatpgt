#!/usr/bin/env python3
"""Check that a Franky change records canonical documentation impact review."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import yaml


def required_surfaces(paths: list[str]) -> set[str]:
    surfaces: set[str] = set()
    for path in paths:
        if (
            path.startswith("/")
            or "\\" in path
            or path == ".."
            or path.startswith("../")
            or "/../" in path
        ):
            raise ValueError(f"changed_paths must be repository-relative: {path}")
        if path == "AGENTS.md" or path.startswith("agents/"):
            surfaces.update({"agent-guidance", "current-state", "operating-workflow"})
        if path.startswith("ops/schemas/") or path.startswith("ops/scripts/"):
            surfaces.add("validation-contracts")
        if path.startswith("documentation/"):
            surfaces.add("canonical-documentation")
        if path.startswith("manifests/"):
            surfaces.add("skill-ownership")
        if path.startswith(".github/workflows/"):
            surfaces.add("ci-workflow")
    return surfaces


def validate(path: Path) -> None:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if document.get("kind") != "franky.documentation-impact.v1":
        raise ValueError("fixture kind must be franky.documentation-impact.v1")
    paths = document.get("changed_paths")
    reviewed = set(document.get("reviewed_surfaces", []))
    if not isinstance(paths, list) or not paths:
        raise ValueError("changed_paths must be a non-empty list")
    required = required_surfaces([str(item) for item in paths])
    missing = sorted(required - reviewed)
    if missing:
        raise ValueError(f"documentation impact surfaces not reviewed: {', '.join(missing)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args()
    try:
        validate(args.fixture)
    except (OSError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL franky-documentation-impact: {exc}")
        return 1
    print("OK franky-documentation-impact: canonical review surfaces recorded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
