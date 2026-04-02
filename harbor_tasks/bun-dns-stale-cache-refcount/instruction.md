# Bug: DNS cache entries never expire while in-flight requests hold a reference

## Summary

Bun's internal DNS cache in `src/bun.js/api/bun/dns.zig` has a bug where stale cache entries are kept alive indefinitely as long as any connection to that host is in-flight (i.e., `refcount > 0`).

The `isExpired` method on `Request` conflates two concerns: whether a cache entry has outlived its TTL, and whether it's safe to free its memory. Currently, the function returns `false` (not expired) whenever the refcount is positive, which means the cache lookup in `GlobalCache.get` will keep serving stale DNS results to new connections as long as even one older connection is still active.

## Observed behavior

- A DNS entry is resolved and cached with a TTL.
- While a long-lived connection (e.g., a keep-alive HTTP request) holds a reference to that entry, the refcount stays above zero.
- New DNS lookups for the same host hit the cache and receive the old (possibly stale) IP address, even if the TTL has long expired.
- The entry is never marked as expired until all existing connections close.

## Expected behavior

- `isExpired` should report expiry based purely on the TTL, regardless of the refcount.
- Memory safety should be handled separately at the call site: expired entries with active references should be skipped (not freed), but they should not be served to new lookups.

## Additional issue

There is also a related problem in the `freeaddrinfo` callback. When a DNS resolution completes, it unconditionally overwrites the `valid` field based on the error code (`req.valid = err == 0`). This means a previously valid entry can have its `valid` flag reset if a subsequent callback runs — it should only set `valid = false` on error, not overwrite it to `true` on success (since it defaults to `true`).

## Files to investigate

- `src/bun.js/api/bun/dns.zig` — look at `Request.isExpired`, `GlobalCache.get`, and the `freeaddrinfo` callback
