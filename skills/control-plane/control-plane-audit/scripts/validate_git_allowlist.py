#!/usr/bin/env python3
"""Validate the Codex Git allowlist and reject sensitive tracked paths."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys


ALLOWED_PREFIXES = ("agents/", "documentation/", "skills/control-plane/control-plane-audit/", "skills/control-plane/runtime-adapter-management/", "skills/control-plane/instruction-maintenance/", "skills/control-plane/project-bootstrap/", "skills/control-plane/external-handoff/", "skills/control-plane/shared-session-closeout/", "skills/control-plane/session-packet-management/", ".github/", "manifests/", "ops/schemas/", "ops/scripts/", "ops/schedulers/", "ops/changes/", "ops/on-demand-skills/")
ALLOWED_FILES = {".gitignore", "AGENTS.md", "README.md", "skills/AGENTS.md", "skills/ADDYOSMANI-AGENT-SKILLS-LICENSE", "workflows/AGENTS.md"}
ALLOWED_SKILL_PACKAGES = frozenset({
    "api-and-interface-design", "aspnet-core", "browser-testing-with-devtools", "chatgpt-apps",
    "ci-cd-and-automation", "cli-creator", "cloudflare-deploy", "code-review-and-quality",
    "code-simplification", "context-engineering", "debugging-and-error-recovery", "deprecation-and-migration",
    "documentation-and-adrs", "doubt-driven-development", "figma", "figma-code-connect-components",
    "figma-create-design-system-rules", "figma-create-new-file", "figma-generate-design",
    "figma-generate-library", "figma-implement-design", "figma-use", "frontend-ui-engineering",
    "git-workflow-and-versioning", "hatch-pet", "idea-refine", "incremental-implementation", "interview-me",
    "jupyter-notebook", "linear", "migrate-to-codex", "netlify-deploy", "notion-knowledge-capture",
    "notion-meeting-intelligence", "notion-research-documentation", "notion-spec-to-implementation",
    "observability-and-instrumentation", "performance-optimization", "planning-and-task-breakdown", "playwright",
    "playwright-interactive", "render-deploy", "screenshot", "security-and-hardening",
    "security-best-practices", "security-ownership-map", "security-threat-model", "sentry", "shipping-and-launch",
    "skill-retrospective", "socratic", "source-driven-development", "spec-driven-development", "speech",
    "test-driven-development", "transcribe", "using-agent-skills", "vercel-deploy", "winui-app",
    "scientific-evidence-synthesis", "hypothesis-and-test-design", "scientific-method-critique", "session-packet-management",
    "codebase-reconnaissance", "research-source-discovery", "reference-state-reconnaissance",
    "independent-artifact-review", "scientific-peer-review", "risk-security-review", "temperature-iv-analysis", "phd-sop",
})
ALLOWED_SKILL_SHARED_PREFIXES = ("skills/references/",)
ALLOWED_SKILL_FAMILY_PREFIXES = ("skills/intent/", "skills/plan/")
FORBIDDEN_MARKERS = (".system/", "sessions/", "memories/", "cache/", "logs", ".sqlite", "config.toml", "credentials", "token")
# Session/record paths may be admitted, but sensitive-name markers must still
# apply to them.  Keeping this separate prevents an allowlist exception from
# silently making credential- or token-like filenames acceptable.
SENSITIVE_MARKERS = tuple(marker for marker in FORBIDDEN_MARKERS if marker != "sessions/")


def is_sensitive_path(path: str) -> bool:
    return any(marker in path for marker in SENSITIVE_MARKERS)
TRACKED_SESSION_PREFIXES = ("documentation/sessions/",)
SESSION_ID = r"[0-9]{8}_[a-z0-9]+(?:-[a-z0-9]+)*_[0-9]{3}"
TRACKED_SESSION_PATH = re.compile(
    rf"^documentation/sessions/(?:README\.md|{SESSION_ID}/(?:session\.yaml|context\.md|spec\.md|plan\.md|task\.md|franky\.ticket\.yaml|franky\.results\.yaml|references\.yaml|\.rag/manifest\.yaml))$"
)
TRACKED_SESSION_RECORD_PATH = re.compile(
    r"^documentation/sessions/records/(?:plans/PLAN-[A-Za-z0-9][A-Za-z0-9._-]*\.md|reviews/ISSUE-[A-Za-z0-9][A-Za-z0-9._-]*\.yaml)$"
)


def is_allowed_path(path: str) -> bool:
    """Return whether a tracked path belongs to an admitted repository surface."""
    if path.startswith(TRACKED_SESSION_PREFIXES):
        admitted = bool(TRACKED_SESSION_PATH.fullmatch(path) or TRACKED_SESSION_RECORD_PATH.fullmatch(path))
        return admitted and not is_sensitive_path(path)
    if path in ALLOWED_FILES or path.startswith(ALLOWED_PREFIXES):
        return True
    if path.startswith(ALLOWED_SKILL_SHARED_PREFIXES):
        return True
    if path.startswith(ALLOWED_SKILL_FAMILY_PREFIXES):
        return True
    if path.startswith("skills/"):
        parts = path.split("/")
        # Taxonomy paths are skills/<domain>/<package>/..., while shared
        # references remain at skills/references/.... Derive identity from
        # the package directory rather than the taxonomy directory.
        package = parts[2] if len(parts) >= 3 else ""
        return package in ALLOWED_SKILL_PACKAGES and len(parts) >= 4 and path.startswith(f"skills/{parts[1]}/{package}/")
    return path.startswith("plans/PLAN-") and path.endswith(".md") and "/" not in path[len("plans/"):]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    try:
        # Include live untracked paths so a just-moved package is validated
        # before the structural migration is staged, while ignoring cached
        # paths that no longer exist in the working tree.
        result = subprocess.run(
            ["git", "-C", str(args.root), "ls-files", "-co", "--exclude-standard"],
            check=True, capture_output=True, text=True,
        )
        paths = [line for line in result.stdout.splitlines() if line and (args.root / line).exists()]
        for path in paths:
            if not is_allowed_path(path):
                raise ValueError(f"tracked path outside allowlist: {path}")
            protected_marker = is_sensitive_path(path)
            if protected_marker:
                raise ValueError(f"sensitive path is tracked: {path}")
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"FAIL {args.root}: {exc}")
        return 1
    print(f"OK {args.root}: {len(paths)} tracked paths within allowlist")
    return 0


if __name__ == "__main__":
    sys.exit(main())
