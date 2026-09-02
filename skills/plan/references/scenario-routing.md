# Plan scenario routing

Select the first matching primary scenario. A plan may mention supporting
capabilities, but it should not silently execute another lifecycle stage.

| Priority | Situation | Primary leaf | Result |
| ---: | --- | --- | --- |
| 1 | Requirements are missing or contradictory | `spec-driven-development` | Reviewable specification and explicit assumptions |
| 2 | Architecture or cross-domain design could change the plan | `socratic` | Resolved or escalated design decisions |
| 3 | Scope is accepted and only decomposition remains | `planning-and-task-breakdown` | Ordered, verifiable tasks and checkpoints |

Negative routing examples:

- A vague idea belongs to `intent/idea-refine`, not `planning-and-task-breakdown`.
- A confirmed task list does not need `interview-me`.
- A code change during plan generation belongs to the build phase, not this family.
