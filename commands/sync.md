---
description: Clone missing subrepos and refresh existing ones, per workspace.yaml.
---

Read `workspace.yaml` at the workspace root.

## Arguments

| Invocation | Behavior |
|---|---|
| `/sync` | Sync all sections that are not `status: archived` and not `optional: true`. |
| `/sync <section>` | Sync that one named section regardless of `status` or `optional`. For instanced sections, `<section>/<slug>` targets one instance. |
| `/sync --dry-run` | Print what would be cloned or fetched — do nothing. |
| `/sync <section> --dry-run` | Same, scoped to one section. |

## Schema (workspace.yaml)

- `org:` (top-level) — default GitHub org for all repos.
- `sections:` — dict; **the section key is the local directory name** relative to the workspace root.
- `tools:` — tool registrations; not sync targets (tool dirs are part of the workspace repo itself).

Each section is one of:

| Type | Indicator | Local path | GitHub repo |
|---|---|---|---|
| Single repo | *(default)* | `<key>/` | `name:` if set, else `<key>` |
| Folder | `folder: true` | `<key>/<entry.name>/` | `entry.name` |
| Local | `local: true` | `<key>/` | *(none — never cloned or fetched)* |
| Instanced | `instanced: true` | `<key>/<slug>/` | `repo:` template with `{slug}` substituted |

Per-section, per-entry, or per-instance fields:

| Field | Meaning |
|---|---|
| `org:` | Override the GitHub org. Resolution: `entry.org → section.org → top-level org`. |
| `status: archived` | Retired. Skipped by plain `/sync`. |
| `optional: true` | Active but not universally needed. Skipped by plain `/sync`. |

All skip-by-default flags are overridden when the section (or instance) is explicitly named.

## Steps

1. Parse `workspace.yaml`; capture top-level `org:` as the default.
2. Determine scope:
   - No argument → every section, skipping entries/instances with `status: archived` or `optional: true`.
   - `<section>` argument → only that section, including all its entries/instances regardless of flags.
3. Build the **(local-path, org, github-repo)** work list:
   - **Single-repo section**: `(<key>/, section.org ?? top-org, name ?? key)`.
   - **Folder section**: one triple per `repos[]` entry — `(<key>/<entry.name>/, entry.org ?? section.org ?? top-org, entry.name)`.
   - **Local section**: no repo; report `[local]` if the directory exists, `[missing]` if not.
   - **Instanced section**: one triple per `instances[]` entry — `(<key>/<slug>/, section.org ?? top-org, repo-template with {slug})`.
4. For each work item — *skip all writes in `--dry-run` mode*:

   **a. Directory absent — clone it:**
   ```
   git clone git@github.com:<org>/<github-repo>.git <local-path>
   ```
   Report `[cloned]`.

   **b. Directory present, `.git` exists — fetch and report:**
   ```
   git -C <local-path> fetch --quiet
   git -C <local-path> status --short --branch
   ```
   Report: branch, clean/dirty, ahead/behind. **Do not auto-pull.**

   **c. Directory present, no `.git` — report `[no-git]` and skip.**

5. Collect **attention** repos (dirty, ahead of upstream, detached HEAD, merge conflicts).
   List them separately at the end and let the user decide.

## Output format

One aligned line per work item, then a summary:

```
[cloned]   course/                          eecs291staff/course
[ok]       website/                         main  clean  up-to-date
[ok]       projects/p1-wnba-player-impact/  main  clean  behind 2
[ok]       projects/p2-bbbq-joint/          main  dirty  up-to-date  ⚠
[local]    lecture-slides/                  (local section — not a GitHub repo)
[skipped]  prairie-learn/                   (optional — run /sync prairie-learn to load)
[skipped]  instance/w26/                    (archived — run /sync instance/w26 to load)

⚠ Needs attention:
  projects/p2-bbbq-joint/  dirty working tree — commit or stash before pulling

3 ok, 1 cloned, 1 local, 2 skipped, 1 need-attention
```

## Do not

- Auto-pull when the working tree is dirty or the branch is ahead.
- Write to any subrepo's files — sync is read/clone only.
- Modify `workspace.yaml` (new instances are created with `/new-instance`, archiving is a hand-edit).
- Touch anything under a tool's `dir` or `owned` paths (see `tools:` in workspace.yaml).
