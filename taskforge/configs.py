"""Pre-fetch agent config files for harbor tasks at their exact base commits.

Writes one markdown file per task at harbor_tasks/{task}/agent_configs.md
containing the full content of every agent config file found at the base commit.

Usage:
    python -m taskforge.configs                       # all tasks
    python -m taskforge.configs --tasks "areal-*"     # glob filter
    python -m taskforge.configs --workers 8            # parallel fetches
    python -m taskforge.configs --force                # re-fetch cached
    python -m taskforge.configs --task-dir harbor_tasks_agentmd_edits
"""

from __future__ import annotations

import argparse
import base64
import fnmatch
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).parent.parent

CONFIG_NAMES = {
    "CLAUDE.md", "AGENTS.md", "SKILL.md", ".cursorrules",
    ".windsurfrules", ".clinerules", ".continuerules",
    "copilot-instructions.md", "CONVENTIONS.md",
}
CONFIG_DIR_PREFIXES = (".cursor/rules/", ".claude/skills/", ".claude/commands/", ".cody/")


def _gh_api(endpoint: str, jq: str = "", retries: int = 3) -> str:
    cmd = ["gh", "api", endpoint]
    if jq:
        cmd += ["--jq", jq]
    for attempt in range(retries):
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            return r.stdout.strip()
        if "rate limit" in r.stderr.lower():
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


def _fetch_file(repo: str, path: str, commit: str) -> str:
    """Fetch a single file's content at a specific commit."""
    content_b64 = _gh_api(
        f"repos/{repo}/contents/{path}?ref={commit}",
        ".content",
    )
    if not content_b64:
        return ""
    try:
        return base64.b64decode(content_b64).decode("utf-8", errors="replace")
    except Exception:
        return ""


def _get_modified_dirs(harbor_dir: Path, task_name: str) -> set[str]:
    """Get directories modified by the PR (from solve.sh patch)."""
    solve = harbor_dir / task_name / "solution" / "solve.sh"
    if not solve.exists():
        return set()
    content = solve.read_text()
    dirs: set[str] = set()
    for line in content.splitlines():
        if line.startswith("diff --git") or line.startswith("---") or line.startswith("+++"):
            parts = line.split()
            for p in parts:
                if "/" in p and not p.startswith("---") and not p.startswith("+++"):
                    p = p.lstrip("ab/")
                    if "/" in p:
                        dirs.add(p.rsplit("/", 1)[0])
    return dirs


def fetch_task_configs(
    task: dict,
    harbor_dir: Path,
) -> tuple[str, str, int]:
    """Fetch all config files for one task. Returns (task_name, status, file_count)."""
    name = task["task"]
    repo = task["repo"]
    commit = task["base_commit"]
    output_file = harbor_dir / name / "agent_configs.md"

    if output_file.exists() and output_file.stat().st_size > 500:
        return name, "cached", 0

    # Discover all files in tree
    all_paths_raw = _gh_api(
        f"repos/{repo}/git/trees/{commit}?recursive=1",
        ".tree[].path",
    )
    all_paths = [p.strip() for p in all_paths_raw.splitlines() if p.strip()]

    paths: list[str] = []
    readme_paths: list[str] = []
    for p in all_paths:
        basename = p.rsplit("/", 1)[-1] if "/" in p else p
        if basename in CONFIG_NAMES:
            paths.append(p)
        elif any(p.startswith(prefix) for prefix in CONFIG_DIR_PREFIXES):
            paths.append(p)
        elif basename == "README.md":
            readme_paths.append(p)

    modified_dirs = _get_modified_dirs(harbor_dir, name)
    for rp in readme_paths:
        if rp == "README.md":
            paths.append(rp)
        elif "/" in rp:
            readme_dir = rp.rsplit("/", 1)[0]
            if any(readme_dir in d or d in readme_dir for d in modified_dirs):
                paths.append(rp)

    if not paths:
        output_file.write_text(f"# No agent config files found\n\nRepo: {repo}\nCommit: {commit}\n")
        return name, "empty", 0

    sections = [
        f"# Agent Config Files for {name}\n",
        f"Repo: {repo}",
        f"Commit: {commit}",
        f"Files found: {len(paths)}\n",
    ]

    fetched = 0
    for path in sorted(set(paths)):
        content = _fetch_file(repo, path, commit)
        if content:
            numbered = "\n".join(
                f"{i+1:4d} | {line}"
                for i, line in enumerate(content.splitlines())
            )
            sections.append(f"\n---\n## {path}\n\n```\n{numbered}\n```\n")
            fetched += 1
        time.sleep(0.1)

    output_file.write_text("\n".join(sections))
    return name, "ok", fetched


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch agent config files for harbor tasks")
    parser.add_argument("--tasks", help="Glob filter for task names")
    parser.add_argument("--task-dir", default="harbor_tasks", help="Task directory")
    parser.add_argument("--metadata", default="task_metadata.jsonl", help="Metadata JSONL file")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--force", action="store_true", help="Re-fetch even if cached")
    args = parser.parse_args()

    harbor_dir = ROOT / args.task_dir
    metadata_path = ROOT / args.metadata

    if not metadata_path.exists():
        print(f"Metadata file not found: {metadata_path}", file=sys.stderr)
        sys.exit(1)

    tasks = []
    with open(metadata_path) as f:
        for line in f:
            d = json.loads(line)
            if args.tasks and not fnmatch.fnmatch(d["task"], args.tasks):
                continue
            tasks.append(d)

    if args.force:
        for t in tasks:
            cached = harbor_dir / t["task"] / "agent_configs.md"
            if cached.exists():
                cached.unlink()

    print(f"Fetching configs for {len(tasks)} tasks ({args.workers} workers)")

    statuses: dict[str, int] = {"ok": 0, "empty": 0, "cached": 0, "error": 0}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(fetch_task_configs, t, harbor_dir): t for t in tasks}
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
