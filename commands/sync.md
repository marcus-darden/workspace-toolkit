---
description: Clone missing subrepos and refresh existing ones, per workspace.yaml.
---

Run `bin/sync $ARGUMENTS` from the workspace root and relay its output to the
user, including the needs-attention list. Do not reimplement its logic.

Accepted arguments: none (all standard sections), a section name (syncs it
even if `optional`/`archived`; `section/slug` for instances), and `--dry-run`.
Schema and semantics: `docs/SPEC.md`.

If the script fails (missing python3 or PyYAML, no ssh access), report the
error and the fix it suggests — do not fall back to cloning by hand.
