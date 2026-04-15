# AITER State Leak Between ROCm MOE Tests

## Symptom

When running fused MOE routed-transform tests on ROCm (AMD GPUs), tests that disable AITER can produce incorrect results if they run after a test that enabled AITER. The observed symptom is large numerical differences (e.g. max_diff=0.277) between results that should be nearly identical. The root cause is that AITER-related class-level state persists across tests in the same process.

## Expected Behavior

- Each ROCm MOE test should run with a clean AITER state regardless of what ran before it in the same process.
- Environment variable overrides set in test fixtures should be correctly applied at teardown regardless of the `use_rocm_aiter` parameter value.
- Test teardown should not leave class-level cached environment state that persists to subsequent tests.

## Background

The ROCm AITER backend (`rocm_aiter_ops`) reads environment variables (`VLLM_ROCM_USE_AITER`, `VLLM_ROCM_USE_AITER_MOE`) at construction time and caches them as class-level attributes. The `parallel_state` module provides a cleanup function that is called between tests to reset environment-related caches.

## To Investigate

1. In the test fixture for routed-input transforms: verify that AITER-related environment variables are set for all ROCm test cases (not only those where the parameter enables AITER). Both `VLLM_ROCM_USE_AITER` and `VLLM_ROCM_USE_AITER_MOE` must be set correctly before the ops module is imported.

2. In the parallel state cleanup path: verify that it resets all environment-dependent class-level caches used by the AITER backend, so that cached state matches `os.environ` after cleanup.

3. In the routing simulator integration test: verify that environment variable overrides use patterns that are automatically cleaned up at teardown, not direct dictionary mutations that survive past test scope.
