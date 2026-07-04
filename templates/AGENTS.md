# {{NAME}} — Workspace Map

Workspace for {{TITLE}}.
The presence of `workspace.yaml` marks this directory as a workspace root: it
hosts orchestration state and clones every subrepo as a child directory.

## Key files

| File | Purpose |
|------|---------|
| `workspace.yaml` | Workspace manifest — sections, repos to clone, instances, tools. |
| `docs/` | Workspace-level planning and reference docs. |

## Commands

- `/sync` — clone or refresh every non-archived, non-optional repo-backed section in `workspace.yaml`.
- `/sync <section>` — clone or refresh a specific section (or `instance/<slug>`), including archived or optional ones.
- `/sync --dry-run` — preview what would be cloned or fetched without doing anything.
- `/status` — one-line git status per repo (root repo included).
- `/push` — commit and push pending work across the root repo and all subrepos.
- `/audit` — read-only health check: pending work, staleness, branch hygiene, drift.
- `/new-instance <slug>` — create a new instance repo from the scaffold, register it in `workspace.yaml`, clone into `instance/<slug>/`.

## Sections

Declared in `workspace.yaml`. Section keys are role-based directory names;
the `name:`/`org:` fields map them to real GitHub repos.

## Instance lifecycle

All instances live at `instance/<slug>/`, declared under the instanced section
in `workspace.yaml`. There is no "current instance" pointer in the workspace —
tools that need one keep it in their own owned directory.

1. **New**: run `/new-instance <slug>`.
2. **Retire**: set `status: archived` on the instance in `workspace.yaml`.
   The local clone stays where it is; `/sync` simply stops refreshing it.

## Cross-cutting rules

1. **One git per subrepo.** Commits, branches, and remotes are per subrepo. This
   workspace repo tracks only its own orchestration files.
2. **Never hand-edit tool-owned paths** (see `tools:` in `workspace.yaml`).
   Tools write and commit their own state.
3. **When adding a new section or repo**: update `workspace.yaml` and re-run `/sync`.
