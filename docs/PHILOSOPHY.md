# The Workspace Toolkit — Philosophy and Rules

*A discussion document for tools and agents that operate inside workspaces —
written originally for the CourseClaw project. The mechanical schema reference
is [SPEC.md](SPEC.md); this document explains why the system is shaped the way
it is and what rules follow from that shape.*

## What a workspace is

A **workspace** is a git repository that gathers and governs a family of
related repositories. The marker is a `workspace.yaml` file at the root — the
way `Cargo.toml` marks a Rust crate. There is no naming convention ("-hq",
"headquarters") and no special repo type: any directory with a `workspace.yaml`
is a workspace, and everything a tool or agent needs to know about the family
is declared in that one file.

Subrepos are cloned **in place** as child directories, each with its own
`.git`, and gitignored by the workspace repo. The workspace repo itself tracks
only orchestration: the manifest, commands, planning docs, templates, and
tool-owned state. Content never lives in two repos at once.

The pattern grew out of multi-repo college courses — a coordination repo, a
public website, per-project repos, a question bank, and one student-facing repo
per semester — but nothing in it is course-specific. Any long-lived project
that spans many repos and gets periodically re-instantiated fits.

## The three-domain boundary

Everything in a workspace belongs to exactly one of three domains, and most of
the design falls out of refusing to let them blur:

1. **Generic orchestration** — the workspace convention itself: the
   `workspace.yaml` schema, the commands (`/sync`, `/status`, `/push`,
   `/audit`, `/new-instance`), the instance model, the tool boundary. This is
   what the toolkit owns. It must contain no knowledge of any particular
   project.

2. **Domain content** — what the workspace is *about*: course plans, style
   guides, schedules, per-repo rules. This lives in the workspace's own
   `docs/`, `AGENTS.md`, and inside the subrepos. It must never leak into
   commands: a command that knows a repo-name prefix or a canonical directory
   layout is a bug, even if it works.

3. **Tool state** — what an external tool (a dashboard, an ingestion agent, an
   automation) needs to remember: pointers, manifests, policies, memory, audit
   logs. This lives only inside the tool's owned paths.

The first version of this system violated all three boundaries at once: a
`current.yaml` at the workspace root mixed tool state (the active-course
pointer a dashboard ingested) with domain content (instructor names, phase
dates); commands hardcoded layout paths; and archiving a semester required
choreographed file moves. Each violation individually looked convenient. The
rules below exist because the convenience never survived the second project.

## Rules

### 1. Commands are pure interpreters of workspace.yaml

A command may know the *schema* — what a section is, what `instanced: true`
means. It may not know any *value*: no repo prefixes, no scaffold paths, no
tool names, no directory layouts. The test: could this command file be copied
byte-for-byte into an unrelated workspace and behave correctly? If not, the
knowledge it carries belongs in `workspace.yaml` (if structural) or in the
workspace's docs (if domain). This is what makes the toolkit distributable:
commands are updated centrally and copied out, and a workspace's identity
lives entirely in its manifest.

### 2. Tools own directories, and the boundary runs both ways

A tool registers in `workspace.yaml` under `tools:` and owns one root
directory named after itself, plus optional `owned:` globs matched inside
every subrepo (e.g. `**/.courseclaw/`).

- **Humans and generic commands never write tool-owned paths.** `/push` will
  not stage them; agents do not hand-edit them. Tools commit their own state.
- **Tools never write outside their owned paths.** A tool that needs a config
  file, a pointer, a manifest, or a scratch area puts it inside its directory
  — never at the workspace root, never loose inside a subrepo.

A tool may additionally use a marker file (CourseClaw's `.courseclaw-owned`)
to signal that a workspace has opted in to that tool's writes. The marker is
tool-specific and is itself tool-owned.

### 3. There is no "current instance"

Sections that get re-instantiated per iteration (semesters, cohorts, annual
editions) are declared `instanced: true`, and every instance lives at
`instance/<slug>/`. All instances are equal. The workspace deliberately has no
active/current pointer, because "current" is not a property of the repos — it
is a property of whoever is asking. A dashboard's current semester, an
instructor's current focus, and a grader's current backlog can legitimately
differ.

A tool that needs a current notion keeps it in its own owned directory, in its
own format, on its own update schedule. Retiring an instance is a one-line
status flip (`status: archived`) in `workspace.yaml` — no file moves, no
pointer dance, no coordination with tools beyond them reading the manifest.
Archived clones stay on disk; the remote is canonical, and nothing in the
system ever suggests deleting them.

### 4. Directory names are roles, not repo names

Section keys — which are the local directory names — describe the role
(`website/`, `course/`, `prairie-learn/`, `instance/`); the `name:` and `org:`
fields map them to actual GitHub repos. Two consequences: every workspace
looks structurally alike, so docs, agents, and muscle memory transfer between
projects; and GitHub-side renames or org moves touch one manifest line instead
of every path in every doc. Entries inside a `folder: true` section keep their
repo names — they are already namespaced by the section.

### 5. One git per repo; the workspace repo tracks only itself

Commits, branches, and remotes are per subrepo. The workspace repo never
contains subrepo content, and subrepo history never depends on workspace
history. `/push` treats the workspace repo as just another entry — same
staging discipline (explicit paths, never `git add -A`), same secret skipping,
same rebase-abort-on-conflict rules.

### 6. Safety defaults are not negotiable

Across all commands: never auto-pull into a dirty tree, never force-push,
never `--no-verify`, never resolve rebase conflicts silently, never stage
secret-looking paths, and every mutating command has a dry-run or reports
before acting. These came from operating real courses where a bad push lands
in front of hundreds of students.

## Distribution

The toolkit repo is the single source of truth for commands and templates. A
scaffolding skill creates new workspaces from it (interview → manifest →
commands copied in → git init) and updates existing ones (per-file diff,
explicit confirmation, and an *upstream* path: when a workspace improves a
command, the improvement flows back to the toolkit and out to the other
workspaces). Workspaces stay self-contained — a collaborator who clones one
gets working commands with no toolkit dependency — while the toolkit prevents
per-workspace drift from becoming per-workspace divergence.

## What this means for a tool like CourseClaw

- Read `workspace.yaml` to learn the family: sections, instances, orgs. Do not
  assume layout beyond what the manifest declares.
- Keep every byte of your state — including your active-course pointer and any
  ingestion manifests — inside your owned paths (`courseclaw/` at the root,
  `.courseclaw/` inside repos you write to).
- Treat `status: archived` as the retirement signal; do not expect file moves.
- Expect role-named directories, and resolve repos through the manifest's
  `name:`/`org:` mapping rather than by directory name.
