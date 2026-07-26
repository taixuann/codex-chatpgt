#!/usr/bin/env python3
"""Deterministically validate a compact Franky change record."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

import yaml

REQUIRED = {"change_id", "operation", "component", "scope", "preview", "approval", "changed_paths", "validation", "rollback", "git", "promotion"}
FORBIDDEN = (".system", "credentials", "linked-project", "linked_project", "result.md")
ALLOWED_PREFIXES = ("/Users/tai/.codex/", "ops/")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        if args.record.name == "result.md" or args.record.suffix != ".yaml":
            raise ValueError("change records must be YAML and result.md is forbidden")
        data = yaml.safe_load(args.record.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or REQUIRED - set(data):
            raise ValueError(f"missing required fields: {sorted(REQUIRED - set(data or {}))}")
        if not re.fullmatch(r"CHG-\d{8}-\d{3}", str(data["change_id"])):
            raise ValueError("change_id must match CHG-YYYYMMDD-NNN")
        for key in ("preview", "approval", "validation", "rollback", "git", "promotion"):
            if not isinstance(data[key], dict):
                raise ValueError(f"{key} must be a mapping")
        if not isinstance(data["scope"], list) or not isinstance(data["changed_paths"], list):
            raise ValueError("scope and changed_paths must be lists")
        if not data["preview"].get("digest") or data["approval"].get("preview_digest") != data["preview"]["digest"]:
            raise ValueError("approval must identify the exact preview digest")
        if data["approval"].get("granted") is not True:
            raise ValueError("approval.granted must be true")
        if data["git"].get("mode") != "local":
            raise ValueError("git.mode must be local")
        if data["promotion"].get("automatic") is not False:
            raise ValueError("automatic promotion is forbidden")
        paths = [str(p) for p in data["scope"] + data["changed_paths"]]
        for path in paths:
            normalized = path.replace("\\", "/").lower()
            if any(marker in normalized for marker in FORBIDDEN):
                raise ValueError(f"forbidden path: {path}")
            if path.startswith("/") and not path.startswith(ALLOWED_PREFIXES[0]):
                raise ValueError(f"path outside Codex scope: {path}")
            if not path.startswith(ALLOWED_PREFIXES) and not path.startswith("/Users/tai/.codex/"):
                raise ValueError(f"unrelated path: {path}")
        if any(Path(p).name == "result.md" for p in paths):
            raise ValueError("result.md is forbidden")
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL {args.record}: {exc}")
        return 1
    print(f"OK {args.record}: {data['change_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
