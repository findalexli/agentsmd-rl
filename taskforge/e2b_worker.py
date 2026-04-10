"""Consolidated E2B pipeline: scaffold → improve → validate → judge.

One E2B sandbox per task handles the full lifecycle. Only tasks that
pass Docker oracle (nop=0, gold=1) get downloaded locally.

Usage:
    # Validate existing tasks (no LLM needed)
    python -m taskforge.e2b_worker --mode validate --task-dir harbor_tasks --concurrency 50

    # Full pipeline from PRs
    python -m taskforge.e2b_worker --mode full --input prs.jsonl --pool --concurrency 18

    # Improve + validate existing tasks
    python -m taskforge.e2b_worker --mode improve --task-dir harbor_tasks --pool --concurrency 18
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from e2b import AsyncSandbox, AsyncTemplate, Template
from e2b.sandbox.commands.command_handle import CommandExitException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = Path(__file__).resolve().parent / "e2b_template"
TEMPLATE_ALIAS = "harbor-worker-v3"

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


class _RateLimited(Exception):
    """Raised when an agent hits LLM rate limit — triggers retry at batch level."""
    pass


@dataclass
class WorkerResult:
    task_ref: str
    task_name: str = ""
    mode: str = ""  # "full" | "validate" | "improve"
    backend_name: str = ""
    sandbox_id: str = ""
    scaffold_status: str = ""  # "ok" | "error" | "skipped"
    scaffold_time: float = 0.0
    improve_status: str = ""  # "ok" | "skipped" | "error"
    improve_time: float = 0.0
    build_status: str = ""  # "ok" | "error"
    build_time: float = 0.0
    nop_reward: float = -1.0
    gold_reward: float = -1.0
    validate_time: float = 0.0
    repair_attempted: bool = False
    repair_status: str = ""
    valid: bool = False  # nop==0 and gold==1
    downloaded: bool = False
    gemini_score: float | None = None
    total_time: float = 0.0
    error: str = ""


# ---------------------------------------------------------------------------
# Sandbox helpers
# ---------------------------------------------------------------------------


async def retry_on_429(fn, max_retries: int = 5):
    """Call async fn, retry on rate-limit. Returns result."""
    for attempt in range(max_retries):
        try:
            return await fn()
        except Exception as e:
            err = str(e).lower()
            if "429" in err or "rate limit" in err:
                wait = 20 * (attempt + 1)
                logger.warning("E2B rate limited (attempt %d), waiting %ds", attempt + 1, wait)
                await asyncio.sleep(wait)
            else:
                raise
    raise RuntimeError(f"Failed after {max_retries} E2B rate-limit retries")


async def run_cmd(
    sandbox: AsyncSandbox, cmd: str, timeout: int = 0, user: str = "root"
) -> tuple[int, str, str]:
    """Run a command in the sandbox. Returns (exit_code, stdout, stderr).
    timeout=0 disables the timeout (wait forever)."""
    try:
        result = await sandbox.commands.run(cmd, timeout=timeout, user=user)
        return result.exit_code, result.stdout or "", result.stderr or ""
    except CommandExitException as e:
        return e.exit_code, e.stdout or "", e.stderr or ""
    except Exception as e:
        return -1, "", str(e)


async def ensure_template() -> str:
    """Build harbor-worker template if it doesn't exist. Returns alias."""
    try:
        exists = await AsyncTemplate.alias_exists(TEMPLATE_ALIAS)
    except Exception:
        exists = False

    if exists:
        logger.info("Template '%s' already exists (cached)", TEMPLATE_ALIAS)
        return TEMPLATE_ALIAS

    logger.info("Building template '%s' from %s ...", TEMPLATE_ALIAS, TEMPLATE_DIR)
    dockerfile_path = TEMPLATE_DIR / "Dockerfile"
    if not dockerfile_path.exists():
        raise FileNotFoundError(f"Template Dockerfile not found: {dockerfile_path}")

    tpl = Template().from_dockerfile(dockerfile_content_or_path=str(dockerfile_path))
    await AsyncTemplate.build(
        template=tpl,
        alias=TEMPLATE_ALIAS,
        cpu_count=8,
        memory_mb=8192,
    )
    logger.info("Template '%s' built successfully", TEMPLATE_ALIAS)
    return TEMPLATE_ALIAS


async def create_worker_sandbox(
    backend_env: dict[str, str] | None = None,
    timeout: int = 3600,
    max_ip_retries: int = 10,
) -> AsyncSandbox:
    """Create sandbox from harbor-worker template with env vars injected.
    Retries sandbox creation if the egress IP is blocked by the LLM provider.
    timeout = sandbox lifetime in seconds (default 1 hour)."""
    envs = {
        "GH_TOKEN": os.environ.get("GH_TOKEN", ""),
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", ""),
    }
    if backend_env:
        envs.update(backend_env)

    # Determine the API base URL for IP probing
    api_base = backend_env.get("ANTHROPIC_BASE_URL", "") if backend_env else ""

    for ip_attempt in range(max_ip_retries):
        sandbox = await retry_on_429(
            lambda: AsyncSandbox.create(
                template=TEMPLATE_ALIAS,
                timeout=timeout,
                envs=envs,
            )
        )

        # Explicitly extend sandbox lifetime
        try:
            await sandbox.set_timeout(timeout)
        except Exception:
            pass

        # Quick IP probe: only for Fireworks backend (detect IP blocks)
        # Skip for Gemini (localhost proxy) and other non-Fireworks backends
        is_fireworks = api_base and "fireworks" in api_base.lower()
        if is_fireworks:
            api_key = envs.get("ANTHROPIC_API_KEY", "")
            if api_key and api_key != "dummy":
                probe_code, probe_out, _ = await run_cmd(
                    sandbox,
                    f'curl -s -o /dev/null -w "%{{http_code}}" -X POST '
                    f'"https://api.fireworks.ai/inference/v1/messages" '
                    f'-H "Content-Type: application/json" '
                    f'-H "x-api-key: {api_key}" '
                    f'-H "anthropic-version: 2023-06-01" '
                    f"""-d '{{"model":"accounts/fireworks/routers/kimi-k2p5-turbo","messages":[{{"role":"user","content":"hi"}}],"max_tokens":1}}'""",
                    timeout=15,
                )
                status_code = probe_out.strip()
                if status_code == "403":
                    logger.warning(
                        "Sandbox %s blocked by Fireworks (403), retrying (%d/%d)...",
                        sandbox.sandbox_id, ip_attempt + 1, max_ip_retries,
                    )
                    try:
                        await sandbox.kill()
                    except Exception:
                        pass
                    await asyncio.sleep(1)
                    continue
                logger.info("Sandbox %s Fireworks IP check OK (status %s)", sandbox.sandbox_id, status_code)

        # Wait for Docker daemon to be ready
        for _ in range(10):
            code, _, _ = await run_cmd(sandbox, "docker info", timeout=10)
            if code == 0:
                break
            await asyncio.sleep(2)

        # Ensure worker user owns workspace (for claude -p as non-root)
        await run_cmd(sandbox, "chown -R worker:worker /workspace /logs/verifier", timeout=10)
        # Add worker to docker group so it can run docker commands
        await run_cmd(sandbox, "usermod -aG docker worker 2>/dev/null || true", timeout=5)

        # Start litellm proxy if using Gemini as main backend
        if backend_env and backend_env.get("ANTHROPIC_BASE_URL") == "http://localhost:4000":
            await _ensure_litellm_proxy(sandbox)

        return sandbox

    # All retries exhausted — return last sandbox anyway
    logger.error("All %d IP probe retries failed, proceeding with blocked sandbox", max_ip_retries)
    return sandbox


async def _ensure_litellm_proxy(sandbox: AsyncSandbox) -> bool:
    """Start litellm proxy for Gemini routing if not already running.

    Used to route specific agents (rubric enrichment) through Gemini 3.1 Pro
    while keeping the main backend (Kimi) for other agents.
    Returns True if proxy is ready.
    """
    # Check if already running
    code, stdout, _ = await run_cmd(
        sandbox,
        'curl -s -o /dev/null -w "%{http_code}" http://localhost:4000/health 2>/dev/null || echo 000',
        timeout=5,
    )
    if stdout.strip() == "200":
        return True

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key:
        logger.warning("No GEMINI_API_KEY — cannot start litellm proxy for Gemini routing")
        return False

    litellm_config = (
        'litellm_settings:\n'
        '  drop_params: true\n'
        'model_list:\n'
        '  - model_name: "claude-opus-4-6"\n'
        '    litellm_params:\n'
        '      model: "gemini/gemini-3.1-pro-preview-customtools"\n'
        f'      api_key: "{gemini_key}"\n'
        '  - model_name: "claude-sonnet-4-6"\n'
        '    litellm_params:\n'
        '      model: "gemini/gemini-3.1-pro-preview-customtools"\n'
        f'      api_key: "{gemini_key}"\n'
        '  - model_name: "opus"\n'
        '    litellm_params:\n'
        '      model: "gemini/gemini-3.1-pro-preview-customtools"\n'
        f'      api_key: "{gemini_key}"\n'
    )
    await sandbox.files.write("/tmp/litellm_config.yaml", litellm_config.encode())
    await run_cmd(
        sandbox,
        "nohup litellm --config /tmp/litellm_config.yaml --port 4000 "
        "> /tmp/litellm.log 2>&1 &",
        timeout=10,
    )
    # Poll for proxy readiness (litellm takes 10-20s to start)
    for _attempt in range(20):
        await asyncio.sleep(2)
        code, stdout, _ = await run_cmd(
            sandbox,
            'curl -s -o /dev/null -w "%{http_code}" http://localhost:4000/health 2>/dev/null || echo 000',
            timeout=5,
        )
        if stdout.strip() == "200":
            logger.info("Sandbox %s: litellm proxy -> Gemini 3.1 Pro ready", sandbox.sandbox_id)
            return True

    logger.warning("Sandbox %s: litellm proxy failed to start after 40s", sandbox.sandbox_id)
    return False


# ---------------------------------------------------------------------------
# Quality gate
# ---------------------------------------------------------------------------


async def check_test_quality(sandbox: AsyncSandbox) -> tuple[bool, str]:
    """Programmatic quality gate on test_outputs.py.
    Returns (needs_improve, reason).
    """
    code, stdout, stderr = await run_cmd(
        sandbox,
        'python3 -c "'
        "import ast, sys; "
        "src = open('/workspace/task/tests/test_outputs.py').read(); "
        "ast.parse(src); "
        "has_stub = 'NotImplementedError' in src; "
        "has_subprocess = 'subprocess.run' in src or 'subprocess.check' in src; "
        "has_test = 'def test_' in src; "
        "print(f'{has_stub},{has_subprocess},{has_test}')"
        '"',
        timeout=10,
    )
    if code != 0:
        return True, f"syntax error or missing file: {stderr[:200]}"

    parts = stdout.strip().split(",")
    if len(parts) != 3:
        return True, f"unexpected output: {stdout[:100]}"

    has_stub = parts[0] == "True"
    has_subprocess = parts[1] == "True"
    has_test = parts[2] == "True"

    if not has_test:
        return True, "no test functions found"
    if has_stub:
        return True, "contains NotImplementedError stubs"
    if not has_subprocess:
        return True, "no subprocess.run (grep-only tests)"
    return False, "tests look good"


# ---------------------------------------------------------------------------
# Pipeline phases
# ---------------------------------------------------------------------------


async def run_scaffold_in_sandbox(
    sandbox: AsyncSandbox,
    pr_ref: str,
    agentmd: bool = False,
) -> tuple[str, str]:
    """Upload scaffold prompt, run claude -p. Returns (status, error)."""
    # Read scaffold prompt template (use agentmd-specific prompt when appropriate)
    if agentmd:
        prompt_file = ROOT / "taskforge" / "prompts" / "scaffold_agentmd.md"
    else:
        prompt_file = ROOT / "taskforge" / "prompts" / "scaffold.md"
    if not prompt_file.exists():
        prompt_file = ROOT / ".claude" / "commands" / "scaffold-task.md"
    prompt = prompt_file.read_text().replace("$ARGUMENTS", pr_ref)

    # Determine task dir name based on mode
    task_dir_name = "harbor_tasks_agentmd_edits" if agentmd else "harbor_tasks"
    prompt = prompt.replace("harbor_tasks/", f"{task_dir_name}/")

    # Upload prompt
    await sandbox.files.write("/workspace/scaffold_prompt.md", prompt.encode())

    # Run claude -p as non-root (refuses --dangerously-skip-permissions as root)
    code, stdout, stderr = await run_cmd(
        sandbox,
        "cat /workspace/scaffold_prompt.md | claude -p "
        "--dangerously-skip-permissions --model opus "
        "--output-format json",
        user="worker",
    )

    if code != 0:
        combined = stdout + stderr
        if "429" in combined or "Rate limit" in combined or "hit your limit" in combined.lower():
            return "rate_limited", combined[:500]
        return "error", combined[:500]

    # Check if scaffold agent abandoned the task
    try:
        raw = await sandbox.files.read("/workspace/task/status.json", format="text")
        status_data = json.loads(raw)
        if status_data.get("abandoned"):
            reason = status_data.get("reason", "no reason given")
            logger.info("  Scaffold abandoned: %s", reason)
            return "abandoned", reason
    except Exception:
        pass

    # Check that task files were created
    check_code, check_out, _ = await run_cmd(
        sandbox,
        "ls /workspace/task/tests/test_outputs.py /workspace/task/environment/Dockerfile "
        "/workspace/task/solution/solve.sh 2>&1",
        timeout=5,
    )
    if check_code != 0:
        # Try to find where scaffold put the files
        find_code, find_out, _ = await run_cmd(
            sandbox,
            "find /workspace -name test_outputs.py -type f -not -path '/workspace/task/*' 2>/dev/null | head -3",
            timeout=10,
        )
        if find_out.strip():
            # Move files to expected location using rsync/cp -a for robustness
            task_root = str(Path(find_out.strip().split("\n")[0]).parent.parent)
            await run_cmd(sandbox, f"cp -a {task_root}/* /workspace/task/ 2>/dev/null; "
                                   f"cp -a {task_root}/.[!.]* /workspace/task/ 2>/dev/null; true")
            # Re-check
            check_code, _, _ = await run_cmd(
                sandbox,
                "ls /workspace/task/tests/test_outputs.py",
                timeout=5,
            )
            if check_code != 0:
                # Also check if files ended up one level deeper
                find2_code, find2_out, _ = await run_cmd(
                    sandbox,
                    "find /workspace -name test_outputs.py -type f 2>/dev/null",
                    timeout=10,
                )
                return "error", f"scaffold created files but not in expected location. Found at: {find2_out.strip()[:200]}"
        else:
            # Maybe scaffold put everything under a named subdir of /workspace/task/
            find_code2, find_out2, _ = await run_cmd(
                sandbox,
                "find /workspace/task -name test_outputs.py -type f 2>/dev/null | head -3",
                timeout=10,
            )
            if find_out2.strip():
                # Files are nested under /workspace/task/<name>/tests/ — flatten
                nested_root = str(Path(find_out2.strip().split("\n")[0]).parent.parent)
                if nested_root != "/workspace/task":
                    await run_cmd(sandbox, f"cp -a {nested_root}/* /workspace/task/ 2>/dev/null; true")
                    check_code, _, _ = await run_cmd(sandbox, "ls /workspace/task/tests/test_outputs.py", timeout=5)
                    if check_code == 0:
                        pass  # Fixed
                    else:
                        return "error", f"scaffold nested files at {nested_root}, couldn't flatten"
            else:
                return "error", f"scaffold did not create task files. stdout: {stdout[:300]}"

    return "ok", ""


async def run_improve_in_sandbox(sandbox: AsyncSandbox) -> tuple[str, str]:
    """Upload improve prompt, run claude -p. Returns (status, error)."""
    prompt_file = ROOT / "taskforge" / "prompts" / "improve_tests.md"
    prompt = prompt_file.read_text()
    # The improve prompt expects $ARGUMENTS = task name and $TASK_DIR
    # In sandbox, task is always at /workspace/task/
    prompt = prompt.replace("$TASK_DIR/$ARGUMENTS/", "/workspace/task/")
    prompt = prompt.replace("$TASK_DIR/", "/workspace/")
    prompt = prompt.replace("$ARGUMENTS", "task")

    await sandbox.files.write("/workspace/improve_prompt.md", prompt.encode())

    code, stdout, stderr = await run_cmd(
        sandbox,
        "cat /workspace/improve_prompt.md | claude -p "
        "--dangerously-skip-permissions --model opus "
        "--output-format json",
        

        user="worker",
    )

    if code != 0:
        combined = stdout + stderr
        if "429" in combined or "Rate limit" in combined or "hit your limit" in combined.lower():
            return "rate_limited", combined[:500]
        return "error", combined[:500]

    return "ok", ""


async def validate_docker_in_sandbox(
    sandbox: AsyncSandbox,
) -> tuple[float, float, str]:
    """Build Docker image, run nop + gold tests.
    Returns (nop_reward, gold_reward, error_detail).
    """
    # Build the task's Docker image
    code, stdout, stderr = await run_cmd(
        sandbox,
        "cd /workspace/task/environment && docker build -t task-env .",
        

    )
    if code != 0:
        return -1, -1, f"docker build failed: {stderr[-500:]}"

    # NOP test (no fix applied, expect reward=0)
    await run_cmd(sandbox, "rm -f /logs/verifier/reward.txt")
    code, stdout, stderr = await run_cmd(
        sandbox,
        "docker run --rm "
        "-v /workspace/task/tests:/tests:ro "
        "-v /logs/verifier:/logs/verifier "
        "task-env bash /tests/test.sh",
        

    )
    nop_reward = await _read_reward(sandbox)

    # Apply gold solution: run solve.sh inside the container, commit
    await run_cmd(sandbox, "docker rm -f task-solved 2>/dev/null || true")
    code, stdout, stderr = await run_cmd(
        sandbox,
        "docker run --name task-solved "
        "-v /workspace/task/solution:/solution:ro "
        "task-env bash /solution/solve.sh",
        

    )
    if code != 0:
        return nop_reward, -1, f"solve.sh failed: {stderr[-300:]}"

    await run_cmd(sandbox, "docker commit task-solved task-env-gold")
    await run_cmd(sandbox, "docker rm task-solved")

    # GOLD test (fix applied, expect reward=1)
    await run_cmd(sandbox, "rm -f /logs/verifier/reward.txt")
    code, stdout, stderr = await run_cmd(
        sandbox,
        "docker run --rm "
        "-v /workspace/task/tests:/tests:ro "
        "-v /logs/verifier:/logs/verifier "
        "task-env-gold bash /tests/test.sh",
        

    )
    gold_reward = await _read_reward(sandbox)

    return nop_reward, gold_reward, ""


async def _read_reward(sandbox: AsyncSandbox) -> float:
    """Read reward.txt from sandbox. Returns -1 if missing/unreadable."""
    try:
        data = await sandbox.files.read("/logs/verifier/reward.txt", format="text")
        return float(data.strip())
    except Exception:
        return -1.0


async def run_repair_in_sandbox(
    sandbox: AsyncSandbox,
    failure_type: str,
    error_detail: str,
) -> tuple[str, str]:
    """One-shot repair attempt. Returns (status, error)."""
    repair_instructions = {
        "build_error": (
            "The Docker build failed. Fix the Dockerfile at /workspace/task/environment/Dockerfile. "
            "Common issues: missing apt package, wrong base image, repo URL changed, "
            "missing python3 on non-Python images."
        ),
        "nop_high": (
            "The tests PASS even without applying the fix (nop reward=1). "
            "This means test_outputs.py doesn't test the actual behavioral change. "
            "Rewrite the fail_to_pass tests to check behavior that differs between "
            "the base commit (broken) and the fixed code."
        ),
        "gold_low": (
            "The tests FAIL after applying solve.sh (gold reward=0). "
            "Check: (1) Is solve.sh applying the patch correctly? "
            "(2) Are tests checking the wrong thing? "
            "(3) Missing dependencies in Dockerfile that tests need?"
        ),
    }

    instructions = repair_instructions.get(failure_type, "Fix the validation failure.")
    prompt = f"""# Repair Task

The task at /workspace/task/ failed validation. Read `/workspace/task/status.json` — the `nodes` section has detailed notes from each previous validation step explaining what passed, what failed, and why.

## Failure type: {failure_type}

## Error details:
{error_detail[:1000]}

## Instructions:
{instructions}

## Process:
1. Read `/workspace/task/status.json` to understand the full validation history
2. Read the relevant task files (Dockerfile, test_outputs.py, solve.sh, etc.)
3. Diagnose the root cause based on the node notes
4. Fix the issue
5. Update the `repair` node in `/workspace/task/status.json` with what you changed

Only modify files in /workspace/task/ — do NOT modify the Docker image directly.
"""

    await sandbox.files.write("/workspace/repair_prompt.md", prompt.encode())

    code, stdout, stderr = await run_cmd(
        sandbox,
        "cat /workspace/repair_prompt.md | claude -p "
        "--dangerously-skip-permissions --model opus "
        "--output-format json",
        

        user="worker",
    )

    if code != 0:
        return "error", (stdout + stderr)[:500]
    return "ok", ""


def classify_failure(nop: float, gold: float, error: str) -> str:
    """Classify validation failure for repair targeting."""
    if error and "docker build" in error.lower():
        return "build_error"
    if nop >= 0.99:
        return "nop_high"
    if gold < 0.99:
        return "gold_low"
    return "unknown"


# ---------------------------------------------------------------------------
# File transfer
# ---------------------------------------------------------------------------


async def upload_task_files(sandbox: AsyncSandbox, task_path: Path) -> None:
    """Upload all task files from local dir to /workspace/task/ in sandbox."""
    for f in task_path.rglob("*"):
        if f.is_file():
            rel = f.relative_to(task_path)
            remote_path = f"/workspace/task/{rel}"
            await sandbox.files.write(remote_path, f.read_bytes())
    # Make scripts executable
    await run_cmd(sandbox, "chmod +x /workspace/task/solution/solve.sh /workspace/task/tests/test.sh 2>/dev/null || true")


async def download_task_files(sandbox: AsyncSandbox, dest: Path) -> list[str]:
    """Download all task files from /workspace/task/ to local dir."""
    dest.mkdir(parents=True, exist_ok=True)

    # List files in sandbox
    code, stdout, _ = await run_cmd(
        sandbox,
        "find /workspace/task -type f | sort",
        timeout=10,
    )
    if code != 0:
        return []

    downloaded = []
    for remote_path in stdout.strip().split("\n"):
        if not remote_path:
            continue
        rel = remote_path.replace("/workspace/task/", "")
        local_path = dest / rel
        local_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            content = await sandbox.files.read(remote_path, format="bytes")
            local_path.write_bytes(content)
            downloaded.append(rel)
        except Exception as e:
            logger.warning("Failed to download %s: %s", remote_path, e)

    return downloaded


# ---------------------------------------------------------------------------
# Status — inter-node communication via status.json
# ---------------------------------------------------------------------------

# status.json lives at /workspace/task/status.json inside the sandbox.
# Each node reads it for context from previous nodes, then updates its section.
# The orchestrator also reads it after the DAG completes to write the final
# local copy. The "nodes" dict is the inter-agent communication channel.


async def read_sandbox_status(sandbox: AsyncSandbox) -> dict:
    """Read status.json from sandbox, or return empty default."""
    try:
        raw = await sandbox.files.read("/workspace/task/status.json", format="text")
        return json.loads(raw)
    except Exception:
        return {"nodes": {}}


async def update_sandbox_status(
    sandbox: AsyncSandbox, node: str, data: dict
) -> None:
    """Update one node's section in status.json inside the sandbox."""
    status = await read_sandbox_status(sandbox)
    if "nodes" not in status:
        status["nodes"] = {}
    status["nodes"][node] = data
    await sandbox.files.write(
        "/workspace/task/status.json",
        json.dumps(status, indent=2).encode(),
    )


def write_status_json(task_path: Path, result: WorkerResult, nodes: dict | None = None) -> None:
    """Write final validation result to local status.json.

    Schema v2: consistent structure with per-node provenance.
    Each node in `nodes` records: status, model, backend, time, notes.
    Top-level fields summarize the final outcome.
    """
    import datetime
    now = datetime.datetime.now().isoformat()

    # Merge existing status (preserve history from older runs)
    existing: dict = {}
    status_file = task_path / "status.json"
    if status_file.exists():
        try:
            existing = json.loads(status_file.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    # Build normalized status
    status: dict = {
        "schema_version": 2,
        "verdict": "pass" if result.valid else "fail",
        "nop_reward": result.nop_reward,
        "gold_reward": result.gold_reward,
        "validated_at": now,
        "total_time": result.total_time,
        "sandbox_id": result.sandbox_id,
        "backend": result.backend_name,
        "pipeline": result.mode or "agents",
    }
    if result.error:
        status["error"] = result.error[:500]
    if result.gemini_score is not None:
        status["rubric_icr"] = result.gemini_score

    # Nodes: per-step provenance (what model, what backend, what happened)
    merged_nodes = existing.get("nodes", {})
    if nodes:
        merged_nodes.update(nodes)
    status["nodes"] = merged_nodes

    # History: append this run to a compact log
    history = existing.get("history", [])
    history.append({
        "verdict": status["verdict"],
        "nop": result.nop_reward,
        "gold": result.gold_reward,
        "backend": result.backend_name,
        "time": result.total_time,
        "at": now,
    })
    # Keep last 5 runs
    status["history"] = history[-5:]

    status_file.write_text(json.dumps(status, indent=2))


# ---------------------------------------------------------------------------
# Core pipeline modes
# ---------------------------------------------------------------------------


async def run_task_validate(
    task_name: str,
    task_dir: Path,
    sandbox_sem: asyncio.Semaphore,
) -> WorkerResult:
    """Validate-only: upload existing task → Docker build → nop/gold test."""
    result = WorkerResult(task_ref=task_name, task_name=task_name, mode="validate")
    t_start = time.monotonic()

    task_path = task_dir / task_name
    if not (task_path / "environment" / "Dockerfile").exists():
        result.error = "Missing Dockerfile"
        result.total_time = time.monotonic() - t_start
        return result

    async with sandbox_sem:
        sandbox = None
        try:
            sandbox = await create_worker_sandbox()
            result.sandbox_id = sandbox.sandbox_id

            await upload_task_files(sandbox, task_path)

            t0 = time.monotonic()
            nop, gold, err = await validate_docker_in_sandbox(sandbox)
            result.nop_reward = nop
            result.gold_reward = gold
            result.validate_time = round(time.monotonic() - t0, 2)
            if err:
                result.error = err

            result.valid = (nop == 0.0 and gold == 1.0)

        except Exception as e:
            result.error = str(e)[:500]
        finally:
            if sandbox:
                try:
                    await sandbox.kill()
                except Exception:
                    pass

    result.total_time = round(time.monotonic() - t_start, 2)
    status = "PASS" if result.valid else "FAIL"
    logger.info("[%s] %s  nop=%.1f gold=%.1f  (%.1fs)%s",
                task_name, status, result.nop_reward, result.gold_reward,
                result.total_time, f"  err={result.error[:60]}" if result.error else "")
    return result


async def run_task_improve(
    task_name: str,
    task_dir: Path,
    pool,  # BackendPool | None
    sandbox_sem: asyncio.Semaphore,
) -> WorkerResult:
    """Improve + validate: upload → improve tests → Docker validate."""
    result = WorkerResult(task_ref=task_name, task_name=task_name, mode="improve")
    t_start = time.monotonic()

    task_path = task_dir / task_name

    async with sandbox_sem:
        sandbox = None
        backend = None
        try:
            # Acquire backend for LLM calls
            if pool:
                backend_ctx = pool.acquire()
                backend = await backend_ctx.__aenter__()
                backend_env = backend.subprocess_env()
                result.backend_name = backend.name
            else:
                backend_ctx = None
                backend_env = None

            sandbox = await create_worker_sandbox(backend_env=backend_env)
            result.sandbox_id = sandbox.sandbox_id

            await upload_task_files(sandbox, task_path)

            # Check if improvement needed
            needs_improve, reason = await check_test_quality(sandbox)
            if not needs_improve:
                result.improve_status = "skipped"
            else:
                t0 = time.monotonic()
                status, err = await run_improve_in_sandbox(sandbox)
                result.improve_status = status
                result.improve_time = round(time.monotonic() - t0, 2)
                if status == "rate_limited":
                    result.error = f"rate limited during improve: {err}"
                    if pool and backend:
                        pool.report_429(backend)
                    return result

            # Docker validate
            t0 = time.monotonic()
            nop, gold, err = await validate_docker_in_sandbox(sandbox)
            result.nop_reward = nop
            result.gold_reward = gold
            result.validate_time = round(time.monotonic() - t0, 2)
            if err:
                result.error = err

            result.valid = (nop == 0.0 and gold == 1.0)

            # Download improved files back if valid
            if result.valid:
                await download_task_files(sandbox, task_path)
                result.downloaded = True

            if pool and backend and "rate limited" not in (result.error or "").lower():
                pool.report_success(backend)

        except Exception as e:
            result.error = str(e)[:500]
        finally:
            if backend_ctx and backend:
                try:
                    await backend_ctx.__aexit__(None, None, None)
                except Exception:
                    pass
            if sandbox:
                try:
                    await sandbox.kill()
                except Exception:
                    pass

    result.total_time = round(time.monotonic() - t_start, 2)
    status = "PASS" if result.valid else "FAIL"
    logger.info("[%s] %s  nop=%.1f gold=%.1f improve=%s (%.1fs)",
                task_name, status, result.nop_reward, result.gold_reward,
                result.improve_status, result.total_time)
    return result


async def run_task_full(
    pr_ref: str,
    pool,  # BackendPool | None
    sandbox_sem: asyncio.Semaphore,
    task_dir: Path,
    agentmd: bool = False,
) -> WorkerResult:
    """Full pipeline: scaffold → improve → validate → download."""
    result = WorkerResult(task_ref=pr_ref, mode="full")
    t_start = time.monotonic()

    async with sandbox_sem:
        sandbox = None
        backend = None
        backend_ctx = None
        try:
            # Acquire backend
            if pool:
                backend_ctx = pool.acquire()
                backend = await backend_ctx.__aenter__()
                backend_env = backend.subprocess_env()
                result.backend_name = backend.name
            else:
                backend_env = None

            sandbox = await create_worker_sandbox(backend_env=backend_env)
            result.sandbox_id = sandbox.sandbox_id

            # Phase 1: Scaffold
            t0 = time.monotonic()
            scaffold_status, err = await run_scaffold_in_sandbox(sandbox, pr_ref, agentmd)
            result.scaffold_status = scaffold_status
            result.scaffold_time = round(time.monotonic() - t0, 2)
            if scaffold_status == "rate_limited":
                result.error = f"rate limited during scaffold: {err}"
                if pool and backend:
                    pool.report_429(backend)
                return result
            if scaffold_status != "ok":
                result.error = f"scaffold failed: {err}"
                return result

            # Phase 2: Quality gate
            needs_improve, reason = await check_test_quality(sandbox)

            # Phase 3: Improve (conditional)
            if needs_improve:
                t0 = time.monotonic()
                improve_status, err = await run_improve_in_sandbox(sandbox)
                result.improve_status = improve_status
                result.improve_time = round(time.monotonic() - t0, 2)
                if improve_status == "rate_limited":
                    result.error = f"rate limited during improve: {err}"
                    if pool and backend:
                        pool.report_429(backend)
                    return result
            else:
                result.improve_status = "skipped"

            # Phase 4: Docker validate
            t0 = time.monotonic()
            nop, gold, err = await validate_docker_in_sandbox(sandbox)
            result.nop_reward = nop
            result.gold_reward = gold
            result.validate_time = round(time.monotonic() - t0, 2)
            if err:
                result.build_status = "error" if "docker build" in err.lower() else "ok"
                result.error = err

            # Phase 5: Repair (conditional, once)
            if not (nop == 0.0 and gold == 1.0) and not result.error.startswith("docker build"):
                failure_type = classify_failure(nop, gold, result.error)
                t0 = time.monotonic()
                repair_status, repair_err = await run_repair_in_sandbox(
                    sandbox, failure_type, result.error or f"nop={nop}, gold={gold}"
                )
                result.repair_attempted = True
                result.repair_status = repair_status

                if repair_status == "ok":
                    # Re-validate after repair
                    nop2, gold2, err2 = await validate_docker_in_sandbox(sandbox)
                    result.nop_reward = nop2
                    result.gold_reward = gold2
                    if err2:
                        result.error = err2

            result.valid = (result.nop_reward == 0.0 and result.gold_reward == 1.0)

            # Phase 6: Download (only if valid)
            if result.valid:
                # Read task name from task.toml or derive from pr_ref
                task_name = await _read_task_name(sandbox, pr_ref)
                result.task_name = task_name
                dest = task_dir / task_name
                await download_task_files(sandbox, dest)
                result.downloaded = True
                logger.info("[%s] Downloaded validated task → %s", pr_ref, dest)

            if pool and backend and "rate limited" not in (result.error or "").lower():
                pool.report_success(backend)

        except Exception as e:
            result.error = str(e)[:500]
        finally:
            if backend_ctx and backend:
                try:
                    await backend_ctx.__aexit__(None, None, None)
                except Exception:
                    pass
            if sandbox:
                try:
                    await sandbox.kill()
                except Exception:
                    pass

    result.total_time = round(time.monotonic() - t_start, 2)
    status = "PASS" if result.valid else "FAIL"
    logger.info("[%s] %s  nop=%.1f gold=%.1f scaffold=%s improve=%s repair=%s (%.1fs)",
                pr_ref, status, result.nop_reward, result.gold_reward,
                result.scaffold_status, result.improve_status,
                result.repair_status or "n/a", result.total_time)
    return result


async def _read_task_name(sandbox: AsyncSandbox, pr_ref: str) -> str:
    """Read task name from task.toml or derive from PR ref."""
    code, stdout, _ = await run_cmd(
        sandbox,
        "ls /workspace/task/task.toml 2>/dev/null && "
        "python3 -c \"import tomllib; "
        "print(tomllib.load(open('/workspace/task/task.toml','rb')).get('name',''))\" 2>/dev/null",
    )
    if code == 0 and stdout.strip():
        lines = stdout.strip().split("\n")
        name = lines[-1].strip()
        if name:
            return name

    # Derive from PR ref: "owner/repo#123" → "repo-pr-123"
    if "#" in pr_ref:
        repo_part, pr_num = pr_ref.rsplit("#", 1)
        repo_name = repo_part.split("/")[-1] if "/" in repo_part else repo_part
        return f"{repo_name}-pr-{pr_num}"
    return pr_ref.replace("/", "-").replace("#", "-")


# ---------------------------------------------------------------------------
# Gemini judge (runs from orchestrator, not inside sandbox)
# ---------------------------------------------------------------------------


async def run_judge_in_sandbox(
    sandbox: AsyncSandbox,
) -> tuple[bool, float]:
    """Run the standardized rubric judge (taskforge/judge.py) inside the sandbox.

    Uses eval_manifest.yaml rubric rules — no hardcoded prompts here.
    The judge runs INSIDE the Docker container (where the repo lives),
    applies the gold solution, then evaluates rubric compliance.

    Returns (all_pass, icr_score). Skips if no rubric rules.
    """
    # First check if there are any rubric rules to evaluate
    code, stdout_check, _ = await run_cmd(
        sandbox,
        "python3 -c \"import yaml; m=yaml.safe_load(open('/workspace/task/eval_manifest.yaml')); "
        "r=m.get('rubric',[]); print(len(r) if r else 0)\"",
        timeout=10,
    )
    rubric_count = int(stdout_check.strip()) if code == 0 and stdout_check.strip().isdigit() else 0
    if rubric_count == 0:
        return True, 1.0  # No rubric rules to evaluate

    # Upload judge.py and config.py into the sandbox
    judge_py = ROOT / "taskforge" / "judge.py"
    config_py = ROOT / "taskforge" / "config.py"
    if not judge_py.exists():
        return True, 1.0

    await sandbox.files.write("/workspace/judge.py", judge_py.read_bytes())
    await sandbox.files.write("/workspace/taskforge/__init__.py", b"")
    await sandbox.files.write("/workspace/taskforge/config.py", config_py.read_bytes())

    # Find the repo workdir from the Dockerfile
    code, stdout, _ = await run_cmd(
        sandbox,
        "grep WORKDIR /workspace/task/environment/Dockerfile | tail -1 | awk '{print $2}'",
    )
    repo_dir = stdout.strip() or "/workspace"

    # Build the gold image (apply solve.sh inside Docker where the repo lives)
    # Use the already-built task-env-gold if it exists, otherwise build it
    code, _, _ = await run_cmd(
        sandbox,
        "docker image inspect task-env-gold >/dev/null 2>&1 || ("
        "  docker rm -f task-judge 2>/dev/null; "
        "  docker run --name task-judge "
        "    -v /workspace/task/solution:/solution:ro "
        "    task-env bash /solution/solve.sh && "
        "  docker commit task-judge task-env-gold && "
        "  docker rm task-judge"
        ")",
    )
    if code != 0:
        logger.warning("Judge: failed to build gold image")
        return True, 1.0

    # Run judge.py INSIDE the gold Docker container
    # Mount judge.py, config.py, and eval_manifest into the container
    code, stdout, stderr = await run_cmd(
        sandbox,
        "docker run --rm "
        "  -v /workspace/judge.py:/judge.py:ro "
        "  -v /workspace/taskforge:/taskforge:ro "
        "  -v /workspace/task/eval_manifest.yaml:/eval_manifest.yaml:ro "
        f"  -e GEMINI_API_KEY=$GEMINI_API_KEY "
        f"  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY "
        f"  task-env-gold python3 /judge.py "
        f"  --manifest /eval_manifest.yaml "
        f"  --repo {repo_dir}",
    )

    if code != 0:
        logger.warning("Judge failed: %s", (stderr or stdout)[:200])
        return True, 1.0  # Skip on error, don't block

    try:
        icr = float(stdout.strip().split('\n')[-1])
    except (ValueError, IndexError):
        return True, 1.0

    logger.info("  Rubric judge ICR: %.2f", icr)
    return icr >= 0.8, icr  # Pass if 80%+ of rubric rules satisfied


async def run_enrich_p2p_in_sandbox(sandbox: AsyncSandbox) -> tuple[str, str]:
    """Agentic claude -p node: discover repo CI/CD and add p2p tests.
    Uses the prompt at taskforge/prompts/enrich_p2p.md.
    Returns (status, error)."""
    prompt_file = ROOT / "taskforge" / "prompts" / "enrich_p2p.md"
    if not prompt_file.exists():
        return "skipped", "prompt file missing"

    prompt = prompt_file.read_text()
    await sandbox.files.write("/workspace/enrich_p2p_prompt.md", prompt.encode())

    code, stdout, stderr = await run_cmd(
        sandbox,
        "cat /workspace/enrich_p2p_prompt.md | claude -p "
        "--dangerously-skip-permissions --model opus "
        "--output-format json",
        

        user="worker",
    )

    if code != 0:
        combined = stdout + stderr
        if "429" in combined or "Rate limit" in combined or "hit your limit" in combined.lower():
            return "rate_limited", combined[:500]
        return "error", combined[:500]
    return "ok", ""


# ---------------------------------------------------------------------------
# Agent-chain pipeline: focused agents, each with Docker access
# ---------------------------------------------------------------------------


async def _run_agent(
    sandbox: AsyncSandbox,
    prompt_name: str,
) -> tuple[str, str, str]:
    """Run a claude -p agent with a prompt file. Returns (status, stdout, stderr).
    No timeout — agents run until completion."""
    prompt_file = ROOT / "taskforge" / "prompts" / prompt_name
    if not prompt_file.exists():
        return "skipped", "", f"prompt file missing: {prompt_name}"

    prompt = prompt_file.read_text()
    await sandbox.files.write(f"/workspace/{prompt_name}", prompt.encode())

    code, stdout, stderr = await run_cmd(
        sandbox,
        f"cat /workspace/{prompt_name} | claude -p "
        f"--dangerously-skip-permissions --model opus "
        f"--output-format json",
        user="worker",
    )

    if code != 0:
        combined = stdout + stderr
        logger.warning("[%s] agent error (exit %d): %s", prompt_name, code, combined[:300])
        if "429" in combined or "Rate limit" in combined or "hit your limit" in combined.lower():
            return "rate_limited", stdout, stderr
        return "error", stdout, stderr
    return "ok", stdout, stderr


async def _run_agent_gemini(
    sandbox: AsyncSandbox,
    prompt_name: str,
) -> tuple[str, str, str]:
    """Run a claude -p agent routed through Gemini 3.1 Pro via litellm proxy.

    Used for rubric enrichment where Gemini's reasoning quality matters.
    Starts litellm proxy if not already running, then overrides
    ANTHROPIC_BASE_URL to route through Gemini instead of the default backend (Kimi).
    """
    prompt_file = ROOT / "taskforge" / "prompts" / prompt_name
    if not prompt_file.exists():
        return "skipped", "", f"prompt file missing: {prompt_name}"

    # Ensure litellm proxy is running (idempotent — skips if already up)
    proxy_ok = await _ensure_litellm_proxy(sandbox)
    if not proxy_ok:
        logger.warning("[%s] litellm proxy not available, falling back to default backend", prompt_name)
        return await _run_agent(sandbox, prompt_name)

    prompt = prompt_file.read_text()
    await sandbox.files.write(f"/workspace/{prompt_name}", prompt.encode())

    # Override env to route through litellm → Gemini instead of default backend.
    # Must clear ALL backend-specific env vars:
    # - ANTHROPIC_BASE_URL → litellm proxy
    # - ANTHROPIC_API_KEY/AUTH_TOKEN → dummy (litellm doesn't need auth)
    # - ANTHROPIC_DEFAULT_*_MODEL → unset (Kimi model names break litellm)
    code, stdout, stderr = await run_cmd(
        sandbox,
        f"cat /workspace/{prompt_name} | "
        f"env -u ANTHROPIC_DEFAULT_OPUS_MODEL -u ANTHROPIC_DEFAULT_SONNET_MODEL -u ANTHROPIC_DEFAULT_HAIKU_MODEL "
        f"ANTHROPIC_BASE_URL=http://localhost:4000 ANTHROPIC_API_KEY=dummy ANTHROPIC_AUTH_TOKEN=dummy "
        f"claude -p --dangerously-skip-permissions --model opus --output-format json",
        user="worker",
    )

    if code != 0:
        combined = stdout + stderr
        logger.warning("[%s] gemini agent error (exit %d): %s", prompt_name, code, combined[:300])
        if "429" in combined or "Rate limit" in combined or "hit your limit" in combined.lower():
            return "rate_limited", stdout, stderr
        return "error", stdout, stderr
    return "ok", stdout, stderr


async def run_task_agents(
    task_name: str,
    task_dir: Path,
    pool,  # BackendPool | None
    sandbox_sem: asyncio.Semaphore,
    pr_ref: str | None = None,
    agentmd: bool = False,
) -> WorkerResult:
    """Agent-chain pipeline. Each step is a focused claude -p agent
    with Docker access that iterates within its own scope:

      [Scaffold] → [P2P Enrich] → [Rubric Enrich] → [Improve] → [Validate+Fix] → [Rubric Judge]

    P2P discovers repo CI/CD and adds pass_to_pass tests.
    Rubric Enrich discovers agent config rules and adds rubric entries (only if empty).
    Validate+Fix builds Docker, runs NOP/Gold tests, fixes issues.
    Rubric Judge evaluates the enriched rubric rules against the gold solution.

    Each node stamps provenance: model, backend, time, notes.
    status.json is the inter-agent communication channel.
    """
    is_new = pr_ref is not None
    result = WorkerResult(
        task_ref=pr_ref or task_name,
        task_name=task_name,
        mode="agents",
    )
    t_start = time.monotonic()

    async with sandbox_sem:
        sandbox = None
        backend = None
        backend_ctx = None
        try:
            # Acquire backend
            if pool:
                backend_ctx = pool.acquire()
                backend = await backend_ctx.__aenter__()
                backend_env = backend.subprocess_env()
                result.backend_name = backend.name
            else:
                backend_env = None

            sandbox = await create_worker_sandbox(
                backend_env=backend_env,
            )
            result.sandbox_id = sandbox.sandbox_id

            # Upload judge.py so validate agent can use it
            judge_py = ROOT / "taskforge" / "judge.py"
            config_py = ROOT / "taskforge" / "config.py"
            if judge_py.exists():
                await sandbox.files.write("/workspace/judge.py", judge_py.read_bytes())
                await run_cmd(sandbox, "mkdir -p /workspace/taskforge")
                await sandbox.files.write("/workspace/taskforge/__init__.py", b"")
                await sandbox.files.write("/workspace/taskforge/config.py", config_py.read_bytes())

            # Resolve local destination
            dest = None if is_new else task_dir / task_name

            # ── Agent 0: Scaffold (new PRs only) ─────────────────
            if is_new:
                t0 = time.monotonic()
                s, err = await run_scaffold_in_sandbox(sandbox, pr_ref, agentmd)
                result.scaffold_status = s
                result.scaffold_time = round(time.monotonic() - t0, 2)
                if s == "rate_limited":
                    result.error = f"rate limited: {err}"
                    result.total_time = round(time.monotonic() - t_start, 2)
                    if pool and backend:
                        pool.report_429(backend)
                    return result
                if s != "ok":
                    result.error = f"scaffold failed: {err}"
                    result.total_time = round(time.monotonic() - t_start, 2)
                    return result
                # Resolve dest from scaffolded task name
                name = await _read_task_name(sandbox, pr_ref)
                result.task_name = name
                dest = task_dir / name
                # Sync scaffold output
                await download_task_files(sandbox, dest)
                logger.info("[%s] scaffold complete, synced to %s", task_name, dest)
            else:
                await upload_task_files(sandbox, task_dir / task_name)
                result.scaffold_status = "skipped"

            # ── Clone repo into sandbox so agents can browse source/tests ──
            # Extract repo URL and commit from the Dockerfile
            code, repo_info, _ = await run_cmd(
                sandbox,
                "python3 -c \""
                "from pathlib import Path; import re; "
                "df = Path('/workspace/task/environment/Dockerfile').read_text(); "
                "repo = re.search(r'github\\.com/([^/]+/[^\\s]+?)(?:\\.git|[\\s]|$)', df); "
                "commit = re.search(r'(?:git checkout |git fetch.*origin |ARG\\s+BASE_COMMIT=)([a-f0-9]{7,})', df); "
                "print(repo.group(1) if repo else ''); "
                "print(commit.group(1) if commit else '')\"",
                timeout=10,
            )
            repo_url = repo_commit = ""
            if code == 0 and repo_info.strip():
                lines = repo_info.strip().split("\n")
                repo_url = lines[0].strip() if len(lines) > 0 else ""
                repo_commit = lines[1].strip() if len(lines) > 1 else ""

            if repo_url and repo_commit:
                # Validate repo_url format
                import re as _re
                if _re.match(r'^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$', repo_url):
                    clone_code, _, clone_err = await run_cmd(
                        sandbox,
                        f"git clone --filter=blob:none https://github.com/{repo_url}.git /workspace/repo "
                        f"&& cd /workspace/repo && git checkout {repo_commit}; "
                        f"chown -R worker:worker /workspace/repo 2>/dev/null || true",
                        timeout=180,
                    )
                    if clone_code == 0:
                        logger.info("[%s] repo cloned at %s to /workspace/repo", task_name, repo_commit[:8])
                    else:
                        logger.warning("[%s] repo clone failed: %s", task_name, (clone_err or "")[:200])
                else:
                    logger.warning("[%s] invalid repo_url format: %s", task_name, repo_url)

            # Refresh sandbox lifetime before agent chain
            try:
                await sandbox.set_timeout(3600)
            except Exception:
                pass

            # Helper: stamp a node with model/backend provenance
            backend_label = backend.name if backend else "none"
            model_label = (backend.resolve_model("opus") if backend else "unknown")

            def _stamp(node_name: str, status: str, elapsed: float, notes: str = ""):
                """Record provenance for one pipeline step."""
                return {
                    "status": status,
                    "model": model_label,
                    "backend": backend_label,
                    "time": round(elapsed, 2),
                    "notes": notes,
                }

            # Helper: abort early on rate limit, surface for retry
            def _check_rate_limit(agent_name: str, status: str):
                if status == "rate_limited":
                    if pool and backend:
                        pool.report_429(backend)
                    result.error = f"rate limited during {agent_name}"
                    return True
                return False

            # ── Agent 1: P2P Enrich (discover CI/CD, add p2p tests) ──
            t0 = time.monotonic()
            s, stdout, stderr = await _run_agent(sandbox, "enrich_p2p.md")
            p2p_time = time.monotonic() - t0
            await update_sandbox_status(sandbox, "p2p_enrichment", _stamp(
                "p2p_enrichment", s, p2p_time,
            ))
            if dest:
                await download_task_files(sandbox, dest)
                logger.info("[%s] p2p agent done (%s), synced", task_name, s)
            if _check_rate_limit("p2p_enrich", s):
                raise _RateLimited(result.error)

            # Refresh sandbox lifetime between agents
            try:
                await sandbox.set_timeout(3600)
            except Exception:
                pass

            # ── Agent 1b: Rubric Enrich → Gemini Validate → Fix loop ──
            # Kimi writes rubric → Gemini checks for hallucinations → Kimi fixes
            code, stdout_check, _ = await run_cmd(
                sandbox,
                "python3 -c \"import yaml; m=yaml.safe_load(open('/workspace/task/eval_manifest.yaml')); "
                "r=m.get('rubric',[]); print(len(r) if r else 0)\"",
                timeout=10,
            )
            rubric_count = int(stdout_check.strip()) if code == 0 and stdout_check.strip().isdigit() else 0
            if rubric_count == 0:
                # Step 1: Kimi writes initial rubric
                t0 = time.monotonic()
                s, stdout, stderr = await _run_agent(sandbox, "enrich_rubric.md")
                rubric_time = time.monotonic() - t0
                existing_node = (await read_sandbox_status(sandbox)).get("nodes", {}).get("rubric_enrichment", {})
                existing_node.update(_stamp("rubric_enrichment", s, rubric_time))
                await update_sandbox_status(sandbox, "rubric_enrichment", existing_node)
                if dest:
                    await download_task_files(sandbox, dest)
                    logger.info("[%s] rubric enrich done (%s), synced", task_name, s)
                if _check_rate_limit("rubric_enrich", s):
                    raise _RateLimited(result.error)

                try:
                    await sandbox.set_timeout(3600)
                except Exception:
                    pass

                # Step 2: Gemini validates rubric (programmatic + semantic)
                # Upload rubric_validator.py to sandbox
                validator_py = ROOT / "taskforge" / "rubric_validator.py"
                if validator_py.exists():
                    await sandbox.files.write("/workspace/rubric_validator.py", validator_py.read_bytes())

                    t0 = time.monotonic()
                    val_code, val_out, val_err = await run_cmd(
                        sandbox,
                        "python3 /workspace/rubric_validator.py "
                        "--task /workspace/task --repo /workspace/repo "
                        "--output /workspace/rubric_feedback.json",
                        timeout=120,
                    )
                    val_time = time.monotonic() - t0

                    # Read validation result
                    precision = 1.0
                    try:
                        feedback_raw = await sandbox.files.read("/workspace/rubric_feedback.json", format="text")
                        feedback = json.loads(feedback_raw)
                        precision = feedback.get("precision_score") or 0.0
                        summary = feedback.get("summary", "")
                        logger.info("[%s] rubric validation: precision=%.2f %s", task_name, precision, summary[:100])
                    except Exception:
                        feedback = {}

                    await update_sandbox_status(sandbox, "rubric_validate", {
                        **_stamp("rubric_validate", "ok" if val_code == 0 else "error", val_time),
                        "model": "gemini-3.1-pro",
                        "precision": precision,
                    })

                    # Step 3: If hallucinations found, Kimi fixes based on Gemini feedback
                    has_bad_rules = any(
                        r.get("verdict") in ("hallucinated", "redundant")
                        for r in feedback.get("rules", [])
                    )
                    if has_bad_rules and precision < 0.9:
                        try:
                            await sandbox.set_timeout(3600)
                        except Exception:
                            pass

                        t0 = time.monotonic()
                        s, stdout, stderr = await _run_agent(sandbox, "fix_rubric.md")
                        fix_time = time.monotonic() - t0
                        await update_sandbox_status(sandbox, "rubric_fix", _stamp(
                            "rubric_fix", s, fix_time,
                            f"precision was {precision:.2f}, fixing hallucinated rules",
                        ))
                        if dest:
                            await download_task_files(sandbox, dest)
                            logger.info("[%s] rubric fix done (%s), synced", task_name, s)
                        if _check_rate_limit("rubric_fix", s):
                            raise _RateLimited(result.error)

                    if dest:
                        await download_task_files(sandbox, dest)

                try:
                    await sandbox.set_timeout(3600)
                except Exception:
                    pass

            # ── Agent 2: Improve tests (skip if already good) ────
            needs_improve, reason = await check_test_quality(sandbox)
            if needs_improve:
                t0 = time.monotonic()
                s, stdout, stderr = await _run_agent(sandbox, "improve_tests.md")
                improve_time = time.monotonic() - t0
                result.improve_status = s
                result.improve_time = round(improve_time, 2)
                await update_sandbox_status(sandbox, "improve", _stamp(
                    "improve", s, improve_time, reason,
                ))
                if dest:
                    await download_task_files(sandbox, dest)
                    logger.info("[%s] improve agent done (%s), synced", task_name, s)
                if _check_rate_limit("improve", s):
                    raise _RateLimited(result.error)
            else:
                result.improve_status = "skipped"
                await update_sandbox_status(sandbox, "improve", _stamp(
                    "improve", "skipped", 0, reason,
                ))

            try:
                await sandbox.set_timeout(3600)
            except Exception:
                pass

            # ── Agent 3: Validate + Fix (the core agent) ─────────
            t0 = time.monotonic()
            s, stdout, stderr = await _run_agent(sandbox, "validate_and_fix.md")
            validate_time = time.monotonic() - t0
            result.validate_time = round(validate_time, 2)

            # Read validation results from status.json
            status = await read_sandbox_status(sandbox)
            val_node = status.get("nodes", {}).get("validate", {})
            result.nop_reward = val_node.get("nop_reward", -1.0)
            result.gold_reward = val_node.get("gold_reward", -1.0)
            result.valid = (result.nop_reward == 0.0 and result.gold_reward == 1.0)

            if _check_rate_limit("validate", s):
                raise _RateLimited(result.error)

            # Merge our provenance into the validate node (agent writes its own notes)
            val_node.update({"model": model_label, "backend": backend_label, "time": round(validate_time, 2)})
            await update_sandbox_status(sandbox, "validate", val_node)

            if dest:
                await download_task_files(sandbox, dest)
                logger.info("[%s] validate agent done (%s), synced", task_name, s)

            # Refresh sandbox before judge
            try:
                await sandbox.set_timeout(3600)
            except Exception:
                pass

            # ── Agent 4: Rubric Judge (if valid and has rubric rules) ──
            if result.valid:
                t0 = time.monotonic()
                judge_pass, icr = await run_judge_in_sandbox(sandbox)
                judge_time = time.monotonic() - t0
                result.gemini_score = icr
                await update_sandbox_status(sandbox, "rubric_judge", _stamp(
                    "rubric_judge",
                    "pass" if judge_pass else "fail",
                    judge_time,
                    f"ICR={icr:.2f}",
                ))
                if dest:
                    await download_task_files(sandbox, dest)
                    logger.info("[%s] rubric judge ICR=%.2f (%s)", task_name, icr,
                                "pass" if judge_pass else "fail")

            # ── Final status ─────────────────────────────────────
            result.total_time = round(time.monotonic() - t_start, 2)
            final_status = await read_sandbox_status(sandbox)
            nodes = final_status.get("nodes", {})
            if dest:
                write_status_json(dest, result, nodes=nodes)

            if pool and backend and "rate limited" not in (result.error or "").lower():
                pool.report_success(backend)

        except _RateLimited:
            # Error already set by _check_rate_limit — sync partial progress and bail fast
            if dest and sandbox:
                try:
                    await download_task_files(sandbox, dest)
                except Exception:
                    pass
            logger.warning("[%s] rate limited on %s, aborting for retry", task_name, result.backend_name)
        except Exception as e:
            result.error = str(e)[:500]
        finally:
            if backend_ctx and backend:
                try:
                    await backend_ctx.__aexit__(None, None, None)
                except Exception:
                    pass
            if sandbox:
                try:
                    await sandbox.kill()
                except Exception:
                    pass

    result.total_time = round(time.monotonic() - t_start, 2)
    status_str = "PASS" if result.valid else "FAIL"
    icr_str = f" icr={result.gemini_score:.2f}" if result.gemini_score is not None else ""
    logger.info(
        "[%s] %s  nop=%.1f gold=%.1f improve=%s%s backend=%s (%.1fs)",
        task_name, status_str, result.nop_reward, result.gold_reward,
        result.improve_status, icr_str, result.backend_name, result.total_time,
    )
    return result


# ---------------------------------------------------------------------------
# DAG pipeline (legacy): iterative validate → repair loop
# ---------------------------------------------------------------------------

MAX_DAG_ITERATIONS = 3


async def run_task_dag(
    task_name: str,
    task_dir: Path,
    pool,  # BackendPool | None
    sandbox_sem: asyncio.Semaphore,
    pr_ref: str | None = None,
    agentmd: bool = False,
) -> WorkerResult:
    """Iterative DAG pipeline. Each task loops through stages until all pass:

    [Scaffold] → [Lint] → [Improve] → [Docker Build] → [NOP Test] →
    [Gold Test] → [LLM Judge] → [Repair on failure] → loop back

    Max iterations: 3. Only downloads task files when ALL gates pass.
    """
    is_new = pr_ref is not None  # New task from PR vs existing task
    result = WorkerResult(
        task_ref=pr_ref or task_name,
        task_name=task_name,
        mode="dag",
    )
    t_start = time.monotonic()

    async with sandbox_sem:
        sandbox = None
        backend = None
        backend_ctx = None
        try:
            # Acquire backend
            if pool:
                backend_ctx = pool.acquire()
                backend = await backend_ctx.__aenter__()
                backend_env = backend.subprocess_env()
                result.backend_name = backend.name
            else:
                backend_env = None

            sandbox = await create_worker_sandbox(
                backend_env=backend_env,
            )
            result.sandbox_id = sandbox.sandbox_id

            # ── Node 0: Scaffold (only for new PRs) ──────────────────
            if is_new:
                t0 = time.monotonic()
                s, err = await run_scaffold_in_sandbox(sandbox, pr_ref, agentmd)
                result.scaffold_status = s
                result.scaffold_time = round(time.monotonic() - t0, 2)
                if s == "rate_limited":
                    result.error = f"rate limited during scaffold: {err}"
                    if pool and backend:
                        pool.report_429(backend)
                    return result
                if s != "ok":
                    result.error = f"scaffold failed: {err}"
                    return result
            else:
                # Upload existing task files
                task_path = task_dir / task_name
                await upload_task_files(sandbox, task_path)
                result.scaffold_status = "skipped"

            # Resolve local destination early so we can sync incrementally
            if is_new:
                dest = None  # Will resolve after scaffold creates task.toml
            else:
                dest = task_dir / task_name

            # ── Iterative validation loop ─────────────────────────────
            for iteration in range(MAX_DAG_ITERATIONS):
                gate_failed = ""

                # ── Node 1: Lint / quality gate ───────────────────────
                needs_improve, reason = await check_test_quality(sandbox)
                await update_sandbox_status(sandbox, "lint", {
                    "status": "needs_improve" if needs_improve else "ok",
                    "notes": reason,
                })

                # ── Node 2: Improve tests (if needed) ────────────────
                if needs_improve:
                    t0 = time.monotonic()
                    s, err = await run_improve_in_sandbox(sandbox)
                    result.improve_status = s
                    result.improve_time += round(time.monotonic() - t0, 2)
                    await update_sandbox_status(sandbox, "improve", {
                        "status": s,
                        "notes": err[:300] if s != "ok" else "tests upgraded with behavioral subprocess assertions",
                    })
                    # ── SYNC: always save improved tests locally ──
                    if s == "ok" and dest:
                        await download_task_files(sandbox, dest)
                        logger.info("[%s] synced improved tests to local", task_name)
                    if s == "rate_limited":
                        result.error = "rate limited during improve"
                        if pool and backend:
                            pool.report_429(backend)
                        break  # don't return — still download what we have
                    if s != "ok":
                        gate_failed = f"improve_error: {err}"
                elif iteration == 0:
                    result.improve_status = "skipped"
                    await update_sandbox_status(sandbox, "improve", {
                        "status": "skipped",
                        "notes": "tests already have subprocess + behavioral assertions",
                    })

                # ── Node 3: Docker build + NOP + Gold tests ──────────
                if not gate_failed:
                    t0 = time.monotonic()
                    nop, gold, err = await validate_docker_in_sandbox(sandbox)
                    result.nop_reward = nop
                    result.gold_reward = gold
                    result.validate_time = round(time.monotonic() - t0, 2)

                    if err:
                        gate_failed = f"docker: {err}"
                        await update_sandbox_status(sandbox, "docker_validate", {
                            "status": "error",
                            "notes": err[:500],
                        })
                    elif nop != 0.0:
                        gate_failed = f"nop={nop} (expected 0)"
                        await update_sandbox_status(sandbox, "docker_validate", {
                            "status": "fail",
                            "nop_reward": nop, "gold_reward": gold,
                            "notes": f"NOP test returned {nop} — tests pass even without the fix. f2p tests are too weak or testing the wrong behavior.",
                        })
                    elif gold != 1.0:
                        gate_failed = f"gold={gold} (expected 1)"
                        await update_sandbox_status(sandbox, "docker_validate", {
                            "status": "fail",
                            "nop_reward": nop, "gold_reward": gold,
                            "notes": f"Gold test returned {gold} — tests fail after applying solve.sh. Either solve.sh is wrong, tests are too strict, or Dockerfile is missing deps.",
                        })
                    else:
                        await update_sandbox_status(sandbox, "docker_validate", {
                            "status": "pass",
                            "nop_reward": nop, "gold_reward": gold,
                            "notes": "NOP=0 (tests correctly fail on base), GOLD=1 (tests pass after fix).",
                        })

                # ── Node 4: Rubric Judge (standardized, uses judge.py) ──
                if not gate_failed:
                    judge_pass, icr = await run_judge_in_sandbox(sandbox)
                    result.gemini_score = icr
                    await update_sandbox_status(sandbox, "rubric_judge", {
                        "status": "pass" if judge_pass else "fail",
                        "icr": icr,
                        "notes": f"ICR={icr:.2f}. " + ("All rubric rules satisfied." if judge_pass else "Some rubric rules failed — config/doc edits may be incomplete."),
                    })
                    if not judge_pass:
                        gate_failed = f"rubric_fail: ICR={icr:.2f} (need >=0.80)"

                # ── Node 5: P2P Enrichment (agentic, first iteration only)
                if not gate_failed and iteration == 0:
                    p2p_status, p2p_err = await run_enrich_p2p_in_sandbox(sandbox)
                    await update_sandbox_status(sandbox, "p2p_enrichment", {
                        "status": p2p_status,
                        "notes": p2p_err[:300] if p2p_status != "ok" else "added repo CI/CD tests as p2p gates",
                    })
                    if p2p_status == "ok":
                        # ── SYNC: save enriched tests locally ──
                        if dest:
                            await download_task_files(sandbox, dest)
                            logger.info("[%s] synced p2p-enriched tests to local", task_name)
                        # Re-validate after adding p2p tests
                        logger.info("[%s] P2P enriched, re-validating...", task_name)
                        t0 = time.monotonic()
                        nop, gold, err = await validate_docker_in_sandbox(sandbox)
                        result.nop_reward = nop
                        result.gold_reward = gold
                        result.validate_time += round(time.monotonic() - t0, 2)
                        if err:
                            gate_failed = f"docker_after_p2p: {err}"
                        elif nop != 0.0:
                            gate_failed = f"nop_after_p2p={nop} (expected 0)"
                        elif gold != 1.0:
                            gate_failed = f"gold_after_p2p={gold} (expected 1)"
                        if gate_failed:
                            await update_sandbox_status(sandbox, "p2p_revalidate", {
                                "status": "fail",
                                "nop_reward": nop, "gold_reward": gold,
                                "notes": f"After adding p2p tests: {gate_failed}. New p2p tests may be failing — check if they need Dockerfile deps or if they're flaky.",
                            })
                    elif p2p_status == "rate_limited":
                        result.error = "rate limited during p2p enrichment"
                        if pool and backend:
                            pool.report_429(backend)
                        break  # don't return — still download what we have
                    # p2p error/skipped = non-fatal, continue

                # ── All gates passed? ─────────────────────────────────
                if not gate_failed:
                    result.valid = True
                    logger.info(
                        "[%s] ALL GATES PASSED on iteration %d",
                        task_name, iteration + 1,
                    )
                    break

                # ── Repair and retry ──────────────────────────────────
                if iteration < MAX_DAG_ITERATIONS - 1:
                    result.repair_attempted = True
                    failure_type = classify_failure(
                        result.nop_reward, result.gold_reward, gate_failed
                    )
                    logger.info(
                        "[%s] iter %d FAILED (%s), repairing...",
                        task_name, iteration + 1, gate_failed[:80],
                    )
                    await update_sandbox_status(sandbox, "repair", {
                        "status": "in_progress",
                        "iteration": iteration + 1,
                        "failure_type": failure_type,
                        "notes": f"Attempting repair for: {gate_failed}",
                    })
                    s, _ = await run_repair_in_sandbox(
                        sandbox, failure_type, gate_failed
                    )
                    result.repair_status = s
                    await update_sandbox_status(sandbox, "repair", {
                        "status": s,
                        "iteration": iteration + 1,
                        "failure_type": failure_type,
                        "notes": f"Repair {'succeeded' if s == 'ok' else 'failed'} for: {gate_failed}",
                    })
                    # ── SYNC: always save repair changes locally ──
                    if s == "ok" and dest:
                        await download_task_files(sandbox, dest)
                        logger.info("[%s] synced repair changes to local", task_name)
                    if s != "ok":
                        result.error = f"repair failed: {gate_failed}"
                        break
                else:
                    result.error = f"failed after {MAX_DAG_ITERATIONS} iterations: {gate_failed}"

            # ── ALWAYS download final state ───────────────────────────
            # Even failed tasks get their improvements saved locally.
            # Progress is cumulative — next run starts from improved state.
            final_status = await read_sandbox_status(sandbox)
            nodes = final_status.get("nodes", {})
            result._iteration = iteration + 1

            if is_new and not dest:
                name = await _read_task_name(sandbox, pr_ref)
                result.task_name = name
                dest = task_dir / name

            result.total_time = round(time.monotonic() - t_start, 2)
            if dest:
                await download_task_files(sandbox, dest)
                result.downloaded = True
                write_status_json(dest, result, nodes=nodes)
                if result.valid:
                    logger.info("[%s] VALID — downloaded to %s", task_name, dest)
                else:
                    logger.info("[%s] FAILED but progress saved to %s", task_name, dest)

            if pool and backend and "rate limited" not in (result.error or "").lower():
                pool.report_success(backend)

        except Exception as e:
            result.error = str(e)[:500]
        finally:
            if backend_ctx and backend:
                try:
                    await backend_ctx.__aexit__(None, None, None)
                except Exception:
                    pass
            if sandbox:
                try:
                    await sandbox.kill()
                except Exception:
                    pass

    result.total_time = round(time.monotonic() - t_start, 2)
    status = "PASS" if result.valid else "FAIL"
    logger.info(
        "[%s] %s  nop=%.1f gold=%.1f improve=%s repair=%s gemini=%s (%.1fs)",
        task_name, status, result.nop_reward, result.gold_reward,
        result.improve_status, result.repair_status or "n/a",
        f"{result.gemini_score:.0%}" if result.gemini_score is not None else "n/a",
        result.total_time,
    )
    return result


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


async def run_batch(
    items: list[dict | str],
    mode: str,
    pool,
    concurrency: int,
    task_dir: Path,
    agentmd: bool = False,
    max_retries: int = 2,
) -> list[WorkerResult]:
    """Dispatch items to E2B sandboxes via async queue with retry."""
    sandbox_sem = asyncio.Semaphore(concurrency)
    results: list[WorkerResult] = []
    results_lock = asyncio.Lock()

    queue: asyncio.Queue[tuple[str | dict, int]] = asyncio.Queue()
    for item in items:
        await queue.put((item, 0))

    total = len(items)
    done_count = 0

    async def worker():
        nonlocal done_count
        while True:
            try:
                item, retries = queue.get_nowait()
            except asyncio.QueueEmpty:
                return

            try:
                if mode == "validate":
                    task_name = item if isinstance(item, str) else item["task"]
                    r = await run_task_validate(task_name, task_dir, sandbox_sem)
                elif mode == "improve":
                    task_name = item if isinstance(item, str) else item["task"]
                    r = await run_task_improve(task_name, task_dir, pool, sandbox_sem)
                elif mode == "full":
                    pr_ref = item if isinstance(item, str) else item["pr_ref"]
                    r = await run_task_full(pr_ref, pool, sandbox_sem, task_dir, agentmd)
                elif mode == "dag":
                    if isinstance(item, dict) and "pr_ref" in item:
                        r = await run_task_dag(
                            "", task_dir, pool, sandbox_sem,
                            pr_ref=item["pr_ref"], agentmd=agentmd,
                        )
                    else:
                        task_name = item if isinstance(item, str) else item["task"]
                        r = await run_task_dag(
                            task_name, task_dir, pool, sandbox_sem,
                        )
                elif mode == "agents":
                    if isinstance(item, dict) and "pr_ref" in item:
                        r = await run_task_agents(
                            "", task_dir, pool, sandbox_sem,
                            pr_ref=item["pr_ref"], agentmd=agentmd,
                        )
                    else:
                        task_name = item if isinstance(item, str) else item["task"]
                        r = await run_task_agents(
                            task_name, task_dir, pool, sandbox_sem,
                        )
                else:
                    raise ValueError(f"Unknown mode: {mode}")

                # Check if we should retry (rate limited)
                if "rate limited" in (r.error or "").lower() and retries < max_retries:
                    logger.info("Re-enqueueing %s (retry %d/%d)", item, retries + 1, max_retries)
                    await queue.put((item, retries + 1))
                else:
                    async with results_lock:
                        results.append(r)
                        done_count += 1
                        if done_count % 10 == 0 or r.valid:
                            valid_count = sum(1 for x in results if x.valid)
                            logger.info("Progress: %d/%d done, %d valid", done_count, total, valid_count)

            except Exception as e:
                logger.error("Worker error for %s: %s", item, e)
                async with results_lock:
                    results.append(WorkerResult(
                        task_ref=str(item), mode=mode, error=str(e)[:500]
                    ))
                    done_count += 1

            queue.task_done()

    # Launch workers (more than concurrency to keep queue drained)
    worker_count = min(concurrency * 2, len(items))
    workers = [asyncio.create_task(worker()) for _ in range(worker_count)]
    await asyncio.gather(*workers)

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def collect_tasks(task_dir: Path, filter_pat: str | None, limit: int | None) -> list[str]:
    """Collect task names from directory."""
    tasks = sorted(
        d.name for d in task_dir.iterdir()
        if d.is_dir()
        and (d / "environment" / "Dockerfile").exists()
        and (d / "tests" / "test.sh").exists()
    )
    if filter_pat:
        import fnmatch
        tasks = [t for t in tasks if fnmatch.fnmatch(t, filter_pat)]
    if limit:
        tasks = tasks[:limit]
    return tasks


def load_pr_items(input_file: Path, offset: int = 0, limit: int | None = None) -> list[dict]:
    """Load PR references from JSONL file."""
    items = []
    for line in input_file.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError:
            items.append({"pr_ref": line})

    items = items[offset:]
    if limit:
        items = items[:limit]
    return items


async def async_main(args):
    if not os.environ.get("E2B_API_KEY"):
        print("E2B_API_KEY not set. Run: set -a && source .env && set +a")
        sys.exit(1)

    # Build/check template
    await ensure_template()

    # Set up pool
    pool = None
    if args.pool:
        from taskforge.backends import BackendPool, backends_from_env
        backends = backends_from_env()
        if backends:
            pool = BackendPool(backends)
            logger.info("Backend pool: %s", pool.names)
        else:
            logger.warning("No backends found, running without pool")

    task_dir = ROOT / args.task_dir

    if args.mode in ("validate", "improve", "dag", "agents"):
        if args.tasks:
            items = args.tasks.split(",")
        else:
            items = collect_tasks(task_dir, args.filter, args.limit)
        logger.info("Mode=%s, %d tasks, concurrency=%d", args.mode, len(items), args.concurrency)
    elif args.mode == "full":
        if not args.input:
            print("--input required for full mode")
            sys.exit(1)
        items = load_pr_items(Path(args.input), args.offset or 0, args.limit)
        logger.info("Mode=full, %d PRs, concurrency=%d", len(items), args.concurrency)
    else:
        print(f"Unknown mode: {args.mode}")
        sys.exit(1)

    wall_start = time.monotonic()
    results = await run_batch(
        items, args.mode, pool, args.concurrency, task_dir, args.agentmd
    )
    wall_time = time.monotonic() - wall_start

    # Summary
    valid = [r for r in results if r.valid]
    failed = [r for r in results if not r.valid and not r.error]
    errored = [r for r in results if r.error]

    print()
    print("=" * 80)
    print(f"  E2B WORKER BATCH COMPLETE ({args.mode})")
    print(f"  Tasks:     {len(results)}")
    print(f"  Valid:     {len(valid)}  (nop=0, gold=1)")
    print(f"  Invalid:   {len(failed)}")
    print(f"  Errors:    {len(errored)}")
    print(f"  Downloaded: {sum(1 for r in results if r.downloaded)}")
    print(f"  Wall time: {wall_time:.1f}s ({wall_time/60:.1f}m)")
    if results:
        print(f"  Throughput: {len(results) / wall_time * 60:.1f} tasks/min")
    if pool:
        print(f"  Pool:      {pool.stats()}")
    print("=" * 80)

    if errored[:10]:
        print("\n  ERRORS (first 10):")
        for r in errored[:10]:
            print(f"    {r.task_ref}: {r.error[:80]}")

    if failed[:10]:
        print("\n  INVALID (first 10):")
        for r in failed[:10]:
            print(f"    {r.task_ref}: nop={r.nop_reward}, gold={r.gold_reward}")

    # Write results
    log_dir = ROOT / "pipeline_logs"
    log_dir.mkdir(exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    results_file = log_dir / f"e2b_worker_{args.mode}_{ts}.json"
    output = {
        "mode": args.mode,
        "wall_time": round(wall_time, 2),
        "total": len(results),
        "valid": len(valid),
        "invalid": len(failed),
        "errors": len(errored),
        "tasks": [asdict(r) for r in results],
    }
    results_file.write_text(json.dumps(output, indent=2))
    print(f"\nResults: {results_file}")


def main():
    parser = argparse.ArgumentParser(description="Consolidated E2B pipeline")
    parser.add_argument("--mode", choices=["validate", "improve", "full", "dag", "agents"], required=True)
    parser.add_argument("--task-dir", default="harbor_tasks")
    parser.add_argument("--tasks", type=str, default=None, help="Comma-sep task names")
    parser.add_argument("--filter", type=str, default=None, help="Glob filter")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--offset", type=int, default=None)
    parser.add_argument("--input", type=str, default=None, help="JSONL file for full mode")
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--pool", action="store_true", help="Use multi-backend pool")
    parser.add_argument("--agentmd", action="store_true", help="AgentMD edit tasks")
    args = parser.parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
