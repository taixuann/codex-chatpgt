#!/usr/bin/env python3
"""Audit one proposed framework-to-Codex skill link without changing it."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


def audit(source: Path, target: Path, workspace_root: Path | None, proposed: bool) -> int:
    source = source.resolve()
    try:
        if ".system" in source.parts:
            raise ValueError("system-owned skills are not linkable")
        if not source.is_dir():
            raise ValueError("source is not a directory")
        if workspace_root:
            workspace_root = workspace_root.resolve()
            target_parent = target.parent.resolve()
            if workspace_root not in (target_parent, *target_parent.parents):
                raise ValueError(f"target is outside trusted workspace: {workspace_root}")
        if proposed and not target.exists() and not target.is_symlink():
            print(f"OK proposed {target} -> {source}")
            return 0
        if not target.is_symlink():
            raise ValueError("target is not a symlink")
        if target.resolve(strict=True) != source:
            raise ValueError(f"target resolves to {target.resolve()}, expected {source}")
    except (OSError, ValueError) as exc:
        print(f"FAIL {target}: {exc}")
        return 1
    print(f"OK {target} -> {source}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--workspace-root", type=Path, default=None)
    parser.add_argument("--proposed", action="store_true")
    args = parser.parse_args()
    return audit(args.source, args.target, args.workspace_root, args.proposed)


if __name__ == "__main__":
    sys.exit(main())
