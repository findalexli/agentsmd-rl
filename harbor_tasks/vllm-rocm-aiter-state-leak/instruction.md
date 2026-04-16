# AITER State Leak Between ROCm MOE Tests

## Symptom

When running fused MOE routed-transform tests on ROCm (AMD GPUs), tests that disable AITER can produce incorrect results if they run after a test that enabled AITER. The observed symptom is large numerical differences (e.g. max_diff=0.277) between results that should be nearly identical. The root cause is that AITER-related class-level state persists across tests in the same process.

## Expected Behavior

- Each ROCm MOE test should run with a clean AITER state regardless of what ran before it in the same process.
- Environment variable overrides set in test fixtures should be correctly applied at teardown regardless of the `use_rocm_aiter` parameter value.
- Test teardown should not leave class-level cached environment state that persists to subsequent tests.

## Background

The ROCm AITER backend (`rocm_aiter_ops`) reads environment variables (`VLLM_ROCM_USE_AITER`, `VLLM_ROCM_USE_AITER_MOE`) at construction time and caches them as class-level attributes. The `parallel_state` module provides a cleanup function that is called between tests to reset environment-related caches.

## Requirements

The following specific behavioral requirements must be met:

1. **Environment variable setup in `test_routed_input_transform_inside_vs_outside`** (located in `tests/kernels/moe/test_shared_fused_moe_routed_transform.py`):
   - Both environment variables `VLLM_ROCM_USE_AITER` and `VLLM_ROCM_USE_AITER_MOE` must be set for all ROCm test cases.
   - The variables must be set to `"1"` when `use_rocm_aiter` is `True`, and `"0"` when `use_rocm_aiter` is `False`.
   - The setup must execute whenever `current_platform.is_rocm()` returns `True`, regardless of the `use_rocm_aiter` parameter value.

2. **Cleanup of AITER state in `cleanup_dist_env_and_memory`** (located in `vllm/distributed/parallel_state.py`):
   - The function must call `refresh_env_variables()` on the `rocm_aiter_ops` module when running on ROCm.
   - This ensures class-level cached environment variables in `rocm_aiter_ops` are synchronized with `os.environ` after cleanup.
   - The function must continue to call `disable_envs_cache()` and `gc.unfreeze()` as it does currently.

3. **Environment variable mutation in `test_routing_strategy_integration`** (located in `tests/kernels/moe/test_routing_simulator.py`):
   - The test must not directly mutate `environment_variables` via subscript assignment (e.g., `envs.environment_variables[key] = value`).
   - Environment variable overrides must use patterns that are automatically restored at test teardown (such as `monkeypatch.setitem`).
