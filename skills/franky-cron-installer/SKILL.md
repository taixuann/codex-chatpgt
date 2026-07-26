---
name: franky-cron-installer
description: Install, update, validate, and retire approved Franky scheduler or cron-job definitions with explicit scope, collision checks, timezone review, approval gates, and rollback evidence. Use when Franky must manage recurring operator jobs; audits remain read-only unless a workflow authorizes a change.
---

# Franky cron installer

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
