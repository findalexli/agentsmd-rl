#!/usr/bin/env python3
"""Pre-fetch all agent config files for each task at its exact base commit.

Outputs one markdown file per task at repo_configs/{task_name}.md containing
the full content of every agent config file found at the task's base commit.

Usage:
    python scripts/fetch_configs.py                    # all tasks
    python scripts/fetch_configs.py --tasks "areal-*"  # glob filter
    python scripts/fetch_configs.py --workers 8         # parallel fetches
"""

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).parent.parent
METADATA = ROOT / "task_metadata.jsonl"
OUTPUT_DIR = None  # Written to harbor_tasks/{task}/agent_configs.md
HARBOR = ROOT / "harbor_tasks"

# Patterns to search for in the git tree
CONFIG_PATTERN = (
    r"CLAUDE\.md|AGENTS\.md|SKILL\.md|"
    r"\.cursorrules|\.cursor/rules|"
    r"copilot-instructions\.md|"
    r"\.windsurfrules|\.clinerules|\.continuerules|"
    r"\.cody|CONVENTIONS\.md"
)

# README.md — only fetch root + directories touched by the PR
README_PATTERN = r"README\.md"


def gh_api(endpoint: str, jq: str = "", retries: int = 3) -> str:
    cmd = ["gh", "api", endpoint]
    if jq:
        cmd += ["--jq", jq]
    for attempt in range(retries):
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            return r.stdout.strip()
        if "rate limit" in r.stderr.lower():
            # Wait for rate limit reset
            try:
                reset_r = subprocess.run(
                    ["gh", "api", "rate_limit", "--jq", ".rate.reset"],
                    capture_output=True, text=True, timeout=10,
                )
                reset_ts = int(reset_r.stdout.strip())
                wait = max(reset_ts - int(time.time()) + 5, 10)
                print(f"    Rate limited, waiting {wait}s for reset...", file=sys.stderr)
                time.sleep(wait)
            except Exception:
                time.sleep(60)
        elif attempt < retries - 1:
            time.sleep(2)
    return ""


def fetch_file(repo: str, path: str, commit: str) -> str:
    """Fetch a single file's content at a specific commit."""
    content_b64 = gh_api(
        f"repos/{repo}/contents/{path}?ref={commit}",
        ".content"
    )
    if not content_b64:
        return ""
    import base64
    try:
        return base64.b64decode(content_b64).decode("utf-8", errors="replace")
    except Exception:
        return ""


def get_modified_dirs(task_name: str) -> set[str]:
    """Get directories modified by the PR (from solve.sh patch)."""
    solve = HARBOR / task_name / "solution" / "solve.sh"
    if not solve.exists():
        return set()
    content = solve.read_text()
    dirs = set()
    for line in content.splitlines():
        if line.startswith("diff --git") or line.startswith("---") or line.startswith("+++"):
            parts = line.split()
            for p in parts:
                if "/" in p and not p.startswith("---") and not p.startswith("+++"):
                    p = p.lstrip("ab/")
                    if "/" in p:
                        dirs.add(p.rsplit("/", 1)[0])
    return dirs


def fetch_task_configs(task: dict) -> tuple[str, str, int]:
    """Fetch all config files for one task. Returns (task_name, status, file_count)."""
    name = task["task"]
    repo = task["repo"]
    commit = task["base_commit"]
    output_file = HARBOR / name / "agent_configs.md"

    if output_file.exists() and output_file.stat().st_size > 500:
        return name, "cached", 0

    # Discover all files in tree, filter in Python (avoids jq regex escaping hell)
    all_paths_raw = gh_api(
        f"repos/{repo}/git/trees/{commit}?recursive=1",
        ".tree[].path",
    )
    all_paths = [p.strip() for p in all_paths_raw.splitlines() if p.strip()]

    CONFIG_NAMES = {
        "CLAUDE.md", "AGENTS.md", "SKILL.md", ".cursorrules",
        ".windsurfrules", ".clinerules", ".continuerules",
        "copilot-instructions.md", "CONVENTIONS.md",
    }
    CONFIG_DIR_PREFIXES = (".cursor/rules/", ".claude/skills/", ".claude/commands/", ".cody/")

    paths = []
    readme_paths = []
    for p in all_paths:
        basename = p.rsplit("/", 1)[-1] if "/" in p else p
        if basename in CONFIG_NAMES:
            paths.append(p)
        elif any(p.startswith(prefix) for prefix in CONFIG_DIR_PREFIXES):
            paths.append(p)
        elif basename == "README.md":
            readme_paths.append(p)
    modified_dirs = get_modified_dirs(name)
    for rp in readme_paths:
        # Root README always included
        if rp == "README.md":
            paths.append(rp)
        # Subdir README only if PR touches that dir
        elif "/" in rp:
            readme_dir = rp.rsplit("/", 1)[0]
            if any(readme_dir in d or d in readme_dir for d in modified_dirs):
                paths.append(rp)

    if not paths:
        output_file.write_text(f"# No agent config files found\n\nRepo: {repo}\nCommit: {commit}\n")
        return name, "empty", 0

    # Fetch each file
    sections = []
    sections.append(f"# Agent Config Files for {name}\n")
    sections.append(f"Repo: {repo}")
    sections.append(f"Commit: {commit}")
    sections.append(f"Files found: {len(paths)}\n")

    fetched = 0
    for path in sorted(set(paths)):
        content = fetch_file(repo, path, commit)
        if content:
            # Add line numbers for source attribution
            numbered = "\n".join(
                f"{i+1:4d} | {line}"
                for i, line in enumerate(content.splitlines())
            )
            sections.append(f"\n---\n## {path}\n\n```\n{numbered}\n```\n")
            fetched += 1
        time.sleep(0.1)  # Rate limit courtesy

    output_file.write_text("\n".join(sections))
    return name, "ok", fetched


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", help="Glob filter for task names")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--force", action="store_true", help="Re-fetch even if cached")
    args = parser.parse_args()

    # Output goes to harbor_tasks/{task}/agent_configs.md

    # Load metadata
    tasks = []
    with open(METADATA) as f:
        for line in f:
            d = json.loads(line)
            if args.tasks:
                import fnmatch
                if not fnmatch.fnmatch(d["task"], args.tasks):
                    continue
            tasks.append(d)

    if args.force:
        for t in tasks:
            cached = HARBOR / t["task"] / "agent_configs.md"
            if cached.exists():
                cached.unlink()

    print(f"Fetching configs for {len(tasks)} tasks ({args.workers} workers)")

    statuses = {"ok": 0, "empty": 0, "cached": 0, "error": 0}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(fetch_task_configs, t): t for t in tasks}
        done = 0
        for future in as_completed(futures):
            done += 1
            try:
                name, status, count = future.result()
                statuses[status] += 1
                if done % 50 == 0 or status == "error":
                    print(f"  [{done}/{len(tasks)}] {name}: {status} ({count} files)")
            except Exception as e:
                statuses["error"] += 1
                print(f"  ERROR: {futures[future]['task']}: {e}")

    print(f"\nDone: {json.dumps(statuses)}")


if __name__ == "__main__":
    main()
