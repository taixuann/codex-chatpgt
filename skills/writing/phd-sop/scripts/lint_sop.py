#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "references" / "ai-pattern-catalog.yaml"

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")


def load_catalog():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_RE.split(text.strip()) if s.strip()]


def lint_text(text: str) -> list[dict]:
    findings: list[dict] = []
    sentences = split_sentences(text)
    catalog = load_catalog()

    # Pattern catalogue matches are warnings only.
    lower = text.lower()
    for pattern in catalog.get("patterns", []):
        hits = [t for t in pattern.get("triggers", []) if t.lower() in lower]
        if hits:
            findings.append({
                "rule": pattern["id"],
                "severity": "warning",
                "hits": hits,
                "diagnostic_only": True,
            })

    # Consecutive first-person openers.
    run = 0
    max_run = 0
    for sentence in sentences:
        if re.match(r"^I\b", sentence):
            run += 1
            max_run = max(max_run, run)
        else:
            run = 0
    if max_run >= 3:
        findings.append({
            "rule": "repeated_first_person_opener",
            "severity": "warning",
            "count": max_run,
            "diagnostic_only": True,
        })

    # Repeated weak openers are signals, not failures.
    openers = []
    for sentence in sentences:
        match = re.match(r"^(This|These|It)\b", sentence)
        openers.append(match.group(1) if match else None)
    for opener in ("This", "These", "It"):
        count = sum(x == opener for x in openers)
        if count >= 3:
            findings.append({
                "rule": "repeated_weak_opener",
                "severity": "warning",
                "opener": opener,
                "count": count,
                "diagnostic_only": True,
            })

    # Very long sentences deserve inspection; they are not automatically bad.
    for index, sentence in enumerate(sentences, start=1):
        words = WORD_RE.findall(sentence)
        if len(words) > 45:
            findings.append({
                "rule": "long_sentence",
                "severity": "warning",
                "sentence": index,
                "word_count": len(words),
                "diagnostic_only": True,
            })

    # Repeated two-word starts can expose templating.
    starts = []
    for sentence in sentences:
        words = [w.lower() for w in WORD_RE.findall(sentence)[:2]]
        if len(words) == 2:
            starts.append(" ".join(words))
    counts = Counter(starts)
    for start, count in counts.items():
        if count >= 3:
            findings.append({
                "rule": "repeated_syntactic_start_proxy",
                "severity": "warning",
                "start": start,
                "count": count,
                "diagnostic_only": True,
            })

    return findings


def run_self_test(path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    for case in data.get("cases", []):
        found = {x["rule"] for x in lint_text(case["text"])}
        expected = set(case.get("expected_rules", []))
        forbidden = set(case.get("forbidden_rules", []))
        missing = sorted(expected - found)
        unexpected = sorted(forbidden & found)
        if missing:
            errors.append(f"{case['id']}: missing expected rules {missing}")
        if unexpected:
            errors.append(f"{case['id']}: fired forbidden rules {unexpected}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {len(data.get('cases', []))} lint self-test cases")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path, nargs="?")
    parser.add_argument("--self-test", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test(args.self_test)
    if not args.file:
        parser.error("provide a text file or --self-test")
    findings = lint_text(args.file.read_text(encoding="utf-8"))
    print(json.dumps({"findings": findings, "authorship_verdict": None}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
