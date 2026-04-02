# XPU Graph Enabled by Default After PyTorch Upgrade

## Problem

After upgrading to a newer version of PyTorch, the XPU graph feature (CUDAGraph on Intel GPU) is now enabled by default. This is problematic because:

- It requires a specific driver version that not all users have
- The feature is not yet stable enough for production use
- Users experience unexpected failures when running vLLM on Intel XPU hardware

## Expected Behavior

XPU graph should be **disabled by default** on Intel GPU platforms. Users who want to opt into XPU graph support should be able to explicitly enable it via an environment variable.

## Affected Files

- `vllm/envs.py` — Environment variable declarations and parsers
- `vllm/platforms/xpu.py` — XPU platform configuration, specifically the `check_and_update_config` method in `XPUPlatform`

## Hints

- Look at how other boolean environment variables are declared and parsed in `vllm/envs.py` (e.g., `VLLM_BATCH_INVARIANT`, `VLLM_SKIP_P2P_CHECK`)
- The `check_and_update_config` method in `xpu.py` already has conditional logic for disabling `cudagraph_mode` — the new check should fit into that chain of conditions
- The environment variable should follow vLLM's naming convention: `VLLM_XPU_*`
