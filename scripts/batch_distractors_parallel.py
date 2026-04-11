#!/usr/bin/env python3
"""Parallel distractor construction — no E2B needed.

Uses asyncio + concurrent repo cloning + parallel Gemini API calls.
Much faster than sequential: 735 tasks in ~30 min vs ~6 hours.

Usage:
    source .env && export GEMINI_API_KEY
    .venv/bin/python scripts/batch_distractors_parallel.py --task-dir harbor_tasks --concurrency 30
    .venv/bin/python scripts/batch_distractors_parallel.py --task-dir harbor_tasks_agentmd_edits --concurrency 30
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml
from taskforge.gemini_rubric_constructor import construct_rubrics, stamp_rubrics_to_manifest

CLONE_DIR = Path("/tmp/rubric_repos")


def find_eligible_tasks(task_dir: Path) -> list[dict]:
    """Find tasks that need distractors and have repo info."""
    eligible = []
    for task_path in sorted(task_dir.iterdir()):
        if not task_path.is_dir():
            continue
        manifest = task_path / "eval_manifest.yaml"
        if not manifest.exists():
            continue
        m_text = manifest.read_text()
        if "distractors" in m_text:
            continue

        m = yaml.safe_load(m_text) or {}
        src = m.get("source", {})
        repo = src.get("repo", "")
        base_commit = src.get("base_commit", "")

        if not repo or not base_commit:
            # Fallback: task.toml
            toml = task_path / "task.toml"
            if toml.exists():
                for line in toml.read_text().splitlines():
                    s = line.strip()
                    if not repo and (s.startswith("source_repo") or s.startswith("repo ")):
                        repo = s.split("=", 1)[1].strip().strip('"')
                    if not base_commit and s.startswith("base_commit"):
                        base_commit = s.split("=", 1)[1].strip().strip('"')

        # Fallback: parse Dockerfile for repo URL + commit
        if not repo or "/" not in repo or not base_commit:
            dockerfile = task_path / "environment" / "Dockerfile"
            if dockerfile.exists():
                import re
                df_text = dockerfile.read_text()
                repo_match = re.search(r'github\.com/([^/]+/[^\s.]+?)(?:\.git|[\s]|$)', df_text)
                commit_match = re.search(r'(?:git checkout |git fetch.*origin |ARG\s+BASE_COMMIT=)([a-f0-9]{7,40})', df_text)
                if repo_match and (not repo or "/" not in repo):
                    repo = repo_match.group(1).rstrip("/")
                if commit_match and not base_commit:
                    base_commit = commit_match.group(1)

        if repo and "/" in repo and base_commit:
            eligible.append({
                "task_name": task_path.name,
                "task_path": str(task_path),
                "repo": repo,
                "base_commit": base_commit,
            })

    return eligible


def ensure_repo_clone(repo: str) -> Path:
    """Clone repo if not already present. Returns clone path."""
    repo_dir = CLONE_DIR / repo.replace("/", "_")
    if repo_dir.exists() and (repo_dir / ".git").exists():
        return repo_dir
    repo_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--filter=blob:none",
         f"https://github.com/{repo}.git", str(repo_dir)],
        capture_output=True, timeout=300,
    )
    return repo_dir


def checkout_commit(repo_dir: Path, commit: str) -> bool:
    """Checkout a specific commit."""
    try:
        r = subprocess.run(
            ["git", "checkout", commit],
            cwd=repo_dir, capture_output=True, timeout=180,
        )
        if r.returncode != 0:
            subprocess.run(
                ["git", "fetch", "origin", commit],
                cwd=repo_dir, capture_output=True, timeout=120,
            )
            r = subprocess.run(
                ["git", "checkout", commit],
                cwd=repo_dir, capture_output=True, timeout=180,
            )
        return r.returncode == 0
    except subprocess.TimeoutExpired:
        return False


async def process_task(
    task: dict,
    gemini_key: str,
    repo_locks: dict,
    sem: asyncio.Semaphore,
    stats: dict,
) -> dict:
    """Process a single task: checkout → construct → stamp."""
    task_name = task["task_name"]
    repo = task["repo"]
    task_path = Path(task["task_path"])

    async with sem:
        # Serialize per-repo (can't checkout multiple commits simultaneously)
        lock = repo_locks.setdefault(repo, asyncio.Lock())
        async with lock:
            loop = asyncio.get_event_loop()

            # Clone + checkout in thread pool (blocking I/O)
            repo_dir = CLONE_DIR / repo.replace("/", "_")
            if not repo_dir.exists() or not (repo_dir / ".git").exists():
                await loop.run_in_executor(None, ensure_repo_clone, repo)

            ok = await loop.run_in_executor(
                None, checkout_commit, repo_dir, task["base_commit"]
            )
            if not ok:
                stats["checkout_fail"] += 1
                return {"task": task_name, "status": "checkout_fail"}

            # Construct rubrics (includes Gemini API call)
            t0 = time.time()
            try:
                result = await loop.run_in_executor(
                    None, construct_rubrics, task_path, repo_dir, gemini_key
                )
            except Exception as e:
                stats["error"] += 1
                return {"task": task_name, "status": "error", "error": str(e)[:200]}

            elapsed = time.time() - t0
            status = result.get("status", "unknown")

            if status == "no_config_files":
                stats["no_config"] += 1
                return {"task": task_name, "status": "no_config"}

            if status != "ok":
                stats["error"] += 1
                return {"task": task_name, "status": status,
                        "error": result.get("error", result.get("raw", ""))[:200]}

            # Stamp results
            try:
                stamp_rubrics_to_manifest(task_path, result)
            except Exception as e:
                stats["error"] += 1
                return {"task": task_name, "status": "stamp_error", "error": str(e)[:200]}

            pos = len(result.get("positive_rubrics", []))
            neg = len(result.get("negative_rubrics", []))
            stats["ok"] += 1
            print(f"  ✓ {task_name[:50]:50s} +{pos} -{neg} ({elapsed:.1f}s)")
            return {"task": task_name, "status": "ok", "positive": pos,
                    "negative": neg, "time": round(elapsed, 1)}


async def run_parallel(tasks: list[dict], gemini_key: str, concurrency: int) -> dict:
    """Run distractor construction in parallel."""
    CLONE_DIR.mkdir(parents=True, exist_ok=True)

    # Pre-clone repos (parallel, 5 at a time)
    repos = list(set(t["repo"] for t in tasks))
    print(f"Pre-cloning {len(repos)} repos...")
    clone_sem = asyncio.Semaphore(5)
    loop = asyncio.get_event_loop()

    async def clone_one(repo):
        async with clone_sem:
            repo_dir = CLONE_DIR / repo.replace("/", "_")
            if not repo_dir.exists() or not (repo_dir / ".git").exists():
                print(f"  Cloning {repo}...")
                await loop.run_in_executor(None, ensure_repo_clone, repo)

    await asyncio.gather(*[clone_one(r) for r in repos])
    print(f"All repos cloned.\n")

    # Process tasks with concurrency limit
    sem = asyncio.Semaphore(concurrency)
    repo_locks = {}
    stats = {"ok": 0, "no_config": 0, "checkout_fail": 0, "error": 0}

    results = await asyncio.gather(
        *[process_task(t, gemini_key, repo_locks, sem, stats) for t in tasks]
    )

    return {"stats": stats, "details": results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-dir", default="harbor_tasks")
    parser.add_argument("--concurrency", type=int, default=30)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--output", default="/tmp/distractors_parallel.json")
    args = parser.parse_args()

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key:
        env_file = Path(".env")
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    gemini_key = line.split("=", 1)[1].strip().strip('"')

    if not gemini_key:
        print("ERROR: No GEMINI_API_KEY")
        sys.exit(1)

    task_dir = Path(args.task_dir)
    eligible = find_eligible_tasks(task_dir)
    print(f"Found {len(eligible)} eligible tasks in {task_dir}")

    if args.limit:
        eligible = eligible[:args.limit]
        print(f"Limited to {len(eligible)}")

    t0 = time.time()
    results = asyncio.run(run_parallel(eligible, gemini_key, args.concurrency))
    elapsed = time.time() - t0

    stats = results["stats"]
    print(f"\n{'='*60}")
    print(f"DONE in {elapsed:.0f}s ({elapsed/60:.1f}m)")
    print(f"  OK: {stats['ok']}, No config: {stats['no_config']}, "
          f"Checkout fail: {stats['checkout_fail']}, Error: {stats['error']}")

    Path(args.output).write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
