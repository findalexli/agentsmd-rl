# Claude Code RL with Tinker

RL training using **Claude Code** as the agent harness and **Tinker API** for GPU compute.

## Architecture

```
Claude Code CLI (inside Harbor sandbox, reads CLAUDE.md naturally)
    │ POST /v1/messages (Anthropic Messages API)
    ▼
anthropic_proxy.py
    ├── Translates Anthropic → OpenAI (LiteLLM AnthropicAdapter)
    ├── Routes through tinker-cookbook renderer pipeline:
    │     tool schema injection → tokenization → sampling → tool call parsing
    ├── Captures per-session (prompt_ids, output_ids, logprobs) at generation time
    └── Returns Anthropic response with structured tool_use blocks
    │
    ▼
Tinker SamplingClient → remote GPU (Qwen3.5, Kimi K2.5, etc.)
    │
    ▼
train.py
    ├── Harbor Trial.run() → sandbox + verifier → reward
    ├── Per-turn datums with captured logprobs (AReaL "individual" style)
    └── GRPO advantages → Tinker forward_backward + optim_step
```

## Key Insights

**From AReaL**: The proxy captures training data (token IDs, logprobs) at generation
time — not post-hoc. Every LLM call goes through the proxy. No extra forward pass
(`compute_logprobs_async`) needed. Harbor's only job is sandbox + reward.

**From SkyRL**: Per-turn datums with the Tinker-convention shift (model_input = seq[:-1],
target = seq[1:]). Loss is implicit via zero advantages/logprobs on prompt tokens —
no explicit mask field needed for Tinker's `importance_sampling` loss.

## Verified Behavior (e2e tests)

**Multi-turn tool use** — Tested with Qwen3.5-35B-A3B via Harbor + Docker:
- 5-turn Claude Code session with tool calls (Read, Bash, Edit)
- Each turn captured: prompt_token_ids, output_token_ids, output_logprobs
- Token round-trip verified: turn N's output tokens appear verbatim in turn N+1's prompt

**Logprob fidelity** — Per-turn proxy logprobs vs. `compute_logprobs_async` and
`forward_backward` (same weights):

| Comparison | Mean diff | Max diff (outlier tokens) |
|---|---|---|
| Proxy vs compute_logprobs | ~0.005 | ~0.25 |
| Proxy vs training forward_backward | ~0.01 | ~0.65 |

Mean diffs are ~0.01 — well within what AReaL, SkyRL, and veRL document as the
expected "rollout-training mismatch" from different attention kernels (sampling with
incremental KV cache vs. prefill forward pass). Handled by importance ratio clipping.

**Token round-trip** — Verified that decode→re-encode produces identical tokens,
including through tool_call/tool_result flows. The proxy uses raw token decode
(not the renderer's parsed/reconstructed text) to avoid whitespace drift. See
`anthropic_proxy.py` docstring, decision #5.

**Tinker training step** — `forward_backward` accepts all datums. Tested with
1–5 turn sessions. `loss_fn="importance_sampling"` works with the 3-field datum
format (target_tokens, logprobs, advantages).

## Files

| File | Purpose |
|------|---------|
| `anthropic_proxy.py` | Anthropic Messages API proxy backed by Tinker SamplingClient via tinker-cookbook renderer. Captures per-session messages + logprobs. See module docstring for critical design decisions. |
| `harbor_tokenization.py` | Tokenize multi-turn chat histories for RL (ported from SkyRL). Used as fallback; primary path uses tinker-cookbook renderer. |
| `train.py` | Main training loop: Harbor Trial → proxy-captured data → GRPO → Tinker training. |
| `test_unit.py` | Unit tests (no API keys needed): Anthropic translation, session management, GRPO, datum construction, SSE streaming. |
| `test_e2e.py` | E2e with Tinker API: tokenizer, sampling+logprobs, proxy message handling, session capture, datum pipeline, forward_backward acceptance. |
| `test_e2e_extended.py` | Extended e2e: tool use, session isolation, one-shot vs per-turn logprobs, weight sync, 3-turn training step. |
| `test_logprob_fidelity.py` | Logprob correctness: proxy vs compute_logprobs, proxy vs training, multi-turn, negativity check. |
| `test_harbor_trial.py` | Full Harbor Trial with Claude Code CLI in Docker sandbox through proxy. |
| `test_multi_turn_models.py` | Multi-model comparison script (Qwen3.5, Kimi K2.5, etc.). |

## Usage

```bash
# Set credentials
export TINKER_API_KEY=tml-...
# ANTHROPIC_API_KEY is set per-trial by train.py (dummy value for CLI check)

# Training
python claude-code-rl-w-tinker/train.py \
    --model_name Qwen/Qwen3.5-35B-A3B \
    --agent_name claude-code \
    --environment_type docker \
    --max_turns 200 \
    --groups_per_batch 4 \
    --group_size 4

# Tests (unit — no API key needed)
uv run python3 -m pytest claude-code-rl-w-tinker/test_unit.py -v

# Tests (e2e — needs TINKER_API_KEY)
set -a && source .env && set +a
uv run python3 -m pytest claude-code-rl-w-tinker/test_e2e.py test_e2e_extended.py test_logprob_fidelity.py -v

# Tests (Harbor trial — needs TINKER_API_KEY + Docker)
uv run python3 -m pytest claude-code-rl-w-tinker/test_harbor_trial.py -v -s
```

## Critical Design Decisions

Documented in detail in `anthropic_proxy.py` and `train.py` module docstrings. Summary:

1. **Renderer pipeline, not raw `apply_chat_template`** — Qwen3's Jinja template crashes on multi-turn tool messages. The tinker-cookbook renderer handles tools correctly.
2. **Tool call parsing** — Model outputs `<tool_call>` XML blocks. Renderer's `parse_response()` extracts them into structured `ToolCall` objects → Anthropic `tool_use` blocks.
3. **Dynamic `max_tokens` capping** — Auto-detects context window from Tinker's error response. No hardcoded limits.
4. **Session routing by API key** — Direct dict lookup, not iterative search.
5. **Raw token decode for response text** — Preserves exact tokens through the multi-turn round-trip. The renderer's parse→render is not lossless (extra `\n`, JSON normalization).
6. **Logprob divergence is expected** — ~0.01 mean diff from different attention kernels. Handled by importance sampling clipping.

## Dependencies

- `harbor` — install from `.repos/harbor/`
- `tinker` — Tinker SDK
- `tinker-cookbook` — renderers, tool schema injection, tool call parsing
- `litellm` — `AnthropicAdapter` for Anthropic ↔ OpenAI translation
- `fastapi`, `uvicorn` — proxy server
- `httpx` — test HTTP client

## Supported Models (tested)

| Model | Tool calling | Multi-turn | Notes |
|---|---|---|---|
| Qwen/Qwen3.5-35B-A3B | ✓ | ✓ (5 turns verified) | 64K context, MoE, good tool calling |
| Qwen/Qwen3-8B | Partial | 1 turn | 32K context, outputs tool calls but less reliable |
| moonshotai/Kimi-K2.5 | Untested | Untested | 32K context, should work via renderer |

## References

- **AReaL** (`../.repos/AReaL/areal/experimental/openai/proxy/`) — Proxy architecture, per-session capture, "individual" export style
- **SkyRL** (`../.repos/SkyRL/examples/train_integrations/harbor/`) — Harbor integration, datum construction, GRPO
- **tinker-cookbook** (`../.repos/tinker-cookbook/tinker_cookbook/third_party/litellm/`) — Renderer pipeline, tool schema injection, LiteLLM provider
