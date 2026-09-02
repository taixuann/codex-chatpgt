#!/usr/bin/env python3
"""Small deterministic helper for the intent run-state contract.

This command observes and validates state; it does not interpret intent or
mutate Issues, plans, tasks, or repository source.  ``--write`` is required
for derived staleness/recovery updates.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[3]
MATRIX_PATH = ROOT / "skills/intent/references/requirement-matrix.yaml"
REFERENCE_POLICY_PATH = ROOT / "skills/intent/references/reference-selection.yaml"
STAGE_STATUSES = {"passed", "skipped_with_reason", "not_applicable", "blocked", "failed"}
REQUIREMENTS = {"required", "optional", "conditional", "not_applicable"}
CLAIM_STATES = {"CONFIRMED", "INFERRED", "UNKNOWN", "USER_DECISION", "PROPOSED"}
TRUST_VALUES = {
    "freshness": {"fresh", "stale_soft", "stale_review_required", "stale_hard"},
    "completeness": {"complete", "partial"},
    "integrity": {"valid", "invalid"},
    "scope_match": {"exact", "related", "mismatch"},
    "evidence_traceability": {"complete", "partial"},
}
_SOURCE_SPEC = importlib.util.spec_from_file_location("intent_source_contract", Path(__file__).with_name("source_contract.py"))
if _SOURCE_SPEC is None or _SOURCE_SPEC.loader is None:  # pragma: no cover - package corruption
    raise ImportError("cannot load source contract")
_SOURCE = importlib.util.module_from_spec(_SOURCE_SPEC)
_SOURCE_SPEC.loader.exec_module(_SOURCE)


class IntentError(ValueError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(cwd), *args], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise IntentError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def dirty_fingerprint(cwd: Path) -> str:
    """Hash a bounded, normalized porcelain snapshot for freshness checks."""
    import hashlib

    snapshot = run_git(cwd, "status", "--porcelain=v1", "--untracked-files=all")
    return hashlib.sha256(snapshot.encode("utf-8")).hexdigest()


def workspace_report(cwd: Path | None = None) -> dict[str, Any]:
    active = (cwd or Path.cwd()).expanduser().resolve()
    report: dict[str, Any] = {
        "cwd": str(active),
        "repo_root": None,
        "head": "uncommitted",
        "branch": "none",
        "dirty": False,
        "dirty_fingerprint": "unbound",
        "instruction_chain": [],
    }
    try:
        root = Path(run_git(active, "rev-parse", "--show-toplevel")).resolve()
        report["repo_root"] = str(root)
        report["head"] = run_git(active, "rev-parse", "HEAD")
        try:
            report["branch"] = run_git(active, "symbolic-ref", "--quiet", "--short", "HEAD")
        except IntentError:
            report["branch"] = "(detached)"
        report["dirty"] = bool(run_git(active, "status", "--porcelain"))
        report["dirty_fingerprint"] = dirty_fingerprint(active)
        if active == root or root in active.parents:
            chain: list[str] = []
            current = root
            while True:
                candidate = current / "AGENTS.md"
                if candidate.is_file():
                    chain.append(candidate.relative_to(root).as_posix())
                if current == active:
                    break
                try:
                    current = current / active.relative_to(current).parts[0]
                except ValueError:
                    break
            report["instruction_chain"] = chain
    except IntentError:
        report["instruction_chain"] = ["(no Git project anchor)"]
    return report


def load_matrix() -> dict[str, Any]:
    try:
        data = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise IntentError(f"cannot load requirement matrix: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise IntentError("requirement matrix must declare schema_version: 1")
    profiles = data.get("profiles")
    stages = data.get("stages")
    if not isinstance(profiles, dict) or not isinstance(stages, list) or not stages:
        raise IntentError("requirement matrix profiles and stages are required")
    for profile, requirements in profiles.items():
        if not isinstance(requirements, dict) or set(requirements) != set(stages):
            raise IntentError(f"matrix profile {profile} must cover every stage")
        if any(value not in REQUIREMENTS for value in requirements.values()):
            raise IntentError(f"matrix profile {profile} contains an invalid requirement")
    return data


def load_reference_policy() -> dict[str, Any]:
    try:
        data = yaml.safe_load(REFERENCE_POLICY_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise IntentError(f"cannot load reference-selection policy: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise IntentError("reference-selection policy must declare schema_version: 1")
    profiles = data.get("profiles")
    references = data.get("references")
    if not isinstance(profiles, dict) or set(profiles) != {
        "issue_light", "issue_focused", "issue_deep", "idea_light", "idea_focused", "idea_deep"
    }:
        raise IntentError("reference-selection policy must cover all six origin/depth profiles")
    if not isinstance(references, dict) or not references:
        raise IntentError("reference-selection policy references are required")
    for profile, names in profiles.items():
        if not isinstance(names, list) or any(name not in references for name in names):
            raise IntentError(f"reference-selection profile {profile} contains an unknown reference")
    stages = data.get("stage_procedures")
    if not isinstance(stages, dict) or not stages:
        raise IntentError("reference-selection stage_procedures are required")
    for stage, names in stages.items():
        if not isinstance(names, list) or not names or any(name not in references for name in names):
            raise IntentError(f"reference-selection stage {stage} must name existing procedures")
    for name in references:
        if not (REFERENCE_POLICY_PATH.parent / name).is_file():
            raise IntentError(f"reference-selection policy points to missing reference: {name}")
        metadata = references[name]
        if not isinstance(metadata, dict) or metadata.get("class") not in {"procedural", "output_contract", "matrix", "schema_reference"}:
            raise IntentError(f"reference-selection metadata class is invalid: {name}")
        if not isinstance(metadata.get("required_observables"), list):
            raise IntentError(f"reference-selection required_observables must be a list: {name}")
    return data


def expected_references(run: dict[str, Any]) -> dict[str, list[str]]:
    """Derive selected procedures from policy and observable material conditions."""
    policy = load_reference_policy()
    profile = run["profile"]
    selected = list(policy["profiles"][profile])
    conditions = policy.get("conditional", {})
    for name, rule in conditions.items():
        if name not in policy["references"]:
            raise IntentError(f"conditional policy names unknown reference: {name}")
        profiles = rule.get("profiles", []) if isinstance(rule, dict) else []
        if profile not in profiles:
            continue
        if rule.get("condition") == "material_relationships" and not (
            run.get("relationships") or run.get("stages", {}).get("relationship_audit", {}).get("status") == "passed"
        ):
            continue
        if name not in selected:
            selected.append(name)
    return {
        stage: [name for name in names if name in selected]
        for stage, names in policy["stage_procedures"].items()
        if any(name in selected for name in names)
    }


def profile_for(origin: str, depth: str) -> str:
    prefix = "issue" if origin == "github_issue" else "idea"
    return f"{prefix}_{depth}"


def _stage(status: str, reason: str | None = None) -> dict[str, Any]:
    value: dict[str, Any] = {"status": status, "evidence": []}
    if reason:
        value["reason"] = reason
    return value


def init_run(origin: str, locator: str, depth: str, cwd: Path) -> dict[str, Any]:
    matrix = load_matrix()
    profile = profile_for(origin, depth)
    requirements = matrix["profiles"].get(profile)
    if requirements is None:
        raise IntentError(f"no requirement profile for {origin}/{depth}")
    workspace = workspace_report(cwd)
    stages = {}
    for name, requirement in requirements.items():
        if requirement == "required":
            stages[name] = _stage("blocked", "pending execution")
        elif requirement == "not_applicable":
            stages[name] = _stage("not_applicable", "not applicable for this origin/depth")
        else:
            stages[name] = _stage("not_applicable", "not selected at initialization")
    return {
        "intent_run": {
            "schema_version": 1,
            "origin": {"type": origin, "locator": locator, "observed_at": now()},
            "workspace": workspace,
            "depth": depth,
            "profile": profile,
            "stages": stages,
            "evidence": [],
            "claims": [],
            "decisions": [],
            "relationships": [],
            "unknowns": [],
            "contradictions": [],
            "blockers": [],
            "procedure_trace": {
                "expected": expected_references({"profile": profile, "relationships": [], "stages": stages}),
                "observed": {},
            },
            "intent": {
                "objective": "",
                "why": "",
                "current_state": "",
                "target_state": "",
                "success_criteria": [],
                "scope": [],
                "out_of_scope": [],
            },
            "orientation": None,
            "handoff": {
                "packet": None,
                "recovery": None,
            },
            "trust": {
                "freshness": "fresh",
                "completeness": "partial",
                "integrity": "valid",
                "scope_match": "exact",
                "evidence_traceability": "partial",
            },
        }
    }


def _require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise IntentError(f"{field} must be a mapping")
    return value


def validate_run(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict) or set(data) != {"intent_run"}:
        return ["document must contain only an intent_run mapping"]
    run = _require_mapping(data["intent_run"], "intent_run")
    if run.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    origin = _require_mapping(run.get("origin"), "origin") if isinstance(run.get("origin"), dict) else {}
    origin_type = origin.get("type")
    locator = origin.get("locator")
    if origin_type not in {"github_issue", "user_idea"}:
        errors.append("origin.type must be github_issue or user_idea")
    if not isinstance(locator, str) or not locator.strip():
        errors.append("origin.locator is required")
    elif not _SOURCE.valid_locator("user" if origin_type == "user_idea" else "github_issue", locator):
        errors.append(_SOURCE.locator_error("user" if origin_type == "user_idea" else "github_issue"))
    if not isinstance(origin.get("observed_at"), str) or not origin.get("observed_at"):
        errors.append("origin.observed_at is required")
    depth = run.get("depth")
    if depth not in {"light", "focused", "deep"}:
        errors.append("depth must be light, focused, or deep")
    matrix = load_matrix()
    profile = profile_for(origin_type, depth) if origin_type in {"github_issue", "user_idea"} and depth in {"light", "focused", "deep"} else None
    if profile and run.get("profile") != profile:
        errors.append(f"profile must be {profile}")

    workspace = run.get("workspace")
    if not isinstance(workspace, dict):
        errors.append("workspace must be a mapping")
    else:
        if not isinstance(workspace.get("cwd"), str) or not workspace.get("cwd"):
            errors.append("workspace.cwd is required")
        if workspace.get("repo_root") is not None and (not isinstance(workspace.get("repo_root"), str) or not workspace.get("repo_root")):
            errors.append("workspace.repo_root must be a path or null")
        for field in ("head", "branch"):
            if not isinstance(workspace.get(field), str) or not workspace.get(field):
                errors.append(f"workspace.{field} is required")
        if not isinstance(workspace.get("dirty"), bool):
            errors.append("workspace.dirty must be boolean")
        if not isinstance(workspace.get("dirty_fingerprint"), str) or not workspace.get("dirty_fingerprint"):
            errors.append("workspace.dirty_fingerprint is required")
        if not isinstance(workspace.get("instruction_chain"), list):
            errors.append("workspace.instruction_chain must be a list")

    requirements = matrix["profiles"].get(profile, {}) if profile else {}
    stages = run.get("stages")
    if not isinstance(stages, dict):
        errors.append("stages must be a mapping")
        stages = {}
    if set(stages) != set(requirements):
        errors.append("stages must exactly match the selected requirement profile")
    for name in requirements:
        stage = stages.get(name)
        if not isinstance(stage, dict):
            errors.append(f"stage {name} must be a mapping")
            continue
        status = stage.get("status")
        if status not in STAGE_STATUSES:
            errors.append(f"stage {name} has invalid status")
        if status in {"blocked", "failed", "skipped_with_reason", "not_applicable"} and not str(stage.get("reason", "")).strip():
            errors.append(f"stage {name} requires a reason for status {status}")
        if not isinstance(stage.get("evidence", []), list):
            errors.append(f"stage {name}.evidence must be a list")

    evidence = run.get("evidence", [])
    evidence_ids: set[str] = set()
    if not isinstance(evidence, list):
        errors.append("evidence must be a list")
        evidence = []
    for index, item in enumerate(evidence):
        if not isinstance(item, dict):
            errors.append(f"evidence[{index}] must be a mapping")
            continue
        ident = item.get("id")
        if not isinstance(ident, str) or not ident.strip() or ident in evidence_ids:
            errors.append(f"evidence[{index}].id must be unique and non-empty")
        else:
            evidence_ids.add(ident)
        for field in ("locator", "kind", "observed_at"):
            if not isinstance(item.get(field), str) or not item.get(field).strip():
                errors.append(f"evidence[{index}].{field} is required")
        observables = item.get("observables", [])
        if not isinstance(observables, list) or any(not isinstance(value, str) or not value.strip() for value in observables):
            errors.append(f"evidence[{index}].observables must be a list of strings")
    if isinstance(stages, dict):
        for stage, record in stages.items():
            refs = record.get("evidence", []) if isinstance(record, dict) else []
            if isinstance(refs, list) and any(ref not in evidence_ids for ref in refs):
                errors.append(f"stage {stage}.evidence contains a dangling reference")

    claims = run.get("claims", [])
    if not isinstance(claims, list):
        errors.append("claims must be a list")
        claims = []
    claim_ids: set[str] = set()
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f"claims[{index}] must be a mapping")
            continue
        ident = claim.get("id")
        if not isinstance(ident, str) or not ident.strip() or ident in claim_ids:
            errors.append(f"claims[{index}].id must be unique and non-empty")
        else:
            claim_ids.add(ident)
        if not isinstance(claim.get("text"), str) or not claim.get("text").strip():
            errors.append(f"claims[{index}].text is required")
        state = claim.get("state")
        if state not in CLAIM_STATES:
            errors.append(f"claims[{index}].state is invalid")
        refs = claim.get("evidence", [])
        if not isinstance(refs, list) or any(ref not in evidence_ids for ref in refs):
            errors.append(f"claims[{index}].evidence contains a dangling reference")
        if state == "CONFIRMED" and not refs:
            errors.append(f"claims[{index}] confirmed claims require evidence")

    for field in ("relationships", "unknowns", "blockers", "contradictions"):
        if not isinstance(run.get(field, []), list):
            errors.append(f"{field} must be a list")
    trace = run.get("procedure_trace")
    if not isinstance(trace, dict) or set(trace) != {"expected", "observed"}:
        errors.append("procedure_trace must be a mapping")
    else:
        expected = trace.get("expected")
        observed = trace.get("observed")
        for key, mapping in (("expected", expected), ("observed", observed)):
            if not isinstance(mapping, dict):
                errors.append(f"procedure_trace.{key} must be a stage mapping")
                continue
            for stage, refs in mapping.items():
                if not isinstance(refs, list) or any(not isinstance(ref, str) or not ref.strip() for ref in refs):
                    errors.append(f"procedure_trace.{key}.{stage} must be a list of references")
                for ref in refs if isinstance(refs, list) else []:
                    if not (ROOT / "skills/intent/references" / ref).is_file():
                        errors.append(f"procedure_trace.{key}.{stage} reference does not resolve: {ref}")
        if isinstance(expected, dict):
            try:
                derived = expected_references(run)
                if expected != derived:
                    errors.append("procedure_trace.expected does not match reference-selection policy")
            except IntentError as exc:
                errors.append(str(exc))
        if isinstance(expected, dict) and isinstance(observed, dict):
            for stage, refs in observed.items():
                if stage not in expected or not set(refs).issubset(set(expected[stage])):
                    errors.append("procedure_trace.observed contains an unnecessary reference")
    decisions = run.get("decisions", [])
    if not isinstance(decisions, list):
        errors.append("decisions must be a list")
    else:
        for index, decision in enumerate(decisions):
            if not isinstance(decision, dict) or not isinstance(decision.get("status"), str):
                errors.append(f"decisions[{index}] must declare a status")

    intent = run.get("intent")
    if not isinstance(intent, dict):
        errors.append("intent must be a mapping")
    else:
        for field in ("objective", "why", "current_state", "target_state"):
            if not isinstance(intent.get(field), str):
                errors.append(f"intent.{field} must be a string")
        for field in ("success_criteria", "scope", "out_of_scope"):
            value = intent.get(field)
            if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
                errors.append(f"intent.{field} must be a list of strings")

    handoff = run.get("handoff")
    if not isinstance(handoff, dict):
        errors.append("handoff must be a mapping")
    else:
        if handoff.get("packet") is not None and not isinstance(handoff.get("packet"), str):
            errors.append("handoff.packet must be a path or null")
        recovery = handoff.get("recovery")
        if recovery is not None and not isinstance(recovery, dict):
            errors.append("handoff.recovery must be a mapping or null")

    trust = run.get("trust")
    if not isinstance(trust, dict):
        errors.append("trust must be a mapping")
    else:
        for field, allowed in TRUST_VALUES.items():
            if trust.get(field) not in allowed:
                errors.append(f"trust.{field} is invalid")
    return errors


def load_run(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise IntentError(f"cannot read run state: {exc}") from exc
    if not isinstance(data, dict):
        raise IntentError("run state must be a YAML mapping")
    return data


def save_run(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def readiness(data: dict[str, Any]) -> list[str]:
    errors = validate_run(data)
    if errors:
        return errors
    run = data["intent_run"]
    requirements = load_matrix()["profiles"][run["profile"]]
    trace = run["procedure_trace"]
    expected = trace["expected"]
    observed = trace["observed"]
    policy = load_reference_policy()
    evidence_by_id = {item.get("id"): item for item in run.get("evidence", []) if isinstance(item, dict)}
    for stage, refs in expected.items():
        if requirements.get(stage) == "required":
            if not set(refs).issubset(set(observed.get(stage, []))):
                errors.append(f"required procedure references not observed: {stage}")
            stage_record = run["stages"].get(stage, {})
            stage_evidence = stage_record.get("evidence", []) if isinstance(stage_record, dict) else []
            if not stage_evidence:
                errors.append(f"required stage lacks observable evidence: {stage}")
            elif not any(evidence_by_id.get(evidence_id, {}).get("procedure") == stage for evidence_id in stage_evidence):
                errors.append(f"required stage evidence is not procedure-bound: {stage}")
            else:
                observable_ids = {
                    observable
                    for evidence_id in stage_evidence
                    for observable in evidence_by_id.get(evidence_id, {}).get("observables", [])
                }
                for ref in refs:
                    required_observables = policy["references"].get(ref, {}).get("required_observables", [])
                    missing_observables = set(required_observables) - observable_ids
                    if missing_observables:
                        errors.append(
                            f"procedure observable proof missing: {stage}/{ref}: {sorted(missing_observables)}"
                        )
    for name, requirement in requirements.items():
        status = run["stages"][name]["status"]
        if requirement == "required" and status != "passed":
            errors.append(f"missing required stage: {name}")
        if requirement in {"conditional", "optional"} and status in {"blocked", "failed"}:
            errors.append(f"stage {name} is {status}")
    for decision in run.get("decisions", []):
        if decision.get("status") in {"open", "blocked", "unresolved"}:
            errors.append("unresolved authority decision remains")
    if run.get("contradictions"):
        errors.append("unresolved contradictions remain")
    intent = run["intent"]
    for field in ("objective", "why"):
        if not intent[field].strip():
            errors.append(f"G5 boundary field missing: intent.{field}")
    for field in ("success_criteria", "scope", "out_of_scope"):
        if not intent[field]:
            errors.append(f"G5 boundary field missing: intent.{field}")
    handoff = run["handoff"]
    if requirements.get("session_handoff") == "required":
        packet = handoff.get("packet")
        packet_path = _resolve_packet_path(run, packet)
        if packet_path is None or not packet_path.exists():
            errors.append("required session handoff packet is missing")
        elif not _packet_is_anchored(run, packet_path):
            errors.append("required session handoff packet is outside anchored repository")
        elif not _session_packet_valid(packet_path, run["workspace"].get("repo_root")):
            errors.append("required session handoff packet failed shared validation")
    if requirements.get("fresh_context_eval") == "required":
        recovery = handoff.get("recovery") or {}
        try:
            derived_recovery = fresh_context(data)
        except IntentError as exc:
            errors.append(f"fresh-context evaluation is invalid: {exc}")
        else:
            if recovery.get("status") != "passed" or derived_recovery.get("status") != "passed":
                errors.append("fresh-context evaluation has not passed")
    trust = run["trust"]
    if trust["freshness"] in {"stale_review_required", "stale_hard"}:
        errors.append(f"freshness requires review: {trust['freshness']}")
    if trust["completeness"] != "complete":
        errors.append("trust completeness is not complete")
    if trust["integrity"] != "valid":
        errors.append("trust integrity is not valid")
    if trust["scope_match"] != "exact":
        errors.append("trust scope_match is not exact")
    if trust["evidence_traceability"] != "complete":
        errors.append("evidence traceability is incomplete")
    if run.get("blockers"):
        errors.extend(f"blocker: {item}" for item in run["blockers"])
    return errors


def _session_packet_valid(packet: Path, expected_repo_root: str | None = None) -> bool:
    """Reuse the shared packet validator without copying its contract."""
    validator = ROOT / "skills/control-plane/session-packet-management/scripts/validate_session_packet.py"
    if not validator.is_file():
        return False
    if expected_repo_root:
        try:
            session = yaml.safe_load((packet / "session.yaml").read_text(encoding="utf-8"))
            declared = session.get("repository_root") if isinstance(session, dict) else None
            declared_root = Path(declared).expanduser().resolve() if isinstance(declared, str) and declared != "." else Path(run_git(packet, "rev-parse", "--show-toplevel")).resolve()
            if declared_root != Path(expected_repo_root).expanduser().resolve():
                return False
        except (OSError, IntentError, yaml.YAMLError):
            return False
    result = subprocess.run(
        [sys.executable, str(validator), str(packet)],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def _resolve_packet_path(run: dict[str, Any], packet: Any) -> Path | None:
    if not isinstance(packet, str) or not packet.strip():
        return None
    path = Path(packet).expanduser()
    if path.is_absolute():
        return path
    repo_root = run.get("workspace", {}).get("repo_root") if isinstance(run.get("workspace"), dict) else None
    if not isinstance(repo_root, str) or not repo_root:
        return None
    return (Path(repo_root) / path).resolve()


def _packet_is_anchored(run: dict[str, Any], packet_path: Path | None) -> bool:
    """Require live packets to belong to the run's anchored repository."""
    if packet_path is None:
        return False
    repo_root = run.get("workspace", {}).get("repo_root") if isinstance(run.get("workspace"), dict) else None
    if not isinstance(repo_root, str) or not repo_root:
        return False
    live_root = (Path(repo_root).expanduser().resolve() / ".agents" / "sessions").resolve()
    try:
        relative = packet_path.resolve().relative_to(live_root)
    except ValueError:
        return False
    return len(relative.parts) == 1


def _frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise IntentError(f"intent artifact is missing frontmatter: {path}")
    try:
        _, header, body = text.split("---\n", 2)
        metadata = yaml.safe_load(header)
    except (ValueError, yaml.YAMLError) as exc:
        raise IntentError(f"invalid intent artifact frontmatter: {exc}") from exc
    if not isinstance(metadata, dict):
        raise IntentError("intent artifact frontmatter must be a mapping")
    return metadata, body


def _canonical_packet_intent(run: dict[str, Any]) -> dict[str, Any]:
    intent = run["intent"]
    return {
        "origin": run["origin"],
        "objective": intent["objective"],
        "why": intent["why"],
        "current_state": intent["current_state"],
        "target_state": intent["target_state"],
        "success_criteria": list(intent["success_criteria"]),
        "scope": list(intent["scope"]),
        "out_of_scope": list(intent["out_of_scope"]),
        "decisions": list(run.get("decisions", [])),
        "unknowns": list(run.get("unknowns", [])),
        "relationships": list(run.get("relationships", [])),
        "evidence": list(run.get("evidence", [])),
        "orientation": run.get("orientation"),
    }


def materialize_intent_artifact(data: dict[str, Any]) -> Path:
    errors = validate_run(data)
    if errors:
        raise IntentError("invalid run state: " + "; ".join(errors))
    run = data["intent_run"]
    packet_path = _resolve_packet_path(run, run.get("handoff", {}).get("packet"))
    if packet_path is None or not packet_path.is_dir() or not _packet_is_anchored(run, packet_path):
        raise IntentError("cannot materialize intent artifact outside the anchored live session packet")
    path = packet_path / "intent.md"
    metadata, _ = _frontmatter(path)
    metadata["intent"] = _canonical_packet_intent(run)
    metadata["status"] = "observed"
    body = f"""\n# Intent\n\n## STATUS\nOBSERVED\n\n## ORIGIN\n{run['origin']['type']}: {run['origin']['locator']}\n\n## WHY\n{run['intent']['why']}\n\n## OBJECTIVE\n{run['intent']['objective']}\n\n## CURRENT STATE\n{run['intent']['current_state']}\n\n## TARGET STATE\n{run['intent']['target_state']}\n\n## SCOPE\n""" + "\n".join(f"- {item}" for item in run["intent"]["scope"]) + "\n\n## OUT OF SCOPE\n" + "\n".join(f"- {item}" for item in run["intent"]["out_of_scope"]) + "\n\n## SUCCESS CRITERIA\n" + "\n".join(f"- {item}" for item in run["intent"]["success_criteria"]) + "\n\n## EVIDENCE STATE\nCanonical machine-readable intent is stored in frontmatter under `intent`; evidence pointers remain bounded in the run state.\n\n## READINESS\nINTENT_READY_RECOMMENDATION\n"
    path.write_text("---\n" + yaml.safe_dump(metadata, sort_keys=False).rstrip() + "\n---\n" + body, encoding="utf-8")
    return path


def _packet_canonical_intent(run: dict[str, Any]) -> dict[str, Any] | None:
    packet_path = _resolve_packet_path(run, run.get("handoff", {}).get("packet"))
    if packet_path is None or not packet_path.is_dir() or not (packet_path / "intent.md").is_file():
        return None
    metadata, _ = _frontmatter(packet_path / "intent.md")
    value = metadata.get("intent")
    return value if isinstance(value, dict) else None


def staleness(data: dict[str, Any], cwd: Path) -> dict[str, Any]:
    errors = validate_run(data)
    if errors:
        raise IntentError("invalid run state: " + "; ".join(errors))
    run = data["intent_run"]
    observed = run["workspace"]
    current = workspace_report(cwd)
    if current.get("repo_root") != observed.get("repo_root"):
        freshness = "stale_hard"
    elif current.get("head") != observed.get("head"):
        freshness = "stale_review_required"
    elif current.get("branch") != observed.get("branch") or current.get("dirty_fingerprint") != observed.get("dirty_fingerprint"):
        freshness = "stale_soft"
    else:
        freshness = "fresh"
    return {"freshness": freshness, "observed": observed, "current": current}


RECOVERY_FIELDS = (
    "objective", "why", "scope", "out_of_scope", "success", "current_state",
    "surfaces", "relationships", "decisions", "unknowns", "evidence_traceability",
)


def fresh_context(data: dict[str, Any]) -> dict[str, Any]:
    errors = validate_run(data)
    if errors:
        raise IntentError("invalid run state: " + "; ".join(errors))
    run = data["intent_run"]
    intent = run["intent"]
    workspace = run["workspace"]
    fields = {
        "objective": bool(intent["objective"].strip()),
        "why": bool(intent["why"].strip()),
        "scope": bool(intent["scope"]),
        "out_of_scope": bool(intent["out_of_scope"]),
        "success": bool(intent["success_criteria"]),
        "current_state": bool(intent["current_state"].strip() and workspace.get("cwd") and workspace.get("head")),
        "surfaces": bool(run.get("evidence")),
        "relationships": isinstance(run.get("relationships"), list),
        "decisions": isinstance(run.get("decisions"), list),
        "unknowns": isinstance(run.get("unknowns"), list),
        "evidence_traceability": run["trust"]["evidence_traceability"] == "complete",
    }
    score = sum(1 for field in RECOVERY_FIELDS if fields.get(field) is True)
    missing = [field for field in RECOVERY_FIELDS if fields.get(field) is not True]
    recovery = (run.get("handoff") or {}).get("recovery") or {}
    burden = len(missing)
    unsupported = 0
    packet = (run.get("handoff") or {}).get("packet")
    profile = run.get("profile", "")
    packet_path = _resolve_packet_path(run, packet)
    if profile.endswith(("_focused", "_deep")) and (packet_path is None or not packet_path.exists()):
        missing.append("session_packet")
        burden += 1
    elif profile.endswith(("_focused", "_deep")) and not _packet_is_anchored(run, packet_path):
        missing.append("session_packet_anchor")
        burden += 1
    if profile.endswith(("_focused", "_deep")) and packet_path is not None and packet_path.exists():
        canonical = _packet_canonical_intent(run)
        expected = _canonical_packet_intent(run)
        if canonical is None:
            missing.append("session_intent_artifact")
            burden += 1
        elif canonical != expected:
            missing.append("session_intent_artifact_binding")
            burden += 1
    status = "passed" if score >= 10 and burden == 0 and unsupported == 0 else "blocked"
    return {
        "status": status,
        "context_recovery_score": {"passed": score, "total": len(RECOVERY_FIELDS)},
        "fields": fields,
        "rediscovery_burden": burden,
        "unsupported_reconstruction": unsupported,
        "missing": missing,
    }


def emit(value: Any, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(value, indent=2, sort_keys=False))
    else:
        print(yaml.safe_dump(value, sort_keys=False).rstrip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="intentctl")
    sub = parser.add_subparsers(dest="command", required=True)
    workspace = sub.add_parser("workspace")
    workspace.add_argument("--json", action="store_true", help="emit JSON")
    workspace.add_argument("--cwd", type=Path, default=Path.cwd())
    init = sub.add_parser("init")
    init.add_argument("--json", action="store_true", help="emit JSON")
    init.add_argument("--origin", choices=("github_issue", "user_idea"), required=True)
    init.add_argument("--locator", required=True)
    init.add_argument("--depth", choices=("light", "focused", "deep"), default="light")
    init.add_argument("--cwd", type=Path, default=Path.cwd())
    init.add_argument("--output", type=Path, required=True)
    materialize = sub.add_parser("materialize")
    materialize.add_argument("run", type=Path)
    materialize.add_argument("--json", action="store_true", help="emit JSON")
    for name in ("status", "validate", "staleness", "readiness", "fresh-context"):
        command = sub.add_parser(name)
        command.add_argument("--json", action="store_true", help="emit JSON")
        command.add_argument("run", type=Path)
        if name == "staleness":
            command.add_argument("--cwd", type=Path, default=Path.cwd())
            command.add_argument("--write", action="store_true")
        if name == "fresh-context":
            command.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "workspace":
            emit(workspace_report(args.cwd), args.json)
            return 0
        if args.command == "init":
            if not _SOURCE.valid_locator("user" if args.origin == "user_idea" else "github_issue", args.locator):
                raise IntentError(_SOURCE.locator_error("user" if args.origin == "user_idea" else "github_issue"))
            data = init_run(args.origin, args.locator, args.depth, args.cwd)
            save_run(args.output, data)
            emit({"status": "initialized", "output": str(args.output), "profile": data["intent_run"]["profile"]}, args.json)
            return 0
        data = load_run(args.run)
        if args.command == "materialize":
            path = materialize_intent_artifact(data)
            emit({"status": "materialized", "path": str(path)}, args.json)
            return 0
        if args.command == "validate":
            errors = validate_run(data)
            if errors:
                for error in errors:
                    print(f"FAIL intent run: {error}")
                return 1
            print("OK intent run: schema, origin, matrix, stage, claim, and trust invariants valid")
            return 0
        if args.command == "status":
            run = data.get("intent_run", {})
            requirements = load_matrix().get("profiles", {}).get(run.get("profile"), {})
            emit({"profile": run.get("profile"), "depth": run.get("depth"), "stages": {
                name: {"requiredness": req, "status": run.get("stages", {}).get(name, {}).get("status")}
                for name, req in requirements.items()
            }, "blockers": run.get("blockers", [])}, args.json)
            return 0
        if args.command == "staleness":
            result = staleness(data, args.cwd)
            if args.write:
                data["intent_run"]["trust"]["freshness"] = result["freshness"]
                save_run(args.run, data)
            emit(result, args.json)
            return 0
        if args.command == "fresh-context":
            result = fresh_context(data)
            if args.write:
                handoff = data["intent_run"].setdefault("handoff", {})
                recovery = handoff.get("recovery")
                if not isinstance(recovery, dict):
                    recovery = {}
                    handoff["recovery"] = recovery
                recovery.update(result)
                existing_stage = data["intent_run"]["stages"].get("fresh_context_eval", {})
                fresh_stage = _stage(result["status"], "rubric evaluation")
                if isinstance(existing_stage, dict) and isinstance(existing_stage.get("evidence"), list):
                    fresh_stage["evidence"] = list(existing_stage["evidence"])
                data["intent_run"]["stages"]["fresh_context_eval"] = fresh_stage
                data["intent_run"]["trust"]["completeness"] = "complete" if result["status"] == "passed" else "partial"
                save_run(args.run, data)
            emit(result, args.json)
            return 0 if result["status"] == "passed" else 1
        if args.command == "readiness":
            errors = readiness(data)
            if errors:
                print("INTENT_BLOCKED")
                for error in errors:
                    print(f"- {error}")
                return 1
            print("INTENT_READY")
            print("PLAN_READY_RECOMMENDATION")
            return 0
    except (IntentError, OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL intentctl: {exc}")
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
