---
description: Compact git status across the workspace repo and all subrepos.
---

Read `workspace.yaml`. Build the repo list: the workspace root repo itself first, then every *present* repo directory from `sections:` (single-repo sections at `<key>/`, folder entries at `<key>/<entry.name>/`, instances at `<key>/<slug>/`; skip `local: true` sections and directories that don't exist — `/status` never clones).

For each repo, run `git status --porcelain=v1 --branch` and emit one line:

```
<dir>  <branch>  <ahead/behind>  <N modified, N untracked>
```

Flag (do not fix):
- uncommitted work
- non-default branch (default = whatever the remote HEAD points to)
- commits ahead of upstream

Prefer a single shell loop over running git status as separate Bash calls per repo. Read-only — no fetch, no pull, no writes.
