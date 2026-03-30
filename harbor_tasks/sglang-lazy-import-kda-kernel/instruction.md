# Fix AMD/ROCm startup crash caused by top-level CUDA import in KDA backend

## Bug Description

The file `python/sglang/srt/layers/attention/linear/kda_backend.py` has a top-level import of `CuteDSLKDAKernel` from the `kda_cutedsl` module. This import chains through to `cuda.bindings.driver`, which is a CUDA-only package that does not exist on AMD/ROCm systems. This causes an immediate `ModuleNotFoundError` when launching any model with linear attention (e.g., Qwen3.5) on AMD GPUs:

```
ModuleNotFoundError: No module named 'cuda'
```

The import is only needed when the CuTeDSL backend is selected AND the platform is CUDA, but because it is at the top level, it is always executed regardless of platform.

## Expected Fix

Move the `CuteDSLKDAKernel` import from the top level to a lazy import inside the code path where it is actually used (inside the `elif decode_backend.is_cutedsl():` branch in the `__init__` method, which already has an `is_cuda()` guard). This way, non-CUDA platforms never attempt to import the CUDA-only module.

## File to Modify

`python/sglang/srt/layers/attention/linear/kda_backend.py` -- remove the top-level import of `CuteDSLKDAKernel` and add it as a local import inside the `is_cutedsl()` branch.
