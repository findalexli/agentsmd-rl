#!/usr/bin/env python3
"""Batch process tasks via E2B sandboxes.

Modes:
  Validate existing:  --all or --recent 24
  Scaffold new PRs:   --input prs.jsonl [--agentmd]

Pipeline per task: [Scaffold] → P2P Enrich → Improve → Validate+Fix → Rubric Judge
Only GLM + Fireworks backends (no OAuth).

Usage:
    set -a && source .env && set +a && export GH_TOKEN=$(gh auth token)
    .venv/bin/python scripts/validate_batch.py --all --concurrency 50
    .venv/bin/python scripts/validate_batch.py --input scouted_new_prs.jsonl --concurrency 70
"""

import asyncio
import json
import random
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from taskforge.backends import Backend, BackendPool, backends_from_env
from taskforge.e2b_worker import (
    ensure_template,
    run_task_agents,
    run_task_dag,
    run_task_improve,
    write_status_json,
    WorkerResult,
    ROOT,
    logger,
)


def find_all_tasks() -> list[tuple[str, Path]]:
    """Find ALL tasks with a Dockerfile and test.sh. Returns (task_name, task_dir)."""
    tasks = []
    for d in ["harbor_tasks", "harbor_tasks_agentmd_edits"]:
        base = ROOT / d
        if not base.exists():
            continue
        for task in sorted(base.iterdir()):
            if not task.is_dir():
                continue
            if not (task / "environment" / "Dockerfile").exists():
                continue
            if not (task / "tests" / "test.sh").exists():
                continue
            tasks.append((task.name, base))
    return tasks


def find_unvalidated(recent_hours: int | None = None) -> list[tuple[str, Path]]:
    """Find all tasks without a passing validation. Returns (task_name, task_dir).

    If recent_hours is set, only include tasks whose Dockerfile was committed
    within that many hours (uses git log).
    """
    # If filtering by recency, get the set of recently-committed task paths
    recent_tasks: set[str] | None = None
    if recent_hours:
        import subprocess
        result = subprocess.run(
            ["git", "log", f"--since={recent_hours} hours ago",
             "--name-only", "--diff-filter=A", "--pretty=format:",
             "--", "harbor_tasks/*/environment/Dockerfile",
             "harbor_tasks_agentmd_edits/*/environment/Dockerfile"],
            capture_output=True, text=True, cwd=ROOT,
        )
        recent_tasks = set()
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                # "harbor_tasks/foo/environment/Dockerfile" -> "harbor_tasks/foo"
                parts = line.strip().split("/")
                if len(parts) >= 2:
                    recent_tasks.add(f"{parts[0]}/{parts[1]}")

    unvalidated = []
    for d in ["harbor_tasks", "harbor_tasks_agentmd_edits"]:
        base = ROOT / d
        if not base.exists():
            continue
        for task in sorted(base.iterdir()):
            if not task.is_dir():
                continue
            if not (task / "environment" / "Dockerfile").exists():
                continue
            if not (task / "tests" / "test.sh").exists():
                continue

            # Filter by recency if requested
            if recent_tasks is not None and f"{d}/{task.name}" not in recent_tasks:
                continue

            status = task / "status.json"
            if status.exists():
                try:
                    data = json.loads(status.read_text())
                    verdict = data.get("verdict", "")
                    validations = data.get("validations", [])
                    if verdict == "pass" or any(
                        v.get("verdict") == "pass" for v in validations
                    ):
                        continue
                except (json.JSONDecodeError, KeyError):
                    pass

            unvalidated.append((task.name, base))
    return unvalidated


def make_pool_no_oauth() -> BackendPool | None:
    """Create backend pool with only GLM + Fireworks (no OAuth)."""
    all_backends = backends_from_env()
    filtered = [b for b in all_backends if b.name != "oauth"]
    if not filtered:
        return None
    return BackendPool(filtered)


async def run_batch_mixed(
    items: list[tuple[str, Path]],
    pool: BackendPool | None,
    concurrency: int,
) -> list[WorkerResult]:
    """Run improve+validate on tasks from mixed directories."""
    sandbox_sem = asyncio.Semaphore(concurrency)
    results: list[WorkerResult] = []
    results_lock = asyncio.Lock()
    total = len(items)
    done = 0

    async def worker(task_name: str, task_dir: Path, max_retries: int = 5):
        nonlocal done
        for attempt in range(max_retries + 1):
            try:
                r = await run_task_agents(
                    task_name, task_dir, pool, sandbox_sem,
                )

                # Retry on rate limit with exponential backoff + jitter
                if "rate limited" in (r.error or "").lower() and attempt < max_retries:
                    wait = min(30 * (2 ** attempt), 300) + random.uniform(0, 30)
                    logger.info(
                        "[%s] rate limited on %s, retrying in %.0fs (%d/%d)...",
                        task_name, r.backend_name, wait, attempt + 1, max_retries,
                    )
                    await asyncio.sleep(wait)
                    continue

                # Write status.json
                if not r.downloaded:
                    task_path = task_dir / task_name
                    write_status_json(task_path, r)

                async with results_lock:
                    results.append(r)
                    done += 1
                    valid_count = sum(1 for x in results if x.valid)
                    if done % 5 == 0 or r.valid:
                        logger.info(
                            "Progress: %d/%d done, %d valid (%.0f%%)",
                            done, total, valid_count,
                            valid_count / done * 100 if done else 0,
                        )
                return
            except Exception as e:
                if attempt < max_retries:
                    logger.warning("Worker error for %s (attempt %d): %s", task_name, attempt + 1, e)
                    await asyncio.sleep(5)
                    continue
                logger.error("Worker error for %s: %s", task_name, e)
                async with results_lock:
                    results.append(
                        WorkerResult(task_ref=task_name, task_name=task_name, error=str(e)[:500])
                    )
                    done += 1

    # Launch all tasks concurrently (semaphore limits actual concurrency)
    tasks = [asyncio.create_task(worker(name, d)) for name, d in items]
    await asyncio.gather(*tasks, return_exceptions=True)
    return results


async def run_batch_scaffold(
    pr_refs: list[str],
    pool: BackendPool | None,
    concurrency: int,
    agentmd: bool = False,
) -> list[WorkerResult]:
    """Scaffold new tasks from PR refs via E2B agent-chain pipeline."""
    sandbox_sem = asyncio.Semaphore(concurrency)
    results: list[WorkerResult] = []
    results_lock = asyncio.Lock()
    total = len(pr_refs)
    done = 0
    task_dir = ROOT / ("harbor_tasks_agentmd_edits" if agentmd else "harbor_tasks")

    async def worker(pr_ref: str, max_retries: int = 5):
        nonlocal done
        for attempt in range(max_retries + 1):
            try:
                r = await run_task_agents(
                    pr_ref, task_dir, pool, sandbox_sem,
                    pr_ref=pr_ref, agentmd=agentmd,
                )

                # Retry on rate limit with exponential backoff + jitter
                if "rate limited" in (r.error or "").lower() and attempt < max_retries:
                    wait = min(30 * (2 ** attempt), 300) + random.uniform(0, 30)
                    logger.info("[%s] rate limited, retrying in %.0fs (%d/%d)...", pr_ref, wait, attempt + 1, max_retries)
                    await asyncio.sleep(wait)
                    continue

                async with results_lock:
                    results.append(r)
                    done += 1
                    valid_count = sum(1 for x in results if x.valid)
                    abandoned = sum(1 for x in results if "abandon" in (x.error or "").lower())
                    if done % 5 == 0 or r.valid:
                        logger.info(
                            "Progress: %d/%d done, %d valid, %d abandoned (%.0f%%)",
                            done, total, valid_count, abandoned,
                            valid_count / done * 100 if done else 0,
                        )
                return
            except Exception as e:
                if attempt < max_retries:
                    logger.warning("Worker error for %s (attempt %d): %s", pr_ref, attempt + 1, e)
                    await asyncio.sleep(5)
                    continue
                logger.error("Worker error for %s: %s", pr_ref, e)
                async with results_lock:
                    results.append(WorkerResult(task_ref=pr_ref, task_name=pr_ref, error=str(e)[:500]))
                    done += 1

    tasks = [asyncio.create_task(worker(ref)) for ref in pr_refs]
    await asyncio.gather(*tasks, return_exceptions=True)
    return results


async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, default=50)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--recent", type=int, default=None,
                        help="Only tasks committed within N hours")
    parser.add_argument("--all", action="store_true",
                        help="Run on ALL tasks (not just unvalidated)")
    parser.add_argument("--input", type=str, default=None,
                        help="JSONL file of PRs to scaffold (each line: {pr_ref, repo})")
    parser.add_argument("--agentmd", action="store_true",
                        help="Scaffold as agentmd_edits (code + config tasks)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not os.environ.get("E2B_API_KEY"):
        print("E2B_API_KEY not set")
        sys.exit(1)

    # Determine mode: scaffold from PRs or validate existing
    if args.input:
        # Scaffold mode: read PR refs from JSONL
        pr_items = []
        with open(args.input) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                    pr_ref = d.get("pr_ref", f"{d['repo']}#{d['pr']}")
                    pr_items.append(pr_ref)
                except (json.JSONDecodeError, KeyError):
                    continue
        if args.limit:
            pr_items = pr_items[: args.limit]
        print(f"Found {len(pr_items)} PRs to scaffold")
        if args.dry_run:
            for ref in pr_items[:20]:
                print(f"  {ref}")
            if len(pr_items) > 20:
                print(f"  ... and {len(pr_items) - 20} more")
            return
        items = None  # Signal scaffold mode
    else:
        # Validate mode: find existing tasks
        if args.all:
            items = find_all_tasks()
        else:
            items = find_unvalidated(recent_hours=args.recent)
        if args.limit:
            items = items[: args.limit]
        print(f"Found {len(items)} tasks to process")
        pr_items = None
    if pr_items is None and args.dry_run:
        for name, d in items[:20]:
            print(f"  {d.name}/{name}")
        if len(items) > 20:
            print(f"  ... and {len(items) - 20} more")
        return

    # Early exit if nothing to do
    if pr_items is not None and len(pr_items) == 0:
        print("No PRs to scaffold (empty input)")
        return
    if pr_items is None and len(items) == 0:
        print("No tasks to process")
        return

    # Build template
    await ensure_template()

    # Create pool (no OAuth)
    pool = make_pool_no_oauth()
    if pool:
        print(f"Backend pool: {pool.names}")
    else:
        print("WARNING: No backends found, improve step will be skipped")

    # Run batch
    wall_start = time.monotonic()
    if pr_items is not None:
        results = await run_batch_scaffold(pr_items, pool, args.concurrency, agentmd=args.agentmd)
    else:
        results = await run_batch_mixed(items, pool, args.concurrency)
    wall_time = time.monotonic() - wall_start

    # Summary
    valid = [r for r in results if r.valid]
    failed = [r for r in results if not r.valid and not r.error]
    errored = [r for r in results if r.error]
    improved = [r for r in results if r.improve_status == "ok"]
    skipped = [r for r in results if r.improve_status == "skipped"]

    print()
    print("=" * 80)
    print(f"  BATCH VALIDATION COMPLETE")
    print(f"  Tasks:      {len(results)}")
    print(f"  Valid:      {len(valid)}  (nop=0, gold=1)")
    print(f"  Invalid:    {len(failed)}")
    print(f"  Errors:     {len(errored)}")
    print(f"  Improved:   {len(improved)}  (tests upgraded by LLM)")
    print(f"  Skipped:    {len(skipped)}  (tests already good)")
    print(f"  Wall time:  {wall_time / 60:.1f} min")
    if results:
        print(f"  Throughput: {len(results) / wall_time * 60:.1f} tasks/min")
    if pool:
        print(f"  Pool:       {pool.stats()}")
    print("=" * 80)

    if errored[:10]:
        print("\n  ERRORS (first 10):")
        for r in errored[:10]:
            print(f"    {r.task_name}: {r.error[:80]}")

    if failed[:10]:
        print("\n  INVALID (first 10):")
        for r in failed[:10]:
            print(f"    {r.task_name}: nop={r.nop_reward} gold={r.gold_reward}")

    # Write results
    ts = time.strftime("%Y%m%d_%H%M%S")
    results_file = ROOT / "pipeline_logs" / f"e2b_validate_batch_{ts}.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "wall_time": round(wall_time, 2),
        "total": len(results),
        "valid": len(valid),
        "invalid": len(failed),
        "errors": len(errored),
        "improved": len(improved),
        "tasks": [
            {
                "task": r.task_name,
                "valid": r.valid,
                "nop": r.nop_reward,
                "gold": r.gold_reward,
                "improve": r.improve_status,
                "backend": r.backend_name,
                "time": r.total_time,
                "error": r.error[:200] if r.error else "",
            }
            for r in results
        ],
    }
    results_file.write_text(json.dumps(output, indent=2))
    print(f"\nResults: {results_file}")


if __name__ == "__main__":
    asyncio.run(main())
