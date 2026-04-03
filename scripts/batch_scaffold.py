#!/usr/bin/env python3
"""Batch scaffold harbor tasks from scouted PRs using claude -p.

Reads scouted_prs.jsonl and runs the scaffold-task command for each PR
via `claude -p` with parallelism control.

Usage:
    python scripts/batch_scaffold.py --input scouted_prs.jsonl --workers 4
    python scripts/batch_scaffold.py --input scouted_prs.jsonl --workers 4 --offset 100 --limit 50
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

ROOT = Path(__file__).parent.parent
HARBOR_TASKS = ROOT / "harbor_tasks"
COMMANDS_DIR = ROOT / ".claude" / "commands"
LOG_DIR = ROOT / "pipeline_logs"


def load_command() -> str:
    """Load the scaffold-task command template."""
    cmd_file = COMMANDS_DIR / "scaffold-task.md"
    return cmd_file.read_text()


def get_existing_tasks() -> set[str]:
    """Get names of existing task directories."""
    return {d.name for d in HARBOR_TASKS.iterdir() if d.is_dir() and (d / "task.toml").exists()}


async def scaffold_one(
    pr: dict,
    prompt_template: str,
    model: str,
    budget: float,
    timeout: int,
    sem: asyncio.Semaphore,
    log_dir: Path,
) -> dict:
    """Scaffold a single task from a PR."""
    repo = pr["repo"]
    pr_num = pr["pr_number"]
    pr_ref = f"{repo}#{pr_num}"

    result = {
        "pr_ref": pr_ref,
        "repo": repo,
        "pr_number": pr_num,
        "status": "pending",
        "started_at": datetime.now().isoformat(),
    }

    log_file = log_dir / f"{repo.replace('/', '_')}_{pr_num}.json"

    async with sem:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] START {pr_ref}")

        prompt = prompt_template.replace("$ARGUMENTS", pr_ref)

        try:
            proc = await asyncio.create_subprocess_exec(
                "claude", "-p",
                "--dangerously-skip-permissions",
                "--model", model,
                "--max-budget-usd", str(budget),
                "--output-format", "json",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(ROOT),
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(prompt.encode()),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                result["status"] = "timeout"
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] TIMEOUT {pr_ref}")
                json.dump(result, open(log_file, "w"), indent=2)
                return result

            stdout_text = stdout.decode("utf-8", errors="replace")
            stderr_text = stderr.decode("utf-8", errors="replace")

            try:
                output = json.loads(stdout_text)
                result["result"] = output.get("result", "")[:3000]
                result["session_id"] = output.get("session_id")
                result["usage"] = output.get("usage")
            except json.JSONDecodeError:
                result["stdout_tail"] = stdout_text[-2000:]

            result["exit_code"] = proc.returncode
            if stderr_text:
                result["stderr_tail"] = stderr_text[-500:]

            if "Exceeded USD budget" in stdout_text or "Exceeded USD budget" in stderr_text:
                result["status"] = "budget_exceeded"
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] BUDGET {pr_ref}")
            elif proc.returncode == 0:
                result["status"] = "success"
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] OK {pr_ref}")
            else:
                result["status"] = "error"
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] FAIL {pr_ref} (exit {proc.returncode})")

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)[:500]
            print(f"  [{datetime.now().strftime('%H:%M:%S')}] ERROR {pr_ref}: {e}")

        result["finished_at"] = datetime.now().isoformat()
        json.dump(result, open(log_file, "w"), indent=2)
        return result


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="scouted_prs.jsonl")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--model", default="opus")
    parser.add_argument("--budget", type=float, default=5.0)
    parser.add_argument("--timeout", type=int, default=900, help="Seconds per scaffold")
    parser.add_argument("--offset", type=int, default=0, help="Skip first N PRs")
    parser.add_argument("--limit", type=int, help="Max PRs to scaffold")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    input_path = ROOT / args.input
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        sys.exit(1)

    with open(input_path) as f:
        all_prs = [json.loads(line) for line in f if line.strip()]

    # Apply offset and limit
    prs = all_prs[args.offset:]
    if args.limit:
        prs = prs[:args.limit]

    # Filter out PRs for tasks that already exist
    existing = get_existing_tasks()
    # We can't know the task name ahead of time, but we can check by repo+PR
    existing_prs = set()
    for task_dir in HARBOR_TASKS.iterdir():
        toml = task_dir / "task.toml"
        if not toml.exists():
            continue
        text = toml.read_text()
        for line in text.splitlines():
            if line.startswith("source_pr"):
                try:
                    pr_num = int(line.split("=")[1].strip())
                    existing_prs.add(pr_num)
                except ValueError:
                    pass

    prs = [p for p in prs if p["pr_number"] not in existing_prs]

    print(f"Input: {len(all_prs)} PRs total")
    print(f"After offset/limit/dedup: {len(prs)} PRs to scaffold")
    print(f"Workers: {args.workers}, Model: {args.model}, Budget: ${args.budget}")

    if args.dry_run:
        for p in prs[:20]:
            print(f"  {p['repo']}#{p['pr_number']}: {p['title'][:60]}")
        if len(prs) > 20:
            print(f"  ... and {len(prs) - 20} more")
        return

    prompt_template = load_command()
    log_dir = LOG_DIR / f"scaffold_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_dir.mkdir(parents=True, exist_ok=True)

    sem = asyncio.Semaphore(args.workers)
    coros = [
        scaffold_one(pr, prompt_template, args.model, args.budget, args.timeout, sem, log_dir)
        for pr in prs
    ]

    start = time.time()
    results = await asyncio.gather(*coros)
    elapsed = time.time() - start

    by_status = {}
    for r in results:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1

    print(f"\n{'='*60}")
    print(f"  Scaffolding done in {elapsed:.0f}s")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")
    print(f"{'='*60}")

    summary_file = log_dir / "_summary.json"
    json.dump({
        "total": len(results),
        "elapsed_sec": elapsed,
        "by_status": by_status,
        "results": results,
    }, open(summary_file, "w"), indent=2)
    print(f"  Logs: {log_dir}")


if __name__ == "__main__":
    asyncio.run(main())
