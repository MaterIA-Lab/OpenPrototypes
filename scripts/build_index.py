#!/usr/bin/env python3
"""Build projects.json and the README project table from projects/registry.yaml.

Usage:
    python scripts/build_index.py           # write files
    python scripts/build_index.py --check   # exit 1 if files are out of date

Requires PyYAML (pip install pyyaml).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "projects" / "registry.yaml"
JSON_OUT = ROOT / "projects.json"
README = ROOT / "README.md"

STATUSES = ("proposed", "approved", "active", "paused", "done", "failed", "abandoned")
REQUIRED = ("id", "title", "status", "goal")
OPTIONAL = ("repo", "path", "started", "tags")
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

START = "<!-- PROJECTS:START -->"
END = "<!-- PROJECTS:END -->"


def load_projects() -> list[dict]:
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    projects = data.get("projects") or []
    errors: list[str] = []
    seen: set[str] = set()

    for i, p in enumerate(projects):
        where = f"projects[{i}]"
        if not isinstance(p, dict):
            errors.append(f"{where}: must be a mapping")
            continue
        for key in REQUIRED:
            if not p.get(key):
                errors.append(f"{where}: missing '{key}'")
        unknown = set(p) - set(REQUIRED) - set(OPTIONAL)
        if unknown:
            errors.append(f"{where}: unknown keys {sorted(unknown)}")
        pid = str(p.get("id", ""))
        if pid and not ID_RE.match(pid):
            errors.append(f"{where}: id '{pid}' must be kebab-case")
        if pid in seen:
            errors.append(f"{where}: duplicate id '{pid}'")
        seen.add(pid)
        if p.get("status") and p["status"] not in STATUSES:
            errors.append(f"{where}: status '{p['status']}' not in {STATUSES}")
        if "started" in p:
            p["started"] = str(p["started"])

    if errors:
        sys.exit("registry.yaml is invalid:\n  " + "\n  ".join(errors))
    return projects


def render_json(projects: list[dict]) -> str:
    out = []
    for p in projects:
        entry = {k: p[k] for k in REQUIRED + OPTIONAL if k in p}
        if "repo" in p:
            entry["url"] = f"https://github.com/{p['repo']}"
        out.append(entry)
    return json.dumps({"projects": out}, indent=2, ensure_ascii=False) + "\n"


def cell(text: str) -> str:
    return " ".join(str(text).split()).replace("|", "\\|")


def render_table(projects: list[dict]) -> str:
    if not projects:
        return "_No projects yet._"
    rows = ["| Project | Status | Goal |", "|---|---|---|"]
    for p in projects:
        name = f"[{p['id']}](https://github.com/{p['repo']})" if p.get("repo") else p["id"]
        rows.append(f"| {name} | {p['status']} | {cell(p['goal'])} |")
    return "\n".join(rows)


def render_readme(projects: list[dict]) -> str:
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        sys.exit(f"README.md is missing the {START} / {END} markers")
    block = f"{START}\n{render_table(projects)}\n{END}"
    return pattern.sub(lambda _: block, text, count=1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if outputs are stale")
    args = parser.parse_args()

    projects = load_projects()
    outputs = {JSON_OUT: render_json(projects), README: render_readme(projects)}

    stale = [path for path, content in outputs.items()
             if not path.exists() or path.read_text(encoding="utf-8") != content]

    if args.check:
        if stale:
            sys.exit("Out of date: " + ", ".join(p.name for p in stale)
                     + "\nRun: python scripts/build_index.py")
        print("Index is up to date.")
        return

    for path in stale:
        path.write_text(outputs[path], encoding="utf-8", newline="\n")
        print(f"Updated {path.relative_to(ROOT)}")
    if not stale:
        print("Nothing to update.")


if __name__ == "__main__":
    main()
