# bun-dns-lookup-buffer-overflow

## Problem

The DNS lookup functionality in Bun has a buffer overflow vulnerability when resolving hostnames longer than 1024 bytes. When processing DNS queries for very long hostnames, the code copies data past the end of a fixed-size stack buffer, causing memory corruption.

## Expected Behavior

The DNS resolution code in `src/bun.js/api/bun/dns.zig` must safely handle hostnames of arbitrary length. The fix must use the following specific patterns:

- Allocate using `std.heap.stackFallback(1024, bun.default_allocator)` for stack-to-heap spilling
- Copy the hostname using `name_allocator.dupeZ(u8, query.name)` for null-terminated dynamic allocation
- Free the allocated memory using `defer name_allocator.free(name_z)` to prevent memory leaks

The vulnerable fixed-size buffer pattern that overflows must no longer be present in the code.

## Files to Look At

- `src/bun.js/api/bun/dns.zig` — Contains the DNS resolution code where the buffer overflow occurs
