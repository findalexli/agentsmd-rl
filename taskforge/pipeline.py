#!/usr/bin/env python3
"""Pipeline orchestrator: run actions against harbor tasks in parallel.

Without ``--pool``, uses a single backend configured via env vars (original behavior).
With ``--pool``, discovers all backends from .env and rotates on 429:
  - Single-shot actions (improve-tests): direct httpx API, ~5 MB/worker
  - Multi-turn actions (scaffold, validate): claude -p subprocess, ~300 MB/worker

Usage:
    python -m taskforge.pipeline improve-tests --workers 6
    python -m taskforge.pipeline improve-tests --pool --workers 30
    python -m taskforge.pipeline scaffold-from-prs --input prs.jsonl --agentmd --pool
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





def load_command(action: str, task: str, task_dir: Path | None = None) -> str:
    """Load a prompt file and substitute $ARGUMENTS with the task name.

    Checks taskforge/prompts/ first, then .claude/commands/.
    Also substitutes $TASK_DIR with the task directory name.
    """
    resolved_dir = (task_dir or HARBOR_TASKS).name

    if action in PROMPT_FILES:
        prompt_file = PROMPTS_DIR / PROMPT_FILES[action]
        if prompt_file.exists():
            return prompt_file.read_text().replace("$ARGUMENTS", task).replace("$TASK_DIR", resolved_dir)

    if action in COMMAND_FILES:
        cmd_file = COMMANDS_DIR / COMMAND_FILES[action]
        if cmd_file.exists():
            return cmd_file.read_text().replace("$ARGUMENTS", task).replace("$TASK_DIR", resolved_dir)

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
    pool: BackendPool | None = None,
) -> dict:
    """Run claude -p with a prompt against one task.

    When *pool* is provided, acquires a backend slot and injects per-subprocess
    env vars.  On 429, retries with the next available backend.
    """
    log_file = log_dir / f"{task}.json"
    ts = lambda: datetime.now().strftime("%H:%M:%S")

    result: dict = {
        "task": task, "model": model,
        "status": "pending", "started_at": datetime.now().isoformat(),
    }

    async with sem:
        print(f"  [{ts()}] START {task}")
        max_attempts = 3 if pool else 1

        for attempt in range(1, max_attempts + 1):
            try:
                result["attempt"] = attempt
                await _exec_subprocess(task, prompt, model, budget, timeout, result, pool)
            except Exception as e:
                result["status"] = "error"
                result["error"] = str(e)[:500]
                print(f"  [{ts()}] ERROR {task}: {e}")

            # Report to pool and maybe retry on 429
            backend = result.pop("_backend", None)
            if pool and backend:
                combined = (result.get("result", "") or "") + (result.get("stderr_tail", "") or "")
                is_429 = "429" in combined or "Rate limit" in combined
                if result["status"] == "error" and is_429:
                    pool.report_429(backend)
                    if attempt < max_attempts:
                        continue
                elif result["status"] == "success":
                    pool.report_success(backend)

            break
        result["finished_at"] = datetime.now().isoformat()
        log_file.write_text(json.dumps(result, indent=2))
        return result


async def _exec_subprocess(
    task: str, prompt: str, model: str, budget: float,
    timeout: int, result: dict, pool: BackendPool | None,
) -> None:
    """Spawn ``claude -p`` and populate *result* dict in-place."""
    ts = lambda: datetime.now().strftime("%H:%M:%S")

    # Build env: merge pool backend env on top of os.environ
    env = dict(os.environ)
    if pool:
        async with pool.acquire() as backend:
            env.update(backend.subprocess_env())
            result["_backend"] = backend  # runtime ref, stripped before JSON
            result["backend_name"] = backend.name
            result["backend_model"] = backend.resolve_model(model)
            return await _run_claude(task, prompt, model, budget, timeout, env, result, ts)
    else:
        backend_model = os.environ.get("ANTHROPIC_DEFAULT_OPUS_MODEL", "") if model == "opus" else \
                        os.environ.get("ANTHROPIC_DEFAULT_SONNET_MODEL", "") if model == "sonnet" else \
                        os.environ.get("ANTHROPIC_DEFAULT_HAIKU_MODEL", "")
        result["backend_model"] = backend_model or model
        return await _run_claude(task, prompt, model, budget, timeout, env, result, ts)


async def _run_claude(
    task: str, prompt: str, model: str, budget: float,
    timeout: int, env: dict, result: dict, ts,
) -> None:
    """The actual subprocess spawn + output parsing."""
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
        env=env,
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(prompt.encode()), timeout=timeout,
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        result["status"] = "timeout"
        print(f"  [{ts()}] TIMEOUT {task}")
        return

    stdout_text = stdout.decode("utf-8", errors="replace")
    stderr_text = stderr.decode("utf-8", errors="replace")

    # Parse JSON output
    try:
        output = json.loads(stdout_text)
        if isinstance(output, dict):
            result["result"] = output.get("result", "")[:3000]
            result["session_id"] = output.get("session_id")
            result["usage"] = output.get("usage")
        elif isinstance(output, list) and output:
            last = output[-1] if isinstance(output[-1], dict) else {}
            result["result"] = str(last.get("content", last.get("result", "")))[:3000]
        else:
            result["stdout_tail"] = stdout_text[-2000:]
    except json.JSONDecodeError:
        result["stdout_tail"] = stdout_text[-2000:]

    result["exit_code"] = proc.returncode
    if stderr_text:
        result["stderr_tail"] = stderr_text[-500:]

    # Classify status
    if "SKIP:" in stdout_text:
        result["status"] = "skipped"
        for line in stdout_text.split("\n"):
            if "SKIP:" in line:
                result["skip_reason"] = line.strip()[:200]
                break
        print(f"  [{ts()}] SKIP {task}: {result.get('skip_reason', '')[:60]}")
    elif "Exceeded USD budget" in stdout_text or "Exceeded USD budget" in stderr_text:
        result["status"] = "budget_exceeded"
        print(f"  [{ts()}] BUDGET {task}")
    elif proc.returncode == 0:
        result["status"] = "success"
        print(f"  [{ts()}] OK {task}")
    else:
        result["status"] = "error"
        print(f"  [{ts()}] FAIL {task} (exit {proc.returncode})")


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
    pool: BackendPool | None = None,
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
        run_one(label, prompt, model, budget, timeout, sem, log_dir, pool=pool)
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
    if pool:
        print(f"  Backends: {pool.stats()}")
    print(f"{'='*60}")

    # Scrub non-serializable Backend objects before writing JSON
    clean_results = []
    for r in results:
        clean = {k: v for k, v in r.items() if not k.startswith("_")}
        clean_results.append(clean)

    summary_file = log_dir / "_summary.json"
    json.dump({
        "model": model, "tasks": len(results),
        "elapsed_sec": elapsed, "by_status": by_status,
        "results": clean_results,
    }, open(summary_file, "w"), indent=2)
    print(f"  Logs: {log_dir}")

    return results


# ---------------------------------------------------------------------------
# Direct API mode — single-shot, no subprocess
# ---------------------------------------------------------------------------

async def run_direct_batch(
    items: list[tuple[str, str]],  # (task_label, prompt)
    model: str,
    workers: int,
    log_dir: Path,
    pool: BackendPool,
    task_dir: Path,
    dry_run: bool = False,
) -> list[dict]:
    """Run improve-tests via direct API calls (no subprocess).

    Pre-loads all task files into the prompt, sends a single API call,
    parses code blocks from the response, and writes the output files.
    """
    from taskforge.backends import call_api, parse_file_blocks

    log_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        for label, _ in items[:20]:
            print(f"  {label}: direct-api, model={model}")
        return []

    import httpx as _httpx
    http = _httpx.AsyncClient(timeout=_httpx.Timeout(300, connect=15))
    sem = asyncio.Semaphore(workers)

    async def _one(task: str, system_prompt: str) -> dict:
        result: dict = {
            "task": task, "model": model, "mode": "direct-api",
            "status": "pending", "started_at": datetime.now().isoformat(),
        }
        ts = lambda: datetime.now().strftime("%H:%M:%S")

        async with sem:
            print(f"  [{ts()}] START {task}")
            try:
                user_msg = await _build_direct_prompt(task, task_dir)
                text, usage, backend_name = await call_api(
                    pool, messages=[{"role": "user", "content": user_msg}],
                    system=system_prompt, model=model, http=http,
                )
                result["backend_name"] = backend_name
                result["usage"] = usage

                # Parse and write output files
                blocks = parse_file_blocks(text)
                wrote = _write_parsed_blocks(blocks, task_dir / task)
                result["wrote"] = wrote

                if "tests/test_outputs.py" in wrote or "test_outputs.py" in wrote:
                    result["status"] = "success"
                    print(f"  [{ts()}] OK {task} via {backend_name} ({len(wrote)} files)")
                else:
                    result["status"] = "error"
                    result["error"] = f"No test_outputs.py in response (got: {list(blocks.keys())})"
                    result["response_tail"] = text[-3000:]
                    print(f"  [{ts()}] FAIL {task}: no test_outputs.py parsed (blocks: {list(blocks.keys())})")

            except Exception as e:
                result["status"] = "error"
                result["error"] = str(e)[:500]
                print(f"  [{ts()}] ERROR {task}: {e}")

            result["finished_at"] = datetime.now().isoformat()
            (log_dir / f"{task}.json").write_text(json.dumps(result, indent=2))
            return result

    start = time.time()
    coros = [_one(task, prompt) for task, prompt in items]
    results = await asyncio.gather(*coros)
    elapsed = time.time() - start
    await http.aclose()

    by_status: dict[str, int] = {}
    for r in results:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1

    print(f"\n{'='*60}")
    print(f"  Done in {elapsed:.0f}s ({elapsed/60:.1f}m)")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")
    print(f"  Backends: {pool.stats()}")
    print(f"{'='*60}")

    summary_file = log_dir / "_summary.json"
    json.dump({
        "model": model, "mode": "direct-api", "tasks": len(results),
        "elapsed_sec": elapsed, "by_status": by_status, "results": results,
    }, open(summary_file, "w"), indent=2)
    print(f"  Logs: {log_dir}")

    return results


async def _build_direct_prompt(task: str, task_dir: Path) -> str:
    """Pre-load all task files + PR diff into a single user message."""
    td = task_dir / task
    parts = [f"# Task: {task}\n\n## Task Files\n"]

    for fname in [
        "instruction.md", "tests/test_outputs.py", "solution/solve.sh",
        "eval_manifest.yaml", "task.toml", "environment/Dockerfile",
    ]:
        fpath = td / fname
        if fpath.exists():
            content = fpath.read_text()
            parts.append(f"### {fname}\n```\n{content}\n```\n")

    # Pre-fetch PR diff
    toml_path = td / "task.toml"
    if toml_path.exists():
        toml_text = toml_path.read_text()
        repo = pr = None
        for line in toml_text.splitlines():
            if line.startswith("source_repo"):
                repo = line.split("=", 1)[1].strip().strip('"')
            if line.startswith("source_pr"):
                try:
                    pr = line.split("=", 1)[1].strip()
                except (ValueError, IndexError):
                    pass
        if repo and pr:
            proc = await asyncio.create_subprocess_exec(
                "gh", "pr", "diff", str(pr), "--repo", repo,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
            diff = stdout.decode("utf-8", errors="replace")[:50000]
            if diff.strip():
                parts.append(f"### PR Diff ({repo}#{pr})\n```diff\n{diff}\n```\n")

    parts.append("""
## Output Format

Return your rewritten files wrapped in XML tags:

<file path="tests/test_outputs.py">
... your rewritten test file ...
</file>

<file path="eval_manifest.yaml">
... your rewritten manifest ...
</file>
""")
    return "\n".join(parts)


def _write_parsed_blocks(blocks: dict[str, str], task_path: Path) -> list[str]:
    """Write parsed file blocks to disk. Returns list of written paths."""
    import ast
    wrote: list[str] = []
    for name, content in blocks.items():
        # Normalize: "tests/test_outputs.py" or just "test_outputs.py"
        if name in ("test_outputs.py", "tests/test_outputs.py"):
            # Syntax-validate before writing
            try:
                ast.parse(content)
            except SyntaxError as e:
                print(f"    Syntax error in {name}: {e}")
                continue
            out = task_path / "tests" / "test_outputs.py"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(content)
            wrote.append(name)
        elif name in ("eval_manifest.yaml",):
            out = task_path / "eval_manifest.yaml"
            out.write_text(content)
            wrote.append(name)
    return wrote


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
    parser.add_argument("--pool", action="store_true",
                        help="Use multi-backend pool with auto-fallback on 429")
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
            prompts = {t: load_command(action, t, task_dir) for t in tasks}
            items = [(t, prompts[t]) for t in tasks]
            await run_batch(items, model, budget, args.timeout, args.workers, log_dir, args.dry_run)
        return

    model = args.model or DEFAULT_MODELS[args.action]
    budget = args.budget or DEFAULT_BUDGETS[args.action]
    log_dir = LOG_DIR / f"{args.action}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Resolve backend pool
    pool = None
    if args.pool:
        from taskforge.backends import BackendPool, backends_from_env
        backends = backends_from_env()
        if not backends:
            print("No backends found in .env / environment")
            sys.exit(1)
        pool = BackendPool(backends)
        print(f"Backend pool: {pool.names}")

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
        items = [(t, load_command(args.action, t, task_dir)) for t in tasks]

    await run_batch(
        items, model, budget, args.timeout, args.workers, log_dir, args.dry_run, pool=pool,
    )


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
