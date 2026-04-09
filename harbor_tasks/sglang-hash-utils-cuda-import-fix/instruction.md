# sglang-hash-utils-cuda-import-fix

## Problem

Importing `radix_cache` (or any module that transitively depends on it) fails on CPU-only machines because it pulls in CUDA dependencies. The root cause is that `radix_cache.py` imports `get_hash_str` and `hash_str_to_int64` from `hicache_storage.py`, which transitively imports `sgl_kernel` that requires `libcuda.so.1`.

This prevents running unit tests or using parts of the codebase that need HTTP server endpoints without having CUDA available.

## Expected Behavior

The hash utility functions (`get_hash_str` and `hash_str_to_int64`) should be importable without triggering CUDA dependency chain. These are pure Python functions that compute SHA256 hashes - they don't need CUDA.

## Files to Look At

- `python/sglang/srt/mem_cache/radix_cache.py` — imports hash functions from hicache_storage
- `python/sglang/srt/mem_cache/hicache_storage.py` — contains hash functions but also CUDA storage code
- `python/sglang/srt/managers/cache_controller.py` — another import site for hash functions
- `python/sglang/srt/mem_cache/utils.py` — existing utility module (pure Python, no CUDA deps)

## What to Do

Move `get_hash_str` and `hash_str_to_int64` from `hicache_storage.py` to `utils.py`, then update all import sites (`radix_cache.py`, `cache_controller.py`) to import from `utils.py` instead. The hash functions should remain functionally identical - only their location changes.
