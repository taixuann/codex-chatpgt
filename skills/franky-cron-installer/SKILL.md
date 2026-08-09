---
name: franky-cron-installer
description: Validate, install, or retire an approved recurring Franky/Codex job when schedule state changes; check identifier, timezone, overlap, scope, secrets, approval, and rollback. Audits remain read-only unless the selected workflow authorizes mutation.
metadata:
  last_reviewed: 2026-08-09
  review_interval_days: 90
---

# Franky cron installer

## Contract

- **Trigger:** a governed recurring scheduler definition must be created, changed, or retired.
- **Inputs:** job identifier, owner, cadence/timezone, prompt source, output, retry policy, and current registration.
- **Output:** collision-safe schedule proposal or approved mutation with rollback metadata.
- **Boundary:** do not touch arbitrary user automations, credentials, or project schedulers.
- **Stop:** stop on duplicate IDs, ambiguous timezone, secret material, or missing approval.
- **Validation:** run scheduler/scope validators and verify the exact destination and overlap lock.

Use this skill only as the cron operation within a selected Franky workflow.
It prepares deterministic inventory and change plans for schedulers, cron
definitions, Codex automations, and related output paths.

## Required behavior

1. Inventory the scheduler, job identifier, owner, timezone, prompt source,
   output destination, retry policy, and current status.
2. Refuse duplicate identifiers, ambiguous schedules, secrets in definitions,
   stale prompt paths, and writes outside the approved control-plane scope.
3. Treat audit and plan as read-only operations.
4. Require explicit human approval before create, update, enable, disable, or
   delete operations.
5. Produce a before/after schedule diff, validation evidence, and reversible
   rollback instructions.

Inventory, validation, and apply planning must be runnable deterministically
from the declared job definition and filesystem state; an LLM is optional only
for ambiguous interpretation and is never required for mechanical cron checks.
Validate job inputs, outputs, and cache policy with the Franky maintenance
IO/cache validator before apply.

Never create a recurring job implicitly, and never use a scheduler to execute
against linked research-project contents without an explicit approved handoff.

The scheduled Franky personal-skill maintenance job is the only unattended
exception: it may update an existing personal skill only, after deterministic
scope and clean-tree checks. New skills and all other component types remain
manual and approval-gated.
