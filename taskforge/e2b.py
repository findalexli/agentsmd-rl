"""E2B sandbox validation for Harbor tasks.

Builds E2B templates from Dockerfiles, then runs each task's test suite
in parallel: base test (nop, expect reward=0) then gold test (solve.sh
applied, expect reward=1).

Usage:
    python -m taskforge.e2b                              # all tasks, concurrency 10
    python -m taskforge.e2b --concurrency 20             # faster
    python -m taskforge.e2b --filter "gradio-*"          # glob filter
    python -m taskforge.e2b --resume                     # skip already-validated
"""

from __future__ import annotations

import argparse
import asyncio
import fnmatch
import json
import logging
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from hashlib import sha256
from pathlib import Path

from e2b import AsyncSandbox, AsyncTemplate, Template
from e2b.sandbox.commands.command_handle import CommandExitException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
HARBOR_TASKS_DIR = ROOT / "markdown_following"
RESULTS_FILE = ROOT / "pipeline_logs" / "e2b_validate_results.json"


@dataclass
class TaskResult:
    task_name: str
    template_name: str = ""
    template_status: str = ""  # "cached", "built", "error"
    template_time: float = 0.0
    sandbox_id: str = ""
    sandbox_create_time: float = 0.0
    base_exit_code: int = -1
    base_reward: float = -1.0
    base_test_time: float = 0.0
    solve_exit_code: int = -1
    solve_time: float = 0.0
    gold_exit_code: int = -1
    gold_reward: float = -1.0
    gold_test_time: float = 0.0
    total_time: float = 0.0
    valid: bool = False  # base_reward=0 and gold_reward=1
    error: str = ""
    rate_limit_retries: int = 0


def dir_hash(env_dir: Path, length: int = 12) -> str:
    dockerfile = env_dir / "Dockerfile"
    if dockerfile.exists():
        return sha256(dockerfile.read_bytes()).hexdigest()[:length]
    return sha256(str(env_dir).encode()).hexdigest()[:length]


def template_name_for(task_name: str, env_dir: Path) -> str:
    dh = dir_hash(env_dir)
    return f"tinker-{task_name}-{dh}".replace(".", "-")


async def retry_on_429(fn, max_retries: int = 5) -> tuple[any, int]:
    """Call async fn, retry on rate-limit. Returns (result, retry_count)."""
    retries = 0
    for attempt in range(max_retries):
        try:
            return await fn(), retries
        except Exception as e:
            err = str(e).lower()
            if "429" in err or "rate limit" in err:
                retries += 1
                wait = 20 * (attempt + 1)
                logger.warning("Rate limited (attempt %d), waiting %ds", attempt + 1, wait)
                await asyncio.sleep(wait)
            else:
                raise
    raise RuntimeError(f"Failed after {max_retries} rate-limit retries")


async def run_cmd(sandbox: AsyncSandbox, cmd: str, timeout: int = 120) -> tuple[int, str, str]:
    try:
        handle = await sandbox.commands.run(cmd, background=True, user="root", timeout=timeout)
        try:
            result = await handle.wait()
        except CommandExitException as e:
            result = e
        return result.exit_code, result.stdout or "", result.stderr or ""
    except Exception as e:
        return -1, "", str(e)


async def validate_one(
    task_name: str,
    build_sem: asyncio.Semaphore,
    run_sem: asyncio.Semaphore,
) -> TaskResult:
    """Full validation for one task."""
    r = TaskResult(task_name=task_name)
    t_start = time.monotonic()

    task_dir = HARBOR_TASKS_DIR / task_name
    env_dir = task_dir / "environment"
    test_sh = task_dir / "tests" / "test.sh"
    solve_sh = task_dir / "solution" / "solve.sh"
    test_outputs_py = task_dir / "tests" / "test_outputs.py"

    for path, label in [(task_dir, "task_dir"), (env_dir / "Dockerfile", "Dockerfile"),
                        (test_sh, "test.sh"), (solve_sh, "solve.sh")]:
        if not path.exists():
            r.error = f"Missing {label}: {path}"
            r.total_time = time.monotonic() - t_start
            return r

    tpl_name = template_name_for(task_name, env_dir)
    r.template_name = tpl_name

    # --- Phase 1: ensure template exists (throttled) ---
    async with build_sem:
        t0 = time.monotonic()
        try:
            (exists, retries) = await retry_on_429(lambda: AsyncTemplate.alias_exists(tpl_name))
            r.rate_limit_retries += retries
        except Exception as e:
            r.error = f"Template check: {e}"
            r.total_time = time.monotonic() - t_start
            return r

        if exists:
            r.template_status = "cached"
            r.template_time = round(time.monotonic() - t0, 2)
        else:
            try:
                dockerfile_path = env_dir / "Dockerfile"
                tpl = Template().from_dockerfile(dockerfile_content_or_path=str(dockerfile_path))

                async def _build():
                    await AsyncTemplate.build(
                        template=tpl, alias=tpl_name,
                        cpu_count=2, memory_mb=1024,
                    )

                _, retries = await retry_on_429(_build)
                r.rate_limit_retries += retries
                r.template_status = "built"
                r.template_time = round(time.monotonic() - t0, 2)
                logger.info("[%s] Template built in %.1fs", task_name, r.template_time)
            except Exception as e:
                r.template_status = "error"
                r.error = f"Template build: {e}"
                r.template_time = round(time.monotonic() - t0, 2)
                r.total_time = time.monotonic() - t_start
                return r

    # --- Phase 2: create sandbox + run tests (throttled) ---
    async with run_sem:
        sandbox = None
        try:
            # Create sandbox
            t0 = time.monotonic()
            try:
                (sandbox, retries) = await retry_on_429(
                    lambda: AsyncSandbox.create(template=tpl_name, timeout=600)
                )
                r.rate_limit_retries += retries
            except Exception as e:
                r.error = f"Sandbox create: {e}"
                r.total_time = time.monotonic() - t_start
                return r

            r.sandbox_id = sandbox.sandbox_id
            r.sandbox_create_time = round(time.monotonic() - t0, 2)

            # Setup
            await run_cmd(sandbox, "mkdir -p /logs/verifier /tests && chmod 777 /logs/verifier /tests")
            await sandbox.files.write("/tests/test.sh", test_sh.read_bytes())
            await run_cmd(sandbox, "chmod +x /tests/test.sh")
            if test_outputs_py.exists():
                await sandbox.files.write("/tests/test_outputs.py", test_outputs_py.read_bytes())
            await sandbox.files.write("/tests/solve.sh", solve_sh.read_bytes())
            await run_cmd(sandbox, "chmod +x /tests/solve.sh")

            # Also upload judge_hook.sh if present
            judge_hook = task_dir / "tests" / "judge_hook.sh"
            if judge_hook.exists():
                await sandbox.files.write("/tests/judge_hook.sh", judge_hook.read_bytes())
                await run_cmd(sandbox, "chmod +x /tests/judge_hook.sh")

            # Base test (nop)
            t0 = time.monotonic()
            r.base_exit_code, stdout, stderr = await run_cmd(sandbox, "bash /tests/test.sh", timeout=180)
            r.base_test_time = round(time.monotonic() - t0, 2)
            try:
                data = await sandbox.files.read("/logs/verifier/reward.txt", format="text")
                r.base_reward = float(data.strip())
            except Exception:
                r.base_reward = -1.0

            # Apply gold patch
            t0 = time.monotonic()
            r.solve_exit_code, _, stderr = await run_cmd(sandbox, "bash /tests/solve.sh", timeout=180)
            r.solve_time = round(time.monotonic() - t0, 2)
            if r.solve_exit_code != 0:
                r.error = f"solve.sh exit={r.solve_exit_code}: {stderr[-200:]}"

            # Gold test
            t0 = time.monotonic()
            r.gold_exit_code, stdout, stderr = await run_cmd(sandbox, "bash /tests/test.sh", timeout=180)
            r.gold_test_time = round(time.monotonic() - t0, 2)
            try:
                data = await sandbox.files.read("/logs/verifier/reward.txt", format="text")
                r.gold_reward = float(data.strip())
            except Exception:
                r.gold_reward = -1.0

        except Exception as e:
            r.error = str(e)
        finally:
            if sandbox:
                try:
                    await sandbox.kill()
                except Exception:
                    pass

    r.valid = (r.base_reward == 0.0 and r.gold_reward == 1.0)
    r.total_time = round(time.monotonic() - t_start, 2)
    status = "PASS" if r.valid else "FAIL"
    logger.info("[%s] %s  base=%.1f gold=%.1f  (%.1fs)%s",
                task_name, status, r.base_reward, r.gold_reward, r.total_time,
                f"  err={r.error[:60]}" if r.error else "")
    return r


def load_previous_results(path: Path) -> dict[str, dict]:
    """Load existing results for resume support."""
    if path.exists():
        data = json.loads(path.read_text())
        return {t["task_name"]: t for t in data.get("tasks", [])}
    return {}


def collect_tasks(args) -> list[str]:
    """Collect task names based on CLI args."""
    all_tasks = sorted(
        d.name for d in HARBOR_TASKS_DIR.iterdir()
        if d.is_dir()
        and (d / "environment" / "Dockerfile").exists()
        and (d / "tests" / "test.sh").exists()
        and (d / "solution" / "solve.sh").exists()
    )
    if args.filter:
        all_tasks = [t for t in all_tasks if fnmatch.fnmatch(t, args.filter)]
    if args.tasks:
        all_tasks = all_tasks[:args.tasks]
    return all_tasks


async def run(args):
    if not os.environ.get("E2B_API_KEY"):
        print("E2B_API_KEY not set. Run: set -a && source .env && set +a")
        sys.exit(1)

    tasks = collect_tasks(args)
    print(f"Found {len(tasks)} tasks to validate")

    # Resume support
    previous = {}
    if args.resume:
        previous = load_previous_results(RESULTS_FILE)
        skip_count = sum(1 for t in tasks if t in previous and previous[t].get("valid"))
        print(f"  Resuming: {skip_count} already validated, {len(tasks) - skip_count} remaining")
        tasks = [t for t in tasks if t not in previous or not previous[t].get("valid")]

    if not tasks:
        print("Nothing to validate.")
        return

    print(f"  Concurrency: build={args.build_concurrency}, run={args.concurrency}")
    print()

    build_sem = asyncio.Semaphore(args.build_concurrency)
    run_sem = asyncio.Semaphore(args.concurrency)

    wall_start = time.monotonic()
    results: list[TaskResult] = await asyncio.gather(
        *[validate_one(t, build_sem, run_sem) for t in tasks]
    )
    wall_time = time.monotonic() - wall_start

    # Merge with previous results
    all_results = dict(previous)
    for r in results:
        all_results[r.task_name] = asdict(r)

    # Print summary
    valid = [r for r in results if r.valid]
    invalid = [r for r in results if not r.valid and not r.error]
    errored = [r for r in results if r.error]
    rate_limits = sum(r.rate_limit_retries for r in results)

    print()
    print("=" * 80)
    print(f"  BATCH VALIDATION COMPLETE")
    print(f"  Tasks run:  {len(results)}")
    print(f"  Valid:      {len(valid)}  (base=0, gold=1)")
    print(f"  Invalid:    {len(invalid)}  (wrong scores)")
    print(f"  Errors:     {len(errored)}")
    print(f"  Wall time:  {wall_time:.1f}s")
    print(f"  Throughput: {len(results) / wall_time:.2f} tasks/sec")
    print(f"  Rate limit retries: {rate_limits}")
    print("=" * 80)

    if errored:
        print("\n  ERRORS:")
        for r in errored:
            print(f"    {r.task_name}: {r.error[:80]}")

    if invalid:
        print("\n  INVALID (wrong scores):")
        for r in invalid:
            print(f"    {r.task_name}: base={r.base_reward}, gold={r.gold_reward}")

    # Write results
    output = {
        "run_time": wall_time,
        "total_tasks": len(all_results),
        "valid_count": sum(1 for v in all_results.values() if v.get("valid")),
        "tasks": sorted(all_results.values(), key=lambda x: x.get("task_name", "")),
    }
    RESULTS_FILE.write_text(json.dumps(output, indent=2))
    print(f"\nResults written to {RESULTS_FILE}")


def main():
    parser = argparse.ArgumentParser(description="Batch-validate Harbor tasks via E2B")
    parser.add_argument("--concurrency", type=int, default=10, help="Max concurrent sandbox runs")
    parser.add_argument("--build-concurrency", type=int, default=5, help="Max concurrent template builds")
    parser.add_argument("--tasks", type=int, default=None, help="Limit to first N tasks")
    parser.add_argument("--filter", type=str, default=None, help="Glob filter on task names (e.g. 'gradio-*')")
    parser.add_argument("--task-dir", type=str, default=None, help="Task directory (default: markdown_following)")
    parser.add_argument("--resume", action="store_true", help="Skip tasks already validated in results file")
    args = parser.parse_args()
    if args.task_dir:
        global HARBOR_TASKS_DIR, RESULTS_FILE
        HARBOR_TASKS_DIR = ROOT / args.task_dir
        RESULTS_FILE = ROOT / "pipeline_logs" / f"e2b_validate_{args.task_dir}_results.json"
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
