"""Consolidated E2B pipeline: scaffold → quality → rubric → enrich → improve → validate → lint.

One E2B sandbox per task handles the full lifecycle. Only tasks that
pass Docker oracle (nop=0, gold=1) get downloaded locally.

Architecture: ONE DAG, entry point controlled by --start-at:

    scaffold → qgate → rubric → enrich → improve → validate → lint → download
      ^          ^        ^         ^         ^          ^
      start-at controls which node the task enters the DAG

Two CLI modes:
  - pipeline: the unified DAG (requires --pool for LLM backends)
  - docker-only: lightweight validation, no LLM (upload → Docker build → nop/gold)

Usage:
    # Docker-only validation (no LLM needed, fast)
    python -m taskforge.e2b_worker --mode docker-only \\
        --task-dir harbor_tasks --concurrency 50

    # Full pipeline from PRs (scaffold new tasks)
    python -m taskforge.e2b_worker --mode pipeline \\
        --input prs.jsonl --pool --concurrency 18

    # Re-run existing tasks from quality gate
    python -m taskforge.e2b_worker --mode pipeline --start-at qgate \\
        --task-dir harbor_tasks --pool --concurrency 18

    # Just improve + validate existing tasks
    python -m taskforge.e2b_worker --mode pipeline --start-at improve \\
        --task-dir harbor_tasks --pool --concurrency 18
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
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
SANDBOX_TIMEOUT = 3600  # seconds — refreshed before each agent step


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


class StartAt(str, Enum):
    """DAG entry point — which node a task starts at."""
    SCAFFOLD = "scaffold"
    QGATE = "qgate"
    RUBRIC = "rubric"
    ENRICH = "enrich"
    IMPROVE = "improve"
    VALIDATE = "validate"

    @classmethod
    def from_str(cls, s: str) -> "StartAt":
        try:
            return cls(s)
        except ValueError:
            raise ValueError(f"Invalid start_at: {s!r}. Must be one of: {[e.value for e in cls]}")

    def should_run(self, node: "StartAt") -> bool:
        """Return True if `node` should execute given this entry point.

        DAG order: scaffold < qgate < rubric < enrich < improve < validate
        A node runs if it is >= the entry point.
        """
        order = list(StartAt)
        return order.index(node) >= order.index(self)


class _RateLimited(Exception):
    """Raised when an agent hits LLM rate limit — triggers retry at batch level."""
    pass


@dataclass
class WorkerResult:
    task_ref: str
    task_name: str = ""
    mode: str = ""  # "pipeline" | "docker-only"
    start_at: str = ""
    backend_name: str = ""
    sandbox_id: str = ""
    scaffold_status: str = ""  # "ok" | "error" | "skipped" | "abandoned"
    scaffold_time: float = 0.0
    qgate_verdict: str = ""  # "passed" | "DELETE" | "skipped"
    rubric_status: str = ""  # "ok" | "abandoned" | "error" | "skipped"
    rubric_quality: str = ""  # "HIGH" | "MEDIUM" | "LOW" | "DELETE"
    improve_status: str = ""  # "ok" | "skipped" | "error"
    improve_time: float = 0.0
    nop_reward: float = -1.0
    gold_reward: float = -1.0
    validate_time: float = 0.0
    repair_attempted: bool = False
    repair_status: str = ""
    valid: bool = False  # nop==0 and gold==1
    downloaded: bool = False
    rubric_icr: float | None = None
    total_time: float = 0.0
    error: str = ""
    nodes: dict = field(default_factory=dict)


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

        # Ensure worker user owns workspace
        await run_cmd(sandbox, "chown -R worker:worker /workspace /logs/verifier", timeout=10)
        await run_cmd(sandbox, "usermod -aG docker worker 2>/dev/null || true", timeout=5)

        # Start litellm proxy if using Gemini as main backend
        if backend_env and backend_env.get("ANTHROPIC_BASE_URL") == "http://localhost:4000":
            await _ensure_litellm_proxy(sandbox)

        return sandbox

    # All retries exhausted
    logger.error("All %d IP probe retries failed, proceeding with blocked sandbox", max_ip_retries)
    return sandbox


async def _ensure_litellm_proxy(sandbox: AsyncSandbox) -> bool:
    """Start litellm proxy for Gemini routing if not already running."""
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
# File transfer
# ---------------------------------------------------------------------------


async def upload_task_files(sandbox: AsyncSandbox, task_path: Path) -> None:
    """Upload all task files from local dir to /workspace/task/ in sandbox."""
    for f in task_path.rglob("*"):
        if f.is_file():
            rel = f.relative_to(task_path)
            remote_path = f"/workspace/task/{rel}"
            await sandbox.files.write(remote_path, f.read_bytes())
    await run_cmd(sandbox, "chmod +x /workspace/task/solution/solve.sh /workspace/task/tests/test.sh 2>/dev/null || true")


async def download_task_files(sandbox: AsyncSandbox, dest: Path) -> list[str]:
    """Download all task files from /workspace/task/ to local dir."""
    dest.mkdir(parents=True, exist_ok=True)

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


async def upload_taskforge_modules(sandbox: AsyncSandbox) -> None:
    """Upload taskforge Python modules to sandbox for in-sandbox operations."""
    await run_cmd(sandbox, "mkdir -p /workspace/taskforge")
    await sandbox.files.write("/workspace/taskforge/__init__.py", b"")
    for py_name in [
        "gemini_rubric_constructor.py", "hierarchy_context.py",
        "quality_gate.py", "models.py", "config.py", "judge.py",
        "rubric_validator.py",
    ]:
        py_file = ROOT / "taskforge" / py_name
        if py_file.exists():
            await sandbox.files.write(
                f"/workspace/taskforge/{py_name}", py_file.read_bytes(),
            )
    judge_py = ROOT / "taskforge" / "judge.py"
    if judge_py.exists():
        await sandbox.files.write("/workspace/judge.py", judge_py.read_bytes())


# ---------------------------------------------------------------------------
# Status — inter-node communication via status.json
# ---------------------------------------------------------------------------


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
    """Write final validation result to local status.json."""
    import datetime
    now = datetime.datetime.now().isoformat()

    existing: dict = {}
    status_file = task_path / "status.json"
    if status_file.exists():
        try:
            existing = json.loads(status_file.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    status: dict = {
        "schema_version": 2,
        "valid": result.valid,
        "verdict": "pass" if result.valid else "fail",
        "nop_reward": result.nop_reward,
        "gold_reward": result.gold_reward,
        "validated_at": now,
        "total_time": result.total_time,
        "sandbox_id": result.sandbox_id,
        "backend": result.backend_name,
        "pipeline": result.mode,
        "start_at": result.start_at,
    }
    if result.error:
        status["error"] = result.error[:500]
    if result.rubric_icr is not None:
        status["rubric_icr"] = result.rubric_icr

    merged_nodes = existing.get("nodes", {})
    if nodes:
        merged_nodes.update(nodes)
    status["nodes"] = merged_nodes

    history = existing.get("history", [])
    history.append({
        "verdict": status["verdict"],
        "nop": result.nop_reward,
        "gold": result.gold_reward,
        "backend": result.backend_name,
        "time": result.total_time,
        "at": now,
    })
    status["history"] = history[-5:]

    status_file.write_text(json.dumps(status, indent=2))


# ---------------------------------------------------------------------------
# Pipeline node functions
#
# Each node has a clear contract:
#   Input:  sandbox with files at /workspace/task/
#   Output: modified files at /workspace/task/, status.json updated
#   Return: node-specific result data
#
# File exchange: ALL files stay in the sandbox until the final download.
# No intermediate downloads to local disk.
# ---------------------------------------------------------------------------


async def node_scaffold(
    sandbox: AsyncSandbox,
    pr_ref: str,
    agentmd: bool = False,
) -> tuple[str, str, str]:
    """Node 0: Scaffold a task from a PR reference.

    Reads: scaffold prompt template from local disk
    Writes: /workspace/task/* (all task files) in the sandbox
    Returns: (status, task_name, error)
    """
    if agentmd:
        prompt_file = ROOT / "taskforge" / "prompts" / "scaffold_agentmd.md"
    else:
        prompt_file = ROOT / "taskforge" / "prompts" / "scaffold.md"
    if not prompt_file.exists():
        prompt_file = ROOT / ".claude" / "commands" / "scaffold-task.md"
    prompt = prompt_file.read_text().replace("$ARGUMENTS", pr_ref)

    task_dir_name = "harbor_tasks_agentmd_edits" if agentmd else "harbor_tasks"
    prompt = prompt.replace("harbor_tasks/", f"{task_dir_name}/")

    await sandbox.files.write("/workspace/scaffold_prompt.md", prompt.encode())

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
            return "rate_limited", "", combined[:500]
        return "error", "", combined[:500]

    # Check if scaffold agent abandoned the task
    try:
        raw = await sandbox.files.read("/workspace/task/status.json", format="text")
        status_data = json.loads(raw)
        if status_data.get("abandoned"):
            reason = status_data.get("reason", "no reason given")
            return "abandoned", "", reason
    except Exception:
        pass

    # Verify task files were created — handle nested output from scaffold agent
    check_code, _, _ = await run_cmd(
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
            task_root = str(Path(find_out.strip().split("\n")[0]).parent.parent)
            await run_cmd(sandbox, f"cp -a {task_root}/* /workspace/task/ 2>/dev/null; "
                                   f"cp -a {task_root}/.[!.]* /workspace/task/ 2>/dev/null; true")
        else:
            # Check if files ended up nested under /workspace/task/<name>/
            find_code2, find_out2, _ = await run_cmd(
                sandbox,
                "find /workspace/task -name test_outputs.py -type f 2>/dev/null | head -3",
                timeout=10,
            )
            if find_out2.strip():
                nested_root = str(Path(find_out2.strip().split("\n")[0]).parent.parent)
                if nested_root != "/workspace/task":
                    await run_cmd(sandbox, f"cp -a {nested_root}/* /workspace/task/ 2>/dev/null; true")

        # Final verification
        check_code2, _, _ = await run_cmd(
            sandbox,
            "ls /workspace/task/tests/test_outputs.py /workspace/task/environment/Dockerfile "
            "/workspace/task/solution/solve.sh 2>&1",
            timeout=5,
        )
        if check_code2 != 0:
            return "error", "", f"scaffold did not create expected files. stdout: {stdout[:300]}"

    # Read task name from task.toml
    task_name = await _read_task_name(sandbox, pr_ref)
    return "ok", task_name, ""


async def node_qgate(sandbox: AsyncSandbox) -> tuple[str, list[str]]:
    """Node 1: Programmatic quality gate — runs INSIDE the sandbox.

    Reads: /workspace/task/eval_manifest.yaml (in sandbox)
    Returns: (verdict, flags) where verdict is "passed", "DELETE", or "error"

    IMPORTANT: This runs in the sandbox, not on the host, because for new tasks
    the files only exist in the sandbox at this point.
    """
    code, stdout, stderr = await run_cmd(
        sandbox,
        "cd /workspace && python3 -c \""
        "from taskforge.quality_gate import classify_task_fast; "
        "from pathlib import Path; import json; "
        "r = classify_task_fast(Path('/workspace/task')); "
        "print(json.dumps({'verdict': r.verdict, 'flags': r.flags}))\"",
        timeout=15,
    )
    if code != 0:
        logger.warning("Quality gate failed in sandbox: %s", (stderr or stdout)[:200])
        return "error", [f"sandbox_error: {(stderr or stdout)[:100]}"]

    try:
        last_line = stdout.strip().split("\n")[-1]
        data = json.loads(last_line)
        verdict = data.get("verdict", "")
        flags = data.get("flags", [])
        if verdict == "DELETE":
            return "DELETE", flags
        # verdict="" means "needs Gemini" which we treat as "passed" for the fast gate
        return "passed", flags
    except (json.JSONDecodeError, IndexError):
        return "error", [f"parse_error: {stdout[:100]}"]


async def node_rubric_loop(
    sandbox: AsyncSandbox,
    repo_url: str,
) -> tuple[str, str, str, int]:
    """Node 2: Gemini↔Kimi rubric+quality loop — runs INSIDE the sandbox.

    Reads: /workspace/task/eval_manifest.yaml, /workspace/repo/ (cloned repo)
    Writes: updated eval_manifest.yaml with rubrics + distractors
    Returns: (status, quality_verdict, abandon_reason, rounds)

    status: "ok" | "abandoned" | "error"
    """
    code, stdout, stderr = await run_cmd(
        sandbox,
        "cd /workspace && python3 -c \""
        "from taskforge.gemini_rubric_constructor import run_rubric_quality_loop, stamp_rubrics_to_manifest; "
        "from pathlib import Path; import json, os; "
        "key = os.environ.get('GEMINI_API_KEY', ''); "
        "r = run_rubric_quality_loop(Path('/workspace/task'), Path('/workspace/repo'), key, max_rounds=3); "
        "print(json.dumps({k: r.get(k) for k in "
        "['status','quality_verdict','quality_reasoning','meta_referential',"
        "'competing_principles','config_navigation','loop_metadata'] "
        "if r.get(k) is not None}, default=str)); "
        "stamp_rubrics_to_manifest(Path('/workspace/task'), r) if r.get('status') == 'ok' else None"
        "\"",
        timeout=300,  # up to 3 rounds of Gemini+Kimi
    )

    if code != 0:
        return "error", "", f"sandbox_error: {(stderr or stdout)[:200]}", 0

    try:
        last_line = stdout.strip().split("\n")[-1]
        data = json.loads(last_line)
        status = data.get("status", "error")
        quality_verdict = data.get("quality_verdict", "")
        lm = data.get("loop_metadata", {})
        if isinstance(lm, str):
            import ast
            try:
                lm = ast.literal_eval(lm)
            except Exception:
                lm = {}
        abandon_reason = lm.get("abandon_reason", "") if isinstance(lm, dict) else ""
        rounds = lm.get("rounds", 0) if isinstance(lm, dict) else 0
        return status, quality_verdict, abandon_reason, rounds
    except (json.JSONDecodeError, IndexError):
        return "error", "", f"parse_error: {stdout[:100]}", 0


async def node_clone_repo(sandbox: AsyncSandbox, task_name: str) -> tuple[str, str]:
    """Clone the task's source repo into /workspace/repo/ for rubric extraction.

    Reads: /workspace/task/environment/Dockerfile (parses repo URL + commit)
    Writes: /workspace/repo/ (cloned repo at base commit)
    Returns: (repo_url, repo_commit)
    """
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
        if re.match(r'^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$', repo_url):
            clone_code, _, clone_err = await run_cmd(
                sandbox,
                f"git clone --filter=blob:none https://github.com/{repo_url}.git /workspace/repo "
                f"&& cd /workspace/repo && git checkout {repo_commit}; "
                f"chown -R worker:worker /workspace/repo 2>/dev/null || true",
                timeout=180,
            )
            if clone_code == 0:
                logger.info("[%s] repo cloned at %s", task_name, repo_commit[:8])
            else:
                logger.warning("[%s] repo clone failed: %s", task_name, (clone_err or "")[:200])
                repo_url = ""  # Signal clone failed
        else:
            logger.warning("[%s] invalid repo_url format: %s", task_name, repo_url)
            repo_url = ""

    return repo_url, repo_commit


async def node_enrich_p2p(sandbox: AsyncSandbox) -> tuple[str, str]:
    """Node 3: P2P enrichment — discovers CI/CD, adds pass-to-pass tests.

    Reads: /workspace/task/*, /workspace/repo/
    Writes: updated test files, eval_manifest.yaml
    Returns: (status, error)
    """
    return await _run_agent(sandbox, "enrich_p2p.md")


async def node_check_test_quality(sandbox: AsyncSandbox) -> tuple[bool, str]:
    """Quality check on test_outputs.py — determines if improve node should run.

    Reads: /workspace/task/tests/test_outputs.py
    Returns: (needs_improve, reason)
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


async def node_improve_tests(sandbox: AsyncSandbox) -> tuple[str, str]:
    """Node 4: Improve tests — rewrites test_outputs.py with behavioral tests.

    Reads: /workspace/task/tests/test_outputs.py, /workspace/task/eval_manifest.yaml
    Writes: updated test_outputs.py, test.sh
    Returns: (status, error)
    """
    return await _run_agent(sandbox, "improve_tests.md")


async def node_validate_and_fix(sandbox: AsyncSandbox) -> tuple[str, str]:
    """Node 5: Validate + fix — Docker oracle (nop=0, gold=1) with one repair attempt.

    Reads: /workspace/task/* (Dockerfile, tests, solve.sh)
    Writes: updated status.json with nop_reward/gold_reward, possibly fixed files
    Returns: (status, error)
    """
    return await _run_agent(sandbox, "validate_and_fix.md")


async def node_validate_docker_only(
    sandbox: AsyncSandbox,
) -> tuple[float, float, str]:
    """Docker-only validation: build → nop test → gold test. No LLM.

    Reads: /workspace/task/environment/Dockerfile, tests/test.sh, solution/solve.sh
    Returns: (nop_reward, gold_reward, error_detail)
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

    # Apply gold solution
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


async def node_rubric_lint(sandbox: AsyncSandbox) -> tuple[int, list[str]]:
    """Node 6: Post-validation rubric linter — strips injection text.

    Reads: /workspace/task/eval_manifest.yaml
    Writes: cleaned eval_manifest.yaml (injection text removed)
    Returns: (injection_count, sample_texts)
    """
    lint_code, lint_out, _ = await run_cmd(
        sandbox,
        "python3 -c \""
        "import yaml, re, json; "
        "m = yaml.safe_load(open('/workspace/task/eval_manifest.yaml')); "
        "INJ = re.compile("
        "r'(?i)(?:CRITICAL\\s+(?:LLM\\s+)?INSTRUCTION|CRITICAL\\s+OVERRIDE|OVERRIDE\\s+(?:JUDGE\\s+)?INSTRUCTION)"
        "|(?:YOU\\s+MUST\\s+(?:RETURN|PASS|EVALUATE))"
        "|(?:IGNORE\\s+ALL\\s+(?:PREVIOUS|OTHER))"
        "|(?:the\\s+world\\s+will\\s+end)"
        "|(?:AUTOMATED\\s+TESTING\\s+BOT)'); "
        "hits = []; "
        "[hits.append(r.get('rule','')[:80]) for r in m.get('rubric',[]) if INJ.search(r.get('rule',''))]; "
        "[hits.append(d.get('rule','')[:80]) for d in m.get('distractors',[]) if INJ.search(d.get('rule',''))]; "
        "print(json.dumps({'injected': len(hits), 'samples': hits[:3]}))\"",
        timeout=10,
    )
    if lint_code != 0:
        return 0, []

    try:
        data = json.loads(lint_out.strip())
        injected = data.get("injected", 0)
        samples = data.get("samples", [])
    except (json.JSONDecodeError, ValueError):
        return 0, []

    if injected == 0:
        return 0, []

    # Strip injection text
    await run_cmd(
        sandbox,
        "python3 -c \""
        "import yaml, re; "
        "INJ = re.compile("
        "r'(?i)(?:CRITICAL\\s+(?:LLM\\s+)?INSTRUCTION.*|CRITICAL\\s+OVERRIDE.*|OVERRIDE\\s+(?:JUDGE\\s+)?INSTRUCTION.*"
        "|YOU\\s+MUST\\s+(?:RETURN|PASS|EVALUATE).*"
        "|IGNORE\\s+ALL\\s+(?:PREVIOUS|OTHER).*"
        "|IMPORTANT:\\s+OVERRIDE.*"
        "|Since\\s+this\\s+(?:is\\s+a\\s+)?(?:code-only|pure\\s+code).*MUST.*"
        "|the\\s+world\\s+will\\s+end.*"
        "|AUTOMATED\\s+TESTING\\s+BOT.*)'); "
        "m = yaml.safe_load(open('/workspace/task/eval_manifest.yaml')); "
        "for s in ['rubric','distractors']: "
        "  new=[]; "
        "  [new.append(dict(r, rule=INJ.sub('',r.get('rule','')).strip())) for r in m.get(s,[]) if INJ.sub('',r.get('rule','')).strip()]; "
        "  m[s]=new; "
        "open('/workspace/task/eval_manifest.yaml','w').write(yaml.dump(m,default_flow_style=False,sort_keys=False,allow_unicode=True))\"",
        timeout=10,
    )

    logger.warning("RUBRIC TAMPERING: %d injected rules cleaned", injected)
    return injected, samples


async def _run_agent(
    sandbox: AsyncSandbox,
    prompt_name: str,
) -> tuple[str, str]:
    """Run a claude -p agent with a prompt file. Returns (status, error)."""
    prompt_file = ROOT / "taskforge" / "prompts" / prompt_name
    if not prompt_file.exists():
        return "skipped", f"prompt file missing: {prompt_name}"

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
        if "429" in combined or "Rate limit" in combined or "hit your limit" in combined.lower():
            return "rate_limited", combined[:500]
        return "error", combined[:500]
    return "ok", ""


async def _read_reward(sandbox: AsyncSandbox) -> float:
    """Read reward.txt from sandbox. Returns -1 if missing/unreadable."""
    try:
        data = await sandbox.files.read("/logs/verifier/reward.txt", format="text")
        return float(data.strip())
    except Exception:
        return -1.0


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

    if "#" in pr_ref:
        repo_part, pr_num = pr_ref.rsplit("#", 1)
        repo_name = repo_part.split("/")[-1] if "/" in repo_part else repo_part
        return f"{repo_name}-pr-{pr_num}"
    return pr_ref.replace("/", "-").replace("#", "-")


def _refresh_timeout(sandbox: AsyncSandbox) -> None:
    """Best-effort sandbox timeout refresh (fire-and-forget)."""
    try:
        asyncio.ensure_future(sandbox.set_timeout(SANDBOX_TIMEOUT))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Unified pipeline: run_task()
# ---------------------------------------------------------------------------


async def run_task(
    task_ref: str,
    task_dir: Path,
    pool,  # BackendPool | None
    sandbox_sem: asyncio.Semaphore,
    *,
    start_at: StartAt = StartAt.SCAFFOLD,
    pr_ref: str | None = None,
    agentmd: bool = True,
    force: bool = False,
) -> WorkerResult:
    """Unified DAG pipeline — one function, entry point controlled by start_at.

    DAG nodes (each runs only if start_at <= node position):
      0. scaffold   — create task from PR (only if pr_ref provided)
      1. qgate      — fast programmatic quality gate (in sandbox)
      2. rubric     — Gemini↔Kimi rubric loop (in sandbox)
      3. enrich     — P2P enrichment (claude -p)
      4. improve    — test improvement (claude -p, conditional)
      5. validate   — Docker oracle + fix (claude -p)
      6. lint       — post-validation rubric linter (in sandbox)
      7. download   — only if valid (nop=0, gold=1)

    File exchange contract:
      - ALL files stay in /workspace/task/ inside the sandbox
      - NO intermediate downloads to local disk
      - Single download at the end, only for valid tasks
      - status.json is the inter-node communication channel
    """
    is_new = pr_ref is not None
    result = WorkerResult(
        task_ref=pr_ref or task_ref,
        task_name=task_ref if not is_new else "",
        mode="pipeline",
        start_at=start_at.value,
    )
    t_start = time.monotonic()

    async with sandbox_sem:
        sandbox = None
        backend = None
        backend_ctx = None
        dest: Path | None = None

        try:
            # ── Acquire backend ───────────────────────────────────
            needs_llm = start_at.should_run(StartAt.ENRICH)  # nodes 3+ need LLM
            if pool and needs_llm:
                backend_ctx = pool.acquire()
                backend = await backend_ctx.__aenter__()
                backend_env = backend.subprocess_env()
                result.backend_name = backend.name
            else:
                backend_env = None

            sandbox = await create_worker_sandbox(backend_env=backend_env)
            result.sandbox_id = sandbox.sandbox_id

            # Upload taskforge modules (needed for qgate + rubric nodes)
            await upload_taskforge_modules(sandbox)

            # Provenance helper
            backend_label = backend.name if backend else "none"
            model_label = (backend.resolve_model("opus") if backend else "unknown")

            def _stamp(node_name: str, status: str, elapsed: float, notes: str = ""):
                return {
                    "status": status,
                    "model": model_label,
                    "backend": backend_label,
                    "time": round(elapsed, 2),
                    "notes": notes,
                }

            # ── Node 0: Scaffold (new PRs only) ───────────────────
            if is_new and start_at == StartAt.SCAFFOLD:
                t0 = time.monotonic()
                s, name, err = await node_scaffold(sandbox, pr_ref, agentmd)
                elapsed = time.monotonic() - t0
                result.scaffold_status = s
                result.scaffold_time = round(elapsed, 2)

                if s == "rate_limited":
                    result.error = f"rate limited: {err}"
                    if pool and backend:
                        pool.report_429(backend)
                    raise _RateLimited(result.error)
                if s == "abandoned":
                    result.error = f"scaffold abandoned: {err}"
                    await update_sandbox_status(sandbox, "scaffold", _stamp("scaffold", s, elapsed, err))
                    result.total_time = round(time.monotonic() - t_start, 2)
                    return result
                if s != "ok":
                    result.error = f"scaffold failed: {err}"
                    result.total_time = round(time.monotonic() - t_start, 2)
                    return result

                result.task_name = name
                dest = task_dir / name
                await update_sandbox_status(sandbox, "scaffold", _stamp("scaffold", "ok", elapsed))
                logger.info("[%s] scaffold ok → %s", pr_ref, name)

                # Dedup check: skip if task already exists on disk (unless --force)
                if dest.exists() and not force:
                    result.error = "dedup: task already exists on disk"
                    result.total_time = round(time.monotonic() - t_start, 2)
                    logger.info("[%s] DEDUP: %s already exists, skipping", pr_ref, dest.name)
                    return result
            elif not is_new:
                # Existing task: upload files to sandbox
                dest = task_dir / task_ref
                if not dest.exists():
                    result.error = f"task dir not found: {dest}"
                    result.total_time = round(time.monotonic() - t_start, 2)
                    return result
                await upload_task_files(sandbox, dest)
                result.scaffold_status = "skipped"
            else:
                # is_new but start_at > SCAFFOLD — error, new tasks must scaffold
                result.error = f"new PR requires start_at=scaffold, got {start_at.value}"
                result.total_time = round(time.monotonic() - t_start, 2)
                return result

            _refresh_timeout(sandbox)

            # ── Clone repo (needed for rubric node) ───────────────
            repo_url = ""
            if start_at.should_run(StartAt.QGATE) and agentmd:
                repo_url, _ = await node_clone_repo(sandbox, result.task_name)

            # ── Node 1: Programmatic Quality Gate ─────────────────
            if start_at.should_run(StartAt.QGATE) and agentmd:
                t0 = time.monotonic()
                verdict, flags = await node_qgate(sandbox)
                elapsed = time.monotonic() - t0
                result.qgate_verdict = verdict

                await update_sandbox_status(sandbox, "quality_gate", _stamp(
                    "quality_gate", verdict, elapsed, f"flags={flags}"))

                if verdict == "DELETE":
                    result.error = f"quality_gate: DELETE ({flags})"
                    result.valid = False
                    result.total_time = round(time.monotonic() - t_start, 2)
                    logger.info("[%s] quality gate REJECTED: %s", result.task_name, flags)
                    # For existing tasks, write status so we know it was reviewed
                    if not is_new and dest:
                        write_status_json(dest, result)
                    return result

                logger.info("[%s] quality gate: %s flags=%s", result.task_name, verdict, flags)

            _refresh_timeout(sandbox)

            # ── Node 2: Gemini↔Kimi Rubric Loop ──────────────────
            if start_at.should_run(StartAt.RUBRIC) and agentmd and repo_url:
                t0 = time.monotonic()
                loop_status, quality_verdict, abandon_reason, rounds = await node_rubric_loop(
                    sandbox, repo_url)
                elapsed = time.monotonic() - t0

                result.rubric_status = loop_status
                result.rubric_quality = quality_verdict

                await update_sandbox_status(sandbox, "rubric_quality_loop", {
                    **_stamp("rubric_quality_loop", loop_status, elapsed,
                             f"verdict={quality_verdict} rounds={rounds}"),
                    "model": "gemini-3.1-pro + kimi-k2.5",
                    "quality_verdict": quality_verdict,
                    "loop_rounds": rounds,
                    "abandon_reason": abandon_reason,
                })
                logger.info("[%s] rubric loop: verdict=%s status=%s rounds=%d (%.1fs)",
                            result.task_name, quality_verdict, loop_status, rounds, elapsed)

                if loop_status == "abandoned":
                    result.error = f"abandoned: {abandon_reason}"
                    result.valid = False
                    result.total_time = round(time.monotonic() - t_start, 2)
                    if not is_new and dest:
                        write_status_json(dest, result)
                    logger.info("[%s] ABANDONED: %s", result.task_name, abandon_reason[:100])
                    return result

            _refresh_timeout(sandbox)

            # ── Node 3: P2P Enrich ────────────────────────────────
            if start_at.should_run(StartAt.ENRICH):
                t0 = time.monotonic()
                s, err = await node_enrich_p2p(sandbox)
                elapsed = time.monotonic() - t0

                await update_sandbox_status(sandbox, "p2p_enrichment", _stamp(
                    "p2p_enrichment", s, elapsed))
                logger.info("[%s] p2p enrich: %s (%.1fs)", result.task_name, s, elapsed)

                if s == "rate_limited":
                    if pool and backend:
                        pool.report_429(backend)
                    result.error = f"rate limited during p2p_enrich: {err}"
                    raise _RateLimited(result.error)

            _refresh_timeout(sandbox)

            # ── Node 4: Improve Tests (conditional) ───────────────
            if start_at.should_run(StartAt.IMPROVE):
                needs_improve, reason = await node_check_test_quality(sandbox)
                if needs_improve:
                    t0 = time.monotonic()
                    s, err = await node_improve_tests(sandbox)
                    elapsed = time.monotonic() - t0
                    result.improve_status = s
                    result.improve_time = round(elapsed, 2)

                    await update_sandbox_status(sandbox, "improve", _stamp(
                        "improve", s, elapsed, reason))
                    logger.info("[%s] improve: %s (%.1fs)", result.task_name, s, elapsed)

                    if s == "rate_limited":
                        if pool and backend:
                            pool.report_429(backend)
                        result.error = f"rate limited during improve: {err}"
                        raise _RateLimited(result.error)
                else:
                    result.improve_status = "skipped"
                    await update_sandbox_status(sandbox, "improve", _stamp(
                        "improve", "skipped", 0, reason))

            _refresh_timeout(sandbox)

            # ── Node 5: Validate + Fix ────────────────────────────
            if start_at.should_run(StartAt.VALIDATE):
                t0 = time.monotonic()
                s, err = await node_validate_and_fix(sandbox)
                elapsed = time.monotonic() - t0
                result.validate_time = round(elapsed, 2)

                # Read validation results from status.json
                status = await read_sandbox_status(sandbox)
                val_node = status.get("nodes", {}).get("validate", {})
                result.nop_reward = val_node.get("nop_reward", -1.0)
                result.gold_reward = val_node.get("gold_reward", -1.0)
                result.valid = (result.nop_reward == 0.0 and result.gold_reward == 1.0)

                if s == "rate_limited":
                    if pool and backend:
                        pool.report_429(backend)
                    result.error = f"rate limited during validate: {err}"
                    raise _RateLimited(result.error)

                val_node.update({"model": model_label, "backend": backend_label,
                                 "time": round(elapsed, 2)})
                await update_sandbox_status(sandbox, "validate", val_node)
                logger.info("[%s] validate: %s nop=%.1f gold=%.1f (%.1fs)",
                            result.task_name, s, result.nop_reward, result.gold_reward, elapsed)

            # ── Node 6: Rubric Lint ───────────────────────────────
            if result.valid and agentmd:
                injected, samples = await node_rubric_lint(sandbox)
                if injected > 0:
                    await update_sandbox_status(sandbox, "rubric_lint", {
                        "status": "cleaned",
                        "injected_count": injected,
                        "samples": samples,
                    })
                    logger.warning("[%s] RUBRIC TAMPERING: %d injected rules cleaned",
                                   result.task_name, injected)

            # ── Node 7: Download (ONCE, only if valid) ────────────
            result.total_time = round(time.monotonic() - t_start, 2)
            final_status = await read_sandbox_status(sandbox)
            result.nodes = final_status.get("nodes", {})

            if result.valid and dest:
                await download_task_files(sandbox, dest)
                write_status_json(dest, result, nodes=result.nodes)
                result.downloaded = True
                logger.info("[%s] PASS — downloaded to %s", result.task_name, dest)
            elif dest and not is_new:
                # Existing task: always write status even if failed
                write_status_json(dest, result, nodes=result.nodes)

            if pool and backend and "rate limited" not in (result.error or "").lower():
                pool.report_success(backend)

        except _RateLimited:
            result.total_time = round(time.monotonic() - t_start, 2)
            # On rate limit, sync partial progress for existing tasks
            if dest and not is_new and sandbox:
                try:
                    await download_task_files(sandbox, dest)
                    nodes = (await read_sandbox_status(sandbox)).get("nodes", {})
                    write_status_json(dest, result, nodes=nodes)
                except Exception:
                    pass
            logger.warning("[%s] rate limited on %s, aborting for retry",
                           result.task_name, result.backend_name)
        except Exception as e:
            result.error = str(e)[:500]
            result.total_time = round(time.monotonic() - t_start, 2)
            if dest and not is_new and sandbox:
                try:
                    write_status_json(dest, result)
                except Exception:
                    pass
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
    logger.info(
        "[%s] %s  nop=%.1f gold=%.1f improve=%s backend=%s start=%s (%.1fs)",
        result.task_name, status_str, result.nop_reward, result.gold_reward,
        result.improve_status, result.backend_name, result.start_at, result.total_time,
    )
    return result


# ---------------------------------------------------------------------------
# Docker-only mode: lightweight validation, no LLM
# ---------------------------------------------------------------------------


async def run_task_docker_only(
    task_name: str,
    task_dir: Path,
    sandbox_sem: asyncio.Semaphore,
) -> WorkerResult:
    """Docker-only: upload existing task → Docker build → nop/gold test. No LLM."""
    result = WorkerResult(task_ref=task_name, task_name=task_name, mode="docker-only")
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
            nop, gold, err = await node_validate_docker_only(sandbox)
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
    status_str = "PASS" if result.valid else "FAIL"
    logger.info("[%s] %s  nop=%.1f gold=%.1f  (%.1fs)%s",
                task_name, status_str, result.nop_reward, result.gold_reward,
                result.total_time, f"  err={result.error[:60]}" if result.error else "")

    # Write status to local disk
    write_status_json(task_path, result)
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
    *,
    start_at: StartAt = StartAt.SCAFFOLD,
    agentmd: bool = True,
    force: bool = False,
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
                if mode == "docker-only":
                    task_name = item if isinstance(item, str) else item.get("task", str(item))
                    r = await run_task_docker_only(task_name, task_dir, sandbox_sem)
                elif mode == "pipeline":
                    if isinstance(item, dict) and "pr_ref" in item:
                        # New PR: scaffold from scratch
                        r = await run_task(
                            "", task_dir, pool, sandbox_sem,
                            start_at=start_at,
                            pr_ref=item["pr_ref"],
                            agentmd=agentmd,
                            force=force,
                        )
                    else:
                        # Existing task
                        task_name = item if isinstance(item, str) else item.get("task", str(item))
                        r = await run_task(
                            task_name, task_dir, pool, sandbox_sem,
                            start_at=start_at,
                            agentmd=agentmd,
                            force=force,
                        )
                else:
                    raise ValueError(f"Unknown mode: {mode}")

                # Re-enqueue on rate limit
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

    await ensure_template()

    # Set up pool (only needed for pipeline mode with LLM nodes)
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

    # Resolve start_at
    start_at = StartAt.from_str(args.start_at) if args.start_at else None

    # Determine items: --input (JSONL) takes priority, then --tasks, then scan dirs
    # CRITICAL: --input MUST be checked first — the old code had a bug where
    # mode=agents ignored --input and always scanned existing dirs.
    if args.input:
        items = load_pr_items(Path(args.input), args.offset or 0, args.limit)
        if start_at is None:
            start_at = StartAt.SCAFFOLD
        logger.info("Mode=%s, start_at=%s, %d PRs from %s, concurrency=%d",
                     args.mode, start_at.value, len(items), args.input, args.concurrency)
    elif args.tasks:
        items = args.tasks.split(",")
        if start_at is None:
            start_at = StartAt.VALIDATE
        logger.info("Mode=%s, start_at=%s, %d tasks, concurrency=%d",
                     args.mode, start_at.value, len(items), args.concurrency)
    else:
        items = collect_tasks(task_dir, args.filter, args.limit)
        if start_at is None:
            start_at = StartAt.VALIDATE
        logger.info("Mode=%s, start_at=%s, %d tasks from %s, concurrency=%d",
                     args.mode, start_at.value, len(items), task_dir, args.concurrency)

    if not items:
        print("No items to process. Check --input, --tasks, or task directory.")
        sys.exit(1)

    wall_start = time.monotonic()
    results = await run_batch(
        items, args.mode, pool, args.concurrency, task_dir,
        start_at=start_at, agentmd=args.agentmd, force=args.force,
    )
    wall_time = time.monotonic() - wall_start

    # Summary
    valid = [r for r in results if r.valid]
    failed = [r for r in results if not r.valid and not r.error]
    errored = [r for r in results if r.error]

    print()
    print("=" * 80)
    print(f"  E2B WORKER BATCH COMPLETE ({args.mode}, start_at={start_at.value})")
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
        "start_at": start_at.value,
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
    parser.add_argument("--mode", choices=["pipeline", "docker-only"], required=True,
                        help="pipeline: unified DAG (LLM + Docker). docker-only: no LLM, just Docker oracle")
    parser.add_argument("--start-at", type=str, default=None,
                        choices=["scaffold", "qgate", "rubric", "enrich", "improve", "validate"],
                        help="DAG entry point (default: scaffold for --input, validate for existing tasks)")
    parser.add_argument("--task-dir", default="harbor_tasks")
    parser.add_argument("--tasks", type=str, default=None, help="Comma-sep task names")
    parser.add_argument("--filter", type=str, default=None, help="Glob filter")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--offset", type=int, default=None)
    parser.add_argument("--input", type=str, default=None, help="JSONL file with PR refs")
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--pool", action="store_true", help="Use multi-backend pool")
    parser.add_argument("--agentmd", action="store_true", help="Enable agentmd quality nodes (qgate, rubric, lint)")
    parser.add_argument("--force", action="store_true", help="Force re-process even if task exists on disk")
    args = parser.parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
