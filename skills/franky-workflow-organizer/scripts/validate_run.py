#!/usr/bin/env python3
"""Validate a Franky workflow-run envelope and step authorization."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required to validate workflow runs") from exc


REQUIRED = {"workflow_id", "workflow_version", "change_id", "step_id", "allowed_skill", "operation", "input_artifact_ids", "approval_record"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("workflow", type=Path)
    args = parser.parse_args()
    try:
        run = yaml.safe_load(args.run.read_text(encoding="utf-8"))
        workflow = yaml.safe_load(args.workflow.read_text(encoding="utf-8"))
        if not isinstance(run, dict) or REQUIRED - run.keys():
            raise ValueError(f"run envelope missing: {', '.join(sorted(REQUIRED - set(run or {})))}")
        if run["workflow_id"] != workflow.get("id"):
            raise ValueError("run workflow_id does not match workflow")
        if run["workflow_version"] != workflow.get("version"):
            raise ValueError("run workflow_version does not match workflow")
        matches = [step for step in workflow.get("steps", []) if step.get("id") == run["step_id"]]
        if len(matches) != 1:
            raise ValueError("run step_id does not identify exactly one workflow step")
        step = matches[0]
        if run["allowed_skill"] != step.get("skill"):
            raise ValueError("run allowed_skill does not match current workflow step")
        if run["operation"] != step.get("operation"):
            raise ValueError("run operation does not match current workflow step")
        if not isinstance(run["input_artifact_ids"], list):
            raise ValueError("input_artifact_ids must be a list")
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL {args.run}: {exc}")
        return 1
    print(f"OK {args.run}: {run['workflow_id']} / {run['step_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
