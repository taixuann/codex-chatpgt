# Architecture decisions

`DECISIONS.md` remains the canonical, immutable decision ledger for the
current repository. This index is the migration target for future ADR links;
it intentionally does not duplicate decision prose or delete the established
ledger.

| ADR | Decision | Source |
| --- | --- | --- |
| ADR-001 | Registry authority is separate from runtime adapters | [D-001](../DECISIONS.md#d-001--registry-authority-is-separate-from-runtime-adapters) |
| ADR-002 | Workflows follow lifecycle, not persona | [D-002](../DECISIONS.md#d-002--workflows-follow-lifecycle-not-persona) |
| ADR-003 | Agents, skills, and task contracts have separate jobs | [D-003](../DECISIONS.md#d-003--agents-skills-and-task-contracts-have-separate-jobs) |
| ADR-004 | Cloud handoff is a thin coordination layer | [D-004](../DECISIONS.md#d-004--cloud-handoff-is-a-thin-coordination-layer) |
| ADR-005 | Knowledge planes remain distinct | [D-005](../DECISIONS.md#d-005--knowledge-planes-remain-distinct) |
| ADR-006 | Review is independent from execution | [D-006](../DECISIONS.md#d-006--review-is-independent-from-execution) |
| ADR-007 | General workflow semantics have one canonical source | [D-007](../DECISIONS.md#d-007--general-workflow-semantics-have-one-canonical-human-readable-source) |
| ADR-008–020 | Accepted later decisions | [DECISIONS.md](../DECISIONS.md) |

Physical per-ADR extraction is deferred until consumers are migrated; no
decision content is lost by this staged approach.
