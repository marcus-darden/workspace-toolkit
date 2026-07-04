---
description: Commit and push pending changes in the workspace repo and every subrepo. Pairs with /sync (pull-side).
---

Read `workspace.yaml`. Operate on the workspace root repo itself **and** every existing subrepo from `sections:` (single-repo sections, folder entries, and instances; skip `local: true` sections and directories that don't exist). The root repo is treated as just another entry — same flow, same rules.

## Tool-owned paths

From `tools:` in workspace.yaml, build the exclusion list: each tool's `dir` (workspace-relative) and each glob in its `owned:` list (matched in every repo). `/push` never stages, commits, or edits anything under these paths — tools commit their own state.

## Per repo

1. Run `git status --porcelain=v1 --branch` to detect:
   - uncommitted changes (staged, modified, or untracked)
   - commits ahead of upstream
   - missing upstream (no tracking branch)

2. Skip the repo silently if it is clean and not ahead.

For repos that need work, just **do it**. No confirmation prompts.

### Commit message

- If the user passed an argument (`$ARGUMENTS`), use it verbatim for every repo.
- Otherwise, generate a per-repo message from `git diff` + `git status`. One short sentence focused on the *why*, matching that repo's recent `git log` style. Do not include a Claude co-author trailer.

### Execute

For each repo with pending work:

1. Stage files explicitly by path (no `git add -A`/`git add .`) — list the paths from the status output, minus tool-owned paths.
2. Skip any path that looks like a secret (`.env`, `credentials.*`, `*.pem`, `id_rsa*`) and flag it in the report. Do **not** ask — just skip it.
3. `git commit -m "<message>"` (no `--no-verify`, no `--amend`).
4. Push with rebase-on-conflict:
   - `git push` first.
   - If push is rejected as non-fast-forward, run `git pull --rebase` then `git push` again.
   - If the rebase has conflicts, abort it (`git rebase --abort`) and mark the repo as failed. Do not try to resolve.
   - If upstream is missing, run `git push -u origin <branch>` (no confirmation needed).
5. If a hook fails: report the failure, do **not** retry with `--no-verify`, do **not** amend.

### Report

One summary line per repo (root repo first, then subrepos):

```
<dir>  <committed N files>  <pushed N commits>
```

Then a final tally: `N committed, N pushed, N rebased, N skipped, N failed`.

### Never

- Edit or stage tool-owned paths (any `tools.*.dir` or `tools.*.owned` match) — they're tool-written and committed by the tool, not by `/push`.
- Use `git add -A` / `git add .` / `--no-verify` / `--amend` / force-push.
- Resolve rebase conflicts automatically — abort and surface them.
