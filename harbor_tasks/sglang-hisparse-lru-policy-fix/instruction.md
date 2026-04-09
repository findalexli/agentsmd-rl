# Fix hisparse LRU policy

## Problem

The `hisparse` JIT kernel (hierarchical sparse attention cache) has a bug in its LRU (Least Recently Used) slot management policy. The kernel manages a hot buffer of cached tokens with LRU eviction, but the ordering of slots after handling cache misses is incorrect.

The bug manifests in the `load_cache_to_device_buffer_kernel` function in `python/sglang/jit_kernel/csrc/hisparse.cuh`. When cache misses occur (tokens that need to be loaded from host memory), the kernel:

1. First computes which slots are hits and which are evictable
2. **Bug:** Writes back the LRU ordering BEFORE counting misses
3. Then counts and handles misses

This means the LRU ordering doesn't account for the newly-loaded miss slots, causing them to be misplaced in the slot order. The misses should be placed in the LRU order right before the hits (as they're freshly used), but the current code doesn't do this.

## Expected Behavior

The LRU write-back should happen AFTER `total_misses` is computed, and the ordering logic should handle three categories:

1. **Misses** (just loaded from host): Place right before hits in LRU order
2. **Evictables** (truly stale slots): Stay at LRU front  
3. **Hits** (already in cache): Stay at MRU back

The fix requires:
- Moving the LRU write-back block to after `total_misses = NUM_TOP_K - s_total_hits - s_newest_hit;`
- Adding a three-way conditional that handles misses separately from evictables
- Computing proper indices: misses at `total_evictable - total_misses + i`, evictables at `i - total_misses`

## Files to Look At

- `python/sglang/jit_kernel/csrc/hisparse.cuh` — The main CUDA kernel file containing `load_cache_to_device_buffer_kernel`

Look for the shared memory LRU management code and the write-back section that updates `req_lru_slots`.
