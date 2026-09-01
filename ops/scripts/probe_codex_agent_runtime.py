#!/usr/bin/env python3
"""Probe installed Codex agent settings without changing runtime state.

The parser check is deterministic. The live check is intentionally best-effort
and reports NOT_ASSESSED unless a completed model turn exposes observable child
agent and skill-selection evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


DEFAULT_CODEX = "/Applications/ChatGPT.app/Contents/Resources/codex"
SKILL_OVERRIDE = (
    'agents.franky.skills.config=[{path="skills/control-plane/control-plane-audit/SKILL.md",enabled=false}]'
)


def run(command: list[str], timeout: int) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", f"timeout after {timeout}s"
    except OSError as exc:
        return 127, "", f"runtime unavailable: {exc}"
    return completed.returncode, completed.stdout, completed.stderr


def probe(codex: str, live: bool, timeout: int) -> dict:
    version_code, version_out, version_err = run([codex, "--version"], timeout)
    parse_code, parse_out, parse_err = run(
        [codex, "--strict-config", "-c", SKILL_OVERRIDE, "--version"], timeout
    )
    help_code, help_out, help_err = run([codex, "exec", "--help"], timeout)
    result = {
        "codex": codex,
        "version": (version_out or version_err).strip(),
        "config_parse": "PASS" if parse_code == 0 else ("NOT_ASSESSED" if parse_code == 127 else "FAIL"),
        "config_parse_evidence": (parse_out or parse_err).strip(),
        "native_mention_hook": "NOT_ASSESSED",
        "native_mention_evidence": "@franky is not a documented codex exec option; host alias behavior is separate from CLI parsing",
        "actual_dispatch": "NOT_ASSESSED",
        "actual_dispatch_limitation": "No completed observable child-agent dispatch trace was available.",
        "skills_config_behavior": "NOT_ASSESSED",
        "skills_config_limitation": "No completed observable child-agent/skill-selection trace was available.",
        "mutation_escalation": "NOT_ASSESSED",
        "mutation_escalation_limitation": "The contract checks explicit mutation authority; host permission enforcement was not observable.",
        "live_turn": "NOT_RUN",
    }
    if version_code != 0:
        result["version_error"] = (version_out or version_err).strip()
    if help_code != 0:
        result["help_error"] = (help_out or help_err).strip()
    if not live:
        result["runtime_evidence"] = {
            "configuration": {"status": result["config_parse"], "evidence": result["config_parse_evidence"] or "No parser evidence."},
            "dispatch": {"status": result["actual_dispatch"], "evidence": result["actual_dispatch_limitation"]},
            "skill_loading": {"status": result["skills_config_behavior"], "evidence": result["skills_config_limitation"]},
            "mutation": {"status": result["mutation_escalation"], "evidence": result["mutation_escalation_limitation"]},
        }
        return result

    code, stdout, stderr = run(
        [
            codex,
            "exec",
            "--json",
            "--ephemeral",
            "--sandbox",
            "read-only",
            "--skip-git-repo-check",
            "-c",
            SKILL_OVERRIDE,
            "Use the custom agent named franky if the host exposes it. Return only RUNTIME_PROBE_COMPLETE.",
        ],
        timeout,
    )
    lines = stdout.splitlines()
    completed = any('"type":"turn.completed"' in line for line in lines)
    failed = any('"type":"turn.failed"' in line for line in lines)
    result["live_turn"] = "PASS" if completed else ("BLOCKED" if failed else "NOT_ASSESSED")
    if stderr.strip():
        result["live_stderr_tail"] = stderr.strip().splitlines()[-1]
    if completed and any("franky" in line.lower() and "agent" in line.lower() for line in lines):
        result["skills_config_behavior"] = "NOT_ASSESSED"
        result["skills_config_limitation"] = "A child-agent trace was visible but did not prove enable/disable semantics."
    else:
        result["skills_config_limitation"] = "No completed observable child-agent/skill-selection trace was available."
    result["live_exit_code"] = code
    result["runtime_evidence"] = {
        "configuration": {"status": result["config_parse"], "evidence": result["config_parse_evidence"] or "No parser evidence."},
        "dispatch": {"status": result["actual_dispatch"], "evidence": result["actual_dispatch_limitation"]},
        "skill_loading": {"status": result["skills_config_behavior"], "evidence": result["skills_config_limitation"]},
        "mutation": {"status": result["mutation_escalation"], "evidence": result["mutation_escalation_limitation"]},
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", default=DEFAULT_CODEX)
    parser.add_argument("--live", action="store_true", help="Attempt one model turn; network failures remain evidence, not success.")
    parser.add_argument("--timeout", type=int, default=35)
    args = parser.parse_args()
    print(json.dumps(probe(args.codex, args.live, args.timeout), sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
