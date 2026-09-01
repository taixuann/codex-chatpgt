---
name: scientific-evidence-synthesis
description: Synthesize supplied, project, or explicitly retrieved scientific evidence for a bounded question while calibrating claims and preserving alternatives; do not execute project analysis or accept scientific conclusions.
---

# Scientific evidence synthesis

Use when a bounded scientific question has identifiable evidence and needs a
provenance-preserving interpretation. This is a candidate reusable procedure,
not a workflow or knowledge store.

Inputs: question and scope, evidence references, project/method context when
applicable, desired output, exclusions, and stop conditions.

Procedure:

1. State the question and claim boundary.
2. Classify each item as `observation`, `sourced_claim`, `inference`,
   `hypothesis`, `uncertainty`, or `unsupported_or_unknown`.
3. Map support, counterevidence, competing explanations, assumptions, and
   evidence gaps. Keep source relevance separate from claim support.
4. Calibrate status as `SUPPORTED`, `PARTIALLY_SUPPORTED`,
   `INSUFFICIENT_EVIDENCE`, `CONFLICTING_EVIDENCE`, or
   `REQUIRES_ADDITIONAL_MEASUREMENT`.
5. State the strongest licensed claim, what remains unknown, and the next
   discriminating evidence or test.

Stop and abstain when provenance is missing, evidence conflicts materially, or
the requested claim exceeds the available support. Route context/provenance
gaps to Argus/parent, implementation gaps to Prometheus/project tooling, and
consequential interpretation to Athena/Human. Do not mutate files or project
state.
