# bun-dns-lookup-buffer-overflow

## Problem

The DNS lookup functionality in Bun crashes or produces incorrect results when resolving hostnames longer than 1024 bytes. The code uses a fixed-size stack buffer that overflows when the hostname exceeds its capacity, causing memory corruption or a runtime panic.

## Expected Behavior

The DNS resolution code must safely handle hostnames of any length without buffer overflow or memory corruption. Specifically:

1. **No fixed-size stack buffer** — The code must not use a stack-allocated buffer with a hardcoded size limit (such as 1024 bytes) for hostname storage.
2. **Dynamic memory allocation** — Hostnames that exceed any stack buffer capacity must be stored in dynamically allocated memory on the heap.
3. **Proper deallocation** — Any heap memory allocated during DNS resolution must be freed when no longer needed.

## Verification

After making changes to the DNS resolution code, the following patterns must be present in `src/bun.js/api/bun/dns.zig`:

- The pattern `std.heap.stackFallback(1024, bun.default_allocator)` must appear somewhere in the file (this is Zig's standard library pattern for stack-to-heap spilling when a buffer would overflow).
- The pattern `name_allocator.dupeZ(u8, query.name)` must appear somewhere in the file (this allocates a zero-terminated string copy on the heap).
- The pattern `defer name_allocator.free(name_z)` must appear somewhere in the file (this ensures the allocated memory is freed when the function returns).

Additionally, the following pattern must NOT be present:

- The pattern `var name_buf: [1024]u8 = undefined` must not appear anywhere in the file (this is the vulnerable fixed-size stack buffer that causes the overflow).

## Files to Look At

- `src/bun.js/api/bun/dns.zig` — Contains the DNS resolution code