# Session record mapping

| Scope | Canonical record | Required evidence |
| --- | --- | --- |
| Routine | Issue / optional PLAN / PR / CI | objective, validation, review, Git commit |
| Machine/audit-required | named task-contract record | named consumer, validation, rollback, Git commit |
| Multi-component | `GOAL.md`, `PLAN.md`, `TASKS.md` | task state, validation, bounded plan |
| Architectural or promotion | Full `GOAL-*` package | walkthrough, revisions, promotion metadata, human approval |

Do not create a full goal package solely because a session ended. Choose the
smallest record that preserves the decision and evidence.
