# Fix compile error for swap_blocks_batch in CUDA 13

## Problem

Building vLLM with CUDA 13 fails during compilation of `csrc/cache_kernels.cu`. The `swap_blocks_batch` function calls `cuMemcpyBatchAsync` with arguments that don't match the CUDA 13 API signature. The compiler reports:

- `argument of type "size_t *" is incompatible with parameter of type "CUstream"`
- `too many arguments in function call`

The CUDA 13 toolkit changed the signature of `cuMemcpyBatchAsync`, removing the `fail_idx` output parameter. The current code only handles the pre-CUDA 13 signature.

## Expected Behavior

`csrc/cache_kernels.cu` should compile successfully on both CUDA 13 and older CUDA versions (12.8+). The `swap_blocks_batch` function needs to handle both API variants.

## Files to Look At

- `csrc/cache_kernels.cu` — CUDA kernel file containing the `swap_blocks_batch` function that calls `cuMemcpyBatchAsync`
