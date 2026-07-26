#!/usr/bin/env python3
"""Validate the registered Franky workflow families."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


EXPECTED = {"franky-install.yaml", "franky-maintenance.yaml", "general-workflow-factory.yaml"}
FORBIDDEN = {"franky-project-link.yaml"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    try:
        top_level = {path.name for path in args.root.glob("*.yaml")}
        missing = EXPECTED - top_level
        forbidden = FORBIDDEN & top_level
        if missing:
            raise ValueError(f"missing top-level workflows: {', '.join(sorted(missing))}")
        if forbidden:
            raise ValueError(f"standalone workflow remains: {', '.join(sorted(forbidden))}")
        for directory in (args.root / "franky-install", args.root / "franky-maintenance", args.root / "general-workflow-factory"):
            if not directory.is_dir():
                raise ValueError(f"missing workflow family directory: {directory}")
            if not any(directory.glob("*.yaml")):
                raise ValueError(f"workflow family is empty: {directory}")
    except (OSError, ValueError) as exc:
        print(f"FAIL {args.root}: {exc}")
        return 1
    print(f"OK {args.root}: {len(EXPECTED)}-entrypoint layout")
    return 0


if __name__ == "__main__":
    sys.exit(main())
