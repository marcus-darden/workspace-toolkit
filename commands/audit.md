---
description: Read-only audit of the workspace. Find stale repos, drift, and inconsistencies.
---

Read `workspace.yaml`. Audit the workspace. Make no changes. Report findings as short markdown sections.

Check:

1. **Pending work** — any repo (root or subrepo) with uncommitted changes or unpushed commits.
2. **Staleness** — last commit date per subrepo. Flag repos untouched longer than `audit.stale_days` from workspace.yaml (default 60 days). Skip `status: archived` entries and instances.
3. **Branch hygiene** — repos not on their default branch (default = remote HEAD).
4. **Drift** — directories present at the workspace root that aren't declared in `workspace.yaml` (as a section, tool `dir`, or workspace-repo content), and non-optional, non-archived declared sections that aren't present on disk.
5. **Instance consistency** — for instanced sections: active instances (no `status:`) missing locally → flag (run `/sync`). Archived instances still present locally → note informationally only; keeping them is fine (the remote is canonical) and nothing should suggest deleting them.
6. **Workspace checklist** — if `docs/audit-checklist.md` exists, run the checks it describes and report them in their own section. This is where domain-specific rules live (content layout, cross-repo consistency, publication checks); the audit mechanism stays generic.

Cap output at ~40 lines unless a finding genuinely needs more detail. Lead with the most actionable items.
