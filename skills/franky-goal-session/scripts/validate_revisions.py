#!/usr/bin/env python3
"""Validate immutable revision snapshots and the current pointer."""
from pathlib import Path
import argparse
import hashlib
import sys
import yaml

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    revisions = args.package / "revisions"
    current = revisions / "current.yaml"
    try:
        if not current.is_file():
            raise ValueError("missing revisions/current.yaml")
        pointer = yaml.safe_load(current.read_text(encoding="utf-8"))
        if not isinstance(pointer, dict) or not all(pointer.get(k) for k in ("revision_id", "snapshot", "sha256")):
            raise ValueError("current pointer requires revision_id, snapshot, and sha256")
        snapshot = revisions / str(pointer["snapshot"])
        if not snapshot.is_file() or digest(snapshot) != pointer["sha256"]:
            raise ValueError("current pointer digest or snapshot is invalid")
        if not str(pointer["revision_id"]).startswith("REV-"):
            raise ValueError("invalid revision_id")
        for path in sorted(revisions.glob("REV-*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or data.get("revision_id") != path.stem:
                raise ValueError(f"snapshot metadata mismatch: {path.name}")
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL {args.package}: {exc}")
        return 1
    print(f"OK {args.package}: current {pointer['revision_id']}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
