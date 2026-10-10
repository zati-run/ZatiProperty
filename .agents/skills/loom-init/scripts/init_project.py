#!/usr/bin/env python3
"""Offline, conservative Loom project scaffolder. No app/backend mutations."""
import argparse
import json
import re
import sys
from pathlib import Path

START = "<!-- loom-init:construction-contract:start -->"
END = "<!-- loom-init:construction-contract:end -->"


def safe_path(root, relative):
    if not relative or any(ord(c) < 32 for c in relative):
        raise ValueError("managed paths must not contain control characters")
    p = Path(relative)
    if p.is_absolute() or not p.parts or ".." in p.parts:
        raise ValueError("managed paths must be relative without traversal")
    current = root
    for part in p.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("symbolic links are not allowed: " + str(current))
        if current.exists() and current != root / p and not current.is_dir():
            raise ValueError("parent is not a directory: " + str(current))
    if current.exists() and not current.is_file():
        raise ValueError("destination is not a regular file: " + str(current))
    if current.exists() and current.stat().st_nlink > 1:
        raise ValueError("hard-linked destination refused: " + str(current))
    return current


def prepare(target, project_name, rfc):
    root = Path(target).absolute()
    for part in (root, *root.parents):
        if part.is_symlink():
            raise ValueError("target and ancestors must not be symbolic links")
    if not root.is_dir():
        raise ValueError("target must be an existing directory")
    name = project_name.strip()
    if not name or len(name) > 100 or any(ord(c) < 32 for c in name) or any(c in name for c in '<>\\/'):
        raise ValueError("project-name must be 1-100 printable characters without path or HTML delimiters")
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "project"
    slug = slug[:48].rstrip("-")
    skill_rel = ".agents/skills/" + slug + "-loom/SKILL.md"
    agents_path = safe_path(root, "AGENTS.md")
    skill_path = safe_path(root, skill_rel)
    rfc_relative = Path(rfc)
    if rfc_relative.suffix.lower() not in (".md", ".markdown") or any(part.startswith(".") for part in rfc_relative.parts):
        raise ValueError("RFC must be a Markdown document outside hidden/control directories")
    rfc_path = safe_path(root, rfc)
    backup = safe_path(root, "AGENTS.md.loom-init.bak")
    paths = [agents_path, skill_path, rfc_path, backup]
    for i, path in enumerate(paths):
        for other in paths[i + 1:]:
            if path == other or path in other.parents or other in path.parents:
                raise ValueError("managed destinations overlap")
    contract = (Path(__file__).resolve().parents[1] / "references/generation-contract.md").read_text()
    agents = ("# " + name + " agent instructions\n\n"
              "Application construction MUST use Loom MCP to generate this application in NocoBase.\n\n"
              "Read " + rfc + " and " + skill_rel + " before implementation. "
              "Follow the Loom construction contract and preserve product requirements. "
              "Do not substitute a custom frontend/backend or direct NocoBase API/CLI writes. "
              "Record missing MCP capabilities and obtain an explicit scope decision.\n\n"
              "Preparation does not authorize live mutations. Discover actual tools and schemas, "
              "verify operator-approved authority and inspect existing state before generation. "
              "Keep secrets out of project files. Report source checks, live checks and acceptance separately.\n")
    skill = ("---\nname: " + slug + "-loom\ndescription: Generate and verify the "
             + name + " application in NocoBase through Loom MCP.\n---\n\n"
             "# Generate " + name + "\n\nRead the authoritative RFC at " + rfc + " and AGENTS.md first.\n\n"
             + contract + "\n## Project tailoring required\n\n"
             "Derive domain entities, workflows, roles, tenant boundaries and acceptance scenarios "
             "from the RFC. Record a dependency-ordered plan with stable task IDs, owners, stages "
             "and explicit acceptance criteria before generation. Preserve existing authored requirements.\n")
    lines = skill.splitlines(keepends=True)
    lines[2] = "description: " + json.dumps(lines[2][len("description: "):].rstrip("\n"), ensure_ascii=False) + "\n"
    skill = "".join(lines)
    original = rfc_path.read_bytes() if rfc_path.exists() else b""
    text = original.decode("utf-8")
    block = START + "\n" + contract.rstrip() + "\n" + END
    if START in text or END in text:
        if text.count(START) != 1 or text.count(END) != 1 or text.index(START) > text.index(END):
            raise ValueError("malformed or duplicate RFC managed markers")
        begin, finish = text.index(START), text.index(END) + len(END)
        text = text[:begin] + block + text[finish:]
    else:
        text = block + "\n\n" + (text if original else "# " + name + " application RFC\n\nProduct requirements must be supplied and reconciled before generation.\n")
    return [(agents_path, agents.encode()), (skill_path, skill.encode()), (rfc_path, text.encode())], backup


def initialize(target, project_name, rfc, write=False, replace_agents=False):
    desired, backup = prepare(target, project_name, rfc)
    pending = []
    for index, (path, data) in enumerate(desired):
        if path.exists():
            old = path.read_bytes()
            if old == data:
                continue
            if index == 0:
                if not replace_agents:
                    raise ValueError("AGENTS.md differs; review it and use --replace-agents explicitly")
                if backup.exists():
                    raise ValueError("AGENTS backup already exists; refusing replacement")
                pending.append((backup, old, False))
            elif index == 1:
                raise ValueError("project skill already exists with different content")
        pending.append((path, data, path.exists()))
    # All collisions, RFC markers and contents are checked before any writes.
    for path, data, existed in pending:
        print(("WRITE " if write else "DRY RUN ") + str(path))
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("wb" if existed else "xb") as output:
                output.write(data)
    if not pending:
        print("No changes.")
    print("Required next step: reconcile the entire RFC and retained agent instructions semantically.")
    return len(pending)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--rfc", default="docs/rfc/rfc-001.md")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--replace-agents", action="store_true")
    args = parser.parse_args()
    try:
        initialize(args.target, args.project_name, args.rfc, args.write, args.replace_agents)
    except (ValueError, OSError, UnicodeError) as exc:
        parser.exit(2, "loom-init: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
