#!/usr/bin/env python3
"""Deterministic staged package generator for the Franky workflow factory."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import re
from pathlib import Path
from typing import Any

import yaml


ROOT = Path("/Users/tai/.codex")
SKILLS = ROOT / "skills"
ROLES = Path("/Users/tai/ai-labs/ops/agents/agents.yaml")
FORBIDDEN = {"model", "executor", "provider", "backend"}
REGISTERED_ROLES = {"feynman", "prometheus", "franky"}
ENTRYPOINT_METADATA = {
    "agent_type": "franky",
    "workflow_id": "WF-FRANKY-CANONICAL",
}
QUALITY_VALIDATOR = ROOT / "skills" / "franky-maintenance" / "scripts" / "validate_skill_quality.py"


def slug(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "workflow"


def delegated_entrypoint_metadata() -> dict[str, str]:
    """Return the single delegated Franky entrypoint metadata."""

    return dict(ENTRYPOINT_METADATA)


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    parts = text.split("---\n", 2)
    return yaml.safe_load(parts[1]) or {}


def tokens(value: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", value.lower()) if len(t) > 2}


def inventory_skills() -> list[dict[str, Any]]:
    result = []
    for skill_md in sorted(SKILLS.glob("*/SKILL.md")):
        meta = frontmatter(skill_md)
        name = meta.get("name", skill_md.parent.name)
        description = str(meta.get("description", ""))
        result.append({"name": name, "description": description, "path": str(skill_md.parent)})
    return result


def role_inventory() -> dict[str, dict[str, Any]]:
    data = load_yaml(ROLES) or {}
    return {item["id"]: item for item in data.get("agents", []) if isinstance(item, dict) and item.get("id")}


def best_skill(description: str, requested: str | None, skills: list[dict[str, Any]]) -> tuple[str | None, int]:
    if requested:
        for item in skills:
            if item["name"] == requested:
                return requested, 100
        return None, 0
    wanted = tokens(description)
    scored = [(len(wanted & tokens(item["name"] + " " + item["description"])), item["name"]) for item in skills]
    scored.sort(reverse=True)
    return (scored[0][1], scored[0][0]) if scored and scored[0][0] else (None, 0)


def walk_forbidden(value: Any, path: str = "package") -> list[str]:
    findings = []
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in FORBIDDEN:
                findings.append(f"forbidden key {key!r} at {path}")
            findings.extend(walk_forbidden(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(walk_forbidden(child, f"{path}[{index}]"))
    return findings


def resource_findings(skill_path: Path, resources: list[str], owner: str) -> list[dict[str, Any]]:
    findings = []
    for resource in resources:
        if not (skill_path / resource).exists():
            findings.append({"severity": "critical", "code": "missing_resource", "owner": owner, "resource": resource})
    return findings


def skill_quality_report(skill_path: Path) -> dict[str, Any]:
    """Run the shared deterministic skill quality gates."""

    spec = importlib.util.spec_from_file_location("franky_skill_quality", QUALITY_VALIDATOR)
    if spec is None or spec.loader is None:
        return {"skill": str(skill_path), "status": "blocked", "results": [{"gate": "quality_validator", "status": "fail", "severity": "critical", "message": "quality validator could not be loaded"}]}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.assess(skill_path)


def make_step(cap: dict[str, Any], skill: str | None, proposed_skill: str | None) -> dict[str, Any]:
    step_id = slug(str(cap.get("id") or cap.get("description") or "step"))
    return {
        "id": step_id,
        "skill": skill or proposed_skill or "unresolved-skill",
        "operation": str(cap.get("operation") or "perform_capability"),
        "inputs": list(cap.get("inputs") or ["approved request"]),
        "outputs": list(cap.get("outputs") or ["capability result"]),
        "validation": list(cap.get("validation") or ["capability contract is satisfied"]),
        "approval_gate": {"required": bool(cap.get("approval_required", False)), "reason": str(cap.get("approval_reason") or "approved_context")},
        "on_failure": "return_to_human",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request", type=Path)
    parser.add_argument("--output-root", type=Path, default=ROOT / "workflows" / "temp")
    parser.add_argument("--operation", choices=["generate_package", "audit_request", "repair_and_validate", "promote_approved_package"], default="generate_package")
    args = parser.parse_args()
    request = load_yaml(args.request) or {}
    if args.operation == "promote_approved_package":
        if request.get("approval", {}).get("status") != "approved":
            print("FAIL package approval is required before promotion")
            return 2
        print("OK package is approved; route workflows, skills, agents, and registry changes through lifecycle pipelines without launching agents")
        return 0
    if args.operation == "repair_and_validate":
        if request.get("schema") != "franky.workflow-factory-package":
            print("FAIL repair input must be a factory manifest")
            return 1
        critical = [item for item in request.get("findings", []) if item.get("severity") == "critical"]
        request["status"] = "blocked" if critical else "proposed"
        request.setdefault("repairs", []).append({"code": "revalidated_manifest", "message": "Deterministic package revalidation completed."})
        request["approval"] = {"required": True, "status": "pending", "digest": None}
        request["approval"]["digest"] = "sha256:" + hashlib.sha256(yaml.safe_dump(request, sort_keys=True).encode()).hexdigest()
        args.request.write_text(yaml.safe_dump(request, sort_keys=False), encoding="utf-8")
        print(f"OK revalidated {args.request} status={request['status']}")
        return 0 if request["status"] != "blocked" else 2
    request_id = str(request.get("request_id") or request.get("id") or "request")
    output = args.output_root / slug(request_id)
    output.mkdir(parents=True, exist_ok=True)
    skills = inventory_skills()
    roles = role_inventory()
    findings: list[dict[str, Any]] = []
    repairs: list[dict[str, Any]] = []
    skill_proposals: list[dict[str, Any]] = []
    agent_proposals: list[dict[str, Any]] = []
    quality_gate_reports: list[dict[str, Any]] = []
    targets = [str(role).lower() for role in (request.get("roles") or ["franky"])]
    for role in targets:
        if role != "shared" and role not in REGISTERED_ROLES:
            findings.append({"severity": "critical", "code": "unknown_role", "message": role})
        elif role != "shared" and role not in roles:
            findings.append({"severity": "critical", "code": "unregistered_role", "message": role})

    capabilities = request.get("capabilities") or []
    if not capabilities:
        findings.append({"severity": "critical", "code": "missing_capabilities", "message": "Explicit capability contracts are required for runnable workflow proposals."})
        capabilities = [{"id": "unresolved-purpose", "description": str(request.get("purpose") or "unresolved purpose")}]

    generated = []
    forbidden = walk_forbidden(request, "request")
    findings.extend({"severity": "critical", "code": "forbidden_key", "message": item} for item in forbidden)
    for role in targets:
        workflow_id = f"WF-{role.upper()}-{slug(request_id).upper().replace('-', '-') }"
        steps = []
        seen = set()
        for cap in capabilities:
            cap = cap if isinstance(cap, dict) else {"description": str(cap)}
            skill, score = best_skill(str(cap.get("description", "")), cap.get("skill"), skills)
            proposed = None
            if not skill:
                proposed = f"proposed-{slug(str(cap.get('id') or cap.get('description') or 'skill'))}"
                findings.append({"severity": "warning", "code": "skill_gap", "role": role, "message": proposed})
                skill_proposals.append({
                    "id": proposed,
                    "role": role,
                    "reason": str(cap.get("description", "capability gap")),
                    "required_resources": list(cap.get("required_resources") or ["SKILL.md", "agents/openai.yaml"]),
                    "status": "proposed",
                })
            elif cap.get("required_resources"):
                skill_path = next((Path(item["path"]) for item in skills if item["name"] == skill), None)
                if skill_path:
                    findings.extend(resource_findings(skill_path, list(cap["required_resources"]), skill))
            if skill:
                skill_path = next((Path(item["path"]) for item in skills if item["name"] == skill), None)
                if skill_path:
                    quality = skill_quality_report(skill_path)
                    quality_gate_reports.append(quality)
                    for gate in quality.get("results", []):
                        if gate.get("status") == "fail":
                            findings.append({"severity": "critical", "code": "skill_quality_gate", "skill": skill, "gate": gate.get("gate"), "message": gate.get("message")})
                        elif gate.get("status") == "warn":
                            findings.append({"severity": "warning", "code": "skill_quality_advisory", "skill": skill, "gate": gate.get("gate"), "message": gate.get("message")})
            target_scope = str(cap.get("target_scope", "")).lower()
            if role == "franky" and any(term in target_scope for term in ("linked project", "research resource", "scientific")):
                findings.append({"severity": "critical", "code": "role_scope_violation", "role": role, "step": cap.get("id")})
            step = make_step(cap, skill, proposed)
            if step["id"] in seen:
                replacement = f"{step['id']}-2"
                repairs.append({"code": "duplicate_step_id", "from": step["id"], "to": replacement})
                step["id"] = replacement
            seen.add(step["id"])
            if not step["inputs"] or not step["outputs"] or not step["validation"]:
                findings.append({"severity": "critical", "code": "incomplete_step_contract", "step": step["id"]})
            steps.append(step)
            if skill and score < 2:
                findings.append({"severity": "warning", "code": "partial_skill_match", "skill": skill, "step": step["id"]})
        workflow = {"version": 1, "id": workflow_id, "name": f"Generated {role} workflow", "invocation_policy": "workflow_only", "owner_role": role, "goal": request.get("purpose", "Generated workflow"), "status": "proposed", "steps": steps}
        generated.append({"role": role, "workflow": workflow, "path": f"workflows/{role}/{slug(workflow_id)}.yaml"})
        (output / "workflows" / role).mkdir(parents=True, exist_ok=True)
        (output / generated[-1]["path"]).write_text(yaml.safe_dump(workflow, sort_keys=False), encoding="utf-8")

        if request.get("mode", "full_package") == "full_package" and role != "shared":
            agent_proposals.append({
                "role": role,
                "workflow_ids": [workflow_id],
                "registry_action": "bind_workflow_after_approval",
                "adapter_action": "review_existing_adapter_before_change",
            })

    manifest = {"schema": "franky.workflow-factory-package", "version": 1, "request_id": request_id, "purpose": request.get("purpose"), "mode": request.get("mode", "full_package"), "roles": targets, "status": "blocked" if any(x["severity"] == "critical" for x in findings) else "proposed", "proposals": {"workflows": generated, "skills": skill_proposals, "agents": agent_proposals}, "quality_gates": {"policy": "franky-skill-quality-v1", "required": ["structure", "security"], "advisory": ["eval", "staleness"], "reports": quality_gate_reports}, "findings": findings, "repairs": repairs, "approval": {"required": True, "status": "pending", "digest": None}, "rollback": {"method": "remove staged package or restore approved changed paths", "destructive": False}}
    manifest["approval"]["digest"] = "sha256:" + hashlib.sha256(yaml.safe_dump(manifest, sort_keys=True).encode()).hexdigest()
    (output / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    print(f"OK staged {output} status={manifest['status']}")
    return 0 if manifest["status"] != "blocked" else 2


if __name__ == "__main__":
    raise SystemExit(main())
