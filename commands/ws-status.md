---
description: Compact git status across the workspace repo and all subrepos.
---

Run `bin/status` from the workspace root and relay its output to the user,
including the flags list. Do not reimplement its logic; it is read-only and
network-free (semantics: `docs/SPEC.md`).

If the script fails (missing python3 or PyYAML), report the error and the
fix it suggests.
