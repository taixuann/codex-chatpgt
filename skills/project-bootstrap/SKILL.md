---
name: project-bootstrap
description: Bootstrap or minimally extend greenfield and brownfield scientific or file-first projects by inspecting requirements, selecting the smallest justified artifact surface, building an artifact map, and safely materializing files. Use when a user asks to set up, initialize, scaffold, or add related Markdown/YAML/JSON/Typst/data artifacts to a project without assuming a code-first repository.
---

# Project Bootstrap

Use this skill to turn a bounded project request into the smallest useful file
surface. Keep reasoning and project-surface selection here; use the bundled
script only for deterministic validation and materialization.

## Procedure

1. Inspect the target path before writing. Classify it as `new` or `existing`,
   read applicable `AGENTS.md` and project conventions, and list requested
   outputs.
2. Inspect existing capabilities before creating anything. Reuse relevant
   project-linking, documentation, research, or workflow skills. Do not create
   a skill per file format or duplicate global agents/workflows.
3. Select only modules justified by the request. Typical experimental
   boundaries are `metadata/`, `data/raw/`, `data/processed/`, `analysis/`,
   and `results/`; add `samples/`, `figures/`, `manuscript/`, or `tools/` only
   when the request gives them a distinct purpose.
4. Build an artifact map before materialization. Every artifact needs a relative
   `path`, `purpose`, and string `content` for `create`/`update`. Add `format`,
   `depends_on`, `links`, and `intent` (`create`, `update`, or `preserve`) when
   material. Dependencies must name another declared artifact.
5. Keep shared knowledge external. Represent Literature Wiki, Personal Wiki,
   RAG, or OpenScience as `external://...` links; never copy their trees into
   the project.
6. Run a dry-run first:

   ```text
   python3 skills/project-bootstrap/scripts/bootstrap_file_project.py MAP.yaml PROJECT_ROOT
   ```

7. Review the actions and then use `--apply` only when the map is correct:

   ```text
   python3 skills/project-bootstrap/scripts/bootstrap_file_project.py MAP.yaml PROJECT_ROOT --apply
   ```

8. Re-read the resulting tree. Confirm raw data is unchanged, declared files
   exist, unrelated files remain intact, optional modules were not emitted, and
   external knowledge was referenced rather than copied.

## Safety boundaries

- Treat `data/raw/` as immutable. Use `preserve` for existing raw files; never
  create or update them through bootstrap.
- Keep paths relative and normalized. The materializer rejects traversal,
  absolute/Windows paths, NUL bytes, control-plane directories, duplicate
  paths, symlink paths, and unsafe targets.
- Existing projects must already have a directory root. Do not reorganize
  unrelated content or overwrite a file through a symlink.
- A failed validation must stop before writing. Repair the map, rerun dry-run,
  and only then apply.
- Stop and return to the user when the target is ambiguous, a requested change
  would migrate/delete existing content, or the request requires a new
  lifecycle/ontology rather than file materialization.

## Ownership boundaries

This skill does not define global-to-project inheritance (#10), scientific
reasoning or knowledge promotion (#16), external evidence acquisition (#7), or
Goal/PLAN graph semantics (#17). It creates requested files and references those
systems; their existing owners remain authoritative. It is not a workflow
engine and does not spawn recursive agents.

## Bundled deterministic primitive

`scripts/bootstrap_file_project.py` validates the artifact map and performs
atomic per-file create/update operations after all targets pass preflight. Its
tests cover adaptive selection, greenfield/brownfield behavior, dry-run/apply,
raw-data protection, dependency/link checks, malformed input, and symlink/path
hardening. Do not bypass the script with ad hoc file writes for a request that
matches this skill.
