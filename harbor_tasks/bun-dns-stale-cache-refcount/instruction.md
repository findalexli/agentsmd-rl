# Bug: DNS cache entries never expire while in-flight requests hold a reference

## Summary

Bun's internal DNS cache in `src/bun.js/api/bun/dns.zig` has a bug where stale cache entries are kept alive indefinitely as long as any connection to that host is in-flight (i.e., `refcount > 0`).

The `isExpired` method on `Request` conflates two concerns: whether a cache entry has outlived its TTL, and whether it's safe to free its memory. This means the cache lookup in `GlobalCache.get` will keep serving stale DNS results to new connections as long as even one older connection is still active.

## Observed behavior

- A DNS entry is resolved and cached with a TTL.
- While a long-lived connection (e.g., a keep-alive HTTP request) holds a reference to that entry, the refcount stays above zero.
- New DNS lookups for the same host hit the cache and receive the old (possibly stale) IP address, even if the TTL has long expired.
- The entry is never marked as expired until all existing connections close.
- When a subsequent DNS resolution callback runs, it can overwrite the `valid` flag on a previously valid entry, causing that entry to be treated as invalid even though it was successfully resolved before.

## Expected behavior

- DNS cache entries should expire based on their configured TTL, independent of how many connections currently hold references to them.
- Expired entries that still have active references should not be served to new lookups, but should also not be freed while in use.
- The `valid` flag on a cache entry should only transition from valid to invalid when an actual error occurs, not be unconditionally overwritten on each callback.

## Files to investigate

- `src/bun.js/api/bun/dns.zig` — investigate the `Request.isExpired` method, the `GlobalCache.get` method, and the `freeaddrinfo` callback
