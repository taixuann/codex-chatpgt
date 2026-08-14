#!/usr/bin/env python3
"""Deterministic validator for shared agent contracts and evidence governance.

This is an evaluator, not a router or workflow engine. It checks the minimum
cross-agent evidence envelope and prevents direct artifact-to-state promotion.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "manifests/agent-contracts.yaml"
REPERTOIRE = ROOT / "manifests/agent-capability-repertoires.yaml"
STATES = {"DRAFT", "VALIDATED", "REVIEWED", "ACCEPTED", "SUPERSEDED", "ARCHIVED", "INVALIDATED"}
ALLOWED_TRANSITIONS = {
    "DRAFT": {"VALIDATED", "INVALIDATED"},
    "VALIDATED": {"REVIEWED", "INVALIDATED"},
    "REVIEWED": {"ACCEPTED", "INVALIDATED"},
    "ACCEPTED": {"SUPERSEDED", "ARCHIVED", "INVALIDATED"},
    "SUPERSEDED": {"ARCHIVED"},
    "ARCHIVED": set(),
    "INVALIDATED": set(),
}
AGENTS = {"argus", "prometheus", "athena"}


def _load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_agent_contracts(path: Path = CONTRACTS) -> dict:
    doc = _load(path)
    if doc.get("kind") != "codex.agent-contract-registry.v1":
        raise ValueError("agent registry: wrong kind")
    agents = doc.get("agents") or {}
    if set(agents) != AGENTS:
        raise ValueError(f"agent registry: expected exactly {sorted(AGENTS)}")
    required = {"role", "responsibility", "forbidden_actions", "consumers", "lifecycle_boundary"}
    for name, entry in agents.items():
        missing = required - set(entry)
        if missing:
            raise ValueError(f"agents.{name}: missing {sorted(missing)}")
        for field in ("responsibility", "forbidden_actions", "consumers"):
            if not isinstance(entry[field], list) or not entry[field]:
                raise ValueError(f"agents.{name}.{field}: non-empty list required")
    expected = {
        "argus": {"scientific_interpretation", "canonical_project_mutation", "global_policy_mutation"},
        "prometheus": {"replace_argus", "scientific_decision", "global_policy_mutation"},
        "athena": {"implementation_mutation", "self_approval", "canonical_state_mutation", "global_policy_mutation"},
    }
    for name, forbidden in expected.items():
        if not forbidden.issubset(set(agents[name]["forbidden_actions"])):
            raise ValueError(f"agents.{name}: required forbidden action missing")
    return doc


def validate_repertoire(path: Path = REPERTOIRE) -> dict:
    doc = _load(path)
    agents = doc.get("agents") or {}
    for name in AGENTS:
        entry = agents.get(name)
        if not entry:
            raise ValueError(f"repertoire.{name}: missing")
        if not entry.get("primary_capabilities"):
            raise ValueError(f"repertoire.{name}: allowed capabilities required")
        if not entry.get("forbidden_capabilities"):
            raise ValueError(f"repertoire.{name}: forbidden capabilities required")
    return doc


def validate_shared_contract(document: dict) -> None:
    required = {"kind", "id", "agent", "provenance", "evidence", "claims", "unknowns", "conflicts", "readiness", "validation_status"}
    missing = required - set(document)
    if missing:
        raise ValueError(f"shared contract: missing {sorted(missing)}")
    if document["kind"] not in {f"{name}.v1" for name in ("request", "context", "handoff", "result", "review", "run")}:
        raise ValueError("shared contract: unsupported kind")
    if document["agent"] not in AGENTS | {"franky", "parent"}:
        raise ValueError("shared contract: unsupported agent")
    if document["readiness"] not in {"NOT_READY", "READY_WITH_BLOCKERS", "READY", "ACCEPTANCE_READY"}:
        raise ValueError("shared contract: invalid readiness")
    if document["validation_status"] not in {"NOT_ASSESSED", "PASS", "FAIL", "BLOCKED"}:
        raise ValueError("shared contract: invalid validation status")
    provenance = document["provenance"]
    if not isinstance(provenance, dict) or not all(provenance.get(k) for k in ("source", "source_state", "captured_at")):
        raise ValueError("shared contract: missing provenance")
    for field in ("evidence", "claims", "unknowns", "conflicts"):
        if not isinstance(document[field], list):
            raise ValueError(f"shared contract.{field}: expected list")


def validate_evidence_chain(doc: dict) -> None:
    def records(name: str) -> dict:
        values = doc.get(name, [])
        if not isinstance(values, list):
            raise ValueError(f"{name}: expected list")
        result = {}
        for index, item in enumerate(values):
            if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].strip():
                raise ValueError(f"{name}[{index}]: non-empty string id required")
            if item["id"] in result:
                raise ValueError(f"{name}: duplicate id {item['id']}")
            result[item["id"]] = item
        return result

    def references(item: dict, field: str, known: set[str]) -> set[str]:
        value = item.get(field)
        if not isinstance(value, list) or not value or any(not isinstance(ref, str) or not ref.strip() for ref in value):
            raise ValueError(f"{item.get('id')}: {field} requires non-empty string identifiers")
        result = set(value)
        if len(result) != len(value) or not result.issubset(known):
            raise ValueError(f"{item.get('id')}: {field} contains duplicate or unknown identifiers")
        return result

    evidence = records("evidence")
    claims = records("claims")
    reviews = records("reviews")
    decisions = records("decisions")
    for claim in claims.values():
        references(claim, "evidence_ids", set(evidence))
    for review in reviews.values():
        references(review, "claim_ids", set(claims))
        if review.get("reviewer") == review.get("producer"):
            raise ValueError(f"review {review.get('id')}: producer cannot review its own artifact")
    for decision in decisions.values():
        references(decision, "review_ids", set(reviews))
        references(decision, "claim_ids", set(claims))
        if decision.get("outcome") not in {"ACCEPT", "REJECT"}:
            raise ValueError(f"decision {decision.get('id')}: invalid outcome")
    for artifact in doc.get("artifacts", []):
        if artifact.get("lifecycle_state") != "ACCEPTED":
            continue
        artifact_evidence = references(artifact, "evidence_ids", set(evidence))
        artifact_claims = references(artifact, "claim_ids", set(claims))
        artifact_reviews = references(artifact, "review_ids", set(reviews))
        if any(not references(claims[item], "evidence_ids", set(evidence)).issubset(artifact_evidence) for item in artifact_claims):
            raise ValueError(f"artifact {artifact.get('artifact_id')}: claims are not bound to artifact evidence")
        if any(not references(reviews[item], "claim_ids", set(claims)).issubset(artifact_claims) for item in artifact_reviews):
            raise ValueError(f"artifact {artifact.get('artifact_id')}: reviews are not bound to artifact claims")
        decision = decisions.get(artifact.get("decision_id"))
        if not decision or set(decision["review_ids"]) != artifact_reviews or set(decision["claim_ids"]) != artifact_claims:
            raise ValueError(f"artifact {artifact.get('artifact_id')}: decision is not bound to artifact review and claim sets")
        if decision.get("outcome") != "ACCEPT":
            raise ValueError(f"artifact {artifact.get('artifact_id')}: accepted artifact requires ACCEPT decision")
    for promotion in doc.get("promotions", []):
        artifact = next((a for a in doc.get("artifacts", []) if a.get("artifact_id") == promotion.get("artifact_id")), None)
        if not artifact:
            raise ValueError("promotion: unknown artifact")
        if promotion.get("target") == "canonical-state" and promotion.get("status") != "ALLOWED":
            raise ValueError("direct artifact-to-state promotion is not allowed")
        if promotion.get("status") == "ALLOWED":
            decision = decisions.get(promotion.get("decision_id"))
            if artifact.get("lifecycle_state") != "ACCEPTED" or not decision:
                raise ValueError("artifact -> state promotion requires ACCEPTED artifact and decision")
            if artifact.get("decision_id") != promotion.get("decision_id") or decision.get("outcome") != "ACCEPT":
                raise ValueError("promotion: accepted artifact must bind to an ACCEPT decision")
            if not set(artifact.get("evidence_ids") or []).issubset(evidence) or not set(artifact.get("claim_ids") or []).issubset(claims) or not set(artifact.get("review_ids") or []).issubset(reviews):
                raise ValueError("promotion: incomplete Evidence -> Claim -> Review chain")
            if not any(item.get("id") in set(artifact.get("review_ids") or []) and item.get("outcome") == "PASS" and item.get("reviewer") != artifact.get("producer") for item in doc.get("reviews", [])):
                raise ValueError("promotion: independent PASS review is required")


def validate_artifacts(doc: dict) -> None:
    for artifact in doc.get("artifacts", []):
        state = artifact.get("lifecycle_state")
        if state not in STATES:
            raise ValueError(f"artifact {artifact.get('artifact_id')}: invalid lifecycle state")
        for field in ("owner", "producer", "authority_status", "evidence_ids", "claim_ids", "review_ids"):
            if field not in artifact:
                raise ValueError(f"artifact {artifact.get('artifact_id')}: missing {field}")
        if not artifact.get("owner") or not artifact.get("producer"):
            raise ValueError(f"artifact {artifact.get('artifact_id')}: owner and producer are required")
        if artifact.get("reviewer") is not None and artifact.get("reviewer") == artifact.get("producer"):
            raise ValueError(f"artifact {artifact.get('artifact_id')}: producer and reviewer must be separate")
        authority = artifact.get("authority_status")
        if authority not in {"proposed", "process_validated", "reviewed", "accepted", "superseded", "archived", "invalidated"}:
            raise ValueError(f"artifact {artifact.get('artifact_id')}: invalid authority status")
        expected_authority = {"DRAFT": "proposed", "VALIDATED": "process_validated", "REVIEWED": "reviewed", "ACCEPTED": "accepted", "SUPERSEDED": "superseded", "ARCHIVED": "archived", "INVALIDATED": "invalidated"}[state]
        if authority != expected_authority:
            raise ValueError(f"artifact {artifact.get('artifact_id')}: authority status does not match lifecycle state")
        if state == "ACCEPTED" and not artifact.get("reviewer"):
            raise ValueError(f"artifact {artifact.get('artifact_id')}: accepted artifact requires reviewer")
        if state in {"REVIEWED", "ACCEPTED"} and not artifact.get("reviewer"):
            raise ValueError(f"artifact {artifact.get('artifact_id')}: reviewed artifact requires reviewer")
        if state == "ACCEPTED" and not all(artifact.get(field) for field in ("evidence_ids", "claim_ids", "review_ids")):
            raise ValueError(f"artifact {artifact.get('artifact_id')}: accepted artifact requires complete evidence chain references")
        previous = artifact.get("previous_state")
        if previous is not None and state not in ALLOWED_TRANSITIONS.get(previous, set()):
            raise ValueError(f"artifact {artifact.get('artifact_id')}: invalid transition {previous} -> {state}")


def evaluate_case(case: dict, repertoire: dict) -> None:
    kind = case.get("kind")
    if kind == "claim" and (not case.get("evidence_ids") or any(not item for item in case.get("evidence_ids", []))):
        raise ValueError("unsupported inference")
    if kind == "evidence" and not case.get("provenance"):
        raise ValueError("missing provenance")
    if kind == "handoff" and case.get("from_agent") == case.get("to_agent"):
        raise ValueError("invalid handoff")
    if kind == "mutation" and case.get("agent") in AGENTS and case.get("target") in {"canonical-state", "global-skills", "agent-contracts", "workflow-policies"}:
        raise ValueError("unauthorized mutation")
    if kind == "capability":
        entry = repertoire["agents"][case["agent"]]
        if case["capability"] in entry.get("forbidden_capabilities", []) or case["capability"] not in entry.get("primary_capabilities", []):
            raise ValueError("wrong capability usage")
    if kind == "closeout" and case.get("status") != "COMPLETE":
        raise ValueError("incomplete closeout")


def validate(path: Path) -> None:
    validate_agent_contracts()
    repertoire = validate_repertoire()
    shared_example = _load(ROOT / "ops/schemas/examples/shared-contracts.yaml")
    validate_shared_contract(shared_example)
    doc = _load(path)
    validate_artifacts(doc)
    validate_evidence_chain(doc)
    for case in doc.get("cases", []):
        try:
            evaluate_case(case, repertoire)
        except ValueError:
            if case.get("expect") != "FAIL":
                raise
        else:
            if case.get("expect") == "FAIL":
                raise ValueError(f"case {case.get('id')}: expected deterministic failure")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args()
    try:
        validate(args.fixture)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL {args.fixture}: {exc}")
        return 1
    print(f"OK {args.fixture}: agent lifecycle")
    return 0


if __name__ == "__main__":
    sys.exit(main())
