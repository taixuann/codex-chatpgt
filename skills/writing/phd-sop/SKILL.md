---
name: phd-sop-writing
description: Draft, revise, diagnose, or evaluate a research-focused PhD Statement of Purpose from supplied evidence with voice, chronology, ownership, narrative, and claim calibration. Use only when the target application's AI/authorship policy permits the requested operation. Do not handle personal-history statements, invent facts or PI fit, predict admission, or optimize for AI-detector/watermark evasion.
metadata:
  last_reviewed: '2026-09-04'
  review_interval_days: 60
---

# PhD SOP writing

**Trigger:** A research-focused PhD SOP is being drafted, revised, compared, or reviewed from user-supplied evidence.

**Inputs:** operation mode; current draft and/or source notes; intended meaning; factual/evidence packet; target prompt and verified PI/program context when applicable; target AI-assistance policy when known; voice evidence with provenance.

**Procedure:** Load `references/authorship-policy.md` first and stop if the requested operation is not allowed. Then load `references/rubric.yaml`, `references/construct-map.yaml`, and only the progressive references needed for the task. Lock facts, chronology, ownership, uncertainty, and claim ceilings before prose. For drafting, map episodes and signals before paragraphing. For revision, preserve meaning and voice before improving expression. For review, evaluate hard gates first, then applicable sentence/pair/paragraph/document criteria without arithmetic double-counting.

**Output:** One of: evidence-bounded draft/revision; diagnostic findings; criterion-level evaluation; comparison; fit adaptation; or explicit unresolved conflicts/policy limits. Readiness is gate- and criterion-based, never a single "quality score."

**Boundary:** No fabricated facts, mechanisms, motivations, chronology, ownership, PI fit, or publication status. No native-speakerization as a human-authorship tactic. No AI-likeness score, detector gaming, watermark removal, perplexity/burstiness optimization, or deliberate degradation of prose. Do not create workflow state or final admissions acceptance.

**Stop:** Stop or narrow the operation for prohibited/unknown material AI policy, ambiguous intended meaning, material cross-document contradiction, unverified PI facts, unsupported major claims, or insufficient voice evidence for a voice judgment.

**Validation:** Run `scripts/validate_rubric.py`, `scripts/validate_references.py`, and `scripts/validate_spec_integrity.py`. A candidate is not ready while any validator fails or a material hard gate remains unresolved.
