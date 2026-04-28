#!/usr/bin/env python3
"""Find skill-authoring PRs via Code Search → per-repo PR enumeration.

Complements `discover_recent_skill_prs.py`. The title-only scout misses PRs
whose title doesn't quote the rule file name ("docs: update guidelines"
that adds CLAUDE.md). This script finds those via:

  Phase 1 — Code Search by filename + path:
    Enumerate every repo on GitHub that has a tier-1 rule file in its
    default branch. Subdivide queries by path/extension to break the
    1000-result cap. Output: deduped (repo) set.

  Phase 2 — Per-repo merged-PR enumeration via GraphQL:
    For each unique repo, list merged PRs since --since. Filter PRs whose
    file_paths match TIER1_DISCOVERY_RE. Output: JSONL in the same shape
    as discover_recent_skill_prs.py's output.

Rate limits: code search = 10/min, GraphQL = 5K/hr.
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from taskforge.config import TIER1_DISCOVERY_RE
from taskforge.gh_graphql import _gh_graphql, _alias

# Code-search queries — each capped at 1000 results, but path/extension
# subdivision spreads the universe across multiple buckets.
CODE_QUERIES = [
    # Tier-1 entrypoints (top-level)
    "filename:CLAUDE.md",
    "filename:CLAUDE.local.md",
    "filename:AGENTS.md",
    "filename:AGENT.md",                 # singular variant
    "filename:CONVENTIONS.md",
    # SKILL.md by path — captures every skill convention. Path-subdivided
    # to break the 1000 cap; bare filename:SKILL.md (no path) is added
    # last so it catches any oddly-located ones.
    "filename:SKILL.md path:skills/",
    "filename:SKILL.md path:.claude/skills/",
    "filename:SKILL.md path:.agents/skills/",
    "filename:SKILL.md path:.agent/skills/",     # singular dir
    "filename:SKILL.md path:.opencode/skills/",
    "filename:SKILL.md path:.codex/skills/",
    "filename:SKILL.md path:.github/skills/",
    "filename:SKILL.md",                  # broad fallback for non-standard paths
    # Sub-rule files inside .claude/
    "path:.claude/rules/ extension:md",
    "path:.claude/agents/ extension:md",
    # Cursor / windsurf / cline / continue
    "filename:.cursorrules",
    "filename:.cursorrule",               # rare singular
    "filename:.windsurfrules",
    "filename:.clinerules",
    "filename:.continuerules",
    "extension:mdc path:.cursor/rules/",
    "extension:mdc",                      # broad MDC fallback
    # Copilot / GitHub
    "filename:copilot-instructions.md",
    "path:.github/prompts/ extension:md",
]


def gh_code_search(query: str, max_pages: int = 10) -> list[tuple[str, str]]:
    """Page through code search. Returns [(repo, path), ...]."""
    out: list[tuple[str, str]] = []
    for page in range(1, max_pages + 1):
        try:
            r = subprocess.run(
                ["gh", "api", "-X", "GET", "search/code",
                 "-F", f"q={query}",
                 "-F", "per_page=100",
                 "-F", f"page={page}"],
                capture_output=True, text=True, timeout=60)
            if r.returncode != 0:
                # 422 = page out of range, 403 = rate-limited; both mean stop
                if "403" in r.stderr or "rate" in r.stderr.lower():
                    print(f"    rate-limited at page {page}, sleeping 60s", flush=True)
                    time.sleep(60)
                    continue
                break
            body = json.loads(r.stdout)
            items = body.get("items", []) or []
            if not items:
                break
            for it in items:
                repo = (it.get("repository") or {}).get("full_name") or ""
                path = it.get("path") or ""
                if repo and path:
                    out.append((repo, path))
            if len(items) < 100:
                break
            # Code-search rate limit is 10/min — sleep 7s between page calls
            time.sleep(7)
        except Exception as e:
            print(f"    error page {page}: {e}", flush=True)
            break
    return out


def enumerate_recent_prs_for_repo(repo: str, since: str,
                                  max_prs: int = 100) -> list[dict]:
    """List merged PRs in repo since `since` via GraphQL.

    Returns [{pr_number, title, merged_at, file_paths}, ...] for PRs whose
    files match TIER1_DISCOVERY_RE.
    """
    try:
        owner, name = repo.split("/", 1)
    except ValueError:
        return []
    owner = owner.replace('"', '\\"')
    name = name.replace('"', '\\"')
    query = f"""
    query {{
      repository(owner: "{owner}", name: "{name}") {{
        pullRequests(states: MERGED, first: {max_prs},
                     orderBy: {{field: UPDATED_AT, direction: DESC}}) {{
          nodes {{
            number
            title
            mergedAt
            files(first: 50) {{ nodes {{ path }} }}
          }}
        }}
      }}
    }}"""
    data = _gh_graphql(query, timeout=60)
    if not data:
        return []
    repo_node = data.get("repository") or {}
    nodes = ((repo_node.get("pullRequests") or {}).get("nodes")) or []
    out: list[dict] = []
    for n in nodes:
        merged_at = n.get("mergedAt") or ""
        if merged_at < since:
            continue
        files_n = ((n.get("files") or {}).get("nodes")) or []
        paths = [f.get("path", "") for f in files_n if f.get("path")]
        # Keep only PRs whose changed files include any tier-1 path
        if not any(TIER1_DISCOVERY_RE.search(p) for p in paths):
            continue
        out.append({
            "repo": repo,
            "pr_number": n.get("number"),
            "title": n.get("title", ""),
            "merged_at": merged_at,
            "file_paths": paths,
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2025-09-01")
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--max-pages", type=int, default=10,
                    help="Per code-search query max pages")
    ap.add_argument("--max-prs", type=int, default=100,
                    help="Per-repo max merged PRs to enumerate")
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--repos-cache", type=Path,
                    default=Path("/tmp/code_search_repos.txt"),
                    help="Skip Phase 1 if this file exists; use its contents")
    args = ap.parse_args()

    # Phase 1 — code search to find repos with rule files
    if args.repos_cache.exists() and args.repos_cache.stat().st_size > 0:
        print(f"Phase 1: using cached repos from {args.repos_cache}", flush=True)
        repos = sorted({r.strip() for r in open(args.repos_cache) if r.strip()})
    else:
        print(f"Phase 1: Code Search across {len(CODE_QUERIES)} queries", flush=True)
        repo_set: set[str] = set()
        for q in CODE_QUERIES:
            print(f"  Query: {q}", flush=True)
            hits = gh_code_search(q, max_pages=args.max_pages)
            n_before = len(repo_set)
            for repo, path in hits:
                repo_set.add(repo)
            print(f"    +{len(repo_set) - n_before} new repos "
                  f"({len(hits)} total hits)", flush=True)
        repos = sorted(repo_set)
        args.repos_cache.write_text("\n".join(repos) + "\n")
        print(f"Phase 1 done. {len(repos)} unique repos. "
              f"Cached → {args.repos_cache}", flush=True)

    # Phase 2 — per-repo merged-PR enumeration via GraphQL
    print(f"\nPhase 2: enumerating merged PRs (since {args.since}) "
          f"across {len(repos)} repos via GraphQL", flush=True)
    all_prs: list[dict] = []
    started = time.monotonic()

    def one(repo):
        return enumerate_recent_prs_for_repo(repo, args.since,
                                             max_prs=args.max_prs)

    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        for i, prs in enumerate(ex.map(one, repos)):
            all_prs.extend(prs)
            if (i + 1) % 100 == 0:
                rate = (i + 1) / max(1e-9, time.monotonic() - started)
                print(f"  [{i+1}/{len(repos)}] {rate:.1f} repo/s, "
                      f"{len(all_prs)} matched PRs so far", flush=True)

    print(f"\nFound {len(all_prs)} skill-authoring PRs across "
          f"{len(repos)} repos", flush=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        for r in all_prs:
            f.write(json.dumps(r) + "\n")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
