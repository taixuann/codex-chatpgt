---
name: skill-retrospective
description: Review a named skill or a completed workflow when the user explicitly asks to collect reusable lessons, assess skill usefulness, or improve a skill. Produce observations and proposed changes in chat only; never activate automatically or write logs, schedules, or skill files without explicit approval.
---

# Skill retrospective

This is a Codex adaptation of Eoghan Henn's *One Skill to Rule Them All* by
Rebelytics, licensed under CC BY 4.0. Source:
https://github.com/rebelytics/one-skill-to-rule-them-all. It is changed to be
an explicit, non-persistent retrospective: it does not install hooks, monitor
sessions, create observation logs, schedule reviews, or change skills.

## Review a bounded episode

1. Confirm the target skill or completed workflow and gather only its relevant
   prompts, outputs, validation evidence, user corrections, and friction.
2. Separate observed facts from inferences. Identify the smallest reusable
   lesson, its trigger, counterexamples, and evidence needed to validate it.
3. Return a concise proposal: keep, adapt, split, merge, archive, or create a
   skill. State the expected benefit, risks, affected paths, and validation.
4. Do not write an observation file, modify a skill, stage a change, or create
   a schedule unless the user explicitly approves that specific action. Route
   approved skill edits through the local `skill-creator` procedure and scoped
   `AGENTS.md` policy.

## Boundaries

- Do not run automatically at session start or after tool calls.
- Do not use a universal routing hook or override role/workflow selection.
- Do not retain personal, project, or session data outside the conversation
  without the user's explicit approval.
