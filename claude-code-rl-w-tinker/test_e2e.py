"""
End-to-end integration tests for claude-code-rl-w-tinker.

Requires:
    - TINKER_API_KEY set (or loaded from .env)
    - Network access to Tinker service

Tests the full chain:
    1. Tinker ServiceClient → TrainingClient → SamplingClient
    2. Tokenizer from SamplingClient (no transformers dependency)
    3. Anthropic proxy startup + message handling + logprob capture
    4. Session management + training data extraction
    5. Datum construction + Tinker forward_backward
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from train import session_to_datums

# Load .env if present
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


# Skip all if no Tinker key
pytestmark = pytest.mark.skipif(
    not os.environ.get("TINKER_API_KEY"),
    reason="TINKER_API_KEY not set",
)

MODEL_NAME = "Qwen/Qwen3-8B"
LORA_RANK = 16


# ── Fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def tinker_clients():
    """Create Tinker training + sampling clients (module-scoped, reused)."""
    import tinker

    svc = tinker.ServiceClient()

    async def _setup():
        tc = await svc.create_lora_training_client_async(
            base_model=MODEL_NAME, rank=LORA_RANK,
        )
        path = (await (await tc.save_weights_for_sampler_async("test")).result_async()).path
        sc = svc.create_sampling_client(model_path=path)
        return tc, sc

    tc, sc = asyncio.run(_setup())
    yield tc, sc


@pytest.fixture(scope="module")
def tokenizer(tinker_clients):
    """Get tokenizer from SamplingClient."""
    _, sc = tinker_clients
    return sc.get_tokenizer()


@pytest.fixture(scope="module")
def sampling_client(tinker_clients):
    _, sc = tinker_clients
    return sc


@pytest.fixture(scope="module")
def training_client(tinker_clients):
    tc, _ = tinker_clients
    return tc


# ── Test 1: Tinker tokenizer works ──────────────────────────────────────


class TestTinkerTokenizer:
    def test_tokenizer_available(self, tokenizer):
        """SamplingClient.get_tokenizer() returns a usable tokenizer."""
        assert tokenizer is not None
        assert hasattr(tokenizer, "encode")
        assert hasattr(tokenizer, "decode")

    def test_chat_template(self, tokenizer):
        """Tokenizer has apply_chat_template for multi-turn conversations."""
        assert hasattr(tokenizer, "apply_chat_template")
        messages = [
            {"role": "user", "content": "Hello"},
        ]
        ids = tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=True, return_dict=False,
        )
        assert isinstance(ids, list)
        assert len(ids) > 0
        assert all(isinstance(i, int) for i in ids)

    def test_eos_token(self, tokenizer):
        """Tokenizer has eos_token_id (needed for loss mask computation)."""
        assert hasattr(tokenizer, "eos_token_id")
        assert isinstance(tokenizer.eos_token_id, int)


# ── Test 2: Tinker sampling + logprobs ───────────────────────────────────


class TestTinkerSampling:
    def test_sample_returns_tokens_and_logprobs(self, sampling_client, tokenizer):
        """SamplingClient.sample() returns tokens with logprobs."""
        import tinker

        messages = [{"role": "user", "content": "What is 2+2?"}]
        prompt_ids = tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=True, return_dict=False,
        )

        result = asyncio.run(sampling_client.sample_async(
            prompt=tinker.types.ModelInput.from_ints(tokens=prompt_ids),
            num_samples=1,
            sampling_params=tinker.SamplingParams(max_tokens=32, temperature=1.0),
        ))

        sample = result.sequences[0]
        assert hasattr(sample, "tokens")
        assert len(sample.tokens) > 0

        # Logprobs should be available
        logprobs = getattr(sample, "logprobs", None) or getattr(sample, "maybe_logprobs", None)
        if logprobs is not None:
            assert len(logprobs) == len(sample.tokens)
            # Logprobs should be negative (log probabilities)
            assert all(lp <= 0.0 for lp in logprobs if lp is not None)

    def test_compute_logprobs(self, sampling_client, tokenizer):
        """compute_logprobs_async returns per-token logprobs for existing tokens."""
        import tinker

        tokens = tokenizer.encode("Hello world, this is a test.")
        result = asyncio.run(
            sampling_client.compute_logprobs_async(
                tinker.types.ModelInput.from_ints(tokens=tokens)
            )
        )
        assert result is not None
        assert len(result) == len(tokens)


# ── Test 3: Proxy startup + Anthropic message handling ───────────────────


class TestAnthropicProxy:
    @pytest.fixture(autouse=True)
    def setup_proxy(self, sampling_client):
        """Start proxy for each test, stop after."""
        from anthropic_proxy import AnthropicTinkerProxy

        self.proxy = AnthropicTinkerProxy(
            sampling_client, model_name="test-model",
        )
        self.proxy.start(port=18321)
        self.base_url = "http://127.0.0.1:18321"
        yield
        self.proxy.stop()

    def test_health_endpoint(self):
        import httpx
        resp = httpx.get(f"{self.base_url}/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_models_endpoint(self):
        import httpx
        resp = httpx.get(f"{self.base_url}/v1/models")
        assert resp.status_code == 200
        assert resp.json()["data"][0]["id"] == "test-model"

    def test_anthropic_messages_non_streaming(self):
        """POST /v1/messages returns a valid Anthropic response with content."""
        import httpx

        # Create a session so the proxy captures the interaction
        self.proxy.create_session("test-session")

        resp = httpx.post(
            f"{self.base_url}/v1/messages",
            json={
                "model": "test-model",
                "max_tokens": 64,
                "temperature": 1.0,
                "messages": [
                    {"role": "user", "content": "Say hello in one word."},
                ],
            },
            headers={"x-api-key": "test-session"},
            timeout=60.0,
        )
        assert resp.status_code == 200
        body = resp.json()

        # Validate Anthropic response structure
        assert body["type"] == "message"
        assert body["role"] == "assistant"
        assert "content" in body
        assert len(body["content"]) > 0
        assert body["content"][0]["type"] == "text"
        assert len(body["content"][0]["text"]) > 0
        assert "usage" in body
        assert body["usage"]["input_tokens"] > 0
        assert body["usage"]["output_tokens"] > 0

    def test_session_captures_logprobs(self):
        """Proxy captures token IDs and logprobs for the session."""
        import httpx

        session_id = "logprob-test"
        self.proxy.create_session(session_id)

        resp = httpx.post(
            f"{self.base_url}/v1/messages",
            json={
                "model": "test-model",
                "max_tokens": 32,
                "temperature": 1.0,
                "messages": [
                    {"role": "user", "content": "Count to 3."},
                ],
            },
            headers={"x-api-key": session_id},
            timeout=60.0,
        )
        assert resp.status_code == 200

        # Check session data was captured
        session = self.proxy.get_session(session_id)
        assert session is not None
        assert len(session.interactions) == 1

        interaction = session.interactions[0]
        assert len(interaction.prompt_token_ids) > 0
        assert len(interaction.output_token_ids) > 0
        assert len(interaction.output_logprobs) == len(interaction.output_token_ids)

        # Logprobs should be real values (negative)
        for lp in interaction.output_logprobs:
            assert isinstance(lp, float)

    def test_streaming_response(self):
        """POST /v1/messages with stream=true returns SSE events."""
        import httpx

        self.proxy.create_session("stream-test")

        with httpx.stream(
            "POST",
            f"{self.base_url}/v1/messages",
            json={
                "model": "test-model",
                "max_tokens": 32,
                "temperature": 1.0,
                "stream": True,
                "messages": [
                    {"role": "user", "content": "Hi"},
                ],
            },
            headers={"x-api-key": "stream-test"},
            timeout=60.0,
        ) as resp:
            assert resp.status_code == 200
            chunks = list(resp.iter_lines())

        # Should contain Anthropic SSE events
        event_types = [
            line.replace("event: ", "")
            for line in chunks if line.startswith("event: ")
        ]
        assert "message_start" in event_types
        assert "message_stop" in event_types

    def test_multi_turn_session(self):
        """Multiple messages in one session accumulate interactions."""
        import httpx

        session_id = "multi-turn"
        self.proxy.create_session(session_id)

        for content in ["First message", "Second message"]:
            resp = httpx.post(
                f"{self.base_url}/v1/messages",
                json={
                    "model": "test-model",
                    "max_tokens": 32,
                    "temperature": 1.0,
                    "messages": [{"role": "user", "content": content}],
                },
                headers={"x-api-key": session_id},
                timeout=60.0,
            )
            assert resp.status_code == 200

        session = self.proxy.get_session(session_id)
        assert session is not None
        assert len(session.interactions) == 2


# ── Test 4: Full datum pipeline ──────────────────────────────────────────


class TestDatumPipeline:
    def test_single_turn_datum(self, sampling_client, tokenizer):
        """Single-turn session → one datum with real logprobs."""
        import tinker
        from anthropic_proxy import SessionData, SessionInteraction

        messages = [{"role": "user", "content": "What is 1+1?"}]
        prompt_ids = tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=True, return_dict=False,
        )
        result = asyncio.run(sampling_client.sample_async(
            prompt=tinker.types.ModelInput.from_ints(tokens=prompt_ids),
            num_samples=1,
            sampling_params=tinker.SamplingParams(max_tokens=32, temperature=1.0),
        ))
        sample = result.sequences[0]
        raw_lps = getattr(sample, "logprobs", None) or getattr(sample, "maybe_logprobs", None)

        session = SessionData(session_id="datum-test")
        session.interactions.append(SessionInteraction(
            interaction_id="msg_1",
            messages=messages,
            prompt_token_ids=prompt_ids,
            output_token_ids=list(sample.tokens),
            output_logprobs=list(raw_lps) if raw_lps else [],
        ))

        datums = session_to_datums(session, advantage=1.5, tokenizer=tokenizer)
        assert len(datums) == 1
        datum = datums[0]

        # Verify shapes consistent
        n = len(datum.model_input.to_ints())
        assert len(datum.loss_fn_inputs["target_tokens"].to_torch()) == n
        assert len(datum.loss_fn_inputs["logprobs"].to_torch()) == n
        assert len(datum.loss_fn_inputs["advantages"].to_torch()) == n

        # Logprobs: 0 for prompt portion, real for output
        lps = datum.loss_fn_inputs["logprobs"].to_torch()
        prompt_len = len(prompt_ids)
        for i in range(prompt_len - 1):
            assert lps[i].item() == 0.0
        assert any(lps[i].item() != 0.0 for i in range(prompt_len - 1, n))

    def test_multi_turn_via_proxy_datums(self, sampling_client, tokenizer):
        """Multi-turn through proxy → per-turn datums with preserved logprobs."""
        import httpx
        from anthropic_proxy import AnthropicTinkerProxy

        proxy = AnthropicTinkerProxy(sampling_client, model_name="test")
        proxy.start(port=18322)
        try:
            sid = "mt-datum-test"
            proxy.create_session(sid)

            # Turn 1
            r1 = httpx.post("http://127.0.0.1:18322/v1/messages", json={
                "model": "test", "max_tokens": 16, "temperature": 1.0,
                "messages": [{"role": "user", "content": "Say hi"}],
            }, headers={"x-api-key": sid}, timeout=60.0)
            assert r1.status_code == 200
            t1_text = r1.json()["content"][0]["text"]

            # Turn 2 (with prior context)
            r2 = httpx.post("http://127.0.0.1:18322/v1/messages", json={
                "model": "test", "max_tokens": 16, "temperature": 1.0,
                "messages": [
                    {"role": "user", "content": "Say hi"},
                    {"role": "assistant", "content": t1_text},
                    {"role": "user", "content": "Now say bye"},
                ],
            }, headers={"x-api-key": sid}, timeout=60.0)
            assert r2.status_code == 200

            session = proxy.get_session(sid)
            assert len(session.interactions) == 2

            datums = session_to_datums(session, advantage=1.0, tokenizer=tokenizer)
            assert len(datums) == 2

            # Each datum has non-zero logprobs in its output portion
            for i, d in enumerate(datums):
                lps = d.loss_fn_inputs["logprobs"].to_torch()
                assert (lps != 0.0).sum().item() > 0, f"Datum {i}: all-zero logprobs"

            # Turn 2 input is longer (includes prior context)
            assert len(datums[1].model_input.to_ints()) > len(datums[0].model_input.to_ints())
        finally:
            proxy.stop()


# ── Test 5: Tinker forward_backward with real datum ──────────────────────


class TestTinkerTraining:
    def test_forward_backward_accepts_datums(self, training_client, sampling_client, tokenizer):
        """Tinker's forward_backward accepts Datums built from our pipeline."""
        import tinker
        from anthropic_proxy import SessionData, SessionInteraction

        messages = [{"role": "user", "content": "Say yes."}]
        prompt_ids = tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=True, return_dict=False,
        )
        result = asyncio.run(sampling_client.sample_async(
            prompt=tinker.types.ModelInput.from_ints(tokens=prompt_ids),
            num_samples=1,
            sampling_params=tinker.SamplingParams(max_tokens=16, temperature=1.0),
        ))
        sample = result.sequences[0]
        raw_lps = getattr(sample, "logprobs", None) or getattr(sample, "maybe_logprobs", None)

        session = SessionData(session_id="train-test")
        session.interactions.append(SessionInteraction(
            interaction_id="msg_1",
            messages=messages,
            prompt_token_ids=prompt_ids,
            output_token_ids=list(sample.tokens),
            output_logprobs=list(raw_lps) if raw_lps else [0.0] * len(sample.tokens),
        ))

        datums = session_to_datums(session, advantage=1.0, tokenizer=tokenizer)
        assert len(datums) == 1

        # Submit to Tinker — validates Datum format is accepted
        fwd_bwd = training_client.forward_backward(datums, loss_fn="importance_sampling")
        fwd_result = fwd_bwd.result()
        assert fwd_result is not None
        assert hasattr(fwd_result, "loss_fn_outputs")
        assert len(fwd_result.loss_fn_outputs) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
