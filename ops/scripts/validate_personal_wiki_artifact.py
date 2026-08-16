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
    if document["artifact_state"] not in {"DRAFT", "REVIEWED", "SUPERSEDED", "ARCHIVED"}:
        raise ValueError("invalid artifact state")
    if document["authority_status"] != "PERSONAL_CONTEXT_ONLY":
        raise ValueError("Personal Wiki artifacts cannot claim project or literature authority")
    provenance = document["provenance"]
    if not isinstance(provenance.get("source_refs"), list) or not provenance["source_refs"]:
        raise ValueError("provenance.source_refs must be non-empty")
    if not all(isinstance(ref, str) and ref for ref in provenance["source_refs"]):
        raise ValueError("provenance source references must be non-empty strings")
    context = document["context_consumption"]
    if context != {"consumer": "feynman", "use": "reusable_context", "project_authority_overrides": True}:
        raise ValueError("context consumption must be bounded Feynman reusable context")
    claims = document["claims"]
    if not isinstance(claims, list) or not claims:
        raise ValueError("claims must be non-empty")
    ids = [claim.get("id") for claim in claims]
    if any(not isinstance(claim_id, str) or not claim_id for claim_id in ids) or len(ids) != len(set(ids)):
        raise ValueError("claim ids must be non-empty and unique")
    for claim in claims:
        if not isinstance(claim.get("evidence_refs"), list):
            raise ValueError(f"{claim['id']}: evidence_refs must be present, even for uncertainty")
    promotion = document["promotion"]
    if promotion.get("status") == "PROPOSED" and not promotion.get("proposal_id"):
        raise ValueError("promotion proposals require proposal_id")
    if promotion.get("target") == "scientific_wiki":
        raise ValueError("Personal Wiki cannot replace or directly write Scientific Wiki")


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
