"""
Harbor Trial integration test: Claude Code CLI in Docker sandbox → Anthropic proxy → Tinker.

This is the real e2e: Harbor builds a Docker image, installs Claude Code CLI,
the CLI calls our proxy (thinking it's the Anthropic API), we capture tokens +
logprobs, Harbor runs the verifier, we get reward + training data.

Requires: TINKER_API_KEY, Docker running.
Slow (~2-5 min per trial due to Docker build + Claude Code install).
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

pytestmark = [
    pytest.mark.skipif(not os.environ.get("TINKER_API_KEY"), reason="TINKER_API_KEY not set"),
    pytest.mark.slow,
]

MODEL_NAME = "Qwen/Qwen3-8B"
LORA_RANK = 16
HARBOR_TASKS_DIR = Path(__file__).resolve().parent.parent / "markdown_following"

# Pick a simple task
TASK_NAME = "areal-batch-rtensor-http-fetch"


@pytest.fixture(scope="module")
def tinker_setup():
    """Set up Tinker clients and proxy."""
    import tinker
    from anthropic_proxy import AnthropicTinkerProxy

    svc = tinker.ServiceClient()

    async def _setup():
        tc = await svc.create_lora_training_client_async(base_model=MODEL_NAME, rank=LORA_RANK)
        path = (await (await tc.save_weights_for_sampler_async("test")).result_async()).path
        sc = svc.create_sampling_client(model_path=path)
        return tc, sc

    tc, sc = asyncio.run(_setup())
    tokenizer = sc.get_tokenizer()

    proxy = AnthropicTinkerProxy(sc, model_name=MODEL_NAME.split("/")[-1])
    # Listen on 0.0.0.0 so Docker containers can reach us
    proxy.start(host="0.0.0.0", port=18340)

    # Docker containers need the host's routable IP (not 127.0.0.1).
    # On WSL2, the Docker bridge gateway doesn't route back to the host.
    # Use the eth0 IP which is reachable from Docker containers.
    import subprocess
    try:
        gw = subprocess.check_output(
            ["ip", "-4", "addr", "show", "eth0"],
            text=True, timeout=5,
        )
        import re
        match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", gw)
        gw = match.group(1) if match else "172.17.0.1"
    except Exception:
        gw = "172.17.0.1"

    yield {
        "training_client": tc,
        "sampling_client": sc,
        "tokenizer": tokenizer,
        "proxy": proxy,
        "proxy_url": f"http://{gw}:18340",
    }

    proxy.stop()


class TestHarborTrialWithClaudeCode:
    """Run a real Harbor Trial with claude-code agent through our proxy."""

    def test_trial_produces_training_data(self, tinker_setup):
        """Full chain: Harbor Trial → Claude Code → proxy → training data.

        This test:
        1. Builds a Docker image from the task's Dockerfile
        2. Installs Claude Code CLI in the container
        3. Claude Code calls our Anthropic proxy (ANTHROPIC_BASE_URL)
        4. Proxy routes to Tinker, captures tokens + logprobs
        5. Harbor runs test.sh → reward
        6. We verify: session has interactions with real logprobs
        """
        from copy import deepcopy
        from uuid import uuid4
        from harbor.models.trial.config import TrialConfig
        from harbor.trial.trial import Trial
        from train import session_to_datums

        proxy = tinker_setup["proxy"]
        tokenizer = tinker_setup["tokenizer"]
        proxy_url = tinker_setup["proxy_url"]

        task_path = HARBOR_TASKS_DIR / TASK_NAME
        assert task_path.exists(), f"Task not found: {task_path}"

        session_id = uuid4().hex
        proxy.create_session(session_id)

        config = {
            "trials_dir": "/tmp/harbor-test-trials",
            "agent": {
                "name": "claude-code",
                "override_timeout_sec": 300,  # 5 min max
                "model_name": MODEL_NAME.split("/")[-1],
                "kwargs": {
                    "max_turns": 5,  # Keep short for testing
                },
                "env": {
                    "ANTHROPIC_BASE_URL": proxy_url,
                    "ANTHROPIC_API_KEY": session_id,
                },
            },
            "environment": {
                "type": "docker",
                "override_cpus": 1,
                "override_memory_mb": 2048,
                "delete": True,
            },
            "verifier": {"disable": False},
            "task": {"path": str(task_path)},
        }

        print(f"\n--- Starting Harbor Trial for {TASK_NAME} ---")
        print(f"Session ID: {session_id}")
        print(f"Proxy URL: {proxy_url}")
        t0 = time.time()

        async def _run():
            trial_config = TrialConfig.model_validate(config)
            trial = await Trial.create(trial_config)
            return await trial.run()

        results = asyncio.run(_run())
        elapsed = time.time() - t0
        print(f"Trial completed in {elapsed:.1f}s")

        # Check trial result
        exc_type = results.exception_info.exception_type if results.exception_info else None
        print(f"Exception type: {exc_type}")

        if results.verifier_result:
            reward = results.verifier_result.rewards.get("reward", 0.0)
            print(f"Reward: {reward}")
        else:
            reward = None
            print("No verifier result")

        # Check proxy captured interactions
        session = proxy.get_session(session_id)
        assert session is not None, "Proxy did not capture any session data"

        n_interactions = len(session.interactions)
        print(f"Proxy captured {n_interactions} interactions")
        assert n_interactions > 0, (
            "Claude Code made zero LLM calls through the proxy. "
            "Check ANTHROPIC_BASE_URL was set correctly in the container."
        )

        # Verify interactions have real data
        for i, interaction in enumerate(session.interactions):
            print(f"  Interaction {i}: "
                  f"prompt={len(interaction.prompt_token_ids)} tokens, "
                  f"output={len(interaction.output_token_ids)} tokens, "
                  f"logprobs={len(interaction.output_logprobs)} values")
            assert len(interaction.output_token_ids) > 0, f"Interaction {i}: no output tokens"
            assert len(interaction.output_logprobs) == len(interaction.output_token_ids), (
                f"Interaction {i}: logprob/token length mismatch"
            )
            # Logprobs should be real (negative) values
            assert any(lp < 0 for lp in interaction.output_logprobs), (
                f"Interaction {i}: all logprobs are non-negative (expected negative log-probs)"
            )

        # Build training datums
        datums = session_to_datums(session, advantage=1.0, tokenizer=tokenizer)
        print(f"Built {len(datums)} training datums")
        assert len(datums) == n_interactions

        # Verify datums are valid
        for i, datum in enumerate(datums):
            n = len(datum.model_input.to_ints())
            assert n > 0, f"Datum {i}: empty model_input"
            assert len(datum.loss_fn_inputs["target_tokens"].to_torch()) == n
            assert len(datum.loss_fn_inputs["logprobs"].to_torch()) == n
            assert len(datum.loss_fn_inputs["advantages"].to_torch()) == n

            lps = datum.loss_fn_inputs["logprobs"].to_torch()
            non_zero = (lps != 0.0).sum().item()
            assert non_zero > 0, f"Datum {i}: all-zero logprobs"

        # Submit to Tinker training (validates format)
        tc = tinker_setup["training_client"]
        fwd_result = tc.forward_backward(datums, loss_fn="importance_sampling").result()
        assert len(fwd_result.loss_fn_outputs) == len(datums)
        print(f"Tinker forward_backward accepted {len(datums)} datums")

        print(f"\n--- PASS: Full chain verified ---")
        print(f"  Task: {TASK_NAME}")
        print(f"  Interactions: {n_interactions}")
        print(f"  Datums: {len(datums)}")
        print(f"  Reward: {reward}")
        print(f"  Time: {elapsed:.1f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=long", "-s"])
