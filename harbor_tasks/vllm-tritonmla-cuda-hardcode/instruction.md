# TritonMLA and MoE have hardcoded CUDA calls that break on non-CUDA platforms

## Problem

The TritonMLA attention backend in `vllm/v1/attention/backends/mla/triton_mla.py` directly calls `torch.cuda.get_device_properties(0)` to obtain the SM (streaming multiprocessor) count. This call is hardcoded to CUDA and will fail on any non-CUDA platform (e.g., Intel XPU).

Separately, the unquantized fused MoE method in `vllm/model_executor/layers/fused_moe/unquantized_fused_moe_method.py` uses a platform detection call to decide whether to enter the XPU weight-processing branch. This is inconsistent with the rest of the method, which uses the `unquantized_backend` enum to select code paths. The platform-based check can misroute execution when running on XPU with a non-XPU backend (e.g., TRITON).

## Expected Behavior

- The TritonMLA backend should use vLLM's platform abstraction layer to query compute unit counts, so it works on any supported device.
- The MoE weight-processing logic should use the backend enum consistently for all backend-specific branches, not mix platform detection with enum checks.

## Files to Look At

- `vllm/v1/attention/backends/mla/triton_mla.py` — TritonMLA attention backend, `__init__` method
- `vllm/model_executor/layers/fused_moe/unquantized_fused_moe_method.py` — `process_weights_after_loading` method
- `vllm/platforms/interface.py` — Platform abstraction API (see `num_compute_units`)
- `vllm/model_executor/layers/fused_moe/oracle/unquantized.py` — `UnquantizedMoeBackend` enum
