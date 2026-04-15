# Fix AMD/ROCm startup crash in KDA backend

## Bug Description

When launching any model with linear attention (e.g., Qwen3.5) on AMD/ROCm GPUs, the server crashes immediately with:

```
ModuleNotFoundError: No module named 'cuda'
```

The crash occurs when importing the KDA backend module at `python/sglang/srt/layers/attention/linear/kda_backend.py`. The module works correctly on NVIDIA/CUDA systems but fails to import on any non-CUDA platform (AMD/ROCm, CPU-only).

## Expected Behavior After Fix

- Importing the `kda_backend` module on a non-CUDA system must succeed without raising `ModuleNotFoundError` or `ImportError` mentioning 'cuda' or 'kda_cutedsl'
- The `KDAKernelDispatcher` class must remain intact with its `__init__` method
- `TritonKDAKernel` must remain as a top-level import from the `kda_triton` module
- `CuteDSLKDAKernel` must still be referenced somewhere in the file — it should not be deleted entirely
- The file must retain the identifiers `decode_kernel`, `is_cuda`, and `is_cutedsl`
- The code must pass standard quality checks: valid Python syntax, ruff linting, black formatting, isort import ordering, and codespell
