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
        --task-dir markdown_following --concurrency 50

    # Full pipeline from PRs (scaffold new tasks)
    python -m taskforge.e2b_worker --mode pipeline \\
        --input prs.jsonl --pool --concurrency 18

    # Re-run existing tasks from quality gate
    python -m taskforge.e2b_worker --mode pipeline --start-at qgate \\
        --task-dir markdown_following --pool --concurrency 18

    # Just improve + validate existing tasks
    python -m taskforge.e2b_worker --mode pipeline --start-at improve \\
        --task-dir markdown_following --pool --concurrency 18
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import atexit
import os
import random
import re
import signal
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path

from e2b import AsyncSandbox, AsyncTemplate, Template, Sandbox
from e2b.sandbox.commands.command_handle import CommandExitException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = Path(__file__).resolve().parent / "e2b_template"
TEMPLATE_ALIAS = "harbor-worker-v4"  # bumped from v3 to force rebuild with
# claude-code 2.1.119 (was 2.1.97 in v3 — broke Opus 4.7 thinking format)
SANDBOX_TIMEOUT = 5400  # seconds — refreshed before each agent step. Bumped
# from 3600 because oneshot fix_task_quality routinely runs >1h on complex
# repos (npm install, large repo clones, iterative Docker builds) — the old
# value killed long-running agents at exactly the 1h mark.


# ---------------------------------------------------------------------------
# Robust sandbox cleanup — prevent orphans from filling 100-sandbox quota
# ---------------------------------------------------------------------------


def cleanup_orphan_sandboxes(api_key: str | None = None, reason: str = "cleanup") -> int:
    """Kill all E2B sandboxes on the account. Returns count killed.

    Use at startup (clean slate) and on signal/exit (release quota).
    This is sync so it works in signal handlers and atexit hooks.
    """
    api_key = api_key or os.environ.get("E2B_API_KEY", "")
    if not api_key:
        return 0

    killed = 0
    try:
        p = Sandbox.list(api_key=api_key)
        while True:
            items = p.next_items()
            if not items:
                break
            for s in items:
                try:
                    Sandbox.kill(s.sandbox_id, api_key=api_key)
                    killed += 1
                except Exception:
                    pass
            if not p.has_next:
                break
    except Exception as e:
        logger.warning("Failed to cleanup sandboxes (%s): %s", reason, e)

    if killed > 0:
        logger.info("[%s] Killed %d orphaned sandboxes", reason, killed)
    return killed


def install_cleanup_handlers(api_key: str | None = None) -> None:
    """Install signal + atexit handlers to clean up sandboxes on exit.

    Handles: SIGTERM, SIGINT, normal exit. Does NOT handle SIGKILL (kill -9)
    since the process can't catch that — but atexit covers most crashes.

    On signal, we set a flag and let asyncio's default handler raise
    KeyboardInterrupt so the main loop's finally blocks can run their
    individual sandbox.kill() calls first. Then atexit runs bulk cleanup
    as a safety net.
    """
    api_key = api_key or os.environ.get("E2B_API_KEY", "")
    if not api_key:
        return

    cleaned = [False]

    def _cleanup_once(reason: str):
        if cleaned[0]:
            return
        cleaned[0] = True
        # Release in-flight claims FIRST so a fast restart can pick them up
        # immediately, even if sandbox cleanup hangs or fails.
        try:
            release_inflight_claims(reason=reason)
        except Exception as e:
            logger.warning("Claim release failed during %s: %s", reason, e)
        try:
            cleanup_orphan_sandboxes(api_key, reason=reason)
        except Exception as e:
            logger.warning("Cleanup failed during %s: %s", reason, e)

    # Register atexit first — runs on any exit path including KeyboardInterrupt
    atexit.register(_cleanup_once, reason="atexit")

    # For SIGTERM, convert to KeyboardInterrupt so asyncio finally blocks run.
    # SIGINT (Ctrl+C) already does this naturally — don't override it.
    def _sigterm_handler(signum, frame):
        logger.warning("Received SIGTERM, draining then cleaning up...")
        # Raise KeyboardInterrupt in main thread — asyncio will cancel tasks
        # and run their finally blocks (including per-sandbox kill)
        raise KeyboardInterrupt("SIGTERM received")

    signal.signal(signal.SIGTERM, _sigterm_handler)
    # SIGINT (Ctrl+C) already raises KeyboardInterrupt; no need to handle


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


class StartAt(str, Enum):
    """DAG entry point — which node a task starts at.

    Supported (canonical):
      ONESHOT_REPAIR — 2-node pipeline: qgate + fix_task_quality. Opus owns
                       Docker validate + give-up internally. Default for
                       repairing existing tasks. ~85-90% pass, ~$5/task.
      SCAFFOLD       — initial PR → task generation. Still in use for new tasks.

    Deprecated (kept for backward compat with in-flight runs; prefer
    ONESHOT_REPAIR which folds these into one Opus call):
      QGATE, RUBRIC, ENRICH    — sub-stages of the older multi-node DAG.
      IMPROVE, FIX_QUALITY     — old test-improvement / quality-fix entry
                                  points. The 4-Opus-call chain they trigger
                                  (fix → validate_and_fix → quality_judge →
                                  instruction_reconcile → tests_rewrite) is
                                  redundant: validate_and_fix often overwrites
                                  fix_task_quality's correct verdict. Use
                                  ONESHOT_REPAIR instead.
      VALIDATE, JUDGE          — retrofit-only entry points; bypassed by
                                  ONESHOT_REPAIR.

    Canonical (one-call) modes:
      ONESHOT_SCAFFOLD — for NEW tasks from a PR ref. Runs scaffold.md
                          (which already does PR fetch → file generation →
                          Docker NOP/GOLD validate → self-audit), then
                          trusts the agent's scaffold_status.json verdict
                          and skips trailing nodes.
      ONESHOT_REPAIR   — for EXISTING tasks with quality flags. Same
                          pattern with fix_task_quality.md.
    """
    SCAFFOLD = "scaffold"
    QGATE = "qgate"           # deprecated — runs as part of ONESHOT_REPAIR
    RUBRIC = "rubric"         # deprecated
    ENRICH = "enrich"         # deprecated
    IMPROVE = "improve"       # deprecated
    FIX_QUALITY = "fix_quality"  # deprecated — use ONESHOT_REPAIR
    VALIDATE = "validate"     # deprecated
    JUDGE = "judge"           # deprecated
    ONESHOT_REPAIR = "oneshot_repair"  # canonical: qgate + fix_task_quality
    ONESHOT_SCAFFOLD = "oneshot_scaffold"  # canonical: one-call scaffold from PR
    ONESHOT_REPAIR_MANIFEST = "oneshot_repair_manifest"  # canonical: rewrite eval_manifest.yaml only, preserve tests/Dockerfile/solve.sh
    ONESHOT_FIX_DOCKERFILE = "oneshot_fix_dockerfile"    # canonical: fix Dockerfile rot from a GHA failure log; preserve tests/solve/instruction
    ONESHOT_REPAIR_FULL = "oneshot_repair_full"          # canonical: free-form Dockerfile + tests/test_outputs.py edits to satisfy Docker oracle (nop=0, gold=1)
    ONESHOT_FULL_QA_REVIEW = "oneshot_full_qa_review"    # canonical: 4-dimension QA review (CI/CD, functional tests, instruction rubrics, Docker) + auto-fix + Docker oracle gate

    @classmethod
    def from_str(cls, s: str) -> "StartAt":
        try:
            return cls(s)
        except ValueError:
            raise ValueError(f"Invalid start_at: {s!r}. Must be one of: {[e.value for e in cls]}")

    def should_run(self, node: "StartAt") -> bool:
        """Return True if `node` should execute given this entry point.

        DAG order: scaffold < qgate < rubric < enrich < improve < validate < judge
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
    # Quality judge / reconcile (20-rubric pipeline revamp)
    judge_status: str = ""              # "ok" | "error" | "skipped"
    judge_summary: dict = field(default_factory=dict)
    reconcile_status: str = ""          # "ok" | "abandoned" | "error" | "rate_limited"
    reconcile_time: float = 0.0
    reconcile_outcome: dict = field(default_factory=dict)
    judge_status_post: str = ""
    judge_summary_post: dict = field(default_factory=dict)
    # Test rewrite (runs when judge flags test-design rubrics)
    tests_rewrite_status: str = ""      # "ok" | "abandoned" | "error" | "rate_limited"
    tests_rewrite_time: float = 0.0
    tests_rewrite_outcome: dict = field(default_factory=dict)
    judge_status_post_tests: str = ""
    judge_summary_post_tests: dict = field(default_factory=dict)
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
    timeout: int = SANDBOX_TIMEOUT,
    max_ip_retries: int = 10,
) -> AsyncSandbox:
    """Create sandbox from harbor-worker template with env vars injected.
    Retries sandbox creation if the egress IP is blocked by the LLM provider.
    timeout = sandbox lifetime in seconds (default 1 hour)."""
    envs = {
        "GH_TOKEN": os.environ.get("GH_TOKEN", ""),
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", ""),
        # JUDGE_API_KEY is the REAL Anthropic key — routed directly to api.anthropic.com.
        # Kept separate from ANTHROPIC_API_KEY so the pool backend (MiniMax/GLM/Kimi)
        # can override ANTHROPIC_API_KEY without disturbing the judge.
        "JUDGE_API_KEY": os.environ.get("JUDGE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY", ""),
    }
    if backend_env:
        envs.update(backend_env)

    # OAuth fix: Claude Code CLI reads auth from ~/.claude/.credentials.json,
    # NOT from the CLAUDE_ACCESS_TOKEN env var alone. If the backend uses
    # bearer auth (OAuth), we'll write the credentials file to the sandbox
    # after creation. Cache it here so we don't re-read per sandbox.
    _oauth_creds_json: bytes | None = None
    if backend_env and backend_env.get("CLAUDE_ACCESS_TOKEN"):
        for candidate in (".credentials.json", ".credentials_backup.json"):
            creds_path = Path.home() / ".claude" / candidate
            if creds_path.exists():
                try:
                    _oauth_creds_json = creds_path.read_bytes()
                    break
                except Exception:
                    pass

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
                # Reject both 403 (IP blocked) and 400/429 (rate limited).
                # Fireworks returns rate limits as HTTP 400 with "rate limit"
                # in the body (via LiteLLM proxy), not always as 429.
                if status_code in ("403", "400", "429"):
                    logger.warning(
                        "Sandbox %s rejected by Fireworks (%s), rotating IP (%d/%d)...",
                        sandbox.sandbox_id, status_code, ip_attempt + 1, max_ip_retries,
                    )
                    try:
                        await sandbox.kill()
                    except Exception:
                        pass
                    await asyncio.sleep(2)
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

        # Start litellm proxy if backend uses localhost:4000 (Gemini or Chutes)
        if backend_env and backend_env.get("ANTHROPIC_BASE_URL") == "http://localhost:4000":
            await _ensure_litellm_proxy(sandbox)

        # OAuth: write credentials file so `claude -p` can authenticate.
        # The CLI reads ~/.claude/.credentials.json, NOT CLAUDE_ACCESS_TOKEN env.
        # _run_agent runs as user "worker" (home=/home/worker), so that's the
        # primary path. Also write to root for any root-context commands.
        if _oauth_creds_json:
            try:
                await run_cmd(sandbox, "mkdir -p /home/worker/.claude /root/.claude", timeout=5)
                await sandbox.files.write("/home/worker/.claude/.credentials.json", _oauth_creds_json)
                await sandbox.files.write("/root/.claude/.credentials.json", _oauth_creds_json)
            except Exception as e:
                logger.warning("Failed to write OAuth credentials to sandbox: %s", e)

        return sandbox

    # All retries exhausted
    logger.error("All %d IP probe retries failed, proceeding with blocked sandbox", max_ip_retries)
    return sandbox


async def _ensure_litellm_proxy(sandbox: AsyncSandbox) -> bool:
    """Start litellm proxy for OpenAI-format backend routing if not already running.

    Supports Gemini (gemini/ prefix) and Chutes (openai/ prefix with api_base).
    The proxy translates requests so claude -p sees Anthropic format.
    """
    code, stdout, _ = await run_cmd(
        sandbox,
        'curl -s -o /dev/null -w "%{http_code}" http://localhost:4000/health 2>/dev/null || echo 000',
        timeout=5,
    )
    if stdout.strip() == "200":
        return True

    # Determine which backend to configure
    chutes_key = os.environ.get("CHUTES_API_KEY", "")
    chutes_model = os.environ.get("CHUTES_MODEL", "moonshotai/Kimi-K2.5-TEE")
    chutes_enabled = os.environ.get("CHUTES_ENABLED", "") == "1"
    gemini_key = os.environ.get("GEMINI_API_KEY", "")

    if chutes_key and chutes_enabled:
        # Chutes — OpenAI-compatible endpoint
        litellm_config = (
            'litellm_settings:\n'
            '  drop_params: true\n'
            'model_list:\n'
            '  - model_name: "claude-opus-4-6"\n'
            '    litellm_params:\n'
            f'      model: "openai/{chutes_model}"\n'
            f'      api_key: "{chutes_key}"\n'
            '      api_base: "https://llm.chutes.ai/v1"\n'
            '  - model_name: "claude-sonnet-4-6"\n'
            '    litellm_params:\n'
            f'      model: "openai/{chutes_model}"\n'
            f'      api_key: "{chutes_key}"\n'
            '      api_base: "https://llm.chutes.ai/v1"\n'
            '  - model_name: "opus"\n'
            '    litellm_params:\n'
            f'      model: "openai/{chutes_model}"\n'
            f'      api_key: "{chutes_key}"\n'
            '      api_base: "https://llm.chutes.ai/v1"\n'
        )
        backend_label = f"Chutes ({chutes_model})"
    elif gemini_key:
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
        backend_label = "Gemini 3.1 Pro"
    else:
        logger.warning("No CHUTES_API_KEY or GEMINI_API_KEY — cannot start litellm proxy")
        return False

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
            logger.info("Sandbox %s: litellm proxy -> %s ready", sandbox.sandbox_id, backend_label)
            return True

    logger.warning("Sandbox %s: litellm proxy failed to start after 40s", sandbox.sandbox_id)
    return False


# ---------------------------------------------------------------------------
# File transfer
# ---------------------------------------------------------------------------


async def upload_task_files(sandbox: AsyncSandbox, task_path: Path) -> None:
    """Upload all task files from local dir to /workspace/task/ in sandbox.

    Skips bulky build artifacts and stray clones of the upstream repo —
    the sandbox already has the repo cloned at base_commit per the Dockerfile.
    Uploading e.g. `gold-workspace/node_modules/` (40k+ files) starves
    concurrency for tens of minutes per task and adds zero value: the gold
    patch is in `solution/solve.sh`, which `git apply`s against the sandbox
    repo directly.
    """
    EXCLUDE_DIR_PARTS = {
        "node_modules", ".git", ".next", "target", "dist", "build",
        ".venv", "__pycache__", ".pytest_cache",
        # Stray gold-clones — the sandbox does its own clone
        "gold-workspace", "gold_workspace", "gold_repo", "gold-repo",
        "gold_workdir", "extracted",
    }
    for f in task_path.rglob("*"):
        if f.is_file():
            rel = f.relative_to(task_path)
            if any(part in EXCLUDE_DIR_PARTS for part in rel.parts):
                continue
            # Skip files >1 MB — likely a build artifact, not source
            try:
                if f.stat().st_size > 1_000_000:
                    continue
            except OSError:
                continue
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


GHCR_OWNER = os.environ.get("GH_OWNER", "findalexli")
GHCR_REPO = "agentsmd-rl"


def _ghcr_image_ref(task_name: str) -> str:
    """Compute the ghcr.io image reference for a task."""
    import re
    name = task_name.lower()
    name = re.sub(r'[^a-z0-9._-]', '-', name)
    name = re.sub(r'-+', '-', name).strip('-')
    return f"ghcr.io/{GHCR_OWNER.lower()}/{GHCR_REPO}/{name}:latest"


async def prepull_task_image(sandbox: AsyncSandbox, task_name: str) -> bool:
    """Pull pre-built task image from ghcr.io and tag as task-env.

    If the image exists on ghcr.io, pulls it and tags as 'task-env' so
    subsequent `docker build` in the agent/validate step is a cache hit.
    Returns True if image was pulled, False otherwise.
    """
    ref = _ghcr_image_ref(task_name)
    code, stdout, stderr = await run_cmd(
        sandbox,
        f"docker pull {ref} 2>&1 && docker tag {ref} task-env",
        timeout=300,
    )
    if code == 0:
        logger.info("[%s] Pre-pulled %s as task-env", task_name, ref)
        return True
    # Image doesn't exist or pull failed — agent will build from Dockerfile
    logger.debug("[%s] No pre-built image at %s, will build from Dockerfile", task_name, ref)
    return False


async def upload_taskforge_modules(sandbox: AsyncSandbox) -> None:
    """Upload taskforge Python modules to sandbox for in-sandbox operations."""
    await run_cmd(sandbox, "mkdir -p /workspace/taskforge")
    await sandbox.files.write("/workspace/taskforge/__init__.py", b"")
    for py_name in [
        "gemini_rubric_constructor.py", "hierarchy_context.py",
        "quality_gate.py", "models.py", "config.py", "judge.py",
        "rubric_validator.py",
        # 20-rubric pipeline revamp
        "rubrics.py", "task_lint.py", "quality_judge.py",
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
    agentmd: bool = False,  # kept for callsite compat; only affects output dir
) -> tuple[str, str, str]:
    """Node 0: Scaffold a task from a PR reference.

    Always uses scaffold.md (the general prompt that handles both Class A
    PRs that edit agent-instruction files AND Class B PRs whose code
    follows a rule from one). The deprecated scaffold_agentmd.md prompt
    abandoned every Class B PR via its strict "no config edit" criterion;
    that footgun caused the 70% abandon rate observed on 2026-04-25.

    Reads: scaffold.md from local disk
    Writes: /workspace/task/* (all task files) in the sandbox
    Returns: (status, task_name, error)
    """
    prompt_file = ROOT / "taskforge" / "prompts" / "scaffold.md"
    if not prompt_file.exists():
        prompt_file = ROOT / ".claude" / "commands" / "scaffold-task.md"
    prompt = prompt_file.read_text().replace("$ARGUMENTS", pr_ref)

    task_dir_name = "markdown_edits" if agentmd else "markdown_following"
    prompt = prompt.replace("markdown_following/", f"{task_dir_name}/")

    await sandbox.files.write("/workspace/scaffold_prompt.md", prompt.encode())

    # Single-shot: let claude -p handle its own internal retries (up to 10).
    # If it fails, report back immediately — the pool's cooldown + batch
    # re-enqueue handle retry scheduling. Previous design had 3 inner retries
    # with 45s/135s/405s backoff ON TOP of claude -p's own 10 retries, creating
    # a 120-API-call retry storm per task that made rate limits worse.
    code, stdout, stderr = await run_cmd(
        sandbox,
        "cat /workspace/scaffold_prompt.md | claude -p "
        "--dangerously-skip-permissions --model opus "
        "--output-format json",
        user="worker",
    )

    if code != 0:
        combined = stdout + stderr
        last_err = combined[:500]
        if _is_rate_limit(combined):
            return "rate_limited", "", last_err
        return "error", "", last_err

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


async def node_full_qa_review(sandbox: AsyncSandbox) -> tuple[str, str]:
    """Full QA review: 4-dimension audit + fixes + oracle validation.
    Reads taskforge/prompts/full_qa_review.md."""
    prompt_file = ROOT / "taskforge" / "prompts" / "full_qa_review.md"
    prompt = prompt_file.read_text()
    await sandbox.files.write("/workspace/full_qa_review_prompt.md", prompt.encode())
    code, stdout, stderr = await run_cmd(
        sandbox,
        "cat /workspace/full_qa_review_prompt.md | claude -p "
        "--dangerously-skip-permissions --model opus "
        "--output-format json",
        user="worker",
        timeout=2700,  # 45 min agent budget
    )
    if code != 0:
        combined = stdout + stderr
        if _is_rate_limit(combined):
            return "rate_limited", combined[:500]
        return "error", combined[:500]
    try:
        raw = await sandbox.files.read("/workspace/task/scaffold_status.json", format="text")
        ss = json.loads(raw)
        if ss.get("abandoned"):
            return "abandoned", ss.get("reason", "")[:300]
    except Exception:
        pass
    return "ok", ""


async def node_repair_full(sandbox: AsyncSandbox) -> tuple[str, str]:
    """Full repair: agent fixes Dockerfile and/or tests/test_outputs.py to make
    Docker oracle nop=0 + gold=1. Tests/solve.sh/instruction.md preserved.
    """
    prompt_file = ROOT / "taskforge" / "prompts" / "repair_full.md"
    prompt = prompt_file.read_text()
    await sandbox.files.write("/workspace/repair_full_prompt.md", prompt.encode())
    code, stdout, stderr = await run_cmd(
        sandbox,
        "cat /workspace/repair_full_prompt.md | claude -p "
        "--dangerously-skip-permissions --model opus "
        "--output-format json",
        user="worker",
        timeout=2400,  # 40 min budget per task — agent does multiple Docker iterations
    )
    if code != 0:
        combined = stdout + stderr
        if _is_rate_limit(combined):
            return "rate_limited", combined[:500]
        return "error", combined[:500]
    try:
        raw = await sandbox.files.read("/workspace/task/scaffold_status.json", format="text")
        ss = json.loads(raw)
        if ss.get("abandoned"):
            return "abandoned", ss.get("reason", "")[:300]
    except Exception:
        pass
    return "ok", ""


async def node_fix_dockerfile(sandbox: AsyncSandbox) -> tuple[str, str]:
    """Fix Dockerfile rot in place. tests/solve/instruction untouched.

    Reads: taskforge/prompts/fix_dockerfile.md  (uploaded via prompt)
    Mutates: /workspace/task/environment/Dockerfile (in sandbox)
    Returns: (status, error)
    """
    prompt_file = ROOT / "taskforge" / "prompts" / "fix_dockerfile.md"
    prompt = prompt_file.read_text()
    await sandbox.files.write("/workspace/fix_dockerfile_prompt.md", prompt.encode())

    code, stdout, stderr = await run_cmd(
        sandbox,
        "cat /workspace/fix_dockerfile_prompt.md | claude -p "
        "--dangerously-skip-permissions --model opus "
        "--output-format json",
        user="worker",
    )
    if code != 0:
        combined = stdout + stderr
        if _is_rate_limit(combined):
            return "rate_limited", combined[:500]
        return "error", combined[:500]
    try:
        raw = await sandbox.files.read("/workspace/task/scaffold_status.json", format="text")
        ss = json.loads(raw)
        if ss.get("abandoned"):
            return "abandoned", ss.get("reason", "")[:300]
    except Exception:
        pass
    return "ok", ""


async def node_repair_manifest(sandbox: AsyncSandbox) -> tuple[str, str]:
    """Repair eval_manifest.yaml in place. Tests/Dockerfile/solve.sh untouched.

    Reads: taskforge/prompts/repair_manifest.md
    Mutates: /workspace/task/eval_manifest.yaml (in sandbox)
    Returns: (status, error)
    """
    prompt_file = ROOT / "taskforge" / "prompts" / "repair_manifest.md"
    prompt = prompt_file.read_text()
    await sandbox.files.write("/workspace/repair_prompt.md", prompt.encode())

    code, stdout, stderr = await run_cmd(
        sandbox,
        "cat /workspace/repair_prompt.md | claude -p "
        "--dangerously-skip-permissions --model opus "
        "--output-format json",
        user="worker",
    )

    if code != 0:
        combined = stdout + stderr
        if _is_rate_limit(combined):
            return "rate_limited", combined[:500]
        return "error", combined[:500]

    # Check if agent abandoned
    try:
        raw = await sandbox.files.read("/workspace/task/scaffold_status.json", format="text")
        ss = json.loads(raw)
        if ss.get("abandoned"):
            return "abandoned", ss.get("reason", "")[:300]
    except Exception:
        pass

    return "ok", ""


async def node_qgate(sandbox: AsyncSandbox, agentmd: bool = False) -> tuple[str, list[str]]:
    """Node 1: Programmatic quality gate — runs INSIDE the sandbox.

    Two-pass check:
      1. task_lint.lint_task    — all 10 programmatic rubrics (dockerfile_determinism,
         pinned_dependencies, pass_to_pass_coverage, test_not_tautological, etc.).
         Runs for BOTH code-only and agentmd tasks.
      2. classify_task_fast     — agentmd-specific (jailbreak, boilerplate, config-edit
         quality). Only runs when agentmd=True.

    Reads: /workspace/task/* inside the sandbox
    Returns: (verdict, flags) where verdict is "passed", "DELETE", or "error"

    DELETE is returned if:
      - task_lint finds ≥1 Tier-A rubric fail (reward-integrity killer)
      - classify_task_fast says DELETE (jailbreak, no manifest, boilerplate-only) — agentmd only

    Tier-B findings are logged as flags but do not block.
    """
    script = (
        "from taskforge.task_lint import lint_task, summarize; "
        "from pathlib import Path; import json; "
        "td = Path('/workspace/task'); "
        "findings = lint_task(td); "
        "s = summarize(findings); "
        "out = {"
        "  'lint_summary': s, "
        "  'lint_tier_a': [str(f) for f in findings if f.tier=='A' and f.severity=='fail'], "
        "  'lint_tier_b': [str(f) for f in findings if f.tier=='B' and f.severity=='fail'][:5],"
        "}; "
    )
    if agentmd:
        script += (
            "from taskforge.quality_gate import classify_task_fast; "
            "qr = classify_task_fast(td); "
            "out['verdict'] = qr.verdict; out['flags'] = qr.flags; "
        )
    else:
        script += "out['verdict'] = ''; out['flags'] = []; "
    script += "print(json.dumps(out))"
    code, stdout, stderr = await run_cmd(
        sandbox,
        f"cd /workspace && python3 -c \"{script}\"",
        timeout=30,
    )
    if code != 0:
        logger.warning("Quality gate failed in sandbox: %s", (stderr or stdout)[:200])
        return "error", [f"sandbox_error: {(stderr or stdout)[:100]}"]

    try:
        last_line = stdout.strip().split("\n")[-1]
        data = json.loads(last_line)
        verdict = data.get("verdict", "")
        flags = list(data.get("flags", []))
        lint_summary = data.get("lint_summary", {})
        tier_a_fails = data.get("lint_tier_a", [])
        tier_b_fails = data.get("lint_tier_b", [])

        # Surface lint findings as flags so they appear in telemetry + abandon logs
        if lint_summary.get("tier_a_fails", 0):
            flags.append(f"lint_tier_a:{lint_summary['tier_a_fails']}")
            flags.extend(f"A:{f[:120]}" for f in tier_a_fails[:4])
        if lint_summary.get("by_tier", {}).get("B", 0):
            flags.append(f"lint_tier_b:{lint_summary['by_tier']['B']}")
            flags.extend(f"B:{f[:120]}" for f in tier_b_fails[:3])

        if verdict == "DELETE":
            return "DELETE", flags

        # New: Tier-A programmatic fail → DELETE.
        # These are unambiguous reward-integrity bugs (unguarded COPY solution/,
        # tautological asserts, zero p2p, pure-grep tests) that no amount of
        # downstream reconciliation can fix — regenerate from scratch.
        if lint_summary.get("tier_a_fails", 0) > 0:
            flags.insert(0, "lint_DELETE: tier-A rubric failure")
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


# ── Gemini CLI prompt (embedded, same as gemini_cli_rubric_extractor.py) ─────

_GEMINI_CLI_PROMPT = """\
# Task: Extract Rubric Rules and Distractors from Agent Config Files

You are analyzing a repository to extract **coding convention rules** from agent \
configuration files (CLAUDE.md, AGENTS.md, SKILL.md, etc.) that are relevant to \
a specific code change (the "gold diff").

## Your Job

1. **Read each config file** listed below using `cat -n` to see exact line numbers.{config_files_hint}
2. **Read the gold diff** at {diff_path}
3. **Extract rules** from config files into three categories:

### Category A: Rubric Rules (gold diff FOLLOWS this convention)
Rules from config files that the gold diff demonstrably follows. These must be:
- Imperative coding conventions (naming, architecture, imports, testing patterns, \
config patterns, style, error handling)
- NOT workflow instructions ("run pre-commit", "use git add", "create PR", "push")
- Actually followed by the gold diff (provide specific evidence from the diff)

### Category B: Distractor Rules (gold diff correctly IGNORES this convention)
Rules from config files that SEEM relevant to the PR but should NOT be followed because:
- They apply to a different scope/domain than the changed files
- Following them would cause a bug or break architecture boundaries
- They conflict with the specific requirements of this change
- They mention technologies/patterns used in the diff but for a different purpose

### Category C: Skip (workflow, irrelevant, too generic)
Rules about git operations, PR creation, build commands, test execution — NOT about \
code patterns. Also skip rules completely unrelated to the changed files' domain.

## CRITICAL Requirements

- **Exact line numbers**: Use `cat -n <file>` to read config files. Report the EXACT \
line range where each rule appears. Do NOT guess or approximate.
- **Quote source text**: Copy the verbatim text from the config file at those lines.
- **Evidence for rubric rules**: Show specifically how the gold diff follows the rule \
(reference actual code, variable names, patterns from the diff).
- **Why distracting**: For distractors, explain why an agent working on THIS specific \
change might mistakenly follow this rule.
- **No workflow rules**: Skip anything about: running commands, git operations, PR \
creation, CI/CD, pre-commit hooks, build systems, deployment.
- **Collision types** for distractors: rule_conflict, scope_ambiguity, meta_confusion, \
architecture_boundary, would_cause_bug
- **Severity** for distractors: high (would cause bug), medium (wasted effort), \
low (minor confusion)

## Output

Respond with ONLY a single JSON object (no markdown fences, no explanation, no text \
before or after). The JSON must have these keys:

- "config_files_found": array of {{"path": str, "type": str, "total_lines": int}}
- "rubric_rules": array of {{"rule": str, "source_path": str, "source_lines": str, \
"source_text": str, "evidence_in_gold": str, "category": str, "verification": str}}
- "distractor_rules": array of {{"rule": str, "source_path": str, "source_lines": str, \
"source_text": str, "collision_type": str, "why_distracting": str, "severity": str}}
- "skipped_rules": array of {{"rule_summary": str, "source_path": str, "source_lines": str, \
"skip_reason": str}}
"""


async def node_gemini_cli_rubric(
    sandbox: AsyncSandbox,
    repo_url: str,
    model: str = "gemini-3.1-pro-preview",
) -> tuple[str, int, int, int]:
    """Node 2b: Gemini CLI rubric extraction — exact line numbers via cat -n.

    Runs `gemini` CLI inside the E2B sandbox against /workspace/repo/.
    The CLI executes shell commands (cat -n) to read config files with exact
    line numbers, then cross-references against the gold diff.

    Reads: /workspace/task/eval_manifest.yaml, /workspace/task/solution/solve.sh,
           /workspace/repo/ (cloned repo)
    Writes: updated eval_manifest.yaml with rubrics + distractors
    Returns: (status, rubrics_added, distractors_added, skipped)

    status: "ok" | "no_new_rules" | "error"
    """
    # Step 1: Extract gold diff from solve.sh
    # Write extraction script to file to avoid shell escaping hell
    extract_script = r'''
import re, sys
from pathlib import Path
text = Path("/workspace/task/solution/solve.sh").read_text()
m = re.search(r"diff --git.*", text, re.DOTALL)
if m:
    d = re.sub(r"\n(PATCH|EOF|DIFF|GOLD)\s*$", "", m.group(0))
    sys.stdout.write(d)
else:
    # Fallback: entire solve.sh — handles python/cat/sed-based patches
    sys.stdout.write(text)
'''
    await sandbox.files.write("/workspace/_extract_diff.py", extract_script.encode())
    code, gold_diff, _ = await run_cmd(
        sandbox, "python3 /workspace/_extract_diff.py", timeout=10,
    )
    if code != 0 or not gold_diff.strip():
        return "error", 0, 0, 0

    # Write diff/patch to a temp file in sandbox
    await sandbox.files.write("/workspace/gold_diff.patch", gold_diff.encode())

    # Step 2: Discover config files in /workspace/repo/
    code, config_out, _ = await run_cmd(
        sandbox,
        "find /workspace/repo/ -maxdepth 5 "
        "\\( -name 'CLAUDE.md' -o -name 'AGENTS.md' -o -name 'CONVENTIONS.md' "
        "-o -name 'SKILL.md' -o -name '.cursorrules' \\) "
        "-not -path '*/.git/*' -not -path '*/node_modules/*' "
        "| sed 's|^/workspace/repo/||' | sort 2>/dev/null; "
        "find /workspace/repo/.claude/rules/ -name '*.md' 2>/dev/null "
        "| sed 's|^/workspace/repo/||' | sort; "
        "find /workspace/repo/.claude/skills/ -name '*.md' 2>/dev/null "
        "| sed 's|^/workspace/repo/||' | sort; "
        "find /workspace/repo/.cursor/rules/ -name '*.md' -o -name '*.mdc' 2>/dev/null "
        "| sed 's|^/workspace/repo/||' | sort",
        timeout=30,
    )
    config_files = [f.strip() for f in config_out.strip().splitlines() if f.strip()]

    if config_files:
        hint = "\n   Known config files in this repo:\n" + \
               "\n".join(f"   - {f}" for f in config_files) + \
               "\n   Also check for any you might find beyond this list."
    else:
        hint = "\n   Search the repo for config files (CLAUDE.md, AGENTS.md, SKILL.md, etc.)"

    # Step 3: Build and write the prompt
    prompt = _GEMINI_CLI_PROMPT.format(
        diff_path="/workspace/gold_diff.patch",
        config_files_hint=hint,
    )
    await sandbox.files.write("/workspace/gemini_prompt.txt", prompt.encode())

    # Step 4: Run gemini CLI
    code, stdout, stderr = await run_cmd(
        sandbox,
        f'cat /workspace/gemini_prompt.txt | '
        f'npx -y @google/gemini-cli -m {model} -p "Follow the instructions from stdin." -y -o json 2>/dev/null',
        timeout=900,  # 15 min — big repos (bun, next.js, playwright) need >5 min
    )

    if code != 0:
        combined = (stdout + stderr)[:500]
        if "429" in combined or "rate limit" in combined.lower():
            return "error", 0, 0, 0
        logger.warning("gemini CLI error: %s", combined[:200])
        return "error", 0, 0, 0

    # Step 5: Parse response
    try:
        envelope = json.loads(stdout.strip())
    except json.JSONDecodeError:
        # Try to find JSON in mixed output
        match = re.search(r'\{.*"session_id".*\}', stdout, re.DOTALL)
        if match:
            try:
                envelope = json.loads(match.group(0))
            except json.JSONDecodeError:
                return "error", 0, 0, 0
        else:
            return "error", 0, 0, 0

    if envelope.get("error"):
        logger.warning("gemini CLI returned error: %s", envelope["error"])
        return "error", 0, 0, 0

    response_text = envelope.get("response", "")
    if not response_text:
        return "error", 0, 0, 0

    # Parse JSON from response text
    parsed = None
    response_text = response_text.strip()
    for attempt_fn in [
        lambda: json.loads(response_text),
        lambda: json.loads(re.search(r'```(?:json)?\s*\n(.*?)```', response_text, re.DOTALL).group(1)),
        lambda: json.loads(response_text[response_text.index('{'):response_text.rindex('}') + 1]),
    ]:
        try:
            parsed = attempt_fn()
            break
        except Exception:
            continue

    if not parsed or ("rubric_rules" not in parsed and "distractor_rules" not in parsed):
        logger.warning("gemini CLI: could not parse rubric JSON from response")
        return "error", 0, 0, 0

    # Step 6: Merge into eval_manifest.yaml
    # Write extraction result to a file in sandbox to avoid shell escaping issues
    await sandbox.files.write(
        "/workspace/gemini_extraction.json",
        json.dumps(parsed).encode(),
    )

    # Run merge script that reads from the file
    merge_script = r'''
import json, yaml
from pathlib import Path

data = json.loads(Path("/workspace/gemini_extraction.json").read_text())
mp = Path("/workspace/task/eval_manifest.yaml")
m = yaml.safe_load(mp.read_text()) or {}

existing_r = {r.get("rule","")[:50].lower().strip() for r in (m.get("rubric") or []) if isinstance(r, dict)}
existing_d = {d.get("rule","")[:50].lower().strip() for d in (m.get("distractors") or []) if isinstance(d, dict)}

new_r = []
for r in data.get("rubric_rules", []):
    rule = r.get("rule", "")
    if len(rule) < 15 or rule[:50].lower().strip() in existing_r:
        continue
    new_r.append({
        "rule": rule,
        "source": {"path": r.get("source_path",""), "lines": str(r.get("source_lines",""))},
        "source_text": r.get("source_text",""),
        "evidence": r.get("evidence_in_gold",""),
        "category": r.get("category",""),
        "verification": "llm_judge",
    })

new_d = []
for d in data.get("distractor_rules", []):
    rule = d.get("rule", "")
    if len(rule) < 15 or rule[:50].lower().strip() in existing_d:
        continue
    new_d.append({
        "rule": rule,
        "source": {"path": d.get("source_path",""), "lines": str(d.get("source_lines",""))},
        "source_text": d.get("source_text",""),
        "collision_type": d.get("collision_type","scope_ambiguity"),
        "why_distracting": d.get("why_distracting",""),
        "severity": d.get("severity","medium"),
    })

m["rubric"] = (m.get("rubric") or []) + new_r
m["distractors"] = (m.get("distractors") or []) + new_d
if new_r or new_d:
    mp.write_text(yaml.dump(m, default_flow_style=False, sort_keys=False, allow_unicode=True))
skipped = len(data.get("skipped_rules", []))
print(json.dumps({"rubrics": len(new_r), "distractors": len(new_d), "skipped": skipped}))
'''
    await sandbox.files.write("/workspace/merge_rubric.py", merge_script.encode())
    code, merge_out, merge_err = await run_cmd(
        sandbox, "python3 /workspace/merge_rubric.py", timeout=15,
    )

    if code != 0:
        logger.warning("gemini CLI merge failed: %s", (merge_err or merge_out)[:200])
        return "error", 0, 0, 0

    try:
        counts = json.loads(merge_out.strip().split("\n")[-1])
        nr = counts.get("rubrics", 0)
        nd = counts.get("distractors", 0)
        ns = counts.get("skipped", 0)
        status = "ok" if (nr + nd) > 0 else "no_new_rules"
        return status, nr, nd, ns
    except (json.JSONDecodeError, IndexError):
        return "error", 0, 0, 0


async def node_clone_repo(sandbox: AsyncSandbox, task_name: str) -> tuple[str, str]:
    """Clone the task's source repo into /workspace/repo/ for rubric extraction.

    Reads: /workspace/task/environment/Dockerfile (parses repo URL + commit)
    Writes: /workspace/repo/ (cloned repo at base commit)
    Returns: (repo_url, repo_commit)
    """
    code, repo_info, _ = await run_cmd(
        sandbox,
        r"""python3 -c "
from pathlib import Path; import re, yaml
repo_url = commit = ''

# Try Dockerfile first
df = Path('/workspace/task/environment/Dockerfile')
if df.exists():
    text = df.read_text()
    m = re.search(r'github\.com/([^/\s]+/[^\s]+?)(?:\.git|[\s]|$)', text)
    if m: repo_url = m.group(1).rstrip('/')
    for pat in [r'git checkout\s+([a-f0-9]{7,40})', r'ARG\s+BASE_COMMIT=([a-f0-9]{7,40})', r'git fetch[^\n]*origin\s+([a-f0-9]{7,40})']:
        cm = re.search(pat, text)
        if cm: commit = cm.group(1); break

# Fallback: eval_manifest.yaml
if not repo_url or not commit:
    mf = Path('/workspace/task/eval_manifest.yaml')
    if mf.exists():
        m = yaml.safe_load(mf.read_text()) or {}
        src = m.get('source', {}) or {}
        if not repo_url and src.get('repo'): repo_url = str(src['repo']).strip('\"')
        if not commit and src.get('base_commit'): commit = str(src['base_commit']).strip('\"')

# Fallback: task.toml
if not repo_url or not commit:
    tp = Path('/workspace/task/task.toml')
    if tp.exists():
        tt = tp.read_text()
        if not repo_url:
            m = re.search(r'source_repo\s*=\s*\"([^\"]+)\"', tt)
            if m: repo_url = m.group(1)
        if not commit:
            m = re.search(r'base_commit\s*=\s*\"([a-f0-9]{7,40})\"', tt)
            if m: commit = m.group(1)

print(repo_url)
print(commit)
" """,
        timeout=10,
    )
    repo_url = repo_commit = ""
    if code == 0 and repo_info.strip():
        lines = repo_info.strip().split("\n")
        repo_url = lines[0].strip() if len(lines) > 0 else ""
        repo_commit = lines[1].strip() if len(lines) > 1 else ""

    if repo_url and repo_commit:
        if re.match(r'^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$', repo_url):
            # Use shallow fetch pattern (faster than full clone)
            # Separate chown so checkout failure is detected
            clone_code, _, clone_err = await run_cmd(
                sandbox,
                f"git init /workspace/repo && "
                f"cd /workspace/repo && "
                f"git remote add origin https://github.com/{repo_url}.git && "
                f"git fetch --depth=1 origin {repo_commit} && "
                f"git checkout {repo_commit}",
                timeout=180,
            )
            # Fix ownership separately (don't let this mask checkout failure)
            await run_cmd(
                sandbox,
                "chown -R worker:worker /workspace/repo 2>/dev/null || true",
                timeout=10,
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


async def node_fix_task_quality(sandbox: AsyncSandbox) -> tuple[str, str]:
    """Node 4+6c combined: Fix tests AND instruction in a single coordinated pass.

    Replaces the sequential improve_tests → validate → judge → instruction_reconcile
    pipeline for tasks with quality issues in both tests and instruction.

    Reads: quality.json, instruction.md, test_outputs.py, solve.sh, Dockerfile, eval_manifest.yaml
    Writes: updated test_outputs.py, instruction.md, eval_manifest.yaml, reconcile_status.json
    Returns: (status, error)
    """
    return await _run_agent(sandbox, "fix_task_quality.md")


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
    # Build the task's Docker image (pre-pulled image makes this a cache hit)
    # Check if task-env already exists (from prepull_task_image)
    code, _, _ = await run_cmd(sandbox, "docker image inspect task-env >/dev/null 2>&1", timeout=5)
    if code != 0:
        # No pre-pulled image, build from Dockerfile
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
    await run_cmd(sandbox, "rm -f /logs/verifier/reward.txt /logs/verifier/ctrf.json")
    code, stdout, stderr = await run_cmd(
        sandbox,
        "docker run --rm "
        "-v /workspace/task/tests:/tests:ro "
        "-v /logs/verifier:/logs/verifier "
        "task-env-gold bash /tests/test.sh",
    )
    gold_reward = await _read_reward(sandbox)

    # Change 4 (every_gold_test_passes): when ctrf.json is present, verify
    # EVERY individual test passed on gold, not just the aggregate reward.
    # Catches cases where test.sh is weakened / has bugs such that it writes
    # reward=1 despite some pytest tests failing inside.
    if gold_reward == 1.0:
        code, ctrf_txt, _ = await run_cmd(
            sandbox, "cat /logs/verifier/ctrf.json 2>/dev/null || true", timeout=5,
        )
        if ctrf_txt.strip().startswith("{"):
            try:
                import json as _json
                data = _json.loads(ctrf_txt)
                tests = (data.get("results") or {}).get("tests") or []
                failed_names = [
                    t.get("name", "?") for t in tests if t.get("status") == "failed"
                ]
                if failed_names:
                    # Gold claims pass but ctrf reveals individual failures → broken scaffold
                    return nop_reward, -1, (
                        f"gold reward=1 but ctrf.json shows {len(failed_names)} "
                        f"failed test(s): {failed_names[:3]} — scaffold bug "
                        f"(brittle test or weakened test.sh)"
                    )
            except Exception:
                pass  # malformed ctrf — don't over-reject

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


async def node_quality_judge(sandbox: AsyncSandbox) -> tuple[str, dict]:
    """Node 6b: LLM quality judge — Opus 4.6 scores task against 10 llm_judge rubrics.

    Uses JUDGE_API_KEY (real Anthropic endpoint), NOT the pool's ANTHROPIC_API_KEY
    (which may point at MiniMax/GLM/Kimi for the executor).

    Reads: /workspace/task/instruction.md, tests/test_outputs.py, solution/solve.sh,
           environment/Dockerfile
    Writes: /workspace/task/quality.json  (per-rubric verdicts + summary)
    Returns: (status, summary_dict)
      status: "ok" | "skipped" | "error"
      summary_dict: { tier_a_fails, tier_b_fails, tier_c_fails, pass_count, fail_count }
    """
    # Write the runner script to a file (inline try/except doesn't fit -c one-liner)
    judge_script = (
        "from taskforge.quality_judge import judge_task, JudgeError\n"
        "from pathlib import Path\n"
        "import json\n"
        "td = Path('/workspace/task')\n"
        "try:\n"
        "    r = judge_task(td)\n"
        "except JudgeError as e:\n"
        "    r = {'error': str(e)}\n"
        "open(td / 'quality.json', 'w').write(json.dumps(r, indent=2))\n"
        "summary_keys = ['tier_a_fails', 'tier_b_fails', 'tier_c_fails', "
        "'pass_count', 'fail_count', 'error']\n"
        "print(json.dumps({k: r.get(k) for k in summary_keys if r.get(k) is not None}))\n"
    )
    await sandbox.files.write("/workspace/run_judge.py", judge_script.encode())
    code, stdout, stderr = await run_cmd(
        sandbox,
        "cd /workspace && python3 /workspace/run_judge.py",
        timeout=240,  # Opus judge ~5-30s typical
    )
    if code != 0:
        return "error", {"error": (stderr or stdout)[:200]}
    try:
        last = stdout.strip().split("\n")[-1]
        data = json.loads(last)
    except (json.JSONDecodeError, IndexError):
        return "error", {"error": f"parse: {stdout[:200]}"}
    if data.get("error"):
        return "error", data
    return "ok", data


async def node_instruction_reconcile(sandbox: AsyncSandbox) -> tuple[str, str]:
    """Node 6c: Instruction reconciliation — cheap executor rewrites instruction.md
    using the judge's findings, then re-validates (nop=0, gold=1 must still hold).

    Called ONLY when node_quality_judge flags behavior_in_task_description,
    no_solution_leakage, or instruction_no_hint_leakage as FAIL.

    The executor is the pool backend (MiniMax/GLM/Kimi) — NOT Opus — because
    this is a conventional rewrite task, not a judgment call.

    Reads: /workspace/task/quality.json + instruction.md + tests/ + solution/
    Writes: /workspace/task/instruction.md (rewritten); reconcile_status.json
    Returns: (status, error)
      status: "ok" | "abandoned" | "error" | "rate_limited"
    """
    return await _run_agent(sandbox, "instruction_reconcile.md")


async def node_tests_rewrite(sandbox: AsyncSandbox) -> tuple[str, str]:
    """Node 6d: Test rewrite — cheap executor rewrites tests/test_outputs.py to
    be behavioral (invoke code instead of grep), then re-validates oracle.

    Called ONLY when node_quality_judge flags test-design rubrics as FAIL:
      - tests_verify_behavior_not_text  (pure text-match tests)
      - solution_uniqueness_guard        (tests assert gold-specific literals)
      - test_not_tautological            (asserts pass on stub impls)

    Cannot fix structural issues (no_hidden_solution_artifacts when solution/
    is COPY'd into image, or pass_to_pass_coverage requiring new eval_manifest
    entries). Agent writes abandoned=true for those.

    Reads: /workspace/task/quality.json + tests/* + solution/solve.sh +
           environment/Dockerfile
    Writes: /workspace/task/tests/test_outputs.py (rewritten);
            tests_rewrite_status.json
    Returns: (status, error)
      status: "ok" | "abandoned" | "error" | "rate_limited"
    """
    return await _run_agent(sandbox, "tests_rewrite.md")


def _is_rate_limit(text: str) -> bool:
    """Detect rate-limit signatures in claude -p output."""
    if not text:
        return False
    lower = text.lower()
    return ("429" in text
            or "rate limit" in lower
            or "hit your limit" in lower
            or "overloaded" in lower)


async def _run_agent(
    sandbox: AsyncSandbox,
    prompt_name: str,
    *,
    inner_retries: int = 0,
    base_backoff: float = 45.0,
) -> tuple[str, str]:
    """Run a claude -p agent with a prompt file. Returns (status, error).

    Single-shot by default: claude -p has its own internal 10-retry backoff.
    Adding outer retries on top creates retry storms (10 internal × N outer
    × M workers = thousands of redundant API calls).

    If inner_retries > 0, will retry with sandbox-level backoff (fresh
    conversation each time). Only use this for critical nodes where a
    fresh conversation might help (not for rate limit recovery).
    """
    prompt_file = ROOT / "taskforge" / "prompts" / prompt_name
    if not prompt_file.exists():
        return "skipped", f"prompt file missing: {prompt_name}"

    prompt = prompt_file.read_text()
    await sandbox.files.write(f"/workspace/{prompt_name}", prompt.encode())

    last_err = ""
    for attempt in range(inner_retries + 1):
        code, stdout, stderr = await run_cmd(
            sandbox,
            f"cat /workspace/{prompt_name} | claude -p "
            f"--dangerously-skip-permissions --model opus "
            f"--output-format json",
            user="worker",
        )

        if code == 0:
            return "ok", ""

        combined = stdout + stderr
        last_err = combined[:500]

        if not _is_rate_limit(combined):
            return "error", last_err

        if attempt < inner_retries:
            delay = base_backoff * (3 ** attempt)
            logger.warning("_run_agent(%s) rate-limited (attempt %d/%d); sleeping %.0fs",
                           prompt_name, attempt + 1, inner_retries + 1, delay)
            await asyncio.sleep(delay)
            continue

        return "rate_limited", last_err

    return "rate_limited", last_err


async def _read_reward(sandbox: AsyncSandbox) -> float:
    """Read reward.txt from sandbox. Returns -1 if missing/unreadable."""
    try:
        data = await sandbox.files.read("/logs/verifier/reward.txt", format="text")
        return float(data.strip())
    except Exception:
        return -1.0


async def _read_task_name(sandbox: AsyncSandbox, pr_ref: str) -> str:
    """Read task name from task.toml or derive from PR ref."""
    # Only run python3 — don't let ls output leak into the name
    code, stdout, _ = await run_cmd(
        sandbox,
        "python3 -c \""
        "import tomllib, os; "
        "p = '/workspace/task/task.toml'; "
        "print(tomllib.load(open(p,'rb')).get('name','') if os.path.exists(p) else '')"
        "\" 2>/dev/null",
    )
    if code == 0:
        name = stdout.strip()
        # Reject anything that looks like a path (contains /)
        if name and "/" not in name and not name.startswith("."):
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


# In-flight claim tracking — releases on SIGTERM/SIGINT/atexit so killed
# workers don't leave ghost claims that block future runs from retrying.
# A claim is "in flight" from acquisition until run_task returns; on normal
# completion it is unregistered (claim stays sticky as designed). On signal
# exit, anything still registered is mid-flight work that must be released.
_inflight_claims: set[Path] = set()
_inflight_lock = threading.Lock()


def _register_inflight(claim_path: Path) -> None:
    with _inflight_lock:
        _inflight_claims.add(claim_path)


def _unregister_inflight(claim_path: Path) -> None:
    with _inflight_lock:
        _inflight_claims.discard(claim_path)


def release_inflight_claims(reason: str = "exit") -> int:
    """Delete any claim files still registered as in-flight. Returns count."""
    with _inflight_lock:
        paths = list(_inflight_claims)
        _inflight_claims.clear()
    n = 0
    for p in paths:
        try:
            p.unlink()
            n += 1
        except FileNotFoundError:
            pass
        except Exception as e:
            logger.warning("Failed to release claim %s: %s", p.name, e)
    if n:
        logger.info("[%s] Released %d in-flight claims", reason, n)
    return n


def _claim_pr(claim_dir: Path, pr_ref: str) -> tuple[Path, bool]:
    """Atomically claim a PR for processing. Returns (claim_file, acquired).

    Uses POSIX O_CREAT|O_EXCL for cross-process atomicity. If the claim file
    already exists, another worker has the PR — return (path, False).

    The claim file holds the owning worker's PID + timestamp for observability.
    Claim files are NEVER deleted automatically on task completion (PASS or
    FAIL): the claim remains as a "this PR was handled" record so a parallel
    pipeline run won't re-pick it up. The exception is signal/exit cleanup —
    if the worker is killed mid-flight, release_inflight_claims() drops claims
    for tasks that didn't get to finish, so the next run can retry them.
    """
    import os
    claim_dir.mkdir(parents=True, exist_ok=True)
    slug = pr_ref.replace("/", "__").replace("#", "_")
    claim_path = claim_dir / f"{slug}.claim"
    try:
        fd = os.open(str(claim_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        try:
            os.write(fd, f"pid={os.getpid()} ts={time.time():.0f} pr_ref={pr_ref}\n".encode())
        finally:
            os.close(fd)
        return claim_path, True
    except FileExistsError:
        return claim_path, False


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
    claim_dir: Path | None = None,
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
    acquired_claim_path: Path | None = None

    # Cross-process claim: if another worker (same or different pipeline process)
    # has already claimed this PR, skip it early — before burning sandbox time.
    # Only applies to new-PR scaffolds; existing-task processing ignores claims.
    if is_new and claim_dir is not None:
        claim_path, acquired = _claim_pr(claim_dir, pr_ref)
        if not acquired:
            logger.info("[%s] already claimed by another worker (%s)", pr_ref, claim_path.name)
            result.error = "claimed_elsewhere"
            result.total_time = round(time.monotonic() - t_start, 2)
            return result
        acquired_claim_path = claim_path
        _register_inflight(claim_path)

    async with sandbox_sem:
        sandbox = None
        backend = None
        backend_ctx = None
        dest: Path | None = None

        try:
            # ── Acquire backend ───────────────────────────────────
            # Every start_at stage except pure-scaffold includes at least one LLM
            # node: validate_and_fix, instruction_reconcile, improve, enrich, etc.
            # Previous code only acquired on `start_at >= ENRICH`, which starved
            # start_at=VALIDATE and start_at=QGATE retrofit runs of an executor —
            # claude-p then failed in the sandbox because no ANTHROPIC_API_KEY
            # was injected.
            if pool:
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
            if is_new and start_at in (StartAt.SCAFFOLD, StartAt.ONESHOT_SCAFFOLD):
                # Oneshot: ensure no stale verdict from a prior attempt.
                if start_at == StartAt.ONESHOT_SCAFFOLD:
                    await run_cmd(
                        sandbox,
                        "rm -f /workspace/task/scaffold_status.json",
                    )

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
                    logger.info("[%s] scaffold ABANDONED (%.0fs): %s",
                                pr_ref, elapsed, err[:200])
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

                # Oneshot mode: trust scaffold.md's verdict (Docker NOP/GOLD
                # already validated inside the agent call) and skip the
                # trailing qgate/rubric/enrich/improve/validate/judge chain.
                if start_at == StartAt.ONESHOT_SCAFFOLD:
                    ss_data: dict = {}
                    # Primary: scaffold_status.json (Step 8 of scaffold.md)
                    try:
                        ss_raw = await sandbox.files.read(
                            "/workspace/task/scaffold_status.json", format="text")
                        ss_data = json.loads(ss_raw)
                    except Exception:
                        # Fallback: agent may have written {abandoned:true} to
                        # status.json via Step 1b's abandon path before reaching
                        # Step 8. Surface that reason rather than blank-failing.
                        try:
                            sj_raw = await sandbox.files.read(
                                "/workspace/task/status.json", format="text")
                            sj_data = json.loads(sj_raw)
                            if sj_data.get("abandoned"):
                                ss_data = sj_data
                        except Exception:
                            pass

                    if ss_data.get("abandoned"):
                        result.error = f"oneshot_scaffold abandoned: {ss_data.get('reason','')[:200]}"
                        result.valid = False
                        logger.info("[%s] oneshot_scaffold ABANDONED: %s",
                                    result.task_name, ss_data.get("reason","")[:120])
                    elif ss_data.get("scaffolded"):
                        result.nop_reward = float(ss_data.get("nop_reward", -1))
                        result.gold_reward = float(ss_data.get("gold_reward", -1))
                        result.valid = (result.nop_reward == 0.0 and result.gold_reward == 1.0)
                        # Schema gate: reject scaffolds whose eval_manifest.yaml
                        # cannot be parsed by the canonical Pydantic model. Backends
                        # otherwise drift (custom origin enums, file/path swaps,
                        # description/rule swaps, etc.). 38% of historic corpus
                        # fails this gate — we stop adding to that pile.
                        if result.valid:
                            try:
                                manifest_raw = await sandbox.files.read(
                                    "/workspace/task/eval_manifest.yaml", format="text")
                                import yaml as _yaml
                                from taskforge.models import EvalManifest
                                EvalManifest.model_validate(_yaml.safe_load(manifest_raw))
                            except Exception as schema_err:
                                msg = str(schema_err)[:400]
                                result.valid = False
                                result.error = f"manifest schema invalid: {msg}"
                                logger.warning("[%s] oneshot_scaffold REJECTED (schema): %s",
                                               result.task_name, msg[:200])
                        logger.info("[%s] oneshot_scaffold SCAFFOLDED: nop=%.1f gold=%.1f valid=%s",
                                    result.task_name, result.nop_reward,
                                    result.gold_reward, result.valid)
                    else:
                        result.error = "oneshot_scaffold: agent wrote no verdict to scaffold_status.json"
                        result.valid = False
                        logger.warning("[%s] oneshot_scaffold: no verdict produced", result.task_name)

                    # Trust the verdict — short-circuit past qgate and the rest
                    # of the multi-node chain. Download outputs only if valid.
                    result.total_time = round(time.monotonic() - t_start, 2)
                    final_status = await read_sandbox_status(sandbox)
                    result.nodes = final_status.get("nodes", {})
                    if result.valid and dest:
                        await download_task_files(sandbox, dest)
                        write_status_json(dest, result, nodes=result.nodes)
                        result.downloaded = True
                        logger.info("[%s] PASS — downloaded to %s",
                                    result.task_name, dest)
                    elif dest and not is_new:
                        write_status_json(dest, result, nodes=result.nodes)
                    if pool and backend and "rate limited" not in (result.error or "").lower():
                        pool.report_success(backend)
                    return result

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
                result.task_name = task_ref

                # ── Oneshot full QA review: 4-dimension audit + fixes + oracle gate ──
                if start_at == StartAt.ONESHOT_FULL_QA_REVIEW:
                    await run_cmd(sandbox, "rm -f /workspace/task/scaffold_status.json")
                    t0 = time.monotonic()
                    s, err = await node_full_qa_review(sandbox)
                    elapsed = time.monotonic() - t0
                    result.scaffold_time = round(elapsed, 2)
                    if s == "rate_limited":
                        result.error = f"rate limited: {err}"
                        if pool and backend: pool.report_429(backend)
                        raise _RateLimited(result.error)
                    if s == "abandoned":
                        result.error = f"qa_review abandoned: {err}"
                        result.valid = False
                        logger.info("[%s] qa_review ABANDONED (%.0fs): %s",
                                    task_ref, elapsed, err[:200])
                        result.total_time = round(time.monotonic() - t_start, 2)
                        return result
                    if s != "ok":
                        result.error = f"qa_review failed: {err}"
                        result.total_time = round(time.monotonic() - t_start, 2)
                        return result
                    # Run Docker oracle to confirm
                    nop, gold, err2 = await node_validate_docker_only(sandbox)
                    result.nop_reward = nop
                    result.gold_reward = gold
                    result.valid = (nop == 0.0 and gold == 1.0)
                    if not result.valid:
                        result.error = f"oracle still failing nop={nop} gold={gold}; {err2[:200]}"
                        logger.warning("[%s] qa_review REJECTED (oracle): nop=%s gold=%s",
                                       task_ref, nop, gold)
                        result.total_time = round(time.monotonic() - t_start, 2)
                        return result
                    # Schema-validate the manifest
                    try:
                        manifest_raw = await sandbox.files.read(
                            "/workspace/task/eval_manifest.yaml", format="text")
                        import yaml as _yaml
                        from taskforge.models import EvalManifest
                        EvalManifest.model_validate(_yaml.safe_load(manifest_raw))
                    except Exception as schema_err:
                        result.valid = False
                        result.error = f"manifest schema invalid after qa: {str(schema_err)[:300]}"
                        logger.warning("[%s] qa_review REJECTED (schema): %s",
                                       task_ref, str(schema_err)[:200])
                        result.total_time = round(time.monotonic() - t_start, 2)
                        return result
                    # Download all touched files
                    try:
                        for sub in [("environment", "Dockerfile"),
                                     ("tests", "test_outputs.py"),
                                     ("eval_manifest.yaml",),
                                     ("instruction.md",)]:
                            sandbox_path = "/workspace/task/" + "/".join(sub)
                            try:
                                content = await sandbox.files.read(sandbox_path, format="text")
                                local = dest.joinpath(*sub)
                                local.parent.mkdir(parents=True, exist_ok=True)
                                local.write_text(content)
                            except Exception:
                                pass
                        result.downloaded = True
                        logger.info("[%s] qa_review PASS — files written (nop=0 gold=1)", task_ref)
                    except Exception as e:
                        result.valid = False
                        result.error = f"download error: {e}"
                    result.total_time = round(time.monotonic() - t_start, 2)
                    if pool and backend and result.valid:
                        pool.report_success(backend)
                    return result

                # ── Oneshot full repair (legacy of qa_review with smaller scope) ──
                if start_at == StartAt.ONESHOT_REPAIR_FULL:
                    await run_cmd(sandbox, "rm -f /workspace/task/scaffold_status.json")
                    t0 = time.monotonic()
                    s, err = await node_repair_full(sandbox)
                    elapsed = time.monotonic() - t0
                    result.scaffold_time = round(elapsed, 2)
                    if s == "rate_limited":
                        result.error = f"rate limited: {err}"
                        if pool and backend: pool.report_429(backend)
                        raise _RateLimited(result.error)
                    if s == "abandoned":
                        result.error = f"repair_full abandoned: {err}"
                        result.valid = False
                        logger.info("[%s] repair_full ABANDONED (%.0fs): %s",
                                    task_ref, elapsed, err[:200])
                        result.total_time = round(time.monotonic() - t_start, 2)
                        return result
                    if s != "ok":
                        result.error = f"repair_full failed: {err}"
                        result.total_time = round(time.monotonic() - t_start, 2)
                        return result
                    # Run our own Docker oracle to confirm nop=0 + gold=1
                    nop, gold, err2 = await node_validate_docker_only(sandbox)
                    result.nop_reward = nop
                    result.gold_reward = gold
                    result.valid = (nop == 0.0 and gold == 1.0)
                    if not result.valid:
                        result.error = f"docker oracle still failing nop={nop} gold={gold}; {err2[:200]}"
                        logger.warning("[%s] repair_full REJECTED (oracle): nop=%s gold=%s",
                                       task_ref, nop, gold)
                        result.total_time = round(time.monotonic() - t_start, 2)
                        return result
                    # Download Dockerfile + tests/test_outputs.py back to disk
                    try:
                        df = await sandbox.files.read(
                            "/workspace/task/environment/Dockerfile", format="text")
                        (dest / "environment" / "Dockerfile").write_text(df)
                        tp = await sandbox.files.read(
                            "/workspace/task/tests/test_outputs.py", format="text")
                        (dest / "tests" / "test_outputs.py").write_text(tp)
                        result.downloaded = True
                        logger.info("[%s] repair_full PASS — files written (nop=0 gold=1)", task_ref)
                    except Exception as e:
                        result.valid = False
                        result.error = f"download error: {e}"
                    result.total_time = round(time.monotonic() - t_start, 2)
                    if pool and backend and result.valid:
                        pool.report_success(backend)
                    return result

                # ── Oneshot Dockerfile fix: rewrite Dockerfile from a failure log ──
                if start_at == StartAt.ONESHOT_FIX_DOCKERFILE:
                    await run_cmd(sandbox, "rm -f /workspace/task/scaffold_status.json")
                    t0 = time.monotonic()
                    s, err = await node_fix_dockerfile(sandbox)
                    elapsed = time.monotonic() - t0
                    result.scaffold_time = round(elapsed, 2)
                    if s == "rate_limited":
                        result.error = f"rate limited: {err}"
                        if pool and backend: pool.report_429(backend)
                        raise _RateLimited(result.error)
                    if s == "abandoned":
                        result.error = f"fix_dockerfile abandoned: {err}"
                        result.valid = False
                        logger.info("[%s] fix_dockerfile ABANDONED (%.0fs): %s",
                                    task_ref, elapsed, err[:200])
                        result.total_time = round(time.monotonic() - t_start, 2)
                        return result
                    if s != "ok":
                        result.error = f"fix_dockerfile failed: {err}"
                        result.total_time = round(time.monotonic() - t_start, 2)
                        return result
                    # Verify docker build succeeds in sandbox
                    code, build_out, _ = await run_cmd(
                        sandbox,
                        "cd /workspace && docker build -t task-env-fixtest ./task/environment/ 2>&1 | tail -20",
                        timeout=600,
                    )
                    if code != 0:
                        result.valid = False
                        result.error = f"docker build still failing: {build_out[-300:]}"
                        logger.warning("[%s] fix_dockerfile REJECTED (build): %s",
                                       task_ref, build_out[-200:])
                        result.total_time = round(time.monotonic() - t_start, 2)
                        return result
                    # Download just the fixed Dockerfile back to disk
                    try:
                        new_df = await sandbox.files.read(
                            "/workspace/task/environment/Dockerfile", format="text")
                        (dest / "environment" / "Dockerfile").write_text(new_df)
                        result.valid = True
                        result.downloaded = True
                        logger.info("[%s] fix_dockerfile PASS — Dockerfile written", task_ref)
                    except Exception as e:
                        result.valid = False
                        result.error = f"failed to download Dockerfile: {e}"
                    result.total_time = round(time.monotonic() - t_start, 2)
                    if pool and backend and result.valid:
                        pool.report_success(backend)
                    return result

                # ── Oneshot manifest repair: rewrite eval_manifest.yaml only ──
                # Skips the rest of the pipeline (qgate/rubric/enrich/improve/validate).
                # Uses the schema gate to verify the agent produced canonical output.
                if start_at == StartAt.ONESHOT_REPAIR_MANIFEST:
                    # Clear stale verdict
                    await run_cmd(sandbox, "rm -f /workspace/task/scaffold_status.json")
                    t0 = time.monotonic()
                    s, err = await node_repair_manifest(sandbox)
                    elapsed = time.monotonic() - t0
                    result.scaffold_time = round(elapsed, 2)

                    if s == "rate_limited":
                        result.error = f"rate limited: {err}"
                        if pool and backend:
                            pool.report_429(backend)
                        raise _RateLimited(result.error)
                    if s == "abandoned":
                        result.error = f"repair abandoned: {err}"
                        result.valid = False
                        logger.info("[%s] repair_manifest ABANDONED (%.0fs): %s",
                                    task_ref, elapsed, err[:200])
                        result.total_time = round(time.monotonic() - t_start, 2)
                        return result
                    if s != "ok":
                        result.error = f"repair failed: {err}"
                        result.total_time = round(time.monotonic() - t_start, 2)
                        logger.info("[%s] repair_manifest FAILED (%.0fs): %s",
                                    task_ref, elapsed, err[:200])
                        return result

                    # Schema gate: validate the new manifest
                    try:
                        manifest_raw = await sandbox.files.read(
                            "/workspace/task/eval_manifest.yaml", format="text")
                        import yaml as _yaml
                        from taskforge.models import EvalManifest
                        EvalManifest.model_validate(_yaml.safe_load(manifest_raw))
                        result.valid = True
                        logger.info("[%s] repair_manifest OK (%.0fs)", task_ref, elapsed)
                    except Exception as schema_err:
                        msg = str(schema_err)[:400]
                        result.valid = False
                        result.error = f"manifest schema invalid: {msg}"
                        logger.warning("[%s] repair_manifest REJECTED (schema): %s",
                                       task_ref, msg[:200])
                        result.total_time = round(time.monotonic() - t_start, 2)
                        return result

                    # Download just the new manifest (not the whole task dir —
                    # tests/Dockerfile/solve.sh weren't touched).
                    new_manifest_text = manifest_raw
                    (dest / "eval_manifest.yaml").write_text(new_manifest_text)
                    result.downloaded = True
                    result.total_time = round(time.monotonic() - t_start, 2)
                    logger.info("[%s] repair_manifest PASS — manifest written to %s",
                                task_ref, dest / "eval_manifest.yaml")
                    if pool and backend:
                        pool.report_success(backend)
                    return result

                # Pre-pull ghcr.io image if available (skips slow Docker build)
                await prepull_task_image(sandbox, task_ref)
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
            # Runs for BOTH code-only and agentmd tasks, ALWAYS (regardless of
            # start_at). task_lint covers the 10 programmatic rubrics (dockerfile
            # determinism, pinned deps, tautological tests, pure-grep tests,
            # zero-p2p, COPY solution/, etc.). The agentmd-specific
            # classify_task_fast only runs when agentmd=True.
            # Always-on because: (a) it's <2s deterministic, (b) we want retrofit
            # mode (--start-at validate) to still get programmatic lint protection.
            if True:
                t0 = time.monotonic()
                verdict, flags = await node_qgate(sandbox, agentmd=agentmd)
                elapsed = time.monotonic() - t0
                result.qgate_verdict = verdict

                await update_sandbox_status(sandbox, "quality_gate", _stamp(
                    "quality_gate", verdict, elapsed, f"flags={flags}"))

                # DELETE semantics:
                # - NEW tasks (scaffold mode): short-circuit — regenerate from scratch.
                # - EXISTING tasks (retrofit mode): record the verdict but CONTINUE
                #   into validate+judge+reconcile so we get a chance to repair.
                if verdict == "DELETE" and is_new:
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

            # ── Node 2b: Gemini CLI Rubric (exact line numbers) ───
            if start_at.should_run(StartAt.RUBRIC) and agentmd and repo_url:
                t0 = time.monotonic()
                cli_status, nr, nd, ns = await node_gemini_cli_rubric(
                    sandbox, repo_url)
                elapsed = time.monotonic() - t0

                await update_sandbox_status(sandbox, "gemini_cli_rubric", {
                    **_stamp("gemini_cli_rubric", cli_status, elapsed,
                             f"+{nr}R +{nd}D skip={ns}"),
                    "model": "gemini-3.1-pro-preview",
                    "rubrics_added": nr,
                    "distractors_added": nd,
                    "skipped": ns,
                })
                logger.info("[%s] gemini CLI rubric: %s +%dR +%dD skip=%d (%.1fs)",
                            result.task_name, cli_status, nr, nd, ns, elapsed)

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
            # If start_at is FIX_QUALITY, skip the old improve node and use the
            # combined fix_task_quality agent instead (fixes tests + instruction
            # together, then validates). Skips to VALIDATE after.
            if start_at in (StartAt.FIX_QUALITY, StartAt.ONESHOT_REPAIR):
                # Oneshot trusts whatever reconcile_status.json the agent writes.
                # Delete any pre-existing copy uploaded with the task so a stale
                # success verdict from a prior run can't be mistaken for a fresh one.
                if start_at == StartAt.ONESHOT_REPAIR:
                    await run_cmd(
                        sandbox,
                        "rm -f /workspace/task/reconcile_status.json",
                    )

                t0 = time.monotonic()
                s, err = await node_fix_task_quality(sandbox)
                elapsed = time.monotonic() - t0
                result.improve_status = s
                result.improve_time = round(elapsed, 2)

                await update_sandbox_status(sandbox, "fix_quality", _stamp(
                    "fix_quality", s, elapsed))
                logger.info("[%s] fix_quality: %s (%.1fs)", result.task_name, s, elapsed)

                if s == "rate_limited":
                    if pool and backend:
                        pool.report_429(backend)
                    result.error = f"rate limited during fix_quality: {err}"
                    raise _RateLimited(result.error)

                # Oneshot mode: trust the agent's verdict from reconcile_status.json
                # and skip the trailing validate/judge/reconcile/tests_rewrite chain.
                if start_at == StartAt.ONESHOT_REPAIR:
                    if s != "ok":
                        result.error = f"oneshot agent {s}: {(err or '')[:200]}"
                        result.valid = False
                        logger.warning("[%s] oneshot: agent did not complete (status=%s)",
                                       result.task_name, s)
                    else:
                        rs_data: dict = {}
                        try:
                            rs_raw = await sandbox.files.read(
                                "/workspace/task/reconcile_status.json", format="text")
                            rs_data = json.loads(rs_raw)
                        except Exception as e:
                            logger.warning("[%s] oneshot: reconcile_status read failed: %s",
                                           result.task_name, str(e)[:80])

                        if rs_data.get("abandoned"):
                            result.error = f"oneshot abandoned: {rs_data.get('reason', '')[:200]}"
                            result.valid = False
                            logger.info("[%s] oneshot ABANDONED: %s",
                                        result.task_name, rs_data.get("reason", "")[:120])
                        elif rs_data.get("fixed"):
                            result.nop_reward = float(rs_data.get("nop_reward", -1))
                            result.gold_reward = float(rs_data.get("gold_reward", -1))
                            result.valid = (result.nop_reward == 0.0 and result.gold_reward == 1.0)
                            logger.info("[%s] oneshot FIXED: nop=%.1f gold=%.1f valid=%s",
                                        result.task_name, result.nop_reward,
                                        result.gold_reward, result.valid)
                        else:
                            result.error = "oneshot: agent wrote no verdict to reconcile_status.json"
                            result.valid = False
                            logger.warning("[%s] oneshot: no verdict produced", result.task_name)

            elif start_at.should_run(StartAt.IMPROVE):
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

            # ── Retrofit: trust prior validation ──────────────────
            # When start_at=JUDGE, we skipped validate_and_fix. The task was
            # validated previously (it's in markdown_following/, meaning it already
            # passed nop=0/gold=1 at download time). Seed result.valid=True from
            # the prior status.json so judge+reconcile nodes run.
            if start_at == StartAt.JUDGE and not result.valid:
                # Read the existing status.json (uploaded with task files)
                prior_status = await read_sandbox_status(sandbox)
                prior_validate = prior_status.get("nodes", {}).get("validate", {})
                result.nop_reward = prior_validate.get("nop_reward", 0.0)
                result.gold_reward = prior_validate.get("gold_reward", 1.0)
                result.valid = (
                    prior_status.get("valid", True)
                    or (result.nop_reward == 0.0 and result.gold_reward == 1.0)
                )
                logger.info("[%s] retrofit: trusting prior nop=%.1f gold=%.1f → valid=%s",
                            result.task_name, result.nop_reward, result.gold_reward, result.valid)

            # ── Node 6a: Rubric Lint (agentmd only) ───────────────
            if result.valid and agentmd and start_at not in (StartAt.ONESHOT_REPAIR, StartAt.ONESHOT_SCAFFOLD):
                injected, samples = await node_rubric_lint(sandbox)
                if injected > 0:
                    await update_sandbox_status(sandbox, "rubric_lint", {
                        "status": "cleaned",
                        "injected_count": injected,
                        "samples": samples,
                    })
                    logger.warning("[%s] RUBRIC TAMPERING: %d injected rules cleaned",
                                   result.task_name, injected)

            # ── Node 6b: Quality Judge (Opus 4.6 via JUDGE_API_KEY) ─
            # Scores task against 10 llm_judge rubrics. Writes quality.json.
            # Runs for BOTH code-only and agentmd tasks.
            judge_summary: dict = {}
            if result.valid and start_at not in (StartAt.ONESHOT_REPAIR, StartAt.ONESHOT_SCAFFOLD):
                t0 = time.monotonic()
                js, judge_summary = await node_quality_judge(sandbox)
                elapsed = time.monotonic() - t0
                result.judge_status = js
                result.judge_summary = judge_summary
                await update_sandbox_status(sandbox, "quality_judge", {
                    "status": js,
                    "time": round(elapsed, 2),
                    **{k: judge_summary.get(k) for k in
                       ["tier_a_fails", "tier_b_fails", "pass_count", "fail_count"]},
                })
                if js == "ok":
                    logger.info("[%s] judge: %d pass, %d fail, tier_a=%s",
                                result.task_name,
                                judge_summary.get("pass_count", 0),
                                judge_summary.get("fail_count", 0),
                                judge_summary.get("tier_a_fails", []))

            # ── Node 6c: Instruction Reconcile (conditional) ──────
            # Runs when the judge flagged instruction-level issues and we think
            # a targeted rewrite can fix them without breaking the oracle.
            INSTRUCTION_RUBRICS = {
                "behavior_in_task_description",
                "no_solution_leakage",
                "instruction_no_hint_leakage",
            }
            reconcile_needed = (
                result.valid
                and result.judge_status == "ok"
                and any(r in INSTRUCTION_RUBRICS
                        for r in judge_summary.get("tier_a_fails", []))
            )
            if reconcile_needed:
                logger.info("[%s] reconcile needed — judge flagged %s",
                            result.task_name,
                            [r for r in judge_summary.get("tier_a_fails", [])
                             if r in INSTRUCTION_RUBRICS])
                t0 = time.monotonic()
                rs, rerr = await node_instruction_reconcile(sandbox)
                elapsed = time.monotonic() - t0
                result.reconcile_status = rs
                result.reconcile_time = round(elapsed, 2)
                if rs == "rate_limited":
                    if pool and backend:
                        pool.report_429(backend)
                    raise _RateLimited(f"rate limited during reconcile: {rerr}")

                # Read reconcile_status.json written by the agent
                rec_data: dict = {}
                try:
                    rec_raw = await sandbox.files.read(
                        "/workspace/task/reconcile_status.json", format="text")
                    rec_data = json.loads(rec_raw)
                    result.reconcile_outcome = rec_data
                except Exception as e:
                    logger.warning("[%s] reconcile_status read failed: %s",
                                   result.task_name, str(e)[:80])

                if rec_data.get("abandoned"):
                    logger.info("[%s] reconcile abandoned: %s",
                                result.task_name, rec_data.get("reason", ""))
                elif rec_data.get("reconciled"):
                    # Agent claims nop=0 and gold=1 still hold. Trust but verify:
                    # rec_data may include reward numbers from the agent's own run.
                    new_nop = rec_data.get("nop_reward")
                    new_gold = rec_data.get("gold_reward")
                    if new_nop is not None:
                        result.nop_reward = float(new_nop)
                    if new_gold is not None:
                        result.gold_reward = float(new_gold)
                    result.valid = (result.nop_reward == 0.0 and result.gold_reward == 1.0)
                    if not result.valid:
                        logger.warning(
                            "[%s] reconcile claimed success but nop=%.1f gold=%.1f",
                            result.task_name, result.nop_reward, result.gold_reward)
                    else:
                        # Re-run judge post-reconcile to confirm instruction issue fixed
                        js2, judge_summary2 = await node_quality_judge(sandbox)
                        result.judge_status_post = js2
                        result.judge_summary_post = judge_summary2
                        logger.info("[%s] post-reconcile judge: %s tier_a=%s",
                                    result.task_name, js2,
                                    judge_summary2.get("tier_a_fails", []))

            # ── Node 6d: Tests Rewrite (conditional) ──────────────
            # Runs when the judge (or post-reconcile judge) still flags
            # test-design rubrics that only a test rewrite can address.
            TEST_RUBRICS = {
                "tests_verify_behavior_not_text",
                "solution_uniqueness_guard",
                "test_not_tautological",
            }
            # Use post-reconcile judge if available, else initial judge
            latest_summary = (result.judge_summary_post
                              if result.judge_summary_post
                              else judge_summary)
            tests_rewrite_needed = (
                result.valid
                and result.judge_status in ("ok", "")
                and any(r in TEST_RUBRICS
                        for r in latest_summary.get("tier_a_fails", []))
            )
            if tests_rewrite_needed:
                logger.info("[%s] tests_rewrite needed — judge flagged %s",
                            result.task_name,
                            [r for r in latest_summary.get("tier_a_fails", [])
                             if r in TEST_RUBRICS])
                t0 = time.monotonic()
                trs, trerr = await node_tests_rewrite(sandbox)
                elapsed = time.monotonic() - t0
                result.tests_rewrite_status = trs
                result.tests_rewrite_time = round(elapsed, 2)
                if trs == "rate_limited":
                    if pool and backend:
                        pool.report_429(backend)
                    raise _RateLimited(f"rate limited during tests_rewrite: {trerr}")

                # Round-3 silent-failure fix: if _run_agent returned "error",
                # the agent never ran → no status file, no test changes. Log
                # visibly and skip the re-judge (stale verdicts shouldn't be
                # overwritten by a re-judge that sees unchanged tests).
                if trs == "error":
                    logger.warning("[%s] tests_rewrite AGENT ERROR (%.1fs): %s",
                                   result.task_name, elapsed, trerr[:200])
                    await update_sandbox_status(sandbox, "tests_rewrite", {
                        "status": "error",
                        "error": trerr[:300],
                        "time": round(elapsed, 2),
                    })
                    # Don't proceed to read status or re-judge — skip to download
                else:
                    # Agent completed (status "ok") — read its output
                    tr_data: dict = {}
                    try:
                        tr_raw = await sandbox.files.read(
                            "/workspace/task/tests_rewrite_status.json", format="text")
                        tr_data = json.loads(tr_raw)
                        result.tests_rewrite_outcome = tr_data
                    except Exception as e:
                        logger.warning("[%s] tests_rewrite_status read failed: %s",
                                       result.task_name, str(e)[:80])

                    if tr_data.get("abandoned"):
                        logger.info("[%s] tests_rewrite abandoned: %s",
                                    result.task_name, tr_data.get("reason", ""))
                    elif tr_data.get("rewritten"):
                        new_nop = tr_data.get("nop_reward")
                        new_gold = tr_data.get("gold_reward")
                        if new_nop is not None:
                            result.nop_reward = float(new_nop)
                        if new_gold is not None:
                            result.gold_reward = float(new_gold)
                        result.valid = (result.nop_reward == 0.0 and result.gold_reward == 1.0)
                        if not result.valid:
                            logger.warning(
                                "[%s] tests_rewrite claimed success but nop=%.1f gold=%.1f",
                                result.task_name, result.nop_reward, result.gold_reward)
                        else:
                            # Re-run judge to confirm test rubrics now pass
                            js3, judge_summary3 = await node_quality_judge(sandbox)
                            result.judge_status_post_tests = js3
                            result.judge_summary_post_tests = judge_summary3
                            logger.info("[%s] post-tests-rewrite judge: %s tier_a=%s",
                                        result.task_name, js3,
                                        judge_summary3.get("tier_a_fails", []))

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
            # Handle the claim FIRST — before any awaits — so a re-cancellation
            # during sandbox/backend cleanup can't strand it. On normal
            # completion (PASS or FAIL) the file stays (sticky). On asyncio
            # cancellation (SIGTERM/SIGINT propagated to tasks) we delete the
            # file so the next run can retry.
            if acquired_claim_path is not None:
                exc = sys.exc_info()[1]
                if isinstance(exc, (asyncio.CancelledError, KeyboardInterrupt)):
                    try:
                        acquired_claim_path.unlink()
                    except FileNotFoundError:
                        pass
                    except Exception:
                        pass
                _unregister_inflight(acquired_claim_path)
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
    err_suffix = f" err={result.error[:120]}" if (not result.valid and result.error) else ""
    logger.info(
        "[%s] %s  nop=%.1f gold=%.1f improve=%s backend=%s start=%s (%.1fs)%s",
        result.task_name, status_str, result.nop_reward, result.gold_reward,
        result.improve_status, result.backend_name, result.start_at, result.total_time,
        err_suffix,
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
    max_retries: int = 4,
    failed_log_path: Path | None = None,
    claim_dir: Path | None = None,
) -> list[WorkerResult]:
    """Dispatch items to E2B sandboxes via async queue with retry.

    If `failed_log_path` is provided, every FAILed task (terminal, not mid-retry)
    is appended there as JSONL with structured failure metadata so the batch can
    be resumed later with a filtered input file.
    """
    sandbox_sem = asyncio.Semaphore(concurrency)
    results: list[WorkerResult] = []
    results_lock = asyncio.Lock()

    # Classifier for failure_type based on WorkerResult fields.
    def _classify_failure(r: WorkerResult) -> str:
        err = (r.error or "").lower()
        if r.scaffold_status == "abandoned":
            return "scaffold_abandoned"   # PR deemed unsuitable by agent
        if r.scaffold_status == "error" or "scaffold failed" in err:
            return "scaffold_error"
        if "rate limit" in err:
            return "rate_limit_exhausted"  # inner + outer retries all failed
        if r.qgate_verdict == "DELETE":
            return "qgate_rejected"
        if r.rubric_status == "abandoned":
            return "rubric_abandoned"
        if r.nop_reward == 1.0 or r.gold_reward == 0.0:
            return "test_contract_failed"  # nop should fail, gold should pass
        if r.nop_reward == -1.0 and r.gold_reward == -1.0 and mode == "pipeline":
            return "validate_unreachable"   # never got to validate node
        if "docker" in err or "build" in err.lower():
            return "docker_build_error"
        if r.error:
            return "other_error"
        return "unknown"

    def _classify_phase(r: WorkerResult) -> str:
        """Which pipeline phase the task died in."""
        if r.scaffold_status in ("abandoned", "error"):
            return "scaffold"
        if not r.task_name:
            return "scaffold"
        if r.qgate_verdict == "DELETE":
            return "qgate"
        if r.rubric_status in ("abandoned", "error"):
            return "rubric"
        if r.improve_status == "error":
            return "improve"
        if r.nop_reward == -1.0 and r.gold_reward == -1.0:
            return "pre_validate"
        if r.nop_reward == 1.0 or r.gold_reward == 0.0:
            return "validate"
        return "unknown"

    failed_log_lock = asyncio.Lock()

    async def _log_failure(r: WorkerResult):
        """Append one FAIL record to failed_tasks.jsonl using fcntl for
        cross-process safety (multiple pipeline processes can share one log)."""
        if failed_log_path is None:
            return
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "pr_ref": r.task_ref,
            "task_name": r.task_name,
            "failure_phase": _classify_phase(r),
            "failure_type": _classify_failure(r),
            "scaffold_status": r.scaffold_status,
            "qgate_verdict": r.qgate_verdict,
            "rubric_status": r.rubric_status,
            "improve_status": r.improve_status,
            "nop_reward": r.nop_reward,
            "gold_reward": r.gold_reward,
            "backend": r.backend_name,
            "start_at": r.start_at,
            "total_time": r.total_time,
            "last_error": (r.error or "")[:300],
        }
        async with failed_log_lock:
            import fcntl
            line = json.dumps(entry) + "\n"
            with failed_log_path.open("a") as fh:
                try:
                    fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
                    fh.write(line)
                    fh.flush()
                finally:
                    try:
                        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
                    except Exception:
                        pass

    # Sentinel object used to tell workers to exit. Must be a distinct object
    # so it cannot collide with real items (which are str or dict).
    _SHUTDOWN = object()

    queue: asyncio.Queue = asyncio.Queue()
    for item in items:
        await queue.put((item, 0))

    total = len(items)
    done_count = 0

    async def worker(worker_id: int):
        nonlocal done_count

        # Stagger startup: each worker waits worker_id * 5s before its
        # first task. Prevents all workers from hitting the LLM backend
        # simultaneously on launch, which triggers rate-limit bursts.
        if worker_id > 0:
            stagger = worker_id * 5 + random.uniform(0, 3)
            await asyncio.sleep(stagger)

        while True:
            # Blocking get — workers park here when queue is empty, rather
            # than exiting. Re-enqueued (rate-limited) items always get picked
            # up, even if every other worker is temporarily busy.
            payload = await queue.get()
            if payload is _SHUTDOWN:
                queue.task_done()
                return
            item, retries = payload

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
                            claim_dir=claim_dir,
                        )
                    else:
                        # Existing task — accept both `task` (legacy) and `task_ref` keys
                        if isinstance(item, str):
                            task_name = item
                        else:
                            task_name = item.get("task_ref") or item.get("task") or item.get("name") or str(item)
                        r = await run_task(
                            task_name, task_dir, pool, sandbox_sem,
                            start_at=start_at,
                            agentmd=agentmd,
                            force=force,
                            claim_dir=claim_dir,
                        )
                else:
                    raise ValueError(f"Unknown mode: {mode}")

                # Re-enqueue on rate limit with backoff delay.
                # Previous design re-enqueued immediately, which meant the task
                # grabbed a backend right away and hammered a still-cooling
                # endpoint. Now we sleep before re-enqueue so the pool cooldown
                # has time to take effect.
                if "rate limited" in (r.error or "").lower() and retries < max_retries:
                    delay = 30 * (2 ** retries) + random.uniform(0, 15)
                    logger.info("Re-enqueueing %s (retry %d/%d) after %.0fs backoff",
                                item, retries + 1, max_retries, delay)
                    await asyncio.sleep(delay)
                    await queue.put((item, retries + 1))
                else:
                    async with results_lock:
                        results.append(r)
                        done_count += 1
                        if done_count % 10 == 0 or r.valid:
                            valid_count = sum(1 for x in results if x.valid)
                            logger.info("Progress: %d/%d done, %d valid", done_count, total, valid_count)
                    # Persist structured FAIL record for resumability.
                    # Skip if the task was simply claimed by another worker —
                    # that's coordination, not a real failure.
                    if not r.valid and "claimed_elsewhere" not in (r.error or ""):
                        await _log_failure(r)

            except Exception as e:
                logger.error("Worker %d error for %s: %s", worker_id, item, e)
                crashed = WorkerResult(
                    task_ref=str(item), mode=mode, error=str(e)[:500]
                )
                async with results_lock:
                    results.append(crashed)
                    done_count += 1
                await _log_failure(crashed)

            finally:
                queue.task_done()

    worker_count = min(concurrency * 2, len(items))
    workers = [asyncio.create_task(worker(i)) for i in range(worker_count)]

    # Heartbeat: log queue + pool state every 2 min so operators can SEE progress
    # during long cooldown waits instead of thinking the pipeline crashed.
    heartbeat_stop = asyncio.Event()

    async def heartbeat():
        while not heartbeat_stop.is_set():
            try:
                await asyncio.wait_for(heartbeat_stop.wait(), timeout=120)
                return
            except asyncio.TimeoutError:
                pass
            try:
                qsize = queue.qsize()
            except Exception:
                qsize = -1
            cooldowns = {}
            if pool is not None:
                now = time.monotonic()
                for s in pool._slots:
                    remaining = max(0, s.cooldown_until - now)
                    if remaining > 0:
                        cooldowns[s.backend.name] = f"{remaining:.0f}s (429s={s.consecutive_429s})"
            async with results_lock:
                valid_n = sum(1 for r in results if r.valid)
                done_n = done_count
            logger.info(
                "HEARTBEAT: done=%d/%d valid=%d queue_pending=%d cooldowns=%s",
                done_n, total, valid_n, qsize,
                cooldowns or "{}"
            )

    heartbeat_task = asyncio.create_task(heartbeat())

    try:
        # Drain barrier: wait until every enqueued item (including re-enqueues)
        # has been task_done()'d. Re-enqueued items keep the unfinished-task
        # counter above zero, so join() only releases once the *transitive*
        # work is done.
        await queue.join()

        # Now tell every worker to exit.
        for _ in range(worker_count):
            await queue.put(_SHUTDOWN)
        await asyncio.gather(*workers)
    finally:
        heartbeat_stop.set()
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except (asyncio.CancelledError, Exception):
            pass

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

    # Per-run failure log (structured JSONL for resumability).
    failed_log_dir = ROOT / "pipeline_logs"
    failed_log_dir.mkdir(exist_ok=True)
    failed_log_path = Path(args.failed_log) if args.failed_log else (
        failed_log_dir / f"failed_tasks_{int(time.time())}.jsonl"
    )
    logger.info("Failed-task log: %s", failed_log_path)

    claim_dir = Path(args.claim_dir) if args.claim_dir else None
    if claim_dir:
        logger.info("Cross-process claim dir: %s", claim_dir)

    wall_start = time.monotonic()
    results = await run_batch(
        items, args.mode, pool, args.concurrency, task_dir,
        start_at=start_at, agentmd=args.agentmd, force=args.force,
        failed_log_path=failed_log_path,
        claim_dir=claim_dir,
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
                        choices=["scaffold", "oneshot_scaffold", "oneshot_repair_manifest", "oneshot_fix_dockerfile", "oneshot_repair_full", "oneshot_full_qa_review", "qgate", "rubric", "enrich", "improve", "validate", "judge"],
                        help="DAG entry point (default: scaffold for --input, validate for existing tasks)")
    parser.add_argument("--task-dir", default="markdown_following")
    parser.add_argument("--tasks", type=str, default=None, help="Comma-sep task names")
    parser.add_argument("--filter", type=str, default=None, help="Glob filter")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--offset", type=int, default=None)
    parser.add_argument("--input", type=str, default=None, help="JSONL file with PR refs")
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--pool", action="store_true", help="Use multi-backend pool")
    parser.add_argument("--agentmd", action="store_true", help="Enable agentmd quality nodes (qgate, rubric, lint)")
    parser.add_argument("--force", action="store_true", help="Force re-process even if task exists on disk")
    parser.add_argument("--failed-log", type=str, default=None,
                        help="Path to failed_tasks.jsonl (default: pipeline_logs/failed_tasks_<ts>.jsonl)")
    parser.add_argument("--claim-dir", type=str, default=None,
                        help="Directory for cross-process PR claims. If set, multiple pipeline "
                             "processes can share an input file and atomically coordinate which PRs "
                             "each one processes. Recommended: './pipeline_claims/'.")
    parser.add_argument("--no-cleanup", action="store_true",
                        help="Skip sandbox cleanup at startup (useful if another batch is running)")
    args = parser.parse_args()

    # Robust sandbox hygiene:
    # 1. Kill any orphaned sandboxes from previous runs (startup cleanup)
    # 2. Install signal handlers so SIGTERM/SIGINT clean up before exit
    # 3. atexit fallback for unexpected exits (but NOT for kill -9)
    if not args.no_cleanup:
        killed = cleanup_orphan_sandboxes(reason="startup")
        if killed > 0:
            logger.info("Startup cleanup: freed %d orphaned sandboxes", killed)
    install_cleanup_handlers()

    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
