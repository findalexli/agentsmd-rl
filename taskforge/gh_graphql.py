"""GitHub GraphQL helpers for batched repo / PR metadata.

Why this module exists: GitHub's REST API uses a 5000/hr core bucket; a single
discover-and-classify run was burning the whole budget. GraphQL has its own
independent 5000/hr bucket AND lets us batch many repos / PRs per query via
field aliases. The end result: ~50× fewer API calls for the same data.

Single-purpose helpers:
  - batch_repo_metadata(repos)  -> dict[repo, {stars, language, ...}]
  - batch_pr_files(items)       -> dict[(repo,pr), list[path]]
  - batch_repo_bundle(repos)    -> dict[repo, {meta, tree, commits, readme}]

All functions handle errors gracefully (missing repo / private / 404) by
returning the failed key with a None or empty value, so callers can iterate
the input keys and decide what to do with each.
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import time
from typing import Iterable

# Per-query batch sizes — tuned to stay well under GraphQL node-cost limit.
REPO_BATCH = 50          # 50 repos × ~5 fields each = small footprint
PR_FILES_BATCH = 25      # PR files are heavier (nested 100-node subquery)
BUNDLE_BATCH = 25        # tree+history+blob is ~200 nodes; 25 ≈ 5K complexity


_ALIAS_INVALID_RE = re.compile(r"[^A-Za-z0-9_]")


def _alias(repo: str, suffix: str = "") -> str:
    """GraphQL aliases must match /[A-Za-z_][A-Za-z0-9_]*/."""
    s = _ALIAS_INVALID_RE.sub("_", repo)
    if suffix:
        s = f"{s}_{suffix}"
    if s and s[0].isdigit():
        s = "r_" + s
    return s


def _gh_graphql(query: str, *, timeout: int = 60) -> dict | None:
    """Call gh api graphql -f query='...' and return parsed data dict.

    Important: GitHub GraphQL returns a JSON body with both `data` and
    `errors` even for partial failures (e.g. one of N batched repos doesn't
    exist). `gh api` exits non-zero in that case, but stdout still contains
    valid JSON whose `data` map has results for the successful aliases.
    We parse stdout regardless of returncode and return whatever data is
    there — caller iterates expected aliases and treats missing ones as
    failed lookups.
    """
    for attempt in range(2):
        try:
            r = subprocess.run(
                ["gh", "api", "graphql", "-f", f"query={query}"],
                capture_output=True, text=True, timeout=timeout)
            if r.stdout:
                try:
                    body = json.loads(r.stdout)
                    return body.get("data")
                except json.JSONDecodeError:
                    pass
            if attempt == 0:
                time.sleep(2)
                continue
            return None
        except subprocess.TimeoutExpired:
            if attempt == 0:
                time.sleep(2)
                continue
            return None
    return None


def batch_repo_metadata(repos: Iterable[str]) -> dict[str, dict]:
    """Fetch stars + basic metadata for many repos in batched GraphQL calls.

    Returns {repo: {stars, primaryLanguage, isFork, isArchived, createdAt,
                    pushedAt, openIssues, description, homepage}}
    Missing/private repos get {} (empty).
    """
    out: dict[str, dict] = {r: {} for r in repos}
    repos = list(out.keys())

    for i in range(0, len(repos), REPO_BATCH):
        chunk = repos[i:i + REPO_BATCH]
        parts = []
        alias_to_repo: dict[str, str] = {}
        for r in chunk:
            try:
                owner, name = r.split("/", 1)
            except ValueError:
                continue
            a = _alias(r)
            alias_to_repo[a] = r
            # Escape quotes defensively
            owner = owner.replace('"', '\\"')
            name = name.replace('"', '\\"')
            parts.append(f"""
              {a}: repository(owner: "{owner}", name: "{name}") {{
                stargazerCount
                primaryLanguage {{ name }}
                isFork
                isArchived
                createdAt
                pushedAt
                openIssues: issues(states: OPEN) {{ totalCount }}
                description
                homepageUrl
              }}""")
        if not parts:
            continue

        query = "query { " + "\n".join(parts) + " }"
        data = _gh_graphql(query, timeout=90)
        if not data:
            continue

        for a, r in alias_to_repo.items():
            n = data.get(a)
            if not n:
                continue
            out[r] = {
                "stars": n.get("stargazerCount"),
                "primaryLanguage":
                    (n.get("primaryLanguage") or {}).get("name"),
                "isFork": n.get("isFork"),
                "isArchived": n.get("isArchived"),
                "createdAt": n.get("createdAt"),
                "pushedAt": n.get("pushedAt"),
                "openIssues":
                    (n.get("openIssues") or {}).get("totalCount"),
                "description": n.get("description"),
                "homepage": n.get("homepageUrl"),
            }
    return out


def batch_pr_files(items: Iterable[tuple[str, int]]) -> dict[tuple[str, int], list[str]]:
    """Fetch file_paths for many (repo, pr) pairs via batched GraphQL.

    Returns {(repo, pr): [path, ...]}. Capped at first 100 files per PR
    (matches REST's per_page=100 first-page semantics).
    """
    out: dict[tuple[str, int], list[str]] = {}
    items = list(items)

    for i in range(0, len(items), PR_FILES_BATCH):
        chunk = items[i:i + PR_FILES_BATCH]
        parts = []
        alias_to_key: dict[str, tuple[str, int]] = {}
        for repo, pr in chunk:
            try:
                owner, name = repo.split("/", 1)
            except ValueError:
                out[(repo, pr)] = []
                continue
            a = _alias(repo, f"pr{pr}")
            alias_to_key[a] = (repo, pr)
            owner = owner.replace('"', '\\"')
            name = name.replace('"', '\\"')
            parts.append(f"""
              {a}: repository(owner: "{owner}", name: "{name}") {{
                pullRequest(number: {pr}) {{
                  files(first: 100) {{ nodes {{ path }} }}
                }}
              }}""")
        if not parts:
            continue

        query = "query { " + "\n".join(parts) + " }"
        data = _gh_graphql(query, timeout=120)
        if not data:
            for k in alias_to_key.values():
                out.setdefault(k, [])
            continue

        for a, key in alias_to_key.items():
            n = data.get(a) or {}
            pr = (n or {}).get("pullRequest") or {}
            files = (pr.get("files") or {}).get("nodes") or []
            out[key] = [f.get("path", "") for f in files if f.get("path")]
    return out


def batch_repo_recent_prs(repos: Iterable[str], *,
                          since: str,
                          last: int = 50) -> dict[str, list[dict]]:
    """For each repo, list its merged PRs (without per-PR file expansion).

    Returns {repo: [{number, title, mergedAt}, ...]} for PRs merged after
    `since`. Cheap: ~`last` nodes per repo, batched ~50 repos per query.
    Caller should follow up with batch_pr_files for survivors that pass
    title/date/star filters — that splits the heavy `files()` subquery
    into a second batched pass.

    `last` capped at 50 in practice (GraphQL complexity per repo grows
    linearly with `last`).
    """
    out: dict[str, list[dict]] = {r: [] for r in repos}
    repos = list(out.keys())
    BATCH = 50  # ~50 PR nodes per repo × 50 repos = 2500 complexity, safe

    for i in range(0, len(repos), BATCH):
        chunk = repos[i:i + BATCH]
        parts = []
        alias_to_repo: dict[str, str] = {}
        for r in chunk:
            try:
                owner, name = r.split("/", 1)
            except ValueError:
                continue
            a = _alias(r)
            alias_to_repo[a] = r
            owner = owner.replace('"', '\\"')
            name = name.replace('"', '\\"')
            parts.append(f"""
              {a}: repository(owner: "{owner}", name: "{name}") {{
                pullRequests(states: MERGED, first: {last},
                             orderBy: {{field: UPDATED_AT, direction: DESC}}) {{
                  nodes {{ number title mergedAt }}
                }}
              }}""")
        if not parts:
            continue

        query = "query { " + "\n".join(parts) + " }"
        data = _gh_graphql(query, timeout=120)
        if not data:
            continue

        for a, r in alias_to_repo.items():
            n = data.get(a) or {}
            nodes = ((n.get("pullRequests") or {}).get("nodes")) or []
            kept = []
            for pr in nodes:
                merged_at = pr.get("mergedAt") or ""
                if merged_at and merged_at >= since:
                    kept.append({
                        "pr_number": pr.get("number"),
                        "title": pr.get("title", ""),
                        "merged_at": merged_at,
                    })
            out[r] = kept
    return out


def batch_repo_bundle(repos: Iterable[str], *,
                      tree_depth: int = 1) -> dict[str, dict]:
    """Fetch repo metadata + top-level tree + recent commits + README in
    batched GraphQL calls.

    Returns {repo: {
        "meta": {...},                  # same shape as batch_repo_metadata
        "tree": [path, ...],            # top-level paths (depth=1 by default)
        "commits": [headline, ...],     # 8 most recent default-branch commits
        "readme": "...",                # first 1500 chars of README
    }}.

    Replaces the classifier's 4 REST calls per repo with ~1 GraphQL call per
    25 repos (~100× fewer requests).
    """
    out: dict[str, dict] = {r: {} for r in repos}
    repos = list(out.keys())

    for i in range(0, len(repos), BUNDLE_BATCH):
        chunk = repos[i:i + BUNDLE_BATCH]
        parts = []
        alias_to_repo: dict[str, str] = {}
        for r in chunk:
            try:
                owner, name = r.split("/", 1)
            except ValueError:
                continue
            a = _alias(r)
            alias_to_repo[a] = r
            owner = owner.replace('"', '\\"')
            name = name.replace('"', '\\"')
            # README: try README.md first; fall back to README is the caller's job
            parts.append(f"""
              {a}: repository(owner: "{owner}", name: "{name}") {{
                stargazerCount
                primaryLanguage {{ name }}
                isFork
                isArchived
                createdAt
                pushedAt
                openIssues: issues(states: OPEN) {{ totalCount }}
                description
                homepageUrl
                tree: object(expression: "HEAD:") {{
                  ... on Tree {{
                    entries {{ name type }}
                  }}
                }}
                history: defaultBranchRef {{
                  target {{
                    ... on Commit {{
                      history(first: 8) {{
                        nodes {{ messageHeadline }}
                      }}
                    }}
                  }}
                }}
                readme: object(expression: "HEAD:README.md") {{
                  ... on Blob {{ text }}
                }}
              }}""")
        if not parts:
            continue

        query = "query { " + "\n".join(parts) + " }"
        data = _gh_graphql(query, timeout=120)
        if not data:
            continue

        for a, r in alias_to_repo.items():
            n = data.get(a)
            if not n:
                continue
            tree_entries = ((n.get("tree") or {}).get("entries") or [])
            tree_paths = [e.get("name", "") for e in tree_entries if e.get("name")]
            history = (((n.get("history") or {}).get("target") or {})
                       .get("history") or {}).get("nodes") or []
            commits = [c.get("messageHeadline", "") for c in history
                       if c.get("messageHeadline")]
            readme = (n.get("readme") or {}).get("text") or ""
            out[r] = {
                "meta": {
                    "stars": n.get("stargazerCount"),
                    "primaryLanguage":
                        (n.get("primaryLanguage") or {}).get("name"),
                    "isFork": n.get("isFork"),
                    "isArchived": n.get("isArchived"),
                    "createdAt": n.get("createdAt"),
                    "pushedAt": n.get("pushedAt"),
                    "openIssues":
                        (n.get("openIssues") or {}).get("totalCount"),
                    "description": n.get("description"),
                    "homepage": n.get("homepageUrl"),
                },
                "tree": tree_paths,
                "commits": commits,
                "readme": readme[:1500],
            }
    return out
