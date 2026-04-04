#!/usr/bin/env python3
"""Scout GitHub repos for PRs that update BOTH code AND agent config files.

These PRs are special: the developer made a functional change AND updated
the repo's agent instructions (CLAUDE.md, AGENTS.md, README.md, etc.).
Tasks from these PRs can test whether agents make the right config edits.

Filters:
  - Merged in last 4 months
  - Touches at least 1 code file AND at least 1 agent config file
  - Config file change is non-trivial (>2 lines added/removed)
  - Total change size: 10-800 lines
  - File count: 2-15 (must have both code + config)

Usage:
    python scripts/scout_agentmd_prs.py --output scouted_agentmd_prs.jsonl
    python scripts/scout_agentmd_prs.py --repos-file scouted_repos.jsonl --limit 15
    python scripts/scout_agentmd_prs.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from taskforge.config import is_config_file, is_code_file, gh_json

# Skip labels
SKIP_LABELS = {
    "dependencies", "documentation", "docs", "release", "ci", "chore",
    "bot", "automated", "renovate", "dependabot", "skip-ci",
}


def get_config_file_changes(repo: str, pr_number: int) -> list[dict]:
    """Get detailed file-level changes for config files in a PR.

    Returns list of {path, additions, deletions} for config files.
    """
    files = gh_json([
        "api", f"repos/{repo}/pulls/{pr_number}/files",
        "--paginate",
        "--jq", '[.[] | {path: .filename, additions: .additions, deletions: .deletions, status: .status}]',
    ])
    if not files:
        return []
    # gh --jq with --paginate returns arrays that get concatenated
    if isinstance(files, list) and files and isinstance(files[0], list):
        files = [f for page in files for f in page]
    return [f for f in files if is_config_file(f.get("path", ""))]


def scout_repo(
    repo: str,
    target: int,
    existing: set[tuple[str, int]],
    cutoff_date: str,
    caution: str | None = None,
    check_config_diff: bool = True,
) -> list[dict]:
    """Scout a single repo for PRs that touch both code and config files."""
    print(f"\n{'='*60}")
    print(f"  Scouting {repo} (target: {target})")
    if caution:
        print(f"  ⚠ {caution}")
    print(f"{'='*60}")

    # Fetch many more since most PRs won't touch config files
    fetch_limit = max(target * 15, 1000)

    # Fetch merged PRs with file info
    prs = gh_json([
        "pr", "list",
        "--repo", repo,
        "--state", "merged",
        "--limit", str(fetch_limit),
        "--json", "number,title,files,changedFiles,additions,deletions,mergedAt,labels,mergeCommit",
    ], retries=3)

    if not prs:
        print(f"  No PRs found or error")
        return []

    print(f"  Fetched {len(prs)} merged PRs")

    candidates = []
    skipped = {
        "existing": 0, "too_old": 0, "label_skip": 0,
        "too_many_files": 0, "too_few_files": 0,
        "too_few_changes": 0, "too_many_changes": 0,
        "no_config_file": 0, "no_code_file": 0,
        "trivial_config_edit": 0,
    }

    for pr in prs:
        pr_num = pr.get("number", 0)

        # Skip already scaffolded
        if (repo, pr_num) in existing:
            skipped["existing"] += 1
            continue

        # Skip old PRs
        merged_at = pr.get("mergedAt", "")
        if merged_at and merged_at < cutoff_date:
            skipped["too_old"] += 1
            continue

        # Skip by labels
        pr_labels = {l.get("name", "").lower() for l in pr.get("labels", [])}
        if pr_labels & SKIP_LABELS:
            skipped["label_skip"] += 1
            continue

        changed_files = pr.get("changedFiles", 0)
        additions = pr.get("additions", 0)
        deletions = pr.get("deletions", 0)
        total_changes = additions + deletions

        # Need at least 2 files (1 code + 1 config)
        if changed_files < 2:
            skipped["too_few_files"] += 1
            continue
        if changed_files > 15:
            skipped["too_many_files"] += 1
            continue

        # Size filters
        if total_changes < 10:
            skipped["too_few_changes"] += 1
            continue
        if total_changes > 800:
            skipped["too_many_changes"] += 1
            continue

        # Check file paths for both code AND config files
        files = pr.get("files", [])
        file_paths = [f.get("path", "") for f in files] if files else []

        config_files = [f for f in file_paths if is_config_file(f)]
        code_files = [f for f in file_paths if is_code_file(f)]

        if not config_files:
            skipped["no_config_file"] += 1
            continue
        if not code_files:
            skipped["no_code_file"] += 1
            continue

        # Check config file changes are non-trivial (>2 lines changed)
        # Use file-level additions/deletions from the PR files list
        config_changes_meaningful = False
        for f in files:
            fpath = f.get("path", "")
            if is_config_file(fpath):
                f_adds = f.get("additions", 0)
                f_dels = f.get("deletions", 0)
                if f_adds + f_dels > 2:
                    config_changes_meaningful = True
                    break

        if not config_changes_meaningful and check_config_diff:
            # Fallback: check via API for detailed file changes
            config_detail = get_config_file_changes(repo, pr_num)
            config_changes_meaningful = any(
                (f.get("additions", 0) + f.get("deletions", 0)) > 2
                for f in config_detail
            )
            if not config_changes_meaningful:
                skipped["trivial_config_edit"] += 1
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
            "merged_at": merged_at,
            "merge_sha": merge_sha,
            "file_paths": file_paths[:15],
            "config_files": config_files,
            "code_files": code_files[:10],
        })

        if len(candidates) >= target:
            break

    print(f"  Candidates: {len(candidates)}")
    for reason, count in sorted(skipped.items()):
        if count > 0:
            print(f"    Skipped ({reason}): {count}")

    # Show sample config files found
    if candidates:
        all_configs = set()
        for c in candidates:
            all_configs.update(c["config_files"])
        print(f"  Config files touched: {sorted(all_configs)[:10]}")

    return candidates


def get_existing_prs(task_dir: Path) -> set[tuple[str, int]]:
    """Get (repo, pr_number) pairs for already-scaffolded tasks."""
    existing = set()
    if not task_dir.exists():
        return existing
    for td in task_dir.iterdir():
        toml = td / "task.toml"
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


def main():
    parser = argparse.ArgumentParser(description="Scout PRs that update both code and agent configs")
    parser.add_argument("--output", default="scouted_agentmd_prs.jsonl")
    parser.add_argument("--repos", help="Comma-separated repo filter")
    parser.add_argument("--repos-file", default="scouted_repos.jsonl",
                        help="JSONL file with repos (default: scouted_repos.jsonl)")
    parser.add_argument("--limit", type=int, default=15,
                        help="Per-repo target count (default: 15)")
    parser.add_argument("--months", type=int, default=4,
                        help="How many months back to search (default: 4)")
    parser.add_argument("--task-dir", default="harbor_tasks_agentmd_edits",
                        help="Task directory to check for existing tasks")
    parser.add_argument("--skip-config-diff-check", action="store_true",
                        help="Skip API call to verify config diff size (faster, less accurate)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    task_dir = ROOT / args.task_dir
    existing = get_existing_prs(task_dir)
    # Also check harbor_tasks to avoid overlap
    existing |= get_existing_prs(ROOT / "harbor_tasks")
    print(f"Existing tasks: {len(existing)} PRs across repos")

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.months * 30)
    cutoff_date = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"Cutoff date: {cutoff_date} ({args.months} months ago)")

    # Load repos
    repos_file = ROOT / args.repos_file
    repos = []
    if repos_file.exists():
        with open(repos_file) as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                repo = r["repo"]
                target = args.limit
                repos.append((repo, target, None))
        print(f"Loaded {len(repos)} repos from {repos_file}")
    else:
        print(f"ERROR: {repos_file} not found", file=sys.stderr)
        sys.exit(1)

    if args.repos:
        filter_repos = set(args.repos.split(","))
        repos = [(r, t, c) for r, t, c in repos if r in filter_repos]

    if args.dry_run:
        for repo, target, caution in repos:
            existing_count = sum(1 for r, _ in existing if r == repo)
            print(f"  {repo}: target {target}, existing {existing_count}")
        return

    all_candidates = []
    for repo, target, caution in repos:
        candidates = scout_repo(
            repo, target, existing, cutoff_date, caution,
            check_config_diff=not args.skip_config_diff_check,
        )
        all_candidates.extend(candidates)
        time.sleep(1)  # Rate limit courtesy

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

    # Config file type summary
    config_types: dict[str, int] = {}
    for c in all_candidates:
        for cf in c["config_files"]:
            basename = cf.rsplit("/", 1)[-1] if "/" in cf else cf
            config_types[basename] = config_types.get(basename, 0) + 1
    print(f"\n  Config file types:")
    for name, count in sorted(config_types.items(), key=lambda x: -x[1])[:15]:
        print(f"    {name}: {count}")

    print(f"{'='*60}")


if __name__ == "__main__":
    main()
