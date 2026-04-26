#!/usr/bin/env python3
"""Migrate harbor_tasks Dockerfiles from full-clone to shallow init+fetch.

Pattern in (current full-clone, two common variants):

  Variant A (chained, no cd):
    RUN git clone --filter=blob:none https://github.com/X/Y.git <dir> \\
     && git checkout <sha>

  Variant B (chained with cd + extras):
    RUN git clone --filter=blob:none https://github.com/X/Y.git /workspace/<dir> && \\
        cd /workspace/<dir> && \\
        git checkout <sha> && \\
        git config user.email "..." && \\
        ...

Pattern out (uniform shallow target):

    RUN git init <abs_dir> && \\
        cd <abs_dir> && \\
        git remote add origin <https-url>.git && \\
        git fetch --depth=1 origin <sha> && \\
        git checkout FETCH_HEAD <preserved_extras>

Skips:
  - Dockerfiles already using `git init` (already shallow)
  - Dockerfiles where parsing fails (logged, not modified)

Usage:
    .venv/bin/python scripts/dockerfile_shallow_migrate.py            # dry-run
    .venv/bin/python scripts/dockerfile_shallow_migrate.py --apply    # write
"""
from __future__ import annotations

import argparse
import re
import sys
import textwrap
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "harbor_tasks"

# Match the entire `RUN git clone ... && git checkout <sha>` block.
# Captures: 1=repo URL (without .git), 2=target dir, 3=commit sha, 4=extras chain.
#
# BODY matches across line continuations (`\\\n`) and arbitrary intervening
# commands like `cd <dir>`, non-greedily.
BODY = r"(?:[^\n]|\\\n)*?"
CLONE_RE = re.compile(
    r"""RUN\s+git\s+clone\b""" + BODY + r"""
        https://github\.com/([\w.-]+/[\w.-]+?)\.git\s+(\S+)
        """ + BODY + r"""
        git\s+checkout\s+(\$\{?BASE_COMMIT\}?|[0-9a-f]{7,40})
        ((?:\s*&&""" + BODY + r""")*)
    """,
    re.VERBOSE,
)
# Match an `ARG BASE_COMMIT=<sha>` line so we can resolve ${BASE_COMMIT} refs.
ARG_RE = re.compile(r"ARG\s+BASE_COMMIT\s*=\s*([0-9a-f]{7,40})")


def find_block(text: str) -> Optional[re.Match]:
    """Find the first full-clone RUN block."""
    return CLONE_RE.search(text)


def build_shallow(repo: str, target: str, sha: str, extras: str) -> str:
    """Construct the shallow replacement RUN block."""
    abs_target = target if target.startswith("/") else f"/workspace/{target}"
    # Strip the trailing parts from `extras` that we already account for
    # (the cd and git checkout we re-emit fresh).
    extras_lines: list[str] = []
    for chunk in re.split(r"\\?\s*\n?\s*&&\s*", extras):
        chunk = chunk.strip().rstrip("\\").strip()
        if not chunk:
            continue
        # Skip cd / checkout — we re-emit ours
        if chunk.startswith("cd "):
            continue
        if chunk.startswith("git checkout "):
            continue
        extras_lines.append(chunk)

    block = (
        f"RUN git init {abs_target} && \\\n"
        f"    cd {abs_target} && \\\n"
        f"    git remote add origin https://github.com/{repo}.git && \\\n"
        f"    git fetch --depth=1 origin {sha} && \\\n"
        f"    git checkout FETCH_HEAD"
    )
    for e in extras_lines:
        block += f" && \\\n    {e}"
    return block


def migrate_one(path: Path) -> tuple[bool, str, Optional[str]]:
    """Returns (changed, status_msg, new_text_or_None)."""
    text = path.read_text()
    # Skip if already migrated. (Some shallow Dockerfiles use ARG BASE_COMMIT;
    # we still want to migrate those if they use full clone, so the check
    # specifically asks for `git init` + `git fetch --depth=1` co-occurring.)
    if "git init " in text and "git fetch --depth=1" in text and "git clone" not in text:
        return False, "already-shallow", None
    m = find_block(text)
    if not m:
        return False, "no-clone-block", None
    repo, target, sha_token, extras = m.group(1), m.group(2), m.group(3), m.group(4) or ""

    # Resolve $BASE_COMMIT or ${BASE_COMMIT} reference if present
    if sha_token.startswith("$"):
        arg_m = ARG_RE.search(text)
        if not arg_m:
            return False, f"unresolved {sha_token} (no ARG BASE_COMMIT=<sha>)", None
        sha = arg_m.group(1)
    else:
        sha = sha_token

    new_block = build_shallow(repo, target, sha, extras)
    new_text = text[: m.start()] + new_block + text[m.end():]
    return True, f"ok repo={repo} sha={sha[:8]} target={target}", new_text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="Write changes (default: dry-run, show diffs)")
    ap.add_argument("--limit", type=int, default=0,
                    help="Process at most N Dockerfiles (for spot-check)")
    ap.add_argument("--show-diff", action="store_true",
                    help="Print first 30 lines of each changed file's diff")
    ap.add_argument("--task-glob", default="*",
                    help="Glob filter on task dir name (e.g. 'effect-*')")
    args = ap.parse_args()

    paths = sorted((TASKS_DIR).glob(f"{args.task_glob}/environment/Dockerfile"))
    if args.limit:
        paths = paths[: args.limit]

    counts = {"ok": 0, "already-shallow": 0, "no-clone-block": 0}
    samples_shown = 0
    for p in paths:
        changed, status, new_text = migrate_one(p)
        key = "ok" if changed else status
        counts[key] = counts.get(key, 0) + 1
        if changed:
            if args.show_diff and samples_shown < 5:
                print(f"\n--- {p.relative_to(ROOT)} ({status}) ---")
                # Show a few lines around the change site
                old_lines = p.read_text().splitlines()
                new_lines = new_text.splitlines()
                # Find first divergence
                for i, (a, b) in enumerate(zip(old_lines, new_lines)):
                    if a != b:
                        start = max(0, i - 1)
                        print("OLD:")
                        for line in old_lines[start:start+8]:
                            print(f"  {line}")
                        print("NEW:")
                        for line in new_lines[start:start+8]:
                            print(f"  {line}")
                        break
                samples_shown += 1
            if args.apply:
                p.write_text(new_text)
        elif status == "no-clone-block":
            print(f"  SKIP (no clone block): {p.relative_to(ROOT)}",
                  file=sys.stderr)

    print(f"\n=== Summary ({len(paths)} dockerfiles) ===")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    if not args.apply:
        print("\n(dry-run — pass --apply to write)")


if __name__ == "__main__":
    main()
