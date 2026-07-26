#!/usr/bin/env python3
"""Create compact, redacted evidence from recent Codex session files."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import yaml

SECRET_PATH = re.compile(r"(^|/)(auth|credentials?|secrets?|tokens?|\.env)(/|$)", re.I)
SECRET_TEXT = re.compile(r"(sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9_]{12,}|BEGIN [A-Z ]+ PRIVATE KEY)")
SKILL = re.compile(r"(?:\$|skill(?:\s+|[:=]))([a-z0-9][a-z0-9-]{2,})", re.I)
FAILURE = re.compile(r"\b(fail(?:ed|ure)?|error|exception|traceback|return_to_human|blocked)\b", re.I)
CORRECTION = re.compile(r"\b(?:no,|not that|wrong|incorrect|you misunderstood|don't|do not|instead|fix this)\b", re.I)
UNRESOLVED = re.compile(r"\b(?:unresolved|blocked|needs approval|return_to_human|not completed)\b", re.I)

def clean_tree(root: Path) -> None:
    result = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True, check=True)
    if result.stdout.strip():
        raise ValueError("Codex checkout is dirty; scheduled maintenance stopped")

def lock(lock_path: Path) -> None:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        lock_path.mkdir()
        (lock_path / "owner").write_text(f"pid={os.getpid()}\n", encoding="utf-8")
    except FileExistsError as exc:
        raise ValueError(f"Franky maintenance lock already exists: {lock_path}") from exc

def unlock(lock_path: Path) -> None:
    owner = lock_path / "owner"
    if owner.exists(): owner.unlink()
    if lock_path.exists(): lock_path.rmdir()

def file_id(path: Path, root: Path) -> str:
    return hashlib.sha256(str(path.relative_to(root)).encode("utf-8")).hexdigest()[:16]

def inspect_file(path: Path, root: Path, cutoff: float, counters: dict[str, Counter], stats: Counter) -> None:
    if path.is_symlink() or not path.is_file() or path.stat().st_mtime < cutoff: return
    relative = str(path.relative_to(root))
    if SECRET_PATH.search(relative):
        stats["skipped_secret_like"] += 1; return
    try: raw = path.read_bytes()
    except OSError:
        stats["unreadable"] += 1; return
    if b"\x00" in raw:
        stats["skipped_binary"] += 1; return
    text = raw[:2_000_000].decode("utf-8", errors="replace")
    if path.suffix.lower() in {".json", ".jsonl"}:
        try:
            if path.suffix.lower() == ".json":
                json.loads(text)
            else:
                for line in text.splitlines():
                    if line.strip(): json.loads(line)
        except json.JSONDecodeError:
            stats["skipped_malformed"] += 1
            return
    if SECRET_TEXT.search(text):
        text = SECRET_TEXT.sub("[REDACTED]", text); stats["redacted_files"] += 1
    stats["files"] += 1
    counters["skills"].update(SKILL.findall(text))
    if FAILURE.search(text): counters["failure_files"][file_id(path, root)] += 1
    if CORRECTION.search(text): counters["correction_files"][file_id(path, root)] += 1
    if UNRESOLVED.search(text): counters["unresolved_files"][file_id(path, root)] += 1

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("/Users/tai/.codex"))
    parser.add_argument("--sessions-dir", type=Path)
    parser.add_argument("--since-hours", type=float, default=24)
    parser.add_argument("--require-clean", action="store_true")
    parser.add_argument("--lock-file", type=Path)
    parser.add_argument("--output", type=Path, default=Path("-"))
    args = parser.parse_args()
    root = args.root.resolve(); sessions = (args.sessions_dir or root / "sessions").resolve()
    lock_path = (args.lock_file or root / "ops" / ".franky-maintenance.lock").resolve(); held = False
    try:
        if args.require_clean: clean_tree(root)
        lock(lock_path); held = True; cutoff = time.time() - args.since_hours * 3600
        counters = {name: Counter() for name in ("skills", "failure_files", "correction_files", "unresolved_files")}; stats = Counter()
        if sessions.exists():
            for path in sessions.rglob("*"): inspect_file(path, sessions, cutoff, counters, stats)
        result = {"schema": "franky.session-inventory", "version": 1, "generated_at": datetime.now(timezone.utc).isoformat(), "window_hours": args.since_hours, "source_root": str(sessions), "raw_content_included": False, "stats": dict(stats), "evidence": {"skill_use": [{"skill": k, "count": v} for k, v in counters["skills"].most_common()], "failure_file_count": len(counters["failure_files"]), "correction_file_count": len(counters["correction_files"]), "unresolved_file_count": len(counters["unresolved_files"])}, "policy": {"personal_skills_only": True, "new_skill_creation": False, "result_md": False}}
        encoded = yaml.safe_dump(result, sort_keys=False)
        if str(args.output) == "-": sys.stdout.write(encoded)
        else: args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(encoded, encoding="utf-8")
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"FAIL session inventory: {exc}", file=sys.stderr); return 1
    finally:
        if held:
            try: unlock(lock_path)
            except OSError: pass
    return 0

if __name__ == "__main__": raise SystemExit(main())
