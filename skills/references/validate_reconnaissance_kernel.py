#!/usr/bin/env python3
"""Deterministic guard for the shared Argus reconnaissance contract."""
from pathlib import Path
import sys

REQUIRED = (
    "authority order", "freshness requirement", "required evidence classes",
    "insufficient or misleading", "coverage/gaps", "Stop at saturation",
    "no write, indexing, session-management",
)

def main() -> int:
    path = Path(__file__).with_name("reconnaissance-kernel.md")
    text = path.read_text(encoding="utf-8").lower()
    missing = [term for term in REQUIRED if term.lower() not in text]
    if missing:
        print("FAIL reconnaissance kernel: missing " + ", ".join(missing))
        return 1
    print("PASS reconnaissance kernel: required pre-search, evidence, stop, and side-effect clauses present")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
