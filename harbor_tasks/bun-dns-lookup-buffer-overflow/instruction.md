# bun-dns-lookup-buffer-overflow

## Problem

The DNS lookup functionality in Bun has a buffer overflow vulnerability. When resolving hostnames longer than 1024 bytes, the code writes past the end of a fixed-size stack buffer. This can cause memory corruption, crashes, or potential security issues.

The vulnerable code is in the `LibInfo.lookup` function in the DNS module, which uses a fixed 1024-byte stack buffer to store the hostname before calling the system's `getaddrinfo_async_start` function.

## Expected Behavior

Hostnames longer than 1024 bytes should be handled safely by spilling to heap allocation instead of overflowing the stack buffer. The fix should:

1. Remove the fixed 1024-byte stack buffer
2. Use a `stackFallback` allocator that keeps small hostnames on the stack but spills longer ones to the heap
3. Properly free any heap-allocated memory after use

## Files to Look At

- `src/bun.js/api/bun/dns.zig` — Contains the `LibInfo.lookup` function with the buffer overflow issue
  - Look for the `LibInfo` struct and its `lookup` method
  - The code paths related to `getaddrinfo_async_start` on macOS

## Implementation Notes

The fix involves replacing the fixed buffer pattern:
```zig
var name_buf: [1024]u8 = undefined;
_ = strings.copy(name_buf[0..], query.name);
name_buf[query.name.len] = 0;
const name_z = name_buf[0..query.name.len :0];
```

With a dynamic allocation pattern using `stackFallback`:
```zig
var stack_fallback = std.heap.stackFallback(1024, bun.default_allocator);
const name_allocator = stack_fallback.get();
const name_z = bun.handleOom(name_allocator.dupeZ(u8, query.name));
defer name_allocator.free(name_z);
```

The `stackFallback` allocator is ideal here because it:
- Keeps small hostnames (≤1024 bytes) on the stack for performance
- Automatically spills longer hostnames to the heap
- Maintains the same API for allocation/deallocation
