#!/usr/bin/env python3
"""Scout GitHub repos for PR candidates suitable for harbor tasks.

Uses `gh` CLI to query merged PRs, filters by quality heuristics,
and outputs candidates as JSONL for batch scaffolding.

Usage:
    python scripts/scout_prs.py --limit 80 --output scouted_prs.jsonl
    python scripts/scout_prs.py --repos "oven-sh/bun,astral-sh/uv" --limit 50
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
HARBOR_TASKS = ROOT / "harbor_tasks"

# Repos to scout, with per-repo target counts and caution flags
REPOS = [
    # (owner/repo, target_count, caution_note)
    ("sgl-project/sglang", 30, None),
    ("vllm-project/vllm", 30, None),
    ("gradio-app/gradio", 40, None),
    ("huggingface/transformers", 40, None),
    ("pytorch/pytorch", 20, "large repo, be selective"),
    ("astral-sh/ruff", 35, None),
    ("vercel/next.js", 30, None),
    ("inclusionAI/AReaL", 25, None),
    ("openclaw/openclaw", 15, "vibecoded, extra careful"),
    ("elev8tion/zeroclaw", 10, "vibecoded, extra careful"),
    ("THUDM/slime", 20, None),
    ("anomalyco/opencode", 40, None),
    ("PrimeIntellect-ai/prime-rl", 20, None),
    ("thinking-machines-lab/tinker", 15, None),
    ("oven-sh/bun", 40, None),
    ("astral-sh/uv", 35, None),
]


def get_existing_prs() -> set[tuple[str, int]]:
    """Get (repo, pr_number) pairs for already-scaffolded tasks."""
    existing = set()
    for task_dir in HARBOR_TASKS.iterdir():
        toml = task_dir / "task.toml"
        if not toml.exists():
            continue
        text = toml.read_text()
        repo = pr = None
        for line in text.splitlines():
            if line.startswith("source_repo"):
                repo = line.split("=")[1].strip().strip('"')
            if line.startswith("source_pr"):
                try:
                    pr = int(line.split("=")[1].strip())
                except ValueError:
                    pass
        if repo and pr:
            existing.add((repo, pr))
    return existing


def gh_json(cmd: list[str], retries: int = 3) -> list | dict:
    """Run a gh command and parse JSON output, with retries for rate limits."""
    for attempt in range(retries):
        result = subprocess.run(
            ["gh"] + cmd,
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        if "rate limit" in result.stderr.lower() or "abuse" in result.stderr.lower():
            wait = 30 * (attempt + 1)
            print(f"  Rate limited, waiting {wait}s...", file=sys.stderr)
            time.sleep(wait)
            continue
        if result.stderr:
            print(f"  gh error: {result.stderr[:200]}", file=sys.stderr)
        return []
    return []


def scout_repo(
    repo: str,
    target: int,
    existing: set[tuple[str, int]],
    caution: str | None = None,
) -> list[dict]:
    """Scout a single repo for candidate PRs."""
    print(f"\n{'='*60}")
    print(f"  Scouting {repo} (target: {target})")
    if caution:
        print(f"  ⚠ {caution}")
    print(f"{'='*60}")

    # Fetch more than target to account for filtering
    fetch_limit = target * 4

    # Use gh pr list with JSON output
    prs = gh_json([
        "pr", "list",
        "--repo", repo,
        "--state", "merged",
        "--limit", str(fetch_limit),
        "--json", "number,title,files,changedFiles,additions,deletions,mergedAt,labels,mergeCommit",
    ])

    if not prs:
        print(f"  No PRs found or error")
        return []

    print(f"  Fetched {len(prs)} merged PRs")

    candidates = []
    skipped = {"existing": 0, "too_many_files": 0, "too_few_changes": 0,
               "too_many_changes": 0, "docs_only": 0, "deps_only": 0, "label_skip": 0}

    skip_labels = {"dependencies", "documentation", "docs", "release", "ci", "chore",
                   "bot", "automated", "renovate", "dependabot", "skip-ci"}

    for pr in prs:
        pr_num = pr.get("number", 0)

        # Skip already scaffolded
        if (repo, pr_num) in existing:
            skipped["existing"] += 1
            continue

        # Skip by labels
        pr_labels = {l.get("name", "").lower() for l in pr.get("labels", [])}
        if pr_labels & skip_labels:
            skipped["label_skip"] += 1
            continue

        changed_files = pr.get("changedFiles", 0)
        additions = pr.get("additions", 0)
        deletions = pr.get("deletions", 0)
        total_changes = additions + deletions

        # Filter: 1-5 files changed (contained fix)
        if changed_files < 1 or changed_files > 8:
            skipped["too_many_files"] += 1
            continue

        # Filter: non-trivial (at least 5 lines changed)
        if total_changes < 5:
            skipped["too_few_changes"] += 1
            continue

        # Filter: not too huge (< 500 lines total)
        if total_changes > 500:
            skipped["too_many_changes"] += 1
            continue

        # Check files for docs-only or deps-only
        files = pr.get("files", [])
        file_paths = [f.get("path", "") for f in files] if files else []

        if file_paths:
            code_files = [f for f in file_paths if not any(
                f.endswith(ext) for ext in (".md", ".rst", ".txt", ".toml", ".cfg", ".ini", ".yml", ".yaml", ".json")
            ) and not f.startswith(("docs/", "doc/", ".github/"))]

            if not code_files:
                skipped["docs_only"] += 1
                continue

            # Skip if only lockfiles/deps
            if all(any(p in f for p in ("lock", "requirements", "package.json", "Cargo.toml", "pyproject.toml"))
                   for f in file_paths):
                skipped["deps_only"] += 1
                continue

        title = pr.get("title", "")
        merge_commit = pr.get("mergeCommit", {})
        merge_sha = merge_commit.get("oid", "") if isinstance(merge_commit, dict) else ""

        candidates.append({
            "repo": repo,
            "pr_number": pr_num,
            "title": title,
            "changed_files": changed_files,
            "additions": additions,
            "deletions": deletions,
            "merged_at": pr.get("mergedAt", ""),
            "merge_sha": merge_sha,
            "file_paths": file_paths[:10],  # Truncate for readability
        })

        if len(candidates) >= target:
            break

    print(f"  Candidates: {len(candidates)}")
    for reason, count in sorted(skipped.items()):
        if count > 0:
            print(f"    Skipped ({reason}): {count}")

    return candidates


def main():
    parser = argparse.ArgumentParser(description="Scout PRs for harbor tasks")
    parser.add_argument("--output", default="scouted_prs.jsonl")
    parser.add_argument("--repos", help="Comma-separated repo filter (default: all)")
    parser.add_argument("--repos-file", help="JSONL file with repos (fields: repo, configs)")
    parser.add_argument("--limit", type=int, help="Override per-repo target count")
    parser.add_argument("--dry-run", action="store_true", help="Just show what would be scouted")
    args = parser.parse_args()

    existing = get_existing_prs()
    print(f"Existing tasks: {len(existing)} PRs across repos")

    if args.repos_file:
        # Load repos from JSONL (e.g., scouted_repos.jsonl)
        repos = []
        with open(ROOT / args.repos_file) as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                repo = r["repo"]
                target = args.limit or min(r.get("configs", 10) * 2, 50)
                repos.append((repo, target, None))
        print(f"Loaded {len(repos)} repos from {args.repos_file}")
    else:
        repos = REPOS
        if args.repos:
            filter_repos = set(args.repos.split(","))
            repos = [(r, t, c) for r, t, c in repos if r in filter_repos]

    if args.dry_run:
        for repo, target, caution in repos:
            t = args.limit or target
            existing_count = sum(1 for r, _ in existing if r == repo)
            print(f"  {repo}: target {t}, existing {existing_count}")
        return

    all_candidates = []
    for repo, target, caution in repos:
        t = args.limit or target
        candidates = scout_repo(repo, t, existing, caution)
        all_candidates.extend(candidates)
        # Small delay to avoid rate limiting
        time.sleep(1)

    # Write output
    output_path = ROOT / args.output
    with open(output_path, "w") as f:
        for c in all_candidates:
            f.write(json.dumps(c) + "\n")

    print(f"\n{'='*60}")
    print(f"  Total candidates: {len(all_candidates)}")
    print(f"  Output: {output_path}")

    # Per-repo summary
    by_repo = {}
    for c in all_candidates:
        by_repo[c["repo"]] = by_repo.get(c["repo"], 0) + 1
    for repo, count in sorted(by_repo.items()):
        print(f"    {repo}: {count}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
