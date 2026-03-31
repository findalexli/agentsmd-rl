"""
Multi-turn Harbor Trial test with different models.

Tests that Claude Code makes MULTIPLE tool calls (multi-turn) through our proxy.
Compares Qwen3.5-35B-A3B and Kimi-K2.5.
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

HARBOR_TASKS_DIR = Path(__file__).resolve().parent.parent / "harbor_tasks"
TASK_NAME = "areal-batch-rtensor-http-fetch"

# Get host IP for Docker
import subprocess, re
try:
    _ip_out = subprocess.check_output(["ip", "-4", "addr", "show", "eth0"], text=True, timeout=5)
    HOST_IP = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", _ip_out).group(1)
except Exception:
    HOST_IP = "172.17.0.1"


def run_trial_with_model(model_name: str, port: int, max_turns: int = 10):
    """Run a Harbor Trial with claude-code agent using the given model."""
    import tinker
    from uuid import uuid4
    from copy import deepcopy
    from harbor.models.trial.config import TrialConfig
    from harbor.trial.trial import Trial
    from anthropic_proxy import AnthropicTinkerProxy
    from train import session_to_datums

    print(f"\n{'='*60}")
    print(f"MODEL: {model_name}")
    print(f"{'='*60}")

    # Create Tinker clients
    svc = tinker.ServiceClient()

    async def _setup():
        tc = await svc.create_lora_training_client_async(base_model=model_name, rank=16)
        path = (await (await tc.save_weights_for_sampler_async("test")).result_async()).path
        sc = svc.create_sampling_client(model_path=path)
        return tc, sc

    tc, sc = asyncio.run(_setup())
    tokenizer = sc.get_tokenizer()

    # Determine context window from model
    ctx_window = 32768
    if "Qwen3.5" in model_name:
        ctx_window = 65536
    print(f"Context window: {ctx_window}")

    # Start proxy
    proxy = AnthropicTinkerProxy(sc, model_name=model_name.split("/")[-1])
    proxy._model_max_ctx = ctx_window  # TODO: make this a proper config
    proxy.start(host="0.0.0.0", port=port)
    proxy_url = f"http://{HOST_IP}:{port}"

    session_id = uuid4().hex
    proxy.create_session(session_id)

    config = {
        "trials_dir": f"/tmp/harbor-multi-turn-{model_name.split('/')[-1]}",
        "agent": {
            "name": "claude-code",
            "override_timeout_sec": 600,
            "model_name": model_name.split("/")[-1],
            "kwargs": {"max_turns": max_turns},
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
        "task": {"path": str(HARBOR_TASKS_DIR / TASK_NAME)},
    }

    print(f"Proxy: {proxy_url}")
    print(f"Session: {session_id}")
    t0 = time.time()

    async def _run():
        trial_config = TrialConfig.model_validate(config)
        trial = await Trial.create(trial_config)
        return await trial.run()

    results = asyncio.run(_run())
    elapsed = time.time() - t0

    exc_type = results.exception_info.exception_type if results.exception_info else None
    reward = results.verifier_result.rewards.get("reward", 0.0) if results.verifier_result else None

    session = proxy.get_session(session_id)
    n_interactions = len(session.interactions) if session else 0

    print(f"\nRESULTS ({model_name.split('/')[-1]}):")
    print(f"  Time: {elapsed:.1f}s")
    print(f"  Exception: {exc_type}")
    print(f"  Reward: {reward}")
    print(f"  Interactions (LLM calls): {n_interactions}")

    if session and n_interactions > 0:
        for i, interaction in enumerate(session.interactions):
            has_lps = len(interaction.output_logprobs) > 0
            print(f"  Turn {i}: prompt={len(interaction.prompt_token_ids)} tok, "
                  f"output={len(interaction.output_token_ids)} tok, "
                  f"logprobs={'YES' if has_lps else 'NO'}")

        datums = session_to_datums(session, advantage=1.0, tokenizer=tokenizer)
        print(f"  Datums built: {len(datums)}")

        # Verify datums with Tinker
        if datums:
            fwd = tc.forward_backward(datums[:3], loss_fn="importance_sampling")  # first 3 only
            fwd.result()
            print(f"  Tinker forward_backward: ACCEPTED ({min(3, len(datums))} datums)")
    else:
        print("  NO INTERACTIONS CAPTURED — model did not make tool calls through proxy")
        # Check trial log for clues
        trial_dir = config["trials_dir"]
        log_files = list(Path(trial_dir).rglob("claude-code.txt"))
        if log_files:
            import json
            with open(log_files[0]) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        ev = json.loads(line)
                        if ev.get("type") == "system" and ev.get("subtype") == "api_retry":
                            print(f"    API retry: attempt={ev.get('attempt')} error={ev.get('error')}")
                        elif ev.get("type") == "result":
                            print(f"    Result: {ev.get('result', '')[:200]}")
                    except:
                        pass

    proxy.stop()
    return {
        "model": model_name,
        "interactions": n_interactions,
        "reward": reward,
        "elapsed": elapsed,
    }


if __name__ == "__main__":
    if not os.environ.get("TINKER_API_KEY"):
        print("TINKER_API_KEY not set")
        sys.exit(1)

    models = [
        ("Qwen/Qwen3.5-35B-A3B", 18350),
        # ("moonshotai/Kimi-K2.5", 18351),     # uncomment to test Kimi
        # ("Qwen/Qwen3-8B", 18352),            # baseline (known to work but no tools)
    ]

    results = []
    for model_name, port in models:
        try:
            r = run_trial_with_model(model_name, port, max_turns=10)
            results.append(r)
        except Exception as e:
            print(f"\nFAILED: {model_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append({"model": model_name, "interactions": 0, "error": str(e)})

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for r in results:
        print(f"  {r['model'].split('/')[-1]:30s} interactions={r.get('interactions',0):3d}  "
              f"reward={r.get('reward','N/A')}  time={r.get('elapsed',0):.0f}s")
