#!/usr/bin/env python3
"""Validate the required files and cross-references in a Franky goal package."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


REQUIRED = ("GOAL.md", "PLAN.md", "TASKS.md", "PROMOTION.yaml")


def frontmatter(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path.name}: missing YAML frontmatter")
    end = text.find("\n---", 4)
    if end < 0:
        raise ValueError(f"{path.name}: unterminated YAML frontmatter")
    return text[4:end]


def value(block: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", block, re.MULTILINE)
    return match.group(1).strip().strip("'\"") if match else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    package = args.package.resolve()
    try:
        missing = [name for name in REQUIRED if not (package / name).is_file()]
        if missing:
            raise ValueError(f"missing required files: {', '.join(missing)}")
        goal_id = value(frontmatter(package / "GOAL.md"), "id")
        plan_id = value(frontmatter(package / "PLAN.md"), "goal_id")
        if not goal_id or not re.fullmatch(r"GOAL-\d{8}-\d{3}", goal_id):
            raise ValueError("GOAL.md id must match GOAL-YYYYMMDD-NNN")
        if plan_id != goal_id:
            raise ValueError("PLAN.md goal_id does not match GOAL.md id")
        tasks = (package / "TASKS.md").read_text(encoding="utf-8")
        if goal_id not in tasks:
            raise ValueError("TASKS.md does not reference the goal id")
        promotion = (package / "PROMOTION.yaml").read_text(encoding="utf-8")
        if f"goal_id: {goal_id}" not in promotion:
            raise ValueError("PROMOTION.yaml does not reference the goal id")
        if "source_root: /Users/tai/.codex" not in promotion:
            raise ValueError("PROMOTION.yaml must use the Codex source root")
    except (OSError, ValueError) as exc:
        print(f"FAIL {package}: {exc}")
        return 1
    print(f"OK {package}: {goal_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
