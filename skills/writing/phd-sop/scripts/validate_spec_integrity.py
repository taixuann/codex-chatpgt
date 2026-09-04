#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    rubric = load("references/rubric.yaml")
    manifest = load("references/source-manifest.yaml")
    cmap = load("references/construct-map.yaml")
    anchors = load("evals/anchors.yaml")
    cases = load("evals/cases.yaml")
    adversarial = load("evals/adversarial.yaml")
    patterns = load("references/ai-pattern-catalog.yaml")

    errors: list[str] = []
    gate_ids = {x["id"] for x in rubric["hard_gates"]}
    criterion_ids = {x["id"] for x in rubric["criteria"]}
    all_ids = gate_ids | criterion_ids
    source_ids = {x["id"] for x in manifest["sources"]}
    runtime_sources = {"runtime_target_policy"}

    # Source aliases must resolve to manifest or declared runtime evidence.
    aliases = rubric.get("source_aliases", {})
    for alias, refs in aliases.items():
        if not refs:
            errors.append(f"source alias {alias} is empty")
        for ref in refs:
            if ref not in source_ids | runtime_sources:
                errors.append(f"source alias {alias} references unknown source {ref}")

    used_aliases = {x for c in rubric["criteria"] for x in c.get("source_basis", [])}
    for alias in used_aliases:
        if alias not in aliases:
            errors.append(f"criterion references undefined source alias {alias}")

    # Construct graph must reference real criterion/gate IDs.
    for group in cmap.get("groups", []):
        for member in group.get("members", []):
            if member not in all_ids:
                errors.append(
                    f"construct group {group.get('id')} references unknown id {member}"
                )

    # Eval/anchor references must remain valid and cover every canonical ID.
    coverage: set[str] = set()
    for container_name, rows, key in (
        ("anchors", anchors.get("examples", []), "targets"),
        ("cases", cases.get("cases", []), "targets"),
        ("adversarial", adversarial.get("cases", []), "must_catch"),
    ):
        seen: set[str] = set()
        for row in rows:
            rid = row.get("id")
            if not rid:
                errors.append(f"{container_name}: row missing id")
            elif rid in seen:
                errors.append(f"{container_name}: duplicate id {rid}")
            if rid:
                seen.add(rid)
            for target in row.get(key, []):
                if target not in all_ids:
                    errors.append(f"{container_name}:{rid} targets unknown id {target}")
                else:
                    coverage.add(target)

    missing_coverage = sorted(all_ids - coverage)
    if missing_coverage:
        errors.append(
            f"canonical IDs without fixture/anchor coverage: {missing_coverage}"
        )

    # Readiness references must be canonical ordinal criteria.
    for row in rubric.get("readiness", {}).get("core_minimums", []):
        rid = row.get("id")
        if rid not in criterion_ids:
            errors.append(
                f"readiness minimum must target ordinal criterion: {rid}"
            )

    # Every scored criterion has local anchors and not-assessed semantics.
    for item in rubric["criteria"]:
        cid = item["id"]
        if set(item.get("anchors", {})) != {"1", "2", "3", "4", "5"}:
            errors.append(f"{cid}: incomplete anchors")
        if "not_assessed_when" not in item:
            errors.append(f"{cid}: missing not_assessed_when")

    # AI-pattern catalogue is dated, false-positive-aware, diagnostic-only.
    pattern_ids: list[str] = []
    for pattern in patterns.get("patterns", []):
        pid = pattern.get("id")
        if pid:
            pattern_ids.append(pid)
        for key in (
            "id",
            "category",
            "first_observed",
            "last_reviewed",
            "confidence",
            "genres",
            "triggers",
            "false_positive_notes",
        ):
            if not pattern.get(key):
                errors.append(f"pattern {pid or '<missing>'}: missing {key}")
        if pattern.get("diagnostic_only") is not True:
            errors.append(
                f"pattern {pid or '<missing>'}: diagnostic_only must be true"
            )

    duplicate_patterns = sorted(
        {pid for pid in pattern_ids if pattern_ids.count(pid) > 1}
    )
    if duplicate_patterns:
        errors.append(f"duplicate AI-pattern ids: {duplicate_patterns}")

    # Mandatory source families from the canonical issue are present.
    required_sources = {
        "repo_skill_guidance",
        "athena_kernel",
        "better_writing",
        "addictive_writing",
        "scholarship_hunting",
        "sop_rubric_evaluator",
        "agent_writing",
        "story_skills",
        "liang_detectors",
        "synthid_text",
        "style_confounds_2026",
        "gopen_swan",
        "brookhart_rubric",
        "moskal_leydens",
        "user_sop_gold",
        "scientific_peer_review",
        "stanford_sop_guidance",
        "duke_sop_guidance",
        "cornell_asop_guidance",
    }
    missing_sources = sorted(required_sources - source_ids)
    if missing_sources:
        errors.append(f"required sources missing: {missing_sources}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        f"PASS: referential closure for {len(all_ids)} canonical IDs; "
        f"{len(pattern_ids)} diagnostic patterns; coverage complete"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
