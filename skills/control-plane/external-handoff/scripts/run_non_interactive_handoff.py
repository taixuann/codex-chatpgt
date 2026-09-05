#!/usr/bin/env python3
"""Run an explicitly approved executable without invoking a shell."""

from collections.abc import Sequence
import shlex
import subprocess
import sys
from pathlib import Path

SHELL_TOKENS = {";", "|", "||", "&", "&&", ">", ">>", "<", "`"}
CANONICAL_ORIGINS = {"git@github.com:taixuann/codex-chatpgt.git", "https://github.com/taixuann/codex-chatpgt.git"}
INSTALLED_CONTROL_PLANE_ROOT = Path(__file__).resolve().parents[4]


def _canonical_origin(value: str) -> str:
    value = value.strip().rstrip("/")
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.split(":", 1)[1]
    return value.removesuffix(".git")

def _verified_root(candidate: Path) -> Path:
    candidate = candidate.expanduser().resolve()
    if candidate != INSTALLED_CONTROL_PLANE_ROOT:
        raise RuntimeError(f"repo root is not the installed control-plane root: {candidate}")
    required_files = (
        candidate / "AGENTS.md",
        candidate / "agents" / "AGENTS.md",
        candidate / "skills" / "AGENTS.md",
    )
    if any(not path.is_file() for path in required_files):
        raise RuntimeError(f"not a control-plane repository root: {candidate}")
    try:
        marker = (candidate / "AGENTS.md").read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"cannot read control-plane marker: {candidate}") from exc
    if "Codex operator workbench" not in marker or "Canonical deployment role identity" not in marker:
        raise RuntimeError(f"not a canonical control-plane root: {candidate}")
    try:
        git_root = subprocess.run(["git", "-C", str(candidate), "rev-parse", "--show-toplevel"], check=True, capture_output=True, text=True).stdout.strip()
        origin = subprocess.run(["git", "-C", str(candidate), "remote", "get-url", "origin"], check=True, capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(f"control-plane root must be a Git repository with an origin: {candidate}") from exc
    if Path(git_root).resolve() != candidate or _canonical_origin(origin) not in {_canonical_origin(item) for item in CANONICAL_ORIGINS}:
        raise RuntimeError(f"control-plane root Git identity is not canonical: {candidate}")
    return candidate


def get_repo_root(explicit: Path | None = None) -> Path:
    if explicit is not None:
        return _verified_root(explicit)
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / "skills" / "AGENTS.md").is_file():
            return _verified_root(candidate)
    raise RuntimeError("cannot locate control-plane repository root")


def _argv(command: Sequence[str] | str) -> list[str]:
    tokens = shlex.split(command) if isinstance(command, str) else list(command)
    if not tokens or any(token in SHELL_TOKENS for token in tokens):
        raise ValueError("command must contain an executable and argv tokens, not shell syntax")
    return tokens


def run_non_interactive_handoff(command: Sequence[str] | str, *, repo_root: Path | None = None):
    if repo_root is None:
        raise ValueError("consequential handoff execution requires explicit --repo-root")
    repo_root = get_repo_root(repo_root)
    argv = _argv(command)
    print(f"Running non-interactive execution from repo root: {repo_root}")
    print(f"Executing argv: {argv!r}")

    res = subprocess.run(argv, shell=False, cwd=repo_root, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"Handoff execution completed cleanly:\n{res.stdout.strip()}")
    else:
        print(f"Handoff execution warning/failed (exit code {res.returncode}):\n{res.stderr.strip()}")

    return res.returncode

if __name__ == "__main__":
    try:
        argv = sys.argv[1:]
        explicit_root = None
        if argv[:1] == ["--repo-root"]:
            if len(argv) < 2:
                raise ValueError("--repo-root requires a path")
            explicit_root = Path(argv[1])
            argv = argv[2:]
        sys.exit(run_non_interactive_handoff(argv or ["echo", "Non-interactive execution test passed"], repo_root=explicit_root))
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Handoff rejected: {exc}", file=sys.stderr)
        sys.exit(2)
