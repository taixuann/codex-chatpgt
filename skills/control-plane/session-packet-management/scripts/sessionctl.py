#!/usr/bin/env python3
"""Create one stage-aware session packet under <repo>/.agents/sessions/."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import subprocess
import sys

import yaml


SESSION_ID = re.compile(r"^[0-9]{8}_[a-z0-9]+(?:-[a-z0-9]+)*_[0-9]{3}$")
STAGES = {"intent", "plan", "execution", "review", "closeout"}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    if result.returncode:
        raise ValueError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def repo_root(value: Path | None) -> Path:
    candidate = (value or Path.cwd()).expanduser().resolve()
    return Path(git(candidate, "rev-parse", "--show-toplevel")).resolve()


def frontmatter(artifact: str, session_id: str, source_commit: str, recorded_by: str, upstream: list[str], downstream: list[str]) -> str:
    header = {
        "kind": "codex.session-artifact.v1",
        "artifact": artifact,
        "session_id": session_id,
        "status": "proposed",
        "provenance": {"source_commit": source_commit, "observed_at": now(), "recorded_by": recorded_by},
        "upstream": upstream,
        "downstream": downstream,
    }
    return "---\n" + yaml.safe_dump(header, sort_keys=False).rstrip() + "\n---\n\n"


def init_packet(root: Path, session_id: str, stage: str, origin: str, force: bool = False) -> Path:
    if not SESSION_ID.fullmatch(session_id):
        raise ValueError("session_id must match YYYYMMDD_slug_NNN")
    if stage not in STAGES:
        raise ValueError(f"stage must be one of {sorted(STAGES)}")
    packet = root / ".agents" / "sessions" / session_id
    if packet.exists() and any(packet.iterdir()) and not force:
        raise ValueError(f"packet already exists: {packet} (use --force only to refresh an empty/owned packet)")
    packet.mkdir(parents=True, exist_ok=True)
    observed = git(root, "rev-parse", "HEAD")
    if git(root, "status", "--porcelain"):
        observed = "uncommitted"
    recorded = now()
    artifacts = {"context": "context.md", "intent": "intent.md", "references": "references.yaml"}
    if stage != "intent":
        artifacts["plan"] = "plan.md"
    session = {
        "kind": "codex.session-packet.v1",
        "schema_version": 1,
        "session_id": session_id,
        "repository_root": str(root),
        "packet_root": f".agents/sessions/{session_id}",
        "stage": stage,
        "canonical_records": {"issue": origin if "#" in origin else None, "plan": None, "pr": None},
        "source_state": {"commit": observed, "recorded_at": recorded},
        "owner": "governed-task",
        "status": "proposed",
        "artifacts": artifacts,
    }
    (packet / "session.yaml").write_text(yaml.safe_dump(session, sort_keys=False), encoding="utf-8")
    plan_link = ["plan.md"] if stage != "intent" else []
    (packet / "context.md").write_text(
        frontmatter("context", session_id, observed, "intent", ["references.yaml"], ["intent.md", *plan_link])
        + f"# Context\n\nSession: `{session_id}`\n\nOrigin: `{origin}`\n\nRecord bounded, evidence-backed observations here.\n",
        encoding="utf-8",
    )
    (packet / "intent.md").write_text(
        frontmatter("intent", session_id, observed, "intent", ["context.md"], plan_link)
        + "# Intent\n\n## STATUS\nPROPOSED\n\n## ORIGIN\n" + origin + "\n\n## WHY\n\n## OBJECTIVE\n\n## CURRENT STATE\n\n## TARGET STATE\n\n## SCOPE\n\n## OUT OF SCOPE\n\n## SUCCESS CRITERIA\n\n## RELATIONSHIPS\n\n## CONSTRAINTS / USER DECISIONS\n\n## EVIDENCE STATE\n- CONFIRMED:\n- INFERRED:\n- UNKNOWN:\n- USER_DECISION:\n- PROPOSED:\n\n## OPEN QUESTIONS\n\n## READINESS\nBLOCKED\n",
        encoding="utf-8",
    )
    if stage != "intent":
        (packet / "plan.md").write_text(
            frontmatter("plan", session_id, observed, "plan", ["context.md", "intent.md"], [])
            + "# Plan\n\nThis plan extends the validated intent in the same session packet.\n",
            encoding="utf-8",
        )
    references = {
        "kind": "codex.session-references.v1",
        "session_id": session_id,
        "references": [
            {"path": origin, "kind": "intent-origin", "state": "observed", "commit_or_hash": observed, "observed_at": recorded, "relationship": "source-origin"},
            {"path": "documentation/architecture/workflow/operation.md", "kind": "canonical-policy", "state": "current", "commit_or_hash": observed, "observed_at": recorded, "relationship": "governing-lifecycle"},
        ],
    }
    (packet / "references.yaml").write_text(yaml.safe_dump(references, sort_keys=False), encoding="utf-8")
    return packet


def advance_packet(packet: Path, stage: str) -> Path:
    """Extend an existing packet without creating a second session."""
    if stage not in STAGES:
        raise ValueError(f"stage must be one of {sorted(STAGES)}")
    session_path = packet / "session.yaml"
    session = yaml.safe_load(session_path.read_text(encoding="utf-8"))
    if not isinstance(session, dict) or session.get("kind") != "codex.session-packet.v1":
        raise ValueError("packet session.yaml is invalid")
    current = session.get("stage", "intent")
    order = {name: index for index, name in enumerate(("intent", "plan", "execution", "review", "closeout"))}
    if order[stage] < order.get(current, -1):
        raise ValueError("cannot move a packet to an earlier stage")
    session_id = session.get("session_id")
    if not isinstance(session_id, str) or not SESSION_ID.fullmatch(session_id):
        raise ValueError("session_id is invalid")
    source_commit = session.get("source_state", {}).get("commit", "uncommitted")
    if stage != "intent" and not (packet / "plan.md").exists():
        (packet / "plan.md").write_text(
            frontmatter("plan", session_id, source_commit, "plan", ["context.md", "intent.md"], [])
            + "# Plan\n\nThis plan extends the validated intent in the same session packet.\n",
            encoding="utf-8",
        )
        context = packet / "context.md"
        context_text = context.read_text(encoding="utf-8")
        if "plan.md" not in context_text:
            context.write_text(context_text.replace("- intent.md\n", "- intent.md\n- plan.md\n"), encoding="utf-8")
        intent = packet / "intent.md"
        intent_text = intent.read_text(encoding="utf-8")
        if "downstream: []" in intent_text:
            intent.write_text(intent_text.replace("downstream: []", "downstream:\n  - plan.md"), encoding="utf-8")
    session["stage"] = stage
    artifacts = session.setdefault("artifacts", {})
    artifacts.update({"context": "context.md", "intent": "intent.md", "references": "references.yaml"})
    if stage != "intent":
        artifacts["plan"] = "plan.md"
    session_path.write_text(yaml.safe_dump(session, sort_keys=False), encoding="utf-8")
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sessionctl")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--repo-root", type=Path)
    init.add_argument("--session-id", required=True)
    init.add_argument("--stage", choices=sorted(STAGES), default="intent")
    init.add_argument("--origin", required=True)
    init.add_argument("--force", action="store_true")
    advance = sub.add_parser("advance")
    advance.add_argument("--packet", type=Path, required=True)
    advance.add_argument("--stage", choices=sorted(STAGES), required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            root = repo_root(args.repo_root)
            packet = init_packet(root, args.session_id, args.stage, args.origin, args.force)
            print(packet)
            return 0
        if args.command == "advance":
            packet = advance_packet(args.packet.expanduser().resolve(), args.stage)
            print(packet)
            return 0
    except (OSError, ValueError, subprocess.SubprocessError, yaml.YAMLError) as exc:
        print(f"FAIL sessionctl: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
