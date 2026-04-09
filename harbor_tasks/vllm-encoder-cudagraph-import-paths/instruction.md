# Fix Import Paths for encoder_cudagraph Modules

## Problem

Enabling `cudagraph_mm_encoder` causes a `ModuleNotFoundError` at runtime. Several files across the codebase import from `vllm.v1.worker.gpu.mm.encoder_cudagraph` and `vllm.v1.worker.gpu.mm.encoder_cudagraph_defs`, but no such modules exist at that path. The actual modules live elsewhere under `vllm/v1/worker/`.

The error looks like:

```
ModuleNotFoundError: No module named 'vllm.v1.worker.gpu.mm.encoder_cudagraph'
```

## Expected Behavior

All imports of the encoder CUDA graph modules should resolve correctly so that `EncoderCudaGraphManager`, `EncoderCudaGraphConfig`, and related classes can be imported without error.

## Files to Look At

- `vllm/v1/worker/encoder_cudagraph.py` — the main encoder CUDA graph manager module
- `vllm/v1/worker/encoder_cudagraph_defs.py` — data transfer objects for encoder CUDA graph management
- `vllm/v1/worker/gpu_model_runner.py` — imports the encoder CUDA graph manager
- `vllm/model_executor/models/qwen3_vl.py` — model with encoder CUDA graph protocol methods
- `vllm/model_executor/models/interfaces.py` — interface definitions with type-checking imports
- `tests/v1/cudagraph/test_encoder_cudagraph.py` — test file for encoder CUDA graph functionality
