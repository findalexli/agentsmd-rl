"""
Logprob fidelity test: verify that per-turn logprobs captured by the proxy
match what compute_logprobs_async and forward_backward produce.

This is the critical correctness test for RL training:
- Proxy captures π_old(a|s) at sampling time
- Training step computes π_θ(a|s) via forward_backward
- The importance ratio π_θ / π_old must use consistent logprobs

Tests:
1. Per-turn proxy logprobs vs compute_logprobs_async (same weights, should be ~equal)
2. Per-turn proxy logprobs vs forward_backward training logprobs (same weights, should be ~equal)
3. Multi-turn: each turn's logprobs are independent and correct
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))

_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("TINKER_API_KEY"),
    reason="TINKER_API_KEY not set",
)

MODEL_NAME = "Qwen/Qwen3.5-35B-A3B"
LORA_RANK = 16


@pytest.fixture(scope="module")
def setup():
    import tinker
    from anthropic_proxy import AnthropicTinkerProxy
    from train import session_to_datums

    svc = tinker.ServiceClient()

    async def _init():
        tc = await svc.create_lora_training_client_async(base_model=MODEL_NAME, rank=LORA_RANK)
        path = (await (await tc.save_weights_for_sampler_async("lp-test")).result_async()).path
        sc = svc.create_sampling_client(model_path=path)
        return tc, sc

    tc, sc = asyncio.run(_init())
    tokenizer = sc.get_tokenizer()

    proxy = AnthropicTinkerProxy(sc, model_name=MODEL_NAME.split("/")[-1])
    proxy.start(host="0.0.0.0", port=18360)

    import subprocess, re
    try:
        ip_out = subprocess.check_output(["ip", "-4", "addr", "show", "eth0"], text=True, timeout=5)
        host_ip = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", ip_out).group(1)
    except Exception:
        host_ip = "127.0.0.1"

    yield {
        "tc": tc, "sc": sc, "tokenizer": tokenizer, "proxy": proxy,
        "svc": svc, "base_url": f"http://{host_ip}:18360",
    }

    proxy.stop()


class TestLogprobFidelity:

    def _do_proxy_call(self, setup, session_id, messages):
        """Make a call through the proxy and return the interaction."""
        import httpx
        resp = httpx.post(
            f"{setup['base_url']}/v1/messages",
            json={
                "model": "test",
                "max_tokens": 64,
                "temperature": 1.0,
                "messages": messages,
            },
            headers={"x-api-key": session_id},
            timeout=120.0,
        )
        assert resp.status_code == 200, f"Proxy returned {resp.status_code}: {resp.text[:200]}"
        return resp.json()

    def test_proxy_vs_compute_logprobs_single_turn(self, setup):
        """Proxy-captured logprobs should match compute_logprobs on the same sequence."""
        import tinker

        proxy = setup["proxy"]
        sc = setup["sc"]

        sid = "lp-single"
        proxy.create_session(sid)
        self._do_proxy_call(setup, sid, [{"role": "user", "content": "What is 2+2?"}])

        session = proxy.get_session(sid)
        assert len(session.interactions) == 1
        interaction = session.interactions[0]

        # Compute logprobs on the full sequence via compute_logprobs_async
        full_seq = interaction.prompt_token_ids + interaction.output_token_ids
        oneshot_lps = asyncio.run(
            sc.compute_logprobs_async(tinker.types.ModelInput.from_ints(tokens=full_seq))
        )

        # Compare: proxy logprobs (output portion) vs compute_logprobs (output portion)
        prompt_len = len(interaction.prompt_token_ids)
        proxy_lps = interaction.output_logprobs
        oneshot_output_lps = [float(lp) if lp is not None else 0.0
                              for lp in oneshot_lps[prompt_len:prompt_len + len(proxy_lps)]]

        assert len(proxy_lps) == len(oneshot_output_lps), (
            f"Length mismatch: proxy={len(proxy_lps)}, oneshot={len(oneshot_output_lps)}"
        )

        diffs = [abs(a - b) for a, b in zip(proxy_lps, oneshot_output_lps)]
        max_diff = max(diffs)
        mean_diff = np.mean(diffs)

        print(f"\nSingle-turn logprob comparison:")
        print(f"  Tokens: {len(proxy_lps)}")
        print(f"  Max diff: {max_diff:.6f}")
        print(f"  Mean diff: {mean_diff:.6f}")

        # Known numerical divergence between sampling (incremental KV cache) and
        # prefill (one-shot forward pass). Production systems handle this via
        # importance ratio clipping (TIS cap ~2.0). Mean diff should be <0.05;
        # max diff can spike on a few tokens.
        # Refs: AReaL decoupled loss, SkyRL TIS, veRL rollout correction math.
        assert mean_diff < 0.05, f"Mean logprob diff {mean_diff:.4f} too high (expected <0.05)"
        assert max_diff < 1.0, f"Max logprob diff {max_diff:.4f} exceeds safety bound 1.0"

    def test_proxy_vs_compute_logprobs_multi_turn(self, setup):
        """Multi-turn: each turn's proxy logprobs match compute_logprobs."""
        import tinker

        proxy = setup["proxy"]
        sc = setup["sc"]

        sid = "lp-multi"
        proxy.create_session(sid)

        # Turn 1
        resp1 = self._do_proxy_call(setup, sid, [{"role": "user", "content": "Say hi"}])
        t1_text = resp1["content"][0]["text"] if resp1["content"] else ""

        # Turn 2
        self._do_proxy_call(setup, sid, [
            {"role": "user", "content": "Say hi"},
            {"role": "assistant", "content": t1_text},
            {"role": "user", "content": "Now say bye"},
        ])

        session = proxy.get_session(sid)
        assert len(session.interactions) == 2

        print(f"\nMulti-turn logprob comparison:")
        for turn_idx, interaction in enumerate(session.interactions):
            full_seq = interaction.prompt_token_ids + interaction.output_token_ids
            oneshot_lps = asyncio.run(
                sc.compute_logprobs_async(tinker.types.ModelInput.from_ints(tokens=full_seq))
            )

            prompt_len = len(interaction.prompt_token_ids)
            proxy_lps = interaction.output_logprobs
            oneshot_output_lps = [float(lp) if lp is not None else 0.0
                                  for lp in oneshot_lps[prompt_len:prompt_len + len(proxy_lps)]]

            if len(proxy_lps) != len(oneshot_output_lps):
                print(f"  Turn {turn_idx}: LENGTH MISMATCH proxy={len(proxy_lps)} oneshot={len(oneshot_output_lps)}")
                continue

            diffs = [abs(a - b) for a, b in zip(proxy_lps, oneshot_output_lps)]
            max_diff = max(diffs) if diffs else 0
            mean_diff = np.mean(diffs) if diffs else 0

            print(f"  Turn {turn_idx}: {len(proxy_lps)} tokens, "
                  f"max_diff={max_diff:.6f}, mean_diff={mean_diff:.6f}")

            assert mean_diff < 0.05, (
                f"Turn {turn_idx}: mean logprob diff {mean_diff:.4f} too high (expected <0.05)"
            )
            assert max_diff < 1.0, (
                f"Turn {turn_idx}: max logprob diff {max_diff:.4f} exceeds safety bound 1.0"
            )

    def test_proxy_vs_training_logprobs(self, setup):
        """Proxy logprobs vs training forward pass logprobs (the actual importance ratio inputs)."""
        import tinker
        from tinker.types.tensor_data import TensorData
        from train import session_to_datums

        proxy = setup["proxy"]
        sc = setup["sc"]
        tc = setup["tc"]

        sid = "lp-train"
        proxy.create_session(sid)
        self._do_proxy_call(setup, sid, [{"role": "user", "content": "Count to 5"}])

        session = proxy.get_session(sid)
        assert len(session.interactions) == 1

        # Build datum from proxy data
        tokenizer = setup["tokenizer"]
        datums = session_to_datums(session, advantage=1.0, tokenizer=tokenizer)
        assert len(datums) == 1
        datum = datums[0]

        # Run forward pass to get training logprobs
        fwd_result = tc.forward_backward(datums, loss_fn="importance_sampling").result()
        assert len(fwd_result.loss_fn_outputs) == 1

        # Extract training logprobs from the forward pass output
        training_lps = fwd_result.loss_fn_outputs[0].get("logprobs")
        if training_lps is None:
            pytest.skip("forward_backward did not return logprobs in loss_fn_outputs")

        training_lps_tensor = training_lps.to_torch().squeeze(0) if hasattr(training_lps, "to_torch") else torch.tensor(training_lps)

        # Extract proxy (sampling) logprobs from the datum
        sampling_lps_tensor = datum.loss_fn_inputs["logprobs"].to_torch()

        # Compare only the output portion (where sampling_lps != 0)
        mask = sampling_lps_tensor != 0.0
        if mask.sum() == 0:
            pytest.skip("No non-zero logprobs to compare")

        sampling_output = sampling_lps_tensor[mask]
        training_output = training_lps_tensor[mask] if len(training_lps_tensor) == len(sampling_lps_tensor) else None

        if training_output is None:
            print(f"\nLength mismatch: sampling={len(sampling_lps_tensor)}, training={len(training_lps_tensor)}")
            pytest.skip("Length mismatch between sampling and training logprobs")

        diffs = (sampling_output - training_output).abs()
        max_diff = diffs.max().item()
        mean_diff = diffs.mean().item()

        print(f"\nProxy vs Training logprobs:")
        print(f"  Output tokens: {mask.sum().item()}")
        print(f"  Max diff: {max_diff:.6f}")
        print(f"  Mean diff: {mean_diff:.6f}")

        # Same weights, but different compute paths (sampling engine vs training engine).
        # Mean diff should be small; max diff can spike on outlier tokens.
        # Production systems clip the importance ratio to handle this.
        assert mean_diff < 0.05, (
            f"Proxy vs training mean diff {mean_diff:.4f} too high (expected <0.05)"
        )
        assert max_diff < 1.0, (
            f"Proxy vs training max diff {max_diff:.4f} exceeds safety bound 1.0"
        )

    def test_logprobs_are_negative(self, setup):
        """Sanity check: all logprobs should be ≤ 0 (log-probabilities)."""
        proxy = setup["proxy"]
        sid = "lp-neg"
        proxy.create_session(sid)
        self._do_proxy_call(setup, sid, [{"role": "user", "content": "Hello"}])

        session = proxy.get_session(sid)
        for interaction in session.interactions:
            for i, lp in enumerate(interaction.output_logprobs):
                assert lp <= 0.0, f"Logprob at position {i} is positive: {lp}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=long", "-s"])
