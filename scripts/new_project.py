#!/usr/bin/env python3
"""Create a new OpenPrototypes research project.

What it does:
  1. Creates MaterIA-Lab/op-<id> from the MaterIA-Lab/op-project-template template.
  2. Sets the repo's Actions permissions (needed for agent/* auto-merge) and topics.
  3. Fills the template placeholders (title, id, goal, status, tags) and pushes to main.
  4. Adds the repo as a submodule at projects/op-<id> and registers it in projects/registry.yaml.
  5. Rebuilds the project index (README table and projects.json).

The root repository changes are staged but not committed, so you can review them.

Usage:
  python scripts/new_project.py sort-cpu-tricks \
      --title "Faster practical sorting using CPU tricks" \
      --goal "Beat state-of-the-art sorting in a specific niche..." \
      --tags performance,sorting

  If the id is already in registry.yaml (e.g. a `proposed` project), --title, --goal
  and --tags default to the values there.

Requires: GitHub CLI (gh) logged in with access to the MaterIA-Lab org, git, PyYAML.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "projects" / "registry.yaml"
ORG = "MaterIA-Lab"
TEMPLATE = f"{ORG}/op-project-template"
STATUSES = ("proposed", "approved", "active", "paused", "done", "failed", "abandoned")
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DRY_RUN = False


# --- helpers -----------------------------------------------------------------

def find_gh() -> str:
    gh = shutil.which("gh")
    if gh:
        return gh
    default = Path(r"C:\Program Files\GitHub CLI\gh.exe")
    if default.exists():
        return str(default)
    sys.exit("GitHub CLI (gh) not found. Install it and run `gh auth login`.")


def run(cmd: list[str], cwd: Path | None = None, capture: bool = False, mutates: bool = True) -> str:
    shown = " ".join(c if " " not in c else f'"{c}"' for c in cmd)
    if DRY_RUN and mutates:
        print(f"[dry-run] {shown}")
        return ""
    print(f"$ {shown}")
    res = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if res.returncode != 0:
        sys.exit(f"Command failed ({res.returncode}): {shown}\n{res.stderr.strip()}")
    return res.stdout.strip() if capture else ""


def yaml_str(value: str) -> str:
    """Quote a scalar safely for YAML."""
    return yaml.safe_dump(value, default_flow_style=True, allow_unicode=True, width=10**6).strip().removesuffix("...").strip()


def yaml_list(values: list[str]) -> str:
    return "[" + ", ".join(yaml_str(v) for v in values) + "]"


# --- template filling --------------------------------------------------------

def fill_placeholders(repo_dir: Path, pid: str, title: str, goal: str, status: str, tags: list[str]) -> None:
    """Replace the template placeholders in a freshly created project repo."""
    readme = repo_dir / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = re.sub(r"\A<!--.*?-->\s*", "", text, flags=re.S)  # drop the new-project checklist
    text = text.replace("<Project title>", title)
    text = text.replace("<One sentence: what this project is trying to find out.>", goal)
    text = text.replace("**Status:** `proposed`", f"**Status:** `{status}`")
    readme.write_text(text, encoding="utf-8", newline="\n")

    meta = repo_dir / "project.yaml"
    text = meta.read_text(encoding="utf-8")
    text = text.replace("id: <project-id>", f"id: {pid}")
    text = text.replace("title: <Project title>", f"title: {yaml_str(title)}")
    text = text.replace("goal: <One-sentence research goal.>", f"goal: {yaml_str(goal)}")
    text = re.sub(r"^status: proposed", f"status: {status}", text, flags=re.M)
    text = re.sub(r"^tags: \[\]", f"tags: {yaml_list(tags)}", text, flags=re.M)
    meta.write_text(text, encoding="utf-8", newline="\n")

    data = yaml.safe_load(text)  # sanity check: still valid YAML with the right values
    assert data["id"] == pid and data["title"] == title and data["goal"] == goal, "project.yaml fill failed"


# --- registry ----------------------------------------------------------------

def load_registry() -> list[dict]:
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    return data.get("projects") or []


def register(pid: str, title: str, goal: str, status: str, tags: list[str], repo: str, path: str) -> None:
    """Add or update the registry entry, editing text so comments are preserved."""
    text = REGISTRY.read_text(encoding="utf-8")
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if re.match(rf"^\s*-\s+id:\s*{re.escape(pid)}\s*$", l)), None)

    if start is None:
        block = [
            f"  - id: {pid}",
            f"    title: {yaml_str(title)}",
            f"    status: {status}",
            f"    goal: {yaml_str(goal)}",
            f"    repo: {repo}",
            f"    path: {path}",
        ]
        if tags:
            block.append(f"    tags: {yaml_list(tags)}")
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend(block)
    else:
        end = next((i for i in range(start + 1, len(lines)) if re.match(r"^\s*-\s+id:", lines[i])), len(lines))
        entry = lines[start:end]
        if any(re.match(r"^\s+repo:", l) for l in entry):
            print(f"registry.yaml: '{pid}' already has a repo; leaving it unchanged.")
            return
        insert_at = end
        while insert_at > start + 1 and not lines[insert_at - 1].strip():
            insert_at -= 1
        lines[insert_at:insert_at] = [f"    repo: {repo}", f"    path: {path}"]

    new_text = "\n".join(lines) + "\n"
    yaml.safe_load(new_text)  # must stay valid
    if DRY_RUN:
        print(f"[dry-run] update projects/registry.yaml")
        return
    REGISTRY.write_text(new_text, encoding="utf-8", newline="\n")
    print(f"Updated projects/registry.yaml")


# --- main --------------------------------------------------------------------

def main() -> None:
    global DRY_RUN
    parser = argparse.ArgumentParser(description="Create a new OpenPrototypes research project.")
    parser.add_argument("id", help="kebab-case project id; the repo will be op-<id>")
    parser.add_argument("--title")
    parser.add_argument("--goal", help="one-sentence research goal")
    parser.add_argument("--tags", help="comma-separated tags")
    parser.add_argument("--status", choices=STATUSES)
    parser.add_argument("--private", action="store_true", help="create the repo as private (default: public)")
    parser.add_argument("--dry-run", action="store_true", help="print what would happen without changing anything")
    args = parser.parse_args()
    DRY_RUN = args.dry_run

    pid = args.id
    if not ID_RE.match(pid):
        sys.exit(f"Invalid id '{pid}': use kebab-case, e.g. sort-cpu-tricks")

    existing = next((p for p in load_registry() if p.get("id") == pid), {})
    title = args.title or existing.get("title")
    goal = args.goal or existing.get("goal")
    status = args.status or existing.get("status") or "proposed"
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else list(existing.get("tags") or [])
    if not title or not goal:
        sys.exit("--title and --goal are required for a project that is not in registry.yaml yet.")
    goal = " ".join(goal.split())

    repo = f"{ORG}/op-{pid}"
    path = f"projects/op-{pid}"
    gh = find_gh()

    if (ROOT / path).exists():
        sys.exit(f"{path} already exists.")
    exists = subprocess.run([gh, "repo", "view", repo], capture_output=True, text=True).returncode == 0
    if exists:
        sys.exit(f"{repo} already exists on GitHub. Nothing created.")

    print(f"Creating {repo}  ({status}) - {title}")

    # 1. Repository from template
    run([gh, "repo", "create", repo, "--public" if not args.private else "--private",
         "--template", TEMPLATE, "--description", goal[:350]])

    # Template generation is asynchronous; wait until main has a commit.
    if not DRY_RUN:
        for _ in range(30):
            ok = subprocess.run([gh, "api", f"repos/{repo}/commits/main", "--silent"], capture_output=True).returncode == 0
            if ok:
                break
            time.sleep(2)
        else:
            sys.exit(f"{repo} was created but its content did not appear in time. Re-run the remaining steps by hand.")

    # 2. Settings
    run([gh, "api", "-X", "PUT", f"repos/{repo}/actions/permissions/workflow",
         "-f", "default_workflow_permissions=write", "-F", "can_approve_pull_request_reviews=true", "--silent"])
    topic_args = [a for t in ["openprototypes", *tags] for a in ("--add-topic", re.sub(r"[^a-z0-9-]", "-", t.lower())[:50])]
    run([gh, "repo", "edit", repo, "--delete-branch-on-merge=false", *topic_args])

    # 3. Fill placeholders and push
    if DRY_RUN:
        print("[dry-run] clone, fill README.md and project.yaml, commit and push to main")
    else:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / f"op-{pid}"
            run([gh, "repo", "clone", repo, str(work)])
            fill_placeholders(work, pid, title, goal, status, tags)
            run(["git", "add", "-A"], cwd=work)
            run(["git", "commit", "-q", "-m", f"Set up project {pid} from template"], cwd=work)
            run(["git", "push", "-q", "origin", "main"], cwd=work)

    # 4. Submodule + registry
    run(["git", "submodule", "add", f"https://github.com/{repo}.git", path], cwd=ROOT)
    register(pid, title, goal, status, tags, repo, path)

    # 5. Index
    run([sys.executable, str(ROOT / "scripts" / "build_index.py")], cwd=ROOT)
    run(["git", "add", ".gitmodules", path, "projects/registry.yaml", "projects.json", "README.md"], cwd=ROOT)

    if DRY_RUN:
        print("\nDry run complete. Nothing was changed.")
        return
    print(f"""
Done: https://github.com/{repo}
Root repository changes are staged. Review them, then commit:
  git commit -m "Add project {pid}"
Next: write GOAL.md and the project-specific rules in AGENTS.md of op-{pid}.""")


if __name__ == "__main__":
    os.environ.setdefault("GH_PROMPT_DISABLED", "1")
    main()
