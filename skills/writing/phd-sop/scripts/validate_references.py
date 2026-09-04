#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "references" / "source-manifest.yaml"

MUTABLE_CLASSES = {"OPEN_SOURCE_DESIGN_COMPARATOR"}
ALLOWED_CLASSES = {
    "OFFICIAL_APPLICATION_POLICY",
    "OFFICIAL_APPLICATION_GUIDANCE",
    "PEER_REVIEWED_RESEARCH",
    "PREPRINT_RESEARCH",
    "PROFESSIONAL_WRITING_GUIDANCE",
    "RUBRIC_METHOD_GUIDANCE",
    "OPEN_SOURCE_DESIGN_COMPARATOR",
    "REPOSITORY_DESIGN",
    "USER_GOLD",
    "SYNTHETIC_ADVERSARIAL",
}
SHA40 = re.compile(r"^[0-9a-f]{40}$")

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    data = load(MANIFEST)
    errors = []
    sources = data.get("sources", [])
    ids = [x.get("id") for x in sources]
    dup = sorted({i for i in ids if i and ids.count(i) > 1})
    if dup:
        errors.append(f"duplicate source ids: {dup}")
    for src in sources:
        sid = src.get("id", "<missing>")
        for key in ("id","class","url","revision","license","used_for","not_authoritative_for"):
            if key not in src or src[key] in (None,"",[]):
                errors.append(f"{sid}: missing/empty {key}")
        source_class = src.get("class")
        if source_class not in ALLOWED_CLASSES:
            errors.append(f"{sid}: unknown source class {source_class}")
        if source_class in MUTABLE_CLASSES and not SHA40.match(str(src.get("revision",""))):
            errors.append(f"{sid}: mutable comparator must pin a 40-char commit SHA")
    if not data.get("checked_date"):
        errors.append("manifest checked_date missing")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {len(sources)} sources with provenance, authority class, and limitations")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
