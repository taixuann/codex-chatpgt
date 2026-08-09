---
id: RESEARCH-KNOWLEDGE-WORKFLOW
status: proposed
updated: 2026-08-09
scope: workflow-family
inherits: OPERATING-WORKFLOW-CODEX-CONTROL-PLANE
---

# Research and Knowledge Workflow

## Purpose

This document defines the shared workflow family for literature-driven scientific understanding, personal research reasoning, hypothesis formation, experiment/analysis planning, knowledge promotion, and academic output.

It extends `documentation/OPERATING-WORKFLOW.md`. Projects inherit this workflow and add only domain-specific context, validation, required comparison dimensions, and genuinely different lifecycle steps.

The workflow is objective-driven. It is not a paper-summarization pipeline.

## Core research spine

```text
OBJECTIVE / QUESTION
  ↓
ORIENT / RETRIEVE
  ↓
BUILD UNDERSTANDING
  ↓
EXTRACT / FORM CLAIMS
  ↓
ALIGN CLAIMS WITH EVIDENCE
  ↓
IDENTIFY AGREEMENT / CONFLICT / GAP
  ↓
FORM HYPOTHESES
  ↓
DERIVE PREDICTIONS / TESTS
  ↓
EXPERIMENT / ANALYZE
  ↓
VALIDATE RESULT / INTERPRETATION
  ↓
SYNTHESIZE
  ↓
PROMOTE KNOWLEDGE
  ↓
ACADEMIC OUTPUT / TYPST PROJECTION
```

Not every session must traverse the entire spine. A literature session may stop after synthesis; an experiment-planning session may begin from an existing hypothesis; a writing session should consume already reviewed claims/evidence rather than inventing scientific state inside the manuscript.

## 1. Objective / question

Start from the research purpose rather than from a pile of documents.

A useful task should establish, when applicable:

- objective;
- research question;
- why the question matters;
- expected decision or deliverable;
- scope and exclusions;
- known constraints;
- current hypothesis or uncertainty, if any.

Do not default to generic summarization when the actual need is mechanism discrimination, experimental choice, literature comparison, claim validation, or manuscript support.

## 2. Retrieval and source routing

Use the existing retrieval and evidence infrastructure rather than rebuilding it inside the workflow.

Conceptual routing:

```text
existing consolidated understanding  → Literature Wiki
personal models/questions/hypotheses → Personal Wiki
known source corpus                   → RAG / BM25 / hybrid retrieval
new external scientific evidence     → OpenScience / external research system
project/repository state              → project files / repository exploration
```

Hybrid lexical/semantic retrieval, reranking, indexing, source acquisition, and paper-access mechanics are service capabilities. This workflow consumes them; it does not duplicate their implementation.

Retrieve only evidence relevant to the active objective and preserve provenance.

## 3. Understanding layer

Convert relevant evidence into a mechanistic/conceptual model rather than accumulating independent paper summaries.

Typical structured elements may include:

- entities and state variables;
- materials/device/system classes;
- carriers or actors;
- mechanisms;
- causal/conditional relationships;
- observables;
- assumptions;
- unresolved uncertainty;
- competing explanations.

Understanding is a synthesis layer. It must remain distinguishable from sourced claims and from personal hypotheses.

## 4. Claims as the reusable scientific unit

Use claims as the primary bridge between literature, personal reasoning, experiments, and writing.

A claim record should be able to express, where useful:

```yaml
id:
claim:
status:
scope:
conditions:
evidence: []
counterevidence: []
confidence:
derived_from: []
uncertainties: []
```

The exact storage schema may remain project-/wiki-specific until real usage proves a stable canonical format.

Claims should be as atomic as practical while retaining the conditions needed for scientific validity.

## 5. Literature Wiki

The Literature Wiki represents reviewed, source-grounded understanding of what the literature supports.

It may contain:

- sourced claims;
- definitions and conceptual relationships;
- structured comparisons;
- areas of agreement/disagreement;
- methodological constraints;
- material/device/condition-specific conclusions;
- provenance to source evidence.

It must not silently convert unsupported personal beliefs into literature consensus.

## 6. Personal Wiki

The Personal Wiki represents the researcher's evolving reasoning state.

It may contain:

- personal mental models;
- research questions;
- hypotheses;
- interpretation candidates;
- experimental ideas;
- research decisions;
- uncertainty and confidence;
- links to supporting/contradicting literature claims.

Personal statements should remain explicitly distinguishable from sourced literature claims.

## 7. Claim alignment

Link personal claims/hypotheses against literature claims rather than merging the two stores.

Useful relation classes include:

- supported;
- partially supported;
- contradicted;
- conditionally compatible;
- untested;
- outside current evidence scope.

The purpose is to expose the scientific state of a proposition, not merely attach citations.

## 8. Structured literature comparison

Compare contributions along dimensions appropriate to the domain rather than only by paper.

For materials/device-physics work, candidate dimensions include:

- material/system;
- device architecture;
- physical state variable;
- carrier/species;
- transport or switching mechanism;
- fabrication/processing;
- measurement method;
- operating condition;
- observation;
- interpretation;
- limitation;
- reproducibility/reliability evidence.

Projects may add or remove dimensions. Do not globalize a domain-specific comparison schema before reuse is demonstrated.

## 9. Gap and conflict detection

Use structured comparison to identify actionable gaps such as:

- conflicting claims under apparently similar conditions;
- claims tested with insufficient discrimination between mechanisms;
- missing control experiments;
- missing material/device regimes;
- untested scaling variables;
- inconsistent methods/definitions;
- evidence that supports multiple competing explanations.

A gap should lead to a research question or decision, not simply a note that 'more work is needed'.

## 10. Hypothesis formation

A hypothesis should connect understanding, evidence, and a falsifiable prediction.

A useful hypothesis record may include:

```yaml
id:
statement:
rationale:
supporting_claims: []
contradicting_claims: []
predictions: []
tests: []
falsification:
status:
```

Do not promote a plausible narrative into a hypothesis without identifying what observation could weaken or reject it.

## 11. Predictions and tests

Translate hypotheses into discriminating measurements or analyses.

The workflow should ask:

- what observation is predicted if the hypothesis is true?
- what competing hypothesis predicts something different?
- what measurement/analysis distinguishes them?
- what controls/conditions are needed?
- what failure/ambiguous result would mean?

This is the bridge from literature reasoning to actual research execution.

## 12. Results and interpretation

Raw outputs do not enter durable knowledge directly.

Use:

```text
RAW DATA / RESULT
  ↓
ANALYSIS
  ↓
VALIDATION / REPRODUCIBILITY CHECK
  ↓
INTERPRETATION CANDIDATE
  ↓
CLAIM CANDIDATE
  ↓
SCIENTIFIC REVIEW
  ↓
PROMOTION
```

Keep measurement fact, analytical result, and interpretation conceptually separate when uncertainty matters.

## 13. Knowledge promotion

Use explicit destinations:

- sourced external claim / reviewed literature synthesis → Literature Wiki;
- personal hypothesis/model/question → Personal Wiki;
- validated project finding → project knowledge / Personal Wiki until broader promotion is justified;
- stable broadly reusable scientific understanding → Wiki after review;
- raw/original source evidence → RAG/source corpus;
- research decision → project `DECISIONS.md` when durable;
- new actionable question → research backlog / Issue when execution-worthy.

Promotion follows:

```text
OBSERVE → PROPOSE → REVIEW → ACCEPT → UPDATE
```

## 14. Academic writing as a projection

The manuscript is an output projection of reviewed scientific state, not the canonical source in which claims are first invented.

Use:

```text
PAPER OBJECTIVE / MESSAGE
  ↓
SELECT REVIEWED CLAIM SET
  ↓
ORDER CLAIMS / ARGUMENT
  ↓
MAP FIGURES + EVIDENCE
  ↓
DRAFT SECTIONS
  ↓
CLAIM–EVIDENCE / CITATION AUDIT
  ↓
REVIEW
  ↓
TYPST RENDERING
```

The writing layer should preserve traceability from manuscript statements to claim/evidence sources where practical.

## 15. Typst output layer

Typst is a preferred scholarly rendering/output layer where appropriate.

A project may maintain manuscript assets such as:

```text
manuscript/
├── main.typ
├── refs.bib
├── template.typ
├── sections/
└── figures/
```

This directory is an example, not a mandatory global repository structure.

Scientific claims, evidence state, and research decisions should remain outside the manuscript as durable knowledge where possible so that papers, reports, presentations, and future analyses can reuse the same reviewed material.

## 16. Project inheritance

A project should normally define only a compact profile over the shared workflow, for example:

```yaml
workflow_family: research-knowledge
objective:
domain:
source_scope:
required_comparison_dimensions: []
project_validation: []
outputs: []
lifecycle_extensions: []
```

A project-specific workflow/lifecycle adapter is justified only when the real domain requires materially different states, gates, or ordering.

Project-specific academic skills are appropriate for stable repeated procedures such as a validated Typst manuscript pipeline, domain-specific analysis protocol, or structured evidence extraction format. Do not create skills for one-off project context.

## 17. Relationship to agents and capabilities

Capability need comes first.

Examples:

- retrieve known literature → RAG/BM25 capability;
- acquire new external evidence → OpenScience/external evidence capability;
- scientific synthesis/critique → scientific reasoning role/capability;
- deterministic data processing → scripts/tools or implementation capability;
- independent scientific judgment → reviewer when justified;
- manuscript rendering → Typst/tooling capability.

Do not create one agent for Literature Wiki, another for Personal Wiki, another for hypothesis generation, and another for writing merely because the stages have different names.

## 18. Reproducibility and provenance

Preserve enough relation between objective, sources, methods, analysis, claims, outputs, and publication artifacts that a project can later reconstruct why a conclusion exists.

Prefer lightweight provenance first. Compatibility with richer research-object/provenance standards may be considered later if demonstrated useful; do not introduce a heavy metadata framework solely for theoretical future interoperability.

## Sustainability rules

Prefer:

- objective-driven retrieval;
- claim-centered reusable knowledge;
- explicit literature vs personal reasoning boundaries;
- source provenance;
- hypothesis falsifiability;
- project overlays rather than duplicated workflows;
- deterministic analysis where possible;
- knowledge-first academic writing;
- Typst as a rendering/output adapter rather than scientific source of truth.

Avoid:

- generic paper-summary accumulation;
- personal hypotheses masquerading as literature facts;
- raw results entering Wiki as accepted conclusions;
- one workflow per wiki/tool/output format;
- one agent per research stage;
- rebuilding existing RAG/BM25/OpenScience infrastructure inside the workflow;
- manuscript text becoming the only durable representation of scientific claims.

## Completion condition

A research/knowledge task is complete when it reaches the smallest justified stopping point in the spine, preserves the distinction between evidence, understanding, personal reasoning, and accepted claims, records unresolved uncertainty, and promotes only reviewed material to the appropriate durable knowledge plane.
