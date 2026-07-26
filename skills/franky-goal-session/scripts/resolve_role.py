#!/usr/bin/env python3
"""Resolve one Franky goal role from the bundled role references."""
from pathlib import Path
import argparse
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("role")
    parser.add_argument("--roles", type=Path, default=ROOT / "references/roles")
    args = parser.parse_args()
    path = args.roles / f"{args.role.lower()}.yaml"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("role_id") != args.role.lower():
            raise ValueError("role reference is missing or has a mismatched role_id")
        for key in ("stable_id", "category", "scope", "approval_gates"):
            if not data.get(key):
                raise ValueError(f"role reference missing {key}")
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL {args.role}: {exc}")
        return 1
    print(yaml.safe_dump(data, sort_keys=False).rstrip())
    return 0

if __name__ == "__main__":
    sys.exit(main())
