#!/usr/bin/env python3
"""Validate the persisted real scientific-slice authority/review binding."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml


REQUIRED_AUTHORITY_PATHS = {
    "active-projects/res_volatile-polydopamine/project.yaml",
    "AGENTS.md",
    ".agents/manifest.yaml",
    ".agents/CURRENT.md",
    ".agents/DECISIONS.md",
    "active-projects/res_volatile-polydopamine/AGENTS.md",
    "active-projects/res_volatile-polydopamine/documentation/CURRENT.md",
    "active-projects/res_volatile-polydopamine/documentation/DECISIONS.md",
}


def _target_digest(packet: dict) -> str:
    canonical = json.loads(json.dumps(packet))
    canonical["lifecycle"]["athena_review"].pop("reviewed_target_digest", None)
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def validate(packet_path: Path, review_path: Path) -> None:
    repo_root = packet_path.resolve().parents[2]
    packet_ref = str(packet_path.resolve().relative_to(repo_root))
    review_ref = str(review_path.resolve().relative_to(repo_root))
    packet = yaml.safe_load(packet_path.read_text(encoding="utf-8"))
    review = yaml.safe_load(review_path.read_text(encoding="utf-8"))
    if packet.get("kind") != "feynman.real-scientific-vertical-slice.v1":
        raise ValueError("unexpected vertical-slice kind")
    context = packet.get("project_context") or {}
    if context.get("authority_status") != "PINNED_AND_VERIFIED":
        raise ValueError("project authority is not pinned and verified")
    authorities = context.get("authority_sources") or []
    entries = {item.get("path"): item for item in authorities}
    missing = REQUIRED_AUTHORITY_PATHS - set(entries)
    if missing:
        raise ValueError(f"missing authority provenance: {sorted(missing)}")
    for path, item in entries.items():
        if not path or not item.get("git_blob") or not item.get("role"):
            raise ValueError(f"incomplete authority provenance: {path}")
    lifecycle_review = (packet.get("lifecycle") or {}).get("athena_review") or {}
    if lifecycle_review.get("status") == "PENDING":
        raise ValueError("Athena review remains pending")
    if lifecycle_review.get("artifact") != review_ref:
        raise ValueError("packet does not reference the persisted Athena review")
    digest = f"sha256:{_target_digest(packet)}"
    if lifecycle_review.get("reviewed_target_digest") != digest:
        raise ValueError("packet target digest is stale")
    if review.get("reviewed_target") != packet_ref:
        raise ValueError("review targets a different packet")
    if review.get("reviewed_target_revision") != digest:
        raise ValueError("persisted review targets a stale packet revision")
    if review.get("reviewer_id") != "athena" or review.get("recommendation") not in {"PASS", "CONDITIONAL_PASS"}:
        raise ValueError("review is not an independent Athena recommendation")
    if (packet.get("lifecycle") or {}).get("scientific_acceptance") != "NOT_ASSESSED":
        raise ValueError("scientific acceptance must remain NOT_ASSESSED")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("review", type=Path)
    args = parser.parse_args()
    try:
        validate(args.packet, args.review)
    except (OSError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL vertical-slice-evidence: {exc}")
        return 1
    print("OK vertical-slice-evidence: authority and Athena review are revision-bound")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
