# Workspace Specification

A **workspace** is a git repository that gathers and governs a family of related
git repositories. The presence of `workspace.yaml` at a directory's root marks it
as a workspace (the way `Cargo.toml` marks a Rust crate). Subrepos are cloned in
place as child directories, gitignored by the workspace repo, and each keeps its
own `.git`. The workspace repo tracks its own content: orchestration
(`workspace.yaml`, `.claude/`, `bin/`, docs, templates, tool directories) and —
when it makes sense — core content of its own. What defines a workspace is not
emptiness but the manifest: it formalizes how multiple repos combine.

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

## Scripts (bin/)

The mechanical operations are plain scripts, copied into each workspace's
`bin/` so humans can run them without an agent. Requirements: `python3` with
PyYAML (`pip3 install pyyaml`).

| Script | Contract |
|---|---|
| `bin/sync` | Clone missing / fetch existing per workspace.yaml. Named-section and `--dry-run` arguments; naming a section overrides `optional`/`archived`. Never pulls, never writes a subrepo's files, never edits workspace.yaml. Ends with a needs-attention list (dirty, ahead, detached HEAD). |
| `bin/status` | One-line git status per present repo, workspace root first. Read-only and network-free; flags uncommitted work, ahead-of-upstream, and non-default branches. Never clones or fetches. |
| `bin/_workspace.py` | The reference workspace.yaml parser, shared by both so they cannot disagree. Generic by rule: nothing workspace-specific may enter it. |

## Commands

Copied into each workspace's `.claude/commands/` (see the scaffolding skill).
Every command is a **pure interpreter of workspace.yaml**: no repo-name
prefixes, scaffold paths, tool names, or layout rules may be hardcoded.
`/sync` and `/ws-status` delegate to the `bin/` scripts — one implementation
for humans and agents.

| Command | Contract |
|---|---|
| `/sync` | Runs `bin/sync` and relays its output. |
| `/ws-status` | Runs `bin/status` and relays its output. (Named `ws-status`: `/status` shadows a CLI built-in.) |
| `/push` | Commit + push pending work everywhere. Explicit-path staging, secret skipping, rebase-on-conflict with abort. Skips tool-owned paths. |
| `/audit` | Read-only health check: pending work, staleness, branch hygiene, drift between disk and workspace.yaml, instance consistency. Domain rules live in the workspace's own `docs/audit-checklist.md`, which /audit runs if present. |
| `/new-instance <slug>` | Create the GitHub repo from `repo:` template + `scaffold:`, register the slug, clone into `<key>/<slug>/`. |

## Conventions

- `.gitignore` in the workspace repo ignores every repo-backed section path,
  `/instance/*/` (scaffold/templates stay tracked), and `__pycache__/`.
- `CLAUDE.md` is a one-liner pointing at `AGENTS.md`; `AGENTS.md` is the
  workspace map (key files, commands, lifecycle, cross-cutting rules).
- Domain knowledge (course plans, style guides, checklists) lives in the
  workspace's `docs/` and per-repo files — never in commands.
