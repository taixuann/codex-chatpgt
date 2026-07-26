---
name: franky-github-review
description: Inspect GitHub pull-request review comments and prepare a numbered, approval-gated action plan without implicit external writes. Use for GitHub review triage inside Franky's operator lifecycle.
---

# Franky GitHub review

Use the installed `gh-address-comments` skill for the GitHub-specific flow.

1. Verify the repository and current branch.
2. Verify `gh` authentication before querying review data.
3. Fetch and number actionable review threads and comments.
4. Summarize the requested changes and ask which numbered items are in scope.
5. Keep inspection and planning separate from applying fixes.
6. Require explicit approval before any GitHub, repository, or code mutation.

Do not invent unresolved comments or imply that a PR is clean without current
evidence.
