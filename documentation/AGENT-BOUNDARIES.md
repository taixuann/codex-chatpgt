---
id: AGENT-BOUNDARIES
status: active
updated: 2026-08-14
---

# Canonical roles and support boundaries

This document explains the call boundary; it does not define a new role
registry or workflow. Canonical role meaning remains owned by the AI Labs
registry and definitions named in [`../agents/AGENTS.md`](../agents/AGENTS.md).

## When to call each role

| Role | Call when | Do not call for | Boundary and handoff |
| --- | --- | --- | --- |
| Argus | context discovery, repository mapping, provenance audit, or uncertainty detection is needed before execution | scientific interpretation, implementation, review decisions, or canonical-state changes | `REQUEST -> CONTEXT -> HANDOFF`; return evidence, paths, and uncertainty to the parent, Prometheus, or Athena |
| Feynman | scientific reasoning, source verification, claim/evidence comparison, or methodology/protocol review is needed | coding, project mutation, control-plane maintenance, or final scientific acceptance | return provisional, provenance-preserving findings; escalate scientific decisions to the human owner |
| Prometheus | an approved implementation, test, diff, documentation, or artifact-lifecycle validation is needed | scientific decisions, Argus provenance work, global policy, agent-contract changes, or independent acceptance | `HANDOFF -> EXECUTION -> VALIDATION -> RESULT`; request Athena review or Franky control-plane handling when crossing those boundaries |
| Athena | an independent review of implementation, evidence, claims, conflicts, or readiness is justified after execution/validation | implementation edits, self-approval, role/policy mutation, or canonical-state promotion | `RESULT -> REVIEW -> DECISION SUPPORT`; return severity-ranked findings to the parent and never approve itself |
| Franky | workflow/control-plane routing, registry/platform maintenance, instruction or adapter maintenance, or approved handoff preparation is needed | linked project contents, scientific work, recursive orchestration, or unreviewed policy/security mutation | operate through `franky.task.v1` and return `franky.result.v1`; human approval remains the promotion boundary |

## Canonical versus support

Feynman, Prometheus, and Franky are the only canonical planning roles. Argus
and Athena are non-canonical support adapters and bounded leaf workers; their
presence under `agents/` does not expand the external role registry.

The capability repertoire is an eligibility and forbidden-capability record,
not a role-definition source. The lifecycle registry in
`manifests/agent-contracts.yaml` is limited to the Argus/Prometheus/Athena
shared evidence and artifact boundary. Neither manifest can override the
canonical registry, adapter permissions, or repository runtime policy.

## Runtime limitations

Static configuration and deterministic validators do not prove host behavior.
The following remain explicitly `NOT_ASSESSED` in v1:

- native host agent selection and dispatch;
- native skill loading and model-mediated skill selection;
- runtime mutation enforcement;
- host permission enforcement.

No configuration check or documentation statement should be presented as proof
of any of these runtime behaviors.
