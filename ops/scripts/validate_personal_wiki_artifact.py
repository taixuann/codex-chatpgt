#!/usr/bin/env python3
"""Validate the bounded Personal Wiki artifact envelope."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import yaml


def validate(path: Path) -> None:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    required = {"kind", "id", "title", "artifact_state", "owner", "producer", "authority_status", "provenance", "claims", "context_consumption", "promotion"}
    missing = required - set(document or {})
    if missing:
        raise ValueError(f"missing required fields: {sorted(missing)}")
    if document["kind"] != "personal-wiki.artifact.v1":
        raise ValueError("unsupported artifact kind")
    for field in ("id", "title"):
        if not isinstance(document[field], str) or not document[field]:
            raise ValueError(f"{field} must be a non-empty string")
    if document["artifact_state"] not in {"DRAFT", "REVIEWED", "SUPERSEDED", "ARCHIVED"}:
        raise ValueError("invalid artifact state")
    if document["owner"] != "personal_wiki_owner":
        raise ValueError("owner must be personal_wiki_owner")
    if document["producer"] not in {"human", "feynman", "parent"}:
        raise ValueError("producer must be human, feynman, or parent")
    if document["authority_status"] != "PERSONAL_CONTEXT_ONLY":
        raise ValueError("Personal Wiki artifacts cannot claim project or literature authority")
    provenance = document["provenance"]
    if not isinstance(provenance, dict):
        raise ValueError("provenance must be a mapping")
    for field in ("captured_at", "source_state"):
        if not isinstance(provenance.get(field), str) or not provenance[field]:
            raise ValueError(f"provenance.{field} must be a non-empty string")
    if not isinstance(provenance.get("source_refs"), list) or not provenance["source_refs"]:
        raise ValueError("provenance.source_refs must be non-empty")
    if not all(isinstance(ref, str) and ref for ref in provenance["source_refs"]):
        raise ValueError("provenance source references must be non-empty strings")
    context = document["context_consumption"]
    consumers = context.get("authorized_consumers")
    if not isinstance(consumers, list) or not consumers or any(not isinstance(item, str) or not item for item in consumers):
        raise ValueError("authorized_consumers must be a non-empty list of names")
    if "feynman" not in consumers:
        raise ValueError("v1 must authorize Feynman as the current primary consumer")
    if not isinstance(context.get("authorization_ref"), str) or not context["authorization_ref"]:
        raise ValueError("authorized consumers require authorization_ref")
    if context.get("use") != "reusable_context" or context.get("project_authority_overrides") is not True:
        raise ValueError("context consumption must remain reusable context below project authority")
    claims = document["claims"]
    if not isinstance(claims, list) or not claims:
        raise ValueError("claims must be non-empty")
    for claim in claims:
        if not isinstance(claim, dict):
            raise ValueError("each claim must be a mapping")
        for field in ("id", "category", "statement", "evidence_refs"):
            if field not in claim:
                raise ValueError(f"claim missing required field: {field}")
        if claim["category"] not in {"personal_understanding", "hypothesis", "uncertainty", "unsupported_or_unknown"}:
            raise ValueError(f"{claim['id']}: invalid claim category")
        if not isinstance(claim["statement"], str) or not claim["statement"]:
            raise ValueError(f"{claim['id']}: statement must be a non-empty string")
        if not isinstance(claim["evidence_refs"], list):
            raise ValueError(f"{claim['id']}: evidence_refs must be a list")
    ids = [claim.get("id") for claim in claims]
    if any(not isinstance(claim_id, str) or not claim_id for claim_id in ids) or len(ids) != len(set(ids)):
        raise ValueError("claim ids must be non-empty and unique")
    for claim in claims:
        if not isinstance(claim.get("evidence_refs"), list):
            raise ValueError(f"{claim['id']}: evidence_refs must be present, even for uncertainty")
    promotion = document["promotion"]
    if not isinstance(promotion, dict):
        raise ValueError("promotion must be a mapping")
    if not isinstance(promotion.get("target"), str) or not promotion["target"]:
        raise ValueError("promotion.target must be a non-empty string")
    if not isinstance(promotion.get("write_performed"), bool):
        raise ValueError("promotion.write_performed must be boolean")
    if promotion.get("status") not in {"NONE", "PROPOSED", "REJECTED", "ACCEPTED"}:
        raise ValueError("invalid promotion status")
    if promotion.get("target") == "scientific_wiki":
        raise ValueError("Personal Wiki cannot replace or directly write Scientific Wiki")
    if promotion.get("target") not in {"personal_context", "project_knowledge"} and not promotion.get("authorization_ref"):
        raise ValueError("future promotion targets require explicit authorization_ref")
    if promotion.get("status") == "PROPOSED" and not promotion.get("proposal_id"):
        raise ValueError("promotion proposals require proposal_id")
    if promotion.get("status") == "ACCEPTED" and not promotion.get("owner_decision_ref"):
        raise ValueError("accepted promotions require owner_decision_ref")
    if promotion.get("write_performed") is not False:
        raise ValueError("promotion validation cannot authorize an automatic write")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    try:
        validate(args.artifact)
    except (OSError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL personal-wiki: {exc}")
        return 1
    print("OK personal-wiki: bounded artifact, provenance, Feynman context, and proposal boundaries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
