# Calibration protocol

This harness measures evaluator reliability; it does not establish rubric validity by itself.

## Required provenance for a real calibration run

Record:
- judge/model identifier;
- model/version when available;
- reasoning/config;
- rubric revision;
- anchor-set revision;
- fixture revision;
- evaluation-prompt revision;
- run date.

Use adjudicated `USER_GOLD`, `EVIDENCE_GOLD`, or `RUBRIC_GOLD` separately from model agreement. Two models agreeing can still be wrong.

## Metrics

For ordinal 1–5 criteria:
- exact agreement;
- adjacent agreement (distance <= 1);
- score-distance distribution;
- weighted Cohen's kappa when exactly two judge streams cover the same items.

Kappa is diagnostic. No universal kappa threshold proves validity.

For contrastive/pairwise cases:
- winner agreement;
- whether the winner was selected for the expected reason, when a reason code is supplied.

Disagreement >1 point on a hard-gate-adjacent criterion should trigger anchor/rubric review, not averaging.

The committed `calibration-sample.json` is a **harness self-test only**. It is synthetic and cannot be cited as behavioral evidence for the skill.
