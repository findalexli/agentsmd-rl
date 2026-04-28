#!/usr/bin/env python3
"""Discover recent skill-creation/update PRs across all ≥500-star GitHub repos.

Uses GitHub's PR/issue search API to find merged PRs in the last 4 months
whose title mentions a tier-1 instruction file (SKILL.md, AGENTS.md, CLAUDE.md,
.cursor/rules, etc.). Per result, fetches repo star count and filters to
≥500-star repos. Output is a JSONL of {repo, pr_number, title, file_paths}
ready to feed Pipeline B.

Usage:
    .venv/bin/python scripts/discover_recent_skill_prs.py \\
        --since 2025-12-27 \\
        --min-stars 500 \\
        --output /tmp/recent_skill_prs.jsonl
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def gh_api(*args, timeout=60):
    """Run `gh api` and return parsed JSON (or None on failure)."""
    try:
        r = subprocess.run(["gh", "api", *args],
                           capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0:
            return None
        return json.loads(r.stdout)
    except Exception:
        return None


def search_prs(query: str, max_pages: int = 10) -> list[dict]:
    """Page through GitHub issue/PR search. Returns up to max_pages × 100 PRs."""
    out = []
    for page in range(1, max_pages + 1):
        res = gh_api("-X", "GET", "search/issues",
                     "-F", f"q={query}",
                     "-F", f"per_page=100",
                     "-F", f"page={page}")
        if not res:
            break
        items = res.get("items", []) or []
        if not items:
            break
        out.extend(items)
        if len(items) < 100:
            break
        time.sleep(2)  # courtesy delay; primary rate limit kicks in fast
    return out


def list_pr_files(repo: str, pr: int) -> list[str]:
    """Fetch the file paths a PR changed.

    Pass query params directly in the URL — using `gh api -F` switches the
    request to POST, which makes a GET endpoint like `pulls/N/files` 404.
    """
    paths: list[str] = []
    for page in range(1, 4):  # up to 300 files
        try:
            r = subprocess.run(
                ["gh", "api",
                 f"repos/{repo}/pulls/{pr}/files?per_page=100&page={page}"],
                capture_output=True, text=True, timeout=30)
            if r.returncode != 0:
                break
            chunk = json.loads(r.stdout or "[]")
            if not chunk:
                break
            paths.extend(f.get("filename", "") for f in chunk if f.get("filename"))
            if len(chunk) < 100:
                break
        except Exception:
            break
    return paths


def get_stars(repo: str, cache: dict) -> int:
    """Cached repo-star lookup."""
    if repo in cache:
        return cache[repo]
    res = gh_api(f"repos/{repo}", "--jq", ".stargazers_count")
    if isinstance(res, int):
        cache[repo] = res
        return res
    cache[repo] = -1
    return -1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2025-12-27",
                    help="ISO date — only consider PRs merged after this")
    ap.add_argument("--min-stars", type=int, default=500)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--max-pages", type=int, default=10,
                    help="GitHub search returns ≤ 1000 results = 10 pages of 100")
    ap.add_argument("--seen-file", type=Path,
                    default=Path("/tmp/already_seen_v3.txt"),
                    help="One repo per line; PRs from these repos are still kept "
                         "but we only fetch file_paths once per repo")
    args = ap.parse_args()

    seen_repos = set()
    if args.seen_file.exists():
        seen_repos = set(open(args.seen_file).read().splitlines())
    print(f"Already-seen repo set size: {len(seen_repos)}", flush=True)

    queries = [
        f'is:pr is:merged merged:>{args.since} SKILL.md in:title',
        f'is:pr is:merged merged:>{args.since} AGENTS.md in:title',
        f'is:pr is:merged merged:>{args.since} CLAUDE.md in:title',
        f'is:pr is:merged merged:>{args.since} ".cursor/rules" in:title',
        f'is:pr is:merged merged:>{args.since} ".claude/skills" in:title',
        f'is:pr is:merged merged:>{args.since} skill in:title agents-md in:topic',
    ]

    all_items: dict[tuple[str, int], dict] = {}
    for q in queries:
        print(f"\nQuery: {q}", flush=True)
        items = search_prs(q, max_pages=args.max_pages)
        print(f"  -> {len(items)} hits", flush=True)
        for it in items:
            url = it.get("html_url", "") or ""
            # url shape: https://github.com/OWNER/REPO/pull/N
            try:
                parts = url.split("/")
                owner, repo, pr = parts[3], parts[4], int(parts[6])
            except Exception:
                continue
            full = f"{owner}/{repo}"
            key = (full, pr)
            if key in all_items:
                continue
            all_items[key] = {
                "repo": full,
                "pr_number": pr,
                "title": it.get("title", ""),
                "merged_at": (it.get("pull_request", {}) or {}).get("merged_at", ""),
            }

    print(f"\nUnique candidate PRs across queries: {len(all_items)}", flush=True)

    # Star filter (parallel lookups)
    star_cache: dict[str, int] = {}
    repos_seen = sorted({it["repo"] for it in all_items.values()})
    print(f"Looking up stars for {len(repos_seen)} unique repos", flush=True)

    def lookup(r):
        return r, get_stars(r, star_cache)

    with ThreadPoolExecutor(max_workers=15) as ex:
        for i, (r, s) in enumerate(ex.map(lookup, repos_seen)):
            if (i + 1) % 100 == 0:
                print(f"  [{i+1}/{len(repos_seen)}]", flush=True)

    kept = [it for it in all_items.values()
            if star_cache.get(it["repo"], -1) >= args.min_stars]
    print(f"\n{len(kept)} PRs in repos with ≥{args.min_stars} stars", flush=True)

    new_repo_kept = [it for it in kept if it["repo"].lower() not in seen_repos]
    print(f"  of those, {len(new_repo_kept)} are from repos NOT in our seen set",
          flush=True)

    # Fetch file_paths per surviving PR (parallel — this is the expensive step)
    print(f"\nFetching file_paths for {len(kept)} PRs", flush=True)

    def fill_paths(it):
        paths = list_pr_files(it["repo"], it["pr_number"])
        return {**it, "file_paths": paths,
                "stars": star_cache.get(it["repo"], -1)}

    with ThreadPoolExecutor(max_workers=10) as ex:
        rows = list(ex.map(fill_paths, kept))

    rows = [r for r in rows if r["file_paths"]]
    print(f"  {len(rows)} have non-empty file_paths", flush=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"\nWrote {args.output}", flush=True)

    # Quick stats
    by_stars = sorted(rows, key=lambda r: -r["stars"])
    print("\nTop 10 ≥500-star repos contributing PRs:")
    repo_counts: dict[str, int] = {}
    for r in rows:
        repo_counts[r["repo"]] = repo_counts.get(r["repo"], 0) + 1
    for repo, n in sorted(repo_counts.items(), key=lambda x: -x[1])[:10]:
        s = star_cache.get(repo, -1)
        print(f"  {n:4d} PRs   {s:>6} stars   {repo}")


if __name__ == "__main__":
    main()
