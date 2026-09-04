#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys


def weighted_kappa(pairs: list[tuple[int, int]]) -> float | None:
    if not pairs:
        return None
    n = len(pairs)
    levels = [1, 2, 3, 4, 5]
    observed = 0.0
    for a, b in pairs:
        observed += abs(a - b) / 4.0
    observed /= n

    ca = {k: 0 for k in levels}
    cb = {k: 0 for k in levels}
    for a, b in pairs:
        ca[a] += 1
        cb[b] += 1

    expected = 0.0
    for a in levels:
        for b in levels:
            pa = ca[a] / n
            pb = cb[b] / n
            expected += pa * pb * (abs(a - b) / 4.0)
    if expected == 0:
        return 1.0 if observed == 0 else None
    return 1.0 - observed / expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    errors: list[str] = []
    prov = data.get("provenance", {})
    for key in ("judge_streams", "rubric_revision", "anchor_revision", "fixture_revision", "prompt_revision", "run_date"):
        if not prov.get(key):
            errors.append(f"missing provenance: {key}")

    grouped: dict[tuple[str, str], dict[str, int]] = defaultdict(dict)
    for row in data.get("ordinal", []):
        score = row.get("score")
        if score not in {1, 2, 3, 4, 5}:
            errors.append(f"invalid ordinal score in {row}")
            continue
        key = (row.get("case_id"), row.get("criterion_id"))
        judge = row.get("judge")
        if not all(key) or not judge:
            errors.append(f"incomplete ordinal record: {row}")
            continue
        if judge in grouped[key]:
            errors.append(f"duplicate judge record for {key}: {judge}")
        grouped[key][judge] = score

    judge_streams = prov.get("judge_streams", [])
    pairs: list[tuple[int, int]] = []
    distances: list[int] = []
    if len(judge_streams) == 2:
        a_name, b_name = judge_streams
        for key, scores in grouped.items():
            if a_name not in scores or b_name not in scores:
                errors.append(f"missing paired judge score for {key}")
                continue
            pair = (scores[a_name], scores[b_name])
            pairs.append(pair)
            distances.append(abs(pair[0] - pair[1]))

    exact = (sum(d == 0 for d in distances) / len(distances)) if distances else None
    adjacent = (sum(d <= 1 for d in distances) / len(distances)) if distances else None
    max_distance = max(distances) if distances else None
    kappa = weighted_kappa(pairs)

    pw_grouped: dict[str, dict[str, tuple[str, str | None]]] = defaultdict(dict)
    for row in data.get("pairwise", []):
        cid = row.get("case_id")
        judge = row.get("judge")
        winner = row.get("winner")
        if not cid or not judge or not winner:
            errors.append(f"incomplete pairwise record: {row}")
            continue
        pw_grouped[cid][judge] = (winner, row.get("reason_code"))

    pairwise_agree = []
    if len(judge_streams) == 2:
        a_name, b_name = judge_streams
        for cid, rows in pw_grouped.items():
            if a_name not in rows or b_name not in rows:
                errors.append(f"missing pairwise judge for {cid}")
                continue
            pairwise_agree.append(rows[a_name] == rows[b_name])

    result = {
        "ordinal_items": len(distances),
        "exact_agreement": exact,
        "adjacent_agreement": adjacent,
        "max_score_distance": max_distance,
        "weighted_kappa_diagnostic": kappa,
        "pairwise_exact_agreement": (
            sum(pairwise_agree) / len(pairwise_agree) if pairwise_agree else None
        ),
        "harness_self_test": bool(data.get("harness_self_test")),
    }
    print(json.dumps(result, indent=2, sort_keys=True))

    if data.get("harness_self_test"):
        expected = data.get("expected_self_test", {})
        if adjacent is None or adjacent < expected.get("adjacent_agreement_min", 0):
            errors.append("self-test adjacent agreement below expected minimum")
        if max_distance is None or max_distance > expected.get("max_score_distance", 4):
            errors.append("self-test score distance exceeds expected maximum")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
