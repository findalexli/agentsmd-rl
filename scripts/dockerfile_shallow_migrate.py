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

# Match `RUN git clone ... git checkout <sha>` — extras after the sha are
# captured separately by `extract_tail()` to avoid non-greedy BODY pitfalls.
BODY = r"(?:[^\n]|\\\n)*?"
CLONE_RE = re.compile(
    r"""RUN\s+git\s+clone\b""" + BODY + r"""
        https://github\.com/([\w.-]+/[\w.-]+?)\.git\s+(\S+)
        """ + BODY + r"""
        git\s+checkout\s+(\$\{?BASE_COMMIT\}?|[0-9a-f]{7,40})
    """,
    re.VERBOSE,
)
# Match an `ARG BASE_COMMIT=<sha>` line so we can resolve ${BASE_COMMIT} refs.
ARG_RE = re.compile(r"ARG\s+BASE_COMMIT\s*=\s*([0-9a-f]{7,40})")


def extract_tail(text: str, start_idx: int) -> tuple[str, int]:
    """Starting at `start_idx` (just past `git checkout <sha>`), walk forward
    through any `&& <command>` chain that is part of the same RUN block (i.e.,
    the previous logical line ended with `\\`). Returns (tail_str, new_end_idx)
    where new_end_idx is the index right after the last command in the chain.
    """
    i = start_idx
    n = len(text)
    end = i
    while i < n:
        # Skip any whitespace / line-continuation prefix
        j = i
        while j < n and text[j] in " \t":
            j += 1
        if j < n and text[j] == "\\" and j + 1 < n and text[j + 1] == "\n":
            j += 2
            while j < n and text[j] in " \t":
                j += 1
        # Now we should see `&&` for the chain to continue
        if j + 1 < n and text[j] == "&" and text[j + 1] == "&":
            j += 2
            # Read the command — stop at end-of-line that isn't \-continued
            while j < n:
                if text[j] == "\n":
                    # Inspect previous non-space char
                    k = j - 1
                    while k > start_idx and text[k] in " \t":
                        k -= 1
                    if k >= start_idx and text[k] == "\\":
                        j += 1  # continuation, keep going
                        continue
                    break
                j += 1
            end = j
            i = j
        else:
            break
    return text[start_idx:end], end


def find_block(text: str) -> Optional[re.Match]:
    """Find the first full-clone RUN block."""
    return CLONE_RE.search(text)


def build_shallow(repo: str, target: str, sha: str, extras: str) -> str:
    """Construct the shallow replacement RUN block."""
    abs_target = target if target.startswith("/") else f"/workspace/{target}"
    # Strip the trailing parts from `extras` that we already account for
    # (the cd and git checkout we re-emit fresh).
    extras_lines: list[str] = []
    for chunk in re.split(r"\s*&&\s*", extras):
        # Collapse any embedded line continuations (`\\\n` + indent) into
        # a single space so the chunk is a clean one-liner.
        chunk = re.sub(r"\\\s*\n\s*", " ", chunk).strip()
        # Drop trailing line-continuation slashes
        chunk = chunk.rstrip("\\").strip()
        if not chunk:
            continue
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
    if "git init " in text and "git fetch --depth=1" in text and "git clone" not in text:
        return False, "already-shallow", None
    # Don't touch Dockerfiles using sparse-checkout — they have non-trivial
    # custom clone logic (filter paths, dual-fetch, etc.). Migrating them
    # destroys the sparse setup and the resulting build fails.
    if "--sparse" in text or "git sparse-checkout" in text:
        return False, "skip (uses sparse-checkout)", None
    m = find_block(text)
    if not m:
        return False, "no-clone-block", None
    repo, target, sha_token = m.group(1), m.group(2), m.group(3)
    # Defend against the regex grabbing a shell operator as the target dir
    # (happens when `git clone <url>.git \\<newline>&& cd <dir>` with no
    # inline target — `\S+` then matches `&&`).
    if target in ("&&", "&", "|", "||", ";", "\\"):
        return False, f"skip (no inline target dir)", None
    extras, tail_end = extract_tail(text, m.end())

    if sha_token.startswith("$"):
        arg_m = ARG_RE.search(text)
        if not arg_m:
            return False, f"unresolved {sha_token} (no ARG BASE_COMMIT=<sha>)", None
        sha = arg_m.group(1)
    else:
        sha = sha_token

    new_block = build_shallow(repo, target, sha, extras)
    new_text = text[: m.start()] + new_block + text[tail_end:]
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
