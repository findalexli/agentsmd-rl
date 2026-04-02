# ROCm HIP Stream Masquerading Functions Missing from Public Header

## Bug Report

External projects that build against PyTorch's C++ headers on ROCm (HIP) are failing to compile because several `*MasqueradingAsCUDA` stream utility functions are not reachable through the standard include path.

Specifically, functions like `getCurrentHIPStreamMasqueradingAsCUDA`, `getDefaultHIPStreamMasqueradingAsCUDA`, `getStreamFromPoolMasqueradingAsCUDA`, `getStreamFromExternalMasqueradingAsCUDA`, and `setCurrentHIPStreamMasqueradingAsCUDA` are declared in `aten/src/ATen/hip/impl/HIPStreamMasqueradingAsCUDA.h`. However, that header is not included directly or indirectly by external projects that only pull in the public `c10/cuda/CUDAStream.h` header.

A recent refactoring of HIP stream compatibility wrappers in `c10/cuda/CUDAStream.h` added non-masquerading HIP aliases (e.g., `getCurrentHIPStream`, `setCurrentHIPStream`) inside the `#ifdef USE_ROCM` / `namespace c10::hip` block, but the masquerading variants were left behind in the internal ATen header.

## Expected Behavior

Any external project including `c10/cuda/CUDAStream.h` (or its hipified equivalent `c10/hip/HIPStream.h`) should have access to all `*MasqueradingAsCUDA` stream functions without needing to separately include the internal ATen header.

## Relevant Files

- `c10/cuda/CUDAStream.h` — public header with HIP backward-compat aliases (look at the `#ifdef USE_ROCM` block near the end)
- `aten/src/ATen/hip/impl/HIPStreamMasqueradingAsCUDA.h` — internal header where the masquerading functions currently live
