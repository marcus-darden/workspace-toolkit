# Workspace Specification

A **workspace** is a git repository that gathers and governs a family of related
git repositories. The presence of `workspace.yaml` at a directory's root marks it
as a workspace (the way `Cargo.toml` marks a Rust crate). Subrepos are cloned in
place as child directories, gitignored by the workspace repo, and each keeps its
own `.git` — the workspace repo tracks only its own orchestration files
(`workspace.yaml`, `.claude/`, docs, templates, scripts, tool directories).

Originally built for multi-repo college courses (course content, projects,
website, per-semester student repos), but nothing in the convention is
course-specific.

## workspace.yaml

```yaml
version: 1                      # schema version

org: my-github-org              # default GitHub org for every repo below

tools:                          # optional — tools that own state in this workspace
  <tool-name>:
    dir: <tool-name>            # tool-owned root directory
    owned:                      # optional globs, matched in every repo
      - "**/.<tool-name>/"

sections:                       # key = local directory name (role-based)
  <key>: ...                    # one of the four section kinds below
```

### Section kinds

| Kind | Indicator | Local path | GitHub repo |
|---|---|---|---|
| Single repo | *(default)* | `<key>/` | `name:` if set, else `<key>` |
| Folder | `folder: true` + `repos:` | `<key>/<entry.name>/` | `entry.name` |
| Local | `local: true` | `<key>/` | *(none)* |
| Instanced | `instanced: true` | `<key>/<slug>/` | `repo:` template with `{slug}` |

### Common fields (section, folder entry, or instance)

| Field | Meaning |
|---|---|
| `name:` | GitHub repo name when it differs from the key. |
| `org:` | Org override. Resolution: `entry.org → section.org → top-level org`. |
| `role:` | Descriptive label surfaced in command output. |
| `description:` | Free text. |
| `status: archived` | Retired. Skipped by default `/sync` and staleness audits; loaded when explicitly named. |
| `optional: true` | Active but not universally needed. Skipped by default `/sync`; loaded when explicitly named. |

### Instanced sections

An instanced section holds repos that are copied-and-reused per iteration
(semesters, cohorts, annual editions). Conventionally the key is `instance`.

| Field | Meaning |
|---|---|
| `repo:` | Repo-name template, e.g. `mycourse-{slug}`. The only place a naming prefix lives. |
| `description:` | Optional description template with `{slug}`. |
| `scaffold:` | Workspace-relative path to the local skeleton `/new-instance` seeds new repos from. |
| `post_create:` | Optional text `/new-instance` prints as next steps. |
| `instances:` | List of `{slug, status?, description?}`. |

**There is no "current instance" pointer in the workspace.** All non-archived
instances are equal. A tool that needs a current/active notion keeps it in its
own owned directory.

Retiring an instance = setting `status: archived`. Nothing moves or gets
deleted; the local clone stays (the remote is canonical) and `/sync` stops
refreshing it.

### Tools

A tool (dashboard, ingestion agent, automation) registers under `tools:` and
owns exactly one root directory (`dir:`) plus optional `owned:` globs matched
inside every repo. The boundary:

- Generic commands never hand-edit or stage tool-owned paths.
- Humans read tool-owned state but don't write it.
- Tools commit their own state and keep tool-specific data (e.g. an
  active-instance pointer, ingestion manifests) inside their owned paths —
  never at the workspace root.

## Commands

Copied into each workspace's `.claude/commands/` (see the scaffolding skill).
Every command is a **pure interpreter of workspace.yaml**: no repo-name
prefixes, scaffold paths, tool names, or layout rules may be hardcoded.

| Command | Contract |
|---|---|
| `/sync` | Clone missing / fetch existing per workspace.yaml. Never pulls, never writes files, never edits workspace.yaml. |
| `/status` | One-line git status per present repo, root repo included. Read-only. |
| `/push` | Commit + push pending work everywhere. Explicit-path staging, secret skipping, rebase-on-conflict with abort. Skips tool-owned paths. |
| `/audit` | Read-only health check: pending work, staleness, branch hygiene, drift between disk and workspace.yaml, instance consistency. Domain rules live in the workspace's own `docs/audit-checklist.md`, which /audit runs if present. |
| `/new-instance <slug>` | Create the GitHub repo from `repo:` template + `scaffold:`, register the slug, clone into `<key>/<slug>/`. |

## Conventions

- `.gitignore` in the workspace repo ignores every repo-backed section path and
  `/instance/*/` (scaffold/templates stay tracked).
- `CLAUDE.md` is a one-liner pointing at `AGENTS.md`; `AGENTS.md` is the
  workspace map (key files, commands, lifecycle, cross-cutting rules).
- Domain knowledge (course plans, style guides, checklists) lives in the
  workspace's `docs/` and per-repo files — never in commands.
