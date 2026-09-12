"""Shared helpers for bin/sync and bin/status.

Parses workspace.yaml (schema: docs/SPEC.md) and yields the repo work
list. Keeping the parser here means sync and status cannot disagree
about what the manifest declares. Maintained in
marcus-darden/workspace-toolkit; workspaces carry copies — keep this
file generic, with nothing specific to any one workspace.
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def load_manifest():
    try:
        import yaml
    except ImportError:
        die("PyYAML is required: pip3 install pyyaml")
    manifest_path = ROOT / "workspace.yaml"
    if not manifest_path.is_file():
        die(f"no workspace.yaml at {ROOT}")
    manifest = yaml.safe_load(manifest_path.read_text())
    if not isinstance(manifest, dict) or "sections" not in manifest:
        die("workspace.yaml has no sections: block")
    return manifest


class Item:
    """One unit of work: a repo to clone/inspect, or a local directory."""

    def __init__(self, section, path, org, repo, kind="repo", skip_reason=None):
        self.section = section      # section key; "<key>/<slug>" for instances
        self.path = path            # local path relative to the workspace root
        self.org = org
        self.repo = repo            # GitHub repo name; None for local sections
        self.kind = kind            # "repo" | "local"
        self.skip_reason = skip_reason  # None | "optional" | "archived"

    @property
    def clone_url(self):
        return f"git@github.com:{self.org}/{self.repo}.git"


def _skip_reason(node):
    if node.get("status") == "archived":
        return "archived"
    if node.get("optional"):
        return "optional"
    return None


def items(manifest):
    """Yield an Item per repo/local directory declared in the manifest."""
    top_org = manifest.get("org")
    for key, sec in (manifest.get("sections") or {}).items():
        sec = sec or {}
        sec_skip = _skip_reason(sec)
        sec_org = sec.get("org") or top_org
        if sec.get("local"):
            yield Item(key, f"{key}/", None, None, kind="local", skip_reason=sec_skip)
        elif sec.get("folder"):
            for entry in sec.get("repos") or []:
                yield Item(
                    key,
                    f"{key}/{entry['name']}/",
                    entry.get("org") or sec_org,
                    entry["name"],
                    skip_reason=_skip_reason(entry) or sec_skip,
                )
        elif sec.get("instanced"):
            template = sec.get("repo", "{slug}")
            for inst in sec.get("instances") or []:
                if isinstance(inst, str):
                    inst = {"slug": inst}
                slug = inst["slug"]
                yield Item(
                    f"{key}/{slug}",
                    f"{key}/{slug}/",
                    inst.get("org") or sec_org,
                    template.format(slug=slug),
                    skip_reason=_skip_reason(inst) or sec_skip,
                )
        else:
            yield Item(key, f"{key}/", sec_org, sec.get("name") or key,
                       skip_reason=sec_skip)


def git(path, *args):
    return subprocess.run(["git", "-C", str(path), *args],
                          capture_output=True, text=True)


def repo_state(path):
    """Summarize a clone: branch, upstream delta, dirty counts, flags.

    Read-only and network-free.
    """
    out = git(path, "status", "--porcelain=v1", "--branch").stdout.splitlines()
    if not out:
        return None
    header, body = out[0], out[1:]
    branch = header[3:].split("...")[0].split(" ")[0]
    if "..." in header:
        if "[" in header:
            delta = header[header.index("[") + 1:header.rindex("]")]
        else:
            delta = "up-to-date"
    else:
        delta = "no upstream"
    modified = sum(1 for l in body if l and not l.startswith("??"))
    untracked = sum(1 for l in body if l.startswith("??"))

    default = None
    ref = git(path, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if ref.returncode == 0:
        default = ref.stdout.strip().split("/", 1)[-1]

    flags = []
    if modified or untracked:
        flags.append("uncommitted work")
    if "ahead" in delta:
        flags.append("ahead of upstream")
    if default and branch != default:
        flags.append(f"on {branch}, default is {default}")
    if branch.startswith("HEAD"):
        flags.append("detached HEAD")
    return {"branch": branch, "delta": delta, "modified": modified,
            "untracked": untracked, "flags": flags}


def print_table(rows):
    """Print rows (lists of strings) with aligned columns."""
    if not rows:
        return
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    for r in rows:
        print("  ".join(cell.ljust(w) for cell, w in zip(r, widths)).rstrip())
