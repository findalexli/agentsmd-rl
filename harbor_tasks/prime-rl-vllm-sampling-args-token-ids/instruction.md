# Bug: Non-TITO rollout client never receives token IDs from vLLM

## Problem Statement

`get_sampling_args()` in the orchestrator utility module builds the sampling argument dictionary sent to the inference server. When the inference backend is vLLM, the response includes token IDs that downstream verifiers need to parse. However, the current implementation fails to include `return_token_ids=True` for vLLM backends under certain configurations, causing downstream verifiers to crash with `len(None)` when they try to parse token IDs from the response.

Additionally, the function currently includes vLLM-specific parameters (`top_k` and `min_p`) unconditionally in the request body, even when the backend is NOT vLLM. This could cause errors on non-vLLM backends such as external teacher models.

## Observed Behavior

### Symptom 1: Token IDs missing for vLLM
When the orchestrator is configured to NOT use the token-in-token-out (TITO) client (`use_token_client=False`), calling `get_sampling_args()` does not set `return_token_ids=True` in the `extra_body` dictionary. However, vLLM needs this flag to return token IDs. Downstream verifiers call `parse_tokens()` on the response and crash because no token IDs are present.

### Symptom 2: vLLM-specific keys sent to non-vLLM backends
The `extra_body` dictionary unconditionally includes `top_k=-1` and `min_p=0.0`, even when the backend is NOT vLLM (e.g., an external teacher model). These parameters are vLLM-specific and may cause errors on non-vLLM backends.

## Required Fix

1. The function must set `return_token_ids=True` in `extra_body` when the backend is vLLM, regardless of the `use_token_client` setting.

2. The function must ONLY include vLLM-specific keys (`top_k`, `min_p`, and `return_token_ids`) in `extra_body` when the backend is vLLM. For non-vLLM backends, these keys must NOT be present in `extra_body`.

3. The `logprobs` key must always be set to `True` in the result dictionary, regardless of backend type.

4. A new boolean parameter must be added to `get_sampling_args()` to control vLLM-specific behavior. This parameter:
   - Must NOT be named `use_token_client`
   - Should have 'vllm' in its name (e.g., `is_vllm`, `vllm_backend`, etc.), OR be a new boolean parameter added to the function signature

5. Callers (`orchestrator.py` and `scheduler.py`) must be updated to pass the new parameter instead of `use_token_client` when calling `get_sampling_args()`.

## Expected Behavior After Fix

- When backend is vLLM: `extra_body` contains `return_token_ids=True`, `top_k=-1`, and `min_p=0.0`
- When backend is NOT vLLM: `extra_body` does NOT contain `return_token_ids`, `top_k`, or `min_p`
- `logprobs` is always `True` in the result
- `min_tokens` and `repetition_penalty` are preserved in `extra_body` when set
- `max_tokens` is passed through in the result

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
- `mypy (Python type checker)`
