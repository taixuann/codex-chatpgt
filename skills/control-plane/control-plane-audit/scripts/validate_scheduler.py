#!/usr/bin/env python3
"""Validate a bounded scheduled-task definition."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import yaml

REQUIRED = {"schema", "version", "id", "surface", "cadence", "timezone", "project_root", "mode", "skill", "workflow", "scope", "forbidden", "preconditions", "output"}
FORBIDDEN = {".system", "project skills", "agents", "workflows", "schedulers", "credentials", "memories", "sessions", "linked projects", "AI Labs", "push", "new skill creation"}

def validate(data: object) -> None:
    if not isinstance(data, dict): raise ValueError("scheduler must be a mapping")
    missing = REQUIRED - data.keys()
    if missing: raise ValueError(f"missing fields: {', '.join(sorted(missing))}")
    if data["schema"] != "control_plane.scheduler" or data["version"] != 1: raise ValueError("invalid scheduler schema/version")
    if data["surface"] != "chatgpt_scheduled_task" or data["cadence"] != "daily": raise ValueError("scheduler must be a daily ChatGPT Scheduled Task")
    if data["mode"] != "scheduled_safe" or data["skill"] != "control-plane-audit" or data["workflow"] not in {"issue-plan", "issue-plan-skill"}: raise ValueError("invalid scheduled routing")
    if not isinstance(data["scope"], list) or not data["scope"]: raise ValueError("scope must be a non-empty list")
    if not isinstance(data["forbidden"], list) or not FORBIDDEN.issubset(set(data["forbidden"])): raise ValueError("forbidden scope is incomplete")
    if not isinstance(data["preconditions"], list) or not {"clean_git_tree", "single_run_lock", "personal_skill_allowlist"}.issubset(set(data["preconditions"])): raise ValueError("preconditions are incomplete")
    if not isinstance(data["output"], dict) or data["output"].get("result_md") is not False: raise ValueError("scheduler must forbid result.md")
    if data.get("automatic_mutation") != "existing_personal_skill_only": raise ValueError("automatic mutation boundary is invalid")
    if not isinstance(data.get("model"), str) or not data["model"].strip(): raise ValueError("scheduler model must be explicitly declared")
    if not isinstance(data.get("reasoning_effort"), str) or not data["reasoning_effort"].strip(): raise ValueError("scheduler reasoning_effort must be explicitly declared")

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("scheduler", type=Path); args = parser.parse_args()
    try: validate(yaml.safe_load(args.scheduler.read_text(encoding="utf-8")))
    except (OSError, ValueError, yaml.YAMLError) as exc: print(f"FAIL {args.scheduler}: {exc}"); return 1
    print(f"OK {args.scheduler}: control_plane.scheduler"); return 0
if __name__ == "__main__": sys.exit(main())
