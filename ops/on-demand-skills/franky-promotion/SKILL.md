---
name: franky-promotion
description: Prepare an approved promotion of Codex control-plane packages into AI Labs when explicit export is requested; hash sources, map destinations, validate registry changes, and record rollback. Do not use for live sync or ordinary commits.
metadata:
  last_reviewed: 2026-08-09
  review_interval_days: 90
---

# Franky promotion

## Contract

- **Trigger:** an explicit, approved Codex-to-AI-Labs export is requested.
- **Inputs:** approved promotion manifest, source paths, destination registry, dependency map, and rollback target.
- **Output:** hashed promotion proposal or approved export record.
- **Boundary:** never promote `.system`, credentials, sessions, or linked project contents; promotion is not live synchronization.
- **Stop:** stop on unapproved destination, hash drift, missing registry entry, or ambiguous rollback.
- **Validation:** validate the manifest and confirm exact source/destination ownership.

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
