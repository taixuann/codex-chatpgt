---
name: franky-promotion
description: Promote approved Codex-first Franky skills and workflows into AI Labs with hashes, dependency metadata, registry destinations, validation evidence, and rollback information. Use after a Codex package is stable and human-approved.
---

# Franky promotion

Promotion is an explicit export step, not a live sync.

1. Read the approved goal package and `PROMOTION.yaml`.
2. Confirm each source is under the approved Codex workbench and each
   destination is under the AI Labs control plane.
3. Hash source artifacts and record exact destination paths.
4. Promote only approved Franky packages and workflow metadata; never promote
   `.system` packages or linked project contents.
5. Update AI Labs registries and platform links only when the manifest names
   those destinations.
6. Record validation and rollback evidence in the goal walkthrough.

Use `scripts/create_promotion_manifest.py` to generate deterministic artifact
records before proposing a promotion.
