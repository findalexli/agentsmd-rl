# Continuous Batching CUDA Graph Capture Crashes Under Multi-Threaded Use

## Bug Description

When running continuous batching inference with multiple threads — each thread managing its own model instance on a separate device — the CUDA graph capture step crashes with graph errors. The threads interfere with each other during `torch.cuda.graph()` capture even though they operate on independent model instances and streams.

The default CUDA graph capture mode does not isolate per-thread graph operations. When multiple threads attempt to capture graphs concurrently in the same process, the capture fails with PyTorch CUDA graph errors.

## Expected Behavior

Each thread should be able to independently capture and replay CUDA graphs without interfering with other threads' captures. The graph capture must use a mode that is safe for concurrent multi-threaded use.

## How to Verify the Fix

After applying your fix, running the continuous batching code under multi-threaded concurrent load should succeed without CUDA graph errors.

The code that creates the CUDA graph (the `torch.cuda.graph()` call during continuous batching capture) must pass a `capture_error_mode` argument set to a **thread-safe mode** — one of the following recognized PyTorch modes:
- `"thread_local"` — each thread maintains its own capture context
- `"relaxed"` — captures are relaxed to avoid cross-thread interference

The mode must not be `"global"` (the default) because `"global"` mode does not support concurrent multi-threaded capture in the same process.

## Code Quality Requirements

The following checks must pass on the modified code:

1. **Ruff lint check** — no lint errors in `src/transformers/generation/continuous_batching/`, `setup.py`, or `conftest.py`
2. **Ruff format check** — code is formatted correctly (run `ruff format --check`)
3. **Type check** — run `python utils/check_types.py` on the modified package
4. **Modeling structure check** — run `python utils/check_modeling_structure.py`
5. **No wildcard imports** — the modified file must not contain `from X import *`
6. **No bare `# type: ignore`** — any type ignore comments must specify an error code (e.g., `# type: ignore[attr-defined]`)
7. **`_generation_step` is not stubbed** — the function must contain meaningful logic (at least 5 substantive statements)

## Relevant File

The code under test is located at:
```
src/transformers/generation/continuous_batching/continuous_api.py
```

This file contains the CUDA graph capture logic for continuous batching. The graph capture happens when a new graph is created for a batch. The fix requires passing an appropriate `capture_error_mode` to the `torch.cuda.graph()` call.