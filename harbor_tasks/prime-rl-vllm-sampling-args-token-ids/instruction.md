# Bug: Non-TITO rollout client never receives token IDs from vLLM

## Context

In `src/prime_rl/orchestrator/utils.py`, the function `get_sampling_args()` builds the
sampling argument dictionary that gets sent to the vLLM inference server. It constructs
an `extra_body` dict with vLLM-specific parameters like `return_token_ids`, `top_k`, and
`min_p`.

## Problem

When the orchestrator is configured to NOT use the token-in-token-out (TITO) client
(i.e. `use_token_client=False`), the `get_sampling_args()` function skips setting
`return_token_ids=True` in `extra_body`. However, even without the TITO client, the
rollout generation still goes through vLLM which needs `return_token_ids` to return
token IDs. Downstream verifiers call `parse_tokens()` on the response and crash with
`len(None)` because no token IDs are present.

The root issue is that the flag controlling whether to include vLLM-specific `extra_body`
parameters is wrong — it's gated on `use_token_client` when it should be gated on
whether the backend is actually vLLM. Additionally, some vLLM-specific parameters are
unconditionally set in `extra_body` even when hitting a non-vLLM backend (like an
external teacher model), which could cause errors on those backends.

## Relevant files

- `src/prime_rl/orchestrator/utils.py` — `get_sampling_args()` function
- `src/prime_rl/orchestrator/orchestrator.py` — calls `get_sampling_args()` around line 493
- `src/prime_rl/orchestrator/scheduler.py` — calls `get_sampling_args()` in `__init__` around line 90

## Reproduction

Running RL training with `--orchestrator.no-use-token-client` against a vLLM backend
will crash when verifiers try to parse token IDs from the rollout response.
