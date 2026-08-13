#!/usr/bin/env python3
"""Validate the runtime-agent README and change-evidence contract.

Runtime adapters are intentionally versionless; any historical version field
in the append-only log is evidence metadata, not an adapter requirement.
"""

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
        if "reason:" not in text or "goal_id:" not in text:
            raise ValueError("changelog entries require reason and goal_id")
    except (OSError, ValueError) as exc:
        print(f"FAIL {args.agents_dir}: {exc}")
        return 1
    entries = len(re.findall(r"^(?:- )?agent: ", text, re.MULTILINE))
    print(f"OK {args.agents_dir}: {entries} changelog entries; adapters remain versionless")
    return 0


if __name__ == "__main__":
    sys.exit(main())
