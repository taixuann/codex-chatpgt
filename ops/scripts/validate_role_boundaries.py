#!/usr/bin/env python3
"""Validate canonical-role adapter boundaries without creating a router."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tomllib

import yaml


ROOT = Path(__file__).resolve().parents[2]
ADAPTERS = ROOT / "agents"
REPERTOIRE = ROOT / "manifests/agent-capability-repertoires.yaml"
ADAPTER_GUIDANCE = ROOT / "agents/AGENTS.md"
BOUNDARY_DOC = ROOT / "documentation/AGENT-BOUNDARIES.md"
CANONICAL = {"feynman", "prometheus", "franky"}
SUPPORT = {"argus", "athena"}
REQUIRED_SECTIONS = {
    "PURPOSE",
    "ALLOWED RESPONSIBILITIES",
    "FORBIDDEN RESPONSIBILITIES",
    "INPUT EXPECTATIONS",
    "OUTPUT EXPECTATIONS",
    "DELEGATION BOUNDARIES",
    "HUMAN ESCALATION",
}


def _read_adapter(name: str) -> str:
    path = ADAPTERS / f"{name}.toml"
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    if data.get("name") != name:
        raise ValueError(f"adapter {name}: name must match canonical id")
    instructions = data.get("developer_instructions")
    if not isinstance(instructions, str) or not instructions.strip():
        raise ValueError(f"adapter {name}: developer_instructions is required")
    return instructions


def _validate_authority_metadata() -> None:
    document = yaml.safe_load(REPERTOIRE.read_text(encoding="utf-8"))
    authority = document.get("authority") or {}
    expected = {
        "canonical_role_registry": "/Users/tai/ai-labs/ops/agents/agents.yaml",
        "canonical_role_definitions": "/Users/tai/ai-labs/ops/agents/{role}.md",
        "repository_runtime_policy": "AGENTS.md",
        "repository_adapters": "agents/*.toml",
        "explanatory_documentation": "documentation/",
    }
    for key, value in expected.items():
        if authority.get(key) != value:
            raise ValueError(f"repertoire.authority.{key}: authority chain mismatch")
    if authority.get("precedence") != [
        "canonical_role_registry_and_definitions",
        "repository_adapters",
        "repository_runtime_policy",
        "explanatory_documentation",
    ]:
        raise ValueError("repertoire.authority.precedence: unexpected order")
    agents = document.get("agents") or {}
    if {name for name, value in agents.items() if value.get("role_surface") == "canonical"} != CANONICAL:
        raise ValueError("repertoire: canonical role surface must be exactly Feynman, Prometheus, and Franky")
    if {name for name, value in agents.items() if value.get("role_surface") == "support"} != SUPPORT:
        raise ValueError("repertoire: support role surface must be exactly Argus and Athena")


def validate() -> None:
    if {path.stem for path in ADAPTERS.glob("*.toml")} != CANONICAL | SUPPORT:
        raise ValueError("agents: adapter set must be exactly canonical roles plus Argus/Athena support")
    for name in sorted(CANONICAL):
        instructions = _read_adapter(name)
        missing = [section for section in REQUIRED_SECTIONS if section not in instructions]
        if missing:
            raise ValueError(f"adapter {name}: missing contract section(s): {', '.join(sorted(missing))}")
    for name in sorted(SUPPORT):
        _read_adapter(name)
    guidance = ADAPTER_GUIDANCE.read_text(encoding="utf-8")
    for phrase in ("Authority precedence and update procedure", "source of truth", "support adapters"):
        if phrase.lower() not in guidance.lower():
            raise ValueError(f"agents/AGENTS.md: missing authority phrase {phrase!r}")
    doc = BOUNDARY_DOC.read_text(encoding="utf-8")
    for phrase in ("When to call each role", "Do not call for", "NOT_ASSESSED", "native skill loading", "host permission enforcement"):
        if phrase.lower() not in doc.lower():
            raise ValueError(f"AGENT-BOUNDARIES.md: missing boundary phrase {phrase!r}")
    _validate_authority_metadata()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        validate()
    except (OSError, TypeError, ValueError, tomllib.TOMLDecodeError, yaml.YAMLError) as exc:
        print(f"FAIL role-boundaries: {exc}")
        return 1
    print("OK role-boundaries: canonical authority, adapters, and call boundaries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
