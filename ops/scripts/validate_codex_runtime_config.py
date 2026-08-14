#!/usr/bin/env python3
"""Validate the repository-owned minimal Codex [agents] contract fixture."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tomllib


EXPECTED = {
    "enabled": True,
    "max_concurrent_threads_per_session": 4,
    "interrupt_message": True,
}


def validate(path: Path) -> None:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    agents = data.get("agents")
    if not isinstance(agents, dict):
        raise ValueError("missing [agents] table")
    for key, expected in EXPECTED.items():
        if agents.get(key) != expected:
            raise ValueError(f"agents.{key}: expected {expected!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    args = parser.parse_args()
    try:
        validate(args.config)
    except (OSError, tomllib.TOMLDecodeError, ValueError) as exc:
        print(f"FAIL {args.config}: {exc}")
        return 1
    print(f"OK {args.config}: minimal [agents] contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
