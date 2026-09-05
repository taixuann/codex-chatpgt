#!/usr/bin/env python3
"""Validate and run the bounded skill-creator evaluation contract."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Iterator

import yaml


GATES = {
    "G1_STRUCTURE",
    "G2_PROVENANCE",
    "G3_ROUTING",
    "G4_BEHAVIOR",
    "G5_COEXISTENCE",
    "G6_EFFICIENCY",
    "G7_INDEPENDENT_REVIEW",
}
PARTITIONS = {"must_pass", "regression", "held_out"}
KINDS = {"routing", "CREATE", "UPDATE", "MAINTAIN", "EVALUATE"}
PROCESS_ITEM_TYPES = {"command_execution", "custom_tool_call", "function_call", "mcp_tool_call", "tool_call"}


def load_cases(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("evaluation file must contain a mapping")
    return data


def validate(path: Path) -> list[str]:
    try:
        data = load_cases(path)
    except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
        return [str(exc)]
    errors: list[str] = []
    if data.get("schema_version") != 2 or data.get("skill") != "skill-creator":
        errors.append("schema_version 2 and skill skill-creator are required")
    gates = data.get("gates")
    if not isinstance(gates, list):
        errors.append("gates must be a list")
    else:
        gate_ids = {item.get("id") for item in gates if isinstance(item, dict)}
        errors.extend(f"missing gate: {gate}" for gate in sorted(GATES - gate_ids))
        if gate_ids - GATES:
            errors.append("gates contain an unknown id")
    cases = data.get("cases")
    if not isinstance(cases, list):
        return errors + ["cases must be a list"]
    seen: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"case {index} must be a mapping")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"case {index} requires id")
        elif case_id in seen:
            errors.append(f"duplicate case id: {case_id}")
        else:
            seen.add(case_id)
        if case.get("kind") not in KINDS:
            errors.append(f"{case_id}: kind must be one of {sorted(KINDS)}")
        if case.get("partition") not in PARTITIONS:
            errors.append(f"{case_id}: partition must be one of {sorted(PARTITIONS)}")
        if case.get("gate") not in GATES:
            errors.append(f"{case_id}: gate is invalid")
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            errors.append(f"{case_id}: prompt is required")
        if not isinstance(case.get("expected"), str) or not case["expected"].strip():
            errors.append(f"{case_id}: expected outcome is required")
        if case.get("kind") == "routing" and case.get("polarity") not in {"positive", "negative"}:
            errors.append(f"{case_id}: routing polarity must be positive or negative")
    routing = [case for case in cases if isinstance(case, dict) and case.get("kind") == "routing"]
    if len(routing) < 10:
        errors.append("routing corpus requires at least 10 realistic prompts")
    if not any(case.get("partition") == "held_out" for case in cases if isinstance(case, dict)):
        errors.append("evaluation requires a held-out partition")
    if not any(case.get("paired") is True for case in cases if isinstance(case, dict)):
        errors.append("evaluation requires at least one paired with/without-skill case")
    return errors


def _text_from_event(event: dict) -> str:
    item = event.get("item")
    if not isinstance(item, dict):
        return ""
    value = item.get("text") or item.get("content")
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(part.get("text", "") for part in value if isinstance(part, dict))
    return ""


def _events(stdout: str) -> list[dict]:
    result = []
    for line in stdout.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            result.append(value)
    return result


def _final_text(events: list[dict]) -> str:
    texts = [_text_from_event(event) for event in events]
    return next((text for text in reversed(texts) if text), "")


def _json_object(text: str) -> dict:
    cleaned = text.strip().strip("`").strip()
    if cleaned.startswith("json"):
        cleaned = cleaned[4:].strip()
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _runtime_observed(events: list[dict], stdout: str, fixture: Path) -> bool:
    """Accept only an observable load/trace signal, never the prompt itself."""
    names = ("skill_loads", "loaded_skills", "loaded_skill", "skill")
    for event in events:
        for key in names:
            value = event.get(key)
            values = value if isinstance(value, list) else [value]
            if any(isinstance(item, str) and ("skill-creator" in item or str(fixture) in item) for item in values):
                return True
            if any(isinstance(item, dict) and "skill-creator" in json.dumps(item) for item in values):
                return True
        item = event.get("item")
        if isinstance(item, dict) and item.get("type") == "skill":
            return True
    return any(marker in stdout for marker in (".agents/skills/skill-creator", "skill-creator/SKILL.md"))


def _process_observed(events: list[dict]) -> bool:
    """Require an execution/tool trace before claiming behavioral evidence."""
    for event in events:
        item = event.get("item")
        item_type = item.get("type") if isinstance(item, dict) else event.get("type")
        if item_type in PROCESS_ITEM_TYPES:
            return True
    return False


@contextmanager
def _fixture(skill_dir: Path, with_skill: bool) -> Iterator[Path]:
    with tempfile.TemporaryDirectory(prefix="skill-creator-eval-") as directory:
        root = Path(directory)
        (root / ".codex-home").mkdir()
        (root / "AGENTS.md").write_text(
            "# Isolated skill evaluation\n\nUse available skills only when the request matches their description.\n",
            encoding="utf-8",
        )
        if with_skill:
            target = root / ".agents" / "skills" / "skill-creator"
            shutil.copytree(skill_dir, target, ignore=shutil.ignore_patterns("__pycache__"))
        yield root


def _run_once(case: dict, runtime: str, timeout: int, skill_dir: Path, with_skill: bool) -> dict:
    with _fixture(skill_dir, with_skill) as fixture:
        marker = "$skill-creator " if with_skill and case["kind"] != "routing" else ""
        prompt = (
            f"{marker}Run this bounded read-only skill-creator evaluation. "
            "Return exactly one JSON object with keys selected_skill and disposition. "
            "selected_skill is skill-creator or none.\n\n"
            f"Case {case['id']} ({case['kind']}): {case['prompt']}"
        )
        base = {
            "case_id": case["id"],
            "expected": case["expected"],
            "condition": "with_skill" if with_skill else "without_skill",
            "fixture": ".agents/skills/skill-creator" if with_skill else "no skill fixture",
        }
        if not shutil.which(runtime):
            return {**base, "status": "NOT_ASSESSED", "reason": f"runtime not found: {runtime}"}
        command = [
            runtime, "exec", "--json", "--ephemeral", "--sandbox", "read-only",
            "--skip-git-repo-check", "--ignore-user-config", "--cd", str(fixture), prompt,
        ]
        environment = os.environ.copy()
        environment["CODEX_HOME"] = str(fixture / ".codex-home")
        started = time.monotonic()
        try:
            process = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False, env=environment)
        except subprocess.TimeoutExpired:
            return {**base, "status": "NOT_ASSESSED", "reason": f"runtime timeout after {timeout}s"}
        stdout = process.stdout or ""
        events = _events(stdout)
        report = _json_object(_final_text(events))
        key = "selected_skill" if case["kind"] == "routing" else "disposition"
        observed = report.get(key)
        loaded = _runtime_observed(events, stdout, fixture)
        process_observed = _process_observed(events)
        if process.returncode != 0:
            status, reason = "NOT_ASSESSED", f"runtime exit {process.returncode}"
        elif not loaded and with_skill:
            status, reason = "NOT_ASSESSED", "runtime did not expose a skill-load signal"
        elif with_skill and observed == case["expected"] and case["kind"] != "routing" and not process_observed:
            status, reason = "NOT_ASSESSED", "runtime outcome lacked an observable tool/command trace"
        elif with_skill and observed == case["expected"]:
            status, reason = "PASS", "skill fixture/load signal and expected outcome observed"
        elif not with_skill:
            status, reason = "OBSERVED", "baseline output recorded without skill fixture"
        else:
            status, reason = "FAIL", f"expected {case['expected']}, observed {observed!r}"
        return {
            **base,
            "status": status,
            "observed": observed,
            "runtime_observed": loaded,
            "process_observed": process_observed,
            "events": len(events),
            "returncode": process.returncode,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "stdout_bytes": len(stdout.encode("utf-8")),
            "reason": reason,
            "stderr": (process.stderr or "").splitlines()[-5:],
        }


def _routing_metrics(results: list[dict], cases: list[dict]) -> dict:
    by_id = {case["id"]: case for case in cases}
    assessed = [result for result in results if result.get("status") == "PASS"]
    tp = sum(by_id[result["case_id"]].get("polarity") == "positive" for result in assessed if result.get("observed") == "skill-creator")
    fn = sum(by_id[result["case_id"]].get("polarity") == "positive" for result in assessed if result.get("observed") != "skill-creator")
    fp = sum(by_id[result["case_id"]].get("polarity") == "negative" for result in assessed if result.get("observed") == "skill-creator")
    tn = sum(by_id[result["case_id"]].get("polarity") == "negative" for result in assessed if result.get("observed") != "skill-creator")
    denominator_precision = tp + fp
    denominator_recall = tp + fn
    expected_cases = [case for case in cases if case.get("kind") == "routing"]
    complete = len(results) == len(expected_cases) and bool(results)
    return {
        "status": "PASS" if complete and len(assessed) == len(results) else "NOT_ASSESSED",
        "TP": tp, "FN": fn, "FP": fp, "TN": tn,
        "precision": round(tp / denominator_precision, 3) if denominator_precision else None,
        "recall": round(tp / denominator_recall, 3) if denominator_recall else None,
        "false_positive_rate": round(fp / (fp + tn), 3) if fp + tn else None,
        "assessed_cases": len(assessed),
        "total_cases": len(results),
    }


def _compare(before_path: Path, after_path: Path) -> dict:
    before = json.loads(before_path.read_text(encoding="utf-8"))
    after = json.loads(after_path.read_text(encoding="utf-8"))
    def with_skill(data: dict) -> list[dict]:
        return [item for item in data.get("results", []) if item.get("condition") == "with_skill"]

    before_results = with_skill(before)
    after_results = with_skill(after)
    before_keys = {(item.get("case_id"), item.get("partition")) for item in before_results}
    after_keys = {(item.get("case_id"), item.get("partition")) for item in after_results}
    statuses = {"PASS", "FAIL"}
    comparable = (
        before.get("coverage", {}).get("full_corpus") is True
        and after.get("coverage", {}).get("full_corpus") is True
        and bool(before_results)
        and before_keys == after_keys
        and {partition for _, partition in before_keys} == PARTITIONS
        and all(item.get("status") in statuses for item in before_results + after_results)
    )

    def score(results: list[dict], partition: str, status: str = "PASS") -> int:
        return sum(item.get("status") == status and item.get("partition") == partition for item in results)

    before_held = score(before_results, "held_out")
    after_held = score(after_results, "held_out")
    before_regression = score(before_results, "regression", "FAIL")
    after_regression = score(after_results, "regression", "FAIL")
    before_must_pass_failures = sum(item.get("partition") == "must_pass" and item.get("status") != "PASS" for item in before_results)
    after_must_pass_failures = sum(item.get("partition") == "must_pass" and item.get("status") != "PASS" for item in after_results)
    return {
        "status": "PASS" if comparable and before_must_pass_failures == 0 and after_must_pass_failures == 0 and after_held > 0 and after_held >= before_held and after_regression <= before_regression else "REJECT",
        "held_out_before": before_held,
        "held_out_after": after_held,
        "regression_failures_before": before_regression,
        "regression_failures_after": after_regression,
        "must_pass_failures_before": before_must_pass_failures,
        "must_pass_failures_after": after_must_pass_failures,
        "validation_gated": comparable,
    }


def _independent_review_status(requested: str, evidence_path: Path | None, skill_dir: Path) -> str:
    if requested != "PASS" or not evidence_path or not evidence_path.is_file():
        return "NOT_ASSESSED"
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        current = subprocess.run(
            ["git", "-C", str(skill_dir), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=False,
        ).stdout.strip()
    except (OSError, UnicodeError, json.JSONDecodeError):
        return "NOT_ASSESSED"
    return "PASS" if (
        evidence.get("verdict") == "PASS"
        and evidence.get("reviewer")
        and evidence.get("independent") is True
        and evidence.get("target_revision") == current
    ) else "NOT_ASSESSED"


def run(path: Path, skill_dir: Path, runtime: str, timeout: int, case_ids: set[str] | None, review_status: str, review_evidence: Path | None) -> dict:
    data = load_cases(path)
    cases = [case for case in data["cases"] if not case_ids or case["id"] in case_ids]
    results = []
    for case in cases:
        result = _run_once(case, runtime, timeout, skill_dir, True)
        result["partition"] = case["partition"]
        results.append(result)
        if case.get("paired"):
            baseline = _run_once(case, runtime, timeout, skill_dir, False)
            baseline["partition"] = case["partition"]
            results.append(baseline)
    routing_ids = {case["id"] for case in cases if case["kind"] == "routing"}
    routing = _routing_metrics([item for item in results if item["condition"] == "with_skill" and item["case_id"] in routing_ids], cases)
    paired = []
    for case in cases:
        if not case.get("paired"):
            continue
        pair = [item for item in results if item["case_id"] == case["id"]]
        with_skill = next((item for item in pair if item["condition"] == "with_skill"), None)
        without_skill = next((item for item in pair if item["condition"] == "without_skill"), None)
        paired.append({
            "case_id": case["id"],
            "with_status": with_skill.get("status") if with_skill else "NOT_ASSESSED",
            "without_status": without_skill.get("status") if without_skill else "NOT_ASSESSED",
            "with_runtime_observed": bool(with_skill and with_skill.get("runtime_observed")),
            "without_runtime_observed": bool(without_skill and without_skill.get("runtime_observed")),
            "with_process_observed": bool(with_skill and with_skill.get("process_observed")),
            "behavior_delta_observed": bool(with_skill and without_skill and with_skill.get("observed") != without_skill.get("observed")),
            "cost_observed": bool(with_skill and without_skill and with_skill.get("elapsed_seconds") is not None and without_skill.get("elapsed_seconds") is not None and with_skill.get("stdout_bytes") is not None and without_skill.get("stdout_bytes") is not None),
            "added_value_observed": bool(
                with_skill and with_skill.get("status") == "PASS"
                and with_skill.get("process_observed")
                and without_skill and without_skill.get("status") == "OBSERVED"
                and with_skill.get("observed") != without_skill.get("observed")
                and with_skill.get("elapsed_seconds") is not None
                and without_skill.get("elapsed_seconds") is not None
                and with_skill.get("stdout_bytes") is not None
                and without_skill.get("stdout_bytes") is not None
            ),
        })
    structure_check = subprocess.run(
        [sys.executable, str(skill_dir / "scripts" / "quick_validate.py"), str(skill_dir)],
        capture_output=True, text=True, check=False,
    )
    provenance_text = (skill_dir / "references" / "provenance.md").read_text(encoding="utf-8") if (skill_dir / "references" / "provenance.md").is_file() else ""
    provenance_ok = all(marker in provenance_text for marker in ("openai/codex", "Source path:", "License:"))
    behavior_cases = [case for case in cases if case["kind"] != "routing"]
    behavior_results = [item for item in results if item["condition"] == "with_skill" and item["case_id"] in {case["id"] for case in behavior_cases}]
    coexistence_cases = {"maintain-overlap", "evaluate-sibling-collision"}
    coexistence_results = [item for item in behavior_results if item["case_id"] in coexistence_cases]
    full_corpus = len(cases) == len(data["cases"])
    paired_complete = len(paired) == sum(case.get("paired") is True for case in cases)
    status_by_gate = {
        "G1_STRUCTURE": "PASS" if structure_check.returncode == 0 else "FAIL",
        "G2_PROVENANCE": "PASS" if provenance_ok else "FAIL",
        "G3_ROUTING": routing["status"],
        "G4_BEHAVIOR": "PASS" if full_corpus and behavior_cases and len(behavior_results) == len(behavior_cases) and all(item["status"] == "PASS" for item in behavior_results) else "NOT_ASSESSED",
        "G5_COEXISTENCE": "PASS" if full_corpus and len(coexistence_results) == len(coexistence_cases) and all(item["status"] == "PASS" for item in coexistence_results) else "NOT_ASSESSED",
        "G6_EFFICIENCY": "PASS" if full_corpus and paired_complete and paired and all(item["added_value_observed"] for item in paired) else "NOT_ASSESSED",
        "G7_INDEPENDENT_REVIEW": _independent_review_status(review_status, review_evidence, skill_dir),
    }
    return {
        "schema_version": 2,
        "skill": "skill-creator",
        "coverage": {"requested_cases": len(cases), "total_cases": len(data["cases"]), "full_corpus": len(cases) == len(data["cases"])},
        "gates": status_by_gate,
        "routing": routing,
        "paired": paired,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", type=Path)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--skill-dir", type=Path, default=Path(__file__).parents[1])
    parser.add_argument("--case-id", action="append")
    parser.add_argument("--runtime", default="codex")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--review-status", choices=("PASS", "NOT_ASSESSED"), default="NOT_ASSESSED")
    parser.add_argument("--review-evidence", type=Path)
    parser.add_argument("--results", type=Path)
    parser.add_argument("--compare-before", type=Path)
    parser.add_argument("--compare-after", type=Path)
    args = parser.parse_args()
    errors = validate(args.cases)
    if errors:
        for error in errors:
            print(f"FAIL eval cases: {error}")
        return 1
    if args.compare_before and args.compare_after:
        report = _compare(args.compare_before, args.compare_after)
        print(json.dumps(report, sort_keys=True))
        return 0 if report["status"] == "PASS" else 1
    if not args.run:
        data = load_cases(args.cases)
        print(f"OK eval cases: {len(data['gates'])} gates, {sum(case['kind'] == 'routing' for case in data['cases'])} routing and {sum(case['kind'] != 'routing' for case in data['cases'])} lifecycle cases")
        return 0
    report = run(args.cases, args.skill_dir, args.runtime, args.timeout, set(args.case_id) if args.case_id else None, args.review_status, args.review_evidence)
    if args.results:
        args.results.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 1 if any(status == "FAIL" for status in report["gates"].values()) else (2 if any(status == "NOT_ASSESSED" for status in report["gates"].values()) else 0)


if __name__ == "__main__":
    sys.exit(main())
