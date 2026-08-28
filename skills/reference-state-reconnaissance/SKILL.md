---
name: reference-state-reconnaissance
description: Inspect a bounded reference or current-state surface and report authoritative facts, drift, and provenance gaps; do not edit, promote, or approve state.
metadata: {last_reviewed: 2026-08-28, review_interval_days: 90}
---

# Reference-state reconnaissance

Use this read-only profile to answer what a named reference, registry, config,
manifest, or current repository state actually contains and whether relevant
surfaces agree. It is a factual state-reconnaissance capability, not a
workflow engine, planner, reviewer, or state mutator.

## Trigger and routing

Positive triggers include “check the current state,” “compare this reference
with the live manifest,” “find drift,” and “what is authoritative right now?”
Oblique triggers include “verify the handoff against the registry” and “locate
the current version before execution.”

Do not use for changing configuration, accepting a change, designing
architecture, implementing code, interpreting scientific evidence, or creating
a session subsystem. Route repository structure questions to
`codebase-reconnaissance`, source discovery to `research-source-discovery`,
and lifecycle recording to `session-packet-management`.

## Inputs

Accept the exact reference/current-state question, named surfaces, comparison
dimensions, authority order if supplied, timestamp/revision boundary, and
consumer. Follow the shared [reconnaissance kernel](../references/reconnaissance-kernel.md),
then:

Before inspection, resolve the consumable [Argus source-map contract](../references/argus-reference-source-contract.yaml)
and record intent, bounded path/source/service retrieval, scope, authority,
priority, load strategy, freshness, and validation state.

- identify each surface and its source state, commit/hash, timestamp, and
  ownership;
- classify authority, artifact, and relationship categories before comparing;
- compare only requested fields or relationships, reporting additions,
  removals, conflicts, and stale references with exact locations;
- distinguish observed drift from an inferred cause; do not repair it;
- identify freshness, supersession, and current-state status, then return a
  bounded packet containing the comparison and exclusions;
- check coverage and state which surfaces were not inspected.

Never treat a local adapter, generated file, retrieved session text, or
documentation statement as canonical without the declared authority chain.
Never modify, archive, index, promote, or approve any surface.

## Output, boundary, stop, and validation

Return a bounded state handoff with question/scope; authoritative source
inventory; observed values and comparison anchors; drift/conflicts; freshness
and provenance; gaps/exclusions; unknowns; and the exact parent/human action
needed. Native runtime selection, skill loading, and host permission behavior
remain `NOT_ASSESSED` unless directly observed.
**Boundary:** read-only state observation and comparison; no repair, promotion,
approval, implementation, planning, interpretation, or session ownership.

**Stop:** stop on authority conflict, missing provenance, protected content, or
insufficient comparison scope.

**Validation:** report exact surface anchors, source state, compared fields,
uninspected areas, and `NOT_ASSESSED` runtime behavior.

## Required GENERAL/REFERENCE evidence

Classify each item as authority, artifact, or relationship; identify the
authoritative source and artifact identity; compare requested relationships;
check freshness, supersession, and current-state status; and return a bounded
packet with exact anchors, conflicts, uninspected surfaces, and exclusions.
Do not infer causality from drift and do not promote a reference over its
declared authority chain.

## Upstream adaptation

Retained: minimal authority/artifact/relationship concepts from
`Cantara/knowledge-context-protocol/SPEC.md` at
`ce893716ead0e946966074d738d6766ea2196700` (Apache-2.0; license anchor
`261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64`). Modified: only bounded
reference/current-state comparison. Removed/rejected: wholesale KCP protocol,
state mutation, and independent lifecycle/session ownership. Added: freshness,
supersession, and explicit bounded packet output.
