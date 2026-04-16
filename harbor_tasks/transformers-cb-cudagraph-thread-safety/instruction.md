# Continuous Batching CUDA Graph Capture Crashes Under Multi-Threaded Use

## Bug Description

When running continuous batching inference with multiple threads — each thread managing its own model instance on a separate device — the CUDA graph capture step crashes with errors. The threads interfere with each other during graph capture even though they operate on independent model instances and streams.

PyTorch's default CUDA graph capture behavior does not isolate per-thread graph operations, causing failures when multiple threads attempt to capture graphs concurrently in the same process.

## Expected Behavior

Each thread should be able to independently capture and replay CUDA graphs without interfering with other threads' captures. The continuous batching code's `torch.cuda.graph()` call must be configured for safe concurrent multi-threaded use.

## Investigation

The continuous batching implementation is in the `src/transformers/generation/continuous_batching/` directory. Investigate the CUDA graph capture logic in this module to find where `torch.cuda.graph()` is called.

Consult the PyTorch API for `torch.cuda.graph()` to understand the available keyword arguments that control capture behavior in multi-threaded scenarios and determine what configuration change is needed to make concurrent capture thread-safe.

## Code Quality Requirements

The following checks must pass on any modified code:

1. **Ruff lint check** — `ruff check src/transformers/generation/continuous_batching/ setup.py conftest.py`
2. **Ruff format check** — `ruff format --check src/transformers/generation/continuous_batching/ setup.py conftest.py`
3. **Type check** — `python utils/check_types.py src/transformers/generation/continuous_batching/`
4. **Modeling structure check** — `python utils/check_modeling_structure.py`
5. **No wildcard imports** — the modified file must not contain `from X import *`
6. **No bare `# type: ignore`** — any type ignore comments must specify an error code (e.g., `# type: ignore[attr-defined]`)
7. **`_generation_step` must not be stubbed** — the function must contain meaningful logic (at least 5 substantive statements)
8. **No `getattr(torch, '<backend>')` for dynamic backends** — do not use `getattr(torch, ...)` for dynamic device backends (`npu`, `xpu`, `hpu`, `musa`, `mlu`, `neuron`, `compiler`); use type guards instead
9. **No `assert` for type narrowing** — do not use `assert x is not None`, `assert x is None`, or `assert isinstance(...)` for type narrowing; use `if ...: raise` instead
