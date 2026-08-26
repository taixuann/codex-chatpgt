#!/usr/bin/env python3
"""Validate the Codex Git allowlist and reject sensitive tracked paths."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys


ALLOWED_PREFIXES = ("agents/", "documentation/", "skills/control-plane-audit/", "skills/runtime-adapter-management/", "skills/instruction-maintenance/", "skills/project-bootstrap/", "skills/external-handoff/", "skills/shared-session-closeout/", "skills/session-packet-management/", ".github/", "manifests/", "ops/schemas/", "ops/scripts/", "ops/schedulers/", "ops/changes/", "ops/on-demand-skills/")
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
})
ALLOWED_SKILL_SHARED_PREFIXES = ("skills/references/",)
FORBIDDEN_MARKERS = (".system/", "sessions/", "memories/", "cache/", "logs", ".sqlite", "config.toml", "credentials", "token")
TRACKED_SESSION_PREFIXES = ("documentation/sessions/",)
SESSION_ID = r"[0-9]{8}_[a-z0-9]+(?:-[a-z0-9]+)*_[0-9]{3}"
TRACKED_SESSION_PATH = re.compile(
    rf"^documentation/sessions/{SESSION_ID}/(?:session\.yaml|context\.md|spec\.md|plan\.md|task\.md|franky\.ticket\.yaml|franky\.results\.yaml|references\.yaml|\.rag/manifest\.yaml)$"
)


def is_allowed_path(path: str) -> bool:
    """Return whether a tracked path belongs to an admitted repository surface."""
    if path.startswith(TRACKED_SESSION_PREFIXES):
        return bool(TRACKED_SESSION_PATH.fullmatch(path))
    if path in ALLOWED_FILES or path.startswith(ALLOWED_PREFIXES):
        return True
    if path.startswith(ALLOWED_SKILL_SHARED_PREFIXES):
        return True
    if path.startswith("skills/"):
        package = path.split("/", 2)[1] if path.count("/") >= 1 else ""
        return package in ALLOWED_SKILL_PACKAGES and path.startswith(f"skills/{package}/")
    return path.startswith("plans/PLAN-") and path.endswith(".md") and "/" not in path[len("plans/"):]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    try:
        result = subprocess.run(["git", "-C", str(args.root), "ls-files"], check=True, capture_output=True, text=True)
        paths = [line for line in result.stdout.splitlines() if line]
        for path in paths:
            if not is_allowed_path(path):
                raise ValueError(f"tracked path outside allowlist: {path}")
            protected_marker = any(marker in path for marker in FORBIDDEN_MARKERS)
            tracked_packet = bool(TRACKED_SESSION_PATH.fullmatch(path))
            if protected_marker and not tracked_packet:
                raise ValueError(f"sensitive path is tracked: {path}")
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"FAIL {args.root}: {exc}")
        return 1
    print(f"OK {args.root}: {len(paths)} tracked paths within allowlist")
    return 0


if __name__ == "__main__":
    sys.exit(main())
