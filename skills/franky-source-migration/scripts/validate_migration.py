#!/usr/bin/env python3
"""Validate a migration manifest before Franky local finalization."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PROTECTED = ("/.system/", "/credentials/", "/sessions/", "/memories/", "/linked-projects/")
STATUSES = {"add", "merge", "manual_review", "not_added"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("artifacts"), list):
        raise SystemExit("FAIL manifest requires an artifacts list")
    for item in data["artifacts"]:
        if not isinstance(item, dict) or not item.get("source") or not item.get("target"):
            raise SystemExit("FAIL every artifact requires source and target")
        if item.get("status") not in STATUSES:
            raise SystemExit(f"FAIL invalid status: {item.get('status')}")
        target = str(item["target"])
        if any(marker in target for marker in PROTECTED):
            raise SystemExit(f"FAIL protected target: {target}")
        if item["status"] in {"add", "merge"} and not item.get("approval_required", True):
            raise SystemExit("FAIL writes must require approval")
    digest = hashlib.sha256(args.manifest.read_bytes()).hexdigest()
    print(f"OK {args.manifest}: {len(data['artifacts'])} artifacts; sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
