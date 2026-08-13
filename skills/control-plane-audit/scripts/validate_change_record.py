#!/usr/bin/env python3
"""Control-plane entrypoint for deterministic change-record validation."""
from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).parents[3] / "ops/scripts/validate_franky_change_record.py"), run_name="__main__")
