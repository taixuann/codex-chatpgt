#!/usr/bin/env python3
"""Run repository quality gates against one skill package.

Structural and security failures block a package. Evaluation and review-age
metadata are advisory so existing skills remain compatible while gaining a
path to stronger maintenance evidence.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml


SECRET_PATTERNS = [
    re.compile(r"\b(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-/+=]{12,}"),
]
DANGEROUS_PATTERNS = [
    re.compile(r"\b(?:curl|wget)\b[^\n|]*\|\s*(?:ba)?sh\b"),
    re.compile(r"\brm\s+-rf\s+(?:/|~|\$HOME)\b"),
    re.compile(r"\bchmod\s+777\b"),
    re.compile(r"\bbase64\s+-d\b[^\n|]*\|\s*(?:ba)?sh\b"),
]


def result(gate: str, status: str, message: str, severity: str = "") -> dict[str, str]:
    item = {"gate": gate, "status": status, "message": message}
    if severity:
        item["severity"] = severity
    return item


def read_frontmatter(skill_md: Path) -> dict[str, Any]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md is missing YAML frontmatter")
    parts = text.split("---\n", 2)
    if len(parts) != 3:
        raise ValueError("SKILL.md frontmatter is not closed")
    data = yaml.safe_load(parts[1]) or {}
    if not isinstance(data, dict):
        raise ValueError("SKILL.md frontmatter must be a mapping")
    return data


def structural_gate(skill_path: Path) -> dict[str, Any]:
    skill_md = skill_path / "SKILL.md"
    try:
        metadata = read_frontmatter(skill_md)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return {"result": result("structure", "fail", str(exc), "critical"), "metadata": {}}

    problems = []
    if not str(metadata.get("name", "")).strip():
        problems.append("frontmatter name is required")
    elif metadata["name"] != skill_path.name:
        problems.append("frontmatter name must match the package directory")
    if not str(metadata.get("description", "")).strip():
        problems.append("frontmatter description is required")
    if problems:
        return {"result": result("structure", "fail", "; ".join(problems), "critical"), "metadata": metadata}
    return {"result": result("structure", "pass", "SKILL.md and required frontmatter are valid"), "metadata": metadata}


def security_gate(skill_path: Path) -> dict[str, Any]:
    findings = []
    code_suffixes = {".py", ".sh", ".bash", ".zsh", ".js", ".ts", ".json", ".yaml", ".yml", ".toml"}
    for path in sorted(p for p in skill_path.rglob("*") if p.is_file() and p.suffix.lower() in code_suffixes and ".git" not in p.parts and not ({"tests", "evals"} & set(p.relative_to(skill_path).parts))):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"possible embedded credential pattern: {path.relative_to(skill_path)}")
        for pattern in DANGEROUS_PATTERNS:
            if pattern.search(text):
                findings.append(f"dangerous command pattern: {path.relative_to(skill_path)}")
    if findings:
        return result("security", "fail", "; ".join(findings), "critical")
    return result("security", "pass", "no blocked credential or dangerous-command patterns found")


def eval_gate(skill_path: Path) -> dict[str, str]:
    evals = skill_path / "evals"
    tests = skill_path / "tests"
    if evals.is_dir() and any(evals.iterdir()):
        return result("eval", "pass", "bundled eval evidence is present")
    if tests.is_dir() and any(tests.iterdir()):
        return result("eval", "pass", "test evidence is present")
    return result("eval", "warn", "no evals/ or tests/ evidence found", "warning")


def staleness_gate(metadata: dict[str, Any], as_of: date) -> dict[str, str]:
    review_metadata = metadata.get("metadata") if isinstance(metadata.get("metadata"), dict) else metadata
    last_reviewed = review_metadata.get("last_reviewed")
    interval = review_metadata.get("review_interval_days")
    if not last_reviewed or interval is None:
        return result("staleness", "warn", "last_reviewed and review_interval_days metadata are not both declared", "warning")
    try:
        reviewed = date.fromisoformat(str(last_reviewed))
        days = int(interval)
    except (TypeError, ValueError):
        return result("staleness", "fail", "review metadata must use an ISO date and integer interval", "critical")
    if days < 1:
        return result("staleness", "fail", "review_interval_days must be positive", "critical")
    due = reviewed + timedelta(days=days)
    if as_of > due:
        return result("staleness", "warn", f"review overdue since {due.isoformat()}", "warning")
    return result("staleness", "pass", f"review current through {due.isoformat()}")


def assess(skill_path: Path, as_of: date | None = None) -> dict[str, Any]:
    if not skill_path.is_dir():
        return {
            "skill": str(skill_path),
            "status": "blocked",
            "results": [result("structure", "fail", "skill package directory does not exist", "critical")],
        }
    structural = structural_gate(skill_path)
    results = [structural["result"], security_gate(skill_path), eval_gate(skill_path), staleness_gate(structural["metadata"], as_of or date.today())]
    status = "blocked" if any(item.get("status") == "fail" and item.get("severity") == "critical" for item in results) else ("warning" if any(item.get("status") == "warn" for item in results) else "pass")
    return {"skill": str(skill_path), "status": status, "results": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill", type=Path)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = assess(args.skill, args.as_of)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"{report['status'].upper()} {args.skill}")
        for item in report["results"]:
            print(f"{item['status'].upper()} {item['gate']}: {item['message']}")
    return 2 if report["status"] == "blocked" else 0


if __name__ == "__main__":
    sys.exit(main())
