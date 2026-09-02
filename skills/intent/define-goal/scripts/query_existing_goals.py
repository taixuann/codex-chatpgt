#!/usr/bin/env python3
"""Query existing goals in the repository's .trekker/sessions/ store."""

import argparse
import json
import re
import sys
from pathlib import Path


def get_repo_root() -> Path:
    curr = Path(__file__).resolve().parent
    for candidate in (curr, *curr.parents):
        if (candidate / ".git").exists() or (candidate / "manifests" / "skill-catalog.yaml").is_file():
            return candidate
    raise RuntimeError("Could not locate repo root")


ROOT = get_repo_root()
SESSIONS_DIR = ROOT / ".trekker" / "sessions"


def parse_version(goal_file: Path) -> str:
    if not goal_file.exists():
        return "v1.0.0"
    content = goal_file.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"version[:`\s]*v?(\d+\.\d+\.\d+)", content, re.IGNORECASE)
    if match:
        return f"v{match.group(1)}"
    return "v1.0.0"


def query_goals(query: str = "") -> list[dict]:
    results = []
    if not SESSIONS_DIR.exists():
        return results

    query_lower = query.lower() if query else ""

    for session_path in sorted(SESSIONS_DIR.iterdir()):
        if not session_path.is_dir():
            continue

        goal_id = session_path.name
        goal_md = session_path / "GOAL.md"
        plan_md = session_path / "PLAN.md"

        goal_text = goal_md.read_text(encoding="utf-8", errors="ignore") if goal_md.exists() else ""
        plan_text = plan_md.read_text(encoding="utf-8", errors="ignore") if plan_md.exists() else ""

        combined = f"{goal_id} {goal_text} {plan_text}".lower()

        if query_lower and query_lower not in combined:
            continue

        version = parse_version(goal_md)

        results.append({
            "goal_id": goal_id,
            "path": str(session_path.relative_to(ROOT)),
            "version": version,
            "goal_file_exists": goal_md.exists(),
            "plan_file_exists": plan_md.exists(),
            "walkout_exists": (session_path / "WALKOUT").is_dir(),
        })

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Query existing goals in the repository")
    parser.add_argument("query", nargs="?", default="", help="Keyword query to search goals")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    matches = query_goals(args.query)

    if args.json:
        print(json.dumps({"count": len(matches), "goals": matches}, indent=2))
    else:
        print(f"Found {len(matches)} matching goal(s):")
        for m in matches:
            print(f"  • {m['goal_id']} [{m['version']}] -> {m['path']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
