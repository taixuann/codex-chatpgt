# Plan scenario routing

Determine the minimum necessary capability set. The `primary`/`scenario` field
is a reporting label only and must not prevent composition of a supporting
capability.

| Priority | Situation | Primary leaf | Result |
| ---: | --- | --- | --- |
| 1 | Goal or scope is missing or contradictory | `RETURN_TO_INTENT` | Intent clarification and confirmation |
| 2 | Architecture or cross-domain design could change the plan | `architecture-preflight` | Resolved or escalated design decisions |
| 3 | Accepted Intent needs decomposition | `planning-and-task-breakdown` | Ordered, verifiable tasks and checkpoints |

The possible active sets are: none, `architecture-preflight`,
`planning-and-task-breakdown`, or both leaves together. A canonical pattern
that resolves design uncertainty skips architecture-preflight.

Negative routing examples:

- A vague idea belongs to `intent/idea-refine`, not `planning-and-task-breakdown`.
- A confirmed task list does not need `interview-me`.
- A code change during plan generation belongs to the build phase, not this family.
