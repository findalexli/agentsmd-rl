# AITER State Leak Between ROCm MOE Tests

## Problem

When running the shared fused MOE routed-transform tests on ROCm (AMD GPUs), tests that disable AITER (`use_rocm_aiter=False`) can produce incorrect results if they run in the same process after a test that enabled AITER (`use_rocm_aiter=True`). The observed symptom is large numerical differences (e.g. max_diff=0.277) between results that should be nearly identical.

The root cause is that AITER state leaks between tests through multiple paths:

1. **Conditional environment setup in the test fixture** — In `tests/kernels/moe/test_shared_fused_moe_routed_transform.py`, the AITER-related environment variables and state refresh are only performed when AITER is being *enabled*. When a subsequent test wants AITER *disabled*, no cleanup or override happens, so stale class-level state from the prior test persists and the kernel silently uses the wrong backend.

2. **Missing state reset in the shared cleanup path** — `vllm/distributed/parallel_state.py` provides a cleanup function that resets environment caches between tests, but it does not touch the AITER ops class-level cached state. Since pytest's monkeypatch only restores `os.environ`, the cached class variables survive across tests.

3. **Unsafe environment dict mutation in a related test** — `tests/kernels/moe/test_routing_simulator.py` directly mutates a shared environment dictionary in a way that is not automatically restored at test teardown, which can pollute state for later tests in the same process.

## Expected Behavior

- Each ROCm MOE test should run with a clean AITER state regardless of what ran before it in the same process.
- Environment variable overrides in test fixtures should be properly cleaned up at teardown.

## Files to Investigate

- `tests/kernels/moe/test_shared_fused_moe_routed_transform.py`
- `vllm/distributed/parallel_state.py`
- `tests/kernels/moe/test_routing_simulator.py`
