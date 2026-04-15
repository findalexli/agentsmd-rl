# bun-dns-lookup-buffer-overflow

## Problem

The DNS lookup functionality in Bun has a buffer overflow vulnerability. The `LibInfo.lookup` function in the DNS module uses a fixed 1024-byte stack buffer (`var name_buf: [1024]u8 = undefined`) to store the hostname before passing it to `getaddrinfo_async_start`. When resolving hostnames longer than 1024 bytes, the code copies data past the end of this buffer, causing memory corruption, crashes, or potential security issues.

## Expected Behavior

The `LibInfo.lookup` function should safely handle hostnames of any length. Hostnames longer than 1024 bytes must not overflow the stack buffer. The fix should:

1. Remove the fixed 1024-byte stack buffer
2. Use a memory allocation strategy that keeps short hostnames efficient (on the stack) but safely handles longer ones (spilling to heap)
3. Properly clean up any dynamically allocated memory after use

## Files to Look At

- `src/bun.js/api/bun/dns.zig` — Contains the `LibInfo` struct and its `lookup` method where the buffer overflow occurs
  - Look for the fixed-size `name_buf` declaration within `LibInfo.lookup`
  - The vulnerable code path leads to `getaddrinfo_async_start` on macOS
