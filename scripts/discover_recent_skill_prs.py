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


def search_prs_windowed(base_query: str, since: str, today: str,
                        max_pages: int = 10,
                        windows: int = 4) -> list[dict]:
    """Title PR search split into N date windows.

    GitHub's search API caps at 1000 results per query. For popular
    rule-file titles (SKILL.md, AGENTS.md, etc.) over 8 months, we hit the
    cap and lose the tail. Splitting into N equal date windows gives us
    N×1000 effective recall for the same rate-limit cost (well, N× search
    calls, but the search bucket refills at 30/min so it's tractable).

    base_query MUST NOT already contain a `merged:` qualifier — this fn
    appends the per-window range itself.
    """
    from datetime import datetime, timedelta
    s = datetime.fromisoformat(since)
    e = datetime.fromisoformat(today)
    span = (e - s).days
    step = max(1, span // windows)
    edges = [s + timedelta(days=step * i) for i in range(windows)] + [e]
    out: list[dict] = []
    seen_urls: set[str] = set()
    for i in range(windows):
        a = edges[i].date().isoformat()
        b = edges[i + 1].date().isoformat()
        q = f"{base_query} merged:{a}..{b}"
        print(f"  [window {i+1}/{windows}] merged:{a}..{b}", flush=True)
        items = search_prs(q, max_pages=max_pages)
        n_new = 0
        for it in items:
            u = it.get("html_url") or ""
            if u and u not in seen_urls:
                seen_urls.add(u)
                out.append(it)
                n_new += 1
        print(f"    +{n_new} new ({len(items)} returned)", flush=True)
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

    # Each query is (base, needs_windowing). Base query MUST NOT contain a
    # `merged:` qualifier — search_prs_windowed adds per-window ranges.
    # If needs_windowing is True, we split the merge window into 4 sub-windows
    # to get past GitHub's 1000-result-per-query cap.
    today = time.strftime("%Y-%m-%d")
    queries: list[tuple[str, bool]] = [
        # Direct rule-file titles — popular ones cap at 1000, window them
        ('is:pr is:merged SKILL.md in:title', True),
        ('is:pr is:merged AGENTS.md in:title', True),
        ('is:pr is:merged AGENT.md in:title', False),       # singular variant
        ('is:pr is:merged CLAUDE.md in:title', True),
        ('is:pr is:merged CLAUDE.local.md in:title', False),
        ('is:pr is:merged CONVENTIONS.md in:title', False),
        # Path-style titles — most cap at 1000
        ('is:pr is:merged ".cursor/rules" in:title', True),
        ('is:pr is:merged ".claude/skills" in:title', True),
        ('is:pr is:merged ".claude/rules" in:title', False),
        ('is:pr is:merged ".claude/agents" in:title', False),
        ('is:pr is:merged ".opencode/skills" in:title', False),
        ('is:pr is:merged ".codex/skills" in:title', False),
        ('is:pr is:merged ".agents/skills" in:title', False),
        ('is:pr is:merged ".agent/skills" in:title', False),  # singular dir variant
        ('is:pr is:merged "skills/" in:title', True),
        # Tool-specific config files — mostly under cap
        ('is:pr is:merged .cursorrules in:title', False),
        ('is:pr is:merged .cursorrule in:title', False),    # rare singular
        ('is:pr is:merged .windsurfrules in:title', False),
        ('is:pr is:merged .clinerules in:title', False),
        ('is:pr is:merged .continuerules in:title', False),
        ('is:pr is:merged .mdc in:title', False),
        ('is:pr is:merged copilot-instructions in:title', True),
        # Bare "skill" / "skills" — broad recall, very common, definitely caps.
        # GitHub's title tokenizer treats singular and plural as different
        # tokens, so we need both queries.
        ('is:pr is:merged skill in:title', True),
        ('is:pr is:merged skills in:title', True),
        # Bare "agent"/"agents" rule-file work — windowed, broad
        ('is:pr is:merged agents.md in:title', True),       # spelled lowercase
        ('is:pr is:merged agents-md in:title', False),       # hyphen variant in titles
        # Topic-based discovery (agents-md as a github topic)
        ('is:pr is:merged skill in:title agents-md in:topic', False),
    ]

    all_items: dict[tuple[str, int], dict] = {}
    for base_q, needs_window in queries:
        if needs_window:
            print(f"\nQuery (windowed x4): {base_q}", flush=True)
            items = search_prs_windowed(base_q, args.since, today,
                                        max_pages=args.max_pages, windows=4)
        else:
            q = f"{base_q} merged:>{args.since}"
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

    # Star filter — batched GraphQL (50 repos per call, ~50× fewer requests
    # than per-repo REST). Independent rate bucket from REST.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from taskforge.gh_graphql import batch_repo_metadata

    repos_seen = sorted({it["repo"] for it in all_items.values()})
    print(f"Batched GraphQL lookup of stars+metadata for {len(repos_seen)} repos",
          flush=True)
    repo_meta = batch_repo_metadata(repos_seen)
    star_cache: dict[str, int] = {r: (m.get("stars") if m.get("stars") is not None
                                      else -1)
                                  for r, m in repo_meta.items()}
    n_resolved = sum(1 for s in star_cache.values() if s >= 0)
    print(f"  resolved stars for {n_resolved}/{len(repos_seen)} repos", flush=True)

    kept = [it for it in all_items.values()
            if star_cache.get(it["repo"], -1) >= args.min_stars]
    print(f"\n{len(kept)} PRs in repos with ≥{args.min_stars} stars", flush=True)

    new_repo_kept = [it for it in kept if it["repo"].lower() not in seen_repos]
    print(f"  of those, {len(new_repo_kept)} are from repos NOT in our seen set",
          flush=True)

    # Fetch file_paths per surviving PR — batched GraphQL (25 PRs/call)
    from taskforge.gh_graphql import batch_pr_files
    pr_keys = [(it["repo"], it["pr_number"]) for it in kept]
    print(f"\nBatched GraphQL fetch of file_paths for {len(pr_keys)} PRs",
          flush=True)
    paths_by_key = batch_pr_files(pr_keys)
    rows = []
    for it in kept:
        paths = paths_by_key.get((it["repo"], it["pr_number"]), [])
        rows.append({**it, "file_paths": paths,
                     "stars": star_cache.get(it["repo"], -1)})

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
