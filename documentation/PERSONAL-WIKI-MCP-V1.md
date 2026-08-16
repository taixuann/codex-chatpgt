---
id: PERSONAL-WIKI-MCP-V1
status: proposed
updated: 2026-08-16
---

# Personal Wiki MCP v1 foundation

This document defines the smallest reusable contract for a future Personal
Wiki MCP capability. It is a context and proposal surface, not a runtime MCP
implementation or a second scientific-evidence system.

## Purpose

Personal Wiki stores the researcher's reusable, explicitly personal
understanding: mental models, questions, hypotheses, interpretation
candidates, uncertainty, and method heuristics. It may help Feynman reason
across projects, but it is not project authority, literature evidence, or
scientific acceptance.

Scientific Wiki remains the literature/evidence capability owned by Issue #7.
Project manifests, methods, results, and accepted project knowledge remain
owned by the project.

## Read and write boundary

| Operation | v1 contract |
| --- | --- |
| Read | Feynman may consume a bounded artifact when Personal Wiki availability is configured and probed. Current project authority always outranks it. |
| Draft write | Feynman or a parent may produce a provenance-bearing draft or promotion proposal; this is not an automatic Personal Wiki write. |
| Accept/write | The Personal Wiki owner or an explicitly authorized human-controlled consumer accepts or writes an artifact. |
| Project/Scientific Wiki write | Forbidden through this capability. Use the owning project or Issue #7 boundary. |
| Synchronization | Not implemented; no automatic or bidirectional sync. |

Model memory is never provenance. A Personal Wiki artifact must preserve its
source references, capture time, producer, and authority status.

## Artifact and provenance

`ops/schemas/personal-wiki-artifact.schema.yaml` defines
`personal-wiki.artifact.v1`. The checked-in example is intentionally a draft
context artifact with a promotion proposal, not an accepted scientific claim.
Each claim points to evidence or an explicit unknown; unsupported personal
statements remain labeled as such.

## Feynman consumption

Feynman consumes Personal Wiki artifacts as `reusable_context` only:

```text
Personal Wiki artifact
  -> provenance/authority check
  -> Feynman bounded context
  -> calibrated reasoning against current project evidence
```

Feynman must not silently promote Personal Wiki context into project state,
Scientific Wiki evidence, or a final scientific decision. Missing, stale, or
conflicting context routes to Argus/parent and remains `NOT_ASSESSED` when the
runtime cannot be probed.

## Promotion proposal flow

```text
DRAFT personal artifact
  -> provenance and claim check
  -> PROPOSED promotion (optional)
  -> independent/project or human review
  -> owner-controlled acceptance or rejection
```

Promotion proposals carry a target and rationale but do not perform writes.
They may target project knowledge or another explicitly authorized personal
context destination; they may not replace Scientific Wiki or create a graph,
database, or synchronization service.

## Explicit non-goals

- automatic synchronization;
- bidirectional mutation;
- graph database or knowledge graph;
- duplicate RAG/retrieval backend;
- replacing Scientific Wiki;
- native per-agent MCP permissions or runtime dispatch claims.
