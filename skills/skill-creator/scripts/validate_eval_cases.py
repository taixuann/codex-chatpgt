#!/usr/bin/env python3
"""Validate and run the bounded skill-creator evaluation contract."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
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
EXPECTED_CASE_COUNT = 26
EXPECTED_ROUTING_CASE_COUNT = 12
EXPECTED_LIFECYCLE_CASE_COUNT = 14
EXPECTED_PARTITIONS = {
    "must_pass": frozenset({
        "route-explicit-positive", "route-implicit-positive", "route-contextual-positive",
        "route-explicit-negative", "route-adjacent-negative", "route-sibling-negative",
        "create-local-upstream", "create-multimode-one-skill", "update-bounded", "evaluate-good",
    }),
    "regression": frozenset({
        "create-no-skill", "update-substantive", "maintain-upstream-drift", "maintain-retire",
        "evaluate-broad-description", "evaluate-decorative-resources",
    }),
    "held_out": frozenset({
        "route-ambiguous-positive", "route-noisy-positive", "route-agents-negative",
        "route-script-negative", "route-native-negative", "route-noisy-negative",
        "maintain-overlap", "maintain-localize", "evaluate-sibling-collision", "evaluate-skipped-process",
    }),
}
EXPECTED_CASE_IDS = frozenset().union(*EXPECTED_PARTITIONS.values())
EXPECTED_FILES = {
    "SKILL.md", "license.txt", "evals/cases.yaml",
    "references/create.md", "references/evaluate.md", "references/maintain.md",
    "references/provenance.md", "references/routing.md", "references/update.md",
    "scripts/generate_openai_yaml.py", "scripts/init_skill.py", "scripts/quick_validate.py",
    "scripts/test_validate_eval_cases.py", "scripts/validate_eval_cases.py",
}
UPSTREAM_MARKERS = (
    "Repository: `openai/codex`",
    "Ref: `dee21ec1bc26cdf9f3c4d77a17706cd19dcf05de`",
    "Source path: `codex-rs/skills/src/assets/samples/skill-creator/`",
    "License: Apache-2.0",
    "Baseline commit: `bb288fd`",
    "`scripts/generate_openai_yaml.py`, `870eefcea9bd0184806b8eb305526e883d2f7241`",
    "`scripts/init_skill.py`, `2ed2fa3125c720fcce60a29f3dd82d04b14d9fa0`",
    "`scripts/quick_validate.py`, `e27023ece4bd259ef36560e19995eec7b6a345bf`",
    "`license.txt`, `d645695673349e3947e8e5ae42332d0ac3164cd7`",
)


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
        case_gates = case.get("gates", [case.get("gate")])
        if not isinstance(case_gates, list) or not case_gates or any(gate not in GATES for gate in case_gates):
            errors.append(f"{case_id}: gates must contain only known gate ids")
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            errors.append(f"{case_id}: prompt is required")
        if not isinstance(case.get("expected"), str) or not case["expected"].strip():
            errors.append(f"{case_id}: expected outcome is required")
        if case.get("kind") == "routing" and case.get("polarity") not in {"positive", "negative"}:
            errors.append(f"{case_id}: routing polarity must be positive or negative")
        if case.get("kind") != "routing" and not isinstance(case.get("trace_markers"), list):
            errors.append(f"{case_id}: lifecycle cases require trace_markers")
    routing = [case for case in cases if isinstance(case, dict) and case.get("kind") == "routing"]
    if seen != EXPECTED_CASE_IDS:
        errors.append("case ids must match the canonical 26-case corpus")
    for partition, expected_ids in EXPECTED_PARTITIONS.items():
        actual_ids = {case.get("id") for case in cases if isinstance(case, dict) and case.get("partition") == partition}
        if actual_ids != expected_ids:
            errors.append(f"{partition} partition does not match the canonical corpus")
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


def _runtime_activation(events: list[dict]) -> str | None:
    """Return loaded/unloaded only from an explicit structured activation event."""
    for event in events:
        for key in ("skill_loads", "loaded_skills", "loaded_skill"):
            if key not in event:
                continue
            value = event[key]
            if isinstance(value, list) and any("skill-creator" in json.dumps(item) for item in value):
                return "loaded"
            if isinstance(value, list) and not value:
                return "unloaded"
            if isinstance(value, str) and value.lower() in {"none", "unloaded"}:
                return "unloaded"
            if isinstance(value, dict) and value.get("status") in {"none", "unloaded"}:
                return "unloaded"
    return None


def _process_observed(events: list[dict]) -> bool:
    """Require an execution/tool trace before claiming behavioral evidence."""
    for event in events:
        item = event.get("item")
        item_type = item.get("type") if isinstance(item, dict) else event.get("type")
        if item_type in PROCESS_ITEM_TYPES:
            return True
    return False


def _trace_matches(case: dict, events: list[dict]) -> bool:
    for marker in case.get("trace_markers", []):
        if not any(marker.lower() in _process_payload(event) for event in events):
            return False
    return True


def _process_payload(event: dict) -> str:
    item = event.get("item") if isinstance(event.get("item"), dict) else event
    item_type = item.get("type") if isinstance(item, dict) else None
    if item_type not in PROCESS_ITEM_TYPES:
        return ""
    fields = {key: item.get(key) for key in ("command", "name", "arguments", "input", "call_id", "tool", "function", "output") if key in item}
    return json.dumps(fields, sort_keys=True).lower()


def _process_events(events: list[dict]) -> list[dict]:
    return [event for event in events if _process_payload(event)]


def _usage_tokens(events: list[dict]) -> int | None:
    total = 0
    observed = False
    for event in events:
        usage = event.get("usage")
        if not isinstance(usage, dict):
            response = event.get("response")
            usage = response.get("usage") if isinstance(response, dict) else None
        if not isinstance(usage, dict):
            continue
        values = [usage.get(key) for key in ("total_tokens", "input_tokens", "output_tokens")]
        numbers = [value for value in values if isinstance(value, int)]
        if numbers:
            observed = True
            total += usage.get("total_tokens") if isinstance(usage.get("total_tokens"), int) else sum(numbers)
    return total if observed else None


def _cost_metrics(events: list[dict], changed_paths: set[str]) -> dict:
    process_events = _process_events(events)
    commands = sum(
        1 for event in process_events
        if (event.get("item", event).get("type") if isinstance(event.get("item", event), dict) else None) == "command_execution"
    )
    tokens = _usage_tokens(events)
    return {
        "tool_calls": len(process_events),
        "command_count": commands,
        "token_count": tokens,
        "artifact_count": len(changed_paths),
        "tokens_observed": tokens is not None,
    }


def _snapshot(root: Path) -> dict[str, str]:
    files = {}
    for path in root.rglob("*"):
        if path.is_file():
            relative = path.relative_to(root)
            if ".codex-home" in relative.parts:
                continue
            files[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def _changed_paths(before: dict[str, str], after: dict[str, str]) -> set[str]:
    return {path for path in set(before) | set(after) if before.get(path) != after.get(path)}


def _package_structure_ok(skill_dir: Path) -> bool:
    files = {
        path.relative_to(skill_dir).as_posix()
        for path in skill_dir.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    if files != EXPECTED_FILES:
        return False
    markdown = "\n".join(path.read_text(encoding="utf-8") for path in skill_dir.rglob("*.md"))
    links = re.findall(r"\]\(([^)#]+)", markdown)
    if any(link.startswith(("/", "file:")) for link in links):
        return False
    if any(not (skill_dir / link).is_file() for link in links if not link.startswith(("http:", "https:"))):
        return False
    if any(marker in markdown for marker in ("TODO", "TBD", "<path/to/", "<skill-name>")):
        return False
    return all((skill_dir / path).stat().st_size > 0 for path in files)


def _provenance_ok(skill_dir: Path) -> bool:
    path = skill_dir / "references" / "provenance.md"
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    return all(marker in text for marker in UPSTREAM_MARKERS)


def _cost(result: dict | None) -> dict | None:
    metrics = result.get("cost_metrics") if result else None
    if not isinstance(metrics, dict):
        return None
    return {key: metrics.get(key) for key in ("tool_calls", "command_count", "token_count", "artifact_count")}


def _paired_evidence(with_skill: dict | None, without_skill: dict | None) -> dict:
    with_cost = _cost(with_skill)
    without_cost = _cost(without_skill)
    required_cost = ("tool_calls", "command_count", "artifact_count")
    cost_delta = (
        {key: with_cost[key] - without_cost[key] for key in with_cost if isinstance(with_cost[key], int) and isinstance(without_cost[key], int)}
        if with_cost is not None and without_cost is not None else None
    )
    cost_comparison_observed = bool(
        with_cost is not None and without_cost is not None
        and all(isinstance(with_cost[key], int) and isinstance(without_cost[key], int) for key in required_cost)
    )
    artifact_delta_observed = bool(
        with_skill and without_skill
        and with_skill.get("changed_paths") != without_skill.get("changed_paths")
    )
    outcome_delta_observed = bool(
        with_skill and without_skill
        and (with_skill.get("observed") != without_skill.get("observed") or artifact_delta_observed)
    )
    added_value_observed = bool(
        with_skill and with_skill.get("status") == "PASS"
        and with_skill.get("process_observed") and with_skill.get("trace_matches") and with_skill.get("artifact_ok")
        and without_skill and without_skill.get("status") == "OBSERVED"
        and without_skill.get("process_observed") and without_skill.get("trace_matches") and without_skill.get("artifact_ok")
        and cost_comparison_observed and outcome_delta_observed
    )
    return {
        "behavior_delta_observed": bool(with_skill and without_skill and with_skill.get("observed") != without_skill.get("observed")),
        "artifact_delta_observed": artifact_delta_observed,
        "outcome_delta_observed": outcome_delta_observed,
        "cost_observed": with_cost is not None and without_cost is not None,
        "cost_delta": cost_delta,
        "cost_comparison_observed": cost_comparison_observed,
        "added_value_observed": added_value_observed,
    }


def _artifact_contract(case: dict) -> dict:
    if case["id"] == "create-no-skill":
        return {}
    if case.get("artifact") and case.get("artifact_path"):
        return {"operation": case["artifact"], "path": case["artifact_path"]}
    if case.get("kind") != "routing":
        return {"operation": "created", "path": f".evaluation/{case['id']}.json"}
    return {}


def _case_gates(case: dict) -> list[str]:
    return case.get("gates", [case["gate"]])


def _artifact_ok(case: dict, before: dict[str, str], after: dict[str, str]) -> tuple[bool, str]:
    contract = _artifact_contract(case)
    if not contract:
        return True, "no artifact required"
    path = contract["path"]
    operation = contract["operation"]
    exists_before = path in before
    exists_after = path in after
    if operation == "created":
        return (not exists_before and exists_after, f"expected created artifact {path}")
    if operation == "modified":
        return (exists_before and exists_after and before[path] != after[path], f"expected modified artifact {path}")
    if operation == "deleted":
        return (exists_before and not exists_after, f"expected deleted artifact {path}")
    return False, f"unknown artifact operation {operation}"


def _seed_case(fixture_root: Path, case: dict) -> None:
    skills_root = fixture_root / ".agents" / "skills"
    case_id = case["id"]
    if case_id in {"update-bounded", "update-substantive", "maintain-upstream-drift"}:
        target = skills_root / "existing-skill"
        (target / "references").mkdir(parents=True, exist_ok=True)
        (target / "SKILL.md").write_text(
            "---\nname: existing-skill\ndescription: Existing bounded skill.\n---\n\nBefore version.\n",
            encoding="utf-8",
        )
        (target / "references" / "provenance.md").write_text(
            "Pinned upstream baseline: old-ref\n",
            encoding="utf-8",
        )
    elif case_id == "maintain-overlap":
        target = skills_root / "overlap-skill"
        target.mkdir(parents=True, exist_ok=True)
        (target / "SKILL.md").write_text(
            "---\nname: overlap-skill\ndescription: Rotate and inspect PDF files.\n---\n\nOverlapping workflow.\n",
            encoding="utf-8",
        )
    elif case_id == "maintain-retire":
        target = skills_root / "stale-skill"
        target.mkdir(parents=True, exist_ok=True)
        (target / "SKILL.md").write_text(
            "---\nname: stale-skill\ndescription: Stale redundant workflow.\n---\n\nRetire me.\n",
            encoding="utf-8",
        )
    elif case_id.startswith("evaluate-"):
        target = skills_root / "candidate-skill"
        target.mkdir(parents=True, exist_ok=True)
        (target / "SKILL.md").write_text(
            "---\nname: candidate-skill\ndescription: Candidate evaluation fixture.\n---\n\nCandidate content.\n",
            encoding="utf-8",
        )


@contextmanager
def _fixture(skill_dir: Path, with_skill: bool, case: dict | None = None) -> Iterator[Path]:
    with tempfile.TemporaryDirectory(prefix="skill-creator-eval-") as directory:
        root = Path(directory)
        (root / ".codex-home").mkdir()
        (root / "AGENTS.md").write_text(
            "# Isolated skill evaluation\n\nUse available skills only when the request matches their description.\n",
            encoding="utf-8",
        )
        fixture_root = root / "project" if case and case["id"] == "maintain-localize" else root
        if case and case["id"] == "maintain-localize":
            fixture_root.mkdir(parents=True, exist_ok=True)
        if with_skill:
            target = fixture_root / ".agents" / "skills" / "skill-creator"
            shutil.copytree(skill_dir, target, ignore=shutil.ignore_patterns("__pycache__"))
        if case and case["id"] in {"maintain-overlap", "maintain-localize", "evaluate-sibling-collision"}:
            sibling = fixture_root / ".agents" / "skills" / "pdf"
            sibling.mkdir(parents=True, exist_ok=True)
            (sibling / "SKILL.md").write_text(
                "---\nname: pdf\ndescription: Rotate and inspect PDF files.\n---\n\nUse the PDF workflow.\n",
                encoding="utf-8",
            )
            if case["id"] == "maintain-localize":
                local = fixture_root / ".agents" / "skills" / "domain-workflow"
                local.mkdir(parents=True, exist_ok=True)
                (local / "SKILL.md").write_text(
                    "---\nname: domain-workflow\ndescription: Repository-local domain workflow.\n---\n\nUse the local workflow.\n",
                    encoding="utf-8",
                )
            (fixture_root / ".fixture-coexistence").write_text("true\n", encoding="utf-8")
        if case:
            _seed_case(fixture_root, case)
        yield root


def _run_once(case: dict, runtime: str, timeout: int, skill_dir: Path, with_skill: bool) -> dict:
    with _fixture(skill_dir, with_skill, case) as fixture:
        operation_root = fixture / "project" if case["id"] == "maintain-localize" else fixture
        artifact = _artifact_contract(case)
        if case["kind"] == "routing":
            prompt = (
                "Handle this natural user request in the isolated fixture. Do not change files. "
                "Return exactly one JSON object with key selected_skill, whose value is the selected "
                "skill name or none.\n\n"
                f"{case['prompt']}"
            )
        else:
            artifact_instruction = (
                f"The required observable artifact is {artifact['operation']} at "
                f"{artifact['path']}. Perform the operation, not just a plan. "
            )
            prompt = (
                "Complete this natural user request in the isolated fixture using available instructions "
                "and tools. You may modify only the fixture. Return exactly one JSON object with keys "
                "disposition, artifacts, and process. The artifacts value lists changed relative paths; "
                "the process value lists the concrete steps performed. "
                f"{artifact_instruction}\n\n{case['prompt']}"
            )
        base = {
            "case_id": case["id"],
            "kind": case["kind"],
            "expected": case["expected"],
            "condition": "with_skill" if with_skill else "without_skill",
            "fixture": ("project/.agents/skills/skill-creator" if case["id"] == "maintain-localize" else ".agents/skills/skill-creator") if with_skill else "no skill fixture",
        }
        if not shutil.which(runtime):
            return {**base, "status": "NOT_ASSESSED", "reason": f"runtime not found: {runtime}"}
        sandbox = "read-only" if case["kind"] == "routing" else "workspace-write"
        command = [
            runtime, "exec", "--json", "--ephemeral", "--sandbox", sandbox,
            "--skip-git-repo-check", "--ignore-user-config", "--cd",
            str(fixture / "project" if case["id"] == "maintain-localize" else fixture), prompt,
        ]
        environment = os.environ.copy()
        environment["CODEX_HOME"] = str(fixture / ".codex-home")
        before_snapshot = _snapshot(operation_root)
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
        activation = _runtime_activation(events)
        loaded = activation == "loaded"
        process_observed = _process_observed(events)
        trace_matches = _trace_matches(case, events)
        after_snapshot = _snapshot(operation_root)
        changed_paths = _changed_paths(before_snapshot, after_snapshot)
        artifact_ok, artifact_reason = _artifact_ok(case, before_snapshot, after_snapshot)
        side_effect_free = not changed_paths
        unavailable = any(
            marker in (process.stderr or "").lower()
            for marker in ("401 unauthorized", "missing bearer", "authentication")
        )
        if process.returncode != 0 and (not events or unavailable):
            status, reason = "NOT_ASSESSED", f"runtime exit {process.returncode}"
        elif process.returncode != 0:
            status, reason = "FAIL", f"runtime exit {process.returncode}"
        elif not with_skill:
            if observed is None or not process_observed:
                status, reason = "NOT_ASSESSED", "baseline outcome or process evidence was not observed"
            elif case["kind"] != "routing" and not artifact_ok:
                status, reason = "NOT_ASSESSED", artifact_reason
            else:
                status, reason = "OBSERVED", "baseline output and evidence recorded without skill fixture"
        elif case["kind"] == "routing" and case["expected"] == "none" and activation == "unloaded" and observed == "none":
            status, reason = "PASS", "explicit runtime non-activation and expected outcome observed"
        elif case["kind"] == "routing" and case["expected"] == "none" and activation == "loaded":
            status, reason = "FAIL", "skill activated for an explicit negative request"
        elif case["kind"] == "routing" and activation is None:
            status, reason = "NOT_ASSESSED", "runtime did not expose an explicit non-activation signal"
        elif activation is None:
            status, reason = "NOT_ASSESSED", "runtime did not expose a skill-load signal"
        elif observed != case["expected"]:
            status, reason = "FAIL", f"expected {case['expected']}, observed {observed!r}"
        elif case["kind"] != "routing" and not (process_observed and trace_matches and artifact_ok):
            status, reason = "FAIL", artifact_reason if not artifact_ok else "required process trace was not observed"
        elif observed == case["expected"]:
            status, reason = "PASS", "expected outcome, process trace, and artifact evidence observed"
        else:
            status, reason = "NOT_ASSESSED", "runtime outcome unavailable"
        cost_metrics = _cost_metrics(events, changed_paths)
        return {
            **base,
            "status": status,
            "observed": observed,
            "runtime_observed": loaded,
            "activation": activation,
            "process_observed": process_observed,
            "trace_matches": trace_matches,
            "side_effect_free": side_effect_free,
            "coexistence_fixture": (((fixture / "project") if case["id"] == "maintain-localize" else fixture) / ".fixture-coexistence").is_file(),
            "artifact_ok": artifact_ok,
            "artifact_reason": artifact_reason,
            "changed_paths": sorted(changed_paths),
            "cost_metrics": cost_metrics,
            "events": len(events),
            "returncode": process.returncode,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "stdout_bytes": len(stdout.encode("utf-8")),
            "reason": reason,
            "stderr": (process.stderr or "").splitlines()[-5:],
        }


def _routing_metrics(results: list[dict], cases: list[dict]) -> dict:
    by_id = {case["id"]: case for case in cases}
    assessed = [result for result in results if result.get("status") in {"PASS", "FAIL"} and result.get("observed") is not None]
    tp = sum(by_id[result["case_id"]].get("polarity") == "positive" for result in assessed if result.get("observed") == "skill-creator")
    fn = sum(by_id[result["case_id"]].get("polarity") == "positive" for result in assessed if result.get("observed") != "skill-creator")
    fp = sum(by_id[result["case_id"]].get("polarity") == "negative" for result in assessed if result.get("observed") == "skill-creator")
    tn = sum(by_id[result["case_id"]].get("polarity") == "negative" for result in assessed if result.get("observed") != "skill-creator")
    denominator_precision = tp + fp
    denominator_recall = tp + fn
    expected_cases = [case for case in cases if case.get("kind") == "routing"]
    complete = len(results) == len(expected_cases) and bool(results)
    status = "PASS" if complete and len(assessed) == len(results) and not any(item.get("status") == "FAIL" for item in results) else (
        "FAIL" if any(item.get("status") == "FAIL" for item in results) else "NOT_ASSESSED"
    )
    return {
        "status": status,
        "TP": tp, "FN": fn, "FP": fp, "TN": tn,
        "precision": round(tp / denominator_precision, 3) if denominator_precision else None,
        "recall": round(tp / denominator_recall, 3) if denominator_recall else None,
        "false_positive_rate": round(fp / (fp + tn), 3) if fp + tn else None,
        "assessed_cases": len(assessed),
        "total_cases": len(results),
    }


def _case_gate_status(results: list[dict], gate: str) -> str:
    owned = [item for item in results if item.get("condition") == "with_skill" and gate in item.get("gates", [item.get("gate")])]
    if not owned:
        return "NOT_ASSESSED"
    if any(item.get("status") == "FAIL" for item in owned):
        return "FAIL"
    return "PASS" if all(item.get("status") == "PASS" for item in owned) else "NOT_ASSESSED"


def _compare(before_path: Path, after_path: Path, cases_path: Path | None = None) -> dict:
    try:
        before = json.loads(before_path.read_text(encoding="utf-8"))
        after = json.loads(after_path.read_text(encoding="utf-8"))
        expected_cases = load_cases(cases_path).get("cases", []) if cases_path else []
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        return {"status": "REJECT", "validation_gated": False, "reason": "invalid before/after/case evidence"}
    def with_skill(data: dict) -> list[dict]:
        return [item for item in data.get("results", []) if item.get("condition") == "with_skill"]

    def without_skill(data: dict) -> list[dict]:
        return [item for item in data.get("results", []) if item.get("condition") == "without_skill"]

    def evidence_complete(data: dict, results: list[dict], baseline_results: list[dict]) -> bool:
        coverage = data.get("coverage", {})
        gates = data.get("gates", {})
        routing = data.get("routing", {})
        cases_by_id = {case["id"]: case for case in expected_cases}
        if coverage.get("full_corpus") is not True or set(gates) != set(GATES):
            return False
        if any(gates.get(gate) not in {"PASS", "FAIL", "NOT_ASSESSED"} for gate in GATES):
            return False
        if gates.get("G7_INDEPENDENT_REVIEW") != "NOT_ASSESSED":
            return False
        if any(gates.get(gate) != "PASS" for gate in GATES if gate != "G7_INDEPENDENT_REVIEW"):
            return False
        if routing.get("status") not in {"PASS", "FAIL"} or not all(
            isinstance(routing.get(field), (int, float)) for field in ("precision", "recall")
        ):
            return False
        routing_results = [item for item in results if item.get("kind") == "routing"]
        expected_routing_status = "FAIL" if any(item.get("status") == "FAIL" for item in routing_results) else "PASS"
        if routing.get("status") != expected_routing_status or gates.get("G3_ROUTING") != routing.get("status"):
            return False
        expected_paired = {case["id"] for case in expected_cases if case.get("paired") is True}
        paired = data.get("paired")
        if not isinstance(paired, list) or {item.get("case_id") for item in paired} != expected_paired:
            return False
        if gates.get("G6_EFFICIENCY") != "PASS" or any(
            item.get("added_value_observed") is not True
            or item.get("cost_comparison_observed") is not True
            or item.get("outcome_delta_observed") is not True
            for item in paired
        ):
            return False
        paired_cases = {case["id"]: case for case in expected_cases if case.get("paired") is True}
        baseline_by_case = {item.get("case_id"): item for item in baseline_results}
        with_by_case = {item.get("case_id"): item for item in results}
        for item in results + baseline_results:
            case = cases_by_id.get(item.get("case_id"))
            if not case or any(
                item.get(field) != expected
                for field, expected in (
                    ("kind", case["kind"]),
                    ("expected", case["expected"]),
                    ("partition", case["partition"]),
                    ("gate", case["gate"]),
                    ("gates", _case_gates(case)),
                )
            ):
                return False
        if set(baseline_by_case) != set(paired_cases) or len(baseline_results) != len(paired_cases):
            return False
        for case_id in paired_cases:
            baseline = baseline_by_case[case_id]
            if (
                baseline.get("status") != "OBSERVED"
                or baseline.get("observed") is None
                or not all(baseline.get(field) is True for field in ("process_observed", "trace_matches", "artifact_ok"))
            ):
                return False
            metrics = baseline.get("cost_metrics")
            if not isinstance(metrics, dict) or not all(isinstance(metrics.get(field), int) for field in ("tool_calls", "command_count", "artifact_count")):
                return False
            recomputed = _paired_evidence(with_by_case.get(case_id), baseline)
            summary = next(item for item in paired if item.get("case_id") == case_id)
            if any(summary.get(field) != recomputed.get(field) for field in recomputed):
                return False
        for item in results:
            case = cases_by_id[item["case_id"]]
            if item.get("status") != "PASS" or item.get("observed") != case["expected"]:
                return False
            activation = item.get("activation")
            if item.get("kind", "routing") == "routing":
                if activation not in {"loaded", "unloaded"}:
                    return False
                continue
            if activation != "loaded" or not all(item.get(field) is True for field in ("process_observed", "trace_matches", "artifact_ok")):
                return False
            metrics = item.get("cost_metrics")
            if not isinstance(metrics, dict) or not all(isinstance(metrics.get(field), int) for field in ("tool_calls", "command_count", "artifact_count")):
                return False
        for gate in GATES - {"G6_EFFICIENCY", "G7_INDEPENDENT_REVIEW"}:
            if _case_gate_status(results, gate) != gates.get(gate):
                return False
        return True

    before_results = with_skill(before)
    after_results = with_skill(after)
    before_baseline = without_skill(before)
    after_baseline = without_skill(after)
    before_keys = {(item.get("case_id"), item.get("partition")) for item in before_results}
    after_keys = {(item.get("case_id"), item.get("partition")) for item in after_results}
    expected_keys = {(case["id"], case["partition"]) for case in expected_cases}
    canonical_keys = {(case_id, partition) for partition, case_ids in EXPECTED_PARTITIONS.items() for case_id in case_ids}
    expected_baseline_keys = {(case["id"], case["partition"]) for case in expected_cases if case.get("paired") is True}
    before_baseline_keys = {(item.get("case_id"), item.get("partition")) for item in before_baseline}
    after_baseline_keys = {(item.get("case_id"), item.get("partition")) for item in after_baseline}
    statuses = {"PASS", "FAIL"}
    comparable = (
        len(expected_cases) == EXPECTED_CASE_COUNT
        and sum(case.get("kind") == "routing" for case in expected_cases) == EXPECTED_ROUTING_CASE_COUNT
        and sum(case.get("kind") != "routing" for case in expected_cases) == EXPECTED_LIFECYCLE_CASE_COUNT
        and expected_keys == canonical_keys
        and bool(before_results)
        and before_keys == after_keys
        and before_keys == expected_keys
        and len(before_results) == len(expected_keys)
        and len(after_results) == len(expected_keys)
        and before_baseline_keys == after_baseline_keys == expected_baseline_keys
        and len(before_baseline) == len(expected_baseline_keys)
        and len(after_baseline) == len(expected_baseline_keys)
        and all(item.get("status") in statuses for item in before_results + after_results)
        and evidence_complete(before, before_results, before_baseline)
        and evidence_complete(after, after_results, after_baseline)
    )

    def score(results: list[dict], partition: str, status: str = "PASS") -> int:
        return sum(item.get("status") == status and item.get("partition") == partition for item in results)

    before_held = score(before_results, "held_out")
    after_held = score(after_results, "held_out")
    before_regression = score(before_results, "regression", "FAIL")
    after_regression = score(after_results, "regression", "FAIL")
    before_must_pass_failures = sum(item.get("partition") == "must_pass" and item.get("status") != "PASS" for item in before_results)
    after_must_pass_failures = sum(item.get("partition") == "must_pass" and item.get("status") != "PASS" for item in after_results)
    before_by_case = {item.get("case_id"): item for item in before_results}
    after_by_case = {item.get("case_id"): item for item in after_results}
    case_deltas = [
        {
            "case_id": case_id,
            "before_status": before_by_case[case_id].get("status"),
            "after_status": after_by_case[case_id].get("status"),
            "before_observed": before_by_case[case_id].get("observed"),
            "after_observed": after_by_case[case_id].get("observed"),
            "before_changed_paths": before_by_case[case_id].get("changed_paths", []),
            "after_changed_paths": after_by_case[case_id].get("changed_paths", []),
            "status_changed": before_by_case[case_id].get("status") != after_by_case[case_id].get("status"),
        }
        for case_id in sorted(before_by_case)
    ]
    before_routing = before.get("routing", {})
    after_routing = after.get("routing", {})
    routing_comparable = all(
        isinstance(payload.get(field), (int, float))
        for payload in (before_routing, after_routing)
        for field in ("precision", "recall")
    )
    routing_non_regressing = routing_comparable and (
        after_routing["precision"] >= before_routing["precision"]
        and after_routing["recall"] >= before_routing["recall"]
    )
    return {
        "status": "PASS" if comparable and before_must_pass_failures == 0 and after_must_pass_failures == 0 and after_held > 0 and after_held >= before_held and after_regression <= before_regression and routing_non_regressing else "REJECT",
        "held_out_before": before_held,
        "held_out_after": after_held,
        "regression_failures_before": before_regression,
        "regression_failures_after": after_regression,
        "must_pass_failures_before": before_must_pass_failures,
        "must_pass_failures_after": after_must_pass_failures,
        "routing_precision_before": before_routing.get("precision"),
        "routing_precision_after": after_routing.get("precision"),
        "routing_recall_before": before_routing.get("recall"),
        "routing_recall_after": after_routing.get("recall"),
        "case_deltas": case_deltas,
        "validation_gated": comparable,
    }


def run(path: Path, skill_dir: Path, runtime: str, timeout: int, case_ids: set[str] | None) -> dict:
    data = load_cases(path)
    cases = [case for case in data["cases"] if not case_ids or case["id"] in case_ids]
    results = []
    for case in cases:
        result = _run_once(case, runtime, timeout, skill_dir, True)
        result["partition"] = case["partition"]
        result["gate"] = case["gate"]
        result["gates"] = _case_gates(case)
        results.append(result)
        if case.get("paired"):
            baseline = _run_once(case, runtime, timeout, skill_dir, False)
            baseline["partition"] = case["partition"]
            baseline["gate"] = case["gate"]
            baseline["gates"] = _case_gates(case)
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
            "without_process_observed": bool(without_skill and without_skill.get("process_observed")),
            **_paired_evidence(with_skill, without_skill),
        })
    structure_check = subprocess.run(
        [sys.executable, str(skill_dir / "scripts" / "quick_validate.py"), str(skill_dir)],
        capture_output=True, text=True, check=False,
    )
    structure_ok = structure_check.returncode == 0 and _package_structure_ok(skill_dir)
    provenance_ok = _provenance_ok(skill_dir)
    behavior_cases = [case for case in cases if case["kind"] != "routing"]
    behavior_results = [item for item in results if item["condition"] == "with_skill" and item["case_id"] in {case["id"] for case in behavior_cases}]
    paired_by_id = {item["case_id"]: item for item in paired}
    full_corpus = len(cases) == len(data["cases"])
    paired_complete = len(paired) == sum(case.get("paired") is True for case in cases)
    status_by_gate = {gate: _case_gate_status(results, gate) for gate in GATES}
    status_by_gate["G1_STRUCTURE"] = "FAIL" if not structure_ok else status_by_gate["G1_STRUCTURE"]
    status_by_gate["G2_PROVENANCE"] = "FAIL" if not provenance_ok else status_by_gate["G2_PROVENANCE"]
    status_by_gate["G3_ROUTING"] = routing["status"]
    if not full_corpus:
        for gate in GATES - {"G7_INDEPENDENT_REVIEW"}:
            if status_by_gate[gate] == "PASS":
                status_by_gate[gate] = "NOT_ASSESSED"
    efficiency_cases = [case for case in cases if "G6_EFFICIENCY" in _case_gates(case)]
    efficiency_pairs = [paired_by_id[case["id"]] for case in efficiency_cases if case.get("paired") and case["id"] in paired_by_id]
    status_by_gate["G6_EFFICIENCY"] = (
        "FAIL" if any(item.get("with_status") == "FAIL" for item in efficiency_pairs)
        else "PASS" if full_corpus and efficiency_pairs and len(efficiency_pairs) == len(efficiency_cases)
        and all(item["added_value_observed"] for item in efficiency_pairs)
        else "NOT_ASSESSED"
    )
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
        report = _compare(args.compare_before, args.compare_after, args.cases)
        print(json.dumps(report, sort_keys=True))
        return 0 if report["status"] == "PASS" else 1
    if not args.run:
        data = load_cases(args.cases)
        print(f"OK eval cases: {len(data['gates'])} gates, {sum(case['kind'] == 'routing' for case in data['cases'])} routing and {sum(case['kind'] != 'routing' for case in data['cases'])} lifecycle cases")
        return 0
    report = run(args.cases, args.skill_dir, args.runtime, args.timeout, set(args.case_id) if args.case_id else None)
    if args.results:
        args.results.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 1 if any(status == "FAIL" for status in report["gates"].values()) else (2 if any(status == "NOT_ASSESSED" for status in report["gates"].values()) else 0)


if __name__ == "__main__":
    sys.exit(main())
