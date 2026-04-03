"""Proof-of-concept: validate a single Harbor task via E2B sandbox.

Self-contained -- uses only the e2b SDK, no tinker_cookbook dependency.
Runs the full validation cycle: build template, create sandbox,
run base test (nop), apply gold patch (solve.sh), run gold test.

Usage:
    set -a && source .env && set +a
    python scripts/e2b_validate_poc.py [task-name]
    python scripts/e2b_validate_poc.py   # defaults to areal-config-postinit-validation
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
from hashlib import sha256
from pathlib import Path

from e2b import AsyncSandbox, AsyncTemplate, Template
from e2b.sandbox.commands.command_handle import CommandExitException

HARBOR_TASKS_DIR = Path(__file__).resolve().parent.parent / "harbor_tasks"


def dir_hash(env_dir: Path, length: int = 12) -> str:
    dockerfile = env_dir / "Dockerfile"
    if dockerfile.exists():
        return sha256(dockerfile.read_bytes()).hexdigest()[:length]
    return sha256(str(env_dir).encode()).hexdigest()[:length]


async def run_cmd(sandbox: AsyncSandbox, cmd: str, timeout: int = 120) -> tuple[int, str, str]:
    """Run a command in the sandbox, return (exit_code, stdout, stderr)."""
    try:
        handle = await sandbox.commands.run(cmd, background=True, user="root", timeout=timeout)
        try:
            result = await handle.wait()
        except CommandExitException as e:
            result = e
        return result.exit_code, result.stdout or "", result.stderr or ""
    except Exception as e:
        return -1, "", str(e)


async def validate_task(task_name: str) -> dict:
    """Validate a single task: build/reuse template, run nop test, apply gold, run gold test."""
    task_dir = HARBOR_TASKS_DIR / task_name
    env_dir = task_dir / "environment"
    test_sh = task_dir / "tests" / "test.sh"
    solve_sh = task_dir / "solution" / "solve.sh"

    # Also grab test_outputs.py if it exists (test.sh runs pytest on it)
    test_outputs_py = task_dir / "tests" / "test_outputs.py"

    assert task_dir.is_dir(), f"Task dir not found: {task_dir}"
    assert (env_dir / "Dockerfile").exists(), f"No Dockerfile in {env_dir}"
    assert test_sh.exists(), f"No test.sh in {task_dir / 'tests'}"
    assert solve_sh.exists(), f"No solve.sh in {task_dir / 'solution'}"

    result = {"task": task_name, "steps": {}}
    total_start = time.monotonic()

    # Step 1: Build or reuse E2B template
    dh = dir_hash(env_dir)
    template_name = f"tinker-{task_name}-{dh}".replace(".", "-")
    print(f"[1/5] Template: {template_name}")

    t0 = time.monotonic()
    try:
        exists = await AsyncTemplate.alias_exists(template_name)
    except Exception as e:
        print(f"  ERROR checking alias: {e}")
        exists = False

    if exists:
        print(f"  Template already cached ({time.monotonic() - t0:.1f}s)")
        result["steps"]["template"] = {"status": "cached", "time": round(time.monotonic() - t0, 2)}
    else:
        print(f"  Building template from Dockerfile...")
        dockerfile_path = env_dir / "Dockerfile"
        tpl = Template().from_dockerfile(dockerfile_content_or_path=str(dockerfile_path))
        await AsyncTemplate.build(
            template=tpl, alias=template_name,
            cpu_count=2, memory_mb=1024,
        )
        build_time = time.monotonic() - t0
        print(f"  Built in {build_time:.1f}s")
        result["steps"]["template"] = {"status": "built", "time": round(build_time, 2)}

    # Step 2: Create sandbox
    print(f"[2/5] Creating sandbox...")
    t0 = time.monotonic()
    sandbox = await AsyncSandbox.create(template=template_name, timeout=600)
    create_time = time.monotonic() - t0
    print(f"  Sandbox {sandbox.sandbox_id} created in {create_time:.1f}s")
    result["steps"]["sandbox_create"] = {"sandbox_id": sandbox.sandbox_id, "time": round(create_time, 2)}

    try:
        # Ensure dirs exist
        await run_cmd(sandbox, "mkdir -p /logs/verifier /tests && chmod 777 /logs/verifier /tests")

        # Upload test files
        await sandbox.files.write("/tests/test.sh", test_sh.read_bytes())
        await run_cmd(sandbox, "chmod +x /tests/test.sh")
        if test_outputs_py.exists():
            await sandbox.files.write("/tests/test_outputs.py", test_outputs_py.read_bytes())

        await sandbox.files.write("/tests/solve.sh", solve_sh.read_bytes())
        await run_cmd(sandbox, "chmod +x /tests/solve.sh")

        # Step 3: Run base test (nop -- should fail, reward=0)
        print(f"[3/5] Running base test (nop)...")
        t0 = time.monotonic()
        exit_code, stdout, stderr = await run_cmd(sandbox, "bash /tests/test.sh", timeout=120)
        base_time = time.monotonic() - t0

        # Read reward
        try:
            reward_data = await sandbox.files.read("/logs/verifier/reward.txt", format="text")
            base_reward = float(reward_data.strip())
        except Exception:
            base_reward = -1.0

        print(f"  Base test: exit={exit_code}, reward={base_reward} ({base_time:.1f}s)")
        if base_reward == 1.0:
            print(f"  WARNING: Base test passed -- test might not be fail-to-pass!")
        result["steps"]["base_test"] = {
            "exit_code": exit_code,
            "reward": base_reward,
            "time": round(base_time, 2),
            "stdout_tail": stdout[-300:] if stdout else "",
            "stderr_tail": stderr[-300:] if stderr else "",
        }

        # Step 4: Apply gold patch (solve.sh)
        print(f"[4/5] Applying gold patch (solve.sh)...")
        t0 = time.monotonic()
        exit_code, stdout, stderr = await run_cmd(sandbox, "bash /tests/solve.sh", timeout=120)
        solve_time = time.monotonic() - t0
        print(f"  Solve: exit={exit_code} ({solve_time:.1f}s)")
        if exit_code != 0:
            print(f"  WARNING: solve.sh exited with {exit_code}")
            print(f"  stderr: {stderr[-200:]}")
        result["steps"]["solve"] = {
            "exit_code": exit_code,
            "time": round(solve_time, 2),
            "stdout_tail": stdout[-200:] if stdout else "",
            "stderr_tail": stderr[-200:] if stderr else "",
        }

        # Step 5: Run gold test (should pass, reward=1)
        print(f"[5/5] Running gold test...")
        t0 = time.monotonic()
        exit_code, stdout, stderr = await run_cmd(sandbox, "bash /tests/test.sh", timeout=120)
        gold_time = time.monotonic() - t0

        try:
            reward_data = await sandbox.files.read("/logs/verifier/reward.txt", format="text")
            gold_reward = float(reward_data.strip())
        except Exception:
            gold_reward = -1.0

        print(f"  Gold test: exit={exit_code}, reward={gold_reward} ({gold_time:.1f}s)")
        result["steps"]["gold_test"] = {
            "exit_code": exit_code,
            "reward": gold_reward,
            "time": round(gold_time, 2),
            "stdout_tail": stdout[-300:] if stdout else "",
            "stderr_tail": stderr[-300:] if stderr else "",
        }

    finally:
        # Cleanup
        try:
            await sandbox.kill()
            print(f"  Sandbox killed.")
        except Exception as e:
            print(f"  Sandbox cleanup warning: {e}")

    total_time = time.monotonic() - total_start
    result["total_time"] = round(total_time, 2)

    # Summary
    base_r = result["steps"].get("base_test", {}).get("reward", -1)
    gold_r = result["steps"].get("gold_test", {}).get("reward", -1)
    valid = base_r == 0.0 and gold_r == 1.0

    print()
    print("=" * 60)
    print(f"  Task:       {task_name}")
    print(f"  Base reward: {base_r}  (want 0)")
    print(f"  Gold reward: {gold_r}  (want 1)")
    print(f"  VALID:      {'YES' if valid else 'NO'}")
    print(f"  Total time: {total_time:.1f}s")
    print("=" * 60)

    result["valid"] = valid
    return result


async def main():
    if not os.environ.get("E2B_API_KEY"):
        print("E2B_API_KEY not set. Run:")
        print("  set -a && source .env && set +a && python scripts/e2b_validate_poc.py")
        sys.exit(1)

    task_name = sys.argv[1] if len(sys.argv) > 1 else "areal-config-postinit-validation"
    print(f"Validating task: {task_name}")
    print()

    result = await validate_task(task_name)
    return result


if __name__ == "__main__":
    asyncio.run(main())
