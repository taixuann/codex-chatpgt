#!/usr/bin/env python3
"""Reject scheduled mutation paths outside existing personal skills."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

ROOT = Path("/Users/tai/.codex/skills").resolve()
FORBIDDEN = {".system", "agents", "workflows", "schedulers", "credentials", "memories", "sessions", "ops"}

def validate(path: Path) -> None:
    resolved = path.resolve()
    try: relative = resolved.relative_to(ROOT)
    except ValueError as exc: raise ValueError(f"outside personal skills root: {path}") from exc
    if not relative.parts or relative.parts[0] == ".system":
        raise ValueError(f"scheduled scope is not an existing personal skill: {path}")
    if any(part in FORBIDDEN for part in relative.parts): raise ValueError(f"forbidden scheduled path: {path}")
    if not resolved.exists(): raise ValueError(f"scheduled target must already exist: {path}")

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("paths", nargs="+", type=Path); args = parser.parse_args()
    try:
        for path in args.paths: validate(path)
    except (OSError, ValueError) as exc: print(f"FAIL scheduled scope: {exc}"); return 1
    print(f"OK scheduled scope: {len(args.paths)} existing personal skill path(s)"); return 0
if __name__ == "__main__": sys.exit(main())
