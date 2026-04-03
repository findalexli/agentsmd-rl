"""Test E2B sandbox building and execution at scale using real harbor tasks.

Measures: template build time, sandbox creation time, test execution time,
solve+test time, and tracks rate limit (429) errors across concurrency levels.

Usage:
    set -a && source .env && set +a && python scripts/test_e2b_scale.py
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path

from e2b import AsyncSandbox, AsyncTemplate, Template

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

HARBOR_TASKS_DIR = Path(__file__).resolve().parent.parent / "harbor_tasks"

# Tasks with E2B templates already built
READY_TASKS = [
    "gradio-dataframe-nan-sort",
    "gradio-button-scale-parameter",
    "gradio-colorpicker-events",
    "gradio-connection-lost-error-handling",
    "gradio-browserstate-pydantic-serialization",
    "ruff-f507-percent-format-nontuple",
    "ruff-ipython-percent-foo-parsing",
    "ruff-ruf050-parenthesize",
    "ruff-up008-lambda-scope",
    "openclaw-discord-reconnect-crash",
    "openclaw-msteams-stream-reset",
    "openclaw-preserve-reply-indentation",
    "openclaw-subagent-tool-resolution",
    "openclaw-telegram-empty-reply-crash",
    "openclaw-telegram-message-split",
    "openclaw-unhandled-stop-reasons",
    "gradio-absolute-path-windows",
    "gradio-custom-component-reload",
    "gradio-duplicate-block-error-reload",
    "gradio-on-triggers-type-hints",
    "gradio-reload-annotated-types",
    "gradio-spaces-reloader-config",
    "gradio-submit-button-example-click",
    "gradio-sync-generator-cancel-valueerror",
    "pytorch-fakeprocessgroup-allgather-uneven",
    "pytorch-inductor-identity-evalf",
    "sglang-benchmark-random-len-fix",
    "sglang-detokenizer-unbound-fix",
    "sglang-flux2-tokenization-length",
    "sglang-lscpu-topology-fix",
]


@dataclass
class TaskResult:
    task_name: str
    template_name: str = ""
    template_exists: bool = False
    build_time: float = 0.0
    sandbox_create_time: float = 0.0
    base_test_time: float = 0.0
    base_score: float = -1.0
    solve_time: float = 0.0
    gold_test_time: float = 0.0
    gold_score: float = -1.0
    total_time: float = 0.0
    error: str = ""
    rate_limit_hits: int = 0


@dataclass
class RunStats:
    concurrency: int
    num_tasks: int
    wall_time: float = 0.0
    total_rate_limit_hits: int = 0
    results: list[TaskResult] = field(default_factory=list)


def _dir_hash(directory: Path, length: int = 12) -> str:
    dockerfile = directory / "Dockerfile"
    if dockerfile.exists():
        return sha256(dockerfile.read_bytes()).hexdigest()[:length]
    return sha256(str(directory).encode()).hexdigest()[:length]


def get_template_name(task_dir: Path) -> str:
    env_dir = task_dir / "environment"
    dir_hash = _dir_hash(env_dir)
    return f"tinker-{task_dir.name}-{dir_hash}".replace(".", "-")


async def retry_on_rate_limit(fn, result: TaskResult, max_retries: int = 5):
    """Call an async function, retrying on 429 / rate-limit errors."""
    for attempt in range(max_retries):
        try:
            return await fn()
        except Exception as e:
            err_str = str(e).lower()
            if "429" in err_str or "rate limit" in err_str:
                result.rate_limit_hits += 1
                wait = 15 * (attempt + 1)
                logger.warning("Rate limited (attempt %d), retrying in %ds: %s", attempt + 1, wait, e)
                await asyncio.sleep(wait)
            else:
                raise
    raise RuntimeError(f"Failed after {max_retries} rate-limit retries")


async def run_task(task_name: str, semaphore: asyncio.Semaphore) -> TaskResult:
    """Run full lifecycle for one task: template check, sandbox create, base test, solve, gold test."""
    result = TaskResult(task_name=task_name)
    task_start = time.monotonic()

    task_dir = HARBOR_TASKS_DIR / task_name
    if not task_dir.is_dir():
        result.error = f"Task directory not found: {task_dir}"
        result.total_time = time.monotonic() - task_start
        return result

    env_dir = task_dir / "environment"
    template_name = get_template_name(task_dir)
    result.template_name = template_name

    test_sh = task_dir / "tests" / "test.sh"
    solve_sh = task_dir / "solution" / "solve.sh"

    if not test_sh.exists():
        result.error = "test.sh not found"
        result.total_time = time.monotonic() - task_start
        return result
    if not solve_sh.exists():
        result.error = "solve.sh not found"
        result.total_time = time.monotonic() - task_start
        return result

    test_content = test_sh.read_text()
    solve_content = solve_sh.read_text()

    async with semaphore:
        sandbox = None
        try:
            # Step 1: Check if template exists, build if not
            t0 = time.monotonic()
            try:
                exists = await retry_on_rate_limit(
                    lambda: AsyncTemplate.alias_exists(template_name), result
                )
                result.template_exists = exists
            except Exception as e:
                result.error = f"Template check failed: {e}"
                result.total_time = time.monotonic() - task_start
                return result

            if not exists:
                logger.info("[%s] Building template %s ...", task_name, template_name)
                dockerfile_path = env_dir / "Dockerfile"
                tpl = Template().from_dockerfile(dockerfile_content_or_path=str(dockerfile_path))

                async def _build():
                    await AsyncTemplate.build(
                        template=tpl, alias=template_name,
                        cpu_count=2, memory_mb=1024,
                    )

                await retry_on_rate_limit(_build, result)
                logger.info("[%s] Template built", task_name)

            result.build_time = time.monotonic() - t0

            # Step 2: Create sandbox from template
            t0 = time.monotonic()

            async def _create_sandbox():
                return await AsyncSandbox.create(template=template_name, timeout=600)

            sandbox = await retry_on_rate_limit(_create_sandbox, result)
            # Ensure /logs/verifier writable
            handle = await sandbox.commands.run(
                "mkdir -p /logs/verifier /tests && chmod 777 /logs/verifier /tests",
                background=True, user="root",
            )
            await handle.wait()
            result.sandbox_create_time = time.monotonic() - t0
            logger.info("[%s] Sandbox created: %s (%.1fs)", task_name, sandbox.sandbox_id, result.sandbox_create_time)

            # Step 3: Copy test.sh and solve.sh into sandbox
            await sandbox.files.write("/tests/test.sh", test_content.encode())
            handle = await sandbox.commands.run("chmod +x /tests/test.sh", background=True, user="root")
            await handle.wait()

            await sandbox.files.write("/tests/solve.sh", solve_content.encode())
            handle = await sandbox.commands.run("chmod +x /tests/solve.sh", background=True, user="root")
            await handle.wait()

            # Also copy judge_hook.sh if it exists (test.sh may source it)
            judge_hook = task_dir / "tests" / "judge_hook.sh"
            if judge_hook.exists():
                await sandbox.files.write("/tests/judge_hook.sh", judge_hook.read_bytes())
                handle = await sandbox.commands.run("chmod +x /tests/judge_hook.sh", background=True, user="root")
                await handle.wait()

            # Step 4: Run test.sh on base commit (should score < 1.0)
            t0 = time.monotonic()
            from e2b.sandbox.commands.command_handle import CommandExitException
            try:
                handle = await sandbox.commands.run(
                    "bash /tests/test.sh", background=True, user="root", timeout=120,
                )
                try:
                    base_result = await handle.wait()
                except CommandExitException as e:
                    base_result = e
                logger.info("[%s] Base test stdout (last 500 chars): %s", task_name, (base_result.stdout or "")[-500:])
            except Exception as e:
                logger.error("[%s] Base test execution error: %s", task_name, e)
                result.error = f"Base test execution error: {e}"
                result.total_time = time.monotonic() - task_start
                return result

            result.base_test_time = time.monotonic() - t0

            # Read reward
            try:
                reward_data = await sandbox.files.read("/logs/verifier/reward.txt", format="text")
                result.base_score = float(reward_data.strip())
            except Exception:
                result.base_score = -1.0
                logger.warning("[%s] Could not read base reward.txt", task_name)

            logger.info("[%s] Base score: %.2f (%.1fs)", task_name, result.base_score, result.base_test_time)

            # Step 5: Run solve.sh (apply gold patch)
            t0 = time.monotonic()
            try:
                handle = await sandbox.commands.run(
                    "bash /tests/solve.sh", background=True, user="root", timeout=120,
                )
                try:
                    solve_result = await handle.wait()
                except CommandExitException as e:
                    solve_result = e
                logger.info("[%s] Solve stdout: %s", task_name, (solve_result.stdout or "")[-300:])
                if solve_result.stderr:
                    logger.info("[%s] Solve stderr: %s", task_name, (solve_result.stderr or "")[-300:])
            except Exception as e:
                logger.error("[%s] Solve execution error: %s", task_name, e)
                result.error = f"Solve execution error: {e}"
                result.total_time = time.monotonic() - task_start
                return result

            result.solve_time = time.monotonic() - t0

            # Step 6: Run test.sh after solve (should score 1.0)
            t0 = time.monotonic()
            try:
                handle = await sandbox.commands.run(
                    "bash /tests/test.sh", background=True, user="root", timeout=120,
                )
                try:
                    gold_result = await handle.wait()
                except CommandExitException as e:
                    gold_result = e
                logger.info("[%s] Gold test stdout (last 500 chars): %s", task_name, (gold_result.stdout or "")[-500:])
            except Exception as e:
                logger.error("[%s] Gold test execution error: %s", task_name, e)
                result.error = f"Gold test execution error: {e}"
                result.total_time = time.monotonic() - task_start
                return result

            result.gold_test_time = time.monotonic() - t0

            # Read reward
            try:
                reward_data = await sandbox.files.read("/logs/verifier/reward.txt", format="text")
                result.gold_score = float(reward_data.strip())
            except Exception:
                result.gold_score = -1.0
                logger.warning("[%s] Could not read gold reward.txt", task_name)

            logger.info("[%s] Gold score: %.2f (%.1fs)", task_name, result.gold_score, result.gold_test_time)

        except Exception as e:
            result.error = str(e)
            logger.error("[%s] FAILED: %s", task_name, e)
        finally:
            # Cleanup sandbox
            if sandbox is not None:
                try:
                    await sandbox.kill()
                except Exception as e:
                    logger.warning("[%s] Sandbox cleanup failed: %s", task_name, e)

    result.total_time = time.monotonic() - task_start
    return result


async def run_batch(task_names: list[str], concurrency: int) -> RunStats:
    """Run a batch of tasks with the given concurrency level."""
    stats = RunStats(concurrency=concurrency, num_tasks=len(task_names))
    semaphore = asyncio.Semaphore(concurrency)

    logger.info("=" * 70)
    logger.info("BATCH: %d tasks, concurrency=%d", len(task_names), concurrency)
    logger.info("=" * 70)

    wall_start = time.monotonic()
    results = await asyncio.gather(*[run_task(t, semaphore) for t in task_names])
    stats.wall_time = time.monotonic() - wall_start
    stats.results = list(results)
    stats.total_rate_limit_hits = sum(r.rate_limit_hits for r in results)

    return stats


def print_report(stats: RunStats) -> None:
    """Print a summary table for a batch run."""
    print()
    print("=" * 100)
    print(f"  BATCH REPORT: {stats.num_tasks} tasks, concurrency={stats.concurrency}, "
          f"wall_time={stats.wall_time:.1f}s, rate_limit_hits={stats.total_rate_limit_hits}")
    print("=" * 100)
    print(f"{'Task':<50} {'Build':>7} {'Create':>7} {'BaseT':>7} {'Base':>6} "
          f"{'Solve':>7} {'GoldT':>7} {'Gold':>6} {'Total':>7} {'429s':>5} {'Error'}")
    print("-" * 130)

    for r in stats.results:
        err_short = r.error[:30] if r.error else ""
        print(f"{r.task_name:<50} {r.build_time:>6.1f}s {r.sandbox_create_time:>6.1f}s "
              f"{r.base_test_time:>6.1f}s {r.base_score:>5.2f} "
              f"{r.solve_time:>6.1f}s {r.gold_test_time:>6.1f}s {r.gold_score:>5.2f} "
              f"{r.total_time:>6.1f}s {r.rate_limit_hits:>4}  {err_short}")

    # Summary stats
    successful = [r for r in stats.results if not r.error]
    failed = [r for r in stats.results if r.error]
    perfect_gold = [r for r in successful if r.gold_score == 1.0]
    low_base = [r for r in successful if 0 <= r.base_score < 1.0]

    print()
    print(f"  Successful: {len(successful)}/{stats.num_tasks}")
    print(f"  Failed: {len(failed)}/{stats.num_tasks}")
    if failed:
        for r in failed:
            print(f"    - {r.task_name}: {r.error[:80]}")
    print(f"  Gold score == 1.0: {len(perfect_gold)}/{len(successful)}")
    print(f"  Base score < 1.0: {len(low_base)}/{len(successful)}")

    if successful:
        avg_create = sum(r.sandbox_create_time for r in successful) / len(successful)
        avg_base_test = sum(r.base_test_time for r in successful) / len(successful)
        avg_solve = sum(r.solve_time for r in successful) / len(successful)
        avg_gold_test = sum(r.gold_test_time for r in successful) / len(successful)
        avg_total = sum(r.total_time for r in successful) / len(successful)
        print(f"\n  Avg sandbox create: {avg_create:.1f}s")
        print(f"  Avg base test: {avg_base_test:.1f}s")
        print(f"  Avg solve: {avg_solve:.1f}s")
        print(f"  Avg gold test: {avg_gold_test:.1f}s")
        print(f"  Avg total per task: {avg_total:.1f}s")
        print(f"  Throughput: {len(successful) / stats.wall_time:.2f} tasks/sec")
    print()


async def main() -> None:
    if not os.environ.get("E2B_API_KEY"):
        print("E2B_API_KEY not set. Source .env first:")
        print("  set -a && source .env && set +a && python scripts/test_e2b_scale.py")
        sys.exit(1)

    # Verify tasks exist locally
    available = []
    for name in READY_TASKS:
        task_dir = HARBOR_TASKS_DIR / name
        if task_dir.is_dir() and (task_dir / "tests" / "test.sh").exists() and (task_dir / "solution" / "solve.sh").exists():
            available.append(name)
        else:
            logger.warning("Task %s missing or incomplete, skipping", name)

    print(f"Available tasks: {len(available)} / {len(READY_TASKS)}")

    # Parse CLI args for batch size / concurrency override
    batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    concurrency = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    tasks_to_run = available[:batch_size]
    print(f"\nRunning {len(tasks_to_run)} tasks at concurrency {concurrency}")
    for t in tasks_to_run:
        print(f"  - {t}")
    print()

    stats = await run_batch(tasks_to_run, concurrency)
    print_report(stats)

    # Write JSON results
    output_path = Path(__file__).parent / "e2b_scale_results.json"
    json_results = {
        "concurrency": stats.concurrency,
        "num_tasks": stats.num_tasks,
        "wall_time": round(stats.wall_time, 2),
        "rate_limit_hits": stats.total_rate_limit_hits,
        "tasks": [
            {
                "task_name": r.task_name,
                "template_name": r.template_name,
                "template_exists": r.template_exists,
                "build_time": round(r.build_time, 2),
                "sandbox_create_time": round(r.sandbox_create_time, 2),
                "base_test_time": round(r.base_test_time, 2),
                "base_score": r.base_score,
                "solve_time": round(r.solve_time, 2),
                "gold_test_time": round(r.gold_test_time, 2),
                "gold_score": r.gold_score,
                "total_time": round(r.total_time, 2),
                "rate_limit_hits": r.rate_limit_hits,
                "error": r.error,
            }
            for r in stats.results
        ],
    }
    output_path.write_text(json.dumps(json_results, indent=2))
    print(f"Results written to {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
