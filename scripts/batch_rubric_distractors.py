#!/usr/bin/env python3
"""Batch Gemini rubric constructor — populates Track 4 distractors.

Groups tasks by repo, shallow-clones each repo once, checks out per-task
base commits, runs gemini_rubric_constructor, stamps results.

Usage:
    source .env && export GEMINI_API_KEY
    .venv/bin/python scripts/batch_rubric_distractors.py --limit 30
    .venv/bin/python scripts/batch_rubric_distractors.py --limit 0  # all eligible
"""

import argparse
import json
import os
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml
from taskforge.gemini_rubric_constructor import construct_rubrics, stamp_rubrics_to_manifest


TASK_DIR = Path("harbor_tasks_agentmd_edits")
CLONE_DIR = Path("/tmp/rubric_repos")


def find_eligible_tasks() -> list[dict]:
    """Find tasks with eval_manifest but no distractors yet."""
    eligible = []
    for task_path in sorted(TASK_DIR.iterdir()):
        if not task_path.is_dir():
            continue
        manifest = task_path / "eval_manifest.yaml"
        toml = task_path / "task.toml"
        if not manifest.exists() or not toml.exists():
            continue

        # Skip if already has distractors
        m_text = manifest.read_text()
        if "distractors" in m_text:
            continue

        # Parse repo + base_commit from eval_manifest.yaml source block (most reliable)
        # Falls back to task.toml fields
        repo = ""
        base_commit = ""
        try:
            m = yaml.safe_load(manifest.read_text()) or {}
            src = m.get("source", {})
            repo = src.get("repo", "")
            base_commit = src.get("base_commit", "")
        except Exception:
            pass

        if not repo or not base_commit:
            # Fallback: task.toml
            toml_text = toml.read_text()
            for line in toml_text.splitlines():
                stripped = line.strip()
                if not repo:
                    for key in ("source_repo", "repo"):
                        if stripped.startswith(f"{key} ") or stripped.startswith(f"{key}="):
                            repo = stripped.split("=", 1)[1].strip().strip('"')
                            repo = repo.strip('"')
                if not base_commit and stripped.startswith("base_commit"):
                    base_commit = stripped.split("=", 1)[1].strip().strip('"')

        if not repo or not base_commit:
            continue

        eligible.append({
            "task_name": task_path.name,
            "task_path": str(task_path),
            "repo": repo,
            "base_commit": base_commit,
        })

    return eligible


def ensure_repo_clone(repo: str) -> Path:
    """Shallow clone repo if not already cloned. Returns clone path."""
    repo_dir = CLONE_DIR / repo.replace("/", "_")
    if repo_dir.exists() and (repo_dir / ".git").exists():
        return repo_dir

    repo_dir.mkdir(parents=True, exist_ok=True)
    print(f"  Cloning {repo}...")
    subprocess.run(
        ["git", "clone", "--filter=blob:none", f"https://github.com/{repo}.git", str(repo_dir)],
        capture_output=True, timeout=300,
    )
    return repo_dir


def checkout_commit(repo_dir: Path, commit: str) -> bool:
    """Checkout specific commit. Returns True on success."""
    try:
        result = subprocess.run(
            ["git", "checkout", commit],
            cwd=repo_dir, capture_output=True, timeout=180,
        )
        if result.returncode != 0:
            # Try fetching first
            subprocess.run(
                ["git", "fetch", "origin", commit],
                cwd=repo_dir, capture_output=True, timeout=120,
            )
            result = subprocess.run(
                ["git", "checkout", commit],
                cwd=repo_dir, capture_output=True, timeout=180,
            )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"    TIMEOUT: checkout {commit[:8]} took >180s")
        return False


def run_batch(tasks: list[dict], gemini_key: str) -> dict:
    """Run rubric constructor on a batch of tasks."""
    CLONE_DIR.mkdir(parents=True, exist_ok=True)

    # Group by repo for efficient cloning
    by_repo = defaultdict(list)
    for t in tasks:
        by_repo[t["repo"]].append(t)

    results = {"ok": 0, "no_config": 0, "error": 0, "details": []}

    for repo, repo_tasks in by_repo.items():
        print(f"\n{'='*60}")
        print(f"Repo: {repo} ({len(repo_tasks)} tasks)")
        print(f"{'='*60}")

        try:
            repo_dir = ensure_repo_clone(repo)
        except Exception as e:
            print(f"  ERROR cloning: {e}")
            for t in repo_tasks:
                results["error"] += 1
                results["details"].append({"task": t["task_name"], "status": "clone_error", "error": str(e)})
            continue

        for t in repo_tasks:
            task_name = t["task_name"]
            task_path = Path(t["task_path"])
            print(f"\n  [{task_name}] commit={t['base_commit'][:8]}...")

            # Checkout base commit
            if not checkout_commit(repo_dir, t["base_commit"]):
                print(f"    SKIP: can't checkout {t['base_commit'][:8]}")
                results["error"] += 1
                results["details"].append({"task": task_name, "status": "checkout_error"})
                continue

            # Run rubric constructor
            start = time.time()
            try:
                result = construct_rubrics(task_path, repo_dir, gemini_key)
            except Exception as e:
                elapsed = time.time() - start
                print(f"    ERROR ({elapsed:.1f}s): {e}")
                results["error"] += 1
                results["details"].append({"task": task_name, "status": "error", "error": str(e)[:200]})
                continue

            elapsed = time.time() - start
            status = result.get("status", "unknown")

            if status == "no_config_files":
                print(f"    SKIP: no config files in hierarchy ({elapsed:.1f}s)")
                results["no_config"] += 1
                results["details"].append({"task": task_name, "status": "no_config"})
                continue

            if status != "ok":
                print(f"    ERROR ({elapsed:.1f}s): {status} — {result.get('error', result.get('raw', '')[:100])}")
                results["error"] += 1
                results["details"].append({"task": task_name, "status": status, "error": result.get("raw", "")[:200]})
                continue

            # Stamp results
            pos = len(result.get("positive_rubrics", []))
            neg = len(result.get("negative_rubrics", []))
            depth = result.get("hierarchy_depth", 0)
            configs = result.get("config_files", [])

            try:
                stamp_rubrics_to_manifest(task_path, result)
                print(f"    OK ({elapsed:.1f}s): +{pos} positive, -{neg} negative, depth={depth}, configs={configs}")
                results["ok"] += 1
                results["details"].append({
                    "task": task_name, "status": "ok",
                    "positive": pos, "negative": neg,
                    "hierarchy_depth": depth, "config_files": configs,
                    "time": round(elapsed, 1),
                })
            except Exception as e:
                print(f"    ERROR stamping: {e}")
                results["error"] += 1
                results["details"].append({"task": task_name, "status": "stamp_error", "error": str(e)[:200]})

            # Rate limit: ~2s between Gemini calls
            time.sleep(1)

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=30, help="Max tasks (0=all)")
    parser.add_argument("--repo-filter", help="Only process tasks from this repo")
    parser.add_argument("--output", help="Save detailed results JSON")
    args = parser.parse_args()

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key:
        # Try .env
        env_file = Path(".env")
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    gemini_key = line.split("=", 1)[1].strip().strip('"')
                    break

    if not gemini_key:
        print("ERROR: No GEMINI_API_KEY found in env or .env")
        sys.exit(1)

    print(f"Gemini key: {gemini_key[:8]}...{gemini_key[-4:]}")

    eligible = find_eligible_tasks()
    print(f"Found {len(eligible)} eligible tasks (no distractors yet)")

    if args.repo_filter:
        eligible = [t for t in eligible if args.repo_filter in t["repo"]]
        print(f"Filtered to {len(eligible)} tasks for repo filter '{args.repo_filter}'")

    if args.limit > 0:
        # Pick diverse repos: round-robin across repos
        by_repo = defaultdict(list)
        for t in eligible:
            by_repo[t["repo"]].append(t)

        selected = []
        repo_iters = {r: iter(tasks) for r, tasks in by_repo.items()}
        while len(selected) < args.limit and repo_iters:
            empty = []
            for repo, it in repo_iters.items():
                if len(selected) >= args.limit:
                    break
                try:
                    selected.append(next(it))
                except StopIteration:
                    empty.append(repo)
            for r in empty:
                del repo_iters[r]

        eligible = selected
        print(f"Selected {len(eligible)} tasks across {len(set(t['repo'] for t in eligible))} repos")

    results = run_batch(eligible, gemini_key)

    print(f"\n{'='*60}")
    print(f"RESULTS: {results['ok']} ok, {results['no_config']} no-config, {results['error']} error")
    print(f"{'='*60}")

    if args.output:
        Path(args.output).write_text(json.dumps(results, indent=2))
        print(f"Details saved to {args.output}")


if __name__ == "__main__":
    main()
