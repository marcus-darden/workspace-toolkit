# {{NAME}}

Workspace for {{TITLE}}.
Holds orchestration only — content lives in the subrepos declared in `workspace.yaml`.

## Layout

| Path | Purpose |
|------|---------|
| `workspace.yaml` | Workspace manifest — sections, repos to clone, instances, tools. |
| `docs/` | Workspace-level planning and reference docs. |

## Setup

```bash
git clone {{CLONE_URL}}
cd {{NAME}}
# /sync clones every repo-backed section as a child directory
```
