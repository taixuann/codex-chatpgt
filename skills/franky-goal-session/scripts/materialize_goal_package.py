#!/usr/bin/env python3
"""Materialize a new goal package from the canonical Codex templates."""
from pathlib import Path
import argparse
import hashlib
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("goal_id", help="GOAL-YYYYMMDD-NNN")
    parser.add_argument("title")
    parser.add_argument("--workflow-id", default="WF-OPS-002")
    parser.add_argument("--role", default="franky")
    parser.add_argument("--objective", default="<one concrete outcome>")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"GOAL-\d{8}-\d{3}", args.goal_id):
        print("FAIL goal_id must match GOAL-YYYYMMDD-NNN")
        return 1
    if args.role.lower() not in {"franky", "feynman", "prometheus"}:
        print("FAIL role must resolve to franky, feynman, or prometheus")
        return 1
    if args.output.exists() and any(args.output.iterdir()) and not args.force:
        print(f"FAIL output is non-empty: {args.output}")
        return 1
    args.output.mkdir(parents=True, exist_ok=True)
    substitutions = {"GOAL-YYYYMMDD-NNN": args.goal_id, "<short title>": args.title, "<goal title>": args.title, "<one concrete outcome>": args.objective, "WF-M1-001": args.workflow_id}
    for source in (ROOT / "references/templates").glob("*.md"):
        text = source.read_text(encoding="utf-8")
        for old, new in substitutions.items():
            text = text.replace(old, new)
        (args.output / source.name).write_text(text, encoding="utf-8")
    (args.output / "context.md").write_text("# Context\n\nCanonical context is selected during qualification.\n", encoding="utf-8")
    (args.output / "walkthroughs").mkdir(exist_ok=True)
    (args.output / "SESSION.yaml").write_text("schema: franky.goal-session\nversion: 1\ngoal_id: " + args.goal_id + "\nrole: " + args.role + "\nlifecycle: [qualify, select_role, load_role_ontology, draft, validate, human_review, materialize, execute, revise]\nstatus: proposed\n", encoding="utf-8")
    (args.output / "PROMOTION.yaml").write_text(f"goal_id: {args.goal_id}\nstatus: proposed\nsource_root: /Users/tai/.codex\nrole: {args.role}\n", encoding="utf-8")
    revisions = args.output / "revisions"
    revisions.mkdir(exist_ok=True)
    snapshot = revisions / "REV-001.yaml"
    snapshot.write_text(yaml.safe_dump({
        "revision_id": "REV-001",
        "parent_revision": None,
        "payload": {
            "goal_id": args.goal_id,
            "title": args.title,
            "role": args.role.lower(),
            "workflow_id": args.workflow_id,
            "status": "proposed",
        },
    }, sort_keys=False), encoding="utf-8")
    (revisions / "current.yaml").write_text(yaml.safe_dump({
        "revision_id": "REV-001",
        "snapshot": "REV-001.yaml",
        "sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
    }, sort_keys=False), encoding="utf-8")
    print(f"OK materialized {args.goal_id} at {args.output}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
