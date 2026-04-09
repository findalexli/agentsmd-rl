# usockets: event loop only processes 1024 ready fds per tick

## Problem

When more than 1024 file descriptors become ready simultaneously, the usockets event loop in Bun only processes the first 1024 per tick. The remaining ready fds are deferred to subsequent ticks, causing increased latency under high I/O load. This is because the `epoll_wait`/`kevent64` calls use a fixed buffer of 1024 slots, and when the kernel fills the entire buffer, any additional ready events remain queued in the kernel.

This behavior differs from libuv, which detects buffer saturation and re-polls with a zero timeout to drain the backlog within a single tick.

## Expected Behavior

When the ready_polls buffer is saturated (all 1024 slots filled), the event loop should re-poll with a zero timeout and dispatch again before running pre/post callbacks, so a single tick covers all pending I/O.

## Files to Look At

- `packages/bun-usockets/src/eventing/epoll_kqueue.c` — the event loop implementation using epoll (Linux) and kqueue (macOS). Contains `us_loop_run` and `us_loop_run_bun_tick` which poll for ready file descriptors and dispatch callbacks.
