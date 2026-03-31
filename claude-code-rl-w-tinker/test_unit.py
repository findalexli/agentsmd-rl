"""
Unit tests for claude-code-rl-w-tinker.

No API keys or network required. Tests the protocol translation,
session management, tokenization, and advantage computation.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from anthropic_proxy import (
    AnthropicTinkerProxy,
    SessionData,
    SessionInteraction,
    _translate_anthropic_to_openai,
    _openai_response_to_anthropic,
)
from harbor_tokenization import (
    encode_messages_subset,
    get_generation_prompt_ids,
    get_response_ids_and_loss_mask,
)
from train import compute_grpo_advantages, session_to_datums


# ── Anthropic ↔ OpenAI translation ──────────────────────────────────────


class TestAnthropicTranslation:
    def test_simple_text_message(self):
        """Translate a basic Anthropic request to OpenAI format."""
        anthropic_req = {
            "model": "test-model",
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": "Hello, world!"}
            ],
        }
        openai_req = _translate_anthropic_to_openai(anthropic_req)
        assert "messages" in openai_req
        assert any(m.get("content") == "Hello, world!" for m in openai_req["messages"])

    def test_content_blocks_flattened(self):
        """Content block lists should be flattened to strings."""
        anthropic_req = {
            "model": "test-model",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Part 1"},
                        {"type": "text", "text": "Part 2"},
                    ],
                }
            ],
        }
        openai_req = _translate_anthropic_to_openai(anthropic_req)
        user_msg = [m for m in openai_req["messages"] if m.get("role") == "user"][0]
        assert isinstance(user_msg["content"], str)
        assert "Part 1" in user_msg["content"]
        assert "Part 2" in user_msg["content"]

    def test_system_prompt_extraction(self):
        """Anthropic system prompt should be extracted into OpenAI system message."""
        anthropic_req = {
            "model": "test-model",
            "max_tokens": 1024,
            "system": "You are a helpful assistant.",
            "messages": [
                {"role": "user", "content": "Hi"}
            ],
        }
        openai_req = _translate_anthropic_to_openai(anthropic_req)
        system_msgs = [m for m in openai_req["messages"] if m.get("role") == "system"]
        assert len(system_msgs) > 0

    def test_openai_to_anthropic_response(self):
        """Convert an OpenAI-style response dict back to Anthropic format."""
        resp = _openai_response_to_anthropic(
            {
                "choices": [{
                    "message": {"role": "assistant", "content": "Hello!"},
                    "finish_reason": "stop",
                }],
            },
            model="test-model",
            prompt_tokens=10,
            completion_tokens=5,
        )
        assert resp["type"] == "message"
        assert resp["role"] == "assistant"
        assert resp["stop_reason"] == "end_turn"
        assert resp["usage"]["input_tokens"] == 10
        assert resp["usage"]["output_tokens"] == 5
        assert any(b["type"] == "text" and b["text"] == "Hello!" for b in resp["content"])

    def test_tool_use_in_response(self):
        """Tool calls in OpenAI response should become tool_use blocks in Anthropic."""
        resp = _openai_response_to_anthropic(
            {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [{
                            "id": "call_123",
                            "function": {
                                "name": "bash",
                                "arguments": '{"command": "ls"}',
                            },
                        }],
                    },
                    "finish_reason": "tool_calls",
                }],
            },
            model="test-model",
            prompt_tokens=10,
            completion_tokens=20,
        )
        assert resp["stop_reason"] == "tool_use"
        tool_blocks = [b for b in resp["content"] if b["type"] == "tool_use"]
        assert len(tool_blocks) == 1
        assert tool_blocks[0]["name"] == "bash"
        assert tool_blocks[0]["input"] == {"command": "ls"}


# ── Session management ───────────────────────────────────────────────────


class TestSessionData:
    def test_create_and_add_interaction(self):
        session = SessionData(session_id="test-123")
        interaction = SessionInteraction(
            interaction_id="msg_abc",
            messages=[{"role": "user", "content": "hi"}],
            prompt_token_ids=[1, 2, 3],
            output_token_ids=[4, 5],
            output_logprobs=[-0.5, -1.0],
        )
        session.interactions.append(interaction)
        assert len(session.interactions) == 1
        assert session.interactions[0].output_token_ids == [4, 5]
        assert session.interactions[0].output_logprobs == [-0.5, -1.0]

    def test_multiple_interactions(self):
        session = SessionData(session_id="test-456")
        for i in range(3):
            session.interactions.append(SessionInteraction(
                interaction_id=f"msg_{i}",
                messages=[],
                prompt_token_ids=[10 * i],
                output_token_ids=[10 * i + 1, 10 * i + 2],
                output_logprobs=[-0.1 * i, -0.2 * i],
            ))
        assert len(session.interactions) == 3
        total_output = sum(len(i.output_token_ids) for i in session.interactions)
        assert total_output == 6


# ── GRPO advantages ─────────────────────────────────────────────────────


class TestGRPOAdvantages:
    def test_uniform_rewards_zero_advantage(self):
        """If all rewards in a group are the same, advantages should be 0."""
        advs = compute_grpo_advantages([1.0, 1.0, 1.0, 1.0], group_size=4)
        assert all(abs(a) < 1e-6 for a in advs)

    def test_varied_rewards(self):
        """Advantages should be positive for above-mean, negative for below."""
        advs = compute_grpo_advantages([0.0, 0.0, 0.0, 1.0], group_size=4)
        assert advs[3] > 0  # highest reward → positive advantage
        assert advs[0] < 0  # lowest reward → negative advantage

    def test_multiple_groups(self):
        rewards = [0.0, 1.0, 0.5, 0.5,   # group 1
                   1.0, 1.0, 0.0, 0.0]    # group 2
        advs = compute_grpo_advantages(rewards, group_size=4)
        assert len(advs) == 8


# ── session_to_datum ─────────────────────────────────────────────────────


class TestSessionToDatums:
    def test_empty_session_returns_empty(self):
        session = SessionData(session_id="empty")
        assert session_to_datums(session, advantage=1.0, tokenizer=None) == []

    def test_single_interaction_datum(self):
        """Single interaction → one datum with correct alignment."""
        session = SessionData(session_id="test")
        session.interactions.append(SessionInteraction(
            interaction_id="msg_1",
            messages=[{"role": "user", "content": "hello"}],
            prompt_token_ids=[1, 2, 3, 4, 5],  # 5 prompt tokens
            output_token_ids=[6, 7, 8],          # 3 output tokens
            output_logprobs=[-0.5, -1.0, -0.3],
        ))

        datums = session_to_datums(session, advantage=2.0, tokenizer=None)
        assert len(datums) == 1
        datum = datums[0]

        # full_seq = [1,2,3,4,5,6,7,8], shifted by 1
        model_input = datum.model_input.to_ints()
        assert len(model_input) == 7

        logprobs = datum.loss_fn_inputs["logprobs"].to_torch()
        assert len(logprobs) == 7
        # First 4 positions (prompt, shifted) should be 0
        assert all(logprobs[i].item() == 0.0 for i in range(4))
        # Last 3 positions should have real logprobs
        assert logprobs[4].item() == pytest.approx(-0.5)
        assert logprobs[5].item() == pytest.approx(-1.0)
        assert logprobs[6].item() == pytest.approx(-0.3)

        advantages = datum.loss_fn_inputs["advantages"].to_torch()
        assert all(advantages[i].item() == 0.0 for i in range(4))
        assert all(advantages[i].item() == pytest.approx(2.0) for i in range(4, 7))

    def test_multi_turn_produces_multiple_datums(self):
        """Multi-turn session → one datum PER interaction, each with its own logprobs."""
        session = SessionData(session_id="multi")
        # Turn 1: short prompt, 2 output tokens
        session.interactions.append(SessionInteraction(
            interaction_id="msg_1",
            messages=[{"role": "user", "content": "hi"}],
            prompt_token_ids=[1, 2, 3],
            output_token_ids=[4, 5],
            output_logprobs=[-0.1, -0.2],
        ))
        # Turn 2: longer prompt (includes turn 1 context), 3 output tokens
        session.interactions.append(SessionInteraction(
            interaction_id="msg_2",
            messages=[{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hey"}],
            prompt_token_ids=[1, 2, 3, 4, 5, 6, 7],  # includes prior context
            output_token_ids=[8, 9, 10],
            output_logprobs=[-0.3, -0.4, -0.5],
        ))

        datums = session_to_datums(session, advantage=1.5, tokenizer=None)
        assert len(datums) == 2

        # Datum 0: turn 1's logprobs are preserved
        lp0 = datums[0].loss_fn_inputs["logprobs"].to_torch()
        assert lp0[-2].item() == pytest.approx(-0.1)
        assert lp0[-1].item() == pytest.approx(-0.2)

        # Datum 1: turn 2's logprobs are preserved
        lp1 = datums[1].loss_fn_inputs["logprobs"].to_torch()
        assert lp1[-3].item() == pytest.approx(-0.3)
        assert lp1[-2].item() == pytest.approx(-0.4)
        assert lp1[-1].item() == pytest.approx(-0.5)


# ── Anthropic SSE stream format ──────────────────────────────────────────


class TestAnthropicSSE:
    @pytest.mark.asyncio
    async def test_sse_stream_structure(self):
        from anthropic_proxy import _anthropic_sse_stream

        response = {
            "id": "msg_test",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "Hello!"}],
            "model": "test",
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 10, "output_tokens": 5},
        }

        events = []
        async for chunk in _anthropic_sse_stream(response):
            events.append(chunk)

        # Should have: message_start, content_block_start, content_block_delta,
        # content_block_stop, message_delta, message_stop
        event_types = []
        for e in events:
            if e.startswith("event: "):
                event_types.append(e.split("\n")[0].replace("event: ", ""))

        assert "message_start" in event_types
        assert "content_block_start" in event_types
        assert "content_block_delta" in event_types
        assert "content_block_stop" in event_types
        assert "message_delta" in event_types
        assert "message_stop" in event_types


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
