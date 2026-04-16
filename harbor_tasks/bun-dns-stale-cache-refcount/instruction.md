# Bug: DNS cache entries never expire

## Summary

Bun's internal DNS cache in `src/bun.js/api/bun/dns.zig` has a bug where cached DNS entries can remain in use past their configured TTL, serving stale IP addresses to new lookups.

## Observed behavior

- A DNS entry is resolved and cached with a TTL.
- New DNS lookups for the same host may receive the old (possibly stale) IP address, even if the TTL has long expired.
- When a DNS resolution callback completes, previously valid entries may be marked invalid.

## Expected behavior

- DNS cache entries should expire when their configured TTL has passed.
- Expired entries should not be served to new lookups.
- Successful DNS resolution callbacks should not inappropriately invalidate previously valid entries.

## Files to investigate

- `src/bun.js/api/bun/dns.zig` — focus on how DNS cache entries are checked for expiration and how entry state is updated after callbacks.