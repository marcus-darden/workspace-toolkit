# workspace-toolkit

Canonical commands, templates, and a Claude Code skill for the **workspace**
convention: one git repo that gathers and governs a family of related repos,
marked by a `workspace.yaml` manifest at its root.

A workspace clones its subrepos in place as child directories (each with its
own `.git`, gitignored by the workspace repo) and declares them all in
`workspace.yaml` — sections, per-iteration *instances* (e.g. one repo per
semester), and *tools* that own state inside the workspace. Generic slash
commands then operate on the whole family: sync, status, push, audit, and
new-instance.

- **[docs/SPEC.md](docs/SPEC.md)** — the `workspace.yaml` schema and conventions.
- **[docs/PHILOSOPHY.md](docs/PHILOSOPHY.md)** — why the system is shaped this way; rules for tools and agents.

Originally built for multi-repo college courses (coordination repo, website,
project repos, question bank, one student repo per semester), but nothing in
the convention is course-specific.

## Installation

Requirements: [Claude Code](https://claude.com/claude-code), `git`, the
[GitHub CLI](https://cli.github.com) (`gh`, used by `/new-instance` and the
scaffolding skill), and `python3` with PyYAML (`pip3 install pyyaml`, used by
the `bin/` scripts).

1. **Clone the toolkit** (the skill looks in `~/Development` by default, or
   set `$WORKSPACE_TOOLKIT` to wherever you put it):

   ```bash
   gh repo clone marcus-darden/workspace-toolkit ~/Development/workspace-toolkit
   ```

2. **Install the skill** so Claude Code can scaffold and update workspaces:

   ```bash
   mkdir -p ~/.claude/skills
   cp -R ~/Development/workspace-toolkit/skill ~/.claude/skills/workspace
   ```

That's it. The commands and scripts are *not* installed globally — the skill
copies commands into each workspace's `.claude/commands/` and the scripts into
its `bin/`, so every workspace is self-contained and works for collaborators
who have never heard of this toolkit — including ones who don't use an agent
at all: `bin/sync` and `bin/status` run directly from a shell.

## Usage

### Create a workspace

In Claude Code, in (or about) an empty directory:

> use the workspace skill to create a new workspace for my course

The skill interviews you (GitHub org, sections and their kinds, instance
naming, tools), writes `workspace.yaml` + `AGENTS.md` + `.gitignore` from the
templates, copies the five commands into `.claude/commands/` and the scripts
into `bin/`, and initializes git. Then run `/sync` to clone any repos that
already exist.

### Enable an existing repo as a workspace

The toolkit is never cloned *into* a workspace — it lives once per machine,
and what a workspace carries are **copies** of the transferable pieces. Any
existing repo becomes a workspace root the moment it has:

1. a `workspace.yaml` declaring its family of repos (start from
   `templates/workspace.yaml`; schema in `docs/SPEC.md`),
2. one `.gitignore` line per repo-backed section (`/<key>/`), plus
   `__pycache__/`,
3. `bin/` and `.claude/commands/` copied from the toolkit.

Run the same skill prompt inside the repo — create mode detects existing
content and adds around it, never overwriting files you already have. The
repo's own content stays where it is: workspace roots may carry core content;
the manifest just formalizes how the repos combine.

### Work day to day

Inside any workspace:

| Command | What it does |
|---|---|
| `/sync` | Clone missing subrepos, fetch existing ones. Never pulls, never writes. `--dry-run` to preview; `/sync <section>` to include optional/archived ones. Delegates to `bin/sync`, which you can also run directly. |
| `/ws-status` | One-line git status per repo, workspace repo included. Read-only. Delegates to `bin/status`, which you can also run directly. |
| `/push` | Commit and push pending work across every repo. Explicit-path staging, secret skipping, rebase-on-conflict with abort. Skips tool-owned paths. |
| `/audit` | Read-only health check: pending work, staleness, branch hygiene, drift between disk and manifest. Runs your `docs/audit-checklist.md` if present. |
| `/new-instance <slug>` | Create the next iteration's repo on GitHub from your template, register it in `workspace.yaml`, clone into `instance/<slug>/`. |

### Update a workspace's commands

When the toolkit improves, refresh any workspace from inside it:

> use the workspace skill to update this workspace

The skill diffs the workspace's commands against the toolkit's, shows you each
difference, and asks per file: take the toolkit version, keep yours, or
**upstream** yours into the toolkit (bumping `VERSION`) so other workspaces
can pick it up.

### Manual use (no skill)

Copy `commands/*.md` into `<workspace>/.claude/commands/` and `bin/` into
`<workspace>/bin/`, start from `templates/workspace.yaml`, and gitignore each
section directory. The templates' `{{PLACEHOLDERS}}` mark what to fill in.

## Repository layout

| Path | Purpose |
|------|---------|
| `docs/SPEC.md` | The workspace.yaml schema and conventions. |
| `docs/PHILOSOPHY.md` | Design rationale and rules for tools/agents operating in workspaces. |
| `commands/` | Canonical generic commands, copied into each workspace's `.claude/commands/`. |
| `bin/` | The `sync`/`status` scripts and shared manifest parser, copied into each workspace's `bin/`. |
| `templates/` | Skeletons for scaffolding: `workspace.yaml`, `AGENTS.md`, `README.md`, `CLAUDE.md`, `gitignore`. |
| `skill/` | The Claude Code skill (`workspace`) — copy to `~/.claude/skills/workspace`. |
| `VERSION` | Toolkit version, read by the skill's update mode. |

## Contributing / updating the toolkit

Commands here are the source of truth. When a workspace improves a command,
upstream the change here (the skill's update mode automates this), bump
`VERSION`, and run update mode in your other workspaces.
