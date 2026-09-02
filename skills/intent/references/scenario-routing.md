# Intent scenario routing

Use the first matching row. If two rows appear to match, prefer the earlier
row and record the ambiguity in `open_questions` rather than loading multiple
leaves automatically.

| Priority | Source/situation | Primary leaf | Expected result |
| ---: | --- | --- | --- |
| 1 | User request or Issue is missing the outcome, audience, constraint, or success measure | `interview-me` | Confirmed intent; no idea variants or tasks yet |
| 2 | User request or Issue contains a rough concept and alternatives/assumptions need exploration | `idea-refine` | Chosen direction plus assumptions and a not-doing list |
| 3 | User request or Issue has a chosen direction but needs measurable scope and acceptance criteria | `define-goal` | Concrete objective ready to feed planning |

Negative routing examples:

- “Implement the approved task exactly as written” is not `interview-me`.
- “Break this confirmed specification into tasks” is not `idea-refine`.
- “Fix this typo” does not need an intent family at all.

For a GitHub Issue, audit the Issue first with
[source-audit.md](source-audit.md), then use the same smallest leaf. Use
`interview-me` only when the Issue remains materially ambiguous; otherwise
normalize it with `define-goal`. Preserve the Issue locator and do not rewrite
the Issue as a side effect.
