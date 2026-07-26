#!/usr/bin/env python3
"""Create one immutable goal revision and advance its current pointer."""
from pathlib import Path
import argparse
import hashlib
import re
import sys
import yaml

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("source", type=Path, help="YAML snapshot input")
    args = parser.parse_args()
    revisions = args.package / "revisions"
    try:
        data = yaml.safe_load(args.source.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("source snapshot must be a YAML mapping")
        revisions.mkdir(exist_ok=True)
        numbers = [int(match.group(1)) for path in revisions.glob("REV-*.yaml") if (match := re.fullmatch(r"REV-(\d{3})\.yaml", path.name))]
        number = max(numbers, default=0) + 1
        revision_id = f"REV-{number:03d}"
        snapshot = revisions / f"{revision_id}.yaml"
        data = {"revision_id": revision_id, "parent_revision": f"REV-{number - 1:03d}" if number > 1 else None, "payload": data}
        snapshot.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        sha256 = hashlib.sha256(snapshot.read_bytes()).hexdigest()
        (revisions / "current.yaml").write_text(yaml.safe_dump({"revision_id": revision_id, "snapshot": snapshot.name, "sha256": sha256}, sort_keys=False), encoding="utf-8")
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL {args.package}: {exc}")
        return 1
    print(f"OK {args.package}: created {revision_id}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
