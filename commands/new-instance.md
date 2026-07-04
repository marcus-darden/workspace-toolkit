---
description: Create a new instance repo (from the instanced section's template) and clone it into instance/<slug>/.
---

Automate the new-instance transition: create GitHub repo → update workspace.yaml → clone.

## Arguments

| Invocation | Behavior |
|---|---|
| `/new-instance <slug>` | Use `<slug>` as the instance identifier (e.g. `f26`, `w27`). |
| `/new-instance` | Prompt: "New instance slug? (e.g. f26, w27)" |

## Step 0 — Read state

Parse `workspace.yaml`. Find the section with `instanced: true` (there is normally exactly one; if several, ask which). Capture:
- `key` — the section key (the local parent directory, conventionally `instance`)
- `org` — `section.org ?? top-level org`
- `repo_template` — the section's `repo:` field (e.g. `eecs291-{slug}`)
- `scaffold` — the section's `scaffold:` path (workspace-relative), if any
- `instances` — the existing `instances:` list

New repo name = `repo_template` with `{slug}` substituted.

## Step 1 — Guard: no duplicate

If `<slug>` already appears in `instances`:
```
✗ <slug> is already an instance (<key>/<slug>) — nothing to do.
```
Stop.

## Step 2 — Create the GitHub repo

If a `scaffold:` is set, check whether a same-named GitHub template repo exists and is a template:
```bash
gh repo view <org>/<scaffold-basename> --json isTemplate --jq '.isTemplate'
```

**If true** — use GitHub's template API:
```bash
gh repo create <org>/<new-repo> --template <org>/<scaffold-basename> --private --confirm
```

**Otherwise** — create an empty repo and push the local scaffold:
```bash
gh repo create <org>/<new-repo> --private --confirm
```
- If the scaffold directory is a git repo: push it via a temporary remote —
  `git -C <scaffold> remote add _new-instance git@github.com:<org>/<new-repo>.git`,
  `git -C <scaffold> push _new-instance HEAD:main`, then remove the remote.
- If the scaffold is **not** a git repo: copy it to a scratch directory, `git init` +
  one commit there, push that to the new repo, delete the scratch copy. Never
  `git init` inside the scaffold itself.
- If there is no `scaffold:` at all: leave the new repo empty.

If `gh repo create` fails (e.g. repo already exists), stop and report the error — do not proceed to workspace.yaml edits.

Report: `✓ Created github.com/<org>/<new-repo>`

## Step 3 — Update workspace.yaml

Append to the section's `instances:` list:
```yaml
      - slug: <slug>
        description: <derive from the section's description template if it has one>
```

Then, if exactly one other instance has no `status:` (the previously active one), offer — do not assume — to mark it `status: archived`. Archiving is only this status flip; **never move or delete its local directory**.

Report: `✓ Updated workspace.yaml — added <key>/<slug>`

## Step 4 — Clone

```bash
git clone git@github.com:<org>/<new-repo>.git <key>/<slug>/
```

Report: `✓ Cloned into <key>/<slug>/`

## Step 5 — Summary

```
New instance initialized: <key>/<slug> (<org>/<new-repo>)

  ✓ Created    github.com/<org>/<new-repo>
  ✓ Updated    workspace.yaml
  ✓ Cloned     <key>/<slug>/
```

Then print next steps: if the instanced section has a `post_create:` field, print it verbatim; otherwise point at the instance-lifecycle notes in AGENTS.md. Do not invent domain-specific advice.

## Do not

- Proceed past Step 2 if the GitHub repo creation fails.
- Modify any file inside an instance or the scaffold — this command only sets up workspace structure.
- Move, delete, or rename existing instance directories.
- Hardcode repo-name prefixes, scaffold paths, or org names — everything comes from workspace.yaml.
