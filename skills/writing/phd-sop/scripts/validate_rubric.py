#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
RUBRIC = ROOT / "references" / "rubric.yaml"

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def fail(errors):
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1

def main() -> int:
    data = load(RUBRIC)
    errors = []
    modes = set(data.get("modes", []))
    if not modes:
        errors.append("rubric.modes is empty")

    gates = data.get("hard_gates", [])
    criteria = data.get("criteria", [])
    gate_ids = [x.get("id") for x in gates]
    criterion_ids = [x.get("id") for x in criteria]

    for label, ids in (("gate", gate_ids), ("criterion", criterion_ids)):
        missing = [i for i in ids if not i]
        if missing:
            errors.append(f"{label} contains missing id")
        dup = sorted({i for i in ids if ids.count(i) > 1})
        if dup:
            errors.append(f"duplicate {label} ids: {dup}")

    if set(gate_ids) & set(criterion_ids):
        errors.append("hard-gate IDs overlap scored criterion IDs")

    for gate in gates:
        gid = gate.get("id", "<missing>")
        if gate.get("status_values") != ["PASS", "FAIL", "UNRESOLVED"]:
            errors.append(f"{gid}: hard gate must use PASS/FAIL/UNRESOLVED")
        if "anchors" in gate or "score" in gate:
            errors.append(f"{gid}: hard gate must not be ordinal-scored")
        app = gate.get("applicable_modes", [])
        if app != ["all"] and not set(app).issubset(modes):
            errors.append(f"{gid}: unknown applicable mode")
        if not gate.get("failure_codes"):
            errors.append(f"{gid}: missing failure_codes")

    required = {"id","name","level","definition","applicable_modes","source_basis","not_assessed_when","anchors"}
    allowed_levels = {"sentence","sentence_pair","paragraph","document"}
    for item in criteria:
        cid = item.get("id", "<missing>")
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{cid}: missing fields {missing}")
            continue
        if item["level"] not in allowed_levels:
            errors.append(f"{cid}: invalid level {item['level']}")
        if not set(item["applicable_modes"]).issubset(modes):
            errors.append(f"{cid}: unknown applicable mode")
        if not isinstance(item["not_assessed_when"], list):
            errors.append(f"{cid}: not_assessed_when must be list")
        anchors = item["anchors"]
        if set(anchors) != {"1","2","3","4","5"}:
            errors.append(f"{cid}: anchors must define 1..5 exactly")
        for score in ("1","2","3","4","5"):
            if not str(anchors.get(score, "")).strip():
                errors.append(f"{cid}: empty anchor {score}")
        if not item["source_basis"]:
            errors.append(f"{cid}: empty source_basis")

    all_ids = set(gate_ids) | set(criterion_ids)
    readiness = data.get("readiness", {})
    for row in readiness.get("core_minimums", []):
        rid = row.get("id")
        if rid not in all_ids:
            errors.append(f"readiness references unknown id {rid}")
        if rid in set(gate_ids):
            errors.append(f"readiness ordinal minimum cannot target hard gate {rid}")
        if row.get("min") not in {1,2,3,4,5}:
            errors.append(f"readiness {rid}: invalid min")
    if readiness.get("arithmetic_overall_score_forbidden") is not True:
        errors.append("arithmetic_overall_score_forbidden must be true")

    expected = {
        "G01","G02","G03","G04","G05","G06","G07","G08","G09","G10",
        *{f"S{i:02d}" for i in range(1,10)},
        *{f"PAIR{i:02d}" for i in range(1,5)},
        *{f"P{i:02d}" for i in range(1,11)},
        *{f"D{i:02d}" for i in range(1,16)}
    }
    missing_expected = sorted(expected - all_ids)
    unexpected = sorted(all_ids - expected)
    if missing_expected:
        errors.append(f"canonical ids missing: {missing_expected}")
    if unexpected:
        errors.append(f"unexpected canonical ids: {unexpected}")

    if errors:
        return fail(errors)
    print(f"PASS: {len(gates)} hard gates, {len(criteria)} ordinal criteria")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
