#!/usr/bin/env python3
"""Audit AGENTS precedence and repository Skill reachability."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile


LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
STALE_MARKERS = ("skills/AGENTS.md", ".agents/skills/AGENTS.md")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ancestors(root: Path, cwd: Path) -> list[Path]:
    try:
        relative = cwd.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"execution CWD is outside repository root: {cwd}") from exc
    return [root.joinpath(*relative.parts[:index]) for index in range(len(relative.parts) + 1)]


def _source(directory: Path) -> tuple[Path | None, list[str]]:
    override = directory / "AGENTS.override.md"
    standard = directory / "AGENTS.md"
    selected = override if override.is_file() else standard if standard.is_file() else None
    ignored = []
    if selected == override and standard.is_file():
        ignored.append(str(standard))
    return selected, ignored


def _skill_roots(ancestors: list[Path]) -> list[Path]:
    roots = []
    for directory in reversed(ancestors):
        for name in (".agents/skills", "skills"):
            candidate = directory / name
            if candidate.is_dir():
                roots.append(candidate)
    return roots


def _relative_links(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    links = []
    for target in LINK_RE.findall(text):
        target = target.split("#", 1)[0].strip()
        if target and not re.match(r"^[a-z]+://", target) and not target.startswith("#"):
            links.append(target)
    return links


def audit(repo_root: Path, execution_cwd: Path, max_bytes: int = 32768) -> dict:
    root = repo_root.resolve()
    cwd = execution_cwd.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    if not root.is_dir():
        return {"status": "FAIL", "errors": [f"repository root is not a directory: {root}"]}
    if not cwd.is_dir():
        return {"status": "FAIL", "errors": [f"execution CWD is not a directory: {cwd}"]}
    try:
        ancestors = _ancestors(root, cwd)
    except ValueError:
        return {"status": "FAIL", "errors": [f"execution CWD is outside repository root: {cwd}"]}

    chain = []
    for directory in ancestors:
        selected, ignored = _source(directory)
        if selected:
            item = {
                "path": str(selected),
                "relative_path": str(selected.relative_to(root)),
                "state": "SELECTED",
                "bytes": selected.stat().st_size,
                "sha256": _sha256(selected),
            }
            chain.append(item)
            if selected.stat().st_size > max_bytes:
                warnings.append(f"oversized instruction source: {selected}")
            text = selected.read_text(encoding="utf-8")
            for marker in STALE_MARKERS:
                if marker in text:
                    errors.append(f"stale authority marker {marker}: {selected}")
            for link in _relative_links(selected):
                target = (selected.parent / link).resolve()
                if not target.exists():
                    errors.append(f"broken relative reference {link}: {selected}")
            if ignored:
                warnings.extend(f"override selected; ignored sibling: {path}" for path in ignored)

    roots = _skill_roots(ancestors)
    packages = []
    for skill_root in roots:
        for package in sorted(skill_root.iterdir()):
            skill_md = package / "SKILL.md"
            if not package.is_dir() or not skill_md.is_file():
                continue
            packages.append({
                "name": package.name,
                "root": str(skill_root),
                "path": str(skill_md),
                "relative_path": str(skill_md.relative_to(root)),
                "bytes": skill_md.stat().st_size,
                "sha256": _sha256(skill_md),
            })

    by_name: dict[str, list[str]] = {}
    for package in packages:
        by_name.setdefault(package["name"], []).append(package["path"])
    for name, paths in sorted(by_name.items()):
        if len(paths) > 1:
            errors.append(f"same-name Skill collision {name}: {', '.join(paths)}")

    fingerprint_input = {
        "repo_root": str(root),
        "execution_cwd": str(cwd),
        "agents": chain,
        "skill_roots": [str(path) for path in roots],
        "skills": packages,
    }
    fingerprint = hashlib.sha256(
        json.dumps(fingerprint_input, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "status": "FAIL" if errors else "PASS",
        "repo_root": str(root),
        "execution_cwd": str(cwd),
        "instruction_chain": chain,
        "skill_roots": [str(path) for path in roots],
        "skills": packages,
        "fingerprint": fingerprint,
        "evidence_states": {
            "expected": "OBSERVED",
            "selected": "OBSERVED",
            "accessed": "OBSERVED",
            "loaded": "NOT_ASSESSED",
            "behavior_observed": "NOT_ASSESSED",
        },
        "warnings": warnings,
        "errors": errors,
    }


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="agents-md-") as temp:
        root = Path(temp)
        (root / "AGENTS.md").write_text("# root\n", encoding="utf-8")
        nested = root / "service"
        nested.mkdir()
        (nested / "AGENTS.override.md").write_text("# delta\n", encoding="utf-8")
        skill = root / "skills" / "sample"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: sample\ndescription: sample\n---\n", encoding="utf-8"
        )
        report = audit(root, nested)
        assert report["status"] == "PASS", report
        assert [item["relative_path"] for item in report["instruction_chain"]] == [
            "AGENTS.md", "service/AGENTS.override.md"
        ]
        assert report["evidence_states"]["loaded"] == "NOT_ASSESSED"
        (root / "AGENTS.md").write_text("[stale](skills/AGENTS.md)\n", encoding="utf-8")
        (nested / "AGENTS.override.md").write_text("[missing](missing.md)\n", encoding="utf-8")
        duplicate = nested / ".agents" / "skills" / "sample"
        duplicate.mkdir(parents=True)
        (duplicate / "SKILL.md").write_text(
            "---\nname: sample\ndescription: duplicate\n---\n", encoding="utf-8"
        )
        report = audit(root, nested)
        assert report["status"] == "FAIL", report
        assert any("stale authority marker" in error for error in report["errors"])
        assert any("broken relative reference" in error for error in report["errors"])
        assert any("same-name Skill collision" in error for error in report["errors"])
        assert audit(root, root.parent)["status"] == "FAIL"
    print("agents-md self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_root", nargs="?", type=Path)
    parser.add_argument("--cwd", dest="execution_cwd", type=Path)
    parser.add_argument("--max-bytes", type=int, default=32768)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.repo_root is None:
        parser.error("repo_root is required unless --self-test is used")
    root = args.repo_root.resolve()
    cwd = (args.execution_cwd or root).resolve()
    print(json.dumps(audit(root, cwd, args.max_bytes), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
