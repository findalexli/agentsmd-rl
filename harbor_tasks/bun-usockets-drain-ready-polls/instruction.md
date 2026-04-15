# usockets: event loop only processes 1024 ready fds per tick

## Problem

When more than 1024 file descriptors become ready simultaneously, the usockets event loop in Bun only processes the first 1024 per tick. The remaining ready fds are deferred to subsequent ticks, causing increased latency under high I/O load. This is because the `epoll_wait`/`kevent64` calls use a fixed buffer of 1024 slots (defined as `LIBUS_MAX_READY_POLLS` in `packages/bun-usockets/src/internal/internal.h`), and when the kernel fills the entire buffer, any additional ready events remain queued in the kernel.

This behavior differs from libuv, which detects buffer saturation and re-polls with a zero timeout to drain the backlog within a single tick.

## Required Implementation

Add a `static void us_internal_drain_ready_polls(struct us_loop_t *loop)` function in `packages/bun-usockets/src/eventing/epoll_kqueue.c` that:

1. Uses a drain counter initialized to 48 with a decrement pattern (`--drain_count`) to cap iterations and prevent unbounded spinning
2. Checks for buffer saturation (`num_ready_polls == LIBUS_MAX_READY_POLLS`) in the loop condition
3. Re-polls with zero timeout:
   - For epoll: use `struct timespec zero = {0, 0}` and pass `&zero` as the timeout
   - For kqueue: use `KEVENT_FLAG_IMMEDIATE` flag
4. Calls `us_internal_dispatch_ready_polls` inside the loop after each successful poll

Then modify both `us_loop_run` and `us_loop_run_bun_tick` to:

1. Replace hardcoded `1024` with `LIBUS_MAX_READY_POLLS` in the `bun_epoll_pwait2` and `kevent64` calls
2. Call `us_internal_drain_ready_polls(loop)` immediately after `us_internal_dispatch_ready_polls` returns, ensuring drain is called after dispatch

The result should be that when the ready_polls buffer is saturated (all 1024 slots filled), the event loop re-polls with a zero timeout and dispatches again before running pre/post callbacks, so a single tick covers all pending I/O.

## Files to Look At

- `packages/bun-usockets/src/eventing/epoll_kqueue.c` — the event loop implementation using epoll (Linux) and kqueue (macOS). Contains `us_loop_run` and `us_loop_run_bun_tick` which poll for ready file descriptors and dispatch callbacks.
- `packages/bun-usockets/src/internal/internal.h` — defines `LIBUS_MAX_READY_POLLS` constant (value 1024)
