#!/usr/bin/env python3
"""Validate the required files and cross-references in a Franky goal package."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required to validate goal packages") from exc


REQUIRED = ("GOAL.md", "PLAN.md", "TASKS.md")


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
        promotion_path = package / "PROMOTION.yaml"
        if promotion_path.is_file():
            promotion = promotion_path.read_text(encoding="utf-8")
            if f"goal_id: {goal_id}" not in promotion:
                raise ValueError("PROMOTION.yaml does not reference the goal id")
            if "source_root: /Users/tai/.codex" not in promotion:
                raise ValueError("PROMOTION.yaml must use the Codex source root")
        elif not (package / "context.md").is_file():
            raise ValueError("legacy package without PROMOTION.yaml must retain context.md")
        goal_text = (package / "GOAL.md").read_text(encoding="utf-8")
        if "revision:" in goal_text and "current_pointer:" not in goal_text:
            raise ValueError("GOAL.md revision metadata must declare current_pointer")
        session = package / "SESSION.yaml"
        if session.is_file():
            session_data = yaml.safe_load(session.read_text(encoding="utf-8"))
            if not isinstance(session_data, dict) or session_data.get("goal_id") != goal_id:
                raise ValueError("SESSION.yaml goal_id does not match GOAL.md")
            if session_data.get("lifecycle") != ["qualify", "select_role", "load_role_ontology", "draft", "validate", "human_review", "materialize", "execute", "revise"]:
                raise ValueError("SESSION.yaml lifecycle does not match the Franky contract")
        revisions = package / "revisions"
        if revisions.exists():
            current = revisions / "current.yaml"
            if not current.is_file():
                raise ValueError("revisions directory requires current.yaml")
            pointer = yaml.safe_load(current.read_text(encoding="utf-8"))
            if not isinstance(pointer, dict) or not all(pointer.get(key) for key in ("revision_id", "snapshot", "sha256")):
                raise ValueError("current pointer requires revision_id, snapshot, and sha256")
    except (OSError, ValueError) as exc:
        print(f"FAIL {package}: {exc}")
        return 1
    mode = "canonical" if (package / "PROMOTION.yaml").is_file() else "legacy compatibility"
    print(f"OK {package}: {goal_id} ({mode})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
