#!/usr/bin/env python3
"""Pipeline orchestrator: run actions against harbor tasks in parallel via claude -p.

Supports two modes:
  1. Task-based: run actions against existing task directories
  2. PR-based: scaffold new tasks from scouted PR JSONL files

Usage:
    # Task-based actions
    python -m taskforge.pipeline scaffold --tasks sglang-lscpu-topology-fix
    python -m taskforge.pipeline scaffold --workers 4 --model opus
    python -m taskforge.pipeline validate --workers 8
    python -m taskforge.pipeline solve --model sonnet --workers 8
    python -m taskforge.pipeline full --workers 4

    # PR-based scaffolding (reads JSONL of scouted PRs)
    python -m taskforge.pipeline scaffold-from-prs --input scouted_prs.jsonl --workers 4
    python -m taskforge.pipeline scaffold-from-prs --input scouted_agentmd_prs.jsonl --agentmd --workers 4
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

ROOT = Path(__file__).parent.parent
HARBOR_TASKS = ROOT / "harbor_tasks"
HARBOR_AGENTMD = ROOT / "harbor_tasks_agentmd_edits"
COMMANDS_DIR = ROOT / ".claude" / "commands"
PROMPTS_DIR = ROOT / "taskforge" / "prompts"
TEMPLATE_DIR = ROOT / "taskforge" / "templates" / "task_template"
LOG_DIR = ROOT / "pipeline_logs"

# Action → prompt file (check taskforge/prompts/ first, then .claude/commands/)
PROMPT_FILES = {
    "scaffold": "scaffold.md",
    "scaffold-agentmd": "scaffold_agentmd.md",
    "enrich-config-edit": "enrich_config_edit.md",
    "improve-tests": "improve_tests.md",
    "validate": "validate.md",
    "remake": "remake.md",
    "enrich-rubric": "enrich-rubric.md",
}
COMMAND_FILES = {
    "scaffold": "scaffold-task.md",
    "validate": "validate-task.md",
}

DEFAULT_MODELS = {
    "scaffold": "opus",
    "scaffold-agentmd": "opus",
    "scaffold-from-prs": "opus",
    "enrich-config-edit": "sonnet",
    "improve-tests": "opus",
    "validate": "opus",
    "remake": "opus",
    "solve": "opus",
    "enrich-rubric": "sonnet",
}

DEFAULT_BUDGETS = {
    "scaffold": 5.0,
    "scaffold-agentmd": 6.0,
    "scaffold-from-prs": 5.0,
    "enrich-config-edit": 2.0,
    "improve-tests": 10.0,
    "validate": 2.0,
    "remake": 5.0,
    "solve": 5.0,
    "enrich-rubric": 1.0,
}


def load_command(action: str, task: str) -> str:
    """Load a prompt file and substitute $ARGUMENTS with the task name.

    Checks taskforge/prompts/ first, then .claude/commands/.
    """
    if action in PROMPT_FILES:
        prompt_file = PROMPTS_DIR / PROMPT_FILES[action]
        if prompt_file.exists():
            return prompt_file.read_text().replace("$ARGUMENTS", task)

    if action in COMMAND_FILES:
        cmd_file = COMMANDS_DIR / COMMAND_FILES[action]
        if cmd_file.exists():
            return cmd_file.read_text().replace("$ARGUMENTS", task)

    raise FileNotFoundError(f"No prompt found for action: {action}")


def get_tasks(filter_tasks: str | None = None, task_dir: Path | None = None) -> list[str]:
    """List all task directories, optionally filtered."""
    base = task_dir or HARBOR_TASKS
    if not base.exists():
        return []
    all_tasks = sorted(
        d.name for d in base.iterdir()
        if d.is_dir() and (d / "task.toml").exists()
    )
    if filter_tasks:
        names = set(filter_tasks.split(","))
        return [t for t in all_tasks if t in names]
    return all_tasks


# ---------------------------------------------------------------------------
# PR-based scaffolding helpers
# ---------------------------------------------------------------------------

def slugify(repo: str, title: str) -> str:
    """Generate a task name slug from repo + PR title."""
    repo_short = repo.split("/")[-1].lower()
    clean = re.sub(r"[^a-z0-9\s]", "", title.lower())
    words = clean.split()[:5]
    slug = "-".join(words)
    if not slug:
        slug = "unnamed"
    return f"{repo_short}-{slug}"[:60]


def get_existing_prs(*task_dirs: Path) -> set[tuple[str, int]]:
    """Get (repo, pr_number) pairs for already-scaffolded tasks."""
    existing: set[tuple[str, int]] = set()
    for task_dir in task_dirs:
        if not task_dir.exists():
            continue
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


# ---------------------------------------------------------------------------
# Core runner
# ---------------------------------------------------------------------------

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
    # Record actual backend model (e.g., glm-5.1 when routed via Z.AI)
    backend_model = os.environ.get("ANTHROPIC_DEFAULT_OPUS_MODEL", "") if model == "opus" else \
                    os.environ.get("ANTHROPIC_DEFAULT_SONNET_MODEL", "") if model == "sonnet" else \
                    os.environ.get("ANTHROPIC_DEFAULT_HAIKU_MODEL", "")
    result = {
        "task": task, "model": model,
        "backend_model": backend_model or model,
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
                for line in stdout_text.split("\n"):
                    if "SKIP:" in line:
                        result["skip_reason"] = line.strip()[:200]
                        break
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] SKIP {task}: {result.get('skip_reason', '')[:60]}")
            elif "Exceeded USD budget" in stdout_text or "Exceeded USD budget" in stderr_text:
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
        log_file.write_text(json.dumps(result, indent=2))
        return result


# ---------------------------------------------------------------------------
# Batch run + summary
# ---------------------------------------------------------------------------

async def run_batch(
    items: list[tuple[str, str]],  # (task_label, prompt)
    model: str,
    budget: float,
    timeout: int,
    workers: int,
    log_dir: Path,
    dry_run: bool = False,
) -> list[dict]:
    """Run claude -p in parallel for a batch of (label, prompt) pairs."""
    log_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        for label, prompt in items[:20]:
            print(f"  {label}: {len(prompt)} chars, model={model}, budget=${budget}")
        if len(items) > 20:
            print(f"  ... and {len(items) - 20} more")
        return []

    sem = asyncio.Semaphore(workers)
    coros = [
        run_one(label, prompt, model, budget, timeout, sem, log_dir)
        for label, prompt in items
    ]

    start = time.time()
    results = await asyncio.gather(*coros)
    elapsed = time.time() - start

    by_status: dict[str, int] = {}
    for r in results:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1

    print(f"\n{'='*60}")
    print(f"  Done in {elapsed:.0f}s ({elapsed/60:.1f}m)")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")
    print(f"{'='*60}")

    summary_file = log_dir / "_summary.json"
    json.dump({
        "model": model, "tasks": len(results),
        "elapsed_sec": elapsed, "by_status": by_status,
        "results": results,
    }, open(summary_file, "w"), indent=2)
    print(f"  Logs: {log_dir}")

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

async def main():
    parser = argparse.ArgumentParser(description="Pipeline orchestrator for harbor tasks")
    all_actions = sorted(set(PROMPT_FILES) | set(COMMAND_FILES) | {"solve", "full", "scaffold-from-prs"})
    parser.add_argument("action", choices=all_actions)
    parser.add_argument("--tasks", help="Comma-separated task names (default: all)")
    parser.add_argument("--task-dir", help="Task directory (default: harbor_tasks)")
    parser.add_argument("--model", help="Override model (opus/sonnet/haiku)")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--budget", type=float, help="Max USD per task")
    parser.add_argument("--timeout", type=int, default=600, help="Seconds per task")
    parser.add_argument("--dry-run", action="store_true")
    # scaffold-from-prs specific
    parser.add_argument("--input", help="Input JSONL file for scaffold-from-prs")
    parser.add_argument("--agentmd", action="store_true", help="Use agentmd scaffold mode")
    parser.add_argument("--offset", type=int, default=0, help="Skip first N PRs")
    parser.add_argument("--limit", type=int, help="Max PRs to scaffold")
    args = parser.parse_args()

    if args.action == "scaffold-from-prs":
        await _cmd_scaffold_from_prs(args)
        return

    task_dir = ROOT / args.task_dir if args.task_dir else HARBOR_TASKS
    tasks = get_tasks(args.tasks, task_dir=task_dir)
    print(f"Tasks: {len(tasks)} (from {task_dir.name})")

    if args.action == "full":
        for action in ["scaffold", "validate"]:
            print(f"\n{'='*60}\n  Phase: {action}\n{'='*60}\n")
            model = args.model or DEFAULT_MODELS[action]
            budget = args.budget or DEFAULT_BUDGETS[action]
            log_dir = LOG_DIR / f"{action}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            prompts = {t: load_command(action, t) for t in tasks}
            items = [(t, prompts[t]) for t in tasks]
            await run_batch(items, model, budget, args.timeout, args.workers, log_dir, args.dry_run)
        return

    model = args.model or DEFAULT_MODELS[args.action]
    budget = args.budget or DEFAULT_BUDGETS[args.action]
    log_dir = LOG_DIR / f"{args.action}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if args.action == "solve":
        items = []
        for t in tasks:
            inst = task_dir / t / "instruction.md"
            prompt = (
                f"You are solving a coding task. Read and fix the bug:\n\n"
                f"{inst.read_text() if inst.exists() else 'No instruction.md found.'}"
            )
            items.append((t, prompt))
    else:
        items = [(t, load_command(args.action, t)) for t in tasks]

    await run_batch(items, model, budget, args.timeout, args.workers, log_dir, args.dry_run)


async def _cmd_scaffold_from_prs(args: argparse.Namespace) -> None:
    """Scaffold new tasks from a JSONL of scouted PRs."""
    input_file = args.input or ("scouted_agentmd_prs.jsonl" if args.agentmd else "scouted_prs.jsonl")
    input_path = ROOT / input_file
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        sys.exit(1)

    with open(input_path) as f:
        all_prs = [json.loads(line) for line in f if line.strip()]

    # Apply offset and limit
    prs = all_prs[args.offset:]
    if args.limit:
        prs = prs[:args.limit]

    # Dedup against existing tasks
    existing = get_existing_prs(HARBOR_TASKS, HARBOR_AGENTMD)
    prs = [p for p in prs if (p["repo"], p["pr_number"]) not in existing]

    print(f"Input: {len(all_prs)} PRs total")
    print(f"After offset/limit/dedup: {len(prs)} PRs to scaffold")

    model = args.model or DEFAULT_MODELS["scaffold-from-prs"]
    budget = args.budget or (6.0 if args.agentmd else 5.0)
    timeout = args.timeout or 900

    if args.agentmd:
        # AgentMD mode: generate slugs, copy template, use agentmd prompt
        task_dir = HARBOR_AGENTMD
        task_dir.mkdir(exist_ok=True)
        prompt_file = PROMPTS_DIR / "scaffold_agentmd.md"
        if not prompt_file.exists():
            prompt_file = COMMANDS_DIR / "scaffold-task.md"
        prompt_template = prompt_file.read_text()

        items = []
        seen_names: set[str] = set()
        for pr in prs:
            name = slugify(pr["repo"], pr["title"])
            if name in seen_names:
                name = f"{name}-{pr['pr_number']}"
            seen_names.add(name)

            # Copy template if task dir doesn't exist
            task_path = task_dir / name
            if not task_path.exists() and not args.dry_run:
                shutil.copytree(TEMPLATE_DIR, task_path)

            pr_ref = f"{pr['repo']}#{pr['pr_number']}"
            prompt = prompt_template.replace("$ARGUMENTS", pr_ref)
            items.append((name, prompt))
    else:
        # Standard mode: use scaffold command, PR ref as argument
        cmd_file = COMMANDS_DIR / "scaffold-task.md"
        prompt_template = cmd_file.read_text()

        items = []
        for pr in prs:
            pr_ref = f"{pr['repo']}#{pr['pr_number']}"
            prompt = prompt_template.replace("$ARGUMENTS", pr_ref)
            items.append((pr_ref, prompt))

    log_dir = LOG_DIR / f"scaffold_{'agentmd_' if args.agentmd else ''}{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print(f"Workers: {args.workers}, Model: {model}, Budget: ${budget}")
    await run_batch(items, model, budget, timeout, args.workers, log_dir, args.dry_run)


if __name__ == "__main__":
    asyncio.run(main())
