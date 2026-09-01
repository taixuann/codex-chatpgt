#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import yaml

REQUIRED = {"schema", "version", "audit_id", "component_type", "component_id", "operation", "scope", "source", "destination", "inputs", "outputs", "cache", "protected_paths", "collisions", "dependencies", "overview", "preview", "rollback", "status", "findings"}
TYPES = {"skill", "agent", "workflow", "cron", "guidance", "project_link", "maintenance"}

def validate(data: object) -> None:
    if not isinstance(data, dict): raise ValueError("audit record must be a mapping")
    missing = REQUIRED - data.keys()
    if missing: raise ValueError(f"missing fields: {', '.join(sorted(missing))}")
    if data["schema"] != "control_plane.audit" or not isinstance(data["version"], int) or data["version"] < 1: raise ValueError("invalid schema or version")
    if data["component_type"] not in TYPES: raise ValueError("unsupported component_type")
    for key in ("audit_id", "component_id", "operation", "scope", "status"):
        if not isinstance(data[key], str) or not data[key].strip(): raise ValueError(f"{key} must be a non-empty string")
    for key in ("inputs", "outputs", "cache", "protected_paths", "overview", "preview", "rollback"):
        if not isinstance(data[key], dict): raise ValueError(f"{key} must be a mapping")
    for key in ("collisions", "dependencies", "findings"):
        if not isinstance(data[key], list): raise ValueError(f"{key} must be a list")
    if data["cache"].get("mode", "no-cache") not in {"no-cache", "read-only", "approved-write"}: raise ValueError("invalid cache mode")
    if not isinstance(data["overview"].get("impact"), str) or not isinstance(data["overview"].get("references", []), list): raise ValueError("overview requires impact and references")
    if not isinstance(data["preview"].get("changed_paths", []), list): raise ValueError("preview.changed_paths must be a list")
    for path in data["protected_paths"].get("touched", []):
        if any(token in str(path).lower() for token in (".system", "credential", "secret", "linked-project")): raise ValueError("protected path touched")

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("record", type=Path); args = parser.parse_args()
    try: validate(yaml.safe_load(args.record.read_text(encoding="utf-8")))
    except (OSError, ValueError, yaml.YAMLError) as exc: print(f"FAIL {args.record}: {exc}"); return 1
    print(f"OK {args.record}: control_plane.audit"); return 0
if __name__ == "__main__": sys.exit(main())
