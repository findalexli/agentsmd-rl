# Heartbeat Task Leaked in SSE Stream

## Bug Description

In `gradio/routes.py`, the `sse_stream` async generator creates a background asyncio task that sends periodic heartbeat messages to keep the SSE connection alive. However, this task is never cancelled when the stream ends.

There are three exit paths from `sse_stream`:

1. **Client disconnects** — `request.is_disconnected()` returns `True` and the function returns
2. **Normal completion** — all queued events are processed and the stream closes
3. **Exception** — an error occurs and is re-raised after cleanup

In all three cases, the heartbeat coroutine continues running indefinitely because no reference to the task is kept and `.cancel()` is never called. This means every SSE connection leaks a background task that loops forever (sleeping and checking for a session that may no longer exist).

## Relevant Code

- **File**: `gradio/routes.py`
- **Function**: Look for the `sse_stream` inner function and how `heartbeat()` is launched within it
- The heartbeat task reference is discarded immediately after creation, making cancellation impossible

## Expected Behavior

The heartbeat task should be properly cancelled in every exit path of the SSE stream — disconnect, normal completion, and exception handling — so that no background tasks are leaked.
