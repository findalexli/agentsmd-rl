# sglang-hash-utils-cuda-import-fix

## Problem

Importing `radix_cache` (or any module that transitively depends on it) fails on CPU-only machines because it pulls in CUDA dependencies. The root cause is that `radix_cache.py` imports `get_hash_str` and `hash_str_to_int64` from `hicache_storage.py`, which transitively imports `sgl_kernel` that requires `libcuda.so.1`.

This prevents running unit tests or using parts of the codebase that need HTTP server endpoints without having CUDA available.

## Expected Behavior

The hash utility functions (`get_hash_str` and `hash_str_to_int64`) should be importable without triggering the CUDA dependency chain. These are pure Python functions that compute SHA256 hashes — they don't need CUDA.

## What to Do

The hash utility functions must be separated from the CUDA-dependent code path so they can be imported independently. The functions must remain functionally identical — only their import accessibility changes. After the fix, `get_hash_str` and `hash_str_to_int64` must be accessible as pure Python utilities without triggering GPU/cuda dependencies.

You may need to modify: `radix_cache.py`, `cache_controller.py`, `hicache_storage.py`, and `utils.py`.