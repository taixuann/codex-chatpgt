"""Canonical locator grammar shared by intent packet and run-state validators."""

from __future__ import annotations

import re


USER_LOCATOR_RE = re.compile(
    r"^(?:conversation|user-request:[A-Za-z0-9][A-Za-z0-9._/-]*|pasted-text:[A-Za-z0-9][A-Za-z0-9._/-]*)$"
)
GITHUB_ISSUE_RE = re.compile(
    r"^(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*|"
    r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/[1-9][0-9]*)$"
)


def valid_locator(kind: str, locator: object) -> bool:
    if not isinstance(locator, str):
        return False
    if kind == "user":
        return bool(USER_LOCATOR_RE.fullmatch(locator))
    if kind == "github_issue":
        return bool(GITHUB_ISSUE_RE.fullmatch(locator))
    return False


def locator_error(kind: str) -> str:
    if kind == "user":
        return "user locator must be conversation, user-request:<ref>, or pasted-text:<ref>"
    return "github_issue locator must be owner/repo#<number> or a canonical GitHub Issue URL"
