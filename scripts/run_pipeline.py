#!/usr/bin/env python3
"""Pipeline orchestrator: run .claude/commands/ against harbor tasks in parallel.

Loads command markdown files and passes them as prompts to `claude -p`.
CLAUDE.md is auto-loaded by `claude -p` for project context.

  ┌─────────────────┬─────────────────────────┬───────────────────────────────────────────────────────────┬────────┐   
  │     Action      │      Prompt source      │                     What Claude does                      │ Model  │ 
  ├─────────────────┼─────────────────────────┼───────────────────────────────────────────────────────────┼────────┤   
  │ rebuild-rubrics │ build-rubric.md         │ gh api to fetch actual config files at base commit,       │ opus   │ 
  │                 │                         │ extract rules verbatim, write rubric.yaml                 │        │ 
  ├─────────────────┼─────────────────────────┼───────────────────────────────────────────────────────────┼────────┤   
  │ audit-tests     │ audit-tests.md          │ Read test.sh, try to game it, check narrow-test problems, │ opus   │ 
  │                 │                         │  rewrite if needed                                        │        │   
  ├─────────────────┼─────────────────────────┼───────────────────────────────────────────────────────────┼────────┤ 
  │ validate        │ validate-task.md        │ Check instruction quality, test↔instruction alignment,    │ opus │   
  │                 │                         │ Dockerfile correctness                                    │        │   
  ├─────────────────┼─────────────────────────┼───────────────────────────────────────────────────────────┼────────┤ 
  │ solve           │ reads instruction.md    │ Read the bug description, fix the code, run tests         │ opus │   
  │                 │ directly                │                                                           │        │   
  └─────────────────┴─────────────────────────┴───────────────────────────────────────────────────────────┴────────┘
Usage:
    python scripts/run_pipeline.py rebuild-rubrics --model opus --workers 4
    python scripts/run_pipeline.py rebuild-rubrics --tasks sglang-lscpu-topology-fix
    python scripts/run_pipeline.py audit-tests --model opus --workers 4
    python scripts/run_pipeline.py solve --model sonnet --workers 8
    python scripts/run_pipeline.py full --workers 4
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

# Action → command file. The command file IS the prompt.
COMMAND_FILES = {
    "rebuild-rubrics": "build-rubric.md",
    "audit-tests": "audit-tests.md",
    "validate": "validate-task.md",
    "scaffold": "scaffold-task.md",
}

DEFAULT_MODELS = {
    "rebuild-rubrics": "opus",
    "audit-tests": "opus",
    "validate": "opus",
    "scaffold": "opus",
    "solve": "opus",
}

DEFAULT_BUDGETS = {
    "rebuild-rubrics": 2.0,
    "audit-tests": 3.0,
    "validate": 2.0,
    "scaffold": 5.0,
    "solve": 5.0,
}


def load_command(action: str, task: str) -> str:
    """Load a .claude/commands/ file and substitute $ARGUMENTS with the task name.

    claude -p can't execute slash commands directly, so we load the
    command file, replace $ARGUMENTS, and pass the full text as the prompt.
    """
    cmd_file = COMMANDS_DIR / COMMAND_FILES[action]
    if not cmd_file.exists():
        raise FileNotFoundError(f"Command file not found: {cmd_file}")
    prompt = cmd_file.read_text()
    return prompt.replace("$ARGUMENTS", task)


def get_tasks(filter_tasks: str | None = None) -> list[str]:
    """List all task directories, optionally filtered."""
    all_tasks = sorted(
        d.name for d in HARBOR_TASKS.iterdir()
        if d.is_dir() and (d / "task.toml").exists()
    )
    if filter_tasks:
        names = set(filter_tasks.split(","))
        return [t for t in all_tasks if t in names]
    return all_tasks


async def run_one(
    task: str,
    prompt: str,
    model: str,
    budget: float,
    timeout: int,
    sem: asyncio.Semaphore,
    log_dir: Path,
) -> dict:
    """Run claude -p with a prompt against one task."""
    log_file = log_dir / f"{task}.json"
    result = {
        "task": task, "model": model,
        "status": "pending", "started_at": datetime.now().isoformat(),
    }

    async with sem:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] START {task}")

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
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] TIMEOUT {task}")
                json.dump(result, open(log_file, "w"), indent=2)
                return result

            stdout_text = stdout.decode("utf-8", errors="replace")
            stderr_text = stderr.decode("utf-8", errors="replace")

            # Parse JSON output from claude
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
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] BUDGET {task}")
            elif proc.returncode == 0:
                result["status"] = "success"
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] OK {task}")
            else:
                result["status"] = "error"
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] FAIL {task} (exit {proc.returncode})")

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)[:500]
            print(f"  [{datetime.now().strftime('%H:%M:%S')}] ERROR {task}: {e}")

        result["finished_at"] = datetime.now().isoformat()
        json.dump(result, open(log_file, "w"), indent=2)
        return result


async def main():
    parser = argparse.ArgumentParser(description="Run .claude/commands/ against harbor tasks")
    parser.add_argument("action", choices=list(COMMAND_FILES) + ["solve", "full"])
    parser.add_argument("--tasks", help="Comma-separated task names (default: all)")
    parser.add_argument("--model", help="Override model (opus/sonnet/haiku)")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--budget", type=float, help="Max USD per task")
    parser.add_argument("--timeout", type=int, default=600, help="Seconds per task")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    tasks = get_tasks(args.tasks)
    print(f"Tasks: {len(tasks)}")

    if args.action == "full":
        # scaffold-task already includes rubric building, so full = audit + validate
        for action in ["audit-tests", "validate"]:
            print(f"\n{'='*60}\n  Phase: {action}\n{'='*60}\n")
            model = args.model or DEFAULT_MODELS[action]
            budget = args.budget or DEFAULT_BUDGETS[action]
            log_dir = LOG_DIR / f"{action}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            log_dir.mkdir(parents=True, exist_ok=True)
            sem = asyncio.Semaphore(args.workers)

            prompts = {t: load_command(action, t) for t in tasks}
            coros = [
                run_one(t, prompts[t], model, budget, args.timeout, sem, log_dir)
                for t in tasks
            ]
            results = await asyncio.gather(*coros)
            ok = sum(1 for r in results if r["status"] == "success")
            print(f"\n  {action}: {ok}/{len(results)} succeeded\n")
        return

    model = args.model or DEFAULT_MODELS[args.action]
    budget = args.budget or DEFAULT_BUDGETS[args.action]
    log_dir = LOG_DIR / f"{args.action}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_dir.mkdir(parents=True, exist_ok=True)

    if args.action == "solve":
        # Solve uses instruction.md as the prompt — no command file
        prompts = {}
        for t in tasks:
            inst = HARBOR_TASKS / t / "instruction.md"
            prompts[t] = (
                f"You are solving a coding task. Read and fix the bug:\n\n"
                f"{inst.read_text() if inst.exists() else 'No instruction.md found.'}"
            )
    else:
        prompts = {t: load_command(args.action, t) for t in tasks}

    if args.dry_run:
        for t in tasks:
            print(f"  {t}: {len(prompts[t])} chars, model={model}, budget=${budget}")
        return

    sem = asyncio.Semaphore(args.workers)
    coros = [
        run_one(t, prompts[t], model, budget, args.timeout, sem, log_dir)
        for t in tasks
    ]

    start = time.time()
    results = await asyncio.gather(*coros)
    elapsed = time.time() - start

    by_status: dict[str, int] = {}
    for r in results:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1

    print(f"\n{'='*60}")
    print(f"  Done in {elapsed:.0f}s")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")
    print(f"{'='*60}")

    summary_file = log_dir / "_summary.json"
    json.dump({
        "action": args.action, "model": model,
        "tasks": len(tasks), "elapsed_sec": elapsed,
        "by_status": by_status, "results": results,
    }, open(summary_file, "w"), indent=2)
    print(f"  Logs: {log_dir}")


if __name__ == "__main__":
    asyncio.run(main())
