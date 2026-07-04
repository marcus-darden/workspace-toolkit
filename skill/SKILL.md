---
name: workspace
description: Create or update a multi-repo "workspace" (a git repo with a workspace.yaml manifest that gathers and governs a family of repos). Use when the user wants to scaffold a new workspace for a course or major multi-repo project, or to refresh an existing workspace's generic commands (/sync /status /push /audit /new-instance) from the workspace-toolkit.
---

# Workspace — create or update

A **workspace** is a git repo whose `workspace.yaml` declares sections (subrepos
cloned in place, gitignored, each with its own `.git`), instances, and tools.
Full spec: `docs/SPEC.md` in the toolkit; rationale: `docs/PHILOSOPHY.md`.

## Step 0 — Locate the toolkit

Find the local clone of `workspace-toolkit`, checking in order:

1. `$WORKSPACE_TOOLKIT` (environment variable), if set.
2. `~/Development/workspace-toolkit`
3. `~/iclouddrive/Development/workspace-toolkit`
4. A `workspace-toolkit/` sibling of the current directory.

(Quote paths — they may contain spaces.) If none exists, offer to
`gh repo clone marcus-darden/workspace-toolkit` into `~/Development/`.
**Never proceed without the toolkit** — do not reconstruct commands or
templates from memory; they drift.

## Step 1 — Pick the mode

- `workspace.yaml` exists in the current directory (or the directory the user
  named) → **update mode**.
- Otherwise → **create mode**.

If ambiguous, ask.

## Create mode

1. **Interview** (skip anything the user already stated):
   - Workspace name and target directory.
   - Default GitHub org.
   - Sections, looping until done. For each: key (role-based directory name,
     e.g. `course`, `website`), kind (single repo / `folder: true` multi-repo /
     `local: true` / `instanced: true`), `name:` override if the repo name
     differs from the key, `org:` override, `optional: true`?
   - If any section is instanced: the `repo:` name template (e.g.
     `mycourse-{slug}`), whether a local scaffold should exist (default
     `templates/instance/`), and any initial instance slugs.
   - Tools to register (default: none). For each: name → `dir:` = the name,
     plus any `owned:` globs.
2. **Scaffold** the directory:
   - Copy `toolkit/templates/*` in: `workspace.yaml`, `AGENTS.md`, `README.md`,
     `CLAUDE.md`, and `gitignore` → `.gitignore`.
   - Fill every `{{PLACEHOLDER}}` and replace the commented example sections
     with the interviewed sections. Add one `.gitignore` line per repo-backed
     section (`/<key>/`), keep `/instance/*/` if instanced.
   - Copy `toolkit/commands/*.md` → `.claude/commands/`.
   - Create `docs/`, and `templates/instance/` (with a starter README) if an
     instanced section wants a local scaffold.
3. **Initialize**: `git init`, initial commit of the orchestration files only.
4. **Offer** (don't assume): `gh repo create <org>/<name>` + push for the
   workspace repo itself.
5. **Finish**: suggest running `/sync` (clones any already-existing repos) and
   filling in AGENTS.md's domain rules.

## Update mode

1. Read `VERSION` in the toolkit and compare each `toolkit/commands/*.md`
   against the workspace's `.claude/commands/`:
   - Missing in workspace → new command, will be added.
   - Identical → up to date, no action.
   - Different → show the user a per-file diff (`diff -u workspace toolkit`).
2. For differing files, distinguish direction honestly: the workspace copy may
   contain **local improvements that should be upstreamed** to the toolkit
   instead of being overwritten. Ask per file: overwrite from toolkit, keep
   local, or upstream local → toolkit. Never silently overwrite a locally
   modified file.
3. Copy confirmed updates into `.claude/commands/`; if upstreaming, copy the
   workspace file into the toolkit, bump `VERSION` (patch), and commit the
   toolkit.
4. If the workspace's `workspace.yaml` has a `version:` newer than what the
   toolkit's SPEC.md documents, warn — the toolkit clone is stale; suggest
   pulling it.
5. **Never touch**: `workspace.yaml` content, section directories, tool-owned
   paths, or workspace docs. Update mode only manages `.claude/commands/`.
6. Report: per-file action taken, plus the toolkit VERSION.
