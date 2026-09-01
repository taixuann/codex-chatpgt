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
REPERTOIRE = ROOT / "manifests/agent-repertoires.yaml"
SKILL_CATALOG = ROOT / "manifests/skill-catalog.yaml"
ADAPTER_GUIDANCE = ROOT / "agents/AGENTS.md"
BOUNDARY_DOC = ROOT / "documentation/architecture/agents.md"
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
FEYNMAN_SECTIONS = {
    "INVOCATION CLASSES",
    "SOURCE ROUTING",
    "EVIDENCE SEMANTICS",
    "SCIENTIFIC ABSTENTION",
}


SUPPORT_PROHIBITIONS = {
    "argus": (
        "Do not modify files.",
        "Do not modify canonical project state.",
        "Do not modify global skills, agent contracts, or workflow policies",
    ),
    "athena": (
        "Do not modify files",
        "Do not modify implementation",
        "Do not change canonical state",
        "Do not modify global skills, agent contracts, or workflow policies",
    ),
}


def _validate_adapter(name: str, data: dict, instructions: str) -> None:
    if data.get("name") != name:
        raise ValueError(f"adapter {name}: name must match canonical id")
    if name in SUPPORT:
        if data.get("sandbox_mode") != "read-only":
            raise ValueError(f"adapter {name}: support adapters must use sandbox_mode=read-only")
        missing = [phrase for phrase in SUPPORT_PROHIBITIONS[name] if phrase.lower() not in instructions.lower()]
        if missing:
            raise ValueError(f"adapter {name}: missing read-only prohibition(s): {', '.join(missing)}")


def _read_adapter(name: str) -> str:
    path = ADAPTERS / f"{name}.toml"
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    instructions = data.get("developer_instructions")
    if not isinstance(instructions, str) or not instructions.strip():
        raise ValueError(f"adapter {name}: developer_instructions is required")
    _validate_adapter(name, data, instructions)
    return instructions


def _validate_authority_metadata() -> None:
    document = yaml.safe_load(REPERTOIRE.read_text(encoding="utf-8"))
    authority = document.get("authority") or {}
    expected = {
        "canonical_role_registry": "external_ai_labs_deployment_registry",
        "canonical_role_definitions": "external_ai_labs_deployment_definitions",
        "portable_role_reference": "agents/AGENTS.md and documentation/architecture/agents.md",
        "local_runtime_registry_path": "/Users/tai/ai-labs/ops/agents/agents.yaml",
        "repository_runtime_policy": "AGENTS.md",
        "repository_adapters": "agents/*.toml",
        "explanatory_documentation": "documentation/",
    }
    for key, value in expected.items():
        observed = authority.get(key)
        # Keep the old root path valid while compatibility pointers remain in
        # place; new metadata should use the subject-organized architecture
        # path. This avoids forcing an unrelated dirty manifest change.
        if key == "portable_role_reference":
            accepted = {value, "agents/AGENTS.md and documentation/AGENT-BOUNDARIES.md"}
            if observed not in accepted:
                raise ValueError(f"repertoire.authority.{key}: authority chain mismatch")
        elif observed != value:
            raise ValueError(f"repertoire.authority.{key}: authority chain mismatch")
    if authority.get("precedence") != [
        "external_deployment_registry_when_available",
        "portable_repository_role_reference",
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
    required_feynman_capabilities = {
        "scientific-reasoning",
        "evidence-synthesis",
        "methodology-critique",
        "hypothesis-gap-analysis",
    }
    if not required_feynman_capabilities.issubset(set(agents["feynman"].get("primary_capabilities", []))):
        raise ValueError("repertoire.feynman: missing scientific v1 capability boundary")


def _validate_skill_admission_alignment(document: dict, catalog: dict) -> None:
    dispositions = catalog.get("dispositions") or {}
    owners = {name: disposition for disposition, names in dispositions.items() for name in names}
    athena = (document.get("agents") or {}).get("athena") or {}
    for capability in athena.get("primary_capabilities", []):
        if capability in owners and owners[capability] != "KEEP":
            raise ValueError(
                f"repertoire.athena: noncanonical skill {capability} cannot be a primary capability; "
                "keep it conditional until catalog admission is KEEP"
            )


def validate() -> None:
    if {path.stem for path in ADAPTERS.glob("*.toml")} != CANONICAL | SUPPORT:
        raise ValueError("agents: adapter set must be exactly canonical roles plus Argus/Athena support")
    for name in sorted(CANONICAL):
        instructions = _read_adapter(name)
        required_sections = REQUIRED_SECTIONS | (FEYNMAN_SECTIONS if name == "feynman" else set())
        missing = [section for section in required_sections if section not in instructions]
        if missing:
            raise ValueError(f"adapter {name}: missing contract section(s): {', '.join(sorted(missing))}")
    for name in sorted(SUPPORT):
        _read_adapter(name)
    guidance = ADAPTER_GUIDANCE.read_text(encoding="utf-8")
    for phrase in ("Authority precedence and update procedure", "portable semantic reference", "support adapters"):
        if phrase.lower() not in guidance.lower():
            raise ValueError(f"agents/AGENTS.md: missing authority phrase {phrase!r}")
    doc = BOUNDARY_DOC.read_text(encoding="utf-8")
    for phrase in ("When to call each role", "Do not call for", "NOT_ASSESSED", "native skill loading", "host permission enforcement"):
        if phrase.lower() not in doc.lower():
            raise ValueError(f"AGENT-BOUNDARIES.md: missing boundary phrase {phrase!r}")
    _validate_authority_metadata()
    repertoire = yaml.safe_load(REPERTOIRE.read_text(encoding="utf-8")) or {}
    catalog = yaml.safe_load(SKILL_CATALOG.read_text(encoding="utf-8")) or {}
    _validate_skill_admission_alignment(repertoire, catalog)


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
