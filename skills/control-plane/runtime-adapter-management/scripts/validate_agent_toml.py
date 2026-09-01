#!/usr/bin/env python3
"""Validate a Codex runtime-agent TOML adapter."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tomllib


REQUIRED = {
    "name",
    "description",
    "model",
    "model_reasoning_effort",
    "sandbox_mode",
    "developer_instructions",
}
ALLOWED = set(REQUIRED)
ALLOWED_SANDBOX = {"read-only", "workspace-write", "danger-full-access"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("agent", type=Path)
    args = parser.parse_args()
    try:
        data = tomllib.loads(args.agent.read_text(encoding="utf-8"))
        missing = REQUIRED - data.keys()
        if missing:
            raise ValueError(f"missing fields: {', '.join(sorted(missing))}")
        unknown = set(data) - ALLOWED
        if unknown:
            raise ValueError(f"unknown fields: {', '.join(sorted(unknown))}")
        if data["sandbox_mode"] not in ALLOWED_SANDBOX:
            raise ValueError(f"unsupported sandbox_mode: {data['sandbox_mode']}")
        if not data["developer_instructions"].strip():
            raise ValueError("developer_instructions must not be empty")
        if data["name"] != args.agent.stem and not (args.agent.parent.name == "templates" and args.agent.stem == "agent"):
            raise ValueError("name must match the filename stem")
    except (OSError, tomllib.TOMLDecodeError, ValueError) as exc:
        print(f"FAIL {args.agent}: {exc}")
        return 1
    print(f"OK {args.agent}: {data['name']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
