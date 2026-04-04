#!/usr/bin/env python3
"""Batch scaffold agentmd-edit tasks from scouted PRs.

Reads scouted_agentmd_prs.jsonl, creates task directories, then runs
the scaffold-agentmd pipeline action via claude -p in parallel.

Usage:
    python scripts/batch_scaffold_agentmd.py --input scouted_agentmd_prs.jsonl --workers 4
    python scripts/batch_scaffold_agentmd.py --input scouted_agentmd_prs.jsonl --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
TASK_DIR = ROOT / "harbor_tasks_agentmd_edits"
TEMPLATE_DIR = ROOT / "taskforge" / "templates" / "task_template"
PROMPT_FILE = ROOT / "taskforge" / "prompts" / "scaffold_agentmd.md"
LOG_DIR = ROOT / "pipeline_logs"

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)


def slugify(repo: str, title: str) -> str:
    """Generate a task name slug from repo + PR title."""
    repo_short = repo.split("/")[-1].lower()
    # Clean title: lowercase, keep alphanumeric and spaces
    clean = re.sub(r"[^a-z0-9\s]", "", title.lower())
    words = clean.split()[:5]  # First 5 words
    slug = "-".join(words)
    if not slug:
        slug = "unnamed"
    return f"{repo_short}-{slug}"[:60]


def load_existing_tasks() -> set[tuple[str, int]]:
    """Get (repo, pr_number) pairs for already-scaffolded tasks."""
    existing = set()
    for task_dir_path in [TASK_DIR, ROOT / "harbor_tasks"]:
        if not task_dir_path.exists():
            continue
        for td in task_dir_path.iterdir():
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


async def scaffold_one(
    pr: dict,
    task_name: str,
    prompt_template: str,
    model: str,
    budget: float,
    timeout: int,
    sem: asyncio.Semaphore,
    log_dir: Path,
) -> dict:
    """Run claude -p to scaffold one task."""
    log_file = log_dir / f"{task_name}.json"
    result = {
        "task": task_name,
        "repo": pr["repo"],
        "pr": pr["pr_number"],
        "status": "pending",
        "started_at": datetime.now().isoformat(),
    }

    # Prepare task directory from template
    task_path = TASK_DIR / task_name
    if not task_path.exists():
        shutil.copytree(TEMPLATE_DIR, task_path)

    # Build prompt with PR reference
    pr_ref = f"{pr['repo']}#{pr['pr_number']}"
    prompt = prompt_template.replace("$ARGUMENTS", pr_ref)

    async with sem:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] START {task_name} ({pr_ref})")

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
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] TIMEOUT {task_name}")
                log_file.write_text(json.dumps(result, indent=2))
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

            if "SKIP:" in stdout_text:
                result["status"] = "skipped"
                # Extract skip reason
                for line in stdout_text.split("\n"):
                    if "SKIP:" in line:
                        result["skip_reason"] = line.strip()[:200]
                        break
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] SKIP {task_name}: {result.get('skip_reason', '')[:60]}")
                # Clean up empty task dir
                if task_path.exists() and not (task_path / "test_outputs.py").exists():
                    shutil.rmtree(task_path, ignore_errors=True)
            elif "Exceeded USD budget" in stdout_text or "Exceeded USD budget" in stderr_text:
                result["status"] = "budget_exceeded"
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] BUDGET {task_name}")
            elif proc.returncode == 0:
                result["status"] = "success"
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] OK {task_name}")
            else:
                result["status"] = "error"
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] FAIL {task_name} (exit {proc.returncode})")

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)[:500]
            print(f"  [{datetime.now().strftime('%H:%M:%S')}] ERROR {task_name}: {e}")

        result["finished_at"] = datetime.now().isoformat()
        log_file.write_text(json.dumps(result, indent=2))
        return result


async def main():
    parser = argparse.ArgumentParser(description="Batch scaffold agentmd-edit tasks")
    parser.add_argument("--input", default="scouted_agentmd_prs.jsonl")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--model", default="opus")
    parser.add_argument("--budget", type=float, default=6.0)
    parser.add_argument("--timeout", type=int, default=900, help="Seconds per task")
    parser.add_argument("--limit", type=int, default=None, help="Limit to first N PRs")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # Load PRs
    input_path = ROOT / args.input
    prs = []
    with open(input_path) as f:
        for line in f:
            if line.strip():
                prs.append(json.loads(line))
    print(f"Loaded {len(prs)} PR candidates from {input_path}")

    # Filter out existing
    existing = load_existing_tasks()
    prs = [pr for pr in prs if (pr["repo"], pr["pr_number"]) not in existing]
    print(f"After dedup: {len(prs)} new PRs to scaffold")

    if args.limit:
        prs = prs[:args.limit]
        print(f"Limited to first {args.limit}")

    # Generate task names
    tasks = []
    seen_names = set()
    for pr in prs:
        name = slugify(pr["repo"], pr["title"])
        # Deduplicate names
        if name in seen_names:
            name = f"{name}-{pr['pr_number']}"
        seen_names.add(name)
        tasks.append((pr, name))

    if args.dry_run:
        for pr, name in tasks:
            print(f"  {name}: {pr['repo']}#{pr['pr_number']} — {pr['title'][:60]}")
            print(f"    Config files: {pr.get('config_files', [])}")
        return

    # Ensure output dirs exist
    TASK_DIR.mkdir(exist_ok=True)
    log_dir = LOG_DIR / f"scaffold_agentmd_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Load prompt template
    prompt_template = PROMPT_FILE.read_text()

    print(f"\nScaffolding {len(tasks)} tasks (workers={args.workers}, model={args.model}, budget=${args.budget})")
    print(f"Logs: {log_dir}\n")

    sem = asyncio.Semaphore(args.workers)
    coros = [
        scaffold_one(pr, name, prompt_template, args.model, args.budget, args.timeout, sem, log_dir)
        for pr, name in tasks
    ]

    start = time.time()
    results = await asyncio.gather(*coros)
    elapsed = time.time() - start

    # Summary
    by_status: dict[str, int] = {}
    for r in results:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1

    print(f"\n{'='*60}")
    print(f"  Done in {elapsed:.0f}s ({elapsed/60:.1f}m)")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")
    print(f"  Logs: {log_dir}")
    print(f"{'='*60}")

    # Write summary
    summary_file = log_dir / "_summary.json"
    json.dump({
        "action": "scaffold-agentmd",
        "model": args.model,
        "tasks": len(tasks),
        "elapsed_sec": elapsed,
        "by_status": by_status,
        "results": results,
    }, open(summary_file, "w"), indent=2)


if __name__ == "__main__":
    asyncio.run(main())
