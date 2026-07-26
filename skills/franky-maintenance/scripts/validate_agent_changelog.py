#!/usr/bin/env python3
"""Validate the Franky agent README and structured changelog contract."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


REQUIRED_KEYS = ("agent:", "version:", "goal_id:", "workflow_id:", "reason:", "changed_paths:", "validation:", "approval:", "change_commit:", "rollback:")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("agents_dir", type=Path)
    args = parser.parse_args()
    try:
        readme = args.agents_dir / "README.md"
        changelog = args.agents_dir / "CHANGELOG.md"
        if not readme.is_file() or not changelog.is_file():
            raise ValueError("agents README.md and CHANGELOG.md are required")
        text = changelog.read_text(encoding="utf-8")
        for key in REQUIRED_KEYS:
            if key not in text:
                raise ValueError(f"changelog missing {key}")
        versions = re.findall(r"^  version: (\d+\.\d+\.\d+)$", text, re.MULTILINE)
        if not versions:
            raise ValueError("changelog has no SemVer version")
        if "reason:" not in text or "goal_id:" not in text:
            raise ValueError("changelog entries require reason and goal_id")
    except (OSError, ValueError) as exc:
        print(f"FAIL {args.agents_dir}: {exc}")
        return 1
    print(f"OK {args.agents_dir}: {len(versions)} changelog entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
