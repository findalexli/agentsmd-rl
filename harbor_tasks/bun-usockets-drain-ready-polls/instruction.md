# usockets: event loop only processes 1024 ready fds per tick

## Problem

When more than 1024 file descriptors become ready simultaneously, the usockets event loop in Bun only processes the first 1024 per tick. The remaining ready fds are deferred to subsequent ticks, causing increased latency under high I/O load.

This is because the polling calls use a fixed buffer of 1024 slots (defined as `LIBUS_MAX_READY_POLLS` in `packages/bun-usockets/src/internal/internal.h`), and when the kernel fills the entire buffer, any additional ready events remain queued in the kernel.

## Expected Behavior

The event loop should ensure that when the ready_polls buffer is saturated (all slots filled with events from the kernel), it continues processing within the same tick until all pending I/O is drained. This prevents high I/O load from causing latency spikes where only a slice of ready file descriptors is processed per tick.

In other words: after the initial polling and dispatch, if the buffer was completely full, the loop should check for and dispatch any additional ready file descriptors before running pre/post callbacks — all within a single tick.

## Files to Look At

- `packages/bun-usockets/src/eventing/epoll_kqueue.c` — the event loop implementation using epoll (Linux) and kqueue (macOS)
- `packages/bun-usockets/src/internal/internal.h` — defines `LIBUS_MAX_READY_POLLS` constant (value 1024)

## Hints

- The existing `LIBUS_MAX_READY_POLLS` constant should be used instead of any hardcoded 1024 value in polling calls.
- The solution should handle both epoll (Linux) and kqueue (macOS) code paths.
- For epoll, a zero/non-blocking timeout allows checking for more events without blocking.
- For kqueue, a flag like `KEVENT_FLAG_IMMEDIATE` achieves the same non-blocking behavior.
- The drain mechanism should have an iteration cap to prevent unbounded spinning if events keep arriving.
- The drain check should stop when no more polls are registered (`num_polls`).

## Code Style Requirements

- The modified C file must pass `clang-format --dry-run --Werror` (the project uses LLVM-style C formatting enforced by CI).
