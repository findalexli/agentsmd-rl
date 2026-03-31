"""
RL training on Harbor tasks using Claude Code + Tinker API.

Architecture
============

    Claude Code CLI (inside Harbor sandbox, reads CLAUDE.md naturally)
        │ Anthropic Messages API
        ▼
    AnthropicTinkerProxy (see anthropic_proxy.py)
        │ Captures tokens + logprobs per session at generation time
        ▼
    Tinker SamplingClient → remote GPU

    Harbor Trial.run() orchestrates: Docker sandbox + Claude Code install + verifier
    Proxy session data → per-turn (token_ids, logprobs)
    GRPO advantages → tinker.Datum → Tinker forward_backward + optim_step

Key Design Decisions
====================

1. **Logprobs captured at generation time, not post-hoc** (from AReaL)
   Every LLM call goes through the proxy, which records (prompt_token_ids,
   output_token_ids, output_logprobs) per interaction. No extra forward pass
   (``compute_logprobs_async``) needed. This is the same approach AReaL uses.

2. **Per-turn datums ("individual" style, from AReaL)**
   Each LLM call (interaction) becomes its own ``tinker.Datum``. This preserves
   per-turn logprobs from sampling time. The alternative (one datum per full
   trajectory) would lose logprobs for earlier turns' outputs — they'd be inside
   the "prompt" of later turns and get masked to 0.

   Trade-off: N datums per trajectory (one per turn) means more data through
   ``forward_backward``, but each datum has correct logprobs. AReaL and SkyRL
   both use this approach.

3. **Harbor Trial as a black box**
   Harbor handles: Docker image build, Claude Code CLI install, agent execution,
   tool sandboxing, test verification (``test.sh → reward.txt``). This script
   writes zero agent/tool code. The only bridge is the proxy.

4. **No ``metadata["all_messages"]`` dependency**
   SkyRL's Harbor integration reads ``agent_result.metadata["all_messages"]``
   from terminus-2, which claude-code does NOT set. We don't need it — the proxy
   captures everything.

5. **Docker networking**
   The proxy listens on ``0.0.0.0`` and the Harbor config sets
   ``ANTHROPIC_BASE_URL`` to the host's eth0 IP (not 127.0.0.1, which is the
   container's own localhost). On WSL2, the Docker bridge gateway (172.17.0.1)
   doesn't route back to the host — use the eth0 IP instead.

6. **Logprob divergence is expected (~0.01 mean, ~0.3 max per token)**
   Sampling logprobs (from proxy) vs training logprobs (from ``forward_backward``)
   differ due to different attention kernels. The ``importance_sampling`` loss in
   Tinker handles this via the importance ratio. See ``test_logprob_fidelity.py``
   for measurements and ``anthropic_proxy.py`` docstring for full explanation.

Prerequisites
=============
    export TINKER_API_KEY=tml-...
    # ANTHROPIC_API_KEY is set per-trial by this script (dummy value for CLI check)
    # Docker must be running (Harbor uses it for sandboxes)

Usage
=====
    python claude-code-rl-w-tinker/train.py
    python claude-code-rl-w-tinker/train.py --model_name Qwen/Qwen3.5-35B-A3B --max_steps 10
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

import numpy as np
import tinker
import torch
from tinker.types.tensor_data import TensorData

from harbor.models.trial.config import TrialConfig
from harbor.trial.trial import Trial

# Local
sys.path.insert(0, str(Path(__file__).resolve().parent))
from anthropic_proxy import AnthropicTinkerProxy, SessionData
from harbor_tokenization import get_response_ids_and_loss_mask

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("uvicorn").setLevel(logging.WARNING)

HARBOR_TASKS_DIR = Path(__file__).resolve().parent.parent / "harbor_tasks"


# ── Config ───────────────────────────────────────────────────────────────


@dataclass
class Config:
    model_name: str = "Qwen/Qwen3-8B"
    lora_rank: int = 32
    learning_rate: float = 1e-5
    max_steps: int = 200
    loss_fn: Literal["importance_sampling", "ppo"] = "importance_sampling"

    # GRPO
    group_size: int = 4
    groups_per_batch: int = 8
    normalize_advantages: bool = True

    # Agent / sandbox
    agent_name: str = "claude-code"
    max_turns: int = 200
    max_tokens: int = 8192
    max_input_tokens: int = 32768
    temperature: float = 1.0
    agent_timeout: int = 1200
    environment_type: str = "docker"  # docker, daytona, e2b

    # Proxy
    proxy_port: int = 8321

    # Logging
    save_every: int = 5
    use_wandb: bool = False
    wandb_project: str | None = None
    wandb_name: str | None = None
    log_dir: str = "/tmp/claude-code-rl-logs"

    only_tasks: set[str] | None = None
    max_retries: int = 2
    max_concurrent_trials: int = 16


# ── Harbor Trial Config ──────────────────────────────────────────────────


def make_harbor_config(cfg: Config, proxy_base_url: str) -> dict[str, Any]:
    """Build Harbor TrialConfig template for claude-code agent.

    The proxy speaks Anthropic Messages API at proxy_base_url.
    Claude Code CLI is told to use it via ANTHROPIC_BASE_URL.
    """
    return {
        "trials_dir": os.path.join(cfg.log_dir, "trials"),
        "agent": {
            "name": cfg.agent_name,
            "override_timeout_sec": cfg.agent_timeout,
            # model_name for claude-code: passed as ANTHROPIC_MODEL env var
            "model_name": cfg.model_name.split("/")[-1],
            "kwargs": {
                "max_turns": cfg.max_turns,
            },
            # Env vars injected into the sandbox for claude-code
            "env": {
                "ANTHROPIC_BASE_URL": proxy_base_url,
                "ANTHROPIC_API_KEY": "dummy-for-proxy",
            },
        },
        "environment": {
            "type": cfg.environment_type,
            "override_cpus": 1,
            "override_memory_mb": 1024,
            "delete": True,
        },
        "verifier": {"disable": False},
    }


# ── Task loading ─────────────────────────────────────────────────────────


@dataclass(frozen=True)
class HarborTask:
    name: str
    path: Path


def load_tasks(tasks_dir: Path, only: set[str] | None = None) -> list[HarborTask]:
    tasks = []
    for d in sorted(tasks_dir.iterdir()):
        if not d.is_dir():
            continue
        if only and d.name not in only:
            continue
        required = [d / "instruction.md", d / "task.toml",
                     d / "environment" / "Dockerfile", d / "tests" / "test.sh"]
        if not all(p.exists() for p in required):
            continue
        tasks.append(HarborTask(name=d.name, path=d))
    return tasks


# ── Single trial ─────────────────────────────────────────────────────────


@dataclass
class TrajectoryResult:
    reward: float = 0.0
    session_id: str = ""
    stop_reason: str = "error"
    success: bool = False


async def run_single_trial(
    task: HarborTask,
    config_template: dict[str, Any],
    proxy: AnthropicTinkerProxy,
    semaphore: asyncio.Semaphore,
    max_retries: int = 2,
) -> TrajectoryResult:
    """Run one Harbor trial with claude-code agent."""
    for attempt in range(max_retries):
        # Create a unique session for this trial
        session_id = uuid4().hex
        proxy.create_session(session_id)

        try:
            config = deepcopy(config_template)
            config["task"] = {"path": str(task.path)}

            # For claude-code, we use the session_id in agent env vars
            # so the proxy can associate API calls with this session.
            # Claude Code sends ANTHROPIC_API_KEY as the x-api-key header.
            # We set it to the session_id so the proxy can route.
            config["agent"]["env"]["ANTHROPIC_API_KEY"] = session_id

            trial_config = TrialConfig.model_validate(config)
            trial = await Trial.create(trial_config)

            async with semaphore:
                results = await trial.run()

            exc_type = results.exception_info.exception_type if results.exception_info else None

            if exc_type == "AgentTimeoutError":
                logger.debug(f"Trial {task.name} timed out")
                return TrajectoryResult(stop_reason="agent_timeout", session_id=session_id)

            if exc_type == "ContextLengthExceededError":
                # Check if proxy captured any interactions
                session = proxy.get_session(session_id)
                has_data = session is not None and len(session.interactions) > 0
                return TrajectoryResult(
                    reward=0.0, session_id=session_id,
                    stop_reason="context_length", success=has_data,
                )

            if not results.verifier_result:
                logger.warning(f"Trial {task.name} attempt {attempt+1}: no verifier result")
                proxy.pop_session(session_id)  # cleanup failed session
                continue

            reward = results.verifier_result.rewards.get("reward", 0.0)
            session = proxy.get_session(session_id)
            has_data = session is not None and len(session.interactions) > 0

            if has_data:
                return TrajectoryResult(
                    reward=reward, session_id=session_id,
                    stop_reason="complete", success=True,
                )
            else:
                logger.warning(f"Trial {task.name}: no proxy interactions captured")
                proxy.pop_session(session_id)
                continue

        except Exception as e:
            logger.warning(f"Trial {task.name} attempt {attempt+1}: {e}")
            proxy.pop_session(session_id)
            continue

    return TrajectoryResult(stop_reason="error")


# ── GRPO ─────────────────────────────────────────────────────────────────


def compute_grpo_advantages(rewards: list[float], group_size: int) -> list[float]:
    rewards_np = np.array(rewards)
    n_groups = len(rewards_np) // group_size
    advantages = []
    for i in range(n_groups):
        group = rewards_np[i * group_size:(i + 1) * group_size]
        group_std = group.std()
        if group_std < 1e-8:
            advantages.extend([0.0] * group_size)
        else:
            advantages.extend(((group - group.mean()) / (group_std + 1e-8)).tolist())
    return advantages


# ── Build Datum from proxy-captured session ──────────────────────────────


def session_to_datums(
    session: SessionData,
    advantage: float,
    tokenizer,
) -> list[tinker.types.Datum]:
    """Convert proxy-captured session data into Tinker Datums for training.

    Uses AReaL's "individual" style: each interaction (LLM call) becomes
    its own Datum. This preserves per-turn logprobs from sampling time.

    For each interaction the proxy captured:
    - prompt_token_ids: full conversation so far (chat-templated)
    - output_token_ids: tokens the model generated this turn
    - output_logprobs: per-token logprobs from sampling time (behavior policy)

    Each Datum has:
    - model_input: full_seq[:-1] (shifted for next-token prediction)
    - target_tokens: full_seq[1:]
    - logprobs: 0 for prompt, real for output (shifted)
    - advantages: applied only on output tokens

    Reference: AReaL/areal/experimental/openai/types.py:to_tensor_dict()
               SkyRL/skyrl-agent/.../tinker_train.py:434
    """
    if not session.interactions:
        return []

    datums = []
    for interaction in session.interactions:
        prompt_ids = interaction.prompt_token_ids
        output_ids = interaction.output_token_ids
        output_lps = interaction.output_logprobs

        if not output_ids:
            continue

        full_seq = prompt_ids + output_ids
        prompt_len = len(prompt_ids)

        # Shift for next-token prediction (Tinker convention)
        target_tokens = full_seq[1:]
        logprobs = ([0.0] * prompt_len + list(output_lps))[1:]

        # Advantages: uniform on output tokens, 0 on prompt
        adv_tensor = torch.zeros(len(full_seq))
        for j in range(prompt_len, len(full_seq)):
            adv_tensor[j] = advantage
        adv_tensor = adv_tensor[1:]

        datums.append(tinker.types.Datum(
            model_input=tinker.types.ModelInput.from_ints(tokens=full_seq[:-1]),
            loss_fn_inputs={
                "target_tokens": TensorData.from_torch(torch.tensor(target_tokens)),
                "logprobs": TensorData.from_torch(torch.tensor(logprobs)),
                "advantages": TensorData.from_torch(adv_tensor),
            },
        ))

    return datums


# ── Training loop ────────────────────────────────────────────────────────


async def run(cfg: Config) -> None:
    tasks = load_tasks(HARBOR_TASKS_DIR, only=cfg.only_tasks)
    logger.info(f"Loaded {len(tasks)} tasks")
    if not tasks:
        logger.error("No valid tasks found")
        sys.exit(1)

    os.makedirs(cfg.log_dir, exist_ok=True)

    # Tinker service
    svc = tinker.ServiceClient()
    tc = await svc.create_lora_training_client_async(
        base_model=cfg.model_name, rank=cfg.lora_rank,
    )
    adam_params = tinker.types.AdamParams(
        learning_rate=cfg.learning_rate, beta1=0.9, beta2=0.95, eps=1e-8,
    )

    # Initial sampling client + tokenizer (from Tinker, no transformers needed)
    sampling_path = (await (await tc.save_weights_for_sampler_async("init")).result_async()).path
    sc = svc.create_sampling_client(model_path=sampling_path)
    tokenizer = sc.get_tokenizer()

    # Start Anthropic proxy
    proxy = AnthropicTinkerProxy(sc, model_name=cfg.model_name.split("/")[-1])
    proxy.start(port=cfg.proxy_port)
    proxy_base_url = f"http://127.0.0.1:{cfg.proxy_port}"

    harbor_template = make_harbor_config(cfg, proxy_base_url)
    semaphore = asyncio.Semaphore(cfg.max_concurrent_trials)

    if cfg.use_wandb:
        import wandb
        wandb.init(project=cfg.wandb_project, name=cfg.wandb_name or f"cc-rl-{datetime.now():%m%d-%H%M}")

    # Training loop
    task_idx = 0
    for step in range(cfg.max_steps):
        t0 = time.time()
        metrics: dict[str, Any] = {"step": step}

        # Select batch
        batch_tasks: list[HarborTask] = []
        for _ in range(cfg.groups_per_batch):
            batch_tasks.append(tasks[task_idx % len(tasks)])
            task_idx += 1

        # Run trials
        logger.info(f"[Step {step}] {len(batch_tasks)} tasks x {cfg.group_size} trajectories")
        trial_coros = []
        for task in batch_tasks:
            for _ in range(cfg.group_size):
                trial_coros.append(run_single_trial(
                    task, harbor_template, proxy, semaphore, max_retries=cfg.max_retries,
                ))
        trial_results: list[TrajectoryResult] = await asyncio.gather(*trial_coros)
        metrics["time/rollout"] = time.time() - t0

        # Instance-level masking
        masked_groups: set[int] = set()
        for i, r in enumerate(trial_results):
            group_idx = i // cfg.group_size
            if r.stop_reason in ("error", "agent_timeout"):
                masked_groups.add(group_idx)

        # Collect successful sessions + rewards
        session_data_list: list[SessionData | None] = []
        all_rewards: list[float] = []
        n_success = 0
        n_masked = 0

        for i, r in enumerate(trial_results):
            group_idx = i // cfg.group_size
            if group_idx in masked_groups or not r.success:
                session_data_list.append(None)
                all_rewards.append(0.0)
                n_masked += 1
                if r.session_id:
                    proxy.pop_session(r.session_id)
                continue

            session = proxy.get_session(r.session_id)
            if session and session.interactions:
                session.reward = r.reward
                session_data_list.append(session)
                all_rewards.append(r.reward)
                n_success += 1
            else:
                session_data_list.append(None)
                all_rewards.append(0.0)
                n_masked += 1

        metrics["n_success"] = n_success
        metrics["n_masked"] = n_masked
        metrics["reward/mean"] = float(np.mean(all_rewards))
        logger.info(f"[Step {step}] {n_success} ok, {n_masked} masked, reward={metrics['reward/mean']:.3f}")

        if n_success == 0:
            logger.warning(f"[Step {step}] All failed, skipping")
            continue

        # GRPO advantages
        advantages = compute_grpo_advantages(all_rewards, group_size=cfg.group_size)

        # Build datums — logprobs come from proxy capture, no extra forward pass.
        # Each interaction (LLM call) becomes its own Datum, preserving
        # per-turn logprobs. Reference: AReaL "individual" export style.
        training_datums = []
        for idx, (session, adv) in enumerate(zip(session_data_list, advantages)):
            if session is None:
                continue
            datums = session_to_datums(session, adv, tokenizer)
            training_datums.extend(datums)
            proxy.pop_session(session.session_id)

        if not training_datums:
            logger.warning(f"[Step {step}] No datums")
            continue

        # Train
        t_train = time.time()
        fwd_bwd_future = tc.forward_backward(training_datums, loss_fn=cfg.loss_fn)
        optim_future = tc.optim_step(adam_params)
        _ = fwd_bwd_future.result()
        _ = optim_future.result()
        metrics["time/train"] = time.time() - t_train

        # Weight sync
        t_sync = time.time()
        sampling_path = tc.save_weights_for_sampler(name=f"step_{step:04d}").result().path
        sc = svc.create_sampling_client(model_path=sampling_path)
        proxy.update_client(sc)
        metrics["time/weight_sync"] = time.time() - t_sync
        metrics["time/total"] = time.time() - t0

        logger.info(f"[Step {step}] train={metrics['time/train']:.1f}s total={metrics['time/total']:.1f}s")

        if cfg.save_every > 0 and (step + 1) % cfg.save_every == 0:
            await (await tc.save_state_async(f"step_{step:04d}")).result_async()

        if cfg.use_wandb:
            import wandb
            wandb.log(metrics, step=step)

    proxy.stop()
    if cfg.use_wandb:
        import wandb
        wandb.finish()
    logger.info("Training complete")


def parse_args() -> Config:
    import argparse
    parser = argparse.ArgumentParser()
    cfg = Config()
    for name, default in vars(cfg).items():
        if name == "only_tasks":
            parser.add_argument(f"--{name}", type=str, default=None)
        elif isinstance(default, bool):
            parser.add_argument(f"--{name}", action="store_true", default=default)
        elif isinstance(default, (int, float, str)):
            parser.add_argument(f"--{name}", type=type(default), default=default)
    args = parser.parse_args()
    d = vars(args)
    if d.get("only_tasks"):
        d["only_tasks"] = set(d["only_tasks"].split(","))
    return Config(**{k: v for k, v in d.items() if v is not None or k == "only_tasks"})


if __name__ == "__main__":
    cfg = parse_args()
    asyncio.run(run(cfg))
