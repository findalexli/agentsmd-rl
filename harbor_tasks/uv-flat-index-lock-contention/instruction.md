# Bug: Flat index lock held across async fetch causes contention

## Summary

When resolving packages from multiple `--find-links`-style flat indexes, `uv` serializes all index fetches behind a single async mutex. The `RegistryClient` stores flat index results in a `FlatIndexCache` protected by `Arc<Mutex<FlatIndexCache>>`. The problem is in the `flat_single_index` method: it acquires the lock at the start of the function and holds it for the entire duration of the HTTP fetch, cache lookup, and cache insertion.

This means that if you have multiple flat indexes configured, fetching index A blocks all lookups for indexes B, C, etc. — even though these fetches are completely independent and could proceed concurrently. Each index fetch involves network I/O that can take seconds, and the lock prevents any parallelism.

## Where to look

- `crates/uv-client/src/registry_client.rs` — the `flat_single_index` method and the `FlatIndexCache` type near the bottom of the file
- The method acquires `self.flat_indexes.lock().await` and never releases it until the function returns
- Compare with how concurrent access patterns typically work in async Rust: acquire a lock briefly to check/insert, but don't hold it across `.await` points (especially network calls)

## Expected behavior

Fetching entries from different flat index URLs should proceed concurrently. The lock should only be held briefly for cache bookkeeping, not across the network fetch.

## Actual behavior

The mutex is held for the entire duration of each flat index fetch, serializing all flat index operations regardless of which URL they target. With multiple `--find-links` indexes, this creates a bottleneck where each index fetch must wait for all previous fetches to complete.
