#!/usr/bin/env python3
"""Franky maintenance entrypoint for deterministic change-record validation."""
from __future__ import annotations

import runpy


if __name__ == "__main__":
    runpy.run_path("/Users/tai/.codex/ops/scripts/validate_franky_change_record.py", run_name="__main__")
