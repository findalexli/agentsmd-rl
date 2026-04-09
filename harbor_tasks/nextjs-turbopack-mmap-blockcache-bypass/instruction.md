# turbo-persistence: skip BlockCache for uncompressed mmap-backed blocks

## Problem

The `StaticSortedFile` in `turbopack/crates/turbo-persistence/src/static_sorted_file.rs` routes all block reads — compressed and uncompressed — through the shared `BlockCache`. For uncompressed (mmap-backed) blocks, this is wasteful: an mmap-backed `ArcBytes` is just an `Arc::clone` plus a pointer copy, which is cheaper than the hash table lookup + lock contention of the cache. Additionally, CRC checksums are re-verified on every access for blocks that bypass or get evicted from the cache.

This causes unnecessary lock contention on the hot read path, pollutes the cache with entries that are essentially free to recreate, and performs redundant CRC computation.

## Expected Behavior

Uncompressed blocks should bypass the `BlockCache` entirely and be served directly from the mmap. CRC verification should happen at most once per block per file open, tracked by a per-file bitmap. Compressed blocks should continue using the cache but also benefit from the bitmap to skip redundant CRC checks on re-reads after eviction.

## Files to Look At

- `turbopack/crates/turbo-persistence/src/static_sorted_file.rs` — the SST block reading path, `StaticSortedFile` struct, `BlockWeighter`, and the `ValueBlockCache` trait implementation
