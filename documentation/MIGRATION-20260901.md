# Documentation and ADR migration record

## Decision

Documentation is organized by subject for discovery, while bounded execution
records remain under `sessions/` and GitHub remains the lifecycle authority.

## Preservation boundary

This migration is additive. Existing canonical documents and historical
surfaces (`DECISIONS.md`, `plans/`, `reviews/`, `handoffs/`, and all session
packets) are retained unchanged because active validators and historical links
consume them. No raw evidence, authored text, or work record is removed.

## Mapping

| Subject path | Existing authority |
| --- | --- |
| `architecture/` | `AGENT-BOUNDARIES.md` |
| `workflow/` | `OPERATING-WORKFLOW.md`, `SYSTEM-EVOLUTION-WORKFLOW.md` |
| `knowledge/` | `PERSONAL-WIKI-MCP-V1.md`, `RESEARCH-KNOWLEDGE-WORKFLOW.md` |
| `decisions/` | `DECISIONS.md` |
| `sessions/` | existing session packets |
| `archify/` | derived architecture evidence |

The new files are pointers and indexes, not competing sources of truth.
