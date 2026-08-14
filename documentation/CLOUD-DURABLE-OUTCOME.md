---
id: CLOUD-DURABLE-OUTCOME
status: active
updated: 2026-08-14
scope: cloud-operation-project-source
---

# Cloud durable-outcome procedure

Use this document as the concise Project Source for a Cloud operation. The
canonical lifecycle, role boundaries, and artifact meanings remain in
[`OPERATING-WORKFLOW.md`](OPERATING-WORKFLOW.md) and the scoped `AGENTS.md`;
this procedure does not replace or restate them.

## Procedure

1. **Orient.** Read the active Issue, applicable instructions, and only the
   canonical/live state material to the operation. Identify confirmed facts,
   assumptions, unresolved uncertainty, the durable destination, and the
   evidence needed for acceptance.
2. **Plan the outcome.** State what must become durably true and the smallest
   change surface. For repository work, first check for an active owning
   branch/PR, then use one Issue/work-unit branch and one draft PR targeting
   fresh `main`.
3. **Execute and repair in place.** Keep implementation, deterministic
   validation, CI diagnosis/repair, review repair, and documentation
   reconciliation on that branch and PR. Classify failures before bounded
   repair; do not create repair/reviewer branches or a second PR.
4. **Present evidence.** In the PR map each acceptance criterion to a changed
   artifact, deterministic check, or review result. Record limitations,
   deviations, unresolved failures, and any explicit waiver; a green check
   alone is not acceptance.
5. **Decide readiness.** Mark ready for merge only when the diff matches the
   Issue, required checks pass on the current head, required review is
   satisfied, documentation agrees with behavior, and no material failure or
   uncertainty is hidden. Otherwise keep the PR draft or escalate.
6. **Close durably.** After human-approved merge, verify the accepted result on
   `main`, close/link the Issue as appropriate, and delete the work-unit branch.
   Record only accepted durable state or knowledge. The normal evolution result
   is `NO ACTION`; observation never directly changes policy.

## Required closeout

Return the Issue/PR links, final head revision, acceptance-criteria evidence,
checks and review status, deviations/waivers, durable destination, and cleanup
status. Stop before merge unless the operator explicitly authorizes merging.
