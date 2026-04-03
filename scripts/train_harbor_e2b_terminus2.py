"""
Launch RL training on agentsmd-rl Harbor tasks using Tinker API + E2B sandboxes.

Prerequisites:
    export TINKER_API_KEY=tml-...
    export E2B_API_KEY=e2b_...

Usage:
    set -a && source .env && set +a && python scripts/train_harbor_e2b.py
"""

from __future__ import annotations

import asyncio
import logging
import sys
import tomllib
from collections.abc import Awaitable, Callable, Sequence
from datetime import datetime
from pathlib import Path

import chz
from tinker_cookbook import cli_utils, model_info, tokenizer_utils
from tinker_cookbook.recipes.harbor_rl.harbor_env import (
    HARBOR_SYSTEM_PROMPT,
    HarborDataset,
    HarborTask,
    _initial_messages,
)
from tinker_cookbook.recipes.harbor_rl.harbor_tools import HarborBashTool, HarborReward
from tinker_cookbook.renderers import get_renderer
from tinker_cookbook.rl.train import Config, main
from tinker_cookbook.rl.types import Env, EnvGroupBuilder, RLDataset, RLDatasetBuilder
from tinker_cookbook.sandbox import SandboxInterface
from tinker_cookbook.tool_use import build_agent_tool_env
from tinker_cookbook.tool_use.agent_tool_message_env import RewardFn

from e2b_sandbox import E2BSandbox

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s: %(message)s")

HARBOR_TASKS_DIR = Path(__file__).resolve().parent.parent / "harbor_tasks"

# ── Config ──────────────────────────────────────────────────────────────────
MODEL_NAME = "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16"
LORA_RANK = 32
MAX_TOKENS = 8192
MAX_TRAJECTORY_TOKENS = 128 * 1024
TEMPERATURE = 1.0
MAX_TURNS = 200
SANDBOX_TIMEOUT = 3600
COMMAND_TIMEOUT = 120
GRADER_TIMEOUT = 120
GROUP_SIZE = 4
GROUPS_PER_BATCH = 8
LEARNING_RATE = 1e-5

# Factory signature: (env_dir: Path, timeout: int) -> SandboxInterface
E2BSandboxFactory = Callable[[Path, int], Awaitable[SandboxInterface]]

# E2B concurrency: Pro plan allows 100 concurrent sandboxes.
# If you hit 429 rate limits, lower this semaphore and add a sleep:
#   _sandbox_semaphore = asyncio.Semaphore(15)
#   await asyncio.sleep(1.0) inside the factory
_sandbox_semaphore = asyncio.Semaphore(50)


async def e2b_sandbox_factory(env_dir: Path, timeout: int) -> SandboxInterface:
    async with _sandbox_semaphore:
        return await E2BSandbox.create(env_dir=env_dir, timeout=timeout)


class E2BHarborEnvGroupBuilder(EnvGroupBuilder):
    """EnvGroupBuilder using E2B sandboxes instead of Modal."""

    def __init__(
        self,
        task: HarborTask,
        model_name: str,
        renderer_name: str | None,
        max_turns: int,
        group_size: int,
        sandbox_timeout: int = 600,
        command_timeout: int = 120,
        grader_timeout: int = 60,
        max_trajectory_tokens: int = 32 * 1024,
        max_generation_tokens: int | None = None,
        context_overflow_reward: float = -0.1,
        sandbox_factory: E2BSandboxFactory | None = None,
        reward_fn: RewardFn | None = None,
    ):
        self.task = task
        self.model_name = model_name
        self.renderer_name = renderer_name
        self.max_turns = max_turns
        self.group_size = group_size
        self.sandbox_timeout = sandbox_timeout
        self.command_timeout = command_timeout
        self.grader_timeout = grader_timeout
        self.max_trajectory_tokens = max_trajectory_tokens
        self.max_generation_tokens = max_generation_tokens
        self.context_overflow_reward = context_overflow_reward
        self.sandbox_factory = sandbox_factory or e2b_sandbox_factory
        self.reward_fn = reward_fn
        self._sandboxes: list[SandboxInterface] = []

    async def make_envs(self) -> Sequence[Env]:
        self._sandboxes = []
        env_dir = self.task.task_dir / "environment"

        tokenizer = tokenizer_utils.get_tokenizer(self.model_name)
        renderer_name = self.renderer_name or model_info.get_recommended_renderer_name(self.model_name)
        renderer = get_renderer(renderer_name, tokenizer)
        tests_dir = self.task.task_dir / "tests"

        envs = []
        for _ in range(self.group_size):
            sandbox = await self.sandbox_factory(env_dir, self.sandbox_timeout)
            self._sandboxes.append(sandbox)

            bash_tool = HarborBashTool(sandbox, command_timeout=self.command_timeout)
            reward_fn = self.reward_fn or HarborReward(
                tests_dir=tests_dir, sandbox=sandbox, grader_timeout=self.grader_timeout,
            )
            envs.append(
                build_agent_tool_env(
                    renderer=renderer,
                    tools=[bash_tool.bash],
                    initial_messages=_initial_messages(self.task, renderer, bash_tool),
                    reward_fn=reward_fn,
                    max_turns=self.max_turns,
                    max_trajectory_tokens=self.max_trajectory_tokens,
                    max_generation_tokens=self.max_generation_tokens,
                    context_overflow_reward=self.context_overflow_reward,
                )
            )
        return envs

    async def cleanup(self) -> None:
        for sandbox in self._sandboxes:
            try:
                await sandbox.cleanup()
            except Exception:
                pass
        self._sandboxes.clear()

    def logging_tags(self) -> list[str]:
        return ["harbor"]


@chz.chz
class E2BHarborDatasetBuilder(RLDatasetBuilder):
    """Build an RL dataset over Harbor tasks using E2B sandboxes."""

    tasks: list[HarborTask]
    batch_size: int
    group_size: int
    model_name: str
    renderer_name: str | None = None
    max_turns: int = 10
    sandbox_timeout: int = 600
    command_timeout: int = 120
    grader_timeout: int = 60
    max_trajectory_tokens: int = 32 * 1024
    sandbox_factory: E2BSandboxFactory | None = None

    def _make_builders(self, group_size: int) -> list[E2BHarborEnvGroupBuilder]:
        return [
            E2BHarborEnvGroupBuilder(
                task=task,
                model_name=self.model_name,
                renderer_name=self.renderer_name,
                max_turns=self.max_turns,
                group_size=group_size,
                sandbox_timeout=self.sandbox_timeout,
                command_timeout=self.command_timeout,
                grader_timeout=self.grader_timeout,
                max_trajectory_tokens=self.max_trajectory_tokens,
                sandbox_factory=self.sandbox_factory,
            )
            for task in self.tasks
        ]

    async def __call__(self) -> tuple[RLDataset, RLDataset | None]:
        train = HarborDataset(env_group_builders=self._make_builders(self.group_size), batch_size=self.batch_size)
        eval_ = HarborDataset(env_group_builders=self._make_builders(group_size=1), batch_size=self.batch_size)
        return train, eval_


def load_local_tasks(tasks_dir: Path, only: set[str] | None = None) -> list[HarborTask]:
    tasks: list[HarborTask] = []
    for task_dir in sorted(tasks_dir.iterdir()):
        if not task_dir.is_dir():
            continue
        if only and task_dir.name not in only:
            continue
        required = [task_dir / "instruction.md", task_dir / "task.toml",
                     task_dir / "environment" / "Dockerfile", task_dir / "tests" / "test.sh"]
        if not all(p.exists() for p in required):
            continue
        tasks.append(HarborTask(
            task_name=task_dir.name,
            instruction=(task_dir / "instruction.md").read_text(),
            task_dir=task_dir,
            config=tomllib.loads((task_dir / "task.toml").read_text()),
        ))
    return tasks


# Tasks with E2B templates already built and ready
READY_TASKS = {
    "areal-batch-rtensor-http-fetch", "areal-pil-image-serialization",
    "areal-socket-bind-failure-cleanup", "gradio-absolute-path-windows",
    "gradio-browserstate-pydantic-serialization", "gradio-button-scale-parameter",
    "gradio-colorpicker-events", "gradio-connection-lost-error-handling",
    "gradio-custom-component-reload", "gradio-dataframe-nan-sort",
    "gradio-duplicate-block-error-reload", "gradio-on-triggers-type-hints",
    "gradio-reload-annotated-types", "gradio-spaces-reloader-config",
    "gradio-submit-button-example-click", "gradio-sync-generator-cancel-valueerror",
    "nextjs-layout-segment-optimization", "nextjs-turbo-persistence-mmap-alignment",
    "openclaw-discord-reconnect-crash", "openclaw-msteams-stream-reset",
    "openclaw-preserve-reply-indentation", "openclaw-subagent-tool-resolution",
    "openclaw-telegram-empty-reply-crash", "openclaw-telegram-message-split",
    "openclaw-unhandled-stop-reasons", "pytorch-fakeprocessgroup-allgather-uneven",
    "pytorch-inductor-identity-evalf", "ruff-f507-percent-format-nontuple",
    "ruff-ipython-percent-foo-parsing", "ruff-ruf050-parenthesize",
    "ruff-up008-lambda-scope", "sglang-benchmark-random-len-fix",
    "sglang-detokenizer-unbound-fix", "sglang-flux2-tokenization-length",
    "sglang-hfrunner-hang-fix", "sglang-lscpu-topology-fix",
    "slime-encoder-only-attr-missing", "slime-httpx-disable-system-proxy",
    "slime-misc-bugfix-cleanup", "slime-wandb-sglang-metrics",
    "transformers-autoprocessor-hub-kwargs", "transformers-camembert-tied-weights",
    "transformers-perceiver-interpolate-pos", "transformers-supports-tp-pp-plan",
    "vllm-cohere-embed-system-prompt", "vllm-multinode-allreduce-fusion",
    "vllm-tool-parser-indexerror",
}


async def run() -> None:
    tasks = load_local_tasks(HARBOR_TASKS_DIR, only=READY_TASKS)
    print(f"Loaded {len(tasks)} tasks (of {len(READY_TASKS)} with ready E2B templates)")
    if not tasks:
        print("No valid tasks found.")
        sys.exit(1)

    for t in tasks[:10]:
        print(f"  - {t.task_name}")
    if len(tasks) > 10:
        print(f"  ... and {len(tasks) - 10} more")

    renderer_name = model_info.get_recommended_renderer_name(MODEL_NAME)
    model_tag = MODEL_NAME.replace("/", "-")
    run_name = (
        f"harbor-{model_tag}-{LORA_RANK}rank-{LEARNING_RATE}lr-"
        f"{GROUP_SIZE}group-{GROUPS_PER_BATCH}batch-"
        f"{datetime.now().strftime('%Y-%m-%d-%H-%M')}"
    )
    log_path = f"/tmp/tinker-examples/harbor_rl/{run_name}"

    dataset_builder = E2BHarborDatasetBuilder(
        tasks=tasks,
        batch_size=GROUPS_PER_BATCH,
        group_size=GROUP_SIZE,
        model_name=MODEL_NAME,
        renderer_name=renderer_name,
        max_turns=MAX_TURNS,
        sandbox_timeout=SANDBOX_TIMEOUT,
        command_timeout=COMMAND_TIMEOUT,
        grader_timeout=GRADER_TIMEOUT,
        max_trajectory_tokens=MAX_TRAJECTORY_TOKENS,
        sandbox_factory=e2b_sandbox_factory,
    )

    config = Config(
        learning_rate=LEARNING_RATE,
        dataset_builder=dataset_builder,
        model_name=MODEL_NAME,
        lora_rank=LORA_RANK,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        log_path=log_path,
        wandb_name=run_name,
        eval_every=5,
        save_every=5,
        kl_penalty_coef=0.0,
    )

    cli_utils.check_log_dir(log_path, behavior_if_exists="overwrite")
    await main(config)


if __name__ == "__main__":
    asyncio.run(run())
