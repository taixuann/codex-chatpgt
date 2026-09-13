#!/usr/bin/env python3
"""Audit AGENTS precedence and repository Skill reachability."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import subprocess
import tempfile


LINK_RE = re.compile(r"\[[^\]]*\]\(\s*(<[^>\n]+>|[^\s)\n]+)(?:\s+[^)\n]*)?\)")
STALE_MARKERS = ("skills/AGENTS.md", ".agents/skills/AGENTS.md")
DEFAULT_PROJECT_CONTEXT_BYTES = 32 * 1024


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_limited(path: Path, limit: int) -> str:
    with path.open("rb") as stream:
        return stream.read(limit + 1).decode("utf-8", errors="replace")


def _has_text(path: Path) -> bool:
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4096), b""):
            if chunk.strip():
                return True
    return False


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _git_ignored(path: Path, root: Path) -> bool:
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    result = subprocess.run(
        ["git", "-C", str(root), "check-ignore", "-q", "--", str(relative)],
        capture_output=True,
    )
    return result.returncode == 0


def _ancestors(root: Path, cwd: Path) -> list[Path]:
    try:
        relative = cwd.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"execution CWD is outside repository root: {cwd}") from exc
    return [root.joinpath(*relative.parts[:index]) for index in range(len(relative.parts) + 1)]


def _source(directory: Path, fallback_names: tuple[str, ...]) -> tuple[Path | None, list[str], str, list[dict]]:
    override = directory / "AGENTS.override.md"
    standard = directory / "AGENTS.md"
    candidates = [(override, "AGENTS.override.md"), (standard, "AGENTS.md")]
    candidates.extend((directory / name, name) for name in fallback_names)
    candidate_evidence = []
    for path, name in candidates:
        if path.is_symlink():
            state = "SYMLINK"
        elif not path.is_file():
            state = "ABSENT"
        elif _has_text(path):
            state = "AVAILABLE"
        else:
            state = "EMPTY"
        candidate_evidence.append({"name": name, "path": str(path), "state": state})
    selected = None
    selection = "NONE"
    if not override.is_symlink() and override.is_file() and _has_text(override):
        selected, selection = override, "SELECTED"
    elif not standard.is_symlink() and standard.is_file() and _has_text(standard):
        selected, selection = standard, "SELECTED"
    else:
        for fallback_name in fallback_names:
            candidate = directory / fallback_name
            if not candidate.is_symlink() and candidate.is_file() and _has_text(candidate):
                selected, selection = candidate, "SELECTED_FALLBACK"
                break
    ignored = []
    if selected == override and standard.is_file():
        ignored.append(str(standard))
    for candidate in candidate_evidence:
        if candidate["path"] == str(selected):
            candidate["state"] = "SELECTED"
        elif candidate["state"] == "AVAILABLE":
            candidate["state"] = "IGNORED"
    return selected, ignored, selection, candidate_evidence


def _skill_roots(ancestors: list[Path], directory_name: str) -> list[Path]:
    roots = []
    for directory in reversed(ancestors):
        candidate = directory / directory_name
        if candidate.is_symlink() or candidate.is_dir():
            roots.append(candidate)
    return roots


def _skill_packages(roots: list[Path], root: Path, max_bytes: int, errors: list[str], warnings: list[str], scope: str) -> list[dict]:
    packages = []
    for skill_root in roots:
        if skill_root.is_symlink():
            errors.append(f"symlinked Skill root is not allowed: {skill_root}")
            continue
        for package in sorted(skill_root.iterdir()):
            skill_md = package / "SKILL.md"
            if package.is_symlink():
                errors.append(f"symlinked Skill package is not allowed: {package}")
                continue
            if not package.is_dir():
                continue
            if _git_ignored(package, root):
                continue
            if skill_md.is_symlink():
                errors.append(f"symlinked Skill source is not allowed: {skill_md}")
                continue
            if _git_ignored(skill_md, root):
                continue
            if not skill_md.is_file() or not _inside(skill_md, root):
                continue
            skill_name = _skill_name(skill_md, package.name, max_bytes)
            packages.append({
                "name": skill_name,
                "root": str(skill_root),
                "path": str(skill_md),
                "relative_path": str(skill_md.relative_to(root)),
                "bytes": skill_md.stat().st_size,
                "sha256": _sha256(skill_md),
                "scope": scope,
            })
            _inspect_file(skill_md, max_bytes, errors, warnings)
    return packages


def _skill_name(path: Path, fallback: str, max_bytes: int) -> str:
    text = _read_limited(path, max_bytes)
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        end = next((index for index, line in enumerate(lines[1:], 1) if line.strip() in {"---", "..."}), None)
        if end is not None:
            for line in lines[1:end]:
                match = re.fullmatch(r"name:\s*([^#\n]+?)\s*", line)
                if match:
                    return match.group(1).strip().strip("'\"") or fallback
    return fallback


def _inspect_file(path: Path, max_bytes: int, errors: list[str], warnings: list[str]) -> dict:
    size = path.stat().st_size
    if size > max_bytes:
        warnings.append(f"oversized instruction/Skill source: {path}")
    text = _read_limited(path, max_bytes)
    for marker in STALE_MARKERS:
        if marker in text:
            errors.append(f"stale authority marker {marker}: {path}")
    for target in LINK_RE.findall(text):
        link = target.strip().removeprefix("<").removesuffix(">")
        link = link.split("#", 1)[0].strip()
        if not link or re.match(r"^[a-z][a-z0-9+.-]*:", link, re.IGNORECASE) or link.startswith("#"):
            continue
        target = (path.parent / link).resolve()
        if not target.exists():
            errors.append(f"broken relative reference {link}: {path}")
    return {"path": str(path), "bytes": size, "sha256": _sha256(path)}


def audit(
    repo_root: Path,
    execution_cwd: Path,
    max_bytes: int = 32768,
    *,
    max_context_bytes: int | None = DEFAULT_PROJECT_CONTEXT_BYTES,
    fallback_names: tuple[str, ...] = (),
    global_root: Path | None = None,
    expected_fingerprint: str | None = None,
    configured_context_limit: int | None = None,
) -> dict:
    root = repo_root.resolve()
    cwd = execution_cwd.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    if max_bytes < 0:
        return {"status": "FAIL", "errors": ["max_bytes must be non-negative"]}
    if not root.is_dir():
        return {"status": "FAIL", "errors": [f"repository root is not a directory: {root}"]}
    if not cwd.is_dir():
        return {"status": "FAIL", "errors": [f"execution CWD is not a directory: {cwd}"]}
    try:
        ancestors = _ancestors(root, cwd)
    except ValueError:
        return {"status": "FAIL", "errors": [f"execution CWD is outside repository root: {cwd}"]}

    chain = []
    instruction_sources = []
    for directory in ancestors:
        selected, ignored, selection, candidates = _source(directory, fallback_names)
        instruction_sources.append({
            "directory": str(directory),
            "selected": str(selected) if selected else None,
            "selection": selection,
            "candidates": candidates,
        })
        errors.extend(
            f"symlinked instruction source is not allowed: {item['path']}"
            for item in candidates if item["state"] == "SYMLINK"
        )
        if selected:
            item = {"relative_path": str(selected.relative_to(root)), "state": selection}
            item.update(_inspect_file(selected, max_bytes, errors, warnings))
            chain.append(item)
            if ignored:
                warnings.extend(f"override selected; ignored sibling: {path}" for path in ignored)

    global_chain = []
    global_instruction_sources = []
    if global_root is not None:
        global_path = global_root.resolve()
        if not global_path.is_dir():
            errors.append(f"global guidance root is not a directory: {global_path}")
        else:
            selected, ignored, selection, candidates = _source(global_path, ())
            candidates.extend({
                "name": name,
                "path": str(global_path / name),
                "state": "NOT_APPLIED",
                "present": (global_path / name).is_file(),
            } for name in fallback_names)
            global_instruction_sources.append({
                "directory": str(global_path),
                "selected": str(selected) if selected else None,
                "selection": selection,
                "candidates": candidates,
            })
            errors.extend(
                f"symlinked instruction source is not allowed: {item['path']}"
                for item in candidates if item["state"] == "SYMLINK"
            )
            if selected:
                item = {"relative_path": str(selected), "state": selection}
                item.update(_inspect_file(selected, max_bytes, errors, warnings))
                global_chain.append(item)
                if ignored:
                    warnings.extend(f"global override selected; ignored sibling: {path}" for path in ignored)

    native_roots = _skill_roots(ancestors, ".agents/skills")
    package_roots = _skill_roots(ancestors, "skills")
    native_packages = _skill_packages(native_roots, root, max_bytes, errors, warnings, "native")
    repository_packages = _skill_packages(package_roots, root, max_bytes, errors, warnings, "repository-package")

    for packages, label in ((native_packages, "native"), (repository_packages, "repository package")):
        by_name: dict[str, list[str]] = {}
        for package in packages:
            by_name.setdefault(package["name"], []).append(package["path"])
        for name, paths in sorted(by_name.items()):
            if len(paths) > 1:
                errors.append(f"same-name {label} Skill collision {name}: {', '.join(paths)}")

    fingerprint_input = {
        "repo_root": str(root),
        "execution_cwd": str(cwd),
        "global_root": str(global_root.resolve()) if global_root is not None else None,
        "fallback_names": list(fallback_names),
        "agents": chain,
        "global_agents": global_chain,
        "instruction_sources": instruction_sources,
        "global_instruction_sources": global_instruction_sources,
        "native_skill_roots": [str(path) for path in native_roots],
        "repository_package_roots": [str(path) for path in package_roots],
        "native_skills": native_packages,
        "repository_skill_packages": repository_packages,
    }
    fingerprint = hashlib.sha256(
        json.dumps(fingerprint_input, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    project_context_bytes = sum(item["bytes"] for item in chain)
    global_context_bytes = sum(item["bytes"] for item in global_chain)
    if max_context_bytes is None:
        context_state = "NOT_ASSESSED"
    elif project_context_bytes > max_context_bytes:
        errors.append(f"project instruction chain exceeds context budget: {project_context_bytes} > {max_context_bytes}")
        context_state = "OVER_BUDGET"
    else:
        context_state = "PASS"
    drift_state = "NOT_ASSESSED"
    if expected_fingerprint is not None:
        drift_state = "MATCH" if expected_fingerprint == fingerprint else "CHANGED"
        if drift_state == "CHANGED":
            errors.append("instruction/Skill discovery fingerprint differs from expected baseline")
    return {
        "status": "FAIL" if errors else "PASS",
        "repo_root": str(root),
        "execution_cwd": str(cwd),
        "instruction_chain": chain,
        "global_instruction_chain": global_chain,
        "instruction_sources": instruction_sources,
        "global_instruction_sources": global_instruction_sources,
        "skill_roots": [str(path) for path in native_roots],
        "native_skill_roots": [str(path) for path in native_roots],
        "repository_package_roots": [str(path) for path in package_roots],
        "skills": native_packages,
        "repository_skill_packages": repository_packages,
        "fingerprint": fingerprint,
        "context_budget": {
            "bytes": project_context_bytes,
            "project_bytes": project_context_bytes,
            "global_bytes": global_context_bytes,
            "limit": max_context_bytes,
            "configured_limit": configured_context_limit if configured_context_limit is not None else "NOT_ASSESSED",
            "assumed_default": DEFAULT_PROJECT_CONTEXT_BYTES if configured_context_limit is None and max_context_bytes == DEFAULT_PROJECT_CONTEXT_BYTES else None,
            "state": context_state,
        },
        "drift": {"expected_fingerprint": expected_fingerprint, "state": drift_state},
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
        package = root / "skills" / "source-sample"
        package.mkdir(parents=True)
        (package / "SKILL.md").write_text(
            "---\nname: sample\ndescription: sample\n---\n[mail](mailto:test@example.invalid) [readme](README.md \"title\")\n", encoding="utf-8"
        )
        (package / "README.md").write_text("fixture\n", encoding="utf-8")
        native = root / ".agents" / "skills" / "native-one"
        native.mkdir(parents=True)
        (native / "SKILL.md").write_text(
            "---\nname: sample\ndescription: native\n---\n", encoding="utf-8"
        )
        report = audit(root, nested, fallback_names=("GUIDANCE.md",))
        assert report["status"] == "PASS", report
        baseline_fingerprint = report["fingerprint"]
        assert [item["relative_path"] for item in report["instruction_chain"]] == [
            "AGENTS.md", "service/AGENTS.override.md"
        ]
        assert report["instruction_sources"][0]["candidates"] == [
            {"name": "AGENTS.override.md", "path": str(root.resolve() / "AGENTS.override.md"), "state": "ABSENT"},
            {"name": "AGENTS.md", "path": str(root.resolve() / "AGENTS.md"), "state": "SELECTED"},
            {"name": "GUIDANCE.md", "path": str(root.resolve() / "GUIDANCE.md"), "state": "ABSENT"},
        ]
        assert [item["scope"] for item in report["skills"]] == ["native"]
        assert [item["scope"] for item in report["repository_skill_packages"]] == ["repository-package"]
        assert report["evidence_states"]["loaded"] == "NOT_ASSESSED"
        (root / "AGENTS.md").write_text("[stale](skills/AGENTS.md)\n", encoding="utf-8")
        (nested / "AGENTS.override.md").write_text("[missing](missing.md)\n", encoding="utf-8")
        (root / "AGENTS.override.md").write_text("[stale](skills/AGENTS.md)\n", encoding="utf-8")
        duplicate = nested / ".agents" / "skills" / "native-two"
        duplicate.mkdir(parents=True)
        (duplicate / "SKILL.md").write_text(
            "---\ndescription: value --- still valid\nname: sample\ndescription: duplicate\n---\n", encoding="utf-8"
        )
        report = audit(root, nested)
        assert report["status"] == "FAIL", report
        assert any("stale authority marker" in error for error in report["errors"])
        assert any("broken relative reference" in error for error in report["errors"])
        assert any("same-name native Skill collision" in error for error in report["errors"])
        linked = nested / ".agents" / "skills" / "linked"
        linked.mkdir(parents=True)
        (linked / "SKILL.md").symlink_to(Path("/etc/hosts"))
        linked_report = audit(root, nested)
        assert any("symlinked Skill source" in error for error in linked_report["errors"])
        linked_package = nested / ".agents" / "skills" / "linked-package"
        linked_package.symlink_to(linked.parent)
        linked_package_report = audit(root, nested)
        assert any("symlinked Skill package" in error for error in linked_package_report["errors"])
        linked_root = root / "linked-root"
        (linked_root / ".agents").mkdir(parents=True)
        (linked_root / ".agents" / "skills").symlink_to(native.parent)
        linked_root_report = audit(linked_root, linked_root)
        assert any("symlinked Skill root" in error for error in linked_root_report["errors"])
        (root / "AGENTS.override.md").unlink()
        (root / "AGENTS.override.md").symlink_to(Path("/etc/hosts"))
        agents_report = audit(root, root)
        assert any("symlinked instruction source" in error for error in agents_report["errors"])
        unicode_agents = root / "unicode-agents"
        unicode_agents.mkdir()
        (unicode_agents / "AGENTS.md").write_text("ééé\n", encoding="utf-8")
        unicode_report = audit(unicode_agents, unicode_agents, max_bytes=4)
        assert unicode_report["context_budget"]["state"] == "PASS"
        assert any("oversized instruction" in warning for warning in unicode_report["warnings"])
        assert audit(root, nested, max_bytes=-2)["status"] == "FAIL"

        whitespace = root / "whitespace"
        whitespace.mkdir()
        (whitespace / "AGENTS.md").write_text(" \n# guidance\n", encoding="utf-8")
        assert audit(whitespace, whitespace)["instruction_chain"]

        git_root = root / "git-fixture"
        git_root.mkdir()
        subprocess.run(["git", "init", "-q", str(git_root)], check=True)
        (git_root / ".gitignore").write_text(".agents/skills/ignored/\n", encoding="utf-8")
        tracked = git_root / ".agents" / "skills" / "tracked"
        tracked.mkdir(parents=True)
        (tracked / "SKILL.md").write_text("---\nname: tracked\n---\n", encoding="utf-8")
        ignored = git_root / ".agents" / "skills" / "ignored"
        ignored.mkdir(parents=True)
        (ignored / "SKILL.md").write_text("---\nname: ignored\n---\n", encoding="utf-8")
        git_report = audit(git_root, git_root)
        assert [item["name"] for item in git_report["skills"]] == ["tracked"]
        root_candidates = report["instruction_sources"][0]["candidates"]
        assert {item["name"]: item["state"] for item in root_candidates} == {
            "AGENTS.override.md": "SELECTED",
            "AGENTS.md": "IGNORED",
        }
        assert audit(root, nested, expected_fingerprint=baseline_fingerprint)["drift"]["state"] == "CHANGED"
        assert audit(root, root.parent)["status"] == "FAIL"
        fallback = root / "fallback"
        fallback.mkdir()
        (fallback / "GUIDANCE.md").write_text("# fallback\n", encoding="utf-8")
        fallback_report = audit(root, fallback, fallback_names=("GUIDANCE.md",))
        assert fallback_report["instruction_chain"][1]["state"] == "SELECTED_FALLBACK"
        assert {item["name"]: item["state"] for item in fallback_report["instruction_sources"][1]["candidates"]} == {
            "AGENTS.override.md": "ABSENT",
            "AGENTS.md": "ABSENT",
            "GUIDANCE.md": "SELECTED",
        }
        assert audit(root, nested, max_context_bytes=1)["context_budget"]["state"] == "OVER_BUDGET"
        global_root = root / "global"
        global_root.mkdir()
        (global_root / "AGENTS.md").write_text("# global\n", encoding="utf-8")
        (global_root / "GUIDANCE.md").write_text("# fallback must not apply globally\n", encoding="utf-8")
        global_report = audit(root, nested, global_root=global_root, fallback_names=("GUIDANCE.md",))
        assert global_report["global_instruction_chain"][0]["state"] == "SELECTED"
        assert {item["name"]: item["state"] for item in global_report["global_instruction_sources"][0]["candidates"]} == {
            "AGENTS.override.md": "ABSENT",
            "AGENTS.md": "SELECTED",
            "GUIDANCE.md": "NOT_APPLIED",
        }
        assert global_report["context_budget"]["global_bytes"] > 0
        assert global_report["context_budget"]["bytes"] == global_report["context_budget"]["project_bytes"]
        assert global_report["context_budget"]["configured_limit"] == "NOT_ASSESSED"
        assert global_report["context_budget"]["assumed_default"] == DEFAULT_PROJECT_CONTEXT_BYTES
        global_fallback = root / "global-fallback"
        global_fallback.mkdir()
        (global_fallback / "GUIDANCE.md").write_text("# global fallback\n", encoding="utf-8")
        global_fallback_report = audit(root, nested, global_root=global_fallback, fallback_names=("GUIDANCE.md",))
        assert global_fallback_report["global_instruction_chain"] == []
        assert {item["name"]: item["state"] for item in global_fallback_report["global_instruction_sources"][0]["candidates"]} == {
            "AGENTS.override.md": "ABSENT",
            "AGENTS.md": "ABSENT",
            "GUIDANCE.md": "NOT_APPLIED",
        }

        setup = root / "setup"
        setup.mkdir()
        before = sorted(path.relative_to(setup).as_posix() for path in setup.rglob("*"))
        setup_report = audit(setup, setup)
        after = sorted(path.relative_to(setup).as_posix() for path in setup.rglob("*"))
        assert setup_report["instruction_chain"] == []
        assert setup_report["instruction_sources"][0]["selection"] == "NONE"
        assert before == after

        qualification = root / "qualification"
        qualification.mkdir()
        (qualification / "AGENTS.md").write_text("[missing](missing.md)\n", encoding="utf-8")
        before = sorted(path.relative_to(qualification).as_posix() for path in qualification.rglob("*"))
        maintain_report = audit(qualification, qualification)
        after = sorted(path.relative_to(qualification).as_posix() for path in qualification.rglob("*"))
        assert maintain_report["status"] == "FAIL"
        assert before == after

        command = [sys.executable, str(Path(__file__)), str(qualification), "--cwd", str(qualification)]
        failed_run = subprocess.run(command + ["--max-context-bytes", "1"], capture_output=True, text=True)
        assert failed_run.returncode == 1, failed_run.stdout
        assert json.loads(failed_run.stdout)["status"] == "FAIL", failed_run.stdout
    print("agents-md self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_root", nargs="?", type=Path)
    parser.add_argument("--cwd", dest="execution_cwd", type=Path)
    parser.add_argument("--max-bytes", type=int, default=32768)
    parser.add_argument("--max-context-bytes", type=int, default=None)
    parser.add_argument("--fallback-name", action="append", default=[])
    parser.add_argument("--global-root", type=Path)
    parser.add_argument("--expected-fingerprint")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.repo_root is None:
        parser.error("repo_root is required unless --self-test is used")
    root = args.repo_root.resolve()
    cwd = (args.execution_cwd or root).resolve()
    configured_limit = args.max_context_bytes
    effective_limit = DEFAULT_PROJECT_CONTEXT_BYTES if configured_limit is None else configured_limit
    report = audit(
        root,
        cwd,
        args.max_bytes,
        max_context_bytes=effective_limit,
        fallback_names=tuple(args.fallback_name),
        global_root=args.global_root,
        expected_fingerprint=args.expected_fingerprint,
        configured_context_limit=configured_limit,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
