#!/usr/bin/env python3
"""Create one explicitly approved reversible project-workspace symlink."""

from __future__ import annotations

import argparse
from pathlib import Path
import os
import sys


def validate(source: Path, target: Path, workspace_root: Path) -> tuple[Path, Path]:
    source = source.resolve()
    workspace_root = workspace_root.resolve()
    target_parent = target.parent.resolve()
    if ".system" in source.parts:
        raise ValueError("system-owned skills are not linkable")
    if not source.is_dir():
        raise ValueError("source is not a directory")
    if workspace_root not in (target_parent, *target_parent.parents):
        raise ValueError(f"target is outside trusted workspace: {workspace_root}")
    if target.exists() or target.is_symlink():
        raise ValueError("target already exists")
    return source, target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--workspace-root", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="create the link")
    args = parser.parse_args()
    try:
        source, target = validate(args.source, args.target, args.workspace_root)
        if not args.apply:
            print(f"OK proposed {target} -> {source}; rerun with --apply to create")
            return 0
        target.parent.mkdir(parents=True, exist_ok=False)
        os.symlink(source, target)
    except (OSError, ValueError) as exc:
        print(f"FAIL {args.target}: {exc}")
        return 1
    print(f"OK created {target} -> {source}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
