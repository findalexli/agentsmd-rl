#!/usr/bin/env python3
"""Pre-cache repo markdown listings + content for the causality judge.

Runs gh API queries in parallel via async subprocess to populate
/tmp/markdown_fetch_cache/ before the (slow, serial) judge starts.

This turns a 50-minute synchronous setup into a 1-2 minute parallel pass.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from markdown_causality_judge import (  # noqa: E402
    _manifest_source, _list_instruction_markdowns, _fetch_markdown_via_gh,
    _FETCH_CACHE_DIR,
)


def collect_repos(corpus: Path) -> dict[str, list[Path]]:
    """Group tasks by repo. Returns {repo_slug: [task_dir]}."""
    out: dict[str, list[Path]] = {}
    for d in sorted(corpus.iterdir()):
        if not d.is_dir():
            continue
        repo, _ = _manifest_source(d)
        if repo:
            out.setdefault(repo, []).append(d)
    return out


def collect_per_repo_refs(tasks: list[Path]) -> set[str]:
    """All distinct base_commits referenced by tasks of this repo."""
    refs = set()
    for t in tasks:
        _, base = _manifest_source(t)
        if base:
            refs.add(base)
    return refs


async def _enum_repo(sem: asyncio.Semaphore, repo: str) -> list[str]:
    """Run _list_instruction_markdowns under a semaphore."""
    async with sem:
        return await asyncio.to_thread(_list_instruction_markdowns, repo, "")


async def _fetch_one(sem: asyncio.Semaphore, repo: str, path: str, ref: str) -> bool:
    async with sem:
        text = await asyncio.to_thread(_fetch_markdown_via_gh, repo, path, ref)
        return text is not None and len(text) > 0


async def main() -> None:
    corpus = Path("harbor_tasks")
    by_repo = collect_repos(corpus)
    print(f"corpus: {sum(len(v) for v in by_repo.values())} tasks across "
          f"{len(by_repo)} repos")

    # Step 1: enumerate markdown paths per repo (parallel)
    enum_sem = asyncio.Semaphore(20)
    enum_results: dict[str, list[str]] = {}

    async def runner(repo: str) -> None:
        paths = await _enum_repo(enum_sem, repo)
        enum_results[repo] = paths

    tasks = [asyncio.create_task(runner(r)) for r in by_repo]
    done = 0
    for t in asyncio.as_completed(tasks):
        await t
        done += 1
        if done % 10 == 0 or done == len(tasks):
            print(f"  enumerated {done}/{len(tasks)} repos", flush=True)

    total_paths = sum(len(v) for v in enum_results.values())
    repos_with_md = sum(1 for v in enum_results.values() if v)
    print(f"  total markdown paths: {total_paths} across {repos_with_md} repos")

    # Step 2: fetch markdown content (parallel, by repo+path+ref)
    fetch_sem = asyncio.Semaphore(20)
    fetch_jobs: list[tuple[str, str, str]] = []
    for repo, paths in enum_results.items():
        if not paths:
            continue
        # All distinct refs for this repo
        refs = collect_per_repo_refs(by_repo[repo])
        # Add empty-ref (HEAD) as fallback
        refs.add("")
        for path in paths:
            for ref in refs:
                fetch_jobs.append((repo, path, ref))

    print(f"  fetching {len(fetch_jobs)} markdown content blobs…")

    async def fetch_runner(repo: str, path: str, ref: str) -> bool:
        return await _fetch_one(fetch_sem, repo, path, ref)

    fetch_tasks = [asyncio.create_task(fetch_runner(r, p, ref))
                   for r, p, ref in fetch_jobs]
    completed = 0
    successes = 0
    for t in asyncio.as_completed(fetch_tasks):
        ok = await t
        completed += 1
        if ok:
            successes += 1
        if completed % 100 == 0 or completed == len(fetch_tasks):
            print(f"  fetched {completed}/{len(fetch_tasks)} "
                  f"({successes} hits)", flush=True)

    cache_size = len(list(_FETCH_CACHE_DIR.iterdir()))
    print(f"\nDone. Cache now has {cache_size} entries at {_FETCH_CACHE_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
