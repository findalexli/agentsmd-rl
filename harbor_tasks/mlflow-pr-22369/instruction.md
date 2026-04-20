# Task: Fix network latency in `_lookup_model_info` all-provider scan

## Problem Statement

The `_lookup_model_info` function in `mlflow/utils/providers.py` causes severe network latency when called without a specific provider.

### Symptoms

When `_lookup_model_info(model_name)` is called **without** specifying `custom_llm_provider`:

1. The function must scan all available providers to find model pricing info
2. With 68 providers and no provider hint, each provider lookup may trigger a remote network fetch
3. Each network fetch has retry logic and timeouts (~15s per provider worst case)
4. For an unknown model, this creates O(N) network latency — potentially 1000+ seconds for 68 providers

### Expected Behavior

When `custom_llm_provider` is `None`, the function should still find model pricing info but **without making any network requests**. The MLflow codebase bundles provider data locally in `mlflow/utils/providers.py` via `_load_bundled_provider()`.

### Files to Examine

- `mlflow/utils/providers.py` — contains `_lookup_model_info()`, `_load_provider()`, and `_load_bundled_provider()`
- `mlflow/tracing/utils/__init__.py` — contains `calculate_cost_by_model_and_token_usage()` which calls `_lookup_model_info`

### Verification

After fixing, running `pytest tests/utils/test_providers.py` should pass. The fix should ensure that:

1. `_lookup_model_info(model_name)` with no provider works correctly using only local/bundled data
2. `_lookup_model_info(model_name, provider)` with a provider continues to use the fast single-provider path
3. No network latency occurs when scanning providers without a hint

### Reference

The `calculate_cost_by_model_and_token_usage` function in `mlflow/tracing/utils/__init__.py` (line ~339) uses `_lookup_model_info` to calculate LLM inference costs. When tracing requests with unknown models, this latency affects end-to-end trace processing time.