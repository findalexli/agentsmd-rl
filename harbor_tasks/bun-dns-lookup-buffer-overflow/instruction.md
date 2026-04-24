# bun-dns-lookup-buffer-overflow

## Problem

The DNS lookup functionality in Bun crashes or produces incorrect results when resolving hostnames longer than 1024 bytes. The code uses a fixed-size stack buffer (`var name_buf: [1024]u8 = undefined`) that overflows when the hostname exceeds its capacity, causing memory corruption or a runtime panic.

## Expected Behavior

The DNS resolution code must safely handle hostnames of any length without buffer overflow or memory corruption. Specifically:

1. **No fixed-size stack buffer** — The code must not use a stack-allocated buffer with a hardcoded size limit (such as 1024 bytes) for hostname storage.
2. **Dynamic memory allocation** — Hostnames that exceed any stack buffer capacity must be stored in dynamically allocated memory on the heap.
3. **Proper deallocation** — Any heap memory allocated during DNS resolution must be freed when no longer needed.

## Files to Look At

- `src/bun.js/api/bun/dns.zig` — Contains the DNS resolution code