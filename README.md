# workspace-toolkit

Canonical commands and templates for the **workspace** convention: one git repo
that gathers and governs a family of related repos, marked by a `workspace.yaml`
at its root. See [docs/SPEC.md](docs/SPEC.md) for the full specification.

## Layout

| Path | Purpose |
|------|---------|
| `docs/SPEC.md` | The workspace.yaml schema and conventions. |
| `commands/` | Canonical generic commands (`/sync`, `/status`, `/push`, `/audit`, `/new-instance`), copied into each workspace's `.claude/commands/`. |
| `templates/` | Skeleton files for scaffolding a new workspace (`workspace.yaml`, `AGENTS.md`, `README.md`, `CLAUDE.md`, `gitignore`). |
| `VERSION` | Toolkit version, read by the scaffolding skill's update mode. |

## Usage

The `workspace` skill in `~/.claude/skills/workspace/` drives this repo:

- **Create**: interviews you for org/sections, copies templates and commands
  into a new workspace, initializes git.
- **Update**: diffs a workspace's `.claude/commands/` against `commands/` here
  and refreshes them on confirmation.

Manual use works too — copy `commands/*` into `<workspace>/.claude/commands/`
and start from `templates/workspace.yaml`.

## Updating the toolkit

Commands here are the source of truth. When a workspace improves a command,
upstream the change here and bump `VERSION`, then run the skill's update mode
in other workspaces.
